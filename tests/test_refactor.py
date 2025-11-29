
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ParsingTool.parsing.domestic_zapi import pipeline as domestic_pipeline

class TestRefactor(unittest.TestCase):

    @patch('ParsingTool.parsing.domestic_zapi.pipeline.extract_text')
    @patch('ParsingTool.parsing.domestic_zapi.pipeline.write_csv')
    def test_domestic_run_accepts_use_ocr(self, mock_write_csv, mock_extract_text):
        """Verify that domestic_pipeline.run accepts use_ocr and passes it to extract_text."""
        mock_extract_text.return_value = "Sample text"
        
        domestic_pipeline.run(
            input_pdf="dummy.pdf",
            out_batches="batches.csv",
            out_sscc="sscc.csv",
            use_ocr=True
        )
        
        # Check if extract_text was called with use_ocr=True
        mock_extract_text.assert_called_with("dummy.pdf", use_ocr=True)

if __name__ == '__main__':
    unittest.main()
