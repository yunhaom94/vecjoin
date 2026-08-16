# GPUfs

**Source**: GPUfs.pdf
**Format**: .pdf

---

|     |                 | GPUfs: |     | Integrating |     |     | a         | File System |     | with |     | GPUs       |     |     |     |
| --- | --------------- | ------ | --- | ----------- | --- | --- | --------- | ----------- | --- | ---- | --- | ---------- | --- | --- | --- |
|     | MarkSilberstein |        |     |             |     |     | BryanFord |             |     |      |     | IditKeidar |     |     |     |
UniversityofTexasatAustin YaleUniversity Technion–IsraelInstituteofTechnology
marks@cs.utexas.edu bryan.ford@yale.edu idish@ee.technion.ac.il
EmmettWitchel
UniversityofTexasatAustin
witchel@cs.utexas.edu
As GPU hardware becomes increasingly general-purpose, it complexityandcodesizeofevensimpleGPUprogramsrequiring
is quickly outgrowing the traditional, constrained GPU-as-copro- fileaccess.Whileprogrammerscanexplicitlyoptimizedatamove-
cessor programming model. To make GPUs easier to program ment,thisperformanceisoftennotportabletonewgenerationsof
andimprovetheirintegrationwithoperatingsystems,wepropose hardware.Overtime,applicationcodetotransferandreuserecently
making the host’s file system directly accessible to GPU code. computed data becomes entwined with program logic, making it
GPUfs provides a POSIX-like API for GPU programs, exploits hardtomaintainfunctionalityandperformance.
GPUparallelismforefficiency,andoptimizesGPUfileaccessby Drawing an analogy to pre-virtual memory days, applications
extending the host CPU’s buffer cache into GPU memory. Our often managed their own address spaces efficiently using manual
experiments, based on a set of real benchmarks adapted to use overlays, but this complex and fragile overlay programming ulti-
our file system, demonstrate the feasibility and benefits of the matelyprovednotworththeeffort.GPUsarequicklyevolvingto-
GPUfsapproach.Forexample,aself-containedGPUprogramthat wardgeneralhigh-performanceprocessorsusefulforawidevari-
searchesforasetofstringsthroughouttheLinuxkernelsourcetree etyofmassivelyparallel,throughput-orientedtasks,andwebelieve
runsoverseventimesfasterthanonaneight-coreCPU. GPUprogrammingshouldreapthesamebenefitsfromthefilesys-
temabstractionenjoyedbyCPUprogrammersfordecades.
| CategoriesandSubjectDescriptors |     |     |     | D.4.7[OperatingSystems]: |     |     |     |     |     |     |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | ------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
WeproposeGPUfs,aninfrastructurethatexposesthefilesys-
| OrganizationandDesign; |     |     | I.3.1[HardwareArchitecture]:Graph- |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
temAPItoGPUprograms,bringingtheconvenienceandpowerof
icsprocessors
|     |     |     |     |     |     |     |     | file systems | to GPU | developers. |     | GPUfs | offers | compute-intensive |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ------ | ----------- | --- | ----- | ------ | ----------------- | --- |
Keywords Operating Systems Design, GPGPUs, File Systems, applications a convenience well-established in the CPU context:
accelerators tobelargelyoblivioustowheredataislocated—whetherondisk,
|     |     |     |     |     |     |     |     | in main | memory, | in a GPU’s | local | memory, | or  | replicated | across |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------- | ---------- | ----- | ------- | --- | ---------- | ------ |
1. Introduction several GPUs or other coprocessors. Further, GPUfs lets the OS
optimizedataaccesslocalityacrossindependently-developedGPU
| The file | system | is a successful, |     | proven | operating | system | abstrac- |     |     |     |     |     |     |     |     |
| -------- | ------ | ---------------- | --- | ------ | --------- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
computemodules,usingapplication-transparentcachinganddata
tion,whichbenefitsdeveloperproductivitybydecouplingtheap-
replication,muchlikeatraditionalOS’sbuffercacheoptimizesac-
plication’slogicalviewofstoragefromlow-leveldetailsofthelo-
cesslocalityacrossmulti-processcomputationpipelines.Aunified
cationandtypeofdevicesonwhichdataphysicallyresides.Mod-
fileAPIinterfaceabstractsawaythelow-leveldetailsofdifferent
| ern file | systems | have buffer | caches | enabling | the | system | to opti- |     |     |     |     |     |     |     |     |
| -------- | ------- | ----------- | ------ | -------- | --- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
GPUhardwarearchitecturesandtheircomplexinter-devicemem-
mizedataaccesslocalityacrosscooperatingprocessesormodules,
oryconsistencymodels,improvingcodeandperformanceportabil-
e.g.,bykeepingfrequently-accesseddataorintermediateresultsin
|     |     |     |     |     |     |     |     | ity. GPUfs | expands | the | appeal | of GPU | programming | by offering |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------- | --- | ------ | ------ | ----------- | ----------- | --- |
memorytominimizethecostofaccessestoslowstoragedevices.
|     |     |     |     |     |     |     |     | familiar, | well-established |     | data | manipulation | interfaces | instead | of  |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ---------------- | --- | ---- | ------------ | ---------- | ------- | --- |
UnlikeCPUapplications,programsrunningongraphicalpro-
proprietaryGPUAPIs.Finally,GPUfsallowsGPUcodetobeself-
cessingunits(GPUs)currentlyhavenodirectaccesstofilesonthe
sufficient,bysimplifyingoreliminatingthecomplexCPUsupport
| host OS | file system. | Although |     | the power, | functionality, |     | and util- |     |     |     |     |     |     |     |     |
| ------- | ------------ | -------- | --- | ---------- | -------------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
codetraditionallyrequiredtofeeddatatoGPUcomputations.
| ity of | today’s GPUs | now | extend | far beyond | graphics | processing, |     |     |     |     |     |     |     |     |     |
| ------ | ------------ | --- | ------ | ---------- | -------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Asasimpleexample,considermultiplyingamatrixbyavector.
thecoprocessor-styleGPUprogrammingmodelstillrequiresdevel-
GPUsexcelatsuchcomputationaltasks,butmostGPUprograms
operstomanagemovementofdataexplicitlybetweenits“home”
willassumethatthematrixfitsinGPUmemory.Iftheinputmatrix
| in the | CPU’s main | memory | and | the GPU’s | local | memory. | Man- |     |     |     |     |     |     |     |     |
| ------ | ---------- | ------ | --- | --------- | ----- | ------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
becomeslargerthanGPUmemory,theprogrammustbeinvasively
| aging | data transfers | between | CPU | and | GPU increases | the | design |          |         |            |           |             |     |          |     |
| ----- | -------------- | ------- | --- | --- | ------------- | --- | ------ | -------- | ------- | ---------- | --------- | ----------- | --- | -------- | --- |
|       |                |         |     |     |               |     |        | modified | and its | complexity | increases | sharply—for |     | example, | the |
inputmustbesplitintochunks,eachchunkprocessedseparately,
anddatatransfersmustbeoverlappedwithcomputationforgood
performance.Filesystemstraditionallyexcelatinsulatingthede-
Permissiontomakedigitalorhardcopiesofallorpartofthisworkforpersonalor
|     |     |     |     |     |     |     |     | veloper from | such | low-level | data | movement | details. | File systems |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ---- | --------- | ---- | -------- | -------- | ------------ | --- |
classroomuseisgrantedwithoutfeeprovidedthatcopiesarenotmadeordistributed
|     |     |     |     |     |     |     |     | also excel | as a communication |     |     | substrate | for composing | different |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------------------ | --- | --- | --------- | ------------- | --------- | --- |
forprofitorcommercialadvantageandthatcopiesbearthisnoticeandthefullcitation
onthefirstpage.Tocopyotherwise,torepublish,topostonserversortoredistribute programs. Currently, GPUs are more often used for stand-alone
tolists,requirespriorspecificpermissionand/orafee. monolithic applications, because the complexity of integrating a
| ASPLOS’13, | March16–20,2013,Houston,Texas,USA. |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Copyright(cid:13)c 2013ACM978-1-4503-1870-9/13/03...$15.00

GPUprogramintoacomplexprocessingpipelineistoohigh.Data ThenextsectionprovidesanoverviewoftheGPUarchitecture.
movementisamajorsourceofthiscomplexity. Wethenexplainandjustifythedesignchoicesthatwemadewhile
With GPU hardware changing so rapidly, a key design chal- buildingGPUfs,followedbytheimplementationdetailsofGPUfs
lengeforGPUfsistofocusonpropertieslikelytobeessentialto onNVIDIAFERMIGPUs.WeevaluatetheGPUfsprototypeim-
theperformanceoffutureaswellascurrentGPUs.Someproper- plementationinSection5,andconcludewithrelatedwork.
tiesofcurrentGPUs,suchasparticularmemoryconsistencymod-
els,maycontinuechangingrapidlyandunpredictably.Webelieve,
however,thattwokeycharacteristics—dataparallelismanddepen-
2. GPUarchitectureoverview
denceonaccesslocality—willpersistasGPUarchitecturesevolve,
andGPUfsmustaddresstheseconcernsinordertosucceed. Thissectionprovidesabrief,simplifiedoverviewoftheGPUsoft-
GPUs are designed to optimize for massive data parallelism, ware/hardwaremodel,highlightingthepropertiesthatareparticu-
by sharing a limited set of “control plane” logic—for instruction larlyrelevanttoGPUfs.WeuseNVIDIACUDAterminologybe-
fetch,memorymanagement,etc.—amongfarmorenumerous“data
causeweimplementGPUfsonNVIDIAcards;formoredetailswe
plane”resourcessuchasvectorALUs.Asaresult,GPUsareeffi-
referthereadertotheCUDAreference[20].
cientwhenthousandsoflightweightthreadsrunsimilaroridentical
GPUsaremulticoreprocessors.Eachcore,calledmultiproces-
code,withlittlecontrol-flowvariation.Thetraditionalfilesystem
|         |           |      |         |           |             |     |          | sor or MP, | features | a wide | SIMD | vector | unit, which | a   | hardware |
| ------- | --------- | ---- | ------- | --------- | ----------- | --- | -------- | ---------- | -------- | ------ | ---- | ------ | ----------- | --- | -------- |
| API was | not built | with | such an | execution | environment |     | in mind. |            |          |        |      |        |             |     |          |
schedulermultiplexesbetweenmultipleexecutioncontexts.
| In GPUfs,      | therefore, | both    | the API  | semantics  |     | and the      | file system |         |       |            |      |              |     |              |     |
| -------------- | ---------- | ------- | -------- | ---------- | --- | ------------ | ----------- | ------- | ----- | ---------- | ---- | ------------ | --- | ------------ | --- |
|                |            |         |          |            |     |              |             | A GPU’s | basic | sequential | unit | of execution |     | is a thread. | GPU |
| implementation |            | must be | designed | to support |     | such massive | paral-      |         |       |            |      |              |     |              |     |
hardwaregroupsanumberofthreads(32inNVIDIAGPUs)into
lelism,efficientlyallowingthousandsofGPUhardwarethreadsto
warps,andexecutesallthreadsinawarpconcurrentlyinlockstep
invokeopen,close,read,orwritecallssimultaneously.
onasinglehardwarevectorunit.EachMPmultiplexesmanywarps
Second,memorylocalityisvitalforperformance,duetotheva-
|                 |     |        |        |                  |     |             |     | onto the | same SIMD | unit | to maximize | hardware |     | utilization, | exe- |
| --------------- | --- | ------ | ------ | ---------------- | --- | ----------- | --- | -------- | --------- | ---- | ----------- | -------- | --- | ------------ | ---- |
| riety in memory |     | system | speeds | and interconnect |     | topologies. | Our |          |           |      |             |          |     |              |      |
cutingonewarpwhileanotherisblockedonamemoryaccessfor
| work currently | focuses |     | on discrete | GPUs, | which | today | provide |     |     |     |     |     |     |     |     |
| -------------- | ------- | --- | ----------- | ----- | ----- | ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
example.Severalwarps(upto32)formathreadblock.Threadsin
higherperformancethanGPUsintegratedwithCPUsonthesame
athreadblockarealwaysexecutedonasingleMP.Multiplethread-
| die. Discrete | GPUs | have | high-bandwidth |     | DRAM, | but | connect to |     |     |     |     |     |     |     |     |
| ------------- | ---- | ---- | -------------- | --- | ----- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
blocksformasinglecompleteGPUprogram,oftentermedakernel
| the host | via a peripheral |     | interconnect |     | bus, typically |     | PCIe. These |     |     |     |     |     |     |     |     |
| -------- | ---------------- | --- | ------------ | --- | -------------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
(unrelatedtoanOSkernel).
busesarehighlatencyandlowbandwidthrelativetoDRAMbuses,
|             |       |          |      |        |           |         |      | A CPU | application | using | the | GPU enqueues |     | all threadblocks |     |
| ----------- | ----- | -------- | ---- | ------ | --------- | ------- | ---- | ----- | ----------- | ----- | --- | ------------ | --- | ---------------- | --- |
| effectively | 6GB/s | for PCIe | 2.0. | Future | multi-GPU | systems | with |       |             |       |     |              |     |                  |     |
comprisingakernelintoasingleglobalhardwarequeue.Thehard-
| both integrated | and | discrete | GPUs | will | further | increase | variance |     |     |     |     |     |     |     |     |
| --------------- | --- | -------- | ---- | ---- | ------- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
wareschedulerdispatchesthreadblocksontoMPswhileassigning
| in hardware | speeds | and | topologies. | The | only | way for | GPUfs to |     |     |     |     |     |     |     |     |
| ----------- | ------ | --- | ----------- | --- | ---- | ------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
uniqueIDstoeachthreadblockandeachthreadintheblock.The
performwellinsuchsystemsiswithcomprehensiveOSmanage-
|     |     |     |     |     |     |     |     | scheduler | strives | to maximize |     | the number | of warps | concurrently |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------- | ----------- | --- | ---------- | -------- | ------------ | --- |
mentofthememorysystem.TheOSmusthaveaglobalpolicyto
|     |     |     |     |     |     |     |     | scheduled | on an | MP without | exceeding |     | MP hardware |     | resources |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----- | ---------- | --------- | --- | ----------- | --- | --------- |
managedataplacementanddatareuseacrossCPUandGPUmem-
suchasavailableregisters.Givensufficienthardwareresourcesthe
| ories based | on dynamic |     | access | patterns. | GPUfs’s | buffer | cache is |     |     |     |     |     |     |     |     |
| ----------- | ---------- | --- | ------ | --------- | ------- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
schedulercanschedulemultipleindependentkernelsatonce.
distributedacrossallsystemmemoriestoenablesuchpolicies.
|             |     |             |                |     |     |       |           | Challenges    | for | GPUfs.     | There | are two      | characteristics |     | of the  |
| ----------- | --- | ----------- | -------------- | --- | --- | ----- | --------- | ------------- | --- | ---------- | ----- | ------------ | --------------- | --- | ------- |
| We evaluate |     | a prototype | implementation |     | of  | GPUfs | on an x86 |               |     |            |       |              |                 |     |         |
|             |     |             |                |     |     |       |           | GPU execution |     | model that | are   | particularly | important       | in  | design- |
PCwithfourNVIDIAGPUs,usingseveralmicrobenchmarksand
ingsystemabstractionssuchasafilesystemAPIonaGPU.First,
| two realistic | I/O             | intensive | applications. |     | All the | presented | GPUfs   |               |       |     |               |         |     |             |      |
| ------------- | --------------- | --------- | ------------- | --- | ------- | --------- | ------- | ------------- | ----- | --- | ------------- | ------- | --- | ----------- | ---- |
|               |                 |           |               |     |         |           |         | once invoked, | warps | run | to completion | without |     | preemption. | This |
| workloads     | are implemented |           | entirely      | in  | the GPU | kernel    | without |               |       |     |               |         |     |             |      |
implies,forexample,thatusingspinlockstosynchronizebetween
CPU-sideapplicationcode.Insequentialfileaccessbenchmarks,a
|     |     |     |     |     |     |     |     | running threads |     | in the same | kernel | may | lead to | a deadlock. | Sec- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ----------- | ------ | --- | ------- | ----------- | ---- |
trivial16lineGPUkernelusingGPUfsoutperformsasimpleGPU
ond,thehardwareschedulesthreadblocksforexecutioninanon-
implementationwithmanualdatatransferbyupto40%,andcomes
deterministicorder,drivensolelybythegoalofmaximizinghard-
within5%ofahand-optimizeddouble-bufferingimplementation.
wareutilization.Thisbehaviorcreateschallengesinimplementing
AmatrixmultiplybenchmarkillustrateshowGPUfseasilyenables
|     |     |     |     |     |     |     |     | reference-count | based | parallel |     | versions of | open | and close | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | ----- | -------- | --- | ----------- | ---- | --------- | ---- |
accesstodatasetslargerthantheGPU’sphysicalmemory,performs
calls,forexample,asdescribedlater(§4).
| from 5%    | to 4× | faster than | the      | manual | double-buffering |         | typical   |     |     |     |     |     |     |     |     |
| ---------- | ----- | ----------- | -------- | ------ | ---------------- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
| in current | GPU   | code, and   | is about | 2×     | smaller          | in code | size. Two |     |     |     |     |     |     |     |     |
paralleldataanalysisapplications,prioritizedimagematchingand
| string search, | highlight |     | the ability | of  | GPUfs | to support | irregular | 3. Design |     |     |     |     |     |     |     |
| -------------- | --------- | --- | ----------- | --- | ----- | ---------- | --------- | --------- | --- | --- | --- | --- | --- | --- | --- |
workloadsinwhichparallelthreadsopenandaccessdynamically-
|     |     |     |     |     |     |     |     | This section | outlines | the | GPUfs | API and | file system | semantics, |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | -------- | --- | ----- | ------- | ----------- | ---------- | --- |
selectedfilesofvaryingsizeandcomposition.
focusingonthesimilaritiesanddifferencesfromthePOSIXAPI,
Thispapermakesthefollowingmaincontributions.
|     |     |     |     |     |     |     |     | and the properties |     | of GPUs | that | motivate | these | design | choices. |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | ------- | ---- | -------- | ----- | ------ | -------- |
1. ThefirstPOSIX-likefilesystemAPIweareawareofforGPU
|           |      |           |          |     |       |             |         | We believe             | that | our design | reflects | several         | key | properties | of data |
| --------- | ---- | --------- | -------- | --- | ----- | ----------- | ------- | ---------------------- | ---- | ---------- | -------- | --------------- | --- | ---------- | ------- |
| programs, | with | semantics | modified |     | to be | appropriate | for the |                        |      |            |          |                 |     |            |         |
|           |      |           |          |     |       |             |         | parallel architectures |      | that       | will     | apply to future | as  | well as    | current |
data-parallelGPUprogrammingenvironment.
|     |     |     |     |     |     |     |     | GPUs and | hybrid | processors. |     | This section | focuses | on  | the high- |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------ | ----------- | --- | ------------ | ------- | --- | --------- |
2. Adesignandimplementationofagenericsoftware-onlybuffer
levelaspectsofthedesignandAPIthatarevisibletoapplications
| cache | mechanism | for | GPUs, | employing |     | a lock-free | traversal |     |     |     |     |     |     |     |     |
| ----- | --------- | --- | ----- | --------- | --- | ----------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
usingGPUfs,deferringlower-levelimplementationconsiderations
algorithmfordataparallelefficiency.
largelyinvisibletoapplicationsto§4.
| 3. A proof-of-concept |     |     | implementation |     | of GPUfs | on  | NVIDIA |        |               |     |              |     |        |     |          |
| --------------------- | --- | --- | -------------- | --- | -------- | --- | ------ | ------ | ------------- | --- | ------------ | --- | ------ | --- | -------- |
|                       |     |     |                |     |          |     |        | Figure | 1 illustrates | the | architecture | of  | GPUfs. | CPU | programs |
FERMIGPUs[21],supportingmulti-GPUsystems.
areunchanged,butGPUprogramscanaccessthehost’sfilesystem,
| 4. A quantitative |     | evaluation | of  | a GPU | file system | that | identifies |             |         |        |      |                   |     |           |     |
| ----------------- | --- | ---------- | --- | ----- | ----------- | ---- | ---------- | ----------- | ------- | ------ | ---- | ----------------- | --- | --------- | --- |
|                   |     |            |     |       |             |      |            | via a GPUfs | library | linked | into | the application’s |     | GPU code. | The |
sensitiveperformanceparameterssuchaspagesize,andevalu-
|     |     |     |     |     |     |     |     | GPUfs library | works | with | the host | OS on | the CPU | to coordinate |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | ----- | ---- | -------- | ----- | ------- | ------------- | --- |
atesefficiencyrelativetohand-codedsolutions.
thefilesystem’snamespaceanddata,cachingfiledatainbothCPU
andGPUmemorylargelytransparentlytotheapplication.

