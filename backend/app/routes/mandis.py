from typing import List
from fastapi import APIRouter, Depends
from ..database import get_db, Session
from ..schemas import MandiResponse
from ..repository import get_all_mandis

router = APIRouter(prefix="", tags=["Mandis"])

@router.get("/mandis", response_model=List[MandiResponse])
def list_mandis(db: Session = Depends(get_db)):
    return get_all_mandis(db)
