from flask_restx import Api, Resource, Namespace, fields
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask import request
from models import User, Farm, db

# Swagger auth setup
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Paste your JWT token here with **Bearer** prefix'
    }
}

api = Api(
    title="User Management API",
    version="1.0",
    description="API for managing users and farms",
    doc="/docs",
    authorizations=authorizations,
    security="Bearer"
)

user_ns = Namespace("users", description="User operations")
farm_ns = Namespace("farms", description="Farm operations")

# Models
signup_model = user_ns.model("Signup", {
    "username": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True),
})

login_model = user_ns.model("Login", {
    "email": fields.String(required=True),
    "password": fields.String(required=True),
})

create_farm_model = farm_ns.model("CreateFarm", {
    "esp32_id": fields.String(required=True),
    "farm_name": fields.String(required=True),
    "location": fields.String(required=True),
})

threshold_model = farm_ns.model("Threshold", {
    "farm_id": fields.Integer(required=True),
    "threshold": fields.Float(required=True),
})


@user_ns.route("/signup")
class UserSignup(Resource):
    @user_ns.expect(signup_model)
    def post(self):
        data = request.json
        if User.query.filter_by(email=data["email"]).first():
            return {"error": "Email already registered"}, 400
        user = User(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201


@user_ns.route("/login")
class UserLogin(Resource):
    @user_ns.expect(login_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.check_password(data["password"]):
            return {"error": "Invalid credentials"}, 401
        token = create_access_token(identity=user.id)
        return {"token": token, "user": {"id": user.id, "username": user.username}}, 200


@farm_ns.route("/create_farm")
class FarmCreate(Resource):
    @farm_ns.expect(create_farm_model)
    @farm_ns.doc(security='Bearer')
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.json
        if Farm.query.filter_by(esp32_id=data["esp32_id"]):
            return {"error": "Register a new farm with a new ESP32"}, 400
        farm = Farm(name=data["farm_name"], location=data["location"], esp32_id=data["esp32_id"], user_id=user_id)
        db.session.add(farm)
        db.session.commit()
        return {"message": "Farm created successfully", "farm_id": farm.id}, 201


@farm_ns.route("/threshold")
class FarmThreshold(Resource):
    @farm_ns.expect(threshold_model)
    @farm_ns.doc(security='Bearer')
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.json
        farm = Farm.query.filter_by(id=data["farm_id"], user_id=user_id).first()
        if not farm:
            return {"error": "Farm not found or unauthorized"}, 404
        farm.threshold = data["threshold"]
        db.session.commit()
        return {"message": "Threshold updated", "threshold": farm.threshold}, 200

@farm_ns.route("/user/<int:user_id>")
class FarmsByUser(Resource):
    @farm_ns.doc(security='Bearer')
    @jwt_required()
    def get(self, user_id):
        farms = Farm.query.filter_by(user_id=user_id).all()
        return [{
            "id": f.id,
            "name": f.name,
            "location": f.location,
            "esp32_id": f.esp32_id,
            "threshold": f.threshold
        } for f in farms], 200






api.add_namespace(user_ns, path="/users")
api.add_namespace(farm_ns, path="/farms")
