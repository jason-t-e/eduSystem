# EduSystem Design Guidelines

> UI/UX supplement to [Final Revised Plan v1.0](final_revised_plan.md). Phase A screens defined in [implementation_plan.md](implementation_plan.md).

---

## Design Principles

1. **Study-first** — rich but not distracting; vibrant mastery colors, calm backgrounds.
2. **Explainable** — surface *why* (roadmap priorities, scheduled reviews, level changes) where Phase A supports it.
3. **Offline-resilient** — core flows work without network; show cached state clearly.
4. **India-focused** — shared devices, intermittent connectivity, low-end hardware.

---

## Frontend Strategy

Use AI tools (Google Stitch, Cursor, Lovable) for rapid shell generation. Manually own:

- API integration and state management
- Educational workflow sequencing
- Caching and offline behavior
- Graph visualization logic

Phase A: vanilla HTML/CSS/JS served by FastAPI.

---

## Color Palette (Mastery States)

| State | Color | Mastery Range |
|-------|-------|---------------|
| UNKNOWN | Gray `#808080` | Not assessed |
| WEAK | Red `#FF4136` | 0–0.4 |
| OK | Amber `#FF851B` | 0.4–0.7 |
| STRONG | Green `#2ECC40` | 0.7–1.0 |

### Graph Edge Semantics (Cytoscape.js)

| Edge Type | Visual Treatment |
|-----------|------------------|
| `REQUIRES` | Solid arrow, cool tone — prerequisite chain |
| `PART_OF` | Dashed arrow — hierarchy |
| `CONTRASTS_WITH` | Dotted bidirectional — misconception pairs |
| `RELATES_TO` | Thin bidirectional — soft link |
| `CONTRADICTS` | Red dashed — flagged for review |

Hover/tooltip: show edge annotations (`how`, `why`, `reason`) from TypedRelation.

---

## Core Screens

### 1. Onboarding (< 10 minutes)

1. Name, goal exam, study hours/day
2. Self-assess chapters (confident / weak / unknown)
3. Auto-diagnostic on top 3 confident topics
4. First session plan + graph view ("wow" moment)

### 2. Dashboard

- Today's session plan with time budget
- Streak counter
- Mastery distribution donut chart
- Upcoming FSRS reviews calendar strip
- Calibration error trend
- **Explainability (Phase A):** brief "why these topics today" text from roadmap agent

### 3. Topic Browser

Chapter list with mastery-colored badges. Filter by weak/unknown.

### 4. Teaching Interface

- Concept name + explanation level badge
- SSE-streamed explanation
- Worked example / completion / independent mode indicator
- Answer input + misconception-targeted feedback
- Level-up notification animation

### 5. Graph View (Cytoscape.js)

Visualize:

- Prerequisites and dependency chains (`REQUIRES`, `PART_OF`)
- Student mastery coloring on concept nodes
- Active misconceptions highlighted on affected nodes
- Roadmap progress (concepts studied vs remaining in chapter)

Click node → concept name, definition snippet, mastery, next review, active misconceptions.

### 6. Upload Portal

Drag-drop zone with staged progress:

`parsing → normalizing → chunking → extracting → mapping → precomputing → merging → done`

Result summary: concepts added, edges created, contradictions flagged.

### 7. Revision Session

FSRS due concepts, recall prompts, quick mastery update.

---

## Typography

Modern, readable fonts for Indian students: Inter, Roboto, or Outfit. Minimum 16px body on mobile.

---

## Aesthetics

- Glassmorphism on graph overlay panels
- Micro-animations: upload progress, level-up, mastery badge transitions
- High contrast for accessibility
- Avoid motion-heavy distractions during teaching mode

---

## Offline-First UX

| Behavior | Offline |
|----------|---------|
| View cached graph | ✅ |
| Teach with precomputed explanations | ✅ |
| FSRS review (local state) | ✅ |
| Upload new documents | ❌ — queue for sync |
| LLM adaptation | ❌ — fallback to cached explanation |

Show connectivity indicator. Queue uploads and sync when online (Phase B).

---

## Explainability UI (Roadmap)

| Surface | Phase A | Phase B+ |
|---------|---------|----------|
| Why topic prioritized | Session plan tooltip | Full reasoning chain |
| Why revision scheduled | "Due for FSRS review" + date | Forgetting curve visualization |
| Why teaching level changed | Level-up notification | Competency breakdown |
| Why question selected | — | Diagnostic trace |

---

## Multi-User

Username-only profiles. Profile switcher on shared devices. No data leakage between students — all queries scoped by `student_id`.

---

## Deferred UI (Post Phase A)

- Coach/mentor dashboard
- Experimentation A/B indicators
- Simulation embeds (Physics/Chemistry)
- Vector search / semantic concept finder
- Full validation review queue UI
