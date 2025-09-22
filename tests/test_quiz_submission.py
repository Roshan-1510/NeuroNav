import pytest
import json
from unittest.mock import patch, MagicMock

class TestQuizQuestions:
    """Test quiz questions endpoint"""
    
    def test_get_quiz_questions_success(self, client, auth_headers):
        """Test successfully getting quiz questions"""
        # First, add some quiz questions via admin API
        sample_questions = [
            {
                "text": "How do you prefer to learn?",
                "options": [
                    {"text": "Visual aids", "brain_type": "Visual"},
                    {"text": "Audio content", "brain_type": "Auditory"},
                    {"text": "Reading", "brain_type": "ReadWrite"},
                    {"text": "Hands-on", "brain_type": "Kinesthetic"}
                ]
            },
            {
                "text": "When studying, you prefer:",
                "options": [
                    {"text": "Diagrams", "brain_type": "Visual"},
                    {"text": "Discussions", "brain_type": "Auditory"},
                    {"text": "Notes", "brain_type": "ReadWrite"},
                    {"text": "Practice", "brain_type": "Kinesthetic"}
                ]
            }
        ]
        
        # Add questions via admin API
        for question in sample_questions:
            client.post('/admin/quiz/questions', json=question, headers=auth_headers)
        
        # Get quiz questions
        response = client.get('/quiz/questions', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'questions' in data
        assert 'total_questions' in data
        assert 'instructions' in data
        assert len(data['questions']) == 2
        
        # Check question structure
        question = data['questions'][0]
        assert 'question_id' in question
        assert 'question_number' in question
        assert 'text' in question
        assert 'options' in question
        
        # Check that brain_type is not exposed in options
        for option in question['options']:
            assert 'brain_type' not in option
            assert 'option_id' in option
            assert 'text' in option
    
    def test_get_quiz_questions_unauthorized(self, client):
        """Test getting quiz questions without authentication"""
        response = client.get('/quiz/questions')
        assert response.status_code == 401

class TestQuizSubmission:
    """Test quiz submission and brain type assessment"""
    
    def setup_quiz_questions(self, client, auth_headers):
        """Helper method to set up quiz questions"""
        questions = [
            {
                "text": "Question 1: Learning preference?",
                "options": [
                    {"text": "Visual", "brain_type": "Visual"},
                    {"text": "Audio", "brain_type": "Auditory"},
                    {"text": "Reading", "brain_type": "ReadWrite"},
                    {"text": "Hands-on", "brain_type": "Kinesthetic"}
                ]
            },
            {
                "text": "Question 2: Study method?",
                "options": [
                    {"text": "Charts", "brain_type": "Visual"},
                    {"text": "Lectures", "brain_type": "Auditory"},
                    {"text": "Books", "brain_type": "ReadWrite"},
                    {"text": "Labs", "brain_type": "Kinesthetic"}
                ]
            },
            {
                "text": "Question 3: Information retention?",
                "options": [
                    {"text": "Images", "brain_type": "Visual"},
                    {"text": "Spoken", "brain_type": "Auditory"},
                    {"text": "Written", "brain_type": "ReadWrite"},
                    {"text": "Practice", "brain_type": "Kinesthetic"}
                ]
            }
        ]
        
        question_ids = []
        for question in questions:
            response = client.post('/admin/quiz/questions', json=question, headers=auth_headers)
            data = response.get_json()
            question_ids.append(data['question_id'])
        
        return question_ids
    
    @patch('backend.routes.quiz.generate_user_roadmap')
    def test_submit_quiz_success(self, mock_roadmap, client, auth_headers):
        """Test successful quiz submission with roadmap generation"""
        # Mock roadmap generation
        mock_roadmap.return_value = {
            'roadmap_id': 'mock_roadmap_id',
            'steps': [{'step': 1}, {'step': 2}],
            'estimated_completion_weeks': 6,
            'daily_time_minutes': 60
        }
        
        # Set up quiz questions
        question_ids = self.setup_quiz_questions(client, auth_headers)
        
        # Submit quiz answers (all Visual responses)
        quiz_answers = {
            "answers": [
                {"question_id": question_ids[0], "selected_option": 0},  # Visual
                {"question_id": question_ids[1], "selected_option": 0},  # Visual
                {"question_id": question_ids[2], "selected_option": 0}   # Visual
            ],
            "preferences": {
                "topic": "Data Science",
                "duration": "intermediate",
                "intensity": "intermediate"
            }
        }
        
        response = client.post('/quiz/submit', json=quiz_answers, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'message' in data
        assert 'assessment_results' in data
        assert 'brain_type_description' in data
        assert 'roadmap' in data
        assert 'next_steps' in data
        
        # Check assessment results
        assessment = data['assessment_results']
        assert assessment['brain_type'] == 'Visual'
        assert assessment['confidence_score'] == 100.0  # All answers were Visual
        assert assessment['total_questions_answered'] == 3
        
        # Check roadmap info
        roadmap = data['roadmap']
        assert roadmap['roadmap_id'] == 'mock_roadmap_id'
        assert roadmap['topic'] == 'Data Science'
        
        # Verify roadmap generation was called
        mock_roadmap.assert_called_once()
    
    def test_submit_quiz_mixed_results(self, client, auth_headers):
        """Test quiz submission with mixed brain type results"""
        # Set up quiz questions
        question_ids = self.setup_quiz_questions(client, auth_headers)
        
        # Submit mixed answers
        quiz_answers = {
            "answers": [
                {"question_id": question_ids[0], "selected_option": 0},  # Visual
                {"question_id": question_ids[1], "selected_option": 1},  # Auditory
                {"question_id": question_ids[2], "selected_option": 0}   # Visual
            ],
            "preferences": {
                "topic": "Web Development"
            }
        }
        
        with patch('backend.routes.quiz.generate_user_roadmap') as mock_roadmap:
            mock_roadmap.return_value = {
                'roadmap_id': 'test_roadmap',
                'steps': [],
                'estimated_completion_weeks': 4,
                'daily_time_minutes': 45
            }
            
            response = client.post('/quiz/submit', json=quiz_answers, headers=auth_headers)
            assert response.status_code == 200
            
            data = response.get_json()
            assessment = data['assessment_results']
            
            # Visual should be dominant (2 out of 3)
            assert assessment['brain_type'] == 'Visual'
            assert assessment['confidence_score'] == 66.7  # 2/3 * 100
            
            # Check brain type distribution
            distribution = assessment['brain_type_distribution']
            assert distribution['Visual'] == 2
            assert distribution['Auditory'] == 1
    
    def test_submit_quiz_missing_answers(self, client, auth_headers):
        """Test quiz submission with missing answers"""
        response = client.post('/quiz/submit', json={}, headers=auth_headers)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Missing quiz answers' in data['error']
    
    def test_submit_quiz_invalid_question_id(self, client, auth_headers):
        """Test quiz submission with invalid question ID"""
        quiz_answers = {
            "answers": [
                {"question_id": "invalid_id", "selected_option": 0}
            ]
        }
        
        response = client.post('/quiz/submit', json=quiz_answers, headers=auth_headers)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid question_id' in data['error']
    
    def test_submit_quiz_invalid_option(self, client, auth_headers):
        """Test quiz submission with invalid option selection"""
        # Set up one question
        question_ids = self.setup_quiz_questions(client, auth_headers)
        
        quiz_answers = {
            "answers": [
                {"question_id": question_ids[0], "selected_option": 99}  # Invalid option
            ]
        }
        
        response = client.post('/quiz/submit', json=quiz_answers, headers=auth_headers)
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid option selection' in data['error']
    
    @patch('backend.routes.quiz.generate_user_roadmap')
    def test_submit_quiz_roadmap_generation_failure(self, mock_roadmap, client, auth_headers):
        """Test quiz submission when roadmap generation fails"""
        # Mock roadmap generation to fail
        mock_roadmap.side_effect = Exception("Roadmap generation error")
        
        # Set up quiz questions
        question_ids = self.setup_quiz_questions(client, auth_headers)
        
        quiz_answers = {
            "answers": [
                {"question_id": question_ids[0], "selected_option": 0}
            ]
        }
        
        response = client.post('/quiz/submit', json=quiz_answers, headers=auth_headers)
        assert response.status_code == 200  # Should still return assessment results
        
        data = response.get_json()
        assert 'assessment_results' in data
        assert data['assessment_results']['brain_type'] == 'Visual'
        
        # Check that roadmap error is included
        assert 'roadmap' in data
        assert data['roadmap']['roadmap_id'] is None
        assert 'generation_error' in data['roadmap']
    
    def test_submit_quiz_unauthorized(self, client):
        """Test quiz submission without authentication"""
        quiz_answers = {
            "answers": [
                {"question_id": "test", "selected_option": 0}
            ]
        }
        
        response = client.post('/quiz/submit', json=quiz_answers)
        assert response.status_code == 401

class TestBrainTypeDescriptions:
    """Test brain type description functionality"""
    
    def test_brain_type_descriptions_included(self, client, auth_headers):
        """Test that brain type descriptions are included in quiz results"""
        # Set up quiz questions
        question_ids = []
        question = {
            "text": "Test question",
            "options": [
                {"text": "Visual option", "brain_type": "Visual"},
                {"text": "Auditory option", "brain_type": "Auditory"},
                {"text": "ReadWrite option", "brain_type": "ReadWrite"},
                {"text": "Kinesthetic option", "brain_type": "Kinesthetic"}
            ]
        }
        
        response = client.post('/admin/quiz/questions', json=question, headers=auth_headers)
        question_id = response.get_json()['question_id']
        
        # Test each brain type
        brain_types = ['Visual', 'Auditory', 'ReadWrite', 'Kinesthetic']
        
        for i, expected_type in enumerate(brain_types):
            quiz_answers = {
                "answers": [
                    {"question_id": question_id, "selected_option": i}
                ]
            }
            
            with patch('backend.routes.quiz.generate_user_roadmap') as mock_roadmap:
                mock_roadmap.return_value = {
                    'roadmap_id': 'test',
                    'steps': [],
                    'estimated_completion_weeks': 4,
                    'daily_time_minutes': 30
                }
                
                response = client.post('/quiz/submit', json=quiz_answers, headers=auth_headers)
                assert response.status_code == 200
                
                data = response.get_json()
                assert data['assessment_results']['brain_type'] == expected_type
                
                # Check that description is included
                description = data['brain_type_description']
                assert 'description' in description
                assert 'learning_tips' in description
                assert 'strengths' in description
                assert isinstance(description['learning_tips'], list)
                assert isinstance(description['strengths'], list)