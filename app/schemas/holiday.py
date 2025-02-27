from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class HolidayBase(BaseModel):
    date: date
    day: str
    defer_all: bool
    description: Optional[str] = None
    allow_download: List[dict] = []

    class Config:
        orm_mode = True
