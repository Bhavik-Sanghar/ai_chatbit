from dataclasses import dataclass


@dataclass
class DocumentRecord:
    document_id: str
    filename: str
    file_path: str