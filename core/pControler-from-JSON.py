# Evolution du process controler pour executé à partir d'un fichier Json en entré
import random
import json
import sys
import time
import os
import paho.mqtt.client as mqtt

# Configuration MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC_CONTROL", "gstreamer/control")

def send_mqtt_command(client, command, pipe_name):
    if not client.is_connected():
        print(f"connection rompue au serveur MQTT pipe : {pipe_name}")
        client.connect(MQTT_BROKER, 1883, 60)

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

        # Vérifier si "conf" est présent
        conf = data.get("conf")
        if conf is None:
            print("❌ Erreur : La section 'conf' est absente du JSON.")
            sys.exit(1)

        # Extraction des paramètres principaux
        ID_Serie = conf.get('ID_Serie', 'N/A')
        ID_Bassin = conf.get('ID_Bassin', 'N/A')
        ID_Arene = conf.get('ID_Arene', 'N/A')
        ID_Sequence = conf.get('ID_Sequence', 'N/A')
        pipeline_name = conf.get('pipeline_name', 'default_pipeline')
        location = conf.get('location', 'N/A')
        video_Path = conf.get('video_Path', 'N/A')
        max_size_time = conf.get('max_size_time', 'N/A')
        max_size_file = conf.get('max_size_file', 'N/A')

        print(f"📌 Bassin: {ID_Bassin}, Arène: {ID_Arene}")

        client = mqtt.Client()
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_start()  # Démarre le loop MQTT en arrière-plan
        message = {
                    "order": "create_pipeline",
                    "ID_Serie": ID_Serie,
                    "ID_Bassin": ID_Bassin,
                    "ID_Arene": ID_Arene,
                    "ID_Sequence": ID_Sequence,
                    "location": location,
                    "video_file_name": pipeline_name,
                    "pipeline_name": pipeline_name,
                    "video_Path" : video_Path,
                    "max_size_time" : int(max_size_time),
                    "max_size_file" : int(max_size_file)
                }
        
        client.publish(MQTT_TOPIC, json.dumps(message))
        print(f"📩 Commande Create_Pipeline envoyée : {message}")
        time.sleep(2)

        for order in data.get("orders", []):
            command = order.get("order")            
            duration = int(order.get("duration", 0)) # par défaut, pas de délai
            send_mqtt_command(client, command, pipeline_name)
            time.sleep(0.5)

            if duration > 0:
                print(f"⏳ Attente de {duration} secondes avant la prochaine commande...")
                time.sleep(duration)
        
        # Fin de la boucle des ordres, on arrete le pipeline
        delay_before_stop = random.uniform(0.5, 10.0)  # Valeur aléatoire entre 0.5 et 2 secondes
        print(f"⏳ {pipeline_name} Attente aléatoire de {delay_before_stop:.2f} secondes avant le stop...")
        time.sleep(delay_before_stop)

        send_mqtt_command(client, "stop", pipeline_name)
        # client.publish(MQTT_TOPIC, json.dumps(message))
        # print(f"📩 Commande MQTT envoyée : {message}")
        time.sleep(1)

        print("🛑 Fin de l'enregistrement")
        client.disconnect()
        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pControler-from-JSON.py <fichier_json>")
        sys.exit(1)

    json_file = sys.argv[1]  # Récupérer le fichier JSON en argument
    process_orders(json_file)
