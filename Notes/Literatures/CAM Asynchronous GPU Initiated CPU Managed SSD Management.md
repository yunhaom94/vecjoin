# CAM

**Source**: CAM.pdf
**Format**: .pdf

---

2025 IEEE 41st International Conference on Data Engineering (ICDE)
CAM: Asynchronous GPU-Initiated, CPU-Managed
SSD Management for Batching Storage Access
Ziyu Song1, Jie Zhang1, Jie Sun1, Mo Sun1, Zihan Yang1, Zheng Zhang2, Xuzheng Chen1,
Fei Wu1,3, Huajin Tang1, Zeke Wang1
1CollegeofComputerScienceandTechnology,ZhejiangUniversity
2PurdueUniversity3ShanghaiInstituteforAdvancedStudyofZhejiangUniversity
Abstract—With the wide adoption of GPU and the explosion addresses the data volume limitation but also decreases the
in data volumes, existing accelerator-centric systems require system cost for the same amount of data.
massive storage access. They adopt high-performance storage
However,thebenefitsofoffloadingdatafromGPUtoSSDs
devices like NVMe SSDs to scale up single-node systems cost-
come at the cost of potential performance degradation if the
effectivelyandleveragetheCPUtomanagetheseSSDs.However,
they suffer from performance bottlenecks because of the high corresponding GPU-powered system is not well optimized,
CPU OS kernel overhead and the CPU memory intermediated especially for its I/O side. Essentially, un-optimized GPU-
data transfer. To address this issue, GPU-initiated and GPU- powered systems could serialize SSD accesses and GPU
managed SSD management is proposed to allow the GPU to
computation. Because SSD accesses suffer from long access
fullymanipulateSSDs:1)directdatatransferfromSSDtoGPU
latency and low throughput, these GPU-powered systems that
memory(dataplane)and2)GPU-managedSSDcontrol(control
plane). This can potentially enable these GPU systems to fully need to access data from SSDs could be easily bottlenecked
leveragetheSSDbandwidth.However,westillidentifytwosevere by slow SSD I/O accesses. In order to better analyze their
issues. First, the GPU-management SSD control leads to low properties, we classify these systems into two categories
GPUStreamingMultiprocessorutilization.Second,itleadstothe according to how they manage SSDs.
serial execution of SSD accesses with GPU computation, which
1. Traditional CPU-OS-Managed SSD Management.
slows down the overall computing task. To this end, we propose
CAM, the first asynchronous GPU-initialized, CPU-managed Many GPU computing systems leverage CPUs to manage
SSD management for batching storage access. It 1) offloads the SSDs, such as Ginex [44], MariusGNN [55], and ZeRO-
SSD control plane from GPU to CPU, thus maximizing GPU Infinity [46]. These systems use libaio [46] or POSIX I/O
streamingmultiprocessorutilization,and2)adoptsasynchronous such as pread [44], [55] to manage SSDs. The CPU is
user-friendly APIs that allow programmers to easily overlap
responsible for 1) sending read/write commands to SSDs, 2)
GPU computation and SSD I/O operations while keeping a
synchronous programming experience. As such, CAM enables pollingthecompletioninformation,and3)notifyingtheGPU
us to achieve the best of two worlds: high performance and tocontinuethefollowingcomputation.However,thesesystems
highprogrammability.TheexperimentalresultsshowthatCAM fail to fully utilize the SSD bandwidth, especially in a multi-
canperformGNNmodeltraining,mergesort,andGEMMupto
SSD setting. On the one hand, the overhead of invoking OS
1.84×,1.5×,and1.84×faster,comparedtotheexistingstate-of-
kernel significantly degrades the achievable SSD bandwidth.
the-art GPU systems, while keeping high programmability.
On the other hand, these kernel functions can only move data
I. INTRODUCTION betweenSSDsandCPUmemory.Assuch,thedatamovement
With the advancement of GPUs, many cutting-edge appli- between GPU memory and SSDs must use CPU memory as
cations, such as neural network models [1], [21] and GPU- an intermedium, thus degrading the overall bandwidth and
baseddatabasesystems[6],[50],areturningintoGPU-centric increasing the I/O latency.
systems,whichcanbenefitfromGPU’smassiveparallelcom- 2. GPU-Managed SSD Management. To relieve the severe
puting power. In particular, the NVIDIA A100 GPU delivers CPU-managed overhead, the state-of-the-art GPU-managed
312TeraFLOPS(TFLOPS)ofcomputingcapability,whilethe SSDmanagementapproachBaM[45]enablesGPUtodirectly
AMDThreadripper3995WXCPUhasfewerthan3TFLOPS. access SSDs without the involment of CPU. The state-of-the-
Together with the increasing requirement of computing art approach BaM [45] allows GPU thread blocks to directly
power,theproblemsizeofanapplicationalsoincreasesfaster. submit their read/write commands to Submission Queues
For GNN, the graph can contain billions of vertices and tens (SQs) of SSDs using a synchronous API and then allows
of billions of edges [35], [59], [63], which needs several these GPU threads to poll on the corresponding entries in the
terabytes of storage space. For DLRM, the memory capacity Completion Queues (CQs), while the data is directly trans-
of embedding tables has increased dramatically from tens of ferred between GPU memory and SSDs, without involving
GBstoTBsthroughouttheindustry[33],[61],[62].Therefore, CPUmemoryasanintermedium.WeobservethatlettingGPU
manyresearches[43],[46],[48],[58]leverageSSDstobreak directly manage SSDs greatly improves the achieved GPU-
the GPU memory and server memory boundaries so as to SSD bandwidth and decreases the I/O latency. However, the
enable out-of-core computation on massive data volume for benefits come at the cost of low GPU resource utilization for
a broad range of applications. Storing data in SSDs not only computekernels.BaMneedstolaunchalargenumberofGPU
2375-026X/25/$31.00 ©2025 IEEE 2309
DOI 10.1109/ICDE65448.2025.00175
57100.5202.84456EDCI/9011.01
:IOD
|
EEEI
5202©
00.13$/52/9-3063-5133-8-979
|
)EDCI(
gnireenignE
ataD
no
ecnerefnoC
lanoitanretnI
ts14
EEEI
5202
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore. Restrictions apply.

threadblockstosubmitenoughin-flightI/Orequestsandthen
| poll their | completions. |       | SSDs    | experience | a       | high I/O | latency |     |     |     |     |     |
| ---------- | ------------ | ----- | ------- | ---------- | ------- | -------- | ------- | --- | --- | --- | --- | --- |
| (tens of   | µs), and     | these | threads | are all    | waiting | idly     | most of |     |     |     |     |     |
thetime.Inparticular,anA100GPUneedstouseallitsSMs
(StreamingMultiprocessor)tofullyexploittheSSDbandwidth
| when the          | number | of SSDs        | exceeds | five.   |          |                  |        |     |     |     |     |     |
| ----------------- | ------ | -------------- | ------- | ------- | -------- | ---------------- | ------ | --- | --- | --- | --- | --- |
| To this           | end,   | we propose     | CAM,    | the     | first    | GPU-initialized, |        |     |     |     |     |     |
| CPU-managed       |        | SSD management |         | for     | batching | SSD              | access |     |     |     |     |     |
| GPU applications. |        | We             | offload | the SSD | control  | plane            | from   |     |     |     |     |     |
GPUtoCPU,thusmaximizingGPUstreamingmultiprocessor
| utilization | for   | compute     | kernels | during   | SSD        | I/O processes. |         |             |          |                |     |                   |
| ----------- | ----- | ----------- | ------- | -------- | ---------- | -------------- | ------- | ----------- | -------- | -------------- | --- | ----------------- |
|             |       |             |         |          |            |                |         | Fig. 1: GNN | training | time breakdown | for | the baseline BAM- |
| However,    | it is | non-trivial | to      | achieve. | We propose |                | two key |             |          |                |     |                   |
basedGIDSonthePaper100M[19]graphdatasetanddifferent
designstosolvethecorrespondingchallenges.Assuch,CAM
models(GCN[26],GAT[53],GRAPHSAGE[16]).Thenode
enablesustoachievethebestoftwoworlds:highperformance
|     |     |     |     |     |     |     |     | feature data | is stored | in 12 SSDs, | while | the graph structure |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --------- | ----------- | ----- | ------------------- |
and high programmability.
|            |            |       |         |            |        |            |        | data is stored | in the CPU | memory.            |     |                  |
| ---------- | ---------- | ----- | ------- | ---------- | ------ | ---------- | ------ | -------------- | ---------- | ------------------ | --- | ---------------- |
| First,     | we propose | a     | dynamic | adjustment | method | to         | change |                |            |                    |     |                  |
| the number | of         | cores | for CPU | control    | SSD    | to address | the    |                |            |                    |     |                  |
|            |            |       |         |            |        |            |        | 3) We          | design the | first asynchronous |     | APIs that enable |
challengeofmanagingSSDswithasfewCPUcoresaspossi-
ble without sacrificing performance (Challenge 1). Assigning a synchronous programming experience while keep-
multiple CPU cores for each SSD achieves high bandwidth. ing high performance for asynchronous GPU-Initiated,
However, this consumes a large number of CPU cores, espe- CPU-Managed SSD Management.
ciallyconsideringthelargenumberofSSDsthataservermay
be equipped with. For instance, controlling 12 SSDs would II. MOTIVATION
| require | 13 cores | for reading |     | and an | additional | 13 cores | for |     |     |     |     |     |
| ------- | -------- | ----------- | --- | ------ | ---------- | -------- | --- | --- | --- | --- | --- | --- |
writing, resulting in a total of 26 cores. As the number of Compared with storing data in the server memory, SSDs’
|                 |        |              |                 |              |                |            |     | large volume | comes at       | the cost of | performance | degradation. |
| --------------- | ------ | ------------ | --------------- | ------------ | -------------- | ---------- | --- | ------------ | -------------- | ----------- | ----------- | ------------ |
| SSDs increases, |        | this becomes |                 | increasingly | unsustainable. |            | To  |              |                |             |             |              |
|                 |        |              |                 |              |                |            |     | The main     | reason for the | performance | degradation | is the high  |
| save CPU        | cores, | CAM          | can dynamically |              | adjust         | the number | of  |              |                |             |             |              |
cores for CPU control SSD. In an environment with N SSDs, data transfer overhead between GPUs and SSDs. To illustrate
CAM can use N/4 to N/2 cores dynamically according to the this, we make GNN training, a typical big data application
|          |         |             |              |      |               |      |      | involving | GPU and SSDs, | as an example. |           | We profile a GNN |
| -------- | ------- | ----------- | ------------ | ---- | ------------- | ---- | ---- | --------- | ------------- | -------------- | --------- | ---------------- |
| relative | time of | computation | and          | I/O. |               |      |      |           |               |                |           |                  |
|          |         |             |              |      |               |      |      | training  | system GIDS   | [43] on the    | Paper100M | [19] dataset     |
| Second,  | we      | propose     | asynchronous |      | user-friendly | APIs | that |           |               |                |           |                  |
allow programmers to easily overlap GPU computation and using 12 SSDs. As depicted in Figure 1, GIDS spends 40%-
SSD I/O operations while keeping synchronous program- 65% of the overall training time on extracting node features,
|                 |     |           |     |         |      |                 |     | which mainly | involves | reading data | from | SSDs to GPUs. |
| --------------- | --- | --------- | --- | ------- | ---- | --------------- | --- | ------------ | -------- | ------------ | ---- | ------------- |
| ming experience |     | to tackle | the | problem | that | an asynchronous |     |              |          |              |      |               |
However,thepoorperformancecannotbeblamedonSSD’s
| interface | comes | with | low programmability |     |     | (Challenge | 2). |     |     |     |     |     |
| --------- | ----- | ---- | ------------------- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- |
Asynchronous APIs, though powerful, are often difficult to abilities. Modern SSDs (solid-state drives) offer significantly
workwith.Tosimplifyusage,wewanttodesignasetofuser- higher performance than traditional HDDs (hard disk drives).
AtypicalenterpriseSSDprovidesrandomreadbandwidthup
| friendly | synchronous | APIs | without | sacrificing |     | performance. |     |              |                    |     |            |             |
| -------- | ----------- | ---- | ------- | ----------- | --- | ------------ | --- | ------------ | ------------------ | --- | ---------- | ----------- |
|          |             |      |         |             |     |              |     | to 4.8 GB/s, | and the throughput | of  | NVMe-based | SSDs scales |
WeevaluateCAMonthesortandGEMMworkloads,three
popular GNN models (GCN, GAT, and GRAPHSAGE), and linearly with the number of SSDs used [11], [15]. GIDS [43]
real-world datasets (Paper100M and IGB-Full) on a GPU uses 12 SSDs when training on the IGB [25] dataset. It only
serverwithA10080GGPUand12SSDs.Experimentalresults achieves 15 GB/s SSD bandwidth. However, the examined
CPU-SSDbandwidthofusing12SSDscanbeupto20GB/s.
showthatoursystemcanfullyutilizetheI/Obandwidth.Inthe
GNNapplication,ourapproachhasconsistentlyoutperformed Applications such as storage-offloaded LLM training and
state-of-the-art implementations across various models and DLRM training present similar conclusions. For example,
datasets, achieving up to 1.84× training speed. CAM also the DLRM training system TorchRec [37] spends 75% of
outperforms up to 1.50× and 1.84× compared to baselines each iteration time on the embedding access, which mainly
~
in sort and GEMM workloads. reads the embedding table from SSD with only the 64%
Overall, our contributions are as follows: SSD bandwidth utilization [2]. LLM training system Zero-
infinity[21],[46]spendsmorethan80%oftimeontheupdate
| 1) We | identify | the | concrete | SSD access | issues | of  | existing |     |     |     |     |     |
| ----- | -------- | --- | -------- | ---------- | ------ | --- | -------- | --- | --- | --- | --- | --- |
~
GPU-powered computing systems. phase that mainly consists of SSD accesses with only 70%
2) We propose CAM, the first GPU-initialized, CPU- SSD bandwidth utilization [32].
managed SSD management that enables parallel execu- In the following, we categorize existing GPU-powered sys-
tion of SSD I/O and GPU computation. The compute tems into two types according to the devices for managing
kernelcanuseallGPUstreamingmultiprocessorssoas SSDs and identify the concrete issues that prevent them from
to maximize the GPU utilization for computation; fully exploiting SSD abilities.
2310
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore.  Restrictions apply.

