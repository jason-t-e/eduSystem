# Gap Analysis: Final Revised Plan vs Phase A Implementation

> Reconciliation document between [Final Revised Plan v1.0](final_revised_plan.md) (north star) and [implementation_plan.md](implementation_plan.md) (skeletal 8-week build). Updated when either document changes.

---

## Document Hierarchy

```text
final_revised_plan.md     ← vision, research roadmap, full ecosystem
        ↓
prd.md                    ← product requirements
trd.md + backend_schema.md ← technical contracts
        ↓
implementation_plan.md    ← Phase A skeletal build (8 weeks)
        ↓
DESIGN.md                 ← UI supplement
```

The implementation plan intentionally builds a **working skeletal structure** — not the full vision. Gaps below are **expected**, not defects.

---

## What Phase A Delivers (Aligned)

| Final Plan Element | Phase A Status |
|--------------------|----------------|
| Hybrid: Concept Objects + Relationship Graph | ✅ Built Week 1–2 |
| Ingestion pipeline (PDF/DOCX/PPT → Docling/Marker → markdown → extract → graph) | ✅ Foundations Week 1; full pipeline Week 2–6 |
| Raw files as inputs, not knowledge bases | ✅ No hardcoded concept JSON |
| Typed edges with semantic annotations | ✅ REQUIRES, PART_OF, RELATES_TO, CONTRASTS_WITH, TESTED_BY, CONTRADICTS |
| Provenance + confidence scoring | ✅ SourceRef, field_confidence |
| Tier 1–4 optimization hierarchy | ✅ |
| Student workflow (goal exam, deadline, study time) | ✅ Week 3 |
| Diagnostic as weak prior + calibration | ✅ |
| Misconception framework with remediation | ✅ |
| Worked example system (3 modes) | ✅ |
| Progressive interleaving (Stages 1–2) | ✅ `learning_stage` on student |
| FSRS + RevisionAgent | ✅ Week 5 |
| Roadmap + basic explainability | ✅ Week 5 |
| Friction + gap detection + KPI dashboard | ✅ Week 7 |
| Metacognitive tips | ✅ Week 7 |
| Cytoscape.js visualization (typed edges) | ✅ |
| Offline-first / local-first | ✅ |
| Multi-user isolated profiles | ✅ |
| Commerce 11 Accountancy (Domain Stage 1) | ✅ |
| 6 core agents | ✅ Diagnostic, Teaching, Revision, Roadmap, Analytics, Ingestion |
| Improvement log + proposals queue | ✅ |

---

## Deliberately Deferred (Final Plan → Phase B/C)

| Final Plan Feature | Deferred To | Rationale |
|--------------------|---------------|-----------|
| Master Orchestrator + Session Orchestrator | Phase B | API routes sufficient for skeletal validation |
| Teaching Strategy Agent (separate) | Phase B | Strategy selection inside TeachingAgent |
| Question Generation Agent (standalone) | Phase A partial | Rolled into TeachingAgent |
| Engagement Agent | Phase A partial | Friction model in AnalyticsAgent |
| Memory Optimization Agent | Phase B | Not needed for core learning validation |
| Validation Agent (full pipeline) | Phase B | Phase A: confidence thresholds + CONTRADICTS flagging |
| Vector retrieval (Qdrant/pgvector) | Phase B | Graph + structured objects sufficient initially |
| Image ingestion | Phase B | PDF/DOCX/PPT first |
| Exam intelligence (goal/necessary/optional taxonomy) | Phase B | Board exam focus in Phase A |
| Progressive interleaving Stages 3–4 | Phase B | Stages 1–2 sufficient for validation |
| 80/20 experimentation split | Phase B | Needs baseline performance data |
| Conservative personalization expansion | Phase B | Population priors need data |
| Explainability layer (full) | Phase B | Basic session-plan reasoning in Phase A |
| Human oversight Levels 2–3 | Phase B/C | improvement_proposals queue is Level 2 seed |
| Coach/mentor dashboard | Phase C | Post-validation |
| Cloud sync, federated learning | Phase C | Local-first validation first |
| Deep simulations | Phase C | Commerce doesn't need them |
| PostgreSQL JSONB migration | Phase B | SQLite sufficient for 3–5 users |
| Neo4j graph migration | Phase C | Kuzu sufficient at current scale |
| MinIO/S3 raw document storage | Phase B | Local filesystem sufficient |
| Domain Stages 2–9 | Phase B+ | Commerce first |

---

## Schema Alignment Status

| Contract | Aligned to Final Plan | Notes |
|----------|----------------------|-------|
| `backend_schema.md` | ✅ | ConceptObject, TypedRelation, pedagogy/exam metadata |
| `trd.md` | ✅ | Ingestion pipeline, env vars, hybrid terminology |
| `prd.md` | ✅ | Hybrid model, exam intelligence, phased scope |
| `implementation_plan.md` | ✅ | Skeletal scope unchanged — source of Phase A truth |
| `core/types/schemas.py` (code) | ⚠️ | Must be updated during Week 1 build to match backend_schema |

---

## Technical Decisions: Final Plan vs Phase A

| Decision | Final Plan | Phase A Choice | Evolution |
|----------|------------|----------------|-----------|
| Concept storage | JSON + PostgreSQL JSONB | Kuzu JSON strings + SQLite | → PostgreSQL JSONB |
| Graph DB | NetworkX → Kuzu → Neo4j | Kuzu | → Neo4j if needed |
| Vector search | Qdrant/pgvector | None | Phase B |
| LLM | Unspecified | Ollama local | Cloud via deps.py swap |
| Orchestration | Explicit orchestrator agents | FastAPI routes | Phase B agents |
| Ontology | Canonical + dynamic layers | Canonical names JSON only | Dynamic layer Phase B |
| Validation | 6-stage pipeline | Schema + confidence + contradictions | Full pipeline Phase B |

---

## KPI Tracking: Final Plan vs Phase A

| KPI | Final Plan | Phase A Instrumentation |
|-----|------------|---------------------------|
| Retention Half-Life | Primary | FSRS stability proxy |
| Time-to-80%-Mastery | Primary | mastery field on LearnerState |
| Near/Medium Transfer | Primary | Diagnostic reframed questions |
| Mock Score Improvement | Primary | Manual entry / future |
| Syllabus Completion Time | Primary | Roadmap progress tracking |
| Misconception Recurrence | Primary | active_misconceptions persistence |
| Study Consistency | Secondary | session_events |
| Burnout Indicators | Secondary | FrictionState |
| Session Completion Rate | Secondary | sessions.end_time |
| Calibration Error | Secondary | calibration_error field |
| Topic Recovery Speed | Secondary | mastery delta after remediation |

---

## Maintenance Rules

1. **final_revised_plan.md** changes only when vision changes.
2. **implementation_plan.md** changes weekly during build — do not expand to full vision.
3. **prd.md, trd.md, backend_schema.md** must stay consistent with both documents.
4. **This document** must be reviewed whenever final_revised_plan or implementation_plan is updated.
5. Code (`schemas.py`, `graph.py`, ingestion modules) must match **backend_schema.md**.

---

## Conclusion

The Final Revised Plan describes a **long-term educational intelligence ecosystem**. The implementation plan builds a **skeletal Phase A foundation** — hybrid knowledge model, ingestion-first architecture, core teaching loop, six agents — upon which Phase B and C features are added through validated improvements.

No contradiction exists between the documents when their roles are understood: vision vs skeletal build.
