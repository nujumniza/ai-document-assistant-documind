
import logging
import os
from uuid import uuid4

import pymupdf
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field

from app.services.chunking import chunk_text
from app.services.embeddings import (
    generate_embeddings,
    generate_query_embedding
)
from app.services.rag import (
    MockLLMProvider,
    GroqLLMProvider,
    build_rag_prompt
)
from app.services.vector_store import (
    store_chunks,
    search_chunks,
    list_documents,
    delete_document
)
from app.services.human_review import (
    review_incident,
    get_incident_reviews
)

# Load environment variables from the project .env file.
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Document Assistant",
    description="An AI-powered document question-answering system",
    version="0.1.0"
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PAGES = 100


@app.get("/documents")
def get_documents():
    """
    List all uploaded and indexed documents.
    """
    documents = list_documents()

    return {
        "total_documents": len(documents),
        "documents": documents
    }


@app.delete("/documents/{document_id}")
def remove_document(document_id: str):
    """
    Delete a document and all its indexed chunks.
    """
    deleted_chunks = delete_document(document_id)

    if deleted_chunks == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "deleted_chunks": deleted_chunks
    }

def create_llm_provider():
    """
    Select the LLM provider using the LLM_PROVIDER
    setting in the .env file.
    """

    provider_name = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    if provider_name == "mock":
        return MockLLMProvider()

    if provider_name == "groq":
        return GroqLLMProvider()

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider_name}"
    )


# Create the selected provider once when the application starts.
llm_provider = create_llm_provider()

PROVIDER_NAME = os.getenv(
    "LLM_PROVIDER", "mock"
).strip().lower()

IS_MOCK = isinstance(llm_provider, MockLLMProvider)


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10
    )

    document_id: str | None = None


@app.get("/")
async def root():
    return {
        "message": "AI Document Assistant API is running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "AI Document Assistant",
        "llm_provider": PROVIDER_NAME,
        "is_mock": IS_MOCK
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):

    # 1. Validate the file extension.
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # 2. Read the uploaded file with a size limit.
    file_content = await file.read(MAX_FILE_SIZE + 1)

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB size limit"
        )

    # 3. Extract text from the PDF page by page.
    try:
        pdf = pymupdf.open(
            stream=file_content,
            filetype="pdf"
        )

        with pdf:
            if pdf.needs_pass:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported"
                )

            if len(pdf) > MAX_PAGES:
                raise HTTPException(
                    status_code=400,
                    detail="PDF exceeds the 100-page limit"
                )

            extracted_pages = []

            for page_number, page in enumerate(pdf, start=1):
                page_text = page.get_text("text")

                extracted_pages.append({
                    "page": page_number,
                    "text": page_text
                })

    except pymupdf.FileDataError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF"
        )

    # 4. Combine extracted page text.
    full_text = "\n".join(
        page["text"] for page in extracted_pages
    )

    document_id = str(uuid4())

    # 5. Create chunks while retaining page information.
    document_chunks = []

    for page in extracted_pages:
        page_chunks = chunk_text(page["text"])

        for chunk_index, chunk in enumerate(
            page_chunks, start=1
        ):
            document_chunks.append({
                "chunk_id": (
                    f"{document_id}-"
                    f"page-{page['page']}-"
                    f"chunk-{chunk_index}"
                ),
                "page_number": page["page"],
                "chunk_index": chunk_index,
                "word_count": len(chunk.split()),
                "text": chunk
            })

    # 6. Generate embeddings and store chunks.
    embedded_chunks = generate_embeddings(document_chunks)

    stored_chunks = store_chunks(
        embedded_chunks=embedded_chunks,
        document_id=document_id,
        filename=file.filename
    )

    return {
        "document_id": document_id,
        "filename": file.filename,
        "total_pages": len(extracted_pages),
        "total_characters": len(full_text),
        "total_chunks": len(embedded_chunks),
        "stored_chunks": stored_chunks,
        "embedding_dimensions": 384,
        "storage_status": "success"
    }

