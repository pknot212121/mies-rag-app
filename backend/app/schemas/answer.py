from pydantic import BaseModel
from typing import Optional, Dict, List

class AnswerOut(BaseModel):
    answer_encoded: Optional[str]
    status: str

class AnswerDetail(BaseModel):
    filename: str
    question_text: str
    question_possible_options: str
    answer_encoded: str
    answer_text: str
    answer_contexts: List[dict] = []
    answer_conversation: List[dict] = []
    evaluation: Dict = {}