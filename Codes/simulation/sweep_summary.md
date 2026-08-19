# Spiral vs. DiskJoin-MECC vs. Block-RCM Sweep Summary

## Executive summary

The sweep now contains 540 cache simulations: 180 matched workload/cache-policy triples for outside-in spiral, DiskJoin's MECC approximation, and block-RCM. It covers ten square matrix sizes from `24 x 24` through `100000 x 100000`, three sparse-density profiles, three row-degree skews, and both Belady-style and LRU caching.

DiskJoin-MECC is the strongest scheduler for the current byte-weighted, asymmetric-block workload:

- versus spiral: 56.2% fewer aggregate total bytes and 11.1% fewer total I/O operations;
- versus block-RCM: 48.4% fewer aggregate total bytes and 5.3% fewer total I/O operations;
- strict best among all three in 142/180 cases for total bytes and 131/180 for total operations;
- no total-byte loss to spiral, and only 15/180 total-byte losses to block-RCM.

The important qualification is the metric boundary. MECC uses 28.8% fewer aggregate SSD-read bytes than RCM but issues 6.8% more SSD-read operations. In the largest dense/high-skew Belady case, RCM reads less from SSD (17.13 TiB versus MECC's 26.31 TiB), yet moves far more data across all tiers (76.51 TiB versus 26.99 TiB). The two-tier hierarchy therefore changes what “minimum I/O” means.

## What was implemented

MECC itself is NP-hard. The implemented `diskjoin-mecc` scheduler is DiskJoin's published approximation, adapted from Algorithm 2 and the reference `tmp/DiskJoin/lib/Gorder.h` implementation:

1. choose the larger relation as the streaming side;
2. choose its maximum-degree active block as the first block;
3. greedily choose the next streaming block with maximum cached-neighbor overlap across the previous `w` blocks;
4. emit all comparison tasks of each streaming block consecutively;
5. execute the resulting fixed trace with the same cache policy as every other scheduler.

For this cross-join, D is always the larger relation because D and Q have the same block count but D blocks are 64 MiB versus 16 MiB for Q. The implementation therefore streams D and reuses Q. After reserving one largest D block in the 256 MiB device cache, 12 Q blocks fit, and the paper's window rule becomes:

```text
w = max(1, floor(12 / average active D-row degree))
```

DiskJoin assumes equal-size buckets and one cache. Reserving the streaming D block before converting bytes to Q slots is the explicit adaptation to this simulator's unequal blocks and device cache. RAM remains the same exclusive victim cache for every scheduler; it is not folded into `w` because tasks can execute only when both operands are in VRAM.

## Experimental setup

| Dimension | Values |
|---|---|
| Matrix sizes | 24, 61, 153, 386, 975, 2,462, 6,214, 15,689, 39,610, 100,000 |
| Average surviving pairs per D row | 1, 4, 16 |
| Row-degree Zipf alpha | 0.0 (uniform), 0.8 (moderate), 1.4 (high) |
| D / Q block size | 64 MiB / 16 MiB |
| Device cache `C_d` | 256 MiB |
| Host victim cache `C_h` | 512 MiB |
| Cache policies | Belady-style, LRU |
| Victim admission | Only blocks with a future use |
| Schedulers | Outside-in spiral, DiskJoin-MECC, block-RCM |
| Repetitions | One deterministic seed per configuration |

Density is average nonzeros per row. An `n x n` matrix with average degree `k` has realized density `k/n`, so the largest graphs contain 100,000, 400,000, or 1,600,000 tasks without materializing ten billion cells.

Zipf ranks are randomly assigned to physical D rows, preventing hot rows from being systematically placed on the spiral boundary. Q popularity remains approximately uniform. One logical I/O is one whole-block transfer; total I/O includes SSD-to-device, host-to-device, and device-to-host transfers.

## Overall pairwise results

Ratios below 1 favor MECC. Wins/ties/losses are from MECC's perspective over 180 matched cases.

| Baseline | Metric | Aggregate ratio | Change | MECC wins / ties / losses |
|---|---|---:|---:|---:|
| Spiral | Total bytes | 0.438 | 56.2% fewer | 176 / 4 / 0 |
| Spiral | Total operations | 0.889 | 11.1% fewer | 173 / 4 / 3 |
| Spiral | SSD-read bytes | 0.522 | 47.8% fewer | 163 / 17 / 0 |
| Spiral | SSD-read operations | 0.936 | 6.4% fewer | 132 / 17 / 31 |
| Block-RCM | Total bytes | 0.516 | 48.4% fewer | 142 / 23 / 15 |
| Block-RCM | Total operations | 0.947 | 5.3% fewer | 132 / 24 / 24 |
| Block-RCM | SSD-read bytes | 0.712 | 28.8% fewer | 116 / 36 / 28 |
| Block-RCM | SSD-read operations | 1.068 | 6.8% more | 94 / 36 / 50 |

The median per-case MECC ratios are 0.476 bytes and 0.831 operations versus spiral, and 0.620 bytes and 0.947 operations versus RCM. Thus, the conclusion is not solely caused by weighting the largest traces, although aggregate byte savings are larger because dense large graphs especially favor D-row grouping.

## Interaction with cache policy

These are aggregate MECC/baseline ratios within each policy.

| Policy | Bytes vs. spiral | Operations vs. spiral | Bytes vs. RCM | Operations vs. RCM |
|---|---:|---:|---:|---:|
| Belady-style | 0.434 | 0.833 | 0.519 | 0.912 |
| LRU | 0.441 | 0.925 | 0.515 | 0.968 |

MECC remains the aggregate byte winner under both policies. Its operation-count advantage is much more dependent on future-aware eviction: relative to its own Belady runs, LRU raises MECC's per-workload I/O count by 50.8% on average. This is consistent with DiskJoin's design, which composes Gorder with Belady rather than treating the eviction policy as incidental.

Belady here means farthest-next-use eviction. It is optimal for one cache of equal-size objects, but remains a heuristic for unequal blocks and two coupled exclusive tiers.

## Effect of density

The following are macro-averages of matched per-case ratios. The last columns count strict MECC wins over RCM out of 60 cases.

| Average D-row degree | Bytes vs. spiral | Ops vs. spiral | Bytes vs. RCM | Ops vs. RCM | Byte wins vs. RCM | Op wins vs. RCM |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.743 | 0.819 | 0.877 | 0.969 | 36 / 60 | 33 / 60 |
| 4 | 0.483 | 0.788 | 0.709 | 0.943 | 46 / 60 | 45 / 60 |
| 16 | 0.400 | 0.879 | 0.447 | 0.927 | 60 / 60 | 54 / 60 |

MECC's byte advantage grows with degree. Grouping all tasks for a 64 MiB D block gives that block one contiguous lifetime, while RCM may preserve more 16 MiB Q locality at the cost of repeatedly moving D blocks. At degree 16, MECC beats RCM on bytes in every case.

## Effect of row skew

These macro-averages compare MECC with RCM.

| Skew | Byte ratio | Operation ratio | Byte W/T/L | Operation W/T/L |
|---|---:|---:|---:|---:|
| Uniform | 0.648 | 0.914 | 40 / 20 / 0 | 36 / 20 / 4 |
| Moderate Zipf (`alpha=0.8`) | 0.644 | 0.919 | 58 / 2 / 0 | 57 / 2 / 1 |
| High Zipf (`alpha=1.4`) | 0.742 | 1.005 | 44 / 1 / 15 | 39 / 2 / 19 |

High row skew weakens MECC's operation-count result: the macro-average is 0.5% worse than RCM and MECC loses 19/60 cases. Byte savings remain strong because the streamed object is the larger operand, but a few hot D rows generate long Q scans whose cache behavior is sensitive to eviction.

## Largest-matrix detail

The following uses Belady-style caching at `100000 x 100000`. Changes compare MECC with RCM; negative values favor MECC.

| Degree | Skew | Tasks | MECC TiB | RCM TiB | Total-byte change | Total-op change | SSD-byte change |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Uniform | 100,000 | 7.07 | 7.07 | 0.0% | 0.0% | 0.0% |
| 1 | Moderate | 100,000 | 4.24 | 5.07 | -16.2% | -10.5% | -13.8% |
| 1 | High | 100,000 | 1.83 | 2.57 | -28.9% | -3.9% | -10.8% |
| 4 | Uniform | 400,000 | 11.02 | 20.76 | -46.9% | -19.5% | -46.2% |
| 4 | Moderate | 400,000 | 11.38 | 18.57 | -38.7% | -12.7% | -31.6% |
| 4 | High | 400,000 | 6.93 | 6.96 | -0.6% | -0.6% | -0.4% |
| 16 | Uniform | 1,600,000 | 30.63 | 57.15 | -46.4% | -2.3% | -46.6% |
| 16 | Moderate | 1,600,000 | 30.63 | 46.90 | -34.7% | -5.2% | -19.7% |
| 16 | High | 1,600,000 | 26.99 | 76.51 | -64.7% | -17.7% | +53.6% |

The degree-16/high-skew case exposes the hierarchy tradeoff most clearly. RCM lowers SSD reads by retaining/reusing blocks through the 512 MiB victim tier, but incurs enough host/device movement to make total traffic 2.84x MECC's. A scheduler optimized only for SSD cache misses would select RCM; a scheduler charging every DMA byte would select MECC.

## Interpretation

MECC wins the byte objective primarily because it gives each large D block a single contiguous task group. Once that group finishes, the D block has no future use and can be dropped instead of demoted. Gorder then tries to arrange neighboring D groups so their Q sets overlap within the device-cache window.

This result strengthens the case for a weighted multi-tier scheduler, but it does not establish Gorder itself as the sole cause. DiskJoin-MECC combines D-row grouping and graph reordering, while the sweep has no “stream D in original order” ablation. That baseline is needed to separate the value of grouping from the additional value of neighbor-overlap ordering.

The disagreement between SSD operations, SSD bytes, and total bytes also shows that MECC's original equal-bucket/single-cache objective is incomplete for SSD–RAM–VRAM execution. The next scheduler should assign different costs to D and Q blocks and to SSD reads, host promotions, and demotions instead of minimizing an unweighted cache-miss count.

## Limitations and next experiments

- This is the MECC scheduling/cache component, not DiskJoin's full bucketization, pruning, CPU distance execution, or end-to-end runtime.
- DiskJoin's equal-size, single-cache window rule is adapted to unequal blocks and VRAM; this adaptation should be called out in any paper comparison.
- Add a streamed D-row-major/no-Gorder ablation to isolate graph reordering.
- Add banded, clustered, and centroid-derived sparsity; current matrix coordinates carry no useful locality for spiral.
- Add Q-side skew and correlated D/Q hotspots; current Q popularity is approximately uniform.
- Vary D:Q block ratios and both cache capacities, including cases where Q is the larger relation.
- Repeat configurations across seeds and report confidence intervals.
- Add request latency, coalescing, prefetch overlap, computation, and output traffic before making end-to-end claims.
- Scheduling-time fields are not compared because prior RCM records span a scalability-fix checkpoint, although the schedule and I/O metrics remain valid.

## Reproduction

```bash
python3 Codes/simulation/test_schedule.py
python3 Codes/simulation/benchmark_sweep.py --dry-run
python3 Codes/simulation/benchmark_sweep.py --overwrite
```

Artifacts:

- [`sweep_config.json`](sweep_config.json)
- [`sweep_results.jsonl`](sweep_results.jsonl)
- [`benchmark_sweep.py`](benchmark_sweep.py)
- [`compare_spiral.py`](compare_spiral.py)
- [`schedule.py`](schedule.py)
- [`test_schedule.py`](test_schedule.py)