Asdetailedbelow,considerationsofdataparallelismalsomo-
tivatedseveralotherdesigndecisionswemadeinGPUfs:tomini-
mizeper-openfilestatebyeliminatingseekpointers,decouplethe
synchronizingside-effectstraditionallyboundintoAPIcallssuch
as close, and constrain mmap semantics to avoid the need for
complexmemorymanagementoncriticaldataparallelpaths.
Locality-optimized file consistency model. GPU memory sys-
tems have pronounced NUMA characteristics, offering far more
bandwidth—over30×incurrentsystems—andlowerlatenciesto
access local GPU memory than to main CPU memory or to that
of other discrete GPUs. Performance therefore critically depends
onminimizingfiledatamovementbetweentheGPUandCPU,or
betweenGPUs.ToenableeachGPUtoaccesslocallycachedfile
dataasindependentlyaspossible,GPUfsimplementsaweakcon-
sistencymodelsimilartotheprivateworkspacemodelinDetermi-
Figure1. GPUfsarchitecture nator [1], and to distributed file systems such as LOCUS [26] or
AFS[10].OnceafilepageisaccessedandcachedonaGPU,its
threadscanreadandwritetothatpagelocallywithoutfurthercom-
3.1 GPUfsdesignprinciples municationwiththehost—evenifthehostand/orotherGPUsmay
Two key principles underly the design of GPUfs and the ways concurrently read and/or modify that file. GPUfs guarantees that
in which it deviates from traditional POSIX semantics: making localfilemodificationspropagatetomainCPUmemoryonlywhen
common API operations efficient when executed in data parallel theapplicationexplicitlysynchronizesthefileorindividualpages
fashion, and choosing consistency and data movement semantics withbackingstore,therebypersistingitscontent.Thesemodifica-
that maximizes file data access locality and minimizes expensive tionsbecomevisibletootherGPUswhentheyre-openthefile.
globaltransfersbetweenGPUandhostmemory.
Concurrentnon-overlappingwritestothesamefile. Inthepo-
APIdesignforstructureddataparallelism. Aswesummarized tentiallycommonsituationinwhichaparalleltaskisexecutingon
in§2,GPUhardwareoffersparallelismatmultiplegranularities, severalGPUsandCPUsinonesystem,thesamefilemaybewrite-
whichcombinetoachievehighthroughput.Atfinergranularities, sharedamongallexecutingprocessors.Concurrenttaskstypically
the hardware achieves efficiency by sharing control logic across write into different parts of the file: i.e., to the particular range
all threads comprising a warp. Processing is efficient when these each is assigned to produce. Workspace consistency allows mul-
threadsfollowthesamecodepathsinlockstep,buthighlyineffi- tiplewriterswithoutcausingmemorypagethrashingbetweendif-
cientifthethreadsfollowdivergentpaths:allthethreadsinawarp ferentGPUs,asasingle-writerMESIprotocolwouldexhibit.An
mustexploreallpossibledivergentpathstogether,merelymasking importantchallenge,however,isthatGPUfsmustbeabletohan-
instructionsapplicableonlytosomethreads. dlefalsesharingofbuffercachepagesamongdifferentGPUs.As
Because of these hardware characteristics, a key semantic de- aresult,ithastodeterminewhichspecificportionsofagivenpage
signdecisionforanyGPU-accessiblelibraryorsystemAPIisthe were modified on a given GPU when propagating those modifi-
granularity at which API calls are to be invoked. Operations af- cations to the host, to avoid accidentally reverting other portions
fectinggloballysharedfilesystemstate,suchasopenandclose of the same page that have been modified concurrently by other
calls,involvecontrol-flowheavyoperationsandrequireserializa- GPUs.Ingeneral,forfilesopenedforwriting,GPUfsmustmain-
tion.EvenbasicreadandwriteAPIcallsrequireupdatestothe taintwocopiesofeachcachedblockperGPU:aworkingcopyto
file system’s buffer cache data structures. If GPUfs allowed each which local writes are performed, and a pristine copy preserved
applicationtoinvoketheseoperationsatthreadgranularity—e.g., whenthepageisfirstread.GPUfs“diffs”theworkingandthepris-
each thread opening different files or reading different blocks— tine copies at the next synchronization point to determine which
these threads would quickly encounter divergent control paths byteshavebeenmodifiedandshouldbewrittenback.
within GPUfs, entailing hardware serialization and inefficiency. An important common case is write-once file access, where
Moreover,hardwareprovidesthehighestmemorythroughputwhen GPU application threads produce a new output file without ever
the accesses of all threads in a warp are aligned and can be coa- reading it or overwriting already-written data. To avoid the costs
lescedintoonememorytransaction. ofbothmakingandstoringtwocopiesoffileblocksinthiscase,
Forthesereasons,GPUfsfollowscommonGPUprogramming GPUfs attaches special semantics to files an application opens in
practicesbyrequiringallthreadsinawarptocooperatetoperform a new (O_GWRONCE) open mode. GPUfs never reads pages of
the same operation, and requires applications to invoke the file suchfilesfromthehostintotheGPUcache,andinsteadimplicitly
systemAPIatwarp—ratherthanthread—granularity. assumes the pristine copy of any file block is all zeros—even if
Thus, all application threads in a warp must invoke the same the host or some other GPUs may in fact have already written
GPUfs call, with the same arguments, at the same point in ap- to parts of that page in the underlying file. As a result, when the
plication code. These lockstep calls together comprise one logi- GPUpropagateslocallywrittenpagesbacktothehost,determining
cal GPUfs operation. For example, GPUfs does not allow an ap- which bytes have been modified locally reduces to a trivial “diff
plication to open one file per thread in parallel, but only one file againstzeros.”ThesesemanticsimplythatoneGPU’sthreadswill
per warp. On the other hand, this warp-granularity API allows typicallyneverobservewritesfromotherprocessorswhilethefile
theGPUfsimplementationtoparallelizethehandlingofAPIcalls is opened for writing, and that multiple GPUs’ concurrent writes
acrossthreadsintheinvokingwarp—parallelizingfiletablesearch areguaranteedtomergecorrectlyonlyifthreadswriteonlyonceto
operationsordatamovement,forexample.Ourprototypecurrently disjointfileareas.Webelievetheseconstraintsareconsistentwith
makes use of this capability only in a few performance-critical commonpracticesinfile-producingdataparallelapplications,and
cases,highlightingthisprinciplebyacceleratingmemorytransfers thusplacereasonablesemanticdemandsonapplicationsinorderto
betweentheuserandsystembuffersinread/writecalls. enableimportantdatamovementoptimizations.

