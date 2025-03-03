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

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text


# class DatabaseConnectionManager:
#     # _db_protocal = os.getenv("db_protocal")
#     # _db_diletics = os.getenv("db_diletics")
#     # _db_username =  os.getenv("db_username")
#     # _db_passward =  os.getenv("db_passward")
#     # _db_url =   os.getenv("db_url")
#     # _db_port =  os.getenv("db_port")
#     # _db_name =  os.getenv("db_name")
#
#     def __init__(self):
#         pass
#
#     # def _get_database_url(self):
#     #     database_url = self._db_protocal + "+" + self._db_diletics + "://" + self._db_username + ":" + self._db_passward + "@" + self._db_url + ":" + self._db_port + "/" + self._db_name
#     #     return database_url
#
#     @classmethod
#     async def established_connection(self):
#         global engine
#         global database_connection_session
#         global session_local
#         global base
#
#         engine = create_async_engine(
#             DATABASE_URL,pool_pre_ping=True,
#         )
#         session_local = sessionmaker(autoflush=False, bind=engine, expire_on_commit=False,
#                                      class_=AsyncSession)
#         base = declarative_base()
#         return True
#
#     @classmethod
#     async def get_database_connection(self):
#         database_connection_session = session_local()
#         try:
#             yield database_connection_session
#         except Exception as exp:
#             await database_connection_session.rollback()
#         finally:
#             print("closess")
#             await database_connection_session.close()
#
#     @classmethod
#     async def check_connection(self):
#         async with engine.begin() as conn:
#             try:
#                 await conn.execute(text("SELECT * from employee"))
#                 await  conn.run_sync(base.metadata.create_all)
#                 print("Database Connection Establised")
#                 return True
#             except Exception as exp:
#                 print(f"Database Connection Failed: {exp}")
#                 return False