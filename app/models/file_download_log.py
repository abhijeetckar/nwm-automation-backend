from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
