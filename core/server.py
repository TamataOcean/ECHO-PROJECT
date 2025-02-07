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

pipeline_name = "VideoSalon"
#pipeline_str = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"
pipeline_str = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! watchdog timeout=200 ! queue ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! fpsdisplaysink sync=false"
pipeline_record = "rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000"

### COMMANDE VALIDE via terminal !!!
####################################
# AFFICHAGE
# time gst-launch-1.0 -q rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=100 ! watchdog timeout=200 ! queue ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! textoverlay text="$(date)" valignment=top halignment=left font-desc="Sans, 24" ! fpsdisplaysink sync=false
# ENREGISTREMENT DANS UN FICHER SEGMENTE
# time gst-launch-1.0 -e -q rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=100 ! watchdog timeout=200 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000

#Pipeline de TEST pour afficher une vidéo "mire"
#pipeline_name = "test"
#pipeline_str = 'videotestsrc ! videoconvert ! autovideosink'

# Création du client gstd
gstd_logger = CustomLogger('pygstc_example', loglevel='DEBUG')
gstd_client = GstdClient(logger=gstd_logger)

# Créer un pipeline
gstd_client.pipeline_create(pipeline_name, pipeline_record)
print(f"✅ Pipeline {pipeline_name} créé avec succès")

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
        gstd_client.pipeline_play(pipeline_name)

    elif command == "pause":
        print("⏸️ Pause du pipeline...")
        gstd_client.pipeline_pause(pipeline_name)

    elif command == "resume":
        print("▶️ Reprise du pipeline...")
        gstd_client.pipeline_play(pipeline_name)

    elif command == "stop":
        print("🛑 Arrêt du pipeline...")
        gstd_client.pipeline_stop(pipeline_name)

    elif command == "status":
        print(gstd_client.read(f'pipelines/{pipeline_name}/state')['value'])


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
    gstd_client.pipeline_stop(pipeline_name)
    gstd_client.pipeline_delete(pipeline_name)