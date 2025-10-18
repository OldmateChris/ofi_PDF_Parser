from pathlib import Path
import argparse
import pandas as pd

from .pdf_parser import parse_pdf
from .qc import validate, write_report

def parse_one(pdf_path: Path, outdir: Path, debug: bool=False, use_ocr: bool=False) -> Path:
    df = parse_pdf(pdf_path, debug=debug, use_ocr=use_ocr)
    # Try to include a useful stem in the filename
    base = str(df.iloc[0].get("Delivery Number") or "").strip() or pdf_path.stem
    out = outdir / f"parsed_{base}.csv"
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"[saved] {out}")
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(description="Parse PDF(s) into CSVs.")
    ap.add_argument("--file", type=Path, help="Single PDF to parse")
    ap.add_argument("--folder", type=Path, help="Folder containing PDFs")
    ap.add_argument("--out", type=Path, required=True, help="Output folder")
    ap.add_argument("--qc-report", action="store_true", help="Write a QC markdown report")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--ocr", action="store_true", help="Use OCR fallback (slower)")
    args = ap.parse_args(argv)

    if not args.file and not args.folder:
        ap.error("Provide --file or --folder")

    pdfs = [args.file] if args.file else sorted(p for p in args.folder.glob("*.pdf"))
    args.out.mkdir(parents=True, exist_ok=True)

    qc_results = []
    for p in pdfs:
        csv_path = parse_one(p, args.out, args.debug, args.ocr)
        df = pd.read_csv(csv_path, dtype=str).fillna("")
        qc_results.append(validate(df, p.name))

    if args.qc-report:
        report_path = args.out / "qc_report.md"
        write_report(qc_results, report_path)
        print(f"[qc] wrote {report_path}")

if __name__ == "__main__":
    main()
