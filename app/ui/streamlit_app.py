import logging
from pathlib import Path
import sys
import time

# Ensure the project root directory is on sys.path so 'app' can always be imported
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from app.chat.memory import get_session_history
from app.config.settings import GOOGLE_API_KEY
from app.services.chat_service import ChatService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_chatbit.ui")

# Page configuration
st.set_page_config(
    page_title="AI ChatBit",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .badge-general {
        display: inline-block;
        background-color: #e0f2fe;
        color: #0369a1;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-bottom: 6px;
    }
    .badge-document {
        display: inline-block;
        background-color: #fef3c7;
        color: #b45309;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-bottom: 6px;
    }
    .doc-pill {
        background-color: #f3f4f6;
        border-radius: 6px;
        padding: 6px 10px;
        margin-bottom: 4px;
        font-size: 0.85rem;
        word-break: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# State Initialization
# ─────────────────────────────────────────────────────────────

if "chat_service" not in st.session_state:
    st.session_state.chat_service = ChatService()

chat_service: ChatService = st.session_state.chat_service

# Map of document_id -> filename
if "doc_names" not in st.session_state:
    st.session_state.doc_names = {}

# Map of (session_id, message_index) -> route metadata
if "message_routes" not in st.session_state:
    st.session_state.message_routes = {}

# Track indexed file keys to prevent re-upload on rerun
if "indexed_file_keys" not in st.session_state:
    st.session_state.indexed_file_keys = set()

# Ensure active session exists
existing_sessions = chat_service.list_chats()
if (
    "current_session_id" not in st.session_state
    or not st.session_state.current_session_id
):
    if existing_sessions:
        st.session_state.current_session_id = existing_sessions[0].session_id
    else:
        new_session = chat_service.create_chat("New Chat")
        st.session_state.current_session_id = new_session.session_id

current_session_id = st.session_state.current_session_id
current_session = chat_service.session_manager.get_session(current_session_id)

# Fallback if current session is missing
if current_session is None:
    existing_sessions = chat_service.list_chats()
    if existing_sessions:
        st.session_state.current_session_id = existing_sessions[0].session_id
        current_session_id = st.session_state.current_session_id
        current_session = existing_sessions[0]
    else:
        new_session = chat_service.create_chat("New Chat")
        st.session_state.current_session_id = new_session.session_id
        current_session_id = new_session.session_id
        current_session = new_session

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🤖 AI ChatBit")
    st.caption("Multi-session Chat & Document RAG")

    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        count = len(chat_service.list_chats()) + 1
        new_session = chat_service.create_chat(f"Chat {count}")
        st.session_state.current_session_id = new_session.session_id
        st.rerun()

    st.divider()

    # Session Management
    st.subheader("Conversations")
    sessions = chat_service.list_chats()

    for s in sessions:
        col1, col2 = st.columns([0.82, 0.18])
        is_active = s.session_id == current_session_id
        button_label = f"💬 {s.title}" if not is_active else f"👉 {s.title}"

        with col1:
            if st.button(
                button_label,
                key=f"sess_{s.session_id}",
                use_container_width=True,
                type="secondary" if not is_active else "primary",
            ):
                st.session_state.current_session_id = s.session_id
                st.rerun()

        with col2:
            if st.button("🗑️", key=f"del_{s.session_id}", help="Delete chat"):
                chat_service.delete_chat(s.session_id)
                if st.session_state.current_session_id == s.session_id:
                    remaining = chat_service.list_chats()
                    st.session_state.current_session_id = (
                        remaining[0].session_id if remaining else None
                    )
                st.rerun()

    st.divider()

    # Document Upload Section
    st.subheader("Attach Documents")
    uploaded_file = st.file_uploader(
        "Upload document for current session",
        type=["pdf", "txt", "md", "html", "htm", "csv", "docx", "xlsx", "xls"],
        key=f"uploader_{current_session_id}",
        help="Upload a document (.pdf, .txt, .md, .html, .csv, .docx, .xlsx, .xls) to ask questions about it in this session.",
    )

    if uploaded_file is not None:
        file_key = f"{current_session_id}_{uploaded_file.name}_{uploaded_file.size}"
        if file_key not in st.session_state.indexed_file_keys:
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                try:
                    upload_dir = Path("data/uploads")
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    saved_path = upload_dir / uploaded_file.name

                    # Write file locally
                    with open(saved_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Index document via existing ChatService
                    doc_id = chat_service.upload_document(
                        current_session_id, str(saved_path)
                    )
                    st.session_state.doc_names[doc_id] = uploaded_file.name
                    st.session_state.indexed_file_keys.add(file_key)
                    st.success(f"Attached {uploaded_file.name}")
                    st.rerun()
                except Exception as e:
                    logger.exception(f"Failed to process PDF {uploaded_file.name}")
                    st.error(f"Failed to process PDF: {e}")

    # Documents attached to current session
    st.subheader("Session Documents")
    attached_doc_ids = current_session.document_ids if current_session else []
    if attached_doc_ids:
        for doc_id in attached_doc_ids:
            doc_name = (
                current_session.document_names.get(doc_id)
                if hasattr(current_session, "document_names")
                else None
            ) or st.session_state.doc_names.get(doc_id, f"Doc-{doc_id[:8]}")
            st.markdown(
                f"<div class='doc-pill'>📄 {doc_name}</div>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No documents attached to this chat.")


# ─────────────────────────────────────────────────────────────
# Main Chat Area
# ─────────────────────────────────────────────────────────────

# Header
st.markdown(
    f"<div class='main-title'>{current_session.title}</div>",
    unsafe_allow_html=True,
)
doc_count = len(attached_doc_ids)
if doc_count > 0:
    st.markdown(
        f"<div class='sub-title'>Attached documents: <b>{doc_count}</b> | Mode: Auto-routing (General or Document RAG)</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='sub-title'>General Chat Mode (Upload a PDF in the sidebar to enable Document RAG)</div>",
        unsafe_allow_html=True,
    )

# API key notice if missing
if not GOOGLE_API_KEY:
    st.warning(
        "⚠️ **Missing API Key**: Neither `GOOGLE_API_KEY` nor `GEMINI_API_KEY` was found. "
        "Please check your `.env` file."
    )

# Render Message History from memory
session_history = get_session_history(current_session_id)
messages = session_history.messages

for idx, msg in enumerate(messages):
    if msg.type == "human":
        with st.chat_message("user"):
            st.write(msg.content)
    elif msg.type == "ai":
        with st.chat_message("assistant"):
            route = st.session_state.message_routes.get(
                f"{current_session_id}_{idx}", "general"
            )
            if route == "document":
                st.markdown(
                    "<span class='badge-document'>📄 Document RAG</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<span class='badge-general'>🤖 General Chat</span>",
                    unsafe_allow_html=True,
                )
            st.write(msg.content)

# ─────────────────────────────────────────────────────────────
# Chat Input & Response Streaming
# ─────────────────────────────────────────────────────────────

prompt = st.chat_input("Type your message here...")

if prompt:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        st.warning("Please enter a non-empty message.")
    elif current_session is None:
        st.error("No active chat session found. Please create a new chat.")
    else:
        # Update session title if still placeholder
        if current_session.title in [
            "New Chat",
            "Chat 1",
        ] or current_session.title.startswith("Chat "):
            truncated_title = clean_prompt[:26] + (
                "..." if len(clean_prompt) > 26 else ""
            )
            current_session.title = truncated_title

        # Display user message
        with st.chat_message("user"):
            st.write(clean_prompt)

        # Generate response
        with st.chat_message("assistant"):
            try:
                # Detect route using the orchestrator's router
                detected_route = "general"
                try:
                    decision = chat_service.orchestrator.router.invoke(
                        {"question": clean_prompt}
                    )
                    detected_route = getattr(decision, "route", "general")
                except Exception:
                    detected_route = "general"

                # Check if document was requested but none attached
                if detected_route == "document" and not current_session.document_ids:
                    response_text = (
                        "No documents have been uploaded to this chat session yet. "
                        "Please upload a PDF in the sidebar to ask questions about your documents, "
                        "or ask a general question."
                    )
                    detected_route = "document"
                    # Add to session history
                    session_history.add_user_message(clean_prompt)
                    session_history.add_ai_message(response_text)
                else:
                    # Execute chat call through ChatService
                    with st.spinner("Thinking..."):
                        response_text = chat_service.chat(
                            current_session_id, clean_prompt
                        )

                # Show mode badge
                if detected_route == "document":
                    st.markdown(
                        "<span class='badge-document'>📄 Document RAG</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<span class='badge-general'>🤖 General Chat</span>",
                        unsafe_allow_html=True,
                    )

                # Stream response words
                def word_stream():
                    words = response_text.split(" ")
                    for i, w in enumerate(words):
                        yield w + (" " if i < len(words) - 1 else "")
                        time.sleep(0.015)

                st.write_stream(word_stream)

                # Save route indicator for rendered history
                new_msg_idx = len(session_history.messages) - 1
                st.session_state.message_routes[
                    f"{current_session_id}_{new_msg_idx}"
                ] = detected_route

            except Exception as e:
                logger.exception("Error generating assistant response")
                st.error(f"Error generating response: {e}")
