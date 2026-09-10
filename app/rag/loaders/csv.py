from pathlib import Path

from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document

from app.rag.loaders.base import BaseDocumentLoader


class CSVDocumentLoader(BaseDocumentLoader):
    """Document loader for Comma-Separated Values (.csv) files."""

    def _load_documents(self, file_path: Path) -> list[Document]:
        loader = CSVLoader(str(file_path))
        return loader.load()
