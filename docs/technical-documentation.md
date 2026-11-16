# ResolveIQ & DocuMind AI — Technical Documentation

## 1. Purpose

This document describes the technical implementation of ResolveIQ and its integrated DocuMind AI document intelligence capability.

The application is a Python-based AI platform combining:

- Retrieval-Augmented Generation (RAG).
- AI-assisted incident analysis.
- A tool-using AI investigation agent.
- Organisation-specific knowledge retrieval.
- Human review and approval workflows.
- PDF document ingestion and semantic search.

The application uses FastAPI for backend services and Streamlit for the user interface.

Groq provides hosted LLM inference, Sentence Transformers generates embeddings, ChromaDB stores document vectors, and SQLite stores operational records.

## 2. Runtime Components

### 2.1 Frontend

**File:** `frontend/streamlit_app.py`

The Streamlit frontend provides the DocuMind AI and ResolveIQ interfaces.

Responsibilities include:

- Render the application dashboard.
- Display document inventory and upload controls.
- Submit document questions and display answers.
- Display source evidence for retrieved passages.
- Submit customer incidents for analysis.
- Display incident classifications, sentiment, summaries, and priorities.
- Allow users to select incidents for investigation.
- Display investigation reports and tool execution information.
- Allow reviewers to edit, approve, or reject customer response drafts.
- Display review and investigation histories.
- Maintain interface state through Streamlit session state.

The frontend communicates with FastAPI using HTTP requests.

**Current limitation:** Chat messages are retained for display in Streamlit session state but are not sent as persistent conversational context to the backend. Separate question requests are independent retrieval-and-answer operations.

### 2.2 Backend

**File:** `app/main.py`

FastAPI provides the REST API and coordinates backend operations.

Responsibilities include:

- Expose document and ResolveIQ endpoints.
- Validate incoming requests and uploads.
- Coordinate PDF extraction, chunking, embedding, and vector storage.
- Execute document retrieval and answer generation.
- Process customer incidents.
- Initiate agentic investigations.
- Handle human review decisions.
- Retrieve incident, investigation, and review records.
- Manage organisation-specific knowledge uploads.

### 2.3 Service Modules

| File                                    | Responsibility                                           |
| --------------------------------------- | -------------------------------------------------------- |
| `app/services/chunking.py`              | Split extracted PDF text into overlapping chunks         |
| `app/services/embeddings.py`            | Generate text embeddings                                 |
| `app/services/vector_store.py`          | ChromaDB storage, retrieval, listing, and deletion       |
| `app/services/rag.py`                   | Semantic retrieval and grounded answer generation        |
| `app/services/incident_intelligence.py` | Incident analysis, priority calculation, and persistence |
| `app/services/incident_agent.py`        | Tool-using investigation agent and retrieval tools       |
| `app/services/human_review.py`          | Human review decisions and review history                |

## 3. DocuMind AI — Document Intelligence

### 3.1 PDF Extraction

PyMuPDF extracts text from uploaded PDF documents.

Text is extracted page by page to preserve source-page information.

Image-only or scanned PDFs may require OCR. OCR is not currently guaranteed by the prototype.

### 3.2 Chunking

The current configuration uses approximately:

- 200 words per chunk.
- 40 words of overlap.

Chunking is page-aware: each page is processed independently.

The overlap preserves some context around chunk boundaries. It also increases the number of vectors and the storage required.

### 3.3 Embeddings

**Model:** `sentence-transformers/all-MiniLM-L6-v2`

Implementation details:

- Used for document chunks and query text.
- Produces 384-dimensional vectors.
- Model loading is cached in process memory.
- The same embedding model must be used for document indexing and query encoding.

The embedding service exposes query embedding functionality through `generate_query_embedding()`.

### 3.4 Vector Storage

**Technology:** ChromaDB

**Collection:** `document_chunks`

**Local persistence directory:** `data/chroma/`

Responsibilities include:

- Store document chunk embeddings.
- Store chunk text and source metadata.
- Retrieve semantically similar chunks.
- Filter retrieval by document identifier.
- Filter organisation-specific knowledge searches.
- List indexed documents.
- Delete document-associated chunks.

The collection uses cosine distance for similarity retrieval.

Distance is a ranking signal, not a calibrated probability or answer-confidence percentage.

### 3.5 Document Metadata

Logical metadata includes:

| Field             | Purpose                                          |
| ----------------- | ------------------------------------------------ |
| `document_id`     | Groups chunks belonging to one uploaded document |
| `filename`        | Original uploaded filename                       |
| `page_number`     | Source page reference                            |
| `organisation_id` | Organisation scope, where supplied               |
| Document content  | Extracted chunk text                             |
| Embedding         | Numerical representation of the chunk            |

