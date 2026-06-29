# Final Revised Plan (v1.0)

> **Canonical north-star document.** All other docs in `docs/` derive from this plan. The [implementation plan](implementation_plan.md) is the **skeletal Phase A build** — a working foundation, not the full vision.

---

## Product Identity

```text
AI-Powered Modular Educational Intelligence Ecosystem
```

A long-term educational operating system for Indian students that evolves from a simple adaptive study planner into a comprehensive educational intelligence platform.

This is:

* A **long-term vision architecture**
* A **research roadmap**
* An **engineering roadmap**
* A **modular ecosystem**

This is **NOT**:

* an MVP,
* an immediate implementation specification,
* or a promise that all components will exist from day one.

The system grows gradually through validated improvements. See [implementation_plan.md](implementation_plan.md) for the current 8-week skeletal build scope.

---

## Core Philosophy

The system optimizes for:

```text
Maximum learning outcomes
with minimum unnecessary effort
within the student's available time.
```

The platform aims to:

1. Maximize conceptual understanding.
2. Maximize long-term retention.
3. Maximize exam performance.
4. Minimize wasted effort.
5. Complete the syllabus early.
6. Maximize high-quality practice time.
7. Continuously improve teaching effectiveness using evidence.

---

## Optimization Priority Hierarchy

### Tier 1 — Learning Correctness (Highest)

Optimize for: conceptual understanding, misconception reduction, retention, transfer ability.

### Tier 2 — Performance

Optimize for: exam readiness, score improvement, syllabus completion efficiency, roadmap effectiveness.

### Tier 3 — Sustainable Engagement

Optimize for: consistency, reduced burnout, productive study habits.

### Tier 4 — Experimentation

Optimize for: pedagogical improvements, adaptive refinements — only if it does not negatively impact higher tiers.

---

## Educational KPIs

### Primary KPIs

| Metric | Purpose |
|--------|---------|
| Retention Half-Life | Memory durability |
| Time-to-80%-Mastery | Learning efficiency |
| Near Transfer Success | Same concepts, different framing |
| Medium Transfer Success | Integrated applications |
| Mock Score Improvement | Exam readiness |
| Syllabus Completion Time | Planning effectiveness |
| Misconception Recurrence | Teaching quality |

### Secondary KPIs

| Metric | Purpose |
|--------|---------|
| Study Consistency | Habit formation |
| Burnout Indicators | Workload safety |
| Session Completion Rate | Pacing quality |
| Confidence Calibration Error | Metacognition |
| Topic Recovery Speed | Diagnostic quality |

---

## Student Workflow

Students provide: goal exam, exam deadline, available study time, current academic status.

Optional: coaching schedules, midterms, assignments, mock exams, additional learning materials.

---

## Exam Intelligence System

### Goal Exams

Examples: JEE Advanced, NEET, CLAT, CA, Board Exams.

### Necessary Exams

Automatically prioritized. Examples: JEE Main, Board examinations, coaching tests.

### Optional Exams

Included if beneficial. Examples: BITSAT, VITEEE, CET examinations.

---

## Learning Architecture

The system uses **Progressive Layered Interleaving** instead of strict chapter blocking.

| Stage | Goal | Methods |
|-------|------|---------|
| **1 — Foundational Coverage** | Cover syllabus quickly, build baseline familiarity | Concise explanations, formulas, worked examples, diagrams |
| **2 — Reinforcement** | Improve chapter understanding | PYQs, completion problems, misconception repair |
| **3 — Integration** | Build advanced reasoning | Integrated problems, cross-topic applications |
| **4 — Optimization** | Maximize exam performance | Mocks, speed improvement, weak-point elimination |

---

## Diagnostic System

Student confidence is treated as a **weak prior signal**.

1. Student labels confident / weak / unknown topics.
2. Calibration testing: transfer questions, conceptual traps, reframed questions.
3. Confidence calibration score generated — tracks confidence vs actual competence.

---

## Misconception Framework

Maintain structured misconception taxonomies: formula misuse, dimensional errors, symbolic mistakes, overgeneralization, causal inversion.

