import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import shutil
import threading
import csv  # NEW

# --- CONTROLLER IMPORT ---
from ParsingTool.core.controller import ProcessingController


# ---------------------------------------------------------------------------
# THEME SETTINGS
# ---------------------------------------------------------------------------
# --- NEW MODULE IMPORTS ---
from ParsingTool.interfaces.gui import theme
from ParsingTool.common.system import is_installed





def run_gui() -> None:
    root = tk.Tk()
    root.title("ParsingTool v2.0")
    root.configure(bg=theme.BG_MAIN)
    root.update_idletasks()  # let Tkinter calculate needed size
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())


    # Layout: Main content expands, status bar fixed
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Main container frame to hold the "steps"
    main_frame = tk.Frame(root, bg=theme.BG_MAIN, padx=10, pady=10)
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)

    # -------------------------------------------------------------------
    # STEP 1: INPUTS (LabelFrame)
    # -------------------------------------------------------------------
    step1 = tk.LabelFrame(
        main_frame,
        text=" 1. Select Files ",
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_TITLE,
    )
    step1.grid(row=0, column=0, sticky="ew", pady=(0, 10), ipady=5)
    step1.columnconfigure(1, weight=1)

    # File
    tk.Label(
        step1, text="Single PDF:", bg=theme.BG_PANEL, fg=theme.FG_TEXT, font=theme.FONT_LABEL
    ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    file_entry = tk.Entry(
        step1,
        bg=theme.ENTRY_BG,
        fg=theme.ENTRY_FG,
        insertbackground=theme.ENTRY_FG,
        font=theme.FONT_ENTRY,
    )
    file_entry.grid(row=0, column=1, sticky="ew", padx=5)

    # Folder
    tk.Label(
        step1, text="OR Folder:", bg=theme.BG_PANEL, fg=theme.FG_TEXT, font=theme.FONT_LABEL
    ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    folder_entry = tk.Entry(
        step1,
        bg=theme.ENTRY_BG,
        fg=theme.ENTRY_FG,
        insertbackground=theme.ENTRY_FG,
        font=theme.FONT_ENTRY,
    )
    folder_entry.grid(row=1, column=1, sticky="ew", padx=5)

    # Output
    tk.Label(
        step1, text="Output To:", bg=theme.BG_PANEL, fg=theme.FG_TEXT, font=theme.FONT_LABEL
    ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    output_entry = tk.Entry(
        step1,
        bg=theme.ENTRY_BG,
        fg=theme.ENTRY_FG,
        insertbackground=theme.ENTRY_FG,
        font=theme.FONT_ENTRY,
    )
    output_entry.grid(row=2, column=1, sticky="ew", padx=5)

    # Buttons
    def browse_file() -> None:
        p = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if p:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, p)

    def browse_folder() -> None:
        p = filedialog.askdirectory()
        if p:
            folder_entry.delete(0, tk.END)
            folder_entry.insert(0, p)

    def browse_output() -> None:
        p = filedialog.askdirectory()
        if p:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, p)

    tk.Button(step1, text="Browse", command=browse_file, bg=theme.BUTTON_BG, fg=theme.BUTTON_FG).grid(
        row=0, column=2, padx=5
    )
    tk.Button(step1, text="Browse", command=browse_folder, bg=theme.BUTTON_BG, fg=theme.BUTTON_FG).grid(
        row=1, column=2, padx=5
    )
    tk.Button(step1, text="Browse", command=browse_output, bg=theme.BUTTON_BG, fg=theme.BUTTON_FG).grid(
        row=2, column=2, padx=5
    )

    # -------------------------------------------------------------------
    # STEP 2: MODE (LabelFrame)
    # -------------------------------------------------------------------
    step2 = tk.LabelFrame(
        main_frame,
        text=" 2. Document Type ",
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_TITLE,
    )
    step2.grid(row=1, column=0, sticky="ew", pady=(0, 10), ipady=5)

    mode_var = tk.StringVar(value="export")

    tk.Radiobutton(
        step2,
        text="Export Orders",
        variable=mode_var,
        value="export",
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_CHECK,
    ).pack(side="left", padx=20)

    tk.Radiobutton(
        step2,
        text="Domestic ZAPI",
        variable=mode_var,
        value="domestic",
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_CHECK,
    ).pack(side="left", padx=20)

    tk.Radiobutton(
        step2,
        text="Packing List (PI)",
        variable=mode_var,
        value="packinglist",
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_CHECK,
    ).pack(side="left", padx=20)

    # -------------------------------------------------------------------
    # STEP 3: OPTIONS (LabelFrame - "Advanced")
    # -------------------------------------------------------------------
    step3 = tk.LabelFrame(
        main_frame,
        text=" 3. Advanced Options ",
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_TITLE,
    )
    step3.grid(row=2, column=0, sticky="ew", pady=(0, 10), ipady=5)

    debug_var = tk.BooleanVar(value=False)
    ocr_var = tk.BooleanVar(value=False)
    qc_var = tk.BooleanVar(value=True)
    combine_var = tk.BooleanVar(value=False)

    ocr_check = tk.Checkbutton(
        step3,
        text="Enable OCR Fallback (Slow)",
        variable=ocr_var,
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_CHECK,
    )
    ocr_check.pack(side="left", padx=10)

    tk.Checkbutton(
        step3,
        text="Generate QC Report (Export Only)",
        variable=qc_var,
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_CHECK,
    ).pack(side="left", padx=10)

    tk.Checkbutton(
        step3,
        text="Show Debug Logs",
        variable=debug_var,
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_CHECK,
    ).pack(side="left", padx=10)

    tk.Checkbutton(
        step3,
        text="Combine folder results into one CSV",
        variable=combine_var,
        bg=theme.BG_PANEL,
        fg=theme.FG_TEXT,
        font=theme.FONT_CHECK,
    ).pack(side="left", padx=10)

    # -------------------------------------------------------------------
    # LOG & ACTION
    # -------------------------------------------------------------------
    process_btn = tk.Button(
        main_frame,
        text="PROCESS FILES",
        font=("Ubuntu", 12, "bold"),
        bg=theme.BUTTON_BG,
        fg=theme.BUTTON_FG,
        height=2,
        width=20,
    )
    process_btn.grid(row=3, column=0, pady=10)

    log_label = tk.Label(
        main_frame, text="Processing Log:", bg=theme.BG_MAIN, fg=theme.FG_TEXT, font=theme.FONT_LABEL
    )
    log_label.grid(row=4, column=0, sticky="w")

    log_box = scrolledtext.ScrolledText(
        main_frame, height=10, bg=theme.LOG_BG, fg=theme.LOG_FG, font=theme.FONT_LOG
    )
    log_box.grid(row=5, column=0, sticky="nsew")
    main_frame.rowconfigure(5, weight=1)  # Log expands

    def log(msg: str) -> None:
        def _insert() -> None:
            log_box.insert(tk.END, msg + "\n")
            log_box.see(tk.END)

        root.after(0, _insert)

    # -------------------------------------------------------------------
    # LOGIC
    # -------------------------------------------------------------------
    def run_processing_thread(
        pdfs, outdir, mode, debug, use_ocr, run_qc, combine, folder_path
    ) -> None:
        controller = ProcessingController(log)
        controller.run(
            pdfs, outdir, mode, debug, use_ocr, run_qc, combine, folder_path
        )
        
        # Re-enable button
        root.after(
            0, lambda: process_btn.config(state=tk.NORMAL, text="PROCESS FILES")
        )

    def start_process() -> None:
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
                combine_var.get(),
                folder_path,
            ),
            daemon=True,
        )
        t.start()

    process_btn.config(command=start_process)

    # -------------------------------------------------------------------
    # STATUS BAR
    # -------------------------------------------------------------------
    status = tk.Frame(root, bg=theme.BG_STATUS)
    status.grid(row=1, column=0, sticky="ew")

    status.columnconfigure(0, weight=1)
    status.columnconfigure(1, weight=0)
    status.columnconfigure(2, weight=1)

    tess_lbl = tk.Label(
        status,
        text="TESSERACT OCR",
        bg=theme.BG_STATUS,
        fg=theme.FG_MUTED,
        font=theme.FONT_STATUS_SIDE,
    )
    tess_lbl.grid(row=0, column=0, sticky="w", padx=10)

    ocr_status_lbl = tk.Label(
        status,
        text="CHECKING OCR...",
        bg=theme.BG_STATUS,
        fg=theme.FG_MUTED,
        font=theme.FONT_STATUS_MAIN,
    )
    ocr_status_lbl.grid(row=0, column=1)

    popp_lbl = tk.Label(
        status,
        text="POPPLER UTILS",
        bg=theme.BG_STATUS,
        fg=theme.FG_MUTED,
        font=theme.FONT_STATUS_SIDE,
    )
    popp_lbl.grid(row=0, column=2, sticky="e", padx=10)

    def update_ocr_status() -> None:
        tess_ok = is_installed("tesseract")
        popp_ok = is_installed("pdftoppm")

        if tess_ok:
            tess_lbl.config(text="✓  TESSERACT", fg=theme.FG_OK, font=theme.FONT_STATUS_SIDE)
        else:
            tess_lbl.config(text="✗  TESSERACT", fg=theme.FG_ERROR, font=theme.FONT_STATUS_SIDE)

        if popp_ok:
            popp_lbl.config(text="POPPLER  ✓", fg=theme.FG_OK, font=theme.FONT_STATUS_SIDE)
        else:
            popp_lbl.config(text="POPPLER  ✗", fg=theme.FG_ERROR, font=theme.FONT_STATUS_SIDE)

        if tess_ok and popp_ok:
            ocr_status_lbl.config(
                text="OCR  READY", fg=theme.FG_OK, font=theme.FONT_STATUS_MAIN
            )
        else:
            ocr_status_lbl.config(
                text="REGEX  ONLY", fg=theme.FG_MUTED, font=theme.FONT_STATUS_MAIN
            )

    root.after(100, update_ocr_status)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
