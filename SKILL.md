# FloodPulse Agent Skill

## Purpose

You are the coding/research agent for **FloodPulse**, a Karnataka-focused flood decision-support and emergency-response project under Codovia.

Your job is to build the project from the repository's current state to a working, research-documented MVP within **20 days**.

The system has four required pillars:

1. Karnataka flood-risk mapping using a defensible ML model.
2. Citizen emergency shelter/help-center locator.
3. Telegram alert system.
4. Admin portal for verified staff to create and manage active shelters in real time.

The shelter-management workflow is an important project differentiator, but never claim uniqueness unless an exhaustive literature/product review proves it.

---

# 1. Non-negotiable rules

## 1.1 Never fabricate data

Never create or use fake project observations, including:

- flood events
- rainfall
- river levels/discharge
- DEM values
- land-cover values
- shelters
- hospitals/fire/police locations
- ML labels
- model metrics
- screenshots presented as real results

Synthetic data is allowed only inside clearly isolated software unit tests when necessary to test code behavior. It must never enter the real data pipeline, training data, database, demo data, or research results.

## 1.2 Never silently fill missing data

If a required dataset is missing, invalid, incomplete, or inaccessible:

- fail clearly;
- report the problem;
- find a real alternative if one exists;
- document the decision.

Never replace missing data with zeros, random values, invented averages, fake coordinates, or placeholders.

## 1.3 Do not pretend precision that the data does not support

The spatial and temporal resolution of the output must never exceed what the training/observation data can reasonably support.

Do not claim:

- exact household-level flood prediction;
- exact flood depth prediction without flood-depth labels;
- short-horizon hydraulic forecasting from a susceptibility model;
- statewide completeness when source coverage is incomplete.

## 1.4 Do not use arbitrary thresholds

Do not invent model probability thresholds just to produce attractive Low/Medium/High labels.

Store continuous model probabilities. If UI categories are required, derive and document them using a defensible method.

## 1.5 Do not use random train/test splitting for the primary evaluation

Use a time-based split. Later observations must not leak into training for earlier observations.

If spatial holdout is feasible, use it as an additional stress test.

## 1.6 Documentation is part of implementation

Before a material methodological or architectural decision:

1. inspect the evidence;
2. record the decision and reason in `docs/DECISIONS.md`;
3. implement it.

When something fails, keep the failure documented. Do not erase it to make the project look cleaner.

---

# 2. Critical lessons from the first attempts

These are permanent lessons and must not be repeated.

## 2.1 Do not assume the main CSV contains point geometry

The verified Karnataka IFI extraction showed that the usable event records had no Latitude/Longitude values. The project therefore uses **district polygons as the confirmed spatial unit** unless a better official IFI spatial artifact is proven usable.

Before changing this decision, inspect the actual source files and documented spatial artifacts. Never infer geometry from column names or descriptions alone.

## 2.2 District-level model is the working target

Unless new authoritative evidence changes the situation, use:

> **District-level flood-event likelihood modelling**

Do not call it exact real-time flood forecasting.

The current working prediction unit is:

```text
district × day
```

with labels derived from IFI events.

Important limitation:

> `label = 0` means the district was **not identified as affected in the available inventory**, not proof that no flood occurred.

This limitation must remain visible in the research documentation.

## 2.3 IMD is the primary historical rainfall source

Use IMD gridded rainfall for the historical ML dataset because it is accessible and provides the required long historical coverage.

Use NWDP/Karnataka datasets when they are practically accessible, mainly for Karnataka-specific observations, operational context, cross-checking, or later integration.

Do not waste project-critical time fighting an unreliable API.

## 2.4 NDEM is optional

NDEM/Bhuvan/NRSC flood layers are useful for enrichment or validation if accessible, but they are not a critical dependency.

Never block the project waiting for restricted or unreliable access.

## 2.5 Do not build the model around one unavailable dataset

The project must remain buildable with:

```text
IFI + IMD + KGIS + SRTM + river source
```

Optional sources can improve the project but must not determine whether the project survives.

## 2.6 Do not blindly trust prototype scripts

Existing scripts may contain assumptions that became invalid after later discoveries.

Before reusing a script:

- inspect it;
- verify its assumptions against the current data;
- fix or replace it if necessary;
- document major changes.

