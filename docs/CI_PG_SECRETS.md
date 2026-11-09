# CI: validación PostgreSQL real (Fase 0)

El workflow `.github/workflows/fase0-check.yml` ejecuta SQLite siempre. El job `fase0-pg-real` está **deshabilitado (`if: false`)**.

Para habilitarlo en GitHub Actions **sin exponer credenciales**:
1. Crear secretos de repositorio/entorno (Settings → Secrets and variables → Actions):
   - `POOLAR_SECRET_KEY_TEST` (clave solo pruebas)
   - `POOLAR_TEST_POSTGRES_URL` (Postgres desechable/CI, `postgresql+psycopg2://...?...sslmode=require`)
2. Cambiar `if: false` por la condición deseada (p. ej. `if: github.event_name == 'workflow_dispatch'` o un entorno protegido).
3. El job ejecuta `alembic upgrade head` y `tests/test_fase0_p04_concurrency_pg.py`.

**Nunca** commitear `.env`, URLs con contraseña ni tokens. Usar bases desechables para pruebas de carrera.
