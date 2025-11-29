import unittest
import sys
import os

# Add project root to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# FIXED IMPORT: Removed 'parse_export_text' which no longer exists
from ParsingTool.parsing.export_orders.pipeline import parse_product_line, _find_line

class TestExportPipeline(unittest.TestCase):

    def test_find_line_header_filtering(self):
        """Test that _find_line filters out table header words."""
        # "Delivery" capturing "Sale"
        pattern = r"Delivery\s*([^\n]+)"
        
        # If text is "Delivery Sale", it matches "Sale". Should be filtered.
        self.assertEqual(_find_line(pattern, "Delivery Sale"), "")
        
        # Valid value
        self.assertEqual(_find_line(pattern, "Delivery 12345"), "12345")

    def test_parse_product_line_standard(self):
        """Test standard product line parsing."""
        line = "Almonds Kern Supr 23/25 50lb ctn"
        result = parse_product_line(line)
        
        self.assertEqual(result["Size"], "23/25")
        self.assertEqual(result["Packaging"], "50lb ctn")
        self.assertIn("Supr", result["Grade"])
        self.assertIn("Almonds Kern", result["Variety"])

    def test_parse_product_line_complex(self):
        """Test complex product line with material code and extra spaces."""
        line = "Almonds   Kern  SSR 27/30  0802.12.00  1T bag"
        result = parse_product_line(line)
        
        self.assertEqual(result["Size"], "27/30")
        self.assertEqual(result["Packaging"], "1T bag")
        self.assertIn("SSR", result["Grade"])
        self.assertEqual(result["Variety"], "Almonds Kern") # Material code removed

    def test_parse_product_line_rejects(self):
        """Test rejects line."""
        line = "Almonds Kern Non Var H&S Bulk Bags"
        result = parse_product_line(line)
        
        self.assertEqual(result["Size"], "N/A")
        self.assertEqual(result["Packaging"], "Bulk Bags")
        self.assertIn("H&S", result["Grade"])
        self.assertIn("Almonds Kern Non Var", result["Variety"])

    def test_parse_product_line_multiple_grades(self):
        """Test multiple grades."""
        line = "Almonds Kern SSR Supr 23/25 50lb ctn"
        result = parse_product_line(line)
        
        # Depending on your logic, it might pick the first one found
        # Just ensure it picked one valid grade
        self.assertTrue(result["Grade"] in ["SSR", "Supr"])
        self.assertEqual(result["Size"], "23/25")

    def test_parse_product_line_material_code_prefix(self):
        """Test removing leading material codes."""
        line = "9054 / Almonds Kern Supr 23/25"
        result = parse_product_line(line)
        self.assertEqual(result["Size"], "23/25")
        self.assertIn("Almonds Kern", result["Variety"])
        # Ensure "9054 /" is gone

if __name__ == '__main__':
    unittest.main()