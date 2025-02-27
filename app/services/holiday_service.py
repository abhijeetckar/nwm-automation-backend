from sqlalchemy.orm import Session
from app.models.holiday import HolidayMaster

def get_all_holidays(db: Session):
    return db.query(HolidayMaster).all()
