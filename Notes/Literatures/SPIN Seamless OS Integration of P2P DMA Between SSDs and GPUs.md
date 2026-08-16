# SPIN

**Source**: SPIN.pdf
**Format**: .pdf

---

SPIN: Seamless Operating System Integration of
Peer-to-Peer DMA Between SSDs and GPUs
Shai Bergman and Tanya Brokhman, Technion; Tzachi Cohen, unaffiliated;
Mark Silberstein, Technion
https://www.usenix.org/conference/atc17/technical-sessions/presentation/bergman
This paper is included in the Proceedings of the
2017 USENIX Annual Technical Conference (USENIX ATC ’17).
July 12–14, 2017 • Santa Clara, CA, USA
ISBN 978-1-931971-38-6
Open access to the Proceedings of the
2017 USENIX Annual Technical Conference
is sponsored by USENIX.

SPIN: Seamless Operating System Integration of Peer-to-Peer DMA
|     |             |     |     | Between       | SSDs | and         | GPUs |     |                 |          |     |
| --- | ----------- | --- | --- | ------------- | ---- | ----------- | ---- | --- | --------------- | -------- | --- |
|     | ShaiBergman |     |     | TanyaBrokhman |      | TzachiCohen |      |     | MarkSilberstein |          |     |
|     | Technion    |     |     | Technion      |      |             |      |     |                 | Technion |     |
Abstract
|     |     |     |     |     |     | In  | order | to realize | the potential | of high | speed I/O de- |
| --- | --- | --- | --- | --- | --- | --- | ----- | ---------- | ------------- | ------- | ------------- |
vicesinGPUworkloads,allrecentdiscreteGPUsenable
Recent GPUs enable Peer-to-Peer Direct Memory Ac- peer-to-peer direct memory access (P2P) to GPU mem-
cess(P2P)fromfastperipheraldeviceslikeNVMeSSDs oryfromPCIe-attachedperipherals[2,3]. P2Peliminates
to exclude the CPU from the data path between them redundantcopiesinCPUmemorywhentransferringdata
| for efficiency. |     | Unfortunately, | using | P2P | to access files |                    |     |     |                                |     |     |
| --------------- | --- | -------------- | ----- | --- | --------------- | ------------------ | --- | --- | ------------------------------ | --- | --- |
|                 |     |                |       |     |                 | betweenthedevices. |     |     | WithoutP2P,copyingfilecontents |     |     |
ischallengingbecauseofthesubtletiesoflow-levelnon- intoaGPUbufferrequiresreadingitfirstintoaninterme-
standard interfaces, which bypass the OS file I/O layers diate CPU buffer, which is then transferred to the GPU.
andmayhurtsystemperformance. P2PallowsdirecttransfersintoGPUmemory,improving
SPINintegratesP2PintothestandardOSfileI/Ostack, performanceandpowerefficiency,ashasbeenshownin
| dynamicallyactivating |     | P2P | whereappropriate, |     | transpar- |     |     |     |     |     |     |
| --------------------- | --- | --- | ----------------- | --- | --------- | --- | --- | --- | --- | --- | --- |
severalpriorworks[4–8].
ently to the user. It combines P2P with page cache Unfortunately, P2P poses significant programming
| accesses, | re-enables | read-ahead |     | for sequential | reads, |             |     |            |       |                 |          |
| --------- | ---------- | ---------- | --- | -------------- | ------ | ----------- | --- | ---------- | ----- | --------------- | -------- |
|           |            |            |     |                |        | challenges. |     | First, the | usage | of P2P requires | intimate |
all while maintaining standard POSIX FS consistency, knowledgeoflow-levelhardwareconstraints. Forexam-
portability across GPUs and SSDs, and compatibility ple,P2Pcannotaccessfilesatmisalignedfileoffsets[9],
withvirtualblockdevicessuchassoftwareRAID.
andmaybesloworunusableacrossdevicesindifferent
| We                            | evaluate | SPIN on NVIDIA |     | and AMD              | GPUs us- | NUMAnodes[10]. |     |     |     |     |     |
| ----------------------------- | -------- | -------------- | --- | -------------------- | -------- | -------------- | --- | --- | --- | --- | --- |
| ingstandardfileI/Obenchmarks, |          |                |     | applicationtracesand |          |                |     |     |     |     |     |
Morecrucially,P2Pactuallyhurtssystemperformance
end-to-end experiments. SPIN achieves significant per- for a range of popular file access patterns. Figure 1
formancespeedupsacrossawiderangeofworkloads,ex-
|     |     |     |     |     |     | showsonesuchexample. |     |     | ForshortsequentialreadsP2P |     |     |
| --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | -------------------------- | --- | --- |
ceedingP2Pthroughputbyuptoanorderofmagnitude.
|     |     |     |     |     |     | is dramatically |     | slower | than CPU-mediated |     | I/O. It per- |
| --- | --- | --- | --- | --- | --- | --------------- | --- | ------ | ----------------- | --- | ------------ |
It also boosts the performance of an aerial imagery ren- forms faster only for reads larger than 512KB. In this
| dering | application | by 2.6× | by dynamically |     | adapting to |     |     |     |     |     |     |
| ------ | ----------- | ------- | -------------- | --- | ----------- | --- | --- | --- | --- | --- | --- |
scenario,CPU-mediatedI/OreapsthebenefitsoftheOS
itsinput-dependentfileaccesspattern,andenables3.3×
read-aheadmechanism,whichP2Pbypasses.
higherthroughputforaGPU-acceleratedlogserver.
Finally,theuseofP2PinhybridCPU-GPUproducer-
consumerworkloadsispronetosubtleconsistencybugs.
1 Introduction Consider, forexample, alogprocessingapplicationlike
|                 |     |              |       |         |           | fail2Ban | [11],   | accelerated | by      | leveraging  | GPUs. Using      |
| --------------- | --- | ------------ | ----- | ------- | --------- | -------- | ------- | ----------- | ------- | ----------- | ---------------- |
|                 |     |              |       |         |           | P2P      | to read | recently    | updated | files might | result in an in- |
| GPU-accelerated |     | applications | often | require | fast data |          |         |             |         |             |                  |
transfers between the GPU and storage devices. They consistent read if the contents have not yet reached the
combine high I/O demands with heavy computations disk.Furthermore,becauseP2Pisnotintegratedwiththe
amenabletoGPUacceleration. Thus,applicationperfor- page cache, users would not benefit from the extensive
manceisboundedbythethroughputoftransfersbetween OSeffortstocachefilecontents.
the disk and the GPU. As high-speed NVMe SSDs with WeconcludethatP2PbetweenSSDsandGPUsistoo
multi-GB/s I/O rates are becoming commodity, we ex- low-level a mechanism to be exposed directly to devel-
pect an increasing number of I/O-intensive applications opers. Existingframeworks[4–8]providenon-standard,
to benefit from GPU acceleration. In fact, recent AMD custom APIs for performing P2P, but rely on the pro-
Solid State GPUs (SSG) [1] target such I/O intensive grammer to work around its limitations and to choose
workloadsbyhostingNVMeSSDsonaGPUcard. the best-performing transfer mechanism for a given ap-
USENIX Association 2017 USENIX Annual Technical Conference    167

plication scenario. Instead, the OS should hide the sub- SPINiscompatiblewithvirtualblockdevicessuchas
tleties of direct access to storage, exploit existing file software RAID, in contrast to the published P2P imple-
I/O optimization mechanisms like read-ahead and page mentations. SPINachievesupto5.2GB/soffilestream-
cache, while dynamically and transparently steering the ingperformancefromtwoSSDsinRAID-0managedby
datapathtoP2P. Linux software RAID [12] – the fastest P2P result re-
SPINisasystemthatachievesthesegoalsbyintegrat- ported to date, to the best of our knowledge. For com-
ingP2PintothefileI/OlayerintheOS.Theprogrammer parison, AMD SSG [1] GPUs with the SSD drives on
pread pwrite a GPU card [13] reportedly achieve 4GB/s and require
| uses standard |     |     | and | calls | to transfer | the |     |     |     |     |     |     |     |
| ------------- | --- | --- | --- | ----- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
file contents to and from the GPU memory, while SPIN customAPIandspecial-purposehardware.
seamlessly activates P2P when necessary. Unlike previ- In real application scenarios, we evaluate a GPU-
ous works on P2P [4–8] which target GPU-only work- acceleratedlogserver,anaerialimageryviewer[14],and
loadswithlargesequentialreads,SPINaddressesabroad an image collage creator [15]. SPIN achieves signifi-
|          |             |           |     |      |         |             | cantspeedupsforallapplications, |     |     |     | e.g., | 3.3×forthelog |     |
| -------- | ----------- | --------- | --- | ---- | ------- | ----------- | ------------------------------- | --- | --- | --- | ----- | ------------- | --- |
| range of | application | scenarios |     | with | diverse | file access |                                 |     |     |     |       |               |     |
patternsandcooperativeCPU-GPUprocessing. server.Ahighlyoptimizedimplementationofthecollage
creatorisimprovedby29%whilerequiringmodification
| SPIN                                          | addresses | three | key | challenges: | integration | of  |              |     |     |     |     |     |     |
| --------------------------------------------- | --------- | ----- | --- | ----------- | ----------- | --- | ------------ | --- | --- | --- | --- | --- | --- |
| P2Pwiththepagecache,read-aheadforGPUreads,and |           |       |     |             |             |     | ofonly10LOC. |     |     |     |     |     |     |
invocationofP2PviaadirectdiskI/Ointerface. Ourmaincontributionsareasfollows:
Combining page cache and P2P. If a GPU read re- • Analysis of programmability and performance limita-
| quest can | be partially |     | served | from the | CPU page | cache, | tionsofP2P. |     |     |     |     |     |     |
| --------- | ------------ | --- | ------ | -------- | -------- | ------ | ----------- | --- | --- | --- | --- | --- | --- |
naivelyreadingallthecacheddatafrommemoryandthe • IntegrationofP2PintotheOSfileI/Ostack,including
rest via P2P might be slower by up to 16× vs. serving standard file I/O API, page cache with a transfer in-
thewholerequestviaP2P. Weconstructagreedyheuris- terleaving scheduler, read-ahead and enabling P2P via
| ticthatsolvestheunderlyingschedulingproblemforev- |     |     |     |     |     |     | directI/O. |     |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- |
ery access, and produces the interleaving schedule that • Thorough evaluation on synthetic and real workloads
achievesabout98%oftheoptimalperformance(§4.3.1). forbothNVIDIAandAMDGPUs,showingsignificant
GPU read-ahead. Our read-ahead mechanism uses performancebenefitsofSPINoveralternatives.
CPUpagecachepagestostorethecontentsofprefetched
| dataforGPUreads. |     | However,SPINpreventspagecache |     |     |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2 Background
| pollution | by maintaining |     | a   | separate | GPU | read-ahead |     |     |     |     |     |     |     |
| --------- | -------------- | --- | --- | -------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
evictionpolicythatrestrictsthespaceusedforprefetched Thissectionprovidesabriefoverviewofthesystemar-
contents(§4.3.2).
chitecturewetargetinourwork.
| Direct         | disk | I/O for     | P2P. Using | direct    | disk            | I/O inter- |                      |     |     |          |          |       |     |
| -------------- | ---- | ----------- | ---------- | --------- | --------------- | ---------- | -------------------- | --- | --- | -------- | -------- | ----- | --- |
|                |      |             |            |           |                 |            | System architecture. |     | We  | consider | a system | where | the |
| face to invoke |      | P2P SSD-GPU |            | transfers | is advantageous |            |                      |     |     |          |          |       |     |
CPU,discreteGPUs,andNVMeSSDareconnectedvia
becauseofitstightintegrationwiththefileI/Ostack,in- PeripheralComponentInterconnectExpress(PCIe)bus.
cludingpagecacheconsistencyhandlingandfileoffset-
ThePCIeswitchenablesfastpeer-to-peerdirectmemory
| to-logical | block | address | mapping. | However, |     | direct I/O |     |     |     |     |     |     |     |
| ---------- | ----- | ------- | -------- | -------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
access(P2P)betweentheGPUandtheSSD.P2Pallows
callscannotbeusedwithGPUresidentpages.Wedevise
|     |     |     |     |     |     |     | the SSD to | transfer | data | directly | to/from | GPU memory, |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | -------- | ---- | -------- | ------- | ----------- | --- |
alightweightaddresstunnelingmechanismtoovercome
bypassingtheCPU.
thisproblem(§5.1).
|              |     |     |                |     |          |         | Mapping | GPU memory |     | into | process | address | space. |
| ------------ | --- | --- | -------------- | --- | -------- | ------- | ------- | ---------- | --- | ---- | ------- | ------- | ------ |
| We implement |     | and | systematically |     | evaluate | SPIN in |         |            |     |      |         |         |        |
GPUsexposeaportionofGPUmemoryonthePCIebus
| Linux by  | running | standard | file          | system | benchmarks, | ap-    |           |                 |     |        |      |          |        |
| --------- | ------- | -------- | ------------- | ------ | ----------- | ------ | --------- | --------------- | --- | ------ | ---- | -------- | ------ |
|           |         |          |               |        |             |        | (device’s | BAR) accessible |     | to the | CPU. | To allow | access |
| plication | traces  | and full | applications. |        | We use      | NVIDIA |           |                 |     |        |      |          |        |
tothismemoryfromausermodeapplicationNVIDIA’s
| K40 and    | AMD        | R9 Fury | GPUs   | with       | two Intel | P3700 |         |           |        |     |            |         |     |
| ---------- | ---------- | ------- | ------ | ---------- | --------- | ----- | ------- | --------- | ------ | --- | ---------- | ------- | --- |
|            |            |         |        |            |           |       | gdrcopy | and AMD’s | OpenCL |     | extensions | provide | the |
| SSDs, both | separately |         | and in | a software | RAID.     | SPIN  |         |           |        |     |            |         |     |
toolstomapitintotheprocessaddressspace.
| tracks or | exceeds | the | performance | of  | the best | transfer |     |     |     |     |     |     |     |
| --------- | ------- | --- | ----------- | --- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- |
mechanism for the respective access pattern, with pro- DirectdiskI/O.DirectdiskI/O(O DIRECT)allowsfile
|     |     |     |     |     |     |     | system operations |     | to bypass | kernel | caches | and | interact |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --------- | ------ | ------ | --- | -------- |
nouncedbenefitsoverP2Pforsequentialaccessesandac-
directlywiththestoragedevice.
| cessestocachedfiles.                           |         |             | Forexample,itachieves10.1GB/s |             |        |           |              |     |     |     |     |     |     |
| ---------------------------------------------- | ------- | ----------- | ----------------------------- | ----------- | ------ | --------- | ------------ | --- | --- | --- | --- | --- | --- |
| when reading                                   |         | a file from | the                           | page cache  | – 3.8× | higher    |              |     |     |     |     |     |     |
| than2.65GB/sofP2Pinthesameconfiguration(within |         |             |                               |             |        |           | 3 Motivation |     |     |     |     |     |     |
| 5% of the                                      | maximum |             | SSD                           | bandwidth). | For    | partially |              |     |     |     |     |     |     |
cachedfiles,SPINisfasterthaneitherCPU-mediatedI/O Prior works [4–8] show that P2P between SSDs and
orP2Pinisolation,e.g.,by2×and20%respectivelyfor GPUssubstantiallyboostssystemperformanceforpopu-
50%cachehits. larGPUbenchmarks. Theseapplicationsexhibitstream-
168    2017 USENIX Annual Technical Conference USENIX Association

