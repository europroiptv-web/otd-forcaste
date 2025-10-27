"""Build a modeling-ready dataset from raw order records."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List

RAW_DATA_PATH = Path("data/raw/orders.csv")
DEFAULT_OUTPUT_PATH = Path("data/orders_modeling.csv")

DATE_FIELDS = [
    "request_date",
    "promised_date",
    "actual_fulfillment_date",
]


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def hours_between(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / 3600.0


def build_dataset(raw_path: Path, output_path: Path) -> Path:
    with raw_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        processed: List[Dict[str, object]] = []
        for row in reader:
            request_date = parse_date(row["request_date"])
            promised_date = parse_date(row["promised_date"])
            actual_date = parse_date(row["actual_fulfillment_date"])

            record: Dict[str, object] = {
                "order_id": int(row["order_id"]),
                "team": row["team"],
                "region": row["region"],
                "requested_hours": float(row["requested_hours"]),
                "request_to_promised_days": (promised_date - request_date).days,
                "promised_to_actual_hours": hours_between(promised_date, actual_date),
                "request_to_actual_hours": hours_between(request_date, actual_date),
                "request_weekday": request_date.strftime("%A"),
                "request_month": request_date.month,
                "is_weekend_request": request_date.weekday() >= 5,
            }
            processed.append(record)

    processed.sort(key=lambda item: item["order_id"])

    fieldnames = [
        "order_id",
        "team",
        "region",
        "requested_hours",
        "request_to_promised_days",
        "promised_to_actual_hours",
        "request_to_actual_hours",
        "request_weekday",
        "request_month",
        "is_weekend_request",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for record in processed:
            writer.writerow(record)

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-path",
        type=Path,
        default=RAW_DATA_PATH,
        help=f"Path to the raw orders CSV (default: {RAW_DATA_PATH}).",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Path for the modeling CSV (default: {DEFAULT_OUTPUT_PATH}).",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    output_path = build_dataset(args.raw_path, args.output_path)
    print(f"Wrote modeling dataset to {output_path}")


if __name__ == "__main__":
    main()
