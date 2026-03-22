from typing import List, Tuple, Dict, Any
from app.services.market_price_service import get_latest_prices, CROP_ALIASES

def calculate_profitable_crops(crop_yields: List[Tuple[str, float]]) -> List[Dict[str, Any]]:

    market_data = get_latest_prices()
    
    price_map = {}
    for entry in market_data:
        crop_name = str(entry.get("commodity", "")).lower().strip()
        price = float(entry.get("modal_price", 0.0))
        
        if crop_name in price_map:
            price_map[crop_name] = max(price_map[crop_name], price)
        else:
            price_map[crop_name] = price
            
            
    valid_prices = [p for p in price_map.values() if p > 0]
    avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 1000.0
    
    final_rankings = []
    
    for crop, predicted_yield in crop_yields:
        crop_clean = crop.lower().strip()
        
        
        if predicted_yield <= 0:
            continue
            
        market_price = avg_price
        aliases = CROP_ALIASES.get(crop_clean, [crop_clean])
        for alias in aliases:
            matches = [price for key, price in price_map.items() if alias in key.lower()]
            if matches:
                # Average if multiple variants match (e.g. Rice(Common) and Rice(Grade A))
                market_price = sum(matches) / len(matches)
                break
        
        
        profit_score = predicted_yield * market_price
        
        final_rankings.append({
            "crop": crop.capitalize(),
            "predicted_yield": round(predicted_yield, 2),
            "expected_market_price": round(market_price, 2),
            "profitability_index": round(profit_score, 2)
        })
        
   
   
    final_rankings.sort(key=lambda x: x["profitability_index"], reverse=True)
    
    return final_rankings
