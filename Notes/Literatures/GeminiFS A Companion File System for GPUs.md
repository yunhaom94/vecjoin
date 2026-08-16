# GeminiFS

**Source**: GeminiFS.pdf
**Format**: .pdf

---

GeminiFS: A Companion File System for GPUs
Shi Qiu, Weinan Liu, Yifan Hu, Jianqin Yan, and Zhirong Shen, NICE Lab, Xiamen
University; Xin Yao, Renhai Chen, and Gong Zhang, Huawei Theory Lab;
Yiming Zhang, NICE Lab, Xiamen University and Shanghai Jiao Tong University
https://www.usenix.org/conference/fast25/presentation/qiu
This paper is included in the Proceedings of the
23rd USENIX Conference on File and Storage Technologies.
February 25–27, 2025 • Santa Clara, CA, USA
ISBN 978-1-939133-45-8
Open access to the Proceedings
of the 23rd USENIX Conference on
File and Storage Technologies
is sponsored by

GeminiFS: A Companion File System for GPUs
ShiQiu1,WeinanLiu1,YifanHu1,JianqinYan1,ZhirongShen1,XinYao3,RenhaiChen3
GongZhang3,YimingZhang1,2
1NICELab,XMU,2SJTU,3HuaweiTheoryLab
Abstract andweights.Thistypicallyinvolvesaccessingnumerousfiles.
Theirsizescanreachuptotensofterabytes(TBs)andare
GPU-centricstoragesolutionsenabledirectaccessfromthe
expectedtocontinuouslygrow.Asaresult,althoughtheca-
GPU to the storage device via NVMe queues, completely
pacityofGPUmemoryhassubstantiallyincreasedinthelast
bypassingtheCPU.Thesesolutionsalleviatetheproblemsof
decade[1,23],thegapbetweenGPUmemorycapacityand
previousCPU-centricsolutionsthatreliedonthehostCPU
applicationdemandiswidening.
toinitiatedatastorageaccess,suchashighCPU-GPUsyn-
Tomitigatethecapacity-demandgapofGPUmemory,tra-
chronization overheads,I/O traffic amplification,and high
ditionalmemory-basedexpansionsolutionsusehostmemory
CPUprocessinglatency.However,thestate-of-the-artGPU-
(DRAM)[29]orpooltogethermultipleGPUs’memories[10]
centricsolutionshavenofileabstractionormanagementfunc-
toaccommodatethemassivedatasetsandweights,whichis
tionalities(e.g.,fine-grainedisolationandaccesscontrol)of
quiteexpensiveintheforeseeablefuture.Incontrast,storage-
traditionalhostfilesystems,andcannotsatisfytheneedsof
based GPUmemoryexpansion solutions[4,11,22,38,40]
GPU-accelerated machine learning (ML) applications like
extendGPUs’reachintostorage,allowingGPUstodirectly
GNNandLLMwhichrequirefastfileaccessanddatashar-
accesstheNVMestoragedevices.Withthedevelopmentof
ing. Therefore,existing GPU-centric storage solutions are
high-performanceflashtechnologies,storage-basedsolutions
inefficientandinconvenientwhenbeingappliedinpractical
aremorecost-effectivethanmemory-basedoneswithlittle
MLscenarios.
performancedegradation[4,39].
Thispaperpresentsacompanionfilesystem(calledGemi-
Moststorage-basedGPUmemoryexpansionsolutionslike
niFS)forGPUs.GeminiFSoffersafilesysteminterfaceto
Dragon[25]andGDS[35]areCPU-centric[39](a.k.a.CPU-
GPUprogramsthatenablesdirectfile-basedaccesstoNVMe
orchestrated[7]).TheyrelyontheCPUtoinitiateaccessto
storage, which is managed by the host file system. Gemi-
thestorageeitherexplicitly(viaCPUuser/OScodetoman-
niFSrealizesmetadatasynchronizationbetweenthehostand
agedatatransfer)orimplicitly(viaCPUpagefaulthandler
GPUfilesystemsbyembeddingthemetadatadirectlyinto
activatedbyGPUpagefaultsofmemory-mappedfiles).Un-
thefiles.WeextendtheexistingNVMedrivertoallowthe
fortunately,CPU-orchestratedapproachesareinefficientand
CPU and the GPU to set up their control planes in paral-
cannot satisfy the GPU’s throughput demands [39],as the
lelforthe storage device. Moreover,GeminiFS provides a
CPUaswellasCPU-GPUsynchronizationbecomesabot-
GPU-friendly,software-definedpagecachetofullyutilizethe
tleneck when hundreds or even thousands of GPU threads
internalbandwidthoftheGPU.Wefurtherofferaconvenient
read/writedataonthestoragedevice.
library (libGemini) tailored for GPU programmers, which
To address the inefficiency of CPU orchestration, BaM
abstractsawayvariousunderlyingcomplexitiestherebyre-
(BigacceleratorMemory)[39]proposesaGPU-centricap-
ducingprogrammingcomplexity.Extensiveevaluationshows
proach that transfers data directly between GPU memory
thatGeminiFSsignificantlyoutperformsthestate-of-the-art
and NVMe storage devices. BaM implements the control
storagesolutionsforlarge-scaleMLworkloads.
planecompletelyontheGPUbyallocatingNVMequeues
in GPU memory,through which GPU threads can directly
1 Introduction send NVMe I/O commands to the NVMe device without
involvingthehostCPU.Onthedownside,however,thestate-
GPU-acceleratedmachinelearning(ML)applications,such of-the-artGPU-orchestratedapproachesdonotsupportfile
asgraphneuralnetworks(GNN)[13,19,20]andlargelan- abstractionandmanagement,thussufferingfromthelackof
guagemodels(LLM)[6,24,49,58],havemassivedatasets dataandmetadataintegrity,crashconsistency,durability,and
USENIX Association 23rd USENIX Conference on File and Storage Technologies 221

the ability to manage in-storage resources across GPU de- ten to the storage only through appends. This implies that
vices[17].Whenaccessingfilesmanagedbyatraditionalfile the metadata of these data is also predictable and remains
system,theystillrequirememorycopiesbetweentheCPU stable.Weexploitthesecharacteristicstosimplifythedesign
andGPU,preventingNVMestoragedevicesfrombeingeffi- (e.g.,themetadataandindexstructuressynchronization)of
cientlyutilizedbyGPUprocesses.Consequently,theexisting thecompanionfilesystemforGPUs.
GPU-orchestratedapproachcannotmeetthehighparallelism Inthispaper,wepresentadesignofacompanionfilesys-
anddatasharingrequirementsofcommontraining/inference tem (called GeminiFS) for GPUs,which provides a set of
scenariossuchasaccessinginputdata[4,56]andsharingKV- simplifiedfilesysteminterfacestoGPUprogramsallowing
cache[11,38].However,buildingageneralGPUfilesystem file-baseddirectstorageaccess.Tothebestofourknowledge,
isprohibitivelydifficult,sinceGPUsarenaturallyunsuitable GeminiFS is the firstGPU-centricfile system thatunlocks
forrunningstoragesoftwarethatrequirescomplexmetadata theGPU’sviewofthehostfilesystemandenablesGPUsto
maintenance[12]. createon-demandfileaccessesdirectlytodataonthedisk,
Totacklethesechallenges,weintroducealightweightGPU withoutrelyingontheCPUtoinitiateortrigger.
filesystemcalledCompanionFileSystem,whichcoexistswith Thispapermakesthefollowingcontributions.
thehostfilesystem.Onthehost,weusethehostfilesystem
• We propose a file format (called GVDK) that integrates
forfilemanagement(e.g.,created,moved,anddeleted)and
theindispensablefilesystemmetadataintothefile,includ-
integratenecessarymetadataintothefiles[9,59,60],sothat
ing the file size/type/offset and the mapping of file logi-
the file system metadata can be managed on the CPU and
cal blocks to NVMe physical blocks. Based on GVDK,
sharedwiththeGPU.OntheGPU,weretrievethemetadata
werealizeefficientmetadatasynchronizationbetweenthe
intotheGPUmemory,basedonwhichwecanprovidefile
CPU/GPUfilesystemsandsupportspecificfileoperations
systemabstractions.
requiredbyGPUprogramstoaccessNVMestorage.
However, designing a companion file system for GPUs
• WeextendtheexistingNVMedrivertoallowtheCPUand
facesuniquetechnicalchallengesincluding(i)metadatasyn-
theGPUtosetupcontrolplanesinparallelforthestorage
chronization, (ii) device driver limitations, (iii) GPU page
device.TheshareddriversupportsI/Oqueuesonboththe
cacheefficiency,and(iv)GPUprogrammingcomplexity.
CPUandtheGPU,enablingthehost/GPUfilesystemsto
First,metadatasynchronizationbetweenthehostandGPU
concurrentlysubmitNVMerequeststothestoragedevice.
filesystemsisvitalforGPUI/Operformance[21,60].Gem-
iniFSneedstoretrievethemetadataintegratedintothefile • We design a GPU-friendly,software-defined page cache
efficientlyandsupportasetoffileoperationsspecifictoGPU architecture,whichprovidesaflexibleAPItoexploitlocal-
programs’storageaccessdemandswithhighparallelism.Fur- ityandcontroldataplacementforGPUs’predictabledata
ther,crashconsistencyandconcurrencycontrolneedtobe access. The page cache can be shared by multiple GPU
carefullyconsideredinmetadatasynchronization. processestoreduceGPUmemoryfootprint.
Second,currently,theNVMedriveronlyallowsthehost
• Weofferanefficientlibrary(calledlibGemini),whichpro-
filesystemtoexclusivelycontroltheNVMestoragedevice,
videssimplebutpowerfulabstractionstolowerthecom-
and cannot support concurrent control planes for both the
plexity of using GeminiFS. libGemini hides the details
hostandtheGPU[54].Therefore,eventhoughtheGPUcan
ofrealizingmetadataretrieval,synchronization,controlof
retrievethemetadatasharedbythehost,itstillcannotdirectly
NVMeI/Oqueues,aswellashost-sideinitialization.
submitNVMecommandstotheNVMestoragedevice.
We have implemented GeminiFS for recently released
Third, page cache is essential for improving the perfor-
GPUs. Extensive evaluation shows that GeminiFS signifi-
manceofnotonlythehostfilesystembutalsotheGPUfile
cantlyoutperformsthestate-of-the-artGPUstoragesolutions.
system. However,the traditional page cache design of the
Wehaveopen-sourcedthekeycomponentsofGeminiFSat
hostfilesystemcannotsatisfytheshareableaccessandhigh
https://github.com/nicexlab/GeminiFS.
parallelismrequirementsofGPUstorageaccesspatterns.
Fourth,acceleratingGPUstorageaccessnecessitatesinter-
actionsbetweentheGPUprograms,thecoexistinghost/GPU 2 BackgroundandMotivation
filesystems,aswellastheNVMedriver.Thesubstantialdif-
ferencesbetweenCPUsandGPUsleadtohighprogramming
2.1 StorageAccessofGPUWorkloads
complexity[41],involvingvariousunderlyingdetails.
Fortunately,ouranalysisshowsthatGPU-acceleratedap- Various GPU-accelerated ML workloads, including DNN
plications (like GNN andLLM) exhibittwo usefulcharac- (deepneuralnetworks)[4,56],LLM[11,14,38,55,61]and
teristics.First,GPUstorageI/Oworkloadshavecertainpre- GNN [3,15,16,30,36,53] require efficient storage access,
dictability,allowingthestorageaccessinformationtobeob- whichhasbeenextensivelystudiedintheliterature.
tainedbeforehandbasedonthemodelsettings.Second,most InDNN[4,56]andLLM[14,55,61]training,existingstud-
on-diskdataisread-onlyduringitslifetime,anddataiswrit- ies focus on offloading intermediate data,including intern
222 23rd USENIX Conference on File and Storage Technologies USENIX Association

