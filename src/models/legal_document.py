"""Modelo para documentos legales.

Este módulo define la estructura de datos para documentos legales
extraídos de diversas fuentes oficiales mexicanas.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class DocumentType(str, Enum):
    """Tipos de documentos legales."""
    DECRETO = "decreto"
    ACUERDO = "acuerdo"
    LEY = "ley"
    REGLAMENTO = "reglamento"
    NORMA = "norma"
    CIRCULAR = "circular"
    RESOLUCION = "resolucion"
    AVISO = "aviso"
    CONVOCATORIA = "convocatoria"
    OTRO = "otro"


class DocumentSource(str, Enum):
    """Fuentes de documentos legales."""
    DOF = "dof"
    CONSTITUCION = "constitucion"
    ORDEN_JURIDICO = "orden_juridico"
    OTRO = "otro"


class DocumentStatus(str, Enum):
    """Estados de procesamiento del documento."""
    RAW = "raw"  # Recién extraído
    PROCESSED = "processed"  # Procesado y limpio
    EMBEDDED = "embedded"  # Con embeddings generados
    INDEXED = "indexed"  # Indexado en base de datos vectorial
    ERROR = "error"  # Error en procesamiento


class LegalDocument(BaseModel):
    """Modelo para documentos legales."""
    
    # Identificadores
    id: Optional[str] = Field(None, description="ID único del documento")
    codigo: Optional[str] = Field(None, description="Código oficial del documento")
    
    # Información básica
    title: str = Field(..., description="Título del documento")
    content: str = Field(..., description="Contenido completo del documento")
    summary: Optional[str] = Field(None, description="Resumen del documento")
    
    # Clasificación
    document_type: DocumentType = Field(DocumentType.OTRO, description="Tipo de documento")
    source: DocumentSource = Field(..., description="Fuente del documento")
    
    # Fechas
    publication_date: Optional[datetime] = Field(None, description="Fecha de publicación")
    effective_date: Optional[datetime] = Field(None, description="Fecha de entrada en vigor")
    scraped_at: datetime = Field(default_factory=datetime.now, description="Fecha de extracción")
    
    # URLs y referencias
    url: Optional[str] = Field(None, description="URL original del documento")
    pdf_url: Optional[str] = Field(None, description="URL del PDF si está disponible")
    
    # Metadatos
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")
    tags: List[str] = Field(default_factory=list, description="Etiquetas del documento")
    
    # Información de la entidad emisora
    issuing_entity: Optional[str] = Field(None, description="Entidad que emite el documento")
    department: Optional[str] = Field(None, description="Departamento o secretaría")
    
    # Procesamiento
    status: DocumentStatus = Field(DocumentStatus.RAW, description="Estado de procesamiento")
    processing_notes: Optional[str] = Field(None, description="Notas del procesamiento")
    
    # Contenido estructurado
    sections: List[Dict[str, str]] = Field(default_factory=list, description="Secciones del documento")
    
    # Información de embeddings
    embedding_model: Optional[str] = Field(None, description="Modelo usado para embeddings")
    chunk_count: Optional[int] = Field(None, description="Número de chunks generados")
    
    class Config:
        """Configuración del modelo."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        """Valida que el título no esté vacío."""
        if not v or not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        """Valida que el contenido no esté vacío."""
        if not v or not v.strip():
            raise ValueError('El contenido no puede estar vacío')
        return v.strip()
    
    @validator('url', 'pdf_url')
    def validate_url(cls, v):
        """Valida que las URLs sean válidas."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('La URL debe comenzar con http:// o https://')
        return v
    
    def add_tag(self, tag: str) -> None:
        """Añade una etiqueta al documento.
        
        Args:
            tag: Etiqueta a añadir.
        """
        if tag and tag not in self.tags:
            self.tags.append(tag.lower().strip())
    
    def add_tags(self, tags: List[str]) -> None:
        """Añade múltiples etiquetas al documento.
        
        Args:
            tags: Lista de etiquetas a añadir.
        """
        for tag in tags:
            self.add_tag(tag)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Establece un valor en los metadatos.
        
        Args:
            key: Clave del metadato.
            value: Valor del metadato.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de los metadatos.
        
        Args:
            key: Clave del metadato.
            default: Valor por defecto si no existe.
            
        Returns:
            Valor del metadato o valor por defecto.
        """
        return self.metadata.get(key, default)
    
    def add_section(self, title: str, content: str) -> None:
        """Añade una sección al documento.
        
        Args:
            title: Título de la sección.
            content: Contenido de la sección.
        """
        self.sections.append({
            'title': title.strip(),
            'content': content.strip()
        })
    
    def get_word_count(self) -> int:
        """Obtiene el número de palabras del contenido.
        
        Returns:
            Número de palabras.
        """
        return len(self.content.split())
    
    def get_char_count(self) -> int:
        """Obtiene el número de caracteres del contenido.
        
        Returns:
            Número de caracteres.
        """
        return len(self.content)
    
    def is_processed(self) -> bool:
        """Verifica si el documento ha sido procesado.
        
        Returns:
            True si el documento está procesado o indexado.
        """
        return self.status in [DocumentStatus.PROCESSED, DocumentStatus.EMBEDDED, DocumentStatus.INDEXED]
    
    def mark_as_processed(self) -> None:
        """Marca el documento como procesado."""
        self.status = DocumentStatus.PROCESSED
    
    def mark_as_embedded(self) -> None:
        """Marca el documento como con embeddings generados."""
        self.status = DocumentStatus.EMBEDDED
    
    def mark_as_indexed(self) -> None:
        """Marca el documento como indexado."""
        self.status = DocumentStatus.INDEXED
    
    def mark_as_error(self, error_message: str) -> None:
        """Marca el documento con error.
        
        Args:
            error_message: Mensaje de error.
        """
        self.status = DocumentStatus.ERROR
        self.processing_notes = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el documento a diccionario.
        
        Returns:
            Diccionario con los datos del documento.
        """
        return self.dict()
    
    def __str__(self) -> str:
        """Representación en string del documento."""
        return f"LegalDocument(title='{self.title[:50]}...', source={self.source}, status={self.status})"
    
    def __repr__(self) -> str:
        """Representación detallada del documento."""
        return (f"LegalDocument(id={self.id}, title='{self.title[:30]}...', "
                f"source={self.source}, type={self.document_type}, status={self.status})")