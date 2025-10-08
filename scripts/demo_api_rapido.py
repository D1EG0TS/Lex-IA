import requests
import json
from datetime import datetime

# Configuración de la API
API_BASE_URL = "http://localhost:8000"

def test_api_completo():
    """Prueba completa de la API sin interacción del usuario"""
    print("🚀 Iniciando prueba completa de la API Legal Mexicana")
    print("=" * 60)
    
    # 1. Verificar salud de la API
    print("\n1️⃣ Verificando salud de la API...")
    try:
        response = requests.get(f"{API_BASE_URL}/salud")
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando correctamente")
            print(f"   Estado: {data['estado']}")
            print(f"   Vectores en BD: {data['base_datos']['vectores_totales']}")
            print(f"   Dimensión: {data['base_datos']['dimension']}")
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False
    
    # 2. Obtener estadísticas
    print("\n2️⃣ Obteniendo estadísticas...")
    try:
        response = requests.get(f"{API_BASE_URL}/estadisticas")
        if response.status_code == 200:
            data = response.json()
            print("✅ Estadísticas obtenidas")
            print(f"   Índice: {data['base_datos']['nombre_indice']}")
            print(f"   Modelo: {data['base_datos']['modelo_embedding']}")
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # 3. Realizar consulta legal
    print("\n3️⃣ Realizando consulta legal...")
    consulta = {
        "pregunta": "¿Cuáles son los derechos fundamentales establecidos en la Constitución Mexicana?",
        "contexto_adicional": "Necesito información sobre derechos humanos básicos para un caso legal",
        "max_documentos": 3
    }
    
    try:
        print(f"   Pregunta: {consulta['pregunta']}")
        print("   ⏳ Procesando...")
        
        response = requests.post(
            f"{API_BASE_URL}/consulta",
            json=consulta,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60 segundos de timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Respuesta obtenida exitosamente")
            print(f"   ⏰ Timestamp: {data['timestamp']}")
            print(f"   🎯 Confianza: {data['confianza']:.3f}")
            print(f"   📚 Fundamentos encontrados: {len(data['fundamentos_legales'])}")
            
            print("\n📖 Respuesta de la IA:")
            print("-" * 80)
            print(data['respuesta'])
            print("-" * 80)
            
            print("\n📚 Fundamentos Legales:")
            for i, fundamento in enumerate(data['fundamentos_legales'], 1):
                print(f"\n   {i}. {fundamento['titulo']}")
                print(f"      Tipo: {fundamento['tipo']}")
                print(f"      Fuente: {fundamento['fuente']}")
                print(f"      Relevancia: {fundamento['relevancia']:.3f}")
                if fundamento['url']:
                    print(f"      URL: {fundamento['url']}")
            
            print("\n✅ Consulta completada exitosamente")
            return True
            
        else:
            print(f"❌ Error en consulta: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data.get('detail', 'Error desconocido')}")
            except:
                print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout: La consulta tardó demasiado en responder")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def main():
    """Función principal"""
    success = test_api_completo()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\n✅ La API Legal Mexicana está funcionando correctamente")
        print("✅ Conexión a DeepSeek establecida")
        print("✅ Conexión a Pinecone establecida")
        print("✅ Modelo de embeddings cargado")
        print("✅ Consultas legales funcionando")
        
        print("\n🌐 Endpoints disponibles:")
        print(f"   • Documentación: {API_BASE_URL}/docs")
        print(f"   • Salud: {API_BASE_URL}/salud")
        print(f"   • Estadísticas: {API_BASE_URL}/estadisticas")
        print(f"   • Consultas: {API_BASE_URL}/consulta (POST)")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("\nVerifica que:")
        print("• La API esté ejecutándose en http://localhost:8000")
        print("• Las credenciales de Pinecone sean correctas")
        print("• La API key de DeepSeek sea válida")
    
    print("=" * 60)

if __name__ == "__main__":
    main()