API Explanation
gread/gwrite Readsandwritesalwayssupplyexplicitfileoffsets,toavoidthefileseekpointerbecomingasequentialbottleneck.
gopen/gclose Openandclosefilesinthenamespaceofasinglethreadblock.Multipleconcurrentopenrequeststoopenorclosethesame
filearecoalescedintooneopen/close.Theprecisesemanticsarefurtherdiscussedinthetext.
gfsync Synchronouslywritebacktothehostalldirtyfilepagesthatarecurrentlyneithermemory-mappednorbeingaccessed
concurrentlyviagreadorgwritecalls.
gmmap/gmunmap Arelaxedformofmmapthatavoidsdoublecopiesingread/gwrite.ImposesAPIconstraintsdiscussedinthetext.
gmsync Write back a specificdirty page to the host. The applicationmust coordinate calls to gmsync with updates by other
threadblocks.
gunlink Removeafile.FilesunlinkedontheGPUhavetheirlocalbufferspacereclaimedimmediately.
gfstat Retrievefilemetadata.Filesizereflectsfilesizeatthetimeofthefirstgopencallthatopenedthisfileonthehost.
gftruncate Truncateafiletoagivensize,andreclaimanyrelevantpagesfromthebuffercache.
Table1. GPUfsAPI,anddiscussionofrelaxedfilesystemsemanticsforGPUfs.
3.2 GPUfsAPI tics cause many costly write-backs due to the nondeterministic
GPUscheduler.Evenifwereferencecountfiles,itiscommonfor
Guidedbytheaboveprinciples,wenowexploretheirimplications
severalthreadblockstoopen,write,thenclosethefile,sendingits
on specific parts of the GPUfs API. GPUfs attempts to preserve
referencecounttemporarilytozerobeforeotherthreadblocksare
thePOSIXAPI’sfamiliarsemanticswhenpractical,whilediverg-
scheduledthatopenthefileagain.Inourexperiencethissituation
ing as needed for efficiency in GPU environments. Table 1 sum-
can be common, and synchronizing files each time the reference
marizes the API and its deviations from from POSIX semantics.
countdropstozeroresultsinmanyunnecessarywrites.
Weprependa‘g’toGPUfs’APIfunctionnamestoemphasizethat
GPUfs therefore decouples the file “close” and “synchronize”
theirsemanticsdeviatesfromstrictPOSIX.
operations.Inparticular,gclosedoesnotpropagatelocallywrit-
Openandfiledescriptors. Traditionally,ifseveralPOSIXthreads tendatabacktotheCPU,ortootherGPUs,untiltheapplication
concurrently open the same file, each thread obtains a fresh file explicitlysynchronizesfiledata,bycallinggfsynctosynchronize
descriptorinaprocess-globalfiletable,eachdescriptorcontaining eitheranentirefileoraspecificoffsetrange.
aseparateseekpointerandotherfile-openstate.ForGPUkernels
weexpectittobecommonplacetoopenthesamefileinparallel
acrosshundredsofconcurrentlyrunningwarps,forexamplewhen
each warp is assigned a given chunk of a given file. Preserving File mapping. GPUfs allows GPU threads to map portions of
POSIXsemanticswouldinsuchcasesrequirethesegopencalls files directly into local GPU memory via gmmap/gmunmap. As
tocoordinatetheefficientsimultaneousallocationandinitialization withtraditionalmmap,filemappingofferstwobenefits:theconve-
oflarge“batches”offiledescriptorsatonce,acomplexandlikely niencetoapplicationsofnothavingtoallocateabufferandsepa-
inefficient file descriptor management task. In GPUfs, therefore, ratelyreaddataintoit,andopportunitiesforthesystemtoimprove
“filedescriptors”donotrepresentindividualfileopensbutmerely performancebyavoidingunnecessarydatacopying.
correspond directly to files, so that all GPU threads opening the Full-featuredmemorymappingfunctionalityrequiresuser-pro-
same file obtain a single shared file descriptor. GPUfs forwards grammable hardware virtual memory, which current GPUs lack.
thefirstgopencallonagivenfiletotheCPUtoopenthefileon EveninfutureGPUsthatmayoffersuchcontrol,weexpectper-
theunderlyinghostfilesystem.GPUfsthenreferencecountsthese formanceconsiderationstorendertraditionalmmapsemanticsim-
openfiles,soagopenonanalready-openfilejustincrementsthe practical in data parallel contexts. GPU hardware shares control
file’sopencountwithoutrequiringCPUcommunication. planelogic,includingmemorymanagement,acrosscomputeunits
Besides the standard open flags, gopen introduces two new runninghundredsorthousandsofthreadsatonce.Thus,anytrans-
flagsenablingusefulperformanceoptimizations. lation change has global impact, likely requiring synchronization
• O GWRONCE:Createsanewwrite-onlyfile,inwhichtheappli- tooexpensiveforfine-grainedusewithinindividualthreads.
cationwillwriteeachbyteatmostonce.Ifdataisoverwritten, GPUfs therefore offers a more relaxed alternative to mmap,
partial updates may occur. This flag eliminates fetching of file permittingmoreefficientimplementationinadataparallelcontext
contentfromtheCPUbeforewriting,asdescribedabovein§3.1. byavoidingfrequenttranslationupdates.Thereisnoguaranteethat
• O NOSYNC:CreatesatemporaryfiletobeusedonlybytheGPU gmmap will map the entire file region the application requests—
openingit.GPUfsneverwritesthefile’sdatatodiskonclose,and instead it may map only a prefix of the requested region, and
neverwritesitatallexcepttoreclaimGPUbuffercachespace. returnthesizeofthesuccessfullymappedprefix.Further,gmmap
isnotguaranteedevertosucceedwhentheapplicationrequestsa
Read and write. Because GPUfs dispenses with most per-open
mappingataparticularaddress:i.e.,MMAP_FIXEDmaynotwork.
state,itsfiledescriptorshavenoseekpointers.Asaresult,gread
Finally,gmmapdoesnotguaranteethatthemappingwillhaveonly
and gwrite correspond to POSIX’s pread and pwrite—
the requested permissions: mapping a read-only file may return
taking file offsets explicitly as arguments—instead of the tradi-
a pointer to read/write memory, and GPUfs trusts the application
tionalstreamingreadandwrite.Thisconventionmatchescom-
nottomodifythatmemory.Improperupdatestosuch“quasi-read-
mon practice in parallel workloads anyway [14], and application
only”pagesareneverpropagatedbacktothehostCPU,soGPUfs
threadscanmaintaintheirownexplicitseekpointersifrequired,as
ensureshostfilesystemintegritydespitelessstringentpage-level
wedemonstrateinourexperiments(§5.2.2).
accessenforcementondataresidentinlocalGPUmemory.
Close and synchronization. POSIX semantics require the con- Theseloosersemanticsultimatelyincreaseefficiencybyallow-
tentsofafiletobesynchronizedtostablestorage(e.g.,disk)after ingGPUfstogivetheapplicationpointersdirectlyintoGPU-local
eachclose.Inthecommon-casesequenceofgopen,gwrite, buffercachepages,residinginthesameaddressspace(andprotec-
gclose,executedbymanyGPUthreads,POSIXcloseseman- tiondomain)astheapplication’sGPUcode.

3.3 Buffercache
Anessentialcomponentofafilesystemlayerisabuffercache.In
| CPUs, the | buffer | cache minimizes |     | disk | accesses, | which | can be a |     |     |     |     |     |     |
| --------- | ------ | --------------- | --- | ---- | --------- | ----- | -------- | --- | --- | --- | --- | --- | --- |
thousandtimesslowerthanmemory.TheGPUpagecacheextends
| this principle | to  | GPU file | accesses, | caching | file | data in | fast local |     |     |     |     |     |     |
| -------------- | --- | -------- | --------- | ------- | ---- | ------- | ---------- | --- | --- | --- | --- | --- | --- |
GPUmemorytominimizetransfersacrosstherelativelyslowand
bandwidth-constrainedperipheralinterconnect.
| The role      | of the  | buffer         | cache            | extends | beyond    | simple            | caching. |     |     |     |     |     |     |
| ------------- | ------- | -------------- | ---------------- | ------- | --------- | ----------------- | -------- | --- | --- | --- | --- | --- | --- |
| As on a       | CPU, a  | GPU buffer     | cache            | enables | further   | performance       |          |     |     |     |     |     |     |
| optimizations | such    | as read-ahead, |                  | data    | transfer  | scheduling,       | and      |     |     |     |     |     |     |
| asynchronous  | writes. | In             | multi-processor, |         | multi-GPU | systems           | the      |     |     |     |     |     |     |
| buffer cache  | spans   | multiple       | GPUs             | and     | serves    | as an abstraction |          |     |     |     |     |     |     |
hidingthelow-leveldetailsofthesharedI/Osubsystem.
|     |     |     |     |     |     |     |     | Figure 2. Main | GPUfs | software | layers and | their location | in the |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | ----- | -------- | ---------- | -------------- | ------ |
Duetolimitationsinthesoftwareinterfacesavailabletotoday’s
softwarestackandphysicalmemory.
GPUhardware,GPUfscurrentlyimplementsaprivateGPUbuffer
cacheforeachhostCPUprocess:buffercachepagesarenotshared
acrosshostapplications,asintheOS-maintainedbuffercacheon
thehostCPU.Programmablememoryprotectioninterfacesonfu-
tioncaches.Anddespitetheseadditionalcosts,wefindGPUfsto
| ture GPUs | could | eliminate | this | limitation, | enabling | a true | cross- |     |     |     |     |     |     |
| --------- | ----- | --------- | ---- | ----------- | -------- | ------ | ------ | --- | --- | --- | --- | --- | --- |
havegoodperformanceinusefulapplicationscenarios(§5).
user,cross-applicationGPUbuffercache.1Ontheotherhand,mul-
GPUfsbydesignimposesnooverheadonGPUkernelsthatuse
tiplekernelslaunchedbythesameprocesscansharedataviathe
nofilesystemfunctionality.Wedeliberatelyavoideddesignalter-
buffercache,andweusethatfeatureinourexperiments(§5.1.3).
|     |     |     |     |     |     |     |     | natives involving | “daemon” | threads: | i.e., persistent | GPU | threads |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | -------- | -------- | ---------------- | --- | ------- |
dedicatedtofilesystemmanagement,suchaspagingorCPU-GPU
| Replacementpolicies. |     | AGPUfilesystemallowstheOStocoor- |     |     |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
synchronization.Whileenablingmoreefficientimplementationof
dinatefilesystemreplacementpoliciesacrossallhardwareinthe
thefilesystemlayer,suchthreadswouldviolatethe“pay-as-you-
| system. For | example, | if the | GPU | is idle, | the OS | could | use GPU |     |     |     |     |     |     |
| ----------- | -------- | ------ | --- | -------- | ------ | ----- | ------- | --- | --- | --- | --- | --- | --- |
go”designprincipletobediscussedfurtherin§4.2
memoryasastagingareafordatabeforewritingittodisk.AsGPU
| computations | evolveto | become |     | partof | heterogeneous | processing |     |     |     |     |     |     |     |
| ------------ | -------- | ------ | --- | ------ | ------------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
pipelines,OSmanagementoffilesystemdatawillenablesignifi-
4. Implementation
cantperformanceoptimizations.
WhetherstandardLRUreplacementpoliciesforCPUswillbe
appropriatefortheGPUbuffercacheisnotyetclear.Typicalfile ThissectiondescribesourGPUfsprototypeforNVIDIAFERMI
access patterns in GPU applications remain to be seen, but we GPUs.Wefirstoutlinetheprototype’sstructureandhowitimple-
already observe accesses to be fairly chaotic even in workloads mentstheaboveAPI,thenexploreimplementationdetailsandchal-
with logically sequential accesses, due to the non-deterministic lenges.Wecoverbuffercachemanagement,GPU-CPUcommuni-
schedulingofthreadblocksintheGPUexecutionmodel. cation,fileconsistencymanagement,andlimitationsofthecurrent
prototype.Someoftheseimplementationchoicesarelikelytobe
Failure semantics. GPUfs has failure semantics similar to the affectedbyfutureGPUevolution,butwefeelthatmostconsider-
CPU page cache: on failure, file updates not yet committed to ationsdiscussedherewillremainrelevant.Forsimplicity,ourcur-
rentimplementationsupportsparallelinvocationoftheGPUfsAPI
| disk may | be lost. | From | the application’s |     | perspective, | successful |     |     |     |     |     |     |     |
| -------- | -------- | ---- | ----------------- | --- | ------------ | ---------- | --- | --- | --- | --- | --- | --- | --- |
onlyatthreadblockandnotwarpgranularity.GPUfscallsrepresent
| completion | of gfsync |     | or gmsync | ensures | that | data | has been |     |     |     |     |     |     |
| ---------- | --------- | --- | --------- | ------- | ---- | ---- | -------- | --- | --- | --- | --- | --- | --- |
animplicitsynchronizationbarrier,andmustbecalledatthesame
writtentothehostpagecache.TheAPIalsoallowsforcingwrites
pointwiththesameparametersfromallthreadsinathreadblock.
tostablestorage,equivalenttofsyncormsynconCPUs.
|     |     |     |     |     |     |     |     | Most of | GPUfs | is a GPU-side | library linked | with | application |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ----- | ------------- | -------------- | ---- | ----------- |
Unfortunately,GPUfailuresaremorefrequentandhavesevere
code.TheCPU-sideportionrunsasauser-levelthreadinthehost
implications.Inexistingsystems,aGPUprogramfailure—suchas
application,givingitaccesstheapplication’sCUDAcontext.
| an invalid | memory | access | or assertion | failure | [20]—may |     | require |          |       |           |               |        |            |
| ---------- | ------ | ------ | ------------ | ------- | -------- | --- | ------- | -------- | ----- | --------- | ------------- | ------ | ---------- |
|            |        |        |              |         |          |     |         | Figure 2 | shows | the three | main software | layers | comprising |
restartingtheGPUcard,thuslosingtheGPU’sentirememorystate.
|         |          |           |      |                  |     |     |        | GPUfs, their | location | in the overall | software | stack shown | on the |
| ------- | -------- | --------- | ---- | ---------------- | --- | --- | ------ | ------------ | -------- | -------------- | -------- | ----------- | ------ |
| As GPUs | continue | to become | more | general-purpose, |     | we  | expect |              |          |                |          |             |        |
rightandindicatedbydifferentcolors,andthetypeofmemorythe
GPUhardwaretogainmoreresiliencetosuchsoftwarefailures.
relevantdatastructuresarelocatedinshownontheleft.
3.4 ResourcecontentionwithGPUprograms ThetoplayeristhecoreofGPUfs,whichrunsinthecontextof
theapplication’sGPUkernelsandmaintainsitsdatastructuresin
| Operating | systems | are known | to  | compete | with | user programs | for |     |     |     |     |     |     |
| --------- | ------- | --------- | --- | ------- | ---- | ------------- | --- | --- | --- | --- | --- | --- | --- |
GPUmemory.ThislayerimplementstheGPUfsAPI,tracksopen
hardwareresourcessuchascaches[23],andareoftenblamedfor
filestate,andimplementsthebuffercacheandpaging.
| decreased | performance | in  | high | performance | computing |     | environ- |                   |     |       |                 |     |            |
| --------- | ----------- | --- | ---- | ----------- | --------- | --- | -------- | ----------------- | --- | ----- | --------------- | --- | ---------- |
|           |             |     |      |             |           |     |          | The communication |     | layer | manages GPU-CPU |     | communica- |
ments.GPUfsislessintrusivethanacompleteOSbecauseithas
|                 |              |          |        |             |           |              |      | tions, and naturally |         | spans the | CPU and GPU | components. | Data      |
| --------------- | ------------ | -------- | ------ | ----------- | --------- | ------------ | ---- | -------------------- | ------- | --------- | ----------- | ----------- | --------- |
| no active,      | continuously | running  |        | components. | It        | necessarily  | adds |                      |         |           |             |             |           |
|                 |              |          |        |             |           |              |      | structures shared    | between | the       | GPU and CPU | are stored  | in write- |
| some overheads, |              | however, | in the | form        | of memory | consumption, |      |                      |         |           |             |             |           |
sharedCPUmemoryaccessibletobothdevices.Thislayerimple-
increasedprograminstructionfootprint,andtheuseofGPUhard-
|     |     |     |     |     |     |     |     | ments a GPU-CPU |     | Remote Procedure | Call | (RPC) infrastructure, |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ---------------- | ---- | --------------------- | --- |
wareregisters.Weexpecttherelativeeffectoftheseoverheadson
tobedetailedinSection4.3.
performancetodecreasewithfuturehardwaregenerations,which
|     |     |     |     |     |     |     |     | Finally, the | GPUfs | consistency | layer is an | OS kernel | module |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ----- | ----------- | ----------- | --------- | ------ |
willprovidelargermemory,largerregisterfiles,andlargerinstruc-
runningonthehostCPU,whichmanagesconsistencybetweenthe
hostOS’sCPUbuffercacheandtheGPUbuffercaches,according
1Across-applicationbuffercachecouldpotentiallybeimplementedalready
tothefileconsistencymodeldescribedabovein§3.
usingthenewIPCfeatureinCUDA5.0,butthisinterfacestilllacksthe
TheGPUfsfilesystemisinspiredbytheLinuxfilesystemand
| programmable | memory | protection | that | would | be necessary | to  | protect a |     |     |     |     |     |     |
| ------------ | ------ | ---------- | ---- | ----- | ------------ | --- | --------- | --- | --- | --- | --- | --- | --- |
sharedGPUfsbuffercachefromerranthostprocessesorGPUkernels. buffercache.Wenowexamineitsfunctioninmoredetail.

