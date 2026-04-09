#!/usr/bin/env python3
"""
Generador del sitio web estático
Combina los datos de noticias (JSON) con la plantilla HTML para producir index.html
"""

import json
import os
from pathlib import Path

TEMPLATE_FILE = "template.html"
NEWS_FILE = "data/news.json"
OUTPUT_FILE = "index.html"

def generate_site():
    """Genera el archivo index.html combinando template y datos"""
    
    # Cargar datos de noticias
    if not os.path.exists(NEWS_FILE):
        print("⚠️ No se encontró el archivo de noticias. Ejecuta script_advanced.py primero.")
        news_data = {"news": [], "categories": {}, "total_views": 0}
    else:
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    
    # Cargar plantilla
    if not os.path.exists(TEMPLATE_FILE):
        print("❌ No se encontró la plantilla template.html")
        return
    
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Convertir datos a JSON string para insertar en JavaScript
    news_json = json.dumps(news_data, ensure_ascii=False, indent=2)
    
    # Reemplazar placeholder con datos reales
    html_content = template.replace('{{NEWS_DATA}}', news_json)
    
    # Guardar archivo final
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Sitio web generado exitosamente: {OUTPUT_FILE}")
    print(f"📰 Total de noticias: {len(news_data.get('news', []))}")
    print(f"📂 Categorías: {len(news_data.get('categories', {}))}")

if __name__ == "__main__":
    generate_site()