(cid:7)(cid:2)(cid:1)(cid:1) (cid:1)(cid:15)(cid:15)(cid:16)(cid:5) (cid:1)(cid:17)(cid:18)(cid:19)(cid:16)(cid:5) (cid:16)(cid:17)(cid:18)(cid:19)(cid:20) cally.Alogscannerinvokedasanotherapplicationmight
(cid:6)(cid:2)(cid:1)(cid:1)
(cid:2)(cid:5)(cid:4)(cid:3)(cid:3)(cid:2)(cid:1) (cid:17)(cid:4)(cid:17)(cid:21)(cid:14)(cid:22) analyzethelogslatertodetectsuspiciousevents. Using
(cid:5)(cid:2)(cid:1)(cid:1)
(cid:4)(cid:2)(cid:1)(cid:1) P2P for such a streaming workload might seem as a vi-
(cid:3)(cid:2)(cid:1)(cid:1)
|     |     |     |     |     |     |     | ablechoice. | However,ifthescannerisinvokedimmedi- |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ------------------------------------ | --- | --- | --- | --- | --- | --- |
(cid:1)(cid:2)(cid:1)(cid:1)
(cid:7)(cid:3)(cid:4)(cid:8) (cid:6)(cid:9) (cid:3)(cid:10)(cid:11) (cid:5)(cid:4)(cid:11) (cid:10)(cid:6)(cid:9) (cid:7)(cid:3)(cid:4)(cid:9) (cid:3)(cid:14) ately after the files are updated, the contents might still
| (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10)(cid:11)(cid:12)(cid:13)(cid:14) | (cid:7)(cid:5) | (cid:4)(cid:10)(cid:4) | (cid:6)(cid:12)(cid:4) | (cid:10)(cid:12)(cid:7) (cid:13)(cid:6)(cid:10) | (cid:4)(cid:7)(cid:12)(cid:1) | (cid:4)(cid:10)(cid:15)(cid:4) |     |     |     |     |     |     |     |     |
| ------------------------------------------------------------------------------------------------------- | -------------- | ---------------------- | ---------------------- | ----------------------------------------------- | ----------------------------- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10) be in the page cache, thus using P2P would reduce sys-
|           |     |         |                 |     |     |          | tem throughput, |     | as we | also | show | in our experiments |     | in  |
| --------- | --- | ------- | --------------- | --- | --- | -------- | --------------- | --- | ----- | ---- | ---- | ------------------ | --- | --- |
| Figure 1: | The | speedup | of CPU-mediated |     | I/O | over P2P | Section6.       |     |       |      |      |                    |     |     |
forsequentialreads.
|            |           |              |              |         |          |          | 3.2 P2P     | programmingchallenges |            |                 |         |        |           |        |
| ---------- | --------- | ------------ | ------------ | ------- | -------- | -------- | ----------- | --------------------- | ---------- | --------------- | ------- | ------ | --------- | ------ |
| ing access | patterns, |              | sequentially | reading | files    | in large |             |                       |            |                 |         |        |           |        |
|            |           |              |              |         |          |          | P2P is a    | low-level             | mechanism, |                 | exposed |        | directly  | to the |
| chunks.    | Our       | measurements |              | in this | section, | however, |             |                       |            |                 |         |        |           |        |
|            |           |              |              |         |          |          | programmer. | Besides               |            | the performance |         | issues | discussed |        |
showthatP2PisactuallyslowerthanCPU-mediatedI/O
earlier,itintroducesanumberofchallengestoprogram-
foraccesspatternsandapplicationscenariosthathavenot
mers.
| been considered |     | previously. |     | We then | highlight | the key |     |     |     |     |     |     |     |     |
| --------------- | --- | ----------- | --- | ------- | --------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
Non-standardAPI.ThereisnostandardOSAPIforac-
challengesthatP2Pposestoprogrammers,motivatingits
|     |     |     |     |     |     |     | cessing | files via | P2P. | All the | existing | frameworks |     | devi- |
| --- | --- | --- | --- | --- | --- | --- | ------- | --------- | ---- | ------- | -------- | ---------- | --- | ----- |
integrationintotheOSfileI/Ostack.
|     |     |     |     |     |     |     | ate from       | the standard |       | file API,   | e.g., | send()/recv() |         |     |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ------------ | ----- | ----------- | ----- | ------------- | ------- | --- |
|     |     |     |     |     |     |     | streaming-like |              | calls | in Gullfoss |       | [5] and       | NVMMU’s |     |
3.1 P2P inefficiencies move() [4]. Custom APIs require programmers to ex-
|     |     |     |     |     |     |     | plicitly select | the | file | transfer | mechanism, |     | a choice | that |
| --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ---- | -------- | ---------- | --- | -------- | ---- |
Short sequential reads. We compare the performance isnottrivialinmanycases,asweexplainearlier.
of P2P and CPU-mediated I/O for reading file contents Datainconsistency. Updateswrittentoafileviaregular
| into NVIDIA                 |         | GPU (AMD | GPUs           | are                | similar).      | We run |                                       |     |        |     |        |          |          |     |
| --------------------------- | ------- | -------- | -------------- | ------------------ | -------------- | ------ | ------------------------------------- | --- | ------ | --- | ------ | -------- | -------- | --- |
|                             |         |          |                |                    |                |        | FSAPIwillbestoredinthepagecachefirst, |     |        |     |        |          | andmight |     |
| the standard                | TIOtest |          | [16] benchmark |                    | only modifying | it     |                                       |     |        |     |        |          |          |     |
|                             |         |          |                |                    |                |        | remain invisible                      |     | to the | P2P | unless | the file | contents | are |
| totransferdatatoGPUbuffers. |         |          |                | TheCPU-mediatedI/O |                |        |                                       |     |        |     |        |          |          |     |
writtenbacktothedisk.
versionissuespread()intoaCPUbufferfollowedby
|     |     |     |     |     |     |     | Unsupported |     | misaligned | accesses. |     | P2P | requires | both |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ---------- | --------- | --- | --- | -------- | ---- |
cudaMemcpy()totransferthebuffertotheGPU.For
|               |         |                                 |                |            |     |            | the source      | and | destination |        | to be   | aligned       | according  | to     |
| ------------- | ------- | ------------------------------- | -------------- | ---------- | --- | ---------- | --------------- | --- | ----------- | ------ | ------- | ------------- | ---------- | ------ |
| P2P we        | use our | own                             | implementation | described  |     | in detail  |                 |     |             |        |         |               |            |        |
|               |         |                                 |                |            |     |            | device-specific |     | rules       | (p.91, | [9]).   | Specifically, |            | an SSD |
| inSection5.1. |         | ForthehardwaresetupseeSection6. |                |            |     |            |                 |     |             |        |         |               |            |        |
|               |         |                                 |                |            |     |            | data offset     | and | destination |        | address | must          | be aligned | on     |
| Figure        | 1 shows | the                             | relative       | throughput | of  | sequential |                 |     |             |        |         |               |            |        |
theminimumtransfersizesupportedbythedevice(512
| accesses | to a 100MB |     | file. P2P | is more | than | an order of |     |     |     |     |     |     |     |     |
| -------- | ---------- | --- | --------- | ------- | ---- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
bytesonIntelSSDs),otherwisetheI/Orequestfails.
magnitudeslowerthatCPU-mediatedI/Oforveryshort
|                                           |        |          |     |              |     |               | In summary, |                 | as GPUs | find | their    | ways | to accelerat- |        |
| ----------------------------------------- | ------ | -------- | --- | ------------ | --- | ------------- | ----------- | --------------- | ------- | ---- | -------- | ---- | ------------- | ------ |
| reads,andabout3×slowerforlarger32KBreads. |        |          |     |              |     | This          |             |                 |         |      |          |      |               |        |
|                                           |        |          |     |              |     |               | ing complex | data-processing |         |      | systems, | such | as            | Apache |
| is a common                               | access | pattern, |     | found, e.g., | in  | grep utility. |             |                 |         |      |          |      |               |        |
Spark[17],thesimplicity,portability,andtransparentop-
P2Pattainsspeedupsonlyforreadsof512KBandabove.
|     |     |     |     |     |     |     | timizations | offered | by  | OS file | I/O | interfaces | make | such |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ------- | --- | ------- | --- | ---------- | ---- | ---- |
Thisperformancegapisduetotheread-aheadmecha-
|            |               |     |           |              |     |      | interfaces | essential | for | building | efficient |     | and maintain- |     |
| ---------- | ------------- | --- | --------- | ------------ | --- | ---- | ---------- | --------- | --- | -------- | --------- | --- | ------------- | --- |
| nism which | transparently |     | optimizes | CPU-mediated |     | I/O, |            |           |     |          |           |     |               |     |
ableGPU-acceleratedsystems.Theseobservationsguide
| and which | P2P | bypasses | entirely. |     | The | OS asyn- |     |     |     |     |     |     |     |     |
| --------- | --- | -------- | --------- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
usinourgoaltointegrateP2PmechanismintotheOSfile
| chronouslyprefetchesthefileintothepagecache, |     |     |     |     |     | over- |     |     |     |     |     |     |     |     |
| -------------------------------------------- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
systemlayeraswediscussnext.
| lapping    | the reads | from       | the       | disk with | CPU-GPU   | data     |     |     |     |     |     |     |     |     |
| ---------- | --------- | ---------- | --------- | --------- | --------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
| transfers. | The       | prefetcher | gradually |           | increases | the size |     |     |     |     |     |     |     |     |
4 Design
| of the prefetch |     | data requests |     | up to 512KB | (by | default), |     |     |     |     |     |     |     |     |
| --------------- | --- | ------------- | --- | ----------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
achievingmuchhighereffectivebandwidthtoSSDthan
P2P,whichperformsshortreads. Design goals. SPIN aims to integrate P2P into the OS
Complex workloads. P2P is significantly slower than file I/O layer. It uses P2P as a low-level mechanism for
|              |     |        |          |          |            |        | optimizing | file | I/O where | applicable. |     | We  | focus | on the |
| ------------ | --- | ------ | -------- | -------- | ---------- | ------ | ---------- | ---- | --------- | ----------- | --- | --- | ----- | ------ |
| CPU-mediated |     | I/O if | the file | contents | are cached | in the |            |      |           |             |     |     |       |        |
page cache, as is often the case for complex software followingdesigngoals:
systems with multiple cooperating applications. How- • CPU-GPU workloads: efficiently handle complex
ever, since the page cache contents change dynamically scenarios with opportunistic data reuse, where appli-
depending on the workload, a programmer is left with- cationsmaysharefiles,e.g.,inproducer-consumerin-
out a single best choice of file transfer mechanism. For teraction. SPIN should provide standard POSIX file
example, consideracentrallogserverthatreceiveslogs consistencyguaranteesregardlessofthetransfermech-
| fromothermachinesoverthenetworkandstoresthemlo- |     |     |     |     |     |     | anismused. |     |     |     |     |     |     |     |
| ----------------------------------------------- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
USENIX Association 2017 USENIX Annual Technical Conference    169

