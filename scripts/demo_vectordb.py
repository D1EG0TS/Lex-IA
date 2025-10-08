#!/usr/bin/env python3
"""
Script de Demostración - Base de Datos Vectorial para Documentos Legales

Este script demuestra el uso completo del sistema de base de datos vectorial
para documentos legales mexicanos, incluyendo:
- Configuración de Pinecone
- Generación de embeddings
- Carga de documentos
- Búsquedas semánticas
- Filtrado por categorías

Ejemplos de uso:
    python demo_vectordb.py --demo-basic
    python demo_vectordb.py --demo-search
    python demo_vectordb.py --demo-filters
    python demo_vectordb.py --demo-complete

Autor: Asistente IA
Fecha: 2024
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VectorDBDemo:
    """
    Demostración del sistema de base de datos vectorial
    """
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "config_vectordb.env"
        self.data_dir = self.project_root / "data" / "raw"
        
        # Cargar configuración
        self._load_config()
        
        # Inicializar componentes
        self.vectordb = None
        self.search_engine = None
        self._initialize_components()
    
    def _load_config(self):
        """Carga la configuración desde el archivo de entorno"""
        try:
            if self.config_file.exists():
                from dotenv import load_dotenv
                load_dotenv(self.config_file)
                logger.info("Configuración cargada correctamente")
            else:
                logger.warning(f"Archivo {self.config_file} no encontrado")
                logger.warning("Usando configuración por defecto")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
    
    def _initialize_components(self):
        """Inicializa los componentes del sistema"""
        try:
            # Importar módulos locales
            from setup_pinecone_vectordb import PineconeVectorDB
            from semantic_search import SemanticSearchEngine
            
            # Configuración
            pinecone_key = os.getenv('PINECONE_API_KEY')
            embedding_model = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            index_name = os.getenv('PINECONE_INDEX_NAME', 'legal-documents-mx')
            
            if not pinecone_key:
                logger.error("PINECONE_API_KEY no encontrada")
                logger.error("Ejecuta: python install_vectordb.py --setup-env")
                return
            
            # Inicializar base de datos vectorial
            self.vectordb = PineconeVectorDB(
                api_key=pinecone_key,
                index_name=index_name,
                embedding_model=embedding_model
            )
            
            # Inicializar motor de búsqueda
            self.search_engine = SemanticSearchEngine(
                pinecone_api_key=pinecone_key,
                index_name=index_name,
                embedding_model=embedding_model
            )
            
            logger.info("Componentes inicializados correctamente")
            
        except ImportError as e:
            logger.error(f"Error importando módulos: {e}")
            logger.error("Asegúrate de que todos los archivos estén presentes")
        except Exception as e:
            logger.error(f"Error inicializando componentes: {e}")
    
    def demo_basic_setup(self) -> bool:
        """
        Demostración básica: configuración y conexión
        
        Returns:
            bool: True si la demostración fue exitosa
        """
        print("\n" + "="*60)
        print("🚀 DEMOSTRACIÓN BÁSICA - CONFIGURACIÓN Y CONEXIÓN")
        print("="*60)
        
        try:
            if not self.vectordb:
                logger.error("Base de datos vectorial no inicializada")
                return False
            
            # 1. Verificar conexión
            print("\n1️⃣ Verificando conexión con Pinecone...")
            if self.vectordb.pc:
                indexes = self.vectordb.pc.list_indexes()
                print(f"   ✅ Conexión exitosa")
                print(f"   📊 Índices disponibles: {len(indexes.names())}")
                
                for idx_name in indexes.names():
                    print(f"      - {idx_name}")
            
            # 2. Verificar índice
            print("\n2️⃣ Verificando índice de documentos legales...")
            index_name = self.vectordb.index_name
            
            if index_name in [idx.name for idx in self.vectordb.pc.list_indexes()]:
                print(f"   ✅ Índice '{index_name}' existe")
                
                # Obtener estadísticas
                stats = self.vectordb.get_index_stats()
                if stats:
                    print(f"   📈 Vectores almacenados: {stats.get('total_vector_count', 0):,}")
                    print(f"   💾 Dimensión: {stats.get('dimension', 'N/A')}")
                    
                    # Mostrar distribución por categorías
                    namespaces = stats.get('namespaces', {})
                    if namespaces:
                        print("   📂 Distribución por categorías:")
                        for namespace, info in namespaces.items():
                            count = info.get('vector_count', 0)
                            print(f"      - {namespace}: {count:,} documentos")
            else:
                print(f"   ⚠️  Índice '{index_name}' no existe")
                print("   💡 Ejecuta: python setup_pinecone_vectordb.py --create-index")
            
            # 3. Verificar modelo de embeddings
            print("\n3️⃣ Verificando modelo de embeddings...")
            model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            print(f"   🧠 Modelo: {model_name}")
            
            # Probar generación de embedding
            test_text = "Constitución Política de los Estados Unidos Mexicanos"
            embeddings = self.vectordb.embedding_generator.generate_embeddings([test_text])
            embedding = embeddings[0] if embeddings else None
            
            if embedding:
                print(f"   ✅ Embedding generado correctamente")
                print(f"   📏 Dimensión: {len(embedding)}")
                print(f"   🔢 Primeros 5 valores: {embedding[:5]}")
            
            print("\n✅ Demostración básica completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en demostración básica: {e}")
            return False
    
    def demo_search_capabilities(self) -> bool:
        """
        Demostración de capacidades de búsqueda semántica
        
        Returns:
            bool: True si la demostración fue exitosa
        """
        print("\n" + "="*60)
        print("🔍 DEMOSTRACIÓN - BÚSQUEDAS SEMÁNTICAS")
        print("="*60)
        
        try:
            if not self.search_engine:
                logger.error("Motor de búsqueda no inicializado")
                return False
            
            # Consultas de ejemplo
            queries = [
                {
                    "query": "derechos humanos y garantías individuales",
                    "description": "Búsqueda sobre derechos fundamentales",
                    "filters": None
                },
                {
                    "query": "impuestos federales y contribuciones",
                    "description": "Búsqueda sobre materia fiscal",
                    "filters": {"category": "leyes_federales"}
                },
                {
                    "query": "procedimiento penal y justicia",
                    "description": "Búsqueda sobre derecho procesal penal",
                    "filters": None
                },
                {
                    "query": "educación pública y sistema educativo",
                    "description": "Búsqueda sobre educación",
                    "filters": {"category": "cpeum"}
                }
            ]
            
            for i, query_info in enumerate(queries, 1):
                print(f"\n{i}️⃣ {query_info['description']}")
                print(f"   🔎 Consulta: \"{query_info['query']}\"")
                
                if query_info['filters']:
                    print(f"   🏷️  Filtros: {query_info['filters']}")
                
                try:
                    # Realizar búsqueda
                    search_params = {
                        'query': query_info['query'],
                        'top_k': 3,
                        'min_score': 0.7
                    }
                    
                    # Agregar filtros si existen
                    if query_info['filters']:
                        if 'category' in query_info['filters']:
                            search_params['category'] = query_info['filters']['category']
                        if 'document_type' in query_info['filters']:
                            search_params['document_type'] = query_info['filters']['document_type']
                    
                    results = self.search_engine.search(**search_params)
                    
                    if results:
                        print(f"   📊 Resultados encontrados: {len(results)}")
                        
                        for j, result in enumerate(results, 1):
                            metadata = result.get('metadata', {})
                            score = result.get('score', 0)
                            
                            print(f"\n      {j}. {metadata.get('title', 'Sin título')}")
                            print(f"         📈 Relevancia: {score:.3f}")
                            print(f"         🏷️  Categoría: {metadata.get('category', 'N/A')}")
                            print(f"         📄 Tipo: {metadata.get('document_type', 'N/A')}")
                            
                            # Mostrar fragmento del contenido
                            content = result.get('content', '')
                            if content:
                                preview = content[:200] + "..." if len(content) > 200 else content
                                print(f"         📝 Contenido: {preview}")
                    else:
                        print("   ❌ No se encontraron resultados")
                
                except Exception as e:
                    print(f"   ❌ Error en búsqueda: {e}")
                
                print("   " + "-"*50)
            
            print("\n✅ Demostración de búsquedas completada")
            return True
            
        except Exception as e:
            logger.error(f"Error en demostración de búsquedas: {e}")
            return False
    
    def demo_filtering_capabilities(self) -> bool:
        """
        Demostración de capacidades de filtrado
        
        Returns:
            bool: True si la demostración fue exitosa
        """
        print("\n" + "="*60)
        print("🏷️ DEMOSTRACIÓN - FILTRADO Y CATEGORIZACIÓN")
        print("="*60)
        
        try:
            if not self.search_engine:
                logger.error("Motor de búsqueda no inicializado")
                return False
            
            base_query = "derechos y obligaciones"
            
            # Filtros de ejemplo
            filter_examples = [
                {
                    "name": "Solo Constitución",
                    "filters": {"category": "cpeum"},
                    "description": "Buscar solo en la Constitución"
                },
                {
                    "name": "Solo Leyes Federales",
                    "filters": {"category": "leyes_federales"},
                    "description": "Buscar solo en leyes federales"
                },
                {
                    "name": "Solo Reglamentos",
                    "filters": {"category": "reglamentos_federales"},
                    "description": "Buscar solo en reglamentos"
                },
                {
                    "name": "Documentos Recientes",
                    "filters": {"year": {"$gte": 2020}},
                    "description": "Documentos del 2020 en adelante"
                }
            ]
            
            print(f"\n🔎 Consulta base: \"{base_query}\"")
            print("\n📊 Comparando resultados con diferentes filtros:")
            
            for i, filter_info in enumerate(filter_examples, 1):
                print(f"\n{i}️⃣ {filter_info['name']}")
                print(f"   📝 {filter_info['description']}")
                print(f"   🏷️  Filtros: {filter_info['filters']}")
                
                try:
                    results = self.search_engine.search(
                        query=base_query,
                        top_k=5,
                        filters=filter_info['filters'],
                        min_score=0.6
                    )
                    
                    if results:
                        print(f"   📊 Resultados: {len(results)}")
                        
                        # Mostrar distribución por tipo
                        categories = {}
                        for result in results:
                            cat = result.get('metadata', {}).get('category', 'unknown')
                            categories[cat] = categories.get(cat, 0) + 1
                        
                        print("   📂 Distribución:")
                        for cat, count in categories.items():
                            print(f"      - {cat}: {count}")
                        
                        # Mostrar mejor resultado
                        best = results[0]
                        metadata = best.get('metadata', {})
                        print(f"   🏆 Mejor resultado: {metadata.get('title', 'Sin título')}")
                        print(f"      📈 Relevancia: {best.get('score', 0):.3f}")
                    else:
                        print("   ❌ No se encontraron resultados")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            # Demostrar búsqueda sin filtros
            print(f"\n🌐 Sin filtros (todos los documentos):")
            try:
                all_results = self.search_engine.search(
                    query=base_query,
                    top_k=10,
                    min_score=0.6
                )
                
                if all_results:
                    print(f"   📊 Total de resultados: {len(all_results)}")
                    
                    # Distribución por categoría
                    categories = {}
                    for result in all_results:
                        cat = result.get('metadata', {}).get('category', 'unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    print("   📂 Distribución por categoría:")
                    for cat, count in sorted(categories.items()):
                        print(f"      - {cat}: {count}")
            
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("\n✅ Demostración de filtrado completada")
            return True
            
        except Exception as e:
            logger.error(f"Error en demostración de filtrado: {e}")
            return False
    
    def demo_complete_workflow(self) -> bool:
        """
        Demostración del flujo completo de trabajo
        
        Returns:
            bool: True si la demostración fue exitosa
        """
        print("\n" + "="*60)
        print("🔄 DEMOSTRACIÓN COMPLETA - FLUJO DE TRABAJO")
        print("="*60)
        
        try:
            # 1. Verificar estado del sistema
            print("\n1️⃣ Verificando estado del sistema...")
            if not self.demo_basic_setup():
                return False
            
            # 2. Mostrar estadísticas generales
            print("\n2️⃣ Estadísticas generales...")
            if self.vectordb:
                stats = self.vectordb.get_index_stats()
                if stats:
                    total_docs = stats.get('total_vector_count', 0)
                    print(f"   📊 Total de documentos: {total_docs:,}")
                    
                    if total_docs > 0:
                        # Calcular uso de almacenamiento estimado
                        dimension = stats.get('dimension', 384)
                        storage_per_vector = dimension * 4 + 1024  # 4 bytes por float + metadata
                        total_storage_mb = (total_docs * storage_per_vector) / (1024 * 1024)
                        
                        print(f"   💾 Almacenamiento estimado: {total_storage_mb:.1f} MB")
                        print(f"   📏 Dimensión de embeddings: {dimension}")
                        
                        # Porcentaje del límite gratuito (2GB)
                        free_limit_mb = 2 * 1024
                        usage_percent = (total_storage_mb / free_limit_mb) * 100
                        print(f"   📈 Uso del tier gratuito: {usage_percent:.1f}%")
            
            # 3. Casos de uso prácticos
            print("\n3️⃣ Casos de uso prácticos...")
            
            practical_cases = [
                {
                    "case": "Investigación Constitucional",
                    "query": "libertad de expresión y prensa",
                    "filters": {"category": "cpeum"}
                },
                {
                    "case": "Consulta Fiscal",
                    "query": "impuesto sobre la renta personas físicas",
                    "filters": {"category": "leyes_federales"}
                },
                {
                    "case": "Procedimiento Administrativo",
                    "query": "recurso de revisión administrativa",
                    "filters": {"category": "reglamentos_federales"}
                }
            ]
            
            for case in practical_cases:
                print(f"\n   📋 {case['case']}")
                print(f"      🔎 Consulta: \"{case['query']}\"")
                
                try:
                    results = self.search_engine.search(
                        query=case['query'],
                        top_k=2,
                        filters=case['filters'],
                        min_score=0.7
                    )
                    
                    if results:
                        print(f"      ✅ {len(results)} resultado(s) relevante(s)")
                        best = results[0]
                        metadata = best.get('metadata', {})
                        print(f"      🏆 Más relevante: {metadata.get('title', 'Sin título')}")
                        print(f"      📈 Relevancia: {best.get('score', 0):.3f}")
                    else:
                        print("      ❌ No se encontraron resultados")
                
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            
            # 4. Recomendaciones
            print("\n4️⃣ Recomendaciones para optimización...")
            
            if self.vectordb:
                stats = self.vectordb.get_index_stats()
                if stats:
                    total_docs = stats.get('total_vector_count', 0)
                    
                    if total_docs < 100:
                        print("   💡 Considera cargar más documentos para mejorar la cobertura")
                    elif total_docs > 50000:
                        print("   ⚠️  Gran volumen de documentos - considera optimizar consultas")
                    
                    # Verificar distribución
                    namespaces = stats.get('namespaces', {})
                    if len(namespaces) < 2:
                        print("   💡 Considera diversificar las categorías de documentos")
            
            print("\n✅ Demostración completa finalizada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en demostración completa: {e}")
            return False
    
    def show_usage_tips(self):
        """Muestra consejos de uso del sistema"""
        print("\n" + "="*60)
        print("💡 CONSEJOS DE USO")
        print("="*60)
        
        tips = [
            "🎯 Usa consultas específicas para mejores resultados",
            "🏷️  Aplica filtros por categoría para búsquedas focalizadas",
            "📊 Ajusta el min_score según la precisión requerida (0.7-0.9)",
            "🔄 Combina múltiples consultas para análisis comparativo",
            "💾 Monitorea el uso de almacenamiento en el tier gratuito",
            "🧠 Experimenta con diferentes modelos de embeddings",
            "📝 Usa sinónimos y términos relacionados en las consultas",
            "⚡ Limita top_k para consultas más rápidas",
            "🔍 Revisa los metadatos para contexto adicional",
            "📈 Analiza los scores para evaluar la relevancia"
        ]
        
        for tip in tips:
            print(f"   {tip}")
        
        print("\n📚 RECURSOS ADICIONALES:")
        print("   • Documentación de Pinecone: https://docs.pinecone.io/")
        print("   • Sentence Transformers: https://www.sbert.net/")
        print("   • Hugging Face Models: https://huggingface.co/models")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Demostración del sistema de base de datos vectorial",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--demo-basic", action="store_true",
                       help="Demostración básica de configuración")
    parser.add_argument("--demo-search", action="store_true",
                       help="Demostración de búsquedas semánticas")
    parser.add_argument("--demo-filters", action="store_true",
                       help="Demostración de filtrado")
    parser.add_argument("--demo-complete", action="store_true",
                       help="Demostración completa")
    parser.add_argument("--show-tips", action="store_true",
                       help="Mostrar consejos de uso")
    
    args = parser.parse_args()
    
    # Si no se especifica ninguna opción, mostrar ayuda
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    demo = VectorDBDemo()
    
    try:
        if args.demo_basic:
            demo.demo_basic_setup()
        
        if args.demo_search:
            demo.demo_search_capabilities()
        
        if args.demo_filters:
            demo.demo_filtering_capabilities()
        
        if args.demo_complete:
            demo.demo_complete_workflow()
        
        if args.show_tips:
            demo.show_usage_tips()
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Demostración cancelada por el usuario")
    except Exception as e:
        logger.error(f"Error en demostración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()