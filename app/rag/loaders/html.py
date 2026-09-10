from pathlib import Path

from bs4 import BeautifulSoup
from langchain_core.documents import Document

from app.rag.loaders.base import BaseDocumentLoader


class HTMLDocumentLoader(BaseDocumentLoader):
    """Document loader for HTML (.html, .htm) files."""

    def _load_documents(self, file_path: Path) -> list[Document]:
        try:
            raw_html = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_html = file_path.read_text(encoding="latin-1")

        soup = BeautifulSoup(raw_html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        text = soup.get_text(separator="\n")

        # Clean up excess whitespace
        lines = [line.strip() for line in text.splitlines()]
        cleaned_text = "\n".join(chunk for chunk in lines if chunk)

        metadata = {"source": str(file_path)}
        if title:
            metadata["title"] = title

        return [
            Document(
                page_content=cleaned_text,
                metadata=metadata,
            )
        ]
