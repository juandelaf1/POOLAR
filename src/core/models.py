from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Table,
    CheckConstraint,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from sqlalchemy.orm import declarative_base

Base = declarative_base()


# --- Enums ---
class EstadoInvitacion(str, enum.Enum):
    pendiente = "pendiente"
    aceptada = "aceptada"
    rechazada = "rechazada"
    retirada = "retirada"
    caducada = "caducada"


# --- Tablas N:M ---
problema_participantes_persona = Table(
    "problema_participantes_persona",
    Base.metadata,
    Column("problema_colectivo_id", Integer, ForeignKey("problemas_colectivos.id"), primary_key=True),
    Column("persona_id", Integer, ForeignKey("personas.id"), primary_key=True),
    Column("fecha_incorporacion", DateTime, server_default=func.now()),
)

problema_participantes_organizacion = Table(
    "problema_participantes_organizacion",
    Base.metadata,
    Column("problema_colectivo_id", Integer, ForeignKey("problemas_colectivos.id"), primary_key=True),
    Column("organizacion_id", Integer, ForeignKey("organizaciones.id"), primary_key=True),
    Column("fecha_incorporacion", DateTime, server_default=func.now()),
)

necesidad_problema_colectivo = Table(
    "necesidad_problema_colectivo",
    Base.metadata,
    Column("necesidad_id", Integer, ForeignKey("necesidades.id"), primary_key=True),
    Column("problema_colectivo_id", Integer, ForeignKey("problemas_colectivos.id"), primary_key=True),
)


# --- Entidades ---
class Organizacion(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)
    tipo_organizacion = Column(String(100), nullable=False)
    contacto_publico = Column(String(200), nullable=False)
    datos_sensibles_separados = Column(Text, nullable=True)
    estado = Column(String(20), default="activa")
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(254), nullable=True, unique=True)
    hashed_password = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    rol = Column(String(50), default="individuo")
    habilidades = Column(Text, nullable=True)
    preferencias_participacion = Column(Text, nullable=True)
    estado = Column(String(20), default="activa")
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    problemas_participados = relationship(
        "ProblemaColectivo", secondary=problema_participantes_persona, back_populates="personas_participantes"
    )
    conocimientos = relationship("ConocimientoCapacidad", back_populates="persona", cascade="all, delete-orphan")


class OperationalUser(Base):
    __tablename__ = "operational_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(254), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(200), nullable=False)
    rol = Column(String(50), default="miembro")
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, server_default=func.now())

    organizacion = relationship("Organizacion", foreign_keys=[organizacion_id])


class Necesidad(Base):
    __tablename__ = "necesidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, default="")
    poblacion_afectada = Column(Text, nullable=True)
    estado = Column(String(50), default="propuesta")
    visibilidad = Column(String(20), default="privada")
    criterios_exito = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organizacion = relationship("Organizacion", foreign_keys=[organizacion_id])
    persona = relationship("Persona")

    __table_args__ = (
        CheckConstraint(
            "organizacion_id IS NOT NULL OR persona_id IS NOT NULL",
            name="ck_necesidad_propietario",
        ),
    )


class ProblemaColectivo(Base):
    __tablename__ = "problemas_colectivos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(Text, nullable=False)
    evidencias = Column(Text, nullable=True)
    estado = Column(String(20), default="detectado")
    origen_datos = Column(String(20), nullable=False)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    creado_por_id = Column(Integer, nullable=False)
    fecha_deteccion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    necesidades_asociadas = relationship("Necesidad", secondary=necesidad_problema_colectivo, lazy="selectin")
    personas_participantes = relationship("Persona", secondary=problema_participantes_persona, back_populates="problemas_participados", lazy="selectin")
    organizaciones_participantes = relationship("Organizacion", secondary=problema_participantes_organizacion, lazy="selectin")
    invitaciones = relationship("Invitacion", back_populates="problema", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "organizacion_id IS NOT NULL OR persona_id IS NOT NULL",
            name="ck_problema_colectivo_propietario",
        ),
    )


