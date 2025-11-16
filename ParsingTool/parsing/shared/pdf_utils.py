from typing import List

# Keep dependencies simple: try PyPDF2 first; if not present, fallback to a minimal text read error.
try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None


def extract_text(path: str) -> str:
    """Extract plain text from a PDF file (simple best-effort)."""
    if PdfReader is None:
        raise RuntimeError("PdfReader not available. Please install PdfReader or wire another extractor.")

    txt_parts: List[str] = []
    with open(path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            try:
                txt_parts.append(page.extract_text() or "")
            except Exception:
                txt_parts.append("")
    return "\n".join(txt_parts)
