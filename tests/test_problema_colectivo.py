"""Pruebas de integración de la API de Problemas Colectivos.

Cubren creación, consulta, persistencia N:M, permisos, privacidad,
estados, duplicados, auditoría, flujo completo y migraciones SQLite.

Datos: sintéticos y etiquetados (`origen_datos=synthetic_pilot`).
"""
import os
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import func, select

from src.core.models import (
    Base,
    EventoAuditoria,
    Necesidad,
    Persona,
    ProblemaColectivo,
    necesidad_problema_colectivo,
    problema_participantes_organizacion,
    problema_participantes_persona,
)


# ---------------------------------------------------------------------------
# Utilidades de prueba
# ---------------------------------------------------------------------------
def crear_persona(db_session, nombre="Persona Sintética", email=None):
    persona = Persona(nombre=nombre, email=email)
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    return persona


def crear_necesidad(
    db_session,
    *,
    organizacion_id=None,
    persona_id=None,
    titulo="Necesidad sintética",
    visibilidad="privada",
    descripcion="Descripción sintética de prueba",
):
    necesidad = Necesidad(
        titulo=titulo,
        descripcion=descripcion,
        organizacion_id=organizacion_id,
        persona_id=persona_id,
        visibilidad=visibilidad,
        estado="propuesta",
    )
    db_session.add(necesidad)
    db_session.commit()
    db_session.refresh(necesidad)
    return necesidad


def crear_problema(client, headers, **overrides):
    payload = {
        "descripcion": (
            "Varias personas y organizaciones comparten dificultades de "
            "transporte para acceder a servicios esenciales."
        ),
        "evidencias": "Datos sintéticos de prueba; no son resultados reales.",
        "necesidades_asociadas": [],
        "personas_participantes": [],
        "organizaciones_participantes": [],
        "origen_datos": "synthetic_pilot",
    }
    payload.update(overrides)
    return client.post("/problemas-colectivos", json=payload, headers=headers)


# ---------------------------------------------------------------------------
# 1-2. Creación y consulta
# ---------------------------------------------------------------------------
def test_crear_problema_colectivo_valido(client, headers_a, org_a):
    response = crear_problema(client, headers_a)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["estado"] == "detectado"
    assert data["origen_datos"] == "synthetic_pilot"
    assert data["necesidades_asociadas"] == []
    assert data["necesidades_ocultas"] == 0
    assert data["organizaciones_participantes"] == [org_a["org_id"]]
    assert data["evidencias"].startswith("Datos sintéticos")


