# Asistente Legal Mexicano 🇲🇽⚖️

Asistente legal especializado en leyes mexicanas que utiliza web scraping, procesamiento de lenguaje natural e inteligencia artificial para proporcionar consultas actualizadas sobre el marco jurídico mexicano.

## Estado del Proyecto

🚧 **En Desarrollo Activo** 🚧

Este proyecto está actualmente en desarrollo. Las funcionalidades se están implementando de manera incremental.

### ✅ Funcionalidades Implementadas

- **Scraper del DOF**: Extracción completa de publicaciones del Diario Oficial de la Federación
  - Soporte para fechas específicas y rangos de fechas
  - Manejo robusto de errores con reintentos automáticos
  - Extracción opcional de contenido completo
  - Organización automática de archivos por fecha
  - Script de línea de comandos fácil de usar

### 🔄 En Desarrollo

- Scrapers para Constitución Política y Orden Jurídico Nacional
- Base de datos vectorial con ChromaDB/Pinecone
- API REST con FastAPI
- Procesamiento de texto con spaCy
- Interfaz conversacional con LangChain

## 🎯 Características

- **Web Scraping Automatizado**: Extrae información actualizada de fuentes oficiales mexicanas
- **Base de Datos Vectorial**: Almacena y consulta documentos legales de manera eficiente
- **IA Conversacional**: Responde preguntas basándose en información legal actualizada
- **API REST**: Interfaz programática para integración con otras aplicaciones
- **Actualizaciones Automáticas**: Mantiene la información legal siempre actualizada

## 📚 Fuentes de Datos

- **[Diario Oficial de la Federación (DOF)](https://www.dof.gob.mx/)**: Publicaciones oficiales diarias
- **[Constitución Política de México](https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf)**: Texto constitucional actualizado
- **[Orden Jurídico Nacional](https://www.ordenjuridico.gob.mx/leyes.php)**: Compilación completa de leyes

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.9+**: Lenguaje principal
- **FastAPI**: Framework web para API REST
- **LangChain**: Orquestación de LLM y RAG
- **ChromaDB/Pinecone**: Base de datos vectorial
- **PostgreSQL**: Base de datos relacional
- **Redis**: Cache y sesiones

### Web Scraping
- **BeautifulSoup4**: Parsing HTML
- **Scrapy**: Framework de scraping
- **Selenium**: Automatización de navegador
- **Requests**: Cliente HTTP

### Procesamiento de Datos
- **spaCy**: Procesamiento de lenguaje natural
- **Pandas**: Manipulación de datos
- **PyPDF2**: Procesamiento de PDFs

### IA y Embeddings
- **OpenAI GPT-4**: Modelo conversacional
- **OpenAI Embeddings**: Generación de embeddings
- **Sentence Transformers**: Embeddings alternativos

## 🚀 Instalación

### Prerrequisitos
- Python 3.9 o superior
- Git
- PostgreSQL (opcional)
- Redis (opcional)

### Configuración del Entorno

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd legal-assistant-mx
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Ejecutar el proyecto**:
   ```bash
   python main.py
   ```

## Uso Rápido

### Scraper del DOF

Para comenzar a extraer publicaciones del Diario Oficial de la Federación:

```bash
# Extraer publicaciones de ayer
python scrape_dof.py --yesterday

# Extraer fecha específica
python scrape_dof.py --date 2025-08-12

# Extraer con contenido completo
python scrape_dof.py --today --content

# Ver todas las opciones
python scrape_dof.py --help
```

Para más detalles, consulta la [Guía del Scraper del DOF](docs/dof_scraper_guide.md).

## ⚙️ Configuración

### Variables de Entorno Principales

```env
# OpenAI (Requerido)
OPENAI_API_KEY=your_openai_api_key_here

# Base de Datos Vectorial (Elegir una)
PINECONE_API_KEY=your_pinecone_api_key_here  # Para Pinecone
# O usar ChromaDB local (por defecto)

# Base de Datos (Opcional)
DATABASE_URL=postgresql://user:pass@localhost:5432/legal_assistant
REDIS_URL=redis://localhost:6379/0
```

## 📁 Estructura del Proyecto

```
legal-assistant-mx/
├── src/
│   ├── scrapers/          # Web scrapers especializados
│   ├── database/          # Gestión de bases de datos
│   ├── api/              # API REST con FastAPI
│   ├── models/           # Modelos de datos
│   └── utils/            # Utilidades y configuración
├── data/                 # Datos extraídos y procesados
├── logs/                 # Archivos de log
├── tests/                # Tests unitarios
├── requirements.txt      # Dependencias Python
├── pyproject.toml       # Configuración del proyecto
└── main.py              # Punto de entrada
```

## 🔄 Flujo de Trabajo

1. **Extracción**: Los scrapers obtienen datos de fuentes oficiales
2. **Procesamiento**: Se limpia y estructura la información legal
3. **Vectorización**: Se generan embeddings de los documentos
4. **Almacenamiento**: Se guarda en base de datos vectorial
5. **Consulta**: La IA responde usando RAG (Retrieval-Augmented Generation)

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=src

# Tests específicos
pytest tests/test_scrapers.py
```

## 📝 Desarrollo

### Formateo de Código
```bash
# Formatear código
black src/

# Verificar estilo
flake8 src/

# Type checking
mypy src/
```

### Contribuir
1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## ⚠️ Disclaimer Legal

Este asistente es una herramienta de apoyo y no constituye asesoría legal profesional. Siempre consulte con un abogado calificado para asuntos legales importantes.

## 🤝 Soporte

Para reportar bugs o solicitar funcionalidades, por favor crear un issue en el repositorio.

---

**Desarrollado con ❤️ para la comunidad legal mexicana**