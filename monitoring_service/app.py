import json
import requests
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required
from api import api
from models import db

app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12345678@localhost/monitoring_service"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["JWT_SECRET_KEY"] = "0ce69303dd65ea3f3b1f0e66bfdf773c0e99ce5e28feb25039d577212c659f98"  # Change in production


# db connection
db.init_app(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

# MQTT Broker Config
MQTT_BROKER = "192.168.8.23"
MQTT_PORT = 1883
TOPIC_SENSOR = "farm/sensor"

# User Management Service (for farm validation)
USER_SERVICE_URL = "http://localhost:5001"

# In-memory cache for last received sensor data
latest_sensor_data = {}

def verify_farm(farm_id):
    """Checks if the given farm_id exists in the User Management Service."""
    try:
        response = requests.get(f"{USER_SERVICE_URL}/farms/{farm_id}")
        return response.status_code == 200
    except requests.RequestException:
        return False

# MQTT Callback for incoming messages
def on_message(client, userdata, msg):
    """Handles incoming sensor data from MQTT and updates the in-memory cache."""
    try:
        payload = json.loads(msg.payload.decode())
        farm_id = payload.get("farm_id")
        moisture = payload.get("moisture")
        temperature = payload.get("temperature")
        humidity = payload.get("humidity")

        if not farm_id or moisture is None:
            print("Invalid sensor data received")
            return

        if not verify_farm(farm_id):
            print(f"Invalid farm ID: {farm_id}")
            return

        # Store the latest sensor values in memory
        latest_sensor_data[farm_id] = {
            "moisture": moisture,
            "temperature": temperature,
            "humidity": humidity
        }
        print(f"Updated latest values for Farm {farm_id}: {latest_sensor_data[farm_id]}")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# MQTT Client Setup
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(TOPIC_SENSOR)
client.loop_start()

@app.route('/sensors/<farm_id>', methods=['GET'])
@jwt_required()
def get_latest_sensor_data(farm_id):
    """Fetches the latest sensor values from memory instead of the database."""
    if farm_id not in latest_sensor_data:
        return jsonify({"error": "No recent sensor data available"}), 404

    return jsonify({
        "farm_id": farm_id,
        "moisture": latest_sensor_data[farm_id]["moisture"],
        "temperature": latest_sensor_data[farm_id]["temperature"],
        "humidity": latest_sensor_data[farm_id]["humidity"]
    })

api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=5001)