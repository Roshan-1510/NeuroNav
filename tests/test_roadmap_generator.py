import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from roadmap_generator import RoadmapGenerator, generate_user_roadmap

class TestRoadmapGenerator:
    """Test roadmap generation functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.sample_resources = [
            {
                "_id": "resource1",
                "title": "Python Tutorial Video",
                "url": "https://example.com/python-video",
                "type": "video",
                "tags": ["Python", "Programming"],
                "est_time": 120
            },
            {
                "_id": "resource2",
                "title": "Data Science Article",
                "url": "https://example.com/ds-article",
                "type": "article",
                "tags": ["Data Science", "Analytics"],
                "est_time": 45
            },
            {
                "_id": "resource3",
                "title": "Hands-on Python Project",
                "url": "https://example.com/python-project",
                "type": "tutorial",
                "tags": ["Python", "Project"],
                "est_time": 180
            },
            {
                "_id": "resource4",
                "title": "Machine Learning Course",
                "url": "https://example.com/ml-course",
                "type": "course",
                "tags": ["Machine Learning", "AI"],
                "est_time": 600
            }
        ]
    
    @patch('roadmap_generator.get_db')
    def test_roadmap_generator_initialization(self, mock_get_db):
        """Test RoadmapGenerator initialization"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        generator = RoadmapGenerator()
        assert generator.db == mock_db
    
    @patch('roadmap_generator.get_db')
    def test_get_topic_resources(self, mock_get_db):
        """Test getting resources for a specific topic"""
        mock_db = MagicMock()
        mock_db.resources.find.return_value = self.sample_resources[:2]  # Return first 2 resources
        mock_get_db.return_value = mock_db
        
        generator = RoadmapGenerator()
        resources = generator._get_topic_resources("Python")
        
        assert len(resources) == 2
        mock_db.resources.find.assert_called_once_with({
            "tags": {"$regex": "Python", "$options": "i"}
        })
    
    @patch('roadmap_generator.get_db')
    def test_get_general_resources(self, mock_get_db):
        """Test getting general resources as fallback"""
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = self.sample_resources
        mock_db.resources.find.return_value = mock_cursor
        mock_get_db.return_value = mock_db
        
        generator = RoadmapGenerator()
        resources = generator._get_general_resources()
        
        assert len(resources) == 4
        mock_db.resources.find.assert_called_once()
        mock_cursor.limit.assert_called_once_with(10)
    
    def test_rank_resources_by_brain_type_visual(self):
        """Test ranking resources for Visual brain type"""
        generator = RoadmapGenerator()
        
        # Mock database connection
        generator.db = MagicMock()
        
        ranked_resources = generator._rank_resources_by_brain_type(
            self.sample_resources.copy(), "Visual"
        )
        
        # Video should be ranked highest for Visual learners
        assert ranked_resources[0]["type"] == "video"
        assert ranked_resources[0]["brain_type_score"] == 0.4  # Video weight for Visual
        
        # Check that all resources have scores
        for resource in ranked_resources:
            assert "brain_type_score" in resource
    
    def test_rank_resources_by_brain_type_kinesthetic(self):
        """Test ranking resources for Kinesthetic brain type"""
        generator = RoadmapGenerator()
        generator.db = MagicMock()
        
        ranked_resources = generator._rank_resources_by_brain_type(
            self.sample_resources.copy(), "Kinesthetic"
        )
        
        # Tutorial should be ranked highest for Kinesthetic learners
        tutorial_resources = [r for r in ranked_resources if r["type"] == "tutorial"]
        assert len(tutorial_resources) > 0
        assert tutorial_resources[0]["brain_type_score"] == 0.4  # Tutorial weight for Kinesthetic
    
    def test_rank_resources_invalid_brain_type(self):
        """Test ranking resources with invalid brain type"""
        generator = RoadmapGenerator()
        generator.db = MagicMock()
        
        # Should return resources unchanged if brain type is invalid
        ranked_resources = generator._rank_resources_by_brain_type(
            self.sample_resources.copy(), "InvalidType"
        )
        
        assert len(ranked_resources) == len(self.sample_resources)
        # Should not have brain_type_score added
        for resource in ranked_resources:
            assert "brain_type_score" not in resource
    
    def test_generate_learning_steps_beginner(self):
        """Test generating learning steps for beginner intensity"""
        generator = RoadmapGenerator()
        generator.db = MagicMock()
        
        steps = generator._generate_learning_steps(
            self.sample_resources.copy(), "Visual", "beginner"
        )
        
        assert len(steps) <= 6  # Beginner max steps
        
        # Check step structure
        for i, step in enumerate(steps):
            assert step["step_number"] == i + 1
            assert "title" in step
            assert "description" in step
            assert "resource_id" in step
            assert "resource_url" in step
            assert "estimated_time_minutes" in step
            assert step["brain_type_optimized"] is True
    
    def test_generate_learning_steps_advanced(self):
        """Test generating learning steps for advanced intensity"""
        generator = RoadmapGenerator()
        generator.db = MagicMock()
        
        steps = generator._generate_learning_steps(
            self.sample_resources.copy(), "Kinesthetic", "advanced"
        )
        
        assert len(steps) <= 10  # Advanced max steps
        assert len(steps) == min(10, len(self.sample_resources))
    
    def test_generate_step_description_visual(self):
        """Test generating step descriptions for Visual learners"""
        generator = RoadmapGenerator()
        generator.db = MagicMock()
        
        resource = {
            "title": "Python Video Tutorial",
            "type": "video"
        }
        
        description = generator._generate_step_description(resource, "Visual")
        
        assert "Python Video Tutorial" in description
        assert "visual" in description.lower() or "watch" in description.lower()
    
    def test_generate_step_description_kinesthetic(self):
        """Test generating step descriptions for Kinesthetic learners"""
        generator = RoadmapGenerator()
        generator.db = MagicMock()
        
        resource = {
            "title": "Hands-on Project",
            "type": "tutorial"
        }
        
        description = generator._generate_step_description(resource, "Kinesthetic")
        
        assert "Hands-on Project" in description
        assert "hands-on" in description.lower() or "practice" in description.lower()
    
    @patch('roadmap_generator.get_db')
    def test_generate_roadmap_success(self, mock_get_db):
        """Test successful roadmap generation"""
        # Mock database
        mock_db = MagicMock()
        mock_db.resources.find.return_value = self.sample_resources
        mock_db.roadmaps.insert_one.return_value = MagicMock(inserted_id="roadmap123")
        mock_get_db.return_value = mock_db
        
        generator = RoadmapGenerator()
        
        roadmap = generator.generate_roadmap(
            user_id="user123",
            topic="Python Programming",
            brain_type="Visual",
            duration="intermediate",
            intensity="intermediate"
        )
        
        assert roadmap["user_id"] == "user123"
        assert roadmap["topic"] == "Python Programming"
        assert roadmap["brain_type"] == "Visual"
        assert roadmap["roadmap_id"] == "roadmap123"
        assert "steps" in roadmap
        assert "estimated_completion_weeks" in roadmap
        assert "daily_time_minutes" in roadmap
        
        # Check that roadmap was saved to database
        mock_db.roadmaps.insert_one.assert_called_once()
    
    @patch('roadmap_generator.get_db')
    def test_generate_roadmap_no_topic_resources(self, mock_get_db):
        """Test roadmap generation when no topic-specific resources found"""
        # Mock database - no topic resources, but general resources available
        mock_db = MagicMock()
        mock_db.resources.find.side_effect = [
            [],  # No topic-specific resources
            self.sample_resources  # General resources
        ]
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = self.sample_resources
        mock_db.resources.find.return_value = mock_cursor
        mock_db.roadmaps.insert_one.return_value = MagicMock(inserted_id="roadmap456")
        mock_get_db.return_value = mock_db
        
        generator = RoadmapGenerator()
        
        roadmap = generator.generate_roadmap(
            user_id="user123",
            topic="Obscure Topic",
            brain_type="Auditory"
        )
        
        assert roadmap["topic"] == "Obscure Topic"
        assert len(roadmap["steps"]) > 0  # Should have steps from general resources
    
    @patch('roadmap_generator.get_db')
    def test_generate_roadmap_database_error(self, mock_get_db):
        """Test roadmap generation with database error"""
        mock_get_db.return_value = None  # Simulate database connection failure
        
        generator = RoadmapGenerator()
        
        with pytest.raises(Exception) as exc_info:
            generator.generate_roadmap(
                user_id="user123",
                topic="Test Topic",
                brain_type="Visual"
            )
        
        assert "Roadmap generation failed" in str(exc_info.value)

