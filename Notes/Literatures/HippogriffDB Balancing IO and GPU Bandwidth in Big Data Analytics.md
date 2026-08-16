# HippogriffDB

**Source**: HippogriffDB.pdf
**Format**: .pdf

---

| HippogriffDB: |     | Balancing |      | I/O       | and | GPU | Bandwidth |     | in  | Big |
| ------------- | --- | --------- | ---- | --------- | --- | --- | --------- | --- | --- | --- |
|               |     |           | Data | Analytics |     |     |           |     |     |     |
Jing Li Hung-Wei Tseng Chunbin Lin Yannis Papakonstantinou Steven Swanson
∗
Department of Computer Science and Engineering, University of California, San Diego
jil261@ucsd.edu h1tseng, chunbinlin, yannis, swanson @cs.ucsd.edu
|     |     | {   |     |     |     |     | }   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ABSTRACT parallelism, commercial availability, and full-blown programma-
bility.Previouswork[10,20,39,41]provedthefeasibilityofaccel-
| As data sets | grow and conventional | processor | performance | scal- |                            |     |     |                            |     |     |
| ------------ | --------------------- | --------- | ----------- | ----- | -------------------------- | --- | --- | -------------------------- | --- | --- |
|              |                       |           |             |       | eratingdatabasesusingGPUs. |     |     | ExperimentsshowthatGPUscan |     |     |
ingslows,dataanalyticsmovetowardsheterogeneousarchitectures
|                                                            |     |     |     |     | accelerateanalyticalqueriesbyupto27 |     |     |     | [15,17,41]. |     |
| ---------------------------------------------------------- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- | ----------- | --- |
| thatincorporatehardwareaccelerators(notablyGPUs)tocontinue |     |     |     |     |                                     |     |     |     | ×           |     |
However,existingGPU-accelerateddatabasesystemssufferfrom
| scalingperformance. | However,existingGPU-baseddatabasesfail |     |     |     |      |              |              |             |               |           |
| ------------------- | -------------------------------------- | --- | --- | --- | ---- | ------------ | ------------ | ----------- | ------------- | --------- |
|                     |                                        |     |     |     | size | limitations: | they require | the working | set to fit in | GPU’s de- |
todealwithbigdataapplicationsefficiently:theirexecutionmodel
suffers from scalability limitations on GPUs whose memory ca- vice memory. With this limitation, existing GPUs cannot handle
pacityislimited;existingsystemsfailtoconsiderthediscrepancy terabyte-scaledatabasesthatarebecomingcommon[8,21].
between fast GPUs and slow storage, which can counteract the ScalingupGPU-accelerateddatabasesystemstoaccommodate
benefitofGPUaccelerators. datasetslargerthanGPUmemorycapacityischallenging:
| In this paper, | we propose HippogriffDB, | an  | efficient, | scalable |     |     |     |     |     |     |
| -------------- | ------------------------ | --- | ---------- | -------- | --- | --- | --- | --- | --- | --- |
1. Thelowbandwidthofdatatransferinheterogenoussys-
| GPU-acceleratedOLAPsystem. |     | Ittacklesthebandwidthdiscrep- |     |     |     |                  |     |             |              |          |
| -------------------------- | --- | ----------------------------- | --- | --- | --- | ---------------- | --- | ----------- | ------------ | -------- |
|                            |     |                               |     |     |     | tems counteracts | the | benefit GPU | accelerators | provide. |
ancyusingcompressionandanoptimizeddatatransferpath.Hippo- Whilethemainmemoryhasalwaysbeenfast(upto8GB/sec
griffDB stores tables in a compressed format and uses the GPU when transferring to a K20 GPU) and new storage devices
fordecompression,tradingGPUcyclesfortheimprovedI/Oband- likesolidstatedrives(SSDs)areimprovingperformance(up
width. To improve the data transfer efficiency, HippogriffDB in- to2.4GB/sec[1]),thebandwidthdemandofGPUdatabase
troduces a peer-to-peer, multi-threaded data transfer mechanism, operatorsisstillhigherthantheinterconnectbandwidthand
directlytransferringdatafromtheSSDtotheGPU.HippogriffDB thestoragebandwidth.AsshowninTable1,typicaldatabase
adoptsaquery-over-blockexecutionmodelthatprovidesscalabili- operatorsandqueriescanrun29 82
fasterthantheSSD
| tyusingastream-basedapproach.Themodelimproveskerneleffi- |     |     |     |     |     |                 |         |        | − ×                 |         |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --------------- | ------- | ------ | ------------------- | ------- |
|                                                          |     |     |     |     |     | read bandwidth. | Without | carefu | l des ign, the slow | storage |
ciencywiththeoperatorfusionanddoublebufferingmechanism.
wouldunder-utilizehigh-performanceGPUaccelerators.
WehaveimplementedHippogriffDBusinganNVMeSSD,which
2. Movingdatabetweenstoragedevicesandmultiplecom-
talksdirectlytoacommercialGPU.Resultsontwopopularbench-
putingdevicesaddsoverhead.Thedatatransfermechanis-
marksdemonstrateitsscalabilityandefficiency.HippogriffDBout- minexistingsystemscanbebothslowandcostly. Itsingle-
performsexistingGPU-baseddatabases(YDB)andin-memorydata threadedlymovesdatafromthedatasourcetotheGPUvia
analytics(MonetDB)by1-2ordersofmagnitude. CPU and the main memory, failing to utilize the internal
parallelisminsidemodernSSDs.Thisalsoaddsindirections
andconsumespreciousCPUandmemoryresources,which
1. INTRODUCTION thesystemcoulduseforothertasks.Recentwork[39]shows
AspowerscalingtrendspreventCPUsfromprovidingscalable that this detour can take over 80% of the execution time
performance [11,13,16], database designers are looking to alter- in typical analytical workloads and can cause the transfer
natecomputingdevicesforlargescaledataanalytics, asopposed bandwidthtobelessthan40%ofthetheoreticalpeak.
toconventionalCPU-centricapproaches. Amongthem, Graphics 3. CurrentexecutionmodelsofGPU-databasesdonotsuit
ProcessingUnits(GPUs)attractthemostdiscussionforitsmassive the architecture of GPUs and cause scalability and per-
|     |     |     |     |     |     | formance | issues. The | query execution | models | in existing |
| --- | --- | --- | --- | --- | --- | -------- | ----------- | --------------- | ------ | ----------- |
GPUdatabases[20,40]areneitherefficientnorscalable.They
| ∗Hung-Wei Tseng | is now an assistant | professor in | the Department | of  |     |     |     |     |     |     |
| --------------- | ------------------- | ------------ | -------------- | --- | --- | --- | --- | --- | --- | --- |
requirethattheworkingsetfitinthesmallGPUdevicemem-
| ComputerScience,NorthCarolinaStateUniversity. |     |     | Hiscurrentemailis |     |     |                              |     |     |                         |     |
| --------------------------------------------- | --- | --- | ----------------- | --- | --- | ---------------------------- | --- | --- | ----------------------- | --- |
|                                               |     |     |                   |     |     | ory(usuallylessthan20GB[2]). |     |     | Besides,theintermediate |     |
hungweitseng@ncsu.edu.
|     |     |     |     |     |     | results | that the current | models produce | put pressure | on the |
| --- | --- | --- | --- | --- | --- | ------- | ---------------- | -------------- | ------------ | ------ |
alreadyscarceGPUmemory.
Toaddresstheabovechallenges,weproposeHippogriffDB,an
|     |     |     |     |     | efficient, | scalable | heterogeneous | data | analytics engine. | The pri- |
| --- | --- | --- | --- | --- | ---------- | -------- | ------------- | ---- | ----------------- | -------- |
This work is licensed under the Creative Commons Attribution- mary issue HippogriffDB tackles is the low performance caused
NonCommercial-NoDerivatives4.0InternationalLicense. Toviewacopy by the bandwidth mismatch between fast computation and slow
ofthislicense,visithttp://creativecommons.org/licenses/by-nc-nd/4.0/.For I/O. HippogriffDB fixes it with compression and optimized data
anyusebeyondthosecoveredbythislicense,obtainpermissionbyemailing
|     |     |     |     |     | transfermechanisms. |     | Thestream-basedexecutionmodelitadopts |     |     |     |
| --- | --- | --- | --- | --- | ------------------- | --- | ------------------------------------- | --- | --- | --- |
info@vldb.org.
makesHippogriffDBthefirstGPU-baseddatabasesystemthatsup-
ProceedingsoftheVLDBEndowment,Vol.9,No.14
|     |     |     |     |     | portsbigdatacubequeries. |     | HippogriffDBusesanoperatorfusion |     |     |     |
| --- | --- | --- | --- | --- | ------------------------ | --- | -------------------------------- | --- | --- | --- |
Copyright2016VLDBEndowment2150-8097/16/10.
1647

| Operation | Throughput |     | Description |     |     |     |     |     |     |     |     |     |     |
| --------- | ---------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Data Transfer
SSBM-Q1.1 61.8GB/s Q1.1 in the Star Schema Benchmark [28]. The output GPU Kernel
Manager
|     |     |     | queryincludesthreeselections,onejoinandone |     |     |     |     |     |     |     |     | Manager |     |
| --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- |
SQL
|           |          |     | aggregation. |             |        |                |     | CPU |     |     |     |     |     |
| --------- | -------- | --- | ------------ | ----------- | ------ | -------------- | --- | --- | --- | --- | --- | --- | --- |
| SSBM-Q4.1 | 31.2GB/s |     | Q4.1         | in the Star | Schema | Benchmark. The |     |     |     |     |     |     |     |
queryincludesthreeselections,fourjoinandone
data
|           |          |     | aggregation. |          |              |                  |     |          |     |     |     | I/O Buffer |     |
| --------- | -------- | --- | ------------ | -------- | ------------ | ---------------- | --- | -------- | --- | --- | --- | ---------- | --- |
| TableJoin | 21.8GB/s |     |              |          |              |                  |     |          |     |     |     | Manager    |     |
|           |          |     | A 100        | MB table | joins a 1 GB | table using hash |     | Database |     |     |     |            |     |
join.Bothtablescontaintwocolumnsandthetwo
|     |     |     |     |     |     |     |     | Device (Memory/SSD) |     |     |     | GPU |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- |
columnsare4-byteintegers.
| SSD Read  | 0.75GB/s |     | SequentiallyreaddatafromanNVMeSSDwith32 |     |                        |     |     |          |                                   |     |     |     |     |
| --------- | -------- | --- | --------------------------------------- | --- | ---------------------- | --- | --- | -------- | --------------------------------- | --- | --- | --- | --- |
|           |          |     |                                         |     |                        |     |     | Figure1: | SystemarchitectureofHippogriffDB. |     |     |     |     |
| inYDB[39] |          |     | MBastheI/Osize.                         |     | Weadoptasimilarwayused |     |     |          |                                   |     |     |     |     |
in[39].
analyticaldatabase(YDB[41]),usingtwopopularbenchmarks(the
|          |     |            |            |     |                    |        | Star Schema | Benchmark                               | [28] | and the | Berkeley | Big | Data Bench- |
| -------- | --- | ---------- | ---------- | --- | ------------------ | ------ | ----------- | --------------------------------------- | ---- | ------- | -------- | --- | ----------- |
| Table 1: | The | throughput | of running |     | essential database | opera- |             |                                         |      |         |          |     |             |
|          |     |            |            |     |                    |        | mark[31]).  | HippogriffDBoutperformsMonetDBbyupto147 |      |         |          |     |             |
tions/queries on a GPU and transferring data to the GPU. There’s a ×
|     |     |     |     |     |     |     | andYDBbyupto10 |     | . ResultsalsoshowthatHippogriffDBcan |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------------------------------------ | --- | --- | --- | --- |
bigbandwidthmismatchbetweenGPUprocessinganddatatransfer.
|     |     |     |     |     |     |     | scaleuptosupportterabyte-scaledatabasesandouroptimizations |     | ×   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
Results
|     |     |     |     |     |     |     | canhelpachieveupto8 |     | performanceimprovementoverall. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | ------------------------------ | --- | --- | --- | --- |
mechanismtoaggressivelyeliminatetheintermediateresultssince ×
|     |     |     |     |     |     |     | HippogriffDBmakes |     | thefollowingcontributions: |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | -------------------------- | --- | --- | --- | --- |
thepenaltyofcachemissesiscostlyontheGPU.
1. HippogriffDBimprovestheperformanceofGPU-baseddata
HippogriffDBstoresthedatainacompressedformatanddecom-
analyticsbyfixingthebandwidthmismatchbetweenthefast
pressesthemontheGPU,tradingGPUcomputationcyclesforthe
GPUandslowI/O,usingadaptivecompression.
| improved | bandwidth. | It  | utilizes | the massive | computation | power |     |     |     |     |     |     |     |
| -------- | ---------- | --- | -------- | ----------- | ----------- | ----- | --- | --- | --- | --- | --- | --- | --- |
2. HippogriffDBimprovesthedatatransferbandwidthandre-
| of the GPU   | to decompress |     | data,        | turning | the bandwidth | gap into    |        |             |     |              |                |     |          |
| ------------ | ------------- | --- | ------------ | ------- | ------------- | ----------- | ------ | ----------- | --- | ------------ | -------------- | --- | -------- |
|              |               |     |              |         |               |             | source | utilization | by  | implementing | a peer-to-peer |     | datapath |
| the improved | bandwidth.    |     | HippogriffDB |         | tailors the   | compression |        |             |     |              |                |     |          |
thateliminatesredundantdatamovementsinheterogeneous
| methods | to fit better | into | the GPU | architecture. | It  | supports com- |     |     |     |     |     |     |     |
| ------- | ------------- | ---- | ------- | ------------- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- |
computingsystems.
| bination  | of multiple | compression |              | methods | to boost | the effective |       |            |             |            |             |                   |           |
| --------- | ----------- | ----------- | ------------ | ------- | -------- | ------------- | ----- | ---------- | ----------- | ---------- | ----------- | ----------------- | --------- |
|           |             |             |              |         |          |               | 3. We | identify   | the problem | of optimal | compression |                   | selection |
| bandwidth | for data    | transfers.  | HippogriffDB |         | employs  | a decision    |       |            |             |            |             |                   |           |
|           |             |             |              |         |          |               | to be | an NP-hard | problem     | and        | provide     | a 2-approximation |           |
modeltoselecttheappropriatecompressioncombinationthatbal-
ancestheGPUkernelthroughputandtheI/Obandwidth.Weprove greedyalgorithmforit.
theoptimalcompressionselectiontobeanNP-hardproblemand 4. HippogriffDBusestheoperatorfusionmechanismtoavoid
propose a 2-approximation greedy algorithm for it. For storage intermediateresultsandtoimprovekernelefficiency.
withmassivecapacity,HippogriffDBadoptsadaptivecompression: 5. HippogriffDBusesquery-over-block,astreamingexecution
model,toprovidenativesupportforbigdataanalytics.
| it maintains | multiple | compressed |     | versions | and then | chooses the |     |     |     |     |     |     |     |
| ------------ | -------- | ---------- | --- | -------- | -------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
bestcompressionschemedynamicallysothatdifferentqueriescan 6. HippogriffDBoutperformsstate-of-the-artdataanalyticssys-
benefitfromdifferentcompressionschemes. temsby1-2ordersofmagnitude,andexperimentresultsdemon-
Furthermore, HippogriffDBtacklesthelowdatatransferband- strateHippogriffDB’sscalability.
widthbyusingamulti-threaded,peer-to-peercommunicationmech-
ThepaperprovidesanoverviewofHippogriffDBinSection2.
| anism (Hippogriff) |     | between | the | data source | (e.g., | SSD and NIC) |            |             |     |               |      |          |         |
| ------------------ | --- | ------- | --- | ----------- | ------ | ------------ | ---------- | ----------- | --- | ------------- | ---- | -------- | ------- |
|                    |     |         |     |             |        |              | We discuss | compression | and | the optimized | data | transfer | in Sec- |
andtheGPU.ThegoalistosolvetwoproblemsintheI/Omecha-
|                 |          |            |     |            |           |                | tion3and4.                             | Section5discussestheexecutionmodelinHippo- |     |     |     |                 |     |
| --------------- | -------- | ---------- | --- | ---------- | --------- | -------------- | -------------------------------------- | ------------------------------------------ | --- | --- | --- | --------------- | --- |
| nism of the     | existing | GPU-based  |     | analytical | engines   | [39]: (1) data |                                        |                                            |     |     |     |                 |     |
|                 |          |            |     |            |           |                | griffDB.Section6and7evaluatethesystem. |                                            |     |     |     | WecompareHippo- |     |
| transfer relies | on       | CPU/memory |     | to forward | the input | (2) single-    |                                        |                                            |     |     |     |                 |     |
griffDBwithrelatedworkinSection8andSection9concludes.
threadingunder-utilizesthemultipledatatransferhardwarecompo-
nentsinsidetheSSD.Toaddressthesetwoproblems,Hippogriff-
2. SYSTEMOVERVIEW
DBreengineersthesoftwarestacksothatthedatabasecandirectly HippogriffDBusesdatacompressionandoptimizeddatamove-
transfer data from the SSD to the GPU. Furthermore, Hippogriff ment,combinedwithastream-basedqueryexecutionmodel,tode-
| introduces | multi-threaded |     | data fetching |     | to take advantage | of the |     |     |     |     |     |     |     |
| ---------- | -------------- | --- | ------------- | --- | ----------------- | ------ | --- | --- | --- | --- | --- | --- | --- |
liveranefficient,scalablesystem.Thissectionprovidesanoverview
massiveparallelisminsidemodernSSDs.
|              |        |           |                   |     |               |            | of the system    | design,    | the | data compression | mechanism,       |     | the op-  |
| ------------ | ------ | --------- | ----------------- | --- | ------------- | ---------- | ---------------- | ---------- | --- | ---------------- | ---------------- | --- | -------- |
| HippogriffDB |        | achieves  | high scalability, |     | high kernel   | efficiency |                  |            |     |                  |                  |     |          |
|              |        |           |                   |     |               |            | timized transfer | mechanism, |     | and the          | query-over-block |     | model to |
| and low      | memory | footprint | by adopting       | a   | new execution | strategy,  |                  |            |     |                  |                  |     |          |
supportscalablebigdataanalytics.
| called query-over-block. |     |     | It contains | two | parts. First, | Hippogriff- |     |     |     |     |     |     |     |
| ------------------------ | --- | --- | ----------- | --- | ------------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
DBstreamsinputinsmallblocks, leadingtohighscalabilityand 2.1 Systemarchitecture
low memory footprint. HippogriffDB adopts double buffering to HippogriffDB targetslargedatabasesandstoresdatabasetables
supportasynchronousdatatransfer. Second,thequery-over-block inthemainmemoryortheSSDinthecurrentimplementation. It
model reduces the intermediate results using an operator fusion containsthreemajorcomponents.
mechanism: itfusesmultipleoperatorsintoone,turningtheinter- DataTransferManager. Thedatatransfermanagermovesthe
mediateresultspassingintothelocalvariablespassinginsideeach requested data from the main memory/SSD to the GPU kernel.
GPUthread. It uses a multi-threaded, peer-to-peer communication mechanism
We implemented HippogriffDB on a heterogeneous computer betweentheGPUandtheSSDtofurtherimprovethedatatransfer
| system with | an  | NVIDIA | K20 and | a high-speed | NVMe | SSD. As | bandwidth. |     |     |     |     |     |     |
| ----------- | --- | ------ | ------- | ------------ | ---- | ------- | ---------- | --- | --- | --- | --- | --- | --- |
an initial look of HippogriffDB design, we focus on star schema I/OBufferManager. HippogriffDBmaintainsacircularinput
queries. We compare it with a state-of-the-art CPU-based ana- bufferintheGPUmemory.ItworkswiththeDataTransferManager
lytical database (MonetDB [9]) and a state-of-the-art GPU-based tooverlapdatatransferandqueryprocessing:anI/Othreadandthe
1648