pread(     f d      ,   b  G u  P f f U e    GPU isalreadyinthecache, using P2P wouldbeslowerthan
r    )
|     |     |     |     |     |     | GPU  | reading the | data | from the | page | cache. | However, |     | if only |
| --- | --- | --- | --- | --- | --- | ---- | ----------- | ---- | -------- | ---- | ------ | -------- | --- | ------- |
buffer
partoftherequestcanbeservedfromthecache,thebest
|     | SPIN  |                  | 1   |          |     |      |              |     |                                  |     |     |     |     |     |
| --- | ----- | ---------------- | --- | -------- | --- | ---- | ------------ | --- | -------------------------------- | --- | --- | --- | --- | --- |
|     | P - R | e a d            |     |          |     |      |              |     |                                  |     |     |     |     |     |
|     |       |                  |     | P-cache  |     | PCIe | waytocombine |     | P2P andcacheaccessesdependsonthe |     |     |     |     |     |
|     | A h   | e a d   P-router |     | checker  |     |      |              |     |                                  |     |     |     |     |     |
policy distribution of the pages in the cache. For example, if
|     |     | 2.a    | 2.b |     |     |            |                 |            |             |         |             |          |         |             |
| --- | --- | ------ | --- | --- | --- | ---------- | --------------- | ---------- | ----------- | ------- | ----------- | -------- | ------- | ----------- |
|     |     | P2PDMA |     |     |     |            | only every      | second     | page        | in a    | 8MB-large   | read     | request | is          |
|     |     |        |     |     |     | refsnart A | c a c h e d , r | e ad i n g | f r o m t h | e p a g | e c a c h e | is 1 6 × | s lo w  | e r t h a n |
VFS
P a g e ca c h e 5.b a s i n g le 2 o f t h e w h o le r e q u e s te d b u f f e r . W e a d d r e s s
|     |     |     |         |       |     |     |     | P P |     |     |     |     |     |     |
| --- | --- | --- | ------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     | 3.a | C P U   | G P U |     | M   |     |     |     |     |     |     |     |     |
P C R A D th e p r o bl e m o f o p t im a l i n t e r l e a v i n g in S e c t i on 4 .3 . 1 .
P2
|     |     |     | 3.b |     |     | P   |            |              |     |     |            |     |           |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------------ | --- | --- | ---------- | --- | --------- | --- |
|     |     |     |     |     |     |     | Read-ahead | integration. |     | A   | read-ahead |     | mechanism | is  |
Current FS API essential for fast sequential accesses (see § 3), but the
5.a
Block best way to integrate it with P2P is not obvious. Tech-
Layer
|     | NVMe |     |     |     |     |     | nically, the | prefetcher |     | never runs | because |     | P2P bypasses |     |
| --- | ---- | --- | --- | --- | --- | --- | ------------ | ---------- | --- | ---------- | ------- | --- | ------------ | --- |
4.b
Driver file the heuristic which identifies a sequential access pat-
|     |     | GPU addr.  | 4.a |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
extraction
|     |     |     |     |     |     |     | tern and | triggers | the read-ahead |     | mechanism. |     | However |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | -------- | -------------- | --- | ---------- | --- | ------- | --- |
NVMe SSD
|     |     |     |     |     |     |     | if we re-enable |     | the prefetcher, |     | where | will | it store | the |
| --- | --- | --- | --- | --- | --- | --- | --------------- | --- | --------------- | --- | ----- | ---- | -------- | --- |
Figure 2: SPIN high-level design and control flow of prefetched contents? One of the benefits of P2P is that
pread(),asexplainedinSection4.2
|     |     |     |     |     |     |     | it does not | pollute | the  | CPU | page cache |          | with the | data |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ------- | ---- | --- | ---------- | -------- | -------- | ---- |
|     |     |     |     |     |     |     | used only   | by the  | GPU. | But | without    | the page | cache    | on   |
theGPU,theread-aheadmechanismwouldhavetostore
| •   | Various | access patterns: |     | enable | high | performance |                |     |         |         |      |        |        |      |
| --- | ------- | ---------------- | --- | ------ | ---- | ----------- | -------------- | --- | ------- | ------- | ---- | ------ | ------ | ---- |
|     |         |                  |     |        |      |             | the prefetched |     | data in | the CPU | page | cache, | losing | this |
across random/sequential access patterns and an unre- advantage. WediscusstheprefetcherinSection4.3.2.
|     | stricted | range of | request | sizes, | from as | little as a few |                               |     |     |     |                  |     |     |     |
| --- | -------- | -------- | ------- | ------ | ------- | --------------- | ----------------------------- | --- | --- | --- | ---------------- | --- | --- | --- |
|     |          |          |         |        |         |                 | PortabilityacrossGPUsoftware. |     |     |     | GPUvendorsexpose |     |     |     |
bytes.
differentAPIsforGPUmanagementanddatatransfersto
| •   | Standard | File API: | support | standard |     | I/O calls like |     |     |     |     |     |     |     |     |
| --- | -------- | --------- | ------- | -------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
andfromGPUmemory,noneofwhichareavailablefor
pwrite()andpread()forportability.
|     |                |     |            |     |              |           | use from   | kernel | space.      | As a | result, | providing | a    | generic |
| --- | -------------- | --- | ---------- | --- | ------------ | --------- | ---------- | ------ | ----------- | ---- | ------- | --------- | ---- | ------- |
| •   | Compatibility: | be  | compatible |     | with virtual | block de- |            |        |             |      |         |           |      |         |
|     |                |     |            |     |              |           | OS service | which  | is agnostic |      | to the  | GPU       | type | and its |
vicessuchasLVMandsoftwareRAIDs,aswellaswith
softwarestackischallenging.
differentGPUsandSSDs.
4.2 Overview
4.1 Designconsiderations
|     |     |     |     |     |     |     | Figure 2 | shows | the main | design | components. |     | SPIN | is  |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----- | -------- | ------ | ----------- | --- | ---- | --- |
PagecacheisthecornerstoneoffileI/OinCPUsystems, positionedontopoftheVirtualFileSystem(VFS)layer.
butitsintegrationwithP2Praisesanumberofquestions.
WeillustratetheinteractionoftheSPINcomponentson
Page cache in GPU memory? One way to combine the example of pread (). The user allocates the desti-
| cachingwith |     | P2P istopartitionthepagecachebetween |           |     |     |               |                   |     |                           |     |            |     |             |     |
| ----------- | --- | ------------------------------------ | --------- | --- | --- | ------------- | ----------------- | --- | ------------------------- | --- | ---------- | --- | ----------- | --- |
|             |     |                                      |           |     |     |               | nation buffer     | in  | GPU memory                |     | and passes |     | the pointer | to  |
| the         | CPU | and GPU                              | memories, | and | use | each to cache |                   |     |                           |     |            |     |             |     |
|             |     |                                      |           |     |     |               | thebuffertopread. |     | TomakeGPUmemorybuffersac- |     |            |     |             |     |
file accesses from the respective device. In fact, GPUfs cessible to I/O calls, the user maps the buffers into the
| demonstrated |     | the benefits |     | of hosting | a page | cache for |     |     |     |     |     |     |     |     |
| ------------ | --- | ------------ | --- | ---------- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
CPUprocessaddressspaceusingexistingGPUvendor-
GPU tasks in GPU memory [15, 18]. Unfortunately, specific tools (§ 5). We note that using CPU-mapped
modern GPUs still lack critical features to enable OS- GPUbuffersinI/OcallsispossiblewithoutSPIN,how-
| controlled |     | GPU-resident | page | cache. | In  | particular, they |     |     |     |     |     |     |     |     |
| ---------- | --- | ------------ | ---- | ------ | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- |
everP2Pisnotinvoked.
donotsupportanonymousmemorythatdoesnotbelong The SPIN core is implemented in P-router. P-router
| to  | any CPU | process, | neither | do they | provide | the means |                          |     |     |     |                        |     |     |     |
| --- | ------- | -------- | ------- | ------- | ------- | --------- | ------------------------ | --- | --- | --- | ---------------------- | --- | --- | --- |
|     |         |          |         |         |         |           | inspectseveryI/Orequest( |     |     | 1   | intheFigure)anddetects |     |     |     |
for the OS to manage GPU memory mappings. As a the requests that operate on GPU memory buffers and
result, GPUfs, for example, maintains a per-application are amenable to P2P. P-router invokes the P-readahead
pagecache,whichdisappearswhenanapplicationtermi-
|     |     |     |     |     |     |     | mechanism, | which | identifies |     | sequential | access |     | pattern |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ----- | ---------- | --- | ---------- | ------ | --- | ------- |
nates. Workarounds, such as running a daemon process andprefetchesfilecontentsintoaGPUread-aheadpar-
inuserspacethatownstheGPUpagecache,areinsecure
tition(GPURAintheFigure)oftheCPUpagecache,as
becausetheyexposethewholepagecachetoallrunning describedin§4.3.2).ItalsocheckswithP-cachewhether
GPUtasks. Weconcludethatmaintainingpagecachein the request can be served from the page cache, and cre-
GPUmemoryiscurrentlynotpractical.
atesanI/OscheduletointerleaveP2Pandpagecacheac-
Reusing file contents from the CPU page cache. P2P cesses,asdiscussedin§4.3.1. Finally,itgeneratesVFS
transfersbypasstheCPUpagecache. Butifthecontent I/Orequeststhatareservedbyacombinationofthepage
170    2017 USENIX Annual Technical Conference USENIX Association

cache 2.b andP2P 2.a. ToinvokeP2PviadirectdiskI/O every I/O request. Instead, we simplify the problem to
interface,P-routeremploysanaddresstunnelingmecha- applyasimplegreedyheuristicasfollows.
nism describedin§5.1. We start by assuming that the P2P transfer time,
3.a
|     |     |     |     |     |     | T (s), | is a piece-wise |     | linear | function | of  | the | transfer |
| --- | --- | --- | --- | --- | --- | ------ | --------------- | --- | ------ | -------- | --- | --- | -------- |
p2p
|     |     |     |     |     |     | sizesoftheformgiveninEq1. |     |     |     | Intuitively,forrequests |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | ----------------------- | --- | --- | --- |
4.3 Integrationwithpagecache
|     |     |     |     |     |     | smaller | than S | cutoff , | the device |     | bandwidth | is not | satu- |
| --- | --- | --- | --- | --- | --- | ------- | ------ | -------- | ---------- | --- | --------- | ------ | ----- |
Wedealwiththreeaspects:interleavingpagecachereads rated,thusthetransfertimeisconstantandcappedbythe
|           |             |      |             |     |              | device’s     | invocation                           | overhead |     | C   | . For requests |     | larger |
| --------- | ----------- | ---- | ----------- | --- | ------------ | ------------ | ------------------------------------ | -------- | --- | --- | -------------- | --- | ------ |
| with P2P, | integration | with | read-ahead, | and | data consis- |              |                                      |          |     | p2p |                |     |        |
| tency.    |             |      |             |     |              | thanS cutoff | ,thedeviceoperatesatmaximumbandwidth |          |     |     |                |     |        |
BW . Theseassumptionsareconsistentwiththearchi-
p2p
|     |     |     |     |     |     | tectural | model | of modern | SSDs | [19]. | Page | cache | trans- |
| --- | --- | --- | --- | --- | --- | -------- | ----- | --------- | ---- | ----- | ---- | ----- | ------ |
4.3.1 CombiningpagecachewithP2P
|     |     |     |     |     |     | fers, in | turn, always |     | achieve | maximum | bandwidth |     | thus |
| --- | --- | --- | --- | --- | --- | -------- | ------------ | --- | ------- | ------- | --------- | --- | ---- |
s
Optimal scheduling of page cache transfers. P-cache thetransfertimeforsizesisT (s)= .
|                                                   |                                        |          |             |          |        |       |      |         |     | pc       | BW    |        |     |
| ------------------------------------------------- | -------------------------------------- | -------- | ----------- | -------- | ------ | ----- | ---- | ------- | --- | -------- | ----- | ------ | --- |
| retrievestheCPUpagecacheresidencemapforagiven     |                                        |          |             |          |        |       |      |         |     |          | pc    |        |     |
| readaccess.                                       | Iftheentirerequestedregioniscached,the |          |             |          |        |       |      |        |     |          |       |        |     |
|                                                   |                                        |          |             |          |        |       |      |  C p2p |     |          | ifs<S | cutoff |     |
| request                                           | is served                              | from the | page cache. | However, | if the |       |      |         |     |          |       |        |     |
|                                                   |                                        |          |             |          |        | T p2p | (s)= |         | s−  | S cutoff |       |        | (1) |
| cachecontainsonlypartoftherequesteddata,thesystem |                                        |          |             |          |        |       |      | C       | +   |          | ifs≥S |        |     |
|                                                   |                                        |          |             |          |        |       |      |  p2p   | BW  |          |       | cutoff |     |
p2p
combinesbothP2Pandpagecachetransfers,bybreaking
theoriginalrequestintosub-requestseachservedviaits Thegreedyheuristicworksasfollows. Foreachthree
|     |     |     |     |     |     | consecutive | data | ranges | a,b,c, | where | b is | in the | page |
| --- | --- | --- | --- | --- | --- | ----------- | ---- | ------ | ------ | ----- | ---- | ------ | ---- |
ownmethod.
|         |          |              |     |         |            | cache, if | |a|+|b| | <   | S      | , always | choose | P2P | for b |
| ------- | -------- | ------------ | --- | ------- | ---------- | --------- | ------- | --- | ------ | -------- | ------ | --- | ----- |
| Finding | the best | interleaving | of  | P2P and | page cache |           |         |     | cutoff |          |        |     |       |
accesses is a challenge. On the one hand, reading from (where|x|isthesizeofx). Otherwise,choose P2P forb
|     |     |     |     |     |     | ifT (|a|+|b|+|c|)<T |     |     |     | (|a|)+T | (|b|)+T |     | (|c|). |
| --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | ------- | ------- | --- | ------ |
the page cache is faster than reading from the SSD. On p2p p2p pc p2p
theotherhand,interleavingP2Pandpagecachereadsat In other words, P2P for b is preferable if the benefits of
readingbfromthepagecachearesmallerthantheover-
| a fine granularity |     | results in | poor performance, |     | because |     |     |     |     |     |     |     |     |
| ------------------ | --- | ---------- | ----------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
headoftransferringcinaseparateP2Ptransaction.
shortI/OrequeststotheSSDarelessefficientthanlarger
ones,andbecauseoftheP2Pinvocationoverhead. Thus, Parameter fitting. We experimentally measure the
SPIN needs to determine the best interleaving schedule transfer times for different request sizes for Intel P3700
foreachI/Orequest. SSD,andfittheparametersofthetransfertimefunction
|               |     |         |             |              |      | in Eq 1 | using | regression. |     | The function | fits | very | well, |
| ------------- | --- | ------- | ----------- | ------------ | ---- | ------- | ----- | ----------- | --- | ------------ | ---- | ---- | ----- |
| The following |     | example | illustrates | the problem. | Con- |         |       |             |     |              |      |      |       |
sider a request of 20KB (5 pages) with its second, and with the coefficient of determination of over 0.99. We
fourthpagesinthepagecache. Then, thereare3possi- find S =512KB and C =584µsec, which cor-
|     |     |     |     |     |     | cutoff |     |     |     | p2p |     |     |     |
| --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
bleschedules: three P2P transfersof4KBandtwo4KB respondstothetimefortransferring249pagesfromthe
transfers from page cache, a single P2P of 20KB of the page cache. Thus, for two consecutive data ranges b,c
|              |     |               |     |         |            | where b | is in | the page | cache | and | c is not, | b will | be al- |
| ------------ | --- | ------------- | --- | ------- | ---------- | ------- | ----- | -------- | ----- | --- | --------- | ------ | ------ |
| whole range, | and | a combination | of  | P2P and | page cache |         |       |          |       |     |           |        |        |
transfersforthesecondandthefourthpage,resultingin waystransferredviaP2Pif|b|<249pages.
| two P2P | transfers | of 4KB | and 12KB. | The choice | of the | Evaluation. |     |       |             |     |       |         |      |
| ------- | --------- | ------ | --------- | ---------- | ------ | ----------- | --- | ----- | ----------- | --- | ----- | ------- | ---- |
|         |           |        |           |            |        |             | We  | build | a simulator |     | which | quickly | com- |
best schedule depends on the actual P2P throughput for putes the transfer cost of an I/O request, given transfer
each transfer size, as well as on the throughput of the schedule,usingthetransfertimesmeasuredonrealhard-
page cache reads. The scheduling decision for different ware. Wevalidatethesimulatorexperimentallyon5,000
pagesarenotindependent,however,becauseSSDtrans- I/Orequests,andfindthatitserroris1.6%onaverage.
fer time is a non-linear function of the request size for We use the simulator to evaluate the quality of the
smallerreads[19]. greedy heuristic, by comparing its results with the op-
To summarize, the scheduling problem at hand is as timaltransferschedulesobtainedbytheexactalgorithm.
follows: for a given I/O request, find all the constituent We evaluate the schedules on 200,000 random vectors,
continuousrangesofpageswhichcanbeservedfromthe eachrepresentingan8MBdatatransferhavingdifferent
page cache. For every such a range, decide whether to page cache residency patterns. We find that the transfer
transfer it from the page cache or via P2P, effectively timeofthegreedyschedulesiswithin98.9%oftheopti-
merging it with the two flanking segments into a single malscheduleonaverage.
P2Ptransfer,suchthatthetotaltransfertimeofthewhole Generalization to other SSDs. We believe that our
requestisminimized. heuristicreflectsthegeneralSSDperformancetrendsand
Greedy heuristic. This problem can be solved exactly canbeusedwithotherSSDs. Specifically, architectural
inpolynomialtimeviadynamicprogramming, however propertiesofSSDs,suchasmulti-channel/multi-way,en-
this is too slow since the solution has to be found for able a high degree of parallelism for relatively large re-
USENIX Association 2017 USENIX Annual Technical Conference    171

