import os
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab
from celery import chain

# Load environment variables from .env file
load_dotenv()

celery = Celery(
    "celeryfastapi",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery.conf.update(
    task_track_started=True,
    result_extended=True,
    task_ignore_result=False,
    result_persistent=True,
    enable_utc=True,
    timezone="Asia/Kolkata",  # Keep only one timezone
    beat_scheduler="celery.beat.schedulers:PersistentScheduler",  # Fix scheduler
)

# import celery_app.tasks
import celery_app.tasks_file_download
celery.autodiscover_tasks(["celery_app.tasks_file_download"])

# celery.conf.beat_schedule = {
#     "fetch-data-every-10-seconds": {
#         "task": "celery_app.tasks.fetch_and_process_data",  # Ensure this task is correctly imported
#         "schedule": 10.0,  # Run every 10 seconds
#     }
# }

celery.conf.beat_schedule = {
    "fetch-and-download-every-minute": {
        "task": "celery_app.tasks_file_download.fetch_and_download_files",
        "schedule": 60.0,  # Run every 1 minute
    }
}

@celery.task(bind=True)
def add(self, x, y):
    return x + y