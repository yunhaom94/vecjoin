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

#

Panorama looks like the closest modern analogue to the projection bound. Let me read it and the third paper.

Panorama's bound *is* the projection bound — with an orthogonal transform, the "discarded suffix" is exactly the orthogonal complement. Let me trace the lineage further.

This EDBT 2026 survey is directly on point. Let me fill in the join-side and GPU-side literature.

Your premise doesn't survive the search: **both methods are extensively published and well received.** What's absent is the specific combination you built. Here's the map.

## The projection bound has at least four independent published lineages

**1. All-pairs similarity search (2007–2016).** [L2AP](http://davidanastasiu.net/pdf/papers/2014-AnastasiuK-ICDE-l2ap.pdf) (Anastasiu & Karypis, ICDE 2014) proposes "ℓ2-norm bounds… leveraging the Cauchy-Schwarz inequality" to bound the dot product of the *unindexed suffix*. That is your bound with P = coordinate-prefix projection. It has parallel (PL2AP) and kNN-graph (L2Knng) descendants.

**2. Vertical decomposition / partial distance (2002–2025).** BOND, [PCA-based branch-and-bound](https://www.sciencedirect.com/science/article/abs/pii/S0167865502003847), Progressive Partial Distance, and [PDX/PDX-BOND](https://arxiv.org/pdf/2503.04422) (PACMMOD 2025).

**3. Distance-Comparison-Operation optimization for ANN (2023–2026).** ADSampling, FINGER, DADE (= ADSampling with PCA instead of random projection), DDC_res/DDC_pca, RaBitQ.

**4. [Panorama](https://arxiv.org/html/2510.00566) (2025) — essentially your exact formulation.** Orthogonal transform, then Cauchy-Schwarz on the tail:

`LB = R(q) + R(x) − 2(p^(0,ℓ) + √(R_tail(q)·R_tail(x)))`

For unit vectors that reduces to ⟨x,y⟩ ≤ ⟨Px,Py⟩ + ρ_xρ_y — your bound, character for character. (The summarizer called it "Cauchy-Schwarz on the suffix, not a projection bound"; with an orthogonal transform those are the same object.) It reports 3.2–18.7× on IVFFlat, 28.9× on IVFPQ, and adds a relaxation knob ε∈[0,1] you don't have.

**SimHash** is Charikar (STOC 2002) and Manku et al. (WWW 2007), deployed at Google for web-scale near-duplicate detection. Thousands of citations. It's canonical, not neglected.

## So why doesn't your configuration appear?

**The community optimizes a different query.** The [EDBT 2026 DCO survey](https://openproceedings.org/2026/conf/edbt/paper-270.pdf) (Wang et al., ECNU) benchmarks 12 of these methods and lands on a blunt finding: *"SIMDized HNSW outperforms advanced DCO optimizations… the superiority of DCO optimizations relative to FDScanning diminishes when confronted with the powerful parallel computing capabilities of modern CPUs."* Once a graph index has cut candidates to a few hundred, saving dimensions on each doesn't pay.

**On CPUs the bound fights the hardware.** Same survey: projection pruning *"relies on vector projection and threshold comparisons, operations that are not fully amenable to SIMD parallelization,"* and *"hypothesis testing in projection sampling disrupts branch-free linear data flow, resulting in a significant increase in branch prediction errors."* DDC_res showed a **6.8× increase in branch mispredictions** on OpenAI embeddings. That is precisely the objection your implementation sidesteps — `__ballot_sync` turns the predicate into a branch-free vote, and the ballot kernel has *one* barrier and no divergent control flow in the FMA stream (which is exactly why decoupling the emission logic bought 10 %).

**And the survey says your regime is the one where it *does* pay.** On IVF — which exhaustively scans candidates — *"all DCO optimizations show substantial acceleration across all datasets… DCO optimization is more important when DCOs become the bottleneck."* They measure DCOs at 77.2 % of HNSW time and 85 % of IVF time. An ε-join is IVF's exhaustive scan taken to the limit: no index, every pair examined, filter is 95 % of the cost. You are on the far end of the axis where the survey says the technique wins, and nobody benchmarked there.

**The dense/sparse split stranded it.** AllPairs and L2AP built the bound for *sparse* vectors, where an inverted index makes candidate generation cheap. For dense embeddings the inverted index is useless, so the whole APSS apparatus doesn't transfer — and the bound was left behind with the apparatus rather than being reconsidered on its own.

**The GPU join literature went elsewhere.** [Gowanlock et al.](https://arxiv.org/abs/1809.09930) use grid-based indices, which collapse above ~6 dimensions. The tensor-core line (TED-Join; [mixed-precision ICPP 2025](https://arxiv.org/pdf/2508.21230), 2.5–51× at 128–960 D) makes the brute force *faster* rather than pruning it. Nobody combined "exact projection bound" with "GPU dense join." The EDBT survey explicitly excludes GPU/FPGA work as *"not directly comparable… specific to hardware platforms that differ substantially from modern CPUs."*

**Joins themselves went approximate.** All three papers you linked are approximate: [Fast Approximate Similarity Join in Vector Databases](https://dl.acm.org/doi/10.1145/3725403) (Xie, Yu, Liu, SIGMOD 2025 — I could only recover metadata, the PDF wouldn't parse); [Work Sharing and Offloading for Approximate Threshold-based Vector Join](https://arxiv.org/html/2603.16360v1) (Kim et al., EPFL, PVLDB — NSG-based, up to 32.6× from a merged index); [DiskJoin](https://arxiv.org/abs/2508.18494) (SIGMOD 2026 — SSD-resident, "probabilistic pruning," no recall guarantee; the abstract doesn't say what the pruning is). An *exact* ε-join is out of fashion, so an exact bound has no natural home.

## Honest assessment of what you have

**The bound is not novel.** Panorama has it in your exact form; L2AP has the coordinate-projection special case; the unit-norm simplification is folklore. If you write this up, the bound is related work, not contribution.

**What isn't in the literature, as far as I can find:**
- The negative result that on Deep, set-level/IVF-style ball pruning prunes **0.0 %** at 96-d, 16-d and 8-d alike, while the identical bound applied per-pair prunes 99.98 % — the failure is bounding balls, not dimension.
- The GPU finding that a K=8 mainloop is epilogue-bound, that CUTLASS's pipeline is the wrong structure there, and that a register-resident ballot kernel beats it by 1.5× at 14.4 T FMA/s — with the crossover back to the GEMM at k≈20.
- The output-format result: a dense bitmask puts a σ-independent floor under refinement (15 s on Deep10M), and switching to a compact survivor list moves the optimal k from 8 to 12 and the end-to-end from 7.0× to 12.7×.

That's a systems contribution in a gap, not a new bound — DaMoN/EDBT/ICPP territory rather than SIGMOD.

**Two caveats before believing your own numbers.** Everything is one dataset (Deep10M, 96-d, exactly unit-norm, ε tuned to ~1e-6 selectivity). Panorama's speedups *grow* with dimension because PCA energy concentrates more; yours might not, since your filter cost grows with k and your own sweep showed CUTLASS overtaking the ballot kernel around k=20. And your baseline is your own brute-force GEMM, not a tuned competitor — the honest comparison is against TED-Join or the mixed-precision tensor-core join, which attack the same problem by making the brute force fast instead of avoiding it.

**Sources:** [L2AP (ICDE 2014)](http://davidanastasiu.net/pdf/papers/2014-AnastasiuK-ICDE-l2ap.pdf) · [Panorama](https://arxiv.org/html/2510.00566) · [EDBT 2026 DCO survey](https://openproceedings.org/2026/conf/edbt/paper-270.pdf) · [PDX (PACMMOD 2025)](https://arxiv.org/pdf/2503.04422) · [Fast Approximate Similarity Join (SIGMOD 2025)](https://dl.acm.org/doi/10.1145/3725403) · [Work Sharing for Vector Join](https://arxiv.org/html/2603.16360v1) · [DiskJoin](https://arxiv.org/abs/2508.18494) · [GPU self-join](https://arxiv.org/abs/1809.09930) · [Tensor-core Euclidean distance](https://arxiv.org/pdf/2508.21230) · [DR survey for ANN](https://arxiv.org/html/2403.13491v2) · [Data-aware DCO](https://arxiv.org/pdf/2411.17229) · [Elastic HNSW vs LSH](https://www.elastic.co/blog/understanding-approximate-nearest-neighbor-search)

#

Let me re-derive this with measurements rather than from memory, since the reframing depends on the exact mechanism.

Two things jump out. Balls prune 0.00 % even for k-means at exactly DiskJoin's 0.1 % cluster size — and the box prune is **identical for k=1 through k=32**. That second fact is the key to the reframing, so let me test it.

A 2-D k-d tree already beats the 1-D sort (64.95 % vs 56.94 %), and crucially the gap *widens* with more blocks. Let me find where it peaks.

1-D sorting saturates at 58.8 % no matter how fine the blocks; the k-d tree keeps improving to 85.5 %. Let me establish the asymptotic ceiling and verify exactness empirically.

Here's the full mechanism, measured, plus a reframing that I think does work as a positive result.

## Why balls fail

The ball prune fires only when `‖cᵢ−cⱼ‖ − rᵢ − rⱼ > √ε = 0.2095`. Measuring all three terms on Deep10M:

| partition | mean r | max ‖cᵢ−cⱼ‖ | mean margin | **best** margin | pruned |
|---|---|---|---|---|---|
| PC1 blocks, 96-d ball | 1.061 | 1.145 | −1.733 | −0.771 | 0.00 % |
| PC1 blocks, 8-d proj ball | 0.823 | 1.116 | −1.274 | −0.174 | 0.00 % |
| PC1 blocks, 16-d proj ball | 0.887 | 1.127 | −1.394 | −0.313 | 0.00 % |
| k-means K=1024 (0.098 % of n) | 0.961 | 1.397 | −0.989 | −0.282 | 0.00 % |

Mean pairwise distance is 1.359 with **std/mean = 0.086**. The margin isn't marginally negative — the single most-separated pair out of 524k k-means cluster pairs still falls **0.49 short** of the threshold.

The arithmetic is forced. All points lie on the unit sphere, so centroids sit inside the unit ball and `‖cᵢ−cⱼ‖ ≤ 2` with an observed max of 1.40. Meanwhile a cluster of 9,765 points has radius 0.96 — **71 % of the mean pairwise distance** — so `rᵢ+rⱼ ≈ 1.92` already exceeds any achievable centroid separation. There is no cluster size that fixes this: shrinking clusters shrinks r far too slowly under concentration, and growing them shrinks centroid separation.

**Two distinct failure modes reach the same 0 %:**

- **Anisotropy** (sorted blocks). A PC1-sorted block is a thin slab: narrow in PC1, full-width in the other 95 axes. Its radius is set by the *widest* axis, so the ball throws away precisely the one direction carrying information. Radius 1.06 while the PC1 extent is a few percent of the range.
- **Concentration** (k-means clusters, which are roughly isotropic). Even at DiskJoin's recommended 0.1 % cluster size, the radius saturates near the dataset scale because distances concentrate.

**Why dimension is not the variable:** projecting to 8-d or 16-d changes nothing (still 0.00 %). Both mechanisms survive projection. The real statement is about **max versus typical** — a ball summarises a set by one scalar, the maximum over its members, and under concentration that maximum saturates at the global scale. The per-pair bound uses each point's *own* residual ρₓ, which sits far below the set maximum. Same inequality, different quantity substituted in.

## The positive reframing: shape, not dimension

Replace the ball with an axis-aligned box in the projected subspace — prune iff `Σ_d gap_d² > ε`. Still exact, since `Σ gap_d² ≤ ‖Px−Py‖² ≤ ‖x−y‖²`.

On PC1-sorted blocks this prunes 56.9 % — but **identically for k=1 through k=32**. Adding dimensions adds nothing, because those blocks are organised along one axis only, so `gap_d = 0` for every d ≥ 2. The bound was never the limitation; **the partition was.**

Fixing the partition (k-d tree, median splits cycling the top nd projected dims):

| blocks | pts/blk | 1-D sort | kd-2 | **kd-3** | kd-4 |
|---|---|---|---|---|---|
| 128 | 78,125 | 56.94 % | 64.95 % | 60.30 % | 51.05 % |
| 1024 | 9,765 | 58.60 % | 75.25 % | **77.94 %** | 73.89 % |
| 8192 | 1,220 | 58.80 % | 78.61 % | **85.46 %** | 85.44 % |

**1-D sorting saturates at 58.8 %** — and that is not an artifact. The asymptotic ceiling as blocks vanish is `1 − Pr[‖P_nd x − P_nd y‖ ≤ √ε]`, which I measured directly:

| nd | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|
| ceiling | **58.65 %** | 80.55 % | 92.03 % | 96.62 % | 99.47 % | 99.89 % |

The measured 58.80 % at 8192 blocks matches the nd=1 ceiling of 58.65 % — theory and measurement close. A 1-D sort cannot exceed it at any granularity, while each extra partitioned axis raises the ceiling steeply. The practical constraint is that L levels give only L/nd splits per axis, and gaps need ~3 splits per axis, so the optimum is **nd ≈ L/3** — which is exactly why kd-2 wins at 128 blocks and kd-3/4 win at 8192.

**Exactness verified empirically, not just algebraically:** I brute-forced 40 pruned block pairs in full 96-d — 3.81 billion pairs — and the smallest d² found inside any of them was **0.291, 6.6× above the 0.0439 threshold**. No true pair was pruned.

## Is this publishable? Yes, and it's the strongest thing in this line of work

It has the shape a good negative-result paper needs: a clean falsification, a mechanism, a matching quantitative law, and a constructive fix.

> Set-level pruning for ε-joins fails for bounding balls at every granularity and every dimension tested (0.00 % on Deep10M, including k-means at the recommended 0.1 % cluster size) — not because of ambient dimension, but because a ball summarises a set by a maximum that saturates under distance concentration. The same exact bound on axis-aligned boxes, with a partition organised along the same axes, prunes 85.5 % at 100 % recall. The determinant is the shape of the set summary and its alignment with the partition. A 1-D sort saturates at exactly the `1 − Pr[|u_x−u_y| ≤ √ε]` ceiling; each additional partitioned axis raises that ceiling steeply.

That also repositions your PC1 sort — currently presented as "the thing that works" — as a special case leaving most of the available pruning on the table.

**Projected impact, flagged as projected.** At 1024 blocks with kd-3, kept drops from 43.7 % to 22.1 %: about 2× less filter work, so ~18.8 s → ~10 s, taking end-to-end from 12.7× to roughly 24× over brute force. **I have not run this through the actual pipeline** — it's inferred from the kept fraction — and it's the obvious next experiment. Two things could eat it: re-partitioning requires a gather (one-time), and finer blocks multiply kernel launches (115k at 1024 blocks is fine at ~0.6 s; 8192 blocks would need 4.9M launches and would demand a persistent work-queue kernel before the 85 % prune rate is realisable).

**Caveats for the write-up.** One dataset, one ε. The concentration ratio (std/mean = 0.086) and the PC spectrum drive every number here, so the claim to make is the *mechanism* plus the ceiling formula — both of which transfer — rather than the specific percentages.