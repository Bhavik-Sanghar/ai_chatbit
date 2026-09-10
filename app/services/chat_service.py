from pathlib import Path

from app.chat.chain import build_chat_chain
from app.chat.orchestrator import ChatOrchestrator
from app.chat.session import ChatSessionManager
from app.db.connection import init_db
from app.rag.chain import build_rag_chain
from app.rag.retriever import SessionRetriever
from app.rag.vectorstore import VectorStoreManager
from app.services.document_service import DocumentService


class ChatService:
    def __init__(self):
        # Ensure database tables, extensions, and schema are ready
        init_db()

        self.session_manager = ChatSessionManager()
        self.vectorstore_manager = VectorStoreManager()
        self.document_service = DocumentService(self.vectorstore_manager)
        self.session_retriever = SessionRetriever(self.vectorstore_manager)

        self.chat_chain = build_chat_chain()
        self.rag_chain = build_rag_chain(self.session_retriever)

        self.orchestrator = ChatOrchestrator(
            chat_chain=self.chat_chain,
            rag_chain=self.rag_chain,
        )

    def create_chat(self, title: str = "New Chat"):
        return self.session_manager.create_session(title)

    def list_chats(self):
        return self.session_manager.list_sessions()

    def get_chat(self, session_id: str):
        return self.session_manager.get_session(session_id)

    def delete_chat(self, session_id: str):
        self.session_manager.delete_session(session_id)

    def upload_document(self, session_id: str, file_path: str) -> str:
        session = self.session_manager.get_session(session_id)
        if session is None:
            raise ValueError(f"Chat session '{session_id}' does not exist.")

        document_id = self.document_service.index_document(file_path)
        filename = Path(file_path).name
        self.session_manager.add_document(session_id, document_id, filename=filename)

        return document_id

    def chat(self, session_id: str, question: str):
        session = self.session_manager.get_session(session_id)
        if session is None:
            raise ValueError(f"Chat session '{session_id}' does not exist.")

        return self.orchestrator.invoke(
            session_id=session_id,
            question=question,
            document_ids=session.document_ids,
        )
