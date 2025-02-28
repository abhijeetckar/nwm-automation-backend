from fastapi import FastAPI,Request
from loguru import logger
from app.db import engine
from app.routes import holiday, files
from app.utils.middleware.middleware import Middleware

app = FastAPI()

logger.add("app.log", level="ERROR", rotation="1 week", retention="30 days", compression="zip")
# logger.add(lambda msg: print(msg, end=""), level="ERROR") # uncomment to enable debug logs

@app.on_event("startup")
def startup_event():
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
            logger.info("DB Connected")
    except Exception as e:
        logger.error(f"DB Connection Failed: {e}")

app.include_router(holiday.router, prefix="/api")
app.include_router(files.router, prefix="/api")

@app.middleware('http')
async def app_middleware(request: Request, call_next):
    # await DatabaseConnectionManager.established_connection()
    # await RedisConnectionManager.establish_connection()
    middleware_handler = Middleware(request=request)
    return await middleware_handler.execute_middleware(call_next)