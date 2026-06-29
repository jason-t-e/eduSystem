# EduSystem — Phase A Implementation Plan

> **Phase A skeletal build** for [Final Revised Plan v1.0](final_revised_plan.md) · 8 weeks · Commerce 11 (Accountancy) · Local-first with Ollama
>
> Builds a **working foundation** with every *basic* feature from the Final Plan wired end-to-end. Advanced agents, full exam taxonomy, vector search, and experimentation ship in Phase B/C.

---

## 1. Product Vision & Scope

### What We're Building

Phase A delivers a runnable educational intelligence **skeleton** for Indian Class 11 Commerce students:

- **Hybrid knowledge architecture** — Concept Objects (structured store) + typed graph relationships (structural store) + per-student Learning State Graph
- **Ingestion-first** — all domain knowledge extracted from PDF/DOCX/PPT via Docling/Marker; raw files are inputs, not knowledge bases
- **Six core agents** — Diagnostic, Teaching, Revision, Roadmap, Analytics, Ingestion (orchestration via API routes; explicit orchestrator agents deferred)
- **Full learning loop** — onboard → diagnose → teach (3 modes) → revise (FSRS) → roadmap → analytics → upload materials

Powered by local Ollama. Designed for 3–5 early users to validate measurable learning improvement before Phase B expansion.

### Core Product Objectives (Priority Order)

| Tier | Objective | Includes |
|------|-----------|----------|
| **Tier 1** | Learning Correctness | Conceptual understanding, misconception reduction, retention, transfer ability |
| **Tier 2** | Exam Performance | Score improvement, syllabus completion, roadmap efficiency |
| **Tier 3** | Productive Engagement | Study consistency, sustainable workload, reduced burnout |
| **Tier 4** | Experimental Optimization | Pedagogical experimentation, adaptive refinement (deferred to month 3+) |

### What This Plan IS vs IS NOT

| ✅ Phase A Delivers | ❌ Phase A Does NOT |
|--------------------|-------------------|
| Every **basic** Final Plan feature wired end-to-end | Full 11-agent ecosystem + orchestrators |
| Hybrid Concept Objects + typed graph + ingestion pipeline | Vector retrieval, PostgreSQL JSONB, Neo4j |
| 6 agents, FSRS, friction model, basic explainability | 80/20 experimentation, memory optimization agent |
| Commerce 11 Accountancy (Domain Stage 1) | Humanities, JEE/NEET, simulations |
| Local-first (Ollama + SQLite + Kuzu) | Cloud sync, federated learning, coach dashboard |
| KPI **event logging** + dashboard for key metrics | Full analytics platform |

### Phase A Feature Coverage (Final Plan → This Build)

| Final Plan Feature | Phase A Delivery | Week |
|--------------------|------------------|------|
| Hybrid Concept Objects + Relationship Graph | Full schema + Kuzu storage | 1–2 |
| Ingestion pipeline (Docling/Marker → markdown → extract → graph) | Parsers Week 1; full pipeline Week 2; automation Week 6 | 1–2, 6 |
| Canonical ontology mapping | `ontology_mapper.py` + `canonical_names.json` | 2 |
| Provenance + confidence scoring | `SourceRef`, `field_confidence` on all artifacts | 2 |
| Basic validation pipeline | Schema validate + confidence threshold + `CONTRADICTS` flagging | 2, 6 |
| Student workflow (goal exam, deadline, study time) | `students` table + onboarding | 3, 8 |
| Exam intelligence (goal exam) | `target_exam` drives roadmap weighting via `exam_metadata` | 3, 5 |
| Diagnostic weak-prior + calibration | Self-assess (confident/weak/unknown) + adversarial traps | 3 |
| Misconception framework | Extracted misconceptions + warning_sign matching | 2, 4 |
| Worked example system (3 modes) | Worked / completion / independent by mastery | 4 |
| Progressive interleaving (Stages 1–2) | `LearningStage` on student; roadmap content mix | 4, 5, 7 |
| Level-aware teaching (5 levels) | Precomputed explanations + runtime adaptation | 2, 4 |
| FSRS revision | `RevisionAgent` + `revision.html` | 5 |
| Metacognitive layer | `metacognitive_tip_v1.j2` post-session | 7 |
| Roadmap + prerequisite ordering | Topo sort + prioritizer + time budget | 5 |
| Basic explainability | `reasons[]` on session plan items | 5 |
| Friction model + gap detection | `AnalyticsAgent` + dashboard warnings | 7 |
| Cytoscape graph visualization | Prerequisites, mastery colors, edge tooltips | 3 |
| Offline-first / multi-user | Local data, username profiles, graceful LLM fallback | 3–8 |
| Improvement log (optimization agent prep) | `improvement_log` + `improvement_proposals` | 5, 7 |
| KPI instrumentation | `session_events` + calibration/consistency on dashboard | 5, 7 |

### Key Milestones

| Milestone | When | What |
|-----------|------|------|
| **Skeleton complete** | End of Week 2 | LLM responds, both graphs initialized, schemas validate, event bus works |
| **First ingested graph** | End of Week 2 | NCERT/source PDFs ingested → Concept Objects + typed edges in Knowledge Graph |
| **First real demo** | End of Week 3 | Student self-assesses → diagnostic questions → graph colors by mastery |
| **Core teaching loop** | End of Week 5 | Teach (3 modes) → FSRS revision → roadmap with explainability |
| **Full ingestion pipeline** | End of Week 6 | Watchdog upload, synthesis, contradiction detection, Ch. 3–6 ingested |
| **Analytics + metacognition** | End of Week 7 | Friction, gaps, calibration KPIs, metacognitive tips |
| **Phase A complete** | End of Week 8 | 3-5 students onboarded; all basic Final Plan features demonstrable |

---

## 2. Architecture Overview

### Layered Architecture (8 Layers)

```
┌──────────────────────────────────────────────────────────────┐
│  UI — Static HTML/JS served by FastAPI                       │
│  onboarding · teach · dashboard · graph view · upload · rev  │
├──────────────────────────────────────────────────────────────┤
│  API — FastAPI v1, SSE streaming, versioned routes           │
│  deps.py injects all clients — swap LLM/DB/Graph freely     │
├──────────────────────────────────────────────────────────────┤
│  Agents — each isolated, communicates via typed events only  │
│  ┌──────────┬──────────┬──────────┬──────────┬─────────────┐ │
│  │Diagnostic│Teaching  │Revision  │Roadmap   │ Ingestion   │ │
│  │adversarial│level-aware│FSRS per │gap-driven│ autonomous  │ │
│  │calibratn │explanatns│concept   │ordering  │ self-improve│ │
│  └──────────┴──────────┴──────────┴──────────┴─────────────┘ │
│                      ┌──────────┐                            │
│                      │Analytics │                            │
│                      │friction + calibration                 │
│                      └──────────┘                            │
├────────────────────────────┬─────────────────────────────────┤
│ LLM — Protocol pattern    │ Scheduler — pure Python          │
│ OllamaClient · swap 1 line│ topo sort · prioritizer · FSRS  │
├────────────────────────────┴─────────────────────────────────┤
│  Core — imports NOTHING from above layers                    │
│  ┌────────────┬──────────┬────────┬──────────────────┐       │
│  │Database +  │Events    │Config  │Types / Schemas   │       │
│  │Alembic     │bus       │        │                  │       │
│  └────────────┴──────────┴────────┴──────────────────┘       │
├────────────────────────────┬─────────────────────────────────┤
│  Knowledge Graph — Kuzu    │ Learning State Graph — Kuzu     │
│  ConceptObject: definition,  │ LearnerConceptState: mastery,   │
│  properties, pedagogy, exam  │ confidence, forgetting score,   │
│  metadata + typed edges      │ active misconceptions           │
│  Shared across all learners│ Per-student, private            │
├────────────────────────────┴─────────────────────────────────┤
│  Ingestion Pipeline (all knowledge enters here — no hardcoding)│
│  PDF/DOCX/PPT → Docling/Marker → Normalized Markdown        │
│  → Structured Educational Extraction → Concept Objects      │
│  → Canonical Ontology Mapping → Knowledge Graph             │
│  → Adaptive Learning Systems                                  │
├──────────────────────────────────────────────────────────────┤
│  Self-Improving Loop (data logging now, analysis month 3+)   │
│  improvement_log → explanation_quality EMA → proposals       │
└──────────────────────────────────────────────────────────────┘
```

### Dependency Flow (strict — no upward imports)

```
frontend → api → agents → llm + scheduler → core → database/graphs
```

> [!IMPORTANT]
> `core/` imports **nothing** from layers above it. `scheduler/` is pure Python — no LLM, no DB. `agents/` imports from `core/`, `llm/`, and `scheduler/` only. These boundaries are non-negotiable.

