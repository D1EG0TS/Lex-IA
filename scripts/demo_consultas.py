#!/usr/bin/env python3
"""
Demo de consultas a la base de datos vectorial de documentos legales mexicanos.
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from loguru import logger

def realizar_consulta_demo():
    """Realiza consultas de demostración a la base de datos vectorial."""
    
    print("🚀 Inicializando conexión a la base de datos vectorial...")
    
    # Cargar configuración
    load_dotenv('config_vectordb.env')
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME', 'legal-documents-mx')
    
    # Conectar a Pinecone
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # Cargar modelo de embeddings
    modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    print("✅ Conexión establecida exitosamente\n")
    
    # Consultas de demostración
    consultas = [
        "¿Qué dice la constitución sobre derechos humanos?",
        "Código penal federal homicidio",
        "Ley del trabajo horas extras",
        "Procedimientos administrativos gobierno",
        "Impuestos y contribuciones federales"
    ]
    
    for i, consulta in enumerate(consultas, 1):
        print(f"🔍 Consulta {i}: {consulta}")
        print("=" * 60)
        
        # Generar embedding
        embedding = modelo.encode(consulta, convert_to_tensor=False).tolist()
        
        # Buscar en Pinecone
        resultados = index.query(
            vector=embedding,
            top_k=3,
            include_metadata=True
        )
        
        # Mostrar resultados
        for j, match in enumerate(resultados['matches'], 1):
            metadata = match['metadata']
            score = match['score']
            
            print(f"\n📄 Resultado {j} (Relevancia: {score:.4f})")
            print(f"📋 Título: {metadata.get('titulo', 'Sin título')[:80]}...")
            print(f"🔗 URL: {metadata.get('url', 'Sin URL')}")
            print(f"📂 Tipo: {metadata.get('tipo', 'Sin tipo')}")
            
            # Mostrar extracto del contenido
            if 'chunk_text' in metadata:
                contenido = metadata['chunk_text'][:200]
                print(f"📝 Extracto: {contenido}...")
        
        print("\n" + "=" * 60 + "\n")
    
    # Estadísticas del índice
    print("📊 Estadísticas de la base de datos:")
    stats = index.describe_index_stats()
    print(f"📈 Total de vectores: {stats['total_vector_count']}")
    print(f"📏 Dimensión: {stats['dimension']}")
    
if __name__ == "__main__":
    realizar_consulta_demo()