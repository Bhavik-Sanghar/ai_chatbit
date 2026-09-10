from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New Chat")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    documents = relationship(
        "SessionDocumentModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionDocumentModel.created_at",
    )


class SessionDocumentModel(Base):
    __tablename__ = "session_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String(64),
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id = Column(String(64), nullable=False, index=True)
    filename = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session = relationship("ChatSessionModel", back_populates="documents")
