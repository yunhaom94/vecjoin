#!/usr/bin/env python3
"""Compare an outside-in sparse-matrix spiral with other task schedules.

Rows are D blocks and columns are Q blocks.  The spiral starts at the top-left,
moves right, and proceeds clockwise from the outside inward.  Pruned cells are
skipped, while every surviving comparison-pair task is emitted exactly once.

The implementation assigns a dense-matrix spiral rank directly to each
surviving task.  It therefore needs O(|E|) auxiliary space and O(|E| log |E|)
sorting time without materializing or scanning the full |D| x |Q| matrix.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Sequence

if __package__:
    from .schedule import (
        AccessGraph,
        SimulationResult,
        Task,
        block_rcm_schedule,
        diskjoin_mecc_schedule,
        exhaustive_optimal_schedule,
        format_bytes,
        generate_synthetic_graph,
        load_graph,
        parse_byte_size,
        random_schedule,
        simulate_schedule,
        task_rcm_schedule,
        validate_schedule,
    )
else:
    from schedule import (
        AccessGraph,
        SimulationResult,
        Task,
        block_rcm_schedule,
        diskjoin_mecc_schedule,
        exhaustive_optimal_schedule,
        format_bytes,
        generate_synthetic_graph,
        load_graph,
        parse_byte_size,
        random_schedule,
        simulate_schedule,
        task_rcm_schedule,
        validate_schedule,
    )


_NATURAL_PART = re.compile(r"(\d+)")


def _natural_key(value: str) -> tuple[tuple[int, object], ...]:
    """Sort D2 before D10 while remaining deterministic for arbitrary ids."""

    return tuple(
        (1, int(part)) if part.isdigit() else (0, part.casefold())
        for part in _NATURAL_PART.split(value)
        if part
    )


def matrix_axes(graph: AccessGraph) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return deterministic D-row and Q-column orders for the pair matrix."""

    d_blocks = tuple(
        sorted(
            (block.name for block in graph.blocks.values() if block.side == "D"),
            key=lambda name: (_natural_key(name), name),
        )
    )
    q_blocks = tuple(
        sorted(
            (block.name for block in graph.blocks.values() if block.side == "Q"),
            key=lambda name: (_natural_key(name), name),
        )
    )
    if not d_blocks or not q_blocks:
        raise ValueError("the comparison matrix needs at least one D row and one Q column")
    return d_blocks, q_blocks


def outside_in_spiral_rank(row: int, column: int, rows: int, columns: int) -> int:
    """Return a cell's rank in a top-left, clockwise, outside-in spiral."""

    if rows <= 0 or columns <= 0:
        raise ValueError("matrix dimensions must be positive")
    if not 0 <= row < rows or not 0 <= column < columns:
        raise ValueError(f"cell ({row}, {column}) is outside a {rows}x{columns} matrix")

    layer = min(row, column, rows - 1 - row, columns - 1 - column)
    top = left = layer
    bottom = rows - 1 - layer
    right = columns - 1 - layer
    height = bottom - top + 1
    width = right - left + 1

    # Number of cells in all complete rings outside this layer.
    rank = rows * columns - (rows - 2 * layer) * (columns - 2 * layer)

    if height == 1:
        return rank + column - left
    if width == 1:
        return rank + row - top
    if row == top:
        return rank + column - left
    if column == right:
        return rank + width + row - top - 1
    if row == bottom:
        return rank + width + height - 1 + right - 1 - column

    # The cell must be on the left edge because `layer` is its minimum
    # distance from any matrix boundary.
    if column != left:
        raise AssertionError("cell is not on its computed spiral layer")
    return rank + 2 * width + height - 2 + bottom - 1 - row


