# FloodPulse Agent Skill

## 0. Skill identity

**Project:** FloodPulse  
**Organization:** Codovia  
**Geography:** Karnataka, India  
**Primary objective:** Build a working, research-documented flood decision-support and early-warning prototype in 20 days using real data only.

This file is an operational instruction set for an agentic coding/research AI. It is not a project description. The agent must use it as the governing workflow, constraints, quality bar, and completion checklist for the project.

---

# 1. Mission

Build FloodPulse end-to-end from the current state of the project:

- no trustworthy model dataset has yet been assembled;
- no production application code can be assumed to exist;
- documentation/scaffolding may already exist;
- the final system must be demonstrable and academically defensible;
- the implementation window is **20 calendar days**;
- the primary state is **Karnataka, India**.

FloodPulse has four confirmed pillars:

1. **Flood-risk susceptibility mapping** using machine learning on tabular/spatial features.
2. **Citizen emergency shelter/help-center locator.**
3. **Telegram-based flood alerts.**
4. **Admin portal for authorized staff to create, verify, activate, deactivate, fill, and manage emergency shelters in real time.**

The administrator-controlled shelter workflow is an important product differentiator, but the agent must never claim that no comparable system exists unless an exhaustive, cited review proves that statement.

---

# 2. Core product definition

FloodPulse is **not** a single black-box system that claims to forecast exact flooding hours in advance.

The system must separate three responsibilities:

```text
Historical data
    -> ML spatial flood susceptibility

Live meteorological/hydrological information
    -> operational warning context

Admin-managed shelters + emergency facilities
    -> response/action layer
```

The ML model provides a **susceptibility/event-likelihood signal**. Official meteorological/hydrological warnings and observations remain explicitly source-labelled. The product must never present a student-built model as an official government warning authority.

The final user experience should make it obvious which information is:

- official source data;
- FloodPulse-derived/model output;
- administrator-entered information;
- derived data;
- user-reported data, if added later.

---

# 3. Non-negotiable rules

## 3.1 Real-data rule

**Never create, fabricate, mock, or silently simulate project data.**

This includes:

- flood events;
- rainfall observations;
- river levels/discharge;
- shelter locations;
- hospital/fire/police records;
- model labels;
- test fixtures that could be mistaken for real observations;
- screenshots presented as live results;
- fake accuracy or evaluation numbers.

Synthetic data may only be used in a temporary isolated unit test when it is mathematically necessary to test software behavior, never as project data, never as model training data, and never inside the real data pipeline. Any such test data must be unmistakably named as test-only and excluded from production/demo paths.

## 3.2 Missing-data rule

The pipeline must fail loudly when a required source is missing or invalid.

Never do this:

```python
if data_missing:
    return generated_fake_data
```

Never silently replace a required dataset with zeros, random values, averages, or placeholders merely to allow a job to finish.

## 3.3 Provenance rule

Every imported dataset and every derived dataset must have provenance metadata.

Minimum provenance classes:

```text
REAL
DERIVED_FROM_REAL
MODEL_OUTPUT
USER_REPORTED
UNKNOWN
```

Each dataset should also record, where available:

```text
source_name
source_url
publisher
retrieved_at
license
coverage_start
coverage_end
spatial_resolution
temporal_resolution
coordinate_reference_system
processing_step
provenance_class
checksum/file hash when practical
```

## 3.4 Temporal validation rule

Never use a random train/test split for the primary ML evaluation.

FloodPulse must use a time-based split so later events are not used to predict earlier events.

## 3.5 Documentation-first rule

Before implementing a material architectural, data, target-definition, or methodology decision:

1. inspect evidence;
2. record the decision and rationale in `docs/DECISIONS.md`;
3. then implement it.

When an approach fails, document the failure instead of deleting the evidence from project history.

## 3.6 No unsupported claims

Do not claim:

- real-time flood prediction if the system only maps susceptibility;
- flood depth prediction unless validated flood-depth labels exist;
- a government-certified warning system;
- a specific accuracy level before actual evaluation;
- statewide completeness when source coverage is incomplete;
- novelty/non-existence of competing systems without a cited review.

## 3.7 No arbitrary thresholds

Do not invent probability thresholds such as 0.33/0.66 without validation.

Keep continuous model probability internally. If categorical display classes are necessary, derive and document thresholds from an explicit method and label them as presentation classes rather than official emergency thresholds.

---

# 4. Recommended technology stack

Use the confirmed stack unless there is a strong, documented reason to change it:

```text
Frontend: React
Backend: FastAPI
Database: PostgreSQL + PostGIS
Messaging: Telegram Bot API
ML: Python + scikit-learn
Geospatial/data processing: Python ecosystem
Containerization: Docker Compose
Migrations: Alembic
CI: GitHub Actions
```

Prefer simple, maintainable architecture over unnecessary microservices.

---

# 5. Required architecture

