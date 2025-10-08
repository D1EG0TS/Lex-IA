#!/usr/bin/env python3
"""Script para generar un documento con enlaces a leyes y reglamentos federales.

Este script crea un documento con enlaces organizados de leyes y reglamentos
federales del Orden Jurídico Nacional de México.
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import re
from urllib.parse import urljoin, urlparse
from loguru import logger


class GeneradorEnlacesLeyes:
    """Generador de enlaces a leyes y reglamentos federales."""
    
    def __init__(self):
        """Inicializa el generador de enlaces."""
        self.base_url = "https://www.ordenjuridico.gob.mx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
        })
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def obtener_enlaces_desde_documentos_existentes(self, directorio_documentos: Path) -> Dict[str, List[Dict]]:
        """Obtiene enlaces de los documentos ya descargados.
        
        Args:
            directorio_documentos: Directorio con documentos JSON descargados.
            
        Returns:
            Diccionario con enlaces organizados por categoría.
        """
        enlaces = {
            'leyes_federales': [],
            'reglamentos_federales': [],
            'decretos': [],
            'otros': []
        }
        
        # Buscar archivos JSON en el directorio
        for archivo_json in directorio_documentos.rglob('*.json'):
            try:
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    documento = json.load(f)
                
                # Extraer información del documento
                enlace_info = {
                    'titulo': documento.get('title', 'Sin título'),
                    'url': documento.get('url', ''),
                    'id': documento.get('id', ''),
                    'tipo': documento.get('document_type', 'otro'),
                    'fecha_publicacion': documento.get('publication_date', ''),
                    'fuente': documento.get('source', 'ORDEN_JURIDICO')
                }
                
                # Clasificar por tipo
                tipo = documento.get('document_type', 'otro').lower()
                if tipo == 'ley':
                    enlaces['leyes_federales'].append(enlace_info)
                elif tipo == 'reglamento':
                    enlaces['reglamentos_federales'].append(enlace_info)
                elif tipo == 'decreto':
                    enlaces['decretos'].append(enlace_info)
                else:
                    enlaces['otros'].append(enlace_info)
                    
            except Exception as e:
                logger.warning(f"Error procesando {archivo_json}: {e}")
                
        return enlaces
    
    def extraer_enlaces_desde_web(self, url_leyes: str = None) -> Dict[str, List[Dict]]:
        """Extrae enlaces directamente del sitio web.
        
        Args:
            url_leyes: URL de la página de leyes (opcional).
            
        Returns:
            Diccionario con enlaces extraídos del sitio web.
        """
        if not url_leyes:
            url_leyes = f"{self.base_url}/leyes.php"
            
        enlaces_web = {
            'leyes_federales': [],
            'reglamentos_federales': []
        }
        
        try:
            logger.info(f"Extrayendo enlaces de: {url_leyes}")
            response = self.session.get(url_leyes, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar todos los enlaces que apunten a documentos
            enlaces_encontrados = soup.find_all('a', href=re.compile(r'wo\d+\.html'))
            
            for enlace in enlaces_encontrados:
                href = enlace.get('href')
                texto = enlace.get_text(strip=True)
                
                if href and texto:
                    # Construir URL completa
                    url_completa = urljoin(self.base_url, href)
                    
                    # Extraer código del documento
                    codigo_match = re.search(r'wo(\d+)\.html', href)
                    codigo = codigo_match.group(1) if codigo_match else ''
                    
                    enlace_info = {
                        'titulo': texto,
                        'url': url_completa,
                        'id': f'wo{codigo}' if codigo else '',
                        'codigo': codigo,
                        'fuente': 'WEB_SCRAPING'
                    }
                    
                    # Clasificar por contexto (esto es una aproximación)
                    if any(palabra in texto.lower() for palabra in ['ley', 'código']):
                        enlaces_web['leyes_federales'].append(enlace_info)
                    elif 'reglamento' in texto.lower():
                        enlaces_web['reglamentos_federales'].append(enlace_info)
                        
        except Exception as e:
            logger.error(f"Error extrayendo enlaces del web: {e}")
            
        return enlaces_web
    
    def generar_enlaces_conocidos(self) -> Dict[str, List[Dict]]:
        """Genera enlaces basándose en documentos conocidos y patrones comunes.
        
        Returns:
            Diccionario con enlaces de documentos conocidos.
        """
        enlaces_conocidos = {
            'leyes_federales': [
                {
                    'titulo': 'Constitución Política de los Estados Unidos Mexicanos',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo14166.html',
                    'id': 'wo14166',
                    'tipo': 'constitucion',
                    'descripcion': 'Carta Magna de México'
                },
                {
                    'titulo': 'Ley General de Educación',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo39036.html',
                    'id': 'wo39036',
                    'tipo': 'ley',
                    'descripcion': 'Ley que regula la educación en México'
                },
                {
                    'titulo': 'Ley General de Educación Superior',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo124400.html',
                    'id': 'wo124400',
                    'tipo': 'ley',
                    'descripcion': 'Ley que regula la educación superior'
                },
                {
                    'titulo': 'Ley de Amparo',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo6028.html',
                    'id': 'wo6028',
                    'tipo': 'ley',
                    'descripcion': 'Ley que regula los artículos 103 y 107 constitucionales'
                },
                {
                    'titulo': 'Ley Orgánica del Congreso General',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo16815.html',
                    'id': 'wo16815',
                    'tipo': 'ley',
                    'descripcion': 'Ley que regula el funcionamiento del Congreso'
                },
                {
                    'titulo': 'Ley General de Instituciones y Procedimientos Electorales',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo95383.html',
                    'id': 'wo95383',
                    'tipo': 'ley',
                    'descripcion': 'Ley electoral federal'
                },
                {
                    'titulo': 'Ley de Asistencia Social',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo11034.html',
                    'id': 'wo11034',
                    'tipo': 'ley',
                    'descripcion': 'Ley que regula la asistencia social'
                }
            ],
            'reglamentos_federales': [
                {
                    'titulo': 'Reglamento General de Deberes Militares',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html',
                    'id': 'wo17186',
                    'tipo': 'reglamento',
                    'descripcion': 'Reglamento militar federal'
                },
                {
                    'titulo': 'Reglamento de la Cámara de Diputados',
                    'url': 'https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html',
                    'id': 'wo88408',
                    'tipo': 'reglamento',
                    'descripcion': 'Reglamento interno de la Cámara de Diputados'
                }
            ]
        }
        
        return enlaces_conocidos
    
    def generar_documento_enlaces(self, output_file: Path) -> None:
        """Genera un documento completo con todos los enlaces organizados.
        
        Args:
            output_file: Archivo donde guardar el documento de enlaces.
        """
        logger.info("Generando documento de enlaces a leyes y reglamentos federales")
        
        # Obtener enlaces de diferentes fuentes
        enlaces_documentos = self.obtener_enlaces_desde_documentos_existentes(
            Path('documentos_legales')
        )
        enlaces_web = self.extraer_enlaces_desde_web()
        enlaces_conocidos = self.generar_enlaces_conocidos()
        
        # Combinar todos los enlaces
        todos_los_enlaces = {
            'metadata': {
                'titulo': 'Enlaces a Leyes y Reglamentos Federales de México',
                'descripcion': 'Documento generado automáticamente con enlaces organizados del Orden Jurídico Nacional',
                'fecha_generacion': datetime.now().isoformat(),
                'fuente': 'Orden Jurídico Nacional - ordenjuridico.gob.mx',
                'total_enlaces': 0
            },
            'leyes_federales': [],
            'reglamentos_federales': [],
            'decretos': [],
            'otros': []
        }
        
        # Combinar enlaces evitando duplicados
        enlaces_unicos = set()
        
        for categoria in ['leyes_federales', 'reglamentos_federales', 'decretos', 'otros']:
            # Agregar enlaces de documentos existentes
            for enlace in enlaces_documentos.get(categoria, []):
                if enlace['url'] not in enlaces_unicos:
                    todos_los_enlaces[categoria].append(enlace)
                    enlaces_unicos.add(enlace['url'])
            
            # Agregar enlaces conocidos
            for enlace in enlaces_conocidos.get(categoria, []):
                if enlace['url'] not in enlaces_unicos:
                    todos_los_enlaces[categoria].append(enlace)
                    enlaces_unicos.add(enlace['url'])
        
        # Agregar enlaces del web
        for categoria in ['leyes_federales', 'reglamentos_federales']:
            for enlace in enlaces_web.get(categoria, []):
                if enlace['url'] not in enlaces_unicos:
                    todos_los_enlaces[categoria].append(enlace)
                    enlaces_unicos.add(enlace['url'])
        
        # Calcular total
        total = sum(len(todos_los_enlaces[cat]) for cat in ['leyes_federales', 'reglamentos_federales', 'decretos', 'otros'])
        todos_los_enlaces['metadata']['total_enlaces'] = total
        
        # Guardar documento
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(todos_los_enlaces, f, indent=2, ensure_ascii=False)
        
        logger.success(f"Documento de enlaces generado: {output_file}")
        logger.info(f"Total de enlaces: {total}")
        logger.info(f"Leyes federales: {len(todos_los_enlaces['leyes_federales'])}")
        logger.info(f"Reglamentos federales: {len(todos_los_enlaces['reglamentos_federales'])}")
        logger.info(f"Decretos: {len(todos_los_enlaces['decretos'])}")
        logger.info(f"Otros: {len(todos_los_enlaces['otros'])}")
    
    def generar_archivo_urls_para_scraper(self, output_file: Path, max_urls: int = 100) -> None:
        """Genera un archivo de URLs para usar con el scraper.
        
        Args:
            output_file: Archivo donde guardar las URLs.
            max_urls: Número máximo de URLs a incluir.
        """
        logger.info(f"Generando archivo de URLs para scraper: {output_file}")
        
        # Obtener enlaces conocidos
        enlaces_conocidos = self.generar_enlaces_conocidos()
        
        urls = []
        urls.append("# URLs de leyes y reglamentos federales para el scraper")
        urls.append("# Generado automáticamente")
        urls.append(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        urls.append("")
        
        # Agregar URLs de leyes federales
        urls.append("# LEYES FEDERALES")
        for enlace in enlaces_conocidos.get('leyes_federales', [])[:max_urls//2]:
            urls.append(f"# {enlace['titulo']}")
            urls.append(enlace['url'])
            urls.append("")
        
        # Agregar URLs de reglamentos federales
        urls.append("# REGLAMENTOS FEDERALES")
        for enlace in enlaces_conocidos.get('reglamentos_federales', [])[:max_urls//2]:
            urls.append(f"# {enlace['titulo']}")
            urls.append(enlace['url'])
            urls.append("")
        
        # Guardar archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(urls))
        
        logger.success(f"Archivo de URLs generado: {output_file}")


def main():
    """Función principal."""
    generador = GeneradorEnlacesLeyes()
    
    # Generar documento de enlaces
    output_enlaces = Path('enlaces_leyes_reglamentos.json')
    generador.generar_documento_enlaces(output_enlaces)
    
    # Generar archivo de URLs para scraper
    output_urls = Path('urls_leyes_reglamentos_completo.txt')
    generador.generar_archivo_urls_para_scraper(output_urls)
    
    print(f"\n✓ Documentos generados:")
    print(f"  - Enlaces organizados: {output_enlaces}")
    print(f"  - URLs para scraper: {output_urls}")


if __name__ == "__main__":
    main()