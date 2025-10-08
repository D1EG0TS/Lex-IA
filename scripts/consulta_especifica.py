#!/usr/bin/env python3
"""
Consulta específica detallada a la base de datos vectorial.
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

def consulta_detallada():
    """Realiza una consulta detallada mostrando contenido completo."""
    
    print("🔍 Consulta Detallada a la Base de Datos Vectorial")
    print("=" * 60)
    
    # Configuración
    load_dotenv('config_vectordb.env')
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME', 'legal-documents-mx')
    
    # Conectar
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # Consulta específica
    consulta = "¿Cuáles son los derechos fundamentales en la Constitución Mexicana?"
    print(f"\n🔍 Pregunta: {consulta}\n")
    
    # Generar embedding y buscar
    embedding = modelo.encode(consulta, convert_to_tensor=False).tolist()
    resultados = index.query(
        vector=embedding,
        top_k=5,
        include_metadata=True
    )
    
    print(f"✅ Encontrados {len(resultados['matches'])} documentos relevantes:\n")
    
    for i, match in enumerate(resultados['matches'], 1):
        metadata = match['metadata']
        score = match['score']
        
        print(f"📄 DOCUMENTO {i}")
        print("=" * 40)
        print(f"🎯 Relevancia: {score:.4f}")
        print(f"📋 Título: {metadata.get('titulo', 'Sin título')}")
        print(f"🔗 URL: {metadata.get('url', 'Sin URL')}")
        print(f"📂 Tipo: {metadata.get('tipo', 'Sin tipo')}")
        print(f"🏛️ Fuente: {metadata.get('fuente', 'Sin fuente')}")
        print(f"📅 Procesado: {metadata.get('fecha_procesamiento', 'Sin fecha')}")
        
        if 'chunk_text' in metadata:
            contenido = metadata['chunk_text']
            print(f"\n📝 CONTENIDO COMPLETO:")
            print("-" * 40)
            print(contenido)
        
        print("\n" + "=" * 60 + "\n")
    
    # Información adicional
    print("📊 INFORMACIÓN DE LA BASE DE DATOS:")
    print("=" * 40)
    stats = index.describe_index_stats()
    print(f"📈 Total de vectores almacenados: {stats['total_vector_count']:,}")
    print(f"📏 Dimensión de vectores: {stats['dimension']}")
    print(f"🎯 Modelo de embeddings: paraphrase-multilingual-MiniLM-L12-v2")
    print(f"🗄️ Índice de Pinecone: {index_name}")
    
if __name__ == "__main__":
    consulta_detallada()