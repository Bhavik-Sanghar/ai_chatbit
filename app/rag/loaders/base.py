from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from langchain_core.documents import Document


class UnsupportedDocumentTypeError(Exception):
    """Raised when an unsupported file type is requested for loading."""


class BaseDocumentLoader(ABC):
    """Abstract base class for document loaders."""

    def load(
        self,
        file_path: str | Path,
        document_id: str | None = None,
    ) -> list[Document]:
        """
        Loads documents from the given file path, ensuring consistent
        document_id and filename metadata are attached across all documents.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        doc_id = document_id or str(uuid4())
        documents = self._load_documents(path)

        for doc in documents:
            doc.metadata.setdefault("filename", path.name)
            doc.metadata.setdefault("page", 1)
            doc.metadata["document_id"] = doc_id

        return documents

    @abstractmethod
    def _load_documents(self, file_path: Path) -> list[Document]:
        """Subclasses implement format-specific document extraction."""
