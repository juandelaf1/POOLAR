CREATE TABLE IF NOT EXISTS organizaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo_organizacion TEXT NOT NULL,
    contacto_publico TEXT NOT NULL,
    datos_sensibles_separados TEXT,
    estado TEXT DEFAULT 'activa',
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_organizaciones_nombre ON organizaciones(nombre);
