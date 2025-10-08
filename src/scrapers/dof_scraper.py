"""Scraper para el Diario Oficial de la Federación (DOF).

Este módulo contiene la implementación del scraper especializado para extraer
publicaciones del Diario Oficial de la Federación de México.
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from loguru import logger

from ..utils.config import settings
from ..models.legal_document import LegalDocument


class DOFScraper:
    """Scraper especializado para el Diario Oficial de la Federación."""
    
    def __init__(self):
        """Inicializa el scraper del DOF."""
        self.base_url = settings.dof_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        # Deshabilitar verificación SSL temporalmente para sitios con problemas de certificado
        self.session.verify = False
        # Suprimir warnings de SSL
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.driver = None
        
    def _setup_selenium_driver(self) -> webdriver.Chrome:
        """Configura el driver de Selenium para navegación dinámica."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={settings.user_agent}')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def get_daily_publications(self, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Obtiene las publicaciones de un día específico.
        
        Args:
            date: Fecha de las publicaciones. Si es None, usa la fecha actual.
            
        Returns:
            Lista de diccionarios con información de las publicaciones.
        """
        if date is None:
            date = datetime.now()
            
        logger.info(f"Obteniendo publicaciones del DOF para {date.strftime('%Y-%m-%d')}")
        
        try:
            # Construir URL para la fecha específica
            date_str = date.strftime('%d/%m/%Y')
            search_url = f"{self.base_url}index.php?year={date.year}&month={date.month:02d}&day={date.day:02d}"
            
            # Intentar múltiples veces en caso de errores de conexión
            for attempt in range(settings.max_retries):
                try:
                    response = self.session.get(
                        search_url, 
                        timeout=settings.request_timeout
                    )
                    response.raise_for_status()
                    break
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.SSLError) as e:
                    if attempt < settings.max_retries - 1:
                        logger.warning(f"Intento {attempt + 1} falló, reintentando en {settings.scrape_delay}s: {e}")
                        import time
                        time.sleep(settings.scrape_delay)
                        continue
                    else:
                        raise e
            
            soup = BeautifulSoup(response.content, 'html.parser')
            publications = self._parse_daily_page(soup, date)
            
            logger.info(f"Encontradas {len(publications)} publicaciones para {date_str}")
            return publications
            
        except Exception as e:
            logger.error(f"Error obteniendo publicaciones del {date_str}: {e}")
            return []
    
    def _parse_daily_page(self, soup: BeautifulSoup, date: datetime) -> List[Dict[str, Any]]:
        """Parsea la página diaria del DOF para extraer publicaciones.
        
        Args:
            soup: Objeto BeautifulSoup de la página.
            date: Fecha de las publicaciones.
            
        Returns:
            Lista de publicaciones encontradas.
        """
        publications = []
        
        # Buscar enlaces a publicaciones (patrón común en DOF)
        publication_links = soup.find_all('a', href=re.compile(r'nota_detalle\.php\?codigo=\d+'))
        
        for link in publication_links:
            try:
                # Extraer información básica del enlace
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if not title or not href:
                    continue
                    
                # Construir URL completa
                if href.startswith('/'):
                    full_url = self.base_url.rstrip('/') + href
                elif not href.startswith('http'):
                    full_url = self.base_url.rstrip('/') + '/' + href
                else:
                    full_url = href
                
                # Extraer código de la publicación
                codigo_match = re.search(r'codigo=(\d+)', href)
                codigo = codigo_match.group(1) if codigo_match else None
                
                publication = {
                    'title': title,
                    'url': full_url,
                    'codigo': codigo,
                    'date': date,
                    'source': 'DOF',
                    'scraped_at': datetime.now()
                }
                
                publications.append(publication)
                
            except Exception as e:
                logger.warning(f"Error procesando enlace de publicación: {e}")
                continue
        
        return publications
    
    def get_publication_content(self, publication_url: str) -> Optional[Dict[str, Any]]:
        """Obtiene el contenido completo de una publicación específica.
        
        Args:
            publication_url: URL de la publicación.
            
        Returns:
            Diccionario con el contenido de la publicación o None si hay error.
        """
        try:
            logger.info(f"Obteniendo contenido de: {publication_url}")
            
            # Intentar múltiples veces en caso de errores de conexión
            for attempt in range(settings.max_retries):
                try:
                    response = self.session.get(
                        publication_url, 
                        timeout=settings.request_timeout
                    )
                    response.raise_for_status()
                    break
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.SSLError) as e:
                    if attempt < settings.max_retries - 1:
                        logger.warning(f"Intento {attempt + 1} falló para contenido, reintentando: {e}")
                        import time
                        time.sleep(settings.scrape_delay)
                        continue
                    else:
                        raise e
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content = self._parse_publication_content(soup)
            
            return content
            
        except Exception as e:
            logger.error(f"Error obteniendo contenido de {publication_url}: {e}")
            return None
    
    def _parse_publication_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parsea el contenido de una publicación individual.
        
        Args:
            soup: Objeto BeautifulSoup de la página de la publicación.
            
        Returns:
            Diccionario con el contenido estructurado.
        """
        content = {
            'title': '',
            'content': '',
            'metadata': {},
            'sections': []
        }
        
        # Extraer título
        title_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
        if title_elem:
            content['title'] = title_elem.get_text(strip=True)
        
        # Extraer contenido principal
        # Buscar div o section con el contenido principal
        main_content = soup.find('div', class_=re.compile(r'content|main|article')) or soup.find('article')
        
        if main_content:
            # Limpiar y extraer texto
            for script in main_content(["script", "style"]):
                script.decompose()
            
            content['content'] = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback: extraer todo el texto del body
            body = soup.find('body')
            if body:
                for script in body(["script", "style", "nav", "header", "footer"]):
                    script.decompose()
                content['content'] = body.get_text(separator='\n', strip=True)
        
        # Extraer metadatos adicionales
        content['metadata'] = self._extract_metadata(soup)
        
        return content
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrae metadatos de la publicación.
        
        Args:
            soup: Objeto BeautifulSoup de la página.
            
        Returns:
            Diccionario con metadatos extraídos.
        """
        metadata = {}
        
        # Extraer meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[name] = content
        
        # Buscar información específica del DOF
        # Fecha de publicación
        date_patterns = [
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        text_content = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text_content)
            if match:
                metadata['fecha_encontrada'] = match.group(0)
                break
        
        return metadata
    
    def scrape_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extrae publicaciones de un rango de fechas.
        
        Args:
            start_date: Fecha de inicio.
            end_date: Fecha de fin.
            
        Returns:
            Lista de todas las publicaciones encontradas.
        """
        all_publications = []
        current_date = start_date
        
        logger.info(f"Iniciando scraping del DOF desde {start_date.strftime('%Y-%m-%d')} hasta {end_date.strftime('%Y-%m-%d')}")
        
        while current_date <= end_date:
            # Evitar fines de semana (DOF generalmente no publica)
            if current_date.weekday() < 5:  # Lunes a Viernes
                daily_publications = self.get_daily_publications(current_date)
                all_publications.extend(daily_publications)
                
                # Delay entre requests
                asyncio.sleep(settings.scrape_delay)
            
            current_date += timedelta(days=1)
        
        logger.info(f"Scraping completado. Total de publicaciones: {len(all_publications)}")
        return all_publications
    
    def save_publications(self, publications: List[Dict[str, Any]], output_dir: Optional[Path] = None) -> None:
        """Guarda las publicaciones extraídas en archivos.
        
        Args:
            publications: Lista de publicaciones a guardar.
            output_dir: Directorio de salida. Si es None, usa el directorio de datos del proyecto.
        """
        if output_dir is None:
            output_dir = settings.data_dir / "raw" / "dof"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for pub in publications:
            try:
                # Crear nombre de archivo basado en fecha y código
                date_str = pub['date'].strftime('%Y-%m-%d')
                codigo = pub.get('codigo', 'unknown')
                filename = f"dof_{date_str}_{codigo}.json"
                
                filepath = output_dir / filename
                
                # Guardar como JSON
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(pub, f, ensure_ascii=False, indent=2, default=str)
                
                logger.debug(f"Publicación guardada: {filepath}")
                
            except Exception as e:
                logger.error(f"Error guardando publicación: {e}")
    
    def close(self):
        """Cierra recursos del scraper."""
        if self.driver:
            self.driver.quit()
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()