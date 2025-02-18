# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from app.core.config import settings
#
# engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
# SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
#
# async def get_db() -> AsyncSession:
#     async with SessionLocal() as session:
#         yield session

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from app.core.config import settings

resi = os.getenv("db_protocal")
class DatabaseConnectionManager:
    # _db_protocal = os.getenv("db_protocal")
    # _db_diletics = os.getenv("db_diletics")
    # _db_username =  os.getenv("db_username")
    # _db_passward =  os.getenv("db_passward")
    # _db_url =   os.getenv("db_url")
    # _db_port =  os.getenv("db_port")
    # _db_name =  os.getenv("db_name")

    def __init__(self):
        pass

    def _get_database_url(self):
        database_url = self._db_protocal + "+" + self._db_diletics + "://" + self._db_username + ":" + self._db_passward + "@" + self._db_url + ":" + self._db_port + "/" + self._db_name
        return database_url

    @classmethod
    async def established_connection(self):
        global engine
        global database_connection_session
        global session_local
        global base

        engine = create_async_engine(
            settings.DATABASE_URL, future=True, echo=True, pool_pre_ping=True, pool_size=settings.POOL_SIZE,
            max_overflow=settings.MAX_OVERFLOW,
            echo_pool="debug"
        )
        session_local = sessionmaker(autoflush=False, bind=engine, expire_on_commit=False,
                                     class_=AsyncSession)
        base = declarative_base()
        return True

    @classmethod
    async def get_database_connection(self):
        database_connection_session = session_local()
        try:
            yield database_connection_session
        except Exception as exp:
            await database_connection_session.rollback()
        finally:
            print("closess")
            await database_connection_session.close()

    @classmethod
    async def check_connection(self):
        async with engine.begin() as conn:
            try:
                await conn.execute(text("SELECT * from employee"))
                await  conn.run_sync(base.metadata.create_all)
                print("Database Connection Establised")
                return True
            except Exception as exp:
                print(f"Database Connection Failed: {exp}")
                return False
