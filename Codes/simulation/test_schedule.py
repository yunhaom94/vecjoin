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
        diskjoin_mecc_schedule,
        validate_schedule,
    )
else:
    from schedule import (
        AccessGraph,
        Block,
        Task,
        _diskjoin_stream_side,
        diskjoin_mecc_schedule,
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


if __name__ == "__main__":
    unittest.main()
