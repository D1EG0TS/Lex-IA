#!/usr/bin/env python3
"""
Script para procesar el PDF de la Constitución Política de los Estados Unidos Mexicanos
y subirlo a la base de datos vectorial de Pinecone.
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import pdfplumber
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
from loguru import logger

# Cargar variables de entorno
load_dotenv('config_vectordb.env')

# Configuración
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = 'legal-documents-mx'
EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
PDF_PATH = 'CPEUM.pdf'
OUTPUT_JSON = 'data/processed/wo14166_pdf.json'

class CPEUMProcessor:
    def __init__(self):
        self.embedding_model = None
        self.pinecone_client = None
        self.index = None
        
    def initialize_services(self):
        """Inicializar servicios de embedding y Pinecone"""
        logger.info("Inicializando modelo de embeddings...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        logger.info("Inicializando cliente de Pinecone...")
        self.pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pinecone_client.Index(PINECONE_INDEX_NAME)
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extraer texto del PDF"""
        logger.info(f"Extrayendo texto del PDF: {pdf_path}")
        text_content = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n\n--- Página {page_num} ---\n\n"
                        text_content += page_text
                        
                logger.info(f"Texto extraído exitosamente. Total de páginas: {len(pdf.pages)}")
                logger.info(f"Longitud del texto: {len(text_content)} caracteres")
                
        except Exception as e:
            logger.error(f"Error al extraer texto del PDF: {e}")
            raise
            
        return text_content
    
    def clean_text(self, text: str) -> str:
        """Limpiar y normalizar el texto"""
        # Remover caracteres de control y normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalizar saltos de línea
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def split_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Dividir el texto en chunks manejables"""
        # Dividir por artículos cuando sea posible
        article_pattern = r'(Artículo \d+[°º]?\.?)'
        parts = re.split(article_pattern, text)
        
        chunks = []
        current_chunk = ""
        
        for i, part in enumerate(parts):
            if not part.strip():
                continue
                
            # Si es un encabezado de artículo
            if re.match(article_pattern, part.strip()):
                if current_chunk and len(current_chunk) > 50:
                    chunks.append(current_chunk.strip())
                current_chunk = part.strip()
            else:
                # Agregar contenido al chunk actual
                potential_chunk = current_chunk + " " + part.strip()
                
                if len(potential_chunk) <= max_chunk_size:
                    current_chunk = potential_chunk
                else:
                    # Si el chunk actual es muy grande, guardarlo y empezar uno nuevo
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # Si la parte actual es muy grande, dividirla por oraciones
                    if len(part.strip()) > max_chunk_size:
                        sentences = re.split(r'[.!?]+', part.strip())
                        temp_chunk = ""
                        
                        for sentence in sentences:
                            if len(temp_chunk + sentence) <= max_chunk_size:
                                temp_chunk += sentence + ". "
                            else:
                                if temp_chunk:
                                    chunks.append(temp_chunk.strip())
                                temp_chunk = sentence + ". "
                        
                        current_chunk = temp_chunk
                    else:
                        current_chunk = part.strip()
        
        # Agregar el último chunk
        if current_chunk and len(current_chunk) > 50:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Texto dividido en {len(chunks)} chunks")
        return chunks
    
    def create_document_json(self, text_content: str, chunks: List[str]) -> Dict[str, Any]:
        """Crear el documento JSON con el formato estándar"""
        document = {
            "id": "wo14166_pdf",
            "titulo": "Constitución Política de los Estados Unidos Mexicanos (PDF Completo)",
            "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf",
            "tipo": "constitucion",
            "fuente": "PDF_OFICIAL",
            "fecha_procesamiento": datetime.now().isoformat(),
            "contenido_completo": text_content,
            "chunks": chunks,
            "metadatos": {
                "num_chunks": len(chunks),
                "longitud_total": len(text_content),
                "fuente_original": "Cámara de Diputados - PDF Oficial",
                "procesado_desde": "PDF"
            }
        }
        
        return document
    
    def save_processed_document(self, document: Dict[str, Any]):
        """Guardar el documento procesado"""
        os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
        
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Documento guardado en: {OUTPUT_JSON}")
    
    def upload_to_pinecone(self, document: Dict[str, Any]):
        """Subir los chunks a Pinecone"""
        logger.info("Generando embeddings y subiendo a Pinecone...")
        
        vectors_to_upsert = []
        
        for i, chunk in enumerate(document['chunks']):
            # Generar embedding
            embedding = self.embedding_model.encode(chunk).tolist()
            
            # Crear vector con metadatos
            vector_id = f"{document['id']}_chunk_{i}"
            metadata = {
                'id': document['id'],
                'titulo': document['titulo'],
                'url': document['url'],
                'tipo': document['tipo'],
                'fuente': document['fuente'],
                'chunk_index': i,
                'texto': chunk[:1000]  # Limitar texto en metadatos
            }
            
            vectors_to_upsert.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Subir en lotes
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)
            logger.info(f"Subido lote {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
        
        logger.info(f"✅ Subidos {len(vectors_to_upsert)} vectores a Pinecone")
    
    def process_cpeum(self):
        """Proceso principal"""
        try:
            logger.info("=== Iniciando procesamiento de CPEUM PDF ===")
            
            # Inicializar servicios
            self.initialize_services()
            
            # Extraer texto del PDF
            raw_text = self.extract_text_from_pdf(PDF_PATH)
            
            # Limpiar texto
            clean_text = self.clean_text(raw_text)
            
            # Dividir en chunks
            chunks = self.split_into_chunks(clean_text)
            
            # Crear documento JSON
            document = self.create_document_json(clean_text, chunks)
            
            # Guardar documento procesado
            self.save_processed_document(document)
            
            # Subir a Pinecone
            self.upload_to_pinecone(document)
            
            logger.info("=== Procesamiento completado exitosamente ===")
            logger.info(f"Documento: {document['titulo']}")
            logger.info(f"Chunks generados: {len(chunks)}")
            logger.info(f"Vectores subidos a Pinecone: {len(chunks)}")
            
        except Exception as e:
            logger.error(f"Error durante el procesamiento: {e}")
            raise

def main():
    processor = CPEUMProcessor()
    processor.process_cpeum()

if __name__ == "__main__":
    main()