from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from app.rag.loaders.base import BaseDocumentLoader


class PDFDocumentLoader(BaseDocumentLoader):
    """Document loader for PDF files."""

    def _load_documents(self, file_path: Path) -> list[Document]:
        loader = PyPDFLoader(str(file_path))
        documents = loader.load()

        for document in documents:
            document.metadata["page"] = document.metadata.get("page", 0)

        return documents