```text
                    ┌─────────────────────────┐
                    │       DATA SOURCES      │
                    ├─────────────────────────┤
                    │ IFI / IFI-Impacts       │
                    │ IMD rainfall            │
                    │ NWDP rainfall          │
                    │ NWDP/CWC river data    │
                    │ SRTM DEM                │
                    │ WorldCover              │
                    │ KGIS boundaries         │
                    │ river network           │
                    │ Karnataka OGD / OSM     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    DATA INGESTION       │
                    │ validation + provenance │
                    │ CRS + quality checks    │
                    └────────────┬────────────┘
                                 │
                       ┌─────────┴────────┐
                       ▼                  ▼
             ┌─────────────────┐ ┌─────────────────┐
             │ ML PIPELINE     │ │ LIVE DATA       │
             │ feature build   │ │ IMD/NWDP/CWC    │
             │ labeling        │ │ official signal │
             │ Random Forest   │ │ normalization   │
             └────────┬────────┘ └────────┬────────┘
                      │                   │
                      └─────────┬─────────┘
                                ▼
                     ┌─────────────────────┐
                     │      FASTAPI        │
                     │ risk / GIS / alerts │
                     │ shelters / admin    │
                     └──────────┬──────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
              ┌──────────────┐      ┌──────────────┐
              │ React client │      │ Telegram bot │
              └──────┬───────┘      └──────────────┘
                     │
              Citizen + Admin
```

---

# 6. Data-source strategy

The agent must verify access and current availability at the beginning of the data phase. Never assume a URL or API endpoint still works simply because it appears in this file.

## P0: required sources

### 6.1 India Flood Inventory / IFI-Impacts

Primary historical flood-event source.

Known publisher/project:

- HydroSense Lab, IIT Delhi
- GitHub: `hydrosenselab/India-Flood-Inventory`
- Zenodo releases of IFI/IFI-Impacts

Use the latest accessible, appropriately documented IFI-Impacts release that provides usable event/impact records and temporal/spatial information.

Primary use:

```text
historical flood events
flood dates/duration
spatial flood evidence
Karnataka event extraction
training-label construction
```

The agent must record the exact release/version/date actually used.

### 6.2 IMD historical gridded rainfall

Use India Meteorological Department gridded rainfall as the primary broad-scale historical precipitation source when accessible.

Known product:

- daily rainfall
- approximately 0.25° grid
- historical multi-decade coverage

Primary use:

```text
rain_1d
rain_3d
rain_7d
rain_14d when justified
lagged rainfall features
historical event-window precipitation
```

The agent must inspect actual coverage before choosing the training period.

### 6.3 Karnataka rainfall from NWDP / Karnataka water-data sources

Use National Water Data Portal and Karnataka-linked datasets when accessible.

Potential products:

```text
daily rainfall
hourly rainfall
telemetry rainfall
```

Use for Karnataka-specific observational support and live/near-live contextual data where suitable.

### 6.4 Karnataka river/discharge data

Use NWDP/CWC/Karnataka water-data sources for river-gauge observations.

Potential products:

```text
daily river discharge
hourly river discharge
water level
reservoir observations
```

Use for:

- operational context;
- validation;
- river-condition display;
- optional model feature if the join is defensible.

Do not invent flood thresholds. Use official/source-provided thresholds when available.

### 6.5 KGIS boundaries

Use Karnataka GIS / KGIS boundary data for:

- Karnataka boundary;
- districts;
- taluks;
- other administrative units only if needed.

Record the exact boundary release/source.

### 6.6 DEM

Use a genuinely accessible open elevation source such as SRTM when Survey of India DTM access is not available within the deadline.

Derive at minimum:

```text
elevation
slope
```

Potential later variables:

```text
flow accumulation
TWI
curvature
```

Only add later variables if they can be computed correctly and improve the project meaningfully.

### 6.7 Land cover

Preferred accessible source:

- ESA WorldCover 10 m or another openly licensed, well-documented land-cover product.

Start with broad classes. Do not create a massive feature space unnecessarily.

### 6.8 River network

Use an authoritative/open hydrological river/stream layer where possible, preferably aligned with CWC/WRIS/NWDP or another well-documented national source.

Derived feature:

```text
distance_to_river
```

The project explicitly excludes drainage-risk mapping. Do not turn the river-network layer into a separate drainage-risk project.

---

# 7. Optional/P1 sources

## 7.1 INDOFLOODS

Use the latest accessible INDOFLOODS release as a research/validation source for observed river flood events if the dataset can be incorporated without derailing the schedule.

Potential fields include:

```text
flood start/end
time to peak
peak level
peak discharge
duration
volume
catchment/gauge information
precipitation/context variables
```

Do not force this dataset into the model merely because it exists. First assess spatial/temporal compatibility with the target.

## 7.2 NDEM / NRSC / Bhuvan flood layers

Treat as **optional validation/enrichment**, not a critical dependency.

Reason:

- official access/distribution may be restricted or operationally difficult;
- historical satellite inundation is valuable but can miss events because of satellite revisit/cloud conditions;
- the project must remain buildable without it.

If accessible, use it for:

- historical inundation validation;
- visual comparison;
- additional evidence in the research paper.

Never stop the entire project waiting for NDEM access.

## 7.3 Karnataka OGD emergency infrastructure

Use official Karnataka Open Government Data sources where available for:

```text
hospitals
fire stations
other emergency infrastructure
```

Record source and retrieval date.

