"""Servicio mejorado de búsqueda vectorial con Pinecone."""

import time
from typing import List, Dict, Any, Optional, Tuple
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from loguru import logger

from ..models.response_models import DocumentoLegal


class VectorSearchService:
    """Servicio mejorado para búsqueda vectorial en Pinecone."""
    
    def __init__(self, api_key: str, index_name: str, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embedding_model = SentenceTransformer(embedding_model)
        self.index_name = index_name
        
        logger.info(f"VectorSearchService inicializado con índice: {index_name}")
    
    def buscar_documentos_relevantes(
        self,
        consulta: str,
        max_documentos: int = 5,
        umbral_relevancia: float = 0.7,
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[DocumentoLegal]:
        """Busca documentos relevantes para una consulta.
        
        Args:
            consulta: Texto de la consulta
            max_documentos: Número máximo de documentos a retornar
            umbral_relevancia: Umbral mínimo de relevancia (0-1)
            filtros: Filtros adicionales para la búsqueda
            
        Returns:
            Lista de documentos legales relevantes
        """
        inicio = time.time()
        
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedding_model.encode(consulta).tolist()
            
            # Realizar búsqueda vectorial
            resultados = self.index.query(
                vector=query_embedding,
                top_k=max_documentos * 2,  # Buscar más para filtrar después
                include_metadata=True,
                filter=filtros
            )
            
            # Procesar resultados
            documentos = []
            for match in resultados.matches:
                if match.score >= umbral_relevancia:
                    documento = self._crear_documento_legal(match)
                    if documento:
                        documentos.append(documento)
            
            # Limitar al número máximo solicitado
            documentos = documentos[:max_documentos]
            
            tiempo_busqueda = time.time() - inicio
            logger.info(f"Búsqueda completada - {len(documentos)} documentos encontrados en {tiempo_busqueda:.2f}s")
            
            return documentos
            
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {str(e)}")
            return []
    
    def _crear_documento_legal(self, match) -> Optional[DocumentoLegal]:
        """Crea un objeto DocumentoLegal a partir de un resultado de Pinecone."""
        try:
            metadata = match.metadata or {}
            
            return DocumentoLegal(
                id=match.id,
                titulo=metadata.get('titulo', 'Documento sin título'),
                tipo=metadata.get('tipo', 'Desconocido'),
                fuente=metadata.get('fuente', 'Fuente no especificada'),
                url=metadata.get('url'),
                relevancia=float(match.score),
                fragmento=metadata.get('contenido', metadata.get('texto', 'Contenido no disponible'))[:500],
                articulo=metadata.get('articulo'),
                fecha_publicacion=metadata.get('fecha_publicacion')
            )
        except Exception as e:
            logger.error(f"Error al crear DocumentoLegal: {str(e)}")
            return None
    
    def buscar_con_expansion_consulta(
        self,
        consulta_original: str,
        max_documentos: int = 5,
        umbral_relevancia: float = 0.7
    ) -> List[DocumentoLegal]:
        """Busca documentos expandiendo la consulta con términos relacionados.
        
        Args:
            consulta_original: Consulta original del usuario
            max_documentos: Número máximo de documentos
            umbral_relevancia: Umbral mínimo de relevancia
            
        Returns:
            Lista de documentos legales relevantes
        """
        # Expandir consulta con sinónimos legales
        consulta_expandida = self._expandir_consulta_legal(consulta_original)
        
        # Realizar búsqueda con consulta expandida
        documentos = self.buscar_documentos_relevantes(
            consulta_expandida,
            max_documentos,
            umbral_relevancia
        )
        
        # Si no hay suficientes resultados, intentar con consulta original
        if len(documentos) < max_documentos // 2:
            documentos_adicionales = self.buscar_documentos_relevantes(
                consulta_original,
                max_documentos - len(documentos),
                umbral_relevancia * 0.8  # Umbral más bajo
            )
            
            # Combinar y deduplicar
            ids_existentes = {doc.id for doc in documentos}
            for doc in documentos_adicionales:
                if doc.id not in ids_existentes:
                    documentos.append(doc)
        
        return documentos[:max_documentos]
    
    def _expandir_consulta_legal(self, consulta: str) -> str:
        """Expande una consulta con términos legales relacionados."""
        # Diccionario de expansiones legales
        expansiones = {
            'derecho': 'derecho facultad potestad prerrogativa',
            'obligación': 'obligación deber responsabilidad carga',
            'contrato': 'contrato convenio acuerdo pacto',
            'ley': 'ley norma ordenamiento disposición',
            'juicio': 'juicio proceso procedimiento litigio',
            'demanda': 'demanda acción pretensión solicitud',
            'sentencia': 'sentencia resolución fallo decisión',
            'recurso': 'recurso impugnación apelación casación',
            'amparo': 'amparo protección garantía tutela',
            'constitución': 'constitución carta magna ley fundamental',
            'código': 'código ordenamiento legislación normativa',
            'reglamento': 'reglamento disposición normativa regulación',
            'tribunal': 'tribunal juzgado corte instancia judicial',
            'responsabilidad': 'responsabilidad culpa negligencia imputabilidad',
            'daño': 'daño perjuicio menoscabo lesión',
            'propiedad': 'propiedad dominio titularidad pertenencia',
            'posesión': 'posesión tenencia detentación',
            'herencia': 'herencia sucesión legado patrimonio hereditario',
            'matrimonio': 'matrimonio unión conyugal vínculo matrimonial',
            'divorcio': 'divorcio disolución separación ruptura matrimonial',
            'trabajo': 'trabajo empleo relación laboral prestación servicios',
            'salario': 'salario sueldo remuneración retribución',
            'despido': 'despido terminación rescisión cese laboral',
            'empresa': 'empresa sociedad persona moral entidad',
            'comercio': 'comercio mercantil actividad empresarial negocio',
            'impuesto': 'impuesto tributo contribución gravamen fiscal',
            'delito': 'delito crimen infracción conducta típica',
            'pena': 'pena sanción castigo punición',
            'prisión': 'prisión cárcel reclusión privación libertad',
            'fianza': 'fianza caución garantía'
        }
        
        consulta_lower = consulta.lower()
        consulta_expandida = consulta
        
        for termino, expansion in expansiones.items():
            if termino in consulta_lower:
                consulta_expandida += f" {expansion}"
        
        return consulta_expandida
    
    def obtener_estadisticas_indice(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice de Pinecone."""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectores': stats.total_vector_count,
                'dimension': stats.dimension,
                'indice_lleno': stats.index_fullness,
                'namespaces': dict(stats.namespaces) if stats.namespaces else {}
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas del índice: {str(e)}")
            return {}
    
    def buscar_por_tipo_documento(
        self,
        consulta: str,
        tipo_documento: str,
        max_documentos: int = 5,
        umbral_relevancia: float = 0.7
    ) -> List[DocumentoLegal]:
        """Busca documentos de un tipo específico.
        
        Args:
            consulta: Texto de la consulta
            tipo_documento: Tipo de documento (ley, reglamento, constitución, etc.)
            max_documentos: Número máximo de documentos
            umbral_relevancia: Umbral mínimo de relevancia
            
        Returns:
            Lista de documentos del tipo especificado
        """
        filtros = {'tipo': {'$eq': tipo_documento}}
        
        return self.buscar_documentos_relevantes(
            consulta,
            max_documentos,
            umbral_relevancia,
            filtros
        )
    
    def buscar_en_constitucion(
        self,
        consulta: str,
        max_documentos: int = 5,
        umbral_relevancia: float = 0.7
    ) -> List[DocumentoLegal]:
        """Busca específicamente en la Constitución Mexicana."""
        filtros = {
            '$or': [
                {'tipo': {'$eq': 'Constitución'}},
                {'fuente': {'$eq': 'CPEUM'}},
                {'titulo': {'$regex': '.*Constitución.*'}}
            ]
        }
        
        return self.buscar_documentos_relevantes(
            consulta,
            max_documentos,
            umbral_relevancia,
            filtros
        )
    
    def verificar_conexion(self) -> bool:
        """Verifica la conexión con Pinecone."""
        try:
            self.index.describe_index_stats()
            return True
        except Exception as e:
            logger.error(f"Error de conexión con Pinecone: {str(e)}")
            return False