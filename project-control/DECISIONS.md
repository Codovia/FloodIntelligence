# Project Decisions

## DEC-001 — Use Existing Git Repository as New Baseline

**Date:** 2026-08-27

**Decision:** Keep the existing local Git repository and use it as the new project baseline.

**Context:**
The local repository contains only the initial commit and README.md. No previous application source code exists in the working tree.

**Evidence:**
Commit `f4ad325` contains only `README.md`.

**Reason:**
There is no application code that needs to be preserved in this working tree, so a new development baseline can safely be established without destroying existing history.

**Affected Components:**
Repository and project structure.

**Reversal Conditions:**
If remote repository history is later found to conflict with the approved project baseline, stop and review before synchronization.