The document inventory is reconstructed from stored chunk metadata by grouping records by document ID and calculating chunk counts and distinct page counts.

### 3.6 RAG Question Answering

The document question-answering workflow:

1. Receives a user question.
2. Generates an embedding for the question.
3. Searches ChromaDB for relevant chunks.
4. Applies an optional document ID filter.
5. Passes retrieved text and source information to the RAG service.
6. Constructs a context-grounded prompt.
7. Sends the prompt to the configured LLM provider.
8. Returns the generated answer and available source metadata.

The frontend displays the answer and supporting document evidence.

Retrieved context is supplied as information rather than trusted instructions. Prompt instructions alone do not provide complete protection against prompt injection.

## 4. ResolveIQ — Incident Intelligence

**File:** `app/services/incident_intelligence.py`

Incident intelligence processes customer-reported information and generates an initial incident analysis.

### 4.1 Incident Processing

The workflow includes:

1. Receive incident information through the API.
2. Prepare the incident details for AI analysis.
3. Use the configured LLM to assist with:
   - Incident categorisation.
   - Customer sentiment identification.
   - Incident summarisation.
   - Business-impact assessment.
   - Recommended actions.
   - Customer response drafting.
4. Calculate priority using Python business rules.
5. Store the incident and analysis in SQLite.
6. Return the analysis to the frontend.

### 4.2 Priority Calculation

Priority is calculated independently of customer sentiment.

The current demonstration implementation assigns numerical values to severity, impact, and urgency and combines them into a priority score.

| Priority | Score threshold | Demonstration response target |
| -------- | --------------: | ----------------------------: |
| P1       |    10 or higher |                        1 hour |
| P2       |             7–9 |                       4 hours |
| P3       |             4–6 |                      24 hours |
| P4       |         Below 4 |                      72 hours |

These response targets represent demonstration support-policy values, not verified contractual SLAs.

### 4.3 Customer Response Drafting

The LLM generates a proposed customer response based on the incident information.

The response-generation instructions include safeguards against:

- Treating customer-provided instructions as trusted system instructions.
- Claiming technical investigations have occurred without supporting evidence.
- Inventing technical findings.
- Making unsupported resolution-time commitments.
- Presenting an unverified diagnosis as fact.

The response is a draft for human review. It is not sent automatically.

## 5. ResolveIQ — Agentic AI Investigation

**File:** `app/services/incident_agent.py`

ResolveIQ implements a central tool-using AI investigation agent using Groq function/tool calling.

The agent retrieves information through predefined application tools rather than relying exclusively on the original customer incident description.

### 5.1 Available Tools

| Tool                            | Function                                   | Responsibility                                                    |
| ------------------------------- | ------------------------------------------ | ----------------------------------------------------------------- |
| `get_customer_incident_history` | `get_customer_incident_history(arguments)` | Retrieve earlier incidents for the same organisation and customer |
| `get_support_policy`            | `get_support_policy(arguments)`            | Retrieve demonstration support-policy information                 |
| `search_organisation_knowledge` | `search_organisation_knowledge(arguments)` | Search organisation-specific knowledge documents                  |

### 5.2 Tool Execution

The investigation workflow:

1. Receives an incident ID.
2. Retrieves the incident record from SQLite.
3. Prepares the incident context and available tool definitions.
4. Sends the request to the Groq LLM.
5. Receives a tool-call request when additional information is needed.
6. Validates the requested tool against the application's available tool allowlist.
7. Executes the corresponding retrieval function.
8. Returns tool results to the LLM.
9. Continues the investigation using the retrieved evidence.
10. Generates an investigation report.
11. Stores the report, tools used, and tool trace in SQLite.

Tool interactions are bounded by a configured maximum of five interactions.

### 5.3 Historical Incident Retrieval

Historical incidents are retrieved using organisation and customer matching.

The query:

- Matches organisation and customer names case-insensitively.
- Excludes the current incident.
- Excludes incidents created after the current incident.
- Retrieves up to five relevant earlier records.

This prevents later-created incidents from being presented as historical evidence for an earlier incident.

### 5.4 Organisation-Specific Knowledge Retrieval

The investigation agent retrieves the organisation identifier from the incident record.

It then:

1. Normalises the organisation identifier.
2. Generates an embedding for the investigation query.
3. Searches ChromaDB using the organisation filter.
4. Retrieves relevant document chunks.
5. Returns available source information, including filename, page number, content excerpt, and retrieval distance.

