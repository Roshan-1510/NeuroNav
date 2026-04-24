"""Quiz domain service: question management, scoring, and roadmap creation."""

from __future__ import annotations

from datetime import datetime
import random
from typing import Any, Dict, List

from bson import ObjectId
from flask import current_app

try:
    from services.cognitive_service import determine_brain_type
    from services.ai_roadmap_service import generate_and_save_roadmap
except ImportError:  # pragma: no cover - supports package import style
    from .cognitive_service import determine_brain_type
    from .ai_roadmap_service import generate_and_save_roadmap


BRAIN_TYPE_DESCRIPTIONS = {
    "Visual": {
        "description": "You learn best through visual aids like diagrams, charts, and videos.",
        "learning_tips": [
            "Use mind maps and flowcharts",
            "Watch educational videos",
            "Use colorful notes and highlighters",
            "Create visual associations",
        ],
        "strengths": ["Pattern recognition", "Spatial awareness", "Visual memory"],
    },
    "Auditory": {
        "description": "You learn best through listening and verbal instruction.",
        "learning_tips": [
            "Listen to podcasts and lectures",
            "Discuss topics with others",
            "Read aloud",
            "Use verbal repetition",
        ],
        "strengths": ["Verbal communication", "Listening skills", "Music appreciation"],
    },
    "ReadWrite": {
        "description": "You learn best through reading and writing activities.",
        "learning_tips": [
            "Take detailed notes",
            "Create lists and outlines",
            "Read extensively",
            "Write summaries",
        ],
        "strengths": ["Written communication", "Research skills", "Critical analysis"],
    },
    "Kinesthetic": {
        "description": "You learn best through hands-on activities and movement.",
        "learning_tips": [
            "Practice with real examples",
            "Use hands-on activities",
            "Take breaks for movement",
            "Build projects",
        ],
        "strengths": ["Problem-solving", "Practical application", "Physical coordination"],
    },
}

CANONICAL_TO_DB_LABEL = {
    "visual": "Visual",
    "auditory": "Auditory",
    "reading": "ReadWrite",
    "kinesthetic": "Kinesthetic",
}


def _interpret_confidence_score(confidence: float, is_tied: bool) -> str:
    """
    Provide human-readable interpretation of brain-type confidence.
    
    - 75-100%: Strong match (high confidence, clear preference)
    - 50-74%: Moderate match (decent confidence, some ambiguity)
    - 25-49%: Weak match (low confidence, tied or split responses)
    - Below 25%: Very weak match (tie with 3+ types, high uncertainty)
    
    Tied results have reduced confidence to reflect ambiguity.
    """
    if confidence >= 75:
        return "Strong match - You have a clear learning preference"
    elif confidence >= 50:
        if is_tied:
            return "Moderate match - You have multiple strong learning styles"
        else:
            return "Moderate match - You have some preference for this style"
    elif confidence >= 25:
        return "Weak match - Your learning style is balanced across multiple types"
    else:
        return "Very weak match - You're equally skilled across all learning styles"


def get_all_questions() -> Dict[str, Any]:
    """Return quiz questions formatted for API clients."""
    db = current_app.db
    questions = list(db.quiz_questions.find())
    formatted_questions = []

    for index, question in enumerate(questions):
        formatted_question = {
            "question_id": f"q{index + 1}",
            "question_number": index + 1,
            "text": question["text"],
            "options": [],
        }

        # Shuffle option display order while keeping option_id tied to original index.
        # This keeps scoring correct because submit uses selected option_id.
        options_with_ids = [
            {
                "option_id": option_index + 1,
                "text": option.get("text", ""),
                "brain_type": option.get("brain_type", ""),
            }
            for option_index, option in enumerate(question.get("options", []))
        ]
        random.shuffle(options_with_ids)
        formatted_question["options"] = options_with_ids

        formatted_questions.append(formatted_question)

    return {
        "questions": formatted_questions,
        "total_questions": len(formatted_questions),
        "instructions": "Choose the option that best describes your learning preferences.",
    }


