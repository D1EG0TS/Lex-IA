# Base de Datos Vectorial para Documentos Legales Mexicanos

## 📋 Descripción General

Este sistema implementa una base de datos vectorial completa para documentos legales mexicanos utilizando **Pinecone** como motor de búsqueda vectorial y modelos de embeddings de última generación. Permite realizar búsquedas semánticas inteligentes sobre la Constitución Política, leyes federales, reglamentos y publicaciones del Diario Oficial de la Federación (DOF).

### 🎯 Características Principales

- **Búsqueda Semántica Avanzada**: Encuentra documentos por significado, no solo por palabras clave
- **Filtrado Inteligente**: Filtra por categoría, tipo de documento, fecha, etc.
- **Múltiples Modelos de Embeddings**: Soporte para modelos gratuitos y de pago
- **Optimizado para Tier Gratuito**: Gestión eficiente del límite de 2GB de Pinecone
- **Priorización Automática**: CPEUM > Leyes Federales > Reglamentos > DOF
- **Instalación Automatizada**: Scripts de configuración completos

## 🏗️ Arquitectura del Sistema

```
📁 Sistema de Base de Datos Vectorial
├── 🔧 Configuración e Instalación
│   ├── install_vectordb.py          # Instalador automatizado
│   ├── config_vectordb.env.example  # Plantilla de configuración
│   └── requirements_vectordb.txt    # Dependencias
├── 🗄️ Componentes Principales
│   ├── setup_pinecone_vectordb.py   # Configuración de Pinecone
│   ├── semantic_search.py           # Motor de búsqueda semántica
│   └── demo_vectordb.py             # Demostraciones y ejemplos
├── 📊 Datos y Almacenamiento
│   └── data/raw/                    # Documentos extraídos
│       ├── cpeum/                   # Constitución
│       ├── leyes_federales/         # Leyes federales
│       ├── reglamentos_federales/   # Reglamentos
│       └── dof/                     # Publicaciones DOF
└── 📝 Documentación
    ├── README_VectorDB.md           # Este archivo
    └── README_OrdenJuridico.md     # Documentación del scraper
```

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)

```bash
# Instalación completa con configuración interactiva
python install_vectordb.py --full-setup
```

### Opción 2: Instalación Manual

```bash
# 1. Verificar Python
python install_vectordb.py --check-python

# 2. Instalar dependencias
python install_vectordb.py --install-deps

# 3. Configurar variables de entorno
python install_vectordb.py --setup-env

# 4. Probar conexión
python install_vectordb.py --test-connection
```

## ⚙️ Configuración

### 1. Obtener API Keys

