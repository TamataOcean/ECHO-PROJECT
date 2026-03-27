# ECHO-PROJECT — CLAUDE.md

## Contexte du projet

Système d'acquisition vidéo automatisé pour une étude comportementale de poissons en bassins d'observation, dans le cadre de la recherche sur les effets de la pression acoustique des éoliennes offshore sur la faune marine (AAP "Observatoire de l'éolien en mer" — Office Français de la Biodiversité). Durée : 3 ans (démarrage janvier 2024).

**Espèces étudiées :** Bar européen (*Dicentrarchus labrax*) et Sole commune (*Solea solea*)
**Chercheure principale :** Morgane Millot (thèse)

## Architecture du système

```
Node-Red UI (port 1880)
        ↕ MQTT (topic: gstreamer/control / server/log)
Eclipse Mosquitto (broker, port 1883)
        ↕
Python server.py (gère les pipelines GStreamer via gstd)
        ↕
GStreamer Daemon (gstd) → 6 caméras Basler (RTSP) → fichiers .mov sur NAS/NVME
```

**Stack technologique :**
- Python 3.11 — serveur MQTT + contrôleur de pipelines
- GStreamer / gstd 1.x — capture et enregistrement vidéo
- Node-Red 4.0.8 + Dashboard 3.6.5 — interface web de contrôle
- Eclipse Mosquitto 2 — broker de messages
- Docker & Docker Compose — orchestration des services
- Raspberry Pi 5 (16 GB) — calcul embarqué
- Basler ace acA1300-60gc — 6 caméras (1 par arène), accès RTSP

## Deux versions du serveur Python — IMPORTANT

Il existe **deux versions de `server.py`** qui ont divergé :

| Fichier | Usage | Config MQTT |
|---|---|---|
| `core/server.py` | Bare-metal / développement | Hardcodée (`localhost:1883`) |
| `docker/core/server.py` | Production Docker | Via variables d'env `.env` (`MQTT_BROKER`, `MQTT_PORT`, etc.) |

La version Docker est packagée dans l'image `echo-core` via `docker/core/dockerfile` (`COPY . .`) et démarrée par `docker/core/entrypoint.sh` qui :
1. Lance `gstd` en arrière-plan
2. Attend 10 secondes
3. Lance `python3 server.py`

**Lors d'une modification du serveur, penser à répercuter les changements dans les deux fichiers** (ou unifier via un `COPY` depuis `core/` dans le Dockerfile).

## Structure des répertoires

```
ECHO-PROJECT/
├── core/                      # Code source de référence (bare-metal / dev)
│   ├── server.py              # Serveur MQTT-GStreamer — version bare-metal
│   ├── pControler-from-JSON.py # Contrôleur JSON de séquences d'enregistrement
│   ├── node-red/              # Flows Node-Red (All_Flows.json)
│   └── configs/SAV/           # Configurations JSON de pipelines sauvegardées
├── docker/                    # Stack Docker Compose (production portable)
│   ├── docker-compose.yml     # Orchestration : mosquitto + echo-core + echo-ui + portainer
│   ├── .env                   # Variables d'environnement (chemins, MQTT, timezone)
│   ├── core/                  # Image echo-core : gstd compilé + server.py
│   │   ├── dockerfile         # Build Python 3.11 + compile gstd depuis source
│   │   ├── server.py          # ⚠️ Copie divergée de core/server.py (lit les vars d'env)
│   │   └── entrypoint.sh      # Démarre gstd puis python3 server.py
│   ├── node-red/              # Image echo-ui : Node-Red + plugins
│   │   └── data/              # Flows et settings Node-Red persistés
│   └── mosquitto/             # Config broker MQTT
├── deploy/                    # Installation bare-metal (Raspberry Pi)
│   ├── server_install.sh      # Script d'installation complet
│   ├── gstd.service           # Service systemd GSTD
│   └── mqtt_server.service    # Service systemd serveur Python (core/server.py)
├── samples/                   # Scripts utilitaires et tests
│   ├── list_camera/           # Listage des caméras Basler connectées
│   ├── export_camera_config/  # Export des paramètres caméra
│   ├── test_gst_daemon/       # Test de connectivité GSTD
│   └── record_video/          # Exemple d'enregistrement direct
├── Hardware/                  # Références matérielles : NAS Synology DS423, Raspberry Pi 5 16 GB
├── private/                   # Fichiers de config locaux non versionnés (ex : ConfigNas.conf)
└── EXPORT_VIDEOS/             # Répertoire de sortie vidéo (volume monté)
```

