from app.rag.vectorstore import VectorStoreManager


class SessionRetriever:

    def __init__(
        self,
        vectorstore_manager: VectorStoreManager,
    ):
        self.vectorstore_manager = vectorstore_manager

    def invoke(
        self,
        query: str,
        document_ids: list[str],
    ):
        return self.vectorstore_manager.search(
            document_ids=document_ids,
            query=query,
        )