from pathlib import Path

from langchain_core.documents import Document

from app.rag.loaders.base import BaseDocumentLoader, UnsupportedDocumentTypeError
from app.rag.loaders.csv import CSVDocumentLoader
from app.rag.loaders.docx import DocxDocumentLoader
from app.rag.loaders.excel import ExcelDocumentLoader
from app.rag.loaders.html import HTMLDocumentLoader
from app.rag.loaders.markdown import MarkdownDocumentLoader
from app.rag.loaders.pdf import PDFDocumentLoader
from app.rag.loaders.text import TextDocumentLoader

LOADER_REGISTRY: dict[str, type[BaseDocumentLoader]] = {
    ".pdf": PDFDocumentLoader,
    ".txt": TextDocumentLoader,
    ".md": MarkdownDocumentLoader,
    ".html": HTMLDocumentLoader,
    ".htm": HTMLDocumentLoader,
    ".csv": CSVDocumentLoader,
    ".docx": DocxDocumentLoader,
    ".xlsx": ExcelDocumentLoader,
    ".xls": ExcelDocumentLoader,
}

SUPPORTED_TYPES_STR = ", ".join(LOADER_REGISTRY.keys())


def get_document_loader(file_path: str | Path) -> BaseDocumentLoader:
    """
    Returns an instantiated BaseDocumentLoader corresponding to the file extension.
    Raises UnsupportedDocumentTypeError if the extension is not supported.
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    loader_cls = LOADER_REGISTRY.get(extension)
    if loader_cls is None:
        raise UnsupportedDocumentTypeError(
            f"Unsupported document type: {extension or path.name}. "
            f"Supported types: {SUPPORTED_TYPES_STR}"
        )

    return loader_cls()


def load_document(
    file_path: str | Path,
    document_id: str | None = None,
) -> list[Document]:
    """
    Resolves the appropriate loader and loads documents with uniform document_id.
    """
    loader = get_document_loader(file_path)
    return loader.load(file_path, document_id=document_id)
