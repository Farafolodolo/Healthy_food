from flask import Blueprint, render_template, request, jsonify
import requests
import config
import re
from googletrans import Translator

main_bp = Blueprint("main", __name__)
translator = Translator()

def clean_ingredient(ingredient):
    tokens = re.findall(r'\b[\w/-]+\b', ingredient)
    
    words_to_remove = {
        "cup", "cups", "tablespoon", "tablespoons", "teaspoon", "teaspoons",
        "cloves", "divided", "minced", "shredded", "chopped", "fresh", "grated",
        "unsalted", "salted", "ounce", "ounces", "pound", "lb", "lbs", "halved",
        "plus", "to", "taste", "n/a", "grams", "gram", "g", "kg", "kilogram",
        "ml", "milliliter", "tbsp", "tsp", "oz", "package", "can", "bunch", 
        "pinch", "dash", "slice", "whole", "diced", "sliced", "crushed", "cooked",
        "raw", "dry", "ground", "stalk", "large", "medium", "small", "clove",
        "extra", "virgin", "more", "optional", "inch", "pieces", "splash", "jar",
        "bottle", "carton", "lean", "about", "as", "needed", "for", "or", "and",
        "of", "a", "an", "the", "with", "into", "from", "by", "on", "in", "at",
        "preferably", "cut", "warm", "cold", "softened", "melted", "cooled",
        "finely", "coarsely", "thinly", "peeled", "seeded", "pitted", "cored",
        "trimmed", "drained", "blanched", "roasted", "mashed", "beaten", "divided",
        "according", "instructions", "recipe", "required", "de", "al", "en", "la",
        "para", "y", "con", "sin", "del", "freshly", "thick", "packed", "any"
        "cup", "cups", "tablespoon", "tablespoons", "teaspoon", "teaspoons",
        "clove", "cloves", "divided", "minced", "shredded", "chopped", "fresh",
        "unsalted", "salted", "ounce", "ounces", "pound", "lb", "lbs", "halved",
        "plus", "to", "taste", "n/a", "of", "and", "with", "for", "a", "an",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", ",", ".", "/"
    }

    filtered_tokens = []
    for token in tokens:
        cleaned_token = re.sub(r'^[^\w/-]+|[^\w/-]+$', '', token)
        
        if not cleaned_token:
            continue
            
        if re.match(r'^[\d½¾¼⅓⅔]|[\d½¾¼⅓⅔]\D', cleaned_token):
            continue
            
        if cleaned_token.lower() in words_to_remove:
            continue
            
        filtered_tokens.append(cleaned_token.lower())
    
    return ' '.join(filtered_tokens) if filtered_tokens else ingredient.lower()

@main_bp.route('/')
def index():
    return render_template('main_page.html')

@main_bp.route('/test')
def test():
    return render_template('test.html')
@main_bp.route('/get_recipes')
def get_recipes():
    query = request.args.get('q', '')
    page = request.args.get('page', '0')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    url = "https://tasty.p.rapidapi.com/recipes/list"
    params = {"q": query, "from": page, "size": "5"}
    headers = {
        "X-RapidAPI-Key": config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": config.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            recipes = []
            
            for recipe in data.get('results', []):
                ingredients = []
                for section in recipe.get('sections', []):
                    for component in section.get('components', []):
                        raw_ing = component.get('raw_text', '')
                        clean_ing = clean_ingredient(raw_ing)
                        if clean_ing:
                            ingredients.append(clean_ing)
                
                recipes.append({
                    'name': recipe.get('name'),
                    'cook_time': recipe.get('cook_time_minutes'),
                    'servings': recipe.get('num_servings'),
                    'categories': [tag['name'] for tag in recipe.get('tags', [])],
                    'video_url': recipe.get('original_video_url'),
                    'ingredients': ingredients,
                    'instructions': [step['display_text'] for step in recipe.get('instructions', [])]
                })
            
            return jsonify({'status': 'success', 'recipes': recipes})
        
        return jsonify({'error': 'Failed to fetch recipes'}), response.status_code
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/get_substitutes')
def get_substitutes():
    ingredient = request.args.get('ingredient', '')
    if not ingredient:
        return jsonify({'error': 'Missing ingredient parameter'}), 400
    
    clean_ing = clean_ingredient(ingredient)
    
    url = "https://api.spoonacular.com/food/ingredients/substitutes"
    params = {"apiKey": config.SPOONACULAR_API_KEY, "ingredientName": clean_ing}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'ingredient': clean_ing,
                'substitutes': data.get('substitutes', []),
                'message': data.get('message', '')
            })
        
        return jsonify({'error': 'Failed to fetch substitutes'}), response.status_code
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/search_ingredient')
def search_products_amazon():
    product = request.args.get('q', '')
    if not product:
        return jsonify({'error': 'Missing product parameter'}), 400
    
    clean_product = clean_ingredient(product)
    
    url = f"https://api.mercadolibre.com/sites/MLM/search?q={clean_product}&category=MLM1403&limit=10"
    headers = {"Authorization": f"Bearer {config.ML_ACCESS_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            products = []
            for item in response.json().get('results', []):
                translated_title = translator.translate(
                    item.get('title', ''),
                    src='es',
                    dest='en'
                ).text
                
                products.append({
                    'title': translated_title,
                    'price': item.get('price'),
                    'seller': item.get('seller', {}).get('nickname'),
                    'link': item.get('permalink'),
                    'image': item.get('thumbnail')
                })
            
            return jsonify({'status': 'success', 'results': products})
        
        return jsonify({'error': 'Failed to search products'}), response.status_code
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500