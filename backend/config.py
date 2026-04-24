import os
<<<<<<< HEAD
=======
from pymongo import MongoClient
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

<<<<<<< HEAD
from mongo_utils import create_mongo_client, get_mongo_uri

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
=======
load_dotenv()
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
    
    # JWT Configuration
<<<<<<< HEAD
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_SECONDS', '86400'))  # 24 hours
=======
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
    
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
<<<<<<< HEAD
        client = create_mongo_client()
        db = client.neuronav
        app.db = db
        print(f"✅ Connected to MongoDB successfully ({get_mongo_uri()})")
=======
        client = MongoClient(Config.MONGO_URI)
        db = client.neuronav
        app.db = db
        print("✅ Connected to MongoDB successfully")
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        app.db = None
    
    return app, jwt

def get_db():
    from flask import current_app
    return current_app.db