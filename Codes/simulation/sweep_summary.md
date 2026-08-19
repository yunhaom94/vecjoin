# Equal-Block D-Grouped Scheduler Sweep Summary

## Executive summary

The corrected sweep contains 540 cache simulations: 180 matched workload/cache-policy triples for D-grouped row-major, DiskJoin's MECC approximation, and D-grouped block-RCM. It covers ten square matrix sizes from `24 x 24` through `100000 x 100000`, three sparse-density profiles, three D-row-degree skews, and both Belady-style and LRU caching.

The experiment now isolates group ordering:

- every D and Q block is 64 MiB;
- every scheduler emits all tasks for each D block contiguously;
- row-major, MECC, and RCM differ only in D-group order and within-group Q order;
- every fixed trace runs through the same two-tier cache simulator and policy.

The previous large MECC advantage disappears under this controlled comparison. Across all cases, MECC uses only 0.25% fewer aggregate total transfers than grouped RCM (`0.9975x`), with a median per-case ratio of `0.9990x`. MECC wins/ties/loses 108/30/42 matched cases against RCM. The two graph orderings are therefore competitive rather than categorically different.

Both graph orderings improve on grouped row-major: MECC uses 2.66% fewer aggregate total transfers and RCM uses 2.42% fewer. MECC is the unique total-transfer winner in 108/180 cases, RCM in 40, and row-major in 2; 30 cases have a tied best result.

Because all blocks have equal size, total-byte and total-operation ratios are identical. The results no longer depend on weighting D transfers four times more heavily than Q transfers.

## What was implemented

### D-grouped row-major

Order active D blocks and their incident Q blocks by natural numeric block ID, then emit every task for one D block before advancing to the next D block.

### DiskJoin-MECC approximation

The implemented scheduler follows DiskJoin's Gorder-style approximation:

1. choose the streaming side; equal-size square relations tie-break to D;
2. choose the maximum-degree active D block first;
3. greedily choose the next D block with maximum Q-neighbor overlap across the previous `w` D groups;
4. emit every task for each selected D block contiguously;
5. order Q tasks within a D group by natural numeric ID.

After reserving one 64 MiB D block in the 256 MiB device cache, three 64 MiB Q blocks fit. The adapted window rule is:

```text
w = max(1, floor(3 / average active D-row degree))
```

The window is therefore three at degree 1 and one at degrees 4 and 16.

### D-grouped block-RCM

RCM itself produces a block-vertex order, not an edge order. The corrected trace construction is:

1. run deterministic RCM on the undirected bipartite D-Q access graph;
2. filter the full RCM vertex order to obtain the D-group order;
3. for each D block, emit all incident tasks contiguously;
4. order those tasks by each Q endpoint's position in the full RCM order.

This gives RCM the same D-grouping policy as MECC. The implementation also supports Q grouping explicitly, although the primary sweep fixes D grouping for every scheduler.

## Experimental setup

| Dimension | Values |
|---|---|
| Matrix sizes | 24, 61, 153, 386, 975, 2,462, 6,214, 15,689, 39,610, 100,000 |
| Average surviving pairs per D row | 1, 4, 16 |
| D-row-degree Zipf alpha | 0.0 (uniform), 0.8 (moderate), 1.4 (high) |
| D / Q block size | 64 MiB / 64 MiB |
| Device cache `C_d` | 256 MiB (four blocks) |
| Host victim cache `C_h` | 512 MiB (eight blocks) |
| Cache policies | Belady-style, LRU |
| Victim admission | Only blocks with a future use |
| Schedulers | D-grouped row-major, DiskJoin-MECC, D-grouped block-RCM |
| Repetitions | One deterministic seed per configuration |

Density is average nonzeros per D row. An `n x n` matrix with average degree `k` has realized density `k/n`, so the largest graphs contain 100,000, 400,000, or 1,600,000 tasks without materializing ten billion cells.

Zipf ranks are randomly assigned to physical D rows. Q popularity remains approximately uniform. One logical I/O is one whole-block transfer; total I/O includes SSD-to-device, host-to-device, and device-to-host transfers.

## Overall pairwise results

Ratios below 1 favor the numerator. Win/tie/loss counts are over 180 matched cases.

| Comparison | Metric | Aggregate ratio | Change | Numerator W/T/L |
|---|---|---:|---:|---:|
| MECC / row-major | Total transfers or bytes | 0.9734 | 2.66% fewer | 165 / 7 / 8 |
| RCM / row-major | Total transfers or bytes | 0.9758 | 2.42% fewer | 159 / 12 / 9 |
| MECC / RCM | Total transfers or bytes | 0.9975 | 0.25% fewer | 108 / 30 / 42 |
| MECC / RCM | SSD-read transfers or bytes | 0.9819 | 1.81% fewer | 134 / 30 / 16 |

MECC's SSD-read advantage shrinks at the total-traffic boundary. Across the sweep, MECC avoids 395,701 SSD reads relative to RCM but performs 316,555 additional host promotions and demotions, leaving a net advantage of only 79,146 total transfers.

The median per-case MECC ratios are `0.9623x` versus row-major and `0.9990x` versus RCM. The aggregate result is not hiding a consistent large RCM loss.

## Interaction with cache policy

These are aggregate total-transfer ratios within each policy.

| Policy | MECC / row-major | RCM / row-major | MECC / RCM | MECC vs. RCM W/T/L |
|---|---:|---:|---:|---:|
| Belady-style | 0.9598 | 0.9600 | 0.9998 | 50 / 11 / 29 |
| LRU | 0.9812 | 0.9849 | 0.9962 | 58 / 19 / 13 |

