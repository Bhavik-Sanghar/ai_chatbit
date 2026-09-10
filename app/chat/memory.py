import logging
import psycopg
from langchain_postgres import PostgresChatMessageHistory

from app.config.settings import PG_CHAT_HISTORY_TABLE_NAME
from app.db.connection import get_raw_connection_string

logger = logging.getLogger("ai_chatbit.chat.memory")

_SYNC_CONN: psycopg.Connection | None = None


def _get_persistent_connection() -> psycopg.Connection:
    """Return a healthy, autocommit psycopg connection for chat history operations."""
    global _SYNC_CONN
    if _SYNC_CONN is None or _SYNC_CONN.closed:
        _SYNC_CONN = psycopg.connect(get_raw_connection_string(), autocommit=True)
    return _SYNC_CONN


def get_session_history(session_id: str) -> PostgresChatMessageHistory:
    """Retrieve the persistent Postgres-backed message history for a given session."""
    conn = _get_persistent_connection()
    return PostgresChatMessageHistory(
        PG_CHAT_HISTORY_TABLE_NAME,
        session_id,
        sync_connection=conn,
    )


def clear_session_history(session_id: str) -> None:
    """Clear all chat messages for a specific session."""
    try:
        history = get_session_history(session_id)
        history.clear()
    except Exception as exc:
        logger.error("Failed to clear session history for %s: %s", session_id, exc)


def delete_session_history(session_id: str) -> None:
    """Hard delete all chat history records for a session from the database."""
    try:
        with psycopg.connect(get_raw_connection_string(), autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {PG_CHAT_HISTORY_TABLE_NAME} WHERE session_id = %s::uuid",
                    (session_id,),
                )
    except Exception as exc:
        logger.error("Failed to delete session history for %s: %s", session_id, exc)