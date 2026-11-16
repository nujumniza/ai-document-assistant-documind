# ResolveIQ — Deployment Guide

## Recommended portfolio deployment topology

Deploy the Streamlit frontend and FastAPI backend separately:

- **Frontend:** Streamlit Community Cloud.
- **Backend:** A Python web-service host such as Render.
- **Vector database:** ChromaDB on the backend's durable mounted storage.
- **Incident database:** SQLite on the same durable storage.
- **LLM:** Groq API, configured through backend environment variables.
- **Document processing:** PDF extraction and embedding generation performed by the backend.

ResolveIQ includes DocuMind AI's document RAG capability. Both applications use the same FastAPI backend and ChromaDB collection.

This guide uses Render as an example backend host. Confirm current plan pricing, resource limits, Python compatibility and persistent-disk eligibility before creating a service.

## Critical storage warning

The application stores data in two locations:

- `data/chroma/` — ChromaDB vector data, including indexed document chunks.
- `data/resolveiq.db` — SQLite records for incidents, investigations and human reviews.

Render web services use an ephemeral filesystem by default. Without durable storage, uploaded document indexes and SQLite records may be lost after a restart or redeployment.

If you use a Render persistent disk, mount it at:

```text
/opt/render/project/src/data
```

This assumes the service working directory is the repository root and the application uses the relative paths described above. Verify the actual working directory and database paths in the deployed logs.

Persistent disks are not available on every free service configuration. Check current Render pricing and eligibility before relying on durable storage.

For a temporary portfolio demonstration, you may deploy with sample data and clearly disclose that uploaded data and incident records are not guaranteed to persist. Do not describe the deployment as durable until persistence has been tested.

## Phase 1 — Prepare the repository

1. Confirm ResolveIQ and DocuMind AI run locally.
2. Run the essential test suite.
3. Keep backend dependencies in the root `requirements.txt`.
4. Keep frontend-only dependencies in `frontend/requirements.txt`.
5. Add or update `.env.example` with placeholder values only.
6. Confirm `.env`, virtual environments, local databases and generated vector data are ignored by Git.
7. Remove personal CVs, private PDFs, API keys, local databases and other private data from the repository.
8. Review the Git diff and repository history for accidentally committed secrets.
9. Commit and push the project to GitHub when ready.

Suggested `.gitignore` additions:

```gitignore
.env
.streamlit/secrets.toml
.venv/
.venv*/
__pycache__/
*.py[cod]
.pytest_cache/
data/chroma/
data/resolveiq.db
documents/*
!documents/.gitkeep
```

Only add `documents/*` if that folder is intended to contain private or user-uploaded documents. Do not ignore sample documents that you intentionally want to publish.

If you use another location for the SQLite database, update the ignore rule accordingly.

## Phase 2 — Configure the frontend API URL

The Streamlit frontend must call the deployed FastAPI backend rather than the local development address.

At the top of `frontend/streamlit_app.py`, ensure `os` is imported:

```python
import os
```

Use this configuration:

```python
def get_api_base_url():
    value = os.getenv("API_BASE_URL")

    if value:
        return value.rstrip("/")

    try:
        return st.secrets["API_BASE_URL"].rstrip("/")
    except Exception:
        return "http://127.0.0.1:8000"


API_BASE_URL = get_api_base_url()
```

This supports:

- Local development using `http://127.0.0.1:8000`.
- Hosted deployment using an environment variable.
- Streamlit Community Cloud secrets as a fallback.

If the existing frontend already has an equivalent configuration, retain it rather than adding a duplicate.

## Phase 3 — Prepare the backend

The backend must bind to `0.0.0.0` and use the port provided by the hosting platform.

**Render build command:**

```bash
pip install -r requirements.txt
```

**Render start command:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure these environment variables in the backend hosting dashboard:

```text
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=<your-secret>
```

Use the exact variable names expected by the application. Do not put the real API key in a committed file.

### Python version

Python 3.12 is a conservative deployment target to evaluate for this dependency stack. Confirm compatibility with the installed versions of FastAPI, ChromaDB, Sentence Transformers, PyTorch and the Groq SDK before deploying.

Do not assume that the local Python 3.14 environment will be supported by every dependency or hosting platform.

### Persistent storage

If a Render persistent disk is available and you need uploaded documents and incident records to survive restarts, mount it at:

```text
/opt/render/project/src/data
```

The application currently uses:

```text
data/chroma/
data/resolveiq.db
```

Both locations should therefore be inside the mounted directory.

After deployment, verify that:

