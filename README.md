# ParsingTool

Turn one or many PDFs into tidy CSV rows. If normal text extraction fails, it can try OCR. You can run it from the command line (good for batches) or a simple windowed app (GUI).

## What it does

- **Gets text from PDFs**  
  Tries **PyMuPDF** first, then **PyPDF2**. If that gives nothing and you ask for it, it tries **Tesseract OCR** (via `pdf2image`).
- **Finds key fields with patterns**  
  Uses label-aware regex to pull fields like Delivery Number, Date, Grade, Size (plus others).
- **Writes a consistent CSV**  
  One row per PDF, stable column order, UTF-8 with BOM.  
  Optionally writes a simple **QC report** (`qc_report.md`) that highlights missing/odd values.
- **Works on a single file or a whole folder**  
  CLI is best for batches; GUI is easiest to click through.

## Install

> You only need a Python venv and the Python packages.

```bash
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt
```

### Optional system tools (only if you use `--ocr`)
- **Tesseract OCR** (binary `tesseract` on PATH)
- **Poppler** (used by `pdf2image`; binaries like `pdftoppm` on PATH)
- Windows users sometimes set environment variables for these (e.g., `TESSERACT_OCR`, `POPPLER_PATH`), but PATH works too.

> If you don’t use `--ocr`, you don’t need Tesseract/Poppler.

## How to run

### Command line (recommended)

```bash
# Single PDF
python -m ParsingTool.parsing.cli --file path/to/input.pdf --out path/to/output --qc-report

# A folder of PDFs
python -m ParsingTool.parsing.cli --folder path/to/folder --out path/to/output --qc-report

# If you want OCR fallback and debug logs
python -m ParsingTool.parsing.cli --file path/to/input.pdf --out path/to/output --ocr --debug
```

**Outputs**
- CSV files saved to your `--out` folder.  
  If a Delivery Number is found, it’s used in the filename; otherwise it uses the PDF name.
- If you add `--qc-report`, you’ll also get `--out/qc_report.md`.

### GUI (simple window)

```bash
python -m ParsingTool.parsing.main
```

Pick a file or folder, choose an output folder, and toggle OCR/Debug/QC options.  
You’ll see a small summary at the end.

## Project layout

```
ParsingTool/
  ParsingTool/
    parsing/
      cli.py                  # command-line entry
      main.py                 # tiny launcher for the GUI
      gui.py                  # Tkinter app
      pdf_parser.py           # extraction + field parsing
      qc.py                   # column order + quick checks + QC report
      merge_with_overrides.py # optional: apply manual corrections
      parser.py               # thin compatibility shim
      __init__.py
  README.md
  requirements.txt
  .gitignore
  tests/                     # add samples/tests here as you go
```

## Tips & next steps

- Keep real PDFs out of the repo; use redacted samples in a `samples/` folder.  
- If you want easy `parsingtool` / `parsingtool-gui` commands later, we can add console scripts in `pyproject.toml`. For now, the `python -m …` commands above are reliable and portable.
- Planning to support **domestic orders** too? Add a new `domestic_parser.py` and a `--mode domestic` flag in `cli.py`—happy to sketch that when you’re ready.
