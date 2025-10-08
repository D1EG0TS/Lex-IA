"""Middleware para filtrar consultas no relacionadas con el ámbito legal mexicano."""

import re
from typing import List, Tuple
from fastapi import HTTPException
from loguru import logger

from ..utils.validators import ValidadorConsultas


class FiltroLegalMexicano:
    """Filtro para validar que las consultas sean del ámbito legal mexicano."""
    
    def __init__(self):
        # Palabras clave que indican contenido legal
        self.palabras_legales = {
            'derecho', 'ley', 'código', 'artículo', 'constitución', 'reglamento',
            'jurisprudencia', 'tribunal', 'juez', 'sentencia', 'demanda', 'juicio',
            'legal', 'jurídico', 'normativa', 'decreto', 'acuerdo', 'resolución',
            'amparo', 'recurso', 'apelación', 'casación', 'procedimiento',
            'proceso', 'litigio', 'contrato', 'obligación', 'responsabilidad',
            'delito', 'penal', 'civil', 'mercantil', 'laboral', 'fiscal',
            'administrativo', 'constitucional', 'federal', 'local', 'municipal',
            'suprema corte', 'scjn', 'tribunal', 'juzgado', 'ministerio público',
            'procuraduría', 'fiscalía', 'notario', 'abogado', 'licenciado',
            'derechos humanos', 'garantías', 'libertades', 'debido proceso',
            'legalidad', 'legitimidad', 'validez', 'nulidad', 'prescripción',
            'caducidad', 'término', 'plazo', 'notificación', 'emplazamiento',
            'citatorio', 'audiencia', 'alegatos', 'pruebas', 'testigo',
            'perito', 'dictamen', 'laudo', 'ejecutoria', 'cosa juzgada'
        }
        
        # Palabras específicas del contexto mexicano
        self.palabras_mexico = {
            'méxico', 'mexicano', 'mexicana', 'federal', 'estados unidos mexicanos',
            'cpeum', 'constitución política', 'dof', 'diario oficial',
            'orden jurídico nacional', 'suprema corte de justicia',
            'tribunal federal', 'poder judicial', 'senado', 'cámara de diputados',
            'congreso de la unión', 'presidente de la república',
            'secretaría', 'inegi', 'sat', 'imss', 'issste', 'cndh',
            'conapred', 'inai', 'cofepris', 'profeco', 'condusef',
            'cnbv', 'cnsf', 'consar', 'cre', 'ift', 'cofece'
        }
        
        # Temas claramente no legales
        self.temas_no_legales = {
            'receta', 'cocina', 'comida', 'restaurante', 'chef',
            'programación', 'código fuente', 'software', 'hardware',
            'matemáticas', 'física', 'química', 'biología',
            'medicina', 'enfermedad', 'síntoma', 'tratamiento',
            'deporte', 'fútbol', 'básquetbol', 'tenis',
            'música', 'canción', 'artista', 'concierto',
            'película', 'actor', 'director', 'cine',
            'videojuego', 'gaming', 'consola',
            'turismo', 'viaje', 'hotel', 'playa',
            'clima', 'temperatura', 'lluvia', 'sol',
            'amor', 'relación', 'pareja', 'cita',
            'moda', 'ropa', 'zapatos', 'estilo'
        }
        
        # Patrones de preguntas legales comunes
        self.patrones_legales = [
            r'\b(qué|cuál|cómo|cuándo|dónde|por qué).*(dice|establece|señala|dispone).*(ley|código|artículo|constitución|reglamento)\b',
            r'\b(es legal|es ilegal|está permitido|está prohibido|se puede|no se puede)\b',
            r'\b(derechos|obligaciones|responsabilidades|sanciones|multas|penas)\b',
            r'\b(demanda|juicio|tribunal|juzgado|amparo|recurso)\b',
            r'\b(contrato|convenio|acuerdo|documento legal)\b',
            r'\b(constitución|cpeum|carta magna)\b',
            r'\b(código (civil|penal|comercio|trabajo|fiscal))\b',
            r'\b(suprema corte|scjn|poder judicial)\b'
        ]
    
    def es_consulta_legal_mexicana(self, consulta: str) -> Tuple[bool, str, float]:
        """Determina si una consulta es del ámbito legal mexicano.
        
        Returns:
            Tuple[bool, str, float]: (es_legal, razón, confianza)
        """
        return ValidadorConsultas.es_consulta_legal(consulta)
    
    def validar_consulta(self, pregunta: str) -> None:
        """Valida una consulta y lanza excepción si no es legal.
        
        Args:
            pregunta: Pregunta a validar
            
        Raises:
            HTTPException: Si la consulta no es del ámbito legal mexicano
        """
        es_legal, razon, confianza = self.es_consulta_legal_mexicana(pregunta)
        
        if not es_legal:
            logger.warning(f"Consulta rechazada: {pregunta[:100]}... - Razón: {razon}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "consulta_no_legal",
                    "mensaje": "Lo siento, solo puedo responder preguntas relacionadas con el ámbito legal mexicano.",
                    "razon": razon,
                    "sugerencias": [
                        "Reformula tu pregunta incluyendo términos legales específicos",
                        "Menciona leyes, códigos, artículos o instituciones mexicanas",
                        "Especifica el contexto legal de tu consulta"
                    ]
                }
            )
        
        logger.info(f"Consulta legal válida aceptada - Confianza: {confianza:.2f}")


# Instancia global del filtro
filtro_legal = FiltroLegalMexicano()