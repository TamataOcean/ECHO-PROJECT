# Export des parametres de la caméra
# Exemple > python export_camera_config.py config_camera1.txt

import sys # Keep console arguments
from pypylon import pylon

output_file = sys.argv[1]

# Initialiser la caméra Basler
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

camera.GainAuto.SetValue("Once") # Permet de faire la mise à jour de la balance au lancement du program

pylon.FeaturePersistence.Save(output_file, camera.GetNodeMap())
print(f"export de la config camera terminé : {output_file} ")
