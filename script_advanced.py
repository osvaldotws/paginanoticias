import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from datetime import datetime
from urllib.parse import urljoin
import feedparser

# Configuración
CONFIG_FILE = "config.json"
HISTORY_FILE = "news_history.json"
TEMPLATE_FILE = "template.html"
OUTPUT_FILE = "index.html"
IMAGE_FILE = "latest_image.png"

def load_config():
    """Cargar configuración desde config.json"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_headers():
    """Headers para simular navegador real"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def fetch_news_from_rss(rss_url):
    """Extraer noticias desde RSS"""
    print(f"Leyendo RSS: {rss_url}")
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
    
    return articles

def fetch_news_from_web(config):
    """Extraer noticias scrapeando una página web"""
    news_page_url = config['news_page_url']
    base_url = config['base_url']
    scraping_config = config['scraping_config']
    
    print(f"Scrapeando: {news_page_url}")
    
    try:
        response = requests.get(news_page_url, headers=get_headers(), timeout=30)
        response.raise_for_status()
        
        # Pequeña pausa para ser respetuosos con el servidor
        time.sleep(random.uniform(1, 2))
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Encontrar todos los contenedores de artículos
        containers = soup.select(scraping_config.get('container_selector', 'article'))
        
        for container in containers[:scraping_config.get('max_articles_to_process', 5)]:
            try:
                # Extraer título
                title_elem = container.select_one(scraping_config.get('title_selector', 'h2 a'))
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # Extraer link
                link_elem = container.select_one(scraping_config.get('link_selector', 'a'))
                if not link_elem or not link_elem.get('href'):
                    continue
                link = urljoin(base_url, link_elem['href'])
                
                # Extraer resumen
                summary_elem = container.select_one(scraping_config.get('summary_selector', 'p'))
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                # Extraer fecha si existe
                date_elem = container.select_one(scraping_config.get('date_selector', 'time'))
                published = date_elem.get_text(strip=True) if date_elem else ''
                
                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published': published,
                    'full_content': None
                })
                
            except Exception as e:
                print(f"Error procesando artículo: {e}")
                continue
        
        print(f"Encontrados {len(articles)} artículos")
        return articles
        
    except Exception as e:
        print(f"Error al scrapear: {e}")
        return []

def extract_full_content(article_link, config):
    """Extraer contenido completo de un artículo"""
    if not config.get('content_extraction', {}).get('extract_full_content', False):
        return None
    
    body_selector = config['content_extraction'].get('body_selector', 'article')
    
    try:
        print(f"Extrayendo contenido completo: {article_link}")
        response = requests.get(article_link, headers=get_headers(), timeout=30)
        response.raise_for_status()
        
        time.sleep(random.uniform(1, 2))
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Intentar varios selectores
        content_elem = None
        for selector in [body_selector, 'article', '.post-content', '.entry-content', 'main']:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if content_elem:
            # Eliminar scripts y estilos
            for elem in content_elem(['script', 'style', 'nav', 'header', 'footer']):
                elem.decompose()
            
            full_text = content_elem.get_text(separator='\n', strip=True)
            return full_text[:3000]  # Limitar longitud
        
    except Exception as e:
        print(f"Error extrayendo contenido: {e}")
    
    return None

client = None

def initialize_gemini():
    """Inicializar cliente Gemini"""
    global client
    if client is None:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return client

def process_with_gemini(title, summary, full_content=None):
    """Procesar noticia con Gemini AI"""
    gemini_client = initialize_gemini()
    
    content_to_use = full_content if full_content else summary
    
    prompt = f"""
    Actúa como un periodista experto en tecnología. Re-escribe la siguiente noticia para un blog profesional.
    
    Título original: {title}
    Resumen: {summary}
    {"Contenido completo: " + full_content[:2000] if full_content else ""}
    
    Instrucciones:
    1. Crea un título llamativo y profesional en español
    2. Escribe un cuerpo de 3-4 párrafos con tono analítico y profundo
    3. Incluye contexto y análisis, no solo traducción
    4. Devuelve JSON estricto con esta estructura:
    {{
      "titulo_es": "título atractivo",
      "contenido_es": "contenido completo en varios párrafos separados por \\n\\n",
      "categoria": "IA|Robótica|Biotech|Cybersecurity|Startups|General",
      "keywords": ["palabra1", "palabra2", "palabra3"],
      "image_description_en": "Professional photography prompt in English. Include: subject, lighting, composition, camera specs like 85mm lens, f/1.8, cinematic lighting, photorealistic, 8k"
    }}
    """
    
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={'response_mime_type': 'application/json'}
    )
    
    return json.loads(response.text)

