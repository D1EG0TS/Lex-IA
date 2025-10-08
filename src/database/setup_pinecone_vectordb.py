#!/usr/bin/env python3
"""
Configuración de Base de Datos Vectorial con Pinecone (Tier Gratuito)

Este script configura una base de datos vectorial usando Pinecone en modo gratuito
para almacenar y buscar documentos legales extraídos por web scraping.

Prioridades de almacenamiento (dentro del límite de 2GB):
1. CPEUM (Constitución Política de los Estados Unidos Mexicanos)
2. Leyes Federales
3. Reglamentos Federales
4. Publicaciones del DOF (si queda espacio)

Modelos de embeddings recomendados (gratuitos/bajo costo):
- sentence-transformers/all-MiniLM-L6-v2 (gratuito, local)
- intfloat/e5-base-v2 (gratuito, local, mejor rendimiento)
- OpenAI text-embedding-ada-002 (bajo costo, API)

Autor: Asistente IA
Fecha: 2024
"""

import os
import json
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import time
from datetime import datetime

# Dependencias principales
try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("Error: Instala pinecone-client: pip install pinecone-client")
    exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: Instala sentence-transformers: pip install sentence-transformers")
    exit(1)

try:
    import openai
except ImportError:
    print("Advertencia: OpenAI no instalado. Instala con: pip install openai")
    openai = None

try:
    import numpy as np
