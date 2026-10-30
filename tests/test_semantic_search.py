# Pruebas del puerto de búsqueda semántica (Fase P3)
from src.core.ports.semantic import (
    SemanticSearchPort,
    Embedding,
    SemanticSearchResult,
    LocalSemanticSearchService,
    semantic_search_service,
)


def test_semantic_search_upsert():
    """Verifica que los embeddings se insertan correctamente."""
    svc = LocalSemanticSearchService()
    svc.upsert_embedding("necesidad", 1, "Necesidad de educación gratuita", "local")
    svc.upsert_embedding("recurso", 1, "Recurso: curso de Python", "local")

    embeddings = svc._embeddings
    assert "necesidad:1" in embeddings
    emb = embeddings["necesidad:1"]
    assert isinstance(emb, Embedding)
    assert emb.entity_type == "necesidad"
    assert emb.entity_id == 1
    assert emb.model == "local"
    assert len(emb.vector) == 16


def test_semantic_search_search_same_text():
    """Verifica que textos similares tienen alta similitud."""
    svc = LocalSemanticSearchService()
    svc.upsert_embedding("necesidad", 1, "Necesidad de educación gratuita", "local")
    results = svc.search("educación gratuita para niños", entity_types=["necesidad"], top_k=5)
    assert len(results) >= 1
    result = results[0]
    assert result.entity_type == "necesidad"
    assert result.entity_id == 1
    assert result.score > 0.5  # Debe coincidir bien con palabras comunes


def test_semantic_search_search_different_entity_types():
    """Verifica la búsqueda solo devuelve tipos especificados."""
    svc = LocalSemanticSearchService()
    svc.upsert_embedding("necesidad", 1, "Necesidad de educación", "local")
    svc.upsert_embedding("recurso", 2, "Recurso de educación", "local")
    results = svc.search("educación", entity_types=["necesidad"], top_k=5)
    assert len(results) == 1
    assert results[0].entity_type == "necesidad"


def test_semantic_search_delete_embedding():
    """Verifica que delete_embedding elimina el embedding."""
    svc = LocalSemanticSearchService()
    svc.upsert_embedding("necesidad", 99, "Eliminar", "local")
    assert "necesidad:99" in svc._embeddings
    svc.delete_embedding("necesidad", 99)
    assert "necesidad:99" not in svc._embeddings


def test_semantic_search_result_structure():
    """Verifica que la estructura de SemanticSearchResult es correcta."""
    result = SemanticSearchResult(
        entity_type="necesidad",
        entity_id=5,
        score=0.95,
        match_reason="perfecto",
        metadata={"modelo": "bert"},
    )
    assert result.entity_type == "necesidad"
    assert result.entity_id == 5
    assert result.score == 0.95
    assert result.match_reason == "perfecto"
    assert result.metadata["modelo"] == "bert"


def test_semantic_search_cosine_similarity():
    """Verifica el cálculo de similitud coseno (implementación auxiliar)."""
    from src.core.ports.semantic import LocalSemanticSearchService
    a = [1.0, 0.0, 0.0]
    b = [0.9, 0.1, 0.0]
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    expected = dot / (norm_a * norm_b)
    got = LocalSemanticSearchService._cosine_similarity(a, b)
    assert abs(got - expected) < 1e-10


def test_semantic_search_simple_embedding():
    """Verifica que el embedding simple es determinístico."""
    from src.core.ports.semantic import LocalSemanticSearchService
    t1 = LocalSemanticSearchService._simple_embedding("test")
    t2 = LocalSemanticSearchService._simple_embedding("test")
    assert t1 == t2
    t3 = LocalSemanticSearchService._simple_embedding("different")
    assert t1 != t3