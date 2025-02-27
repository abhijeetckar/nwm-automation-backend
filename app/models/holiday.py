from sqlalchemy import Column, Integer, String, Date, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from app.db import Base

class HolidayMaster(Base):
    __tablename__ = "holiday_master"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    day = Column(String(50), nullable=False)
    defer_all = Column(Boolean, default=True, nullable=False)
    description = Column(String(50), nullable=True)
    allow_download = Column(JSONB, nullable=True, server_default="[]")

    __table_args__ = (
        CheckConstraint(
            "defer_all = TRUE OR (allow_download IS NOT NULL AND jsonb_array_length(allow_download) > 0)",
            name="check_allow_download_not_empty_if_defer_all_false"
        ),
    )
