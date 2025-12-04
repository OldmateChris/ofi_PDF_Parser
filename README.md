# ParsingTool

Turn one or many PDFs into tidy CSV rows. If normal text extraction fails, it can try OCR. You can run it from the command line (good for batches) or a simple windowed app (GUI).

## What it does

* **Gets text from PDFs**
  Tries **PyMuPDF** first, then **PyPDF2**. If that gives nothing and you ask for it, it can fall back to **Tesseract OCR** (via `pdf2image`).
* **Finds key fields with patterns**
  Uses label-aware regex and parsing logic to pull fields like Delivery Number, Date, Grade, Size (plus others), depending on the document type.
* **Writes consistent CSVs**
  Stable column order, UTF‑8 with BOM where appropriate.
  Optionally writes a simple **QC report** (`qc_report.md`) that highlights missing/odd values.
* **Works on a single file or a whole folder**
  CLI is best for batches; GUI is easiest to click through.
* **Responsive GUI**
  The GUI runs processing in the background, so the window stays responsive even when parsing hundreds of files.

## Install

> You only need a Python virtual environment and the Python packages. All dependencies and entry points are declared in `pyproject.toml`.

```bash
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2) Install ParsingTool (and its dependencies) from pyproject.toml
pip install .
```

This will:

* Install all dependencies under `[project].dependencies` in `pyproject.toml`.
* Install the `ParsingTool` package itself.
* Register the console scripts:

  * `parsingtool` (CLI)
  * `parsingtool-gui` (GUI launcher)

### Optional system tools (only if you use OCR)

If you plan to use OCR fallback (available for Domestic, Export and Packing List modes):

* **Tesseract OCR** (binary `tesseract` on PATH)
* **Poppler** (used by `pdf2image`; binaries like `pdftoppm` on PATH)

Windows users sometimes set environment variables for these (e.g., `TESSERACT_OCR`, `POPPLER_PATH`), but having them on `PATH` is usually sufficient.

> If you do not enable OCR in the CLI/GUI, you do not need Tesseract/Poppler.

## How to run

### Command line (recommended)

The CLI is exposed as the `parsingtool` command and uses subcommands for different document types.

#### Domestic ZAPI PDFs → Batches & SSCC CSVs

```bash
parsingtool domestic INPUT.pdf \
  --out-batches path/to/batches.csv \
  --out-sscc path/to/sscc.csv \
  --ocr
```

* `INPUT.pdf` – source Domestic ZAPI PDF.
* `--out-batches` – output CSV for batch-level data.
* `--out-sscc` – output CSV for SSCC data.
* `--ocr` – (Optional) Enable OCR fallback if text extraction fails.

#### Export PDFs → Single CSV

```bash
parsingtool export INPUT.pdf \
  --out path/to/export.csv \
  --ocr
```

* `INPUT.pdf` – source Export order PDF.
* `--out` – output CSV for all rows.
* `--ocr` – (Optional) Enable OCR fallback if text extraction fails.

#### Packing List PDFs → Single CSV

```bash
parsingtool packinglist INPUT.pdf \
  --out path/to/packing_list.csv \
  --ocr
```

* `INPUT.pdf` – source Packing List PDF (e.g. `*_PI.pdf`).
* `--out` – output CSV for packing list details.
* `--ocr` – (Optional) Enable OCR fallback if text extraction fails.

You can always inspect available options with:

```bash
parsingtool --help
parsingtool domestic --help
parsingtool export --help
parsingtool packinglist --help
```

#### Running without installing console scripts (alternative)

If you prefer not to install console entry points, you can run via the module directly from the project root:

```bash
python -m ParsingTool.parsing.cli domestic INPUT.pdf --out-batches path/to/batches.csv --out-sscc path/to/sscc.csv

python -m ParsingTool.parsing.cli export INPUT.pdf --out path/to/export.csv

python -m ParsingTool.parsing.cli packinglist INPUT.pdf --out path/to/packing_list.csv
```

### GUI (simple window)

After installation, you can start the GUI with:

```bash
parsingtool-gui
```

or, equivalently from the project root:

```bash
python -m ParsingTool.main
```

The GUI lets you:

* Pick a single PDF or a folder of PDFs.
* Choose an output folder.
* Toggle options such as OCR (works for all modes), debug mode, and QC report generation.
* **Process in background**: The UI remains responsive while processing files.

When it finishes, it writes the CSV outputs (and optional QC report) into your chosen output folder and shows a brief summary.

## Outputs

* **Domestic ZAPI PDFs**: Generates two CSV files per input PDF (or merged if processing a folder):

  * `*_batches.csv`: Batch-level details.
  * `*_sscc.csv`: SSCC-level details.
* **Export PDFs**: Generates a single CSV file with all order details.
* **Packing List PDFs**: Generates a single CSV file with packing list details.
* **QC Report**: Optional markdown report (`qc_report.md`) highlighting potential issues (Export mode only).

## Project layout

The high‑level layout for this version of the project is:

```text
ParsingTool/
  ParsingTool/
    __init__.py
    main.py                 # tiny launcher for the GUI
    parsing/
      cli.py                # command-line entry (subcommands: domestic, export, packinglist)
      gui.py                # Tkinter app
      domestic_zapi/        # domestic ZAPI-specific parsing pipeline
      export_orders/        # export order parsing pipeline
      packing_list/         # packing list parsing pipeline
      shared/               # shared helpers (PDF, dates, CSV, patterns, etc.)
      __init__.py
  pyproject.toml            # project metadata, dependencies, console scripts
  README.md                 # this file
  tests/                    # tests and sample PDFs
```

The exact internal modules (`domestic_zapi`, `export_orders`, `packing_list`, etc.) may vary, but `cli.py` and `main.py` are the primary entry points for the CLI and GUI, and `pyproject.toml` is the single source of truth for installation.

## Tips & next steps

* Keep real PDFs out of the repo; use redacted samples in a `tests/` or `samples/` folder.
* When you change dependencies, update only `pyproject.toml` and reinstall with `pip install .`.
* If you later add new modes (e.g., additional document types), extend `cli.py` with another subcommand and wire it to the appropriate pipeline.
