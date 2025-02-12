# Evolution du process controler pour executé à partir d'un fichier Json en entré

import json
import sys
import time
import os
import paho.mqtt.client as mqtt

# Configuration MQTT
MQTT_BROKER = "localhost"  # Remplace par ton broker MQTT
MQTT_TOPIC = "gstreamer/control"  # Le topic auquel publier

def send_mqtt_command(client, command, pipe_name):
    """ Envoie une commande MQTT """
    message = {"order": command, "pipeline_name": pipe_name}
    json_message = json.dumps(message)
    client.publish(MQTT_TOPIC, json_message)
    print(f"📩 Commande MQTT envoyée : {json_message}")

def process_orders(json_file):
    """ Lit et traite le fichier JSON """
    if not os.path.exists(json_file):
        print(f"❌ Erreur : Fichier {json_file} non trouvé.")
        sys.exit(1)

    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)  # Charger le JSON depuis le fichier

        # Extraction des paramètres principaux
        ID_Serie = data.get('ID_Serie', 'N/A')
        ID_Bassin = data.get('ID_Bassin', 'N/A')
        ID_Arene = data.get('ID_Arene', 'N/A')
        ID_Sequence = data.get('ID_Sequence', 'N/A')
        ID_Camera = data.get('ID_Camera', 'N/A')
        pipeline_name = data.get('pipeline_name', 'default_pipeline')
        location = data.get('location', 'N/A')

        print(f"📌 Bassin: {ID_Bassin}, Arène: {ID_Arene}, Caméra: {ID_Camera}")

        client = mqtt.Client()
        client.connect(MQTT_BROKER, 1883, 60)
        message = {
                    "order": "create_pipeline",
                    "ID_Serie": ID_Serie,
                    "ID_Bassin": ID_Bassin,
                    "ID_Arene": ID_Arene,
                    "ID_Sequence": ID_Sequence,
                    "ID_Camera": ID_Camera,
                    "location": location,
                    "video_file_name": pipeline_name,
                    "pipeline_name": pipeline_name
                }
        
        client.publish(MQTT_TOPIC, json.dumps(message))
        print(f"📩 Commande Create_Pipeline envoyée : {message}")
        time.sleep(2)

        for order in data.get("orders", []):
            command = order.get("order")            
            duration = order.get("duration", None) 
            send_mqtt_command(client, command, pipeline_name)

            if duration is not None:
                print(f"⏳ Attente de {duration} secondes avant la prochaine commande...")
                time.sleep(duration)
        
        # Fin de la boucle des ordres, on arrete le pipeline
        message = {"order": "stop", "pipeline_name": pipeline_name }
        client.publish(MQTT_TOPIC, json.dumps(message))
        print(f"📩 Commande MQTT envoyée : {message}")
        print("🛑 Fin de l'enregistrement")
        sys.exit(0)
        client.disconnect()

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pControler-from-JSON.py <fichier_json>")
        sys.exit(1)

    json_file = sys.argv[1]  # Récupérer le fichier JSON en argument
    process_orders(json_file)