(a)4KBRandomRead (b)4KBRandomWrite (a)4KBRandomReadTimeBreakdown
Fig.2:4KBrandomreadandwriteI/Othroughputofsoftware
I/O stacks
A. GPU-Powered systems with CPU-Managed SSDs.
Many GPU-powered computing systems leverage CPUs to
manage SSDs, such as Ginex [44], MariusGNN [55], and
ZeRO-Infinity[46]:1)Forthecontrolpath,thesesystemsuse
(b)4KBRandomWriteTimeBreakdown
libaio or POSIX I/O primitives pread and pwrite to
Fig.3:Read/writeI/OtimebreakdownofsoftwareI/Ostacks
manage SSDs. In particular, the CPU sends the read/write
commands to SSDs, polls for completion information, and
notifiestheGPUtocontinuethefollowingcomputation.2)For • User: The CPU application issues I/O requests through
the data path, these systems use CPU memory as an inter- pread calls, with the parameter file descriptor, offset, and
mediumbetweenGPUmemoryandSSDs.Inparticular,these the destination buffer. Each pread call reads a sequential
systemsonlysupporttransferringdatabetweenSSDsandCPU chunk in the file.
memoryandthenusecudaMemcpytotransferdatabetween
• File system: The file system retrieves the page’s logical
CPU memory and GPU memory. block address (LBA) mapped to the file request according
Theabovesystemsexperiencetwosevereissuesthatprevent to the file ID and the offset.
the system from fully exploiting SSD performance.
• I/O mapping: The I/O mapping module calls I/O map-
Issue 1: I/O Stack Overhead Due to Heavy OS Kernel.
related functions to pin kernel pages and add them to the
Current CPU-managed systems adopt I/O stacks that require
Block I/O.
OS kernel functions to perform I/O, such as POSIX I/O,
• Block I/O: The block I/O module assigns the requests to
libaio, and io_uring. We found that these I/O stacks
SSD’s request queue and communicates with SSDs for I/O
incur heavy overhead for GPU-SSD transfer. To show this,
transaction notification.
we measure the maximum throughput of various I/O stacks,
includingPOSIXI/O,libaio,io_uringininterruptmode • I/O mapping: Upon the SSD I/O completion, the data has
(io uringint)andio_uringinpollingmode(io uringpoll) beentransferredtotheCPUmemorybySSDs,andtheCPU
whenmanipulatingasingleIntelP5510SSD.Figure2shows unpins the pinned kernel pages. The pread procedure is
the random read and write throughput with the 4KB access completed, and the CPU exits to user mode. After that, the
granularity, where the dashed line indicates the maximum CPU transfers data to the GPU.
I/O throughput the SSD provides. The result shows that all
To illustrate the OS kernel overhead, we break down the
these software I/O stacks’ performance is far below SSD’s
I/O procedure into time spent in the four layers. We evaluate
throughput, indicating the severe overhead.
on both 4KB random read and random write workloads, and
The reason for the overhead is due to heavy OS kernel viadifferentkernelI/OstacksincludingPOSIXI/O,libaio,
processing. In the kernel mode, they all need the logical io_uring in interrupt mode (io uring int) and io_uring
block address retrieval, io map, and Block I/O (the OS I/O in polling mode (io uring poll). Figure 3 shows the I/O time
abstraction) to handle a single request. In the following, we breakdown.Weobservethatsignificantamountoftimeisspent
take the most commonly used pread primitive from POSIX on the io map and logical block address retrieval procedure
I/Oasanexample,whilePOSIXpwriteandotherI/Ostacks
(more than 34%). According to the SSD characteristics, the
are alike to pread. We divide the I/O procedure into four I/O stack should issue many NVMe commands concurrently
layers, namely User, file system, I/O mapping, and Block to maximize the SSD’s throughput. However, too much time
I/O (the OS I/O abstraction), and describe concrete the I/O spent on the file system and I/O mapping layers limits the
procedure and the layer that handles each step: number of concurrent NVMe commands sent to SSDs. In
• User: The GPU calculates the file’s data address and trans- contrast, the smaller fraction of time spent in the two layers
fers it to the CPU. results in more throughput.
Opportunity for Improvement. Since I/O spends a large
2311
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore. Restrictions apply.

TABLE I: Architectural design comparison
Initializedby Controlplane Dataplane
SSD-CPUmemory
POSIXI/O CPU CPUOSkernel
-GPUmemory
GPUUser
BaM GPU SSD-GPUmemory
I/Oqueue
CPUUser
CAM GPU SSD-GPUmemory
I/Oqueue
involvement. However, it still has a severe issue that prevents
Fig. 4: Single A100 SM utilization (%) in BAM system with
it from efficient I/O.
the number of SSDs to saturate SSDs.
Issue 3: Serial Execution of Computation and I/O due
fractionoftimeonend-to-endperformance,reducingtheCPU to Low GPU SM Utilization. BaM [45] offers an array-
OS kernel software overheads is essential. We observe that basedsynchronousAPI(bam::array)toaccessSSD,which
overhead caused by the file system and I/O mapping layers provides fine-grained, on-demand SSD access. However, this
canbeeliminated.TheunderlyingreasonthattheseI/Ostacks user interface design comes at a performance cost in three
need to map and unmap the buffer is that these management aspects: 1) Due to its synchronous interface, threads wait
handlerequestsonebyone.Theydon’tknowthetotalrequest for their competition after submitting I/O requests instead of
sizeaheadoftime,sotheycan’tmaponceinasinglebatching submittingotherrequests.2)TofullyexploitSSDbandwidth,
access. Besides, traditional file systems like EXT4 require BaMneedstolaunchalargenumberofGPUthreadblocksto
logical block address retrieval design because the file is not submit enough in-flight I/O requests and poll the completion.
always mapped to continuous blocks. The file system must 3)SSDI/Oincurshighlatency,e.g.,arandomreadlatencyof
look up the LBA from the file and offset. 15 microseconds and a random write latency of 82 microsec-
In contrast, the SSD data access granularity in the scenario onds [49]. Thus, the thread idle period is long. As a result, a
of GPU-powered systems is often 512 B or 4 KB, and the large number of thread blocks in BaM are waiting idly.
batch size is usually large. The file size is usually fixed or Worse still, many application utilizes multiple SSDs to
varies regularly. As such, the LBA can be mapped using a enlarge the SSD capacity and improve the aggregated I/O
simplermethod,suchasdirectmapping.Meanwhile,thetotal bandwidth, and the problem becomes more severe with the
batch number can be determined before the first request is increase in SSD numbers. To illustrate this, Figure 4 shows
handled. As such, the buffer only needs to be mapped once the A100 SM (Streaming Multiprocessor, computing unit of
beforebatchingaccessismadeandonlyneedstobeunmapped a GPU) utilization to fully exploit the bandwidth of different
after the whole batch accesses. numbersofSSDs.WhenthenumberofSSDsexceedsfive,the
Issue 2: Redundant Memory Copy. Instead of directly BaMsystemengagesnearlyallavailableGPUstreamingmul-
transferring data between SSDs and GPU memory, system tiprocessorstoinitiateNVMecommands.Thishighutilization
calls like pread can only take CPU memory addresses as for the I/O process results in substantial contention between
parameters. As such, these systems use CPU memory as an GPU computation and GPU-managed I/O. Consequently, the
inter-medium between GPU memory and SSDs. When the I/O and computation phases are executed serially, leading to
accessgranularityissmall,thecudaMemcpyAsyncfunction low GPU utilization for the computation process.
needs to be called multiple times. The smaller the access TovalidatethatBaMfailedtooverlapI/Oandcomputation,
granularity, the greater the impact on performance. A 4KB we evaluated the relative execution time of I/O and compu-
granularity can only yield 1.3GB/s SSD bandwidth, which tation in a real-world application. We profile each stage in
is only 6% of PCIe peak bandwidth. When we evaluate the the GNN training execution of GIDS, as shown in Figure 1.
ANNS workload that mainly involves 4 KB SSD accesses, GIDS extracts node features based on the BaM’s high-level
cudaMemcpyAsynccosts78%ofthetotaltime.Suchalarge interfaces.GIDSspends40%-65%oftheoveralltrainingtime
proportion can not be overlapped by computation. on I/O. The training phase accounts for a significant portion
oftheexecutiontime,rangingfrom16%to44%foreachstep.
B. GPU-Powered Systems with GPU-Managed SSDs Inconclusion,BaM’slowGPUSMutilizationfailstooverlap
computation and I/O.
InordertoaddresstheissuesofOSkernel-managedSSDs,
recent works [45] intend to offload control and data planes III. DESIGNOFCAM
ontoGPUs.BaM(BigAcceleratorMemory)[45]isthestate-
To address the above issues, we propose CAM, a GPU-
of-the-art GPU-initiated GPU-managed SSD management.
initialized, CPU-managed system that efficiently offloads the
BaM allows GPU thread blocks to submit their read/write
SSDmanagementtoCPUuserspacewhileprovidingasetof
commands to Submission Queues (SQs) to SSD using a
APIstokeepprogrammability.TableIshowsthearchitectural
synchronous API and allows these GPU threads to poll on
design comparison of CAM, BaM, and POSIX I/O. We have
the corresponding entry in Completion Queues (CQs) to be
three design goals that motivate the design of CAM.
aware of the completion. BaM enables GPUs to achieve high
Goal 1: Minimum GPU SM Overhead for I/O Pro-
throughput and fine-grained SSD-GPU accesses without CPU
cessing. Minimum GPU SM utilization for I/O processing
2312
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore. Restrictions apply.

