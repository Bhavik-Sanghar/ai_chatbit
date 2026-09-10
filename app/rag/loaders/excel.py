from pathlib import Path

from langchain_core.documents import Document
import pandas as pd

from app.rag.loaders.base import BaseDocumentLoader


class ExcelDocumentLoader(BaseDocumentLoader):
    """Document loader for Excel spreadsheets (.xlsx, .xls)."""

    def _load_documents(self, file_path: Path) -> list[Document]:
        documents: list[Document] = []
        excel_data = pd.read_excel(str(file_path), sheet_name=None)

        for sheet_name, df in excel_data.items():
            if df.empty:
                continue

            for row_idx, row in df.iterrows():
                row_items = [
                    f"{col}: {val}"
                    for col, val in row.items()
                    if pd.notna(val)
                ]
                row_text = ", ".join(row_items)
                if row_text.strip():
                    documents.append(
                        Document(
                            page_content=row_text,
                            metadata={
                                "source": str(file_path),
                                "sheet": sheet_name,
                                "row": int(str(row_idx)),
                            },
                        )
                    )

        if not documents:
            documents.append(
                Document(
                    page_content="",
                    metadata={"source": str(file_path)},
                )
            )

        return documents
