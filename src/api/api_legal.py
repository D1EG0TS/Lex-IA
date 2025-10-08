from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from openai import OpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime
from loguru import logger
import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('config_vectordb.env')

# Configurar logging
logger.add("logs/api_legal.log", rotation="10 MB", level="INFO")

# Configuración de la aplicación
app = FastAPI(
    title="API Legal Mexicana",
    description="API para consultas legales con fundamentos actualizados usando IA",
    version="1.0.0"
)

# Modelos Pydantic
class ConsultaLegal(BaseModel):
    pregunta: str
    contexto_adicional: Optional[str] = None
    max_documentos: Optional[int] = 5

class RespuestaLegal(BaseModel):
    pregunta: str
    respuesta: str
    fundamentos_legales: List[dict]
    timestamp: str
    confianza: Optional[float] = None

# Configuración global
class ConfiguracionAPI:
    def __init__(self):
        # DeepSeek Configuration
        self.deepseek_api_key = "sk-5d5e7a7a4426459da8dcd9c5a5f421e5"
        self.deepseek_base_url = "https://api.deepseek.com"
        
        # Pinecone Configuration
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_name = "legal-documents-mx"
        
        # Embedding model
        self.embedding_model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        
        # Inicializar clientes
        self.deepseek_client = None
        self.pinecone_client = None
        self.embedding_model = None
        self.index = None
        
    def inicializar_clientes(self):
        """Inicializa todos los clientes necesarios"""
        try:
            # Cliente DeepSeek
            self.deepseek_client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url
            )
            logger.info("Cliente DeepSeek inicializado correctamente")
            
            # Cliente Pinecone
            if not self.pinecone_api_key:
                raise ValueError("PINECONE_API_KEY no encontrada en variables de entorno")
                
            self.pinecone_client = Pinecone(api_key=self.pinecone_api_key)
            self.index = self.pinecone_client.Index(self.pinecone_index_name)
            logger.info("Cliente Pinecone inicializado correctamente")
            
            # Modelo de embeddings
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("Modelo de embeddings cargado correctamente")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar clientes: {str(e)}")
            return False

# Instancia global de configuración
config = ConfiguracionAPI()

class ServicioLegal:
    def __init__(self, config: ConfiguracionAPI):
        self.config = config
    
    def generar_embedding(self, texto: str) -> List[float]:
        """Genera embedding para un texto dado"""
        try:
            embedding = self.config.embedding_model.encode(texto)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error al generar embedding: {str(e)}")
            raise HTTPException(status_code=500, detail="Error al procesar la consulta")
    
    def buscar_documentos_relevantes(self, pregunta: str, max_resultados: int = 5) -> List[dict]:
        """Busca documentos relevantes en Pinecone"""
        try:
            # Generar embedding de la pregunta
            embedding_pregunta = self.generar_embedding(pregunta)
            
            # Buscar en Pinecone
            resultados = self.config.index.query(
                vector=embedding_pregunta,
                top_k=max_resultados,
                include_metadata=True
            )
            
            documentos_relevantes = []
            for match in resultados['matches']:
                documento = {
                    'id': match['id'],
                    'score': match['score'],
                    'titulo': match['metadata'].get('titulo', 'Sin título'),
                    'contenido': match['metadata'].get('contenido', ''),
                    'url': match['metadata'].get('url', ''),
                    'tipo': match['metadata'].get('tipo', ''),
                    'fuente': match['metadata'].get('fuente', ''),
                    'fecha_procesamiento': match['metadata'].get('fecha_procesamiento', '')
                }
                documentos_relevantes.append(documento)
            
            logger.info(f"Encontrados {len(documentos_relevantes)} documentos relevantes")
            return documentos_relevantes
            
        except Exception as e:
            logger.error(f"Error al buscar documentos: {str(e)}")
            raise HTTPException(status_code=500, detail="Error al buscar información legal")
    
    def generar_respuesta_legal(self, pregunta: str, documentos: List[dict], contexto_adicional: str = None) -> str:
        """Genera respuesta usando DeepSeek con los documentos encontrados"""
        try:
            # Preparar contexto legal
            contexto_legal = "\n\n".join([
                f"**{doc['titulo']}** (Relevancia: {doc['score']:.3f})\n"
                f"Fuente: {doc['fuente']}\n"
                f"Tipo: {doc['tipo']}\n"
                f"URL: {doc['url']}\n"
                f"Contenido: {doc['contenido'][:1000]}..."
                for doc in documentos
            ])
            
            # Construir prompt para DeepSeek
            prompt_sistema = """
Eres un asistente legal especializado en derecho mexicano. Tu función es proporcionar respuestas precisas y fundamentadas basándose únicamente en la legislación mexicana vigente.

Instrucciones:
1. Responde ÚNICAMENTE basándote en los documentos legales proporcionados
2. Cita específicamente las leyes, artículos y reglamentos relevantes
3. Si no encuentras información suficiente en los documentos, indícalo claramente
4. Proporciona una respuesta estructurada y profesional
5. Incluye referencias específicas a los fundamentos legales
6. Usa un lenguaje claro pero técnicamente preciso
"""
            
            prompt_usuario = f"""
Pregunta legal: {pregunta}

{f"Contexto adicional: {contexto_adicional}" if contexto_adicional else ""}

Documentos legales relevantes:
{contexto_legal}

Por favor, proporciona una respuesta fundamentada basándote en estos documentos legales.
"""
            
            # Llamada a DeepSeek
            response = self.config.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            respuesta = response.choices[0].message.content
            logger.info("Respuesta generada exitosamente con DeepSeek")
            return respuesta
            
        except Exception as e:
            logger.error(f"Error al generar respuesta: {str(e)}")
            raise HTTPException(status_code=500, detail="Error al generar respuesta legal")

