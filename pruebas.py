import asyncio
import requests
from googletrans import Translator

# Función asíncrona para traducir un título
async def translate_title(translator, title):
    translated = await translator.translate(title, src='de', dest='es')
    return translated.text

async def main():
    # Configuración de la URL, parámetros y headers para la API de gustar.io
    url = "https://gustar-io-deutsche-rezepte.p.rapidapi.com/search_api"
    params = {"text": "a"}
    headers = {
        "x-rapidapi-host": "gustar-io-deutsche-rezepte.p.rapidapi.com",
        "x-rapidapi-key": "e3b46062d9mshd6f2268d8c67c88p19446bjsn69418f3b4a5b"  # Reemplaza con tu API key real
    }

    # Realiza la solicitud GET
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # La respuesta es una lista de recetas
        recipes = response.json()
        
        # Inicializa el traductor
        translator = Translator()

        # Crea una lista de tareas para traducir los títulos de forma asíncrona
        tasks = []
        for recipe in recipes:
            title_de = recipe.get("title", "")
            ingredientes = recipe.get("ingredients", "")
            if title_de:
                tasks.append(translate_title(translator, title_de))
            else:
                tasks.append(asyncio.sleep(0, result=""))
        
        # Ejecuta todas las tareas asíncronamente y espera sus resultados
        translated_titles = await asyncio.gather(*tasks)
        
        # Agrega el título traducido a cada receta
        for recipe, title_es in zip(recipes, translated_titles):
            recipe["title_es"] = title_es
        
        # Imprime los títulos originales y traducidos
        for recipe in recipes:
            print(f"Alemán: {recipe.get('title', '')}")
            print(f"Español: {recipe.get('title_es', '')}\n")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Ejecuta la función principal asíncrona
asyncio.run(main())
