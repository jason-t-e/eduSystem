# Backend Schema Document: EduSystem

> Derived from [Final Revised Plan v1.0](final_revised_plan.md). Hybrid model: **Concept Objects** (structured store) + **Typed Relations** (graph store). Phase A uses Kuzu + SQLite. See [trd.md](trd.md) for stack evolution.

---

## 1. Storage Overview

| Layer | Phase A | Purpose |
|-------|---------|---------|
| Raw documents | `data/source_docs/`, `data/uploads/` | Educational inputs — not knowledge bases |
| Normalized markdown | `data/markdown_cache/{sha256}.md` | Canonical intermediate representation |
| Concept Objects | Kuzu `Concept` nodes (JSON-serialized fields) | Rich structured content |
| Typed Relations | Kuzu edge tables | Structural semantics (what, how, why) |
| Learner state | Kuzu `LearnerState` nodes | Per-student mastery |
| Transactional | SQLite via SQLAlchemy | Sessions, events, logs |
| Vector retrieval | — (Phase B) | Qdrant/pgvector — semantic search only |

**Kuzu note:** Nested objects are stored as JSON strings and deserialized on read.

---

## 2. Knowledge Graph (Kuzu — Shared)

**Path:** `KNOWLEDGE_GRAPH_PATH`

Populated **only** via ingestion pipeline. One node per canonical concept.

### 2.1 Node Table: `Concept` (Concept Object)

| Column | Type | Description |
|--------|------|-------------|
| `id` | `STRING` PK | Versioned ID: `{subject}_{grade}_{slug}_v{N}` |
| `name` | `STRING` | Canonical name (post ontology mapping) |
| `subject` | `STRING` | e.g. "Accountancy" |
| `grade` | `INT` | e.g. 11 |
| `version` | `INT` | Increments on update |
| `is_deprecated` | `BOOL` | Outdated knowledge flag |
| `confidence_score` | `DOUBLE` | Aggregate extraction confidence (0–1) |
| `definition` | `STRING` | Primary extracted definition |
| `intuition` | `STRING` | Plain-language summary |
| `aliases` | `STRING` | JSON: `list[str]` |
| `domain_tags` | `STRING` | JSON: `list[str]` |
| `properties` | `STRING` | JSON: `list[Property]` — `name`, `value`, `unit`, `confidence`, `source` |
| `functions` | `STRING` | JSON: `list[Function]` — `name`, `formula`, `description`, `variables`, `confidence`, `source` |
| `explanations` | `STRING` | JSON: `dict[Level, str]` — precomputed at ingestion |
| `examples` | `STRING` | JSON: `list[Example]` — `text`, `difficulty`, `steps`, `confidence`, `source` |
| `misconceptions` | `STRING` | JSON: `list[Misconception]` — `description`, `warning_signs`, `fixes`, `frequency`, `confidence`, `source` |
| `pedagogy_metadata` | `STRING` | JSON: `PedagogyMeta` — `difficulty`, `prerequisite_hints`, `teaching_notes`, `common_sticking_points` |
| `exam_metadata` | `STRING` | JSON: `ExamMeta` — `weightage`, `question_types`, `board_tags`, `chapter_ref` |
| `sources` | `STRING` | JSON: `list[SourceRef]` |
| `field_confidence` | `STRING` | JSON: `dict[str, float]` — per-field confidence |
| `explanation_quality` | `STRING` | JSON: `dict[Level, float]` — EMA from retention outcomes |

#### DDL

```sql
CREATE NODE TABLE Concept(
  id STRING,
  name STRING,
  subject STRING,
  grade INT,
  version INT,
  is_deprecated BOOL,
  confidence_score DOUBLE,
  definition STRING,
  intuition STRING,
  aliases STRING,
  domain_tags STRING,
  properties STRING,
  functions STRING,
  explanations STRING,
  examples STRING,
  misconceptions STRING,
  pedagogy_metadata STRING,
  exam_metadata STRING,
  sources STRING,
  field_confidence STRING,
  explanation_quality STRING,
  PRIMARY KEY(id)
);
```

