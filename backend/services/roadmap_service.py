"""Deterministic roadmap generator service."""

from __future__ import annotations

from typing import Any, Dict, List

try:
	from services.skill_service import get_skill_graph_for_goal, normalize_goal, resolve_skill_order
except ImportError:  # pragma: no cover - supports package import style
	from .skill_service import get_skill_graph_for_goal, normalize_goal, resolve_skill_order

try:
	from services.content_service import get_content_options_for_skill
except ImportError:  # pragma: no cover - supports package import style
	from .content_service import get_content_options_for_skill

try:
	from services.content_service import get_learning_resource_for_skill
except ImportError:  # pragma: no cover - supports package import style
	from .content_service import get_learning_resource_for_skill

try:
	from services.neuronav_engine import enrich_roadmap_steps
except ImportError:  # pragma: no cover - supports package import style
	from .neuronav_engine import enrich_roadmap_steps


BRAIN_TYPE_TO_CONTENT_TYPE_BY_GOAL = {
	"data analyst": {
		"visual": "video",
		"auditory": "video",
		"reading": "article",
		"readwrite": "article",
		"kinesthetic": "project",
	},
	"design": {
		"visual": "video",
		"auditory": "podcast",
		"reading": "article",
		"readwrite": "article",
		"kinesthetic": "project",
	},
}


def generate_roadmap(goal: str, brain_type: str) -> List[Dict[str, Any]]:
	"""
	Generate a deterministic ordered roadmap for a goal and brain type.

	Steps:
	1. Load skill graph
	2. Topologically sort skills by prerequisites
	3. Map each skill to content type by brain type
	4. Return ordered roadmap list
	"""
	normalized_goal = _normalize_goal(goal)
	normalized_brain_type = _normalize_brain_type(brain_type)
	content_type = _get_content_type_for_brain_type(normalized_goal, normalized_brain_type)

	skills = _load_skill_graph_for_goal(normalized_goal)
	ordered_skills = resolve_skill_order(skills)
	target_steps = _target_step_count(normalized_goal, normalized_brain_type)

	roadmap_steps: List[Dict[str, Any]] = []
	for index, skill in enumerate(ordered_skills, start=1):
		skill_id = skill["id"]
		content_bundle = _get_content_bundle(skill_id)
		bundle_key = _normalize_content_bundle_key(content_type)
		resource = get_learning_resource_for_skill(skill_id, content_type)
		edge = _build_neuronav_edge(skill=skill, brain_type=normalized_brain_type, step_number=index, goal=normalized_goal)

		roadmap_steps.append(
			{
				"step": index,
				"goal": normalized_goal,
				"skill_id": skill_id,
				"skill_name": skill["name"],
				"difficulty": skill["difficulty"],
				"prerequisites": list(skill["prerequisites"]),
				"brain_type": normalized_brain_type,
				"content_type": content_type,
				"content": content_bundle.get(bundle_key) or content_bundle.get("article") or next(iter(content_bundle.values())),
				"resource_title": resource["title"],
				"resource_url": resource["url"],
				"resource_type": resource["resource_type"],
				"estimated_time_minutes": 45 if content_type == "video" else 25 if content_type == "article" else 90,
				"tags": [normalized_brain_type, skill_id, content_type],
				"brain_type_optimized": True,
				"mission": edge["mission"],
				"proof_of_work": edge["proof_of_work"],
				"win_condition": edge["win_condition"],
				"speed_boost": edge["speed_boost"],
				"generic_gap": edge["generic_gap"],
				"resources": content_bundle,
			}
		)

	# Add adaptive deep-dive steps so deterministic roadmaps are not fixed-length clones.
	if len(roadmap_steps) < target_steps:
		roadmap_steps.extend(
			_build_deep_dive_steps(
				start_step=len(roadmap_steps) + 1,
				target_steps=target_steps,
				goal=normalized_goal,
				brain_type=normalized_brain_type,
				base_content_type=content_type,
			)
		)

	return enrich_roadmap_steps(
		steps=roadmap_steps,
		goal=normalized_goal,
		brain_type=normalized_brain_type,
		source="rule-based",
	)


def _load_skill_graph_for_goal(goal: str) -> List[Dict[str, Any]]:
	"""Load supported goal skill graph."""
	return get_skill_graph_for_goal(goal)


def _normalize_goal(goal: str) -> str:
	"""Normalize user goal for deterministic matching."""
	return normalize_goal(goal)


