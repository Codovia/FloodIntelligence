"""Construct district-day labels from verified IFI events and real candidates."""

from __future__ import annotations

import csv
import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


class LabelInputError(ValueError):
    """Raised when an input violates the label construction contract."""


@dataclass(frozen=True, order=True)
class DistrictDay:
    district_id: str
    event_date: date


def _parse_date(value: str, *, field: str, row_number: int) -> date:
    try:
        return date.fromisoformat(value.strip())
    except (TypeError, ValueError) as exc:
        raise LabelInputError(
            f"Invalid {field} at CSV row {row_number}: {value!r}; "
            "expected ISO YYYY-MM-DD"
        ) from exc


def read_ifi_events(path: Path) -> set[DistrictDay]:
    """Read IFI positive district-days and reject malformed source records."""
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"district_id", "event_date"}
            if not required.issubset(reader.fieldnames or set()):
                missing = sorted(required - set(reader.fieldnames or ()))
                raise LabelInputError(
                    f"IFI event CSV {path} is missing columns: {', '.join(missing)}"
                )

            events: set[DistrictDay] = set()
            for row_number, row in enumerate(reader, start=2):
                district_id = (row.get("district_id") or "").strip()
                if not district_id:
                    raise LabelInputError(
                        f"Missing district_id at CSV row {row_number}"
                    )
                events.add(
                    DistrictDay(
                        district_id=district_id,
                        event_date=_parse_date(
                            row.get("event_date", ""),
                            field="event_date",
                            row_number=row_number,
                        ),
                    )
                )
    except OSError as exc:
        raise LabelInputError(f"Unable to read IFI event CSV {path}: {exc}") from exc

    if not events:
        raise LabelInputError(f"IFI event CSV {path} contains no records")
    return events


def build_labels(candidates: Iterable[DistrictDay], events: set[DistrictDay]) -> list[dict[str, object]]:
    """Label only supplied candidate days; never invent a candidate calendar."""
    candidate_list = list(candidates)
    if not candidate_list:
        raise LabelInputError("Cannot build labels from an empty candidate set")

    seen: set[DistrictDay] = set()
    labels: list[dict[str, object]] = []
    for candidate in candidate_list:
        if candidate in seen:
            raise LabelInputError(f"Duplicate candidate district-day: {candidate}")
        seen.add(candidate)
        labels.append(
            {
                "district_id": candidate.district_id,
                "event_date": candidate.event_date.isoformat(),
                "label": int(candidate in events),
            }
        )
    return labels


def _read_candidates(path: Path) -> list[DistrictDay]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"district_id", "event_date"}
            if not required.issubset(reader.fieldnames or set()):
                missing = sorted(required - set(reader.fieldnames or ()))
                raise LabelInputError(
                    f"Candidate CSV {path} is missing columns: {', '.join(missing)}"
                )
            candidates = []
            for row_number, row in enumerate(reader, start=2):
                district_id = (row.get("district_id") or "").strip()
                if not district_id:
                    raise LabelInputError(
                        f"Missing district_id at CSV row {row_number}"
                    )
                candidates.append(
                    DistrictDay(
                        district_id,
                        _parse_date(
                            row.get("event_date", ""),
                            field="event_date",
                            row_number=row_number,
                        ),
                    )
                )
            return candidates
    except OSError as exc:
        raise LabelInputError(f"Unable to read candidate CSV {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build IFI labels for real candidate district-days."
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    labels = build_labels(_read_candidates(args.candidates), read_ifi_events(args.events))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["district_id", "event_date", "label"]
        )
        writer.writeheader()
        writer.writerows(labels)
    print(f"Wrote {len(labels)} labeled district-days to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