quests. These requests are often striped across domains transfer, and explicitly performs a write back from the
| and exploit | the internal |     | parallelism | SSDs | offer | [19, 20]. | pagecachetotheSSD. |     |     |     |     |     |     |
| ----------- | ------------ | --- | ----------- | ---- | ----- | --------- | ------------------ | --- | --- | --- | --- | --- | --- |
Therefore,ourmodelwhichpredictshigherperformance
forlargerrequestsisconsistentwiththeseproperties.We
|                                     |               |      |            |     |              |       | 5 Implementation   |         |           |        |          |                |        |
| ----------------------------------- | ------------- | ---- | ---------- | --- | ------------ | ----- | ------------------ | ------- | --------- | ------ | -------- | -------------- | ------ |
| provide                             | a calibration | tool | to perform | the | measurements |       |                    |         |           |        |          |                |        |
| andregressiontoautomaticallyadjustS |               |      |            |     | cutoff andC  | p2p . |                    |         |           |        |          |                |        |
|                                     |               |      |            |     |              |       | Our implementation |         | leverages |        | existing | kernel         | mecha- |
|                                     |               |      |            |     |              |       | nisms to           | achieve | SPIN’s    | design | goals.   | We encapsulate |        |
4.3.2 Read-aheadforGPUaccesses
|     |     |     |     |     |     |     | all new | functionality | in  | a kernel | module | SPINDRV, | a   |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------------- | --- | -------- | ------ | -------- | --- |
slightlymodifiedgenericNVMedriver,andalightweight
| The OS         | read-ahead | is        | not activated |     | for accesses | via        |               |         |               |     |            |               |     |
| -------------- | ---------- | --------- | ------------- | --- | ------------ | ---------- | ------------- | ------- | ------------- | --- | ---------- | ------------- | --- |
|                |            |           |               |     |              |            | user space    | library | LIBSPIN.      |     | Thus,      | SPIN requires | no  |
| P2P, therefore | we         | introduce | P-readahead.  |     | It           | stores the |               |         |               |     |            |               |     |
|                |            |           |               |     |              |            | modifications |         | to the kernel | and | is readily | deployable    | on  |
| prefetched     | data in    | a special | partition     | in  | the CPU      | page       |               |         |               |     |            |               |     |
existingsystems.
cacheasweexplainnext.
|                |            |        |         |             |             |     | libSPIN.   | is a    | shim that | interposes | on    | standard | file I/O |
| -------------- | ---------- | ------ | ------- | ----------- | ----------- | --- | ---------- | ------- | --------- | ---------- | ----- | -------- | -------- |
| GPU read-ahead |            | cache. | To      | avoid cache | pollution   | by  |            |         |           |            |       |          |          |
|                |            |        |         |             |             |     | calls. The | library | is loaded | via        | an LD | PRELOAD  | envi-    |
| the contents   | prefetched |        | as part | of the      | read-ahead, | we  |            |         |           |            |       |          |          |
ronmentvariable.ApplicationsthatdonotloadLIBSPIN
| add a lightweight |     | management |     | mechanism, | GPU | read- |     |     |     |     |     |     |     |
| ----------------- | --- | ---------- | --- | ---------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
maysharefileswiththosethatdo.
| ahead cache, | RA    | cache.     | A page | is assigned | to  | the RA    |             |      |       |     |      |           |        |
| ------------ | ----- | ---------- | ------ | ----------- | --- | --------- | ----------- | ---- | ----- | --- | ---- | --------- | ------ |
|              |       |            |        |             |     |           | Interaction | with | GPUs. |     | SPIN | leverages | exist- |
| cache when   | it is | first used | by     | P-readahead | to  | store the |             |      |       |     |      |           |        |
prefetcheddata.ThepagesintheRAcachebelongtothe ing tools for mapping GPU memory into the CPU
|         |            |     |         |       |            |      | address | space. | In  | particular, | we  | use | OpenCL’s |
| ------- | ---------- | --- | ------- | ----- | ---------- | ---- | ------- | ------ | --- | ----------- | --- | --- | -------- |
| OS page | cache, and | are | subject | to OS | page cache | man- |         |        |     |             |     |     |          |
agementpolicies. Inaddition,theRAcacheforcesevic- CL MEM USE PERSISTENT MEM AMD extension
tion of its pages once its total size exceeds a predefined from AMD, and gdrcopy module from NVIDIA.
UsingCPU-mappedGPUmemoryforI/Oenablesporta-
| threshold. | IfapageislateraccessedbyaCPUprogram, |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
the page is removed from the RA cache, but remains in bility across GPU vendors, interaction with GPUs from
|        |             |     |           |           |      |        | kernel space, |     | and independence |     | from | GPU | software |
| ------ | ----------- | --- | --------- | --------- | ---- | ------ | ------------- | --- | ---------------- | --- | ---- | --- | -------- |
| the OS | page cache. | As  | a result, | the pages | used | exclu- |               |     |                  |     |      |     |          |
interfaces.
| sively to | store the | data | prefetched | for | GPU I/O | do not |     |     |     |     |     |     |     |
| --------- | --------- | ---- | ---------- | --- | ------- | ------ | --- | --- | --- | --- | --- | --- | --- |
pollutetheOSpagecache. SPINdrv. The driver implements the SPIN design in-
Read-ahead mechanism. P-readahead watches for se- cluding the page cache and read-ahead as described in
|          |                |     |               |     |          |          | § 4. In | addition, | it introduces |     | a new | address | tunneling |
| -------- | -------------- | --- | ------------- | --- | -------- | -------- | ------- | --------- | ------------- | --- | ----- | ------- | --------- |
| quential | access pattern |     | by monitoring |     | the last | accessed |         |           |               |     |       |         |           |
offset in each file, similarly to the CPU read-ahead mechanism to enable P2P via direct disk I/O which we
| heuristic.Forsequentialaccesses,thedataisreadintothe |     |     |     |     |     |     | discussnext. |     |     |     |     |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- |
GPURAcacheviaCPUVFScalls,effectivelyengaging
theoriginalOSread-aheadmechanismredirectedtostore
|     |     |     |     |     |     |     | 5.1 P2P | viadirectdiskI/O |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | ---------------- | --- | --- | --- | --- | --- |
dataintheGPURApagecache.Asaresult,P-readahead
respects the standard fadvise calls, and does not re- OurimplementationofP2Ptakesadvantageofthedirect
quire new management interfaces. We also modify the diskI/Ofileinterface,addingaspecialmechanismtoen-
defaultbehaviorofP-readaheadinresponsetofadvise ableitsusewithGPUmemorybuffers.
policies,e.g.,disablingitforPOSIX FADV RANDOM. DirectdiskI/OandP2Ppursuethesamegoals:theyal-
Forsequentialrequeststhatcannotbeservedfromthe lowdirectaccesstostoragedeviceswhilebypassingthe
pagecacheandexceedacertainthreshold,P-routerdeac- OS page cache. Using direct disk I/O mechanisms for
tivates P-readahead and switches to P2P. The threshold P2Phasanumberofadvantages. First,thefileI/Ostack
equals to the maximum size of the OS-configured read- performsthestandardfileoffset-to-LBAmappingwhich
aheadwindow(512KBbydefault),whichdeterminesthe is compatible with virtual block layers, e.g., software
maximum size of SSD requests generated by the read- RAID.Second,themechanismalreadyimplementsvari-
ahead. Using P2P for requests exceeding the threshold ousoptimizations,e.g. usesmultiplesubmissionqueues
resultsinlargerSSDrequestsandhigherthroughput. and merges/splits block I/O requests. Last, it already
|     |     |     |     |     |     |     | handles | the data | consistency | by  | writing | back | dirty page |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | ----------- | --- | ------- | ---- | ---------- |
cachepagesintherangeofitsI/Orequest.
4.3.3 Dataconsistency
Unfortunately,directdiskI/Orequirestheuserbuffers
Combiningfileaccessesfromthepagecachewithdirect toresideinCPUphysicalmemory,andcannotaccommo-
accesses to a storage device raises an obvious data con- date CPU-mapped GPU buffers. This is because it pins
sistencyproblem,sincethedatainthepagecachemight userbuffersinmemorytoperformDMAto/fromthestor-
notbesynchronizedwiththecontentontheSSD.There- age device, and fails to pin GPU buffers. This problem
fore, SPIN detects dirty pages in the range of the P2P hasnoeasysolution,aswediscussbelow(§5.2).
172    2017 USENIX Annual Technical Conference USENIX Association

