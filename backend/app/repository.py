"""
Data access repository layer supporting PostgreSQL with fallback to initial seed cache.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from .database import Session
from .models import Commodity, Mandi, PriceRecord, QueryLog
from ..data.seed_records import COMMODITIES_SEED, MANDIS_SEED, generate_sample_price_records

# In-memory store initialized with seed records
_MEMORY_COMMODITIES = COMMODITIES_SEED
_MEMORY_MANDIS = MANDIS_SEED
_MEMORY_RECORDS = generate_sample_price_records()
_MEMORY_LOGS = []

def get_all_commodities(db: Optional[Session] = None) -> List[Dict[str, Any]]:
    if db:
        try:
            records = db.query(Commodity).all()
            if records:
                return [{"commodity_id": c.commodity_id, "name": c.name, "name_hi": c.name_hi} for c in records]
        except Exception:
            pass
    return [{"commodity_id": i + 1, "name": c["name"], "name_hi": c["name_hi"]} for i, c in enumerate(_MEMORY_COMMODITIES)]


def get_all_mandis(db: Optional[Session] = None) -> List[Dict[str, Any]]:
    if db:
        try:
            records = db.query(Mandi).all()
            if records:
                return [{"mandi_id": m.mandi_id, "name": m.name, "district": m.district, "state": m.state} for m in records]
        except Exception:
            pass
    return [{"mandi_id": i + 1, "name": m["name"], "district": m["district"], "state": m["state"]} for i, m in enumerate(_MEMORY_MANDIS)]


def get_latest_price(commodity: str, mandi: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
    # 1. Try Live Government data.gov.in API
    try:
        from .services.agmarknet_service import get_live_mandi_price_for
        live_rec = get_live_mandi_price_for(commodity, mandi)
        if live_rec:
            return live_rec
    except Exception:
        pass

    # 2. Try PostgreSQL database
    if db:
        try:
            c = db.query(Commodity).filter(Commodity.name.ilike(commodity)).first()
            m = db.query(Mandi).filter(Mandi.name.ilike(mandi)).first()
            if c and m:
                latest = (
                    db.query(PriceRecord)
                    .filter(PriceRecord.commodity_id == c.commodity_id, PriceRecord.mandi_id == m.mandi_id)
                    .order_by(PriceRecord.price_date.desc())
                    .first()
                )
                if latest:
                    return {
                        "commodity": c.name,
                        "mandi": m.name,
                        "price_date": latest.price_date,
                        "min_price": latest.min_price,
                        "max_price": latest.max_price,
                        "modal_price": latest.modal_price,
                        "unit": latest.unit,
                        "source": latest.source
                    }
        except Exception:
            pass

    # Fallback to in-memory records
    matched = [
        r for r in _MEMORY_RECORDS 
        if r["commodity"].lower() == commodity.lower() and r["mandi"].lower() == mandi.lower()
    ]
    if matched:
        sorted_m = sorted(matched, key=lambda x: x["price_date"], reverse=True)
        return sorted_m[0]
    return None


def get_price_history(commodity: str, mandi: str, days: int = 30, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    if db:
        try:
            c = db.query(Commodity).filter(Commodity.name.ilike(commodity)).first()
            m = db.query(Mandi).filter(Mandi.name.ilike(mandi)).first()
            if c and m:
                records = (
                    db.query(PriceRecord)
                    .filter(PriceRecord.commodity_id == c.commodity_id, PriceRecord.mandi_id == m.mandi_id)
                    .order_by(PriceRecord.price_date.desc())
                    .limit(days)
                    .all()
                )
                if records:
                    return [
                        {
                            "price_date": r.price_date,
                            "min_price": r.min_price,
                            "max_price": r.max_price,
                            "modal_price": r.modal_price,
                            "unit": r.unit,
                            "source": r.source
                        }
                        for r in reversed(records)
                    ]
        except Exception:
            pass

    # Fallback to in-memory seed records
    matched = [
        r for r in _MEMORY_RECORDS 
        if r["commodity"].lower() == commodity.lower() and r["mandi"].lower() == mandi.lower()
    ]
    if matched:
        sorted_m = sorted(matched, key=lambda x: x["price_date"])
        return sorted_m[-days:]
    return []


def log_query(query: str, crop: Optional[str], mandi: Optional[str], intent: str, status: str, db: Optional[Session] = None):
    if db:
        try:
            log_entry = QueryLog(
                user_query=query,
                detected_crop=crop,
                detected_mandi=mandi,
                detected_intent=intent,
                status=status
            )
            db.add(log_entry)
            db.commit()
            return
        except Exception:
            pass

    _MEMORY_LOGS.append({
        "query": query,
        "crop": crop,
        "mandi": mandi,
        "intent": intent,
        "status": status
    })
