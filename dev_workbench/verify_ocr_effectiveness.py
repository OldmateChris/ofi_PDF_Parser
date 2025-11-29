
import sys
import os
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ParsingTool.parsing.export_orders.pipeline import parse_export_pdf

def verify_ocr_effectiveness():
    input_dir = Path("input")
    if not input_dir.exists():
        print("Input directory 'input/' not found.")
        return

    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in 'input/'.")
        return

    print(f"Found {len(pdfs)} PDFs. Running verification...\n")

    for pdf in pdfs:
        print(f"Checking {pdf.name}...")
        
        # Run without OCR
        try:
            df_no_ocr = parse_export_pdf(pdf, use_ocr=False)
            batches_no_ocr = len(df_no_ocr[df_no_ocr["Batch Number"].astype(bool)])
        except Exception as e:
            print(f"  Standard run failed: {e}")
            batches_no_ocr = 0

        # Run with OCR
        try:
            df_ocr = parse_export_pdf(pdf, use_ocr=True)
            batches_ocr = len(df_ocr[df_ocr["Batch Number"].astype(bool)])
        except Exception as e:
            print(f"  OCR run failed: {e}")
            batches_ocr = 0

        # Compare
        if batches_ocr > batches_no_ocr:
            status = "OCR REQUIRED"
        elif batches_ocr == batches_no_ocr:
            status = "OCR NOT NEEDED"
        else:
            status = "OCR WORSE (Check this!)"

        print(f"  Standard={batches_no_ocr} batches, OCR={batches_ocr} batches ({status})")
        print("-" * 40)

if __name__ == "__main__":
    verify_ocr_effectiveness()
