# V1.0 Programme permettant à partir d'un flux RTSP d'enregistrer des vidéos à la demande 
# en fonction des commandes MQTT reçue.
from pygstc.gstc import *
from pygstc.logger import *
import paho.mqtt.client as mqtt
import os

# Configurations MQTT
MQTT_BROKER = "localhost"  # Remplace par ton broker MQTT
MQTT_TOPIC = "gstreamer/control"  # Le topic auquel tu t'abonnes
MQTT_PORT = 1883

# Configuration du pipeline dans gstd
#pipeline_str = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=100 ! watchdog timeout=200 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"

pipeline_name_record = "RECORD_VideoSalon"
pipiline_name_display = "DISPLAY_VideoSalon"

export_directory_file = "/home/bibi/code/ECHO-PROJECT/TEST_VIDEOS/Bassin_A/"
camera_location = "rtsp://admin:JKFLFO@172.24.1.112/11"

# Vérifier et créer le répertoire de destination (export_directory_file) si nécessaire
if not os.path.exists(export_directory_file):
    os.makedirs(export_directory_file)
    print(f"📁 Répertoire créé : {export_directory_file}")
else:
    print(f"📂 Répertoire déjà existant : {export_directory_file}")

pipeline_display = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! fpsdisplaysink sync=false"
pipeline_record = f"rtspsrc location={camera_location} latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location={export_directory_file}video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"

# Création du client gstd
gstd_logger = CustomLogger('pygstc_example', loglevel='DEBUG')
gstd_client = GstdClient(logger=gstd_logger)

# Création du pipeline Display
# gstd_client.pipeline_create(pipiline_name_display, pipeline_display)
# print(f"✅ Pipeline {pipeline_name_record} créé avec succès")
# pipelines = gstd_client.read("pipelines")
# print(f"📜 Liste des pipelines actifs : {pipelines}")

# # Création du pipeline Record
# gstd_client.pipeline_create(pipeline_name_record, pipeline_record)
# print(f"✅ Pipeline {pipeline_name_record} créé avec succès")
# pipelines = gstd_client.read("pipelines")
# print(f"📜 Liste des pipelines actifs : {pipelines}")

# Callback : Connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    print("📡 Connecté au broker MQTT")
    client.subscribe(MQTT_TOPIC)

# Callback : Réception d'un message MQTT
def on_message(client, userdata, msg):
    try:
        #command = msg.payload.decode()
        payload = json.loads(msg.payload.decode())
        command = payload.get("order")
        camera_ID = payload.get("camera_ID")
        print(f"📩 Commande MQTT reçue : {command} / camera_ID : {camera_ID}")
        pipe_Name = payload.get("pipeline_name")

        if command == "create_pipeline":
            # Recupération des parametres de création 
            pipe_Location = payload.get("location")

            print(f"▶️ Creation du pipeline : {pipe_Name} / location : {pipe_Location} ")
            # Création du pipeline
            pipe_Record = f"rtspsrc location={pipe_Location} latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location={export_directory_file}{pipe_Name}%02d.mov max-size-time=10000000000 max-size-bytes=1000000"
            try:
                gstd_client.pipeline_create(pipe_Name, pipe_Record)
                print(f"✅ Pipeline {pipe_Name} créé avec succès")
            except(GstcError, GstdError) as e:
                print(f"Error on Pipeline {pipe_Name} Error : {e}")

        elif command == "start":
            print(f"▶️ Démarrage du pipeline : {pipe_Name}")
            gstd_client.pipeline_play(pipe_Name)
            # Vérifier l'état du pipeline
            state = gstd_client.read(f'pipelines/{pipe_Name}/state')
            print(f"🚦 État du pipeline après start : {state}")

        elif command == "pause":
            print(f"⏸️ Pause du pipeline : {pipe_Name}")
            gstd_client.pipeline_pause(pipe_Name)

        elif command == "resume":
            print(f"▶️ Reprise du pipeline : {pipe_Name}")
            gstd_client.pipeline_play(pipe_Name)

        elif command == "stop":
            print(f"🛑 Arrêt du pipeline : {pipe_Name}")
            gstd_client.pipeline_stop(pipe_Name)
        
        # Renvoie les "states" de tous les pipelines. 
        elif command == "status":
            pipelines = gstd_client.list_pipelines()  # Liste des pipelines
            for pipeline in pipelines:
                pipe_name = pipeline['name']  # Ou pipeline.name, selon la structure de votre pipeline
                # Lire l'état du pipeline en utilisant la méthode read
                state = gstd_client.read(f'pipelines/{pipe_name}/state')['value']
                print(f"Pipeline: {pipe_name} - State: {state}")

        elif command == "status_record":
            print(gstd_client.read(f'pipelines/{pipe_Name}/state')['value'])

        elif command == "start_display":
            gstd_client.pipeline_play(pipiline_name_display)

        elif command == "pause_display":
            gstd_client.pipeline_pause(pipiline_name_display)

        elif command == "stop_display":
            gstd_client.pipeline_stop(pipiline_name_display)
        
        # Erreur sur la commande
        else:
            print(f"Command : {command} inconnue côté server")
    
    except json.JSONDecodeError as e:
        print(f"Erreur lors du parsing du JSON: {e}")

# Connexion MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    # Boucle infinie pour recevoir les messages MQTT
    client.loop_forever()

except KeyboardInterrupt:
    print("\n🔴 Arrêt du programme.")
    gstd_client.pipeline_stop(pipeline_name_record)
    gstd_client.pipeline_delete(pipeline_name_record)
    gstd_client.pipeline_stop(pipiline_name_display)
    gstd_client.pipeline_delete(pipiline_name_display)