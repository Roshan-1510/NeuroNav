from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

try:
    from services.quiz_service import (
        create_question,
        delete_question,
        get_all_questions,
        submit_quiz_and_generate_roadmap,
        update_question,
    )
except ImportError:  # pragma: no cover - supports package import style
    from ..services.quiz_service import (
        create_question,
        delete_question,
        get_all_questions,
        submit_quiz_and_generate_roadmap,
        update_question,
    )

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/questions', methods=['GET'])
def get_questions():
    """Get all quiz questions"""
    try:
        return jsonify(get_all_questions()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    """Submit quiz answers and generate roadmap"""
    try:
        result = submit_quiz_and_generate_roadmap(
            user_id=get_jwt_identity(),
            payload=request.get_json(silent=True) or {},
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/questions', methods=['POST'])
def add_question():
    try:
        return jsonify(create_question(request.get_json(silent=True) or {})), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@quiz_bp.route('/questions/<id>', methods=['PUT'])
def edit_question(id):
    try:
        return jsonify(update_question(id, request.get_json(silent=True) or {})), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/questions/<id>', methods=['DELETE'])
def delete_question_route(id):
    try:
        return jsonify(delete_question(id)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
