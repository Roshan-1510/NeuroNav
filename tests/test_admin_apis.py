import pytest
import json
from bson import ObjectId

class TestQuizQuestionAPIs:
    """Test quiz question management APIs"""
    
    def test_get_quiz_questions_empty(self, client, auth_headers):
        """Test getting quiz questions when database is empty"""
        response = client.get('/admin/quiz/questions', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'questions' in data
        assert 'count' in data
        assert isinstance(data['questions'], list)
        assert data['count'] == len(data['questions'])
    
    def test_add_quiz_question_success(self, client, auth_headers, sample_quiz_question):
        """Test successfully adding a quiz question"""
        response = client.post('/admin/quiz/questions', 
                             json=sample_quiz_question, 
                             headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'message' in data
        assert 'question_id' in data
        assert data['message'] == 'Quiz question added successfully'
    
    def test_add_quiz_question_missing_fields(self, client, auth_headers):
        """Test adding quiz question with missing required fields"""
        incomplete_data = {"text": "Incomplete question"}
        
        response = client.post('/admin/quiz/questions', 
                             json=incomplete_data, 
                             headers=auth_headers)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
    
    def test_add_quiz_question_invalid_options(self, client, auth_headers):
        """Test adding quiz question with invalid options format"""
        invalid_data = {
            "text": "Test question",
            "options": [{"text": "Missing brain_type"}]
        }
        
        response = client.post('/admin/quiz/questions', 
                             json=invalid_data, 
                             headers=auth_headers)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'brain_type' in data['error']
    
    def test_quiz_question_crud_flow(self, client, auth_headers, sample_quiz_question):
        """Test complete CRUD flow for quiz questions"""
        # Create
        response = client.post('/admin/quiz/questions', 
                             json=sample_quiz_question, 
                             headers=auth_headers)
        assert response.status_code == 201
        question_id = response.get_json()['question_id']
        
        # Read
        response = client.get('/admin/quiz/questions', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 1
        assert data['questions'][0]['text'] == sample_quiz_question['text']
        
        # Update
        updated_data = {
            "text": "Updated test question",
            "options": sample_quiz_question['options']
        }
        response = client.put(f'/admin/quiz/questions/{question_id}', 
                            json=updated_data, 
                            headers=auth_headers)
        assert response.status_code == 200
        
        # Verify update
        response = client.get('/admin/quiz/questions', headers=auth_headers)
        data = response.get_json()
        assert data['questions'][0]['text'] == "Updated test question"
        
        # Delete
        response = client.delete(f'/admin/quiz/questions/{question_id}', 
                               headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get('/admin/quiz/questions', headers=auth_headers)
        data = response.get_json()
        assert data['count'] == 0
    
    def test_quiz_question_unauthorized(self, client, sample_quiz_question):
        """Test quiz question APIs without authentication"""
        # No auth headers
        response = client.get('/admin/quiz/questions')
        assert response.status_code == 401
        
        response = client.post('/admin/quiz/questions', json=sample_quiz_question)
        assert response.status_code == 401

class TestResourceAPIs:
    """Test resource management APIs"""
    
    def test_get_resources_empty(self, client, auth_headers):
        """Test getting resources when database is empty"""
        response = client.get('/admin/resources', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'resources' in data
        assert 'count' in data
        assert isinstance(data['resources'], list)
    
    def test_add_resource_success(self, client, auth_headers, sample_resource):
        """Test successfully adding a resource"""
        response = client.post('/admin/resources', 
                             json=sample_resource, 
                             headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'message' in data
        assert 'resource_id' in data
        assert data['message'] == 'Resource added successfully'
    
    def test_add_resource_missing_fields(self, client, auth_headers):
        """Test adding resource with missing required fields"""
        incomplete_data = {"title": "Incomplete resource"}
        
        response = client.post('/admin/resources', 
                             json=incomplete_data, 
                             headers=auth_headers)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
    
    def test_resource_crud_flow(self, client, auth_headers, sample_resource):
        """Test complete CRUD flow for resources"""
        # Create
        response = client.post('/admin/resources', 
                             json=sample_resource, 
                             headers=auth_headers)
        assert response.status_code == 201
        resource_id = response.get_json()['resource_id']
        
        # Read
        response = client.get('/admin/resources', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 1
        assert data['resources'][0]['title'] == sample_resource['title']
        
        # Update
        updated_data = {
            "title": "Updated Test Resource",
            "est_time": 120
        }
        response = client.put(f'/admin/resources/{resource_id}', 
                            json=updated_data, 
                            headers=auth_headers)
        assert response.status_code == 200
        
        # Verify update
        response = client.get('/admin/resources', headers=auth_headers)
        data = response.get_json()
        assert data['resources'][0]['title'] == "Updated Test Resource"
        
        # Delete
        response = client.delete(f'/admin/resources/{resource_id}', 
                               headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get('/admin/resources', headers=auth_headers)
        data = response.get_json()
        assert data['count'] == 0
    
    def test_get_resources_with_filters(self, client, auth_headers):
        """Test getting resources with topic and type filters"""
        # Add multiple resources
        resources = [
            {
                "title": "Python Tutorial",
                "url": "https://example.com/python",
                "type": "tutorial",
                "tags": ["Python", "Programming"]
            },
            {
                "title": "Data Science Article",
                "url": "https://example.com/datascience",
                "type": "article",
                "tags": ["Data Science", "Analytics"]
            }
        ]
        
        for resource in resources:
            client.post('/admin/resources', json=resource, headers=auth_headers)
        
        # Test topic filter
        response = client.get('/admin/resources?topic=Python', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 1
        assert "Python" in data['resources'][0]['tags']
        
        # Test type filter
        response = client.get('/admin/resources?type=tutorial', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 1
        assert data['resources'][0]['type'] == 'tutorial'
    
    def test_resource_unauthorized(self, client, sample_resource):
        """Test resource APIs without authentication"""
        # No auth headers
        response = client.get('/admin/resources')
        assert response.status_code == 401
        
        response = client.post('/admin/resources', json=sample_resource)
        assert response.status_code == 401

class TestInvalidObjectIds:
    """Test handling of invalid ObjectIds"""
    
    def test_invalid_question_id(self, client, auth_headers):
        """Test operations with invalid question ID"""
        invalid_id = "invalid-object-id"
        
        response = client.put(f'/admin/quiz/questions/{invalid_id}', 
                            json={"text": "Updated"}, 
                            headers=auth_headers)
        assert response.status_code == 400
        
        response = client.delete(f'/admin/quiz/questions/{invalid_id}', 
                               headers=auth_headers)
        assert response.status_code == 400
    
    def test_invalid_resource_id(self, client, auth_headers):
        """Test operations with invalid resource ID"""
        invalid_id = "invalid-object-id"
        
        response = client.put(f'/admin/resources/{invalid_id}', 
                            json={"title": "Updated"}, 
                            headers=auth_headers)
        assert response.status_code == 400
        
        response = client.delete(f'/admin/resources/{invalid_id}', 
                               headers=auth_headers)
        assert response.status_code == 400
    
    def test_nonexistent_ids(self, client, auth_headers):
        """Test operations with valid but nonexistent ObjectIds"""
        nonexistent_id = str(ObjectId())
        
        # Quiz question
        response = client.put(f'/admin/quiz/questions/{nonexistent_id}', 
                            json={"text": "Updated"}, 
                            headers=auth_headers)
        assert response.status_code == 404
        
        response = client.delete(f'/admin/quiz/questions/{nonexistent_id}', 
                               headers=auth_headers)
        assert response.status_code == 404
        
        # Resource
        response = client.put(f'/admin/resources/{nonexistent_id}', 
                            json={"title": "Updated"}, 
                            headers=auth_headers)
        assert response.status_code == 404
        
        response = client.delete(f'/admin/resources/{nonexistent_id}', 
                               headers=auth_headers)
        assert response.status_code == 404