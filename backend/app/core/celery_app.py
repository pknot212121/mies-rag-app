from celery import Celery 

print("Starting Celery app...")

celery_app = Celery("app")
celery_app.config_from_object("app.core.config_celary")
celery_app.autodiscover_tasks(["app.tasks"])

import app.tasks.process_job

print("Registered tasks:", celery_app.tasks.keys())

print("Celery app is ready!")