Used for: diagnostics, targeted remediation, revision planning.

---

## Worked Example System

| Mode | Purpose |
|------|---------|
| Worked Examples | Novice learning |
| Completion Problems | Guided transition |
| Independent Problems | Mastery evaluation |

Transition adapts using retention, competency, and transfer success.

---

## Metacognitive Layer

Teach students how to revise, how retrieval works, how forgetting occurs, and how to self-assess accurately. Goal: create independent learners.

---

## Multi-Agent Architecture

### Orchestrators

- **Master Orchestrator** — coordinates agents, priorities, workflows.
- **Session Orchestrator** — coordinates individual study sessions.

### Specialized Agents

| Agent | Role |
|-------|------|
| Roadmap Agent | Planning and scheduling |
| Diagnostic Agent | Gap detection |
| Teaching Strategy Agent | Method selection |
| Concept Teaching Agent | Content delivery |
| Question Generation Agent | Exam-quality questions |
| Revision Agent | Scheduling reinforcement |
| Engagement Agent | Learning friction analysis |
| Memory Optimization Agent | Mnemonics and memory aids |
| Performance Analytics Agent | Learning metrics |
| Material Ingestion Agent | Educational parsing |
| Validation Agent | Quality assurance |

> **Phase A (skeletal):** See [implementation_plan.md](implementation_plan.md) — 6 core agents (Diagnostic, Teaching, Revision, Roadmap, Analytics, Ingestion) with orchestration implicit in API routes. Remaining agents deferred.

---

## Adaptive Experimentation

```text
80–90% validated methods
10–20% experimentation
```

Experiments evaluate delayed retention, transfer, and misconception reduction — not immediate correctness alone.

---

## Personalization Strategy

Start conservatively. Adapt only: forgetting rates, pacing preferences, explanation density, practice intensity. Expand only after validation.

---

## Educational Content Pipeline

Raw files are treated as **educational inputs, NOT knowledge bases**.

Supported formats: PDF, DOCX, PPTX, Images.

---

## Educational Parsing Pipeline

```text
Educational Files (PDF / DOCX / PPT / Images)
        ↓
Parser Layer (Docling / Marker)
        ↓
Normalized Markdown          ← canonical intermediate representation
        ↓
Educational Extraction
        ↓
Canonical Mapping
        ↓
Concept Objects
        ↓
Relationship Graph
        ↓
Teaching Systems
```

### Canonical Markdown Layer

Markdown is the canonical intermediate representation: human-readable, LLM-friendly, version-controllable, parser-independent.

### Educational Extraction

Extract: concepts, definitions, formulas, examples, misconceptions, questions, diagrams, pedagogical cues.

### Canonical Concept Registry

Every concept maps to a unique canonical ID — prevents duplicates, fragmented graphs, and inconsistent terminology.

---

## Knowledge Representation (Hybrid Architecture)

### Concept Objects (Structured Store)

Store as JSON objects:

* definitions, properties, functions (if any)
* misconceptions, examples, intuition
* pedagogy metadata, exam metadata
* provenance, confidence scores

Later modifiable by a **Concept Optimization Agent** to improve teaching effectiveness.

### Relationship Graph (Structural Store)

Typed educational relationships with semantic annotations (what, how, why):

* `REQUIRES`
* `PART_OF`
* `RELATES_TO`
* `TESTED_BY`
* `CONTRASTS_WITH`
* `CONTRADICTS` (cross-document disagreement, flagged for review)

---

## Storage Architecture

| Layer | Technology | Notes |
|-------|------------|-------|
| Raw Documents | Local storage → MinIO → S3 | Evolution path |
| Concept Objects | JSON → PostgreSQL JSONB | SQLite JSON columns in Phase A |
| Graph Layer | NetworkX → **Kuzu** → Neo4j | Kuzu = "SQLite for graphs" — local-first, embedded |
| Vector Layer | Qdrant / pgvector | Semantic retrieval only — NOT primary knowledge storage |
| Relational/Transactional | SQLite (Phase A) → PostgreSQL | Sessions, events, logs |

---