def sparse_spiral_schedule(graph: AccessGraph) -> tuple[Task, ...]:
    """Order surviving tasks by their positions in the implicit dense spiral."""

    d_blocks, q_blocks = matrix_axes(graph)
    row_of = {name: index for index, name in enumerate(d_blocks)}
    column_of = {name: index for index, name in enumerate(q_blocks)}
    schedule = tuple(
        sorted(
            graph.tasks,
            key=lambda task: outside_in_spiral_rank(
                row_of[task.d_block],
                column_of[task.q_block],
                len(d_blocks),
                len(q_blocks),
            ),
        )
    )
    validate_schedule(graph, schedule)
    return schedule


def matrix_row_major_schedule(graph: AccessGraph) -> tuple[Task, ...]:
    d_blocks, q_blocks = matrix_axes(graph)
    row_of = {name: index for index, name in enumerate(d_blocks)}
    column_of = {name: index for index, name in enumerate(q_blocks)}
    schedule = tuple(
        sorted(graph.tasks, key=lambda task: (row_of[task.d_block], column_of[task.q_block]))
    )
    validate_schedule(graph, schedule)
    return schedule


def matrix_column_major_schedule(graph: AccessGraph) -> tuple[Task, ...]:
    d_blocks, q_blocks = matrix_axes(graph)
    row_of = {name: index for index, name in enumerate(d_blocks)}
    column_of = {name: index for index, name in enumerate(q_blocks)}
    schedule = tuple(
        sorted(graph.tasks, key=lambda task: (column_of[task.q_block], row_of[task.d_block]))
    )
    validate_schedule(graph, schedule)
    return schedule


def render_sparse_order_matrix(graph: AccessGraph, schedule: Sequence[Task]) -> str:
    """Render task visit indices; '.' marks a pruned/absent comparison."""

    validate_schedule(graph, schedule)
    d_blocks, q_blocks = matrix_axes(graph)
    visit = {task: index for index, task in enumerate(schedule)}
    cell_width = max(
        1,
        len(str(len(schedule) - 1)),
        *(len(name) for name in q_blocks),
    )
    row_width = max(len(name) for name in d_blocks)
    header = " " * (row_width + 2) + " ".join(name.rjust(cell_width) for name in q_blocks)
    lines = [header]
    for d_block in d_blocks:
        cells = [
            str(visit[Task(d_block, q_block)]).rjust(cell_width)
            if Task(d_block, q_block) in visit
            else ".".rjust(cell_width)
            for q_block in q_blocks
        ]
        lines.append(d_block.rjust(row_width) + "  " + " ".join(cells))
    return "\n".join(lines)


