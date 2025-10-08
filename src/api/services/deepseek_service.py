"""Servicio mejorado de DeepSeek para consultas legales mexicanas."""

import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from loguru import logger

from ..models.request_models import TipoLenguaje
from ..models.response_models import DocumentoLegal


class DeepSeekService:
    """Servicio mejorado para interactuar con DeepSeek."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = "deepseek-chat"
        
        # Prompts base según el tipo de lenguaje
        self.prompts_base = {
            TipoLenguaje.TECNICO: self._get_prompt_tecnico(),
            TipoLenguaje.COLOQUIAL: self._get_prompt_coloquial(),
            TipoLenguaje.MIXTO: self._get_prompt_mixto()
        }
    
    def _get_prompt_tecnico(self) -> str:
        """Prompt para respuestas con lenguaje técnico legal."""
        return """
Eres un jurista experto en derecho mexicano con amplia experiencia en litigio y consultoría legal. Tu especialidad abarca todas las ramas del derecho mexicano: constitucional, civil, penal, mercantil, laboral, administrativo y fiscal.

INSTRUCCIONES ESPECÍFICAS:
1. Utiliza terminología jurídica precisa y técnica apropiada para abogados y profesionales del derecho
2. Cita específicamente artículos, códigos, leyes y jurisprudencias relevantes
3. Estructura tu respuesta con fundamentos legales sólidos y análisis doctrinal
4. Incluye referencias a criterios jurisprudenciales de la SCJN cuando sea pertinente
5. Menciona plazos, procedimientos y requisitos legales específicos
6. Analiza posibles interpretaciones y excepciones legales
7. Proporciona un análisis crítico de la situación jurídica planteada

FORMATO DE RESPUESTA:
- Fundamento legal principal
- Análisis jurídico detallado
- Criterios jurisprudenciales aplicables
- Consideraciones procedimentales
- Conclusiones y recomendaciones técnicas

RECUERDA:
- Siempre fundamenta tus respuestas en la legislación mexicana vigente
- Si hay dudas sobre la interpretación, menciona las diferentes corrientes doctrinales
- Advierte sobre posibles cambios legislativos recientes
- No proporciones asesoría legal específica, solo información general
"""
    
    def _get_prompt_coloquial(self) -> str:
        """Prompt para respuestas en lenguaje coloquial."""
        return """
Eres un asesor legal amigable y accesible que ayuda a ciudadanos mexicanos a entender sus derechos y obligaciones de manera sencilla.

INSTRUCCIONES ESPECÍFICAS:
1. Explica conceptos legales complejos usando analogías y ejemplos de la vida cotidiana
2. Evita jerga jurídica innecesaria; cuando uses términos técnicos, explícalos inmediatamente
3. Usa un tono conversacional, empático y comprensible
4. Proporciona ejemplos prácticos y situaciones reales
5. Estructura la información de manera clara y fácil de seguir
6. Incluye consejos prácticos y pasos concretos que la persona puede seguir
7. Anticipa dudas comunes y proporciona aclaraciones adicionales

FORMATO DE RESPUESTA:
- Explicación simple del tema
- Ejemplos prácticos y cotidianos
- Qué significa esto para ti como ciudadano
- Pasos prácticos a seguir
- Consejos útiles y advertencias importantes

RECUERDA:
- Tu objetivo es empoderar al ciudadano con conocimiento legal accesible
- Si mencionas una ley o artículo, explica qué significa en términos simples
- Usa frases como "En palabras sencillas...", "Esto significa que...", "Por ejemplo..."
- Mantén la precisión legal pero con claridad comunicativa
- No proporciones asesoría legal específica, solo información educativa
"""
    
    def _get_prompt_mixto(self) -> str:
        """Prompt para respuestas con lenguaje mixto (técnico + coloquial)."""
        return """
Eres un consultor legal experto que combina rigor técnico con claridad comunicativa, especializado en hacer accesible el derecho mexicano tanto para profesionales como para ciudadanos.

INSTRUCCIONES ESPECÍFICAS:
1. Inicia con una explicación clara y accesible del tema
2. Proporciona los fundamentos legales técnicos necesarios
3. Explica la terminología jurídica cuando la uses
4. Incluye tanto el análisis técnico como las implicaciones prácticas
5. Balancea precisión legal con comprensibilidad
6. Proporciona ejemplos que ilustren tanto el aspecto técnico como práctico
7. Estructura la respuesta para que sea útil tanto para abogados como para ciudadanos

FORMATO DE RESPUESTA:
- Resumen ejecutivo en lenguaje claro
- Fundamentos legales con explicaciones
- Análisis técnico-jurídico accesible
- Implicaciones prácticas y ejemplos
- Recomendaciones tanto técnicas como prácticas
- Consideraciones adicionales relevantes