def _normalize_brain_type(brain_type: str) -> str:
	"""Normalize brain type aliases to canonical values."""
	value = (brain_type or "").strip().lower().replace("/", "").replace("-", "")
	alias_map = {
		"visual": "visual",
		"auditory": "auditory",
		"reading": "reading",
		"readwrite": "reading",
		"readwriting": "reading",
		"kinesthetic": "kinesthetic",
		"kinaesthetic": "kinesthetic",
	}

	if value not in alias_map:
		raise ValueError(
			"Invalid brain_type. Use one of: visual, auditory, reading, kinesthetic"
		)

	return alias_map[value]


def _get_content_type_for_brain_type(goal: str, brain_type: str) -> str:
	"""Map brain type to a primary content type."""
	goal_map = BRAIN_TYPE_TO_CONTENT_TYPE_BY_GOAL.get(goal, BRAIN_TYPE_TO_CONTENT_TYPE_BY_GOAL["data analyst"])
	return goal_map.get(brain_type, "article")


def _get_content_bundle(skill_id: str) -> Dict[str, str]:
	"""Get deterministic content bundle for a skill."""
	return get_content_options_for_skill(skill_id)


def _build_neuronav_edge(skill: Dict[str, Any], brain_type: str, step_number: int, goal: str) -> Dict[str, str]:
	"""Build step-level differentiators to avoid generic course-like roadmaps."""
	brain_tactics = {
		"visual": "Sketch a one-page visual map before and after learning to track concept clarity.",
		"auditory": "Explain the concept out loud in a 90-second voice note and replay for gaps.",
		"reading": "Write a concise synthesis note: definition, method, caveat, and use-case.",
		"kinesthetic": "Implement a mini-task immediately and learn by fixing one real mistake.",
	}

	tactic = brain_tactics.get(brain_type, "Use your strongest learning mode and produce a concrete output.")
	skill_name = str(skill.get("name", "this skill"))

	return {
		"mission": f"Complete Step {step_number} by applying {skill_name} to one realistic {goal} problem.",
		"proof_of_work": f"Produce one tangible artifact for {skill_name} that can be reviewed and improved.",
		"win_condition": "You can explain what changed from input to insight in under 2 minutes with confidence.",
		"speed_boost": tactic,
		"generic_gap": "Generic roadmaps stop at 'watch/read'; this step requires an artifact and evidence of understanding.",
	}


def _normalize_content_bundle_key(content_type: str) -> str:
	"""Map extended content labels to canonical bundle keys."""
	normalized = str(content_type or "").strip().lower()
	mapping = {
		"lecture": "video",
		"podcast": "video",
		"diagram": "video",
		"documentation": "article",
		"exercise": "project",
	}
	return mapping.get(normalized, normalized)


def _target_step_count(goal: str, brain_type: str) -> int:
	"""Return adaptive deterministic roadmap size to avoid fixed patterns."""
	base_by_brain = {
		"visual": 10,
		"auditory": 11,
		"reading": 11,
		"kinesthetic": 12,
	}
	base = base_by_brain.get(brain_type, 10)
	goal_signal = sum(ord(ch) for ch in goal) % 2
	return max(10, min(12, base + goal_signal))


def _build_deep_dive_steps(
	start_step: int,
	target_steps: int,
	goal: str,
	brain_type: str,
	base_content_type: str,
) -> List[Dict[str, Any]]:
	"""Create performance deep-dive checkpoints beyond core skill graph."""
	steps: List[Dict[str, Any]] = []
	for step_number in range(start_step, target_steps + 1):
		resource_url = "https://www.kaggle.com/competitions"
		if goal == "design":
			resource_url = "https://www.frontendmentor.io/challenges"
		steps.append(
			{
				"step": step_number,
				"goal": goal,
				"skill_id": f"deep-dive-{step_number}",
				"skill_name": "Performance Deep Dive",
				"difficulty": "advanced",
				"prerequisites": [],
				"brain_type": brain_type,
				"content_type": base_content_type,
				"content": "Performance checkpoint and capstone refinement",
				"resource_title": "Capstone Enhancement Playbook",
				"resource_url": resource_url,
				"resource_type": "project",
				"estimated_time_minutes": 75,
				"tags": [brain_type, "deep-dive", "capstone"],
				"brain_type_optimized": True,
				"mission": f"Run a measurable improvement sprint for your {goal} capstone artifact.",
				"proof_of_work": "Before/after artifact comparison with quality rubric and performance notes.",
				"win_condition": "Capstone quality improves on at least one measurable dimension.",
				"speed_boost": "Use a short iterative loop: build, test, critique, refine.",
				"generic_gap": "Most roadmaps end at completion; this step enforces performance optimization.",
				"resources": {
					"video": "Capstone review walkthrough",
					"article": "Performance review checklist",
					"project": "Run an improvement sprint",
				},
			}
		)

	return steps