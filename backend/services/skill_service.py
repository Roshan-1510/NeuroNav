"""Skill graph service for goal-aware deterministic roadmap generation."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List


DATA_ANALYST_SKILLS: List[Dict[str, Any]] = [
	{
		"id": "da-01",
		"name": "Data Literacy Fundamentals",
		"prerequisites": [],
		"difficulty": "beginner",
	},
	{
		"id": "da-02",
		"name": "Spreadsheet Analysis",
		"prerequisites": ["da-01"],
		"difficulty": "beginner",
	},
	{
		"id": "da-03",
		"name": "SQL for Data Querying",
		"prerequisites": ["da-01"],
		"difficulty": "beginner",
	},
	{
		"id": "da-04",
		"name": "Statistics for Analysis",
		"prerequisites": ["da-01"],
		"difficulty": "intermediate",
	},
	{
		"id": "da-05",
		"name": "Python for Data Analysis",
		"prerequisites": ["da-02", "da-03"],
		"difficulty": "intermediate",
	},
	{
		"id": "da-06",
		"name": "Data Cleaning and Preparation",
		"prerequisites": ["da-03", "da-05"],
		"difficulty": "intermediate",
	},
	{
		"id": "da-07",
		"name": "Data Visualization",
		"prerequisites": ["da-04", "da-06"],
		"difficulty": "intermediate",
	},
	{
		"id": "da-08",
		"name": "A/B Testing and Experimentation",
		"prerequisites": ["da-04", "da-06"],
		"difficulty": "advanced",
	},
	{
		"id": "da-09",
		"name": "Dashboarding and BI Tools",
		"prerequisites": ["da-06", "da-07"],
		"difficulty": "advanced",
	},
	{
		"id": "da-10",
		"name": "Business Case Analysis",
		"prerequisites": ["da-07", "da-08", "da-09"],
		"difficulty": "advanced",
	},
]


DESIGN_SKILLS: List[Dict[str, Any]] = [
	{
		"id": "ds-01",
		"name": "Design Foundations",
		"prerequisites": [],
		"difficulty": "beginner",
	},
	{
		"id": "ds-02",
		"name": "Color, Typography, and Composition",
		"prerequisites": ["ds-01"],
		"difficulty": "beginner",
	},
	{
		"id": "ds-03",
		"name": "UX Research and Problem Framing",
		"prerequisites": ["ds-01"],
		"difficulty": "beginner",
	},
	{
		"id": "ds-04",
		"name": "Information Architecture and User Flows",
		"prerequisites": ["ds-03"],
		"difficulty": "intermediate",
	},
	{
		"id": "ds-05",
		"name": "Wireframing and Interaction Patterns",
		"prerequisites": ["ds-02", "ds-04"],
		"difficulty": "intermediate",
	},
	{
		"id": "ds-06",
		"name": "High-Fidelity UI Design",
		"prerequisites": ["ds-05"],
		"difficulty": "intermediate",
	},
	{
		"id": "ds-07",
		"name": "Prototyping and Micro-Interactions",
		"prerequisites": ["ds-06"],
		"difficulty": "intermediate",
	},
	{
		"id": "ds-08",
		"name": "Usability Testing and Iteration",
		"prerequisites": ["ds-07"],
		"difficulty": "advanced",
	},
	{
		"id": "ds-09",
		"name": "Design Systems and Accessibility",
		"prerequisites": ["ds-06", "ds-08"],
		"difficulty": "advanced",
	},
	{
		"id": "ds-10",
		"name": "Portfolio Case Study and Critique",
		"prerequisites": ["ds-09"],
		"difficulty": "advanced",
	},
]


GOAL_ALIASES: Dict[str, str] = {
	"data analyst": "data analyst",
	"data analysis": "data analyst",
	"data science": "data analyst",
	"analyst": "data analyst",
	"machine learning": "data analyst",
	"ml": "data analyst",
	"programming": "data analyst",
	"web development": "data analyst",
	"business": "data analyst",
	"design": "design",
	"ui ux design": "design",
	"ui/ux design": "design",
	"ux design": "design",
	"product design": "design",
	"ui design": "design",
}


GOAL_SKILL_GRAPHS: Dict[str, List[Dict[str, Any]]] = {
	"data analyst": DATA_ANALYST_SKILLS,
	"design": DESIGN_SKILLS,
}


def get_data_analyst_skill_graph() -> List[Dict[str, Any]]:
	"""Return the deterministic Data Analyst skill graph."""
	validate_skill_graph(DATA_ANALYST_SKILLS)
	return [
		{
			"id": skill["id"],
			"name": skill["name"],
			"prerequisites": list(skill["prerequisites"]),
			"difficulty": skill["difficulty"],
		}
		for skill in DATA_ANALYST_SKILLS
	]



def get_design_skill_graph() -> List[Dict[str, Any]]:
	"""Return the deterministic Design skill graph."""
	validate_skill_graph(DESIGN_SKILLS)
	return [
		{
			"id": skill["id"],
			"name": skill["name"],
			"prerequisites": list(skill["prerequisites"]),
			"difficulty": skill["difficulty"],
		}
		for skill in DESIGN_SKILLS
	]



def normalize_goal(goal: str) -> str:
	"""Normalize goal text into a supported canonical goal key."""
	normalized = " ".join((goal or "").strip().lower().split())
	if normalized in GOAL_ALIASES:
		return GOAL_ALIASES[normalized]

	# Keyword-based normalization for common user-entered variants.
	if "design" in normalized or "ux" in normalized or "ui" in normalized:
		return "design"

	if any(keyword in normalized for keyword in ("data", "analyst", "machine learning", "ml", "python", "business", "web", "programming")):
		return "data analyst"

	# Safe default so roadmap fetch/regenerate never fails on unknown legacy goals.
	return "data analyst"


def get_skill_graph_for_goal(goal: str) -> List[Dict[str, Any]]:
	"""Return skill graph for a supported goal."""
	canonical_goal = normalize_goal(goal)
	if canonical_goal not in GOAL_SKILL_GRAPHS:
		canonical_goal = "data analyst"

	skills = GOAL_SKILL_GRAPHS[canonical_goal]
	validate_skill_graph(skills)
	return [
		{
			"id": skill["id"],
			"name": skill["name"],
			"prerequisites": list(skill["prerequisites"]),
			"difficulty": skill["difficulty"],
		}
		for skill in skills
	]


def get_ordered_skills_for_goal(goal: str) -> List[Dict[str, Any]]:
	"""Return topologically ordered skills for a supported goal."""
	return resolve_skill_order(get_skill_graph_for_goal(goal))
def get_ordered_data_analyst_skills() -> List[Dict[str, Any]]:
	"""Return Data Analyst skills sorted by prerequisites."""
	return resolve_skill_order(get_data_analyst_skill_graph())


def validate_skill_graph(skills: List[Dict[str, Any]]) -> None:
	"""Ensure each skill has required fields and valid dependencies."""
	required_fields = {"id", "name", "prerequisites", "difficulty"}
	allowed_difficulties = {"beginner", "intermediate", "advanced"}

	skill_ids = set()
	for skill in skills:
		missing_fields = required_fields - set(skill.keys())
		if missing_fields:
			missing = ", ".join(sorted(missing_fields))
			raise ValueError(f"Skill definition missing fields: {missing}")

		skill_id = skill["id"]
		if skill_id in skill_ids:
			raise ValueError(f"Duplicate skill id found: {skill_id}")
		skill_ids.add(skill_id)

		if not isinstance(skill["prerequisites"], list):
			raise ValueError(f"Skill prerequisites must be a list: {skill_id}")

		if skill["difficulty"] not in allowed_difficulties:
			raise ValueError(
				f"Invalid difficulty for {skill_id}: {skill['difficulty']}"
			)

	for skill in skills:
		for prereq in skill["prerequisites"]:
			if prereq not in skill_ids:
				raise ValueError(
					f"Skill {skill['id']} references unknown prerequisite: {prereq}"
				)


def resolve_skill_order(skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
	"""Topologically sort skills so prerequisites always appear first."""
	validate_skill_graph(skills)

	by_id = {skill["id"]: skill for skill in skills}
	in_degree = {skill["id"]: 0 for skill in skills}
	edges = defaultdict(list)

	for skill in skills:
		current = skill["id"]
		for prereq in skill["prerequisites"]:
			edges[prereq].append(current)
			in_degree[current] += 1

	# Stable deterministic ordering when multiple nodes have in-degree zero.
	queue = deque(sorted([skill_id for skill_id, degree in in_degree.items() if degree == 0]))
	ordered_ids: List[str] = []

	while queue:
		node = queue.popleft()
		ordered_ids.append(node)

		for neighbor in sorted(edges[node]):
			in_degree[neighbor] -= 1
			if in_degree[neighbor] == 0:
				queue.append(neighbor)

	if len(ordered_ids) != len(skills):
		raise ValueError("Skill graph contains a cycle and cannot be ordered")

	return [
		{
			"id": by_id[skill_id]["id"],
			"name": by_id[skill_id]["name"],
			"prerequisites": list(by_id[skill_id]["prerequisites"]),
			"difficulty": by_id[skill_id]["difficulty"],
		}
		for skill_id in ordered_ids
	]