from pypylon import pylon

# Fonction pour lister les caméras connectées et afficher leurs numéros de série
def list_camera_ids():
    # Créer une instance de la caméra en utilisant le framework Pylon
    tl_factory = pylon.TlFactory.GetInstance()
    
    # Lister toutes les caméras disponibles
    cameras = tl_factory.EnumerateDevices()

    if len(cameras) == 0:
        print("Aucune caméra Basler trouvée.")
        return

    print(f"Nombre de caméras Basler détectées : {len(cameras)}")
    for i, camera in enumerate(cameras):
        print(f"Caméra {i+1}:")
        print(f"  Modèle : {camera.GetModelName()}")
        print(f"  Numéro de série (ID) : {camera.GetSerialNumber()}")
        print(f"  Adresse IP : {camera.GetIpAddress()}")
        print("")

if __name__ == "__main__":
    list_camera_ids()
