#!/bin/bash
# Monte le partage NAS CIFS sur /app/EXPORT_VIDEOS
# Lit la config depuis /app/config.env

if [ -f /app/config.env ]; then
    export $(grep -v '^#' /app/config.env | grep -E '^NAS_' | xargs)
fi

if [ -z "$NAS_HOST" ] || [ -z "$NAS_SHARE" ]; then
    echo "ERREUR: NAS_HOST ou NAS_SHARE non configuré" >&2
    exit 1
fi

# Démonter si déjà monté
# umount /app/EXPORT_VIDEOS 2>/dev/null || true
umount /mnt/raspi_travel 2>/dev/null || true

# Écrire les credentials dans un fichier temporaire
printf "username=%s\npassword=%s\n" "${NAS_USER:-}" "${NAS_PASS:-}" > /tmp/nas.cred
chmod 600 /tmp/nas.cred

# Montage CIFS
mount -t cifs "//${NAS_HOST}/${NAS_SHARE}" /app/EXPORT_VIDEOS \
    -o username=${NAS_USER},password=${NAS_PASS},vers=3.0,iocharset=utf8,uid=1000,gid=1000,file_mode=0777,dir_mode=0777

STATUS=$?
rm -f /tmp/nas.cred

if [ $STATUS -eq 0 ]; then
    echo "OK: //${NAS_HOST}/${NAS_SHARE} monté sur /app/EXPORT_VIDEOS"
else
    echo "ERREUR: montage échoué (code $STATUS)" >&2
    exit $STATUS
fi
