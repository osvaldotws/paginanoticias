# 🤖 TechNews AI - Sistema de Noticias Automatizado

Sistema automatizado que extrae noticias de sitios web (con o sin RSS), las procesa con Gemini AI, genera imágenes con Imagen 3, y publica un sitio web profesional en GitHub Pages.

## ✨ Características Principales

### 🔍 Extracción Flexible
- **Soporte RSS**: Lee feeds RSS tradicionales
- **Web Scraping Inteligente**: Extrae noticias de sitios sin RSS usando selectores CSS configurables
- **Contenido Completo**: Opción para extraer el artículo completo visitando cada URL
- **Configuración para El Ancasti**: Pre-configurado para `https://www.elancasti.com.ar`

### 🧠 Procesamiento con IA
- **Redacción Profesional**: Gemini AI reescribe noticias con tono periodístico argentino
- **Clasificación Automática**: Categoriza en Política, Economía, Deportes, Espectáculos, Tecnología, Sociedad, Internacional, General
- **Keywords SEO**: Genera palabras clave automáticamente
- **Imágenes Personalizadas**: Genera imágenes únicas con Imagen 3 (opcional)

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
├── config.json             # Configuración de fuentes y selectores (¡EDITAR AQUÍ!)
├── news_history.json       # Historial de noticias procesadas (auto-generado)
├── index.html              # Página web resultante (auto-generado)
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
git commit -m "Initial commit - Sistema de Noticias AI"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### 2. Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Get API Key"** o **"Create API Key"**
4. Copia la clave generada (comienza con `AIza...`)

