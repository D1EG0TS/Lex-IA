#!/usr/bin/env python3
"""Scraper completo para extraer todos los enlaces del Orden Jurídico Nacional.

Este script está diseñado para extraer la lista completa de 302 leyes federales
y 135 reglamentos federales del sitio web ordenjuridico.gob.mx.
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
import sys


class ScraperCompletoOrdenJuridico:
    """Scraper completo para extraer todos los enlaces del Orden Jurídico Nacional."""
    
    def __init__(self):
        """Inicializa el scraper completo."""
        self.base_url = "https://www.ordenjuridico.gob.mx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.enlaces_encontrados = set()
        self.leyes_federales = []
        self.reglamentos_federales = []
        
    def extraer_enlaces_javascript(self, url: str, tipo_documento: str) -> List[Dict]:
        """Extrae enlaces que se cargan dinámicamente via JavaScript.
        
        Args:
            url: URL de la página a explorar.
            tipo_documento: 'leyes' o 'reglamentos'.
            
        Returns:
            Lista de enlaces encontrados.
        """
        enlaces = []
        
        try:
            logger.info(f"Extrayendo {tipo_documento} desde: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar scripts que contengan datos de documentos
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string:
                    script_content = script.string
                    
                    # Buscar patrones de URLs en el JavaScript
                    url_patterns = re.findall(r'wo\d+\.html', script_content)
                    
                    for pattern in url_patterns:
                        url_completa = f"{self.base_url}/Documentos/Federal/html/{pattern}"
                        
                        if url_completa not in self.enlaces_encontrados:
                            self.enlaces_encontrados.add(url_completa)
                            
                            # Extraer código del documento
                            codigo_match = re.search(r'wo(\d+)\.html', pattern)
                            codigo = codigo_match.group(1) if codigo_match else ''
                            
                            enlace_info = {
                                'titulo': f'{tipo_documento.title()} wo{codigo}',
                                'url': url_completa,
                                'id': f'wo{codigo}',
                                'codigo': codigo,
                                'tipo': 'ley' if tipo_documento == 'leyes' else 'reglamento',
                                'fuente': 'JAVASCRIPT_EXTRACTION',
                                'fecha_extraccion': datetime.now().isoformat()
                            }
                            
                            enlaces.append(enlace_info)
            
            logger.info(f"Encontrados {len(enlaces)} {tipo_documento} en JavaScript")
            
        except Exception as e:
            logger.error(f"Error extrayendo {tipo_documento} via JavaScript: {e}")
            
        return enlaces
    
    def extraer_enlaces_ajax(self, tipo: int) -> List[Dict]:
        """Intenta extraer enlaces via llamadas AJAX simuladas.
        
        Args:
            tipo: 1 para leyes, 2 para reglamentos.
            
        Returns:
            Lista de enlaces encontrados.
        """
        enlaces = []
        tipo_nombre = 'leyes' if tipo == 1 else 'reglamentos'
        
        try:
            # Intentar diferentes endpoints AJAX posibles
            ajax_urls = [
                f"{self.base_url}/ajax/mostrar_documentos.php",
                f"{self.base_url}/ajax/leyes.php",
                f"{self.base_url}/mostrar_leyes.php",
                f"{self.base_url}/get_documentos.php"
            ]
            
            for ajax_url in ajax_urls:
                try:
                    # Datos para la petición AJAX
                    data = {
                        'tipo': tipo,
                        'action': 'mostrar',
                        'categoria': tipo_nombre
                    }
                    
                    headers = {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': f'{self.base_url}/leyes.php'
                    }
                    
                    response = self.session.post(ajax_url, data=data, headers=headers, timeout=15)
                    
                    if response.status_code == 200 and response.text.strip():
                        # Parsear respuesta HTML
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Buscar enlaces a documentos
                        links = soup.find_all('a', href=re.compile(r'wo\d+\.html'))
                        
                        for link in links:
                            href = link.get('href')
                            texto = link.get_text(strip=True)
                            
                            if href and texto:
                                url_completa = urljoin(self.base_url, href)
                                
                                if url_completa not in self.enlaces_encontrados:
                                    self.enlaces_encontrados.add(url_completa)
                                    
                                    codigo_match = re.search(r'wo(\d+)\.html', href)
                                    codigo = codigo_match.group(1) if codigo_match else ''
                                    
                                    enlace_info = {
                                        'titulo': texto.strip(),
                                        'url': url_completa,
                                        'id': f'wo{codigo}',
                                        'codigo': codigo,
                                        'tipo': 'ley' if tipo == 1 else 'reglamento',
                                        'fuente': 'AJAX_EXTRACTION',
                                        'fecha_extraccion': datetime.now().isoformat()
                                    }
                                    
                                    enlaces.append(enlace_info)
                        
                        if enlaces:
                            logger.success(f"AJAX exitoso en {ajax_url}: {len(enlaces)} {tipo_nombre}")
                            break
                            
                except Exception as e:
                    logger.debug(f"AJAX falló en {ajax_url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error en extracción AJAX para {tipo_nombre}: {e}")
            
        return enlaces
    
    def explorar_sitemap_xml(self) -> List[Dict]:
        """Intenta encontrar y explorar sitemaps XML.
        
        Returns:
            Lista de enlaces encontrados en sitemaps.
        """
        enlaces = []
        
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/robots.txt"
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=15)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Buscar URLs de documentos en el contenido
                    urls_encontradas = re.findall(r'https?://[^\s<>"]+wo\d+\.html', content)
                    
                    for url in urls_encontradas:
                        if url not in self.enlaces_encontrados:
                            self.enlaces_encontrados.add(url)
                            
                            codigo_match = re.search(r'wo(\d+)\.html', url)
                            codigo = codigo_match.group(1) if codigo_match else ''
                            
                            enlace_info = {
                                'titulo': f'Documento wo{codigo}',
                                'url': url,
                                'id': f'wo{codigo}',
                                'codigo': codigo,
                                'tipo': 'documento',
                                'fuente': 'SITEMAP_XML',
                                'fecha_extraccion': datetime.now().isoformat()
                            }
                            
                            enlaces.append(enlace_info)
                    
                    if enlaces:
                        logger.success(f"Sitemap encontrado en {sitemap_url}: {len(enlaces)} enlaces")
                        break
                        
            except Exception as e:
                logger.debug(f"No se pudo acceder a {sitemap_url}: {e}")
                continue
        
        return enlaces
    
    def explorar_indices_numericos(self, rango_inicio: int = 1, rango_fin: int = 150000) -> List[Dict]:
        """Explora documentos por rangos numéricos de códigos.
        
        Args:
            rango_inicio: Código inicial a explorar.
            rango_fin: Código final a explorar.
            
        Returns:
            Lista de enlaces válidos encontrados.
        """
        enlaces_validos = []
        
        logger.info(f"Explorando códigos desde wo{rango_inicio} hasta wo{rango_fin}")
        
        # Explorar en lotes para no sobrecargar el servidor
        lote_size = 100
        
        for i in range(rango_inicio, rango_fin + 1, lote_size):
            fin_lote = min(i + lote_size - 1, rango_fin)
            
            logger.info(f"Explorando lote: wo{i} - wo{fin_lote}")
            
            for codigo in range(i, fin_lote + 1):
                url = f"{self.base_url}/Documentos/Federal/html/wo{codigo}.html"
                
                try:
                    # Hacer petición HEAD para verificar existencia
                    response = self.session.head(url, timeout=5)
                    
                    if response.status_code == 200:
                        if url not in self.enlaces_encontrados:
                            self.enlaces_encontrados.add(url)
                            
                            enlace_info = {
                                'titulo': f'Documento wo{codigo}',
                                'url': url,
                                'id': f'wo{codigo}',
                                'codigo': str(codigo),
                                'tipo': 'documento',
                                'fuente': 'NUMERIC_EXPLORATION',
                                'fecha_extraccion': datetime.now().isoformat()
                            }
                            
                            enlaces_validos.append(enlace_info)
                            
                            if len(enlaces_validos) % 50 == 0:
                                logger.info(f"Encontrados {len(enlaces_validos)} documentos válidos")
                    
                    # Pausa pequeña para no sobrecargar
                    time.sleep(0.1)
                    
                except Exception as e:
                    # Ignorar errores individuales
                    continue
            
            # Pausa entre lotes
            time.sleep(2)
            
            # Mostrar progreso
            logger.info(f"Progreso: {fin_lote}/{rango_fin} códigos explorados")
        
        logger.success(f"Exploración numérica completada: {len(enlaces_validos)} documentos válidos")
        return enlaces_validos
    
    def clasificar_documentos_por_contenido(self, enlaces: List[Dict]) -> Dict[str, List[Dict]]:
        """Clasifica documentos obteniendo información de su contenido.
        
        Args:
            enlaces: Lista de enlaces a clasificar.
            
        Returns:
            Diccionario con documentos clasificados.
        """
        clasificados = {
            'leyes_federales': [],
            'reglamentos_federales': [],
            'decretos': [],
            'acuerdos': [],
            'normas': [],
            'otros': []
        }
        
        logger.info(f"Clasificando {len(enlaces)} documentos por contenido")
        
        for i, enlace in enumerate(enlaces):
            try:
                # Obtener título real del documento
                response = self.session.get(enlace['url'], timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Buscar título en diferentes elementos
                    titulo_real = None
                    
                    # Intentar diferentes selectores para el título
                    selectores_titulo = [
                        'h1',
                        'h2',
                        '.titulo',
                        '.title',
                        'title',
                        '.documento-titulo'
                    ]
                    
                    for selector in selectores_titulo:
                        elemento = soup.select_one(selector)
                        if elemento and elemento.get_text(strip=True):
                            titulo_real = elemento.get_text(strip=True)
                            break
                    
                    if titulo_real:
                        enlace['titulo'] = titulo_real
                        titulo_lower = titulo_real.lower()
                        
                        # Clasificar por palabras clave
                        if any(palabra in titulo_lower for palabra in ['ley ', 'código']):
                            enlace['tipo'] = 'ley'
                            clasificados['leyes_federales'].append(enlace)
                        elif 'reglamento' in titulo_lower:
                            enlace['tipo'] = 'reglamento'
                            clasificados['reglamentos_federales'].append(enlace)
                        elif 'decreto' in titulo_lower:
                            enlace['tipo'] = 'decreto'
                            clasificados['decretos'].append(enlace)
                        elif 'acuerdo' in titulo_lower:
                            enlace['tipo'] = 'acuerdo'
                            clasificados['acuerdos'].append(enlace)
                        elif any(palabra in titulo_lower for palabra in ['norma', 'nom-']):
                            enlace['tipo'] = 'norma'
                            clasificados['normas'].append(enlace)
                        else:
                            enlace['tipo'] = 'otro'
                            clasificados['otros'].append(enlace)
                    else:
                        enlace['tipo'] = 'otro'
                        clasificados['otros'].append(enlace)
                
                # Pausa para no sobrecargar el servidor
                time.sleep(0.5)
                
                # Mostrar progreso cada 25 documentos
                if (i + 1) % 25 == 0:
                    logger.info(f"Clasificados {i + 1}/{len(enlaces)} documentos")
                    
            except Exception as e:
                logger.warning(f"Error clasificando {enlace['url']}: {e}")
                enlace['tipo'] = 'otro'
                clasificados['otros'].append(enlace)
                continue
        
        return clasificados
    
    def ejecutar_scraping_completo(self) -> Dict[str, List[Dict]]:
        """Ejecuta el scraping completo usando múltiples métodos.
        
        Returns:
            Diccionario con todos los enlaces clasificados.
        """
        logger.info("Iniciando scraping completo del Orden Jurídico Nacional")
        
        todos_los_enlaces = []
        
        # Método 1: Extracción JavaScript
        logger.info("=== Método 1: Extracción JavaScript ===")
        enlaces_js_leyes = self.extraer_enlaces_javascript(f"{self.base_url}/leyes.php", "leyes")
        enlaces_js_reglamentos = self.extraer_enlaces_javascript(f"{self.base_url}/leyes.php", "reglamentos")
        todos_los_enlaces.extend(enlaces_js_leyes + enlaces_js_reglamentos)
        
        # Método 2: Extracción AJAX
        logger.info("=== Método 2: Extracción AJAX ===")
        enlaces_ajax_leyes = self.extraer_enlaces_ajax(1)
        enlaces_ajax_reglamentos = self.extraer_enlaces_ajax(2)
        todos_los_enlaces.extend(enlaces_ajax_leyes + enlaces_ajax_reglamentos)
        
        # Método 3: Explorar sitemaps
        logger.info("=== Método 3: Exploración de Sitemaps ===")
        enlaces_sitemap = self.explorar_sitemap_xml()
        todos_los_enlaces.extend(enlaces_sitemap)
        
        # Método 4: Exploración numérica (limitada)
        logger.info("=== Método 4: Exploración Numérica ===")
        # Explorar rangos conocidos de documentos activos
        rangos_exploracion = [
            (1, 1000),
            (5000, 10000),
            (10000, 20000),
            (30000, 50000),
            (80000, 100000),
            (120000, 130000)
        ]
        
        for inicio, fin in rangos_exploracion:
            logger.info(f"Explorando rango {inicio}-{fin}")
            enlaces_numericos = self.explorar_indices_numericos(inicio, fin)
            todos_los_enlaces.extend(enlaces_numericos)
            
            # Si encontramos suficientes enlaces, podemos parar
            if len(self.enlaces_encontrados) > 400:
                logger.info(f"Encontrados {len(self.enlaces_encontrados)} enlaces, suficiente para continuar")
                break
        
        # Eliminar duplicados
        enlaces_unicos = []
        urls_vistas = set()
        
        for enlace in todos_los_enlaces:
            if enlace['url'] not in urls_vistas:
                urls_vistas.add(enlace['url'])
                enlaces_unicos.append(enlace)
        
        logger.info(f"Total de enlaces únicos encontrados: {len(enlaces_unicos)}")
        
        # Clasificar documentos por contenido
        logger.info("=== Clasificación por Contenido ===")
        documentos_clasificados = self.clasificar_documentos_por_contenido(enlaces_unicos)
        
        return documentos_clasificados
    
    def generar_documento_completo(self, archivo_salida: Path) -> None:
        """Genera el documento completo con todos los enlaces.
        
        Args:
            archivo_salida: Archivo donde guardar los resultados.
        """
        logger.info("Ejecutando scraping completo")
        
        documentos_clasificados = self.ejecutar_scraping_completo()
        
        # Calcular totales
        total_leyes = len(documentos_clasificados['leyes_federales'])
        total_reglamentos = len(documentos_clasificados['reglamentos_federales'])
        total_general = sum(len(docs) for docs in documentos_clasificados.values())
        
        # Crear documento final
        documento_final = {
            'metadata': {
                'titulo': 'Lista Completa de Enlaces - Orden Jurídico Nacional',
                'descripcion': 'Extracción completa de leyes y reglamentos federales',
                'fecha_generacion': datetime.now().isoformat(),
                'fuente': 'Orden Jurídico Nacional - ordenjuridico.gob.mx',
                'metodo': 'Scraping completo multi-método',
                'total_enlaces': total_general,
                'total_leyes_federales': total_leyes,
                'total_reglamentos_federales': total_reglamentos,
                'objetivo_leyes': 302,
                'objetivo_reglamentos': 135,
                'porcentaje_leyes': round((total_leyes / 302) * 100, 2) if total_leyes <= 302 else 100,
                'porcentaje_reglamentos': round((total_reglamentos / 135) * 100, 2) if total_reglamentos <= 135 else 100
            }
        }
        
        # Agregar documentos clasificados
        documento_final.update(documentos_clasificados)
        
        # Guardar archivo
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(documento_final, f, indent=2, ensure_ascii=False)
        
        logger.success(f"Documento completo generado: {archivo_salida}")
        logger.info(f"Leyes federales encontradas: {total_leyes}/302 ({documento_final['metadata']['porcentaje_leyes']}%)")
        logger.info(f"Reglamentos federales encontrados: {total_reglamentos}/135 ({documento_final['metadata']['porcentaje_reglamentos']}%)")
        logger.info(f"Total de documentos: {total_general}")
        
        return documento_final


def main():
    """Función principal."""
    scraper = ScraperCompletoOrdenJuridico()
    
    archivo_salida = Path('enlaces_completos_orden_juridico.json')
    
    try:
        documento = scraper.generar_documento_completo(archivo_salida)
        
        print(f"\n✓ Scraping completo finalizado")
        print(f"  - Archivo generado: {archivo_salida}")
        print(f"  - Leyes federales: {documento['metadata']['total_leyes_federales']}")
        print(f"  - Reglamentos federales: {documento['metadata']['total_reglamentos_federales']}")
        print(f"  - Total documentos: {documento['metadata']['total_enlaces']}")
        
    except KeyboardInterrupt:
        logger.warning("Scraping interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()