SSD GPU CPU Main Memory
CPU Main memory (1) Create file descriptors
(2) Allocate main memory space
(3) Issue read commands
(4) Transfer data from the storage device to the main memory
(5) Allocate GPU device memory
(6) Transfer data from the main memory to the GPU memory
PCIe (b)
Interconnect
(1) Create file descriptors
(2) Allocate GPU memory space
(3) Issue read commands
SSD GPU (4) Transfer data from the storage device to the GPU memory
Control Data
(a) (c)
Figure2: (a)TheconventionalheterogenousplaStSfoDrm,(bG)PthUeprocCePssUofMmaionv MinegmodraytabetweentheGPUandtheSSDinexistingsystems,and(c)
Figure2:(a)TheconventionalGPGPUplatformand(b)theprocessofmovingdatabetweentheGPUandtheSSDonthisplatform
directdataaccessinHippogriffDB.
GPUkernelactastheproducerandconsumerrespectivelytocopy storage device and the GPU is the main performance bottleneck.
datafromstoragetotheGPU.HippogriffDBalsomaintainsaresult As shown in Table 1, typical database operators and queries can
bufferinGPU’smemory,iftheresultcanfitintheGPUmemory. run29 82 fasterthantheSSDreadbandwidth.
lo_revenue 𝜎 lo_revenue’ Comp−ared×withDtAhTeEexisting query processing model used on
quloe G _rqi P eu U asntoi K tny e t r h n e e ≥r l e M cesi a evl n e_ a vde g cd e _a r lo . ta. T H he ipp G o P g U riff k D er B n𝜎e s l up mlo p a_ o nr r ea t v s gene q ur u e’ e e’ r v i a e l s ua th te a s t G S P S E U D x , s i t s t h o ti i n s s g t m o h r o e i d g d h e a l - t p Dh a A e a , T r s b E fo _ u sK r e t E m v t Y h e a e r n a N c l e a V h d M e v t a e e n r s t o a t g a g e n e n d s o : a u rd ss is ys in te h m er s e u n s tl e y N in V e M ffi e c - i b en as t ed
colon_tpaairntkseyelection,join𝜎,aggrelog_aptairotkne,y’andsortoperators. for 1 m . o It vi e n n g ab d l a e t s a q b u e e t…w r…y ee p n ro th ce e s S si S n D g o an n d p t a h r e tia G l P i U np . u F t, ig a u s re op 2 p (b o ) se il d lu t s o -
thewholetable,whichhasgreatsignificanceonincreasethe
Trpa
F
_np
ig
safr
u
tek
r
re
e
yM
1
a
s
n
h
a
o
g
w
e
s
r
h
p
o
r
w
e𝜎p
H
ar
i
e
p
s
p
pt
o
h_
g
pe
r
a
i
rr
f
tek
f
le
D
eyv’
B
an
p
t
ro
c
c
o
e
lu
ss
m
ef
n
sil
s
tae
f
rq_
o
vu
r
eec
a
rtoy
g
r.
iv
T
e
h
n
e
q
D
u
a
er
ta
y lineo
t
m r
r
d
a
a e
t
i r
e
n
s
m s
t
c
h
e a
e
m la
p
o b
r
r i
oD
y li
bi
t (
ml
y s
e
t
em
o e
n
f p
s:i
q …
o
1
t
u …
nh
- e 4
et
r )
a
y ,
sb
a
yl
p
e
n
s
r
t
d o
e
c
m
t e h s e
fi
s n i
r
n
s
c g
t
o . p
m
ie
o
s
ve
th
s
e
d
m
at
t
a
o
f
t
r
h
o
e
m
GP
th
U
e
(
S
s
S
te
D
p5
to
-
DATEKE2Y. Iteliminatesredundantandunnecessaryintermediateresults
byp_rceattreigeovryingda=tafrsoelm_veeci_tpherthemainmemo𝜎ryopr_tbhraendS1S’’D.Itthen
PART
6
K
)
E
.
Y
Pr
a
i
n
o
d
r
m
wo
o
r
ll
k
if
[
y
3
t
8
h
]…
e
…i
m
nd
e
i
m
ca
o
te
ry
s
p
th
re
a
s
t
s
s
u
o
r
m
eo
e
n
a
G
pp
P
li
U
ca
.
tions spend more
wop_rkbrsanwd1iththeI/OB𝜎ufferMpa_nbraagnde1r’tosendrelevantcolumnsfrom than 80% ofDitmheeinrsitoimn teabcloepying data from main memory to the
SUPPKEY
the main memory/SSD to the input buffer in the GPU memory. 3G.PU.DInAaTddAitioCnOStoUMPwPLaYPstRingEbSanSdIwOidNth,thisapproachalsowastes
FTighuer G e P 4 U : S K ch e e rn m e a l o M f a Q n u a e g r e y r 1 t g h e e n n er e a v t a e l d ua b t y es Y t D h B e . qT I uy t pe c er re ye a .q t u e Wa s ti l ho a ne rg nh e eq i r n eu. t e e r r- y ORDE m RK e H E m Y ip o p r o y g c r a if p f a D c B ity aSlU a le n PvP d KiaE C Yte P s U th p e er b f a o n r d m w a i n d c t e h , m bo is th ma o t f ch wh b i y ch us c i o n u g ld da b ta e
evaluationfinishes,theGPUKernelManagerwillsendtheresult puttomoreproductiveuses.
mediateresults(greyboxes). ItalsorequiresallrelevantcolumnsinGPU compressionandtrad…ingGPUcyclesforimprovedbandwidth.The
backtotheoutputbuffer. Furthermore, theLinuxNVMedriverdoesnotfullyutilizethe
memory,limitingthescalabilityofthesystem. massiveparallelisminsideGPUcanproduceresultinathroughput
There is a huge bandwidth mismatch between the GPU kernel (b) peaxraalmlelpislme tshcahteSmSDas offer, since it is single threaded. This has
thatisoneorderofmagnitudehigherthanthedatatransferband-
andI/O.Withoutcarefuldesign,theslowI/Otransferwillcounter- large negative impacts on performance: Our experiments in Sec-
executionplanYDB[45]generatesinFigure4. Theexistingmod- width memory or SSD can deliver, creating an imbalance among
actthespeedupthathardwareacceleratorsprovide. HippogriffDB tion 7.1 show that a SSD-based version of YDB [38] can only
el that YDB uses , “operator at a time and bulk execution” [10], differentcomponentsinsideaGPU-basedanalyticssystem.Hippo-
alleviatesthemismatchbystoringdatainacompressedformand achieve 30% of the peak performance if we store data in SSD-
evaluates each operation (e.g. selection of quantity<25) to griffDBclosesthegapusingcompression: itcompressesdatabase
usingGPUcyclesfordecompression. Tofurtherimprovephysical s. Hippogriff addresses these problems. Hippogriff provides
completion over its entire input (e.g. lo quantity) and send- tablesandusestheGPUtodecompressthem,effectivelyconvert-
I/Obandwidth,HippogriffDBremovestheredundantdatatransfers multi-threaded,peer-to-peerdatamovementbetweenSSDsandG-
s the whole intermediate results to the upcoming operator (e.g. ing GPU compute capabilities into improved transfer bandwidth.
byimplementingapeer-to-peercommunicationfromstoragetothe PUs. As Figure 2(c) shows, Hippogriff only needs to obtain the
lineorder1part). Inthisway,HippogriffDBimprovestheI/Obandwidthefficiency
GPU.WeprovideanoverviewfortheminSection2.2. fileinformationandpermissionfromtheCPUprograminStep(1).
Thequery-over-blockmodelgeneratesthreeoperatorsforQuery andincreasesthesystemthroughput.
Wealsonoticetheinefficiencyandthescalabilitylimitationof AfterthesystemallocatesspaceintheGPU’smemory(Step(2)),
1,asshowninthedashed,rectangularboxinFigure4.Twoofthem Inthissection,wefirstintroducethecompressionmethodsthat
currentqueryexecutionmodels.HippogriffDBfixesitbyintroduc- HippogriffissuesNVMecommandswithGPUmemoryaddresses
arethenewselectionoperatorswhosefunctionalitiesincludetradi- HippogriffDB adopts and then analyze the compression ratio of
inganewquerymodelinGPUprocessing.Weprovideanoverview asthesourcesordestinationsinStep(3)andallowsthedatatoflow
tionalselection(e.g. quantity<25),projection. Theotherone them. Afterthat, wediscusshowtoefficientlycombinedifferent
ofitinSection2.3. directlybetweentheSSDandtheGPUwithoutusingmainmem-
isthenewjoinoperatorwhichcoversthefunctionalitiesofthejoin compressionmethodstogenerateacompressionplan.
ory(Step(4)). Hippogrifffurtherexploitsparallelismbycreating
in2.th2eorOigipnatlipmlainz(ien.gg. ldianteaormdeorv1empaernt)tandtheaggregation
3m.u1ltiplGetPhrUea-dbsatosuetdilizceoimdlepNrVesMseioqnuemueseftrhomodasllprocessors
opeTrahteiopnr(ime.gar.yγobstacleforbuilding).anefficient, GPU-based, big
p.brand1,sum(lo.revenue) inHthieppsoygstreifmfD.B supports several compression methods to maxi-
dataanalyticssystemisthat,inmodernsystems,GPUscanprocess
Cdoamtap6a-r1i2sonofafstthereethxaisntinagtympoicdaellastnodraqgueesryys-toevmer-cbalnocpkr.ov Y i D de B’ i s t.
mizHeitphpeoegfrfieffcitmiveplbeamnednwtsidththesbeeftewaetuenretshbeyGfuPlUlyalenvdetrhaegisntgortahgeepdeee-r-
qHueiprypopglrainff × DisBneaidthderersssceaslathbilseinmobraelfafinccieenbtyfoexrcthwaongreinagsoansp.leFnitrisfut,l vtoic-ep.eeIrnftehaistusruebsstehcattioPnC,Iweepirnotvrioddeuscaentdhocsoemcboimnipnrgestshieomnmweitthhoidns-
threissopularcnee(vGalPuUatecsomeapcuhteopceyrcalteiso)nfotorcaosmcaprlceetiroensoouvrecreit(sefefnetcitrieveindpautta
atneldliagneanltyszcehtehdeuclionmgporfesIsOiotnrarnastifoertsh.eyPCcaIensaucphpieovrets. directtransfer
atnrdanssefnedrsbtahnedrwesidutlhts).oIftthacehpireevveisouthsisopuesrinatgortw(io.et.e f c i hn l i t q e u r es v : ector)
ofHdiaptpaogbreitfwfDeeBncParCeIfeulldyevcihcoeoss,easscolomnpgreasssiboonthmedtehvoidcsesbassuepdpoornt
toth1e.nIetxatdoopptesraatmoru[l1ti0-t]h.reInadtehdis,pweaeyr-,ttoh-epepelrancogmemneurnatiecsatliaorngmeeinc-h-
tiwto–carliltetrhiaat:i(s1)retqhueirdeedcoismtphraetss1i)onthaelgdoersittihnmatifiontsdweivtihcetheexGpoPsUe’as
termediaanteismres(uHltisp,ptohgartifcfo)sotvperretchieouPsCmIeeimntoerrycornesnoeucrtcteosmanodveaddadtsa
vpeocrttoiorinzaotfiointsnoantu-breo.ar(d2)mceommoprryesinsiothneisPCcoIemapdadtirbelseswspitahcethaenedxe2-)
latency,dsiriencctelyacfcroesmsinthgegsltoobraalgmeesmysoterymo(ni.Ge.,PUanisSSslDow).toSethceonGdP,iUt
ctuhteiosnoumrcoededle.viWceedarlisvoermdaikreectasftehwescohuarncgeedsetvoictehetoextriastnisnfgercodmata-
requireswtihthaotuatllsrheulettvlianngtddaattaabtahsreoucgohlummanisnmmuesmtfiotryin.toGPUmem-
ptoresthsiaotnadmdertehsosdvsisaodtihreacttGmPeUmcoarnyeafcfeccetsisve(lDyMdeAc)o.mGpPreUsssathnedmn.et-
ory[24.5I]t,wsthoircehsltiambiltessthinescyosmtepmresscsaeldabfiolritmy.and uses the GPU to
woTrhkeincotemrfparceessciaorndsmseutphpoodrsttthhaetseHtirpapnosgferirfsfDviBatuhseesGaPrUe:Direct[3]
mechanism.HippogriffextendsthiscapabilitytoSSDs.
Theqdueceorym-opvreesrs-btlhoecmk,meoffdeecltiavdedlyrescsoensvtehretinligmGitaPtUioncsombypufutesincag- RLE(run-lengthencoding):Run-lengthencodingrepresents
H•ippogriffcanalsoleveragetheconventionaldatatransfermech-
multiplpeaobpielirtaietisoinnstoinetfofeocnteivaenddaptarotrvaindsinfegrsbtraenadmw-ibdathse.doperators. runsofdata(consecutivenumbersofthesamevalue)asas-
anisminwhichdataflowsfromonedevice,tomainmemory,and
Combining multiple operators allows the system to avoid materi- ingledatavalueandcount[39].HippogriffDBdecompresses
2.2.1 Hippogriff then out to another device. While this path is less efficient, it
alizationofintermediateresultsandpassthedatamoreefficiently byassigningeachrunathreadtoreconstructthecolumn.
canimproveperformanceiftheresourcesrequiredforpeer-to-peer
usinHgipfapsotglroicffaDlBmeemmoprlyo.yTshHeipqpuoegryri-fofv,ear-PbCloIcekdmatoadterlancasfnerprsoccheesds- DICT:DICT(dictionaryencoding)replacesthedatawithits
inupleurttbhlaotceknshiannacesstrbeaanmdiwngidathppbryoaucshin.gInmtuhlitsi-wtharey,adtheidsamnoddpeelesru-tpo--
tran•sfe
c
r
or
a
r
r
e
e
s
o
p
c
o
c
n
u
d
p
in
ie
g
d
r
o
e
r
p
u
re
n
s
a
e
v
n
a
t
i
a
la
ti
b
o
l
n
e.
c
D
on
e
t
p
a
e
i
n
n
d
ed
ing
in
o
a
nt
m
he
ap
s
p
e
i
t
n
o
g
fp
ta
e
b
n
l
d
e
-
.
ing transfers, Hippogriff dynamically chooses which data move-
ppoeretsrddaattaastreatnsslfaerrgemretchhaannitshmesG. PTUhismiesmimorpyocrtaapnatcsitiyncaenidnhGenPcUe- HippogriffDBdecompressesdatabysearchingthemapping
mentchannelorchannelstouse.
imbapsreodvdesatsaybsatseemsyscstaelmabsi,litthye.bandwidthofmovingdatabetweenthe orcalculatingthetranslationfunction.
4
1649

