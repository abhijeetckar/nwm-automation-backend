import os
import requests
from fastapi import APIRouter, Depends, BackgroundTasks,Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.file_download_archive import FileDownloadArchive
from app.models.files_master import FilesMaster
from app.models.file_download_log import FileDownloadLog
from app.schemas.files import FilesSchema
import re
from datetime import datetime
from app.models.holiday import HolidayMaster,HolidayException
from sqlalchemy.sql import func
from fastapi.encoders import jsonable_encoder
from app.config import app_config
import json

# app/routes/files.py

from app.services.file_download_service import download_files_task  # Import the download task
from app.utils.response_handler.response_handler import APIResponse
from datetime import datetime, timedelta
import re
from enum import Enum

# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

router = APIRouter()

def replace_date_patterns(filename: str, days_offset: int = 0) -> str:
    """Replace YYYYMMDD and DDMMYYYY placeholders with today's date."""
    # today = datetime.today()
    # # today = datetime(2025, 2, 3)
    # formatted_date1 = today.strftime("%Y%m%d")  # YYYYMMDD
    # formatted_date2 = today.strftime("%d%m%Y")  # DDMMYYYY
    #
    # filename = re.sub(r"YYYYMMDD", formatted_date1, filename)
    # filename = re.sub(r"DDMMYYYY", formatted_date2, filename)
    #
    # return filename
    adjusted_date = datetime.today() + timedelta(days=days_offset)
    formatted_date1 = adjusted_date.strftime("%Y%m%d")  # YYYYMMDD
    formatted_date2 = adjusted_date.strftime("%d%m%Y")  # DDMMYYYY

    filename = re.sub(r"YYYYMMDD", formatted_date1, filename)
    filename = re.sub(r"DDMMYYYY", formatted_date2, filename)
    return filename


def get_days_offset(db,filetime: str) -> int:
    today = datetime.today()
    # today = datetime(2025, 3, 17)
    weekday = today.weekday()  # Monday = 0, Sunday = 6

    if filetime == "EOD":
        offset = -3 if weekday == 0 else -1  # Monday -> last Friday, otherwise yesterday
    else:
        offset = 0# "BOD" files use the current day

    adjusted_date = today + timedelta(days=offset)

    while True:
        holiday = db.query(HolidayMaster).filter(HolidayMaster.date == adjusted_date).first()
        if holiday and holiday.defer_all:
            holiday_exception = db.query(HolidayException).filter(HolidayException.date == adjusted_date).first()
            if  holiday_exception is None or (holiday_exception and holiday_exception.defer_all):
                offset -= 1
                adjusted_date = today + timedelta(days=offset)
                continue  # Check the next previous day
        break  # Exit loop when a working day is found

    return offset


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
        updated_filename = replace_date_patterns(file.filename,get_days_offset(db,file.file_time.value))

        print("Inserting into file_download_log:", updated_filename)  # Debugging
        
        download_url = f"{file.url}{updated_filename}"  # Concatenate the URL and the filename

        # Insert into file_download_log
        update_data = {
            "filename":updated_filename,
            "fileurl":download_url,
            "is_private":file.is_private,
            "source":file.source,
            "file_time":file.file_time.value
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
        if file_entry.reason is None or len(file_entry.reason) == 0:
            file_url = file_entry.fileurl
            filename = file_entry.filename
            # Add a task to download the file in the background
            if file_entry.is_private:
                response = requests.post(app_config.SOURCE_URL.get(file_entry.source,"").get("url",""), json=app_config.SOURCE_URL.get(file_entry.source,"").get("request_body",{}),headers=app_config.SOURCE_URL.get(file_entry.source,"").get("headers",{}))
                json_response = response.json()
                headers["Authorization"] = f"Bearer {response.json().get("token")}"
                print(json_response)
            background_tasks.add_task(download_file, file_url, headers, DOWNLOAD_DIR, filename, db, file_entry)
            # download_file(file_url, headers, DOWNLOAD_DIR, filename, db, file_entry)

    api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                   data={"message": "Download process started in the background."})
    return await api_response_obj.response_model()


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
            print(f"-->{url}")

        # Increment attempts and commit changes
        file_entry.attempts += 1
        db.add(file_entry)  # Ensure the object is added to the session
        db.flush()  # Explicitly flush changes to ensure they are staged in the session
        db.commit()  # Commit changes to the database

    except requests.RequestException as e:
        # Handle any request-related exceptions (like connection errors)
        print(f"❌ Error while downloading file: {e}")
        print(url)
        file_entry.reason = str(e)

        # Increment attempts and commit changes
        file_entry.attempts += 1
        db.add(file_entry)  # Ensure the object is added to the session
        db.flush()  # Explicitly flush changes to ensure they are staged in the session
        db.commit()  # Commit changes to the database



def serialize_log(log):
    """Convert SQLAlchemy object to JSON serializable dict."""
    log_dict = log.__dict__.copy()
    log_dict.pop("_sa_instance_state", None)  # Remove SQLAlchemy metadata

    # Convert datetime fields to string
    for key, value in log_dict.items():
        if isinstance(value, datetime):
            log_dict[key] = value.isoformat()  # Convert datetime to ISO format
        elif isinstance(value, Enum):
            log_dict[key] = value.name

    return log_dict

@router.get("/file_download_archive")
async def update_file_download_archive(request:Request,db: Session = Depends(get_db)):
    try:
        logs = db.query(FileDownloadLog).all()
        if logs:
            logs_json = [serialize_log(log) for log in logs]
            archive_entry = FileDownloadArchive(date=func.now(), log=logs_json)
            db.add(archive_entry)
            db.query(FileDownloadLog).delete()
            db.commit()
        api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                       data={"message": "Logs archived successfully"})
        return await api_response_obj.response_model()
    except Exception as exp:
        print(exp)

@router.get("/retry/download/{filename}")
async def rety_to_download_file(request:Request,filename:str,db: Session = Depends(get_db)):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bseindia.com"
    }
    DOWNLOAD_DIR = "downloads"

    # Fetch files that haven't been downloaded yet
    pending_file = db.query(FileDownloadLog).filter_by(filename=filename).first()

    # print(f"Pending files: {pending_file}")  # Log the number of pending files
    if not pending_file.downloaded:
        file_url = pending_file.fileurl
        filename = pending_file.filename
        # Add a task to download the file in the background
        if pending_file.is_private:
            response = requests.post(app_config.SOURCE_URL.get(pending_file.source, "").get("url", ""),
                                     json=app_config.SOURCE_URL.get(pending_file.source, "").get("request_body", {}),
                                     headers=app_config.SOURCE_URL.get(pending_file.source, "").get("headers", {}))
            json_response = response.json()
            headers["Authorization"] = f"Bearer {response.json().get("token")}"
            print(json_response)
        # background_tasks.add_task(download_file, file_url, headers, DOWNLOAD_DIR, filename, db, file_entry)
        download_file(file_url, headers, DOWNLOAD_DIR, filename, db, pending_file)
        api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                       data={"message": "File Download is Completed"})
        return await api_response_obj.response_model()
    api_response_obj = APIResponse(request.headers.get("requestid"), status_code="success_response",
                                   data={"message": "File is Already downloaded"})
    return await api_response_obj.response_model()