| indicates | that more | GPU      | SMs can | be       | used by    | computation |       |     |     |     |     |     |     |     |
| --------- | --------- | -------- | ------- | -------- | ---------- | ----------- | ----- | --- | --- | --- | --- | --- | --- | --- |
| tasks and | thus can  | directly | reduce  | the task | completion |             | time. |     |     |     |     |     |     |     |
Goal2:FullyUtilizingSSDs’BandwidthandScalability.
| Our design | must | provide | high | scalability | when | managing |     |     |     |     |     |     |     |     |
| ---------- | ---- | ------- | ---- | ----------- | ---- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
multipleSSDs,soastomeetthefastprocessingrequirements
| of the growing | data                    | volume. |         |             |      |            |     |     |     |     |     |     |     |     |
| -------------- | ----------------------- | ------- | ------- | ----------- | ---- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| Goal           | 3: Programming-Friendly |         |         | Interfaces. |      | Generally, |     |     |     |     |     |     |     |     |
| asynchronous   | APIs                    | are     | thought | to be       | able | to provide | a   |     |     |     |     |     |     |     |
betterperformancethansynchronousAPIs,however,anasyn-
chronousinterfacecomeswithlowprogrammability.Assuch,
| CAM intends        | to             | provide         | APIs as      | easy           | as synchronous |                | APIs    |     |     |     |     |     |     |     |
| ------------------ | -------------- | --------------- | ------------ | -------------- | -------------- | -------------- | ------- | --- | --- | --- | --- | --- | --- | --- |
| to simplify        | programming    |                 | without      | sacrificing    | performance.   |                |         |     |     |     |     |     |     |     |
| To achieve         | the            | above           | goals,       | we propose     | CAM,           | an             | asyn-   |     |     |     |     |     |     |     |
| chronous           | GPU-initiated, |                 | CPU-managed  |                | SSD management |                | for     |     |     |     |     |     |     |     |
| batching           | storage        | access.         | CAM consists | of             | 1) a           | GPU-initiated, |         |     |     |     |     |     |     |     |
| CPU-managed        | SSD            | I/O             | stack and    | 2) a           | set of         | user-friendly  |         |     |     |     |     |     |     |     |
| synchronous        | programming    |                 | APIs.        |                |                |                |         |     |     |     |     |     |     |     |
| A. GPU-Initiated,  |                | CPU-Managed     |              | SSD I/O        | Stack          |                |         |     |     |     |     |     |     |     |
| CAM’s              | I/O stack      | consists        | of           | new designs    | in             | both           | control |     |     |     |     |     |     |     |
| and data           | planes.        | Regarding       | the control  | plane,         | CAM            | proposes       |         |     |     |     |     |     |     |     |
| 1) a GPU-initiated |                | asynchronous    |              | I/O submission |                | technology,    |         |     |     |     |     |     |     |     |
| 2) a CPU           | user-space     | SSD             | control      | offloading     | technology,    |                | and     |     |     |     |     |     |     |     |
| 3) a thread-level  |                | synchronization |              | technology.    |                | Regarding      | the     |     |     |     |     |     |     |     |
| data plane,        | CAM            | presents        | the direct   | data           | path           | between        | GPU     |     |     |     |     |     |     |     |
and SSD.
| Overall | I/O Procedure. |     | Figure | 5 shows | how | GPUs | access |     |     |     |     |     |     |     |
| ------- | -------------- | --- | ------ | ------- | --- | ---- | ------ | --- | --- | --- | --- | --- | --- | --- |
SSDsinCAM.Here,wetakeGPUreadingdatafromanSSD
asanexample,whilethewritingprocedureisthesame,except
|     |     |     |     |     |     |     |     | Fig. 5: CAM’s | GPU-initiated, |     | CPU-managed |     | disk | I/O stack |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | -------------- | --- | ----------- | --- | ---- | --------- |
forthedatatransferdirection.GPUfirstwritestheLBAofthe
(I:GPUprefetchinitialization;C:GPUcomputation;M:CPU
| data to be | prefetched | in  | the next | step into | CPU | memory | (1). |                 |        |         |             |     |     |     |
| ---------- | ---------- | --- | -------- | --------- | --- | ------ | ---- | --------------- | ------ | ------- | ----------- | --- | --- | --- |
|            |            |     |          |           |     |        |      | SSD management; | P: SSD | request | processing) |     |     |     |
Meanwhile,theCPUthreadkeepspollinguntilitreceivesthe
GPUsignalthatinformsthenewI/Orequest(2).Afterissuing
|     |     |     |     |     |     |     |     | completes | the block initially, | the | GPU | synchronizes |     | with the |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | -------------------- | --- | --- | ------------ | --- | -------- |
theLBA,GPUinitializestheasynchronousI/Osubmissionby
CPU(3).Followingthisinitialprocess,theGPUcanperform
sendingthesynchronizationsignal(3).Then,theCPUissues
|         |         |         |           |          |     |          |     | computations | using data | prefetched |     | in the | last step. | This |
| ------- | ------- | ------- | --------- | -------- | --- | -------- | --- | ------------ | ---------- | ---------- | --- | ------ | ---------- | ---- |
| the I/O | request | to SSDs | and waits | for SSDs | to  | complete | the |              |            |            |     |        |            |      |
data transfer (4). Meanwhile, GPU polls for the complete arrangement ensures that the GPU remains productive rather
|           |             |               |        |                |             |        |       | than lying     | idle awaiting | the completion |             | of I/O | tasks. |         |
| --------- | ----------- | ------------- | ------ | -------------- | ----------- | ------ | ----- | -------------- | ------------- | -------------- | ----------- | ------ | ------ | ------- |
| prefetch  | signal when | there         | are no | ongoing        | computation |        | tasks |                |               |                |             |        |        |         |
|           |             |               |        |                |             |        |       | CPU User-Space | SSD           | Control        | Offloading. |        | To     | achieve |
| (5). Upon | the         | CPU receiving |        | the completion |             | signal | from  |                |               |                |             |        |        |         |
SSDs,itinformstheGPUthroughthecompletionsignal(6). Goal 1, we should minimize the GPU SM utilization from
After the data is prefetched completely into GPU memory, I/O processing. So, we offload the SSD management to the
CPU,achievingzeroGPUstreamingmultiprocessorutilization
| the GPU     | starts      | the computation |      | (7). For | the data | path,   | data |            |                 |      |     |         |     |           |
| ----------- | ----------- | --------------- | ---- | -------- | -------- | ------- | ---- | ---------- | --------------- | ---- | --- | ------- | --- | --------- |
|             |             |                 |      |          |          |         |      | during SSD | I/O. To achieve | Goal | 2,  | we have | two | tasks: 1) |
| is directly | transferred | between         | SSDs | and      | GPU      | memory. |      |            |                 |      |     |         |     |           |
GPU-Initiated Asynchronous I/O Submission. to make an SSD achieve maximum throughput, and 2) to
To achieve Goal 1, we aim to reduce GPU SM utilization achievescalabilitywhentheSSD’snumberincreases.Wehave
adoptedthelightweightStoragePerformanceDevelopmentKit
| during SSD  | I/O.     | GPU  | computes        | the LBA | of      | blocks | to be   |           |                |     |            |      |        |       |
| ----------- | -------- | ---- | --------------- | ------- | ------- | ------ | ------- | --------- | -------------- | --- | ---------- | ---- | ------ | ----- |
|             |          |      |                 |         |         |        |         | (SPDK) to | achieve higher | SSD | bandwidth. | SPDK | offers | a set |
| prefetched. | It takes | tens | of microseconds |         | between |        | issuing |           |                |     |            |      |        |       |
NVMe commands and waiting for the request to complete, of tools and libraries for writing high-performance, scalable,
thus such a long time brings a significant challenge to fully user-mode storage applications. Users can simply write a
|     |     |     |     |     |     |     |     | request into | a predefined | ring | buffer | and signal | to  | the SSD |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ------------ | ---- | ------ | ---------- | --- | ------- |
harnessSMutilization.Therefore,wepresentanasynchronous
|                |     |         |      |        |     |         |      | that there | are pending | requests. | SPDK | completely |     | bypasses |
| -------------- | --- | ------- | ---- | ------ | --- | ------- | ---- | ---------- | ----------- | --------- | ---- | ---------- | --- | -------- |
| initial method | to  | let GPU | send | LBA to | CPU | without | con- |            |             |           |      |            |     |          |
cerning the SSD control (e.g., creating SSD commands and the operating system kernel, including the block device layer,
sending commands to SSDs). file systems, and the page cache. With SPDK’s capabilities,
wehavemanagedtoavoidkernelI/Ostacksandachievehigh
| As illustrated |     | in Figure | 5, GPU | threads | compute | LBA | and |     |     |     |     |     |     |     |
| -------------- | --- | --------- | ------ | ------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
bandwidthforSSDdatareading.Toachievescalability,weuse
| write the | LBA to | CPU memory |     | (1). This | is an | asynchronous |     |     |     |     |     |     |     |     |
| --------- | ------ | ---------- | --- | --------- | ----- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
GPUinitialblockrequestwithoutblocking.Aftereachthread thethreadpoolthatallowseachthreadtocontroloneormany
2313
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore.  Restrictions apply.

|     |     | TABLE | II: CAM | software |       | API         |     |     |     |     |     |     |     |     |
| --- | --- | ----- | ------- | -------- | ----- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | API |       | RunOn   |          | Input | Description |     |     |     |     |     |     |     |     |
CAM_init
|     |           |     | Host   |          | —       | InitializeSSD     |     |     |     |     |     |     |     |     |
| --- | --------- | --- | ------ | -------- | ------- | ----------------- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | CAM_alloc |     | Host   |          | size    | AllocateGPUmemory |     |     |     |     |     |     |     |     |
|     | CAM_free  |     | Host   |          | pointer | FreeGPUmemory     |     |     |     |     |     |     |     |     |
|     |           |     |        | LBAarray |         | Prefetchdata      |     |     |     |     |     |     |     |     |
|     | prefetch  |     | Device | req      | num     | fromSSDsto        |     |     |     |     |     |     |     |     |
|     |           |     |        | destaddr |         | pinnedGPUmemory   |     |     |     |     |     |     |     |     |
Synchronizethelast
| prefetch_synchronize |     |     | Device |     | —   |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
prefetchfunction
|     |     |     |     | LBAarray |     | Writebackdata |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | -------- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
write_back Device req num frompinnedGPU Fig. 6: CAM pipeline in GNN application
|     |     |     |     | destaddr |     | memorytoSSDs |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | -------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
Synchronizethelast
write_back_synchronize Device — have an asynchronous interface to overlap computation and
write backfunction
|     |     |     |     |     |     |     |     | communication |     | while keeping | high | GPU utilization |     | for com- |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ------------- | ---- | --------------- | --- | -------- |
putekernels.Therefore,CAMexposessynchronous-likehigh-
| SSDs | and | dedicate | a single | NVMe | queue | pair to | each NVMe |     |     |     |     |     |     |     |
| ---- | --- | -------- | -------- | ---- | ----- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- |
device. The NVMe driver takes no locks in the I/O path. So, level application programming interfaces to guarantee high
it scales linearly in terms of performance per thread, as long programmability.WeaimtopipelinetheI/Oandcomputation
as a queue pair and a CPU core are dedicated to each new phases as shown in Figure 5. Figure 6 shows how the steps
|     |     |     |     |     |     |     |     | are logically | pipelined |     | for the | GNN workload. | The | pipeline |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --------- | --- | ------- | ------------- | --- | -------- |
thread.TooptimizeCPUusage,CAMcandynamicallyadjust
thenumberofCPUcoresforcontrollingSSD.Ifcomputation programming procedure consists of a series of coordinated
takes a longer time, the total execution time is bounded by steps to manage data flow with SSDs and processing tasks.
computation because I/O time completely overlaps with com- Firstly, node sampling enables us to identify which nodes
|     |     |     |     |     |     |     |     | should be | prefetched. |     | Secondly, | the data | is retrieved | from |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----------- | --- | --------- | -------- | ------------ | ---- |
putationtime.LessI/Othroughputmayalsobenolongerthan
the computation time, allowing CAM to dynamically reduce SSDs and stored in a read buffer. Thirdly, users utilize this
the CPU cores without affecting performance. CAM records data to perform computations for model training purposes.
computationandI/Otime.CAMrecordsbothcomputationand Thesethreestagesoverlapwitheachother,ensuringaseamless
|     |        |             |     |        |          |     |           | and efficient | process. |     | If the read | is dependent | on  | the prior |
| --- | ------ | ----------- | --- | ------ | -------- | --- | --------- | ------------- | -------- | --- | ----------- | ------------ | --- | --------- |
| I/O | times. | CAM adjusts | the | number | of cores | for | CPU-based |               |          |     |             |              |     |           |
SSDcontrolaccordingtotherelativetimeofcomputationand compute, pipeline bubbles will appear. This is a limitation of
I/O in the last batch. thealgorithm.Oursystemcan’teliminatethepipelinebubbles
DirectDataPathbetweenGPUandSSD.ToachieveGoal2, causedbydatadependencies.Inthissituationwheredatahave
|     |     |     |     |     |     |     |     | dependencies, | the | compute | and | I/O are serial. | Our | system |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ------- | --- | --------------- | --- | ------ |
weneedtooptimizethedatapathfromstoragetoGPU,which
is essential for performance efficiency in massive storage achieveshighI/OthroughputandthusachievesshortI/Otime.
access.Oursystemtacklesmemorycopyissuesbyestablishing Table II shows our APIs. This section will describe the
a direct data path from the SSD to GPU, bypassing the design for CAM API in the order of initialization, GPU
memorymanagement,andread-write-relatedfunctions,which
| CPU | and | thus avoiding | unnecessary |     | memory | staging | at CPU |     |     |     |     |     |     |     |
| --- | --- | ------------- | ----------- | --- | ------ | ------- | ------ | --- | --- | --- | --- | --- | --- | --- |
memory. To implement this, we need to get the physical are similar to the order of use. Finally, we will show a
address of pinned GPU memory and then use the physical simplified example using CAM.
address to make SSD commands. Initialization. CAM utilizes an CAM_init function to set
|     |            |              |     |             |     |            |        | up the data | structure | and | manage | threads for | CPU-GPU | syn- |
| --- | ---------- | ------------ | --- | ----------- | --- | ---------- | ------ | ----------- | --------- | --- | ------ | ----------- | ------- | ---- |
|     | Our system | incorporates |     | the GDRCopy |     | technology | to pin |             |           |     |        |             |         |      |
GPU memory and get the physical address of the pinned chronization and SSD management. CPU-GPU synchroniza-
GPU memory. Specifically, these pinned memory buffers tion involves four main memory regions and a polling CPU
can be mapped to the GPU memory through the function thread.RegardingSSDmanagement,theinitializationfunction
|                       |     |     |     |       |      |            |        | focuses on | setting | up the | SSD | controllers and | mapping | GPU |
| --------------------- | --- | --- | --- | ----- | ---- | ---------- | ------ | ---------- | ------- | ------ | --- | --------------- | ------- | --- |
| nvidia_p2p_get_pages. |     |     |     | After | this | procedure, | we can |            |         |        |     |                 |         |     |
memoryregions,whichweusedfortheCAM_allocfunction.
| know | the | start physical | address | of  | this big | chunk | of memory, |     |     |     |     |     |     |     |
| ---- | --- | -------------- | ------- | --- | -------- | ----- | ---------- | --- | --- | --- | --- | --- | --- | --- |
and the address is continuous. So, we can calculate the GPU Memory Management. The CAM_alloc and
physical address from any virtual address in this chunk. CAM_free functions are used to manage the GPU mem-
|     |        |          |           |     |        |        |           | ory. Users | should | use | our alloc | interface | instead | of the |
| --- | ------ | -------- | --------- | --- | ------ | ------ | --------- | ---------- | ------ | --- | --------- | --------- | ------- | ------ |
|     | During | the data | transfer, | our | system | issues | NVMe Sub- |            |        |     |           |           |         |        |
cudaMalloc
mission Queue Entries (SQEs) with the target addresses set function to allocate the GPU memory. The
to specific physical locations within pinned GPU memory. allocfunctionreturnsanaddressregisteredbyGDRCopy.The
By directly targeting these pinned GPU memory’s physical allocated buffer would be pinned and the SSDs can directly
|     |     |     |     |     |     |     |     | access these | buffers. |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | -------- | --- | --- | --- | --- | --- |
addresseswhensendingNVMeSQEs,thedatapathisdirectly
between GPU and SSDs. Read and Write related Functions. CAM does not require
persistentthreadsontheGPU.Instead,itrequiresapersistent
B. Asyn. API with Synchronous Programming Experience thread on the CPU. We realize the synchronization between
|     |          |            |      |        |       |          |          | GPU and | CPU | by four | pre-allocated | memory | regions. | These |
| --- | -------- | ---------- | ---- | ------ | ----- | -------- | -------- | ------- | --- | ------- | ------------- | ------ | -------- | ----- |
|     | In order | to achieve | Goal | 3, CAM | needs | to offer | a series |         |     |         |               |        |          |       |
of programming-friendly interfaces, while an asynchronous regionsaredesignatedforprefetchingandareallocatedinthe
initializationfunction.(1)Thefirstregioncontainsanarrayof
| interface |     | can lack | programmability. |     | However, |     | CAM must |     |     |     |     |     |     |     |
| --------- | --- | -------- | ---------------- | --- | -------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
2314
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore.  Restrictions apply.

