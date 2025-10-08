"""Validadores y utilidades de validación."""

import re
from typing import List, Tuple, Optional
from loguru import logger


class ValidadorConsultas:
    """Validador para consultas legales."""
    
    # Patrones de consultas válidas
    PATRONES_LEGALES = [
        r'\b(derecho|legal|ley|código|constitución|artículo|jurisprudencia)\b',
        r'\b(demanda|juicio|tribunal|juzgado|amparo|recurso)\b',
        r'\b(contrato|convenio|acuerdo|obligación|responsabilidad)\b',
        r'\b(penal|civil|mercantil|laboral|administrativo|fiscal)\b',
        r'\b(delito|falta|sanción|multa|pena|prisión)\b',
        r'\b(matrimonio|divorcio|patria potestad|alimentos|custodia)\b',
        r'\b(propiedad|posesión|usufructo|servidumbre|hipoteca)\b',
        r'\b(trabajo|empleado|patrón|salario|despido|liquidación)\b',
        r'\b(impuesto|contribución|hacienda|sat|rfc)\b',
        r'\b(notario|registro|escritura|testamento|herencia)\b'
    ]
    
    # Palabras clave mexicanas
    PALABRAS_MEXICANAS = [
        'méxico', 'mexicano', 'mexicana', 'cdmx', 'ciudad de méxico',
        'estado de méxico', 'guadalajara', 'monterrey', 'puebla',
        'sat', 'imss', 'issste', 'infonavit', 'fonacot',
        'scjn', 'suprema corte', 'tribunal federal',
        'cpeum', 'constitución política', 'código civil federal',
        'código penal federal', 'ley federal del trabajo'
    ]
    
    # Temas no legales
    TEMAS_NO_LEGALES = [
        'receta', 'cocina', 'comida', 'restaurante', 'chef',
        'medicina', 'doctor', 'enfermedad', 'síntoma', 'tratamiento',
        'deporte', 'fútbol', 'básquetbol', 'ejercicio', 'gimnasio',
        'tecnología', 'programación', 'software', 'computadora',
        'música', 'canción', 'artista', 'concierto', 'instrumento',
        'viaje', 'turismo', 'hotel', 'vacaciones', 'destino',
        'moda', 'ropa', 'estilo', 'tendencia', 'diseño',
        'clima', 'tiempo', 'temperatura', 'lluvia', 'sol'
    ]
    
    @classmethod
    def es_consulta_legal(cls, texto: str) -> Tuple[bool, str, float]:
        """Determina si una consulta es del ámbito legal.
        
        Args:
            texto: Texto de la consulta
            
        Returns:
            Tuple[bool, str, float]: (es_legal, razón, confianza)
        """
        texto_lower = texto.lower()
        
        # Verificar temas explícitamente no legales
        for tema in cls.TEMAS_NO_LEGALES:
            if tema in texto_lower:
                return False, f"Contiene tema no legal: {tema}", 0.9
        
        # Contar coincidencias legales
        coincidencias_legales = 0
        patrones_encontrados = []
        
        for patron in cls.PATRONES_LEGALES:
            matches = re.findall(patron, texto_lower, re.IGNORECASE)
            if matches:
                coincidencias_legales += len(matches)
                patrones_encontrados.extend(matches)
        
        # Verificar contexto mexicano
        es_mexicano = any(palabra in texto_lower for palabra in cls.PALABRAS_MEXICANAS)
        
        # Calcular confianza
        if coincidencias_legales >= 2:
            confianza = min(0.95, 0.7 + (coincidencias_legales * 0.1))
            if es_mexicano:
                confianza = min(0.98, confianza + 0.1)
            return True, f"Patrones legales encontrados: {', '.join(set(patrones_encontrados))}", confianza
        
        elif coincidencias_legales == 1:
            confianza = 0.6
            if es_mexicano:
                confianza = 0.75
                return True, f"Patrón legal encontrado: {patrones_encontrados[0]} (contexto mexicano)", confianza
            return True, f"Patrón legal encontrado: {patrones_encontrados[0]}", confianza
        
        else:
            if es_mexicano:
                return True, "Contexto mexicano detectado", 0.4
            return False, "No se detectaron patrones legales", 0.1
    
    @classmethod
    def validar_longitud(cls, texto: str, min_chars: int = 10, max_chars: int = 1000) -> Tuple[bool, str]:
        """Valida la longitud del texto.
        
        Args:
            texto: Texto a validar
            min_chars: Mínimo de caracteres
            max_chars: Máximo de caracteres
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje)
        """
        longitud = len(texto.strip())
        
        if longitud < min_chars:
            return False, f"La consulta es muy corta (mínimo {min_chars} caracteres)"
        
        if longitud > max_chars:
            return False, f"La consulta es muy larga (máximo {max_chars} caracteres)"
        
        return True, "Longitud válida"
    
    @classmethod
    def limpiar_texto(cls, texto: str) -> str:
        """Limpia y normaliza el texto de entrada.
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            str: Texto limpio
        """
        # Eliminar espacios extra
        texto = re.sub(r'\s+', ' ', texto.strip())
        
        # Eliminar caracteres especiales problemáticos
        texto = re.sub(r'[^\w\s\.,;:¿?¡!()\-"\']', '', texto)
        
        return texto
    
    @classmethod
    def extraer_palabras_clave(cls, texto: str) -> List[str]:
        """Extrae palabras clave legales del texto.
        
        Args:
            texto: Texto de entrada
            
        Returns:
            List[str]: Lista de palabras clave encontradas
        """
        texto_lower = texto.lower()
        palabras_clave = []
        
        # Buscar patrones legales
        for patron in cls.PATRONES_LEGALES:
            matches = re.findall(patron, texto_lower, re.IGNORECASE)
            palabras_clave.extend(matches)
        
        # Buscar palabras mexicanas
        for palabra in cls.PALABRAS_MEXICANAS:
            if palabra in texto_lower:
                palabras_clave.append(palabra)
        
        return list(set(palabras_clave))


