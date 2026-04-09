# Sistema de Noticias Automatizado con IA

Este proyecto utiliza **GitHub Actions** y **Google Gemini AI** para crear un sistema automatizado que:
1. Lee las últimas noticias de un feed RSS
2. Procesa el contenido con IA para reescribirlo en español
3. Genera una página web automáticamente
4. Publica la noticia en GitHub Pages

## Estructura del Proyecto

```
├── script.py                 # Script básico (solo texto)
├── script_advanced.py        # Script avanzado (texto + imágenes)
├── template.html             # Plantilla HTML para las noticias
├── requirements.txt          # Dependencias de Python
├── news_history.json         # Historial de noticias procesadas (auto-generado)
├── index.html                # Página web resultante (auto-generado)
├── latest_image.png          # Imagen generada por IA (auto-generado)
└── .github/
    └── workflows/
        ├── update_news.yml           # Workflow básico
        └── update_news_advanced.yml  # Workflow avanzado con imágenes
```

## Configuración

### 1. Generar tu API Key de Gemini

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Create API Key"
4. Copia la clave generada

### 2. Configurar Secretos en GitHub

1. En tu repositorio de GitHub, ve a **Settings > Secrets and variables > Actions**
2. Haz clic en **New repository secret**
3. Nombre: `GEMINI_API_KEY`
4. Valor: (Pega tu clave de Google)
5. Haz clic en **Add secret**

### 3. Activar GitHub Pages

1. Ve a **Settings > Pages**
2. En "Build and deployment", selecciona:
   - **Source**: Deploy from a branch
   - **Branch**: `main` y carpeta `/ (root)`
3. Haz clic en **Save**

En unos minutos, tu web estará disponible en: `https://tu-usuario.github.io/tu-repo/`

## Scripts Disponibles

### Opción 1: Script Básico (`script.py`)
- Lee noticias del feed RSS
- Procesa el contenido con Gemini AI
- Genera HTML con texto
- **No genera imágenes**

### Opción 2: Script Avanzado (`script_advanced.py`)
- Lee noticias del feed RSS
- Procesa el contenido con Gemini AI
- Genera imágenes con Imagen 3
- Genera HTML con texto e imagen
- **Requiere acceso a Imagen 3 API**

## Workflows de GitHub Actions

### Workflow Básico (`update_news.yml`)
- Se ejecuta cada hora (`0 * * * *`)
- Usa `script.py`
- Actualiza solo texto

### Workflow Avanzado (`update_news_advanced.yml`)
- Se ejecuta cada hora (`0 * * * *`)
- Usa `script_advanced.py`
- Actualiza texto e imágenes

## Ejecución Manual

Para probar el script localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Exportar tu API key
export GEMINI_API_KEY="tu-api-key-aqui"

# Ejecutar script básico
python script.py

# O ejecutar script avanzado
python script_advanced.py
```

## Personalización

### Cambiar la fuente de noticias

Edita la variable `RSS_URL` en el script:

```python
RSS_URL = "https://www.technologyreview.com/feed/"  # Cambia esta URL
```

Algunas fuentes RSS populares:
- MIT Technology Review: `https://www.technologyreview.com/feed/`
- TechCrunch: `https://techcrunch.com/feed/`
- The Verge: `https://www.theverge.com/rss/index.xml`
- Wired: `https://www.wired.com/feed/rss`

### Modificar el prompt de IA

Edita la función `process_with_gemini()` o `process_content_and_image_prompt()` para cambiar cómo la IA reescribe las noticias.

## Notas Importantes

1. **API Key**: Nunca commits tu API Key al repositorio. Usa siempre los secrets de GitHub.
2. **Historial**: El archivo `news_history.json` guarda las últimas 50 noticias procesadas para evitar duplicados.
3. **Costos**: El uso de la API de Gemini tiene costos asociados. Revisa la documentación oficial.
4. **Imágenes**: La generación de imágenes requiere acceso a Imagen 3, que puede tener disponibilidad limitada.

## Licencia

MIT License