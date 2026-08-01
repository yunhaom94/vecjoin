# Epic Massively Parallel Multi Versioned Transaction Processing

**Source**: Epic Massively Parallel Multi Versioned Transaction Processing.pdf
**Format**: .pdf

---

Massively Parallel Multi-Versioned
Transaction Processing
Shujian Qian and Ashvin Goel, University of Toronto
https://www.usenix.org/conference/osdi24/presentation/qian
This paper is included in the Proceedings of the
18th USENIX Symposium on Operating Systems
Design and Implementation.
July 10–12, 2024 • Santa Clara, CA, USA
978-1-939133-40-3
Open access to the Proceedings of the
18th USENIX Symposium on Operating
Systems Design and Implementation
is sponsored by

Massively Parallel Multi-Versioned Transaction Processing
ShujianQian AshvinGoel
UniversityofToronto UniversityofToronto
Abstract However,currentmulti-versiondesignshaveseveraldraw-
Multi-versionconcurrencycontrolcanavoidmostread-write backs,includingincreasedoverheadsduringtransactionpro-
conflictsinOLTPworkloads.However,multi-versionedsys- cessing,datastorage,allocationandgarbagecollection.These
temsoftenhavehighercomplexityandoverheadscompared designsstorerecordversionsinlinkedlists,introducingan
to single-versioned systems due to the need for allocating, additional layer of indirection and necessitating list traver-
searching and garbage collecting versions. Consequently, saltolocatetheappropriateversion.Accessingtheversions
single-versionedsystemscanoftendramaticallyoutperform resultsinalargerworkingset,leadingtohighercachemiss
multi-versionedsystems. rates and performance degradation. Multiple versions also
We introduce Epic,the firstmulti-versionedGPU-based leadtohighermemoryrequirements.Toreducethememory
deterministicOLTPdatabase.Epicutilizesabatchedexecu- footprint,versions are frequently garbage collected,which
tionscheme,performingconcurrencycontrolinitializationfor incurs additional overheads. As a result, a previous study
abatchoftransactionsbeforeexecutingthetransactionsde- thatcomparedcarefullytuned,state-of-the-artmulti-version
terministically.Byleveragingthepredeterminedorderingof andsingle-versionsystemsdemonstratedthatunderlowcon-
transactions,Epiceliminatesversionsearchentirelyandsig- tention,amulti-versionsystemhasroughlyhalf thethrough-
nificantlyreducesversionallocationandgarbagecollection putofsingle-versionsystems[14].
overheads. Ourapproach utilizes the computational power Current multi-version designs allocate versions dynami-
of the GPU architecture to accelerate Epic’s concurrency callybecausetransactionsmaywriteandthuscreateversions
controlinitializationandefficientlyparallelizebatchedtrans- atanytime.Thus,versionsarestoredinlinkedlists,readsre-
actionexecution,whileensuringlowlatency.Ourevaluation quiresearchingforversions,andgarbagecollectingversions
demonstratesthatEpicachievescomparableperformanceun- haspoorlocalityandrequiresexpensivesynchronization.
derlowcontentionandconsistentlyhigherperformanceunder Ourkeyinsightisthatdeterministicdatabasesemploying
mediumtohighcontentionversusstate-of-the-artsingleand transactionbatchingandknowntransactionread-writesets
multi-versionedsystems. canavoidmostofthesemulti-versioningcosts,thusenabling
goodperformanceforallworkloads.Thetransactionbatching
andknownread-writesetsrequirementsarecommonlymet
1 Introduction
bymostdeterministicdatabases[11,12,18,19,26,28,31,35].
Therehasbeenagrowingneedforhigh-throughputonline WeintroduceEpic,thefirstmulti-versioned,GPU-based
transaction processing (OLTP) systems capable of execut- deterministictransaction-processingdatabase.Epicbatches
ingtensofthousandsoftransactionspersecond.In-memory transactionsintoepochsandestablishesaserialorderingof
databasesystems,specificallydesignedforworkloadswith transactionswithinabatchbeforetransactionexecution,simi-
datasetsthatfitentirelyinDRAMmemoryandprovidedura- lartootherdeterministicdatabases.
bilityandhighavailabilityvialoggingandreplication,have Transaction batching enables splitting an epoch into an
beendevelopedtoaddressthisdemand.Althoughthesesys- initializationphaseduringwhichconcurrencycontroloper-
temsofferconsiderableperformanceadvantagesovertradi- ationsareinitializedusingtheread-writesets,followedby
tionaldisk-basedsystems,theysufferundercontention,lead- anexecutionphaseduringwhichtransactionsareexecuted
ingtolowperformanceandlimitedscalabilityacrosscores. concurrently and synchronized to ensure the deterministic
Multi-versioningoffersapromisingsolutionforcontended ordering.Duringtheinitializationphase,Epicallocatesver-
andread-heavyworkloads.Multi-versionsystemsmaintain sionsbasedonthewriteset.Theseallocationoperationsare
recentpastversionsofeachrecord,enablingconcurrentreads performedefficientlybecausetheydonotinterferewithtrans-
and writes to the same record; reads do not block writes actionexecution.Inaddition,Epiccalculatestheversionlo-
because writes can safely create new versions while reads cationofeachread/writeoperationbasedontheorderingof
are accessing the old versions. Consequently, transactions transactions and the known read-write sets. This approach
canbeserializedinwaysunattainableinsingle-versionde- enables transactions to access versions directly during the
signs,thereby enabling greater parallelism. Previous work executionphase,withoutrequiringanyversionsearch.
hasshownthatmulti-versionsystemscanoutperformsingle- Epic’sepoch-baseddesignenablesefficientgarbagecollec-
versionsystemsunderhighcontention[17]. tionaswell.Sincetransactionsinthenextepochareserialized
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation 765

afteralltransactionsinthecurrentepoch,onlythefinalwrite Wuetal.conductadetailedstudyofthecostsassociated
to a record is visible to the transactions in the next epoch. with concurrency control, version storage, garbage collec-
Thusallversionsexceptthelastonebecomeobsoletewhen tion,andindexmanagementinvariousin-memoryMVCC
anepochends.Epicstoresallintermediaterecordversions schemes [37]. Cicada [17] outperforms previous MVCC
separatelyfromthelastversionandreclaimsthemefficiently schemes with several optimizations, including optimistic
attheendofanepoch. multi-versioning,contentionregulation,versioninlining,and
The challenge is that Epic’s initialization phase is ex- rapidgarbagecollection.However,astudycomparingstate-
pensive,requiringbothsignificantcomputationandmemory of-theartmulti-versionandsingle-versionsystemsshowed
bandwidth.Fortunately,Epic’sinitializationphaseishighly thatwhileMVCCoutperformsOCCunderhighcontention,
parallelizable. With the rapid commoditization of general- itsthroughputissignificantlylowerunderlowcontention[14].
purpose GPU computing, Epic harnesses the thread paral- Epicaimstominimizemulti-versioningcostsassociatedwith
lelismofferedbymodernGPUarchitecturestosignificantly versionstorage,lookupandgarbagecollection.
acceleratetheinitializationphase.
ModernGPUsarewellsuitedforEpic’sexecutionphaseas
2.2 DeterministicDatabaseSystems
wellbecausetheyofferhigh-bandwidthmemoryformemory-
boundworkloads. In addition,theyperform zero-overhead Deterministicdatabaseshavegainedincreasingattentionin
contextswitchingbetweenthreadcontexts,whichallowshid- recentyears,drivenbytheneedforefficientreplicationand
ingmemoryaccesslatency.Theseadvantageshelptocounter improvedscalabilityfordistributedtransactions[35].These
theincreasedmemoryfootprintandlowercacheutilization systems execute transactions deterministically by ensuring
commonly associated with multi-version systems. Conse- that the serial ordering of operations remains consistent
quently,Epicachieveshighthroughputandensureslowtrans- across different runs. Determinism enables efficient repli-
actionlatencyevenwithitsepoch-basedexecutionscheme. cation[27,31,33]andlivemigration[18,19]sinceallrepli-
WhileGPUtransactionexecutionperformswell,itislim- casexecutetransactionsindependentlywithoutcoordination.
itedbydatasetsthatfitinGPUmemory.Thus,Epicalsosup- Furthermore,deterministicsystemsreducetheneedfortwo-
portslargerdatasetswithaCPUexecutionmodelinwhich phasecommit,helpingscaletheperformanceofdistributed
theinitializationphaserunsontheGPUwhiletheexecution transactions[35]. Theycanalsoeffectivelyhandleskewed
phaserunsontheCPU. andcontendedaccesses,e.g.,ordersforpopularitems[28].
TodemonstratetheeffectivenessofEpic’sdesign,wecon- Deterministic systems typically batch transactions into
ductextensiveevaluationusingtheTPC-CandYCSBbench- epochstoperformdeterministicconcurrencycontrolbefore
marks andshowthatEpicsignificantlyoutperforms recent execution[11,12,28,35].Thusthesesystemrequiretheread
single-andmulti-versionsystemsonmostworkloads. andwritesetsoftransactionstobeknownbeforeexecution.
Whentheyarenotfullyknown,theycanbedeterminedus-
ingreconnaissancequeries[35].Calvin[35]andPWV[12]
2 Background
aresingleversioned,whileBohm[11]andCaracal[28]uti-
lizeMVCC.Calvinusesacentralizedlockmanager,while
This work builds on a rich body of research on multi-
PWVemploysamore-scalableper-coredependencyanalysis
version concurrency control, deterministic databases, and
forconcurrencycontrol.BohmandCaracalallocateversions
GPU-acceleratedcomputation,asdiscussedbelow.
scalablyduringtheconcurrencycontrolinitializationphase,
butBohmperformspartitionedinitialization,whileCaracal
2.1 Multi-versionedConcurrencyControl performssharedmemoryinitialization.Bohmpartitionsthe
recordsinatableacrosscores.Duringtheinitializationphase,
Multi-versionconcurrencycontrol(MVCC)hasalonghis- allpartitionsanalyzeeachtransaction’swritesetandinsert
tory[29,30],withearlyworkevaluatingitsperformance[8], placeholderversionsinalinkedlistfortherecordstheyown.
ensuringsnapshotisolation[5],providingserializablesnap- Duringexecution,areadoperationtraversesthelisttofind
shotisolation[7],usingdynamictimestampassignment[20] thecorrectversionbasedonitstotalorderID.Then,itsyn-
andenablingefficientindexing[32],fordisk-baseddatabases. chronizeswithawriteoperationthatfillsthecorresponding
With the advent of machines equipped with high core placeholderversion.Caracalusesshared-memoryinitializa-
countsandterabytesofDRAMmemory,muchworkhasfo- tion,whichenablesbetterhandlingofskewedworkloads.It
cusedon in-memorydatabase designs,andseveralMVCC scalesversionallocationforcontendedrecordsbybatching
schemesoptimizedforthemhavebeenproposed[15,16,22]. the allocations. Itstores versions as sortedarrays anduses
MVCC schemes are popular because they provide robust binarysearchtoreduceversionlookupcostsduringexecu-
performance under a wide range of workloads. As a re- tion.Epicperformsshared-memoryinitializationsimilarto
sult, many commercial in-memory databases implement Caracal.However,Epicavoidsanyversionlookupcostsand
MVCC[10,24,25,34]. minimizesversionstorageandgarbagecollectionoverheads.
766 18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