## Configuration Docker

**Fichier principal :** `docker/docker-compose.yml`
**Variables d'environnement :** `docker/`.env`

| Variable | Valeur par défaut | Usage |
|---|---|---|
| `LOCAL_VIDEO_PATH` | `/mnt/NVME/EXPORT_VIDEOS` | Stockage vidéo sur l'hôte |
| `MQTT_BROKER` | `127.0.0.1` | Adresse du broker |
| `MQTT_PORT` | `1883` | Port MQTT |
| `TIMEZONE` | `Europe/Paris` | Timezone des containers |
| `NAS_HOST` | `192.168.0.17` | IP/hostname du NAS (utilisée pour le ping de connectivité depuis l'UI) |

Le fichier `docker/.env` est monté dans le container echo-core en `/app/config.env` afin que l'UI Node-Red puisse mettre à jour `NAS_HOST` à chaud sans redémarrer la stack.

**Démarrer la stack :**
```bash
cd docker && docker compose up -d
```

**Accès :**
- Node-Red UI : `http://localhost:1880`
- Node-Red Dashboard : `http://localhost:1880/ui`
- Portainer : `http://localhost:9000`

## Format des configurations pipeline

Les configs JSON (dans `core/configs/SAV/`) définissent une session d'enregistrement :

```json
{
  "conf": {
    "pipeline_name": "pipeline1",
    "ID_Serie": "Serie1",
    "ID_Bassin": "Bassin_1",
    "ID_Arene": "Arene_2",
    "ID_Sequence": "Seq1",
    "location": "rtsp://192.168.1.26:8554/sub/av",
    "video_Path": "/path/to/EXPORT_VIDEOS/",
    "max_size_time": "15",
    "max_size_file": "10"
  },
  "orders": [
    {"order": "play", "duration": "30"},
    {"order": "pause", "duration": "120"},
    {"order": "play", "duration": "120"}
  ]
}
```

**Convention de nommage des fichiers vidéo :**
`{timestamp}_{ID_SERIE}_{pipeline}_{ID_BASSIN}_{ID_ARENE}_{ID_SEQUENCE}_NNN.mov`

## Topics MQTT

| Topic | Sens | Usage |
|---|---|---|
| `gstreamer/control` | UI → serveur | Commandes JSON (create, play, pause, stop, stop_ALL, status) |
| `server/log` | serveur → UI | Mises à jour d'état en temps réel |

## Commandes MQTT supportées par `server.py`

- `create_pipeline` — crée un pipeline GStreamer RTSP
- `play` — démarre/reprend l'enregistrement
- `pause` — met en pause
- `stop` — arrête et détruit un pipeline
- `stop_ALL` — arrêt d'urgence de tous les pipelines
- `status` — retourne l'état courant des pipelines

## Flows Node-Red — onglets UI

| Onglet (dev) | Onglet Dashboard | Rôle |
|---|---|---|
| *(flows principaux)* | Contrôle / Monitoring | Création de pipelines, enregistrement, logs |
| `Ping Equipements` | Config Matériel → Equipements | Ping réseau des caméras, NAS et routeur |
| `Liste Caméras` | — | Listage des caméras Basler disponibles |
| `Read Pipeline` | Read Pipeline(s) | Affichage/lecture des configs pipeline JSON |

L'onglet "Config Matériel" remplace l'ancien "Tab 4" et centralise les infos réseau + équipements.

## Notes de développement

- Les fichiers `pipeline*.json` sont exclus du dépôt git (contiennent des IPs et chemins locaux).
- Les fichiers `.mov` sont exclus du dépôt git.
- `node_modules/` est exclu du dépôt git.
- Le dossier `private/` contient des configs locales non versionnées (ex : `ConfigNas.conf`).
- Le fichier `core/node-red/All_Flows.json` est la source de vérité pour les flows Node-Red — ne pas modifier directement les flows dans `docker/node-red/data/` si les deux existent.
- La stack Docker utilise le réseau `host` pour les services MQTT/GStreamer (nécessaire pour accéder aux périphériques `/dev/`).
- Pour le déploiement bare-metal Raspberry Pi, utiliser `deploy/server_install.sh`.
