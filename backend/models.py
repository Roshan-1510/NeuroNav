from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
import os

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
client = MongoClient(mongo_uri)
db = client.get_database()

# Collection references
users_collection = db.users
quiz_questions_collection = db.quiz_questions
resources_collection = db.resources
roadmaps_collection = db.roadmaps
progress_collection = db.progress

class User:
    @staticmethod
    def create_user(name, email, password_hash, brain_type=None):
        user = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "brain_type": brain_type,
            "created_at": datetime.utcnow()
        }
        result = users_collection.insert_one(user)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_by_email(email):
        return users_collection.find_one({"email": email})
    
    @staticmethod
    def get_user_by_id(user_id):
        return users_collection.find_one({"_id": ObjectId(user_id)})
    
    @staticmethod
    def update_user(user_id, update_data):
        return users_collection.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )

class QuizQuestion:
    @staticmethod
    def get_all_questions():
        questions = list(quiz_questions_collection.find())
        for q in questions:
            q['_id'] = str(q['_id'])
        return questions
    
    @staticmethod
    def create_question(text, options):
        question = {
            "text": text,
            "options": options,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = quiz_questions_collection.insert_one(question)
        return str(result.inserted_id)

class Resource:
    @staticmethod
    def get_all_resources():
        resources = list(resources_collection.find())
        for r in resources:
            r['_id'] = str(r['_id'])
        return resources
    
    @staticmethod
    def get_resources_by_tags(tags):
        if not tags:
            return []
        return list(resources_collection.find({"tags": {"$in": tags}}))

class Roadmap:
    @staticmethod
    def create_roadmap(user_id, topic, brain_type, steps, estimated_completion_weeks=4, daily_time_minutes=30):
        roadmap = {
            "user_id": user_id,
            "topic": topic,
            "brain_type": brain_type,
            "steps": steps,
            "estimated_completion_weeks": estimated_completion_weeks,
            "daily_time_minutes": daily_time_minutes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = roadmaps_collection.insert_one(roadmap)
        return str(result.inserted_id)
    
    @staticmethod
    def get_roadmap_by_id(roadmap_id):
        return roadmaps_collection.find_one({"_id": ObjectId(roadmap_id)})
    
    @staticmethod
    def get_user_roadmaps(user_id):
        return list(roadmaps_collection.find({"user_id": user_id}))
    
    @staticmethod
    def update_roadmap(roadmap_id, update_data):
        return roadmaps_collection.update_one(
            {"_id": ObjectId(roadmap_id)},
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
    
    @staticmethod
    def delete_roadmap(roadmap_id):
        return roadmaps_collection.delete_one({"_id": ObjectId(roadmap_id)})

class Progress:
    @staticmethod
    def update_step_progress(user_id, roadmap_id, step_number, completed):
        progress = {
            "user_id": user_id,
            "roadmap_id": roadmap_id,
            "step_number": step_number,
            "completed": completed,
            "completed_at": datetime.utcnow() if completed else None,
            "updated_at": datetime.utcnow()
        }
        return progress_collection.update_one(
            {"user_id": user_id, "roadmap_id": roadmap_id, "step_number": step_number},
            {"$set": progress},
            upsert=True
        )
    
    @staticmethod
    def get_roadmap_progress(user_id, roadmap_id):
        return list(progress_collection.find({
            "user_id": user_id,
            "roadmap_id": roadmap_id
        }))
    
    @staticmethod
    def get_user_progress_summary(user_id):
        # Get all user's roadmaps with progress
        roadmaps = list(roadmaps_collection.find({"user_id": user_id}))
        roadmap_summaries = []
        
        total_steps = 0
        completed_steps = 0
        
        for roadmap in roadmaps:
            roadmap_id = str(roadmap['_id'])
            progress_records = list(progress_collection.find({
                "user_id": user_id,
                "roadmap_id": roadmap_id
            }))
            
            roadmap_total_steps = len(roadmap.get('steps', []))
            roadmap_completed_steps = sum(1 for p in progress_records if p.get('completed', False))
            completion_percentage = (roadmap_completed_steps / roadmap_total_steps) * 100 if roadmap_total_steps > 0 else 0
            
            # Get last activity
            last_activity = roadmap.get('updated_at', roadmap.get('created_at', datetime.utcnow()))
            if progress_records:
                latest_progress = max(progress_records, key=lambda x: x.get('updated_at', datetime.min))
                last_activity = latest_progress.get('updated_at', last_activity)
            
            roadmap_summaries.append({
                "roadmap_id": roadmap_id,
                "roadmap_title": roadmap.get('topic', 'Untitled Roadmap'),
                "brain_type": roadmap.get('brain_type', 'Unknown'),
                "total_steps": roadmap_total_steps,
                "completed_steps": roadmap_completed_steps,
                "completion_percentage": round(completion_percentage, 1),
                "last_activity": last_activity.isoformat() if isinstance(last_activity, datetime) else str(last_activity),
                "created_at": roadmap.get('created_at', datetime.utcnow()).isoformat()
            })
            
            total_steps += roadmap_total_steps
            completed_steps += roadmap_completed_steps
        
        overall_completion_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        
        return {
            "user_id": user_id,
            "roadmaps": roadmap_summaries,
            "overall_summary": {
                "total_roadmaps": len(roadmaps),
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "overall_completion_percentage": round(overall_completion_percentage, 1)
            }
        }

# Legacy model functions for backward compatibility
def user_model():
    return {
        "_id": ObjectId(),
        "name": "",
        "email": "",
        "password_hash": "",
        "brain_type": None,
        "created_at": datetime.utcnow()
    }

def quiz_question_model():
    return {
        "_id": ObjectId(),
        "text": "",
        "options": [],  # [{"text": str, "brain_type": str}]
        "updated_at": datetime.utcnow()
    }

def resource_model():
    return {
        "_id": ObjectId(),
        "title": "",
        "url": "",
        "type": "",
        "tags": [],
        "est_time": 0
    }

def roadmap_model():
    return {
        "_id": ObjectId(),
        "user_id": ObjectId(),
        "topic": "",
        "brain_type": "",
        "steps": [],
        "created_at": datetime.utcnow()
    }

def progress_model():
    return {
        "_id": ObjectId(),
        "user_id": ObjectId(),
        "roadmap_id": ObjectId(),
        "step_id": ObjectId(),
        "status": "",
        "timestamp": datetime.utcnow()
    }
