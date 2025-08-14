from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask import jsonify, request
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


authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Paste your JWT token here with **Bearer** prefix'
    }
}


# Namespace and API setup
sensor_ns = Namespace("sensors", description="Sensor monitoring endpoints")
api = Api(
    title="Sensor Monitoring API",
    version="1.0",
    description="API for real-time farm sensor monitoring",
    doc="sesnor/docs",
    authorizations=authorizations,
    security="Bearer"
)

# InfluxDB setup
influx_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)
query_api = influx_client.query_api()
write_api = influx_client.write_api()

simulate_model = sensor_ns.model("Simulate", {
    "farm_id": fields.Integer(required=True),

})


@sensor_ns.route("/<string:esp32_id>")
class SensorData(Resource):
    @sensor_ns.doc(security='Bearer')
    @jwt_required()
    def get(self, esp32_id):
        esp32_id = str(esp32_id)
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -30d)
          |> filter(fn: (r) => r._measurement == "sensor_readings" and r.farm_id == "{str(eps32_id)}")
          |> last()
        '''
        try:
            tables = query_api.query(query)
            data = {}
            for table in tables:
                for record in table.records:
                    data[record.get_field()] = int(record.get_value())

            if not data:
                return {"error": "No recent sensor data available"}, 404

            data["farm_id"] = farm_id
            return data, 200

        except Exception as e:
            return {"error": str(e)}, 500




@sensor_ns.route("/simulate")
class SimulateSensor(Resource):
    @sensor_ns.expect(simulate_model)
    def post(self, farm_id="demo-farm"):
        # Generate random values
        moisture = random.uniform(300, 800)
        temperature = random.uniform(20, 35)
        humidity = random.uniform(40, 90)

        moisture = (moisture / 800) * 100

        data = request.get_json()
        if not data or 'farm_id' not in data:
            return {"error": "farm_id is required in request body"}, 400

        farm_id = data['farm_id']

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