## 7.4 OpenStreetMap / Overpass

Use OSM/Overpass for current map context and non-authoritative POIs such as:

```text
roads
hospitals
schools
community facilities
police
fire stations
other relevant amenities
```

An OSM facility is **not automatically an emergency shelter**. Only administrators may activate a facility as an operational FloodPulse shelter unless an official source explicitly identifies it as such.

---

# 8. Data acquisition protocol

When starting data acquisition:

1. search the official publisher first;
2. verify license/access;
3. download the smallest geographically relevant dataset possible;
4. compute file hashes where practical;
5. record metadata;
6. inspect the actual schema;
7. inspect date and spatial coverage;
8. check for missingness and duplicates;
9. only then write the adapter.

For every source, create an adapter or ingestion module with the same conceptual interface:

```text
fetch()
validate_schema()
validate_coverage()
normalize_crs()
clean()
write_raw_or_interim()
write_provenance()
```

Do not bury source-specific assumptions throughout the ML code.

---

# 9. Initial repository structure

Use or improve this structure:

```text
FloodPulse/
├── README.md
├── PROJECT_MASTER_PLAN.md
├── .env.example
├── docker-compose.yml
├── Makefile or task runner
├── pyproject.toml
├── package.json (frontend)
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   ├── HANDOVER.md
│   ├── DECISIONS.md
│   ├── ARCHITECTURE.md
│   ├── CONSTRAINTS.md
│   ├── FLOW.md
│   ├── TEST_CHECKLIST.md
│   ├── ROLLBACK.md
│   ├── DATA_DICTIONARY.md
│   ├── DATA_SOURCES.md
│   ├── MODEL_CARD.md
│   ├── EXPERIMENT_LOG.md
│   └── RESEARCH_PAPER.md or paper/
│
├── data/
│   ├── raw/
│   │   ├── flood_inventory/
│   │   ├── rainfall_imd/
│   │   ├── rainfall_nwdp/
│   │   ├── discharge_nwdp/
│   │   ├── reservoirs/
│   │   ├── dem/
│   │   ├── landcover/
│   │   ├── rivers/
│   │   └── boundaries/
│   ├── interim/
│   └── processed/
│
├── ml/
│   ├── ingest/
│   ├── features/
│   ├── labels/
│   ├── training/
│   ├── evaluation/
│   └── artifacts/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── hooks/
│       └── map/
│
├── bot/
│   ├── app/
│   └── tests/
│
└── scripts/
    ├── bootstrap.sh
    ├── download_data.*
    ├── validate_data.*
    └── build_features.*
```

Use the existing scaffold when present instead of duplicating files.

---

# 10. ML problem definition

## 10.1 What the model should predict

Primary target:

> **Spatial flood susceptibility / historical event likelihood under observed environmental and precipitation conditions.**

The output is a probability-like model score for a spatial cell.

Do not call this an exact short-horizon hydraulic forecast.

## 10.2 Initial feature set

Start small:

```text
elevation
slope
distance_to_river
land_cover
rain_1d
rain_3d
rain_7d
rain_lag_1d
```

Potential second-wave features:

```text
TWI
flow accumulation
additional terrain metrics
soil
```

Only add them after the baseline is working and only with documented rationale.

## 10.3 Rainfall engineering

Use accumulated rainfall rather than relying only on same-day rainfall.

At minimum:

```text
rain_1d
rain_3d = rolling sum of previous 3 days according to clearly documented convention
rain_7d = rolling sum of previous 7 days
rain_lag_1d
```

The agent must write the exact mathematical definition and citation in the research documentation.

Do not copy arbitrary constants from another paper without explaining why they are applicable.

---

# 11. Label-construction protocol

This is the most important ML research task.

The agent must first inspect the actual flood-inventory schema and geometry before defining labels.

Preferred process:

```text
Historical flood event
        ↓
identify event date/window
        ↓
intersect flood evidence with modelling grid
        ↓
positive samples = observed flooded cells
        ↓
select carefully defined non-flood samples from comparable event context
        ↓
attach rainfall + terrain + land-cover features
```

Critical warning:

> A cell outside an observed flood polygon is not automatically proof that no flood occurred.

The paper must distinguish:

```text
observed flooded
```

from

```text
not identified as flooded in the available source
```

Negative-sample selection must therefore be documented and conservative.

If the chosen inventory only provides administrative/event-level information rather than reliable fine-grained polygons, the agent must **not pretend** to have cell-level ground truth. It must revise the target to the most defensible spatial unit supported by the data.

---

# 12. Spatial modelling grid

Default recommendation:

> approximately **0.05° (~5 km order-of-magnitude)** grid for the initial statewide model.

Reason:

- the historical IMD rainfall input is approximately 0.25°;
- a much finer grid may imply spatial precision that the historical meteorological input cannot support;
- a moderate grid is manageable within the deadline.

The exact grid should be selected after inspecting source resolution and event geometry. Record the final choice in `DECISIONS.md`.

Do not claim 100 m/1 km predictive precision from coarse historical rainfall.

---

# 13. Model algorithm

Default model:

> **Class-weighted Random Forest**

Use it because it is:

