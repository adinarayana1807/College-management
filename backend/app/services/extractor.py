"""Text extractor helpers (PDF)."""
from pathlib import Path
from typing import Optional

try:
    from pypdf import PdfReader
except Exception:
    # older library name
    from PyPDF2 import PdfReader


def extract_text_from_pdf(path: Path) -> str:
    text = []
    try:
        reader = PdfReader(str(path))
        for p in reader.pages:
            try:
                page_text = p.extract_text() or ""
            except Exception:
                page_text = ""
            text.append(page_text)
    except Exception:
        return ""
    return "\n".join(text)
