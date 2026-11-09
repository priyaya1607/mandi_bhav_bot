from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class CommodityBase(BaseModel):
    name: str
    name_hi: Optional[str] = None

class CommodityResponse(CommodityBase):
    commodity_id: int
    class Config:
        from_attributes = True


class MandiBase(BaseModel):
    name: str
    district: str
    state: str

class MandiResponse(MandiBase):
    mandi_id: int
    class Config:
        from_attributes = True


class PriceRecordItem(BaseModel):
    price_date: date
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    modal_price: float
    unit: str = "₹/Quintal"
    source: str = "Agmarknet"

    class Config:
        from_attributes = True


class LatestPriceResponse(BaseModel):
    commodity: str
    mandi: str
    data_available: bool
    price_date: Optional[date] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    modal_price: Optional[float] = None
    unit: str = "₹/Quintal"
    source: Optional[str] = "Agmarknet"
    message: Optional[str] = None


class PriceHistoryResponse(BaseModel):
    commodity: str
    mandi: str
    data_available: bool
    record_count: int
    trend: str = "stable"  # "rising", "falling", "stable"
    trend_percentage: Optional[float] = None
    records: List[PriceRecordItem] = []
    message: Optional[str] = None


class ForecastItem(BaseModel):
    date: str
    day_name: str
    predicted_price: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    commodity: str
    mandi: str
    data_available: bool
    model_name: str
    generated_at: datetime
    horizon_days: int = 7
    trend_direction: str = "stable"
    forecasts: List[ForecastItem] = []
    mae: Optional[float] = None
    rmse: Optional[float] = None
    disclaimer: str = (
        "AI estimates are based on historical market trends and do not guarantee actual future prices. "
        "Market conditions can fluctuate due to weather, supply, and local demand."
    )
    message: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Natural language price query")


class QueryResponse(BaseModel):
    query: str
    detected_commodity: Optional[str] = None
    detected_mandi: Optional[str] = None
    detected_intent: str = "latest_price"
    success: bool
    message: str
    latest_price: Optional[LatestPriceResponse] = None
    history: Optional[PriceHistoryResponse] = None
    forecast: Optional[ForecastResponse] = None
