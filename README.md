# ParsingTool

A robust PDF parsing application designed to extract structured data from "Domestic" (ZAPI) and "Export" (ZAPA/PI) packing lists. It features a modern GUI, automatic Regex-based extraction, and a seamless OCR fallback for scanned documents.

## How It Works (The Architecture)

The application follows a clean **MVC (Model-View-Controller)** pattern, separating the visual interface from the business logic.

### 1. The High-Level Flow
*   **Entry Point:** `main.py` launches the application.
*   **The Controller:** Found in `core/controller.py`, this is the "Brain".
    *   The GUI (`interfaces/gui`) sends user actions (like "Run Batch") to the Controller.
    *   The Controller determines the file type and selects the appropriate **Pipeline**.
    *   It manages background threads to keep the UI responsive while processing.

### 2. The Data Pipeline (Step-by-Step)
*   **Domestic Pipeline:**
    *   **Trigger:** Controller detects `Domestic` mode.
    *   **Action:** calls `parsing/domestic_zapi`.
    *   **Logic:** Uses strict Regex to extract sscc codes (18-20 digits) and batch lines.
    *   **Output:** `domestic_batches.csv` and `domestic_sscc.csv`.

*   **Export Pipeline:**
    *   **Trigger:** Controller detects `Export` mode.
    *   **Action:** calls `parsing/export_orders`.
    *   **Logic:** Uses keyword matching (Dictionary approach) to parse headers and line items.
    *   **Output:** `export_combined.csv`.

## Project Structure

```text
ParsingTool/
├── main.py                # Entry point
├── core/
│   └── controller.py      # The "Brain" - orchestrates GUI and Parsers
├── interfaces/
│   └── gui/               # The User Interface (Windows, Buttons)
├── parsing/               # The "Workhorse" Logic
│   ├── domestic_zapi/     # Domestic Pipeline (Regex-heavy)
│   ├── export_orders/     # Export Pipeline (Keyword-heavy)
│   └── shared/            # Common Utilities (PDF Reading, Schemas)
└── common/
    └── system.py          # System checks (OCR availability, etc.)
```

## How to Run

**1. Setup Environment**

We use `pyproject.toml` for dependency management. Install the project in **editable mode** so any changes you make are immediately reflected:

```bash
pip install -e .
```

*Note: This command reads `pyproject.toml` and installs all required packages (pandas, pymupdf, pytesseract, etc.).*

**2. Launch the App**
```bash
python main.py
```
