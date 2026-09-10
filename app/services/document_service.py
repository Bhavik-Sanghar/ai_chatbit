from pathlib import Path

from app.rag.loaders import load_document
from app.rag.splitter import split_documents
from app.rag.vectorstore import VectorStoreManager


class DocumentService:

    def __init__(
        self,
        vectorstore_manager: VectorStoreManager,
    ):
        self.vectorstore_manager = vectorstore_manager

    def index_document(
        self,
        file_path: str | Path,
    ) -> str:
        documents = load_document(file_path)
        if not documents:
            raise ValueError(f"No content could be extracted from {Path(file_path).name}")

        chunks = split_documents(documents)
        if not chunks:
            raise ValueError(f"No text chunks could be generated from {Path(file_path).name}")

        document_id = chunks[0].metadata["document_id"]

        self.vectorstore_manager.add_document(
            document_id=document_id,
            chunks=chunks,
        )

        return document_id