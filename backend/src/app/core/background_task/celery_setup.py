from celery import Celery

from ..config import config_value

broker_url = (
    f"redis://{config_value.host}:" 
    f"{config_value.port}/"
    f"{config_value.REDIS_BROKER_DB}"
)

backend_url = (
    f"redis://{config_value.host}:"
    f"{config_value.port}/"
    f"{config_value.REDIS_RESULT_DB}"
)

celery = Celery(
    "knowbase-ai", # this specifies the name of the Celery application

    broker=broker_url, # this specifies the broker URL for Celery to send and receive messages 

    backend=backend_url # this specifies the backend URL for Celery to store the results of tasks
)

celery.conf.update(

    task_serializer="json", # this specifies that tasks will be serialized in JSON format

    result_serializer="json", # this specifies that results will be serialized in JSON format

    accept_content=["json"], # this specifies that only JSON content will be accepted

    timezone="UTC", # this specifies that the timezone for Celery will be UTC

    enable_utc=True, # this specifies that UTC support will be enabled

    result_expires=60, # this specifies that the results of tasks will expire after 3600 seconds (1 hour)

    broker_connection_retry_on_startup=True, # this specifies that Celery will retry the broker connection on startup if it fails

    task_track_started=True, # this specifies that Celery will track the start of tasks
)

