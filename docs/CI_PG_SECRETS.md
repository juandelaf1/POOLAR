# CI: Real PostgreSQL Validation (Phase 0)

> Updated: 2026-11-10. Status: **documented; PG CI job disabled by default**.

The workflow `.github/workflows/fase0-check.yml` always runs the SQLite suite. The `fase0-pg-real` job is **disabled (`if: false`)**.

To enable it in GitHub Actions **without exposing credentials**:
1. Create repository/environment secrets (Settings → Secrets and variables → Actions):
   - `POOLAR_SECRET_KEY_TEST` (test-only key)
   - `POOLAR_TEST_POSTGRES_URL` (disposable/CI PostgreSQL, e.g. `postgresql+psycopg2://...?...sslmode=require`)
2. Replace `if: false` with the desired condition (e.g. `workflow_dispatch` or a protected environment).
3. The job runs `alembic upgrade head` and PG-specific tests (e.g. `tests/test_fase0_p04_concurrency_pg.py`).

**Never** commit `.env`, credentialed URLs, or tokens. Use disposable databases for concurrency/race tests. Revalidate PG evidence in the target CI environment.
