from sqlalchemy import Column, Integer, String, Unicode, Boolean,CheckConstraint
from app.db import Base

class FilesMaster(Base):
    __tablename__ = "files_master"

    id = Column(Integer, primary_key=True)
    filename = Column(String(150), nullable=False)
    url = Column(String(150), nullable=False)
    is_private = Column(Boolean, nullable=False,default=False)
    source = Column(String(50), nullable=True )
    __table_args__ = (
        CheckConstraint(
            "NOT is_private OR source IS NOT NULL",
            name="check_allow_download_not_empty_if_defer_all_false"
        ),
    )