2.3 GPUAcceleratedOLTPDatabases
batch
| General-Purpose | computing |     | on Graphics |     | Processing | Units | CPU |     |     |     |     |     |     |
| --------------- | --------- | --- | ----------- | --- | ---------- | ----- | --- | --- | --- | --- | --- | --- | --- |
txn param
| (GPGPU)hasbecomepopularwiththerapidcommoditization |     |     |     |     |     |     | GPU |       |             |                |           |     |           |
| -------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----- | ----------- | -------------- | --------- | --- | --------- |
|                                                    |     |     |     |     |     |     |     | index | indexed txn | initialization | exec plan |     | execution |
ofGPUs,theadventofuser-friendlyprogrammingmodels
andframeworkslikeCUDAandOpenCL,andthegrowing
demandforhigh-performancecomputingonlargedatasets. (a)GPUExecutionModel
| Modern GPUs                                           | contain | an array | of       | streaming | multiproces- |          |       |     |     |     |     |     |           |
| ----------------------------------------------------- | ------- | -------- | -------- | --------- | ------------ | -------- | ----- | --- | --- | --- | --- | --- | --------- |
|                                                       |         |          |          |           |              |          | batch |     |     |     |     |     | execution |
| sors (SMs),each                                       | of      | which    | contains | many      | CUDA         | cores or |       |     |     |     |     |     |           |
| streamprocessors,allowingexecutionofthousandsofactive |         |          |          |           |              |          | CPU   |     |     |     |     |     |           |
txn param
GPU
threadsconcurrently.GPUsusestheSingleProgram,Multiple
|     |     |     |     |     |     |     |     | index | indexed txn | initialization | exec plan |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ----------- | -------------- | --------- | --- | --- |
Data(SPMD)parallelprogrammingmodelinwhichmultiple
(b)CPUExecutionModel
threadsexecutethesameprogramondifferentdataelements.
| GPU-baseddatabases |     | are | an active | area | ofresearch,but |     |     |     |     |     |     |     |     |
| ------------------ | --- | --- | --------- | ---- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Figure1:EpicArchitecture
| most work | has focused | on  | accelerating | Online | Analytical |     |     |     |     |     |     |     |     |
| --------- | ----------- | --- | ------------ | ------ | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
Processing(OLAP)workloadssincetypicalOLAPoperators,
|     |     |     |     |     |     |     | bles during | transaction |     | execution. | The initialization |     | phase |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ----------- | --- | ---------- | ------------------ | --- | ----- |
suchasjoinandsort,areagoodfitforparallelizationusing
performsmulti-versionedconcurrencycontrolandgenerates
theGPU’sSPMDexecutionmodel.
aper-transactionexecutionplan,whichconsistsoftheloca-
GPU-basedtransactionprocessingisrelativelyunexplored
|     |     |     |     |     |     |     | tions ofthe | recordversions |     | thata | transaction | then | directly |
| --- | --- | --- | --- | --- | --- | --- | ----------- | -------------- | --- | ----- | ----------- | ---- | -------- |
becausetransactionalworkloadscompriseshort-livedtrans- accessesduringexecution.
actionswithrandomaccesses,andatomicityandisolationre-
|     |     |     |     |     |     |     | While | indexing | and initialization |     | are always |     | run on the |
| --- | --- | --- | --- | --- | --- | --- | ----- | -------- | ------------------ | --- | ---------- | --- | ---------- |
quiresignificantsynchronization.Theserequirementsmakes
GPU,EpiccanexecutetransactionsontheGPU(Figure1a)
ithardtoexploittheparallelismavailableinGPUs.
|     |     |     |     |     |     |     | orthe CPU | (Figure | 1b). | CPU | execution is | usedto | support |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------- | ---- | --- | ------------ | ------ | ------- |
Previously,twoGPU-basedtransactionprocessingsystems,
|     |     |     |     |     |     |     | databases | largerthan | GPU | memory. | In this | case,the | GPU |
| --- | --- | --- | --- | --- | --- | --- | --------- | ---------- | --- | ------- | ------- | -------- | --- |
GPUTx[13]andGaccO[6],havebeenproposed.Similarto servesasanacceleratorforindexingandinitialization.
| Epic,both | batch transactions |     | and | use epoch-based |     | concur- |     |     |     |     |     |     |     |
| --------- | ------------------ | --- | --- | --------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
Sometimesatransaction’sreadandwritesetsarenotfully
rencycontrolinitializationandexecution.GPUTx,anearly
|            |           |      |           |     |       |          | knownbeforetheindexingphase. |     |     |     | ForexampletheTPC-C |     |     |
| ---------- | --------- | ---- | --------- | --- | ----- | -------- | ---------------------------- | --- | --- | --- | ------------------ | --- | --- |
| attempt at | executing | OLTP | workloads | on  | GPUs, | uses de- |                              |     |     |     |                    |     |     |
order-statustransactionrequiresasecondaryindextolocatea
| pendency tracking | to  | group | transactions | into | sets; | transac- |     |     |     |     |     |     |     |
| ----------------- | --- | ----- | ------------ | ---- | ----- | -------- | --- | --- | --- | --- | --- | --- | --- |
customer’slatestorder.Forthesetransactions,Epicrunsan
tionswithineachsetareconflict-freeandcanexecutewith- optionalread-writesetidentificationphaseontheGPUbefore
outsynchronization.However,wefoundthattheirefficient
theindexingphase.Thetransactioninputstotheidentification
dependencytrackingalgorithm,K-Set,doesnotensurethat
|     |     |     |     |     |     |     | phase only | contain | the | read-write | keys that | are | known at |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------- | --- | ---------- | --------- | --- | -------- |
transactionsinasetareconflict-free,therebyfailingtoguar-
transactiongenerationtime.Thisphaserunsreconnaissance
anteecorrectness.GaccOisadeterministicdatabasethatuses
queries[35]thatusethesepartialtransactioninputstoidentify
single-version,deterministiclocking,similartoCalvin.We
theremainingread-writekeys.
describeGaccoindetailandcompareitwithEpicinSection5.
ThefollowingsectionsdescribeEpic’sstorageschemeand
thenEpic’sinitializationandexecutionphases.
3 Design
3.1 Epicstoragescheme
EpicisaGPU-accelerated,in-memorydeterministicdatabase
that employs a novel multi-versioned concurrency control Epic’sstorageschemeseparatestemporaryversionscreated
protocol. Epic assumes that transactions are one-shot and withinanepochfromversionsthatexistacrossepochs.All
usestoredprocedures,similartootherhigh-performancein- writes to a recordwithin an epoch,exceptthe lastone,are
memorydatabases[36]. only read by other transactions within the epoch. This is
Figure1showstheEpicarchitecture.Epicbatchestransac- becausetransactionsfromalaterepochareserializedafter
tionsintoepochsandsplitseachepochintoindexing,initial- alltransactionsinthecurrentepochandthuscanonlyread
izationandexecutionphases.Thetransactioninputs,consist- thelastversionofeachrecord.Wecalltheversionsthatare
ingofread-setandwrite-setkeysandothertransactiondata, readbytransactionswithinanepochtemporaryversions.The
arebatchedontheCPUandthentransferredtotheGPUfor finalwritetoarecordwithinanepochmaybereadinlater
indexing(shownas“txnparam”inFigure1).Duringindex- epochsandsothislastversionissavedacrossepochs.
ing,thekeysareusedtoretrieveandstorethecorresponding Figure2showsanexampleofEpic’sstorageschemewith
recordIDsinaper-transactiondatastructure(shownas“in- transactionsT1toT8readingandwritingRecord1atEpoch
dexedtxn” in Figure 1). These recordIDs are usedduring 3. Epic places all temporary versions in a scratchpad area.
initializationandusedasindicesforaccessingtherecordta- Duringanepoch,thewritetransactionsonarecord,except
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation    767

|     |     |     |     | Scratchpad Memory |     |     |     | Algorithm1:DeterminingtheprevVerandcurrVer |     |     |     |     |     |
| --- | --- | --- | --- | ----------------- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- |
//Takesthetwotableversionsofarecord
|     | tVersion 1 | eid 3 | V tVersion 2 | eeiidd  23 | VV tVersion 3 | eid 3 | V ... |     |     |     |     |     |     |
| --- | ---------- | ----- | ------------ | ---------- | ------------- | ----- | ----- | --- | --- | --- | --- | --- | --- |
FunctionGetTableVersions(V[2]):
1
eid0←atomicRead(V[0].eid)
2
3 eid1←atomicRead(V[1].eid)
|     |          |          |                   |          |                   |          | write | //current_eidisthecurrentepoch’sID |     |     |     |     |     |
| --- | -------- | -------- | ----------------- | -------- | ----------------- | -------- | ----- | ---------------------------------- | --- | --- | --- | --- | --- |
|     | record 1 | record 1 | record 1 record 1 | record 1 | record 1 record 1 | record 1 |       |                                    |     |     |     |     |     |
txn 1 txn 2 txn 3 txn 4 txn 5 txn 6 txn 7 txn 8 read 4 ifeid0=current_eidthen
|     |     |     |     |     |     |     |     | 5   | prevVer←V[1];currVer←V[0] |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | --- |
6 elseifeid1=current_eidthen
record 1prevVersioneid 2 V currVersion eid 3 V prevVer←V[0];currVer←V[1]
7
else
8
ifeid0>eid1then
9
prevVer←V[0];currVer←V[1]
|     |     |     |     |     |     | ... |     | 10  |      |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
|     |     |     |     |     |     |     |     | 11  | else |     |     |     |     |
record 1record 2record 3record 4record 5
|     |     |     |     |     |     |     |     | 12  | prevVer←V[1];currVer←V[0] |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | --- |
Table
13 return{prevVer,currVer}
Figure2:EpicStorageScheme
3.2 Multi-VersionInitialization
thelastone,filltheseversions,andreadssynchronizewiththe
writestoensureRAWdependenciesaresatisfied.Attheend
Duringtheinitializationphase,Epicusestheorderingoftrans-
ofanepoch,whenallthereadsforthetemporaryversionsare
actionsandtheknowledgeoftheirread-writesetstoallocate
done,thescratchpadisreclaimedandusedinthenextepoch,
versionsforallwritesperformedintheepoch.Toavoidthe
completelyeliminatingper-versiongarbagecollection.
expensiveversionsearchrequiredinpreviousmulti-versioned
Thefinalversionsofeachrecordareplacedinadensetable systems,Epiccalculatestheread-writeversionlocationsfor
areaanddonotrequiregarbagecollection.Thelastwritein
|     |     |     |     |     |     |     |     | each transaction | in the | epoch | before | any transactions | exe- |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | ------ | ----- | ------ | ---------------- | ---- |
anepochtoeachrecordupdatesthevalueinthetabledirectly,
|     |     |     |     |     |     |     |     | cute. These | operations | are parallelizable |     | because | they are |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | ------------------ | --- | ------- | -------- |
leadingtopotentialraceconditionswhentransactionsinthe
performedinaphaseseparatefromtransactionexecution.
| current | epoch | need | to read | data | from | the previous | epoch. |     |     |     |     |     |     |
| ------- | ----- | ---- | ------- | ---- | ---- | ------------ | ------ | --- | --- | --- | --- | --- | --- |
AsshowninAlgorithm2,EpicemploysaparallelGPU-
Epicaddressesthisproblembystoringtwoversionsforeach
|          |     |            |     |          |         |           |        | based algorithm   | to perform | concurrency |     | control    | initializa- |
| -------- | --- | ---------- | --- | -------- | ------- | --------- | ------ | ----------------- | ---------- | ----------- | --- | ---------- | ----------- |
| recordin |     | the table: | the | previous | version | (prevVer) | andthe |                   |            |             |     |            |             |
|          |     |            |     |          |         |           |        | tion efficiently. | Figure     | 3 provides  | an  | example of | this algo-  |
currentversion(currVer),asshowninFigure2.Ineachepoch,
rithm.Theinitializationphasestartsbycollectingalltheread
| prevVer   |     | holds the | data  | from the | previous  | epoch    | (original |                                          |            |       |          |               |           |
| --------- | --- | --------- | ----- | -------- | --------- | -------- | --------- | ---------------------------------------- | ---------- | ----- | -------- | ------------- | --------- |
|           |     |           |       |          |           |          |           | andwriteoperationswithintheepoch(Step1). |            |       |          |               | Eachentry |
| version). |     | The last  | write | (Txn     | 7) within | an epoch | updates   |                                          |            |       |          |               |           |
|           |     |           |       |          |           |          |           | in the all_ops                           | operations | array | contains | the record_id | and       |
currVer toavoidoverwritingtheoriginalversion.Thiswrite thetxn_idassociatedwiththeoperation,theoperation’sin-
isperformeddirectlyonthetable,soalltemporaryversions
|     |           |           |     |         |        |       |               | dex within | the transaction | (op_id), | and | the operation | type |
| --- | --------- | --------- | --- | ------- | ------ | ----- | ------------- | ---------- | --------------- | -------- | --- | ------------- | ---- |
| can | be easily | collected |     | afteran | epoch. | Reads | afterthe last |            |                 |          |     |               |      |
(read/write).Thisoperationisparallelizablebecausetheor-
writetoarecord(Txn8)readfromcurrVer.
derofoperationsdoesnotmatterforthenextstep,whichsorts
ThelocationsofprevVerandcurrVerineachrecorddepend theoperationsarraybyrecord_idandtxn_id(Step2).
ontransactionhistory,astheirpositionsonlychangewhena
Then,Epiccountsthenumberofwriteoperationstoeach
recordiswrittenduringanepoch.Therefore,Epicstoresan recordthatoccurbeforeandaftereachoperation.Sincethe
epochIDineachversion,whichhelpsdistinguishtheversion operationsarealreadygroupedbyrecord_id,theseoperations
frompreviousepochs(prevVer)fromtheversionthatshould
useparallelprefixandpostfixsumbykey(Steps3–4).Next,
beupdatedinthecurrentepoch(currVer).Algorithm1isused GetOpTypeinAlgorithm3calculatestheread-writelocation
| bytransactionstodistinguishbetweenprevVer |     |     |     |     |     |     | andcurrVer. |          |                |       |             |           |        |
| ----------------------------------------- | --- | --- | --- | --- | --- | --- | ----------- | -------- | -------------- | ----- | ----------- | --------- | ------ |
|                                           |     |     |     |     |     |     |             | type for | each operation | (Step | 5). A write | operation | writes |
Inanepoch,beforeanywritehashappenedtocurrVer,Epic tocurrVer forthelastwritetotherecordorelsetotempVer.
ensuresthattheversionwithalargerepochIDcontainsthe A readoperation willreadfrom the version written by the
| moreup-to-datevalueandshouldbeusedasprevVer |     |     |     |     |     |     | (Lines |                         |     |         |                      |     |     |
| ------------------------------------------- | --- | --- | --- | --- | --- | --- | ------ | ----------------------- | --- | ------- | -------------------- | --- | --- |
|                                             |     |     |     |     |     |     |        | previouswriteasfollows: |     | prevVer | ifthereisnopreceding |     |     |
9–12).Duringthelastwrite,thewriterwillupdatetheepoch writepreceding,currVer ifthereisnosucceedingwrite,and
| IDofcurrVer |     | tothecurrentepoch’sID(current_eid),after |     |     |     |     |     |     |     |     |     |     |     |
| ----------- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
tempVer otherwise.
| whichcurrVer |     | willhavealargerepochID,butitisstilldis- |     |     |     |     |     |                    |     |                             |     |     |     |
| ------------ | --- | --------------------------------------- | --- | --- | --- | --- | --- | ------------------ | --- | --------------------------- | --- | --- | --- |
|              |     |                                         |     |     |     |     |     | ThenumberoftempVer |     | variablescreatedinanepochis |     |     |     |
tinguishablesinceitsepochIDmatchesthecurrentepochID equal to the number of tempVer writes. Thus,Epic places
(Lines4–7).TheepochIDisalsousedforsynchronization
|     |     |     |     |     |     |     |     | the tempVer | variables | in the | scratchpad | area in | the same |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --------- | ------ | ---------- | ------- | -------- |
betweenreadsandwrites,asdiscussedlaterinSection3.3. order as the tempVer write operations in the sorted opera-
Therecordtablesandthescratchpadmemoryarestored tionsarray.TocalculatethetempVer locations,Epicperforms
inGPUmemoryfortheGPUexecutionmodelandinCPU aparallelprefixsumoveralloperations,countingtempVer
memoryfortheCPUexecutionmodel. writesbeforeeachoperation(Step6).Withthisinformation,
768    18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Algorithm2:Multi-VersionInitializationPhase 1. Submit the read and write operations write read
FunctionInitialize(txns[NUM_TXN]): record 1record 2record 3record 1record 3record 1record 2record 3record 1record 3
1 txn 1 txn 1 txn 1 txn 2 txn 2 txn 3 txn 3 txn 3 txn 4 txn 4
| all_ops | //allread-writeoperationsintheepoch, |     |     |     |     |     |     |     |     |     |     |     |     |
| ------- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2
//containstuples:{record_id,txn_id,op_id,read_write}
|     |     |     |     |     |     |     | txn 1 |     | txn 2 |     | txn 3 |     | txn 4 |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | ----- | --- | ----- | --- | ----- |
//Alllocalvariablesarearraysofsizeequaltoall_opssize
2. Sort: first by record_id then by txn_id
//Step1:submitoperations
record 1record 1record 1record 1record 2record 2record 3record 3record 3record 3
3 parallelforeachtxn∈txnsdo txn 1 txn 2 txn 3 txn 4 txn 1 txn 3 txn 1 txn 2 txn 3 txn 4
| 4 op_id=0 |     |     |     |     |     |     |     | 3. Segmented Forward Scan (PrefixSumByKey) |     |     |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- |
5 foreachrecord_id∈txn.read_record_idsdo writes writes writes writes writes writes writes writes writes writes
op_id++
6 before before before before before before before before before before
all_ops.pushback({record_id,txn.id,op_id,Read}) 0 0 1 1 0 1 0 0 1 2
7
4. Segmented Backward Scan (PostfixSumByKey)
| 8 foreachrecord_id∈txn.write_record_idsdo |     |     |     |     |     |        |        |        |        |        |               |               |        |
| ----------------------------------------- | --- | --- | --- | --- | --- | ------ | ------ | ------ | ------ | ------ | ------------- | ------------- | ------ |
|                                           |     |     |     |     |     | writes | writes | writes | writes | writes | writes writes | writes writes | writes |
9 op_id++ after after after after after after after after after after
10 all_ops.pushback({record_id,txn.id,op_id,Write}) 2 1 1 0 0 0 2 1 0 0
write read
| //Step2:sortfirstbyrecord_idthenbytxn_id |     |     |     |     |     | 5. Determine Read/Write Type |     |     |     |     |     |     |     |
| ---------------------------------------- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- | --- | --- | --- |
sorted_ops=Sort(all_ops,key={record_id,txn_id})
11 prevVertempVertempVercurrVer currVer currVer prevVertempVercurrVer currVer
//Steps3-4:countwritesbefore/aftereachoponsamerecord
12 writes_before=PrefixSumByKey(sorted_ops,
| 13  |     |     | key=record_id,   |     |     |     |                |              | 6. Full Scan (PrefixSum) |             |                   |               |                   |
| --- | --- | --- | ---------------- | --- | --- | --- | -------------- | ------------ | ------------------------ | ----------- | ----------------- | ------------- | ----------------- |
|     |     |     |                  |     |     | t   | m p W r t m p  | W r t m p W  | r t m p W r              | t m p W r t | m p W r t m p W   | r t m p W r t | m p W r t m p W r |
| 14  |     |     | value=Write?1:0) |     |     |     |                |              |                          |             |                   |               |                   |
|     |     |     |                  |     |     | b   | e fo re b e fo | re b e fo re | b e fo re                | b e fo re b | e fo re b e fo re | b e fo re b   | e fo re b e fo re |
15 writes_after=PostfixSumByKey(sorted_ops,key=record_id, 0 0 1 1 1 1 1 1 2 2
| 16  |     |     | value=Write?1:0) |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
7. Calculate Read/Write Locations
//Step5:getoperationtype,canbe:
//prevVerread,currVerread/write,tempVerread/write
op_types=GetOpType(sorted_ops,writes_before, tempVertempVer tempVer
| 17  |     |               |     |     |     | prevVer |         |         | currVer | currVer currVer | prevVer | currVer | currVer |
| --- | --- | ------------- | --- | --- | --- | ------- | ------- | ------- | ------- | --------------- | ------- | ------- | ------- |
|     |     | writes_after) |     |     |     |         | index 0 | index 0 |         |                 |         | index 1 |         |
18
//Step6:counttempVerwritesbeforeeachopintheepoch
19 tw_before=PrefixSum(op_types,value=tempVerWrite?1:0) 8. Scatter Read/Write locations back to transactions
| //Step7:getread/writelocationforallops |     |     |     |     |     |         |         |         | tempVertempVertempVer |     |         |                 |         |
| -------------------------------------- | --- | --- | --- | --- | --- | ------- | ------- | ------- | --------------------- | --- | ------- | --------------- | ------- |
|                                        |     |     |     |     |     | prevVer | currVer | prevVer |                       |     | currVer | currVer currVer | currVer |
20 rw_loc=GetRWLocation(op_types,tw_before) index 0 index 1 index 0
//Step8:scatterrw_locbacktotransactions txn 1 txn 2 txn 3 txn 4
21 parallelfori=0tosorted_ops.sizedo
txn_id=sorted_ops[i].txn_id Figure3:ExampleofEpic’sInitializationPhase
22
op_id=sorted_ops[i].op_id
23
txns[txn_id].locations[op_id]=rw_loc[i]
| 24  |     |     |     |     |     | directlyusingthelocationinformationcalculatedintheini- |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
tializationphase(lines11–25forreadsandlines26–34for
writes).Atransactionreadwaitsforaversiontobewritten
GetRWLocationinAlgorithm4calculatestheread-writelo-
byanearliertransactionbyspinningontheepochIDofthe
| cations for | all operations | (Step | 7). The | ith tempVer | write |     |     |     |     |     |     |     |     |
| ----------- | -------------- | ----- | ------- | ----------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
versionuntilitmatchesthecurrentepochID(lines21–22).
| updatestheithtempVer |              | inthescratchpadarea.Areadfrom |          |                       |     |                          |       |              |     |               |                          |           |          |
| -------------------- | ------------ | ----------------------------- | -------- | --------------------- | --- | ------------------------ | ----- | ------------ | --- | ------------- | ------------------------ | --------- | -------- |
|                      |              |                               |          |                       |     | However,readsfromprevVer |       |              |     |               | donotneedanysynchroniza- |           |          |
| tempVer reads        | the previous |                               | write in | the sorted operations |     |                          |       |              |     |               |                          |           |          |
|                      |              |                               |          |                       |     | tion                     | since | this version |     | was updatedin |                          | aprevious | epoch. A |
array.Finally,theread-writelocationsarescatteredbackto
transactionwritestothedataoftheversionbeforeupdating
eachtransactiontobeusedintheexecutionphase(Step8).
theversion’sepochID(lines32–34).TheGPUweakmemory
consistencymodelrequiresamemoryfencebetweenthedata
3.3 TransactionExecution writeandtheepochIDupdatetoensurethatthedataisvisible
tootherthreadsbeforetheupdatedversion.
Epic’sexecutionphaseisconsiderablysimplerthantheinitial-
|     |     |     |     |     |     | CPU-sideExecution |     |     |     | Epiccanalsoexecutetransactions |     |     |     |
| --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | ------------------------------ | --- | --- | --- |
izationphase.Atransactionaccessesversionsdirectlyusing
ontheCPU,whichisparticularlyusefulwhenthedatabase
thelocationscalculatedduringinitialization,eliminatingany
sizeexceedsGPUmemorycapacity.Inthiscase,Epictrans-
| version lookup | during | execution. | Due | to multi-versioning, |     |     |     |     |     |     |     |     |     |
| -------------- | ------ | ---------- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ferstheoutputofindexing(readandwriterecordIDs)and
write-after-read(WAR)andwrite-after-write(WAW)depen-
theinitializationphase(read-writelocations)totheCPU,as
| dencies do | not require | explicit | coordination. | Epic | uses the |       |     |        |             |     |           |          |          |
| ---------- | ----------- | -------- | ------------- | ---- | -------- | ----- | --- | ------ | ----------- | --- | --------- | -------- | -------- |
|            |             |          |               |      |          | shown | in  | Figure | 1. CPU-side |     | execution | utilizes | the same |
epochIDassociatedwitheachversiontosynchronizeread-
synchronizationmechanismasGPUexecution.
after-write(RAW)dependenciesbetweentransactions.
Algorithm5showsEpic’stransactionexecutionphase.The HandlingInsertsandDeletes Epictreatsrecordinsertions
transactionsinanepocharescheduledintheirpredetermined anddeletionsthesamewayasupdates.Bothinsertanddelete
serialorderasthreadresourcesbecomeavailable,asexplained operations are considered write operations, so they create
further in Section 4.4. The RunTxn function shows an ex- anewversionoftherecord,similartoanupdate. Foreach
ampleofatransaction.Thetransactionaccessestheversions version,Epic uses a valid flag to mark whetherit contains
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation    769

