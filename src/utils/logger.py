"""Configuración de logging para el proyecto."""

import sys
from pathlib import Path
from loguru import logger
from .config import settings


def setup_logger() -> None:
    """Configura el sistema de logging del proyecto."""
    
    # Remover el handler por defecto
    logger.remove()
    
    # Crear directorio de logs si no existe
    logs_dir = Path(settings.logs_dir)
    logs_dir.mkdir(exist_ok=True)
    
    # Configurar formato de logs
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Handler para consola
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Handler para archivo
    logger.add(
        settings.log_file,
        format=log_format,
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Handler para errores críticos
    logger.add(
        logs_dir / "errors.log",
        format=log_format,
        level="ERROR",
        rotation="5 MB",
        retention="60 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("Sistema de logging configurado correctamente")


# Configurar logger al importar el módulo
setup_logger()