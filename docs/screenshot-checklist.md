# DocuMind AI — Screenshot Capture Checklist

Capture screenshots from the real running application after the final UI is in place. Use a synthetic or redacted PDF. Never expose API keys, personal CV data, private reports, local file paths, or document IDs that should remain private.

## Capture settings

- Browser window: desktop, approximately 1440 × 900 or larger.
- Browser zoom: 100%.
- Use the same browser dimensions and zoom for all screenshots.
- Close developer tools and unrelated tabs.
- Use a clean sample workspace with one or two synthetic PDFs.
- Ensure no loading spinner, traceback, warning, or modal obscures the screen.
- Save PNG files in this folder using the names below.

## Required screenshots

### 1. `dashboard.png`

Show:
- DocuMind AI branding and sidebar.
- Welcome panel.
- Document, chunk and page metrics.
- Backend health.
- LLM provider status.
- Recent documents.

### 2. `document-library.png`

Show:
- Upload area.
- One successfully indexed sample document.
- Page and chunk counts.
- Document listing.

### 3. `ai-assistant.png`

Show:
- Selected document or All documents.
- A meaningful question.
- A useful answer.
- A clean conversation layout.

### 4. `source-evidence.png`

Show:
- An answer.
- Expanded source evidence.
- Source filename and page number.
- A sample question whose answer can be verified in that source.

## Optional screenshots

- `upload-success.png`: upload success with pages/chunks.
- `delete-confirmation.png`: delete confirmation prompt.
- `api-health.png`: `/health` response in browser or API docs.

## Demo script (60–90 seconds)

1. Introduce DocuMind AI and the problem it solves.
2. Show dashboard metrics and system health.
3. Upload a small synthetic PDF.
4. Show the document indexed in the library.
5. Ask a question that requires retrieving a specific passage.
6. Expand the source evidence and show the page reference.
7. Briefly explain the flow: PDF → extraction → chunking → embeddings → ChromaDB → retrieval → Groq → cited answer.

Do not claim that source citations guarantee factual correctness. Explain that they provide traceability to retrieved passages.
