import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ImportTests(unittest.TestCase):
    def test_main_imports_without_circular_error(self):
        import main
        self.assertTrue(main.DEMO_MODE in (True, False))


if __name__ == "__main__":
    unittest.main()
