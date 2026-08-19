#!/usr/bin/env python3
"""Trace-level simulator for two-tier block-pair scheduling.

Every edge ``(D_i, Q_j)`` is a join task that requires both endpoint blocks in
device memory.  Device memory is the main cache and host memory is an exclusive
victim cache.  Blocks not present in either cache are read directly from SSD to
the device.

One block transfer is counted as one logical I/O.  The simulator reports the
operation count and transferred bytes separately for:

* SSD -> device
* host -> device
* device -> host

The RCM schedulers and DiskJoin's MECC approximation are heuristics, not
optimality claims.  ``optimal`` performs an exhaustive permutation search and
is intentionally restricted to tiny graphs.

An input JSON file has this shape (sizes may also be strings such as ``64MiB``):

.. code-block:: json

   {
     "d_blocks": [{"id": "D0", "size": "64MiB"}],
     "q_blocks": [{"id": "Q0", "size": "16MiB"}],
     "edges": [["D0", "Q0"]]
   }

Run ``python3 schedule.py --help`` for the synthetic-graph and cache options.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import re
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


_SIZE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([kmgtpe]?i?b)?\s*$", re.IGNORECASE)
_SIZE_MULTIPLIERS = {
    "": 1,
    "b": 1,
    "kb": 1_000,
    "mb": 1_000**2,
    "gb": 1_000**3,
    "tb": 1_000**4,
    "pb": 1_000**5,
    "eb": 1_000**6,
    "kib": 1 << 10,
    "mib": 1 << 20,
    "gib": 1 << 30,
    "tib": 1 << 40,
    "pib": 1 << 50,
    "eib": 1 << 60,
}


def parse_byte_size(value: object) -> int:
    """Parse an integer byte count or a human-readable byte size."""

    if isinstance(value, bool):
        raise ValueError("a boolean is not a byte size")
    if isinstance(value, int):
        size = value
    elif isinstance(value, float):
        if not value.is_integer():
            raise ValueError(f"byte count must be integral, got {value!r}")
        size = int(value)
    elif isinstance(value, str):
        match = _SIZE_RE.match(value)
        if match is None:
            raise ValueError(f"invalid byte size: {value!r}")
        number, suffix = match.groups()
        size = int(float(number) * _SIZE_MULTIPLIERS[(suffix or "").lower()])
    else:
        raise ValueError(f"invalid byte size: {value!r}")

    if size < 0:
        raise ValueError("byte size cannot be negative")
    return size


def format_bytes(size: int) -> str:
    """Format bytes using IEC units."""

    if size < 0:
        raise ValueError("byte size cannot be negative")
    value = float(size)
    for suffix in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if value < 1024.0 or suffix == "PiB":
            if suffix == "B":
                return f"{int(value)} {suffix}"
            return f"{value:.2f} {suffix}"
        value /= 1024.0
    raise AssertionError("unreachable")


@dataclass(frozen=True, order=True)
class Block:
    name: str
    side: str
    size_bytes: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("block name cannot be empty")
        if self.side not in {"D", "Q"}:
            raise ValueError(f"block {self.name!r} has invalid side {self.side!r}")
        if self.size_bytes <= 0:
            raise ValueError(f"block {self.name!r} must have positive size")


@dataclass(frozen=True, order=True)
class Task:
    d_block: str
    q_block: str

    @property
    def blocks(self) -> tuple[str, str]:
        return (self.d_block, self.q_block)

    def label(self) -> str:
        return f"({self.d_block},{self.q_block})"


@dataclass
class AccessGraph:
    blocks: dict[str, Block]
    tasks: tuple[Task, ...]

    def __post_init__(self) -> None:
        if not self.tasks:
            raise ValueError("the access graph must contain at least one task")
        if len(set(self.tasks)) != len(self.tasks):
            raise ValueError("duplicate edges/tasks are not allowed")

        for task in self.tasks:
            try:
                d_block = self.blocks[task.d_block]
                q_block = self.blocks[task.q_block]
            except KeyError as error:
                raise ValueError(f"task references unknown block {error.args[0]!r}") from error
            if d_block.side != "D" or q_block.side != "Q":
                raise ValueError(
                    f"task {task.label()} must reference a D block followed by a Q block"
                )

    def task_working_set_bytes(self, task: Task) -> int:
        return sum(self.blocks[name].size_bytes for name in task.blocks)


@dataclass
class TransferCounter:
    operations: int = 0
    bytes: int = 0

    def record(self, size_bytes: int) -> None:
        self.operations += 1
        self.bytes += size_bytes

    @property
    def average_bytes(self) -> float:
        return self.bytes / self.operations if self.operations else 0.0


@dataclass
class SimulationResult:
    schedule: str
    tasks: int
    block_accesses: int = 0
    device_hits: int = 0
    host_hits: int = 0
    ssd_misses: int = 0
    ssd_to_device: TransferCounter = field(default_factory=TransferCounter)
    host_to_device: TransferCounter = field(default_factory=TransferCounter)
    device_to_host: TransferCounter = field(default_factory=TransferCounter)

    @property
    def total_io_operations(self) -> int:
        return (
            self.ssd_to_device.operations
            + self.host_to_device.operations
            + self.device_to_host.operations
        )

    @property
    def total_io_bytes(self) -> int:
        return self.ssd_to_device.bytes + self.host_to_device.bytes + self.device_to_host.bytes

    @property
    def average_io_bytes(self) -> float:
        if not self.total_io_operations:
            return 0.0
        return self.total_io_bytes / self.total_io_operations

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result.update(
            total_io_operations=self.total_io_operations,
            total_io_bytes=self.total_io_bytes,
            average_io_bytes=self.average_io_bytes,
        )
        return result


class FutureUses:
    """Remaining task positions for every block in a fixed schedule."""

    def __init__(self, schedule: Sequence[Task]) -> None:
        self._positions: dict[str, deque[int]] = defaultdict(deque)
        for position, task in enumerate(schedule):
            for block_name in task.blocks:
                self._positions[block_name].append(position)

    def consume(self, block_names: Iterable[str], position: int) -> None:
        for block_name in block_names:
            positions = self._positions[block_name]
            if not positions or positions[0] != position:
                raise AssertionError(f"invalid future-use trace for {block_name!r}")
            positions.popleft()

    def next_use(self, block_name: str) -> float:
        positions = self._positions.get(block_name)
        return float(positions[0]) if positions else math.inf


class TwoTierCacheSimulator:
    """Simulate an exclusive VRAM cache plus RAM victim cache.

    ``belady`` evicts the block with the furthest next use.  This is optimal for
    one cache with equal-sized blocks, but remains a heuristic for variable-sized
    blocks and for the coupled two-tier hierarchy.
    """

    def __init__(
        self,
        graph: AccessGraph,
        schedule: Sequence[Task],
        device_capacity: int,
        host_capacity: int,
        policy: str = "belady",
        victim_admission: str = "future",
    ) -> None:
        if device_capacity <= 0:
            raise ValueError("device capacity must be positive")
        if host_capacity < 0:
            raise ValueError("host capacity cannot be negative")
        if policy not in {"lru", "belady"}:
            raise ValueError(f"unknown cache policy {policy!r}")
        if victim_admission not in {"none", "future", "always"}:
            raise ValueError(f"unknown victim admission policy {victim_admission!r}")

        validate_schedule(graph, schedule)
        for task in schedule:
            required = graph.task_working_set_bytes(task)
            if required > device_capacity:
                raise ValueError(
                    f"task {task.label()} needs {format_bytes(required)}, exceeding device "
                    f"capacity {format_bytes(device_capacity)}"
                )

        self.graph = graph
        self.schedule = tuple(schedule)
        self.device_capacity = device_capacity
        self.host_capacity = host_capacity
        self.policy = policy
        self.victim_admission = victim_admission
        self.future = FutureUses(schedule)

        # Cache values are the most recent access/admission positions for LRU.
        self.device: dict[str, int] = {}
        self.host: dict[str, int] = {}
        self.device_bytes = 0
        self.host_bytes = 0

    def run(self, schedule_name: str) -> SimulationResult:
        result = SimulationResult(schedule=schedule_name, tasks=len(self.schedule))

        for position, task in enumerate(self.schedule):
            required = set(task.blocks)
            self.future.consume(required, position)
            result.block_accesses += len(required)

            initially_on_device = required & self.device.keys()
            initially_on_host = required & self.host.keys()
            initially_on_ssd = required - initially_on_device - initially_on_host
            result.device_hits += len(initially_on_device)
            result.host_hits += len(initially_on_host)
            result.ssd_misses += len(initially_on_ssd)

            # Promote host hits first and protect the other operands that this
            # task still needs from being displaced by victim admissions.
            host_protected = set(initially_on_host)
            for block_name in sorted(initially_on_host):
                host_protected.remove(block_name)
                self._promote_from_host(
                    block_name,
                    position,
                    device_protected=required,
                    host_protected=host_protected,
                    result=result,
                )

            for block_name in sorted(initially_on_ssd):
                self._load_from_ssd(
                    block_name,
                    position,
                    device_protected=required,
                    host_protected=set(),
                    result=result,
                )

            for block_name in required:
                if block_name not in self.device:
                    raise AssertionError(f"required block {block_name!r} is not on the device")
                self.device[block_name] = position

            self._assert_invariants()

        return result

    def _promote_from_host(
        self,
        block_name: str,
        position: int,
        device_protected: set[str],
        host_protected: set[str],
        result: SimulationResult,
    ) -> None:
        if block_name not in self.host:
            raise AssertionError(f"host hit {block_name!r} was displaced before promotion")
        size = self.graph.blocks[block_name].size_bytes
        del self.host[block_name]
        self.host_bytes -= size
        self._make_device_space(
            size,
            position,
            device_protected,
            host_protected,
            result,
        )
        result.host_to_device.record(size)
        self.device[block_name] = position
        self.device_bytes += size

    def _load_from_ssd(
        self,
        block_name: str,
        position: int,
        device_protected: set[str],
        host_protected: set[str],
        result: SimulationResult,
    ) -> None:
        size = self.graph.blocks[block_name].size_bytes
        self._make_device_space(
            size,
            position,
            device_protected,
            host_protected,
            result,
        )
        result.ssd_to_device.record(size)
        self.device[block_name] = position
        self.device_bytes += size

    def _make_device_space(
        self,
        incoming_size: int,
        position: int,
        device_protected: set[str],
        host_protected: set[str],
        result: SimulationResult,
    ) -> None:
        while self.device_bytes + incoming_size > self.device_capacity:
            candidates = [name for name in self.device if name not in device_protected]
            if not candidates:
                raise ValueError(
                    "device capacity cannot hold the current task's required blocks together"
                )
            victim = self._choose_victim(self.device, candidates)
            size = self.graph.blocks[victim].size_bytes
            del self.device[victim]
            self.device_bytes -= size
            self._admit_to_host(victim, position, host_protected, result)

    def _admit_to_host(
        self,
        block_name: str,
        position: int,
        host_protected: set[str],
        result: SimulationResult,
    ) -> None:
        size = self.graph.blocks[block_name].size_bytes
        if self.victim_admission == "none" or self.host_capacity == 0:
            return
        if size > self.host_capacity:
            return
        if self.victim_admission == "future" and math.isinf(self.future.next_use(block_name)):
            return

        candidate_cache = dict(self.host)
        candidate_cache[block_name] = position
        candidate_bytes = self.host_bytes + size

        while candidate_bytes > self.host_capacity:
            evictable = [name for name in candidate_cache if name not in host_protected]
            if not evictable:
                return
            victim = self._choose_victim(candidate_cache, evictable)
            candidate_bytes -= self.graph.blocks[victim].size_bytes
            del candidate_cache[victim]

        if block_name not in candidate_cache:
            return

        self.host = candidate_cache
        self.host_bytes = candidate_bytes
        result.device_to_host.record(size)

    def _choose_victim(self, cache: Mapping[str, int], candidates: Sequence[str]) -> str:
        if self.policy == "lru":
            return min(candidates, key=lambda name: (cache[name], name))
        return max(
            candidates,
            key=lambda name: (
                self.future.next_use(name),
                self.graph.blocks[name].size_bytes,
                name,
            ),
        )

    def _assert_invariants(self) -> None:
        if self.device.keys() & self.host.keys():
            raise AssertionError("exclusive caches contain the same block")
        if self.device_bytes != sum(self.graph.blocks[name].size_bytes for name in self.device):
            raise AssertionError("incorrect device-cache byte accounting")
        if self.host_bytes != sum(self.graph.blocks[name].size_bytes for name in self.host):
            raise AssertionError("incorrect host-cache byte accounting")
        if self.device_bytes > self.device_capacity:
            raise AssertionError("device-cache capacity exceeded")
        if self.host_bytes > self.host_capacity:
            raise AssertionError("host-cache capacity exceeded")


def validate_schedule(graph: AccessGraph, schedule: Sequence[Task]) -> None:
    if len(schedule) != len(graph.tasks) or set(schedule) != set(graph.tasks):
        raise ValueError("a schedule must contain every graph task exactly once")


def row_major_schedule(graph: AccessGraph) -> tuple[Task, ...]:
    return tuple(sorted(graph.tasks))


def random_schedule(graph: AccessGraph, seed: int) -> tuple[Task, ...]:
    tasks = list(graph.tasks)
    random.Random(seed).shuffle(tasks)
    return tuple(tasks)


def _block_order_key(name: str) -> tuple[str, int, str]:
    """Return a deterministic key that orders ``Q2`` before ``Q10``."""

    match = re.match(r"^(.*?)(\d+)$", name)
    if match is None:
        return (name.casefold(), -1, name)
    prefix, number = match.groups()
    return (prefix.casefold(), int(number), name)


def _diskjoin_stream_side(graph: AccessGraph) -> str:
    """Choose the larger relation, as recommended for DiskJoin cross-joins."""

    side_bytes = {
        side: sum(
            block.size_bytes
            for block in graph.blocks.values()
            if block.side == side
        )
        for side in ("D", "Q")
    }
    # D is the deterministic tie break and the conventional streamed relation.
    return "Q" if side_bytes["Q"] > side_bytes["D"] else "D"


def diskjoin_mecc_schedule(
    graph: AccessGraph,
    device_capacity: int,
    *,
    window_size: int | None = None,
) -> tuple[Task, ...]:
    """Approximate MECC using DiskJoin's cross-join Gorder heuristic.

    DiskJoin streams the larger relation and caches the smaller relation.  It
    processes every edge of a streaming-side block consecutively, while the
    streaming blocks are greedily ordered to maximize common cached-side
    neighbors within a sliding window.  The paper chooses
    ``w = C / average_out_degree``.

    The original algorithm assumes equal-sized buckets and one cache.  This
    simulator uses a byte-capacity device cache and unequal D/Q blocks, so ``C``
    is conservatively derived as the number of largest cached-side blocks that
    fit after reserving the largest current streaming block.  ``window_size``
    can override this derivation for reference tests and sensitivity studies.

    Candidate overlap scores are maintained with integer score buckets.  This
    is equivalent to the incremental score updates in DiskJoin's ``Gorder.h``,
    but uses O(|V| + |E|) memory without accumulating stale heap entries.
    """

    if device_capacity <= 0:
        raise ValueError("device capacity must be positive")
    if window_size is not None and window_size <= 0:
        raise ValueError("DiskJoin's Gorder window must be positive")

    stream_side = _diskjoin_stream_side(graph)
    cached_side = "Q" if stream_side == "D" else "D"
    stream_names = sorted(
        {
            task.d_block if stream_side == "D" else task.q_block
            for task in graph.tasks
        },
        key=_block_order_key,
    )
    cached_names = sorted(
        {
            task.q_block if stream_side == "D" else task.d_block
            for task in graph.tasks
        },
        key=_block_order_key,
    )
    stream_index = {name: index for index, name in enumerate(stream_names)}
    cached_index = {name: index for index, name in enumerate(cached_names)}

    tasks_by_stream: list[list[Task]] = [[] for _ in stream_names]
    neighbors: list[list[int]] = [[] for _ in stream_names]
    streams_by_cached: list[list[int]] = [[] for _ in cached_names]
    for task in graph.tasks:
        stream_name = task.d_block if stream_side == "D" else task.q_block
        cached_name = task.q_block if stream_side == "D" else task.d_block
        stream_id = stream_index[stream_name]
        cached_id = cached_index[cached_name]
        tasks_by_stream[stream_id].append(task)
        neighbors[stream_id].append(cached_id)
        streams_by_cached[cached_id].append(stream_id)

    for stream_id, tasks in enumerate(tasks_by_stream):
        if stream_side == "D":
            tasks.sort(key=lambda task: _block_order_key(task.q_block))
        else:
            tasks.sort(key=lambda task: _block_order_key(task.d_block))
        neighbors[stream_id].sort()
    for incident_streams in streams_by_cached:
        incident_streams.sort()

    stream_count = len(stream_names)
    if window_size is None:
        largest_stream_block = max(
            graph.blocks[name].size_bytes for name in stream_names
        )
        largest_cached_block = max(
            graph.blocks[name].size_bytes for name in cached_names
        )
        cached_capacity = max(0, device_capacity - largest_stream_block)
        cache_slots = cached_capacity // largest_cached_block
        average_out_degree = len(graph.tasks) / stream_count
        window_size = max(1, math.floor(cache_slots / average_out_degree))
    window_size = min(window_size, stream_count)

    degrees = [len(items) for items in neighbors]
    initial_order = sorted(
        range(stream_count),
        key=lambda stream_id: (-degrees[stream_id], _block_order_key(stream_names[stream_id])),
    )
    scheduled = [False] * stream_count
    scores = [0] * stream_count
    # Dict insertion order gives O(1), deterministic FIFO tie handling within
    # each positive score.  Algorithm 2 constrains only the maximum overlap;
    # it does not specify how equal-score candidates must be ordered.
    positive_score_members: dict[int, dict[int, None]] = {}
    maximum_score = 0
    zero_cursor = 0

    def add_to_score(score: int, stream_id: int) -> None:
        positive_score_members.setdefault(score, {})[stream_id] = None

    def remove_from_score(score: int, stream_id: int) -> None:
        members = positive_score_members[score]
        members.pop(stream_id, None)
        if not members:
            del positive_score_members[score]

    def adjust_scores(stream_id: int, delta: int) -> None:
        nonlocal maximum_score
        changes: dict[int, int] = defaultdict(int)
        for cached_id in neighbors[stream_id]:
            for candidate in streams_by_cached[cached_id]:
                if scheduled[candidate]:
                    continue
                changes[candidate] += delta

        # A candidate may share several neighbors with the entering/leaving
        # row.  DiskJoin's UnitHeap accumulates those increments lazily; batch
        # them here too so a high-degree row causes one score-bucket move per
        # affected candidate rather than one heap insertion per shared edge.
        for candidate, change in changes.items():
            old_score = scores[candidate]
            if old_score > 0:
                remove_from_score(old_score, candidate)
            new_score = old_score + change
            if new_score < 0:
                raise AssertionError("negative DiskJoin overlap score")
            scores[candidate] = new_score
            if new_score > 0:
                add_to_score(new_score, candidate)
                maximum_score = max(maximum_score, new_score)

    def choose_next() -> int:
        nonlocal maximum_score, zero_cursor
        while maximum_score > 0 and maximum_score not in positive_score_members:
            maximum_score -= 1
        if maximum_score > 0:
            members = positive_score_members[maximum_score]
            chosen = next(iter(members))
            del members[chosen]
            if not members:
                del positive_score_members[maximum_score]
            return chosen

        while scheduled[initial_order[zero_cursor]]:
            zero_cursor += 1
        return initial_order[zero_cursor]

    order: list[int] = []
    active_window: deque[int] = deque()
    while len(order) < stream_count:
        chosen = choose_next()
        scheduled[chosen] = True
        order.append(chosen)
        adjust_scores(chosen, +1)
        active_window.append(chosen)
        if len(active_window) > window_size:
            adjust_scores(active_window.popleft(), -1)

    schedule = tuple(
        task
        for stream_id in order
        for task in tasks_by_stream[stream_id]
    )
    validate_schedule(graph, schedule)
    return schedule


def _reverse_cuthill_mckee(
    nodes: Iterable[object],
    neighbors: Callable[[object], Iterable[object]],
    degree: Callable[[object], int],
    stable_key: Callable[[object], object],
) -> list[object]:
    """Return a deterministic RCM order, reversing each connected component."""

    remaining = set(nodes)
    # Degree is static for this graph.  Sorting potential component roots once
    # avoids an O(|V|^2) repeated ``min(remaining)`` scan on graphs containing
    # many disconnected components (common in extremely sparse matrices).
    root_candidates = sorted(remaining, key=lambda node: (degree(node), stable_key(node)))
    root_cursor = 0
    result: list[object] = []

    while remaining:
        while root_candidates[root_cursor] not in remaining:
            root_cursor += 1
        root = root_candidates[root_cursor]
        remaining.remove(root)
        queue = deque([root])
        component: list[object] = []

        while queue:
            node = queue.popleft()
            component.append(node)
            unseen_neighbors = [neighbor for neighbor in neighbors(node) if neighbor in remaining]
            unseen_neighbors.sort(key=lambda item: (degree(item), stable_key(item)))
            for neighbor in unseen_neighbors:
                # A neighbor can occur more than once in an implicit adjacency
                # iterator, so check again before enqueuing it.
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)

        result.extend(reversed(component))

    return result


def block_rcm_schedule(graph: AccessGraph) -> tuple[Task, ...]:
    """Run RCM on the block graph, then sweep unscheduled incident tasks."""

    adjacency: dict[str, set[str]] = {name: set() for name in graph.blocks}
    incidence: dict[str, list[int]] = defaultdict(list)
    for task_index, task in enumerate(graph.tasks):
        adjacency[task.d_block].add(task.q_block)
        adjacency[task.q_block].add(task.d_block)
        incidence[task.d_block].append(task_index)
        incidence[task.q_block].append(task_index)

    used_nodes = {name for task in graph.tasks for name in task.blocks}
    order = _reverse_cuthill_mckee(
        used_nodes,
        neighbors=lambda name: adjacency[str(name)],
        degree=lambda name: len(adjacency[str(name)]),
        stable_key=str,
    )
    position = {str(name): index for index, name in enumerate(order)}

    scheduled: set[int] = set()
    result: list[Task] = []
    for raw_name in order:
        name = str(raw_name)

        def incident_key(task_index: int) -> tuple[int, str, str]:
            task = graph.tasks[task_index]
            other = task.q_block if task.d_block == name else task.d_block
            return (position[other], task.d_block, task.q_block)

        for task_index in sorted(incidence[name], key=incident_key):
            if task_index not in scheduled:
                scheduled.add(task_index)
                result.append(graph.tasks[task_index])

    validate_schedule(graph, result)
    return tuple(result)


def task_rcm_schedule(graph: AccessGraph) -> tuple[Task, ...]:
    """Run RCM on the implicit line graph whose vertices are join tasks."""

    incidence: dict[str, list[int]] = defaultdict(list)
    for task_index, task in enumerate(graph.tasks):
        incidence[task.d_block].append(task_index)
        incidence[task.q_block].append(task_index)

    degrees = {
        task_index: len(incidence[task.d_block]) + len(incidence[task.q_block]) - 2
        for task_index, task in enumerate(graph.tasks)
    }

    def neighbors(raw_task_index: object) -> Iterable[int]:
        task_index = int(raw_task_index)
        task = graph.tasks[task_index]
        return itertools.chain(incidence[task.d_block], incidence[task.q_block])

    order = _reverse_cuthill_mckee(
        range(len(graph.tasks)),
        neighbors=neighbors,
        degree=lambda task_index: degrees[int(task_index)],
        stable_key=lambda task_index: graph.tasks[int(task_index)],
    )
    schedule = tuple(graph.tasks[int(task_index)] for task_index in order)
    validate_schedule(graph, schedule)
    return schedule


def simulate_schedule(
    graph: AccessGraph,
    schedule: Sequence[Task],
    schedule_name: str,
    device_capacity: int,
    host_capacity: int,
    policy: str,
    victim_admission: str,
) -> SimulationResult:
    simulator = TwoTierCacheSimulator(
        graph=graph,
        schedule=schedule,
        device_capacity=device_capacity,
        host_capacity=host_capacity,
        policy=policy,
        victim_admission=victim_admission,
    )
    return simulator.run(schedule_name)


def exhaustive_optimal_schedule(
    graph: AccessGraph,
    device_capacity: int,
    host_capacity: int,
    policy: str,
    victim_admission: str,
    objective: str,
    max_tasks: int,
) -> tuple[Task, ...]:
    """Find a tiny-graph oracle by evaluating every task permutation."""

    if len(graph.tasks) > max_tasks:
        raise ValueError(
            f"optimal scheduling is limited to {max_tasks} tasks, but the graph has "
            f"{len(graph.tasks)}"
        )

    best_schedule: tuple[Task, ...] | None = None
    best_score: tuple[int, int] | None = None
    for candidate in itertools.permutations(sorted(graph.tasks)):
        metrics = simulate_schedule(
            graph,
            candidate,
            "optimal-candidate",
            device_capacity,
            host_capacity,
            policy,
            victim_admission,
        )
        if objective == "operations":
            score = (metrics.total_io_operations, metrics.total_io_bytes)
        else:
            score = (metrics.total_io_bytes, metrics.total_io_operations)
        if best_score is None or score < best_score:
            best_score = score
            best_schedule = tuple(candidate)

    if best_schedule is None:
        raise AssertionError("the non-empty graph produced no task permutations")
    return best_schedule


def _parse_block_records(raw: object, side: str) -> list[Block]:
    if isinstance(raw, dict):
        records = [{"id": name, "size": size} for name, size in raw.items()]
    elif isinstance(raw, list):
        records = raw
    else:
        raise ValueError(f"{side.lower()}_blocks must be a list or object")

    blocks: list[Block] = []
    for record in records:
        if not isinstance(record, dict) or "id" not in record:
            raise ValueError(f"every {side} block must contain an id")
        size_value = record.get("size", record.get("size_bytes"))
        if size_value is None:
            raise ValueError(f"block {record['id']!r} is missing size")
        blocks.append(Block(str(record["id"]), side, parse_byte_size(size_value)))
    return blocks


def load_graph(path: Path) -> AccessGraph:
    with path.open("r", encoding="utf-8") as input_file:
        raw = json.load(input_file)
    if not isinstance(raw, dict):
        raise ValueError("input JSON must be an object")

    block_list = _parse_block_records(raw.get("d_blocks"), "D")
    block_list.extend(_parse_block_records(raw.get("q_blocks"), "Q"))
    blocks = {block.name: block for block in block_list}
    if len(blocks) != len(block_list):
        raise ValueError("block ids must be unique across D and Q")

    raw_edges = raw.get("edges")
    if not isinstance(raw_edges, list):
        raise ValueError("edges must be a list")
    tasks: list[Task] = []
    for edge in raw_edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"invalid edge {edge!r}; expected [D_block, Q_block]")
        tasks.append(Task(str(edge[0]), str(edge[1])))
    return AccessGraph(blocks=blocks, tasks=tuple(tasks))


def generate_synthetic_graph(
    d_blocks: int,
    q_blocks: int,
    d_block_size: int,
    q_block_size: int,
    edge_probability: float,
    seed: int,
) -> AccessGraph:
    if d_blocks <= 0 or q_blocks <= 0:
        raise ValueError("synthetic graph dimensions must be positive")
    if not 0.0 <= edge_probability <= 1.0:
        raise ValueError("edge probability must be between zero and one")

    d_names = [f"D{index}" for index in range(d_blocks)]
    q_names = [f"Q{index}" for index in range(q_blocks)]
    blocks = {
        name: Block(name, "D", d_block_size) for name in d_names
    } | {
        name: Block(name, "Q", q_block_size) for name in q_names
    }

    rng = random.Random(seed)
    edge_set = {
        (d_name, q_name)
        for d_name in d_names
        for q_name in q_names
        if rng.random() < edge_probability
    }

    # Avoid isolated synthetic blocks so compulsory-I/O comparisons use the
    # requested graph dimensions.
    for d_name in d_names:
        if not any(edge[0] == d_name for edge in edge_set):
            edge_set.add((d_name, rng.choice(q_names)))
    for q_name in q_names:
        if not any(edge[1] == q_name for edge in edge_set):
            edge_set.add((rng.choice(d_names), q_name))

    tasks = tuple(Task(d_name, q_name) for d_name, q_name in sorted(edge_set))
    return AccessGraph(blocks=blocks, tasks=tasks)


def _format_table(results: Sequence[SimulationResult]) -> str:
    headers = (
        "schedule",
        "I/Os",
        "I/O bytes",
        "avg I/O",
        "SSD reads",
        "SSD bytes",
        "H->D",
        "H->D bytes",
        "D->H",
        "D->H bytes",
    )
    rows = [
        (
            result.schedule,
            str(result.total_io_operations),
            format_bytes(result.total_io_bytes),
            format_bytes(round(result.average_io_bytes)),
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
    return "\n".join([render(headers), separator, *(render(row) for row in rows)])


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
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
        help="demote only blocks with future use, every evicted block, or no blocks",
    )
    parser.add_argument(
        "--schedulers",
        nargs="+",
        choices=(
            "row-major",
            "random",
            "diskjoin-mecc",
            "block-rcm",
            "task-rcm",
            "optimal",
        ),
        default=("row-major", "random", "diskjoin-mecc", "block-rcm", "task-rcm"),
    )
    parser.add_argument("--objective", choices=("bytes", "operations"), default="bytes")
    parser.add_argument("--optimal-max-tasks", type=int, default=9)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--show-schedules", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        if args.input:
            graph = load_graph(args.input)
        else:
            graph = generate_synthetic_graph(
                d_blocks=args.d_blocks,
                q_blocks=args.q_blocks,
                d_block_size=args.d_block_size,
                q_block_size=args.q_block_size,
                edge_probability=args.edge_probability,
                seed=args.seed,
            )

        schedules: list[tuple[str, tuple[Task, ...]]] = []
        for scheduler in args.schedulers:
            if scheduler == "row-major":
                schedule = row_major_schedule(graph)
            elif scheduler == "random":
                schedule = random_schedule(graph, args.seed)
            elif scheduler == "diskjoin-mecc":
                schedule = diskjoin_mecc_schedule(graph, args.device_capacity)
            elif scheduler == "block-rcm":
                schedule = block_rcm_schedule(graph)
            elif scheduler == "task-rcm":
                schedule = task_rcm_schedule(graph)
            elif scheduler == "optimal":
                schedule = exhaustive_optimal_schedule(
                    graph,
                    args.device_capacity,
                    args.host_capacity,
                    args.policy,
                    args.victim_admission,
                    args.objective,
                    args.optimal_max_tasks,
                )
            else:
                raise AssertionError(f"unhandled scheduler {scheduler!r}")
            schedules.append((scheduler, schedule))

        results = [
            simulate_schedule(
                graph,
                schedule,
                scheduler,
                args.device_capacity,
                args.host_capacity,
                args.policy,
                args.victim_admission,
            )
            for scheduler, schedule in schedules
        ]
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    if args.json:
        payload: dict[str, object] = {
            "graph": {
                "blocks": len(graph.blocks),
                "tasks": len(graph.tasks),
                "referenced_bytes": sum(block.size_bytes for block in graph.blocks.values()),
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
        print(json.dumps(payload, indent=2))
        return 0

    print(
        f"graph: {len(graph.blocks)} blocks, {len(graph.tasks)} tasks; "
        f"C_d={format_bytes(args.device_capacity)}, C_h={format_bytes(args.host_capacity)}; "
        f"policy={args.policy}, victim_admission={args.victim_admission}"
    )
    print(_format_table(results))
    if args.show_schedules:
        for name, schedule in schedules:
            print(f"\n{name}: " + " -> ".join(task.label() for task in schedule))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
