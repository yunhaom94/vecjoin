#!/usr/bin/env python3
"""Flatten matched scheduler results into one comparison row per workload."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Sequence


DEFAULT_INPUT = Path(__file__).with_name("sweep_results.jsonl")
DEFAULT_OUTPUT = Path(__file__).with_name("sweep_summary.csv")
SCHEDULERS = ("row-major", "diskjoin-mecc", "block-rcm")
SCHEDULER_PREFIX = {
    "row-major": "row_major",
    "diskjoin-mecc": "diskjoin_mecc",
    "block-rcm": "block_rcm",
}
METRICS = (
    "total_io_operations",
    "total_io_bytes",
    "ssd_io_operations",
    "ssd_io_bytes",
    "host_to_device_io_operations",
    "host_to_device_io_bytes",
    "device_to_host_io_operations",
    "device_to_host_io_bytes",
)
RATIO_METRICS = (
    "total_io_operations",
    "total_io_bytes",
    "ssd_io_operations",
    "ssd_io_bytes",
)
COMPARISONS = (
    ("diskjoin_mecc_to_row_major", "diskjoin-mecc", "row-major"),
    ("diskjoin_mecc_to_block_rcm", "diskjoin-mecc", "block-rcm"),
    ("block_rcm_to_row_major", "block-rcm", "row-major"),
)


def _match_key(record: dict[str, object]) -> tuple[object, ...]:
    matrix = record["matrix"]
    run = record["run"]
    if not isinstance(matrix, dict) or not isinstance(run, dict):
        raise ValueError("result record is missing matrix/run objects")
    return (
        matrix["rows"],
        matrix["density_profile"],
        matrix["skew_profile"],
        run["repetition"],
        run["cache_policy"],
    )


def _metric_values(record: dict[str, object]) -> dict[str, int]:
    metrics = record["metrics"]
    if not isinstance(metrics, dict):
        raise ValueError("result record is missing metrics")
    ssd = metrics["ssd_to_device"]
    host_to_device = metrics["host_to_device"]
    device_to_host = metrics["device_to_host"]
    if not all(isinstance(value, dict) for value in (ssd, host_to_device, device_to_host)):
        raise ValueError("result record contains malformed transfer counters")
    return {
        "total_io_operations": int(metrics["total_io_operations"]),
        "total_io_bytes": int(metrics["total_io_bytes"]),
        "ssd_io_operations": int(ssd["operations"]),
        "ssd_io_bytes": int(ssd["bytes"]),
        "host_to_device_io_operations": int(host_to_device["operations"]),
        "host_to_device_io_bytes": int(host_to_device["bytes"]),
        "device_to_host_io_operations": int(device_to_host["operations"]),
        "device_to_host_io_bytes": int(device_to_host["bytes"]),
    }


def load_matched_results(path: Path) -> dict[tuple[object, ...], dict[str, dict[str, object]]]:
    matched: dict[tuple[object, ...], dict[str, dict[str, object]]] = {}
    with path.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                key = _match_key(record)
                run = record["run"]
                scheduler = str(run["scheduler"])
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid JSONL record at line {line_number}: {error}") from error
            if scheduler not in SCHEDULERS:
                raise ValueError(f"unexpected scheduler {scheduler!r} at line {line_number}")
            group = matched.setdefault(key, {})
            if scheduler in group:
                raise ValueError(f"duplicate scheduler {scheduler!r} for match key {key!r}")
            group[scheduler] = record

    expected = set(SCHEDULERS)
    for key, group in matched.items():
        if set(group) != expected:
            raise ValueError(
                f"match key {key!r} has schedulers {sorted(group)}, expected {sorted(expected)}"
            )
    return matched


def _winner(values: dict[str, dict[str, int]], metric: str) -> str:
    minimum = min(values[scheduler][metric] for scheduler in SCHEDULERS)
    return "|".join(
        SCHEDULER_PREFIX[scheduler]
        for scheduler in SCHEDULERS
        if values[scheduler][metric] == minimum
    )


def _row(group: dict[str, dict[str, object]]) -> dict[str, object]:
    reference = group["row-major"]
    matrix = reference["matrix"]
    run = reference["run"]
    byte_config = reference["bytes"]
    if not all(isinstance(value, dict) for value in (matrix, run, byte_config)):
        raise ValueError("result record is missing configuration objects")

    row: dict[str, object] = {
        "matrix_rows": matrix["rows"],
        "matrix_columns": matrix["columns"],
        "matrix_tasks": matrix["tasks"],
        "matrix_density": matrix["density"],
        "density_profile": matrix["density_profile"],
        "average_nonzeros_per_row": matrix["average_nonzeros_per_row"],
        "skew_profile": matrix["skew_profile"],
        "row_degree_zipf_alpha": matrix["row_degree_zipf_alpha"],
        "repetition": run["repetition"],
        "seed": run["seed"],
        "cache_policy": run["cache_policy"],
        "victim_admission": run["victim_admission"],
        "d_block_bytes": byte_config["d_block"],
        "q_block_bytes": byte_config["q_block"],
        "device_capacity_bytes": byte_config["device_capacity"],
        "host_capacity_bytes": byte_config["host_capacity"],
    }

    values = {scheduler: _metric_values(group[scheduler]) for scheduler in SCHEDULERS}
    for scheduler in SCHEDULERS:
        prefix = SCHEDULER_PREFIX[scheduler]
        for metric in METRICS:
            row[f"{prefix}_{metric}"] = values[scheduler][metric]

    for prefix, numerator, denominator in COMPARISONS:
        for metric in RATIO_METRICS:
            denominator_value = values[denominator][metric]
            row[f"{prefix}_{metric}_ratio"] = (
                values[numerator][metric] / denominator_value
                if denominator_value
                else ""
            )

    for metric in RATIO_METRICS:
        row[f"best_{metric}_scheduler"] = _winner(values, metric)
    return row


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        matched = load_matched_results(args.input)
        rows = [_row(group) for group in matched.values()]
        rows.sort(
            key=lambda row: (
                int(row["matrix_rows"]),
                float(row["average_nonzeros_per_row"]),
                float(row["row_degree_zipf_alpha"]),
                int(row["repetition"]),
                str(row["cache_policy"]),
            )
        )
        if not rows:
            raise ValueError("input contains no matched results")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    except (OSError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error

    print(f"wrote {len(rows)} matched comparison rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
