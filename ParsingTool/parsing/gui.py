import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import pandas as pd

from .pdf_parser import parse_pdf
from .qc import validate, write_report
from .merge_with_overrides import apply_overrides

def run_gui():
    root = tk.Tk()
    root.title("ParsingTool")

    file_entry = tk.Entry(root, width=60)
    folder_entry = tk.Entry(root, width=60)
    output_entry = tk.Entry(root, width=60)

    def browse_file():
        p = filedialog.askopenfilename(filetypes=[("PDF files","*.pdf")])
        if p: file_entry.delete(0, tk.END); file_entry.insert(0, p)

    def browse_folder():
        p = filedialog.askdirectory()
        if p: folder_entry.delete(0, tk.END); folder_entry.insert(0, p)

    def browse_output():
        p = filedialog.askdirectory()
        if p: output_entry.delete(0, tk.END); output_entry.insert(0, p)

    debug_var = tk.BooleanVar(value=False)
    ocr_var = tk.BooleanVar(value=False)
    qc_var = tk.BooleanVar(value=True)

    def log(msg):
        log_box.insert(tk.END, msg + "\n"); log_box.see(tk.END)

    def process():
        outdir = Path(output_entry.get().strip() or ".")
        file_path = file_entry.get().strip()
        folder_path = folder_entry.get().strip()

        pdfs = []
        if file_path:
            pdfs = [Path(file_path)]
        elif folder_path:
            pdfs = sorted(Path(folder_path).glob("*.pdf"))
        else:
            messagebox.showerror("Error", "Choose a file or a folder")
            return

        outdir.mkdir(parents=True, exist_ok=True)
        qc_results = []
        for p in pdfs:
            try:
                df = parse_pdf(p, debug=debug_var.get(), use_ocr=ocr_var.get())
                base = (df.iloc[0].get("Delivery Number") or "").strip() or p.stem
                out = outdir / f"parsed_{base}.csv"
                df.to_csv(out, index=False, encoding="utf-8-sig")
                log(f"[saved] {out}")
                qc_results.append(validate(df, p.name))
            except Exception as e:
                log(f"[error] {p}: {e}")

        if qc_var.get():
            report_path = outdir / "qc_report.md"
            write_report(qc_results, report_path)
            log(f"[qc] wrote {report_path}")

    # Layout
    tk.Label(root, text="Single PDF:").grid(row=0, column=0, sticky="e")
    file_entry.grid(row=0, column=1); tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

    tk.Label(root, text="Folder of PDFs:").grid(row=1, column=0, sticky="e")
    folder_entry.grid(row=1, column=1); tk.Button(root, text="Browse", command=browse_folder).grid(row=1, column=2)

    tk.Label(root, text="Output Folder:").grid(row=2, column=0, sticky="e")
    output_entry.grid(row=2, column=1); tk.Button(root, text="Browse", command=browse_output).grid(row=2, column=2)

    tk.Checkbutton(root, text="Debug logs", variable=debug_var).grid(row=3, column=1, sticky="w")
    tk.Checkbutton(root, text="Use OCR fallback", variable=ocr_var).grid(row=3, column=2, sticky="w")
    tk.Checkbutton(root, text="Write QC report", variable=qc_var).grid(row=4, column=1, sticky="w")

    tk.Button(root, text="Process", command=process).grid(row=5, column=1, pady=10)

    log_box = scrolledtext.ScrolledText(root, height=18, width=98)
    log_box.grid(row=6, column=0, columnspan=3, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
