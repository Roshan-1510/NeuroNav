"""Deterministic content mapping service for roadmap generation."""

from __future__ import annotations

from typing import Dict, List

try:
	from services.skill_service import get_data_analyst_skill_graph, get_design_skill_graph
except ImportError:  # pragma: no cover - supports package import style
	from .skill_service import get_data_analyst_skill_graph, get_design_skill_graph


CONTENT_TYPES = ("video", "article", "project")


LEARNING_RESOURCE_CATALOG: Dict[str, Dict[str, Dict[str, str]]] = {
	"da-01": {
		"video": {
			"title": "StatQuest - Data Literacy Foundations",
			"url": "https://www.youtube.com/c/joshstarmer",
			"resource_type": "video",
		},
		"article": {
			"title": "Python Data Science Handbook",
			"url": "https://jakevdp.github.io/PythonDataScienceHandbook/",
			"resource_type": "article",
		},
		"project": {
			"title": "Kaggle Learn - Data Science Foundations",
			"url": "https://www.kaggle.com/learn",
			"resource_type": "project",
		},
	},
	"da-02": {
		"video": {
			"title": "Spreadsheet Analysis Walkthrough",
			"url": "https://www.youtube.com/c/TraversyMedia",
			"resource_type": "video",
		},
		"article": {
			"title": "Google Sheets Functions Guide",
			"url": "https://support.google.com/docs/answer/161684?hl=en",
			"resource_type": "article",
		},
		"project": {
			"title": "Build a Sales Analysis Workbook",
			"url": "https://www.kaggle.com/learn/pandas",
			"resource_type": "project",
		},
	},
	"da-03": {
		"video": {
			"title": "SQL Querying Explained",
			"url": "https://www.youtube.com/c/joshstarmer",
			"resource_type": "video",
		},
		"article": {
			"title": "SQLBolt Interactive SQL Tutorial",
			"url": "https://sqlbolt.com/",
			"resource_type": "article",
		},
		"project": {
			"title": "Mode SQL Tutorial Practice",
			"url": "https://mode.com/sql-tutorial/",
			"resource_type": "project",
		},
	},
	"da-04": {
		"video": {
			"title": "Statistics for Analysts with StatQuest",
			"url": "https://www.youtube.com/c/joshstarmer",
			"resource_type": "video",
		},
		"article": {
			"title": "Khan Academy Statistics & Probability",
			"url": "https://www.khanacademy.org/math/statistics-probability",
			"resource_type": "article",
		},
		"project": {
			"title": "Kaggle Intro to Statistics Practice",
			"url": "https://www.kaggle.com/learn/intro-to-statistics",
			"resource_type": "project",
		},
	},
	"da-05": {
		"video": {
			"title": "Python for Data Analysis Walkthrough",
			"url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
			"resource_type": "video",
		},
		"article": {
			"title": "Python Data Science Handbook",
			"url": "https://jakevdp.github.io/PythonDataScienceHandbook/",
			"resource_type": "article",
		},
		"project": {
			"title": "Kaggle Learn Python",
			"url": "https://www.kaggle.com/learn/python",
			"resource_type": "project",
		},
	},
	"da-06": {
		"video": {
			"title": "Data Cleaning Techniques Explained",
			"url": "https://www.youtube.com/c/joshstarmer",
			"resource_type": "video",
		},
		"article": {
			"title": "Pandas User Guide",
			"url": "https://pandas.pydata.org/docs/",
			"resource_type": "article",
		},
		"project": {
			"title": "Kaggle Data Cleaning Practice",
			"url": "https://www.kaggle.com/learn/data-cleaning",
			"resource_type": "project",
		},
	},
	"da-07": {
		"video": {
			"title": "Data Visualization Storytelling",
			"url": "https://www.youtube.com/c/joshstarmer",
			"resource_type": "video",
		},
		"article": {
			"title": "Data to Viz Chart Selection Guide",
			"url": "https://www.data-to-viz.com/",
			"resource_type": "article",
		},
		"project": {
			"title": "Kaggle Data Visualization Project",
			"url": "https://www.kaggle.com/learn/data-visualization",
			"resource_type": "project",
		},
	},
	"da-08": {
		"video": {
			"title": "A/B Testing Explained",
			"url": "https://www.youtube.com/c/joshstarmer",
			"resource_type": "video",
		},
		"article": {
			"title": "A/B Testing Foundations",
			"url": "https://www.optimizely.com/optimization-glossary/ab-testing/",
			"resource_type": "article",
		},
		"project": {
			"title": "Experiment Design Practice",
			"url": "https://www.kaggle.com/competitions",
			"resource_type": "project",
		},
	},
	"da-09": {
		"video": {
			"title": "Dashboarding and BI Tools Demo",
			"url": "https://www.youtube.com/c/PowerBI",
			"resource_type": "video",
		},
		"article": {
			"title": "BI Modeling and KPI Tracking",
			"url": "https://powerbi.microsoft.com/en-us/getting-started-with-power-bi/",
			"resource_type": "article",
		},
		"project": {
			"title": "Build a BI Dashboard",
			"url": "https://powerbi.microsoft.com/en-us/getting-started-with-power-bi/",
			"resource_type": "project",
		},
	},
	"da-10": {
		"video": {
			"title": "Business Case Analysis Framework",
			"url": "https://www.youtube.com/c/joshstarmer",
			"resource_type": "video",
		},
		"article": {
			"title": "Communicating Data Insights",
			"url": "https://www.storytellingwithdata.com/blog",
			"resource_type": "article",
		},
		"project": {
			"title": "Present a Recommendation Deck",
			"url": "https://www.kaggle.com/learn",
			"resource_type": "project",
		},
	},
}


