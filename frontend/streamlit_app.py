
import os
import requests
import streamlit as st


# ==========================================================
# CONFIGURATION
# ==========================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.set_page_config(
    page_title="DocuMind AI | ResolveIQ",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# ENTERPRISE DESIGN SYSTEM
# ==========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --navy: #14213D;
        --blue: #315EAA;
        --blue-dark: #244B8C;
        --muted: #64748B;
        --border: #E3E9F2;
        --surface: #FFFFFF;
        --background: #F4F6FA;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--background);
    }

    .block-container {
        max-width: 1450px;
        padding: 1.8rem 2.3rem 3rem;
    }

    h1, h2, h3, h4 {
        color: var(--navy);
        font-weight: 750;
        letter-spacing: -0.45px;
    }

    h1 {
        font-size: 2rem;
    }

    h2 {
        font-size: 1.45rem;
    }

    h3 {
        font-size: 1.08rem;
    }

    p, li {
        color: #526078;
    }

    [data-testid="stSidebar"] {
        background: #111C35;
        border-right: 1px solid #293956;
    }

    [data-testid="stSidebar"] * {
        color: #E8EEF9;
    }

    [data-testid="stSidebar"] hr {
        border-color: #33415E;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 9px 11px;
        border-radius: 9px;
        margin-bottom: 4px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #263957;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 17px 19px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.025);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 600;
        font-size: 0.84rem;
    }

    [data-testid="stMetricValue"] {
        color: var(--navy);
        font-weight: 800;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #D8E1ED;
        font-weight: 650;
        min-height: 40px;
        transition: 0.15s ease;
        color: #ffffff !important;

    }

    .stButton > button[kind="primary"] {
        background: var(--blue);
        border: 1px solid var(--blue);
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--blue-dark);
        border-color: var(--blue-dark);
        color: white !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"],
    .stNumberInput input {
        border-radius: 8px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border-color: var(--border);
        border-radius: 13px;
    }

    [data-testid="stExpander"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 11px;
    }

    [data-testid="stFileUploader"] {
        background: #FAFBFD;
        border: 1px dashed #A8B8CF;
        border-radius: 10px;
        padding: 12px;
    }

    [data-testid="stChatMessage"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 13px;
        margin-bottom: 10px;
    }

    .page-subtitle {
        color: #718096;
        font-size: 0.94rem;
        margin-top: -10px;
        margin-bottom: 23px;
    }

    .section-label {
        color: #94A8C7;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    .brand-caption {
        color: #AAB8D0;
        font-size: 0.76rem;
    }

    .hero {
        background: linear-gradient(115deg, #14213D 0%, #254D86 100%);
        border-radius: 16px;
        padding: 25px 29px;
        margin: 8px 0 23px;
        color: white;
        box-shadow: 0 5px 18px rgba(20, 33, 61, 0.12);
    }

    .hero h2 {
        color: white;
        font-size: 1.45rem;
        margin: 0 0 8px;
    }

    .hero p {
        color: #D8E4F5;
        margin: 0;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .eyebrow {
        color: #B8CBE7;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        font-weight: 800;
        margin-bottom: 9px;
    }

    .panel-heading {
        color: #64748B;
        text-transform: uppercase;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .soft-panel {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 17px 19px;
        margin-bottom: 10px;
    }

    .evidence-note {
        background: #EFF6FF;
        border: 1px solid #D7E8FF;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 12px 15px;
        margin: 10px 0 15px;
        color: #29466F;
        font-size: 0.88rem;
    }

    .warning-note {
        background: #FFF8ED;
        border: 1px solid #F8E5C6;
        border-left: 4px solid #E9A23B;
        border-radius: 8px;
        padding: 12px 15px;
        margin: 10px 0 15px;
        color: #79521B;
        font-size: 0.88rem;
    }

    .source-card {
        background: #F6F8FC;
        border: 1px solid #E3E9F2;
        border-radius: 9px;
        padding: 11px 14px;
        margin: 8px 0;
    }

    .source-card strong {
        color: #203657;
    }

    .source-card small {
        color: #64748B;
    }

    .status-line {
        color: #64748B;
        font-size: 0.82rem;
    }

    .divider-space {
        padding-top: 5px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            padding: 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# API HELPERS
# ==========================================================

def get_api_data(endpoint):
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=30
        )
        response.raise_for_status()
        return response.json(), None

    except requests.RequestException as error:
        details = error.response.text if error.response is not None else ""
        return None, f"{error}\n{details}"


def post_api_data(endpoint, payload=None):
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload or {},
            timeout=180
        )
        response.raise_for_status()
        return response.json(), None

    except requests.RequestException as error:
        details = error.response.text if error.response is not None else ""
        return None, f"{error}\n{details}"


def upload_document(uploaded_file):
    return requests.post(
        f"{API_BASE_URL}/documents/upload",
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        },
        timeout=180
    )


def upload_resolveiq_knowledge(uploaded_file, organisation):
    return requests.post(
        f"{API_BASE_URL}/resolveiq/knowledge/upload",
        data={"organisation": organisation},
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        },
        timeout=180
    )


