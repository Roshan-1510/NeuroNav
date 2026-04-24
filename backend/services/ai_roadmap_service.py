"""LLM-first roadmap service with strict JSON validation and safe fallback."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib import error, request
import sys

from bson import ObjectId

try:
    from services.roadmap_service import generate_roadmap as _generate_rule_based_roadmap
    from services.skill_service import get_ordered_skills_for_goal, normalize_goal
    from services.content_service import get_learning_resource_for_skill
    from services.neuronav_engine import enrich_roadmap_steps
except ImportError:  # pragma: no cover - supports package import style
    from .roadmap_service import generate_roadmap as _generate_rule_based_roadmap
    from .skill_service import get_ordered_skills_for_goal, normalize_goal
    from .content_service import get_learning_resource_for_skill
    from .neuronav_engine import enrich_roadmap_steps


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")


def generate_roadmap(
    goal: str,
    brain_type: str,
    skill_level: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Generate a roadmap via LLM; fallback to rule-based if response is invalid."""
    _ = skill_level

    try:
        print(f"🚀 Attempting LLM roadmap generation for goal='{goal}', brain_type='{brain_type}'", file=sys.stderr)
        response_text = _call_openrouter(goal=goal, brain_type=brain_type)
        print(f"✅ LLM response received", file=sys.stderr)
        parsed_steps = _parse_and_validate_steps(response_text, brain_type)
        print(f"✅ Steps validated: {len(parsed_steps)} steps", file=sys.stderr)
        normalized = _normalize_steps(parsed_steps, goal, brain_type)
        return enrich_roadmap_steps(
            steps=normalized,
            goal=goal,
            brain_type=brain_type,
            source="llm",
        )
    except Exception as e:
        print(f"❌ LLM generation failed: {str(e)}", file=sys.stderr)
        print(f"🔄 Falling back to rule-based generation", file=sys.stderr)
        return _generate_rule_based_roadmap(goal=goal, brain_type=brain_type)


