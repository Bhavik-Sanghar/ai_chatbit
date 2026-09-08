import uuid

from app.chat.memory import delete_session_history


class ChatSession:
    def __init__(self, session_id: str, title: str = "New Chat"):
        self.session_id = session_id
        self.title = title


class ChatSessionManager:

    def __init__(self):
        self.sessions: dict[str, ChatSession] = {}

    def create_session(self, title: str = "New Chat") -> ChatSession:
        session_id = str(uuid.uuid4())

        session = ChatSession(
            session_id=session_id,
            title=title,
        )

        self.sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> ChatSession | None:
        return self.sessions.get(session_id)

    def list_sessions(self) -> list[ChatSession]:
        return list(self.sessions.values())

    def delete_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)
        delete_session_history(session_id)