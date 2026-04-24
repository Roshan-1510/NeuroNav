# NeuroNav Engine Notes

## Purpose
The NeuroNav Engine is the brain-type intelligence layer in roadmap generation.
It turns a basic list of learning steps into an execution system tailored to how a learner processes information.

It is not CRUD logic.
CRUD stores, updates, and deletes roadmap data.
NeuroNav Engine designs how each step should be learned and validated.

## What NeuroNav Engine does

1. Brain-type cognitive loop per step
- Adds encode, retrieve, apply, and review strategy based on brain type.
- Example: visual learners get diagram/map-first loops; kinesthetic learners get build/debug loops.

2. Learning phase architecture
- Classifies each step as foundation, integration, or mastery.
- Makes progression intentional, not flat linear content.

3. Session plan generation
- Adds session breakdown per step (warmup, deep work, synthesis).
- Encourages focused sessions instead of passive browsing.

4. Measurable validation
- Adds a validation gate for each step so completion requires proof.
- Prevents generic "watched/read = done" behavior.

5. Anti-generic differentiation
- Adds explicit anti-generic marker and learning contract.
- Requires output + explanation quality before moving on.

## Files changed for NeuroNav Engine

1. backend/services/neuronav_engine.py
- New engine module.
- Adds enrichment metadata to every roadmap step.

2. backend/services/roadmap_service.py
- Rule-based roadmap output now passes through NeuroNav Engine.
- Ensures deterministic generation is brain-type-first.

3. backend/services/ai_roadmap_service.py
- AI-generated roadmap output now also passes through NeuroNav Engine.
- Ensures consistent behavior between AI and fallback paths.

## Output fields added by the engine
Each enriched step now includes:
- neuronav_engine.version
- neuronav_engine.source
- neuronav_engine.brain_type
- neuronav_engine.phase
- neuronav_engine.decision_style
- neuronav_engine.cognitive_loop.encode
- neuronav_engine.cognitive_loop.retrieve
- neuronav_engine.cognitive_loop.apply
- neuronav_engine.cognitive_loop.review
- neuronav_engine.session_plan
- neuronav_engine.measurable_validation
- neuronav_engine.anti_generic_marker
- learning_contract

## Why this matters
A generic roadmap usually says what to study.
NeuroNav Engine defines:
- how to study (brain-type strategy)
- how to prove learning (artifact and validation)
- when a step is truly complete (quality gate)

This is the core differentiator of NeuroNav.

## Date
Created: 2026-04-22