def _comparison_table(results: Sequence[SimulationResult]) -> str:
    headers = (
        "schedule",
        "total I/Os",
        "total bytes",
        "SSD I/Os",
        "SSD bytes",
        "H->D I/Os",
        "H->D bytes",
        "D->H I/Os",
        "D->H bytes",
    )
    rows = [
        (
            result.schedule,
            str(result.total_io_operations),
            format_bytes(result.total_io_bytes),
            str(result.ssd_to_device.operations),
            format_bytes(result.ssd_to_device.bytes),
            str(result.host_to_device.operations),
            format_bytes(result.host_to_device.bytes),
            str(result.device_to_host.operations),
            format_bytes(result.device_to_host.bytes),
        )
        for result in results
    ]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]

    def render(row: Sequence[str]) -> str:
        return "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))

    separator = "  ".join("-" * width for width in widths)
    return "\n".join((render(headers), separator, *(render(row) for row in rows)))


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", type=Path, help="access-graph JSON; otherwise generate one")
    parser.add_argument("--d-blocks", type=int, default=24)
    parser.add_argument("--q-blocks", type=int, default=24)
    parser.add_argument("--d-block-size", type=parse_byte_size, default=parse_byte_size("64MiB"))
    parser.add_argument("--q-block-size", type=parse_byte_size, default=parse_byte_size("16MiB"))
    parser.add_argument("--edge-probability", type=float, default=0.12)
    parser.add_argument("--device-capacity", type=parse_byte_size, default=parse_byte_size("256MiB"))
    parser.add_argument("--host-capacity", type=parse_byte_size, default=parse_byte_size("512MiB"))
    parser.add_argument("--policy", choices=("belady", "lru"), default="belady")
    parser.add_argument(
        "--victim-admission",
        choices=("future", "always", "none"),
        default="future",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--include-random", action="store_true")
    parser.add_argument("--include-optimal", action="store_true")
    parser.add_argument("--objective", choices=("bytes", "operations"), default="bytes")
    parser.add_argument("--optimal-max-tasks", type=int, default=9)
    parser.add_argument("--show-schedules", action="store_true")
    parser.add_argument("--show-matrix", action="store_true")
    parser.add_argument("--matrix-max-cells", type=int, default=400)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        graph = (
            load_graph(args.input)
            if args.input
            else generate_synthetic_graph(
                d_blocks=args.d_blocks,
                q_blocks=args.q_blocks,
                d_block_size=args.d_block_size,
                q_block_size=args.q_block_size,
                edge_probability=args.edge_probability,
                seed=args.seed,
            )
        )

        schedules: list[tuple[str, tuple[Task, ...]]] = [
            ("row-major", matrix_row_major_schedule(graph)),
            ("column-major", matrix_column_major_schedule(graph)),
            ("spiral", sparse_spiral_schedule(graph)),
            ("diskjoin-mecc", diskjoin_mecc_schedule(graph, args.device_capacity)),
            ("block-rcm", block_rcm_schedule(graph)),
            ("task-rcm", task_rcm_schedule(graph)),
        ]
        if args.include_random:
            schedules.append(("random", random_schedule(graph, args.seed)))
        if args.include_optimal:
            schedules.append(
                (
                    "optimal",
                    exhaustive_optimal_schedule(
                        graph,
                        args.device_capacity,
                        args.host_capacity,
                        args.policy,
                        args.victim_admission,
                        args.objective,
                        args.optimal_max_tasks,
                    ),
                )
            )

        results = [
            simulate_schedule(
                graph,
                schedule,
                name,
                args.device_capacity,
                args.host_capacity,
                args.policy,
                args.victim_admission,
            )
            for name, schedule in schedules
        ]

        d_axis, q_axis = matrix_axes(graph)
        matrix_cells = len(d_axis) * len(q_axis)
        if args.show_matrix and matrix_cells > args.matrix_max_cells:
            raise ValueError(
                f"matrix has {matrix_cells} cells; increase --matrix-max-cells to render it"
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    if args.json:
        payload: dict[str, object] = {
            "graph": {
                "d_blocks": len(d_axis),
                "q_blocks": len(q_axis),
                "matrix_cells": matrix_cells,
                "tasks": len(graph.tasks),
                "density": len(graph.tasks) / matrix_cells,
            },
            "configuration": {
                "device_capacity": args.device_capacity,
                "host_capacity": args.host_capacity,
                "policy": args.policy,
                "victim_admission": args.victim_admission,
                "seed": args.seed,
            },
            "results": [result.to_dict() for result in results],
        }
        if args.show_schedules:
            payload["schedules"] = {
                name: [task.label() for task in schedule] for name, schedule in schedules
            }
        if args.show_matrix:
            payload["spiral_matrix"] = render_sparse_order_matrix(
                graph, dict(schedules)["spiral"]
            )
        print(json.dumps(payload, indent=2))
        return 0

    print(
        f"matrix: {len(d_axis)}x{len(q_axis)}, {len(graph.tasks)} surviving tasks "
        f"({100.0 * len(graph.tasks) / matrix_cells:.2f}% dense); "
        f"C_d={format_bytes(args.device_capacity)}, C_h={format_bytes(args.host_capacity)}"
    )
    print(_comparison_table(results))
    if args.show_matrix:
        print("\nspiral visit order ('.' = pruned cell):")
        print(render_sparse_order_matrix(graph, dict(schedules)["spiral"]))
    if args.show_schedules:
        for name, schedule in schedules:
            print(f"\n{name}: " + " -> ".join(task.label() for task in schedule))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
