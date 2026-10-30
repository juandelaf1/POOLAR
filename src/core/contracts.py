"""Contratos versionados de Poolar MVP v0.6.

Entidades de dominio y DTOs de API. Los DTOs públicos no incluyen datos
personales (email, contacto, DNI) ni campos internos de autenticación.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Procedencia de datos ---
class OrigenDatos(str, Enum):
    """Etiqueta explícita del origen de los datos.

    El piloto solo admite datos sintéticos hasta que exista un proceso
    documentado de consentimiento para datos reales.
    """

    synthetic_pilot = "synthetic_pilot"
    real_pilot = "real_pilot"


class ProcedenciaDatos(BaseModel):
    id: int
    fuente: str = Field(min_length=2)
    fecha_fuente: datetime
    formato: str = Field(min_length=1)
    calidad_reportada: str = Field(default="desconocida")
    supuestos: Optional[str] = Field(default=None, max_length=500)
    transformaciones: Optional[str] = Field(default=None, max_length=500)
    responsable: Optional[int] = Field(default=None, gt=0)


# --- Persona ---
class PersonaEstado(str, Enum):
    activa = "activa"
    inactiva = "inactiva"


class Persona(BaseModel):
    id: int
    nombre: str = Field(min_length=1, max_length=200)
    email: Optional[str] = Field(default=None, max_length=254)
    habilidades: Optional[List[str]] = None
    preferencias_participacion: Optional[str] = Field(default=None, max_length=500)
    estado: PersonaEstado = PersonaEstado.activa
    fecha_creacion: datetime
    fecha_actualizacion: datetime


# --- Organización ---
class OrganizacionEstado(str, Enum):
    activa = "activa"
    inactiva = "inactiva"


class Organizacion(BaseModel):
    id: int
    nombre: str = Field(min_length=2, max_length=200)
    tipo_organizacion: str = Field(min_length=1, max_length=100)
    contacto_publico: str = Field(min_length=3, max_length=200)
    datos_sensibles_separados: Optional[str] = Field(default=None, max_length=1000)
    estado: OrganizacionEstado = OrganizacionEstado.activa
    fecha_creacion: datetime
    fecha_actualizacion: datetime


# --- Necesidad ---
class NecesidadEstado(str, Enum):
    propuesta = "propuesta"
    en_evaluacion = "en_evaluacion"
    en_ejecucion = "en_ejecucion"
    resuelto = "resuelto"
    cerrado = "cerrado"


class NecesidadVisibilidad(str, Enum):
    """Visibilidad de una necesidad.

    - privada: solo su organización/persona propietaria y operadores autorizados.
    - compartible: puede asociarse a problemas colectivos y verse en ellos.
    - publica: además puede exponerse en listados/exportaciones sin PII.
    """

    privada = "privada"
    compartible = "compartible"
    publica = "publica"


class Necesidad(BaseModel):
    id: int
    organizacion_id: Optional[int] = Field(default=None, gt=0)
    persona_id: Optional[int] = Field(default=None, gt=0)
    titulo: str = Field(min_length=3, max_length=200)
    descripcion: str = Field(default="", max_length=1000)
    poblacion_afectada: Optional[str] = Field(default=None, max_length=500)
    estado: NecesidadEstado = NecesidadEstado.propuesta
    visibilidad: NecesidadVisibilidad = NecesidadVisibilidad.privada
    criterios_exito: Optional[str] = Field(default=None, max_length=1000)
    fecha_creacion: datetime
    fecha_actualizacion: datetime


# --- Problema colectivo ---
class ProblemaColectivoEstado(str, Enum):
    detectado = "detectado"
    en_analisis = "en_analisis"
    validado = "validado"
    cerrado = "cerrado"


# Transiciones explícitas del ciclo de vida. No se permite saltar de
# `detectado` a `validado` sin pasar por `en_analisis` y sin evidencias.
TRANSICIONES_PROBLEMA_COLECTIVO = {
    ProblemaColectivoEstado.detectado: {
        ProblemaColectivoEstado.en_analisis,
        ProblemaColectivoEstado.cerrado,
    },
    ProblemaColectivoEstado.en_analisis: {
        ProblemaColectivoEstado.validado,
        ProblemaColectivoEstado.cerrado,
    },
    ProblemaColectivoEstado.validado: {ProblemaColectivoEstado.cerrado},
    ProblemaColectivoEstado.cerrado: set(),
}


class ProblemaColectivoCreate(BaseModel):
    """DTO de creación. `estado` no se acepta: lo fija el servidor."""

    model_config = ConfigDict(extra="forbid")

    descripcion: str = Field(min_length=10, max_length=2000)
    evidencias: Optional[str] = Field(default=None, max_length=2000)
    necesidades_asociadas: List[int] = Field(default_factory=list, max_length=500)
    personas_participantes: List[int] = Field(default_factory=list, max_length=500)
    organizaciones_participantes: List[int] = Field(default_factory=list, max_length=500)
    origen_datos: OrigenDatos = OrigenDatos.synthetic_pilot

    @field_validator(
        "necesidades_asociadas",
        "personas_participantes",
        "organizaciones_participantes",
    )
    @classmethod
    def ids_positivos_sin_duplicados(cls, values: List[int]) -> List[int]:
        if any(value <= 0 for value in values):
            raise ValueError("Los identificadores deben ser positivos")
        # Elimina duplicados conservando el orden.
        return list(dict.fromkeys(values))


class ProblemaColectivoEstadoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: ProblemaColectivoEstado
    justificacion: Optional[str] = Field(default=None, max_length=500)


class ProblemaColectivoResponse(BaseModel):
    """DTO público: sin datos personales ni secretos."""

    id: int
    descripcion: str
    estado: ProblemaColectivoEstado
    necesidades_asociadas: List[int] = Field(default_factory=list)
    necesidades_ocultas: int = 0
    personas_participantes: List[int] = Field(default_factory=list)
    organizaciones_participantes: List[int] = Field(default_factory=list)
    evidencias: Optional[str] = None
    origen_datos: OrigenDatos
    fecha_deteccion: datetime
    fecha_actualizacion: datetime


# --- Conocimiento o capacidad ---
class ConocimientoCapacidadEstado(str, Enum):
    disponible = "disponible"
    ocupado = "ocupado"


class ConocimientoCapacidad(BaseModel):
    id: int
    persona_id: Optional[int] = Field(default=None, gt=0)
    organizacion_id: Optional[int] = Field(default=None, gt=0)
    area: str = Field(min_length=1, max_length=200)
    anos_experiencia: Optional[int] = Field(default=None, ge=0)
    descripcion: Optional[str] = Field(default=None, max_length=1000)
    estado: ConocimientoCapacidadEstado = ConocimientoCapacidadEstado.disponible
    fecha_registro: datetime


# --- Recurso o aporte ---
class RecursoAporteTipo(str, Enum):
    tiempo = "tiempo"
    conocimiento = "conocimiento"
    materiales = "materiales"
    herramientas = "herramientas"
    informacion = "informacion"
    otros = "otros"


class RecursoAporteDisponibilidad(str, Enum):
    disponible = "disponible"
    reservado = "reservado"
    usado = "usado"


class RecursoAporte(BaseModel):
    id: int
    tipo: RecursoAporteTipo
    duenio_id: int = Field(gt=0)
    duenio_tipo: str = Field(pattern="^(persona|organizacion)$")
    nombre: str = Field(min_length=1, max_length=200)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    disponibilidad: RecursoAporteDisponibilidad = RecursoAporteDisponibilidad.disponible
    condiciones_uso: Optional[str] = Field(default=None, max_length=500)
    fecha_creacion: datetime


# --- Iniciativa ---
class IniciativaEstado(str, Enum):
    propuesta = "propuesta"
    en_ejecucion = "en_ejecucion"
    finalizada = "finalizada"
    cerrada = "cerrada"


class Iniciativa(BaseModel):
    id: int
    problema_colectivo_id: Optional[int] = Field(default=None, gt=0)
    responsable_id: Optional[int] = Field(default=None, gt=0)
    responsable_tipo: Optional[str] = Field(default=None, pattern="^(persona|organizacion)$")
    titulo: str = Field(min_length=3, max_length=200)
    descripcion: str = Field(default="", max_length=1000)
    alternativas_evaluadas: Optional[str] = Field(default=None, max_length=2000)
    criterios_decision: str = Field(min_length=5)
    presupuesto_estimate: Optional[float] = Field(default=None, ge=0)
    plazo: Optional[str] = Field(default=None, max_length=20)
    estado: IniciativaEstado = IniciativaEstado.propuesta
    fecha_creacion: datetime
    fecha_actualizacion: datetime


# --- Decisión ---
class DecisionEstado(str, Enum):
    propuesta = "propuesta"
    aprobada = "aprobada"
    rechazada = "rechazada"
    pendiente = "pendiente"


class Decision(BaseModel):
    id: int
    iniciativa_id: int = Field(gt=0)
    tipo_decision: str = Field(min_length=1)
    alternativa_elegida: str = Field(min_length=2)
    motivo: str = Field(min_length=2)
    responsable_decision: int = Field(gt=0)
    version_metodologia: str = Field(min_length=1)
    factors: Optional[str] = Field(default=None, max_length=500)
    fecha: datetime


# --- Evento de auditoría ---
class EventoTipo(str, Enum):
    inicio = "inicio"
    hito = "hito"
    incidente = "incidente"
    resultado = "resultado"
    cambio_estado = "cambio_estado"
    exportacion = "exportacion"


class EventoAuditoria(BaseModel):
    id: int
    entidad_referencia: str = Field(min_length=2)
    entidad_id: int = Field(gt=0)
    tipo_evento: EventoTipo
    usuario_o_sistema: Optional[str] = Field(default=None, max_length=200)
    dato_anterior: Optional[str] = Field(default=None, max_length=1000)
    dato_nuevo: Optional[str] = Field(default=None, max_length=1000)
    justificacion: Optional[str] = Field(default=None, max_length=500)
    fecha: datetime