|     |     |     |     |     |     |     | Figure | 7 demonstrates |     | a simplified |     | example | using | CAM to |
| --- | --- | --- | --- | --- | --- | --- | ------ | -------------- | --- | ------------ | --- | ------- | ----- | ------ |
writeanapplicationthatoverlapsprefetchingandcomputation
throughastructured,three-stepprocess.Thefirststepinvokes
theprefetch_synchronizefunctiontoensurecomplete
|     |     |     |     |     |     |     | data fetching | (Line        | 3). | The second |        | step entails |        | preloading |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ------------ | --- | ---------- | ------ | ------------ | ------ | ---------- |
|     |     |     |     |     |     |     | logical block | addresses    |     | of SSDs’   | blocks |              | to be  | prefetched |
|     |     |     |     |     |     |     | and calling   | the prefetch |     | function   |        | (Lines       | 7-10). | The core   |
computationalworkiscarriedoutduringthethirdstep.Inthe
|     |     |     |     |     |     |     | host function, | users  | only   | need     | to initialize | the | initialize |           |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ------ | ------ | -------- | ------------- | --- | ---------- | --------- |
|     |     |     |     |     |     |     | function once  | (Line  | 2 in   | the host | function).    |     | Users      | alloc and |
|     |     |     |     |     |     |     | free buffers   | in GPU | memory | using    | alloc         | and | free.      |           |
Weobservethattheuserexperienceofsequentiallyreading
andcomputingmirrorsthefamiliarsynchronousprogramming
(a)KernelFuntion
|     |     |     |     |     |     |     | model. Essentially, |     | CAM | offers | the | programmer |     | a natural |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | ------ | --- | ---------- | --- | --------- |
workflowwherereadingissynchronizedbeforedataretrieval.
|     |     |     |     |     |     |     | This implicitly | aligns | with   | conventional |         | programming |       | prac- |
| --- | --- | --- | --- | --- | --- | --- | --------------- | ------ | ------ | ------------ | ------- | ----------- | ----- | ----- |
|     |     |     |     |     |     |     | tices, offering | ease   | of use | and          | reduced | cognitive   | load. |       |
C. Discussion
|     |     |     |     |     |     |     | CAM        | has three | limitations.   |     | Firstly,    | CAM | requires | SSDs       |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --------- | -------------- | --- | ----------- | --- | -------- | ---------- |
|     |     |     |     |     |     |     | to operate | without   | a pre-existing |     | filesystem. |     | Any      | filesystem |
|     |     |     |     |     |     |     | must be    | removed   | before         | CAM | deployment, |     | and      | concurrent |
accesstothesamedatablocksbymultipleprocessesrisksdata
|     |     |     |     |     |     |     | consistency | issues. | Secondly, |     | the current | prototype |     | restricts |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ------- | --------- | --- | ----------- | --------- | --- | --------- |
(b)HostFuntion data consumption capabilities to a single GPU configuration.
|      |                |     |         |         |     |     | Thirdly, CAM’s  | architecture |     | requires |        | a linear | scaling | of CPU     |
| ---- | -------------- | --- | ------- | ------- | --- | --- | --------------- | ------------ | --- | -------- | ------ | -------- | ------- | ---------- |
| Fig. | 7: Programming |     | example | powered | by  | CAM |                 |              |     |          |        |          |         |            |
|      |                |     |         |         |     |     | core allocation | relative     |     | to the   | number | of SSDs  | to      | fully uti- |
logicalblocksthatneedtobeprocessed.(2)Thesecondregion lize their aggregate bandwidth. This scalability model risks
stores arguments for the CPU to process a batch of requests. resourcecontentionwhenCAMoperatesalongsideconcurrent
|     |     |     |     |     |     |     | applications | that | require | almost | all CPU | cores. |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ---- | ------- | ------ | ------- | ------ | --- | --- |
(3)ThethirdregionisusedbytheCPUtobeinformedwhen
| the GPU             | has finished | writing | all the | block | IDs; | this region is |     |     |     |            |     |     |     |     |
| ------------------- | ------------ | ------- | ------- | ----- | ---- | -------------- | --- | --- | --- | ---------- | --- | --- | --- | --- |
|                     |              |         |         |       |      |                |     |     | IV. | EVALUATION |     |     |     |     |
| written exclusively |              | by the  | GPU and | read  | only | by the CPU.    |     |     |     |            |     |     |     |     |
(4) The fourth region notifies the GPU when the CPU has Our evaluations aim to answer the following questions:
|                                                       |     |     |     |     |     |     | What | are the | performance |     | characteristics |     | of CAM | com- |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---- | ------- | ----------- | --- | --------------- | --- | ------ | ---- |
| processedallrequests;theCPUwritestothisregionbutreads |     |     |     |     |     |     | •    |         |             |     |                 |     |        |      |
from it only when requested by the GPU. The first three paredwithexistingCPU-andGPU-managedapproaches
| regionsareimplementedusingunifiedmemory,whilethelast |     |     |     |     |     |     | (§IV-B)? |     |     |     |     |     |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
region is located in GPU memory but has its copy stored in What is the end-to-end performance in real world appli-
•
|             |     |             |         |     |              |        | cations | of CAM | compared |     | to baseline |     | solutions | (§IV-C, |
| ----------- | --- | ----------- | ------- | --- | ------------ | ------ | ------- | ------ | -------- | --- | ----------- | --- | --------- | ------- |
| CPU memory. | The | first three | regions | are | only written | by the |         |        |          |     |             |     |           |         |
GPU and read by the CPU, whereas the last region is only §IV-D, and §IV-E)?
written by the CPU and read by the GPU. • How user-friendly is the CAM API for programming
|                |              |      |               |            |        |             | purposes | (§IV-F)?          |     |     |      |           |              |     |
| -------------- | ------------ | ---- | ------------- | ---------- | ------ | ----------- | -------- | ----------------- | --- | --- | ---- | --------- | ------------ | --- |
| Before         | the prefetch |      | function      | is called, | the    | GPU threads |          |                   |     |     |      |           |              |     |
|                |              |      |               |            |        |             | Does     | the user-friendly |     |     | APIs | sacrifice | performance? |     |
| fill the first | region       | with | logical block | addresses. |        | Within the  | •        |                   |     |     |      |           |              |     |
| prefetch       | function,    | only | the leading   | thread     | writes | the nec-    | (§IV-G)? |                   |     |     |      |           |              |     |
essaryargumentsfortheCPUtoprocessthisbatchofrequests • What is the performance penalty of handling multiple
|     |     |     |     |     |     |     | NVMes | with | a single | CPU | thread | (§IV-H)? |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | ---- | -------- | --- | ------ | -------- | --- | --- |
intothesecondregion.Theleadingthreadalsowritesasignal
|              |         |           |         |         |        |          | How | much is | the CPU | overhead |     | for CAM? | (§IV-I)? |     |
| ------------ | ------- | --------- | ------- | ------- | ------ | -------- | --- | ------- | ------- | -------- | --- | -------- | -------- | --- |
| to the third | region, | informing | the CPU | polling | thread | that the | •   |         |         |          |     |          |          |     |
GPUhascompletedwritingandisreadyfortheCPUtobegin • How does CAM compare with optimized SPDK (with
processing I/O requests. The prefetch function only needs overlapping) (§IV-J)?
theleadingthreadtoperformtheseactions,whileotherthreads
|          |              |     |                          |     |     |     | A. Experimental |     | Setting |     |     |     |     |     |
| -------- | ------------ | --- | ------------------------ | --- | --- | --- | --------------- | --- | ------- | --- | --- | --- | --- | --- |
| need not | do anything. | In  | the prefetch_synchronize |     |     |     |                 |     |         |     |     |     |     |     |
function,allthreadsareblockedandwaitfortheleadingthread Hardware Testbed. Table III summarizes the hardware and
to check if the fourth region has been written. This region software configurations of our evaluation platform.
|                 |     |        |             |        |      |              | Workloads. | In  | this | section, | we  | first | conduct | micro- |
| --------------- | --- | ------ | ----------- | ------ | ---- | ------------ | ---------- | --- | ---- | -------- | --- | ----- | ------- | ------ |
| will be written | to  | by the | CPU polling | thread | once | it has fully |            |     |      |          |     |       |         |        |
processed all requests. Regarding the write-related functions, benchmarkstoevaluatetheperformanceofCAManddifferent
write_back and write_back_synchronize operate I/O stacks, then benchmark the end-to-end performance of
similarly to the read functions. CAM on three real-world workloads, namely GNN training,
2315
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore.  Restrictions apply.

