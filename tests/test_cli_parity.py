
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ParsingTool.parsing import cli
from ParsingTool.parsing.export_orders import pipeline as export_pipeline
from ParsingTool.parsing.domestic_zapi import pipeline as domestic_pipeline

class TestCLIParity(unittest.TestCase):

    @patch('ParsingTool.parsing.cli.run_domestic')
    def test_cli_domestic_flags(self, mock_run_domestic):
        """Test that domestic CLI command passes debug and ocr flags."""
        test_args = [
            'parsingtool', 'domestic', 'input.pdf', 
            '--out-batches', 'batches.csv', 
            '--out-sscc', 'sscc.csv', 
            '--ocr', '--debug'
        ]
        with patch.object(sys, 'argv', test_args):
            cli.main()
            
        mock_run_domestic.assert_called_with(
            input_pdf='input.pdf',
            out_batches='batches.csv',
            out_sscc='sscc.csv',
            use_ocr=True,
            debug=True
        )

    @patch('ParsingTool.parsing.cli.run_export')
    def test_cli_export_flags(self, mock_run_export):
        """Test that export CLI command passes debug, ocr, and qc flags."""
        test_args = [
            'parsingtool', 'export', 'input.pdf', 
            '--out', 'output.csv', 
            '--ocr', '--debug', '--qc'
        ]
        with patch.object(sys, 'argv', test_args):
            cli.main()
            
        mock_run_export.assert_called_with(
            input_pdf='input.pdf',
            out='output.csv',
            use_ocr=True,
            debug=True,
            generate_qc=True
        )

    @patch('ParsingTool.parsing.export_orders.pipeline.parse_export_pdf')
    @patch('ParsingTool.parsing.export_orders.pipeline.pd.DataFrame.to_csv')
    @patch('ParsingTool.parsing.qc.validate')
    @patch('ParsingTool.parsing.qc.write_report')
    def test_export_pipeline_qc_generation(self, mock_write_report, mock_validate, mock_to_csv, mock_parse):
        """Test that export pipeline generates QC report when requested."""
        mock_df = MagicMock()
        mock_parse.return_value = mock_df
        
        export_pipeline.run(
            input_pdf='input.pdf',
            out='output.csv',
            generate_qc=True
        )
        
        mock_validate.assert_called()
        mock_write_report.assert_called()
        # Check that report path is correct (sibling to output.csv)
        expected_report_path = Path('qc_report.md')
        mock_write_report.assert_called_with(
            [mock_validate.return_value], 
            expected_report_path
        )

if __name__ == '__main__':
    unittest.main()