class ValidadorRespuestas:
    """Validador para respuestas generadas por IA."""
    
    @classmethod
    def validar_respuesta_ia(cls, respuesta: str) -> Tuple[bool, List[str]]:
        """Valida que la respuesta de IA sea apropiada.
        
        Args:
            respuesta: Respuesta generada por IA
            
        Returns:
            Tuple[bool, List[str]]: (es_válida, lista_de_problemas)
        """
        problemas = []
        
        # Verificar longitud mínima
        if len(respuesta.strip()) < 50:
            problemas.append("Respuesta muy corta")
        
        # Verificar que no contenga placeholder text
        placeholders = ['[placeholder]', 'TODO', 'FIXME', '{{', '}}']
        for placeholder in placeholders:
            if placeholder in respuesta:
                problemas.append(f"Contiene placeholder: {placeholder}")
        
        # Verificar que no sea solo una disculpa
        disculpas = ['lo siento', 'no puedo', 'no sé', 'disculpe']
        if len(respuesta.strip()) < 100 and any(disculpa in respuesta.lower() for disculpa in disculpas):
            problemas.append("Respuesta parece ser solo una disculpa")
        
        return len(problemas) == 0, problemas
    
    @classmethod
    def calcular_confianza_respuesta(cls, respuesta: str, documentos_usados: int) -> float:
        """Calcula la confianza de una respuesta basada en varios factores.
        
        Args:
            respuesta: Respuesta generada
            documentos_usados: Número de documentos utilizados
            
        Returns:
            float: Nivel de confianza (0.0 - 1.0)
        """
        confianza = 0.5  # Base
        
        # Factor por longitud de respuesta
        longitud = len(respuesta.strip())
        if longitud > 200:
            confianza += 0.1
        if longitud > 500:
            confianza += 0.1
        
        # Factor por documentos utilizados
        if documentos_usados > 0:
            confianza += min(0.3, documentos_usados * 0.1)
        
        # Factor por referencias legales
        referencias_legales = len(re.findall(r'\b(artículo|ley|código|constitución)\b', respuesta.lower()))
        confianza += min(0.2, referencias_legales * 0.05)
        
        return min(1.0, confianza)