Algorithm3:CalculateRead/WriteType Algorithm5:TransactionExecutionPhase
FunctionGetOpType(sorted_ops,writes_before,writes_after): FunctionExecute(txns[NUM_TXN]):
| 1   |     |     |     | 1   |
| --- | --- | --- | --- | --- |
op_types[sorted_ops.size] //typeofoperations parallelfori=0totxns.sizedo
| 2   |     |     |     | 2   |
| --- | --- | --- | --- | --- |
parallelfori=0tosorted_ops.sizedo RunTxn(txns[i])
| 3   |                                       |     |     | 3   |
| --- | ------------------------------------- | --- | --- | --- |
| 4   | ifsorted_ops[i].read_write==Writethen |     |     |     |
| 5   | ifwrites_after[i]==0then              |     |     |     |
4 FunctionRunTxn(txn):
6 op_types[i]=currVerWrite value1=ReadFromTable(txn.record_id1,txn.read_loc1)
5
| 7   | else |     |     | value2=ReadFromTable(txn.record_id2,txn.read_loc2) |
| --- | ---- | --- | --- | -------------------------------------------------- |
6
| 8   | op_types[i]=tempVerWrite |     |     | //performtransactionlogic |
| --- | ------------------------ | --- | --- | ------------------------- |
ifvalue1isNoneorvalue2isNonethen
| 9   | else//readoperation       |     |     | 7         |
| --- | ------------------------- | --- | --- | --------- |
|     | ifwrites_before[i]==0then |     |     | 8 abort() |
10
op_types[i]=prevVerRead
| 11  |     |     |     | 9 result=SomeOperation(value1,value2) |
| --- | --- | --- | --- | ------------------------------------- |
elseifwrites_after[i]==0then
| 12  |                         |     |     | //noabortscanhappenbeyondthispoint |
| --- | ----------------------- | --- | --- | ---------------------------------- |
| 13  | op_types[i]=currVerRead |     |     |                                    |
10 WriteToTable(txn.result_record_id,txn.write_loc,result)
| 14  | else |     |     |     |
| --- | ---- | --- | --- | --- |
15 op_types[i]=tempVerRead FunctionReadFromTable(rec_id,read_loc):
11
ifrec_id=INVALID_RECORDthen
12
| returnop_types |     |     |     | 13 returnNone |
| -------------- | --- | --- | --- | ------------- |
16
14 prevVer,currVer=GetTableVersions(table[rec_id])
15 ifread_loc==prevVerthen
| Algorithm4:CalculateRead/WriteLocations |     |     |     | 16 read_ver=prevVer |
| --------------------------------------- | --- | --- | --- | ------------------- |
elseifread_loc==currVerthen
17
FunctionGetRWLocation(op_types,tw_before): read_ver=currVer
| 1                     |     |                                   |     | 18                |
| --------------------- | --- | --------------------------------- | --- | ----------------- |
| rw_loc[op_types.size] |     | //locationsofread/writeoperations |     | else//tempVerread |
| 2                     |     |                                   |     | 19                |
parallelfori=0tosorted_ops.sizedo 20 read_ver=tempVers[read_loc.index]
3
ifop_types[i]∈{currVerRead,currVerWrite}then
| 4   |                   |     |     | 21 whileread_loc̸=prevVerand |
| --- | ----------------- | --- | --- | ---------------------------- |
| 5   | rw_loc[i]=currVer |     |     |                              |
atomicRead(read_ver.eid)̸=current_eiddo
| 6   | elseifop_types[i]==prevVerReadthen |     |     |     |
| --- | ---------------------------------- | --- | --- | --- |
22 Spin() //Waituntilversionisready
| 7   | rw_loc[i]=prevVer |     |     |     |
| --- | ----------------- | --- | --- | --- |
ifnotread_ver.is_validthen
| 8   | else//tempVerread/write,returntempVerindex |     |     | 23  |
| --- | ------------------------------------------ | --- | --- | --- |
returnNone
| 9   | ifop_types[i]==tempVerReadthen |     |     | 24                     |
| --- | ------------------------------ | --- | --- | ---------------------- |
|     | //indexiszero-based            |     |     | 25 returnread_ver.data |
rw_loc[i]={tempVer,index=tw_before[i]−1}
10
FunctionwriteToTable(rec_id,write_loc,data):
| 11  | else |     |     | 26  |
| --- | ---- | --- | --- | --- |
rw_loc[i]={tempVer,index=tw_before[i]} prevVer,currVer=GetTableVersions(table[rec_id])
| 12  |     |     |     | 27  |
| --- | --- | --- | --- | --- |
ifwrite_loc==currVerthen
28
write_ver=currVer
| 13 returnrw_loc |     |     |     | 29  |
| --------------- | --- | --- | --- | --- |
30 else//tempVerwrite
31 write_ver=tempVers[write_loc.index]
valid(V)data,asshowninFigure2.Anupdateorinsertsets 32 PerformWrite(write_ver.data,data)
andadeleteunsetsthevalidflagofthecorrespondingversion. 33 __threadfence()
atomicWrite(write_ver.eid,current_eid)
| Readoperationsusethevalidflagtodetermineiftherecord |     |     |     | 34  |
| --------------------------------------------------- | --- | --- | --- | --- |
existsatthetimestampoftheread,preventingtransactions
fromreadinginvaliddata(Algorithm5,lines23–24). areexpectedtoperformtheirreads,bufferwritesandissue
Deletion of records can happen at any point within an abortsbeforeanydatabasewrites.Sinceabortsdonotoccur
epoch,andalaterwriteoperationtoadeletedrecordwillre- afterthefirstwrite,thewritesofatransactionaremadevisible
| insertit.Consequently,therecordshouldbefreedonlywhen |     |     |     | immediately[12]. |
| ---------------------------------------------------- | --- | --- | --- | ---------------- |
the last write operation to a record in an epoch is a delete. In previous multi-versioned systems,a sentinel value is
Epictracksrecordsthataredeletedinanepochbysettinga usedtoindicatean abortedversion. Subsequentreadsskip
per-recorddeletedflagwhendeletionsoccurtocurrVer.At suchversionsandreadthepreviousnon-abortedversion.This
theendoftheepoch,theseflagsarescannedtogeneratealist approach is not suitable for Epic since there is no version
ofdeletedrecordsthataresubsequentlyfreed,asdescribed
search.Instead,theabortedwriteoperationsmustcopythe
laterinSection4.2.Afullscanaftereachepochisacceptable previousversiontothecurrentversion.Thus,fortransactions
becausetheflagisonebitperrecordandparallelscansare thatmayabort,Epicalsocalculatesthereadlocation(i.e.,of
efficientonGPUs.
thepreviousversion)forwriteoperationsduringinitialization.
| HandlingAborts |     | Epiceliminatesconcurrency-controlre- |     |     |
| -------------- | --- | ------------------------------------ | --- | --- |
latedabortsbecausetransactionsareserializedinapredeter-
3.4 FieldSplitting
| minedorder,similarto |     | otherdeterministic | databases. Epic |     |
| -------------------- | --- | ------------------ | --------------- | --- |
allowsapplication-levelaborts(e.g.,constraintviolations)be- Databaserecordsoftenconsistofmultiplefields.SinceEpic
foreanywritesareperformedtothedatabase.Transactions eliminatesversionsearch,eachversionofarecordmustcon-
770    18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

