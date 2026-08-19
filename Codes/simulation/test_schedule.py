#!/usr/bin/env python3
"""Focused regression tests for trace schedulers."""

from __future__ import annotations

import unittest

if __package__:
    from .schedule import (
        AccessGraph,
        Block,
        Task,
        _diskjoin_stream_side,
        block_rcm_schedule,
        diskjoin_mecc_schedule,
        row_major_schedule,
        validate_schedule,
    )
else:
    from schedule import (
        AccessGraph,
        Block,
        Task,
        _diskjoin_stream_side,
        block_rcm_schedule,
        diskjoin_mecc_schedule,
        row_major_schedule,
        validate_schedule,
    )


class DiskJoinMECCTests(unittest.TestCase):
    def test_greedy_order_groups_stream_rows_and_maximizes_overlap(self) -> None:
        blocks = {
            **{f"D{i}": Block(f"D{i}", "D", 64) for i in range(4)},
            **{f"Q{i}": Block(f"Q{i}", "Q", 16) for i in range(3)},
        }
        graph = AccessGraph(
            blocks,
            (
                Task("D0", "Q0"),
                Task("D0", "Q1"),
                Task("D1", "Q0"),
                Task("D1", "Q1"),
                Task("D2", "Q2"),
                Task("D3", "Q1"),
            ),
        )

        schedule = diskjoin_mecc_schedule(graph, 256, window_size=1)
        validate_schedule(graph, schedule)
        row_order: list[str] = []
        for task in schedule:
            if not row_order or task.d_block != row_order[-1]:
                row_order.append(task.d_block)

        # D0 is the deterministic maximum-degree root. D1 must follow because
        # it overlaps both of D0's neighbors, more than any other row.
        self.assertEqual(row_order[:2], ["D0", "D1"])
        self.assertEqual(len(row_order), len(set(row_order)))

    def test_stream_side_uses_whole_relation_size_not_only_active_blocks(self) -> None:
        blocks = {
            "D0": Block("D0", "D", 64),
            "D1": Block("D1", "D", 64),  # pruned but part of relation D
            "Q0": Block("Q0", "Q", 60),
            "Q1": Block("Q1", "Q", 60),
        }
        graph = AccessGraph(
            blocks,
            (Task("D0", "Q0"), Task("D0", "Q1")),
        )

        # Referenced bytes alone would choose Q (120 > 64), while DiskJoin's
        # relation-level rule correctly chooses D (128 > 120).
        self.assertEqual(_diskjoin_stream_side(graph), "D")


class BlockRCMTests(unittest.TestCase):
    def test_groups_every_d_block_once(self) -> None:
        blocks = {
            **{f"D{i}": Block(f"D{i}", "D", 64) for i in range(4)},
            **{f"Q{i}": Block(f"Q{i}", "Q", 64) for i in range(4)},
        }
        graph = AccessGraph(
            blocks,
            (
                Task("D0", "Q0"),
                Task("D0", "Q2"),
                Task("D1", "Q0"),
                Task("D1", "Q1"),
                Task("D2", "Q1"),
                Task("D2", "Q3"),
                Task("D3", "Q0"),
                Task("D3", "Q3"),
            ),
        )

        schedule = block_rcm_schedule(graph)
        validate_schedule(graph, schedule)
        positions_by_d: dict[str, list[int]] = {}
        for position, task in enumerate(schedule):
            positions_by_d.setdefault(task.d_block, []).append(position)

        for positions in positions_by_d.values():
            self.assertEqual(positions, list(range(positions[0], positions[-1] + 1)))

    def test_can_group_q_instead(self) -> None:
        blocks = {
            **{f"D{i}": Block(f"D{i}", "D", 64) for i in range(2)},
            **{f"Q{i}": Block(f"Q{i}", "Q", 64) for i in range(2)},
        }
        graph = AccessGraph(
            blocks,
            (
                Task("D0", "Q0"),
                Task("D0", "Q1"),
                Task("D1", "Q0"),
                Task("D1", "Q1"),
            ),
        )

        schedule = block_rcm_schedule(graph, group_side="Q")
        validate_schedule(graph, schedule)
        q_runs = [task.q_block for task in schedule]
        self.assertLessEqual(
            sum(left != right for left, right in zip(q_runs, q_runs[1:])),
            1,
        )


class RowMajorTests(unittest.TestCase):
    def test_uses_natural_numeric_block_order(self) -> None:
        blocks = {
            "D2": Block("D2", "D", 64),
            "D10": Block("D10", "D", 64),
            "Q2": Block("Q2", "Q", 64),
            "Q10": Block("Q10", "Q", 64),
        }
        graph = AccessGraph(
            blocks,
            (
                Task("D10", "Q10"),
                Task("D2", "Q10"),
                Task("D10", "Q2"),
                Task("D2", "Q2"),
            ),
        )

        self.assertEqual(
            row_major_schedule(graph),
            (
                Task("D2", "Q2"),
                Task("D2", "Q10"),
                Task("D10", "Q2"),
                Task("D10", "Q10"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
