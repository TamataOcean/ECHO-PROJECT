import json
import sys
import time
import paho.mqtt.client as mqtt

# Configurations MQTT
MQTT_BROKER = "localhost"  # Remplace par ton broker MQTT
MQTT_TOPIC = "gstreamer/control"  # Le topic auquel publier

def send_mqtt_command(client, command, pipeName):
    message = {"order": command}
    message["pipeline_name"] = pipeName
    json_message = json.dumps(message)
    client.publish(MQTT_TOPIC, json_message)
    print(f"📩 Commande MQTT envoyée : {json_message}")

def process_orders(json_data):
    try:
        data = json.loads(json_data)  # Charger le JSON
        ID_Serie = data['ID_Serie']
        ID_Bassin = data['ID_Bassin']
        ID_Arene = data['ID_Arene']
        ID_Sequence = data['ID_Sequence']
        ID_Camera = data['ID_Camera']
        
        pipeline_name = data['pipeline_name']
        location = data['location']

        print(f"Bassin: {data['ID_Bassin']}")
        print(f"Arene: {data['ID_Arene']}")
        print(f"ID de la caméra: {data['ID_Camera']}")

        client = mqtt.Client()
        client.connect(MQTT_BROKER, 1883, 60)
        
        for order in data["orders"]:
            command = order["order"]

            if command == "create_pipeline":
                message = f'{{"order": "create_pipeline","ID_Serie": "{ID_Serie}","ID_Bassin": "{ID_Bassin}","ID_Arene": "{ID_Arene}","ID_Sequence": "{ID_Sequence}","ID_Camera": "{ID_Camera}","location": "{location}","video_file_name": "{pipeline_name}","pipeline_name": "{pipeline_name}"}}'
                print(f"📩 Commande MQTT envoyée : {message}")
                client.publish(MQTT_TOPIC, message)
                time.sleep(2)

            elif command == "stop":
                message = {"order": "stop","pipeline_name":order.get("pipeline_name")}
                client.publish(MQTT_TOPIC, json.dumps(message))
                print(f"📩 Commande MQTT envoyée : {message}")
                print("Fin de l'enregistrement")
                sys.exit(0)

            else: # Ordre start ou pause 
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
    if len(sys.argv) != 3:
        print("Usage: python script.py 'Camera_XXX' 'duration(seconde)")
        sys.exit(1)
    
    pipeName = sys.argv[1]
    pipeDuration = sys.argv[2]

    # Exemple d'utilisation
    json_input = f'{{\n' \
    f'    "ID_Serie": "S1",\n' \
    f'    "ID_Bassin": "B1",\n' \
    f'    "ID_Arene": "A1",\n' \
    f'    "ID_Sequence": "Seq1",\n' \
    f'    "ID_Camera": "Camera_1",\n' \
    f'    "location": "rtsp://admin:JKFLFO@172.24.1.112/11",\n' \
    f'    "video_file_name": "{pipeName}",\n' \
    f'    "pipeline_name": "{pipeName}",\n' \
    f'    "orders": [\n' \
    f'        {{"order": "create_pipeline" }},\n' \
    f'        {{"order": "start", "duration": {pipeDuration}, "pipeline_name": "{pipeName}"}},\n' \
    f'        {{"order": "stop", "pipeline_name": "{pipeName}"}}\n' \
    f'    ]\n' \
    f'}}'

    # DEBUG print(json_input)

    process_orders(json_input)


process_orders(json_input)

# Exemple du JSON que l'on pourra recevoir de Node-Red
# {
#     "ID_Serie": "S1",
#     "ID_Bassin": "B1",
#     "ID_Arene": "A1",
#     "ID_Sequence": "Seq1",
#     "ID_Camera": "Camera_1",
#     "location": "rtsp://admin:JKFLFO@172.24.1.112/11",
#     "video_file_name": "Camera_TEST1",
#     "pipeline_name": "Camera_TEST1",
#     "orders": [
#         {"order": "create_pipeline" },
#         {"order": "start", "duration": 20, "pipeline_name": "Camera_TEST1"},
#         {"order": "stop", "pipeline_name": "Camera_TEST1"}
#     ]
# }
