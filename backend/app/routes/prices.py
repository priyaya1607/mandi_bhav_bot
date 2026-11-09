from fastapi import APIRouter, Query, Depends
from ..database import get_db, Session
from ..schemas import LatestPriceResponse, PriceHistoryResponse, PriceRecordItem
from ..repository import get_latest_price, get_price_history
from ..forecasting.model import calculate_trend

router = APIRouter(prefix="/prices", tags=["Prices"])

@router.get("/latest", response_model=LatestPriceResponse)
def get_latest(
    commodity: str = Query(..., min_length=1, description="Crop name (e.g., Tomato, Potato, Onion)"),
    mandi: str = Query(..., min_length=1, description="Mandi name (e.g., Lucknow)"),
    db: Session = Depends(get_db)
):
    rec = get_latest_price(commodity, mandi, db)
    if not rec:
        return LatestPriceResponse(
            commodity=commodity,
            mandi=mandi,
            data_available=False,
            message=f"No recent market price record found for {commodity} in {mandi} mandi."
        )

    return LatestPriceResponse(
        commodity=commodity,
        mandi=mandi,
        data_available=True,
        price_date=rec["price_date"],
        min_price=rec["min_price"],
        max_price=rec["max_price"],
        modal_price=rec["modal_price"],
        unit=rec.get("unit", "₹/Quintal"),
        source=rec.get("source", "Agmarknet"),
        message="Latest mandi price retrieved successfully."
    )


@router.get("/history", response_model=PriceHistoryResponse)
def get_history(
    commodity: str = Query(..., min_length=1),
    mandi: str = Query(..., min_length=1),
    days: int = Query(7, ge=3, le=90),
    db: Session = Depends(get_db)
):
    records = get_price_history(commodity, mandi, days=days, db=db)
    if not records:
        return PriceHistoryResponse(
            commodity=commodity,
            mandi=mandi,
            data_available=False,
            record_count=0,
            trend="stable",
            message=f"Insufficient history records for {commodity} in {mandi}."
        )

    modal_prices = [r["modal_price"] for r in records]
    trend_label, pct_change = calculate_trend(modal_prices)

    items = [
        PriceRecordItem(
            price_date=r["price_date"],
            min_price=r.get("min_price"),
            max_price=r.get("max_price"),
            modal_price=r["modal_price"],
            unit=r.get("unit", "₹/Quintal"),
            source=r.get("source", "Agmarknet")
        )
        for r in records
    ]

    return PriceHistoryResponse(
        commodity=commodity,
        mandi=mandi,
        data_available=True,
        record_count=len(items),
        trend=trend_label,
        trend_percentage=pct_change,
        records=items,
        message="Historical prices and trend calculated successfully."
    )
