#!/usr/bin/env python3
"""Punto de entrada principal del Asistente Legal Mexicano."""

import asyncio
from pathlib import Path
from loguru import logger

# Importar configuración y logging
from src.utils.config import settings
from src.utils.logger import setup_logger


def create_directories() -> None:
    """Crea los directorios necesarios para el proyecto."""
    directories = [
        settings.data_dir,
        settings.logs_dir,
        settings.data_dir / "raw",
        settings.data_dir / "processed",
        settings.data_dir / "embeddings"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado/verificado: {directory}")


async def main() -> None:
    """Función principal del proyecto."""
    logger.info("Iniciando Asistente Legal Mexicano v0.1.0")
    
    try:
        # Crear directorios necesarios
        create_directories()
        
        # Verificar configuración
        logger.info(f"Configuración cargada:")
        logger.info(f"  - API Host: {settings.api_host}:{settings.api_port}")
        logger.info(f"  - Debug Mode: {settings.api_debug}")
        logger.info(f"  - Log Level: {settings.log_level}")
        logger.info(f"  - Chunk Size: {settings.chunk_size}")
        logger.info(f"  - Embedding Model: {settings.embedding_model}")
        
        # TODO: Inicializar componentes del sistema
        # - Base de datos vectorial
        # - Scrapers
        # - API
        
        logger.success("Sistema inicializado correctamente")
        
    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        raise


if __name__ == "__main__":
    # Configurar logging
    setup_logger()
    
    # Ejecutar función principal
    asyncio.run(main())