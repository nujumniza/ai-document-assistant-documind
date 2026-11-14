from app.services.rag import build_rag_prompt


SAMPLE_CHUNKS = [
    {
        "text": "The company uses Python and FastAPI.",
        "metadata": {
            "filename": "sample.pdf",
            "page_number": 2
        }
    },
    {
        "text": "The system uses ChromaDB for vector storage.",
        "metadata": {
            "filename": "sample.pdf",
            "page_number": 3
        }
    }
]


def test_prompt_contains_user_question():
    question = "Which programming language does the company use?"

    prompt = build_rag_prompt(question, SAMPLE_CHUNKS)

    assert question in prompt


def test_prompt_contains_retrieved_document_content():
    prompt = build_rag_prompt(
        "What technologies are mentioned?",
        SAMPLE_CHUNKS
    )

    assert "Python and FastAPI" in prompt
    assert "ChromaDB" in prompt


def test_prompt_contains_source_information():
    prompt = build_rag_prompt(
        "What technologies are mentioned?",
        SAMPLE_CHUNKS
    )

    assert "sample.pdf" in prompt
    assert "2" in prompt
    assert "3" in prompt


def test_prompt_instructs_model_not_to_invent():
    prompt = build_rag_prompt(
        "What technologies are mentioned?",
        SAMPLE_CHUNKS
    )

    assert "do not invent" in prompt.lower()


def test_prompt_handles_empty_retrieved_chunks():
    prompt = build_rag_prompt(
        "What technologies are mentioned?",
        []
    )

    assert "What technologies are mentioned?" in prompt