> 💡 **Nota**: La API de Gemini es gratuita hasta cierto límite. Revisa los precios en [Google AI Pricing](https://ai.google.dev/pricing)

### 3. Configurar Secretos en GitHub

1. En tu repositorio de GitHub, ve a **Settings** → **Secrets and variables** → **Actions**
2. Haz clic en **"New repository secret"**
3. Completa:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: (pega tu API Key de Gemini)
4. Haz clic en **"Add secret"**

### 4. Activar GitHub Pages

#### Método A: Usando GitHub Actions (RECOMENDADO)

El workflow ya está configurado para desplegar automáticamente. Solo necesitas:

1. Ir a **Settings** → **Pages**
2. En **Build and deployment**:
   - **Source**: Seleccionar **"GitHub Actions"**
3. El sistema desplegará automáticamente después de cada ejecución del workflow

#### Método B: Usando Rama gh-pages (Alternativo)

Si prefieres el método tradicional:

1. Ir a **Settings** → **Pages**
2. En **Build and deployment**:
   - **Source**: **"Deploy from a branch"**
   - **Branch**: Seleccionar `gh-pages` y carpeta `/ (root)`
3. El workflow creará automáticamente la rama `gh-pages` con el contenido

### 5. Verificar/Modificar Configuración (config.json)

El archivo `config.json` ya está pre-configurado para **El Ancasti**. Si quieres cambiarlo:

```json
{
  "source_name": "El Ancasti",
  "base_url": "https://www.elancasti.com.ar",
  "news_page_url": "https://www.elancasti.com.ar/",
  "use_rss": false,
  "scraping_config": {
    "container_selector": "article.card, article.teaser, div.news-item, article, .nota-item",
    "title_selector": "h2, h3, .title, .headline, h2 a, h3 a, .titulo",
    "link_selector": "a[href]",
    "summary_selector": "p.summary, .excerpt, .description, p.bajada, .bajada, p:nth-of-type(1)",
    "max_articles_to_process": 5
  }
}
```

#### Para otro sitio web sin RSS:

1. Identifica los selectores CSS usando las herramientas de desarrollador del navegador (F12)
2. Modifica `config.json` con los nuevos selectores

### 6. Ejecutar Manualmente (Opcional - Para pruebas)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Establecer API Key
export GEMINI_API_KEY="tu-api-key-aqui"  # Linux/Mac
# o en Windows: set GEMINI_API_KEY=tu-api-key-aqui

# Ejecutar script
python script_advanced.py
```

## ⚙️ Automatización

El workflow se ejecuta:
- **Automáticamente**: Cada hora exacta (`0 * * * *` en cron)
- **Manualmente**: 
  1. Ve a **Actions** → **"Hourly News Update"**
  2. Haz clic en **"Run workflow"**
  3. Selecciona la rama `main`
  4. Espera ~2-3 minutos a que termine

### Flujo de Ejecución:

1. GitHub Actions se activa (cada hora o manualmente)
2. Instala Python y dependencias
3. Ejecuta `script_advanced.py`:
   - Scrapea noticias de El Ancasti
   - Filtra noticias ya procesadas
   - Procesa hasta 3 noticias nuevas con Gemini AI
   - Genera imágenes (opcional)
   - Actualiza `news_history.json`
   - Genera `index.html`
4. Hace commit y push de los cambios
5. Despliega a GitHub Pages

## 🎨 Personalización del Diseño

Edita `template.html` para cambiar:

- **Colores**: Busca `:root` en el CSS
- **Fuentes**: Cambia los enlaces de Google Fonts
- **Layout**: Modifica CSS Grid/Flexbox
- **Animaciones**: Ajusta las transiciones y keyframes

## 🔧 Troubleshooting

### Error: "No articles found"

**Causa**: Los selectores CSS no coinciden con la estructura del sitio

**Solución**:
1. Abre el sitio en tu navegador
2. Presiona F12 (Herramientas de desarrollador)
3. Inspecciona un artículo para encontrar sus clases/etiquetas
4. Actualiza `config.json` con los selectores correctos

### Error: "GEMINI_API_KEY no está configurada"

**Causa**: El secreto no está configurado correctamente

**Solución**:
1. Verifica en **Settings** → **Secrets and variables** → **Actions**
2. Asegúrate de que el nombre sea exactamente `GEMINI_API_KEY`
3. Verifica que la API Key sea válida en Google AI Studio

### Error: "Workflow failed with exit code 1"

**Causa**: El script encontró un error

**Solución**:
1. Ve a **Actions** → selecciona el workflow fallido
2. Expande el paso **"Run news scraper"**
3. Lee los mensajes de error (tienen emojis ❌ o ⚠️)
4. Soluciona según el error específico

### La página no se actualiza

**Causa**: GitHub Pages no está bien configurado

**Solución**:
1. Verifica en **Settings** → **Pages** que el Source sea **"GitHub Actions"**
2. Revisa que el workflow tenga el job `deploy` completado
3. Espera 1-2 minutos después del deploy

### Error de Node.js 20 (advertencia)

**Causa**: Las acciones están actualizándose a Node.js 24

**Solución**: Ya está resuelto en este proyecto usando las versiones más recientes:
- `actions/checkout@v5`
- `actions/setup-python@v6`
- `actions/deploy-pages@v5`

## 📊 Métricas y Análisis

El sistema trackea:
- ✅ Número total de artículos
- ✅ Vistas por artículo (localStorage del navegador)
- ✅ Fecha de última actualización
- ✅ Historial de últimos 50 artículos
- ✅ Links procesados (últimos 100)

## 🛡️ Consideraciones Legales y Éticas

- ✅ Respeta los `robots.txt` de cada sitio
- ✅ Delays entre requests (2-3 segundos) para no sobrecargar servidores
- ✅ Cita siempre la fuente original (incluida en cada artículo)
- ✅ Uso recomendado: fines personales/educativos
- ⚠️ Verifica los términos de servicio del sitio origen

## 📝 Licencia

MIT License - Libre uso y modificación

---

## 🎯 Resumen Rápido para Empezar

1. **Push inicial**: `git push -u origin main`
2. **API Key**: Configurar en GitHub Secrets como `GEMINI_API_KEY`
3. **GitHub Pages**: Settings → Pages → Source: GitHub Actions
4. **Primera ejecución**: Actions → Run workflow (o esperar 1 hora)
5. **Ver resultado**: `https://TU_USUARIO.github.io/TU_REPO/`

---

**Hecho con ❤️ desde Argentina 🇦🇷 y Gemini AI**
