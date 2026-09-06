# FloodPulse — Full Development Plan
**AI-Based Flood Risk Mapping & Early Warning System for Karnataka, India**
GitHub Org: Codovia | Timeline: 3 weeks | Primary implementer: Nandan

---

## 1. Project Overview

FloodPulse is a full-loop flood risk system: **prediction → alert → shelter locator → admin-managed real shelter data.** The academic deliverable is two-part:
1. A working application demonstrating the full loop.
2. A research paper documenting every implementation step and decision.

### Core components
| Component | Purpose |
|---|---|
| ML flood risk prediction model | Continuous district-level flood probability |
| Telegram alert bot | Push warnings based on prediction output |
| Citizen shelter/help-center locator | Public-facing map of real, active shelters |
| Admin portal | Manage real shelter data in real time |

---

## 2. Non-Negotiable Constraints

These override convenience at every step — violating any of these is a bigger risk to the grade than an incomplete feature.

- **No synthetic, mocked, or fabricated data — anywhere, including during development.** All data must be real, with provenance tracked on every record.
- **Provenance classification per record:** `REAL` / `DERIVED_FROM_REAL` / `MODEL_OUTPUT` / `USER_REPORTED` / `UNKNOWN`. Implement as a JSON sidecar per file initially — don't over-engineer this before the pipeline needs it.
- **The project must not appear AI-generated.** Enforced by:
  - Logging every rejected approach in `DECISIONS.md` (including the Google Flood Hub and H2O/NVIDIA evaluations — see Section 9).
  - No inflated or unverifiable accuracy claims.
  - Incremental commits with specific, meaningful messages — no giant single commits.
  - Every formula cited to an external source.
- **Label semantics are strict:** `label = 0` means "not identified as affected" — **never** "confirmed no flood." Preserve this distinction through the entire ML pipeline; do not silently treat it as a negative ground truth.
- **No arbitrary risk threshold cutoffs.** Store continuous flood probabilities. Any place a threshold is genuinely needed (e.g., triggering a Telegram alert), the choice of threshold and its justification goes in `DECISIONS.md`.
- **No hard-coded latitude-based slope approximations.** Use real terrain data (SRTM) and proper geospatial processing.
- **Reject templated, unverifiable architectures.** The "FloodGuard" YouTube pattern (CNN on scalar tabular data, unverifiable accuracy, physically invalid features like "political factors") is the canonical anti-pattern. The H2O.ai/NVIDIA blueprint falls in the same category for this project — see Section 9.
- **Git discipline:** no raw datasets committed to the repo, no casual force-pushes, mandatory inspection before any destructive operation.
- **Agent-failure recovery:** if a coding agent (or you) gets into a broken state, recover from git history — don't rebuild from scratch.

---

## 3. Tech Stack

