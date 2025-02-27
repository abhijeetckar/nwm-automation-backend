import os
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.file_download_log import FileDownloadLog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure directory exists

def download_files_task(url: str, headers: dict, download_dir: str, filename: str):
    """Function to download a file using requests and save it to a specified directory."""
    try:
        # Send a GET request with headers
        response = requests.get(url, headers=headers)
        print(response)
        # Check if the request was successful
        if response.status_code == 200:
            # Save the content to a file
            file_path = os.path.join(download_dir, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"✅ File downloaded successfully: {file_path}")
        else:
            print(f"❌ Failed to download file. HTTP Status Code: {response.status_code}")
            return None
    except requests.RequestException as e:
        # Handle any request-related exceptions (like connection errors)
        print(f"❌ Error while downloading file: {e}")
        return None
