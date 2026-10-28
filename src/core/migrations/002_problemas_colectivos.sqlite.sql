-- Migración 002 — Problemas colectivos y modelo centrado en personas
-- Dialecto: SQLite (prototipo de desarrollo).
-- La migración equivalente para PostgreSQL está pendiente de ejecución
-- contra un servidor real; ver docs/riesgos_pendientes.md.
--
-- Esta migración es aditiva sobre 001_init.sql. Usa CREATE TABLE IF NOT
-- EXISTS para no destruir datos existentes.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE,
    habilidades TEXT,
    preferencias_participacion TEXT,
    estado TEXT NOT NULL DEFAULT 'activa',
    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (estado IN ('activa', 'inactiva'))
);

CREATE TABLE IF NOT EXISTS operational_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'miembro',
    organizacion_id INTEGER NOT NULL REFERENCES organizaciones(id),
    activo INTEGER NOT NULL DEFAULT 1,
    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS necesidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organizacion_id INTEGER REFERENCES organizaciones(id),
    persona_id INTEGER REFERENCES personas(id),
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    poblacion_afectada TEXT,
    estado TEXT NOT NULL DEFAULT 'propuesta',
    visibilidad TEXT NOT NULL DEFAULT 'privada',
    criterios_exito TEXT,
    responsable_id INTEGER,
    responsable_tipo TEXT,
    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (estado IN ('propuesta','en_evaluacion','en_ejecucion','resuelto','cerrado')),
    CHECK (visibilidad IN ('privada','compartible','publica')),
    CHECK (responsable_tipo IS NULL OR responsable_tipo IN ('persona','organizacion'))
);

CREATE TABLE IF NOT EXISTS recursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_recurso TEXT NOT NULL,
    nombre TEXT NOT NULL,
    organizacion_id INTEGER NOT NULL REFERENCES organizaciones(id),
    necesidad_id INTEGER REFERENCES necesidades(id),
    disponibilidad TEXT NOT NULL DEFAULT 'disponible',
    restricciones TEXT,
    licencia_utilizacion TEXT NOT NULL,
    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS problemas_colectivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL,
    evidencias TEXT,
    estado TEXT NOT NULL DEFAULT 'detectado',
    origen_datos TEXT NOT NULL DEFAULT 'synthetic_pilot',
    organizacion_id INTEGER REFERENCES organizaciones(id),
    persona_id INTEGER REFERENCES personas(id),
    creado_por_id INTEGER REFERENCES operational_users(id) ON DELETE SET NULL,
    fecha_deteccion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (estado IN ('detectado','en_analisis','validado','cerrado')),
    CHECK (origen_datos IN ('synthetic_pilot','real_pilot')),
    CHECK (organizacion_id IS NOT NULL OR persona_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS necesidad_problema_colectivo (
    necesidad_id INTEGER NOT NULL REFERENCES necesidades(id) ON DELETE CASCADE,
    problema_colectivo_id INTEGER NOT NULL REFERENCES problemas_colectivos(id) ON DELETE CASCADE,
    PRIMARY KEY (necesidad_id, problema_colectivo_id)
);

CREATE TABLE IF NOT EXISTS problema_participantes_persona (
    problema_colectivo_id INTEGER NOT NULL REFERENCES problemas_colectivos(id) ON DELETE CASCADE,
    persona_id INTEGER NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    PRIMARY KEY (problema_colectivo_id, persona_id)
);

CREATE TABLE IF NOT EXISTS problema_participantes_organizacion (
    problema_colectivo_id INTEGER NOT NULL REFERENCES problemas_colectivos(id) ON DELETE CASCADE,
    organizacion_id INTEGER NOT NULL REFERENCES organizaciones(id) ON DELETE CASCADE,
    PRIMARY KEY (problema_colectivo_id, organizacion_id)
);

CREATE TABLE IF NOT EXISTS iniciativas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problema_colectivo_id INTEGER REFERENCES problemas_colectivos(id),
    responsable_id INTEGER,
    responsable_tipo TEXT,
    necesidad_id INTEGER REFERENCES necesidades(id),
    titulo TEXT,
    descripcion TEXT DEFAULT '',
    alternativas_evaluadas TEXT,
    criterios_decision TEXT NOT NULL,
    presupuesto_estimate REAL,
    plazo TEXT,
    estado TEXT NOT NULL DEFAULT 'propuesta',
    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (estado IN ('propuesta','en_ejecucion','finalizada','cerrada')),
    CHECK (responsable_tipo IS NULL OR responsable_tipo IN ('persona','organizacion'))
);

CREATE TABLE IF NOT EXISTS decisiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    iniciativa_id INTEGER NOT NULL REFERENCES iniciativas(id),
    tipo_decision TEXT NOT NULL,
    alternativa_elegida TEXT NOT NULL,
    motivo TEXT NOT NULL,
    responsable_decision INTEGER NOT NULL,
    version_metodologia TEXT NOT NULL,
    factors TEXT,
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conocimiento_capacidad (    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER REFERENCES personas(id),
    organizacion_id INTEGER REFERENCES organizaciones(id),
    area TEXT NOT NULL,
    anos_experiencia INTEGER,
    descripcion TEXT,
    estado TEXT NOT NULL DEFAULT 'disponible',
    fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (persona_id IS NOT NULL OR organizacion_id IS NOT NULL),
    CHECK (estado IN ('disponible','ocupado'))
);

CREATE TABLE IF NOT EXISTS recursos_aporte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    duenio_id INTEGER NOT NULL,
    duenio_tipo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    disponibilidad TEXT NOT NULL DEFAULT 'disponible',
    condiciones_uso TEXT,
    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (duenio_tipo IN ('persona','organizacion')),
    CHECK (tipo IN ('tiempo','conocimiento','materiales','herramientas','informacion','otros')),
    CHECK (disponibilidad IN ('disponible','reservado','usado'))
);

CREATE TABLE IF NOT EXISTS eventos_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entidad_referencia TEXT NOT NULL,
    entidad_id INTEGER NOT NULL,
    tipo_evento TEXT NOT NULL,
    usuario_o_sistema TEXT,
    dato_anterior TEXT,
    dato_nuevo TEXT,
    justificacion TEXT,
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS procedencia_datos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fuente TEXT NOT NULL,
    fecha_fuente TEXT NOT NULL,
    formato TEXT NOT NULL,
    calidad_reportada TEXT NOT NULL DEFAULT 'desconocida',
    supuestos TEXT,
    transformaciones TEXT,
    responsable INTEGER
);

CREATE INDEX IF NOT EXISTS idx_necesidades_organizacion ON necesidades(organizacion_id);
CREATE INDEX IF NOT EXISTS idx_necesidades_visibilidad ON necesidades(visibilidad);
CREATE INDEX IF NOT EXISTS idx_problemas_estado ON problemas_colectivos(estado);
CREATE INDEX IF NOT EXISTS idx_problemas_organizacion ON problemas_colectivos(organizacion_id);
CREATE INDEX IF NOT EXISTS idx_eventos_entidad ON eventos_auditoria(entidad_referencia, entidad_id);
CREATE INDEX IF NOT EXISTS idx_iniciativas_problema ON iniciativas(problema_colectivo_id);