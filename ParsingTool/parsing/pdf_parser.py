from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Any
import pandas as pd

from .qc import EXPECTED_COLUMNS

# --- Helpers ---------------------------------------------------------------

FLAGS = re.IGNORECASE | re.MULTILINE


def _extract_text(pdf_path: Path, debug: bool = False) -> str:
    """Pull text from a PDF using lightweight extractors.

    We keep this simple: try PyMuPDF (fast, often accurate) then PyPDF2.
    We *don't* fail the whole run if extraction is empty—we'll still
    return an empty string so the OCR fallback (if enabled) can try.
    """
    text = ""

    # Try PyMuPDF first (usually better text extraction)
    try:
        import fitz  # PyMuPDF

        with fitz.open(str(pdf_path)) as doc:
            pages = [page.get_text() or "" for page in doc]
        text = "\n".join(pages)
        if debug:
            print("[info] Extracted text with PyMuPDF")
    except Exception as e1:
        if debug:
            print(f"[warn] PyMuPDF failed: {e1}")
        # Fallback: PyPDF2
        try:
            import PyPDF2

            reader = PyPDF2.PdfReader(str(pdf_path))
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages)
            if debug:
                print("[info] Extracted text with PyPDF2")
        except Exception as e2:
            if debug:
                print(f"[warn] PyPDF2 failed: {e2}")
            text = ""

    # Normalise newlines for consistent line-based matching
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _find_line(pattern: str, text: str) -> str:
    """Return the first capture group on the matching *line*.

    - Uses MULTILINE mode so ^ and $ mean start/end *of line*.
    - Captures everything up to the newline (no greedy cross-line issues).
    """
    m = re.search(pattern, text, FLAGS)
    return m.group(1).strip() if m else ""


def _parse_fields(text: str) -> Dict[str, Any]:
    """Simple label-aware regex extraction. Tune patterns as needed.

    We look for lines like:
        Label: value
    and capture everything to the end of that line.
    """
    # Common token class for 'rest of line'
    LINE = r"([^\n]+)"

    return {
        "Name": _find_line(rf"^\s*Name[:\s]+{LINE}$", text),
        "Date Requested": _find_line(r"^\s*Date\s*Requested[:\s]+([\d\-/]+)$", text),
        "Delivery Number": _find_line(r"^\s*Delivery\s*Number[:\s]+([\w-]+)$", text),
        "Sale Order Number": _find_line(r"^\s*Sale\s*Order\s*Number[:\s]+([\w-]+)$", text),
        "Batch Number": _find_line(r"^\s*Batch\s*Number[:\s]+([\w-]+)$", text),
        "SSCC Qty": _find_line(r"^\s*SSCC\s*Qty[:\s]+([\w-]+)$", text),
        "Vessel ETD": _find_line(r"^\s*Vessel\s*ETD[:\s]+([\w\-/]+)$", text),
        "Destination": _find_line(rf"^\s*Destination[:\s]+{LINE}$", text),
        "3rd Party Storage": _find_line(rf"^\s*3rd\s*Party\s*Storage[:\s]+{LINE}$", text),
        "Variety": _find_line(rf"^\s*Variety[:\s]+{LINE}$", text),
        "Grade": _find_line(r"^\s*Grade[:\s]+([\w]+)$", text),
        "Size": _find_line(r"^\s*Size[:\s]+([\w/]+)$", text),
        "Packaging": _find_line(rf"^\s*Packaging[:\s]+{LINE}$", text),
        "Pallet": _find_line(r"^\s*Pallet[:\s]+([\w-]+)$", text),
        "Fumigation": _find_line(rf"^\s*Fumigation[:\s]+{LINE}$", text),
        "Container": _find_line(r"^\s*Container[:\s]+([\w-]+)$", text),
    }


# --- Public API ------------------------------------------------------------

def parse_pdf(pdf_path: Path | str, debug: bool = False, use_ocr: bool = False) -> pd.DataFrame:
    """Parse a single PDF into a one-row DataFrame using EXPECTED_COLUMNS.

    This intentionally starts simple so you can gain confidence quickly.
    Improve the regexes over time as you see real-world cases.
    """
    pdf_path = Path(pdf_path)
    text = _extract_text(pdf_path, debug=debug)

    # Optional OCR fallback (only if extraction gave nothing)
    if use_ocr and not text.strip():
        try:
            from pdf2image import convert_from_path
            import pytesseract

            pages = convert_from_path(str(pdf_path))
            ocr_text = [pytesseract.image_to_string(im) for im in pages]
            text = "\n".join(ocr_text)
            if debug:
                print("[info] Extracted text with OCR")
        except Exception as e:
            if debug:
                print(f"[warn] OCR failed: {e}")

    fields = _parse_fields(text)

    # Create a one-row DataFrame with stable column order
    row = [fields.get(c, "") for c in EXPECTED_COLUMNS]
    return pd.DataFrame([row], columns=EXPECTED_COLUMNS)

