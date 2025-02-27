from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.holiday_service import get_all_holidays
from app.schemas.holiday import HolidayBase

router = APIRouter()

@router.get("/holidays", response_model=list[HolidayBase])
def fetch_holidays(db: Session = Depends(get_db)):
    return get_all_holidays(db)
