# Guía del Scraper del DOF

Esta guía explica cómo usar el scraper del Diario Oficial de la Federación (DOF) para extraer publicaciones legales mexicanas.

## Características

- ✅ Extracción de publicaciones diarias del DOF
- ✅ Manejo robusto de errores de conexión con reintentos automáticos
- ✅ Soporte para fechas específicas y rangos de fechas
- ✅ Extracción opcional del contenido completo de cada publicación
- ✅ Organización automática de archivos por año y mes
- ✅ Formato JSON estructurado para fácil procesamiento
- ✅ Logging detallado para monitoreo

## Instalación

Asegúrate de tener instaladas las dependencias:

```bash
pip install requests beautifulsoup4 selenium loguru pydantic
```

## Uso Básico

### Script de Línea de Comandos

El script principal `scrape_dof.py` ofrece múltiples opciones:

```bash
# Extraer publicaciones de hoy
python scrape_dof.py --today

# Extraer publicaciones de ayer
python scrape_dof.py --yesterday

# Extraer fecha específica
python scrape_dof.py --date 2025-08-12

# Extraer rango de fechas
python scrape_dof.py --start 2025-08-01 --end 2025-08-07

# Extraer última semana
python scrape_dof.py --last-week

# Incluir contenido completo (más lento)
python scrape_dof.py --today --content

# Especificar directorio de salida
python scrape_dof.py --today --output ./mi_directorio

# Modo verbose para debugging
python scrape_dof.py --today --verbose
```

### Uso Programático

```python
from src.scrapers import DOFScraper
from datetime import datetime

# Crear instancia del scraper
with DOFScraper() as scraper:
    # Obtener publicaciones de hoy
    publications = scraper.get_daily_publications()
    
    # Obtener publicaciones de fecha específica
    date = datetime(2025, 8, 12)
    publications = scraper.get_daily_publications(date)
    
    # Obtener contenido completo de una publicación
    if publications:
        content = scraper.get_publication_content(publications[0]['url'])
    
    # Extraer rango de fechas
    start_date = datetime(2025, 8, 1)
    end_date = datetime(2025, 8, 7)
    all_publications = scraper.scrape_date_range(start_date, end_date)
    
    # Guardar publicaciones
    scraper.save_publications(publications)
```

## Estructura de Datos

### Publicación Básica

Cada publicación extraída tiene la siguiente estructura:

```json
{
  "title": "Título de la publicación",
  "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5765226&fecha=12/08/2025",
  "codigo": "5765226",
  "date": "2025-08-12 01:09:05.528824",
  "source": "DOF",
  "scraped_at": "2025-08-13 01:09:08.144119"
}
```

### Publicación con Contenido Completo

Cuando se usa la opción `--content`, se añaden campos adicionales:

```json
{
  "title": "Título completo de la publicación",
  "content": "Contenido completo del documento...",
  "metadata": {
    "fecha_encontrada": "12 de agosto de 2025",
    "description": "Meta descripción si está disponible"
  },
  "sections": [],
  "legal_document": {
    "id": null,
    "title": "Título",
    "content": "Contenido completo",
    "document_type": "otro",
    "source": "dof",
    "status": "raw"
  }
}
```

## Organización de Archivos

Los archivos se organizan automáticamente:

```
data/raw/dof/
├── 2025/
│   ├── 08/
│   │   ├── dof_2025-08-12_5765226.json
│   │   ├── dof_2025-08-12_5765227.json
│   │   └── ...
│   └── 09/
│       └── ...
└── 2024/
    └── ...
```

## Configuración

Las configuraciones se pueden ajustar en `src/utils/config.py` o mediante variables de entorno:

```python
# URLs y configuración web
DOF_BASE_URL="https://www.dof.gob.mx/"
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."

# Configuración de scraping
SCRAPE_DELAY=1.0  # Segundos entre requests
REQUEST_TIMEOUT=30  # Timeout en segundos
MAX_RETRIES=3  # Máximo número de reintentos
```

## Manejo de Errores

El scraper incluye manejo robusto de errores:

- **Errores de conexión**: Reintentos automáticos con delay
- **Errores SSL**: Verificación deshabilitada para sitios problemáticos
- **Timeouts**: Configurables por request
- **Errores de parsing**: Logging detallado sin interrumpir el proceso

## Limitaciones y Consideraciones

### Limitaciones Técnicas

- El scraper depende de la estructura HTML del sitio del DOF
- Cambios en el sitio web pueden requerir actualizaciones del código
- La verificación SSL está deshabilitada debido a problemas del sitio

### Consideraciones Éticas

- **Respeta los términos de servicio** del sitio web
- **Usa delays apropiados** entre requests (configurado en 1 segundo por defecto)
- **No sobrecargues el servidor** con requests excesivos
- **Solo extrae información pública** disponible en el sitio

### Recomendaciones de Uso

- Ejecuta el scraper durante horas de menor tráfico
- Monitorea los logs para detectar problemas
- Haz backups regulares de los datos extraídos
- Considera usar proxies para scraping intensivo

## Troubleshooting

### Problemas Comunes

**Error de conexión SSL:**
```
SSLError: certificate verify failed
```
*Solución*: El scraper ya maneja esto deshabilitando la verificación SSL.

**Timeout de conexión:**
```
ConnectionError: Max retries exceeded
```
*Solución*: Aumenta `REQUEST_TIMEOUT` y `MAX_RETRIES` en la configuración.

**No se encuentran publicaciones:**
```
No se encontraron publicaciones para [fecha]
```
*Solución*: Verifica que la fecha sea un día laborable y que haya publicaciones.

**Error de parsing:**
```
Error procesando enlace de publicación
```
*Solución*: El sitio web puede haber cambiado su estructura. Revisa los logs detallados.

### Debugging

Para debugging detallado:

```bash
# Ejecutar con logs verbose
python scrape_dof.py --today --verbose

# Ejecutar script de prueba
python test_dof_scraper.py
```

## Próximas Mejoras

- [ ] Clasificación automática de tipos de documentos
- [ ] Extracción de metadatos más detallados
- [ ] Soporte para filtros por tipo de publicación
- [ ] Integración con base de datos vectorial
- [ ] API REST para acceso programático
- [ ] Dashboard web para monitoreo

## Soporte

Para reportar problemas o sugerir mejoras:

1. Revisa los logs detallados
2. Ejecuta el script de prueba
3. Documenta el error con ejemplos
4. Incluye información del entorno (OS, Python version, etc.)

---

*Última actualización: Agosto 2025*