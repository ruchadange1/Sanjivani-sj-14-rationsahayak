from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


# 1. Test health endpoint
def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# 2. Test get records
def test_get_records():
    response = client.get("/records")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# 3. Test empty search
def test_empty_search():
    response = client.get("/search", params={"q": " "})

    assert response.status_code == 400


# 4. Test RAG question with fake LLM
def test_ask_with_fake_llm(monkeypatch):

    def fake_rag(question):
        return {
            "answer": "AAY households receive 35 kg per month.",
            "citations": [
                {"source": "ration_rules.pdf", "page": 1}
            ]
        }

    monkeypatch.setattr(main, "rag_ask_question", fake_rag)

    monkeypatch.setattr(
        main.collection,
        "count",
        lambda: 1
    )

    response = client.post(
        "/ask",
        json={"question": "How much ration does AAY receive?"}
    )

    assert response.status_code == 200
    assert "35 kg" in response.json()["answer"]
    assert len(response.json()["citations"]) > 0


# 5. Test question with exactly 1000 characters
def test_ask_accepts_question_within_limit(monkeypatch):

    monkeypatch.setattr(
        main.collection,
        "count",
        lambda: 1
    )

    response = client.post(
        "/ask",
        json={"question": "A" * 1000}
    )

    # Should pass Pydantic validation
    assert response.status_code != 422


# 6. Test question exceeding 1000 characters
def test_ask_rejects_question_over_limit():

    response = client.post(
        "/ask",
        json={"question": "A" * 1001}
    )

    assert response.status_code == 422