import requests
import json
from datetime import datetime

# Configuración de la API
API_BASE_URL = "http://localhost:8000"

def test_api_health():
    """Prueba el endpoint de salud de la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/salud")
        if response.status_code == 200:
            print("✅ API está funcionando correctamente")
            data = response.json()
            print(f"Estado: {data['estado']}")
            print(f"Vectores en BD: {data['base_datos']['vectores_totales']}")
            return True
        else:
            print(f"❌ Error en API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def test_api_stats():
    """Prueba el endpoint de estadísticas"""
    try:
        response = requests.get(f"{API_BASE_URL}/estadisticas")
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Estadísticas de la Base de Datos:")
            print(f"Índice: {data['base_datos']['nombre_indice']}")
            print(f"Vectores totales: {data['base_datos']['vectores_totales']}")
            print(f"Dimensión: {data['base_datos']['dimension']}")
            print(f"Modelo: {data['base_datos']['modelo_embedding']}")
            return True
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_legal_query(pregunta, contexto_adicional=None, max_documentos=5):
    """Prueba una consulta legal específica"""
    try:
        payload = {
            "pregunta": pregunta,
            "max_documentos": max_documentos
        }
        
        if contexto_adicional:
            payload["contexto_adicional"] = contexto_adicional
        
        print(f"\n🔍 Consultando: {pregunta}")
        print("⏳ Procesando...")
        
        response = requests.post(
            f"{API_BASE_URL}/consulta",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Respuesta obtenida:")
            print(f"📝 Pregunta: {data['pregunta']}")
            print(f"⏰ Timestamp: {data['timestamp']}")
            print(f"🎯 Confianza: {data['confianza']:.3f}")
            
            print("\n📖 Respuesta:")
            print("-" * 80)
            print(data['respuesta'])
            print("-" * 80)
            
            print(f"\n📚 Fundamentos Legales ({len(data['fundamentos_legales'])}):")            
            for i, fundamento in enumerate(data['fundamentos_legales'], 1):
                print(f"\n{i}. {fundamento['titulo']}")
                print(f"   Tipo: {fundamento['tipo']}")
                print(f"   Fuente: {fundamento['fuente']}")
                print(f"   Relevancia: {fundamento['relevancia']:.3f}")
                if fundamento['url']:
                    print(f"   URL: {fundamento['url']}")
            
            return True
            
        else:
            print(f"❌ Error en consulta: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalle: {error_data.get('detail', 'Error desconocido')}")
            except:
                print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Función principal para probar la API"""
    print("🚀 Iniciando pruebas de la API Legal Mexicana")
    print("=" * 60)
    
    # Verificar salud de la API
    if not test_api_health():
        print("❌ La API no está disponible. Asegúrate de que esté ejecutándose.")
        return
    
    # Obtener estadísticas
    test_api_stats()
    
    # Consultas de prueba
    consultas_prueba = [
        {
            "pregunta": "¿Cuáles son los derechos fundamentales en la Constitución Mexicana?",
            "contexto": "Necesito información sobre derechos humanos básicos"
        },
        {
            "pregunta": "¿Qué establece la ley sobre el salario mínimo en México?",
            "contexto": "Consulta laboral sobre remuneración"
        },
        {
            "pregunta": "¿Cuáles son las obligaciones fiscales de las empresas?",
            "contexto": "Consulta tributaria empresarial"
        }
    ]
    
    print("\n" + "=" * 60)
    print("🧪 EJECUTANDO CONSULTAS DE PRUEBA")
    print("=" * 60)
    
    for i, consulta in enumerate(consultas_prueba, 1):
        print(f"\n{'='*20} CONSULTA {i} {'='*20}")
        success = test_legal_query(
            consulta["pregunta"], 
            consulta["contexto"],
            max_documentos=3
        )
        
        if success:
            print("✅ Consulta exitosa")
        else:
            print("❌ Consulta falló")
        
        # Pausa entre consultas
        if i < len(consultas_prueba):
            input("\nPresiona Enter para continuar con la siguiente consulta...")
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")
    print("=" * 60)

if __name__ == "__main__":
    main()