- appropriate for tabular data;
- interpretable enough for an academic project;
- fast to train;
- robust to nonlinear relationships;
- practical within a 20-day schedule.

Do not use CNNs for this scalar tabular problem merely because a reference project used CNNs.

Do not jump to LSTM, Transformer, graph neural networks, or deep-learning segmentation unless the entire baseline is complete and there is a compelling, documented reason.

The project is graded on correctness and evidence, not algorithm count.

---

# 14. Evaluation protocol

Report at minimum:

```text
precision
recall
F1-score
confusion matrix
ROC-AUC where valid
per-class metrics
```

Do not report aggregate accuracy as the only metric.

Because class imbalance is expected, inspect class distributions and use documented class weighting rather than silently resampling until metrics look good.

## Time-based split

Choose the split after inspecting the actual Karnataka event period.

Conceptually:

```text
older years -> training
later years -> validation
latest available years -> held-out test
```

Example only; do not hardcode these years without checking the real dataset:

```text
TRAIN: 1998–2018
VALIDATION: 2019–2021
TEST: 2022–2023
```

Do not alter the split simply because the metrics become worse.

## Optional spatial stress test

If time permits, perform a geographic holdout or district/region stress test to detect spatial generalization problems. This is secondary to the temporal split.

---

# 15. Model probability and categories

Persist continuous model probability:

```text
risk_probability
```

Do not hardcode arbitrary classes.

If the UI needs categories, use one of these defensible approaches:

1. quantile-based display classes;
2. validation-derived operating thresholds;
3. a transparent equal-interval visualization strictly labelled as a display classification;
4. source/official thresholds only for official warnings, not for ML probabilities.

Document the choice.

---

# 16. Live warning architecture

FloodPulse must separate model output from official live information.

## Official/live sources

Preferred:

```text
IMD APIs
NWDP/Karnataka/CWC observations
```

Potential IMD products include:

```text
current weather
rainfall
nowcast
District warning
forecast
```

Potential hydrological products include:

```text
river gauge readings
water level
discharge
reservoir observations
```

The agent must verify current endpoint documentation before implementation because API endpoints and access details can change.

---

# 17. Alert decision engine

Start with transparent rules rather than a second unexplained ML model.

Conceptual pattern:

```text
IF official IMD warning is severe
    -> label official warning prominently

IF river observation reaches an official/source-defined alert state
    -> river alert

IF rainfall/forecast is materially elevated
AND ML susceptibility is high
    -> FloodPulse elevated-risk context
```

The exact logic must be based on available source fields and documented thresholds.

Do not invent hydrological danger thresholds simply to make alerts fire.

Every alert should store:

```text
source
trigger
location
created_at
severity
message
model_version if model-derived
```

---

# 18. Shelter management system

This is a core feature, not an afterthought.

## Citizen-facing shelter properties

Minimum:

```text
name
coordinates
status
capacity
contact
last_updated
verification state
```

## Shelter status

Start with:

```text
CANDIDATE
ACTIVE
FULL
CLOSED
```

Only `ACTIVE` shelters should be shown as operational shelters to normal citizens.

## Administrator operations

Authorized admin users must be able to:

```text
create shelter
edit shelter
verify shelter
activate shelter
deactivate shelter
mark full
reopen shelter
view audit history
```

Each action should write an audit record:

```text
who
what
when
old value
new value
```

Do not expose a user-created or OSM POI as an official shelter merely because it looks like a suitable facility.

---

# 19. Emergency facility locator

Citizen map should optionally expose:

```text
active shelters
hospitals
fire stations
other verified emergency facilities
```

Nearest-location functionality should use PostGIS spatial operations where practical.

Examples conceptually:

```sql
ST_DWithin(...)
ST_Distance(...)
```

The API should return distance and useful contact/status information, not just coordinates.

---

# 20. Telegram bot

Use the official Telegram Bot API.

Minimum commands:

```text
/start
/location
/risk
/shelter
/alerts
```

A user should be able to:

1. register/associate a location or share current location;
2. request current FloodPulse status;
3. get nearby active shelters;
4. receive relevant alerts.

Alert messages must clearly label:

```text
Official warning
```

and

```text
FloodPulse model/context
```

Never fabricate warning text or pretend to speak on behalf of IMD/CWC/government agencies.

Store secrets only in environment variables or a proper secret-management mechanism. Never commit bot tokens.

---

# 21. Database design

Minimum PostGIS entities:

## `flood_cells`

```text
id
geom
cell_code
```

## `risk_predictions`

```text
id
cell_id
risk_probability
model_version
generated_at
provenance
```

## `rainfall_observations`

```text
id
station_or_grid_id
timestamp
rainfall_mm
geom
source
provenance
```

## `river_observations`

```text
id
gauge_id
timestamp
water_level
discharge
geom
source
provenance
```

## `shelters`

```text
id
name
geom
capacity
status
contact
source
provenance
verified_by
verified_at
created_at
updated_at
```

## `shelter_audit_log`

```text
id
shelter_id
admin_id
action
timestamp
old_value
new_value
```

## `official_warnings`

```text
id
source
location
severity
valid_from
valid_until
raw_reference
created_at
```

## `alerts`

