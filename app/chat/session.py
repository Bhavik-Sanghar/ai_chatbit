import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.chat.memory import delete_session_history
from app.db.connection import get_db_session
from app.db.models import ChatSessionModel, SessionDocumentModel


class ChatSession:
    def __init__(
        self,
        session_id: str,
        title: str = "New Chat",
        document_ids: list[str] | None = None,
        document_names: dict[str, str] | None = None,
        created_at: datetime | None = None,
    ):
        self.session_id = session_id
        self.title = title
        self.document_ids: list[str] = document_ids if document_ids is not None else []
        self.document_names: dict[str, str] = (
            document_names if document_names is not None else {}
        )
        self.created_at = created_at or datetime.now(timezone.utc)

    def add_document(self, document_id: str, filename: str | None = None) -> None:
        if document_id not in self.document_ids:
            self.document_ids.append(document_id)
        if filename:
            self.document_names[document_id] = filename


class ChatSessionManager:
    """Persistent PostgreSQL repository for Chat Sessions and attached Documents."""

    def create_session(self, title: str = "New Chat") -> ChatSession:
        session_id = str(uuid.uuid4())
        with get_db_session() as db:
            session_record = ChatSessionModel(
                session_id=session_id,
                title=title,
            )
            db.add(session_record)

        return ChatSession(
            session_id=session_id,
            title=title,
            document_ids=[],
            document_names={},
        )

    def get_session(self, session_id: str) -> ChatSession | None:
        with get_db_session() as db:
            stmt = (
                select(ChatSessionModel)
                .options(selectinload(ChatSessionModel.documents))
                .where(ChatSessionModel.session_id == session_id)
            )
            record = db.execute(stmt).scalar_one_or_none()
            if record is None:
                return None

            doc_ids = [d.document_id for d in record.documents]
            doc_names = {
                d.document_id: (d.filename or f"Doc-{d.document_id[:8]}")
                for d in record.documents
            }
            return ChatSession(
                session_id=str(record.session_id),
                title=str(record.title),
                document_ids=doc_ids,
                document_names=doc_names,
                created_at=(
                    record.created_at
                    if isinstance(record.created_at, datetime)
                    else None
                ),
            )

    def list_sessions(self) -> list[ChatSession]:
        with get_db_session() as db:
            stmt = (
                select(ChatSessionModel)
                .options(selectinload(ChatSessionModel.documents))
                .order_by(ChatSessionModel.created_at.asc())
            )
            records = db.execute(stmt).scalars().all()
            return [
                ChatSession(
                    session_id=str(r.session_id),
                    title=str(r.title),
                    document_ids=[str(d.document_id) for d in r.documents],
                    document_names={
                        str(d.document_id): (d.filename or f"Doc-{str(d.document_id)[:8]}")
                        for d in r.documents
                    },
                    created_at=(
                        r.created_at
                        if isinstance(r.created_at, datetime)
                        else None
                    ),
                )
                for r in records
            ]

    def delete_session(self, session_id: str) -> None:
        with get_db_session() as db:
            stmt = select(ChatSessionModel).where(ChatSessionModel.session_id == session_id)
            record = db.execute(stmt).scalar_one_or_none()
            if record:
                db.delete(record)

        # Also purge the chat messages from the Postgres chat_history table
        delete_session_history(session_id)

    def add_document(
        self,
        session_id: str,
        document_id: str,
        filename: str | None = None,
    ) -> None:
        with get_db_session() as db:
            session_record = db.get(ChatSessionModel, session_id)
            if session_record is None:
                raise ValueError(f"Chat session '{session_id}' does not exist.")

            # Check if document already attached
            existing = (
                db.execute(
                    select(SessionDocumentModel).where(
                        SessionDocumentModel.session_id == session_id,
                        SessionDocumentModel.document_id == document_id,
                    )
                )
                .scalars()
                .first()
            )

            if not existing:
                doc_record = SessionDocumentModel(
                    session_id=session_id,
                    document_id=document_id,
                    filename=filename,
                )
                db.add(doc_record)
