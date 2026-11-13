import json
import requests

import pathlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.smart_search import smart_search
from app.llm import generate_answer


app = FastAPI(title="RationSahayak API")


# Project folder location
base_path = pathlib.Path(__file__).resolve().parent.parent
file_path = base_path / "data" / "records.json"


# Load records
def load_records():
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# Request models
class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    task: str = "general"


# 1. HEALTH
@app.get("/health")
def health():
    return {"status": "healthy"}


# 2. GET RECORDS
@app.get("/records")
def get_records(limit: int = 10):

    if limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit")

    records = load_records()
    result = []

    for i, record in enumerate(records[:limit]):
        new_record = record.copy()
        new_record["id"] = i + 1
        result.append(new_record)

    return result


# 3. GET RECORD BY ID
@app.get("/records/{id}")
def get_record(id: int):

    records = load_records()

    if id < 1 or id > len(records):
        raise HTTPException(status_code=404, detail="Record not found")

    record = records[id - 1].copy()
    record["id"] = id

    return record


# 4. SMART SEARCH
@app.get("/search")
def search_records(q: str):

    if q.strip() == "":
        raise HTTPException(status_code=400, detail="Empty search")

    result = smart_search(load_records(), q)

    return {
        "query": q,
        "total_results": len(result),
        "results": result[:5]
    }


# 5. POST QUESTIONS
@app.post("/questions")
def ask_question(data: Question):

    if data.question.strip() == "":
        raise HTTPException(status_code=400, detail="Empty question")

    result = smart_search(load_records(), data.question)

    return {
        "question": data.question,
        "total_results": len(result),
        "relevant_records": result[:5]
    }


# 6. CHAT WITH RATIONSAHAYAK
@app.post("/chat")
def chat(data: ChatRequest):

    question = data.question.strip()

    if question == "":
        raise HTTPException(status_code=400, detail="Empty question")

    # Load system prompt
    with open(base_path / "prompts" / "system.txt", "r", encoding="utf-8") as file:
        system_prompt = file.read()

    # Select task prompt
    if data.task == "eligibility":
        task_file = "task_2.txt"
    else:
        task_file = "task_1.txt"

    with open(base_path / "prompts" / task_file, "r", encoding="utf-8") as file:
        task_prompt = file.read()

    # Find relevant records
    records = smart_search(load_records(), question)

    context = ""

    for record in records[:5]:
        context += record["rule"] + "\n"

    # Prepare user prompt
    user_prompt = (
        task_prompt +
        "\n\nAvailable Records:\n" +
        context +
        "\nQuestion: " + question +
        "\nReturn only valid JSON."
    )

    try:

        answer = generate_answer(system_prompt, user_prompt)

        # Convert response into JSON
        result = json.loads(answer)

        return {
            "answer": result.get("answer", ""),
            "confidence": result.get("confidence", "low"),
            "follow_up": result.get("follow_up", "")
        }

    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error))

    except requests.RequestException:
        raise HTTPException(status_code=502, detail="LLM request failed")

    except (json.JSONDecodeError, KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Invalid LLM response")