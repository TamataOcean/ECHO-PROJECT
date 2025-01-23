# Streaming programme with Ffmpeg
# NE MARCHE PAS !!! PAS ENCORE ;) !

import subprocess
import sys # Keep console arguments
from pypylon import pylon

# Paramètres vidéo
# output_file = "output_video.mp4"
#output_file = sys.argv[1]
fps = 25  # Fréquence d'acquisition
width = 1278
height = 1024
codec = "libx264"

# Commande FFmpeg
ffmpeg_cmd = [
    "ffmpeg",
    "-y",
    "-f", "rawvideo",
    "-pixel_format", "bayer_bggr8",
    "-video_size", f"{width}x{height}",
    "-framerate", str(fps),
    "-i", "-",
    "-c:v", codec,
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    # "-pix_fmt", "yuv420p",  # Format de pixel compatible avec H.264
    "-r", str(fps),
    "-f", "rtsp",
    "-rtsp_flags", "listen",
    "rtsp://localhost:8554/live"
]

# Lancement de FFmpeg
ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

# Initialiser la caméra Basler
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

camera.GainAuto.SetValue("Once") 
#camera.PixelFormat.SetValue("Mono8")  # Format compatible pour les vidéos en noir et blanc

# Configurer la caméra
camera.Width.SetValue(width)
camera.Height.SetValue(height)
camera.PixelFormat.SetValue("BayerRG8")  # Format compatible avec FFmpeg

# Acquisition et envoi à FFmpeg
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

try:
    print("Appuyez sur 'Ctrl+C' pour arrêter le streaming...")
    while camera.IsGrabbing():
        grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grab_result.GrabSucceeded():
            frame = grab_result.Array
            if frame is not None:
                ffmpeg_process.stdin.write(frame.tobytes())
        grab_result.Release()
except KeyboardInterrupt:
    print("Arrêt du streaming.")
finally:
    # Fermer la caméra et FFmpeg
    camera.StopGrabbing()
    camera.Close()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

print(f"Fin du programme")


