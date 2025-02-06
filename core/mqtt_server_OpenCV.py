import subprocess
import paho.mqtt.client as mqtt
import time
import cv2
import os

# Paramètres
MQTT_BROKER = "localhost"
MQTT_TOPIC = "video/control"
output_prefix = "Record_Video_MQTT"
fps = 25
width = 1024
height = 1024
rtsp_url = "rtsp://username:password@ip_address:port/stream"  # URL de votre flux RTSP

# Variables de contrôle
recording = False
ffmpeg_process = None
segment_index = 0

# Fonction pour démarrer FFmpeg
def start_recording():
    global ffmpeg_process, recording, segment_index
    if not recording:
        print("🎥 Reprise de l'enregistrement...")
        segment_file = f"{output_prefix}_{segment_index:03d}.mp4"
        
        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-pixel_format", "bgr24",  # OpenCV capture les images en BGR
            "-video_size", f"{width}x{height}",
            "-framerate", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-vsync", "cfr",
            segment_file,
        ]
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
        recording = True

# Fonction pour arrêter FFmpeg (pause)
def pause_recording():
    global ffmpeg_process, recording, segment_index
    if recording and ffmpeg_process:
        print("⏸️ Pause de l'enregistrement reçu...")
        recording = False
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        segment_index += 1  # Incrémente l'index pour la prochaine reprise

# Fonction pour arrêter FFmpeg (pause)
def stop_recording():
    global ffmpeg_process, recording, segment_index
    if recording and ffmpeg_process:
        print("⏸️ Stop de l'enregistrement reçu...")
        recording = False
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        ffmpeg_process = None

# MQTT - Gestion des messages reçus
def on_message(client, userdata, message):
    command = message.payload.decode("utf-8")
    print(f"📩 Commande MQTT reçue: {command}")

    if command == "start":
        start_recording()
    elif command == "pause":
        pause_recording()
    elif command == "stop":
        stop_recording()
        concatenate_videos()

def clean_Temporary_Files(final_video):
    print(f"Clean temporary files sauf : {final_video}")
    files = [f for f in os.listdir() if f.endswith(".mp4")]

    for file in files:
        if file != final_video:
            try:
                os.remove(file)
                print(f"🗑️ Fichier supprimé : {file}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file}: {e}")

    print("✅ Nettoyage terminé, seul le fichier final est conservé.")

# Fonction pour fusionner les fichiers après l'arrêt
def concatenate_videos():
    print("🔗 Fusion des fichiers vidéo...")
    file_list = "concat_list.txt"

    # Récupérer la liste des fichiers .mp4 dans le répertoire courant
    files = [f for f in os.listdir() if f.endswith(".mp4")]

    if files:
        with open(file_list, "w") as f:
            for file in files:
                f.write(f"file '{file}'\n")
        print("✅ Fichier 'file_list.txt' généré avec succès !")
    else:
        print("⚠️ Aucun fichier .mp4 trouvé.")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", file_list, "-c", "copy", f"{output_prefix}_final.mp4"
    ])
    file_final = f"{output_prefix}_final.mp4"
    print(f"✅ Vidéo finale générée : {file_final}")
    
    clean_Temporary_Files(file_final)
    os.remove(file_list)

# Configuration MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER)
client.subscribe(MQTT_TOPIC)
client.loop_start()

print("📡 En attente de commandes MQTT...")

# Ouvrir le flux RTSP avec OpenCV
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ Impossible d'ouvrir le flux RTSP")
    exit()

# Boucle principale pour capturer les images
try:
    while True:
        if recording:
            ret, frame = cap.read()
            if ret:
                frame_resized = cv2.resize(frame, (width, height))  # Redimensionner l'image si nécessaire
                try:
                    ffmpeg_process.stdin.write(frame_resized.tobytes())
                except BrokenPipeError:
                    print("⚠️ FFmpeg a été arrêté brutalement.")
                    recording = False
        time.sleep(1 / fps)  # 1/25s pour 25 FPS
except KeyboardInterrupt:
    print("🔚 Programme terminé.")
finally:
    cap.release()
    if ffmpeg_process:
        stop_recording()
