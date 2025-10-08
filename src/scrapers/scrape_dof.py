#!/usr/bin/env python3
"""Script principal para extraer publicaciones del DOF.

Este script permite extraer publicaciones del Diario Oficial de la Federación
de manera práctica, con opciones para fechas específicas o rangos de fechas.
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scrapers import DOFScraper
from src.models import LegalDocument, DocumentSource, DocumentType
from src.utils.config import settings
from src.utils.logger import setup_logger
from loguru import logger


def parse_date(date_str: str) -> datetime:
    """Parsea una fecha en formato YYYY-MM-DD.
    
    Args:
        date_str: Fecha en formato YYYY-MM-DD.
        
    Returns:
        Objeto datetime.
        
    Raises:
        ValueError: Si el formato de fecha es inválido.
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Formato de fecha inválido: {date_str}. Use YYYY-MM-DD")


def scrape_single_date(date: datetime, output_dir: Path, get_content: bool = False) -> int:
    """Extrae publicaciones de una fecha específica.
    
    Args:
        date: Fecha a extraer.
        output_dir: Directorio de salida.
        get_content: Si obtener el contenido completo de cada publicación.
        
    Returns:
        Número de publicaciones extraídas.
    """
    logger.info(f"Extrayendo publicaciones del DOF para {date.strftime('%Y-%m-%d')}")
    
    with DOFScraper() as scraper:
        # Obtener lista de publicaciones
        publications = scraper.get_daily_publications(date)
        
        if not publications:
            logger.info(f"No se encontraron publicaciones para {date.strftime('%Y-%m-%d')}")
            return 0
        
        logger.info(f"Encontradas {len(publications)} publicaciones")
        
        # Obtener contenido completo si se solicita
        if get_content:
            logger.info("Obteniendo contenido completo de las publicaciones...")
            
            for i, pub in enumerate(publications):
                try:
                    logger.info(f"Procesando publicación {i+1}/{len(publications)}: {pub.get('title', 'Sin título')[:50]}...")
                    
                    content = scraper.get_publication_content(pub['url'])
                    if content:
                        # Actualizar la publicación con el contenido completo
                        pub.update(content)
                        
                        # Crear objeto LegalDocument
                        legal_doc = LegalDocument(
                            title=pub.get('title', ''),
                            content=pub.get('content', ''),
                            source=DocumentSource.DOF,
                            document_type=DocumentType.OTRO,  # Se podría mejorar la clasificación
                            url=pub.get('url'),
                            publication_date=pub.get('date'),
                            scraped_at=pub.get('scraped_at'),
                            metadata=pub.get('metadata', {})
                        )
                        
                        # Añadir código como metadato
                        if pub.get('codigo'):
                            legal_doc.set_metadata('codigo_dof', pub['codigo'])
                        
                        # Actualizar la publicación con el objeto serializado
                        pub['legal_document'] = legal_doc.dict()
                        
                except Exception as e:
                    logger.error(f"Error procesando publicación {i+1}: {e}")
                    continue
        
        # Guardar publicaciones
        date_dir = output_dir / date.strftime('%Y') / date.strftime('%m')
        scraper.save_publications(publications, date_dir)
        
        logger.info(f"Publicaciones guardadas en: {date_dir}")
        return len(publications)


def scrape_date_range(start_date: datetime, end_date: datetime, output_dir: Path, get_content: bool = False) -> int:
    """Extrae publicaciones de un rango de fechas.
    
    Args:
        start_date: Fecha de inicio.
        end_date: Fecha de fin.
        output_dir: Directorio de salida.
        get_content: Si obtener el contenido completo de cada publicación.
        
    Returns:
        Número total de publicaciones extraídas.
    """
    logger.info(f"Extrayendo publicaciones del DOF desde {start_date.strftime('%Y-%m-%d')} hasta {end_date.strftime('%Y-%m-%d')}")
    
    total_publications = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Solo procesar días laborables (DOF generalmente no publica en fines de semana)
        if current_date.weekday() < 5:  # Lunes a Viernes
            try:
                count = scrape_single_date(current_date, output_dir, get_content)
                total_publications += count
                
                # Pequeña pausa entre fechas
                import time
                time.sleep(settings.scrape_delay)
                
            except Exception as e:
                logger.error(f"Error procesando fecha {current_date.strftime('%Y-%m-%d')}: {e}")
        else:
            logger.debug(f"Saltando fin de semana: {current_date.strftime('%Y-%m-%d')}")
        
        current_date += timedelta(days=1)
    
    logger.info(f"Extracción completada. Total de publicaciones: {total_publications}")
    return total_publications


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Extrae publicaciones del Diario Oficial de la Federación",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python scrape_dof.py --today                    # Extraer publicaciones de hoy
  python scrape_dof.py --yesterday                 # Extraer publicaciones de ayer
  python scrape_dof.py --date 2025-08-13          # Extraer fecha específica
  python scrape_dof.py --start 2025-08-01 --end 2025-08-07  # Rango de fechas
  python scrape_dof.py --today --content          # Incluir contenido completo
  python scrape_dof.py --last-week --output ./mi_directorio  # Directorio personalizado
"""
    )
    
    # Opciones de fecha
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument('--today', action='store_true', help='Extraer publicaciones de hoy')
    date_group.add_argument('--yesterday', action='store_true', help='Extraer publicaciones de ayer')
    date_group.add_argument('--last-week', action='store_true', help='Extraer publicaciones de la última semana')
    date_group.add_argument('--date', type=str, help='Fecha específica (YYYY-MM-DD)')
    date_group.add_argument('--start', type=str, help='Fecha de inicio para rango (YYYY-MM-DD)')
    
    # Opciones adicionales
    parser.add_argument('--end', type=str, help='Fecha de fin para rango (YYYY-MM-DD, requerido con --start)')
    parser.add_argument('--content', action='store_true', help='Obtener contenido completo de las publicaciones')
    parser.add_argument('--output', type=str, help='Directorio de salida (por defecto: data/raw/dof)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mostrar información detallada')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logger()
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # Validar argumentos
    if args.start and not args.end:
        parser.error("--end es requerido cuando se usa --start")
    
    # Determinar directorio de salida
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = settings.data_dir / "raw" / "dof"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Determinar fechas a procesar
        if args.today:
            date = datetime.now()
            total = scrape_single_date(date, output_dir, args.content)
            
        elif args.yesterday:
            date = datetime.now() - timedelta(days=1)
            total = scrape_single_date(date, output_dir, args.content)
            
        elif args.last_week:
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=7)
            total = scrape_date_range(start_date, end_date, output_dir, args.content)
            
        elif args.date:
            date = parse_date(args.date)
            total = scrape_single_date(date, output_dir, args.content)
            
        elif args.start:
            start_date = parse_date(args.start)
            end_date = parse_date(args.end)
            
            if start_date > end_date:
                parser.error("La fecha de inicio debe ser anterior a la fecha de fin")
            
            total = scrape_date_range(start_date, end_date, output_dir, args.content)
        
        # Mostrar resumen
        print(f"\n{'='*60}")
        print(f"RESUMEN DE EXTRACCIÓN")
        print(f"{'='*60}")
        print(f"Total de publicaciones extraídas: {total}")
        print(f"Directorio de salida: {output_dir.absolute()}")
        print(f"Contenido completo: {'Sí' if args.content else 'No'}")
        print(f"{'='*60}")
        
        if total > 0:
            print(f"\n🎉 ¡Extracción completada exitosamente!")
        else:
            print(f"\n⚠️  No se encontraron publicaciones para las fechas especificadas.")
            
    except Exception as e:
        logger.error(f"Error durante la extracción: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()