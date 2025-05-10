from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import jwt_required
from flask import jsonify
import os
from influxdb_client import InfluxDBClient, Point
from dotenv import load_dotenv
import random


# load environmental variables
load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# Namespace and API setup
sensor_ns = Namespace("sensors", description="Sensor monitoring endpoints")
api = Api(
    title="Sensor Monitoring API",
    version="1.0",
    description="API for real-time farm sensor monitoring",
    doc="/docs"
)

# InfluxDB setup
influx_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)
query_api = influx_client.query_api()
write_api = influx_client.write_api()


@sensor_ns.route("/<string:farm_id>")
class SensorData(Resource):
    @sensor_ns.doc(security='Bearer')
    # @jwt_required() TODO: fix this to only allow authorized users view their farm sensor data
    def get(self, farm_id):
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "sensor_readings" and r.farm_id == "{farm_id}")
          |> last()
        '''

        try:
            tables = query_api.query(query)
            data = {}
            for table in tables:
                for record in table.records:
                    data[record.get_field()] = record.get_value()

            if not data:
                return {"error": "No recent sensor data available"}, 404

            data["farm_id"] = farm_id
            return data, 200

        except Exception as e:
            return {"error": str(e)}, 500




@sensor_ns.route("/simulate")
class SimulateSensor(Resource):
    def post(self, farm_id="demo-farm"):
        # Generate random values
        moisture = random.uniform(300, 800)
        temperature = random.uniform(20, 35)
        humidity = random.uniform(40, 90)

        point = (
            Point("sensor_readings")
            .tag("farm_id", farm_id)
            .field("moisture", moisture)
            .field("temperature", temperature)
            .field("humidity", humidity)
        )
        try:
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            return {
                "message": "Dummy data written to InfluxDB",
                "data": {
                    "farm_id": farm_id,
                    "moisture": round(moisture, 2),
                    "temperature": round(temperature, 2),
                    "humidity": round(humidity, 2)
                }
            }, 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


api.add_namespace(sensor_ns, path="/sensors")
