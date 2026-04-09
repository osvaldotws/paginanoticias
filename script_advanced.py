import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from datetime import datetime
from urllib.parse import urljoin, urlparse
import feedparser
import traceback

# Configuración
CONFIG_FILE = "config.json"
HISTORY_FILE = "news_history.json"
TEMPLATE_FILE = "template.html"
OUTPUT_FILE = "index.html"
IMAGE_FILE = "latest_image.png"

def load_config():
    """Cargar configuración desde config.json"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"✅ Configuración cargada: {config.get('source_name', 'Unknown')}")
            return config
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        # Configuración por defecto para El Ancasti
        return {
            "source_name": "El Ancasti",
            "base_url": "https://www.elancasti.com.ar",
            "news_page_url": "https://www.elancasti.com.ar/",
            "use_rss": False,
            "scraping_config": {
                "container_selector": "article, .nota-item, .card",
                "title_selector": "h2, h3, .titulo, h2 a, h3 a",
                "link_selector": "a[href]",
                "summary_selector": "p.bajada, .bajada, p:nth-of-type(1)",
                "max_articles_to_process": 5
            }
        }

def get_headers(config=None):
    """Headers para simular navegador real"""
    user_agent = config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36') if config else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

def fetch_news_from_rss(rss_url):
    """Extraer noticias desde RSS"""
    print(f"📡 Leyendo RSS: {rss_url}")
    try:
        feed = feedparser.parse(rss_url)
        articles = []
        
        for entry in feed.entries[:5]:
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('summary', entry.get('description', '')),
                'published': entry.get('published', ''),
                'full_content': None
            })
        
        print(f"✅ Encontrados {len(articles)} artículos en RSS")
        return articles
    except Exception as e:
        print(f"❌ Error leyendo RSS: {e}")
        return []

def fetch_news_from_web(config):
    """Extraer noticias scrapeando una página web"""
    news_page_url = config['news_page_url']
    base_url = config['base_url']
    scraping_config = config['scraping_config']
    
    print(f"🕷️ Scrapeando: {news_page_url}")
    
    try:
        response = requests.get(news_page_url, headers=get_headers(config), timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Verificar que obtenimos HTML
        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(f"⚠️ La respuesta no es HTML: {response.headers.get('Content-Type')}")
            return []
        
        # Pequeña pausa para ser respetuosos con el servidor
        time.sleep(random.uniform(2, 3))
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Encontrar todos los contenedores de artículos
        container_selector = scraping_config.get('container_selector', 'article')
        containers = soup.select(container_selector)
        
        print(f"📦 Contenedores encontrados: {len(containers)}")
        
        for container in containers[:scraping_config.get('max_articles_to_process', 5)]:
            try:
                # Extraer título
                title_selector = scraping_config.get('title_selector', 'h2 a')
                title_elem = container.select_one(title_selector)
                if not title_elem:
                    # Intentar encontrar título en el contenedor actual si es un enlace
                    if container.name == 'a' or container.has_attr('href'):
                        title_elem = container
                    else:
                        continue
                
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                
                # Extraer link
                link_selector = scraping_config.get('link_selector', 'a[href]')
                link_elem = container.select_one(link_selector) if container.name != 'a' else container
                if not link_elem:
                    continue
                    
                link_href = link_elem.get('href')
                if not link_href:
                    continue
                    
                link = urljoin(base_url, link_href)
                
                # Validar que el link sea del mismo dominio
                parsed_link = urlparse(link)
                parsed_base = urlparse(base_url)
                if parsed_link.netloc != parsed_base.netloc:
                    continue
                
                # Extraer resumen
                summary_selector = scraping_config.get('summary_selector', 'p')
                summary_elem = container.select_one(summary_selector)
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                # Si no hay resumen, usar el título o un fragmento
                if not summary:
                    summary = title[:200]
                
                # Extraer fecha si existe
                date_selector = scraping_config.get('date_selector', 'time')
                date_elem = container.select_one(date_selector)
                published = date_elem.get_text(strip=True) if date_elem else ''
                
                # Extraer imagen si existe
                image_selector = scraping_config.get('image_selector', 'img[src]')
                image_elem = container.select_one(image_selector)
                image_url = urljoin(base_url, image_elem.get('src')) if image_elem and image_elem.get('src') else None
                
                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary[:500],  # Limitar longitud
                    'published': published,
                    'image_url': image_url,
                    'full_content': None
                })
                
            except Exception as e:
                print(f"⚠️ Error procesando artículo: {e}")
                continue
        
        print(f"✅ Encontrados {len(articles)} artículos válidos")
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de red al scrapear: {e}")
        return []
    except Exception as e:
        print(f"❌ Error al scrapear: {e}")
        traceback.print_exc()
        return []

def extract_full_content(article_link, config):
    """Extraer contenido completo de un artículo"""
    if not config.get('content_extraction', {}).get('extract_full_content', False):
        return None
    
    body_selector = config['content_extraction'].get('body_selector', 'article')
    
    try:
        print(f"📄 Extrayendo contenido: {article_link[:60]}...")
        response = requests.get(article_link, headers=get_headers(config), timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        time.sleep(random.uniform(1, 2))
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Intentar varios selectores
        content_elem = None
        selectors_to_try = [body_selector, 'article', '.post-content', '.entry-content', '.contenido', '.nota-contenido', 'main']
        
        for selector in selectors_to_try:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if content_elem:
            # Eliminar scripts y estilos
            for elem in content_elem(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                elem.decompose()
            
            full_text = content_elem.get_text(separator='\n', strip=True)
            return full_text[:3000]  # Limitar longitud
        
    except Exception as e:
        print(f"⚠️ Error extrayendo contenido: {e}")
    
    return None

client = None

def initialize_gemini():
    """Inicializar cliente Gemini"""
    global client
    if client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY no está configurada")
        client = genai.Client(api_key=api_key)
        print("✅ Cliente Gemini inicializado")
    return client

def process_with_gemini(title, summary, full_content=None):
    """Procesar noticia con Gemini AI"""
    gemini_client = initialize_gemini()
    
    content_to_use = full_content if full_content and len(full_content) > 100 else summary
    
    prompt = f"""