|     |     |     | GPU  |     |     |     | the block | layer | may reorder |     | the requests | and | split | them |
| --- | --- | --- | ---- | --- | --- | --- | --------- | ----- | ----------- | --- | ------------ | --- | ----- | ---- |
pread(     f d     ,    b  u  f f  e  r  )
intosmallerchunks.
| SPIN LIb |     |     |        |      |     |     | Multiplethreadsinthesameprocessmayusethesame |                |     |     |               |     |         |     |
| -------- | --- | --- | ------ | ---- | --- | --- | -------------------------------------------- | -------------- | --- | --- | ------------- | --- | ------- | --- |
|          |     |     |        |      |     |     | phony buffer                                 | simultaneously |     |     | in a lockless |     | manner. | One |
| SPIN     |     |     |        | GPU  |     |     |                                              |                |     |     |               |     |         |     |
| Driver   |     |     | buffer |      |     |     | threadconsumesonly16bytesperaGPUaddressina4K |                |     |     |               |     |         |     |
page,thereforeasinglephonybuffermayaccommodate
|     |     | Phony |     |     |     |     | upto256concurrentrequestsfromdifferentthreads. |     |     |     |     |     |     |     |
| --- | --- | ----- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
Buffer
TheGPUread-aheadcacheisimplementedasalinked
Linux File I/O stack listthatreferences512pages(tunable),locatedintheOS
|     |     |     |     |     |     |     | page cache. | The | eviction | is  | policy | is LRU. | Pages | ac- |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | -------- | --- | ------ | ------- | ----- | --- |
Translation
cessedbyaCPUprogramaresimplyremovedfromthe
NVMe SSD
list,andarenotevictedfromtheOSpagecacheitself.
GPU
buffer
|     |     | Phony  |     |     |     |     | Interaction                                     | with | generic | NVMe  |      | driver. | The  | phony |
| --- | --- | ------ | --- | --- | --- | --- | ----------------------------------------------- | ---- | ------- | ----- | ---- | ------- | ---- | ----- |
|     |     | Buffer |     |     |     |     | buffer’spagesaremarkedbysettinganunused(foruser |      |         |       |      |         |      |       |
|     |     |        |     |     |     |     | mode) arch                                      | 1    | flag in | their | page | struct. | This | flag  |
Figure3: AddresstunnelingfordirectdiskI/OwithGPU is used by the driver to differentiate P2P requests from
buffers.
regularpagesandextracttheGPUaddresses.
|     |     |     |     |     |     |     | Implementationcomplexity. |     |     |     | SPINDRVisimplemented |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | -------------------- | --- | --- | --- |
in700LOCandLIBSPINjust30LOC.Wemodified10
| Address | tunneling. | To  | overcome | this | limitation | with- |                                        |     |     |     |     |     |     |       |
| ------- | ---------- | --- | -------- | ---- | ---------- | ----- | -------------------------------------- | --- | --- | --- | --- | --- | --- | ----- |
|         |            |     |          |      |            |       | LOCintheLinuxgenericNVMedrivertodetect |     |     |     |     |     |     | phony |
outmajormodificationstotheLinuxkernel,wedesigna
buffersandextractrespectiveGPUaddresses.
simplemechanismthatwecalladdresstunneling,which
deliverstheGPUaddressthroughunmodifiedVFSstack
| andblocklayersdowntothegenericNVMedriver. |     |     |     |                    |     |     | 5.2 Limitations |           |     |         |     |     |        |      |
| ----------------------------------------- | --- | --- | --- | ------------------ | --- | --- | --------------- | --------- | --- | ------- | --- | --- | ------ | ---- |
| Figure3explainsthebasicidea.              |     |     |     | Weallocateaspecial |     |     |                 |           |     |         |     |     |        |      |
|                                           |     |     |     |                    |     |     | Supporting      | pwrite(). |     | Mapping |     | GPU | memory | into |
user-spacephonybufferintheCPU,whichisusedasan
|          |         |            |     |          |           |        | the process’s | address        |     | space      | is a recent | capability |               | that is |
| -------- | ------- | ---------- | --- | -------- | --------- | ------ | ------------- | -------------- | --- | ---------- | ----------- | ---------- | ------------- | ------- |
| envelope | for the | GPU buffer |     | address. | The phony | buffer |               |                |     |            |             |            |               |         |
|          |         |            |     |          |           |        | not yet       | well supported |     | in current | systems.    |            | Specifically, |         |
isthenpassedtoaVFSfileI/Ocall,insteadoftheorigi-
|               |     |                                      |     |     |     |     | CPU reads    | from | that      | memory | mapping | are | about  | two-  |
| ------------- | --- | ------------------------------------ | --- | --- | --- | --- | ------------ | ---- | --------- | ------ | ------- | --- | ------ | ----- |
| nalGPUbuffer. |     | Therefore,itsuccessfullyundergoesall |     |     |     |     |              |      |           |        |         |     |        |       |
|               |     |                                      |     |     |     |     | three orders | of   | magnitude | slower | than    | CPU | writes | [21], |
thetranslationandpinningprocesswhilepassingthrough
|                    |     |                                |      |              |         |     | i.e., about        | 30MB/s | and        | 70MB/s | for   | NVIDIA  | and  | AMD  |
| ------------------ | --- | ------------------------------ | ---- | ------------ | ------- | --- | ------------------ | ------ | ---------- | ------ | ----- | ------- | ---- | ---- |
| intermediate       | I/O | layers.                        | When | the envelope | reaches | the |                    |        |            |        |       |         |      |      |
|                    |     |                                |      |              |         |     | GPUs respectively. |        | Therefore, |        | while | reading | data | from |
| genericNVMedriver, |     | thedriverretrievestheaddressof |      |              |         |     |                    |        |            |        |       |         |      |      |
thepagecacheintotheGPUisfast,writingfilesfromthe
theGPUbufferandusesthisaddresstoperformP2P.
GPUintothepagecache–whichmightbebeneficiale.g.,
| Security                        | of address | tunneling. |     | One | potential       | problem |               |              |     |            |        |              |     |        |
| ------------------------------- | ---------- | ---------- | --- | --- | --------------- | ------- | ------------- | ------------ | --- | ---------- | ------ | ------------ | --- | ------ |
|                                 |            |            |     |     |                 |         | for buffering | writes       | in  | CPU        | memory | – results    | in  | severe |
| withthetunnelingmechanismisthat |            |            |     |     | phonybuffersare |         |               |              |     |            |        |              |     |        |
|                                 |            |            |     |     |                 |         | performance   | degradation. |     | Therefore, |        | we currently |     | con-   |
allocatedintheuser-spacememory(otherwisetheycan-
|     |     |     |     |     |     |     | figure SPIN | to  | perform | writes | from | GPU | memory | only |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ------- | ------ | ---- | --- | ------ | ---- |
notbepassedtoVFScalls),hencetheyareaccessibleto
viaP2P,whiletakingcareofdataconsistency.
| user-space | programs | and | can | be overwritten |     | by an ad- |     |     |     |     |     |     |     |     |
| ---------- | -------- | --- | --- | -------------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
ChangingLinuxtonativelysupportGPUbuffers.The
| versary                         | to potentially | hold         | any       | physical      | CPU           | address,  |                                   |            |           |           |            |               |         |     |
| ------------------------------- | -------------- | ------------ | --------- | ------------- | ------------- | --------- | --------------------------------- | ---------- | --------- | --------- | ---------- | ------------- | ------- | --- |
|                                 |                |              |           |               |               |           | address                           | tunneling  | mechanism |           | sidesteps  | the           | problem | of  |
| thereby                         | enabling       | DMA          | attacks.  | SPIN,         | therefore,    | does      |                                   |            |           |           |            |               |         |     |
|                                 |                |              |           |               |               |           | passing                           | GPU        | buffers   | to direct | disk       | I/O,          | but why | not |
| notstoretheactualGPUaddressesin |                |              |           |               | phonybuffers. | In-       |                                   |            |           |           |            |               |         |     |
|                                 |                |              |           |               |               |           | changing                          | the kernel | in        | the first | place?     | Technically,  |         | the |
| stead, it                       | first creates  | a            | temporary | pseudo-random |               | token     |                                   |            |           |           |            |               |         |     |
|                                 |                |              |           |               |               |           | problemoriginatesintheuseofstruct |            |           |           |            | pagewhichis   |         |     |
| associated                      | with the       | current      | request,  | and           | uses          | the token |                                   |            |           |           |            |               |         |     |
|                                 |                |              |           |               |               |           | not available                     | for        | I/O       | re-mapped | addresses  |               | such as | GPU |
| as the key                      | to the         | kernel-space |           | translation   | table         | with the  |                                   |            |           |           |            |               |         |     |
|                                 |                |              |           |               |               |           | memory                            | buffers.   | However,  |           | thisstruct | is requiredby |         | the |
actualGPUaddresses.
|                |     |          |     |       |        |           | blocklayer. | Attemptshavebeenmadetosolvetheprob- |     |       |          |         |          |     |
| -------------- | --- | -------- | --- | ----- | ------ | --------- | ----------- | ----------------------------------- | --- | ----- | -------- | ------- | -------- | --- |
| Implementation |     | details. | The | phony | buffer | is a user |             |                                     |     |       |          |         |          |     |
|                |     |          |     |       |        |           | lem in a    | systematic                          | way | [22], | yet they | require | touching |     |
spaceCPUmemorybufferallocatedonceduringthepro-
over100filesofkernelcode.Wethereforechooseamore
| cess invocation | when | LIBSPIN |     | is loaded. | The | buffer is |     |     |     |     |     |     |     |     |
| --------------- | ---- | ------- | --- | ---------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
conservativesolution.
| pinnedinmemoryandregisteredwiththeSPINDRV. |     |     |     |     |     | Its |     |     |     |     |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
sizeremainsconstant(currently4MB)throughouttheex-
| ecution.SinceanI/Orequestmustfitinthephonybuffer, |          |        |          |     |            |          | 6 Evaluation |     |     |     |     |     |     |     |
| ------------------------------------------------- | -------- | ------ | -------- | --- | ---------- | -------- | ------------ | --- | --- | --- | --- | --- | --- | --- |
| the I/O                                           | requests | larger | than 4MB | are | split into | multiple |              |     |     |     |     |     |     |     |
requests. Eachmemorypageofthephonybufferisused We evaluate SPIN on two hardware systems (Table 1).
tostoretheaddressofonepageintheGPUbuffer,since WedisableHyperThreadingandconfigurethefrequency
USENIX Association 2017 USENIX Annual Technical Conference    173

NvidiaTeslaK40c 2×IntelXeonE5-2620v2, We report the results for the AMD GPU, and discuss
IntelC602Chipset,64GBDDR4,1NVMeSSD
theperformanceoftheNVIDIAGPUinthetext.
| AMDRadeonR9Fury |     | IntelCorei7-5930K, |     |     |     |     |     |     |     |     |     |     |     |
| --------------- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
IntelX99Chipset,24GBDDR4,2NVMeSSDs RandomReads. Inthisexperimenteachworkerthread
reads500blocksatrandomoffsetsfroma50GBthread-
|         |                      |     |                      |     |     |     | private file. | Figure | 4a  | shows the | results. | Note | that the |
| ------- | -------------------- | --- | -------------------- | --- | --- | --- | ------------- | ------ | --- | --------- | -------- | ---- | -------- |
| Table1: | Evaluationplatforms. |     | BothuseoneortwoIntel |     |     |     |               |        |     |           |          |      |          |
dropsintherelativethroughputonthegraphdonotimply
P3700800GBNVMeSSD
|         |                      |      |          |               |     |            | lower absolute | throughput, |        | rather     | they           | mean | slowdown |
| ------- | -------------------- | ---- | -------- | ------------- | --- | ---------- | -------------- | ----------- | ------ | ---------- | -------------- | ---- | -------- |
|         |                      |      |          |               |     |            | compared       | to SPIN     | in the | respective | configuration. |      | The      |
| ClWrite | Regular              | read | into the | CPU, followed | by  | a blocking |                |             |        |            |                |      |          |
|         |                      |      |          |               |     |            | results for    | a single    | CPU    | thread     | are similar    | and  | omitted  |
|         | clEnqueueWriteBuffer |      |          | / cudaMemcopy |     | call to    |                |             |        |            |                |      |          |
theGPU.
duespacelimitations.
| ClWrite+D | SameasClWritebutwithbypassingtheCPUpagecachevia |     |     |     |     |     |      |             |         |     |         |         |        |
| --------- | ----------------------------------------------- | --- | --- | --- | --- | --- | ---- | ----------- | ------- | --- | ------- | ------- | ------ |
|           |                                                 |     |     |     |     |     | SPIN | performance | matches |     | the one | of P2P, | adding |
ODIRECTflag.
| P2P       | SPIN’simplementationofP2Pthatbypassesthepagecache. |     |     |     |     |     |                 |     |                              |     |     |     |     |
| --------- | -------------------------------------------------- | --- | --- | --- | --- | --- | --------------- | --- | ---------------------------- | --- | --- | --- | --- |
|           |                                                    |     |     |     |     |     | only1%overhead. |     | Forblocksabove1MBtheoverhead |     |     |     |     |
| pread+GPU | preadintotheGPUmemorythatismappedtothepro-         |     |     |     |     |     |                 |     |                              |     |     |     |     |
cess’saddressspace.UnlikeSPIN,pread()+GPUalways of additional memory copy in CPU memory gets amor-
usesthepagecache.Notevaluatedinpriorworks.
tizedforalltheimplementationsbutClWrite,becauseof
itssecondextracopyinthetemporaryCPUbuffer.
| Table2: | Transfermechanismsusedforevaluation. |     |     |     |     |     |            |        |     |            |        |      |        |
| ------- | ------------------------------------ | --- | --- | --- | --- | --- | ---------- | ------ | --- | ---------- | ------ | ---- | ------ |
|         |                                      |     |     |     |     |     | Sequential | reads. | For | sequential | reads, | each | worker |
threadinTIOtestreadsanentirefileof100MB.Figure4b
governor to high performance to reduce overall system shows that SPIN tracks the best performing method for
noise. Both machines run Ubuntu 15.04 with and un- thespecificblocksize,switchingfrompagecachetoP2P
taintedLinuxkernel3.19.0-47andext4onSSD.Weuse at512KBasexplainedinSection4.3.2. Weobservethat
CUDA7.5forNVIDIAandOpenCL2.0forAMD. forblockssmallerthan4KSPINexperienceshigherrel-
ativeoverheadofupto10%becauseitservesthemfrom
| Methodology. |     | We run each | experiment |     | 11 times, | omit |     |     |     |     |     |     |     |
| ------------ | --- | ----------- | ---------- | --- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- |
the first result as a warmup, and report the average of the page cache. The overhead is amortized for larger
reads,however.
| the last | 10 runs. | We explicitly |     | flush the | contents | of the |     |     |     |     |     |     |     |
| -------- | -------- | ------------- | --- | --------- | -------- | ------ | --- | --- | --- | --- | --- | --- | --- |
pagecachebeforeeachrun(unlessstatedotherwise).We Sequential/random writes. For the sequential writes,
pwrite
observe the standard deviation below 1% across all the each worker thread writes a 100MB file. The
experimentsanddonotreportitinthefigures. +GPUmechanismisdramaticallyslowerthanP2P,aswe
|                             |     |     |     |                   |     |     | explain | in Section | 5.2, | therefore | SPIN | always | performs |
| --------------------------- | --- | --- | --- | ----------------- | --- | --- | ------- | ---------- | ---- | --------- | ---- | ------ | -------- |
| Alternativetransfermethods. |     |     |     | WecompareSPINwith |     |     |         |            |      |           |      |        |          |
several different implementations described in Table 2. alignedwritesviaP2P.Randomwritesperformsimilarly.
Duetothelackofspace,thefigureisomitted.
| We note | that the | implementation |     | where | pread | () is in- |     |     |     |     |     |     |     |
| ------- | -------- | -------------- | --- | ----- | ----- | --------- | --- | --- | --- | --- | --- | --- | --- |
voked with the CPU-mapped GPU buffer (last row) has Performance on NVIDIA and AMD GPUs. SPIN
notbeenevaluatedinpriorworks. achieves 5-10% higher throughput on AMD R9 GPU
|                              |     |     |     |      |                 |     | than on         | NVIDIA | K40C    | GPU, | while the   | overall | behav-   |
| ---------------------------- | --- | --- | --- | ---- | --------------- | --- | --------------- | ------ | ------- | ---- | ----------- | ------- | -------- |
| Alternativeimplementationsof |     |     |     | P2P. | Althoughseveral |     |                 |        |         |      |             |         |          |
|                              |     |     |     |      |                 |     | ior is similar. |        | We find | that | cudaMemcopy |         | might be |
priorworksreportedlyimplementP2PbetweenSSDsand
GPUs[4–8],wefoundonlytheearlyprototypeofProject slowerthenAMDClWrite,andtheGPUBARwritesfor
|           |         |               |            |             |     |            | NVIDIA           | GPUs | are slower | for   | some block | sizes. | These     |
| --------- | ------- | ------------- | ---------- | ----------- | --- | ---------- | ---------------- | ---- | ---------- | ----- | ---------- | ------ | --------- |
| Donard    | [8] to  | be publicly   | available. | However,    |     | this pro-  |                  |      |            |       |            |        |           |
|           |         |               |            |             |     |            | results indicate |      | that SPIN  | works | well       | with   | GPUs from |
| totype is | limited | and is slower | for        | all request |     | sizes, and |                  |      |            |       |            |        |           |
differentvendors,howeverthesmallperformancegapwe
| particularlyforshorterrequests, |     |     |     | thereforewedonotin- |     |     |     |     |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
observerequiresfurtherinvestigation.
cludeitintheexperiments.
|     |     |     |     |     |     |     | SoftwareRAID-0. |        | WeusethestandardmdadmLinux |            |     |        |          |
| --- | --- | --- | --- | --- | --- | --- | --------------- | ------ | -------------------------- | ---------- | --- | ------ | -------- |
|     |     |     |     |     |     |     | utility to      | create | a RAID-0                   | (striping) |     | volume | over two |
6.1 ThreadedIObenchmarks
NVMeSSDs.Inthisconfiguration,thestoreddataissplit
betweentwoSSDsaccordingtotheconfiguredstripesize
| We use | TIOtest | [16] for | our benchmarks. |     | TIOtest | is a |     |     |     |     |     |     |     |
| ------ | ------- | -------- | --------------- | --- | ------- | ---- | --- | --- | --- | --- | --- | --- | --- |
(512KBinourconfiguration),thusperforminglargerfile
standardtoolforevaluatingfileI/OperformanceinCPU-
accessesinparallel.
| only systems. |     | It supports | multi-threading |     | (each | thread |     |     |     |     |     |     |     |
| ------------- | --- | ----------- | --------------- | --- | ----- | ------ | --- | --- | --- | --- | --- | --- | --- |
Figure4cshowstherelativethroughputofrandomac-
accessesitsownfile),sequential/randomaccesspatterns
|               |                  |           |             |           |             |          | cessesforwhichSPINalwaysusesP2P.              |          |           |     |               | RAID-0outper- |            |
| ------------- | ---------------- | --------- | ----------- | --------- | ----------- | -------- | --------------------------------------------- | -------- | --------- | --- | ------------- | ------------- | ---------- |
| and different | I/O              | request   | sizes.      | We modify | the         | original |                                               |          |           |     |               |               |            |
| 1             |                  |           |             |           |             |          | formsasingleSSDonlyforlargereads(above512KB). |          |           |     |               |               |            |
| code to       | read             | data into | GPU buffers |           | using all   | the five |                                               |          |           |     |               |               |            |
|               |                  |           |             |           |             |          | This is due                                   | to extra | overheads |     | of additional |               | processing |
| evaluated     | implementations. |           | For         | SPIN      | our changes | re-      |                                               |          |           |     |               |               |            |
intheRAIDlayerwhichgetamortizedforlargerblocks.
quiredmodifying10LOCforbufferallocation.
|     |     |     |     |     |     |     | For large   | sequential | reads, | SPIN      | achieves | a      | throughput |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | ------ | --------- | -------- | ------ | ---------- |
|     |     |     |     |     |     |     | of 5.2GB/s. | The        | higher | bandwidth | is       | due to | the SSDs   |
1https://wiki.codeaurora.org/xwiki/bin/Linux+
| Filesystems/Tiobench |     |     |     |     |     |     | performancecharacteristics. |     |     |     |     |     |     |
| -------------------- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | --- | --- | --- |
174    2017 USENIX Annual Technical Conference USENIX Association

