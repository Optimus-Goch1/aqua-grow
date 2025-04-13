from flask_restx import Api, Resource, Namespace

api = Api(title="Irrigation Service API", description="API for managing irrigation system", doc="/docs")

irrigation_ns = Namespace("irrigation", description="Irrigation operations")

api.add_namespace(irrigation_ns, path="/irrigation")

@irrigation_ns.route("/manual")
class ManualIrrigation(Resource):
    def post(self):
        """Manually start/stop irrigation"""
        return {"message": "Manual irrigation command sent"}

@irrigation_ns.route("/threshold")
class IrrigationThreshold(Resource):
    def post(self):
        """Set irrigation threshold"""
        return {"message": "Irrigation threshold updated"}