from langchain_core.chat_history import InMemoryChatMessageHistory


_SESSION_STORE: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = InMemoryChatMessageHistory()

    return _SESSION_STORE[session_id]


def clear_session_history(session_id: str) -> None:
    history = _SESSION_STORE.get(session_id)

    if history:
        history.clear()


def delete_session_history(session_id: str) -> None:
    _SESSION_STORE.pop(session_id, None)