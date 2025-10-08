#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador y Cargador de Documentos Legales a Pinecone
Descarga, procesa y sube documentos legales a la base de datos vectorial Pinecone
"""

import json
import os
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from loguru import logger
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('config_vectordb.env')

# Configuración de logging
logger.add("procesamiento_documentos.log", rotation="50 MB", level="INFO")

class ProcesadorDocumentosLegales:
    def __init__(self):
        self.base_url = "https://www.ordenjuridico.gob.mx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        self.session.verify = False
        
        # Configuración de directorios
        self.data_dir = Path("data")
        self.raw_dir = self.data_dir / "raw" / "orden_juridico"
        self.processed_dir = self.data_dir / "processed"
        self.embeddings_dir = self.data_dir / "embeddings"
        
        # Crear directorios si no existen
        for dir_path in [self.raw_dir, self.processed_dir, self.embeddings_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Configuración de Pinecone
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.pinecone_environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'lex-ia-legal-docs')
        
        # Modelo de embeddings
        self.embedding_model = None
        self.pinecone_index = None
        
        # Contadores y estadísticas
        self.stats = {
            'documentos_descargados': 0,
            'documentos_procesados': 0,
            'documentos_subidos': 0,
            'errores_descarga': 0,
            'errores_procesamiento': 0,
            'errores_subida': 0
        }
        
        self.lock = threading.Lock()

    def inicializar_pinecone(self):
        """Inicializa la conexión con Pinecone"""
        try:
            # Inicializar Pinecone
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Verificar si el índice existe
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creando índice {self.index_name}...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # Dimensión para paraphrase-multilingual-MiniLM-L12-v2
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.success(f"Índice {self.index_name} creado exitosamente")
            
            # Conectar al índice
            self.pinecone_index = self.pc.Index(self.index_name)
            logger.success(f"Conectado al índice Pinecone: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando Pinecone: {e}")
            return False

    def inicializar_modelo_embeddings(self):
        """Inicializa el modelo de embeddings"""
        try:
            logger.info("Cargando modelo de embeddings...")
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.success("Modelo de embeddings cargado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error cargando modelo de embeddings: {e}")
            return False

    def cargar_enlaces(self, archivo_json: str = "enlaces_exhaustivos_completos.json") -> List[Dict]:
        """Carga la lista de enlaces desde el archivo JSON"""
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraer todos los documentos
            documentos = []
            for categoria in ['leyes_federales', 'reglamentos_federales', 'decretos', 'acuerdos', 'constituciones', 'otros']:
                if categoria in data:
                    documentos.extend(data[categoria])
            
            logger.info(f"Cargados {len(documentos)} enlaces desde {archivo_json}")
            return documentos
            
        except Exception as e:
            logger.error(f"Error cargando enlaces: {e}")
            return []

    def descargar_documento(self, documento: Dict) -> Optional[Dict]:
        """Descarga un documento individual"""
        try:
            url = documento['url']
            doc_id = documento['id']
            
            # Verificar si ya existe el archivo
            archivo_raw = self.raw_dir / f"{doc_id}.html"
            if archivo_raw.exists():
                logger.debug(f"Documento {doc_id} ya existe, saltando descarga")
                return self.cargar_documento_existente(archivo_raw, documento)
            
            # Descargar documento
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                # Guardar HTML crudo
                with open(archivo_raw, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                with self.lock:
                    self.stats['documentos_descargados'] += 1
                
                logger.info(f"Descargado: {doc_id} - {documento['titulo'][:50]}...")
                return {
                    'documento': documento,
                    'html_content': response.text,
                    'archivo_raw': str(archivo_raw)
                }
            else:
                logger.warning(f"Error descargando {doc_id}: HTTP {response.status_code}")
                with self.lock:
                    self.stats['errores_descarga'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Error descargando {documento['id']}: {e}")
            with self.lock:
                self.stats['errores_descarga'] += 1
            return None

    def cargar_documento_existente(self, archivo_raw: Path, documento: Dict) -> Optional[Dict]:
        """Carga un documento ya descargado"""
        try:
            with open(archivo_raw, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return {
                'documento': documento,
                'html_content': html_content,
                'archivo_raw': str(archivo_raw)
            }
        except Exception as e:
            logger.error(f"Error cargando documento existente {archivo_raw}: {e}")
            return None

    def procesar_documento(self, data: Dict) -> Optional[Dict]:
        """Procesa un documento descargado"""
        try:
            documento = data['documento']
            html_content = data['html_content']
            doc_id = documento['id']
            
            # Parsear HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraer texto limpio
            texto_completo = self.extraer_texto_limpio(soup)
            
            if not texto_completo or len(texto_completo.strip()) < 100:
                logger.warning(f"Documento {doc_id} tiene poco contenido, saltando")
                return None
            
            # Dividir en chunks
            chunks = self.dividir_en_chunks(texto_completo)
            
            # Crear documento procesado
            documento_procesado = {
                'id': doc_id,
                'titulo': documento['titulo'],
                'url': documento['url'],
                'tipo': documento['tipo'],
                'fuente': documento.get('fuente', 'ORDEN_JURIDICO'),
                'fecha_procesamiento': datetime.now().isoformat(),
                'texto_completo': texto_completo,
                'chunks': chunks,
                'num_chunks': len(chunks),
                'longitud_texto': len(texto_completo)
            }
            
            # Guardar documento procesado
            archivo_procesado = self.processed_dir / f"{doc_id}.json"
            with open(archivo_procesado, 'w', encoding='utf-8') as f:
                json.dump(documento_procesado, f, ensure_ascii=False, indent=2)
            
            with self.lock:
                self.stats['documentos_procesados'] += 1
            
            logger.info(f"Procesado: {doc_id} - {len(chunks)} chunks")
            return documento_procesado
            
        except Exception as e:
            logger.error(f"Error procesando documento {data['documento']['id']}: {e}")
            with self.lock:
                self.stats['errores_procesamiento'] += 1
            return None

    def extraer_texto_limpio(self, soup: BeautifulSoup) -> str:
        """Extrae texto limpio del HTML"""
        # Remover scripts, estilos y otros elementos no deseados
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Obtener texto
        texto = soup.get_text()
        
        # Limpiar texto
        texto = re.sub(r'\s+', ' ', texto)  # Múltiples espacios a uno
        texto = re.sub(r'\n+', '\n', texto)  # Múltiples saltos de línea
        texto = texto.strip()
        
        return texto

    def dividir_en_chunks(self, texto: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[Dict]:
        """Divide el texto en chunks manejables"""
        chunks = []
        palabras = texto.split()
        
        i = 0
        chunk_id = 0
        
        while i < len(palabras):
            # Tomar palabras para el chunk
            chunk_palabras = palabras[i:i + max_chunk_size]
            chunk_texto = ' '.join(chunk_palabras)
            
            if chunk_texto.strip():
                chunks.append({
                    'chunk_id': chunk_id,
                    'texto': chunk_texto,
                    'inicio_palabra': i,
                    'fin_palabra': min(i + len(chunk_palabras), len(palabras)),
                    'longitud': len(chunk_texto)
                })
                chunk_id += 1
            
            # Avanzar con overlap
            i += max_chunk_size - overlap
        
        return chunks

    def generar_embeddings_y_subir(self, documento_procesado: Dict) -> bool:
        """Genera embeddings y sube a Pinecone"""
        try:
            doc_id = documento_procesado['id']
            chunks = documento_procesado['chunks']
            
            # Preparar vectores para Pinecone
            vectores = []
            
            for chunk in chunks:
                # Generar embedding
                embedding = self.embedding_model.encode(chunk['texto']).tolist()
                
                # Crear ID único para el chunk
                chunk_id = f"{doc_id}_chunk_{chunk['chunk_id']}"
                
                # Metadatos
                metadata = {
                    'documento_id': doc_id,
                    'titulo': documento_procesado['titulo'],
                    'url': documento_procesado['url'],
                    'tipo': documento_procesado['tipo'],
                    'fuente': documento_procesado['fuente'],
                    'chunk_id': chunk['chunk_id'],
                    'texto': chunk['texto'][:1000],  # Limitar texto en metadata
                    'longitud_chunk': chunk['longitud'],
                    'fecha_procesamiento': documento_procesado['fecha_procesamiento']
                }
                
                vectores.append({
                    'id': chunk_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Subir a Pinecone en lotes
            batch_size = 100
            for i in range(0, len(vectores), batch_size):
                batch = vectores[i:i + batch_size]
                self.pinecone_index.upsert(vectors=batch)
            
            with self.lock:
                self.stats['documentos_subidos'] += 1
            
            logger.success(f"Subido a Pinecone: {doc_id} - {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error subiendo documento {documento_procesado['id']} a Pinecone: {e}")
            with self.lock:
                self.stats['errores_subida'] += 1
            return False

    def procesar_lote_documentos(self, documentos: List[Dict]) -> None:
        """Procesa un lote de documentos"""
        for documento in documentos:
            try:
                # Descargar
                data_descarga = self.descargar_documento(documento)
                if not data_descarga:
                    continue
                
                # Procesar
                documento_procesado = self.procesar_documento(data_descarga)
                if not documento_procesado:
                    continue
                
                # Generar embeddings y subir
                self.generar_embeddings_y_subir(documento_procesado)
                
                # Pausa pequeña para no sobrecargar
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error en lote procesando {documento.get('id', 'unknown')}: {e}")

    def mostrar_progreso(self):
        """Muestra el progreso actual"""
        total_procesados = self.stats['documentos_subidos'] + self.stats['errores_subida']
        logger.info(
            f"Progreso: {total_procesados} documentos | "
            f"Descargados: {self.stats['documentos_descargados']} | "
            f"Procesados: {self.stats['documentos_procesados']} | "
            f"Subidos: {self.stats['documentos_subidos']} | "
            f"Errores: {self.stats['errores_descarga'] + self.stats['errores_procesamiento'] + self.stats['errores_subida']}"
        )

    def procesar_todos_los_documentos(self, max_workers: int = 3, batch_size: int = 10):
        """Procesa todos los documentos con paralelización controlada"""
        # Cargar enlaces
        documentos = self.cargar_enlaces()
        if not documentos:
            logger.error("No se pudieron cargar los enlaces")
            return
        
        logger.info(f"Iniciando procesamiento de {len(documentos)} documentos")
        
        # Dividir en lotes
        lotes = [documentos[i:i + batch_size] for i in range(0, len(documentos), batch_size)]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for lote in lotes:
                future = executor.submit(self.procesar_lote_documentos, lote)
                futures.append(future)
            
            # Procesar resultados
            for i, future in enumerate(as_completed(futures)):
                try:
                    future.result()
                    if (i + 1) % 5 == 0:  # Mostrar progreso cada 5 lotes
                        self.mostrar_progreso()
                except Exception as e:
                    logger.error(f"Error en lote {i}: {e}")

    def generar_reporte_final(self):
        """Genera un reporte final del procesamiento"""
        reporte = {
            'fecha_procesamiento': datetime.now().isoformat(),
            'estadisticas': self.stats,
            'tasa_exito_descarga': (self.stats['documentos_descargados'] / 
                                   (self.stats['documentos_descargados'] + self.stats['errores_descarga'])) * 100 
                                   if (self.stats['documentos_descargados'] + self.stats['errores_descarga']) > 0 else 0,
            'tasa_exito_procesamiento': (self.stats['documentos_procesados'] / 
                                        (self.stats['documentos_procesados'] + self.stats['errores_procesamiento'])) * 100 
                                        if (self.stats['documentos_procesados'] + self.stats['errores_procesamiento']) > 0 else 0,
            'tasa_exito_subida': (self.stats['documentos_subidos'] / 
                                 (self.stats['documentos_subidos'] + self.stats['errores_subida'])) * 100 
                                 if (self.stats['documentos_subidos'] + self.stats['errores_subida']) > 0 else 0
        }
        
        # Guardar reporte
        with open('reporte_procesamiento.json', 'w', encoding='utf-8') as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)
        
        logger.success("\n" + "="*60)
        logger.success("REPORTE FINAL DE PROCESAMIENTO")
        logger.success("="*60)
        logger.success(f"Documentos descargados: {self.stats['documentos_descargados']}")
        logger.success(f"Documentos procesados: {self.stats['documentos_procesados']}")
        logger.success(f"Documentos subidos a Pinecone: {self.stats['documentos_subidos']}")
        logger.success(f"Errores de descarga: {self.stats['errores_descarga']}")
        logger.success(f"Errores de procesamiento: {self.stats['errores_procesamiento']}")
        logger.success(f"Errores de subida: {self.stats['errores_subida']}")
        logger.success(f"Tasa de éxito general: {reporte['tasa_exito_subida']:.1f}%")
        logger.success("="*60)
        
        return reporte

def main():
    """Función principal"""
    procesador = ProcesadorDocumentosLegales()
    
    try:
        # Inicializar componentes
        logger.info("Inicializando procesador de documentos legales...")
        
        if not procesador.inicializar_pinecone():
            logger.error("No se pudo inicializar Pinecone. Verifica la configuración.")
            return
        
        if not procesador.inicializar_modelo_embeddings():
            logger.error("No se pudo inicializar el modelo de embeddings.")
            return
        
        # Procesar todos los documentos
        procesador.procesar_todos_los_documentos(
            max_workers=2,  # Paralelización controlada
            batch_size=5    # Lotes pequeños para mejor control
        )
        
        # Generar reporte final
        reporte = procesador.generar_reporte_final()
        
        print("\n✓ Procesamiento completado exitosamente")
        print(f"  - Documentos subidos a Pinecone: {procesador.stats['documentos_subidos']}")
        print(f"  - Tasa de éxito: {reporte['tasa_exito_subida']:.1f}%")
        print(f"  - Reporte guardado en: reporte_procesamiento.json")
        
    except KeyboardInterrupt:
        logger.warning("Procesamiento interrumpido por el usuario")
        procesador.generar_reporte_final()
        print(f"\n⚠️  Procesamiento interrumpido. Documentos procesados: {procesador.stats['documentos_subidos']}")
    
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}")
        procesador.generar_reporte_final()
        raise

if __name__ == "__main__":
    main()