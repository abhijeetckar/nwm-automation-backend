from fastapi import FastAPI
from loguru import logger
from app.db import engine
from app.routes import holiday, files  

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