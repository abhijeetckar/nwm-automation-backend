from typing import Optional

from pydantic import BaseModel, Field


class StandarResponseModel(BaseModel):
    reqId: Optional[str] = None
    errors: Optional[str] = []
    data: Optional[str] = {}


class RequestBody(BaseModel):
    kamlesh: Optional[str] = None
    kjak: Optional[str] = None


class StandarErrorResponseModel(BaseModel):
    error_code: Optional[str] = Field(None, alias="errorCode")
    error_type: Optional[str] = Field(None, alias="errorType")
    error_message: Optional[str] = Field(None, alias="errorMessage")
    error_display_msg: Optional[str] = Field(None, alias="errorDisplayMsg")

    class Config:
        populate_by_name = True
