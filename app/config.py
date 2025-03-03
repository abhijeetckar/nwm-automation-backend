from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    DB_HOST: str
    DB_PORT: int = 5432  # Default port value
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    NSE_BASE_URL: str
    BSE_BASE_URL: str
    DOWNLOAD_DIR: str
    CELERY_BROKER_URL: str  # Add Celery broker URL
    CELERY_RESULT_BACKEND: str  # Add Celery result backend
    
    class Config:
        env_file = ".env"  # Path to your .env file

# Create an instance of the configuration
app_config = AppConfig()
