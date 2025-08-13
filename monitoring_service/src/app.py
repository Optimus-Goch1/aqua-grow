import os
import json
import logging
from datetime import datetime

import requests
import paho.mqtt.client as mqtt
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from api import api

# Load .env
load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_VERIFY_SUB'] = False

app.logger.setLevel(logging.DEBUG)

jwt = JWTManager(app)

# InfluxDB setup
influx_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# MQTT config
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MONITORING_TOPIC = os.getenv("MONITORING_TOPIC")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        app.logger.info("Connected to MQTT Broker")
        mqtt_client.subscribe(MONITORING_TOPIC)
    else:
        app.logger.error(f"Failed to connect to MQTT Broker, return code {rc}")

def on_message(mqtt_client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        esp32_id = payload.get("esp32_id")
        moisture = payload.get("moisture")

        if not esp32_id or moisture is None:
            app.logger.warning("Invalid sensor data received")
            return

        point = (
            Point("sensor_readings")
            .tag("esp32_id", esp32_id)
            .field("moisture", moisture)
        )
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        app.logger.info(f"Data written for ESP32 {esp32_id} at")

    except Exception as e:
        app.logger.error(f"Error processing MQTT message: {e}")

# MQTT setup
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

# API
api.init_app(app)

@app.route("/sensors")
def health():
    return {"status": "The monitoring service is up and running"}, 200

@app.route("/")
def landing_page_route():
    return {"AquaGrow Landing Page"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)