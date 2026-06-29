# Product Requirements Document (PRD): EduSystem

> Derived from [Final Revised Plan v1.0](final_revised_plan.md). The [implementation plan](implementation_plan.md) defines **Phase A** — a skeletal 8-week build upon which later features are implemented.

---

## 1. Product Overview

**Product Name:** EduSystem — AI-Powered Modular Educational Intelligence Ecosystem

**Target Audience:** Indian students from school through early college foundation learning. Phase A focus: Class 11 Commerce (Accountancy).

**Identity:** A long-term educational operating system — not an AI tutor, chatbot, or simple study planner. It transforms educational materials into structured knowledge and delivers personalized, measurable, explainable learning experiences.

**This PRD is:** a product requirements document aligned to the long-term vision.

**This PRD is NOT:** a promise that all features ship in Phase A. See implementation plan for skeletal scope.

### Core Philosophy

```text
Maximum learning outcomes with minimum unnecessary effort
within the student's available time.
```

### Hybrid Knowledge Architecture

EduSystem uses a **hybrid representation** — not a graph alone:

1. **Concept Objects (structured store):** Rich JSON records — definitions, properties, functions, misconceptions, examples, pedagogy metadata, exam metadata, provenance, confidence scores. Modifiable by a future optimization agent.
2. **Relationship Graph (structural store):** Typed edges (`REQUIRES`, `PART_OF`, `RELATES_TO`, `CONTRASTS_WITH`, `TESTED_BY`) with semantic annotations (what, how, why).
3. **Learning State Graph (per-student):** Private mastery, confidence, forgetting curves, and active misconceptions per `(student, concept)`.

All domain knowledge enters via the **ingestion pipeline** — raw files are educational **inputs, not knowledge bases**. No hardcoded concept content.

```text
PDF / DOCX / PPT / Images
        ↓
Docling / Marker → Normalized Markdown → Educational Extraction
        ↓
Canonical Mapping → Concept Objects → Relationship Graph → Teaching Systems
```

---

## 2. Optimization Priority Hierarchy

| Tier | Focus | Rule |
|------|-------|------|
| **Tier 1 — Learning Correctness** | Understanding, misconception reduction, retention, transfer | Highest priority |
| **Tier 2 — Performance** | Exam readiness, score improvement, syllabus completion, roadmap efficiency | Never overrides Tier 1 |
| **Tier 3 — Sustainable Engagement** | Consistency, burnout prevention, productive habits | Never overrides Tier 1–2 |
| **Tier 4 — Experimentation** | Pedagogical improvements, adaptive refinements | Only if higher tiers unaffected |

---

## 3. Student Workflow & Exam Intelligence

### Student Inputs

Required: goal exam, exam deadline, available study time, current academic status.

Optional: coaching schedules, midterms, assignments, mock exams, additional learning materials.

### Exam Classification

| Type | Examples | Behavior |
|------|----------|----------|
| **Goal Exams** | JEE Advanced, NEET, CLAT, CA, Board Exams | Primary optimization target |
| **Necessary Exams** | JEE Main, Board exams, coaching tests | Auto-prioritized |
| **Optional Exams** | BITSAT, VITEEE, CET | Included when beneficial |

*Phase A: Board Exam / CA Foundation focus for Commerce 11. Full exam taxonomy deferred.*

---

## 4. Learning Architecture

### Progressive Layered Interleaving

| Stage | Goal | Methods |
|-------|------|---------|
| **1 — Foundational Coverage** | Fast syllabus coverage, baseline familiarity | Concise explanations, formulas, worked examples, diagrams |
| **2 — Reinforcement** | Chapter depth | PYQs, completion problems, misconception repair |
| **3 — Integration** | Advanced reasoning | Integrated problems, cross-topic applications |
| **4 — Optimization** | Exam performance | Mocks, speed, weak-point elimination |

*Phase A: Stages 1–2 with lightweight interleaving. Stages 3–4 deferred.*

---

## 5. Product Features

### 5.1 Diagnostic System

Confidence is a **weak prior signal**.

1. Student labels topics: confident / weak / unknown.
2. Calibration testing: transfer questions, conceptual traps, reframed questions.
3. System generates confidence calibration score (`|stated confidence − actual mastery|`).

### 5.2 Misconception Framework

Structured taxonomies: formula misuse, dimensional errors, symbolic mistakes, overgeneralization, causal inversion. Each misconception has `warning_signs`, `fixes`, `frequency`, provenance, and confidence. Wrong answers match warning signs for targeted remediation.

### 5.3 Worked Example System

| Mode | When |
|------|------|
| Worked Examples | Novice (low mastery) |
| Completion Problems | Transition (OK mastery) |
| Independent Problems | Mastery evaluation (strong) |

Transition driven by retention, competency, and transfer success.

### 5.4 Level-Aware Teaching

Explanation levels: `eli10`, `highschool`, `college`, `graduate`, `expert`. Precomputed at ingestion; LLM adapts for active misconceptions at runtime.

