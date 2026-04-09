# 🤖 TechNews AI - Sistema de Noticias Automatizado

Sistema automatizado que extrae noticias de sitios web (con o sin RSS), las procesa con Gemini AI, genera imágenes con Imagen 3, y publica un sitio web profesional en GitHub Pages.

## ✨ Características Principales

### 🔍 Extracción Flexible
- **Soporte RSS**: Lee feeds RSS tradicionales
- **Web Scraping**: Extrae noticias de sitios sin RSS usando selectores CSS configurables
- **Contenido Completo**: Opción para extraer el artículo completo visitando cada URL

### 🧠 Procesamiento con IA
- **Redacción Profesional**: Gemini AI reescribe noticias con tono periodístico
- **Clasificación Automática**: Categoriza en IA, Robótica, Biotech, Cybersecurity, Startups, General
- **Keywords SEO**: Genera palabras clave automáticamente
- **Imágenes Personalizadas**: Genera imágenes únicas con Imagen 3

### 🌐 Frontend Moderno
- **Diseño Responsive**: Se adapta a móviles, tablets y desktop
- **Filtros Interactivos**: Filtra por categoría en tiempo real
- **Modal de Lectura**: Vista detallada con animaciones suaves
- **Contador de Vistas**: Trackea lecturas por artículo
- **Tipografía Premium**: Inter + Playfair Display de Google Fonts

## 📁 Estructura del Proyecto

```
├── script_advanced.py      # Script principal de extracción y procesamiento
├── template.html           # Plantilla HTML con diseño moderno
├── config.json             # Configuración de fuentes y selectores
├── news_history.json       # Historial de noticias procesadas
├── requirements.txt        # Dependencias de Python
├── .gitignore              # Archivos ignorados por Git
├── README.md               # Esta documentación
└── .github/
    └── workflows/
        └── update_news.yml # Automatización horaria con GitHub Actions
```

## 🚀 Configuración Paso a Paso

### 1. Crear Repositorio en GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### 2. Obtener API Key de Gemini
1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Get API Key"
4. Copia la clave generada

### 3. Configurar Secretos en GitHub
1. En tu repositorio, ve a **Settings** → **Secrets and variables** → **Actions**
2. Haz clic en **New repository secret**
3. Nombre: `GEMINI_API_KEY`
4. Valor: (pega tu API Key de Gemini)
5. Guarda

### 4. Activar GitHub Pages
1. Ve a **Settings** → **Pages**
2. En **Build and deployment**:
   - Source: **GitHub Actions**
3. Guarda

### 5. Configurar Fuente de Noticias (config.json)

#### Opción A: Usando RSS
```json
{
  "source_name": "MIT Technology Review",
  "use_rss": true,
  "rss_url": "https://www.technologyreview.com/feed/",
  "base_url": "https://www.technologyreview.com"
}
```

#### Opción B: Web Scraping (sin RSS)
```json
{
  "source_name": "Nombre del Sitio",
  "use_rss": false,
  "news_page_url": "https://ejemplo.com/noticias",
  "base_url": "https://ejemplo.com",
  "scraping_config": {
    "container_selector": "article",
    "title_selector": "h2 a",
    "link_selector": "a",
    "summary_selector": "p.summary",
    "date_selector": "time",
    "max_articles_to_process": 5
  },
  "content_extraction": {
    "extract_full_content": true,
    "body_selector": ".article-body"
  }
}
```

### 6. Ejecutar Manualmente (Opcional)
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="tu-api-key-aqui"
python script_advanced.py
```

## ⚙️ Automatización

El workflow se ejecuta:
- **Automáticamente**: Cada hora exacta (`0 * * * *`)
- **Manualmente**: Desde GitHub Actions → "Hourly News Update" → "Run workflow"

## 🎨 Personalización del Diseño

Edita `template.html` para cambiar:
- Colores (variables CSS en `:root`)
- Fuentes (Google Fonts)
- Layout (CSS Grid/Flexbox)
- Animaciones

## 🔧 Troubleshooting

### Error: "No articles found"
- Verifica que los selectores CSS en `config.json` coincidan con la estructura HTML del sitio
- Usa las herramientas de desarrollador del navegador para inspeccionar los elementos

### Error: "API key not valid"
- Asegúrate de haber configurado el secreto `GEMINI_API_KEY` correctamente
- Verifica que la API Key esté activa en Google AI Studio

### Error: "Workflow failed"
- Revisa los logs en GitHub Actions
- Verifica que todas las dependencias estén en `requirements.txt`

## 📊 Métricas y Análisis

El sistema trackea:
- Número total de artículos
- Vistas por artículo (localStorage)
- Fecha de última actualización
- Historial de últimos 50 artículos

## 🛡️ Consideraciones Legales

- Respeta los `robots.txt` de cada sitio
- Añade delays entre requests (ya implementado)
- Cita siempre la fuente original
- Usa solo para fines personales/educativos

## 📝 Licencia

MIT License - Libre uso y modificación

---

**Hecho con ❤️ y Gemini AI**
