# Trama Abierta — MVP v0.6 independiente

![Trama Abierta Logo](assets/logo_trama_abierta.svg)

[![Estado](https://img.shields.io/badge/estado-prototipo%20no%20produccion-blue?logo=shield)](docs/cierre_iteracion.md)
[![Versión](https://img.shields.io/badge/version-v0.6--mvp-blue?logo=tag)]()
[![Tests](https://img.shields.io/badge/tests-31%20passed%2C%201%20skipped-2ea44f?logo=pytest)]()
[![Datos](https://img.shields.io/badge/datos-syntetic%20pilot-7C3AED?logo=database)]()
[![Auth](https://img.shields.io/badge/auth-PBKDF2--SHA256%20%2B%20JWT-2563EB?logo=lock)]()
[![PostgreSQL](https://img.shields.io/badge/postgresql-pendiente%20servidor-red?logo=postgresql)]()
[![Repos](https://img.shields.io/badge/repos%20auditados-no%20modificados-10B981?logo=git)]()

Estado: **Prototipo funcional, no producción**. Diseño independiente (`04_arquitectura_trama_abierta.md`), basado en `v0.5` documento maestro y resultados de auditoría (`audit_trama_abierta/`).

## Estado de la auditoría previa

- `P0` (`Anexo_Risk` privacidad/integridad): confirmada; no se copia código de `Anexo_Risk`; `auth` diseñado sin clave predeterminada; datos sensibles separados por diseño.
- `P1` (`EnRuta` secreto JWT): confirmada; `SECRET_KEY` requiere variable de entorno; falla segura si falta.
- `Anexo_Risk`/`EnRuta`/`CASE`: no integrados; se mantienen como referencias (`D`/`C`) con licencia pendiente o confirmada según corresponda.
- Datos sintéticos: etiquetados explícitamente (`DataProvenance`). No se presentan como resultados reales.
- No se declara "listo para producción"; no se afirma impacto verificado sin evidencia.

## Inicio rápido

### Requisitos previos
- Python 3.11+
- Docker y Docker Compose (opcional, para PostgreSQL)
- PostgreSQL 16 (opcional, para pruebas de integración)

### Variables de entorno

Copiar `.env.example` a `.env` y ajustar:

```bash
cp .env.example .env
```

Variables requeridas:
- `TRAMA_ABIERTA_SECRET_KEY` — secreto aleatorio para JWT (obligatorio, sin valor por defecto)
- `DATABASE_URL` — URL de conexión a la base de datos
- `TRAMA_DEMO_MODE` — `true`/`false` (false por defecto)
- `CORS_ALLOW_ORIGINS` — orígenes permitidos para CORS

### Instalación (desarrollo local)

```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python -m pytest tests/ -q

# Iniciar API
python -m uvicorn src.main:app --reload --port 8000
```

### Docker Compose (PostgreSQL + API)

```bash
# Construir y levantar servicios
docker-compose up -d db
docker-compose up -d api

# Ver logs
docker-compose logs -f api

# Detener (conserva datos)
docker-compose down

# Restablecer datos (destructivo)
docker-compose down -v
```

### Migraciones PostgreSQL

```bash
# Aplicar migraciones
alembic upgrade head

# Verificar revisión
alembic current
```

### Pruebas PostgreSQL

```bash
# Configurar URL de prueba
set TRAMA_TEST_POSTGRES_URL=postgresql+psycopg2://trama:trama@localhost:5432/trama_test

# Ejecutar tests
python -m pytest tests/ -q
```

### Interfaz

Abrir `interfaz/index.html` en el navegador (requiere API en `localhost:8000`).

1. Crear organización + usuario autorizado (o persona individual).
2. Registrar necesidad (`Need`).
3. Registrar recursos (`Resource`) con restricciones.
4. Crear iniciativa (`Initiative`) vinculada.
5. Registrar decisión (`Decision`) con método/version.
6. Registrar evento (`EventAudit`) de ejecución/medición.
7. Exportar `JSON`/`CSV`.

## Seguridad aplicada

- `SECRET_KEY` y `DATABASE_URL` solo por entorno; `fail` si faltan obligatorios.
- `auth` con `JWT` + `depends` por organización; sin clave fija.
- `Need`/`Resource`/`Initiative`/`Decision`/`EventAudit`: lectura pública solo si `public_access` configurado; datos sensibles (`contacto`, `dni`, `ubicaciones_privadas`) nunca en respuestas públicas.
- `EventAudit`: no copia datos personales a logs sin filtro.
- Pruebas: autenticación, expiración, aislamiento entre orgs, no acceso anónimo a escritura, ausencia de datos privados en `GET` público, transición válida, audit, exportación, datos sintéticos etiquetados.

## Datos

- Datos de desarrollo: sintéticos (`DataProvenance.source = "synthetic_pilot"`, `quality = "low"`, `assumptions = "development only"`). No se confunden con resultados verificados.
- Datos de piloto: autorizados por organización anfitriona, con consentimiento documentado.

## Instalación rápida (desarrollo)

```bash
# Instalar dependencias
python -m pip install -r requirements.txt

# Configurar variables (no en repositorio)
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export DATABASE_URL="postgresql://user:pass@localhost/trama_abierta"
# O para desarrollo local: sqlite (solo prototipo controlado)
export DATABASE_URL="sqlite:///./trama_abierta.db"

# Migraciones
python -m alembic upgrade head

# Tests
python -m pytest tests/ -q

# Iniciar
python -m uvicorn src.main:app --reload
```

## Limitaciones conocidas (documentadas, no ocultas)

- No incluye pagos ni custodia de fondos.
- No integra `Anexo_Risk` (especializado emergencias), `EnRuta` (logística) ni `CASE` (orquestación IA) hasta validar licencias y corregir `P0`/`P1`.
- `PostgreSQL` objetivo; `SQLite` solo para desarrollo controlado.
- No es producción; no afirma resultados de impacto sin evidencia.
- Datos sintéticos etiquetados; no usados como resultados reales.
