#!/usr/bin/env python3
"""
Búsqueda Semántica en Base de Datos Vectorial de Documentos Legales

Este script permite realizar búsquedas semánticas en la base de datos vectorial
de documentos legales mexicanos almacenada en Pinecone.

Ejemplos de uso:
    python semantic_search.py "derechos humanos constitución"
    python semantic_search.py "impuestos federales" --category leyes_federales
    python semantic_search.py "amparo judicial" --top-k 10 --min-score 0.7

Autor: Asistente IA
Fecha: 2024
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv('config_vectordb.env')
except ImportError:
    print("Advertencia: python-dotenv no instalado. Usando variables de entorno del sistema.")

# Importar clases del script principal
try:
    from setup_pinecone_vectordb import PineconeVectorDB, EmbeddingGenerator
except ImportError:
    print("Error: No se puede importar setup_pinecone_vectordb.py")
    print("Asegúrate de que el archivo esté en el mismo directorio.")
    sys.exit(1)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    """
    Motor de búsqueda semántica para documentos legales
    """
    
    def __init__(self, pinecone_api_key: str, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 openai_api_key: Optional[str] = None, index_name: str = "legal-documents-mx"):
        """
        Inicializa el motor de búsqueda
        
        Args:
            pinecone_api_key: API key de Pinecone
            embedding_model: Modelo de embeddings a usar
            openai_api_key: API key de OpenAI (opcional)
            index_name: Nombre del índice en Pinecone
        """
        self.pinecone_api_key = pinecone_api_key
        self.embedding_model = embedding_model
        self.openai_api_key = openai_api_key
        self.index_name = index_name
        
        # Inicializar componentes
        self.embedding_generator = None
        self.vector_db = None
        
        self._initialize()
    
    def _initialize(self):
        """Inicializa los componentes del motor de búsqueda"""
        try:
            # Inicializar generador de embeddings
            logger.info(f"Inicializando modelo de embeddings: {self.embedding_model}")
            self.embedding_generator = EmbeddingGenerator(
                model_name=self.embedding_model,
                openai_api_key=self.openai_api_key
            )
            
            # Inicializar conexión con Pinecone
            logger.info("Conectando con Pinecone...")
            self.vector_db = PineconeVectorDB(api_key=self.pinecone_api_key)
            self.vector_db.index_name = self.index_name
            
            # Conectar al índice existente
            self.vector_db.index = self.vector_db.pc.Index(self.index_name)
            
            logger.info("Motor de búsqueda inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando motor de búsqueda: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5, category: Optional[str] = None,
              min_score: float = 0.0, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda semántica
        
        Args:
            query: Consulta en lenguaje natural
            top_k: Número máximo de resultados
            category: Filtrar por categoría (cpeum, leyes_federales, etc.)
            min_score: Puntuación mínima de similitud
            document_type: Filtrar por tipo de documento
        
        Returns:
            Lista de resultados ordenados por relevancia
        """
        try:
            # Generar embedding de la consulta
            logger.info(f"Generando embedding para: '{query}'")
            query_embedding = self.embedding_generator.generate_single_embedding(query)
            
            if not query_embedding:
                logger.error("Error generando embedding de la consulta")
                return []
            
            # Preparar filtros
            filter_dict = {}
            if document_type:
                filter_dict['document_type'] = document_type
            
            # Realizar búsqueda
            namespace = category if category else ""
            results = self.vector_db.query_similar(
                query_vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter_dict=filter_dict if filter_dict else None
            )
            
            # Filtrar por puntuación mínima
            filtered_results = [
                result for result in results 
                if result.get('score', 0) >= min_score
            ]
            
            logger.info(f"Encontrados {len(filtered_results)} resultados")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice"""
        if self.vector_db:
            return self.vector_db.get_index_stats()
        return {}
    
    def search_by_category(self, query: str, top_k_per_category: int = 3) -> Dict[str, List[Dict]]:
        """
        Busca en todas las categorías y retorna resultados agrupados
        
        Args:
            query: Consulta en lenguaje natural
            top_k_per_category: Número de resultados por categoría
        
        Returns:
            Diccionario con resultados por categoría
        """
        categories = ['cpeum', 'leyes_federales', 'reglamentos_federales', 'dof']
        results_by_category = {}
        
        for category in categories:
            logger.info(f"Buscando en categoría: {category}")
            results = self.search(
                query=query,
                top_k=top_k_per_category,
                category=category
            )
            
            if results:
                results_by_category[category] = results
        
        return results_by_category

def format_search_results(results: List[Dict[str, Any]], show_content: bool = False) -> str:
    """
    Formatea los resultados de búsqueda para mostrar
    
    Args:
        results: Lista de resultados
        show_content: Si mostrar el contenido completo
    
    Returns:
        String formateado con los resultados
    """
    if not results:
        return "No se encontraron resultados."
    
    output = []
    output.append(f"\n{'='*80}")
    output.append(f"RESULTADOS DE BÚSQUEDA ({len(results)} encontrados)")
    output.append(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        score = result.get('score', 0)
        
        output.append(f"{i}. {metadata.get('title', 'Sin título')}")
        output.append(f"   📁 Categoría: {metadata.get('category', 'N/A')}")
        output.append(f"   📄 Tipo: {metadata.get('document_type', 'N/A')}")
        output.append(f"   🎯 Similitud: {score:.4f}")
        output.append(f"   📅 Fecha: {metadata.get('publication_date', 'N/A')}")
        output.append(f"   🔗 URL: {metadata.get('url', 'N/A')}")
        
        if show_content and 'content' in metadata:
            content = metadata['content'][:500] + "..." if len(metadata.get('content', '')) > 500 else metadata.get('content', '')
            output.append(f"   📝 Contenido: {content}")
        
        output.append(f"   📊 Longitud: {metadata.get('content_length', 0)} caracteres")
        output.append("")
    
    return "\n".join(output)

def format_category_results(results_by_category: Dict[str, List[Dict]]) -> str:
    """
    Formatea resultados agrupados por categoría
    
    Args:
        results_by_category: Resultados por categoría
    
    Returns:
        String formateado
    """
    if not results_by_category:
        return "No se encontraron resultados en ninguna categoría."
    
    output = []
    output.append(f"\n{'='*80}")
    output.append("RESULTADOS POR CATEGORÍA")
    output.append(f"{'='*80}\n")
    
    category_names = {
        'cpeum': '🏛️  CONSTITUCIÓN POLÍTICA (CPEUM)',
        'leyes_federales': '⚖️  LEYES FEDERALES',
        'reglamentos_federales': '📋 REGLAMENTOS FEDERALES',
        'dof': '📰 DIARIO OFICIAL DE LA FEDERACIÓN'
    }
    
    for category, results in results_by_category.items():
        category_title = category_names.get(category, category.upper())
        output.append(f"{category_title}")
        output.append("-" * len(category_title))
        
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            score = result.get('score', 0)
            
            output.append(f"{i}. {metadata.get('title', 'Sin título')} (similitud: {score:.3f})")
            output.append(f"   🔗 {metadata.get('url', 'N/A')}")
        
        output.append("")
    
    return "\n".join(output)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Búsqueda semántica en documentos legales mexicanos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s "derechos humanos constitución"
  %(prog)s "impuestos federales" --category leyes_federales
  %(prog)s "amparo judicial" --top-k 10 --min-score 0.7
  %(prog)s "libertad de expresión" --all-categories
  %(prog)s "procedimiento penal" --document-type "Código"
        """
    )
    
    parser.add_argument("query", help="Consulta de búsqueda en lenguaje natural")
    parser.add_argument("--top-k", type=int, default=5, help="Número máximo de resultados (default: 5)")
    parser.add_argument("--category", choices=['cpeum', 'leyes_federales', 'reglamentos_federales', 'dof'],
                       help="Filtrar por categoría específica")
    parser.add_argument("--document-type", help="Filtrar por tipo de documento")
    parser.add_argument("--min-score", type=float, default=0.0, 
                       help="Puntuación mínima de similitud (0.0-1.0, default: 0.0)")
    parser.add_argument("--show-content", action="store_true", 
                       help="Mostrar contenido de los documentos")
    parser.add_argument("--all-categories", action="store_true",
                       help="Buscar en todas las categorías por separado")
    parser.add_argument("--model", default=None,
                       help="Modelo de embeddings (override de config)")
    parser.add_argument("--stats", action="store_true",
                       help="Mostrar estadísticas del índice")
    
    args = parser.parse_args()
    
    try:
        # Obtener configuración
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not pinecone_api_key:
            print("Error: PINECONE_API_KEY no encontrada en variables de entorno")
            print("Configura el archivo config_vectordb.env o establece la variable de entorno")
            sys.exit(1)
        
        embedding_model = args.model or os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        index_name = os.getenv('PINECONE_INDEX_NAME', 'legal-documents-mx')
        
        # Inicializar motor de búsqueda
        search_engine = SemanticSearchEngine(
            pinecone_api_key=pinecone_api_key,
            embedding_model=embedding_model,
            openai_api_key=openai_api_key,
            index_name=index_name
        )
        
        # Mostrar estadísticas si se solicita
        if args.stats:
            stats = search_engine.get_index_stats()
            print("\n📊 ESTADÍSTICAS DEL ÍNDICE")
            print("=" * 30)
            print(f"Total de vectores: {stats.get('total_vector_count', 0):,}")
            print(f"Dimensión: {stats.get('dimension', 'N/A')}")
            
            namespaces = stats.get('namespaces', {})
            if namespaces:
                print("\nVectores por categoría:")
                for namespace, ns_stats in namespaces.items():
                    count = ns_stats.get('vector_count', 0)
                    print(f"  {namespace}: {count:,} vectores")
            print()
        
        # Realizar búsqueda
        if args.all_categories:
            # Buscar en todas las categorías
            print(f"🔍 Buscando '{args.query}' en todas las categorías...")
            results_by_category = search_engine.search_by_category(
                query=args.query,
                top_k_per_category=args.top_k
            )
            print(format_category_results(results_by_category))
            
        else:
            # Búsqueda normal
            category_text = f" en {args.category}" if args.category else ""
            print(f"🔍 Buscando '{args.query}'{category_text}...")
            
            results = search_engine.search(
                query=args.query,
                top_k=args.top_k,
                category=args.category,
                min_score=args.min_score,
                document_type=args.document_type
            )
            
            print(format_search_results(results, show_content=args.show_content))
        
        # Sugerencias de mejora
        if not args.all_categories:
            print("💡 SUGERENCIAS:")
            print("   • Usa --all-categories para buscar en todas las categorías")
            print("   • Ajusta --min-score para filtrar resultados menos relevantes")
            print("   • Usa --show-content para ver el contenido de los documentos")
            print("   • Prueba términos más específicos para mejores resultados")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Búsqueda cancelada por el usuario")
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        print(f"\n❌ Error: {e}")
        print("\nVerifica que:")
        print("• El archivo config_vectordb.env esté configurado correctamente")
        print("• El índice de Pinecone exista y tenga datos")
        print("• Las dependencias estén instaladas (pip install -r requirements_vectordb.txt)")

if __name__ == "__main__":
    main()