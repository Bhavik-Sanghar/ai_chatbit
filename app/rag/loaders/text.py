from pathlib import Path

from langchain_core.documents import Document

from app.rag.loaders.base import BaseDocumentLoader


class TextDocumentLoader(BaseDocumentLoader):
    """Document loader for plain text (.txt) files."""

    def _load_documents(self, file_path: Path) -> list[Document]:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")

        return [
            Document(
                page_content=content,
                metadata={"source": str(file_path)},
            )
        ]
