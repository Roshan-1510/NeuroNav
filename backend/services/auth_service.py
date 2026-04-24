"""Authentication business logic service."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from bson import ObjectId
from flask import current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash


def register_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new user and return a success payload."""
    if not data or not data.get("email") or not data.get("password") or not data.get("name"):
        raise ValueError("name, email, and password are required")

    db = current_app.db
    email = str(data["email"]).strip().lower()

    if db.users.find_one({"email": email}):
        raise ValueError("Email already registered.")

    user_doc = {
        "name": data["name"],
        "email": email,
        "password_hash": generate_password_hash(data["password"]),
        "brain_type": data.get("brain_type"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    db.users.insert_one(user_doc)
    return {"msg": "User registered successfully."}


def login_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate credentials and return JWT token payload."""
    if not data or not data.get("email") or not data.get("password"):
        raise ValueError("email and password are required")

    db = current_app.db
    email = str(data["email"]).strip().lower()
    user = db.users.find_one({"email": email})

    if not user or not check_password_hash(user["password_hash"], data["password"]):
        raise PermissionError("Invalid credentials.")

    access_token = create_access_token(identity=str(user["_id"]))
    return {"access_token": access_token}


def get_user_from_token(user_id: str) -> Dict[str, Any]:
    """Fetch user profile for token verification."""
    db = current_app.db
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise LookupError("Invalid token.")

    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "brain_type": user.get("brain_type"),
    }
