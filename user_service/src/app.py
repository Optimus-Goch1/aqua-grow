from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Farm, bcrypt
from api import api

app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12345678@localhost/user_service"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["JWT_SECRET_KEY"] = "0ce69303dd65ea3f3b1f0e66bfdf773c0e99ce5e28feb25039d577212c659f98"
app.config['JWT_VERIFY_SUB'] = False

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.route('/signup', methods=['POST'])
def signup():
    """Handles user sign-up."""
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Handles user login and returns JWT token."""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token, "user": {"id": user.id, "username": user.username}}), 200

@app.route('/create_farm', methods=['POST'])
@jwt_required()
def create_farm():
    """Creates a new farm and assigns it to the authenticated user."""
    user_id = get_jwt_identity()
    data = request.json
    farm_name = data.get("name")
    location = data.get("location")

    if not farm_name:
        return jsonify({"error": "Farm name is required"}), 400

    if Farm.query.filter_by(name=farm_name).first():
        return jsonify({"error": "Farm name must be unique"}), 400

    new_farm = Farm(name=farm_name, location=location, user_id=user_id)
    db.session.add(new_farm)
    db.session.commit()

    return jsonify({"message": "Farm created successfully", "farm_id": new_farm.id}), 201

@app.route('/farms/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_farms(user_id):
    """Returns all farms owned by the user."""
    farms = Farm.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": f.id, "name": f.name, "location": f.location} for f in farms])

@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Fetch user details."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "username": user.username, "email": user.email, "role": user.role})

@app.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """List all users (admin-only)."""
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in users])


@app.route('/farms/threshold', methods=['POST'])
@jwt_required()
def set_or_update_farm_threshold():
    """Allows users to set or update the moisture threshold for their farm."""
    user_id = get_jwt_identity()
    data = request.json
    farm_id = data.get("farm_id")
    threshold = data.get("threshold")

    if not farm_id or threshold is None:
        return jsonify({"error": "Farm ID and threshold are required"}), 400

    farm = Farm.query.filter_by(id=farm_id, user_id=user_id).first()
    if not farm:
        return jsonify({"error": "Farm not found or unauthorized"}), 404

    farm.threshold = threshold
    db.session.commit()

    return jsonify({"message": "Threshold updated successfully", "farm_id": farm.id, "threshold": farm.threshold}), 200

@app.route('/farms/<int:farm_id>/threshold', methods=['GET'])
@jwt_required()
def get_farm_threshold(farm_id):
    """Fetches the moisture threshold for a given farm."""
    user_id = get_jwt_identity()
    farm = Farm.query.filter_by(id=farm_id, user_id=user_id).first()

    if not farm:
        return jsonify({"error": "Farm not found or unauthorized"}), 404

    return jsonify({"farm_id": farm.id, "threshold": farm.threshold})


@app.route("/health")
def health():
    return {"status": "ok"}, 200


api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=5000)