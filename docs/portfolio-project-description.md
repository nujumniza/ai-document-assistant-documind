# ResolveIQ — Portfolio Project Description

## Project title

**ResolveIQ — Agentic AI Service Operations & Customer Support Platform**

ResolveIQ is a full-stack AI application that helps support teams understand customer incidents, assess priority, retrieve relevant organisational knowledge, investigate issues using AI tools, and prepare customer responses for human review.

It includes **DocuMind AI**, an integrated Retrieval-Augmented Generation (RAG) capability for searching PDF documents and answering questions with source-page evidence.

## Short description

ResolveIQ combines incident intelligence, agentic AI investigation, organisation-specific knowledge retrieval and human approval in a single support workflow.

The platform analyses customer-reported incidents, classifies sentiment and category, calculates priority using configurable rule-based inputs, generates response drafts, and uses a tool-calling AI agent to retrieve relevant historical incidents, support policies and knowledge-base evidence.

Support staff remain in control of the final decision. Investigation findings and customer responses are presented for human review; the application does not automatically send emails or perform external system changes.

## Key capabilities

### 1. Incident intelligence

- Accepts customer incident information through a simulated support workflow.
- Generates an AI-assisted incident summary.
- Identifies issue category and customer sentiment.
- Summarises reported business impact.
- Calculates priority using severity, impact and urgency rules.
- Recommends next actions.
- Drafts a professional customer response for review.

Priority is calculated using application rules rather than allowing the language model to decide the final priority from sentiment alone.

### 2. Agentic AI investigation

- Uses Groq tool calling to coordinate an investigation workflow.
- Retrieves relevant historical incidents for the same organisation and customer.
- Retrieves the applicable demonstration support policy.
- Searches organisation-specific knowledge-base documents.
- Combines retrieved evidence into an investigation report.
- Records the tools used and their execution trace.
- Limits tool execution to an allowlisted set of read-only functions and a bounded number of interactions.

The agent supports investigation and recommendations. It does not claim to diagnose systems or perform checks for which the application has no access or evidence.

### 3. Organisation-specific knowledge retrieval

- Supports PDF knowledge-base uploads associated with an organisation.
- Extracts document text and creates searchable chunks.
- Generates embeddings using Sentence Transformers.
- Stores and retrieves vectors through ChromaDB.
- Filters knowledge retrieval by organisation.
- Provides retrieved document evidence to the investigation workflow.

### 4. Human review and approval

- Presents generated customer responses for review.
- Allows a reviewer to edit the response.
- Records approval or rejection decisions.
- Stores reviewer information and the final reviewed response.
- Maintains a review history for the incident.

Approval records a human decision; it does not send an email automatically.

### 5. DocuMind AI document assistant

- Uploads and processes PDF documents.
- Extracts text while retaining page information.
- Splits extracted text into overlapping chunks.
- Generates semantic embeddings.
- Stores document vectors in ChromaDB.
- Retrieves relevant passages for natural-language questions.
- Generates answers using retrieved context and a Groq-hosted LLM.
- Displays source evidence, including filenames and page numbers.
- Supports document listing and deletion.

## Technology stack

| Area                        | Technology                              |
| --------------------------- | --------------------------------------- |
| Backend API                 | Python, FastAPI                         |
| Frontend                    | Streamlit                               |
| LLM provider                | Groq API                                |
| LLM model configuration     | `openai/gpt-oss-20b`                    |
| Agent tool calling          | Groq tool/function calling              |
| Embeddings                  | Sentence Transformers                   |
| Embedding model             | `all-MiniLM-L6-v2`                      |
| Vector database             | ChromaDB                                |
| Incident and review storage | SQLite                                  |
| PDF extraction              | PyMuPDF                                 |
| API and data validation     | Pydantic                                |
| Configuration               | Python environment variables and `.env` |
| Testing                     | Pytest and HTTPX                        |

## Resume / portfolio bullets

- Built **ResolveIQ**, a full-stack agentic AI support platform using Python, FastAPI and Streamlit to analyse customer incidents, classify issues, calculate priority, and generate customer response drafts.
- Implemented a tool-calling AI investigation workflow using Groq, with allowlisted read-only tools for historical incident retrieval, support policy lookup and organisation-specific knowledge search.
- Integrated a RAG pipeline using Sentence Transformers and ChromaDB to retrieve organisation-specific PDF knowledge and provide evidence-backed investigation context.
- Developed a human-in-the-loop review workflow that supports response editing, approval and rejection, with decisions and review history persisted in SQLite.
- Integrated **DocuMind AI**, a document question-answering capability using PDF extraction, page-aware chunking, semantic search and source-attributed LLM responses.
- Designed a bounded investigation workflow that records tool execution traces and distinguishes retrieved evidence from recommendations and unverified assumptions.

