# Agent Skill Spec (FloodPulse)

This document dictates the behavior and methodology of AI agents operating within the FloodPulse project.

1. **Methodology:** Agents must never mock or fabricate data. 
2. **Git Discipline:** Commit messages must be meaningful. No giant single commits. Force pushes are disallowed.
3. **Recovery:** If an agent gets into a broken state, it must attempt to recover via git history rather than starting from scratch.
4. **Documentation:** Agents must diligently log their rejected approaches in `DECISIONS.md`.
