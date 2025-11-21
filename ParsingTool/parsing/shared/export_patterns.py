"""Shared regular expression patterns for export-order PDFs.

This module centralises the field name -> regex mapping so that both the
export pipeline and any simple parsers (for example GUI helpers) can use the
same, canonical definitions.

Each pattern is expected to contain exactly one *capturing group* which
represents the value to extract from the line.
"""

from __future__ import annotations

from typing import Dict

# Matches the rest of a line after the label (non-newline characters)
LINE = r"([^\n]+)"

# Canonical mapping of field name -> regex pattern
EXPORT_FIELD_PATTERNS: Dict[str, str] = {
    "Name": rf"^\s*Name[:\s]+{LINE}$",
    "Date Requested": r"^\s*Date\s*Requested[:\s]+([\d\-/]+)$",
    "Delivery Number": r"^\s*Delivery\s*Number[:\s]+([\w-]+)$",
    "Sale Order Number": r"^\s*Sale\s*Order\s*Number[:\s]+([\w-]+)$",
    "Batch Number": r"^\s*Batch\s*Number[:\s]+([\w-]+)$",
    "SSCC Qty": r"^\s*SSCC\s*Qty[:\s]+([\w-]+)$",
    "Vessel ETD": r"^\s*Vessel\s*ETD[:\s]+([\w\-/]+)$",
    "Destination": rf"^\s*Destination[:\s]+{LINE}$",
    "3rd Party Storage": rf"^\s*3rd\s*Party\s*Storage[:\s]+{LINE}$",
    "Variety": rf"^\s*Variety[:\s]+{LINE}$",
    "Grade": r"^\s*Grade[:\s]+([\w]+)$",
    "Size": r"^\s*Size[:\s]+([\w/]+)$",
    "Packaging": rf"^\s*Packaging[:\s]+{LINE}$",
    "Pallet": r"^\s*Pallet[:\s]+([\w-]+)$",
    "Fumigation": rf"^\s*Fumigation[:\s]+{LINE}$",
    "Container": r"^\s*Container[:\s]+([\w-]+)$",
}