Under Belady-style eviction, MECC and RCM differ by only 0.02% in aggregate traffic. Under LRU, MECC is ahead by 0.38%. Belady here is farthest-next-use eviction; with equal-size objects it is optimal for one cache, but the simulator still has two coupled exclusive tiers.

## Effect of density

The following compares MECC with grouped RCM within each density stratum.

| Average D-row degree | Aggregate ratio | Change | MECC W/T/L |
|---:|---:|---:|---:|
| 1 | 0.9969 | 0.31% fewer | 23 / 22 / 15 |
| 4 | 0.9731 | 2.69% fewer | 55 / 1 / 4 |
| 16 | 1.0036 | 0.36% more | 30 / 7 / 23 |

MECC is strongest relative to RCM at degree 4. At degree 16, reserving one D block leaves only three Q slots and the Gorder window collapses to one; grouped RCM is slightly better in aggregate. Under LRU, many degree-16 cases approach two transfers per task regardless of group ordering because the small cache cannot retain useful Q neighborhoods.

## Effect of D-row skew

| Skew | Aggregate MECC/RCM ratio | Change | MECC W/T/L |
|---|---:|---:|---:|
| Uniform | 0.9974 | 0.26% fewer | 26 / 25 / 9 |
| Moderate Zipf (`alpha=0.8`) | 0.9966 | 0.34% fewer | 34 / 4 / 22 |
| High Zipf (`alpha=1.4`) | 0.9986 | 0.14% fewer | 48 / 1 / 11 |

The aggregate MECC-RCM difference stays below 0.4% for every skew stratum. High skew gives MECC more individual wins, but those wins are generally small.

## Largest-matrix detail

The following uses Belady-style caching at `100000 x 100000`. Traffic is total movement across all tiers. Negative changes favor MECC.

| Degree | Skew | Tasks | Row-major TiB | MECC TiB | RCM TiB | MECC vs. RCM | MECC vs. row-major |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Uniform | 100,000 | 12.40 | 9.97 | 9.97 | 0.00% | -19.60% |
| 1 | Moderate | 100,000 | 9.26 | 8.35 | 8.48 | -1.54% | -9.89% |
| 1 | High | 100,000 | 6.46 | 6.41 | 6.43 | -0.27% | -0.75% |
| 4 | Uniform | 400,000 | 31.44 | 25.68 | 28.13 | -8.71% | -18.32% |
| 4 | Moderate | 400,000 | 31.39 | 27.82 | 28.91 | -3.76% | -11.39% |
| 4 | High | 400,000 | 25.42 | 25.27 | 25.38 | -0.45% | -0.59% |
| 16 | Uniform | 1,600,000 | 107.69 | 105.06 | 103.34 | +1.67% | -2.44% |
| 16 | Moderate | 1,600,000 | 107.18 | 104.02 | 103.74 | +0.27% | -2.95% |
| 16 | High | 1,600,000 | 100.94 | 100.32 | 100.52 | -0.19% | -0.61% |

The largest cases show that no scheduler dominates. MECC has a meaningful advantage for degree-4 uniform and moderate graphs, while RCM wins the degree-16 uniform and moderate cases. High-skew cases make all three D-group orders similar.

## Interpretation

The corrected experiment supports three narrower conclusions:

1. D grouping is an execution-policy choice, not a unique MECC advantage. Giving RCM the same grouping removes the previous multi-fold traffic gap.
2. Graph-aware D-group ordering helps over original row order, especially at degrees 1 and 4, but the gain depends strongly on cache policy and graph structure.
3. MECC/Gorder and grouped RCM optimize different locality surrogates and are nearly tied overall. The strongest direction is therefore a cache- and tier-aware scheduler evaluated against both, not a claim that one of these two heuristics categorically dominates the other.

Scheduling overhead also differs. On the largest degree-16 uniform graph, row-major scheduling takes 2.35 seconds, grouped RCM 3.79 seconds, and MECC 8.25 seconds. These are trace-construction times only and are not included in the transfer metric.

## Limitations and next experiments

- This is trace-level scheduling and cache simulation, not DiskJoin's full bucketization or an end-to-end GPU runtime.
- The primary sweep intentionally fixes equal-size blocks. Test asymmetric sizes later only as a separately justified sensitivity study, for example when D carries an index artifact.
- Device capacity is only four blocks. Sweep cache capacities in block units to test whether the degree-16 convergence is a capacity artifact.
- The primary comparison fixes D grouping. Run the supported Q-grouped RCM variant and transpose D/Q skew to test side choice.
- Add Q-side skew, correlated D/Q hotspots, banded graphs, clustered graphs, and centroid-derived pruning patterns; current Q popularity is approximately uniform.
- Repeat configurations across seeds and report confidence intervals.
- Add latency, transfer overlap, compute, output traffic, and scheduling time before making end-to-end runtime claims.
- Compare with a small-trace optimum or lower bound to measure how much opportunity remains beyond both heuristics.

## Reproduction

```bash
python3 Codes/simulation/test_schedule.py
python3 Codes/simulation/benchmark_sweep.py --dry-run
python3 Codes/simulation/benchmark_sweep.py --overwrite
python3 Codes/simulation/summarize_sweep_csv.py
```

Artifacts:

- [`sweep_config.json`](sweep_config.json)
- [`sweep_results.jsonl`](sweep_results.jsonl)
- [`sweep_summary.csv`](sweep_summary.csv)
- [`benchmark_sweep.py`](benchmark_sweep.py)
- [`summarize_sweep_csv.py`](summarize_sweep_csv.py)
- [`compare_spiral.py`](compare_spiral.py)
- [`schedule.py`](schedule.py)
- [`test_schedule.py`](test_schedule.py)
