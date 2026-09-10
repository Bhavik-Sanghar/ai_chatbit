import logging
from langchain_core.documents import Document
from langchain_postgres import PGVector

from app.config.settings import (
    DATABASE_URL,
    PG_VECTOR_COLLECTION_NAME,
    RETRIEVAL_K,
)
from app.rag.embeddings import get_embedding_model

logger = logging.getLogger("ai_chatbit.rag.vectorstore")


class VectorStoreManager:
    """Persistent PostgreSQL VectorStore Manager using pgvector and langchain-postgres."""

    def __init__(
        self,
        collection_name: str = PG_VECTOR_COLLECTION_NAME,
        connection_url: str = DATABASE_URL,
    ):
        self.embedding_model = get_embedding_model()
        self.collection_name = collection_name
        self.connection_url = connection_url

        self.vector_store = PGVector(
            embeddings=self.embedding_model,
            collection_name=self.collection_name,
            connection=self.connection_url,
            use_jsonb=True,
        )
        self.vector_store.create_tables_if_not_exists()

    def add_document(
        self,
        document_id: str,
        chunks: list[Document],
    ) -> None:
        """Add document text chunks to the persistent PostgreSQL vector store."""
        if not chunks:
            return

        ids = []
        for index, chunk in enumerate(chunks):
            chunk.metadata["document_id"] = document_id
            chunk_id = chunk.metadata.get("chunk_id", f"{document_id}_{index}")
            ids.append(chunk_id)

        self.vector_store.add_documents(chunks, ids=ids)
        logger.info(
            "Indexed %d chunks for document_id '%s' into PostgreSQL.",
            len(chunks),
            document_id,
        )

    def search(
        self,
        document_ids: list[str],
        query: str,
        k: int = RETRIEVAL_K,
    ) -> list[Document]:
        """Perform similarity search on document chunks filtered by the specified document IDs."""
        if not document_ids:
            return []

        filter_clause = {"document_id": {"$in": document_ids}}

        return self.vector_store.similarity_search(
            query=str(query),
            k=k,
            filter=filter_clause,
        )

    def delete_document(self, document_id: str) -> None:
        """Remove all chunks associated with a document_id from the vector store."""
        try:
            # Delete via direct SQL from langchain_pg_embedding table
            from app.db.connection import get_engine
            from sqlalchemy import text

            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(
                    text(
                        "DELETE FROM langchain_pg_embedding "
                        "WHERE cmetadata->>'document_id' = :doc_id"
                    ),
                    {"doc_id": document_id},
                )
                conn.commit()
            logger.info("Deleted vectors for document_id '%s'", document_id)
        except Exception as exc:
            logger.error("Failed to delete vectors for %s: %s", document_id, exc)