def create_question(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new quiz question."""
    if not data or "text" not in data or "options" not in data:
        raise ValueError("text and options are required")

    db = current_app.db
    question = {
        "text": data["text"],
        "options": data["options"],
        "updated_at": datetime.utcnow(),
    }
    result = db.quiz_questions.insert_one(question)
    return {"id": str(result.inserted_id)}


def update_question(question_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing quiz question."""
    if not ObjectId.is_valid(question_id):
        raise ValueError("Invalid question id")

    db = current_app.db
    update = {
        "$set": {
            "text": data.get("text"),
            "options": data.get("options"),
            "updated_at": datetime.utcnow(),
        }
    }
    db.quiz_questions.update_one({"_id": ObjectId(question_id)}, update)
    return {"msg": "Updated"}


def delete_question(question_id: str) -> Dict[str, Any]:
    """Delete a quiz question by ID."""
    if not ObjectId.is_valid(question_id):
        raise ValueError("Invalid question id")

    db = current_app.db
    db.quiz_questions.delete_one({"_id": ObjectId(question_id)})
    return {"msg": "Deleted"}


def submit_quiz_and_generate_roadmap(user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate quiz answers, persist brain type, and generate deterministic roadmap."""
    if not payload or "answers" not in payload:
        raise ValueError("Answers are required")

    answers: List[Dict[str, Any]] = payload["answers"]
    preferences: Dict[str, Any] = payload.get("preferences", {})

    db = current_app.db
    questions = list(db.quiz_questions.find())
    question_map = {f"q{i + 1}": q for i, q in enumerate(questions)}

    cognitive_result = determine_brain_type(answers=answers, question_map=question_map)
    dominant_brain_type = cognitive_result["brain_type"]  # lowercase: "visual", "auditory", etc.
    dominant_brain_type_db = CANONICAL_TO_DB_LABEL[dominant_brain_type]  # Full name: "Visual", "Auditory", etc.

    # Detect if brain type was a tie (multiple types with same highest score)
    distribution = cognitive_result["distribution"]
    max_score = max(distribution.values())
    tied_brain_types = [bt for bt, score in distribution.items() if score == max_score]
    is_tie = len(tied_brain_types) > 1

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "brain_type": dominant_brain_type_db,
            "brain_type_tie": is_tie,  # Flag indicating if brain type was a tie
            "tied_brain_types": tied_brain_types if is_tie else [],  # All tied types
            "updated_at": datetime.utcnow()
        }},
    )

    goal = preferences.get("goal") or preferences.get("topic") or "data analyst"
    print(f"🎯 Quiz submitted: brain_type={dominant_brain_type}, goal={goal}")
    
    roadmap_result = generate_and_save_roadmap(
        db=db,
        user_id=user_id,
        goal=goal,
        brain_type=dominant_brain_type,  # Pass lowercase brain type
    )

    total_minutes = sum(int(step.get("estimated_time_minutes", 30) or 30) for step in roadmap_result["steps"])
    estimated_completion_weeks = max(1, round(total_minutes / (45 * 7)))

    return {
        "message": "Quiz completed successfully! Your personalized learning roadmap has been generated.",
        "assessment_results": {
            "brain_type": dominant_brain_type,
            "confidence_score": cognitive_result["confidence_score"],
            "brain_type_distribution": cognitive_result["distribution"],
            "total_questions_answered": cognitive_result["total_answers"],
            "is_tied": is_tie,
            "tied_brain_types": tied_brain_types if is_tie else [],
            "confidence_interpretation": _interpret_confidence_score(cognitive_result["confidence_score"], is_tie),
        },
        "brain_type_description": BRAIN_TYPE_DESCRIPTIONS.get(dominant_brain_type_db, {}),
        "roadmap": {
            "roadmap_id": roadmap_result["roadmap_id"],
            "topic": goal,
            "source": roadmap_result["source"],
            "total_steps": roadmap_result["total_steps"],
            "estimated_completion_weeks": estimated_completion_weeks,
            "daily_time_minutes": 45,
            "steps": roadmap_result["steps"],
        },
        "next_steps": [
            "Review your personalized roadmap",
            "Start with the first learning step",
            "Track your progress as you complete each step",
            "Adjust your learning pace as needed",
        ],
    }