class Invitacion(Base):
    __tablename__ = "invitaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    problema_colectivo_id = Column(Integer, ForeignKey("problemas_colectivos.id"), nullable=False)
    emisor_id = Column(Integer, nullable=False)
    emisor_tipo = Column(String(20), nullable=False)  # individuo u organizacion
    destinatario_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    estado = Column(String(20), default="pendiente")
    mensaje = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_respuesta = Column(DateTime, nullable=True)
    fecha_retirada = Column(DateTime, nullable=True)

    problema = relationship("ProblemaColectivo", back_populates="invitaciones")
    destinatario = relationship("Persona")

    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'aceptada', 'rechazada', 'retirada', 'caducada')",
            name="ck_invitacion_estado",
        ),
    )


class ConocimientoCapacidad(Base):
    __tablename__ = "conocimiento_capacidad"

    id = Column(Integer, primary_key=True, autoincrement=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)
    area = Column(String(200), nullable=False)
    anos_experiencia = Column(Integer, nullable=True)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(20), default="disponible")
    fecha_registro = Column(DateTime, server_default=func.now())

    persona = relationship("Persona", back_populates="conocimientos")
    organizacion = relationship("Organizacion", foreign_keys=[organizacion_id])

    __table_args__ = (
        CheckConstraint(
            "persona_id IS NOT NULL OR organizacion_id IS NOT NULL",
            name="ck_conocimiento_propietario",
        ),
    )


class RecursoAporte(Base):
    __tablename__ = "recursos_aportes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50), nullable=False)
    duenio_id = Column(Integer, nullable=False)
    duenio_tipo = Column(String(20), nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    disponibilidad = Column(String(20), default="disponible")
    condiciones_uso = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, server_default=func.now())


class Iniciativa(Base):
    __tablename__ = "iniciativas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    necesidad_id = Column(Integer, ForeignKey("necesidades.id"), nullable=True)
    problema_colectivo_id = Column(Integer, ForeignKey("problemas_colectivos.id"), nullable=True)
    responsable_id = Column(Integer, nullable=True)
    responsable_tipo = Column(String(20), nullable=True)
    titulo = Column(String(200), nullable=True)
    descripcion = Column(Text, default="")
    alternativas_evaluadas = Column(Text, nullable=True)
    criterios_decision = Column(Text, nullable=False)
    presupuesto_estimate = Column(Integer, nullable=True)
    plazo = Column(String(20), nullable=True)
    estado = Column(String(20), default="propuesta")
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    necesidad = relationship("Necesidad")
    problema_colectivo = relationship("ProblemaColectivo")


class Decision(Base):
    __tablename__ = "decisiones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iniciativa_id = Column(Integer, ForeignKey("iniciativas.id"), nullable=False)
    tipo_decision = Column(String(50), nullable=False)
    alternativa_elegida = Column(String(200), nullable=False)
    motivo = Column(Text, nullable=False)
    responsable_decision = Column(Integer, nullable=False)
    version_metodologia = Column(String(50), nullable=False)
    factors = Column(Text, nullable=True)
    fecha = Column(DateTime, server_default=func.now())

    iniciativa = relationship("Iniciativa")


class ApprovalRequest(Base):
    """Solicitud de aprobación persistida en base de datos."""
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    approval_id = Column(String(100), nullable=False, unique=True, index=True)
    execution_id = Column(String(200), nullable=False, index=True)
    tool_name = Column(String(200), nullable=False)
    inputs = Column(Text, nullable=False, default="{}")
    proposed_by = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="pendiente")
    reason = Column(Text, nullable=True)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_by = Column(Integer, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class EventoAuditoria(Base):
    __tablename__ = "eventos_auditoria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entidad_referencia = Column(String(100), nullable=False)
    entidad_id = Column(Integer, nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    usuario_o_sistema = Column(String(200), nullable=True)
    justificacion = Column(Text, nullable=True)
    dato_anterior = Column(Text, nullable=True)
    dato_nuevo = Column(Text, nullable=True)
    fecha = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("entidad_id > 0", name="ck_evento_entidad_id"),
    )


class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_recurso = Column(String(50), nullable=False)
    nombre = Column(String(200), nullable=False)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)
    disponibilidad = Column(String(20), default="disponible")
    restricciones = Column(Text, nullable=True)
    licencia_utilizacion = Column(String(50), default="CC-BY")
    necesidad_id = Column(Integer, ForeignKey("necesidades.id"), nullable=True)
    fecha_creacion = Column(DateTime, server_default=func.now())

    organizacion = relationship("Organizacion", foreign_keys=[organizacion_id])
    necesidad = relationship("Necesidad")