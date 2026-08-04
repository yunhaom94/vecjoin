# Plan
*This file outlines a list of items that need to be done for the project.*



## TODO List
*This is a list of tasks that need to be done for the project. This should be a living document that can be changed as the project evolves.*

- Baseline Design
    - Assume cache (max usable VRAM) x10 (adjustable to see which looks the best) = dataset size
    - Use FAISS (IVF) + Raw Nested Loop join
- 随机 coarse block + brute-force/GEMM I/O pipeline
    - 找到并接入真实 random coarse schedule；当前 `simjoin_gpu` 仍是 row-major Cartesian schedule + `resize(100)`
    - 复现 `32Ki x 32Ki`（read/compute `8 ms / 2 ms`）与 `256Ki x 256Ki`（`600 ms / 40 ms`）；固定 `d`、冷热 page cache 与计时边界
    - 分离计时：SSD/page fault、`mmap -> pinned` memcpy、H2D、bitmask compute、scan/sync、decode、D2H、sink acquire wait、buffered write、durable write
    - 每个 block pair 记录：`m,n,d`、命中率 `p`、输入/bitmask/decoded bytes、active/reserved VRAM、buffer occupancy、stall 原因
    - 验证带宽异常：block 边长放大 `8x`、输入字节仅 `8x`，read latency 却放大 `75x`（effective BW 下降 `9.375x`）？
    - 验证存储模型：输入 `4d(m+n)`；bitmask `8m ceil(n/64) ~= mn/8`；当前 pair list `16pmn`
    - 对比三种结果格式：当前两个 `int64`（16 B/hit）、local/linear ID（8 B/hit）、raw bitmask；当前格式 crossover `p=1/128 ~= 0.78%`
    - 增加 direct-bitmask -> pinned RAM sink baseline；先测 RAM/D2H，再决定是否实现 GDS/device-to-file
    - 将 H2D、compute、decode/D2H 拆为独立 streams + event/credit backpressure；输入双缓冲、输出至少三缓冲
    - `256Ki` 路径改为 row-band bitmask 流式生成/输出，避免完整 8 GiB mask 长驻 HBM
    - 扫描 `chunk_capacity x pool_size`：吞吐、decode amplification、host/device pool 等待；验证有限 buffer 只能吸收 burst，不能修复平均 sink 带宽不足
    - 对比 row-major、random、access-graph ordering 的 block reload、I/O bytes 与 GPU idle；确定需要的平均 block reuse
    - 输出容量不足必须报错或 rotate，禁止 `pairs_found != pairs_written` 的静默截断
- SimJoin-inspired fine-search feasibility
    - Hold one representative `D_i` and its graph index fully resident in HBM; exclude outer I/O first
    - Build one query proximity graph/MST per correlated `Q_j`; cut into a shallow forest with bounded depth/cluster size
    - Compare at equal recall: independent batched graph search; MST reorder only; literal parent-window sliding; shallow forest + compact parent seeds; forest + sibling candidate microtiles
    - Workloads: correlated stream batch vs shuffled/OOD batch; sparse mean window `~1` and moderate window `~32-100`
    - Metrics: block-pair latency, distance computations, graph expansions, unique node/vector loads, HBM bytes, occupancy, p95 query work, seed/frontier memory, recall
    - Continue if shallow-forest reuse is `>=20%` faster than tuned independent GPU search with `<10%` slowdown on uncorrelated queries
    - If reorder-only captures most of the gain, keep ordering and drop stateful sliding

## Paper Outline
*This is a outline of the paper that we will write the project. This should be a list of sections, subsections, and summaries of what will be included in each section. This should be a living document that can be changed as the project evolves.* 

- [ ] Introduction
- [ ] Background and motivation
  - [ ]  ...
  - [ ]  ...



## Implementation Plan
*This is a outline of the implementation plan for the project. This should be a list of tasks that need to be done for the implementation of the project. This should be a living document that can be changed as the project evolves.*
- [ ] Data ingestion and parsing
- [ ] Add a per-`D_i` graph-index loader/cache and indexed `GraphJoiner` beside the exact dense joiner
- [ ] Compile per-`Q_j` shallow proximity forests; retain explicit query/global-ID maps after reordering
- [ ] Implement frontier/ready-queue batching with bounded device seed/frontier storage and local-entry fallback
- [ ] Add sibling candidate-slab execution and adaptive dense vs indexed dispatch
- [ ] Instrument fine-search work, HBM traffic, occupancy, state size, and recall separately from outer I/O