ESTILO DE COMUNICACIÓN:
- "Según el artículo X de [ley], esto significa que..."
- "El término jurídico [concepto] se refiere a..."
- "En la práctica, esto implica que..."
- "Por ejemplo, si una persona..."

RECUERDA:
- Tu meta es ser preciso legalmente pero comprensible humanamente
- Fundamenta siempre en legislación mexicana vigente
- Explica tanto el "qué" como el "por qué" de las normas
- No proporciones asesoría legal específica, solo información educativa
"""
    
    def _construir_contexto_documentos(self, documentos: List[DocumentoLegal]) -> str:
        """Construye el contexto basado en documentos relevantes."""
        if not documentos:
            return """No se encontraron documentos específicos en la base de datos para esta consulta.
            
INSTRUCCIONES ESPECIALES PARA RESPUESTA SIN DOCUMENTOS:
- Utiliza tu conocimiento general del derecho mexicano para proporcionar una respuesta útil
- Basa tu respuesta en la legislación mexicana vigente que conozcas
- Menciona las leyes, códigos o reglamentos relevantes que apliquen al tema
- Incluye referencias a la Constitución Política de los Estados Unidos Mexicanos cuando sea pertinente
- Proporciona información general pero precisa sobre el tema legal consultado
- Advierte claramente que la respuesta se basa en conocimiento general y no en documentos específicos
- Recomienda verificar la información con fuentes oficiales actualizadas"""
        
        contexto = "DOCUMENTOS LEGALES RELEVANTES:\n\n"
        
        for i, doc in enumerate(documentos[:5], 1):
            contexto += f"{i}. {doc.titulo}\n"
            contexto += f"   Tipo: {doc.tipo}\n"
            contexto += f"   Fuente: {doc.fuente}\n"
            if doc.articulo:
                contexto += f"   Artículo: {doc.articulo}\n"
            contexto += f"   Contenido relevante: {doc.fragmento}\n"
            if doc.url:
                contexto += f"   URL: {doc.url}\n"
            contexto += "\n"
        
        return contexto
    
    def _get_instrucciones_adicionales(self, tipo_lenguaje: TipoLenguaje) -> str:
        """Obtiene instrucciones adicionales según el tipo de lenguaje."""
        instrucciones = {
            TipoLenguaje.TECNICO: """
INSTRUCCIONES ADICIONALES PARA RESPUESTA TÉCNICA:
- Emplea la terminología jurídica exacta y precisa
- Cita numerales, fracciones y párrafos específicos
- Menciona principios doctrinales y jurisprudenciales
- Usa construcciones formales del lenguaje jurídico
- Incluye referencias cruzadas entre ordenamientos cuando sea relevante
""",
            TipoLenguaje.COLOQUIAL: """
INSTRUCCIONES ADICIONALES PARA RESPUESTA COLOQUIAL:
- Traduce todos los términos legales a lenguaje cotidiano
- Usa analogías familiares y ejemplos de la vida diaria
- Evita latinismos y tecnicismos sin explicación
- Emplea un tono conversacional y amigable
- Organiza la información como si fuera una conversación educativa
""",
            TipoLenguaje.MIXTO: """
INSTRUCCIONES ADICIONALES PARA RESPUESTA MIXTA:
- Presenta primero el marco técnico, luego la explicación simple
- Usa formato: "Técnicamente [concepto legal], lo que significa [explicación simple]"
- Balancea rigor jurídico con accesibilidad comunicativa
- Incluye tanto citas precisas como interpretaciones comprensibles
- Estructura: fundamento técnico → explicación práctica → ejemplo
"""
        }
        return instrucciones.get(tipo_lenguaje, "")
    
    def generar_respuesta(
        self,
        pregunta: str,
        documentos: List[DocumentoLegal],
        tipo_lenguaje: TipoLenguaje = TipoLenguaje.MIXTO,
        contexto_adicional: Optional[str] = None
    ) -> Dict[str, Any]:
        """Genera una respuesta usando DeepSeek con el prompt mejorado.
        
        Args:
            pregunta: Pregunta del usuario
            documentos: Documentos legales relevantes
            tipo_lenguaje: Tipo de lenguaje para la respuesta
            contexto_adicional: Contexto adicional opcional
            
        Returns:
            Dict con la respuesta y metadatos
        """
        inicio = time.time()
        
        try:
            # Construir el prompt completo mejorado
            prompt_base = self.prompts_base[tipo_lenguaje]
            contexto_docs = self._construir_contexto_documentos(documentos)
            instrucciones_adicionales = self._get_instrucciones_adicionales(tipo_lenguaje)
            
            # Construir contexto completo mejorado
            contexto_completo = f"""{prompt_base}

{instrucciones_adicionales}

CONTEXTO NORMATIVO MEXICANO:
{contexto_docs}

CONSULTA LEGAL:
"{pregunta}"

