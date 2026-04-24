from flask import Blueprint, request, jsonify
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

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        user_data = get_user_from_token(get_jwt_identity())
        return jsonify({"msg": "Token valid.", "user": user_data}), 200
    except LookupError as exc:
        return jsonify({"msg": str(exc)}), 401
