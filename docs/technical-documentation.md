# DocuMind AI — Technical Documentation

## 1. Purpose

DocuMind AI is a full-stack Retrieval-Augmented Generation (RAG) prototype. It allows a user to upload PDF files, index their contents, retrieve semantically relevant passages, and ask natural-language questions answered by a hosted LLM.

## 2. Runtime components

### Frontend

`frontend/streamlit_app.py`

Responsibilities:
- Render Dashboard, Document Library, and AI Assistant.
- Send PDF uploads to the backend using multipart HTTP.
- Retrieve document inventory and backend health.
- Submit question, selected document filter, and `top_k`.
- Render answers and returned source metadata.
- Maintain visible chat history in Streamlit session state.

**Current limitation:** previous chat messages are retained for display but are not sent to the backend as conversation history. Each request is therefore an independent retrieval-and-answer operation.

### Backend

`app/main.py`

Responsibilities:
- Expose REST endpoints.
- Validate and process uploads.
- Coordinate PDF extraction, chunking, embedding and vector storage.
- Perform retrieval and answer generation.
- List and delete indexed documents.

### PDF extraction

PyMuPDF extracts text from each page. Image-only/scanned PDFs may require OCR, which is not currently guaranteed by the prototype.

### Chunking

The current configuration uses approximately 200 words per chunk with 40 words of overlap. Chunking is page-aware: each page is chunked independently.

The overlap preserves some context around chunk boundaries. It increases the number of vectors and storage required.

### Embeddings

Model: `sentence-transformers/all-MiniLM-L6-v2`

- Used for both document chunks and query text.
- Produces 384-dimensional vectors.
- Model loading is cached in process memory.
- The vector collection expects consistent embedding dimensions and model semantics.

### Vector storage

ChromaDB persistent client; collection name: `document_chunks`.

- Cosine distance is used for similarity search.
- The application supplies query embeddings.
- Metadata supports document-level filtering and source display.
- Deletion is scoped by `document_id`.

The local data directory is `data/chroma/`. In hosted environments, configure durable storage or move to a managed vector database before treating uploaded content as persistent.

### LLM provider

The current configured provider is Groq, with model configured by `GROQ_MODEL`. The tested model setting was `openai/gpt-oss-20b`.

The API key is supplied through `GROQ_API_KEY`. Never commit this key or include it in logs, screenshots, issue reports, or public documentation.

## 3. API reference

The endpoint summary below reflects the prototype routes. Check `app/main.py` for the authoritative Pydantic request and response schemas before publishing exact JSON examples.

| Method | Path | Description |
|---|---|---|
| GET | `/` | API welcome response |
| GET | `/health` | Reports application/provider health |
| POST | `/documents/upload` | Accepts a PDF multipart upload and indexes it |
| GET | `/documents` | Lists documents reconstructed from chunk metadata |
| POST | `/documents/search` | Embeds a query and retrieves relevant chunks |
| POST | `/documents/ask` | Retrieves context and generates an answer |
| DELETE | `/documents/{document_id}` | Deletes all chunks for the selected document |

### Upload

`POST /documents/upload`

- Content type: `multipart/form-data`
- File type: PDF
- Prototype validation limits: 10 MB and 100 pages.
- Success metadata includes document ID, filename, page count and chunk count.

### Search

`POST /documents/search`

Search request fields include the query, `top_k`, and an optional `document_id` filter. The exact schema is defined in `app/main.py`.

### Ask

`POST /documents/ask`

The frontend currently sends:

```json
{
  "query": "What are the main findings?",
  "top_k": 3,
  "document_id": null
}
```

A `null` document ID means search across the full indexed collection. A selected ID restricts retrieval to that document.

The frontend expects an answer and may receive source metadata and an `is_mock` indicator. Verify the exact backend response model before changing field names.

### Delete

`DELETE /documents/{document_id}`

Deletes the vectors associated with a document ID. The prototype returns a deleted-chunk count and reports not-found when no chunks match.

## 4. Configuration

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | Selects the configured LLM provider |
| `GROQ_MODEL` | Groq model identifier |
| `GROQ_API_KEY` | Secret API credential |
| `API_BASE_URL` | Frontend base URL for the FastAPI backend |

Keep secrets in `.env` locally or the hosting provider's secret/environment-variable manager. Commit only `.env.example` with placeholder values.

## 5. Data lifecycle

1. Upload arrives at the API.
2. File validation runs before extraction.
3. Page text is extracted.
4. Text chunks and metadata are created.
5. Embeddings are generated.
6. Vector records are persisted.
7. Search queries retrieve chunk text and metadata.
8. The RAG layer builds a prompt.
9. The configured LLM returns an answer.
10. The UI renders answer and source references.
11. A delete request removes all vector records for a document ID.

The current application does not provide a separate original-PDF object store or a complete document lifecycle/audit subsystem.

## 6. Error handling

The frontend should display a user-friendly error when:
- The API cannot be reached.
- An upload is rejected.
- A document cannot be deleted.
- The ask endpoint fails.

Before a public release, improve error responses so the UI can distinguish invalid PDFs, size/page-limit violations, provider quota/rate errors, timeouts, and internal server errors without exposing secrets or stack traces.

## 7. Security and privacy considerations

This prototype is not a production medical, legal, financial, or enterprise document platform.

Before real sensitive data is used, implement:
- Authentication and authorization.
- Per-user or per-tenant document isolation.
- Upload quotas and rate limiting.
- Strict file validation and safe temporary-file handling.
- Secrets management and secret redaction.
- HTTPS for all public traffic.
- Retention/deletion policy and backups.
- Prompt-injection-aware handling of retrieved document content.
- Monitoring and audit logging.
- Privacy review of the external LLM provider and data-processing terms.

**Hosted LLM data flow:** retrieved excerpts included in the prompt are sent to Groq. Use synthetic/redacted documents in public demonstrations unless the data owner has approved that processing.

## 8. Known limitations and future work

| Area | Current state | Possible next improvement |
|---|---|---|
| Conversation | Display-only history | Pass bounded chat context into RAG |
| Retrieval | Vector similarity top-k | Evaluate hybrid retrieval and reranking |
| Evaluation | Essential unit/API tests | Build a labelled retrieval/answer evaluation set |
| PDFs | Text extraction | OCR support for scanned documents |
| Security | Basic validation and prompt guidance | Auth, tenant isolation, injection controls |
| Operations | Local persistent ChromaDB | Durable hosted storage, backups and monitoring |
| Scale | Single-process prototype | Background ingestion and managed vector storage |

## 9. Test baseline

The prototype currently has 17 essential tests across:
- API health and core search/ask behavior.
- Empty and short text handling.
- Chunk count and overlap behavior.
- Invalid chunk parameters.
- RAG prompt construction and empty retrieval context.

Run:

```bash
pytest -q
```

Passing these tests is a useful baseline, not proof of production readiness.
