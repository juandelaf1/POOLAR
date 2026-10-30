"""Puertos de geografía y optimización para Poolar.

Inspirado en EnRuta, DashLogistics, GeoRisk_Finder y Anexo_Risk.
"""
import math
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class GeoPoint:
    """Punto geográfico."""
    lat: float
    lon: float
    label: Optional[str] = None


@dataclass
class GeoMatch:
    """Resultado de una coincidencia geográfica."""
    distance_km: Optional[float] = None
    route_available: bool = False
    detour_km: Optional[float] = None
    source: str = ""
    note: str = ""


class GeoPort(ABC):
    """Puerto para consultas espaciales."""

    @abstractmethod
    def proximity(self, point_a: GeoPoint, point_b: GeoPoint) -> Optional[float]:
        """Distancia entre dos puntos en km."""
        ...

    @abstractmethod
    def zone_coverage(self, point: GeoPoint, radius_km: float) -> List[str]:
        """Zonas cubiertas por un punto con radio."""
        ...

    @abstractmethod
    def match_by_detour(self, origin: GeoPoint, destination: GeoPoint, capacity: float) -> GeoMatch:
        """Matching por desvío de ruta y capacidad."""
        ...


class OptimizationPort(ABC):
    """Puerto para optimización de rutas, horarios y capacidades."""

    @abstractmethod
    def calculate_route(self, origin: GeoPoint, destination: GeoPoint) -> Dict[str, Any]:
        """Calcula una ruta con distancia y duración."""
        ...

    @abstractmethod
    def optimize_assignment(self, demands: List[Dict], resources: List[Dict]) -> Dict[str, Any]:
        """Optimiza asignación de recursos a demandas."""
        ...

    @abstractmethod
    def identify_gaps(self, demands: List[Dict], available: List[Dict]) -> List[Dict]:
        """Identifica capacidades faltantes."""
        ...


class SimpleGeoService:
    """Implementación simple de GeoPort (sin dependencias externas).

    Usa fórmula de Haversine para distancia. No requiere PostGIS.
    """

    def proximity(self, point_a: GeoPoint, point_b: GeoPoint) -> Optional[float]:
        """Distancia Haversine en km."""
        R = 6371  # Radio de la Tierra en km
        lat1, lon1 = math.radians(point_a.lat), math.radians(point_a.lon)
        lat2, lon2 = math.radians(point_b.lat), math.radians(point_b.lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def zone_coverage(self, point: GeoPoint, radius_km: float) -> List[str]:
        """Zonas cubiertas (simplificado)."""
        return [f"zone_{point.lat:.2f}_{point.lon:.2f}_r{radius_km}"]

    def match_by_detour(self, origin: GeoPoint, destination: GeoPoint, capacity: float) -> GeoMatch:
        """Matching por desvío (simplificado)."""
        dist = self.proximity(origin, destination)
        return GeoMatch(
            distance_km=dist,
            route_available=dist is not None and dist < 100,
            detour_km=None,
            source="haversine",
            note="Distancia lineal; ruta real requiere OSRM o similar.",
        )


class SimpleOptimizationService:
    """Implementación simple de OptimizationPort."""

    def calculate_route(self, origin: GeoPoint, destination: GeoPoint) -> Dict[str, Any]:
        geo = SimpleGeoService()
        dist = geo.proximity(origin, destination)
        return {
            "origin": (origin.lat, origin.lon),
            "destination": (destination.lat, destination.lon),
            "distance_km": dist,
            "duration_min": round(dist * 2) if dist else None,
            "source": "haversine",
            "note": "Estimación basada en distancia lineal; ruta real requiere OSRM.",
        }

    def optimize_assignment(self, demands: List[Dict], resources: List[Dict]) -> Dict[str, Any]:
        """Optimización simple: asigna recursos a demandas por orden."""
        assignments = []
        for i, demand in enumerate(demands):
            resource = resources[i % len(resources)] if resources else None
            assignments.append({
                "demand": demand,
                "resource": resource,
                "note": "Asignación por orden; optimización real requiere OR-Tools.",
            })
        return {"assignments": assignments, "note": "Asignación simplificada."}

    def identify_gaps(self, demands: List[Dict], available: List[Dict]) -> List[Dict]:
        """Identifica capacidades faltantes."""
        gaps = []
        for demand in demands:
            required = demand.get("required_capacity", 0)
            avail = sum(r.get("capacity", 0) for r in available)
            if avail < required:
                gaps.append({
                    "demand": demand,
                    "required": required,
                    "available": avail,
                    "gap": required - avail,
                })
        return gaps


# Instancias globales
geo_service = SimpleGeoService()
optimization_service = SimpleOptimizationService()