Actúa como un periodista experto de Argentina. Re-escribe la siguiente noticia para un portal de noticias profesional.

Título original: {title}
Resumen: {summary}
{"Contenido completo: " + full_content[:2000] if full_content and len(full_content) > 100 else ""}

Instrucciones:
1. Crea un título llamativo y profesional en español argentino
2. Escribe un cuerpo de 3-4 párrafos con tono periodístico y analítico
3. Incluye contexto local si es relevante
4. Devuelve JSON estricto con esta estructura:
{{
  "titulo_es": "título atractivo",
  "contenido_es": "contenido completo en varios párrafos separados por \\n\\n",
  "categoria": "Política|Economía|Deportes|Espectáculos|Tecnología|Sociedad|Internacional|General",
  "keywords": ["palabra1", "palabra2", "palabra3"],
  "image_description_en": "Professional photography prompt in English. Include: subject, lighting, composition, camera specs like 85mm lens, f/1.8, cinematic lighting, photorealistic, 8k"
}}
"""
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        result = json.loads(response.text)
        print("✅ Contenido generado con IA")
        return result
    except Exception as e:
        print(f"❌ Error procesando con Gemini: {e}")
        # Respuesta de fallback
        return {
            "titulo_es": title,
            "contenido_es": summary,
            "categoria": "General",
            "keywords": ["noticia"],
            "image_description_en": "News photography, professional, realistic"
        }

def generate_image(image_prompt):
    """Generar imagen con Imagen 3"""
    gemini_client = initialize_gemini()
    
    try:
        print("🎨 Generando imagen...")
        response = gemini_client.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=image_prompt,
            config=types.GenerateImageConfig(
                aspect_ratio="16:9",
                output_mime_type="image/png"
            )
        )
        
        if response.generated_images and len(response.generated_images) > 0:
            response.generated_images[0].image.save(IMAGE_FILE)
            print(f"✅ Imagen guardada: {IMAGE_FILE}")
            return True
    except Exception as e:
        print(f"⚠️ Error generando imagen: {e}")
    
    return False

def main():
    print("=" * 60)
    print("🚀 Iniciando sistema de noticias automatizado")
    print("=" * 60)
    
    # Cargar configuración
    config = load_config()
    
    # Cargar historial
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            print(f"📚 Historial cargado: {len(history.get('processed_links', []))} links, {len(history.get('articles', []))} artículos")
        except:
            history = {'processed_links': [], 'articles': []}
            print("📚 Nuevo historial creado")
    else:
        history = {'processed_links': [], 'articles': []}
        print("📚 Historial nuevo creado")
    
    # Determinar método de extracción
    if config.get('use_rss', False) and config.get('rss_url'):
        articles = fetch_news_from_rss(config['rss_url'])
    else:
        articles = fetch_news_from_web(config)
    
    if not articles:
        print("⚠️ No se encontraron artículos")
        # Generar HTML vacío de todas formas
        generate_html(history.get('articles', []))
        return
    
    # Filtrar artículos ya procesados
    processed_links = history.get('processed_links', [])
    new_articles = [a for a in articles if a['link'] not in processed_links]
    
    if not new_articles:
        print("ℹ️ No hay noticias nuevas")
        generate_html(history.get('articles', []))
        return
    
    print(f"🆕 {len(new_articles)} noticias nuevas para procesar")
    
    processed_articles = []
    
    # Procesar máximo 3 artículos por ejecución para evitar timeouts
    max_to_process = min(3, len(new_articles))
    
    for i, article in enumerate(new_articles[:max_to_process]):
        print(f"\n[{i+1}/{max_to_process}] 📰 Procesando: {article['title'][:50]}...")
        
        # Extraer contenido completo si está configurado
        full_content = None
        if config.get('content_extraction', {}).get('extract_full_content', False):
            full_content = extract_full_content(article['link'], config)
        
        # Procesar con IA
        try:
            nueva_noticia = process_with_gemini(
                article['title'],
                article['summary'],
                full_content
            )
            
            # Generar imagen (opcional, puede fallar sin detener el proceso)
            image_generated = False
            image_desc = nueva_noticia.get('image_description_en', '')
            if image_desc and len(image_desc) > 10:
                image_generated = generate_image(image_desc)
            
            # Crear slug único
            slug = nueva_noticia.get('titulo_es', article['title'])[:50].lower()
            slug = ''.join(c for c in slug if c.isalnum() or c in ' -_')
            slug = slug.replace(' ', '-').replace('--', '-')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_id = f"{slug[:30]}-{timestamp}"
            
            processed_article = {
                'id': unique_id,
                'titulo': nueva_noticia['titulo_es'],
                'contenido': nueva_noticia['contenido_es'],
                'resumen': article['summary'][:200],
                'categoria': nueva_noticia.get('categoria', 'General'),
                'keywords': nueva_noticia.get('keywords', []),
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'fecha_timestamp': datetime.now().isoformat(),
                'link_original': article['link'],
                'imagen': IMAGE_FILE if image_generated else article.get('image_url'),
                'destacada': (i == 0),  # El primero es destacado
                'vistas': 0
            }
            
            processed_articles.append(processed_article)
            processed_links.append(article['link'])
            
            # Pausa entre artículos
            if i < max_to_process - 1:
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error procesando artículo: {e}")
            traceback.print_exc()
            continue
    
    if not processed_articles:
        print("⚠️ No se pudo procesar ninguna noticia")
        generate_html(history.get('articles', []))
        return
    
    # Actualizar historial
    all_articles = processed_articles + history.get('articles', [])
    max_items = config.get('output', {}).get('max_history_items', 50)
    max_links = config.get('output', {}).get('max_processed_links', 100)
    
    history['articles'] = all_articles[:max_items]
    history['processed_links'] = processed_links[-max_links:]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\n📚 Historial actualizado: {len(history['articles'])} artículos totales")
    
    # Generar HTML con todas las noticias
    generate_html(history['articles'])
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado exitosamente")
    print("=" * 60)

def generate_html(articles):
    """Generar archivo HTML con todas las noticias"""
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Preparar datos de artículos para JavaScript
        articles_json = json.dumps(articles, ensure_ascii=False)
        
        html_content = template.replace("{{NEWS_DATA}}", articles_json)
        html_content = html_content.replace("{{FECHA_ACTUALIZACION}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTML generado: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Error generando HTML: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
