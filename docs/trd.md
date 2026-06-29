# Technical Requirements Document (TRD): EduSystem

> Derived from [Final Revised Plan v1.0](final_revised_plan.md). Phase A implementation details in [implementation_plan.md](implementation_plan.md). Data contracts in [backend_schema.md](backend_schema.md).

---

## 1. System Architecture

### 1.1 Final Architecture (Target)

```text
UI Layer
        ↓
Session Orchestrators                    ← Phase B (implicit in API routes in Phase A)
        ↓
Educational Agents
        ↓
Deterministic Core Systems (Scheduler, Event Bus)
        ↓
Knowledge Services
        ↓
Concept Objects (JSON) + Relationship Graph (Kuzu) + Vector Retrieval (Phase B)
        ↓
Educational Knowledge Infrastructure
        ↓
Validation & Ontology Systems
        ↓
Raw Educational Assets
```

### 1.2 Phase A Layered Architecture (8 Layers)

Strict downward dependencies — no upward imports.

| Layer | Responsibility |
|-------|----------------|
| **UI** | Static HTML/JS, Cytoscape.js graph rendering |
| **API** | FastAPI `/api/v1/`, SSE streaming, `deps.py` injection |
| **Agents** | Isolated agents via `BaseAgent`, typed event bus |
| **LLM + Scheduler** | `LLMClient` Protocol / Ollama; pure-Python FSRS + topo sort |
| **Core** | Pydantic schemas, logging, event bus, config — imports nothing above |
| **Graph (Kuzu)** | Knowledge Graph + Learner Graph (hybrid: Concept Objects + typed edges) |
| **Relational (SQLite)** | Students, sessions, attempts, events, ingestion/improvement logs |
| **Pipelines** | Ingestion (parse → extract → map → graph), improvement logging |

**Dependency rule:** `frontend → api → agents → llm + scheduler → core → database/graphs`

---

## 2. Hybrid Data Model

### Concept Objects (Structured Store)

Rich Pydantic `ConceptObject` records serialized to Kuzu `Concept` nodes (JSON for complex fields). Populated **only** via ingestion — never hardcoded.

Fields: `definition`, `properties`, `functions`, `examples`, `misconceptions`, `pedagogy_metadata`, `exam_metadata`, `explanations`, `sources`, `field_confidence`, `confidence_score`, `version`.

### Typed Relations (Structural Store)

`TypedRelation` model maps to Kuzu edge tables with semantic annotations:

| Edge | Annotations |
|------|-------------|
| `REQUIRES` | `reason`, `strength`, `confidence`, `source` |
| `PART_OF` | `container_type`, `role`, `how`, `why`, `confidence`, `source` |
| `RELATES_TO` | `relation_kind`, `description`, `confidence`, `source` |
| `CONTRASTS_WITH` | `contrast_axis`, `description`, `confidence`, `source` |
| `TESTED_BY` | `question_type`, `difficulty`, `board_ref`, `confidence`, `source` |
| `CONTRADICTS` | `field`, `description`, `confidence`, `source` |
| `HAS_STATE` | Cross-graph bridge: Concept → LearnerState |

### Learner State

`LearnerConceptState` per `(student_id, concept_id)`: mastery, confidence, calibration_error, forgetting_score, next_review, explanation_level, active_misconceptions.

---

## 3. Ingestion Pipeline

Raw files are **inputs, not knowledge bases**.

```text
PDF / DOCX / PPT
        ↓
Docling (primary) / Marker (fallback) / pymupdf4llm (tertiary)
        ↓
Normalized Markdown          ← canonical IR, cached at data/markdown_cache/{sha256}.md
        ↓
Semantic Chunking            ← H2/H3 splits, 300–600 tokens, heading path prefix
        ↓
Educational Extraction       ← LLM → ConceptObject + TypedRelation JSON
        ↓
Canonical Ontology Mapping   ← alias resolution via config/ontology/, dedup
        ↓
Knowledge Graph Upsert     ← Kuzu Concept nodes + typed edges
        ↓
Explanation Precomputation ← 5 levels before teaching flow
```

