"""NeuroNav Engine: brain-type-first roadmap enrichment and differentiation."""

from __future__ import annotations

from typing import Any, Dict, List


ENGINE_VERSION = "neuronav-engine-v2"


_BRAIN_PROTOCOLS: Dict[str, Dict[str, str]] = {
    "visual": {
        "encoding": "Convert concepts into diagrams, relationship maps, and visual contrast tables.",
        "retrieval": "Recall using blank-canvas redraw before reviewing the source.",
        "transfer": "Apply by building chart-first or pipeline-first visual outputs.",
        "feedback": "Review visual clarity and signal-to-noise ratio with a checklist.",
        "decision_style": "Pattern and structure detection",
    },
    "auditory": {
        "encoding": "Learn through spoken walkthroughs and narrative explanation.",
        "retrieval": "Use teach-back voice notes with 2-minute recap limits.",
        "transfer": "Apply by presenting reasoning aloud before implementation.",
        "feedback": "Compare spoken explanation against rubric gaps.",
        "decision_style": "Narrative and verbal reasoning",
    },
    "reading": {
        "encoding": "Build structured notes with definition-method-example-caveat frames.",
        "retrieval": "Use short written recall prompts without source text.",
        "transfer": "Apply by writing analytical summaries and justifications.",
        "feedback": "Audit note precision, assumptions, and evidence quality.",
        "decision_style": "Textual synthesis and precision",
    },
    "kinesthetic": {
        "encoding": "Learn by immediate implementation and hands-on micro-experiments.",
        "retrieval": "Rebuild from scratch in short timed sprints.",
        "transfer": "Apply via end-to-end mini-project and debugging loops.",
        "feedback": "Score execution quality by output correctness and iteration speed.",
        "decision_style": "Action and feedback-loop reasoning",
    },
}


def enrich_roadmap_steps(
    steps: List[Dict[str, Any]],
    goal: str,
    brain_type: str,
    source: str,
) -> List[Dict[str, Any]]:
    """Attach NeuroNav cognitive engine fields so roadmap is non-generic by design."""
    normalized_brain = str(brain_type or "").strip().lower()
    protocol = _BRAIN_PROTOCOLS.get(normalized_brain, _BRAIN_PROTOCOLS["reading"])

    enriched: List[Dict[str, Any]] = []
    total_steps = max(len(steps), 1)
    for index, step in enumerate(steps, start=1):
        step_number = int(step.get("step_number") or step.get("step") or index)
        phase = _phase_bucket(step_number, total_steps)
        session_plan = _session_plan(step, normalized_brain)
        step_focus = _step_focus(step)
        phase_directive = _phase_directive(phase, normalized_brain)

        enriched_step = dict(step)
        enriched_step["step"] = step_number
        enriched_step["step_number"] = step_number
        enriched_step["neuronav_engine"] = {
            "version": ENGINE_VERSION,
            "source": source,
            "brain_type": normalized_brain,
            "phase": phase,
            "focus": step_focus,
            "phase_directive": phase_directive,
            "decision_style": protocol["decision_style"],
            "cognitive_loop": {
                "encode": protocol["encoding"],
                "retrieve": protocol["retrieval"],
                "apply": protocol["transfer"],
                "review": protocol["feedback"],
            },
            "session_plan": session_plan,
            "measurable_validation": _validation_rule(step, goal, step_number),
            "anti_generic_marker": (
                "Mandatory artifact + retrieval + transfer + review loop. "
                "Passive completion does not qualify as done."
            ),
        }
        enriched_step["learning_contract"] = (
            f"Before marking complete: produce one concrete output for '{step_focus}', run the validation gate, "
            f"and explain your trade-offs in plain language. Goal context: {goal}."
        )
        enriched.append(enriched_step)

    return enriched


def _phase_bucket(step_number: int, total_steps: int) -> str:
    if step_number <= max(1, total_steps // 3):
        return "foundation"
    if step_number <= max(2, (2 * total_steps) // 3):
        return "integration"
    return "mastery"


def _session_plan(step: Dict[str, Any], brain_type: str) -> Dict[str, int]:
    base = int(step.get("estimated_time_minutes", 45) or 45)
    if brain_type == "reading":
        return {"warmup_min": 10, "deep_work_min": max(20, base - 20), "synthesis_min": 10}
    if brain_type == "auditory":
        return {"warmup_min": 8, "deep_work_min": max(20, base - 18), "synthesis_min": 10}
    if brain_type == "kinesthetic":
        return {"warmup_min": 5, "deep_work_min": max(20, base - 15), "synthesis_min": 10}
    return {"warmup_min": 7, "deep_work_min": max(20, base - 17), "synthesis_min": 10}


def _validation_rule(step: Dict[str, Any], goal: str, step_number: int) -> str:
    title = str(step.get("title") or step.get("skill_name") or f"Step {step_number}")
    return (
        f"Validation Gate S{step_number}: deliver artifact + 120-second rationale for {title}, "
        f"then pass a relevance check against goal '{goal}'."
    )


def _step_focus(step: Dict[str, Any]) -> str:
    """Infer practical focus area from step metadata."""
    text = f"{step.get('title', '')} {step.get('skill_name', '')} {step.get('description', '')}".lower()
    keyword_map = [
        ("query design", ["sql", "query", "join", "database"]),
        ("data preparation", ["clean", "wrangle", "missing", "outlier", "prepare"]),
        ("analysis scripting", ["python", "pandas", "notebook", "script"]),
        ("insight communication", ["dashboard", "visual", "chart", "story", "stakeholder"]),
        ("experimentation", ["ab", "experiment", "hypothesis", "test"]),
        ("business impact framing", ["business", "kpi", "case", "recommendation"]),
    ]
    for focus, keywords in keyword_map:
        if any(keyword in text for keyword in keywords):
            return focus
    return "analytical reasoning"


def _phase_directive(phase: str, brain_type: str) -> str:
    """Return distinct phase-level directive to avoid template-like steps."""
    phase_playbook: Dict[str, Dict[str, str]] = {
        "foundation": {
            "visual": "Build one-page concept maps before touching tools.",
            "auditory": "Use explain-first audio recaps before implementation.",
            "reading": "Create structured notes and definitions before practice.",
            "kinesthetic": "Start with a tiny build to learn through action.",
        },
        "integration": {
            "visual": "Connect concepts using pipeline diagrams and dashboard drafts.",
            "auditory": "Debate alternatives out loud and justify your selected path.",
            "reading": "Synthesize references into decision logs and written rationale.",
            "kinesthetic": "Run implementation sprints and fix one deliberate breakage.",
        },
        "mastery": {
            "visual": "Present a visual narrative with trade-off annotations.",
            "auditory": "Deliver a concise spoken defense of your approach.",
            "reading": "Publish a polished written brief with evidence-backed conclusions.",
            "kinesthetic": "Ship a capstone iteration with measurable quality gains.",
        },
    }
    brain_map = phase_playbook.get(phase, {})
    return brain_map.get(brain_type, "Deliver measurable output and articulate your reasoning.")