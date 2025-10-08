#!/usr/bin/env python3
"""Script principal para extraer documentos del Orden Jurídico Nacional.

Este script permite extraer leyes y reglamentos federales del sitio
ordenjuridico.gob.mx mediante URLs específicas.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List
from loguru import logger

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.orden_juridico_scraper import OrdenJuridicoScraper
from src.utils.logger import setup_logger
from src.utils.config import settings


def scrape_urls(urls: List[str], output_dir: Path, extract_content: bool = True) -> int:
    """Extrae documentos de una lista de URLs.
    
    Args:
        urls: Lista de URLs a extraer.
        output_dir: Directorio donde guardar los documentos.
        extract_content: Si extraer el contenido completo.
        
    Returns:
        Número de documentos extraídos exitosamente.
    """
    logger.info(f"Iniciando extracción de {len(urls)} URLs del Orden Jurídico Nacional")
    logger.info(f"Directorio de salida: {output_dir}")
    logger.info(f"Contenido completo: {'Sí' if extract_content else 'No'}")
    
    scraper = OrdenJuridicoScraper()
    
    try:
        # Extraer documentos
        documents = scraper.scrape_multiple_documents(urls, extract_content)
        
        if documents:
            # Guardar documentos
            scraper.save_documents(documents, output_dir)
            
            logger.success(f"✓ Extraídos y guardados {len(documents)} documentos")
            
            # Mostrar resumen
            logger.info("\n=== RESUMEN DE DOCUMENTOS EXTRAÍDOS ===")
            for i, doc in enumerate(documents, 1):
                logger.info(f"{i}. {doc.title}")
                logger.info(f"   - ID: {doc.id}")
                logger.info(f"   - Tipo: {doc.document_type}")
                logger.info(f"   - Fecha publicación: {doc.publication_date}")
                logger.info(f"   - Tamaño contenido: {len(doc.content)} caracteres")
                logger.info(f"   - URL: {doc.url}")
                logger.info("")
            
            return len(documents)
        else:
            logger.warning("No se pudieron extraer documentos")
            return 0
            
    except Exception as e:
        logger.error(f"Error durante la extracción: {e}")
        return 0


def scrape_from_file(file_path: Path, output_dir: Path, extract_content: bool = True) -> int:
    """Extrae documentos de URLs listadas en un archivo.
    
    Args:
        file_path: Archivo con URLs (una por línea).
        output_dir: Directorio donde guardar los documentos.
        extract_content: Si extraer el contenido completo.
        
    Returns:
        Número de documentos extraídos exitosamente.
    """
    logger.info(f"Leyendo URLs desde: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        logger.info(f"Encontradas {len(urls)} URLs en el archivo")
        
        if not urls:
            logger.warning("No se encontraron URLs válidas en el archivo")
            return 0
        
        return scrape_urls(urls, output_dir, extract_content)
        
    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {file_path}")
        return 0
    except Exception as e:
        logger.error(f"Error leyendo archivo: {e}")
        return 0


def validate_urls(urls: List[str]) -> List[str]:
    """Valida que las URLs sean del dominio correcto.
    
    Args:
        urls: Lista de URLs a validar.
        
    Returns:
        Lista de URLs válidas.
    """
    valid_urls = []
    
    for url in urls:
        if 'ordenjuridico.gob.mx' in url and url.endswith('.html'):
            valid_urls.append(url)
        else:
            logger.warning(f"URL no válida ignorada: {url}")
    
    return valid_urls


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Extrae documentos del Orden Jurídico Nacional",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ejemplos de uso:
  # Extraer documentos específicos
  python scrape_orden_juridico.py --urls https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html
  
  # Extraer desde archivo de URLs
  python scrape_orden_juridico.py --file urls.txt
  
  # Extraer sin contenido completo (solo metadatos)
  python scrape_orden_juridico.py --urls URL1 URL2 --no-content
  
  # Especificar directorio de salida
  python scrape_orden_juridico.py --file urls.txt --output /ruta/personalizada
"""
    )
    
    # Argumentos principales
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--urls', nargs='+', help='URLs específicas a extraer')
    group.add_argument('--file', type=str, help='Archivo con URLs (una por línea)')
    
    # Opciones
    parser.add_argument('--output', type=str, help='Directorio de salida (por defecto: data/raw/orden_juridico)')
    parser.add_argument('--no-content', action='store_true', help='No extraer contenido completo (solo metadatos)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mostrar información detallada')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logger()
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # Determinar directorio de salida
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = settings.data_dir / "raw" / "orden_juridico"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info("=== SCRAPER DEL ORDEN JURÍDICO NACIONAL ===")
        logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
        total_extracted = 0
        
        if args.urls:
            # Validar URLs
            valid_urls = validate_urls(args.urls)
            
            if not valid_urls:
                logger.error("No se proporcionaron URLs válidas")
                sys.exit(1)
            
            logger.info(f"URLs válidas: {len(valid_urls)} de {len(args.urls)}")
            
            # Extraer documentos
            total_extracted = scrape_urls(
                valid_urls, 
                output_dir, 
                extract_content=not args.no_content
            )
            
        elif args.file:
            # Extraer desde archivo
            total_extracted = scrape_from_file(
                Path(args.file), 
                output_dir, 
                extract_content=not args.no_content
            )
        
        # Resumen final
        logger.info("=" * 50)
        if total_extracted > 0:
            logger.success(f"🎉 ¡Extracción completada exitosamente!")
            logger.info(f"Documentos extraídos: {total_extracted}")
            logger.info(f"Directorio de salida: {output_dir}")
            
            # Mostrar archivos guardados
            saved_files = list(output_dir.glob("*.json"))
            if saved_files:
                logger.info(f"Archivos guardados: {len(saved_files)}")
                for file in saved_files[-5:]:  # Mostrar últimos 5
                    size_kb = file.stat().st_size / 1024
                    logger.info(f"  - {file.name} ({size_kb:.1f} KB)")
                if len(saved_files) > 5:
                    logger.info(f"  ... y {len(saved_files) - 5} archivos más")
        else:
            logger.warning("❌ No se extrajeron documentos")
            logger.info("Verifica las URLs y la conectividad")
        
    except KeyboardInterrupt:
        logger.warning("\nExtracción interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error general: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()