```text
id
alert_type
location
severity
message
source
trigger_details
created_at
```

## `admins`

Use secure authentication. At minimum:

```text
id
username/email
password_hash
role
is_active
created_at
```

Never store plaintext passwords.

---

# 22. API design

Minimum endpoints conceptually:

```text
GET  /health
GET  /api/v1/risk/{lat}/{lon}
GET  /api/v1/risk/cells
GET  /api/v1/warnings
GET  /api/v1/rainfall
GET  /api/v1/rivers
GET  /api/v1/shelters
GET  /api/v1/shelters/nearby
GET  /api/v1/emergency-facilities

POST /api/v1/admin/shelters
PATCH /api/v1/admin/shelters/{id}
POST /api/v1/admin/shelters/{id}/activate
POST /api/v1/admin/shelters/{id}/deactivate
POST /api/v1/admin/shelters/{id}/full
GET  /api/v1/admin/shelters/{id}/audit

POST /api/v1/telegram/webhook if webhook mode is used
```

Use Pydantic validation and structured error responses.

Do not create dozens of endpoints before the core user flows work.

---

# 23. Frontend requirements

The React application must prioritize functional map interaction.

## Citizen view

Show:

```text
Karnataka risk map
current/official warning layer
active shelters
nearest shelter
emergency facilities
last-updated timestamps
source/provenance labels
```

Location interaction:

```text
select/click location
    -> susceptibility
    -> live warning context
    -> rainfall context
    -> nearest active shelter
```

## Admin view

Show:

```text
map
shelters
status
capacity
verification
recent updates
alerts
```

Admin actions must be clear and fast.

Avoid heavy animation, unnecessary charts, and cosmetic complexity until all critical workflows work.

---

# 24. Research/documentation requirements

Documentation is part of the deliverable.

Maintain:

## `README.md`

Must explain:

- project objective;
- architecture;
- setup;
- data sources;
- ML methodology;
- API/frontend/bot components;
- how to reproduce results;
- known limitations.

## `docs/DATA_SOURCES.md`

For every source:

```text
name
publisher
URL
license/access
coverage
resolution
purpose
retrieval date
processing notes
limitations
```

## `docs/DATA_DICTIONARY.md`

Define every important field, unit, CRS, and provenance state.

## `docs/DECISIONS.md`

Log:

```text
decision
context
alternatives considered
reason
consequence
```

Include failed approaches.

## `docs/MODEL_CARD.md`

Include:

```text
model purpose
training data
target
features
split strategy
metrics
limitations
known biases
intended use
not intended use
version
```

## `docs/EXPERIMENT_LOG.md`

Each experiment:

```text
experiment id
date
hypothesis
change
data version
model config
result
interpretation
next decision
```

## `docs/ARCHITECTURE.md`

Maintain current architecture and data flows.

## `docs/TEST_CHECKLIST.md`

Keep integration/system acceptance tests updated.

---

# 25. Research paper plan

The implementation should generate evidence needed for the research paper continuously, not at the end.

Recommended sections:

```text
1. Abstract
2. Introduction
3. Problem Definition
4. Karnataka Study Area
5. Related Work
6. Data Sources
7. Data Provenance and Quality Control
8. Flood Label Construction
9. Feature Engineering
10. Model Development
11. Temporal Validation
12. Spatial Risk Mapping
13. Live Warning Integration
14. Shelter Management Architecture
15. System Implementation
16. Results
17. Error Analysis
18. Limitations
19. Discussion
20. Conclusion
```

Every formula, source-dependent methodology, dataset statistic, and technical claim must have a traceable citation.

Never manufacture literature references.

---

# 26. Anti-AI-generation research discipline

The project must reflect the actual engineering process.

Do:

- make incremental commits;
- write descriptive commit messages;
- retain meaningful failed experiments;
- document discarded features;
- report weaknesses honestly;
- report class-wise metrics;
- explain data limitations;
- use real source versions and retrieval dates;
- maintain reproducible scripts.

Do not:

- generate a fake history in bulk;
- fabricate “failed attempts” that never happened;
- deliberately inject mistakes to make the repository look human;
- hide poor results;
- invent benchmark numbers;
- copy a research paper's exact claims without verification;
- make the project look artificially complex.

The repository should look like a real engineering project because the engineering process itself is real and traceable.

---

# 27. 20-day delivery plan

The agent must treat these as hard gates. If a phase is not complete, reduce scope rather than adding new features.

## Day 1 — project bootstrap + source verification

Deliver:

- repository structure;
- Python/Node environments;
- Docker Compose baseline;
- FastAPI health endpoint;
- React shell;
- PostGIS database starts;
- Alembic configured;
- CI/pre-commit baseline;
- source inventory and accessibility table.

Gate:

> All core tools start successfully from a clean checkout.

## Day 2 — acquire IFI + inspect

Deliver:

- raw IFI/IFI-Impacts data;
- source metadata;
- schema inspection;
- Karnataka extraction;
- event count/coverage report.

Gate:

> Real Karnataka historical flood records are confirmed and inspectable.

## Day 3 — rainfall ingestion

Deliver:

- IMD historical rainfall adapter;
- Karnataka/NWDP rainfall adapter where usable;
- coverage check;
- missingness report;
- normalized intermediate dataset.

