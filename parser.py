"""Extract plain text from PDF, DOCX, or raw strings."""

from __future__ import annotations

from io import BytesIO
from typing import Optional

import fitz  # PyMuPDF
from docx import Document


def extract_from_upload(uploaded_file) -> str:
    """Return text from a Streamlit UploadedFile (.pdf or .docx)."""
    if uploaded_file is None:
        return ""

    name = (uploaded_file.name or "").lower()
    data = uploaded_file.getvalue()

    if name.endswith(".pdf"):
        return extract_pdf(data)
    if name.endswith(".docx"):
        return extract_docx(data)

    raise ValueError("Unsupported file type. Use a .pdf or .docx file.")


def extract_pdf(data: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    if not data:
        return ""

    pages: list[str] = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            pages.append(page.get_text("text") or "")
    return _normalize("\n".join(pages))


def extract_docx(data: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    if not data:
        return ""

    document = Document(BytesIO(data))
    parts: list[str] = []

    for paragraph in document.paragraphs:
        if paragraph.text:
            parts.append(paragraph.text)

    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))

    return _normalize("\n".join(parts))


def extract_text_string(text: Optional[str]) -> str:
    """Normalize a pasted job-description (or other) string."""
    return _normalize(text or "")


def _normalize(text: str) -> str:
    """Collapse extra whitespace while preserving paragraph breaks."""
    lines = [" ".join(line.split()) for line in text.replace("\r\n", "\n").split("\n")]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()
