"""Pruebas de autenticación, contratos y etiquetado sintético."""
from datetime import timedelta

import pytest
from pydantic import ValidationError

from src.core.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.core.contracts import (
    EventoAuditoria,
    Necesidad,
    ProblemaColectivoCreate,
    ProblemaColectivoEstado,
    TRANSICIONES_PROBLEMA_COLECTIVO,
)


def test_auth_token_expiration():
    token = create_access_token(
        {"organizacion_id": 1, "user_id": 2},
        expires_delta=timedelta(seconds=-1),
    )
    assert decode_token(token) is None


def test_password_hash():
    hashed = hash_password("secret")
    assert verify_password("secret", hashed)
    assert not verify_password("wrong", hashed)


def test_synthetic_tag_explicit():
    evento = EventoAuditoria(
        id=1,
        entidad_referencia="iniciativa",
        entidad_id=1,
        tipo_evento="resultado",
        justificacion="etiquetado como estimado",
        fecha="2026-01-01T00:00:00",
    )
    assert evento.tipo_evento == "resultado"


def test_problema_colectivo_create_rechaza_estado_del_cliente():
    with pytest.raises(ValidationError):
        ProblemaColectivoCreate(
            descripcion="Problema suficientemente descriptivo",
            estado="validado",
        )


def test_problema_colectivo_create_etiqueta_sintetica_por_defecto():
    payload = ProblemaColectivoCreate(
        descripcion="Problema suficientemente descriptivo"
    )
    assert payload.origen_datos.value == "synthetic_pilot"


def test_transiciones_no_permiten_saltar_a_validado():
    permitidas = TRANSICIONES_PROBLEMA_COLECTIVO[
        ProblemaColectivoEstado.detectado
    ]
    assert ProblemaColectivoEstado.validado not in permitidas
    assert ProblemaColectivoEstado.en_analisis in permitidas


def test_necesidad_visibilidad_por_defecto_privada():
    necesidad = Necesidad(
        id=1,
        titulo="Necesidad de prueba",
        fecha_creacion="2026-01-01T00:00:00",
        fecha_actualizacion="2026-01-01T00:00:00",
    )
    assert necesidad.visibilidad.value == "privada"