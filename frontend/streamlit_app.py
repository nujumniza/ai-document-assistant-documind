
import streamlit as st
import requests
import os

# ==========================================================
# CONFIGURATION
# ==========================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# DESIGN SYSTEM
# ==========================================================

st.markdown(
    """
    <style>

    /* GLOBAL */
    .stApp {
        background: #F5F7FB;
    }

    .block-container {
        max-width: 1380px;
        padding: 2rem 2.5rem 3rem;
    }

    h1, h2, h3 {
        color: #14213D;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    p {
        color: #526078;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: #111C35;
        border-right: 1px solid #26334F;
    }

    section[data-testid="stSidebar"] * {
        color: #E8EEF9;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #33415E;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 8px 10px;
        border-radius: 9px;
    }

    /* METRIC CARDS */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E5EAF2;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.035);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
        font-weight: 500;
    }

    div[data-testid="stMetricValue"] {
        color: #14213D;
        font-weight: 750;
    }

    /* BUTTONS */
    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
        border: 1px solid #DCE4F0;
        padding: 0.55rem 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: #2563EB;
        color: white;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background: #1D4ED8;
    }

    /* INPUTS */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 9px;
    }

    /* CONTAINERS */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border-color: #E5EAF2;
        border-radius: 13px;
    }

    /* UPLOAD */
    section[data-testid="stFileUploader"] {
        background: white;
        border: 1px dashed #93A9CA;
        border-radius: 12px;
        padding: 14px;
    }

    /* CHAT */
    div[data-testid="stChatMessage"] {
        border: 1px solid #E5EAF2;
        border-radius: 13px;
        padding: 14px;
        margin-bottom: 12px;
        background: white;
    }

    div[data-testid="stChatInput"] {
        border-radius: 12px;
    }

    /* ALERTS */
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* CUSTOM COMPONENTS */
    .page-subtitle {
        color: #718096;
        font-size: 0.96rem;
        margin-top: -8px;
        margin-bottom: 25px;
    }

    .section-label {
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .brand-caption {
        color: #AAB8D0;
        font-size: 0.78rem;
    }

    .welcome-panel {
        background: linear-gradient(120deg, #17294C, #254C88);
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 25px;
        color: white;
    }

    .welcome-panel h2 {
        color: white;
        margin-bottom: 8px;
    }

    .welcome-panel p {
        color: #D5E2F5;
        margin-bottom: 0;
    }

    .source-card {
        background: #F4F7FC;
        border: 1px solid #E1E8F3;
        border-radius: 10px;
        padding: 12px 15px;
        margin-bottom: 10px;
    }

    .source-card strong {
        color: #203657;
    }

    .source-card small {
        color: #64748B;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# API FUNCTIONS
# ==========================================================

def get_api_data(endpoint):

    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=15
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return None


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


def delete_document(document_id):

    return requests.delete(
        f"{API_BASE_URL}/documents/{document_id}",
        timeout=15
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


# ==========================================================
# SESSION STATE
# ==========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("# 📚 DocuMind AI")

    st.markdown(
        '<div class="brand-caption">'
        'INTELLIGENT DOCUMENT WORKSPACE'
        '</div>',
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
            "AI Assistant"
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
        '<div class="brand-caption">'
        'DocuMind AI · Intelligent knowledge retrieval'
        '</div>',
        unsafe_allow_html=True
    )


# ==========================================================
# LOAD BACKEND INFORMATION
# ==========================================================

health = get_api_data("/health")


# ==========================================================
# DASHBOARD
# ==========================================================

if page == "Dashboard":

    data = get_api_data("/documents")

    st.markdown(
        """
        <div class="welcome-panel">
            <h2>Welcome to DocuMind AI 👋</h2>
            <p>
                Transform your documents into searchable knowledge.
                Upload PDFs, explore their content and get
                AI-powered answers with source evidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if data is None:

        st.error(
            "Cannot connect to the backend. "
            "Please start FastAPI."
        )

    else:

        documents = data.get("documents", [])

        total_documents = len(documents)

        total_chunks = sum(
            doc.get("total_chunks", 0)
            for doc in documents
        )

        total_pages = sum(
            doc.get("total_pages", 0)
            for doc in documents
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Documents",
            total_documents,
            help="Number of uploaded documents"
        )

        col2.metric(
            "Indexed Chunks",
            total_chunks,
            help="Number of text chunks stored in ChromaDB"
        )

        col3.metric(
            "Total Pages",
            total_pages,
            help="Total indexed PDF pages"
        )

        st.write("")

        st.subheader("System Overview")

        col1, col2 = st.columns(2)

        with col1:

            if health:

                st.success(
                    f"Backend: {health.get('status', 'Unknown')}"
                )

                st.caption(
                    health.get(
                        "application",
                        "AI Document Assistant"
                    )
                )

            else:

                st.error("Backend unavailable")

        with col2:

            if health:

                provider = health.get(
                    "llm_provider",
                    health.get("provider", "Unknown")
                )

                st.success(f"AI Provider: {provider}")

                if health.get("is_mock"):
                    st.warning("Mock provider is active.")

            else:

                st.error("AI provider unavailable")

        st.write("")

        st.subheader("Recent Documents")

        if documents:

            for document in documents[:5]:

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:

                        st.markdown(
                            f"📄 **{document['filename']}**"
                        )

                        st.caption(
                            f"{document['total_pages']} pages · "
                            f"{document['total_chunks']} indexed chunks"
                        )

                    with col2:

                        st.caption("Indexed")

        else:

            st.info(
                "Your workspace is empty. "
                "Upload your first PDF to get started."
            )


# ==========================================================
# DOCUMENT LIBRARY
# ==========================================================

elif page == "Document Library":

    st.title("Document Library")

    st.markdown(
        '<div class="page-subtitle">'
        'Upload, organize and manage your knowledge documents.'
        '</div>',
        unsafe_allow_html=True
    )

    # UPLOAD SECTION

    st.subheader("Upload Documents")

    with st.container(border=True):

        st.markdown("**Add a new PDF to your knowledge base**")

        uploaded_file = st.file_uploader(
            "Choose a PDF document",
            type=["pdf"],
            help="Maximum file size: 10 MB"
        )

        if st.button(
            "Upload and Process",
            type="primary",
            disabled=uploaded_file is None
        ):

            try:

                with st.spinner(
                    "Extracting text, generating embeddings "
                    "and indexing your document..."
                ):

                    response = upload_document(uploaded_file)

                    response.raise_for_status()

                    result = response.json()

                st.success(
                    "Document uploaded and indexed successfully!"
                )

                st.write(
                    f"**Filename:** {result.get('filename')}"
                )

                st.write(
                    f"**Pages:** {result.get('total_pages')}"
                )

                st.write(
                    f"**Chunks:** {result.get('total_chunks')}"
                )

                st.rerun()

            except requests.RequestException as error:

                st.error(f"Upload failed: {error}")

    st.write("")

    # DOCUMENT LIST

    st.subheader("Your Documents")

    data = get_api_data("/documents")

    if data is None:

        st.error("Unable to retrieve documents.")

    else:

        documents = data.get("documents", [])

        st.caption(
            f"{len(documents)} document(s) in your knowledge base"
        )

        if not documents:

            st.info(
                "No documents available. Upload a PDF to get started."
            )

        for document in documents:

            document_id = document["document_id"]

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.markdown(
                        f"### 📄 {document['filename']}"
                    )

                    st.caption(
                        f"{document['total_pages']} pages · "
                        f"{document['total_chunks']} chunks"
                    )

                    with st.expander("Document details"):

                        st.code(document_id)

                with col2:

                    if st.button(
                        "Delete",
                        key=f"delete_{document_id}"
                    ):

                        st.session_state.pending_delete = document_id
                        st.rerun()

                if st.session_state.pending_delete == document_id:

                    st.warning(
                        "Are you sure? This permanently deletes "
                        "the document's indexed chunks."
                    )

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

                                st.success("Document deleted successfully.")

                                st.rerun()

                            except requests.RequestException:

                                st.error("Unable to delete the document.")

                    with cancel_col:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{document_id}"
                        ):

                            st.session_state.pending_delete = None
                            st.rerun()


