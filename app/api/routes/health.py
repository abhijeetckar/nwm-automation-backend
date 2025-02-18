import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import DatabaseConnectionManager
from app.core.redis_client import RedisConnectionManager
from app.core.s3_client import  Boto3ConnectionManager
from typing import Optional
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.utils.response_handler.response_handler import APIResponse
health_router = APIRouter()

@health_router.get("/health")
async def health_check(request:Request,forceUpdate: Optional[bool] = False,db: Session = Depends(DatabaseConnectionManager().get_database_connection)):
    # try:
    #     # Check PostgreSQL
    #     await db.execute("SELECT 1")
    #
    #     # Check Redis
    #     redis_status = await redis_client.ping()
    #
    #     # Check S3
    #     s3_status = check_s3_connection()
    #
    #     return {
    #         "postgres": "ok",
    #         "redis": "ok" if redis_status else "fail",
    #         "s3": "ok" if s3_status else "fail",
    #     }
    # except Exception as e:
    #     return {"error": str(e)}

    # status_code = "success_response"
    # check_database_connection = await DatabaseConnectionManager.check_connection() ## Check Database Connection
    # redis_database_connection = await RedisConnectionManager.check_redis_connection() ## Check Redis Connection
    # s3_connection = Boto3ConnectionManager.check_s3_connection() ## Check S3 Connection
    if forceUpdate:
        status_code = "success_response"
        check_database_connection = await DatabaseConnectionManager.check_connection()  ## Check Database Connection
        redis_database_connection = await RedisConnectionManager.check_redis_connection()  ## Check Redis Connection
        # s3_connection = Boto3ConnectionManager.check_s3_connection()  ## Check S3 Connection
    else:
        status_code = "success_response"
        check_database_connection = await DatabaseConnectionManager.check_connection()  ## Check Database Connection
        redis_database_connection = await RedisConnectionManager.check_redis_connection()  ## Check Redis Connection
        # s3_connection = Boto3ConnectionManager.check_s3_connection()  ## Check S3 Connection


    health_response = {
        "databaseConnection": "success" if check_database_connection else "failed",
        "redisConnection": "success" if redis_database_connection else "failed",
        # "S3Connection": "success" if s3_connection else "failed"
    }
    redis_client = await RedisConnectionManager.get_redis_connection()
    await redis_client.set('health_check_status', str(health_response))
    if not check_database_connection or not redis_database_connection :
        status_code = "bad_gateway"

    api_response_obj = APIResponse(request.headers.get("requestId"), status_code=status_code, data=health_response)
    return await api_response_obj.response_model()
