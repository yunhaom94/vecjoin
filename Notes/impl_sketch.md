# Method 1 — Projection bound (exact)

## Principle

For an orthogonal projection P onto a k-dimensional subspace, split each vector into `x = Px + (I−P)x`. Cauchy–Schwarz on the discarded part gives

`⟨x,y⟩ = ⟨Px,Py⟩ + ⟨(I−P)x,(I−P)y⟩ ≤ ⟨Px,Py⟩ + ρ_x ρ_y`,  `ρ = ‖(I−P)x‖`

Equivalently `‖x−y‖² ≥ ‖Px−Py‖² + (ρ_x−ρ_y)²`. This holds for **any** orthogonal P, so recall is 100 % by construction; P only affects tightness. PCA is chosen because it maximises captured energy, which minimises ρ.

## Steps

**1. Fit the basis.** Take a sample (200k rows suffices — recall is exact at every sample size and survivor rate is insensitive), subtract its mean, eigendecompose the covariance, order eigenvectors by descending eigenvalue. Keep `V ∈ ℝ^{D×k}`.

**2. Project.** `Q = X·V`, giving k coordinates per vector. k=12 measured optimal on Deep10M; the optimum shifts up with flatter spectra or larger ε.

**3. Residual norms.** `ρ_x = √(‖x‖² − ‖Q_x‖²)`. For unit-norm data this is `√(1 − ‖Q_x‖²)`. Store one float per vector. Do **not** recompute per pair.

**4. Partition.** Build a k-d tree by recursive median splits cycling the top 3 projected dimensions, L levels → 2^L blocks. Sort vectors by block id; this permutation must be applied to `Q`, `ρ`, and the full vectors so blocks are contiguous. Store block start offsets.

**5. Per-block bounding boxes.** For each block, `lo[d] = min`, `hi[d] = max` over the first ~32 projected dims. Scatter-reduce, not a per-block loop.

**6. Block-pair prune.** For blocks (A,B) with per-axis gap `g_d = max(0, lo_{B,d}−hi_{A,d}, lo_{A,d}−hi_{B,d})`, discard the pair if `Σ_d g_d² > ε`. Exact, since `Σ g_d² ≤ ‖Px−Py‖² ≤ ‖x−y‖²`. Enumerate only the upper triangle including the diagonal.

**7. Slab the work.** Split each surviving block pair's rows into slabs sized so that even 100 % survival fits the output buffer: `rows ≤ 0.75·CAP/|B|`. This guarantees no single work item can overflow, which is what makes the retry loop terminate.

**8. Filter kernel.** Tile TM×TN (512×128 for k=12). A warp spans n: lane *l* owns columns *l, l+32, l+64, l+96*, so shared-memory reads are conflict-free and `__ballot_sync` assembles a 32-bit result word directly with no shared-memory atomics. Stage `Q` k-major and `ρ` in shared memory. Per pair: k FMAs for `⟨Q_x,Q_y⟩`, one FMA for `+ρ_xρ_y`, compare against `τ = 1 − ε/2 − 1e-6` (the slack absorbs fp32 evaluation error).

Two structural requirements, both worth ~10–20 %: compute a **group of 4 rows' predicates first, then handle emission** — interleaving them forces the warp to reconverge mid-FMA-stream; and gate emission on a single `__any_sync`, since almost every row survives nothing.

**9. Emit a compact list, not a bitmask.** On a surviving row: popcount the ballot word, warp prefix-scan the counts, one lane reserves the exact slot count with a single `atomicAdd`, each lane writes packed `(i,j)` as uint64 global indices. A dense bitmask imposes a σ-independent floor on refinement (measured 15 s on Deep10M) because the refine must then scan every word regardless of survivor count.

**10. Self-join dedup.** Diagonal block pairs are computed as full squares, so intra-block pairs appear twice. Mask `j ≤ i` out of the ballot word **before** the prefix scan, so reserved slots match what is written.

**11. Batch and adapt.** Launch many work items into one shared list without syncing, flush when the estimated count approaches capacity. Size batches with AIMD (back off by 4× on overflow, grow by 1.5× on success) — density varies ~84× between diagonal and distant block pairs, and naive feedback oscillates.

**12. Refine exactly.** One warp per survivor, grid-stride over the list; the 32 lanes split the D dimensions, then a shuffle reduction. Use the **unexpanded** sum of squared differences, never the Gram form — `‖x‖²+‖y‖²−2⟨x,y⟩` cancels catastrophically for near pairs. Measured against FP64: 0 false negatives, 7 false positives in 75.68 M.

