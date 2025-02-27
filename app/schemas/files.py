from pydantic import BaseModel
from typing import Optional

class FilesSchema(BaseModel):
    id: int
    filename: str
    url: Optional[str] = None  # Unicode(200) can be None

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
