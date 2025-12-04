"""Packing List (PI) pipeline.

Specialised for '_PI.pdf' files which explicitly list PAL quantities
and have a cleaner 'Packer' layout than ZAPI files.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import re
import pandas as pd
from ..shared.pdf_utils import extract_text
from ..shared.export_patterns import EXPORT_FIELD_PATTERNS
from ..qc import EXPECTED_COLUMNS

# Reuse your shared patterns
FIELD_PATTERNS = EXPORT_FIELD_PATTERNS
FLAGS = re.IGNORECASE | re.MULTILINE

def _find_line(pattern: str, text: str) -> str:
    """Helper to find a single value using a regex pattern."""
    match = re.search(pattern, text, FLAGS)
    if match:
        val = match.group(1).strip()
        # Filter out common header noise if the regex grabs the label itself
        if val.lower() in ["sale", "date", "delivery", "booking", "quantity", "description"]:
            return ""
        return val
    return ""

def parse_pi_pdf(
    pdf_path: Path | str,
    debug: bool = False,
    use_ocr: bool = False,
) -> pd.DataFrame:
    pdf_path = Path(pdf_path)
    text = extract_text(str(pdf_path), debug=debug, use_ocr=use_ocr)

    fields = {}

    # 1. Standard Fields (Headers)
    for field, pattern in FIELD_PATTERNS.items():
        fields[field] = _find_line(pattern, text)

    # 2. PI-Specific: Explicit Pallet Count
    # PI files have a column "22.000 PAL" which ZAPIs do not.
    # We grab this directly instead of calculating it.
    pal_match = re.search(r"\b(\d+(?:[.,]\d+)?)\s+PAL\b", text, FLAGS)
    if pal_match:
        fields["SSCC Qty"] = f"{pal_match.group(1).strip()} PAL"

    # 3. PI-Specific: Packer
    # PI files usually list "Packer:" then the name on the next line.
    packer_match = re.search(r"Packer\s*[:\s]*\n([^\n]+)", text, FLAGS)
    if packer_match:
        val = packer_match.group(1).strip()
        if "Seaway" in val or "RJN" in val or "Olam" in val:
            fields["3rd Party Storage"] = val

    # 4. Product Description (Simplified)
    # PIs usually have the description line starting with "Almonds" or "Kern"
    # and often include the Grade/Size in that same line.
    desc_match = re.search(r"^.*(?:Almonds|Kern|Inshell).*$", text, FLAGS)
    if desc_match:
        raw_desc = desc_match.group(0).strip()
        # Clean up leading material codes (e.g. "8571/0802...")
        clean_desc = re.sub(r"^\s*\d+[\s/]+", "", raw_desc)
        fields["Variety"] = clean_desc # Default to full line
        
        # Extract Grade/Size from this clean line if possible
        if "XNo1" in clean_desc: fields["Grade"] = "XNo1"
        if "SSR" in clean_desc: fields["Grade"] = "SSR"
        if "Supr" in clean_desc: fields["Grade"] = "Supr"
        
        size_m = re.search(r"\b(\d{2}/\d{2})\b", clean_desc)
        if size_m: fields["Size"] = size_m.group(1)

        pack_m = re.search(r"\b(\d+(?:[.,]\d+)?)\s*(lb|kg|ctn)\b", clean_desc, re.IGNORECASE)
        if pack_m: fields["Packaging"] = pack_m.group(0)

    # 5. Build Row(s)
    row = [fields.get(c, "") for c in EXPECTED_COLUMNS]
    return pd.DataFrame([row], columns=EXPECTED_COLUMNS)

# --- THIS WAS THE MISSING PART ---
def run(
    *,
    input_pdf: str,
    out: str,
    use_ocr: bool = False,
    debug: bool = False,
) -> None:
    df = parse_pi_pdf(input_pdf, use_ocr=use_ocr, debug=debug)
    df.to_csv(out, index=False)
    if debug:
        print(f"Processed PI: {input_pdf}")