**Measured:** 18.84 s on the full Deep10M self-join (filter 17.96, refine 0.88), 12.7× over a 238.6 s exact brute force, 100.00000 % recall, σ = 2.484e-4 at k=12.

---

# Method 2 — Symmetric RaBitQ filter (approximate)

## Principle

Quantize each vector to a binary sketch and bound the distance from the sketch alone. RaBitQ's published estimator is *asymmetric* (data quantized, query in full precision) and **breaks in the symmetric case**: writing `ō = αo + √(1−α²)v`, the derivation drops `⟨v_x,v_y⟩` as zero-mean, but when two vectors are close their codes coincide and that term is ≈ +1. The estimator then maps identical codes to `1/α² = 1.566` instead of 1.0 — a **+0.566 bias at d² < 0.05**, four times the generic σ, concentrated exactly on the pairs a join cares about.

The repair keeps RaBitQ's centering and explicit norms but replaces the estimator with the angular one, which is exact at h=0 and had 30× lower RMS error on near pairs.

## Steps

**1. Centre.** `c = mean(X)`, `R = X − c`, `n_x = ‖R_x‖`. Storing n explicitly is what makes the method scale-aware, and is why it survives unnormalized data.

**2. Build Super-Bit directions.** Generate `⌈B/D⌉` Gaussian D×D matrices, orthogonalize each by QR, concatenate, keep B columns. Orthogonalizing in batches is unbiased with strictly lower variance than i.i.d. Gaussian directions. B=128 measured as the sweet spot.

**3. Sketch.** `bit_b = sign⟨r_b, x−c⟩`, packed into B/32 uint32 per vector (4 words at B=128). Normalization is unnecessary — the sign is scale-invariant.

**4. Build the bound lookup table.** With `h ~ Binomial(B, θ/π)`, compute the Wilson lower confidence bound on `θ/π` at level z and set `t_up[h] = cos(π·p_lo(h))`, an upper bound on `⟨o_x,o_y⟩`. Since h is an integer in [0,B], this is a table of B+1 floats — **no transcendentals per pair**, which is what makes it cheap. z=3 gives ~99.98 % recall.

**5. Precompute the quick-reject threshold.** `W_min = 1 − ε/(2 n_min²)`; `h_reject = max{h : t_up[h] ≥ W_min}` (20 of 128 on Deep10M). No pair with `h > h_reject` can pass under any norms.

**6. Partition.** The sketch space cannot supply a bounding box — the analogue would be bits on which a whole block agrees, and for a 131,072-vector block the probability any bit is unanimous is ~2⁻¹³¹⁰⁷¹, so the bound is vacuous. Carry auxiliary PCA coordinates (3 floats for a k-d-3 tree, 12 bytes on top of the 16-byte sketch) purely for partitioning, build blocks by recursive median splits, and prune block pairs by `Σ_d g_d² > ε` on those coordinates.

**7. Slab and batch** exactly as any list-emitting filter must: cap slab rows so a single work item cannot overflow the buffer, batch many items into one shared list, AIMD the batch size.

**8. Filter kernel on binary tensor cores.** `mma.sync.aligned.m8n8k128.row.col.s32.b1.b1.s32.xor.popc` computes `D = popc(A⊕B) + C` — 64 Hamming distances over 128-bit sketches per instruction. Because k=128 covers the whole sketch, **there is no k-loop**: the accumulator lives for one instruction, so no pipelining, no multi-stage staging, 40 registers and 5.6 KB shared memory. Fragment layout (verify it against a scalar reference before building on it): `gid = lane>>2`, `tig = lane&3`; A row = gid, word tig; B col = gid, word tig; D row = gid, col = 2·tig+{0,1}.

