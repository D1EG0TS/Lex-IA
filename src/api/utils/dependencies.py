"""Dependencias para la inyección de dependencias de FastAPI."""

from functools import lru_cache
from typing import Optional
from loguru import logger

from ..services.deepseek_service import DeepSeekService
from ..services.vector_search_service import VectorSearchService


# Instancias globales de servicios (singleton pattern)
_deepseek_service: Optional[DeepSeekService] = None
_vector_service: Optional[VectorSearchService] = None


def inicializar_servicios(
    deepseek_api_key: str,
    pinecone_api_key: str,
    pinecone_environment: str,
    pinecone_index_name: str,
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
):
    """Inicializa los servicios globales de la aplicación.
    
    Esta función debe ser llamada al inicio de la aplicación para
    configurar las instancias de los servicios que serán utilizadas
    por toda la API.
    
    Args:
        deepseek_api_key: Clave API de DeepSeek
        pinecone_api_key: Clave API de Pinecone
        pinecone_environment: Entorno de Pinecone
        pinecone_index_name: Nombre del índice de Pinecone
        embedding_model_name: Nombre del modelo de embeddings
    """
    global _deepseek_service, _vector_service
    
    try:
        logger.info("Inicializando servicios de la aplicación...")
        
        # Inicializar servicio de DeepSeek
        logger.info("Inicializando servicio DeepSeek...")
        _deepseek_service = DeepSeekService(deepseek_api_key)
        
        # Inicializar servicio de búsqueda vectorial
        logger.info("Inicializando servicio de búsqueda vectorial...")
        _vector_service = VectorSearchService(
            api_key=pinecone_api_key,
            index_name=pinecone_index_name,
            embedding_model=embedding_model_name
        )
        
        logger.success("Servicios inicializados correctamente")
        
    except Exception as e:
        logger.error(f"Error inicializando servicios: {str(e)}")
        raise


def get_deepseek_service() -> DeepSeekService:
    """Obtiene la instancia del servicio DeepSeek.
    
    Esta función es utilizada como dependencia de FastAPI para
    inyectar el servicio DeepSeek en los endpoints.
    
    Returns:
        DeepSeekService: Instancia del servicio DeepSeek
        
    Raises:
        RuntimeError: Si el servicio no ha sido inicializado
    """
    if _deepseek_service is None:
        logger.error("Servicio DeepSeek no inicializado")
        raise RuntimeError(
            "Servicio DeepSeek no inicializado. "
            "Llama a inicializar_servicios() primero."
        )
    
    return _deepseek_service


def get_vector_service() -> VectorSearchService:
    """Obtiene la instancia del servicio de búsqueda vectorial.
    
    Esta función es utilizada como dependencia de FastAPI para
    inyectar el servicio de búsqueda vectorial en los endpoints.
    
    Returns:
        VectorSearchService: Instancia del servicio de búsqueda vectorial
        
    Raises:
        RuntimeError: Si el servicio no ha sido inicializado
    """
    if _vector_service is None:
        logger.error("Servicio de búsqueda vectorial no inicializado")
        raise RuntimeError(
            "Servicio de búsqueda vectorial no inicializado. "
            "Llama a inicializar_servicios() primero."
        )
    
    return _vector_service


@lru_cache(maxsize=1)
def get_app_config():
    """Obtiene la configuración de la aplicación (cached).
    
    Esta función utiliza cache para evitar recargar la configuración
    en cada llamada.
    
    Returns:
        dict: Configuración de la aplicación
    """
    return {
        "app_name": "API Legal Mexicana",
        "version": "2.0.0",
        "debug": False,
        "max_query_length": 1000,
        "default_language": "mixto",
        "cache_ttl": 3600,  # 1 hora
        "rate_limit": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000
        }
    }


def verificar_servicios_inicializados() -> bool:
    """Verifica si todos los servicios han sido inicializados.
    
    Returns:
        bool: True si todos los servicios están inicializados
    """
    return _deepseek_service is not None and _vector_service is not None


def obtener_estado_servicios() -> dict:
    """Obtiene el estado actual de los servicios.
    
    Returns:
        dict: Estado de cada servicio
    """
    return {
        "deepseek_service": _deepseek_service is not None,
        "vector_service": _vector_service is not None,
        "todos_inicializados": verificar_servicios_inicializados()
    }