📂 Procédure de Déploiement & Maintenance - Projet ECHO

Ce répertoire contient l'ensemble des scripts et configurations nécessaires pour reconstruire le système à partir de zéro en cas de défaillance matérielle (notamment corruption de carte SD).
🚀 Déploiement Rapide (Quick Start)

Si vous devez réinstaller le système sur un nouveau Raspberry Pi :

    Préparation de l'OS à partir de : Installer Ubuntu Server ou Raspberry Pi OS (64-bit).

    Clonage du projet :
    Bash

    git clone https://github.com/votre-repo/echo-project.git
    cd echo-project/deploy

    Installation des dépendances :
    Bash

    chmod +x setup_system.sh
    ./setup_system.sh

🛠 Architecture du Déploiement

Le projet repose sur deux modes de fonctionnement :
1. Mode Conteneurisé (Docker) - Recommandé

La pile technique est isolée pour éviter les conflits de versions.

    Lancement : docker-compose up -d
    Services inclus : Node-RED, MQTT Broker, AgentDVR (via image compatible ARM64).
    Avantage : Migration instantanée sur n'importe quel autre ordinateur.

2. Mode Natif (Services Systemd)

Pour les scripts Python critiques (Core GStreamer) nécessitant un accès direct au matériel.

    Logs : journalctl -u echo-core.service -f
    Redémarrage : sudo systemctl restart echo-core

💾 Stratégie de Sauvegarde (Backup)

Pour éviter de perdre la configuration des caméras (AgentDVR) :

    Localisation de la config : /home/pi/AgentDVR/Media/XML/

    Procédure de sauvegarde :

        Modifier la configuration via l'interface web (Port 8090).

        Exécuter ./backup_config.sh dans ce répertoire.

        Faire un git push pour synchroniser sur le dépôt distant.

⚠️ Points de Vigilance (Maintenance)
Composant	Risque	Solution
Carte SD	Corruption après coupure de courant	Utiliser un disque NVME pour les écritures (logs/vidéos).
Flux RTSP	Changement d'IP des caméras	Mettre à jour objects.xml dans le dossier backup.
Connectivité	Perte du Remote Shell	systemctl --user restart rpi-connect.
📞 Support & Contacts


# Commandes utiles

### Log server-Echo de l'orchestrateur
Permet de voir si le service Python orchestre correctement les pipelines

    sudo journalctl -u mqtt_server.service -f

### Connection à distance avec Rpi-connect
Pour tester et vérifier l'état de la connexion Raspberry Pi Connect, la commande principale à utiliser directement dans ton terminal est :
Bash

    rpi-connect status

Ce qu'il faut surveiller dans le résultat :
| TLigne | État idéal | Signification |
| :--- | :--- | :--- |
| Signed in | yes | Le compte est bien lié au Pi. |
| Subscribed to events | yes | Le Pi communique bien avec les serveurs de Relay |
| Screen sharing | allowed | Le partage d'écran est possible (nécessite Wayland). |
| Remote shell | allowed | L'accès au terminal via le web est activé. |

Autres commandes utiles :
### Vérifier si le service tourne (système) :

    systemctl --user status rpi-connect

### Forcer le partage si "disallowed" :

    rpi-connect host on

### Se reconnecter (si déconnecté) :

    rpi-connect sign-in

Voir si une session est déjà ouverte (ce qui bloque souvent le portail) :
Regarde la ligne (X sessions active) à la fin du rpi-connect status. Si c'est à 1, le portail web te dira souvent "Not available".
