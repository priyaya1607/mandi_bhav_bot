from datetime import datetime
from fastapi import APIRouter, Query, Depends
from ..database import get_db, Session
from ..schemas import ForecastResponse, ForecastItem
from ..repository import get_price_history
from ..forecasting.model import generate_forecast

router = APIRouter(prefix="", tags=["Forecasting"])

@router.get("/forecast", response_model=ForecastResponse)
def get_crop_forecast(
    commodity: str = Query(..., min_length=1),
    mandi: str = Query(..., min_length=1),
    days: int = Query(7, ge=3, le=14),
    db: Session = Depends(get_db)
):
    history = get_price_history(commodity, mandi, days=30, db=db)
    
    if len(history) < 5:
        return ForecastResponse(
            commodity=commodity,
            mandi=mandi,
            data_available=False,
            model_name="N/A",
            generated_at=datetime.utcnow(),
            forecasts=[],
            message=f"Insufficient historical data available for {commodity} in {mandi} to generate a reliable forecast."
        )

    res = generate_forecast(history, horizon_days=days)

    forecast_items = [
        ForecastItem(
            date=f["date"],
            day_name=f["day_name"],
            predicted_price=f["predicted_price"],
            lower_bound=f["lower_bound"],
            upper_bound=f["upper_bound"]
        )
        for f in res["forecasts"]
    ]

    return ForecastResponse(
        commodity=commodity,
        mandi=mandi,
        data_available=True,
        model_name=res["model_name"],
        generated_at=res["generated_at"],
        horizon_days=days,
        trend_direction=res["trend_direction"],
        forecasts=forecast_items,
        mae=res.get("mae"),
        rmse=res.get("rmse"),
        message=res.get("message")
    )
