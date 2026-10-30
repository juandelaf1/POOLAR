"""Observabilidad desacoplada para Trama Abierta.

Soporta:
- Sin observabilidad (por defecto).
- OpenTelemetry (trazas locales).
- LangSmith (opcional, desactivado por defecto).

Principios:
- No registrar datos sensibles.
- Redactar información privada.
- LangSmith es opcional y desactivado por defecto.
- La aplicación funciona sin credenciales de observabilidad.
"""
import os
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger("trama_abierta.observability")


class ObservabilityProvider(str, Enum):
    NONE = "none"
    OPENTELEMETRY = "opentelemetry"
    LANGSMITH = "langsmith"


class ObservabilityAdapter:
    """Adaptador de observabilidad desacoplado."""

    def __init__(self):
        self.provider = ObservabilityProvider(os.getenv("TRAMA_OBSERVABILITY_PROVIDER", "none"))
        self.enabled = os.getenv("TRAMA_OBSERVABILITY_ENABLED", "false").lower() == "true"
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY", "")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "trama-abierta")
        self.langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        self.redact_sensitive = os.getenv("TRAMA_OBSERVABILITY_REDACT", "true").lower() == "true"

    def is_enabled(self) -> bool:
        return self.enabled and self.provider != ObservabilityProvider.NONE

    def trace_start(self, execution_id: str, metadata: Dict[str, Any]) -> None:
        """Inicia una traza."""
        if not self.is_enabled():
            return
        safe_metadata = self._redact(metadata)
        logger.info("Trace start: %s %s", execution_id, safe_metadata)

    def trace_end(self, execution_id: str, result: Dict[str, Any]) -> None:
        """Finaliza una traza."""
        if not self.is_enabled():
            return
        safe_result = self._redact(result)
        logger.info("Trace end: %s %s", execution_id, safe_result)

    def trace_tool_call(self, execution_id: str, tool_name: str, inputs: Dict[str, Any], output: Dict[str, Any]) -> None:
        """Registra una llamada a herramienta."""
        if not self.is_enabled():
            return
        safe_inputs = self._redact(inputs)
        safe_output = self._redact(output)
        logger.info("Tool call: %s %s inputs=%s output=%s", execution_id, tool_name, safe_inputs, safe_output)

    def _redact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redacta datos sensibles."""
        if not self.redact_sensitive:
            return data
        from src.core.security import sanitize_for_log
        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = sanitize_for_log(value)
            elif isinstance(value, dict):
                redacted[key] = self._redact(value)
            else:
                redacted[key] = value
        return redacted


# Adaptador global
observability = ObservabilityAdapter()