- **IDE:** Antigravity IDE (Google's agent-first IDE), used in **Agent-assisted or Review-driven mode** — not Autopilot. Persistent guardrail: never generate or simulate data.
- **Data processing:** Python, pandas
- **Database:** PostgreSQL + PostGIS
- **Backend:** FastAPI
- **Frontend:** React
- **Alerts:** Telegram Bot API
- **File discovery:** prefer the GitHub API (`api.github.com/repos/{owner}/{repo}/contents/{path}`) over scraping the GitHub web UI.
- **Raw file download pattern:** `https://raw.githubusercontent.com/{owner}/{repo}/main/{path}` via `curl -o`.

---

## 4. Data Sources

| Source | What it provides | Access |
|---|---|---|
| **India Flood Inventory v3** (IIT Delhi HydroSense Lab) | Historical flood event records | GitHub: `hydrosenselab/India-Flood-Inventory`, also on Zenodo |
| **IMD historical gridded rainfall** (1901–2024) | Primary rainfall data source, district-level | `imdpune.gov.in` — open |
| **KSNDMC Karnataka rainfall** | State-specific rainfall, supplements IMD | OpenCity CKAN API |
| **CWC river/reservoir data** | River/reservoir levels | National Water Data Portal, `nwdp.nwic.gov.in` |
| **KGIS district/taluk boundaries** | Karnataka administrative polygons for spatial join | `kgis.ksrsac.in`, or GitHub mirror `samashti/KGIS` |
| **OpenTopography SRTM** | Terrain elevation for real slope calculation | Open — used because SOI DTM and NRSC/Bhuvan are login-restricted |

**Known data quirk:** `India_Flood_Inventory_v3.csv` requires `encoding='utf-8-sig'` when read with pandas — it has a BOM character.

**Shelter data (separate from the above):** Real, verified shelter/help-center locations for Karnataka. This is *not* an open dataset — source it manually from government disaster-management sites, NDMA lists, or district administration contacts. Start this on Day 1, in parallel with everything else — it's the highest external-dependency risk in the whole project.

---

## 5. ML Methodology

- **Model:** Class-weighted Random Forest.
- **Train/test split:** Time-based, not random — random splits leak future information into training (temporal leakage) and would invalidate the whole result.
- **Features:**
  - Rolling rainfall accumulation: 3-day sum, 7-day sum, 1-day lag.
  - Real terrain-derived slope from SRTM (no latitude-based shortcuts).
- **Hyperparameter tuning:** Grid search, tuned to the actual dataset distribution — not copied defaults.
- **Missing data policy:** Pipeline fails loudly on missing data. Never silently substitute or interpolate without an explicit, documented decision.
- **Output:** Continuous flood probability per district. No hard cutoffs stored in the database.
- **Spatial unit:** District-polygon level, using IMD rainfall as the primary rainfall source.

---

## 6. System Architecture

### Database (PostgreSQL + PostGIS)
- `predictions` — district ID, timestamp, continuous probability, model version.
- `shelters` — location, capacity, status, audit fields (who changed it, when).
- `provenance` — per-record classification (`REAL`/`DERIVED_FROM_REAL`/`MODEL_OUTPUT`/`USER_REPORTED`/`UNKNOWN`), source, retrieval date.

### Shelter state machine
`CANDIDATE → ACTIVE / FULL / CLOSED`
- Admin actions transition state.
- Every transition writes a mandatory audit field (who, when, why).

### Backend (FastAPI)
- Endpoint(s) to serve per-district prediction probability.
- Endpoint(s) for shelter CRUD (admin-only, authenticated).
- Endpoint(s) for public shelter locator (read-only).

### Telegram bot
Strictly bounded to **five specific commands** — define these explicitly before building (e.g., subscribe, check district status, nearest shelter, unsubscribe, help). Wire alert triggers to the prediction API using a documented probability→alert threshold (see Section 2 — this threshold decision itself needs a `DECISIONS.md` entry, since it's the one place a cutoff is unavoidable).

### Frontend (React)
- Citizen-facing shelter/help-center locator (map view).
- Admin portal for managing shelter state and viewing prediction data.

---

## 7. Documentation Practice (ongoing, not end-of-project)

- **`DECISIONS.md`** — every rejected approach, every threshold choice, every "we tried X, it didn't work because Y" moment. This is your strongest evidence of genuine engineering judgment.
- **`ARCHITECTURE.md`** — kept current as the system evolves, not written once at the start.
- **`CONSTRAINTS.md`** — the rules in Section 2, as a living reference.
- **`FLOW.md`** — data flow from ingestion to alert.
- **`HANDOVER.md`** — state of the project at any checkpoint, useful if you lose momentum and need to re-orient.
- **`TEST_CHECKLIST.md`** — used in Section 9's integration testing phase.
- **`ROLLBACK.md`** — how to recover from a broken state via git history.
- **`SKILL.md`** — the formal spec governing methodology, git discipline, and agent-failure recovery.

---

## 8. Three-Week Execution Schedule

### Week 1 — Foundation & Data
| Day | Task |
|---|---|
| 1 | Repo scaffold under Codovia, PostgreSQL+PostGIS instance, FastAPI/React skeletons, doc files created and live |
| 1 (parallel) | **Start sourcing real shelter data** — highest external-dependency risk, don't defer this |
| 2–4 | Acquire all data sources (IFI, IMD, KSNDMC, CWC, KGIS, SRTM); provenance-tag every file at download time |
| 5–7 | Fix IFI BOM encoding, inspect schemas, spatial join to Karnataka district polygons; log rejected approaches in `DECISIONS.md` as you go |

### Week 2 — Modeling & Backend
| Day | Task |
|---|---|
| 8–9 | Feature engineering: rolling rainfall accumulation, SRTM-derived slope |
| 10–12 | Train and evaluate Random Forest: time-based split, grid search, continuous probability output |
| 13–14 | FastAPI prediction endpoints; PostGIS schema for predictions/shelters/provenance |

### Week 3 — Frontend, Alerts, Testing, Paper
| Day | Task |
|---|---|
| 15–16 | Shelter locator + admin portal (React) — keep UI minimal and functional given the timeline |
| 17 | Telegram bot (five commands) wired to the prediction API; document the alert-threshold decision |
| 18 | Full integration test against `TEST_CHECKLIST.md` — this is the decision point for cutting scope if behind |
| 19–20 | Finish research paper — should be largely assembled from `DECISIONS.md` notes already, not written from scratch |
| 21 | Presentation prep: slides, live demo script, recorded fallback video in case live demo fails |

**Pre-committed fallback scope (decide now, not on Day 18):** if behind schedule, cut the admin portal's full state-machine UI first (keep it backend-only with a few manually verified real shelter records) — never cut the "no fake data" rule or the ML pipeline's integrity. If IMD/KSNDMC access is slow, drop to IFI + KGIS + SRTM as the core three sources and treat CWC/KSNDMC as stretch goals.

---

## 9. Evaluated & Rejected External Options (for `DECISIONS.md`)

Document both of these explicitly — this is exactly the kind of critical evaluation that strengthens the "this wasn't AI-assembled" narrative.

### Google Flood Hub / Flood Forecasting API
- **Considered for:** riverine flood forecasting as a possible core data source or benchmark.
- **Rejected as core dependency because:** API access requires a pilot waitlist that can take months — incompatible with a 3-week timeline. More importantly, consuming Google's forecast instead of building an original model would undermine the project's core academic contribution.
- **Limited legitimate use:** cite Google's published methodology as related work in the research paper; optionally submit the waitlist form as a zero-effort background task, and if approved during the project, use it as an external validation comparison for one district — not a dependency the project relies on.

### H2O.ai + NVIDIA Flood Intelligence Blueprint
- **Considered for:** multi-agent flood intelligence architecture inspiration.
- **Rejected outright because:**
  - Built on USGS/NOAA (US) data — wrong country, doesn't map to IMD/CWC/KGIS.
  - Uses a closed, hosted LLM for "risk analysis" rather than a trained, documented statistical model — the opposite of the class-weighted Random Forest approach this project uses.
  - It's a pre-built template scaffold, structurally the same red flag already identified in the "FloodGuard" pattern: unverifiable, not original work, hard to defend under questioning.
  - Its own NVIDIA catalog listing is marked deprecated, though the underlying GitHub repo remains open-source and functional — a further reason not to build a load-bearing dependency on it.

---

## 10. Research Paper Structure (draft in parallel, not after)

1. Introduction & motivation (Karnataka flood risk context)
2. Related work (include Google Flood Hub, GloFAS, and similar systems as comparison points)
3. Data sources & provenance methodology
4. Feature engineering & rationale (pull directly from `DECISIONS.md`)
5. Model architecture, training methodology, evaluation metrics
6. System architecture (prediction → alert → locator → admin loop)
7. Rejected approaches and why (pull directly from `DECISIONS.md`)
8. Limitations & future work
9. Conclusion

---

## 11. Presentation Day Checklist

- [ ] Live demo script written and rehearsed
- [ ] Recorded fallback video of the full demo, in case of live failure (network, API downtime, etc.)
- [ ] Slides cover: problem statement, architecture, model methodology, key rejected-approach decisions, live/recorded demo, limitations
- [ ] Be ready to explain *why* Random Forest over other models, *why* time-based split, and *why* Google Flood Hub / H2O-NVIDIA blueprint weren't used — these are the questions most likely to probe for genuine understanding versus templated work
