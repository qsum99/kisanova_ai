from flask import Blueprint, jsonify, request
from app.services.market_price_service import get_latest_prices, fetch_and_store_prices, get_top_crops

price_routes = Blueprint('price_routes', __name__)

@price_routes.route('/prices', methods=['GET'])
def get_prices_api():
    state_filter = request.args.get('state')
    commodity_filter = request.args.get('commodity')
    
    try:
        prices = get_latest_prices(state=state_filter, commodity=commodity_filter)
        return jsonify({"success": True, "count": len(prices), "data": prices}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@price_routes.route('/prices/sync', methods=['POST'])
def sync_prices_api():
    try:
        count = fetch_and_store_prices()
        return jsonify({"success": True, "message": f"Successfully synced {count} records."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@price_routes.route('/prices/top', methods=['GET'])
def top_crops_api():
    limit = request.args.get('limit', 30, type=int)
    try:
        crops = get_top_crops(limit=limit)
        return jsonify({"success": True, "count": len(crops), "data": crops}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