Gate:

> Rainfall can be joined to the selected event period.

## Day 4 — spatial layers

Acquire and normalize:

- KGIS boundaries;
- SRTM;
- land cover;
- river layer.

Derive:

- elevation;
- slope;
- distance-to-river.

Gate:

> Every required static feature can be generated for the modelling grid.

## Day 5 — target and labels

Build and document:

- modelling grid;
- event windows;
- positive samples;
- defensible negative-sample strategy;
- label QA plots/statistics.

Gate:

> Training-target definition is documented and reproducible.

## Day 6 — training dataset

Build:

```text
training_samples.parquet
feature_schema.json
provenance metadata
```

Gate:

> A real, reproducible training table exists.

## Day 7 — baseline RF

Train:

- class-weighted Random Forest;
- baseline evaluation;
- feature importance.

Gate:

> There is a real baseline result, regardless of whether it is good.

## Day 8 — temporal validation

Finalize:

- temporal split;
- test metrics;
- confusion matrix;
- per-class precision/recall/F1;
- ROC-AUC where valid.

Gate:

> Primary evaluation is frozen and documented.

## Day 9 — error analysis

Inspect:

- false positives;
- false negatives;
- class balance;
- calibration/probability behavior if practical;
- feature leakage.

Gate:

> Major methodological weaknesses are recorded.

## Day 10 — model artifact + map output

Produce:

- versioned model artifact;
- prediction grid;
- map-ready risk data;
- model card.

Gate:

> Risk map can be loaded independently of training code.

## Day 11 — PostGIS integration

Load:

- risk cells;
- boundaries;
- rivers;
- observations;
- shelters schema.

Gate:

> Geospatial backend queries work.

## Day 12 — FastAPI core

Implement:

- risk endpoints;
- warning endpoints;
- rainfall/river endpoints;
- shelter endpoints.

Gate:

> APIs return real data end-to-end.

## Day 13 — live-data integration

Implement the minimum reliable IMD/NWDP/CWC ingestion needed for live context.

Gate:

> Live/near-live source data is source-labelled and visible through API.

## Day 14 — admin portal

Implement:

- admin authentication;
- shelter creation;
- activate/deactivate/full;
- audit history.

Gate:

> Shelter lifecycle works through the UI and database.

## Day 15 — citizen map

Implement:

- risk map;
- warning layer;
- shelters;
- emergency facilities;
- location query.

Gate:

> A citizen can find risk and an active shelter.

## Day 16 — Telegram

Implement:

- command handling;
- location flow;
- risk response;
- shelter response;
- alert delivery.

Gate:

> Telegram can return real system information.

## Day 17 — integration + alert engine

Join:

```text
model
+ live conditions
+ admin shelter state
+ alert delivery
```

Gate:

> A single scenario can be traced from data to alert to shelter.

## Day 18 — testing

Test:

- missing source;
- API failure;
- invalid coordinates;
- database failure;
- no shelter;
- closed/full shelter;
- admin permissions;
- Telegram failure;
- stale source data.

Gate:

> Critical failures are handled explicitly.

## Day 19 — paper + final documentation

Generate:

- plots;
- metrics;
- methodology text;
- architecture figure;
- limitations;
- reproducibility instructions.

Gate:

> Every number in the paper traces to a file, script, or source.

## Day 20 — release freeze

Do:

- clean-install test;
- Docker test;
- API test;
- frontend test;
- Telegram test;
- admin test;
- README review;
- citation review;
- provenance review;
- demo flow;
- Git release/tag.

Do not introduce new research features on Day 20.

---

# 28. Scope-cutting rules when behind schedule

If the project is behind schedule, cut in this order:

1. additional ML features;
2. NDEM integration;
3. advanced analytics;
4. advanced Telegram conversation features;
5. secondary emergency POI types;
6. optional dashboards/charts;
7. advanced spatial stress tests.

Never cut:

- real data provenance;
- label documentation;
- temporal evaluation;
- admin shelter workflow;
- API/database correctness;
- core citizen map;
- failure handling;
- research limitations.

---

# 29. Acceptance criteria

FloodPulse is considered functionally complete only when all of the following are true.

## Data

- real flood inventory is installed;
- Karnataka records are identified;
- rainfall data is installed;
- terrain and spatial layers are installed;
- provenance is recorded;
- dataset versions are recorded.

## ML

- target is documented;
- feature schema is documented;
- model trains from real data;
- temporal split is used;
- per-class metrics exist;
- held-out test results are saved;
- feature importance/error analysis exists;
- model version is stored.

## Backend

- database starts from clean checkout;
- migrations work;
- geospatial queries work;
- health check works;
- API validates input;
- errors are explicit.

## Frontend

- map renders;
- risk data renders;
- warnings render;
- active shelters render;
- nearest shelter works;
- admin portal works.

## Shelter

- admin can create shelter;
- admin can activate/deactivate;
- full/closed status is reflected immediately;
- audit log is written;
- citizens see only operational shelters.

## Telegram

- bot starts;
- location works;
- shelter lookup works;
- risk lookup works;
- alert flow works;
- secrets are protected.

