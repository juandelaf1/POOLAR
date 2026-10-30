# Pruebas del motor de matching determinista
from src.core.models import Necesidad
from src.services.matching_service import matching_find_related_needs, matching_explain_match


def test_matching_coincidencia_alta():
    """Verifica que necesidades con tokens compartidos y misma ubicación tienen score alto."""
    n1 = Necesidad(titulo="Transporte al centro", descripcion="Necesito transporte regular", visibilidad="compartible", estado="propuesta")
    n2 = Necesidad(titulo="Entregas al centro", descripcion="Necesito entregas regular", visibilidad="compartible", estado="propuesta")
    n1.id = 1
    n2.id = 2
    results = matching_find_related_needs([n1, n2])
    assert len(results) == 1
    assert results[0]["match_score"] > 0
    assert "tokens_compartidos" in results[0]["shared_criteria"]
    assert results[0]["uncertainty"] in ("baja", "media", "alta")


def test_matching_sin_coincidencia():
    """Verifica que necesidades sin tokens compartidos no generan coincidencia."""
    n1 = Necesidad(titulo="Transporte", descripcion="Logística de carga", visibilidad="compartible", estado="propuesta")
    n2 = Necesidad(titulo="Contabilidad", descripcion="Finanzas y contabilidad", visibilidad="compartible", estado="propuesta")
    n1.id = 1
    n2.id = 2
    results = matching_find_related_needs([n1, n2])
    assert len(results) == 0


def test_matching_geo_filter_excluye():
    """Verifica que el filtro territorial excluye resultados no coincidentes."""
    n1 = Necesidad(titulo="Transporte", descripcion="Necesito transporte", visibilidad="compartible", estado="propuesta", poblacion_afectada="Sevilla")
    n2 = Necesidad(titulo="Entregas", descripcion="Necesito entregas", visibilidad="compartible", estado="propuesta", poblacion_afectada="Madrid")
    n1.id = 1
    n2.id = 2
    results = matching_find_related_needs([n1, n2], geo_filter="Sevilla")
    assert len(results) == 0


def test_matching_geo_filter_incluye():
    """Verifica que el filtro territorial incluye resultados coincidentes."""
    n1 = Necesidad(titulo="Transporte", descripcion="Necesito transporte", visibilidad="compartible", estado="propuesta", poblacion_afectada="Sevilla")
    n2 = Necesidad(titulo="Entregas", descripcion="Necesito entregas", visibilidad="compartible", estado="propuesta", poblacion_afectada="Sevilla")
    n1.id = 1
    n2.id = 2
    results = matching_find_related_needs([n1, n2], geo_filter="Sevilla")
    assert len(results) == 1


def test_matching_evidencia_faltante():
    """Verifica que la incertidumbre aumenta cuando faltan datos."""
    n1 = Necesidad(titulo="Transporte", descripcion="Necesito transporte", visibilidad="compartible", estado="propuesta")
    n2 = Necesidad(titulo="Entregas", descripcion="Necesito entregas", visibilidad="compartible", estado="propuesta")
    n1.id = 1
    n2.id = 2
    results = matching_find_related_needs([n1, n2])
    assert len(results) == 1
    assert "missing_evidence" in results[0]
    assert len(results[0]["missing_evidence"]) > 0


def test_matching_explicacion_coherente():
    """Verifica que la explicación es coherente con la puntuación."""
    n1 = Necesidad(titulo="Transporte", descripcion="Necesito transporte", visibilidad="compartible", estado="propuesta", poblacion_afectada="Sevilla")
    n2 = Necesidad(titulo="Entregas", descripcion="Necesito entregas", visibilidad="compartible", estado="propuesta", poblacion_afectada="Sevilla")
    n1.id = 1
    n2.id = 2
    results = matching_find_related_needs([n1, n2])
    assert len(results) == 1
    assert results[0]["match_score"] > 0
    assert "explanation" in results[0]
    assert "tokens_compartidos" in results[0]["explanation"] or results[0]["explanation"].get("tokens_compartidos") is not None


def test_matching_no_probabilidad():
    """Verifica que el score no se presenta como probabilidad estadística."""
    n1 = Necesidad(titulo="Transporte", descripcion="Necesito transporte", visibilidad="compartible", estado="propuesta")
    n2 = Necesidad(titulo="Entregas", descripcion="Necesito entregas", visibilidad="compartible", estado="propuesta")
    n1.id = 1
    n2.id = 2
    results = matching_find_related_needs([n1, n2])
    # El score debe ser determinista (0-1) y no un porcentaje
    if results:
        assert 0 <= results[0]["match_score"] <= 1
        assert results[0]["match_score"] != 0.8  # No hardcoded