DATE
|                                 |     |     |         |           |          | lo_revenue  |     | 𝜎          | lo_revenue’ |     |                |     |     | DATE     |
| ------------------------------- | --- | --- | ------- | --------- | -------- | ----------- | --- | ---------- | ----------- | --- | -------------- | --- | --- | -------- |
| SELECTSUM(lo.revenue), p.brand1 |     |     | DATEKEY |           |          |             |     |            |             |     | 𝜎 lo_revenue’’ |     |     |          |
|                                 |     |     |         | LINEORDER |          |             |     | sel_vec_lo |             |     |                |     |     | DATE_KEY |
| FROMlineorderlo, part p         |     |     | YEAR    |           | SUPPLIER | lo_quantity | ≥   |            |             |     |                |     |     |          |
W H E R E l o . p a r t k e y =   p . p a r tk e y D A T E K E Y S U P P KE Y … …
|     |     |                                   |         |           |                 | l o _ p a r t k | e y | 𝜎   | lo _ p a r tk e | y ’ |     |     |     |     |
| --- | --- | --------------------------------- | ------- | --------- | --------------- | --------------- | --- | --- | --------------- | --- | --- | --- | --- | --- |
|     | A N | D   l o . q u a n t i t y <   2 5 | P A R T | P A R T K | E Y N A T I O N |                 |     |     |                 |     |     |     |     |     |
P A R T K E Y S U P P K E Y filter_vector   Dimens i o n table
A N D   p . c a t e g o r y =   ' M FGR#12' R E G I O N p _ p a r t k e y p _ p a r tk e y ’ lineorder
GR O U P  B Y p . b r a n d 1 C A T E G O R Y R E V E N U E 𝜎 … …
DATEKEY
|     |     |             | BRAND |            |     | p_category | =   | sel_vec_p |           |     | p_brand1’’ |     |         | ……              |
| --- | --- | ----------- | ----- | ---------- | --- | ---------- | --- | --------- | --------- | --- | ---------- | --- | ------- | --------------- |
|     |     |             |       | (b) Schema |     |            |     |           |           |     | 𝜎          |     | PARTKEY |                 |
|     |     | (a) Query 1 |       |            |     | p_brand1   |     | 𝜎         | p_brand1’ |     |            |     |         |                 |
|     |     |             |       |            |     |            |     |           |           |     |            |     | SUPPKEY | Dimension table |
Figure3:Query1anditscorrespondingschema.
SUPPLY
|     |     |     |     |     |     |     |     |     |     |     | Typeequationhere. |     | ORDERKEY |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | -------- | --- |
Figure 4: Schema of Query 1 generated by YDB. It creates large SUPPKEY
2.2.2 Column-based,compressedtables intermediateresults(greyboxes). Italsorequiresallrelevantcolumnsin …
GPUmemory,limitingthescalabilityofthesystem.
To surpass the physical bandwidth limit that the interconnect (b) example schema
| and | the devices | set, HippogriffDB | stores | database | tables using a |     |     |     |     |     |     |     |     |     |
| --- | ----------- | ----------------- | ------ | -------- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Comparisonoftheexistingmodelandquery-over-block.YDB’s
column-based,compressedformatandtradesGPUdecompression
|     |     |     |     |     |     | queryplanisneitherscalablenorefficientfortworeasons. |     |     |     |     |     | First, |     |     |
| --- | --- | --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | ------ | --- | --- |
cyclesforimprovedeffectivebandwidth.
|     |     |     |     |     |     | thisplangenerateslargeintermediateresults(i.e.filter |     |     |     |     |     | vector), |     |     |
| --- | --- | --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | -------- | --- | --- |
HippogriffDBfollowsthemoderncolumnstoredesignsbyusing
whichcostpreciousmemoryresourcesandreducethequerypro-
implicitvirtual-ids[6],asopposedtoexplicitrecord-ids,toavoid
|          |     |                       |              |        |          | cessingefficiency, |     | sinceaccessingglobalmemoryontheGPUis |     |     |     |     |     |     |
| -------- | --- | --------------------- | ------------ | ------ | -------- | ------------------ | --- | ------------------------------------ | --- | --- | --- | --- | --- | --- |
| bloating | the | size of data storage. | Column-based | format | provides |                    |     |                                      |     |     |     |     |     |     |
slow. Second,itrequiresthatallrelevantdatabasecolumnsfitinto
moreopportunityforcompression,whichfurtherimprovestheI/O
theGPUmemory[41],whichlimitsthesystemscalability.
bandwidth[6,9].
Thequery-over-blockmodeladdressesthelimitationsbyfusing
HippogriffDBstorestablesinacompressedformatandusesGPU
|     |     |     |     |     |     | multipleoperationsintooneandstreamingtheinput. |     |     |     |     |     | Combining |     |     |
| --- | --- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- | --------- | --- | --- |
idlecyclesfordecompressiontofurtherimprovetheeffectiveI/O
multipleoperatorsallowsthesystemtoavoidmaterializationofin-
bandwidth.HippogriffDBallowsbothlight-weightedcompression
termediateresultsandpassthedatamoreefficientlyusingfastlocal
andheavy-weightedcompressionmethods.
variable. Thequery-over-blockmodelcanprocessinputblocksin
Thereisatradeoffbetweenthecompressionaggressivenessand
|     |     |     |     |     |     | a streaming | approach. | In  | this way, | this model | supports | data sets |     |     |
| --- | --- | --- | --- | --- | --- | ----------- | --------- | --- | --------- | ---------- | -------- | --------- | --- | --- |
theGPUefficiency.Aggressivecompressionscanhelpreachbetter
largerthantheGPUmemorycapacity.
compressionratiobutalsobringmorecosttotheGPUdecompres-
sionandslowdowntheGPUaccelerators[6].HippogriffDBadopts 3. DATACOMPRESSION
acost-benefitmodeltoevaluatethetrade-offandtochooseappro- ThemassiveparallelisminsidetheGPUmakestheGPUcompu-
tationthroughputmuchhigherthanthedatatransferbandwidththat
| priate | strategies. | We identify | the optimal | compression | selection |                                   |     |     |     |     |                  |     |     |     |
| ------ | ----------- | ----------- | ----------- | ----------- | --------- | --------------------------------- | --- | --- | --- | --- | ---------------- | --- | --- | --- |
|        |             |             |             |             |           | mainmemoryorSSDscandeliver(upto12 |     |     |     |     | forthemainmemory |     |     |     |
problemtobeanNP-hardproblemandproposea2-approximation
|     |     |     |     |     |     | and30 | fortheSSD),creatinganimbalanceamongdifferentcom- |     |     | ×   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ----- | ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
greedyalgorithm.
×
HippogriffDB observes the limitation of maintaining only one ponents inside GPU-based analytics systems. HippogriffDB nar-
compressionplanandhenceadoptsanadaptivecompressionstrat- rowsthegapusingcompression:itcompressesdatabasetablesand
egy, when possible. One compression plan may benefit certain uses the GPU to decompress them, effectively converting GPU’s
kinds of queries but works poorly on others. HippogriffDB fixes computecapabilitiesintotheimprovedtransferbandwidth. Inthis
thisissuebykeepingmultiplecompressionschemasandchoosing way,HippogriffDBimprovesthethesystemthroughput.
theoptimalonedynamically. We first introduce a compression strategy that minimizes the
overallspacecost.Thenweshowthiskindofaggressivecompres-
2.3 Query-Over-Blockoverview sion strategy may not be GPU-friendly and provide an improved
Thequery-over-blockexecutionmodelenablesthesystemtoef- compressionstrategythatbettersuitstheGPUenvironment.
| ficientlyscalebeyondtheGPUmemorycapacity. |     |     |     | Itcontainstwo |     |     |     |     |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
3.1 Minimizingspacecost(MSC)
aspects:first,itprocessesinputsasstreamsandusesdoublebuffer- HippogriffDB employs run length encoding (RLE) [35], dic-
ingtosupportasynchronousexecution(block-orientedexecution); tionaryencoding(DICT),huffmanencoding(Huffman),anddelta
second,itpacksmultipleoperatorsintooneandsendsintermediate encoding(DELTA)tocompresstables.
Whencompresseddatais
resultsviathread-localvariables(operatorfusionmechanism).
|     |     |     |     |     |     | sent to GPU, | we  | decompress | the data | by using | the | conventional |     |     |
| --- | --- | --- | --- | --- | --- | ------------ | --- | ---------- | -------- | -------- | --- | ------------ | --- | --- |
Exampletodemonstrateexistingmodelsandquery-over-block. methodintroducedin[14]. NoticethatHippogriffDBcanevaluate
Query1(Figure3(a))comparestherevenueforsomeproductsthat thecolumnsencodedbyRLE directlywithoutthedecompression
certain manufacturer makes and whose quantity is less than 25, costasismentionedin[34].
grouped by the product brands (Figure 3(b) shows the database HippogriffDB compresses tables in a heuristic strategy: it first
schema). We show the query execution plan YDB [41] generates sortsthetableusingtwosortkeys(oneprimaryandonesecondary
in Figure 4. The model that YDB uses , “operator at a time and sortkey). Notice, howtochooseprimaryandsecondarysortkey
bulk execution” [9], evaluates each operation (e.g. selection of columns will be discussed later. It applies RLE on the primary
quantity<25)tocompletionoveritsentireinput(e.g.lo quantity) sort key column and DELTA on the secondary sort key column.
and sends the whole intermediate results to the upcoming opera- Forothercolumns,itappliesDICT ifpossible. Thereasonbehind
tor(e.g.lineorder(cid:49)part).
|     |     |     |     |     |     | this heuristic | strategy | is  | discussed | as follows. | To work | with the |     |     |
| --- | --- | --- | --- | --- | --- | -------------- | -------- | --- | --------- | ----------- | ------- | -------- | --- | --- |
Thequery-over-blockmodelgeneratesthreeoperatorsforQuery streaming-basedexecutionmodel,weonlyallowonecolumntobe
1, as shown in the dashed, rectangular box in Figure 4. Two of sorted,andforit,weapplyRLEasitleadstoveryhighcompression
themarethenewselectionoperatorswhosefunctionalitiesinclude ratio.Aswearenotabletointroduceanotherprimarysortkey,we
traditionalselection(e.g. quantity<25),projection. Theother decidetochooseasecondarysortkey. Forthecolumnchosenas
one is the new join operator which covers the functionalities of thesecondarysortkey,wetakeadvantageoftheorderlinessanduse
the join in the original plan (e.g. lineorder(cid:49)part) and the thedeltabetweentwoconsecutiveelementstoencodethecolumn.
aggregationoperation(e.g.γ ). Forothercolumns,weevaluatethedomainsizeandthedistribution
p.brand1,sum(lo.revenue)
1650