(a) Read I/O throughput w.r.t SSD (b) Read I/O throughput w.r.t access(c) Write I/O throughput w.r.t SSD (d) Write I/O throughput w.r.t access
number ganularity number ganularity
Fig. 8: I/O throughput of CAM compared to BaM, SPDK, and POSIX I/O
TABLE III: Experimental platform Parameter Setting
GNNTask Nodeclassification
Configuration Specification SamplingMethod 2-hoprandomneighborsampling
Intel(R)Xeon(R)Gold5320CPU SamplingFan-outs 25,10
CPU
(2×52threads)@2.20GHz HiddenLayerDimension 128
CPU Memory 768GB BatchSize 8000
GPU 80GB-PCIe-A100
TABLE V: Configuration Details in the GNN Experiment
SSD 12×3.84TBIntelP5510
PCIe Gen4x16
Ubuntu22.04LTS,
NVIDIADriver550.54 GB/s) is lower than the theoretical value (32 GB/s) due to 1)
S/W
CUDA11.4DGL0.10 PCIe header and control signal overhead and 2) PCIe traffic
Pytorch1.13.0 contention between multiple SSDs.
Secondly, the write I/O throughput is slower than the read
TABLE IV: Real-world dataset used for evaluating CAM
throughput for all the measured SSD managements. This is
Dataset Paper100M IGB-full because SSD itself has higher read throughput than write.
Nodes Num 111,059,956 269,364,174
Thirdly, our findings also show that the I/O throughput
Edges Num 1,615,685,872 3,995,777,033
increases with increases in access size in all workloads using
Feature Dimension 128 1024
12 SSDs, as shown in Figures 8b and 8d. The throughput
Feature Size 56GB 1.1TB
increase is facilitated by the NVMe protocol’s efficiency,
where more data are retrieved from the SSDs using a single
merge sort, and general matrix multiplication (GEMM). We SubmissionQueueEntry(SQE).Thishasaloweroverheadin
will describe the concrete workload and baseline settings in the flash translation layer [15].
their individual subsections. Inconclusion,CAMperformshigherI/OthroughputPOSIX
I/O and has similar performance to SPDK and BaM. When
B. I/O Stack Microbenmarks
configured with 12 SSDs and an access granularity of 4096,
We first present the performance of CAM in comparison
CAM is capable of achieving 20GB/s throughput. Addition-
with(1)BaM,(2)POSIXI/O,and(3)SPDK.CAMmanages
ally, as CAM employs CPU resources exclusively to orches-
eachSSDusingoneCPUthread.Weevaluatetheperformance
trate the SSDs, it does not engage any GPU SMs. Con-
of BaM using 262144 CUDA threads, a CUDA block size of
sequently, during the computation phase, all available GPU
64, a queue depth of 1024, and the number of queues per
SMs can be dedicated to computational tasks without any
controller of 128. We evaluate the performance of POSIX
reservation or hindrance.
I/O with O DIRECT. To measure the scalability of this SSD
management, we create a widely adopted method of RAID 0
C. Comparison of GNN Training Epoch Time
array to support multiple SSDs because POSIX I/O doesn’t
support varying SSD numbers. The goal is to examine the We compare CAM with the state-of-the-art out-of-core
achieved disk I/O throughput. We examine the achieved I/O GNNtrainingsystems,GIDS[43],regardingtheGNNtraining
throughput on our platform with Intel P5510 SSDs [49] in epochtime.WerunthreeGNNmodels(GCN[26],GAT[53],
differentSSDnumbersandaccessgranularity.FromFigure8, andGRAPHSAGE[16]).Eachmodelistestedintwodatasets
we make 3 major observations. (Paper100M and IGB-Full). The node number, edge number,
Firstly, Figure 8a shows CAM achieves similar read andfeaturedimensionofPaper100MandIGB-Fullareshown
throughput to that of SPDK and BaM. All three systems in Table IV. We use 12 SSDs to store the datasets. Neither
outperform POSIX I/O because they can bypass the overhead GIDSnorourcodeusestheCPUmemorycache.Theconfig-
of the OS kernel. The measured peak PCIe bandwidth (21 uration details in the GNN experiment are shown in Table V.
2316
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore. Restrictions apply.

(a)GCN (b)GAT (c)GRAPHSAGE
Fig. 9: End-to-end performance comparison between CAM and GIDS in GNN training
(a)SortTime (b)GEMMTime (c)GEMMFlops
Fig. 10: End-to-end performance comparison in Sort and GEMM workloads
Figure 9 shows the results. We make 3 observations. operation that is suitable to be executed in GPUs [7], [24].
Firstly, our approach has consistently outperformed state-of- We implement a sort algorithm based on the NVIDIA
the-art implementations across various models and datasets. ModernGPU library [4]. The modern GPU library is a high-
The reason is that the I/O overlaps with computation, and performance library. We compare CAM against SPDK and
thus shortens I/O time, because CAM can achieve higher POSIXI/O.Oursolutionisstructuredintotwodistinctphases
throughput than BaM. Secondly, with the Paper100M dataset, to optimize efficiency. In the initial phase, we leverage the
oursolutioncanachievegreaterspeedintheGATmodelthan advancedsortingcapabilitiesoftheModernGPUlibrarytome-
GCN and GRAPHSAGE. This is because I/O time is slightly thodically combine data blocks, each containing a substantial
longer than the computation time. We find that the GAT volume of 1 billion int32 entries. Following this preliminary
involves the most intensive computations when evaluating step, we embark on the second phase, which involves the
differentmodels.Duetothischaracteristic,CAMcanoverlap pairwise merging of these pre-sorted blocks in a systematic
more time with the GAT model over others, such as GCN fashionuntilalldataentriesarefullyorganizedinasequential
and GraphSAGE, which have lower computational demands. manner.
Thirdly, we have observed that the CAM achieves a greater Figure 10a shows the mergesort time comparison of CAM
speed-upontheIGBdatasetthanthePaper100Mdataset.This and baselines on the mergesort workload. CAM outperforms
is primarily because the I/O operations consume more time POSIX I/O and achieves a similar execution time to SPDK.
on the IGB dataset than the Paper100M dataset. For the IGB CAM performs better than POSIX I/O because CAM can
dataset, the I/O time is slightly longer than the computation achieve higher I/O throughput. CAM and SPDK achieve
time. In the ideal situation, if the I/O and computation parts similarexecutiontimesbecause1)theycanachievesimilarI/O
fully overlap, the total time is I/O bound. CAM can take throughputinthisapplication,and2)theyoverlapcomputation
advantage of the available SSD throughput better than BaM. and I/O.
In summary, CAM enables the overlap of SSD I/O and
computation to achieve better performance in out-of-core E. Comparison of GEMM Performance
GNN training applications compared to state-of-the-art BaM- We examine the General Matrix-matrix Multiplication
powered out-of-core GNN training system GIDS. (GEMM) performance of systems based on CAM, BaM,
NVIDIAGPUDirectStorage(GDS)[40],andSPDK.GEMM
D. Comparison of Sort Performance
is the core computational task of most deep learning models
We examine the sort time of the system based on CAM in training and inference. Accelerating GEMM has become a
comparedwiththesortbaseline,whichisanessentialdatabase major goal of hardware accelerator design. Since three huge
2317
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore. Restrictions apply.

TABLE VI: Lines of code in real-world applications
LinesofCode Workloads
GNNTraining Sort GEMM
SSDManagement
POSIXI/O / 644 /
GDS / / 158
BaM 65 / 165
CAM 66 510 130
Fig. 12: I/O throughput using one thread to control multiple
SSDs
code.CAMempowersdeveloperstoremaindata-centric,min-
imizingtheneedtomanageintricateasynchronousoperations.
CAM effectively meets Goal 3 of enhancing programmability
without sacrificing efficiency, offering a more accessible and
less labor-intensive coding experience.
(a)RandomRead (b)SortApplication
Fig. 11: Throughput and execution time comparison of CAM G. Comparison with Asynchronous APIs
and other asynchronous APIs The main goal of the synchronous APIs is to allow users
(regardlessoftheirskilllevel)towriteapplicationcodeeasily
matrices cannot fit into GPU memory entirely, we need to without sacrificing performance.
divide these matrices into smaller blocks. We run a sort application that sorts billions of integer
Figures 10b and 10c show that our system can be used elementsinSSDs.WeimplementaversionthatadoptsSPDK
to accelerate GEMM compared to BAM and GDS solutions. asynchronous APIs, a version with raw asynchronous CAM
GDS demonstrates slower throughput than BaM and CAM APIs(CAM-Async),andaversionwithourcarefullydesigned
becauseGDSreliesonacomplexfilesystemtodealwiththe synchronous APIs (CAM-Sync). For all three implementa-
EXT4 File System, NVFS Management, and CUDA library- tions, we use the same configurations. We let them use
relatedtasks.TheseI/Ounrelatedoperationsaccountfor70% the same number of CPU threads. Figure 11a shows the
of the total processing time. The substantial time spent on achieved read throughput with different numbers of SSDs,
the file system and I/O mapping layers limits the number and Figure 11b shows the execution time on datasets with
of concurrent NVMe commands that can be sent to SSDs, differentsizes.WeobservethatCAM-Synccanachievenearly
resulting in lower performance. For example, GDS achieves the same performance as CAM-Async/SPDK, indicating that
a throughput of only 0.8 GB/s with 12 SSDs, whereas CAM our synchronous APIs would not harm performance while
can attain nearly 20 GB/s. CAM outperforms BaM because preserving programmability.
CAM can overlap I/O with computation.
H. Effect of Handling Multiple NVMes with one CPU thread
From the above three applications, we conclude that CAM
has wide applicability and good performance. To show the performance penalty of handling multiple
NVMes with one CPU thread, we test the achieved random
F. Programming-Friendly APIs readand randomwrite I/Othroughputwith differentnumbers
of CPU threads using 12 SSDs.
WevalidatetheprogrammabilityofourAPIsbycomparing
A polling thread is used in each implementation and is not
the lines of the code we use with their baselines, as shown
counted. We change the number of managed SSDs for each
in Table VI. In the GNN training workload, we compare the
threadandmeasuretheachievedthroughputwiththedifferent
code lines of the SSD-related I/O stack and the training one-
number of threads. Figure 12 shows the result of CAM’s I/O
step function, which are related to SSD management. CAM
throughput when using different numbers of cores to control
needs slightly longer lines of code than that of BaM, which
12 SSDs at random read and random write workloads. We
relies on a synchronous API. In the context of the mergesort
observe that when using a thread to control 2 SSDs, the
workload,thecentralprocessingloopoftheCAMimplemen-
I/O throughput is similar to that of one thread managing 1
tation comprises just 510 lines of code, compared to the 644
SSD. When a single thread controls more than two SSDs, the
lines of the traditional version. Within the GEMM workload,
performance begins to decline. The I/O throughput using one
the core loop of the CAM implementation is executed in 130
thread to control 4 SSDs is 75% of the throughput using one
lines of code, showing a reduction of around 30 lines of code
thread to control one SSD.
compared to the BaM and GDS solutions.
In conclusion, CAM allows a single thread to control two
Irrespective of the algorithmic complexity, each implemen-
SSDswithoutperformancedegradation.However,4SSDsper
tation is streamlined, requiring fewer lines of code than tradi-
thread could incur a 25% throughput degradation. In a cloud
tional approaches or similar code lines than the synchronous
2318
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore. Restrictions apply.

