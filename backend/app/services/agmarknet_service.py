import json
import urllib.request
import urllib.parse
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..config import settings

logger = logging.getLogger("agmarknet_service")

# In-memory cache to respect API rate limits
_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_EXPIRY_SECONDS = 1800  # 30 minutes


def fetch_live_mandi_prices(commodity: str, state: str = "Uttar Pradesh") -> List[Dict[str, Any]]:
    """
    Fetches real-time commodity mandi prices from data.gov.in official API.
    """
    cache_key = f"{commodity}_{state}"
    now = datetime.utcnow().timestamp()

    if cache_key in _CACHE:
        cached = _CACHE[cache_key]
        if now - cached["timestamp"] < _CACHE_EXPIRY_SECONDS:
            return cached["data"]

    api_key = settings.DATAGOV_API_KEY
    resource_id = settings.DATAGOV_RESOURCE_ID

    if not api_key:
        logger.warning("No data.gov.in API key configured.")
        return []

    # Map canonical to API commodity spelling
    commodity_clean = commodity.strip().title()
    if commodity_clean in ["Tomatoes", "Tamatar"]:
        commodity_clean = "Tomato"
    elif commodity_clean in ["Potatoes", "Aloo", "Alu"]:
        commodity_clean = "Potato"
    elif commodity_clean in ["Onions", "Pyaz", "Pyaaz"]:
        commodity_clean = "Onion"

    base_url = f"https://api.data.gov.in/resource/{resource_id}"
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": 50,
        "filters[state.keyword]": state,
        "filters[commodity.keyword]": commodity_clean
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "MandiBhavBot/1.0 (MinistryOfAgri-Client)"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                raw_data = json.loads(response.read().decode("utf-8"))
                records = raw_data.get("records", [])
                
                parsed_records = []
                for r in records:
                    try:
                        modal_p = float(r.get("modal_price", 0))
                        min_p = float(r.get("min_price", modal_p))
                        max_p = float(r.get("max_price", modal_p))
                        
                        arrival_raw = r.get("arrival_date", "")
                        # Parse DD/MM/YYYY to YYYY-MM-DD
                        if "/" in arrival_raw:
                            parts = arrival_raw.split("/")
                            if len(parts) == 3:
                                arrival_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                            else:
                                arrival_date = arrival_raw
                        else:
                            arrival_date = arrival_raw

                        parsed_records.append({
                            "state": r.get("state"),
                            "district": r.get("district"),
                            "market": r.get("market"),
                            "commodity": r.get("commodity"),
                            "arrival_date": arrival_date,
                            "min_price": min_p,
                            "max_price": max_p,
                            "modal_price": modal_p,
                            "unit": "₹/Quintal",
                            "source": "Agmarknet (data.gov.in Live Official)"
                        })
                    except (ValueError, TypeError):
                        continue

                _CACHE[cache_key] = {"timestamp": now, "data": parsed_records}
                logger.info(f"Fetched {len(parsed_records)} live records from data.gov.in for {commodity}")
                return parsed_records
    except Exception as e:
        logger.error(f"Error fetching from data.gov.in: {e}")

    return []


def get_live_mandi_price_for(commodity: str, mandi: str = "Lucknow") -> Optional[Dict[str, Any]]:
    """
    Returns live price for target mandi, or closest reporting UP market today.
    """
    records = fetch_live_mandi_prices(commodity, state="Uttar Pradesh")
    if not records:
        return None

    mandi_clean = mandi.strip().lower()

    # 1. Exact match on market name (e.g. Lucknow APMC)
    for r in records:
        market_name = r.get("market", "").lower()
        district_name = r.get("district", "").lower()
        if mandi_clean in market_name or mandi_clean in district_name:
            return {
                "commodity": commodity,
                "mandi": r.get("market", mandi),
                "price_date": r["arrival_date"],
                "min_price": r["min_price"],
                "max_price": r["max_price"],
                "modal_price": r["modal_price"],
                "unit": "₹/Quintal",
                "source": "Agmarknet (data.gov.in Live Official)",
                "live": True,
                "note": "Live official price reported today."
            }

    # 2. If Lucknow hasn't uploaded today yet, return primary UP benchmark market with transparent note
    top_record = records[0]
    return {
        "commodity": commodity,
        "mandi": f"{mandi} (Ref: {top_record.get('market')})",
        "price_date": top_record["arrival_date"],
        "min_price": top_record["min_price"],
        "max_price": top_record["max_price"],
        "modal_price": top_record["modal_price"],
        "unit": "₹/Quintal",
        "source": "Agmarknet (data.gov.in Live Official)",
        "live": True,
        "note": f"Live state benchmark from {top_record.get('market')} ({top_record.get('district')})."
    }
