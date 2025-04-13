from flask_restx import Api, Resource, Namespace

api = Api(title="Sensor Data API", description="API for managing sensor data", doc="/docs")

sensor_ns = Namespace("sensors", description="Sensor data operations")

api.add_namespace(sensor_ns, path="/sensors")

@sensor_ns.route("/<farm_id>")
class GetSensorData(Resource):
    def get(self, farm_id):
        """Fetches the latest sensor data for a farm"""
        return {"message": f"Latest sensor data for farm {farm_id}"}