(a)InstructionsperI/O (b)CyclesperI/O
Fig. 13: The process SSD cost of CAM, SPDK, and libaio (a)RandomRead (b)RandomWrite
Fig. 14: CPU memory bandwidth usage and SSD bandwidth
usage comparison of CAM and SPDK
environment with N SSDs, users should guarantee that at
least N/2 threads could be used to manage SSDs to avoid
performance degradation.
I. Cost of CPU Processing
WetestthecostofCPUprocessingSSD,intermsofcycles
and instructions of the CPU to process each request. We
comparetheperformanceofCAMwithSPDKandlibaio.It’s
important to note that our experiment does not include BaM, (a)RandomRead (b)RandomWrite
as it utilizes GPU processing for SSDs, making comparisons
Fig. 15: I/O throughput of CAM and SPDK at different CPU
with CPU instructions and cycles irrelevant. The results are memory bandwidth. nc indicates running with n memory
shown in Figure 13.
channels.
We have four key observations. Firstly, CAM and SPDK
usefewerinstructionsthanlibaiobecauseCAMandSPDK then copied from CPU memory to GPU memory. Similarly,
bypass the OS kernel and avoid complex OS-related tasks, when a GPU writes to an SSD, the process is analogous.
whichresultsinareductioninthenumberofexecutedinstruc- Reading from SSDs consumes two times the CPU memory
tions. Secondly, CAM and SPDK consume fewer CPU cycles bandwidth, while writing to SSDs also consumes two times
comparedtolibaio.CAM’sefficiencystemsfromhavingfewer theCPUmemorybandwidth.SaturatingasinglePCIe4.0x16
processing instructions and achieving higher I/O throughput. GPU’s read/write SSD throughput (21 GB/s) would consume
Thirdly,CAMandSPDKrequirefewerinstructionsandcycles nearly 42 GB/s CPU memory bandwidth. As such, the CPU
for random read workloads than for random write workloads memory bandwidth would easily become a system bottleneck
because random read operations can utilize more bandwidth if other co-located applications also heavily consume CPU
than random write operations. Fourthly, when comparing ran- memory bandwidth or multiple GPUs are reading/writing
dom write workloads, CAM and SPDK incur slightly fewer SSDsconcurrently.Todemonstratethis,wecalculatetheCPU
instructions but significantly fewer cycles than libaio. The memorybandwidthduringdatatransferandtestthethroughput
substantial reduction in cycles arises from the much higher change when the memory bandwidth is insufficient.
SSD throughput achieved by CAM and SPDK. The reason
We first measure the real-time CPU memory bandwidth
theyonlysaveafewinstructionsisthattheyarepolling-based;
consumptionwhentheGPUisreading/writing(Randomread-
they continuously check for SSD completion information.
/Randomwrite)SSDsusingCAMandSPDK.Figure14shows
This polling method has a high instructions per cycle (IPC)
that the CPU memory bandwidth of SPDK is nearly twice
ratio, resulting in significantly reduced cycles. In contrast,
thebandwidthofSSDs.TheCAM’sCPUmemorybandwidth
libaio is interrupt-based and does not require polling for SSD
increases at a much slower pace. CAM requires much less
completion information. In conclusion, CAM costs less CPU
CPU memory bandwidth than SPDK to fill the bandwidth.
resources than libaio and achieves a similar cost to SPDK.
To further demonstrate the potential effect of the insufficient
CPUmemorybandwidth,wemeasuretheachievedGPU-SSD
J. Discussion on SPDK
throughputwith2and16CPUmemorychannels(labeled“2c”
Relying on SPDK to overlap kernel invocations is effective and “16c”, respectively). We use random read and random
onlywhen1)CPUmemorybandwidthissufficientand2)the write workloads. Figure 15 shows that SPDK’s throughput
access granularity is large enough. If any of these conditions decreaseswhentheCPUmemorybandwidthislimitedatboth
are not fulfilled, Performance degradation will occur. In the workloads, while CAM is not affected by the limited CPU
following, we show the memory bandwidth limitation and memory bandwidth.
access granularity limitation when using SPDK. AccessGranularityLimitation. SPDK’sadditionalmemory
MemoryBandwidthLimitation. WhentheGPUreadsfrom copy would call a cudaMemcpyAsync function and thus
an SSD, the SSD data is first written to CPU memory and increase the I/O latency. When the destination buffer is not
continuous, the cudaMemcpyAsync function needs to be
2319
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore. Restrictions apply.

contrast,ourAsynchronousAPI,CAM,canhelpthesesystems
tackleSSDI/OproblemsbyoverlappingtheI/Oprocesswith
|     |     |     |     |     |     |     | computation    | while          | providing  | easy          | programming. |                |          |            |
| --- | --- | --- | --- | --- | --- | --- | -------------- | -------------- | ---------- | ------------- | ------------ | -------------- | -------- | ---------- |
|     |     |     |     |     |     |     | Massive        | Storage        | Access     | Applications. |              | For            | DLRM     | train-     |
|     |     |     |     |     |     |     | ing, RecTS     | [9] implements |            | vector-based  |              | log-structured |          | man-       |
|     |     |     |     |     |     |     | agement        | to increase    | the        | cache         | hit          | ratio. RecSSD  |          | [58] is    |
|     |     |     |     |     |     |     | the first      | NDP-based      | SSD        | system        | specifically |                | designed | for        |
|     |     |     |     |     |     |     | recommendation |                | inference. | It            | assigns      | embedding      |          | vectors to |
Fig.16:I/OthroughputofCAMandSPDKatdifferentaccess
|     |     |     |     |     |     |     | specific | SSD pages. | This | can increase |     | SSD throughput |     | due to |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ---- | ------------ | --- | -------------- | --- | ------ |
granularity
|                 |            |       |          |     |           |     | SSD’s character. |          | Muhammad | et          | al. [1] | optimize | the       | caching  |
| --------------- | ---------- | ----- | -------- | --- | --------- | --- | ---------------- | -------- | -------- | ----------- | ------- | -------- | --------- | -------- |
|                 |            |       |          |     |           |     | of frequently    | accessed |          | embeddings. |         | Existing | practices | have     |
| called multiple | times. The | extra | overhead | and | increased | I/O |                  |          |          |             |         |          |           |          |
|                 |            |       |          |     |           |     | optimized        | several  | data     | management  | tasks,  | such     | as        | database |
latencywouldrequirealargeraccessgranularitytohidethem buffer management [5], [8], [10], [12]–[14], [17], [18], [20],
by overlapping.
|     |     |     |     |     |     |     | [28], [29], | [31], | [34], [41], | [42], | [47], | [64] | and information |     |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ----- | ----------- | ----- | ----- | ---- | --------------- | --- |
Todemonstratethis,wemeasuretheI/Othroughputwiththe
|     |     |     |     |     |     |     | retrieval | [56]. Marius | Graph | Embeddings |     | [38] | offloads | node |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------------ | ----- | ---------- | --- | ---- | -------- | ---- |
differentaccessgranularitieswhenthedestinationbufferisnot
|     |     |     |     |     |     |     | embedding | parameters | into | SSDs | and | uses | traditional | CPU |
| --- | --- | --- | --- | --- | --- | --- | --------- | ---------- | ---- | ---- | --- | ---- | ----------- | --- |
continuous. Figure 16 shows that when the destination buffer management. LuWu [51] optimizes parameter reading by
| is not continuous, | the application |     | with | an access | granularity |     |     |     |     |     |     |     |     |     |
| ------------------ | --------------- | --- | ---- | --------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
assigningeachlayeritsdatabuffersandretrievingparameters
| of less than   | 128MB will | decrease     | performance |        | significantly. |         |          |          |         |               |     |         |       |          |
| -------------- | ---------- | ------------ | ----------- | ------ | -------------- | ------- | -------- | -------- | ------- | ------------- | --- | ------- | ----- | -------- |
|                |            |              |             |        |                |         | directly | from the | SSDs to | the parameter |     | buffer. | Ratel | [32] in- |
| When accessing | is in 4KB  | granularity, |             | it can | only           | achieve |          |          |         |               |     |         |       |          |
troducesSSD-CPUcommunicationasanadditionaloptimiza-
1.3GB/s bandwidth, which is 93.5% lower than the CAM’s tion dimension. Two notable examples of out-of-core GNN
achieved bandwidth.
|                   |      |         |             |           |      |         | training  | systems | are Ginex | [44]       | and MariusGNN |         | [55].           | These |
| ----------------- | ---- | ------- | ----------- | --------- | ---- | ------- | --------- | ------- | --------- | ---------- | ------------- | ------- | --------------- | ----- |
| In conclusion,    | SPDK | with    | overlapping | can       | only | achieve |           |         |           |            |               |         |                 |       |
|                   |      |         |             |           |      |         | platforms | rely on | the CPU   | to         | manage        | disk    | I/O operations. |       |
| ideal performance | when | the CPU | memory      | bandwidth |      | is suf- |           |         |           |            |               |         |                 |       |
|                   |      |         |             |           |      |         | BaM-based | GIDS    | [43]      | represents | an            | attempt | at creating     | a     |
ficient, and when the application has a relatively large access GPU-managed disk-based system that still struggles with the
SSD granularity.
serialexecutionofnodefeatureextractionandtrainingdueto
BaM’ssynchronousinterface.Theirprimaryapproachfocuses
V. RELATEDWORK
|     |     |     |     |     |     |     | on utilizing | CPU | memory | to  | cache data | to  | reduce | the data |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ------ | --- | ---------- | --- | ------ | -------- |
To our knowledge, CAM is the first asynchronous SSD amounttobeaccessedintheSSDwithoutconsideringtheSSD
managementforbatchingstorageaccessthatoffloadstheSSD
accessprocess.Incontrast,CAMcanacceleratetheprocedure
controller from GPU to CPU. In the following, we contrast of SSD data access and help applications make I/O overlap
| CAM and         | existing works       | in          | the following |     | aspects: | GPU- | with computation. |     |     |            |     |     |     |     |
| --------------- | -------------------- | ----------- | ------------- | --- | -------- | ---- | ----------------- | --- | --- | ---------- | --- | --- | --- | --- |
| managed direct  | SSD access,          | CPU-managed |               | SSD | access,  | and  |                   |     |     |            |     |     |     |     |
| massive storage | access applications. |             |               |     |          |      |                   |     | VI. | CONCLUSION |     |     |     |     |
GPU-ManagedDirectSSDAccess. Intherealmofdatabase In this work, we propose CAM, an asynchronous GPU-
query optimization, HippogriffDB [31] has effectively har- initialized,CPU-managedSSDmanagementforbatchingstor-
nessed the power of direct GPU-SSD transfers. On a similar age access. CAM provides a series of APIs for data transfer
front,Morpheus[52]andGPUKV[23]haverefineddataseri- betweenGPUandSSDs,minimizingGPUstreamingmultipro-
alization and the performance of key-value store applications cessorutilizationduringI/Oprocesses,enablingsimultaneous
through the use of in-storage computation. BaM [45] has in- maximization of GPU interface bandwidth, and overlapping
troduced a synchronous model for GPU-initiated SSD access. computationandI/Ooperations.OurstrategyinvolvesaGPU-
Distinctively,CAMoffloadstheSSDmanagementtoCPUuser issued,CPU-managedSSDmanagementapproach,alongwith
space. This approach unlocks the GPU resource, significantly asynchronous APIs that provide a synchronous programming
boosting the efficiency of GNN training processes. experience. Experimental results show that our system can
CPU-Managed SSD Access. Recent advancements in tech- fully utilize the bandwidth of the GPU interface. In the end-
nologiessuchasNVMMU[60]haveenabledGPUstodirectly to-end experiments, CAM can perform GNN models train-
transfer data to and from SSDs using the GPUDirect [39] ing, mergesort, and GEMM up to 1.84×, 1.5×, and 1.84×
technology.Butitstillrequiresakernel/usermodeswitch.Our faster, compared to the existing state-of-the-art GPU systems,
systemdoesnotneedanymodeswitch.Moreimportantly,this while keeping high programmability. CAM is available at
workislatency-oriented,andourworkisthroughput-oriented. https://github.com/RC4ML/CAM.
Recent works [3], [15], [27], [30], [36], [54], [57] study the Acknowledgement. The work is supported by the following
characteristics of SSDs and modern hardware and guide the grants: the National Key R&D Program of China (Grant No.
designfordatamanagementtasks.Junetal.[22]explainwhy 2022ZD0119301), the National Natural Science Foundation
thecontentofafileisnotalwaysmappedtocontinuousblocks. of China under the grant numbers (62236007, 62472384,
Didona et al. [11] presents the first systematic study and 62441236, U24A20326). Zeke Wang is the corresponding
| comparison | of storage APIs | on  | top of | raw block | devices. | In  | author. |     |     |     |     |     |     |     |
| ---------- | --------------- | --- | ------ | --------- | -------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
2320
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore.  Restrictions apply.

