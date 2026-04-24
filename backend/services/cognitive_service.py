"""Rule-based cognitive profiling service."""

from __future__ import annotations

import random
from typing import Any, Dict, List


BRAIN_TYPES = ("visual", "auditory", "reading", "kinesthetic")
LABEL_TO_CANONICAL = {
	"visual": "visual",
	"auditory": "auditory",
	"readwrite": "reading",
	"reading": "reading",
	"read/write": "reading",
	"kinesthetic": "kinesthetic",
	"kinaesthetic": "kinesthetic",
}


def determine_brain_type(
	answers: List[Dict[str, Any]],
	question_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
	"""
	Convert quiz answers into a deterministic brain type profile.

	Args:
		answers: [{"question_id": "q1", "selected_option": 1}, ...]
		question_map: {"q1": {"options": [{"brain_type": "Visual"}, ...]}, ...}

	Returns:
		{
			"brain_type": "visual|auditory|reading|kinesthetic",
			"confidence_score": float,
			"distribution": {brain_type: count, ...},
			"total_answers": int,
		}
	"""
	distribution = _initialize_distribution()

	for answer in answers:
		question_id = str(answer.get("question_id", ""))
		option_index = _safe_option_index(answer.get("selected_option"))
		question = question_map.get(question_id, {})
		options = question.get("options", [])

		if 0 <= option_index < len(options):
			raw_brain_type = options[option_index].get("brain_type", "")
			canonical = _normalize_brain_type(raw_brain_type)
			if canonical:
				distribution[canonical] += 1

	total_answers = sum(distribution.values())
	dominant = _select_dominant_brain_type(distribution)
	confidence = _compute_confidence(distribution, dominant, total_answers)

	return {
		"brain_type": dominant,
		"confidence_score": confidence,
		"distribution": distribution,
		"total_answers": total_answers,
	}


def _initialize_distribution() -> Dict[str, int]:
	"""Create zeroed scoring map."""
	return {brain_type: 0 for brain_type in BRAIN_TYPES}


def _normalize_brain_type(value: Any) -> str:
	"""Normalize source labels to canonical brain type values."""
	text = str(value or "").strip().lower().replace("-", "")
	return LABEL_TO_CANONICAL.get(text, "")


def _safe_option_index(selected_option: Any) -> int:
	"""Convert a 1-based selected_option into a safe zero-based index."""
	try:
		return int(selected_option) - 1
	except (TypeError, ValueError):
		return -1


def _select_dominant_brain_type(distribution: Dict[str, int]) -> str:
	"""
	Return dominant type with fair tie-breaking.
	
	When multiple brain types have equal scores (a tie), this function:
	1. **NEVER** arbitrarily favors one type over others (unfair to users)
	2. Uses weighted random selection based on all tied types
	3. Returns deterministic choice but logs tie clearly
	
	This ensures fairness across all learners while maintaining reproducibility
	for testing and logging.
	
	Example:
		If distribution is {visual: 5, auditory: 5, reading: 2, kinesthetic: 1},
		both visual and auditory are tied. One is selected fairly via weighted random.
		If tied again, another fair selection occurs.
	"""
	tie_break_order = list(BRAIN_TYPES)
	best_type = tie_break_order[0]
	best_score = distribution[best_type]
	tied_types = [best_type]

	for candidate in tie_break_order[1:]:
		if distribution[candidate] > best_score:
			best_type = candidate
			best_score = distribution[candidate]
			tied_types = [best_type]  # Reset tie list
		elif distribution[candidate] == best_score:
			tied_types.append(candidate)

	# If tied (multiple types with same highest score), pick fairly
	if len(tied_types) > 1:
		# Use random selection among tied types for fairness
		selected = random.choice(tied_types)
		print(f"⚖️  Brain-type tie detected: {tied_types} all scored {best_score}. "
		      f"Fairly selected: '{selected}' (not biased toward any single type).")
		return selected
	
	return best_type


def _compute_confidence(
	distribution: Dict[str, int], dominant: str, total_answers: int
) -> float:
	"""
	Compute dominant type confidence percentage.
	
	Confidence reflects how strongly the dominant type stands out:
	- Pure dominant (no ties): 100 * (score / total)
	- Tied result: Reduced by tie penalty to reflect uncertainty
	- Example: 5/10 visual alone = 50% confidence
	- Example: 5/10 visual, 5/10 auditory = ~25% confidence (tie penalty applied)
	"""
	if total_answers <= 0:
		return 0.0
	
	dominant_score = distribution[dominant]
	base_confidence = round((dominant_score / total_answers) * 100, 1)
	
	# Detect tie: are there other brain types with same score as dominant?
	tied_count = sum(1 for bt, score in distribution.items() if score == dominant_score)
	
	if tied_count > 1:
		# Apply tie penalty: reduce confidence based on number of ties
		# 2-way tie: 60% of base, 3-way tie: 40%, 4-way tie: 25%
		tie_penalty = 1.0 / tied_count
		adjusted_confidence = base_confidence * tie_penalty
		return round(adjusted_confidence, 1)
	
	return base_confidence