def test_consultar_problema_colectivo(client, headers_a):
    creado = crear_problema(client, headers_a).json()

    response = client.get(
        f"/problemas-colectivos/{creado['id']}", headers=headers_a
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == creado["id"]
    assert data["descripcion"] == creado["descripcion"]
    assert data["estado"] == "detectado"


def test_problema_inexistente_devuelve_404(client, headers_a):
    response = client.get("/problemas-colectivos/99999", headers=headers_a)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 3-4. Persistencia N:M y necesidades de personas y organizaciones
# ---------------------------------------------------------------------------
def test_relaciones_nm_persisten(client, headers_a, org_a, db_session):
    persona = crear_persona(db_session)
    necesidad_org = crear_necesidad(
        db_session, organizacion_id=org_a["org_id"], titulo="Necesidad de la org"
    )
    necesidad_persona = crear_necesidad(
        db_session,
        persona_id=persona.id,
        titulo="Necesidad de la persona",
        visibilidad="compartible",
    )

    response = crear_problema(
        client,
        headers_a,
        necesidades_asociadas=[necesidad_org.id, necesidad_persona.id],
    )
    assert response.status_code == 201, response.text
    problema_id = response.json()["id"]

    # Recuperar desde una sesión limpia: verifica persistencia real.
    db_session.expire_all()
    problema = db_session.get(ProblemaColectivo, problema_id)
    assert problema is not None
    assert {n.id for n in problema.necesidades_asociadas} == {
        necesidad_org.id,
        necesidad_persona.id,
    }
    assert {p.id for p in problema.personas_participantes} == {persona.id}
    assert {o.id for o in problema.organizaciones_participantes} == {
        org_a["org_id"]
    }

    # La API también refleja ambas relaciones.
    data = client.get(
        f"/problemas-colectivos/{problema_id}", headers=headers_a
    ).json()
    assert set(data["necesidades_asociadas"]) == {
        necesidad_org.id,
        necesidad_persona.id,
    }
    assert data["personas_participantes"] == [persona.id]


def test_necesidad_de_persona_sin_organizacion(client, headers_a, db_session):
    persona = crear_persona(db_session)
    necesidad = crear_necesidad(
        db_session,
        persona_id=persona.id,
        visibilidad="compartible",
        titulo="Necesidad individual compartida",
    )

    response = crear_problema(
        client, headers_a, necesidades_asociadas=[necesidad.id]
    )

    assert response.status_code == 201, response.text
    assert response.json()["necesidades_asociadas"] == [necesidad.id]


# ---------------------------------------------------------------------------
# 5. Referencias inexistentes
# ---------------------------------------------------------------------------
def test_rechaza_necesidad_inexistente(client, headers_a):
    response = crear_problema(client, headers_a, necesidades_asociadas=[99999])
    assert response.status_code == 404
    assert "no encontrada o no accesible" in response.json()["detail"]


def test_rechaza_persona_y_organizacion_inexistentes(client, headers_a):
    response = crear_problema(
        client,
        headers_a,
        personas_participantes=[99999],
    )
    assert response.status_code == 404

    response = crear_problema(
        client,
        headers_a,
        organizaciones_participantes=[99999],
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 6. Operaciones no autorizadas
# ---------------------------------------------------------------------------
def test_escritura_anonima_rechazada(client):
    response = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Sin autenticación, debe fallar"},
    )
    assert response.status_code == 401


def test_no_puede_vincular_necesidad_privada_de_otra_org(
    client, headers_a, org_b, db_session
):
    necesidad_b = crear_necesidad(
        db_session,
        organizacion_id=org_b["org_id"],
        visibilidad="privada",
        titulo="Necesidad privada de B",
    )

    response = crear_problema(
        client, headers_a, necesidades_asociadas=[necesidad_b.id]
    )

    assert response.status_code == 404
    assert "no encontrada o no accesible" in response.json()["detail"]


def test_no_puede_ver_problema_de_otra_org(client, headers_a, headers_b):
    problema = crear_problema(client, headers_a).json()

    response = client.get(
        f"/problemas-colectivos/{problema['id']}", headers=headers_b
    )
    assert response.status_code == 404

    listado_b = client.get("/problemas-colectivos", headers=headers_b).json()
    assert listado_b == []


def test_no_puede_cambiar_estado_de_problema_ajeno(
    client, headers_a, headers_b
):
    problema = crear_problema(client, headers_a).json()

    response = client.post(
        f"/problemas-colectivos/{problema['id']}/estado",
        json={"estado": "en_analisis"},
        headers=headers_b,
    )
    assert response.status_code == 404


def test_no_puede_incorporar_organizacion_sin_relacion(
    client, headers_a, headers_b, org_b
):
    response = crear_problema(
        client,
        headers_a,
        organizaciones_participantes=[org_b["org_id"]],
    )
    assert response.status_code == 403
    assert "sin relación" in response.json()["detail"]


def test_no_puede_crear_necesidad_para_otra_org(
    client, headers_b, org_a
):
    response = client.post(
        "/necesidades",
        params={
            "titulo": "Necesidad ajena",
            "descripcion": "Intento no autorizado",
            "organizacion_id": org_a["org_id"],
        },
        headers=headers_b,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 7. Privacidad de las necesidades asociadas
# ---------------------------------------------------------------------------
def test_privacidad_necesidades_asociadas(
    client, headers_a, headers_b, org_a, org_b, db_session
):
    necesidad_privada_a = crear_necesidad(
        db_session,
        organizacion_id=org_a["org_id"],
        titulo="Necesidad privada de A",
        visibilidad="privada",
    )
    necesidad_compartida_b = crear_necesidad(
        db_session,
        organizacion_id=org_b["org_id"],
        titulo="Necesidad compartible de B",
        visibilidad="compartible",
    )

    response = crear_problema(
        client,
        headers_a,
        necesidades_asociadas=[
            necesidad_privada_a.id,
            necesidad_compartida_b.id,
        ],
    )
    assert response.status_code == 201, response.text
    problema_id = response.json()["id"]

    # A ve sus dos necesidades asociadas.
    data_a = client.get(
        f"/problemas-colectivos/{problema_id}", headers=headers_a
    ).json()
    assert set(data_a["necesidades_asociadas"]) == {
        necesidad_privada_a.id,
        necesidad_compartida_b.id,
    }
    assert data_a["necesidades_ocultas"] == 0

    # B participa por su necesidad compartible, pero no ve la privada de A.
    data_b = client.get(
        f"/problemas-colectivos/{problema_id}", headers=headers_b
    ).json()
    assert data_b["necesidades_asociadas"] == [necesidad_compartida_b.id]
    assert data_b["necesidades_ocultas"] == 1
    assert data_b["personas_participantes"] == []


# ---------------------------------------------------------------------------
# 8. Estado inicial y transiciones
# ---------------------------------------------------------------------------
def test_cliente_no_puede_fijar_estado_al_crear(client, headers_a):
    response = crear_problema(client, headers_a, estado="validado")
    assert response.status_code == 422


def test_estado_inicial_detectado_ignorando_defaults(client, headers_a):
    response = client.post(
        "/problemas-colectivos",
        json={
            "descripcion": "Problema sin estado explícito en el cuerpo",
            "evidencias": "Evidencia sintética",
        },
        headers=headers_a,
    )
    assert response.status_code == 201
    assert response.json()["estado"] == "detectado"


def test_transiciones_de_estado_permitidas(client, headers_a):
    problema = crear_problema(client, headers_a).json()
    url = f"/problemas-colectivos/{problema['id']}/estado"

    # No se puede saltar de detectado a validado.
    response = client.post(url, json={"estado": "validado"}, headers=headers_a)
    assert response.status_code == 409

    response = client.post(
        url,
        json={"estado": "en_analisis", "justificacion": "Análisis inicial"},
        headers=headers_a,
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "en_analisis"

    response = client.post(
        url,
        json={
            "estado": "validado",
            "justificacion": "Evidencia revisada por la organización",
        },
        headers=headers_a,
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "validado"

    # No se puede retroceder.
    response = client.post(url, json={"estado": "en_analisis"}, headers=headers_a)
    assert response.status_code == 409

    response = client.post(url, json={"estado": "cerrado"}, headers=headers_a)
    assert response.status_code == 200
    assert response.json()["estado"] == "cerrado"

    # Estado final: sin transiciones.
    response = client.post(url, json={"estado": "detectado"}, headers=headers_a)
    assert response.status_code == 409


def test_no_valida_sin_evidencia(client, headers_a):
    problema = crear_problema(client, headers_a, evidencias=None).json()
    url = f"/problemas-colectivos/{problema['id']}/estado"

    assert client.post(
        url, json={"estado": "en_analisis"}, headers=headers_a
    ).status_code == 200
    response = client.post(url, json={"estado": "validado"}, headers=headers_a)
    assert response.status_code == 422
    assert "evidencia" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 9. Sin duplicados ni relaciones inconsistentes
# ---------------------------------------------------------------------------
def test_sin_duplicados_en_relaciones(client, headers_a, org_a, db_session):
    persona = crear_persona(db_session)
    necesidad = crear_necesidad(
        db_session,
        organizacion_id=org_a["org_id"],
        titulo="Necesidad única",
    )
    necesidad_persona = crear_necesidad(
        db_session,
        persona_id=persona.id,
        visibilidad="compartible",
        titulo="Necesidad compartida",
    )

    response = crear_problema(
        client,
        headers_a,
        necesidades_asociadas=[necesidad.id, necesidad.id, necesidad_persona.id],
        personas_participantes=[persona.id, persona.id],
        organizaciones_participantes=[org_a["org_id"], org_a["org_id"]],
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["necesidades_asociadas"] == sorted(
        [necesidad.id, necesidad_persona.id]
    )
    assert data["personas_participantes"] == [persona.id]
    assert data["organizaciones_participantes"] == [org_a["org_id"]]

    problema_id = data["id"]
    db_session.expire_all()
    total_necesidades = db_session.execute(
        select(func.count())
        .select_from(necesidad_problema_colectivo)
        .where(
            necesidad_problema_colectivo.c.problema_colectivo_id == problema_id
        )
    ).scalar_one()
    total_personas = db_session.execute(
        select(func.count())
        .select_from(problema_participantes_persona)
        .where(
            problema_participantes_persona.c.problema_colectivo_id == problema_id
        )
    ).scalar_one()
    total_orgs = db_session.execute(
        select(func.count())
        .select_from(problema_participantes_organizacion)
        .where(
            problema_participantes_organizacion.c.problema_colectivo_id
            == problema_id
        )
    ).scalar_one()

    assert total_necesidades == 2
    assert total_personas == 1
    assert total_orgs == 1


# ---------------------------------------------------------------------------
# 10. Migraciones (SQLite prototipo) y metadata
# ---------------------------------------------------------------------------
def test_migraciones_sqlite_persisten_y_respetan_integridad(tmp_path):
    migrations = (
        Path(__file__).resolve().parents[1] / "src" / "core" / "migrations"
    )
    sql_001 = (migrations / "001_init.sql").read_text(encoding="utf-8")
    sql_002 = (migrations / "002_problemas_colectivos.sqlite.sql").read_text(
        encoding="utf-8"
    )

    db_path = tmp_path / "migracion.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.executescript(sql_001)
        connection.executescript(sql_002)

        tablas = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {
            "personas",
            "operational_users",
            "necesidades",
            "problemas_colectivos",
            "necesidad_problema_colectivo",
            "problema_participantes_persona",
            "problema_participantes_organizacion",
            "iniciativas",
            "eventos_auditoria",
        } <= tablas

        connection.execute(
            "INSERT INTO organizaciones (nombre, tipo_organizacion, contacto_publico) "
            "VALUES ('Org', 'cooperativa', 'org@example.test')"
        )
        org_id = connection.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]
        connection.execute("INSERT INTO personas (nombre) VALUES ('Persona')")
        persona_id = connection.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO necesidades (organizacion_id, titulo) VALUES (?, 'N')",
            (org_id,),
        )
        necesidad_id = connection.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO problemas_colectivos (descripcion, organizacion_id) "
            "VALUES ('Problema sintético', ?)",
            (org_id,),
        )
        problema_id = connection.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO necesidad_problema_colectivo VALUES (?, ?)",
            (necesidad_id, problema_id),
        )
        connection.execute(
            "INSERT INTO problema_participantes_persona VALUES (?, ?)",
            (problema_id, persona_id),
        )
        connection.execute(
            "INSERT INTO problema_participantes_organizacion VALUES (?, ?)",
            (problema_id, org_id),
        )
        connection.commit()

        # Clave compuesta: duplicado rechazado.
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO necesidad_problema_colectivo VALUES (?, ?)",
                (necesidad_id, problema_id),
            )
        connection.rollback()

        # FK: referencia inexistente rechazada.
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO necesidad_problema_colectivo VALUES (99999, ?)",
                (problema_id,),
            )
        connection.rollback()

        # Check: estado inválido rechazado.
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO problemas_colectivos (descripcion, estado, organizacion_id) "
                "VALUES ('Inválido', 'inventado', ?)",
                (org_id,),
            )
        connection.rollback()

        # Check: propietario obligatorio.
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO problemas_colectivos (descripcion) VALUES ('Sin dueño')"
            )
        connection.rollback()

        # ON DELETE CASCADE en la tabla de unión.
        connection.execute(
            "DELETE FROM necesidades WHERE id = ?", (necesidad_id,)
        )
        connection.commit()
        restantes = connection.execute(
            "SELECT COUNT(*) FROM necesidad_problema_colectivo "
            "WHERE necesidad_id = ?",
            (necesidad_id,),
        ).fetchone()[0]
        assert restantes == 0
    finally:
        connection.close()


