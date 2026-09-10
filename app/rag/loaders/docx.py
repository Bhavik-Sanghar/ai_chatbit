from pathlib import Path

import docx2txt
from langchain_core.documents import Document

from app.rag.loaders.base import BaseDocumentLoader


class DocxDocumentLoader(BaseDocumentLoader):
    """Document loader for Microsoft Word (.docx) files."""

    def _load_documents(self, file_path: Path) -> list[Document]:
        content = docx2txt.process(str(file_path)) or ""
        return [
            Document(
                page_content=content.strip(),
                metadata={"source": str(file_path)},
            )
        ]
