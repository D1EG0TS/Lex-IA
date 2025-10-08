"""Rutas principales para consultas legales."""

import time
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from ..models.request_models import ConsultaLegal
from ..models.response_models import RespuestaLegal, DocumentoLegal
from ..services.deepseek_service import DeepSeekService
from ..services.vector_search_service import VectorSearchService
from ..utils.dependencies import get_deepseek_service, get_vector_service


router = APIRouter(prefix="/legal", tags=["Consultas Legales"])


@router.post("/consulta", response_model=RespuestaLegal)
async def realizar_consulta_legal(
    consulta: ConsultaLegal,
    deepseek_service: DeepSeekService = Depends(get_deepseek_service),
    vector_service: VectorSearchService = Depends(get_vector_service)
):
    """Realiza una consulta legal completa.
    
    Esta función:
    1. Busca documentos relevantes en la base vectorial
    2. Genera una respuesta usando IA con el tipo de lenguaje solicitado
    3. Retorna una respuesta estructurada con fundamentos legales
    
    Nota: DeepSeek evalúa directamente todas las consultas sin filtros previos.
    """
    inicio = time.time()
    
    try:
        # 1. Buscar documentos relevantes
        logger.info(f"Procesando consulta: {consulta.pregunta[:100]}...")
        logger.info("Buscando documentos relevantes...")
        documentos = vector_service.buscar_con_expansion_consulta(
            consulta.pregunta,
            max_documentos=consulta.max_documentos,
            umbral_relevancia=consulta.umbral_relevancia
        )
        
        logger.info(f"Encontrados {len(documentos)} documentos relevantes")
        
        # 2. Generar respuesta con IA
        logger.info(f"Generando respuesta con lenguaje: {consulta.tipo_lenguaje.value}")
        resultado_ia = deepseek_service.generar_respuesta(
            pregunta=consulta.pregunta,
            documentos=documentos,
            tipo_lenguaje=consulta.tipo_lenguaje,
            contexto_adicional=consulta.contexto_adicional
        )
        
        # 3. Construir respuesta final
        tiempo_total = time.time() - inicio
        
        respuesta = RespuestaLegal(
            respuesta=resultado_ia["respuesta"],
            tipo_lenguaje_usado=resultado_ia["tipo_lenguaje_usado"],
            fundamentos_legales=documentos if consulta.incluir_fundamentos else [],
            confianza=resultado_ia["confianza"],
            advertencias=resultado_ia["advertencias"],
            sugerencias=resultado_ia["sugerencias"],
            tiempo_procesamiento=tiempo_total
        )
        
        logger.success(f"Consulta procesada exitosamente en {tiempo_total:.2f}s")
        return respuesta
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        logger.error(f"Error procesando consulta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "error_procesamiento",
                "mensaje": "Error interno al procesar la consulta",
                "detalles": str(e)
            }
        )


@router.post("/consulta-rapida", response_model=RespuestaLegal)
async def consulta_rapida(
    consulta: ConsultaLegal,
    deepseek_service: DeepSeekService = Depends(get_deepseek_service),
    vector_service: VectorSearchService = Depends(get_vector_service)
):
    """Consulta rápida que usa el mismo modelo que la consulta completa."""
    return await realizar_consulta_legal(consulta, deepseek_service, vector_service)


@router.get("/buscar-documentos", response_model=List[DocumentoLegal])
async def buscar_documentos(
    consulta: str,
    max_documentos: int = 5,
    umbral_relevancia: float = 0.7,
    tipo_documento: str = None,
    vector_service: VectorSearchService = Depends(get_vector_service)
):
    """Busca documentos legales sin generar respuesta de IA."""
    try:
        if tipo_documento:
            documentos = vector_service.buscar_por_tipo_documento(
                consulta, tipo_documento, max_documentos, umbral_relevancia
            )
        else:
            documentos = vector_service.buscar_documentos_relevantes(
                consulta, max_documentos, umbral_relevancia
            )
        
        return documentos
        
    except Exception as e:
        logger.error(f"Error buscando documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "error_busqueda",
                "mensaje": "Error al buscar documentos",
                "detalles": str(e)
            }
        )


@router.get("/buscar-constitucion", response_model=List[DocumentoLegal])
async def buscar_en_constitucion(
    consulta: str,
    max_documentos: int = 5,
    umbral_relevancia: float = 0.7,
    vector_service: VectorSearchService = Depends(get_vector_service)
):
    """Busca específicamente en la Constitución Mexicana."""
    try:
        documentos = vector_service.buscar_en_constitucion(
            consulta, max_documentos, umbral_relevancia
        )
        
        return documentos
        
    except Exception as e:
        logger.error(f"Error buscando en constitución: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "error_busqueda_constitucion",
                "mensaje": "Error al buscar en la Constitución",
                "detalles": str(e)
            }
        )


# Endpoint de validación eliminado - DeepSeek evalúa directamente todas las consultas