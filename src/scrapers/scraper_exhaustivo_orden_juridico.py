#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Exhaustivo para Orden Jurídico Nacional
Extrae TODOS los enlaces disponibles explorando sistemáticamente códigos wo1-wo200000
Objetivo: 302 leyes federales + 135 reglamentos federales = 437 documentos mínimo
"""

import requests
import json
import time
import re
import ssl
import urllib3
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import List, Dict, Set, Tuple

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de logging
logger.add("scraper_exhaustivo.log", rotation="10 MB", level="INFO")

class ScraperExhaustivo:
    def __init__(self):
        self.base_url = "https://www.ordenjuridico.gob.mx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Configurar para ignorar SSL
        self.session.verify = False
        
        self.documentos_encontrados = []
        self.codigos_validos = set()
        self.codigos_procesados = set()
        self.lock = threading.Lock()
        
        # Contadores por tipo
        self.contadores = {
            'leyes_federales': 0,
            'reglamentos_federales': 0,
            'decretos': 0,
            'acuerdos': 0,
            'constituciones': 0,
            'otros': 0
        }
        
        # Patrones para clasificación mejorados
        self.patrones_clasificacion = {
            'ley': [
                r'\bley\b(?!.*reglament)', r'\bcode\b', r'\bcodigo\b',
                r'ley.*federal', r'ley.*general', r'ley.*organica',
                r'ley.*amparo', r'ley.*electoral', r'ley.*educacion',
                r'ley.*salud', r'ley.*trabajo', r'ley.*seguridad'
            ],
            'reglamento': [
                r'\breglament', r'reglamento.*federal', r'reglamento.*general',
                r'reglamento.*interior', r'reglamento.*organico', r'reglamento.*ley',
                r'reglamento.*prestacion', r'reglamento.*servicios'
            ],
            'constitucion': [r'\bconstituci[oó]n\b', r'\bcarta\s+magna\b'],
            'decreto': [r'\bdecreto\b', r'decreto.*federal', r'decreto.*reforma'],
            'acuerdo': [r'\bacuerdo\b', r'acuerdo.*federal', r'acuerdo.*secretar']
        }
        
        # Rangos conocidos con alta probabilidad de documentos
        self.rangos_prioritarios = [
            (1, 1000),      # Documentos históricos
            (5000, 15000),  # Leyes principales
            (15000, 25000), # Reglamentos
            (30000, 50000), # Decretos y acuerdos
            (80000, 100000), # Documentos recientes
            (120000, 140000) # Documentos muy recientes
        ]

    def verificar_documento_existe(self, codigo: str) -> Tuple[bool, str, str]:
        """Verifica si un documento existe y obtiene su título"""
        url = f"{self.base_url}/Documentos/Federal/html/wo{codigo}.html"
        
        try:
            response = self.session.get(url, timeout=15, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar título en diferentes elementos
                titulo = None
                for selector in ['title', 'h1', 'h2', '.titulo', '#titulo', 'h3']:
                    elemento = soup.select_one(selector)
                    if elemento and elemento.get_text(strip=True):
                        titulo = elemento.get_text(strip=True)
                        # Limpiar título
                        titulo = re.sub(r'\s+', ' ', titulo).strip()
                        if len(titulo) > 10 and 'error' not in titulo.lower():
                            break
                
                if not titulo:
                    # Buscar en el contenido del documento
                    content = soup.get_text()
                    if len(content) > 200:  # Documento válido si tiene contenido suficiente
                        # Intentar extraer título del contenido
                        lines = content.split('\n')[:10]
                        for line in lines:
                            line = line.strip()
                            if len(line) > 15 and len(line) < 200:
                                titulo = line
                                break
                        
                        if not titulo:
                            titulo = f"Documento Federal wo{codigo}"
                
                if titulo and len(titulo) > 5 and 'error' not in titulo.lower():
                    return True, titulo, url
                    
        except requests.exceptions.SSLError:
            # Intentar con HTTP en lugar de HTTPS
            try:
                url_http = url.replace('https://', 'http://')
                response = self.session.get(url_http, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    titulo = soup.select_one('title')
                    if titulo and len(titulo.get_text(strip=True)) > 5:
                        return True, titulo.get_text(strip=True), url_http
            except:
                pass
                
        except Exception as e:
            if 'timeout' not in str(e).lower():
                logger.debug(f"Error verificando wo{codigo}: {e}")
            
        return False, "", ""

    def clasificar_documento(self, titulo: str) -> str:
        """Clasifica un documento según su título"""
        titulo_lower = titulo.lower()
        
        for tipo, patrones in self.patrones_clasificacion.items():
            for patron in patrones:
                if re.search(patron, titulo_lower, re.IGNORECASE):
                    return tipo
        
        # Clasificación adicional por palabras clave
        if any(word in titulo_lower for word in ['federal', 'nacional', 'general']):
            if 'reglament' in titulo_lower:
                return 'reglamento'
            elif any(word in titulo_lower for word in ['ley', 'codigo']):
                return 'ley'
        
        return 'otro'

    def procesar_lote_codigos(self, inicio: int, fin: int) -> List[Dict]:
        """Procesa un lote de códigos"""
        documentos_lote = []
        
        for codigo in range(inicio, fin + 1):
            with self.lock:
                if codigo in self.codigos_procesados:
                    continue
                self.codigos_procesados.add(codigo)
            
            existe, titulo, url = self.verificar_documento_existe(str(codigo))
            
            if existe:
                tipo = self.clasificar_documento(titulo)
                
                documento = {
                    'titulo': titulo,
                    'url': url,
                    'id': f'wo{codigo}',
                    'codigo': str(codigo),
                    'tipo': tipo,
                    'fuente': 'SCRAPING_EXHAUSTIVO',
                    'fecha_descubrimiento': datetime.now().isoformat()
                }
                
                documentos_lote.append(documento)
                
                with self.lock:
                    self.codigos_validos.add(codigo)
                    if tipo == 'ley':
                        self.contadores['leyes_federales'] += 1
                    elif tipo == 'reglamento':
                        self.contadores['reglamentos_federales'] += 1
                    elif tipo == 'decreto':
                        self.contadores['decretos'] += 1
                    elif tipo == 'acuerdo':
                        self.contadores['acuerdos'] += 1
                    elif tipo == 'constitucion':
                        self.contadores['constituciones'] += 1
                    else:
                        self.contadores['otros'] += 1
                
                logger.info(f"Encontrado wo{codigo}: {tipo} - {titulo[:50]}...")
            
            # Pausa más corta
            time.sleep(0.05)
        
        return documentos_lote

    def explorar_rangos_prioritarios(self, max_workers: int = 4):
        """Explora primero los rangos con mayor probabilidad de documentos"""
        logger.info("Iniciando exploración de rangos prioritarios")
        
        for inicio, fin in self.rangos_prioritarios:
            logger.info(f"Explorando rango prioritario: wo{inicio} - wo{fin}")
            
            batch_size = 25
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                
                for batch_inicio in range(inicio, fin + 1, batch_size):
                    batch_fin = min(batch_inicio + batch_size - 1, fin)
                    future = executor.submit(self.procesar_lote_codigos, batch_inicio, batch_fin)
                    futures.append(future)
                
                for future in as_completed(futures):
                    try:
                        documentos_lote = future.result()
                        self.documentos_encontrados.extend(documentos_lote)
                        
                        if len(self.documentos_encontrados) % 25 == 0:
                            self.mostrar_progreso()
                            
                    except Exception as e:
                        logger.error(f"Error procesando lote: {e}")
            
            # Verificar si ya tenemos suficientes documentos
            if (self.contadores['leyes_federales'] >= 302 and 
                self.contadores['reglamentos_federales'] >= 135):
                logger.success("¡Objetivo alcanzado en rangos prioritarios!")
                return

    def explorar_rango_completo(self, inicio: int = 1, fin: int = 200000, 
                               batch_size: int = 50, max_workers: int = 3):
        """Explora exhaustivamente un rango de códigos"""
        logger.info(f"Iniciando exploración exhaustiva: wo{inicio} - wo{fin}")
        logger.info(f"Objetivo: 302 leyes federales + 135 reglamentos federales")
        
        # Primero explorar rangos prioritarios
        self.explorar_rangos_prioritarios()
        
        # Si no hemos alcanzado el objetivo, continuar con exploración completa
        if (self.contadores['leyes_federales'] < 302 or 
            self.contadores['reglamentos_federales'] < 135):
            
            logger.info("Continuando con exploración exhaustiva completa...")
            
            total_batches = (fin - inicio + 1) // batch_size + 1
            batch_actual = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                
                for batch_inicio in range(inicio, fin + 1, batch_size):
                    batch_fin = min(batch_inicio + batch_size - 1, fin)
                    
                    # Saltar si ya procesamos este rango
                    if all(codigo in self.codigos_procesados 
                           for codigo in range(batch_inicio, batch_fin + 1)):
                        continue
                    
                    future = executor.submit(self.procesar_lote_codigos, batch_inicio, batch_fin)
                    futures.append(future)
                    
                    batch_actual += 1
                    if batch_actual % 20 == 0:
                        logger.info(f"Enviados {batch_actual}/{total_batches} lotes")
                
                # Recopilar resultados
                for future in as_completed(futures):
                    try:
                        documentos_lote = future.result()
                        self.documentos_encontrados.extend(documentos_lote)
                        
                        if len(self.documentos_encontrados) % 50 == 0:
                            self.mostrar_progreso()
                            
                            # Verificar si ya alcanzamos el objetivo
                            if (self.contadores['leyes_federales'] >= 302 and 
                                self.contadores['reglamentos_federales'] >= 135):
                                logger.success("¡Objetivo alcanzado! Deteniendo exploración...")
                                for f in futures:
                                    f.cancel()
                                break
                                
                    except Exception as e:
                        logger.error(f"Error procesando lote: {e}")

    def mostrar_progreso(self):
        """Muestra el progreso actual"""
        total = len(self.documentos_encontrados)
        leyes = self.contadores['leyes_federales']
        reglamentos = self.contadores['reglamentos_federales']
        
        logger.info(f"Progreso: {total} documentos | Leyes: {leyes}/302 ({leyes/302*100:.1f}%) | Reglamentos: {reglamentos}/135 ({reglamentos/135*100:.1f}%)")

    def organizar_documentos(self) -> Dict:
        """Organiza los documentos por tipo"""
        organizados = {
            'leyes_federales': [],
            'reglamentos_federales': [],
            'decretos': [],
            'acuerdos': [],
            'constituciones': [],
            'otros': []
        }
        
        for doc in self.documentos_encontrados:
            tipo = doc['tipo']
            if tipo == 'ley':
                organizados['leyes_federales'].append(doc)
            elif tipo == 'reglamento':
                organizados['reglamentos_federales'].append(doc)
            elif tipo == 'decreto':
                organizados['decretos'].append(doc)
            elif tipo == 'acuerdo':
                organizados['acuerdos'].append(doc)
            elif tipo == 'constitucion':
                organizados['constituciones'].append(doc)
            else:
                organizados['otros'].append(doc)
        
        return organizados

    def guardar_resultados(self, archivo_json: str = "enlaces_exhaustivos_completos.json",
                          archivo_urls: str = "urls_exhaustivas_completas.txt"):
        """Guarda los resultados en archivos JSON y TXT"""
        documentos_organizados = self.organizar_documentos()
        
        resultado = {
            'metadata': {
                'titulo': 'Lista Exhaustiva Completa - Orden Jurídico Nacional',
                'descripcion': 'Lista completa obtenida por scraping exhaustivo',
                'fecha_generacion': datetime.now().isoformat(),
                'fuente': 'Orden Jurídico Nacional - ordenjuridico.gob.mx',
                'metodo': 'Scraping exhaustivo con rangos prioritarios',
                'total_enlaces': len(self.documentos_encontrados),
                'total_leyes_federales': self.contadores['leyes_federales'],
                'total_reglamentos_federales': self.contadores['reglamentos_federales'],
                'total_decretos': self.contadores['decretos'],
                'total_acuerdos': self.contadores['acuerdos'],
                'total_constituciones': self.contadores['constituciones'],
                'total_otros': self.contadores['otros'],
                'objetivo_leyes': 302,
                'objetivo_reglamentos': 135,
                'porcentaje_leyes': (self.contadores['leyes_federales'] / 302) * 100,
                'porcentaje_reglamentos': (self.contadores['reglamentos_federales'] / 135) * 100,
                'codigos_explorados': len(self.codigos_validos)
            }
        }
        
        resultado.update(documentos_organizados)
        
        # Guardar JSON
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        # Guardar URLs para scraper
        with open(archivo_urls, 'w', encoding='utf-8') as f:
            f.write(f"# URLs Exhaustivas - Orden Jurídico Nacional\n")
            f.write(f"# Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total URLs: {len(self.documentos_encontrados)}\n\n")
            
            for doc in self.documentos_encontrados:
                f.write(f"# {doc['tipo'].upper()}: {doc['titulo'][:60]}...\n")
                f.write(f"{doc['url']}\n\n")
        
        logger.success(f"Resultados guardados en: {archivo_json}")
        logger.success(f"URLs guardadas en: {archivo_urls}")
        
        return resultado

def main():
    """Función principal"""
    scraper = ScraperExhaustivo()
    
    try:
        # Explorar exhaustivamente
        scraper.explorar_rango_completo(
            inicio=1,
            fin=150000,  # Reducir rango inicial
            batch_size=25,  # Lotes más pequeños
            max_workers=2   # Menos workers para estabilidad
        )
        
        # Guardar resultados
        resultado = scraper.guardar_resultados()
        
        # Mostrar resumen final
        logger.success("\n" + "="*60)
        logger.success("SCRAPING EXHAUSTIVO COMPLETADO")
        logger.success("="*60)
        logger.success(f"Total documentos encontrados: {len(scraper.documentos_encontrados)}")
        logger.success(f"Leyes federales: {scraper.contadores['leyes_federales']}/302 ({scraper.contadores['leyes_federales']/302*100:.1f}%)")
        logger.success(f"Reglamentos federales: {scraper.contadores['reglamentos_federales']}/135 ({scraper.contadores['reglamentos_federales']/135*100:.1f}%)")
        logger.success(f"Decretos: {scraper.contadores['decretos']}")
        logger.success(f"Acuerdos: {scraper.contadores['acuerdos']}")
        logger.success(f"Constituciones: {scraper.contadores['constituciones']}")
        logger.success(f"Otros: {scraper.contadores['otros']}")
        logger.success("="*60)
        
        print("\n✓ Scraping exhaustivo completado exitosamente")
        print(f"  - Archivo principal: enlaces_exhaustivos_completos.json")
        print(f"  - URLs para scraper: urls_exhaustivas_completas.txt")
        print(f"  - Leyes federales: {scraper.contadores['leyes_federales']}")
        print(f"  - Reglamentos federales: {scraper.contadores['reglamentos_federales']}")
        print(f"  - Total documentos: {len(scraper.documentos_encontrados)}")
        
    except KeyboardInterrupt:
        logger.warning("Scraping interrumpido por el usuario")
        # Guardar resultados parciales
        if scraper.documentos_encontrados:
            scraper.guardar_resultados("enlaces_exhaustivos_parciales.json", 
                                     "urls_exhaustivas_parciales.txt")
            print(f"\n⚠️  Resultados parciales guardados: {len(scraper.documentos_encontrados)} documentos")
    
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")
        raise

if __name__ == "__main__":
    main()