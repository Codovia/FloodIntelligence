# Non-Negotiable Constraints

1. **No synthetic, mocked, or fabricated data** — all data must be real, with provenance tracked.
2. **Provenance classification per record:** `REAL` / `DERIVED_FROM_REAL` / `MODEL_OUTPUT` / `USER_REPORTED` / `UNKNOWN`.
3. **The project must not appear AI-generated.** Log all decisions, don't inflate accuracy, maintain incremental commits.
4. **Label semantics are strict:** `label = 0` means "not identified as affected" — never "confirmed no flood."
5. **No arbitrary risk threshold cutoffs.** Store continuous probabilities, document any thresholds used for alerts.
6. **No hard-coded latitude-based slope approximations.** Use real terrain data (SRTM).
7. **Reject templated, unverifiable architectures.** 
8. **Git discipline:** no raw datasets in repo, no casual force-pushes.
9. **Agent-failure recovery:** recover from git history, don't rebuild from scratch.
