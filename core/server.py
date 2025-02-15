# V1.0 Programme permettant à partir d'un flux RTSP d'enregistrer des vidéos à la demande 
# en fonction des commandes MQTT reçue.
from pygstc.gstc import *
from pygstc.logger import *
import paho.mqtt.client as mqtt
import os
import time
import datetime

# Configurations MQTT
MQTT_BROKER = "localhost"  # Remplace par ton broker MQTT
MQTT_TOPIC = "gstreamer/control"  # Le topic auquel tu t'abonnes
MQTT_LOG_SERVER = "server/log"

MQTT_PORT = 1883

# Configuration du pipeline dans gstd
#pipeline_str = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=100 ! watchdog timeout=200 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"
pipiline_name_display = "DISPLAY_VideoSalon"

# PARAMETRE pour GSTD 
# defautl
# max_size_file = 10000000 # 10 Mo (1 000 000 octets).
# max_size_time = 60000000000 # 60 secondes = 10 × 60 × 1 000 000 000 ns

export_directory_file = "/home/bibi/NAS/code/ECHO-PROJECT/EXPORT_VIDEOS/"
camera_location = "rtsp://admin:JKFLFO@172.24.1.112/11"

pipeline_display = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! fpsdisplaysink sync=false"
pipeline_record = f"rtspsrc location={camera_location} latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location={export_directory_file}video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"

# pipeline_webcam = f"v4l2src ! videoconvert ! autovideosink ! splitmuxsink location={export_directory_file}video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"

# Création du client gstd
gstd_logger = CustomLogger('pygstc_example', loglevel='DEBUG')
#gstd_client = GstdClient(logger=gstd_logger)

gstd_client = GstdClient()

# Controle permettant d'éviter la création d'un pipeline du meme nom
def checkCreationPipeline(pipe_Name):
    pipelines = gstd_client.list_pipelines()  # Liste des pipelines
    for pipeline in pipelines:
        pName = pipeline['name']  # Ou pipeline.name, selon la structure de votre pipeline
        # Lire l'état du pipeline en utilisant la méthode read
        state = gstd_client.read(f'pipelines/{pName}/state')['value']
        print(f"Pipeline: {pName} - State: {state}")
        if (pipe_Name == pName ):
            print(f"Pipeline {pName} existe déja avec le state = {state}. Commande de creation refusé ")
            return False
    # Si pas de correspondance trouvé, on retourne vrai
    return True

# Vérifie si une commande peut être envoyée ( par exemple aprés un pipeline delete )
def checkCommandOnPipeline(pipe_Name):
    pipelines = gstd_client.list_pipelines()  # Liste des pipelines
    for pipeline in pipelines:
        pName = pipeline['name']  # Ou pipeline.name, selon la structure de votre pipeline
        # Lire l'état du pipeline en utilisant la méthode read
        state = gstd_client.read(f'pipelines/{pName}/state')['value']
        print(f"Pipeline: {pName} - State: {state}")
        if (pipe_Name == pName ):
            print(f"Pipeline {pipe_Name} existe et peut recevoir une commande ")
            return True
    # Si pas de correspondance trouvé, on retourne vrai
    print(f"Pipeline {pipe_Name} a été deleted et ne peut recevoir une commande, lancer une commande create_pipeline ")
    return False

