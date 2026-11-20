from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_records():
    response = client.get("/records")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_empty_search():
    response = client.get("/search", params={"q": " "})

    assert response.status_code == 400


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