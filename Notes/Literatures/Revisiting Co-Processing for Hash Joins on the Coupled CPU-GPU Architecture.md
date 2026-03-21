Revisiting Co-Processing for Hash Joins on the Coupled
CPU-GPU Architecture

Jiong He
Nanyang Technological
University

Mian Lu
A*STAR Institute of HPC,
Singapore

Bingsheng He
Nanyang Technological
University

3
1
0
2

l
u
J

8

]

C
D
.
s
c
[

1
v
5
5
9
1
.
7
0
3
1
:
v
i
X
r
a

ABSTRACT
Query co-processing on graphics processors (GPUs) has be-
come an eﬀective means to improve the performance of main
memory databases. However, the relatively low bandwidth
and high latency of the PCI-e bus are usually bottleneck
issues for co-processing. Recently, coupled CPU-GPU archi-
tectures have received a lot of attention, e.g. AMD APUs
with the CPU and the GPU integrated into a single chip.
That opens up new opportunities for optimizing query co-
processing.
In this paper, we experimentally revisit hash
joins, one of the most important join algorithms for main
memory databases, on a coupled CPU-GPU architecture.
Particularly, we study the ﬁne-grained co-processing mech-
anisms on hash joins with and without partitioning. The
co-processing outlines an interesting design space. We ex-
tend existing cost models to automatically guide decisions
on the design space. Our experimental results on a recent
AMD APU show that (1) the coupled architecture enables
ﬁne-grained co-processing and cache reuses, which are ineﬃ-
cient on discrete CPU-GPU architectures; (2) the cost model
can automatically guide the design and tuning knobs in the
design space; (3) ﬁne-grained co-processing achieves up to
53%, 35% and 28% performance improvement over CPU-
only, GPU-only and conventional CPU-GPU co-processing,
respectively. We believe that the insights and implications
from this study are initial yet important for further research
on query co-processing on coupled CPU-GPU architectures.

1.

INTRODUCTION

Query co-processing on GPUs (or Graphics Processing
Units) have been an eﬀective means to improve the perfor-
mance of main memory databases(e.g., [15, 12, 17, 28, 22,
21]). Compared with CPUs, GPUs have rather high mem-
ory bandwidth and massive thread parallelism, which is ideal
for data parallelism in query processing. Designed as a co-
processor, the GPU is usually connected to the CPU with a
PCI-e bus. So far, most research studies on GPU query co-
processing have been conducted on such discrete CPU-GPU

architectures. The relatively low bandwidth and high la-
tency of the PCI-e bus are usually bottleneck issues [15, 12,
28, 21]. GPU co-processing algorithms have to be carefully
designed so that the overhead of data transfer on PCI-e is
minimized. Recently, hardware vendors have attempted to
resolve this overhead with new architectures. We have seen
integrated chips with coupled CPU-GPU architectures. The
CPU and the GPU are integrated into a single chip, avoid-
ing the costly data transfer via the PCI-e bus. For example,
the AMD APU (Accelerated Processing Unit) architecture
integrates the CPU and the GPU into a single chip, and
Intel released their latest generation Ivy Bridge processor in
late April, 2012. These new heterogeneous architectures po-
tentially open up new optimization opportunities for GPU
query co-processing. Since hash joins have been extensively
studied on both CPUs and GPUs and are one of the most
important join algorithms for main memory databases, this
paper revisits co-processing for hash joins on the coupled
CPU-GPU architecture.

Before exploring the new opportunities by the coupled ar-
chitecture, let us analyze the performance issues of query co-
processing on discrete architectures. A number of hash join
algorithms have been developed for CPU-GPU co-processing
on the discrete architecture [17, 21, 22]. The data transfer
on the PCI-e bus is an inevitable overhead, although it is
feasible to reduce this overhead by overlapping computation
and data transfer. This data transfer leads to coarse-grained
query co-processing schemes. Most studies oﬀ-load the en-
tire join to the GPU, and the CPU is usually under-utilized
during the join process. On the other hand, co-processing
on the discrete architecture under-utilizes the data cache,
because the CPU and the GPU have their own caches. This
prohibits cache reuse among processors to reduce the mem-
ory stall, which is one of the major performance factors for
hash joins [1, 27].

By integrating the CPU and the GPU into the same chip,
the coupled architecture eliminates the data transfer over-
head of the PCI-e bus. Existing query co-processing algo-
rithms (e.g., [21, 22]) can immediately gain this performance
improvement. However, a natural question is whether and
how we can further improve the performance of co-processing
on the coupled architecture. Considering the above-mentioned
performance issues of co-processing on discrete architectures,
we ﬁnd that the two hardware features of the coupled archi-
tecture lead to signiﬁcant implications on the eﬀectiveness
of co-processing.

Firstly, unlike discrete architectures where the CPU and
the GPU have their own memory hierarchy, the CPU and

the GPU in the coupled architecture share the same physical
main memory. Furthermore, they can share some levels of
the cache hierarchy (e.g., the CPU and the GPU in the AMD
APU share the L2 data cache). The CPU and the GPU
can communicate at the memory (or even cache) speed, and
more ﬁne-grained co-processing designs and data sharing are
feasible, which are ineﬃcient on the discrete architecture.

Secondly, due to the limited chip area, the GPU in the
coupled architecture is usually less powerful than the high-
end GPU in discrete architectures (see Table 1 of Section 2).
The GPU in the coupled architecture usually cannot deliver
a dominant performance speedup as it does in discrete archi-
tectures. Therefore, a good co-processing scheme must keep
both processors busy as well as carefully assigning workloads
to them for the maximized speedup.

In this paper, we revisit co-processing schemes for hash
joins on such CPU-GPU coupled architectures. Speciﬁcally,
we examine both hash joins with and without partitioning,
and explore the design space of ﬁne-grained co-processing on
the coupled architecture. Additionally, we consider a series
of design tradeoﬀs such as whether the hash table should
be shared or separated between the two processors as well
as diﬀerent co-processing granularities. We extend existing
cost models to predict the performance of hash joins with
diﬀerent co-processing schemes, and thus guide the decisions
on co-processing design space.

We implement all co-processing schemes of hash joins with
OpenCL on AMD APU A8 3870K. The major experimental
results are summarized as follows.

First, we evaluate the co-processing schemes on the (emu-
lated) discrete architecture in comparison with the coupled
architecture, and show that (1) conventional co-processing
of hash joins [17, 22] can achieve only marginal performance
improvement on the coupled architecture; (2) the coupled
architecture enables ﬁne-grained co-processing and cache reuse
optimizations, which are ineﬃcient/infeasible on discrete ar-
chitectures (Section 5.2).

Second, we evaluate the cost model and show that our
cost model is able to eﬀectively guide the decision on the
optimizations in the design space (Section 5.3).

Third, we evaluate a number of design tradeoﬀs on the
ﬁne-grained co-processing, which are important for the hash
join performance (Section 5.4).

Fourth, we evaluate a number of co-processing variants,
and show that ﬁne-grained co-processing achieves up to 53%,
35% and 28% performance improvement compared with CPU-
only, GPU-only and conventional CPU-GPU co-processing,
respectively (Section 5.5).

To the best of our knowledge, this is the ﬁrst systematic
study of hash join co-processing on the coupled architecture.
We believe that the insights and implications from this study
can shed light on further research of query co-processing on
CPU-GPU coupled architectures.

Organization. The remainder of this paper is organized
as follows.
In Section 2, we brieﬂy introduce background
and related work. In Section 3, we revisit ﬁne-grained CPU-
GPU co-processing schemes for hash joins. The cost model is
described in Section 4. We present the experimental results
in Section 5 and conclude in Section 6.

2. PRELIMINARIES AND RELATED WORK
We ﬁrst introduce CPU-GPU architectures and OpenCL,

and then review the related work on hash joins.

CPU

PCI-e

CPU

GPU

Cache

Cache

Cache

Main Memory

Device Memory

(a) Discrete

Main Memory

(b) Coupled

Figure 1: An overview of discrete and coupled CPU-
GPU architectures

2.1 Coupled CPU-GPU Architecture

GPUs have emerged as promising hardware co-processors
to speedup various applications, such as scientiﬁc comput-
ing [33] and database operations [17]. With massive thread
parallelism and high memory bandwidth, GPUs are suit-
able for applications with massive data parallelism and high
computation intensity.

One hurdle for the eﬀectiveness of CPU-GPU co-processing
is that the GPU is usually connected with the CPU with a
PCI-e bus, as illustrated in Figure 1 (a). On such discrete
architectures, the mismatch between the PCI-e bandwidth
(e.g., 4–8 GB/sec) and CPU/GPU memory bandwidth (e.g.,
dozens to hundreds of GB/sec) can oﬀset the overall perfor-
mance of CPU-GPU co-processing. As a result, it is pre-
ferred to have coarse-grained co-processing to reduce the
data transfer on the PCI-e bus. Moreover, as the GPU
and the CPU have their own memory controllers and caches
(such as L2 data cache), data accesses are in diﬀerent paths.
Recently, vendors have released new coupled CPU-GPU
architectures, such as the AMD APU and Intel Ivy Bridge.
An abstract view of the coupled architecture is illustrated
in Figure 1 (b). The CPU and the GPU are integrated into
the same chip. They can access the same main memory
space, which is managed by a uniﬁed memory controller.
Furthermore, both processors share the L2/L3 data cache,
which potentially increases the cache eﬃciency.

Table 1 gives an overview of AMD APU A8-3870K, which
is used in our study. We also show the speciﬁcation of the
latest AMD GPU (Radeon HD 7970) in discrete architec-
tures for comparison. The GPU in the coupled architecture
has a much smaller number of cores at lower clock frequency,
mainly because of chip area limitations. On current AMD
APUs, the system memory is further divided into two parts,
which are host memory for the CPU and device memory
for the GPU. Both of the two memory spaces can be ac-
cessed by either the GPU or the CPU through the zero copy
buﬀer. This study stores the data in the zero copy buﬀer to
fully take advantage of co-processing capabilities of the cou-
pled architecture. The current zero copy buﬀer is relatively
small, which can be relaxed in the future coupled CPU-GPU
architecture [2].

There have been some studies (like MapReduce [6] and
key-value stores [19]) on the coupled architecture. Most
studies have demonstrated the performance advantage of the
coupled architecture over the CPU-only or the GPU-only al-
gorithm. This study focuses on hash joins, and goes beyond
existing studies [6, 19] in two major aspects. Firstly, we re-
visit the design space of hash joins on the coupled architec-
ture and develop a cost model that can guide the decisions
for co-processing. We conjecture that the design space and
cost models are also applicable to those studies [6, 19]. Sec-

Table 1: Conﬁguration of AMD Fusion A8-3870K.
The last column shows the conﬁguration of AMD
Radeon HD 7970 for reference.

CPU
(APU)

GPU
(APU)

GPU (Dis-
crete)

# Cores

Core frequency(GHz)

4

3.0

400

0.6

Zero copy buﬀer (MB)

512 (shared)

Local memory size(KB)

32

32

Cache size(MB)

4 (shared)

2048

0.9

–

32

–

ondly, we quantitatively show the advantage of co-processing
on the coupled architecture, in comparison with that on the
discrete architecture.

2.2 OpenCL

We develop our co-processing schemes based on OpenCL,
which is speciﬁcally designed for heterogeneous computing.
The advantage of OpenCL is that the same OpenCL code
can run on both the CPU and the GPU without modiﬁ-
cation. A vendor-speciﬁc compiler is employed to optimize
OpenCL to the target architecture. Previous studies (such
as [11, 35]) have shown that implementations with OpenCL
achieve very close performance to those with native lan-
guages such as CUDA and OpenMP on the GPU and the
CPU, respectively.

In OpenCL, the CPU and the GPU can be viewed to have
the same logical architecture, namely compute device. On
the APU, the CPU and the GPU are programmed as two
compute devices. A compute device consists of a number
of Compute Units (CUs). Furthermore, each CU contains
multiple Processing Elements (PEs) running in SIMD style.
The piece of code executed by a speciﬁc device is called
a kernel. A kernel employs multiple work groups for the
execution, and each work group contains a number of work
items. A work group is mapped to a CU, and multiple work
items are executed concurrently on the CU. The execution of
a work group on the target architecture is vendor speciﬁc.
AMD usually executes 64 work items in a wavefront and
NVIDIA with 32 work items in a warp. All work items in
the same wavefront run in the SIMD manner. In this paper,
we use the terminology from AMD.

OpenCL exposes a logical memory hierarchy with three
levels, i.e., global memory, local memory and private mem-
ory. The global memory is accessible to all work items with
high access latency. The small but fast local memory is
shared by all work items within the same work group. Fur-
thermore, the smallest private memory is only accessible to
a work item with the lowest latency. The logical memory
hierarchy is mapped to the physical memory hierarchy of
the target processor by the compiler.

2.3 Architecture-aware Hash Joins

Hash joins are considered as the most eﬃcient join algo-
rithm for main memory databases. Fruitful research eﬀorts
have been devoted to hash joins in the past decades. Re-
searchers have optimized hash join algorithms in two main
categories: for a single hash join [31, 16, 5, 8, 32, 29, 3] and
for a pipeline of hash joins [25, 7]. In this study, we focus on
a single hash join, which can be the basic building block for

a pipeline of hash joins. There are also many studies on par-
allel hash joins on multi-processor environments(e.g.,
[30,
10]). We focus on the related work on modern architectures.
Memory stalls have been a major performance bottleneck
for hash joins in main memory databases [1, 27], because
of random memory accesses. New algorithms (either cache-
conscious [31, 5] or cache-oblivious [16]) have been developed
to exploit data access locality. The other approach [8] is
to hide the memory latency with computation by software
prefetching techniques.

For multi-core CPUs, memory optimizations continue to
be a major research focus. Garcia et al. [13] examined a
pipelined hash join implementation. NUMA memory sys-
tems have also been investigated [34, 24].
In addition to
memory optimizations, there have been studies with architecture-
aware tuning and optimizations. Blanas et al. [4] showed
that synchronization is also an important factor aﬀecting
the overall performance of hash joins on multi-core proces-
sors. Ross [29] proposed a hash join implementation based
on Cuckoo hashing employing branch instruction elimina-
tion and SIMD instructions. Balkesen et al. [3] carefully
evaluated hardware-conscious techniques.

In addition to CPUs, new architectures (e.g., network pro-
cessors [14], cell [29] and GPUs [17, 22]) have also been pro-
posed to improve join performance. Query co-processing on
GPUs has received a lot of attentions. By exploiting the
hardware feature of GPUs, the performance of hash joins
can be signiﬁcantly improved [17, 22]. There have also been
proposals on reducing the PCI-e bus overhead for join co-
processing on the GPU. Kaldewey et al. [21] evaluated the
join processing on NVIDIA GPUs by adopting UVA (Uni-
versal Virtual Addressing). Pirk et al. [28] proposed to ex-
ploit the asymmetric memory channels.

Among various hash join algorithms, there are two basic
forms: simple hash join and partitioned hash join. These
two algorithms have demonstrated very competitive perfor-
mance on multi-core CPUs and GPUs in many previous
studies [4, 22, 17]. Thus, this study will experimentally
revisit both of them on the coupled architecture.

3. HASH JOIN CO-PROCESSING

In the Introduction, we have described the two implica-
tions on the eﬀectiveness of co-processing on the coupled
architecture. On the coupled architecture, co-processing
should be ﬁne-grained, and schedule the workloads carefully
to the CPU and the GPU. Moreover, we need to consider
the memory speciﬁc optimizations for the shared cache ar-
chitecture and memory systems exposed by OpenCL.

We start by deﬁning the ﬁne-grained step deﬁnitions in
hash joins. A step consists of computation or memory ac-
cesses on a set of input or intermediate tuples. Next, we
revisit the design space of co-processing, leading to a num-
ber of hash join variants with and without partitioning. Fi-
nally, we present the implementation details of some design
tradeoﬀs in memory optimizations and OpenCL-related op-
timizations.

3.1 Fine-grained Steps in Hash Joins

A hash join operator works on two input relations, R and
S. We assume that |R| < |S|. A typical hash join algorithm
has three phases: partition, build, and probe. The partition
phase is optional, and the simple hash join does not have
a partition phase. We deﬁne the ﬁne-grained steps for the

simple hash join (SHJ) and the partitioned hash join (PHJ)
in Algorithms 1 and 2, respectively. The granularity of our
step deﬁnition is similar to that in the previous study by
Chen et al. [8]. We will discuss other step deﬁnitions in
Section 3.3.

In SHJ, the build phase constructs an in-memory hash
table for R. Then in the probe phase, for each tuple in S, it
looks up the hash table for matching entries. Both the build
and the probe phases are divided into four steps, b1 to b4 and
p1 to p4, respectively. The simple hash join has poor data
locality if the hash table cannot ﬁt into the cache. However,
a recent study by Blanas et al. [4] showed that SHJ is very
competitive to other complex hash join algorithms on the
multi-core CPUs, especially with data skew.

We adopt the hash table implementation that has been
used in the previous studies [4, 17, 22]. A hash table consists
of an array of bucket headers. Each bucket header contains
two ﬁelds: total number of tuples within that bucket and
the pointer to a key list. The key list contains all the unique
keys with the same hash value, each of which links a rid list
storing the IDs for all tuples with the same key.

Algorithm 1 Fine-grained steps in SHJ

/*build*/
for each tuple in R do

(b1) compute hash bucket number;
(b2) visit the hash bucket header;
(b3) visit the hash key lists and create a key header if neces-
sary;
(b4) insert the record id into the rid list;

/*probe*/
for each tuple in S do

(p1) compute hash bucket number;
(p2) visit the hash bucket header;
(p3) visit the hash key lists;
(p4) visit the matching build tuple to compare keys and pro-
duce output tuple;

Algorithm 2 Fine-grained steps in PHJ
Main Procedure for PHJ:

/*Partitioning: perform multiple passes if necessary*/
Partition (R);
Partition (S);
/*Apply SHJ on each partition pair*/
for each partition pair Ri and Si do

Apply SHJ on Ri and Si;

Procedure: Partition (R)
for each tuple in R do

(n1) compute partition number;
(n2) visit the partition header;
(n3) insert the <key, rid> into partition;

We adopt radix hash join [5] as PHJ in this study.
In
PHJ, it ﬁrst splits the input relations R and S into the
same number of partitions through a radix partitioning al-
gorithm. The radix partitioning is performed by multiple
passes based on a number of lower bits of the integer hash
values. The number of passes is tuned according to the
memory hierarchy (e.g., TLB and data caches). On each
pass of partitioning, the steps are the same, n1 to n3. We
use a structure similar to the hash table to store all the par-
titions, where a bucket is used to store a partition. Next,
PHJ performs SHJ on each partition pair from R and S in
Algorithm 1.

We consider a hash join algorithm with multiple series of
data-parallel steps (namely step series) separated by bar-
riers. For each input data item (e.g., a tuple or larger-
granularity data), it goes through all the steps to generate
the result, and data dependency exists between two consec-
utive steps. We view the step deﬁnition with the granularity
of one tuple as ﬁne-grained ones. That is, we develop co-
processing schemes based on the per-tuple step deﬁnitions
in Algorithms 1 and 2. An SHJ has two step series, b1, ...,
b4 for the build phase and p1, ..., p4 for the probe phase.
There is a barrier between the build and the probe phases.
Similarly, a PHJ with g-pass partitioning has g step series
(n1, ..., n3) plus two step series the same as SHJ for joining
each partition pair.

3.2 Revisiting Co-processing Mechanisms

We revisit the following co-processing mechanisms, which
have their roots in query processing techniques in previous
studies [17, 21, 22]. Particularly, we describe the high-level
idea of each co-processing mechanism and their strengths
and weakness in co-processing on the coupled architecture.
Applying those co-processing schemes to SHJ and PHJ cre-
ates an interesting design space for co-processing on the cou-
pled architecture. Thus, we summarize a number of hash
join variants at the end of this subsection.

In the following description, we consider a general step

series with n steps denoted by s1, ..., sn.

Oﬀ-loading (OL). In the previous study on GPU-accelerated

query processing [17], OL is the major technique to exploit
the GPU. For example, the previous study [17] proposed to
oﬀ-load some heavy operators like joins to the GPU while
other operators in the query remain on the CPU. The basic
idea of OL on a step series is: the GPU is designed as a
powerful massively parallel query co-processor, and a step
is evaluated entirely by either the GPU or the CPU. Query
processing continues on the CPU until the oﬀ-loaded compu-
tation completes on the GPU, and vice versa. That is, given
a step series s1, ..., sn, we need to decide if si is performed
on the CPU or the GPU.

On the discrete architecture, the PCI-e data transfer over-
head is an important consideration for OL. The decision to
oﬀ-load a step aﬀects the decisions on other steps. As a re-
sult, we have to consider 2n possible oﬄoading schemes for
the step series. In contrast, on the coupled architecture, by
eliminating the data transfer overhead, the oﬄoading deci-
sion is relatively simple: depending only on the performance
comparison of running the steps on the CPU and the GPU.
Data dividing (DD). OL could under-utilize the CPU
when the oﬀ-loaded computations are being executed on the
GPU, and vice versa. As the performance gap between the
GPU and the CPU on the coupled architecture is smaller
than that on discrete architectures, we need to keep both
the CPU and the GPU busy to further improve the per-
formance. Thus, the CPU and the GPU work simultane-
ously on the same step. We can model the CPU and the
GPU as two independent processors, and the problem is
to schedule the workload to them. This problem has its
root in parallel query processing [9]. One of the most com-
monly used schemes is to partition the input data among
processors, perform parallel query processing on individual
processors and merge the partial results from individual pro-
cessors as the ﬁnal result. We adopt this scheme to be the
data-dividing co-processing scheme (DD) on the coupled ar-

chitecture. Particularly, given a step series s1, ..., sn, we
need to decide a work ratio for the CPU, r (0 ≤ r ≤ 1) so
that a portion of r of all tuples on the step series are per-
formed on the CPU, and the remainder are performed on
the GPU. If r = 0, DD becomes a CPU-only execution; if
r = 1.0, it becomes a GPU-only execution. To reduce the
amount of the intermediate result, each tuple goes through
all the steps in a pipelined manner in DD.

The advantage of DD is that we can leverage the paral-
lel query processing techniques in parallel databases to keep
both the CPU and the GPU busy. However, DD may still
cause under-utilization of the CPU and the GPU. Consider-
ing the fact that DD uses coarse-grained workload schedul-
ing, some steps assigned to the CPU actually have higher
performance on the GPU, and vice versa. That means, the
workload scheduling has to consider the performance char-
acteristics of the CPU and the GPU, and to perform ﬁne-
grained scheduling for the optimal eﬃciency on individual
processors.

Pipelined execution (PL). To address the limitations
of OL and DD, we consider ﬁne-grained workload schedul-
ing between the CPU and the GPU so that we can capture
their performance diﬀerences in processing the same work-
load. For example, the GPU is much more eﬃcient than the
CPU on b1 and p1 whereas b3 and p3 are more eﬃcient on
the CPU. Meanwhile, we should keep both processors busy.
Therefore, we leverage the concept of pipelined execution
and develop an adaptive ﬁne-grained co-processing scheme
for maximizing the eﬃciency of co-processing on the coupled
architecture.

Unlike DD that has the same workload ratios for all steps,
we consider the data-dividing approach at the granularity of
each step (as illustrated in Figure 2). Within Step si, we
have a ratio ri of the tuples assigned to the CPU and the
remainder (1 − ri) assigned to the GPU. This diﬀers from
DD as we may have diﬀerent workload ratios across steps.
Intermediate results are generated on two consecutive steps
if they have diﬀerent workload ratios. For given workload
ratios, we prefer a longer pipeline (a larger number of steps
that a tuple can go through) to reduce the amount of inter-
mediate results. On the other hand, we need to pay atten-
tion to the data dependency between steps. If the output
data of Step si is not available for Step si+1, Step si+1 has
to be stalled.

To achieve the optimal performance, the suitable work-
load ratios ri (1 ≤ i ≤ n) should adapt to the computa-
tional characteristics of the steps. We have developed a
cost model to evaluate the performance of the pipelined ex-
ecution for the given ratios r1, ..., rn for Steps s1, ..., sn,
respectively. Then, we use a simple approach to obtain the
suitable ratios for the best estimated performance. Speciﬁ-
cally, we consider all the possible ratios at the step of δ for
ri (1 ≤ i ≤ n, 0 ≤ δ ≤ 1), i.e., ri=δ, 2δ, 3δ, ..., ⌊ 1
δ ⌋δ. For
each set of given ratios, we use the cost model to predict the
performance, and thus get the suitable workload ratios. In
our experiments, we use δ = 0.02 as a tradeoﬀ between the
eﬀectiveness and the execution time of optimizations.

We can consider OL and DD as special cases for PL. DD
is equivalent to PL with all the ratios the same on all steps.
OL is equivalent to PL with all the workload ratios being
either zero or one.

The co-processing schemes presented above outline an in-
teresting design space for hash joins on the coupled archi-

input data

t1

t2

t3

t4

t5

t6

...

tm

CPU

GPU

unit
workload

s
t
e
p

s1

s2

s3
s4

Figure 2: Fine-grained co-processing algorithm on a
series of steps.

tecture.
In this experimental study, we focus on evaluat-
ing how those co-processing mechanisms are implemented
in SHJ and PHJ.

We apply DD, OL and PL schemes to SHJ and obtain
three variants (SHJ-DD, SHJ-OL and SHJ-PL, respectively).
For each variant, we consider all bi (1 ≤ i ≤ 4) in the build
phase and all pi (1 ≤ i ≤ 4) in the probe phase as two dif-
ferent step series. There are some tuning parameters, and
we use the cost model presented in the next section to de-
termine their suitable values for the best performance.

Some details of those SHJ variants are described as fol-
lows: (1) SHJ-DD: It decides two workload ratios, rb and
rp, 0 ≤ rb, rp ≤ 1, for the build and the probe phases, re-
spectively. For example, in the build phase, a portion of rb
of the build table are processed by the CPU to construct
the hash table. (2) SHJ-OL: It decides whether each of the
steps (bi in the build phase and pi in the probe phase) is
performed on the CPU or the GPU. (3) SHJ-PL: It deter-
mines the suitable workload ratios for all the steps in the
build and the probe phases.

We apply DD, OL and PL schemes to PHJ and obtain
three variants (PHJ-DD, PHJ-OL and PHJ-PL, respectively).
The idea is the same as the above SHJ variants, except that
we consider the steps in each pass of partitioning as a step
series.

3.3 Implementations and Design Tradeoffs

There are a few design tradeoﬀs in memory optimizations
and OpenCL-related optimizations, which often have signif-
icant impact on the performance of hash joins.

Memory allocator. In the hash join algorithm, dynamic
memory allocations are common, including (1) the output
buﬀer for a partition, (2) allocating a new key in the key
list, and (3) the join result output. Current OpenCL (ver-
sion 1.2) does not support dynamic memory allocation inside
the kernel. The eﬃciency in supporting dynamic memory al-
locations is essential for those operations. Inspired by the
previous study [20], we develop a software dynamic memory
allocator on a pre-allocated array, and memory requests are
dynamically allocated from that array.

A basic implementation of the memory allocator is to use a
single pointer marking the starting address of the free mem-
ory in an pre-allocated array. The pointer initially points to
the starting address of the array. After serving a memory re-
quest, the pointer is moved accordingly. We use the atomic
operation (speciﬁcally atomic add in our study) to imple-
ment a latch for synchronization among multiple requests.
Additionally, the latch is applicable at both the local mem-
ory and the global memory operations. However, this basic
implementation could suﬀer from the contention of atomic
operations, especially for supporting massive thread paral-
lelism on the GPU.

To reduce the contention, we develop an optimized mem-
ory allocator. The memory allocation is at the granularity
of a block. The block size is a tuning parameter and we will
experimentally evaluate its impact in the experiments. The
memory allocator maintains a global pointer. The memory
request is always made by work item 0 (Thread 0) from a
work group, and the global pointer is advanced by one block
size. The memory allocator returns one block to the work
group. The threads within the work group request memory
from the block. It uses a local pointer for synchronization
among the threads within the work group. We allocate the
local pointer in the local memory to reduce the memory ac-
cess overhead. Note, the local memory is accessible to all
the threads within a work group.

The optimized memory allocator resolves the contention
on the GPU. Additionally, the pre-allocation is also bene-
ﬁcial for the CPU. It eliminates many small malloc opera-
tions, and reduces the memory allocation overhead on the
CPU.

Shared vs. separate hash tables. Cache performance
and concurrency are two key factors for the design of hash
tables. An important design choice in the build phase is to
use a shared hash table or separate hash tables for the CPU
and the GPU. Either solution has its own beneﬁts and draw-
backs. A shared hash table has better cache performance,
since the CPU and the GPU share the data cache on the cou-
pled architecture. Additionally, it uses less memory space
in the zero copy buﬀer. On the other hand, separate hash
tables have smaller latch contention between the CPU and
the GPU. We experimentally evaluate these two solutions.
Workload divergence. In OpenCL, all work items in
the same wavefront run simultaneously in a lockstep. The
execution time of a wavefront is equal to the worst execution
time of all work items. Workload divergence among work
items causes severe penalties in the overall performance of
the wavefront. One common source of workload divergence
in hash joins is data skew. For example, data skews cause
workload divergence in b3 in the build phase and p3 in the
probe phase.

To reduce the workload divergence, we adopt a grouping-
based approach in the previous study [18], which is used
to reduce the branch divergence of transaction executions
on the GPU. In order to reduce the workload divergence,
we group the input data according to the amount of work-
load. Using the probe as an example, the input data are the
hash bucket headers given in b2, and the amount of work-
load is represented by the number of keys in the key list.
After grouping, the input data with the similar amount of
workload are grouped together, and the divergence among
the work items in a work group is reduced. The number of
groups is tuned for the tradeoﬀ between the grouping over-
head and the gain of reduced workload divergence.

Step deﬁnitions. So far, we have adopted very ﬁne-
grained step deﬁnitions for co-processing. Ideally, there are
other granularities of deﬁning steps, which can have diﬀerent
memory performance and eﬃciency of co-processing.

We are particularly interested in evaluating the step deﬁ-
nition for PHJ in the previous study [4]. After the partition
phase, we have got P partition pairs on R and S (<Ri, Si>,
0 ≤ i ≤ P − 1). The further join processing on Ri and Si
is performed by one thread. Thus, all the join processing
on the P partition pairs on R and S can be viewed as a
step, and a partition pair is considered to be the input data

Table 2: Notations in the cost model

Notation Description
ri

Workload ratios for the CPU at Step i (1 ≤ i ≤
#Steps)
The number of input items (e.g., tuples) at Step i
(1 ≤ i ≤ #Steps)

Total elapsed time of executing the entire step series
The execution time on the processor XPU (XPU =
{CPU , GPU })
The execution time on the processor XPU at Step i
Computation time at Step i
Total global memory access time at Step i
The pipelined delay at Step i
The average number of instructions on XPU per tuple
in Step i
The peak instruction per cycle on XPU

xi

T

TXPU

XPU

T i
XPU
C i
M i
Di
#I

XPU
i
XPU

XPU

IPC XPU

item to the step. Thus, the granularity for a step for this
co-processing is a SHJ on the partition pair. Note, those
SHJs use separate hash tables, which potentially loses the
opportunities of cache reuse in our ﬁne-grained PHJ vari-
ants.

4. PERFORMANCE MODEL

There are a number of parameters (for example, the ratio
in the data-dividing scheme) to be determined for the co-
processing performance on the coupled architecture. In this
section, we develop a cost model to predict the performance
of hash joins with co-processing on the coupled architecture,
and then use the cost model to determine the suitable values
for the parameters.

Cost models for hash joins have been developed in pre-
vious studies, e.g., on the CPU [5, 26] and the GPU [15].
Those cost models are highly specialized for the target ar-
chitectures and the architecture-speciﬁc query processing al-
gorithms. For example, the cost model for GPU-based co-
processing [15] needs the cost estimation on the PCI-e data
transfer.
In this study, the implementations on the CPU
and the GPU are based on the same OpenCL programs with
diﬀerent input parameters. The CPU and the GPU are ab-
stracted as the same compute device model. Moreover, the
CPU and the GPU share the data cache and the main mem-
ory without the PCI-e bus on the coupled architecture. It
is desirable to have an uniﬁed model to estimate the perfor-
mance of co-processing on both the CPU and the GPU in
terms of both computation and memory latency.

In Section 3, we have identiﬁed PL as a basic abstrac-
tion for hash join co-processing on the coupled architecture
(DD and OL are special cases for PL). This allows us to
abstract the common design issues on the cost model for
diﬀerent co-processing schemes. We call this high level ab-
straction the abstract model. For a speciﬁc co-processing
algorithm, we obtain its cost model by instantiating the ab-
stract model with proﬁling and algorithm-speciﬁc analytic
modelling (e.g., memory optimizations). In the remainder
of this section, we ﬁrst present the abstract model for PL on
the coupled architecture, and next use SHJs as an example
of instantiating the abstract model.

4.1 The Abstract Model

We model the elapsed time of executing a step series with
PL. The step series consists of n steps, with xi input data

items on Step i (1 ≤ i ≤ n). The cost model predicts
the elapsed time of PL with workload ratios ri in Step i.
The parameters are summarized in Table 2 for reference.
Thus, the total elapsed time T is estimated to be the longer
execution time of the CPU and the GPU.

Case 2: If ri < ri−1, we use Eq. 5 to calculate the pipelined

execution delay for the GPU in a similar way to Case 1.

Di

GPU =

i−1

X
j=1

T j
CPU − (

i

X
j=1

GPU − T i
T j

GPU ×

1 − ri−1
1 − ri

)

(5)

T = max(TXPU ), XPU = {CPU , GPU }

(1)

On each processor, we estimate the execution time to be
the total execution time of all steps in the step series. The
execution time of Step i (T i
XPU ) is further estimated in three
parts: computation time C i
XPU , global memory access time
M i

XPU and the pipelined delay Di

XPU .

TXPU =

n

X
i=1

T i

XPU =

n

(C i

XPU + M i

XPU + Di

XPU )

X
i=1

(2)

We describe the estimation of each component accordingly.
We estimate the computation time to be the total exe-
cution time for all the instructions of the step. We assume
an ideal execution pipeline with the optimal IPC on each
processor, and a hash join on uniform data distributions.

C i

XPU =

#I i

XPU × ri × xi
IPC XPU

(3)

To estimate the memory stalls, we adopt a traditional
calibration method for the CPU [26] and for the GPU [15],
which can estimate the memory stall cost per data item
in each step. The basic idea is to measure the memory
stall cost, by excluding the caching eﬀects and the thread
parallelism. It is suitable to estimate the memory stall costs
for both random and sequential accesses. For details on
the calibrations and models, we refer readers to the original
paper [15, 26]. For diﬀerent steps, we have instantiated the
model with the consideration of their access patterns.

For Di

XPU , this delay is caused by diﬀerent workload ra-
tios in the two consecutive steps. Due to data dependency
between the two processors, one processor has to synchro-
nize with the other one on Step i if the workload ratios are
diﬀerent on Steps i and (i − 1). The delay occurs when
the input data for Step i have not been generated from Step
(i−1). There are two cases depending on the workload ratio
comparison.
Case 1:

if ri > ri−1, we use Eq. 4. The CPU may en-
counter delay while the GPU prepares the input data in
Step (i − 1) for the CPU in Step i. The ratio of the GPU
time that is not pipelined with the CPU in Step (i − 1) is
1−ri
1−ri−1 . By subtracting this amount of time (T i−1
1−ri−1 )
from the total GPU time from Step 1 to Step i − 1, we get
the time of the GPU from Step 1 to the end of the pipelined
execution area in Step i − 1. The total CPU time from Step
1 to the end of pipelined execution area with the GPU in

GP U × 1−ri

Step i is

i
P
j=1

T j
CPU . Therefore, Di

CP U is the delay time on

the CPU to wait for data generated from the GPU in Step
i − 1, as in Eq. 4. Naturally, if Di
CP U ≤ 0, it is set as 0,
meaning there will be no pipelined execution delay.

Di

CPU = (

i−1

X
j=1

GPU − T i−1
T j

GP U ×

1 − ri
1 − ri−1

) −

i

X
j=1

T j
CPU

(4)

Finally, as speciﬁc to the pipelined co-processing, we need
to estimate the cost of intermediate results and the commu-
nication cost between the CPU and the GPU. We estimate
the cost for two consecutive steps.
If they have the same
workload ratio, we can ignore the costs on intermediate re-
sults and the communication. Otherwise, the amount of in-
termediate results can be derived from the diﬀerence of the
workload ratio between the two steps. For Step i, the num-
ber of intermediate data items is (ri − ri−1) × xi, assuming
a uniform distribution.

4.2 Model Instantiation

We use SHJs as an example to illustrate the model instan-
tiation. We consider ﬁne-grained co-processing SHJ variants
(with the granularity of tuples).

For computation time, the optimal IPC value can be ob-
tained from the hardware speciﬁcation. The number of in-
structions for per tuple in each step can be obtained from
proﬁling tools such as AMD CodeXL and AMD APP Pro-
ﬁler. One issue to handle is that the number of instructions
per tuple in some steps varies with the workload. For ex-
ample, the costs of b3 and p3 depend on the length of the
key list. Therefore, we use the number of instructions per
key search as the unit cost for that step, and estimate the
number of instructions of the step to be the number of in-
structions per key search multiplied by the average number
of keys in the key list.

Next, we calibrate the memory unit cost per tuple with the
calibration method [15]. For some steps, the memory unit
cost is workload-dependent. We adopt the same approach
as proﬁling the number of instructions discussed above.

Given the above calibrations, we can derive the total cost
for diﬀerent SHJ variants. Here, we use SHJ-DD as an ex-
ample, and we can derive the cost for other variants simi-
larly. We estimate the performance of SHJ-DD as the total
elapsed time of the build phase and the probe phase. Since
the estimation of the build phase is similar to the probe
phase, we estimate the build phase as follows. We instanti-
ate Eqs. 1–5. In Eq. 2, we set n = 4, because there are four
steps in the build phase. In Eq. 3, the number of instruc-
tions is substituted with the proﬁled result from each step.
We then use the calibrated values for each step to get the
memory costs, and determine the pipelined execution delay
in Eqs. 4 and 5. Thus, we can get the cost for the build
phase in Eq. 1.

5. EVALUATION

In section, we experimentally evaluate the co-processing
scheme for the hash join on the coupled CPU-GPU architec-
ture. Overall, there are four groups of experiments. Firstly,
we investigate the overhead of data transfers and other op-
erations of co-processing for the hash join on a discrete
CPU-GPU architecture (Section 5.2). Secondly, we eval-
uate the accuracy of our cost model (Section 5.3). Thirdly,
we study the performance impact of the design tradeoﬀs in
co-processing of hash joins (Section 5.4). Finally, we show
the end-to-end performance comparison (Section 5.5).

5.1 Experimental Setup

Hardware conﬁguration. We conduct our experiments
on a PC equipped with an AMD APU A8-3870K. The hard-
ware speciﬁcation has been summarized in Table 1.

Data sets. We use the same synthetic data sets as the
previous study [4] to evaluate our implementations. Both re-
lations R and S consist of two four-byte integer attributes,
namely the record ID and key value. Our default data set
size is 16 million tuples with uniform-distributed key values
for both relations R and S, unless speciﬁed otherwise. Both
R and S can be considered as basic relations (without com-
pression) in column-oriented databases, or the intermediate
relations by extracting the key and record ID from much
larger relations in row-oriented databases. We experimen-
tally evaluate the impact of diﬀerent data sizes. In addition
to uniform data sets, we also use skewed data sets and vary
the selectivity to show the overall performance comparisons.
We created two skewed datasets with s% of tuples with one
low-skew with s = 10 and high-skew
duplicate key values:
with s = 25.

Implementation details. We develop all hash join vari-
ants using OpenCL 1.2. The OpenCL conﬁguration includ-
ing work groups and work items has been tuned to fully
utilize the CPU and the GPU capabilities. In addition to
co-processing, we also implement CPU-only and GPU-only
algorithms. Our implementations have adopted the com-
mon practice in the previous implementations [17, 4, 5]. For
example, we choose the hash function MurmurHash 2.0 that
is also used in the previous study [4], which has a good hash
collision rate and low computational overhead.

We compare the discrete and the coupled architectures to
investigate the performance issues of discrete architectures.
For a fair comparison, we should ideally use the CPU and
the GPU that have exactly the same architectures as those
in the coupled architecture. However, this may be not al-
ways feasible as the coupled architecture advances. Instead,
we use the CPU and the GPU on the coupled architecture to
emulate the CPU and the GPU on a discrete architecture,
and emulate the PCI-e bus data transfer with a delay. This
simulation-based approach allows us to evaluate the impact
of diﬀerent processors and PCI-e bus. Unlike real discrete
architectures, the CPU and the GPU in the emulated ar-
chitecture still share the cache. In our experiment, we ﬁnd
that the emulated approach is able to help us to understand
the performance issues of the discrete architecture. The de-
lay of one data transfer on PCI-e bus is estimated to be
latency + size
bandwidth , where size is the data size and latency
and bandwidth are the latency and bandwidth of the PCI-e
bus, respectively. In our study, we emulate a PCI-e bus with
latency = 0.015 ms and bandwidth = 3 GB/sec.

On the emulated discrete architecture, we can implement
all the hash join variants except PL. Using SHJ-DD as an
example, in the build phase, a part of the build table is trans-
ferred to the GPU memory before the GPU starts building
hash tables. An estimated delay is added so that the GPU
starts the build phase later. When the build phase is done,
the partial hash table is transferred back to the CPU for
a merge operation. The probe phase has a similar process
to the build phase. For PL, it is ineﬃcient to implement
the ﬁne-grained co-processing on the discrete architecture
for two reasons. Firstly, there are much more memory data
transfers by exchanging the intermediate results between the
CPU and the GPU. Secondly, the data dependency control

logic on the GPU memory is diﬃcult to implement on the
PCI-e bus. Thus, we use the execution of PL on the coupled
architecture to analyse the impact of PL on the discrete ar-
chitecture, including intermediate results and eﬃciency of
pipelined execution.

5.2 Evaluations on Discrete Architectures

data-transfer

merge

partition

build

probe

)
.
c
e
s
(
e
m

i
t
d
e
s
p
a
E

l

3.5

3

2.5

2

1.5

1

0.5

0

discrete coupled
SHJ-DD

discrete coupled
SHJ-OL

discrete coupled
PHJ-DD

discrete coupled
PHJ-OL

Figure 3: Time breakdown on discrete and coupled
architectures

Data transfer and merge overhead. We ﬁrst study
the time breakdown of hash join variants on the discrete
architecture. For comparison, we also show the time break-
down on the coupled architecture. Figure 3 shows the time
breakdown for the data dividing and oﬀ-loading co-processing
schemes. On the discrete architecture, the workload ra-
tios for the build and probe phases for SHJ-DD are 25%
and 42%, respectively; the workload ratios for the partition,
build and probe phases for PHJ-DD are 11%, 26% and 41%,
respectively. We can see that the suitable workload ratios
vary across diﬀerent phases. SHJ-OL and PHJ-OL have de-
graded to be GPU-only, because all the steps on the GPU
are faster than those on the CPU (as we will discussed later).
On the discrete architecture, co-processing usually requires
explicit data transfer on the PCI-e bus and the merge oper-
ation. In the experiments, DD has both kinds of overhead
and OL has only the data transfer overhead because OL is
essentially GPU-only. Overall, the PCI-e data transfer over-
head is 4–10% of the overall execution time. PHJ generally
has higher data transfer overhead, since it has one more
phase than SHJ. In comparison, this data transfer overhead
is eliminated on the coupled CPU-GPU architecture.

The merging operation usually creates a more signiﬁcant
overhead than the data transfer on PCI-e bus (14% and
18% of the overall time in SHJ-DD and PHJ-DD, respec-
tively). While the data transfer overhead on the PCI-e bus
can be reduced with advanced overlapping of computation
and data transfer, the merge overhead is inherent to DD on
the discrete architecture. In comparison, on the coupled ar-
chitecture, DD uses a shared hash table (as we evaluate in
Section 5.4), and the merge overhead is eliminated.

Workload ratios in DD. We study the workload ratios
on two diﬀerent architectures (Figures are omitted due to
space limits). Generally, we ﬁnd that the suitable workload
ratios of the CPU on the discrete architectures are higher
than those on the coupled architecture. During the data
transfer, the CPU can do more useful work for DD. Since
the data transfer accounts for 4–10% of the total execution
time, the diﬀerence is small (smaller than 5%).

GPU and CPU processing capabilities for diﬀer-
ent steps. In order to achieve the eﬃciency of employing
ﬁne-grained co-processing, we need to understand the pro-
cessing performance of each step on the CPU and the GPU.
We measure the performance of each step on the CPU-only

CPU

GPU

)
s
n
(
e
p
u
t

l

r
e
p
e
m

i
t
d
e
s
p
a
E

l

25

20

15

10

5

0

n1

n2

n3

b1

b2

b3

b4

p1

p2

p3

p4

Partition

Build

Probe

Figure 4: Unit costs for diﬀerent steps on the CPU
and the GPU for PHJ

CPU

0%

4%

60%

22%

GPU

100%

96%

40%

78%

b1

b2

b3

b4

CPU

0%

4%

5(cid:0)(cid:1)

99%

p1

p2

p3

p4

GPU

100%

96%

47%

1%

(a) build in SHJ

(b) probe in SHJ

Figure 5: Optimal workload ratios of diﬀerent steps
for SHJ-PL on the coupled architecture

and the GPU-only algorithms. Figure 4 shows the aver-
age processing time per tuple for diﬀerent steps in PHJ on
the CPU and the GPU. We have observed similar results
on SHJ. Overall, the hash value computation can greatly
beneﬁt from the GPU acceleration due to its massive data
parallelism and computation intensity. Therefore, the GPU
can accelerate the hash value computation based steps (i.e.,
n1, b1, and p1) by more than 15X. Instead, some other oper-
ations, such as b3 or p3, cannot match the GPU architecture
features, because of random memory accesses and divergent
branches. As a result, the GPU and the CPU have very
close performance on those steps. Since diﬀerent steps may
have diﬀerent performance comparison on the CPU and the
GPU, this conﬁrms that a ﬁne-grained co-processing algo-
rithm is essential to better exploit the strength of the CPU
and the GPU. Workloads of diﬀerent steps should be care-
fully assigned to suitable compute devices. That leads to
our further analysis of PL.

Analyzing PL. We analyze the workload ratios of diﬀer-
ent steps for PL on the coupled architecture to understand
the impact of intermediate results and eﬃciency of pipelined
execution. Figures 5 and 6 show the optimal workload ra-
tios of diﬀerent steps in SHJ-PL and PHJ-PL on the coupled
architecture, respectively. Overall, the optimal workload ra-
tios are varied across diﬀerent steps. The GPU can take all
workload (b1 in Figure 5(a) and p1 in Figure 5(b)), or takes
only a very small portion of workload (1% for p4 in Figure
5(b)). We have the following two implications.

Firstly, PL can be ineﬃcient on the discrete architecture,
since the signiﬁcant diﬀerence in the workload ratios among
the steps creates signiﬁcant overhead in data transfer and

CPU

3(cid:3)

47%

GPU

CPU

2%

7%

97%

(cid:2)3(cid:3)

(cid:4)(cid:5)(cid:6)

6(cid:2)(cid:3)

91%

n1

n2

n3

 b1

 b2

 b3

 b4

CPU

(cid:7)(cid:8)

11%

64%

GPU

98%

93%

44%

9%

GPU

p1

(cid:9)(cid:7)(cid:8)

p(cid:10)

p

(cid:11)

8(cid:9)(cid:8)

36%

p

(cid:12)

1(cid:7)(cid:8)

3(cid:2)(cid:3)

8(cid:7)(cid:8)

(a) partition in PHJ

(b) build in PHJ

(c) probe in PHJ

Figure 6: Optimal workload ratios of diﬀerent steps
for PHJ-PL on the coupled architecture

5
4
3
2
1
0

)
s
(
e
m

i
t
d
e
s
p
a

l
E

estimated

measured

estimated

measured

4

3

2

1

0

)
s
(
e
m

i
t
d
e
s
p
a

l
E

0  10  20  30  40  50  60  70  80  90 100
Workload ratio of build (%)

0  10  20  30  40  50  60  70  80  90 100

Workload ratio of probe (%)

(a) build

(b) probe

Figure 7: Estimated and measured time for SHJ-DD
with workload ratios varied

estimated

measured

4

3

2

1

0

)
s
(
e
m

i
t
d
e
s
p
a

l
E

3

2

1

0

)
s
(
e
m

i
t
d
e
s
p
a

l
E

estimated

measured

0  10  20  30  40  50  60  70  80  90 100
Workload ratio of build (%)

0  10  20  30  40  50  60  70  80  90 100

Workload ratio of probe (%)

(a) build

(b) probe

Figure 8: Estimated and measured time for a special
case for PL: oﬄoading entire b1 and p1 to the GPU,
and applying data-dividing with the same ratio r to
all the other steps. The results are measured by
varying r.

pipeline execution. Recall that, in PL, the workload ra-
tio diﬀerence between two consecutive steps determines the
amount of intermediate results. We use the grey area in the
ﬁgures to indicate the intermediate results to be generated
during the execution of PL. For example, in Figure 5, the
CPU only takes 4% workload for b2, but takes 60% for b3.
That requires a transfer of 56% of the output data of b2 on
the PCI-e bus, if PL runs on the discrete architecture. On
the other hand, the overhead of pipelined execution is not
shown in the ﬁgure. The diﬀerence in the workload ratios re-
sults in diﬀerent lengths of pipelines in the execution, which
results in workload divergence.

The other implication is that, since the optimal workload
ratios vary for diﬀerent steps, the conventional approach (by
oﬄoading the entire join to the GPU) cannot fully exploit
the co-processing capabilities from both the CPU and the
GPU.

5.3 Cost Model Evaluation

Overall, our cost model can accurately predict the perfor-
mance of all hash join variants with diﬀerent tuning param-
eters, and thus can guide the decision of getting the suitable
value. Since the results are similar for both SHJs and PHJs,
we focus of the results on SHJs.

Figure 7 compares the estimated performance with mea-
sured performance for SHJ-DD with the workload ratios var-
ied. The black solid squares in the ﬁgures denote the op-
timal points. It shows that our estimated time is close to
the measured time. However, the estimated time is slightly
lower than the measured time. One factor to consider is that
our cost model does not include the estimation of the lock
contention overhead.

PL has a large design space. In general, our estimation can
closely predict the performance of PL with diﬀerent work-
load ratios. For clarity of presentation, we consider a special
case for PL: oﬄoading the entire b1 and p1 to the GPU, and
applying data-dividing with the same ratio r to all the other

s
e
c
n
a
t
s
n

i

f
o
F
D
C

100%

80%

60%

40%

20%

0%

Ours

s
e
c
n
a
t
s
n

i

f
o
F
D
C

100%

80%

60%

40%

20%

0%

Ours

5
6
0

.

.

7
0

.

8
0

5
7
0

.

5
8
0

.

.

9
0

5 1
9
0

.

5
0
1

.

.

1
1

.

2
1

5
1
1

.

5
2
1

.

e
r
o
M

5
3
0

.

8
3
0

.

1
4
0

.

4
4
0

.

7
4
0

.

.

5
0

3
5
0

.

6
5
0

.

9
5
0

.

2
6
0

.

5
6
0

.

8
6
0

.

e
r
o
M

Build time in SHJ-PL (s)

Probe time in PHJ-PL (s)

(a) build of SHJ-PL

(b) probe of PHJ-PL

Figure 9: CDF of SHJ-PL (build) and PHJ-PL
(probe) with one thousand Monte Carlo simulations

separate hash table
shared hash table

)
s
(
e
m

i
t
d
e
s
p
a

l
E

1.8
1.6
1.4
1.2
1
0.8
0.6
0.4
0.2
0

Simple hash join

Partitioned hash join

Figure 10: Elapsed time of the build phase in DD
with separate and shared hash tables

steps. The results in Figure 8 are measured by varying r.
In this special case of PL, we see that our prediction is close
to the performance varying r and also is able to predict its
suitable value.

To evaluate our cost model in more details, we perform
experiments with Monte Carlo simulations on the workload
ratios. Each simulation runs a PL with randomly generated
ratio settings. Figure 9 demonstrates the cumulative dis-
tribution function (CDF) for the elapsed time of the build
phase of SHJ-PL and the probe phase of PHJ-PL with one
thousand simulation runs. We also highlight the elapsed
time of our approach given by the cost model. The pro-
posed approach is very close to the best performance of the
Monte Carlo simulations. For each simulation run, we evalu-
ate the prediction by our model and the measured execution
time. The diﬀerence is smaller than 15% in most cases.

5.4 Design Tradeoffs on Coupled CPU-GPU

Architectures

We evaluate the impact of each tradeoﬀ by varying the
setting of that tradeoﬀ while other tradeoﬀs have already
been tuned. Based on them, we optimize the performance
of the hash join variants on the target coupled architecture.
Separate vs. shared hash table. We ﬁrst show the
elapsed time of build phase of DD with separate and shared
hash tables, as shown in Figure 10. SHJ-DD and PHJ-DD
with a shared hash table outperform those with separate
hash tables by 16% and 26%, respectively. The major ben-
eﬁt of adopting the shared hash table is the elimination of
the merging operation (as we have seen in Section 5.2). The
other beneﬁt is the improved cache performance due to po-
tential cache reuse on the coupled architecture. The num-
bers of cache misses of SHJ-DD and PHJ-DD with separate
hash tables are 2% and 4% larger than those with shared
hash table, respectively. The improvement shows that, on
the tested coupled architecture, the concurrency overhead
of the shared hash table is compensated by the two major
beneﬁts over the separate hash table.

Optimized memory allocator. We adopt an optimized

4

3

2

1

0

)
s
(
e
m

i
t
d
e
s
p
a

l
E

PHJ-DD

PHJ-OL

PHJ-PL

8

6
1

2
3

4
6

8
2
1

6
5
2

2
1
5

K
1

K
2

K
4

K
8

K
6
1

K
2
3

Allocation block size (Byte)

PHJ-DD

PHJ-OL

PHJ-PL

1

0.8

0.6

0.4

0.2

0

)
s
(
d
a
e
h
r
e
v
o
k
c
o
L

8

6
1

2
3

4
6

8
2
1

6
5
2

2
1
5

K
1

K
2

K
4

K
8

K
6
1

K
2
3

Allocation block size (Bytes)

(a) Elapsed time (sec.)

(b) Lock overhead

Figure 11: Elapsed time (left) and lock overhead
(right) of PHJ

Basic

Ours

Basic

Ours

)
s
(
e
m

i
t
d
e
s
p
a
l
E

4

3

2

1

0

)
s
(
e
m

i
t
d
e
s
p
a
l
E

4

3

2

1

0

SHJ-DD

SHJ-OL
(a) SHJ

SHJ-PL

PHJ-DD

PHJ-OL
(b) PHJ

PHJ-PL

Figure 12: Comparison between basic and optimized
memory allocators (Basic and Ours, respectively)

memory allocator to reduce the number of atomic opera-
tions. Figure 11(a) shows the overall time with the memory
allocation block size varied in PHJ. We observed similar re-
sults on SHJ. Overall, at the beginning, the performance
keeps improving when the block size becomes larger. How-
ever, the performance remains stable when the block size is
larger than 2KB. The suitable block size is set to 2KB in
our experiments. The major reason of the performance im-
provement is the reduction of global memory lock overhead
from atomic operations.

To conﬁrm our conclusion, we further study the lock over-
head with the block size varied in Figure 11(b) for PHJ.
So far, there is no proﬁling tool to measure the lock over-
head directly on the hardware. Therefore, we estimate the
lock overhead as the diﬀerence of the measured time and
estimated time based on our cost model. This is because
our cost model does not consider the lock overhead. This
back-of-the-envelop approach is simplistic but suﬃcient to
show the trend of the lock overhead for our purpose. As the
allocation memory block size increases, the lock overhead
decreases signiﬁcantly for all hash join variants.

Figure 12 compares the performance of hash joins with the
basic memory allocator and our optimized memory allocator
(denoted as Basic and Ours, respectively). Compared with
the Basic allocator, the optimized allocator signiﬁcantly im-
proves the hash join performance, with up to 36% and 39%
improvement on SHJ and PHJ.

Workload divergence. We study the impact of group-
ing approach on reducing the workload divergence. Our ex-
perimental results show that, the grouping approach can im-
prove the overall performance by 5–10% (Figures are omit-
ted due to space interests). The impact on the GPU is larger
than that on the CPU, because the GPU hardware executes
the wavefront strictly in a SIMD manner and also does not
have advanced branch prediction mechanisms like the CPU.
Fine-grained step deﬁnition. We study the CPU and
the GPU running time for hash joins employing the ﬁne-
grained and coarse-grained step deﬁnition. We apply PL to
the coarse-grained step deﬁnition that we discussed in Sec-

CPU-only

PHJ-DD

PHJ-OL

PHJ-PL

)
s
(
e
m

i
t
d
e
s
p
a

l
E

3.5

3

2.5

2

1.5

1

0.5

0

CPU-only

SHJ-DD

SHJ-OL

SHJ-PL

)
s
(
e
m

i
t
d
e
s
p
a

l
E

3.5

3

2.5

2

1.5

1

0.5

0

K
4
6

K
8
2
1

K
6
5
2

K
2
1
5

M
1

M
2

M
4

M
6

M
8

M
0
1

M
2
1

M
4
1

M
6
1

K
4
6

K
8
2
1

K
6
5
2

K
2
1
5

M
1

M
2

M
4

M
6

M
8

M
0
1

M
2
1

M
4
1

M
6
1

Size of build table
(a) SHJ

Size of build table
(b) PHJ

Figure 13: Elapsed time comparison on the uniform
data set

CPU-only

PHJ-DD

PHJ-OL

PHJ-PL

CPU-only

SHJ-DD

SHJ-OL

SHJ-PL

)
s
(
e
m

i
t
d
e
s
p
a

l
E

3.5

3

2.5

2

1.5

1

0.5

0

)
s
(
e
m

i
t
d
e
s
p
a

l
E

3.5

3

2.5

2

1.5

1

0.5

0

K
4
6

K
8
2
1

K
6
5
2

K
2
1
5

M
1

M
2

M
4

M
6

M
8

M
0
1

M
2
1

M
4
1

M
6
1

K
4
6

K
8
2
1

K
6
5
2

K
2
1
5

M
1

M
2

M
4

M
6

M
8

M
0
1

M
2
1

M
4
1

M
6
1

Size of build table
(a) SHJ

Size of build table

(b) PHJ

Figure 14: Elapsed time comparison on the high-
skew data set

tion 3.3, and denote this co-processing to be PHJ-PL’. Table
3 shows the execution time and the cache performance of
PHJ-PL and PHJ-PL’. PHJ-PL’ is much slower than PHJ-
PL. As the coarse-grained step deﬁnition introduces separate
hash tables, PHJ-PL’ has a larger number of cache misses
and a higher cache miss ratio than PHJ-PL. This shows the
advantage of co-processing with ﬁne-grained steps.

Table 3: Comparison between ﬁne-grained and
coarse-grained step deﬁnitions in PL
L2 cache misses
(×106)
7

L2 cache miss
ratio

Time (s)

PHJ-PL

10%

1.6

PHJ-PL’

15

23%

2.2

5.5 End-to-End Performance Comparison

In this section, we compare end-to-end performance for
diﬀerent hash join variants on the coupled architecture. The
OL essentially is a GPU-only implementation, and thus the
results for GPU-only are omitted.

Data skew and data size. We ﬁrst show performance
numbers on the uniform, low-skew and high-skew data sets.
We ﬁx the probe relation to 16 million tuples and vary the
build relation from 64K to 16M tuples. Figures 13 and 14
show the comparison results for uniform and high-skew data
sets, respectively. The ﬁgures for the low-skew data sets are
omitted due to the space limits, and we describe the results
in texts. In general, they have similar performance trends
on all three data sets. It shows that our co-processing tech-
niques work well on either uniform or skew data sets. The
elapsed time of running on high-skew data can be actually
comparable to or even lower than that on uniform data. This
is mainly because the beneﬁt of data locality in high-skew
data compensates the overhead of latches. This point has
also been pointed out in the previous study [4]. We have
also observed that when the relation size exceeds the cache

Partition

Build

Probe

)
s
(
e
m

i
t
d
e
s
p
a

l
E

3

2.5

2

1.5

1

0.5

0

DD  OL

PL

DD  OL

PL

DD  OL

PL

12.5%

50.0%

100%

Join selectivity

Figure 15: PHJ with join selectivity varied

size (4MB), there is a leap in the running time. Addition-
ally, the performance improvement also scales well with the
build relation size. In most cases, exploiting the capabili-
ties of the both the GPU and the CPU (DD and Pipelined)
can generate better performance than using only the CPU
(CPU-only) or GPU-only (OL). Speciﬁcally, the optimized
ﬁne-grained pipelined join outperforms the CPU-only and
GPU-only implementations by up to 53% and 35%, respec-
tively. Thus, it is important to exploit both the CPU and
the GPU on the coupled architecture. Additionally, PL out-
performs DD by up to 28%. This conﬁrms the eﬀectiveness
of our optimizations on ﬁne-grained co-processing.

Join selectivity. We study the impact of join selectivity.
Figure 15 shows the results on time breakdown for the join
selectivity values of 12.5%, 50% and 100%. For DD and
OL, the selectivity only aﬀects the probe phase. As a result,
the time for the probe phase becomes slightly longer when
the selectivity increases from 12.5 % to 100% for DD (from
0.47 to 0.58 seconds) or OL (from 0.59 to 0.71 seconds).
For PL, both the build and probe phases are aﬀected by
the join selectivity. However, the performance impact is
marginal, because our implementation simply outputs the
matching rid pair. When the selectivity increases, there
are more chances for workload divergence when probing the
hash table.

After studying all hash join variants, we ﬁnd that PHJ-
PL is usually the fastest, which is 2–6% faster than SHJ-PL.
Nevertheless, both SHJ-PL and PHJ-PL are very competi-
tive on the coupled architecture on diﬀerent data sets.

5.6 Summary and Lessons Learnt

We summarize the major ﬁndings and lessons learnt from
this study and their implications for developing an eﬃcient
query processor on the coupled architecture.

Firstly, conventional co-processing of hash joins [17, 22]
can achieve only marginal performance improvement on the
coupled architecture, since only the data transfer overhead
is eliminated (accounting for 4–10% of the total execution
time). This calls for the use of ﬁne-grained co-processing
on the coupled architecture, instead of coarse-grained co-
processing in the previous studies [15, 12, 17]. Moreover,
ﬁne-grained co-processing schemes are ineﬃcient on the dis-
crete architecture. It indicates that “one size does not ﬁt
all”, and we need to adopt diﬀerent co-processing schemes
between discrete and coupled architectures.

Secondly, ﬁne-grained co-processing on hash joins has an
interesting design space. It further increases the number of
tuning knobs for hash joins. Automaticity of optimization
is feasible which is enabled by our cost model. Going be-
yond hash joins, we believe that the automaticity could be
achieved through integrating the awareness of ﬁne-grained
co-processing into query optimizations.

Thirdly, memory optimizations and OpenCL-related opti-
mizations have signiﬁcant impact on the overall performance
of hash join co-processing. Traditional issues like shared vs.
separate hash tables remain important on the coupled archi-
tecture. More generally, architecture-aware query process-
ing techniques (e.g., [3, 29]) are still relevant to performance
optimizations. But their impacts should be carefully studied
on the target coupled architecture.

Fourthly, ﬁne-grained co-processing is a must on the cou-
pled architecture, which signiﬁcantly outperforms the per-
formance of processing on a single processor and the conven-
tional co-processing. It not only keeps both processors busy,
but also assigns the suitable workload to them for eﬃciency.
The design space applies to general query processing, and
an eﬃcient query processor should expose suﬃciently ﬁne-
grained data parallelism for scheduling among diﬀerent pro-
cessors. Additionally, we conjecture that the design space of
co-processing in this study is relevant to not only the cou-
pled CPU-GPU architectures but also other heterogeneous
architectures [23].

6. CONCLUSION

While GPU co-processing has shown signiﬁcant perfor-
mance speedups on main memory databases, the discrete
CPU-GPU architecture design has hindered the further per-
formance improvement of GPU co-processing. This paper
revisits co-processing for hash joins on the coupled CPU-
GPU architecture. With the integration of the CPU and
the GPU into a single chip, the data transfer via PCI-e
bus is eliminated on the coupled architecture. More im-
portantly, the coupled architecture has opened up vast op-
portunities for improving the performance of co-processing
of hash joins, as we have demonstrated in this experimen-
tal study. Speciﬁcally, we revisit the design space of ﬁne-
grained co-processing on hash joins with and without par-
titioning. We show that the ﬁne-grained co-processing can
improve the performance by up to 53%, 35% and 28% over
the CPU-only, GPU-only and conventional CPU-GPU co-
processing, respectively. This paper represents a key ﬁrst
step in designing eﬃcient query co-processing on coupled
architectures. We are developing a full-ﬂedged query pro-
cessor on the coupled architecture [36].

7. ACKNOWLEDGEMENT

The authors would like to thank anonymous reviewers,
Qiong Luo and Ong Zhong Liang for their valuable com-
ments. This work is partly supported by a MoE AcRF Tier
2 grant (MOE2012-T2-2-067) in Singapore and an Inter-
disciplinary Strategic Competitive Fund of Nanyang Tech-
nological University 2011 for “C3: Cloud-Assisted Green
Computing at NTU Campus”.

8. REFERENCES
[1] A. Ailamaki, D. J. DeWitt, M. D. Hill, and D. A. Wood. Dbmss

on a modern processor: Where does time go? In VLDB, 1999.

[2] AMD Corp.

http://amddevcentral.com/afds/pages/default.aspx.

[3] C. Balkesen, J. Teubner, G. Alonso, and M. T. Oszu.

Main-memory hash joins on multi-core cpus: tunning to the
underlying hardware. In ICDE, 2013.

[4] S. Blanas, Y. Li, and J. M. Patel. Design and evaluation of

main memory hash join algorithms for multi-core cpus. In
SIGMOD, pages 37–48, 2011.

[5] P. A. Boncz, S. Manegold, and M. L. Kersten. Database

architecture optimized for the new bottleneck: Memory access.
In VLDB, 1999.

[6] L. Chen, X. Huo, and G. Agrawal. Accelerating mapreduce on
a coupled cpu-gpu architecture. In SC, pages 25:1–25:11, 2012.

[7] M.-S. Chen, M.-L. Lo, P. S. Yu, and H. C. Young. Using

segmented right-deep trees for the execution of pipelined hash
joins. In VLDB, pages 15–26, 1992.

[8] S. Chen, A. Ailamaki, P. B. Gibbons, and T. C. Mowry.

Improving hash join performance through prefetching. ACM
Trans. Database Syst., 2007.

[9] D. DeWitt and J. Gray. Parallel database systems: the future
of high performance database systems. Commun. ACM, 1992.

[10] D. J. DeWitt and R. H. Gerber. Multiprocessor hash-based join

algorithms. In VLDB, pages 151–164, 1985.

[11] J. Fang, A. L. Varbanescu, and H. Sips. A comprehensive

performance comparison of cuda and opencl. In ICPP, 2011.
[12] W. Fang, B. He, and Q. Luo. Database compression on graphics

processors. Proc. VLDB Endow., pages 670–680, 2010.

[13] P. Garcia and H. F. Korth. Pipelined hash-join on

multithreaded architectures. In DaMoN, pages 1:1–1:8, 2007.
[14] B. Gold, A. Ailamaki, L. Huston, and B. Falsaﬁ. Accelerating

database operators using a network processor. In DaMoN, 2005.

[15] B. He, M. Lu, K. Yang, R. Fang, N. K. Govindaraju, Q. Luo,
and P. V. Sander. Relational query coprocessing on graphics
processors. ACM TODS, pages 21:1–21:39, 2009.

[16] B. He and Q. Luo. Cache-oblivious databases: Limitations and
opportunities. ACM Trans. Database Syst., pages 8:1–8:42,
2008.

[17] B. He, K. Yang, R. Fang, M. Lu, N. Govindaraju, Q. Luo, and

P. Sander. Relational joins on graphics processors. In
SIGMOD, pages 511–524, 2008.

[18] B. He and J. X. Yu. High-throughput transaction executions on
graphics processors. Proc. VLDB Endow., pages 314–325, 2011.

[19] T. H. Hetherington and et al. Characterizing and evaluating a
key-value store application on heterogeneous cpu-gpu systems.
In ISPASS, pages 88–98, 2012.

[20] C. Hong, D. Chen, W. Chen, W. Zheng, and H. Lin. Mapcg:

writing parallel program portable between cpu and gpu. In
PACT, pages 217–226, 2010.

[21] T. Kaldewey, G. Lohman, R. Mueller, and P. Volk. Gpu join

processing revisited. In DaMoN, pages 55–62, 2012.

[22] C. Kim and et al. Sort vs. hash revisited: fast join

implementation on modern multi-core cpus. PVLDB, 2009.
[23] R. Kumar, D. M. Tullsen, and N. P. Jouppi. Core architecture
optimization for heterogeneous chip multiprocessors. In PACT,
pages 23–32, 2006.

[24] Y. Li, I. Pandis, R. Mueller, V. Raman, and G. Lohman.

Numa-aware algorithms: the case of data shuﬄing. In CIDR,
2013.

[25] M.-L. Lo, M.-S. S. Chen, C. V. Ravishankar, and P. S. Yu. On
optimal processor allocation to support pipelined hash joins. In
SIGMOD, pages 69–78, 1993.

[26] S. Manegold, P. Boncz, and M. L. Kersten. Generic database

cost models for hierarchical memory systems. In VLDB, pages
191–202, 2002.

[27] S. Manegold, P. A. Boncz, and M. L. Kersten. What happens

during a join? dissecting cpu and memory optimization eﬀects.
In VLDB, 2000.

[28] H. Pirk, S. Manegold, and M. Kersten. Accelerating foreign-key
joins using asymmetric memory channels. In ADMS, 2011.
[29] K. Ross. Eﬃcient hash probes on modern processors. In ICDE,

pages 1297–1301, 2007.

[30] D. A. Schneider and D. J. DeWitt. A performance evaluation of
four parallel join algorithms in a shared-nothing multiprocessor
environment. In SIGMOD, pages 110–121, 1989.

[31] A. Shatdal, C. Kant, and J. F. Naughton. Cache conscious
algorithms for relational query processing. In VLDB, 1994.
[32] M. Stonebraker and et al. C-store: a column-oriented dbms. In

VLDB, pages 553–564, 2005.

[33] G. Tan, L. Li, S. Triechle, E. Phillips, Y. Bao, and N. Sun. Fast

implementation of dgemm on fermi gpu. In SC, 2011.
[34] J. Teubner and R. Mueller. How soccer players would do

stream joins. In SIGMOD, pages 625–636, 2011.

[35] K. Thouti and S.R.Sathe. Comparison of openmp and opencl
parallel processing technologies. IJACSA, pages 56–161, 2012.
[36] S. Zhang, J. He, B. He, and M. Lu. Omnidb: Towards portable

and eﬃcient query processing on parallel cpu/gpu
architectures. In PVLDB, pages 1–4, 2013.

APPENDIX

A. MORE EXPERIMENTAL RESULTS

CPU

GPU

We present more experimental results, including compar-
ison with a coarse-grained scheduling approach, evaluating
hash join performance for data sets larger than zero copy
buﬀer and more detailed studies on latches.

Comparison with A Coarse-Grained Scheduling Ap-

proach. For comparison, we have implemented a simple
coarse-grained scheduling approach (namely “BasicUnit”).
The BasicUnit approach dynamically assigns a chunk of tu-
ples to the CPU or the GPU, and performs the build or
probe operations with that chunk on the corresponding pro-
cessor. Due to the architectural diﬀerence between the CPU
and the GPU, the chunk size is tuned for the target archi-
tecture. Compared with our proposed approach, the Ba-
the CPU may
sicUnit approach has a major deﬁciency:
perform more non-CPU-optimized tasks than our proposed
ﬁne-grained co-processing, and vice versa. We have imple-
mented the suggested approach, and report the results in
Figure 16. When both R and S tables have 16M tuples,
our proposed approaches (SHJ-PL and PHJ-PL) are 31%
and 25% faster than their counterparts using the BasicU-
nit approach. Besides, although BasicUnit works like DD,
the scheduling overhead of BasicUnit results in performance
degradation.

We have further investigated the workload ratios of diﬀer-
ent steps on the CPU and the GPU. Figures 17 and 18 show
the results using the BasicUnit approach for SHJ and PHJ,
respectively. The ratios are signiﬁcantly diﬀerent from the
optimal ratios given by our cost model (Figures 5 and 6 in
the paper) because the CPU or the GPU has to process the
same portion of the workload in all steps of a given phase,
resulting in deﬁciency compared with our ﬁne-grained co-
processing.

)
s
(
e
m

i
t
d
e
s
p
a

l
E

2.5

2

1.5

1

0.5

0

BasicUnit
(SHJ)

SHJ-DD

SHJ-PL

BasicUnit
(PHJ)

PHJ-DD

PHJ-PL

Figure 16: Performance comparison between Basi-
cUnit and ﬁne-grained co-processing algorithms

CPU

GPU

CPU

GPU

b1

b2

b3

b4

p1

p2

p3

p4

13%

87%

(a) Build

41%

59%
(b) Probe

Figure 17: Workload ratios of diﬀerent steps for SHJ
employing BasicUnit

Large datasets that cannot ﬁt into the zero copy
In the current system, the zero copy buﬀer size

buﬀer.

CPU

GPU

CPU

GPU

b1

b2

b3

b4

p1

p2

p3

p4

n1

n2

n3

78%

22%
(a) Partition

31%

69%

(b) Build

46%

54%
(c) Probe

Figure 18: Workload ratios of diﬀerent steps for
PHJ employing BasicUnit

is limited. For larger data sets that cannot ﬁt into the zero
copy buﬀer, we perform the hash join with partitioning. The
algorithm is similar to classic hash joins for external mem-
ory. Here, we view the zero copy buﬀer as main memory
and other system memory as external memory. Speciﬁcally,
we partition the build and the probe relations so that the
join of a partition pair can ﬁt into zero copy buﬀer. The
partitioning can have multiple passes. In partition phase, a
block of tuples from the input relation is partitioned in the
zero copy buﬀer with our current partitioning algorithm. In
our experiment, the chunk size is 16 million tuples. Next,
we copy the intermediate partitions out from the zero copy
buﬀer to the system memory. After all the inputs are par-
titioned, we link all the intermediate partitions together to
form the result partition pairs. Next, we apply the hash join
algorithms proposed in this paper to handle the join in each
partition pair.

Figure 19 shows the performance when we vary the num-
ber of tuples in both relations R and S from 16M (256MB)
to 128M (2GB). We compare diﬀerent join algorithms on
the partition pair, either SHJ-PL or PHJ-PL. PHJ-PL is up
to 9% faster than SHJ-PL. We divide the elapsed time into
three parts: data copy time, partition time and join time for
the time on data transfer between the system memory and
zero copy buﬀer, the time for partitioning and for perform-
ing the join on the partition pairs, respectively. There is no
data copy time or partition time when |R| = |S| = 16M ,
because the entire join can ﬁt into the zero copy buﬀer. On
other cases, partition time is very signiﬁcant. We obtain the
data copy time from AMD CodeAnalyst proﬁler. The data
copy time is around 4% of the total time. Furthermore, both
the partition time and the join time increase almost linearly
with the size of input tables. It indicates good scalability
of our algorithm when the data size is larger than zero copy
buﬀer.

Partiton time

Join time

Data copy time

)
s
(
e
m

i
t
d
e
s
p
a
l
E

25

20

15

10

5

0

SHJ-PLPHJ-PL

SHJ-PLPHJ-PL

SHJ-PLPHJ-PL

SHJ-PLPHJ-PL

 16M                            32M                              64M                        128M
Number of tuples in R/S

Figure 19: Comparing elapsed time of diﬀerent join
algorithms on each partition pair for large data sets
(|R| = |S|)

uniform

low-skew

high-skew

uniform

low-skew

high-skew

)
s
(
e
m

i
t
d
e
s
p
a

l
E

0.9
0.8
0.7
0.6
0.5
0.4
0.3
0.2
0.1
0

)
s
(
e
m

i
t
d
e
s
p
a

l
E

0.6

0.5

0.4

0.3

0.2

0.1

0

1 4

6
1

4
6

6
5
2

K
1

K
4

K
6
1

K
4
6

K
6
5
2

M
1

M
4

M
6
1

1 4

6
1

4
6

6
5
2

K
1

K
4

K
6
1

K
4
6

K
6
5
2

M
1

M
4

M
6
1

Number of integers in the array

Number of integers in the array

(a) Locking time on the CPU

(b) Locking time on the GPU

Figure 20: The performance of micro benchmark on
locking overhead on the CPU and the GPU

Locking overhead. We have designed a micro bench-
mark to study the performance impact of our latch imple-
mentation on APU. In the micro benchmark, we ﬁrst gen-
erated an array of N integers and then we used K threads
to perform X increments in total on the array, where X is
a constant. The increment operation is implemented with
our latch. We investigated diﬀerent data distributions (the
notations of “uniform”, “low-skew” and “high-skew” have
the same meanings as the experimental setting in the pa-
per). The results are shown in Figure 20, where N ranges
from 1 to 16M, X is ﬁxed to be 16M on both the CPU and
the GPU, K is ﬁxed to be 8192 and 256 on the GPU and
the CPU respectively. For both the CPU and the GPU,
the overhead decreases when the data size increases until
the input array cannot ﬁt into the cache size (4MB). After
that, the execution time of running on the high-skew data is
slightly lower than that on the uniform data. This is mainly
because of the beneﬁt of data locality in the high-skew data
that compensates the overhead of latches. This point has
also been pointed out in Section 4.4 of the previous study
[4].