def generate_image(image_prompt):
    """Generar imagen con Imagen 3"""
    gemini_client = initialize_gemini()
    
    try:
        print("Generando imagen...")
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
            print(f"Imagen guardada: {IMAGE_FILE}")
            return True
    except Exception as e:
        print(f"Error generando imagen: {e}")
    
    return False

def main():
    # Cargar configuración
    config = load_config()
    print(f"Configuración cargada: {config['source_name']}")
    
    # Cargar historial
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {'processed_links': [], 'articles': []}
    
    # Determinar método de extracción
    if config.get('use_rss', False) and config.get('rss_url'):
        articles = fetch_news_from_rss(config['rss_url'])
    else:
        articles = fetch_news_from_web(config)
    
    if not articles:
        print("No se encontraron artículos")
        return
    
    # Filtrar artículos ya procesados
    new_articles = [a for a in articles if a['link'] not in history.get('processed_links', [])]
    
    if not new_articles:
        print("No hay noticias nuevas")
        return
    
    print(f"Procesando {len(new_articles)} noticias nuevas")
    
    processed_articles = []
    
    for i, article in enumerate(new_articles[:3]):  # Procesar máximo 3 por ejecución
        print(f"\n[{i+1}/{len(new_articles)}] Procesando: {article['title']}")
        
        # Extraer contenido completo si está configurado
        full_content = extract_full_content(article['link'], config) if config.get('content_extraction', {}).get('extract_full_content', False) else None
        
        # Procesar con IA
        try:
            nueva_noticia = process_with_gemini(
                article['title'],
                article['summary'],
                full_content
            )
            
            # Generar imagen
            image_generated = generate_image(nueva_noticia.get('image_description_en', ''))
            
            # Crear slug único
            slug = nueva_noticia.get('titulo_es', article['title'])[:50].lower().replace(' ', '-').replace(':', '')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')
            
            processed_article = {
                'id': slug,
                'titulo': nueva_noticia['titulo_es'],
                'contenido': nueva_noticia['contenido_es'],
                'categoria': nueva_noticia.get('categoria', 'General'),
                'keywords': nueva_noticia.get('keywords', []),
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'fecha_timestamp': datetime.now().isoformat(),
                'link_original': article['link'],
                'imagen': IMAGE_FILE if image_generated else None,
                'vistas': 0
            }
            
            processed_articles.append(processed_article)
            history['processed_links'].append(article['link'])
            
            # Pausa entre artículos
            if i < len(new_articles) - 1:
                time.sleep(2)
                
        except Exception as e:
            print(f"Error procesando artículo: {e}")
            continue
    
    if not processed_articles:
        print("No se pudo procesar ninguna noticia")
        return
    
    # Actualizar historial
    history['articles'] = processed_articles + history.get('articles', [])
    history['articles'] = history['articles'][:50]  # Mantener últimas 50
    history['processed_links'] = history['processed_links'][-100:]  # Mantener últimos 100 links
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\nHistorial actualizado: {len(history['articles'])} artículos guardados")
    
    # Generar HTML con todas las noticias
    generate_html(history['articles'])

def generate_html(articles):
    """Generar archivo HTML con todas las noticias"""
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Preparar datos de artículos para JavaScript
    articles_json = json.dumps(articles, ensure_ascii=False)
    
    html_content = template.replace("{{ARTICULOS_JSON}}", articles_json)
    html_content = html_content.replace("{{FECHA_ACTUALIZACION}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML generado: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
