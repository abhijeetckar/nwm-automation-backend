import boto3
from botocore.exceptions import NoCredentialsError
from app.core.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.S3_REGION
)

def check_s3_connection():
    try:
        s3_client.list_buckets()
        return True
    except NoCredentialsError:
        return False