Table1:SummaryofstorageaccesscharacteristicsofGPU-acceleratedMLworkloads.
| Application |     |     | DataTypes       |     |     | AccessMode |     | DataSize     |     | Retention |     |
| ----------- | --- | --- | --------------- | --- | --- | ---------- | --- | ------------ | --- | --------- | --- |
|             |     |     | Training-inputs |     |     | Readonly   |     | 10-1TB~103TB |     | Years     |     |
101TB~102TB
| DNN[4,56] |     |     | Intermediateweights/activations |     |     | Read&Write |     |     |     | Minutes |     |
| --------- | --- | --- | ------------------------------- | --- | --- | ---------- | --- | --- | --- | ------- | --- |
10-1GB~103GB
|     |     |     | Modelweights    |     |     | Read&Appendonlyseq.write |     |             |     | Years |     |
| --- | --- | --- | --------------- | --- | --- | ------------------------ | --- | ----------- | --- | ----- | --- |
|     |     |     | AdjacencyMatrix |     |     | Readonly                 |     | 102GB~101TB |     | Years |     |
|     |     |     | Featurevectors  |     |     | Read&Appendonly          |     | 103GB~101TB |     | Years |     |
GNN[3,15,16,30,36,53]
|     |     |     | Intermediateweights/activations/ |     |     |            |     | 103GB~102TB |     |         |     |
| --- | --- | --- | -------------------------------- | --- | --- | ---------- | --- | ----------- | --- | ------- | --- |
|     |     |     |                                  |     |     | Read&Write |     |             |     | Minutes |     |
featurevectors
|     |     |     | Modelweights    |     |     | Read&Appendonlyseq.write |     | 102GB~103GB |     | Years |     |
| --- | --- | --- | --------------- | --- | --- | ------------------------ | --- | ----------- | --- | ----- | --- |
|     |     |     | Training-inputs |     |     | Readonly                 |     | 103TB~      |     | Years |     |
101TB~103TB
|     |     |     | Intermediateweights/activations |     |     | Read&Write |     |     |     | Minutes |     |
| --- | --- | --- | ------------------------------- | --- | --- | ---------- | --- | --- | --- | ------- | --- |
LLM[2,11,14,38,43,55,61]
|     |     |     | KV-Cache     |     |     | Read&Appendonly          |     | 103TB~101PB |     | Years |     |
| --- | --- | --- | ------------ | --- | --- | ------------------------ | --- | ----------- | --- | ----- | --- |
|     |     |     | Modelweights |     |     | Read&Appendonlyseq.write |     | 102GB~101TB |     | Years |     |
weightsandactivationgeneratedduringforwardpropagation. • Short-termdataneedsnopersistence.
| In GNN | training,some | works | [16,30,36,53] | utilize | high- |     |     |     |     |     |     |
| ------ | ------------- | ----- | ------------- | ------- | ----- | --- | --- | --- | --- | --- | --- |
• Long-termdataisappend-only.
| volume SSDs | to  | store hundreds | of terabytes | of  | adjacency |     |     |     |     |     |     |
| ----------- | --- | -------------- | ------------ | --- | --------- | --- | --- | --- | --- | --- | --- |
matrices,featurevectors,andintermediatedatagenerateddur- • Moststorageaccesshaspredictablepatterns.
ingthetrainingprocess,whicharereferredtoasshort-term • DataneedstobesharedacrossmultipleGPUprocesses.
data.Theretentionofshort-termdatatypicallydoesnotex-
ceedseveralminutes.Oncethesubsequenttrainingiteration
2.2 ExtendingGPUReachtoStorage
starts,theshort-termdatawillbecomeinvalid[4].Currently,
storagedevicesmainlyserveasthesecondarycacheforGPU
|     |     |     |     |     |     | As illustrated | in Fig. 1, | existing | GPU storage | access | ap- |
| --- | --- | --- | --- | --- | --- | -------------- | ---------- | -------- | ----------- | ------ | --- |
memory.Trainingworkloadsalsoperiodicallywritemodel
proachescanbeclassifiedintotwocategories[7,39],CPU-
weightstostorageascheckpoints,whichcanbeusedtore-
centricandGPU-centric,dependingonwhethertheyareiniti-
sumetrainingincaseoffailures.Thesizeofcheckpointis
atedbytheCPUorbytheGPU.
basicallythesameasthatofmodelweight.
InLLMinferenceapplications,someefforts[2,43]utilize
SSDstostoremodelweights,whichcanreachhundredsof 2.2.1 CPU-CentricStorageAccess
GBstoTBs.Recentworks[11,38]storeKV-cacheinSSDs
CPU-centricapproachesrelyontheCPUtoinitiatestorage
andreusetheKV-cacheacrossmulti-turnconversations,to
|     |     |     |     |     |     | access requests. | For instance,GPUfs |     | [44] | and syscalls | for |
| --- | --- | --- | --- | --- | --- | ---------------- | ------------------ | --- | ---- | ------------ | --- |
reducetherepetitivecomputationoverheadandimprovethe
GPUs[50]allowGPUstorequestfiledatathroughthehost
| inference | performance. | The | model weights | and | KV-cache |                     |      |        |                       |     |     |
| --------- | ------------ | --- | ------------- | --- | -------- | ------------------- | ---- | ------ | --------------------- | --- | --- |
|           |              |     |               |     |          | CPU. ActivePointers | [42] | adds a | memory-mapabstraction |     |     |
inLLMinference,aswellasthetraininginputdata,require
on topofGPUfs,allowingGPUthreadstoaccessfiledata
long-termretention.Duringthelifetime,thelong-termdata
asiftheywereaccessingmemory.Dragon[25]incorporates
undergoesaninitialphaseofappend-onlysequentialwrites
storageaccesstotheUVM[32]pagefaultmechanism.
asdataisgenerated.Subsequently,itremainsunchangedand
TheseeffortsprovideaPOSIX-likeinterfaceforGPUpro-
willbeaccessedinaread-onlymanner.
|     |     |     |     |     |     | grams and | rely on CPU | user/OS | code to | orchestrate | data |
| --- | --- | --- | --- | --- | --- | --------- | ----------- | ------- | ------- | ----------- | ---- |
Long-termdataisoftensharedandreadbymultipleGPU
transferbetweenstorageandGPUmemory.Theyutilizethe
processes.Forinstance,modelweightsaresharedacrossmul-
hostfilesystemtosimplifytheprogrammingcomplexityof
tipleGPUprocesseswhenperformingparallelmodeltraining.
GPUstoragesoftware.However,thecomplexcontrollogic
KV-cache is widely used in prefix caching to enable their betweentheCPUandtheGPUprolongsthestorageaccess
| reuse across | multiple | requests | for reducing | computational |     |     |     |     |     |     |     |
| ------------ | -------- | -------- | ------------ | ------------- | --- | --- | --- | --- | --- | --- | --- |
path.Furthermore,usinglow-parallelismCPUstoservethe
overheadinLLMinference.
datademandsofhigh-parallelismGPUsisinefficient[7,39].
| Most | data access | exhibits | certain predictability. |     | For in- |     |     |     |     |     |     |
| ---- | ----------- | -------- | ----------------------- | --- | ------- | --- | --- | --- | --- | --- | --- |
Toaddressthisinefficiency,GDS[35]establishesadirect
stance, the process of DNN training and data features are dataplanebetweenGPUmemoryandstoragebyexploiting
determinedbythemodeldesignandthenumberofiterations. theirDMAcapabilities.Unfortunately,GDScanonlyprovide
Therefore,thedataaccesspatternanddatasizeofDNNtrain-
anon-POSIXinterface,whichgreatlyincreasesthecomplex-
ingcanbestaticallyanalyzedandpredicted[56]. ityofprogramming.Moreover,GDSstillreliesontheCPU
Table1summarizesthedatatypes,accessmodes,datasizes, toinitiateI/OtotheGPU,thusbeingabottleneckforGPU
andretentionsofstorageaccessofcommonGPUworkloads, storageaccess.Forinstance,thecuFileBatchIOSubmitoper-
whichhavethefollowingcharacteristics: ationinGDSislimitedtohandlingatmost128operations
USENIX Association 23rd USENIX Conference on File and Storage Technologies    223

