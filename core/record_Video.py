# Enregistrement vidéo dans un fichier .mp4 passé en paramètre 
# exemple > python record_Video.py output_video.mp4 

import subprocess
import sys # Keep console arguments
from pypylon import pylon

# Paramètres vidéo
#output_file = sys.argv[1]
output_file = "Record_Video_MQTT.mp4"
fps = 25  # Fréquence d'acquisition
width = 1024
height = 1024
codec = "libx264"

# Commande FFmpeg
ffmpeg_command_OLD = [
    "ffmpeg",
    "-y",
    "-r", str(fps),  
    "-f", "rawvideo",
    "-pixel_format", "gray",  
    "-video_size", f"{width}x{height}",
    "-framerate", str(fps),  
    "-i", "-",
    "-c:v", "libx264",  
    "-preset", "ultrafast",  
    #"-b:v", "2000k",  
    #"-crf", "23",
    "-pix_fmt", "yuv420p",
    "-vf", "format=yuv420p",  # 🔹 Convertit en YUV pour la compression
    "-vsync", "cfr",
    output_file,
]

ffmpeg_command = [
    "ffmpeg",
    "-y",
    "-f", "rawvideo",
    "-pixel_format", "gray",
    "-video_size", f"{width}x{height}",
    "-framerate", str(fps),  # 🔹 Définit bien l'entrée en 25 FPS
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-vsync", "cfr",
    output_file,
]

# Lancement de FFmpeg
ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

# Initialiser la caméra Basler
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

print(f"FPS réel configuré : {camera.AcquisitionFrameRateAbs.Value}")

# Configurer la caméra
camera.GainAuto.SetValue("Once") # Permet de faire la mise à jour de la balance au lancement du program
camera.Width.SetValue(width)
camera.Height.SetValue(height)
#camera.PixelFormat.SetValue("YUV422_YUYV_Packed") # Format from Basler
camera.PixelFormat.SetValue("BayerRG8")  # Format compatible avec FFmpeg
camera.PixelFormat.Value = "Mono8"
# Set the upper limit of the camera's frame rate to 30 fps
camera.AcquisitionFrameRateEnable.Value = True
camera.AcquisitionFrameRateAbs.Value = fps
camera.ExposureAuto.SetValue("Continuous")
camera.GammaEnable.SetValue(False)
#camera.ExposureTimeAbs.SetValue(2000)

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