Delta Dictionary Algorithm: MSCandGFCAlgorithms
SUPPLYKEY PARTKEY ORDERDATE PARTKEY ORDERDATE
… 0 0 … … 1 1 0 5 … 0 0 1 1 9 9 9 9 7 5 0 0 5 1 0 0 6 2 S R UP L PL E YKEY … 1 5 0 … 0 0 1 1 9 0 5 9 0 7 I O n u p t u p t u : t A :A fa c c o t m ta p b r le es w si i o th n n str c a o te lu g m y n M s, C = = { { M C 1 , 1 . , . . . . , . C , M n } n } ,where
… 0 … 10 … 00 … 00 ……. ( ( 0 1 , , 2 3 5 0 0 0 2 0 ) ) … 2 … 0 ……. 1 ∅ M ; // iis s t t h o e re c s o t m he p o r p e t s i s m i a o l n p m la e n thodfor C i.
1 1 9 9 9 9 9 9 3 3 0 0 0 0 0 1 0 0 (199 … 9, … 3100) 30 1 0 0 00 2 M M B ← ← ∅;M // MBstoresthetemporarybalanceplan
……. ……. ……. 3 min ratio 1;
←
1999 31000 19970506 66 1950 4 fori 1tondo
(a) Original fact table (b) Compressed fact table 5 d i ← dict cmp ratio( i);//computedictionaryencodingratio
← C
Figure5: Exampleofacompressionplan. RLEappliestotheprimary 6 fori
←
1tondo // Ciastheprimarysortkey
sortkeycolumn(SUPPLEYKEY)andDELTAappliestosecondarysortkey 7 forj ← i+1tondo // C jasthesecondarysortkey
column(PARTKEY). TheORDERDATEcolumnusesDICTduetoitslimited 8 r i ← rle cmp ratio( C i );//computeRLEencodingratio
numberofdistinctvalues. 9
r
j ←
delta cmp ratio(
C i
,
C j
);//computeDELTAratio
10 current ratio compute ratio(r i ,r j ,d 1 ,...,d n );
←
11 ifmin ratio>current ratiothen
ofthecolumnandthenchooseadequatecompressionmethodsfor 12 min ratio current ratio;
←
them. 13 [i] RLE; [j] DELTA;
M ← M ←
Forexample,Figure5showshowHippogriffDBcompressesfact 14 foreachk 1,2...n i,j do
∈{ }\{ }
tablebyusingthemethoddiscussedabove.SUPPLYKEYandPARTKEY 15 [k] DICT;
M ←
workastheprimaryandsecondarysortkeyrespectively. Hippo-
16 [i] RLE; [j] DELTA;
griffDBencodesthemusingRLEandDELTArespectively.Hippo- M ← M ←
17 foreachk 1,2...n i,j do
griffDBevaluatesthedomainsizeanddistributionandusesDICT ∈{ }\{ }
18 [k] DICT; //encodeothercolumnswithDICT
toencodeORDERDATE. M ←
Toachievetheminimalspacecost,HippogriffDBenumeratesall 19 r k ← d k;//assignthecompressionratio
primary-secondarysortkeycombinationsoverthecolumnstofind 20 M B ← balance cmp(( C , M ), ∇ = { r k} );
outtheplanthatcomeswiththeminimalspacecost,asshownin 21 current ratio compute ratio( B );
← M
theMSC(MinimizeSpaceCost)algorithm(Figure6).Hippogriff-
//computethecompressionratioofcompressionplan
MB
DBexploresallpossibleprimary-secondarysortkeycombinations
22 ifmin ratio>current ratiothen
(Lines6-7),encodesthemusingRLEandDELTAandcalculates 23 min ratio ← current ratio;
thecompressionratioofthem(Lines8-9). Itthencalculatesthe
24
M←M
B;
overallcompressionratio(Line10)andupdatesthecurrentplanif
25 return ;
itscompressionratioisbetterthanallpreviousplans(Line11-15). M
Functionbalance cmp(( , ), );
3.2 GPU-friendlycompressionplans
//LetDibethedecompressionCbaMndwi∇dthofCi
//LetBIObethedatatransferrate
TheMSCalgorithminSection3.1generatesacompressionplan //LetTGbetheGPUkernelprocessingtime
thatcomeswiththeminimalspacecost,however,theplangenerat- 26 sort(( , ),(sizeof( i ) r i )/D i);
C M C ∗
edmaynotbeGPU-friendlyandmayresultinsuboptimalsystem //sortthecolumnsinnon-decreasingorderof(Ci∗ ri)/Di
throughput. Below,wefirstillustratethepotentialproblemsofthe 27 B ∅;
M ←
MSCalgorithmandthendiscussanalgorithmtogeneratecompres- 28 fori 1tondo
←
sionplansthatoptimizefortheentiresystemthroughput. i n
Using aggressive compressions to achieve minimal space cost 29 new io ← C i ∗ r i /B IO + C i /B IO;
j=1 j=i+1
may result in two problems. First, the decompression task may P i P
overburden the GPU, creating a new form of imbalance and im- 30 new gpu T G + C i /D i;
←
i=1
pairing the system throughput. Second, intensive decompression
31 ifnew io<new gPputhen
operationsontheGPUwoulddegradetheperformanceofHippo-
32 break;
griff, deviating from our original goal of improving data transfer
bandwidth.
33
M B
[i]
←M
[i];
Toavoidtheproblemsdiscussedaboveandmakecompression 34 return B;
M
plansGPU-friendly,werequirethedecompressionprocessdonot
overburdentheGPU.Weformulateacost-benefitanalysisbelow. Figure6:MSCandGFCalgorithms.Codesinthesolidboxare
The cost in this case is the GPU decompression cycles and the MSConly,whilethoseinthedottedboxareGFConly.
benefitisreducingtheamountofdatatransfer.
n
Let T G denote the GPU kernel time to run the queries and r x r i )/B IO >=T G + (C i r i )/D iforacompressionplantobe
denotethecompressionratioofthecompressionmethodusedon i=1 ∗
columnx (assumewehavencolumns). Thecorrespondingcol- GPU-friendly. (cid:80)
umnsizeisC x andD x denotesthedecompressionbandwidthof Wedefinetheoptimalcompressionselectionproblemasfinding
it. SupposethedatatransferrateisB IO. Thetimetotransferthe aplanwhichcanminimizethedatatransfertimewhilemaintaining
n theGPU-friendliness:
compresseddatais:( C i r i )/B IO andthetimetodecompress n
i=1 ∗ min C i r i /B IO
them and run the qu (cid:80) ery is: T G + n (C i r i )/D i. To prevent n (cid:88) i=1 ∗ n
∗
i (cid:80) =1 n s.t. C i ∗ r i /B IO >=T G + (C i ∗ r i )/D i
theGPUfromrunningslowerthanI/O,werequirethat: ( C i ∗ (cid:88) i=1 (cid:88) i=1
i=1
(cid:80)
1651

Theproblemofselectingtheoptimalcompressioncombination 4.2 Adaptivecompression
is proved to be an NP-hard problem by a reduction from the 0- HippogriffDBusesadaptivecompressionstofurtherimprovecom-
1 Knapsack problem [26]. Similar to the greedy algorithm for pressionratiofordatabasesonsecondarystorage.TheGFCalgorithm
the 0-1 Knapsack problem [26], we propose a 2-approximation in Section 3 aims to minimize the table size while maintaining
greedyalgorithm, whichhastwosteps. First, thealgorithmsorts GPU-friendliness,however,itcouldworkpoorlyonsomequeries.
thecolumnsinnon-decreasingorderof(C r )/D i,asshownin In this section, we first show the inefficiency of the fixed com-
i ∗ i
Line26intheGFCalgorithm(Figure6).Second,itgreedilypicks pressionschemeandthendemonstratehowHippogriffDBfixesthe
columnsintheaboveorder(Line28-33).Duetospacelimitations, problemwiththeadaptiveapproach.
weomittheproofoftheNP-hardnessandthe2-approximation.
QUERY 2
| In the | GFC algorithm, | we integrate |     | the GPU-friendliness | re- |     |     |     |     |     |     |
| ------ | -------------- | ------------ | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- |
SELECTSUM(lo.revenue), d.year, p.brand1
| quirementwhengeneratingthecompressionplans. |     |     |     | Givenacom- |     |     |     |     |     |     |     |
| ------------------------------------------- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
FROMlineorder lo, date d, part p, supplier s
pressionplangeneratedbyMSC(Line6-9,16-19),Line20calls
WHERElo.orderdate= d.datekeyAND lo.partkey= p.partkey
thegreedyalgorithmtoconvertitintoanoptimal(approximately AND lo.suppkey= s.suppkey AND lo.quantity< 25
andlocally1)GPU-friendlycompressionplan. AND p.category= 'MFGR#12'  AND s.region= 'AMERICA'
Line21-24com-
GROUP BYd.year, p.brand1
parealllocally-optimalcompressionplansandchoosetheglobally
optimalonetoreturn. The best compression plan for one query can work poorly on
|     |     |     |     |     |     | other | queries. For | Query 2, the | best | compression | plan is as fol- |
| --- | --- | --- | --- | --- | --- | ----- | ------------ | ------------ | ---- | ----------- | --------------- |
4. SSD-SPECIFICOPTIMIZATIONS low: RLE on lo partkey, DELTA on lo supplykey, DICT on
HippogriffDBimprovesthedatatransferfromtheslowSSDsby lo orderdateandlo revenue.However,thisplanworkspoorly
allowingdirectdatatransferfromtheSSDtotheGPUandusinga on the query below, as one column in it is not compressed and
query-adaptivecompressiontofurtherimprovecompressionratio, compressionratioofothercolumnsisnotasgoodasitcouldbe.
tradingstoragespacesfortheimprovedsystemthroughput.
SELECTc.nation, s.nation, d.year, SUM(lo.revenue) as revenue
Inthefollowingsections, wefirstintroducethenewdatapath, FROMcustomer c, lineorderlo, supplier s, date d
Hippogriff.Wethenillustratetheinefficiencyofthefixedcompres- WHERElo.custkey= c.custkey
sionstrategyandbasedonsuchobservation, introducean“adap- AND lo.suppkey= s.suppkey
tive”compressionstrategytoextendthebenefitofcompressionto AND lo.orderdate= d.datekey
AND c.region= ‘ASIA’
awide-rangeofqueries.
AND s.region= ‘ASIA’
| 4.1 Hippogriff |     |     |     |     |     |     | AND d.year>= 1992 and d.year<= 1997 |     |     |     |     |
| -------------- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- | --- |
GROUP BY c.nation, s.nation, d.year
| HippogriffDBreliesonthreecomponents |     |     |     | toprovidethemulti- |     |     |     |     |     |     |     |
| ----------------------------------- | --- | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- |
Tobeadaptivetodifferentqueries,HippogriffDBusestheadap-
threaded,peer-to-peerdatatransfer:
1. Hippogriff API: HippogriffDB provides APIs for program- tivecompressionmechanismbyallowingatabletokeepmultiple
merstospecifythedatatransfersourcesanddestinations. compressedversions. Fortheexampleabove,insteadofhavinga
2. Hippogriff runtime system: it maintains the runtime infor- versionthatappliesRLEonlo partkey,DELTAonlo supplykey,
mationfromallprocessesthatuseHippogriff. DICTonlo orderdateandrevenue,thesystemmayalsomain-
3. Hippogriff: HippogriffDBusesHippogrifftoperformpeer- tainanotherversionwhichappliesRLEonlo supplykey,DELTA
to-peertransfersbetweentheSSDandtheGPU. onlo custkey,DICTonlo orderdateandlo revenue.Hippo-
Compared with existing systems, HippogriffDB improves the griffDBmaymaintainothercompressionversionsaswell.
I/Obandwidthintwoaspects: Duringthequeryprocessing,HippogriffDBexaminesallavail-
HippogriffDBimplementsapeer-to-peerdatatransferpathbe- ablecompressionplansandthencalculatestheoverallcompression
tweentheSSDandtheGPUbyre-engineeringthesoftwarestack ratio for each of them. It will then adopt the one with the best
ofNVMeSSDsasin[4,25,36].Whenthestoragesystemreceives compressionratioforthequeryandsendittotheGPU.
arequestwithaGPUdeviceaddressasthesourceordestination, Supposethenumberofforeign-keycolumns(onwhichHuffman
| the NVMe | software stack | leverages | NVIDIA’s | GPUDirect | [3] to |     |     |     |     |     |     |
| -------- | -------------- | --------- | -------- | --------- | ------ | --- | --- | --- | --- | --- | --- |
andDICT workpoorly)isn,theadaptivestrategywillproduceat
makethesourceordestinationGPUdevicememoryaddressvisible
|             |                                            |                 |     |          |              | mostn(n        | 1)differentcompressionplan.Eachcompressionplan |     |     |     |                |
| ----------- | ------------------------------------------ | --------------- | --- | -------- | ------------ | -------------- | ---------------------------------------------- | --- | --- | --- | -------------- |
| for other   | PCIe devices                               | (by programming |     | the PCIe | base address |                | −                                              |     |     |     |                |
|             |                                            |                 |     |          |              | willcreate     | acompressedversionofthetable,                  |     |     |     | whichcanbeabig |
| registers). | UponthesuccessofexposingdevicememorytoPCIe |                 |     |          |              |                |                                                |     |     |     |                |
|             |                                            |                 |     |          |              | spaceoverhead. | Thefollowingtheoremreducesthespacecostby       |     |     |     |                |
interconnect, ourNVMesoftwarestackissuesNVMereadtothe half,withoutsignificantperformancedegradation.
SSDusingtheseGPUaddressesastheDMAaddressesinsteadof
|             |            |         |      |                |           | THEOREM | 1. GiventwocompressionplanAandB,wherethe |      |         |             |                 |
| ----------- | ---------- | ------- | ---- | -------------- | --------- | ------- | ---------------------------------------- | ---- | ------- | ----------- | --------------- |
| main memory | addresses. | The SSD | then | directly pulls | or pushes |         |                                          |      |         |             |                 |
|             |            |         |      |                |           | only    | difference between                       | them | is that | they switch | the primary and |
datafromortotheGPUdevicememory,withoutfurtherinterven-
secondarysortkey,thecompressionratiodifferenceisasymptoti-
tionsfromtheCPUandthemainmemory.
|                                             |     |     |     |               |     | cally0(AssumethatP |     | = o(N),whereP                     |     | isthecardinalityofthe |     |
| ------------------------------------------- | --- | --- | --- | ------------- | --- | ------------------ | --- | --------------------------------- | --- | --------------------- | --- |
| HippogriffDBusesmulti-threadeddatatransfer. |     |     |     | Itinvokesmul- |     |                    |     |                                   |     |                       |     |
|                                             |     |     |     |               |     | primarysortkeyandN |     | isthenumberofrowsinthefacttable). |     |                       |     |
tiplethreads(4threadsinthecurrentdesign)toreaddatafromSSD.
Toprovidefairsharingamongprocessors,theNVMeSSDperiod- For databases with large number of foreign key columns, we
ically polls the software-maintained NVMe command queue for trade slight compression degradation for big space efficiency im-
eachprocessor.Asaresult,theSSDcanunder-utilizebothinternal
|            |                    |     |         |                      |     | provement.    | Insteadofenumeratingallprimary-secondarysortkey |                |     |         |                  |
| ---------- | ------------------ | --- | ------- | -------------------- | --- | ------------- | ----------------------------------------------- | -------------- | --- | ------- | ---------------- |
| access and | outgoing bandwidth |     | if only | one or two processes | are |               |                                                 |                |     |         |                  |
|            |                    |     |         |                      |     | combinations, | we                                              | only enumerate | the | primary | sort key column. |
issuing commands to the SSD. HippogriffDB fixes this problem Hence,wereducethenumberofdifferentcompressedtablesfrom
n
byqueryingtheoccupancyoftheSSDNVMecommandqueues. tonwithminorcost(wecanstilluseothercompressionmeth-
2
Ifthequeuesarenearlyempty, itboostsperformancebyrunning ods for the column that is originally encoded using DELTA). For
(cid:0) (cid:1)
multiplepeer-to-peertransfersinparalleltoimprovebandwidth. example, whenrunningQ2.2inttheStarSchemaBenchmark(S-
1 rysortkeycombination,< Ci, >in F = 10 ), t h e o ve r a l l com p r e ssi o n r a ti o i n c re a se d fr o m 0 .2 8 t o 0.32
| G i v e n th e | ce r t ai n p r im a | r y -s e c o n d a |     |     | Cj  |     |     |     |     |     |     |
| -------------- | -------------------- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
t h e a l g or it hm , i t i st h e o p t im a l p l a n . an d th e e n ti re s y s t em sy s te m t h ro u g h p u t o n ly d ro p s by 1 3 % .
1652

Inpractice,databaseusersmayhaveadditionalknowledgeabout Category Operations
|     |     |     |     |     |     |     |     |     | Category1 | p.category=MFGR#12 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------------------ | --- | --- | --- |
thedatabase(e.g.,querylogs)thatcanhelpreducethespaceover-
s.region=AMERICA’
headevenfurther.
|     |     |     |     |     |     |     |     |     | Category2 | lo.orderdate=d.datekey |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | ---------------------- | --- | --- | --- |
RemarkInthissection,wediscusstheoptimizationsforthesec-
lo.partkey=p.partkey
ondarystorage.Thoseoptimizationsalsoworkforotherstoragesas lo.quantity<25
well.Forexample,theadaptivecompressionisapplicableinadis- Category3 SUM(lo.revenue)
GROUPBYd.year,p.brand1
tributedtopology,asthespaceisabundantinsucharchitecture.[5]
alsoallowsadirectdatatransferfromNICstotheGPU,bypassing Table2:CategorizationofoperationsinQuery2.
theCPU/memoryoverheadforthedistributeddatabases.
|     |                       |     |       |              |             |          |     | 2. (cid:49)   | outputsσ             | (R)(cid:49)L | (cid:49)...(cid:49)L | n.   |     |
| --- | --------------------- | --- | ----- | ------------ | ----------- | -------- | --- | ------------- | -------------------- | ------------ | -------------------- | ---- | --- |
| 5.  | QUERY-OVER-BLOCKMODEL |     |       |              |             |          |     | R,c,L1,...,Ln |                      | c            | 1                    |      |     |
|     |                       |     |       |              |             |          |     | 3. γ          | outputstheresultsofγ |              |                      | (J). |     |
|     |                       |     |       |              |             |          |     | J,A,f1,...,m  |                      |              | A,f1,...,m           |      |     |
|     | The query-over-block  |     | model | handles data | sets larger | than the |     |               |                      |              |                      |      |     |
Implem(cid:98)entationWeimplementthephysicaloperatorsasfollows:
| GPUmemory. |     | Itprovideshighscalabilitybyprocessinginputin |     |     |     |     |     |     |     |     |     |     |     |
| ---------- | --- | -------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
astreamingmanner. Italsoremovesintermediateresultsandim- 1. Λ R,c,K,V.WeimplementthehashtableusingCuckooHash-
provesGPUkernelefficiencywiththeoperatorfusionmechanism. ing[29]. EachGPUthreadevaluatestheselectioncondition
Inthissection,wefirstintroducethedataschemasthatwefocus on its input and, if the condition is met, inserts the input
on,thenformally(re)definethequeriesrunningontheseschemas. intothehashindex. WeuseatomicinstructionsthatCUDA
Basedonthedefinition,weintroducethreephysicaloperatorsand providestoavoidconflictsintheparallelprogram.
thenshowhowHippogriffDBusesthemtooptimizethequeryplan. 2. (cid:49) . We assign each GPU thread a row in the
R,c,L1,...,Ln
5.1 Schemaandquerydefinition fact table. The GPU thread first evaluate selection condi-
HippogriffDBtargetsdatawarehouseapplications. Dataware- t(cid:98)ionsontherelationR andthenprobesthehashindicesof
n.2
| housestypicallyorganizedataintomultidimensionalcubes(or |     |     |     |     |     |     |     | L 1 ,...,L |     |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- |
hypercubes)andmaphypercubesintorelationaldatabasesusing 3. γ J,A,f1,...,m . Weusethehashmaporarray(ifweknowthe
|     |             |        |           |         |        |              |     | domainsizeinadvance)fortheaggregation. |     |     |     | Weuseatomic |     |
| --- | ----------- | ------ | --------- | ------- | ------ | ------------ | --- | -------------------------------------- | --- | --- | --- | ----------- | --- |
| the | star schema | or the | snowflake | schema. | In the | star schema, | a   |                                        |     |     |     |             |     |
instructionstoresolveconflictsbetweendifferentthreads.
| central | table | contains | fact data | and multiple | dimension | tables ra- |     |     |     |     |     |     |     |
| ------- | ----- | -------- | --------- | ------------ | --------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
diateoutfromit. Thefacttableandthedimensiontablesconnect Operatorfusionmechanism
through the primary/foreign key relationships. Existing compari- HippogriffDB mollifies the memory contention that the inter-
sonresultsshowthatstarschemaisprevalentindatawarehouses[6, mediateresultscauseusingtheoperatorfusionmechanism. This
23].HippogriffDBfocusesonstarschemaqueries(SSQ).Forother mechanismcombinesmultipleoperatorsintoasingleGPUkernel
queriesandschemas,HippogriffDBcanworkasanacceleratoron and, inthisway, turnintermediateresultspassingintolocalvari-
SSQsubexpressionsandleavetheresttoclassicmethods. ablespassinginsideeachGPUthread.
TheoperatorsinsideanSSQfallintothreecategories. Thefirst For example, for the physical operator (cid:49) , we fuse
R,c,L1,...,Ln
categoryisunaryoperations, suchasselectionandprojection, on alljoins(hashjoins)andselectionsonthefacttableintooneGPU
dimensiontables. Thesecondcategoryincludesunaryoperations kernel.Weprovidetheoperatorfusionmec(cid:98)hanisminAlgorithm1.
Thekernelfirstevaluatestheselectionoperationonagivenrow(Line
onthefacttableandnaturaljoinbetweenthefactandthedimen-
siontables. Thelastcategoryisaggregationandgroupbyonthe 7-9).Iftherowsurvivestheselectionconditions,itwillproceedto
joinresults.Asanexample,wecategorizetheoperationsinQuery join with other dimension tables (Line 10-12). The GPU kernel
2intothesethreecategories,asshowninTable2. passesintermediateresultsusinglocalvariablesinsidethethread.
Figure 7 provides the Normalized Algebra (NA) expression for TheimplementationsofphysicaloperatorΛ R,c,K,V,γ J,f1,...,m fol-
SSQs. ThisattributegrammarhastheabilitytodescribeallSSQs. lowsimilarapproaches.
TherootoftheNAiseitheranaggregationofajoinorjustajoin. WeuseQuery2asanexampletocompareourqueryplanwith
The join here is either a series of joins over F,D ,...D or F thequeryplanthatexistingmodelsgenerate. Figure8(a)presents
|     |     |     |     |     | 1   | n   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
itself,whereF isafacttable(ortheresultofunaryoperationson thequeryplanthatmostexistingGPU-baseddatabasesadopt. Af-
thefacttable)andD isadimensiontable(ortheresultofunary terjoininglineorder andpart, thesystemsendsthejoinresult-
i
operationsonthedimensiontable). s (intermediate results) to join another table, supplier, and then
|     |     |     |     |     |     |     | generates |     | another set of | intermediate | results, | and so | forth. The |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | -------------- | ------------ | -------- | ------ | ---------- |
5.2 Query-over-blockexecutionmodel
|     |                  |     |          |                 |                |       | existing | query | plan sends | large intermediate |     | results several | times |
| --- | ---------------- | --- | -------- | --------------- | -------------- | ----- | -------- | ----- | ---------- | ------------------ | --- | --------------- | ----- |
|     | Query-over-block |     | improves | the scalability | and efficiency | using |          |       |            |                    |     |                 |       |
duringthequeryexecution,whichiscostlyasaccessingGPUglob-
| an“operatorfusion”mechanismandastream-basedapproach. |             |     |                 |       |              | In        |                 |     |                                            |     |     |     |     |
| ---------------------------------------------------- | ----------- | --- | --------------- | ----- | ------------ | --------- | --------------- | --- | ------------------------------------------ | --- | --- | --- | --- |
|                                                      |             |     |                 |       |              |           | almemoryisslow. |     | Inaddition,storingthoseintermediateresults |     |     |     |     |
| this                                                 | subsection, | we  | first introduce | three | new physical | operators |                 |     |                                            |     |     |     |     |
onamemory-scarcedevicehurtsthescalabilityofthesystem.Fig-
andthendemonstratehowquery-over-blockgeneratesqueryplans
ure8(b)showsourapproach.Itpackstheselectionsonthedimen-
usingthesephysicaloperators.
|     |     |     |     |     |     |     | sion | tables | and hash index | building | into the | Λ operator. | It fuses |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------ | -------------- | -------- | -------- | ----------- | -------- |
5.2.1 Operatorfusion
thethreenaturaljoins,theselectionontablelineorder,andthe
We implement three physical operators using operator fusion aggregationintooneGPUkernel.Inthisway,HippogriffDBavoids
mechanism to improve the kernel efficiency and to eliminate in- allintermediateresults.
termediateresults. Below,wefirstdefinethesephysicaloperators Discussion [7]usesinvisiblejoinstoreduceredundantdatatrans-
andthendiscusstheirimplementations. fers. Itfirstevaluatestheinvisiblejoinandthen,basedonthejoin
Physicaloperatordefinition results,readstheothercolumnsondemand.HippogriffDBdoesnot
BasedontheattributegrammarinSection5.1,HippogriffDBintro-
adoptthisapproach,asthesecondstepwouldinvolvelargeamount
| ducesthreecorrespondingphysicaloperators:Λ |     |     |     |     | R,c,K,V,(cid:49) |               | ,                                                   |     |     |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | ---------------- | ------------- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                                            |     |     |     |     |                  | R,c,L1,...,Ln | ofrandomreadstotheSSD,whichisslowforaflash-basedSSD |     |     |     |     |     |     |
andΓ J,f1,...,m .Wedefinethethreeoperatorslogicallyasfollows: (andalsoharddisks).
1. Λ outputsπ σ (R),ahashmapLwithπ(cid:98)K σ (R) 2WeassumethehashindicescanfitintheGPUmemory.
|     | R,c,K,V |     | K,V | c   |     | c   |     |     |     |     |     | Wediscussthe |     |
| --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- |
asthekeysandπ σ (R)asthevalues. memoryrequirementattheendofthissection.
V c
1653

𝛾
|     |     |     |     |     |     |     | 𝛾 𝑑 . 𝑦 𝑒 | 𝑎𝑟 , 𝑝 .𝑏 𝑟 𝑎 𝑛 𝑑 𝑙, | 𝑆𝑈 𝑀 ( 𝑙 𝑜 .𝑟 𝑒 𝑣 | 𝑒𝑛 𝑢 𝑒 ) |     | 𝛾   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | -------------------- | ----------------- | -------- | --- | --- | --- | --- | --- |
γ 𝑑.𝑦𝑒𝑎𝑟 , 𝑝 . 𝑏 𝑟 𝑎 𝑛 𝑑 𝑙 , 𝑆 𝑈 𝑀 ( 𝑙𝑜 . 𝑟 𝑒 𝑣 𝑒 𝑛 𝑢 𝑒 ) J,𝛾 F J1,… Fn
| NA  |     | G;f1(.) | N1,...,fn(.) | Nnγ Join |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ------- | ------------ | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | ⇒   | 7→      |              | 7→       |     |     |     |     |     |     |     | J   | 1…n |     |     |
Join
| d ate d lin Je o r d er ,  q u a n t i ty < 2 5 , ( L 1 ,L 2, L 3 )
| Join |     | F1D11D2...1Dn |     |     |     |     |     |     |     |     |     |     |     |     |     |
| ---- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
⇒ 𝜎 𝑟𝑒𝑔d𝑖𝑜a𝑛t e= d L L li n e o r d e Lr ,   q u a n t i t y < 2 5 , ( L 1 ,L 2 ,L 3 )
|     |     | F   |     |     |     |     |     |     | ′𝐴𝑀 𝐸 | 𝑅𝐼𝐶𝐴′ | 1   |                   | 2   | 3   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | ----- | --- | ----------------- | --- | --- | --- |
|     | |   |     |     |     |     |     | 𝜎   | 𝜎   |       |       |     | l i n e o r d e r |     |     |     |
F π a t t σ c F a ct 𝑞 𝑢 𝑎 𝑛 𝑡 𝑖𝑡 𝑦 < 2 5 C a t e g o r y = 𝑟‘ M 𝑒 F𝑔G 𝑖 R𝑜 # 𝑛 1= 2 ’ ′ 𝐴 𝑀s 𝐸p p𝑅 𝐼ie𝐶 r𝐴′ s p L a r 1t ,   d a Lt e 2,   N U L L ,   Ls u 3 p p l i e r ,
⇒ u l c a t e g o r y = ‘ M F G R # 1 2 ’ ,   r e g i o n = ‘ A M E R I C A ’ ,
F a c t 𝜎 <l in 2e 5o r d er 𝜎 tle o p a r t p l i n e o r d e r d a t e k e y ,  y e a r s u p p k e y ,   N U L L
| 𝑞 𝑢 𝑎 𝑛 𝑡 𝑖𝑡 𝑦 C a g o r y = ‘ M F G R # 1 2 ’ parp p t a r t k e y ,   b r a n d 1 s Uu Lp Lp l  i e r s u p p l i e r ,
D i π σ D i m ension s u p p l i e r s a r t ,   d a te d a t e ,   N , r e g i o n = ‘ A M E RICA’,
⇒ a t t c ( a )   Y D B   q u e r y   p l a n c a t ( e bg o ) r   y H= ‘ i M p F p G o R g # r 1 i2 f’ f,   D B q d u a t e e kr e y y  , py el aa r n
D im e n s io n l in e o r d er l o p a r t p p a r t k e y ,   b r a n d 1 s u p p k e y ,   N U LL
|     | |   |     |     |     |     |     |     |     |     |     | part |     | date | supplier |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | ---- | -------- | --- |
(a)  A n   a tt r ib u t e   g r a m m a r  o f  S S Q s Figure(8b:) TYhDeqBu eqruyeprlayn pfolranQuery2byYDBan(dc)H HippipogproifgfDriBf.fD Qu B ery q p u l e an ry th   a p t l H an ippogriffDB
|     | F ig u r e | 7 : A n a t t ri | b u te gr a | m m a ro f | SS Qs |     |     |     |     |     |     |     |     |     |     |
| --- | ---------- | ---------------- | ----------- | ---------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
generatescanavoidintermediateresultsandsupportdatasetlargerthanGPUmemory.
Algorithm1:Operatorfusionalgorithm ifications. The execution model first pushes down the selection
|     |     |     |     |     |     |     |     | operators | on  | the dimension | tables | and | then fuses | the | other oper- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | ------------- | ------ | --- | ---------- | --- | ----------- |
Input:AfacttableF,dimensiontableindices
|     |     |         |                             |     |     |     |     | ators | (selection, | join | and aggregations |     | on the | fact table) | into one |
| --- | --- | ------- | --------------------------- | --- | --- | --- | --- | ----- | ----------- | ---- | ---------------- | --- | ------ | ----------- | -------- |
|     |     | = ,..., | ,alistofselectionconditions |     |     |     |     |       |             |      |                  |     |        |             |          |
H {H 1 H n } GPUkernel. Thisapproachcanbestraightforwardlyextendedto
|     |     | = ,..., | ,joinconditions |     | =   | J ,...,J | ,   |     |     |     |     |     |     |     |     |
| --- | --- | ------- | --------------- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
C {C 1 C m } J { 1 l } snowflake schema queries, as both steps in the query-over-block
|     |     | groupbycolumns |            | = G ,...,G | ,aggregation |     |     |                                                 |     |     |     |     |     |     |     |
| --- | --- | -------------- | ---------- | ---------- | ------------ | --- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|     |     |                |            | G { 1      | k }          |     |     | executionmodelcanbeappliedtothesnowflakeschema. |     |     |     |     |     |     |     |
|     |     | function       | = A ,...,A |            |              |     |     |                                                 |     |     |     |     |     |     |     |
A { 1 p } Thequery-over-blockexecutionmodelhastwolimitations. First,
Output:Analyticalresults
Funcfused kernel(F, , R , , , ); itassumesthattheindicesofthedimensiontablescanfitintothe
1
H J C G A GPUdevicememory. WelookforwardtousingmultipleGPUsor
2 ∅;
|     | R←         |                  |     |     |       |     |      | enlargedGPUdevicememoryinfuturegenerations,asonesolution |     |     |     |     |     |     |     |
| --- | ---------- | ---------------- | --- | --- | ----- | --- | ---- | -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| 3   | cuda fused | kernel<<<...>>>( |     |     | ,F, , | , , | , ); |                                                          |     |     |     |     |     |     |     |
R H J C G A tothisissue. Second,itrequiresthatthequeryexecutionisdriven
| 4   | return | ;   |     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
R by processing blocks of the fact table. As we discussed above,
| 5   | Funcfused | kernel( | ,F, | , , | , , ); |     |     |     |     |     |     |     |     |     |     |
| --- | --------- | ------- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
R H J C G A bothstar-schemaandsnowflake-schemaqueriescanbeprocessed
| 6   | r R[thread | id]; |     |     |     |     |     |                                      |     |     |     |     |                      |     |     |
| --- | ---------- | ---- | --- | --- | --- | --- | --- | ------------------------------------ | --- | --- | --- | --- | -------------------- | --- | --- |
|     | ←          |      |     |     |     |     |     | byiteratingoverblocksofthefacttable. |     |     |     |     | However,therearealso |     |     |
| 7   | for c      | do   |     |     |     |     |     |                                      |     |     |     |     |                      |     |     |
∈C queries that cannot be processed by streaming a single table and
8 if eval(c,r)==falsethen
|     |     |              |     |     |     |     |     | immediatelyaggregatingit. |     |     | Forexample,queriesinvolvingmany- |     |     |     |     |
| --- | --- | ------------ | --- | --- | --- | --- | --- | ------------------------- | --- | --- | -------------------------------- | --- | --- | --- | --- |
| 9   |     | returnfalse; |     |     |     |     |     |                           |     |     |                                  |     |     |     |     |
to-manyjoinswillneedafutureextensionwhereweutilizethehost
memorytostoreintermediateresults.
| 10  | for j | do  |     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
∈J
| 11  | if  | j .find(P r,j | )==NULLthen |     |     |     |     | 6.  | EXPERIMENTALMETHODOLOGY |     |     |     |     |     |     |
| --- | --- | ------------- | ----------- | --- | --- | --- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- |
H
| 12  |     | returnfalse; |     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
WebuiltHippogriffDBandatestbedthatcontainsanIntelXeon
13 evalAggr( ,P r, , ); processor, an NVIDIA K20 GPU and a PCIe-attached SSD. We
|     |     | R   | G A |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
evaluateHippogriffDBusingtwopopulardataanalyticbenchmarks
|     |     |     |     |     |     |     |     | and | we compare | it  | with two | state-of-the-art |     | data analytics. | This |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | -------- | ---------------- | --- | --------------- | ---- |
sectiondescribesourtestbed,benchmarkapplications,andthetwo
| 5.2.2 |     | Block-orientedexecutionplan |     |     |     |     |     |     |     |     |     |     |     |     |     |
| ----- | --- | --------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
systemsthatwecompareHippogriffDBwith.
HippogriffDBusesablockexecutionplantoimprovethesystem
6.1 Experimentalplatform
| scalability. |     | It streams | the | fact table | to support | data | sets larger |     |     |     |     |     |     |     |     |
| ------------ | --- | ---------- | --- | ---------- | ---------- | ---- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
WerunourexperimentsonaserverwithanIntelXeonE52609V2
| thantheGPUmemory. |     |     | HippogriffDBadoptsdoublebufferingto |     |     |     |     |            |                                                |     |     |     |     |     |     |
| ----------------- | --- | --- | ----------------------------------- | --- | --- | --- | --- | ---------- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                   |     |     |                                     |     |     |     |     | processor. | Theprocessorcontains4coresandeachprocessorcore |     |     |     |     |     |     |
supportasynchronousdatatransfer,whichallowstheoverlapping
betweenthekernelexecutionandthedatatransfer. runs at 2.5 GHz by default. The server contains 64 GB DDR3-
HippogriffDBgeneratesthephysicalqueryplanforagivenquery 1600DRAMthatweusedasthemainmemoryinourexperiments.
inthreephases. Itfirstpushesdownunaryoperators(category1) TheGPUinourtestbedisanNVIDIATeslaK20GPUaccelerator,
whichcontains5GBGDDR5memoryonboard3.
onthedimensiontablesandbuildsin-GPU-memoryhashindices TheK20GPU
|     |      |                    |     | Λ         |     |            |           | connectstotherestofthesystemthrough16lanesofthePCIein- |     |     |     |     |     |     |     |
| --- | ---- | ------------------ | --- | --------- | --- | ---------- | --------- | ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
| for | them | (physical operator |     | R,c,K,V). | In  | the second | phase, it |                                                        |     |     |     |     |     |     |     |
terconnectthatprovides8GB/secI/Obandwidthineachdirection.
evaluatesnaturaljoins(category2)usingthehashindicesbuiltin
|     |              |                |               |               |                     |          |                     | W e | u se a h | i gh -e nd | P C Ie - a t ta | c he d SS | D a s th | e s ec on | d a ry s t o r a g e |
| --- | ------------ | -------------- | ------------- | ------------- | ------------------- | -------- | ------------------- | --- | -------- | ---------- | --------------- | --------- | -------- | --------- | -------------------- |
| t h | e p r e v io | u s s ta g e ( | p h y s i c a | l o pe r a to | r (cid:49) R ,c , L | ,.. . ,L | ) . T h e t h i r d |     |          |            |                 |           |          |           |                      |
1 n de vic e ( w it h 1 T B c ap a c it y ) . T he te stb e d u se s a L in u x s y s t e m
| s   | ta g e e v a | lu a te s a g gr | e g a t i o n s | o n t h e j | oi n re s u | l ts ( p h ysi | c al o p e r a t o r |      |               |            |               |          |            |            |             |
| --- | ------------ | ---------------- | --------------- | ----------- | ----------- | -------------- | -------------------- | ---- | ------------- | ---------- | ------------- | -------- | ---------- | ---------- | ----------- |
|     |              |                  |                 |             |             |                |                      | r un | n i n g t h e | 3 .1 6.3 k | e r ne l .W e | im p lem | en t the G | P U o p er | atorlibrary |
| Γ   | J ,f         | ) .              |                 |             | (cid:98)    |                |                      |      |               |            |               |          |            |            |             |
1 ,. .. ,m in H i p p o g r if fD B ba s e d o n NV I DI A CU D A To o lk it 6 .5 .
|     | H i p p o | gri f fDBadoptsacircularinput |     |     | buffertoenableasynchronous |     |     |     |     |     |     |     |     |     |     |
| --- | --------- | ----------------------------- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
data transfer for efficient streaming. The data transfer manager 6.2 Benchmarks
continues to transfer data while the kernel manager evaluates the To evaluate our system, we use two popular analytical bench-
receivedinput. marks. ThetwobenchmarksaretheStarSchemaBenchmark(SS-
BM)[28]andtheBerkeleyBigDataBenchmark(BBDB)[31].
MemoryrequirementInthecurrentimplementation,Hippogriff-
SSBMisawidelyusedbenchmarkindatabaseresearchdueto
DB requiresthehashindicesofthedimensiontablesfitintheGPU
memory. WealsomaintaintheinputandoutputbufferintheGPU its realistic modeling of data warehousing workloads. In SSBM,
memory. Hence, the memory requirement is S +S + the databasecontains one facttable ( lineorder table) andfour
|     |     |     |     |     |     | input | output |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ----- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
H i,whereH idenotesthesizeofhashindicesofthedimension dimension tables (supplier, customer, date and part table).
tableiandS input,S outputdenotethesizeoftheinput/outputbuffer. Thefacttablereferstotheotherfourdimensiontables, asshown
(cid:80) inFigure9(a). SSBMprovides13queriesin4flights. Hippogriff-
DiscussionWeusethestarschemaqueriestodemonstratethequery-
|                           |     |     |     |                                  |     |     |     | DB  | supportsall13queries. |     |     | Whenthescalefactoris1, |     |     | thetotal |
| ------------------------- | --- | --- | --- | -------------------------------- | --- | --- | --- | --- | --------------------- | --- | --- | ---------------------- | --- | --- | -------- |
| over-blockexecutionmodel. |     |     |     | However,thequery-over-blocktech- |     |     |     |     |                       |     |     |                        |     |     |          |
niquecan applyto otherschemas aswell, withappropriate mod- 3weuseanNVIDIAGTX650GPUforthewimpyhardwareexperiment,
1654

300
250
200
150
100
50
0
Q1.1 Q2.1 Q3.1 Q4.1
pudeeps
dezilamroN
20
YDB HDB-NO-OPT
HDB-NO-OPT 15 HDB
HDB
10
5
0
Q1 Q2
pudeeps
dezilamroN
20
15
10
5
0
Q1.1 Q2.1 Q3.1 Q4.1
(a)NormalizedspeeduponSSBM (b)NormalizedspeeduponBBDB
Figure 10: Normalized speedup relative to MonetDB (SF=10) when data are in memory.
HippogriffDBoutperformscompetitorsby1-2ordersofmagnitude.
pudeeps
dezilamroN
YDB
HDB-NO-OPT HDB
Figure 11: Performanceofdifferentsystems
(SF=10) when data are in SSD. HippogriffDB
outperformsYDBbyupto12 .
×
CUSTOMER LINEORDER PART USERVISITS RANKINGS 600
CUSTKEY ORDERKEY PARTKEY Stores server logs Lists websites and NAME LINENUMBER NAME for each web page their page rank 500 …… CUSTKEY M … F … GR d s e o s r t c U e R IP L p p a a g g e e R U a R n L k 400 S 3 i 0 z 0 e , = 00 S 0 F× P S A U R P T PK K E E Y Y S (1 iz + e l = og 20 S 0 F ,0 ) 00× a v d i R si e t v D e a n t u e e Size av = g 1 D 5 u 5 ra M tio i n llion 2 3 0 0 0 0
SUPPLIER ORDERDATE 2 userAgent
SUPPKEY …… DATE countryCode DOCUMENTS 100
… NA … ME COMM TA IT X DATE DA … D T A E … T K E EY la s n e g a u rc a h g W eC o o rd de U d n o H s c tr u T u m M c e t L u n r t e s d 0 YDB HDB-NO-OPT HDB
S 2 i ,0 ze 0 = 0 SF× Size= SH S I F P × M 6 O , D 00 E 0,000 Size=356 × 7 Size= du 1 r 8 a t M ion illion 29.0GB
(a) Star Schema Benchmark(SSBM) (b)Berkeley Big Data Benchmark(BBDB)
Figure9:SchemaofthedatabaseinSSBMandBBDB.
databasesizeisabout0.7GB.Wevarythescalefactorfrom1to
1000 in our experiments. The database size is 0.7 TB when the
scalefactorreaches1000.
BBDBincludesseveralsearchengineworkloads. Thedatabase
in BBDB contains three tables, depicting documents, pageranks
anduservisitsinformation, asshowninFigure9(b). Thebench-
mark contains 4 queries. The third query contains a string join,
whichcurrentHippogriffDBdoesnotsupport,andthelastonein-
volvesanexternalPythonprogram.Hence,weevaluateoursystem
usingQuery1andQuery2inthisbenchmark.
6.3 Competitors
We compare HippogriffDB with two analytical database sys-
tems, MonetDB [9] and YDB [41]. MonetDB is a state-of-the-
art column-store database system that targets analytics over large
inputs.YDBisaGPUexecutionengineforOLAPqueries.Exper-
imentresultsshowthatYDBrunsupto6.5 fasterthanitsCPU
× counterpartonworkloadsthatcanfitinGPU’smemory.
7. RESULTS
In this section, we present the experimental results for Hippo-
griffDB.Thissectionfirstpresentstheend-to-endperformancecom-
paredwiththetwocompetitors. Afterthat,weevaluatetheeffec-
tivenessoftheproposedmethodsinbalancingcomponentthrough-
putinsidethesystem.Wethenevaluatetheexecutionmodel.
7.1 Overallperformance
We first evaluate the speedup that HippogriffDB can achieve.
We compare out system with two baselines: MonetDB [9] and
YDB[41].WeprovidetwoversionsofHippogriffDBhere:Hippo-
griffDBwithoutcompressionandpipeliningoptimizations(HDB-
NO-OPT)andthefull-fledgedversion(HDB).
Figure10(a)showsthenormalizedspeedupofdifferentsystems
(relativetoMonetDB)whendataareintheGPUmemory. Weuse
10asthescalefactorhere.Inthiscase,theworkingsetsizeis0.96-
1.44GBforSSBM.ForBBDB,weadopta1.2GBinput.Asshown
inFigure10(a),HDB-NO-OPToutperformsMonetDBby38 and
×
)sm( emit gninnuR
1800
I/O 1600 Kernel 1400 1200 1000 800 600
400
200
0 YDB HDB-NO-OPT HDB
)sm(
emit gninnuR I/O Kernel
(a)Inmemory (b)OnSSD
Figure12: BreakdownofqueryQ1.1executiontime. HDBimproves
bothkernelandI/Oefficiencycomparedwithotheranalyticalsystems.
YDBby2.6 onaverageforSSBMqueries.Thefull-fledgedver-
×
sion(includingcompressionandpipelining)outperformsMonetD-
Bby147 andYDBby9.8 onaverage. ForBBDB,HDB-NO-
× ×
OPT achieves 4.2 speedup compared with MonetDB and with
×
optimizationsthespeeduprisesto11.8 ,asshowninFigure10(b).
×
HDB-NO-OPT produces less speedup for BBDB compared with
SSBM, as the queries in BBDB are relatively simple and cannot
fullyutilizetheGPUcomputationpower.
Figure11comparestheexecutiontimewhenthedatabaseresides
in the SSD. As shown in the figure, HDB-NO-OPT outperforms
YDBby2.4 onaverage. Withoptimizations,HDBoutperforms
×
YDBby8.4 onaverage.
Figure 12×(a) breaks down the execution time of Q1.1 into I/O
andkernelexecutionwhenHippogriffDB(bothHDB-NO-OPTand
HDB)andYDBstoredatainthemainmemory. Wedonotshow
MonetDBhere,asitisnotaGPU-baseddatabaseanditdoesnot
havethesetwostages. Tomeasuretheexecutiontimebreakdown,
wedisablethepipeliningmechanisminoursystems.Theexecution
time breakdown indicates that the majority of performance boost
comesfromtheGPUkernel.Byremovingintermediateresultsand
usingnewphysicaloperators,HDB-NO-OPTruns9.8 fasterthan
×
YDB.Inaddition, thedatatransferrateinHDB-NO-OPTisalso
36%fasterthanYDB,duetolesssoftwareandmetadataoverhead4.
Compressionreducesthetablesizeby4.6 andhencereducesthe
×
I/OtimeinHDB.Thoughthedecompressionaddsadditionalcost
to the GPU processing, because of the significant improvement
from the I/O stage, HDB still achieves 2.5 speedup compared
×
withHDB-NO-OPT.
WealsoshowtheexecutiontimebreakdownfortheSSDversion
inFigure12(b). Theperformancegaininthiscaseismainlyfrom
the optimized data transfer in HippogriffDB. The inefficiency of
4We use the same method as in [39] to run YDB: warm up memory
by executing each query once before the experiments. Reading from a
warmcachecouldbeslowercomparedwithreadingdirectlyfromthemain
memoryduetosomeoperatingsystemoverhead.
1655

|                 |                    |     |     | emit dezilamroN 2.0 |      |     |        |  2500 |     |     |     |     |     |
| --------------- | ------------------ | --- | --- | ------------------- | ---- | --- | ------ | ----- | --- | --- | --- | --- | --- |
| 8               |                    |     |     |                     | Host |     | Direct |       |     |     |     |     |     |
| emit dezilamroN | HDB-NO-COMPRESSION |     |     | 1.5                 |      |     |        |       |     |     |     |     |     |
6 HDB
 2000
|     |     |     |     | 1.0 |     |     |     | )ceS/BM( tuphguorhT |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- |
4
|     |     |     |     | 0.5 |     |     |     |  1500 |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
2
0.0
| 0    |      |           |     |        | Q1.1 |        | Q4.1        |       |     |     |     |     |     |
| ---- | ---- | --------- | --- | ------ | ---- | ------ | ----------- | ----- | --- | --- | --- | --- | --- |
| Q1.1 | Q2.1 | Q3.1 Q4.1 |     |        |      |        |             |  1000 |     |     |     |     |     |
|      |      |           |     | Figure | 14:  | Effect | of peer-to- |       |     |     |     |     |     |
Figure 13:
|                               | HippogriffDB  |     | with |        |                   |                    |          |  500 |     |     |     |                | NVMe |
| ----------------------------- | ------------- | --- | ---- | ------ | ----------------- | ------------------ | -------- | ---- | --- | --- | --- | -------------- | ---- |
|                               |               |     |      | peer   | I/O optimization, |                    | SF=1000. |      |     |     |     | NVMe-pipeline  |      |
| and without                   | compressions, |     |      | S-     |                   |                    |          |      |     |     |     | Hippogriff (S) |      |
|                               |               |     |      | Direct | datapath          | and multi-threaded |          |      |     |     |     | Hippogriff (M) |      |
| F=10. Compressionhelpsimprove |               |     |      |        |                   |                    |          |  0   |     |     |     |                |      |
helpimprovesystemthroughputby 4M 8M 16M 32M 64M 128M 256M 512M 1GB 2GB 4GB
| systemthroughputbyupto5 |     |     | .   |      |      |      |      |           |                                                  |           |     |     |     |
| ----------------------- | --- | --- | --- | ---- | ---- | ---- | ---- | --------- | ------------------------------------------------ | --------- | --- | --- | --- |
|                         |     |     | ×   | 18%. |      |      |      |           |                                                  | File size |     |     |     |
|                         |     |     |     |      |      |      |      | Figure15: | ThethroughputofdifferentdatapathsinHippogriffDB. |           |     |     |     |
|                         |     |     |     | 1    | 10   | 100  | 1000 |           |                                                  |           |     |     |     |
| HDB-Q-ADAPTIVE          |     |     |     | 0.28 | 0.30 | 0.31 | 0.32 |           |                                                  |           |     |     |     |
|                         |     |     |     |      |      |      |      | 70        |                                                  | 70        |     |     |     |
HDB-Q-INSENSITIVE 0.42 0.46 0.48 0.49 )s/BG( htdiwdnaB GPU )s/BG( htdiwdnaB GPU I/O
|     |      |     |     |      |      |      |      | 60  | I/O | 60  |     |     |     |
| --- | ---- | --- | --- | ---- | ---- | ---- | ---- | --- | --- | --- | --- | --- | --- |
|     | DICT |     |     | 0.44 | 0.48 | 0.52 | 0.55 | 50  |     | 50  |     |     |     |
Table3: Compressionratioofquery-adaptiveandquery-insensitive 40 40
|     | Query-adaptive |     | compression |     | can keep | good | compression | 30  |     | 30  |     |     |     |
| --- | -------------- | --- | ----------- | --- | -------- | ---- | ----------- | --- | --- | --- | --- | --- | --- |
compression.
|                                                       |            |      |     |            |       |         |           | 20   |                        | 20  |      |     |     |
| ----------------------------------------------------- | ---------- | ---- | --- | ---------- | ----- | ------- | --------- | ---- | ---------------------- | --- | ---- | --- | --- |
| ratiowhenthedatabasescalesup(x-axisisthescalefactor). |            |      |     |            |       |         |           | 10   |                        | 10  |      |     |     |
|                                                       |            |      |     |            |       |         |           | 0    |                        |     | 0    |     |     |
|                                                       |            |      |     |            |       |         |           | BASE | Direct-IODirect-IO+CMP |     | BASE |     | CMP |
| I/O in                                                | YDB agrees | with | the | results in | [39]. | The I/O | bandwidth |      |                        |     |      |     |     |
HDBcanachieveisupto2.3 largerthanitscompetitor. (a)SSD (b)Memory
×
|     |     |     |     |     |     |     |     | Figure 16: | EffectofclosingtheGPU-IObandwidthgap. |     |     |     | Proposed |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------------------------------------- | --- | --- | --- | -------- |
7.2 ClosetheGPU-I/Obandwidthgap
|                                                      |     |     |     |     |     |     |     | approachesnarrowtheGPU-IOgapbyupto21 |     |     | .   |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------ | --- | --- | --- | --- | --- |
| HippogriffDBfixesthegapbetweenthefastGPUkernelandthe |     |     |     |     |     |     |     |                                      |     |     | ×   |     |     |
slowdatatransferbyovercomingtheI/Obottleneckintwoways: Figure 15 compares the throughput of moving data from the
(1)itcompressesdatabasesandtradesidleGPUcyclesfordecom- SSDtotheGPUusingHippogriff(M)againststandardNVMe(N-
pressiontoachievebetterdatatransferefficiency. (2)itredesigns VMe),pipelinedNVMe(NVMe-pipeline)5andthesinglechannel,
thedatapathtobypassthehostCPUandthemainmemorywhen peer-to-peer transfer (Hippogriff (S)). We report the data transfer
transferringdatafromtheSSDtotheGPU.Inthissubsection,we
|     |     |     |     |     |     |     |     | throughput | under different file | sizes, | excluding | the | overhead of |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | -------------------- | ------ | --------- | --- | ----------- |
evaluatetheseapproaches.
allocatingallnecessaryresources(e.g.,memorybuffers)alongthe
| 7.2.1        | Effectofcompression |        |      |                 |     |        |            | datapaths. |                         |           |         |          |             |
| ------------ | ------------------- | ------ | ---- | --------------- | --- | ------ | ---------- | ---------- | ----------------------- | --------- | ------- | -------- | ----------- |
|              |                     |        |      |                 |     |        |            | Hippogriff | (M) outperforms         | all other | route   | options. | The per-    |
| HippogriffDB |                     | stores | data | in a compressed |     | format | and trades |            |                         |           |         |          |             |
|              |                     |        |      |                 |     |        |            | formance   | advantage of Hippogriff | (M)       | becomes | more     | significant |
GPUcyclesforbetterI/Operformance.Inthissubsection,westudy
|     |     |     |     |     |     |     |     | asfilesizeincreases. | Whentransferringa4GBfilebetweenthe |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | ---------------------------------- | --- | --- | --- | --- |
theeffectofdatacompressionintermsofbandwidthimprovement.
SSDandtheGPU,Hippogriff(S)thatperformsfileaccessrequests
| We first | compare | the | execution | time | with compression |     | (HDB) |                |              |       |      |          |           |
| -------- | ------- | --- | --------- | ---- | ---------------- | --- | ----- | -------------- | ------------ | ----- | ---- | -------- | --------- |
|          |         |     |           |      |                  |     |       | using a single | NVMe command | queue | only | achieves | bandwidth |
andwithoutcompression(HDB-NO-COMPRESSION)forvarious
of1110MB/sec,duetotheunder-utilizedNVMeSSDresources.
| queries. | We use | 10 as | the scale | factor | here. | Figure | 13 shows |     |     |     |     |     |     |
| -------- | ------ | ----- | --------- | ------ | ----- | ------ | -------- | --- | --- | --- | --- | --- | --- |
Hippogriff(M),ontheotherhand,offersupto2221MB/secband-
| the comparison |     | results. | Compression |     | can achieve | 2.8 | 4.9        |                                                        |     |     |     |     |     |
| -------------- | --- | -------- | ----------- | --- | ----------- | --- | ---------- | ------------------------------------------------------ | --- | --- | --- | --- | --- |
|                |     |          |             |     |             |     | ×− ×       | width. NVMe-pipelineimprovestheperformanceofstandardN- |     |     |     |     |     |
| improvement    | in  | system   | throughput. | As  | discussed   | in  | Section 3, |                                                        |     |     |     |     |     |
compressionontheforeignkeycolumnsisthemostdifficult,due VMe by compensating for latencies with multiple data transfers.
toitslargecardinality. CompressionbenefitsmostinQ1.1,asthis However, NVMe-pipeline can still only achieve a throughput of
queryonlyinvolvesoneforeignkey. Forotherqueries,HDBcan 1691MB/SecbetweentheSSDandtheGPUfor4GBfiles,34%
slowerthanHippogriff(M),becauseNVMe-pipelinerequiresmore
stillreacharatherdecentcompressionratio.
CPUresources.
HippogriffDBadoptsquery-adaptivecompressionfordatabases
Wecomparetheexecutiontimeofusinganoptimizedhostroute
| stored in | SSD. | We compare | the | compression |     | ratio difference | be- |                     |                                        |     |     |     |     |
| --------- | ---- | ---------- | --- | ----------- | --- | ---------------- | --- | ------------------- | -------------------------------------- | --- | --- | --- | --- |
|           |      |            |     |             |     |                  |     | andusingHippogriff. | Experimentshowsthatthepeer-to-peerdata |     |     |     |     |
tweenaquery-adaptivecompression(HDB-Q-ADAPTIVE)anda
transferhelpsreducetheend-to-endlatencyby19%.
fixedapproach(HDB-Q-INSENSITIVE)usingtheexamplegiven
Asasummaryoftheeffectoftheendeavoursdiscussedabove,
| in Section | 4.2. | We show | the | compression | ratio | in Table | 3. As |     |     |     |     |     |     |
| ---------- | ---- | ------- | --- | ----------- | ----- | -------- | ----- | --- | --- | --- | --- | --- | --- |
Figure16showstheeffectofnarrowingthebandwidthgapbetween
| shown | in the table, | the | query-adaptive |     | compression | can | maintain |     |     |     |     |     |     |
| ----- | ------------- | --- | -------------- | --- | ----------- | --- | -------- | --- | --- | --- | --- | --- | --- |
decentcompressionratiowhendatabasesscalingupwhilethecom- theGPUkernelandI/O.WecomparethedifferencebetweenGPU
pressionefficiencyofthefixedapproachdegradessignificantly.It’s kernelanddatatransferbandwidthusingSSBMQ1.1andshowthe
becausethefixedcompressionfailstoapplyeffectivecompression resultsforbothSSD-basedandmemory-basedHippogriffDB.For
methodsoncriticalforeignkeys. Previousliterature[41]indicates theSSDversion,theinitialgap(BASE)isupto82 . Thedirect
×
|     |     |     |     |     |     |     |     | datatransfer(Direct-IO)bringsitdownto38 |     |     |     | andthecompres- |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------- | --- | --- | --- | -------------- | --- |
that DICT can achieve a satisfying compression effect on small ×
|                                                         |     |     |     |     |     |     |     | sion(Direct-IO+CMP)furtherbringsthegapdownto3.9 |     |     |     |     | . For |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------- | --- | --- | --- | --- | ----- |
| datasetswhileourresultsshowthattheperformanceofDICTalso |     |     |     |     |     |     |     |                                                 |     |     |     |     | ×     |
thein-memoryversion,compression(CMP)narrowsthegapfrom
degradesrapidlywhendatasetsscaleup.
|       |                                  |     |     |     |     |     |     | 12 to1.2 | ,veryclosetoachievingthebalance. |     |     |     |     |
| ----- | -------------------------------- | --- | --- | --- | --- | --- | --- | -------- | -------------------------------- | --- | --- | --- | --- |
| 7.2.2 | Effectofpeer-to-peerdatatransfer |     |     |     |     |     |     | ×        | ×                                |     |     |     |     |
Observingthatdatatransferbandwidthisthesystembottleneck, 7.3 Query-over-blockmodelevaluation
| weadoptseveraloptimizationstoimprovethebandwidth.          |     |     |     |     |     |     | Inthis |             |                    |               |     |            |          |
| ---------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------ | ----------- | ------------------ | ------------- | --- | ---------- | -------- |
| subsection,weevaluatethebandwidthimprovementusingthemulti- |     |     |     |     |     |     |        | 5This       |                    |               |     |            |          |
|                                                            |     |     |     |     |     |     |        | is an       | optimized baseline | that overlaps | the | SSD access | with GPU |
| threaded,peer-to-peercommunicationmechanism.               |     |     |     |     |     |     |        | memorycopy. |                    |               |     |            |          |
1656

|     |              | 1     | 10    | 100   | 1000  | )s/BG( tuphguorhT 100 |               |     | )S/BG( tuphguorhT 60 |               |     |
| --- | ------------ | ----- | ----- | ----- | ----- | --------------------- | ------------- | --- | -------------------- | ------------- | --- |
|     |              |       |       |       |       |                       | HDB-NO-FUSION |     |                      | HDB-NO-FUSION |     |
|     | YDB          | 12.27 | 98.03 | N/A   | N/A   | 80                    |               |     | 50                   |               |     |
|     |              |       |       |       |       |                       | HDB           |     |                      | HDB           |     |
|     | HippogriffDB | 1     | 10.27 | 93.60 | 938.0 |                       |               |     | 40                   |               |     |
60
30
| Table4:NormalizedscalabilityperformancewithincreasingSF(from |     |     |     |     |     | 40  |     |     |     |     |     |
| ------------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
20
| 1to1000). | ResultstestifythescalabilityofHippogriffDB(x-axisisthe |     |     |     |     |     |     |     |     |     |     |
| --------- | ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|           |                                                        |     |     |     |     | 20  |     |     | 10  |     |     |
scalefactor).
|     |     |     |     |     |     | 0   |     |     | 0       |     |        |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | ------ |
|     |     |     |     |     |     | 0.7 | 7   | 70  | 700 0.7 | 7   | 70 700 |
100   V P   H P L W  Q R L W X F H [ H  H Y L W D O H U 1.25 Size (GB) Size (GB)
)S/BG( tuphguorhT
|     | Q1.1    | Q3.1 |      | NO-DB | DB  |        | (a)Q1.1    |             |              | (b)Q4.1  |          |
| --- | ------- | ---- | ---- | ----- | --- | ------ | ---------- | ----------- | ------------ | -------- | -------- |
|     | 80 Q2.1 | Q4.1 | 1.00 |       |     |        |            |             |              |          |          |
|     |         |      |      |       |     | Figure | 19: Effect | of removing | intermediate | results. | Removing |
|     | 60      |      | 0.75 |       |     |        |            |             |              |          |          |
intermediateresultscanimprovequeryexecutiontimebyupto91%.
|     | 40  |     | 0.50 |     |     |       |                                     |     |     |     |     |
| --- | --- | --- | ---- | --- | --- | ----- | ----------------------------------- | --- | --- | --- | --- |
|     | 20  |     | 0.25 |     |     | 7.3.3 | Effectofavoidingintermediateresults |     |     |     |     |
|     | 0   |     | 0.00 |     |     |       |                                     |     |     |     |     |
0.7 7 70 700 Q1.1(S)Q1.1(M)Q4.1(S)Q4.1(M) Figure19comparesthethebenefitofreducingintermediatere-
Size(GB)
|     |     |     |     |     |     | sults using | SSBM | Q1.1 and | Q4.1. We | vary SF | from 1 to 1000 |
| --- | --- | --- | --- | --- | --- | ----------- | ---- | -------- | -------- | ------- | -------------- |
Figure 18: Effect of double (databasesizefrom0.7GB-0.7TB).Wecomparethethroughput
| Figure | 17: Scalability | of GPU |     |     |     |     |     |     |     |     |     |
| ------ | --------------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
buffering. Double buffering helps of HippogriffDB (HDB) and HippogriffDB without operator fu-
| kernels | on SSBM. | GPU kernel |     |     |     |     |     |     |     |     |     |
| ------- | -------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
reduce the execution time by up sion(HDB-NO-FUSION).AsshowninFigure19,theGPUkernel
| throughput | is consistently | higher |     |     |     |     |     |     |     |     |     |
| ---------- | --------------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
to 15% without compression. It throughputimprovesby91%forQ1.1and43%forQ4.1.Reducing
| than | I/O bandwidth | by over one |     |     |     |     |     |     |     |     |     |
| ---- | ------------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
canfurtherimprovesystemperfor- intermediate results works better on light-weighted queries. For
orderofmagnitude.
mancewithotheroptimizations. heavy-weightedqueries,thecomputationcantakeasignificantpor-
tionoftimeandoperatorfusionwillnotoptimizeforthispart.For
Thequery-over-blockmodelmakesHippogriffDBthefirstGPU-
|     |     |     |     |     |     | query 4.1, | the benefits | of  | reducing intermediate |     | results decreases |
| --- | --- | --- | --- | --- | --- | ---------- | ------------ | --- | --------------------- | --- | ----------------- |
baseddatabasesystemthatprovidesnativesupportforbigdataana-
|     |     |     |     |     |     | withthegrowthofthescalefactor. |     |     | Itisalsobecausethecomputa- |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------ | --- | --- | -------------------------- | --- | --- |
lytics.Thequerymodelusesseveraloptimizationstoimproveper-
formance, including removing materialization and double buffer- tionloadincreaseswiththegrowthofthescalefactor.
ing. Inthissubsection,wefirstevaluatethesystemscalabilityand 7.4 Performanceonwimpyhardware
thenanalyzetheeffectoftheproposedoptimizations. Intheprevioussections,wediscusstheproposedoptimizations
7.3.1 Systemscalability on the high-end hardware. In this subsection, we examine the
We test the scalability of HippogriffDB by varying the scale optimizationsonthewimpyhardwares,suchaslow-endGPUs.
factor from 1 to 1000 (database size from 0.7 GB - 0.7 TB). We While Hippogriff does not work with low-end GPUs because
runtheSSBMQ1.1intheexperimentwithoutcompression. Table oftheBIOSsetupofmanufacturers, thequery-over-blockexecu-
4reportstheexecutiontimeforqueriesonYDBandHippogriff- tion model can still improve the kernel efficiency on the wimpy
DB. The database resides in SSD in this experiment. As shown hardware. By reducing the intermediate results, the query-over-
blockexecutionmodelimprovestheGPUprocessingrateby2.9
| inthetable,YDBcannotsupportquerieswhenthescalefactoris |     |     |     |     |     |                                                |     |     |     |     | ×   |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- |
|                                                        |     |     |     |     |     | forlight-weightedquery(SSBMQ1.1,SF=10)andby2.4 |     |     |     |     | for |
| above10whileHippogriffDBshowsitssuperioritybyscalingup |     |     |     |     |     |                                                |     |     |     |     | ×   |
heavy-weightedquery(SSBMQ4.1,SF=10).Withoutpeer-to-peer
tosupportterabyte-levelinput.
datacommunicationsupports,themulti-threadedtransferstillhelps
|     | Whenscalingup,thethroughputofHippogriffDB |     |     |     | remainssta- |     |     |     |     |     |     |
| --- | ----------------------------------------- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- |
boostthebandwidthinthesystemusinglow-endGPUs.Asshown
| ble(assameasthedatatransferbandwidth). |     |     |     | Thisisbecausethe |     |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
inFigure15,usingmulti-threadedI/Ocanachieveupto1.6GB/s
GPUkernelalwaysrunsfasterthandatatransferbandwidthinthis
case. WeshowtheGPUkernelthroughputinFigure17:thespeed onourSSD.Compressionstillworkstonarrowthebandwidthmis-
thattheGPUprocessesdatabasequeries(morethan20GB/s)isat matchbetweentheSSDandtheGPU.Forexample,thecompres-
least12 higherthantheI/Obandwidth.Thistrendsustainswhen sion can increase theeffective I/Obandwidthby 4.6 on SSBM
×
theinputscalesuptoterabyte-leveltables. × Thedoublebuffering Q1.1 while the GPU can still process at 22.9 GB/s, 3.3 larger
×
alwayskeepsI/OdevicebusyandsaturatestheI/Obandwidth. As thantheeffectivebandwidth.
aresult,theperformanceremainsthestablewhenscalingup. The 8. RELATEDWORK
I/Obandwidthwithoutoptimizationisnotsatisfiableandthatisthe
WiththeendofDennardscaling[12](powerdensitystayscon-
| reason | we propose | compression | and peer-to-peer |     | data transfer to |     |     |     |     |     |     |
| ------ | ---------- | ----------- | ---------------- | --- | ---------------- | --- | --- | --- | --- | --- | --- |
stant),itishardforgeneralpurposeCPUstoprovidescalableper-
improvetheeffectiveI/Obandwidth.
|     |     |     |     |     |     | formance | in the | future due | to the power | challenges | [13,16]. In |
| --- | --- | --- | --- | --- | --- | -------- | ------ | ---------- | ------------ | ---------- | ----------- |
7.3.2 Effectofdoublebuffering
recentyears,researchersindatabasecommunitystartedtousehet-
HippogriffDB usesdoublebufferingtooverlapthedatatransfer erogeneouscomputingtoovercomethescalingproblemofCPUs
andkernelexecution,reducingtheexecutiontimeofqueryprocess- andtocontinuedeliveringscalableperformancefordatabaseappli-
ing. WecomparetheeffectofusingdoublebufferinginFigure18 cations[18,19,33,41].
(SF = 10). The double buffering reduces the execution time for Amongvarioushardwareaccelerators,GPUistheonethatdraws
Q1.1inSSBMby3%and7%forSSD-basedandmemory-based the most attention. Several full-fledged GPU database query en-
HippogriffDB. For Q4.1, it can help improve the execution time gines [10,20,41] came out in the recent years. Ocelot [20] pro-
by 5% and 15% respectively. Double buffering works better on videsahybridanalyticalqueryengineasanextensiontoMonetDB.
complexqueries,astheGPUkerneltimeconsumeshigherportion HyPE[10]isahybridanalyticalengineutilizingboththeCPUand
inthetotalexecutiontimeforcomplexqueries. Doublebuffering the GPU for query processing. YDB [41] is a GPU-based data
canfurtherimprovethesystemperformanceincombinationwith warehousequeryengine.ThoughYDBallowsdatabasestoreinthe
otheroptimizations,suchascompression. Withdatacompression, mainmemoryortheSSD,itstillassumesthattheworkingsetcan
thegapbetweenfasterpartandslowerpartnarrowsandhencethe fitinthemainmemory. HippogriffDB differsfromtheprevious
overlappingcanresultinmoreperformancegain. work as HippogriffDB is targeting large scale database systems
1657

(TB scale input). HippogriffDB allows data sets larger than the [8] D.Agrawal,P.Bernstein,E.Bertino,S.Davidson,U.Dayal,M.Franklin,
GPU memory capacity. To cope with the limited GPU memory J.Gehrke,L.Haas,A.Halevy,J.Han,etal.Challengesandopportunitieswith
bigdata2011-1.2011.
capacity,HippogriffDB usesstreamingdatabaseoperationswhich
[9] P.A.Boncz,M.Zukowski,andN.Nes.Monetdb/x100:Hyper-pipeliningquery
enabledataprocessingonsmallchunks. execution.InCIDR,volume5,pages225–237,2005.
SeveralCPU-baseddatabasesalsouseblock-orientedexecution [10] S.BreßandG.Saake.Whyitistimeforahype:Ahybridqueryprocessing
engineforefficientgpucoprocessingindbms.VLDB,6(12):1398–1403,2013.
model. [9] identifies that the system bottleneck in a CPU-based
[11] E.S.Chung,P.A.Milder,J.C.Hoe,andK.Mai.Single-chipheterogeneous
in-memory database is the limited memory bandwidth and uses computing:Doesthefutureincludecustomlogic,fpgas,andgpgpus?In
a cache-aware approach to reduce memory traffic. However, the MICRO,pages225–236.IEEEComputerSociety,2010.
limitedmemorybandwidthconcernofCPU-baseddatabasesdoes [12] R.H.Dennard,V.Rideout,E.Bassous,andA.Leblanc.Designof
ion-implantedmosfet’swithverysmallphysicaldimensions.Solid-State
notholdforaGPU-basedsystem,astheGPUshavemuchhigher Circuits,IEEEJournalof,9(5):256–268,1974.
memory bandwidth (100s GB/sec). HippogriffDB uses a block- [13] H.Esmaeilzadeh,E.Blem,R.S.Amant,K.Sankaralingam,andD.Burger.
basedexecutiontoremovethescalabilitylimitation posed bythe Darksiliconandtheendofmulticorescaling.InISCA,pages365–376,2011.
[14] W.Fang,B.He,andQ.Luo.Databasecompressionongraphicsprocessors.
smallGPUmemorycapacity. TheblocksizebetweenHippogriff-
VLDB,3(1-2):670–680,2010.
DBand[9]isalsodifferent: HippogriffDBchoosesasizethatis [15] N.Govindaraju,J.Gray,R.Kumar,andD.Manocha.Gputerasort:high
largeenoughtodelivergoodI/ObandwidthfromtheSSDtothe performancegraphicsco-processorsortingforlargedatabasemanagement.In
SIGMOD,pages325–336.ACM,2006.
GPU,whichismuchlargerthanthecachesize(10sKBonGPUs).
[16] N.Hardavellas,M.Ferdman,B.Falsafi,andA.Ailamaki.Towarddarksilicon
Compression is a popular strategy to reduce the storage space inservers.IEEEMicro,31(EPFL-ARTICLE-168285):6–15,2011.
and the amount of data transfer. Several works [14,27,30] dis- [17] B.He,K.Yang,R.Fang,M.Lu,N.Govindaraju,Q.Luo,andP.Sander.
Relationaljoinsongraphicsprocessors.InSIGMOD,pages511–524,2008.
cussedthealgorithmsofcompression/decompressiononGPU.YDB
[18] B.HeandJ.X.Yu.High-throughputtransactionexecutionsongraphics
[41] uses dictionary and run-length encoding to reduce data sets processors.VLDB,4(5):314–325,2011.
sothatitcansupporttablesslightlylargerthantheGPUmemory [19] J.He,M.Lu,andB.He.Revisitingco-processingforhashjoinsonthecoupled
cpu-gpuarchitecture.VLDB,6(10):889–900,2013.
capacity. HippogriffDB differsfromthepreviousworkasHippo-
[20] M.Heimel,M.Saecker,H.Pirk,S.Manegold,andV.Markl.
griffDB uses the query-adaptive compression. Wu et al. [40] Hardware-obliviousparallelismforin-memorycolumn-stores.VLDB,
proposedaprimitivefusingstrategytoreducetheback-and-forth 6(9):709–720,2013.
traffic between GPU and hosts. HippogriffDB adopts a similar [21] H.Jagadish,J.Gehrke,A.Labrinidis,Y.Papakonstantinou,J.M.Patel,
R.Ramakrishnan,andC.Shahabi.Bigdataanditstechnicalchallenges.
technologytoreducethedataexchange. CommunicationsoftheACM,57(7):86–94,2014.
There are several related projects on the direct communication [22] S.Kim,S.Huh,Y.Hu,X.Zhang,A.Wated,E.Witchel,andM.Silberstein.
between two PCIe devices. For example, GPUDirect [3] offers Gpunet:Networkingabstractionsforgpuprograms.InOSDI,pages6–8,2014.
[23] R.KimballandM.Ross.Thedatawarehousetoolkit:Thedefinitiveguideto
direct communication between two GPUs and [22] offers direct
dimensionalmodeling.JohnWiley&Sons,2013.
communication between the Network Interface Card (NIC). Our [24] J.Li,H.-W.Tseng,C.Lin,Y.Papakonstantinou,andS.Swanson.Hippogriffdb:
workdiffersfromthoseworksintwoways.First,ourworkdemon- Balancingi/oandgpubandwidthinbigdataanalytics.VLDB,9(14),2016.
[25] Y.Liu,H.-W.Tseng,M.Gahagan,J.Li,Y.Jin,andS.Swanson.Hippogriff:
stratesthatlowI/ObandwidthfromtheSSDtotheGPUislargely
EfficientlyMovingDatainHeterogeneousComputingSystems.InICCD,2016.
duetothefailuretofullyutilizetheinternalparallelisminsidethe [26] S.MartelloandP.Toth.Knapsackproblems:algorithmsandcomputer
SSD.Toaddressthisissue, weadoptmulti-threadedI/Otoboost implementations.JohnWiley&Sons,Inc.,1990.
[27] M.A.O’NeilandM.Burtscher.Floating-pointdatacompressionat75gb/sona
theutilizationofthemultipledatatransferunits.Second,ourwork
gpu.InGPGPU,page7.ACM,2011.
offersdirectcommunicationbetweenaGPUandaPCIeSSD. [28] P.ONeil,E.ONeil,X.Chen,andS.Revilak.Thestarschemabenchmarkand
Severalworks[32,37]discussedthegapbetweenthroughputof augmentedfacttableindexing.InPerformanceevaluationandbenchmarking,
pages237–252.Springer,2009.
GPU kernel and off-chip memory bandwidth and proposed using
[29] R.PaghandF.F.Rodler.Cuckoohashing.Springer,2001.
compressiontoalleviatediscrepancy. HippogriffDB differsfrom [30] R.Patel,Y.Zhang,J.Mak,A.Davidson,J.D.Owens,etal.Parallellossless
these works in two aspects. First HippogriffDB tries to reduce datacompressionontheGPU.IEEE,2012.
thegapbetweenbetweentheGPUkernelandSSDI/Othroughput. [31] A.Pavlo,E.Paulson,A.Rasin,D.J.Abadi,D.J.DeWitt,S.Madden,and
M.Stonebraker.Acomparisonofapproachestolarge-scaledataanalysis.In
Second,HippogriffDB achievesbettercompressionratiobyusing SIGMOD,pages165–178.ACM,2009.
aggressiveandadaptivecompressionstrategies. [32] V.Sathish,M.J.Schulte,andN.S.Kim.Losslessandlossymemoryi/olink
compressionforimprovingperformanceofgpgpuworkloads.InPACT,pages
9. CONCLUSION 325–334.ACM,2012.
Inthispaper,weproposedHippogriffDB,anefficient,scalable [33] S.Seshadri,M.Gahagan,S.Bhaskaran,T.Bunker,A.De,Y.Jin,Y.Liu,and
S.Swanson.Willow:Auser-programmablessd.InOSDI,pages67–80,
heterogenousdataanalyticssystem.HippogriffDBisthefirstGPU- Broomfield,CO,Oct.2014.USENIXAssociation.
based data analytics that can scale up to support terabyte input. [34] B.Smith.Asurveyofcompresseddomainprocessingtechniques.Cornell
HippogriffDBreacheshighperformancebyfixingthehugeimbal- University,1995.
[35] J.Teuhola.Acompressionmethodforclusteredbit-vectors.Information
ancebetweenGPUkernelandI/Ousingcompressionandpeer-to-
processingletters,7(6):308–311,1978.
peertransferpath.HippogriffDB usesastreamingexecutionmodel [36] H.-W.Tseng,Y.Liu,M.Gahagan,J.Li,Y.Jin,andS.Swanson.Gullfoss:
toprocessdatasetslargerthantheGPUmemory.Ourcomprehen- Acceleratingandsimplifyingdatamovementamongheterogeneouscomputing
andstorageresources.Technicalreport.
siveexperimentshavedemonstratedthesuperiorityofHippogriff-
[37] N.Vijaykumar,G.Pekhimenko,A.Jog,A.Bhowmick,R.Ausavarungnirun,
DB intermsofbothscalabilityandperformance.test[24]. C.Das,M.Kandemir,T.C.Mowry,andO.Mutlu.Acaseforcore-assisted
bottleneckaccelerationingpus:enablingflexibledatacompressionwithassist
10. REFERENCES
warps.InISCA,pages41–53.ACM,2015.
[1] http://www.intel.com/content/dam/www/public/us/en/documents/ [38] K.Wang,Y.Huai,R.Lee,F.Wang,X.Zhang,andJ.H.Saltz.Accelerating
product-specifications/ssd-dc-s3700-spec.pdf. pathologyimagedatacross-comparisononcpu-gpuhybridsystems.VLDB,
[2] http://www.nvidia.com/object/tesla-servers.html. 5(11):1543–1554,2012.
[3] https://developer.nvidia.com/gpudirect. [39] K.Wang,K.Zhang,Y.Yuan,S.Ma,R.Lee,X.Ding,andX.Zhang.Concurrent
[4] http://blog.pmcs.com/project-donard-peer-to-peer-communication-with-nvm- analyticalqueryprocessingwithgpus.VLDB,7(11):1011–1022,July2014.
express-devices-part-two. [40] H.Wu,G.Diamos,S.Cadambi,andS.Yalamanchili.Kernelweaver:
[5] https://trademarks.justia.com/865/43/nvmedirect-86543720.html. Automaticallyfusingdatabaseprimitivesforefficientgpucomputation.In
[6] D.J.Abadi.Queryexecutionincolumn-orienteddatabasesystems.PhDthesis, MICRO,pages107–118.IEEEComputerSociety,2012.
MassachusettsInstituteofTechnology,2008. [41] Y.Yuan,R.Lee,andX.Zhang.Theyinandyangofprocessingdata
[7] D.J.Abadi,S.R.Madden,andN.Hachem.Column-storesvs.row-stores:How warehousingqueriesongpudevices.VLDB,6(10):817–828,2013.
differentaretheyreally?InSIGMOD,pages967–980.ACM,2008.
1658