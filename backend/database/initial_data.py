from sqlalchemy import text
from database.models.user import User
from app.core.security import hash_password
from database.models.job import Job
from database.models.question import Question
from database.models.file import File
from database.models.answer import Answer

from database.data_demo.questions import QUESTIONS
from database.data_demo.files import FILES
from database.data_demo.ansewers import ANSWERS
import os

def reset_sequence(db, table_name, id_column):
    db.execute(text(f"""
        SELECT setval(
            pg_get_serial_sequence('{table_name}', '{id_column}'),
            COALESCE((SELECT MAX({id_column}) FROM {table_name}), 0),
            true
        );
    """))
    db.commit()

def create_default_users(db):
    users = [
        {"id": 1, "email": "admin@example.com", "name": "Admin", "password": os.getenv("FRONTEND_ADMIN_PASSWORD")},
    ]

    for user_data in users:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            new_user = User(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                hashed_password=hash_password(user_data["password"]),
            )
            db.add(new_user)

    db.commit()
    reset_sequence(db, 'users', 'id')


def create_demo_job(db):
    existing_job = db.query(Job).filter(Job.id == 1).first()
    if not existing_job:
        job = Job(id=1, name="Demo", user_id=1, status="done")
        db.add(job)

    if db.query(Question).count() < 5:
        for q in QUESTIONS:
            db_question = Question(
                id=q["id"],
                job_id=q["job_id"],
                text=q["text"],
                possible_options=q["possible_options"]
            )
            db.add(db_question)

    if db.query(File).count() < 10:
        for f in FILES:
            db_file = File(
                id=f["id"],
                job_id=f["job_id"],
                filename=f["filename"],
                filepath=f["filepath"]
            )
            db.add(db_file)

    if db.query(Answer).count() < 50:
        for a in ANSWERS:
            db_answer = Answer(
                id=a["id"],
                job_id=a["job_id"],
                file_id=a["file_id"],
                question_id=a["question_id"],
                status=a["status"],
                answer_text=a["answer_text"],
                answer_encoded=a["answer_encoded"],
                answer_contexts=a["answer_contexts"],
                answer_conversation=a["answer_conversation"],
                evaluation=a["evaluation"],
            )
            db.add(db_answer)

    db.commit()

    reset_sequence(db, 'jobs', 'id')
    reset_sequence(db, 'questions', 'id')
    reset_sequence(db, 'files', 'id')
    reset_sequence(db, 'answers', 'id')
