#!/bin/bash

echo "--- Démarrage de GSTD ---"
/usr/local/bin/gstd &

echo "--- Attente de 10sec pour GSTD ---"
sleep 10

echo "--- Lancement du Serveur Python ECHO ---"
# On se place là où est le script pour éviter les erreurs d'import
cd /app
python3 server.py