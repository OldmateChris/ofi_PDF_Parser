import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import shutil
import threading
import csv  # NEW

# --- PIPELINE IMPORTS ---
from .export_orders.pipeline import parse_export_pdf
from .domestic_zapi import pipeline as domestic_pipeline
from .packing_list.pipeline import run as run_packing_pipeline
from .qc import validate, write_report
from .shared.pdf_utils import NoTextError  # NEW


# ---------------------------------------------------------------------------
# THEME SETTINGS
# ---------------------------------------------------------------------------
BG_MAIN   = "#acacac"
BG_PANEL  = "#b8b8b8"   # Slightly lighter for groups
BG_STATUS = "#302f2f"
ENTRY_BG  = "#686868"
ENTRY_FG  = "#65F008"
LOG_BG    = "#0C0C0C"
LOG_FG    = "#65F008"
BUTTON_BG = "#444444"
BUTTON_FG = "#ffffff"
FG_TEXT   = "#202124"
FG_OK     = "#65F008"
FG_ERROR  = "#ff0000"
FG_MUTED  = "#5f6368"

FONT_LABEL  = ("Ubuntu", 10)
FONT_ENTRY  = ("Share Tech Mono", 10)
FONT_BUTTON = ("Ubuntu", 11)
FONT_CHECK  = ("Ubuntu", 10)
FONT_LOG    = ("JetBrainsMono NF", 9)
FONT_STATUS_SIDE = ("Inconsolata ExtraExpanded", 9, "bold")   # smaller side labels
FONT_STATUS_MAIN = ("Inconsolata ExtraExpanded", 11, "bold")  # bigger center label
FONT_TITLE  = ("Ubuntu", 11, "bold")  # For group headers


