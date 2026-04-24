from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
<<<<<<< HEAD
import os
from datetime import timedelta
from dotenv import load_dotenv

from mongo_utils import create_mongo_client, get_mongo_uri

# Load environment variables from .env file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
=======
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
<<<<<<< HEAD
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
=======
jwt = JWTManager(app)

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
client = MongoClient(mongo_uri)
db = client.get_database()
app.db = db  # Make db available through app context
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b

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
<<<<<<< HEAD
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
=======
    app.run(debug=True, host='0.0.0.0', port=5000)
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
