
import app.main as main
from fastapi.testclient import TestClient


client = TestClient(main.app)


# A predictable fake provider for automated tests.
class FakeLLMProvider:

    def generate(self, prompt: str) -> str:
        return "The document describes software and AI experience."


class FailingLLMProvider:

    def generate(self, prompt: str) -> str:
        raise RuntimeError("Simulated provider failure")


# Sample retrieved document chunk.
SAMPLE_CHUNK = {
    "chunk_id": "test-document-page-1-chunk-1",
    "text": "The applicant has experience in Python and AI development.",
    "metadata": {
        "filename": "sample.pdf",
        "document_id": "test-document",
        "page_number": 1,
        "chunk_index": 1,
        "word_count": 10
    },
    "distance": 0.25
}


def configure_fake_retrieval(monkeypatch):
    """
    Replace embedding generation and vector search
    with predictable test results.
    """

    monkeypatch.setattr(
        main,
        "generate_query_embedding",
        lambda query: [0.1, 0.2, 0.3]
    )

    monkeypatch.setattr(
        main,
        "search_chunks",
        lambda **kwargs: [SAMPLE_CHUNK]
    )


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_endpoint_returns_results(monkeypatch):
    configure_fake_retrieval(monkeypatch)

    response = client.post(
        "/documents/search",
        json={
            "query": "What skills are mentioned?",
            "top_k": 3,
            "document_id": "test-document"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_results"] == 1
    assert data["results"][0]["filename"] == "sample.pdf"
    assert data["results"][0]["page_number"] == 1


def test_ask_endpoint_generates_answer(monkeypatch):
    configure_fake_retrieval(monkeypatch)

    monkeypatch.setattr(
        main,
        "llm_provider",
        FakeLLMProvider()
    )

    monkeypatch.setattr(main, "PROVIDER_NAME", "test")
    monkeypatch.setattr(main, "IS_MOCK", True)

    response = client.post(
        "/documents/ask",
        json={
            "query": "Summarise the document.",
            "top_k": 3,
            "document_id": "test-document"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "The document describes software and AI experience."
    )
    assert data["provider"] == "test"
    assert data["retrieved_chunks"] == 1
    assert len(data["sources"]) == 1


def test_ask_endpoint_handles_no_results(monkeypatch):
    monkeypatch.setattr(
        main,
        "generate_query_embedding",
        lambda query: [0.1, 0.2, 0.3]
    )

    monkeypatch.setattr(
        main,
        "search_chunks",
        lambda **kwargs: []
    )

    response = client.post(
        "/documents/ask",
        json={
            "query": "Find information about salary.",
            "top_k": 3,
            "document_id": "test-document"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "No document content was found for this search."
    )
    assert data["sources"] == []


def test_ask_endpoint_handles_provider_failure(monkeypatch):
    configure_fake_retrieval(monkeypatch)

    monkeypatch.setattr(
        main,
        "llm_provider",
        FailingLLMProvider()
    )

    response = client.post(
        "/documents/ask",
        json={
            "query": "Summarise the document.",
            "top_k": 3,
            "document_id": "test-document"
        }
    )

    assert response.status_code == 502

    assert response.json()["detail"] == (
        "The AI provider could not generate an answer. "
        "Check the server logs."
    )
