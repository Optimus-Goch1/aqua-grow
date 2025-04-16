from flask_restx import Api, Resource, Namespace, fields

api = Api(title="User Management API", description="API for managing users and farms", doc="/docs")

user_ns = Namespace("users", description="User operations")
farm_ns = Namespace("farms", description="Farm operations")

api.add_namespace(user_ns, path="/")
api.add_namespace(farm_ns, path="/")


signup_model = api.model("Signup", {
    "username": fields.String(required=True, description="Username of the user"),
    "email": fields.String(required=True, description="User's email"),
    "password": fields.String(required=True, description="User's password"),
})

login_model = api.model("Login", {
    "email": fields.String(required=True, description="User's email"),
    "password": fields.String(required=True, description="User's password"),
})

threshold_model = api.model("Threshold", {
    "farm_id": fields.Integer(required=True, description="Farm ID"),
    "threshold": fields.Float(required=True, description="Moisture threshold"),
})


@user_ns.route("signup")
class UserSignup(Resource):
    @api.expect(signup_model)
    def post(self):
        """Handles user sign-up"""
        return {"message": "Signup endpoint"}

@user_ns.route("login")
class UserLogin(Resource):
    @api.expect(login_model)
    def post(self):
        """Handles user login"""
        return {"message": "Login endpoint"}

@farm_ns.route("threshold")
class FarmThreshold(Resource):
    @api.expect(threshold_model)
    def post(self):
        """Set or update the irrigation threshold"""
        return {"message": "Threshold set"}