RESOURCE_FALLBACK_BY_TYPE: Dict[str, Dict[str, str]] = {
	"video": {
		"title": "Data Analyst Video Learning Hub",
		"url": "https://www.youtube.com/c/joshstarmer",
		"resource_type": "video",
	},
	"article": {
		"title": "Data Analyst Reading Guide",
		"url": "https://www.khanacademy.org/math/statistics-probability",
		"resource_type": "article",
	},
	"project": {
		"title": "Hands-on Practice Hub",
		"url": "https://www.kaggle.com/learn",
		"resource_type": "project",
	},
}


DESIGN_RESOURCE_FALLBACK_BY_TYPE: Dict[str, Dict[str, str]] = {
	"video": {
		"title": "Design Video Learning Hub",
		"url": "https://www.youtube.com/c/thefuturishere",
		"resource_type": "video",
	},
	"article": {
		"title": "Design Reading Guide",
		"url": "https://www.nngroup.com/articles/",
		"resource_type": "article",
	},
	"project": {
		"title": "Design Practice Projects",
		"url": "https://www.frontendmentor.io/challenges",
		"resource_type": "project",
	},
}


DATA_ANALYST_CONTENT_MAP: Dict[str, Dict[str, str]] = {
	"da-01": {
		"video": "Intro to Data Literacy (video lesson)",
		"article": "Data Literacy Basics (read)",
		"project": "Define KPIs for a sample product",
	},
	"da-02": {
		"video": "Spreadsheet Analysis Essentials (walkthrough)",
		"article": "Spreadsheet Functions and Pivot Tables",
		"project": "Build a sales analysis workbook",
	},
	"da-03": {
		"video": "SQL Query Patterns for Analysts",
		"article": "SQL SELECT, JOIN, GROUP BY Guide",
		"project": "Answer business questions with SQL",
	},
	"da-04": {
		"video": "Statistics for Analysts (concept visuals)",
		"article": "Descriptive and Inferential Stats",
		"project": "Analyze A/B test summary metrics",
	},
	"da-05": {
		"video": "Python Data Analysis Workflow",
		"article": "Pandas Fundamentals for Analysis",
		"project": "Clean and analyze CSV datasets",
	},
	"da-06": {
		"video": "Data Cleaning Techniques",
		"article": "Handling Missing Data and Outliers",
		"project": "Prepare messy data for reporting",
	},
	"da-07": {
		"video": "Data Visualization Storytelling",
		"article": "Chart Selection and Dashboard Design",
		"project": "Create a stakeholder-ready dashboard",
	},
	"da-08": {
		"video": "A/B Testing in Practice",
		"article": "Experiment Design and Hypothesis Testing",
		"project": "Design and evaluate an experiment",
	},
	"da-09": {
		"video": "BI Tools End-to-End Demo",
		"article": "BI Modeling and KPI Tracking",
		"project": "Build a BI dashboard for operations",
	},
	"da-10": {
		"video": "Business Case Analysis Framework",
		"article": "Communicating Data Insights",
		"project": "Present a recommendation deck",
	},
}


