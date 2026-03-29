#!/usr/bin/env bash
# =============================================================================
# ECHO-PROJECT — Script d'installation one-liner
#
# Usage :
#   curl -fsSL https://raw.githubusercontent.com/TamataOcean/ECHO-PROJECT/master/deploy/install.sh | bash
#
# Options (variables d'environnement) :
#   INSTALL_DIR   Répertoire d'installation  (défaut : $HOME/ECHO-PROJECT)
#   VIDEO_PATH    Chemin stockage vidéo hôte (défaut : /mnt/NVME/EXPORT_VIDEOS)
#   NAS_HOST      IP/hostname du NAS         (défaut : vide)
#   NAS_SHARE     Nom du partage CIFS        (défaut : vide)
#   NAS_USER      Utilisateur NAS            (défaut : vide)
#   NAS_PASS      Mot de passe NAS           (défaut : vide)
#   BRANCH        Branche git à cloner       (défaut : master)
#   AUTOSTART     Installer service systemd  (défaut : false)
#
# Exemple avec options :
#   curl -fsSL .../install.sh | \
#     VIDEO_PATH=/data/videos NAS_HOST=192.168.0.17 AUTOSTART=true bash
# =============================================================================

set -euo pipefail

# --- Couleurs ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# --- Détection Raspberry Pi ---
IS_RASPBERRY_PI=false
RPI_MODEL=""
if [[ -f /proc/device-tree/model ]]; then
    RPI_MODEL=$(tr -d '\0' < /proc/device-tree/model)
    if [[ "$RPI_MODEL" == *"Raspberry Pi"* ]]; then
        IS_RASPBERRY_PI=true
    fi
fi

# --- Paramètres ---
INSTALL_DIR="${INSTALL_DIR:-$HOME/ECHO-PROJECT}"
VIDEO_PATH="${VIDEO_PATH:-/mnt/NVME/EXPORT_VIDEOS}"
NAS_HOST="${NAS_HOST:-}"
NAS_SHARE="${NAS_SHARE:-}"
NAS_USER="${NAS_USER:-}"
NAS_PASS="${NAS_PASS:-}"
BRANCH="${BRANCH:-master}"
AUTOSTART="${AUTOSTART:-false}"
REPO_URL="https://github.com/TamataOcean/ECHO-PROJECT.git"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        ECHO-PROJECT — Installation           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# 1. Vérification OS
# =============================================================================
info "Vérification du système..."
if [[ "$(uname -s)" != "Linux" ]]; then
    error "Ce script requiert Linux."
fi

if $IS_RASPBERRY_PI; then
    info "Raspberry Pi détecté : $RPI_MODEL ($(uname -m))"
fi

# =============================================================================
# 2. Raspberry Pi — cgroups mémoire (requis pour Docker)
# =============================================================================
if $IS_RASPBERRY_PI; then
    # Raspberry Pi OS Bookworm : cmdline dans /boot/firmware/cmdline.txt
    # Raspberry Pi OS Bullseye et antérieur : /boot/cmdline.txt
    if [[ -f /boot/firmware/cmdline.txt ]]; then
        CMDLINE_FILE="/boot/firmware/cmdline.txt"
    elif [[ -f /boot/cmdline.txt ]]; then
        CMDLINE_FILE="/boot/cmdline.txt"
    else
        CMDLINE_FILE=""
        warn "Fichier cmdline.txt introuvable — vérifiez les cgroups manuellement."
    fi

    if [[ -n "$CMDLINE_FILE" ]]; then
        NEEDS_REBOOT=false
        if ! grep -q "cgroup_enable=memory" "$CMDLINE_FILE"; then
            info "Activation des cgroups mémoire dans $CMDLINE_FILE..."
            # Ajouter en fin de la première ligne (cmdline.txt est sur une seule ligne)
            sed -i '1s/$/ cgroup_enable=memory cgroup_memory=1/' "$CMDLINE_FILE"
            NEEDS_REBOOT=true
            success "cgroups mémoire activés."
        else
            success "cgroups mémoire déjà activés."
        fi

        if $NEEDS_REBOOT; then
            echo ""
            echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${YELLOW}║  REDÉMARRAGE REQUIS pour activer les cgroups mémoire.        ║${NC}"
            echo -e "${YELLOW}║  Relancez ce script après le reboot pour continuer.          ║${NC}"
            echo -e "${YELLOW}║                                                              ║${NC}"
            echo -e "${YELLOW}║    sudo reboot                                               ║${NC}"
            echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            exit 0
        fi
    fi
fi

# =============================================================================
# 3. Docker
# =============================================================================
install_docker() {
    info "Installation de Docker via get.docker.com..."
    curl -fsSL https://get.docker.com | sh
    # Ajouter l'utilisateur courant au groupe docker
    if [[ -n "${SUDO_USER:-}" ]]; then
        usermod -aG docker "$SUDO_USER"
    else
        usermod -aG docker "$USER" 2>/dev/null || true
    fi
    systemctl enable --now docker
    success "Docker installé."
}

