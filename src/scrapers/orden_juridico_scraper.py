"""Scraper para el Orden Jurídico Nacional (ordenjuridico.gob.mx).

Este módulo contiene la implementación del scraper especializado para extraer
leyes y reglamentos federales del Orden Jurídico Nacional de México.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from loguru import logger

from ..utils.config import settings
from ..models.legal_document import LegalDocument, DocumentType, DocumentSource


class OrdenJuridicoScraper:
    """Scraper especializado para el Orden Jurídico Nacional."""
    
    def __init__(self):
        """Inicializa el scraper del Orden Jurídico Nacional."""
        self.base_url = "https://www.ordenjuridico.gob.mx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        # Configurar SSL
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def scrape_document_by_url(self, url: str, extract_content: bool = True) -> Optional[LegalDocument]:
        """Extrae un documento específico por su URL.
        
        Args:
            url: URL del documento a extraer.
            extract_content: Si extraer el contenido completo del documento.
            
        Returns:
            LegalDocument con la información extraída o None si hay error.
        """
        logger.info(f"Extrayendo documento de: {url}")
        
        try:
            # Realizar petición con reintentos
            for attempt in range(settings.max_retries):
                try:
                    response = self.session.get(
                        url, 
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
            
            # Extraer información del documento
            document_info = self._parse_document_page(soup, url)
            
            if extract_content:
                document_info['content'] = self._extract_document_content(soup)
            
            # Asegurar que hay contenido si no se extrajo
            if not extract_content:
                document_info['content'] = "[Contenido no extraído - solo metadatos]"
            
            # Crear objeto LegalDocument
            legal_doc = self._create_legal_document(document_info)
            
            logger.info(f"Documento extraído exitosamente: {legal_doc.title[:100]}...")
            return legal_doc
            
        except Exception as e:
            logger.error(f"Error extrayendo documento de {url}: {e}")
            return None
    
    def _parse_document_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parsea la página de un documento para extraer metadatos.
        
        Args:
            soup: Objeto BeautifulSoup de la página.
            url: URL del documento.
            
        Returns:
            Diccionario con información del documento.
        """
        document_info = {
            'url': url,
            'source': 'ORDEN_JURIDICO',
            'scraped_at': datetime.now()
        }
        
        # Extraer código del documento de la URL
        codigo_match = re.search(r'wo(\d+)\.html', url)
        if codigo_match:
            document_info['codigo'] = codigo_match.group(1)
            document_info['id'] = f"wo{codigo_match.group(1)}"
        
        # Extraer título
        title_element = soup.find('title')
        if title_element:
            document_info['title'] = title_element.get_text(strip=True)
        else:
            # Buscar en h1, h2, etc.
            for tag in ['h1', 'h2', 'h3']:
                title_element = soup.find(tag)
                if title_element:
                    document_info['title'] = title_element.get_text(strip=True)
                    break
        
        # Si no se encuentra título, usar un título por defecto
        if 'title' not in document_info:
            document_info['title'] = f"Documento {document_info.get('codigo', 'sin código')}"
        
        # Extraer fecha de publicación (buscar patrones comunes)
        date_patterns = [
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        text_content = soup.get_text()
        for pattern in date_patterns:
            date_match = re.search(pattern, text_content)
            if date_match:
                try:
                    # Intentar parsear la fecha
                    if 'de' in pattern:
                        # Formato: "día de mes de año"
                        day, month_name, year = date_match.groups()
                        month_names = {
                            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                        }
                        month = month_names.get(month_name.lower(), 1)
                        document_info['publication_date'] = datetime(int(year), month, int(day))
                    else:
                        # Otros formatos
                        parts = date_match.groups()
                        if len(parts) == 3:
                            if len(parts[0]) == 4:  # YYYY-MM-DD
                                document_info['publication_date'] = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                            else:  # DD/MM/YYYY
                                document_info['publication_date'] = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                    break
                except (ValueError, KeyError):
                    continue
        
        # Determinar tipo de documento basado en el contenido
        document_info['document_type'] = self._determine_document_type(text_content, document_info.get('title', ''))
        
        return document_info
    
    def _extract_document_content(self, soup: BeautifulSoup) -> str:
        """Extrae el contenido principal del documento.
        
        Args:
            soup: Objeto BeautifulSoup de la página.
            
        Returns:
            Contenido del documento como texto.
        """
        # Remover elementos no deseados
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Buscar el contenido principal
        main_content = None
        
        # Intentar encontrar el contenido en diferentes contenedores
        content_selectors = [
            'div.content',
            'div.main-content',
            'div.document-content',
            'div.texto',
            'div#content',
            'main',
            'article'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # Si no se encuentra un contenedor específico, usar el body
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Limpiar y extraer texto
            text = main_content.get_text(separator='\n', strip=True)
            # Limpiar espacios en blanco excesivos
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            return text
        
        return soup.get_text(separator='\n', strip=True)
    
    def _determine_document_type(self, content: str, title: str) -> DocumentType:
        """Determina el tipo de documento basado en su contenido y título.
        
        Args:
            content: Contenido del documento.
            title: Título del documento.
            
        Returns:
            Tipo de documento.
        """
        content_lower = content.lower()
        title_lower = title.lower()
        
        # Patrones para identificar tipos de documentos
        if any(word in title_lower for word in ['ley', 'código']):
            return DocumentType.LEY
        elif any(word in title_lower for word in ['reglamento']):
            return DocumentType.REGLAMENTO
        elif any(word in title_lower for word in ['decreto']):
            return DocumentType.DECRETO
        elif any(word in title_lower for word in ['acuerdo']):
            return DocumentType.ACUERDO
        elif any(word in content_lower for word in ['norma oficial mexicana', 'nom-']):
            return DocumentType.NORMA
        else:
            return DocumentType.OTRO
    
    def _create_legal_document(self, document_info: Dict[str, Any]) -> LegalDocument:
        """Crea un objeto LegalDocument a partir de la información extraída.
        
        Args:
            document_info: Diccionario con información del documento.
            
        Returns:
            Objeto LegalDocument.
        """
        return LegalDocument(
            id=document_info.get('id', ''),
            title=document_info.get('title', ''),
            document_type=document_info.get('document_type', DocumentType.OTRO),
            source=DocumentSource.ORDEN_JURIDICO,
            url=document_info.get('url', ''),
            publication_date=document_info.get('publication_date'),
            content=document_info.get('content', ''),
            metadata={
                'codigo': document_info.get('codigo'),
                'scraped_at': document_info.get('scraped_at').isoformat() if document_info.get('scraped_at') else None,
                'extraction_method': 'orden_juridico_scraper'
            }
        )
    
    def scrape_multiple_documents(self, urls: List[str], extract_content: bool = True) -> List[LegalDocument]:
        """Extrae múltiples documentos por sus URLs.
        
        Args:
            urls: Lista de URLs de documentos a extraer.
            extract_content: Si extraer el contenido completo de los documentos.
            
        Returns:
            Lista de LegalDocument extraídos.
        """
        documents = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Procesando documento {i}/{len(urls)}: {url}")
            
            document = self.scrape_document_by_url(url, extract_content)
            if document:
                documents.append(document)
            
            # Pausa entre peticiones
            if i < len(urls):
                import time
                time.sleep(settings.scrape_delay)
        
        logger.info(f"Extraídos {len(documents)} documentos de {len(urls)} URLs")
        return documents
    
    def save_documents(self, documents: List[LegalDocument], output_dir: Path) -> None:
        """Guarda los documentos extraídos en archivos JSON.
        
        Args:
            documents: Lista de documentos a guardar.
            output_dir: Directorio donde guardar los archivos.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for document in documents:
            # Crear nombre de archivo basado en el código o ID
            filename = f"orden_juridico_{document.id or 'unknown'}.json"
            filepath = output_dir / filename
            
            # Guardar como JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(document.model_dump_json(indent=2))
            
            logger.info(f"Documento guardado: {filepath}")
        
        logger.info(f"Guardados {len(documents)} documentos en {output_dir}")