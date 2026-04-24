from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta
from dotenv import load_dotenv

from mongo_utils import create_mongo_client, get_mongo_uri

# Load environment variables from .env file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_HOURS', '24')))
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
jwt = JWTManager(app)


@jwt.unauthorized_loader
def handle_missing_token(reason: str):
    return {"msg": f"Missing or malformed Authorization header: {reason}"}, 401


@jwt.invalid_token_loader
def handle_invalid_token(reason: str):
    return {"msg": f"Invalid token: {reason}"}, 401


@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    _ = jwt_header
    _ = jwt_payload
    return {"msg": "Token expired. Please sign in again."}, 401


@jwt.revoked_token_loader
def handle_revoked_token(jwt_header, jwt_payload):
    _ = jwt_header
    _ = jwt_payload
    return {"msg": "Token revoked. Please sign in again."}, 401

# MongoDB connection
client = create_mongo_client()
app.db = client.get_database()  # Make db available through app context
print(f"✅ MongoDB client initialized with {get_mongo_uri()}")

# Import and register routesthe 
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from routes.quiz import quiz_bp
app.register_blueprint(quiz_bp, url_prefix='/quiz')

from routes.roadmaps import roadmaps_bp
app.register_blueprint(roadmaps_bp)

from routes.progress import progress_bp
app.register_blueprint(progress_bp)

# Add a simple root route for testing
@app.route('/')
def home():
    return {
        "message": "NeuroNav API is running! 🧠",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth (register, login, verify-token)",
            "quiz": "/quiz (questions, submit)",
            "roadmaps": "/roadmaps",
            "progress": "/progress"
        },
        "status": "healthy"
    }

# Commenting out admin routes for now
# from routes.admin import admin_bp
# app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
