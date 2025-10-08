"""Aplicación principal de la API Legal Mexicana.

Esta es la nueva versión estructurada de la API que incluye:
- Filtrado automático de consultas no legales
- Respuestas en diferentes tipos de lenguaje (técnico, coloquial, mixto)
- Arquitectura modular con separación de responsabilidades
- Mejor manejo de errores y logging
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api.routes import legal_routes, admin_routes
from src.api.utils.dependencies import inicializar_servicios, verificar_servicios_inicializados
from src.api.models.response_models import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    # Startup
    logger.info("Iniciando API Legal Mexicana v2.0...")
    
    try:
        # Obtener configuración desde variables de entorno
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
        pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "legal-docs-mx")
        
        if not deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY no encontrada en variables de entorno")
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY no encontrada en variables de entorno")
        
        # Inicializar servicios
        inicializar_servicios(
            deepseek_api_key=deepseek_api_key,
            pinecone_api_key=pinecone_api_key,
            pinecone_environment=pinecone_environment,
            pinecone_index_name=pinecone_index_name
        )
        
        if verificar_servicios_inicializados():
            logger.success("API Legal Mexicana iniciada correctamente")
        else:
            logger.error("Error: No todos los servicios se inicializaron correctamente")
            
    except Exception as e:
        logger.error(f"Error durante el inicio de la aplicación: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Cerrando API Legal Mexicana...")


# Crear aplicación FastAPI
app = FastAPI(
    title="API Legal Mexicana",
    description="""API especializada en consultas del ámbito legal mexicano.
    
    ## Características principales:
    
    * **Filtrado automático**: Solo responde preguntas relacionadas con el ámbito legal mexicano
    * **Múltiples tipos de lenguaje**: Respuestas técnicas, coloquiales o mixtas
    * **Búsqueda vectorial**: Encuentra documentos legales relevantes
    * **IA especializada**: Utiliza DeepSeek para generar respuestas precisas
    * **Constitución Mexicana**: Búsqueda específica en la CPEUM
    
    ## Tipos de lenguaje disponibles:
    
    * `tecnico`: Utiliza terminología jurídica especializada
    * `coloquial`: Lenguaje sencillo para cualquier persona
    * `mixto`: Combina ambos enfoques según el contexto
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(legal_routes.router)
app.include_router(admin_routes.router)


# Manejadores de errores globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Maneja excepciones HTTP de manera consistente."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"http_error_{exc.status_code}",
            mensaje=str(exc.detail) if isinstance(exc.detail, str) else exc.detail.get("mensaje", "Error HTTP"),
            codigo=exc.status_code,
            detalles=exc.detail if not isinstance(exc.detail, str) else None
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de request (422)."""
    logger.error(f"Error de validación en {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "mensaje": "Error de validación en los datos enviados",
            "codigo": 422,
            "detalles": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Maneja excepciones generales no capturadas."""
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="error_interno",
            mensaje="Error interno del servidor",
            codigo=500,
            detalles=str(exc) if app.debug else None
        ).dict()
    )


# Rutas básicas
@app.get("/")
async def root():
    """Endpoint raíz con información básica."""
    return {
        "mensaje": "API Legal Mexicana v2.0",
        "descripcion": "API especializada en consultas del ámbito legal mexicano",
        "version": "2.0.0",
        "documentacion": "/docs",
        "salud": "/admin/salud",
        "endpoints_principales": {
            "consulta_completa": "/legal/consulta",
            "consulta_rapida": "/legal/consulta-rapida",
            "buscar_documentos": "/legal/buscar-documentos",
            "buscar_constitucion": "/legal/buscar-constitucion",
            "validar_consulta": "/legal/validar-consulta"
        },
        "tipos_lenguaje": ["tecnico", "coloquial", "mixto"]
    }


@app.get("/version")
async def version():
    """Información de versión de la API."""
    return {
        "version": "2.0.0",
        "nombre": "API Legal Mexicana",
        "fecha_version": "2024-01-01",
        "cambios_principales": [
            "Arquitectura modular",
            "Filtrado automático de consultas no legales",
            "Múltiples tipos de lenguaje",
            "Mejor manejo de errores",
            "Documentación mejorada"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Ejecutar servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )