#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <utility>
#include <cmath>
#include <algorithm>
#include <limits>
#include <omp.h>
#include <immintrin.h>
#include <cstring>
#include <cstdlib>


#define DATASET "/home/dev/md/sift/sift_base.fvecs"

extern "C" {
    // BLAS SGEMM: C = alpha*A*B + beta*C
    void cblas_sgemm(int order, int transA, int transB,
                     int M, int N, int K,
                     float alpha, const float* A, int lda,
                     const float* B, int ldb,
                     float beta, float* C, int ldc);
    // OpenBLAS thread control
    void openblas_set_num_threads(int num_threads);
    int  openblas_get_num_threads(void);
}
// CBLAS constants
static constexpr int CblasRowMajor = 101;
static constexpr int CblasNoTrans  = 111;
static constexpr int CblasTrans    = 112;


struct FVecs {
    std::size_t n = 0;   // number of vectors
    std::size_t d = 0;   // dimension
    std::vector<float> data; // contiguous vector data, size n*d

    const float* vec(std::size_t i) const { return &data[i * d]; }
    float* vec_mut(std::size_t i) { return &data[i * d]; }
};

static std::uint64_t file_size_bytes(std::ifstream& in) {
    auto cur = in.tellg();
    in.seekg(0, std::ios::end);
    auto end = in.tellg();
    in.seekg(cur, std::ios::beg);
    return static_cast<std::uint64_t>(end);
}

FVecs read_fvecs(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("Failed to open: " + path);

    // Read first dimension
    std::int32_t d32 = 0;
    in.read(reinterpret_cast<char*>(&d32), sizeof(d32));
    if (!in) throw std::runtime_error("Failed to read dimension from: " + path);
    if (d32 <= 0) throw std::runtime_error("Invalid dimension in file.");

    const std::size_t d = static_cast<std::size_t>(d32);

    // Compute number of vectors from file size
    in.seekg(0, std::ios::beg);
    const std::uint64_t sz = file_size_bytes(in);
    const std::uint64_t record_bytes = 4ull + 4ull * static_cast<std::uint64_t>(d);

    if (sz % record_bytes != 0) {
        throw std::runtime_error("File size is not a multiple of record size. "
                                 "Wrong dim or corrupt file?");
    }

    const std::size_t n = static_cast<std::size_t>(sz / record_bytes);

    FVecs out;
    out.n = n;
    out.d = d;
    out.data.resize(n * d);

    // Read all records
    in.seekg(0, std::ios::beg);
    for (std::size_t i = 0; i < n; ++i) {
        std::int32_t dim_check = 0;
        in.read(reinterpret_cast<char*>(&dim_check), sizeof(dim_check));
        if (static_cast<std::size_t>(dim_check) != d) {
            throw std::runtime_error("Dimension mismatch at vector " + std::to_string(i));
        }
        in.read(reinterpret_cast<char*>(out.vec_mut(i)), d * sizeof(float));
    }

    std::cout << "Loaded n=" << out.n << " d=" << out.d << "\n";
    return out;
}

/// @brief Compute squared Euclidean distance using AVX-256 intrinsics
static inline float squared_distance_avx(const float* __restrict__ a,
                                          const float* __restrict__ b,
                                          std::size_t d) {
    __m256 sum = _mm256_setzero_ps();

    std::size_t i = 0;
    // Process 8 floats at a time
    for (; i + 8 <= d; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        __m256 diff = _mm256_sub_ps(va, vb);
        sum = _mm256_fmadd_ps(diff, diff, sum);  // FMA: sum += diff * diff
    }

    // Horizontal sum of the 8 floats in sum
    // sum = [s0 s1 s2 s3 | s4 s5 s6 s7]
    __m128 hi = _mm256_extractf128_ps(sum, 1);     // [s4 s5 s6 s7]
    __m128 lo = _mm256_castps256_ps128(sum);        // [s0 s1 s2 s3]
    __m128 r  = _mm_add_ps(lo, hi);                 // [s0+s4 s1+s5 s2+s6 s3+s7]
    r = _mm_hadd_ps(r, r);                          // [s01+s45 s23+s67 ...]
    r = _mm_hadd_ps(r, r);                          // [total ...]
    float result = _mm_cvtss_f32(r);

    // Handle remaining elements
    for (; i < d; ++i) {
        float diff = a[i] - b[i];
        result += diff * diff;
    }

    return result;
}

/// @brief Find the top k closest pairs of vectors using tile-based static scheduling for cache locality
/// @param fvecs input vectors
/// @param k number of top pairs to find
/// @param top_k output vector of top k pairs (index1, index2) sorted by distance
void top_k_pairs(const FVecs& fvecs, std::size_t k, std::vector<std::pair<std::size_t, std::size_t>>& top_k) {
    const std::size_t n = fvecs.n;
    const std::size_t d = fvecs.d;

    // Tile size chosen so that two tiles of vectors fit comfortably in L2 cache.
    // For d=128 floats (512 B per vec), TILE=256 → 256*512 = 128 KB per tile block.
    constexpr std::size_t TILE = 256;

    // Each element: (distance, (i, j))  — max-heap so we can evict the largest
    using Entry = std::pair<float, std::pair<std::size_t, std::size_t>>;
    auto cmp = [](const Entry& a, const Entry& b) { return a.first < b.first; };
    using MaxHeap = std::priority_queue<Entry, std::vector<Entry>, decltype(cmp)>;

    const int num_threads = omp_get_max_threads();
    std::vector<MaxHeap> local_heaps(num_threads, MaxHeap(cmp));

    // Number of tile blocks along each axis
    const std::size_t num_tiles = (n + TILE - 1) / TILE;

    // Total upper-triangular tile pairs (including diagonal): num_tiles*(num_tiles+1)/2
    const std::size_t total_tile_pairs = num_tiles * (num_tiles + 1) / 2;

    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        auto& heap = local_heaps[tid];

        // Cache the current threshold to avoid heap queries on every pair
        float threshold = std::numeric_limits<float>::max();

        #pragma omp for schedule(static)
        for (std::size_t tp = 0; tp < total_tile_pairs; ++tp) {
            // Map linear index to upper-triangular tile coords (ti, tj) with ti <= tj.
            // Encoding: tp = tj*(tj+1)/2 + ti
            std::size_t tj = static_cast<std::size_t>(
                (-1.0 + std::sqrt(1.0 + 8.0 * static_cast<double>(tp))) / 2.0);
            while (tj * (tj + 1) / 2 > tp) --tj;
            while ((tj + 1) * (tj + 2) / 2 <= tp) ++tj;
            std::size_t ti = tp - tj * (tj + 1) / 2;

            const std::size_t i_begin = ti * TILE;
            const std::size_t j_begin = tj * TILE;
            const std::size_t i_end = std::min(i_begin + TILE, n);
            const std::size_t j_end = std::min(j_begin + TILE, n);

            if (ti == tj) {
                // Diagonal tile: only upper triangle (i < j)
                for (std::size_t i = i_begin; i < i_end; ++i) {
                    const float* vi = fvecs.vec(i);
                    for (std::size_t j = i + 1; j < j_end; ++j) {
                        float dist = squared_distance_avx(vi, fvecs.vec(j), d);
                        if (heap.size() < k) {
                            heap.push({dist, {i, j}});
                            if (heap.size() == k) threshold = heap.top().first;
                        } else if (dist < threshold) {
                            heap.pop();
                            heap.push({dist, {i, j}});
                            threshold = heap.top().first;
                        }
                    }
                }
            } else {
                // Off-diagonal tile: all i×j pairs (ti < tj guarantees i < j)
                for (std::size_t i = i_begin; i < i_end; ++i) {
                    const float* vi = fvecs.vec(i);
                    for (std::size_t j = j_begin; j < j_end; ++j) {
                        float dist = squared_distance_avx(vi, fvecs.vec(j), d);
                        if (heap.size() < k) {
                            heap.push({dist, {i, j}});
                            if (heap.size() == k) threshold = heap.top().first;
                        } else if (dist < threshold) {
                            heap.pop();
                            heap.push({dist, {i, j}});
                            threshold = heap.top().first;
                        }
                    }
                }
            }
        }
    }

    // Merge all thread-local heaps into one global heap
    MaxHeap global_heap(cmp);
    for (auto& heap : local_heaps) {
        while (!heap.empty()) {
            auto entry = heap.top();
            heap.pop();
            if (global_heap.size() < k) {
                global_heap.push(entry);
            } else if (entry.first < global_heap.top().first) {
                global_heap.pop();
                global_heap.push(entry);
            }
        }
    }

    // Extract results sorted by distance (ascending)
    top_k.resize(global_heap.size());
    for (int i = static_cast<int>(top_k.size()) - 1; i >= 0; --i) {
        top_k[i] = global_heap.top().second;
        global_heap.pop();
    }
}