---

## 3. Hybrid Data Model — Concept Objects + Typed Graph

> **Design principle**: All domain knowledge is **extracted from source documents** (PDF, DOCX, PPT) — never hardcoded. The hybrid stores rich **Concept Objects** (modifiable by a future optimization agent) alongside a **typed relationship graph** (structural semantics: what, how, why).

### 3.0 Ingestion Pipeline (Source of All Knowledge)

```
PDF / DOCX / PPT
       ↓
Docling / Marker          ← document parsers (Docling primary, Marker fallback)
       ↓
Normalized Markdown       ← consistent heading hierarchy, page anchors, SHA256 cache
       ↓
Structured Educational Extraction   ← LLM extracts Concept Objects per chunk
       ↓
Concept Objects           ← rich Pydantic records (definitions, properties, …)
       ↓
Canonical Ontology Mapping        ← dedup, alias resolution, cross-doc merge
       ↓
Knowledge Graph           ← Concept nodes + typed edges in Kuzu
       ↓
Adaptive Learning Systems ← Diagnostic, Teaching, Revision, Roadmap agents
```

**Provides at every stage**:
- Concrete node schemas (Concept Object fields → Kuzu node)
- Typed relationship schemas (edge type + semantic annotations)
- Provenance structure (`SourceRef` on every extracted field)
- Confidence scoring (per-field and per-edge)

### 3.1 Knowledge Graph (Kuzu — Shared)

One node per distinct concept. Lives in the shared Knowledge Graph. Never duplicated per student. Populated **only** via the ingestion pipeline.

#### Concept Object Schema (Structured Store)

Each concept is a rich object — later modifiable by a dedicated optimization agent to improve teaching effectiveness. Stored as a Kuzu node with JSON-serialized complex fields.

| Field | Type | Description |
|-------|------|-------------|
| **Identity** | | |
| `id` | `str` | `subject_grade_name_v{N}` — versioned, primary key |
| `name` | `str` | Canonical concept name (post ontology mapping) |
| `aliases` | `list[str]` | Alternate names found in source documents |
| `domain_tags` | `list[str]` | e.g. `["accounting", "commerce", "class_11"]` |
| **Definition & Structure** | | |
| `definition` | `str` | Primary extracted definition |
| `properties` | `list[Property]` | Key attributes: `name`, `value`, `unit`, `confidence`, `source` |
| `functions` | `list[Function]` | If applicable: `name`, `formula`, `description`, `variables`, `confidence` |
| **Pedagogy & Assessment** | | |
| `explanations` | `dict[Level, str]` | `eli10 / highschool / college / graduate / expert` — precomputed at ingestion |
| `intuition` | `str` | Plain-language one-paragraph summary |
| `examples` | `list[Example]` | Worked examples with difficulty, steps, source |
| `misconceptions` | `list[Misconception]` | `description`, `warning_signs`, `fixes`, `frequency`, `confidence` |
| `pedagogy_metadata` | `PedagogyMeta` | `difficulty`, `prerequisite_hints`, `teaching_notes`, `common_sticking_points` |
| `exam_metadata` | `ExamMeta` | `weightage`, `question_types`, `board_tags`, `chapter_ref` |
| **Provenance & Confidence** | | |
| `sources` | `list[SourceRef]` | `doc_id`, `page`, `paragraph`, `extraction_confidence`, `extracted_at` |
| `confidence_score` | `float` | Aggregate extraction confidence (0–1) |
| `field_confidence` | `dict[str, float]` | Per-field confidence: `definition`, `properties`, `misconceptions`, etc. |
| **Temporal & Optimization** | | |
| `version` | `int` | Increments on update; old versions kept |
| `is_deprecated` | `bool` | For outdated knowledge |
| `explanation_quality` | `dict[Level, float]` | 0–1, updated by EMA based on retention outcomes |

**Kuzu Implementation Note**: Kuzu doesn't support nested objects. All complex Concept Object fields (`properties`, `functions`, `examples`, `misconceptions`, `pedagogy_metadata`, `exam_metadata`, `sources`, `field_confidence`, etc.) are serialized as JSON strings in the Kuzu node and deserialized on read.

#### Kuzu Node Table DDL

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
  -- JSON-serialized complex fields
  aliases STRING,              -- JSON: list[str]
  domain_tags STRING,          -- JSON: list[str]
  properties STRING,           -- JSON: list[Property]
  functions STRING,            -- JSON: list[Function]
  explanations STRING,         -- JSON: dict[Level, str]
  examples STRING,             -- JSON: list[Example]
  misconceptions STRING,       -- JSON: list[Misconception]
  pedagogy_metadata STRING,    -- JSON: PedagogyMeta
  exam_metadata STRING,        -- JSON: ExamMeta
  sources STRING,              -- JSON: list[SourceRef]
  field_confidence STRING,     -- JSON: dict[str, float]
  explanation_quality STRING,  -- JSON: dict[Level, float]
  PRIMARY KEY(id)
)
```

### 3.2 Learning State Graph (Kuzu — Per-Student)

One node per `(student, concept)` pair. This is the competitive moat — continuously modeled understanding state.

#### LearnerConceptState Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Composite key |
| `student_id` | `str` | FK to student profile |
| `concept_id` | `str` | FK to ConceptObject |
| `mastery` | `float 0–1` | Derived from attempt accuracy + FSRS |
| `confidence` | `float 0–1` | Student self-reported |
| `calibration_error` | `float` | `|confidence - mastery|` — EMA tracked |
| `forgetting_score` | `float` | FSRS stability parameter |
| `next_review` | `datetime` | FSRS scheduled review date |
| `explanation_level` | `Level` | Which level this student is at for this concept |
| `active_misconceptions` | `list[str]` | Misconception IDs currently active |
| `attempt_history` | `list[Attempt]` | Last N attempts with timestamps |

#### Kuzu Node Table DDL

```sql
CREATE NODE TABLE LearnerState(
  id STRING,
  student_id STRING,
  concept_id STRING,
  mastery DOUBLE,
  confidence DOUBLE,
  calibration_error DOUBLE,
  forgetting_score DOUBLE,
  next_review STRING,       -- ISO datetime string
  explanation_level STRING, -- Level enum as string
  active_misconceptions STRING, -- JSON: list[str]
  attempt_history STRING,   -- JSON: list[Attempt]
  PRIMARY KEY(id)
)
```

### 3.3 Typed Graph Relationships (Structural Store)

Relationships carry **semantic annotations** — not just "A connects to B" but *what* the connection is, *how* it holds, and *why* it matters. Extracted during ingestion; stored as Kuzu edge tables with JSON annotation payloads.

| Relation | Direction | Semantic Fields | Description |
|----------|-----------|-----------------|-------------|
| `REQUIRES →` | Directed | `reason`, `strength`, `confidence`, `source` | A cannot be understood without B; includes why B is prerequisite |
| `PART_OF →` | Directed | `container_type`, `role`, `how`, `why`, `confidence`, `source` | What exactly B is part of, how it fits (component/chapter/section), why it belongs |
| `RELATES_TO ↔` | Bidirectional | `relation_kind`, `description`, `confidence`, `source` | Conceptual link (analogy, application, extension) |
| `CONTRASTS_WITH ↔` | Bidirectional | `contrast_axis`, `description`, `confidence`, `source` | Deliberate distinction — critical for misconception resolution |
| `TESTED_BY →` | Directed | `question_type`, `difficulty`, `board_ref`, `confidence`, `source` | Concept assessed by a question or exercise |
| `CONTRADICTS ↔` | Bidirectional | `field`, `description`, `confidence`, `source` | Cross-document disagreement (flagged for human review) |
| `HAS_STATE →` | Directed | — | ConceptObject → LearnerConceptState (learner graph only) |

#### Kuzu Edge Table DDL (example)

```sql
CREATE REL TABLE REQUIRES(
  FROM Concept TO Concept,
  reason STRING,
  strength DOUBLE,
  confidence DOUBLE,
  source STRING          -- JSON: SourceRef
);

CREATE REL TABLE PART_OF(
  FROM Concept TO Concept,
  container_type STRING,  -- "chapter" | "topic" | "unit" | "section"
  role STRING,            -- "component" | "subsection" | "example_of"
  how STRING,             -- how A is part of B
  why STRING,             -- pedagogical reason for grouping
  confidence DOUBLE,
  source STRING           -- JSON: SourceRef
);

CREATE REL TABLE RELATES_TO(FROM Concept TO Concept,
  relation_kind STRING, description STRING, confidence DOUBLE, source STRING);