## Research

- all material claims cited;
- data sources documented;
- failed approaches documented;
- limitations documented;
- exact model configuration recorded;
- results reproducible.

---

# 30. Testing strategy

## Unit tests

Test:

- rainfall rolling calculations;
- CRS transformations;
- label construction;
- geospatial distance calculations;
- API validation;
- shelter state transitions;
- alert rule evaluation.

## Integration tests

At minimum:

```text
source -> processor
processor -> database
model -> PostGIS
FastAPI -> PostGIS
React -> FastAPI
Telegram -> FastAPI
admin -> shelter -> citizen map
```

## End-to-end scenario

Build one fully reproducible test using real project data:

```text
choose a real Karnataka location
        ↓
retrieve FloodPulse susceptibility
        ↓
retrieve current/most recent official context
        ↓
retrieve active shelters
        ↓
choose nearest shelter
        ↓
send Telegram-compatible alert response
```

Do not fabricate the scenario's observations.

---

# 31. Security requirements

Minimum:

- secrets in environment variables;
- no credentials in Git;
- password hashing;
- admin authorization checks;
- input validation;
- SQL parameterization/ORM;
- CORS configured deliberately;
- Telegram webhook validation if webhook mode is used;
- audit logs for administrative changes.

Do not implement complicated enterprise IAM unless required.

---

# 32. Performance priorities

For the 20-day prototype:

Prioritize:

1. correct spatial queries;
2. reasonable map payload size;
3. indexed PostGIS geometry;
4. cached/static model predictions where appropriate;
5. bounded external API requests;
6. background refresh for live-source ingestion where necessary.

Do not prematurely optimize the ML training process unless it blocks progress.

---

# 33. GIS implementation rules

Use one documented canonical CRS strategy.

Typical pattern:

- store geometries in a PostgreSQL/PostGIS geographic/project CRS appropriate to operations;
- perform metric distance/area calculations in a suitable projected CRS or correct geography functions;
- document all transformations.

Never mix latitude/longitude axes accidentally.

Every spatial dataset must have its CRS identified before joining.

QA must include:

```text
bounds overlap Karnataka?
geometry valid?
coordinates plausible?
empty geometry?
duplicate geometry?
```

---

# 34. Reproducibility

Every important transformation should be executable from a script rather than an undocumented notebook-only manual step.

Preferred pipeline:

```text
raw data
  -> validate
  -> normalize
  -> derive features
  -> construct labels
  -> build training table
  -> train
  -> evaluate
  -> generate predictions
  -> load PostGIS
```

Store configuration separately from code.

Example:

```text
configs/
  data.yaml
  model.yaml
  app.yaml
```

Do not hardcode local machine paths.

---

# 35. Agent operating procedure

When executing this skill, the agent must behave in the following order.

## Phase A — inspect

Read:

- repository structure;
- existing README;
- existing docs;
- existing scripts;
- Git status/history;
- environment setup.

Do not overwrite working files simply because this skill contains an ideal structure.

## Phase B — verify sources

Research and verify current access to the required datasets.

Produce:

```text
data source
access status
coverage
license
format
next action
```

## Phase C — build the data foundation

Do not start visual application polish before the real model dataset is established.

## Phase D — build baseline ML

Get one honest baseline working before expanding features.

## Phase E — integrate application

Only after model/data output exists should the agent expose the risk map through the application.

## Phase F — integrate operations

Add warnings, shelters, Telegram, and admin controls.

## Phase G — test and document

No release without the acceptance criteria.

---

# 36. Agent decision hierarchy

When two choices conflict, use this priority order:

```text
1. scientific validity
2. real-data integrity
3. safety/accuracy of user-facing warnings
4. reproducibility
5. project completion
6. maintainability
7. performance
8. visual polish
```

A visually impressive but methodologically invalid feature must be rejected.

A theoretically superior method that cannot be validated in 20 days must be deferred.

---

# 37. Required Git workflow

Use incremental commits.

Recommended pattern:

```text
chore: bootstrap project infrastructure
feat(data): add IFI source adapter
feat(data): add IMD rainfall ingestion
feat(features): derive terrain features
feat(labels): build flood event labels
feat(ml): train baseline random forest
feat(ml): add temporal evaluation
feat(api): expose risk endpoints
feat(shelter): add admin shelter lifecycle
feat(telegram): add risk and shelter commands
feat(ui): add citizen risk map
feat(ui): add admin shelter controls
test: add end-to-end flood workflow
docs: document methodology and limitations
```

Commit messages must describe actual work performed.

---

# 38. Required project artifacts at completion

At minimum:

```text
README.md
PROJECT_MASTER_PLAN.md
docs/DECISIONS.md
docs/DATA_SOURCES.md
docs/DATA_DICTIONARY.md
docs/MODEL_CARD.md
docs/EXPERIMENT_LOG.md
docs/ARCHITECTURE.md
docs/TEST_CHECKLIST.md

raw/real data metadata
processed training dataset metadata
trained model artifact
model evaluation results
risk prediction output
PostGIS migrations
FastAPI application
React application
Telegram bot
Docker Compose
CI pipeline
research paper
```