4.2 GPUbuffercache
|     |     |     |     | Pages, page | frames      | and page | table. | GPUfs | manages    |      | file con- |
| --- | --- | --- | --- | ----------- | ----------- | -------- | ------ | ----- | ---------- | ---- | --------- |
|     |     |     |     | tent at the | granularity | of a     | buffer | cache | page. This | page | size is   |
configurable,thoughperformanceconsiderationstypicallydictate
pagesizeslargerthanOS-managedpagesonthehostCPU—e.g.,
256KB,sinceGPUcodeoftenparallelizestheprocessingofapage
acrossmanythreadsinathreadblock(ontheorderof256threads).
Theidealpagesizedependsonempiricalconsiderationsexplored
furtherin§5.Forefficiency,GPUfspre-allocatespagesinalarge
contiguousmemoryarray,whichwecalltherawdataarray.
|     |     |     |     | As in | Linux, | each page | has an | associated | pframe |     | structure |
| --- | --- | --- | --- | ----- | ------ | --------- | ------ | ---------- | ------ | --- | --------- |
holdingmetadataforthatpage,e.g.,thesizeoftheactualdatain
|     |     |     |     | the page, | dirty status, | and others. |     | Unlike | Linux, | pframes | contain |
| --- | --- | --- | --- | --------- | ------------- | ----------- | --- | ------ | ------ | ------- | ------- |
somefile-relatedinformation,suchasauniquefileidentifierused
forlock-freetraversal,andthepage’soffsetinthefile,becausein
GPUfsallpagesarebackedbyahostOSfile.
Pframesareallocatedinanarrayseparatefromthepagesthem-
|     |     |     |     | selves,buttheith |     | pframeinthisarrayholdsmetadatafortheith |     |     |     |     |     |
| --- | --- | --- | --- | ---------------- | --- | --------------------------------------- | --- | --- | --- | --- | --- |
pageintherawdataarray,makingiteasytotranslateinbothdirec-
tions,asneededinoperationssuchasgmunmapandgmsync.
|     |     |     |     | Per-file buffer | cache. | The | buffer | cache | keeps replicas |     | of previ- |
| --- | --- | --- | --- | --------------- | ------ | --- | ------ | ----- | -------------- | --- | --------- |
ouslyaccessedfilecontentforlaterreuse.ForsimplicitytheGPUfs
buffercacheisper-file,notper-blockdeviceasinLinux,butfuture
| Figure3. | Functionaldiagramofacalltogread.Colorscheme |     |     |     |     |     |     |     |     |     |     |
| -------- | ------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
GPUsupportfordirectaccesstostoragedevicesmaymotivatere-
isthesameasFigure2.
considerationofthisdecision.
Adynamicradixtreeindexeseachfile’sbuffercache,enabling
|     |     |     |     | efficient page | lookups  | given    | a file      | offset. | Last-level | nodes       | in the |
| --- | --- | --- | --- | -------------- | -------- | -------- | ----------- | ------- | ---------- | ----------- | ------ |
|     |     |     |     | tree hold      | an array | of fpage | structures, | each    | with       | a reference | to a   |
4.1 Filesystemoperations
|     |     |     |     | corresponding | pframe. | The | fpages | manage | concurrent |     | access to |
| --- | --- | --- | --- | ------------- | ------- | --- | ------ | ------ | ---------- | --- | --------- |
Openandclose. GPUfskeepstrackofopenandrecentlyclosed the respective pframes: each holds a read/write reference count
files in several tables. Each open file has an entry in the open andaspinlock,togetherpreventingconcurrentaccessbymutually
file table. This table holds a pointer to a radix tree indexing the exclusive operations such as initialization, read/write access, and
file’spages.Foreachfile,thetablestoresseveralfileparameters, pagingout.Thefpagesareallocatednotbyreference,butbyvalue
includingthepathnameandtheCPUfiledescriptorusedfordata within radix tree nodes. We use in-place data structures to avoid
requestshandledbytheCPU.Finally,eachentrystoresareference pointer traversal and minimize memory allocations, even though
countofthenumberofthreadblocksholdingthefileopen. alldynamicmemoryismanagedbyGPUfsviaspecialallocators.
| When | a file is closed its pages | are retained | in GPU memory |     |     |     |     |     |     |     |     |
| ---- | -------------------------- | ------------ | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Buffercachemanagement.
untiltheyarereclaimedforcachingotherdata.Theclosedfiletable CPUshandlebuffercachemanage-
|     |     |     |     | ment tasks | in a daemon | thread, | keeping |     | costly activities |     | such as |
| --- | --- | --- | --- | ---------- | ----------- | ------- | ------- | --- | ----------------- | --- | ------- |
maintainspointerstothecachesofclosedfiles,andisahashtable
|     |     |     |     | flushing | dirty pages | out of | an application’s |     | performance |     | path. |
| --- | --- | --- | --- | -------- | ----------- | ------ | ---------------- | --- | ----------- | --- | ----- |
indexedbyfileinodenumberintheCPUfilesystem.Becauseof
GPUsunfortunatelyhaveascheduling-relatedweaknessthatmakes
| GPU hardware | thread scheduling,     | files can | appear to be closed |                |              |       |           |                 |     |              |         |
| ------------ | ---------------------- | --------- | ------------------- | -------------- | ------------ | ----- | --------- | --------------- | --- | ------------ | ------- |
|              |                        |           |                     | daemon threads | inefficient, |       | affecting | the performance |     | of           | all GPU |
| while still  | in use by threadblocks | that have | yet to be scheduled |                |              |       |           |                 |     |              |         |
|              |                        |           |                     | applications   | including    | those | not using | GPUfs.          | GPU | threadblocks |         |
(§3.2). Tooptimizeforthiscaseandtosupportdatareuseinand
|     |     |     |     | are non-preemptive, |     | so a daemon |     | would | require | its own | thread- |
| --- | --- | --- | --- | ------------------- | --- | ----------- | --- | ----- | ------- | ------- | ------- |
acrosskernels,gopencheckstheclosedfiletablefirst,andmoves
block.Thisdedicatedthreadblockcouldbeeitheranindependent,
thefilecachebacktotheopenfiletable.
|     |     |     |     | constantly | running | GPU kernel, | or  | it could | be part | of each | GPU |
| --- | --- | --- | --- | ---------- | ------- | ----------- | --- | -------- | ------- | ------- | --- |
application.Theformerapproachreducesperformancebyperma-
Reads and writes. Reads and writes work as expected, first nentlyconsumingaportionofGPUhardwareresources,whereas
checkingthecachefortherelevantblock,andforwardingrequests thelatterbreaksthecorrectnessofGPUapplicationsthatrelyon
totheCPUandallocatingcachespaceasnecessary.Figure3shows theavailabilityofaspecificnumberofthreadblocksforexecution.
a functional summary of gread’s operation. Reads and writes Alternatively, offloading GPU cache management to a CPU dae-
exploit the GPU’s fine-grain parallelism by using many threads monisimpracticalonexistinghardwareduetothelackofatomic
tocopydataorinitializepagestozerocollaboratively.Reference operationsoveraPCIebus,asexplainedlaterin§4.3.
countsprotectpagesduringmemorytransfers. OrganizingthefilesystemtoavoidasynchronousGPU-initiated
Whengwritecompletes,eachthreadissuesamemoryfence activity has important design consequences, such as the need to
toensurethatupdatesreachGPUmemory,incasetheGPUbuffer optimizethepagingalgorithmforspeed.GPUfsperformspaging
cache needs to write the page back to the CPU. Otherwise, due as a part of regular file operations such as gwrite, with the
to the GPU’s weak memory consistency model, the data paged GPUfscodehijackingthecallingthreadtoperformpaging.Tokeep
backviaaDMAfromtheGPUmemorymightbeleftinconsistent pagingfast,GPUfsdoesnotusereplacementpoliciesthatperform
becausethewritesmightremainbufferedintheGPU’sL1cache. avariableamountofwork,suchastheclockalgorithm[5].
GPUfsimplementsaFIFO-likepolicybytrackingallocationof
Filemanagementoperations. Filemanagementoperationssuch last-levelradixtreenodes.Newlyallocatednodesareplacedatthe
asgunlinkandgftruncateeachgenerateanRPCtotheCPU head of a doubly-linked list. When a thread needs to evict pages
torequesttherespectiveoperationonthehost.Theyalsoreclaim back to the CPU, it performs a lock-free traversal of this list to
thefilepagecacheontheGPUifnecessary. reclaimadesirednumberofpagesfromaparticularfile.