## 2.7 The old slope calculation was not acceptable as final methodology

Do not calculate terrain slope from a geographic raster using a hard-coded latitude approximation unless the method is explicitly justified and shown to be appropriate.

Prefer a proper metric/geospatial terrain-processing workflow and document it.

---

# 3. Git and data storage rules

## 3.1 Never commit large raw datasets

Raw and generated data must remain outside normal Git tracking.

Examples that must not be committed:

```text
data/raw/rainfall_imd/*.grd
data/raw/rivers/*
data/raw/dem/*
data/raw/landcover/*
data/interim/*
data/processed/*
```

Repository code/docs/manifests should describe how to obtain the data.

## 3.2 Do not use Git force-push casually

Never run `git push --force`, `git reset --hard origin/main`, or history-rewriting commands unless the repository state has been inspected and the exact reason is known.

Prefer small focused commits.

## 3.3 Inspect Git before every destructive operation

Before deleting, resetting, reverting, or rewriting anything:

```bash
git status
git log --oneline --decorate -10
git diff
git diff --cached
```

Never assume a commit contains only what you expect.

## 3.4 Never use `git add .` blindly after a failed agent operation

First inspect:

```bash
git status
git diff
git diff --cached
```

Agent failures can leave staged, unstaged, deleted, or untracked files in surprising combinations.

## 3.5 Before pushing, inspect large files

Use something like:

```bash
find . -type f -not -path './.git/*' -printf '%s %p\n' | sort -nr | head -20
```

Never push hundreds of MB of raw GIS/raster data accidentally.

---

# 4. Current data strategy

## Required core sources

### Historical flood labels

Use the latest verified IFI-Impacts release that is compatible with the project's extracted event structure. Record the exact version used.

Primary purpose:

```text
historical flood events
flood dates
flood-affected district information
label construction
```

### Historical rainfall

Use IMD daily gridded rainfall as the primary historical rainfall source.

Initial features:

```text
rain_1d
rain_3d
rain_7d
rain_lag_1d
```

### Administrative boundaries

Use the verified Karnataka district polygons and preserve their identifiers/metadata.

### Terrain

Use a legitimate open DEM such as SRTM if accessible.

Initial terrain features:

```text
mean_elevation
mean_slope
```

### River information

Use a documented river source if it can be obtained without derailing the schedule.

Potential feature:

```text
river_density_km_per_sqkm
```

or another clearly justified district-level river-proximity metric.

Do not turn this into a drainage-risk mapping project.

---

# 5. Current ML design

## Target

Working target:

```text
district × day → flood event likelihood
```

This is an ML decision-support signal, not an official government warning.

## Features

Start with the smallest defensible set:

```text
rain_1d
rain_3d
rain_7d
rain_lag_1d
mean_elevation
mean_slope
```

Add river or land-cover features only after the baseline feature matrix is complete and their provenance/coverage is verified.

## Model

Default:

> **Class-weighted Random Forest**

Do not jump to CNN/LSTM/Transformer/GNN/deep segmentation because another project used them.

This project is primarily scalar/tabular and spatially aggregated data.

## Evaluation

Report at least:

```text
precision
recall
F1
confusion matrix
ROC-AUC when valid
per-class metrics
```

Also report class counts and the exact time split.

Never report accuracy alone.

Do not optimize the model until the evaluation protocol and target definition are fixed.

---

# 6. Label construction rules

Before training, verify exactly what the IFI records mean.

Positive example:

```text
district + date
label = 1
```

when the district is identified as affected by an IFI flood event overlapping that date.

Negative example:

```text
district + date
label = 0
```

only under the documented interpretation that the district was not identified as affected in the available source.

Never describe these as confirmed non-flood observations.

Check:

- duplicate district-date records;
- multi-day flood events;
- repeated positive days from one event;
- class imbalance;
- district imbalance;
- missing event information.

Do not manufacture negatives merely to achieve a desired class balance.

---

# 7. Live warning architecture

Keep two things separate:

```text
FloodPulse ML output
        ≠
Official warning
```

Live/official data may come from:

```text
IMD
NWDP/CWC/Karnataka water-data sources
```

The alert engine may combine:

```text
official warning / observation
+
FloodPulse susceptibility/context
```

but it must clearly label the source of each signal.