## Ontology Strategy

**Canonical Ontology** — stable, curated foundation.

**Dynamic Layer** — AI proposes new links and refinements; validated before promotion.

---

## Educational Validation Pipeline

```text
Security Checks
        ↓
Authenticity Verification
        ↓
Quality Analysis
        ↓
Novelty Detection
        ↓
Contradiction Detection
        ↓
Controlled Integration
```

---

## Human Oversight

| Level | Scope |
|-------|-------|
| **Level 1** | Automatic approval — low-risk updates |
| **Level 2** | Expert review — ontology rewiring, pedagogical modifications |
| **Level 3** | Multi-review approval — cloud-wide updates |

---

## Revision System

Initially: FSRS-style scheduling + EMA personalization.

Eventually: per-student + per-concept + per-question-type memory modeling.

---

## Simulation Philosophy

Use simulations only when ROI is high (e.g., electromagnetism, rotational mechanics, molecular geometry). Otherwise prefer diagrams, animations, and worked examples.

---

## Frontend Strategy

Use AI tools (Google Stitch, Cursor, Lovable) for rapid UI generation, dashboards, and prototypes. Manually control architecture, state management, educational workflows, and caching.

---

## Visualization System

Visualize prerequisites, dependency chains, misconceptions, and roadmap progress. Recommended: **Cytoscape.js**.

---

## Offline-First Architecture

Support low-end devices, intermittent internet, and shared devices. Features: local caching, offline revision, resumable synchronization.

---

## Multi-User Support

Each student profile stores progress, roadmap, analytics, retention state, and personalization data. Profiles remain isolated.

---

## Explainability Layer

Track why topics were prioritized, why revisions were scheduled, why teaching changed, and why questions were selected.

---

## Coach Integration

Optional mentor dashboard: roadmap review, overrides, monitoring.

---

## Domain Expansion Order

| Stage | Domain |
|-------|--------|
| 0 | Core infrastructure |
| 1 | Commerce (Accountancy, Economics, Business Studies) |
| 2 | Humanities |
| 3 | Law (CLAT) |
| 4 | Chemistry |
| 5 | Mathematics |
| 6 | Computer Science |
| 7 | Biology |
| 8 | Physics |
| 9 | Architecture and Design |

---

## MVP Roadmap

### Phase A — Skeletal Foundation (see implementation_plan.md)

Build: Roadmap Planner, Diagnostics, Teaching Agent, Question Generation (within Teaching), Revision Scheduler, Analytics Dashboard, basic Ingestion pipeline.

Goal: validate measurable educational improvement on a working skeletal structure.

### Phase B

Add: memory optimization, lightweight simulations, bounded experimentation, ontology refinement.

### Phase C

Add: advanced simulations, pedagogical extraction, federated improvements, ontology evolution.

---

## Final Architecture

```text
UI Layer
        ↓
Session Orchestrators
        ↓
Educational Agents
        ↓
Deterministic Core Systems
        ↓
Knowledge Services
        ↓
Concept Objects (JSON)
+
Relationship Graph (Kuzu)
+
Vector Retrieval (Qdrant)          ← Phase B+
        ↓
Educational Knowledge Infrastructure
        ↓
Validation & Ontology Systems
        ↓
Raw Educational Assets
```

---

## Final Identity

This project is best described as:

```text
A long-term educational intelligence ecosystem that transforms educational
materials into structured knowledge and uses that knowledge to deliver
personalized, measurable, explainable learning experiences for Indian students.
```

rather than an AI tutor, a chatbot, or a simple study planner.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [final_revised_plan.md](final_revised_plan.md) | This document — north star |
| [prd.md](prd.md) | Product requirements derived from this plan |
| [implementation_plan.md](implementation_plan.md) | Phase A skeletal 8-week build (unchanged scope) |
| [trd.md](trd.md) | Technical requirements and contracts |
| [backend_schema.md](backend_schema.md) | Data model specification |
| [DESIGN.md](DESIGN.md) | UI/UX guidelines |
| [final_design_document.md](final_design_document.md) | Gap analysis: vision vs skeletal build |
