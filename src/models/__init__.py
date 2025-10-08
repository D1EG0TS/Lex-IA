"""Módulo de modelos de datos para el asistente legal.

Contiene:
- Modelos de documentos legales
- Esquemas de base de datos
- Validadores de datos
- Tipos personalizados
"""

from .legal_document import LegalDocument, DocumentType, DocumentSource, DocumentStatus

# TODO: Implementar modelos adicionales
# from .query_models import Query, QueryResult
# from .embedding_models import DocumentEmbedding

__all__ = [
    "LegalDocument",
    "DocumentType",
    "DocumentSource",
    "DocumentStatus"
]