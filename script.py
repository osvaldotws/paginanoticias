import os
import json
import feedparser
from google import genai
from datetime import datetime

# Configuración
RSS_URL = "https://www.technologyreview.com/feed/"
HISTORY_FILE = "news_history.json"
TEMPLATE_FILE = "template.html"
OUTPUT_FILE = "index.html"

def process_with_gemini(title, summary):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = f"""
    Actúa como un periodista experto. Re-escribe la siguiente noticia para un blog de tecnología.
    Título original: {title}
    Resumen: {summary}
    
    Instrucciones:
    1. Crea un título llamativo en español.
    2. Escribe un cuerpo de 3 párrafos con tono profesional y analítico.
    3. Devuelve el resultado en formato JSON estrictamente: 
       {{"titulo_es": "...", "contenido_es": "..."}}
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={'response_mime_type': 'application/json'}
    )
    return json.loads(response.text)

def main():
    # 1. Cargar historial
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []

    # 2. Leer RSS
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("No se encontraron entradas en el feed RSS.")
        return
    
    latest_entry = feed.entries[0]
    
    if latest_entry.link in history:
        print("No hay noticias nuevas.")
        return

    # 3. Procesar con IA
    print(f"Procesando: {latest_entry.title}")
    nueva_noticia = process_with_gemini(latest_entry.title, latest_entry.summary)
    
    # 4. Actualizar historial
    history.append(latest_entry.link)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-50:], f) # Guardamos solo las últimas 50

    # 5. Generar HTML (inyectar en el template)
    with open(TEMPLATE_FILE, 'r') as f:
        template = f.read()
    
    html_content = template.replace("{{TITULO}}", nueva_noticia['titulo_es'])
    html_content = html_content.replace("{{CONTENIDO}}", nueva_noticia['contenido_es'].replace("\n", "<br>"))
    html_content = html_content.replace("{{FECHA}}", datetime.now().strftime("%Y-%m-%d %H:%M"))

    with open(OUTPUT_FILE, 'w') as f:
        f.write(html_content)
    
    print(f"Noticia publicada exitosamente: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
