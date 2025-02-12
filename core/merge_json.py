# Programme lancer par le bouton Merged JSON dans NodeRed
# Permet de merge 2 JSON ( le config.json et le orders.json )
import json
import os
import sys

def load_json(file_path):
    """ Charge un fichier JSON et retourne son contenu sous forme de dictionnaire. """
    if not os.path.exists(file_path):
        print(f"❌ Erreur : Fichier {file_path} non trouvé.")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON dans {file_path} : {e}")
        return {}

def merge_json(config_file, orders_file, output_file="/home/bibi/code/ECHO-PROJECT/core/merged.json"):
    """ Fusionne les fichiers JSON fournis en paramètre. """
    config_data = load_json(config_file)
    orders_data = load_json(orders_file)

    merged_data = config_data.copy()  # On part des paramètres de config
    merged_data["orders"] = orders_data.get("orders", [])  # Ajout des ordres

    # Sauvegarde du fichier fusionné
    with open(output_file, "w", encoding="utf-8") as output_file:
        json.dump(merged_data, output_file, indent=4)

    print(f"✅ Fichier fusionné enregistré sous {output_file}")
    exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 merge_json.py <config.json> <orders.json>")
        sys.exit(1)

    config_file = sys.argv[1]
    orders_file = sys.argv[2]

    merge_json(config_file, orders_file)