# ==========================================================
# AI ASSISTANT
# ==========================================================

elif page == "AI Assistant":

    st.title("AI Document Assistant")

    st.markdown(
        '<div class="page-subtitle">'
        'Ask questions and discover insights from your documents.'
        '</div>',
        unsafe_allow_html=True
    )

    data = get_api_data("/documents")

    if data is None:

        st.error("Cannot connect to the backend.")

    elif not data.get("documents"):

        st.info(
            "Your document library is empty. "
            "Upload a PDF before starting a conversation."
        )

    else:

        documents = data["documents"]

        # DOCUMENT SELECTION

        document_options = {
            "All documents": None
        }

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

            selected_document_id = document_options[
                selected_document
            ]

            top_k = st.slider(
                "Relevant passages to retrieve",
                min_value=1,
                max_value=10,
                value=3
            )

        # CHAT ACTIONS

        action_col, info_col = st.columns([1, 4])

        with action_col:

            if st.button("Clear conversation"):

                st.session_state.chat_history = []
                st.rerun()

        with info_col:

            st.caption(
                "Answers are generated using retrieved document evidence."
            )

        # EMPTY CHAT EXPERIENCE

        if not st.session_state.chat_history:

            st.write("")

            st.markdown(
                """
                <div style="
                    background:white;
                    border:1px solid #E5EAF2;
                    border-radius:16px;
                    padding:28px;
                    text-align:center;
                ">
                    <div style="font-size:38px;">💬</div>
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

        # DISPLAY CHAT HISTORY

        for message in st.session_state.chat_history:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

                if message["role"] == "assistant":

                    if message.get("is_mock"):

                        st.warning(
                            "This response came from a mock provider, "
                            "not a real LLM."
                        )

                    sources = message.get("sources", [])

                    if sources:

                        with st.expander(
                            f"View source evidence ({len(sources)})"
                        ):

                            for index, source in enumerate(sources, 1):

                                st.markdown(
                                    f"""
                                    <div class="source-card">
                                        <strong>
                                            Source {index}: 
                                            {source.get('filename', 'Document')}
                                        </strong>
                                        <br>
                                        <small>
                                            Page {source.get('page_number', 'Unknown')}
                                        </small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

        # QUESTION INPUT

        pending_question = st.session_state.pop(
            "pending_question",
            None
        )

        question = st.chat_input(
            "Ask a question about your documents..."
        )

        question_to_process = question or pending_question

        if question_to_process:

            st.session_state.chat_history.append({
                "role": "user",
                "content": question_to_process
            })

            with st.spinner(
                "Searching documents and generating your answer..."
            ):

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
                        "content": (
                            "I couldn't generate an answer. "
                            "Please check the backend and try again."
                        ),
                        "sources": [],
                        "is_mock": False
                    }

            st.session_state.chat_history.append(
                assistant_message
            )

            st.rerun()
