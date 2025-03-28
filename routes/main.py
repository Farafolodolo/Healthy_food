from flask import Blueprint, render_template, request, jsonify
import requests
#A blueprint is a way to declarate the endpoints
main_bp = Blueprint("main", __name__)

RAIN_FOREST_KEY = ""

@main_bp.route('/')
def index():
    return render_template('main_page.html')

@main_bp.route('/search_products_amazon')
def search_products_amazon():
    search = request.args.get('q',default='')
    domain = 'amazon.com'
    page = request.args.get('page', default=1,type=int)

    if search:
        params_search = {
            "api_key": RAIN_FOREST_KEY,
            "type": "search",
            "amazon_domain": domain,
            "search_term": search,
            "page": page
        }
    try:
        response = requests.get(response = requests.get('https://api.rainforestapi.com/request', params=params_search))
        response.raise_for_status()

        data = response.json()

        results = []

        if 'search_results' in data:
            for product in data['search_results']:
                results.append({
                    'title': product.get('title'),
                    'price': product.get('price', {}).get('value'),
                    'type': product.get('price', {}).get('currency'),
                    'url': product.get('link'),
                    'imagen': product.get('image')
                })

        return jsonify({
            'status': 'success',
            'results': results,
            'total_resultados': len(results)
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
