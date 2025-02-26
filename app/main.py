# from fastapi import FastAPI
# from app.api.routes import health
#
# app = FastAPI(title="FastAPI Boilerplate")
#
# app.include_router(health.router, prefix="/api")
#
# @app.get("/")
# def root():
#     return {"message": "FastAPI Boilerplate is running"}

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from app.core.database import DatabaseConnectionManager
from app.core.redis_client import RedisConnectionManager
from app.utils.error_handling.global_handler import GlobalHandler
from app.utils.middleware.middleware import Middleware
from app.api.routes.health import health_router as router
from app.api.routes.chacha import capcha_router
from app.api.routes.download_document import download_router
app = FastAPI()

app.include_router(router, prefix="/v1")

app.include_router(capcha_router, prefix="/v1")
app.include_router(download_router, prefix="/v1")


@app.middleware('http')
async def app_middleware(request: Request, call_next):
    await DatabaseConnectionManager.established_connection()
    await RedisConnectionManager.establish_connection()
    middleware_handler = Middleware(request=request)
    return await middleware_handler.execute_middleware(call_next)


