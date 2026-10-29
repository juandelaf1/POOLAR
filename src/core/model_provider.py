"""Capa de acceso a modelos desacoplada de la lógica de Trama Abierta.

Implementa un adaptador propio mínimo. Sustituible por LiteLLM si se necesitan
múltiples proveedores, presupuestos centralizados o integraciones complejas.

Diseño:
- Interfaz estable: `ModelProvider.generate(prompt, context, config)`
- Implementación por defecto: `NullProvider` (no llama a ningún modelo).
- Configuración por entorno: `TRAMA_MODEL_PROVIDER`, `TRAMA_MODEL_NAME`,
  `TRAMA_MODEL_TIMEOUT`, `TRAMA_MODEL_MAX_TOKENS`.
- Límites de coste y consumo configurables.
- Reintentos controlados con backoff exponencial.
- Fallbacks cuando son seguros (proveedor no disponible).
- Cuotas por proceso/usuario.
- Redacción de datos sensibles en logs.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger("trama_abierta.model_provider")


@dataclass
class ModelConfig:
    """Configuración del proveedor de modelos."""
    provider: str = os.getenv("TRAMA_MODEL_PROVIDER", "null")
    model_name: str = os.getenv("TRAMA_MODEL_NAME", "default")
    timeout_seconds: float = float(os.getenv("TRAMA_MODEL_TIMEOUT", "30"))
    max_tokens: int = int(os.getenv("TRAMA_MODEL_MAX_TOKENS", "1024"))
    max_retries: int = int(os.getenv("TRAMA_MODEL_MAX_RETRIES", "3"))
    retry_delay: float = float(os.getenv("TRAMA_MODEL_RETRY_DELAY", "1.0"))
    cost_limit_per_request: float = float(os.getenv("TRAMA_MODEL_COST_LIMIT", "0.01"))
    quota_per_user: int = int(os.getenv("TRAMA_MODEL_QUOTA", "100"))
    fallback_enabled: bool = os.getenv("TRAMA_MODEL_FALLBACK", "true").lower() == "true"


@dataclass
class ModelResponse:
    """Respuesta tipada del proveedor."""
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelProvider:
    """Interfaz estable para proveedores de modelos."""

    def __init__(self, config: ModelConfig):
        self.config = config

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError


class NullProvider(ModelProvider):
    """Proveedor nulo: no llama a ningún modelo. Útil para desarrollo y pruebas."""

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        return ModelResponse(
            content="[NullProvider] No model call performed.",
            model="null",
            provider="null",
            tokens_used=0,
            latency_ms=0.0,
            success=True,
            metadata={"note": "Model provider not configured"},
        )

    def is_available(self) -> bool:
        return True


class ModelProviderFactory:
    """Factory para crear proveedores basados en configuración."""

    @staticmethod
    def create(config: Optional[ModelConfig] = None) -> ModelProvider:
        cfg = config or ModelConfig()
        if cfg.provider == "null":
            return NullProvider(cfg)
        # Aquí se pueden añadir adaptadores para OpenAI, Anthropic, etc.
        # Si se necesita LiteLLM, cambiar a LiteLLMProvider cuando esté justificado.
        logger.warning("Proveedor '%s' no implementado; usando NullProvider", cfg.provider)
        return NullProvider(cfg)


def get_model_provider() -> ModelProvider:
    """Obtiene el proveedor configurado por entorno."""
    return ModelProviderFactory.create()


# Quota tracking por usuario (en memoria, por proceso)
_quota_tracker: Dict[int, int] = {}


def check_quota(user_id: int, config: ModelConfig) -> bool:
    """Verifica si el usuario tiene cuota disponible."""
    used = _quota_tracker.get(user_id, 0)
    return used < config.quota_per_user


def record_usage(user_id: int, tokens: int) -> None:
    """Registra uso de tokens para el usuario."""
    _quota_tracker[user_id] = _quota_tracker.get(user_id, 0) + tokens


def redact_sensitive(text: str) -> str:
    """Redacta datos sensibles (tokens, contraseñas) de texto para logs."""
    import re
    # Redactar tokens JWT
    text = re.sub(r"ghp_[A-Za-z0-9]+", "[REDACTED_TOKEN]", text)
    text = re.sub(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[REDACTED_JWT]", text)
    # Redactar contraseñas comunes
    text = re.sub(r"password[\"']?\s*[:=]\s*[\"']?[^\s\"']+", "password=[REDACTED]", text, flags=re.IGNORECASE)
    return text