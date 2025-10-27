"""Compute fulfillment-time quantiles from the modeling dataset."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Tuple

DEFAULT_MODELING_PATH = Path("data/orders_modeling.csv")
DEFAULT_PREDICTIONS_PATH = Path("data/orders_modeling_quantiles.csv")
DEFAULT_METADATA_PATH = Path("models/otd_quantile_metadata.json")

TARGET_COLUMN = "request_to_actual_hours"
GROUP_COLUMNS = ["team", "region"]


@dataclass
class QuantileSummary:
    team: str
    region: str
    count: int
    p10: float
    p50: float
    p90: float


QuantileMap = Dict[Tuple[str, str], List[float]]


def load_modeling_data(path: Path) -> QuantileMap:
    aggregates: DefaultDict[Tuple[str, str], List[float]] = defaultdict(list)
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = tuple(row[column] for column in GROUP_COLUMNS)
            target_value = float(row[TARGET_COLUMN])
            aggregates[key].append(target_value)
    return aggregates


def compute_quantile(values: Iterable[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot compute quantiles of an empty sequence")
    if len(ordered) == 1:
        return ordered[0]
    position = percentile * (len(ordered) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]
    if lower_index == upper_index:
        return lower_value
    weight = position - lower_index
    return lower_value * (1 - weight) + upper_value * weight


def summarize_quantiles(aggregates: QuantileMap) -> List[QuantileSummary]:
    summaries: List[QuantileSummary] = []
    for (team, region), values in sorted(aggregates.items()):
        summaries.append(
            QuantileSummary(
                team=team,
                region=region,
                count=len(values),
                p10=compute_quantile(values, 0.10),
                p50=compute_quantile(values, 0.50),
                p90=compute_quantile(values, 0.90),
            )
        )
    return summaries


def write_predictions(summaries: List[QuantileSummary], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["team", "region", "count", "P10", "P50", "P90"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            writer.writerow(
                {
                    "team": summary.team,
                    "region": summary.region,
                    "count": summary.count,
                    "P10": round(summary.p10, 2),
                    "P50": round(summary.p50, 2),
                    "P90": round(summary.p90, 2),
                }
            )


def write_metadata(summaries: List[QuantileSummary], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "group_columns": GROUP_COLUMNS,
        "target_column": TARGET_COLUMN,
        "summaries": [asdict(summary) for summary in summaries],
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--modeling-path",
        type=Path,
        default=DEFAULT_MODELING_PATH,
        help=f"Path to the modeling dataset (default: {DEFAULT_MODELING_PATH}).",
    )
    parser.add_argument(
        "--predictions-path",
        type=Path,
        default=DEFAULT_PREDICTIONS_PATH,
        help=(
            "Where to store the group-level quantiles, typically "
            f"{DEFAULT_PREDICTIONS_PATH}."
        ),
    )
    parser.add_argument(
        "--metadata-path",
        type=Path,
        default=DEFAULT_METADATA_PATH,
        help=f"Where to store metadata about the computation (default: {DEFAULT_METADATA_PATH}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    aggregates = load_modeling_data(args.modeling_path)
    summaries = summarize_quantiles(aggregates)
    write_predictions(summaries, args.predictions_path)
    write_metadata(summaries, args.metadata_path)
    print(
        "Computed quantiles for"
        f" {len(summaries)} groups and stored results in {args.predictions_path}"
    )


if __name__ == "__main__":
    main()
