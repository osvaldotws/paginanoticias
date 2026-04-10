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
    user_agent = config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36') if config else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }

def fetch_news_from_rss(rss_url):
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
    news_page_url = config['news_page_url']
    base_url = config['base_url']
    print(f"🕷️ Scrapeando: {news_page_url}")
    try:
        response = requests.get(news_page_url, headers=get_headers(config), timeout=30)
        response.raise_for_status()
        time.sleep(random.uniform(2, 3))
        ai_scraping = config.get('ai_scraping', {})
        if ai_scraping.get('enabled', False):
            print("🤖 Usando AI para extracción...")
            articles = extract_news_with_ai(response.text, base_url, ai_scraping)
            if articles: return articles
        return extract_news_with_selectors(response.text, base_url, config.get('scraping_config', {}))
    except Exception as e:
        print(f"❌ Error al scrapear: {e}")
        return []

def extract_news_with_ai(html_content, base_url, ai_config):
    gemini_client = initialize_gemini()
    instructions = ai_config.get('instructions', 'Extrae las noticias principales.')
    max_articles = ai_config.get('max_articles_to_extract', 5)
    
    # Aumentado para manejar sitios modernos más pesados
    max_html_length = 150000 
    if len(html_content) > max_html_length:
        html_content = html_content[:max_html_length]
    
    prompt = f"Analiza este HTML y extrae {max_articles} noticias. {instructions}\n\nHTML:\n{html_content}\n\nDevuelve JSON: [{{'title':'','link':'','summary':'','published':'','image_url':''}}]"
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        result = json.loads(response.text)
        articles = []
        for item in result:
            link = urljoin(base_url, item.get('link', ''))
            articles.append({
                'title': item.get('title', '').strip(),
                'link': link,
                'summary': item.get('summary', '').strip(),
                'published': item.get('published', ''),
                'image_url': urljoin(base_url, item.get('image_url', '')) if item.get('image_url') else None,
                'full_content': None
            })
        return articles
    except Exception as e:
        print(f"⚠️ Error en AI scraping: {e}")
        return []

def extract_news_with_selectors(html_content, base_url, scraping_config):
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []
    containers = soup.select(scraping_config.get('container_selector', 'article'))
    for container in containers[:5]:
        try:
            title_elem = container.select_one(scraping_config.get('title_selector', 'h2 a'))
            if not title_elem: continue
            title = title_elem.get_text(strip=True)
            link = urljoin(base_url, container.select_one('a')['href'])
            articles.append({
                'title': title, 'link': link, 'summary': title, 'published': '', 'image_url': None, 'full_content': None
            })
        except: continue
    return articles

client = None
def initialize_gemini():
    global client
    if client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key: raise ValueError("❌ GEMINI_API_KEY faltante")
        client = genai.Client(api_key=api_key)
    return client

def process_with_gemini(title, summary, full_content=None):
    gemini_client = initialize_gemini()
    prompt = f"Re-escribe como periodista argentino:\nTítulo: {title}\nResumen: {summary}\nContenido: {full_content if full_content else ''}\n\nDevuelve JSON con: titulo_es, contenido_es, categoria, keywords, image_description_en"
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except:
        return {"titulo_es": title, "contenido_es": summary, "categoria": "General", "keywords": [], "image_description_en": ""}

def generate_image(image_prompt):
    gemini_client = initialize_gemini()
    try:
        response = gemini_client.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=image_prompt,
            config=types.GenerateImageConfig(aspect_ratio="16:9", output_mime_type="image/png")
        )
        if response.generated_images:
            response.generated_images[0].image.save(IMAGE_FILE)
            return True
    except: return False
    return False

def main():
    config = load_config()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {'processed_links': [], 'articles': []}

    articles = fetch_news_from_rss(config['rss_url']) if config.get('use_rss') else fetch_news_from_web(config)
    if not articles:
        generate_html(history.get('articles', []))
        return

    new_articles = [a for a in articles if a['link'] not in history['processed_links']][:3]
    for i, article in enumerate(new_articles):
        try:
            nueva = process_with_gemini(article['title'], article['summary'])
            img_ok = generate_image(nueva.get('image_description_en', ''))
            
            # Mapeo de campos corregido para template.html
            processed = {
                'id': f"news-{int(time.time())}-{i}",
                'titulo': nueva['titulo_es'],
                'contenido': nueva['contenido_es'],
                'resumen': article['summary'][:200],
                'categoria': nueva.get('categoria', 'General'),
                'palabras_clave': nueva.get('keywords', []),
                'fecha_formateada': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'fecha_timestamp': datetime.now().isoformat(),
                'fuente_original': article['link'],
                'imagen': IMAGE_FILE if img_ok else article.get('image_url'),
                'destacada': (i == 0),
                'vistas': random.randint(10, 50)
            }
            history['articles'].insert(0, processed)
            history['processed_links'].append(article['link'])
        except Exception as e: print(f"Error: {e}")

    history['articles'] = history['articles'][:50]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    generate_html(history['articles'])

def generate_html(articles):
    """Generar archivo HTML con estructura compatible"""
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Crear objeto que espera el JavaScript del template
        data_for_ui = {
            "news": articles,
            "categories": {a['categoria']: True for a in articles}
        }
        
        html_content = template.replace("{{NEWS_DATA}}", json.dumps(data_for_ui, ensure_ascii=False))
        html_content = html_content.replace("{{FECHA_ACTUALIZACION}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Sitio generado con {len(articles)} noticias")
    except Exception as e: print(f"❌ Error HTML: {e}")

if __name__ == "__main__":
    main()
