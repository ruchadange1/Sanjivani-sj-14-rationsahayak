import json
import pathlib
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel

from app.graph import graph
from app.llm import generate_answer
from app.rag import ask_question as rag_ask_question
from app.smart_search import smart_search
from app.vectorstore import collection, index_documents, semantic_search

# ==========================================
# 1. APPLICATION LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        document_count = collection.count()

        if document_count == 0:
            print("No documents found. Starting document indexing...")

            index_documents()

            print("Document indexing completed.")
            print("Total indexed documents:", collection.count())

        else:
            print("Documents already indexed:", document_count)

    except Exception as error:
        print("Vector database initialization failed:", error)
        raise

    yield


app = FastAPI(
    title="RationSahayak API",
    lifespan=lifespan
)


# ==========================================
# 2. PROJECT FOLDER LOCATION
# ==========================================

base_path = pathlib.Path(__file__).resolve().parent.parent
file_path = base_path / "data" / "records.json"


# ==========================================
# 3. LOAD RECORDS
# ==========================================

def load_records():
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================================
# 4. REQUEST MODELS
# ==========================================

class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    task: str = "general"


class AgentRequest(BaseModel):
    question: str
    card_type: str | None = None
    family_size: int | None = None
    annual_income: float | None = None
    area: str | None = None
    thread_id: str
    approved: bool = False


# ==========================================
# 5. HEALTH
# ==========================================

@app.get("/health")
def health():
    return {"status": "healthy"}


# ==========================================
# 6. GET RECORDS
# ==========================================

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


# ==========================================
# 7. GET RECORD BY ID
# ==========================================

@app.get("/records/{id}")
def get_record(id: int):

    records = load_records()

    if id < 1 or id > len(records):
        raise HTTPException(status_code=404, detail="Record not found")

    record = records[id - 1].copy()
    record["id"] = id

    return record


# ==========================================
# 8. SMART SEARCH
# ==========================================

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


# ==========================================
# 9. POST QUESTIONS
# ==========================================

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


# ==========================================
# 10. CHAT WITH RATIONSAHAYAK
# ==========================================

@app.post("/chat")
def chat(data: ChatRequest):

    question = data.question.strip()

    if question == "":
        raise HTTPException(status_code=400, detail="Empty question")

    with open(
        base_path / "prompts" / "system.txt",
        "r",
        encoding="utf-8"
    ) as file:
        system_prompt = file.read()

    if data.task == "eligibility":
        task_file = "task_2.txt"
    else:
        task_file = "task_1.txt"

    with open(
        base_path / "prompts" / task_file,
        "r",
        encoding="utf-8"
    ) as file:
        task_prompt = file.read()

    records = smart_search(load_records(), question)

    context = ""

    for record in records[:5]:
        context += record["rule"] + "\n"

    user_prompt = (
        task_prompt +
        "\n\nAvailable Records:\n" +
        context +
        "\nQuestion: " + question +
        "\nReturn only valid JSON."
    )

    try:

        answer = generate_answer(system_prompt, user_prompt)

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


# ==========================================
# 11. SEMANTIC SEARCH
# ==========================================

@app.get("/search/semantic")
def search_semantic(q: str):

    if q.strip() == "":
        raise HTTPException(status_code=400, detail="Empty search query")

    if collection.count() == 0:
        raise HTTPException(status_code=404, detail="No documents indexed")

    results = semantic_search(q)

    response = []

    for i in range(len(results["documents"][0])):

        response.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "page": results["metadatas"][0][i]["page"],
            "title": results["metadatas"][0][i]["title"],
            "distance": results["distances"][0][i]
        })

    return {
        "query": q,
        "total_results": len(response),
        "results": response
    }


# ==========================================
# 12. RAG QUESTION ANSWERING
# ==========================================

@app.post("/ask")
def ask_rag_question(data: Question):

    question = data.question.strip()

    if question == "":
        raise HTTPException(status_code=400, detail="Empty question")

    if collection.count() == 0:
        raise HTTPException(status_code=404, detail="No documents indexed")

    try:

        result = rag_ask_question(question)

        return {
            "question": question,
            "answer": result["answer"],
            "citations": result["citations"]
        }

    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error))

    except requests.RequestException:
        raise HTTPException(status_code=502, detail="LLM request failed")


# ==========================================
# 13. LANGGRAPH AGENT
# ==========================================

@app.post("/agent")
def run_agent(data: AgentRequest):

    question = data.question.strip()

    if question == "":
        raise HTTPException(status_code=400, detail="Empty question")

    if data.thread_id.strip() == "":
        raise HTTPException(status_code=400, detail="Thread ID is required")

    config = {
        "configurable": {
            "thread_id": data.thread_id
        }
    }

    try:

        # Resume graph after approval
        if data.approved:

            result = graph.invoke(
                Command(resume=True),
                config
            )

        else:

            # Start a new graph execution
            state = {
                "question": question,
                "card_type": data.card_type,
                "family_size": data.family_size,
                "annual_income": data.annual_income,
                "area": data.area,
                "tool_used": "",
                "answer": "",
                "approved": False
            }

            result = graph.invoke(state, config)

        # Check for approval request
        if "__interrupt__" in result:

            return {
                "status": "approval_required",
                "message": result["__interrupt__"][0].value["message"],
                "thread_id": data.thread_id
            }

        return {
            "status": "completed",
            "tool_used": result["tool_used"],
            "answer": result["answer"],
            "thread_id": data.thread_id
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Agent request failed")