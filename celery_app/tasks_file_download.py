import os
import requests
import re
from datetime import datetime
from celery_app.celery_app import celery
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db import get_db
from app.models.file_download_log import FileDownloadLog
from app.models.files_master import FilesMaster
from celery import chain

# Define headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bseindia.com"
}
DOWNLOAD_DIR = "downloads"

def replace_date_patterns(filename: str) -> str:
    """Replace YYYYMMDD and DDMMYYYY placeholders with today's date."""
    today = datetime.today()
    formatted_date1 = today.strftime("%Y%m%d")  # YYYYMMDD
    formatted_date2 = today.strftime("%d%m%Y")  # DDMMYYYY
    return re.sub(r"YYYYMMDD", formatted_date1, re.sub(r"DDMMYYYY", formatted_date2, filename))

@celery.task(name="celery_app.tasks_file_download.fetch_files")
def fetch_files():
    """Fetch all records from files_master, modify filenames, and insert into file_download_log."""
    with next(get_db()) as db:
        files = db.query(FilesMaster).all()
        if not files:
            return "No files found in files_master."

        reformatted_files = []
        for file in files:
            updated_filename = replace_date_patterns(file.filename)
            download_url = f"{file.url}{updated_filename}"

            log_entry = FileDownloadLog(filename=updated_filename, fileurl=download_url)
            db.add(log_entry)
            reformatted_files.append({"id": file.id, "filename": updated_filename, "url": download_url})

        db.commit()
        return f"📄 Inserted {len(reformatted_files)} records into file_download_log."

@celery.task(name="celery_app.tasks_file_download.download_all_files")
def download_all_files():
    """Download all pending files one by one and update each row separately."""
    with next(get_db()) as db:
        pending_files = (
            db.query(FileDownloadLog)
            .filter(FileDownloadLog.downloaded == False)
            .with_for_update(skip_locked=True)  # Prevents race conditions
            .all()
        )

        if not pending_files:
            return "No pending downloads."

        successful_downloads = 0
        failed_downloads = 0

        for file_entry in pending_files:
            try:
                response = requests.get(file_entry.fileurl, headers=HEADERS)

                if response.status_code == 200:
                    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                    file_path = os.path.join(DOWNLOAD_DIR, file_entry.filename)

                    with open(file_path, "wb") as file:
                        file.write(response.content)

                    # ✅ Update the database row after each successful download
                    file_entry.downloaded = True
                    file_entry.downloaded_at = datetime.utcnow()
                    file_entry.reason = None
                    file_entry.attempts += 1
                    db.commit()

                    successful_downloads += 1
                else:
                    file_entry.reason = f"HTTP {response.status_code}"
                    file_entry.attempts += 1
                    db.commit()

                    failed_downloads += 1

            except requests.RequestException as e:
                file_entry.reason = str(e)
                file_entry.attempts += 1
                db.commit()

                failed_downloads += 1

        return f"✅ {successful_downloads} files downloaded, ❌ {failed_downloads} failed."

@celery.task(name="celery_app.tasks_file_download.fetch_and_download_files")
def fetch_and_download_files():
    """Chained task to fetch files first and then download them."""
    return chain(fetch_files.si(), download_all_files.si())() 