(cid:11)(cid:2)(cid:12)(cid:13)(cid:8)(cid:14)(cid:10) (cid:11)(cid:2)(cid:12)(cid:13)(cid:8)(cid:14)(cid:10)(cid:15)(cid:16) (cid:17)(cid:18)(cid:17) (cid:19)(cid:13)(cid:10)(cid:20)(cid:21)(cid:22)(cid:23)(cid:6)(cid:15)(cid:6)(cid:24)(cid:17)(cid:25) (cid:26)(cid:17)(cid:27)(cid:28) (cid:11)(cid:2)(cid:12)(cid:13)(cid:8)(cid:14)(cid:10) (cid:11)(cid:15)(cid:12)(cid:13)(cid:8)(cid:14)(cid:10)(cid:16)(cid:17) (cid:18)(cid:19)(cid:18) (cid:20)(cid:13)(cid:10)(cid:21)(cid:22)(cid:23)(cid:24)(cid:16)(cid:25)(cid:18)(cid:26) (cid:27)(cid:18)(cid:28)(cid:29)
|                                                                                                                                                            | (cid:6)(cid:2)(cid:1) |     |     |     |     |     | (cid:6)(cid:2)(cid:1)                                                                                                                                      |         |     |     |     |     |     |     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | --- | --- | --- | --- | --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | --- | --- | --- | --- | --- | --- |
| (cid:15)(cid:8)(cid:5)(cid:12)(cid:14)(cid:9)(cid:13)(cid:12)(cid:11)(cid:10)(cid:9)(cid:5)(cid:8)(cid:2)(cid:7)(cid:6)(cid:5)(cid:4)(cid:3)(cid:2)(cid:1) |                       |     |     |     |     |     | (cid:15)(cid:8)(cid:5)(cid:12)(cid:14)(cid:9)(cid:13)(cid:12)(cid:11)(cid:10)(cid:9)(cid:5)(cid:8)(cid:2)(cid:7)(cid:6)(cid:5)(cid:4)(cid:3)(cid:2)(cid:1) |         |     |     |     |     |     |     |
|                                                                                                                                                            | (cid:6)(cid:1)(cid:1) |     |     |     |     |     | (cid:6)(cid:1)(cid:1)                                                                                                                                      |         |     |     |     |     |     |     |
|                                                                                                                                                            | (cid:5)(cid:1)        |     |     |     |     |     | (cid:5)(cid:1)                                                                                                                                             |         |     |     |     |     |     |     |
|                                                                                                                                                            | (cid:4)(cid:1)        |     |     |     |     |     | (cid:4)(cid:1)                                                                                                                                             |         |     |     |     |     |     |     |
|                                                                                                                                                            | (cid:3)(cid:1)        |     |     |     |     |     | (cid:3)(cid:1)                                                                                                                                             |         |     |     |     |     |     |     |
|                                                                                                                                                            | (cid:2)(cid:1)        |     |     |     |     |     | (cid:2)(cid:1)                                                                                                                                             |         |     |     |     |     |     |     |
|                                                                                                                                                            | (cid:1)               |     |     |     |     |     |                                                                                                                                                            | (cid:1) |     |     |     |     |     |     |
(cid:7)(cid:6)(cid:2)(cid:8) (cid:3)(cid:9) (cid:6)(cid:4)(cid:9) (cid:4)(cid:3)(cid:9) (cid:7)(cid:6)(cid:2)(cid:9) (cid:6)(cid:12) (cid:3)(cid:12) (cid:5)(cid:12) (cid:1)(cid:2)(cid:3)(cid:4) (cid:7)(cid:8) (cid:2)(cid:5)(cid:8) (cid:5)(cid:7)(cid:8) (cid:1)(cid:2)(cid:3)(cid:8) (cid:2)(cid:11) (cid:7)(cid:11) (cid:10)(cid:11)
(cid:2)(cid:5) (cid:6)(cid:10)(cid:7) (cid:3)(cid:1)(cid:1) (cid:4)(cid:5)(cid:4) (cid:2)(cid:6)(cid:10)(cid:11) (cid:2)(cid:3)(cid:2)(cid:4) (cid:2)(cid:7)(cid:3)(cid:6) (cid:2)(cid:7)(cid:7)(cid:6) (cid:2)(cid:1)(cid:5)(cid:6) (cid:2)(cid:9)(cid:9)(cid:9) (cid:2)(cid:10)(cid:10)(cid:9) (cid:2)(cid:9)(cid:1)(cid:1) (cid:3)(cid:1)(cid:6)(cid:1) (cid:3)(cid:5)(cid:9)(cid:12) (cid:3)(cid:9)(cid:3)(cid:9) (cid:3)(cid:5)(cid:6)(cid:3)
| (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10)(cid:11)(cid:12)(cid:13)(cid:14) |     |                         |     |                                                                         |     |     | (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10)(cid:11)(cid:12)(cid:13)(cid:14) |     |                             |     |                                                                         |     |     |     |
| ------------------------------------------------------------------------------------------------------- | --- | ----------------------- | --- | ----------------------------------------------------------------------- | --- | --- | ------------------------------------------------------------------------------------------------------- | --- | --------------------------- | --- | ----------------------------------------------------------------------- | --- | --- | --- |
|                                                                                                         |     |                         |     | (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10) |     |     |                                                                                                         |     |                             |     | (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10) |     |     |     |
|                                                                                                         |     | (a)Randomreads,4threads |     |                                                                         |     |     |                                                                                                         |     | (b)Sequentialreads,4threads |     |                                                                         |     |     |     |
(cid:11)(cid:2)(cid:12)(cid:13)(cid:8)(cid:14)(cid:10) (cid:11)(cid:2)(cid:12)(cid:13)(cid:8)(cid:14)(cid:10)(cid:15)(cid:16) (cid:17)(cid:18)(cid:17) (cid:19)(cid:13)(cid:10)(cid:20)(cid:21)(cid:22)(cid:23)(cid:6)(cid:15)(cid:6)(cid:24)(cid:17)(cid:25) (cid:26)(cid:17)(cid:27)(cid:28) (cid:14)(cid:6)(cid:15)(cid:16)(cid:5)(cid:17)(cid:7) (cid:14)(cid:6)(cid:15)(cid:16)(cid:5)(cid:17)(cid:7)(cid:18)(cid:19) (cid:20)(cid:21)(cid:20) (cid:9)(cid:16)(cid:7)(cid:10)(cid:22)(cid:23)(cid:24)(cid:2)(cid:18)(cid:2)(cid:25)(cid:20)(cid:26) (cid:27)(cid:20)(cid:28)(cid:29)
|                                                                                                                                                            | (cid:6)(cid:2)(cid:1) |     |     |     |     |     | (cid:6)(cid:2)(cid:1)                                                                                                                                             |     |     |     |     |     |     |     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | --- | --- | --- | --- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| (cid:15)(cid:8)(cid:5)(cid:12)(cid:14)(cid:9)(cid:13)(cid:12)(cid:11)(cid:10)(cid:9)(cid:5)(cid:8)(cid:2)(cid:7)(cid:6)(cid:5)(cid:4)(cid:3)(cid:2)(cid:1) |                       |     |     |     |     |     | (cid:14)(cid:8)(cid:5)(cid:12)(cid:13)(cid:12)(cid:11)(cid:10)(cid:9)(cid:5)(cid:8)(cid:2)(cid:7)(cid:6)(cid:5)(cid:4)(cid:3)(cid:2)(cid:1) (cid:6)(cid:1)(cid:1) |     |     |     |     |     |     |     |
(cid:6)(cid:1)(cid:1)
(cid:5)(cid:1)
|     | (cid:5)(cid:1) |     |     |     |     |     |     | (cid:4)(cid:1) |     |     |     |     |     |     |
| --- | -------------- | --- | --- | --- | --- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- |
|     | (cid:4)(cid:1) |     |     |     |     |     |     | (cid:3)(cid:1) |     |     |     |     |     |     |
(cid:2)(cid:1)
(cid:3)(cid:1)
(cid:1)
(cid:2)(cid:1)
|     |     |     |     |     |     |     |     | (cid:1)(cid:7) | (cid:8)(cid:1)(cid:7) (cid:6)(cid:1)(cid:1)(cid:7) | (cid:1)(cid:7) | (cid:8)(cid:1)(cid:7) | (cid:6)(cid:1)(cid:1)(cid:7) (cid:1)(cid:7) | (cid:8)(cid:1)(cid:7) | (cid:6)(cid:1)(cid:1)(cid:7) |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | -------------------------------------------------- | -------------- | --------------------- | ------------------------------------------- | --------------------- | ---------------------------- |
(cid:1)
(cid:7)(cid:6)(cid:2)(cid:8) (cid:3)(cid:10) (cid:6)(cid:4)(cid:10) (cid:4)(cid:3)(cid:10) (cid:7)(cid:6)(cid:2)(cid:10) (cid:6)(cid:12) (cid:3)(cid:12) (cid:5)(cid:12) (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10)(cid:11)(cid:12)(cid:13)(cid:14) (cid:6)(cid:2)(cid:8)(cid:9) (cid:6)(cid:9)(cid:3)(cid:10) (cid:8)(cid:2)(cid:9)(cid:4) (cid:6)(cid:2)(cid:3)(cid:5) (cid:6)(cid:9)(cid:8)(cid:8) (cid:3)(cid:6)(cid:6)(cid:3) (cid:5)(cid:10)(cid:1) (cid:6)(cid:10)(cid:4)(cid:11) (cid:8)(cid:10)(cid:6)(cid:8)
(cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10)(cid:11)(cid:12)(cid:13)(cid:14) (cid:2)(cid:9) (cid:6)(cid:9)(cid:7) (cid:3)(cid:6)(cid:7) (cid:9)(cid:4)(cid:6) (cid:2)(cid:11)(cid:7)(cid:4) (cid:3)(cid:6)(cid:3)(cid:3) (cid:3)(cid:9)(cid:2)(cid:4) (cid:3)(cid:5)(cid:4)(cid:11) (cid:12)(cid:13)(cid:14)(cid:15)(cid:13)(cid:16)(cid:17)(cid:18)(cid:17)(cid:13)(cid:19)(cid:20) (cid:21)(cid:22)(cid:23)(cid:14)(cid:15)(cid:13)(cid:16)(cid:18)(cid:17)(cid:13)(cid:19)(cid:20) (cid:24)(cid:25)(cid:26)(cid:14)(cid:15)(cid:13)(cid:16)(cid:18)(cid:17)(cid:13)(cid:19)(cid:20)
|     |     |     |     | (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10) |     |     |     |     |     | (cid:1)(cid:2)(cid:3)(cid:4)(cid:2)(cid:4)(cid:5)(cid:6)(cid:7)(cid:2)(cid:5)(cid:8)(cid:2)(cid:9)(cid:10)(cid:11)(cid:7)(cid:2)(cid:12)(cid:10)(cid:12)(cid:13)(cid:7) |     |     |     |     |
| --- | --- | --- | --- | ----------------------------------------------------------------------- | --- | --- | --- | --- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | --- | --- | --- |
(c)RAID:Randomreads,4threads (d) Random512KBreads,inparallelwithCPU/I/Oworkloads
|     |     |     |     | Figure4: |     | ThreadedIObenchmarksforAMDGPUs. |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | -------- | --- | ------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
SPIN pread P2P P2P + ClWrite CLWrite+ Effect of the page cache on read throughput. The
|     |     | +GPU |     | RAID |     | D+RAID |     |     |     |     |     |     |     |     |
| --- | --- | ---- | --- | ---- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
goalofthisexperimentistoshowpotentialperformance
| 10.13 |     | 10.28 | 2.65 | 5.29 | 5.72 | 4.69 |       |     |                   |     |           |     |       |          |
| ----- | --- | ----- | ---- | ---- | ---- | ---- | ----- | --- | ----------------- | --- | --------- | --- | ----- | -------- |
|       |     |       |      |      |      |      | gains | for | producer-consumer |     | workloads |     | which | may uti- |
Table3:Maxreadthroughput(GB/s).Fileinpagecache. lize both the CPU and GPU while they access a shared
|     |                                                       |                                                                       |     |                                                  |                                                                                        |                                  | file. | We   | prefetch    | different | portions | of     | a 40GB      | file into |
| --- | ----------------------------------------------------- | --------------------------------------------------------------------- | --- | ------------------------------------------------ | -------------------------------------------------------------------------------------- | -------------------------------- | ----- | ---- | ----------- | --------- | -------- | ------ | ----------- | --------- |
|     |                                                       |                                                                       |     |                                                  |                                                                                        |                                  | the   | page | cache using | vmtouch   |          | 2, and | run TIOtest | for       |
|     | (cid:14)(cid:6)(cid:15)(cid:16)(cid:5)(cid:17)(cid:7) | (cid:14)(cid:6)(cid:15)(cid:16)(cid:5)(cid:17)(cid:7)(cid:18)(cid:19) |     | (cid:20)(cid:21)(cid:20)(cid:19)(cid:22)(cid:23) | (cid:9)(cid:16)(cid:7)(cid:10)(cid:24)(cid:25)(cid:26)(cid:18)(cid:27)(cid:20)(cid:28) | (cid:29)(cid:20)(cid:30)(cid:31) |       |      |             |           |          |        |             |           |
512Brandomreads.
(cid:15)(cid:8)(cid:5)(cid:12)(cid:14)(cid:9)(cid:13)(cid:12)(cid:11)(cid:10)(cid:9)(cid:5)(cid:8)(cid:2)(cid:7)(cid:6)(cid:5)(cid:4)(cid:3)(cid:2)(cid:1) (cid:6)(cid:2)(cid:1)
|     |     |     |     |     |     |     |     | Figure | 5 shows | the relative | throughput, |     | highlighting |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------- | ------------ | ----------- | --- | ------------ | --- |
(cid:6)(cid:1)(cid:1)
(cid:5)(cid:1) thedifferencesbetweentransfermethods. Notonlydoes
(cid:4)(cid:1) SPINtrackthebestalternative,itisfasterthanthefastest
|     | (cid:3)(cid:1) |     |     |     |     |     | amongthembyupto20%. |     |     |     | Thatisbecauseitcombines |     |     |     |
| --- | -------------- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | ----------------------- | --- | --- | --- |
(cid:2)(cid:1)
bothpagecacheandP2P,dynamicallychoosingbetween
(cid:1)
(cid:1) (cid:6)(cid:1) (cid:2)(cid:1) (cid:8)(cid:1) (cid:3)(cid:1) (cid:9)(cid:1) (cid:4)(cid:1) (cid:7)(cid:1) (cid:5)(cid:1) (cid:10)(cid:1) (cid:6)(cid:1)(cid:1) themperrequestdependingontheresidenceinthepage
| (cid:1)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:10)(cid:11)(cid:12)(cid:13)(cid:14) |     | (cid:7) (cid:5) | (cid:5) (cid:6)(cid:1) | (cid:6)(cid:6) (cid:6)(cid:3) (cid:6)(cid:7) | (cid:2)(cid:2) | (cid:8)(cid:2) (cid:9)(cid:5) (cid:2)(cid:8)(cid:10) |       |            |     |             |     |         |          |        |
| ------------------------------------------------------------------------------------------------------- | --- | --------------- | ---------------------- | -------------------------------------------- | -------------- | ---------------------------------------------------- | ----- | ---------- | --- | ----------- | --- | ------- | -------- | ------ |
|                                                                                                         |     |                 |                        |                                              |                |                                                      | cache | (discussed | in  | (§ 4.3.1)). |     | SPIN is | slightly | slower |
(cid:1)(cid:2)(cid:3)(cid:4)(cid:2)(cid:4)(cid:5)(cid:6)(cid:7)(cid:2)(cid:5)(cid:8)(cid:2)(cid:9)(cid:10)(cid:11)(cid:7)(cid:2)(cid:12)(cid:10)(cid:12)(cid:13)(cid:7)
|     |     |     |     |     |     |     | on  | the extremes   | due | to      | the 5%  | overhead | it introduces |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------- | ------- | -------- | ------------- | --- |
|     |     |     |     |     |     |     | in  | this scenario. |     | ClWrite | results | in low   | performance   |     |
Figure5: Randomaccessperformancefordifferentpage
|                 |     |                      |     |     |     |     | due    | to its | constant | invocation | overhead, |     | whose  | relative |
| --------------- | --- | -------------------- | --- | --- | --- | --- | ------ | ------ | -------- | ---------- | --------- | --- | ------ | -------- |
| cacheoccupancy. |     | Readingblocksof512B. |     |     |     |     |        |        |          |            |           |     |        |          |
|                 |     |                      |     |     |     |     | weight | grows  | when     | most       | requests  | are | served | from the |
pagecache,aswealsoseeinFigure4b.
|         |     |            |      |             |     |            | SPINperformanceunderCPUandI/Oload. |     |     |     |     |     |     | Weexe- |
| ------- | --- | ---------- | ---- | ----------- | --- | ---------- | ---------------------------------- | --- | --- | --- | --- | --- | --- | ------ |
| Maximum |     | sequential | read | throughput. |     | We compare |                                    |     |     |     |     |     |     |        |
cutethesameexperimentasinFigure5,butnowimpose
themaximumachievablethroughputoverdifferenttrans-
|                |     |                                    |     |     |     |             | heavy      | load | on all | the CPUs  | or SSD   | in  | parallel | with the |
| -------------- | --- | ---------------------------------- | --- | --- | --- | ----------- | ---------- | ---- | ------ | --------- | -------- | --- | -------- | -------- |
| fermechanisms. |     | Thetestperformssequentialreadsfrom |     |     |     |             |            |      |        |           |          |     |          |          |
|                |     |                                    |     |     |     |             | benchmark. |      | The    | benchmark | performs |     | 512KB    | random   |
| 4threads,      |     | 8MBperreadfroma4GBfile,            |     |     |     | whenafileis |            |      |        |           |          |     |          |          |
prefetched into the page cache. Table 3 shows the re- reads (cutoff size for reading from the page cache), to
showtheworst-casescenarioforSPINunderCPUload.
| sults. | SPIN | is faster | than | all the transfer |     | methods that |     |     |     |     |     |     |     |     |
| ------ | ---- | --------- | ---- | ---------------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
donotusepagecache,andfasterthanClWritethatdoes.
SPIN’soverheadinthisscenariois1.5%. 2https://hoytech.com/vmtouch/
USENIX Association 2017 USENIX Annual Technical Conference    175

