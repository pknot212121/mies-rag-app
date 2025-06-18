from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.schemas.jobs import JobOut, JobDetail, JobStatus
from database.models.user import User
from database.models.job import Job
from app.services.jobs_service import get_status_job_by_id, get_user_jobs, get_job_detail_demo, get_job_detail_by_id, create_job_with_files, stop_job_by_id
from database.database import get_db
from app.api.auth import get_current_user

router = APIRouter()

@router.get("", response_model=List[JobOut])
def list_user_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_jobs(db, current_user)

@router.get("/demo", response_model=JobDetail)
def get_demo_detail(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_job_detail_demo(db, job_id=1)

@router.get("/{job_id}", response_model=JobDetail)
def get_job_detail(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_job_detail_by_id(db, current_user, job_id)

@router.get("/demo/status", response_model=JobStatus)
def get_status_job(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_status_job_by_id(db, current_user, job_id=1)

@router.get("/{job_id}/status", response_model=JobStatus)
def get_status_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_status_job_by_id(db, current_user, job_id)

@router.post("")
def create_job(
    name: str = Form(...),
    questions: List[str] = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_job_with_files(db, current_user, name, questions, files)

@router.post("/{job_id}/stop")
def stop_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return stop_job_by_id(db, current_user, job_id)