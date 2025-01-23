# Enregistrement vidéo dans un fichier .mp4 passé en paramètre 
# exemple > python record_Video.py output_video.mp4 

import subprocess
import sys # Keep console arguments
from pypylon import pylon

# Paramètres vidéo
output_file = sys.argv[1]
fps = 25  # Fréquence d'acquisition
width = 1278
height = 1024
codec = "libx264"

# Commande FFmpeg
ffmpeg_command = [
    "ffmpeg",
    "-y",
    "-f", "rawvideo",
    "-pixel_format", "bayer_bggr8",
    "-video_size", f"{width}x{height}",
    "-framerate", str(fps),
    "-i", "-",
    "-c:v", codec,
    "-preset", "ultrafast",
    "-r", str(fps),             # -r to force output framarate 
    #"-vsync cfr",              # Pour éviter toute désynchronisation, on encode avec un framerate constant
    output_file,
]

# Lancement de FFmpeg
ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

# Initialiser la caméra Basler
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

camera.GainAuto.SetValue("Once") # Permet de faire la mise à jour de la balance au lancement du program
# camera.ExposureAuto.SetValue("On") ne marche pas !!!

# pylon.FeaturePersistence.Save("config_record_Video.txt", camera.GetNodeMap())

# Configurer la caméra
camera.Width.SetValue(width)
camera.Height.SetValue(height)
camera.PixelFormat.SetValue("BayerRG8")  # Format compatible avec FFmpeg

# Acquisition et envoi à FFmpeg
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

try:
    print("Appuyez sur 'Ctrl+C' pour arrêter...")
    while camera.IsGrabbing():
        grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grab_result.GrabSucceeded():
            frame = grab_result.Array
            if frame is not None:
                ffmpeg_process.stdin.write(frame.tobytes())
        grab_result.Release()
except KeyboardInterrupt:
    print("Arrêt de l'enregistrement.")
finally:
    # Fermer la caméra et FFmpeg
    camera.StopGrabbing()
    camera.Close()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

print(f"Vidéo enregistrée : {output_file}")
