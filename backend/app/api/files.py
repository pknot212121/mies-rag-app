from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.database import get_db
from app.api.auth import get_current_user
from database.models.user import User
from database.models.file import File
from app.services.file_service import (
    generate_main_encoded_raport,
    generate_main_detailed_raport,
    generate_partial_report_md,
    generate_partial_report_json
)
import os
router = APIRouter()
JOB_FILES_DIR = "/app/jobs_files"

@router.get("/{file_id}")
def get_pdf(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file = db.query(File).filter(File.id == file_id).first()
    output_path = file.filepath
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(output_path, media_type="application/pdf", filename=os.path.basename(output_path))

@router.get("/main_encoded_raport/{job_id}")
def get_main_encoded_raport(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dir = "demo" if job_id == 1 else job_id
    output_dir = os.path.join(JOB_FILES_DIR, str(dir), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "raport_encoded.csv")
    if not os.path.exists(output_path):
        output_path = generate_main_encoded_raport(db, job_id, output_path)
    return FileResponse(output_path, media_type="text/csv", filename=os.path.basename(output_path))

@router.get("/main_detailed_raport/{job_id}")
def get_main_detailed_raport(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dir = "demo" if job_id == 1 else job_id
    output_dir = os.path.join(JOB_FILES_DIR, str(dir), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "raport_detailed.csv")
    if not os.path.exists(output_path):
        output_path = generate_main_detailed_raport(db, job_id, output_path)
    return FileResponse(output_path, media_type="text/csv", filename=os.path.basename(output_path))

@router.get("/partial_report/{file_id}/md")
def get_partial_report_md(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file = db.query(File).filter(File.id == file_id).first()
    dir = "demo" if file.job_id == 1 else file.job_id
    output_dir = os.path.join(JOB_FILES_DIR, str(dir), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{os.path.splitext(file.filename)[0]}_raport.md")
    if not os.path.exists(output_path):
        output_path = generate_partial_report_md(db, file.job_id, file.id, file.filename,  output_path)
    return FileResponse(output_path, media_type="text/markdown", filename=os.path.basename(output_path))

@router.get("/partial_report/{file_id}/json")
def get_partial_report_md(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file = db.query(File).filter(File.id == file_id).first()
    dir = "demo" if file.job_id == 1 else file.job_id
    output_dir = os.path.join(JOB_FILES_DIR, str(dir), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{os.path.splitext(file.filename)[0]}_raport.json")
    if not os.path.exists(output_path):
        output_path = generate_partial_report_json(db, file.job_id, file.id, file.filename,  output_path)
    return FileResponse(output_path, media_type="application/json", filename=os.path.basename(output_path))