def test_metadata_incluye_tablas_del_modelo():
    requeridas = {
        "organizaciones",
        "personas",
        "necesidades",
        "problemas_colectivos",
        "necesidad_problema_colectivo",
        "problema_participantes_persona",
        "problema_participantes_organizacion",
        "iniciativas",
        "eventos_auditoria",
    }
    assert requeridas <= set(Base.metadata.tables)


@pytest.mark.skipif(
    not os.getenv("POOLAR_TEST_POSTGRES_URL"),
    reason=(
        "Sin servidor PostgreSQL disponible. La migración objetivo "
        "PostgreSQL sigue pendiente y se documenta en riesgos_pendientes.md."
    ),
)
def test_migracion_postgresql():  # pragma: no cover - requiere servidor real
    """Reservado para cuando exista servidor PostgreSQL y migración objetivo."""
    assert os.getenv("POOLAR_TEST_POSTGRES_URL")


# ---------------------------------------------------------------------------
# 11. Flujo completo y auditoría
# ---------------------------------------------------------------------------
def test_flujo_completo_necesidad_problema_iniciativa(
    client, headers_a, org_a, db_session
):
    # 1. Registrar una necesidad.
    response = client.post(
        "/necesidades",
        params={
            "titulo": "Falta de transporte al centro de salud",
            "descripcion": "Datos sintéticos del piloto",
            "organizacion_id": org_a["org_id"],
            "visibilidad": "privada",
        },
        headers=headers_a,
    )
    assert response.status_code == 201, response.text
    necesidad_id = response.json()["id"]

    # 2. Crear un problema colectivo relacionado.
    response = crear_problema(
        client, headers_a, necesidades_asociadas=[necesidad_id]
    )
    assert response.status_code == 201, response.text
    problema_id = response.json()["id"]

    # 3. Recuperar el problema y comprobar relaciones.
    data = client.get(
        f"/problemas-colectivos/{problema_id}", headers=headers_a
    ).json()
    assert data["necesidades_asociadas"] == [necesidad_id]

    # 4. Crear una iniciativa vinculada al problema.
    response = client.post(
        "/iniciativas",
        params={
            "necesidad_id": necesidad_id,
            "responsable_id": org_a["org_id"],
            "alternativas_evaluadas": (
                "Ruta compartida; servicio contratado; acuerdo comunitario"
            ),
            "criterios_decision": "Costo por usuario y cobertura territorial",
            "presupuesto_estimate": 500.0,
            "plazo": "6 meses",
            "problema_colectivo_id": problema_id,
            "titulo": "Ruta compartida al centro de salud",
        },
        headers=headers_a,
    )
    assert response.status_code == 201, response.text
    iniciativa = response.json()
    assert iniciativa["problema_colectivo_id"] == problema_id

    # 5. Recuperar la iniciativa y comprobar el vínculo.
    response = client.get(
        f"/iniciativas/{iniciativa['id']}", headers=headers_a
    )
    assert response.status_code == 200, response.text
    assert response.json()["problema_colectivo_id"] == problema_id
    assert response.json()["necesidad_id"] == necesidad_id

    # 6. Registrar una decisión y un evento; verificar auditoría.
    response = client.post(
        "/decisiones",
        params={
            "iniciativa_id": iniciativa["id"],
            "tipo_decision": "seleccion_alternativa",
            "alternativa_elegida": "Ruta compartida",
            "motivo": "Menor costo por usuario con cobertura suficiente",
            "responsable_decision": org_a["user_id"],
            "version_metodologia": "v0.6-sintetica",
        },
        headers=headers_a,
    )
    assert response.status_code == 201, response.text

    response = client.post(
        "/eventos",
        params={
            "entidad_referencia": "problema_colectivo",
            "entidad_id": problema_id,
            "tipo_evento": "hito",
            "justificacion": "Iniciativa propuesta y decisión registrada",
        },
        headers=headers_a,
    )
    assert response.status_code == 201, response.text

    eventos = (
        db_session.query(EventoAuditoria)
        .filter(EventoAuditoria.entidad_referencia == "problema_colectivo")
        .all()
    )
    assert len(eventos) >= 2
    assert {evento.tipo_evento for evento in eventos} >= {"inicio", "hito"}
    # Los eventos no copian datos personales.
    for evento in eventos:
        contenido = " ".join(
            filter(
                None,
                [
                    evento.usuario_o_sistema,
                    evento.justificacion,
                    evento.dato_anterior,
                    evento.dato_nuevo,
                ],
            )
        )
        assert "@" not in contenido


def test_exportacion_etiqueta_datos_sinteticos(client, headers_a, org_a, db_session):
    crear_necesidad(db_session, organizacion_id=org_a["org_id"])

    response = client.get("/exportar/necesidades", headers=headers_a)
    assert response.status_code == 200
    data = response.json()
    assert data["synthetic"] is True
    assert "no son resultados reales" in data["nota"].lower()

    response = client.get("/exportar/csv", headers=headers_a)
    assert response.status_code == 200
    assert response.json()["synthetic"] is True