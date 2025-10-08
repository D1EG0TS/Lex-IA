#!/usr/bin/env python3
"""Script de prueba para el scraper del Orden Jurídico Nacional.

Este script prueba la funcionalidad del OrdenJuridicoScraper con URLs específicas
de leyes y reglamentos federales.
"""

import sys
from pathlib import Path
from loguru import logger

# Agregar el directorio raíz al path para importaciones
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar desde src
from src.scrapers.orden_juridico_scraper import OrdenJuridicoScraper
from src.utils.logger import setup_logger


def test_specific_urls():
    """Prueba el scraper con URLs específicas del Orden Jurídico Nacional."""
    logger.info("=== Prueba de URLs específicas del Orden Jurídico Nacional ===")
    
    # URLs de ejemplo proporcionadas por el usuario
    test_urls = [
        "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html",
        "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html"
    ]
    
    scraper = OrdenJuridicoScraper()
    
    for i, url in enumerate(test_urls, 1):
        logger.info(f"\n--- Probando URL {i}: {url} ---")
        
        try:
            # Extraer documento sin contenido completo primero
            document = scraper.scrape_document_by_url(url, extract_content=False)
            
            if document:
                logger.success(f"✓ Documento extraído exitosamente:")
                logger.info(f"  - ID: {document.document_id}")
                logger.info(f"  - Título: {document.title[:100]}...")
                logger.info(f"  - Tipo: {document.document_type}")
                logger.info(f"  - Fuente: {document.source}")
                logger.info(f"  - Fecha publicación: {document.publication_date}")
                logger.info(f"  - URL: {document.url}")
                
                # Ahora extraer con contenido completo
                logger.info("Extrayendo contenido completo...")
                document_with_content = scraper.scrape_document_by_url(url, extract_content=True)
                
                if document_with_content and document_with_content.content:
                    content_preview = document_with_content.content[:500].replace('\n', ' ')
                    logger.info(f"  - Contenido (preview): {content_preview}...")
                    logger.info(f"  - Longitud del contenido: {len(document_with_content.content)} caracteres")
                else:
                    logger.warning("  - No se pudo extraer contenido")
                    
            else:
                logger.error(f"✗ No se pudo extraer el documento de {url}")
                
        except Exception as e:
            logger.error(f"✗ Error procesando {url}: {e}")


def test_multiple_documents():
    """Prueba la extracción de múltiples documentos."""
    logger.info("\n=== Prueba de extracción múltiple ===")
    
    test_urls = [
        "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html",
        "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html"
    ]
    
    scraper = OrdenJuridicoScraper()
    
    try:
        documents = scraper.scrape_multiple_documents(test_urls, extract_content=False)
        
        logger.info(f"Extraídos {len(documents)} documentos de {len(test_urls)} URLs")
        
        for i, doc in enumerate(documents, 1):
            logger.info(f"Documento {i}: {doc.title[:50]}... (Tipo: {doc.document_type})")
            
        return documents
        
    except Exception as e:
        logger.error(f"Error en extracción múltiple: {e}")
        return []


def test_save_documents():
    """Prueba el guardado de documentos."""
    logger.info("\n=== Prueba de guardado de documentos ===")
    
    test_urls = [
        "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html",
        "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html"
    ]
    
    scraper = OrdenJuridicoScraper()
    
    try:
        # Extraer documentos
        documents = scraper.scrape_multiple_documents(test_urls, extract_content=True)
        
        if documents:
            # Crear directorio de salida
            output_dir = Path("data/raw/orden_juridico/test")
            
            # Guardar documentos
            scraper.save_documents(documents, output_dir)
            
            logger.success(f"✓ Documentos guardados en {output_dir}")
            
            # Verificar archivos guardados
            saved_files = list(output_dir.glob("*.json"))
            logger.info(f"Archivos guardados: {len(saved_files)}")
            
            for file in saved_files:
                logger.info(f"  - {file.name} ({file.stat().st_size} bytes)")
        else:
            logger.warning("No se extrajeron documentos para guardar")
            
    except Exception as e:
        logger.error(f"Error guardando documentos: {e}")


def main():
    """Función principal de pruebas."""
    # Configurar logging
    setup_logger()
    
    logger.info("Iniciando pruebas del OrdenJuridicoScraper")
    logger.info("=" * 60)
    
    try:
        # Ejecutar pruebas
        test_specific_urls()
        test_multiple_documents()
        test_save_documents()
        
        logger.success("\n✓ Todas las pruebas completadas")
        
    except KeyboardInterrupt:
        logger.warning("\nPruebas interrumpidas por el usuario")
    except Exception as e:
        logger.error(f"\nError general en las pruebas: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()