if ! command -v docker &>/dev/null; then
    warn "Docker non trouvé."
    install_docker
else
    success "Docker $(docker --version | awk '{print $3}' | tr -d ',')"
fi

# Vérifier docker compose (plugin v2)
if ! docker compose version &>/dev/null; then
    error "Docker Compose plugin introuvable. Installez Docker >= 23 (inclut compose)."
fi
success "Docker Compose $(docker compose version --short)"

# =============================================================================
# 4. Git
# =============================================================================
if ! command -v git &>/dev/null; then
    info "Installation de git..."
    apt-get install -y git 2>/dev/null || error "Impossible d'installer git. Installez-le manuellement."
fi
success "git $(git --version | awk '{print $3}')"

# =============================================================================
# 5. Clonage du dépôt
# =============================================================================
if [[ -d "$INSTALL_DIR/.git" ]]; then
    info "Dépôt existant détecté dans $INSTALL_DIR — mise à jour..."
    git -C "$INSTALL_DIR" fetch origin
    git -C "$INSTALL_DIR" checkout "$BRANCH"
    git -C "$INSTALL_DIR" pull origin "$BRANCH"
    success "Dépôt mis à jour."
else
    info "Clonage dans $INSTALL_DIR (branche : $BRANCH)..."
    git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    success "Dépôt cloné."
fi

cd "$INSTALL_DIR"

# =============================================================================
# 6. Configuration .env
# =============================================================================
if [[ ! -f ".env" ]]; then
    info "Création du fichier .env depuis .env.example..."
    cp .env.example .env
fi

# Mettre à jour les valeurs dans .env
set_env() {
    local key="$1" val="$2"
    if grep -q "^${key}=" .env; then
        sed -i "s|^${key}=.*|${key}=${val}|" .env
    else
        echo "${key}=${val}" >> .env
    fi
}

set_env "LOCAL_VIDEO_PATH" "$VIDEO_PATH"
[[ -n "$NAS_HOST"  ]] && set_env "NAS_HOST"  "$NAS_HOST"
[[ -n "$NAS_SHARE" ]] && set_env "NAS_SHARE" "$NAS_SHARE"
[[ -n "$NAS_USER"  ]] && set_env "NAS_USER"  "$NAS_USER"
[[ -n "$NAS_PASS"  ]] && set_env "NAS_PASS"  "$NAS_PASS"

success ".env configuré (LOCAL_VIDEO_PATH=$VIDEO_PATH)"

# =============================================================================
# 7. Création du répertoire vidéo
# =============================================================================
if [[ ! -d "$VIDEO_PATH" ]]; then
    info "Création du répertoire vidéo : $VIDEO_PATH"
    mkdir -p "$VIDEO_PATH" || warn "Impossible de créer $VIDEO_PATH — à faire manuellement si nécessaire."
fi

# =============================================================================
# 8. Build et démarrage de la stack
# =============================================================================
info "Build de l'image Docker (peut prendre plusieurs minutes)..."
docker compose build

info "Démarrage de la stack..."
docker compose up -d

success "Stack démarrée."

# =============================================================================
# 9. Service systemd (optionnel)
# =============================================================================
if [[ "$AUTOSTART" == "true" ]]; then
    if ! command -v systemctl &>/dev/null; then
        warn "systemd non disponible — installation du service ignorée."
    else
        info "Installation du service systemd echo-project..."
        SERVICE_FILE="/etc/systemd/system/echo-project.service"
        cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Echo Project — Système d'acquisition vidéo ECHO
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStartPre=/usr/bin/docker compose build --no-cache
ExecStart=/usr/bin/docker compose up
ExecStop=/usr/bin/docker compose down
Restart=on-failure
RestartSec=15s
TimeoutStartSec=600
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl enable echo-project.service
        success "Service systemd installé et activé (démarrage automatique au boot)."
    fi
fi

# =============================================================================
# Résumé
# =============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation terminée !              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Répertoire : ${CYAN}$INSTALL_DIR${NC}"
echo -e "  Vidéos     : ${CYAN}$VIDEO_PATH${NC}"
echo ""
echo -e "  ${YELLOW}Interfaces disponibles :${NC}"
echo -e "    Node-Red flows     →  http://localhost:1880"
echo -e "    Node-Red Dashboard →  http://localhost:1880/ui"
echo ""
echo -e "  Commandes utiles :"
echo -e "    Logs    : ${CYAN}docker compose -C $INSTALL_DIR logs -f${NC}"
echo -e "    Stop    : ${CYAN}docker compose -C $INSTALL_DIR down${NC}"
echo -e "    Restart : ${CYAN}docker compose -C $INSTALL_DIR restart${NC}"
echo ""