Tochoosethefilewhosepageswillbereclaimed,GPUfsuses Today’sGPUsalsolackasignal-likemechanismaccessibleto
apolicysimilartoLinux’s.GPUfsfirstlooksatclosedfiles,which applications,tonotifyahostCPUprocessofeventsoriginatingon
are not in use so their content can be evicted with lower perfor- theGPU.ThecurrentAPIofferstheCPUonlycoarse-grainedno-
mancepenaltyfortherunningapplication.Furthermore,theirpages tificationswhenentireGPUkernelsormemorytransferscomplete,
areclean,sotheycanbereclaimedwithoutGPU-CPUcommuni- anddonotallowcodewithinaGPUkerneltosendnotifications.
cation.2GPUfsthenlooksforpagesfromread-onlyopenfiles,and
TheCPUmustthereforepolltheGPU-CPUsharedmemoryregion
asalastresortchoosespagesfromwritableopenfiles. continuouslytodetectRPCrequestsfromtheGPU.
| Lock-free          | buffer cache access.   | The     | buffer cache    | radix tree is    |              |                 |                |           |                |           |     |
| ------------------ | ---------------------- | ------- | --------------- | ---------------- | ------------ | --------------- | -------------- | --------- | -------------- | --------- | --- |
| a major contention | point among            | threads | accessing       | the same file.   |              |                 |                |           |                |           |     |
|                    |                        |         |                 |                  | RPC protocol | implementation. |                | GPU-CPU   | communications |           | in  |
| These accesses     | must be synchronized   |         | to avoid        | data races, such |              |                 |                |           |                |           |     |
|                    |                        |         |                 |                  | GPUfs follow |                 | a synchronous, | stateless | client-server  | protocol, |     |
| as concurrent      | attempts to initialize |         | pages belonging | to the same      |              |                 |                |           |                |           |     |
wheretheGPUsendsrequeststotheCPUandwaitsfortheCPU
intermediatenode,ornodedeletionduetopagereclamation,which toacknowledgetherequest’scompletion.TheRPCrequestchan-
maybeperformedconcurrentlywithpagelookup. nelisaFIFOqueueinwrite-sharedmemory,whichtheCPUpolls
GPUfs uses lock-free reads and locked updates, similar to forrequests.EachGPUinthesystemhasaseparateRPCrequest
Linux’s seqlocks [9]. Updates maintain the radix-tree invariants queue,managedexclusivelybytheGPUthatownsthatqueue.
used by readers, and all fields are initialized before a new node TheGPUusesitsrequestqueueonlytosendcommands:when
becomesvisibletoreaders.Readscanfail,inwhichcasetheyretry. theGPUissuesabulktransferrequestsuchasabulkdatareador
GPUfsretriesoncewithoutlocking,thenlocksonitsthirdattempt. write, the CPU initiates a DMA-based bulk data transfer directly
To check that the page found is correct, GPUfs assigns a unique toorfromtherespectiveGPUbuffercachepages,usingsourceor
identifier to each radix tree during initialization, then propagates destinationpointerssuppliedbyGPUcode.TheCPUthennotifies
thisidentifiertoeverypagereferencedbythetree.Thisidentifier, theGPUwhenthetransfercompletes.
combinedwiththepageoffset,uniquelyidentifiesthepage. The RPC queue usually contains multiple concurrent requests
The paging algorithm also uses lock-free reads on a doubly that, in principle, CPU code could handle in parallel. Our imple-
linkedlistusedasaFIFOqueue. mentation uses a single-threaded, event-based design on the host
|     |     |     |     |     | to restrict | the GPU-related |     | CPU load to | one CPU, | simplify | syn- |
| --- | --- | --- | --- | --- | ----------- | --------------- | --- | ----------- | -------- | -------- | ---- |
4.3 GPU-CPURemoteProcedureCall chronization,andtoavoidoverwhelmingthedisksubsystemwith
concurrentrequests.Ourimplementationthuscurrentlyordersfile
| GPUfs implements | an RPC protocol |     | to coordinate | data transfers |     |     |     |     |     |     |     |
| ---------------- | --------------- | --- | ------------- | -------------- | --- | --- | --- | --- | --- | --- | --- |
accesses,butdatatransferstoandfromtheGPUusemultipleasyn-
betweentheCPUandGPU.TheGPUservesasaclientthatissues
chronousCPU-GPUchannelstoutilizefull-duplexDMAandover-
| requests | to a file server running | on  | the host | CPU. This GPU- |     |     |     |     |     |     |     |
| -------- | ------------------------ | --- | -------- | -------------- | --- | --- | --- | --- | --- | --- | --- |
lapGPU-CPUtransferswithdiskaccesses.
as-clientdesigncontrastswiththetraditionalGPU-as-coprocessor
programmingmodel,reversingtherolesofCPUandGPU.
| The challenge | of implementing | an  | efficient | RPC protocol lies |     |     |     |     |     |     |     |
| ------------- | --------------- | --- | --------- | ----------------- | --- | --- | --- | --- | --- | --- | --- |
in the CPU/GPU memory consistency model. GPU consistency 4.4 Fileconsistencymanagement
| models are | tailored to the bulk-synchronous |     | GPU | programming |     |     |     |     |     |     |     |
| ---------- | -------------------------------- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
Thecurrentprototypeimplementsthelocality-optimizedfilecon-
model,whereGPU-CPUcommunicationstraditionallyoccuronly
|     |     |     |     |     | sistency model | described | in  | Section 3, | though | currently | only for |
| --- | --- | --- | --- | --- | -------------- | --------- | --- | ---------- | ------ | --------- | -------- |
atkernelinvocationboundariesandnotwhilethekernelisrunning. thecommoncasesoffilesopenedineitherread-only(O_RDONLY)
Except at these points, CPU/GPU consistency is not guaranteed. (O_GWRONCE, §3.2).
|     |     |     |     |     | or write-once | mode |     | see |     | The GPUfs | proto- |
| --- | --- | --- | --- | --- | ------------- | ---- | --- | --- | --- | --------- | ------ |
Our RPC system is thus not currently portable to all GPUs, but typedoesnotyetimplementthediff-and-mergeprotocolrequired
reliesonhardwareprovidingthefollowingconsistencyfeatures. tosupportgeneralwrite-sharing,andthuscurrentlysupportsonly
| 1. GPU-CPUmemoryfences.GPUfilereadandwriterequests |     |     |     |     | onewriteratatime. |     |     |     |     |     |     |
| -------------------------------------------------- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- |
mustbedeliveredtotheCPUwhiletheGPUkernelisrunning. If a GPU is caching the contents of a closed file, this cache
This is only possible if consistent updates of the CPU-GPU must be invalidated if the file is opened for write or unlinked by
write-sharedmemorycanbeenforcedinbothdirections. anotherGPUorCPU.GPUfspropagatessuchinvalidationslazily,
2. GPUcachebypass.ToallowconsistentreadsofGPUmemory ifandwhentheGPUcachingthisstaledatalaterreopensthefile.
fromtherunningGPUkernel,afterthismemoryhasbeenup- We call this strategy lazy because closing a file on one GPU or
datedbyCPU-initiatedDMAtransfers,GPUreadsmusteither CPUdoesnotactivelypushaninvalidationtootherGPUscaching
invalidateorbypasstheGPU’sL1andL2caches. the file. The GPUfs API currently offers no direct way to push
The OpenCL [7] standard, and consequently AMD’s discrete changesmadeononeGPUtoanotherGPU,exceptwhenthelatter
GPUs,currentlydonotsupportthesefeatures.HybridAMDGPUs reopensthefile.SupportingsuchinvalidationswithoutPCIatomics
are adding support for the first feature, but are not yet available. would require GPUs to run daemon threads waiting for such an
OnlyNVIDIAGPUscurrentlysatisfyallofourrequirements. invalidationsignal,anoverheadwewishtoavoid(see§4.2).
|     |     |     |     |     | GPUfs | uses | WRAPFS [28], | a stackable | passthru | file | system, |
| --- | --- | --- | --- | --- | ----- | ---- | ------------ | ----------- | -------- | ---- | ------- |
Challenges due to hardware constraints. RPC implementation on the CPU to implement file consistency. WRAPFS is a Linux
iscomplicatedbythelackofatomicoperationsoverthePCIebus. module that introduces a thin software layer on top of any file
ThenewPCIe-IIIstandardincludesatomics,butimplementationis system, enabling interposition on calls to the underlying file sys-
optionalandweknowofnohardwarecurrentlysupportingit. tem.WemodifiedWRAPFStoimplementourconsistencyproto-
Thislimitationprecludestheuseofefficientone-sidecommu- col,enablingseamlessintegrationofGPUfswithunmodifiedCPU
nication protocols. A CPU cannot reliably lock and copy a page programs.TheCPU-sideGPUfsdaemoncommunicateswiththis
fromGPUmemory,forexample,withoutGPUcodebeinginvolved modifiedWRAPFSmoduleviaaspecialcharacterdevice.Thisde-
in acknowledging that the page has been locked. Consequently, viceisusedsolelytoupdateandqueryfilestatetoimplementfile
thecurrentimplementationmustresorttoalessefficientmessage- consistency,andprovidesnoaccesstoactualfilecontent,thereby
passingprotocolforsynchronization. leavingthehostOS’sfileaccesspoliciesuncompromised.Wedo
|     |     |     |     |     | not currently | protect | against | denial-of-service |     | by misbehaved | ap- |
| --- | --- | --- | --- | --- | ------------- | ------- | ------- | ----------------- | --- | ------------- | --- |
2Forclarityweomitsometechnicaldetailsonhandlingdirtyfilesonclose. plicationsviabuffercacheinvalidation,however.

