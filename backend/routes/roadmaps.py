from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime

# Database connection
client = MongoClient('mongodb://localhost:27017/')
db = client['neuronav']
roadmaps_collection = db['roadmaps']
users_collection = db['users']
progress_collection = db['progress']

roadmaps_bp = Blueprint('roadmaps', __name__)

@roadmaps_bp.route('/roadmaps', methods=['GET'])
@jwt_required()
def get_user_roadmaps():
    """Get all roadmaps for the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get all roadmaps for this user
        roadmaps = list(roadmaps_collection.find({
            'user_id': ObjectId(user_id)
        }))
        
        # Convert ObjectId to string for JSON serialization
        for roadmap in roadmaps:
            roadmap['roadmap_id'] = str(roadmap['_id'])
            roadmap['user_id'] = str(roadmap['user_id'])
            
            # Remove MongoDB _id field from response
            del roadmap['_id']
            
            # Add progress information
            progress_records = list(progress_collection.find({
                'user_id': ObjectId(user_id),
                'roadmap_id': roadmap['_id']
            }))
            
            completed_steps = len([p for p in progress_records if p.get('completed', False)])
            total_steps = len(roadmap.get('steps', []))
            
            roadmap['progress'] = {
                'completed_steps': completed_steps,
                'total_steps': total_steps,
                'completion_percentage': (completed_steps / total_steps * 100) if total_steps > 0 else 0
            }
        
        return jsonify(roadmaps), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roadmaps_bp.route('/roadmaps/<roadmap_id>', methods=['GET'])
@jwt_required()
def get_roadmap(roadmap_id):
    """Get a specific roadmap by ID"""
    try:
        user_id = get_jwt_identity()
        
        # Get the roadmap
        roadmap = roadmaps_collection.find_one({
            '_id': ObjectId(roadmap_id),
            'user_id': ObjectId(user_id)
        })
        
        if not roadmap:
            return jsonify({'error': 'Roadmap not found'}), 404
        
        # Convert ObjectId to string and clean up response
        roadmap['roadmap_id'] = str(roadmap['_id'])
        roadmap['user_id'] = str(roadmap['user_id'])
        
        # Remove MongoDB _id field from response
        del roadmap['_id']
        
        # Get progress for each step
        progress_records = list(progress_collection.find({
            'user_id': ObjectId(user_id),
            'roadmap_id': ObjectId(roadmap_id)
        }))
        
        # Create a map of step progress
        progress_map = {str(p['step_id']): p for p in progress_records}
        
        # Add progress to each step
        for step in roadmap.get('steps', []):
            step_id = str(step.get('_id', step.get('id', '')))
            step['progress'] = progress_map.get(step_id, {
                'completed': False,
                'completion_date': None,
                'time_spent': 0
            })
        
        return jsonify(roadmap), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roadmaps_bp.route('/roadmaps/<roadmap_id>', methods=['PUT'])
@jwt_required()
def update_roadmap(roadmap_id):
    """Update a roadmap"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify ownership
        roadmap = roadmaps_collection.find_one({
            '_id': ObjectId(roadmap_id),
            'user_id': ObjectId(user_id)
        })
        
        if not roadmap:
            return jsonify({'error': 'Roadmap not found'}), 404
        
        # Update roadmap
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        # Only update allowed fields
        allowed_fields = ['title', 'description', 'difficulty', 'estimated_duration']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        roadmaps_collection.update_one(
            {'_id': ObjectId(roadmap_id)},
            {'$set': update_data}
        )
        
        # Return updated roadmap
        updated_roadmap = roadmaps_collection.find_one({'_id': ObjectId(roadmap_id)})
        updated_roadmap['_id'] = str(updated_roadmap['_id'])
        updated_roadmap['user_id'] = str(updated_roadmap['user_id'])
        
        return jsonify(updated_roadmap), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roadmaps_bp.route('/roadmaps/<roadmap_id>', methods=['DELETE'])
@jwt_required()
def delete_roadmap(roadmap_id):
    """Delete a roadmap"""
    try:
        user_id = get_jwt_identity()
        
        # Verify ownership and delete
        result = roadmaps_collection.delete_one({
            '_id': ObjectId(roadmap_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Roadmap not found'}), 404
        
        # Also delete associated progress records
        progress_collection.delete_many({
            'user_id': ObjectId(user_id),
            'roadmap_id': ObjectId(roadmap_id)
        })
        
        return jsonify({'message': 'Roadmap deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roadmaps_bp.route('/roadmaps/<roadmap_id>/steps', methods=['POST'])
@jwt_required()
def add_step(roadmap_id):
    """Add a new step to a roadmap"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify ownership
        roadmap = roadmaps_collection.find_one({
            '_id': ObjectId(roadmap_id),
            'user_id': ObjectId(user_id)
        })
        
        if not roadmap:
            return jsonify({'error': 'Roadmap not found'}), 404
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get current steps
        current_steps = roadmap.get('steps', [])
        
        # Create new step
        new_step = {
            'step_number': len(current_steps) + 1,
            'title': data['title'],
            'description': data['description'],
            'resource_type': data.get('resource_type', 'tutorial'),
            'resource_url': data.get('resource_url', ''),
            'estimated_time_minutes': data.get('estimated_time_minutes', 60),
            'tags': data.get('tags', []),
            'brain_type_optimized': True
        }
        
        # Add the new step
        current_steps.append(new_step)
        
        # Update roadmap
        roadmaps_collection.update_one(
            {'_id': ObjectId(roadmap_id)},
            {
                '$set': {
                    'steps': current_steps,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'message': 'Step added successfully',
            'step': new_step
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roadmaps_bp.route('/roadmaps/<roadmap_id>/steps/<int:step_number>', methods=['DELETE'])
@jwt_required()
def delete_step(roadmap_id, step_number):
    """Delete a step from a roadmap"""
    try:
        user_id = get_jwt_identity()
        
        # Verify ownership
        roadmap = roadmaps_collection.find_one({
            '_id': ObjectId(roadmap_id),
            'user_id': ObjectId(user_id)
        })
        
        if not roadmap:
            return jsonify({'error': 'Roadmap not found'}), 404
        
        # Get current steps
        current_steps = roadmap.get('steps', [])
        
        # Find and remove the step
        updated_steps = [step for step in current_steps if step.get('step_number') != step_number]
        
        if len(updated_steps) == len(current_steps):
            return jsonify({'error': 'Step not found'}), 404
        
        # Renumber remaining steps
        for i, step in enumerate(updated_steps):
            step['step_number'] = i + 1
        
        # Update roadmap
        roadmaps_collection.update_one(
            {'_id': ObjectId(roadmap_id)},
            {
                '$set': {
                    'steps': updated_steps,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Also delete any progress records for this step and renumber
        progress_collection.delete_many({
            'user_id': ObjectId(user_id),
            'roadmap_id': ObjectId(roadmap_id),
            'step_number': step_number
        })
        
        # Update step numbers in remaining progress records
        progress_records = list(progress_collection.find({
            'user_id': ObjectId(user_id),
            'roadmap_id': ObjectId(roadmap_id),
            'step_number': {'$gt': step_number}
        }))
        
        for progress in progress_records:
            progress_collection.update_one(
                {'_id': progress['_id']},
                {'$set': {'step_number': progress['step_number'] - 1}}
            )
        
        return jsonify({'message': 'Step deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
