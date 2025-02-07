import paho.mqtt.client as mqtt
import subprocess
import signal
import time

# Configuration MQTT
MQTT_BROKER = "localhost"
MQTT_TOPIC = "video/control"

# Commande GStreamer
# gst-launch-1.0 -e -q rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=1000 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000

GST_PIPELINE = [
    "gst-launch-1.0", "-e", "-q",
    "rtspsrc", "location=rtsp://admin:JKFLFO@172.24.1.112/11", "latency=1000",
    #"!", "watchdog", 
    #"timeout=500",
    "!", "queue",
    "!", "rtph264depay",
    "!", "h264parse",
    "!", "queue",
    "!", "h264parse",
    "!", "splitmuxsink", "location=video%02d.mov",
    "max-size-time=10000000000", "max-size-bytes=1000000"
]

# Variable globale pour le processus GStreamer
gst_process = None

# Callback : Connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    print("📡 Connecté au broker MQTT")
    client.subscribe(MQTT_TOPIC)

# Callback : Réception d'un message MQTT
def on_message(client, userdata, msg):
    global gst_process

    command = msg.payload.decode()
    print(f"📩 Commande MQTT reçue : {command}")

    if command == "start":
        if gst_process is None:
            print("▶️ Démarrage du pipeline GStreamer...")
            gst_process = subprocess.Popen(GST_PIPELINE)
        else:
            print("⚠️ Le pipeline est déjà en cours d'exécution.")

    elif command == "pause":
        if gst_process:
            print("⏸️ Mise en pause du pipeline...")
            gst_process.send_signal(signal.SIGSTOP)  # Pause
        else:
            print("⚠️ Aucun pipeline en cours d'exécution.")

    elif command == "resume":
        if gst_process:
            print("▶️ Reprise du pipeline...")
            gst_process.send_signal(signal.SIGCONT)  # Reprise
        else:
            print("⚠️ Aucun pipeline en pause.")

    elif command == "stop":
        if gst_process:
            print("🛑 Arrêt du pipeline GStreamer...")
            gst_process.terminate()  # Arrêt propre
            gst_process.wait()
            gst_process = None
        else:
            print("⚠️ Aucun pipeline à arrêter.")

# Configuration et démarrage du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

# Boucle principale (Garde le programme en vie)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🔴 Arrêt du programme.")
    client.loop_stop()
    client.disconnect()