def build_ai_roadmap_document(
    user_id: str,
    goal: str,
    brain_type: str,
    roadmap: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build MongoDB roadmap document with required AI schema fields."""
    normalized_user_id: Any = user_id
    if isinstance(user_id, str):
        stripped = user_id.strip()
        if ObjectId.is_valid(stripped):
            normalized_user_id = ObjectId(stripped)
        else:
            normalized_user_id = stripped

    return {
        "user_id": normalized_user_id,
        "goal": goal,
        "topic": goal,
        "brain_type": brain_type,
        "roadmap": roadmap,
        "steps": roadmap,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "source": "ai",
    }


def save_ai_roadmap(
    db: Any,
    user_id: str,
    goal: str,
    brain_type: str,
    roadmap: List[Dict[str, Any]],
) -> str:
    """Persist AI roadmap in MongoDB and return inserted roadmap id."""
    document = build_ai_roadmap_document(
        user_id=user_id,
        goal=goal,
        brain_type=brain_type,
        roadmap=roadmap,
    )
    result = db.roadmaps.insert_one(document)
    return str(result.inserted_id)


def generate_and_save_roadmap(
    db: Any,
    user_id: str,
    goal: str,
    brain_type: str,
    skill_level: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate roadmap and persist it using the required AI schema."""
    steps = generate_roadmap(goal=goal, brain_type=brain_type, skill_level=skill_level)
    roadmap_id = save_ai_roadmap(
        db=db,
        user_id=user_id,
        goal=goal,
        brain_type=brain_type,
        roadmap=steps,
    )
    return {
        "roadmap_id": roadmap_id,
        "goal": goal,
        "brain_type": brain_type,
        "source": "ai",
        "total_steps": len(steps),
        "steps": steps,
    }


def _call_openrouter(goal: str, brain_type: str) -> str:
    """Call OpenRouter and return assistant text content."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    print(f"📝 Building prompt for goal='{goal}', brain_type='{brain_type}'", file=sys.stderr)
    prompt = _build_prompt(goal, brain_type)
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a roadmap generator. Return valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }

    print(f"🔗 Calling OpenRouter API at {OPENROUTER_URL}", file=sys.stderr)
    print(f"📦 Model: {DEFAULT_MODEL}", file=sys.stderr)
    
    req = request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print(f"✅ OpenRouter API response received (status: {resp.status})", file=sys.stderr)
    except error.URLError as exc:
        print(f"❌ OpenRouter API error: {exc}", file=sys.stderr)
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc
    except Exception as exc:
        print(f"❌ Unexpected error calling OpenRouter: {exc}", file=sys.stderr)
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    try:
        response_json = json.loads(body)
    except json.JSONDecodeError as exc:
        print(f"❌ Failed to parse OpenRouter response as JSON: {exc}", file=sys.stderr)
        print(f"Response body: {body[:500]}", file=sys.stderr)
        raise RuntimeError(f"OpenRouter response is not valid JSON: {exc}") from exc
    
    choices = response_json.get("choices", [])
    if not choices:
        error_msg = response_json.get("error", {}).get("message", "Unknown error")
        print(f"❌ OpenRouter error response: {error_msg}", file=sys.stderr)
        raise RuntimeError(f"OpenRouter response missing choices. Error: {error_msg}")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("OpenRouter response content is empty")

    return content


def _build_prompt(goal: str, brain_type: str) -> str:
    """Build detailed brain-type-specific roadmap prompt."""
    normalized_brain_type = str(brain_type).strip().lower()
    target_steps = _target_step_count(goal, normalized_brain_type)
    
    # Brain-type specific learning strategies and instructions
    brain_type_details = {
        "visual": {
            "strategy": "Focus on visual content with diagrams, flowcharts, and videos",
            "instruction": "Each step MUST emphasize visual learning: diagrams, flowcharts, color-coded content, screenshots, mindmaps, infographics.",
            "content_types": "video, diagram",
            "roadmap_arc": "Start with concept maps, then visual pattern recognition, then model/process diagrams, then dashboard storytelling, then portfolio visuals.",
            "example_title": "Understanding Data Pipelines with Flowcharts",
            "example_description": "Learn how data flows through ETL pipelines using visual diagrams and screen recordings showing real-world pipeline architectures.",
        },
        "auditory": {
            "strategy": "Focus on lectures, discussions, and audio content",
            "instruction": "Each step MUST emphasize learning through listening and discussion: podcasts, recorded lectures, webinars, discussion forums, verbal explanations.",
            "content_types": "lecture, podcast",
            "roadmap_arc": "Start with listen-first foundations, then guided audio explanations, then peer discussion, then explain-back sessions, then spoken case analysis.",
            "example_title": "Data Analysis Fundamentals Through Expert Lectures",
            "example_description": "Listen to recorded lectures from data science experts explaining core concepts, interview discussions with analysts, and webinar recordings.",
        },
        "reading": {
            "strategy": "Focus on articles, documentation, and text-based learning",
            "instruction": "Each step MUST emphasize reading and writing: comprehensive articles, technical documentation, research papers, detailed guides, written tutorials.",
            "content_types": "article, documentation",
            "roadmap_arc": "Start with core reading, then annotation and note synthesis, then technical documentation deep dives, then written analysis, then publishable summaries.",
            "example_title": "SQL Query Optimization - Complete Guide",
            "example_description": "Read comprehensive articles and documentation about SQL optimization techniques, best practices, and case studies.",
        },
        "kinesthetic": {
            "strategy": "Focus on hands-on projects, exercises, and practical application",
            "instruction": "Each step MUST be project-based and hands-on: build real projects, write code, perform data analysis, create dashboards, solve real problems.",
            "content_types": "project, exercise",
            "roadmap_arc": "Start with quick practical drills, then guided mini-builds, then debugging tasks, then end-to-end implementation, then real-world deployment practice.",
            "example_title": "Build Your First Data Analysis Project",
            "example_description": "Create an end-to-end data analysis project from data collection through visualization, using real datasets and solving real business problems.",
        },
    }
    
    details = brain_type_details.get(normalized_brain_type, brain_type_details["visual"])
    
    return f"""Generate a personalized learning roadmap for someone with a {normalized_brain_type.upper()} learning style.

GOAL: {goal}
LEARNING STYLE: {normalized_brain_type.upper()}

INSTRUCTIONS:
1. Create a step-by-step learning roadmap with exactly {target_steps} practical steps
2. {details['instruction']}
3. Each step must have: step (integer), title (string), description (string), content_type (string)
4. Content types MUST be one of: {details['content_types']}
5. Descriptions must emphasize HOW this learner should approach each topic based on their {normalized_brain_type} learning style
6. Make titles specific and engaging for {normalized_brain_type} learners
7. Use this roadmap progression: {details['roadmap_arc']}
8. At least 5 step titles must explicitly contain words strongly associated with {normalized_brain_type} learning methods
9. Return ONLY valid JSON array, no markdown or extra text
10. Include at least 1 step explicitly labeled as a capstone or portfolio-ready outcome

EXAMPLE for {normalized_brain_type} learner:
{{"step": 1, "title": "{details['example_title']}", "description": "{details['example_description']}", "content_type": "{details['content_types'].split(',')[0].strip()}"}}

Generate the roadmap for goal: {goal}
Return valid JSON array only:"""



def _parse_and_validate_steps(content: str, brain_type: str) -> List[Dict[str, Any]]:
    """Parse LLM content as JSON and validate required roadmap schema."""
    cleaned = _extract_json_array(content)
    parsed = json.loads(cleaned)
    allowed_types = set(_allowed_content_types_for_brain_type(brain_type))

    if not isinstance(parsed, list):
        raise ValueError("LLM response must be a JSON list")

    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError("Each roadmap step must be an object")

        required = ("step", "title", "description", "content_type")
        for key in required:
            if key not in item:
                raise ValueError(f"Missing required field in step: {key}")

        if not isinstance(item["step"], int):
            raise ValueError("step must be an integer")
        if not isinstance(item["title"], str) or not item["title"].strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(item["description"], str) or not item["description"].strip():
            raise ValueError("description must be a non-empty string")
        if not isinstance(item["content_type"], str) or not item["content_type"].strip():
            raise ValueError("content_type must be a non-empty string")

        normalized_content_type = item["content_type"].strip().lower()
        # Allow any recognized content type, even if not ideal for brain type (better than failing)
        all_allowed = {"video", "diagram", "lecture", "podcast", "article", "documentation", "project", "exercise"}
        if normalized_content_type not in all_allowed:
            raise ValueError(
                f"Invalid content_type '{normalized_content_type}'. Must be one of: {', '.join(sorted(all_allowed))}"
            )

    return parsed


def _allowed_content_types_for_brain_type(brain_type: str) -> List[str]:
    """Return allowed content types for each brain type."""
    normalized = str(brain_type).strip().lower()
    mapping = {
        "visual": ["video", "diagram"],
        "auditory": ["lecture", "podcast"],
        "reading": ["article", "documentation"],
        "kinesthetic": ["project", "exercise"],
    }
    return mapping.get(normalized, ["video", "article", "project", "lecture", "diagram", "documentation", "podcast", "exercise"])


def _extract_json_array(content: str) -> str:
    """Extract JSON array text and strip code fences if present."""
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()

    if text.startswith("[") and text.endswith("]"):
        return text

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON array found in LLM response")

    return text[start : end + 1]


def _normalize_steps(
    steps: List[Dict[str, Any]], goal: str, brain_type: str
) -> List[Dict[str, Any]]:
    """Normalize and sort validated steps for route/service compatibility."""
    normalized = []
    normalized_goal = normalize_goal(goal)
    preferred_types = _allowed_content_types_for_brain_type(brain_type)
    phase_labels = _phase_labels_for_brain_type(brain_type)
    skill_sequence = get_ordered_skills_for_goal(normalized_goal)
    target_steps = _target_step_count(normalized_goal, brain_type)
    shaped_steps = _reshape_step_count(steps, target_steps, goal, brain_type, skill_sequence)
    skill_lookup = _skill_lookup_from_text(shaped_steps, skill_sequence, normalized_goal)

    for item in sorted(shaped_steps, key=lambda x: x["step"]):
        step_num = int(item["step"])
        raw_content_type = item["content_type"].strip().lower()
        content_type = raw_content_type if raw_content_type in preferred_types else preferred_types[(step_num - 1) % len(preferred_types)]
        base_title = item["title"].strip()
        title = _apply_phase_label(base_title, phase_labels, step_num)
        description = _add_brain_alignment_line(
            base_description=item["description"].strip(),
            brain_type=brain_type,
            content_type=content_type,
        )
        matched_skill = skill_lookup.get(step_num) or _match_skill_from_text(
            base_title,
            description,
            skill_sequence,
            step_num,
            normalized_goal,
        )
        resource = get_learning_resource_for_skill(matched_skill["id"], content_type)
        edge = _build_neuronav_edge(matched_skill, brain_type, step_num)
        
        # Extract tags from title and description
        tags = _extract_tags(title, goal)
        tags.extend([matched_skill["id"], matched_skill["name"].lower()])
        
        # Estimate time based on content type
        estimated_time = _estimate_time_minutes(content_type)
        
        normalized.append(
            {
                "step": step_num,
                "step_number": step_num,
                "goal": goal,
                "brain_type": str(brain_type),
                "skill_id": matched_skill["id"],
                "skill_name": matched_skill["name"],
                "difficulty": matched_skill.get("difficulty", "beginner"),
                "title": title,
                "description": description,
                "content_type": content_type,
                "resource_title": resource["title"],
                "resource_type": resource["resource_type"],
                "resource_url": resource["url"],
                "estimated_time_minutes": estimated_time,
                "tags": tags,
                "brain_type_optimized": True,
                "mission": edge["mission"],
                "proof_of_work": edge["proof_of_work"],
                "win_condition": edge["win_condition"],
                "speed_boost": edge["speed_boost"],
                "generic_gap": edge["generic_gap"],
                "completed": False,
            }
        )
    return normalized


def _target_step_count(goal: str, brain_type: str) -> int:
    """Return adaptive roadmap size so outputs do not collapse into a fixed template."""
    normalized_goal = str(goal or "").strip().lower()
    normalized_brain = str(brain_type or "").strip().lower()

    base_by_brain = {
        "visual": 8,
        "auditory": 9,
        "reading": 10,
        "kinesthetic": 11,
    }
    base = base_by_brain.get(normalized_brain, 9)

    goal_signal = sum(ord(ch) for ch in normalized_goal) % 2
    return max(8, min(12, base + goal_signal))


def _reshape_step_count(
    steps: List[Dict[str, Any]],
    target_steps: int,
    goal: str,
    brain_type: str,
    skill_sequence: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Expand or trim LLM steps to the adaptive target count."""
    if not steps:
        return []

    ordered = sorted(steps, key=lambda x: int(x.get("step", 0) or 0))

    if len(ordered) > target_steps:
        trimmed = ordered[:target_steps]
        for idx, item in enumerate(trimmed, start=1):
            item["step"] = idx
        return trimmed

    if len(ordered) == target_steps:
        return ordered

    preferred_types = _allowed_content_types_for_brain_type(brain_type)
    existing_step_count = len(ordered)

    for idx in range(existing_step_count + 1, target_steps + 1):
        skill_index = min(idx - 1, len(skill_sequence) - 1)
        skill = skill_sequence[skill_index]
        content_type = preferred_types[(idx - 1) % len(preferred_types)]
        ordered.append(
            {
                "step": idx,
                "title": f"Capstone Sprint: {skill['name']} in {goal}",
                "description": (
                    f"Build a performance-grade artifact for {skill['name']} and evaluate it with "
                    f"a clear quality rubric. This closes a generic-gap by forcing measurable execution."
                ),
                "content_type": content_type,
            }
        )

    return ordered


def _skill_lookup_from_text(
    steps: List[Dict[str, Any]],
    skill_sequence: List[Dict[str, Any]],
    goal: str,
) -> Dict[int, Dict[str, Any]]:
    """Pre-map obvious step keywords to goal-specific skills for stable AI grounding."""
    lookup: Dict[int, Dict[str, Any]] = {}
    keyword_map = _keyword_skill_map(goal)

    for item in steps:
        step_num = int(item.get("step", 0))
        title = str(item.get("title", "")).lower()
        description = str(item.get("description", "")).lower()
        text = f"{title} {description}"

        for skill_id, keywords in keyword_map:
            if any(word in text for word in keywords):
                lookup[step_num] = _find_skill(skill_sequence, skill_id)
                break

    return lookup


def _match_skill_from_text(
    title: str,
    description: str,
    skill_sequence: List[Dict[str, Any]],
    step_num: int,
    goal: str,
) -> Dict[str, Any]:
    """Fallback: choose a stable skill based on keywords or step order."""
    text = f"{title} {description}".lower()

    keyword_map = _keyword_skill_map(goal)

    for skill_id, keywords in keyword_map:
        if any(keyword in text for keyword in keywords):
            return _find_skill(skill_sequence, skill_id)

    index = min(max(step_num - 1, 0), len(skill_sequence) - 1)
    return skill_sequence[index]


def _find_skill(skill_sequence: List[Dict[str, Any]], skill_id: str) -> Dict[str, Any]:
    for skill in skill_sequence:
        if skill["id"] == skill_id:
            return skill
    return skill_sequence[0]


def _keyword_skill_map(goal: str) -> List[tuple[str, List[str]]]:
    """Return goal-specific keyword-to-skill mapping."""
    if goal == "design":
        return [
            ("ds-09", ["accessibility", "wcag", "contrast", "a11y", "inclusive"]),
            ("ds-10", ["portfolio", "case study", "presentation", "critique", "showcase"]),
            ("ds-08", ["usability", "testing", "research", "interview", "feedback"]),
            ("ds-07", ["prototype", "motion", "interaction", "transition", "microinteraction"]),
            ("ds-06", ["figma", "ui", "high-fidelity", "visual", "screen"]),
            ("ds-05", ["wireframe", "wireframing", "layout", "user flow", "ia"]),
            ("ds-04", ["architecture", "navigation", "flow", "journey", "structure"]),
            ("ds-03", ["persona", "problem", "jtbd", "discovery", "insight"]),
            ("ds-02", ["color", "typography", "spacing", "grid", "composition"]),
            ("ds-01", ["principles", "foundation", "basics", "gestalt", "hierarchy"]),
        ]

    return [
        ("da-03", ["sql", "query", "join", "database"]),
        ("da-07", ["visual", "chart", "dashboard", "graph", "plot", "story"]),
        ("da-05", ["python", "pandas", "numpy", "script"]),
        ("da-06", ["clean", "prepare", "wrangle", "missing", "outlier"]),
        ("da-04", ["statistics", "statistical", "probability", "metric"]),
        ("da-08", ["ab test", "experiment", "hypothesis"]),
        ("da-10", ["business", "stakeholder", "kpi", "case"]),
        ("da-02", ["spreadsheet", "excel", "pivot", "worksheet"]),
        ("da-01", ["foundation", "literacy", "overview", "basics"]),
    ]


def _phase_labels_for_brain_type(brain_type: str) -> List[str]:
    """Return phase labels to make roadmap sequencing visibly brain-type specific."""
    normalized = str(brain_type or "").strip().lower()
    mapping = {
        "visual": ["Map", "Observe", "Model", "Compare", "Storyboard", "Present", "Portfolio"],
        "auditory": ["Listen", "Discuss", "Explain", "Debate", "Teach", "Reflect", "Broadcast"],
        "reading": ["Read", "Annotate", "Synthesize", "Reference", "Document", "Critique", "Publish"],
        "kinesthetic": ["Build", "Practice", "Experiment", "Implement", "Debug", "Ship", "Demo"],
    }
    return mapping.get(normalized, ["Learn", "Apply", "Improve", "Master", "Deliver"])


def _apply_phase_label(title: str, phase_labels: List[str], step_num: int) -> str:
    """Prefix title with a brain-style phase label if not already labeled."""
    if ":" in title:
        return title
    phase = phase_labels[(step_num - 1) % len(phase_labels)]
    return f"{phase}: {title}"


def _add_brain_alignment_line(base_description: str, brain_type: str, content_type: str) -> str:
    """Append an explicit alignment sentence so users can see why it is personalized."""
    guidance = {
        "visual": "Use diagrams, visual pattern comparisons, and color-coded notes while completing this step.",
        "auditory": "Use spoken explanations, listen-first materials, and explain concepts aloud during this step.",
        "reading": "Use deep reading, written summaries, and note synthesis to complete this step.",
        "kinesthetic": "Use hands-on execution, mini-builds, and trial-and-error practice in this step.",
    }
    normalized = str(brain_type or "").strip().lower()
    alignment = guidance.get(normalized, "Use a study method aligned with your learner profile.")
    return f"{base_description} This step is optimized for {normalized} learners via {content_type} content. {alignment}"


def _extract_tags(title: str, goal: str) -> List[str]:
    """Extract relevant tags from title and goal."""
    # Extract key words from title
    common_words = {"with", "and", "the", "a", "an", "to", "learn", "learning", "about", "using"}
    words = title.lower().split()
    tags = [w for w in words if w not in common_words and len(w) > 3]
    
    # Add goal as tag if relevant
    goal_words = [w for w in goal.lower().split() if len(w) > 3]
    tags.extend(goal_words[:2])
    
    # Return unique tags
    return list(dict.fromkeys(tags[:5]))


def _estimate_time_minutes(content_type: str) -> int:
    """Estimate learning time based on content type."""
    time_estimates = {
        "video": 45,
        "diagram": 20,
        "lecture": 60,
        "podcast": 30,
        "article": 25,
        "documentation": 35,
        "project": 90,
        "exercise": 40,
    }
    return time_estimates.get(content_type.lower(), 30)


def _build_neuronav_edge(skill: Dict[str, Any], brain_type: str, step_number: int) -> Dict[str, str]:
    """Create per-step differentiators that make roadmap execution measurable and non-generic."""
    brain_tactics = {
        "visual": "Convert the lesson into a visual concept map and compare before-vs-after understanding.",
        "auditory": "Record a short teach-back and listen for weak explanations to close gaps.",
        "reading": "Write a structured summary: concept, method, common pitfall, and practical use.",
        "kinesthetic": "Ship a mini implementation and intentionally debug one issue to lock in skill transfer.",
    }

    normalized = str(brain_type or "").strip().lower()
    tactic = brain_tactics.get(normalized, "Create a concrete output and verify understanding with a quick teach-back.")
    skill_name = str(skill.get("name", "this skill"))

    return {
        "mission": f"Step {step_number} mission: apply {skill_name} to a practical analysis scenario.",
        "proof_of_work": f"Deliver one artifact for {skill_name}: notebook, dashboard, SQL output, or concise brief.",
        "win_condition": "You can justify your approach, trade-offs, and result quality in plain language.",
        "speed_boost": tactic,
        "generic_gap": "Unlike generic plans, this step enforces output + evidence, not passive completion.",
    }