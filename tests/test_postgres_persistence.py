import sys
from pathlib import Path
import uuid

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.documents import Document

from app.chat.memory import (
    clear_session_history,
    delete_session_history,
    get_session_history,
)
from app.chat.session import ChatSessionManager
from app.db.connection import init_db
from app.rag.vectorstore import VectorStoreManager
from app.services.chat_service import ChatService


def test_postgres_persistence():
    print("=== 1. Initializing Database ===")
    init_db()
    print("✓ Database initialized with pgvector and tables.")

    print("\n=== 2. Testing Chat Session Persistence ===")
    session_manager = ChatSessionManager()
    session = session_manager.create_session("Test Session PostgreSQL")
    session_id = session.session_id
    print(f"✓ Created session: {session_id} - '{session.title}'")

    # Add document association
    doc_id = str(uuid.uuid4())
    session_manager.add_document(session_id, doc_id, filename="sample_report.pdf")
    print(f"✓ Associated document {doc_id} with session.")

    # Retrieve session in a fresh manager instance
    fresh_session_manager = ChatSessionManager()
    fetched = fresh_session_manager.get_session(session_id)
    assert fetched is not None, "Session should be found in database"
    assert fetched.title == "Test Session PostgreSQL"
    assert doc_id in fetched.document_ids
    assert fetched.document_names.get(doc_id) == "sample_report.pdf"
    print("✓ Fresh ChatSessionManager successfully loaded session from DB!")

    print("\n=== 3. Testing Chat Message History Persistence ===")
    history = get_session_history(session_id)
    history.add_user_message("What are the key benefits of PostgreSQL with pgvector?")
    history.add_ai_message("It provides ACID compliance, fast vector similarity search, and relational storage together.")

    # Retrieve history in a new call
    new_history = get_session_history(session_id)
    assert len(new_history.messages) == 2, f"Expected 2 messages, got {len(new_history.messages)}"
    assert str(new_history.messages[0].content).startswith("What are the key benefits")
    assert str(new_history.messages[1].content).startswith("It provides ACID compliance")
    print(f"✓ Persistent history verified ({len(new_history.messages)} messages stored).")

    print("\n=== 4. Testing PGVector VectorStore Persistence & Search ===")
    vector_manager = VectorStoreManager()
    test_chunks = [
        Document(
            page_content="PostgreSQL with pgvector allows scalable indexing using HNSW.",
            metadata={"document_id": doc_id, "filename": "sample_report.pdf", "page": 1},
        ),
        Document(
            page_content="Python asyncio is used for concurrent asynchronous I/O.",
            metadata={"document_id": doc_id, "filename": "sample_report.pdf", "page": 2},
        ),
    ]
    vector_manager.add_document(doc_id, test_chunks)
    print("✓ Added chunks to PGVector.")

    # Search with document filter
    results = vector_manager.search([doc_id], "How does pgvector indexing work?")
    assert len(results) > 0, "Expected at least 1 search result"
    assert "HNSW" in results[0].page_content
    print(f"✓ Vector similarity search returned matching chunk: '{results[0].page_content}'")

    print("\n=== 5. Testing ChatService End-to-End Orchestration ===")
    service = ChatService()
    chats = service.list_chats()
    assert any(c.session_id == session_id for c in chats), "Session must appear in ChatService.list_chats()"
    print(f"✓ ChatService listed {len(chats)} active persistent chats.")

    print("\n=== 6. Cleanup Verification ===")
    session_manager.delete_session(session_id)
    vector_manager.delete_document(doc_id)
    deleted_session = session_manager.get_session(session_id)
    assert deleted_session is None, "Deleted session should not be found"
    deleted_history = get_session_history(session_id)
    assert len(deleted_history.messages) == 0, "Chat history should be empty after deletion"
    print("✓ Session, history, and vectors cleaned up successfully.")

    print("\n🎉 ALL PERSISTENCE TESTS PASSED!")


if __name__ == "__main__":
    test_postgres_persistence()
