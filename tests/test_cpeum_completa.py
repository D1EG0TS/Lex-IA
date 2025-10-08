#!/usr/bin/env python3
"""
Script para probar que la Constitución completa está disponible
y que las consultas sobre derechos fundamentales funcionan correctamente.
"""

import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def test_constitutional_rights():
    """Probar consultas específicas sobre derechos constitucionales"""
    
    queries = [
        "¿Cuáles son los derechos fundamentales en la Constitución Mexicana?",
        "¿Qué dice el artículo 1 de la Constitución sobre derechos humanos?",
        "¿Cuáles son las garantías individuales en México?",
        "¿Qué derechos tienen los ciudadanos mexicanos según la Constitución?",
        "¿Qué dice la Constitución sobre la libertad de expresión?"
    ]
    
    print("🔍 PROBANDO CONSULTAS SOBRE DERECHOS CONSTITUCIONALES")
    print("=" * 70)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📋 CONSULTA {i}: {query}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/consulta",
                json={"pregunta": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Respuesta generada exitosamente")
                print(f"📊 Documentos encontrados: {len(data.get('documentos_relevantes', []))}")
                
                # Mostrar documentos relevantes
                for j, doc in enumerate(data.get('documentos_relevantes', [])[:3], 1):
                    print(f"\n   {j}. {doc.get('titulo', 'Sin título')}")
                    print(f"      Tipo: {doc.get('tipo', 'N/A')}")
                    print(f"      Fuente: {doc.get('fuente', 'N/A')}")
                    print(f"      Relevancia: {doc.get('score', 0):.3f}")
                    if doc.get('fuente') == 'PDF_OFICIAL':
                        print(f"      🎯 ¡CONSTITUCIÓN COMPLETA ENCONTRADA!")
                
                # Mostrar parte de la respuesta
                respuesta = data.get('respuesta', '')
                if respuesta:
                    print(f"\n💬 Respuesta (primeros 300 caracteres):")
                    print(f"   {respuesta[:300]}...")
                
            else:
                print(f"❌ Error en la consulta: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ Error al realizar consulta: {e}")
        
        print("\n" + "="*70)

def check_database_stats():
    """Verificar estadísticas de la base de datos"""
    print("\n📊 ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/estadisticas")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Total de vectores: {stats.get('total_vectores', 'N/A')}")
            print(f"✅ Dimensiones: {stats.get('dimensiones', 'N/A')}")
            print(f"✅ Índice: {stats.get('indice', 'N/A')}")
            print(f"✅ Modelo de embeddings: {stats.get('modelo_embeddings', 'N/A')}")
        else:
            print(f"❌ Error al obtener estadísticas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🏛️ PRUEBA DE LA CONSTITUCIÓN COMPLETA EN LA BASE DE DATOS")
    print("=" * 70)
    print("\nEste script verifica que la Constitución Política de los Estados")
    print("Unidos Mexicanos completa esté disponible en la base de datos")
    print("vectorial y que las consultas sobre derechos fundamentales")
    print("funcionen correctamente.\n")
    
    # Verificar estadísticas
    check_database_stats()
    
    # Probar consultas constitucionales
    test_constitutional_rights()
    
    print("\n🎉 PRUEBA COMPLETADA")
    print("\nSi ves documentos marcados con 'PDF_OFICIAL' y respuestas")
    print("detalladas sobre derechos constitucionales, ¡la integración")
    print("de la Constitución completa fue exitosa!")

if __name__ == "__main__":
    main()