# Création du pipeline Display
# gstd_client.pipeline_create(pipiline_name_display, pipeline_display)
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
        raw_payload = msg.payload.decode()
        print(f"Message MQTT reçu : {raw_payload}")

        payload = json.loads(raw_payload)
        if not isinstance(payload, dict):
            print("❌ Erreur : Le payload MQTT n'est pas un dictionnaire JSON valide")
            return
        print(f"✅ Payload JSON décodé : {payload}")

        command = payload.get("order")
        pipe_Name = payload.get("pipeline_name")
        print(f"📩 Commande MQTT reçue : {command} / pipe_Name : {pipe_Name}")
        
        if command == "create_pipeline" and checkCreationPipeline(pipe_Name):
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

            # Vérifier et créer le répertoire de destination (video_Path) si nécessaire
            if not os.path.exists(video_Path):
                os.makedirs(video_Path)
                print(f"📁 Répertoire créé : {video_Path}")
            else:
                print(f"📂 Répertoire déjà existant : {video_Path}")
                
            # Recupération des parametres de création 

            print(f"▶️ Creation du pipeline : {pipe_Name} / location : {pipe_Location} ")
            
            # Création du pipeline
            pipe_Record = f"rtspsrc location={pipe_Location} latency=1000 \
                ! queue ! rtph264depay ! h264parse \
                ! queue ! h264parse \
                ! splitmuxsink \
                location={video_Path}{video_name}%03d.mov \
                max-size-time={max_size_time} \
                max-size-bytes={max_size_file}"
            # DEBUG print(f"pipe_Record : {pipe_Record}")

            try:
                gstd_client.pipeline_create(pipe_Name, pipe_Record)
                print(f"✅ Pipeline {pipe_Name} créé avec succès")
                
                # CREATION REUSSI, ENVOI INFO EN MQTT
                state = "created"
                message = {"state": state, "pipeline_name": pipe_Name}

                json_message = json.dumps(message)
                client.publish(MQTT_LOG_SERVER, json_message)

            except(GstcError, GstdError) as e:
                print(f"Error on Pipeline {pipe_Name} Error : {e}")

        elif command == "play" and checkCommandOnPipeline(pipe_Name):
            print(f"▶️ Démarrage du pipeline : {pipe_Name}")
            gstd_client.pipeline_play(pipe_Name)
            # Vérifier l'état du pipeline
            state = gstd_client.read(f'pipelines/{pipe_Name}/state')
            print(f"🚦 État du pipeline après start : {state}")
            # CREATION REUSSI, ENVOI INFO EN MQTT
            state = "playing"
            message = {"state": state, "pipeline_name": pipe_Name}

            json_message = json.dumps(message)
            client.publish(MQTT_LOG_SERVER, json_message)

        elif command == "pause" and checkCommandOnPipeline(pipe_Name):
            print(f"⏸️ Pause du pipeline : {pipe_Name}")
            gstd_client.pipeline_pause(pipe_Name)
            state = "paused"
            message = {"state": state, "pipeline_name": pipe_Name}

            json_message = json.dumps(message)
            client.publish(MQTT_LOG_SERVER, json_message)

        elif command == "resume" and checkCommandOnPipeline(pipe_Name):
            print(f"▶️ Reprise du pipeline : {pipe_Name}")
            gstd_client.pipeline_play(pipe_Name)

        elif command == "stop" and checkCommandOnPipeline(pipe_Name):
            print(f"🛑 Arrêt du pipeline : {pipe_Name}")
            state = "suppression"
            message = {"state": state, "pipeline_name": pipe_Name}

            json_message = json.dumps(message)
            client.publish(MQTT_LOG_SERVER, json_message)
            # Envoi du signal EOS avant l'arrêt
            try:
                gstd_client.event_eos(pipe_Name)
                print(f"📩 EOS envoyé au pipeline {pipe_Name}")
            except (GstcError, GstdError) as e:
                print(f"❌ Erreur lors de l'envoi de EOS : {e}")

            # Attendre un peu pour laisser le pipeline finaliser l'écriture
            time.sleep(5)
            gstd_client.pipeline_stop(pipe_Name)
            gstd_client.pipeline_delete(pipe_Name)
            state = "deleted"
            message = {"state": state, "pipeline_name": pipe_Name}
            json_message = json.dumps(message)
            client.publish(MQTT_LOG_SERVER, json_message)
            print(f"🛑 Arrêt du pipeline : {pipe_Name} terminé")
        
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
    print("\n🔴 Arrêt du programme et fermeture propre des pipelines existantes dans Gstd")

    pipelines = gstd_client.list_pipelines()  # Liste des pipelines
    for pipeline in pipelines:
        pipe_name = pipeline['name']  # Ou pipeline.name, selon la structure de votre pipeline
        # Lire l'état du pipeline en utilisant la méthode read
        state = gstd_client.read(f'pipelines/{pipe_name}/state')['value']
        print(f"Pipeline: {pipe_name} - State: {state}")

        # Envoi du signal EOS avant l'arrêt
        try:
            gstd_client.event_eos(pipe_name)
            print(f"📩 EOS envoyé au pipeline {pipe_name}")
        except (GstcError, GstdError) as e:
            print(f"❌ Erreur lors de l'envoi de EOS : {e}")

        # Attendre un peu pour laisser le pipeline finaliser l'écriture
        time.sleep(1)  # Pause de 1 secondes (ajuster si nécessaire)
        print(f"🛑 Arrêt du pipeline : {pipe_name} terminé")
        # Stopper et supprimer le pipeline
        gstd_client.pipeline_stop(pipe_name)
        gstd_client.pipeline_delete(pipe_name)

    print("\n🔴 Arrêt du programme terminé")