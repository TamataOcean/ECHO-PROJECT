import json
import sys
import time
import paho.mqtt.client as mqtt

# Configurations MQTT
MQTT_BROKER = "localhost"  # Remplace par ton broker MQTT
MQTT_TOPIC = "gstreamer/control"  # Le topic auquel publier

def send_mqtt_command(client, command, pipeName):
    message = {"order": command}
    message["camera_ID"] = "camera_ID"
    message["pipeline_name"] = pipeName
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

            if command == "create_pipeline":
                message = {"order": "create_pipeline","pipeline_name":order.get("pipeline_name"), "location":order.get("location")}
                client.publish(MQTT_TOPIC, json.dumps(message))
                print(f"📩 Commande MQTT envoyée : {message}")
                time.sleep(2)
            elif command == "stop":
                message = {"order": "stop","pipeline_name":order.get("pipeline_name")}
                client.publish(MQTT_TOPIC, json.dumps(message))
                print(f"📩 Commande MQTT envoyée : {message}")
                print("Fin de l'enregistrement")
                sys.exit(0)
            else:
                duration = order.get("duration", None)  # Certains ordres ont une durée
                pipeName = order.get("pipeline_name")
                send_mqtt_command(client, command, pipeName)
                
                if duration is not None:
                    print(f"⏳ Attente de {duration} secondes avant la prochaine commande...")
                    time.sleep(duration)
            
        client.disconnect()
    except json.JSONDecodeError as e:
        print(f"Erreur lors du parsing du JSON: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py 'Camera_XXX'")
        sys.exit(1)
    
    exec_param = sys.argv[1]

    # Exemple d'utilisation
    json_input = f'{{\n' \
    f'    "Bassin": "Bassin_1",\n' \
    f'    "Nasse": "Nasse_1",\n' \
    f'    "camera_ID": "Camera_12345",\n' \
    f'    "orders": [\n' \
    f'        {{"order": "create_pipeline", "pipeline_name": "{exec_param}", "location": "rtsp://admin:JKFLFO@172.24.1.112/11"}},\n' \
    f'        {{"order": "start", "duration": 20, "pipeline_name": "{exec_param}"}},\n' \
    f'        {{"order": "pause", "duration": 10, "pipeline_name": "{exec_param}"}},\n' \
    f'        {{"order": "start", "duration": 10, "pipeline_name": "{exec_param}"}},\n' \
    f'        {{"order": "pause", "duration": 20, "pipeline_name": "{exec_param}"}},\n' \
    f'        {{"order": "start", "duration": 30, "pipeline_name": "{exec_param}"}},\n' \
    f'        {{"order": "stop", "pipeline_name": "{exec_param}"}}\n' \
    f'    ]\n' \
    f'}}'


    process_orders(json_input)


process_orders(json_input)