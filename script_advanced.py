import os
import json
import feedparser
import requests
from google import genai
from google.genai import types
from datetime import datetime

# Configuración técnica
RSS_URL = "https://www.technologyreview.com/feed/"
HISTORY_FILE = "news_history.json"
TEMPLATE_FILE = "template.html"
OUTPUT_FILE = "index.html"
IMAGE_FILE = "latest_image.png"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def process_content_and_image_prompt(title, summary):
    # Generación de contenido y Prompt para la imagen (en inglés técnico)
    prompt_texto = f"""
    Actúa como un editor senior. Re-escribe esta noticia:
    Título: {title}
    Resumen: {summary}
    
    Salida en JSON:
    {{
      "titulo_es": "título atractivo",
      "contenido_es": "3 párrafos profesionales",
      "image_description_en": "A highly technical image prompt in English for this news. Include: cinematic lighting, volumetric atmosphere, 85mm lens, f/1.8, photorealistic, sharp focus, 8k resolution, technical keywords."
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt_texto,
        config={'response_mime_type': 'application/json'}
    )
    return json.loads(response.text)

def generate_image(image_prompt):
    # Generación de imagen con Imagen 3
    response = client.models.generate_image(
        model="imagen-3.0-generate-001",
        prompt=image_prompt,
        config=types.GenerateImageConfig(
            aspect_ratio="16:9",
            output_mime_type="image/png"
        )
    )
    # Guardar los bytes de la imagen
    response.generated_images[0].image.save(IMAGE_FILE)

def main():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []

    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("No se encontraron entradas en el feed RSS.")
        return
    
    latest_entry = feed.entries[0]
    if latest_entry.link in history:
        print("Sin novedades.")
        return

    # Procesamiento
    print(f"Procesando: {latest_entry.title}")
    data = process_content_and_image_prompt(latest_entry.title, latest_entry.summary)
    print("Generando imagen...")
    generate_image(data['image_description_en'])
    
    # Persistencia
    history.append(latest_entry.link)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-50:], f)

    # Inyección en HTML
    with open(TEMPLATE_FILE, 'r') as f:
        template = f.read()
    
    html = template.replace("{{TITULO}}", data['titulo_es'])
    html = html.replace("{{CONTENIDO}}", data['contenido_es'].replace("\n", "<br>"))
    html = html.replace("{{FECHA}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
    html = html.replace("{{IMAGEN}}", IMAGE_FILE)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    
    print(f"Noticia publicada exitosamente: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