DESIGN_CONTENT_MAP: Dict[str, Dict[str, str]] = {
	"ds-01": {
		"video": "Design principles foundations walkthrough",
		"article": "Principles of visual hierarchy and gestalt",
		"project": "Audit 3 interfaces and identify principle usage",
	},
	"ds-02": {
		"video": "Color and typography systems tutorial",
		"article": "Type scale, contrast, and composition guide",
		"project": "Create a style tile and component moodboard",
	},
	"ds-03": {
		"video": "UX research interviews and synthesis demo",
		"article": "Problem framing and JTBD methods",
		"project": "Run 3 user interviews and produce insight summary",
	},
	"ds-04": {
		"video": "Information architecture and user flow mapping",
		"article": "Task flow vs user flow practical guide",
		"project": "Design end-to-end flow for a product task",
	},
	"ds-05": {
		"video": "Wireframing patterns and interaction decisions",
		"article": "Interaction patterns and usability heuristics",
		"project": "Build low-fidelity wireframes for 5 core screens",
	},
	"ds-06": {
		"video": "High-fidelity UI in Figma workflow",
		"article": "Visual systems and consistency checklist",
		"project": "Design a polished high-fidelity screen set",
	},
	"ds-07": {
		"video": "Prototyping and motion principles",
		"article": "Micro-interactions and transition design",
		"project": "Create interactive prototype with key transitions",
	},
	"ds-08": {
		"video": "Usability test planning and execution",
		"article": "Moderated testing and issue prioritization",
		"project": "Run usability test and synthesize findings",
	},
	"ds-09": {
		"video": "Design systems and accessibility deep dive",
		"article": "WCAG and component system architecture",
		"project": "Build accessible component library starter",
	},
	"ds-10": {
		"video": "Portfolio storytelling and critique sessions",
		"article": "How to write strong design case studies",
		"project": "Publish one portfolio case study end-to-end",
	},
}


DESIGN_RESOURCE_CATALOG: Dict[str, Dict[str, Dict[str, str]]] = {
	"ds-01": {
		"video": {"title": "Design Principles Explained", "url": "https://www.youtube.com/watch?v=_o0zH6s2M8Y", "resource_type": "video"},
		"article": {"title": "Nielsen Norman UX Articles", "url": "https://www.nngroup.com/articles/", "resource_type": "article"},
		"project": {"title": "UI Design Daily Briefs", "url": "https://www.uidesigndaily.com/", "resource_type": "project"},
	},
	"ds-02": {
		"video": {"title": "Typography in UI Design", "url": "https://www.youtube.com/c/thefuturishere", "resource_type": "video"},
		"article": {"title": "Refactoring UI - Visual Design Guide", "url": "https://www.refactoringui.com/", "resource_type": "article"},
		"project": {"title": "Color Palette Practice", "url": "https://coolors.co/", "resource_type": "project"},
	},
	"ds-03": {
		"video": {"title": "UX Research Fundamentals", "url": "https://www.youtube.com/c/NNgroup", "resource_type": "video"},
		"article": {"title": "UX Research Methods", "url": "https://www.interaction-design.org/literature/topics/ux-research", "resource_type": "article"},
		"project": {"title": "Interview Script Builder", "url": "https://maze.co/", "resource_type": "project"},
	},
	"ds-04": {
		"video": {"title": "User Flow Mapping", "url": "https://www.youtube.com/c/designcourse", "resource_type": "video"},
		"article": {"title": "Information Architecture Basics", "url": "https://www.nngroup.com/topic/information-architecture/", "resource_type": "article"},
		"project": {"title": "Flow Diagram Exercise", "url": "https://whimsical.com/", "resource_type": "project"},
	},
	"ds-05": {
		"video": {"title": "Wireframing and UX Patterns", "url": "https://www.youtube.com/c/fluxacademy", "resource_type": "video"},
		"article": {"title": "Usability Heuristics", "url": "https://www.nngroup.com/articles/ten-usability-heuristics/", "resource_type": "article"},
		"project": {"title": "Wireframe Challenge", "url": "https://www.frontendmentor.io/challenges", "resource_type": "project"},
	},
	"ds-06": {
		"video": {"title": "Figma UI Design Workflow", "url": "https://www.youtube.com/c/Figmadesign", "resource_type": "video"},
		"article": {"title": "UI Design Best Practices", "url": "https://www.smashingmagazine.com/category/user-experience/", "resource_type": "article"},
		"project": {"title": "High-Fidelity Screen Sprint", "url": "https://dribbble.com/", "resource_type": "project"},
	},
	"ds-07": {
		"video": {"title": "Prototyping Interactions", "url": "https://www.youtube.com/c/Figmadesign", "resource_type": "video"},
		"article": {"title": "Microinteraction Patterns", "url": "https://www.nngroup.com/articles/", "resource_type": "article"},
		"project": {"title": "Prototype Drill", "url": "https://www.figma.com/community", "resource_type": "project"},
	},
	"ds-08": {
		"video": {"title": "Usability Testing Walkthrough", "url": "https://www.youtube.com/c/NNgroup", "resource_type": "video"},
		"article": {"title": "Usability Testing Guide", "url": "https://www.usability.gov/how-to-and-tools/methods/usability-testing.html", "resource_type": "article"},
		"project": {"title": "Maze Testing Project", "url": "https://maze.co/", "resource_type": "project"},
	},
	"ds-09": {
		"video": {"title": "Design Systems in Practice", "url": "https://www.youtube.com/c/designsystems", "resource_type": "video"},
		"article": {"title": "W3C WAI Accessibility Intro", "url": "https://www.w3.org/WAI/fundamentals/accessibility-intro/", "resource_type": "article"},
		"project": {"title": "Accessible Component Build", "url": "https://www.a11yproject.com/", "resource_type": "project"},
	},
	"ds-10": {
		"video": {"title": "Portfolio Case Study Reviews", "url": "https://www.youtube.com/c/thefuturishere", "resource_type": "video"},
		"article": {"title": "UX Portfolio Case Study Guide", "url": "https://www.nngroup.com/articles/ux-portfolio/", "resource_type": "article"},
		"project": {"title": "Case Study Publishing Sprint", "url": "https://www.behance.net/", "resource_type": "project"},
	},
}


