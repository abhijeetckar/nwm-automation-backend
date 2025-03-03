from sqlalchemy import Column, Integer, String, Boolean, DateTime,CheckConstraint
from app.db import Base
from datetime import datetime

class FileDownloadLog(Base):
    __tablename__ = "file_download_log"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(50), nullable=False)
    fileurl = Column(String(255), nullable=False)
    downloaded = Column(Boolean, default=False)
    reason = Column(String(50), nullable=True)
    attempts = Column(Integer, default=0)
    downloaded_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    is_private = Column(Boolean, nullable=False, default=False)
    source = Column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "NOT is_private OR source IS NOT NULL",
            name="check_allow_download_not_empty_if_defer_all_false"
        ),
    )
