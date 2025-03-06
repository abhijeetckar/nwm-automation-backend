from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base


class FileDownloadArchive(Base):
    __tablename__ = "file_download_archive"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    log = Column('log', JSONB)