def get_data_analyst_content_mapping() -> Dict[str, Dict[str, str]]:
	"""Return structured mapping skill_id -> content options."""
	validate_content_mapping(DATA_ANALYST_CONTENT_MAP)
	return {
		skill_id: dict(content_options)
		for skill_id, content_options in DATA_ANALYST_CONTENT_MAP.items()
	}


def get_content_options_for_skill(skill_id: str) -> Dict[str, str]:
	"""Return content options for a single skill id."""
	content_mapping = DESIGN_CONTENT_MAP if str(skill_id).startswith("ds-") else get_data_analyst_content_mapping()
	if skill_id not in content_mapping:
		raise ValueError(f"Missing content mapping for skill: {skill_id}")
	return dict(content_mapping[skill_id])


def get_learning_resource_for_skill(skill_id: str, content_type: str) -> Dict[str, str]:
	"""Return a curated learning resource object for a skill and content type."""
	normalized_content_type = _normalize_content_type(content_type)
	resource_catalog = DESIGN_RESOURCE_CATALOG if str(skill_id).startswith("ds-") else LEARNING_RESOURCE_CATALOG
	fallback_catalog = DESIGN_RESOURCE_FALLBACK_BY_TYPE if str(skill_id).startswith("ds-") else RESOURCE_FALLBACK_BY_TYPE

	if skill_id not in resource_catalog:
		fallback_type = normalized_content_type if normalized_content_type in fallback_catalog else "article"
		return dict(fallback_catalog[fallback_type])

	resource_bundle = resource_catalog[skill_id]
	if normalized_content_type not in resource_bundle:
		fallback_type = "article" if "article" in resource_bundle else next(iter(resource_bundle))
		resource = dict(resource_bundle[fallback_type])
		resource["url"] = _normalize_external_url(resource.get("url", ""), fallback_type)
		return resource

	resource = dict(resource_bundle[normalized_content_type])
	resource["url"] = _normalize_external_url(resource.get("url", ""), normalized_content_type)
	if not _looks_valid_external_url(resource["url"]):
		fallback_type = normalized_content_type if normalized_content_type in fallback_catalog else "article"
		return dict(fallback_catalog[fallback_type])

	return resource


def _normalize_content_type(content_type: str) -> str:
	"""Map aliases from AI output into catalog-supported content types."""
	normalized = str(content_type or "").strip().lower()
	mapping = {
		"lecture": "video",
		"podcast": "video",
		"diagram": "video",
		"documentation": "article",
		"exercise": "project",
	}
	return mapping.get(normalized, normalized)


def _normalize_external_url(url: str, content_type: str) -> str:
	"""Return a safe external URL with scheme and fallback when malformed."""
	normalized = str(url or "").strip()
	if not normalized:
		fallback = RESOURCE_FALLBACK_BY_TYPE.get(content_type, RESOURCE_FALLBACK_BY_TYPE["article"])
		return fallback["url"]

	if normalized.startswith("www."):
		normalized = f"https://{normalized}"
	elif not normalized.startswith("http://") and not normalized.startswith("https://"):
		normalized = f"https://{normalized}"

	return normalized


def _looks_valid_external_url(url: str) -> bool:
	"""Basic URL validity guard to avoid blank tabs from malformed links."""
	normalized = str(url or "").strip().lower()
	return normalized.startswith("http://") or normalized.startswith("https://")


def validate_content_mapping(mapping: Dict[str, Dict[str, str]]) -> None:
	"""Validate expected content types and full skill coverage."""
	skill_ids: List[str] = [skill["id"] for skill in get_data_analyst_skill_graph()]

	for skill_id in skill_ids:
		if skill_id not in mapping:
			raise ValueError(f"Content mapping missing skill id: {skill_id}")

		options = mapping[skill_id]
		for content_type in CONTENT_TYPES:
			if content_type not in options:
				raise ValueError(
					f"Skill {skill_id} missing required content type: {content_type}"
				)

			if not options[content_type] or not isinstance(options[content_type], str):
				raise ValueError(
					f"Skill {skill_id} has invalid content for type: {content_type}"
				)

	for skill_id in mapping:
		if skill_id not in skill_ids:
			raise ValueError(f"Content mapping contains unknown skill id: {skill_id}")