|     |         | Data Plane |     | Controll Plane |         |     | Data |             |     |            |      |  avg  |  p95   p99   p99.9 |
| --- | ------- | ---------- | --- | -------------- | ------- | --- | ---- | ----------- | --- | ---------- | ---- | ----- | ------------------ |
|     |         |            |     |                |         |     |      | 1200        |     | ZhiTi 7000 | 1200 |       | Intel P5800        |
|     |         |            |     |                |         |     |      | 1000        |     |            | 1000 |       |                    |
|     | GPU HBM |            |     | NVMe           | GPU HBM |     | NVMe | )su(ycnetaL |     |            |      |       |                    |
|     |         |            |     |                |         |     |      |             | 800 |            |      | 800   |                    |
|     |         |            |     |                |         |     |      |             | 600 |            |      | 600   |                    |
Bam
|     |     |              | GDS  |     |     |       |     |     | 400                 |                         |     | 400 |                         |
| --- | --- | ------------ | ---- | --- | --- | ----- | --- | --- | ------------------- | ----------------------- | --- | --- | ----------------------- |
|     |     |              | PCIe |     |     | PCIe  |     |     | 200                 |                         |     | 200 |                         |
|     |     | GPUFS，Dragon |      |     |     |       |     |     | 0                   |                         |     | 0   |                         |
|     |     |              |      |     |     |       |     |     | 1 4                 | 8 16 32 641282565121024 |     | 1 4 | 8 16 32 641282565121024 |
|     |     |              |      |     |     |       |     |     | Num of GPU threads  |                         |     |     | Num of GPU threads      |
|     |     | File         |      |     |     | File  |     |     |                     |                         |     |     |                         |
CPU CPU (a)Averageandtaillatenciesof4KBreadI/OforGPUfsunderdifferent
|     |     | System |     |     | System |     |     |     |     |     |     |     |     |
| --- | --- | ------ | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
numbersofthreads.Asthenumberofthreadsincreases,theaverageand
DRAM DRAM taillatenciessignificantlyincreaseduetocontentionamongCPUcores.
|     |     | CPU Centric |     |     |     | GPU Centric |     |     |     |     |     |       |                    |
| --- | --- | ----------- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | ----- | ------------------ |
|     |     |             |     |     |     |             |     |     |     |     |     |  avg  |  p95   p99   p99.9 |
Figure1:CPU-centricandGPU-centricstoragearchitectures. 800 ZhiTi 7000 800 Intel P5800
|     |     |     |     |     |     |     |     | )su(ycnetaL | 600 |     |     | 600 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- |
perbatch[31],whichfallsshortofmeetingthedemandsof
| GPUs.                                             |                                                |     |     |     |     |     |     |     | 400 |           |        | 400 |                  |
| ------------------------------------------------- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------ | --- | ---------------- |
|                                                   | Wecomparethereadperformanceoftworepresentative |     |     |     |     |     |     |     | 200 |           |        | 200 |                  |
| CPU-centricapproaches,namely,GPUfs[44]andGDS[35], |                                                |     |     |     |     |     |     |     | 0   |           |        |     |                  |
|                                                   |                                                |     |     |     |     |     |     |     | 1   | 4 8 16 32 | 64 128 | 0 1 | 4 8 16 32 64 128 |
withdifferentparallelism levels. The experimentis run on GDS batch size GDS batch size
aserverequippedwith64CPUcoresandanNVIDIAGPU (b)Averageandtaillatenciesof4KBreadI/OforGDSunderdifferent
with80GBmemory.TheL1cacheoftheGPUisdisabled.We batchsizes.InGDS,thesoftwareoverheadaccountsformorethan90%
ofthememoryaccesslatency.Asthebatchsizeincreases,theoverhead
usetwoNVMestoragedevices,ZhitiTiPro7000(withR/W graduallydecreasesbutremainsatahighlevel.
Latencyof15µs[27])andIntelOptaneP5800X(withR/W
Latencyof4µs[8]),bothofwhichcanachieveabandwidth Figure2:Averageandtaillatenciesof4KreadI/OforGPUfs
ofupto7GB/sec.TheresultsareshowninFig.2. andGDSunderdifferentparallelismlevels.
|     | As illustrated |     | in Fig. | 2(a),forGPUfs,when |     |     | the number |     |     |     |     |     |     |
| --- | -------------- | --- | ------- | ------------------ | --- | --- | ---------- | --- | --- | --- | --- | --- | --- |
GPUandCPUprograms.Therefore,BaMnaturallyencoun-
| of  | GPU | threads | is low,the | I/O | latency | is  | higher than 190 |     |     |     |     |     |     |
| --- | --- | ------- | ---------- | --- | ------- | --- | --------------- | --- | --- | --- | --- | --- | --- |
tersthesameproblem[62]asSPDK:eachGPU/CPUprocess
µsonbothstoragedevices,implyingthatthesoftwarestack
isgranteddirectaccesstothestoragedeviceasablockdevice,
| overhead |     | accounts | forover90% |     | of  | the overall | I/O latency. |     |     |     |     |     |     |
| -------- | --- | -------- | ---------- | --- | --- | ----------- | ------------ | --- | --- | --- | --- | --- | --- |
losingtheappropriateabstractionprovidedbythetraditional
Further,whenthenumberofGPUthreadsexceedsthenum-
filesysteminthehostkernel.Asaresult,theprocessneeds
berofCPUcores,boththeaverageandtaillatenciessurge
toimplementauser-levelfilesystem(e.g.BlobFSprovided
dramatically,e.g.,increasingbyabout250%for1024GPU
bySPDK[47])thatmanagesalldataandmetadatatoensure
threads.Fig.2(b)showsthatwithsmallbatchsizes,theaver-
ageandtaillatenciesofGDSareevenhigherthanthoseof systemintegrity,crashconsistency,anddurability.Moreover,
metadataisolationmakesitdifficulttosharedatabothamong
GPUfs.Asthebatchsizeincreases,theaverageandtaillaten-
|     |     |     |     |     |     |     |     | different | GPU | processes | and between |     | GPU and CPU pro- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --------- | ----------- | --- | ---------------- |
ciesdecreasebutstillremainrelativelyhigh(around160µs).
|     |     |     |     |     |     |     |     | cesses | [17]. | When loading | files | from | the host file system, |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ----- | ------------ | ----- | ---- | --------------------- |
ThesoftwarestackoverheadofGDSisstillnon-ignorable.
BaMneedstoreadin-filedatafromtheNVMedevicetothe
hostmemory,andthencopyittotheGPUmemory.Thisis
2.2.2 GPU-CentricStorageAccess
inefficientinvariousAIcomputationscenarios,suchasmodel
loading/saving,checkpointing,andsharing[39].
| To  | avoid | the inefficiency |     | of  | the CPU-centric |     | approaches. |     |     |     |     |     |     |
| --- | ----- | ---------------- | --- | --- | --------------- | --- | ----------- | --- | --- | --- | --- | --- | --- |
BaM[39]enablesGPUstoorchestratehigh-throughput,fine-
grainedaccessestostoragewithoutCPUorchestrationover- 2.3 Challenges
| head. | GMT | [7] | further | extends | BaM’s | two-tier | hierarchy |     |     |     |     |     |     |
| ----- | --- | --- | ------- | ------- | ----- | -------- | --------- | --- | --- | --- | --- | --- | --- |
(GPUmemoryandstorage)toathree-tierone,addinghost To satisfy the stringent performance demand of GPU-
memorybetweentheGPUmemoryandthestoragedevice. acceleratedapplications,thegoalofthispaperistodesign
BaMallocatesNVMequeuesinGPUmemoryandmaps aGPU-centricapproachforGPUstorageaccess,whichcan
themviatheGPUdriver,makingthemvisibletootherdevices submitI/Orequestsdirectlytothestoragedevicecompletely
onthePCIebus.Further,BaMintegratesanNVMedriverinto bypassing the CPU. Meanwhile,the GPU-centric solution
theGPU,enablingGPUthreadstodirectlysendNVMeI/O needstosupportessentialmanagementandprovideasetof
commands,whicharethenexecutedbytheSSDcontrollers. POSIX-likefilesysteminterfacestoGPUprograms.
Byanalogy,itcanbeseenthatBaMadoptsasimilarap- Thesetwoobjectivesmakeitnecessarytodesignanewfile
proachtothewell-knownStoragePerformanceDevelopment systemforGPUs.Typically,afilesystemneedstoimplement
Kit(SPDK)[57]: bothprovideafullblockstackasauser- aminimumsetoffunctionalities,including:(i)maintaining
levellibrarytoenabledirectstorageaccess,respectivelyfor metadataforfilesanddirectories(includingtheinodeinforma-
224    23rd USENIX Conference on File and Storage Technologies USENIX Association

CPU Memory GPU Memory doesnotsupportthesimultaneousestablishmentofNVMe
|       |             |     |     |                  |     |     | queuepairsonboththehostandtheGPU. |     |     |     |     | Asaresult,the |
| ----- | ----------- | --- | --- | ---------------- | --- | --- | --------------------------------- | --- | --- | --- | --- | ------------- |
| User  | CPU Runtime |     |     | GPU Applications |     |     |                                   |     |     |     |     |               |
Kernel  Lib_Gemini GPUisunabletodirectlysubmitNVMecommandstoNVMe
devices.
|     | MMeettaaddaattaa |     | Info |     | Data | Data |     |     |     |     |     |     |
| --- | ---------------- | --- | ---- | --- | ---- | ---- | --- | --- | --- | --- | --- | --- |
G V D K   Map... C l us te r C l us te r (3)InefficiencyofGPUpagecache.Establishingapage
|            | GGVVDDKK  FFiillee |     |     | ping | ...       |           |     |     |     |     |     |     |
| ---------- | ------------------ | --- | --- | ---- | --------- | --------- | --- | --- | --- | --- | --- | --- |
| H e lp e r |                    |     |     |      | N V M e   | N V M e   |     |     |     |     |     |     |
FFiillee  SSyysstteemm N VM e   of fs et offset offset cache on a GPU file system can fully leverage the GPU’s
|     |     |     | H e a | d e r |     |     |     |     |     |     |     |     |
| --- | --- | --- | ----- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
GPU Storage Volume Layer internal memory bandwidth,significantly surpassing PCIe
| Block Layer |     |     |     | Page Cache |     |     |     |     |     |     |     |     |
| ----------- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
bandwidth.However,modernGPUsdonotsupportapublic
documentedprivilegedmode[45],meaningthatpagecache
NNVVMMee
|     |     |     | I/O |     |     |     | canonlybeconstructedwithintheGPUprocess,makingit |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- |
CCoonnttrrooll
| BBlloocckk |     |     | Queue |     | ... |     |     |     |     |     |     |     |
| ---------- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
difficulttoshareacrossGPUs.Thisresultsinmemoryredun-
| Share | Admin  | I/O  | Driver |     |         |     |                   |     |                 |     |         |              |
| ----- | ------ | ---- | ------ | --- | ------- | --- | ----------------- | --- | --------------- | --- | ------- | ------------ |
|       |        |      |        |     | I/O QPs |     | dancyandincreases |     | synchronization |     | issues. | Moreover,the |
| NVMe  | QP QPs |      |        |     |         |     |                   |     |                 |     |         |              |
pagecacheincorporatesintricatecontrollogictoensuredata
consistency.ImplementingthissamelogicwithinGPUsmay
|     |     |     |     | PCIe |     |     | leadtoareductioninGPUparallelism,compromisingsys- |     |     |     |     |     |
| --- | --- | --- | --- | ---- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- |
Mem NVMe  temperformance.Therefore,aGPU-specificsystemdesignis
|     |     |     |     | SSDs |     | GPU | crucialtomaintainingoptimalsystemperformance. |     |     |     |     |     |
| --- | --- | --- | --- | ---- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- |
(4)GPUprogrammingcomplexity.ToimplementaGPU-
Figure3:OverviewofGeminiFS.
specificfilesystemcapableofsharingmetadatawiththehost
filesystem,GPUprogramsmustefficientlycoordinatewith
tionandtransactionprocessingforconsistency),(ii)mapping
logical offset to physical data blocks for I/O requests,(iii) thehostfilesystemandNVMedevicedriversonthehostker-
nel.ToprovideaPOSIX-likeinterfaceforhostprogrammers,
offeringaunifiedinterfaceforupper-layerapplications,and
|     |     |     |     |     |     |     | itis essentialto |     | abstractthe | differences | among | underlying |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ----------- | ----------- | ----- | ---------- |
(iv)cachingrecentlyaccesseddatablocksforperformance
|          |                |          |     |        |         |          | system processing |     | units | and ensure | compatibility | with the |
| -------- | -------------- | -------- | --- | ------ | ------- | -------- | ----------------- | --- | ----- | ---------- | ------------- | -------- |
| purpose. | Unfortunately, | building |     | such a | general | GPU file |                   |     |       |            |               |          |
existingwell-establishedGPUprogrammingmodels,which
systemisprohibitivelydifficult,sinceGPUsarenaturallyun-
suitableforrunningastatefulsoftwaresuchasafilesystem needsdeveloperstoexplicitlydistinguishbetweenhostand
GPUcode,aswellasmanagethemovementofdatabetween
thatrequirescomplexmetadatamaintenance[12].
|     |     |     |     |     |     |     | the CPU | memory | and the | GPU | memory [28,46]. | This ap- |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------ | ------- | --- | --------------- | -------- |
ConsideringallGPU-accessedfilescanbemanaged(e.g.,
proachdemandsaconsiderableprogrammingeffort.
created,moved,anddeleted)bytheCPU,astraightforward
solutionistointroducealightweightGPUfilesystemthat
coexistswiththehostfilesystem,sothatthefilesystemmeta-
3 GeminiFS
datacanbemanagedontheCPUandsharedwiththeGPU.
However,applyingthismethodtoGPUscenariosposesthe To address these challenges,we presentGeminiFS,a com-
followingchallenges. panionFileSystemforGPUs,whichprovidesGPUprograms
(1)Metadatasynchronization.Thefilesystemmetadata with direct access to disk space managed by the host file
needstobesynchronizedefficientlyandsafelybetweenthe
systemthroughfileinterfaces.Thearchitectureoverviewof
hostandtheGPU.First,itisdifficulttofullyutilizethehigh GeminiFSisshowninFig.3.
| parallelism | of the GPU | in  | metadata | synchronization |     | [28], |     |     |     |     |     |     |
| ----------- | ---------- | --- | -------- | --------------- | --- | ----- | --- | --- | --- | --- | --- | --- |
whichmaycauseadegradationinI/Operformance.Second,
3.1 CPU-BypassingviaMetadataEmbedding
| in traditional | host file | systems | like | EXT4,the | metadata | is  |     |     |     |     |     |     |
| -------------- | --------- | ------- | ---- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- |
exclusivelymanagedinthehostkernel.Whenboththehost
|     |     |     |     |     |     |     | File systems | achieve | a   | wealth | of functionalities | based on |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ------- | --- | ------ | ------------------ | -------- |
andtheGPUhavetheirownfilesystems,itischallengingto metadata.Typically,metadatacomprisesthefollowingcompo-
ensuremetadatasafety,asGPUfileoperationscanbeclosely nents:inode,superblock,directories,indexstructure,journal,
intertwined with metadata operations. It would potentially etc.GeminiFSembedsthemetadataofthehostfilesystemto
underminethebenefitofbypassingCPUandresultsinsubop- facilitatesharingthismetadatabetweentheCPUandGPU,
timalperformanceduetocommunicationoverhead[5].
therebyenablingfilesystemfunctionalitywithintheGPU.
| (2) Limitations | of  | the NVMe |     | device | driver. Tradition- |     |     |     |     |     |     |     |
| --------------- | --- | -------- | --- | ------ | ------------------ | --- | --- | --- | --- | --- | --- | --- |
ally,theNVMedriverinthekernelmanagestheNVMehost
3.1.1 SelectiveEmbeddingofMetadata
partoftheprotocolthroughthenativedriveravailableinthe
operating system. The driver adheres to the NVMe proto- Embeddingallfilesystemmetadatadirectlywithinthefiles
col specification to carry out the initialization procedures, andconstructingacompletefilesystemontheGPUarepro-
| whichincludesimplementingtheAdminqueuepairandI/O |     |     |     |     |     |     | hibitivelycostly. |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- |
queuepairsusedtosubmittheadminandI/Ocommandsto First,the kernel file systems on the host have exclusive
theNVMedevice.Currently,theNVMedriverinthekernel controlovermetadatamanagement,primarilytoupholdthe
USENIX Association 23rd USENIX Conference on File and Storage Technologies    225

securityandintegrityofthefilesystem.Performingfileop-
m1 m2 m3
erations on GPUs is inherently intertwined with metadata
L1 index L2 index Block Offset
File type
manipulations. For instance,appending data during writes
NVMe NVMe
requirestheallocationofindexstructures,whereasopening File size offset offset
andclosingfilesinvolvesupdatingaccessandmodification Access mode
timestamps.Tomaintaincoherence,metadataneedstobesyn- IO block size
L1 Tables L2 tables
chronizedbetweentheCPUandGPUfilesystems.Thisruns Blocks
countertoourinitialobjectiveofbypassingtheCPU.Fortu- Offset ...
nately,ouranalysisinSection2.1revealsthatGPUstorage NVMe offset
I/Oworkloadspossessadegreeofpredictability,permitting
Dirty Bitmap
ustoobtainstorageaccessinformationbeforehand,guided NVMe offset Used Block Data Blocks
bythemodelsettings.Thisadvantageousfeatureallowsus
topreemptivelyallocateafixed-sizefileonthehostforGPU- Figure4:Filewithmetadataembedding.
acceleratedapplications,integratingonlyexistingmetadata
mentingaddresstranslationonaGPUwouldrequirelotsof
(e.g.,accessmode,filesize,andindexstructure).Wedonot
effortandwoulddecreasetheefficiencyofGPUI/O.There-
needtoallocatenewmetadatawithintheGPU’sfilesystem
fore,weimplementedakernelmodule,GVDKhelper,onthe
andsynchronizeitwiththeCPU’sfilesystem.
host.Duringfilecreation,thismoduleobtainsthephysical
Second,specificmetadatarelatedtofilesystemmanage-
blockoffsetcorrespondingtoeachlogicalblockfromthehost
ment is neither suitable nor necessary for implementation
kernel and embeds it into the file. Although this results in
on the GPU side. For instance,directories in a file system
approximatelya0.2%capacityoverhead(asa4KBphysical
areusedtoorganizefiles.However,implementingthemon
blockrequires8BtostoretheNVMeoffset),itcanenhance
the GPU significantly increases programming complexity.
GPUI/Operformance.
Furthermore,theprimaryprogramminglanguagesforGPUs,
suchasCUDA,involveapplicationswherethesourcecodeis
3.1.3 FileOrganization
amixtureoftraditionalC++hostcodeandGPUdevicefunc-
tions.Fromadeveloper’sperspective,itisstraightforwardto
Basedontheaforementioneddesignapproaches,wepropose
obtainhostfilesysteminformationanddirectorydetailsusing
afileformattailoredforGPUusage,namedtheGPUvirtual
traditionalC++.Therefore,wedonotembedsuchmetadata
diskformat(GVDK).Fig.4illustratestheorganizationofthe
forfilesystemmanagement;instead,weonlyembedprivate
fileformat.
metadataspecifictoeachfile.
TheGVDKisorganizedinunitsofblocks,eachofwhich
Privatemetadataspecifictoeachfileencompassesthefile is equivalent to the block size of the host file system (for
type,filesize,I/Oblocksize,datablocks,indexstructure,and instance,4KinthecaseofEXT4).Ablockisaunitinwhich
blockbitmap.Byleveragingthemetadata,wecanperform allallocationsaredonebothforactualdataandmetadata.The
operationsliketranslatingfilevirtualoffsetstophysicaldisk privatemetadataspecifictoeachfileisembeddedwithinthe
offsets,managingfileoffsets,andassessingread/writeranges, firstblockofthefile.Whenthefileisopened,thesedatawill
whichpavethewayforofferingaread()andwrite()interface bereadoutandcachedinGPUmemory.
to GPU programs. In addition,the metadata also includes GeminiFSusesatwo-levelstructuretomapfileoffsetto
a dirty bitmap, which GeminiFS utilizes to support crash NVMeoffset.Theyarecalledfirst-levelmappingtable(i.e.,
consistency.ThedirtybitmapNVMeoffsetinthemetadata L1table)andsecond-levelmappingtable(i.e.,L2table).The
pointstoacontiguousstoragepage,whereeachbitrecords L1tablehasavariablesize(storedintheheader)andmayuse
whetherthecorrespondingfilepagehasbeenwritten.After multipleblocks.However,itmustbecontiguousinthefile.
thedataiswritten,thedirtybitmapflagisupdated,andthe EachentryintheL1tablerecordsanNVMeoffsetthatpoints
bitmapwillbeflushedlater. toanL2table,witheachL2tablebeingexactlyoneblockin
size.Similarly,eachentryintheL2tablerecordsanNVMe
offsetthatpointstoadatablock.AfileoffsetofGVDKm
3.1.2 EmbeddedBlockMap
issplitintothreeparts,i.e.,m=(m1,m2,m3),wherem1is
Incurrentfilesystems,theindexstructureistypicallyacom- theindextotheL1table,whichisusedtolocatethecorre-
plexdatastructure.Forinstance,inEXT4[26],anextenttree spondingentryintheL2table;m2istheindextotheL2table,
isemployedtorecordtheblockmappingbetweenlogicaland whichisusedtolocatetheNVMeoffsetofthecorresponding
physicalblocks.Implementingthetranslationlogicinvolves datablock;andm3istheoffsetinthedatacluster.Toacceler-
intricate controllogic andbranchjumps. Nevertheless,the atetheaddresslookup,wheninvokinganopen()operation,
controlunitofaGPUisrelativelysimpleandcannoteffec- thismappingtablewillbecachedintotheGPUmemory.For
tively handle advanced features,such as branch prediction systemsecurity,GeminiFScanadoptasimplemethod(sim-
andout-of-orderexecutionincomplexprograms[28].Imple- ilartoCUDAlib)toprovideuserswithonlypre-compiled
226 23rd USENIX Conference on File and Storage Technologies USENIX Association

static/dynamiclibrariesandheaderfilestoconcealthedetails firstandthirdstepsoftheinitializationprocessforthestan-
offiles.Furthermore,GeminiFScanperformintegritychecks dardNVMesubsystem,asdefinedbytheNVMespecification
on the metadata region to prevent malicious tampering of mentionedearlier.Thecorrespondingchangesforeachstage
theembeddedmetadata,thusprotectingagainstunauthorized aredetailedbelow:
accesstootherfilesonthedisk. (1)Beforethefirststage,weinitiallyallocatememoryfor
the I/O queue in the GPU memory. The GPU buffer man-
agementmodulethentranslatestheGPUvirtualaddressinto
3.2 CPU/GPUSharedNVMeDriver
aDMAaddress,makingitvisibletotheNVMedevice.By
GeminiFS requires the establishment of a storage device’s leveragingtheflexibilityoftheNVMestandard,wepresetthe
controlplaneanddataplaneonboththeCPUandGPUsi- numberofI/Oqueuesandtheirdepth,recordingthisinforma-
multaneously.However,currentoperatingsystemkernelsor tionintheGPUbuffermanagementmodule.Aftercompleting
devicedriversdonotpossesssuchcapabilities. thesesteps,westartthefirststepofthestandardprocess.
The NVMe protocol [54] establishes the commands for (2) In the third step,the controlleralso registers the I/O
communication between the host and SSD and how these queuesthathavebeenallocatedintheGPUmemory.These
commandsareexecuted.Onatypicalserver,theCPUallo- queuesdonotrequiretheuseofhostinterruptstocomplete
catessubmissionqueues(SQ)andcompletionqueues(CQ) I/Ooperations;instead,theyutilizeGPUthreadpolling.In
in host memory to transmit NVMe commands. The estab- GPU memory, we utilize the high-throughput I/O queues
lishmentoftheNVMedevicecontrollerintheLinuxkernel driverproposed by BaM [39] to achieve efficient SQ com-
includesthefollowingprocesses: First,exactlyonepairof mandsubmissionandCQpollingforGPUthreadswithhigh
an admin submission queue (SQ) and its associated com- parallelism.
pletionqueue(CQ)iscreated,whichisusedtomanagethe
NVMecontroller(e.g.,creationanddeletionofI/Osubmis- 3.3 GPU-SpecificPageCache
sionandcompletionqueues,abortingcommands,etc.).Next,
the NVMe driver submits the admin commands to get the Comparedwithpage cache on CPUs, constructing a page
capabilities and settings of the controller data structure. It cacheonGPUsexhibitstwoprimarydistinctions:
also submits the admin commands to indicate capabilities Firstly,becauseGeminiFScanonlyruninnon-privileged
andsettingsspecifictoaparticularnamespace.Finally,the modeontheGPU,pagecachescanonlybeallocatedwithin
controllerallocatesanappropriatenumberofI/Oqueuepairs GPU processes’ memory space. This results in the redun-
andregistersthemusingtheadmincommand. dancyofpagecachesandsubsequentwastageofGPUmem-
Afterthisprocess,theNVMedriverregistersthenames- ory when multiple GPU processes open the same file. To
pace with the block layer as host-managed block devices, addressthisissue,wehavedesignedapagecachemanage-
uponwhichtheoperatingsystemcanestablishafilesystem. mentmodulewithintheSNVMeonthehost. Thismodule
OurinsightisthattheGPUdoesnotneedtomanagethe functionsasfollows: wheneveraprogram opensafileand
entire NVMe device space; it only needs to correctly read establishesapagecacheontheGPU,itcheckswhetherthe
andwriteitondemand.Therefore,theGPUdoesnotneedto correspondingpagecacheexistswithinthemanagementmod-
implementtheentirecomplexNVMedriver,whichincreases ule.Ifnot,itallocatestherequisitememoryontheGPUand
programmingcomplexityandmakestheNVMedeviceexclu- employsthehostdrivertoestablishapersistentmapping.Sub-
sivetotheprocess.EstablishingI/OqueuepairsontheGPU sequently,itretrievesaninter-processmemoryhandleforthe
isonlynecessary,andprovidingarelativelysimpleI/OQP existing device memory allocation and stores it within the
drivercanestablishthecontrolplaneforNVMeI/O. managementmodule.Whenanotherprocessattemptstoopen
Thus, we propose the CPU/GPU Shared NVMe Driver thesamefile,apointertothecorrespondingpagecachecan
(SNVMe),asillustratedinthelowerhalfofFig3,enclosed be obtainedvia this memory handle. CurrentGPU drivers,
withinthebluedashedbox.ComparedtothestandardNVMe such as CUDA, already support this process; for instance,
hostdriver,SNVMemakestwomajorchanges.First,wehave cuIpcGetMemHandleexportsexistingdevicememoryforuse
addedaGPUbuffermanagementmoduletotheNVMedriver. inanotherprocess,andnvidia_p2p_get_pages_persistentcan
Themainroleofthismoduleistorecordtheexistingmemory pinGPUmemorypersistently.
allocationonGPUs,whichareusedtoconstructI/Oqueues. Secondly,locksareessentialtoensuremutuallyexclusive
ThismodulealsocooperateswiththeGPUdriver,usingthe access to the cache when modifying page mappings in the
nvidia_p2p_get_pages_persistentAPItopintheI/Oqueue page cache during file page swapping. Due to the GPU’s
memory pages allocated on the GPU and make the pages higher level of parallelism,lock contention becomes more
underlyingarangeofGPUvirtualmemoryaccessibletoa severethanthatontheCPU,whichcanleadtoasignificant
third-partydevice.Then,itusesnvidia_p2p_dma_map_pages degradation in page cache performance. Thus, GeminiFS
toconvertGPUvirtualmemoryintoDMAaddresses,making employsthefollowingtwomethodstomitigatethisissue.
itvisibletotheNVMedevice.Secondly,wehaverevisedthe GeminiFSacquirespagesatthewarplevelratherthanthe
USENIX Association 23rd USENIX Conference on File and Storage Technologies 227

threadlevel,whichhelps reduce lockcontention to a man- Table2:CPU-sideandGPU-sideAPIsofGeminiFS.
ageablelevel.Fromamicro-architecturalperspective,each
Type GeminiFSInterface
Streaming Multiprocessor(SM),whichis the fundamental
intGeminifs_init(char*dev_path,
componentofGPUs,executesoneinstructionfromawarpata
char* GPU_ids,intQ_num)
time,andthenumberofSMsandwarpschedulersdetermines host
dev_fdG_open(char*path,uint16flag,
themaximumnumberofwarpsthatcanexecuteconcurrently,
uint64_tcache_capacity,intpage_size)
which in turn affects the intensity of lock contention. For
intG_close(dev_fdfd)
example,intheAmperearchitecture[34],thereare108SMs,
intG_read(dev_fdfd,
eachwith4warpschedulers.Thismeansthatevenifthere void*buf,uint64_toffset,size_tnbyte)
device
arethousandsofwarpstryingtoacquiredifferentpages,at intG_write(dev_fdfd,
most4×108 controlflows willbe competing forthe page void*buf,uint64_toffset,size_tnbyte)
cache lock at any given moment. Compared to the thread intG_sync(dev_fdfd)
contentionatthelevelofthousands,thislevelofcontentionis
morereasonable,albeititstillexceedsthecontentiontypically
observedintheCPUpagecache. forboththeunderlyingarchitectureandfilesystem.Fromthe
Tofurtherreducelockcontention,aconstant-timecontainer perspectiveofGPUprogramming,developersutilizeasimple
forinsertion,deletion,andlookupoperationscanbeemployed. interfacetoinitializeGeminiFS,remainingoblivioustothe
First,ahashtableisusedtotrackthemappingbetweenfile complexity of the underlying system components through-
pagesandmemorypages,allowingforconstant-timelookup outthesysteminitializationprocess.Thereisnodiscernible
todeterminewhetherapageisacachehit.Ifcachemisses,a differencefordeveloperswheninitiatingfileI/Ooperations
combinationofadoublylinkedlistandahashtableisusedto withintheGPUcomparedtothoseonthehost,anditcanbe
managepageswithzeroreference.Thiscombinationensures accessedviaasubsetofPOSIX-likefileI/OAPIsoutlined
thatinsertion,deletion,andlookupoperationsareallconstant- inTable2.TheseAPIsstreamlinetheprocessofintegrating
time. If cache hits,it is first queried the page if it is in the GeminiFSintoexistingframeworks,suchasPyTorch’sDat-
zero-referencesetandthenremovedfromthissetinconstant aLoader[37].BymerelysetupGeminiFSattheinitialstage
time.Ifapageisreleasedandbecomesazero-referencepage andreplacingthehostfilesysteminterfacewithGeminiFS’s
again, it is added to the end of the doubly linked list. By interface,theneedforahostbouncebufferiseliminated.
doingso,pagesthathavenotbeenreferencedforalongtime libGeminidoesnotprovidethefullsetofPOSIXseman-
will be gradually moved to the head of the doubly linked tics,suchascrashconsistency.Weleavetheoptionofcrash
list,becomingthecoldestpages. Thisapproachminimizes consistencytotheapplicationsbyprovidingthesyncinter-
thedurationofcriticalsectionswhenmanipulatingthepage facetoensurethatdataandmetadataareflushedtothedisk
cache,thusreducinglockcontention. consistently.Thisisbecauseofthefollowingreasons.First,
Basedontheabovedesign,GeminiFSoffersaGPUpage asanalyzedinSection2.1,dataismostlyread-only.Interme-
cache with a large tuning space. The page cache size and diatedataoffloadedtodiskduringtrainingdoesnotrequire
pagesizecan beflexiblysettoadjustthecontention inten- consistencyguarantees.Second,allmetadatawithinfilesis
sityofpagecachelocks.Whenthedatalocalityofthewarp managedbytheapplicationitself,andGPUread/writeopera-
remainsunchanged,increasingthepagesizecanreducethe tionsdonotaffectthemetadataofthehostfilesystem.
numberofpagesinvolvedbythewarp,therebydecreasingthe Inaddition,libGeminidoesnotimplementacomprehen-
frequencywithwhichthewarpaccessesthepagecache,and sivesuiteofPOSIXI/Ooperations.Weconcurwiththeview-
consequentlyreducingpagecachelockcontention.Thepage pointexpressedinsomeworks[41]thatbeingfullyPOSIX-
cachealsoincludesaprefetchingfeature,whichallowsfor compliantisnotonlycostlybutalsounnecessaryformostuse
adjustingthenumberofprefetchedpages.Thisenablesasin- cases.Thecurrentread/writeinterfacesaresufficienttomeet
glewarptoissuealargenumberofNVMecommandstothe the storage needs of GPU-accelerated applications. In this
NVMeI/Oqueuewhileacquiringpagesatwarpgranularity, section,WewillpresenttheGPUprogrammingmodeinthe
therebymaximizingNVMebandwidth.TheGPUpagecache contextofsystemstartupandtheread/writeprocess.Fig.5
withalargetuningspacecanhelpusersachieveoptimalper- illustratesthecorrespondingdiagram.
formanceacrossdifferentGPUmodels. Notethatpagecache
SNVMeInit:AsillustratedinthefirstdiagramofFig.5,
ispartoftheGPUuser-spaceprogram,andthusleavingitup
thedeveloperinitializesthesystembycallingGeminifs_init,
toasettingwillnotintroducenewsecurityvulnerabilities.
which serves as a CPU-side interface. This interface com-
prises three parameters: (i) dev_path,whichrepresents the
3.4 GPUProgrammingModel NVMedevicetobeused(e.g.,/dev/nvme0n1);(ii)GPU_ids,
which signifies an array of GPU device IDs forwhich I/O
In this section,we presentlibGemini,a GPU-orientedpro- queues need to be established; and (iii) the number of I/O
grammingmodelwithinGeminiFS,whichoffersabstractions queuepairstobecreatedoneachGPUdevice.Afterthede-
228 23rd USENIX Conference on File and Storage Technologies USENIX Association

(1) System Startup (2) GVDK File Pre-allocation (3) GVDK File Open (4) GVDK File Read/Write (5) GVDK File Close
|  O U      | re           |     |  dn        |  e    | elba          |     | G 1.3   | )tesffo,ezis,rdd |     |     |        |
| --------- | ------------ | --- | ---------- | ----- | ------------- | --- | ------- | ---------------- | --- | --- | ------ |
| /I eM P G |  e llo       |     | skcolb     | ht te | M E 5.2       |     | na      | etirw            |     |     | G 1.5  |
| /U        | zilaitin rtn |     | a e G 2.2  |       | T  gnippa ppa |     | M d     |                  |     |     |        |
| V P       | oC           |     | lif etae   | G     |               |     | eht te  | p                |     |     | eht te |
| N C       |              |     |  etaco M   |  4    | gni m         |     | a       | /da              |     |     |        |
|  etae  no | I 2  e       |     | ate eht te | .2    | T  eb         |     | nipp    | erp 1            |     |     |        |
|  se       | .1 M V       |     | ad         |       | M elba  eht d |     | M       |                  |     |     | M      |
| rC        | N            |     | rC llae at |       |               |     | T g ate | av,d             |     |     | ate    |
|  1 ue     |              |     |  1 F       |       |               |     | a       | .4               |     |     |        |
.1 uQ .2 rp eli elb ad f( ad
|     |     |     |     |     |     |     |  at |     |     |     |  at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
4.2 NVMe requests
|                      |     |     | File   | GVDK   | GVDK  | Metadata  | GVDK  | Lib_Ganymede | GVDK  | File   | GVDK  |
| -------------------- | --- | --- | ------ | ------ | ----- | --------- | ----- | ------------ | ----- | ------ | ----- |
|                      |     |     | System | Helper | File  | Cache     | File  |              | File  | System | File  |
| SShhaarree  NNVVMMee |     | GPU |        |        | NVMe  |           | NVMe  |              | NVMe  |        | NVMe  |
 Mem CPU Mem Device GPU Mem Device GPU Mem Device CPU Mem Device
CCPPUU  MMeemm
Figure5:ThesystemdiagramofperformingfileRead/WriteonGPUusingGeminiFS.
veloper calls Geminifs_init,the NVMe I/O queues will be basedontheresultsobtainedbypollingtheCQandreturn
createdontheGPUs,andsubsequently,thesysteminitializes thenumberofbytestransferred.
SNVMeperthemethoddescribedinSection3.2. FileSync:BasedontheanalysisinSection2.1,duringthe
|            |     |          |        |            |     |           | generation | of Model weights | and KV-cache | in  | GPU work- |
| ---------- | --- | -------- | ------ | ---------- | --- | --------- | ---------- | ---------------- | ------------ | --- | --------- |
| File Open: | The | GeminiFS | offers | a CPU-side |     | interface |            |                  |              |     |           |
calledG_Open. ItreturnsaPOSIX-likefiledescriptorthat loads,write operations occur. These involve modifications
|          |          |     |                   |     |        |          | to both internal | file metadata | and data | blocks. | To mitigate |
| -------- | -------- | --- | ----------------- | --- | ------ | -------- | ---------------- | ------------- | -------- | ------- | ----------- |
| GPU-side | programs | can | utilize. Compared |     | to the | standard |                  |               |          |         |             |
theriskofdatalossorfilecorruption,GeminiFSprovidesa
openinterface,thisinterfaceabstractsthecomplexlogicre-
quiredbyGeminiFS,suchascreatingspecificallyformatted GPU-sideG_syncmechanismtoensurethatthemodifiedfile
systemmetadataandcachedfiledataarewrittentothefile,
filesandestablishingpagecaches.Theprocessisillustrated
| inFig.5(2)(3). |     |     |     |     |     |     | guaranteeingdatapersistence. |     |     |     |     |
| -------------- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- |
FileClose:Toensuretheencapsulationofoperations,Gem-
Thisinterfaceusesfourinputparameters,namely,path,flag,
iniFSoffersaCPU-sideG_syncinterfacefunction.Thisfunc-
cache_capacity,andpage_size.Thepathparameterdenotes
tionlocatesthemetadataandthepagecacheofthefilewithin
| the address | of a | specific | path on the | host. | It is noteworthy |     |     |     |     |     |     |
| ----------- | ---- | -------- | ----------- | ----- | ---------------- | --- | --- | --- | --- | --- | --- |
theGPUbasedondev_fd.Afterensuringthatthemodified
| that G_open | is  | solely capable | of opening |     | GeminiFS | files. |     |     |     |     |     |
| ----------- | --- | -------------- | ---------- | --- | -------- | ------ | --- | --- | --- | --- | --- |
datahasbeenwrittentodisk,itreleasestheseGPUmemory
Theflagparameter,similartoitscounterpartinthestandard
resources.
openfunction,mustincludeoneoftheaccessmodeslisted
below:O_RDONLY,O_WRONLY,orO_RDWR.Ifthespec-
ifiedpathdoesnotexist,theflagmustadditionallyinclude 4 Evaluation
O_CREAT,promptingG_Opentogeneratethefileinaccor-
Inthissection,weseektoanswerthefollowingquestions:
| dance with | the format |     | detailed in | Section | 3.1. In | addition, |     |     |     |     |     |
| ---------- | ---------- | --- | ----------- | ------- | ------- | --------- | --- | --- | --- | --- | --- |
theflagshouldencompassO_DIRECTtoindicatewhether
• WhatistheperformanceadvantageofGeminiFScompared
thepagecacheshouldbeemployed.Afterthecompletionof
tothestate-of-the-artsolutions(§4.1)?
theaforementionedprocedures,GeminiFSproceedstostore
• HowtomaximizetheperformanceofGeminiFSonGPU
thepertinentmetadataofthefileintheGPU’smemoryand
Architectures(§4.2)?
providestheaddressofthismetadatacache.Thisaddressis
abstractedasdev_fd.Thesubsequentread/writeoperations • HowdoesGeminiFSbenefitreal-worldapplications(§4.3)?
canleveragedev_fdtoaccessthenecessarymetadata.
Systemsettings.WehaveimplementedGeminiFSforre-
FileRead/Write:TheGeminiFSofferstwoGPU-sidein- centlyreleasedGPUs,whereabout2000line-of-code(LoC)
terfacesfordatatransfer,namelyG_readandG_write.Both isforthesharedNVMekernelmodule,andabout3000LoC
of these functions encompass four parameters identical to forLibGemini.Allexperimentsareconductedona64-core
thestandardpread/pwrite:dev_fd,buf,offset,andnbyte.Ini-
IntelXeon5416Sserverequippedwith512GBofmemory,
tially,theinterfaceslocatethemetadataofthefiletoberead runningUbuntu20.04andLinuxkernel5.15.0.Theserver
from or written to based on dev_fd. They begin by assess- wasequippedwithaGPUwith80GBHBM[33].TheGPU’s
ingtheaccessmode,checkingwhethertheoffsetandnbytes HBMbandwidthpeaksat1,935GB/s,anditinterconnected
fallwithinthefile’sboundaries.Iftherequestisvalid,they with the host via PCIe Gen4 x16,offering a bandwidth of
convertthevirtualaddress(vaddr)usingthetransformation 64GB/s.TheNVMedeviceisanIntelOptane5800X[8]with
methoddescribedinSection3.1,transformingthefileoffset an EXT4 file system mountedon it. The NVMe controller
intoanNVMeoffset.Subsequently,theyinvoketheNVMe ofthisdevicesupportstheestablishmentofupto135pairs
I/OqueuedriverontheGPUsidetogenerateanNVMere- ofI/OQPs.Weallocate64QPsonthehostand32QPson
quest, which is then submitted to the CQ. Following this, theGPU.Theallocationof32QPsissufficientforGPUto
theydeterminethecompletionstatusoftheread/writerequest maximizethebandwidthofthedisk[39].Theblocksizeof
USENIX Association 23rd USENIX Conference on File and Storage Technologies    229

6000
4000
2000
0
0.5 1 2 4 8 16 32 64 128 256 5121024
)s/BM(htdiwdnaB
GPUfs GDS BaM Geminifs
4400
4000
NVMe Device Max Bandwith 3600
3200
2800
2400
2000
1600
1200
800
400
0
1 4 8 16 32 64 128 256 512 1024
Number of threads
Figure6:Comparisonof4KreadI/ObandwidthofGeminiFS
withGPUfs,GDSandBaMatvariouslevelsofparallelism.
theEXT4filesystemonthehostandthatofGeminiFSonthe
GPUareboth4k.NotethatEXT4cannothandlecaseswhere
theblocksizeexceedsthesystempagesize.
Baselines. We compare GeminiFS with state-of-the-art
GPUstoragesolutions.(a):GPUfs[44],CPU-centricsolution
usingtheaccelerator-centricmodel.ForGPUfs,weallocate
fourCPUthreadstohandleincomingrequestsfromtheGPU,
aconfigurationcapableofsaturatingthephysicaldisk’sca-
pacity [57]. (b): NVIDIA GDS [35],CPU-centric solution
usingCPUcodefordataorchestration.ForGDS,weusethe
cufileAPIprovidedbyNVIDIAtocreateCPUthreadsfor
datatransfer.(c):BaM[39]isaGPU-centricsolutionwithout
filesystemsupport.Weemployanon-file-systeminterfaceto
transferdatafromNVMerawdevicestoGPUmemory.
4.1 ComparisonwiththeSOTASolutions
ToinvestigatethearchitecturaladvantagesofGeminiFS,we
initiallycompareitsreadperformance,operatingwitha4K
granularity,acrossvariouslevelsofparallelism,withthatof
GPUfs,GDS,andBaM.Toeliminatetheimpactofcaching
onperformance,ourtestsinthissectionspecificallybypassed
thecachingmechanismofGeminiFS.ForGPUfs,wereduced
its GPU cache size to 256MB and opened host files using
O_directmode.
Bandwidth.Fig.6showsthebandwidthperformanceof
varioussolutionsemployinga4KBgranularityacrossdiverse
levelsofparallelism.ComparedtoGPUfs,GeminiFSexhibits
higherbandwidthacrossallnumbersofGPUthreads,averag-
ing7.33×thebandwidthofGPUfs.Whenthethreadnumber
reaches1,024,GeminiFSreachestheNVMebandwidthpeak.
AlthoughGPUfscanalsoinitiateI/OrequestswithintheGPU
program,exploitingthehighparallelismwithintheGPUtoen-
hancerequestconcurrency,thelimitednumberofcoresonthe
hostCPUleadstoperformancedegradationduetocontention
whenprocessingGPUI/Orequests.GeminiFSbypassesthe
CPU,allowingtheGPUkerneltodirectlysubmitrequeststo
NVMeI/Oqueues.Additionally,GeminiFSincorporatesthe
high-throughputI/OqueuesdesignontheGPUside,proposed
)su(ycnetal
egarevA
GPUfs GDS BaM Geminifs
400
300
200
100
0
1 4 8 16 32 64
Number of threads
Figure 7: Comparison of 4K read I/O average latency of
GeminiFSwithGPUfs,GDSandBaMatvariouslevelsof
parallelism.
byBaM[39],whichenhancestheparallelismofGPUthread
requestsubmissionsandreducescontentionforI/Oqueues,re-
sultinginimprovedoverallperformance.GDSdemonstrates
abandwidththatisapproximately57%higherthanthatofthe
GeminiFSsystemonlywhenthethreadcountrangesfrom1to
16.ThisadvantagestemsfromGDS’sutilizationoftheCPU
to orchestrate data transfers. With its CPU core frequency
reaching4GHz,whichsurpassesthe1GHzoftheGPUcore
(asmentionedin[48]),GDSensuressuperiorperformance
foritssoftwarestack.However,astheGPUthreadcountin-
creasesto128to512,thebandwidthoftheGeminiFSsystem
reaches6.2timesthatofGDS.ThisisattributedtotheGPU’s
ultra-highphysicalparallelism,whichallowsthefilesystem
tofullyleveragethemaximumbandwidthofthediskeven
ata small4K granularity. In contrast,GDS fails to deliver
sufficientparallelismatlowerthreadcountstofullysaturate
theNVMereadbandwidth.Conversely,higherthreadcounts
lead to thread contention, resulting in a decline in perfor-
mance[51].ComparedtoBaM,GeminiFSexhibitsaslightly
lowerbandwidthby4.6%acrossvariouslevelsofparallelism.
Thisisbecause,unlikeBaM,whichutilizesNVMedevices
inarawdevicemanner,GeminiFSaccessesfilesthroughits
read/writeinterfaces.Theseinterfacesincuroverheaddueto
metadataparsingandaddresstranslation.
Latency.Fig.7showstheaveragelatencyof4Ksequen-
tialread.ComparedtoGPUfs,GeminiFSachievesalatency
reduction of (79.6% - - 90.9%) under different number of
threads. This is because GPUfs demands significant mem-
oryonboththeGPUandCPUforI/Orequesttransmission.
Thisalsoprolongsboththecontrolplaneanddataplaneand
leadstoahighI/Olatency.GeminiFSeliminatestheoverhead
incurredbyGPU-to-GPUcommunicationandthesoftware
stackcostonthehost.ComparedtoGDS,whenthenumber
of threads ranges from 1 to 8,the latency of GeminiFS is
57.2%higherthanthatofGDS.However,asthenumberof
threadsincreases,thelatencyofGeminiFSdoesnotriseas
rapidlyasthatofGDS.Specifically,whenthethreadcount
reaches1,024,thelatencyofGeminiFSisonly17%ofGDS.
This advantage is attributed to the high parallelism within
230 23rd USENIX Conference on File and Storage Technologies USENIX Association

700
|     |     |     |     |     |     |     |     |  Write |  Read |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ----- | --- | --- |
fo % sa wb deveihcA wb ypoc lenrek kaep 120%
|      |     |     |  Write |  Read |     |     |                 | 600 |     |     |     |
| ---- | --- | --- | ------ | ----- | --- | --- | --------------- | --- | --- | --- | --- |
| 100% |     |     |        |       |     |     | )s/BG(htdiwdnaB |     |     |     |     |
500
80%
| 60% |     |     |     |     |     |     |     | 400 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
40%
| 20% |     |     |     |     |     |     |     | 300 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | 0   |     | 2   | 4   | 6   | 8   |     |     |     |     |     |
200
Number of prefetched pages
100
| Figure 8: | Contribution |     | of different | numbers | of  | prefetched |     | 0   |         |        |              |
| --------- | ------------ | --- | ------------ | ------- | --- | ---------- | --- | --- | ------- | ------ | ------------ |
|           |              |     |              |         |     |            |     | 1 4 | 8 16 32 | 64 128 | 256 512 1024 |
pagestothepagecacheperformance.Prefetchisneeded.
Number of warps
| the GPU, | which | prevents | performance | degradation |     | due to |        |                 |                          |     |        |
| -------- | ----- | -------- | ----------- | ----------- | --- | ------ | ------ | --------------- | ------------------------ | --- | ------ |
|          |       |          |             |             |     |        | Figure | 9: Contribution | ofdifferentnumberofwarps |     | to the |
threadcontentionforCPUcores,unlikeinthecaseofGDS.
pagecaheperformance.Thepeakbandwidthprovidedbythe
Finally,comparedtoBaM,thelatencyofGeminiFShasonly
pagecacheinGeminiFSexceeds640GBps.
increasedbyapproximately4.8%.
4.2 PerformanceofPageCache
|     |     |     |     |     |     |     |     | 140 |     |  Write |  Read |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | ----- |
Max kernel memcopy bandwidth
120
| GeminiFS | provides | a   | configurable | page | cache | to leverage | )s/BG(htdiwdnaB |     |     |     |     |
| -------- | -------- | --- | ------------ | ---- | ----- | ----------- | --------------- | --- | --- | --- | --- |
100
| theGPU’sinternalbandwidthfully.                   |     |     |     | Weusethesimplemi- |     |     |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- | --- |
| crobenchmarkbelowtoexaminetheessentialperformance |     |     |     |                   |     |     |     | 80  |     |     |     |
60
ofthepagecacheanditssensitivitytoseveralkeyconfigura-
| tionparameters.Themicrobenchmarksequentiallyreadsdata |     |         |        |               |     |           |     | 40          |                      |                         |                         |
| ----------------------------------------------------- | --- | ------- | ------ | ------------- | --- | --------- | --- | ----------- | -------------------- | ----------------------- | ----------------------- |
| from a single                                         | 20  | GB file | in the | GPU kernelvia |     | GeminiFS. |     | 20          |                      |                         |                         |
|                                                       |     |         |        |               |     |           |     | 54 84 36 76 | 28 68 89 001 801 901 | 211 511 611 811 811 911 | 021 121 911 121 021 021 |
| TopreventNVMebandwidthfrombecomingabottleneckin       |     |         |        |               |     |           |     | 0           |                      |                         |                         |
|                                                       |     |         |        |               |     |           |     | 4 8         | 16 32 64             | 128 256 512             | 1024 2048 4096          |
thesystem,weconductedtestsusingmemoryreplicationasa
Pagesize(KB)
substituteforaccessingNVMedevices.
Prefetch.Firstly,Weevaluatedtheimpactofprefetchon Figure10:Contributionofdifferentnumberofpagesizesto
pagecacheperformance.Inthisexperiment,wesetthepage thepagecaheperformance.
sizeto64KBandthepagecachesizeto1GB.Theprefetch
strategyemployedisstraightforward:thepagecachewould
prefetchmultiplepagesintomemoryuponeachcachemiss. This observed trend demonstrates the effectiveness of our
| This strategy | caters | to  | the demands | of sequential |     | read and |     |     |     |     |     |
| ------------- | ------ | --- | ----------- | ------------- | --- | -------- | --- | --- | --- | --- | --- |
strategyinreducinglockcontentionwithinthepagecache.
write workloads. Fig.8 compares page cache performance Currently,a single NVMe device can provide a maximum
withandwithoutprefetchenabled.Beforeenablingprefetch,
bandwidthof7GB/s.Thisimpliesthatitwouldrequireclose
| the read | and write | bandwidth | of  | the page | cache | were only |     |     |     |     |     |
| -------- | --------- | --------- | --- | -------- | ----- | --------- | --- | --- | --- | --- | --- |
to100NVMedrivestosaturatethebandwidthofthepage
30.2% and 28% of the theoretical bandwidth,respectively. cache,makingithighlyunlikelyforthepagecachetobecome
Afterenablingprefetch,regardlessofthenumberofmemory
abottleneckinsystemperformance.
pagesprefetched,thereadandwriteperformanceofthepage
cacheapproximatelyimprovedby2.4×and2.34×,respec- Page size. We also conducted evaluations to assess the
tively,nearlyreachingthemaximumbandwidth. performanceofthepagecacheforvariouspagesizes.With
NumberofWarps.GeminiFSacquiresthepagesinpage awarpcountof128,basedontheexperimentalresultsfrom
cacheatthewarplevelandemploysaconstant-timecontainer theprevioussection,themaximummemorybandwidthfor
forinsertion,deletion,andlookupoperationstoreducelock kernelmemcopyisapproximately120GB/s.Thepagecache
contention.Tovalidatetheeffectivenessofthisstrategy,we comprises4,096pages,andprefetchingisenabledtoenhance
utilizedtheG_Read/G_Writeinterfacesforreadingandwrit- performancefurther.Fig.10showsreadbandwidthfordif-
ingpagecache,assigning32threadstoeachwarp.Then,we ferentpage sizes. As the page size increasedfrom 4KB to
adjustedthenumberofwarpstoevaluatetheperformanceof 1,024KB, the write bandwidth notably rose from approxi-
thepagecacheundervariousconditions.Theresultsareillus- mately45.8GB/sto120.1GB/s,whilethereadbandwidth
tratedinFig.9.Asdepictedinthefigure,thewritebandwidth also climbed from around 48.4 GB/s to 121.4 GB/s. With
steadilyincreasesfromapproximately1.7GB/storoughly 1,024KBpagesize,boththereadandwritebandwidthsap-
641.2GB/s,whilethereadbandwidthrisesfromabout2.3 proachedthe theoreticallimits. Basedon the experimental
GB/stonearly658.1GB/s.Thebandwidthgrowthfollowsa results,itisevidentthatlargerpagesizesaremoreeffective
multiplicativetrend,ultimatelypeakingataround650GB/s. inachievingthepeakbandwidthofthepagecache.
USENIX Association 23rd USENIX Conference on File and Storage Technologies    231

Type FileSize AccessMode CPUtoreducecommunicationoverhead.Ontheotherhand,
ModelWeights 238MB Read&Write theultra-highbandwidthofpagecachealsoimprovessystem
| Checkpoint |     | 713MB/Step |     | Append-onlyseq.write |     |     |     |     |     |     |     |     |     |     |
| ---------- | --- | ---------- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
throughput.
| Activation |     | 57.96GB |     | Read&Write |     |     |     |     |     |     |     |     |     |     |
| ---------- | --- | ------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Fig.11(b)presentstheexperimentalresultsunderthecondi-
tionofunloadingactivations.GeminiFSsignificantlyreduces
Table3:StorageaccessinGPT2-124Mtraining.
|     |     |     |     |     |     |     |     | the training | time,decreasing |     | 94.5% | and | 91% compared | to  |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --------------- | --- | ----- | --- | ------------ | --- |
nativeandGDS,respectively.Underthisworkload,theun-
|     |  Computing  |     |  Checkpoint |     |  Model Weights  |     |  Activation |                                                         |     |     |     |     |     |     |
| --- | ----------- | --- | ----------- | --- | --------------- | --- | ----------- | ------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| 14  |             |     |             |     |                 |     |             | loadingofactivationsaccountsforthemajorityofthetraining |     |     |     |     |     |     |
1000
)s(emitnuR metsyS 12 time,includingalargeamountofsmallI/Os,preventingthe
10 800 effective utilization of system bandwidth. In CPU-centric
| 8   |     |     |     | 600 |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
solutions,GeminiFSmitigatesthefrequentcommunication
6
|     |     |     |     | 400 |     |     |     | overheadbetweentheGPUandtheCPU.Furthermore,the |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- |
4
| 2                |     |     |          | 200 |        |     |          | high-bandwidthpagecacheenablesfullutilizationofsystem |     |     |     |     |     |     |
| ---------------- | --- | --- | -------- | --- | ------ | --- | -------- | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| 0                |     |     |          |     | 0      |     |          | bandwidth.Moreover,comparedtokeepingallactivationsin  |     |     |     |     |     |     |
| NativeDLRover-RM |     | GDS | Geminifs |     | Native | GDS | Geminifs |                                                       |     |     |     |     |     |     |
GPUmemory,thetrainingtimeonlyincreasesbyabout4×.
|     | (a)Disable_Offloading |     |     |     | (b)Enable_Offloading |     |     |     |     |     |     |     |     |     |
| --- | --------------------- | --- | --- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Theoretically,byintegratingmultipleNVMedevicesintothe
Figure11:ComparisonofGPT2-124Mtrainingperformance system,similarperformancetoaDRAM-onlysetupcanbe
| between | GeminiFS,GDS,DLRover-RM |     |     |     | and | a native | way |     |     |     |     |     |     |     |
| ------- | ----------------------- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
achieved.
(memcopy+read/write).(a)MaintaintheactivationonHBM;
(b)Offloadtheactivation.
5 ConclusionandFutureWork
Thispaperpresentsacompanionfilesystem(GeminiFS)for
4.3 PerformanceBenefitforLLMtraining GPUs.GeminiFSrealizesmetadatasynchronizationbetween
thehostandGPUfilesystemsbyembeddingmetadatainto
WecomparedtheperformanceofseveralexistingGPUstor-
|                |     |           |        |          |     |                |     | the file | andextends | the | existing | NVMe | driverto | allowthe |
| -------------- | --- | --------- | ------ | -------- | --- | -------------- | --- | -------- | ---------- | --- | -------- | ---- | -------- | -------- |
| age solutions, |     | including | native | (memcopy |     | + read/write), |     |          |            |     |          |      |          |          |
CPUandtheGPUtosetupcontrolplanesinparallel.These
DLRover-RM[52],GDS,andGeminiFS,inoffloadingdata
enableGPU-centricstoragesolutionstodirectaccesstodisk
generatedduringLLMtraining.DLRover-RMprovidesafast
spacemanagedbythehostfilesystemthroughafileinterface.
| checkpoint | mechanism |     | that | accelerates | the | process | by per- |     |     |     |     |     |     |     |
| ---------- | --------- | --- | ---- | ----------- | --- | ------- | ------- | --- | --- | --- | --- | --- | --- | --- |
GeminiFSshortensthecontrolanddataplanesoftheGPU
formingasynchronousdatapersistence.ThesizeoftheGemi-
storageandimprovesfilesystemperformancebyleveraging
niFSpagecacheissetto2GB.Weconductedtrainingusing
thearchitecturaladvantagesoftheGPU.Itscoexistencewith
| the GPT2-124M |     | model | [18],which |     | is a large | transformer- |     |     |     |     |     |     |     |     |
| ------------- | --- | ----- | ---------- | --- | ---------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
thehostfilesystembettersatisfiesthestorageaccessdemands
| basedlanguage |     | modelwith1.5 |     | billion | parameters. |     | During |     |     |     |     |     |     |     |
| ------------- | --- | ------------ | --- | ------- | ----------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
ofMLapplications.
ourtrainingprocess,weusedabatchsizeof64.Werunthe
|     |     |     |     |     |     |     |     | GeminiFS | will | completely |     | support | multi-GPUs. | Our |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---- | ---------- | --- | ------- | ----------- | --- |
traininginonlythreesteps,witheachstepincludingonefor-
|     |     |     |     |     |     |     |     | roadmap | is as | follows. | We will | first enable | parallel | reads |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ----- | -------- | ------- | ------------ | -------- | ----- |
wardpassandonebackwardpass.Themodelweightswere
|     |     |     |     |     |     |     |     | and writes | by  | splitting | files logically. | Next, | we  | aggregate |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --------- | ---------------- | ----- | --- | --------- |
alsoupdated,andacheckpointwasrecordedaftereachstep.
multipleNVMedevicesusingRAIDtomeetthebandwidth
Thisissufficientforstudyingstorageaccessoptimization,as
requirementsofmultipleGPUs.Forunpredictableworkloads,
thecomputationandstorageaccesspatternsremainalmost
|     |     |     |     |     |     |     |     | GeminiFS | will | adopt file | pre-allocation |     | [21] that | allocates |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---- | ---------- | -------------- | --- | --------- | --------- |
consistentineachstepofLLMtraining.Thecharacteristicof
pre-allocatedfileslotsbeforerunningthesystem,andbatch-
storageaccessisshowninTable3.
allocatefilestofilltheseslotsbasedonactualusageduring
Wecomparedtwotrainingmodels,onethatkeepsactiva-
|     |     |     |     |     |     |     |     | runtime. | Besides,We | will | integrate | GeminiFS |     | into the Py- |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ---- | --------- | -------- | --- | ------------ |
tionsinmemoryduringthetrainingprocessandanotherthat
|          |             |     |         |        |           |     |          | Torch framework |     | so that | state-of-the-art |     | solutions,such | as  |
| -------- | ----------- | --- | ------- | ------ | --------- | --- | -------- | --------------- | --- | ------- | ---------------- | --- | -------------- | --- |
| offloads | activations | to  | storage | during | training, | to  | evaluate |                 |     |         |                  |     |                |     |
vLLM,willbenefitfromit.
| the benefits | ofthe | system | in  | differentscenarios. |     | Fig. | 11(a) |     |     |     |     |     |     |     |
| ------------ | ----- | ------ | --- | ------------------- | --- | ---- | ----- | --- | --- | --- | --- | --- | --- | --- |
presentsthesystemruntimeusingdifferentschemesinthe
firsttrainingmodeandathoroughtime-slicinganalysis.The Acknowledgment
| system | runtime | of GeminiFS |     | has decreased |     | by 25%, | 12% |     |     |     |     |     |     |     |
| ------ | ------- | ----------- | --- | ------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
and10%comparedtonative,DLRover-RMandGDS,respec- We thank our shepherd, Prof. Sudarsun Kannan, and the
tively.Inthistrainingmode,computationtimeaccountsfor anonymous reviewers for their valuable feedback and sug-
themajorityofthetotalsystemruntime,andthemaincontri- gestions. The work is supported by the National Key
butionofoptimizationcomesfromGeminiFS’soptimization Research and Development Program of China (grant no.
ofcheckpointI/O.Specifically,thecheckpointwritetimehas 2022YFB4500302)andtheNationalNaturalScienceFoun-
beenreducedby85%,75%and59%comparedtoothers.This dationofChina(grantno.62441220).YimingZhangisthe
isbecause,ononehand,GeminiFScompletelybypassesthe correspondingauthor.
232    23rd USENIX Conference on File and Storage Technologies USENIX Association

| References |     |     |     |     |     |     | dataprovisioningforrdmatrainingclusters. |     |     |     |     |     | InIEEE |
| ---------- | --- | --- | --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | ------ |
ICNP,2024.
| [1] Nvidiahopperh100. |     | https://resources.nvidia.c |     |     |     |     |                                                |     |     |     |     |     |     |
| --------------------- | --- | -------------------------- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                       |     |                            |     |     |     |     | [11] BinGao,ZhuominHe,PuruSharma,QingxuanKang, |     |     |     |     |     |     |
om/en-us-tensor-core/nvidia-tensor-core-g
pu-datasheet?ncid=no-ncid,2024. DjordjeJevdjic,JunboDeng,XingkunYang,ZhouYu,
|     |     |     |     |     |     |     | andPengfeiZuo. |     | Attentionstore:Cost-effectiveatten- |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ----------------------------------- | --- | --- | --- | --- |
[2] Keivan Alizadeh, Iman Mirzadeh, Dmitry Belenko, tionreuseacrossmulti-turnconversationsinlargelan-
KarenKhatamifard,MinsikCho,CarloCDelMundo, guagemodelserving. arXivpreprintarXiv:2403.19708,
| MohammadRastegari,andMehrdadFarajtabar.Llmina |     |     |     |     |     |     | 2024. |     |     |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- |
flash:Efficientlargelanguagemodelinferencewithlim-
|             |     |                                     |     |     |     |     | [12] JayshreeGhorpade,JitendraParande,MadhuraKulka- |          |           |       |            |     |         |
| ----------- | --- | ----------------------------------- | --- | --- | --- | --- | --------------------------------------------------- | -------- | --------- | ----- | ---------- | --- | ------- |
| itedmemory. |     | arXivpreprintarXiv:2312.11514,2023. |     |     |     |     |                                                     |          |           |       |            |     |         |
|             |     |                                     |     |     |     |     | rni,                                                | and Amit | Bawaskar. | Gpgpu | processing |     | in cuda |
[3] JiyoungAn,EsmeraldAliaj,andSang-WooJun. Barad- architecture. arXivpreprintarXiv:1202.4347,2012.
| dur: Near-storage |     | acceleratorfortraining |     |     | large | graph |                                                 |     |     |     |     |     |     |
| ----------------- | --- | ---------------------- | --- | --- | ----- | ----- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                   |     |                        |     |     |       |       | [13] WeihuaHu,MatthiasFey,HongyuRen,MahoNakata, |     |     |     |     |     |     |
neuralnetworks.In202332ndInternationalConference
|     |     |     |     |     |     |     | Yuxiao | Dong, | and Jure Leskovec. |     | Ogb-lsc: |     | A large- |
| --- | --- | --- | --- | --- | --- | --- | ------ | ----- | ------------------ | --- | -------- | --- | -------- |
onParallelArchitecturesandCompilationTechniques
(PACT),pages225–237.IEEE,2023. scalechallengeformachinelearningongraphs. arXiv
preprintarXiv:2103.09430,2021.
| [4] Jonghyun                                      | Bae,        | Jongsung | Lee,     | Yunho          | Jin, Sam | Son, |                                                  |          |          |       |      |                 |     |
| ------------------------------------------------- | ----------- | -------- | -------- | -------------- | -------- | ---- | ------------------------------------------------ | -------- | -------- | ----- | ---- | --------------- | --- |
|                                                   |             |          |          |                |          |      | [14] HongsunJang,JaeyongSong,JaewonJung,Jaeyoung |          |          |       |      |                 |     |
| Shine                                             | Kim,Hakbeom |          | Jang,Tae | Jun Ham,andJae |          | W    |                                                  |          |          |       |      |                 |     |
|                                                   |             |          |          |                |          |      | Park,                                            | Youngsok | Kim, and | Jinho | Lee. | Smart-infinity: |     |
| Lee. Flashneuron:Ssd-enabledlarge-batchtrainingof |             |          |          |                |          |      |                                                  |          |          |       |      |                 |     |
Fastlargelanguagemodeltrainingusingnear-storage
| very deep | neural | networks. | In  | 19th USENIX | Confer- |     |     |     |     |     |     |     |     |
| --------- | ------ | --------- | --- | ----------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
processingonarealsystem.In2024IEEEInternational
enceonFileandStorageTechnologies(FAST21),pages
SymposiumonHigh-PerformanceComputerArchitec-
387–401,2021.
ture(HPCA),pages345–360.IEEE,2024.
[5] AntonioBarbalace,AnthonyIliopoulos,HolmRauch-
|          |       |          |      |         |             |     | [15] QishengJiang,LeiJia,andChundongWang. |        |            |     |         |            | Gnndrive: |
| -------- | ----- | -------- | ---- | ------- | ----------- | --- | ----------------------------------------- | ------ | ---------- | --- | ------- | ---------- | --------- |
| fuss,and | Goetz | Brasche. | It’s | time to | think about | an  |                                           |        |            |     |         |            |           |
|          |       |          |      |         |             |     | Reducing                                  | memory | contention |     | and i/o | congestion | for       |
operatingsystemforneardataprocessingarchitectures.
|     |     |     |     |     |     |     | disk-based |     | gnn training. | In Proceedings |     | of  | the 53rd |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ------------- | -------------- | --- | --- | -------- |
InProceedingsofthe16thWorkshoponHotTopicsin
InternationalConferenceonParallelProcessing,ICPP
OperatingSystems,pages56–61,2017.
’24,page650–659,NewYork,NY,USA,2024.Associ-
[6] Tom Brown, Benjamin Mann, Nick Ryder, Melanie ationforComputingMachinery.
| Subbiah,     | Jared | D Kaplan, | Prafulla | Dhariwal, |                | Arvind |                                           |     |     |     |     |     |          |
| ------------ | ----- | --------- | -------- | --------- | -------------- | ------ | ----------------------------------------- | --- | --- | --- | --- | --- | -------- |
|              |       |           |          |           |                |        | [16] QishengJiang,LeiJia,andChundongWang. |     |     |     |     |     | Reducing |
| Neelakantan, |       | Pranav    | Shyam,   | Girish    | Sastry, Amanda |        |                                           |     |     |     |     |     |          |
memorycontentionandi/ocongestionfordisk-based
| Askell, | et al. | Language | models | are | few-shot | learn- |              |     |                                     |     |     |     |     |
| ------- | ------ | -------- | ------ | --- | -------- | ------ | ------------ | --- | ----------------------------------- | --- | --- | --- | --- |
|         |        |          |        |     |          |        | gnntraining. |     | arXivpreprintarXiv:2406.13984,2024. |     |     |     |     |
ers. Advancesinneuralinformationprocessingsystems,
33:1877–1901,2020.
|     |     |     |     |     |     |     | [17] SudarsunKannan,AndreaCArpaci-Dusseau,RemziH |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- | --- |
Arpaci-Dusseau,YuangangWang,JunXu,andGopinath
[7] Chia-HaoChang,JihoonHan,AnandSivasubramaniam,
|     |     |     |     |     |     |     | Palani. | Designingatrue{Direct-Access}filesystem |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | --------------------------------------- | --- | --- | --- | --- | --- |
VikramSharmaMailthody,ZaidQureshi,andWen-Mei
|      |                                           |     |     |     |     |     | with{DevFS}. |     | In16thUSENIXConferenceonFileand |     |     |     |     |
| ---- | ----------------------------------------- | --- | --- | --- | --- | --- | ------------ | --- | ------------------------------- | --- | --- | --- | --- |
| Hwu. | Gmt:Gpuorchestratedmemorytieringforthebig |     |     |     |     |     |              |     |                                 |     |     |     |     |
StorageTechnologies(FAST18),pages241–256,2018.
| dataera. | InProceedingsofthe29thACMInternational |     |     |     |     |     |     |     |     |     |     |     |     |
| -------- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ConferenceonArchitecturalSupportforProgramming [18] Andrejkarpathy. Gpt2-124m. https://github.com
LanguagesandOperatingSystems,Volume3,pages464–
/karpathy/llm.c.git.
478,2024.
|     |     |     |     |     |     |     | [19] Thomas | N   | Kipf and Max | Welling. | Semi-supervised |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ------------ | -------- | --------------- | --- | --- |
[8] Intel Corporation. Intel optane dc ssd series 400 gb. classificationwithgraphconvolutionalnetworks. arXiv
| https://www.intel.cn/. |     |     |     |     |     |     | preprintarXiv:1609.02907,2016. |     |     |     |     |     |     |
| ---------------------- | --- | --- | --- | --- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- |
[9] Deepset. Embeddingmetadataforimprovedretrieval. [20] CangyuanLi,YingWang,ChengLiu,ShengwenLiang,
https://haystack.deepset.ai/tutorials/39_e HuaweiLi,andXiaoweiLi. Glist:Towardsin-storage
mbedding_metadata_for_improved_retrieval, graph learning. In 2021 USENIX Annual Technical
| 2024. |     |     |     |     |     |     | Conference(USENIXATC21),pages225–238,2021. |     |     |     |     |     |     |
| ----- | --- | --- | --- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- | --- |
[10] Jianbo Dong,Hao Qi,Tianjing Xu,Xiaoli Liu,Chen [21] Haoyu Li, Sheng Jiang, Chen Chen, Ashwini Raina,
Wei,RongyaoWang,XiaoyiLu,ZhengCao,YunfeiDu, XingyuZhu,ChangxuLuo,andAsafCidon. Rubbledb:
andFuBinZhang. Kspeed:Beatingi/obottlenecksof Cpu-efficientreplicationwithnvme-of.In2023USENIX
USENIX Association 23rd USENIX Conference on File and Storage Technologies    233

AnnualTechnicalConference(USENIXATC23),pages [31] NVIDIA. Gpudirectstorageparameters. https://do
| 689–703,2023. |     |     |     | cs.nvidia.com/gpudirect-storage/configura |     |     |     |
| ------------- | --- | --- | --- | ----------------------------------------- | --- | --- | --- |
tion-guide/topics/gds-parameters.html.
[22] ChangyueLiao,MoSun,ZihanYang,KaiqiChen,Bin-
hangYuan,FeiWu,andZekeWang. Addingnvmessds [32] Nvidia. Unifiedmemoryforcudabeginners. https:
to enable andaccelerate 100bmodelfine-tuning on a //developer.nvidia.com/blog/unified-memor
y-cuda-beginners,2017.
| singlegpu. | arXivpreprintarXiv:2403.06504,2024. |     |     |     |     |     |     |
| ---------- | ----------------------------------- | --- | --- | --- | --- | --- | --- |
[23] ErikLindholm,JohnNickolls,StuartOberman,andJohn [33] Nvidia. Nvidiaa100tensorcoregpuarchitecture. http
Montrym. Nvidiatesla:Aunifiedgraphicsandcomput- s://images.nvidia.com/aem-dam/en-zz/Soluti
ons/data-center/nvidia-ampere-architectur
| ingarchitecture. | IEEEmicro,28(2):39–55,2008. |     |     |     |     |     |     |
| ---------------- | --------------------------- | --- | --- | --- | --- | --- | --- |
e-whitepaper.pdf,2020.
[24] ZichangLiu,JueWang,TriDao,TianyiZhou,Binhang
|           |                |                |        | [34] Nvidia. | Nvidiaamperega102gpuarchitecture. |     | https: |
| --------- | -------------- | -------------- | ------ | ------------ | --------------------------------- | --- | ------ |
| Yuan,Zhao | Song,Anshumali | Shrivastava,Ce | Zhang, |              |                                   |     |        |
//www.nvidia.com/content/PDF/nvidia-amper
| YuandongTian,ChristopherRe,andBeidiChen. |     |     | Deja |     |     |     |     |
| ---------------------------------------- | --- | --- | ---- | --- | --- | --- | --- |
vu:ContextualsparsityforefficientLLMsatinference e-ga-102-gpu-architecture-whitepaper-v2.pd
f,2020.
| time. InAndreasKrause,EmmaBrunskill,Kyunghyun |     |     |     |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
Cho,BarbaraEngelhardt,SivanSabato,andJonathan
|     |     |     |     | [35] Nvidia. | Nvidiagpudirectstorage. | https://docs.nvi |     |
| --- | --- | --- | --- | ------------ | ----------------------- | ---------------- | --- |
Scarlett,editors,Proceedingsofthe40thInternational
dia.com/gpudirect-storage/index.html,2024.
ConferenceonMachineLearning,volume202ofPro-
ceedingsofMachineLearningResearch,pages22137–
|     |     |     |     | [36] Jeongmin | Brian | Park, Kun Wu, Vikram | Sharma |
| --- | --- | --- | --- | ------------- | ----- | -------------------- | ------ |
22176.PMLR,23–29Jul2023. Mailthody,Zaid Quresh,Scott Mahlke,and Wen-mei
|     |     |     |     | Hwu. | Lsm-gnn:Large-scalestorage-basedmulti-gpu |     |     |
| --- | --- | --- | --- | ---- | ----------------------------------------- | --- | --- |
[25] PakMarkthub,MehmetEBelviranli,SeyongLee,Jef-
|                                 |     |                 |     | gnntrainingbyoptimizingdatatransferscheme. |     |     | arXiv |
| ------------------------------- | --- | --------------- | --- | ------------------------------------------ | --- | --- | ----- |
| freySVetter,andSatoshiMatsuoka. |     | Dragon:breaking |     |                                            |     |     |       |
preprintarXiv:2407.15264,2024.
| gpumemorycapacitylimitswithdirectnvmaccess. |     |     | In  |     |     |     |     |
| ------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
SC18:InternationalConferenceforHighPerformance https://pytorch.
|     |     |     |     | [37] Pytorch. | Pytorchdocumentation. |     |     |
| --- | --- | --- | --- | ------------- | --------------------- | --- | --- |
Computing,Networking,Storage and Analysis,pages org/docs/stable/data.html#torch.utils.data
| 414–426.IEEE,2018. |                  |              |       | .DataLoader. |     |     |     |
| ------------------ | ---------------- | ------------ | ----- | ------------ | --- | --- | --- |
| [26] Avantika      | Mathur, Mingming | Cao, Suparna | Bhat- |              |     |     |     |
[38] RuoyuQin,ZhemingLi,WeiranHe,MingxingZhang,
tacharya, Andreas Dilger, Alex Tomas, and Laurent YongweiWu,WeiminZheng,andXinranXu. Moon-
Vivier. The new ext4 filesystem: current status and cake:Kimi’skvcache-centricarchitectureforllmserv-
futureplans. InProceedingsoftheLinuxsymposium, ing. arXivpreprintarXiv:2407.00079,2024.
volume2,pages21–33.Citeseer,2007.
[39] ZaidQureshi,VikramSharmaMailthody,IsaacGelado,
[27] YANGTZEMEMORY. Tipro7000nvmessd. https: Seungwon Min, Amna Masood, Jeongmin Park, Jin-
//www.ymtc.com/cn/products/34.html?cat=44/. junXiong,ChrisJNewburn,DmitriVainbrand,I-Hsin
|     |     |     |     | Chung,etal. | Gpu-initiatedon-demandhigh-throughput |     |     |
| --- | --- | --- | --- | ----------- | ------------------------------------- | --- | --- |
[28] ChangwooMin,WoonhakKang,MohanKumar,Sanid- storageaccessinthebamsystemarchitecture. InPro-
hyaKashyap,SteffenMaass,HeeseungJo,andTaesoo
ceedingsofthe28thACMInternationalConferenceon
Kim. Solros:adata-centricoperatingsystemarchitec- ArchitecturalSupportforProgrammingLanguagesand
| tureforheterogeneouscomputing. |     | InProceedingsof |     |     |     |     |     |
| ------------------------------ | --- | --------------- | --- | --- | --- | --- | --- |
OperatingSystems,Volume2,pages325–339,2023.
theThirteenthEuroSysConference,pages1–15,2018.
|     |     |     |     | [40] Samyam | Rajbhandari, | Olatunji Ruwase, | Jeff Rasley, |
| --- | --- | --- | --- | ----------- | ------------ | ---------------- | ------------ |
[29] Seungwon Min, Vikram Sharma Mailthody, Zaid ShadenSmith,andYuxiongHe. Zero-infinity:Breaking
Qureshi,JinjunXiong,EimanEbrahimi,andWen-Mei
thegpumemorywallforextremescaledeeplearning.In
Hwu. EMOGI: efficient memory-access for out-of- Proceedingsoftheinternationalconferenceforhighper-
memorygraph-traversalingpus. Proc.VLDBEndow., formancecomputing,networking,storageandanalysis,
| 14(2):114–127,2020. |     |     |     | pages1–14,2021. |     |     |     |
| ------------------- | --- | --- | --- | --------------- | --- | --- | --- |
[30] FupingNiu,JianhuiYue,JiangqiuShen,XiaofeiLiao, [41] Zhenyuan Ruan, Tong He, and Jason Cong. Insider:
and Hai Jin. Flashgnn: An in-ssd accelerator for Designingin-storagecomputingsystemforemerging
gnntraining. In2024IEEEInternationalSymposium high-performancedrive. In2019USENIXAnnualTech-
onHigh-PerformanceComputerArchitecture(HPCA), nical Conference (USENIX ATC 19),pages 379–394,
| pages361–378.IEEE,2024. |     |     |     | 2019. |     |     |     |
| ----------------------- | --- | --- | --- | ----- | --- | --- | --- |
234    23rd USENIX Conference on File and Storage Technologies USENIX Association

[42] SagiShahar,ShaiBergman,andMarkSilberstein. Ac- [52] QinlongWang,TingfengLan,YinghaoTang,BoSang,
tivepointers:acaseforsoftwareaddresstranslationon ZilingHuang,YihengDu,HaitaoZhang,JianSha,Hui
gpus. ACM SIGARCH Computer Architecture News, Lu,Yuanchun Zhou,et al. Dlrover-rm: Resource op-
44(3):596–608,2016. timization for deep recommendation models training
|     |     |     |     |     |     |     | in  | the cloud. | Proceedings |     | of the VLDB |     | Endowment, |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ----------- | --- | ----------- | --- | ---------- |
[43] YingSheng,LianminZheng,BinhangYuan,Zhuohan 17(12):4130–4144,2024.
| Li,Max | Ryabinin,Beidi |     | Chen,Percy |     | Liang,Christo- |     |     |     |     |     |     |     |     |
| ------ | -------------- | --- | ---------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
pher Re, Ion Stoica, and Ce Zhang. FlexGen: High- [53] Yuyue Wang, Xiurui Pan, Yuda An, Jie Zhang, and
|     |     |     |     |     |     |     | Glenn | Reinman. |     | Beacongnn: | Large-scale |     | gnn accel- |
| --- | --- | --- | --- | --- | --- | --- | ----- | -------- | --- | ---------- | ----------- | --- | ---------- |
throughputgenerativeinferenceoflargelanguagemod-
els with a single GPU. In Andreas Krause, Emma erationwithout-of-orderstreamingin-storagecomput-
|     |     |     |     |     |     |     | ing. | In2024IEEEInternationalSymposiumonHigh- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --------------------------------------- | --- | --- | --- | --- | --- |
Brunskill,KyunghyunCho,BarbaraEngelhardt,Sivan
Sabato,andJonathanScarlett,editors,Proceedingsof Performance Computer Architecture (HPCA), pages
the40thInternationalConferenceonMachineLearn- 330–344.IEEE,2024.
ing,volume202ofProceedingsofMachineLearning
|     |     |     |     |     |     |     | [54] NVMExpressWorkgroup. |     |     |     | Nvmexpressbasespecifica- |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | ------------------------ | --- | --- |
Research,pages31094–31116.PMLR,23–29Jul2023.
|     |     |     |     |     |     |     | tionrevision2.0c. |     |     | https://nvmexpress.org/wp-c |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --------------------------- | --- | --- | --- |
ontent/uploads/NVM-Express-Base-Specifica
[44] MarkSilberstein,BryanFord,IditKeidar,andEmmett
tion-2.0c-2022.10.04-Ratified.pdf,2022.
| Witchel. | Gpufs: | Integrating |     | a file | system | with gpus. |     |     |     |     |     |     |     |
| -------- | ------ | ----------- | --- | ------ | ------ | ---------- | --- | --- | --- | --- | --- | --- | --- |
ACMTrans.Comput.Syst.,32(1):1:1–1:31,2014.
|     |     |     |     |     |     |     | [55] Kun | Wu,Jeongmin |     | Brian | Park,Xiaofan | Zhang,Mert |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | --- | ----- | ------------ | ---------- | --- |
Hidayetog˘lu,VikramSharmaMailthody,SitaoHuang,
| [45] Mark Silberstein, |     | Bryan | Ford, | and | Emmett | Witchel. |                                 |     |     |     |     |     |            |
| ---------------------- | --- | ----- | ----- | --- | ------ | -------- | ------------------------------- | --- | --- | --- | --- | --- | ---------- |
|                        |     |       |       |     |        |          | StevenSamLumetta,andWen-meiHwu. |     |     |     |     |     | Tba:Faster |
Gpufs:Thecaseforoperatingsystemservicesongpus.
largelanguagemodeltrainingusingssd-basedactivation
CommunicationsoftheACM,57(12):68–79,2014.
|     |     |     |     |     |     |     | offloading. |     | arXivpreprintarXiv:2408.10013,2024. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ----------------------------------- | --- | --- | --- | --- |
[46] MarkSilberstein,SangmanKim,SeongguHuh,Xinya
|        |          |      |        |     |        |          | [56] ChunhuaXiao,ShiQiu,andDandanXu. |     |     |     |     | Pasm:Paral- |     |
| ------ | -------- | ---- | ------ | --- | ------ | -------- | ------------------------------------ | --- | --- | --- | --- | ----------- | --- |
| Zhang, | Yige Hu, | Amir | Wated, | and | Emmett | Witchel. |                                      |     |     |     |     |             |     |
lelismawarespacemanagementstrategyforhybridssd
| Gpunet:          | Networking |     | abstractions |     | for gpu | programs. |                                           |     |     |     |     |     |           |
| ---------------- | ---------- | --- | ------------ | --- | ------- | --------- | ----------------------------------------- | --- | --- | --- | --- | --- | --------- |
|                  |            |     |              |     |         |           | towardsin-storagednntrainingacceleration. |     |     |     |     |     | Journalof |
| ACM Transactions |            |     | on Computer  |     | Systems | (TOCS),   |                                           |     |     |     |     |     |           |
SystemsArchitecture,128:102565,2022.
34(3):1–31,2016.
[57] ZiyeYang,JamesRHarris,BenjaminWalker,Daniel
| [47] SPDK. | Blobfs. | https://spdk.io/doc/blobfs.htm |     |     |     |     |                   |     |     |            |     |            |      |
| ---------- | ------- | ------------------------------ | --- | --- | --- | --- | ----------------- | --- | --- | ---------- | --- | ---------- | ---- |
|            |         |                                |     |     |     |     | Verkamp,Changpeng |     |     | Liu,Cunyin |     | Chang,Gang | Cao, |
l.
|                 |                     |     |     |     |                |     | JonathanStern,VishalVerma,andLuseEPaul. |             |                                     |                         |     |     | Spdk:   |
| --------------- | ------------------- | --- | --- | --- | -------------- | --- | --------------------------------------- | ----------- | ----------------------------------- | ----------------------- | --- | --- | ------- |
|                 |                     |     |     |     |                |     | A                                       | development | kit                                 | to buildhighperformance |     |     | storage |
| [48] Techpower. | Nvidiaa100pcie80gb. |     |     |     | https://www.te |     |                                         |             |                                     |                         |     |     |         |
|                 |                     |     |     |     |                |     | applications.                           |             | In2017IEEEInternationalConferenceon |                         |     |     |         |
chpowerup.com/gpu-specs/a100-pcie-80-gb.c3
CloudComputingTechnologyandScience(CloudCom),
821,2021.
pages154–161.IEEE,2017.
[49] HugoTouvron,ThibautLavril,GautierIzacard,Xavier
|     |     |     |     |     |     |     | [58] Susan | Zhang, | Stephen | Roller, | Naman | Goyal, | Mikel |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------ | ------- | ------- | ----- | ------ | ----- |
Martinet,Marie-AnneLachaux,TimothéeLacroix,Bap- Artetxe,Moya Chen,Shuohui Chen,Christopher De-
tisteRozière,NamanGoyal,EricHambro,FaisalAzhar,
|                                                |     |     |     |     |     |     | wan,MonaDiab,XianLi,XiVictoriaLin,etal.   |     |     |     |     |     | Opt:  |
| ---------------------------------------------- | --- | --- | --- | --- | --- | --- | ----------------------------------------- | --- | --- | --- | --- | --- | ----- |
| etal. Llama:Openandefficientfoundationlanguage |     |     |     |     |     |     |                                           |     |     |     |     |     |       |
|                                                |     |     |     |     |     |     | Openpre-trainedtransformerlanguagemodels. |     |     |     |     |     | arXiv |
models. arXivpreprintarXiv:2302.13971,2023. preprintarXiv:2205.01068,2022.
[50] JánVesely`,ArkapravaBasu,AbhishekBhattacharjee,
[59] YimingZhang,LiWang,ShengyunLiu,ShunGai,Hao-
GabrielHLoh,MarkOskin,andStevenKReinhardt. nan Wang,Xin Yao,MeilingWang,Kai Chen,Dong-
Genericsystemcallsforgpus. In2018ACM/IEEE45th shengLi,andJiwuShu. Cheetah:Metadataaggregation
AnnualInternationalSymposiumonComputerArchitec-
|                                    |     |     |     |     |     |     | forfastobjectstoragewithoutdistributedordering. |     |     |     |     |     | In  |
| ---------------------------------- | --- | --- | --- | --- | --- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
| ture(ISCA),pages843–856.IEEE,2018. |     |     |     |     |     |     | ACMEuroSys2025,2025.                            |     |     |     |     |     |     |
[51] Devavret Makkar Vukasin Milovanovic and Gregory [60] Shawn Zhong, Chenhao Ye, Guanzhou Hu, Suyan
Kimball.Boostingdataingestthroughputwithgpudirect Qu,Andrea Arpaci-Dusseau,Remzi Arpaci-Dusseau,
storageandrapidscudf. https://developer.nvidia and Michael Swift. Madfs:per-file virtualization for
.com/zh-cn/blog/boosting-data-ingest-throu userspace persistent memory filesystems. In 21st
ghput-with-gpudirect-storage-and-rapids-c USENIXConferenceonFileandStorageTechnologies
| udf/,2022. |     |     |     |     |     |     | (FAST23),pages265–280,2023. |     |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | --- | --- | --- |
USENIX Association 23rd USENIX Conference on File and Storage Technologies    235

[61] TianleZhong,JiechenZhao,XindiGuo,QiangSu,and
| GeoffreyFox.   | Optimizingdatai/oforllmdatasetson |     |
| -------------- | --------------------------------- | --- |
| remotestorage. | 2024.                             |     |
[62] YuhongZhong,HaoyuLi,YuJianWu,IoannisZarkadas,
JeffreyTao,EvanMesterhazy,MichaelMakris,Junfeng
| Yang,Amy                  | Tai,Ryan Stutsman,et | al. Xrp:in-kernel |
| ------------------------- | -------------------- | ----------------- |
| storagefunctionswithebpf. | In16thUSENIXSympo-   |                   |
siumonOperatingSystemsDesignandImplementation
(OSDI22),pages375–393,2022.
236    23rd USENIX Conference on File and Storage Technologies USENIX Association