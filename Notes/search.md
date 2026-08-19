## What SimHash is

For unit vectors, a single random hyperplane through the origin separates `x` and `y` with probability proportional to the angle between them. Draw `r ~ N(0, I_d)` and set `h_r(x) = sign(⟨r, x⟩)`. Then

```
Pr[ h_r(x) ≠ h_r(y) ] = θ / π,      θ = angle(x, y)
```

The hyperplane separates them exactly when `r` falls in the wedge spanned by the two vectors — angular measure `2θ` out of `2π`.

Take `B` independent hyperplanes and the Hamming distance between the two sign vectors is `H ~ Binomial(B, θ/π)`, so `E[H] = B·θ/π` and `θ̂ = π·H/B` is an unbiased angle estimate. Because your data is exactly unit-norm, the join predicate is purely angular:

```
‖x−y‖² ≤ ε   ⟺   ⟨x,y⟩ ≥ 1 − ε/2   ⟺   θ ≤ θ_max = arccos(1 − ε/2)
```

so a Hamming threshold *is* a distance threshold. At your `θ² = 0.07`: `θ_max = 0.265 rad`, `θ/π = 0.0844`, `E[H] = 10.8` for B=128 — and I measured `H ≤ 14` gives 99 % recall.

**The critical property: this is an estimate, not a bound.** Unlike triangle-inequality pruning or prefix projection, no Hamming threshold below `B` guarantees zero false negatives — a close pair *can* produce a large `H`. Recall is a tunable probability, never a proof. That's the price for it working independently of intrinsic dimension.

## Pre-processing

**1. The projection matrix `R`** — `d × B` iid Gaussian, 96 × 128 = 48 KB. It is part of the index format: the same `R` must be used for every vector in both datasets, forever. Store the seed rather than the matrix. Fix the tie-break at `⟨r,x⟩ = 0` (measure zero, but make it deterministic so both sides agree).

Orthogonalising `R` via QR slightly reduces estimator variance for `B ≤ d`; at `B = 128 > 96` you can't fully orthogonalise and the gain is marginal. Skip it.

**2. Sketch computation** — this is just a GEMM followed by a sign and a bit-pack:

```
S = pack(sign(X · R))          (m × 96) × (96 × 128) → m × 128 bits
```

Cost is `2·m·96·128` FLOP — for the full 1B vectors that's 2.5e13 FLOP, **under a second of GPU time**. Utterly dominated by reading the 384 GB once.

**3. Storage — this is the part that changes the architecture.** 128 bits is **16 bytes per vector**, against 384 bytes for the fp32 vector. For 1B vectors:

| | size |
|---|---|
| raw vectors | 384 GB |
| **sketches** | **16 GB** |

16 GB fits comfortably in a Pro 6000's 96 GB and nearly in a 4090's 24 GB. **The entire dataset's sketches can be GPU-resident.** The I/O amplification that forced large blocks in the earlier analysis — 5.9 PB of y re-streaming — becomes 244 TB, or vanishes entirely if sketches stay resident. That frees you to pick block sizes at the compute optimum instead of by disk bandwidth.

Do this offline, once, writing a `.sketch` file parallel to the `.fbin`.

## The filter pass

Per pair: `H = popcll(SX[i][0] ^ SY[j][0]) + popcll(SX[i][1] ^ SY[j][1])`, emit bit if `H ≤ 14`.

Structurally this is **your existing `bitmask_gemm` with a different ring** — exactly the `L2FmaPolicy` / `L2SsdPolicy` parametrisation you already have. A `HammingPolicy` where the "multiply" is XOR and the "accumulate" is popcount-add, K = 2 words instead of 96 floats, and the epilogue compares against a constant. The mask output format, `bitmask_decode`, the CSR export — all unchanged.

Measured cost on your 4090: `POPC` is quarter-rate (4.41 Tops/s for 64-bit vs 35.87 for FFMA), so 128-bit SimHash is **5.9× cheaper** than a 96-dim distance. Not the 12× I claimed from instruction counts.

`mma.sync.aligned.m8n8k128.row.col.s32.b1.b1.s32.xor.popc` compiles on sm_89, and `m8n8k128` means one instruction covers 128 bits — exactly your sketch width. CUTLASS has b1 MMA atoms. That path uses tensor cores this workload leaves idle and could go well beyond 5.9×; it's the main unknown worth measuring.

## Post-processing

1. **Decode** the candidate bitmask — `bitmask_decode`, unchanged.
2. **Refine**: gather `x_i` and `y_j`, compute the exact fp32 distance, re-threshold. This is exact, so end-to-end recall equals filter recall.
3. **Emit** survivors through the existing sink.

Volume is the reason this works. At `θ²=0.07` the candidate rate is 2.24e-5, so a 32768² block pair yields ~24,000 candidates — 18 MB of gathers. The refine pass is irregular, but at that volume irregularity is irrelevant.

