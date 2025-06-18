from sqlalchemy.orm import Session
from database.models.answer import Answer
from database.models.job import Job
import csv
import json

def generate_main_encoded_raport(db: Session, job_id: int, output_path: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise ValueError(f"Job with id {job_id} not found.")

    questions = job.questions
    files = job.files

    header = [""] + [
        f"{q.text}\n{q.possible_options}" if q.possible_options else q.text
        for q in questions
    ]

    answers = db.query(Answer).filter(Answer.job_id == job_id).all()
    answer_map = {(a.file_id, a.question_id): a for a in answers}

    data_rows = []
    for file in files:
        row = [file.filename]
        for question in questions:
            key = (file.id, question.id)
            answer = answer_map.get(key)
            row.append(answer.answer_encoded if answer and answer.answer_encoded else "")
        data_rows.append(row)

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data_rows)

    return output_path


def generate_main_detailed_raport(db: Session, job_id: int, output_path: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise ValueError(f"Job with id {job_id} not found.")

    questions = job.questions
    files = job.files

    header_line_1 = [""] + [q.text for q in questions for _ in range(3)]
    header_line_2 = [""] + [
        item
        for q in questions
        for item in (
            "[context = original text]",
            "[LLM answer]",
            f"[kod]:\n{q.possible_options}" if q.possible_options else "[kod]"
        )
    ]
    answers = db.query(Answer).filter(Answer.job_id == job_id).all()
    answer_map = {(a.file_id, a.question_id): a for a in answers}

    data_rows = []
    for file in files:
        data_row = [file.filename]
        for question in questions:
            key = (file.id, question.id)
            answer = answer_map.get(key)

            context = answer_text = answer_encoded = ""
            if answer:
                answer_encoded = answer.answer_encoded or ""
                answer_text = answer.answer_text or ""
                context = ""
                for i, c in enumerate(answer.answer_contexts or []):
                    context += f"{i+1}.  {c.get('context', '')}\n"

            data_row.extend([context.strip(), answer_text, answer_encoded])
        data_rows.append(data_row)

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header_line_1)
        writer.writerow(header_line_2)
        writer.writerows(data_rows)

    return output_path


def generate_partial_report_md(db: Session, job_id: int, file_id:int, filename: str, output_path: str):
    job = db.query(Job).filter(Job.id == job_id).first()

    questions = job.questions
    answers = {
        (a.question_id): a
        for a in db.query(Answer).filter(
            Answer.job_id == job_id,
            Answer.file_id == file_id
        ).all()
    }

    lines = [f"# {filename}\n"]

    for q in questions:
        header = f"## {q.text.strip()}"
        if q.possible_options:
            header += f"\n\n**Options:** {q.possible_options.strip()}"
        lines.append(header + "\n")

        answer = answers.get(q.id)
        if not answer:
            lines.append("_No answer available._\n")
            continue

        if answer.answer_encoded:
            lines.append(f"**Encoded Answer:**\n\n`{answer.answer_encoded.strip()}`\n")

        if answer.answer_conversation:
            lines.append("**Conversation:**")
            for pair in answer.answer_conversation:
                question = pair.get("question", "").strip()
                response = pair.get("answer", "").strip()
                lines.append(f"- **Question:** \n```text\n{question}\n```")
                lines.append(f"  **Answer:** \n```text\n{response}\n```")
            lines.append("")

        if answer.answer_text:
            lines.append(f"**Text Answer:**\n\n{answer.answer_text.strip()}\n")

        if answer.answer_contexts:
            lines.append("**Contexts:**")
            for i, ctx in enumerate(answer.answer_contexts):
                context = ctx.get("context", "").strip()
                score = ctx.get("score", None)
                score_str = f" *(score: {score:.2f})*" if score is not None else ""
                lines.append(f"{i+1}.{score_str}\n```text\n{context}\n```")
            lines.append("")

        if answer.evaluation:
            lines.append("**Evaluation Metrics:**")

            ragas = answer.evaluation.get("ragas", {})
            if ragas:
                lines.append("- **RAGAS:**")
                for key, value in ragas.items():
                    if isinstance(value, float):
                        lines.append(f"  - {key.replace('_', ' ').capitalize()}: {value:.2f}")
                    else:
                        lines.append(f"  - {key.replace('_', ' ').capitalize()}: {value}")
            
            deepeval = answer.evaluation.get("deepeval", {})
            if deepeval:
                lines.append("- **DeepEval:**")
                for key, value in deepeval.items():
                    if isinstance(value, float):
                        lines.append(f"  - {key.replace('_', ' ').capitalize()}: {value:.2f}")
                    else:
                        lines.append(f"  - {key.replace('_', ' ').capitalize()}: {value}")

            lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return output_path


def generate_partial_report_json(db: Session, job_id: int, file_id: int, filename: str, output_path: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    questions = job.questions
    answers = {
        (a.question_id): a
        for a in db.query(Answer).filter(
            Answer.job_id == job_id,
            Answer.file_id == file_id
        ).all()
    }

    report = {
        "filename": filename,
        "questions": []
    }

    for q in questions:
        answer = answers.get(q.id)

        question_entry = {
            "question_text": q.text.strip(),
            "possible_options": q.possible_options.strip() if q.possible_options else None,
            "encoded_answer": None,
            "conversation": [],
            "text_answer": None,
            "contexts": [],
            "evaluation": {
                "ragas": {},
                "deepeval": {}
            }
        }

        if not answer:
            report["questions"].append(question_entry)
            continue

        if answer.answer_encoded:
            question_entry["encoded_answer"] = answer.answer_encoded.strip()

        if answer.answer_conversation:
            question_entry["conversation"] = [
                {
                    "question": pair.get("question", "").strip(),
                    "answer": pair.get("answer", "").strip()
                }
                for pair in answer.answer_conversation
            ]

        if answer.answer_text:
            question_entry["text_answer"] = answer.answer_text.strip()

        if answer.answer_contexts:
            question_entry["contexts"] = [
                {
                    "context": ctx.get("context", "").strip(),
                    "score": ctx.get("score")
                }
                for ctx in answer.answer_contexts
            ]

        if answer.evaluation:
            question_entry["evaluation"]["ragas"] = answer.evaluation.get("ragas", {})
            question_entry["evaluation"]["deepeval"] = answer.evaluation.get("deepeval", {})

        report["questions"].append(question_entry)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return output_path