def is_installed(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_gui() -> None:
    root = tk.Tk()
    root.title("ParsingTool v2.0")
    root.configure(bg=BG_MAIN)
    root.geometry("750x650")  # Set a reasonable default size

    # Layout: Main content expands, status bar fixed
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Main container frame to hold the "steps"
    main_frame = tk.Frame(root, bg=BG_MAIN, padx=10, pady=10)
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)

    # -------------------------------------------------------------------
    # STEP 1: INPUTS (LabelFrame)
    # -------------------------------------------------------------------
    step1 = tk.LabelFrame(
        main_frame,
        text=" 1. Select Files ",
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_TITLE,
    )
    step1.grid(row=0, column=0, sticky="ew", pady=(0, 10), ipady=5)
    step1.columnconfigure(1, weight=1)

    # File
    tk.Label(
        step1, text="Single PDF:", bg=BG_PANEL, fg=FG_TEXT, font=FONT_LABEL
    ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    file_entry = tk.Entry(
        step1,
        bg=ENTRY_BG,
        fg=ENTRY_FG,
        insertbackground=ENTRY_FG,
        font=FONT_ENTRY,
    )
    file_entry.grid(row=0, column=1, sticky="ew", padx=5)

    # Folder
    tk.Label(
        step1, text="OR Folder:", bg=BG_PANEL, fg=FG_TEXT, font=FONT_LABEL
    ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    folder_entry = tk.Entry(
        step1,
        bg=ENTRY_BG,
        fg=ENTRY_FG,
        insertbackground=ENTRY_FG,
        font=FONT_ENTRY,
    )
    folder_entry.grid(row=1, column=1, sticky="ew", padx=5)

    # Output
    tk.Label(
        step1, text="Output To:", bg=BG_PANEL, fg=FG_TEXT, font=FONT_LABEL
    ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    output_entry = tk.Entry(
        step1,
        bg=ENTRY_BG,
        fg=ENTRY_FG,
        insertbackground=ENTRY_FG,
        font=FONT_ENTRY,
    )
    output_entry.grid(row=2, column=1, sticky="ew", padx=5)

    # Buttons
    def browse_file():
        p = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if p:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, p)

    def browse_folder():
        p = filedialog.askdirectory()
        if p:
            folder_entry.delete(0, tk.END)
            folder_entry.insert(0, p)

    def browse_output():
        p = filedialog.askdirectory()
        if p:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, p)

    tk.Button(step1, text="Browse", command=browse_file, bg=BUTTON_BG, fg=BUTTON_FG).grid(
        row=0, column=2, padx=5
    )
    tk.Button(step1, text="Browse", command=browse_folder, bg=BUTTON_BG, fg=BUTTON_FG).grid(
        row=1, column=2, padx=5
    )
    tk.Button(step1, text="Browse", command=browse_output, bg=BUTTON_BG, fg=BUTTON_FG).grid(
        row=2, column=2, padx=5
    )

    # -------------------------------------------------------------------
    # STEP 2: MODE (LabelFrame)
    # -------------------------------------------------------------------
    step2 = tk.LabelFrame(
        main_frame,
        text=" 2. Document Type ",
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_TITLE,
    )
    step2.grid(row=1, column=0, sticky="ew", pady=(0, 10), ipady=5)

    mode_var = tk.StringVar(value="export")

    tk.Radiobutton(
        step2,
        text="Export Orders",
        variable=mode_var,
        value="export",
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_CHECK,
    ).pack(side="left", padx=20)

    tk.Radiobutton(
        step2,
        text="Domestic ZAPI",
        variable=mode_var,
        value="domestic",
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_CHECK,
    ).pack(side="left", padx=20)

    tk.Radiobutton(
        step2,
        text="Packing List (PI)",
        variable=mode_var,
        value="packinglist",
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_CHECK,
    ).pack(side="left", padx=20)

    # -------------------------------------------------------------------
    # STEP 3: OPTIONS (LabelFrame - "Advanced")
    # -------------------------------------------------------------------
    step3 = tk.LabelFrame(
        main_frame,
        text=" 3. Advanced Options ",
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_TITLE,
    )
    step3.grid(row=2, column=0, sticky="ew", pady=(0, 10), ipady=5)

    debug_var = tk.BooleanVar(value=False)
    ocr_var = tk.BooleanVar(value=False)
    qc_var = tk.BooleanVar(value=True)

    ocr_check = tk.Checkbutton(
        step3,
        text="Enable OCR Fallback (Slow)",
        variable=ocr_var,
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_CHECK,
    )
    ocr_check.pack(side="left", padx=10)

    tk.Checkbutton(
        step3,
        text="Generate QC Report (Export Only)",
        variable=qc_var,
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_CHECK,
    ).pack(side="left", padx=10)

    tk.Checkbutton(
        step3,
        text="Show Debug Logs",
        variable=debug_var,
        bg=BG_PANEL,
        fg=FG_TEXT,
        font=FONT_CHECK,
    ).pack(side="left", padx=10)

    # -------------------------------------------------------------------
    # LOG & ACTION
    # -------------------------------------------------------------------
    process_btn = tk.Button(
        main_frame,
        text="PROCESS FILES",
        font=("Ubuntu", 12, "bold"),
        bg=BUTTON_BG,
        fg=BUTTON_FG,
        height=2,
        width=20,
    )
    process_btn.grid(row=3, column=0, pady=10)

    log_label = tk.Label(
        main_frame, text="Processing Log:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL
    )
    log_label.grid(row=4, column=0, sticky="w")

    log_box = scrolledtext.ScrolledText(
        main_frame, height=10, bg=LOG_BG, fg=LOG_FG, font=FONT_LOG
    )
    log_box.grid(row=5, column=0, sticky="nsew")
    main_frame.rowconfigure(5, weight=1)  # Log expands

    def log(msg: str):
        def _insert():
            log_box.insert(tk.END, msg + "\n")
            log_box.see(tk.END)

        root.after(0, _insert)

    # -------------------------------------------------------------------
    # LOGIC
    # -------------------------------------------------------------------
    def run_processing_thread(pdfs, outdir, mode, debug, use_ocr, run_qc):
        try:
            log(f"--- Starting {mode.upper()} mode on {len(pdfs)} file(s) ---")
            qc_results = []

            for p in pdfs:
                try:
                    ...
                except Exception as e:
                    log(f"[ERROR] {p.name}: {e}")

            if mode == "export" and run_qc and qc_results:
                ...
            log("--- Completed ---")


        except Exception as e:
            log(f"Critical System Error: {e}")
        finally:
            root.after(
                0, lambda: process_btn.config(state=tk.NORMAL, text="PROCESS FILES")
            )

    def start_process():
        outdir = Path(output_entry.get().strip() or ".")
        file_path = file_entry.get().strip()
        folder_path = folder_entry.get().strip()

        pdfs = []
        if file_path:
            pdfs = [Path(file_path)]
        elif folder_path:
            pdfs = sorted(Path(folder_path).glob("*.pdf"))

        if not pdfs:
            messagebox.showerror("Error", "Please select a file or folder first.")
            return

        outdir.mkdir(parents=True, exist_ok=True)
        process_btn.config(state=tk.DISABLED, text="Running...")

        mode = mode_var.get()
        t = threading.Thread(
            target=run_processing_thread,
            args=(
                pdfs,
                outdir,
                mode,
                debug_var.get(),
                ocr_var.get(),
                qc_var.get(),
            ),
            daemon=True,
        )
        t.start()

    process_btn.config(command=start_process)

    # -------------------------------------------------------------------
    # STATUS BAR
    # -------------------------------------------------------------------
   
    status = tk.Frame(root, bg=BG_STATUS)
    status.grid(row=1, column=0, sticky="ew")

    # 3 columns: left & right stretch, middle stays centered
    status.columnconfigure(0, weight=1)
    status.columnconfigure(1, weight=0)
    status.columnconfigure(2, weight=1)

    tess_lbl = tk.Label(
        status,
        text="TESSERACT OCR",
        bg=BG_STATUS,
        fg=FG_MUTED,
        font=FONT_STATUS_SIDE,   # smaller
    )
    tess_lbl.grid(row=0, column=0, sticky="w", padx=10)

    ocr_status_lbl = tk.Label(
        status,
        text="CHECKING OCR...",
        bg=BG_STATUS,
        fg=FG_MUTED,
        font=FONT_STATUS_MAIN,   # larger, centered
    )
    ocr_status_lbl.grid(row=0, column=1)  # center column

    popp_lbl = tk.Label(
        status,
        text="POPPLER UTILS",
        bg=BG_STATUS,
        fg=FG_MUTED,
        font=FONT_STATUS_SIDE,   # smaller
    )
    popp_lbl.grid(row=0, column=2, sticky="e", padx=10)



if __name__ == "__main__":
    run_gui()