tainafullcopyofallofitsfields.Thisapproachaddscopying counter.Beforeanepochstarts,transactionsfromallcores
overheadwhenatransactionupdatesonlyafewfieldsofa canbeserializedbasedonthecoreIDandthelocalcounter
recordsinceallofitsfieldsmustbecopiedfromtheprevious value.ThismethodissimilartoCalvin[35].
version.Inaddition,itintroducesunnecessarydependencies
becauseeveryfieldupdatebecomesaread-modify-writeop-
4.2 IndexingandAllocation
erationfortherecord.
Epicimplementsafieldsplittingoptimizationbystoring Epiciscapableofexecutingtensofmillionsoftransactions
differentfieldsofarecordseparately.Eachversionnowcom- persecond.Itsindexneedstohandlehundredsofmillionsof
prisesonlyasinglefield.Asaresult,awritetoafielddoes operationspersecond,andsoweuseGPU-basedindexing.
notrequirecopyingotherfieldsandintroducesnoadditional EpicusesahashtableindextomapkeystorecordIDs.When
dependencies.However,thefieldsplittingoptimizationadds needed, range queries are performed in the read-write set
overhead forfull record operations,which need to be split identificationphaseusingarangeindextoobtainallthekeys
intomultipleper-fieldoperations,leadingtoincreasedinitial- forthe readandwrite sets. The keys are then usedto look
izationandsynchronizationcosts. uptherecordIDsinthehashtableindex.Epicimplements
indexingusingCuCollection[23],aGPU-basedconcurrent
3.5 Recovery hashtable.EpicusesamodifiedversionofaGPUB-tree[2,4]
fortherangeindex.
Currently, Epic does not support recovery and replica- SinceEpic’sindexingoperatesinparallel,weensurethat
tion. However,itcan provide durabilityandhighavailabil- readoperationsseeallpreviouslyinsertedrecordsbyperform-
ity by using techniques similar to previous deterministic inginsertoperationsbeforeanyindexingoperations,which
databases [35]. In each epoch, transaction inputs can be also prevents phantom reads. Epicdoes notdistinguishbe-
loggedtostorageontheCPUsideconcurrentlywithtransac- tweeninsertandwriteoperations,andsoitfirstindexesall
tionexecution.Onceallinputsarelogged,transactionresults writeoperationsinanepochtofindthekeystobeinserted
canbemadeexternallyvisibletoapplications.Currently,Epic (keysthatareinthewritesetbutarenotfoundinthehash
returnstheseresultsconservativelyattheendoftheepoch, table).Toallocatearecordforeachto-be-insertedkey,Epic
whichenableshandlingcertainproblematictransactionlogic, maintains a ring bufferof free record IDs on the GPU. To
suchasinfiniteloops,byabortingtherelevanttransactionand ease allocation,these keys are uniquified. Then,Epic allo-
itsdependenttransactions[12]. catesrecordIDsforthembyremovingthesamenumberof
Forrecovery,thetransactioninputsareusedtoreplayall recordIDsfromtheringbuffer.Thekey-recordIDmappings
transactionsdeterministicallyuntilthelastloggedepoch.The are then inserted in the hash table. Next, Epic indexes all
replayusesthesamemechanismasnormaltransactionpro- readandwriteoperations.Forreadoperations,ifakeyisnot
cessing.Toreducerecoverytime,Epic’stwo-versiontables found,Epicmarksthereadasinvalidbyreturningasentinel
allowcheckpointstobecreatedefficiently.Thecheckpointing invalid_readvaluefortherecordID.Thisvalueistreated
processcanruninparallelwithanepochandcreateaconsis- asanyotherrecordIDduringinitialization,andthenreads
tentdatabasesnapshotbycopyingtheprevVer ofeachrecord detectitduringexecution(Algorithm5,lines12–13).Since
toadifferentmemoryarea(e.g.,CPUmemory).However,the Epicperformsinsertsbeforereadoperations,areadofanon-
nextepochmuststartafterthecheckpointingcompletesor existingrecordmayseeanindexentryfromalaterwrite.A
elsetheresultingsnapshotmaybeinconsistent.Aftercreating readoperationdetectsthisversionasinvalidduringexecution
acopyofthetables,theycanbetransferredtopersistentstor- (seeSection3.3).
ageinthebackground.Theindexandallocationinformation Attheendofanepoch,Epic’sexecutionphasereturnsthe
alsoneedstobecheckpointedorrebuiltduringrecovery. deletedrecordIDs(seeSection3.3).Epicgarbagecollects
theserecordsbyappendingthemtotheringbuffer.Tofree
4 Implementation theindexentriesfortheserecords,Epicalsokeepsaback-link
arraythatmapsrecordIDstokeys. Thehashtableandthe
ThissectiondescribesEpic’sGPU-basedimplementationof back-linkarestoredinGPUmemoryandareonlyaccessed
indexing,initializationandtransactionexecutionphases. bytheGPUduringindexing.
4.1 TransactionBatchingandOrdering 4.3 Multi-VersionInitialization
Currently,Epicbatchestransactionswhentheyaregenerated Epic’smulti-versionconcurrencycontrolinitializationisim-
andseriallyordersthembyassigningatransactionIDtoeach plementedusingtheCUBandThrustparallelalgorithmsli-
transaction. In practice,the batching and ordering process brary.AsshowninAlgorithm2,alloperations,suchassort-
can be performed without contention by batching transac- ingandprefixsum,arehighlyparallelizable.Epicperforms
tionsseparatelyoneachcoreandorderingthemusingalocal initializationforeachtableseparatelyforeaseofimplementa-
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation 771

tion.Eachoperation’srecordID,transactionID,operationID GPUTransactionScheduling TheGPUhardwaresched-
andread-writetypearestoredina64bitintegerforefficient ulerdispatchesthreadsonanSMatthegranularityofagroup
sorting.ItispossibletoprefixtherecordIDwithatableID of threads called a thread block. While the GPU does not
andperforminitializationforalltablestogether. provide control overthe scheduling orderof thread blocks
We implemented an optimized CPU-based initialization (orthreadswithinathreadblock),itguaranteesthatanactive
phaseusingIntel’sTBBlibrarybutitsperformancewasat threadrunstocompletionwithoutbeingpreempted.
leastanorderofmagnitudeslowerthantheGPUimplemen- Since Epic assigns a serial order to each transaction be-
tation,motivatingourGPU-basedapproach. foreexecution,transactionsmustbescheduledbasedontheir
serial order. Otherwise,a later transaction may depend on
an earliertransaction,which nevergets to run because the
4.4 TransactionExecution latertransaction holdsthehardwareresources. Epicsched-
ules transactions in serial order by dynamically assigning
Afterthe concurrency controlinitialization phase,Epic ex- transactionstothreadswhentheybecomeactive.Todoso,
ecutes the entire batch of transactions concurrently on the ituses a next-transaction globalcounter,thatitincrements
GPUusingwarp-cooperativeexecution,anapproachmoti- onceperblocktoallocatetransactionsforallwarpswithina
vatedbypreviousworkonGPU-basedconcurrentdatastruc- block.Threadswithintheblockthendistributetheallocated
tures[1,3,39].Next,weprovidesomebackgroundonGPUs transactionsusingalocalcounter.
tomotivateourexecutionapproach.
GPUsprovideanarrayofmulti-threadedStreamingMul- 4.5 OtherOptimizations
tiprocessors (SMs),witheachSM containing simple cores
(typically64–128perSM).TheGPUexecutesinstructions Epic exploits parallelism within a transaction by splitting
fromagroupofthreads,calledawarp,inaSingleInstruction, transactions,whenpossible,intomultipleindependentpieces.
MultipleThreads(SIMT)lockstepmanneronthecoresofan Duetoitsdeterministicnature,thesepiecescanbeexecuted
SM,withthreadsexecutingthesameinstructionondifferent concurrentlywhilestillensuringisolation[12,28].
dataelements.Awarptypicallyconsistsofafixednumberof Epicaimstooverlapdatatransferandcomputationonthe
threads,suchas32threadsinNvidiaGPUs. GPUwheneverpossiblebylaunchingasynchronoustaskson
Thewarp-basedexecutionmodelmakesbranchdivergence differentnon-blockingCUDAstreams.Thisapproacheffec-
animportantaspectofGPUalgorithmdesign.Branchdiver- tivelyhidesthelatencyassociatedwithtransferringtransac-
genceoccurswhenthreadexecutiondivergesduetocontrol tionparametersanddata.AsshowninFigure1,Epictransfers
flowstatements,suchasbranches,forthreadswithinawarp. transactionparameterstotheGPU.Thistransferisoverlapped
Inthiscase,theGPUserializestheexecutionofthedivergent withtheexecutionofthepreviousbatchoftransactions.With
paths,causinglongerexecutiontimesperwarp. CPU-sideexecution,Epicoverlapsthetransferoftheindexed
transactionstotheCPUwiththeinitializationphase.
Insteadofrunningadifferenttransactiononeachthreadof
ItispossibletopipelineEpic’sCPU-sideexecutionwith
awarp,Epic’swarp-cooperativeexecutionmodelusesallthe
threadsinawarptocooperativelyexecuteasingletransaction, GPUindexingandinitialization.However,thisapproachcom-
plicatestheindexgarbagecollectionmechanism.Ifarecord
whichavoidsbranchdivergencealtogether.Thethreadsina
isdeletedinepochN,itsindexinformationcannotbegarbage
warpreadandwriteversionsbyaccessingconsecutiveloca-
collected until epoch N+2 because the indexing in epoch
tionsofarecord.TheGPUcancoalesce(orcombine)these
N+1runsconcurrentlywiththeexecutionofepochN.How-
contiguous memory accesses into a single request, which
ever,thesamekeymaybere-insertedinepochN+1.Inthis
improvesmemorybandwidthutilizationandisespeciallyben-
case,theindexinformationfortherecorddeletedinepochN
eficialwhentransactionsaccesslargerecords.Forexample,
cannotbegarbagecollected.Thisissuecanberesolvedby
32threadsinawarprunningthesameinstructioncanaccess
tracking the epochID in an index entry when itis created.
128contiguousbytesinparallelfromglobalmemory.
Epiccurrentlydoesnotimplementthispipelinedexecution.
Althoughwarp-cooperativeexecutioncanleadtoreduced
concurrency,theamountofparallelismavailableonmodern
GPUsismorethansufficientforEpic’stransactionprocess- 5 Evaluation
ingrequirements.Forexample,Nvidia’sA6000GPUhas84
SMs,eachcapableofscheduling1536threads(48warps)at We compare the overall performance of Epic with several
a time. Withthe warp-cooperative execution scheme,Epic state-of-the-artin-memorytransactionprocessingdatabases
can execute 84×48=4032 transactions concurrently. We using the TPC-C, TPC-C NP and the YCSB benchmarks.
believethattransactionexecutionwillnotbenefitfromhigher Then,weprovideamoredetailedanalysisofEpic’sdesign.
concurrencyduetodependenciesbetweentransactions.There- All experiments are run on cloud server with a 32-core
fore,thebenefitsofavoidingbranchdivergenceandcoalesced Epyc CPU and 512GB of memory. For all the CPU-based
memoryaccessoutweighthereducedconcurrency. databasesexceptAria,weuse1threadpercoreforatotalof
772 18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

