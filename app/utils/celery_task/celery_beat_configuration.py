from celery import Celery
import requests
from celery.schedules import solar,crontab

app = Celery('backend-service', broker='redis://localhost:6379/0')
app.autodiscover_tasks(['app.utils.login_automation'])

# Celery Beat configuration
#
# app.conf.beat_schedule = {
#     'health_check_every_hour': {
#         'task': 'app.api.router.celery.celery_task.trigger_health_api',
#         # 'schedule': crontab(minute=0, hour='*'),  # Runs every hour on the hour
#         'schedule': crontab(minute='*'),
#     },
#     'run_sunrise_task': {
#         'task': 'app.api.router.celery.celery_task.trigger_health_api',
#         ## sunset, solar_noon
#         'schedule': solar('sunrise',latitude=21.1458, longitude=79.0882),
#     },
#
# }

from celery.schedules import solar

# app.conf.beat_schedule = {
#     'health_check_every_hour': {
#         'task': 'app.utils.celery_task.celery_task.trigger_health_api',
#         # 'schedule': crontab(minute=0, hour='*'),  # Runs every hour on the hour
#     'schedule': crontab(minute='*')
#     },
#     'run_sunrise_task': {
#         'task': 'app.utils.celery_task.celery_task.trigger_health_api',
#         'schedule': solar('sunrise', lat=21.1458, lon=79.0882),
#     },
# }

app.conf.beat_schedule = {
    'login_automation': {
        'task': 'app.utils.login_automation.capture_initial_network_calls_sync',
        # 'schedule': crontab(minute=0, hour='*'),  # Runs every hour on the hour
        'schedule': crontab(minute='*')
    }
}


app.conf.timezone = 'Asia/Kolkata'