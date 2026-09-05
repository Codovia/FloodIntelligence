import tempfile
import unittest
from datetime import date
from pathlib import Path

from floodpulse.labels import DistrictDay, LabelInputError, build_labels, read_ifi_events


class LabelTests(unittest.TestCase):
    def test_events_are_read_and_candidates_are_labeled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text(
                "district_id,event_date\nKA01,2020-06-01\n",
                encoding="utf-8",
            )

            events = read_ifi_events(path)
            labels = build_labels(
                [
                    DistrictDay("KA01", date(2020, 6, 1)),
                    DistrictDay("KA01", date(2020, 6, 2)),
                ],
                events,
            )

        self.assertEqual([row["label"] for row in labels], [1, 0])

    def test_duplicate_candidates_fail(self) -> None:
        candidate = DistrictDay("KA01", date(2020, 6, 1))
        with self.assertRaises(LabelInputError):
            build_labels([candidate, candidate], set())

    def test_empty_event_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text("district_id,event_date\n", encoding="utf-8")
            with self.assertRaises(LabelInputError):
                read_ifi_events(path)


if __name__ == "__main__":
    unittest.main()

