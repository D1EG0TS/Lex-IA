"""Módulo de utilidades para el asistente legal.

Contiene:
- Funciones de procesamiento de texto
- Utilidades de logging
- Helpers para embeddings
- Configuración y validación
"""

from .config import Settings
from .logger import setup_logger

__all__ = ["Settings", "setup_logger"]