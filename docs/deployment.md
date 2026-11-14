# DocuMind AI — Deployment Guide

## Recommended portfolio topology

Deploy the Streamlit frontend and FastAPI backend separately:

- **Frontend:** Streamlit Community Cloud.
- **Backend:** a Python web-service host that supports environment variables and durable disk storage.
- **Vector database:** keep ChromaDB on the backend's durable mounted storage.
- **LLM:** Groq API, configured only through a backend secret.

This guide uses Render as an example backend host. Confirm current plan pricing and resource limits before creating a paid service.

## Critical storage warning

Render web services use an ephemeral filesystem by default. ChromaDB writes to disk, so a deployment without a persistent disk can lose its indexed documents after a restart or redeploy. Render documents persistent disks as a paid-service feature; the disk is attached to one service instance and has scaling/deploy limitations.

For a no-cost demonstration, you can deploy with temporary sample data and clearly disclose that it is not durable. Do not promise users that their uploads will persist unless durable storage has been configured and verified.

## Phase 1 — Prepare the repository

1. Ensure the project runs locally.
2. Run the essential test suite.
3. Keep backend dependencies in the root `requirements.txt`.
4. Keep frontend-only dependencies in `frontend/requirements.txt` (Streamlit Community Cloud can find a requirements file alongside the entrypoint).
5. Add `.env.example`.
6. Confirm `.env`, virtual environments, and `data/chroma/` are ignored by Git.
7. Remove personal CVs, private PDFs, API keys, local databases, and other private data from the repository.
8. Commit and push the project to GitHub.

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
documents/*
!documents/.gitkeep
```

Only add `documents/*` if the folder is intended to contain user-uploaded/private documents. Do not ignore sample documents that you intentionally want to publish.

## Phase 2 — Make the frontend API URL configurable

At the top of `frontend/streamlit_app.py`, add:

```python
import os
```

Replace:

```python
API_BASE_URL = "http://127.0.0.1:8000"
```

with:

```python
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")
```

This keeps the current local default while allowing the hosted frontend to call the deployed API.

## Phase 3 — Prepare the backend for a hosted service

The backend must bind to `0.0.0.0` and the host-provided port. Use this Render start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Build command:

```bash
pip install -r requirements.txt
```

Set the backend environment variables in the hosting dashboard:

```text
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=<your-secret>
```

Do not put the real API key in a committed file.

### ChromaDB disk

If you use a Render persistent disk, mount it at:

```text
/opt/render/project/src/data
```

This assumes the service working directory is the repository root and the application writes to the relative path `data/chroma/`. Verify the actual working directory and ChromaDB path in the deployed logs before relying on it.

A persistent disk is not available on every free service configuration. Check current Render pricing and disk eligibility. Do not proceed as if persistent storage is free.

### CORS

The current Streamlit frontend calls the API from the Streamlit server-side Python process using `requests`; it is not a browser JavaScript fetch. CORS is therefore not normally needed for this specific frontend-to-backend call. If a browser-based frontend is introduced later, configure CORS with explicit allowed origins rather than `*` for an authenticated production app.

## Phase 4 — Deploy the backend

1. Create a Python web service from the GitHub repository.
2. Select a supported Python runtime (Python 3.11 or 3.12 is a conservative deployment target for this dependency stack; verify package compatibility).
3. Set the build and start commands above.
4. Add the environment variables.
5. Configure durable storage if uploaded vector data must persist.
6. Deploy.
7. Open `https://YOUR-BACKEND.onrender.com/health`.
8. Confirm the response reports a healthy application and the expected LLM provider.
9. Check logs for embedding model load errors, ChromaDB path issues, and provider failures.

Do not publish a backend URL until this health check succeeds.

## Phase 5 — Deploy Streamlit frontend

1. Push the complete repository to GitHub.
2. Sign in to Streamlit Community Cloud using GitHub.
3. Create an app from the repository.
4. Set the entrypoint to `frontend/streamlit_app.py`.
5. Select Python 3.12 in advanced settings, if available.
6. Add the frontend environment variable in the app's secrets/settings:

```toml
API_BASE_URL = "https://YOUR-BACKEND.onrender.com"
```

The application reads `API_BASE_URL` from the process environment. If using Streamlit secrets, update the code to read `st.secrets` as a fallback, or configure an environment variable through the host if supported. A simple robust helper is:

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

Use the helper instead of the simpler `os.getenv` assignment if you configure the value in Streamlit's secrets UI.

7. Deploy and open the public Streamlit URL.
8. Test the UI against the hosted backend.

## Phase 6 — Hosted smoke test

Use a non-sensitive, small sample PDF.

- [ ] Dashboard loads.
- [ ] Backend status is healthy.
- [ ] AI provider is shown correctly.
- [ ] Upload a sample PDF.
- [ ] Confirm page and chunk counts.
- [ ] Ask a question whose answer is clearly present in the sample.
- [ ] Confirm the answer is generated by the real provider, not mock mode.
- [ ] Expand source evidence and verify filename/page.
- [ ] Delete the sample document.
- [ ] Confirm the document disappears from the library.
- [ ] Restart/redeploy backend and verify persistence if a durable disk is configured.

## Rollback and cost control

- Start with one small service and a small sample PDF.
- Check provider usage and hosting costs.
- Set provider-side usage limits where available.
- Do not leave paid resources running if the demo is no longer needed.
- Keep a local working copy and GitHub source as the recoverable project source.
- A free frontend does not make the whole application free if the backend needs paid compute or persistent storage.

## Official references

- Streamlit Community Cloud deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit dependencies: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Render environment variables: https://render.com/docs/configure-environment-variables
- Render persistent disks: https://render.com/docs/disks
- Render web services: https://render.com/docs/web-services
