"""Modelos SQLAlchemy de Trama Abierta MVP v0.6.

Integridad:
- Relaciones N:M con claves foráneas y claves primarias compuestas
  (sin duplicados por construcción).
- `ProblemaColectivo` exige un propietario (organización o persona).
- `Necesidad.visibilidad` controla qué necesidades pueden asociarse y
  exponerse en problemas colectivos.

Riesgo documentado: `Necesidad.responsable_id` y `RecursoAporte.duenio_id`
son referencias polimórficas sin FK. Ver `docs/riesgos_pendientes.md`.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _utcnow() -> datetime:
    """UTC naive para columnas DateTime portables (SQLite/PostgreSQL)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# --- N:M entre Necesidad y ProblemaColectivo ---
necesidad_problema_colectivo = Table(
    "necesidad_problema_colectivo",
    Base.metadata,
    Column(
        "necesidad_id",
        Integer,
        ForeignKey("necesidades.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "problema_colectivo_id",
        Integer,
        ForeignKey("problemas_colectivos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# --- N:M de participantes (personas y organizaciones) ---
problema_participantes_persona = Table(
    "problema_participantes_persona",
    Base.metadata,
    Column(
        "problema_colectivo_id",
        Integer,
        ForeignKey("problemas_colectivos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "persona_id",
        Integer,
        ForeignKey("personas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

problema_participantes_organizacion = Table(
    "problema_participantes_organizacion",
    Base.metadata,
    Column(
        "problema_colectivo_id",
        Integer,
        ForeignKey("problemas_colectivos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "organizacion_id",
        Integer,
        ForeignKey("organizaciones.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# === Organización ===
class Organizacion(Base):
    __tablename__ = "organizaciones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)
    tipo_organizacion = Column(String(100), nullable=False)
    contacto_publico = Column(String(200), nullable=False)
    datos_sensibles_separados = Column(Text, nullable=True)
    estado = Column(String(20), default="activa", nullable=False)
    fecha_creacion = Column(DateTime, default=_utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=_utcnow, onupdate=datetime.utcnow, nullable=False
    )

    usuarios = relationship(
        "OperationalUser", back_populates="organizacion", cascade="all, delete-orphan"
    )
    necesidades = relationship("Necesidad", back_populates="organizacion")
    recursos = relationship(
        "Recurso", back_populates="organizacion", cascade="all, delete-orphan"
    )


# === Usuario operativo (autenticación / backoffice) ===
class OperationalUser(Base):
    __tablename__ = "operational_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(200), nullable=False)
    rol = Column(String(50), default="miembro", nullable=False)
    organizacion_id = Column(
        Integer, ForeignKey("organizaciones.id"), nullable=False
    )
    activo = Column(Integer, default=1, nullable=False)
    fecha_creacion = Column(DateTime, default=_utcnow, nullable=False)

    organizacion = relationship("Organizacion", back_populates="usuarios")


# === Persona ===
class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(254), unique=True, nullable=True)
    # Texto libre (lista separada por comas). No es PII por sí mismo, pero
    # no se expone en DTOs públicos de problemas colectivos.
    # Auth independiente: permite registro y autenticación sin organización.
    hashed_password = Column(String(255), nullable=True)
    rol = Column(String(50), default="individuo", nullable=False)
    activo = Column(Integer, default=1, nullable=False)
    habilidades = Column(Text, nullable=True)
    preferencias_participacion = Column(String(500), nullable=True)
    estado = Column(String(20), default="activa", nullable=False)
    fecha_creacion = Column(DateTime, default=_utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=_utcnow, onupdate=datetime.utcnow, nullable=False
    )

    conocimientos = relationship(
        "ConocimientoCapacidad",
        back_populates="persona",
        cascade="all, delete-orphan",
    )


# === Necesidad ===
class Necesidad(Base):
    __tablename__ = "necesidades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, default="", nullable=False)
    poblacion_afectada = Column(String(500), nullable=True)
    estado = Column(String(20), default="propuesta", nullable=False)
    visibilidad = Column(String(20), default="privada", nullable=False)
    criterios_exito = Column(Text, nullable=True)
    # Referencia polimórfica (persona u organización) sin FK. Riesgo documentado.
    responsable_id = Column(Integer, nullable=True)
    responsable_tipo = Column(String(20), nullable=True)
    fecha_creacion = Column(DateTime, default=_utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=_utcnow, onupdate=datetime.utcnow, nullable=False
    )

    organizacion = relationship("Organizacion", back_populates="necesidades")
    persona = relationship("Persona", foreign_keys=[persona_id])
    iniciativas = relationship("Iniciativa", back_populates="necesidad")
    recursos = relationship("Recurso", back_populates="necesidad")
    problemas_colectivos = relationship(
        "ProblemaColectivo",
        secondary=necesidad_problema_colectivo,
        back_populates="necesidades_asociadas",
    )

    __table_args__ = (
        CheckConstraint(
            "visibilidad IN ('privada','compartible','publica')",
            name="ck_necesidad_visibilidad",
        ),
        CheckConstraint(
            "estado IN ('propuesta','en_evaluacion','en_ejecucion','resuelto','cerrado')",
            name="ck_necesidad_estado",
        ),
    )


# === Recurso (organización) ===
class Recurso(Base):
    __tablename__ = "recursos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_recurso = Column(String(50), nullable=False)
    nombre = Column(String(200), nullable=False)
    organizacion_id = Column(
        Integer, ForeignKey("organizaciones.id"), nullable=False
    )
    necesidad_id = Column(Integer, ForeignKey("necesidades.id"), nullable=True)
    disponibilidad = Column(String(20), default="disponible", nullable=False)
    restricciones = Column(String(500), nullable=True)
    licencia_utilizacion = Column(String(200), nullable=False)
    fecha_creacion = Column(DateTime, default=_utcnow, nullable=False)

    organizacion = relationship("Organizacion", back_populates="recursos")
    necesidad = relationship("Necesidad", back_populates="recursos")


# === Problema colectivo ===
class ProblemaColectivo(Base):
    __tablename__ = "problemas_colectivos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(2000), nullable=False)
    evidencias = Column(Text, nullable=True)
    estado = Column(String(20), default="detectado", nullable=False)
    origen_datos = Column(String(30), default="synthetic_pilot", nullable=False)

    # Propietario: organización o persona. Exactamente uno debe existir.
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    creado_por_id = Column(
        Integer, ForeignKey("operational_users.id", ondelete="SET NULL"), nullable=True
    )

    fecha_deteccion = Column(DateTime, default=_utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=_utcnow, onupdate=datetime.utcnow, nullable=False
    )

    organizacion = relationship(
        "Organizacion", foreign_keys=[organizacion_id], backref="problemas_creados"
    )
    persona = relationship(
        "Persona", foreign_keys=[persona_id], backref="problemas_creados"
    )
    necesidades_asociadas = relationship(
        "Necesidad",
        secondary=necesidad_problema_colectivo,
        back_populates="problemas_colectivos",
    )
    personas_participantes = relationship(
        "Persona", secondary=problema_participantes_persona, lazy="selectin"
    )
    organizaciones_participantes = relationship(
        "Organizacion",
        secondary=problema_participantes_organizacion,
        lazy="selectin",
    )
    iniciativas = relationship("Iniciativa", back_populates="problema_colectivo")

    __table_args__ = (
        CheckConstraint(
            "estado IN ('detectado','en_analisis','validado','cerrado')",
            name="ck_problema_colectivo_estado",
        ),
        CheckConstraint(
            "origen_datos IN ('synthetic_pilot','real_pilot')",
            name="ck_problema_colectivo_origen",
        ),
        CheckConstraint(
            "organizacion_id IS NOT NULL OR persona_id IS NOT NULL",
            name="ck_problema_colectivo_propietario",
        ),
        Index("idx_problemas_estado", "estado"),
        Index("idx_problemas_organizacion", "organizacion_id"),
    )


# === Iniciativa ===
class Iniciativa(Base):
    __tablename__ = "iniciativas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    problema_colectivo_id = Column(
        Integer, ForeignKey("problemas_colectivos.id"), nullable=True
    )
    responsable_id = Column(Integer, nullable=True)
    responsable_tipo = Column(String(20), nullable=True)
    necesidad_id = Column(Integer, ForeignKey("necesidades.id"), nullable=True)
    titulo = Column(String(200), nullable=True)
    descripcion = Column(Text, default="", nullable=True)
    alternativas_evaluadas = Column(Text, nullable=True)
    criterios_decision = Column(Text, nullable=False)
    presupuesto_estimate = Column(Float, nullable=True)
    plazo = Column(String(20), nullable=True)
    estado = Column(String(20), default="propuesta", nullable=False)
    fecha_creacion = Column(DateTime, default=_utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=_utcnow, onupdate=datetime.utcnow, nullable=False
    )

    necesidad = relationship("Necesidad", back_populates="iniciativas")
    problema_colectivo = relationship(
        "ProblemaColectivo", back_populates="iniciativas"
    )


# === Decisión ===
class Decision(Base):
    __tablename__ = "decisiones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    iniciativa_id = Column(
        Integer, ForeignKey("iniciativas.id"), nullable=False
    )
    tipo_decision = Column(String(100), nullable=False)
    alternativa_elegida = Column(String(2000), nullable=False)
    motivo = Column(Text, nullable=False)
    responsable_decision = Column(Integer, nullable=False)
    version_metodologia = Column(String(100), nullable=False)
    factors = Column(Text, nullable=True)
    fecha = Column(DateTime, default=_utcnow, nullable=False)

    iniciativa = relationship("Iniciativa", backref="decisiones")


# === Conocimiento o capacidad ===
class ConocimientoCapacidad(Base):
    __tablename__ = "conocimiento_capacidad"
    id = Column(Integer, primary_key=True, autoincrement=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)
    area = Column(String(200), nullable=False)
    anos_experiencia = Column(Integer, nullable=True)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(20), default="disponible", nullable=False)
    fecha_registro = Column(DateTime, default=_utcnow, nullable=False)

    persona = relationship("Persona", back_populates="conocimientos")
    organizacion = relationship(
        "Organizacion", foreign_keys=[organizacion_id], backref="conocimientos"
    )

    __table_args__ = (
        CheckConstraint(
            "persona_id IS NOT NULL OR organizacion_id IS NOT NULL",
            name="ck_conocimiento_propietario",
        ),
    )


# === Recurso o aporte (persona u organización) ===
class RecursoAporte(Base):
    __tablename__ = "recursos_aporte"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(20), nullable=False)
    # Referencia polimórfica sin FK (riesgo documentado).
    duenio_id = Column(Integer, nullable=False)
    duenio_tipo = Column(String(20), nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    disponibilidad = Column(String(20), default="disponible", nullable=False)
    condiciones_uso = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=_utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "duenio_tipo IN ('persona','organizacion')",
            name="ck_recurso_aporte_duenio_tipo",
        ),
        CheckConstraint(
            "tipo IN ('tiempo','conocimiento','materiales','herramientas','informacion','otros')",
            name="ck_recurso_aporte_tipo",
        ),
    )


# === Evento de auditoría ===
class EventoAuditoria(Base):
    __tablename__ = "eventos_auditoria"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entidad_referencia = Column(String(100), nullable=False)
    entidad_id = Column(Integer, nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    usuario_o_sistema = Column(String(200), nullable=True)
    dato_anterior = Column(Text, nullable=True)
    dato_nuevo = Column(Text, nullable=True)
    justificacion = Column(String(500), nullable=True)
    fecha = Column(DateTime, default=_utcnow, nullable=False)

    __table_args__ = (
        Index("idx_eventos_entidad", "entidad_referencia", "entidad_id"),
    )


# === Procedencia de datos ===
class ProcedenciaDatos(Base):
    __tablename__ = "procedencia_datos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fuente = Column(String(200), nullable=False)
    fecha_fuente = Column(DateTime, nullable=False)
    formato = Column(String(50), nullable=False)
    calidad_reportada = Column(String(50), default="desconocida", nullable=False)
    supuestos = Column(Text, nullable=True)
    transformaciones = Column(Text, nullable=True)
    responsable = Column(Integer, nullable=True)