## Knobs and recall accounting

| bits | H thresh | recall | cand/true | filter cost |
|---|---|---|---|---|
| 64 | 10 | 99.4 % | 63.6× | 11.8× cheaper |
| **128** | **14** | **99.1 %** | **5.4×** | **5.9× cheaper** |
| 256 | 28 | 99.1 % | 3.6× | 3.0× cheaper |

More bits → tighter concentration → fewer candidates, but linearly more filter work. 128 is the knee at your selectivity. Raising `H_thresh` buys recall at the cost of candidates along a curve you can calibrate on a sample.

One methodological caution: I set the threshold **empirically** from the observed angle distribution, which gives *aggregate* recall over your data. The analytic alternative — the binomial tail at `θ_max` — gives a *per-pair* worst-case guarantee and would be more conservative (≈18 rather than 14 for B=128). Choose based on whether you need "99 % of pairs found" or "each pair found with probability 99 %".

## Two honest caveats

**This is a constant-factor win, not an asymptotic one.** SimHash still touches all `m·n` pairs; it just makes each ~6× cheaper. A genuine range query — sublinear, index-driven — would need to avoid touching most pairs, and at intrinsic dimension 10–21 (TwoNN 20.8, D₂ 10.2) index-based range search degrades toward linear scan anyway. You could bucket by bit-prefix for true LSH sublinearity, but bucketing is irregular and GPU-hostile; a cheap linear scan is the better shape for this hardware. 6× on a 55-day job is 46 days.

**It composes with, rather than replaces, your DiskJoin clustering.** A 1M × 1M cluster pair is 1e12 pairs and a 125 GB mask — it cannot run as one dense block, so your existing block machinery still operates *inside* each cluster pair. And at 1M-vector clusters the radii are essentially the global scale (median 100-NN distance is already 0.72 against a 1.9 mean), so TI pruning at that granularity should prune almost nothing. Clustering gives you locality and scheduling structure; SimHash is what actually reduces the work.

#

Both parts deserve grounding. Let me first check whether set-level pruning fails *everywhere*, or only in ≥2 dimensions — because a sorted 1-D interval is a very different object from a high-dimensional ball.

The 1-D result changes the picture, so let me correct what I said: **set-level pruning does work — just not with balls.**

## What set-level / IVF pruning means

Pair-level filtering makes each of the m·n distance computations cheaper. **Set-level pruning skips whole rectangles of the m×n grid** without looking at any pair inside them. Represent each set by a summary — centroid `c` and radius `ρ` — then bound the best possible pair across two sets:

```
⟨x,y⟩ ≤ ⟨c_A,c_B⟩ + ‖c_A‖ρ_B + ‖c_B‖ρ_A + ρ_A ρ_B
```

If that is below τ, no pair in A×B can match. In distance form this is your `TriangleInequalityPruner`: `d(c_A,c_B) − ρ_A − ρ_B > θ`. IVF is the index built on top — partition into lists by nearest centroid, and for a join, evaluate list-pairs and expand only survivors. The appeal is that it's the only mechanism that is *sub-quadratic in principle*.

## Why balls fail here

The bound fires only when `ρ_A + ρ_B < d(c_A,c_B) − θ`. Your measured geometry:

| quantity | value |
|---|---|
| typical inter-point distance | √1.863 = **1.365** |
| median 1-NN distance | √0.44 = 0.66 |
| median 100-NN distance | √0.72 = **0.85** |
| θ at selectivity 1e-5 | **0.318** |

A cluster of 100 points already has radius ≈0.85 — **62 % of the distance between two random points**. Two such clusters give `ρ_A + ρ_B ≈ 1.7`, against a required budget of `1.365 − 0.318 = 1.047`. The bound is negative before it starts. Measured: **0.0 % pruned at 64, 128 and 256 clusters, in 96-d and in 8-d and 16-d projections.**

Worse, centroids sit *inside* the sphere (‖μ‖ = 0.26), so `d(c_A,c_B)` is smaller than the inter-point distance, tightening the budget further.

The root cause is that going from 1 to 100 neighbours only grows the radius from 0.66 to 0.85 — a 29 % increase for 100× the points. Distances are so concentrated that "nearby" and "random" are nearly the same distance. To get `ρ < 0.5` you need clusters of ~2–4 points, and then each surviving cluster pair is a 4×4 GEMM — the granularity trap, where throughput collapses (we measured 18 TF/s at 2048×2048, versus 44 at 8192).

**And crucially, projecting to 8-d does not rescue it.** A bounding ball's radius is set by its worst point, and in ≥8 dimensions concentration puts every point near the shell, so the ball encloses vastly more volume than the cluster occupies. The looseness is intrinsic to balls, not to the ambient dimension.

## Why 1-D intervals *do* work

