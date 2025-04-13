import json
import requests
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from api import api

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "0ce69303dd65ea3f3b1f0e66bfdf773c0e99ce5e28feb25039d577212c659f98"

jwt = JWTManager(app)

# MQTT Broker Config
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
TOPIC_SENSOR = "farm/sensor"
TOPIC_IRRIGATION = "farm/irrigate"
USER_SERVICE_URL = "http://localhost:5001"

# MQTT Client Setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)

def control_irrigation(farm_id, action):
    """Publishes ON/OFF commands to the irrigation system."""
    payload = json.dumps({"farm_id": farm_id, "action": action})
    client.publish(TOPIC_IRRIGATION, payload)
    print(f"Irrigation {action} command sent for Farm {farm_id}")

def get_threshold_from_user_service(farm_id):
    """Fetches the irrigation threshold for a farm from User Management Service."""
    try:
        response = requests.get(f"{USER_SERVICE_URL}/farms/{farm_id}/threshold")
        if response.status_code == 200:
            return response.json().get("threshold")
    except requests.RequestException:
        pass
    return None

def on_message(client, userdata, msg):
    """Handles incoming sensor data and triggers irrigation if needed."""
    try:
        payload = json.loads(msg.payload.decode())
        farm_id = payload.get("farm_id")
        moisture = payload.get("moisture")

        # Fetch threshold from User Management Service
        threshold = get_threshold_from_user_service(farm_id)
        if threshold is None:
            print(f"No threshold set for Farm {farm_id}, skipping irrigation check.")
            return

        # Determine irrigation action
        if moisture < threshold:
            control_irrigation(farm_id, "ON")
        else:
            control_irrigation(farm_id, "OFF")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")
@app.route('/irrigate/manual', methods=['POST'])
@jwt_required()
def manual_irrigation():
    """Allows users to manually start or stop irrigation."""
    data = request.json
    farm_id = data.get("farm_id")
    action = data.get("action")  # "ON" or "OFF"

    if action not in ["ON", "OFF"]:
        return jsonify({"error": "Invalid action"}), 400

    control_irrigation(farm_id, action)
    return jsonify({"message": f"Irrigation {action} command sent for Farm {farm_id}"}), 200



# Subscribe to MQTT sensor data
client.subscribe(TOPIC_SENSOR)
client.on_message = on_message
client.loop_start()


api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=5003)