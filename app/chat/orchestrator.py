from app.chat.router import build_router


class ChatOrchestrator:
    def __init__(
        self,
        chat_chain,
        rag_chain,
    ):
        self.router = build_router()
        self.chat_chain = chat_chain
        self.rag_chain = rag_chain

    def invoke(
        self,
        session_id: str,
        question: str,
        document_ids: list[str],
    ):
        decision = self.router.invoke(
            {
                "question": question,
            }
        )

        if decision.route == "document":
            return self.rag_chain.invoke(
                {
                    "question": question,
                    "document_ids": document_ids,
                },
                config={
                    "configurable": {
                        "session_id": session_id,
                    }
                },
            )

        return self.chat_chain.invoke(
            {"question": question},
            config={
                "configurable": {
                    "session_id": session_id,
                }
            },
        )
