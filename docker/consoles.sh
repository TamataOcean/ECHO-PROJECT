#!/bin/bash

# Ouverture du terminal pour MOSQUITTO (Logs en temps réel)
 gnome-terminal --title="MQTT Logs" -- bash -c "docker exec -it echo-mqtt mosquitto_sub -v -t '#'; exec bash" &

# Ouverture du terminal pour ECHO-CORE (Console Python/Gstd)
 gnome-terminal --title="CORE - Python & Gstd" -- bash -c "docker exec -it echo-core bash; exec bash" &

# Ouverture du terminal pour NODE-RED (Logs système)
 gnome-terminal --title="NODE-RED Console" -- bash -c "docker exec -it echo-ui /bin/bash; exec bash" &

echo "Les 3 terminaux ont été lancés."