import threading
import subprocess
from pypylon import pylon
import numpy as np

# Paramètres vidéo
fps = 25  # Fréquence d'acquisition
width = 1024
height = 1024
codec = "libx264"

# Fonction de capture vidéo d'une caméra
def capture_video_from_camera(camera_id, output_file):
    # Créer l'instance de la caméra à partir de l'ID de série
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    
    camera = None
    for device in devices:
        if device.GetSerialNumber() == camera_id:
            # Correct: Utilisez CreateDevice pour obtenir l'appareil
            camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(device))
            break
    
    if camera is None:
        print(f"Aucune caméra trouvée avec l'ID {camera_id}")
        return
    
    # Lancement de FFmpeg
    ffmpeg_command = [
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
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-vf", "format=yuv420p",  # 🔹 Convertit en YUV pour la compression
    "-vsync", "cfr",
    output_file,
]

    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

    # Initialisation de la caméra
    camera.Open()
    camera.Width.SetValue(width)
    camera.Height.SetValue(height)
    camera.PixelFormat.SetValue("Mono8")
    camera.AcquisitionFrameRateEnable.Value = True
    camera.AcquisitionFrameRateAbs.Value = fps
    camera.ExposureAuto.SetValue("Continuous")
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    
    print(f"Caméra {camera_id} démarrée, capture en cours...")

    try:
        while camera.IsGrabbing():
            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                frame = grab_result.Array
                if frame is not None and frame.size > 0:
                    ffmpeg_process.stdin.write(frame.tobytes())
            grab_result.Release()
    except KeyboardInterrupt:
        print(f"Arrêt de la capture pour la caméra {camera_id}.")
        
    finally:
        camera.StopGrabbing()
        camera.Close()
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        print(f"Vidéo enregistrée pour la caméra {camera_id} dans {output_file}.")

# Fonction principale pour gérer plusieurs caméras
def record_multiple_cameras(camera_ids, output_files):
    threads = []
    
    # Lancer une capture vidéo pour chaque caméra dans un thread séparé
    for i in range(len(camera_ids)):
        thread = threading.Thread(target=capture_video_from_camera, args=(camera_ids[i], output_files[i]))
        threads.append(thread)
        thread.start()

    # Attendre que toutes les captures vidéo soient terminées
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Liste des IDs des caméras et des fichiers de sortie correspondants
    camera_ids = ["23582133"]  # Remplacez par les numéros de série de vos caméras
    output_files = ["camera_1_output.mp4"]

    # Lancer l'enregistrement en parallèle pour toutes les caméras
    record_multiple_cameras(camera_ids, output_files)
