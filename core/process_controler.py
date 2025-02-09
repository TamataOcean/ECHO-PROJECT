import json
import sys
import time
import paho.mqtt.client as mqtt

# Configurations MQTT
MQTT_BROKER = "localhost"  # Remplace par ton broker MQTT
MQTT_TOPIC = "gstreamer/control"  # Le topic auquel publier

def send_mqtt_command(client, command, camera_ID):
    message = {"order": command}
    message["camera_ID"] = camera_ID
    
    json_message = json.dumps(message)
    client.publish(MQTT_TOPIC, json_message)
    print(f"📩 Commande MQTT envoyée : {json_message}")

def process_orders(json_data):
    try:
        data = json.loads(json_data)  # Charger le JSON
        print(f"Bassin: {data['Bassin']}")
        print(f"Nasse: {data['Nasse']}")
        print(f"ID de la caméra: {data['camera_ID']}")
        camera_ID = data.get("camera_ID")

        client = mqtt.Client()
        client.connect(MQTT_BROKER, 1883, 60)
        
        for order in data["orders"]:
            command = order["order"]
            duration = order.get("duration", None)  # Certains ordres ont une durée
            
            send_mqtt_command(client, command, camera_ID)
            
            if duration is not None:
                print(f"⏳ Attente de {duration} secondes avant la prochaine commande...")
                time.sleep(duration)
        
        client.disconnect()
    except json.JSONDecodeError as e:
        print(f"Erreur lors du parsing du JSON: {e}")

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python script.py '<json_string>'")
#         sys.exit(1)
    
#     json_input = sys.argv[1]
#     process_orders(json_input)

# Exemple d'utilisation
json_input = '''{
    "Bassin": "Bassin_1",
    "Nasse": "Nasse_1",
    "camera_ID": 12345,
    "orders": [
        {"order": "start","duration": 30},
        {"order": "pause", "duration": 20},
        {"order": "start", "duration": 120},
        {"order": "pause", "duration": 30},
        {"order": "start", "duration": 60},
        {"order": "stop"}
    ]
}'''

process_orders(json_input)