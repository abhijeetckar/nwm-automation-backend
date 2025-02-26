from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.core.database import DatabaseConnectionManager
from app.utils.error_handling.loggers import async_info, async_debug
from app.utils.manufacturer_operations.manufacturer_operations import ManufacturerOperations
from app.utils.response_handler.response_handler import APIResponse
from fastapi.encoders import jsonable_encoder
import inspect

download_router = APIRouter()


@download_router.get("/download_document")
async def health_check(request: Request, db: Session = Depends(DatabaseConnectionManager().get_database_connection)):
    await async_info(jsonable_encoder(request.headers).get("requestid"), inspect.currentframe().f_code.co_name, f"Started API: {inspect.currentframe().f_code.co_name}")
    download_response_body = {"filePath": ""}
    status_code = "success_response"
    file_path = await ManufacturerOperations(jsonable_encoder(request.headers).get("requestid")).document_download_api()
    download_response_body["filePath"] = file_path
    await async_debug(jsonable_encoder(request.headers).get("requestid"), inspect.currentframe().f_code.co_name,
                     f"Download Response Body: {download_response_body}")
    api_response_obj = APIResponse(request.headers.get("requestid"), status_code=status_code,
                                   data=download_response_body)
    return await api_response_obj.response_model()
