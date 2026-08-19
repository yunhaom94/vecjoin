# Ordering for cross-joins: the complete picture

## The three-layer decomposition

Everything measured this session fits one frame. The pruned cross-join is a 0/1 matrix `A` — rows are x-blocks, columns are y-blocks, `A[i,j]=1` means the pair survived. Minimising disk traffic decomposes into three decisions:

1. **Relabeling** — permute block IDs so index distance reflects data affinity (RCM, Sloan, recursive k-means, Gorder, spectral)
2. **Traversal** — the order pairs are visited on the permuted grid (row-major, strip, supertile, Hilbert)
3. **Eviction** — Belady, which is provably optimal *given* the sequence, `O(E log C)`, and composes with everything above

The measured leverage is ordered 1 > 2 > 3: relabeling swung 4.4×, traversal up to 10×-from-worst but ~1.5× between sensible choices, and eviction ~20 % (DiskJoin's own ablation agrees).

## Definitions: bandwidth, profile, wavefront

Using the worked 5×5 example:

```
row 0:  ##..#   leftmost j=0   i-j = 0
row 1:  ###..   leftmost j=0   i-j = 1
row 2:  .###.   leftmost j=1   i-j = 1
row 3:  ..###   leftmost j=2   i-j = 1
row 4:  #..##   leftmost j=0   i-j = 4
```

**Bandwidth** = `max |i−j|` over all nonzeros = **4** here, set entirely by the single stray mark at (4,0). A *maximum* — one outlier ruins it while costing almost nothing in traffic. Minimising it is NP-hard (Papadimitriou 1976); CM/RCM are the heuristics.

**Profile** = `Σᵢ (i − j_min(i))` where `j_min(i)` is the leftmost nonzero of row *i* = 0+1+1+1+4 = **7**. The area of the envelope hugging the diagonal — what a skyline solver stores. A *sum*, so robust to outliers.

**Wavefront**: during a top-to-bottom row sweep, column *j* is *live* from the first row touching it to the last. The row-*i* wavefront is the number of live columns at row *i*; here the per-row counts are `[3,4,5,4,3]`, so **max wavefront = 5**. It is literally the working-set size of a row-major sweep, and the three metrics are related: mean wavefront ≈ profile/N + 1, so profile is the "integral" of the wavefront.

**The operational theorem**: if `C ≥ max wavefront + 1`, a row-major sweep incurs zero capacity misses and achieves the compulsory floor (every block loaded exactly once) — verified exactly: both reordered matrices hit the floor at C just past their wavefronts of 36–37, and stayed there.

**Its limit** (your counterexample question): the max is *loose*. Twenty-four columns touched twice each, far apart, inflated max wavefront from 17 to 40; shrinking the cache to 17 cost only +17 % because Belady correctly reloads sparse long-range blocks rather than pinning them. So: minimise profile / quantile-wavefront when choosing an ordering, but *provision* memory from the measured loads-vs-C curve, whose knee sits at the dense core's working set, not the max.

## Q1: dense matrix

**Strip traversal: hold `a = C−2` x-blocks resident, stream all y-blocks past them, serpentine at the turns.** No relabeling — there's nothing to find; every pair is computed regardless.

Measured (96×96, C=16): row-major 0.865, square supertile 0.126, Hilbert 0.127, **strip 0.082**, against a floor of 1/C = 0.0625. The square-tile derivation (`4/C`, minimised at `a=b`) is wrong because it ignores that adjacent tiles share their x-blocks; with reuse counted, loads/pair ≈ `1/a`, maximised by the widest strip that fits. The strip is within ~30 % of the information-theoretic floor and is also the *simplest* schedule — it's just row-major batched `C−2` rows at a time.

## Q2: banded matrix with bandwidth w

**Two regimes, split by whether the band's working set `2w+2` fits in `C`:**

| w | working set | row-major | strip | floor |
|---|---|---|---|---|
| 6 | 14 ≤ 16 | **0.159 = floor** | 0.219 | 0.159 |
| 12 | 26 > 16 | 0.410 | **0.150** | 0.086 |
| 24 | 50 > 16 | 0.686 | **0.112** | 0.047 |
| 48 | 98 > 16 | 0.819 | **0.092** | 0.028 |

- **`2w+2 ≤ C`: plain row-major, and it is provably optimal** — it achieves the compulsory floor exactly (0.159 = 2N/pairs), since the wavefront of a width-w band is 2w+1. Any tiling is strictly worse (~35 %) because tile boundaries force reloads the natural locality avoided.
- **`2w+2 > C`: the strip takes over**, winning by up to **9×** at w=48. Inside the band the problem is locally dense, so the dense-case logic applies. The transition is sharp — one comparison, `2w+2 ≤ C`, decides the schedule.

## Q3: realistic matrix (embedding-derived, imperfectly clustered)

**Two-step recipe: relabel first, then pick the traversal by the resulting wavefront.**

**Step 1 — relabel.** Measured on 128 blocks from an overlapping 10-mode Gaussian mixture, 10 % density, shuffled file order (loads/pair, C=16):

| relabeling | bandwidth | profile | wavefront | loads/pair |
|---|---|---|---|---|
| file order | 125 | 6639 | 128 | 0.788 |
| PCA 1-D projection | 45 | 2345 | 54 | 0.497 |
| spectral (Fiedler) | 47 | 1858 | 52 | 0.351 |
| RCM | **31** | **1095** | 37 | 0.240 |
| **recursive 2-means on centroids** | 108 | 1738 | **36** | **0.230** |

The algorithm families, and what each actually optimises:

- **Bandwidth reduction — Cuthill–McKee / RCM, GPS**: BFS level structures from a pseudo-peripheral node; `O(E)`; in scipy/MATLAB/Boost. Targets bandwidth, gets profile incidentally. Strong here (0.240) — but note it optimises the *wrong metric*: recursive 2-means has 3.5× worse bandwidth (108 vs 31) and still wins on loads, because a few long-range pairs inflate bandwidth without widening the working set.
- **Profile/wavefront reduction — Sloan**: priority-search mixing distance-to-target with degree; targets wavefront *directly*, typically beating RCM on profile by 20–30 % in the sparse-matrix literature. The classically correct choice for this cost model (untested here — Boost has it, scipy doesn't).
- **Spectral/Fiedler**: sort by the Laplacian's second eigenvector; the continuous relaxation of minimum linear arrangement. Global view, mid-pack result, needs an eigensolve.
- **Recursive k-means bisection on block centroids**: recursively 2-means the centroids, emit IDs in recursion order. **Won the measurement**, and has two structural advantages: it needs *no adjacency matrix* — just centroids, so it runs before pruning rather than after — and its recursion tree is a ready-made hierarchy for tiling. For a bipartite cross-join it also handles the two sides naturally: cluster x-centroids and y-centroids in the same space, where graph methods need the bipartite symmetrisation `[[0,A],[Aᵀ,0]]`.
- **Gorder** (DiskJoin's choice): sliding-window neighbour-overlap greedy; same goal, `O(Σd²)` and inherently sequential.
- **Hypergraph partitioning** (KaHyPar/PaToH): the only method whose objective *is* block loads (connectivity−1). Needed only when structure exists that no 1-D embedding can express — measured proxy: 0.201 vs 0.537 for the best rectangle on permuted clusters. But after relabeling, row-major reached 0.167 on the same structure, so for geometric data the cheap relabeling makes the partitioner unnecessary.

**Step 2 — traverse** by the banded rule above: compute the relabelled matrix's wavefront; if it fits in C, row-major (done — you're at the floor); if not, strip. Sweeping all C−1 rectangle shapes through the Belady simulator costs seconds, so measure rather than assume.

**Uniform-random control**: no ordering helps (best 0.49 vs floor 0.16) — sparsity without structure offers nothing to exploit, which is why "realistic" (modal, clustered) and "random" must not be conflated.

Caveats on all numbers: synthetic matrices at N ≤ 200, one seed, greedy as a partitioner proxy, Sloan unmeasured. The rankings' *mechanisms* are solid; the small gaps (0.230 vs 0.240) are within noise and should be re-measured on your real pruned matrix — the simulator runs in seconds and is the decisive test.


#

Both questions deserve a measurement. The second especially — I can construct the condition where partitioning should win and test whether it actually does, using an *oracle* partition rather than my greedy proxy.

# 1. RCM operates on the bipartite symmetrisation

**Confirmed empirically.** RCM is defined only for structurally symmetric matrices — it's a BFS over an undirected graph, and a rectangular `A` has no such graph. `scipy` doesn't even reject it cleanly:

```
RCM on rectangular 96x128 A -> IndexError: Out of bounds on buffer access (axis 0)
```

It indexes `A` as if square and walks off the buffer. So you must build

$$B = \begin{bmatrix} 0 & A \\ A^{\mathsf T} & 0 \end{bmatrix}$$

an `(X+Y)×(X+Y)` symmetric matrix whose graph is exactly the bipartite incidence graph: vertices `0…X−1` are x-blocks, `X…X+Y−1` are y-blocks, edges are surviving pairs. RCM on that returns one permutation of all `X+Y` vertices; **you then split it into two orderings** by filtering on `p < X`, preserving relative order:

```python
B = bmat([[None, A], [A.T, None]], format="csr")
perm  = reverse_cuthill_mckee(B, symmetric_mode=True)
xperm = [p     for p in perm if p <  X]
yperm = [p - X for p in perm if p >= X]
```

Two consequences worth knowing:

- **The two sides interleave.** RCM's BFS alternates between x and y vertices (every edge crosses sides), so the level structure is really a bipartite BFS. Splitting afterwards is what makes it usable, and it works because relative order within each side is what the traversal consumes.
- **Bandwidth in `B` isn't bandwidth in `A`.** A pair at `(i,j)` sits at distance `|i − (X+j)|` in `B`, which mixes the two index spaces. Minimising `B`'s bandwidth is a proxy for what you want, not the thing itself — one more reason to prefer wavefront-targeting methods (Sloan) or geometric ones over RCM here.

This is also where **recursive k-means on centroids** has a structural edge: x-centroids and y-centroids live in the same ℝᵈ, so you cluster them jointly and read off both orderings directly. No symmetrisation, no splitting, and it works before the pruning matrix exists.

# 2. When hypergraph partitioning wins

The condition is **structure that no linear arrangement can express** — most cleanly, **overlapping membership**.

## The construction

96×128 cross-join, 24 latent groups, **every block belongs to two groups**, pair survives iff the blocks share a group. 2003 pairs, 16 % dense.

| order | loads/pair |
|---|---|
| row-major, file order | 0.739 |
| row-major, RCM relabel | 0.526 |
| best rectangle (15,1), file order | 0.417 |
| best rectangle (15,1), RCM relabel | 0.334 |
| **oracle partition (by group)** | **0.219** |
| *(analytic bound: 2 loads/block)* | *0.224* |

The partition beats the best relabel-plus-traversal combination by **1.53×**, and lands on its analytic bound (0.219 vs 0.224 — slightly better, since blocks sharing both groups get reused).

## Why no ordering can close the gap

A 1-D ordering assigns each block **one** position. A block in groups 3 and 17 is pulled toward both; wherever it lands, half its pairs are far away on the line. That isn't a permuted band waiting to be discovered — **no permutation exists** that makes this matrix banded, so RCM, Sloan, spectral and k-means all fail together, differing only in how gracefully.

A partition is not a permutation: it can place the *same block in two parts*, paying one reload. That extra degree of freedom is exactly what the connectivity−1 objective buys, and exactly what a linear order lacks.

## The conditions, stated

Partitioning wins when **all** of these hold:

1. **Overlapping / non-hierarchical community structure** — blocks with multiple affinities. This is the essential one.
2. **Structure invisible in block indices** — otherwise relabeling is far cheaper. Recall the earlier disjoint-cluster case: greedy got 0.201, but *relabeling* then row-major got 0.167 and beat it.
3. **No usable geometry** — if centroids exist, recursive k-means captures most hierarchical structure for a fraction of the cost.
4. **The pruned matrix is sparse but not random** — random has nothing for anyone to find (measured: nothing beat 0.49 against a 0.16 floor).

It **loses** when the grid is dense (measured 0.312 vs 0.127 for Hilbert — 2.5× worse; there's nothing to search and greedy just makes locally-sensible globally-poor choices), or when the structure is disjoint and relabeling suffices.

## For your cross-join specifically

Embeddings from a model *do* produce overlapping semantic structure — a vector near both "dog" and "wolf" regions is the norm, not the exception. So condition 1 is plausibly satisfied. But conditions 2 and 3 are not: you have block centroids in ℝ⁹⁶, so the cheap geometric relabeling is available and captures the dominant hierarchical part.

The decision procedure that follows from all of this: relabel by recursive k-means, measure loads/pair, and compare against the compulsory floor. If you land within ~1.5× of the floor, stop — the overlap isn't costing you much. A persistent 2×+ gap after relabeling is the signature of overlapping membership, and only then is KaHyPar/PaToH worth the integration.

Caveat: my "oracle partition" knows the true group labels, so 0.219 is what a *perfect* partitioner achieves. A real one recovers overlapping communities imperfectly, so treat 1.53× as the ceiling on the gain, not the expected one.