(cid:6)(cid:2)(cid:1)
(cid:6)(cid:1)(cid:1)
(cid:5)(cid:1)
(cid:4)(cid:1)
(cid:3)(cid:1)
(cid:2)(cid:1)
(cid:1)
(cid:1)(cid:2)(cid:3) (cid:4)(cid:2)(cid:3) (cid:5)(cid:1)(cid:2)(cid:3) (cid:4)(cid:6)(cid:2) (cid:5)(cid:7)(cid:1)(cid:2)
(cid:8)(cid:9)(cid:10)(cid:11)(cid:12)(cid:13)(cid:14)(cid:15)(cid:16)(cid:17)(cid:11)(cid:18)(cid:19)(cid:20)(cid:16)(cid:20)(cid:10) (cid:23)(cid:18)(cid:21)(cid:12)(cid:14)(cid:15)(cid:16)(cid:17)(cid:11)(cid:18)(cid:19)(cid:20)(cid:16)(cid:20)(cid:10)
(cid:21)(cid:9)(cid:22)(cid:16)(cid:20)(cid:11) (cid:21)(cid:9)(cid:22)(cid:16)(cid:20)(cid:11)
(cid:10)(cid:12)(cid:11)(cid:2)(cid:2)(cid:10)(cid:9)(cid:8)(cid:2)(cid:7)(cid:6)(cid:5)(cid:4)(cid:3)(cid:2)(cid:1)
GPU
(cid:24)(cid:21)(cid:25)(cid:13)(cid:18)(cid:11)(cid:12) (cid:24)(cid:21)(cid:25)(cid:13)(cid:18)(cid:11)(cid:12)(cid:26)(cid:27) (cid:28)(cid:1)(cid:28) (cid:29)(cid:13)(cid:12)(cid:9)(cid:30)(cid:31) !(cid:26)!"(cid:28)# $(cid:28)%& Configuration CPU
P2P ClWrite() SPIN
Thput 771 594(0.8×) 1921(2.5×) 1950(2.5×)
R-time
CPUutil 79.5% 3% 11.8% 10.7%
Thput 634 2549(4×) 1822(2.9×) 2550(4×)
Offline CPUutil 70.3% 8.5% 12.3% 8.5%
Table 4: Log server throughput (in MB/s), CPU utiliza-
tionandspeedupovertheCPU-onlyversion
mechanismdependsonthelayoutinuse. Forthenative
Figure6: Aerialimagerybenchmarkthroughputrelative layoutwithmostlyrandomaccesspattern,P2PandSPIN
toSPINfordifferentfilelayouts. Higherisbetter. achievethehighestthroughput.However,fortiledlayout
thereadsaremostlysequential, andSPINbenefitsfrom
the read-ahead achieving up to 2.5× higher throughput
We use stress-ng 3 benchmarking tool. Figure 4d
than P2P for 12K reads. SPIN eliminates the need to
shows the relative throughput for 0%, 50%, and 100%
manuallyperformsuchlowleveloptimizations,reducing
file residency in the page cache, with and without CPU
codecomplexityanddevelopmentefforts.
or SSD load. We observe that SPIN retains its perfor-
GPU-accelerated log server. Log servers, such as
manceadvantagesregardlessofthesystemload.
VMWare VRealize [25], are commonly used in dis-
tributed systems for centralized storage and processing
6.2 Applicationbenchmarks
of logs from multiple servers. Log processing usually
involves string and regular expression matching, which
AerialImageryRendering. GPUsarecommonlyused
maybenefitfromaccelerationonGPUs[26].
for rendering aerial imagery in geographic information
Weimplementasimplelogserverwhichreceiveslog
systems (GIS). The datasets used in such systems may
files over the network, stores them locally in files, and
growtohundredsofGBs.Largerastersaresplitintotiles
scans them for suspicious IPs from the list provided by
inordertoshortensystemresponsetime. Therendering
theuser. Asiscommoninlogprocessingsystems, e.g.,
engine reads the tilesfrom a file depending on the view
Fail2Ban [11], log analysis is performed in a separate
point,andstitchesthemtogether.
scannerprocessthatreadsthespecifiedlogfileandpro-
In our evaluation we generate I/O traces via a bench-
cesses it. Such a modular design is convenient because
marking tool for web-based rendering engines [23].
it enables to easily extend the analysis using several in-
We use TrueMarble dataset [24] from standard bench-
dependentbackends. Ourimplementationofthescanner
marks[23], whichisa190GBmulti-rasteroftheEarth,
offloadsthestringmatchingtoaGPU.
eachrastercorrespondstoadifferentimageresolution.
We measure the maximum system throughput in two
The actual file access pattern in this application de-
scenarios: (1)realtime,inwhichthescannerisinvoked
pends on the underlying file layout. There are two lay-
each time the files get updated (using inotify inter-
outs:(1)raster-contiguouslayout,wherethewholeraster
face) (2) offline, in which the scanner is invoked on a
isstoredasa1Dvectorinthefileand(2)tile-contiguous
specificlogfiletobeprocessedasawhole. Inbothcon-
layout, where each tile is a 1D vector and the raster is
figurations,atotalof80GBofdataisprocessed.
composed of many 1D tiles. The first layout results in
We evaluate our GPU implementation with different
mostly random accesses 2-4KB each, whereas the sec-
I/O mechanisms: (1) traditional pread() followed by
ondinvolvesmostlysequentialaccesseseachfrom12KB
ClWrite()toGPUmemory,(2)P2P(3)SPIN.Wealso
to192KB.Weemphasizethattherenderingapplications
implementaCPU-onlyversionthatusesIntel’sThread-
mustbeabletoaccommodatefileswithbothlayouts.
ingBuildingBlocksandrunson6cores.
To generate the trace we randomly choose the target
Table 4 shows that in the real time scenario SPIN
imageresolutionandtheviewregion, derivethetilesto
achieves the highest throughput among all other I/O
render that region and record their respective offsets in
methods. Since the system triggers log processing right
thedatasetfile. Weusetilesofsizesrangingfrom64x64
after it receives log file updates from the network, the
pixelsupto1024x1024pixels. Ineverytraceweemulate
new contents have not yet been written back to the disk
renderingof1000differentregionsinfullHD.
and reside entirely in the page cache. SPIN, therefore,
We generate the traces for different input layouts
reads the data from the page cache, relieving I/O con-
and compare the throughput of different transfer mech-
tentionontheSSDwhichdooccurinP2Pconfiguration.
anisms. As Figure 6 shows, the choice of the transfer
In the steady state, the system throughput is limited by
3https://openbenchmarking.org/test/pts/stress-ng the maximum SSD write throughput, because the net-
176 2017 USENIX Annual Technical Conference USENIX Association