/// @brief Find the top k closest pairs using SGEMM (OpenBLAS) for bulk distance computation.
/// D2[i,j] = ||a_i||^2 + ||b_j||^2 - 2 * <a_i, b_j>
/// Self-join optimized: 64B-aligned data, AVX-512 post-processing, OpenBLAS threading control.
void top_k_pairs_sgemm(const FVecs& fvecs, std::size_t k, std::vector<std::pair<std::size_t, std::size_t>>& top_k) {
    const std::size_t n = fvecs.n;
    const std::size_t d = fvecs.d;
    const int num_threads = omp_get_max_threads();

    // --- Step 1: 64B-aligned data layout for optimal SGEMM packing (Zen4 AVX-512) ---
    // d=128 → 512 bytes/row, every row is automatically 64B-aligned.
    float* A = static_cast<float*>(std::aligned_alloc(64, n * d * sizeof(float)));
    if (!A) throw std::runtime_error("aligned_alloc failed for A");
    std::memcpy(A, fvecs.data.data(), n * d * sizeof(float));

    // --- Step 2: Precompute squared norms with AVX-512 (OpenMP) ---
    float* norms2 = static_cast<float*>(std::aligned_alloc(64, ((n * sizeof(float) + 63) / 64) * 64));
    if (!norms2) throw std::runtime_error("aligned_alloc failed for norms2");

    #pragma omp parallel for schedule(static)
    for (std::size_t i = 0; i < n; ++i) {
        const float* v = A + i * d;
        __m256 sum = _mm256_setzero_ps();
        std::size_t j = 0;
        for (; j + 8 <= d; j += 8) {
            __m256 x = _mm256_load_ps(v + j);  // 32B-aligned (rows are 512B = 64B-aligned)
            sum = _mm256_fmadd_ps(x, x, sum);
        }
        __m128 hi = _mm256_extractf128_ps(sum, 1);
        __m128 lo = _mm256_castps256_ps128(sum);
        __m128 r  = _mm_add_ps(lo, hi);
        r = _mm_hadd_ps(r, r);
        r = _mm_hadd_ps(r, r);
        float s = _mm_cvtss_f32(r);
        for (; j < d; ++j) s += v[j] * v[j];
        norms2[i] = s;
    }

    // --- Step 3: Tile-based SGEMM + AVX-512 distance extraction ---
    // TILE×TILE×4 bytes = peak memory for the Gram sub-block.  4096 → 64 MB.
    constexpr std::size_t TILE = 4096;

    using Entry = std::pair<float, std::pair<std::size_t, std::size_t>>;
    auto cmp = [](const Entry& a, const Entry& b) { return a.first < b.first; };
    using MaxHeap = std::priority_queue<Entry, std::vector<Entry>, decltype(cmp)>;

    std::vector<MaxHeap> local_heaps(num_threads, MaxHeap(cmp));

    const std::size_t num_tiles = (n + TILE - 1) / TILE;

    // Pre-allocate G buffer once (TILE×TILE), reuse across tile pairs
    const std::size_t G_alloc = TILE * TILE * sizeof(float);
    float* G = static_cast<float*>(std::aligned_alloc(64, G_alloc));
    if (!G) throw std::runtime_error("aligned_alloc failed for G");

    // Let OpenBLAS use all cores for SGEMM; avoid nested parallelism
    openblas_set_num_threads(num_threads);

    for (std::size_t ti = 0; ti < num_tiles; ++ti) {
        const std::size_t i_begin = ti * TILE;
        const std::size_t i_end   = std::min(i_begin + TILE, n);
        const std::size_t m       = i_end - i_begin;

        for (std::size_t tj = ti; tj < num_tiles; ++tj) {
            const std::size_t j_begin = tj * TILE;
            const std::size_t j_end   = std::min(j_begin + TILE, n);
            const std::size_t p       = j_end - j_begin;

            // SGEMM: G = A[ti] * A[tj]^T  — OpenBLAS parallelizes internally
            cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasTrans,
                        static_cast<int>(m), static_cast<int>(p), static_cast<int>(d),
                        1.0f, A + i_begin * d, static_cast<int>(d),
                              A + j_begin * d, static_cast<int>(d),
                        0.0f, G, static_cast<int>(p));

            // Convert dot products → squared distances, extract top-k (OpenMP + AVX-512)
            #pragma omp parallel
            {
                int tid = omp_get_thread_num();
                auto& heap = local_heaps[tid];
                float threshold = (heap.size() >= k) ? heap.top().first
                                                      : std::numeric_limits<float>::max();

                #pragma omp for schedule(static)
                for (std::size_t li = 0; li < m; ++li) {
                    const std::size_t gi = i_begin + li;
                    const float ni = norms2[gi];
                    const float* G_row = G + li * p;
                    const float* b2    = norms2 + j_begin;

                    // Diagonal tile: only upper triangle (gi < gj)
                    const std::size_t lj_start = (ti == tj) ? (li + 1) : 0;

                    // --- Scalar prefix to reach 16-aligned lj ---
                    std::size_t lj = lj_start;
                    for (; lj < p && (lj & 15); ++lj) {
                        float dist2 = ni + b2[lj] - 2.0f * G_row[lj];
                        if (dist2 < 0.0f) dist2 = 0.0f;
                        if (heap.size() < k) {
                            heap.push({dist2, {gi, j_begin + lj}});
                            if (heap.size() == k) threshold = heap.top().first;
                        } else if (dist2 < threshold) {
                            heap.pop();
                            heap.push({dist2, {gi, j_begin + lj}});
                            threshold = heap.top().first;
                        }
                    }

                    // --- AVX2 main loop: 8 distances per iteration ---
                    const __m256 vni   = _mm256_set1_ps(ni);
                    const __m256 vtwo  = _mm256_set1_ps(2.0f);
                    const __m256 vzero = _mm256_setzero_ps();
                    __m256 vthresh = _mm256_set1_ps(threshold);

                    for (; lj + 8 <= p; lj += 8) {
                        __m256 vb2 = _mm256_loadu_ps(b2 + lj);
                        __m256 vg  = _mm256_loadu_ps(G_row + lj);
                        // D2 = ni + b2 - 2*G
                        __m256 vd2 = _mm256_add_ps(vni, vb2);
                        vd2 = _mm256_fnmadd_ps(vtwo, vg, vd2);
                        vd2 = _mm256_max_ps(vd2, vzero);

                        // Fast skip: compare all 8 against threshold
                        __m256 cmp = _mm256_cmp_ps(vd2, vthresh, _CMP_LT_OS);
                        int mask = _mm256_movemask_ps(cmp);
                        if (mask) {
                            // At least one candidate below threshold — extract
                            alignas(32) float d2_arr[8];
                            _mm256_store_ps(d2_arr, vd2);
                            while (mask) {
                                int bit = __builtin_ctz(mask);
                                mask &= mask - 1;
                                float dist2 = d2_arr[bit];
                                std::size_t gj = j_begin + lj + static_cast<std::size_t>(bit);
                                if (heap.size() < k) {
                                    heap.push({dist2, {gi, gj}});
                                    if (heap.size() == k) {
                                        threshold = heap.top().first;
                                        vthresh = _mm256_set1_ps(threshold);
                                    }
                                } else if (dist2 < threshold) {
                                    heap.pop();
                                    heap.push({dist2, {gi, gj}});
                                    threshold = heap.top().first;
                                    vthresh = _mm256_set1_ps(threshold);
                                }
                            }
                        }
                    }

                    // --- Scalar tail ---
                    for (; lj < p; ++lj) {
                        float dist2 = ni + b2[lj] - 2.0f * G_row[lj];
                        if (dist2 < 0.0f) dist2 = 0.0f;
                        if (heap.size() < k) {
                            heap.push({dist2, {gi, j_begin + lj}});
                            if (heap.size() == k) threshold = heap.top().first;
                        } else if (dist2 < threshold) {
                            heap.pop();
                            heap.push({dist2, {gi, j_begin + lj}});
                            threshold = heap.top().first;
                        }
                    }
                }
            }
        }
    }

    std::free(G);

    // Merge all thread-local heaps into one global heap
    MaxHeap global_heap(cmp);
    for (auto& heap : local_heaps) {
        while (!heap.empty()) {
            auto entry = heap.top();
            heap.pop();
            if (global_heap.size() < k) {
                global_heap.push(entry);
            } else if (entry.first < global_heap.top().first) {
                global_heap.pop();
                global_heap.push(entry);
            }
        }
    }

    // Extract results sorted by distance (ascending)
    top_k.resize(global_heap.size());
    for (int i = static_cast<int>(top_k.size()) - 1; i >= 0; --i) {
        top_k[i] = global_heap.top().second;
        global_heap.pop();
    }

    std::free(norms2);
    std::free(A);
}