CREATE REL TABLE CONTRASTS_WITH(FROM Concept TO Concept,
  contrast_axis STRING, description STRING, confidence DOUBLE, source STRING);

CREATE REL TABLE TESTED_BY(FROM Concept TO Concept,
  question_type STRING, difficulty INT, board_ref STRING, confidence DOUBLE, source STRING);
```

> [!NOTE]
> **Why hybrid?** Concept Objects hold the *content* (definitions, examples, pedagogy) that an optimization agent can rewrite in place. Typed edges hold the *structure* (prerequisites, hierarchy, contrasts) that agents traverse for sequencing and gap detection. Neither alone is sufficient.
>
> Both graphs live in Kuzu. The Knowledge Graph is a single shared database file at `KNOWLEDGE_GRAPH_PATH`. The Learning State Graph is a separate Kuzu DB file at `LEARNER_GRAPH_PATH`. Student concept state nodes link to shared concept nodes via `HAS_STATE` edges. Cytoscape.js renders both simultaneously — mastery colors the shared concept nodes per-student.

### 3.4 SQLAlchemy Relational Models (SQLite)

For relational/transactional data that doesn't belong in a graph:

| Table | Purpose |
|-------|---------|
| `students` | Profile: `username`, `target_exam`, `exam_deadline`, `study_hours_per_day`, `learning_stage` |
| `sessions` | Session tracking (start, end, student_id, friction_state) |
| `question_attempts` | Individual question attempts with timestamps |
| `session_events` | Timestamped events for analytics (fire-and-forget) |
| `ingestion_log` | Document processing records with provenance |
| `improvement_proposals` | Proposed improvements for manual review |
| `improvement_log` | Teaching outcome data for self-improvement |

---

## 4. Pydantic v2 Type System (System Contract)

All types live in a single file: [schemas.py](file:///a:/project%20edu/edusystem/core/types/schemas.py)

### Core Enums & Types

```python
Level = Literal["eli10", "highschool", "college", "graduate", "expert"]

class ConceptState(str, Enum):
    UNKNOWN = "unknown"
    SEEN = "seen"
    WEAK = "weak"      # mastery 0–0.4
    OK = "ok"          # mastery 0.4–0.7
    STRONG = "strong"  # mastery 0.7–1.0

class FrictionState(str, Enum):
    OVERLOAD = "overload"
    BOREDOM = "boredom"
    CONFUSION = "confusion"
    DISENGAGED = "disengaged"
    NORMAL = "normal"

class LearningStage(str, Enum):
    FOUNDATION = "foundation"       # Stage 1: fast coverage, worked examples
    REINFORCEMENT = "reinforcement" # Stage 2: completion problems, misconception repair

class SelfAssessLevel(str, Enum):
    CONFIDENT = "confident"
    WEAK = "weak"
    UNKNOWN = "unknown"
```

### Core Pydantic Models

```python
class Property(BaseModel):
    name: str
    value: str
    unit: str | None = None
    confidence: float = 0.0
    source: SourceRef | None = None

class Function(BaseModel):
    name: str
    formula: str | None = None
    description: str
    variables: dict[str, str] = {}
    confidence: float = 0.0
    source: SourceRef | None = None

class Example(BaseModel):
    text: str
    difficulty: int = 1               # 1–5
    steps: list[str] = []
    confidence: float = 0.0
    source: SourceRef | None = None

class Misconception(BaseModel):
    description: str
    warning_signs: list[str]
    fixes: list[str]
    frequency: float = 0.0            # 0–1 how commonly encountered
    confidence: float = 0.0
    source: SourceRef | None = None

class PedagogyMeta(BaseModel):
    difficulty: int = 1                 # 1–5
    prerequisite_hints: list[str] = []
    teaching_notes: str = ""
    common_sticking_points: list[str] = []

class ExamMeta(BaseModel):
    weightage: float = 0.0              # 0–1 relative exam importance
    question_types: list[str] = []      # e.g. ["mcq", "numerical", "journal_entry"]
    board_tags: list[str] = []          # e.g. ["cbse", "class_11"]
    chapter_ref: str | None = None

class SourceRef(BaseModel):
    document_id: str
    document_name: str
    page_number: int | None
    paragraph_index: int | None
    heading_path: str | None = None
    extraction_confidence: float
    extracted_at: datetime

class ConceptObject(BaseModel):     # maps to Kuzu Concept node — the structured store
    id: str
    name: str
    aliases: list[str] = []
    domain_tags: list[str] = []
    definition: str
    properties: list[Property] = []
    functions: list[Function] = []
    explanations: dict[str, str] = {}   # Level -> explanation text
    intuition: str = ""
    examples: list[Example] = []
    misconceptions: list[Misconception] = []
    pedagogy_metadata: PedagogyMeta = PedagogyMeta()
    exam_metadata: ExamMeta = ExamMeta()
    sources: list[SourceRef] = []
    version: int = 1
    is_deprecated: bool = False
    confidence_score: float = 0.0
    field_confidence: dict[str, float] = {}
    explanation_quality: dict[str, float] = {}

class LearnerConceptState(BaseModel):  # maps to Kuzu LearnerState node
    student_id: str
    concept_id: str
    mastery: float = 0.0              # 0–1
    confidence: float = 0.0           # 0–1
    calibration_error: float = 0.0
    forgetting_score: float = 0.0
    next_review: datetime | None = None
    explanation_level: str = "highschool"
    active_misconceptions: list[str] = []

class TypedRelation(BaseModel):       # maps to Kuzu edge tables — the structural store
    source_id: str
    target_id: str
    relation_type: Literal[
        "REQUIRES", "PART_OF", "RELATES_TO",
        "CONTRASTS_WITH", "TESTED_BY", "CONTRADICTS"
    ]
    confidence: float = 0.0
    # Semantic annotations — populated per relation type
    reason: str | None = None           # REQUIRES: why prerequisite
    strength: float | None = None       # REQUIRES: 0–1
    container_type: str | None = None     # PART_OF: chapter/topic/unit/section
    role: str | None = None             # PART_OF: component/subsection/example_of
    how: str | None = None              # PART_OF: how A is part of B
    why: str | None = None              # PART_OF: pedagogical reason
    relation_kind: str | None = None    # RELATES_TO: analogy/application/extension
    description: str | None = None        # RELATES_TO / CONTRASTS_WITH
    contrast_axis: str | None = None    # CONTRASTS_WITH: what dimension differs
    question_type: str | None = None    # TESTED_BY
    difficulty: int | None = None       # TESTED_BY
    board_ref: str | None = None        # TESTED_BY
    field: str | None = None            # CONTRADICTS: which field disagrees
    source: SourceRef | None = None

class StudentProfile(BaseModel):
    id: str
    username: str
    target_exam: str                  # Phase A: "CBSE Board" | "CA Foundation"
    exam_deadline: date | None = None
    study_hours_per_day: float = 1.0
    learning_stage: LearningStage = LearningStage.FOUNDATION

class SessionPlanItem(BaseModel):
    concept_id: str
    concept_name: str
    item_type: Literal["new", "review", "prerequisite_refresh"]
    estimated_minutes: int
    reasons: list[str]                # explainability: why this item is scheduled

class SessionPlan(BaseModel):
    student_id: str
    learning_stage: LearningStage
    items: list[SessionPlanItem]
    total_minutes: int
    summary_reason: str               # one-line explainability for the whole plan
```

### Event Dataclasses

```python
@dataclass
class SessionEvent:        # base for all events
    event_id: str
    timestamp: datetime
    student_id: str

@dataclass
class DiagnosticStarted(SessionEvent):
    concept_id: str
    confidence_rating: float

@dataclass
class AttemptRecorded(SessionEvent):
    concept_id: str
    is_correct: bool
    stated_confidence: float
    misconception_ids: list[str]

@dataclass
class ConceptTaught(SessionEvent):
    concept_id: str
    explanation_level: str
    mastery_before: float
    mastery_after: float

@dataclass
class IngestionCompleted(SessionEvent):
    document_id: str
    concepts_added: int
    concepts_updated: int

@dataclass
class ImprovementProposed(SessionEvent):
    concept_id: str
    proposal_type: str
    description: str
```

---

## 5. Technology Stack & Dependencies

### Core Dependencies ([pyproject.toml](file:///a:/project%20edu/edusystem/pyproject.toml))

| Package | Purpose |
|---------|---------|
| `fastapi` | API framework |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy[asyncio]` | Async ORM for relational data |
| `aiosqlite` | Async SQLite driver |
| `alembic` | Database migrations |
| `pydantic` | Data validation (v2) |
| `pydantic-settings` | Environment variable management |
| `httpx` | Async HTTP client (for Ollama) |
| `jinja2` | Prompt templates |
| `loguru` | Structured logging with correlation IDs |
| `kuzu` | Graph database engine |
| `watchdog` | Filesystem monitoring for ingestion |
| `docling` | PDF/DOCX parsing (primary) |
| `marker-pdf` | PDF parsing (fallback — layout-aware markdown) |
| `pymupdf4llm` | PDF parsing (tertiary fallback) |
| `python-docx` | DOCX parsing |
| `python-pptx` | PPTX parsing |
| `py-fsrs` | Spaced repetition scheduling |
| `pytest` | Testing |
| `pytest-asyncio` | Async test support |

