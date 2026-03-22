from typing import List, Tuple, Dict, Any
from app.services.market_price_service import get_latest_prices

def calculate_profitable_crops(crop_yields: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
    """
    Combines the ML predicted yield with real market prices.
    Returns the final ranked list of crops optimized for Profit (Revenue/Ha).
    """
    # 1. Fetch current market prices
    market_data = get_latest_prices()
    
    price_map = {}
    for entry in market_data:
        crop_name = str(entry.get("commodity", "")).lower().strip()
        price = float(entry.get("modal_price", 0.0))
        # Since state/district might give multiple entries per crop, we'll keep the highest or average
        if crop_name in price_map:
            price_map[crop_name] = max(price_map[crop_name], price)
        else:
            price_map[crop_name] = price
            
            
    valid_prices = [p for p in price_map.values() if p > 0]
    avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 1000.0
    
    final_rankings = []
    
    for crop, predicted_yield in crop_yields:
        crop_clean = crop.lower().strip()
        
        # If model yield is 0, skip
        if predicted_yield <= 0:
            continue
            
        market_price = price_map.get(crop_clean, avg_price)
        
        # Revenue/Profit Score = Expected Yield * Expected Price
        profit_score = predicted_yield * market_price
        
        final_rankings.append({
            "crop": crop.capitalize(),
            "predicted_yield": round(predicted_yield, 2),
            "expected_market_price": round(market_price, 2),
            "profitability_index": round(profit_score, 2)
        })
        
    # Sort purely by profitability index descending
    final_rankings.sort(key=lambda x: x["profitability_index"], reverse=True)
    
    return final_rankings
