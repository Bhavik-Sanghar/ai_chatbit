from app.chat.chain import build_chat_chain


class ChatService:

    def __init__(self):
        self.chain = build_chat_chain()

    def chat(self, session_id: str, question: str) -> str:
        response = self.chain.invoke(
            {"question": question},
            config={
                "configurable": {
                    "session_id": session_id
                }
            },
        )

        return response