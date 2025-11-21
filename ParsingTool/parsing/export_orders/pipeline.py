"""Export-orders pipeline using shared EXPORT_FIELD_PATTERNS.

This module parses an export-order PDF into a one-row CSV. It relies on the
shared EXPORT_FIELD_PATTERNS so that the regex definitions are centralised
and consistent with the simple `parse_pdf` helper.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import re

import pandas as pd

from ..shared.pdf_utils import extract_text
from ..shared.export_patterns import EXPORT_FIELD_PATTERNS
from ..qc import EXPECTED_COLUMNS

# Backwards-compat alias: some existing code may still import FIELD_PATTERNS
FIELD_PATTERNS = EXPORT_FIELD_PATTERNS

FLAGS = re.IGNORECASE | re.MULTILINE


def _find_line(pattern: str, text: str) -> str:
    """Return the first capture group for the given pattern in the text."""
    match = re.search(pattern, text, FLAGS)
    return match.group(1).strip() if match else ""


def parse_export_text(text: str) -> Dict[str, Any]:
    """Parse raw PDF text into a dict of field -> value using shared patterns."""
    return {
        field: _find_line(pattern, text)
        for field, pattern in FIELD_PATTERNS.items()
    }


def _extract_text_compat(path: str, debug: bool, use_ocr: bool) -> str:
    """Call `extract_text` but stay compatible with simple monkeypatched fakes."""
    try:
        return extract_text(path, debug=debug, use_ocr=use_ocr)
    except TypeError:
        # Likely a simple fake/monkeypatch that only takes `path`.
        return extract_text(path)


def parse_export_pdf(
    pdf_path: Path | str,
    debug: bool = False,
    use_ocr: bool = False,
) -> pd.DataFrame:
    """Parse a single export-order PDF into a one-row DataFrame.

    The resulting DataFrame uses EXPECTED_COLUMNS for a stable column order
    and fills any missing fields with empty strings.
    """
    pdf_path = Path(pdf_path)
    text = _extract_text_compat(str(pdf_path), debug=debug, use_ocr=use_ocr)
    fields = parse_export_text(text)

    row = [fields.get(column, "") for column in EXPECTED_COLUMNS]
    return pd.DataFrame([row], columns=EXPECTED_COLUMNS)


def run(
    input_pdf: Path | str,
    out: Path | str,
    debug: bool = False,
    use_ocr: bool = False,
) -> None:
    """High-level entry point: parse an export-order PDF and write a CSV."""
    df = parse_export_pdf(input_pdf, debug=debug, use_ocr=use_ocr)

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