REFERENCES [21] HongsunJang,JaeyongSong,JaewonJung,JaeyoungPark,Youngsok
|     |     |     |     |     |     |     | Kim,andJinhoLee. |     | Smart-infinity:Fastlargelanguagemodeltraining |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | --------------------------------------------- | --- | --- | --- | --- |
[1] MuhammadAdnan,YassamanEbrahimzadehMaboud,DivyaMahajan, usingnear-storageprocessingonarealsystem. In2024IEEEInterna-
tionalSymposiumonHigh-PerformanceComputerArchitecture(HPCA),
| and Prashant                  | J. Nair. | Heterogeneous |     | acceleration | pipeline | for recom- |                    |     |     |     |     |     |     |
| ----------------------------- | -------- | ------------- | --- | ------------ | -------- | ---------- | ------------------ | --- | --- | --- | --- | --- | --- |
| mendationsystemtraining,2024. |          |               |     |              |          |            | pages345–360,2024. |     |     |     |     |     |     |
[2] SaurabhAgarwal,ChengpoYan,ZiyiZhang,andShivaramVenkatara- [22] Yuhun Jun, Shinhyun Park, Jeong-Uk Kang, Sang-Hoon Kim, and
man. Bagpipe:Acceleratingdeeprecommendationmodeltraining. In Euiseong Seo. We ain’t afraid of no file fragmentation: causes and
Proceedings of the 29th Symposium on Operating Systems Principles, preventionofitsperformanceimpactonmodernflashssds.InProceed-
SOSP’23,page348–363,NewYork,NY,USA,2023.Associationfor ingsofthe22ndUSENIXConferenceonFileandStorageTechnologies,
| ComputingMachinery. |     |     |     |     |     |     | FAST’24,USA,2024.USENIXAssociation. |     |     |     |     |     |     |
| ------------------- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- |
[3] GustavoAlonso,NatassaAilamaki,SaileshKrishnamurthy,SamMad- [23] Min-Gyo Jung, Chang-Gyu Lee, Donggyu Park, et al. Gpukv: an
den, Swami Sivasubramanian, and Raghu Ramakrishnan. Future of integratedframeworkwithkvssdandgputhroughp2pcommunication
databasesystemarchitectures. InCompanionofthe2023International support. InSAC2021,2021.
ConferenceonManagementofData,pages261–262,2023.
|     |     |     |     |     |     |     | [24] BenKarsin,VolkerWeichert,HenriCasanova,JohnIacono,andNodari |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
[4] SeanBaxter.moderngpu2.0.https://github.com/moderngpu/moderngpu/ Sitchinava. Analysis-driven engineering of comparison-based sorting
wiki,2016. algorithmsongpus.InProceedingsofthe2018InternationalConference
[5] NilsBoeschenandCarstenBinnig.Gacco-agpu-acceleratedoltpdbms. onSupercomputing,ICS’18,page86–95,NewYork,NY,USA,2018.
In Proceedings of the 2022 International Conference on Management AssociationforComputingMachinery.
ofData,pages1003–1016,2022. [25] Arpandeep Khatua, Vikram Sharma Mailthody, Bhagyashree Taleka,
[6] SebastianBreßandGunterSaake. Whyitistimeforahype:ahybrid etal. Igb:Addressingthegapsinlabeling,features,heterogeneity,and
| queryprocessingengineforefficientgpucoprocessingindbms. |     |     |     |     |     | Proc. |                                                   |     |     |     |     |               |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | ----- | ------------------------------------------------- | --- | --- | --- | --- | ------------- | --- |
|                                                         |     |     |     |     |     |       | sizeofpublicgraphdatasetsfordeeplearningresearch. |     |     |     |     | arXivpreprint |     |
| VLDBEndow.,6(12):1398–1403,August2013.                  |     |     |     |     |     |       | arXiv:2302.13522,2023.                            |     |     |     |     |               |     |
[7] Daniel Cederman and Philippas Tsigas. Gpu-quicksort: A practical [26] ThomasNKipfandMaxWelling. Semi-supervisedclassificationwith
| quicksortalgorithmforgraphicsprocessors. |     |     |     | ACMJ.Exp.Algorithmics, |     |     |                             |     |     |                                     |     |     |     |
| ---------------------------------------- | --- | --- | --- | ---------------------- | --- | --- | --------------------------- | --- | --- | ----------------------------------- | --- | --- | --- |
|                                          |     |     |     |                        |     |     | graphconvolutionalnetworks. |     |     | arXivpreprintarXiv:1609.02907,2016. |     |     |     |
14,January2010.
|     |     |     |     |     |     |     | [27] Artem Kroviakov, | Petr | Kurapov, | Christoph | Anneser, | and | Jana Giceva. |
| --- | --- | --- | --- | --- | --- | --- | --------------------- | ---- | -------- | --------- | -------- | --- | ------------ |
[8] Yunpeng Chai, Yanfeng Chai, Xin Wang, Haocheng Wei, Ning Bao, Heterogeneousintra-pipelinedevice-parallelaggregations. InProceed-
and Yushi Liang. Ldc: a lower-level driven compaction method to ingsofthe20thInternationalWorkshoponDataManagementonNew
optimizessd-orientedkey-valuestores.In2019IEEE35thInternational
Hardware,pages1–10,2024.
ConferenceonDataEngineering(ICDE),pages722–733.IEEE,2019. [28] BohyunLee,MijinAn,andSang-WonLee.Lru-c:Parallelizingdatabase
[9] Cheng-Yu Chen, Jui-Nan Yen, You-Ru Lai, Yun-Ping Lin, and Chia- i/osforflashssds. ProceedingsoftheVLDBEndowment,16(9):2364–
| Lin Yang. | Rects: | A temporal-aware |     | memory system | optimization | for |     |     |     |     |     |     |     |
| --------- | ------ | ---------------- | --- | ------------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
2376,2023.
| trainingdeeplearningrecommendationmodels. |     |     |     |     | InProceedingsofthe |     |                                                                    |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | --- | --- | ------------------ | --- | ------------------------------------------------------------------ | --- | --- | --- | --- | --- | --- |
|                                           |     |     |     |     |                    |     | [29] SangjinLee,AlbertoLerner,Andre´Ryser,KibinPark,ChanyoungJeon, |     |     |     |     |     |     |
17thACMInternationalSystemsandStorageConference,SYSTOR’24, Jinsub Park, Yong Ho Song, and Philippe Cudre´-Mauroux. X-ssd: A
page104–117,NewYork,NY,USA,2024.AssociationforComputing
storagesystemwithnativesupportfordatabaseloggingandreplication.
Machinery.
|     |     |     |     |     |     |     | In Proceedings | of the | 2022 International |     | Conference | on  | Management |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ------ | ------------------ | --- | ---------- | --- | ---------- |
[10] Jiajia Chu, Yunshan Tu, Yao Zhang, and Chuliang Weng. Latte: A ofData,pages988–1002,2022.
In2020IEEE36thInternational
nativetableengineonnvmestorage. [30] Alberto Lerner and Gustavo Alonso. Data flow architectures for data
| Conference | on Data | Engineering | (ICDE), | pages | 1225–1236. | IEEE, |                                                       |           |           |     |           |      |               |
| ---------- | ------- | ----------- | ------- | ----- | ---------- | ----- | ----------------------------------------------------- | --------- | --------- | --- | --------- | ---- | ------------- |
|            |         |             |         |       |            |       | processing                                            | on modern | hardware. | In  | 2024 IEEE | 40th | International |
| 2020.      |         |             |         |       |            |       | ConferenceonDataEngineering,pages5511–5522.IEEE,2024. |           |           |     |           |      |               |
[11] DiegoDidona,JonasPfefferle,NikolasIoannou,BernardMetzler,and [31] JingLi,Hung-WeiTseng,ChunbinLin,etal. Hippogriffdb:Balancing
| Animesh  | Trivedi. | Understanding | modern    | storage        | apis: a | systematic  |                                                             |     |     |     |       |     |     |
| -------- | -------- | ------------- | --------- | -------------- | ------- | ----------- | ----------------------------------------------------------- | --- | --- | --- | ----- | --- | --- |
|          |          |               |           |                |         |             | i/oandgpubandwidthinbigdataanalytics.                       |     |     |     | 2016. |     |     |
| study of | libaio,  | spdk, and     | io uring. | In Proceedings |         | of the 15th |                                                             |     |     |     |       |     |     |
|          |          |               |           |                |         |             | [32] ChangyueLiao,MoSun,ZihanYang,KaiqiChen,BinhangYuan,Fei |     |     |     |       |     |     |
ACMInternationalConferenceonSystemsandStorage,SYSTOR’22, Wu,andZekeWang. Addingnvmessdstoenableandaccelerate100b
page120–127,NewYork,NY,USA,2022.AssociationforComputing
modelfine-tuningonasinglegpu,2024.
Machinery.
|               |          |              |       |        |              |         | [33] MichaelLui,YavuzYetim,O¨zgu¨rO¨zkan,ZhuoranZhao,Shin-YehTsai, |     |     |     |     |     |     |
| ------------- | -------- | ------------ | ----- | ------ | ------------ | ------- | ------------------------------------------------------------------ | --- | --- | --- | --- | --- | --- |
| [12] Jaeyoung | Do, Ivan | Luiz Picoli, | David | Lomet, | and Philippe | Bonnet. |                                                                    |     |     |     |     |     |     |
Betterdatabasecost/performanceviabatchedi/oonprogrammablessd. Carole-JeanWu,andMarkHempstead. Understandingcapacity-driven
scale-outneuralrecommendationinference.In2021IEEEInternational
TheVLDBJournal,30:403–424,2021.
SymposiumonPerformanceAnalysisofSystemsandSoftware(ISPASS),
| [13] CarlDuffy,JaehoonShim,Sang-HoonKim,andJin-SooKim. |     |     |     |     |     | Dotori: |     |     |     |     |     |     |     |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
pages162–171,2021.
| Akey-valuessdbasedkvstore. |     |     | ProceedingsoftheVLDBEndowment, |     |     |     |     |     |     |     |     |     |     |
| -------------------------- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
16(6):1560–1572,2023. [34] YanfeiLv,BinCui,BingshengHe,andXuexuanChen.Operation-aware
|     |     |     |     |     |     |     | buffermanagementinflash-basedsystems. |     |     |     | InProceedingsofthe2011 |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------- | --- | --- | --- | ---------------------- | --- | --- |
[14] XiaopengFan,SongYan,YuchenHuang,andChuliangWeng.Tengine:
ACMSIGMODInternationalConferenceonManagementofdata,pages
| A native | distributed | table storage | engine.     | In      | 2024 IEEE | 40th Inter- |                     |          |      |          |          |         |       |
| -------- | ----------- | ------------- | ----------- | ------- | --------- | ----------- | ------------------- | -------- | ---- | -------- | -------- | ------- | ----- |
| national | Conference  | on Data       | Engineering | (ICDE), | pages     | 3782–3795.  | 13–24,2011.         |          |      |          |          |         |       |
|          |             |               |             |         |           |             | [35] Steffen Maass, | Changwoo | Min, | Sanidhya | Kashyap, | Woonhak | Kang, |
IEEE,2024.
|                                |     |     |                                |     |     |     | Mohan Kumar, | and | Taesoo Kim. | Mosaic: | Processing | a   | trillion-edge |
| ------------------------------ | --- | --- | ------------------------------ | --- | --- | --- | ------------ | --- | ----------- | ------- | ---------- | --- | ------------- |
| [15] GabrielHaasandViktorLeis. |     |     | Whatmodernnvmestoragecando,and |     |     |     |              |     |             |         |            |     |               |
how to exploit it: high-performance i/o for high-performance storage graph on a single machine. In Proceedings of the Twelfth European
|     |     |     |     |     |     |     | Conference | on Computer | Systems, | EuroSys | ’17, | page 527–543, | New |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ----------- | -------- | ------- | ---- | ------------- | --- |
engines.ProceedingsoftheVLDBEndowment,16(9):2090–2102,2023.
York,NY,USA,2017.AssociationforComputingMachinery.
[16] WillHamilton,ZhitaoYing,andJureLeskovec.Inductiverepresentation
InNIPS2017,2017. [36] Fabio Maschi and Gustavo Alonso. The difficult balance between
learningonlargegraphs.
[17] Michael Haubenschild, Caetano Sauer, Thomas Neumann, and Vik- modern hardware and conventional cpus. In Proceedings of the 19th
InternationalWorkshoponDataManagementonNewHardware,pages
| tor Leis. | Rethinking | logging, | checkpoints, | and | recovery | for high- |     |     |     |     |     |     |     |
| --------- | ---------- | -------- | ------------ | --- | -------- | --------- | --- | --- | --- | --- | --- | --- | --- |
53–62,2023.
performancestorageengines.InProceedingsofthe2020ACMSIGMOD
InternationalConferenceonManagementofData,pages877–892,2020. [37] Meta. Torchrec. https://github.com/pytorch/torchrec/,2022. Accessed:
October5,2024.
[18] HaochenHe,ErciXu,ShanshanLi,ZhouyangJia,SiZheng,YueYu,Jun
|                    |     |                                        |     |     |     |     | [38] JasonMohoney,RogerWaleffe,HenryXu,TheodorosRekatsinas,and |     |     |     |     |     |     |
| ------------------ | --- | -------------------------------------- | --- | --- | --- | --- | -------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| Ma,andXiangkeLiao. |     | Whendatabasemeetsnewstoragedevices:Un- |     |     |     |     |                                                                |     |     |     |     |     |     |
derstanding and exposing performance mismatches via configurations. ShivaramVenkataraman. Marius:Learningmassivegraphembeddings
ProceedingsoftheVLDBEndowment,16(7):1712–1725,2023. on a single machine. In 15th USENIX Symposium on Operating Sys-
temsDesignandImplementation(OSDI21),pages533–549.USENIX
[19] WeihuaHu,MatthiasFey,MarinkaZitnik,etal.Opengraphbenchmark:
|     |     |     |     | InNIPS2020,2020. |     |     | Association,July2021. |     |     |     |     |     |     |
| --- | --- | --- | --- | ---------------- | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- |
Datasetsformachinelearningongraphs.
[20] YuchenHuang,XiaopengFan,SongYan,andChuliangWeng.Neos:A [39] NVIDIA. NVIDIAGPUDirect. https://developer.nvidia.com/gpudirect,
2011.
nvme-gpusdirectvectorservicebufferinuserspace.In2024IEEE40th
|               |            |     |                  |     |               |       | [40] Nvidia. GPUDirectStorage:ADirectPathBetweenStorageandGPU |     |     |     |     |     |     |
| ------------- | ---------- | --- | ---------------- | --- | ------------- | ----- | ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| International | Conference | on  | Data Engineering |     | (ICDE), pages | 3767– |                                                               |     |     |     |     |     |     |
3781.IEEE,2024. Memory. https://developer.nvidia.com/blog/gpudirect-storage/,2022.
2321
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore.  Restrictions apply.

