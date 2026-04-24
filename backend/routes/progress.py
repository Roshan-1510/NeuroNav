from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

try:
    from services.progress_service import (
        adapt_and_persist_roadmap,
        get_roadmap_progress as service_get_roadmap_progress,
        get_user_progress_summary as service_get_user_progress_summary,
        update_step_progress as service_update_step_progress,
    )
except ImportError:  # pragma: no cover - supports package import style
    from ..services.progress_service import (
        adapt_and_persist_roadmap,
        get_roadmap_progress as service_get_roadmap_progress,
        get_user_progress_summary as service_get_user_progress_summary,
        update_step_progress as service_update_step_progress,
    )

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/roadmaps/<roadmap_id>/progress', methods=['POST'])
@jwt_required()
def update_step_progress(roadmap_id):
    """Update progress for a specific roadmap step"""
    try:
        result = service_update_step_progress(
            user_id=get_jwt_identity(),
            roadmap_id=roadmap_id,
            data=request.get_json(silent=True) or {},
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/roadmaps/<roadmap_id>/progress', methods=['GET'])
@jwt_required()
def get_roadmap_progress(roadmap_id):
    """Get progress for a specific roadmap"""
    try:
        return jsonify(service_get_roadmap_progress(get_jwt_identity(), roadmap_id)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/progress/summary', methods=['GET'])
@jwt_required()
def get_user_progress_summary():
    """Get overall progress summary for the user"""
    try:
        return jsonify(service_get_user_progress_summary(get_jwt_identity())), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@progress_bp.route('/roadmaps/<roadmap_id>/adapt', methods=['POST'])
@jwt_required()
def adapt_user_roadmap(roadmap_id):
    """Apply deterministic adaptation rules and persist updated roadmap."""
    try:
        return jsonify(adapt_and_persist_roadmap(get_jwt_identity(), roadmap_id)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