# --------------------------------------------------
# RESOLVEIQ - ORGANISATION KNOWLEDGE BASE
# --------------------------------------------------

@app.post("/resolveiq/knowledge/upload")
async def upload_resolveiq_knowledge(
    organisation: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a PDF into an organisation-specific
    ResolveIQ knowledge base.
    """

    organisation_id = organisation.strip().casefold()

    if len(organisation_id) < 2:
        raise HTTPException(
            status_code=400,
            detail="A valid organisation name is required."
        )

    if len(organisation_id) > 150:
        raise HTTPException(
            status_code=400,
            detail="Organisation name is too long."
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_content = await file.read(MAX_FILE_SIZE + 1)

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB size limit."
        )

    try:
        pdf = pymupdf.open(
            stream=file_content,
            filetype="pdf"
        )

        with pdf:
            if pdf.needs_pass:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported."
                )

            if len(pdf) > MAX_PAGES:
                raise HTTPException(
                    status_code=400,
                    detail="PDF exceeds the 100-page limit."
                )

            extracted_pages = []

            for page_number, page in enumerate(pdf, start=1):
                page_text = page.get_text("text")

                extracted_pages.append({
                    "page": page_number,
                    "text": page_text
                })

    except pymupdf.FileDataError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF."
        )

    full_text = "\n".join(
        page["text"] for page in extracted_pages
    )

    if not full_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No extractable text was found in the PDF."
        )

    document_id = str(uuid4())

    document_chunks = []

    for page in extracted_pages:
        page_chunks = chunk_text(page["text"])

        for chunk_index, chunk in enumerate(page_chunks, start=1):
            document_chunks.append({
                "chunk_id": (
                    f"{document_id}-"
                    f"page-{page['page']}-"
                    f"chunk-{chunk_index}"
                ),
                "page_number": page["page"],
                "chunk_index": chunk_index,
                "word_count": len(chunk.split()),
                "text": chunk
            })

    embedded_chunks = generate_embeddings(document_chunks)

    stored_chunks = store_chunks(
        embedded_chunks=embedded_chunks,
        document_id=document_id,
        filename=file.filename,
        organisation_id=organisation_id
    )

    return {
        "message": "ResolveIQ knowledge document uploaded successfully.",
        "organisation_id": organisation_id,
        "document_id": document_id,
        "filename": file.filename,
        "total_pages": len(extracted_pages),
        "total_chunks": len(embedded_chunks),
        "stored_chunks": stored_chunks,
        "storage_status": "success"
    }
@app.post("/documents/search")
async def search_documents(request: SearchRequest):

    # 1. Convert the question into an embedding.
    query_embedding = generate_query_embedding(
        request.query
    )

    # 2. Search ChromaDB.
    matches = search_chunks(
        query_embedding=query_embedding,
        top_k=request.top_k,
        document_id=request.document_id
    )

    # 3. Return matching document sections.
    return {
        "query": request.query,
        "total_results": len(matches),
        "results": [
            {
                "chunk_id": match["chunk_id"],
                "text": match["text"],
                "filename": match["metadata"]["filename"],
                "document_id": match["metadata"]["document_id"],
                "page_number": match["metadata"]["page_number"],
                "chunk_index": match["metadata"]["chunk_index"],
                "distance": match["distance"]
            }
            for match in matches
        ]
    }


@app.post("/documents/ask")
async def ask_documents(request: SearchRequest):

    # 1. Convert the question into an embedding.
    query_embedding = generate_query_embedding(
        request.query
    )

    # 2. Retrieve relevant chunks from ChromaDB.
    retrieved_chunks = search_chunks(
        query_embedding=query_embedding,
        top_k=request.top_k,
        document_id=request.document_id
    )

    # 3. Handle cases where no relevant chunks exist.
    if not retrieved_chunks:
        return {
            "question": request.query,
            "answer": "No document content was found for this search.",
            "sources": [],
            "provider": PROVIDER_NAME,
            "is_mock": IS_MOCK
        }

    # 4. Build the RAG prompt.
    prompt = build_rag_prompt(
        question=request.query,
        retrieved_chunks=retrieved_chunks
    )

    # 5. Generate an answer using the selected provider.
    try:
        answer = llm_provider.generate(prompt)

    except Exception:
        logger.exception("LLM provider request failed")

        raise HTTPException(
            status_code=502,
            detail="The AI provider could not generate an answer. Check the server logs."
        )

    # 6. Return the answer and source information.
    return {
        "question": request.query,
        "answer": answer,
        "provider": PROVIDER_NAME,
        "is_mock": IS_MOCK,
        "retrieved_chunks": len(retrieved_chunks),
        "sources": [
            {
                "filename": chunk["metadata"]["filename"],
                "page_number": chunk["metadata"]["page_number"],
                "chunk_id": chunk["chunk_id"],
                "distance": chunk["distance"]
            }
            for chunk in retrieved_chunks
        ]
    }

# --------------------------------------------------
# RESOLVEIQ - INCIDENT INTELLIGENCE
# --------------------------------------------------

from typing import Literal

from app.services.incident_intelligence import (
    analyse_incident,
    get_incidents
)

class IncidentReviewRequest(BaseModel):
    decision: Literal["approved", "rejected"]

    reviewer: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    edited_response: str | None = Field(
        default=None,
        max_length=10000
    )
class IncidentRequest(BaseModel):

    organisation: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    subject: str = Field(
        ...,
        min_length=3,
        max_length=250
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000
    )

    severity: Literal[
        "low", "medium", "high", "critical"
    ]

    business_impact: Literal[
        "low", "medium", "high", "critical"
    ]

    urgency: Literal[
        "low", "medium", "high", "critical"
    ]

    affected_users: int = Field(
        default=1,
        ge=1,
        le=100000
    )


@app.post("/incidents/analyze")
async def analyse_customer_incident(request: IncidentRequest):

    try:
        result = analyse_incident(
            incident=request.dict(),
            llm_provider=llm_provider
        )

        return result

    except Exception:
        logger.exception("ResolveIQ incident analysis failed")

        raise HTTPException(
            status_code=502,
            detail=(
                "Incident analysis failed. "
                "Check the backend terminal for details."
            )
        )


@app.get("/incidents")
async def get_saved_incidents():

    incidents = get_incidents()

    return {
        "total_incidents": len(incidents),
        "incidents": incidents
    }

# --------------------------------------------------
# RESOLVEIQ - AGENTIC INVESTIGATION
# --------------------------------------------------

from app.services.incident_agent import (
    run_investigation_agent,
    get_investigations
)


@app.post("/incidents/{incident_id}/investigate")
async def investigate_incident(incident_id: str):

    try:
        return run_investigation_agent(
            incident_id=incident_id,
            llm_provider=llm_provider
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception:
        logger.exception("ResolveIQ agent investigation failed")

        raise HTTPException(
            status_code=502,
            detail=(
                "Agent investigation failed. "
                "Check the backend terminal."
            )
        )


@app.get("/incidents/{incident_id}/investigations")
async def get_incident_investigations(incident_id: str):

    try:
        investigations = get_investigations(incident_id)

        return {
            "incident_id": incident_id,
            "total_investigations": len(investigations),
            "investigations": investigations
        }

    except Exception:
        logger.exception("Could not retrieve investigations")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve investigations."
        )

@app.post("/incidents/{incident_id}/review")
async def review_customer_response(
    incident_id: str,
    request: IncidentReviewRequest
):
    try:
        return review_incident(
            incident_id=incident_id,
            decision=request.decision,
            reviewer=request.reviewer,
            edited_response=request.edited_response
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception:
        logger.exception("Incident review failed")

        raise HTTPException(
            status_code=500,
            detail="Could not save incident review."
        )


@app.get("/incidents/{incident_id}/reviews")
async def retrieve_incident_reviews(incident_id: str):

    return {
        "incident_id": incident_id,
        "reviews": get_incident_reviews(incident_id)
    }