Per output: quick-reject on `h > h_reject` (integer compare, keeps the LUT's bank-conflicting gather off the hot path), else `d²_lb = n_x² + n_y² − 2 n_x n_y · t_up[h] ≤ ε`. Tile 512×256 measured best.

**9. Emit a compact list.** No transpose is needed: each thread already knows the global coordinates of both its outputs. Count per-thread hits (0–2), gate on `__any_sync`, warp prefix-scan, one `atomicAdd` per warp, write directly.

**10. Pass separate operand base pointers.** Give the kernel `code + offset_A` and `code + offset_B` and index locally. Indexing one global pointer with slab-local indices silently compares the wrong vectors — and produces a *plausible-looking survivor rate* while being nonsense.

**11. Refine exactly.** One warp per survivor, lanes split D, unexpanded sum of squared differences, shuffle reduction. Never the Gram form.

**Measured:** 13.81 s on Deep10M (filter 13.53, refine 0.28), **99.977 %** recall. Portability caveat: b1 MMA exists on sm_75/80/89 only and is dropped after Ada; the int8 fallback (`±1` codes, `⟨s_x,s_y⟩ = B − 2h`) is untested, and scalar POPC is 1.15× *slower* than a k=12 float filter.

---

# Implementation todo — projection bound, from the current codebase

**Phase 0 — build hygiene (do first; blocks accurate measurement)**

1. Turn off `CUDA_SEPARABLE_COMPILATION` in [cpp/src/vess/gpu/CMakeLists.txt:8](cpp/src/vess/gpu/CMakeLists.txt). All 8 current `.cu` objects device-link standalone, so RDC is unnecessary — and it costs **36 %** on a ballot-style kernel (registers 64→130) while costing CUTLASS only 2 %. Also drop it from `apps/{scheduler,simjoin_gpu,ivf_flat_roundtrip}`, which is where header templates get instantiated.
2. Clean reconfigure — the build tree still holds `cutlass_bak/*.o` for a deleted directory.
3. Commit the pending `.github/workflows/pre-commit.yml`.

**Phase 1 — preprocessing** (new `cpp/src/vess/simjoin/gpu/projection_prep.{h,cu}`)

4. PCA fit on a sample → basis; project → `Q (n×k)`; residual norms `ρ`. ~0.21 s for 10M on GPU.
5. k-d partition builder (median splits cycling top 3 dims) producing block ids, permutation, block starts.
6. Apply the permutation to Q, ρ and the base vectors; keep the composed index map so results map back to original ids.
7. Per-block AABB via scatter-reduce; block-pair enumeration with the `Σ g_d² > ε` prune.
8. Serialization so preprocessing is reusable across queries.

**Phase 2 — filter kernel** (new `cpp/include/vess/simjoin/gpu/projection_filter.cuh`)

9. Ballot filter templated on `<KDIM, RB, ROWS>`, emitting packed uint64 pairs. Structure it with the group-of-4 decoupling and the `__any_sync` gate from the start — both are worth 10–20 % and are awkward to retrofit.
10. `j ≤ i` masking applied **before** the prefix scan, for self-join dedup.
11. Unit test the kernel against a CPU reference on a small block pair before wiring anything up.

**Phase 3 — driver** (new joiner alongside `epsilon_neighborhood.cu`)

12. Slab expansion with the capacity-derived row cap.
13. Batched launches, AIMD sizing, per-attempt overflow flag reset (a flag cleared once turns handled retries into false alarms).
14. Per-block base pointers passed explicitly.

**Phase 4 — refine and output**

15. SSD refine over the survivor list; consider reusing `L2SsdPolicy`'s formulation.
16. Decide the output contract: raw pair list, or CSR via the existing `bitmask_decode` path. The list is 158× smaller than a dense mask at σ=1e-4 and removes the refine floor.

**Phase 5 — tests** (extend `cpp/tests/gpu/`)

17. Exactness vs brute force on a small dataset — the primary correctness gate.
18. Invariance tests: identical true-pair counts across k ∈ {8,12,16} and across partitions. These caught real bugs.
19. Edge cases: partial trailing blocks, unaligned n, empty blocks, ε large enough to keep everything.
20. A guard that ground truth uses FP64 **SSD**, not FP64 Gram — the Gram form cancels to noise at d² ~1e-4 and will silently certify wrong answers.

**Phase 6 — integration**

21. Register as a `JOINER` variant next to the FMA/SSD joiners.
22. Benchmark against the existing `bitmask_gemm` path at matched ε and recall.

**Two open items I'd flag rather than schedule.** The k-d-3 partition prunes 73.9 % vs a 1-D sort's 58.4 %, but measured end-to-end it was only 1.39× at matched block size and ~1.06× overall — the granularity it needs costs kernel efficiency. Fixing that means a persistent work-queue kernel (`blockIdx.z` over work items), which is a real design change, not a tweak. And every number here is one dataset at one ε; the k optimum, σ, and partition ceilings are all data-dependent, so the config wants to be tunable rather than baked in.