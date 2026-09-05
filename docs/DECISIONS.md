# Architecture and methodology decisions

## 2026-09-05 — Start with a strict, data-first foundation

**Decision:** Build the repository around a district-day baseline and explicit
data contracts before adding frontend or operational integrations.

**Reason:** The verified IFI extraction does not provide point geometry, so the
defensible initial spatial unit is the Karnataka district polygon. The project
must not fabricate observations or silently replace inaccessible data.

**Consequence:** The first implementation fails clearly when core files are
missing. Model training, metrics, and UI categories will only be added after
source coverage and label semantics are inspected.

## Fixed baseline design

- Historical labels: verified IFI-Impacts extraction.
- Historical rainfall: IMD daily gridded rainfall.
- Static terrain: SRTM-derived mean elevation and mean slope.
- Initial model: class-weighted Random Forest.
- Primary evaluation: chronological/time-based split.

