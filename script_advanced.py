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
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "source_name": "El Ancasti",
            "base_url": "https://www.elancasti.com.ar",
            "news_page_url": "https://www.elancasti.com.ar/",
            "use_rss": False,
            "ai_scraping": {"enabled": True, "instructions": "Extrae las noticias principales.", "max_articles_to_extract": 5}
        }

def initialize_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY no configurada en los Secrets de GitHub")
    return genai.Client(api_key=api_key)

def fetch_news(config):
    url = config['news_page_url']
    print(f"🕷️ Scrapeando: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        client = initialize_gemini()
        # Aumentamos el límite de HTML para capturar más contenido
        html_segment = response.text[:150000]
        
        prompt = f"Analiza este HTML y extrae las 5 noticias más importantes en formato JSON: [{{'title':'','link':'','summary':''}}]. URL base: {config['base_url']}\n\nHTML:\n{html_segment}"
        
        ai_resp = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(ai_resp.text)
    except Exception as e:
        print(f"❌ Error en scraping: {e}")
        return []

def process_article(article):
    client = initialize_gemini()
    prompt = f"Re-escribe esta noticia para un portal tecnológico en español latino:\n{article['title']}\n{article['summary']}\n\nDevuelve JSON: {{'titulo_es':'','contenido_es':'','categoria':'','keywords':[],'image_prompt':''}}"
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        data = json.loads(resp.text)
        
        return {
            "id": f"news_{int(time.time())}_{random.randint(100,999)}",
            "titulo": data['titulo_es'],
            "contenido": data['contenido_es'],
            "resumen": article['summary'][:200],
            "categoria": data.get('categoria', 'Tecnología'),
            "palabras_clave": data.get('keywords', []),
            "fecha_formateada": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fuente_original": article['link'],
            "imagen": article.get('image_url', ''),
            "destacada": False,
            "vistas": random.randint(50, 500)
        }
    except: return None

def main():
    config = load_config()
    raw_news = fetch_news(config)
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {"processed_links": [], "articles": []}

    new_articles = []
    for item in raw_news[:3]: # Procesamos 3 para no tardar mucho
        link = urljoin(config['base_url'], item['link'])
        if link not in history['processed_links']:
            processed = process_article(item)
            if processed:
                processed['fuente_original'] = link
                new_articles.append(processed)
                history['processed_links'].append(link)

    # El primero de la lista es destacado
    if new_articles:
        new_articles[0]['destacada'] = True
        history['articles'] = new_articles + history['articles']
    
    history['articles'] = history['articles'][:50] # Mantener solo 50
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # Generar HTML con la estructura que espera template.html
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # IMPORTANTE: El template espera data.news y data.categories
    categories = list(set(a['categoria'] for a in history['articles']))
    news_data = {
        "news": history['articles'],
        "categories": {cat: True for cat in categories}
    }
    
    final_html = template.replace("{{NEWS_DATA}}", json.dumps(news_data, ensure_ascii=False))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("✅ Proceso completado exitosamente.")

if __name__ == "__main__":
    main()