### 5.5 Revision System

FSRS-style scheduling + EMA personalization. Eventually: per-student, per-concept, per-question-type memory modeling.

### 5.6 Metacognitive Layer

Actionable study advice based on session data — revision strategies, retrieval practice, calibration improvement. Goal: independent learners.

### 5.7 Material Ingestion

- Supported formats: PDF, DOCX, PPTX (Images in Phase B).
- Pipeline: parse → normalize markdown → extract Concept Objects + TypedRelations → ontology map → graph.
- Cross-document synthesis: merge duplicates, flag `CONTRADICTS` edges.
- Validation pipeline (full): security → authenticity → quality → novelty → contradiction → controlled integration. *Phase A: quality thresholds + contradiction flagging.*

### 5.8 Explainability

Surface why topics were prioritized, revisions scheduled, teaching adapted, and questions selected. *Phase A: basic roadmap and session-plan reasoning. Full explainability layer in Phase B.*

### 5.9 Adaptive Experimentation

80–90% validated methods, 10–20% bounded experimentation. Evaluate delayed retention, transfer, misconception reduction — not immediate correctness alone. *Deferred to Phase B.*

---

## 6. Multi-Agent Architecture

### Full Vision (Final Plan)

Master Orchestrator, Session Orchestrator, and 11 specialized agents (Roadmap, Diagnostic, Teaching Strategy, Concept Teaching, Question Generation, Revision, Engagement, Memory Optimization, Performance Analytics, Material Ingestion, Validation).

### Phase A (Implementation Plan)

Six agents with orchestration implicit in API routes:

| Agent | Responsibility |
|-------|----------------|
| DiagnosticAgent | Gap detection, adversarial calibration |
| TeachingAgent | Level-aware delivery, misconception remediation, question generation |
| RevisionAgent | FSRS scheduling |
| RoadmapAgent | Session planning, prerequisite ordering |
| AnalyticsAgent | Friction model, calibration tracking |
| IngestionAgent | Document parsing, extraction, synthesis |

---

## 7. User Experience

### 7.1 Offline-First & Multi-User

Local-first for low-end devices, intermittent connectivity, shared devices. Username-only profiles in Phase A. Isolated learner state per student.

### 7.2 Key Interfaces

| Screen | Purpose |
|--------|---------|
| Onboarding | Goals, self-assessment, initial diagnostic, first session plan (< 10 min) |
| Dashboard | Session plan, mastery distribution, review calendar, calibration trend |
| Topic Browser | Chapters with mastery badges |
| Teaching | Level badges, streamed explanations, worked examples, interactive answers |
| Graph View | Cytoscape.js — prerequisites, mastery colors, misconception highlights |
| Upload Portal | Drag-drop with live ingestion progress |

### 7.3 Frontend Strategy

AI tools (Stitch, Cursor, Lovable) for rapid UI shells. Manual control of architecture, state, workflows, caching. See [DESIGN.md](DESIGN.md).

---

## 8. Success Metrics (KPIs)

### Primary

| KPI | Purpose |
|-----|---------|
| Retention Half-Life | Memory durability |
| Time-to-80%-Mastery | Learning efficiency |
| Near Transfer Success | Reframed application |
| Medium Transfer Success | Integrated application |
| Mock Score Improvement | Exam readiness |
| Syllabus Completion Time | Planning effectiveness |
| Misconception Recurrence | Teaching quality |

### Secondary

| KPI | Purpose |
|-----|---------|
| Study Consistency | Habit formation |
| Burnout Indicators | Workload safety |
| Session Completion Rate | Pacing quality |
| Confidence Calibration Error | Metacognition |
| Topic Recovery Speed | Diagnostic quality |

---

## 9. Domain Expansion Order

Commerce (Accountancy, Economics, Business Studies) → Humanities → Law → Chemistry → Mathematics → Computer Science → Biology → Physics → Architecture/Design.

*Phase A: Commerce 11 Accountancy only.*

---

## 10. Roadmap Phases

| Phase | Scope | Document |
|-------|-------|----------|
| **A — Skeletal** | Working core: graphs, ingestion foundations, 6 agents, teaching loop | [implementation_plan.md](implementation_plan.md) |
| **B** | Memory optimization, lightweight simulations, experimentation, ontology refinement, vector retrieval, explainability | Future |
| **C** | Advanced simulations, federated improvements, full validation hierarchy, coach dashboard | Future |

---

## 11. Deferred Features (Post Phase A)

- Master/Session Orchestrators as explicit agents
- Teaching Strategy Agent (separate from Teaching Agent)
- Memory Optimization Agent
- Validation Agent (full security/authenticity pipeline)
- Vector retrieval (Qdrant/pgvector)
- Image ingestion
- Coach/mentor dashboard
- Cloud sync and federated learning
- Deep simulations (Physics/Chemistry)
- 3-level human oversight workflow
- PostgreSQL JSONB migration
- Neo4j graph migration (if scale requires)