- ChromaDB is writing to the mounted directory.
- SQLite is creating or updating `resolveiq.db` there.
- The application can read existing records after a restart.

Do not assume persistence works solely because the service starts successfully.

### CORS

The current Streamlit frontend calls the API using Python `requests` from the Streamlit server-side process. This is not a browser JavaScript fetch, so CORS is not normally required for this frontend-to-backend communication.

If a browser-based frontend is introduced later, configure explicit allowed origins rather than using `*` for an authenticated production application.

## Phase 4 — Deploy the backend

1. Create a Python web service using the GitHub repository.
2. Select a supported Python runtime.
3. Set the build and start commands.
4. Configure the required environment variables.
5. Configure persistent storage if document indexes and incident records must survive restarts.
6. Deploy the service.
7. Open the health endpoint:

```text
https://YOUR-BACKEND.onrender.com/health
```

8. Confirm that the application reports a healthy status and the expected LLM provider.
9. Check the service logs for:
   - Embedding model loading errors.
   - ChromaDB path or permission errors.
   - SQLite initialization errors.
   - Groq authentication or API errors.

Do not publish the backend URL as a working demo until the health check succeeds.

## Phase 5 — Deploy the Streamlit frontend

1. Confirm the complete project is pushed to GitHub.
2. Sign in to Streamlit Community Cloud using GitHub.
3. Create a new application from the repository.
4. Set the entrypoint to:

```text
frontend/streamlit_app.py
```

5. Select a compatible Python version, such as Python 3.12, if available.
6. Configure the frontend secret:

```toml
API_BASE_URL = "https://YOUR-BACKEND.onrender.com"
```

The frontend configuration in Phase 2 reads this value from Streamlit secrets when an environment variable is not available.

7. Deploy the application.
8. Open the public Streamlit URL.
9. Confirm that the frontend can communicate with the hosted backend.

Keep the Groq API key on the backend only. The frontend needs the backend URL, not the LLM provider secret.

## Phase 6 — Hosted smoke test

Use synthetic incident information and a small, non-sensitive sample PDF.

### General application checks

- [ ] Streamlit application loads.
- [ ] Backend health check succeeds.
- [ ] The configured AI provider is displayed correctly.
- [ ] The frontend can communicate with the backend.
- [ ] No secrets are exposed in the frontend or repository.

### DocuMind AI checks

- [ ] Upload a sample PDF.
- [ ] Confirm page and chunk counts.
- [ ] Ask a question whose answer is clearly present in the sample.
- [ ] Confirm the answer is generated using the configured provider, not mock mode.
- [ ] Expand source evidence and verify the filename and page number.
- [ ] Delete the sample document.
- [ ] Confirm the document disappears from the library.

### ResolveIQ checks

- [ ] Submit a synthetic customer incident.
- [ ] Confirm incident analysis and priority classification.
- [ ] Confirm the customer response draft is generated.
- [ ] Run an AI investigation.
- [ ] Confirm the investigation report and tool trace are displayed.
- [ ] Confirm historical incident and organisation-specific knowledge retrieval work when matching data is available.
- [ ] Approve or reject a response through human review.
- [ ] Confirm the review record appears in the review history.
- [ ] Confirm that approval does not send an email automatically.

### Persistence checks

If a persistent disk is configured:

- [ ] Restart or redeploy the backend.
- [ ] Confirm previously uploaded document indexes remain available.
- [ ] Confirm incident records remain available.
- [ ] Confirm investigation and review records remain available.

If these checks have not been completed, describe persistence as unverified.

## Rollback and cost control

- Start with one small backend service and a small sample PDF.
- Monitor hosting resource usage and Groq API consumption.
- Set provider-side usage limits where available.
- Do not leave paid resources running when the demonstration is no longer needed.
- Keep a local working copy and GitHub source as the recoverable project source.
- Remember that a free frontend does not make the complete application free if the backend requires paid compute or persistent storage.

## Deployment limitations

This is a portfolio application, not a production-ready multi-customer service.

Before handling real customer data, the application would need additional work on authentication, authorization, tenant isolation, secure file handling, data retention, operational monitoring, backups and deployment security.

The current application uses a simulated incident workflow. It does not connect to real customer email systems, send customer emails automatically, or diagnose and control third-party infrastructure.

## Official references

- Streamlit Community Cloud deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit dependencies: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Render environment variables: https://render.com/docs/configure-environment-variables
- Render persistent disks: https://render.com/docs/disks
- Render web services: https://render.com/docs/web-services