except ImportError:
    print("Error: Instala numpy: pip install numpy")
    exit(1)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pinecone_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PineconeVectorDB:
    """
    Clase para manejar la base de datos vectorial de Pinecone
    """
    
    def __init__(self, api_key: str, environment: str = "us-east-1", index_name: str = "legal-documents-mx", embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa la conexión con Pinecone
        
        Args:
            api_key: API key de Pinecone
            environment: Región de Pinecone (default: us-east-1 para tier gratuito)
            index_name: Nombre del índice de Pinecone
            embedding_model: Modelo de embeddings a usar
        """
        self.api_key = api_key
        self.environment = environment
        self.pc = None
        self.index = None
        self.index_name = index_name
        self.embedding_model = embedding_model
        
        # Límites del tier gratuito
        self.max_storage_gb = 2.0
        self.max_vectors_approx = 100000  # Para embeddings de 384 dimensiones
        
        # Inicializar generador de embeddings
        self.embedding_generator = None
        
        self._connect()
        self._initialize_embedding_generator()
    
    def _initialize_embedding_generator(self):
        """Inicializa el generador de embeddings"""
        try:
            self.embedding_generator = EmbeddingGenerator(model_name=self.embedding_model)
        except Exception as e:
            logger.error(f"Error inicializando generador de embeddings: {e}")
            self.embedding_generator = None
    
    def _connect(self):
        """Establece conexión con Pinecone"""
        try:
            self.pc = Pinecone(api_key=self.api_key)
            logger.info("Conexión exitosa con Pinecone")
        except Exception as e:
            logger.error(f"Error conectando con Pinecone: {e}")
            raise
    
    def create_index(self, dimension: int = 384, metric: str = "cosine"):
        """
        Crea un índice en Pinecone
        
        Args:
            dimension: Dimensión de los embeddings (384 para MiniLM, 768 para e5-base)
            metric: Métrica de similitud (cosine, euclidean, dotproduct)
        """
        try:
            # Verificar si el índice ya existe
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name in existing_indexes:
                logger.info(f"El índice '{self.index_name}' ya existe")
                self.index = self.pc.Index(self.index_name)
                return
            
            # Crear nuevo índice serverless (gratuito)
            logger.info(f"Creando índice '{self.index_name}' con dimensión {dimension}")
            
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self.environment
                )
            )
            
            # Esperar a que el índice esté listo
            logger.info("Esperando a que el índice esté listo...")
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Índice '{self.index_name}' creado exitosamente")
            
        except Exception as e:
            logger.error(f"Error creando índice: {e}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice"""
        if not self.index:
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def upsert_vectors(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]], 
                      namespace: str = "") -> bool:
        """
        Inserta vectores en el índice
        
        Args:
            vectors: Lista de tuplas (id, vector, metadata)
            namespace: Namespace para organizar vectores
        
        Returns:
            bool: True si la inserción fue exitosa
        """
        if not self.index:
            logger.error("Índice no inicializado")
            return False
        
        try:
            # Insertar en lotes de 100 (límite recomendado)
            batch_size = 100
            total_vectors = len(vectors)
            
            for i in range(0, total_vectors, batch_size):
                batch = vectors[i:i + batch_size]
                
                # Formatear para Pinecone
                formatted_vectors = [
                    {
                        "id": vec_id,
                        "values": values,
                        "metadata": metadata
                    }
                    for vec_id, values, metadata in batch
                ]
                
                self.index.upsert(
                    vectors=formatted_vectors,
                    namespace=namespace
                )
                
                logger.info(f"Insertados {min(i + batch_size, total_vectors)}/{total_vectors} vectores")
            
            return True
            
        except Exception as e:
            logger.error(f"Error insertando vectores: {e}")
            return False
    
    def query_similar(self, query_vector: List[float], top_k: int = 10, 
                     namespace: str = "", filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Busca vectores similares
        
        Args:
            query_vector: Vector de consulta
            top_k: Número de resultados a retornar
            namespace: Namespace a consultar
            filter_dict: Filtros de metadata
        
        Returns:
            Lista de resultados similares
        """
        if not self.index:
            logger.error("Índice no inicializado")
            return []
        
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            return results.matches
            
        except Exception as e:
            logger.error(f"Error en consulta: {e}")
            return []

class EmbeddingGenerator:
    """
    Clase para generar embeddings usando diferentes modelos
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", 
                 openai_api_key: Optional[str] = None):
        """
        Inicializa el generador de embeddings
        
        Args:
            model_name: Nombre del modelo a usar
            openai_api_key: API key de OpenAI (opcional)
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # Default para MiniLM
        self.openai_api_key = openai_api_key
        
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de embeddings"""
        try:
            if self.model_name.startswith("sentence-transformers/"):
                # Modelo local de Sentence Transformers
                model_path = self.model_name.replace("sentence-transformers/", "")
                self.model = SentenceTransformer(model_path)
                self.dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Modelo {model_path} cargado. Dimensión: {self.dimension}")
                
            elif self.model_name == "openai-ada-002":
                # Modelo de OpenAI
                if not self.openai_api_key or not openai:
                    raise ValueError("Se requiere API key de OpenAI y librería openai")
                
                openai.api_key = self.openai_api_key
                self.dimension = 1536  # Dimensión de ada-002
                logger.info("Modelo OpenAI ada-002 configurado")
                
            else:
                raise ValueError(f"Modelo no soportado: {self.model_name}")
                
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos
        
        Args:
            texts: Lista de textos
        
        Returns:
            Lista de embeddings
        """
        try:
            if self.model_name.startswith("sentence-transformers/"):
                # Usar Sentence Transformers
                embeddings = self.model.encode(texts, convert_to_tensor=False)
                return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
                
            elif self.model_name == "openai-ada-002":
                # Usar OpenAI
                embeddings = []
                for text in texts:
                    response = openai.Embedding.create(
                        input=text,
                        model="text-embedding-ada-002"
                    )
                    embeddings.append(response['data'][0]['embedding'])
                return embeddings
                
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            return []
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """Genera embedding para un solo texto"""
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

class LegalDocumentProcessor:
    """
    Procesador de documentos legales con priorización
    """
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        
        # Definir prioridades y límites de almacenamiento
        self.priorities = {
            "cpeum": {"priority": 1, "max_size_mb": 50},
            "leyes_federales": {"priority": 2, "max_size_mb": 800},
            "reglamentos_federales": {"priority": 3, "max_size_mb": 600},
            "otros": {"priority": 4, "max_size_mb": 400},
            "dof": {"priority": 5, "max_size_mb": 550}
        }
    
    def load_documents_by_priority(self) -> Dict[str, List[Dict]]:
        """
        Carga documentos organizados por prioridad
        
        Returns:
            Diccionario con documentos por categoría
        """
        documents_by_category = {}
        
        for category, config in self.priorities.items():
            category_path = self.data_dir / category
            documents = []
            
            if category_path.exists():
                total_size = 0
                max_size_bytes = config["max_size_mb"] * 1024 * 1024
                
                # Cargar archivos JSON
                for json_file in category_path.glob("*.json"):
                    if total_size >= max_size_bytes:
                        logger.warning(f"Límite de tamaño alcanzado para {category}")
                        break
                    
                    try:
                        file_size = json_file.stat().st_size
                        if total_size + file_size > max_size_bytes:
                            continue
                        
                        with open(json_file, 'r', encoding='utf-8') as f:
                            doc = json.load(f)
                            doc['category'] = category
                            doc['file_path'] = str(json_file)
                            documents.append(doc)
                            total_size += file_size
                            
                    except Exception as e:
                        logger.error(f"Error cargando {json_file}: {e}")
                
                logger.info(f"Cargados {len(documents)} documentos de {category} ({total_size/1024/1024:.1f} MB)")
            
            documents_by_category[category] = documents
        
        return documents_by_category
    
    def prepare_texts_for_embedding(self, documents: List[Dict]) -> List[Tuple[str, str, Dict]]:
        """
        Prepara textos para generar embeddings
        
        Args:
            documents: Lista de documentos
        
        Returns:
            Lista de tuplas (id, texto, metadata)
        """
        prepared_texts = []
        
        for doc in documents:
            try:
                # Crear ID único
                doc_id = f"{doc.get('category', 'unknown')}_{doc.get('id', 'unknown')}"
                
                # Preparar texto para embedding (título + contenido truncado)
                title = doc.get('title', '')
                content = doc.get('content', '')
                
                # Truncar contenido si es muy largo (max 8000 caracteres)
                if len(content) > 8000:
                    content = content[:8000] + "..."
                
                text_for_embedding = f"{title}\n\n{content}"
                
                # Preparar metadata
                metadata = {
                    'id': doc.get('id', ''),
                    'title': title,
                    'category': doc.get('category', ''),
                    'document_type': doc.get('document_type', ''),
                    'source': doc.get('source', ''),
                    'publication_date': doc.get('publication_date', ''),
                    'url': doc.get('url', ''),
                    'file_path': doc.get('file_path', ''),
                    'content_length': len(doc.get('content', ''))
                }
                
                prepared_texts.append((doc_id, text_for_embedding, metadata))
                
            except Exception as e:
                logger.error(f"Error preparando documento {doc.get('id', 'unknown')}: {e}")
        
        return prepared_texts

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Configurar base de datos vectorial con Pinecone")
    parser.add_argument("--pinecone-key", required=True, help="API key de Pinecone")
    parser.add_argument("--openai-key", help="API key de OpenAI (opcional)")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", 
                       choices=[
                           "sentence-transformers/all-MiniLM-L6-v2",
                           "sentence-transformers/all-mpnet-base-v2", 
                           "intfloat/e5-base-v2",
                           "openai-ada-002"
                       ],
                       help="Modelo de embeddings a usar")
    parser.add_argument("--data-dir", default="data/raw", help="Directorio de datos")
    parser.add_argument("--create-index", action="store_true", help="Crear nuevo índice")
    parser.add_argument("--load-documents", action="store_true", help="Cargar documentos")
    parser.add_argument("--test-search", help="Probar búsqueda con consulta")
    
    args = parser.parse_args()
    
    try:
        # Inicializar generador de embeddings
        logger.info(f"Inicializando modelo de embeddings: {args.model}")
        embedding_gen = EmbeddingGenerator(
            model_name=args.model,
            openai_api_key=args.openai_key
        )
        
        # Inicializar Pinecone
        logger.info("Conectando con Pinecone...")
        vector_db = PineconeVectorDB(api_key=args.pinecone_key)
        
        # Crear índice si se solicita
        if args.create_index:
            vector_db.create_index(dimension=embedding_gen.dimension)
        
        # Cargar documentos si se solicita
        if args.load_documents:
            logger.info("Cargando documentos por prioridad...")
            processor = LegalDocumentProcessor(data_dir=args.data_dir)
            documents_by_category = processor.load_documents_by_priority()
            
            # Procesar por prioridad
            total_vectors = 0
            for category in sorted(processor.priorities.keys(), 
                                 key=lambda x: processor.priorities[x]["priority"]):
                
                documents = documents_by_category.get(category, [])
                if not documents:
                    logger.info(f"No hay documentos para {category}")
                    continue
                
                logger.info(f"Procesando {len(documents)} documentos de {category}")
                
                # Preparar textos
                prepared_texts = processor.prepare_texts_for_embedding(documents)
                
                # Generar embeddings
                texts = [text for _, text, _ in prepared_texts]
                logger.info(f"Generando embeddings para {len(texts)} textos...")
                embeddings = embedding_gen.generate_embeddings(texts)
                
                if not embeddings:
                    logger.error(f"Error generando embeddings para {category}")
                    continue
                
                # Preparar vectores para Pinecone
                vectors = [
                    (doc_id, embedding, metadata)
                    for (doc_id, _, metadata), embedding in zip(prepared_texts, embeddings)
                ]
                
                # Insertar en Pinecone
                success = vector_db.upsert_vectors(vectors, namespace=category)
                if success:
                    total_vectors += len(vectors)
                    logger.info(f"Insertados {len(vectors)} vectores de {category}")
                else:
                    logger.error(f"Error insertando vectores de {category}")
                
                # Verificar límites
                stats = vector_db.get_index_stats()
                if stats and 'total_vector_count' in stats:
                    if stats['total_vector_count'] >= vector_db.max_vectors_approx:
                        logger.warning("Límite de vectores alcanzado")
                        break
            
            logger.info(f"Proceso completado. Total de vectores insertados: {total_vectors}")
        
        # Probar búsqueda si se solicita
        if args.test_search:
            logger.info(f"Probando búsqueda: '{args.test_search}'")
            query_embedding = embedding_gen.generate_single_embedding(args.test_search)
            
            if query_embedding:
                results = vector_db.query_similar(query_embedding, top_k=5)
                
                print(f"\nResultados para: '{args.test_search}'")
                print("=" * 50)
                
                for i, result in enumerate(results, 1):
                    metadata = result.get('metadata', {})
                    score = result.get('score', 0)
                    
                    print(f"{i}. {metadata.get('title', 'Sin título')}")
                    print(f"   Categoría: {metadata.get('category', 'N/A')}")
                    print(f"   Similitud: {score:.4f}")
                    print(f"   URL: {metadata.get('url', 'N/A')}")
                    print()
        
        # Mostrar estadísticas finales
        stats = vector_db.get_index_stats()
        if stats:
            print("\nEstadísticas del índice:")
            print("=" * 30)
            print(f"Total de vectores: {stats.get('total_vector_count', 0)}")
            print(f"Namespaces: {list(stats.get('namespaces', {}).keys())}")
            
            for namespace, ns_stats in stats.get('namespaces', {}).items():
                print(f"  {namespace}: {ns_stats.get('vector_count', 0)} vectores")
        
    except Exception as e:
        logger.error(f"Error en ejecución principal: {e}")
        raise

if __name__ == "__main__":
    main()