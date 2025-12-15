import time

from app.celery_app import celery_app


@celery_app.task(name="tasks.heartbeat")
def heartbeat():
    msg = f"[beat] Alive at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    print(msg)
    return {"message": msg}