---

## 3. Learning State Graph (Kuzu — Per-Student)

**Path:** `LEARNER_GRAPH_PATH`

One `LearnerState` node per `(student_id, concept_id)`.

### 3.1 Node Table: `LearnerState`

| Column | Type | Description |
|--------|------|-------------|
| `id` | `STRING` PK | `{student_id}_{concept_id}` |
| `student_id` | `STRING` | FK → SQLite `students.id` |
| `concept_id` | `STRING` | FK → Kuzu `Concept.id` |
| `mastery` | `DOUBLE` | 0.0–1.0 |
| `confidence` | `DOUBLE` | 0.0–1.0 self-reported |
| `calibration_error` | `DOUBLE` | `\|confidence − mastery\|` EMA |
| `forgetting_score` | `DOUBLE` | FSRS stability |
| `next_review` | `STRING` | ISO datetime |
| `explanation_level` | `STRING` | Level enum as string |
| `active_misconceptions` | `STRING` | JSON: `list[str]` |
| `attempt_history` | `STRING` | JSON: `list[Attempt]` |

#### DDL

```sql
CREATE NODE TABLE LearnerState(
  id STRING,
  student_id STRING,
  concept_id STRING,
  mastery DOUBLE,
  confidence DOUBLE,
  calibration_error DOUBLE,
  forgetting_score DOUBLE,
  next_review STRING,
  explanation_level STRING,
  active_misconceptions STRING,
  attempt_history STRING,
  PRIMARY KEY(id)
);
```

---

## 4. Typed Edge Tables

Edges carry semantic annotations — not just connectivity.

### 4.1 `REQUIRES` (Directed)

| Column | Type | Description |
|--------|------|-------------|
| `reason` | `STRING` | Why B is prerequisite for A |
| `strength` | `DOUBLE` | 0–1 prerequisite strength |
| `confidence` | `DOUBLE` | Extraction confidence |
| `source` | `STRING` | JSON: `SourceRef` |

```sql
CREATE REL TABLE REQUIRES(
  FROM Concept TO Concept,
  reason STRING, strength DOUBLE, confidence DOUBLE, source STRING
);
```

### 4.2 `PART_OF` (Directed)

| Column | Type | Description |
|--------|------|-------------|
| `container_type` | `STRING` | `chapter` \| `topic` \| `unit` \| `section` |
| `role` | `STRING` | `component` \| `subsection` \| `example_of` |
| `how` | `STRING` | How A is part of B |
| `why` | `STRING` | Pedagogical reason for grouping |
| `confidence` | `DOUBLE` | |
| `source` | `STRING` | JSON: `SourceRef` |

```sql
CREATE REL TABLE PART_OF(
  FROM Concept TO Concept,
  container_type STRING, role STRING, how STRING, why STRING,
  confidence DOUBLE, source STRING
);
```

### 4.3 `RELATES_TO` (Bidirectional)

`relation_kind`, `description`, `confidence`, `source`

### 4.4 `CONTRASTS_WITH` (Bidirectional)

`contrast_axis`, `description`, `confidence`, `source`

### 4.5 `TESTED_BY` (Directed)

`question_type`, `difficulty`, `board_ref`, `confidence`, `source`

*Phase A: target may be another Concept representing an exercise. Question bank nodes in Phase B.*

### 4.6 `CONTRADICTS` (Bidirectional)

`field`, `description`, `confidence`, `source` — cross-document disagreement, flagged for review.

### 4.7 `HAS_STATE` (Cross-Graph)

`FROM Concept TO LearnerState` — bridges knowledge graph to learner graph.

---

## 5. Relational Schema (SQLite)

### `students`