class TestRoadmapGeneratorIntensityMapping:
    """Test intensity and duration mappings"""
    
    def test_intensity_time_mapping(self):
        """Test that intensity mappings are correct"""
        generator = RoadmapGenerator()
        
        # Check beginner mapping
        beginner = generator.INTENSITY_TIME_MAPPING["beginner"]
        assert beginner["daily"] == 30
        assert beginner["total_weeks"] == 8
        
        # Check intermediate mapping
        intermediate = generator.INTENSITY_TIME_MAPPING["intermediate"]
        assert intermediate["daily"] == 60
        assert intermediate["total_weeks"] == 6
        
        # Check advanced mapping
        advanced = generator.INTENSITY_TIME_MAPPING["advanced"]
        assert advanced["daily"] == 90
        assert advanced["total_weeks"] == 4
    
    def test_brain_type_preferences(self):
        """Test that brain type preferences are correctly defined"""
        generator = RoadmapGenerator()
        
        # Check that all brain types have preferences
        expected_types = ["Visual", "Auditory", "ReadWrite", "Kinesthetic"]
        for brain_type in expected_types:
            assert brain_type in generator.BRAIN_TYPE_PREFERENCES
            
            prefs = generator.BRAIN_TYPE_PREFERENCES[brain_type]
            assert "preferred_types" in prefs
            assert "weights" in prefs
            assert isinstance(prefs["preferred_types"], list)
            assert isinstance(prefs["weights"], dict)
            
            # Check that weights sum to approximately 1.0
            total_weight = sum(prefs["weights"].values())
            assert abs(total_weight - 1.0) < 0.1  # Allow small floating point differences

class TestConvenienceFunction:
    """Test the convenience function for roadmap generation"""
    
    @patch('roadmap_generator.RoadmapGenerator')
    def test_generate_user_roadmap_function(self, mock_generator_class):
        """Test the generate_user_roadmap convenience function"""
        # Mock the generator instance
        mock_generator = MagicMock()
        mock_generator.generate_roadmap.return_value = {"roadmap_id": "test123"}
        mock_generator_class.return_value = mock_generator
        
        result = generate_user_roadmap(
            user_id="user123",
            topic="Test Topic",
            brain_type="Visual",
            duration="intermediate",
            intensity="advanced"
        )
        
        assert result == {"roadmap_id": "test123"}
        
        # Verify that generator was called with correct parameters
        mock_generator.generate_roadmap.assert_called_once_with(
            "user123", "Test Topic", "Visual", "intermediate", "advanced"
        )