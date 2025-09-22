#!/usr/bin/env python3
"""
Generate test data for NeuroNav engagement analysis.

This script creates sample users, roadmaps, and progress data to demonstrate
the analysis functionality when real user data is limited.
"""

import sys
import os
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from bson import ObjectId

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import User, Roadmap, Progress

# Test data configuration
TEST_DATA_CONFIG = {
    'users': [
        {'name': 'Alice Johnson', 'email': 'alice@test.com', 'brain_type': 'Visual'},
        {'name': 'Bob Smith', 'email': 'bob@test.com', 'brain_type': 'Auditory'},
        {'name': 'Carol Davis', 'email': 'carol@test.com', 'brain_type': 'ReadWrite'},
        {'name': 'David Wilson', 'email': 'david@test.com', 'brain_type': 'Kinesthetic'},
        {'name': 'Eva Brown', 'email': 'eva@test.com', 'brain_type': 'Visual'},
    ],
    'roadmaps': [
        {
            'topic': 'Data Science Fundamentals',
            'steps': [
                {'title': 'Introduction to Data Science', 'resource_type': 'video', 'time': 45},
                {'title': 'Python for Data Analysis', 'resource_type': 'tutorial', 'time': 90},
                {'title': 'Data Visualization', 'resource_type': 'article', 'time': 60},
                {'title': 'Statistical Analysis', 'resource_type': 'course', 'time': 120},
            ]
        },
        {
            'topic': 'Web Development Basics',
            'steps': [
                {'title': 'HTML Fundamentals', 'resource_type': 'course', 'time': 60},
                {'title': 'CSS Styling', 'resource_type': 'video', 'time': 75},
                {'title': 'JavaScript Basics', 'resource_type': 'tutorial', 'time': 120},
                {'title': 'Responsive Design', 'resource_type': 'article', 'time': 45},
            ]
        },
        {
            'topic': 'Machine Learning Introduction',
            'steps': [
                {'title': 'ML Theory Overview', 'resource_type': 'article', 'time': 90},
                {'title': 'Linear Regression', 'resource_type': 'tutorial', 'time': 120},
                {'title': 'Model Evaluation', 'resource_type': 'video', 'time': 45},
                {'title': 'Practical Project', 'resource_type': 'exercise', 'time': 180},
            ]
        }
    ]
}

def generate_test_data():
    """Generate comprehensive test data for analysis."""
    
    print("🔧 Generating test data for NeuroNav analysis...")
    
    # Connect to MongoDB
    try:
        from config import MONGO_URI
        client = MongoClient(MONGO_URI)
        db = client.neuronav
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return
    
    # Clear existing test data (optional - be careful in production!)
    print("🗑️  Clearing existing test data...")
    db.users.delete_many({'email': {'$regex': '@test.com'}})
    
    # Create test users
    print("👥 Creating test users...")
    user_ids = []
    for user_data in TEST_DATA_CONFIG['users']:
        user_id = User.create_user(
            name=user_data['name'],
            email=user_data['email'],
            password='testpass123'
        )
        
        # Update brain type
        User.update_brain_type(str(user_id), user_data['brain_type'])
        user_ids.append(str(user_id))
        print(f"   • Created {user_data['name']} ({user_data['brain_type']})")
    
    # Create test roadmaps and progress
    print("🗺️  Creating test roadmaps and progress...")
    
    for i, user_id in enumerate(user_ids):
        user = User.find_by_id(user_id)
        brain_type = user['brain_type']
        
        # Each user gets 1-2 roadmaps
        num_roadmaps = random.randint(1, 2)
        selected_roadmaps = random.sample(TEST_DATA_CONFIG['roadmaps'], num_roadmaps)
        
        for roadmap_data in selected_roadmaps:
            # Create roadmap steps
            steps = []
            for j, step_data in enumerate(roadmap_data['steps']):
                # Determine if step is brain-type optimized
                brain_type_optimized = determine_optimization(brain_type, step_data['resource_type'])
                
                step = {
                    'step_number': j + 1,
                    'title': step_data['title'],
                    'description': f"Learn about {step_data['title'].lower()} through {step_data['resource_type']} content",
                    'resource_id': '',
                    'resource_url': f"https://example.com/{step_data['title'].lower().replace(' ', '-')}",
                    'resource_type': step_data['resource_type'],
                    'estimated_time_minutes': step_data['time'],
                    'tags': [roadmap_data['topic'].split()[0].lower()],
                    'brain_type_optimized': brain_type_optimized
                }
                steps.append(step)
            
            # Create roadmap
            roadmap_id = Roadmap.create_roadmap(
                user_id=user_id,
                topic=roadmap_data['topic'],
                brain_type=brain_type,
                steps=steps,
                estimated_completion_weeks=random.randint(4, 8),
                daily_time_minutes=random.randint(30, 90)
            )
            
            print(f"   • Created roadmap '{roadmap_data['topic']}' for {user['name']}")
            
            # Generate realistic progress data
            generate_progress_for_roadmap(user_id, str(roadmap_id), steps, brain_type)
    
    print("✅ Test data generation complete!")
    print(f"   • Created {len(user_ids)} users")
    print(f"   • Generated roadmaps and progress data")
    print("   • Ready for analysis!")

def determine_optimization(brain_type, resource_type):
    """Determine if a resource type is optimized for a brain type."""
    
    # Brain type preferences (from config)
    preferences = {
        'Visual': ['video', 'tutorial'],
        'Auditory': ['course', 'video'],
        'ReadWrite': ['article', 'book'],
        'Kinesthetic': ['tutorial', 'exercise']
    }
    
    return resource_type in preferences.get(brain_type, [])

def generate_progress_for_roadmap(user_id, roadmap_id, steps, brain_type):
    """Generate realistic progress data for a roadmap."""
    
    base_date = datetime.now() - timedelta(days=random.randint(1, 30))
    
    for i, step in enumerate(steps):
        step_number = step['step_number']
        
        # Calculate completion probability based on brain type matching
        is_optimized = step['brain_type_optimized']
        
        # Higher completion rate for optimized steps
        if is_optimized:
            completion_prob = 0.85  # 85% completion for matched resources
        else:
            completion_prob = 0.45  # 45% completion for non-matched resources
        
        # Add some randomness
        completion_prob += random.uniform(-0.1, 0.1)
        completion_prob = max(0.1, min(0.95, completion_prob))  # Clamp between 10-95%
        
        # Determine if step is completed
        completed = random.random() < completion_prob
        
        # Create progress record
        Progress.create_or_update_progress(
            user_id=user_id,
            roadmap_id=roadmap_id,
            step_number=step_number,
            completed=completed
        )
        
        # If completed, simulate realistic completion time
        if completed:
            # Simulate time spent (with some variation from estimated time)
            estimated_time = step['estimated_time_minutes']
            
            # Optimized resources tend to be completed faster
            if is_optimized:
                time_factor = random.uniform(0.8, 1.1)  # 80-110% of estimated time
            else:
                time_factor = random.uniform(1.0, 1.4)  # 100-140% of estimated time
            
            actual_time = estimated_time * time_factor
            
            # Update progress with completion time
            completed_at = base_date + timedelta(days=i, minutes=random.randint(0, 1440))
            
            # Update the progress record with completion time
            # (This would require updating the Progress model to handle completion times)

if __name__ == '__main__':
    generate_test_data()