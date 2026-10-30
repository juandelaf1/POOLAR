# Pruebas del servicio de geografía y optimización
from src.core.ports.geo import GeoPoint, SimpleGeoService, SimpleOptimizationService


def test_geo_proximity_haversine():
    """Verifica que la distancia Haversine se calcula correctamente."""
    geo = SimpleGeoService()
    a = GeoPoint(lat=40.4168, lon=-3.7038)  # Madrid
    b = GeoPoint(lat=37.3891, lon=-5.9845)  # Sevilla
    dist = geo.proximity(a, b)
    assert dist is not None
    assert 380 < dist < 420  # ~390 km Madrid-Sevilla


def test_geo_zone_coverage():
    """Verifica que la cobertura de zona devuelve resultados."""
    geo = SimpleGeoService()
    point = GeoPoint(lat=40.4168, lon=-3.7038)
    zones = geo.zone_coverage(point, 10.0)
    assert len(zones) == 1
    assert "zone_" in zones[0]


def test_geo_match_by_detour():
    """Verifica que el matching por desvío devuelve resultado estructurado."""
    geo = SimpleGeoService()
    origin = GeoPoint(lat=40.4168, lon=-3.7038)
    dest = GeoPoint(lat=37.3891, lon=-5.9845)
    match = geo.match_by_detour(origin, dest, 100.0)
    assert match.distance_km is not None
    assert match.source == "haversine"
    assert "ruta real" in match.note.lower() or "osrm" in match.note.lower()


def test_optimization_calculate_route():
    """Verifica que el cálculo de ruta devuelve estructura completa."""
    opt = SimpleOptimizationService()
    origin = GeoPoint(lat=40.4168, lon=-3.7038)
    dest = GeoPoint(lat=37.3891, lon=-5.9845)
    route = opt.calculate_route(origin, dest)
    assert "distance_km" in route
    assert "duration_min" in route
    assert "source" in route
    assert route["source"] == "haversine"


def test_optimization_identify_gaps():
    """Verifica que se identifican gaps de capacidad."""
    opt = SimpleOptimizationService()
    demands = [{"required_capacity": 100}]
    available = [{"capacity": 30}]
    gaps = opt.identify_gaps(demands, available)
    assert len(gaps) == 1
    assert gaps[0]["gap"] == 70


def test_optimization_no_gaps():
    """Verifica que no hay gaps cuando la capacidad es suficiente."""
    opt = SimpleOptimizationService()
    demands = [{"required_capacity": 50}]
    available = [{"capacity": 100}]
    gaps = opt.identify_gaps(demands, available)
    assert len(gaps) == 0