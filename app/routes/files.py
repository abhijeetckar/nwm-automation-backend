import os
import requests
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.files_master import FilesMaster
from app.models.file_download_log import FileDownloadLog
from app.schemas.files import FilesSchema
from celery_app.tasks_file_download import fetch_files, process_file_downloads
import re
from datetime import datetime
# app/routes/files.py

from app.services.file_download_service import download_files_task  # Import the download task

# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.get("/files")
def fetch_files_task():
    """Trigger Celery task to fetch files and update `file_download_log`."""
    task = fetch_files.delay()
    return {"task_id": task.id, "status": "Fetching files in the background."}

@router.get("/download")
def process_download_task():
    """Trigger Celery task to process all pending downloads."""
    task = process_file_downloads.delay()
    return {"task_id": task.id, "status": "Downloading files in the background."}


def replace_date_patterns(filename: str) -> str:
    """Replace YYYYMMDD and DDMMYYYY placeholders with today's date."""
    today = datetime.today()
    formatted_date1 = today.strftime("%Y%m%d")  # YYYYMMDD
    formatted_date2 = today.strftime("%d%m%Y")  # DDMMYYYY

    filename = re.sub(r"YYYYMMDD", formatted_date1, filename)
    filename = re.sub(r"DDMMYYYY", formatted_date2, filename)
    
    return filename

@router.get("/files", response_model=list[FilesSchema])
def fetch_files(db: Session = Depends(get_db)):
    """Fetch all records from files_master, modify filenames, insert into file_download_log, and return."""
    files = db.query(FilesMaster).all()
    reformatted_files = []

    print("Total files fetched:", len(files))  # Debugging

    for file in files:
        updated_filename = replace_date_patterns(file.filename)

        print("Inserting into file_download_log:", updated_filename)  # Debugging
        
        download_url = f"{file.url}{updated_filename}"  # Concatenate the URL and the filename

        # Insert into file_download_log
        log_entry = FileDownloadLog(filename=updated_filename, fileurl=download_url)
        db.add(log_entry)

        reformatted_files.append({
            "id": file.id,
            "filename": updated_filename,
            "url": download_url
        })

    db.flush()  # Ensures all insertions are staged before committing
    db.commit()  # Commit all insertions at once

    print("✅ Inserted all filenames into file_download_log")  # Debugging

    return reformatted_files

@router.get("/download")
def process_file_downloads(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Define headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bseindia.com"
    }
    DOWNLOAD_DIR = "downloads"
    
    # Fetch files that haven't been downloaded yet
    pending_files = db.query(FileDownloadLog).filter_by(downloaded=False).all()

    print(f"Pending files: {len(pending_files)}")  # Log the number of pending files

    # Add background tasks for each file
    for file_entry in pending_files:
        # Use the file's fileurl and filename from file_download_log
        file_url = file_entry.fileurl
        filename = file_entry.filename
        # Add a task to download the file in the background
        background_tasks.add_task(download_file, file_url, headers, DOWNLOAD_DIR, filename, db, file_entry)

    return {"message": "Download process started in the background."}


def download_file(url: str, headers: dict, download_dir: str, filename: str, db: Session, file_entry: FileDownloadLog):
    """Function to download a file using requests and save it to a specified directory."""
    try:
        # Send a GET request with headers
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the content to a file
            file_path = os.path.join(download_dir, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"✅ File downloaded successfully: {file_path}")

            # Update the file entry after successful download
            file_entry.downloaded = True
            file_entry.downloaded_at = datetime.utcnow()
            file_entry.reason = None

        else:
            print(f"❌ Failed to download file. HTTP Status Code: {response.status_code}")
            file_entry.reason = f"HTTP {response.status_code}"

        # Increment attempts and commit changes
        file_entry.attempts += 1
        db.add(file_entry)  # Ensure the object is added to the session
        db.flush()  # Explicitly flush changes to ensure they are staged in the session
        db.commit()  # Commit changes to the database

    except requests.RequestException as e:
        # Handle any request-related exceptions (like connection errors)
        print(f"❌ Error while downloading file: {e}")
        file_entry.reason = str(e)

        # Increment attempts and commit changes
        file_entry.attempts += 1
        db.add(file_entry)  # Ensure the object is added to the session
        db.flush()  # Explicitly flush changes to ensure they are staged in the session
        db.commit()  # Commit changes to the database