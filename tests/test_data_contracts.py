import tempfile
import unittest
from pathlib import Path

from floodpulse.data_contracts import validate_required_datasets


class DataContractTests(unittest.TestCase):
    def test_missing_inputs_are_reported_without_fabrication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_required_datasets(Path(directory))

        self.assertEqual(len(errors), 4)
        self.assertTrue(all("Missing " in error for error in errors))


if __name__ == "__main__":
    unittest.main()

