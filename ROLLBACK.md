# Rollback Plan

If the state of the project breaks, do not rebuild from scratch. Follow this process:

1. Identify the last known good commit using `git log`.
2. Evaluate if the breakage is isolated to a few files (`git checkout <commit> -- <file>`) or requires a full hard reset (`git reset --hard <commit>`).
3. If database state is corrupted, down the docker container (`docker-compose down -v`) and restart to wipe the PostgreSQL volumes, then re-run migrations.
4. Document the failure reason in `DECISIONS.md`.
