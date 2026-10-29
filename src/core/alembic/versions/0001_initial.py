"""Initial schema with all Trama Abierta entities."""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Organizaciones
    op.create_table(
        "organizaciones",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("tipo_organizacion", sa.String(100), nullable=False),
        sa.Column("contacto_publico", sa.String(200), nullable=False),
        sa.Column("datos_sensibles_separados", sa.Text, nullable=True),
        sa.Column("estado", sa.String(20), default="activa"),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # Personas
    op.create_table(
        "personas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("email", sa.String(254), nullable=True, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("activo", sa.Boolean, default=True),
        sa.Column("rol", sa.String(50), default="individuo"),
        sa.Column("habilidades", sa.Text, nullable=True),
        sa.Column("preferencias_participacion", sa.Text, nullable=True),
        sa.Column("estado", sa.String(20), default="activa"),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # Operational users
    op.create_table(
        "operational_users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("rol", sa.String(50), default="miembro"),
        sa.Column("organizacion_id", sa.Integer, sa.ForeignKey("organizaciones.id"), nullable=False),
        sa.Column("activo", sa.Boolean, default=True),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
    )
    # Necesidades
    op.create_table(
        "necesidades",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organizacion_id", sa.Integer, sa.ForeignKey("organizaciones.id"), nullable=True),
        sa.Column("persona_id", sa.Integer, sa.ForeignKey("personas.id"), nullable=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text, default=""),
        sa.Column("poblacion_afectada", sa.Text, nullable=True),
        sa.Column("estado", sa.String(50), default="propuesta"),
        sa.Column("visibilidad", sa.String(20), default="privada"),
        sa.Column("criterios_exito", sa.Text, nullable=True),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_check_constraint(
        "ck_necesidad_propietario",
        "necesidades",
        "organizacion_id IS NOT NULL OR persona_id IS NOT NULL",
    )
    # Conocimiento/capacidad
    op.create_table(
        "conocimiento_capacidad",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("persona_id", sa.Integer, sa.ForeignKey("personas.id"), nullable=True),
        sa.Column("organizacion_id", sa.Integer, sa.ForeignKey("organizaciones.id"), nullable=True),
        sa.Column("area", sa.String(200), nullable=False),
        sa.Column("anos_experiencia", sa.Integer, nullable=True),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("estado", sa.String(20), default="disponible"),
        sa.Column("fecha_registro", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_check_constraint(
        "ck_conocimiento_propietario",
        "conocimiento_capacidad",
        "persona_id IS NOT NULL OR organizacion_id IS NOT NULL",
    )
    # Recursos/aportes
    op.create_table(
        "recursos_aportes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("duenio_id", sa.Integer, nullable=False),
        sa.Column("duenio_tipo", sa.String(20), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("disponibilidad", sa.String(20), default="disponible"),
        sa.Column("condiciones_uso", sa.Text, nullable=True),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
    )
    # Problemas colectivos
    op.create_table(
        "problemas_colectivos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("descripcion", sa.Text, nullable=False),
        sa.Column("evidencias", sa.Text, nullable=True),
        sa.Column("estado", sa.String(20), default="detectado"),
        sa.Column("origen_datos", sa.String(20), nullable=False),
        sa.Column("organizacion_id", sa.Integer, sa.ForeignKey("organizaciones.id"), nullable=True),
        sa.Column("persona_id", sa.Integer, sa.ForeignKey("personas.id"), nullable=True),
        sa.Column("creado_por_id", sa.Integer, nullable=False),
        sa.Column("fecha_deteccion", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_check_constraint(
        "ck_problema_colectivo_propietario",
        "problemas_colectivos",
        "organizacion_id IS NOT NULL OR persona_id IS NOT NULL",
    )
    # Invitaciones
    op.create_table(
        "invitaciones",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("problema_colectivo_id", sa.Integer, sa.ForeignKey("problemas_colectivos.id"), nullable=False),
        sa.Column("emisor_id", sa.Integer, nullable=False),
        sa.Column("emisor_tipo", sa.String(20), nullable=False),
        sa.Column("destinatario_id", sa.Integer, sa.ForeignKey("personas.id"), nullable=False),
        sa.Column("estado", sa.String(20), default="pendiente"),
        sa.Column("mensaje", sa.Text, nullable=True),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_respuesta", sa.DateTime, nullable=True),
        sa.Column("fecha_retirada", sa.DateTime, nullable=True),
    )
    op.create_check_constraint(
        "ck_invitacion_estado",
        "invitaciones",
        "estado IN ('pendiente', 'aceptada', 'rechazada', 'retirada', 'caducada')",
    )
    # Iniciativas
    op.create_table(
        "iniciativas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("necesidad_id", sa.Integer, sa.ForeignKey("necesidades.id"), nullable=True),
        sa.Column("problema_colectivo_id", sa.Integer, sa.ForeignKey("problemas_colectivos.id"), nullable=True),
        sa.Column("responsable_id", sa.Integer, nullable=True),
        sa.Column("responsable_tipo", sa.String(20), nullable=True),
        sa.Column("titulo", sa.String(200), nullable=True),
        sa.Column("descripcion", sa.Text, default=""),
        sa.Column("alternativas_evaluadas", sa.Text, nullable=True),
        sa.Column("criterios_decision", sa.Text, nullable=False),
        sa.Column("presupuesto_estimate", sa.Integer, nullable=True),
        sa.Column("plazo", sa.String(20), nullable=True),
        sa.Column("estado", sa.String(20), default="propuesta"),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # Decisiones
    op.create_table(
        "decisiones",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("iniciativa_id", sa.Integer, sa.ForeignKey("iniciativas.id"), nullable=False),
        sa.Column("tipo_decision", sa.String(50), nullable=False),
        sa.Column("alternativa_elegida", sa.String(200), nullable=False),
        sa.Column("motivo", sa.Text, nullable=False),
        sa.Column("responsable_decision", sa.Integer, nullable=False),
        sa.Column("version_metodologia", sa.String(50), nullable=False),
        sa.Column("factors", sa.Text, nullable=True),
        sa.Column("fecha", sa.DateTime, server_default=sa.func.now()),
    )
    # Eventos de auditoría
    op.create_table(
        "eventos_auditoria",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("entidad_referencia", sa.String(100), nullable=False),
        sa.Column("entidad_id", sa.Integer, nullable=False),
        sa.Column("tipo_evento", sa.String(50), nullable=False),
        sa.Column("usuario_o_sistema", sa.String(200), nullable=True),
        sa.Column("justificacion", sa.Text, nullable=True),
        sa.Column("dato_anterior", sa.Text, nullable=True),
        sa.Column("dato_nuevo", sa.Text, nullable=True),
        sa.Column("fecha", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_check_constraint(
        "ck_evento_entidad_id",
        "eventos_auditoria",
        "entidad_id > 0",
    )
    # Recursos
    op.create_table(
        "recursos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tipo_recurso", sa.String(50), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("organizacion_id", sa.Integer, sa.ForeignKey("organizaciones.id"), nullable=True),
        sa.Column("disponibilidad", sa.String(20), default="disponible"),
        sa.Column("restricciones", sa.Text, nullable=True),
        sa.Column("licencia_utilizacion", sa.String(50), default="CC-BY"),
        sa.Column("necesidad_id", sa.Integer, sa.ForeignKey("necesidades.id"), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
    )
    # Tablas N:M
    op.create_table(
        "necesidad_problema_colectivo",
        sa.Column("necesidad_id", sa.Integer, sa.ForeignKey("necesidades.id"), primary_key=True),
        sa.Column("problema_colectivo_id", sa.Integer, sa.ForeignKey("problemas_colectivos.id"), primary_key=True),
    )
    op.create_table(
        "problema_participantes_persona",
        sa.Column("problema_colectivo_id", sa.Integer, sa.ForeignKey("problemas_colectivos.id"), primary_key=True),
        sa.Column("persona_id", sa.Integer, sa.ForeignKey("personas.id"), primary_key=True),
        sa.Column("fecha_incorporacion", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        "problema_participantes_organizacion",
        sa.Column("problema_colectivo_id", sa.Integer, sa.ForeignKey("problemas_colectivos.id"), primary_key=True),
        sa.Column("organizacion_id", sa.Integer, sa.ForeignKey("organizaciones.id"), primary_key=True),
        sa.Column("fecha_incorporacion", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("problema_participantes_organizacion")
    op.drop_table("problema_participantes_persona")
    op.drop_table("necesidad_problema_colectivo")
    op.drop_table("recursos")
    op.drop_table("eventos_auditoria")
    op.drop_table("decisiones")
    op.drop_table("iniciativas")
    op.drop_table("invitaciones")
    op.drop_table("problemas_colectivos")
    op.drop_table("recursos_aportes")
    op.drop_table("conocimiento_capacidad")
    op.drop_table("necesidades")
    op.drop_table("operational_users")
    op.drop_table("personas")
    op.drop_table("organizaciones")