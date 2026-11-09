from fastapi import APIRouter, Depends
from ..database import get_db, Session
from ..schemas import QueryRequest, QueryResponse, LatestPriceResponse, PriceHistoryResponse, ForecastResponse
from ..nlp.parser import parse_query
from ..repository import log_query
from .prices import get_latest, get_history
from .forecast import get_crop_forecast

router = APIRouter(prefix="", tags=["NLP Query"])

@router.post("/query", response_model=QueryResponse)
def handle_natural_query(payload: QueryRequest, db: Session = Depends(get_db)):
    parsed = parse_query(payload.query)
    commodity = parsed["commodity"]
    mandi = parsed["mandi"]
    intent = parsed["intent"]

    if not commodity:
        log_query(payload.query, None, mandi, intent, "missing_commodity", db)
        return QueryResponse(
            query=payload.query,
            detected_commodity=None,
            detected_mandi=mandi,
            detected_intent=intent,
            success=False,
            message="Could not identify the crop in your query. Supported crops are Tomato, Potato, and Onion."
        )

    if not mandi:
        log_query(payload.query, commodity, None, intent, "missing_mandi", db)
        return QueryResponse(
            query=payload.query,
            detected_commodity=commodity,
            detected_mandi=None,
            detected_intent=intent,
            success=False,
            message=f"Identified crop '{commodity}', but please specify a mandi (e.g. Lucknow, Kanpur, Agra)."
        )

    # Fetch corresponding data
    latest = get_latest(commodity=commodity, mandi=mandi, db=db)
    history = get_history(commodity=commodity, mandi=mandi, days=7, db=db)
    forecast = get_crop_forecast(commodity=commodity, mandi=mandi, days=7, db=db)

    log_query(payload.query, commodity, mandi, intent, "success", db)

    return QueryResponse(
        query=payload.query,
        detected_commodity=commodity,
        detected_mandi=mandi,
        detected_intent=intent,
        success=True,
        message=f"Results for {commodity} in {mandi} Mandi ({intent.replace('_', ' ').title()}).",
        latest_price=latest,
        history=history,
        forecast=forecast
    )
