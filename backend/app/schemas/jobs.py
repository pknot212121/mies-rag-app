from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class Question(BaseModel):
    id: int
    text: str

class File(BaseModel):
    id: int
    filename: str

class Answer(BaseModel):
    id: int
    file_id: int
    question_id: int

class JobDetail(BaseModel):
    id: int
    name: str
    questions: List[Question]
    files: List[File]
    answers: List[Answer]

class JobStatus(BaseModel):
    status: str