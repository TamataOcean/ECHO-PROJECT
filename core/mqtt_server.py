import paho.mqtt.client as mqtt
import subprocess

BROKER = "localhost"  # Change si ton broker est sur un autre PC
PORT = 1883
TOPIC_CMD = "python/control"
TOPIC_RESP = "python/response"

process = None  # Pour stocker le processus du script

def on_message(client, userdata, msg):
    global process
    command = msg.payload.decode()
    print(f"Commande reçue: {command}")

    if command == "start" and process is None:
        #process = subprocess.Popen(["python", "record_multi_camera.py"])
        process = subprocess.Popen(["python", "record_Video.py"])
        client.publish(TOPIC_RESP, "Script started")
    
    elif command == "stop" and process:
        process.terminate()
        process = None
        client.publish(TOPIC_RESP, "Script stopped")

    elif command == "status":
        status = "running" if process else "stopped"
        client.publish(TOPIC_RESP, f"Statut: {status}")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC_CMD)
client.loop_forever()
