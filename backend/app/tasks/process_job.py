from app.core.celery_app import celery_app
from database.database import SessionLocal
from database.models import Job, Answer, Question
from mies_rag.main import main as miesRAG
import time


@celery_app.task(name="app.tasks.process_job.process_job")
def process_job(job_id: int):
    print(f"Processing job {job_id}")
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return f"Job {job_id} not found"

    job.status = "processing"
    questions = db.query(Question).filter(Question.job_id == job_id).all()
    quesries = []
    for q in questions:
        quesries.append(
            {
                "topic": q.text,
                "possible_options": q.possible_options
            }
        )
    miesRAG(db, job_id, quesries)
    job.status = "done"
    db.commit()

    return f"Processed job {job_id}"