/// @brief Compute all pairwise squared distances using tiled SGEMM, no top-k heap.
/// Writes upper-triangular D2 tile blocks to a binary file ("D2_block") as they are computed.
/// Each written record: { uint64 i_begin, uint64 j_begin, uint64 m, uint64 p, float[m*p] }
/// For diagonal tiles only the upper triangle is meaningful (entries with gi < gj).
/// This function benchmarks raw SGEMM + D2 throughput without heap overhead.
void pairs_without_topk(const FVecs& fvecs, const std::string& out_path) {
    const std::size_t n = fvecs.n;
    const std::size_t d = fvecs.d;
    const int num_threads = omp_get_max_threads();

    // --- 64B-aligned data copy ---
    float* A = static_cast<float*>(std::aligned_alloc(64, n * d * sizeof(float)));
    if (!A) throw std::runtime_error("aligned_alloc failed for A");
    std::memcpy(A, fvecs.data.data(), n * d * sizeof(float));

    // --- Precompute squared norms (OpenMP, AVX2) ---
    float* norms2 = static_cast<float*>(std::aligned_alloc(64, ((n * sizeof(float) + 63) / 64) * 64));
    if (!norms2) throw std::runtime_error("aligned_alloc failed for norms2");

    #pragma omp parallel for schedule(static)
    for (std::size_t i = 0; i < n; ++i) {
        const float* v = A + i * d;
        __m256 sum = _mm256_setzero_ps();
        std::size_t j = 0;
        for (; j + 8 <= d; j += 8) {
            __m256 x = _mm256_load_ps(v + j);
            sum = _mm256_fmadd_ps(x, x, sum);
        }
        __m128 hi = _mm256_extractf128_ps(sum, 1);
        __m128 lo = _mm256_castps256_ps128(sum);
        __m128 r  = _mm_add_ps(lo, hi);
        r = _mm_hadd_ps(r, r);
        r = _mm_hadd_ps(r, r);
        float s = _mm_cvtss_f32(r);
        for (; j < d; ++j) s += v[j] * v[j];
        norms2[i] = s;
    }

    // --- Tile-based SGEMM → D2 conversion, written to file ---
    constexpr std::size_t TILE = 4096;
    const std::size_t num_tiles = (n + TILE - 1) / TILE;

    // Pre-allocate G and D2 buffers (reused across tiles)
    float* G  = static_cast<float*>(std::aligned_alloc(64, TILE * TILE * sizeof(float)));
    float* D2 = static_cast<float*>(std::aligned_alloc(64, TILE * TILE * sizeof(float)));
    if (!G || !D2) throw std::runtime_error("aligned_alloc failed for G/D2 buffers");

    openblas_set_num_threads(num_threads);

    std::ofstream out(out_path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("Failed to open output: " + out_path);

    std::size_t tiles_done = 0;
    const std::size_t total_tile_pairs = num_tiles * (num_tiles + 1) / 2;

    for (std::size_t ti = 0; ti < num_tiles; ++ti) {
        const std::size_t i_begin = ti * TILE;
        const std::size_t i_end   = std::min(i_begin + TILE, n);
        const std::size_t m       = i_end - i_begin;

        for (std::size_t tj = ti; tj < num_tiles; ++tj) {
            const std::size_t j_begin = tj * TILE;
            const std::size_t j_end   = std::min(j_begin + TILE, n);
            const std::size_t p       = j_end - j_begin;

            // SGEMM: G = A[ti] * A[tj]^T — OpenBLAS parallelizes internally
            cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasTrans,
                        static_cast<int>(m), static_cast<int>(p), static_cast<int>(d),
                        1.0f, A + i_begin * d, static_cast<int>(d),
                              A + j_begin * d, static_cast<int>(d),
                        0.0f, G, static_cast<int>(p));

            // Convert G → D2 in parallel (OpenMP + AVX2)
            #pragma omp parallel for schedule(static)
            for (std::size_t li = 0; li < m; ++li) {
                const float ni = norms2[i_begin + li];
                const float* G_row  = G  + li * p;
                float*       D2_row = D2 + li * p;
                const float* b2     = norms2 + j_begin;

                const __m256 vni   = _mm256_set1_ps(ni);
                const __m256 vtwo  = _mm256_set1_ps(2.0f);
                const __m256 vzero = _mm256_setzero_ps();

                std::size_t lj = 0;
                for (; lj + 8 <= p; lj += 8) {
                    __m256 vb2 = _mm256_loadu_ps(b2 + lj);
                    __m256 vg  = _mm256_loadu_ps(G_row + lj);
                    __m256 vd2 = _mm256_add_ps(vni, vb2);
                    vd2 = _mm256_fnmadd_ps(vtwo, vg, vd2);  // ni + b2 - 2*G
                    vd2 = _mm256_max_ps(vd2, vzero);
                    _mm256_storeu_ps(D2_row + lj, vd2);
                }
                for (; lj < p; ++lj) {
                    float dist2 = ni + b2[lj] - 2.0f * G_row[lj];
                    D2_row[lj] = std::max(dist2, 0.0f);
                }
            }

            // Write tile header + D2 block
            std::uint64_t hdr[4] = { i_begin, j_begin, m, p };
            out.write(reinterpret_cast<const char*>(hdr), sizeof(hdr));
            out.write(reinterpret_cast<const char*>(D2), m * p * sizeof(float));

            ++tiles_done;
            if (tiles_done % 50 == 0 || tiles_done == total_tile_pairs) {
                std::cout << "\r  Tiles: " << tiles_done << "/" << total_tile_pairs << std::flush;
            }
        }
    }

    out.close();
    std::cout << "\nWrote D2 blocks to: " << out_path << "\n";

    std::free(D2);
    std::free(G);
    std::free(norms2);
    std::free(A);
}

