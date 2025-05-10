import os
import json
import requests
import paho.mqtt.client as mqtt
from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from src.api import api  #TODO add a verify_farm function remains for farm validation


#load environmental variables
load_dotenv()


INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Initialize JWT
jwt = JWTManager(app)


# InfluxDB setup
influx_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# MQTT config
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
TOPIC_SENSOR = os.getenv("MQTT_TOPIC")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         farm_id = payload.get("farm_id")
#         moisture = payload.get("moisture")
#         temperature = payload.get("temperature")
#         humidity = payload.get("humidity")
#
#         if not farm_id or moisture is None:
#             print("Invalid sensor data received")
#             return
#
#         if not verify_farm(farm_id):
#             print(f"Invalid farm ID: {farm_id}")
#             return
#
#         point = (
#             Point("sensor_readings")
#             .tag("farm_id", farm_id)
#             .field("moisture", moisture)
#             .field("temperature", temperature)
#             .field("humidity", humidity)
#         )
#         write_api.write(bucket=bucket, record=point)
#         print(f"Data written for farm {farm_id}")
#
#     except Exception as e:
#         print(f"Error processing MQTT message: {e}")


# # MQTT setup
# client = mqtt.Client()
# client.on_message = on_message
# client.connect(MQTT_BROKER, MQTT_PORT)
# client.subscribe(TOPIC_SENSOR)
# client.loop_start()




# Swagger
api.init_app(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001) #TODO: turn off debug and configure logging