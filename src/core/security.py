"""Controles de seguridad transversales para Trama Abierta.

- Rate limiting por usuario/IP.
- Validación de argumentos.
- Redacción de datos sensibles en logs.
- Cuotas de consumo.
- Protección frente a inyección de instrucciones.
"""

import os
import time
import re
import logging
from typing import Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger("trama_abierta.security")


# Rate limiting por usuario (en memoria, por proceso)
_rate_limits: Dict[str, list] = defaultdict(list)
_rate_limit_window = 60  # segundos
_rate_limit_max = int(os.getenv("TRAMA_RATE_LIMIT", "60"))  # requests por ventana


def check_rate_limit(user_id: str, endpoint: str) -> bool:
    """Verifica si el usuario no excede el límite de tasa."""
    key = f"{user_id}:{endpoint}"
    now = time.time()
    # Limpiar entradas antiguas
    _rate_limits[key] = [t for t in _rate_limits[key] if now - t < _rate_limit_window]
    if len(_rate_limits[key]) >= _rate_limit_max:
        return False
    _rate_limits[key].append(now)
    return True


def validate_input(data: Dict[str, Any], schema: Dict[str, Any]) -> list:
    """Valida argumentos contra un esquema. Devuelve lista de errores."""
    errors = []
    for field_name, rules in schema.items():
        if field_name not in data:
            if rules.get("required", False):
                errors.append(f"Campo requerido faltante: {field_name}")
            continue
        value = data[field_name]
        if "min_length" in rules and len(str(value)) < rules["min_length"]:
            errors.append(f"{field_name}: longitud mínima {rules['min_length']}")
        if "max_length" in rules and len(str(value)) > rules["max_length"]:
            errors.append(f"{field_name}: longitud máxima {rules['max_length']}")
        if "pattern" in rules and not re.match(rules["pattern"], str(value)):
            errors.append(f"{field_name}: patrón inválido")
        if "type" in rules and not isinstance(value, rules["type"]):
            errors.append(f"{field_name}: tipo inválido")
    return errors


def sanitize_for_log(text: str) -> str:
    """Redacta datos sensibles para logs y trazas."""
    # Redactar tokens
    text = re.sub(r"ghp_[A-Za-z0-9]+", "[REDACTED_TOKEN]", text)
    text = re.sub(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[REDACTED_JWT]", text)
    # Redactar contraseñas
    text = re.sub(r"password[\"']?\s*[:=]\s*[\"']?[^\s\"']+", "password=[REDACTED]", text, flags=re.IGNORECASE)
    # Redactar emails
    text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[REDACTED_EMAIL]", text)
    return text


def check_injection(text: str) -> bool:
    """Detecta patrones de inyección de instrucciones en texto."""
    injection_patterns = [
        r"ignore previous instructions",
        r"disregard above",
        r"forget everything",
        r"system prompt",
        r"you are now",
        r"act as",
        r"pretend to be",
    ]
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def redact_audit_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Redacta campos sensibles de un evento de auditoría antes de persistir."""
    sensitive_keys = {"password", "token", "secret", "hash", "email"}
    redacted = {}
    for key, value in event_data.items():
        if key.lower() in sensitive_keys:
            redacted[key] = "[REDACTED]"
        elif isinstance(value, str):
            redacted[key] = sanitize_for_log(value)
        else:
            redacted[key] = value
    return redacted