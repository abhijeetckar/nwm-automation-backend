from fastapi import FastAPI
from app.api.routes import health

app = FastAPI(title="FastAPI Boilerplate")

app.include_router(health.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "FastAPI Boilerplate is running"}
