# V1.0 Programme permettant à partir d'un flux RTSP d'enregistrer des vidéos à la demande 
# en fonction des commandes MQTT reçue.
from pygstc.gstc import *
from pygstc.logger import *
import paho.mqtt.client as mqtt

# Configurations MQTT
MQTT_BROKER = "localhost"  # Remplace par ton broker MQTT
MQTT_TOPIC = "gstreamer/control"  # Le topic auquel tu t'abonnes

# Création du pipeline dans gstd
#pipeline_str = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=100 ! watchdog timeout=200 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"

pipiline_name_record = "RECORD_VideoSalon"
pipiline_name_display = "DISPLAY_VideoSalon"
export_directory_file = "/home/bibi/code/ECHO-PROJECT/TEST_VIDEOS/"

#pipeline_str = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"
pipeline_display = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! fpsdisplaysink sync=false"
pipeline_record = f"rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location={export_directory_file}video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"

### COMMANDE VALIDE via terminal !!!
####################################
# AFFICHAGE
# time gst-launch-1.0 -q rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! textoverlay text="$(date)" valignment=top halignment=left font-desc="Sans, 24" ! fpsdisplaysink sync=false
# ENREGISTREMENT DANS UN FICHER SEGMENTE
# time gst-launch-1.0 -e -q rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=/home/bibi/code/ECHO-PROJECT/TEST_VIDEOS/video%02d.mov max-size-time=10000000000 max-size-bytes=1000000

#Pipeline de T  EST pour afficher une vidéo "mire"
#pipiline_name_record = "test"
#pipeline_str = 'videotestsrc ! videoconvert ! autovideosink'

# Création du client gstd
gstd_logger = CustomLogger('pygstc_example', loglevel='DEBUG')
gstd_client = GstdClient(logger=gstd_logger)

# Création du pipeline Display
gstd_client.pipeline_create(pipiline_name_display, pipeline_display)
print(f"✅ Pipeline {pipiline_name_record} créé avec succès")
pipelines = gstd_client.read("pipelines")
print(f"📜 Liste des pipelines actifs : {pipelines}")

# Création du pipeline Record
gstd_client.pipeline_create(pipiline_name_record, pipeline_record)
print(f"✅ Pipeline {pipiline_name_record} créé avec succès")
pipelines = gstd_client.read("pipelines")
print(f"📜 Liste des pipelines actifs : {pipelines}")

# Callback : Connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    print("📡 Connecté au broker MQTT")
    client.subscribe(MQTT_TOPIC)

# Callback : Réception d'un message MQTT
def on_message(client, userdata, msg):
    command = msg.payload.decode()
    print(f"📩 Commande MQTT reçue : {command}")

    if command == "start":
        print("▶️ Démarrage du pipeline...")
        gstd_client.pipeline_play(pipiline_name_record)
        # Vérifier l'état du pipeline
        state = gstd_client.read(f'pipelines/{pipiline_name_record}/state')
        print(f"🚦 État du pipeline après start : {state}")

    elif command == "pause":
        print("⏸️ Pause du pipeline...")
        gstd_client.pipeline_pause(pipiline_name_record)

    elif command == "resume":
        print("▶️ Reprise du pipeline...")
        gstd_client.pipeline_play(pipiline_name_record)

    elif command == "stop":
        print("🛑 Arrêt du pipeline...")
        gstd_client.pipeline_stop(pipiline_name_record)

    elif command == "status_record":
        print(gstd_client.read(f'pipelines/{pipiline_name_record}/state')['value'])

    elif command == "status_display":
        state = gstd_client.read(f'pipelines/{pipiline_name_display}/state')
        print(f"🚦 État du pipeline display : {state}")

    elif command == "start_display":
        gstd_client.pipeline_play(pipiline_name_display)

    elif command == "pause_display":
        gstd_client.pipeline_pause(pipiline_name_display)

    elif command == "stop_display":
        gstd_client.pipeline_stop(pipiline_name_display)


# Connexion MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)

try:
    # Boucle infinie pour recevoir les messages MQTT
    client.loop_forever()

except KeyboardInterrupt:
    print("\n🔴 Arrêt du programme.")
    gstd_client.pipeline_stop(pipiline_name_record)
    gstd_client.pipeline_delete(pipiline_name_record)
    gstd_client.pipeline_stop(pipiline_name_display)
    gstd_client.pipeline_delete(pipiline_name_display)