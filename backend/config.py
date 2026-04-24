import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

from mongo_utils import create_mongo_client, get_mongo_uri

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_SECONDS', '86400'))  # 24 hours
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-flask-secret-key')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    jwt = JWTManager(app)
    CORS(app, origins=["http://localhost:5173"])  # React dev server
    
    # MongoDB connection
    try:
        client = create_mongo_client()
        db = client.neuronav
        app.db = db
        print(f"✅ Connected to MongoDB successfully ({get_mongo_uri()})")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        app.db = None
    
    return app, jwt

def get_db():
    from flask import current_app
    return current_app.db