This provides application-level organisation-scoped retrieval for the demonstration.

It is not a substitute for complete production-grade tenant isolation and access control.

### 5.5 Investigation Evidence and Safeguards

The investigation workflow is designed to distinguish:

- Customer-reported information.
- Information retrieved from incident records.
- Support-policy information.
- Organisation knowledge-document evidence.
- Hypotheses and unknowns.

The agent has access to predefined read-only retrieval tools.

It does not have unrestricted access to external vendor infrastructure, monitoring systems, customer environments, or third-party APIs.

It cannot independently perform external diagnostics or execute operational changes.

## 6. ResolveIQ — Human Review

**File:** `app/services/human_review.py`

The human review service manages approval and rejection of AI-generated customer responses.

### 6.1 Review Workflow

1. Retrieve the selected incident.
2. Display the AI-generated customer response.
3. Allow the reviewer to edit the response.
4. Accept an approval or rejection decision.
5. Record the reviewer and decision.
6. Store the final response associated with the review.
7. Make the review history available through the API.

### 6.2 Review Records

The SQLite review table stores information such as:

- Review identifier.
- Incident identifier.
- Review decision.
- Reviewer.
- Edited or final response.
- Review timestamp.

The current implementation records approval without sending an email. The review record explicitly reflects that email has not been sent.

Human approval and external communication are separate operations.

## 7. Database and Persistence

The application uses two persistence systems.

### 7.1 SQLite

**Database:** `data/resolveiq.db`

SQLite stores structured operational records.

| Table              | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| `incidents`        | Customer incident details, AI analysis, priority, and status |
| `investigations`   | Investigation reports and associated tool information        |
| `incident_reviews` | Human approval/rejection decisions and review history        |

The service modules initialise and access the database through their database functions.

### 7.2 ChromaDB

ChromaDB stores document chunks, embeddings, and associated metadata.

The same vector collection supports:

- General document search.
- Document question answering.
- Organisation-specific knowledge retrieval for ResolveIQ.

### 7.3 Data Persistence Considerations

Local runtime data is stored under the project's `data/` directory.

The directory contains application-generated databases and vector-store data and should not be treated as source code.

For hosted deployment, persistent storage must be configured for both SQLite and ChromaDB. A hosting platform with ephemeral storage is not suitable unless an appropriate durable storage solution is provided.

## 8. API Reference

The following endpoint summary describes the implemented application routes. Exact request and response schemas should be checked in `app/main.py` and the interactive FastAPI documentation before publishing detailed API examples.

### 8.1 General and Document Endpoints

| Method | Endpoint                   | Description                        |
| ------ | -------------------------- | ---------------------------------- |
| GET    | `/`                        | API welcome response               |
| GET    | `/health`                  | Application/provider health        |
| POST   | `/documents/upload`        | Upload and index a PDF             |
| GET    | `/documents`               | List indexed documents             |
| POST   | `/documents/search`        | Retrieve relevant document chunks  |
| POST   | `/documents/ask`           | Generate a context-grounded answer |
| DELETE | `/documents/{document_id}` | Delete document-associated chunks  |

### 8.2 ResolveIQ Endpoints

| Method | Endpoint                                  | Description                            |
| ------ | ----------------------------------------- | -------------------------------------- |
| POST   | `/incidents/analyze`                      | Analyse and record a customer incident |
| GET    | `/incidents`                              | Retrieve recorded incidents            |
| POST   | `/incidents/{incident_id}/investigate`    | Run the investigation agent            |
| GET    | `/incidents/{incident_id}/investigations` | Retrieve investigation history         |
| POST   | `/incidents/{incident_id}/review`         | Record a human review decision         |
| GET    | `/incidents/{incident_id}/reviews`        | Retrieve review history                |
| POST   | `/resolveiq/knowledge/upload`             | Upload organisation-specific knowledge |

FastAPI Swagger UI is available at:

`http://127.0.0.1:8000/docs`

## 9. Configuration

The application uses environment variables for runtime configuration.

| Variable       | Purpose                                   |
| -------------- | ----------------------------------------- |
| `LLM_PROVIDER` | Selects the configured LLM provider       |
| `GROQ_MODEL`   | Groq model identifier                     |
| `GROQ_API_KEY` | Groq API credential                       |
| `API_BASE_URL` | Frontend base URL for the FastAPI backend |

The tested model setting was:

`openai/gpt-oss-20b`

The frontend defaults to the local FastAPI address when `API_BASE_URL` is not set.

Example configuration:

```env
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=your_groq_api_key
```

