from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database.database import Base

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    file_id = Column(Integer, ForeignKey("files.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    status = Column(String, default="pending")
    answer_text = Column(Text, nullable=True)
    answer_encoded = Column(Text, default="")
    answer_contexts = Column(JSONB, default=list)
    answer_conversation = Column(JSONB, default=list)
    evaluation = Column(JSONB, default=dict)


    job = relationship("Job", back_populates="answers")
    file = relationship("File")
    question = relationship("Question")
