from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
jwt = JWTManager(app)

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
client = MongoClient(mongo_uri)
db = client.get_database()
app.db = db  # Make db available through app context

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
    app.run(debug=True, host='0.0.0.0', port=5000)