# Instancia del servicio
servicio_legal = ServicioLegal(config)

@app.on_event("startup")
async def startup_event():
    """Inicializa los clientes al arrancar la aplicación"""
    logger.info("Iniciando API Legal Mexicana...")
    if not config.inicializar_clientes():
        logger.error("Error crítico: No se pudieron inicializar los clientes")
        raise Exception("Error de inicialización")
    logger.info("API Legal Mexicana iniciada correctamente")

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "mensaje": "API Legal Mexicana",
        "version": "1.0.0",
        "descripcion": "API para consultas legales con fundamentos actualizados",
        "endpoints": {
            "/consulta": "POST - Realizar consulta legal",
            "/salud": "GET - Estado de la API",
            "/estadisticas": "GET - Estadísticas de la base de datos"
        }
    }

@app.get("/salud")
async def verificar_salud():
    """Endpoint para verificar el estado de la API"""
    try:
        # Verificar conexión a Pinecone
        stats = config.index.describe_index_stats()
        
        return {
            "estado": "saludable",
            "timestamp": datetime.now().isoformat(),
            "servicios": {
                "deepseek": "conectado",
                "pinecone": "conectado",
                "embedding_model": "cargado"
            },
            "base_datos": {
                "vectores_totales": stats['total_vector_count'],
                "dimension": stats['dimension']
            }
        }
    except Exception as e:
        logger.error(f"Error en verificación de salud: {str(e)}")
        raise HTTPException(status_code=503, detail="Servicio no disponible")

@app.get("/estadisticas")
async def obtener_estadisticas():
    """Obtiene estadísticas de la base de datos vectorial"""
    try:
        stats = config.index.describe_index_stats()
        return {
            "base_datos": {
                "nombre_indice": config.pinecone_index_name,
                "vectores_totales": stats['total_vector_count'],
                "dimension": stats['dimension'],
                "modelo_embedding": config.embedding_model_name
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")

@app.post("/consulta", response_model=RespuestaLegal)
async def realizar_consulta_legal(consulta: ConsultaLegal):
    """Endpoint principal para realizar consultas legales"""
    try:
        logger.info(f"Nueva consulta recibida: {consulta.pregunta[:100]}...")
        
        # Buscar documentos relevantes
        documentos_relevantes = servicio_legal.buscar_documentos_relevantes(
            consulta.pregunta, 
            consulta.max_documentos
        )
        
        if not documentos_relevantes:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron documentos legales relevantes para su consulta"
            )
        
        # Generar respuesta con DeepSeek
        respuesta = servicio_legal.generar_respuesta_legal(
            consulta.pregunta,
            documentos_relevantes,
            consulta.contexto_adicional
        )
        
        # Preparar fundamentos legales para la respuesta
        fundamentos = [
            {
                "titulo": doc["titulo"],
                "tipo": doc["tipo"],
                "fuente": doc["fuente"],
                "url": doc["url"],
                "relevancia": doc["score"],
                "fecha_procesamiento": doc["fecha_procesamiento"]
            }
            for doc in documentos_relevantes
        ]
        
        # Calcular confianza promedio
        confianza_promedio = sum(doc["score"] for doc in documentos_relevantes) / len(documentos_relevantes)
        
        resultado = RespuestaLegal(
            pregunta=consulta.pregunta,
            respuesta=respuesta,
            fundamentos_legales=fundamentos,
            timestamp=datetime.now().isoformat(),
            confianza=confianza_promedio
        )
        
        logger.info(f"Consulta procesada exitosamente con {len(fundamentos)} fundamentos")
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en consulta: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    uvicorn.run(
        "api_legal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )