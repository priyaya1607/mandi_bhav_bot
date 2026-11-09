from fastapi import APIRouter
from ..database import check_db_connection

router = APIRouter(prefix="", tags=["Health"])

@router.get("/health")
def health_check():
    db_status = check_db_connection()
    return {
        "status": "healthy",
        "service": "CROPORA AI - Mandi Bhav Bot Backend",
        "database": db_status
    }