Keep secrets in a local `.env` file or the hosting provider's secret manager.

Commit only `.env.example` with placeholder values. Never expose API keys in source code, logs, screenshots, or public documentation.

## 10. Data Lifecycle

### Document lifecycle

1. PDF upload reaches FastAPI.
2. File validation runs.
3. PyMuPDF extracts page text.
4. The chunking service generates overlapping chunks.
5. Sentence Transformers generates embeddings.
6. ChromaDB persists vectors and metadata.
7. Search requests retrieve relevant chunks.
8. The RAG service constructs a grounded prompt.
9. Groq generates an answer.
10. The frontend displays the answer and source references.
11. Document deletion removes associated vector records.

### Incident lifecycle

1. Customer incident information is submitted.
2. The incident intelligence service generates an analysis.
3. Python rules calculate priority.
4. The incident and analysis are stored in SQLite.
5. A support user can initiate an investigation.
6. The investigation agent retrieves historical records, policy information, and knowledge evidence.
7. The investigation report and tool trace are stored in SQLite.
8. A reviewer edits, approves, or rejects the customer response.
9. The review decision is stored and made available through review history.

## 11. Error Handling

The frontend should provide understandable feedback when:

- The backend cannot be reached.
- A PDF upload is rejected.
- A document cannot be retrieved or deleted.
- An LLM request fails.
- An incident analysis request fails.
- An investigation cannot be completed.
- A review request fails.

Before production use, improve error handling so the frontend can distinguish validation failures, provider quota or rate-limit errors, timeouts, and internal server errors without exposing secrets or stack traces.

## 12. Security and Privacy Considerations

This application is a portfolio demonstration, not a production-ready medical, legal, financial, or enterprise document platform.

Before processing real sensitive data, implement:

- User authentication and authorisation.
- Role-based access control.
- Production-grade organisation and tenant isolation.
- Upload quotas and rate limiting.
- Strict file validation and safe temporary-file handling.
- Secure secret management and redaction.
- HTTPS for public communication.
- Retention, deletion, and backup policies.
- Prompt-injection-aware handling of customer and retrieved document content.
- Audit logging and monitoring.
- Access controls for incident and review records.

### Hosted LLM Data Flow

Document excerpts, incident information, and investigation context may be sent to Groq for inference.

Use synthetic or redacted information in public demonstrations unless the data owner has approved the relevant data processing.

### Agent Tool Security

The investigation agent is restricted to predefined application retrieval tools. It does not have unrestricted shell access, external system control, or autonomous email-sending capabilities.

## 13. Known Limitations and Future Work

| Area                  | Current implementation               | Possible improvement                                   |
| --------------------- | ------------------------------------ | ------------------------------------------------------ |
| Conversation          | Display-only chat history            | Pass bounded conversation context into RAG             |
| Retrieval             | Vector similarity top-k              | Evaluate hybrid retrieval and reranking                |
| Evaluation            | Essential application tests          | Add labelled retrieval and answer evaluation datasets  |
| PDF processing        | Text extraction                      | Add OCR for scanned PDFs                               |
| Incident intelligence | Demonstration priority rules         | Configurable organisation-specific policies            |
| Investigation         | Bounded tool-using agent             | Expand evaluation and tool reliability                 |
| Security              | Basic validation and prompt guidance | Authentication, access controls, and tenant isolation  |
| Email                 | Human-reviewed response drafts       | Controlled email integration with explicit permissions |
| Operations            | Local SQLite and persistent ChromaDB | Managed databases, backups, and monitoring             |
| Scale                 | Single-process prototype             | Background ingestion and distributed processing        |

## 14. Test Baseline

The existing prototype test baseline contains 17 essential tests covering areas including:

- API health and core search/answer behaviour.
- Empty and short text handling.
- Chunk count and overlap behaviour.
- Invalid chunk parameters.
- RAG prompt construction.
- Empty retrieval context.

Run the test suite using:

```bash
pytest -q
```

Passing these tests provides a useful development baseline. It does not establish production readiness or guarantee the correctness of every LLM-generated answer and agent investigation.

## 15. Technical Summary

ResolveIQ combines three complementary capabilities:

1. **Incident intelligence:** AI-assisted analysis, business-rule priority calculation, and customer response drafting.
2. **Agentic investigation:** Tool-based retrieval of historical incidents, support policies, and organisation-specific knowledge.
3. **Document intelligence:** Semantic search and RAG-based question answering over PDF documents.

Human review remains part of the operational workflow, keeping AI-generated recommendations separate from authorised customer communication and external actions.
