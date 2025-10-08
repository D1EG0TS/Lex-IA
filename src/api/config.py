"""Configuración centralizada de la API Legal Mexicana."""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from loguru import logger


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings."""
    
    # Información de la aplicación
    app_name: str = Field(default="API Legal Mexicana", description="Nombre de la aplicación")
    app_version: str = Field(default="2.0.0", description="Versión de la aplicación")
    debug: bool = Field(default=False, description="Modo debug")
    
    # Configuración del servidor
    host: str = Field(default="0.0.0.0", description="Host del servidor")
    port: int = Field(default=8000, description="Puerto del servidor")
    reload: bool = Field(default=True, description="Auto-reload en desarrollo")
    
    # APIs externas
    deepseek_api_key: str = Field(..., description="Clave API de DeepSeek")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        description="URL base de la API de DeepSeek"
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="Modelo de DeepSeek a utilizar"
    )
    
    # Configuración de Pinecone
    pinecone_api_key: str = Field(..., description="Clave API de Pinecone")
    pinecone_environment: str = Field(
        default="gcp-starter",
        description="Entorno de Pinecone"
    )
    pinecone_index_name: str = Field(
        default="legal-docs-mx",
        description="Nombre del índice de Pinecone"
    )
    
    # Configuración de embeddings
    embedding_model_name: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="Modelo de embeddings"
    )
    embedding_dimension: int = Field(
        default=384,
        description="Dimensión de los embeddings"
    )
    
    # Configuración de consultas
    max_query_length: int = Field(
        default=1000,
        description="Longitud máxima de consulta en caracteres"
    )
    min_query_length: int = Field(
        default=10,
        description="Longitud mínima de consulta en caracteres"
    )
    default_max_documents: int = Field(
        default=5,
        description="Número máximo de documentos por defecto"
    )
    default_relevance_threshold: float = Field(
        default=0.7,
        description="Umbral de relevancia por defecto"
    )
    
    # Configuración de respuestas
    max_response_tokens: int = Field(
        default=2000,
        description="Máximo de tokens en respuestas"
    )
    response_temperature: float = Field(
        default=0.3,
        description="Temperatura para generación de respuestas"
    )
    
    # Configuración de logging
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Formato de logging"
    )
    
    # Configuración de CORS
    cors_origins: list = Field(
        default=["*"],
        description="Orígenes permitidos para CORS"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Permitir credenciales en CORS"
    )
    
    # Configuración de rate limiting
    rate_limit_requests_per_minute: int = Field(
        default=60,
        description="Límite de requests por minuto"
    )
    rate_limit_requests_per_hour: int = Field(
        default=1000,
        description="Límite de requests por hora"
    )
    
    # Configuración de cache
    cache_ttl_seconds: int = Field(
        default=3600,
        description="TTL del cache en segundos"
    )
    enable_cache: bool = Field(
        default=True,
        description="Habilitar cache"
    )
    
    # Configuración de filtros
    legal_filter_confidence_threshold: float = Field(
        default=0.5,
        description="Umbral de confianza para filtro legal"
    )
    enable_strict_legal_filter: bool = Field(
        default=True,
        description="Habilitar filtro legal estricto"
    )
    
    # Configuración de monitoreo
    enable_metrics: bool = Field(
        default=True,
        description="Habilitar métricas"
    )
    metrics_endpoint: str = Field(
        default="/metrics",
        description="Endpoint de métricas"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Mapeo de variables de entorno
        fields = {
            "deepseek_api_key": {"env": "DEEPSEEK_API_KEY"},
            "pinecone_api_key": {"env": "PINECONE_API_KEY"},
            "pinecone_environment": {"env": "PINECONE_ENVIRONMENT"},
            "pinecone_index_name": {"env": "PINECONE_INDEX_NAME"},
        }


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación.
    
    Returns:
        Settings: Configuración de la aplicación
    """
    return settings


def validate_settings() -> bool:
    """Valida que todas las configuraciones requeridas estén presentes.
    
    Returns:
        bool: True si la configuración es válida
        
    Raises:
        ValueError: Si falta alguna configuración requerida
    """
    try:
        # Validar APIs requeridas
        if not settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY es requerida")
        
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY es requerida")
        
        # Validar rangos de valores
        if settings.max_query_length <= settings.min_query_length:
            raise ValueError("max_query_length debe ser mayor que min_query_length")
        
        if not (0.0 <= settings.default_relevance_threshold <= 1.0):
            raise ValueError("default_relevance_threshold debe estar entre 0.0 y 1.0")
        
        if not (0.0 <= settings.response_temperature <= 2.0):
            raise ValueError("response_temperature debe estar entre 0.0 y 2.0")
        
        if not (0.0 <= settings.legal_filter_confidence_threshold <= 1.0):
            raise ValueError("legal_filter_confidence_threshold debe estar entre 0.0 y 1.0")
        
        logger.info("Configuración validada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error validando configuración: {str(e)}")
        raise


def log_settings_summary():
    """Registra un resumen de la configuración actual (sin datos sensibles)."""
    logger.info(f"=== Configuración de {settings.app_name} v{settings.app_version} ===")
    logger.info(f"Servidor: {settings.host}:{settings.port}")
    logger.info(f"Debug: {settings.debug}")
    logger.info(f"Modelo DeepSeek: {settings.deepseek_model}")
    logger.info(f"Índice Pinecone: {settings.pinecone_index_name}")
    logger.info(f"Modelo embeddings: {settings.embedding_model_name}")
    logger.info(f"Máx. documentos: {settings.default_max_documents}")
    logger.info(f"Umbral relevancia: {settings.default_relevance_threshold}")
    logger.info(f"Filtro legal estricto: {settings.enable_strict_legal_filter}")
    logger.info(f"Cache habilitado: {settings.enable_cache}")
    logger.info(f"Métricas habilitadas: {settings.enable_metrics}")
    logger.info("=" * 50)


# Configuraciones específicas por entorno
class DevelopmentSettings(Settings):
    """Configuración para desarrollo."""
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    cors_origins: list = ["*"]


class ProductionSettings(Settings):
    """Configuración para producción."""
    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"
    cors_origins: list = []  # Especificar dominios específicos
    rate_limit_requests_per_minute: int = 30
    rate_limit_requests_per_hour: int = 500


class TestingSettings(Settings):
    """Configuración para testing."""
    debug: bool = True
    log_level: str = "DEBUG"
    enable_cache: bool = False
    enable_metrics: bool = False


def get_settings_by_environment(env: str = None) -> Settings:
    """Obtiene configuración específica por entorno.
    
    Args:
        env: Entorno (development, production, testing)
        
    Returns:
        Settings: Configuración específica del entorno
    """
    env = env or os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()