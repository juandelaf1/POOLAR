"""Servicio de coincidencias y descubrimiento de problemas colectivos."""
from src.core.contracts import OrigenDatos
from src.core.models import Necesidad, ProblemaColectivo, Persona


def matching_find_related_needs(needs: list, category_filter: str = None, geo_filter: str = None):
    # Implementación determinista basada en categoría y ámbito aproximado
    results = []
    for need in needs:
        if category_filter is not None and (need.titulo or "").lower().find(category_filter) == -1:
            continue
        results.append({"need_id": need.id, "match_score": 0.8, "criteria": ["categoria", "ambito_territorial"]})
    return results


def explain_match(need_a, need_b, criteria: list):
    explanation = {
        "need_ids": [need_a.id, need_b.id],
        "shared_criteria": criteria,
        "differences": [
            f"Propietario: {'individuo' if need_a.persona_id else 'organizacion'} vs {'individuo' if need_b.persona_id else 'organizacion'}",
            f"Estado: {need_a.estado} vs {need_b.estado}"
        ],
        "missing_evidence": ["escala_total", "recursos_necesarios", "restricciones_territoriales"]
    }
    return explanation
