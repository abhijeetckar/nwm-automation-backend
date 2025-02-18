# from pydantic_settings import BaseSettings
#
# class Settings(BaseSettings):
#     DATABASE_URL: str
#     REDIS_URL: str
#     AWS_ACCESS_KEY_ID: str
#     AWS_SECRET_ACCESS_KEY: str
#     S3_BUCKET_NAME: str
#     S3_REGION: str
#     POOL_SIZE: int
#     MAX_OVERFLOW: int
#
#     class Config:
#         env_file = ".env"
#
# settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str
    S3_REGION: str
    POOL_SIZE: int
    MAX_OVERFLOW: int

    class Config:
        env_file = ".env"

settings = Settings()
