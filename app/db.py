import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import app_config

DATABASE_URL = f"postgresql://{app_config.DB_USER}:{app_config.DB_PASS}@{app_config.DB_HOST}:{app_config.DB_PORT}/{app_config.DB_NAME}"

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db: Session = SessionLocal()
    try:
        yield db  # Yields the session for use in API routes
    finally:
        db.close()  # Closes the session after request