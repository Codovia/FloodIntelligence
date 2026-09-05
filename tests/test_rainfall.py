import unittest
from datetime import date, timedelta

from floodpulse.rainfall import (
    RainfallInputError,
    RainfallObservation,
    build_features,
)


class RainfallFeatureTests(unittest.TestCase):
    def test_rolling_features_use_prior_observations(self) -> None:
        start = date(2020, 1, 1)
        observations = [
            RainfallObservation("KA01", start + timedelta(days=day), float(day + 1))
            for day in range(7)
        ]

        rows = build_features(observations)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[-1]["rain_1d"], 7.0)
        self.assertEqual(rows[-1]["rain_3d"], 18.0)
        self.assertEqual(rows[-1]["rain_7d"], 28.0)
        self.assertEqual(rows[-1]["rain_lag_1d"], 6.0)

    def test_missing_history_fails_instead_of_filling(self) -> None:
        observations = [
            RainfallObservation("KA01", date(2020, 1, 2), 1.0),
        ]

        with self.assertRaises(RainfallInputError):
            build_features(observations)


if __name__ == "__main__":
    unittest.main()
