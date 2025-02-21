import threading
import json
import time
import os
import datetime
import paho.mqtt.client as mqtt
from pygstc.gstc import *
from pygstc.logger import *

# Configuration MQTT
MQTT_BROKER = "localhost"
MQTT_TOPIC = "gstreamer/control"
MQTT_LOG_SERVER = "server/log"
MQTT_PORT = 1883

# Paramètres de pipeline
export_directory_file = "/home/bibi/NAS/code/ECHO-PROJECT/EXPORT_VIDEOS/"
camera_location = "rtsp://admin:JKFLFO@172.24.1.112/11"
pipiline_name_display = "DISPLAY_VideoSalon"

# Création du client gstd
gstd_logger = CustomLogger('pygstc_example', loglevel='DEBUG')
gstd_client = GstdClient()

def checkCreationPipeline(pipe_Name):
    pipelines = gstd_client.list_pipelines()
    for pipeline in pipelines:
        pName = pipeline['name']
        state = gstd_client.read(f'pipelines/{pName}/state')['value']
        if pipe_Name == pName:
            print(f"Pipeline {pName} existe déjà avec le state = {state}. Commande de création refusée.")
            return False
    return True

def checkCommandOnPipeline(pipe_Name):
    pipelines = gstd_client.list_pipelines()
    for pipeline in pipelines:
        pName = pipeline['name']
        state = gstd_client.read(f'pipelines/{pName}/state')['value']
        if pipe_Name == pName:
            return True
    return False

def create_pipeline(client, pipe_Name, payload):
    try:
        ID_Serie = payload.get("ID_Serie")
        ID_Bassin = payload.get("ID_Bassin")
        ID_Arene = payload.get("ID_Arene")
        ID_Sequence = payload.get("ID_Sequence")
        ID_Camera = payload.get("ID_Camera")
        pipe_Location = payload.get("location")
        video_Path = payload.get("video_Path")
        max_size_time = payload.get("max_size_time")
        max_size_file = payload.get("max_size_file")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = f"{timestamp}_{ID_Serie}_{pipe_Name}_{ID_Bassin}_{ID_Arene}_{ID_Sequence}_{ID_Camera}_"

        if not os.path.exists(video_Path):
            os.makedirs(video_Path)
        
        pipe_Record = f"rtspsrc location={pipe_Location} latency=1000 \
            ! queue ! rtph264depay ! h264parse \
            ! queue ! h264parse \
            ! splitmuxsink \
            location={video_Path}{video_name}%03d.mov \
            max-size-time={max_size_time} \
            max-size-bytes={max_size_file}"
        
        gstd_client.pipeline_create(pipe_Name, pipe_Record)
        print(f"✅ Pipeline {pipe_Name} créé avec succès")
        
        state = "created"
        message = {"state": state, "pipeline_name": pipe_Name}
        json_message = json.dumps(message)
        client.publish(MQTT_LOG_SERVER, json_message)

    except (GstcError, GstdError) as e:
        print(f"Error creating pipeline {pipe_Name}: {e}")

def play_pipeline(client, pipe_Name):
    try:
        gstd_client.pipeline_play(pipe_Name)
        state = gstd_client.read(f'pipelines/{pipe_Name}/state')
        print(f"🚦 État du pipeline après démarrage : {state}")
        state = "playing"
        message = {"state": state, "pipeline_name": pipe_Name}
        json_message = json.dumps(message)
        client.publish(MQTT_LOG_SERVER, json_message)
    except (GstcError, GstdError) as e:
        print(f"Error playing pipeline {pipe_Name}: {e}")

def pause_pipeline(client, pipe_Name):
    try:
        gstd_client.pipeline_pause(pipe_Name)
        state = "paused"
        message = {"state": state, "pipeline_name": pipe_Name}
        json_message = json.dumps(message)
        client.publish(MQTT_LOG_SERVER, json_message)
    except (GstcError, GstdError) as e:
        print(f"Error pausing pipeline {pipe_Name}: {e}")

