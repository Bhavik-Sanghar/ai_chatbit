import logging
from contextlib import contextmanager
from typing import Generator

import psycopg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import (
    DATABASE_URL,
    PG_CHAT_HISTORY_TABLE_NAME,
)
from app.db.models import Base

logger = logging.getLogger("ai_chatbit.db")

_ENGINE = None
_SESSION_FACTORY = None


def get_raw_connection_string() -> str:
    """Return a standard PostgreSQL connection URI for psycopg/direct drivers."""
    return DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def get_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    return _ENGINE


def get_session_factory():
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SESSION_FACTORY


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize Postgres extensions, relational tables, and chat history store."""
    engine = get_engine()

    # 1. Enable pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    # 2. Create declarative relational tables (chat_sessions, session_documents)
    Base.metadata.create_all(bind=engine)

    # 3. Create chat history table for langchain-postgres
    try:
        from langchain_postgres import PostgresChatMessageHistory

        raw_conn_str = get_raw_connection_string()
        with psycopg.connect(raw_conn_str) as sync_conn:
            PostgresChatMessageHistory.create_tables(
                sync_conn, PG_CHAT_HISTORY_TABLE_NAME
            )
            sync_conn.commit()
    except Exception as exc:
        logger.warning(
            "Could not ensure chat history table: %s",
            exc,
        )

    logger.info("Database initialized successfully.")