int main(int argc, char *argv[]) {
    auto fvecs = read_fvecs(DATASET);

    const std::size_t k = 100;

    // --- Tile-based AVX implementation ---
    // {
    //     std::vector<std::pair<std::size_t, std::size_t>> results;
    //     auto t0 = omp_get_wtime();
    //     top_k_pairs(fvecs, k, results);
    //     auto t1 = omp_get_wtime();

    //     std::cout << "\n=== Tile-based AVX ===\n";
    //     std::cout << "Top " << k << " closest pairs (squared L2 distance):\n";
    //     for (std::size_t i = 0; i < results.size(); ++i) {
    //         auto [a, b] = results[i];
    //         float dist = squared_distance_avx(fvecs.vec(a), fvecs.vec(b), fvecs.d);
    //         std::cout << i + 1 << ": (" << a << ", " << b << ") dist=" << dist << "\n";
    //     }
    //     std::cout << "Time: " << (t1 - t0) << " seconds\n";
    // }

    // --- SGEMM (OpenBLAS) implementation ---
    // {
    //     std::vector<std::pair<std::size_t, std::size_t>> results;
    //     auto t0 = omp_get_wtime();
    //     top_k_pairs_sgemm(fvecs, k, results);
    //     auto t1 = omp_get_wtime();

    //     std::cout << "\n=== SGEMM (OpenBLAS) top-k ===\n";
    //     std::cout << "Top " << k << " closest pairs (squared L2 distance):\n";
    //     for (std::size_t i = 0; i < results.size(); ++i) {
    //         auto [a, b] = results[i];
    //         float dist = squared_distance_avx(fvecs.vec(a), fvecs.vec(b), fvecs.d);
    //         std::cout << i + 1 << ": (" << a << ", " << b << ") dist=" << dist << "\n";
    //     }
    //     std::cout << "Time: " << (t1 - t0) << " seconds\n";
    // }

    // --- SGEMM full pairwise (no heap) ---
    {
        auto t0 = omp_get_wtime();
        pairs_without_topk(fvecs, "D2_block");
        auto t1 = omp_get_wtime();

        std::cout << "\n=== SGEMM full pairwise (no heap) ===\n";
        std::cout << "Time: " << (t1 - t0) << " seconds\n";
    }

    std::cout << "\nThreads: " << omp_get_max_threads() << "\n";

    return 0;
}