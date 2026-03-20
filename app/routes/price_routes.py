from flask import Blueprint, jsonify, request
from app.services.market_price_service import get_latest_prices, fetch_and_store_prices

price_routes = Blueprint('price_routes', __name__)

@price_routes.route('/prices', methods=['GET'])
def get_prices_api():
    """
    Returns the latest crop prices from the SQLite database.
    Query params: state, commodity
    """
    state_filter = request.args.get('state')
    commodity_filter = request.args.get('commodity')
    
    try:
        prices = get_latest_prices(state=state_filter, commodity=commodity_filter)
        return jsonify({"success": True, "count": len(prices), "data": prices}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@price_routes.route('/prices/sync', methods=['POST'])
def sync_prices_api():
    """
    Forces a sync from the Government API to the SQLite database.
    """
    try:
        count = fetch_and_store_prices()
        return jsonify({"success": True, "message": f"Successfully synced {count} records."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
