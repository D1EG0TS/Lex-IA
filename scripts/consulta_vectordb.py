#!/usr/bin/env python3
"""
Script para realizar consultas a la base de datos vectorial de documentos legales mexicanos.
Utiliza Pinecone para búsqueda semántica de documentos jurídicos.
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from loguru import logger

class ConsultorVectorDB:
    def __init__(self):
        """Inicializa el consultor de base de datos vectorial."""
        self.pc = None
        self.index = None
        self.modelo_embeddings = None
        
        # Configurar logging
        logger.add("logs/consultas.log", rotation="10 MB")
        
    def inicializar(self):
        """Inicializa la conexión a Pinecone y carga el modelo de embeddings."""
        try:
            # Cargar variables de entorno
            load_dotenv('config_vectordb.env')
            
            api_key = os.getenv('PINECONE_API_KEY')
            index_name = os.getenv('PINECONE_INDEX_NAME', 'legal-documents-mx')
            
            if not api_key:
                raise ValueError("PINECONE_API_KEY no encontrada en config_vectordb.env")
            
            # Inicializar Pinecone
            self.pc = Pinecone(api_key=api_key)
            self.index = self.pc.Index(index_name)
            
            logger.success(f"Conectado al índice Pinecone: {index_name}")
            
            # Cargar modelo de embeddings
            logger.info("Cargando modelo de embeddings...")
            self.modelo_embeddings = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.success("Modelo de embeddings cargado exitosamente")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar: {e}")
            return False
    
    def generar_embedding(self, texto: str) -> List[float]:
        """Genera embedding para un texto dado."""
        try:
            embedding = self.modelo_embeddings.encode(texto, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error al generar embedding: {e}")
            return []
    
    def consultar(self, consulta: str, top_k: int = 5, filtros: Dict = None) -> List[Dict[str, Any]]:
        """Realiza una consulta semántica a la base de datos vectorial."""
        try:
            logger.info(f"Realizando consulta: '{consulta}'")
            
            # Generar embedding de la consulta
            embedding_consulta = self.generar_embedding(consulta)
            if not embedding_consulta:
                return []
            
            # Realizar búsqueda en Pinecone
            resultados = self.index.query(
                vector=embedding_consulta,
                top_k=top_k,
                include_metadata=True,
                filter=filtros
            )
            
            # Procesar resultados
            documentos_encontrados = []
            for match in resultados['matches']:
                documento = {
                    'id': match['id'],
                    'score': match['score'],
                    'metadata': match['metadata']
                }
                documentos_encontrados.append(documento)
            
            logger.success(f"Encontrados {len(documentos_encontrados)} documentos relevantes")
            return documentos_encontrados
            
        except Exception as e:
            logger.error(f"Error en consulta: {e}")
            return []
    
    def mostrar_resultados(self, resultados: List[Dict[str, Any]], mostrar_contenido: bool = True):
        """Muestra los resultados de manera formateada."""
        if not resultados:
            print("\n❌ No se encontraron documentos relevantes.")
            return
        
        print(f"\n✅ Encontrados {len(resultados)} documentos relevantes:\n")
        print("=" * 80)
        
        for i, doc in enumerate(resultados, 1):
            metadata = doc['metadata']
            score = doc['score']
            
            print(f"\n📄 Resultado {i} (Relevancia: {score:.4f})")
            print("-" * 50)
            print(f"📋 Título: {metadata.get('titulo', 'Sin título')}")
            print(f"🔗 URL: {metadata.get('url', 'Sin URL')}")
            print(f"📂 Tipo: {metadata.get('tipo', 'Sin tipo')}")
            print(f"🏛️ Fuente: {metadata.get('fuente', 'Sin fuente')}")
            print(f"📅 Fecha: {metadata.get('fecha_procesamiento', 'Sin fecha')}")
            
            if mostrar_contenido and 'chunk_text' in metadata:
                contenido = metadata['chunk_text'][:500]  # Primeros 500 caracteres
                print(f"\n📝 Contenido (extracto):\n{contenido}...")
            
            print("=" * 80)
    
    def consulta_interactiva(self):
        """Modo interactivo para realizar consultas."""
        print("\n🔍 Consultor de Base de Datos Vectorial - Documentos Legales Mexicanos")
        print("=" * 70)
        print("Escribe tu consulta o 'salir' para terminar.")
        print("Ejemplos:")
        print("  - ¿Qué dice sobre derechos humanos?")
        print("  - Código penal federal")
        print("  - Procedimientos administrativos")
        print("  - Constitución mexicana artículo 1")
        print("=" * 70)
        
        while True:
            try:
                consulta = input("\n🔍 Tu consulta: ").strip()
                
                if consulta.lower() in ['salir', 'exit', 'quit']:
                    print("\n👋 ¡Hasta luego!")
                    break
                
                if not consulta:
                    print("❌ Por favor ingresa una consulta válida.")
                    continue
                
                # Realizar consulta
                resultados = self.consultar(consulta, top_k=3)
                self.mostrar_resultados(resultados)
                
                # Preguntar si quiere ver más resultados
                if len(resultados) >= 3:
                    respuesta = input("\n¿Quieres ver más resultados? (s/n): ").strip().lower()
                    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                        mas_resultados = self.consultar(consulta, top_k=10)
                        self.mostrar_resultados(mas_resultados[3:])  # Mostrar del 4to en adelante
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                logger.error(f"Error en consulta interactiva: {e}")
                print(f"❌ Error: {e}")

def main():
    """Función principal."""
    consultor = ConsultorVectorDB()
    
    print("🚀 Inicializando consultor de base de datos vectorial...")
    
    if not consultor.inicializar():
        print("❌ Error al inicializar el consultor. Verifica la configuración.")
        return
    
    print("✅ Consultor inicializado exitosamente.")
    
    # Realizar algunas consultas de ejemplo
    consultas_ejemplo = [
        "derechos humanos",
        "código penal federal",
        "constitución mexicana"
    ]
    
    print("\n📋 Realizando consultas de ejemplo...")
    for consulta in consultas_ejemplo:
        print(f"\n🔍 Consultando: '{consulta}'")
        resultados = consultor.consultar(consulta, top_k=2)
        consultor.mostrar_resultados(resultados, mostrar_contenido=False)
    
    # Modo interactivo
    consultor.consulta_interactiva()

if __name__ == "__main__":
    main()