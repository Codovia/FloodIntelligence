# Project Constraints

## Non-Negotiable Rules

1. Never fabricate environmental observations.
2. Never fabricate ML labels and present them as real.
3. Never invent external APIs or endpoints.
4. Missing data must remain explicitly missing.
5. Official warnings must remain separate from AI predictions.
6. Every important external observation must have provenance.
7. Every location must have validated coordinates and documented CRS.
8. Do not choose the final ML model before validating the dataset.
9. Do not introduce microservices unless there is a demonstrated need.
10. Do not introduce Kubernetes or blockchain.
11. AI coding agents must make small, reviewable changes.
12. Every implementation change must be tested and its diff reviewed.
13. Data availability determines the ML architecture.
14. If required data is unavailable, the system must report it as unavailable rather than inventing a substitute.

## Data Integrity

Allowed classifications:

- REAL
- DERIVED_FROM_REAL
- MODEL_OUTPUT
- USER_REPORTED
- UNKNOWN / UNVERIFIED

Synthetic data may be used for technical testing only and must never be presented as real observations or real ML ground truth.

## Development Rule

REQUEST
-> READ CONTEXT
-> PLAN
-> IMPLEMENT SMALL CHANGE
-> TEST
-> REVIEW DIFF
-> VERIFY
-> UPDATE DOCUMENTATION
-> COMMIT
-> HANDOFF