| 4.5 Implementationlimitations                             |     |     |     |     |     |     |      | CUDA pipeline |     | GPU File I/O |     |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---- | ------------- | --- | ------------ | --- |
| GPUscontainhardwaretranslationandprotectionmechanismsthat |     |     |     |     |     |     | 6000 |               |     |              |     |
preventGPUkernelslaunchedbyoneCPUprocessfromaccessing  Maximum PCI bandwidth (5731MB/s)
5000
theGPUmemoryofkernelslaunchedbyotherprocesses.Today’s
| GPUs do | not offer software | interfaces |     | to control | this | memory | B/s) |     |     |     |     |
| ------- | ------------------ | ---------- | --- | ---------- | ---- | ------ | ---- | --- | --- | --- | --- |
4000
p r o t e c t i o n h a r d w a r e , h o w e v e r . A G P U f s i n s t a n c e c a n t h e r e f o r e M  Whole file transfer (2100MB/s)
Throughput (
| s e r v e o n   | l y a s i n g l e C P  | U p r o c e     | s s , a n d   | G P U f s     | c a n n o t s   | h a r e s t a t e | 3 0 0 0 |     |     |     |     |
| --------------- | ---------------------- | --------------- | ------------- | ------------- | --------------- | ----------------- | ------- | --- | --- | --- | --- |
| a c r o s s G   | P U in v o c a t i o n | s b y d i f f   | e r e n t h o | s t p r o c e | s s e s . F o r | t h e s a m e     |         |     |     |     |     |
| re a s o n , G  | P U f s c a n n o t p  | r o t e c t t h | e c o n t e n | t s o f i t s | G P U b u f     | f e r c a c h e s | 2 0 0 0 |     |     |     |     |
| from corruption | by the                 | application     | it            | serves. Such  | features        | may               |         |     |     |     |     |
1000
becomefeasibleonceGPUvendorsofferappropriateinterfaces.
GPUfsdoespreservefileaccessprotectionatthehostOSlevel,
0
however.ThehostOSpreventsaGPUfsapplicationfromopening 16K 32K 64K 128K 256K 512K 1M 2M 4M 8M 16M
host files the application doesn’t have permission to access, and Page size
itdenieswritesofdirtyblocksbacktothehostfilesystemifthe
|     |     |     |     |     |     |     | Figure4. | Sequentialreadperformanceasafunctionofthepage |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | --------------------------------------------- | --- | --- | --- |
GPUfsapplicationhasopenedthefileread-only.
|     |     |     |     |     |     |     | size. The | red line is the maximum |     | achievable | PCI bandwidth on |
| --- | --- | --- | --- | --- | --- | --- | --------- | ----------------------- | --- | ---------- | ---------------- |
thishardwareconfiguration.Higherisbetter.
5. Evaluation
WeevaluateGPUfsonaSuperMicroserversystemfeaturingtwo
| 4-coreIntelXeonL5630CPUsat2.13GHzwith12MBL3cache |     |     |     |     |     |     | 2000 |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
Total time
| per CPU, | and four NVIDIA | TESLA | C2075 | GPUs, | each | with 6 | 1800 |     |     |     |     |
| -------- | --------------- | ----- | ----- | ----- | ---- | ------ | ---- | --- | --- | --- | --- |
CPU DMA excluded
| GB of GDDR5 | memory. | We run | Ubuntu | Linux | kernel | 3.0.0-27, | 1600 |     |     |     |     |
| ----------- | ------- | ------ | ------ | ----- | ------ | --------- | ---- | --- | --- | --- | --- |
CPU file I/O excluded
w i t h C U D A S D K 5 . 0 , G P U d r iv e r 3 0 4 . 5 4 . G P U f s is m o u n te d C P U   fil e  I/O and CPU DMA
|               |                          |                  |             |           |         |               | msec) 1 4 0 0 |     |     | ex c lu | d e d |
| ------------- | ------------------------ | ---------------- | ----------- | --------- | ------- | ------------- | ------------- | --- | --- | ------- | ----- |
| a t o p a r e | g u l ar d i s k p a r t | it i o n ; t h e | d i s k i s | a 5 0 0 G | B W D C | W D 5 0 0 3 , |               |     |     |         |       |
me ( 1 2 0 0
| 7 2 0 0R P M | . T h e p e rf o r m | a n c e a s | r e p o rt e | d b y ‘ h d | p a r m - | t - T ’ i s |     |     |     |     |     |
| ------------ | -------------------- | ----------- | ------------ | ----------- | --------- | ----------- | --- | --- | --- | --- | --- |
Total running ti10 0 0
| 6 , 6 0 0 M B | / s a n d 1 3 2 M B | / s f o r c a | c h e d a n | d d i s k r e | a d s r es p | e c t i v e l y . |     |     |     |     |     |
| ------------- | ------------------- | ------------- | ----------- | ------------- | ------------ | ----------------- | --- | --- | --- | --- | --- |
8 0 0 792.4
| W e e v         | a l u a t e t h e s y s | t e m ’ s p e   | r f o r m a n | c e a n d u   | t i l i t y w   | i t h s e v e r a l   |       |     |     |     |     |
| --------------- | ----------------------- | --------------- | ------------- | ------------- | --------------- | --------------------- | ----- | --- | --- | --- | --- |
| m i c r o b e n | c h m a r k s , a n d   | a l s o p r e s | e n t t w o   | m o r e r e a | l i s t i c a p | p l i c a t i o n s . | 6 0 0 |     |     |     |     |
433.3
| F o r e v e r y | d a t a p o i n t w e | r e p o r t t | h e a r i t h m | e t i c m e | a n o f 5 e | x e c u t i o n s | 4 0 0 |     |     |     |     |
| --------------- | --------------------- | ------------- | --------------- | ----------- | ----------- | ----------------- | ----- | --- | --- | --- | --- |
a ft e r o n e w a r m u p, u n l e s s s ta t ed o t h e r w i se . I n a l l e x p e r im en tswe 200 200.2
97.2 52.9
fo u n d t h e st a n da rd d e v i a ti o n o f th e r e s u lt s t o b e l e s s t h a n 1% . 23.4 12.3 7.3 3.9 2.4 1.9
0
Oneimportantpropertysharedbyallthetestworkloadsisthat 16K 32K 64K 128K 256K 512K 1M 2M 4M 8M 16M
their GPUfs implementation required almost no CPU code: they Page size
| were entirely | implemented | in the | GPU | kernel. | For all | the work- |          |                                                   |     |     |     |
| ------------- | ----------- | ------ | --- | ------- | ------- | --------- | -------- | ------------------------------------------------- | --- | --- | --- |
|               |             |        |     |         |         |           | Figure5. | ContributionofdifferentfactorstothefileI/Operfor- |     |     |     |
loads,theCPUcodeisidentical,savethenameoftheGPUkernel
manceasafunctionofthepagesize.Lowerisbetter.
toinvoke.ThisisaremarkablecontrastwithstandardGPUdevel-
opment,whichalwaysrequiressubstantialCPUprogrammingef-
fort.Fromourexperiencewefounditsignificantlyeasiertodevelop
self-containedGPUprograms,andbelievethatself-containedGPU The CPU code uses pread to read each chunk of the file
programmingwillenablebroaderadoptionofGPUs. intopinnedCPUmemoryallocatedwithcudaHostMalloc,then
issuesanasynchronouscudaMemcpytoenqueueaDMAtransfer
5.1 Microbenchmarks
requestforthatchunk,thenproceedstothenextchunk(exceptin
The microbenchmarks below examine basic system performance thewholefiletransfercaseinwhichthereisonlyonebigchunk).
anditssensitivitytoseveralimportantconfigurationparameters. DividingthefileintochunksoverlapsfileaccesslatencywithDMA
|     |     |     |     |     |     |     | data transfers | to the GPU. | An alternative | implementation, | which |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ----------- | -------------- | --------------- | ----- |
5.1.1 Sequentialfileread copiesfilecontentdirectlyfromtheCPUpagecacheexposedvia
We first evaluate the effect of page size on sequential read per- mmap,performsworsebecauseitpreventsCUDAfromoptimizing
formance. The benchmark transfers a single 1.8 GB file, in three DMAtransactionsandforcescudaMemcpytobesynchronous.
ways: (a) reading data from the GPU kernel via GPUfs, (b) us- ThegraphinFigure4showsreadbandwidthfordifferentpage
ingtheCUDAmemorytransferAPIinchunksthesamesizeasa sizes.Asexpected,smallGPUfspages(lessthan64KB)resultin
GPUfspage(CUDApipeline),and(c)readingthewholefileinone lowperformance,andincreasingpagesizeincreasesperformance,
chunkandtransferringittotheGPUinoneCUDAAPIcall. withdiminishingreturnsafter512KB.Readingentirefiles,acom-
TheGPUfilereadingkernelrunswith28threadblocks(twice monpracticeamongGPUprogrammersexpectinglargertransfers
the number of active multiprocessors in the GPU), where each toamortizedatatransferoverheadsmosteffectively,isinfactless
threadblockmapspagesfromacontiguousrangeinthefile.Each efficientthanbreakingreadsintochunks,aschunksallowoverlap
threadblockmapsonepageatatime,untilthetotal64MBofdata of pread from the CPU page cache with PCI data transfer. The
ismapped.Thenumberofmaprequestsdependsonthepagesize. CUDApipelineimplementationappearstoachievethemaximum
Thedataitselfisnotaccessed,butthepagesarefetchedfromthe possiblefile-to-GPUtransferperformanceonthismachine.
CPUpagecacheintotheGPUbuffercache.Thethreadblockthen GPUfs outperforms simple CUDA whole file reads at 64 KB
closes the file and exits. GPU file access is not strictly sequen- pagesandhigher,andachievesonaveragewithin5%oftheband-
tial because the order of reads by different threadblock is non- width of the hand-pipelined version, a cost we consider to be a
deterministic. We do not anticipate any measurable effect from reasonabletradeofffortheconvenienceGPUfsoffers.
thesenon-sequentialreads,however,becausethefiledataiscached Figure 5 breaks down the timing of the microbenchmark, by
inCPUmemoryandfitsintheGPUpagecache. eliminating PCI data transfer time while leaving only the RPC

| 10000 |      |     |     |                       |     | 1000 |     |     |     |     |     |
| ----- | ---- | --- | --- | --------------------- | --- | ---- | --- | --- | --- | --- | --- |
|       | 9000 |     |     | Unique pages accessed |     | 900  |     |     |     |     |     |
|       | 8000 |     |     | Throughput            |     | 800  |     |     |     |     |     |
B/s)
| Unique pages accessed | 7 0 0 0 |     |     |     |     | 7 0 0 |     |     |     |     |     |
| --------------------- | ------- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
M
|     | 6 0 0 0 |     |     |     |     | 6 0 0 width ( |     |     |     |     |     |
| --- | ------- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- |
|     | 5 0 0 0 |     |     |     |     | 5 0 0         |     |     |     |     |     |
Effective band
|     | 4 0 0 0 |         |           |            |       | 4 0 0 |     |     |     |     |     |
| --- | ------- | ------- | --------- | ---------- | ----- | ----- | --- | --- | --- | --- | --- |
|     | 3 0 0 0 |         |           |            |       | 3 0 0 |     |     |     |     |     |
|     | 2 0 0 0 |         |           |            |       | 2 0 0 |     |     |     |     |     |
|     | 1000    |         |           |            |       | 100   |     |     |     |     |     |
|     | 0       |         |           |            |       | 0     |     |     |     |     |     |
|     | 16K     | 32K 64K | 128K 256K | 512K 1M 2M | 4M 8M | 16M   |     |     |     |     |     |
Page size
|     |     |     |     |     |     |     | Figure7. | Buffercacheaccessperformancewithandwithoutlock- |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------------------------------------------- | --- | --- | --- |
Figure6. Randomread/writeperformanceasafunctionofpage free radix tree traversal, normalized by the raw memory access
| size.Higherisbetter. |     |     |     |     |     |     | time. |     |     |     |     |
| -------------------- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- |
tern,however.Inthecurrentimplementation,inwhichGPUfsisde-
traffic,eliminatingCPUfilereads,andeliminatingboth.Thegraph
ployedonaper-applicationbasis,pagesizemayeasilybetailored
showslatency,wherelowerisbetter.
totheparticularapplication’saccesspatternsifnecessary.
| Execution |     | time with | small pages | is dominated | by  | the DMA |     |     |     |     |     |
| --------- | --- | --------- | ----------- | ------------ | --- | ------- | --- | --- | --- | --- | --- |
transfers,whichcopytoolittledatapertransaction,andbyGPUfs
5.1.3 Buffercacheaccessperformance
| API | costs. I/O | operations | become | fully overlapped | with | GPUfs |     |     |     |     |     |
| --- | ---------- | ---------- | ------ | ---------------- | ---- | ----- | --- | --- | --- | --- | --- |
buffer cache code execution for pages larger than 64KB. We see Asthe“GPUfs-lock-free”caseinFigure7shows,GPUfsachieves
that total page cache access overhead (the rightmost labeled col- 85–88%ofrawmemoryaccessperformancewhenaccessingfiles
umn) diminishes proportionally to page size. This is because the in the GPU buffer cache, for 128KB pages or larger. In this ex-
totalamountofmemorymappedbyeachthreadblockisfixedwhile perimentweinvoke112threadblocks,eachreading64MBofdata
thepagesizechanges,sothenumberofmaprequestsperformedby intotheGPU’son-diescratchpadmemoryinchunksof16KB.The
eachthreadblockisreducedasthepagesizegrows.Forpageslarger baselineimplementationreadsdatadirectlyfromtheGPU’smain
than128KtheCPUpagecachebecomesthemainbottleneck. memory, without using the GPUfs API. The GPUfs implementa-
tionreadsdatafromthecachedfileviagread,passingtogread
5.1.2 Randomfileread a direct pointer to the destination buffer in scratchpad memory.
|     |     |     |     |     |     |     | The file is | fully prefetched | into the GPU page | cache | by another |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ---------------- | ----------------- | ----- | ---------- |
Thisexperimentshowstheperformanceofrandomfileaccessfor
|     |     |     |     |     |     |     | previously | invoked kernel, | excluding PCI | transfer | time from the |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --------------- | ------------- | -------- | ------------- |
differentpagesizes.Thiskernelisinvokedwith112threadblocks,
measurements.Werandomizedthememoryaccessessothatevery
whereeachthreadblockreads3232KBdatablocksfromrandom
|     |     |     |     |     |     |     | 16KB chunk | is read from a | different file location, |     | to cause non- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | -------------- | ------------------------ | --- | ------------- |
offsetsina1GBfile,foratotalof112MBread.Thekerneluses
greadtoreadthedataintoa32KBarrayallocatedintheGPUon- trivialcontentiononthebuffercachedatastructure.
diescratchpadmemory.Unlikegmmap,greadisnotconstrained This workload mimics the behavior of linear algebra kernels,
insizetoasinglecachepage,henceitismoreappropriateforac- for example, which perform tiled operations on large matrices,
cessingfiledataatrandomoffsets.Occasionally,differentthread- prefetchingdatatobeprocessedintoscratchpadmemory.
blocksmayaccessthesamepageandfetchitfromtheGPUbuffer We ran this experiment with a locked traversal of the buffer
cache.Timemeasurementsareanaverageover8runs. cache’s radix trees, for comparison against our default lock-free
Figure6showsthataswithsequentialreads,smallpagesleadto implementation. As described in §4.2, we normally use the lock-
badperformance,butnowlargepagesalsoleadtobadperformance. freetraversaltoaccesseachpage,resortingtolockingonlyincases
Smallpagesfailtoamortizetransfercosts,whilelargepagestrans- of high contention. When file data is fully resident in the buffer
fertoomuchdatathatisnotactuallyreadbytheapplication.64KB cache,GPUfslocksthetreerarely,asconfirmedlaterinTable2.As
achievesthebestperformanceinthistest. aresult,Figure7showsthatthelock-freeprotocolperformsnearly
We calculate effective throughput in this experiment assum- 3×betterthanthelockedprotocolacrossvariouspagesizes.
| ing an | ideal | case of exactly | 112MB | of data transferred. |     | To sup- |     |     |     |     |     |
| ------ | ----- | --------------- | ----- | -------------------- | --- | ------- | --- | --- | --- | --- | --- |
portrandomaccessesfromGPUcodewithoutGPUfs,aGPUpro- 5.1.4 Matrix-vectorproduct
gramwouldtypicallytransferthewhole1GBandperformtheran- We run a simple single-precision matrix-vector product kernel to
domaccessesinGPUmemory.Assumingthemaximumobserved highlight two key benefits of the file system API: automatic data
throughputof3100MB/s(seeFigure4),usingonlyonetenthofthe transferpipeliningandcodesimplification.
total1GBoftransferreddataresultsinaneffectiverandom-access Thistestreadsaninputmatrixandvectorfromfiles,andwrites
throughput of only 310 MB/s, comparable to GPUfs’s worst per- the result to an output file. We compare three implementations:
formanceusingverylargepages.Further,withoutGPUfs,random oneusingGPUfs,onethatexplicitlyimplementsdoublebuffering
accesstofileswhosesizeexceedstheGPU’sphysicalmemoryis tooverlapthePCIdatatransferandthekernelexecution(CUDA
complexandinefficientinhand-codedGPUprograms,oftenrequir- na¨ıveinFigure8),andanoptimizedversionofthelatter(CUDA
ingfrequent,briefkernelinvocationsbetweeneachrandomaccess. optimized). The GPUfs implementation does not call the CUDA
GPUfseliminatesfromtheapplicationthedesignandimplementa- host-side API, employing gmmap to read the data in the kernel,
tioncomplexityrequiredtohandlesuchcasesefficiently. gftruncatetotruncatetheoutputfileatthestart,gwriteto
Intheaboveexperiments,a128KBpagesizeachievesareason- write the output, and finally gfsync to synchronize the data to
ablebalancebetweensequentialandrandomaccessperformance. disk.TheGPUfsbuffercacheissizedto2GB,with2MBpages.
Theoptimalpagesizeingeneraldependsonapplicationaccesspat- The“na¨ıve”versionimplementsasimplepipeline,splittingthefile

|     |     |     |     |     |     |     |     | Buffer | Time(s) |     | Pages | Lock-free |     | Locked |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------- | --- | ----- | --------- | --- | ------ |
3500 GPU file I/O CUDA naïve CUDA optimized cachesize reclaimed accesses accesses
| 3000 |     |     |     |     |     |     |     | 2G  |     | 53  |        | 0 1,088,838 |         | 21,516 |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | ----------- | ------- | ------ |
|      |     |     |     |     |     |     |     | 1G  |     | 69  | 11,509 | 547,819     | 574,463 |        |
B/s) 2500
|     |     |     |     |     |     |     |     | 0.5G |     | 99  | 38,317 | 176,758 | 1,351,903 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | ------ | ------- | --------- | --- |
M
ut ( 2000
Table2. Impactofthebuffercachesizeontherunningtimeand
p h
g 1500 locking behavior for the image search workload. Locked access
u o
| hr  |     |     |     |     |     |     | countalsoincludesunlockedretries. |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- |
T 1000
500
5.2.1 Findingapproximatelymatchingimages
0
280 560 2800 5600 11200 The first application’s input is a set of query images and several
Matrix size (MB) imagedatabasescontainingmanysmallimages.Thegoalistofind
whichdatabasescontainimagesmatchingthequeryimages,where
| Figure8. | Matrix-vectorproductforlargematrices |     |     |     |     |     |     |     |     |     |     |     |     |     |
| -------- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
amatchisdefinedbyathresholdonasimilaritymetric,inourcase
|     |     |     |     |     |     |     | Euclidian |     | distance. | While | each | image may be | present in | several |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | --------- | ----- | ---- | ------------ | ---------- | ------- |
databases,thedatabasesmustbescannedinapredefinedorderand
onlythefirstmatchoutputforagivenqueryimage.Thisprocess
isrepresentativeoflarge-scaleimageregistrationtasks,e.g.,when
| into four chunks | and | processing | each chunk | independently, |     | over- |     |     |     |     |     |     |     |     |
| ---------------- | --- | ---------- | ---------- | -------------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
processingaerialphotographswhileattemptingtofindamatching
| lapping the | file read, | data transfer | and | kernel execution |     | between |     |     |     |     |     |     |     |     |
| ----------- | ---------- | ------------- | --- | ---------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
imageinaspecificregionfirst.
| them. Note | that the | chunk size | depends | on the | size of | the input, |     |     |     |     |     |     |     |     |
| ---------- | -------- | ---------- | ------- | ------ | ------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
Wecaneasilyparallelizethisproblembydynamicallyorstat-
whichisconvenientbecauseeveryGPUkernelinvocationmayuse
|     |     |     |     |     |     |     | ically | splitting | the | input | images | between the | threadblocks. | The |
| --- | --- | --- | --- | --- | --- | --- | ------ | --------- | --- | ----- | ------ | ----------- | ------------- | --- |
thesamenumberofthreads.Theoptimizedversionissimilar,but
|     |     |     |     |     |     |     | databases |     | or/and the | input | set may | not fit in | GPU memory, | how- |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | ---------- | ----- | ------- | ---------- | ----------- | ---- |
thechunksizeisfixedat70MBandthereare16independentlypro-
ever.Thus,thedecisionofwhichdatabasetoloadandwhenmust
cessedchunks.SimilarlytotheCUDAna¨ıveversion,eachchunkis
|     |     |     |     |     |     |     | be  | done at | runtime | depending | on  | the outcome | of prior | matching |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------- | --------- | --- | ----------- | -------- | -------- |
processedseparately,andthefileread,datatransferandkernelex-
attempts.Forexample,ifallthematchingimagesarelocatedatthe
ecutionareoverlappedbetweenthechunks.Bothimplementations
beginningofthefirstdatabase,theamountofdatatobetransferred
runthesamecodeforcomputingtheinner-product.
ismuchlowerthansimplytransferringallofthedatabasesatonce.
Wefixtheinputvectorlengthto128Kelements,andvarythe
WithoutGPUaccesstothefilesystem,theCPUmusttransfer
| matrix size | from a few | megabytes | up to | 11GB. | The largest | input |     |             |        |     |          |                    |     |            |
| ----------- | ---------- | --------- | ----- | ----- | ----------- | ----- | --- | ----------- | ------ | --- | -------- | ------------------ | --- | ---------- |
|             |            |           |       |       |             |       | the | databasesto | theGPU |     | first.To | avoid redundantPCI |     | transfers, |
doesnotfitintheGPU’smemory,andbarelyfitsintotheCPU’s
theCPUislikelytosplitthedatabasesintochunks,smallenough
| RAM. The | GPUfs version |     | requires no | special | treatment | for this |     |     |     |     |     |     |     |     |
| -------- | ------------- | --- | ----------- | ------- | --------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
sothattheamountofredundantdatatransferredwouldbenegligi-
case,however.WhilethisworkloadisentirelylimitedbythePCIe
ble,butlargeenoughtoamortizetheoverheadsofGPUinvocation
busbandwidth,andforthelargestinputsbythediskbandwidth,it
oneachchunk.Thisheuristicisnotonlysuboptimalandintroduces
isrepresentativeofmanykernelsthatneedtoreaddatafromdisk
|     |     |     |     |     |     |     | additional |     | overheads, | but | significantly | complicates | the code. | Fur- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ---------- | --- | ------------- | ----------- | --------- | ---- |
aspartofalargeprocessingpipeline.
thermore,beforestartingthekerneltoprocessthenextchunk,all
| Figure    | 8 shows that     | the | GPUfs based     | implementation |     | outper- |            |     |         |        |      |            |          |            |
| --------- | ---------------- | --- | --------------- | -------------- | --- | ------- | ---------- | --- | ------- | ------ | ---- | ---------- | -------- | ---------- |
|           |                  |     |                 |                |     |         | previously |     | matched | images | must | be removed | from the | input set, |
| forms the | double-buffering |     | implementation, | achieving      |     | maximum |            |     |         |        |      |            |          |            |
requiringadditionalprogramlogictocompacttheinputarray.
PCIbandwidthequivalenttoreadingsequentialfiles(seeFigure4).
GPUfsstreamlinesthistask,makingtheimplementationalmost
Themainreasonfortheperformancebenefitisthatthenon-GPUfs
|            |           |          |             |        |       |       | trivial | and | closely | following | the | design for CPU | code. | Both the |
| ---------- | --------- | -------- | ----------- | ------ | ----- | ----- | ------- | --- | ------- | --------- | --- | -------------- | ----- | -------- |
| code reads | the input | in large | chunks (1GB | each), | which | some- |         |     |         |           |     |                |       |          |
OpenMPparallelCPUandGPUfs-basedversionsoftheprogram
| times causes    | slowdowns   | due | spurious paging    | of  | the CPU | buffer   |     |       |         |      |          |                  |                |     |
| --------------- | ----------- | --- | ------------------ | --- | ------- | -------- | --- | ----- | ------- | ---- | -------- | ---------------- | -------------- | --- |
|                 |             |     |                    |     |         |          | are | about | 130±10  | LOC, | counting | semicolons.3     | The associated |     |
| cache, stalling | the CPU-GPU |     | transfer pipeline. |     | GPUfs   | performs |     |       |         |      |          |                  |                |     |
|                 |             |     |                    |     |         |          | CPU | code  | for the | GPU  | version  | is only a single | line—the       | GPU |
manyshorterreads,duetothe2MBpagesizeinthisexperiment,
kernelinvocation.
andtheperformanceirregularitiesaresmoothedbythefine-grained
|     |     |     |     |     |     |     |     | In our | synthetic | workload, | the | images in | the input | and the |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --------- | --------- | --- | --------- | --------- | ------- |
pipeliningperformedunderthehoodbytheCPU’sRPCdaemon.
databasesarerandomlygenerated.Eachimageisrepresentedasa
WhenfilesizeexceedsavailableCPUbuffercache(thelastdata
4K-elementvector.Theinputcontains2,016images,amountingto
| point in the | graph), | performance | falls as | the workload |     | becomes |     |     |     |     |     |     |     |     |
| ------------ | ------- | ----------- | -------- | ------------ | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
31.5MBofrawdata.Weuse3databasefiles,ofsizes383,357and
diskbound.Inthisperformanceregime,GPUfsoutperformsboth
400MB,containingabout25,000imageseach.Theimagesfrom
| CUDA versions | by  | a factor | of 4. The | pinned memory |     | allocated |     |     |     |     |     |     |     |     |
| ------------- | --- | -------- | --------- | ------------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
theinputareinjectedatrandomlocationsinthedatabases.Wein-
forlargetransferbuffersfortheCUDAimplementationscompetes
vokethekernelwith28threadblocks,512threadsperthreadblock.
withtheCPUbuffercache,slowingitdownsignificantly.
Wemeasurerawperformanceusingaquerysetcontainingonly
Ontheotherhand,weobservenoslowdownforinputsexceed-
|     |     |     |     |     |     |     | images | with | no matches |     | in the | databases, forcing | all databases |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | ---- | ---------- | --- | ------ | ------------------ | ------------- | --- |
ingthesizeoftheGPUbuffercache(largerthan2GB).TheFIFO-
|     |     |     |     |     |     |     | to  | be read | completely. | We  | flush | the OS page | cache before | each |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ----------- | --- | ----- | ----------- | ------------ | ---- |
likereplacementpolicyemployedbyGPUfsappearstoofferade-
experiment.WesettheGPUbuffercachesizeto2GB,enoughto
quateefficiencyforsuchstreamingworkloads.
keepalldatabasesinGPUmemory.TheGPUthroughputachieved
is18GFLOP/s,twiceasfastasan8-coreCPUrunusingOpenMP.
5.2 Applicationbenchmarks Changing the buffer cache size. We examine the effect of the
WenowconsidertwomorerealisticI/Ointensiveworkloads:image buffercachesizeonprogramperformanceinTable2.Observethat
search,anda“grep”-likesearchoftextfiles.Bothapplicationshave as the amount of available memory decreases, the ratio between
highly data-dependent, unbounded working sets that dynamically lock-freeandlockedaccessesdropsduetothepagingalgorithm’s
changeduringcomputations.Suchdynamicdatadependenciesare
challengingtohandleinGPUprogramswithoutGPUfs. 3WetriedDavidWheeler’sSLOCCountbutitfailstoparseCUDAcode.

Input CPUx8 #GPUs of 58,000 modern English words4, within the complete works of
1 2 3 4 Shakespeareasasingle6MBtextfile5,andwithintheLinux3.3.1
Nomatch 119s 53s 27s 18s 13s kernelsourcecontainingabout33,000filesfor524MBintotal.To
(2.0×) (2.9×) (4.1×) simplifytheparsingofthedictionaryfilebyaGPU,wereformat
Exactmatch 100s 40s 21s 14s 11s thedictionarytoaligneverywordona32byteboundary;noneof
(1.9×) (2.9×) (3.6×) thewordsinthedictionaryexceedthatlength.Thelistofinputfiles
isitselfspecifiedinafile.
Table3. Approximateimagematchingperformance.Speedupfor Each threadblock opens one file at a time, then each thread
multi-GPUrunsrelativetoasingleGPUaregiveninparentheses. searches for a subset of the dictionary that it is allocated to
match.Matchedwordsareprintedouttogetherwiththefilename
and match count into an internal per-threadblock output buffer,
Input CPUx8 GPU-GPUfs GPU-vanilla whichisthenperiodicallyflushedintoaglobaloutputfile.Various
Linuxsource 6.07h 53m(6.8×) 50m(7.2×) text parsing and formatted output tasks required us to implement
Shakespeare 292s 40s(7.3×) 40s(7.3×) limited GPU versions of the sprintf, strtok, strlen,
LOC(semicolon) 80 140(+52) 178 strcatfunctionsnotnormallyavailabletoGPUcode.
ThisworkloadputsextremelyhighpressureonGPUfsbecause
Table4. GPUexactstringmatch“grep-w”performance.
mostofthefilesarefairlysmall(fewkilobytesonaverage),leading
tofrequentcallstogopenandgclose.Sincetheprogressofeach
threadblock depends on the actual number of matching words in
attemptstofreepagesbeingused.Eachthreadblockrunsindepen-
its input subset, the number of concurrently open files eventually
dentlyoftheothers,andmayfollowdifferentexecutionpaths,for
reachesthenumberofconcurrentlyrunningthreadblocks.
example accessing the databases relevant to the set of input im-
As a point of reference we compared two other implementa-
agesitisprocessing.Fileaccesspatternsamongdifferentthread-
tions:asimpleCPUprogramperformingthesametaskon8cores
blocksquicklydesynchronizes,awellknowneffectinlarge-scale
(usingOpenMP),anda“vanilla”GPUversionimplementedwith-
parallelenvironments,requiringcarefulimplementationandpossi-
outGPUfs.Bothimplementationsprefetchthecontentsoftheinput
blyredundantworktoavoid.
filesintoalargememorybufferfirst,thendonotreadfromthefile
Finally, we evaluate our implementation’s scalability by split-
systemduringthematchingphase.
tingthequerylistequallyamongupto4GPUs.Wedonotevaluate
The vanilla GPU version pre-allocates a large output buffer
thediff-and-mergealgorithmforwrite-sharing,butthesystemin-
in the GPU memory (5GB—all remaining GPU memory), but
teractionwiththeWRAPFS-basedconsistencydaemonisincluded
if it overflows, the GPU kernel crashes. In general, our vanilla
(asisthecaseforallexperimentspresentedinthissection).
GPU version is more limited than the one using GPUfs because
Thissetofexperimentsisperformedwithpreliminarywarmup
it conservatively assumes that the inputs and outputs fit in the
inordertoprefetchthedataintotheCPUbuffercacheandhighlight
GPU’s physical memory. Large file support would substantially
thescalingcapabilitiesofthesystem.Asconfirmedintheexperi-
complicatetheimplementation,whereastheGPUfs-basedversion
mentsinTable3,GPUfsshowsnearlinearscalingwithincreasing
automaticallysupportsarbitrarilylargeinputfiles.
GPU count because of the lightweight consistency protocol. The
Wepresenttheresults(nowarmup)inTable4.Evenforsuch
firstrun(“Nomatch”)showstheperformanceofthemoreregular
afile-systemintensiveworkload,asingleGPUoutperformsthe8-
workload, for which GPUfs shows ideal scaling. The second run
core CPU by 6.8×. The GPUfs version is only 9% slower than
isirregularbecausethenumberofexactmatchesperprocessoris
thevanillaGPUimplementationontheLinuxkernelinput,butthe
different,andstaticinputpartitioningdoesnotscaleaswellinei-
twoversionsperformsimilarlyononelargeinputfile.TheGPUfs-
thertheGPUfsorCPUversions.All4GPUstogetheroutperform
basedcodeisshorterthanthevanillaversionifweexcludestring
asingleCPUexecutionbyaboutafactorof9.
parsing and formatted output functions (52 lines of code), which
Thebenefitsofdynamicdatabaseloadingbecomesapparentas
arenotusedinthevanillaversionbecausetheyareexecutedona
we relax the matching threshold, allowing searches to terminate
CPUasapartofapost-processingphase.
earlier, and occasionally eliminating the need to accesses lower-
We emphasize, however, that no serious effort has been made
priority databases altogether. Runtime decreases as expected; in
tooptimizeeithertheGPUorCPUversion.Themainpointofthis
the degenerate case where images always match the first entry
exerciseistohighlighttheutilityofthefilesystemAPIonGPUs,
in the first database, runtime falls by 400×—from 53 seconds
whichopensupnewwaystoexplorethecomputingpowerofthese
toaminimumof130ms—leavingonlythecostsofinitialization,
massivelyparallelprocessors.
invocation,andmatchingthequerylistwiththefirstdatabasepage.
5.2.2 Exactstringmatchingintextfiles
6. Relatedwork
Thelastexperimentisanimplementationofaconstrainedversion
ToourknowledgeGPUfsisthefirstextensionofthefilesystemab-
ofgreponaGPU.Givenadictionaryandasetoftextfiles,foreach
stractiontomodernGPUarchitectures.Thisworktouchesonmany
word in the dictionary, the program determines how many times
areasfromclassicOSdesignandefficientlock-freesynchroniza-
andinwhichfilesitappears.
tiontoGPUarchitecturesandprogrammingtechniques.
Thisapplicationisconceptuallysimilartoimagematching,but
with two key differences. The parallelization strategy is different
General-purposeGPUcomputing. Theresearchcommunityhas
because words are typically short (up to 32 symbols), so each
focusedconsiderableeffortontheproblemofprovidingageneral-
GPUthreadisassignedoneword,insteadofoneimageperthread-
purpose programming interface to the specialized hardware sup-
blockinthepreviouscase.Second,theoutputbufferbecomesun-
ported by GPUs (GPGPU). GPGPU computing frameworks such
bounded, so we need to write the output frequently to flush the
as CUDA [20], OpenCL [7], and others [3, 4, 8, 17, 25] provide
per-threadblockinternalbuffer.
This experiment counts the frequencies of modern English
words in two datasets: the works of William Shakespeare, and 4http://www.mieliestronk.com/wordlist.html
theLinuxkernelsourcecode.Wesearchforaspecificdictionary 5http://www.gutenberg.org/ebooks/100

anexpressiveplatform,butnoneprovideanywayforGPUstouse passing.GPUfstakesamorepragmaticviewofapplicationsinter-
hostOSservicesingeneral,orfilesystemaccessinparticular. actingthroughthefilesystem,keepingthehostOSlargelyintact.
I/O for GPUs. GPUDirect from NVIDIA allows GPUs to ac- Lock-free algorithms. Lock-free algorithms are a well known
cesscertainstorageandnetworkdeviceswithoutthemediationof technique in parallel programming [16]. Our algorithm was in-
thehostOS.Thistechnologyisexposedviaproprietary,low-level spired by seqlocks [9] and read-copy update(RCU) [18]. We are
hardware-specificinterfaces,anddoesnotprovidehigher-levelab- unaware of any prior radix tree designs with lock-free traversal
| stractions,suchasafilesystemAPI. |                |     |                |     |           | availableforGPUs. |     |     |     |     |
| -------------------------------- | -------------- | --- | -------------- | --- | --------- | ----------------- | --- | --- | --- | --- |
| Other hardware                   | architectures. | The | Cell processor |     | [12] pio- |                   |     |     |     |     |
7. Conclusions
neeredtheintegrationofparallelacceleratorsintotheOS,allowing
system calls and file accesses from its Synergistic Processor Ele- This paper describes the design and implementation of GPUfs, a
ments(SPEs).TheSPEssharethesamedieasthemainprocessor, file system API and implementation allowing data parallel GPU
offeringahighbandwidthchannelwithmemoryperformancemore softwaretoaccesshostfilesdirectly.GPUfsextendstheconstrained
likemulticoreSMPsthantoday’sdiscreteGPUs.Also,weareun- GPU-as-coprocessorprogrammingmodel,turningGPUsintofirst-
awareofanypublishedworkanalyzingfilesystemdesigntradeoffs classcomputingdeviceswithfullfileI/Osupport.GPUfsexploits
orI/Ointensivedataparallelapplications,thefocusofthispaper. fine-grained parallelism and memory locality to offer a familiar
Intel’s Xeon-Phi [11] is a PCIe-attached accelerator sharing and efficient file system for GPU programs, and simplifies GPU
the NUMA characteristics of discrete GPUs, but built of more programmingbyhidingthecomplexitiesoflow-leveldatamove-
traditional CPU cores that can run a full OS such as Linux. To mentbetweenGPUsandCPUsandamongGPUs.Ourprototype
ourknowledgeXeon-Phidoesnotexposethehost’sfilesystemto showsthatfilesystemaccessforGPUkernelsenablesgoodperfor-
softwareontheaccelerator.WeexpectmanyaspectsofGPUfsto manceandeaseofdevelopmentforapplicationsthathavenottypi-
be relevant to Xeon-Phi systems, particularly the NUMA-driven callybeenconsideredsuitableforGPUprocessing.GPUfsachieves
need to maximize file cache locality. Matuso et al [15] presented goodperformanceontoday’sarchitecture,andislikelytobenefit
afilesystemlayerforXeon-phi,providingaccesstothehostfile fromfuturehardwarearchitectureadvances.
systemfromthecard.ThisdesigndoesnotexplorefileI/Oinfine-
graindata-parallelworkloads,however,oneofthemainfociofour Acknowledgments
work.
ThisresearchwassupportedinpartbyNSFgrantsCNS-1017785
andCNS-1017206,bytheAndrewandErnaFinceViterbiFellow-
| HostOSsupportforGPUprogramming. |     |     | Stuart[24]prototyped |     |     |     |     |     |     |     |
| ------------------------------- | --- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- |
ship,andbya2010NVIDIAresearchaward.
| CPU-GPU   | communication | via RPC,       | enabling | GPU software | to  |     |     |     |     |     |
| --------- | ------------- | -------------- | -------- | ------------ | --- | --- | --- | --- | --- | --- |
| make host | system calls. | GPUfs includes | such     | a mechanism, | but |     |     |     |     |     |
References
focusesoncopingwithdataparallelismandlocalityatdesignlevel
via its GPU buffer cache, to avoid redundant data transfers and [1] AmittaiAviram,Shu-ChunWeng,SenHu,andBryanFord. Efficient
GPU-CPUinteraction. system-enforceddeterministicparallelism. InProceedingsofthe9th
Hydra [27] and PTask [22] explore dataflow frameworks for USENIXSymposiumonOperatingSystemsDesignandImplementa-
tion,October2010.
GPUprogramming,offeringhostCPUsoftwareanAPIwithwhich
[2] AndrewBaumann,PaulBarham,Pierre-EvaristeDagand,TimHarris,
tocomposeGPUmodules.GPUfsincontrastfocusesonthecom-
|     |     |     |     |     |     | Rebecca | Isaacs, Simon | Peter, Timothy | Roscoe, | Adrian Schu¨pbach, |
| --- | --- | --- | --- | --- | --- | ------- | ------------- | -------------- | ------- | ------------------ |
plementarygoalofenhancingtheAPIavailabletoGPUcode.
|     |     |     |     |     |     | andAkhileshSinghania. |     | TheMultikernel:AnewOSarchitecturefor |     |     |
| --- | --- | --- | --- | --- | --- | --------------------- | --- | ------------------------------------ | --- | --- |
Kato[13]introducesahostOSdriverforGPUsthatfacilitates
|     |     |     |     |     |     | scalablemulticoresystems. |     | InProceedingsoftheACMSIGOPS22nd |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------- | --- | ------------------------------- | --- | --- |
theOS-managedsharingofGPUresources,allowingdifferentCPU
symposiumonOperatingSystemsPrinciples,pages29–44,NewYork,
| processestoshareGPUmemoryforexample.Wehopetoleverage |     |     |     |     |     | NY,USA,2009. |     |     |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- |
thiscomplementaryfunctionalitytoenablefuturecross-application [3] Amr Bayoumi, Michael Chu, Yasser Hanafy, Patricia Harrell, and
filesystemsupportinGPUfs. GamalRefai-Ahmed. ScientificandEngineeringComputingUsing
|                                  |     |     |                     |     |     | ATI Stream | Technology. | Computing | in Science | and Engineering, |
| -------------------------------- | --- | --- | ------------------- | --- | --- | ---------- | ----------- | --------- | ---------- | ---------------- |
| SimplifyingdatamanagementinGPUs. |     |     | Thecomplexityofdata |     |     |            |             |           |            |                  |
11(6):92–97,2009.
managementindiscreteGPUsiswellrecognized.Gelado[6]sug-
[4] IanBuck,TimFoley,DanielHorn,JeremySugerman,KayvonFata-
| gested ADSM, | an asymmetric, | CPU-centric | shared | memory | [6]. |                                    |     |     |                     |     |
| ------------ | -------------- | ----------- | ------ | ------ | ---- | ---------------------------------- | --- | --- | ------------------- | --- |
|              |                |             |        |        |      | halian,MikeHouston,andPatHanrahan. |     |     | BrookforGPUs:Stream |     |
ADSMemulatesaunifiedaddressspacebetweenCPUsandGPUs, ComputingonGraphicsHardware. ACMTransactionsonGraphics,
alleviatingmanagementproblems.UnlikeGPUfs,ADSMdoesnot 23(3),August2004.
supportcommunicationswitharunningkernel,andalsointroduces [5] WolfgangEffelsbergandTheoHaerder. Principlesofdatabasebuffer
newaccelerator-specificabstractions,whichGPUfsavoids. management. ACM Transactions on Database Systems, 9(4):560–
595,December1984.
| Heterogeneous        | and multi-core | OS design.      |             | A number | of re-   |                          |         |               |                               |                     |
| -------------------- | -------------- | --------------- | ----------- | -------- | -------- | ------------------------ | ------- | ------------- | ----------------------------- | ------------------- |
|                      |                |                 |             |          |          | [6] Isaac Gelado,        | John E. | Stone, Javier | Cabezas,                      | Sanjay Patel, Nacho |
| searchers considered | the            | general problem | of building |          | OSes for |                          |         |               |                               |                     |
|                      |                |                 |             |          |          | Navarro,andWen-meiW.Hwu. |         |               | Anasymmetricdistributedshared |                     |
heterogeneousarchitectures.TheHeliosoperatingsystem[19]tar- memorymodelforheterogeneousparallelsystems. InProceedingsof
getsheterogeneoussystemswithmultipleprogrammabledevices. the15thInternationalConferenceonArchitecturalSupportforPro-
However, Helios requires the processors to expose interfaces to grammingLanguagesandOperatingSystems,pages347–358,New
three basic hardware primitives: a timer, an interrupt controller, York,NY,USA,2010.
andtheabilitytocatchexceptions.Theseservicesarecurrentlynot [7] KhronosGroup. OpenCL-theopenstandardforparallelprogram-
|     |     |     |     |     |     | ming of | heterogeneous | systems. | http://www.khronos.org/ |     |
| --- | --- | --- | --- | --- | --- | ------- | ------------- | -------- | ----------------------- | --- |
availableonmostGPUs,makingHeliosinapplicabletosucharchi-
opencl.
tectures.Furthermore,Heliosdoesnotaccountforthespecificsof
|     |     |     |     |     |     | [8] TianyiDavidHanandTarekS.Abdelrahman. |     |     |     | hiCUDA:ahigh-level |
| --- | --- | --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | ------------------ |
massivelyparallelSIMDarchitectures,asGPUfsdoes.
|                |        |                     |     |           |        | directive-basedlanguageforGPUprogramming. |     |     |     | InProceedingsof |
| -------------- | ------ | ------------------- | --- | --------- | ------ | ----------------------------------------- | --- | --- | --- | --------------- |
| The Barrelfish | OS [2] | treats the hardware | as  | a network | of in- |                                           |     |     |     |                 |
the2ndWorkshoponGeneralPurposeProcessingonGraphicsPro-
dependent,heterogeneouscorescommunicatingviaRPC.Again,it
cessingUnits(GPGPU-2),March2009.
isnotclearifaGPUcouldrunBarrelfishdirectly.Philosophically,
|     |     |     |     |     |     | [9] StephenHemminger. |     | fastreader/writerlockforgettimeofday2.5.30, |     |     |
| --- | --- | --- | --- | --- | --- | --------------------- | --- | ------------------------------------------- | --- | --- |
Barrelfish argues for a ground-up OS redesign based on message 2002. http://lwn.net/Articles/7388/.

| [10] John | H. Howard, | Michael | L. Kazar, Sherri | G. Menees, | David | A.  |
| --------- | ---------- | ------- | ---------------- | ---------- | ----- | --- |
Nichols,M.Satyanarayanan,RobertN.Sidebotham,andMichaelJ.
| West. | Scale and | performance | in a distributed | file | system. | ACM |
| ----- | --------- | ----------- | ---------------- | ---- | ------- | --- |
TransactionsonComputingSystems,6(1),February1988.
| [11] Intel | Xeon-Phi | Coprocessor:                      | System Software | Developers |     | Guide, |
| ---------- | -------- | --------------------------------- | --------------- | ---------- | --- | ------ |
| November   | 2012.    | http://www.intel.com/content/www/ |                 |            |     |        |
us/en/processors/xeon/xeon-phi-coprocessor-
system-software-developers-guide.html.
[12] J.A.Kahle,M.N.Day,H.P.Hofstee,C.R.Johns,T.R.Maeurer,and
| D.Shippy. | IntroductiontotheCellmultiprocessor. |     |     |     | IBMJournalof |     |
| --------- | ------------------------------------ | --- | --- | --- | ------------ | --- |
ResearchandDevelopment,49:589–604,July2005.
| [13] S. Kato,                                   | M. McThrow, | C.  | Maltzahn, and | S. Brandt. | Gdev:    | First- |
| ----------------------------------------------- | ----------- | --- | ------------- | ---------- | -------- | ------ |
| classGPUresourcemanagementintheoperatingsystem. |             |     |               |            | InUSENIX |        |
AnnualTechnicalConference,June2012.
| [14] WaltLigonandRobRoss. |     |     | Paralleli/oandtheparallelvirtualfilesys- |     |     |     |
| ------------------------- | --- | --- | ---------------------------------------- | --- | --- | --- |
tem. InWilliamGropp,EwingLusk,andThomasSterling,editors,
BeowulfClusterComputingwithLinux,pages493–535.MITPress,
2003.
| [15] YukiMatsuo,TakuShimosawa,andYutakaIshikawa. |     |     |                               |     | AfileI/Osys- |     |
| ------------------------------------------------ | --- | --- | ----------------------------- | --- | ------------ | --- |
| temformany-corebasedclusters.                    |     |     | InProceedingsofthe2ndInterna- |     |              |     |
tionalWorkshoponRuntimeandOperatingSystemsforSupercomput-
ers,pages3:1–3:8,NewYork,NY,USA,2012.
| [16] MauriceHerlihyandNirShavit. |     |     | TheArtofMultiprocessorProgram- |     |     |     |
| -------------------------------- | --- | --- | ------------------------------ | --- | --- | --- |
ming. MorganKaufmann,2008.
| [17] MichaelD.McCoolandBruceD’Amora. |     |                                      | ProgrammingusingRapid- |     |     |     |
| ------------------------------------ | --- | ------------------------------------ | ---------------------- | --- | --- | --- |
| MindontheCellBE.                     |     | InSC’06:Proceedingsofthe2006ACM/IEEE |                        |     |     |     |
conferenceonSupercomputing,page222,NewYork,NY,USA,2006.
ACM.
[18] PaulE.McKenney,DipankarSarma,AndreaArcangeli,AndiKleen,
| Orran | Krieger, | and Rusty | Russell. Read-copy | update. | In  | Ottawa |
| ----- | -------- | --------- | ------------------ | ------- | --- | ------ |
LinuxSymposium,pages338–367,June2002.
| [19] Edmund           | B. Nightingale, | Orion                                   | Hodson, Ross | McIlroy, | Chris | Haw- |
| --------------------- | --------------- | --------------------------------------- | ------------ | -------- | ----- | ---- |
| blitzel,andGalenHunt. |                 | Helios:heterogeneousmultiprocessingwith |              |          |       |      |
| satellitekernels.     |                 | InSOSP’09:Proceedingsofthe22ndACMsympo- |              |          |       |      |
siumonOperatingsystemsprinciples,2009.
| NVIDIA | CUDA | 4.2 Developer | Guide. http://developer. |     |     |     |
| ------ | ---- | ------------- | ------------------------ | --- | --- | --- |
[20]
nvidia.com/category/zone/cuda-zone.
| [21] NVIDIA’s | Next  | Generation                     | CUDA | Compute | Architecture: |     |
| ------------- | ----- | ------------------------------ | ---- | ------- | ------------- | --- |
| Fermi,        | 2011. | http://www.nvidia.com/content/ |      |         |               |     |
PDF/fermi_white_papers/NVIDIA_Fermi_Compute_
Architecture_Whitepaper.pdf.
[22] ChristopherJ.Rossbach,JonCurrey,MarkSilberstein,BaishakhiRay,
| andEmmettWitchel.     |     | PTask:operatingsystemabstractionstomanage |                                   |     |     |     |
| --------------------- | --- | ----------------------------------------- | --------------------------------- | --- | --- | --- |
| GPUsascomputedevices. |     |                                           | InProceedingsoftheTwenty-ThirdACM |     |     |     |
SymposiumonOperatingSystemsPrinciples,pages233–248,2011.
| [23] Livio | Soares and | Michael        | Stumm. FlexSC: | flexible       | system | call   |
| ---------- | ---------- | -------------- | -------------- | -------------- | ------ | ------ |
| scheduling | with       | exception-less | system calls.  | In Proceedings |        | of the |
9thUSENIXconferenceonOperatingsystemsdesignandimplemen-
tation,pages1–8,Berkeley,CA,USA,2010.
| [24] JeffA.Stuart,MichaelCox,andJohnD.Owens. |          |          |                   | GPU-to-CPUcall- |             |     |
| -------------------------------------------- | -------- | -------- | ----------------- | --------------- | ----------- | --- |
| backs.                                       | In Third | Workshop | on UnConventional | High            | Performance |     |
Computing(UCHPC2010),August2010.
[25] Sain-ZeeUeng,MelvinLathara,SaraS.Baghsorkhi,andWen-MeiW.
| Hwu. | CUDA-Lite: | Reducing | GPU Programming |     | Complexity. | In  |
| ---- | ---------- | -------- | --------------- | --- | ----------- | --- |
LCPC2008,21thAnnualWorkshoponLanguagesandCompilersfor
ParallelComputing,2008.
[26] BruceWalker,GeraldPopek,RobertEnglish,CharlesKline,andGreg
| Thiel. | TheLOCUSdistributedoperatingsystem. |     |     | InProceedingsof |     |     |
| ------ | ----------------------------------- | --- | --- | --------------- | --- | --- |
theninthACMsymposiumonOperatingsystemsprinciples,pages49–
70,NewYork,NY,USA,1983.
| [27] Yaron                        | Weinsberg, | Danny                                        | Dolev, Tal Anker,          | Muli Ben-Yehuda, |     | and |
| --------------------------------- | ---------- | -------------------------------------------- | -------------------------- | ---------------- | --- | --- |
| PeteWyckoff.                      |            | TappingintothefountainofCPUs:onoperatingsys- |                            |                  |     |     |
| temsupportforprogrammabledevices. |            |                                              | In13thInternationalConfer- |                  |     |     |
enceonArchitecturalSupportforProgrammingLanguagesandOp-
eratingSystems(ASPLOS’08),March2008.
| [28] E. Zadok | and | I. Ba˘dulescu. | A stackable             | file system | interface      |     |
| ------------- | --- | -------------- | ----------------------- | ----------- | -------------- | --- |
| for Linux.    | In  | LinuxExpo      | Conference Proceedings, |             | pages 141–151, |     |
Raleigh,NC,May1999.