# SwarmIO

**Source**: SwarmIO.pdf
**Format**: .pdf

---

SwarmIO: Towards 100 Million IOPS SSD Emulation for
Next-generation GPU-centric Storage Systems
Hyeseong Kim Gwangoo Yeo Minsoo Rhu
KAIST KAIST KAIST
hyeseong.kim@kaist.ac.kr gwangoo525@kaist.ac.kr mrhu@kaist.ac.kr
Abstract—GPU-initiated I/O has emerged as a key mecha- retrieval-augmented generation (RAG) [27], recommendation
nism for achieving high-throughput storage access by leveraging systems [37], and agentic AI workflows [19] generate sparse,
massive GPU thread-level parallelism, while recent industry
fine-grained accesses to large datasets. These workloads are
trends point toward SSDs optimized for ultra-high random-
driving the development of “GPU-centric” storage systems
read IOPS. Together, these trends are enabling the emergence
of IOPS-optimized, GPU-centric storage systems. Despite this that prioritize fine-grained I/O parallelism, enabling GPUs
momentum, no existing framework enables quantitative end-to- to directly access storage via GPU-initiated I/O [50]. In
end evaluation of storage systems optimized for GPU-initiated this model, GPUs natively submit I/O requests on demand,
I/O.WhileconventionalSSDemulatorsprovideapromisingpath
bypassingthehostCPU’sorchestrationpathentirely.However,
toward end-to-end modeling in traditional storage systems, they
although GPU-initiated I/O can generate tens to hundreds of
face three key challenges in this GPU-centric setting: limited
frontend scalability for ingesting massive request streams, high millions of IOPS (MIOPS), traditional storage devices cannot
software overhead in emulating GPU-initiated I/O control and sustain such extreme random-read throughput. For instance,
datapaths,andexcessivetiming-modelmaintenanceoverheadat evenhigh-endenterprise-gradeSSDssupportonlyuptoabout
extremelyhighI/Orequestrates.WeproposeSwarmIO,anSSD
3 MIOPS [22], [36], [54], leaving current storage systems
emulator for massively parallel, GPU-centric storage. SwarmIO
fundamentally unable to meet the massive, fine-grained IOPS
faithfully models IOPS-optimized SSDs at target performance
levels of up to 40 MIOPS, achieving a 303.9× speedup over the demands of GPU-initiated I/O.
state-of-the-art baseline SSD emulator under GPU-initiated I/O. These limitations are motivating the development of next
We further demonstrate its utility through a vector search case generation “ultra-high IOPS” storage architectures that prior-
study,showingthatincreasingSSDIOPSfrom2.5MIOPSto40
itize IOPS over sequential bandwidth. Under initiatives such
MIOPS yields an average end-to-end speedup of up to 9.7×.
as NVIDIA’s StorageNext [40], industry leaders are rapidly
developing IOPS-optimized SSD designs tailored for mas-
I. INTRODUCTION
sivelyparallel,fine-grained512-byteaccessesfromGPUs[4],
The rapid growth of modern AI workloads has pushed [18], [26], [32], [38]–[40]. For example, the Kioxia GP
runtime data footprints far beyond the capacity of GPU Series, utilizing low-latency XL-FLASH [23], exemplifies
High Bandwidth Memory (HBM), making storage systems an this transition, targeting 10 MIOPS in 2026, with industry
essential component of the AI data pipeline. As applications roadmaps projecting 100 MIOPS by 2027 using PCIe Gen6
evolve from simple generative queries to multi-stage, chain- andGen7interfaces[4],[18].Despitethismomentum,system
of-thought agentic AI, the required Key-Value (KV) cache for designers and application developers face a classic chicken-
massive context windows drives an unprecedented expansion and-eggproblem:whileultra-highIOPSstoragesystemsbased
in memory requirements. Given this landscape, storage is no on next-generation SSDs are on the horizon, their practical
longer merely a passive capacity layer, but is increasingly benefits cannot yet be evaluated because the hardware is not
treated as an active, ephemeral memory tier for efficient commercially available. Nevertheless, quantifying the benefits
large-scale AI deployments. To serve this role effectively, of employing these ultra-high IOPS storage devices on end-
architectures such as the NVIDIA Inference Context Memory to-end application performance is critical for guiding future
Storage Platform (CMX) have been introduced to act as an system development, motivating the need for a quantitative,
AI-native context tier, extending GPU memory across high- end-to-end performance modeling approach.
bandwidth networks [43]. This fundamental shift marks the While cycle-level system simulators (e.g., gem5 [3] inte-
collapseofthetraditionalmemory-storagehierarchy,requiring grated with GPGPU-Sim [6], [17] and an SSD simulator [8],
NAND flash SSDs to operate at near-memory speeds to avoid [59]) could, in principle, provide such insights, they are
computational stalling. prohibitively slow and cannot evaluate full-system behavior
Among the evolving performance demands on storage, within a reasonable wall-clock time. For instance, GPGPU-
an emerging class of data-intensive applications introduces Sim achieves a simulation speed of only about 3 KIPS (kilo-
a new design objective: sustaining high random read I/O instructionspersecond),whichisfartooslowtosimulateeven
operations per second (IOPS) for massively parallel, fine- a simple AI model’s inference within a practical timeframe.
grained accesses. Datacenter-native AI applications such as A promising alternative is to develop a high-performance
6202
rpA
8
]RA.sc[
1v86660.4062:viXra

SSD emulator capable of sustaining hundreds of millions of
GPU SSD
IOPS in “real time” while operating alongside a real GPU.
SM DRAM
Such an emulation framework enables end-to-end evaluation Threads of future GPU-centric storage systems integrated with ultra-
`
high IOPS SSDs. Unfortunately, existing SSD emulators [20], SM
[28], [33], [62] are inadequate for this regime as they face Threads I/O queue pairs I/O buffers
three key challenges. First, prior designs do not scale to tens
or hundreds of millions of IOPS, as they were originally built
for traditional CPU-based storage; their frontend architectures
cannot efficiently ingest the massively parallel I/O request
streams generated by GPUs, leading to severe queue buildup.
Second,GPU-initiatedI/Ointroducesdistinctcontrolanddata
paths that require software-mediated data movement between
CPU-side emulated storage structures and GPU-resident I/O
buffers, incurring significant overhead. Third, at such high
request rates, per-request updates to the emulator’s timing
model become a bottleneck, making it difficult to maintain
high model fidelity at ultra-high IOPS.
SwarmIO is designed to fill this critical gap by providing
an IOPS-scalable SSD emulation framework with a funda-
mental goal of reaching 100 MIOPS1. SwarmIO is built
upon three key innovations that significantly advance the
performance of prior SSD emulators. First, we accelerate the
frontendofouremulatorusingaparallelism-awarearchitecture
that adopts a distributed software design and incorporates
a throughput-oriented request fetching mechanism leveraging
NVMe protocol semantics. This approach enables request
ingestion throughput to scale with request-level parallelism
whilesubstantiallyreducingqueuingdelays.Second,welever-
age the Intel Data Streaming Accelerator (DSA) to offload
SSD backend data copy operations, significantly reducing the
overhead associated with emulating GPU-initiated I/O. Our
proposal is co-designed with a DSA-aware, kernel-level API
for high-throughput copy offloading, maximizing DSA uti-
lization in a multi-threaded environment. Third, we introduce
an aggregated timing model update mechanism that amortizes
state management overhead across a group of requests while
preserving high-fidelity timing emulation.
We evaluate SwarmIO by first validating its modeling
fidelity against an enterprise-grade 2.5 MIOPS SSD, and then
demonstrating the scalability of its architecture. Although
hardware constraints in our evaluation testbed cap the current
emulation throughput at 40 MIOPS, this still represents a
massive leap forward under extreme request parallelism un-
lockedwithGPU-initiatedI/O.WefurthershowthatSwarmIO
enables end-to-end evaluation of AI applications that leverage
GPU-initiated I/O, highlighting the need for GPU-centric
storage systems capable of sustaining hundreds of millions of
IOPS.Usingvectorsearch,akeycomponentofRAGsystems,
as a case study, we quantify the end-to-end performance
benefits of combining GPU-initiated I/O with ultra-high IOPS
SSDs. We summarize the key contributions of this work:
• We propose SwarmIO, an IOPS-scalable NVMe SSD
emulation framework that supports end-to-end modeling
1SwarmIOisopen-sourcedathttps://github.com/VIA-Research/SwarmIO.
sllebrooD
sllebrooD
ecafretni
tsoH
Control Data (PCIe P2P for both paths)
NANccD NANccD
SQ CQ Page cache SSD
⁝
controller NANccD NANccD
SQ CQ ⁝ ⁝
DMA NANccD NANccD
Fig. 1: GPU-initiated I/O.
of GPU-centric storage systems with GPU-initiated I/O.
• We demonstrate, on real GPU systems, that SwarmIO
scales to 40 MIOPS, achieving a 307.7× speedup over a
state-of-the-art SSD emulation framework.
• We enable end-to-end analysis of GPU-centric storage
systems with future IOPS-optimized SSDs, and demon-
strate through a vector-search case study that increasing
SSD IOPS from 2.5 MIOPS to 40 MIOPS yields an
average 9.7× end-to-end system-level speedup.
II. BACKGROUND
A. GPU-initiated Storage I/O
GPU-initiated I/O enables high-throughput, fine-grained,
on-demandstorageaccessesfromtheGPU,meetingtheneeds
of emerging applications with sparse and random data access
patterns [5], [47], [50]. As illustrated in Figure 1, GPU-
initiatedI/OoffloadstheentireI/OstacktotheGPU,including
I/O queues for the control path and I/O buffers for the data
path.Consequently,allcommunicationwiththestoragedevice
occurs via PCIe peer-to-peer (P2P) transfers between the
GPU and SSD, allowing the entire I/O lifecycle to proceed
without CPU intervention. This design minimizes CPU–GPU
synchronization overhead and reduces I/O amplification by
enabling GPU threads to directly submit I/O requests on
demand. By leveraging GPU’s massive thread-level paral-
lelism,GPU-initiatedI/Ocangeneratealargenumberoffine-
grained I/O requests, fully stressing storage IOPS and PCIe
bandwidthutilizationbeyondwhattraditionalCPU-centricI/O
can achieve for random accesses.
B. SSD Simulation and Emulation Frameworks
SSD simulators. SSD simulators model storage I/O behav-
ior, from the frontend host interface to the backend NAND
flash device, within their own event time domains. Existing
simulatorsgenerallyfallintotwocategories.First,trace-driven
approaches [59] replay timestamped I/O traces. Therefore,
they lack closed-loop interaction with running systems, mak-
ing it difficult to capture dynamic runtime behavior such
as inter-request dependencies or interactions with host I/O
stack components (e.g., the page cache). Second, full-system
approaches [8], [59] integrate with full-system simulators [3]
to enable detailed application-level characterization. However,
these full-system simulators are not only slow but also ill-
suitedforstudyingGPU-initiatedI/O;tothebestofourknowl-
edge, no existing full-system simulation framework models
PCIe P2P between an SSD and a GPU.
SSD emulators. In contrast, SSD emulators interact with
running applications and can therefore provide end-to-end

Not copied Copied Control Data
Host NVMeVirt
Worker Emulated storage blocks
Worker
Worker
tegraT T
:emit
I/O buffers
rehctapsiD ledom
gnimiT
Frontend Backend
Worker
llebrooD
llebrooD
forsignalingI/Osubmissions),andsequentiallyfetchesnewly
submitted requests when the doorbells are set. After fetching
eachrequest,itdispatchestherequesttooneoftheworkersvia
SQ CQ itsper-workerqueue,wherestoragedatatransfersareemulated
by deriving the target completion time of the request using
NVMeVirt’s timing model. A worker scans all its local queue
entries in each iteration and checks the status of each request.
If a request is newly enqueued, the worker emulates the
(a) NVMeVirtarchitecture
corresponding storage data transfer by copying data between
Target time t0' t1' t2' t0' t1' t2'
the target I/O buffer and the emulated storage blocks, which
Resource
occupancy r0 Lmin r1 r2 r0 r1 r2 is implemented by modeling the storage block address space
M lat o e d n e c l y ed r r 0 1 Sched M S in c _ h d e e d lay Min_delay Sc W he a d it M Sc i h n e _ d dela M y in_delay in CPU memory. A worker posts completion of a request to
r2 Sched Min_delay Wait Sched Min_delay the completion queue (CQ) only if the target completion time
R ar e r q iv u a e l s t t i me t0 t1 t2 Time t0t1t2 Time has already elapsed. Otherwise, the request remains copied
Low load High load but not yet completed. For such requests, the worker re-
(b) NVMeVirt’stiming model evaluateswhetherthetargetcompletiontimehasbeenelapsed
Fig. 2: (a) High-level overview of NVMeVirt and (b) an
in subsequent iterations.
example illustrating its timing model. The timing model de-
Timing model. Among the timing models provided by
rives a request’s target completion time when it is fetched
NVMeVirt,wedescribeitssimpletimingmodelasarepresen-
by the dispatcher. Sched updates the modeled SSD resource
tative example. NVMeVirt captures SSD performance using
availability to regulate sustained throughput (T max ), while two configurable parameters: maximum throughput (T )
max
Min_delay enforces minimum per-request latency (L min ). and minimum latency (L ). It abstracts SSD hardware
min
resources as a set of parallel scheduling instances (e.g., flash
functional modeling, with several works [20], [28], [33], [62]
controllers and channels) and decomposes each I/O request
also supporting performance modeling in the wall-clock time
into unit-sized operations (e.g., read from flash page) that
domain. However, existing frameworks often fall short in
are scheduled across these scheduling instances. By tracking
scalability and interoperability with GPU-initiated I/O. Some
scheduling instance availability (i.e., resource occupancy),
emulators[33]requiredevice-drivermodificationstointercept
the timing model regulates sustained throughput below the
I/O requests and emulate storage I/O using a DRAM-backed
configured maximum throughput (T ), and each request is
virtual disk while rate-limiting requests to match target SSD’s max
assumed to occupy its target instances for a fixed scheduling
performance. This approach is fundamentally incompatible
time (Sched), during which the instance is unavailable to
with GPU-initiated I/O, which bypasses the host driver and
others. Figure 2(b) illustrates this process assuming a single
uses a dedicated GPU-side I/O stack. Virtualization-based
scheduling instance. Under high input load, if the target
emulators [28], [62] instead present virtual SSDs to guest
instance is occupied by preceding requests when a request
virtual machines via QEMU. However, they either incur
arrives,schedulingisdeferreduntiltheinstancebecomesavail-
significant context-switch overhead when trapping at MMIO
able;forexample,theinstanceisoccupiedbyrequestr0when
operations [62] or lack support for the PCIe P2P transfers
r2 arrives at t2. The target completion time is then derived
required by GPU-initiated I/O [28].
by adding Sched and an additional delay (Min_delay) to
C. NVMeVirt enforce the configured minimum latency (L ). Under low
min
Unlike prior SSD emulators, NVMeVirt [20] exposes a input load, by contrast, a request is scheduled as soon as it
software-defined PCIe device directly through the kernel PCI arrives, and its target latency is simply the sum of the two
subsystem,presentingavirtualSSDonabare-metalhost.This delays, Sched and Min_delay.
design enables the emulation of diverse storage environments,
D. Intel Data Streaming Accelerator
including those that require PCIe P2P transfers. As such,
NVMeVirt is functionally capable of modeling GPU-initiated The Intel Data Streaming Accelerator (DSA) [14], inte-
I/O. However, as detailed in Section III, it does not provide grated into 4th-Gen Xeon Scalable Processors, accelerates
sufficient scalability to emulate future SSD IOPS targets, and data movement and transformation tasks. DSA is organized
thedistinctcontrolanddatapathsofGPU-initiatedI/Ofurther aroundgroups,whicharesoftware-configurableunitscompris-
degrade achievable performance. We next describe the overall ing work queues (WQs) and engines (blue box in Figure 6).
architecture and timing model of NVMeVirt. Softwareoffloadsoperationsbyissuing64-byteworkdescrip-
Overall architecture. As shown in Figure 2(a), NVMeVirt tors to specific WQs, with each descriptor occupying one
consists of a “frontend” that models the host interface and a WQ slot. Descriptors are issued via 64-byte writes to portals,
“backend” that emulates storage data transfers, implemented which are MMIO regions mapped to specific WQs. WQs
by a single dispatcher and multiple worker threads, respec- can operate in either shared mode, where multiple software
tively. The dispatcher polls submission queue (SQ) doorbells clientsshareaqueue,ordedicatedmode,whereasingleclient
(i.e., software-defined NVMe registers exposed to the host exclusively uses the queue and manages available descriptor

5
4 3
2
1
0
8 16 32 64 128 256 512
SPOIM
Weusethefio[2]4KBrandomreadbenchmarktoevaluate
NVMeVirt’s scalability under traditional “CPU-centric” I/O.
The dispatcher and worker threads are pinned to dedicated
cores within a single CPU socket, while fio runs on the
remaining cores in the same socket. Section V provides
I/O depth
further details of our experimental setup. To isolate frontend
Fig. 3: Frontend throughput of NVMeVirt under CPU-centric
dispatcher performance, we disable worker-side data transfer
I/O with 32 fio threads.
emulation,whichwerefertoasthebackend(Figure2(a)).We
slots itself. Engines fetch descriptors from any WQ within thenstressthedispatcherbyrunning32fiothreadsinparallel,
the same group and execute the corresponding operations in a each submitting I/O requests through its own dedicated SQ,
pipelined manner. Among the supported descriptor types, our while increasing the I/O depth from 8 to 512. A higher
workusesmemorycopyandbatchdescriptorstooffloadcopy I/O depth denotes a larger number of outstanding requests
operations during emulation, where batch descriptors allow per thread within its SQ, thereby increasing the submission
an array of copy descriptors to be issued at once, amortizing pressure on NVMeVirt. As shown in Figure 3, the frontend
descriptor issue overhead [24]. Each copy descriptor can use dispatcher’sthroughputplateausat4.6MIOPSdespiteincreas-
either physical addresses (PAs) and virtual addresses (VAs) to ing I/O depth, well below the 10–100 MIOPS target range of
specify the source and destination locations. future ultra-high IOPS SSDs. This limited frontend scalability
fundamentally constrains achievable throughput to only a few
III. CHARACTERIZATIONANDMOTIVATION MIOPS, regardless of how effectively backend data transfers
are parallelized across multiple workers.
In this section, we characterize the limitations of existing
SSD emulators in modeling future IOPS-optimized SSDs B. Key Challenges with GPU-initiated I/O
while supporting GPU-initiated I/O. We focus on NVMeVirt,
Beyond modeling ultra-high IOPS SSDs, this work aims to
as alternative emulators are incompatible with GPU-initiated
provideanend-to-endemulationframeworkforGPU-initiated
I/O due to their reliance on host-system modifications or vir-
I/O. However, GPU-initiated I/O’s control and data paths
tualization mechanisms. As we detail in this section, although
differfundamentallyfromthoseoftraditionalCPU-centricI/O,
NVMeVirt provides the functional foundation for modeling
posinguniquechallengesforfaithfullymodelingthisemerging
GPU-initiated I/O by presenting a software-defined, virtual
storage paradigm for real time emulation.
PCIe device to the host, it cannot sustain the level of request-
Small-block data transfers over PCIe. As described in
level parallelism required by future SSDs.
Section II-C, NVMeVirt emulates storage data transfers by
havingworkerthreadscopydatabetweenthetargetI/Obuffers
A. Frontend Scalability Bottleneck
and emulated storage blocks. Under traditional CPU-centric
Modern SSDs adopt NVMe as the storage protocol be- I/O, both ends of this copy reside in CPU memory. Under
cause it is designed to fully exploit SSD throughput via a GPU-initiated I/O, however, both the I/O buffers and I/O
multi-queue I/O interface. An SSD controller includes a host queue pairs (SQ and CQ) reside in GPU memory (Figure 1),
interface layer (i.e., the frontend) that dispatches incoming so each request requires data transfer over PCIe, introducing
requests and handles completions through I/O queue pairs. To additional overhead in both the data and control paths. In the
fully leverage NVMe’s request-level parallelism within and data path, applications using GPU-initiated I/O often exhibit
across I/O queues, the frontend request ingestion bandwidth fine-grained access granularity, typically below 8 KB [32],
must not become a performance bottleneck. In practice, sev- forcing workers to perform many small PCIe transfers (e.g.,
eral works [15], [25], [34], [49] accelerate this layer using CPU-to-GPU copies for storage reads). In the control path,
dedicated hardware to mitigate this bottleneck. the dispatcher sequentially fetches even smaller 64-byte SQ
Limited dispatch throughput. Despite its importance, entries allocated in GPU memory, resulting in fragmented
frontend performance scalability is often overlooked in exist- PCIe transactions. Therefore, when combined with limited
ing software-based SSD emulators, which struggle to sustain CPU thread-level parallelism, NVMeVirt fails to effectively
highlyconcurrentI/OrequestsarrivingacrossdifferentSQs.In utilize PCIe bandwidth, limiting achievable IOPS.
particular, NVMeVirt relies on a single dispatcher thread that Address mapping overhead. Natively, GPU-initiated I/O
sequentially polls the emulated doorbells of all SQs, which allowsSSDstoaccessGPUmemorybyexposingitinthehost
is similar to frontend designs commonly adopted in prior physical address (PA) space through a base address register
work [28]. When multiple SQ doorbells are updated simul- (BAR) [42]. A GPU thread submits an NVMe command that
taneously, the dispatcher fetches requests from a given SQ specifies the target I/O buffer with a PA, and the SSD’s DMA
before proceeding to the next, thereby serializing I/O request engine uses that PA to perform P2P DMA to and from GPU
processing. Consequently, the centralized frontend architec- memory.InNVMeVirt,however,datatransfersareemulatedin
ture exacerbates SQ queuing delays and prevents emulation software using CPU worker threads. Upon receiving a request
throughput from scaling with the request-level parallelism fromthedispatcher,anNVMeVirtworkermustmapthetarget
exposed by the NVMe interface. I/O buffer’s PA to a virtual address (VA) to access the GPU

100
75
50
25
0 1 2 4 8 16 32
)sμ(
ycnetaL
Map Copy
# of worker threads
Fig.4:Dynamicaddressmapping/unmappingoverhead(Map)
to prepare CPU thread-driven 512-byte random data copies
(Copy) from CPU to GPU memory.
3
2
1
0
256 1K 4K 16K 64K256K
SPOIM
NVMeVirt Real SSD
100
10
1
0.1
0.01
256 1K 4K 16K 64K256K
# of GPU threads
)sm(
ycnetaL
GPU Global timing model SwarmIO
SSQ SQ SQQ CCQ CQ CQQ
SSQ SQ SQQ CCQ CQ CQQ T1
T2
T3
I/O buffers T4
NVMeVirt Real SSD
DSA DSA DSA
# of GPU threads
(a) Average latency (b) IOPS
Fig. 5: (a) Average latency and (b) IOPS of NVMeVirt under
Not copied Copied Control Data
GPU-initiatedI/O,comparedwiththoseobservedunderareal
SSD (Solidigm D7-PS1010), as the number of GPU threads
submitting 512-byte random read I/O requests varies.
memory from the CPU. Because the target I/O buffer address
differs across requests, workers must dynamically map and
unmapitforeachemulateddatatransferusingmemremap()
and memunmap(), incurring substantial latency overhead.
Because these functions modify page tables under inter-
nal kernel locks, this repeated mapping and unmapping by
numerous worker threads creates a severe serialization bot-
tleneck. To quantify the resulting overhead, we implement
a microbenchmark that models NVMeVirt’s backend data
transfer behavior under GPU-initiated I/O while assuming
the frontend is not a performance bottleneck (i.e., a worker-
only setup). Multiple CPU worker threads repeatedly map a
target buffer, copy a random 512-byte block from the CPU-
side emulated storage blocks to the GPU-side I/O buffer,
and unmap the buffer. As shown in Figure 4, mapping and
unmapping (Map) account for 98.8% of the total data transfer
latency on average. Under heavy contention with 32 threads,
the latency of emulating a single storage data transfer reaches
94µs,limitingaggregatethroughputtoonly0.34MIOPS(i.e.,
at most 32 parallel I/Os per 94 µs), far below the 3 MIOPS
available in state-of-the-art SSDs [22], [36], [54].
NVMeVirt vs. real SSD. Using the BaM [50] 512-byte
random read benchmark on an NVIDIA H200 GPU [41],
weevaluateNVMeVirt’send-to-endperformanceunderGPU-
initiatedI/OwhilevaryingthenumberofGPUthreadssubmit-
tingstoragereadI/Os.NVMeVirt’stimingmodelisconfigured
to match that of a real Solidigm D7-PS1010 SSD. As shown
in Figure 5, NVMeVirt achieves at most 0.13 MIOPS with
256K GPU threads, making it 16.6× slower than the same
benchmarkrunningontherealSSD.Overall,NVMeVirtincurs
17.4–63.7× higher latency than the physical SSD, failing to
meetourreal-timeemulationrequirementsfornext-generation
GPU-centric storage systems.
IV. SWARMIO
In this section, we present SwarmIO, an IOPS-scalable
SSD emulation framework for GPU-centric storage systems.
sllebrooD
sllebrooD rekroW
Fetch buffers Target time:
❸
❹C
Local
queues
rehctapsiD
❷ rekroW
Service unit
❺C Emulated ❶ storage blocks
DSA group
slatroP
DSA
Pointer to an array WQ Descriptor of copy descriptors processing unit
Batch
WQ processing unit EEnnggiinnee
DSA copy descriptor DSA batch descriptor
Fig. 6: High-level overview of SwarmIO.
Existing SSD emulators fail to faithfully model end-to-end
performance of GPU-centric storage: some lack support for
GPU-initiatedI/O,whileothers(e.g.,NVMeVirt)provideonly
functional modeling and suffer from non-scalable frontends
and high CPU-driven data movement overheads. SwarmIO
addressestheselimitationswithadistributed,high-throughput
frontend design, hardware-accelerated data transfers, and a
newtimingmodelupdatemechanismthatpreservesemulation
fidelity at extreme IOPS. Together, these techniques remove
fundamental bottlenecks in prior emulators, significantly im-
proving achievable IOPS for GPU-initiated I/O.
A. High-level Overview
SwarmIO is implemented as a Linux kernel module and
builds on NVMeVirt’s core mechanisms to provide a virtual
SSD abstraction within the PCI subsystem. Prior work [20],
[28] relies on centralized frontends and throughput-limited
datatransferemulation.Incontrast,SwarmIOintroducesadis-
tributed,IOPS-orientedarchitecturecenteredaroundamodular
operational unit called the service unit (Figure 6).
Eachserviceunitadoptsaproducer–consumermodelwhere
a dispatcher (frontend) polls SQ doorbells to fetch requests,
while multiple workers (backend) process storage data trans-
fers in parallel and handle completions. Figure 6 depicts
the execution flow within a service unit: the dispatcher first
fetches enqueued requests from its assigned SQs (step ❶) and
computes their target completion times by invoking a global
timing model shared across all service units (step ❷). These
timestamped requests (T1-4) are then distributed to the local
queuesofassignedworkers(step❸).Eachworkeroperatesin
a continuous loop: it first performs storage data transfers for
up to a predefined number of requests from its local queue
(step ❹), and then re-evaluates the queue from the beginning
to process completions for any “copy-done” requests whose
targetcompletiontimeshavearrived(step❺).Thismechanism
ensures that request completion is not delayed by a long
sequenceofprecedingdatatransfers,therebymaintainingstrict
adherence to the timing model.

By partitioning I/O queue pairs across service units, we that all entries within each SQ/CQ are allocated contiguously
transform the centralized frontend into a distributed architec- in physical memory. By merging multiple PCIe transactions,
ture. With coalesced request fetching, SwarmIO fully exploits SwarmIO amortizes transaction overhead and improves trans-
NVMe request-level parallelism (Section IV-B). In addition, ferefficiency.Togetherwithdistributeddispatching,coalesced
to reduce the software overhead of CPU-driven data copies, fetching enables SwarmIO to efficiently handle bursty I/O
SwarmIOadoptsDSA-acceleratedstorageI/Oemulation(Sec- submissions while maintaining a highly parallel and scalable
| tion IV-C). | It offloads | both | dispatcher-side |     | request | fetching | frontend | design. |     |     |     |     |     |
| ----------- | ----------- | ---- | --------------- | --- | ------- | -------- | -------- | ------- | --- | --- | --- | --- | --- |
andworker-sidestoragedatatransferstoIntelDSAs[14],and
| introduces | a DSA-aware | kernel-level |     | API | for high-throughput |     |                    |     |         |               |     |     |     |
| ---------- | ----------- | ------------ | --- | --- | ------------------- | --- | ------------------ | --- | ------- | ------------- | --- | --- | --- |
|            |             |              |     |     |                     |     | C. DSA-accelerated |     | Storage | I/O Emulation |     |     |     |
copyoffloadinginmulti-threadedenvironments.Finally,while
the global timing model shared across dispatchers enables 1) Design Principles for DSA-efficient Data Movement:
|            |             |           |     |         |            |        | Rethinking | data | transfers | with DSA. | Despite | improved |     |
| ---------- | ----------- | --------- | --- | ------- | ---------- | ------ | ---------- | ---- | --------- | --------- | ------- | -------- | --- |
| consistent | performance | modeling, |     | it also | introduces | a non- |            |      |           |           |         |          |     |
trivial design challenge: under high request rates, frequent frontend scalability for parallel request ingestion, software-
updates to the shared timing state by all dispatchers can incur mediated data transfers over PCIe in GPU-initiated I/O re-
|             |               |           |     |            |     |                 | main a major |     | performance | bottleneck, | as  | discussed | in Sec- |
| ----------- | ------------- | --------- | --- | ---------- | --- | --------------- | ------------ | --- | ----------- | ----------- | --- | --------- | ------- |
| substantial | serialization | overhead. |     | To address |     | this challenge, |              |     |             |             |     |           |         |
weintroduceaggregatedtimingmodelupdates(SectionIV-D), tion III-B. To address this, we propose hardware-accelerated
which minimize serialization across dispatchers by entering data movement using Intel DSA, which offloads data trans-
the critical section only once per set of requests. Together, fers from the CPU and enables total IOPS to scale beyond
these techniques enable SwarmIO to push achievable IOPS CPU processing limits. Importantly, offloading worker-side
|            |            |          |     |           |     |               | copies to | DSA | eliminates | address mapping |     | overhead, | as DSA |
| ---------- | ---------- | -------- | --- | --------- | --- | ------------- | --------- | --- | ---------- | --------------- | --- | --------- | ------ |
| far beyond | the limits | of prior | SSD | emulators |     | under massive |           |     |            |                 |     |           |        |
request-level parallelism in GPU-centric storage systems. operates directly on PAs without requiring VA mappings.
|                      |     |          |              |     |     |     | While NVMeVirt |        | utilizes      | the legacy | Crystal    | Beach | DMA     |
| -------------------- | --- | -------- | ------------ | --- | --- | --- | -------------- | ------ | ------------- | ---------- | ---------- | ----- | ------- |
| B. Parallelism-aware |     | Frontend | Architecture |     |     |     |                |        |               |            |            |       |         |
|                      |     |          |              |     |     |     | (CBDMA)        | engine | to accelerate | data       | transfers, | its   | support |
Distributed dispatch architecture. To overcome fron- is limited to na¨ıvely offloading worker-side transfers via a
|                   |         |     |            |      |     |             | synchronous | issue-and-wait |     | model. | We confirmed |     | that this |
| ----------------- | ------- | --- | ---------- | ---- | --- | ----------- | ----------- | -------------- | --- | ------ | ------------ | --- | --------- |
| tend bottlenecks, | SwarmIO |     | partitions | NVMe | I/O | queue pairs |             |                |     |        |              |     |           |
(SQ/CQ) across multiple service units, each led by a dedi- approach provides minimal practical benefit in reducing PCIe
cated dispatcher thread (Figure 6), reducing the number of transfer latency. Moreover, prior studies [24], [65] show that
SQs handled by each dispatcher. This alleviates SQ queuing evenwithDSA,suchsynchronous,per-requestoffloadingfails
delay when a single dispatcher cannot keep up with requests to amortize the software overheads in preparing and issuing
|           |            |          |     |     |             |          | individual | copy | descriptors. | This limitation |     | is more severe | for |
| --------- | ---------- | -------- | --- | --- | ----------- | -------- | ---------- | ---- | ------------ | --------------- | --- | -------------- | --- |
| submitted | to tens to | hundreds | of  | SQs | by multiple | host (or |            |      |              |                 |     |                |     |
GPU)threads.Eachserviceunitisprovisionedwithdedicated CBDMA,whichincurshigheroffloadingoverheadsthanDSA.
compute resources, including worker threads and DSAs, as SwarmIO is carefully designed to overcome these limita-
detailedinSectionIV-C.Thisdesignensuresconsistentperfor- tionsbyenablinghighlyparalleldatatransfersthatexploitkey
mance across I/O request flows targeting different sets of I/O architectural features of DSA (Section II-D). First, workers
queuesandscalesflexiblybyinstantiatingtheoptimalnumber descriptor batching asynchronous offloading
|     |     |     |     |     |     |     | use |     |     | and |     |     | to max- |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- |
of service units proportional to the target storage IOPS. imize DSA utilization. Each worker receives requests from
Coalesced request fetching. Beyond inter-queue paral- the dispatcher via its local queue. Rather than issuing copy
lelism from distributed dispatching, SwarmIO exploits intra- descriptors for each request, it collects multiple requests, up
queue parallelism via coalesced request fetching. Upon an to a predefined maximum batch size, into a single DSA
SQ doorbell update, a dispatcher identifies newly enqueued batchdescriptor (purpleinFigure6)toamortizetheoverhead
entriesandfetchesmultiplerequestsoverasingletransferinto of issuing copy descriptors. In addition, SwarmIO maintains
a reserved CPU memory region, the fetch buffer (Figure 6). multiple in-flight batch descriptors via asynchronous offload-
ThisoptimizationisparticularlyeffectiveunderGPU-initiated ing to overlap CPU-thread-side computation with DSA-side
I/Ofortworeasons.First,coalescedrequestfetchingnaturally data movement, while exploiting the DSA engine’s pipelined
aligns with the submission semantics of GPU-initiated I/O execution to overlap data transfers across batch descriptors.
where requests within a warp are submitted together to the Second, SwarmIO extends DSA acceleration not only to
same SQ via a single doorbell update [50]. Meanwhile, many worker-sidedatatransferemulationbutalsotodispatcher-side
warps interleave their accesses to SQ, causing a large number request fetching. Combined with coalesced request fetching,
of requests to accumulate in each SQ and creating ample this creates a significant opportunity to improve transfer ef-
opportunity to fetch these requests at once. Second, because ficiency by enabling each P2P DMA transaction to fetch up
request fetching in GPU-initiated I/O requires GPU-to-CPU to tens of KB. Together, these techniques enable SwarmIO’s
data transfer, coalesced fetching can merge multiple small frontend to sustain tens of MIOPS, which would not be
PCIe transactions, provided that SQ entries are physically achievable without either technique (see Section VI-C for an
contiguous. To enable this, SwarmIO sets the Contiguous ablation study). Overall, our DSA-accelerated data transfers
Queues Required (CQR) [44] bit to ‘1’ in the emulated con- effectively mitigate software overhead and establish high-
trollerregister,asdefinedbytheNVMespecification,ensuring throughput control and data paths for storage I/O emulation.

1 void do_async_batch_dsa_offloading(void) { for reuse across requests and provides interfaces for directly
2 ...
3 struct dsa_ctx *ctx; /* Setup per-thread DMA context */ programming DSA descriptors, including their use as batch
4 dsa_ctx_init(ctx, dev, wq, batch_size, num_desc, ...); descriptors. A representative asynchronous workflow enabled
5
6 while (!empty(queue)) { by our API is as follows:
7 for (i = 0; i < n; i++) { /* Add requests into a batch */
8 work = head(queue); 1) Batch descriptor construction (line 7–11): A thread col-
9 dsa_batch_issue_async(ctx, work.dest, work.src, lectsmultiplecopyoperationsintoasinglebatchdescrip-
10 work.len, ...);
11 } tor, and the API transparently issues the batch descriptor
12 do_something(); /* Perform useful computation */ once the maximum batch size is reached (i.e., i ≥
13
14 /* Issue the pending batch on timeout */ batch_size).
15 if (dsa_batch_should_issue_pending(ctx, s_timeout))
16 dsa_batch_issue_pending(ctx); 2) Computation pipelining (line 12): Instead of busy-
17 waiting, the thread performs useful computation while
18 /* Wait for the oldest in-flight batch on timeout */
19 if (dsa_batch_should_wait(ctx, c_timeout)) DSA processes data transfers. For instance, after issuing
20 dsa_batch_wait_oldest(ctx); newbatchdescriptors,SwarmIOworkersre-evaluatetheir
21 }
22 } localqueuestoprocessrequestswhosecopieshavecom-
pleted and target completion times have been reached.
Fig.7:Anexampleasynchronous,batcheddatatransferwork-
3) Timeout-driven issue (line 15–16): To ensure forward
flow using our DSA-aware kernel-level offloading API.
progress under low load, the thread explicitly issues the
current batch when pending entries remain and the con-
DSA-awarekernel-levelAPIforcopyoffloading.Tofully
figured timeout expires, as tracked by the DSA context.
unlockDSA’spotential,SwarmIOrequiresahigh-performance
4) Timeout-drivenwaiting(line19–20):Oncesufficienttime
kernel-level programming interface for offloading data trans-
has elapsed, the thread polls for completion of the oldest
fers because it is implemented as a kernel module. The
in-flight batch, thereby reducing unnecessary blocking.
standard Linux DMA Engine API [31] exposes diverse DMA
controllers via “hardware-agnostic” abstractions. While this Through this concurrent workflow, SwarmIO amortizes the
abstraction simplifies DMA usage, it fails to fully exploit overheadofissuingcopydescriptorsandoverlapsusefulcom-
DSA’s capabilities for three key reasons. First, the DMA En- putation with DSA-orchestrated data transfers, thereby over-
gineAPIdoesnotexposeDSA-specificfeatures.Forexample, comingthelimitationsofbaselineNVMeVirt,whichprimarily
although the DSA device driver (idxd) provides low-level relies on CPU thread-level parallelism for data transfers.
device control, the DMA Engine API exposes little beyond
2) DSA Configuration Tuning via Microbenchmarking:
idxd_dma_submit_memcpy(),whichsupportsonlynon-
Microbenchmark. To validate our API design and iden-
batched offloading of a single copy. Second, the default API
tify optimal DSA configurations for SwarmIO, this subsec-
solely relies on interrupt-driven notifications, even though
tion characterizes DSA performance using a microbench-
DSAalsosupportspolling.Thisinterrupt-baseddesignhinders
mark that models GPU-initiated I/O. At a high level, our
latency-sensitive completion handling, even though SwarmIO
microbenchmark fetches groups of I/O requests from the
requires timely request completions to preserve timing model
SQ (GPU→CPU), followed by the corresponding storage
fidelity. While polling preserves low latency, it incurs addi-
I/O operations (CPU→GPU), with the goal of identifying
tional CPU overhead; however, this cost can be effectively
the design points that maximize the throughput of frontend
hiddenbyissuingrequestsuptoDSA’smaximumconcurrency,
and backend of SwarmIO. The microbenchmark utilizes our
overlapping them with useful computation, and polling only
service unit abstraction that mirrors SwarmIO’s design. In
when necessary. Finally, because the API does not maintain
eachserviceunit,the(frontend)dispatcherperformssequential
per-thread offloading context (e.g., preallocated descriptor
4 KB GPU→CPU transfers to model coalesced fetching of
arrays and per-descriptor status), each thread must repeatedly
64 requests, while the (backend) workers perform strided
allocate and program DSA descriptors for every request. This
512-byte CPU→GPU transfers to model random 512-byte
incurs unnecessary control path overhead and prevents full
storage reads. Each service unit is mapped to a DSA group
utilization of the multi-threaded execution environment.
with one engine and two WQs, as shown in Figure 6. Our
Toaddressthesechallenges,wedesignaDSA-awarekernel- microbenchmark instantiates four service units over a single
level API that streamlines copy offloading in multi-threaded DSAdevicetofullyexploitthemaximumoffourDSAgroups
environments. As shown in Figure 7, the API operates via a supportedbyourdevice.Althoughthedispatcherandworkers
per-threadoffloadingcontext(i.e.,struct dsa_ctxinline operate independently in this microbenchmark, our goal is to
3). During initialization (dsa_ctx_init in line 4), each identifytheoperatingpointthatbalancesfrontendandbackend
thread configures its dedicated context (ctx) by specifying IOPS while maximizing overall system-level IOPS. Because
(1) the target DSA WQ (wq), (2) the maximum batch size one4KBdispatchertransferdrives64worker-sidetransfersin
(batch_size), and (3) the descriptor count (num_desc), SwarmIO,wefocusonmaximizingworkerIOPS;accordingly,
denotingtheper-threadWQdepth(i.e.,themaximumnumber we use asynchronous, batched offloading to DSA for workers
of in-flight descriptors maintained in the WQ) for asyn- and synchronous, non-batched offloading for the dispatcher.
chronous offloading. The API also preallocates descriptors We limit total dispatcher IOPS to 20 MIOPS (counting each

15 )sμ( ycnetaL 1.5 effective throughput across all service units is bounded by the
| SPOIM 10 |     |     |     |     | 1   | Issue | Wait |          |       |            |                        |     |          |     |
| -------- | --- | --- | --- | --- | --- | ----- | ---- | -------- | ----- | ---------- | ---------------------- | --- | -------- | --- |
|          |     |     |     |     |     |       |      | lower of | total | dispatcher | and worker throughput, |     | reaching | at  |
|          | 5   |     |     | 0.5 |     |       |      |          |       |            |                        |     |          |     |
most13.3MIOPSinpractice.Wethereforeuse13.3MIOPSas
|     | 0   |     |       |     | 0   |     |       |           |            |        |                 |         |     |       |
| --- | --- | --- | ----- | --- | --- | --- | ----- | --------- | ---------- | ------ | --------------- | ------- | --- | ----- |
|     |     |     |       |     |     |     |       | a per-DSA | throughput | target | for configuring | SwarmIO |     | under |
|     | 1 2 | 4 8 | 16 32 |     | 1 2 | 4 8 | 16 32 |           |            |        |                 |         |     |       |
Per-worker WQ depth Per-worker WQ depth GPU-initiated I/O; specifically, one worker per service unit
(a) IOPS (b) Latency breakdown with a batch size of around 4 is sufficient to saturate peak
| Fig. | 8: Effect | of SwarmIO’s |     | asynchronous | copy | offloading | on  |                 |     |             |           |       |         |     |
| ---- | --------- | ------------ | --- | ------------ | ---- | ---------- | --- | --------------- | --- | ----------- | --------- | ----- | ------- | --- |
|      |           |              |     |              |      |            |     | DSA performance |     | and achieve | this 13.3 | MIOPS | target. |     |
(a)workerthroughputand(b)theresultingworker-sidelatency
breakdown as the per-worker WQ depth varies. D. Aggregated Timing Model Updates
|          |     |       |       |          |       |        |     | SwarmIO’s      |     | timing model   | builds on            | top of | NVMeVirt’s |       |
| -------- | --- | ----- | ----- | -------- | ----- | ------ | --- | -------------- | --- | -------------- | -------------------- | ------ | ---------- | ----- |
|          |     | BS: 1 | BS: 2 | BS: 4    | BS: 8 | BS: 16 |     |                |     |                |                      |        |            |       |
|          |     |       |       |          |       |        |     | simple timing  |     | model (Section | II-C), parameterized |        | by         | maxi- |
| SPOIM 20 |     |       |       | SPOIM 20 |       |        |     |                |     |                |                      |        |            |       |
| 15       |     |       |       | 15       |       |        |     | mum throughput |     | and minimum    | latency. However,    |        | SwarmIO’s  |       |
| 10       |     |       |       | 10       |       |        |     |                |     |                |                      |        |            |       |
5 5 distributed frontend architecture introduces additional system
|     | 0                             |     |     |     | 0                             |     |     |                       |        |              |                   |        |        |       |
| --- | ----------------------------- | --- | --- | --- | ----------------------------- | --- | --- | --------------------- | ------ | ------------ | ----------------- | ------ | ------ | ----- |
|     |                               |     |     |     |                               |     |     | design considerations |        | for          | properly updating | the    | timing | model |
|     | 1                             | 2   | 4   |     | 1                             | 2   | 4   |                       |        |              |                   |        |        |       |
|     | # of workers per service unit |     |     |     | # of workers per service unit |     |     |                       |        |              |                   |        |        |       |
|     |                               |     |     |     |                               |     |     | across multiple       |        | dispatchers. |                   |        |        |       |
|     | (a) Total worker IOPS         |     |     |     | (b) Total dispatcher IOPS     |     |     |                       |        |              |                   |        |        |       |
|     |                               |     |     |     |                               |     |     | Global                | timing | model.       | One possible      | design | point  | is to |
Fig. 9: Effect of DSA’s batch size (BS) on (a) total worker use a local timing model per dispatcher, with each of the
| throughput |       | and (b)      | total dispatcher |          | throughput  | across | four |             |        |               |            |     |        |        |
| ---------- | ----- | ------------ | ---------------- | -------- | ----------- | ------ | ---- | ----------- | ------ | ------------- | ---------- | --- | ------ | ------ |
|            |       |              |                  |          |             |        |      | N timing    | models | configured    | to sustain | 1/N | of the | target |
| service    | units | instantiated | on               | a single | DSA device. |        |      |             |        |               |            |     |        |        |
|            |       |              |                  |          |             |        |      | throughput. | While  | this approach | simplifies | the | design | by     |
4 KB transfer as 64 I/O requests) and seek to maximize total eliminating inter-dispatcher dependencies, it cannot faithfully
worker IOPS up to this threshold. model skewed request distributions in which I/O requests
|        |     |              |     |     |                     |     |      | are concentrated |     | in only | a subset of SQs | and | are therefore |     |
| ------ | --- | ------------ | --- | --- | ------------------- | --- | ---- | ---------------- | --- | ------- | --------------- | --- | ------------- | --- |
| Effect | of  | asynchronous |     | and | batched offloading. |     | Fig- |                  |     |         |                 |     |               |     |
ure 8(a) shows the benefits of SwarmIO’s asynchronous copy handled by only a few dispatchers. Even if each active SQ
offloadingbyshowingtotalworkerIOPSasafunctionofper- is heavily loaded enough for a real SSD to achieve high
worker WQ depth, assuming a DSA batch size of 1 and one IOPS through sufficient intra-queue parallelism, the emulator
worker per service unit. Compared to a per-worker WQ depth withlocaltimingmodelsremainsconstrainedbytheaggregate
ofone(effectivelyequivalenttosynchronousoffloading),total capacity of only the few active timing models. Consequently,
worker IOPS increases by 3.3× at a WQ depth of 32. This we propose a global timing model shared across dispatchers
improvement is primarily driven by a significant reduction so that it can capture the global system load faithfully. With
in wait time for a copy descriptor to complete (Wait in such design, the timing model’s internal state, such as SSD
Figure 8(b), reduced by up to 9.8× on average), enabled resource availability, is shared across dispatchers and must
by overlapping multiple DSA-side data transfers, while copy- therefore be updated consistently to avoid race conditions. To
descriptor issue latency (Issue) remains nearly unchanged. this end, we protect the shared state with a lock, serializing
Figure9(a)furtherhighlightsourbatchdescriptorscheme’s timingmodelupdatesacrossdispatchersonaper-requestbasis.
|     |     |     |     |     |     |     |     | However, | this | design introduces | a tension | between | frontend |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---- | ----------------- | --------- | ------- | -------- | --- |
effectiveness.Tomaximizeconcurrencyacrossconfigurations,
we partition each DSA group’s maximum WQ depth (i.e., 32 scalabilityandserializationoverhead:sustaininghighfrontend
descriptors) among the workers in the corresponding service IOPS requires multiple dispatchers, but at high request rates,
unit while varying the number of workers per unit. We make thosedispatcherscontendmorefrequentlyforthesharedlock,
two key observations. First, batching substantially improves increasing serialization overhead and threatening scalability.
Aggregatedtimingmodelupdates.Toresolvethistension,
| offloading | efficiency, |     | saturating | total | worker IOPS | at  | approx- |     |     |     |     |     |     |     |
| ---------- | ----------- | --- | ---------- | ----- | ----------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
imately 22.1 MIOPS. Second, a single worker thread (i.e., we propose aggregated timing model updates, which preserve
single CPU core) per service unit is sufficient to achieve peak scalability by mitigating serialization overhead while preserv-
performance by maximizing both per-worker WQ depth and ing timing model semantics. Combined with our dispatcher’s
batch size. These results confirm that our API enables high- coalesced request fetching feature, this design allows each
throughputcopyoffloadingwithfewerCPUthreads(cores)by dispatcher to enter the critical section of timing model update
hiding data transfer latency via asynchronous offloading and once per fetched set of requests rather than once per request,
amortizing copy descriptor issue overhead through batching. as in the original design. Specifically, after fetching a set
Dispatcher vs. worker interference. Although our mi- of requests, a dispatcher first computes the corresponding
crobenchmark is configured to achieve 20 MIOPS of dis- state updates (i.e., aggregate scheduling-time increment for
patcherthroughput,therealizedthroughputgraduallydegrades each scheduling instance in Figure 2(b)), assuming back-
as the batch size increases (Figure 9(b), showing a 1.9× to-back scheduling of requests on their target instances. It
reduction when the worker batch size increases from 1 (non- then acquires the lock and applies these updates in a single
batched)to16).Thisdegradationarisesbecausethedispatcher step, thereby amortizing serialization overhead. Finally, each
andworkerswithinaserviceunitsharethesameDSAengine; request’s completion time is determined by assuming that
thus, aggressive worker offloading with large WQ depths and requests are assigned to scheduling instances in the order in
batch sizes can delay dispatcher progress. Consequently, the which they appear in the SQ.

V. METHODOLOGY
3
2
System configurations. We conduct our experiments on a 1
server with an Intel Xeon 6787P 86-core single-socket CPU 0
1 4 16 64 256 1K
and 256 GB of DDR5 DRAM. The CPU includes four DSA
devices (v2.0), and we configure each DSA device into four
DSA groups, each with one engine and two WQs. Each WQ
is set to a maximum depth of 32 and operates in dedicated
mode, as SwarmIO uses DSA exclusively within the kernel.
The server contains an NVIDIA H200 GPU [41] for GPU-
initiated I/O and a 1.92 TB Solidigm D7-PS1010 PCIe Gen5
SSD[54],whichweusetovalidatetheperformancemodeling
fidelity of SwarmIO on a modern enterprise-grade SSD.
We reserve 33 CPU cores and 128 GB of DRAM for SSD
emulation in both the baseline NVMeVirt and the proposed
SwarmIO systems. In both designs, all dispatcher and worker
threads are pinned to separate CPU cores. NVMeVirt uses
one dispatcher and 32 workers, whereas SwarmIO uses up to
16 service units, each consisting of one dispatcher and one
worker, with each service unit paired with a DSA group. In
SwarmIO, a single worker per service unit, combined with
asynchronous batched offloading, suffices to saturate DSA
performance.Bydefault,eachworkerusesanoffloadingbatch
sizeof16,largerthanthebatchsizeof4usedinSectionIV-C,
because end-to-end emulation introduces additional worker-
side tasks beyond data transfer, slightly reducing the batch
descriptor issue rate compared to our microbenchmark. Each
workermaintainsaWQdepthof32,whilethedispatcheruses
synchronous, non-batched offloading for request fetching.
Benchmarks.Weevaluaterandomstoragereadbenchmarks
using fio (v3.38) [2] for CPU-centric I/O and BaM [50] for
GPU-initiated I/O. For compatibility with our Linux kernel
version (v6.16.10), we use a patched BaM implementation
based on commit 315fadf. We use fio with a 4 KB I/O
size and the SPDK engine (v25.09) [57]. In fio, we scale
request-level parallelism by increasing the I/O depth while
fixing the number of fio threads at 32. With SPDK, each
fio thread uses a dedicated I/O queue pair, resulting in 32
queue pairs, each with a queue depth of 1,024. We use BaM
with a default I/O size of 512 bytes, 256 I/O queue pairs,
matching the maximum supported by the D7-PS1010 SSD,
and a queue depth of 1,024. This configuration supports on
the order of 100K concurrent requests. Accordingly, we set
the default number of GPU threads to 256K.
VI. EVALUATION
Inthissection,wefirstvalidateSwarmIO’sabilitytocapture
the performance characteristics of a modern PCIe Gen5 SSD
(Section VI-A), and then evaluate its scalability to next-
generation IOPS levels (Section VI-B). Next, we quantify
the contribution of each proposed optimization to SwarmIO’s
achievableIOPS(SectionVI-C).Finally,wepresentsensitivity
studies to further characterize its performance across a range
of I/O stack configurations (Section VI-D).
SPOIM
3
2
1
0
256 1K 4K 16K 64K256K
I/O depth
SPOIM
Real SSD SwarmIO NVMeVirt
# of GPU threads
(a) CPU-centric I/O (b) GPU-initiated I/O
Fig. 10: Sustained IOPS under (a) CPU-centric I/O (fio) and
(b) GPU-initiated I/O (BaM) for SwarmIO and NVMeVirt,
compared with a real SSD (Solidigm D7-PS1010).
1000
100 10
1
0.1
0.01
NVMeVSwarmIONVMeVSwarmIONVMeVSwarmIONVMeVSwarmIO
4K 16K 64K 256K
)sm(
ycnetaL
Target Proc E2E E2E (Real SSD)
# of GPU threads
Fig. 11: Average target completion latency from the timing
model (Target), request processing time to meet the target
(Proc), and end-to-end latency (E2E) of NVMeVirt and
SwarmIOunderGPU-initiatedI/O.Thereddottedlinedenotes
the end-to-end latency measured on the real SSD.
A. Emulator Validation
We first validate SwarmIO against a real SSD by profiling
theperformancecharacteristicsoftheD7-PS1010usingthefio
and BaM benchmarks. We then execute the same benchmarks
on NVMeVirt and SwarmIO, with their timing models cali-
brated to reproduce the D7-PS1010’s characteristics, specifi-
cally a minimum latency of 50 µs and a peak random-read
throughput of 2.47 MIOPS.
Throughput. As shown in Figure 10, SwarmIO effectively
captures the IOPS characteristics of a commodity SSD under
both CPU-centric I/O and GPU-initiated I/O. The average rel-
ativeIOPSerroris7.7%forfioand7.4%forBaM,indicating
close alignment with the real SSD in both settings. Although
SwarmIOexhibitsslightlyhigherIOPSunderlightinputloads
(e.g., at I/O depths below 16 in fio and with fewer than
4K GPU threads in BaM), it closely matches the SSD IOPS
under highly parallel conditions, which is typical of future
IOPS-optimizedSSDusecases.NVMeVirtisalsosufficiently
accuratetocapturetheSSDIOPSinCPU-centricI/O,withan
average relative IOPS error of 1.2% for fio. However, under
GPU-initiated I/O, it fails to reach the configured target IOPS
regardless of the degree of GPU thread-level parallelism, due
to the bottlenecks discussed in Section III-B.
Latency. NVMeVirt’s limited frontend scalability causes
requests to be fetched at a rate far below the submission
rateunderhighload,therebyincurringsubstantialSQqueuing
delays. GPU-initiated I/O further exacerbates this bottleneck.
Figure 11 illustrates the average target completion latency
(Target), internal request processing time used to realize
Target (Proc), and end-to-end latency including SQ queu-
ing delay (E2E) for NVMeVirt and SwarmIO under GPU-
initiated I/O. Because the single dispatcher becomes the bot-
tleneck in NVMeVirt, the timing model remains in the “low-
load”modeshowninFigure2(b)regardlessofthetruesystem

50 40 30
20
10
0
1 2 3 4
SPOIM 60 Target Measured 50 40
30
20
10
0
0102030405060
# of DSA devices
derusaeM SPOIM 8 6 4
2
0
1 4 16 64 256
TargetMIOPS
(a) (b)
Fig. 12: SwarmIO’s (a) peak IOPS as the number of DSA de-
vicesincreases,and(b)sustainedIOPSwithfourDSAdevices
when the target IOPS is scaled in 5 MIOPS increments.
load, and thus always derives Target as the configured
minimum latency of 50 µs. As the number of GPU threads
increases, Proc gradually deviates from Target, reaching
upto2.7×higher,suggestingthatNVMeVirt’sbackendcannot
sustain that degree of request-level parallelism and thus fails
to meet the target completion time. E2E also greatly exceeds
Proc,indicatingthatSQqueuingdelaydominatestheoverall
latency in NVMeVirt. Consequently, NVMeVirt’s E2E is on
average21.8×higherthanthatoftherealSSD(E2E (Real
SSD)), showing that SQ queuing delay severely undermines
modelingfidelity.Incontrast,SwarmIOpreventsthedispatch-
ers from becoming a bottleneck, allowing its timing model to
derive target completion latencies that closely match with the
target SSD’s average completion latency at each input load
level. In addition, DSA-accelerated data transfers allow the
workers to satisfy these target latencies, keeping SwarmIO’s
end-to-end latency remains close to that of the real SSD, with
an average relative error of 2.8%.
B. Scalability
We next evaluate the scalability of SwarmIO. As shown
in Figure 12(a), under GPU-initiated I/O, SwarmIO achieves
up to 9.8 MIOPS with a single DSA device, compared to
the 10 MIOPS target. This is close to the practical peak
DSA performance under dispatcher–worker interference re-
ported in Section IV-C, i.e., the minimum of dispatcher and
worker throughput when both operate concurrently. To scale
beyond a single DSA device, we increase the number of DSA
devices and, accordingly, the total number of service units.
Specifically, each DSA device serves four service units, each
mapped to a dedicated DSA group. With four DSA devices
(the maximum available in our server), SwarmIO achieves
up to 38.6 MIOPS at a 40 MIOPS target, corresponding to
a 303.9× speedup over NVMeVirt. It is worth pointing out
that SwarmIO is not limited to emulating only the maxi-
mum performance supported by the DSA devices. Using four
DSA devices, it can flexibly scale the target performance
to emulate storage across a range of operating points, as
shown in Figure 12(b), where we increase the target IOPS
of the timing model in 5 MIOPS increments starting from 5
MIOPS.SwarmIOsustainsmorethan96.6%oftheconfigured
target IOPS up to 40 MIOPS. Beyond this point, it can still
reach up to 45 MIOPS but no longer consistently matches
the configured target. While SwarmIO is currently limited to
40 MIOPS, this limit is primarily imposed by the available
DSA resources on our evaluation platform, rather than by an
SPOIM 12 31.9 52.6 8
4
0
256 1K 4K 16K 64K
I/O depth
SPOIM Base Base+D Base+D+A Base+D+C Base+D+A+C
# of GPU threads
(a) CPU-centric I/O (b) GPU-initiated I/O
Fig. 13: Effect of SwarmIO’s optimizations on baseline
NVMeVirt frontend performance (Base) by adding (D) a dis-
tributedarchitecturewith16dispatchers,(A)DSA-accelerated
request fetching, and (C) coalesced request fetching.
40 4 30 3
20 2
10 1
0 0
4 8 12 16
SPOIM pudeepS
Per-request update Aggregated update Speedup
# of service units
Fig.14:EffectofSwarmIO’saggregatedtimingmodelupdates
relativetothebaselineper-requestupdatesonachievableIOPS
under GPU-initiated I/O, while varying the number of service
units sharing a global timing model.
architecturallimitationofSwarmIO.Givenitsscalabledesign,
weexpectSwarmIOtoreach100MIOPStargetsunderascale-
upconfiguration,assumingadual-socketplatformprovisioned
with at least five DSA devices per socket.
C. Ablation Study
We conduct ablation studies to quantify the impact of each
proposed optimization on frontend scalability and to demon-
strate the effectiveness of aggregated timing model updates.
Frontend performance. Figure 13 shows how frontend
throughput, excluding backend data transfers, improves as we
add the following features to the baseline NVMeVirt (Base):
(D) a distributed architecture with 16 dispatchers, (A) DSA-
accelerated request fetching with synchronous offloading, and
(C)coalescedrequestfetchingthatallowsupto1,024requests
within an SQ to be fetched at once. Our analysis shows that,
under CPU-centric I/O, the distributed design with coalesced
fetching (D+C) alone, without DSA-accelerated request fetch-
ing, is sufficient to saturate the throughput supported by 32
CPU threads, reaching up to 6.5 MIOPS at an I/O depth
of 16 or higher. Under GPU-initiated I/O, the distributed
design alone does not scale beyond 1.5 MIOPS. Adding
either DSA-accelerated request fetching (D+A) or coalesced
fetching (D+C) to the distributed-only design improves fron-
tend scalability, delivering speedups of up to 2.8× and 6.2×,
respectively. Importantly, combining both optimizations with
the distributed design (D+A+C) increases frontend throughput
to at most 52.6 MIOPS, corresponding to a 537.2× speedup
over the baseline. This speedup is particularly pronounced
because large PCIe P2P DMA operations improve transfer ef-
ficiency, whileour high-throughput offloading APIand DSA’s
pipelined processing effectively hide data transfer latency.
Together,theseresultsshowthattheproposedtechniqueswork
synergistically to improve frontend performance.
Aggregated timing model updates. In addition, we evalu-
ate the effectiveness of our aggregated timing model updates.

45  htdiwdnaB DSA devices, we find that the aggregate DSA bandwidth
| SPOIM |     |     |     | 45    | IOPS Bandwidth |     | 45     |             |         |        |     |       |             |       |
| ----- | --- | --- | --- | ----- | -------------- | --- | ------ | ----------- | ------- | ------ | --- | ----- | ----------- | ----- |
|       | 30  |     |     | SPOIM |                |     | )s/BG( |             |         |        |     |       |             |       |
|       |     |     |     | 30    |                |     | 30     | for copying | data to | a PCIe | Gen | 5 ×16 | GPU reaches | up to |
15
15 15 42.1 GB/s at I/O sizes of 8 KB and above, still well below
|     |     |           |       |     | 0         |       | 0   |           |             |                |     |      |           |       |
| --- | --- | --------- | ----- | --- | --------- | ----- | --- | --------- | ----------- | -------------- | --- | ---- | --------- | ----- |
|     | 0   |           |       |     |           |       |     | the GPU’s | theoretical | unidirectional |     | PCIe | bandwidth | of 64 |
|     | 64  | 128256512 | 1K 2K | 4K  | 512 1K 2K | 4K 8K |     |           |             |                |     |      |           |       |
Block size (bytes)
# of I/O queue pairs GB/s. Nevertheless, SwarmIO achieves at least 44.6% of the
|      |                 | (a) |              |     | (b)       |      |            |             |                |     |         |               |     |              |
| ---- | --------------- | --- | ------------ | --- | --------- | ---- | ---------- | ----------- | -------------- | --- | ------- | ------------- | --- | ------------ |
|      |                 |     |              |     |           |      |            | theoretical | peak bandwidth |     | for I/O | sizes greater |     | than 1 KB, a |
| Fig. | 15: Sensitivity |     | of SwarmIO’s |     | sustained | IOPS | to (a) the |             |                |     |         |               |     |              |
levelthatnomodernenterprise-gradeSSDprovidesatsuchI/O
| number    | ofI/O | queuepairs |             | and(b) | I/Oblock | size underGPU- |     |                  |                       |     |        |             |          |           |
| --------- | ----- | ---------- | ----------- | ------ | -------- | -------------- | --- | ---------------- | --------------------- | --- | ------ | ----------- | -------- | --------- |
|           |       |            |             |        |          |                |     | sizes. Moreover, | according             |     | to the | StorageNext | roadmap  | [32],     |
| initiated | I/O   | with       | 2M threads. |        |          |                |     |                  |                       |     |        |             |          |           |
|           |       |            |             |        |          |                |     | [39], [40],      | future IOPS-optimized |     |        | SSDs are    | expected | to target |
In Figure 14, we scale the number of service units, along ultra-high IOPS at 512-byte granularity, and our emulator
with the corresponding number of DSA groups, and set the sustains 38.6 MIOPS at this operating point.
targetIOPSaccordingly,i.e.,10MIOPSforeveryfourservice
units. We then measure the achievable IOPS for designs VII. CASESTUDY:SCALINGUPGPU-CENTRICSTORAGE
| with | and without |     | aggregated | timing | model | updates. | Without |     |     |     |     |     |     |     |
| ---- | ----------- | --- | ---------- | ------ | ----- | -------- | ------- | --- | --- | --- | --- | --- | --- | --- |
SYSTEMSWITHFUTUREIOPS-OPTIMIZEDSSDS
| aggregated |     | updates, | per-request |     | timing model | updates | incur |     |     |     |     |     |     |     |
| ---------- | --- | -------- | ----------- | --- | ------------ | ------- | ----- | --- | --- | --- | --- | --- | --- | --- |
increasing contention as the number of dispatchers grows, AsintroducedinSectionI,GPU-initiatedI/Oisapromising
mechanismfordata-intensiveapplicationswithhighlyparallel,
| preventing |     | performance |     | from scaling | beyond | 10  | MIOPS. In |             |        |        |           |               |     |             |
| ---------- | --- | ----------- | --- | ------------ | ------ | --- | --------- | ----------- | ------ | ------ | --------- | ------------- | --- | ----------- |
|            |     |             |     |              |        |     |           | sparse, and | random | access | patterns. | To understand |     | the end-to- |
contrast,aggregatedtimingmodelupdatessubstantiallyreduce
serialization overhead across dispatchers. With 16 service end benefits of combining next generation, ultra-high IOPS-
|        |         |        |     |         |            |       |        | optimized | SSDs with | GPU-initiated |     | I/O in | such | applications, |
| ------ | ------- | ------ | --- | ------- | ---------- | ----- | ------ | --------- | --------- | ------------- | --- | ------ | ---- | ------------- |
| units, | SwarmIO | scales | to  | sustain | the target | of 40 | MIOPS, |           |           |               |     |        |      |               |
achieving a 3.6× speedup over the baseline design. we conduct a case study on GPU-accelerated, on-disk vector
|     |     |     |     |     |     |     |     | search [9], | [52], [58], | [60], | [61]. |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ----------- | ----- | ----- | --- | --- | --- |
D. Sensitivity Study GPU-accelerated, on-disk vector search.Asarepresenta-
We further examine the robustness and practical limits of tive case study, we focus on vector search, a core component
ofRAGsystemsforretrievingdata(e.g.,documentsorimages,
| SwarmIO |     | under different |     | I/O system | configurations. |     | Specifi- |     |     |     |     |     |     |     |
| ------- | --- | --------------- | --- | ---------- | --------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
cally,westudytheimpactofthenumberofI/Oqueuesandthe that is semantically relevant to a query in the embedding
SSDblocksize(i.e.,I/Ogranularity).Theformerisimportant space). We utilize CAGRA [45], a GPU-accelerated vector
|         |        |                |     |     |          |         |         | search algorithm | based | on  | graph-based |     | approximate | nearest |
| ------- | ------ | -------------- | --- | --- | -------- | ------- | ------- | ---------------- | ----- | --- | ----------- | --- | ----------- | ------- |
| because | future | IOPS-optimized |     |     | SSDs may | require | a wider |                  |       |     |             |     |             |         |
NVMehostinterfacetofullyexploitinternalparallelism,while neighbor search (ANNS). In graph-based ANNS, dataset vec-
|     |     |     |     |     |     |     |     | tors are indexed | as  | a graph, | and | the CAGRA | search | traverses |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | -------- | --- | --------- | ------ | --------- |
thelattermattersbecausetheoptimalI/Osizecanvaryacross
applications. We use the BaM benchmark because GPU- the graph toward nodes closer to the query to identify the
initiated I/O naturally exercises both dimensions by scaling top-k nearest vectors. Upon visiting a node corresponding to
|           |     |              |     |           |               |     |       | a dataset | vector, the | algorithm |     | (1) computes | the | distances |
| --------- | --- | ------------ | --- | --------- | ------------- | --- | ----- | --------- | ----------- | --------- | --- | ------------ | --- | --------- |
| thenumber |     | ofGPUthreads |     | toutilize | moreI/Oqueues |     | andby |           |             |           |     |              |     |           |
varying the I/O size via the GPU-side I/O buffer size. between the query and the node’s neighbors, (2) sorts the
Number of I/O queues. Figure 15(a) shows the robustness results by distance, and (3) iteratively extends the search by
ofSwarmIO’sperformancemodelingacrossvariousI/Oqueue proceeding to the closest, unvisited nodes until the configured
counts,withrequestssubmittedby2MGPUthreads.SwarmIO maximum number of iterations is reached.
sustains near-peak performance up to 1K queues, enabled We consider an on-disk vector search scenario [9], [52],
by our throughput-optimized frontend architecture combining [58], [60], [61] in which the entire vector index (i.e., both
distributed dispatching with coalesced request fetching via the graph structure and vector data) cannot fit in GPU or
DSA acceleration. Given an I/O depth of 1K, this is sufficient CPU memory. To enable direct SSD access from the GPU,
for 1M GPU threads to enqueue requests simultaneously. we integrate GPU-initiated I/O with CAGRA so that the
|        |     |         |            |     |            |       |            | GPU can | read index | data | directly | from the | SSD. | We use the |
| ------ | --- | ------- | ---------- | --- | ---------- | ----- | ---------- | ------- | ---------- | ---- | -------- | -------- | ---- | ---------- |
| Beyond | 1K  | queues, | achievable |     | IOPS falls | below | the target |         |            |      |          |          |      |            |
(e.g., reaching only 88.9% of the 40 MIOPS target at 2K BIGANN-100M dataset [53], whose CAGRA index occupies
queues) because the sequential overhead of processing many 71.5 GB. To emulate a larger-scale deployment, we evaluate
SQs begins to constrain frontend dispatch throughput. a downscaled configuration in which the GPU memory avail-
Block size. Figure 15(b) shows overall performance as the able for CAGRA search is limited to 2 GB. This preserves
|     |     |     |     |     |     |     |     | approximately | the | same GPU | memory-to-index |     | ratio | as a 144 |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | -------- | --------------- | --- | ----- | -------- |
blocksizevaries.Astheblocksizeincreases,achievableIOPS
drops from the peak at 512 bytes. For example, SwarmIO GB H200 GPU serving a 5 TB index, a practical scale for
achieves 15.1 MIOPS with 2 KB blocks. We attribute this vector search over billions of vectors [51].
limit to practical platform constraints when DSA devices ImplicationoffutureIOPS-optimizedSSDs.Wemeasure
transfer data to a peer PCIe device (i.e., GPU) across distinct CAGRA search throughput, i.e., queries per second (QPS),
PCIe controllers to which the devices are attached. As the while varying SSD IOPS using SwarmIO. In this experiment,
block size increases, transfer efficiency improves, and the we set the block size to 512 bytes, corresponding to the
achievable bandwidth correspondingly rises, but only up to 128-dimensional FP32 vector size. As shown in Figure 16(a),
about 40 GB/s. Specifically, through stress testing with four increasing SSD IOPS provides little benefit at a small batch

6
4
2
0
2.5 M 5 M 10 M 20 M 40 M
SPQk
8
6
4
2
0
2.5 M 5 M 10 M 20 M 40 M
W: 2 W: 4 W: 8 W: 16
IOPS
SPQk
BS: 1 BS: 4 BS: 16 BS: 64 BS: 256 Several studies [1], [8], [12], [13], [16], [21], [59] develop
detailed SSD simulators for modeling SSD’s internal device-
levelbehavior,whileintegratingthemintofull-systemsimula-
tion environments. While effective for modeling internal SSD
IOPS behavior, they do not support real-time modeling of GPU-
(a) Sensitivity to batch size centric storage systems. Prior emulators [20], [28], [33], [62]
instead expose software-defined SSDs to systems for end-to-
end evaluation. FEMU [28] adopts a QEMU-based virtual-
ization approach, while NVMeVirt [20] presents a software-
defined PCI NVMe device to the host system and supports
versatile storage emulation environments. Recent studies fur-
(b) Sensitivity to search width ther extend SSD emulation to emerging interfaces and de-
Fig. 16: End-to-end performance of on-disk CAGRA search vice classes [11], [55], [63], [66], but still primarily target
when scaling SwarmIO target IOPS from 2.5 to 40 MIOPS: conventional CPU-centric storage settings rather than GPU-
(a) sensitivity to batch size (BS) at search width 4, and (b) centric storage systems. Some prior works [15], [25], [64]
sensitivity to search width (W) at batch size 64. utilizeFPGA-basedplatformsforSSDprototyping.Whilethey
size (BS) of 4 because the CAGRA search generates insuf- offerhardwareaccelerationwithnativePCIeconnectivity,they
ficient parallel storage I/O to utilize the additional IOPS. As require specialized hardware and expertise. A growing body
batchsizeincreases,however,thebenefitofhigherSSDIOPS of work uses these modeling frameworks to study real-world
becomes clear. Scaling SSD IOPS by 16×, from 2.5 to 40 applications whose performance depends on SSD designs not
MIOPS, yields a 9.7× end-to-end speedup of CAGRA search yetcommerciallyavailable[7],[30],[35],[46],[67].SwarmIO
at a batch size of 256. In other words, higher storage IOPS broadens this line of work by enabling performance modeling
enables larger batch sizes by allowing more vector fetches foranewclassofapplicationswithnextgenerationultra-high
from storage to proceed in parallel, thereby improving QPS. IOPS demands in GPU-centric storage environments.
Looking forward: the need for IOPS-aware algorithmic GPU-centric storage systems. Numerous prior studies
shifts.Increasingsearchwidththroughbeamsearch[45],[58], exploreGPU-centricstoragesystemstomeetthehighrandom-
which expands the search frontier by visiting multiple graph access IOPS demands of data-intensive workloads. BaM [50]
nodes in parallel at each iteration, allows the algorithm to enables high-IOPS GPU-initiated I/O for fine-grained random
explore more nodes per iteration and can potentially reduce accesses. GIDS [47] applies GPU-initiated I/O to GNN train-
the total number of search iterations needed to reach a target ingwithsparseandirregularaccesses,andGMT[5]proposesa
accuracy. In ANNS, recall is the primary accuracy metric GPU-orchestrated memory hierarchy spanning GPU memory,
and is defined as the fraction of ground-truth top-k neighbors host memory, and SSDs. Other studies propose GPU-centric
included in the retrieved results. We first profile CAGRA file systems [29], [48] or extend GPU-initiated I/O with asyn-
search offline by varying the search width and identifying, for chronousexecutiontooverlapI/Oandcomputation[10],[56].
each search width, the minimum number of search iterations There is also a growing industry trend toward satisfying the
required to guarantee at least 95% recall. We then apply IOPSdemandofsuchsystemsatthestorage-devicelevel[40].
the corresponding iteration count for each search width and Ourworkstandsapartfromthisliteraturebyfocusingonend-
measure QPS while varying both search width and SSD to-end performance modeling of GPU-centric storage systems
IOPS. As shown in Figure 16(b), the optimal search width while enabling flexible scaling of storage IOPS.
(W) depends on the provisioned IOPS. For example, a search
width of 2 is optimal at 5 MIOPS or below, whereas a
search width of 4 becomes faster at 10 MIOPS or above. IX. CONCLUSION
This result suggests that future ultra-high IOPS SSDs can
shift the optimal algorithmic configuration for maximizing GPU-initiated I/O introduces a fundamentally different op-
end-to-endperformance,highlightingtheneedforIOPS-aware erating regime for storage systems, where massive numbers
algorithmic shifts in data-intensive applications running on of GPU threads generate fine-grained requests at extreme
next generation GPU-centric storage systems. rates. Existing SSD emulation frameworks are not designed
to handle this level of parallelism and IOPS, limiting their ef-
VIII. RELATEDWORK
fectiveness in studying emerging GPU-centric workloads. We
ThereexistsalargebodyofpriorworkonSSDperformance present SwarmIO, an SSD emulation framework that sustains
modeling, and numerous prior studies have also explored tensofmillionsofIOPSwhilepreservingaccurateend-to-end
GPU-centric storage systems, which represent the primary behavior. Our evaluation shows that it closely matches real
target environments for SwarmIO. We briefly summarize the SSD performance and enables scalable exploration of GPU-
most relevant studies below. centric storage. SwarmIO provides a practical foundation for
SSD performance modeling. Prior work on SSD per- studyingIOPS-intensiveworkloadsandhighlightsthegrowing
formance modeling spans both simulation and emulation. importance of storage scalability in GPU-centric computing.

ACKNOWLEDGMENT
|     |     |     |     |     |     |     |     | [16] M.Jung,W.Choi,S.Gao,E.H.WilsonIII,D.Donofrio,J.Shalf,and |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
M.T.Kandemir,“Nandflashsim:High-fidelity,microarchitecture-aware
This work was supported in part by SK hynix, which nandflashmemorysimulation,”ACMTrans.Storage,2016.
provided funding for the study and design of SwarmIO, [17] M. Khairy, Z. Shen, T. M. Aamodt, and T. G. Rogers, “Accel-Sim:
AnExtensibleSimulationFrameworkforValidatedGPUModeling,”in
| and in | part by | Institute | of Information |     | &   | Communications |     |     |     |     |     |     |     |     |     |
| ------ | ------- | --------- | -------------- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ProceedingsoftheInternationalSymposiumonComputerArchitecture
| Technology | Planning |     | & Evaluation(IITP) |     |     | grant funded | by  | (ISCA),2020. |     |     |     |     |     |     |     |
| ---------- | -------- | --- | ------------------ | --- | --- | ------------ | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |
the Korea government(MSIT) (No.RS-2024-00438851, (SW [18] C.Kim,“BeyondSSD:SKHynixAINFamilyRedefiningStorageas
theCoreEnablerofAIatScalepresentedbySKHynix,”OpenCompute
Starlab)High-performancePrivacy-preservingMachineLearn-
Project(OCP)GlobalSummit,2025.
| ing System | and | System | Software), |     | (No.RS-2025-02264029, |     |     |                                                                |     |     |     |     |     |     |     |
| ---------- | --- | ------ | ---------- | --- | --------------------- | --- | --- | -------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|            |     |        |            |     |                       |     |     | [19] J.Kim,B.Shin,J.Chung,andM.Rhu,“Thecostofdynamicreasoning: |     |     |     |     |     |     |     |
ImplementationandValidationofanAISemiconductor-Based Demystifying ai agents and test-time scaling from an ai infrastructure
|             |            |     |         |                 |     |       |       | perspective,” |     | in Proceedings | of  | the International |     | Symposium | on High- |
| ----------- | ---------- | --- | ------- | --------------- | --- | ----- | ----- | ------------- | --- | -------------- | --- | ----------------- | --- | --------- | -------- |
| Data Center | Composable |     | Cluster | Infrastructure, |     | 30%), | which |               |     |                |     |                   |     |           |          |
PerformanceComputerArchitecture(HPCA),2026.
| provided | the computing |     | infrastructure |     | (CPU | and GPU) | used |            |      |          |         |           |          |     |            |
| -------- | ------------- | --- | -------------- | --- | ---- | -------- | ---- | ---------- | ---- | -------- | ------- | --------- | -------- | --- | ---------- |
|          |               |     |                |     |      |          |      | [20] S.-H. | Kim, | J. Shim, | E. Lee, | S. Jeong, | I. Kang, | and | J.-S. Kim, |
in this study. “NVMeVirt: A Versatile Software-defined Virtual NVMe Device,” in
ProceedingsoftheConferenceonFileandStorageTechnologies(FAST),
2023.
REFERENCES
|                 |     |                 |     |            |       |        |             | [21] Y.Kim,B.Tauras,A.Gupta,andB.Urgaonkar,“Flashsim:Asimulator |                  |     |             |          |         |       |               |
| --------------- | --- | --------------- | --- | ---------- | ----- | ------ | ----------- | --------------------------------------------------------------- | ---------------- | --- | ----------- | -------- | ------- | ----- | ------------- |
|                 |     |                 |     |            |       |        |             | for                                                             | nand flash-based |     | solid-state | drives,” | in 2009 | First | International |
| [1] N. Agrawal, |     | V. Prabhakaran, |     | T. Wobber, | J. D. | Davis, | M. Manasse, |                                                                 |                  |     |             |          |         |       |               |
ConferenceonAdvancesinSystemSimulation,2009.
| and | R. Panigrahy, | “Design | tradeoffs | for | ssd performance,” |     | in USENIX |              |     |         |       |        |              |       |           |
| --- | ------------- | ------- | --------- | --- | ----------------- | --- | --------- | ------------ | --- | ------- | ----- | ------ | ------------ | ----- | --------- |
|     |               |         |           |     |                   |     |           | [22] KIOXIA, |     | “KIOXIA | CM9-V | Series | (2.5-inch),” | 2025. | [Online]. |
AnnualTechnicalConference(ATC),2008.
|               |           |     |              |       |           |            |        | Available:     |     | https://americas.kioxia.com/en-us/business/ssd/enterprise- |     |     |     |     |     |
| ------------- | --------- | --- | ------------ | ----- | --------- | ---------- | ------ | -------------- | --- | ---------------------------------------------------------- | --- | --- | --- | --- | --- |
| [2] J. Axboe, | “Flexible |     | I/O Tester,” | 2024. | [Online]. | Available: | https: | ssd/cm9-v.html |     |                                                            |     |     |     |     |     |
//github.com/axboe/fio
|     |     |     |     |     |     |     |     | [23] ——, | “KIOXIA |     | XL-FLASH,” |     | 2025. | [Online]. | Avail- |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------- | --- | ---------- | --- | ----- | --------- | ------ |
[3] N.Binkert,B.Beckmann,G.Black,S.K.Reinhardt,A.Saidi,A.Basu,
able: https://kr.kioxia.com/content/dam/kioxia/shared/business/memory/
J.Hestness,D.R.Hower,T.Krishna,S.Sardashti,R.Sen,K.Sewell,
|     |         |           |       |           |       |       |           | xlflash/asset/KIOXIA |        |           | XL-FLASH | Infographic.pdf |                 |     |         |
| --- | ------- | --------- | ----- | --------- | ----- | ----- | --------- | -------------------- | ------ | --------- | -------- | --------------- | --------------- | --- | ------- |
| M.  | Shoaib, | N. Vaish, | M. D. | Hill, and | D. A. | Wood, | “The gem5 |                      |        |           |          |                 |                 |     |         |
|     |         |           |       |           |       |       |           | [24] R.              | Kuper, | I. Jeong, | Y. Yuan, | R. Wang,        | N. Ranganathan, |     | N. Rao, |
Simulator,”ACMSIGARCHComputerArchitectureNews,2011.
|     |     |     |     |     |     |     |     | J. Hu, | S. Kumar, | P. Lantz, | and | N. S. | Kim, “A | Quantitative | Analysis |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --------- | --------- | --- | ----- | ------- | ------------ | -------- |
[4] R.Bolt,“HighIOPSSSDsforAIUseCases,”FlashMemorySummit and Guidelines of Data Streaming Accelerator in Modern Intel Xeon
(FMS),2025.
|           |        |         |                     |     |     |        |            | Scalable         | Processors,” |         | in Proceedings  |     | of the International |     | Conference |
| --------- | ------ | ------- | ------------------- | --- | --- | ------ | ---------- | ---------------- | ------------ | ------- | --------------- | --- | -------------------- | --- | ---------- |
| [5] C.-H. | Chang, | J. Han, | A. Sivasubramaniam, |     | V.  | Sharma | Mailthody, |                  |              |         |                 |     |                      |     |            |
|           |        |         |                     |     |     |        |            | on Architectural |              | Support | for Programming |     | Languages            | and | Operating  |
Z.Qureshi,andW.-m.Hwu,“GMT:GPUOrchestratedMemoryTiering
Systems(ASPLOS),2024.
| for the          | Big Data | Era,”   | in Proceedings  | of  | the International |     | Conference |                                                               |     |     |     |     |     |     |     |
| ---------------- | -------- | ------- | --------------- | --- | ----------------- | --- | ---------- | ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|                  |          |         |                 |     |                   |     |            | [25] J.Kwak,S.Lee,K.Park,J.Jeong,andY.H.Song,“Cosmos+OpenSSD: |     |     |     |     |     |     |     |
| on Architectural |          | Support | for Programming |     | Languages         | and | Operating  |                                                               |     |     |     |     |     |     |     |
Systems(ASPLOS),2024. Rapid Prototype for Flash Storage Systems,” ACM Transactions on
Storage,2020.
[6] W.W.Fung,I.Sham,G.Yuan,andT.M.Aamodt,“DynamicWarpFor-
|     |     |     |     |     |     |     |     | [26] J. Lee | and | R. Stenfort, | “FADU: | Pushing | the Storage | Frontier: | Next- |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ------------ | ------ | ------- | ----------- | --------- | ----- |
mationandSchedulingforEfficientGPUControlFlow,”inProceedings
GenerationSSDsforTomorrow’sDatacenters,”FlashMemorySummit
oftheInternationalSymposiumonMicroarchitecture(MICRO),2007.
(FMS),2025.
| [7] N. M. | Ghiasi, | M. Sadrosadati, |     | H. Mustafa, | A.  | Gollwitzer, | C. Firtina, |     |     |     |     |     |     |     |     |
| --------- | ------- | --------------- | --- | ----------- | --- | ----------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
J. Eudine, H. Mao, J. Lindegger, M. B. Cavlak, M. Alser, J. Park, [27] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal,
andO.Mutlu,“Megis:High-performance,energy-efficient,andlow-cost H.Ku¨ttler,M.Lewis,W.-t.Yih,T.Rockta¨schel,S.Riedel,andD.Kiela,
“Retrieval-AugmentedGenerationforKnowledge-IntensiveNLPTasks,”
metagenomicanalysiswithin-storageprocessing,”inProceedingsofthe
|     |     |     |     |     |     |     |     | in Proceedings |     | of the | International | Conference |     | on Neural | Information |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------ | ------------- | ---------- | --- | --------- | ----------- |
InternationalSymposiumonComputerArchitecture(ISCA),2024.
ProcessingSystems(NeurIPS),2020.
[8] D.Gouk,M.Kwon,J.Zhang,S.Koh,W.Choi,N.S.Kim,M.Kandemir,
and M. Jung, “Amber: Enabling Precise Full-system Simulation with [28] H.Li,M.Hao,M.H.Tong,S.Sundararaman,M.Bjørling,andH.S.
Detailed Modeling of All SSD Resources,” in Proceedings of the Gunawi,“TheCaseofFEMU:Cheap,Accurate,ScalableandExtensible
FlashEmulator,”inProceedingsoftheConferenceonFileandStorage
InternationalSymposiumonMicroarchitecture(MICRO),2018.
Technologies(FAST),2018.
[9] H.GuoandY.Lu,“AchievingLow-LatencyGraph-BasedVectorSearch
|     |     |     |     |     |     |     |     | [29] S. Li, | Y. E. | Zhou, Y. | Xue, Y. | Xu, and | J. Huang, | “Managing | Scalable |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ----- | -------- | ------- | ------- | --------- | --------- | -------- |
viaAligningBest-FirstSearchAlgorithmwithSSD,”inProceedingsof
the USENIX Symposium on Operating Systems Design and Implemen- Direct Storage Accesses for GPUs with GoFS,” in Proceedings of the
tation(OSDI),2025. ACMSymposiumonOperatingSystemsPrinciples(SOSP),2025.
[10] J.Han,A.Sivasubramaniam,C.-H.Chang,V.S.Mailthody,Z.Qureshi, [30] S. Li, F. Tu, L. Liu, J. Lin, Z. Wang, Y. Kang, Y. Ding, and Y. Xie,
|         |            |             |                |           |                   |      |            | “Ecssd: | Hardware/data |                          | layout | co-designed    | in-storage-computing |        | archi-        |
| ------- | ---------- | ----------- | -------------- | --------- | ----------------- | ---- | ---------- | ------- | ------------- | ------------------------ | ------ | -------------- | -------------------- | ------ | ------------- |
| and     | W.-M. Hwu, | “Asynchrony |                | and GPUs: | Bridging          | this | Dichotomy  |         |               |                          |        |                |                      |        |               |
|         |            |             |                |           |                   |      |            | tecture | for           | extreme classification,” |        | in Proceedings |                      | of the | International |
| for I/O | with       | AGIO,”      | in Proceedings | of        | the International |      | Conference |         |               |                          |        |                |                      |        |               |
on Architectural Support for Programming Languages and Operating SymposiumonComputerArchitecture(ISCA),2023.
Systems(ASPLOS),2026. [31] Linux Kernel Organization, “DMAEngine documentation,” 2026.
[11] K. Han, H. Gwak, D. Shin, and J. Hwang, “ZNS+: Advanced Zoned [Online]. Available: https://www.kernel.org/doc/html/latest/driver-api/
| Namespace   | Interface |               | for Supporting | In-Storage |              | Zone Compaction,” |        | in dmaengine/index.html |            |            |     |        |             |               |     |
| ----------- | --------- | ------------- | -------------- | ---------- | ------------ | ----------------- | ------ | ----------------------- | ---------- | ---------- | --- | ------ | ----------- | ------------- | --- |
|             |           |               |                |            |              |                   |        | [32] V. S.              | Mailthody, | “Advancing |     | Memory | and Storage | Architectures | for |
| Proceedings |           | of the USENIX | Symposium      |            | on Operating | Systems           | Design |                         |            |            |     |        |             |               |     |
andImplementation(OSDI),2021. Next-GenAIWorkloads,”FlashMemorySummit(FMS),2025.
[12] J. He, S. Kannan, A. C. Arpaci-Dusseau, and R. H. Arpaci-Dusseau, [33] K.T.Malladi,M.Awasthi,andH.Zheng,“FlexDrive:AFrameworkto
“The unwritten contract of solid state drives,” in Proceedings of the ExploreNVMeStorageSolutions,”inProceedingsoftheInternational
TwelfthEuropeanConferenceonComputerSystems,2017. Conference on High Performance Computing and Communications;
[13] Y.Hu,H.Jiang,D.Feng,L.Tian,H.Luo,andS.Zhang,“Performance International Conference on Smart City; International Conference on
DataScienceandSystems(HPCC/SmartCity/DSS),2016.
| impact | and interplay |     | of ssd parallelism |     | through | advanced | commands, |     |     |     |     |     |     |     |     |
| ------ | ------------- | --- | ------------------ | --- | ------- | -------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
allocationstrategyanddatagranularity,”inProceedingsoftheInterna- [34] Marvell, “Marvell Bravera SC5 SSD Controllers,” 2021. [Online].
tionalConferenceonSupercomputing,2011. Available: https://www.marvell.com/content/dam/marvell/en/public-
[14] Intel, “Intel Data Streaming Accelerator (Intel DSA),” 2022. collateral/storage/marvell-ssd-mv-ss1331-1333-product-brief.pdf
[Online].Available:https://www.intel.com/content/www/us/en/products/ [35] K. K. Matam, G. Koo, H. Zha, H.-W. Tseng, and M. Annavaram,
docs/accelerator-engines/data-streaming-accelerator.html “Graphssd: Graph semantics aware ssd,” in Proceedings of the Inter-
[15] M. Jung, “OpenExpress: Fully Hardware Automated Open Research nationalSymposiumonComputerArchitecture(ISCA),2019.
FrameworkforFutureFastNVMeDevices,”inUSENIXAnnualTech- [36] Micron, “9550 NVMe SSD,” 2024. [Online]. Available: https:
nicalConference(ATC),2020. //www.micron.com/products/storage/ssd/data-center-ssd/9550-ssd

[37] M. Naumov, D. Mudigere, H.-J. M. Shi, J. Huang, N. Sundaraman, [57] SPDK, “SPDK: NVMe Driver,” 2026. [Online]. Available: https:
J.Park,X.Wang,U.Gupta,C.-J.Wu,A.G.Azzolini,D.Dzhulgakov, //spdk.io/doc/nvme.html
A.Mallevich,I.Cherniavskii,Y.Lu,R.Krishnamoorthi,A.Yu,V.Kon- [58] S. J. Subramanya, Devvrit, R. Kadekodi, R. Krishaswamy, and H. V.
dratenko, S. Pereira, X. Chen, W. Chen, V. Rao, B. Jia, L. Xiong, Simhadri, “DiskANN: Fast Accurate Billion-point Nearest Neighbor
and M. Smelyanskiy, “Deep Learning Recommendation Model for SearchonaSinglenode,”inProceedingsoftheInternationalConference
PersonalizationandRecommendationSystems,”inarxiv.org,2019. onNeuralInformationProcessingSystems(NeurIPS),2019.
[38] C. J. Newburn and W.-m. Hwu, “Storage Implications for the New [59] A.Tavakkol,J.Go´mez-Luna,M.Sadrosadati,S.Ghose,andO.Mutlu,
Generation of AI Applications,” SNIA Developer Conference (SDC), “MQSim:AFrameworkforEnablingRealisticStudiesofModernMulti-
2025. Queue SSD Devices,” in Proceedings of the Conference on File and
[39] C.J.NewburnandV.S.Mailthody,“TechnicalPathstotheNewEraof StorageTechnologies(FAST),2018.
[60] B.Tian,H.Liu,Y.Tang,S.Xiao,Z.Duan,X.Liao,H.Jin,X.Zhang,
GPU-initiatedStorage,”OpenComputeProject(OCP)GlobalSummit,
2025. J. Zhu, and Y. Zhang, “Towards High-throughput and Low-latency
[40] C. Newburn, P. Prabhu, and V. S. Mailthody, “StorageNext for AI: Billion-scale Vector Search via CPU/GPU Collaborative Filtering and
HowtoEliminatetheMemoryWallforGenAIandLLMWorkloads,” Re-ranking,” in Proceedings of the Conference on File and Storage
NVIDIA GTC, 2025. [Online]. Available: https://www.nvidia.com/en- Technologies(FAST),2025.
|     |     |     |     |     |     |     |     |     | [61] M. Wang, | W. Xu, | X. Yi, S. Wu, | Z. Peng, | X. Ke, | Y. Gao, | X. Xu, |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- | ------ | ------------- | -------- | ------ | ------- | ------ |
us/on-demand/session/gtc25-s73012/
[41] NVIDIA, “NVIDIA H200 GPU,” 2024. [Online]. Available: https: R. Guo, and C. Xie, “Starling: An I/O-Efficient Disk-Resident Graph
//www.nvidia.com/en-us/data-center/h200/ Index Framework for High-Dimensional Vector Similarity Search on
[42] ——, “GPUDirect RDMA,” 2026. [Online]. Available: https://docs. DataSegment,”ProceedingsoftheACMonManagementofData,2024.
nvidia.com/cuda/pdf/GPUDirect RDMA.pdf [62] J. Yoo, Y. Won, J. Hwang, S. Kang, J. Choi, S. Yoon, and J. Cha,
“VSSIM:VirtualMachinebasedSSDSimulator,”inProceedingsofthe
| [43] ——, | “NVIDIA | CMX | Context |     | Memory | Storage | Platform,” |     |     |     |     |     |     |     |     |
| -------- | ------- | --- | ------- | --- | ------ | ------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
2026.[Online].Available:https://www.nvidia.com/en-us/data-center/ai- SymposiumonMassStorageSystemsandTechnologies(MSST),2013.
storage/cmx/ [63] D. Yoon, H. Idden, J. Liu, B. Inceisci, S. H. Noh, and H. Li, “Cylon:
[44] NVM Express, “NVM Express Base Specification,” 2026. Fast and accurate full-system emulation of cxl-ssds,” in 24th USENIX
[Online]. Available: https://nvmexpress.org/specification/nvm-express- ConferenceonFileandStorageTechnologies(FAST26),2026.
|     |     |     |     |     |     |     |     |     | [64] L. Yu, | Y. Lu, M. | Mandava, E. | Richter, | V. S. Mailthody, | S. W. | Min, |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --------- | ----------- | -------- | ---------------- | ----- | ---- |
base-specification/
[45] H. Ootomo, A. Naruse, C. Nolet, R. Wang, T. Feher, and Y. Wang, W.-m. Hwu, and D. Chen, “Fssd: Fpga-based emulator for ssds,” in
“Cagra: Highly parallel graph construction and approximate nearest 202333rdInternationalConferenceonField-ProgrammableLogicand
neighbor search for gpus,” in Proceedings of the International Con- Applications(FPL),2023.
ferenceonDataEngineering(ICDE),2024. [65] Y. Yuan, R. Wang, N. Ranganathan, N. Rao, S. Kumar, P. Lantz,
|              |        |        |           |          |     |          |         |       | V. Sanjeepan, | J.Cabrera, | A. Kwatra, | R.Sankaran, | I. Jeong, | andN. | S.  |
| ------------ | ------ | ------ | --------- | -------- | --- | -------- | ------- | ----- | ------------- | ---------- | ---------- | ----------- | --------- | ----- | --- |
| [46] X. Pan, | E. Li, | Q. Li, | S. Liang, | Y. Shan, | K.  | Zhou, Y. | Luo, X. | Wang, |               |            |            |             |           |       |     |
andJ.Zhang,“InstAttention:In-StorageAttentionOffloadingforCost- Kim, “Intel Accelerators Ecosystem: An SoC-Oriented Perspective :
EffectiveLong-ContextLLMInference,”inProceedingsoftheInterna- Industry Product,” in Proceedings of the International Symposium on
tionalSymposiumonHigh-PerformanceComputerArchitecture(HPCA), ComputerArchitecture(ISCA),2024.
2025. [66] Q. Zhang, J. Wang, Y. Zhou, P. Xu, K. Lu, J. Wan, F. Wu, and
T.Lu,“Cemu:Enablingfull-systememulationofcomputationalstorage
| [47] J. B. | Park, V. | S. Mailthody, | Z.  | Qureshi, | and | W.-m. Hwu, | “Accelerat- |     |     |     |     |     |     |     |     |
| ---------- | -------- | ------------- | --- | -------- | --- | ---------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
ing Sampling and Aggregation Operations in GNN Frameworks with beyondhardwarelimits,”inProceedingsoftheInternationalConference
GPU Initiated Direct Storage Accesses,” in Proceedings of the VLDB on Architectural Support for Programming Languages and Operating
| Endowment(PVLDB),2024. |           |            |         |           |         |          |            |        | Systems(ASPLOS),2026. |               |                  |              |                |     |        |
| ---------------------- | --------- | ---------- | ------- | --------- | ------- | -------- | ---------- | ------ | --------------------- | ------------- | ---------------- | ------------ | -------------- | --- | ------ |
|                        |           |            |         |           |         |          |            |        | [67] C. Zou           | and A. A.     | Chien, “Assasin: | Architecture | support        | for | stream |
| [48] S. Qiu,           | W. Liu,   | Y. Hu,     | J. Yan, | Z. Shen,  | X. Yao, | R. Chen, | G.         | Zhang, |                       |               |                  |              |                |     |        |
|                        |           |            |         |           |         |          |            |        | computing             | to accelerate | computational    | storage,”    | in Proceedings |     | of the |
| and                    | Y. Zhang, | “GeminiFS: | A       | Companion | File    | System   | for GPUs,” | in     |                       |               |                  |              |                |     |        |
ProceedingsoftheConferenceonFileandStorageTechnologies(FAST), InternationalSymposiumonMicroarchitecture(MICRO),2022.
2025.
| [49] Y. Qiu, | W.  | Yin, and | L. Wang, | “A  | high-performance |     | and | scalable |     |     |     |     |     |     |     |
| ------------ | --- | -------- | -------- | --- | ---------------- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
nvmecontrollerfeaturinghardwareacceleration,”IEEETransactionson
Computer-AidedDesignofIntegratedCircuitsandSystems,2022.
| [50] Z. Qureshi, |           | V. S. Mailthody,  |            | I. Gelado,     | S. Min,          | A. Masood,     |         | J. Park, |     |     |     |     |     |     |     |
| ---------------- | --------- | ----------------- | ---------- | -------------- | ---------------- | -------------- | ------- | -------- | --- | --- | --- | --- | --- | --- | --- |
| J. Xiong,        | C.        | J. Newburn,       |            | D. Vainbrand,  |                  | I.-H. Chung,   | M.      | Gar-     |     |     |     |     |     |     |     |
| land,            | W. Dally, | and               | W.-m. Hwu, | “GPU-Initiated |                  | On-Demand      |         | High-    |     |     |     |     |     |     |     |
| Throughput       |           | Storage Access    | in         | the BaM        | System           | Architecture,” |         | in Pro-  |     |     |     |     |     |     |     |
| ceedings         | of        | the International |            | Conference     | on Architectural |                | Support | for      |     |     |     |     |     |     |     |
ProgrammingLanguagesandOperatingSystems(ASPLOS),2023.
| [51] M. Shen,    | M.         | Umar, K.  | Maeng,      | G. E.         | Suh, and            | U. Gupta, | “Hermes:  |      |     |     |     |     |     |     |     |
| ---------------- | ---------- | --------- | ----------- | ------------- | ------------------- | --------- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- |
| Algorithm-System |            | Co-design |             | for Efficient | Retrieval-Augmented |           |           | Gen- |     |     |     |     |     |     |     |
| eration          | At-Scale,” | in        | Proceedings | of            | the International   |           | Symposium | on   |     |     |     |     |     |     |     |
ComputerArchitecture(ISCA),2025.
| [52] J. Shim, | J. Oh, | H. Roh, | J. Do, | and S.-W.      | Lee, | “Turbocharging |      | Vector |     |     |     |     |     |     |     |
| ------------- | ------ | ------- | ------ | -------------- | ---- | -------------- | ---- | ------ | --- | --- | --- | --- | --- | --- | --- |
| Databases     | Using  | Modern  | SSDs,” | in Proceedings |      | of the         | VLDB | Endow- |     |     |     |     |     |     |     |
ment(PVLDB),2025.
| [53] H. V. | Simhadri, | G. Williams, |     | M. Aumu¨ller, |     | M. Douze, | A. Babenko, |     |     |     |     |     |     |     |     |
| ---------- | --------- | ------------ | --- | ------------- | --- | --------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
D.Baranchuk,Q.Chen,L.Hosseini,R.Krishnaswamny,G.Srinivasa,
S.J.Subramanya,andJ.Wang,“ResultsoftheNeurIPS’21Challenge
onBillion-ScaleApproximateNearestNeighborSearch,”inProceedings
ofMachineLearningResearch(PMLR),2021.
| [54] Solidigm, | “D7-PS1010,” |     | 2024. | [Online]. |     | Available: | https://www. |     |     |     |     |     |     |     |     |
| -------------- | ------------ | --- | ----- | --------- | --- | ---------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
solidigm.com/products/data-center/d7/ps1010.html
[55] I.Song,M.Oh,B.S.J.Kim,S.Yoo,J.Lee,andJ.Choi,“ConfZNS:
| A Novel     | Emulator | for        | Exploring     | Design | Space      | of ZNS | SSDs,”  | in  |     |     |     |     |     |     |     |
| ----------- | -------- | ---------- | ------------- | ------ | ---------- | ------ | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
| Proceedings |          | of the ACM | International |        | Conference | on     | Systems | and |     |     |     |     |     |     |     |
Storage(SYSTOR),2023.
[56] Z.Song,J.Zhang,J.Sun,M.Sun,Z.Yang,Z.Zhang,X.Chen,F.Wu,
| H. Tang, | and | Z. Wang, | “CAM: | Asynchronous |     | GPU-Initiated, |     | CPU- |     |     |     |     |     |     |     |
| -------- | --- | -------- | ----- | ------------ | --- | -------------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
ManagedSSDManagementforBatchingStorageAccess,”inProceed-
ingsoftheInternationalConferenceonDataEngineering(ICDE),2025.