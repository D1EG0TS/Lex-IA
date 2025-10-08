# API Legal Mexicana v2.0

## 🚀 Nueva Arquitectura Modular

La API Legal Mexicana ha sido completamente reestructurada con una arquitectura modular que mejora el mantenimiento, escalabilidad y funcionalidades.

## 📁 Estructura del Proyecto

```
src/api/
├── main.py                 # Aplicación principal FastAPI
├── config.py              # Configuración centralizada
├── routes/                # Rutas de la API
│   ├── legal_routes.py    # Endpoints de consultas legales
│   └── admin_routes.py    # Endpoints de administración
├── services/              # Servicios de negocio
│   ├── deepseek_service.py    # Servicio de IA (DeepSeek)
│   └── vector_search_service.py # Servicio de búsqueda vectorial
├── middleware/            # Middleware personalizado
│   └── legal_filter.py    # Filtro de consultas legales
├── models/               # Modelos de datos
│   ├── request_models.py  # Modelos de peticiones
│   └── response_models.py # Modelos de respuestas
└── utils/                # Utilidades
    ├── dependencies.py    # Inyección de dependencias
    └── validators.py      # Validadores
```

## ✨ Nuevas Funcionalidades

### 🔍 Filtrado Automático de Consultas
- **Filtro inteligente**: Solo responde preguntas relacionadas con el ámbito legal mexicano
- **Respuesta automática**: Informa automáticamente cuando una consulta no es legal
- **Alta precisión**: Utiliza patrones avanzados y palabras clave específicas

### 🗣️ Múltiples Tipos de Lenguaje

#### 1. **Técnico Legal** (`tecnico`)
- Terminología jurídica especializada
- Citas específicas de artículos y leyes
- Análisis doctrinal profundo
- Orientado a profesionales del derecho

#### 2. **Coloquial** (`coloquial`)
- Lenguaje sencillo y comprensible
- Explicaciones con ejemplos cotidianos
- Sin tecnicismos innecesarios
- Orientado al ciudadano común

#### 3. **Mixto** (`mixto`)
- Combina precisión técnica con claridad
- Explica términos jurídicos cuando los usa
- Balanceado para múltiples audiencias
- Recomendado para uso general

### 🧠 Prompts Mejorados de IA

Los prompts de DeepSeek han sido completamente rediseñados para:
- **Mayor precisión**: Respuestas más exactas y fundamentadas
- **Mejor estructura**: Formato consistente y organizado
- **Contexto mexicano**: Especialización en legislación nacional
- **Análisis crítico**: Consideración de excepciones y limitaciones

## 🛠️ Configuración

### Variables de Entorno Requeridas

```env
# APIs externas
DEEPSEEK_API_KEY=tu_clave_deepseek_aqui
PINECONE_API_KEY=tu_clave_pinecone_aqui
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=legal-docs-mx

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development
```

### Instalación y Ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
# Editar el archivo .env con tus claves API

# 3. Ejecutar la API
python src/api/main.py
```

## 📚 Endpoints Principales

### Consultas Legales

#### `POST /legal/consulta`
Consulta legal completa con configuración avanzada.

```json
{
  "pregunta": "¿Cuáles son mis derechos laborales en México?",
  "tipo_lenguaje": "mixto",
  "contexto_adicional": "Trabajo en una empresa privada",
  "incluir_fundamentos": true
}
```

#### `POST /legal/consulta-rapida`
Consulta simplificada para uso rápido.

```json
{
  "pregunta": "¿Qué es el amparo?",
  "tipo_lenguaje": "coloquial"
}
```

#### `GET /legal/buscar-documentos`
Búsqueda de documentos legales sin generar respuesta de IA.

#### `GET /legal/buscar-constitucion`
Búsqueda específica en la Constitución Mexicana.

#### `POST /legal/validar-consulta`
Valida si una consulta es del ámbito legal mexicano.

### Administración

#### `GET /admin/salud`
Verifica el estado de salud de la API y sus servicios.

#### `GET /admin/estadisticas`
Obtiene estadísticas de la base de datos vectorial.

#### `GET /admin/info`
Información general de la API.

## 🔧 Características Técnicas

### Arquitectura
- **FastAPI**: Framework web moderno y rápido
- **Pydantic**: Validación de datos robusta
- **Inyección de dependencias**: Gestión limpia de servicios
- **Middleware personalizado**: Filtrado automático de consultas
- **Manejo de errores**: Respuestas consistentes y informativas

### Servicios
- **DeepSeek**: IA especializada en respuestas legales
- **Pinecone**: Base de datos vectorial para búsqueda semántica
- **Sentence Transformers**: Embeddings multilingües

### Validaciones
- **Filtro legal**: Detección automática de consultas no legales
- **Validación de entrada**: Longitud, formato y contenido
- **Validación de respuesta**: Calidad y coherencia de respuestas IA

## 📊 Monitoreo y Logging

- **Logging estructurado**: Con Loguru para mejor trazabilidad
- **Métricas de salud**: Endpoints de monitoreo
- **Estadísticas de uso**: Tracking de consultas y rendimiento

## 🔒 Seguridad

- **CORS configurado**: Control de orígenes permitidos
- **Rate limiting**: Límites de consultas por minuto/hora
- **Validación estricta**: Filtrado de contenido malicioso
- **Manejo seguro de errores**: Sin exposición de información sensible

## 🚦 Estados de Respuesta

### Respuesta Exitosa
```json
{
  "respuesta": "Análisis legal detallado...",
  "tipo_lenguaje_usado": "mixto",
  "fundamentos_legales": [...],
  "confianza": 0.95,
  "advertencias": [...],
  "sugerencias": [...],
  "tiempo_procesamiento": 2.34
}
```

### Consulta No Legal
```json
{
  "error": "consulta_no_legal",
  "mensaje": "Esta consulta no está relacionada con el ámbito legal mexicano",
  "detalles": {
    "razon": "Contiene tema no legal: receta",
    "confianza": 0.9
  }
}
```

## 🔄 Migración desde v1.0

La nueva API mantiene compatibilidad básica, pero se recomienda:

1. **Actualizar endpoints**: Usar las nuevas rutas estructuradas
2. **Configurar filtro legal**: Aprovechar el filtrado automático
3. **Especificar tipo de lenguaje**: Para respuestas optimizadas
4. **Usar nuevos modelos**: Aprovechar la validación mejorada

## 📈 Mejoras de Rendimiento

- **Arquitectura modular**: Mejor organización y mantenimiento
- **Prompts optimizados**: Respuestas más precisas y rápidas
- **Filtrado inteligente**: Reduce procesamiento innecesario
- **Cache integrado**: Respuestas más rápidas para consultas frecuentes
- **Validación temprana**: Detección rápida de errores

## 🤝 Contribución

Para contribuir al proyecto:

1. Seguir la estructura modular establecida
2. Mantener la separación de responsabilidades
3. Agregar tests para nuevas funcionalidades
4. Documentar cambios en este README

## 📞 Soporte

Para soporte técnico o consultas sobre la API:
- Revisar la documentación en `/docs`
- Verificar el estado en `/admin/salud`
- Consultar logs para debugging

---

**API Legal Mexicana v2.0** - Especializada en consultas del ámbito legal mexicano con IA avanzada y arquitectura modular.