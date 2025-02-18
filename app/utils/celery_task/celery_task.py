from app.utils.celery_task.celery_beat_configuration import app
import requests


@app.task
def trigger_health_api():
    url = 'http://127.0.0.1:8001/v1/health'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Health API is up and running")
            return True
        else:
            print(f"Health API failed with status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return False
