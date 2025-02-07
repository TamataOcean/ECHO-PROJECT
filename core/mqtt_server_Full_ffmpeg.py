import subprocess
import paho.mqtt.client as mqtt
import os

# Paramètres
MQTT_BROKER = "localhost"
MQTT_TOPIC = "video/control"
TOPIC_RESP = "video/response"

output_prefix = "Record_Video_MQTT"
rtsp_url = "rtsp://admin:JKFLFO@172.24.1.112/11"

# THE COMMAND avec GStreamer
# gst-launch-1.0 -e -q rtspsrc location=rtsp://admin:JKFLFO@172.24.1.112/11 latency=100 ! watchdog timeout=200 ! queue ! rtph264depay ! h264parse ! queue ! h264parse ! splitmuxsink location=video%02d.mov max-size-time=10000000000 max-size-bytes=1000000
# Variables de contrôle
recording = False
ffmpeg_process = None
segment_index = 0
fps = 25
width = 1024
height = 1024

# Fonction pour démarrer FFmpeg directement depuis RTSP
def start_recording():
    global ffmpeg_process, recording, segment_index
    if not recording:
        print("🎥 Démarrage de l'enregistrement...")
        segment_file = f"{output_prefix}_{segment_index:03d}.mp4"
        
        ffmpeg_command_OLD = [
            "ffmpeg",
            "-y",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-use_wallclock_as_timestamps", "1",
            "-fflags", "+genpts",
            "-c:a", "aac", "-b:a", "128k",
            #"-c:v", "copy",  # Copie vidéo brute
            "-c:v", "libx264", "-preset", "ultrafast",
            #"-c:a", "aac",  # Réencodage audio (nécessaire pour MP4 parfois)
            "-movflags", "frag_keyframe+empty_moov",  # Écrit l’atome moov dès le début
            #"-loglevel", "debug",
            segment_file,
        ]

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-f", "rawvideo",
            #"-pixel_format", "gray",
            #"-video_size", f"{width}x{height}",
            #"-framerate", str(fps),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-vsync", "cfr",
            segment_file,
        ]

        # Lancement de FFmpeg avec capture des erreurs
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
        #ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        recording = True
        #stdout, stderr = ffmpeg_process.communicate()
        #print(stderr)

        print(f"✅ FFmpeg lancé, enregistrement dans {segment_file}")
        client.publish(TOPIC_RESP, "Record started")
# Fonction pour arrêter l'enregistrement (pause)
def pause_recording():
    global ffmpeg_process, recording, segment_index
    if recording and ffmpeg_process:
        print("⏸️ Pause de l'enregistrement...")
        recording = False
        ffmpeg_process.terminate()
        ffmpeg_process.wait()
        ffmpeg_process = None
        segment_index += 1
        client.publish(TOPIC_RESP, "Record paused")

# Fonction pour arrêter complètement l'enregistrement
def stop_recording():
    global ffmpeg_process, recording
    if recording and ffmpeg_process:
        print("🛑 Arrêt de l'enregistrement...")
        recording = False
        ffmpeg_process.terminate()
        ffmpeg_process.wait()
        ffmpeg_process = None
        concatenate_videos()
    client.publish(TOPIC_RESP, "Record stopped")

# Fonction pour fusionner les vidéos
def concatenate_videos():
    print("🔗 Fusion des fichiers vidéo...")
    file_list = "concat_list.txt"

    files = sorted(f for f in os.listdir() if f.startswith(output_prefix) and f.endswith(".mp4"))

    if files:
        with open(file_list, "w") as f:
            for file in files:
                f.write(f"file '{file}'\n")

        final_output = f"{output_prefix}_final.mp4"
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", file_list, "-c", "copy", final_output])

        print(f"✅ Vidéo finale générée : {final_output}")
        clean_Temporary_Files(final_output)
        os.remove(file_list)

    client.publish(TOPIC_RESP, "Records merged")

# Fonction pour supprimer les fichiers temporaires
def clean_Temporary_Files(final_video):
    print(f"🧹 Nettoyage des fichiers temporaires sauf {final_video}...")
    for file in os.listdir():
        if file.startswith(output_prefix) and file.endswith(".mp4") and file != final_video:
            os.remove(file)
            print(f"🗑️ Supprimé : {file}")

# Gestion MQTT
def on_message(client, userdata, message):
    command = message.payload.decode("utf-8")
    print(f"📩 Commande MQTT reçue: {command}")

    if command == "start":
        start_recording()
    elif command == "pause":
        pause_recording()
    elif command == "stop":
        stop_recording()

# Initialisation MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER)
client.subscribe(MQTT_TOPIC)
client.loop_start()

print("📡 En attente de commandes MQTT...")

# Boucle infinie pour garder le script actif
try:
    while True:
        pass
except KeyboardInterrupt:
    print("🔚 Programme arrêté.")
    stop_recording()
