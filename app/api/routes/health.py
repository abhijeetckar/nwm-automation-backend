from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.core.s3_client import check_s3_connection

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Check PostgreSQL
        await db.execute("SELECT 1")
        
        # Check Redis
        redis_status = await redis_client.ping()

        # Check S3
        s3_status = check_s3_connection()

        return {
            "postgres": "ok",
            "redis": "ok" if redis_status else "fail",
            "s3": "ok" if s3_status else "fail",
        }
    except Exception as e:
        return {"error": str(e)}
