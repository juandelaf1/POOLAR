# Pruebas del servicio de evidencias
from src.core.ports.evidence import Evidence, EvidenceService


def test_evidence_valida():
    """Verifica que una evidencia válida se registra correctamente."""
    ev = Evidence(
        source="https://example.com/source",
        value=42,
        unit="km",
        entity_type="necesidad",
        entity_id=1,
        verification_status="observed",
    )
    svc = EvidenceService()
    result = svc.register(ev)
    assert result.id is not None
    assert result.hash_fingerprint is not None
    assert result.verification_status == "observed"


def test_evidence_sin_fuente_rechazada():
    """Verifica que una evidencia sin fuente es rechazada."""
    ev = Evidence(
        value=42,
        unit="km",
        entity_type="necesidad",
        entity_id=1,
    )
    svc = EvidenceService()
    try:
        svc.register(ev)
        assert False, "Debería haber lanzado ValueError"
    except ValueError as e:
        assert "Fuente" in str(e)


def test_evidence_sin_entidad_rechazada():
    """Verifica que una evidencia sin entidad es rechazada."""
    ev = Evidence(
        source="https://example.com",
        value=42,
        unit="km",
    )
    svc = EvidenceService()
    try:
        svc.register(ev)
        assert False, "Debería haber lanzado ValueError"
    except ValueError as e:
        assert "entidad" in str(e).lower() or "entity" in str(e).lower()


def test_evidence_get_by_entity():
    """Verifica que se pueden obtener evidencias por entidad."""
    svc = EvidenceService()
    ev1 = Evidence(source="src1", value=10, unit="km", entity_type="necesidad", entity_id=1, verification_status="observed")
    ev2 = Evidence(source="src2", value=20, unit="km", entity_type="necesidad", entity_id=2, verification_status="observed")
    svc.register(ev1)
    svc.register(ev2)
    results = svc.get_by_entity("necesidad", 1)
    assert len(results) == 1
    assert results[0].value == 10


def test_evidence_fingerprint_determinista():
    """Verifica que el fingerprint es determinista."""
    ev1 = Evidence(source="src", value=42, unit="km", entity_type="necesidad", entity_id=1)
    ev2 = Evidence(source="src", value=42, unit="km", entity_type="necesidad", entity_id=1)
    fp1 = ev1.compute_fingerprint()
    fp2 = ev2.compute_fingerprint()
    assert fp1 == fp2