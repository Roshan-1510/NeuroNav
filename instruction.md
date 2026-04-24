# NeuroNav — Copilot Instruction Contract

## Objective

Build a deterministic, adaptive learning system based on cognitive profiling and behavioral feedback.

This is NOT an AI wrapper.

---

## Core System Flow

User → Quiz → Brain Type
→ Roadmap Generator (rule-based)
→ Progress Tracking
→ Adaptation Engine
→ Updated Roadmap

---

## Non-Negotiable Rules

* Do NOT use LLM for roadmap generation
* All recommendations must be deterministic and explainable
* All modules must be independent and testable
* No business logic inside routes
* No random outputs

---

## Required Modules

### 1. Skill Graph

* Define skills with prerequisites
* Must support ordering via dependency resolution

---

### 2. Content Mapping

* Each skill must map to:

  * video
  * article
  * project

---

### 3. Cognitive Engine

* Input: quiz answers
* Output: brain_type (visual, auditory, reading, kinesthetic)

---

### 4. Roadmap Generator (CRITICAL)

* Input: goal + brain_type
* Steps:

  1. Load skills
  2. Sort using prerequisites
  3. Map content based on brain_type
* Output: ordered roadmap

---

### 5. Progress Tracking

Track:

* completed
* time_spent
* skipped
* attempts

---

### 6. Adaptation Engine (CRITICAL)

Rules:

* If user skips content type → reduce that type
* If user completes fast → skip beginner steps
* If user struggles → insert simpler steps

Must return updated roadmap

---

## Folder Responsibilities

* routes/ → request/response only
* services/ → all logic
* models/ → DB schema
* utils/ → helpers

---

## Code Requirements

* Use Flask for API
* Use MongoDB for storage
* Modular functions only
* No monolithic files
* Each function must have a single responsibility

---

## Forbidden Patterns

* Calling AI inside roadmap generation
* Hardcoding outputs in routes
* Mixing DB logic with business logic
* Skipping prerequisite handling

---

## Success Criteria

System must:

* Generate roadmap from quiz
* Track user behavior
* Modify roadmap based on behavior

If roadmap does not change → system is incomplete
