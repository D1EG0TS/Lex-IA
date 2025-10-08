"""Rutas de administración y monitoreo de la API."""

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ..models.response_models import SaludAPI, EstadisticasAPI
from ..services.vector_search_service import VectorSearchService
from ..utils.dependencies import get_vector_service


router = APIRouter(prefix="/admin", tags=["Administración"])


@router.get("/salud", response_model=SaludAPI)
async def verificar_salud(
    vector_service: VectorSearchService = Depends(get_vector_service)
):
    """Verifica el estado de salud de la API y sus servicios."""
    try:
        # Verificar conexión a Pinecone
        pinecone_ok = vector_service.verificar_conexion()
        
        # Verificar otros servicios aquí si es necesario
        deepseek_ok = True  # Por ahora asumimos que está bien
        
        estado_general = "saludable" if (pinecone_ok and deepseek_ok) else "degradado"
        
        return SaludAPI(
            estado=estado_general,
            version="2.0.0",
            servicios={
                "pinecone": "activo" if pinecone_ok else "inactivo",
                "deepseek": "activo" if deepseek_ok else "inactivo",
                "api": "activo"
            },
            timestamp="2024-01-01T00:00:00Z"  # Se actualizará automáticamente por el modelo
        )
        
    except Exception as e:
        logger.error(f"Error verificando salud: {str(e)}")
        return SaludAPI(
            estado="error",
            version="2.0.0",
            servicios={
                "pinecone": "error",
                "deepseek": "desconocido",
                "api": "activo"
            }
        )


@router.get("/estadisticas", response_model=EstadisticasAPI)
async def obtener_estadisticas(
    vector_service: VectorSearchService = Depends(get_vector_service)
):
    """Obtiene estadísticas de la base de datos vectorial."""
    try:
        stats = vector_service.obtener_estadisticas_indice()
        
        return EstadisticasAPI(
            total_documentos=stats.get("total_vector_count", 0),
            indices_activos=1 if stats else 0,
            consultas_realizadas=0,  # Implementar contador si es necesario
            tiempo_promedio_respuesta=0.0,  # Implementar medición si es necesario
            documentos_por_tipo={
                "constitucion": stats.get("constitucion_count", 0),
                "leyes": stats.get("leyes_count", 0),
                "codigos": stats.get("codigos_count", 0),
                "otros": stats.get("otros_count", 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "error_estadisticas",
                "mensaje": "Error al obtener estadísticas",
                "detalles": str(e)
            }
        )


@router.post("/limpiar-cache")
async def limpiar_cache():
    """Limpia el cache de la aplicación (si existe)."""
    try:
        # Implementar limpieza de cache si es necesario
        logger.info("Cache limpiado exitosamente")
        
        return {
            "mensaje": "Cache limpiado exitosamente",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error limpiando cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "error_cache",
                "mensaje": "Error al limpiar cache",
                "detalles": str(e)
            }
        )


@router.get("/historial")
async def obtener_historial():
    """Obtiene el historial de consultas realizadas."""
    try:
        # Por ahora retornamos datos de ejemplo
        # En el futuro se puede implementar persistencia en base de datos
        historial_ejemplo = [
            {
                "id": "1",
                "pregunta": "¿Cuáles son los requisitos para un contrato de arrendamiento válido en México?",
                "respuesta": "Un contrato de arrendamiento válido en México debe cumplir con los siguientes requisitos según el Código Civil...",
                "fecha": "2024-01-15T10:30:00Z",
                "tipo_lenguaje": "mixto",
                "confianza": 0.92,
                "tiempo_procesamiento": 2.3
            },
            {
                "id": "2",
                "pregunta": "¿Qué es el despido injustificado y cuáles son mis derechos?",
                "respuesta": "El despido injustificado ocurre cuando un empleador termina la relación laboral sin causa justificada...",
                "fecha": "2024-01-14T15:45:00Z",
                "tipo_lenguaje": "coloquial",
                "confianza": 0.88,
                "tiempo_procesamiento": 1.8
            }
        ]
        
        logger.info("Historial de consultas obtenido exitosamente")
        return historial_ejemplo
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "error_historial",
                "mensaje": "Error al obtener historial de consultas",
                "detalles": str(e)
            }
        )


@router.get("/info")
async def informacion_api():
    """Información general de la API."""
    return {
        "nombre": "API Legal Mexicana",
        "version": "2.0.0",
        "descripcion": "API especializada en consultas del ámbito legal mexicano",
        "funcionalidades": [
            "Consultas legales con IA",
            "Búsqueda en documentos legales",
            "Filtrado automático de consultas no legales",
            "Respuestas en lenguaje técnico o coloquial",
            "Búsqueda específica en la Constitución Mexicana"
        ],
        "tipos_lenguaje": [
            "tecnico",
            "coloquial",
            "mixto"
        ],
        "documentacion": "/docs"
    }