from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from app.api.auth import get_current_user
from database.models.user import User
from app.schemas.answer import AnswerOut, AnswerDetail
from app.services.answer_service import get_answer_code, get_answer_detail_by_id

router = APIRouter()

@router.get("/{answer_id}", response_model=AnswerOut)
def get_answer_by_id(answer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_answer_code(db, current_user, answer_id)

@router.get("/{answer_id}/detail", response_model=AnswerDetail)
def get_answer_detail(answer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_answer_detail_by_id(db, current_user, answer_id)