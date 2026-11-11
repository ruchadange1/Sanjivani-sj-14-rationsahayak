import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.smart_search import smart_search


app = FastAPI(title="RationSahayak API")


# Getting the project folder location
base_path = Path(__file__).resolve().parent.parent
file_path = base_path / "data" / "records.json"


# Function to load records
def load_records():
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            records = json.load(file)

        return records

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Records file not found")


# Question model for POST request
class Question(BaseModel):
    question: str


# 1. HEALTH CHECK
@app.get("/health")
def health():
    return {"status": "healthy"}


# 2. GET RECORDS WITH LIMIT
@app.get("/records")
def get_records(limit: int = 10):

    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")

    records = load_records()
    result = []

    for i, record in enumerate(records[:limit]):
        new_record = record.copy()
        new_record["id"] = i + 1
        result.append(new_record)

    return result


# 3. GET RECORD USING ID
@app.get("/records/{id}")
def get_record(id: int):

    records = load_records()

    if id < 1 or id > len(records):
        raise HTTPException(status_code=404, detail="Record not found")

    record = records[id - 1].copy()
    record["id"] = id

    return record


# 4. SMART SEARCH USING TF-IDF AND COSINE SIMILARITY
@app.get("/search")
def search_records(q: str):

    if q.strip() == "":
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    records = load_records()
    result = smart_search(records, q)

    return {
        "query": q,
        "total_results": len(result),
        "results": result[:5]
    }


# 5. POST QUESTIONS
@app.post("/questions")
def ask_question(data: Question):

    question = data.question.strip()

    if question == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    records = load_records()
    result = smart_search(records, question)

    return {
        "question": question,
        "total_results": len(result),
        "relevant_records": result[:5]
    }