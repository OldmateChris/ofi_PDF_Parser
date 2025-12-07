# Refactoring Roadmap: ParsingTool

## 1. The `GUI.py` Audit

### Identified Responsibilities (The "Spaghetti")
Currently, `GUI.py` is doing three distinct jobs:
1.  **View (UI Layout & Style)**: ~200 lines of `tkinter` code (Frames, Buttons, Labels) and hardcoded styling constants (`BG_MAIN`, `FONT_TITLE`, etc.).
2.  **Controller (Orchestration Logic)**: The `run_processing_thread` function is the biggest offender. It contains business logic that belongs in the core application, specifically:
    *   Iterating over lists of files.
    *   Auto-routing logic (e.g., detecting `_PI.PDF` vs normal export).
    *   **Batch & Combine Logic**: The logic to merge multiple CSVs into one is currently hardcoded inside the GUI thread, making it inaccessible to the CLI.
3.  **System Utilities**: Functions like `is_installed` and `update_ocr_status` are checking system state, which is a shared utility concern.

### Decomposition Strategy
We will break `GUI.py` into the following components:

| New File | Responsibility |
| :--- | :--- |
| `ui/theme.py` | Holds all constants: Colors (`BG_MAIN`), Fonts (`FONT_TITLE`), and style configurations. |
| `ui/components.py` | (Optional) specialized widgets if needed, but likely just `layout.py` is enough. |
| `ui/main_window.py` | The `tkinter` layout code. It initializes the window and widgets but contains *no business logic*. It takes a `controller` as an argument. |
| `core/controller.py` | **New Component**. This class accepts inputs (file lists, modes) and orchestrates the pipelines. It handles the threading, the "auto-routing" logic, and the "combine" logic. |
| `ui/app.py` | The entry point that initializes the `Controller`, creates the `MainWindow`, and starts the loop. |

---

## 2. Project Directory Reorganization

The current `ParsingTool/parsing` folder is overloaded. We will move to a "Feature-by-Package" structure that clearly separates the User Interface from the Core Logic.

### Proposed Structure

```text
ParsingTool/
├── core/                   # The "Business Logic" (formerly 'parsing')
│   ├── pipelines/          # The actual parsing engines
│   │   ├── domestic/       # (Renamed from domestic_zapi)
│   │   ├── export/         # (Renamed from export_orders)
│   │   └── packing/        # (Renamed from packing_list)
│   ├── controller.py       # The new orchestrator (extracted from GUI)
│   └── qc.py               # Quality Control logic
├── interfaces/             # The "Front Ends"
│   ├── gui/                # The GUI Application
│   │   ├── __init__.py
│   │   ├── app.py          # Entry point
│   │   ├── main_window.py  # Layout
│   │   └── theme.py        # Styles
│   └── cli/                # The CLI Application
│       └── main.py         # (Renamed from cli.py)
├── common/                 # Shared Utilities
│   ├── pdf_utils.py        # (Moved from shared/pdf_utils.py)
│   └── system.py           # (New home for is_installed checks)
└── main.py                 # Root entry point (optional wrapper)
```

---

## 3. The Action Plan

We will execute this in phases to ensure the application remains runnable at each step.

### Phase 1: Preparation & Utility Extraction
*   **Step 1**: Create the new directory structure (`core/pipelines`, `interfaces/gui`, `common`).
*   **Step 2**: Move `shared/pdf_utils.py` to `common/pdf_utils.py`.
*   **Step 3**: Extract the system check functions (`is_installed`) from `GUI.py` into `common/system.py`. Update `GUI.py` to import them.

### Phase 2: Core Logic Extraction (The Hard Part)
*   **Step 4**: Create `core/controller.py`.
*   **Step 5**: Move the `run_processing_thread` logic from `GUI.py` into a `ProcessingController` class in `core/controller.py`.
    *   *Crucial*: This class should yield progress updates or logs via a callback, rather than writing directly to a `tkinter` widget.
*   **Step 6**: Refactor `GUI.py` to instantiate this controller and pass a callback function for logging.
    *   *Checkpoint*: Run the GUI. It should work exactly as before, but the "heavy lifting" is now in `core`.

### Phase 3: UI Decomposition
*   **Step 7**: Extract `ui/theme.py` from `GUI.py`.
*   **Step 8**: Move the remaining `tkinter` layout code into `interfaces/gui/main_window.py`.
*   **Step 9**: Create `interfaces/gui/app.py` to wire everything together.

### Phase 4: Cleanup
*   **Step 10**: Move the existing pipeline folders (`export_orders`, etc.) into `core/pipelines/` and update imports.
*   **Step 11**: Delete the old `ParsingTool/parsing` folder once empty.
