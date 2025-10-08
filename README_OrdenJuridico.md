# Scraper del Orden Jurídico Nacional

Este scraper permite extraer leyes y reglamentos federales del sitio web oficial [ordenjuridico.gob.mx](https://www.ordenjuridico.gob.mx), que es mantenido por la Secretaría de Gobernación y contiene la compilación y sistematización de leyes federales, estatales, municipales, tratados internacionales, reglamentos, decretos y otros documentos jurídicos.

## 🎯 Características

- ✅ **Extracción de metadatos**: Título, código, tipo de documento, fecha de publicación
- ✅ **Contenido completo**: Extrae el texto completo de los documentos legales
- ✅ **Modo solo metadatos**: Opción para extraer únicamente metadatos sin contenido
- ✅ **Procesamiento por lotes**: Maneja múltiples URLs desde archivos o línea de comandos
- ✅ **Manejo robusto de errores**: Reintentos automáticos y manejo de fallos de conexión
- ✅ **Guardado estructurado**: Salida en formato JSON con estructura consistente
- ✅ **Logging detallado**: Información completa del proceso de extracción
- ✅ **Validación de URLs**: Verifica que las URLs sean del dominio correcto

## 📋 Requisitos

- Python 3.8+
- Chrome/Chromium instalado
- Dependencias del proyecto (ver `requirements.txt`)

## 🚀 Uso

### Línea de comandos

#### Extraer documentos específicos
```bash
# Extraer documentos con contenido completo
python scrape_orden_juridico.py --urls https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html

# Extraer múltiples documentos
python scrape_orden_juridico.py --urls \
  https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html \
  https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html

# Extraer solo metadatos (sin contenido completo)
python scrape_orden_juridico.py --urls URL1 URL2 --no-content
```

#### Extraer desde archivo de URLs
```bash
# Crear archivo con URLs (una por línea)
echo "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html" > urls.txt
echo "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html" >> urls.txt

# Extraer desde archivo
python scrape_orden_juridico.py --file urls.txt

# Con directorio de salida personalizado
python scrape_orden_juridico.py --file urls.txt --output /ruta/personalizada
```

#### Opciones adicionales
```bash
# Modo verbose (información detallada)
python scrape_orden_juridico.py --urls URL --verbose

# Ver ayuda completa
python scrape_orden_juridico.py --help
```

### Uso programático

```python
from src.scrapers.orden_juridico_scraper import OrdenJuridicoScraper
from pathlib import Path

# Crear instancia del scraper
scraper = OrdenJuridicoScraper()

# Extraer un documento específico
url = "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html"
document = scraper.scrape_document_by_url(url, extract_content=True)

if document:
    print(f"Título: {document.title}")
    print(f"Tipo: {document.document_type}")
    print(f"Fecha: {document.publication_date}")
    print(f"Contenido: {len(document.content)} caracteres")

# Extraer múltiples documentos
urls = [
    "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html",
    "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html"
]

documents = scraper.scrape_multiple_documents(urls, extract_content=True)
print(f"Extraídos {len(documents)} documentos")

# Guardar documentos
output_dir = Path("data/raw/orden_juridico")
scraper.save_documents(documents, output_dir)
```

## 📁 Estructura de salida

Los documentos se guardan en formato JSON con la siguiente estructura:

```json
{
  "id": "wo17186",
  "codigo": null,
  "title": "Reglamento General de Deberes Militares",
  "content": "[Contenido completo del documento...]",
  "summary": null,
  "document_type": "reglamento",
  "source": "orden_juridico",
  "publication_date": "1994-01-12T00:00:00",
  "effective_date": null,
  "scraped_at": "2025-08-13T01:22:15.123456",
  "url": "https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html",
  "pdf_url": null,
  "metadata": {
    "codigo": "17186",
    "extraction_method": "selenium_chrome"
  },
  "tags": [],
  "issuing_entity": null,
  "department": null,
  "status": "raw",
  "processing_notes": null,
  "sections": [],
  "embedding_model": null,
  "chunk_count": null
}
```

## 📂 Organización de archivos

Los documentos se organizan automáticamente:

```
data/raw/orden_juridico/
├── orden_juridico_wo17186.json    # Reglamento General de Deberes Militares
├── orden_juridico_wo88408.json    # Reglamento de la Cámara de Diputados
└── ...
```

## 🔍 Tipos de documentos soportados

El scraper puede identificar y clasificar automáticamente:

- **Reglamentos**: Documentos normativos específicos
- **Leyes**: Legislación federal
- **Decretos**: Disposiciones ejecutivas
- **Acuerdos**: Resoluciones administrativas
- **Otros**: Documentos no clasificados específicamente

## ⚙️ Configuración

El scraper utiliza la configuración global del proyecto definida en `src/utils/config.py`:

- **Directorio de datos**: `data/raw/orden_juridico/`
- **Timeout**: 30 segundos por página
- **Reintentos**: 3 intentos por URL
- **User-Agent**: Chrome estándar

## 🐛 Manejo de errores

El scraper incluye manejo robusto de errores:

- **Errores de conexión**: Reintentos automáticos
- **Páginas no encontradas**: Logging y continuación
- **Contenido malformado**: Extracción parcial cuando es posible
- **Timeouts**: Configurables por documento

## 📊 Ejemplos de URLs soportadas

```
# Reglamentos
https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo17186.html
https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo88408.html

# Leyes federales
https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo12345.html

# Formato general
https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo[CODIGO].html
```

## 🔧 Solución de problemas

### Error: "No se pudieron extraer documentos"
- Verifica que las URLs sean correctas y accesibles
- Comprueba la conectividad a internet
- Revisa los logs para errores específicos

### Error: "Chrome driver not found"
- Instala Chrome o Chromium
- Verifica que ChromeDriver esté en el PATH

### Error: "Validation error for LegalDocument"
- Verifica que el contenido se esté extrayendo correctamente
- Revisa que los campos requeridos no estén vacíos

## 📝 Logging

El scraper genera logs detallados que incluyen:

- URLs procesadas
- Documentos extraídos exitosamente
- Errores y reintentos
- Tiempo de procesamiento
- Estadísticas de extracción

## 🤝 Integración

Este scraper se integra perfectamente con:

- **DOF Scraper**: Para documentos del Diario Oficial
- **Sistema de embeddings**: Para procesamiento de texto
- **Base de datos vectorial**: Para búsqueda semántica
- **API de Lex iA**: Para consultas legales

## 📄 Licencia

Este código es parte del proyecto Lex iA y sigue las mismas condiciones de licencia.