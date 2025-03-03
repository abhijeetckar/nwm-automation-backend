from fastapi import APIRouter
from celery.result import AsyncResult
from celery import chain
from celery_app.tasks import fetch_data_task, fetch_users_task  # Import Celery tasks

router = APIRouter()

@router.get("/task-status/")
def get_task_status(task_id: str):
    """Check the status of a Celery task"""
    result = AsyncResult(task_id)
    return {"status": result.status, "result": result.result}

@router.get("/fetch-data-async")
def fetch_data_async():
    """Trigger Celery Task"""
    print("------------------------Trigger Celery Task /fetch-data-async------------------------")
    task_chain = chain(fetch_data_task.s(), fetch_users_task.s())()
    return {"task_id": task_chain.id, "status": "Processing..."}

@router.get("/fetch-data-chain")
def fetch_data_chain():
    """Trigger a Celery task chain"""
    print("------------------------Trigger Celery Task /fetch-data-chain------------------------")
    task = chain(fetch_data_task.s(), fetch_users_task.s())()
    return {"task_id": task.id, "status": "Processing..."}
