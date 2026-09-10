import tempfile
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document
import pandas as pd

from app.rag.loader import load_pdf
from app.rag.loaders import (
    BaseDocumentLoader,
    CSVDocumentLoader,
    DocxDocumentLoader,
    ExcelDocumentLoader,
    HTMLDocumentLoader,
    MarkdownDocumentLoader,
    PDFDocumentLoader,
    TextDocumentLoader,
    UnsupportedDocumentTypeError,
    get_document_loader,
    load_document,
)


class TestDocumentLoaders(unittest.TestCase):

    def test_router_selects_correct_loader(self):
        cases = [
            ("doc.pdf", PDFDocumentLoader),
            ("notes.txt", TextDocumentLoader),
            ("readme.md", MarkdownDocumentLoader),
            ("page.html", HTMLDocumentLoader),
            ("page.htm", HTMLDocumentLoader),
            ("data.csv", CSVDocumentLoader),
            ("report.docx", DocxDocumentLoader),
            ("sheet.xlsx", ExcelDocumentLoader),
            ("old_sheet.xls", ExcelDocumentLoader),
        ]
        for filename, expected_cls in cases:
            with self.subTest(filename=filename):
                loader = get_document_loader(filename)
                self.assertIsInstance(loader, expected_cls)

    def test_router_case_insensitive(self):
        cases = [
            "DOC.PDF",
            "Notes.Txt",
            "README.MD",
            "PAGE.HTML",
            "Page.Htm",
            "DATA.CSV",
            "REPORT.DOCX",
            "SHEET.XLSX",
            "Old.Xls",
        ]
        for filename in cases:
            with self.subTest(filename=filename):
                loader = get_document_loader(filename)
                self.assertIsInstance(loader, BaseDocumentLoader)

    def test_router_unsupported_extension_raises(self):
        unsupported = ["image.png", "archive.zip", "program.exe", "file.pptx"]
        for filename in unsupported:
            with self.subTest(filename=filename):
                with self.assertRaises(UnsupportedDocumentTypeError) as ctx:
                    get_document_loader(filename)
                self.assertIn("Unsupported document type", str(ctx.exception))
                self.assertIn(".pdf", str(ctx.exception))

    def test_missing_file_raises_file_not_found(self):
        loader = TextDocumentLoader()
        with self.assertRaises(FileNotFoundError):
            loader.load("non_existent_file_12345.txt")

    def test_text_loader(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("Hello text file content")
            f_path = Path(f.name)

        try:
            docs = load_document(f_path)
            self.assertIsInstance(docs, list)
            self.assertEqual(len(docs), 1)
            self.assertIn("Hello text file content", docs[0].page_content)
            self.assertEqual(docs[0].metadata["filename"], f_path.name)
            self.assertTrue(bool(docs[0].metadata.get("document_id")))
        finally:
            f_path.unlink(missing_ok=True)

    def test_markdown_loader(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# Title\n\n- Item 1\n- Item 2")
            f_path = Path(f.name)

        try:
            docs = load_document(f_path)
            self.assertIsInstance(docs, list)
            self.assertEqual(len(docs), 1)
            self.assertIn("# Title", docs[0].page_content)
            self.assertEqual(docs[0].metadata["filename"], f_path.name)
            self.assertTrue(bool(docs[0].metadata.get("document_id")))
        finally:
            f_path.unlink(missing_ok=True)

    def test_html_loader(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>My Test Page</title></head>
        <body>
            <script>console.log('ignore');</script>
            <h1>Main Heading</h1>
            <p>This is test paragraph text.</p>
        </body>
        </html>
        """
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(html_content)
            f_path = Path(f.name)

        try:
            docs = load_document(f_path)
            self.assertIsInstance(docs, list)
            self.assertEqual(len(docs), 1)
            self.assertIn("Main Heading", docs[0].page_content)
            self.assertNotIn("console.log", docs[0].page_content)
            self.assertEqual(docs[0].metadata.get("title"), "My Test Page")
            self.assertEqual(docs[0].metadata["filename"], f_path.name)
        finally:
            f_path.unlink(missing_ok=True)

    def test_csv_loader(self):
        csv_content = "Name,Department\nAlice,Engineering\nBob,Design\n"
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            f_path = Path(f.name)

        try:
            docs = load_document(f_path)
            self.assertIsInstance(docs, list)
            self.assertEqual(len(docs), 2)
            for doc in docs:
                self.assertIn("row", doc.metadata)
                self.assertEqual(doc.metadata["filename"], f_path.name)
                self.assertTrue(bool(doc.metadata.get("document_id")))
            # Verify uniform document_id across rows
            self.assertEqual(docs[0].metadata["document_id"], docs[1].metadata["document_id"])
        finally:
            f_path.unlink(missing_ok=True)

    def test_excel_loader(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f_path = Path(f.name)

        df = pd.DataFrame({
            "Employee": ["Carol", "Dave"],
            "Role": ["Manager", "Analyst"],
        })
        with pd.ExcelWriter(f_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Staff", index=False)

        try:
            docs = load_document(f_path)
            self.assertIsInstance(docs, list)
            self.assertEqual(len(docs), 2)
            self.assertIn("Carol", docs[0].page_content)
            self.assertEqual(docs[0].metadata["sheet"], "Staff")
            self.assertIn("row", docs[0].metadata)
            self.assertEqual(docs[0].metadata["filename"], f_path.name)
            self.assertEqual(docs[0].metadata["document_id"], docs[1].metadata["document_id"])
        finally:
            f_path.unlink(missing_ok=True)

    @patch("docx2txt.process")
    def test_docx_loader(self, mock_docx_process):
        mock_docx_process.return_value = "Extracted docx document text."
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            f.write(b"dummy")
            f_path = Path(f.name)

        try:
            docs = load_document(f_path)
            self.assertIsInstance(docs, list)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0].page_content, "Extracted docx document text.")
            self.assertEqual(docs[0].metadata["filename"], f_path.name)
            self.assertTrue(bool(docs[0].metadata.get("document_id")))
        finally:
            f_path.unlink(missing_ok=True)

    @patch("app.rag.loaders.pdf.PyPDFLoader")
    def test_pdf_loader_mock(self, mock_pypdf_loader):
        mock_instance = MagicMock()
        mock_instance.load.return_value = [
            Document(page_content="Page 1", metadata={"page": 0}),
            Document(page_content="Page 2", metadata={"page": 1}),
        ]
        mock_pypdf_loader.return_value = mock_instance

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-dummy")
            f_path = Path(f.name)

        try:
            docs = load_document(f_path)
            self.assertEqual(len(docs), 2)
            self.assertEqual(docs[0].metadata["document_id"], docs[1].metadata["document_id"])
            self.assertEqual(docs[0].metadata["filename"], f_path.name)
        finally:
            f_path.unlink(missing_ok=True)

    def test_document_id_consistency_across_multiple_docs(self):
        loader = CSVDocumentLoader()
        csv_content = "Col1,Col2\nA,1\nB,2\nC,3\n"
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            f_path = Path(f.name)

        try:
            custom_id = "test-custom-doc-id-123"
            docs = loader.load(f_path, document_id=custom_id)
            self.assertEqual(len(docs), 3)
            for doc in docs:
                self.assertEqual(doc.metadata["document_id"], custom_id)
        finally:
            f_path.unlink(missing_ok=True)

    def test_backward_compatible_load_pdf(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("Text via load_pdf test")
            f_path = Path(f.name)

        try:
            # Calling load_pdf from app.rag.loader delegates to load_document
            docs = load_pdf(f_path)
            self.assertEqual(len(docs), 1)
            self.assertIn("Text via load_pdf test", docs[0].page_content)
        finally:
            f_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