32threads. ForAria,we usethe default12 workerthreads We only compare with GaccO’s GPU-based execution,
becausethisconfigurationachievesthehighestthroughput. so no synchronization with the CPU is needed. Similar to
We use the Nvidia A6000 GPU with 10752 CUDA cores Epic,GaccOrequirestransactions’read-writesetsinadvance.
and48GBGDDR6memory.TheoperatingsystemisUbuntu GaccOinitializesanepochbycreatingaper-recordlockta-
22.04.AllexperimentsarecompiledwithNVCC12.0with ble. Foreachrecord,alloperationsaresortedbasedonthe
CUDAruntimeversion12.0. serialID ofthe transactions. The corresponding serial IDs
are stored in the lock table,representing the order of lock
acquisition.Duringtheexecutionphase,transactionsacquire
5.1 DatabaseSystemsComparison
locksonrecordsdeterministicallybycheckingthelocktable
We compare Epic against four state-of-the-art in-memory andwaitinguntilthelockvaluematchesthetransaction’sID.
databases:STOv2[14],Caracal[28],GaccO[6]andAria[21]. Uponrelease,thelockvalueisadvancedtomatchthenext
We use the publicly available implementations of Caracal, transactionthataccessestherecord.However,thislock-based
STOv2andAria.SinceGaccO’simplementationisnotpub- concurrencycontroldoesnotpermitreaderstosharelocks.
liclyavailable,weimplementedGaccO’sGPU-sidetransac- GaccOexecutesatransactionperthreadandbatchestrans-
tion execution based on the description in their paper. We actionsbytype(e.g.,NewOrderinTPC-C)withinanepoch
usethedefaultepochsizesof500forAria,100KforCara- tominimizewarpdivergence(seeSection4.4).Thisbatching
cal,and32768forGaccOasspecifiedintheirpapersforall alsoenablesGaccOtouseacommutativeoptimizationwhen
experimentsexceptforthelatencyexperimentinSection5.7. highly-contended items are accessed commutatively. If an
Weuseanepochsizeof100KtransactionsforEpicbecause operationupdatesadataitemcommutativelythentheorder
throughputimprovementsbecomesmallerbeyondthisepoch ofperformingsuchupdatesisflexible,providedthedataitem
size,whichbalancesthroughputandlatency. isnototherwiseobservedbyitstransactionandthereareno
STOv2isastate-of-artin-memoryCPUdatabase.STOv2 otherconflictingoperationsontheitem.Forinstance,atrans-
implementsandcomparesthreeconcurrencycontrolmecha- actionthatincrementsacounterinthedatabaserowbutnever
nisms:OCC-basedSilo[36],timestamp-basedTicToc[38], readsthevalueofthecountercanimplementtheupdateusing
andavariantofMVCC-basedCicada[17].Thesemechanisms atomicinstructions,withoutusingthedeterministiclocking
arecalledOSTO,TSTO,andMSTOrespectively.STOv2’s protocol.SinceGaccObatchestransactionsbytype,conflicts
implementationsofTicTocandCicadaperformwellthanksto donotoccurwithothertypesoftransactions.
carefulattentiontoimplementationchoices.Weenableboth However,duetothisbatchingoftransactionsbytype,we
thetimestampsplittinganddeferredupdatesoptimizations donotimplementthefullTPC-CbenchmarkforGaccO.For
inSTOv2.Timestampsplittingbehavessimilartoourfield theOrderStatusandStockLeveltransactions,batchingbytype
splittingoptimization. wouldcausethesetransactionstoexecuteonasnapshotof
Caracal is a multi-versioned, deterministic CPU in- the database and return the same results within an epoch.
memorydatabase.SimilartoEpic,Caracalbatchestransac- Therefore,we only evaluate GaccO on the TPC-C NP and
tionsandsplitseachepochintoaninitializationphaseandan YCSBbenchmarks.1
executionphase.Caracalusesaversionarraytoimplement
Ariaisadeterministicdatabasethatdoesnotrequiread-
multi-versionconcurrencycontrol(MVCC).Eachrecordcon-
vance knowledge of read-write sets [21]. It achieves deter-
tainsanarrayofversionsthatarecreatedduringtheinitial-
minism by executing all transactions in a batch against a
izationphaseandreadduringtheexecutionphase.Caracal
databasesnapshotfromthepreviousepoch,whilebuffering
performswellundercontentionduetotransactionbatching
writesanddelayingcommituntiltheendoftheepoch.After
andMVCC.However,Caracal’sconcurrencycontrolmecha-
alltransactionshaveexecuted,Ariadeterministicallyaborts
nismkeepstheversionarraysortedbytheversionID,which
transactionsthatconflictwithanearliertransactionbasedon
imposes overhead during the initialization phase,and read
transactionIDordering,anditusesadeterministicreordering
operationsneedtoperformabinarysearchthroughthever-
optimizationtoreordertransactionsinabatchtoreducethe
sionarrays.Additionally,theversionarrayrequiresexpensive
numberof aborts. Aria assumes that the read-write sets of
garbagecollection.
transactions are known afterthe execution phase,anduses
GaccOisasingle-version,deterministicGPUdatabasethat
Calvin’sdeterministiclockingasafallbackstrategytorerun
useslock-basedconcurrencycontrol[6].Tosupportdatabases
theabortedtransactionsaftertheexecutionphase.
largerthanGPUmemory,GaccOproposesrunningtransac-
Aria only implements TPC-C NP. We evaluate the vari-
tions on both the GPU and the CPU. This CPU-GPU co-
antwiththefallbackstrategysincetheirpaperreportsthatit
execution model requires keeping copies of CPU memory
performsbetterthanwithoutthefallbackstrategyunderall
tablesinGPUmemorywhenthetablesareaccessedbyGPU-
contentionlevelsonTPC-CNP.
sidetransactions,synchronizingupdatestothetablesatepoch
boundaries,anddelayingCPU-sidetransactionsthatconflict
withGPU-sidetransactions. 1TheGaccOpaperalsoevaluatesTPC-CNPontheGPU.
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation 773

