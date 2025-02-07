import subprocess
import paho.mqtt.client as mqtt
import time
from pypylon import pylon
import os

# Paramètres
MQTT_BROKER = "localhost"
MQTT_TOPIC = "video2/control"
TOPIC_RESP = "video2/response"

output_prefix = "Record_Video2_MQTT"
fps = 25
width = 1024
height = 1024

# Variables de contrôle
recording = False
ffmpeg_process = None
segment_index = 0

# Initialisation caméra
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

# Fonction pour démarrer FFmpeg
def start_recording():
    global ffmpeg_process, recording, segment_index
    if not recording:
        print("🎥 Reprise de l'enregistrement...")
        segment_file = f"{output_prefix}_{segment_index:03d}.mp4"
        #segment_file = f"{output_prefix}_%03d.mp4"

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-pixel_format", "gray",
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
        client.publish(TOPIC_RESP, "Record started")


# Fonction pour arrêter FFmpeg (pause)
def pause_recording():
    global ffmpeg_process, recording, segment_index
    if recording and ffmpeg_process:
        print("⏸️ Pause de l'enregistrement reçu...")
        recording = False
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        segment_index += 1  # Incrémente l'index pour la prochaine reprise
        client.publish(TOPIC_RESP, "Record paused")


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
        client.publish(TOPIC_RESP, "Record stopped")


def clean_Temporary_Files(final_video):
    print(f"Clean temporary files sauf : {final_video}")
    # Récupérer la liste des fichiers .mp4 dans le répertoire courant
    files = [f for f in os.listdir() if f.endswith(".mp4")]

    # Supprimer tous les fichiers .mp4 sauf le fichier final
    for file in files:
        print(file)
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
    
    # Suppression des fichiers temporaires
    clean_Temporary_Files(file_final)
    os.remove(file_list)

# Configuration MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER)
client.subscribe(MQTT_TOPIC)
client.loop_start()

print("📡 En attente de commandes MQTT...")

# Boucle principale pour capturer les images
try:
    while True:
        if recording and camera.IsGrabbing():
            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                frame = grab_result.Array
                if frame is not None and recording:#ffmpeg_process:
                    try:
                        ffmpeg_process.stdin.write(frame.tobytes())
                    except BrokenPipeError:
                        print("⚠️ FFmpeg a été arrêté brutalement.")
                        recording = False
            grab_result.Release()
        time.sleep(0.04)  # 🔹 1/25s pour 25 FPS
except KeyboardInterrupt:
    #stop_recording()
    #concatenate_videos()
    print("🔚 Programme terminé.")
