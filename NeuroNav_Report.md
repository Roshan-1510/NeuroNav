# NeuroNav Final Report

## Abstract
NeuroNav is an AI-powered platform that generates personalized learning paths based on users' brain types, leveraging the VARK model. The system aims to improve engagement and completion rates by matching resource formats to individual preferences.

## Introduction
Personalized learning is a key challenge in education technology. NeuroNav addresses this by using brain-type classification to recommend resources and structure learning roadmaps.

## Problem Statement
Learners often struggle to find resources and study methods that suit their cognitive preferences. Existing platforms lack adaptive, brain-type-driven guidance.

## Related Work
- VARK model (Fleming, 2001)
- Critique of learning styles (Pashler et al., 2008)
- Adaptive learning systems

## System Architecture
- Backend: Flask, MongoDB
- Frontend: React/Next.js, Tailwind CSS
- Models: User, QuizQuestion, Resource, Roadmap, Progress
- APIs: Auth, Quiz, Roadmap, Progress, Analysis

## Implementation
- Rule-based mapping from quiz answers to brain type
- Roadmap generator prioritizes resource formats by brain type
- Progress tracking and dashboard visualization
- Analysis script for engagement metrics

## Validation Plan & Analysis
- Collect progress data and compare engagement for matching/non-matching formats
- Metrics: completion %, average time spent
- See analysis/engagement_metrics.csv and summary.txt

## Future Work
- Integrate RAG for dynamic resource recommendations
- A/B testing of mapping strategies
- Expand to more brain-type models and external datasets

## References
- Fleming, N. D. (2001). Teaching and Learning Styles: VARK Strategies. Christchurch, New Zealand: N.D. Fleming.
- Pashler, H., McDaniel, M., Rohrer, D., & Bjork, R. (2008). Learning Styles: Concepts and Evidence. Psychological Science in the Public Interest, 9(3), 105-119.
