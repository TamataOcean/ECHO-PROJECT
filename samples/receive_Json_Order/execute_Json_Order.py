import json

# Exemple d'utilisation
json_input = '''{
    "Bassin": "Bassin_1",
    "Nasse": "Nasse_1",
    "camera_ID": 12345,
    "orders": [
        {"order": "start"},
        {"order": "play", "duration": 10},
        {"order": "pause", "duration": 30},
        {"order": "play", "duration": 5},
        {"order": "stop"}
    ]
}'''


def process_orders(json_data):
    try:
        data = json.loads(json_data)  # Charger le JSON
        print(f"Bassin: {data['Bassin']}")
        print(f"Nasse: {data['Nasse']}")
        print(f"ID de la caméra: {data['camera_ID']}")
        
        for order in data["orders"]:
            command = order["order"]
            duration = order.get("duration", None)  # Certains ordres n'ont pas de durée
            
            if duration is not None:
                print(f"Commande: {command}, Durée: {duration} secondes")
            else:
                print(f"Commande: {command}")

    except json.JSONDecodeError as e:
        print(f"Erreur lors du parsing du JSON: {e}")

process_orders(json_input)
