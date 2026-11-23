import json
from contextlib import asynccontextmanager
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.graph import graph
from app.llm import generate_answer
from app.rag import ask_question as rag_ask_question
from app.records import load_policy_records
from app.smart_search import smart_search
from app.vectorstore import collection, index_documents, semantic_search

BASE_PATH = Path(__file__).resolve().parent.parent


# Application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        count = collection.count()

        if count == 0:
            print("Indexing documents...")
            index_documents()
            print("Indexed documents:", collection.count())
        else:
            print("Documents already indexed:", count)

    except Exception as error:
        print("Vector database initialization failed:", error)
        raise

    yield


app = FastAPI(title="RationSahayak API", lifespan=lifespan)


# Request models
class Question(BaseModel):
    question: str = Field(..., max_length=1000)


class ChatRequest(BaseModel):
    question: str = Field(..., max_length=1000)
    task: str = "general"


class AgentRequest(BaseModel):
    question: str = Field(..., max_length=1000)
    card_type: str | None = None
    family_size: int | None = None
    annual_income: float | None = None
    area: str | None = None
    thread_id: str
    approved: bool = False


# Health check
@app.get("/health")
def health():
    return {"status": "healthy"}


# Get policy records
@app.get("/records")
def get_records(limit: int = 10):
    if limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit")

    records = load_policy_records()

    return [
        {**record, "id": index}
        for index, record in enumerate(records[:limit], start=1)
    ]


# Get one record
@app.get("/records/{id}")
def get_record(id: int):
    records = load_policy_records()

    if id < 1 or id > len(records):
        raise HTTPException(status_code=404, detail="Record not found")

    return {**records[id - 1], "id": id}


# Smart search
@app.get("/search")
def search_records(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Empty search")

    results = smart_search(load_policy_records(), q)

    return {
        "query": q,
        "total_results": len(results),
        "results": results[:5]
    }


# Question-based record search
@app.post("/questions")
def ask_question(data: Question):
    question = data.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    results = smart_search(load_policy_records(), question)

    return {
        "question": question,
        "total_results": len(results),
        "relevant_records": results[:5]
    }


# Chat
@app.post("/chat")
def chat(data: ChatRequest):
    question = data.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    system_prompt = (BASE_PATH / "prompts" / "system.txt").read_text(
        encoding="utf-8"
    )

    task_file = "task_2.txt" if data.task == "eligibility" else "task_1.txt"
    task_prompt = (BASE_PATH / "prompts" / task_file).read_text(
        encoding="utf-8"
    )

    records = smart_search(load_policy_records(), question)
    context = "\n".join(record["rule"] for record in records[:5])

    user_prompt = (
        f"{task_prompt}\n\nAvailable Records:\n{context}"
        f"\nQuestion: {question}\nReturn only valid JSON."
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


# Semantic search
@app.get("/search/semantic")
def search_semantic(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Empty search query")

    if collection.count() == 0:
        raise HTTPException(status_code=404, detail="No documents indexed")

    results = semantic_search(q)

    response = [
        {
            "text": document,
            "source": metadata["source"],
            "page": metadata["page"],
            "title": metadata["title"],
            "distance": distance
        }
        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ]

    return {
        "query": q,
        "total_results": len(response),
        "results": response
    }


# RAG question answering
@app.post("/ask")
def ask_rag_question(data: Question):
    question = data.question.strip()

    if not question:
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


# LangGraph agent
@app.post("/agent")
def run_agent(data: AgentRequest):
    question = data.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    if not data.thread_id.strip():
        raise HTTPException(status_code=400, detail="Thread ID is required")

    config = {"configurable": {"thread_id": data.thread_id}}

    try:
        if data.approved:
            result = graph.invoke(Command(resume=True), config)
        else:
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