def delete_document(document_id):
    return requests.delete(
        f"{API_BASE_URL}/documents/{document_id}",
        timeout=30
    )


def ask_question(question, document_id, top_k):
    return requests.post(
        f"{API_BASE_URL}/documents/ask",
        json={
            "query": question,
            "top_k": top_k,
            "document_id": document_id
        },
        timeout=120
    )


def get_incidents():
    data, error = get_api_data("/incidents")
    if error:
        return [], error
    return data.get("incidents", []), None


def get_reviews(incident_id):
    data, error = get_api_data(
        f"/incidents/{incident_id}/reviews"
    )
    if error:
        return [], error
    return data.get("reviews", []), None


def get_investigations(incident_id):
    data, error = get_api_data(
        f"/incidents/{incident_id}/investigations"
    )
    if error:
        return [], error
    return data.get("investigations", []), None


def display_priority(priority):
    priority = str(priority or "").upper()

    if priority == "P1":
        st.error("🔴 P1 · Critical")
    elif priority == "P2":
        st.warning("🟠 P2 · High")
    elif priority == "P3":
        st.info("🔵 P3 · Medium")
    elif priority == "P4":
        st.success("🟢 P4 · Low")
    else:
        st.write(priority or "Not available")


def display_list(items, empty_message):
    if isinstance(items, list) and items:
        for index, item in enumerate(items, 1):
            st.markdown(f"{index}. {item}")
    else:
        st.caption(empty_message)


# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULT_STATE = {
    "chat_history": [],
    "pending_delete": None,
    "pending_question": None,
    "resolveiq_result": None,
    "resolveiq_error": None,
    "resolveiq_investigation": None,
    "resolveiq_investigation_error": None,
    "resolveiq_review_result": None,
    "resolveiq_review_error": None,
    "resolveiq_selected_incident": None,
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Reset old automatic incident selection after this UI update
if st.session_state.get("resolveiq_ui_version") != 2:
    st.session_state.resolveiq_selected_incident = None
    st.session_state.resolveiq_ui_version = 2


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("# 📚 DocuMind AI")

    st.markdown(
        '<div class="brand-caption">INTELLIGENT DOCUMENT WORKSPACE</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<div class="section-label">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Document Library",
            "AI Assistant",
            "ResolveIQ"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        '<div class="section-label">TECHNOLOGY</div>',
        unsafe_allow_html=True
    )

    st.caption("FastAPI · ChromaDB · Groq")
    st.caption("Sentence Transformers")

    st.divider()

    st.markdown(
        '<div class="brand-caption">DocuMind AI · Intelligent knowledge retrieval</div>',
        unsafe_allow_html=True
    )


health, health_error = get_api_data("/health")


# ==========================================================
# DOCUMIND DASHBOARD
# ==========================================================

