from pathlib import Path
from typing import Callable, Iterable, Optional

# --- PIPELINE IMPORTS ---
# Note: These imports assume the current structure where pipelines are in ParsingTool.parsing
# In Phase 4, these will be moved to ParsingTool.core.pipelines
from ParsingTool.parsing.export_orders.pipeline import parse_export_pdf, run_batch as run_export_batch
from ParsingTool.parsing.domestic_zapi import pipeline as domestic_pipeline
from ParsingTool.parsing.packing_list.pipeline import run as run_packing_pipeline, run_batch as run_packing_batch
from ParsingTool.parsing.qc import validate, write_report
from ParsingTool.parsing.shared.pdf_utils import NoTextError

class ProcessingController:
    def __init__(self, log_callback: Callable[[str], None]):
        self.log = log_callback

    def run(
        self,
        pdfs: Iterable[Path],
        outdir: Path,
        mode: str,
        debug: bool,
        use_ocr: bool,
        run_qc: bool,
        combine: bool,
        folder_path: Optional[str]
    ) -> None:
        """Process a list of PDFs and write their CSV outputs.

        Args:
            pdfs: Iterable of Path objects for input PDFs.
            outdir: Path to output directory.
            mode: One of "export", "domestic", "packinglist".
            debug: Whether to enable debug logging.
            use_ocr: Whether to enable OCR fallback.
            run_qc: Whether to run QC (export mode only).
            combine: whether to combine outputs.
            folder_path: original folder path string.
        """
        try:
            self.log(f"--- Starting {mode.upper()} mode on {len(pdfs)} file(s) ---")
            qc_results = []

            # If user asked to combine and gave us a folder, use the batch pipelines
            folder = Path(folder_path) if folder_path else None
            if combine and folder is not None and folder.is_dir():
                self.log("Combine mode enabled: creating combined CSV(s) from folder.")

                if mode == "export":
                    run_export_batch(folder, outdir, use_ocr=use_ocr, debug=debug)
                    combined = outdir / "export_combined.csv"
                    self.log(f"[COMBINED] Wrote {combined.name}")

                elif mode == "domestic":
                    domestic_pipeline.run_batch(
                        folder, outdir, use_ocr=use_ocr, debug=debug
                    )
                    self.log(
                        "[COMBINED] Wrote domestic_batches_combined.csv "
                        "and domestic_sscc_combined.csv"
                    )

                elif mode == "packinglist":
                    run_packing_batch(
                        folder,
                        outdir,
                        use_ocr=use_ocr,
                        debug=debug,
                    )
                    combined = outdir / "pi_combined.csv"
                    self.log(f"[COMBINED] Wrote {combined.name}")

                else:
                    self.log(f"[WARN] Combine is not supported for mode: {mode}")

                self.log("--- Completed ---")
                return

            # Normal per-file processing
            for p in pdfs:
                try:
                    if mode == "export":
                        name_upper = p.name.upper()

                        # Auto-route PI / ZAPI files to the PI pipeline
                        if name_upper.endswith("_PI.PDF") or name_upper.endswith("_ZAPI.PDF"):
                            out_csv = outdir / f"{p.stem}_packing.csv"
                            run_packing_pipeline(
                            input_pdf=str(p),
                            out=str(out_csv),
                            use_ocr=use_ocr,
                            debug=debug,
                        )
                            self.log(f"[OK][PI] {p.name} -> {out_csv.name}")

                        else:
                            # Normal export pipeline
                            df = parse_export_pdf(
                                str(p), use_ocr=use_ocr, debug=debug
                            )
                            out_csv = outdir / f"{p.stem}.csv"
                            df.to_csv(out_csv, index=False, encoding="utf-8-sig")
                            self.log(
                                f"[OK] {p.name} -> {out_csv.name} "
                                f"({len(df)} rows)"
                            )

                            if run_qc:
                                qc_results.append(validate(df, p.name))

                    elif mode == "domestic":
                        batches_csv = outdir / f"{p.stem}_batches.csv"
                        sscc_csv = outdir / f"{p.stem}_sscc.csv"

                        domestic_pipeline.run(
                            input_pdf=str(p),
                            out_batches=str(batches_csv),
                            out_sscc=str(sscc_csv),
                            use_ocr=use_ocr,
                            debug=debug,
                        )
                        self.log(
                            f"[OK] {p.name} -> "
                            f"{batches_csv.name}, {sscc_csv.name}"
                        )

                    elif mode == "packinglist":
                        out_csv = outdir / f"{p.stem}_packing.csv"
                        run_packing_pipeline(
                            input_pdf=str(p),
                            out=str(out_csv),
                            use_ocr=use_ocr,
                            debug=debug,
                        )
                        self.log(f"[OK] {p.name} -> {out_csv.name}")

                    else:
                        self.log(f"[WARN] Unknown mode: {mode}")

                except NoTextError as e:
                    self.log(f"[WARN] {p.name}: no extractable text ({e})")
                except Exception as e:
                    self.log(f"[ERROR] {p.name}: {e}")

            # QC report for export
            if mode == "export" and run_qc and qc_results:
                report_path = outdir / "qc_report.md"
                write_report(qc_results, report_path)
                self.log(f"[QC] Wrote report: {report_path.name}")

            self.log("--- Completed ---")

        except Exception as e:
            self.log(f"[FATAL] {e}")
