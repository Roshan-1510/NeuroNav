"""Analytics service for progress-driven learning insights."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

from bson import ObjectId
from flask import current_app


WEAK_SKILL_ATTEMPTS_THRESHOLD = 3


def analyze_user_progress(user_id: str) -> Dict[str, Any]:
	"""Analyze user progress collection and return key learning analytics."""
	db = current_app.db

	progress_records = _get_user_progress_records(db, user_id)
	roadmap_ids = sorted({str(record.get("roadmap_id", "")) for record in progress_records if record.get("roadmap_id")})
	roadmap_step_index = _build_roadmap_step_index(db, roadmap_ids)

	most_skipped = _most_skipped_content_type(progress_records, roadmap_step_index)
	average_time = _average_completion_time(progress_records)
	weakest_skills = _weakest_skills(progress_records, roadmap_step_index)

	return {
		"user_id": user_id,
		"most_skipped_content_type": most_skipped,
		"average_completion_time": average_time,
		"weakest_skills": weakest_skills,
	}


def _get_user_progress_records(db: Any, user_id: str) -> List[Dict[str, Any]]:
	"""Fetch progress records for the user handling string/ObjectId variations."""
	query_options: List[Any] = [user_id]
	if ObjectId.is_valid(user_id):
		query_options.append(ObjectId(user_id))

	return list(db.progress.find({"user_id": {"$in": query_options}}))


def _build_roadmap_step_index(db: Any, roadmap_ids: List[str]) -> Dict[Tuple[str, int], Dict[str, Any]]:
	"""Build index for step metadata keyed by (roadmap_id, step_number)."""
	index: Dict[Tuple[str, int], Dict[str, Any]] = {}

	for roadmap_id in roadmap_ids:
		roadmap_doc = None
		if ObjectId.is_valid(roadmap_id):
			roadmap_doc = db.roadmaps.find_one({"_id": ObjectId(roadmap_id)})

		if not roadmap_doc:
			continue

		steps = roadmap_doc.get("steps") or roadmap_doc.get("roadmap") or []
		for step in steps:
			step_number = _to_int(step.get("step"), -1)
			if step_number <= 0:
				continue
			index[(roadmap_id, step_number)] = step

	return index


def _most_skipped_content_type(
	progress_records: List[Dict[str, Any]],
	roadmap_step_index: Dict[Tuple[str, int], Dict[str, Any]],
) -> Dict[str, Any]:
	"""Find most skipped content type based on skipped progress records."""
	skipped_counter: Counter[str] = Counter()

	for record in progress_records:
		if not bool(record.get("skipped", False)):
			continue

		roadmap_id = str(record.get("roadmap_id", ""))
		step_number = _to_int(record.get("step_number"), -1)
		if not roadmap_id or step_number <= 0:
			continue

		step = roadmap_step_index.get((roadmap_id, step_number), {})
		content_type = str(step.get("content_type", "unknown")).strip().lower() or "unknown"
		skipped_counter[content_type] += 1

	if not skipped_counter:
		return {"content_type": None, "count": 0}

	content_type, count = sorted(skipped_counter.items(), key=lambda kv: (-kv[1], kv[0]))[0]
	return {"content_type": content_type, "count": count}


def _average_completion_time(progress_records: List[Dict[str, Any]]) -> Dict[str, Any]:
	"""Compute average time_spent for completed steps."""
	completion_times: List[int] = []

	for record in progress_records:
		if not bool(record.get("completed", False)):
			continue

		time_spent = _to_int(record.get("time_spent"), 0)
		if time_spent > 0:
			completion_times.append(time_spent)

	if not completion_times:
		return {"minutes": 0.0, "samples": 0}

	avg = round(sum(completion_times) / len(completion_times), 1)
	return {"minutes": avg, "samples": len(completion_times)}


def _weakest_skills(
	progress_records: List[Dict[str, Any]],
	roadmap_step_index: Dict[Tuple[str, int], Dict[str, Any]],
) -> List[Dict[str, Any]]:
	"""Return skills with high total attempts across records."""
	attempts_by_skill: Dict[str, int] = defaultdict(int)

	for record in progress_records:
		attempts = _to_int(record.get("attempts"), 0)
		if attempts <= 0:
			continue

		roadmap_id = str(record.get("roadmap_id", ""))
		step_number = _to_int(record.get("step_number"), -1)
		if not roadmap_id or step_number <= 0:
			continue

		step = roadmap_step_index.get((roadmap_id, step_number), {})
		skill_name = str(
			step.get("skill_name")
			or step.get("title")
			or step.get("skill_id")
			or f"step-{step_number}"
		)
		attempts_by_skill[skill_name] += attempts

	weak = [
		{"skill": skill, "attempts": attempts}
		for skill, attempts in attempts_by_skill.items()
		if attempts >= WEAK_SKILL_ATTEMPTS_THRESHOLD
	]

	return sorted(weak, key=lambda x: (-x["attempts"], x["skill"]))


def _to_int(value: Any, default: int) -> int:
	"""Safely parse integer values."""
	try:
		return int(value)
	except (TypeError, ValueError):
		return default