if page == "Dashboard":

    st.markdown("# Dashboard")

    st.markdown(
        '<div class="page-subtitle">Your intelligent document workspace at a glance.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">DOCUMIND AI WORKSPACE</div>
            <h2>Knowledge, made accessible.</h2>
            <p>
                Transform your documents into searchable knowledge.
                Upload PDFs, retrieve relevant evidence and get
                AI-powered answers grounded in your sources.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    data, documents_error = get_api_data("/documents")

    if documents_error:
        st.error("Cannot connect to the backend. Please start FastAPI.")

    else:
        documents = data.get("documents", [])

        total_documents = len(documents)
        total_chunks = sum(doc.get("total_chunks", 0) for doc in documents)
        total_pages = sum(doc.get("total_pages", 0) for doc in documents)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Documents", total_documents)
        c2.metric("Indexed Chunks", total_chunks)
        c3.metric("Total Pages", total_pages)

        st.write("")
        st.subheader("System Overview")

        c1, c2 = st.columns(2)

        with c1:
            if health:
                st.success(f"Backend · {health.get('status', 'Available')}")
                st.caption(health.get("application", "AI Document Assistant"))
            else:
                st.error("Backend unavailable")

        with c2:
            if health:
                provider = health.get(
                    "llm_provider",
                    health.get("provider", "Unknown")
                )
                st.success(f"AI Provider · {provider}")
                if health.get("is_mock"):
                    st.warning("Mock provider is active.")
            else:
                st.error("AI provider unavailable")

        st.write("")
        st.subheader("Recent Documents")

        if documents:
            for document in documents[:5]:
                with st.container(border=True):
                    st.markdown(f"**📄 {document['filename']}**")
                    st.caption(
                        f"{document['total_pages']} pages · "
                        f"{document['total_chunks']} indexed chunks"
                    )
        else:
            st.info("Your workspace is empty. Upload your first PDF to get started.")


# ==========================================================
# DOCUMENT LIBRARY
# ==========================================================

elif page == "Document Library":

    st.markdown("# Document Library")

    st.markdown(
        '<div class="page-subtitle">Upload, organize and manage your knowledge documents.</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):
        st.subheader("Upload a Document")

        uploaded_file = st.file_uploader(
            "Choose a PDF document",
            type=["pdf"],
            help="Upload a PDF to extract text and index its content.",
            key="documind_upload"
        )

        if st.button(
            "Upload and Process",
            type="primary",
            disabled=uploaded_file is None
        ):
            try:
                with st.spinner("Extracting, embedding and indexing your document..."):
                    response = upload_document(uploaded_file)
                    response.raise_for_status()
                    result = response.json()

                st.success("Document uploaded and indexed successfully.")
                st.write(f"**Filename:** {result.get('filename')}")
                st.write(f"**Pages:** {result.get('total_pages')}")
                st.write(f"**Chunks:** {result.get('total_chunks')}")
                st.rerun()

            except requests.RequestException as error:
                st.error(f"Upload failed: {error}")

    st.write("")
    st.subheader("Your Documents")

    data, error = get_api_data("/documents")

    if error:
        st.error("Unable to retrieve documents.")

    else:
        documents = data.get("documents", [])
        st.caption(f"{len(documents)} document(s) in your knowledge base.")

        if not documents:
            st.info("No documents available. Upload a PDF to get started.")

        for document in documents:

            document_id = document["document_id"]

            with st.container(border=True):

                c1, c2 = st.columns([4, 1])

                with c1:
                    st.markdown(f"**📄 {document['filename']}**")
                    st.caption(
                        f"{document['total_pages']} pages · "
                        f"{document['total_chunks']} chunks"
                    )

                    with st.expander("Document details"):
                        st.code(document_id)

                with c2:
                    if st.button("Delete", key=f"delete_{document_id}"):
                        st.session_state.pending_delete = document_id
                        st.rerun()

                if st.session_state.pending_delete == document_id:

                    st.warning("This permanently deletes the document's indexed chunks.")

                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Confirm deletion",
                            key=f"confirm_{document_id}",
                            type="primary"
                        ):
                            try:
                                response = delete_document(document_id)
                                response.raise_for_status()
                                st.session_state.pending_delete = None
                                st.success("Document deleted.")
                                st.rerun()
                            except requests.RequestException as error:
                                st.error(f"Unable to delete: {error}")

                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_{document_id}"):
                            st.session_state.pending_delete = None
                            st.rerun()


# ==========================================================
# AI DOCUMENT ASSISTANT
# ==========================================================

elif page == "AI Assistant":

    st.markdown("# AI Document Assistant")

    st.markdown(
        '<div class="page-subtitle">Ask questions and discover insights from your documents.</div>',
        unsafe_allow_html=True
    )

    data, error = get_api_data("/documents")

    if error:
        st.error("Cannot connect to the backend.")

    elif not data.get("documents"):
        st.info("Your document library is empty. Upload a PDF before starting a conversation.")

    else:

        documents = data["documents"]
        document_options = {"All documents": None}

        for document in documents:
            label = (
                f"{document['filename']} "
                f"({document['document_id'][:8]})"
            )
            document_options[label] = document["document_id"]

        with st.container(border=True):
            st.markdown("**Search configuration**")

            selected_document = st.selectbox(
                "Knowledge source",
                options=list(document_options.keys())
            )

            selected_document_id = document_options[selected_document]

            top_k = st.slider(
                "Relevant passages to retrieve",
                min_value=1,
                max_value=10,
                value=3
            )

        c1, c2 = st.columns([1, 4])

        with c1:
            if st.button("Clear conversation"):
                st.session_state.chat_history = []
                st.rerun()

        with c2:
            st.caption("Answers are generated using retrieved document evidence.")

        if not st.session_state.chat_history:
            st.markdown(
                """
                <div class="soft-panel" style="text-align:center;padding:27px;">
                    <div style="font-size:34px;">💬</div>
                    <h3>What would you like to know?</h3>
                    <p>
                        Ask questions about your documents.
                        DocuMind AI will retrieve relevant passages
                        and generate an evidence-based answer.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")
            st.markdown("**Try asking:**")

            suggestions = [
                "Summarise this document.",
                "What are the main technologies mentioned?",
                "What are the key findings?",
                "Which page contains the relevant information?"
            ]

            suggestion_cols = st.columns(2)

            for index, suggestion in enumerate(suggestions):
                with suggestion_cols[index % 2]:
                    if st.button(
                        suggestion,
                        key=f"suggestion_{index}",
                        use_container_width=True
                    ):
                        st.session_state.pending_question = suggestion
                        st.rerun()

        for message in st.session_state.chat_history:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                if message["role"] == "assistant":

                    if message.get("is_mock"):
                        st.warning("This response came from a mock provider, not a real LLM.")

                    sources = message.get("sources", [])

                    if sources:
                        with st.expander(f"View source evidence ({len(sources)})"):
                            for index, source in enumerate(sources, 1):
                                st.markdown(
                                    f"""
                                    <div class="source-card">
                                        <strong>Source {index}: {source.get('filename', 'Document')}</strong>
                                        <br>
                                        <small>Page {source.get('page_number', 'Unknown')}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

        pending_question = st.session_state.pop("pending_question", None)
        question = st.chat_input("Ask a question about your documents...")
        question_to_process = question or pending_question

        if question_to_process:

            st.session_state.chat_history.append({
                "role": "user",
                "content": question_to_process
            })

            with st.spinner("Searching documents and generating your answer..."):
                try:
                    response = ask_question(
                        question_to_process,
                        selected_document_id,
                        top_k
                    )
                    response.raise_for_status()
                    result = response.json()

                    assistant_message = {
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result.get("sources", []),
                        "is_mock": result.get("is_mock", False)
                    }

                except requests.RequestException:
                    assistant_message = {
                        "role": "assistant",
                        "content": "I couldn't generate an answer. Please check the backend and try again.",
                        "sources": [],
                        "is_mock": False
                    }

            st.session_state.chat_history.append(assistant_message)
            st.rerun()


# ==========================================================
# RESOLVEIQ — SERVICE OPERATIONS WORKSPACE
# ==========================================================

elif page == "ResolveIQ":

    st.markdown("# ResolveIQ")

    st.markdown(
        '<div class="page-subtitle">Agentic AI service operations and customer support platform.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">SERVICE OPERATIONS INTELLIGENCE</div>
            <h2>From customer incident to informed action.</h2>
            <p>
                Structure incoming incidents, assess business impact,
                retrieve relevant evidence and support human-reviewed
                customer communication.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # LOAD INCIDENTS AND METRICS
    # ------------------------------------------------------

    incidents, incidents_error = get_incidents()

    if incidents_error:
        st.error("Unable to retrieve incident records.")
        incidents = []

    total_incidents = len(incidents)

    p1_count = sum(
        1 for item in incidents
        if str(item.get("priority", "")).upper() == "P1"
    )

    pending_count = sum(
        1 for item in incidents
        if item.get("status") == "awaiting_review"
    )

    reviewed_count = max(0, total_incidents - pending_count)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", total_incidents)
    c2.metric("P1 · Critical", p1_count)
    c3.metric("Awaiting Review", pending_count)
    c4.metric("Other Statuses", reviewed_count)

    st.write("")

    # ------------------------------------------------------
    # KNOWLEDGE BASE
    # ------------------------------------------------------

    with st.expander("📚  Organisation Knowledge Base", expanded=False):

        st.write(
            "Upload organisation-specific support procedures and reference "
            "documents. The investigation agent can retrieve relevant passages."
        )

        with st.form("resolveiq_knowledge_form"):

            knowledge_organisation = st.text_input(
                "Organisation",
                placeholder="e.g. Demo Logistics"
            )

            knowledge_file = st.file_uploader(
                "Support knowledge PDF",
                type=["pdf"],
                key="resolveiq_knowledge_file"
            )

            knowledge_submitted = st.form_submit_button(
                "Upload to Knowledge Base",
                type="primary"
            )

            if knowledge_submitted:

                if not knowledge_organisation.strip():
                    st.error("Enter the organisation name.")

                elif knowledge_file is None:
                    st.error("Select a PDF document.")

                else:
                    try:
                        with st.spinner("Processing and indexing the knowledge document..."):
                            response = upload_resolveiq_knowledge(
                                knowledge_file,
                                knowledge_organisation.strip()
                            )
                            response.raise_for_status()
                            knowledge_result = response.json()

                        st.success("Knowledge document uploaded successfully.")
                        st.json(knowledge_result)

                    except requests.RequestException as error:
                        st.error(f"Knowledge upload failed: {error}")

    # ------------------------------------------------------
    # SUBMIT INCIDENT
    # ------------------------------------------------------

    with st.expander("＋  Submit a Customer Incident", expanded=False):

        with st.form("resolveiq_incident_form"):

            c1, c2 = st.columns(2)

            with c1:
                organisation = st.text_input(
                    "Organisation *",
                    placeholder="e.g. Demo Logistics"
                )

                customer_name = st.text_input(
                    "Customer *",
                    placeholder="e.g. ABC Distribution"
                )

            with c2:
                subject = st.text_input(
                    "Incident subject *",
                    placeholder="e.g. Shipment tracking dashboard unavailable"
                )

                affected_users = st.number_input(
                    "Affected users",
                    min_value=1,
                    max_value=100000,
                    value=25
                )

            description = st.text_area(
                "Incident description *",
                height=125,
                placeholder=(
                    "Describe what the customer reported, the business impact "
                    "and observed symptoms. Avoid presenting assumptions as verified facts."
                )
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                severity = st.selectbox(
                    "Severity",
                    ["low", "medium", "high", "critical"],
                    index=2
                )

            with c2:
                business_impact = st.selectbox(
                    "Business impact",
                    ["low", "medium", "high", "critical"],
                    index=2
                )

            with c3:
                urgency = st.selectbox(
                    "Urgency",
                    ["low", "medium", "high", "critical"],
                    index=3
                )

            submitted = st.form_submit_button(
                "Analyse Incident",
                type="primary",
                use_container_width=True
            )

            if submitted:

                if not all([
                    organisation.strip(),
                    customer_name.strip(),
                    subject.strip(),
                    description.strip()
                ]):
                    st.error("Please complete all required incident fields.")

                else:
                    payload = {
                        "organisation": organisation.strip(),
                        "customer_name": customer_name.strip(),
                        "subject": subject.strip(),
                        "description": description.strip(),
                        "severity": severity,
                        "business_impact": business_impact,
                        "urgency": urgency,
                        "affected_users": int(affected_users)
                    }

                    with st.spinner("ResolveIQ is analysing the incident..."):
                        result, error = post_api_data(
                            "/incidents/analyze",
                            payload
                        )

                    if error:
                        st.session_state.resolveiq_error = error
                        st.session_state.resolveiq_result = None

                    else:
                        st.session_state.resolveiq_result = result
                        st.session_state.resolveiq_error = None
                        st.session_state.resolveiq_selected_incident = result.get("incident_id")
                        st.session_state.resolveiq_investigation = None
                        st.session_state.resolveiq_investigation_error = None
                        st.session_state.resolveiq_review_result = None
                        st.session_state.resolveiq_review_error = None

                    st.rerun()

    if st.session_state.resolveiq_error:
        st.error("Incident analysis failed.")
        st.code(st.session_state.resolveiq_error)

    # ------------------------------------------------------
    # INCIDENT SELECTION
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INCIDENT SELECTION
    # ------------------------------------------------------

    st.divider()
    st.subheader("Incident Workspace")

    if not incidents:

        st.info(
            "No incidents recorded yet. "
            "Submit a customer incident to begin."
        )

    else:

        st.caption(f"{total_incidents} incident(s) recorded.")

        incident_options = {}

        for item in incidents:
            incident_id = item.get("incident_id")

            if not incident_id:
                continue

            label = (
                f"{str(item.get('priority', 'N/A')).upper()}  ·  "
                f"{item.get('customer_name', 'Unknown customer')}  ·  "
                f"{item.get('subject', 'Untitled incident')}  ·  "
                f"{incident_id[:8]}"
            )

            incident_options[label] = incident_id

        placeholder = "— Select an incident to review —"

        options = [placeholder] + list(incident_options.keys())

        current_id = st.session_state.resolveiq_selected_incident

        selected_label = st.selectbox(
            "Select an incident",
            options=options,
            index=(
                options.index(
                    next(
                        (
                            label for label, value in incident_options.items()
                            if value == current_id
                        ),
                        placeholder
                    )
                )
            ),
            key="resolveiq_incident_selector"
        )

        if selected_label == placeholder:
            selected_incident_id = None
        else:
            selected_incident_id = incident_options[selected_label]

        if selected_incident_id != current_id:

            st.session_state.resolveiq_selected_incident = selected_incident_id
            st.session_state.resolveiq_investigation = None
            st.session_state.resolveiq_investigation_error = None
            st.session_state.resolveiq_review_result = None
            st.session_state.resolveiq_review_error = None
            st.rerun()


    # ------------------------------------------------------
    # SELECTED INCIDENT
    # ------------------------------------------------------

    selected_id = st.session_state.resolveiq_selected_incident

    selected_incident = next(
        (
            item for item in incidents
            if item.get("incident_id") == selected_id
        ),
        None
    )

    analysis_result = st.session_state.resolveiq_result

    if analysis_result and analysis_result.get("incident_id") == selected_id:
        incident_details = analysis_result
    else:
        incident_details = selected_incident

    if incident_details:

        incident_id = incident_details.get("incident_id")

        st.divider()

        # --------------------------------------------------
        # INCIDENT HEADER
        # --------------------------------------------------

        header_col, priority_col, sla_col = st.columns([3, 1, 1])

        with header_col:
            st.markdown("### " + str(incident_details.get("subject", "Customer Incident")))
            st.caption(
                f"{incident_details.get('organisation', '')}  ·  "
                f"{incident_details.get('customer_name', '')}"
            )

        with priority_col:
            display_priority(incident_details.get("priority"))

        with sla_col:
            st.metric(
                "SLA Target",
                f"{incident_details.get('sla_target_hours', 'N/A')} hrs"
            )

        st.caption(
            f"Incident ID: {incident_id}  ·  "
            f"Status: {incident_details.get('status', 'N/A')}"
        )

        with st.expander("View original incident record"):
            st.json(incident_details)

        # --------------------------------------------------
        # CLASSIFICATION AND SUMMARY
        # --------------------------------------------------

        st.markdown("### Incident Intelligence")

        c1, c2 = st.columns(2)

        with c1:
            with st.container(border=True):
                st.markdown('<div class="panel-heading">Incident Category</div>', unsafe_allow_html=True)
                st.markdown(f"**{incident_details.get('category', 'Not available')}**")

        with c2:
            with st.container(border=True):
                st.markdown('<div class="panel-heading">Customer Sentiment</div>', unsafe_allow_html=True)
                sentiment = incident_details.get("sentiment", "Not available")
                st.markdown(f"**{str(sentiment).capitalize()}**")

        c1, c2 = st.columns(2)

        with c1:
            with st.container(border=True):
                st.markdown("**Incident Summary**")
                st.write(
                    incident_details.get("summary", "No summary available.")
                )

        with c2:
            with st.container(border=True):
                st.markdown("**Business Impact**")
                st.write(
                    incident_details.get(
                        "business_impact_summary",
                        "No business impact summary available."
                    )
                )

        with st.container(border=True):
            st.markdown("**Priority Explanation**")
            st.info(
                incident_details.get(
                    "priority_explanation",
                    "Priority explanation not available."
                )
            )

        c1, c2 = st.columns(2)

        with c1:
            with st.container(border=True):
                st.markdown("**Key Observations**")
                display_list(
                    incident_details.get("key_observations", []),
                    "No observations available."
                )

        with c2:
            with st.container(border=True):
                st.markdown("**Recommended Actions**")
                display_list(
                    incident_details.get("recommended_actions", []),
                    "No recommended actions available."
                )

        # --------------------------------------------------
        # CUSTOMER RESPONSE
        # --------------------------------------------------

        st.divider()
        st.markdown("### Customer Response")

        st.markdown(
            """
            <div class="warning-note">
                <strong>Human review required</strong><br>
                Review and edit the AI-generated draft before recording
                an approval decision. Approval does not send an email.
            </div>
            """,
            unsafe_allow_html=True
        )

        response_draft = incident_details.get("customer_response_draft", "")

        edited_response = st.text_area(
            "Customer response draft",
            value=response_draft,
            height=230,
            key=f"response_draft_{incident_id}"
        )

        # --------------------------------------------------
        # HUMAN REVIEW
        # --------------------------------------------------

        st.markdown("### Human Review")

        with st.container(border=True):

            st.write(
                "A human reviewer makes the final decision on the customer response."
            )

            reviewer = st.text_input(
                "Reviewer name or role",
                value="Support Manager",
                key=f"reviewer_{incident_id}"
            )

            approve_col, reject_col = st.columns(2)

            with approve_col:
                approve_clicked = st.button(
                    "✓  Approve Response",
                    type="primary",
                    use_container_width=True,
                    key=f"approve_{incident_id}"
                )

            with reject_col:
                reject_clicked = st.button(
                    "✕  Reject Response",
                    use_container_width=True,
                    key=f"reject_{incident_id}"
                )

        if approve_clicked or reject_clicked:

            if not reviewer.strip():
                st.session_state.resolveiq_review_error = "Enter the reviewer name or role."

            elif not edited_response.strip():
                st.session_state.resolveiq_review_error = "The customer response cannot be empty."

            else:
                decision = "approved" if approve_clicked else "rejected"

                review_payload = {
                    "decision": decision,
                    "reviewer": reviewer.strip(),
                    "edited_response": edited_response
                }

                with st.spinner("Recording human review decision..."):
                    review_result, review_error = post_api_data(
                        f"/incidents/{incident_id}/review",
                        review_payload
                    )

                if review_error:
                    st.session_state.resolveiq_review_error = review_error
                    st.session_state.resolveiq_review_result = None
                else:
                    st.session_state.resolveiq_review_result = review_result
                    st.session_state.resolveiq_review_error = None

                st.rerun()

        if st.session_state.resolveiq_review_error:
            st.error(st.session_state.resolveiq_review_error)

        review_result = st.session_state.resolveiq_review_result

        if review_result and review_result.get("incident_id") == incident_id:

            if review_result.get("decision") == "approved":
                st.success("Response approval recorded.")
            else:
                st.warning("Response rejection recorded.")

            c1, c2, c3 = st.columns(3)
            c1.metric("Decision", str(review_result.get("decision", "N/A")).title())
            c2.metric("Reviewer", review_result.get("reviewer", "N/A"))
            c3.metric("Email Sent", "Yes" if review_result.get("email_sent") else "No")

            st.caption("The review decision is recorded. This application does not send emails.")

        # --------------------------------------------------
        # REVIEW HISTORY
        # --------------------------------------------------

        with st.expander("Review History", expanded=True):

            reviews, reviews_error = get_reviews(incident_id)

            if reviews_error:
                st.warning("Unable to retrieve review history.")

            elif reviews:
                for review in reviews:

                    with st.container(border=True):

                        c1, c2 = st.columns(2)

                        with c1:
                            st.markdown("**Decision**")
                            decision = str(review.get("decision", "N/A")).upper()
                            st.write(decision)

                        with c2:
                            st.markdown("**Reviewer**")
                            st.write(review.get("reviewer", "N/A"))

                        st.caption(f"Review ID: {review.get('review_id', 'N/A')}")

            else:
                st.info("No review decisions recorded yet.")

        # --------------------------------------------------
        # AI INVESTIGATION
        # --------------------------------------------------

        st.divider()
        st.markdown("### AI Investigation")

        st.write(
            "Retrieve relevant customer incident history, support policies "
            "and organisation-specific knowledge documents."
        )

        st.markdown(
            """
            <div class="evidence-note">
                <strong>Investigation boundaries</strong><br>
                ResolveIQ uses available records and knowledge documents
                to produce evidence-informed recommendations. It does not
                directly diagnose or control external third-party systems.
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Run AI Investigation",
            type="primary",
            use_container_width=True,
            key=f"investigate_{incident_id}"
        ):

            with st.spinner("ResolveIQ agent is investigating the incident..."):
                investigation_result, investigation_error = post_api_data(
                    f"/incidents/{incident_id}/investigate"
                )

            if investigation_error:
                st.session_state.resolveiq_investigation_error = investigation_error
                st.session_state.resolveiq_investigation = None
            else:
                st.session_state.resolveiq_investigation = investigation_result
                st.session_state.resolveiq_investigation_error = None

            st.rerun()

        if st.session_state.resolveiq_investigation_error:
            st.error("Investigation failed.")
            st.code(st.session_state.resolveiq_investigation_error)

        investigation = st.session_state.resolveiq_investigation

        if investigation and investigation.get("incident_id") == incident_id:

            st.success("Investigation completed.")

            st.markdown("#### Investigation Report")

            report = investigation.get("report")

            if isinstance(report, str):
                st.markdown(report)
            elif isinstance(report, dict):
                st.json(report)
            else:
                st.info("No investigation report was returned.")

            st.markdown("#### Tools Used")

            tools_used = investigation.get("tools_used", [])

            if tools_used:
                tool_cols = st.columns(min(len(tools_used), 3))

                for index, tool in enumerate(tools_used):
                    with tool_cols[index % len(tool_cols)]:
                        with st.container(border=True):
                            st.markdown(f"**{tool}**")
            else:
                st.caption("No tools reported.")

            st.caption(
                "Investigation status: "
                f"{investigation.get('status', 'N/A')}"
            )

        # --------------------------------------------------
        # INVESTIGATION HISTORY
        # --------------------------------------------------


        # --------------------------------------------------
        # INVESTIGATION HISTORY
        # --------------------------------------------------

        st.markdown("#### Investigation History")

        investigation_history, history_error = get_investigations(incident_id)

        if history_error:
            st.warning("Unable to retrieve investigation history.")

        elif investigation_history:

            for previous in investigation_history:

                investigation_label = (
                    "Investigation · "
                    + str(previous.get("investigation_id", "Record"))[:8]
                )

                with st.expander(investigation_label):

                    previous_report = previous.get("report")

                    if isinstance(previous_report, str):
                        st.markdown(previous_report)
                    elif isinstance(previous_report, dict):
                        st.json(previous_report)
                    else:
                        st.write(previous_report)

                    st.caption(
                        f"Status: {previous.get('status', 'N/A')}"
                    )

        else:
            st.info("No investigation records are available for this incident.")
