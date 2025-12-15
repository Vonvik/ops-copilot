from datetime import timedelta

beat_schedule = {
    "heartbeat-every-60s": {
        "task": "tasks.heartbeat",
        "schedule": timedelta(seconds=60),
    },
}
