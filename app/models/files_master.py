from sqlalchemy import Column, Integer, String, Unicode
from app.db import Base

class FilesMaster(Base):
    __tablename__ = "files_master"

    id = Column(Integer, primary_key=True)
    filename = Column(String(150), nullable=False)
    url = Column(String(150), nullable=False)