### External Services

| Service | Purpose | Setup |
|---------|---------|-------|
| **Ollama** | Local LLM inference | Install Ollama, pull `llama3.1:8b` (fallback: `mistral:7b` if >15s response) |

### Environment Configuration ([settings.py](file:///a:/project%20edu/edusystem/config/settings.py))

All configuration from `.env` — **no hardcoded strings anywhere**.

```ini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
DB_URL=sqlite+aiosqlite:///./data/edusystem.db
KNOWLEDGE_GRAPH_PATH=./data/knowledge_graph
LEARNER_GRAPH_PATH=./data/learner_graph
WATCH_FOLDER=./data/uploads
LOG_LEVEL=DEBUG
ONTOLOGY_DIR=./config/ontology    ← canonical name mappings only, NOT concept content
SOURCE_DOCS_DIR=./data/source_docs  ← authoritative PDFs/DOCX/PPT to ingest
```

---

## 6. Verified Folder Structure

> [!NOTE]
> The structure below has been verified against the existing codebase at [edusystem/](file:///a:/project%20edu/edusystem). All listed files and directories currently exist. Files marked with `[NEEDS IMPL]` exist but are stubs that require full implementation. Files marked with `[NEEDS CREATE]` need to be added.

```
edusystem/
├── pyproject.toml                          ← single source of truth for deps + tools
├── .env                                    ← environment variables (gitignored)
├── .gitignore
├── alembic/
│   └── versions/
│       └── .gitkeep                        ← never delete migration files
│
├── config/
│   ├── settings.py                         ← pydantic-settings, all env vars here only
│   └── ontology/
│       └── commerce_11/
│           ├── canonical_names.json        ← alias → canonical name mapping (ontology only)
│           └── stream_metadata.json        ← subject, grade, board — no concept content
│
├── core/                                   ← imports NOTHING from above layers
│   ├── logging.py                          ← loguru setup with UUID correlation IDs
│   ├── explainability.py           [WEEK 5] ← build reason strings for roadmap items
│   ├── database/
│   │   ├── models.py                       ← SQLAlchemy ORM models
│   │   ├── session.py                      ← async session factory + get_db()
│   │   ├── graph.py                [NEEDS CREATE] ← KnowledgeGraph + LearnerGraph Kuzu wrappers
│   │   ├── improvement_log.py      [NEEDS CREATE] ← self-improvement data logging
│   │   └── repositories/
│   │       ├── base.py                     ← generic CRUD — all repos extend this
│   │       ├── student.py
│   │       ├── topic.py
│   │       ├── diagnostic.py
│   │       └── teaching.py
│   ├── events/
│   │   ├── bus.py                          ← EventBus: emit() + subscribe()
│   │   └── events.py                       ← all typed Event dataclasses
│   └── types/
│       └── schemas.py                      ← ALL Pydantic v2 models — the system contract
│
├── llm/                                    ← imports from core/ only
│   ├── client.py                           ← LLMClient Protocol + OllamaClient
│   ├── prompt_registry.py                  ← Jinja2 loader, versioned
│   ├── validators.py                       ← parse + retry LLM output
│   └── prompts/
│       ├── diagnostic_v1.j2                ← adversarial diagnostic questions
│       ├── teaching_explanation_v1.j2      ← level-aware explanation adaptation
│       ├── teaching_completion_v1.j2       ← completion problems for OK students
│       ├── revision_v1.j2                  ← revision session prompts
│       ├── metacognitive_tip_v1.j2         ← personalized metacognitive advice
│       ├── precompute_explanations_v1.j2  [NEEDS CREATE] ← generate all 5 explanation levels
│       ├── concept_extraction_v1.j2       [NEEDS CREATE] ← extract ConceptObjects + TypedRelations
│       ├── relation_extraction_v1.j2      [NEEDS CREATE] ← infer edges with how/why annotations
│       ├── question_generation_v1.j2      [NEEDS CREATE] ← independent questions for STRONG
│       └── misconception_remediation_v1.j2 [NEEDS CREATE] ← targeted misconception fixes
│
├── agents/                                 ← imports from core/ + llm/ + scheduler/
│   ├── base.py                             ← BaseAgent with injected dependencies
│   ├── diagnostic/
│   │   ├── agent.py                        ← DiagnosticAgent
│   │   └── tests/
│   │       └── .gitkeep
│   ├── teaching/
│   │   ├── agent.py                        ← TeachingAgent
│   │   └── tests/
│   │       └── .gitkeep
│   ├── revision/
│   │   ├── agent.py                        ← RevisionAgent
│   │   └── tests/
│   │       └── .gitkeep
│   ├── roadmap/
│   │   ├── agent.py                        ← RoadmapAgent
│   │   ├── fsrs.py                         ← py-fsrs wrapper
│   │   └── tests/
│   │       └── .gitkeep
│   ├── analytics/
│   │   ├── agent.py                        ← AnalyticsAgent
│   │   ├── friction.py                     ← FrictionState computation
│   │   ├── calibration.py                  ← Confidence calibration tracking
│   │   └── tests/
│   │       └── .gitkeep
│   └── ingestion/
│       ├── agent.py                [NEEDS CREATE] ← IngestionAgent orchestrator
│       ├── parsers.py              [WEEK 1] ← PDF/DOCX/PPTX → Docling/Marker → normalized markdown
│       ├── normalizer.py           [WEEK 1] ← heading hierarchy, page anchors, SHA256 cache
│       ├── chunker.py              [WEEK 2] ← semantic chunking by headings
│       ├── extractor.py            [WEEK 2] ← LLM structured educational extraction → ConceptObjects
│       ├── ontology_mapper.py      [WEEK 2] ← canonical name resolution + dedup
│       ├── synthesizer.py          [WEEK 6] ← cross-doc synthesis + contradiction detection
│       ├── validator.py            [WEEK 2] ← schema validation + confidence thresholds
│       ├── watchdog.py             [WEEK 6] ← filesystem watcher for WATCH_FOLDER
│       └── tests/
│           └── .gitkeep
│
├── scheduler/                              ← pure Python, no LLM, no DB ever
│   ├── dependency_graph.py                 ← topological sort from REQUIRES edges
│   └── topic_prioritizer.py               ← score = exam_metadata.weightage × (1-mastery) × prereq_readiness
│
├── api/                                    ← imports from agents/ + core/ only
│   ├── main.py                             ← FastAPI app creation + lifespan
│   ├── deps.py                             ← get_db(), get_llm(), get_event_bus(), get_graphs()
│   └── v1/
│       ├── router.py                       ← central router aggregator
│       ├── health.py                       ← GET /health
│       ├── diagnostic.py                   ← diagnostic endpoints
│       ├── teaching.py                     ← teaching endpoints
│       ├── revision.py                     ← revision endpoints
│       ├── roadmap.py                      ← roadmap endpoints
│       ├── analytics.py                    ← analytics + friction endpoints
│       └── ingest.py              [NEEDS CREATE] ← upload + ingestion status endpoints
│
├── frontend/
│   ├── index.html                          ← onboarding flow
│   ├── topic_list.html                     ← chapter/topic browser
│   ├── teach.html                          ← teaching interface
│   ├── dashboard.html                      ← student dashboard
│   ├── revision.html                       ← revision session
│   ├── upload.html                [NEEDS CREATE] ← document upload + progress
│   └── app.js                              ← shared JavaScript
│
├── scripts/
│   ├── test_ollama.py                      ← LLM connectivity test
│   ├── ingest_source_docs.py      [NEEDS CREATE] ← batch-ingest SOURCE_DOCS_DIR → Knowledge Graph
│   └── precompute_explanations.py [NEEDS CREATE] ← batch precompute all 5 levels post-extraction
│
├── data/                          [NEEDS CREATE] ← runtime data directory
│   ├── source_docs/                        ← authoritative NCERT/textbook files to ingest
│   ├── knowledge_graph/                    ← Kuzu DB files (populated by ingestion only)
│   ├── learner_graph/                      ← Kuzu DB files
│   ├── uploads/                            ← watchdog-monitored folder (user uploads)
│   ├── markdown_cache/                     ← cached normalized markdown (by SHA256)
│   └── edusystem.db                        ← SQLite database
│
├── logs/
│   └── edusystem.log                       ← loguru output
│
└── tests/
    ├── unit/
    │   └── .gitkeep
    └── integration/
        └── .gitkeep
```

---

## 7. API Route Specification

### Health & Graph

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/health` | Kuzu status ×2, Ollama ping, DB status, version |
| `GET` | `/api/v1/graph/{concept_id}` | Subgraph as Cytoscape.js JSON |
| `GET` | `/api/v1/graph/{concept_id}/learner/{student_id}` | Same + LearnerConceptState enrichment |

### Diagnostic

| Method | Route | Purpose |
|--------|-------|---------|
| `POST` | `/api/v1/diagnostic/self-assess` | Topic list + confidence ratings → initial LearnerConceptState |
| `POST` | `/api/v1/diagnostic/start/{concept_id}` | Returns adversarial diagnostic questions |
| `POST` | `/api/v1/diagnostic/submit` | Answers → updated concept states with misconception detection |

### Teaching

| Method | Route | Purpose |
|--------|-------|---------|
| `POST` | `/api/v1/teach/{concept_id}` | Level-aware teaching with SSE streaming |
| `POST` | `/api/v1/teach/evaluate` | Evaluate student response, trigger misconception remediation |

### Revision

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/api/v1/revision/{student_id}/due` | Concepts due for FSRS review |
| `POST` | `/api/v1/revision/complete` | Mark review complete, update FSRS |

### Roadmap

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/api/v1/roadmap/{student_id}` | Full session plan (reviews + new concepts) |
| `POST` | `/api/v1/roadmap/{student_id}/plan` | Generate session plan for available_minutes |

### Analytics

| Method | Route | Purpose |
|--------|-------|---------|
| `POST` | `/api/v1/analytics/event` | Fire-and-forget session event logging |
| `GET` | `/api/v1/analytics/{student_id}/friction` | Current friction state + recommendations |
| `GET` | `/api/v1/analytics/{student_id}/gaps` | Knowledge gap detection results |
| `GET` | `/api/v1/analytics/{student_id}/calibration` | Confidence calibration metrics |
| `GET` | `/api/v1/analytics/{student_id}/misconceptions` | Top persistent misconceptions |

### Ingestion

| Method | Route | Purpose |
|--------|-------|---------|
| `POST` | `/api/v1/ingest/upload` | Multipart upload → copies to WATCH_FOLDER, returns job_id |
| `GET` | `/api/v1/ingest/status/{job_id}` | SSE stream of ingestion progress |

### Improvement

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/api/v1/improve/proposals` | Current improvement proposals for manual review |

### Students

| Method | Route | Purpose |
|--------|-------|---------|
| `POST` | `/api/v1/students/register` | Username-only registration |
| `GET` | `/api/v1/students/{student_id}` | Profile data |

---

## 8. Prompt Template Inventory

| Template | Version | Input | Output | Used By |
|----------|---------|-------|--------|---------|
| `diagnostic_v1.j2` | v1 | concept name, definition, misconception warning_signs | JSON array of adversarial questions | DiagnosticAgent |
| `teaching_explanation_v1.j2` | v1 | precomputed explanation, active_misconceptions, level | Adapted explanation + worked example | TeachingAgent |
| `teaching_completion_v1.j2` | v1 | concept, mastery level | Completion problem JSON | TeachingAgent |
| `question_generation_v1.j2` | v1 | concept, difficulty | Independent question JSON | TeachingAgent |
| `misconception_remediation_v1.j2` | v1 | wrong answer, matched misconception | Targeted correction explanation | TeachingAgent |
| `precompute_explanations_v1.j2` | v1 | concept name, definition, subject, grade | All 5 explanation levels as JSON dict | ingest script |
| `concept_extraction_v1.j2` | v1 | text chunk, heading path | JSON: ConceptObjects + TypedRelations with provenance | IngestionAgent |
| `relation_extraction_v1.j2` | v1 | two concept names, chunk context | JSON: TypedRelation with how/why annotations | IngestionAgent |
| `revision_v1.j2` | v1 | concept, last attempt, mastery | Revision question + recall prompt | RevisionAgent |
| `metacognitive_tip_v1.j2` | v1 | session summary, calibration trend, misconception pattern | 2-3 specific actionable tips | AnalyticsAgent |

---

## 9. Week-by-Week Implementation Plan

---

### Phase 0 — Skeleton (Weeks 1–2)

---

#### Week 1: Project skeleton + hybrid schemas + ingestion foundations (~35 hrs)

**End state**: LLM responds via OllamaClient, both Kuzu graphs initialized with hybrid schemas (Concept Objects + typed edges), all Pydantic v2 types validate, basic document parsers produce normalized markdown from PDF/DOCX/PPT.

##### Day 1 — Project structure and tooling

- [ ] Verify/update [pyproject.toml](file:///a:/project%20edu/edusystem/pyproject.toml) with all dependencies pinned (include `docling`, `marker-pdf`)
- [ ] Implement [config/settings.py](file:///a:/project%20edu/edusystem/config/settings.py) fully with pydantic-settings: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `DB_URL`, `KNOWLEDGE_GRAPH_PATH`, `LEARNER_GRAPH_PATH`, `WATCH_FOLDER`, `SOURCE_DOCS_DIR`, `ONTOLOGY_DIR`, `LOG_LEVEL`
- [ ] Install Ollama, pull `llama3.1:8b`. If response time >15s for short prompts, use `mistral:7b`
- [ ] Implement [core/logging.py](file:///a:/project%20edu/edusystem/core/logging.py) — every request gets a UUID correlation ID that flows through every log line
- [ ] Create `data/source_docs/` — place NCERT Accountancy Ch. 1–2 PDFs here (no hardcoded concept JSON)

##### Day 2–3 — All Pydantic schemas (hybrid model)

- [ ] Write all schemas in [core/types/schemas.py](file:///a:/project%20edu/edusystem/core/types/schemas.py):
  - `Level`, `Property`, `Function`, `Example`, `Misconception`, `PedagogyMeta`, `ExamMeta`, `SourceRef`
  - `ConceptObject` — full structured store: `definition`, `properties`, `functions`, `examples`, `misconceptions`, `pedagogy_metadata`, `exam_metadata`, `field_confidence`, `confidence_score`, `sources`, `explanations`, `version`
  - `TypedRelation` — structural store with semantic annotations: `REQUIRES` (reason, strength), `PART_OF` (container_type, role, how, why), `RELATES_TO`, `CONTRASTS_WITH`, `TESTED_BY`, `CONTRADICTS`
  - `LearnerConceptState` with mastery, confidence, calibration_error, forgetting_score, next_review, explanation_level, active_misconceptions
  - `StudentProfile`, `SessionPlan`, `SessionPlanItem` — student workflow + explainability
- [ ] Write all enums: `ConceptState`, `FrictionState`, `LearningStage`, `SelfAssessLevel`
- [ ] Write all event dataclasses: `SessionEvent`, `AttemptRecorded`, `ConceptTaught`, `DiagnosticStarted`, `IngestionCompleted`, `ImprovementProposed`

##### Day 3–4 — Dual Kuzu graph setup + SQLite

- [ ] Create `core/database/graph.py`:
  - `KnowledgeGraph` class wrapping Kuzu at `KNOWLEDGE_GRAPH_PATH` with Concept node table + typed edge tables (`REQUIRES`, `PART_OF`, `RELATES_TO`, `CONTRASTS_WITH`, `TESTED_BY`, `CONTRADICTS`)
  - `LearnerGraph` class wrapping separate Kuzu at `LEARNER_GRAPH_PATH` with LearnerState node table + `HAS_STATE` edges
  - CRUD for `ConceptObject` upsert and `TypedRelation` insert with provenance
- [ ] Implement SQLAlchemy async models in [core/database/models.py](file:///a:/project%20edu/edusystem/core/database/models.py): `students` (include `target_exam`, `exam_deadline`, `learning_stage`), `sessions`, `question_attempts`, `session_events`, `ingestion_log`, `improvement_proposals`
- [ ] Run first Alembic migration

##### Day 5 — LLM client + event bus + basic ingestion parsers

- [ ] Implement [llm/client.py](file:///a:/project%20edu/edusystem/llm/client.py): `LLMClient(Protocol)` with `complete(system, user) -> str` and `stream(system, user) -> AsyncIterator[str]`. `OllamaClient` implementing it with httpx async, 3-retry exponential backoff
- [ ] Implement [core/events/bus.py](file:///a:/project%20edu/edusystem/core/events/bus.py): async `emit(event)` + `subscribe(type, handler)`
- [ ] Implement [core/database/repositories/base.py](file:///a:/project%20edu/edusystem/core/database/repositories/base.py): generic CRUD
- [ ] Create `agents/ingestion/parsers.py`:
  - Route by extension: `.pdf` → Docling (fallback Marker, then pymupdf4llm), `.docx` → Docling/python-docx, `.pptx` → python-pptx
  - Return raw markdown string per document
- [ ] Create `agents/ingestion/normalizer.py`:
  - Normalize heading hierarchy (`#` / `##` / `###`), inject page anchors, strip artifacts
  - Cache output at `data/markdown_cache/{sha256}.md`
- [ ] Write unit tests: LLM client, event bus, parser round-trip on a sample PDF — **all green before moving on**

> [!IMPORTANT]
> **Checkpoint**: OllamaClient test passes · both Kuzu graphs init with hybrid schemas · `ConceptObject` + `TypedRelation` validate · sample PDF → normalized markdown cached · event bus test green · Alembic migration runs

---

#### Week 2: Extraction pipeline → populated Knowledge Graph (~35 hrs)

**End state**: NCERT Accountancy Ch. 1–2 ingested end-to-end. 40+ Concept Objects in Kuzu with typed edges (REQUIRES, PART_OF, etc.) carrying semantic annotations. Every concept has all 5 explanation levels precomputed. Prompt registry + FastAPI skeleton with /health and /graph endpoints.

> [!NOTE]
> **No hardcoded concept data.** All definitions, misconceptions, properties, and relationships come from document extraction. `config/ontology/commerce_11/canonical_names.json` holds alias mappings only — not concept content.

##### Day 1 — Semantic chunker + extraction prompt

- [ ] Create `agents/ingestion/chunker.py`: split normalized markdown by H2/H3 headings. Chunks 300–600 tokens. Prepend heading path. Return `list[Chunk(text, heading_path, source_file, page_estimate, chunk_index)]`
- [ ] Write `llm/prompts/concept_extraction_v1.j2`: given chunk + heading path → JSON with 1–5 `ConceptObject` stubs (definition, properties, functions, misconceptions, examples, pedagogy_metadata, exam_metadata) + `TypedRelation` stubs (REQUIRES, PART_OF with how/why, RELATES_TO, CONTRASTS_WITH, TESTED_BY). Every field includes `SourceRef` + per-field confidence

##### Day 2 — Extractor + ontology mapper

- [ ] Create `agents/ingestion/extractor.py`: loops chunks → LLM → validates against `ConceptObject` + `TypedRelation` schemas via `parse_with_retry`
- [ ] Create `agents/ingestion/ontology_mapper.py`: resolve aliases via `canonical_names.json`, dedup by name+definition similarity, assign canonical IDs (`commerce_11_{slug}_v1`)
- [ ] Create `agents/ingestion/validator.py`: Phase A validation subset — schema validate, reject concepts below confidence threshold (default 0.6), flag low-confidence edges and `CONTRADICTS` candidates for `improvement_proposals` queue

##### Day 3 — Batch ingest script + explanation precomputation

- [ ] Write `scripts/ingest_source_docs.py`: `SOURCE_DOCS_DIR` → parsers → normalizer → chunker → extractor → ontology_mapper → KnowledgeGraph upsert. Log to `ingestion_log` table
- [ ] Write `llm/prompts/precompute_explanations_v1.j2`: given extracted definition + properties → generate all 5 explanation levels. Return JSON dict
- [ ] Write `scripts/precompute_explanations.py`: loops ingested concepts missing explanations, calls LLM, updates KnowledgeGraph

##### Day 4 — Prompt registry + validators

- [ ] Implement [llm/prompt_registry.py](file:///a:/project%20edu/edusystem/llm/prompt_registry.py): Jinja2 loader from `llm/prompts/`, method `render(name, version, **ctx) -> str`. Falls back to latest version. Logs which version was rendered
- [ ] Implement [llm/validators.py](file:///a:/project%20edu/edusystem/llm/validators.py): `parse_with_retry(raw, schema, retries=2)` — strips markdown fences, tries json.loads, validates against Pydantic schema, on failure sends correction prompt to LLM

##### Day 5 — FastAPI skeleton + graph endpoint

- [ ] Implement [api/main.py](file:///a:/project%20edu/edusystem/api/main.py) + [api/deps.py](file:///a:/project%20edu/edusystem/api/deps.py): inject KnowledgeGraph, LearnerGraph, LLMClient, AsyncSession, EventBus
- [ ] Implement `GET /health`: Kuzu status ×2, Ollama ping, DB status, concept count from ingestion
- [ ] Implement `GET /api/v1/graph/{concept_id}`: returns subgraph as Cytoscape.js JSON (nodes = ConceptObjects, edges = TypedRelations with annotations)
- [ ] Implement `GET /api/v1/graph/{concept_id}/learner/{student_id}`: same + LearnerConceptState enrichment
- [ ] Run `ingest_source_docs.py` on NCERT Ch. 1–2. Verify: `MATCH (a)-[:REQUIRES]->(b) RETURN a.name, b.reason`

> [!IMPORTANT]
> **Checkpoint**: 40+ ingested Concept Objects · typed edges with how/why annotations · all concepts have 5 precomputed explanation levels · /graph returns valid Cytoscape JSON · /health green

---

### Phase 1 — Core Teaching Loop (Weeks 3–5)

---

#### Week 3: Student workflow + diagnostic + first frontend (~35 hrs)

**End state**: Student registers with goal exam + deadline, self-assesses topics (confident/weak/unknown), receives adversarial calibration questions, LearnerConceptState nodes update, Cytoscape graph renders with typed edges and mastery coloring. First real demo.

##### Day 1 — Student profile + registration

- [ ] Implement `POST /api/v1/students/register` and `GET /api/v1/students/{id}`: username, `target_exam` (CBSE Board / CA Foundation), `exam_deadline`, `study_hours_per_day`, default `learning_stage=FOUNDATION`
- [ ] Implement [core/database/repositories/student.py](file:///a:/project%20edu/edusystem/core/database/repositories/student.py): CRUD for StudentProfile

##### Day 2–3 — Diagnostic agent

- [ ] Implement [agents/base.py](file:///a:/project%20edu/edusystem/agents/base.py): BaseAgent with injected `(llm, db, knowledge_graph, learner_graph, bus, logger)`. No agent instantiates anything
- [ ] Implement [agents/diagnostic/agent.py](file:///a:/project%20edu/edusystem/agents/diagnostic/agent.py):
  - `self_assess(student_id, ratings: dict[concept_id, SelfAssessLevel])`: maps confident→0.7, weak→0.3, unknown→0.0 initial confidence; creates LearnerConceptState stubs
  - `run_calibration(student_id, concept_id)`: fetches ConceptObject misconceptions; renders `diagnostic_v1.j2` with transfer questions + trap cues from `warning_signs`; emits `DiagnosticStarted`
  - `score_attempt(attempt) -> LearnerConceptState`: updates mastery, active_misconceptions, `calibration_error = |confidence − mastery|`; emits `AttemptRecorded`
- [ ] Implement [api/v1/diagnostic.py](file:///a:/project%20edu/edusystem/api/v1/diagnostic.py): thin routes for self-assess, start, submit

##### Day 4–5 — Frontend v1 + graph

- [ ] Wire [frontend/index.html](file:///a:/project%20edu/edusystem/frontend/index.html): step 1 — register (name, goal exam, deadline, study hours)
- [ ] Wire [frontend/topic_list.html](file:///a:/project%20edu/edusystem/frontend/topic_list.html): self-assess each chapter (confident / weak / unknown buttons) + mastery badges
- [ ] Implement Cytoscape.js in [frontend/app.js](file:///a:/project%20edu/edusystem/frontend/app.js):
  - Nodes colored by mastery; edges styled by type (`REQUIRES` solid, `PART_OF` dashed, `CONTRASTS_WITH` dotted)
  - Edge tooltips show `how`/`why`/`reason` from TypedRelation annotations
  - Click node → definition snippet, mastery, next_review, active_misconceptions
- [ ] End-to-end test: register → self-assess → diagnostic on 1 concept → graph updates

> [!IMPORTANT]
> **Checkpoint**: Student workflow complete · weak-prior self-assess works · calibration_error computed · graph shows typed edges · first demo end-to-end

---

#### Week 4: Teaching agent — 3 modes + learning stages (~35 hrs)

**End state**: TeachingAgent delivers worked examples (FOUNDATION stage / low mastery), completion problems (REINFORCEMENT / OK mastery), or independent problems (strong mastery). Misconception-targeted remediation on wrong answers. Teaching API + frontend wired.

##### Day 1–2 — Teaching prompts

- [ ] Implement `teaching_explanation_v1.j2`: adapt precomputed explanation for active_misconceptions + generate contextual worked example (Stage 1 / novice mode)
- [ ] Implement `teaching_completion_v1.j2`: completion problem with missing steps (Stage 2 / transition mode)
- [ ] Implement `question_generation_v1.j2`: independent question (mastery evaluation mode)
- [ ] Implement `misconception_remediation_v1.j2`: targeted correction from matched `warning_signs`

##### Day 3–4 — Teaching agent + evaluation

- [ ] Implement [agents/teaching/agent.py](file:///a:/project%20edu/edusystem/agents/teaching/agent.py):
  - `select_mode(student, learner_state)`: FOUNDATION stage + mastery < 0.4 → worked example; REINFORCEMENT + mastery 0.4–0.7 → completion; mastery > 0.7 → independent
  - `teach(student_id, concept_id)`: streams SSE response; updates `explanation_level` on readiness; emits `ConceptTaught`
  - `evaluate_response(...)`: deterministic checks first (e.g. debit=credit), then LLM; match wrong answers to misconception `warning_signs`; update `active_misconceptions`
- [ ] Implement [api/v1/teaching.py](file:///a:/project%20edu/edusystem/api/v1/teaching.py): teach + evaluate routes
- [ ] Write tests: mode selection by mastery + learning_stage; misconception fix on wrong answer (mocked LLM)

##### Day 5 — Teach page frontend

- [ ] Implement [frontend/teach.html](file:///a:/project%20edu/edusystem/frontend/teach.html): level badge, mode indicator (worked/completion/independent), SSE stream, answer input, misconception hint, level-up notification
- [ ] Graceful fallback: if LLM fails → serve cached precomputed explanation from KnowledgeGraph

> [!IMPORTANT]
> **Checkpoint**: All 3 teaching modes work · stage-aware mode selection · misconception remediation · LLM fallback to cached explanation

---

#### Week 5: Revision + roadmap + explainability + KPI logging (~35 hrs)

**End state**: Full core loop — FSRS revision sessions, roadmap with explainable session plans, learning-stage-aware prioritization, improvement log active. Dashboard shows today's plan with reasons.

##### Day 1 — FSRS + RevisionAgent

- [ ] Implement [agents/roadmap/fsrs.py](file:///a:/project%20edu/edusystem/agents/roadmap/fsrs.py): wraps `py-fsrs`; updates `forgetting_score`, `next_review`; subscribes to `AttemptRecorded`
- [ ] Implement [agents/revision/agent.py](file:///a:/project%20edu/edusystem/agents/revision/agent.py): `get_due(student_id)`, `run_review(student_id, concept_id)` using `revision_v1.j2`
- [ ] Implement [api/v1/revision.py](file:///a:/project%20edu/edusystem/api/v1/revision.py): `GET /revision/{uid}/due`, `POST /revision/complete`

##### Day 2–3 — Roadmap + explainability

- [ ] Implement [scheduler/dependency_graph.py](file:///a:/project%20edu/edusystem/scheduler/dependency_graph.py): topological sort on `REQUIRES` edges
- [ ] Implement [scheduler/topic_prioritizer.py](file:///a:/project%20edu/edusystem/scheduler/topic_prioritizer.py): `score = exam_metadata.weightage × (1−mastery) × prereq_readiness × deadline_urgency`
- [ ] Implement [core/explainability.py](file:///a:/project%20edu/edusystem/core/explainability.py): `build_reasons(concept, learner_state, item_type) -> list[str]`
- [ ] Implement [agents/roadmap/agent.py](file:///a:/project%20edu/edusystem/agents/roadmap/agent.py): `get_session_plan() -> SessionPlan` with `reasons[]` per item; respects `learning_stage`; 15 min/new, 5 min/review
- [ ] Implement [api/v1/roadmap.py](file:///a:/project%20edu/edusystem/api/v1/roadmap.py): roadmap endpoints

##### Day 4 — Improvement log + KPI events

- [ ] Create `core/database/improvement_log.py`: log per `ConceptTaught` event
- [ ] Explanation quality EMA on FSRS recall outcomes
- [ ] `session_events` captures KPI derivation data (session start/end, teach, review, friction)

##### Day 5 — Dashboard + revision UI

- [ ] Implement [frontend/dashboard.html](file:///a:/project%20edu/edusystem/frontend/dashboard.html): session plan with per-item reason tooltips, streak, mastery donut, review calendar, calibration trend, learning stage badge
- [ ] Implement [frontend/revision.html](file:///a:/project%20edu/edusystem/frontend/revision.html): FSRS due list, recall prompt, mark complete

> [!IMPORTANT]
> **Checkpoint**: FSRS + revision UI · explainable SessionPlan · learning stage affects plan · improvement log · dashboard shows reasons

---

### Phase 2 — Ingestion Automation + Analytics (Weeks 6–8)

---

#### Week 6: Autonomous ingestion + cross-document synthesis (~35 hrs)

**End state**: Drop a PDF/DOCX/PPTX into watch folder → full pipeline runs automatically (parse → extract → ontology map → merge → precompute). Multi-document synthesis handles duplicates and contradictions. Upload UI with live progress.

> [!NOTE]
> Basic ingestion (parsers, normalizer, chunker, extractor) is built in Weeks 1–2. Week 6 adds automation, synthesis, and the upload interface.

##### Day 1 — IngestionAgent orchestrator + watchdog

- [ ] Create `agents/ingestion/agent.py`: orchestrates the full pipeline as a single async job with SSE progress events (`parsing`, `chunking`, `extracting`, `mapping`, `precomputing`, `merging`, `done`)
- [ ] Create `agents/ingestion/watchdog.py`: monitors `WATCH_FOLDER`, triggers IngestionAgent on new files. Background thread alongside FastAPI

##### Day 2 — Cross-document synthesis

- [ ] Create `agents/ingestion/synthesizer.py`:
  - Same canonical name + similar definition → UPSERT (merge Concept Objects, union provenance, max confidence)
  - Same name + different definition → `CONTRADICTS` edge + flag for review
  - Overlapping domain_tags + no existing edge → LLM infers `REQUIRES` / `RELATES_TO` with how/why annotations if confidence > 0.8
- [ ] Enforce rule: a concept without all 5 explanation levels never enters the teaching flow

##### Day 3 — Remaining chapters + quality pass

- [ ] Ingest NCERT Accountancy Ch. 3–5 via `ingest_source_docs.py`
- [ ] Review low-confidence extractions flagged by validator. Tune extraction prompt if systematic gaps found
- [ ] Verify PART_OF edges form correct chapter hierarchy with `how`/`why` annotations

##### Day 4–5 — Upload API + upload page

- [ ] Create `api/v1/ingest.py`: `POST /api/v1/ingest/upload` + `GET /api/v1/ingest/status/{job_id}` (SSE progress)
- [ ] Create `frontend/upload.html`: drag-drop zone, live progress bar, result summary (concepts added, edges created, contradictions flagged)

> [!WARNING]
> Docling takes 10–30s per page locally. Cap uploads at 25 pages with a clear message. Async queue for larger files comes in month 3.

> [!IMPORTANT]
> **Checkpoint**: Drop NCERT Chapter 6 PDF → auto-ingested with provenance → graph updated → new concepts appear in study plan · contradictions flagged · upload UI works

---

#### Week 7: Analytics + friction + learning stage progression (~30 hrs)

**End state**: Friction adjusts session plans. Gap detection surfaces hidden prerequisite failures. Metacognitive tips post-session. KPI dashboard shows calibration + consistency. Student auto-advances FOUNDATION → REINFORCEMENT when ready.

##### Day 1–2 — AnalyticsAgent + friction

- [ ] Implement [agents/analytics/agent.py](file:///a:/project%20edu/edusystem/agents/analytics/agent.py): orchestrates friction, gaps, calibration, metacognitive tips
- [ ] Implement [agents/analytics/friction.py](file:///a:/project%20edu/edusystem/agents/analytics/friction.py): BOREDOM / OVERLOAD / CONFUSION / DISENGAGED rules; RoadmapAgent reads friction to adjust next plan
- [ ] Implement [api/v1/analytics.py](file:///a:/project%20edu/edusystem/api/v1/analytics.py): event, friction, gaps, calibration, misconceptions endpoints
- [ ] Gap detection: mastery > 0.6 but `REQUIRES`-linked concept mastery < 0.4 → dashboard warnings with prerequisite refresh in next plan

##### Day 3 — KPI dashboard + learning stage progression

- [ ] Dashboard KPI widgets: calibration error trend, study consistency (days/week from `session_events`), session completion rate
- [ ] Auto-advance `learning_stage`: FOUNDATION → REINFORCEMENT when ≥ 60% of chapter concepts have mastery ≥ 0.4 (configurable threshold)
- [ ] Misconception analytics: top 3 persistent `active_misconceptions` with fixes from ConceptObject

##### Day 4–5 — Metacognition + improvement proposals

- [ ] Implement `metacognitive_tip_v1.j2`: actionable tips shown on dashboard after each session
- [ ] `GET /api/v1/improve/proposals`: queue from low-confidence ingestions + improvement_log patterns (Human Oversight Level 2 seed)
- [ ] Wire friction → roadmap: OVERLOAD reduces next session 30%; CONFUSION inserts prerequisite review

> [!IMPORTANT]
> **Checkpoint**: Friction changes next plan · gap warnings visible · learning stage auto-progresses · KPI widgets live · metacognitive tips specific

---

#### Week 8: Polish onboarding + offline resilience + early users (~25 hrs)

**End state**: Complete onboarding under 10 minutes. Full loop demonstrable offline (cached explanations). 3–5 real students validated.

##### Day 1–2 — Complete onboarding flow

- [ ] Polish [frontend/index.html](file:///a:/project%20edu/edusystem/frontend/index.html) full 4-step flow:
  1. Register — name, goal exam, exam deadline, study hours/day
  2. Self-assess all ingested chapters (confident / weak / unknown)
  3. Auto-diagnostic on top 3 confident topics
  4. First explainable session plan + graph view ("wow" moment)
- [ ] Profile switcher for multi-user shared devices; `student_id` on every query

##### Day 3 — Offline resilience + integration test

- [ ] Verify teach flow works with Ollama stopped (cached precomputed explanations served)
- [ ] Verify revision + dashboard work fully offline (local Kuzu + SQLite)
- [ ] Run `pytest tests/integration/test_full_flow.py`: register → self-assess → diagnose → teach → revise → roadmap

##### Day 4 — Bug bash

- [ ] Full flow 5× as different fictional students; fix crashes → wrong outputs → UX confusion
- [ ] Every 500 → graceful degraded response + correlation ID in logs

##### Day 5 — Ship to early users

- [ ] `setup.sh`: migrations → `ingest_source_docs.py` → `precompute_explanations.py` → start server
- [ ] Test on a machine that isn't yours
- [ ] 3–5 Class 11 Commerce students; observe silently; schedule 5-day follow-up

> [!IMPORTANT]
> **Final Checkpoint**: All basic Final Plan features demonstrable in one session · offline teach works · real student feedback collected

---

## 10. What You Have at End of Week 8 (Phase A Complete)

Every **basic** feature from [Final Revised Plan v1.0](final_revised_plan.md) is wired and demonstrable:

| Final Plan Basic Feature | Phase A Status |
|--------------------------|----------------|
| Hybrid Concept Objects + typed Relationship Graph | ✅ |
| Ingestion pipeline (no hardcoded knowledge) | ✅ |
| Canonical ontology + provenance + confidence | ✅ |
| Basic validation (schema, threshold, CONTRADICTS) | ✅ |
| Student workflow (goal exam, deadline, study time) | ✅ |
| Diagnostic weak-prior + calibration | ✅ |
| Misconception taxonomy + remediation | ✅ |
| Worked example system (3 modes) | ✅ |
| Progressive interleaving (Stages 1–2) | ✅ |
| Level-aware teaching (5 levels) | ✅ |
| FSRS revision + RevisionAgent | ✅ |
| Roadmap + prerequisite ordering | ✅ |
| Basic explainability (reasons on session plan) | ✅ |
| Metacognitive tips | ✅ |
| Friction model + gap detection | ✅ |
| Cytoscape visualization (edges + mastery) | ✅ |
| Offline-first + multi-user | ✅ |
| KPI event logging + dashboard metrics | ✅ |
| Improvement log (optimization agent prep) | ✅ |
| Upload + autonomous ingestion | ✅ |
| 3–5 validated students | ✅ |

---

## 11. Deliberately Deferred (Phase B/C)

| Feature | Phase | Why Deferred |
|---------|-------|-------------|
| Master + Session Orchestrator agents | B | API routes sufficient for skeletal validation |
| Teaching Strategy Agent (separate) | B | Mode selection inside TeachingAgent |
| Memory Optimization Agent | B | Not needed for core loop validation |
| Validation Agent (full 6-stage pipeline) | B | Basic validator sufficient for Phase A |
| 80/20 adaptive experimentation | B | Needs baseline KPI data |
| Exam taxonomy (necessary/optional exams) | B | Board/CA goal exam sufficient for Commerce 11 |
| Interleaving Stages 3–4 (integration, optimization) | B | Stages 1–2 validate the architecture |
| Vector retrieval (Qdrant/pgvector) | B | Graph + Concept Objects sufficient |
| Image ingestion | B | PDF/DOCX/PPT first |
| Full explainability layer | B | Per-item reasons sufficient for Phase A |
| Human oversight Levels 2–3 (full) | B/C | improvement_proposals queue seeds Level 2 |
| Concept optimization agent | B | Needs improvement_log data |
| PostgreSQL JSONB, Neo4j, MinIO/S3 | B/C | SQLite + Kuzu sufficient at current scale |
| Coach dashboard, federated learning, social layer | C | Post-validation |
| Deep simulations, cloud sync | C | Domain and infrastructure not ready |
| Additional streams (Economics, JEE/NEET, etc.) | B+ | Commerce 11 validates infrastructure |

---

## 12. Verification Plan

### Automated Tests

| Test Type | What | Command |
|-----------|------|---------|
| Unit — schemas | All Pydantic models validate with sample data | `pytest tests/unit/test_schemas.py` |
| Unit — event bus | emit → subscribe → handler called | `pytest tests/unit/test_events.py` |
| Unit — LLM client | OllamaClient completes prompt (mocked) | `pytest tests/unit/test_llm.py` |
| Unit — graph ops | Kuzu CRUD on both graphs | `pytest tests/unit/test_graph.py` |
| Unit — FSRS | py-fsrs schedules correctly | `pytest tests/unit/test_fsrs.py` |
| Unit — scheduler | Topological sort + prioritizer deterministic | `pytest tests/unit/test_scheduler.py` |
| Unit — agents | Mocked LLM, verify correct prompt selection + output routing | `pytest tests/unit/test_agents.py` |
| Integration | Full flow: register → self-assess → diagnose → teach → revise → roadmap | `pytest tests/integration/test_full_flow.py` |
| Unit — explainability | SessionPlanItem reasons generated deterministically | `pytest tests/unit/test_explainability.py` |
| Unit — learning stage | FOUNDATION→REINFORCEMENT threshold logic | `pytest tests/unit/test_learning_stage.py` |
| API | All endpoints return correct status codes + shapes | `pytest tests/integration/test_api.py` |

### Manual Verification

| Step | Criteria |
|------|----------|
| Health check | `GET /health` returns all-green status |
| Ingestion verification | 40+ extracted Concept Objects in Kuzu with typed edges + all 5 explanation levels |
| Graph render | Cytoscape.js loads with correct coloring for a test student |
| Teaching flow | Explanation at correct level, misconception fix on wrong answer |
| Ingestion test | Drop NCERT Chapter 2 PDF → new concepts appear in graph in <5 min |
| End-to-end | Fresh student onboards in <10 min, completes session, graph updates |
| Multi-user | Two students on same machine, data isolated |

### Browser Testing

| Page | Key Interactions to Verify |
|------|---------------------------|
| `index.html` | Multi-step onboarding completes without errors |
| `topic_list.html` | Mastery badges update after diagnostic |
| `teach.html` | SSE streaming works, misconception hint appears |
| `dashboard.html` | Session plan loads with real data |
| `revision.html` | FSRS-scheduled concepts appear |
| `upload.html` | Drag-drop → progress bar → graph updates |

---

## Open Questions

> [!IMPORTANT]
> **Q1**: NCERT Accountancy Class 11 PDFs must be in `data/source_docs/` before Week 2. Extraction quality depends entirely on source material. Do you have Ch. 1–6 ready?

> [!IMPORTANT]
> **Q2**: Kuzu must be installed and working locally. If not, fall back to SQLite graph-like tables is possible but loses typed edge query performance. Confirm Kuzu works on your machine before Week 1 Day 3.

> [!IMPORTANT]
> **Q3**: Phase A uses vanilla HTML/JS (per [DESIGN.md](DESIGN.md)). AI UI tools (Stitch/Lovable) can generate shells externally — architecture and API wiring stay manual. Preferred approach?

> [!IMPORTANT]
> **Q4**: Phase A goal exams are **CBSE Board** and **CA Foundation** only. Is this the right pair for your first 3–5 test students?