workserverkeepswritingtheupdatestostorage,eventu- Gullfoss [5] software framework for P2P shares many
allyexhaustingthepagecachespace. Intheofflinesce- conceptual similarities with NVMMU, and hence many
nario the data is not in the page cache, therefore SPIN of its limitations. Morpheus [7] enables P2P to GPUs
switchestouseP2P. from SSDs, but does not address the challenges of inte-
Inthisapplication,complexinteractionsbetweenmul- grating P2P intostandardfileI/O,focusingprimarilyon
tipleprocessesdynamicallycreatefiledatareuseoppor- lowlevelP2Pfunctionality.
tunitiesthatcannotbeknowninadvance,hencearehard GDRcopy [21] uses CPU-mapped regions of GPU
|                                |     |     |     |                   |     |     | memoryforefficientdatatransferstoGPUs. |     |     |     |     | SPINlever- |     |
| ------------------------------ | --- | --- | --- | ----------------- | --- | --- | -------------------------------------- | --- | --- | --- | --- | ---------- | --- |
| toleveragewithouttheOSsupport. |     |     |     | SPINre-enablesthe |     |     |                                        |     |     |     |     |            |     |
standard OS ability to handle such opportunistic reuse agesthesamefunctionality.
automaticallyforfiletransferstotheGPU.
|     |     |     |     |     |     |     | P2P technologies. |     | Recent | GPUs | offer support | for | P2P, |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | ------ | ---- | ------------- | --- | ---- |
Imagecollage. Theimagecollageapplication[15]cre- includingGPUDirectRDMA[28]fromNVIDIAandDi-
|         |       |         |              |        |     |           | rectGMA | [3] from | AMD. | These | technologies |     | provide |
| ------- | ----- | ------- | ------------ | ------ | --- | --------- | ------- | -------- | ---- | ----- | ------------ | --- | ------- |
| ates an | image | collage | by replacing | blocks | in  | the input |         |          |      |       |              |     |         |
image with ”similar” tiny images from a data base (we generic support for direct access to GPU memory from
use [27]). Pre-processed tiny images are stored in a PCIedevices,buttheydonotintegrateitintohigherlevel
| file of size | 38GB. | We  | use an | open-source | implementa- |     | serviceslikefileI/O. |     |     |     |     |     |     |
| ------------ | ----- | --- | ------ | ----------- | ----------- | --- | -------------------- | --- | --- | --- | --- | --- | --- |
tionthatusesGPUfs[18]GPU-sidelibraryforaccessing System abstractions for GPUs. GPUfs and GPUnet
filesfromGPUkernels. GPUfsusesadedicatedworker [10, 18, 29] provide file access and networking directly
thread running on the CPU to handle the file transfers to GPU programs. The current work is complementary
| intotheGPUmemory. |     |     | Thisapplicationperformsmostly |     |     |     |     |     |     |     |     |     |     |
| ----------------- | --- | --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
asitsimplifiestheuseofP2PforCPUprograms.
randomreads512Beach.
TheoriginalversionofGPUfsfirstreadsthefilecon-
|     |     |     |     |     |     |     | 8 Conclusions |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- |
tentsintothehoststagingarea,andthencopiesthedata
| intoGPUmemoryviacudaMemcopy. |     |     |     |     | Weremovethe |     |              |     |                 |     |         |              |     |
| ---------------------------- | --- | --- | --- | --- | ----------- | --- | ------------ | --- | --------------- | --- | ------- | ------------ | --- |
|                              |     |     |     |     |             |     | SPIN focuses | on  | the fundamental |     | problem | of providing |     |
staging area in the host, and allocate the staging area in generic OS abstractions in heterogeneous systems, ex-
theGPUmemory,changingintotal30LOC.
tendingthetraditionalI/Omechanismstosystematically
| We measure |     | the SPIN | speedup | over | the unmodified |     |           |        |          |          |         |     |        |
| ---------- | --- | -------- | ------- | ---- | -------------- | --- | --------- | ------ | -------- | -------- | ------- | --- | ------ |
|            |     |          |         |      |                |     | deal with | direct | I/O into | the GPU. | We show | the | impor- |
version. Forthreedifferentinputimagesof3MB,12MB
tanceoftighterintegrationofP2PwiththefileI/Ostack,
and48MBSPINis×1.27±0.02fasteronaveragethanks
|     |     |     |     |     |     |     | exposethechallengesassociatedwiththeuseof |     |     |     |     |     | P2P to- |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------------- | --- | --- | --- | --- | --- | ------- |
totheuseofP2Pforshortrandomreads. getherwiththepagecacheandread-ahead,anddevisea
practicalsolutionwhichoutperformsthestate-of-the-art
inarangeofrealisticscenarios.
7 Relatedwork
Currenthardwaretrendsaretowardsystemswithmul-
|                      |     |     |                           |     |     |     | tiple accelerators |     | [30, | 31], which | will | dramatically | in- |
| -------------------- | --- | --- | ------------------------- | --- | --- | --- | ------------------ | --- | ---- | ---------- | ---- | ------------ | --- |
| SystemsupportforP2P. |     |     | Therehavebeenseveralworks |     |     |     |                    |     |      |            |      |              |     |
creasesystemheterogeneityandcomplicatesoftwarede-
| whichenable | P2P       | betweenNVMeSSDsandGPUs, |             |      |                   | but       |               |     |             |          |              |           |     |
| ----------- | --------- | ----------------------- | ----------- | ---- | ----------------- | --------- | ------------- | --- | ----------- | -------- | ------------ | --------- | --- |
|             |           |                         |             |      |                   |           | velopment.    | OS  | support     | for such | increasingly | heteroge- |     |
| SPIN is     | the first | to integrate            | P2P         | with | the OS            | file I/O, |               |     |             |          |              |           |     |
|             |           |                         |             |      |                   |           | neous systems |     | must extend | beyond   | low-level    | APIs,     | and |
| dealing     | with page | cache,                  | read-ahead, |      | data consistency, |           |               |     |             |          |              |           |     |
providetheconvenienceofhighlevelOSabstractionsto
andcompatibilitywithvirtualblockdevices.
achievetheirperformancepotential.SPINisastepinthis
| GPUDrive | [6] | is a | system | for processing |     | streaming |     |     |     |     |     |     |     |
| -------- | --- | ---- | ------ | -------------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
direction.
I/O-intensiveGPUworkloadsbasedonanall-flashstor-
|     |     |     |     |     |     |     | SPIN | is  | available | at  | https://github.com/acsl- |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --------- | --- | ------------------------ | --- | --- |
agearrayconnectedtotheGPU.
technion/spin
NVMMU[4]introducesaspecialprogrammingmodel
| and runtime | for | P2P | with GPUs. | NVMUU | shows | that |     |     |     |     |     |     |     |
| ----------- | --- | --- | ---------- | ----- | ----- | ---- | --- | --- | --- | --- | --- | --- | --- |
Acknowledgements
P2PachieveshighperformancewithstandardGPUcom-
| pute benchmarks |     | modified | to read | input | data from | files. |     |     |     |     |     |     |     |
| --------------- | --- | -------- | ------- | ----- | --------- | ------ | --- | --- | --- | --- | --- | --- | --- |
UnlikeSPIN,however,itrequiresacustominterfacefor MarkSilbersteinissupportedbytheIsraelScienceFoun-
|     |     |     |     |     |     |     | dation (grant | No. | 1138/14), | and | the Israeli | Ministry | of  |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | --------- | --- | ----------- | -------- | --- |
P2P, doesnotaddressthepagecacheintegrationissues,
EconomicsviaHiPerconsortium.
andfocusesonlyonGPU-onlyapplicationswithlargese-
| quentialreads.                           |     | Infact,itshowsthatP2Pisslowforsmall |     |     |     |     |            |     |     |     |     |     |     |
| ---------------------------------------- | --- | ----------------------------------- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- |
| I/Orequestsbutdoesnotaddressthisproblem. |     |                                     |     |     |     |     | References |     |     |     |     |     |     |
ProjectDonard[8]wasamongthefirsttosupportP2P
viaalowleveldriverinterface. Amongitsmanylimita- [1] “AMD Radeon Pro SSG Set to Transform
tions,itrunsonlywithrootprivilegesduetodirectaccess Workstation PC Architecture, and to Shat-
to NVMe DMA, and suffers from performance issues. ter Real-Time Visual Computing Barriers.”
USENIX Association 2017 USENIX Annual Technical Conference    177

http://www.amd.com/en-us/press- [14] “ArcGIS for Desktop.” http://desktop.
| releases/Pages/amd-radeon-pro- |     |     |     |     |     | arcgis.com/en/arcmap. |     |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- |
2016jul25.aspx,2016.
|     |     |     |     |     |     | [15] S. Shahar, | S.  | Bergman, | and | M. Silberstein, |     | “Ac- |
| --- | --- | --- | --- | --- | --- | --------------- | --- | -------- | --- | --------------- | --- | ---- |
[2] “GPUDirectRDMA.”http://docs.nvidia. tivePointers: A Case For Software Translation on
com/cuda/gpudirect-rdma/index.
GPUs,”ISCA,IEEE,ACM,2016.
html,2015.
https://
|     |     |     |     |     |     | [16] “Threaded |     | I/O | Tester.” |     |     |     |
| --- | --- | --- | --- | --- | --- | -------------- | --- | --- | -------- | --- | --- | --- |
[3] “Tech Brief: AMD FireProTM SDI - sourceforge.net/p/tiobench.
| Link | and | AMD | DirectGMA | Technology.” |     |     |     |     |     |     |     |     |
| ---- | --- | --- | --------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
https://www.amd.com/Documents/SDI- [17] “GPU Support in Apache Spark and GPU/CPU
|     |     |     |     |     |     | Mixed | Resource |     | Scheduling | at  | Production |     |
| --- | --- | --- | --- | --- | --- | ----- | -------- | --- | ---------- | --- | ---------- | --- |
tech-brief.pdf.
|               |     |           |           |       |           | Scale.” |     | http://www.spark.tc/gpu- |     |     |     |     |
| ------------- | --- | --------- | --------- | ----- | --------- | ------- | --- | ------------------------ | --- | --- | --- | --- |
| [4] J. Zhang, | D.  | Donofrio, | J. Shalf, | M. T. | Kandemir, |         |     |                          |     |     |     |     |
support-in-spark-and-gpu-cpu-
and M. Jung, “NVMMU: A Non-volatile Memory mixed-resource-scheduling-at-
| Management |     | Unit | for Heterogeneous |     | GPU-SSD |     |     |     |     |     |     |     |
| ---------- | --- | ---- | ----------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
production-scale/,2016.
Architectures,”inPACT,pp.13–24,IEEE,2015.
|     |     |     |     |     |     | [18] M. Silberstein, |     | B. Ford, | I. Keidar, | and | E. Witchel, |     |
| --- | --- | --- | --- | --- | --- | -------------------- | --- | -------- | ---------- | --- | ----------- | --- |
[5] H.-W.Tseng,Y.Liu,M.Gahagan,J.Li,Y.Jin,and
|     |     |     |     |     |     | “GPUfs: | integrating |     | file systems | with | GPUs,” | in  |
| --- | --- | --- | --- | --- | --- | ------- | ----------- | --- | ------------ | ---- | ------ | --- |
S.Swanson,“Gullfoss: AcceleratingandSimplify- ASPLOS’13,ACM,2013.
| ing Data | Movement |     | Among Heterogeneous |     | Com- |     |     |     |     |     |     |     |
| -------- | -------- | --- | ------------------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
putingandStorageResources,”Tech.Rep.CS2015- [19] J. Yoo, Y. Won, J. Hwang, S. Kang, J. Choil,
1015, Department of Computer Science and Engi- S.Yoon,andJ.Cha,“Vssim:Virtualmachinebased
neering, University of California, San Diego tech- ssdsimulator,” inMassStorageSystemsandTech-
nicalreport,2015. nologies (MSST), 2013 IEEE 29th Symposium on,
pp.1–14,IEEE,2013.
| [6] M.Shihab,K.Taht,andM.Jung,“GPUDrive: |     |     |     |     | Re- |     |     |     |     |     |     |     |
| ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
considering Storage Accesses for GPU Accelera- [20] F. Chen, R. Lee, and X. Zhang, “Essential roles
tion,”inWorkshoponArchitecturesandSystemsfor of exploiting internal parallelism of flash memory
BigData,2014.
basedsolidstatedrivesinhigh-speeddataprocess-
|           |        |          |          |             |     | ing,” | in High | Performance | Computer |     | Architecture |     |
| --------- | ------ | -------- | -------- | ----------- | --- | ----- | ------- | ----------- | -------- | --- | ------------ | --- |
| [7] H.-W. | Tseng, | Q. Zhao, | Y. Zhou, | M. Gahagan, | and |       |         |             |          |     |              |     |
(HPCA),2011IEEE17thInternationalSymposium
| S. Swanson, |     | “Morpheus: | creating | application | ob- |     |     |     |     |     |     |     |
| ----------- | --- | ---------- | -------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
on,pp.266–277,IEEE,2011.
| jects    | efficiently  | for | heterogeneous | computing,”   | in  |              |     |        |      |         |       |     |
| -------- | ------------ | --- | ------------- | ------------- | --- | ------------ | --- | ------ | ---- | ------- | ----- | --- |
| Computer | Architecture |     | (ISCA),       | 2016 ACM/IEEE |     |              |     |        |      |         |       |     |
|          |              |     |               |               |     | [21] “A fast | GPU | memory | copy | library | based | on  |
43rd Annual International Symposium on, pp. 53– NVIDIAGPUDirectRDMAtechnology.”https:
| 65,IEEE,2016. |     |     |     |     |     | //github.com/NVIDIA/gdrcopy,2015. |     |     |     |     |     |     |
| ------------- | --- | --- | --- | --- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- |
[8] “Project Donard.” https://github.com/ [22] “Evacuate struct page from the block layer.”
sbates130272/donard,2015.
https://lwn.net/Articles/636968/,
2015.
| [9] “NVM | Express |     | 1.0e.” | http://www. |     |     |     |     |     |     |     |     |
| -------- | ------- | --- | ------ | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
nvmexpress.org/wp-content/uploads/
|                            |     |      |            |        |        | [23] “FOSS4G                     |     | Benchmark.” |     | https://wiki. |     |     |
| -------------------------- | --- | ---- | ---------- | ------ | ------ | -------------------------------- | --- | ----------- | --- | ------------- | --- | --- |
| NVM-Express-1_0e.pdf,2013. |     |      |            |        |        | osgeo.org/wiki/FOSS4G_Benchmark. |     |             |     |               |     |     |
| [10] S. Kim,               | S.  | Huh, | X. Z. Yige | Hu, A. | Wated, |                                  |     |             |     |               |     |     |
|                            |     |      |            |        |        | [24] “True                       |     | Marble.”    |     | http://www.   |     |     |
E.Witchel,andM.Silberstein,“GPUnet:Network-
unearthedoutdoors.net/global_data/
| ing Abstractions |     | for | GPU Programs,” | in  | OSDI 14, |     |     |     |     |     |     |     |
| ---------------- | --- | --- | -------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
true_marble/.
pp.6–8,USENIX,2014.
[25] VMWare,“vRealizeLogInsight.”http://www.
[11] “Fail2Ban.”www.fail2ban.org/.
vmware.com/products/vrealize-log-
[12] “mdadm - manage MD devices aka Linux Soft- insight.html.
| ware | RAID.” | https://www.kernel.org/ |     |     |     |                     |     |                   |     |     |               |     |
| ---- | ------ | ----------------------- | --- | --- | --- | ------------------- | --- | ----------------- | --- | --- | ------------- | --- |
|      |        |                         |     |     |     | [26] G. Vasiliadis, |     | M. Polychronakis, |     |     | S. Antonatos, |     |
pub/linux/utils/raid/mdadm/.
|     |     |     |     |     |     | E. P. | Markatos, | and | S. Ioannidis, |     | “Regular | ex- |
| --- | --- | --- | --- | --- | --- | ----- | --------- | --- | ------------- | --- | -------- | --- |
[13] Anandech, “AMD announces Radeon-Pro SSG.” pression matching on graphics hardware for intru-
http://www.anandtech.com/show/ sion detection,” in International Workshop on Re-
10518/amd-announces-radeon-pro- centAdvancesinIntrusionDetection,pp.265–283,
ssg-fiji-with-m2-ssds-onboard,2016.
Springer,2009.
178    2017 USENIX Annual Technical Conference USENIX Association

[27] Antonio Torralba, Robert Fergus and William T
Freeman, “80 Million Tiny Images: A Large Data
Set for Nonparametric Object and Scene Recogni-
tion,” Pattern Analysis and Machine Intelligence,
IEEE Transactions on, vol. 30, no. 11, pp. 1958–
1970,2008.
[28] “Benchmarking GPUDirect RDMA on Modern
Server Platforms.” https://devblogs.
nvidia.com/parallelforall/
benchmarking-gpudirect-rdma-on-
modern-server-platforms/,2014.
[29] M. Silberstein, B. Ford, I. Keidar, and E. Witchel,
“GPUfs: Integrating a File System with GPUs,”
TOCS,vol.32,no.1,p.1,2014.
[30] OpenCAPI. http://opencapi.org/.
[31] Cache Coherent Interconnect for Accelerators
(CCIX). http://www.ccixconsortium.
com/.
USENIX Association 2017 USENIX Annual Technical Conference 179