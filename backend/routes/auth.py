from flask import Blueprint, request, jsonify
<<<<<<< HEAD
from flask_jwt_extended import jwt_required, get_jwt_identity

try:
    from services.auth_service import register_user, login_user, get_user_from_token
except ImportError:  # pragma: no cover - supports package import style
    from ..services.auth_service import register_user, login_user, get_user_from_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        result = register_user(request.get_json(silent=True) or {})
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"msg": str(exc)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        result = login_user(request.get_json(silent=True) or {})
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"msg": str(exc)}), 400
    except PermissionError as exc:
        return jsonify({"msg": str(exc)}), 401
=======
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
import os
from datetime import datetime
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
client = MongoClient(mongo_uri)
db = client.get_database()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if db.users.find_one({"email": data["email"]}):
        return jsonify({"msg": "Email already registered."}), 400
    user = {
        "name": data["name"],
        "email": data["email"],
        "password_hash": generate_password_hash(data["password"]),
        "brain_type": data.get("brain_type"),
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user)
    return jsonify({"msg": "User registered successfully."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = db.users.find_one({"email": data["email"]})
    if not user or not check_password_hash(user["password_hash"], data["password"]):
        return jsonify({"msg": "Invalid credentials."}), 401
    access_token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": access_token}), 200
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
<<<<<<< HEAD
    try:
        user_data = get_user_from_token(get_jwt_identity())
        return jsonify({"msg": "Token valid.", "user": user_data}), 200
    except LookupError as exc:
        return jsonify({"msg": str(exc)}), 401
=======
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"msg": "Invalid token."}), 401
    
    user_data = {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user["email"],
        "brain_type": user.get("brain_type")
    }
    
    return jsonify({
        "msg": "Token valid.", 
        "user": user_data
    }), 200
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
