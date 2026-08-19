#!/usr/bin/env python3
"""Run a scalable spiral-versus-RCM sparse-matrix benchmark sweep.

The runner reads ``sweep_config.json`` by default and writes one JSON object per
scheduler/cache-policy result.  Matrix density is expressed as average
nonzeros per row, so a 100000 x 100000 matrix can be represented without
materializing its 10 billion cells.

Skew controls the Zipf distribution of row degrees.  Zipf ranks are randomly
assigned to physical row ids so skew is not accidentally correlated with the
outside boundary used by the spiral schedule.  Each row's distinct columns are
generated with a deterministic modular permutation.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

if __package__:
    from .compare_spiral import sparse_spiral_schedule
    from .schedule import (
        AccessGraph,
        Block,
        SimulationResult,
        Task,
        block_rcm_schedule,
        diskjoin_mecc_schedule,
        format_bytes,
        parse_byte_size,
        simulate_schedule,
    )
else:
    from compare_spiral import sparse_spiral_schedule
    from schedule import (
        AccessGraph,
        Block,
        SimulationResult,
        Task,
        block_rcm_schedule,
        diskjoin_mecc_schedule,
        format_bytes,
        parse_byte_size,
        simulate_schedule,
    )


DEFAULT_CONFIG = Path(__file__).with_name("sweep_config.json")
MASK_64 = (1 << 64) - 1


@dataclass(frozen=True)
class GeneratedGraph:
    graph: AccessGraph
    row_degrees: tuple[int, ...]
    requested_tasks: int
    target_tasks: int
    clipped_by_task_limit: bool


def _mix64(value: int) -> int:
    """Deterministic SplitMix64 finalizer."""

    value = (value + 0x9E3779B97F4A7C15) & MASK_64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK_64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK_64
    return value ^ (value >> 31)


def _coprime_stride(size: int, seed: int) -> int:
    if size == 1:
        return 1
    stride = 1 + seed % (size - 1)
    while math.gcd(stride, size) != 1:
        stride += 1
        if stride == size:
            stride = 1
    return stride


def allocate_row_degrees(
    rows: int,
    target_tasks: int,
    zipf_alpha: float,
    seed: int,
) -> tuple[int, ...]:
    """Allocate exactly ``target_tasks`` across rows with a capped Zipf law."""

    if rows <= 0:
        raise ValueError("row count must be positive")
    if not 0 <= target_tasks <= rows * rows:
        raise ValueError("target task count must be between zero and rows squared")
    if zipf_alpha < 0:
        raise ValueError("Zipf alpha cannot be negative")

    row_for_rank = list(range(rows))
    random.Random(seed).shuffle(row_for_rank)

    if zipf_alpha == 0.0:
        base, remainder = divmod(target_tasks, rows)
        degrees = [base] * rows
        for rank in range(remainder):
            degrees[row_for_rank[rank]] += 1
        return tuple(degrees)

    weights = [(rank + 1) ** (-zipf_alpha) for rank in range(rows)]
    fractional = [0.0] * rows
    active = list(range(rows))
    remaining_tasks = target_tasks

    # Water-fill Zipf shares while respecting the per-row maximum of `rows`.
    while active:
        active_weight = sum(weights[rank] for rank in active)
        capped = [
            rank
            for rank in active
            if remaining_tasks * weights[rank] / active_weight >= rows
        ]
        if not capped:
            for rank in active:
                fractional[rank] = remaining_tasks * weights[rank] / active_weight
            break
        for rank in capped:
            fractional[rank] = float(rows)
            remaining_tasks -= rows
        capped_set = set(capped)
        active = [rank for rank in active if rank not in capped_set]

    integer_by_rank = [min(rows, int(value)) for value in fractional]
    remainder = target_tasks - sum(integer_by_rank)
    candidates = sorted(
        (rank for rank in range(rows) if integer_by_rank[rank] < rows),
        key=lambda rank: (fractional[rank] - integer_by_rank[rank], -rank),
        reverse=True,
    )
    if remainder > len(candidates):
        raise AssertionError("degree rounding remainder exceeds the active row count")
    for rank in candidates[:remainder]:
        integer_by_rank[rank] += 1

    degrees = [0] * rows
    for rank, row in enumerate(row_for_rank):
        degrees[row] = integer_by_rank[rank]
    if sum(degrees) != target_tasks or max(degrees, default=0) > rows:
        raise AssertionError("invalid capped-Zipf degree allocation")
    return tuple(degrees)


def generate_sparse_square_graph(
    size: int,
    average_nonzeros_per_row: float,
    row_degree_zipf_alpha: float,
    d_block_size: int,
    q_block_size: int,
    seed: int,
    max_tasks: int,
) -> GeneratedGraph:
    """Generate a square sparse graph in O(size + number of tasks)."""

    if size <= 0:
        raise ValueError("matrix size must be positive")
    if average_nonzeros_per_row < 0:
        raise ValueError("average nonzeros per row cannot be negative")
    requested_tasks = min(size * size, round(size * average_nonzeros_per_row))
    target_tasks = min(requested_tasks, max_tasks)
    if target_tasks <= 0:
        raise ValueError("each generated graph must contain at least one task")

    row_degrees = allocate_row_degrees(
        size,
        target_tasks,
        row_degree_zipf_alpha,
        seed,
    )
    d_names = [f"D{index}" for index in range(size)]
    q_names = [f"Q{index}" for index in range(size)]
    blocks = {
        name: Block(name, "D", d_block_size) for name in d_names
    } | {
        name: Block(name, "Q", q_block_size) for name in q_names
    }

    tasks: list[Task] = []
    tasks_append = tasks.append
    for row, degree in enumerate(row_degrees):
        if degree == 0:
            continue
        row_seed = _mix64(seed ^ (row * 0xD6E8FEB86659FD93))
        offset = row_seed % size
        stride = _coprime_stride(size, _mix64(row_seed))
        d_name = d_names[row]
        for index in range(degree):
            column = (offset + index * stride) % size
            tasks_append(Task(d_name, q_names[column]))

    if len(tasks) != target_tasks:
        raise AssertionError("generated task count differs from the degree allocation")
    graph = AccessGraph(blocks=blocks, tasks=tuple(tasks))
    return GeneratedGraph(
        graph=graph,
        row_degrees=row_degrees,
        requested_tasks=requested_tasks,
        target_tasks=target_tasks,
        clipped_by_task_limit=target_tasks != requested_tasks,
    )


def degree_statistics(degrees: Sequence[int]) -> dict[str, float | int]:
    ordered = sorted(degrees)

    def percentile(fraction: float) -> int:
        if not ordered:
            return 0
        return ordered[round(fraction * (len(ordered) - 1))]

    mean = statistics.fmean(ordered) if ordered else 0.0
    population_stddev = statistics.pstdev(ordered) if len(ordered) > 1 else 0.0
    return {
        "minimum": ordered[0] if ordered else 0,
        "mean": mean,
        "p50": percentile(0.50),
        "p95": percentile(0.95),
        "p99": percentile(0.99),
        "maximum": ordered[-1] if ordered else 0,
        "coefficient_of_variation": population_stddev / mean if mean else 0.0,
    }


def load_config(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as input_file:
        config = json.load(input_file)
    if not isinstance(config, dict):
        raise ValueError("sweep config must be a JSON object")
    return config


def _require_list(config: dict[str, object], key: str) -> list[object]:
    value = config.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"config field {key!r} must be a non-empty list")
    return value


def _profile(profile: object, fields: Iterable[str]) -> dict[str, object]:
    if not isinstance(profile, dict):
        raise ValueError("sweep profiles must be JSON objects")
    for field in fields:
        if field not in profile:
            raise ValueError(f"profile is missing field {field!r}")
    return profile


def _result_record(
    *,
    config_path: Path,
    size: int,
    density: dict[str, object],
    skew: dict[str, object],
    repetition: int,
    graph_seed: int,
    generated: GeneratedGraph,
    scheduler: str,
    policy: str,
    schedule_seconds: float,
    simulation_seconds: float,
    result: SimulationResult,
    d_block_size: int,
    q_block_size: int,
    device_capacity: int,
    host_capacity: int,
    victim_admission: str,
) -> dict[str, object]:
    return {
        "status": "ok",
        "config": str(config_path),
        "matrix": {
            "rows": size,
            "columns": size,
            "cells": size * size,
            "tasks": generated.target_tasks,
            "density": generated.target_tasks / (size * size),
            "requested_tasks": generated.requested_tasks,
            "clipped_by_task_limit": generated.clipped_by_task_limit,
            "density_profile": density["name"],
            "average_nonzeros_per_row": generated.target_tasks / size,
            "skew_profile": skew["name"],
            "row_degree_zipf_alpha": skew["row_degree_zipf_alpha"],
            "row_degree_statistics": degree_statistics(generated.row_degrees),
        },
        "run": {
            "repetition": repetition,
            "seed": graph_seed,
            "scheduler": scheduler,
            "cache_policy": policy,
            "victim_admission": victim_admission,
            "schedule_seconds": schedule_seconds,
            "simulation_seconds": simulation_seconds,
        },
        "bytes": {
            "d_block": d_block_size,
            "q_block": q_block_size,
            "device_capacity": device_capacity,
            "host_capacity": host_capacity,
        },
        "metrics": result.to_dict(),
    }


def _record_key(record: dict[str, object]) -> tuple[object, ...]:
    matrix = record["matrix"]
    run = record["run"]
    if not isinstance(matrix, dict) or not isinstance(run, dict):
        raise ValueError("invalid result record")
    return (
        matrix["rows"],
        matrix["density_profile"],
        matrix["skew_profile"],
        run["repetition"],
        run["scheduler"],
        run["cache_policy"],
    )


def read_completed_keys(path: Path) -> set[tuple[object, ...]]:
    completed: set[tuple[object, ...]] = set()
    with path.open("r", encoding="utf-8") as result_file:
        for line_number, line in enumerate(result_file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                completed.add(_record_key(record))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid result JSONL at line {line_number}: {error}") from error
    return completed


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, help="override the config's output path")
    parser.add_argument("--max-matrix-size", type=int, help="run only sizes at or below this value")
    parser.add_argument("--limit-graphs", type=int, help="stop after this many graph configurations")
    parser.add_argument("--dry-run", action="store_true")
    output_mode = parser.add_mutually_exclusive_group()
    output_mode.add_argument("--resume", action="store_true")
    output_mode.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        config_path = args.config.resolve()
        config = load_config(config_path)
        sizes = [int(size) for size in _require_list(config, "matrix_sizes")]
        if args.max_matrix_size is not None:
            sizes = [size for size in sizes if size <= args.max_matrix_size]
        if not sizes:
            raise ValueError("no configured matrix sizes remain after filtering")

        densities = [
            _profile(profile, ("name", "average_nonzeros_per_row"))
            for profile in _require_list(config, "density_profiles")
        ]
        skews = [
            _profile(profile, ("name", "row_degree_zipf_alpha"))
            for profile in _require_list(config, "skew_profiles")
        ]
        scheduler_names = [str(name) for name in _require_list(config, "schedulers")]
        known_schedulers = {"spiral", "diskjoin-mecc", "block-rcm"}
        unknown_schedulers = set(scheduler_names) - known_schedulers
        if unknown_schedulers:
            raise ValueError(f"unknown schedulers: {sorted(unknown_schedulers)}")

        block_sizes = config.get("block_sizes")
        cache = config.get("cache")
        if not isinstance(block_sizes, dict) or not isinstance(cache, dict):
            raise ValueError("block_sizes and cache must be JSON objects")
        d_block_size = parse_byte_size(block_sizes.get("d"))
        q_block_size = parse_byte_size(block_sizes.get("q"))
        device_capacity = parse_byte_size(cache.get("device_capacity"))
        host_capacity = parse_byte_size(cache.get("host_capacity"))
        policies = [str(policy) for policy in cache.get("policies", [])]
        if not policies or any(policy not in {"belady", "lru"} for policy in policies):
            raise ValueError("cache policies must be a non-empty subset of belady and lru")
        victim_admission = str(cache.get("victim_admission", "future"))
        if victim_admission not in {"none", "future", "always"}:
            raise ValueError("invalid victim-admission policy")
        scheduler_functions: dict[str, Callable[[AccessGraph], tuple[Task, ...]]] = {
            "spiral": sparse_spiral_schedule,
            "diskjoin-mecc": lambda graph: diskjoin_mecc_schedule(
                graph, device_capacity
            ),
            "block-rcm": block_rcm_schedule,
        }

        base_seed = int(config.get("seed", 0))
        repetitions = int(config.get("repetitions", 1))
        max_tasks = int(config.get("max_tasks_per_graph", 2_000_000))
        if repetitions <= 0 or max_tasks <= 0:
            raise ValueError("repetitions and max_tasks_per_graph must be positive")

        configured_output = Path(str(config.get("output", "sweep_results.jsonl")))
        output_path = args.output or (
            configured_output
            if configured_output.is_absolute()
            else config_path.parent / configured_output
        )
        output_path = output_path.resolve()

        graph_combinations = len(sizes) * len(densities) * len(skews) * repetitions
        result_combinations = graph_combinations * len(scheduler_names) * len(policies)
        largest_size = max(sizes)
        largest_average_degree = max(float(item["average_nonzeros_per_row"]) for item in densities)
        largest_tasks = min(
            largest_size * largest_size,
            round(largest_size * largest_average_degree),
            max_tasks,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))

    print(
        f"planned: {graph_combinations} graphs, {result_combinations} results; "
        f"sizes={len(sizes)} ({min(sizes)}..{max(sizes)}), "
        f"largest graph={largest_tasks:,} tasks"
    )
    print(
        f"cache: C_d={format_bytes(device_capacity)}, C_h={format_bytes(host_capacity)}; "
        f"policies={','.join(policies)}, admission={victim_admission}"
    )
    if args.dry_run:
        return 0

    if output_path.exists() and not args.resume and not args.overwrite:
        parser.error(f"output {output_path} exists; use --resume or --overwrite")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    completed = read_completed_keys(output_path) if args.resume and output_path.exists() else set()
    mode = "a" if args.resume else "w" if args.overwrite else "x"

    graph_number = 0
    result_number = 0
    start_time = time.perf_counter()
    with output_path.open(mode, encoding="utf-8") as output_file:
        stop = False
        for size_index, size in enumerate(sizes):
            for density_index, density in enumerate(densities):
                for skew_index, skew in enumerate(skews):
                    for repetition in range(repetitions):
                        if args.limit_graphs is not None and graph_number >= args.limit_graphs:
                            stop = True
                            break
                        graph_number += 1
                        graph_seed = (
                            base_seed
                            + size_index * 1_000_003
                            + density_index * 10_007
                            + skew_index * 101
                            + repetition
                        )
                        generated = generate_sparse_square_graph(
                            size=size,
                            average_nonzeros_per_row=float(
                                density["average_nonzeros_per_row"]
                            ),
                            row_degree_zipf_alpha=float(skew["row_degree_zipf_alpha"]),
                            d_block_size=d_block_size,
                            q_block_size=q_block_size,
                            seed=graph_seed,
                            max_tasks=max_tasks,
                        )

                        for scheduler_name in scheduler_names:
                            pending_policies = [
                                policy
                                for policy in policies
                                if (
                                    size,
                                    density["name"],
                                    skew["name"],
                                    repetition,
                                    scheduler_name,
                                    policy,
                                )
                                not in completed
                            ]
                            if not pending_policies:
                                continue

                            schedule_start = time.perf_counter()
                            schedule = scheduler_functions[scheduler_name](generated.graph)
                            schedule_seconds = time.perf_counter() - schedule_start

                            for policy in pending_policies:
                                simulation_start = time.perf_counter()
                                result = simulate_schedule(
                                    generated.graph,
                                    schedule,
                                    scheduler_name,
                                    device_capacity,
                                    host_capacity,
                                    policy,
                                    victim_admission,
                                )
                                simulation_seconds = time.perf_counter() - simulation_start
                                record = _result_record(
                                    config_path=config_path,
                                    size=size,
                                    density=density,
                                    skew=skew,
                                    repetition=repetition,
                                    graph_seed=graph_seed,
                                    generated=generated,
                                    scheduler=scheduler_name,
                                    policy=policy,
                                    schedule_seconds=schedule_seconds,
                                    simulation_seconds=simulation_seconds,
                                    result=result,
                                    d_block_size=d_block_size,
                                    q_block_size=q_block_size,
                                    device_capacity=device_capacity,
                                    host_capacity=host_capacity,
                                    victim_admission=victim_admission,
                                )
                                output_file.write(json.dumps(record, sort_keys=True) + "\n")
                                output_file.flush()
                                result_number += 1
                                elapsed = time.perf_counter() - start_time
                                print(
                                    f"[{result_number}/{result_combinations}] n={size:,} "
                                    f"edges={generated.target_tasks:,} "
                                    f"density={density['name']} skew={skew['name']} "
                                    f"scheduler={scheduler_name} policy={policy} "
                                    f"I/Os={result.total_io_operations:,} "
                                    f"bytes={format_bytes(result.total_io_bytes)} "
                                    f"elapsed={elapsed:.1f}s",
                                    flush=True,
                                )
                            del schedule
                            gc.collect()
                        del generated
                        gc.collect()
                    if stop:
                        break
                if stop:
                    break
            if stop:
                break

    elapsed = time.perf_counter() - start_time
    print(f"wrote {result_number} new results to {output_path} in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
