from celery_app import celery
from celery import chain
from celery_app.tasks import fetch_data_task , fetch_users_task
from celery_app.tasks_file_download import fetch_files, download_all_files

# @celery.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(
#         10.0,  # Run every 10 seconds
#         chain(fetch_data_task.s(), fetch_users_task.s()).apply_async()
#         name="Fetch Data Every 10 Seconds",
#     )


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Schedule fetch_files first, then download_all_files in sequence every minute."""
    sender.add_periodic_task(
        60.0,  # Run every 1 minute
        chain(fetch_files.s(), download_all_files.s()),  # Chain both tasks
        name="Fetch and Download Files Every Minute",
    )