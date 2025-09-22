import pytest
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app as flask_app
from config import create_app
import tempfile

@pytest.fixture
def app():
    """Create application for testing"""
    # Use a temporary database for testing
    test_app, _ = create_app()
    test_app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret-key"
    })
    
    yield test_app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers"""
    # Register a test user
    register_data = {
        "name": "Test Admin",
        "email": "admin@test.com",
        "password": "testpassword123"
    }
    
    response = client.post('/auth/register', json=register_data)
    assert response.status_code == 201
    
    data = response.get_json()
    token = data['access_token']
    
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_quiz_question():
    """Sample quiz question data for testing"""
    return {
        "text": "Test question: How do you prefer to learn?",
        "options": [
            {"text": "Visual aids", "brain_type": "Visual"},
            {"text": "Audio content", "brain_type": "Auditory"},
            {"text": "Reading materials", "brain_type": "ReadWrite"},
            {"text": "Hands-on practice", "brain_type": "Kinesthetic"}
        ]
    }

@pytest.fixture
def sample_resource():
    """Sample resource data for testing"""
    return {
        "title": "Test Learning Resource",
        "url": "https://example.com/test-resource",
        "type": "article",
        "tags": ["Testing", "Education"],
        "est_time": 60
    }