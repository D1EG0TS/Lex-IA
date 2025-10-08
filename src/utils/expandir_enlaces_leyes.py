#!/usr/bin/env python3
"""Script para expandir la lista de enlaces extrayendo más documentos del Orden Jurídico.

Este script busca más enlaces en diferentes secciones del sitio web del Orden Jurídico Nacional.
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
import time


class ExpandirEnlacesLeyes:
    """Expandir la lista de enlaces a leyes y reglamentos federales."""
    
    def __init__(self):
        """Inicializa el expandidor de enlaces."""
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
        
    def buscar_enlaces_en_seccion(self, url_seccion: str, nombre_seccion: str) -> List[Dict]:
        """Busca enlaces en una sección específica del sitio.
        
        Args:
            url_seccion: URL de la sección a explorar.
            nombre_seccion: Nombre descriptivo de la sección.
            
        Returns:
            Lista de enlaces encontrados.
        """
        enlaces_encontrados = []
        
        try:
            logger.info(f"Explorando sección: {nombre_seccion} - {url_seccion}")
            response = self.session.get(url_seccion, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces a documentos (patrón wo####.html)
            enlaces = soup.find_all('a', href=re.compile(r'wo\d+\.html'))
            
            for enlace in enlaces:
                href = enlace.get('href')
                texto = enlace.get_text(strip=True)
                
                if href and texto and len(texto) > 5:  # Filtrar textos muy cortos
                    # Construir URL completa
                    url_completa = urljoin(self.base_url, href)
                    
                    # Extraer código del documento
                    codigo_match = re.search(r'wo(\d+)\.html', href)
                    codigo = codigo_match.group(1) if codigo_match else ''
                    
                    enlace_info = {
                        'titulo': texto.strip(),
                        'url': url_completa,
                        'id': f'wo{codigo}' if codigo else '',
                        'codigo': codigo,
                        'seccion': nombre_seccion,
                        'fuente': 'WEB_SCRAPING_EXPANDIDO',
                        'fecha_extraccion': datetime.now().isoformat()
                    }
                    
                    enlaces_encontrados.append(enlace_info)
            
            logger.info(f"Encontrados {len(enlaces_encontrados)} enlaces en {nombre_seccion}")
            
        except Exception as e:
            logger.error(f"Error explorando {nombre_seccion}: {e}")
            
        return enlaces_encontrados
    
    def explorar_multiples_secciones(self) -> Dict[str, List[Dict]]:
        """Explora múltiples secciones del sitio web.
        
        Returns:
            Diccionario con enlaces organizados por sección.
        """
        secciones_a_explorar = [
            {
                'url': f'{self.base_url}/ambfed.php',
                'nombre': 'Ámbito Federal',
                'categoria': 'federal'
            },
            {
                'url': f'{self.base_url}/leyes.php',
                'nombre': 'Leyes y Reglamentos',
                'categoria': 'leyes_reglamentos'
            },
            # Agregar más secciones según sea necesario
        ]
        
        todos_los_enlaces = {
            'federal': [],
            'leyes_reglamentos': [],
            'otros': []
        }
        
        for seccion in secciones_a_explorar:
            enlaces = self.buscar_enlaces_en_seccion(
                seccion['url'], 
                seccion['nombre']
            )
            
            categoria = seccion.get('categoria', 'otros')
            todos_los_enlaces[categoria].extend(enlaces)
            
            # Pausa entre peticiones
            time.sleep(2)
        
        return todos_los_enlaces
    
    def clasificar_documentos_por_tipo(self, enlaces: List[Dict]) -> Dict[str, List[Dict]]:
        """Clasifica los documentos por tipo basándose en su título.
        
        Args:
            enlaces: Lista de enlaces a clasificar.
            
        Returns:
            Diccionario con enlaces clasificados por tipo.
        """
        clasificados = {
            'leyes_federales': [],
            'reglamentos_federales': [],
            'decretos': [],
            'acuerdos': [],
            'normas': [],
            'otros': []
        }
        
        for enlace in enlaces:
            titulo_lower = enlace.get('titulo', '').lower()
            
            # Clasificar por palabras clave en el título
            if any(palabra in titulo_lower for palabra in ['ley ', 'código']):
                enlace['tipo_documento'] = 'ley'
                clasificados['leyes_federales'].append(enlace)
            elif 'reglamento' in titulo_lower:
                enlace['tipo_documento'] = 'reglamento'
                clasificados['reglamentos_federales'].append(enlace)
            elif 'decreto' in titulo_lower:
                enlace['tipo_documento'] = 'decreto'
                clasificados['decretos'].append(enlace)
            elif 'acuerdo' in titulo_lower:
                enlace['tipo_documento'] = 'acuerdo'
                clasificados['acuerdos'].append(enlace)
            elif any(palabra in titulo_lower for palabra in ['norma', 'nom-']):
                enlace['tipo_documento'] = 'norma'
                clasificados['normas'].append(enlace)
            else:
                enlace['tipo_documento'] = 'otro'
                clasificados['otros'].append(enlace)
        
        return clasificados
    
    def generar_documento_expandido(self, archivo_base: Path, archivo_expandido: Path) -> None:
        """Genera un documento expandido combinando enlaces existentes con nuevos.
        
        Args:
            archivo_base: Archivo JSON base con enlaces existentes.
            archivo_expandido: Archivo donde guardar la versión expandida.
        """
        logger.info("Generando documento expandido de enlaces")
        
        # Cargar enlaces existentes si el archivo existe
        enlaces_existentes = {
            'leyes_federales': [],
            'reglamentos_federales': [],
            'decretos': [],
            'acuerdos': [],
            'normas': [],
            'otros': []
        }
        
        if archivo_base.exists():
            try:
                with open(archivo_base, 'r', encoding='utf-8') as f:
                    datos_base = json.load(f)
                    for categoria in enlaces_existentes.keys():
                        if categoria in datos_base:
                            enlaces_existentes[categoria] = datos_base[categoria]
            except Exception as e:
                logger.warning(f"Error cargando archivo base: {e}")
        
        # Obtener nuevos enlaces
        nuevos_enlaces_por_seccion = self.explorar_multiples_secciones()
        
        # Combinar todos los nuevos enlaces
        todos_los_nuevos_enlaces = []
        for seccion, enlaces in nuevos_enlaces_por_seccion.items():
            todos_los_nuevos_enlaces.extend(enlaces)
        
        # Clasificar nuevos enlaces
        nuevos_clasificados = self.clasificar_documentos_por_tipo(todos_los_nuevos_enlaces)
        
        # Combinar enlaces existentes con nuevos (evitando duplicados)
        urls_existentes = set()
        documento_final = {
            'metadata': {
                'titulo': 'Enlaces Expandidos a Leyes y Reglamentos Federales de México',
                'descripcion': 'Documento expandido con enlaces del Orden Jurídico Nacional',
                'fecha_generacion': datetime.now().isoformat(),
                'fuente': 'Orden Jurídico Nacional - ordenjuridico.gob.mx',
                'metodo': 'Web scraping expandido',
                'total_enlaces': 0
            },
            'leyes_federales': [],
            'reglamentos_federales': [],
            'decretos': [],
            'acuerdos': [],
            'normas': [],
            'otros': []
        }
        
        # Agregar enlaces existentes primero
        for categoria in documento_final.keys():
            if categoria != 'metadata':
                for enlace in enlaces_existentes.get(categoria, []):
                    if enlace.get('url') not in urls_existentes:
                        documento_final[categoria].append(enlace)
                        urls_existentes.add(enlace.get('url'))
        
        # Agregar nuevos enlaces
        for categoria in documento_final.keys():
            if categoria != 'metadata':
                for enlace in nuevos_clasificados.get(categoria, []):
                    if enlace.get('url') not in urls_existentes:
                        documento_final[categoria].append(enlace)
                        urls_existentes.add(enlace.get('url'))
        
        # Calcular totales
        total = sum(len(documento_final[cat]) for cat in documento_final.keys() if cat != 'metadata')
        documento_final['metadata']['total_enlaces'] = total
        
        # Guardar documento expandido
        with open(archivo_expandido, 'w', encoding='utf-8') as f:
            json.dump(documento_final, f, indent=2, ensure_ascii=False)
        
        logger.success(f"Documento expandido generado: {archivo_expandido}")
        logger.info(f"Total de enlaces: {total}")
        for categoria in documento_final.keys():
            if categoria != 'metadata':
                count = len(documento_final[categoria])
                if count > 0:
                    logger.info(f"{categoria.replace('_', ' ').title()}: {count}")
    
    def generar_urls_para_scraper_expandido(self, archivo_json: Path, archivo_urls: Path, max_urls: int = 200) -> None:
        """Genera archivo de URLs para scraper desde el documento expandido.
        
        Args:
            archivo_json: Archivo JSON con enlaces expandidos.
            archivo_urls: Archivo donde guardar las URLs.
            max_urls: Número máximo de URLs.
        """
        if not archivo_json.exists():
            logger.error(f"Archivo JSON no encontrado: {archivo_json}")
            return
        
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            urls = []
            urls.append("# URLs expandidas de leyes y reglamentos federales")
            urls.append(f"# Generado desde: {archivo_json}")
            urls.append(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            urls.append("")
            
            contador = 0
            
            for categoria, enlaces in datos.items():
                if categoria == 'metadata' or contador >= max_urls:
                    continue
                
                if enlaces and len(enlaces) > 0:
                    urls.append(f"# {categoria.replace('_', ' ').upper()}")
                    
                    for enlace in enlaces:
                        if contador >= max_urls:
                            break
                        
                        titulo = enlace.get('titulo', 'Sin título')[:80]
                        url = enlace.get('url', '')
                        
                        if url:
                            urls.append(f"# {titulo}")
                            urls.append(url)
                            urls.append("")
                            contador += 1
            
            # Guardar archivo
            with open(archivo_urls, 'w', encoding='utf-8') as f:
                f.write('\n'.join(urls))
            
            logger.success(f"Archivo de URLs expandido generado: {archivo_urls}")
            logger.info(f"Total de URLs incluidas: {contador}")
            
        except Exception as e:
            logger.error(f"Error generando URLs expandidas: {e}")


def main():
    """Función principal."""
    expandir = ExpandirEnlacesLeyes()
    
    # Archivos
    archivo_base = Path('enlaces_leyes_reglamentos.json')
    archivo_expandido = Path('enlaces_leyes_reglamentos_expandido.json')
    archivo_urls_expandido = Path('urls_leyes_reglamentos_expandido.txt')
    
    # Generar documento expandido
    expandir.generar_documento_expandido(archivo_base, archivo_expandido)
    
    # Generar archivo de URLs expandido
    expandir.generar_urls_para_scraper_expandido(
        archivo_expandido, 
        archivo_urls_expandido, 
        max_urls=150
    )
    
    print(f"\n✓ Documentos expandidos generados:")
    print(f"  - Enlaces expandidos: {archivo_expandido}")
    print(f"  - URLs expandidas para scraper: {archivo_urls_expandido}")


if __name__ == "__main__":
    main()