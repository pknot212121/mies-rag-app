import os
import time
import asyncio
import nest_asyncio
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI 

from mies_rag.config.config import (
    MODEL, 
    MAX_STEPS, 
    DESABLE_SECOND_LOOP,
    EVALUATION, 
    RAGAS,
    G_EVAL,
)

from mies_rag.utils.QuestionsManager import QuestionsManager
from mies_rag.utils.VectorQueryEngineCreator import VectorQueryEngineCreator
from mies_rag.utils.RAGEvaluator import RAGEvaluator
from mies_rag.workflow.MultiStepQueryEngineWorkflow import MultiStepQueryEngineWorkflow

from sqlalchemy import and_
from database.models import Answer, Question, File
from dotenv import load_dotenv

load_dotenv()

def main(db, job_id, queries):
    INPUT_PATH = os.path.join("/app/jobs_files", str(job_id), "input")
    start = time.time()
    nest_asyncio.apply()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(model=MODEL)
    Settings.llm = llm
    
    questionsManager = QuestionsManager(queries, Settings.llm)

    files = os.listdir(INPUT_PATH)
    pdf_files = []

    for file in files:
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.splitext(file)[0])

    for i, file in enumerate(pdf_files):
        
        query_engine = VectorQueryEngineCreator(MODEL, INPUT_PATH).get_query_engine(file)
        workflow = MultiStepQueryEngineWorkflow(timeout=10000)
        result = asyncio.run(process_file(db, job_id, f"[{i+1}/{len(pdf_files)}]", file, workflow, questionsManager, Settings.llm, query_engine))
        
    end = time.time()
    execution_time = end - start
    
    print("END")
    print(f"Execution time: {execution_time} seconds")
    return 

async def process_file(db, job_id, f, filename, workflow, questionsManager, llm, query_engine):
    for i in range(questionsManager.count):
        print(f"\nProcessing: file {f}; query [{i+1}/{questionsManager.count}]")
        respon = await workflow.run(
            llm = llm,
            query = questionsManager.get_question(i),
            query_engine = query_engine,
            max_steps = MAX_STEPS,
            disable_second_loop = DESABLE_SECOND_LOOP,
        )
        respon = evaluation(llm, respon)
        save_in_db(db, job_id, filename, respon)
    return 1

def evaluation(llm, respon):
    if EVALUATION:
        evaluation = RAGEvaluator(llm, respon, MODEL, RAGAS, G_EVAL).evaluate()
    else:
        evaluation = {}

    if "contexts" in respon:
        del respon["contexts"]

    respon["evaluation"] = evaluation
    return respon
    
def save_in_db(db, job_id, filename, respon):
    file = db.query(File).filter(
        and_(
            File.filename == f"{filename}.pdf",
            File.job_id == job_id
        )
    ).first()

    question = db.query(Question).filter(
        and_(
            Question.text == respon["query"]["topic"],
            Question.job_id == job_id
        )
    ).first()

    existing_answer = db.query(Answer).filter(
        and_(
            Answer.file_id == file.id,
            Answer.question_id == question.id
        )
    ).first()
    if  existing_answer:
        existing_answer.status = "done"
        existing_answer.answer_text = respon["answer"]
        existing_answer.answer_encoded = respon["code"]
        existing_answer.answer_contexts = respon["best_context"]
        existing_answer.answer_conversation = respon["reasoning"]
        existing_answer.evaluation = respon["evaluation"]

    db.commit()
    return 
