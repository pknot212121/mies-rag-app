from sqlalchemy.orm import Session
from fastapi import HTTPException
from database.models.job import Job
from database.models.file import File
from database.models.question import Question
from database.models.user import User
from database.models.answer import Answer
from typing import List
from fastapi import UploadFile
import os
import json
from uuid import uuid4
from datetime import datetime
from app.tasks.process_job import process_job

JOB_FILES_DIR = "/app/jobs_files"


def get_user_jobs(db: Session, user: User):
    jobs = db.query(Job.id, Job.name).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).all()
    if not jobs:
        return []
    return jobs

def get_job_detail_demo(db: Session, job_id: int):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
    "id": job.id,
    "name": job.name,
    "questions": [
        {
            "id": q.id, 
            "text": q.text
        } for q in job.questions],
    "files": [
        {
            "id": f.id, 
            "filename": f.filename
            } for f in job.files],
    "answers": [
        {
            "id": a.id,
            "question_id": a.question_id,
            "file_id": a.file_id
        } for a in job.answers
    ]
}

def get_job_detail_by_id(db: Session, user: User, job_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "name": job.name,
        "questions": [
            {
                "id": q.id, 
                "text": q.text
            } for q in job.questions],
        "files": [
            {
                "id": f.id, 
                "filename": f.filename
                } for f in job.files],
        "answers": [
            {
                "id": a.id,
                "question_id": a.question_id,
                "file_id": a.file_id
            } for a in job.answers
        ]
    }

def get_status_job_by_id(db: Session, user: User, job_id: int):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job.status}

def create_job_with_files(db: Session, user: User, name: str, questions: List[str], files: List[UploadFile]):
    job = Job(name=name, user_id=user.id, status="pending")
    db.add(job)
    db.flush()

    db_questions = []
    for text in questions:
        question = json.loads(text)
        db_question = Question(job_id=job.id, text=question["text"], possible_options=question["possible_options"] )
        db.add(db_question)
        db_questions.append(db_question)

    file_dir = os.path.join(JOB_FILES_DIR, str(job.id), "input")
    os.makedirs(file_dir, exist_ok=True)

    db_files = []
    for file in files:
        filename = file.filename
        filepath = os.path.join(file_dir, filename)
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        db_file = File(
            job_id=job.id,
            filename=filename,
            filepath=filepath,
        )
        db.add(db_file)
        db_files.append(db_file)

    db.flush()  

    for question in db_questions:
        for db_file in db_files:
            db_answer = Answer(
                job_id=job.id,
                question_id=question.id,
                file_id=db_file.id,
                status="pending",
            )
            db.add(db_answer)

    db.commit()
    db.refresh(job)
    process_job.delay(job.id)
    return job


def stop_job_by_id(db: Session, user: User, job_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if job and job.status != "done":
        job.status = "error"
        job.finished_at = datetime.utcnow()
        db.commit()
    return job