Sort by the top principal coordinate and a block becomes an **interval** — the tightest possible bound on a set's extent, with no wasted volume. The projection bound `|⟨u,x⟩ − ⟨u,y⟩| ≤ ‖x−y‖` then makes interval separation an exact necessary condition:

| blocks/side | pts/block | sel 1e-6 | 1e-5 | 1e-4 | 1e-3 |
|---|---|---|---|---|---|
| 16 | 2048 | 48.4 % | 32.0 % | 7.8 % | 0.8 % |
| 64 | 512 | 56.2 % | 38.4 % | 11.1 % | 2.6 % |
| **256** | 128 | **58.3 %** | **40.2 %** | 12.2 % | 3.1 % |

**58 % of block pairs proven empty at 1e-6, exactly, for free.** The top PC has std 0.260 and range 1.265, against θ = 0.208 — enough separation to matter. Finer blocking helps, so at production granularity (1907 blocks/side for 500M at 262144) expect ≥58 %.

So the correct statement isn't "set-level pruning doesn't work" — it's **"balls don't work; sorted intervals do."** I should have distinguished those.

---

# Pipeline A — projection bound

### Phase 0: offline, once per dataset

1. **Fit the basis.** Sample ~200k vectors, form the covariance, eigendecompose → `V` (96×96). Centring is irrelevant (measured identical); random bases are 28× worse, so this step is load-bearing.
2. **Choose k** from the measured table: 8 for ≤1e-5 selectivity, 16 at 1e-4, 24 at 1e-3.
3. **Project everything**: `Q = x·V[:,:k]` (k floats), `r = √(1 − ‖Q‖²)` (1 float, clamp at 0). Companion file at 36 bytes/vector for k=8 — **10× smaller than the vectors**.
4. **Sort the dataset by `Q[0]`**, the top principal coordinate. An external sort of 384 GB, done once; keep the permutation to map output indices back. This is what makes Phase 2 possible.

### Phase 1: blocking

5. Cut into x-blocks of ~262144 and y-blocks of ~16384–32768 (asymmetric: x_block alone divides y re-reads; y_block with x_block sets the mask at 536 MB–1 GB).
6. Record `[Q0_min, Q0_max]` per block — two floats.

### Phase 2: schedule

7. **Prune block pairs** whose intervals are separated by more than θ. Exact, ~58 % removed, cost is `n_blocks²` float comparisons.
8. Order survivors **x-row-major** so x stays resident while y streams.

### Phase 3: per surviving block pair, on GPU

9. Load `(Q, r)` for both blocks — 36 bytes/vector, not 384.
10. **Filter**: GEMM `Qx (Bx×k) × Qyᵀ (k×By)`, add the rank-1 term `r_x·r_y`, threshold at τ, emit bitmask.
11. **Scan + decode** → candidate list (existing `bitmask_decode`, unchanged).
12. **Refine**: gather the survivors' full 96-d vectors, compute exact `⟨x,y⟩`, threshold, emit.
13. Map indices through the sort permutation.

**Step 10 is a small change to your code.** The bound `⟨Qx,Qy⟩ + r_x·r_y ≥ τ` has exactly the shape `L2FmaPolicy` already implements — a GEMM plus a rank-1 correction from per-row scalars staged in shared memory. Substitute `r` for the norms, `+` for `−`, and K=8 for K=96. It's a new `Policy`, not a new kernel.

# Pipeline B — SimHash

Identical skeleton; three steps differ.

**Phase 0.1** — fix a seed, generate `R` (96×B Gaussian). Store the seed, not the matrix.
**Phase 0.3** — `s = pack(sign(x·R))`, 8 bytes/vector at B=64. **48× smaller than the vectors.**
**Phase 0.5** — *calibration*, which Pipeline A doesn't need: choose `H_max` for your recall target on a sample. At B=64, sel 1e-5, `H ≤ 11` gives 99 %.
**Phase 3.10** — filter is XOR+POPC accumulation over B/64 words against `H_max`.

You still sort by `Q[0]`, so Phase 2 needs the PCA basis anyway — SimHash doesn't remove that dependency.

## Combined economics

The two mechanisms compose multiplicatively, since a pruned block pair skips both filter and refine:

| | remaining work |
|---|---|
| brute force | 1.00 |
| + 1-D interval pruning (58 %) | 0.42 |
| + projection bound, k=8 (10.5×) | **0.040 → ~25×** |
| + SimHash instead (4.8×) | 0.088 → ~11× |

At 1e-6 selectivity on a 4090, that takes the 500M × 500M projection from **17.9 days to roughly 17 hours** — all exact, 100 % recall, no approximation anywhere.

Three caveats. The 58 % was measured at 256 blocks on a 32768 sample; re-measure at production granularity, where it should improve. The projection-filter kernel's achieved throughput is modelled from instruction counts, not measured — a K=8 GEMM has low arithmetic intensity and may land bandwidth-bound. And the external sort in Phase 0.4 is a real engineering cost that none of the compute models include.