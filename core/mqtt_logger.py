import os
import json
import logging
import logging.handlers
import paho.mqtt.client as mqtt

LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "mqtt.log")
MAX_BYTES = 1 * 1024 * 1024  # 1 Mo
BACKUP_COUNT = 3

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("mqtt_logger")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(handler)

# Aussi afficher dans stdout (supervisord le capture)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(console)


def on_connect(client, userdata, flags, rc):
    print("MQTT Logger connecte au broker")
    client.subscribe("#")
    logger.info("[LOGGER] Connecte au broker MQTT — ecoute tous les topics")


def on_message(client, userdata, msg):
    try:
        payload_raw = msg.payload.decode("utf-8", errors="replace")
        try:
            parsed = json.loads(payload_raw)
            payload_str = json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            payload_str = payload_raw
        logger.info("[%s] %s", msg.topic, payload_str)
    except Exception as e:
        logger.error("[LOGGER] Erreur: %s", e)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="echo-mqtt-logger")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
