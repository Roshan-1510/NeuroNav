"""Deterministic adaptation engine for roadmap updates."""


from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


FAST_COMPLETION_MINUTES = 20
VIDEO_SKIP_THRESHOLD = 2
STRUGGLE_ATTEMPTS_THRESHOLD = 2
STRUGGLE_TIME_THRESHOLD = 90

def adapt_roadmap(
    roadmap_steps: List[Dict[str, Any]],
    progress_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Update roadmap deterministically based on user behavior.

    Rules:
    1. Track content_type usage and skip counts.
    2. If video skipped > 2, change all future video steps to article/project.
    3. If user completes fast, skip beginner steps not yet started.
    4. If attempts > 2 (or strong struggle signal), insert remedial step before failed step.
    """
    updated_steps = deepcopy(roadmap_steps)
    changes: List[Dict[str, Any]] = []

    progress_by_step = _index_progress_by_step(progress_records)
    usage_summary = _summarize_content_type_usage(updated_steps, progress_by_step)

    if usage_summary["skip_counts"].get("video", 0) > VIDEO_SKIP_THRESHOLD:
        _replace_future_video_steps(updated_steps, progress_by_step, changes)

    if _should_skip_beginner_steps(progress_records):
        removed = _remove_unstarted_beginner_steps(updated_steps, progress_by_step)
        if removed:
            changes.append(
                {
                    "rule": "fast_completion",
                    "message": "Removed unstarted beginner steps due to fast completion trend",
                    "affected_step_ids": removed,
                }
            )

    struggling_steps = _detect_struggling_steps(progress_records)
    if struggling_steps:
        inserted_ids = _insert_remedial_steps(updated_steps, struggling_steps, changes)
        if inserted_ids:
            changes.append(
                {
                    "rule": "attempts_threshold",
                    "message": "Inserted remedial steps before failed steps",
                    "affected_step_ids": inserted_ids,
                }
            )

    _renumber_steps(updated_steps)

    return {
        "updated_roadmap": updated_steps,
        "content_type_usage": usage_summary,
        "changes": changes,
    }


def _index_progress_by_step(progress_records: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Map progress records by step number for quick lookups."""
    by_step: Dict[int, Dict[str, Any]] = {}
    for record in progress_records:
        step_number = _to_int(record.get("step_number"), -1)
        if step_number > 0:
            by_step[step_number] = record
    return by_step


def _summarize_content_type_usage(
    steps: List[Dict[str, Any]], progress_by_step: Dict[int, Dict[str, Any]]
) -> Dict[str, Dict[str, int]]:
    """Track content type usage and skip counts across steps."""
    totals: Dict[str, int] = {}
    skipped: Dict[str, int] = {}

    for step in steps:
        step_number = _to_int(step.get("step"), -1)
        content_type = str(step.get("content_type", "")).strip().lower()
        if step_number <= 0 or not content_type:
            continue

        progress = progress_by_step.get(step_number)
        if not progress:
            continue

        totals[content_type] = totals.get(content_type, 0) + 1
        if bool(progress.get("skipped", False)):
            skipped[content_type] = skipped.get(content_type, 0) + 1

    return {
        "total_counts": totals,
        "skip_counts": skipped,
    }


def _replace_future_video_steps(
    steps: List[Dict[str, Any]],
    progress_by_step: Dict[int, Dict[str, Any]],
    changes: List[Dict[str, Any]],
) -> None:
    """If video was skipped repeatedly, change all future video steps to article/project."""
    skipped_video_steps = []

    for step in steps:
        step_number = _to_int(step.get("step"), -1)
        if step_number <= 0:
            continue
        progress = progress_by_step.get(step_number)
        if progress and bool(progress.get("skipped", False)):
            content_type = str(step.get("content_type", "")).strip().lower()
            if content_type == "video":
                skipped_video_steps.append(step_number)

    if not skipped_video_steps:
        return

    future_start = max(skipped_video_steps)

    for step in steps:
        step_number = _to_int(step.get("step"), -1)
        if step_number <= 0:
            continue
        if step_number <= future_start:
            continue

        progress = progress_by_step.get(step_number)
        if progress and (bool(progress.get("completed")) or bool(progress.get("skipped"))):
            continue

        current_type = str(step.get("content_type", "")).strip().lower()
        if current_type != "video":
            continue

        resources = step.get("resources", {})
        replacement_type = _pick_video_fallback(resources)
        if replacement_type:
            step["content_type"] = replacement_type
            step["content"] = resources[replacement_type]
            changes.append(
                {
                    "rule": "video_skip_threshold",
                    "message": "Video skipped >2: replaced future video step",
                    "step": step_number,
                    "from": current_type,
                    "to": replacement_type,
                }
            )


def _pick_video_fallback(resources: Dict[str, Any]) -> str:
    """Pick article first, else project, when replacing video steps."""
    for candidate in ["article", "project"]:
        if candidate in resources and resources[candidate]:
            return candidate
    return ""


def _should_skip_beginner_steps(progress_records: List[Dict[str, Any]]) -> bool:
    """Detect fast completion trend from completed records."""
    completed_times: List[int] = []
    for record in progress_records:
        if bool(record.get("completed", False)):
            time_spent = _to_int(record.get("time_spent"), 0)
            if time_spent > 0:
                completed_times.append(time_spent)

    if len(completed_times) < 2:
        return False

    avg_time = sum(completed_times) / len(completed_times)
    return avg_time <= FAST_COMPLETION_MINUTES


def _remove_unstarted_beginner_steps(
    steps: List[Dict[str, Any]], progress_by_step: Dict[int, Dict[str, Any]]
) -> List[str]:
    """Remove beginner steps that have not been started yet."""
    removed_skill_ids: List[str] = []
    kept_steps: List[Dict[str, Any]] = []

    for step in steps:
        step_number = _to_int(step.get("step"), -1)
        difficulty = str(step.get("difficulty", "")).strip().lower()
        progress = progress_by_step.get(step_number)
        started = bool(progress) and (
            bool(progress.get("completed", False))
            or bool(progress.get("skipped", False))
            or _to_int(progress.get("attempts"), 0) > 0
            or _to_int(progress.get("time_spent"), 0) > 0
        )

        if difficulty == "beginner" and not started:
            removed_skill_ids.append(str(step.get("skill_id", "")))
            continue

        kept_steps.append(step)

    steps[:] = kept_steps
    return [skill_id for skill_id in removed_skill_ids if skill_id]


def _detect_struggling_steps(progress_records: List[Dict[str, Any]]) -> List[int]:
    """Find step numbers where learner appears to be struggling."""
    struggling: List[int] = []

    for record in progress_records:
        attempts = _to_int(record.get("attempts"), 0)
        time_spent = _to_int(record.get("time_spent"), 0)
        completed = bool(record.get("completed", False))
        step_number = _to_int(record.get("step_number"), -1)

        if step_number <= 0:
            continue

        if (attempts > STRUGGLE_ATTEMPTS_THRESHOLD or time_spent >= STRUGGLE_TIME_THRESHOLD) and not completed:
            struggling.append(step_number)

    return sorted(set(struggling))


def _insert_remedial_steps(
    steps: List[Dict[str, Any]], struggling_steps: List[int], changes: List[Dict[str, Any]]
) -> List[str]:
    """Insert deterministic remedial steps before failed steps."""
    inserted_ids: List[str] = []

    offset = 0
    for target_step in struggling_steps:
        insert_at = target_step - 1 + offset
        if insert_at < 0 or insert_at > len(steps):
            continue

        target = steps[insert_at] if insert_at < len(steps) else None
        if not target:
            continue

        support_step = {
            "step": 0,
            "goal": target.get("goal", ""),
            "skill_id": f"remedial-{target.get('skill_id', 'unknown')}",
            "skill_name": f"Remedial: {target.get('skill_name', 'Practice')}",
            "difficulty": "beginner",
            "prerequisites": [],
            "brain_type": target.get("brain_type", "reading"),
            "content_type": "article",
            "content": f"Remedial fundamentals for {target.get('skill_name', 'the next skill')}",
            "resources": {
                "video": f"Remedial concept refresher for {target.get('skill_name', 'the next skill')}",
                "article": f"Remedial step-by-step guide for {target.get('skill_name', 'the next skill')}",
                "project": f"Remedial mini-practice before {target.get('skill_name', 'the next skill')}",
            },
            "is_remedial_step": True,
        }

        steps.insert(insert_at, support_step)
        offset += 1
        inserted_ids.append(str(support_step["skill_id"]))
        changes.append(
            {
                "rule": "attempts_threshold",
                "message": "Attempts >2: inserted remedial step before failed step",
                "before_step": target_step,
                "remedial_skill_id": support_step["skill_id"],
            }
        )

    return inserted_ids


def _renumber_steps(steps: List[Dict[str, Any]]) -> None:
    """Ensure roadmap step numbers stay sequential after adaptation."""
    for index, step in enumerate(steps, start=1):
        step["step"] = index


def _to_int(value: Any, default: int) -> int:
    """Safe integer parsing helper."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
