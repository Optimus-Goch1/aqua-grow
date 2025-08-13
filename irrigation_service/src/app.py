import json
import os

import requests
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import logging



app = Flask(__name__)
load_dotenv()

logging.basicConfig(level=logging.DEBUG)  # Make sure debug messages are shown
app.logger.setLevel(logging.DEBUG)        # Set app's logger to debug



app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

jwt = JWTManager(app)

# MQTT Broker Config
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MONITORING_TOPIC = os.getenv("MONITORING_TOPIC")
IRRIGATION_TOPIC = os.getenv("IRRIGATION_TOPIC")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
API_KEY = os.getenv("API_KEY")

# MQTT Client Setup
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT)



cache = {}

def control_irrigation(esp32_id, action):
    """Publishes ON/OFF commands to the irrigation system."""
    message = json.dumps({
        "esp32_id": esp32_id,
        "action": action  # "1" for ON, "0" for OFF
    })
    client.publish(IRRIGATION_TOPIC, message)


def get_threshold_from_user_service(esp32_id):
    """Fetches the irrigation threshold for a farm from User Management Service."""
    try:
        url = f"{USER_SERVICE_URL}/farms/threshold/{esp32_id}"
        headers = {"X-API-KEY": API_KEY}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            cache[esp32_id] = response.json()
            return response.json()  # Return parsed threshold data
        else:
            app.logger.warning(
                f"Failed to fetch threshold for farm {esp32_id}. "
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return None

    except requests.RequestException as e:
        app.logger.error(f"Error fetching threshold from User Service: {e}")
        return None

def on_message(mqtt_client, userdata, msg):
    """Handles incoming sensor data and triggers irrigation if needed."""
    try:
        payload = json.loads(msg.payload.decode())
        esp32_id = payload.get("esp32_id")
        moisture = payload.get("moisture")
        app.logger.debug(f"Received payload: {payload}")

        # Fetch the thresholds from User Management Service
        if esp32_id in cache:
            threshold = cache[esp32_id]
        else:
            threshold = get_threshold_from_user_service(esp32_id)

        temperature_upper_threshold = threshold.get("temperature_upper_threshold", None)
        temperature_lower_threshold = threshold.get("temperature_lower_threshold", None)
        moisture_upper_threshold = threshold.get("moisture_upper_threshold")
        moisture_lower_threshold = threshold.get("moisture_lower_threshold")



        # Determine irrigation action
        if moisture < moisture_lower_threshold:
            control_irrigation(esp32_id, "1")
        elif moisture >= moisture_upper_threshold:
            control_irrigation(esp32_id, "0")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")
@app.route('/irrigation/toggle/<string:esp32_id>', methods=['POST'])
@jwt_required()
def manual_irrigation(esp32_id):
    """Allows users to manually start or stop irrigation."""
    user_id = get_jwt_identity()
    data = request.json
    action = data.get("action")  # "ON" or "OFF"

    app.logger.debug(f"Payload: {data}")
    app.logger.debug(f"ESP32 ID: {esp32_id}")

    action = "1" if action is True else "0"

    # if action not in ["ON", "OFF"]:
    #     return jsonify({"error": "Invalid action"}), 400

    control_irrigation(esp32_id, action)
    return jsonify({"message": f"Irrigation {action} for Farm {esp32_id}"}), 200



# Subscribe to MQTT sensor data
client.subscribe(MONITORING_TOPIC)
client.on_message = on_message
client.loop_start()

@app.route("/irrigation")
def health():
    return {"status": "The irrigation service is up and running"}, 200

@app.route("/")
def landing_page_route():
    return {"AquaGrow Landing Page"}, 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5000)