| Column | Type | Description |
|--------|------|-------------|
| `id` | `VARCHAR` PK | UUID |
| `username` | `VARCHAR` UNIQUE | Login identifier |
| `target_exam` | `VARCHAR` | Goal exam: "CBSE Board", "CA Foundation" (Phase A) |
| `exam_deadline` | `DATE` | Nullable; drives roadmap urgency |
| `study_hours_per_day` | `FLOAT` | Preference |
| `learning_stage` | `VARCHAR` | `foundation` \| `reinforcement` |
| `created_at` | `DATETIME` | |

### `sessions`

| Column | Type | Description |
|--------|------|-------------|
| `id` | `VARCHAR` PK | UUID |
| `student_id` | `VARCHAR` FK | |
| `start_time` | `DATETIME` | |
| `end_time` | `DATETIME` NULL | |
| `friction_state` | `VARCHAR` | OVERLOAD, BOREDOM, CONFUSION, DISENGAGED, NORMAL |

### `question_attempts`

| Column | Type | Description |
|--------|------|-------------|
| `id` | `VARCHAR` PK | |
| `student_id` | `VARCHAR` FK | |
| `session_id` | `VARCHAR` FK | |
| `concept_id` | `VARCHAR` | → Kuzu `Concept.id` |
| `is_correct` | `BOOLEAN` | |
| `time_taken_seconds` | `INT` | |
| `timestamp` | `DATETIME` | |

### `session_events`

| Column | Type | Description |
|--------|------|-------------|
| `event_id` | `VARCHAR` PK | |
| `student_id` | `VARCHAR` FK | |
| `event_type` | `VARCHAR` | e.g. ConceptTaught, DiagnosticStarted |
| `payload` | `JSON` | |
| `timestamp` | `DATETIME` | |

### `ingestion_log`

| Column | Type | Description |
|--------|------|-------------|
| `id` | `VARCHAR` PK | |
| `file_hash` | `VARCHAR` UNIQUE | SHA256 |
| `filename` | `VARCHAR` | |
| `status` | `VARCHAR` | COMPLETED, FAILED, FLAGGED |
| `concepts_added` | `INT` | |
| `concepts_updated` | `INT` | |
| `processed_at` | `DATETIME` | |

### `improvement_log`

Training data for concept optimization agent (Phase B+).

| Column | Type | Description |
|--------|------|-------------|
| `id` | `VARCHAR` PK | |
| `concept_id` | `VARCHAR` | |
| `explanation_level_used` | `VARCHAR` | |
| `mastery_before` | `FLOAT` | |
| `mastery_after` | `FLOAT` | |
| `misconception_hints_shown` | `JSON` | |
| `hints_effective` | `BOOLEAN` | |
| `timestamp` | `DATETIME` | |

### `improvement_proposals`

Human-reviewable queue (Human Oversight Level 2).

| Column | Type | Description |
|--------|------|-------------|
| `id` | `VARCHAR` PK | |
| `concept_id` | `VARCHAR` | |
| `proposal_type` | `VARCHAR` | UPDATE_EXPLANATION, NEW_MISCONCEPTION, etc. |
| `description` | `TEXT` | |
| `status` | `VARCHAR` | PENDING, APPROVED, REJECTED |

---

## 6. Pydantic System Contract

All models in `core/types/schemas.py`.

| Model | Maps To |
|-------|---------|
| `ConceptObject` | Kuzu `Concept` node |
| `LearnerConceptState` | Kuzu `LearnerState` node |
| `TypedRelation` | Kuzu edge tables |
| `Property`, `Function`, `Example`, `Misconception` | Nested within ConceptObject |
| `PedagogyMeta`, `ExamMeta` | Nested within ConceptObject |
| `SourceRef` | Provenance on objects, fields, and edges |

Repository layer handles JSON serialization/deserialization transparently before Kuzu driver calls.

---

## 7. Ontology Files (Not Concept Content)

```
config/ontology/{stream}/
  canonical_names.json    ← alias → canonical name
  stream_metadata.json    ← subject, grade, board
```

No syllabus, misconception, or dependency JSON. All concept content comes from ingestion.
