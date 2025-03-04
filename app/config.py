from pydantic_settings import BaseSettings
import json
from pydantic import field_validator

class AppConfig(BaseSettings):
    DB_HOST: str
    DB_PORT: int = 5432  # Default port value
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    NSE_BASE_URL: str
    BSE_BASE_URL: str
    DOWNLOAD_DIR: str
    SOURCE_URL:dict

    @field_validator("SOURCE_URL", mode="before")
    @classmethod
    def parse_source_url(cls, value):
        """Convert JSON string from .env to dictionary"""
        if isinstance(value, str):
            try:
                return json.loads(value)  # Convert JSON string to dict
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON for SOURCE_URL: {e}")
        return value  # If already a dict, return as is

    class Config:
        env_file = ".env"  # Path to your .env file
        nv_file_encoding = "utf-8"

# Create an instance of the configuration
app_config = AppConfig()
