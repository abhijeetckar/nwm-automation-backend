from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.core.database import DatabaseConnectionManager
from app.utils.manufacturer_operations.manufacturer_operations import ManufacturerOperations
from app.utils.response_handler.response_handler import APIResponse

download_router = APIRouter()


@download_router.get("/download_document")
async def health_check(request: Request, db: Session = Depends(DatabaseConnectionManager().get_database_connection)):
    download_response_body = {"filePath": ""}
    status_code = "success_response"
    file_path = await ManufacturerOperations().document_download_api()
    download_response_body["filePath"] = file_path
    api_response_obj = APIResponse(request.headers.get("requestId"), status_code=status_code,
                                   data=download_response_body)
    return await api_response_obj.response_model()
