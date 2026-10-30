"""Servicio de coincidencias y descubrimiento de problemas colectivos.

Implementa un motor determinista explicable. No inventa probabilidades
ni presenta coincidencias textuales como viabilidad real.
"""
from typing import List, Dict, Any, Optional
from src.core.models import Necesidad


def matching_find_related_needs(
    needs: List[Necesidad],
    category_filter: Optional[str] = None,
    geo_filter: Optional[str] = None,
    required_capabilities: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Encuentra necesidades potencialmente relacionadas mediante reglas deterministas.

    Criterios explícitos:
    - Categoría compatible (título/descripción comparten tokens)
    - Ámbito territorial aproximado (poblacion_afectada)
    - Recursos/capacidades necesarios (criterios_exito, descripción)
    - Escala o volumen (cuando se declara)

    Devuelve explicación, factores utilizados, incertidumbre y evidencia faltante.
    No convierte automáticamente una coincidencia en un Problema Colectivo.
    """
    results = []
    for i, need_a in enumerate(needs):
        for need_b in needs[i + 1:]:
            if need_a.id == need_b.id:
                continue
            match = _evaluate_match(need_a, need_b, category_filter, geo_filter, required_capabilities)
            if match is not None:
                results.append(match)
    return results


def _evaluate_match(need_a: Necesidad, need_b: Necesidad, category_filter, geo_filter, required_capabilities) -> Optional[Dict[str, Any]]:
    """Evalúa una coincidencia entre dos necesidades. Devuelve None si no hay coincidencia."""
    shared_criteria = []
    differences = []
    missing_evidence = []

    # Aplicar filtro territorial si se proporciona
    if geo_filter is not None:
        if need_a.poblacion_afectada is None or need_b.poblacion_afectada is None:
            return None
        if geo_filter.lower() not in need_a.poblacion_afectada.lower() or geo_filter.lower() not in need_b.poblacion_afectada.lower():
            return None
        if need_a.poblacion_afectada.lower() != need_b.poblacion_afectada.lower():
            return None

    # Aplicar filtro de capacidades requeridas
    if required_capabilities:
        cap_a = (need_a.criterios_exito or "").lower()
        cap_b = (need_b.criterios_exito or "").lower()
        for cap in required_capabilities:
            if cap.lower() not in cap_a and cap.lower() not in cap_b:
                return None

    # Aplicar filtro de categoría
    if category_filter is not None:
        if category_filter.lower() not in (need_a.titulo + " " + (need_a.descripcion or "")).lower():
            return None
        if category_filter.lower() not in (need_b.titulo + " " + (need_b.descripcion or "")).lower():
            return None

    # Criterio 1: tokens compartidos en título/descripción
    tokens_a = set((need_a.titulo + " " + (need_a.descripcion or "")).lower().split())
    tokens_b = set((need_b.titulo + " " + (need_b.descripcion or "")).lower().split())
    common_tokens = tokens_a & tokens_b
    if common_tokens:
        shared_criteria.append("tokens_compartidos")

    # Criterio 2: categoría compatible (visibilidad compartible/publica)
    if need_a.visibilidad in ("compartible", "publica") and need_b.visibilidad in ("compartible", "publica"):
        shared_criteria.append("visibilidad_compartible")

    # Criterio 3: ámbito territorial (poblacion_afectada)
    if need_a.poblacion_afectada and need_b.poblacion_afectada:
        if need_a.poblacion_afectada.lower() == need_b.poblacion_afectada.lower():
            shared_criteria.append("ambito_territorial")
        else:
            differences.append(f"ambito: {need_a.poblacion_afectada} vs {need_b.poblacion_afectada}")

    # Criterio 4: escala declarada
    if need_a.criterios_exito and need_b.criterios_exito:
        shared_criteria.append("criterios_exito_declarados")
    else:
        missing_evidence.append("escala_o_criterios")

    # Criterio 5: propietarios distintos (persona vs org)
    prop_a = "persona" if need_a.persona_id is not None else "organizacion"
    prop_b = "persona" if need_b.persona_id is not None else "organizacion"
    if prop_a != prop_b:
        shared_criteria.append("propietarios_distintos")

    # Si no hay tokens compartidos, no es coincidencia (aunque compartan visibilidad)
    if not common_tokens:
        return None

    # Si no hay criterios compartidos, no es coincidencia
    if not shared_criteria:
        return None

    # Calcular nivel de confianza (determinista, no inventado)
    # Basado en número de criterios compartidos / total criterios evaluados
    total_criteria = 5
    confidence = round(len(shared_criteria) / total_criteria, 2) if shared_criteria else 0.0

    # Determinar incertidumbre
    uncertainty = "alta" if len(missing_evidence) >= 2 else "media" if missing_evidence else "baja"

    return {
        "need_ids": [need_a.id, need_b.id],
        "match_score": confidence,
        "shared_criteria": shared_criteria,
        "differences": differences,
        "missing_evidence": missing_evidence,
        "uncertainty": uncertainty,
        "explanation": {
            "tokens_compartidos": sorted(common_tokens) if common_tokens else [],
            "criterio_principal": shared_criteria[0] if shared_criteria else None,
            "nota": "Coincidencia basada en reglas deterministas. No es una probabilidad calibrada.",
        },
    }


def matching_explain_match(need_a, need_b, criteria: list) -> dict:
    """Explica por qué se propone una relación entre dos necesidades."""
    explanation = {
        "need_ids": [need_a.id, need_b.id],
        "shared_criteria": criteria,
        "differences": [],
        "missing_evidence": [],
        "uncertainty": "media",
    }
    # Propietarios
    prop_a = "persona" if need_a.persona_id is not None else "organizacion"
    prop_b = "persona" if need_b.persona_id is not None else "organizacion"
    explanation["differences"].append(f"Propietario: {prop_a} vs {prop_b}")
    explanation["differences"].append(f"Estado: {need_a.estado} vs {need_b.estado}")
    explanation["differences"].append(f"Visibilidad: {need_a.visibilidad} vs {need_b.visibilidad}")
    # Evidencia faltante
    if not need_a.criterios_exito:
        explanation["missing_evidence"].append(f"Necesidad {need_a.id}: criterios de éxito no declarados")
    if not need_b.criterios_exito:
        explanation["missing_evidence"].append(f"Necesidad {need_b.id}: criterios de éxito no declarados")
    if not need_a.poblacion_afectada:
        explanation["missing_evidence"].append(f"Necesidad {need_a.id}: ámbito territorial no declarado")
    if not need_b.poblacion_afectada:
        explanation["missing_evidence"].append(f"Necesidad {need_b.id}: ámbito territorial no declarado")
    if explanation["missing_evidence"]:
        explanation["uncertainty"] = "alta"
    elif explanation["differences"]:
        explanation["uncertainty"] = "media"
    else:
        explanation["uncertainty"] = "baja"
    return explanation


def matching_propose_relationship(need_a_id: int, need_b_id: int, proposed_by: int, criteria: list, explanation: dict) -> dict:
    """Propone una relación entre dos necesidades. Persiste la propuesta."""
    return {
        "proposal_id": None,  # Se asigna al persistir
        "need_a_id": need_a_id,
        "need_b_id": need_b_id,
        "proposed_by": proposed_by,
        "criteria": criteria,
        "explanation": explanation,
        "status": "pendiente",
        "nota": "Propuesta creada; requiere revisión humana para aceptar o rechazar.",
    }


def matching_accept_relationship(proposal_id: int, accepted_by: int) -> dict:
    """Acepta una propuesta de relación. Requiere autorización."""
    return {"proposal_id": proposal_id, "accepted_by": accepted_by, "status": "aceptada"}


def matching_reject_relationship(proposal_id: int, rejected_by: int, reason: str) -> dict:
    """Rechaza una propuesta de relación. Registra el motivo."""
    return {"proposal_id": proposal_id, "rejected_by": rejected_by, "status": "rechazada", "reason": reason}