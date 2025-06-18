from sqlalchemy.orm import Session
from database.models.answer import Answer
from database.models.user import User
from database.models.job import Job
from database.models.question import Question
from database.models.file import File


def get_answer_code(db: Session, user: User, answer_id: int):
    user_id = 1 if answer_id <= 50 else user.id
    answer = db.query(Answer).join(Job).filter(
        Answer.id == answer_id,
        Job.user_id == user_id
    ).first()

    if not answer:
        return {
            "answer_encoded": "db error", 
            "status": "error"
        }

    if answer.status == "done" and answer.answer_encoded:
        return {
            "answer_encoded": answer.answer_encoded, 
            "status": answer.status
        }

    return {
            "answer_encoded": "", 
            "status": answer.status
        }

def get_answer_detail_by_id(db: Session, user: User, answer_id: int):
    user_id = 1 if answer_id <= 50 else user.id
    answer = db.query(Answer).join(Job).filter(
        Answer.id == answer_id,
        Job.user_id == user_id
    ).first()
    question = db.query(Question).join(Job).filter(
        Question.id == answer.question_id,
        Job.user_id == user_id
    ).first()
    file = db.query(File).join(Job).filter(
        File.id == answer.file_id,
        Job.user_id == user_id
    ).first()
    
    return {
        "filename": file.filename,
        "question_text": question.text,
        "question_possible_options": question.possible_options,
        "answer_encoded": answer.answer_encoded,
        "answer_text": answer.answer_text,
        "answer_contexts": answer.answer_contexts,
        "answer_conversation": answer.answer_conversation,
        "evaluation": answer.evaluation,
    }