**Validation (Phase A):** schema validation, confidence thresholds (default 0.6), contradiction flagging.

**Validation (Phase B+):** full pipeline — security, authenticity, quality, novelty, controlled integration.

---

## 4. Technology Stack

### Phase A (Current)

| Component | Technology |
|-----------|------------|
| Backend | Python 3.x, FastAPI, Uvicorn |
| Relational DB | SQLite + SQLAlchemy asyncio + Alembic |
| Graph DB | Kuzu (two files: knowledge + learner) |
| LLM | Ollama (`llama3.1:8b`, fallback `mistral:7b`) |
| HTTP | httpx async, 3-retry exponential backoff |
| Prompts | Jinja2 versioned registry |
| Parsers | Docling, marker-pdf, pymupdf4llm, python-docx, python-pptx |
| FSRS | py-fsrs |
| Logging | loguru + UUID correlation IDs |
| Testing | pytest, pytest-asyncio |
| Visualization | Cytoscape.js |

### Evolution Path (Final Plan)

| Layer | Phase A | Future |
|-------|---------|--------|
| Concept Objects | SQLite JSON / Kuzu JSON strings | PostgreSQL JSONB |
| Graph | Kuzu | Neo4j if scale requires |
| Vector retrieval | — | Qdrant / pgvector (semantic search only) |
| Raw docs | Local filesystem | MinIO → S3 |
| Orchestrators | Implicit in API | Master + Session Orchestrator agents |

---

## 5. Environment & Configuration

All config via `.env` + `config/settings.py`. No hardcoded strings.

```ini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
DB_URL=sqlite+aiosqlite:///./data/edusystem.db
KNOWLEDGE_GRAPH_PATH=./data/knowledge_graph
LEARNER_GRAPH_PATH=./data/learner_graph
WATCH_FOLDER=./data/uploads
SOURCE_DOCS_DIR=./data/source_docs
ONTOLOGY_DIR=./config/ontology
LOG_LEVEL=DEBUG
```

`config/ontology/{stream}/canonical_names.json` — alias → canonical name mappings only. No concept content.

---

## 6. API Design Contract

REST + SSE for streaming and long-running jobs.

| Group | Method | Endpoint | Purpose |
|-------|--------|----------|---------|
| Core | `GET` | `/health` | DB, both graphs, Ollama, concept count |
| Graph | `GET` | `/api/v1/graph/{id}` | Cytoscape JSON — ConceptObjects + TypedRelations |
| Graph | `GET` | `/api/v1/graph/{id}/learner/{uid}` | + LearnerConceptState enrichment |
| Diag | `POST` | `/api/v1/diagnostic/self-assess` | Initialize learner nodes from confidence |
| Diag | `POST` | `/api/v1/diagnostic/start/{id}` | Adversarial calibration questions |
| Diag | `POST` | `/api/v1/diagnostic/submit` | Score attempts, update mastery |
| Teach | `POST` | `/api/v1/teach/{concept_id}` | SSE level-aware explanation |
| Teach | `POST` | `/api/v1/teach/evaluate` | Answer evaluation + remediation |
| Revise | `GET` | `/api/v1/revision/{uid}/due` | FSRS due concepts |
| Revise | `POST` | `/api/v1/revision/complete` | Update FSRS after review |
| Roadmap | `GET` | `/api/v1/roadmap/{uid}` | Prioritized session plan |
| Roadmap | `POST` | `/api/v1/roadmap/{uid}/plan` | Plan for available minutes |
| Ingest | `POST` | `/api/v1/ingest/upload` | Upload to WATCH_FOLDER |
| Ingest | `GET` | `/api/v1/ingest/status/{job}` | SSE ingestion progress |
| Analytics | `POST` | `/api/v1/analytics/event` | Fire-and-forget UX events |
| Analytics | `GET` | `/api/v1/analytics/{uid}/friction` | Friction state + recommendations |
| Analytics | `GET` | `/api/v1/analytics/{uid}/gaps` | Prerequisite gap warnings |
| Analytics | `GET` | `/api/v1/analytics/{uid}/calibration` | Calibration metrics |
| Improve | `GET` | `/api/v1/improve/proposals` | Human-reviewable proposals |
| Students | `POST` | `/api/v1/students/register` | Username-only registration |
| Students | `GET` | `/api/v1/students/{uid}` | Profile |

