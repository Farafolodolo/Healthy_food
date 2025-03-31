from flask import Blueprint, render_template, request, jsonify
import requests
import config
from googletrans import Translator

# A blueprint is a way to declare the endpoints
main_bp = Blueprint("main", __name__)

# It initializes the translator
translator = Translator()

@main_bp.route('/')
def index():
    return render_template('main_page.html')

@main_bp.route('/search_ingredient')
def search_products_amazon():
    PRODUCT = request.args.get('q', default='')

    # It verifies if a product was given
    if PRODUCT:
        url = f"https://api.mercadolibre.com/sites/MLM/search?q={PRODUCT}&category=MLM1403&limit=10"
        headers = {"Authorization": f"Bearer {config.ML_ACCESS_TOKEN}"}
        try:
            print(f"Making request to: {url}")  # depuration: it prints the url
            response = requests.get(url, headers=headers)

            # it verifies if the status is correct
            if response.status_code == 200:
                data = response.json()

                # It stores the information
                results = []
                for product in data.get("results", []):

                    # It translates the title to english
                    translated_title = translator.translate(product.get('title', 'N/A'), src='es', dest='en').text

                    #It creates a dictionary for adding to the results
                    results.append({
                        'title': translated_title,
                        'price': product.get('price', 'N/A'),
                        'seller': product.get('seller', 'N/A').get('nickname'),
                        'link': product.get('permalink', 'N/A') ,
                        'image': product.get('thumbnail', '')
                    })

                # it returns the results
                return jsonify({
                    'status': 'success',
                    'results': results,
                    'total_results': len(results)
                })
            else:
                print(f"Error in the answer: {response.status_code}")  # Depuration
                return jsonify({
                    'status': 'error',
                    'message': f"Error in getting the data. Status code: {response.status_code}"
                }), 500
        except requests.exceptions.RequestException as e:
            # If there is an exception
            print(f"Request error: {str(e)}")  # Depuration
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return jsonify({
        'status': 'error',
        'message': 'A product was not given.'
    }), 400
