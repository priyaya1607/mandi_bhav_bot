from typing import List
from fastapi import APIRouter, Depends
from ..database import get_db, Session
from ..schemas import CommodityResponse
from ..repository import get_all_commodities

router = APIRouter(prefix="", tags=["Commodities"])

@router.get("/commodities", response_model=List[CommodityResponse])
def list_commodities(db: Session = Depends(get_db)):
    return get_all_commodities(db)
