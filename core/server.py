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
        
        # Enregistrer les paramètres pour ce pipeline
        store_pipeline_params(pipe_Name, pipe_Location, video_Path, video_name, max_size_time, max_size_file)

        # Creation de la pipeline 
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
    # """ Met le pipeline en pause proprement en envoyant un EOS """
    try:
        print(f"🛑 Envoi EOS avant la pause pour {pipe_Name}")
        gstd_client.event_eos(pipe_Name)
        time.sleep(5)
        gstd_client.pipeline_stop(pipe_Name)
        time.sleep(2)
        gstd_client.pipeline_delete(pipe_Name)
        
        # state = gstd_client.read(f'pipelines/{pipe_Name}/state')
        # print(f"🚦 État du pipeline après démarrage : {state}")

        print(f"⏸️ Pipeline {pipe_Name} mis en pause proprement.")

        message = {"state": "paused", "pipeline_name": pipe_Name}
        client.publish(MQTT_LOG_SERVER, json.dumps(message))

        # on le recrée juste aprés pour faire play quand il faudra 
        # Récupérer les paramètres du pipeline
        payload = retrieve_pipeline_payload(pipe_Name)
        if payload is None:
            print(f"❌ Impossible de récupérer les paramètres pour {pipe_Name}")
            return
        print(f"PAUSE : payload : {payload}")
        # Recréer le pipeline avec les paramètres récupérés
        pipe_Record = payload.get("pipe_record")
        gstd_client.pipeline_create(pipe_Name, pipe_Record)
        time.sleep(2)
        print(f"⏸️ Pipeline {pipe_Name} recrée avec pipeRecord = {pipe_Record}")

    except (GstcError, GstdError) as e:
        print(f"❌ Erreur pause pipeline {pipe_Name}: {e}")

# Dictionnaire global pour stocker les paramètres des pipelines
pipeline_params = {}

def store_pipeline_params(pipe_Name, pipe_Location, video_Path, video_name, max_size_time, max_size_file):
    """ Fonction pour stocker les paramètres du pipeline dans le dictionnaire """
    pipeline_params[pipe_Name] = {
        "pipe_Location": pipe_Location,
        "video_Path": video_Path,
        "video_name": video_name,
        "max_size_time": max_size_time,
        "max_size_file": max_size_file,
        "nbPause":0
    }
    print(f"📦 Paramètres du pipeline {pipe_Name} enregistrés.\n {pipeline_params[pipe_Name]}")

def retrieve_pipeline_payload(pipe_Name):
    #""" Récupère les informations pour recréer un pipeline spécifique """
    try:
        # Vérifier si les paramètres du pipeline existent
        if pipe_Name not in pipeline_params:
            print(f"❌ Paramètres non trouvés pour le pipeline {pipe_Name}")
            return None

        # Récupérer les paramètres enregistrés pour ce pipeline
        params = pipeline_params[pipe_Name]
        nbPause = pipeline_params[pipe_Name]["nbPause"]
        nbPause += 1  # Incrémenter le compteur de pause
        pipeline_params[pipe_Name]["nbPause"] = nbPause  # Mettre à jour le compteur de pause
        print(f"Retrive pipeline nbPause = {nbPause}")
        
        # Construire le record de la pipeline avec l'incrément
        pipe_record = f"rtspsrc location={params['pipe_Location']} latency=1000 ! queue ! rtph264depay ! h264parse ! splitmuxsink location={params['video_Path']}{params['video_name']}-{nbPause}%03d.mov max-size-time={params['max_size_time']} max-size-bytes={params['max_size_file']}"

        # Retourner le payload du pipeline à recréer
        return {
            "pipe_record": pipe_record
        }
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des paramètres du pipeline {pipe_Name}: {e}")
        return None



def stop_pipeline(client, pipe_Name):
    try:
        gstd_client.event_eos(pipe_Name)
        time.sleep(5)
        gstd_client.pipeline_stop(pipe_Name)
        time.sleep(2)
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