5.2 TPC-C contentionlevels.Underlowcontention,Epicbenefitsfrom
thehighmemorybandwidthandparallelismofferedbythe
WeusetheTPC-COLTPbenchmarktoevaluateEpic.The GPU,enablingittooutperformallothersystems. Thetwo
TPC-CbenchmarksimulatesanOLTPworkloadforaware- multi-versionedCPUsystems,MSTOandCaracal,perform
house management system. It consists of five transactions: poorly under low contention due to the high overhead of
NewOrder,Payment,OrderStatus,Delivery,andStockLevel. MVCC.However,theyperformbetterunderhighcontention
TheNewOrdertransactioncreatesaneworderforacus- comparedtothesingleversionsystems.Asexpected,Epic’s
tomerbyincrementingthenextOrderIDfieldintheDistrict performancedegradesunderhighcontention.However,due
table to obtain the order ID. This makes the write-set of tothedeterministicorderingoftransactionsanditsefficient
NewOrderdependentontheexecution-timevalueoftheorder multi-versioningimplementation,Epicoutperformstheother
ID.OrderStatusretrievesthestatusofthelastorderplaced systemsunderhighcontentionaswell.
by a customer; StockLevel checks the stock level of items
orderedinthelast20transactionsinadistrict;andDelivery
5.3 TPC-CNP
processestheoldestundeliveredorderinadistrict.
Toidentifytheread-setandwrite-setkeysofthesetransac-
TheTPC-CNPbenchmarkisasubsetoftheTPC-Cbench-
tions,Epicrunstheread-writesetidentificationphasebefore
markthatconsistsof50%NewOrderand50%Paymenttrans-
theindexingphase.Initially,theorderIDusedbyNewOrder
actions.WeusethisbenchmarktocomparewithGaccOand
is calculated using a per-district counter,which also helps
Ariaaswell.TheleftgraphinFigure5showsthethroughput
determinethelatestorderIDforOrderStatusandStockLevel.
oftheGPUandthentheCPUsystemsforTPC-CNP.
Then,foreachNewOrdertransaction,theorderinformation
TheEpic,STOv2andCaracalTPC-CNPresultsarequali-
isinsertedintoasecondaryindex.Thesecondaryindexuses
tativelysimilartoTPC-Cresults.Thesedatabaseshavehigher
a range index keyed by the customer ID and the order ID.
throughputonTPC-CNPunderlowcontentionbecauseTPC-
The secondary index also stores the items ordered in each
C NP has shorter transactions than TPC-C. However,they
order. OrderStatus performs a backward range scan using
havelowerthroughputonTPC-CNPunderhighcontention
thecustomerIDandthelatestorderIDinthedistrictasthe
becauseTPC-CNPhashighercontentionthanTPC-C.Cara-
keytofindthelastorderIDforacustomer.StockLeveluses
cal and Aria have lowerthroughput than otherCPU based
thelatestorderIDtolookuptheorderediteminformationto
databases,buttheyalsosupportdistributedoperation.
checkforstocklevels.Lastly,Deliveryusesaper-warehouse
GaccOperformspoorlyunderallcontentionlevelsbecause
countertofindtheoldestundeliveredorder.
itbatchestransactionsbytype.ForthePaymenttransaction,
Duringexecution,transactionscanvalidatetheread-write updates on the warehouse table require GaccO to serialize
setsdeterminedbytheidentificationphaseandaborttrans- alltransactions.Also,GaccOcannotrunNewOrdertransac-
actionsiftheydonotmatchthekeysthatwouldbeaccessed tionsconcurrentlywithPaymenttransactions,resultinginthe
duringtheexecutionphase[35].However,sinceEpicdoesnot GPUbeingunderutilized.Additionally,GaccO’slock-based
causeanyconcurrency-controlrelatedaborts,theread-write concurrencycontrolhashighoverheadundercontention.
setsalwaysmatchinTPC-Candsonoabortsoccur[11].
Epic’sperformanceunderlowcontentionforTPC-CNPis
Furthermore,thePaymentandOrderStatustransactionsin muchhigherthanforTPC-Cfortworeasons.First,TPC-C
theoriginalTPC-Cbenchmarkcanbeprovidedwithacus- NP does not require scanning for the latest order of a cus-
tomerIDorthecustomer’slastname.Inthelattercase,the tomerandlookupforordereditemsandsotheoverheadof
customer ID is retrieved by scanning a read-only index of read-writeidentificationissignificantlylower.Second,and
customers.SinceexistingGPUrangeindexesdonotsupport moreimportantly,TPC-CNPhasshorttransactionsthatcan
variablelengthkeysneededforscanningthelastname,we bescheduledonGPUthreadblocks(seeSection4.4)more
simplifiedPaymentandOrderStatustoonlyusethecustomer efficiently.WithTPC-C’smixofshortandlongtransactions,
IDforallthedatabases.Otherthanthischange,thebehavior ablockneedstowaitforthelongesttransactiontocomplete.
andcontentionlevelofEpic’sTPC-Cimplementationcon- Weplantoexploreschedulingstrategiesthatco-locatelong
formstotheTPC-Cspecification. read-onlytransactionswithinblocks.
TPC-C has low contention when each warehouse is as- ToimplementGaccO’scommutativeoptimizationforTPC-
signed a separate CPU core. We vary the numberof ware- CNP,wechangedtheNewOrdertransactiontouseatomic
houses to evaluate performance under different contention CASinstructionstoupdatetheDistrictandStocktables,and
levels.Withasinglewarehouse,TPC-Cbecomeshighlycon- we changed the Payment transaction to use atomicAdd to
tended due to the per-warehouse Warehouse,District,and increment the balances of the warehouse,district,and cus-
Stocktables. tomerstables.Sincetheupdatedvaluesarenotusedafterthe
STOv2andCaracalimplementtheTPC-Cbenchmarkand updateorreadbyothertransactions,theorderofupdatesis
wecompareEpicagainstthem.Figure4showsthethroughput flexible.TherightgraphinFigure5showsthatGaccOwith
ofthesystems.Epicoutperformstheothersystemsunderall this optimization outperforms all systems. The throughput
774 18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|     |     |     | Epic | OSTO | TSTO | MSTO | Caracal |     |     |     |
| --- | --- | --- | ---- | ---- | ---- | ---- | ------- | --- | --- | --- |
)s/snxTM(tuphguorhT
30
|     |     | 20  |     |     |     |     | 94.41 |     | 57.41 |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | ----- | --- |
78.21
16.9
|     |     | 10             | 98.3                | 4.6       |           |                |      | 34.4 59.3 | 45.4 40.4 |      |
| --- | --- | -------------- | ------------------- | --------- | --------- | -------------- | ---- | --------- | --------- | ---- |
|     |     | 51.2           | 98.1                | 43.3 99.2 | 25.3 41.3 | 77.3 63.3 29.1 |      | 71.2      |           | 62.2 |
|     |     | 74.0 73.0 44.1 | 16.0 35.1 65.1 67.0 | 56.1 78.0 | 37.1 20.1 |                | 60.1 | 21.1      |           | 89.0 |
0
|     |     | 1   | 2   | 4   | 8   | 16  |     | 32  | 64  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
NumberofWarehouses
Figure4:TPC-CThroughput
|     |     | Epic Gacco | OSTO | TSTO | MSTO | Caracal | Aria |     |     | Gacco+Commutative |
| --- | --- | ---------- | ---- | ---- | ---- | ------- | ---- | --- | --- | ----------------- |
80
| )s/snxTM(tuphguorhT |     |     |     |     |     |     |     |       |     | 19.06             |
| ------------------- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | ----------------- |
| 30                  |     |     |     |     |     |     |     | 84.42 |     | 13.85 41.75 48.45 |
53.25 81.05 75.94
|     |           |               |      |       |           | 84.02 |     |           |     | 60  |
| --- | --------- | ------------- | ---- | ----- | --------- | ----- | --- | --------- | --- | --- |
| 20  |           |               |      |       | 23.51     |       |     |           |     |     |
|     |           |               |      | 34.01 |           |       |     |           |     | 40  |
| 10  | 2−01·26.2 | 2−01·30.5     | 14.6 |       |           | 23.5  |     | 11.5      |     |     |
|     |           | 2−01·7.9 26.3 | 60.3 | 93.3  | 63.4 67.3 | 26.4  |     | 61.3 14.4 |     | 20  |
39.1 11.1 34.1 85.1 4.3 57.1 79.0 9.3 49.1 23.1 30.1 2.2 83.1 55.2 34.1 64.2 92.1
53.0 33.0 4.1 6.0 8.0 21.0 61.0 11.0 15.0 72.0 23.0 8.1 83.0 24.0
| 0   |     |     |                    |     |     |     |     |     |     | 0                  |
| --- | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- | ------------------ |
|     | 1   | 2   | 4                  | 8   | 16  | 32  |     | 64  |     | 1 2 4 8 163264     |
|     |     |     | NumberofWarehouses |     |     |     |     |     |     | NumberofWarehouses |
Figure5:TPC-CNPThroughput
dropsslightlywithmorewarehousesduetodecreasedcache Workload Description Operations
locality.Thisoptimizationeliminatesconcurrencycontrolin
|     |     |     |     |     | YCSB-A | Updateheavy |     |     | Read:50%,Update:50% |     |
| --- | --- | --- | --- | --- | ------ | ----------- | --- | --- | ------------------- | --- |
TPC-CNPsinceboththeNewOrderandthePaymenttrans-
|     |     |     |     |     | YCSB-B | Readheavy |     |     | Read:95%,Update:5% |     |
| --- | --- | --- | --- | --- | ------ | --------- | --- | --- | ------------------ | --- |
actionsdonotholdanylocks.However,thisoptimizationis
|     |     |     |     |     | YCSB-C | Readonly |     |     | Read:100% |     |
| --- | --- | --- | --- | --- | ------ | -------- | --- | --- | --------- | --- |
notgeneral-purpose,e.g.,itdoesn’tallowreadingtheDistrict
|     |     |     |     |     | YCSB-F | Read-modify-write |     |     | Read:50%,RMW:50% |     |
| --- | --- | --- | --- | --- | ------ | ----------------- | --- | --- | ---------------- | --- |
tabletovalidatetheorderIDintheNewOrdertransaction.
Figure6:YCSBWorkloadConfigurations
5.4 YCSB
record,theentirerecordneedstobecopiedfromtheprevious
Next,weconductexperimentsusingtheYahoo!CloudServ- version.Asaresult,theread-modify-writeoperationsform
ingBenchmark(YCSB)[9].Fortheexperimentalsetup,we longdependencychainsunderhighcontention.IntheYCSB-
useasingletableconsistingof1,000,000records.Weused Bbenchmark,wherethewriteratioislow,Epic’sperformance
thestandardrecordsizeinYCSB,whereeachrecordis1000 drops more gently underhigh contention. In the read-only
bytesandconsistsoften100bytefields.Weperformedex- YCSB-Cbenchmark,Epicachieveshighthroughputdueto
perimentsusingfourYCSBworkloads,asshowninFigure6. thehighmemorybandwidthofGPUs.Finally,intheYCSB-F
Inallworkloads,areadoperationreadstheentirerecord.An benchmark,EpicshowsasimilartrendasYCSB-A,where
updateoperationreplacesthevalueofonerandomlychosen performance drops significantly under high contention be-
field.Aread-modify-write(RMW)operationreadsarecord causeEpicperformsthesameread-modify-writeoperations
andupdatesarandomlychosenfield.Forourevaluation,we forbothYCSB-AandYCSB-F.Insomeworkloads,Epic’s
group10operationstoformatransaction.WevarytheZipfian throughputincreasesslightlyfromlowtomediumcontention
skewfactorθfrom0to0.99tovarycontentionlevels. level(skewfactor0.0to0.5)duetobettercachelocalitythat
Figure7showsthethroughputofthesixdatabasesforthe improvesGPUindexingperformance.Theexecutionphase
fourYCSBworkloadswithincreasingcontentionlevels.Epic inEpicalsobenefitsfromthisbettercachelocality,especially
outperformsallotherdatabasesforallworkloads.InYCSB-A, forread-onlyYCSB-C.
Epic’sperformancedropssignificantlyunderhighcontention. WealsoevaluatetheperformanceofEpicwithfieldsplit-
Epicperformsaread-modify-writeoperationforeachupdate ting,asdescribedinSection3.4.Inthiscase,eachrecordis
operation.Evenwhenanupdateonlywritestoapartofthe dividedintotenfields,andeachfieldistreatedasaseparate
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation    775

40
30
20
10
0.0 0.2 0.4 0.6 0.8 0.9 0.95 0.99
Zipfiancontentionfactorθ
s/snxTMtuphguorhT
Epic Epic+FieldSplit Gacco OSTO TSTO MSTO Caracal
YCSB-A YCSB-B YCSB-C YCSB-F
40
30
20
10
0.0 0.2 0.4 0.6 0.8 0.9 0.95 0.99 0.0 0.2 0.4 0.6 0.8 0.9 0.95 0.99 0.0 0.2 0.4 0.6 0.8 0.9 0.95 0.99
Zipfiancontentionfactorθ Zipfiancontentionfactorθ Zipfiancontentionfactorθ
Figure7:YCSBThroughput
dataitemfromtheperspectiveofconcurrencycontrol.Asa read-heavyworkloads(YCSB-BandYCSB-C),OSTOand
result,eachfull-recordreadoperationneedstoperform10 TSTOoutperformMSTOandCaracalduetotheirlightweight
fieldreads,eachrequiringseparatesynchronization.Asare- concurrencycontrolmechanisms.However,Caracalachieves
sult,thenumberofreadoperationsintheinitializationphase higher throughput than OSTO and TSTO in YCSB-A and
increases by 10x,and read performance decreases. On the YCSB-FunderhighcontentionbecauseitsMVCC-basedcon-
otherhand,sinceeachfieldistreatedseparately,anupdate currencycontrolallowsreaderstoruninparallelwithwriters.
operationonasinglefielddoesnotrequirecopyingtherest
of the fields from the previous versions,improving update
5.5 CPU-sideExecution
performance.AsshowninFigure7,Epicwithfieldsplitting
performsbetterthandefaultEpicunderYCSB-Awithhigh
Next,weevaluatetheperformanceofEpic’sCPU-sideexe-
contention.However,Epic’sperformanceislowerinYCSB-
cutionusingthesamesetupfortheTPC-C,TPC-CNPand
B,YCSB-C,andYCSB-F,wherethereadratioishigher.
YCSBbenchmarks.AsmentionedinSection3.3,theGPU
GaccOshowssimilartrendsunderallworkloads,perform- performsindexingandinitializationfortheepochandthen
ing well under low contention, but its performance drops transfers the execution plan to the CPU. This data transfer
significantlyunderhighcontentionduetoitslock-basedcon- takesroughly4msfortheTPC-CNPandYCSBbenchmarks
currencycontrol.GaccO’sinitializationphaseissimplerand and 6 ms forTPC-C,which contains long running queries
fasterthanEpic’sMVCCinitializationbutitslock-basedcon- withmoreoperations.Thetransactionsarethenexecutedon
currencycontroldoesnotallowreaderstosharelocks,causing theCPU.ThethroughputreportedinFigure8includesthe
itsperformancetodropsignificantlyundercontention,even timeforindexing,initialization,datatransferandexecution
underaread-onlyworkload.GaccO’sassignseachtransaction becauseEpiccurrentlydoesnotimplementpipelining.
toasingleGPUthread,whichcausesnon-coalescedmemory WithTPC-CandTPC-CNP,CPU-sideexecutionachieves
accessesthatreducememorybandwidthutilization.Asare- higher throughput than GPU-side execution with a single
sult,GaccO’sperformancedecreaseswhentheratioofread warehouse.WebelievethatthecontendedPaymenttransac-
operationsincreases(YCSB-AandYCSB-B)becauseread tionlimitsEpicfromutilizingtheparallelismoftheGPUef-
operationsretrievetheentirerecord.GaccO’scommutative fectively.OntheCPU,Epic’sexecutiontimesynchronization
operationoptimizationcannotbeappliedtoYCSBworkloads ismoreefficientastheatomicflagscanbedirectlycommu-
(exceptYCSB-C)becauseothertransactionsreadthevalues nicatedthroughtheCPUcache.However,withmoreware-
ofthedataitemsupdated.Therefore,wedidnotimplement houses,GPU-sideexecutionachieveshigherthroughputdue
thisoptimizationfortheYCSBworkloads. tothehigherparallelismandmemorybandwidthoftheGPU.
Bothmulti-versionedsystems(MSTOandCaracal)suffer WithCPU-sideexecution,Epicachieveslowerthroughput
fromthesameextradependencyasEpicinYCSB-A.There- inTPC-CthanTPC-CNPunderlowcontentionduetothe
fore,theyexhibitsimilartrends forYCSB-A andYCSB-F. longerdatatransfertime.However,Epicperformsbetterfor
OSTO and TSTO perform well under low contention, but TPC-C witha single warehouse because TPC-C has lower
theirperformancedropssignificantlyunderhighcontention contentionthanTPC-CNP.
withwrite-heavyworkloads(YCSB-AandYCSB-F).Thisis WithYCSB,eachtransactionreadsseveralrecords,andso
duetoincreasedabortsresultingfromahighconflictrate.In CPU-sideexecutionislimitedbymemorybandwidthandla-
776 18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|                     |     |     |       | Epic | EpicCPU |         |     |     |     | RWSetIdentification  | Index        |                   | Initialization |     |
| ------------------- | --- | --- | ----- | ---- | ------- | ------- | --- | --- | --- | -------------------- | ------------ | ----------------- | -------------- | --- |
|                     |     |     | TPC-C |      |         | TPC-CNP |     |     |     | DataTransfer         | GPUExecution |                   | CPUExecution   |     |
|                     |     |     |       |      |         |         |     |     |     | TPC-CSingleWarehouse |              | TPC-C64Warehouses |                |     |
| )s/snxTM(tuphguorhT | 30  |     |       |      | 30      |         |     |     |     |                      |              |                   |                |     |
84.42
84.02
|     | 20  |     |       | 94.41 57.41 | 20  |     | 23.51 |     |     |     |     |     |     |     |
| --- | --- | --- | ----- | ----------- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     | 78.21 |             |     |     |       |     | 40  |     |     | 40  |     |     |
34.01
16.9
|                     | 10   |               |           |           | 10      | 14.6          |           | 51.6  |          |                     |     |     |           |           |
| ------------------- | ---- | ------------- | --------- | --------- | ------- | ------------- | --------- | ----- | -------- | ------------------- | --- | --- | --------- | --------- |
|                     |      | 4.6           |           |           |         | 72.4 31.5     | 74.5 38.5 | 27.5  |          |                     |     |     |           |           |
|                     | 49.2 | 98.3 12.3 5.3 | 86.3 76.3 | 48.3 98.3 |         | 77.2 26.3     |           |       | )sm(emit |                     |     |     |           |           |
|                     | 51.2 |               |           |           | 39.1    |               |           |       |          |                     |     |     |           |           |
|                     | 0    |               |           |           | 0       |               |           |       |          |                     |     |     |           |           |
|                     |      |               |           |           |         |               |           |       | 20       |                     |     | 20  |           |           |
|                     | 1    | 2 4           | 8 16      | 32 64     | 1       | 2 4           | 8 16      | 32 64 |          |                     |     |     |           |           |
|                     |      | NumWarehouses |           |           |         | NumWarehouses |           |       |          |                     |     |     |           |           |
|                     |      |               |           | Epic      | EpicCPU |               |           |       |          |                     |     |     |           |           |
|                     |      | YCSB-C        |           |           |         | YCSB-F        |           |       |          |                     |     |     |           |           |
|                     |      |               |           |           |         |               |           |       | 0        |                     |     | 0   |           |           |
| )s/snxTM(tuphguorhT |      |               |           |           |         |               |           |       |          | GPU CPU             |     |     | GPU       | CPU       |
|                     |      |               |           |           | 40      |               |           |       |          | Execution Execution |     |     | Execution | Execution |
40
Figure9:EpicRunTimeBreakdown
|     | 30  |     |     |     | 30  |     |     |     |                                                    |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- |
|     | 20  |     |     |     | 20  |     |     |     | phaseisunaffectedbythecontentionlevel.TheGPUexecu- |     |     |     |     |     |
tiontimeissignificantlylongerunderhighcontentionbecause
|     | 10  |     |     |     | 10  |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
transactiondependenciesreduceGPUutilization.
ForCPUexecution,theindexedtransactionsandthetrans-
actionexecutionplansneedtobetransferredfromtheGPU
|     | 0.0 | 0.2 0.4 | 0.6 0.8 0.9 | 0.950.99 | 0.0 | 0.2 0.4 | 0.6 0.8 0.9 | 0.950.99 |     |     |     |     |     |     |
| --- | --- | ------- | ----------- | -------- | --- | ------- | ----------- | -------- | --- | --- | --- | --- | --- | --- |
Zipfiancontentionfactorθ Zipfiancontentionfactorθ totheCPU.Dependingonthecomplexityofthetransaction,
thedatatransfertimecanvarybutisasignificantportionof
Figure8:ThroughputwithCPU-sideExecution
thetotalruntime.PipeliningtheGPUandCPUphaseswill
helpreducetheepochruntime.
tency.Forread-onlyYCSB-C,CPU-sideexecutionhasmuch
lowerthroughputthanGPU-sideexecution.Throughputin-
| creasesslightlyundercontentionduetocachelocality.For |     |     |     |     |     |     |     |     | 5.7 Latency |     |     |     |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- |
YCSB-F,CPU-sideexecutionthroughputisbottleneckedby
Inthisexperiment,weevaluateEpic’sthroughputandlatency
| memorybandwidthatlowcontention |     |             |     |           | andachieves |      | similar     |     |               |                        |     |            |         |              |
| ------------------------------ | --- | ----------- | --- | --------- | ----------- | ---- | ----------- | --- | ------------- | ---------------------- | --- | ---------- | ------- | ------------ |
|                                |     |             |     |           |             |      |             |     | for different | epoch sizes            | by  | comparing  | against | the GaccO,   |
| throughput                     |     | as GPU-side |     | execution | under       | high | contention. |     |               |                        |     |            |         |              |
|                                |     |             |     |           |             |      |             |     | Caracal,      | and Aria deterministic |     | databases. |         | We show TPC- |
YCSB-AandYCSB-Bshowsimilartrendssoweomitthem.
CNPresultsbecauseourGaccOimplementationandAria
Forallthethreebenchmarks,Epic’sCPU-sideexecution
implementTPC-CNP.WealsoshowYCSB-Fresults(butnot
| achieves | comparable |     | throughput |     | to OSTO | and | TSTO | un- |     |     |     |     |     |     |
| -------- | ---------- | --- | ---------- | --- | ------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
forAria,whichdoesn’timplementit).Forbothworkloads,
derlowcontentionbecauseEpic’sGPUinitializationisef-
weshowresultsunderlowandhighcontention.Epic’sresults
ficient.Underhighcontention,EpicoutperformsOSTOby
forTPC-CarenotshownbuttheyaresimilartoTPC-CNP.
| 6.2x | and TSTO |     | by 7.9x | for TPC-C | single | warehouse |     | and |         |           |      |      |        |               |
| ---- | -------- | --- | ------- | --------- | ------ | --------- | --- | --- | ------- | --------- | ---- | ---- | ------ | ------------- |
|      |          |     |         |           |        |           |     |     | We vary | the epoch | size | from | 500 to | 200K transac- |
bothby3.2xforYCSB-Fwitha0.99skewfactorduetoits
|     |     |     |     |     |     |     |     |     | tions/epoch. | Epic batches | transactions |     | during | the previous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ------------ | ------------ | --- | ------ | ------------ |
multi-versioning.Epic-CPUoutperformsbothmulti-version
|              |     |     |                   |     |     |           |         |     | epoch and | the benchmarks |     | do not | cause aborts, | so Epic’s |
| ------------ | --- | --- | ----------------- | --- | --- | --------- | ------- | --- | --------- | -------------- | --- | ------ | ------------- | --------- |
| systems,MSTO |     |     | and Caracal,under |     | all | workloads | because |     |           |                |     |        |               |           |
averagetransactionlatencyis1.5×theepochruntime.
Epic’sMVCCinitializationisefficientand,unlikeMSTOand
Figure10showsthethroughputandaveragelatencyofthe
Caracal,Epic’sCPU-sideexecutionrunswithoutperforming
foursystems.Eachpointonalinerepresentsanepochsize.
expensiveversionsearch.
Thelinesstartat5000forCaracal(whichcrashesatlower
epochsizes)and500forallothersystems.Thelinesalsoshow
somekeyepochsizes,e.g.,atmaximumthroughputandat
5.6 RunTimeBreakdown
thekneeofthecurve.Inallworkloads,Epicachieveshigher
Figure9showsthebreakdownofper-epochruntimeforEpic throughput withincreasing epoch size. Intuitively,a larger
running TPC-C with the CPU- and GPU-execution model. epochenableshigherparallelismandamortizesoverheadsat
Thefigureshowsthattheinitializationtimeissimilarforboth thecostoftransactionlatency.Similarly,Caracal’sthroughput
lowandhighcontentionlevelsbecauseEpic’sinitialization increaseswithlargerepochsizes.
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation    777

|     |     |      |       |         |      |     |     | Throughput |     |     |     | Latency |     |
| --- | --- | ---- | ----- | ------- | ---- | --- | --- | ---------- | --- | --- | --- | ------- | --- |
|     |     | Epic | Gacco | Caracal | Aria |     |     |            |     |     |     |         |     |
)sm(ycnetaLnoitcasnarTgvA
|     | TPC-CNPSingleWarehouse |     |     |     |     |     | 8   |     |     |     |     |     |     |
| --- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
TPC-CNP64Warehouses
|     |     |     |      | 10  |     |       | s/snxTMtuphguorhT |     |     |     |     |     |     |
| --- | --- | --- | ---- | --- | --- | ----- | ----------------- | --- | --- | --- | --- | --- | --- |
|     |     |     | ←30k |     | ←   |       |                   |     |     |     |     |     |     |
|     |     |     |      |     | 20k | 160k← |                   |     |     |     | 20  |     |     |
6
| 20  |     |     |     | 8   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
←14k
)sm(ycnetaL
4
6
10
| 10  |     |     |     | 4   |      |      | 2   |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | ---- | ---- | --- | --- | --- | --- | --- | --- | --- |
|     | 1k← |     |     |     |      | ←50k |     |     |     |     |     |     |     |
|     |     | 5k  | ←   |     | ← 7k |      |     |     |     |     |     |     |     |
2
|     |              |     |     |     |             |       | 0   |              |       |       | 0   |              |          |
| --- | ------------ | --- | --- | --- | ----------- | ----- | --- | ------------ | ----- | ----- | --- | ------------ | -------- |
|     |              |     |     |     |             |       |     | 0 5          | 10 15 | 20 25 |     | 0 5 10       | 15 20 25 |
| 0   |              |     |     | 0   |             |       |     |              |       |       |     |              |          |
|     |              |     |     |     |             |       |     | AbortRate(%) |       |       |     | AbortRate(%) |          |
|     | 0            | 1   | 2   | 0   | 10          | 20 30 |     |              |       |       |     |              |          |
|     | YCSB-Fθ=0.99 |     |     |     | YCSB-Fθ=0.0 |       |     |              |       |       |     |              |          |
Figure11:ImpactofAbortRate
10 ←30k
|     |     |     | ←50k |     |     | 160k← |     |     |     |     |     |     |     |
| --- | --- | --- | ---- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
| 20  |     |     |      | 8   |     |       |     |     |     |     |     |     |     |
andsoanabortedtransactionwillnotabortagainwhenrerun,
)sm(ycnetaL
similartoAria’sassumptionforitsfallbackstrategy[21].
6
|     |     |     |     |     |     |     | Figure                                               | 11  | shows Epic’s | throughput |     | and average | latency. |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- | --- | ------------ | ---------- | --- | ----------- | -------- |
| 10  |     |     |     | 4   |     |     | Astheabortrateincreases,Epic’sthroughputdecreasesand |     |              |            |     |             |          |
←18k
50k←
latencyincreasesroughlylinearly.Abortedtransactionsare
2
|     |     |     |     |     | ← 6k 5k |      | rerun | in the next | epoch,which |     | increases | their | latency and |
| --- | --- | --- | --- | --- | ------- | ---- | ----- | ----------- | ----------- | --- | --------- | ----- | ----------- |
|     | ←1k |     | ←5k |     | ←       | ←16k |       |             |             |     |           |       |             |
requiresadditionalwork.
| 0   |                   |                               |     | 0   |                   |       |     |             |     |     |     |     |     |
| --- | ----------------- | ----------------------------- | --- | --- | ----------------- | ----- | --- | ----------- | --- | --- | --- | --- | --- |
|     | 0 1               | 2                             | 3   | 4 0 | 10                | 20 30 |     |             |     |     |     |     |     |
|     | ThroughputMTxns/s |                               |     |     | ThroughputMTxns/s |       |     |             |     |     |     |     |     |
|     |                   | Figure10:Latencyvs.Throughput |     |     |                   |       | 6   | Conclusions |     |     |     |     |     |
GaccO’sthroughputincreaseswithlargerepochsizesini-
|     |     |     |     |     |     |     | Multi-versioning |     | schemes | for | transaction | processing | sys- |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------- | --- | ----------- | ---------- | ---- |
tiallybutthendecreases.WebelievethatGaccO’slock-based
|     |     |     |     |     |     |     | tems | have traditionally |     | been | popularbecause | they | provide |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------------------ | --- | ---- | -------------- | ---- | ------- |
schedulingperformancedegradeswithincreasingnumberof
|     |     |     |     |     |     |     | good | performance | for | a range | of workloads,including |     | for |
| --- | --- | --- | --- | --- | --- | --- | ---- | ----------- | --- | ------- | ---------------------- | --- | --- |
concurrenttransactions.Weplantoinvestigatethisissue.
|     |     |     |     |     |     |     | long-running |     | transactions | and | contended | workloads. | With |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ------------ | --- | --------- | ---------- | ---- |
Aria’sthroughputdecreaseswithlargerepochsizesunder
|               |     |                                         |     |     |     |     | in-memory | databases |     | increasingly | being | used | for applica- |
| ------------- | --- | --------------------------------------- | --- | --- | --- | --- | --------- | --------- | --- | ------------ | ----- | ---- | ------------ |
| lowcontention |     | becausemoretransactionsaredeterministi- |     |     |     |     |           |           |     |              |       |      |              |
tionsrequiringhigh-throughputtransactionprocessing,sev-
cally aborted. However,Aria benefits from a larger epoch eralmulti-versionschemeshavebeenproposedforin-memory
sizeunderhighcontention.Inthiscase,Aria’sdeterministic
databases.However,theseschemeshavesignificantcostsas-
schedulingmechanismabortsamajorityoftransactions.The
sociatedwithversionsearchandstorage,garbagecollection,
abortedtransactionsarererunusingthedeterministiclocking
indexmanagement.
fallbackstrategy,whichismoreefficientatlargerepochsizes.
|     |     |     |     |     |     |     | This | work | proposes | a novel | design | for multi-versioning |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | ---- | -------- | ------- | ------ | -------------------- | --- |
Overall,Epicachievescomparablelatencytoothersystems
thattakesadvantageofthepredeterminedorderingoftrans-
| at small | epoch | sizes. | Epic | has higher | latency than | GaccO |     |     |     |     |     |     |     |
| -------- | ----- | ------ | ---- | ---------- | ------------ | ----- | --- | --- | --- | --- | --- | --- | --- |
actionsandknownread-writesetsindeterministicdatabases
atsmallepochsizesbecauseitsmulti-versioninitialization
toeliminateversionsearchbyefficientlypre-calculatingthe
phaseisslowerandthesmallepochsizedoesnotallowitto
versionlocationofeachread/writeoperation.Ourbatching
amortizethisoverhead.However,beyondroughly2msaver-
designhelpsreduceversionallocation,garbagecollectionand
agetransactionlatency,Epicoutperformsallothersystems.
indexingoverheadsaswell.Ourdesignisparallelizableand
soweexploreacceleratingtransactionprocessingonGPUs.
5.8 ImpactofAborts
Ourevaluationshowsthatourmulti-versioned,GPUdatabase
performswellunderbothlowandhighcontentionworkloads
ToevaluatetheimpactofabortsonEpic’sperformance,we andsignificantlyoutperformsstate-of-the-artsystems.
runamicro-benchmarkwhereeachtransactionreadsandup-
dates10records.ThekeysaregeneratedusingaZipfiandis-
tributionwithθ=0.8formediumcontention.Transactions
Acknowledgments
| abort | when | the read-set | or  | the write-set | is predicted | incor- |     |     |     |     |     |     |     |
| ----- | ---- | ------------ | --- | ------------- | ------------ | ------ | --- | --- | --- | --- | --- | --- | --- |
rectly,andabortedtransactionsarereruninthenextepoch.
Wevarytheabortratefortheexperiments.Weassumethatthe We thank ourshepherd,Eddie Kohler,and the anonymous
read-setandwrite-setareknownafteratransactionexecutes, reviewersfortheirvaluablefeedback.
778    18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| References |           |        |                |             | andMikeZwilling.     |     | Hekaton:SQLServer’sMemory- |                            |     |     |
| ---------- | --------- | ------ | -------------- | ----------- | -------------------- | --- | -------------------------- | -------------------------- | --- | --- |
|            |           |        |                |             | OptimizedOLTPEngine. |     |                            | InProceedingsoftheInterna- |     |     |
| [1] Saman  | Ashkiani, | Martin | Farach-Colton, | and John D. |                      |     |                            |                            |     |     |
tionalConferenceonManagementofData-SIGMOD,
Owens. ADynamicHashTablefortheGPU. In2018 pages1243–1254.ACM,2013.
IEEEInternationalParallelandDistributedProcessing
Symposium(IPDPS),pages419–429,May2018. [11] JoseM.FaleiroandDanielJ.Abadi. Rethinkingserial-
|     |     |     |     |     | izablemultiversionconcurrencycontrol. |     |     |     |     | Proceedings |
| --- | --- | --- | --- | --- | ------------------------------------- | --- | --- | --- | --- | ----------- |
[2] MuhammadA.Awad,SamanAshkiani,RobJohnson, oftheVLDBEndowment,8(11):1190–1201,July2015.
| MartínFarach-Colton,andJohnD.Owens. |     |     |     | Engineering |     |     |     |     |     |     |
| ----------------------------------- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- |
a high-performance GPU B-tree. In Proceedings of [12] JoseM.Faleiro,DanielJ.Abadi,andJosephM.Heller-
stein.Highperformancetransactionsviaearlywritevisi-
the24thACMSIGPLANSymposiumonPrinciplesand
PracticeofParallelProgramming,PPoPP2019,pages bility.ProceedingsoftheVLDBEndowment,10(5):613–
624,January2017.
145–157,February2019.
|     |     |     |     |     | [13] Bingsheng | He  | and Jeffrey | Xu  | Yu. High-throughput |     |
| --- | --- | --- | --- | --- | -------------- | --- | ----------- | --- | ------------------- | --- |
[3] MuhammadA.Awad,SamanAshkiani,RobJohnson,
MartínFarach-Colton,andJohnD.Owens. Engineering transactionexecutionsongraphicsprocessors. Proceed-
ahigh-performanceGPUB-Tree. InProceedingsofthe ingsoftheVLDBEndowment,4(5):314–325,February
2011.
24thSymposiumonPrinciplesandPracticeofParallel
Programming,PPoPP’19,pages145–157,NewYork,
|     |     |     |     |     | [14] Yihe Huang, | William |     | Qian, | Eddie Kohler, | Barbara |
| --- | --- | --- | --- | --- | ---------------- | ------- | --- | ----- | ------------- | ------- |
NY,USA,February2019.AssociationforComputing
|     |     |     |     |     | Liskov,andLiubaShrira. |     |     | Opportunitiesforoptimism |     |     |
| --- | --- | --- | --- | --- | ---------------------- | --- | --- | ------------------------ | --- | --- |
Machinery.
|     |     |     |     |     | incontendedmain-memorymulticoretransactions. |     |     |     |     | The |
| --- | --- | --- | --- | --- | -------------------------------------------- | --- | --- | --- | --- | --- |
[4] Muhammad A. Awad, Serban D. Porumbescu, and VLDBJournal,January2022.
| JohnD.Owens. |     | AGPUmultiversionB-tree. |     | InPro- |     |     |     |     |     |     |
| ------------ | --- | ----------------------- | --- | ------ | --- | --- | --- | --- | --- | --- |
[15] KangnyeonKim,TianzhengWang,RyanJohnson,and
| ceedings | of the International |     | Conference | on Parallel |                   |     |        |                      |     |     |
| -------- | -------------------- | --- | ---------- | ----------- | ----------------- | --- | ------ | -------------------- | --- | --- |
|          |                      |     |            |             | IppokratisPandis. |     | ERMIA: | FastMemory-Optimized |     |     |
ArchitecturesandCompilationTechniques,PACT2022,
InPro-
DatabaseSystemforHeterogeneousWorkloads.
October2022.
ceedingsofthe2016InternationalConferenceonMan-
agementofData,SIGMOD’16,pages1675–1687,New
| [5] Hal Berenson, | Phil | Bernstein, | Jim Gray, | Jim Melton, |     |     |     |     |     |     |
| ----------------- | ---- | ---------- | --------- | ----------- | --- | --- | --- | --- | --- | --- |
Elizabeth O’Neil, and Patrick O’Neil. A critique of York,NY,USA,June2016.AssociationforComputing
Machinery.
| ANSI SQL | isolation | levels. | ACM SIGMOD | Record, |     |     |     |     |     |     |
| -------- | --------- | ------- | ---------- | ------- | --- | --- | --- | --- | --- | --- |
24(2):1–10,1995.
[16] Per-ÅkeLarson,SpyrosBlanas,CristianDiaconu,Craig
[6] NilsBoeschenandCarstenBinnig. GaccO-AGPU- Freedman,JigneshM.Patel,andMikeZwilling. High-
InProceedingsofthe2022 performanceconcurrencycontrolmechanismsformain-
acceleratedOLTPDBMS.
|     |     |     |     |     | memorydatabases. |     | ProceedingsoftheVLDBEndow- |     |     |     |
| --- | --- | --- | --- | --- | ---------------- | --- | -------------------------- | --- | --- | --- |
InternationalConferenceonManagementofData,SIG-
MOD’22,pages1003–1016,NewYork,NY,USA,June ment,5(4):298–309,December2011.
2022.AssociationforComputingMachinery.
[17] HyeontaekLim,MichaelKaminsky,andDavidG.An-
|                                              |     |     |     |     | dersen. | Cicada: | Dependably |     | Fast Multi-Core | In- |
| -------------------------------------------- | --- | --- | --- | --- | ------- | ------- | ---------- | --- | --------------- | --- |
| [7] MichaelJ.Cahill,UweRöhm,andAlanD.Fekete. |     |     |     | Se- |         |         |            |     |                 |     |
rializableisolationforsnapshotdatabases. ACMTrans. MemoryTransactions. InProceedingsofthe2017ACM
InternationalConferenceonManagementofData,SIG-
DatabaseSyst.,34(4),dec2009.
MOD’17,pages21–35,NewYork,NY,USA,May2017.
[8] MichaelJ.CareyandWaleedA.Muhanna. Theperfor- AssociationforComputingMachinery.
manceofmultiversionconcurrencycontrolalgorithms.
ACMTransactionsonComputerSystems,4(4):338–378, [18] Yu-ShanLin,Shao-KanPi,Meng-KaiLiao,ChingTsai,
|     |     |     |     |     | AaronElmore,andShan-HungWu. |     |     |     | Mgcrab:Transac- |     |
| --- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | --------------- | --- |
September1986.
tioncrabbingforlivemigrationindeterministicdatabase
[9] BrianF.Cooper,AdamSilberstein,ErwinTam,Raghu systems. Proc.VLDBEndow.,12(5):597–610,jan2019.
| Ramakrishnan,andRussellSears. |     |     | Benchmarkingcloud |     |     |     |     |     |     |     |
| ----------------------------- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- | --- |
[19] Yu-ShanLin,ChingTsai,Tz-YuLin,Yun-ShengChang,
| servingsystemswithYCSB. |     |     | InProceedingsofthe1st |     |               |     |           |      |            |          |
| ----------------------- | --- | --- | --------------------- | --- | ------------- | --- | --------- | ---- | ---------- | -------- |
|                         |     |     |                       |     | and Shan-Hung |     | Wu. Don’t | look | back, look | into the |
ACMSymposiumonCloudComputing,SoCC’10,pages
future:Prescientdatapartitioningandmigrationforde-
143–154,NewYork,NY,USA,June2010.Association
|     |     |     |     |     | terministic | database | systems. |     | In Proceedings | of the |
| --- | --- | --- | --- | --- | ----------- | -------- | -------- | --- | -------------- | ------ |
forComputingMachinery.
2021InternationalConferenceonManagementofData,
[10] CristianDiaconu,CraigFreedman,ErikIsmert,Per-Ake SIGMOD’21,page1156–1168,NewYork,NY,USA,
Larson,PravinMittal,RyanStonecipher,NitinVerma, 2021.AssociationforComputingMachinery.
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation    779

[20] DavidLomet,AlanFekete,RuiWang,andPeterWard. [32] Mohammad Sadoghi, Mustafa Canim, Bishwaranjan
Multi-versionConcurrencyviaTimestampRangeCon- Bhattacharjee, Fabian Nagel, and Kenneth A. Ross.
flict Management. In 2012 IEEE 28th International Reducing database locking contention through multi-
ConferenceonDataEngineering,pages714–725,April versionconcurrency. ProceedingsoftheVLDBEndow-
| 2012. |     |     |     |     |     |     | ment,7(13):1331–1342,August2014. |     |     |     |     |     |     |     |
| ----- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | --- | --- | --- | --- | --- |
[21] YiLu,XiangyaoYu,LeiCao,andSamuelMadden.Aria:
|                                             |     |     |     |     |     |      | [33] Weihai | Shen, | Ansh | Khanna, | Sebastian |     | Angel, | Sid- |
| ------------------------------------------- | --- | --- | --- | --- | --- | ---- | ----------- | ----- | ---- | ------- | --------- | --- | ------ | ---- |
| AfastandpracticaldeterministicOLTPdatabase. |     |     |     |     |     | Pro- |             |       |      |         |           |     |        |      |
ceedingsoftheVLDBEndowment,13(12):2047–2060, dharthaSen,andShuaiMu. Rolis:asoftwareapproach
July2020. toefficientlyreplicatingmulti-coretransactions. InPro-
|     |     |     |     |     |     |     | ceedings | ofthe | SeventeenthEuropean |     |     | Conference |     | on  |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----- | ------------------- | --- | --- | ---------- | --- | --- |
[22] ThomasNeumann,TobiasMühlbauer,andAlfonsKem-
ComputerSystems,pages69–84,2022.
per. FastSerializableMulti-VersionConcurrencyCon-
| trolforMain-MemoryDatabaseSystems. |     |     |     |     | InProceed- |     |     |     |     |     |     |     |     |     |
| ---------------------------------- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ingsofthe2015ACMSIGMODInternationalConfer- [34] VishalSikka,FranzFärber,andWolfgangLehner. Ef-
ficienttransactionprocessinginSAPHANAdatabase:
enceonManagementofData,SIGMOD’15,pages677–
689,NewYork,NY,USA,May2015.Associationfor The end of a column store myth. In Proceedings of
ComputingMachinery. the2012ACMSIGMODInternationalConferenceon
ManagementofData,2012.
| [23] Nvidia. | Cucollection. |     | https://github.com/NVIDIA/ |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | ------------- | --- | -------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
cuCollections,2023.
|              |     |          |           |     |          |      | [35] Alexander |     | Thomson, | Thaddeus     |     | Diamond, | Shu-Chun |        |
| ------------ | --- | -------- | --------- | --- | -------- | ---- | -------------- | --- | -------- | ------------ | --- | -------- | -------- | ------ |
| [24] Oracle. |     | TimesTen | In-Memory |     | Database | FAQ. |                |     |          |              |     |          |          |        |
|              |     |          |           |     |          |      | Weng,          | Kun | Ren,     | Philip Shao, | and | Daniel   | J.       | Abadi. |
https://www.oracle.com/database/technologies/timesten- Calvin: Fast distributed transactions for partitioned
faq.html,2021. database systems. In Proceedings of the 2012 ACM
SIGMODInternationalConferenceonManagementof
| [25] Dan | R. K. | Ports | and Kevin | Grittner. | Serializable |     |     |     |     |     |     |     |     |     |
| -------- | ----- | ----- | --------- | --------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Data,SIGMOD’12,pages1–12,NewYork,NY,USA,
| snapshotisolationinpostgresql. |     |     |     | Proc.VLDBEndow., |     |     |     |     |     |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
May2012.AssociationforComputingMachinery.
5(12):1850–1861,aug2012.
| [26] ThamirM.QadahandMohammadSadoghi. |     |     |     |     |     | Quecc:A |              |     |         |        |       |         |         |     |
| ------------------------------------- | --- | --- | --- | --- | --- | ------- | ------------ | --- | ------- | ------ | ----- | ------- | ------- | --- |
|                                       |     |     |     |     |     |         | [36] Stephen | Tu, | Wenting | Zheng, | Eddie | Kohler, | Barbara |     |
queue-oriented,control-freeconcurrencyarchitecture.
|                       |     |     |                        |           |            |       | Liskov,and |           | Samuel | Madden.    | Speedy | transactions   |     | in  |
| --------------------- | --- | --- | ---------------------- | --------- | ---------- | ----- | ---------- | --------- | ------ | ---------- | ------ | -------------- | --- | --- |
| In Proceedings        |     | of  | the 19th International |           | Middleware |       |            |           |        |            |        |                |     |     |
|                       |     |     |                        |           |            |       | multicore  | in-memory |        | databases. |        | In Proceedings |     | of  |
| Conference,Middleware |     |     | ’18,page               | 13–25,New |            | York, |            |           |        |            |        |                |     |     |
theTwenty-FourthACMSymposiumonOperatingSys-
NY,USA,2018.AssociationforComputingMachinery.
|     |     |     |     |     |     |     | tems | Principles, | SOSP | ’13, | pages | 18–32, | New | York, |
| --- | --- | --- | --- | --- | --- | --- | ---- | ----------- | ---- | ---- | ----- | ------ | --- | ----- |
[27] DaiQin,AngelaDemkeBrown,andAshvinGoel. Scal- NY,USA,November2013.AssociationforComputing
| able | replay-based | replication |     | for fast | databases. | Pro- | Machinery. |     |     |     |     |     |     |     |
| ---- | ------------ | ----------- | --- | -------- | ---------- | ---- | ---------- | --- | --- | --- | --- | --- | --- | --- |
ceedingsoftheVLDBEndowment,10(13):2025–2036,
September2017.
[37] YingjunWu,JoyArulraj,JiexiLin,RanXian,andAn-
|                                             |     |     |     |     |     |       | drew | Pavlo. | An  | empirical | evaluation |     | of in-memory |     |
| ------------------------------------------- | --- | --- | --- | --- | --- | ----- | ---- | ------ | --- | --------- | ---------- | --- | ------------ | --- |
| [28] DaiQin,AngelaDemkeBrown,andAshvinGoel. |     |     |     |     |     | Cara- |      |        |     |           |            |     |              |     |
cal:ContentionManagementwithDeterministicConcur- multi-versionconcurrencycontrol. Proc.VLDBEndow.,
10(7):781–792,mar2017.
rencyControl.InProceedingsoftheACMSIGOPS28th
SymposiumonOperatingSystemsPrinciples,SOSP’21,
| pages | 180–194, | New | York, | NY, USA, | October | 2021. |     |     |     |     |     |     |     |     |
| ----- | -------- | --- | ----- | -------- | ------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
[38] XiangyaoYu,AndrewPavlo,DanielSanchez,andSrini-
AssociationforComputingMachinery. vasDevadas. TicToc:TimeTravelingOptimisticCon-
|                |     |                                       |     |     |     |     | currencyControl. |     |     | InProceedingsofthe2016Interna- |     |     |     |     |
| -------------- | --- | ------------------------------------- | --- | --- | --- | --- | ---------------- | --- | --- | ------------------------------ | --- | --- | --- | --- |
| [29] D.P.Reed. |     | Namingandsynchronizationinadecentral- |     |     |     |     |                  |     |     |                                |     |     |     |     |
tionalConferenceonManagementofData,SIGMOD
| izedcomputersystem. |     |     | Technicalreport,Massachusetts |     |     |     |     |     |     |     |     |     |     |     |
| ------------------- | --- | --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
InstituteofTechnology,1978. ’16,pages1629–1642,NewYork,NY,USA,June2016.
AssociationforComputingMachinery.
| [30] DavidP.Reed. |     | Implementingatomicactionsondecen-   |     |     |     |     |     |     |     |     |     |     |     |     |
| ----------------- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tralizeddata.     |     | ACMTrans.Comput.Syst.,1(1):3–23,feb |     |     |     |     |     |     |     |     |     |     |     |     |
[39] KaiZhang,KaiboWang,YuanYuan,LeiGuo,Rubao
1983.
|     |     |     |     |     |     |     | Lee, | and Xiaodong |     | Zhang. | Mega-KV: |     | A case | for |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------------ | --- | ------ | -------- | --- | ------ | --- |
[31] KunRen,DennisLi,andDanielJ.Abadi. Slog:Serial- GPUstomaximizethethroughputofin-memorykey-
izable,low-latency,geo-replicatedtransactions. Proc. value stores. Proceedings of the VLDB Endowment,
VLDBEndow.,12(11):1747–1761,jul2019. 8(11):1226–1237,July2015.
780    18th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

A ArtifactAppendix Requirements
Ourexperimentsrequirerunningonserversequippedwith
Abstract
GPUs.WeusedFluidStacktohoston-demandvirtualGPU
WeimplementEpic,thefirstmulti-versionedGPU-basedde- servers.Ourartifactrepositorycontainsinstructionsonhow
terministic OLTP database. Epic batches transactions into tosetupthevirtualserversandruntheexperiments.
epochsandestablishesaserialorderingoftransactionswithin Alternatively,theexperimentscanberunonmachineswith
abatchbeforetransactionexecution.Epicperformsconcur- NVIDIAGPUs.Theartifactrepositoryistestedformachines
rencycontrolinitializationforabatchoftransactionsbefore withmorethan32CPUcores,128GBofRAM,andNVIDIA
execution,avoidingversionsearchandreducingversional- GPUsofcomputecapability8.6andGPUmemoryof48GB.
locationandgarbagecollectionoverheads.Epicrunsonthe Theartifactrepositorycontainsscriptstoinstallthenecessary
GPUtoaccelerateconcurrencycontrolinitializationandpar- dependenciesandruntheexperiments.
allelizebatchedtransactionexecution.Inaddition,Epicsup-
portslargerdatasetswithaCPUexecutionmodel.Weevaluate
EpicusingtheTPC-CandYCSBbenchmarksandcompare
itwithstate-of-the-artsystems:STOv2,Caracal,Gacco,and
Aria.
Scope
Theartifactallowsreproductionoftheresultsofthepaper,in-
cludingtheperformanceevaluationofEpicusingtheTPC-C
andYCSBbenchmarks,thelatencyandthroughputcompar-
ison,and the performance evaluation of Epic with varying
abortrates.
AlltheexperimentsexcepttheruntimebreakdowninFig-
ure9canbereproducedusingtheartifact.Theruntimebreak-
downiscreatedbyretrievingtheruntimeinformationmanu-
ally,andwedonothaveascripttoautomatethisprocess.
Additionally,theartifactcannotperformtheperformance
evaluationforAriaduetotheconflictofdependencies.There-
fore,theAriaresultsinFigure5andFigure7arenotrepro-
ducibleusingtheartifact.
Contents
The artifact repository contains the source code of Epic,
STOv2,and Caracal as separate submodules. We used our
best-effortimplementationofGacco,andthesourcecodeisin-
cludedintheEpicsubmodule.Therepositorycontainsscripts
toruntheexperimentsandgeneratethefiguresinthepaper.
Therepositoryalsocontainsscriptstoinstallthenecessary
dependencies and set up the experiment environment. The
READMEfileintherepositoryprovidesdetailedinstructions
onhowtoruntheartifact.
Hosting
Our artifact repository is hosted on GitHub at https:
//github.com/ShujianQian/epic-artifact/commit/
9303f4d2b1fa8368de0dbdc24bcd798585ceb920.
Moredetailsonhowtosetuptheexperimentenvironment,
runtheexperiments,andreproducetheresultsareprovided
intheREADMEfileintherepository.
USENIX Association 18th USENIX Symposium on Operating Systems Design and Implementation 781