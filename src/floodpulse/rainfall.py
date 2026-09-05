"""Build temporal rainfall features from real district-day observations."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


class RainfallInputError(ValueError):
    """Raised when rainfall input violates the feature contract."""


@dataclass(frozen=True, order=True)
class RainfallObservation:
    district_id: str
    observation_date: date
    rainfall_mm: float


def _parse_date(value: str, row_number: int) -> date:
    try:
        return date.fromisoformat(value.strip())
    except (TypeError, ValueError) as exc:
        raise RainfallInputError(
            f"Invalid observation_date at CSV row {row_number}: {value!r}"
        ) from exc


def read_observations(path: Path) -> list[RainfallObservation]:
    """Read district-day rainfall, rejecting invalid and duplicate rows."""
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"district_id", "observation_date", "rainfall_mm"}
            missing = sorted(required - set(reader.fieldnames or ()))
            if missing:
                raise RainfallInputError(
                    f"Rainfall CSV {path} is missing columns: {', '.join(missing)}"
                )

            observations: list[RainfallObservation] = []
            seen: set[tuple[str, date]] = set()
            for row_number, row in enumerate(reader, start=2):
                district_id = (row.get("district_id") or "").strip()
                if not district_id:
                    raise RainfallInputError(
                        f"Missing district_id at CSV row {row_number}"
                    )
                observation_date = _parse_date(
                    row.get("observation_date", ""), row_number
                )
                try:
                    rainfall_mm = float(row.get("rainfall_mm", ""))
                except (TypeError, ValueError) as exc:
                    raise RainfallInputError(
                        f"Invalid rainfall_mm at CSV row {row_number}"
                    ) from exc
                if rainfall_mm < 0:
                    raise RainfallInputError(
                        f"Negative rainfall_mm at CSV row {row_number}"
                    )
                key = (district_id, observation_date)
                if key in seen:
                    raise RainfallInputError(
                        f"Duplicate rainfall observation: {district_id}, "
                        f"{observation_date.isoformat()}"
                    )
                seen.add(key)
                observations.append(
                    RainfallObservation(district_id, observation_date, rainfall_mm)
                )
    except OSError as exc:
        raise RainfallInputError(f"Unable to read rainfall CSV {path}: {exc}") from exc

    if not observations:
        raise RainfallInputError(f"Rainfall CSV {path} contains no observations")
    return observations


def build_features(
    observations: list[RainfallObservation],
) -> list[dict[str, object]]:
    """Compute rolling rainfall features without silently filling missing days."""
    by_district: dict[str, dict[date, float]] = {}
    for observation in observations:
        by_district.setdefault(observation.district_id, {})[
            observation.observation_date
        ] = observation.rainfall_mm

    features: list[dict[str, object]] = []
    for district_id, values in sorted(by_district.items()):
        dates = sorted(values)
        for index, observation_date in enumerate(dates):
            required_dates = [
                observation_date - timedelta(days=offset) for offset in range(7)
            ]
            missing = [day for day in required_dates if day not in values]
            if missing:
                if index < 6 and missing == required_dates[index + 1 :]:
                    continue
                raise RainfallInputError(
                    f"Missing rainfall dates for {district_id} before "
                    f"{observation_date.isoformat()}: "
                    + ", ".join(day.isoformat() for day in missing)
                )
            features.append(
                {
                    "district_id": district_id,
                    "event_date": observation_date.isoformat(),
                    "rain_1d": values[observation_date],
                    "rain_3d": sum(values[day] for day in required_dates[:3]),
                    "rain_7d": sum(values[day] for day in required_dates),
                    "rain_lag_1d": values[observation_date - timedelta(days=1)],
                }
            )
    if not features:
        raise RainfallInputError(
            "No rainfall feature rows have a complete seven-day history"
        )
    return features


def main() -> int:
    parser = argparse.ArgumentParser(description="Build rainfall temporal features.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    features = build_features(read_observations(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "district_id",
                "event_date",
                "rain_1d",
                "rain_3d",
                "rain_7d",
                "rain_lag_1d",
            ],
        )
        writer.writeheader()
        writer.writerows(features)
    print(f"Wrote {len(features)} rainfall feature rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
