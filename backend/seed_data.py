#!/usr/bin/env python3
"""
NeuroNav Database Seeding Script
Seeds the database with initial quiz questions and learning resources
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import create_app

def seed_quiz_questions(db):
    """Seed quiz questions for VARK learning style assessment"""
    
    quiz_questions = [
        {
            "text": "When learning something new, I prefer to:",
            "options": [
                {"text": "Watch demonstrations or videos", "brain_type": "Visual"},
                {"text": "Listen to explanations or lectures", "brain_type": "Auditory"},
                {"text": "Read detailed instructions or articles", "brain_type": "ReadWrite"},
                {"text": "Try it out hands-on immediately", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "When studying for an exam, I find it most helpful to:",
            "options": [
                {"text": "Create colorful diagrams and mind maps", "brain_type": "Visual"},
                {"text": "Record myself reading notes and listen back", "brain_type": "Auditory"},
                {"text": "Write detailed summaries and flashcards", "brain_type": "ReadWrite"},
                {"text": "Practice with real examples and exercises", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "I remember information best when it's presented as:",
            "options": [
                {"text": "Charts, graphs, or infographics", "brain_type": "Visual"},
                {"text": "Spoken explanations or discussions", "brain_type": "Auditory"},
                {"text": "Written text or bullet points", "brain_type": "ReadWrite"},
                {"text": "Interactive activities or simulations", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "When giving directions, I typically:",
            "options": [
                {"text": "Draw a map or show pictures", "brain_type": "Visual"},
                {"text": "Explain verbally with landmarks", "brain_type": "Auditory"},
                {"text": "Write down step-by-step instructions", "brain_type": "ReadWrite"},
                {"text": "Walk through the route together", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "My ideal learning environment includes:",
            "options": [
                {"text": "Visual aids and bright, organized spaces", "brain_type": "Visual"},
                {"text": "Background music or discussion groups", "brain_type": "Auditory"},
                {"text": "Quiet spaces with books and notes", "brain_type": "ReadWrite"},
                {"text": "Flexible seating and hands-on materials", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "When solving a complex problem, I prefer to:",
            "options": [
                {"text": "Visualize the solution with diagrams", "brain_type": "Visual"},
                {"text": "Talk through it with others", "brain_type": "Auditory"},
                {"text": "Research and read about similar problems", "brain_type": "ReadWrite"},
                {"text": "Experiment with different approaches", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "I learn programming concepts best through:",
            "options": [
                {"text": "Code visualization tools and flowcharts", "brain_type": "Visual"},
                {"text": "Pair programming and code reviews", "brain_type": "Auditory"},
                {"text": "Reading documentation and tutorials", "brain_type": "ReadWrite"},
                {"text": "Building projects and debugging code", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "When attending a workshop, I prefer:",
            "options": [
                {"text": "Slide presentations with visual examples", "brain_type": "Visual"},
                {"text": "Interactive discussions and Q&A sessions", "brain_type": "Auditory"},
                {"text": "Detailed handouts and reference materials", "brain_type": "ReadWrite"},
                {"text": "Hands-on labs and practical exercises", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "My note-taking style typically involves:",
            "options": [
                {"text": "Colorful highlights, diagrams, and sketches", "brain_type": "Visual"},
                {"text": "Recording lectures or discussing with peers", "brain_type": "Auditory"},
                {"text": "Detailed written notes and outlines", "brain_type": "ReadWrite"},
                {"text": "Quick notes while doing practical work", "brain_type": "Kinesthetic"}
            ]
        },
        {
            "text": "When learning a new technology, I start by:",
            "options": [
                {"text": "Watching tutorial videos or demos", "brain_type": "Visual"},
                {"text": "Listening to podcasts or tech talks", "brain_type": "Auditory"},
                {"text": "Reading official documentation", "brain_type": "ReadWrite"},
                {"text": "Installing it and experimenting immediately", "brain_type": "Kinesthetic"}
            ]
        }
    ]
    
    print("🔄 Seeding quiz questions...")
    
    # Clear existing questions
    db.quiz_questions.delete_many({})
    
    # Insert new questions
    for q_data in quiz_questions:
        question_doc = {
            "text": q_data["text"],
            "options": q_data["options"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db.quiz_questions.insert_one(question_doc)
    
    print(f"✅ Added {len(quiz_questions)} quiz questions")

def seed_resources(db):
    """Seed learning resources for various topics"""
    
    resources = [
        # Data Science Resources
        {
            "title": "Python for Data Science Handbook",
            "url": "https://jakevdp.github.io/PythonDataScienceHandbook/",
            "type": "article",
            "tags": ["Data Science", "Python", "Pandas", "NumPy"],
            "est_time": 480  # 8 hours
        },
        {
            "title": "Kaggle Learn: Data Science Micro-Courses",
            "url": "https://www.kaggle.com/learn",
            "type": "course",
            "tags": ["Data Science", "Machine Learning", "Python"],
            "est_time": 300  # 5 hours
        },
        {
            "title": "StatQuest with Josh Starmer",
            "url": "https://www.youtube.com/c/joshstarmer",
            "type": "video",
            "tags": ["Data Science", "Statistics", "Machine Learning"],
            "est_time": 600  # 10 hours of content
        },
        {
            "title": "Hands-On Machine Learning (2nd Edition)",
            "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/",
            "type": "book",
            "tags": ["Machine Learning", "Python", "Scikit-learn", "TensorFlow"],
            "est_time": 1200  # 20 hours
        },
        {
            "title": "Data Science Cheat Sheets",
            "url": "https://www.datacamp.com/cheat-sheet",
            "type": "reference",
            "tags": ["Data Science", "Python", "R", "SQL"],
            "est_time": 30  # 30 minutes
        },
        
        # Web Development Resources
        {
            "title": "MDN Web Docs - JavaScript Guide",
            "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            "type": "documentation",
            "tags": ["Web Development", "JavaScript", "Frontend"],
            "est_time": 360  # 6 hours
        },
        {
            "title": "React Official Tutorial",
            "url": "https://react.dev/learn",
            "type": "tutorial",
            "tags": ["Web Development", "React", "Frontend", "JavaScript"],
            "est_time": 240  # 4 hours
        },
        {
            "title": "The Odin Project - Full Stack JavaScript",
            "url": "https://www.theodinproject.com/paths/full-stack-javascript",
            "type": "course",
            "tags": ["Web Development", "JavaScript", "Full Stack", "Node.js"],
            "est_time": 2400  # 40 hours
        },
        {
            "title": "CSS-Tricks - A Complete Guide to Flexbox",
            "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
            "type": "article",
            "tags": ["Web Development", "CSS", "Frontend", "Layout"],
            "est_time": 60  # 1 hour
        },
        {
            "title": "Traversy Media - Web Development Crash Courses",
            "url": "https://www.youtube.com/c/TraversyMedia",
            "type": "video",
            "tags": ["Web Development", "JavaScript", "Python", "PHP"],
            "est_time": 720  # 12 hours of content
        },
        
        # Machine Learning Resources
        {
            "title": "Andrew Ng's Machine Learning Course",
            "url": "https://www.coursera.org/learn/machine-learning",
            "type": "course",
            "tags": ["Machine Learning", "Mathematics", "Algorithms"],
            "est_time": 660  # 11 weeks * 1 hour
        },
        {
            "title": "Fast.ai Practical Deep Learning",
            "url": "https://course.fast.ai/",
            "type": "course",
            "tags": ["Machine Learning", "Deep Learning", "Python", "PyTorch"],
            "est_time": 840  # 14 hours
        },
        {
            "title": "Scikit-learn User Guide",
            "url": "https://scikit-learn.org/stable/user_guide.html",
            "type": "documentation",
            "tags": ["Machine Learning", "Python", "Scikit-learn"],
            "est_time": 300  # 5 hours
        },
        {
            "title": "3Blue1Brown - Neural Networks Series",
            "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi",
            "type": "video",
            "tags": ["Machine Learning", "Deep Learning", "Neural Networks", "Mathematics"],
            "est_time": 180  # 3 hours
        },
        {
            "title": "Papers With Code - Latest ML Research",
            "url": "https://paperswithcode.com/",
            "type": "reference",
            "tags": ["Machine Learning", "Research", "Deep Learning", "AI"],
            "est_time": 120  # 2 hours browsing
        }
    ]
    
    print("🔄 Seeding learning resources...")
    
    # Clear existing resources
    db.resources.delete_many({})
    
    # Insert new resources
    for r_data in resources:
        resource_doc = {
            "title": r_data["title"],
            "url": r_data["url"],
            "resource_type": r_data["type"],
            "tags": r_data["tags"],
            "est_time": r_data["est_time"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db.resources.insert_one(resource_doc)
    
    print(f"✅ Added {len(resources)} learning resources")

def main():
    """Main seeding function"""
    print("🚀 Starting NeuroNav database seeding...")
    
    try:
        # Create app and get database connection
        app, _ = create_app()
        
        with app.app_context():
            db = app.db
            if db is None:
                print("❌ Failed to connect to database")
                return False
            
            print("✅ Connected to MongoDB successfully")
            
            # Seed data
            seed_quiz_questions(db)
            seed_resources(db)
            
            print("🎉 Database seeding completed successfully!")
            
            # Print summary
            question_count = db.quiz_questions.count_documents({})
            resource_count = db.resources.count_documents({})
            
            print(f"\n📈 Database Summary:")
            print(f"   Quiz Questions: {question_count}")
            print(f"   Learning Resources: {resource_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)