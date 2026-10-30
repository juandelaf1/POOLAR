"""Punto de entrada del API de Trama Abierta MVP v0.6.

Alcance: prototipo funcional, no producción. SQLite solo para desarrollo
controlado; PostgreSQL es la base objetivo.

Autenticación: JWT con `TRAMA_ABIERTA_SECRET_KEY` obligatoria de entorno.
Autorización: por organización/rol y por persona individual (`tipo` en token).
"""
import csv
import io
import os
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.core.auth import (
    Token,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.core.contracts import (
    EventoTipo,
    NecesidadVisibilidad,
    OrigenDatos,
    ProblemaColectivoCreate,
    ProblemaColectivoEstado,
    ProblemaColectivoEstadoUpdate,
    ProblemaColectivoResponse,
    TRANSICIONES_PROBLEMA_COLECTIVO,
)
from src.core.database import engine, get_db
from src.core.models import (
    Base,
    Decision,
    EventoAuditoria,
    Iniciativa,
    Invitacion,
    Necesidad,
    Organizacion,
    OperationalUser,
    Persona,
    ProblemaColectivo,
    Recurso,
    problema_participantes_organizacion,
    problema_participantes_persona,
)
from src.services.matching_service import matching_find_related_needs

# Solo desarrollo: en producción las tablas se crean con migraciones.
if os.getenv("DATABASE_URL", "").startswith("sqlite"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trama Abierta MVP", version="0.6.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.6.0"}


# ---------------------------------------------------------------------------
# Dependencias y utilidades de autorización
# ---------------------------------------------------------------------------
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    org_id = payload.get("organizacion_id")
    persona_id = payload.get("persona_id")
    if org_id is not None and persona_id is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ambiguo",
        )
    if org_id is not None:
        return {
            "tipo": "organizacion",
            "organizacion_id": org_id,
            "user_id": payload.get("user_id"),
            "rol": payload.get("rol", "miembro"),
            "persona_id": None,
        }
    if persona_id is not None:
        return {
            "tipo": "individuo",
            "organizacion_id": None,
            "user_id": payload.get("user_id"),
            "rol": payload.get("rol", "individuo"),
            "persona_id": persona_id,
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token sin contexto",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _get_org(db: Session, org_id: int) -> Organizacion:
    org = db.get(Organizacion, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    return org


def _need_accesible(need: Necesidad, user_ctx) -> bool:
    """Una necesidad es accesible si es propia o se marcó compartible/pública."""
    tipo = None
    if isinstance(user_ctx, dict):
        tipo = user_ctx.get("tipo")
        if tipo == "individuo":
            pid = user_ctx.get("persona_id")
            return need.persona_id == pid or need.visibilidad in ("compartible", "publica")
        org_id = user_ctx.get("organizacion_id")
    else:
        org_id = user_ctx
    return need.organizacion_id == org_id or need.visibilidad in ("compartible", "publica")


def _need_dto(need: Necesidad, org_id: int) -> dict:
    propia = need.organizacion_id == org_id
    return {
        "id": need.id,
        "titulo": need.titulo,
        "descripcion": need.descripcion,
        "estado": need.estado,
        "visibilidad": need.visibilidad,
        "organizacion_id": need.organizacion_id,
        # No se expone la persona propietaria a otras organizaciones.
        "persona_id": need.persona_id if propia else None,
        "propietario_tipo": (
            "persona" if need.persona_id is not None else "organizacion"
        ),
        "fecha_creacion": need.fecha_creacion,
    }


def _problema_visible(problema: ProblemaColectivo, user_ctx) -> bool:
    # Soporta contexto de organización (int/org_id) o dict (tipo/organizacion_id/persona_id)
    tipo = None
    if isinstance(user_ctx, dict):
        tipo = user_ctx.get("tipo")
        if tipo == "individuo":
            pid = user_ctx.get("persona_id")
            # Propietario individual o participante derivado
            if problema.persona_id == pid:
                return True
            if any(p.id == pid for p in problema.personas_participantes):
                return True
            # Si el problema pertenece a org pero persona derivada por necesidad
            return False
        org_id = user_ctx.get("organizacion_id")
    else:
        org_id = user_ctx
    if problema.organizacion_id == org_id:
        return True
    return any(org.id == org_id for org in problema.organizaciones_participantes)


def _problema_dto(problema: ProblemaColectivo, user_ctx) -> ProblemaColectivoResponse:
    # Asegurar contexto de acceso para necesidades asociadas
    tipo = None
    if isinstance(user_ctx, dict):
        tipo = user_ctx.get("tipo")
        if tipo == "individuo":
            org_id = user_ctx.get("organizacion_id")  # None
            persona_id = user_ctx.get("persona_id")
            def _need_accesible_individual(need):
                return need.persona_id == persona_id or need.visibilidad in ("compartible", "publica")
            visible_ids = [need.id for need in problema.necesidades_asociadas if _need_accesible_individual(need)]
            ocultas = len(problema.necesidades_asociadas) - len(visible_ids)
        else:
            org_id = user_ctx.get("organizacion_id")
            visible_ids = [need.id for need in problema.necesidades_asociadas if _need_accesible(need, org_id)]
            ocultas = len(problema.necesidades_asociadas) - len(visible_ids)
    else:
        org_id = user_ctx
        visible_ids = [need.id for need in problema.necesidades_asociadas if _need_accesible(need, org_id)]
        ocultas = len(problema.necesidades_asociadas) - len(visible_ids)
    return ProblemaColectivoResponse(
        id=problema.id,
        descripcion=problema.descripcion,
        estado=ProblemaColectivoEstado(problema.estado),
        necesidades_asociadas=sorted(visible_ids),
        necesidades_ocultas=ocultas,
        personas_participantes=sorted(
            persona.id for persona in problema.personas_participantes
        ),
        organizaciones_participantes=sorted(
            org.id for org in problema.organizaciones_participantes
        ),
        evidencias=problema.evidencias,
        origen_datos=OrigenDatos(problema.origen_datos),
        fecha_deteccion=problema.fecha_deteccion,
        fecha_actualizacion=problema.fecha_actualizacion,
    )


def _puede_ver_iniciativa(iniciativa: Iniciativa, user_ctx) -> bool:
    """Lectura: responsable, propietario de la necesidad o participante del problema."""
    if isinstance(user_ctx, dict):
        tipo = user_ctx.get("tipo")
        if tipo == "individuo":
            persona_id = user_ctx.get("persona_id")
            if iniciativa.responsable_tipo == "persona" and iniciativa.responsable_id == persona_id:
                return True
            if iniciativa.necesidad is not None and iniciativa.necesidad.persona_id == persona_id:
                return True
            problema = iniciativa.problema_colectivo
            if problema is not None and (problema.persona_id == persona_id or any(p.id == persona_id for p in problema.personas_participantes)):
                return True
            return False
        org_id = user_ctx.get("organizacion_id")
    else:
        org_id = user_ctx
    if iniciativa.responsable_tipo == "organizacion" and iniciativa.responsable_id == org_id:
        return True
    if iniciativa.necesidad is not None and iniciativa.necesidad.organizacion_id == org_id:
        return True
    problema = iniciativa.problema_colectivo
    if problema is None:
        return False
    if problema.organizacion_id == org_id:
        return True
    return any(org.id == org_id for org in problema.organizaciones_participantes)


def _puede_gestionar_iniciativa(iniciativa: Iniciativa, user_ctx) -> bool:
    """Escritura: solo el responsable de la iniciativa."""
    if isinstance(user_ctx, dict):
        tipo = user_ctx.get("tipo")
        if tipo == "individuo":
            persona_id = user_ctx.get("persona_id")
            return (iniciativa.responsable_tipo == "persona" and iniciativa.responsable_id == persona_id)
        org_id = user_ctx.get("organizacion_id")
    else:
        org_id = user_ctx
    if iniciativa.responsable_tipo == "organizacion":
        return iniciativa.responsable_id == org_id
    return (
        iniciativa.necesidad is not None
        and iniciativa.necesidad.organizacion_id == org_id
    )


def _registrar_evento(
    db: Session,
    entidad_referencia: str,
    entidad_id: int,
    tipo_evento: str,
    user: dict,
    justificacion: Optional[str] = None,
    dato_anterior: Optional[str] = None,
    dato_nuevo: Optional[str] = None,
) -> None:
    db.add(
        EventoAuditoria(
            entidad_referencia=entidad_referencia,
            entidad_id=entidad_id,
            tipo_evento=tipo_evento,
            usuario_o_sistema=f"user_{user.get('user_id')}",
            justificacion=justificacion,
            dato_anterior=dato_anterior,
            dato_nuevo=dato_nuevo,
        )
    )


# ---------------------------------------------------------------------------
# Autenticación y organizaciones
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=200)


class PersonaRegistroRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=200)
    experiencia: Optional[str] = Field(default=None, max_length=500)


@app.post("/personas/registro", status_code=201)
def register_persona(payload: PersonaRegistroRequest, db: Session = Depends(get_db)):
    email_norm = payload.email.strip().lower()
    if "@" not in email_norm:
        raise HTTPException(status_code=422, detail="Correo no válido")
    existente = db.query(Persona).filter(Persona.email == email_norm).first()
    if existente is not None and existente.activo:
        raise HTTPException(status_code=400, detail="Cuenta existente")
    persona = Persona(
        nombre=payload.nombre.strip(),
        email=email_norm,
        hashed_password=hash_password(payload.password),
        rol="individuo",
        activo=1,
        estado="activa",
        preferencias_participacion=payload.experiencia,
    )
    db.add(persona)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cuenta existente")
    db.refresh(persona)
    return {
        "id": persona.id,
        "nombre": persona.nombre,
        "rol": persona.rol,
        "estado": persona.estado,
        "nota": "Datos sintéticos (synthetic_pilot). Recuperación de acceso pendiente.",
    }


@app.post("/auth/token", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = (
        db.query(OperationalUser)
        .filter(OperationalUser.email == payload.email)
        .first()
    )
    persona = db.query(Persona).filter(Persona.email == payload.email).first()
    # Intentar organización primero.
    if usuario is not None and usuario.activo:
        try:
            if verify_password(payload.password, usuario.hashed_password):
                token = create_access_token(
                    {
                        "organizacion_id": usuario.organizacion_id,
                        "user_id": usuario.id,
                        "rol": usuario.rol,
                    }
                )
                return Token(access_token=token)
        except Exception:
            pass
    # Si no es organización válida, intentar persona independiente.
    if persona is not None and persona.activo and persona.hashed_password:
        try:
            if verify_password(payload.password, persona.hashed_password):
                token = create_access_token(
                    {
                        "persona_id": persona.id,
                        "user_id": persona.id,
                        "rol": persona.rol,
                    }
                )
                return Token(access_token=token)
        except Exception:
            pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post("/organizaciones", status_code=201)
def create_org(
    nombre: str,
    tipo_organizacion: str,
    contacto_publico: str,
    password: str,
    db: Session = Depends(get_db),
):
    if len(password) < 8:
        raise HTTPException(
            status_code=422, detail="La contraseña debe tener al menos 8 caracteres"
        )
    existe = db.query(Organizacion).filter(Organizacion.nombre == nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail="Organización ya existe")
    org = Organizacion(
        nombre=nombre,
        tipo_organizacion=tipo_organizacion,
        contacto_publico=contacto_publico,
    )
    db.add(org)
    db.flush()
    founder = OperationalUser(
        email=f"fundador+{org.id}@trama.local",
        hashed_password=hash_password(password),
        nombre="fundador",
        rol="administrador",
        organizacion_id=org.id,
    )
    db.add(founder)
    db.commit()
    db.refresh(org)
    db.refresh(founder)
    return {
        "id": org.id,
        "nombre": org.nombre,
        "estado": org.estado,
        "fundador_id": founder.id,
        "fundador_email": founder.email,
    }


@app.post("/organizaciones/{org_id}/usuarios")
def create_user(
    org_id: int,
    email: str,
    nombre: str,
    password: str,
    rol: str = "miembro",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.get("organizacion_id") != org_id:
        raise HTTPException(status_code=403, detail="No pertenece a esta organización")
    operador = db.get(OperationalUser, user.get("user_id"))
    if (
        operador is None
        or not operador.activo
        or operador.organizacion_id != org_id
        or operador.rol != "administrador"
    ):
        raise HTTPException(
            status_code=403, detail="Se requiere rol administrador"
        )
    if len(password) < 8:
        raise HTTPException(
            status_code=422, detail="La contraseña debe tener al menos 8 caracteres"
        )
    if rol not in {"administrador", "miembro", "observador"}:
        raise HTTPException(status_code=422, detail="Rol no permitido")
    if db.query(OperationalUser).filter(OperationalUser.email == email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    nuevo = OperationalUser(
        email=email,
        nombre=nombre,
        hashed_password=hash_password(password),
        rol=rol,
        organizacion_id=org_id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {
        "id": nuevo.id,
        "email": nuevo.email,
        "nombre": nuevo.nombre,
        "rol": nuevo.rol,
        "organizacion_id": nuevo.organizacion_id,
    }


# ---------------------------------------------------------------------------
# Necesidades
# ---------------------------------------------------------------------------
@app.post("/necesidades", status_code=201)
def create_necesidad(
    titulo: str,
    descripcion: str,
    organizacion_id: Optional[int] = None,
    persona_id: Optional[int] = None,
    visibilidad: str = "privada",
    criterios_exito: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    tipo = user.get("tipo")
    if tipo == "individuo":
        if organizacion_id is not None:
            raise HTTPException(status_code=403, detail="No pertenece a esta organización")
        if persona_id is None or persona_id != user.get("persona_id"):
            raise HTTPException(status_code=403, detail="No pertenece a esta persona")
        org_id = None
    else:
        org_id = user.get("organizacion_id")
        if organizacion_id is not None and org_id != organizacion_id:
            raise HTTPException(status_code=403, detail="No pertenece a esta organización")
        if organizacion_id is None:
            organizacion_id = org_id
        persona_id = None
    if visibilidad not in {v.value for v in NecesidadVisibilidad}:
        raise HTTPException(status_code=422, detail="Visibilidad no permitida")
    necesidad = Necesidad(
        titulo=titulo,
        descripcion=descripcion,
        organizacion_id=organizacion_id,
        persona_id=persona_id,
        visibilidad=visibilidad,
        criterios_exito=criterios_exito,
        estado="propuesta",
    )
    db.add(necesidad)
    db.flush()
    _registrar_evento(
        db,
        "necesidad",
        necesidad.id,
        "inicio",
        user,
        justificacion="Necesidad registrada",
    )
    db.commit()
    db.refresh(necesidad)
    return _need_dto(necesidad, org_id if tipo != "individuo" else None)


@app.get("/necesidades")
def list_necesidades(
    organizacion_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    org_id = user["organizacion_id"]
    if organizacion_id is not None:
        if org_id != organizacion_id:
            raise HTTPException(
                status_code=403, detail="No pertenece a esta organización"
            )
        query = db.query(Necesidad).filter(
            Necesidad.organizacion_id == organizacion_id
        )
    else:
        # Descubrimiento: necesidades propias + compartibles/públicas.
        query = db.query(Necesidad).filter(
            or_(
                Necesidad.organizacion_id == org_id,
                Necesidad.visibilidad.in_(["compartible", "publica"]),
            )
        )
    return [_need_dto(n, org_id) for n in query.order_by(Necesidad.id).all()]


# ---------------------------------------------------------------------------
# Recursos
# ---------------------------------------------------------------------------
@app.post("/recursos", status_code=201)
def create_recurso(
    tipo_recurso: str,
    nombre: str,
    organizacion_id: int,
    disponibilidad: str = "disponible",
    restricciones: str = "",
    licencia_utilizacion: str = "CC-BY",
    necesidad_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.get("organizacion_id") != organizacion_id:
        raise HTTPException(status_code=403, detail="No pertenece a esta organización")
    _get_org(db, organizacion_id)
    if necesidad_id is not None:
        necesidad = db.get(Necesidad, necesidad_id)
        if necesidad is None or not _need_accesible(necesidad, {"tipo": "organizacion", "organizacion_id": organizacion_id}):
            raise HTTPException(
                status_code=404,
                detail=f"Necesidad {necesidad_id} no encontrada o no accesible",
            )
    recurso = Recurso(
        tipo_recurso=tipo_recurso,
        nombre=nombre,
        organizacion_id=organizacion_id,
        disponibilidad=disponibilidad,
        restricciones=restricciones,
        licencia_utilizacion=licencia_utilizacion,
        necesidad_id=necesidad_id,
    )
    db.add(recurso)
    db.commit()
    db.refresh(recurso)
    return {
        "id": recurso.id,
        "tipo_recurso": recurso.tipo_recurso,
        "nombre": recurso.nombre,
        "disponibilidad": recurso.disponibilidad,
        "licencia_utilizacion": recurso.licencia_utilizacion,
        "organizacion_id": recurso.organizacion_id,
        "necesidad_id": recurso.necesidad_id,
    }


@app.get("/recursos")
def list_recursos(
    organizacion_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(Recurso)
    if organizacion_id is not None:
        if user.get("organizacion_id") != organizacion_id:
            raise HTTPException(
                status_code=403, detail="No pertenece a esta organización"
            )
        query = query.filter(Recurso.organizacion_id == organizacion_id)
    else:
        query = query.filter(Recurso.organizacion_id == user.get("organizacion_id"))
    return [
        {
            "id": r.id,
            "tipo_recurso": r.tipo_recurso,
            "nombre": r.nombre,
            "disponibilidad": r.disponibilidad,
            "licencia_utilizacion": r.licencia_utilizacion,
            "organizacion_id": r.organizacion_id,
            "necesidad_id": r.necesidad_id,
        }
        for r in query.order_by(Recurso.id).all()
    ]


# ---------------------------------------------------------------------------
# Problemas colectivos
# ---------------------------------------------------------------------------
@app.post(
    "/problemas-colectivos",
    response_model=ProblemaColectivoResponse,
    status_code=201,
)
def create_problema_colectivo(
    payload: ProblemaColectivoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Autorización dual: individuo puede crear a partir de sus necesidades.
    tipo = user.get("tipo")
    if tipo == "individuo":
        org_id = None
    else:
        org_id = user.get("organizacion_id")
        if org_id is None:
            raise HTTPException(status_code=403, detail="No se identificó una organización válida")
        _get_org(db, org_id)

    if payload.origen_datos is not OrigenDatos.synthetic_pilot:
        # El MVP no tiene proceso de consentimiento para datos reales.
        raise HTTPException(
            status_code=403,
            detail=(
                "Este MVP solo admite datos sintéticos etiquetados "
                "(origen_datos=synthetic_pilot)"
            ),
        )

    necesidades = []
    for need_id in payload.necesidades_asociadas:
        need = db.get(Necesidad, need_id)
        # No se distingue entre inexistente e inaccesible para no filtrar
        # la existencia de necesidades privadas de otras organizaciones.
        if need is None or (org_id is not None and not _need_accesible(need, org_id)) and not (tipo == "individuo" and need.persona_id is not None and need.persona_id == user.get("persona_id")):
            raise HTTPException(
                status_code=404,
                detail=f"Necesidad {need_id} no encontrada o no accesible",
            )
        necesidades.append(need)

    personas_solicitadas = []
    for persona_id in payload.personas_participantes:
        persona = db.get(Persona, persona_id)
        if persona is None:
            raise HTTPException(
                status_code=404, detail=f"Persona {persona_id} no encontrada"
            )
        personas_solicitadas.append(persona)

    organizaciones_solicitadas = []
    for participante_id in payload.organizaciones_participantes:
        participante = db.get(Organizacion, participante_id)
        if participante is None:
            raise HTTPException(
                status_code=404,
                detail=f"Organización {participante_id} no encontrada",
            )
        organizaciones_solicitadas.append(participante)

    # Participantes derivados de las necesidades asociadas. No se permite
    # incorporar terceros sin una relación previa (no hay flujo de invitación
    # ni consentimiento implementado todavía).
    personas_derivadas = {
        need.persona_id for need in necesidades if need.persona_id is not None
    }
    organizaciones_derivadas = {
        need.organizacion_id
        for need in necesidades
        if need.organizacion_id is not None
    }
    if org_id is not None:
        organizaciones_derivadas.add(org_id)

    if any(p.id not in personas_derivadas for p in personas_solicitadas):
        raise HTTPException(
            status_code=403,
            detail=(
                "No se puede incorporar una persona sin relación con las "
                "necesidades asociadas (falta flujo de consentimiento)"
            ),
        )
    if any(o.id not in organizaciones_derivadas for o in organizaciones_solicitadas):
        raise HTTPException(
            status_code=403,
            detail=(
                "No se puede incorporar una organización sin relación con las "
                "necesidades asociadas (falta flujo de invitación)"
            ),
        )

    # Los propietarios de las necesidades asociadas participan por definición.
    personas_participantes = sorted(personas_derivadas)
    organizaciones_participantes = sorted(organizaciones_derivadas)

    problema = ProblemaColectivo(
        descripcion=payload.descripcion,
        evidencias=payload.evidencias,
        estado=ProblemaColectivoEstado.detectado.value,
        origen_datos=payload.origen_datos.value,
        organizacion_id=org_id,
        persona_id=user.get("persona_id") if tipo == "individuo" else None,
        creado_por_id=user.get("user_id") or user.get("persona_id"),
    )
    problema.necesidades_asociadas = necesidades
    problema.personas_participantes = [
        db.get(Persona, persona_id) for persona_id in personas_participantes
    ]
    problema.organizaciones_participantes = [
        db.get(Organizacion, organizacion_id)
        for organizacion_id in organizaciones_participantes
    ]
    db.add(problema)
    db.flush()
    _registrar_evento(
        db,
        "problema_colectivo",
        problema.id,
        "inicio",
        user,
        justificacion="Problema colectivo creado en estado detectado",
    )
    db.commit()
    db.refresh(problema)
    return _problema_dto(problema, org_id)


class InvitacionRequest(BaseModel):
    persona_id: int = Field(gt=0)
    mensaje: Optional[str] = Field(default=None, max_length=500)


class ParticipacionRequest(BaseModel):
    persona_id: int = Field(gt=0)
    aceptar: bool = True


@app.post("/problemas-colectivos/{problema_id}/invitaciones", status_code=201)
def enviar_invitacion(
    problema_id: int,
    payload: InvitacionRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    problema = db.get(ProblemaColectivo, problema_id)
    if problema is None:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    if not _problema_visible(problema, user):
        raise HTTPException(status_code=403, detail="No puedes invitar a este problema")
    persona = db.get(Persona, payload.persona_id)
    if persona is None or not persona.activo:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    # No duplicados: verificar invitación pendiente existente
    existente = db.query(Invitacion).filter(
        Invitacion.problema_colectivo_id == problema_id,
        Invitacion.destinatario_id == payload.persona_id,
        Invitacion.estado == "pendiente",
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una invitación pendiente")
    emisor_tipo = "persona" if user.get("tipo") == "individuo" else "organizacion"
    emisor_id = user.get("persona_id") if user.get("tipo") == "individuo" else user.get("organizacion_id")
    invitacion = Invitacion(
        problema_colectivo_id=problema_id,
        emisor_id=emisor_id,
        emisor_tipo=emisor_tipo,
        destinatario_id=payload.persona_id,
        estado="pendiente",
        mensaje=payload.mensaje,
    )
    db.add(invitacion)
    try:
        db.commit()
        db.refresh(invitacion)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar invitación")
    _registrar_evento(db, "problema_colectivo", problema_id, "inicio", user, justificacion=f"Invitación {invitacion.id} creada para persona {payload.persona_id}: {payload.mensaje or ''}")
    db.commit()
    return {"id": invitacion.id, "problema_id": problema_id, "persona_id": payload.persona_id, "estado": invitacion.estado, "nota": "Invitación persistida; consentimiento pendiente."}


@app.post("/problemas-colectivos/{problema_id}/participaciones", status_code=201)
def aceptar_participacion(
    problema_id: int,
    payload: ParticipacionRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    problema = db.get(ProblemaColectivo, problema_id)
    if problema is None:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    persona_id = payload.persona_id
    if user.get("tipo") == "individuo" and user.get("persona_id") != persona_id:
        raise HTTPException(status_code=403, detail="No corresponde a esta persona")
    persona = db.get(Persona, persona_id)
    if persona is None or not persona.activo:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    # Verificar invitación válida y pendiente
    invitacion = db.query(Invitacion).filter(
        Invitacion.problema_colectivo_id == problema_id,
        Invitacion.destinatario_id == persona_id,
        Invitacion.estado == "pendiente",
    ).first()
    if not invitacion and payload.aceptar:
        # Permitir solo si ya es participante (compatibilidad)
        if not any(p.id == persona_id for p in (problema.personas_participantes or [])):
            raise HTTPException(status_code=403, detail="No existe invitación pendiente para esta persona")
    if payload.aceptar:
        if not any(p.id == persona_id for p in (problema.personas_participantes or [])):
            problema.personas_participantes = (problema.personas_participantes or []) + [persona]
            db.commit()
        if invitacion:
            invitacion.estado = "aceptada"
            from sqlalchemy.sql import func
            invitacion.fecha_respuesta = func.now()
            db.commit()
        _registrar_evento(db, "problema_colectivo", problema_id, "hito", user, justificacion="Participación aceptada")
        db.commit()
        return {"problema_id": problema_id, "persona_id": persona_id, "estado": "aceptada"}
    else:
        if invitacion:
            invitacion.estado = "rechazada"
            from sqlalchemy.sql import func
            invitacion.fecha_respuesta = func.now()
            db.commit()
        problema.personas_participantes = [p for p in (problema.personas_participantes or []) if p.id != persona_id]
        db.commit()
        _registrar_evento(db, "problema_colectivo", problema_id, "cambio_estado", user, justificacion="Participación retirada")
        db.commit()
        return {"problema_id": problema_id, "persona_id": persona_id, "estado": "rechazada"}


@app.get(
    "/problemas-colectivos",
    response_model=list[ProblemaColectivoResponse],
)
def list_problemas_colectivos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Soporta tanto organizaciones como personas independientes
    tipo = user.get("tipo")
    if tipo == "individuo":
        persona_id = user.get("persona_id")
        problemas = (
            db.query(ProblemaColectivo)
            .filter(
                or_(
                    ProblemaColectivo.persona_id == persona_id,
                    ProblemaColectivo.id.in_(
                        db.query(problema_participantes_persona.c.problema_colectivo_id)
                        .filter(problema_participantes_persona.c.persona_id == persona_id)
                    )
                )
            )
            .order_by(ProblemaColectivo.id)
            .all()
        )
        return [_problema_dto(problema, user) for problema in problemas]
    org_id = user.get("organizacion_id")
    problemas = (
        db.query(ProblemaColectivo)
        .outerjoin(
            problema_participantes_organizacion,
            problema_participantes_organizacion.c.problema_colectivo_id
            == ProblemaColectivo.id,
        )
        .filter(
            or_(
                ProblemaColectivo.organizacion_id == org_id,
                problema_participantes_organizacion.c.organizacion_id == org_id,
            )
        )
        .distinct()
        .order_by(ProblemaColectivo.id)
        .all()
    )
    return [_problema_dto(problema, user) for problema in problemas]


@app.get(
    "/problemas-colectivos/{problema_id}",
    response_model=ProblemaColectivoResponse,
)
def get_problema_colectivo(
    problema_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    problema = db.get(ProblemaColectivo, problema_id)
    # 404 también para problemas existentes pero no accesibles: no se
    # confirma la existencia de recursos de otras organizaciones.
    if problema is None or not _problema_visible(
        problema, user["organizacion_id"]
    ):
        raise HTTPException(
            status_code=404, detail="Problema colectivo no encontrado"
        )
    return _problema_dto(problema, user["organizacion_id"])


@app.post(
    "/problemas-colectivos/{problema_id}/estado",
    response_model=ProblemaColectivoResponse,
)
def cambiar_estado_problema_colectivo(
    problema_id: int,
    payload: ProblemaColectivoEstadoUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    problema = db.get(ProblemaColectivo, problema_id)
    # Solo el propietario puede validar/cerrar. No hay roles por problema
    # definidos todavía; se documenta como limitación.
    if problema is None or problema.organizacion_id != user["organizacion_id"]:
        raise HTTPException(
            status_code=404, detail="Problema colectivo no encontrado"
        )

    estado_actual = ProblemaColectivoEstado(problema.estado)
    permitidos = TRANSICIONES_PROBLEMA_COLECTIVO[estado_actual]
    if payload.estado not in permitidos:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Transición no permitida: {estado_actual.value} → "
                f"{payload.estado.value}"
            ),
        )
    if (
        payload.estado is ProblemaColectivoEstado.validado
        and not (problema.evidencias or "").strip()
    ):
        raise HTTPException(
            status_code=422,
            detail="Para validar el problema se requiere evidencia registrada",
        )

    anterior = problema.estado
    problema.estado = payload.estado.value
    _registrar_evento(
        db,
        "problema_colectivo",
        problema.id,
        "cambio_estado",
        user,
        justificacion=payload.justificacion or "Cambio de estado",
        dato_anterior=anterior,
        dato_nuevo=problema.estado,
    )
    db.commit()
    db.refresh(problema)
    return _problema_dto(problema, user["organizacion_id"])


# ---------------------------------------------------------------------------
# Iniciativas
# ---------------------------------------------------------------------------
@app.post("/iniciativas", status_code=201)
def create_iniciativa(
    necesidad_id: int,
    responsable_id: int,
    alternativas_evaluadas: str = "",
    criterios_decision: str = "",
    presupuesto_estimate: Optional[float] = None,
    plazo: Optional[str] = None,
    problema_colectivo_id: Optional[int] = None,
    titulo: Optional[str] = None,
    descripcion: str = "",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    tipo = user.get("tipo")
    if tipo == "individuo":
        org_id = None
    else:
        org_id = user.get("organizacion_id")
        if org_id is None:
            raise HTTPException(status_code=403, detail="No se identificó organización")
    necesidad = db.get(Necesidad, necesidad_id)
    if necesidad is None or (org_id is not None and not _need_accesible(necesidad, org_id)) or (tipo == "individuo" and (necesidad.persona_id is None or necesidad.persona_id != user.get("persona_id"))):
        raise HTTPException(status_code=404, detail="Necesidad no accesible")
    if user.get("tipo") == "individuo":
        if responsable_id != user.get("persona_id"):
            raise HTTPException(status_code=403, detail="Responsable debe ser la persona autenticada")
    else:
        if responsable_id != org_id:
            raise HTTPException(
                status_code=403,
                detail="El responsable debe ser la organización autenticada",
            )
    if len((criterios_decision or "").strip()) < 5:
        raise HTTPException(
            status_code=422,
            detail="criterios_decision debe describir el criterio de decisión",
        )

    problema = None
    if problema_colectivo_id is not None:
        problema = db.get(ProblemaColectivo, problema_colectivo_id)
        if problema is None or not _problema_visible(problema, user if tipo == "individuo" else org_id):
            raise HTTPException(
                status_code=404, detail="Problema colectivo no encontrado"
            )

    resp_tipo = "persona" if user.get("tipo") == "individuo" else "organizacion"
    resp_id = user.get("persona_id") if user.get("tipo") == "individuo" else org_id
    iniciativa = Iniciativa(
        necesidad_id=necesidad_id,
        problema_colectivo_id=problema_colectivo_id,
        responsable_id=resp_id,
        responsable_tipo=resp_tipo,
        titulo=titulo,
        descripcion=descripcion,
        alternativas_evaluadas=alternativas_evaluadas,
        criterios_decision=criterios_decision,
        presupuesto_estimate=presupuesto_estimate,
        plazo=plazo,
        estado="propuesta",
    )
    db.add(iniciativa)
    db.flush()
    _registrar_evento(
        db,
        "iniciativa",
        iniciativa.id,
        "inicio",
        user,
        justificacion="Iniciativa propuesta",
    )
    db.commit()
    db.refresh(iniciativa)
    return {
        "id": iniciativa.id,
        "necesidad_id": iniciativa.necesidad_id,
        "problema_colectivo_id": iniciativa.problema_colectivo_id,
        "titulo": iniciativa.titulo,
        "descripcion": iniciativa.descripcion,
        "alternativas_evaluadas": iniciativa.alternativas_evaluadas,
        "criterios_decision": iniciativa.criterios_decision,
        "presupuesto_estimate": iniciativa.presupuesto_estimate,
        "plazo": iniciativa.plazo,
        "estado": iniciativa.estado,
        "responsable_id": iniciativa.responsable_id,
        "responsable_tipo": iniciativa.responsable_tipo,
        "fecha_creacion": iniciativa.fecha_creacion,
        "fecha_actualizacion": iniciativa.fecha_actualizacion,
    }


@app.get("/iniciativas/{iniciativa_id}")
def get_iniciativa(
    iniciativa_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_ver_iniciativa(iniciativa, user):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    return {
        "id": iniciativa.id,
        "necesidad_id": iniciativa.necesidad_id,
        "problema_colectivo_id": iniciativa.problema_colectivo_id,
        "titulo": iniciativa.titulo,
        "descripcion": iniciativa.descripcion,
        "alternativas_evaluadas": iniciativa.alternativas_evaluadas,
        "criterios_decision": iniciativa.criterios_decision,
        "presupuesto_estimate": iniciativa.presupuesto_estimate,
        "plazo": iniciativa.plazo,
        "estado": iniciativa.estado,
        "responsable_id": iniciativa.responsable_id,
        "responsable_tipo": iniciativa.responsable_tipo,
        "fecha_creacion": iniciativa.fecha_creacion,
        "fecha_actualizacion": iniciativa.fecha_actualizacion,
    }


# ---------------------------------------------------------------------------
# Decisiones y eventos
# ---------------------------------------------------------------------------
@app.post("/decisiones", status_code=201)
def create_decision(
    iniciativa_id: int,
    tipo_decision: str,
    alternativa_elegida: str,
    motivo: str,
    responsable_decision: int,
    version_metodologia: str,
    factors: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_gestionar_iniciativa(
        iniciativa, user
    ):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")

    decision = Decision(
        iniciativa_id=iniciativa_id,
        tipo_decision=tipo_decision,
        alternativa_elegida=alternativa_elegida,
        motivo=motivo,
        responsable_decision=responsable_decision,
        version_metodologia=version_metodologia,
        factors=factors,
    )
    db.add(decision)
    db.flush()
    _registrar_evento(
        db,
        "decision",
        decision.id,
        "resultado",
        user,
        justificacion=motivo,
        dato_nuevo=alternativa_elegida,
    )
    db.commit()
    db.refresh(decision)
    return {
        "id": decision.id,
        "iniciativa_id": decision.iniciativa_id,
        "version_metodologia": decision.version_metodologia,
        "alternativa_elegida": decision.alternativa_elegida,
    }


ENTIDADES_AUDITABLES = {
    "necesidad",
    "iniciativa",
    "problema_colectivo",
    "decision",
}


@app.post("/eventos", status_code=201)
def create_evento(
    entidad_referencia: str,
    entidad_id: int,
    tipo_evento: str,
    justificacion: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if entidad_referencia not in ENTIDADES_AUDITABLES:
        raise HTTPException(
            status_code=422, detail="Entidad de auditoría no permitida"
        )
    if tipo_evento not in {tipo.value for tipo in EventoTipo}:
        raise HTTPException(status_code=422, detail="Tipo de evento no permitido")

    org_id = user["organizacion_id"] if user.get("tipo") != "individuo" else None
    persona_id = user.get("persona_id")
    autorizado = False
    if entidad_referencia == "necesidad":
        entidad = db.get(Necesidad, entidad_id)
        if user.get("tipo") == "individuo":
            autorizado = entidad is not None and (entidad.persona_id == persona_id or entidad.visibilidad in ("compartible", "publica"))
        else:
            autorizado = entidad is not None and entidad.organizacion_id == org_id
    elif entidad_referencia == "iniciativa":
        entidad = db.get(Iniciativa, entidad_id)
        autorizado = entidad is not None and _puede_gestionar_iniciativa(entidad, user)
    elif entidad_referencia == "problema_colectivo":
        entidad = db.get(ProblemaColectivo, entidad_id)
        autorizado = entidad is not None and _problema_visible(entidad, user)
    elif entidad_referencia == "decision":
        entidad = db.get(Decision, entidad_id)
        autorizado = entidad is not None and _puede_gestionar_iniciativa(entidad.iniciativa, user)

    if not autorizado:
        raise HTTPException(
            status_code=404, detail="Entidad no encontrada o no accesible"
        )

    evento = EventoAuditoria(
        entidad_referencia=entidad_referencia,
        entidad_id=entidad_id,
        tipo_evento=tipo_evento,
        usuario_o_sistema=f"user_{user.get('user_id')}",
        justificacion=justificacion,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return {
        "id": evento.id,
        "tipo_evento": evento.tipo_evento,
        "entidad_referencia": evento.entidad_referencia,
        "entidad_id": evento.entidad_id,
    }


# ---------------------------------------------------------------------------
# Exportación (solo datos propios; etiqueta sintética explícita)
# ---------------------------------------------------------------------------
NOTA_SINTETICA = (
    "Datos de desarrollo/piloto sintético. No son resultados reales "
    "ni impacto verificado."
)


@app.get("/exportar/necesidades")
def export_necesidades(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    org_id = user["organizacion_id"]
    needs = (
        db.query(Necesidad)
        .filter(Necesidad.organizacion_id == org_id)
        .order_by(Necesidad.id)
        .all()
    )
    output = [
        {
            "id": n.id,
            "titulo": n.titulo,
            "estado": n.estado,
            "visibilidad": n.visibilidad,
            "organizacion_id": n.organizacion_id,
            "fecha_creacion": n.fecha_creacion.isoformat(),
        }
        for n in needs
    ]
    return JSONResponse(
        content={
            "export": output,
            "format": "json",
            "synthetic": True,
            "nota": NOTA_SINTETICA,
        }
    )


@app.get("/exportar/csv")
def export_csv_necesidades(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    org_id = user["organizacion_id"]
    needs = (
        db.query(Necesidad)
        .filter(Necesidad.organizacion_id == org_id)
        .order_by(Necesidad.id)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "titulo",
            "estado",
            "visibilidad",
            "organizacion_id",
            "fecha_creacion",
        ]
    )
    for need in needs:
        writer.writerow(
            [
                need.id,
                need.titulo,
                need.estado,
                need.visibilidad,
                need.organizacion_id,
                need.fecha_creacion,
            ]
        )
    return JSONResponse(
        content={
            "export": output.getvalue(),
            "format": "csv",
            "synthetic": True,
            "nota": NOTA_SINTETICA,
        }
    )# ---------------------------------------------------------------------------
# Matching / Descubrimiento
# ---------------------------------------------------------------------------
@app.get("/matching/necesidades-relacionadas")
def matching_necesidades_relacionadas(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Descubre necesidades potencialmente relacionadas mediante reglas deterministas."""
    tipo = user.get("tipo")
    if tipo == "individuo":
        pid = user.get("persona_id")
        needs = (
            db.query(Necesidad)
            .filter(
                (Necesidad.persona_id == pid)
                | (Necesidad.visibilidad.in_(["compartible", "publica"]))
            )
            .order_by(Necesidad.id)
            .all()
        )
    else:
        org_id = user.get("organizacion_id")
        needs = (
            db.query(Necesidad)
            .filter(
                (Necesidad.organizacion_id == org_id)
                | (Necesidad.visibilidad.in_(["compartible", "publica"]))
            )
            .order_by(Necesidad.id)
            .all()
        )
    matches = matching_find_related_needs(needs)
    return {"matches": matches, "total": len(matches), "nota": "Coincidencias basadas en reglas deterministas. No son probabilidades calibradas."}


# ---------------------------------------------------------------------------
# Decisiones por iniciativa
# ---------------------------------------------------------------------------
@app.post("/iniciativas/{iniciativa_id}/decisiones", status_code=201)
def create_decision_for_initiative(
    iniciativa_id: int,
    tipo_decision: str,
    alternativa_elegida: str,
    motivo: str,
    version_metodologia: str,
    factors: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Registra una decision para una iniciativa con autorizacion."""
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_gestionar_iniciativa(iniciativa, user):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    tipo = user.get("tipo")
    responsable = user.get("persona_id") if tipo == "individuo" else user.get("organizacion_id")
    decision = Decision(
        iniciativa_id=iniciativa_id,
        tipo_decision=tipo_decision,
        alternativa_elegida=alternativa_elegida,
        motivo=motivo,
        responsable_decision=responsable,
        version_metodologia=version_metodologia,
        factors=factors,
    )
    db.add(decision)
    db.flush()
    _registrar_evento(db, "decision", decision.id, "resultado", user, justificacion=motivo)
    db.commit()
    db.refresh(decision)
    return {
        "id": decision.id,
        "iniciativa_id": decision.iniciativa_id,
        "tipo_decision": decision.tipo_decision,
        "alternativa_elegida": decision.alternativa_elegida,
        "motivo": decision.motivo,
        "responsable_decision": decision.responsable_decision,
        "version_metodologia": decision.version_metodologia,
        "fecha": decision.fecha,
    }


# ---------------------------------------------------------------------------
# Actividades / Hitos por iniciativa
# ---------------------------------------------------------------------------
@app.post("/iniciativas/{iniciativa_id}/actividades", status_code=201)
def create_actividad_for_initiative(
    iniciativa_id: int,
    tipo_actividad: str,
    descripcion: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Registra una actividad o hito de ejecucion para una iniciativa."""
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_ver_iniciativa(iniciativa, user):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    evento = EventoAuditoria(
        entidad_referencia="iniciativa",
        entidad_id=iniciativa_id,
        tipo_evento="hito",
        usuario_o_sistema=f"user_{user.get('user_id')}",
        justificacion=descripcion,
        dato_nuevo=tipo_actividad,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return {
        "id": evento.id,
        "iniciativa_id": iniciativa_id,
        "tipo_actividad": tipo_actividad,
        "descripcion": descripcion,
        "fecha": evento.fecha,
    }


# ---------------------------------------------------------------------------
# Historial de iniciativa
# ---------------------------------------------------------------------------
@app.get("/iniciativas/{iniciativa_id}/historial")
def get_historial_iniciativa(
    iniciativa_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Retorna el timeline cronologico de una iniciativa."""
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_ver_iniciativa(iniciativa, user):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    eventos = (
        db.query(EventoAuditoria)
        .filter(
            EventoAuditoria.entidad_referencia == "iniciativa",
            EventoAuditoria.entidad_id == iniciativa_id,
        )
        .order_by(EventoAuditoria.fecha)
        .all()
    )
    decisiones = (
        db.query(Decision)
        .filter(Decision.iniciativa_id == iniciativa_id)
        .order_by(Decision.fecha)
        .all()
    )
    timeline = []
    for e in eventos:
        timeline.append({
            "tipo": "evento",
            "id": e.id,
            "tipo_evento": e.tipo_evento,
            "usuario": e.usuario_o_sistema,
            "justificacion": e.justificacion,
            "dato_nuevo": e.dato_nuevo,
            "fecha": e.fecha.isoformat(),
        })
    for d in decisiones:
        timeline.append({
            "tipo": "decision",
            "id": d.id,
            "tipo_decision": d.tipo_decision,
            "alternativa_elegida": d.alternativa_elegida,
            "motivo": d.motivo,
            "responsable_decision": d.responsable_decision,
            "version_metodologia": d.version_metodologia,
            "fecha": d.fecha.isoformat(),
        })
    timeline.sort(key=lambda x: x["fecha"])
    return {"iniciativa_id": iniciativa_id, "timeline": timeline, "total": len(timeline)}


# ---------------------------------------------------------------------------
# Exportacion de expediente completo de iniciativa
# ---------------------------------------------------------------------------
@app.get("/exportar/iniciativa/{iniciativa_id}")
def export_iniciativa(
    iniciativa_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Exporta el expediente completo de una iniciativa (JSON)."""
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_ver_iniciativa(iniciativa, user):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    decisiones = (
        db.query(Decision)
        .filter(Decision.iniciativa_id == iniciativa_id)
        .order_by(Decision.fecha)
        .all()
    )
    eventos = (
        db.query(EventoAuditoria)
        .filter(
            EventoAuditoria.entidad_referencia == "iniciativa",
            EventoAuditoria.entidad_id == iniciativa_id,
        )
        .order_by(EventoAuditoria.fecha)
        .all()
    )
    necesidad = iniciativa.necesidad
    problema = iniciativa.problema_colectivo
    return JSONResponse(content={
        "iniciativa": {
            "id": iniciativa.id,
            "titulo": iniciativa.titulo,
            "descripcion": iniciativa.descripcion,
            "estado": iniciativa.estado,
            "responsable_id": iniciativa.responsable_id,
            "responsable_tipo": iniciativa.responsable_tipo,
            "criterios_decision": iniciativa.criterios_decision,
            "alternativas_evaluadas": iniciativa.alternativas_evaluadas,
            "plazo": iniciativa.plazo,
            "fecha_creacion": iniciativa.fecha_creacion.isoformat(),
        },
        "necesidad_origen": {
            "id": necesidad.id,
            "titulo": necesidad.titulo,
            "descripcion": necesidad.descripcion,
            "visibilidad": necesidad.visibilidad,
        } if necesidad else None,
        "problema_colectivo": {
            "id": problema.id,
            "descripcion": problema.descripcion,
            "estado": problema.estado,
            "origen_datos": problema.origen_datos,
        } if problema else None,
        "decisiones": [
            {
                "id": d.id,
                "tipo_decision": d.tipo_decision,
                "alternativa_elegida": d.alternativa_elegida,
                "motivo": d.motivo,
                "responsable_decision": d.responsable_decision,
                "version_metodologia": d.version_metodologia,
                "fecha": d.fecha.isoformat(),
            }
            for d in decisiones
        ],
        "eventos": [
            {
                "id": e.id,
                "tipo_evento": e.tipo_evento,
                "usuario": e.usuario_o_sistema,
                "justificacion": e.justificacion,
                "fecha": e.fecha.isoformat(),
            }
            for e in eventos
        ],
        "synthetic": True,
        "nota": NOTA_SINTETICA,
    })