The exact binary/raw-data distribution strategy must respect source licenses. If raw data cannot be committed, provide reproducible download instructions and provenance metadata instead.

---

# 39. Final demo scenario

The finished demonstration should tell one coherent story:

```text
1. Open Karnataka FloodPulse map.
2. Show historical/ML susceptibility layer.
3. Select a real Karnataka location.
4. Show FloodPulse risk score.
5. Show current/most recent official warning context.
6. Show rainfall/river context where available.
7. Show nearest ACTIVE shelter.
8. Switch to Admin portal.
9. Change shelter from ACTIVE to FULL or CLOSED.
10. Return to citizen view and demonstrate the changed availability.
11. Trigger/show the corresponding alert workflow.
12. Demonstrate Telegram response.
```

Every displayed value must originate from a real source, a clearly labelled derived computation, a model output, or an explicitly admin-entered operational record.

---

# 40. Known limitations that must be preserved

The agent must not attempt to hide these limitations.

Potential limitations include:

- flood inventories have reporting and observation biases;
- satellite-derived inundation can miss peak flooding because of revisit/cloud constraints;
- coarse historical rainfall limits fine spatial precision;
- administrative/event records may not represent exact cell-level truth;
- OSM/emergency datasets may be incomplete or change over time;
- some official data services may be inaccessible or restricted;
- the ML output is a susceptibility/event-likelihood signal, not a guaranteed forecast;
- operational warning authority remains with official agencies.

The exact limitation list must be updated to match actual evidence encountered during implementation.

---

# 41. What the agent must do if a data source fails

Use this decision tree:

```text
Required source fails
      |
      +-- Can an official equivalent satisfy the same target?
      |       |
      |       +-- yes -> document substitution -> continue
      |       +-- no  -> reduce scope or change target honestly
      |
Optional source fails
      |
      +-- skip -> document limitation -> continue
```

Never substitute a fabricated dataset.

Examples:

```text
NDEM unavailable -> continue without NDEM
Survey of India DTM unavailable -> use documented open DEM such as SRTM
one secondary POI source unavailable -> use official Karnataka OGD/OSM where suitable
live API unavailable -> expose last verified observation with timestamp only if the product semantics allow it; otherwise show unavailable
```

Do not disguise stale data as live data.

---

# 42. What the agent must do if model performance is poor

Do not hide it.

First investigate:

```text
label quality
spatial leakage
temporal leakage
class imbalance
feature leakage
misaligned timestamps
CRS mismatch
sample bias
```

Then try only a small number of justified improvements:

```text
better negative sampling
better temporal feature definition
class weighting
feature pruning
additional validated terrain variable
calibration
```

If results remain weak:

> report the weak result and explain why it occurs.

Do not tune until the metric becomes impressive.

---

# 43. Definition of “done”

The project is done when:

```text
REAL DATA
   ↓
VALIDATED PIPELINE
   ↓
REPRODUCIBLE LABELS
   ↓
HONEST TEMPORAL ML EVALUATION
   ↓
POSTGIS RISK MAP
   ↓
FASTAPI
   ↓
REACT CITIZEN + ADMIN UI
   ↓
REAL/VERIFIED LIVE CONTEXT
   ↓
ADMIN-CONTROLLED SHELTERS
   ↓
TELEGRAM ALERTS
   ↓
TESTED DEMO
   ↓
DOCUMENTED RESEARCH PAPER
```

A feature is not “done” merely because code exists. It is done only when the relevant acceptance criteria, tests, provenance, and documentation exist.

---

# 44. First command/task for a new agent

When this skill is loaded into an agentic coding environment, the agent must begin by:

1. inspect the current repository and Git status;
2. read existing project documentation before changing architecture;
3. verify the actual current date and the remaining 20-day schedule;
4. audit data availability;
5. create/update `docs/DATA_SOURCES.md` and `docs/DECISIONS.md` with source verification;
6. acquire the real India Flood Inventory data;
7. extract and inspect Karnataka flood events;
8. report the first concrete data facts to the operator;
9. proceed to rainfall joining only after the flood source is understood.

Do **not** begin by building the dashboard UI.

Do **not** begin by training on synthetic data.

Do **not** begin by selecting a more complicated ML architecture.

The first hard evidence the agent should produce is:

```text
- exact IFI/IFI-Impacts release used
- file(s) downloaded
- coverage period
- number of Karnataka flood events/records after extraction
- available spatial representation
- available date fields
- any important quality limitation
- whether the first rainfall join is feasible
```

Then continue from evidence, not assumptions.

---

# 45. Compact operating mantra

```text
REAL DATA > MOCK DATA
EVIDENCE > ASSUMPTION
SIMPLE VALID MODEL > COMPLEX UNVALIDATED MODEL
OFFICIAL WARNING > STUDENT-GENERATED AUTHORITY
ADMIN-VERIFIED SHELTER > ASSUMED FACILITY
TEMPORAL TEST > RANDOM SPLIT
DOCUMENTED FAILURE > HIDDEN FAILURE
WORKING SYSTEM > UNFINISHED FEATURES
20-DAY DELIVERY > UNBOUNDED SCOPE
```

End of FloodPulse Agent Skill.
