"""Progress tracking and adaptation persistence service."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId
from flask import current_app

try:
    from services.adaptation_service import adapt_roadmap
except ImportError:  # pragma: no cover - supports package import style
    from .adaptation_service import adapt_roadmap


def update_step_progress(user_id: str, roadmap_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Upsert progress for one step and return persisted values."""
    if not data or "step_number" not in data or "completed" not in data:
        raise ValueError("step_number and completed fields are required")

    db = current_app.db
    roadmap = _get_user_roadmap(db, user_id, roadmap_id)
    if not roadmap:
        raise LookupError("Roadmap not found or access denied")

    step_number = int(data["step_number"])
    completed = bool(data["completed"])
    skipped = bool(data.get("skipped", False))
    time_spent = int(data.get("time_spent", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)

    progress_entry = {
        "user_id": user_id,
        "roadmap_id": roadmap_id,
        "step_number": step_number,
        "step_id": str(data.get("step_id") or f"step-{step_number}"),
        "completed": completed,
        "skipped": skipped,
        "time_spent": time_spent,
        "attempts": attempts,
        "completed_at": datetime.utcnow() if completed else None,
        "updated_at": datetime.utcnow(),
    }

    db.progress.update_one(
        {
            "user_id": {"$in": _user_id_variants(user_id)},
            "roadmap_id": roadmap_id,
            "step_number": step_number,
        },
        {"$set": progress_entry},
        upsert=True,
    )

    return {
        "message": "Progress updated successfully",
        "step_number": step_number,
        "completed": completed,
        "skipped": skipped,
        "time_spent": time_spent,
        "attempts": attempts,
    }


def get_roadmap_progress(user_id: str, roadmap_id: str) -> List[Dict[str, Any]]:
    """Return progress records for one roadmap."""
    db = current_app.db
    roadmap = _get_user_roadmap(db, user_id, roadmap_id)
    if not roadmap:
        raise LookupError("Roadmap not found or access denied")

    progress_records = list(
        db.progress.find(
            {
                "user_id": {"$in": _user_id_variants(user_id)},
                "roadmap_id": roadmap_id,
            }
        )
    )
    return [
        {
            "step_number": record["step_number"],
            "completed": record.get("completed", False),
            "skipped": record.get("skipped", False),
            "time_spent": record.get("time_spent", 0),
            "attempts": record.get("attempts", 0),
            "completed_at": record.get("completed_at"),
            "updated_at": record.get("updated_at"),
        }
        for record in progress_records
    ]


def get_user_progress_summary(user_id: str) -> Dict[str, Any]:
    """Compute aggregated progress summary across all user roadmaps."""
    db = current_app.db
    roadmaps = list(db.roadmaps.find({"user_id": {"$in": _user_id_variants(user_id)}}))

    roadmap_summaries = []
    total_steps = 0
    total_completed = 0

    for roadmap in roadmaps:
        roadmap_id = str(roadmap["_id"])
        progress_records = list(
            db.progress.find(
                {
                    "user_id": {"$in": _user_id_variants(user_id)},
                    "roadmap_id": roadmap_id,
                }
            )
        )

        roadmap_total_steps = len(roadmap.get("steps", []))
        roadmap_completed_steps = sum(1 for p in progress_records if p.get("completed", False))
        completion_percentage = (roadmap_completed_steps / roadmap_total_steps * 100) if roadmap_total_steps > 0 else 0

        last_activity = None
        if progress_records:
            dated = [
                p.get("updated_at") or p.get("completed_at")
                for p in progress_records
                if p.get("updated_at") or p.get("completed_at")
            ]
            if dated:
                last_activity = max(dated)

        roadmap_summaries.append(
            {
                "roadmap_id": roadmap_id,
                "roadmap_title": roadmap.get("topic", "Untitled"),
                "brain_type": roadmap.get("brain_type", ""),
                "total_steps": roadmap_total_steps,
                "completed_steps": roadmap_completed_steps,
                "completion_percentage": round(completion_percentage, 1),
                "last_activity": last_activity.isoformat() if last_activity else None,
                "created_at": roadmap.get("created_at").isoformat() if roadmap.get("created_at") else None,
            }
        )

        total_steps += roadmap_total_steps
        total_completed += roadmap_completed_steps

    overall_completion = (total_completed / total_steps * 100) if total_steps > 0 else 0

    return {
        "user_id": user_id,
        "roadmaps": roadmap_summaries,
        "overall_summary": {
            "total_roadmaps": len(roadmaps),
            "total_steps": total_steps,
            "completed_steps": total_completed,
            "overall_completion_percentage": round(overall_completion, 1),
        },
    }


def adapt_and_persist_roadmap(user_id: str, roadmap_id: str) -> Dict[str, Any]:
    """Apply adaptation engine and persist updated roadmap steps."""
    db = current_app.db
    roadmap = _get_user_roadmap(db, user_id, roadmap_id)
    if not roadmap:
        raise LookupError("Roadmap not found or access denied")

    progress_records = list(
        db.progress.find(
            {
                "user_id": {"$in": _user_id_variants(user_id)},
                "roadmap_id": roadmap_id,
            }
        )
    )

    adaptation_result = adapt_roadmap(
        roadmap_steps=roadmap.get("steps", []),
        progress_records=progress_records,
    )

    db.roadmaps.update_one(
        {"_id": ObjectId(roadmap_id), "user_id": {"$in": _user_id_variants(user_id)}},
        {
            "$set": {
                "steps": adaptation_result["updated_roadmap"],
                "roadmap": adaptation_result["updated_roadmap"],
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return {
        "message": "Roadmap adapted successfully",
        "roadmap_id": roadmap_id,
        "content_type_usage": adaptation_result.get("content_type_usage", {}),
        "changes": adaptation_result["changes"],
        "total_steps": len(adaptation_result["updated_roadmap"]),
        "steps": adaptation_result["updated_roadmap"],
    }


def _user_id_variants(user_id: str) -> List[Any]:
    """Return possible stored variants for user_id lookups."""
    variants: List[Any] = [user_id]
    if ObjectId.is_valid(user_id):
        variants.append(ObjectId(user_id))
    return variants


def _get_user_roadmap(db: Any, user_id: str, roadmap_id: str) -> Dict[str, Any] | None:
    """Find roadmap by id and user ownership with robust id handling."""
    if not ObjectId.is_valid(roadmap_id):
        return None

    return db.roadmaps.find_one(
        {
            "_id": ObjectId(roadmap_id),
            "user_id": {"$in": _user_id_variants(user_id)},
        }
    )
