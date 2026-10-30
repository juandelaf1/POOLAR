"""Puerto de búsqueda semántica para Poolar (Fase P3).

Proporciona una interfaz ABC para búsqueda semántica de necesidades/recursos
conectada a modelos ligeros de embeddings o adaptadores locales.

Inspirado en RAG + pgvector (documentado, pendiente de necesidad demostrada).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SemanticSearchResult:
    """Resultado de búsqueda semántica."""
    entity_type: str  # necesidad, recurso, iniciativa, problema_colectivo
    entity_id: int
    score: float  # similitud coseno [0, 1]
    match_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Embedding:
    """Vector de embedding con metadatos."""
    entity_type: str
    entity_id: int
    vector: List[float]
    model: str
    created_at: str


class SemanticSearchPort(ABC):
    """Puerto para búsqueda semántica de entidades de Poolar.

    Implementaciones posibles:
    - pgvector (PostgreSQL + extensión pgvector)
    - SentenceTransformers + FAISS local
    - OpenAI Embeddings + pgvector
    """

    @abstractmethod
    def upsert_embedding(self, entity_type: str, entity_id: int, text: str, model: str = "local") -> None:
        """Indexa un texto para búsqueda semántica."""
        ...

    @abstractmethod
    def search(self, query: str, entity_types: Optional[List[str]] = None,
               top_k: int = 5, min_score: float = 0.7) -> List[SemanticSearchResult]:
        """Busca entidades semánticamente similares al texto de consulta."""
        ...

    @abstractmethod
    def delete_embedding(self, entity_type: str, entity_id: int) -> None:
        """Elimina el embedding de una entidad."""
        ...


class LocalSemanticSearchService:
    """Implementación local (mock/adaptador) de SemanticSearchPort.

    Usa embeddings simples basados en hash para pruebas y desarrollo sin
    depender de modelos de ML pesados ni de pgvector. No es adecuado para
    producción.
    """

    def __init__(self) -> None:
        self._embeddings: Dict[str, Embedding] = {}  # key: f"{entity_type}:{entity_id}"

    def upsert_embedding(self, entity_type: str, entity_id: int, text: str, model: str = "local") -> None:
        key = f"{entity_type}:{entity_id}"
        vector = self._simple_embedding(text)
        self._embeddings[key] = Embedding(
            entity_type=entity_type,
            entity_id=entity_id,
            vector=vector,
            model=model,
            created_at=str(__import__("datetime").datetime.utcnow()),
        )

    def search(self, query: str, entity_types: Optional[List[str]] = None,
               top_k: int = 5, min_score: float = 0.7) -> List[SemanticSearchResult]:
        query_vec = self._simple_embedding(query)
        results: List[SemanticSearchResult] = []

        for key, emb in self._embeddings.items():
            if entity_types and emb.entity_type not in entity_types:
                continue
            score = self._cosine_similarity(query_vec, emb.vector)
            if score >= min_score:
                results.append(SemanticSearchResult(
                    entity_type=emb.entity_type,
                    entity_id=emb.entity_id,
                    score=round(score, 4),
                    match_reason="local-hash-similarity",
                    metadata={"model": emb.model},
                ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def delete_embedding(self, entity_type: str, entity_id: int) -> None:
        key = f"{entity_type}:{entity_id}"
        self._embeddings.pop(key, None)

    @staticmethod
    def _simple_embedding(text: str) -> List[float]:
        """Embedding determinístico basado en hash (solo para pruebas locales)."""
        import hashlib
        h = hashlib.sha256(text.lower().encode()).hexdigest()
        return [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# Instancia global para uso local/desarrollo
semantic_search_service = LocalSemanticSearchService()