#### Pinecone (Gratuito)
1. Regístrate en [Pinecone](https://app.pinecone.io/)
2. Crea un nuevo proyecto
3. Copia tu API Key desde el dashboard
4. Anota tu Environment (ej: `gcp-starter`)

#### OpenAI (Opcional - Solo para modelo Ada-002)
1. Regístrate en [OpenAI Platform](https://platform.openai.com/)
2. Ve a [API Keys](https://platform.openai.com/api-keys)
3. Crea una nueva API Key
4. Añade créditos a tu cuenta

### 2. Configurar Variables de Entorno

El instalador creará automáticamente `config_vectordb.env`:

```env
# Configuración de Pinecone
PINECONE_API_KEY=tu_api_key_aqui
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=legal-documents-mx

# Modelo de Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# OpenAI (opcional)
OPENAI_API_KEY=tu_openai_key_aqui

# Configuración de datos
DATA_DIRECTORY=data/raw
MAX_TEXT_LENGTH=8000
BATCH_SIZE=100

# Límites de almacenamiento (MB)
CPEUM_STORAGE_LIMIT=50
LEYES_STORAGE_LIMIT=800
REGLAMENTOS_STORAGE_LIMIT=600
DOF_STORAGE_LIMIT=550
```

## 🧠 Modelos de Embeddings Disponibles

### Modelos Gratuitos (Recomendados)

| Modelo | Dimensión | Tamaño | Rendimiento | Uso Recomendado |
|--------|-----------|--------|-------------|------------------|
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | 80MB | ⭐⭐⭐ | Rápido, eficiente |
| `sentence-transformers/all-mpnet-base-v2` | 768 | 420MB | ⭐⭐⭐⭐ | Mejor calidad |
| `intfloat/e5-base-v2` | 768 | 420MB | ⭐⭐⭐⭐⭐ | Excelente rendimiento |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 384 | 420MB | ⭐⭐⭐⭐ | Multiidioma |

### Modelos de Pago

| Modelo | Dimensión | Costo | Rendimiento | Notas |
|--------|-----------|-------|-------------|-------|
| `openai-ada-002` | 1536 | $0.0001/1K tokens | ⭐⭐⭐⭐⭐ | Mejor calidad, requiere OpenAI API |

## 📊 Uso del Sistema

### 1. Crear Índice en Pinecone

```bash
# Crear índice con configuración automática
python setup_pinecone_vectordb.py --create-index

# Crear índice con configuración personalizada
python setup_pinecone_vectordb.py --create-index --dimension 768 --metric cosine
```

### 2. Cargar Documentos

```bash
# Cargar todos los documentos disponibles
python setup_pinecone_vectordb.py --load-documents

# Cargar solo categorías específicas
python setup_pinecone_vectordb.py --load-documents --categories cpeum,leyes_federales

# Cargar con límite personalizado
python setup_pinecone_vectordb.py --load-documents --max-docs 1000
```

### 3. Realizar Búsquedas

#### Búsqueda Básica
```bash
# Búsqueda simple
python semantic_search.py "derechos humanos constitución"

# Búsqueda con más resultados
python semantic_search.py "impuestos federales" --top-k 10
```

#### Búsqueda con Filtros
```bash
# Solo en la Constitución
python semantic_search.py "libertad de expresión" --category cpeum

# Solo en leyes federales
python semantic_search.py "procedimiento penal" --category leyes_federales

# Con score mínimo
python semantic_search.py "educación pública" --min-score 0.8
```

#### Búsqueda Programática
```python
from semantic_search import SemanticSearchEngine

# Inicializar motor de búsqueda
search_engine = SemanticSearchEngine(
    pinecone_api_key="tu_api_key",
    index_name="legal-documents-mx",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)

# Realizar búsqueda
results = search_engine.search(
    query="derechos laborales trabajadores",
    top_k=5,
    filters={"category": "leyes_federales"},
    min_score=0.7
)

# Procesar resultados
for result in results:
    print(f"Título: {result['metadata']['title']}")
    print(f"Relevancia: {result['score']:.3f}")
    print(f"Contenido: {result['content'][:200]}...")
    print("-" * 50)
```

### 4. Gestión del Índice

```bash
# Ver estadísticas del índice
python setup_pinecone_vectordb.py --stats

# Limpiar índice
python setup_pinecone_vectordb.py --clear-index

# Eliminar índice
python setup_pinecone_vectordb.py --delete-index
```

## 🎮 Demostraciones

### Demostración Básica
```bash
# Verificar configuración y conexión
python demo_vectordb.py --demo-basic
```

### Demostración de Búsquedas
```bash
# Ejemplos de búsquedas semánticas
python demo_vectordb.py --demo-search
```

### Demostración de Filtros
```bash
# Ejemplos de filtrado por categorías
python demo_vectordb.py --demo-filters
```

### Demostración Completa
```bash
# Flujo completo de trabajo
python demo_vectordb.py --demo-complete
```

## 📈 Optimización y Límites

### Tier Gratuito de Pinecone
- **Almacenamiento**: 2GB máximo
- **Operaciones de escritura**: 2M/mes
- **Operaciones de lectura**: 1M/mes
- **Índices**: 1 índice activo

### Estimación de Capacidad

| Categoría | Documentos Estimados | Almacenamiento (MB) | Prioridad |
|-----------|---------------------|---------------------|----------|
| CPEUM | 1 | 50 | 🔴 Alta |
| Leyes Federales | 302 | 800 | 🟡 Media-Alta |
| Reglamentos | 135 | 600 | 🟡 Media |
| DOF | Variable | 550 | 🟢 Baja |
| **Total** | **~438+** | **~2000** | |

### Consejos de Optimización

1. **Priorización**: Carga primero CPEUM y leyes más importantes
2. **Fragmentación**: Divide documentos largos en secciones
3. **Metadatos**: Usa metadatos eficientes para filtrado
4. **Limpieza**: Elimina documentos obsoletos regularmente
5. **Monitoreo**: Revisa el uso de almacenamiento frecuentemente

## 🔍 Casos de Uso Prácticos

### 1. Investigación Jurídica
```python
# Buscar precedentes constitucionales
results = search_engine.search(
    "debido proceso legal garantías",
    filters={"category": "cpeum"},
    top_k=5
)
```

### 2. Consulta Fiscal
```python
# Encontrar regulaciones fiscales específicas
results = search_engine.search(
    "impuesto sobre la renta deducciones",
    filters={"category": "leyes_federales"},
    min_score=0.8
)
```

### 3. Análisis Comparativo
```python
# Comparar regulaciones entre categorías
query = "procedimiento administrativo recurso"

# Buscar en leyes
leyes = search_engine.search(query, filters={"category": "leyes_federales"})

# Buscar en reglamentos
reglamentos = search_engine.search(query, filters={"category": "reglamentos_federales"})
```

### 4. Búsqueda Temporal
```python
# Encontrar regulaciones recientes
results = search_engine.search(
    "reforma constitucional",
    filters={"year": {"$gte": 2020}},
    top_k=10
)
```

## 🛠️ Solución de Problemas

### Errores Comunes

#### Error de Conexión a Pinecone
```
PineconeException: Invalid API key
```
**Solución**: Verifica que `PINECONE_API_KEY` esté correctamente configurada

#### Error de Modelo de Embeddings
```
OSError: Can't load tokenizer for 'sentence-transformers/...'
```
**Solución**: 
```bash
pip install sentence-transformers torch
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

#### Error de Memoria
```
RuntimeError: CUDA out of memory
```
**Solución**: Usa un modelo más pequeño o procesa en lotes menores

#### Límite de Almacenamiento
```
PineconeException: Quota exceeded
```
**Solución**: 
1. Elimina documentos menos importantes
2. Usa un modelo con menor dimensión
3. Considera actualizar a plan de pago

### Comandos de Diagnóstico

```bash
# Verificar configuración
python install_vectordb.py --test-connection

# Probar modelo de embeddings
python install_vectordb.py --test-embeddings

# Ver estadísticas del índice
python setup_pinecone_vectordb.py --stats

# Ejecutar demostración básica
python demo_vectordb.py --demo-basic
```

## 📚 Integración con Otros Componentes

### Con Scrapers de Documentos
```python
# Después de extraer documentos
from setup_pinecone_vectordb import LegalDocumentProcessor

processor = LegalDocumentProcessor()
processor.load_documents_to_pinecone()
```

### Con APIs Web
```python
from flask import Flask, request, jsonify
from semantic_search import SemanticSearchEngine

app = Flask(__name__)
search_engine = SemanticSearchEngine(...)

@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    results = search_engine.search(query)
    return jsonify(results)
```

### Con Interfaces de Usuario
```python
import streamlit as st
from semantic_search import SemanticSearchEngine

st.title("Búsqueda Legal Inteligente")
query = st.text_input("Ingresa tu consulta:")

if query:
    results = search_engine.search(query)
    for result in results:
        st.write(f"**{result['metadata']['title']}**")
        st.write(result['content'][:300] + "...")
```

## 🔄 Mantenimiento y Actualizaciones

### Actualización de Documentos
```bash
# Actualizar documentos existentes
python setup_pinecone_vectordb.py --update-documents

# Añadir nuevos documentos
python setup_pinecone_vectordb.py --load-documents --incremental
```

### Backup y Restauración
```bash
# Exportar metadatos
python setup_pinecone_vectordb.py --export-metadata backup.json

# Recrear índice desde backup
python setup_pinecone_vectordb.py --import-metadata backup.json
```

### Monitoreo de Uso
```python
from setup_pinecone_vectordb import PineconeVectorDB

vectordb = PineconeVectorDB(...)
stats = vectordb.get_index_stats()

print(f"Documentos: {stats['total_vector_count']}")
print(f"Almacenamiento: {stats['storage_usage_mb']:.1f} MB")
print(f"Uso del límite: {stats['usage_percentage']:.1f}%")
```

## 🤝 Contribución y Desarrollo

### Estructura del Código
```
src/
├── vectordb/
│   ├── __init__.py
│   ├── pinecone_client.py      # Cliente de Pinecone
│   ├── embedding_generator.py  # Generación de embeddings
│   ├── document_processor.py   # Procesamiento de documentos
│   └── search_engine.py        # Motor de búsqueda
├── utils/
│   ├── config.py              # Gestión de configuración
│   ├── logging.py             # Sistema de logging
│   └── validators.py          # Validadores
└── tests/
    ├── test_vectordb.py       # Tests de base de datos
    ├── test_embeddings.py     # Tests de embeddings
    └── test_search.py         # Tests de búsqueda
```

### Ejecutar Tests
```bash
# Tests completos
python -m pytest tests/ -v

# Tests específicos
python -m pytest tests/test_vectordb.py -v

# Tests con cobertura
python -m pytest tests/ --cov=src --cov-report=html
```

### Añadir Nuevos Modelos
```python
# En embedding_generator.py
class EmbeddingGenerator:
    def _load_custom_model(self, model_name: str):
        if model_name == "tu-modelo-personalizado":
            # Implementar carga del modelo
            pass
```

## 📄 Licencia y Créditos

### Licencia
Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

### Créditos
- **Pinecone**: Motor de base de datos vectorial
- **Sentence Transformers**: Modelos de embeddings
- **Hugging Face**: Repositorio de modelos
- **OpenAI**: Modelo Ada-002 (opcional)

### Contribuidores
- Asistente IA - Desarrollo inicial
- Comunidad - Mejoras y sugerencias

## 📞 Soporte

### Documentación Adicional
- [Documentación de Pinecone](https://docs.pinecone.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

### Problemas y Sugerencias
Para reportar problemas o sugerir mejoras:
1. Revisa la sección de solución de problemas
2. Ejecuta los comandos de diagnóstico
3. Documenta el error con logs completos
4. Incluye tu configuración (sin API keys)

---

**¡Disfruta explorando el mundo del derecho mexicano con búsqueda semántica inteligente!** 🇲🇽⚖️🔍