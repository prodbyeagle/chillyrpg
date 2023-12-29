import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

data_directory = r'C:\Users\heypa\rpg_botdata'

@app.route('/api/data/<daten_datei>', methods=['GET'])
def get_data(daten_datei):
    daten_datei_pfad = os.path.join(data_directory, f"{daten_datei}.json")

    if not os.path.isfile(daten_datei_pfad):
        return jsonify({"message": "Daten-Datei nicht gefunden"}), 404

    with open(daten_datei_pfad, 'r') as json_file:
        daten = json.load(json_file)

    return jsonify(daten)

@app.route('/api/data/<daten_datei>', methods=['PUT'])
def update_data(daten_datei):
    daten_datei_pfad = os.path.join(data_directory, f"{daten_datei}.json")

    if not os.path.isfile(daten_datei_pfad):
        return jsonify({"message": "Daten-Datei nicht gefunden"}), 404

    with open(daten_datei_pfad, 'r') as json_file:
        daten = json.load(json_file)

    data = request.get_json()
    daten.update(data)
    with open(daten_datei_pfad, 'w') as json_file:
        json.dump(daten, json_file, indent=4)
    return jsonify({"message": "Daten aktualisiert"})

@app.route('/api/data/list', methods=['GET'])
def get_data_list():
    dateien = os.listdir(data_directory)
    dateien = [datei.replace('.json', '') for datei in dateien if datei.endswith('.json')]
    return jsonify(dateien)

if __name__ == '__main__':
    app.run(debug=True)