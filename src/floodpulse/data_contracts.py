"""Validation for the real datasets required by the FloodPulse baseline.

This module intentionally validates presence and basic structure only. It never
creates replacement observations or fills missing values.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RequiredDataset:
    name: str
    path: Path
    description: str


def required_datasets(data_root: Path) -> tuple[RequiredDataset, ...]:
    """Return the core inputs for the district-day baseline."""
    return (
        RequiredDataset(
            "IFI flood events",
            data_root / "raw" / "ifi" / "events.csv",
            "Verified IFI event extraction used to construct labels.",
        ),
        RequiredDataset(
            "IMD rainfall",
            data_root / "raw" / "rainfall_imd" / "daily_gridded.csv",
            "Historical daily rainfall used for temporal features.",
        ),
        RequiredDataset(
            "Karnataka districts",
            data_root / "raw" / "boundaries" / "karnataka_districts.geojson",
            "District polygons and stable administrative identifiers.",
        ),
        RequiredDataset(
            "SRTM terrain",
            data_root / "raw" / "dem" / "srtm.tif",
            "Open DEM used to derive elevation and slope.",
        ),
    )


def validate_required_datasets(data_root: Path) -> list[str]:
    """Return actionable errors for missing or empty required inputs."""
    errors: list[str] = []
    for dataset in required_datasets(data_root):
        if not dataset.path.exists():
            errors.append(
                f"Missing {dataset.name}: {dataset.path}. "
                f"{dataset.description}"
            )
        elif dataset.path.is_file() and dataset.path.stat().st_size == 0:
            errors.append(f"Empty {dataset.name}: {dataset.path}")

    events = data_root / "raw" / "ifi" / "events.csv"
    if events.exists() and events.stat().st_size > 0:
        try:
            with events.open(newline="", encoding="utf-8") as handle:
                columns = set(next(csv.reader(handle), []))
        except (OSError, UnicodeError, csv.Error) as exc:
            errors.append(f"Unable to read IFI event CSV {events}: {exc}")
        else:
            required_columns = {"district_id", "event_date"}
            missing = sorted(required_columns - columns)
            if missing:
                errors.append(
                    f"IFI event CSV {events} is missing required columns: "
                    + ", ".join(missing)
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether FloodPulse core input datasets are present."
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data"),
        help="Root directory containing raw/interim/processed data.",
    )
    args = parser.parse_args()

    errors = validate_required_datasets(args.data_root)
    if errors:
        print("Data readiness check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Data readiness check passed for all required datasets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

