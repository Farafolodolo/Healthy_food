from flask import Blueprint, render_template, request, jsonify
import requests
import config
import re
from googletrans import Translator

main_bp = Blueprint("main", __name__)
translator = Translator()

# Function to clean and normalize ingredient descriptions
def clean_ingredient(ingredient):
    tokens = re.findall(r'\b[\w/-]+\b', ingredient)
    
    # Create a set of measurement units and irrelevant words to remove
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
    # Process each token found by regex
    for token in tokens:
        # Remove non-word characters from start/end of token
        cleaned_token = re.sub(r'^[^\w/-]+|[^\w/-]+$', '', token)
        
        # Skip empty tokens
        if not cleaned_token:
            continue
        # Skip tokens starting with numbers or fractions
        if re.match(r'^[\d½¾¼⅓⅔]|[\d½¾¼⅓⅔]\D', cleaned_token):
            continue
        # Skip tokens in our removal list
        if cleaned_token.lower() in words_to_remove:
            continue
        # Add cleaned token to filtered list
        filtered_tokens.append(cleaned_token.lower())
    # Return cleaned string or original if no tokens remain
    return ' '.join(filtered_tokens) if filtered_tokens else ingredient.lower()

@main_bp.route('/')
def index():
    return render_template('main_page.html')

@main_bp.route('/test')
def test():
    return render_template('test.html')    
# Route to fetch recipes from external API
@main_bp.route('/get_recipes')
def get_recipes():
    # Get query parameters from URL
    query = request.args.get('q', default='Pasta')
    page = request.args.get('page', '0')
    # Validate required parameter
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    # Prepare API request parameters
    url = "https://tasty.p.rapidapi.com/recipes/list"
    params = {"q": query, "from": page, "size": "8"}
    headers = {
        "X-RapidAPI-Key": config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": config.RAPIDAPI_HOST
    }

    try:
        # Make API call
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            recipes = []
            
            # Process each recipe in response
            for recipe in data.get('results', []):
                ingredients = []
                # Extract and clean ingredients from recipe components
                for section in recipe.get('sections', []):
                    for component in section.get('components', []):
                        raw_ing = component.get('raw_text', '')
                        clean_ing = clean_ingredient(raw_ing)
                        if clean_ing:
                            ingredients.append(clean_ing)
                
                # Build recipe data structure
                recipes.append({
                    'id': recipe.get('id'),
                    'name': recipe.get('name'),
                    'cook_time': recipe.get('cook_time_minutes'),
                    'servings': recipe.get('num_servings'),
                    'categories': [tag['name'] for tag in recipe.get('tags', [])],
                    'image_url': recipe.get('thumbnail_url'),
                    'video_url': recipe.get('original_video_url'),
                    'ingredients': ingredients,
                    'instructions': [step['display_text'] for step in recipe.get('instructions', [])]
                })
            # Return successful response
            return jsonify({'status': 'success', 'recipes': recipes})
        # Handle API errors
        return jsonify({'error': 'Failed to fetch recipes'}), response.status_code
    
    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': str(e)}), 500

# Route to find ingredient substitutes
@main_bp.route('/get_substitutes')
def get_substitutes():
    # Get ingredient from query parameters
    ingredient = request.args.get('ingredient', '')
    if not ingredient:
        return jsonify({'error': 'Missing ingredient parameter'}), 400
    # Clean ingredient name
    clean_ing = clean_ingredient(ingredient)
    # Prepare Spoonacular API request
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
        # Handle API errors
        return jsonify({'error': 'Failed to fetch substitutes'}), response.status_code
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to search Amazon products
@main_bp.route('/search_ingredient')
def search_products_amazon():
    # Get product query parameter
    product = request.args.get('q', '')
    if not product:
        return jsonify({'error': 'Missing product parameter'}), 400
    # Clean product name
    clean_product = clean_ingredient(product)
    # Prepare Amazon API request
    url = "https://realtime-amazon-data.p.rapidapi.com/product-search"
    headers = {
        "X-RapidAPI-Host": "realtime-amazon-data.p.rapidapi.com",
        "X-RapidAPI-Key": config.RAPIDAPI_KEY  # Asegúrate de añadir esta variable a tu config
    }
    
    querystring = {
        "keyword": clean_product,
        "country": "us",
        "page": "1",
        "sort": "Featured"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Amazon API Response ({response.status_code}):", response.text)  # Depuration
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') != 'success':
                return jsonify({'error': 'API returned error', 'details': data}), 500
            # Process product results
            products = []
            for item in data.get('details', []):
                products.append({
                    'title': item.get('ProductTitle'),
                    'price': item.get('price'),
                    'originalPrice': item.get('originalPrice'),
                    'rating': item.get('rating'),
                    'link': item.get('productUrl'),
                    'image': item.get('productImage'),
                    'isPrime': item.get('isPrime'),
                    'asin': item.get('asin'),
                    'totalRatings': item.get('totalRatings')
                })
            # Return formatted results
            return jsonify({
                'status': 'success',
                'totalResults': data.get('totalResultsCount'),
                'currency': data.get('currency'),
                'results': products
            })
            
        return jsonify({'error': 'Failed to search products', 'details': response.text}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Route to get detailed recipe information
@main_bp.route('/specific_recipe/<int:id>')
def specific_recipe(id):
    # Prepare API request for detailed recipe
    url = "https://tasty.p.rapidapi.com/recipes/get-more-info"
    # It calls the API by ID
    params = {
        "id": id
    }
    
    #The headers necessary
    headers = {
        "X-RapidAPI-Key": config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": config.RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            recipe_data = response.json()  
            
            # Verify if the recipe it's got
            if not recipe_data.get('name'):
                return render_template('recipe_not_found.html'), 404

            # Process the ingredients and save it on an array
            ingredients = []
            for section in recipe_data.get('sections', []):
                for component in section.get('components', []):
                    raw_ing = component.get('raw_text', '')
                    clean_ing = clean_ingredient(raw_ing)
                    if clean_ing:
                        ingredients.append(clean_ing)
            #It saves all the information on a dictionary
            formatted_recipe = {
                'id': recipe_data['id'],
                'name': recipe_data['name'],
                'cook_time': recipe_data.get('cook_time_minutes'),
                'servings': recipe_data.get('num_servings'),
                'categories': [tag['name'] for tag in recipe_data.get('tags', [])],
                'image_url': recipe_data.get('thumbnail_url'),
                'video_url': recipe_data.get('original_video_url'),
                'ingredients': ingredients,
                'instructions': [step['display_text'] for step in recipe_data.get('instructions', [])],
                'yields': recipe_data.get('yields'),
                'total_time': recipe_data.get('total_time_minutes'),
                'user_ratings': recipe_data.get('user_ratings', {})
            }
            
            return render_template('test.html', recipe=formatted_recipe)
            
        return render_template('recipe_not_found.html'), response.status_code
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        return render_template('api_error.html'), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('error.html'), 500