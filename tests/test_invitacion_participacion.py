# Pruebas de invitación y participación persistente
import pytest
from src.core.models import Persona, ProblemaColectivo, Invitacion


def test_invitacion_crea_registro_persistente(client, db_session, org_a, headers_a):
    """Verifica que una invitación crea un registro persistente en la BD."""
    from src.core.models import Organizacion, Necesidad
    # Crear persona destinataria
    persona = Persona(nombre="Destinatario", email="dest@test.local", activo=True)
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    # Crear necesidad y problema
    necesidad = Necesidad(titulo="Necesidad test", descripcion="Desc", organizacion_id=org_a["org_id"], visibilidad="compartible", estado="propuesta")
    db_session.add(necesidad)
    db_session.commit()
    db_session.refresh(necesidad)
    # Crear problema colectivo
    problema = ProblemaColectivo(descripcion="Problema test para invitación", estado="detectado", origen_datos="synthetic_pilot", organizacion_id=org_a["org_id"], creado_por_id=org_a["user_id"])
    problema.necesidades_asociadas = [necesidad]
    db_session.add(problema)
    db_session.commit()
    db_session.refresh(problema)
    # Enviar invitación
    r = client.post(f"/problemas-colectivos/{problema.id}/invitaciones", json={"persona_id": persona.id, "mensaje": "Invitación test"}, headers=headers_a)
    assert r.status_code == 201
    assert r.json()["estado"] == "pendiente"
    # Verificar persistencia
    inv = db_session.query(Invitacion).filter(Invitacion.problema_colectivo_id == problema.id).first()
    assert inv is not None
    assert inv.estado == "pendiente"
    assert inv.destinatario_id == persona.id


def test_invitacion_rechaza_duplicados(client, db_session, org_a, headers_a):
    """Verifica que no se crean invitaciones duplicadas pendientes."""
    from src.core.models import Necesidad
    persona = Persona(nombre="Dup", email="dup@test.local", activo=True)
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    necesidad = Necesidad(titulo="Necesidad dup", descripcion="Desc", organizacion_id=org_a["org_id"], visibilidad="compartible", estado="propuesta")
    db_session.add(necesidad)
    db_session.commit()
    db_session.refresh(necesidad)
    problema = ProblemaColectivo(descripcion="Problema dup", estado="detectado", origen_datos="synthetic_pilot", organizacion_id=org_a["org_id"], creado_por_id=org_a["user_id"])
    problema.necesidades_asociadas = [necesidad]
    db_session.add(problema)
    db_session.commit()
    db_session.refresh(problema)
    # Primera invitación
    r1 = client.post(f"/problemas-colectivos/{problema.id}/invitaciones", json={"persona_id": persona.id}, headers=headers_a)
    assert r1.status_code == 201
    # Segunda invitación (duplicada)
    r2 = client.post(f"/problemas-colectivos/{problema.id}/invitaciones", json={"persona_id": persona.id}, headers=headers_a)
    assert r2.status_code == 400


def test_participacion_requiere_invitacion_pendiente(client, db_session, org_a, headers_a):
    """Verifica que la participación requiere invitación pendiente."""
    from src.core.models import Necesidad
    persona = Persona(nombre="NoInv", email="noinv@test.local", activo=True)
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    necesidad = Necesidad(titulo="Necesidad noinv", descripcion="Desc", organizacion_id=org_a["org_id"], visibilidad="compartible", estado="propuesta")
    db_session.add(necesidad)
    db_session.commit()
    db_session.refresh(necesidad)
    problema = ProblemaColectivo(descripcion="Problema noinv", estado="detectado", origen_datos="synthetic_pilot", organizacion_id=org_a["org_id"], creado_por_id=org_a["user_id"])
    problema.necesidades_asociadas = [necesidad]
    db_session.add(problema)
    db_session.commit()
    db_session.refresh(problema)
    # Intentar aceptar sin invitación
    r = client.post(f"/problemas-colectivos/{problema.id}/participaciones", json={"persona_id": persona.id, "aceptar": True}, headers=headers_a)
    assert r.status_code == 403