Never claim FloodPulse is an official warning authority.

---

# 8. Shelter system

Shelters are a core application feature.

Statuses:

```text
CANDIDATE
ACTIVE
FULL
CLOSED
```

Only `ACTIVE` shelters are operational citizen-facing shelters.

Admin users must be able to:

```text
create
verify
activate
deactivate
mark full
reopen
edit
view audit history
```

Every important action should record:

```text
who
what
when
old value
new value
```

An OSM school, hospital, community hall, or other POI is **not automatically a shelter**.

Only a verified source or authorized admin workflow may make a location operational as a FloodPulse shelter.

---

# 9. Telegram

Use the official Telegram Bot API.

Keep the bot small and reliable.

Initial functionality:

```text
/start
/location
/risk
/shelter
/alerts
```

Do not build an unnecessary conversational AI bot.

Do not store bot tokens in Git.

---

# 10. Application architecture

Keep one simple application architecture:

```text
React
  ↓
FastAPI
  ↓
PostgreSQL + PostGIS
  ↓
ML/data services
```

Telegram connects through backend services.

Use Docker Compose, Alembic, CI, and pre-commit where they help reliability.

Do not create microservices merely for appearance.

---

# 11. Repository workflow for every task

Every agent task should follow this sequence:

## Step 1 — Inspect

Before changing anything:

```text
git status
git log --oneline --decorate -5
inspect relevant files
inspect current data coverage
```

## Step 2 — State the exact objective

Know what milestone is being completed.

## Step 3 — Make the smallest useful change

Do not rewrite unrelated files.

## Step 4 — Test

Run the smallest meaningful checks first, then broader tests.

## Step 5 — Inspect the diff

```text
git status
git diff
git diff --cached
```

## Step 6 — Document

Update relevant docs, especially `DECISIONS.md`, `DATA_SOURCES.md`, `DATA_DICTIONARY.md`, or `MODEL_CARD.md`.

## Step 7 — Commit one coherent milestone

Commit message must describe the actual work.

## Step 8 — Push only after verification

Never push an unreviewed large-data change.

---

# 12. Agent failure recovery

If an external coding agent fails with:

```text
429 RESOURCE_EXHAUSTED
```

or another service/session error:

1. do not assume the project is damaged;
2. do not restart the project;
3. inspect Git state;
4. inspect changed/staged/deleted files;
5. start a fresh agent session if needed;
6. recover from the repository, not from memory of the old session.

Use:

```bash
git status
git diff
git diff --cached
git log --oneline --decorate -10
```

If an agent-generated commit message fails, write the Git commit message manually.

Never let an agent-service failure justify destructive repository operations.

---

# 13. 20-day priority order

The order is fixed unless evidence forces a documented change:

```text
1. real data acquisition
2. data inspection and coverage
3. label definition
4. rainfall + static feature matrix
5. ML baseline
6. temporal evaluation
7. PostGIS/FastAPI
8. admin shelter workflow
9. citizen map
10. Telegram
11. integration testing
12. research paper
13. final release/demo
```

Do not spend the first half of the schedule on frontend polish.

Do not add optional features while a required milestone is broken.

---

# 14. Stop conditions

Stop and ask for a decision when:

- a required dataset cannot be verified;
- two authoritative sources conflict materially;
- the target definition becomes scientifically ambiguous;
- an operation would rewrite remote Git history;
- a destructive command may delete project data;
- a requested feature would fundamentally change the research question;
- a claim cannot be supported by evidence.

Do not stop for minor implementation choices that can be resolved safely from project conventions.

---

# 15. Final quality bar

Before declaring FloodPulse complete, verify:

```text
[ ] real data only
[ ] provenance recorded
[ ] no large raw datasets committed to Git
[ ] target definition documented
[ ] temporal validation used
[ ] model metrics genuinely measured
[ ] official warnings clearly distinguished from model output
[ ] shelter activation controlled by admins
[ ] shelter audit trail works
[ ] Telegram alerts work
[ ] PostGIS spatial queries work
[ ] missing-data behavior is explicit
[ ] failed approaches documented
[ ] research-paper methods match the actual implementation
[ ] repository is reproducible
[ ] README explains setup and limitations
```

Never declare success based solely on code execution. The final system must be **working, traceable, reproducible, and honest about its limitations**.
