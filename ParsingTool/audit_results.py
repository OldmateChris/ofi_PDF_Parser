
import pandas as pd
from pathlib import Path
import re

def audit_results(csv_path):
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: File not found at {path}")
        return

    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Auditing {len(df)} rows from {path}...\n")

    failures = []
    unique_failed_files = set()

    for index, row in df.iterrows():
        source_file = row.get('Source_File', f"Row_{index}")
        issues = []

        # 1. Empty Essential Fields
        for field in ['Variety', 'Grade', 'Packaging']:
            val = row.get(field)
            if pd.isna(val) or str(val).strip() == "":
                issues.append(f"Missing {field}")

        # 2. Garbage Data in Variety (Material Codes)
        variety = str(row.get('Variety', ''))
        # Check for strings starting with digits like "9054 /" or "26115"
        # Regex: Start of string, optional whitespace, digits, optional whitespace, slash or just digits?
        # User said: "starting with digits like '9054 /' or '26115'"
        if re.match(r"^\s*\d+[\s/]+", variety) or re.match(r"^\s*\d+\s*$", variety):
             issues.append(f"Garbage in Variety ('{variety}')")
        
        # Also check for the specific case mentioned in previous turns if relevant, but user gave specific examples.

        # 3. Missing Packer
        packer = row.get('3rd Party Storage')
        if pd.isna(packer) or str(packer).strip() == "":
            issues.append("Missing Packer")

        if issues:
            unique_failed_files.add(source_file)
            failures.append({
                "file": source_file,
                "issues": issues
            })

    # Report
    if not failures:
        print("No failures found! All rows passed the audit.")
    else:
        print(f"Found issues in {len(unique_failed_files)} unique files:\n")
        for f in failures:
            print(f"File: {f['file']}")
            for issue in f['issues']:
                print(f"  - {issue}")
            print("-" * 20)
        
        print(f"\nTotal unique files needing attention: {len(unique_failed_files)}")

if __name__ == "__main__":
    # Assuming running from project root
    audit_results("output/combined_results.csv")
