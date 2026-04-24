"""MongoDB schema helpers for user progress."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from bson import ObjectId


def progress_schema() -> Dict[str, Any]:
	"""Return default progress document schema."""
	return {
		"_id": ObjectId(),
		"user_id": ObjectId(),
		"roadmap_id": ObjectId(),
		"step_id": "",
		"step_number": 0,
		"completed": False,
		"time_spent": 0,
		"skipped": False,
		"attempts": 0,
		"completed_at": None,
		"created_at": datetime.utcnow(),
		"updated_at": datetime.utcnow(),
	}


def validate_progress_payload(payload: Dict[str, Any]) -> None:
	"""Validate required fields and value ranges for progress updates."""
	required_fields = ["user_id", "roadmap_id", "step_id", "completed"]
	missing = [field for field in required_fields if field not in payload]
	if missing:
		raise ValueError(f"Missing required fields: {', '.join(missing)}")

	if not isinstance(payload["step_id"], str) or not payload["step_id"].strip():
		raise ValueError("step_id must be a non-empty string")

	if not isinstance(payload["completed"], bool):
		raise ValueError("completed must be a boolean")

	time_spent = payload.get("time_spent", 0)
	attempts = payload.get("attempts", 0)
	if not isinstance(time_spent, int) or time_spent < 0:
		raise ValueError("time_spent must be a non-negative integer")
	if not isinstance(attempts, int) or attempts < 0:
		raise ValueError("attempts must be a non-negative integer")


def build_progress_document(payload: Dict[str, Any]) -> Dict[str, Any]:
	"""Build normalized progress document from API/service payload."""
	validate_progress_payload(payload)

	completed = payload["completed"]
	now = datetime.utcnow()
	return {
		"user_id": payload["user_id"],
		"roadmap_id": payload["roadmap_id"],
		"step_id": payload["step_id"].strip(),
		"step_number": int(payload.get("step_number", 0) or 0),
		"completed": completed,
		"time_spent": int(payload.get("time_spent", 0) or 0),
		"skipped": bool(payload.get("skipped", False)),
		"attempts": int(payload.get("attempts", 0) or 0),
		"completed_at": now if completed else None,
		"updated_at": now,
	}


def ensure_progress_indexes(progress_collection: Any) -> None:
	"""Create deterministic indexes for progress queries and upserts."""
	progress_collection.create_index(
		[("user_id", 1), ("roadmap_id", 1), ("step_id", 1)],
		unique=True,
		name="uniq_user_roadmap_step",
	)
	progress_collection.create_index(
		[("user_id", 1), ("roadmap_id", 1), ("step_number", 1)],
		name="idx_user_roadmap_step_number",
	)
	progress_collection.create_index(
		[("updated_at", -1)],
		name="idx_progress_updated_at",
	)