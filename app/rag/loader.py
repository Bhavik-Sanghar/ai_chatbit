from pathlib import Path

from langchain_core.documents import Document

from app.rag.loaders import (
    BaseDocumentLoader,
    UnsupportedDocumentTypeError,
    get_document_loader,
    load_document,
)


def load_pdf(file_path: str | Path) -> list[Document]:
    """
    Backward-compatible loader function for PDF files.
    Delegates to the modular loader router.
    """
    return load_document(file_path)


__all__ = [
    "BaseDocumentLoader",
    "UnsupportedDocumentTypeError",
    "get_document_loader",
    "load_document",
    "load_pdf",
]