---

## 7. Agent Specifications (Phase A)

All agents extend `BaseAgent` with injected `(llm, db, knowledge_graph, learner_graph, bus, logger)`.

| Agent | Key Behavior |
|-------|--------------|
| **DiagnosticAgent** | Fetches ConceptObject misconceptions; adversarial traps from `warning_signs`; emits `DiagnosticStarted`, `AttemptRecorded` |
| **TeachingAgent** | Serves precomputed explanations; LLM adapts for active misconceptions; worked/completion/independent modes by mastery |
| **RevisionAgent** | py-fsrs wrapper; updates `forgetting_score`, `next_review` |
| **RoadmapAgent** | Topo sort on `REQUIRES`; score = `exam_metadata.weightage × (1−mastery) × prereq_readiness` |
| **IngestionAgent** | Full pipeline orchestration; cross-doc synthesis; SSE progress |
| **AnalyticsAgent** | FrictionState (OVERLOAD, BOREDOM, CONFUSION, DISENGAGED); calibration EMA |

### Deferred Agents (Final Plan)

Master Orchestrator, Session Orchestrator, Teaching Strategy Agent, Question Generation Agent (standalone), Engagement Agent, Memory Optimization Agent, Validation Agent.

---

## 8. Prompt Engineering

Versioned `.j2` templates via `prompt_registry.py`. Output validated through `parse_with_retry(raw, schema, retries=2)`.

| Template | Output |
|----------|--------|
| `diagnostic_v1.j2` | Adversarial question JSON array |
| `teaching_explanation_v1.j2` | Adapted explanation + worked example |
| `teaching_completion_v1.j2` | Completion problem JSON |
| `question_generation_v1.j2` | Independent question JSON |
| `misconception_remediation_v1.j2` | Targeted correction |
| `precompute_explanations_v1.j2` | All 5 explanation levels |
| `concept_extraction_v1.j2` | ConceptObjects + TypedRelations with provenance |
| `relation_extraction_v1.j2` | TypedRelation with how/why annotations |
| `revision_v1.j2` | Recall prompt + question |
| `metacognitive_tip_v1.j2` | Actionable study tips |

---

## 9. Testing & Quality Assurance

- **Unit tests:** schemas, event bus, LLM client (mocked), Kuzu CRUD, FSRS, scheduler determinism.
- **Integration tests:** register → self-assess → diagnose → teach → review.
- **Graceful degradation:** TeachingAgent LLM failure → serve cached precomputed explanation from Knowledge Graph.
- **Correlation tracing:** UUID per HTTP request through all log lines.
- **Ingestion gate:** concepts without all 5 explanation levels do not enter teaching flow.

---

## 10. Ontology & Human Oversight

**Canonical ontology:** `config/ontology/{stream}/canonical_names.json` + `stream_metadata.json`.

**Dynamic layer (Phase B):** AI-proposed links validated before promotion.

**Human oversight levels (Final Plan):**

| Level | Phase A | Future |
|-------|---------|--------|
| L1 — Auto-approve low-risk | Confidence threshold auto-accept | Full |
| L2 — Expert review | `improvement_proposals` queue | Ontology rewiring |
| L3 — Multi-review | — | Cloud-wide updates |
