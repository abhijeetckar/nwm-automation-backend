import os
import requests
from fastapi import APIRouter, Depends, BackgroundTasks,Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.files_master import FilesMaster
from app.models.file_download_log import FileDownloadLog
from app.schemas.files import FilesSchema
import re
from datetime import datetime
from app.models.holiday import HolidayMaster,HolidayException
from sqlalchemy.sql import func
from fastapi.encoders import jsonable_encoder

# app/routes/files.py

from app.services.file_download_service import download_files_task  # Import the download task
from app.utils.response_handler.response_handler import APIResponse

# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

router = APIRouter()

def replace_date_patterns(filename: str) -> str:
    """Replace YYYYMMDD and DDMMYYYY placeholders with today's date."""
    today = datetime.today()
    formatted_date1 = today.strftime("%Y%m%d")  # YYYYMMDD
    formatted_date2 = today.strftime("%d%m%Y")  # DDMMYYYY

    filename = re.sub(r"YYYYMMDD", formatted_date1, filename)
    filename = re.sub(r"DDMMYYYY", formatted_date2, filename)
    
    return filename


@router.get("/files", response_model=list[FilesSchema])
async def fetch_files(request:Request,db: Session = Depends(get_db)):
    """Fetch all records from files_master, modify filenames, insert into file_download_log, and return."""
    today = func.current_date()
    reason = ""
    holiday = db.query(HolidayMaster).filter(HolidayMaster.date == today).first()
    if holiday and holiday.defer_all:
        holiday_exception = db.query(HolidayException).filter(HolidayException.date == today).first()
        if holiday_exception is None:
            reason = holiday.description
        if holiday_exception and holiday_exception.defer_all:
            reason =  holiday_exception.description

    files = db.query(FilesMaster).all()
    reformatted_files = []

    print("Total files fetched:", len(files))  # Debugging

    for file in files:
        updated_filename = replace_date_patterns(file.filename)

        print("Inserting into file_download_log:", updated_filename)  # Debugging
        
        download_url = f"{file.url}{updated_filename}"  # Concatenate the URL and the filename

        # Insert into file_download_log
        update_data = {
            "filename":updated_filename,
            "fileurl":download_url
        }
        if len(reason) >0:
            update_data["reason"] = reason
        # log_entry = FileDownloadLog(filename=updated_filename, fileurl=download_url)
        log_entry = FileDownloadLog(**update_data)
        db.add(log_entry)

        reformatted_files.append(update_data)

    db.flush()  # Ensures all insertions are staged before committing
    db.commit()  # Commit all insertions at once

    print("✅ Inserted all filenames into file_download_log")  # Debugging

    # return reformatted_files
    api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                   data=reformatted_files)
    return await api_response_obj.response_model()

@router.get("/download")
async def process_file_downloads(request:Request,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Define headers to mimic a browser request
    today = func.current_date()

    holiday = db.query(HolidayMaster).filter(HolidayMaster.date == today).first()
    if holiday and holiday.defer_all:
        holiday_exception = db.query(HolidayException).filter(HolidayException.date == today).first()
        if holiday_exception is None:
            api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                           data=jsonable_encoder(holiday))
            return await api_response_obj.response_model()
        if holiday_exception and holiday_exception.defer_all:
            api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                           data=jsonable_encoder(holiday_exception))
            return await api_response_obj.response_model()

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
        if len(file_entry.reason) == 0:
            file_url = file_entry.fileurl
            filename = file_entry.filename
            # Add a task to download the file in the background
            background_tasks.add_task(download_file, file_url, headers, DOWNLOAD_DIR, filename, db, file_entry)

    api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                   data={"message": "Download process started in the background."})
    return await api_response_obj.response_model()
    # return {"message": "Download process started in the background."}


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



