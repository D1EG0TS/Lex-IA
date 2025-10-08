
# Lex iA - Arquitectura Técnica

## Resumen Ejecutivo

Lex iA es una plataforma de consultas legales que combina web scraping, procesamiento de lenguaje natural, bases de datos vectoriales e inteligencia artificial para proporcionar respuestas precisas sobre el marco jurídico mexicano.

## Stack Tecnológico

### Backend

#### Lenguaje Principal
- **Python 3.9+**
  - Ecosistema maduro para IA/ML
  - Excelente soporte para web scraping
  - Librerías especializadas en NLP

#### Framework Web
- **FastAPI 0.104.1**
  - Alto rendimiento (basado en Starlette/Pydantic)
  - Documentación automática con OpenAPI
  - Soporte nativo para async/await
  - Validación automática de tipos

#### Base de Datos

**Relacional:**
- **PostgreSQL**
  - Almacenamiento de metadatos
  - Gestión de usuarios y sesiones
  - Logs y auditoría

**Vectorial:**
- **ChromaDB 0.4.15** (Desarrollo)
  - Base de datos vectorial local
  - Fácil setup y desarrollo
- **Pinecone** (Producción)
  - Escalabilidad cloud
  - Alto rendimiento
  - Gestión automática de índices

**Cache:**
- **Redis 5.0.1**
  - Cache de consultas frecuentes
  - Gestión de sesiones
  - Rate limiting

#### Procesamiento de Lenguaje Natural

**Embeddings:**
- **OpenAI Embeddings**
  - Modelo: text-embedding-ada-002
  - Dimensiones: 1536
  - Soporte multiidioma
- **Sentence Transformers 2.2.2**
  - Modelos locales alternativos
  - Especialización en español

**Modelos de Lenguaje:**
- **DeepSeek API**
  - Generación de respuestas
  - Comprensión contextual
  - Especialización en tareas legales

**Framework de Orquestación:**
- **LangChain 0.0.340**
  - RAG (Retrieval-Augmented Generation)
  - Cadenas de procesamiento
  - Gestión de prompts
  - Integración con múltiples LLMs

#### Web Scraping

**Librerías Principales:**
- **Requests 2.31.0**: HTTP requests básicos
- **BeautifulSoup 4.12.2**: Parsing HTML/XML
- **Selenium 4.15.2**: Scraping dinámico
- **Scrapy 2.11.0**: Framework de scraping escalable

**Procesamiento de PDFs:**
- **PyPDF2 3.0.1**: Extracción básica de texto
- **pdfplumber 0.10.3**: Extracción avanzada con layout

#### Procesamiento de Datos
- **pandas 2.1.3**: Manipulación de datos
- **numpy 1.25.2**: Operaciones numéricas
- **spaCy 3.7.2**: NLP avanzado en español
- **NLTK 3.8.1**: Herramientas de procesamiento de texto

### Frontend

#### Aplicación Móvil
- **React Native 0.79.5**
  - Desarrollo multiplataforma
  - Rendimiento nativo
  - Ecosistema maduro

- **Expo SDK ~53.0.20**
  - Desarrollo rápido
  - Servicios integrados
  - Deployment simplificado

#### Librerías UI/UX
- **@react-navigation**: Navegación entre pantallas
- **expo-linear-gradient**: Gradientes y efectos visuales
- **react-native-reanimated**: Animaciones fluidas
- **@codsod/react-native-chat**: Interfaz de chat

#### Comunicación
- **Axios 1.11.0**: Cliente HTTP
- **react-native-webview**: Integración web

### DevOps y Herramientas

#### Desarrollo
- **TypeScript 5.8.3**: Tipado estático
- **ESLint 9.25.0**: Linting de código
- **Black 23.11.0**: Formateo de Python
- **pytest 7.4.3**: Testing framework

#### Gestión de Dependencias
- **pip**: Paquetes Python
- **npm**: Paquetes JavaScript
- **python-dotenv**: Variables de entorno

#### Monitoreo y Logging
- **Loguru**: Logging avanzado en Python
- **APScheduler 3.10.4**: Tareas programadas

## Arquitectura del Sistema

### Componentes Principales