def stop_pipeline(client, pipe_Name):
    try:
        gstd_client.event_eos(pipe_Name)
        time.sleep(5)
        gstd_client.pipeline_stop(pipe_Name)
        gstd_client.pipeline_delete(pipe_Name)
        state = "deleted"
        message = {"state": state, "pipeline_name": pipe_Name}
        json_message = json.dumps(message)
        client.publish(MQTT_LOG_SERVER, json_message)
        print(f"🛑 Arrêt du pipeline : {pipe_Name} terminé")
    except (GstcError, GstdError) as e:
        print(f"Error stopping pipeline {pipe_Name}: {e}")

# Callback : Réception d'un message MQTT
def on_message(client, userdata, msg):
    try:
        raw_payload = msg.payload.decode()
        print(f"Message MQTT reçu : {raw_payload}")

        payload = json.loads(raw_payload)
        if not isinstance(payload, dict):
            print("❌ Erreur : Le payload MQTT n'est pas un dictionnaire JSON valide")
            return
        
        command = payload.get("order")
        pipe_Name = payload.get("pipeline_name")
        print(f"📩 Commande MQTT reçue : {command} / pipe_Name : {pipe_Name}")

        if command == "create_pipeline" and checkCreationPipeline(pipe_Name):
            thread = threading.Thread(target=create_pipeline, args=(client, pipe_Name, payload))
            thread.start()

        elif command == "play" and checkCommandOnPipeline(pipe_Name):
            thread = threading.Thread(target=play_pipeline, args=(client, pipe_Name))
            thread.start()

        elif command == "pause" and checkCommandOnPipeline(pipe_Name):
            thread = threading.Thread(target=pause_pipeline, args=(client, pipe_Name))
            thread.start()

        elif command == "stop": #and checkCommandOnPipeline(pipe_Name):
            thread = threading.Thread(target=stop_pipeline, args=(client, pipe_Name))
            thread.start()

        elif command == "status":
            pipelines = gstd_client.list_pipelines()
            for pipeline in pipelines:
                pipe_name = pipeline['name']
                state = gstd_client.read(f'pipelines/{pipe_name}/state')['value']
                print(f"Pipeline: {pipe_name} - State: {state}")
                message = f"Status command Pipeline: {pipe_name} - State: {state}"
                json_message = json.dumps(message)
                client.publish(MQTT_LOG_SERVER, json_message)
        elif command == "stop_ALL":
            print("Stop d'urgence envoyé, on coupe toutes les pipelines")
            pipelines = gstd_client.list_pipelines()
            for pipeline in pipelines:
                pipe_name = pipeline['name']
                state = gstd_client.read(f'pipelines/{pipe_name}/state')['value']
                gstd_client.pipeline_stop(pipe_name)
                gstd_client.pipeline_delete(pipe_name)

                message = {"state": "stopped", "pipeline_name": pipe_name}
                json_message = json.dumps(message)
                client.publish(MQTT_LOG_SERVER, json_message)
                print(f"Message MQTT envoyé : {message}")

            print("\n🔴 Arrêt des pipelines terminés")
        else:
            print(f"Command : {command} inconnue côté serveur")

    except json.JSONDecodeError as e:
        print(f"Erreur lors du parsing du JSON: {e}")

# Callback : Connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    print("📡 Connecté au broker MQTT")
    client.subscribe(MQTT_TOPIC)

# Connexion MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    # Boucle infinie pour recevoir les messages MQTT
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🔴 Arrêt du programme et fermeture propre des pipelines existants dans Gstd")
    pipelines = gstd_client.list_pipelines()
    for pipeline in pipelines:
        pipe_name = pipeline['name']
        state = gstd_client.read(f'pipelines/{pipe_name}/state')['value']
        print(f"Pipeline: {pipe_name} - State: {state}")
        gstd_client.pipeline_stop(pipe_name)
        gstd_client.pipeline_delete(pipe_name)
    print("\n🔴 Arrêt du programme terminé")
