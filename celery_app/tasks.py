# tasks.py
import requests
from celery_app.celery_app import celery
from celery import chain

@celery.task(name="celery_app.tasks.fetch_data_task")
def fetch_data_task():
    print("---------------------fetch_data_task---------------------")
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    return response.json()[:5] 

@celery.task(name="celery_app.tasks.fetch_users_task")
def fetch_users_task(previous_data):
    print("---------------------fetch_users_task---------------------")
    """Fetch users after fetching posts"""
    response = requests.get("https://jsonplaceholder.typicode.com/users")
    users = response.json()[:5] 
    
    # Here you can process both `previous_data` (posts) and `users`
    return {"posts": previous_data, "users": users}


@celery.task(name="celery_app.tasks.fetch_and_process_data")
def fetch_and_process_data():
    """This task chains fetch_data_task → fetch_users_task"""
    return chain(fetch_data_task.s(), fetch_users_task.s())()

# tasks.py
# @celery.task(name="tasks.fetch_data_task")
# def fetch_data_task():
#     response = requests.get("https://jsonplaceholder.typicode.com/posts")
#     data = response.json()
    
#     # Call the next task upon success
#     fetch_users_task.delay(data)
#     print("---------------------fetch_users_task---------------------")
#     return data
