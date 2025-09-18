import os
from dotenv import load_dotenv
from flask_restx import Api, Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask import request
from models import User, Farm, db
from logging import getLogger


logger = getLogger(__name__)

# Load environment variables
load_dotenv()

# Swagger auth setup
authorizations = {
    'Bearer': {
        'type': 'jwtToken',
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
    security="Bearer",
)


threshold_parser = reqparse.RequestParser()
threshold_parser.add_argument(
    'X-API-KEY',
    location='headers',
    required=True,
    help="Your API key"
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
    "moisture_upper_threshold": fields.Float(required=False),
    "moisture_lower_threshold": fields.Float(required=False),
    "temperature_upper_threshold": fields.Float(required=False),
    "temperature_lower_threshold": fields.Float(required=False),
    "soil_type": fields.String(required=False),
    "crop_type": fields.String(required=False),
    "size": fields.String(required=False),
})

threshold_model = farm_ns.model("Threshold", {
    "moisture_upper_threshold": fields.Float(required=False),
    "moisture_lower_threshold": fields.Float(required=False),
    "temperature_upper_threshold": fields.Float(required=False),
    "temperature_lower_threshold": fields.Float(required=False),
})

update_farm_model = farm_ns.model("UpdateFarm", {
    "esp32_id": fields.String(required=False),
    "farm_name": fields.String(required=False),
    "location": fields.String(required=False),
    "soil_type": fields.String(required=False),
    "crop_type": fields.String(required=False),
    "size_unit": fields.String(required=False),
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
        token = create_access_token(identity=str(user.id))
        return {"token": token, "user": {"id": user.id, "username": user.username}}, 200


def parse_threshold(value):
    return None if value == '' else value


@farm_ns.route("/create_farm")
class FarmCreate(Resource):
    @farm_ns.expect(create_farm_model)
    @farm_ns.doc(security='Bearer')
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.json

        try:
            if Farm.query.filter_by(esp32_id=data["esp32_id"]).first():
                return {"error": "Register a new farm with a new ESP32"}, 400
            farm = Farm(
                name=data["farm_name"],
                location=data["location"],
                esp32_id=data["esp32_id"],
                temperature_upper_threshold=parse_threshold(data.get("temperature_upper_threshold")),
                temperature_lower_threshold=parse_threshold(data.get("temperature_lower_threshold")),
                soil_type=data["soil_type"],
                crop_type=data["crop_type"],
                size_unit=data["size"],
                moisture_upper_threshold=parse_threshold(data.get("moisture_upper_threshold")),
                moisture_lower_threshold=parse_threshold(data.get("moisture_lower_threshold")),
                user_id=user_id
            )
            db.session.add(farm)
            db.session.commit()
            return {"message": "Farm created successfully", "farm_id": farm.id}, 201
        except Exception as e:
            app.logger.error(f"Error creating farm: {e}")
            return {"error": "Error creating farm"}, 500


@farm_ns.route("/update_threshold/<int:farm_id>")
class UpdateFarmThreshold(Resource):
    @farm_ns.expect(threshold_model)
    @farm_ns.doc(security='Bearer')
    @jwt_required()
    def put(self, farm_id):
        user_id = get_jwt_identity()
        farm = Farm.query.filter_by(id=farm_id, user_id=user_id).first()
        if not farm:
            return {"error": "Farm not found or unauthorized"}, 404

        data = request.json

        farm.moisture_lower_threshold = parse_threshold(data.get("moisture_lower_threshold"))
        farm.moisture_upper_threshold = parse_threshold(data.get("moisture_upper_threshold"))
        farm.temperature_upper_threshold = parse_threshold(data.get("temperature_upper_threshold"))
        farm.temperature_lower_threshold = parse_threshold(data.get("temperature_lower_threshold"))

        db.session.commit()
        return {"message": "Thresholds updated successfully"}, 200


@farm_ns.route("/threshold/<string:esp32_id>")
class GetFarmThreshold(Resource):
    @farm_ns.expect(threshold_parser)
    def get(self, esp32_id):
        api_key = request.headers.get("X-API-KEY")
        expected_key = os.getenv("API_KEY")

        logger.info(f"API_KEY: {api_key}")

        if api_key != expected_key:
            return {"error": "Unauthorized"}, 401

        farm = Farm.query.filter_by(esp32_id=esp32_id).first()
        if not farm:
            return {"error": "Farm not found or unauthorized"}, 404

        return {
            "moisture_lower_threshold": farm.moisture_lower_threshold,
            "moisture_upper_threshold": farm.moisture_upper_threshold,
            "temperature_lower_threshold": farm.temperature_lower_threshold,
            "temperature_upper_threshold": farm.temperature_upper_threshold
        }, 200


@farm_ns.route("/my_farms")
class FarmsByUser(Resource):
    @farm_ns.doc(security='Bearer')
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        farms = Farm.query.filter_by(user_id=user_id).all()
        farms_list = [{
            "id": f.id,
            "name": f.name,
            "location": f.location,
            "esp32_id": f.esp32_id,
            "crop_type": f.crop_type,
            "size":f.size_unit,
            "temperature_upper_threshold":f.temperature_upper_threshold,
            "temperature_lower_threshold": f.temperature_lower_threshold,
            "moisture_upper_threshold": f.moisture_upper_threshold,
            "moisture_lower_threshold" : f.moisture_lower_threshold,


        } for f in farms]
        return {"farms": farms_list}, 200
    
@farm_ns.route("/update_farm/<int:farm_id>")
class FarmUpdate(Resource):
    @farm_ns.expect(update_farm_model)
    @farm_ns.doc(security="Bearer")
    @jwt_required()
    def put(self, farm_id):
        user_id = get_jwt_identity()
        farm = Farm.query.filter_by(id=farm_id, user_id=user_id).first()

        if not farm:
            return {"error": "Farm not found or unauthorized"}, 404

        data = request.get_json()

        farm.name = data.get("farm_name", farm.name)
        farm.esp32_id = data.get("esp32_id", farm.esp32_id)
        farm.soil_type = data.get("soil_type", farm.soil_type)
        farm.crop_type = data.get("crop_type", farm.crop_type)
        farm.size_unit = data.get("size_unit", farm.size_unit)
        db.session.commit()

        return {"message": "Farm updated successfully"}, 200


@farm_ns.route("/delete_farm/<int:farm_id>")
class FarmDelete(Resource):
    @farm_ns.doc(security="Bearer")
    @jwt_required()
    def delete(self, farm_id):
        user_id = get_jwt_identity()
        farm = Farm.query.filter_by(id=farm_id, user_id=user_id).first()
        if not farm:
            return {"error": "Farm not found or unauthorized"}, 404
        db.session.delete(farm)
        db.session.commit()
        return {"message": "Farm deleted successfully"}, 200






api.add_namespace(user_ns, path="/users")
api.add_namespace(farm_ns, path="/farms")
