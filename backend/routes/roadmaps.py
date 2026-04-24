<<<<<<< HEAD
"""Roadmap routes: normalized API for roadmap CRUD, steps, and regeneration."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo.errors import AutoReconnect, NetworkTimeout, ServerSelectionTimeoutError

try:
    from services.ai_roadmap_service import generate_and_save_roadmap, generate_roadmap
except ImportError:  # pragma: no cover - supports package import style
    from ..services.ai_roadmap_service import generate_and_save_roadmap, generate_roadmap

try:
    from services.content_service import get_learning_resource_for_skill
    from services.skill_service import get_ordered_skills_for_goal, normalize_goal
except ImportError:  # pragma: no cover - supports package import style
    from ..services.content_service import get_learning_resource_for_skill
    from ..services.skill_service import get_ordered_skills_for_goal, normalize_goal

roadmaps_bp = Blueprint("roadmaps", __name__)


def _user_id_variants(user_id: str) -> List[Any]:
    variants: List[Any] = [user_id]
    if ObjectId.is_valid(user_id):
        variants.append(ObjectId(user_id))
    return variants


def _estimate_completion_weeks(steps: List[Dict[str, Any]]) -> int:
    total_minutes = sum(int(step.get("estimated_time_minutes", 30) or 30) for step in steps)
    # Assume 45 mins/day learning pace.
    return max(1, round(total_minutes / (45 * 7)))


def _coerce_step(raw_step: Any, default_step_number: int) -> Dict[str, Any]:
    """Normalize legacy/non-standard step payloads into a dict shape."""
    if isinstance(raw_step, dict):
        step = dict(raw_step)
        step.setdefault("step_number", step.get("step") or default_step_number)
        return step

    # Legacy roadmaps may store simple strings or unknown values.
    if isinstance(raw_step, str):
        return {
            "step_number": default_step_number,
            "title": f"Step {default_step_number}",
            "description": raw_step,
            "resource_url": "",
            "resource_type": "article",
            "estimated_time_minutes": 30,
            "tags": [],
            "brain_type_optimized": True,
        }

    return {
        "step_number": default_step_number,
        "title": f"Step {default_step_number}",
        "description": "Learn this concept.",
        "resource_url": "",
        "resource_type": "article",
        "estimated_time_minutes": 30,
        "tags": [],
        "brain_type_optimized": True,
    }


def _merge_progress(roadmap_id: str, steps: List[Dict[str, Any]], user_id: str, goal: str) -> Dict[str, Any]:
    db = current_app.db
    progress_records = list(
        db.progress.find(
            {
                "user_id": {"$in": _user_id_variants(user_id)},
                "roadmap_id": roadmap_id,
            }
        )
    )

    progress_by_step = {int(p.get("step_number", 0)): p for p in progress_records}
    completed_count = 0
    try:
        ordered_skills = get_ordered_skills_for_goal(normalize_goal(goal or ""))
    except Exception:
        # Never fail roadmap fetch due to legacy/unsupported goal labels.
        ordered_skills = get_ordered_skills_for_goal("data analyst")

    merged_steps: List[Dict[str, Any]] = []
    for index, raw_step in enumerate(steps, start=1):
        step = _coerce_step(raw_step, index)
        step_number = int(step.get("step_number") or step.get("step") or index)
        progress = progress_by_step.get(step_number, {})
        completed = bool(progress.get("completed", step.get("completed", False)))
        if completed:
            completed_count += 1

        resource_type = step.get("resource_type") or step.get("content_type") or "article"
        resource_url = str(step.get("resource_url") or "").strip()
        resource_title = str(step.get("resource_title") or "").strip()
        inferred_skill_id = _infer_skill_id(step, step_number, ordered_skills)

        if not _looks_valid_external_url(resource_url):
            fallback_resource = get_learning_resource_for_skill(inferred_skill_id, resource_type)
            resource_url = fallback_resource.get("url", "")
            if not resource_title:
                resource_title = fallback_resource.get("title", "")
            resource_type = fallback_resource.get("resource_type", resource_type)

        merged_steps.append(
            {
                "step_number": step_number,
                "title": step.get("title") or step.get("skill_name") or f"Step {step_number}",
                "description": step.get("description") or step.get("content") or "Learn this concept.",
                "resource_id": str(step.get("resource_id") or f"resource-{step_number}"),
                "resource_title": resource_title,
                "resource_url": resource_url,
                "resource_type": resource_type,
                "estimated_time_minutes": int(step.get("estimated_time_minutes", 30) or 30),
                "tags": step.get("tags") if isinstance(step.get("tags"), list) else [],
                "brain_type_optimized": bool(step.get("brain_type_optimized", True)),
                "mission": step.get("mission", ""),
                "proof_of_work": step.get("proof_of_work", ""),
                "win_condition": step.get("win_condition", ""),
                "speed_boost": step.get("speed_boost", ""),
                "generic_gap": step.get("generic_gap", ""),
                "neuronav_engine": step.get("neuronav_engine") if isinstance(step.get("neuronav_engine"), dict) else {},
                "learning_contract": step.get("learning_contract", ""),
                "completed": completed,
                "completed_at": progress.get("completed_at") or step.get("completed_at"),
            }
        )

    total_steps = len(merged_steps)
    completion_percentage = round((completed_count / total_steps) * 100, 1) if total_steps else 0.0

    return {
        "steps": merged_steps,
        "progress_summary": {
            "total_steps": total_steps,
            "completed_steps": completed_count,
            "completion_percentage": completion_percentage,
        },
    }


def _looks_valid_external_url(url: str) -> bool:
    normalized = str(url or "").strip().lower()
    return normalized.startswith("http://") or normalized.startswith("https://")


def _infer_skill_id(step: Dict[str, Any], step_number: int, ordered_skills: List[Dict[str, Any]]) -> str:
    skill_id = str(step.get("skill_id") or "").strip()
    if skill_id:
        return skill_id

    if not ordered_skills:
        return "da-01"

    index = min(max(step_number - 1, 0), len(ordered_skills) - 1)
    return str(ordered_skills[index].get("id") or "da-01")


def _format_roadmap_doc(roadmap: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    roadmap_id = str(roadmap.get("_id"))
    raw_steps = roadmap.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        fallback_steps = roadmap.get("roadmap")
        raw_steps = fallback_steps if isinstance(fallback_steps, list) else []

    merged = _merge_progress(roadmap_id, raw_steps, user_id, roadmap.get("goal") or roadmap.get("topic") or "")

    steps = merged["steps"]
    total_minutes = sum(int(step.get("estimated_time_minutes", 30) or 30) for step in steps)

    created_at = roadmap.get("created_at")
    updated_at = roadmap.get("updated_at")

    return {
        "roadmap_id": roadmap_id,
        "user_id": str(roadmap.get("user_id", "")),
        "topic": roadmap.get("topic") or roadmap.get("goal") or "Untitled",
        "goal": roadmap.get("goal") or roadmap.get("topic") or "",
        "brain_type": roadmap.get("brain_type", ""),
        "steps": steps,
        "estimated_completion_weeks": roadmap.get("estimated_completion_weeks") or _estimate_completion_weeks(steps),
        "daily_time_minutes": roadmap.get("daily_time_minutes") or 45,
        "total_time_minutes": total_minutes,
        "source": roadmap.get("source", "ai"),
        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
        "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else updated_at,
        "progress_summary": merged["progress_summary"],
    }


@roadmaps_bp.route("/roadmaps", methods=["GET"])
@jwt_required()
def get_user_roadmaps():
    """Get all roadmaps for the current user."""
    user_id = get_jwt_identity()
    db = current_app.db

    try:
        roadmaps = list(
            db.roadmaps.find(
                {"user_id": {"$in": _user_id_variants(user_id)}},
                sort=[("updated_at", -1)],
            )
        )
        formatted = [_format_roadmap_doc(roadmap, user_id) for roadmap in roadmaps]
        return jsonify({"roadmaps": formatted, "total_roadmaps": len(formatted)}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to fetch roadmaps: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/<roadmap_id>", methods=["GET"])
@jwt_required()
def get_roadmap(roadmap_id):
    """Get a specific roadmap by ID."""
    user_id = get_jwt_identity()
    db = current_app.db

    try:
        if not ObjectId.is_valid(roadmap_id):
            return jsonify({"error": "Invalid roadmap ID"}), 400

        roadmap = db.roadmaps.find_one(
            {
                "_id": ObjectId(roadmap_id),
                "user_id": {"$in": _user_id_variants(user_id)},
            }
        )
        if not roadmap:
            return jsonify({"error": "Roadmap not found"}), 404

        return jsonify(_format_roadmap_doc(roadmap, user_id)), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to fetch roadmap: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/<roadmap_id>", methods=["PUT"])
@jwt_required()
def update_roadmap(roadmap_id):
    """Update roadmap fields, including full steps replacement."""
    user_id = get_jwt_identity()
    db = current_app.db
    payload = request.get_json(silent=True) or {}

    try:
        if not ObjectId.is_valid(roadmap_id):
            return jsonify({"error": "Invalid roadmap ID"}), 400

        if "steps" in payload and isinstance(payload["steps"], list):
            # Keep backward-compatible alias in roadmap field.
            payload["roadmap"] = payload["steps"]

        payload["updated_at"] = datetime.utcnow()

        result = db.roadmaps.update_one(
            {
                "_id": ObjectId(roadmap_id),
                "user_id": {"$in": _user_id_variants(user_id)},
            },
            {"$set": payload},
        )
        if result.matched_count == 0:
            return jsonify({"error": "Roadmap not found"}), 404

        updated = db.roadmaps.find_one({"_id": ObjectId(roadmap_id)})
        return jsonify(_format_roadmap_doc(updated, user_id)), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to update roadmap: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/<roadmap_id>", methods=["DELETE"])
@jwt_required()
def delete_roadmap(roadmap_id):
    """Delete a specific roadmap."""
    user_id = get_jwt_identity()
    db = current_app.db

    try:
        if not ObjectId.is_valid(roadmap_id):
            return jsonify({"error": "Invalid roadmap ID"}), 400

        query = {
            "_id": ObjectId(roadmap_id),
            "user_id": {"$in": _user_id_variants(user_id)},
        }

        result = None
        transient_error: Exception | None = None
        for _ in range(2):
            try:
                result = db.roadmaps.delete_one(query)
                db.progress.delete_many({"roadmap_id": roadmap_id, "user_id": {"$in": _user_id_variants(user_id)}})
                transient_error = None
                break
            except (ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect) as exc:
                transient_error = exc

        if transient_error is not None:
            return (
                jsonify(
                    {
                        "error": "Database is temporarily unavailable. Please retry in a few seconds.",
                        "details": str(transient_error),
                    }
                ),
                503,
            )

        if result is None:
            return jsonify({"error": "Failed to delete roadmap"}), 500

        if result.deleted_count == 0:
            return jsonify({"error": "Roadmap not found"}), 404

        return jsonify({"message": "Roadmap deleted"}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to delete roadmap: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/<roadmap_id>/steps", methods=["POST"])
@jwt_required()
def add_step(roadmap_id):
    """Add a step to roadmap and renumber steps."""
    user_id = get_jwt_identity()
    db = current_app.db
    payload = request.get_json(silent=True) or {}

    try:
        if not ObjectId.is_valid(roadmap_id):
            return jsonify({"error": "Invalid roadmap ID"}), 400

        roadmap = db.roadmaps.find_one(
            {
                "_id": ObjectId(roadmap_id),
                "user_id": {"$in": _user_id_variants(user_id)},
            }
        )
        if not roadmap:
            return jsonify({"error": "Roadmap not found"}), 404

        steps = list(roadmap.get("steps") or [])
        insert_position = int(payload.get("insert_position") or (len(steps) + 1))
        insert_index = max(0, min(insert_position - 1, len(steps)))

        new_step = {
            "step_number": 0,
            "title": payload.get("title") or "New Step",
            "description": payload.get("description") or "Describe this learning step.",
            "resource_id": payload.get("resource_id") or f"resource-{len(steps) + 1}",
            "resource_url": payload.get("resource_url") or "",
            "resource_type": payload.get("resource_type") or payload.get("content_type") or "article",
            "estimated_time_minutes": int(payload.get("estimated_time_minutes", 30) or 30),
            "tags": payload.get("tags") if isinstance(payload.get("tags"), list) else [],
            "brain_type_optimized": bool(payload.get("brain_type_optimized", True)),
            "completed": False,
        }

        steps.insert(insert_index, new_step)
        for idx, step in enumerate(steps, start=1):
            step["step_number"] = idx
            step["step"] = idx

        db.roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "steps": steps,
                    "roadmap": steps,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        updated = db.roadmaps.find_one({"_id": ObjectId(roadmap_id)})
        return jsonify(_format_roadmap_doc(updated, user_id)), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to add step: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/<roadmap_id>/steps/<int:step_number>", methods=["DELETE"])
@jwt_required()
def delete_step(roadmap_id, step_number):
    """Delete a step and renumber remaining steps."""
    user_id = get_jwt_identity()
    db = current_app.db

    try:
        if not ObjectId.is_valid(roadmap_id):
            return jsonify({"error": "Invalid roadmap ID"}), 400

        roadmap = db.roadmaps.find_one(
            {
                "_id": ObjectId(roadmap_id),
                "user_id": {"$in": _user_id_variants(user_id)},
            }
        )
        if not roadmap:
            return jsonify({"error": "Roadmap not found"}), 404

        steps = list(roadmap.get("steps") or [])
        filtered = [s for s in steps if int(s.get("step_number") or s.get("step") or -1) != int(step_number)]
        if len(filtered) == len(steps):
            return jsonify({"error": "Step not found"}), 404

        for idx, step in enumerate(filtered, start=1):
            step["step_number"] = idx
            step["step"] = idx

        db.roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "steps": filtered,
                    "roadmap": filtered,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        db.progress.delete_many(
            {
                "roadmap_id": roadmap_id,
                "step_number": int(step_number),
                "user_id": {"$in": _user_id_variants(user_id)},
            }
        )

        updated = db.roadmaps.find_one({"_id": ObjectId(roadmap_id)})
        return jsonify(_format_roadmap_doc(updated, user_id)), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to delete step: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/<roadmap_id>/steps/reorder", methods=["PUT"])
@jwt_required()
def reorder_steps(roadmap_id):
    """Reorder steps using provided step_number order."""
    user_id = get_jwt_identity()
    db = current_app.db
    payload = request.get_json(silent=True) or {}

    try:
        if not ObjectId.is_valid(roadmap_id):
            return jsonify({"error": "Invalid roadmap ID"}), 400

        roadmap = db.roadmaps.find_one(
            {
                "_id": ObjectId(roadmap_id),
                "user_id": {"$in": _user_id_variants(user_id)},
            }
        )
        if not roadmap:
            return jsonify({"error": "Roadmap not found"}), 404

        step_order = payload.get("step_order")
        if not isinstance(step_order, list) or not step_order:
            return jsonify({"error": "step_order must be a non-empty list"}), 400

        steps = list(roadmap.get("steps") or [])
        by_step_number = {
            int(step.get("step_number") or step.get("step") or idx + 1): step
            for idx, step in enumerate(steps)
        }

        reordered: List[Dict[str, Any]] = []
        for original_step_number in step_order:
            key = int(original_step_number)
            if key in by_step_number:
                reordered.append(by_step_number[key])

        # Append any missing steps to avoid data loss.
        used = {int(s.get("step_number") or s.get("step") or 0) for s in reordered}
        for key, step in by_step_number.items():
            if key not in used:
                reordered.append(step)

        for idx, step in enumerate(reordered, start=1):
            step["step_number"] = idx
            step["step"] = idx

        db.roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "steps": reordered,
                    "roadmap": reordered,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        updated = db.roadmaps.find_one({"_id": ObjectId(roadmap_id)})
        return jsonify(_format_roadmap_doc(updated, user_id)), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to reorder steps: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/<roadmap_id>/regenerate", methods=["POST"])
@jwt_required()
def regenerate_roadmap(roadmap_id):
    """Regenerate an existing roadmap using its goal/topic and brain_type."""
    user_id = get_jwt_identity()
    db = current_app.db
    payload = request.get_json(silent=True) or {}

    try:
        if not ObjectId.is_valid(roadmap_id):
            return jsonify({"error": "Invalid roadmap ID"}), 400

        roadmap = db.roadmaps.find_one(
            {
                "_id": ObjectId(roadmap_id),
                "user_id": {"$in": _user_id_variants(user_id)},
            }
        )
        if not roadmap:
            return jsonify({"error": "Roadmap not found"}), 404

        goal = payload.get("goal") or roadmap.get("goal") or roadmap.get("topic") or "data analyst"
        brain_type = payload.get("brain_type") or roadmap.get("brain_type") or "visual"

        regenerated_steps = generate_roadmap(goal=goal, brain_type=brain_type)

        db.roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "goal": goal,
                    "topic": goal,
                    "brain_type": brain_type,
                    "steps": regenerated_steps,
                    "roadmap": regenerated_steps,
                    "source": "ai",
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        db.progress.delete_many({"roadmap_id": roadmap_id, "user_id": {"$in": _user_id_variants(user_id)}})

        updated = db.roadmaps.find_one({"_id": ObjectId(roadmap_id)})
        return jsonify(
            {
                "message": "Roadmap regenerated successfully",
                "roadmap": _format_roadmap_doc(updated, user_id),
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to regenerate roadmap: {exc}"}), 500


@roadmaps_bp.route("/roadmaps/generate", methods=["POST"])
@jwt_required()
def generate_user_roadmap():
    """Generate a roadmap for goal + brain type and persist as a new roadmap."""
    payload = request.get_json(silent=True) or {}
    goal = payload.get("goal", "")
    brain_type = payload.get("brain_type", "")
    user_id = payload.get("user_id") or get_jwt_identity()

    if not goal or not brain_type:
        return jsonify({"error": "Both 'goal' and 'brain_type' are required"}), 400

    if not user_id:
        return jsonify({"error": "Unable to resolve user_id from token"}), 400

    try:
        result = generate_and_save_roadmap(
            db=current_app.db,
            user_id=user_id,
            goal=goal,
            brain_type=brain_type,
        )
        return (
            jsonify(
                {
                    "roadmap_id": result["roadmap_id"],
                    "goal": result["goal"],
                    "topic": result["goal"],
                    "brain_type": result["brain_type"],
                    "source": result["source"],
                    "total_steps": result["total_steps"],
                    "steps": result["steps"],
                    "estimated_completion_weeks": _estimate_completion_weeks(result["steps"]),
                    "daily_time_minutes": 45,
                }
            ),
            200,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Roadmap generation failed: {exc}"}), 500
=======
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
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