CONTEXTO ADICIONAL:
{contexto_adicional or 'Ninguno proporcionado.'}

INSTRUCCIONES ADICIONALES:
- Basa tu respuesta exclusivamente en el derecho mexicano vigente
- Si no hay documentos específicos disponibles, utiliza tu conocimiento general del derecho mexicano
- Cuando uses conocimiento general, menciona claramente que no se encontraron documentos específicos
- Proporciona una respuesta estructurada y completa basada en la legislación mexicana
- Incluye advertencias sobre limitaciones o excepciones importantes
- Si aplica, menciona si se requiere asesoría legal personalizada
- Mantén el tipo de lenguaje solicitado: {tipo_lenguaje.value}
- Siempre recomienda verificar la información con fuentes oficiales cuando no hay documentos específicos

RESPUESTA:"""
            
            # Llamada a DeepSeek
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en derecho mexicano que proporciona información legal precisa y bien fundamentada."
                    },
                    {
                        "role": "user",
                        "content": contexto_completo
                    }
                ],
                temperature=0.3,  # Respuestas más consistentes para temas legales
                max_tokens=2000,
                top_p=0.9
            )
            
            respuesta_texto = response.choices[0].message.content
            tiempo_procesamiento = time.time() - inicio
            
            # Calcular confianza basada en la calidad de la respuesta
            confianza = self._calcular_confianza(respuesta_texto, documentos)
            
            # Generar advertencias y sugerencias
            advertencias = self._generar_advertencias(respuesta_texto, documentos)
            sugerencias = self._generar_sugerencias(pregunta, tipo_lenguaje)
            
            logger.info(f"Respuesta generada exitosamente - Tiempo: {tiempo_procesamiento:.2f}s - Confianza: {confianza:.2f}")
            
            return {
                "respuesta": respuesta_texto,
                "confianza": confianza,
                "advertencias": advertencias,
                "sugerencias": sugerencias,
                "tiempo_procesamiento": tiempo_procesamiento,
                "tipo_lenguaje_usado": tipo_lenguaje,
                "documentos_utilizados": len(documentos)
            }
            
        except Exception as e:
            logger.error(f"Error al generar respuesta con DeepSeek: {str(e)}")
            raise Exception(f"Error en el servicio de IA: {str(e)}")
    
    def _calcular_confianza(self, respuesta: str, documentos: List[DocumentoLegal]) -> float:
        """Calcula el nivel de confianza de la respuesta."""
        if documentos:
            # Con documentos específicos: confianza alta
            confianza_base = 0.7
            confianza_base += min(len(documentos) * 0.1, 0.3)
        else:
            # Sin documentos específicos: confianza moderada basada en conocimiento general
            confianza_base = 0.6
        
        # Aumentar confianza por longitud y estructura de respuesta
        if len(respuesta) > 200:
            confianza_base += 0.1
        
        # Verificar menciones de leyes específicas
        menciones_legales = ['artículo', 'código', 'ley', 'constitución', 'reglamento']
        menciones_encontradas = sum(1 for mencion in menciones_legales if mencion.lower() in respuesta.lower())
        confianza_base += min(menciones_encontradas * 0.05, 0.15)
        
        return min(confianza_base, 1.0)
    
    def _generar_advertencias(self, respuesta: str, documentos: List[DocumentoLegal]) -> List[str]:
        """Genera advertencias apropiadas para la respuesta."""
        advertencias = [
            "Esta información es de carácter general y educativo",
            "Para casos específicos, consulte a un abogado especializado",
            "La legislación puede cambiar, verifique la vigencia de las normas"
        ]
        
        if not documentos:
            advertencias.extend([
                "Respuesta basada en conocimiento general del derecho mexicano",
                "No se encontraron documentos específicos en la base de datos",
                "Verifique la información con fuentes oficiales actualizadas",
                "Consulte los códigos y leyes vigentes para confirmación"
            ])
        
        if len(respuesta) < 100:
            advertencias.append("Respuesta breve, considere reformular la pregunta para más detalles")
        
        return advertencias
    
    def _generar_sugerencias(self, pregunta: str, tipo_lenguaje: TipoLenguaje) -> List[str]:
        """Genera sugerencias útiles para el usuario."""
        sugerencias = []
        
        if tipo_lenguaje == TipoLenguaje.TECNICO:
            sugerencias.append("Consulte la jurisprudencia actualizada para interpretaciones específicas")
        elif tipo_lenguaje == TipoLenguaje.COLOQUIAL:
            sugerencias.append("Si necesita más detalles técnicos, puede solicitar una explicación más especializada")
        
        sugerencias.extend([
            "Verifique siempre las fuentes primarias (leyes, códigos, reglamentos)",
            "Considere consultar con un profesional del derecho para aplicaciones específicas",
            "Manténgase actualizado sobre reformas y cambios legislativos"
        ])
        
        return sugerencias