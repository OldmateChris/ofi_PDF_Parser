from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# These are the columns your CSVs should have in this order.
EXPECTED_COLUMNS: List[str] = [
    "Name","Date Requested","OLAM Ref Number","Delivery Number","Sale Order Number",
    "Batch Number","SSCC Qty","Vessel ETD","Destination","3rd Party Storage",
    "Variety","Grade","Size","Packaging","Pallet","Fumigation","Container"
]

# Valid Grade values (adjust as needed).
VALID_GRADES = {"SSR","Supr","Xno1","Rejects"}

def validate(df: pd.DataFrame, source_name: str) -> Dict[str, Any]:
    """Lightweight QC checks.
    - Ensures all expected columns are present.
    - Counts rows with unexpected Grade values.
    - Checks Size looks like '12/34' or 'NA' (tweak if your format differs).
    """
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]

    # Validate Grade
    if "Grade" in df.columns:
        grade_series = df["Grade"].fillna("")
        invalid_grade = int((~grade_series.isin(VALID_GRADES)).sum())
    else:
        invalid_grade = 0

    # Validate Size
    if "Size" in df.columns:
        size_series = df["Size"].fillna("")
        invalid_size = int((~size_series.astype(str).str.match(r"^\d{2}/\d{2}$|^NA$", na=False)).sum())
    else:
        invalid_size = 0

    return {
        "source": source_name,
        "missing_columns": missing_cols,
        "invalid_grade": invalid_grade,
        "invalid_size": invalid_size,
    }

def write_report(results, out_path, extra_notes=None):
    """Write a simple Markdown QC report."""
    lines = ["# QC Report\n"]
    total = len(results)
    blocked = 0
    for r in results:
        missing = ", ".join(r["missing_columns"]) if r["missing_columns"] else "None"
        lines += [
            f"## {r['source']}",
            f"- Missing columns: {missing}",
            f"- Invalid grade rows: {r['invalid_grade']}",
            f"- Invalid size rows: {r['invalid_size']}\n",
        ]
        if r["missing_columns"] or r["invalid_grade"] or r["invalid_size"]:
            blocked += 1
    lines.append(f"\n**Summary:** {blocked}/{total} had QC issues.\n")
    if extra_notes:
        lines.append("### Notes\n")
        lines += [f"- {n}" for n in extra_notes]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
