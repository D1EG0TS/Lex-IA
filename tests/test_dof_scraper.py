#!/usr/bin/env python3
"""Script de prueba para el scraper del DOF.

Este script prueba la funcionalidad básica del scraper del Diario Oficial
de la Federación para verificar que puede extraer publicaciones correctamente.
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.scrapers import DOFScraper
from src.utils.config import settings
from src.utils.logger import setup_logger


def test_dof_scraper():
    """Prueba básica del scraper del DOF."""
    setup_logger()
    from loguru import logger
    logger.info("Iniciando prueba del scraper del DOF")
    
    try:
        # Crear instancia del scraper
        with DOFScraper() as scraper:
            logger.info("Scraper del DOF inicializado correctamente")
            
            # Probar obtener publicaciones de hoy
            logger.info("Probando obtener publicaciones de hoy...")
            today_publications = scraper.get_daily_publications()
            
            logger.info(f"Publicaciones encontradas hoy: {len(today_publications)}")
            
            if today_publications:
                # Mostrar información de las primeras publicaciones
                for i, pub in enumerate(today_publications[:3]):
                    logger.info(f"Publicación {i+1}:")
                    logger.info(f"  Título: {pub.get('title', 'N/A')[:100]}...")
                    logger.info(f"  URL: {pub.get('url', 'N/A')}")
                    logger.info(f"  Código: {pub.get('codigo', 'N/A')}")
                    logger.info(f"  Fecha: {pub.get('date', 'N/A')}")
                    print()
                
                # Probar obtener contenido de la primera publicación
                if today_publications[0].get('url'):
                    logger.info("Probando obtener contenido de la primera publicación...")
                    content = scraper.get_publication_content(today_publications[0]['url'])
                    
                    if content:
                        logger.info(f"Contenido obtenido:")
                        logger.info(f"  Título: {content.get('title', 'N/A')[:100]}...")
                        logger.info(f"  Contenido: {len(content.get('content', ''))} caracteres")
                        logger.info(f"  Metadatos: {len(content.get('metadata', {}))} elementos")
                    else:
                        logger.warning("No se pudo obtener el contenido de la publicación")
            else:
                logger.info("No se encontraron publicaciones para hoy")
                
                # Probar con fecha anterior (ayer)
                yesterday = datetime.now() - timedelta(days=1)
                logger.info(f"Probando con fecha anterior: {yesterday.strftime('%Y-%m-%d')}")
                
                yesterday_publications = scraper.get_daily_publications(yesterday)
                logger.info(f"Publicaciones encontradas ayer: {len(yesterday_publications)}")
                
                if yesterday_publications:
                    for i, pub in enumerate(yesterday_publications[:2]):
                        logger.info(f"Publicación ayer {i+1}:")
                        logger.info(f"  Título: {pub.get('title', 'N/A')[:100]}...")
                        logger.info(f"  URL: {pub.get('url', 'N/A')}")
            
            # Probar guardar publicaciones si hay alguna
            all_publications = today_publications + (yesterday_publications if 'yesterday_publications' in locals() else [])
            
            if all_publications:
                logger.info(f"Guardando {len(all_publications)} publicaciones...")
                output_dir = Path("test_output")
                scraper.save_publications(all_publications, output_dir)
                logger.info(f"Publicaciones guardadas en: {output_dir.absolute()}")
            
            logger.info("Prueba del scraper del DOF completada exitosamente")
            
    except Exception as e:
        logger.error(f"Error durante la prueba del scraper: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    
    return True


def test_configuration():
    """Prueba la configuración del proyecto."""
    setup_logger()
    from loguru import logger
    logger.info("Probando configuración del proyecto...")
    
    try:
        logger.info(f"URL base DOF: {settings.dof_base_url}")
        logger.info(f"User Agent: {settings.user_agent}")
        logger.info(f"Delay entre requests: {settings.scrape_delay}s")
        logger.info(f"Timeout de requests: {settings.request_timeout}s")
        logger.info(f"Máximo reintentos: {settings.max_retries}")
        logger.info(f"Directorio de datos: {settings.data_dir}")
        
        logger.info("Configuración cargada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error en la configuración: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DEL SCRAPER DEL DOF")
    print("=" * 60)
    print()
    
    # Probar configuración
    print("1. Probando configuración...")
    config_ok = test_configuration()
    print(f"   Configuración: {'✓ OK' if config_ok else '✗ ERROR'}")
    print()
    
    if config_ok:
        # Probar scraper
        print("2. Probando scraper del DOF...")
        scraper_ok = test_dof_scraper()
        print(f"   Scraper DOF: {'✓ OK' if scraper_ok else '✗ ERROR'}")
        print()
        
        if scraper_ok:
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
            print("El scraper del DOF está listo para usar.")
        else:
            print("❌ Hubo errores en las pruebas del scraper.")
            print("Revisa los logs para más detalles.")
    else:
        print("❌ Error en la configuración. No se pueden ejecutar más pruebas.")
    
    print()
    print("=" * 60)