## Interview explanation

### What problem does ResolveIQ solve?

Support teams receive incidents through customer messages, but understanding the issue, assessing urgency, checking previous incidents, finding relevant procedures and preparing an accurate response can take time.

ResolveIQ brings these activities into one workflow. It helps support staff understand the reported problem, retrieve relevant evidence, investigate using approved tools and prepare a response for human review.

### Why did you build an agent rather than use a single LLM prompt?

A single prompt can generate a summary or recommendation, but it cannot independently retrieve information from application data sources unless those sources are provided to it.

The investigation agent can select from a defined set of tools. It can retrieve historical incidents, look up support policies and search the organisation's knowledge base. It then uses the returned information to prepare a more evidence-informed investigation report.

The agent is bounded: it uses an allowlist of read-only tools and has a maximum interaction limit.

### How does the agent know which tools to use?

The application defines the available tools and their descriptions using Groq-compatible tool schemas.

The model can request a tool call based on the incident and the information it needs. The application validates the requested tool against its allowlist, executes the corresponding function, and returns the result to the model.

The model does not directly execute arbitrary Python code or access unrestricted application resources.

### How does the RAG component work?

The application extracts text from PDF documents, splits it into overlapping chunks, and generates an embedding for each chunk.

ChromaDB stores the vectors and their associated metadata. When a user asks a question, the application generates a query embedding and retrieves semantically relevant passages.

The retrieved passages are provided to the LLM as context. The answer can then be displayed with source information such as document filename and page number.

### Why use RAG instead of sending the entire PDF to the model?

RAG retrieves a smaller set of relevant passages for each question rather than sending the entire document.

This helps reduce irrelevant context, supports larger document collections, and makes it possible to show which source passages informed an answer.

### What is the role of embeddings?

Embeddings convert text into numerical vectors that represent semantic meaning.

This allows the application to retrieve passages that are conceptually related to a question, even when the question and document use different wording.

### Why ChromaDB?

ChromaDB provides vector storage, metadata filtering and similarity search with a relatively straightforward development setup.

In this project it stores document chunks and supports retrieval for both DocuMind AI and ResolveIQ's organisation-specific knowledge search.

### How is incident priority calculated?

The application calculates priority using rule-based inputs for severity, business impact and urgency.

The language model assists with understanding and summarising the incident, but the priority calculation is handled by application logic. This keeps the final priority decision more consistent and easier to explain than relying on an unconstrained LLM response.

### Why include human approval?

AI-generated responses and recommendations can contain mistakes or incomplete information.

The human review workflow allows a support representative to inspect and edit a response before approving or rejecting it. The decision is stored in the review history.

The current prototype does not automatically send customer emails.

### How do you handle information that has not been verified?

The investigation workflow is designed to distinguish:

- Information reported by the customer.
- Evidence retrieved from application records.
- Relevant knowledge-base instructions.
- AI-generated hypotheses and recommendations.
- Information that remains unknown.

The application should not claim that a technical check, diagnosis or escalation has occurred unless the available evidence confirms it.

### What are the current limitations?

ResolveIQ is a portfolio prototype rather than a production-ready support platform.

Current limitations include:

- No authentication or production-grade access control.
- No real email inbox integration or automatic email sending.
- No direct integration with external monitoring, CRM or ticketing platforms.
- No access to third-party vendor infrastructure or diagnostic systems.
- SQLite is used for incident and review records.
- Deployment requires durable storage if uploaded documents and application records must persist.
- AI outputs require human review.
- Retrieval quality and agent behaviour need broader evaluation using a labelled test dataset.
- Production use would require stronger security, tenant isolation, backup, monitoring and operational controls.

### How would you improve it?

Potential future improvements include:

- Authentication, role-based access control and verified tenant isolation.
- More extensive retrieval and agent evaluation using labelled datasets.
- Better retrieval through hybrid search and reranking.
- OCR support for scanned PDFs.
- Managed database and durable object storage.
- Production monitoring, structured logging and backup procedures.
- Optional integrations with approved ticketing and email platforms, with explicit human approval controls.

## Project positioning

ResolveIQ demonstrates practical application of AI in a business workflow rather than only a standalone chatbot or document question-answering demonstration.

It combines:

- LLM-based incident understanding.
- Rule-based business logic.
- Tool-calling agent orchestration.
- Retrieval-Augmented Generation.
- Persistent application records.
- Human-in-the-loop decision-making.
- A user-facing application built with Streamlit and FastAPI.

It is suitable as a portfolio project demonstrating skills relevant to AI Application Developer, AI Solutions Specialist and AI Product Specialist roles.

## Repository

GitHub: https://github.com/nujumniza/ai-document-assistant-documind
