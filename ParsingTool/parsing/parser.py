# Compatibility shim so older imports like `from parser import parse_pdf` keep working
# Prefer: from ParsingTool.parsing import parse_pdf

from .pdf_parser import parse_pdf  # noqa: F401  # imported but unused on purpose
