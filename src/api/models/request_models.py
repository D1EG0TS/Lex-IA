"""Modelos de solicitud para la API Legal Mexicana."""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from enum import Enum


class TipoLenguaje(str, Enum):
    """Tipos de lenguaje para las respuestas."""
    TECNICO = "tecnico"
    COLOQUIAL = "coloquial"
    MIXTO = "mixto"


class ConsultaLegal(BaseModel):
    """Modelo para consultas legales."""
    pregunta: str = Field(
        ..., 
        min_length=3, 
        max_length=1000,
        description="Pregunta legal a consultar"
    )
    contexto_adicional: Optional[str] = Field(
        None, 
        max_length=500,
        description="Contexto adicional para la consulta"
    )
    tipo_lenguaje: TipoLenguaje = Field(
        default=TipoLenguaje.MIXTO,
        description="Tipo de lenguaje para la respuesta: técnico, coloquial o mixto"
    )
    incluir_fundamentos: bool = Field(
        default=True,
        description="Si incluir fundamentos legales en la respuesta"
    )
    max_documentos: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Número máximo de documentos a considerar"
    )
    umbral_relevancia: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Umbral mínimo de relevancia para documentos"
    )
    incluir_metadatos: bool = Field(
        default=True,
        description="Si incluir metadatos de los documentos encontrados"
    )
    
    @validator('pregunta')
    def validar_pregunta(cls, v):
        """Valida que la pregunta no esté vacía."""
        if not v.strip():
            raise ValueError('La pregunta no puede estar vacía')
        return v.strip()


class ValidacionConsulta(BaseModel):
    """Modelo para validar consultas legales."""
    pregunta: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Pregunta a validar"
    )
    
    @validator('pregunta')
    def validar_pregunta(cls, v):
        """Valida que la pregunta no esté vacía."""
        if not v.strip():
            raise ValueError('La pregunta no puede estar vacía')
        return v.strip()