from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from pymongo import MongoClient
import os
from datetime import datetime

progress_bp = Blueprint('progress', __name__)

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
client = MongoClient(mongo_uri)
db = client.get_database()

@progress_bp.route('/roadmaps/<roadmap_id>/progress', methods=['POST'])
@jwt_required()
def update_step_progress(roadmap_id):
    """Update progress for a specific roadmap step"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'step_number' not in data or 'completed' not in data:
            return jsonify({'error': 'step_number and completed fields are required'}), 400
        
        step_number = data['step_number']
        completed = data['completed']
        
        # Verify roadmap belongs to user
        roadmap = db.roadmaps.find_one({'_id': ObjectId(roadmap_id), 'user_id': ObjectId(user_id)})
        if not roadmap:
            return jsonify({'error': 'Roadmap not found or access denied'}), 404
        
        # Update or create progress entry
        progress_entry = {
            'user_id': user_id,
            'roadmap_id': roadmap_id,
            'step_number': step_number,
            'completed': completed,
            'completed_at': datetime.utcnow() if completed else None,
            'updated_at': datetime.utcnow()
        }
        
        # Upsert progress record
        db.progress.update_one(
            {
                'user_id': user_id,
                'roadmap_id': roadmap_id,
                'step_number': step_number
            },
            {'$set': progress_entry},
            upsert=True
        )
        
        return jsonify({
            'message': 'Progress updated successfully',
            'step_number': step_number,
            'completed': completed
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/roadmaps/<roadmap_id>/progress', methods=['GET'])
@jwt_required()
def get_roadmap_progress(roadmap_id):
    """Get progress for a specific roadmap"""
    try:
        user_id = get_jwt_identity()
        
        # Verify roadmap belongs to user
        roadmap = db.roadmaps.find_one({'_id': ObjectId(roadmap_id), 'user_id': ObjectId(user_id)})
        if not roadmap:
            return jsonify({'error': 'Roadmap not found or access denied'}), 404
        
        # Get progress records
        progress_records = list(db.progress.find({
            'user_id': user_id,
            'roadmap_id': roadmap_id
        }))
        
        # Format progress data
        progress_data = []
        for record in progress_records:
            progress_data.append({
                'step_number': record['step_number'],
                'completed': record['completed'],
                'completed_at': record.get('completed_at'),
                'updated_at': record.get('updated_at')
            })
        
        return jsonify(progress_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/progress/summary', methods=['GET'])
@jwt_required()
def get_user_progress_summary():
    """Get overall progress summary for the user"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's roadmaps - convert user_id to ObjectId for query
        roadmaps = list(db.roadmaps.find({'user_id': ObjectId(user_id)}))
        
        roadmap_summaries = []
        total_steps = 0
        total_completed = 0
        
        for roadmap in roadmaps:
            roadmap_id = str(roadmap['_id'])
            
            # Get progress for this roadmap
            progress_records = list(db.progress.find({
                'user_id': user_id,
                'roadmap_id': roadmap_id
            }))
            
            # Calculate completion stats
            roadmap_total_steps = len(roadmap.get('steps', []))
            roadmap_completed_steps = sum(1 for p in progress_records if p.get('completed', False))
            completion_percentage = (roadmap_completed_steps / roadmap_total_steps) * 100 if roadmap_total_steps > 0 else 0
            
            # Get last activity
            last_activity = None
            if progress_records:
                last_activity = max(p.get('updated_at') or p.get('completed_at') for p in progress_records if p.get('updated_at') or p.get('completed_at'))
            
            roadmap_summary = {
                'roadmap_id': roadmap_id,
                'roadmap_title': roadmap.get('topic', 'Untitled'),
                'brain_type': roadmap.get('brain_type', ''),
                'total_steps': roadmap_total_steps,
                'completed_steps': roadmap_completed_steps,
                'completion_percentage': round(completion_percentage, 1),
                'last_activity': last_activity.isoformat() if last_activity else None,
                'created_at': roadmap.get('created_at').isoformat() if roadmap.get('created_at') else None
            }
            
            roadmap_summaries.append(roadmap_summary)
            total_steps += roadmap_total_steps
            total_completed += roadmap_completed_steps
        
        overall_completion = (total_completed / total_steps) * 100 if total_steps > 0 else 0
        
        return jsonify({
            'user_id': user_id,
            'roadmaps': roadmap_summaries,
            'overall_summary': {
                'total_roadmaps': len(roadmaps),
                'total_steps': total_steps,
                'completed_steps': total_completed,
                'overall_completion_percentage': round(overall_completion, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
