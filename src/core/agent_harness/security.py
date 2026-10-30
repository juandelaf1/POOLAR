"""Límites de seguridad para el Agent Harness de Poolar."""
import os
import time
from typing import Dict, Any, Optional
from collections import defaultdict

# Límites configurables por entorno
MAX_ITERATIONS = int(os.getenv("POOLAR_HARNESS_MAX_ITERATIONS", "10"))
MAX_TOOL_CALLS = int(os.getenv("POOLAR_HARNESS_MAX_TOOL_CALLS", "50"))
TIMEOUT_SECONDS = int(os.getenv("POOLAR_HARNESS_TIMEOUT", "300"))
TOKEN_BUDGET = int(os.getenv("POOLAR_HARNESS_TOKEN_BUDGET", "4096"))
COST_BUDGET = float(os.getenv("POOLAR_HARNESS_COST_BUDGET", "0.10"))
MAX_RETRIES = int(os.getenv("POOLAR_HARNESS_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("POOLAR_HARNESS_RETRY_DELAY", "1.0"))
RATE_LIMIT_WINDOW = int(os.getenv("POOLAR_HARNESS_RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_MAX = int(os.getenv("POOLAR_HARNESS_RATE_LIMIT_MAX", "30"))

# Tracking de ejecuciones
_execution_tracking: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    "tool_calls": 0,
    "iterations": 0,
    "tokens_used": 0,
    "cost_used": 0.0,
    "start_time": 0.0,
})


def init_execution(execution_id: str) -> None:
    """Inicializa el tracking de una ejecución."""
    _execution_tracking[execution_id] = {
        "tool_calls": 0,
        "iterations": 0,
        "tokens_used": 0,
        "cost_used": 0.0,
        "start_time": time.time(),
    }


def check_iteration_limit(execution_id: str) -> bool:
    """Verifica si se ha excedido el límite de iteraciones."""
    tracking = _execution_tracking[execution_id]
    return tracking["iterations"] < MAX_ITERATIONS


def check_tool_call_limit(execution_id: str) -> bool:
    """Verifica si se ha excedido el límite de llamadas a herramientas."""
    tracking = _execution_tracking[execution_id]
    return tracking["tool_calls"] < MAX_TOOL_CALLS


def check_timeout(execution_id: str) -> bool:
    """Verifica si se ha excedido el timeout."""
    tracking = _execution_tracking[execution_id]
    elapsed = time.time() - tracking["start_time"]
    return elapsed < TIMEOUT_SECONDS


def check_budget(execution_id: str, tokens: int, cost: float) -> bool:
    """Verifica si se ha excedido el presupuesto."""
    tracking = _execution_tracking[execution_id]
    return (tracking["tokens_used"] + tokens <= TOKEN_BUDGET and
            tracking["cost_used"] + cost <= COST_BUDGET)


def record_tool_call(execution_id: str, tokens: int = 0, cost: float = 0.0) -> None:
    """Registra una llamada a herramienta."""
    tracking = _execution_tracking[execution_id]
    tracking["tool_calls"] += 1
    tracking["tokens_used"] += tokens
    tracking["cost_used"] += cost


def record_iteration(execution_id: str) -> None:
    """Registra una iteración."""
    tracking = _execution_tracking[execution_id]
    tracking["iterations"] += 1


def get_tracking(execution_id: str) -> Dict[str, Any]:
    """Obtiene el estado de tracking de una ejecución."""
    return _execution_tracking.get(execution_id, {})


def cleanup_execution(execution_id: str) -> None:
    """Limpia el tracking de una ejecución completada."""
    _execution_tracking.pop(execution_id, None)