from fastapi import FastAPI
from loguru import logger
from app.db import engine
from app.routes import holiday, files, celery_tasks  
from celery_app.tasks import fetch_data_task, fetch_users_task  # Import the Celery task
from celery.result import AsyncResult
from celery import chain

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

# api_router = APIRouter(prefix="/api") #todo remove /api prefix

app.include_router(holiday.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(celery_tasks.router, prefix="/api/celery")

# app.include_router(api_router)