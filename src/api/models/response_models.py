"""Modelos de respuesta para la API Legal Mexicana."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .request_models import TipoLenguaje


class DocumentoLegal(BaseModel):
    """Información de un documento legal encontrado."""
    id: str = Field(..., description="ID único del documento")
    titulo: str = Field(..., description="Título del documento")
    tipo: str = Field(..., description="Tipo de documento (ley, reglamento, etc.)")
    fuente: str = Field(..., description="Fuente del documento")
    url: Optional[str] = Field(None, description="URL del documento")
    relevancia: float = Field(..., description="Score de relevancia (0-1)")
    fragmento: str = Field(..., description="Fragmento relevante del documento")
    articulo: Optional[str] = Field(None, description="Artículo específico si aplica")
    fecha_publicacion: Optional[str] = Field(None, description="Fecha de publicación")


class RespuestaLegal(BaseModel):
    """Respuesta completa a una consulta legal."""
    respuesta: str = Field(..., description="Respuesta generada por IA")
    tipo_lenguaje_usado: TipoLenguaje = Field(..., description="Tipo de lenguaje utilizado")
    fundamentos_legales: List[DocumentoLegal] = Field(
        default_factory=list,
        description="Documentos legales que fundamentan la respuesta"
    )
    confianza: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Nivel de confianza en la respuesta (0-1)"
    )
    advertencias: List[str] = Field(
        default_factory=list,
        description="Advertencias o limitaciones de la respuesta"
    )
    sugerencias: List[str] = Field(
        default_factory=list,
        description="Sugerencias adicionales para el usuario"
    )
    tiempo_procesamiento: float = Field(..., description="Tiempo de procesamiento en segundos")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")


class EstadisticasAPI(BaseModel):
    """Estadísticas de la API."""
    total_documentos: int = Field(..., description="Total de documentos en la base vectorial")
    indices_activos: int = Field(..., description="Número de índices activos")
    consultas_realizadas: int = Field(..., description="Total de consultas realizadas")
    tiempo_promedio_respuesta: float = Field(..., description="Tiempo promedio de respuesta en segundos")
    documentos_por_tipo: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribución de documentos por tipo"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de las estadísticas")


class SaludAPI(BaseModel):
    """Estado de salud de la API."""
    estado: str = Field(..., description="Estado general de la API")
    version: str = Field(..., description="Versión de la API")
    timestamp: datetime = Field(default_factory=datetime.now)
    servicios: Dict[str, str] = Field(
        default_factory=dict,
        description="Estado de servicios externos (DeepSeek, Pinecone, etc.)"
    )
    base_datos: Dict[str, Any] = Field(
        default_factory=dict,
        description="Información de la base de datos vectorial"
    )
    estadisticas: Optional[EstadisticasAPI] = Field(
        None,
        description="Estadísticas de uso"
    )


class ErrorResponse(BaseModel):
    """Respuesta de error estándar."""
    error: str = Field(..., description="Tipo de error")
    mensaje: str = Field(..., description="Mensaje descriptivo del error")
    codigo: int = Field(..., description="Código de error HTTP")
    timestamp: datetime = Field(default_factory=datetime.now)
    detalles: Optional[Dict[str, Any]] = Field(
        None,
        description="Detalles adicionales del error"
    )