|     |     |     |     |     |     |     |     | [61] Weijie Zhao, | Deping Xie, | Ronglai | Jia, Yulei | Qian, Ruiquan Ding, |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | ----------- | ------- | ---------- | ------------------- |
[41] TarikulIslamPapon.Enhancingdatasystemsperformancebyexploiting
ssdconcurrency&asymmetry.InProceedingsoftheIEEEInternational Mingming Sun, and Ping Li. Distributed hierarchical gpu parameter
ConferenceonDataEngineeringPhDSymposium,2024. serverformassivescaledeeplearningadssystems,2020.
|                                              |     |     |     |     |                     |     |     | [62] GuoruiZhou,XiaoqiangZhu,ChenruSong,YingFan,HanZhu,Xiao |     |     |     |     |
| -------------------------------------------- | --- | --- | --- | --- | ------------------- | --- | --- | ----------------------------------------------------------- | --- | --- | --- | --- |
| [42] TarikulIslamPaponandManosAthanassoulis. |     |     |     |     | Aceingthebufferpool |     |     |                                                             |     |     |     |     |
managementparadigmformodernstoragedevices. In2023IEEE39th Ma,YanghuiYan,JunqiJin,HanLi,andKunGai.Deepinterestnetwork
International Conference on Data Engineering (ICDE), pages 1326– forclick-throughrateprediction.KDD’18,page1059–1068,NewYork,
NY,USA,2018.AssociationforComputingMachinery.
1339.IEEE,2023.
|               |       |              |     |                   |     |               |     | [63] RongZhu,KunZhao,HongxiaYang,WeiLin,ChangZhou,BaoleAi, |     |     |     |     |
| ------------- | ----- | ------------ | --- | ----------------- | --- | ------------- | --- | ---------------------------------------------------------- | --- | --- | --- | --- |
| [43] Jeongmin | Brian | Park, Vikram |     | Sharma Mailthody, |     | Zaid Qureshi, | and |                                                            |     |     |     |     |
Wen-meiHwu.Acceleratingsamplingandaggregationoperationsingnn Yong Li, and Jingren Zhou. Aligraph: a comprehensive graph neural
|            |      |               |        |         |           |       |          | networkplatform.     | Proc.VLDBEndow.,12(12):2094–2105,aug2019. |     |              |                    |
| ---------- | ---- | ------------- | ------ | ------- | --------- | ----- | -------- | -------------------- | ----------------------------------------- | --- | ------------ | ------------------ |
| frameworks | with | gpu initiated | direct | storage | accesses. | arXiv | preprint |                      |                                           |     |              |                    |
|            |      |               |        |         |           |       |          | [64] Tobias Ziegler, | Carsten Binnig,                           | and | Viktor Leis. | Scalestore: A fast |
arXiv:2306.16384,2023.
|               |       |         |      |         |        |                    |     | and cost-efficient | storage | engine using | dram, | nvme, and rdma. In |
| ------------- | ----- | ------- | ---- | ------- | ------ | ------------------ | --- | ------------------ | ------- | ------------ | ----- | ------------------ |
| [44] Yeonhong | Park, | Sunhong | Min, | and Jae | W Lee. | Ginex: Ssd-enabled |     |                    |         |              |       |                    |
billion-scale graph neural network training on a single machine via Proceedings of the 2022 International Conference on Management of
Data,pages685–699,2022.
| provablyoptimalin-memorycaching. |          |               |     | InVLDB2022,2022. |               |     |          |     |     |     |     |     |
| -------------------------------- | -------- | ------------- | --- | ---------------- | ------------- | --- | -------- | --- | --- | --- | --- | --- |
| [45] Zaid                        | Qureshi, | Vikram Sharma |     | Mailthody,       | Isaac Gelado, | et  | al. Gpu- |     |     |     |     |     |
initiatedon-demandhigh-throughputstorageaccessinthebamsystem
| architecture. |     | InASPLOS2023,2023. |     |     |     |     |     |     |     |     |     |     |
| ------------- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[46] SamyamRajbhandari,OlatunjiRuwase,JeffRasley,ShadenSmith,and
| YuxiongHe.         |             | Zero-infinity:breakingthegpumemorywallforextreme |     |             |         |               |     |     |     |     |     |     |
| ------------------ | ----------- | ------------------------------------------------ | --- | ----------- | ------- | ------------- | --- | --- | --- | --- | --- | --- |
| scaledeeplearning. |             | InProceedingsoftheInternationalConferencefor     |     |             |         |               |     |     |     |     |     |     |
| High               | Performance | Computing,                                       |     | Networking, | Storage | and Analysis, | SC  |     |     |     |     |     |
’21,NewYork,NY,USA,2021.AssociationforComputingMachinery.
[47] SagarShedge,NishantSharma,AnantAgarwal,MohammedAbouzour,
| andGu¨nes¸Aluc¸. |     | Anextendedssd-basedcacheforefficientobjectstore |     |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| accessinsapiq.   |     | In2022IEEE38thInternationalConferenceonData     |     |     |     |     |     |     |     |     |     |     |
Engineering(ICDE),pages1861–1873.IEEE,2022.
[48] YingSheng,LianminZheng,BinhangYuan,ZhuohanLi,MaxRyabinin,
| Daniel    | Y. Fu, | Zhiqiang | Xie, Beidi  | Chen, | Clark       | Barrett, | Joseph E. |     |     |     |     |     |
| --------- | ------ | -------- | ----------- | ----- | ----------- | -------- | --------- | --- | --- | --- | --- | --- |
| Gonzalez, | Percy  | Liang,   | Christopher | Re´,  | Ion Stoica, | and      | Ce Zhang. |     |     |     |     |     |
Flexgen:High-throughputgenerativeinferenceoflargelanguagemodels
withasinglegpu,2023.
| [49] Solidigm. | D7-P5510 | high-performing,                                         |     | standard-endurance |     |     | PCIe 4.0 |     |     |     |     |     |
| -------------- | -------- | -------------------------------------------------------- | --- | ------------------ | --- | --- | -------- | --- | --- | --- | --- | --- |
| NVMe           | SSD      | drive. https://www.solidigm.com/products/data-center/d7/ |     |                    |     |     |          |     |     |     |     |     |
p5510.html,2021.
| [50] Young-Kyoon |                                                   | Suh, Junyoung  | An,   | Byungchul     | Tak,        | and Gap-Joo | Na.        |     |     |     |     |     |
| ---------------- | ------------------------------------------------- | -------------- | ----- | ------------- | ----------- | ----------- | ---------- | --- | --- | --- | --- | --- |
| A comprehensive  |                                                   | empirical      | study | of query      | performance |             | across gpu |     |     |     |     |     |
| dbmses.          | Proc.ACMMeas.Anal.Comput.Syst.,6(1),February2022. |                |       |               |             |             |            |     |     |     |     |     |
| [51] Mo Sun,     | Zihan                                             | Yang, Changyue |       | Liao, Yingtao | Li,         | Fei Wu,     | and Zeke   |     |     |     |     |     |
Wang.Luwu:Anend-to-endin-networkout-of-coreoptimizerfor100b-
scalemodel-in-networkdata-paralleltrainingondistributedgpus,2024.
| [52] Hung-Wei | Tseng,      | Qianchen | Zhao,       | Yuxiao | Zhou,         | et al. | Morpheus:  |     |     |     |     |     |
| ------------- | ----------- | -------- | ----------- | ------ | ------------- | ------ | ---------- | --- | --- | --- | --- | --- |
| Creating      | application | objects  | efficiently | for    | heterogeneous |        | computing. |     |     |     |     |     |
ACMSIGARCHComputerArchitectureNews,2016.
[53] PetarVelicˇkovic´,GuillemCucurull,ArantxaCasanova,AdrianaRomero,
PietroLio,andYoshuaBengio.Graphattentionnetworks.arXivpreprint
arXiv:1710.10903,2017.
| [54] Leonard                                      | Von  | Merzljak, | Philipp | Fent, Thomas | Neumann,   |                  | and Jana |     |     |     |     |     |
| ------------------------------------------------- | ---- | --------- | ------- | ------------ | ---------- | ---------------- | -------- | --- | --- | --- | --- | --- |
| Giceva.                                           | What | are you   | waiting | for? use     | coroutines | for asynchronous |          |     |     |     |     |     |
| i/otohidei/olatenciesandmaximizethereadbandwidth! |      |           |         |              |            |                  | InADMS@  |     |     |     |     |     |
VLDB,pages36–46,2022.
| [55] Roger           | Waleffe, | Jason Mohoney, |                     | Theodoros                | Rekatsinas, | and | Shivaram    |     |     |     |     |     |
| -------------------- | -------- | -------------- | ------------------- | ------------------------ | ----------- | --- | ----------- | --- | --- | --- | --- | --- |
| Venkataraman.        |          | Mariusgnn:     | Resource-efficient  |                          | out-of-core |     | training of |     |     |     |     |     |
| graphneuralnetworks. |          |                | InEuroSys2023,2023. |                          |             |     |             |     |     |     |     |     |
| [56] Jianguo         | Wang,    | Chunbin        | Lin,                | Yannis Papakonstantinou, |             |     | and Steven  |     |     |     |     |     |
Swanson.Evaluatinglistintersectiononssdsforparalleli/oskipping.In
2021IEEE37thInternationalConferenceonDataEngineering(ICDE),
pages1823–1828.IEEE,2021.
| [57] JiaWeiandXingjunZhang. |     |            | Howmuchstoragedoweneedforhigh |      |               |            |     |     |     |     |     |     |
| --------------------------- | --- | ---------- | ----------------------------- | ---- | ------------- | ---------- | --- | --- | --- | --- | --- | --- |
| performance                 |     | server. In | 2022 IEEE                     | 38th | International | Conference | on  |     |     |     |     |     |
DataEngineering(ICDE),pages3221–3225.IEEE,2022.
| [58] Mark | Wilkening, | Udit Gupta, | Samuel | Hsia, | Caroline | Trippel, | Carole- |     |     |     |     |     |
| --------- | ---------- | ----------- | ------ | ----- | -------- | -------- | ------- | --- | --- | --- | --- | --- |
JeanWu,DavidBrooks,andGu-YeonWei.Recssd:neardataprocessing
| for solid | state | drive based | recommendation |     | inference. | ASPLOS | ’21, |     |     |     |     |     |
| --------- | ----- | ----------- | -------------- | --- | ---------- | ------ | ---- | --- | --- | --- | --- | --- |
page717–729,NewYork,NY,USA,2021.AssociationforComputing
Machinery.
[59] DalongZhang,XinHuang,ZiqiLiu,JunZhou,ZhiyangHu,Xianzheng
| Song,    | Zhibang | Ge, Lin                | Wang, | Zhiqiang | Zhang, and | Yuan      | Qi. Agl: a |     |     |     |     |     |
| -------- | ------- | ---------------------- | ----- | -------- | ---------- | --------- | ---------- | --- | --- | --- | --- | --- |
| scalable | system  | for industrial-purpose |       | graph    | machine    | learning. | Proc.      |     |     |     |     |     |
VLDBEndow.,13(12):3125–3137,aug2020.
| [60] JieZhang,DavidDonofrio,JohnShalf,etal.               |     |     |     |     | Nvmmu:Anon-volatile |     |     |     |     |     |     |     |
| --------------------------------------------------------- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- |
| memorymanagementunitforheterogeneousgpu-ssdarchitectures. |     |     |     |     |                     |     | In  |     |     |     |     |     |
PACT2015,2015.
2322
Authorized licensed use limited to: Zhejiang University. Downloaded on October 27,2025 at 00:06:45 UTC from IEEE Xplore.  Restrictions apply.