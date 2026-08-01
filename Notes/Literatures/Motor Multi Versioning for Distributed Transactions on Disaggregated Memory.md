# Motor Multi Versioning for Distributed Transactions on Disaggregated Memory

**Source**: Motor Multi Versioning for Distributed Transactions on Disaggregated Memory.pdf
**Format**: .pdf

---

Motor: Enabling Multi-Versioning for Distributed
Transactions on Disaggregated Memory
Ming Zhang, Yu Hua, and Zhijun Yang, Wuhan National Laboratory for
Optoelectronics, School of Computer, Huazhong University of Science and Technology
https://www.usenix.org/conference/osdi24/presentation/zhang-ming
This paper is included in the Proceedings of the
18th USENIX Symposium on Operating Systems
Design and Implementation.
July 10–12, 2024 • Santa Clara, CA, USA
978-1-939133-40-3
Open access to the Proceedings of the
18th USENIX Symposium on Operating
Systems Design and Implementation
is sponsored by

Motor: Enabling Multi-Versioning for Distributed Transactions on
Disaggregated Memory
MingZhang,YuHua*,ZhijunYang
WuhanNationalLaboratoryforOptoelectronics,SchoolofComputer
HuazhongUniversityofScienceandTechnology
*CorrespondingAuthor:YuHua(csyhua@hust.edu.cn)
Abstract computeunitsonlyformemoryallocationsandnetworkin-
terconnections [84,86]. With the aid of efficient resource
In modern datacenters, memory disaggregation unpacks
pooling,memorydisaggregationsignificantlyimprovesthe
monolithic servers to build network-connected distributed
resourceutilization,elasticity,andfailureisolation[65,72].
computeandmemorypoolstoimproveresourceutilization
anddeliverhighperformance.Thecomputepoolleverages Toprovideatomicityandstrongconsistencyguaranteesfor
distributed transactions to access remote data in the mem- applicationsonthedisaggregatedmemory,thecomputepool
ory pool to provide atomicity and strong consistency. Ex- leveragesdistributedtransactionstoaccessremotedatainthe
istingsingle-versioningdesignshavebeenconstraineddue memory pool. A recent design,i.e.,FORD [84],is able to
tolimitedsystemconcurrencyandhighloggingoverheads. rundistributedtransactionsonthedisaggregatedmemory.To
Although the multi-versioning design in the conventional simplifythedatastoreinthememorypool,FORDmaintains
monolithicserversispromisingtoofferhighconcurrencyand one version of each data. However, this single-versioning
reduceloggingoverheads,whichhoweverfailstoworkinthe design limits the concurrency since the reads need to wait
disaggregatedmemory.Inordertobridgethegapbetweenthe forthewritestobecomevisibleduringtransactioncommit.
multi-versioningdesignandthedisaggregatedmemory,we Moreover,toguaranteeatomicity,FORDwritesmanyundo
proposeMotorthatholisticallyredesignstheversionstruc- logs to back up the old data,which consumes the network
tureandtransactionprotocoltoenablemulti-versioningfor bandwidthanddecreasesthroughput.
fastdistributedtransactionprocessingonthedisaggregated Enablingmulti-versioningisexpectedtoefficientlyaddress
memory.Toefficientlyorganizedifferentversionsofdatain theabovelimitations.Bystoringmultipleversionsofeach
the memory pool,Motor leverages a new consecutive ver- datainthememorypool,thereadrequestsareabletofetch
siontuple(CVT)structuretostoretheversionstogetherina existingversionsofdataratherthanwaitingforthewritesto
continuousmanner,whichallowsthecomputepooltoobtain complete,thusimprovingtheconcurrency.Moreover,with
thetargetversioninasinglenetworkroundtrip.Ontopof multi-versioning,theoldversionsofdataareretainedtopro-
CVT,Motorleveragesafullyone-sidedRDMA-basedMVCC videtheatomicity,thuseliminatingtheneedofwritingundo
protocoltosupportfastdistributedtransactionswithflexible logs.Priormulti-versioningbaseddistributedtransactionpro-
isolationlevels.ExperimentalresultsdemonstratethatMotor cessingsystemshavebeenproposedinthetraditionalmono-
improvesthethroughputbyupto98.1%andreducesthela- lithicarchitecture[57,64,76].Unfortunately,thesesystems
tencybyupto55.8%comparedwithstate-of-the-artsystems. aredifficulttoworkonthenewdisaggregatedmemoryarchi-
tectureduetotwochallenges,aspresentedbelow.
1 Introduction
1) Incompatible Transaction Protocol. Prior systems
Memorydisaggregationinmoderndatacentersreceivesex- workingonmonolithicarchitectureassumethateachserver
tensiveattentions[2,3,35,46,53,62].Specifically,memory hasstrongCPUstoexecutecomputetasksinthetransaction
disaggregationdecouplesthecomputeandmemoryresources protocol,e.g.,locking[64],validation[57],andtimestamp
fromtraditionalmonolithicserverstobuildindependentand calculation [76]. In general, a single task is not computa-
scalable compute andmemorypools. These pools are con- tionallyexpensive. However,whenthenumberofrequests
nected via fast network (e.g.,RDMA [75] or CXL [7]). A increases,thesetasksbecomesubstantialandfrequent.The
computepoolcontainsmanypowerfulcomputeunitstorun CPUinamemorypoolistooweaktofrequentlypollmassive
tasksandsmallDRAM-basedmemorytomaintainmetadata. tasksandexecutethem[45,46,66,69,75,84,86].Therefore,
Moreover, a memory pool consists of substantial memory legacymulti-versioningbasedtransactionprotocolsarenot
modulestostoreapplicationdataandasmallnumberofweak compatiblewiththedisaggregatedmemorypool.
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation 801

s
t
th
u
io
i
r
2
s
e
n
)
s
p
s
a
I
t
o
o
n
p
f
e
e
d
d
r
f
y
.
a
fi
n
I
t
c
n
a
a
i
,
m
e
g
e
n
e
i
x
c
t
n
i
a
e
s
V
l
r
t
l
i
a
e
y
n
l
r
,
g
l
s
i
t
i
n
h
s
o
k
c
e
n
h
r
t
e
e
h
S
m
e
a
t
r
r
v
e
e
u
e
s
t
c
r
w
l
s
t
e
i
u
o
v
o
r
e
n
t
e
r
y
s
a
.
,
p
g
T
c
e
e
a
s
o
l
p
o
l
s
e
o
f
t
d
o
i
t
n
h
r
l
t
e
i
e
e
n
r
l
d
k
-
i
e
i
n
b
f
d
k
a
fe
e
s
c
r
e
d
h
e
d
a
c
n
i
h
s
t
n
t
a
r
v
s
i
u
e
n
i
c
r
n
s
-
-
.
Key V
V
V
V
a
a
a
a
l
l
l
l
u
u
u
u
e
e
e
e
V
V
V
V
e
e
e
e
r
r
r
r
s
s
s
s
i
i
i
i
o
o
o
o
n
n
n
n
(
(
(
(
1
2
4
3
)
)
)
)
P
P
P
P
t
t
t
t
r
r
r
r
Key V
V
V
V
a
a
a
a
l
l
l
l
u
u
u
u
e
e
e
e
V
V
V
V
e
e
e
e
r
r
r
r
s
s
s
s
i
i
i
i
o
o
o
o
n
n
n
n
(
(
(
(
4
3
1
2
)
)
)
)
P
P
P
P
t
t
t
t
r
r
r
r
)sµ(
ycnetal
daeR
2
4
6
8
0
0
0
0
0
The 2 num 4 be 6 r o 8 f st 1 e 0 ps 1 i 2 n c 1 h 4 ai 1 n 6 w 1 a 8 lki 2 n 0 g
(a) Old-to-new chain (b) New-to-old chain (c) Read latency of different walk steps
(1)Theold-to-newchainlinkstheversionsfromtheoldest
Figure1:Thelinkedchainbasedversionstructures(a,b),and
tothenewestversion[10,25,38,76],asshowninFig.1a.(2)
thelatencyofusingRDMAREADforchainwalking(c).
Thenew-to-oldchainlinkstheversionsfromthenewesttothe
oldestversion[9,32,57,64,81],asshowninFig.1b.Toreada bandwidth.Moreover,ourprotocolsupportsvariousisolation
specificversion,CPUperformschainwalkingthatleverages levels(e.g.,serializabilityandsnapshotisolation)toflexibly
thepointerstofetchtheversionsonebyoneuntilthetarget meettherequirementsofdifferentOLTPapplications.
version. In fact,the linked chains work well in monolithic Insummary,thispapermakesthefollowingcontributions:
servers,sinceeachservercontainsenoughCPUstoquickly • WeproposeMotorthatenablesmulti-versioningfordis-
perform chain walking in its local memory. However, the tributedtransactionsonthedisaggregatedmemory.
linkedchainsbecomeinefficientin disaggregatedmemory, • Motordesigns a new consecutive version tuple (CVT)
sincealltheapplicationdataarestoredintheremotememory structuretoefficientlyorganizemultipleversionsofdatain
pool,whichdoesnotcontainpowerfulCPUtoexecutethe thememorypool.CVTenablesthecomputepooltoobtain
chainwalking.Asaresult,thecomputepoolhastoperform thetargetversioninoneroundtrip,andprovideslightweight
thechainwalkingbyconsumingmultiplenetworkroundtrips garbagecollectionwithouttheoverheadoftracking(§4).
to fetch remote versions one after another until the target • MotorleveragesafastMVCCtransactionprotocolthat
version,leadingtohighoverheads.Fig.1cshowsthatwhen fullyexploitsone-sidedRDMAandCVTtomeettheCPU-
increasingthenumberofstepsinthechainwalkingfrom1to lessmemorypoolwithvariousisolation-levelsupports(§5).
20,theRDMAreadlatencysignificantlyincreasesby24.8× • Weimplement1Motorandcompareitwithtwostate-of-
inourtestbed(§7.1).Moreover,topreventlongchains,the the-artsystems[64,84].Theexperimentalresultsdemonstrate
garbage collection (GC) is required to delete the obsolete thatMotorsignificantlyimprovesthetransactionthroughput
versionsthatarenolongerusedbyanytransaction[16].How- byupto98.1%andreducesthelatencybyupto55.8%.
ever,whenusinglinkedchains,GCisdifficulttocarryout
2 BackgroundandMotivation
ondisaggregatedmemory,sincethecomputepoolneedsto
frequently track the oldest transaction and reclaim the un- 2.1 MemoryDisaggregation
usedversions.Suchtrackingconsumesmanyroundtripsfor
Traditionaldatacentersconsistofmanymonolithicservers,
synchronizationsandwastesthecomputepower.
eachofwhichcontainsasetofcomputeandmemoryunits.
Toaddresstheabovechallenges,weproposeMotor,which
However,this monolithic architecture suffers from low re-
holistically redesigns the version structure and transaction
sourceutilizationandcoarsefailuredomain[65,72].Specif-
protocoltoenablemulti-versioningfordistributedtransaction
ically, even if a user only needs more compute power, we
processing on the disaggregatedmemory. Insteadofusing
havetoaddmoreentireserversinwhichthememorymodules
linked chains, Motor leverages a new consecutive version
arewasted.Moreover,ifaCPUisbroken,thewholeserver
tuple(CVT)structuretoefficientlyorganizemultipleversions
becomesunusable,whichexpandsthefailuredomain.
ofonedatainthememorypool.CVTconsecutivelystores
Toimproveresourceutilizationandfailureisolation,mem-
severalversionstogethertofillincontinuousaddressspace.In
orydisaggregation[20,35,46,50,51]becomesapromising
thisway,thecomputepoolisabletofetchalltheversionsof
solution,whichdecouplesthecomputeandmemoryresources
thesamedatabyreadingaCVTinasingleroundtrip,instead
from a monolithic server to build separate resource pools.
offetchingtheremoteversionsonebyone,thusreducingthe
Thesepoolsareconnectedviafastnetwork,e.g.,RDMA[29]
networkingoverheadstoachievelowlatency.WhentheCVT
orCXL[7].AcomputepoolcontainsmanystrongCPUsto
isfilledup,Motorleveragesalightweightcoordinator-active
intensivelyexecutecomputingtasks.Therearesmallamounts
garbagecollection(GC)schemethatreclaimstheoldversions
ofDRAMinthecomputepooltocachesomemetadata.More-
inapreemptivemannerwithouttracingtransactionstates.In
over,amemorypoolconsistsofsubstantialmemorymodules
thepresenceofGC,Motoralsoenablestheapplicationsto
tostorethelarge-volumeapplicationdata.Thememorypool
easilyidentifytheconsistencybetweenthedatavalueandits
doesnotcontainstrongcomputecapability[46,65,69,72,75],
versioninCVTtoguaranteethecorrectness.
but have some low-power compute units only for memory
OntopoftheCVTstructure,Motordesignsafastmulti-
allocationandnetworkinterconnection[84,86].Byefficient
versionconcurrencycontrol(MVCC)basedtransactionproto-
resourcepooling,datacentersareabletoprovideappropriate
col.Thisprotocolfullyleveragesone-sidedRDMAtobypass
amountsofcomputeandmemoryunitstomeettherequire-
the weakcompute units in the memorypool. Ourprotocol
mentsofdifferentapplicationsinanon-demandmanner,thus
allowsthereadsnottobeblockedbywrites,andavoidswrit-
inglogs,thusimprovingtheconcurrencyandsavingnetwork 1Sourcecodeisavailableathttps://github.com/minghust/motor.
802 17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Clients
| improving | the resource |     | utilization | andreducing |     | costs [48]. |                     |     |     |     |            |
| --------- | ------------ | --- | ----------- | ----------- | --- | ----------- | ------------------- | --- | --- | --- | ---------- |
|           |              |     |             |             |     |             | ❸Issue txn requests |     |     |     | ❶Load data |
Moreover,evenifaCPUfailsinthecomputepool,thedecou- App App App App
pledmemorymodulesinthememorypoolarenotaffected
due to the separate architecture,thus narrowing the failure Coordinators ❷RDMA connect DB Tables
| domain. | Therefore,memory |     | disaggregation |     |     | is a promising |     |              |     |              |     |
| ------- | ---------------- | --- | -------------- | --- | --- | -------------- | --- | ------------ | --- | ------------ | --- |
|         |                  |     |                |     |     |                |     | Txn Protocol |     | Memory Store |     |
solutionformoderndatacentersandcloudproviders.Without One-sided RDMA
❹Execute,
lossofgenerality,thispaperconsidersthatthecomputepool READ/WRITE/CAS
|     |     |     |     |     |     |     |     | Commit/Abort |     |     | Indexes |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- | ------- |
READ,WRITE,
| leverages   | one-sided | RDMA   | verbs   | (including |        |                 |     |              |     |     |             |
| ----------- | --------- | ------ | ------- | ---------- | ------ | --------------- | --- | ------------ | --- | --- | ----------- |
|             |           |        |         |            |        |                 |     | Compute Pool |     |     | Memory Pool |
| and atomics | such      | as CAS | an FAA) | to         | access | the application |     |              |     |     |             |
datainthememorypooltobypassremoteCPUslikeexisting Figure2:ThesystemoverviewofMotor.
studies[53,66,75,84]. block reads,since the read request obtains an existing ver-
2.2 TransactionsonDisaggregatedMemory sionofdata,insteadofwaitingfortheupdateoperation,thus
improvingtheconcurrency.Moreover,themulti-versioning
SystemModel.Toprovideatomicityandstrongconsistency
|     |     |     |     |     |     |     | design does | not need to | additionally | write | logs to back up |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ----------- | ------------ | ----- | --------------- |
forapplicationsonthedisaggregatedmemory,thecompute
datainreplicas,sincetheoldversionsnaturallyactas“undo
poolisrequiredtoemploydistributedtransactionstoaccess logs” to guarantee atomicity. In this way,we eliminate the
remotedatainthememorypool[84].Specifically,theCPU
loggingoverheadstoacceleratetransactioncommit.
threadsinacomputepoolrunmanycoordinators,whichexe-
Challenges.Existingstudieshaveadoptedmulti-versioning
cuteatransactionprotocoltoreaddata,handleconflicts,and
intransactionprocessing[16,43,57,64,76].However,asan-
| commitupdates. |     | The compute |     | pooldoes | notstore | applica- |     |     |     |     |     |
| -------------- | --- | ----------- | --- | -------- | -------- | -------- | --- | --- | --- | --- | --- |
alyzedin§1,thesestudiesdonotfitthenewdisaggregated
tion data,butcontains a smallamountofDRAM to buffer memoryarchitectureduetotworeasons. (1)Theirtransac-
| some metadata |     | (e.g.,remote | data | addresses). |     | The memory |     |     |     |     |     |
| ------------- | --- | ------------ | ---- | ----------- | --- | ---------- | --- | --- | --- | --- | --- |
tionprotocolstargetontraditionalmonolithicservers,which
poolstoresalltheapplicationdatawithoutrunningcompute
requirespowerfulCPUsineachservertoexecutesubstantial
tasks.Eachdataisreplicatedintomultiplereplicasforhigh
|     |     |     |     |     |     |     | compute | tasks [57,64,76]. | However,in |     | the disaggregated |
| --- | --- | --- | --- | --- | --- | --- | ------- | ----------------- | ---------- | --- | ----------------- |
availability.Inpractice,thefail-stopfailure[36]couldoccur
memoryarchitecture,thecomputeunitsinthememorypool
at any time to cause the data in the memory pool inacces- aretooweaktofrequentlyhandlecomputetasks[75,84,86].
| sible2 [27]. | To tolerate |     | suchfailures,we |     | adoptthe | (f +1)- |     |     |     |     |     |
| ------------ | ----------- | --- | --------------- | --- | -------- | ------- | --- | --- | --- | --- | --- |
(2)Theversionstructuresofnew-to-oldandold-to-newlinked
wayprimary-backupreplication[42]togenerate1primary
chainsincursubstantialRDMAroundtripsforchainwalking
| replica and | f backupreplicas |     |     | foreachdata |     | in the memory |     |     |     |     |     |
| ----------- | ---------------- | --- | --- | ----------- | --- | ------------- | --- | --- | --- | --- | --- |
andhighoverheadsforgarbagecollection.
pool.Eachreplicacanbeaccessedbymultiplecoordinators.
Toaddresstheabovechallenges,weproposeMotortoeffi-
Duringtransactionprocessing,coordinatorsincomputepool
cientlyenablemulti-versioningforfastdistributedtransaction
read/writeremotereplicasvianetworkatthebytegranularity,
processingonthedisaggregatedmemory.
andthecomputeunitsinmemorypoolarenotinvolved.Since
3 MotorOverview
thecoordinatorsandreplicasarefullyseparatedbynetwork,
alltransactionsbecomedistributedinoursystemmodel.
Fig.2illustratesthesystemoverviewofMotor,whichcon-
LimitationsofSingle-Versioning.Recently,FORD[84]sup-
tainstwopartsworkinginharmony.First,theMotormemory
portsdistributedtransactionsonthedisaggregatedmemory
store(§4)efficientlyorganizesmultipleversionsofdatain
andstoresthelatestversionofeachdatainthememorypool.
|     |     |     |     |     |     |     | the memory | pool. Second,the | Motor | transaction | protocol |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ---------------- | ----- | ----------- | -------- |
Thissingle-versioningdesignsimplifiesthememorystorebut
(§5)handlesmulti-versioningbaseddistributedtransactions
incurstwolimitations.(1)Lowconcurrency.Duringtransac-
inthecomputepool.
tioncommit,thedatabeingupdatedcannotberead.FORD
Workflow.WeoutlinetheworkflowofMotor.❶Theclient
| makes these | data | invisible | until | completing |     | the write,thus |     |     |     |     |     |
| ----------- | ---- | --------- | ----- | ---------- | --- | -------------- | --- | --- | --- | --- | --- |
initiallyleveragestheCPUsinthememorypooltoallocate
| blocking | the read | operations; |     | (2) High | logging | overheads. |     |     |     |     |     |
| -------- | -------- | ----------- | --- | -------- | ------- | ---------- | --- | --- | --- | --- | --- |
memorytoloadtheapplicationdataintorelationaldatabase
FORDwritestheundologstoallreplicastoguaranteeatom-
(DB)tables.Thesetablesareorganizedbyourconsecutive
icity.Theseundologsconsumethenetworkbandwidth,and
|                 |     |       |         |         |      |                | version | tuple (CVT) structure, | as  | described | in § 4.1. The |
| --------------- | --- | ----- | ------- | ------- | ---- | -------------- | ------- | ---------------------- | --- | --------- | ------------- |
| the coordinator |     | needs | to wait | for all | ACKs | of the logging |         |                        |     |           |               |
CVTscanbequicklyaccessedusingindexes,e.g.,hashta-
requestsbeforecommittingtheupdatestoremotereplicas. ble[86]orB+tree[75].❷WeestablishRDMAconnections
2.3 EnablingMulti-Versioning betweenthecomputeandmemorypools.Moreover,themem-
orypoolsendssomemetadata(e.g.,theaddressoftheRDMA
Toaddressthelimitationsofsingle-versioning,weadopta
memoryregionanddescriptionsofindexes)tothecompute
multi-versioningmethodologytostoremultipleversionsof
pool.Thesemetadatahelpcoordinatorslocatetheremotedata
eachdatainthememorypool.Bydoingso,thewritesdonot atruntime.❸Theclientsissuetransactionstothecompute
pooltobeexecuted.❹ThecomputepoolusesCPUthreads
2Inlinewithexistingstudies[27,38,39,64,77,84],wecurrentlydonot
tosimultaneouslyrunmanycoordinators,whichleverageour
considerthebyzantinefailures[37].
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation    803

CVT Region
transactionprotocoltoprocesstransactions.Ingeneral,the
A consecutive version tuple (CVT)
coordinatorsfetchandlockremotedata,andthenexecutethe
|     |     |     |     |             | H e a d e r V c e | l l … V c e | l l V c e l l |                       |
| --- | --- | --- | --- | ----------- | ----------------- | ----------- | ------------- | --------------------- |
|     |     |     |     | H e a d e r | 1                 | 1           | n - 1 n       | V e rs i o n  c e l l |
t ra n s a c ti o n lo g i c . A f te r ex e c u t io n , t h e c o o rd i n a t o rs v al i d a t e H e a d e r V c e l l … V c e l l V c e l l
|     |     |     |     | Ta bl e ID   (8 B) | 2   | 1   | n - 1 n | V ce ll S A ( 1 B ) |
| --- | --- | --- | --- | ------------------ | --- | --- | ------- | ------------------- |
th a t t h e d a ta v e r s io n s a re n o t c h a n g e d . F in a ll y , t h e co o r d i n a - … … … … …
|     |     |     |     | K e y   ( 8 B ) |     |     |     | V a l i d  ( 1 B ) |
| --- | --- | --- | --- | --------------- | --- | --- | --- | ------------------ |
torscommittheupdatestoremotememorypoolandunlock Headern Vcell1 … Vcelln-1 Vcelln
|     |     |     |     | L o c k   ( 8 B ) |     |     |     | Ve r s i o n   ( 8B ) |
| --- | --- | --- | --- | ----------------- | --- | --- | --- | --------------------- |
data.Ourprotocolenablescoordinatorstofullyuseone-sided AttrBarPtr (8B) StartOffset(2B)
R D M A to b y p a s s t h e weak CPUs in memory pool during V p k g P tr   ( 8 B ) B it m a p  (1 -4 B )
|               |                       |     |     |                          | V p k g    |          | B i tm a p                 |                                            |
| ------------- | --------------------- | --- | --- | ------------------------ | ---------- | -------- | -------------------------- | ------------------------------------------ |
|               |                       |     |     | A u x i li ar y   i n fo | . … Table1 |          | 0 1 01 1                   | V c el lE A (1 B )                         |
| tra n sa ctio | n p ro c e s si n g . |     |     |                          | V p k g    |          |                            |                                            |
|               |                       |     |     |                          |            | Mo d i f | i e d   a t t r ib u t e s |                                            |
|               |                       |     |     |                          | V p k g    | o f      |   a   v e r s i o n Const  | r u c t i n g   a  vers io n  o f  v a lue |
… Table2
4 MotorMemoryStore Value package V p k g A   m o d i f i ed  D a t a   v a l u e
|                             |     |     |     |                     | …        | …                | a t t r i b u t e | in   V p k g M o d ifi e d   |
| --------------------------- | --- | --- | --- | ------------------- | -------- | ---------------- | ----------------- | ---------------------------- |
|                             |     |     |     | V p k g S A ( 1 B ) | V p k g  |                  |                   | attributes                   |
|                             |     |     |     |                     | … Tablen | An attribute bar |                   | +                            |
| 4.1 ConsecutiveVersionTuple |     |     |     | D a t a  V a l u e  |          |                  |                   |                              |
V p k g
|     |     |     |     | VpkgEA(1B) |                 |            |     | A version of value |
| --- | --- | --- | --- | ---------- | --------------- | ---------- | --- | ------------------ |
|     |     |     |     |            | Full-value area | Delta area |     |                    |
KeyIdea.Motorproposesaconsecutiveversiontuple(CVT)
Value Region
structuretomaintaindifferentversionsofdatainthememory
Figure3:ThestructureoftheMotormemorystore,whichis
pool.Unlikethelinkedchainsusingpointerstolinkversions, organizedbyCVTsinthedisaggregatedmemorypool.
CVTconsecutivelystorestheversionstogethertofillincon-
andalsoreducesthememoryfootprintinmemorypool.How-
tinuousaddressspace.ByusingCVT,thecoordinatorisable
tofetchmultipleversionsinasingleRDMAREAD,instead ever,duetolimitedavailableversionsinCVT,thegarbage
ofperformingthechainwalkingtoreadremoteversionsone collection(§4.3)canbefrequentlytriggered,andthismay
increasetransactionabortstohamperthethroughputwhenthe
byoneuntilthetargetversion.AfterfetchingtheCVT,the
coordinatorlocallysearchesforthetargetversion,whichis contentionishigh.Incontrast,ifVNumistoolarge,ithelps
mitigatetransactionaborts,butwouldwastememoryinread-
fastduetonotinvolvinganynetworkI/O.
Structure.Fig.3showsthestructureofthememorystorein intensiveworkloadsthatdonotrequiremanyversionsofdata.
Moreover,sinceanentireCVTisreadatatime,alargeCVT
thememorypool,whichisorganizedbyCVTs.AlltheCVTs
|     |     |     |     | increases | the payload to | lengthen the | RDMA read | latency. |
| --- | --- | --- | --- | --------- | -------------- | ------------ | --------- | -------- |
formaCVTregion.ACVTconsistsofaheaderandseveral
versioncells(Vcells).Inaheader,TableIDindicatestheDB Weexploresuchtradeoffin§7.2and§7.6,andobservethat
asuitableVNumsignificantlydependsonthecharacteristics
tablethisrecordbelongsto.Arecordisarowofuserdata,
containingthekeyandvalue,inaDBtable.Moreover,Key ofworkloads(e.g.,theaccesscontentionandthenumberof
is the unique identifierofthis record,andLock is usedfor recordstoreadinatransaction).Ingeneral,settingVNumto2
issufficientforlow-contentionworkloadswithshort-running
| concurrency | control in transaction | processing | (§ 5.1). The |     |     |     |     |     |
| ----------- | ---------------------- | ---------- | ------------ | --- | --- | --- | --- | --- |
AttrBarPtrpointstoanattributebarinthevalueregion.An transactions(e.g.,TATP[1]).Forhigh-contentionworkloads
withlong-runningtransactions(e.g.,TPCC[13]),aslightly
attributebarstoresthemodifiedattributesofdifferentversions
ofarecord’svalue,asdescribedin§4.2.TheVpkgPtrpoints largerVNum(e.g.,4)efficientlyreducestransactionaborts
toavaluepackage(Vpkg)invalueregion.AVpkgcontains withoutheavymemoryfootprintandhighreadlatency.
theactualdatavalue,whichiswrappedbyaVpkgSAanda IndexesSupports.Motorprovidesunifiedinterfacesforcoor-
VpkgEAtoindicatewhetherthevalueiscompletelywritten, dinatorstoquicklyaccessremoteCVTsbyleveragingindexes
|              |                     |             | VcellSA | (e.g.,hashtable[86]andB+tree[75]). |     |     | MotorstoresCVTs |     |
| ------------ | ------------------- | ----------- | ------- | ---------------------------------- | --- | --- | --------------- | --- |
| as explained | in § 4.4. Moreover, | in a Vcell, | the     |                                    |     |     |                 |     |
and VcellEA work with the VpkgSA and VpkgEA to check withintheindex.Forexample,whenusingB+treeindexes,
theconsistencybetweenaversionanditsvalue(§4.4).The CVTsarestoredinleafnodes,andtheinternalpointernodes
Valid indicates whether this version of value is available, arecachedincomputepooltoreduceremotetreetraverses.
andtheVersionrepresentsaversionnumber.Inaddition,the Whenusinghashingindexes,CVTsarestoredinhashtables
Bitmapindicatesthemodifiedattributesatthecurrentversion, by hashing Keys. Therefore,writing CVTs simultaneously
andtheStartOffsetrepresentstheoffsetofattributesstored modifiestheindex.Withoutlossofgenerality,ourpapercon-
intheattributebar(moredetailsarepresentedin§4.2). siderstousethehashtableasacaseinpointtopresentthede-
NumberofVersionsinCVT.Motorneedstoconfigurethe tailsofindexingremotedatalikeexistingstudies[26,78,84].
number of versions (VNum) to hold in CVT. Considering Toaddresshashcollisions,Motorreservesmultipleslotsina
hashbucket[86].EachslotstoresoneCVT.Givenakey(e.g.,
thatthememorypooldoesnotcontainpowerfulCPUtody-
namicallyadjustVNumintransactionprocessing,Motorsets K0)ofarecord,thecoordinatorhashesK0toobtaintheIDof
VNumtobefixed,i.e.,arecordhasafixedmaximumnumber hashbucketandcalculatetheremoteaddressofthisbucket.
of versions. In fact, it is challenging to determine an effi- Thecoordinatorthenreadsthebucketandlocallytraverses
cientVNumduetothetradeoffamongreadlatency,memory slotstosearchforthetargetCVTwhoseKeyisequaltoK0.
footprint,andtransaction abortrate. Specifically,ifVNum CVTAddressCache.Inpractice,itisexpensivetofetchan
istoosmall,theCVTsizebecomessmall,whichdecreases entirehashbucketeachtimewhenreadingaCVT.Toaddress
theRDMAtransmissionpayloadtodecreasethereadlatency, thisissue,Motorenableseachcoordinatortoleverageasmall
804    17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

privateCVTaddresscacheinthecomputepooltostorethe 1)AttrBarPtrinHeader. Whenarecordisupdatedfor
remoteaddressesofCVTs.WhenreadingthesameCVTsnext thefirsttime,thecoordinatorallocatesanattributebarinthe
time,thecoordinatorcanquicklyusethecachedaddresses deltaarea,andkeepstheremoteaddressoftheattributebar
todirectlyreadtheCVTsinsteadofhashbuckets.However, (i.e.,AttrBarPtr)intheCVT’sheader.
iftheKeyoffetchedCVTmismatchesthequeriedkey,the 2)BitmapinVcell.ThecoordinatorusesabitmapinVcell
cachedaddressbecomesstale.Thecoordinatoraddressesthis torepresentthemodifiedattributesatthecurrentversion.For
issuebyre-readingthehashbuckettoconfirmtheexistence example,ifavaluehas8attributesandthe1st,2nd,and4th
ofthetargetCVT,andthenupdatesitsaddresscache.Tostore attributesaremodifiedbyatransaction,thecoordinatorwrites
millionsofaddresses(eachoneis8B),anaddresscacheonly abitmapof“00001011”(therightmostbitrepresentsthefirst
consumesseveralMBsofDRAMspace,whichisacceptable attribute,i.e.,thelittle-endianstyle)intotheVcell.Thelength
forthecomputepool[65,84]. ofbitmapdependsonthenumberofattributes.
3) StartOffset in Vcell. This is used to represent the
4.2 SeparateValueRegion
offset of a group of modified attributes at the current ver-
SomepriorstudieslikeFORD[84]andSilo[71]storethe sion inside the attribute bar. The initial StartOffset is 0.
valuetogetherwithitsversion,sothatcoordinatorscanfetch ThecoordinatorcalculatesanewStartOffsetbyusingthe
thevalueandversioninoneread.However,thisdesignbe- last-writtenVcell’sStartOffsetandBitmap.Specifically,
comes inefficient in ourcontext,because storing the value accordingtothepositionsof“1”inthelast-writtenbitmap,
togetherwithitsversionsignificantlyincreasestheCVTsize, the coordinator accumulates the total size of attributes in
leading to highreadlatencyandnetworkbandwidthwaste the last write,and adds this total size with the last-written
(allvaluesaretransmittedbutonlyoneisneeded).Suchdraw- StartOffsettoobtainanewStartOffset.
backsbecomeevenworsewhenthevaluesizegetslarger. AttributeBarSize.Acoordinatorneedstoallocateaproper-
Totackletheabovechallenge,MotorseparatestheCVTs sizedattributebartoholdmodifiedattributestoalleviatemem-
fromdatavaluesinmemorypool.Thecoordinatorfirstreads orywastes.Bysamplingtransactionexecution,weobserve
a CVT to determine the target version,and then reads the thatforrecordsinaDBtable,thetotalsizesofattributesbe-
correspondingvalue.Inthisway,theCVTsizeisnotaffected ingupdatedpertransaction(calledTotAttrSizes)aredifferent
bythevaluesizetoachievestablelowreadlatency,andonly but occur at specific frequencies. For example,in TPCC’s
onedatavalueistransmittedtomitigatebandwidthwastes. CUSTOMERtable,theTotAttrSizecanbe512B,12B,and4B,
ReducingMemoryOverhead.Inthevalueregion,storinga respectivelyoccurringatfrequenciesof10%,88%,and2%
full-sizeddatavalueforeachversionsimplifiesthedatastore acrosstransactions.ThisisbecauseinOLTPscenarios,the
butwastesmemoryspace.Toalleviatethememoryoverhead, transaction logic specifies the attributes to update,and dif-
we have two observations. (1) The records in a relational ferenttransactionsfollowthestandardexecutionratiointhe
DB table follow the same schema,which defines the num- transaction mix [1,4,13]. According to the frequencies of
berof attributes of the value and the size of each attribute. differentTotAttrSizes,Motorreservescorrespondingpropor-
(2)Whenupdatingarecord,atransactioncanmodifyonly tionsofspaceintheattributebartoholdtheseattributesof
one orseveral attributes. Forexample,in TPCC,the value VNumversions(i.e.,ifsomeattributesaremorefrequentlyup-
ofarecordinDISTRICTtablecontains9attributes(100Bin dated,Motorreservesmorespacefortheseattributes).Hence,
total),butinNEW_ORDERtransactiononlyoneattributeismod- Motorapproximatelyestimatestheattributebarsize(ABS)=
ified,i.e.,D_NEXT_O_ID(4B).Basedontheseobservations, ∑n
i=1
(max(VNum×Frequency
i
,1)×TotAttrSize
i
),wheren
Motorstoresthevariable-sizedmodifiedattributes,instead isthenumberofTotAttrSizes.Forexample,whenVNum=4,
offull-sizedvalues,tomaintaindifferentversionsofvalues theABSofrecordsinCUSTOMERtableis:1×512B+3×12B+
foranyrecord,thusreducingthememoryoverhead. Fig.3 1×4B=552B,whichissufficienttoholdmodifiedattributes
shows that the value region contains a full-value area plus ofdifferentversionswithoutwastingmemory.Notethateven
a delta area. The full-value area stores the newest version ifallattributesofavaluearemodifiedatsomeversions(i.e.,
offull-sizedvalues,andthe delta area stores oldattributes TotAttrSize=full-valuesize),theattributebarcanstillstore
beingmodifiedbytransactions(like“undologs”).Therefore, alltheseattributes,sinceinthiscasethecalculatedABSis
anupdatedrecordhasonlyonefullvalueanddifferentver- guaranteedtobelargerthanthefull-valuesize.
sionsofvariable-sizedattributesthatareactuallymodified. Mitigating Contentions on Allocating Attribute Bars.
Toconstructanold-versionvalue,weonlyneedtoapplythe Whencoordinatorssimultaneouslyallocateattributebars,they
attributesattheoldtargetversionintothenewestfullvalue. willcompeteforthefreespaceindeltaarea,leadingtohigh
AttributeBar.Inthedeltaarea,Motorleveragesanewstruc- contentions. To avoid this,Motor pre-assigns a small MB-
ture,calledattributebar,toconsecutivelyandcompactlystore scaledeltaspacewithpropersize(basedonABS)inthedelta
themodifiedattributesofarecordacrosstransactions,asil- areatoeachcoordinator.Inthisway,thecoordinatorallocates
lustratedinFig.3.MotorusesthefollowingmetadatainCVT attributebarsinitsowndeltaspacewithoutcompetingwith
toefficientlymanageattributesbars. others.TheAttrBarPtrisgloballyvisibletoallcoordinators
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation 805

aftercompletingtheupdateoperation,sothatacoordinatoris Read queue Being read Preemptive
selection
abletoappendattributestotheattributebarscreatedbyother Txn4 Header V1 V3 V5 V7 Header V1 V3 V5 V7
Txn2
coordinators.Inrarecasesthedeltaspaceisexhausted,the
Header V1 V3 V9 V7 Header V9 V3 V5 V7
coordinatorinformsremoteCPUtoallocatelargerspace.
(a) Skipping the versions being read (b) Overwriting the oldest version
One RTT for Reading/Writing Values. Though the full
Figure4:DifferentgarbagecollectionschemesforCVT.
valueandattributesareseparated,Motorconsumesonlyone
overheadinthebaselinemethod.Thetradeoffisthatsome
round-triptime(RTT)toread/writeavalueattargetversion.
long-runningtransactionswouldbeabortediftheirpreviously
(1)Read.Acoordinatorselectsthetargetversion(e.g.,V0)
readdataarequicklyreclaimed.Nevertheless,theexperimen-
inaCVT.Theselectionschemeispresentedin§5.1.IfV0
talresults in § 7.2 showthatreserving a propernumberof
is the newest version, the coordinator reads the full value
versionsinCVTefficientlymitigatessuchaborts.Overwrit-
usingRDMAREADinoneRTT.Otherwise,thecoordinator
ingoldversionswillmaketheversionsinCVTunsorted,but
calculatesremoteaddressesoftherequiredoldattributesby
thecorrectnessisnotaffected,sincethecoordinatorlocally
usingAttrBarPtrinCVTheaderandStartOffsetaswell
traversesalltheversionsinCVTtolocatethetargetone.
as Bitmap in the Vcells whose Version is larger thanV0.
Notethatiftheattributebardoesnothaveenoughspace,
ThecoordinatorthenusesbatchedRDMAREADstoreadthe
thecoordinatorreclaimsoldattributesfromthestartofthe
fullvalueandoldattributestogetherinoneRTTandlocally
attributebartowritenewlymodifiedattributes.Inthisproce-
constructsanoldversionofvalue.(2)Write.Thecoordinator
dure,thecoordinatorcheckswhichVcellscorrespondtothe
uses batched RDMA WRITEs to update the full value and
reclaimedattributes,andsetstheValidintheseVcellsto0to
appendsoldattributestotheattributebartogetherinoneRTT.
deletetheseversions.SinceMotorappropriatelyconfigures
4.3 Coordinator-ActiveGarbageCollection thesizeofattributebartostoreattributesofmultipleversions,
reclaimingtheoldattributesdoesnotinvalidatemanyVcells.
If there is no empty Vcell when updating data,we need a
garbagecollection(GC)mechanismtoreclaimtheobsolete 4.4 Anchor-AssistedRead
versions.LegacyGCschemestracktheoldestrunningtrans- Toobtainadatavalue,thecoordinatorreadsaCVTtoselect
actionsanddeletetheversionsthatarenolongerused[16,64]. thetargetversion,andthenreadsthefullvalueandnecessary
However,sincethecomputeunitinthememorypoolisnot attributes.AsshowninFig.5a,coordinatorC1readsaCVT
aware of transaction states,it is difficult to apply tracking andneedsthevalueatversionV1(Value ).C1readsthefull
V1
inthememorypool.Ontheotherhand,ifthecomputepool value(Value )andoldattributestoreconstructValue .At
V7 V1
performs tracking,the coordinators needto confirm which thispoint,anothercoordinatorC2isperformingGCtoreclaim
versionsareunusedamongallthein-flighttransactions.This versionV1andwriteValue .Asaresult,therearetwoincor-
V9
increasesthenetworkroundtripsforsynchronizationsand rectresultsforC1.(1)C1readsacorruptedfullvaluedueto
wastesthecomputepower. beingpartiallyupdatedbyC2.(2)C1readsValue butmis-
V9
Inordertoavoidtheoverheadoftracking,Motorproposes takenlyregardsitasValue ,thusreconstructinganincorrect
V7
a coordinator-active GC scheme. The idea is that,if there Value .Therootcauseofthisissueisthattheversionand
V1
isnoemptyVcell,Motorallowsthecoordinatortoactively datavalueareseparatelystored,whichpreventscoordinators
selectavictimversiontobeoverwrittenbythenewversionto from“atomically”readingavalueanditsversion.
completeGC.Thisschemeislightweightduetoeliminating Toaddresstheabovechallenge,Motorproposesananchor-
theneedoftrackingtheoldestrunningtransaction. assistedreadschemetohelpcoordinatorsidentifytheconsis-
To select the victim version, Fig. 4a shows a baseline tencybetweentheversionandvalue.AsshowninFig.5b,this
scheme that skips the versions being read in a CVT, and schemeusestwoanchorsatthestartandendofaVcell,called
selectstheoldestversionintheremainingversions.Aread VcellSA(i.e.,Vcell’sStartAnchor)andVcellEA(i.e.,Vcell’s
queueisreservedineachCVTtostorethetimestampsoftrans- EndAnchor). Similarly,in a Vpkg,two anchors (VpkgSA
actionsthatarereadingtheCVT.Othercoordinatorscheck andVpkgEA)areusedtowrapthefullvalue.Ananchoris1
thereadqueueandskipthein-useversions.However,forread byte.ApairofSAandEAandthecontenttheywrapareim-
operations,sincethecoordinatordoesnotknowthecurrent plementedinaC++struct,allowingacoordinatortoaccess
positionofthequeue’stail,ithastouseRDMAFetchAndAdd themtogetherusingasingleRDMAREADorWRITE.
toatomicallymovethetail,andthen useRDMAWRITEto Tomakeanchorsefficientlywork,coordinatorsfollowtwo
insertatimestamptothereadqueue.SuchextraRTTsineach rules.(1)Write.Acoordinatorincreasestheanchorvalueby
readsignificantlyincreasethelatency. 1forallthefouranchors(i.e.,VpkgSA,VpkgEA,VcellSA,
WeobservethattheoldestversioninCVThasthesmallest andVcellEA)tomakethemequal.Thecoordinatorwrites
probabilitytobeused,giventhatRDMAsignificantlyacceler- the Vpkg first,then the modified attributes,and finally the
atestransactions[26,78].Hence,Motorenablescoordinators Vcell.(2)Read.AcoordinatorreadsaCVTandthenfetches
topreemptivelyselecttheoldestversioninCVTasthevic- theVpkgandnecessaryattributes.Sincethefullvalueregion
tim,as shown in Fig. 4b. This GC scheme avoids the RTT storesthenewestvalue,theVpkgSAandVpkgEAarealso
806 17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

❶Read CVT Start Anchor End Anchor TimestampGeneration.Motorleveragessequentialnumbers
❷ CVT
C1 want V1 Header V1 V3 V5 V7 VcellSA Version VcellEA Vcell as transaction timestamps (i.e., 1, 2, 3 ...), which are also
❸Read full value and required attributes VpkgSA Value VpkgEA Vpkg adoptedasdataversions.Infact,thetimestampgenerationis
(Error 1:read a corrupted value. Error 2:read value V9) •Writer: writeVpkg gattributesgVcell
C2 Full Value(V7) •Reader:compare anchors as follows orthogonaltoourdesigns.Existingstudiesproposescalable
❸GC (V9) Attribute Bar VcellSA= VcellEA= VpkgSA= VpkgEA
timestampgenerationschemes[24,38,64,76],whichcanbe
(a) Reading an incorrect value caused by concurrent GC (b) Using anchors to detect incorrectness
Figure5:Theanchor-assistedreadscheme. appliedtothecomputepoolasthetimestampservicetoassign
strictlyandmonotonicallyincreasingtimestamps.Ourpaper
thenewest.Hence,thecoordinatorcheckswhetherthenewest
doesnotfocusonoptimizingthetimestampgeneration,and
VcellSA and VcellEA in CVT are equal to VpkgSA and
we assume that a scalable timestamp service is efficiently
VpkgEA. If the four anchors are equal,the full value and
leveragedinthecomputepooltoserveforallcoordinators.
attributesarenotmodifiedsincethelastread.Thecoordinator
Overview.Inthememorypool,eachtableisreplicatedto1
thensafelyreconstructsthetarget-versionvaluebycopying
primaryand f backups,andtheweakCPUsarenotinvolved
thefetchedoldattributesintothenewestfullvalue.However,
duringtransactionprocessing.Inthecomputepool,theco-
ifanyofthetwoanchorsarenotequal,thecoordinatoraborts
ordinatorsleverageourprotocoltoexecutetransactionsand
thetransactionduetodetectingpartialupdatesoraconflicting
accessremotedatathroughone-sidedRDMA.
in-flightGCprocedure.Inessence,thefouranchorsassistthe
5.1 ProcessingPhases
coordinatortoreadaversionandthecorrespondingvaluein
an“atomic”manner.UnlikeSilo[71]thatreadstheversion Fig. 6 shows the procedure of handling a read-write trans-
twicetoconfirmconsistency,ourschemeonlyneedstoread
action(e.g.,T0)withserializabilityguarantee.Allrequests
onceandcomparesthefouranchorstoidentifyconsistency. inthesameRTTareissuedinparallel.Theread-writesetis
GuaranteeingWriteOrder.Thecorrectnessoftheanchor-
{A,B}andtheread-onlysetis{C}.InMotor,thewritesetis
includedinthereadset,since(1)forUpdatesandDeletions,
assistedreadschemeisbasedonthatallthewrittendataare
thecoordinatorreadsremoteCVTsbeforewritingdataback,
installedintothememorypoolinthecorrectorder,whichhas
tworequirements.[R1]Vpkg→modifiedattributes→Vcell.
and(2)forInsertions,thecoordinatorreadsremotebuckets
[R2] Inside a Vpkg (or Vcell): start anchor → content → to obtain empty CVTs before inserting data. The detailed
processingphasesarepresentedbelow.
endanchor.Inpractice,thetworequirementsaresatisfiedin
networkandatremoteRDMANIC(RNIC),because(1)the Phase1.Execution.Thecoordinatorobtainsastarttimes-
reliableconnectionmodeforone-sidedRDMAguarantees tamp(T start )fromthetimestampservice.Foreachread-only
thatthetransmittedmessagesarenotlostorreordered[6],and (RO) orread-write (RW) data,the coordinatorlooks upits
(2)whentherequestreachestheremoteRNIC,theRNICen- localCVTaddresscache.(1)Iftheaddresshasbeencached
suresthattheRDMAWRITEsaretotallyorderedwithregard (e.g.,AandC),fortheROdata(e.g.,C),thecoordinatoruses
to each other [61],i.e.,these write requests are sent to the RDMA READ to fetch their CVTs from the primaries; for
on-chipintegratedmemorycontroller(iMC)inorder.How-
theRWdata(e.g.,A),thecoordinatorusesdoorbell-batched
ever,thetworequirementscanbethenviolatedduetoDDIO RDMA CAS+READ to respectively lock and read the CVTs
(i.e.,DataDirectI/O[8]).IfDDIOisenabled,iMCsendsthe fromtheprimaries.Thelockingrequestpreventsothercon-
writtendatatotheL3CPUcache.Duetounpredictablecache flicting transactions from modifying the same CVT at the
behavior,thedatainL3cachecouldbeevictedtomemory sametime.Ifthelockingrequestfails,thecoordinatoraborts
outofordertobreakR1andR2.Infact,DDIOaimstoim- the transaction,instead of waiting,to avoid deadlocks. (2)
provethecachelocality,whichbenefitstheCPUexecution If the address is not cached (e.g., B), the coordinator uses
intraditionalmonolithicservers,butbecomesuselessinthe
RDMAREADtofetchahashbucketandthenlocallysearch
disaggregatedmemory,sincetheweakCPUinmemorypool
foraKey-matchedCVT.AfterobtainingtheCVT,thecoordi-
isnotinvolvedduringtransactionprocessing.Hence,Motor
natorselectsatargetversionV0,whichisthelargestversion
disablesDDIOinthememorypool,sothatiMCdirectlysends amongalltheversionsthataresmallerthanT start .
writesfromitsinternalfirst-come-first-servewritepending
EarlyAbort.Ifthecoordinatorobservesaversion(e.g.,V1)
queuetothemainmemory.Inthisway,thewritesareinstalled largerthanT start intheCVT,itmeansthatanothertransaction
intoremotememoryinthecorrectordertosatisfyR1andR2. T1,hascommittedafterT0’sT start .Inthiscase,thecoordina-
torcanearlyabortT0toguaranteeserializability.Thereason
5 MotorTransactionProtocol
isthat,evenifusingT toselectV0forexecution,T0will
start
We present the Motor transaction protocol. Our protocol beabortedinthenextValidationphase,inwhichT0willob-
worksinawidely-recognizedtransactionprocessingframe- tain a largercommittimestampthan T1. Thatis,T0 witha
work,which includes reading data,handling conflicts,and largercommittimestampshouldhaveusedT1’supdate,i.e.,
writing data back. The main difference from existing stud- V1,for execution,but T0 usedV0. Hence,the coordinator
ies[27,39,64,77,78,84]isthatourprotocolfullyexploitsthe earlyabortsT0.Notethattheearlyabortisunnecessaryinthe
CVTstructureandpureone-sidedRDMAtosupportMVCC snapshotisolation,sinceitissufficientforT0toreadasnap-
baseddistributedtransactionsonthedisaggregatedmemory. shotatT ,evenifthesnapshotbecomesslightlystale[76].
start
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation 807

A CVT A Vpkg and any required attributes A Batched writes Lock Unlock in the fetched CVT,sets the Valid to 1,fills the Version
usingT ,setstheBitmapoftheupdatedattributes,calcu-
Get Tstart Execution Get Tcommit(Serialization point) Report “committed” commit
Coordinator
Read CVT Read Value Validation Commit latestheStartOffsetinsidetheattributebar,andconfigures
A B C A B C C A A B B
A’s primary Txn begin bothofVcellSAandVcellEAtobeequaltoanewnumber.
B
A B ’ ’ s s b p a ri c m ku a p ry s B u - n C c V a T c a h d e d d r R W e r a i d t e A A , = B A , + C C IfthereisnoemptyVcellortheStartOffsetexceedsthe
B’s backups Write B=B-C lengthofattributebar,thecoordinatoractivelyperformsGC
C’s primary Txn commit toreclaimoldversions. Moreover,thecoordinatorcollects
1 RTT 1 RTT 1 RTT 1 RTT
C’s backups
themodifiedattributesthatwillbewrittentotheattributebar.
Figure6:ThedistributedtransactionprotocolofMotor.
ThecoordinatorthenpreparesanewVpkgbyfillingthenew
After version selection, the coordinator uses batched datavalue,andsettingbothofVpkgSAandVpkgEAtobe
RDMA READs to read the Vpkgs and any required old at- equaltoVcellSA.(2)Insert.ApartfrompreparingtheVpkg
tributestoconstructthetarget-versionvalue(§4.2).Notethat andVcellliketheUpdateoperation,thecoordinatorprepares
forRWdatathathavenotbeenlocked(e.g.,B),thecoordina- anewheaderandfillstheTableID,Key,andVpkgPtr.The
toradditionallybatchesRDMACASwithREADstolockand TableIDandKeycomefromapplications.Thecoordinator
re-readtheirCVTswhenreadingVpkgs.Afterfetchingallthe allocatestheVpkgPtrinitsdeltaspace,i.e.,Motorallowsthe
data,thecoordinatorperformsthreechecksforcorrectness: newlyinserteddatatosharethedeltaareawithattributebars
(1)ifanylockingfails,T0isaborted;(2)ifanewerversion toimprovethespaceefficiency.(3)Delete.Thecoordinator
largerthanV0occursinthere-readCVT,T0isaborted,since setstheValidofV0to0,sothatsubsequenttransactionswith
anothertransactionhasupdatedthisdata;(3)ifthefouran- largertimestampscannotusethedeletedversion.Thedelete
chorsarenotequal,T0isaborted,becausetheversionand operationneedstosetthefullvalueinremotememorypoolto
valueareinconsistent.Ifpassingallchecks,thecoordinator anold-versionvalue.Tothisend,thecoordinatorcopiesthe
safelyusesthedatavalueinsidetheVpkgtoexecutethetrans- oldattributesfetchedinExecutionphaseintothefullvalue.
actionlogic.ThoughMotorusestwoRTTstoreadtheCVT Afterthese local preparations,the coordinatorleverages
anddatavalue,thenetworkpayloadissignificantlyreduced doorbell-batchedRDMAWRITEstowritetheprepareddata
duetonottransmittingunnecessarydatavalues. toallreplicasandunlocksprimariesinoneRTT.Whenre-
Phase2.Validation.AfteralltheremoteCVTsoftheRW ceivingallACKsfromallreplicas,thecoordinatorreports
dataaresuccessfullylocked,thecoordinatorobtainsacommit “committed”totheapplication.
timestamp(T )fromthetimestampservice.Notethatif ProcessingRead-OnlyTransactions.Acoordinatorobtains
commit
theread-writetransactiondoesnotcontainanyROdata,the areadtimestamp(T start )andreadstherequiredCVTsfromthe
followingoperationscanbeskippedtoreducelatency,since primaries.ThecoordinatorusesT start todeterminethetarget
allthe RW data have been alreadylocked. However,ifthe version, and then fetches the Vpkgs and any required old
transactioncontainsROdata,thecoordinatorneedstovalidate attributesfromprimariestoconstructthevalueatthetarget
thatthe versions ofRO data are notchangedfrom T to version.Ifthefouranchorsareequal,thetransactioncommits,
start
T toprovideserializability.Tothisend,thecoordinator andotherwiseaborts.Notethatinsingle-versioningdesigns,
commit
re-reads the CVT of each RO data from remote primaries theread-onlytransactionsrequirevalidation[27,39,77,84].
andusesT toselectaversionV′,whichisthelargest However,withmulti-versioning,theread-onlytransactionsdo
commit
versionamongalltheversionsthataresmallerthanT . notrequirevalidation[57]duetoobtainingastableversion
commit
Thecoordinatorcheckswhetheranyofthetwocasesoccur: snapshotatT start (moredetailsarediscussedin§5.2).
(1)theCVTislockedbyanothercoordinator,or(2)V′̸=V0.
5.2 FlexibleSupportofIsolationLevels
In thefirstcase,itispossiblethatanothertransaction with
a lower T commit is committing a new version. The second Byusingourprotocol,Motorsupportstwowidely-usedisola-
casemeansthatanothertransactionwithalowerT commit has tionlevels,i.e.,serializability(SR)[11]andsnapshotisolation
committedanewversion.Ifeithercaseoccurs,thevalidation (SI)[12],toflexiblymeettherequirementsofdifferentOLTP
fails,becauseT0withahigherT commit shouldreadthenew applications.WithSR,theconcurrenttransactionsappearto
versionbutfailstodosointheExecutionphase.Asaresult, beexecutedonebyone.Moreover,withSI,thetransaction
T0isabortedtoensureserializability.Inshort,thevalidation readsdatafromasnapshotatatime,whichdoesnotreflect
succeedsonlyiftheCVTisnotlockedandV′=V0.
changesmadebyotherin-flighttransactions.
Phase3.Commit.Whenthevalidationsucceeds,acoordi- SupportingSR.(1)Forread-writetransactions,theyareseri-
natorcommitstheupdatestoallremotereplicastogetherina alizableatthepointofT ifguaranteeingthatallthetarget
commit
singleRTT.Thecoordinatorlocallypreparesthedatatobe versionsselectedatT areequaltothoseatT .This
start commit
written,whichcanbeinterpretedinthreescenarios.(1)Up- propertyallowsthetransactionstobeconsideredasexecuting
date.Iftherecordisupdatedforthefirsttime,thecoordinator attheirT oneafteranother.Motorensuresthisproperty
commit
allocatesanattributebarinitsownpre-assigneddeltaspace. byusinglocksandvalidations.i)Ifatransactionobtainsall
ThecoordinatorthenfindsanemptyVcell(i.e.,Validis0) the locks of CVTs at T ,the versions of read-write data
start
808 17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

cannotbechangedbyothertransactionsuntilT .Hence, backup.Addingabackuprequiresdatamigration,inwhich
commit
theversionsofread-writedataatT areequaltothoseat MotorenablesmemorynodestouseRDMAWRITEtoquickly
start
T .ii)Duringvalidation,ifatransactiondetectsthatthe transmitapplicationdata.Subsequenttransactionsinvolving
commit
remote CVT is locked ora new version appears at T , failedreplicashangupuntilthereplicasarerecovered.The
commit
thevalidationfailsandthetransactionaborts,sincetheprevi- (f+1)-wayreplicationtoleratesatmost f replicafailures.
ouslyfetchedversionsofread-onlydatabecomestale.Ifthe CoordinatorFailuresinComputePool.Inlinewithexisting
validation succeeds,the versions ofread-onlydata atT start studies[27,78],Motorsupportstouseleases[31]todetect
areequaltothoseatT commit .(2)Forread-onlytransactions, coordinatorfailures.Motorenablesthecoordinatorstowrite
theydonothaveacommittimestampduetonotmakingdata small-sizedoperationlogsinlocalmemorytorecordtheoper-
changes.Inthemulti-versioningdesign,sinceread-onlytrans- ations(e.g.,thekeysthatwillbelockedorcommitted)during
actionsonlyobserveasnapshot,thestarttimeofread-only execution.TheoperationlogsarestoredinUPS-backedmem-
transactionscanbeconsideredtobe“movable”inorderto oryandarenotlost[27].Ifacoordinatorfails,Motoremploys
find a serializable execution order [57], i.e., the read-only anewonetousetheoperationlogstoresumethein-flight
transactionscanbeplacedamongotherread-writetransac- commitandunlockkeysforrecovery.Forexample,thenew
tionstomakeallthetransactionsappeartoexecuteoneby coordinatorusesRDMACAStounlocktherecordedkeys,i.e.,
one.Insummary,thewrite-writeandread-writeconflictsbe- if the CAS succeeds,the previous lock is released to avoid
tweentransactionsarerespectivelyaddressedbyusinglocks starvation,andotherwisethekeyisactuallynotlocked.
andvalidations,whichensurethattheprecedencegraphs[5] NetworkFailures.Anetworkfailurecausesthenetworkpar-
ofallthe transaction schedules do notcontain cycles,thus tition. In practice,it is hard to distinguish network failure
guaranteeingserializability[68]. fromserverfailure.LikeuKharon[34],weassumethatthe
Supporting SI. To support SI,Motor disables the version networkpartitionsarediscoveredandresolvedbydatacenter
validationfortheread-onlydatainread-writetransactions, administrators.Ifanetworkpartitionoccurs,eitheravailabil-
i.e.,thesetransactionsareallowedtouseastalesnapshotby ityorconsistencycannotbefullyguaranteedaccordingtothe
usingT start .Notethatthelockingisstillrequiredtoresolve CAPtheorem[18,30].InthecontextofOLTPapplications,
thewrite-writeconflicts.SIisweakerthanSR,butachieves offeringconsistencyismoreimportanttosatisfytheACID
higherperformance(asdemonstratedin§7.7)andhasbeen requirements.Hence,Motorweakenstheavailabilitybyonly
adoptedbymultiplepopularsystems,e.g.,MySQL[56],Post- allowingthemajorpartition[17]toserverequests.
greSQL[60],Oracle[59],andSQLServer[63].
6 Implementations
ACIDGuarantee.MotorguaranteesACIDfortransactions.
(1)Atomicity.Motormaintainsmultipleversionsofdata,and Wepresentsomeimportantimplementationdetailsincluding
theoldversionsactas“undologs”topreservetheatomicity. thetransactioninterfacesandexecutionframework.
(2)Consistency.Thedataversionsinmemorypoolareina Easy-to-Use Transaction Interfaces. Motor provides the
consistentstatebeforeatransactionstartsandafteritcommits. following interfaces for applications to easily run MVCC
(3)Isolation.Motorsupportsserializabilityandsnapshotiso- baseddistributedtransactionsonthedisaggregatedmemory.
lation.(4)Durability.Motorstores f+1replicasofeachdata • TxnBegin():StartatransactionandrecorditsID.
againstdataloss,andcanemployUPS-backedDRAM[27]or • GetTS():Getatimestampfromthetimestampservice.
persistentmemory[84]inthememorypooltodurablystore • AddObject():Addaread-only(orread-write)objectto
thecommittedupdatesevenifapowerfailureoccurs.
theread-only(orread-write)set.
5.3 FaultTolerance • FetchAll(): Obtain remote CVTs and target-version
ReplicaFailuresinMemoryPool.Byenablingdatarepli- datavalues.TheremoteCVTsaresimultaneouslylocked.
cation,Motorisabletotoleratereplicafailuresinthemem- • Validate():Validatetheversionsofread-onlydata.
orypool.Thereplicafailurescanbequicklydetectedusing • TxnCommit(): Commit the transaction by writing the
RDMA [27]. If any replica fails before commit, the coor- updatesbacktoremotereplicasandunlockingtheprimaries.
dinatordiscards allthe fetcheddata,unlocks remote locks, ExecutionFramework.Inthecomputepool,Motorusesthe
and aborts the transactions. If a primary fails during com- CPUcorestospawnmassivethreadstoexecutetransactionsin
mit,Motorpromotesabackupasthenewprimarytoretain parallel.However,ifusingathreadasacoordinator,theCPU
thecommittedupdates,becausethebackupshavethesame corewillbecomeidlewhenwaitingforRDMAACKs,which
updatesasprimary.Thenewprimaryisnotvisibletocoordi- decreasesthethroughput.Tosaturatethecomputepowerof
natorsuntiltheupdatesareinstalledintoalivereplicas.When aCPUcore,MotorgeneratesmultiplecoroutinesinaCPU
thenewprimarybecomesvisibleandsubsequentcoordinators threadtoexecuteinapipelinemanner[39,77,84].Inathread,
cangrablocksonthenewprimary,theupdatesofprevious onecoroutinepollstheRDMAACKs,andeachoftheother
transactionshavebeenalreadycommitted,thusguaranteeing coroutinesactsasatransactioncoordinator.Therefore,Mo-
serializability. Moreover, if a backup fails during commit, torenablessubstantialcoordinatorstoconcurrentlyexecute
thecoordinatorselectsanothermemorynodetoaddanew transactionsinthecomputepool.
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation 809

|     |     |     |     |     |     | 6   |     |     | )s/nxt K( tuphguorhT |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | --- | --- | --- |
7 P e r f o r m a n c e E v a lu a t i o n ) µs 5 0 0 0 5 0 0 0
|         |             |                 |     |     |     | ( ycnetal D 5 |     |     |     | 4 5 0 0 |     | 4 5 0  | 0   |     |
| ------- | ----------- | --------------- | --- | --- | --- | ------------- | --- | --- | --- | ------- | --- | ------ | --- | --- |
|         |             |                 |     |     |     | 4             |     |     |     | 4 0 00  |     | 4 0 0  | 0   |     |
| 7 . 1 E | x p e r i m | e n t a l S e t | u p |     |     | 3             |     |     |     | 3 5 0 0 |     | 3 5 00 |     |     |
|         |             |                 |     |     |     | 2             |     |     |     | 3 0 0 0 |     | 3 0 0  | 0   |     |
|         |             |                 |     |     |     |               |     |     |     | 2 5 0 0 |     | 2 5 0  | 0   |     |
T e s tb e d . W e c o n fi g u r e f o u r s e r v e rs c o nn e c te d t h ro u g h a M e l - A ER A 1 2 0 0 0 2 0 0 0
|     |     |     |     |     |     | 0   |     |     |     | 2 4 | 6 8 1 0 1 | 2 14 | 2 4 6 | 8 1 0 1 2 14 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | ---- | ----- | ------------ |
M
la n o x S B 7 8 9 0 1 0 0 G b p s I n fi n i B a n d ( IB ) S w i tc h . E a c h se rv e r D 0 4 8 1 2 V N u m VN u m
|          |           |          |            |          |     | R Data size        |  (KB, 64B |  intervals | )      | (a) S | ke w n e s s = |  0 .7       | (b ) Sk ew | n e s s  = 0 . 99 |
| -------- | --------- | -------- | ---------- | -------- | --- | ------------------ | --------- | ---------- | ------ | ----- | -------------- | ----------- | ---------- | ----------------- |
| contains | a 100Gbps | Mellanox | ConnectX-5 | IB RNIC. | One |                    |           |            |        |       |                |             |            |                   |
|          |           |          |            |          |     | Figure7:Thelatency |           |            | Figure | 8:    | The            | transaction | through-   |                   |
servercontainingIntelXeonGold6330CPUsisconfiguredas of reading different puton KVS benchmarkwhen varying
thecomputepooltoruncoordinators.Otherthreeserversform sizesofdata. VNumwithskewness0.7and0.99.
thememorypool,andeachservercontains192GBDRAM.
3 0 0 0
|     |     |     |     |     |     | )s/nxt K( 1 2 0 |     |     |     |     |     | 5 0 0 0 |     |     |
| --- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | ------- | --- | --- |
B e n c h m a r k s . W e l e v e ra g e a k e y - v a l u e s t o r e ( K V S ) a s a m i c r o - 1 0 0 2 5 00 4 5 0 0
|     |     |     |     |     |     | 8 0 |     |     | 2 0 0 0 |     |     | 4 0 0 0 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | ------- | --- | --- |
b e n c h m a r k . K V S s t o r e s 1 0 M k e y - v a l u e p a i r s i n o n e d a t a b a s e tuphguorhT 6 0 1 5 0 0 3 5 0 0
|     |     |     |     |     |     | 4 0 |     |     | 1 0 0 0 |     |     | 3 0 0 0 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | ------- | --- | --- |
|     |     |     |     |     |     | 2 0 |     |     | 50 0    |     |     | 2 5 0 0 |     |     |
( D B ) t a b l e . T h e k e y i s 8 B a n d t h e v a l u e i s 4 0 B [ 3 9 , 8 4 ] . I n 0 0 2 0 0 0
K V S , e a c h t r a n s ac t i o n p e r f o r m s a r e a d o r a n u p d at e o p e r a t io n 2 4 6 8 10 12 14 2 4 6 8 10 12 14 2 4 6 8 10 12 14
|     |     |     |     |     |     |     | VNum |     |     | VNum |     |     | VNum |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | ---- | --- | --- | ---- | --- |
toa48BKVpairwithskewedaccessesfollowingtheZipfian
|              |       |           |              |         |          |          | (a) TPCC       |     |     | (b) SmallBank               |     |     | (c) TATP |     |
| ------------ | ----- | --------- | ------------ | ------- | -------- | -------- | -------------- | --- | --- | --------------------------- | --- | --- | -------- | --- |
|              |       |           |              |         |          | Figure9: | Thetransaction |     |     | throughputonTPCC,SmallBank, |     |     |          |     |
| distribution | [23]. | We enable | the skewness | and the | ratio of |          |                |     |     |                             |     |     |          |     |
read-write transactions in the transaction mix ofKVS to be andTATPbenchmarkswhenvaryingVNum.
configurabletofacilitatecomprehensiveevaluation.Further-
thetransactionthroughputgenerallyfirstincreasesandthen
more,weleveragethreewidely-usedOLTPbenchmarks,i.e.,
|     |     |     |     |     |     | decreases. | The | reason | is  | that,when | VNum | gets | larger,the |     |
| --- | --- | --- | --- | --- | --- | ---------- | --- | ------ | --- | --------- | ---- | ---- | ---------- | --- |
TATP[1],SmallBank[4],andTPCC[13],toevaluatetheend-
abortrateofread-onlytransactionsisreducedtoincreasethe
to-endtransactionthroughputandlatency.Specifically,TATP
|     |     |     |     |     |     | throughput. |     | Forexample,in |     | TPCC,the |     | abortrate | ofa | long- |
| --- | --- | --- | --- | --- | --- | ----------- | --- | ------------- | --- | -------- | --- | --------- | --- | ----- |
showsatelecomapplication,whichincludes4DBtablesand
runningread-onlytransactionSTOCK_LEVELdecreasesfrom
80%ofthetransactionsareread-only.TATPcontains2Msub-
|     |     |     |     |     |     | 32.1% | (VNum | = 2) | to 3.8% | (VNum | =   | 4). However,after |     |     |
| --- | --- | --- | --- | --- | --- | ----- | ----- | ---- | ------- | ----- | --- | ----------------- | --- | --- |
scribersandtherecordsizeisupto48B.SmallBankmodels
reachingthepeaktransactionthroughput,increasingVNum
abankingapplication,whichcontains2DBtablesand85%
nolongersignificantlyreducesaborts,buttheCVTsizecon-
oftransactionsareread-write.SmallBankhas10Maccounts
tinuestoincrease,whichenlargesthepayloadsizetoincrease
andtherecordsizeis16B.TPCCmodelsacomplexordering
RDMAreadlatency,asshowninFig.7.Theincreasedread
system,whichcontains9DBtablesand92%oftransactions
|     |     |     |     |     |     | overhead | overwhelms |     | the | benefit | of reducing |     | aborts, | thus |
| --- | --- | --- | --- | --- | --- | -------- | ---------- | --- | --- | ------- | ----------- | --- | ------- | ---- |
areread-write.TPCCcontains24warehousesandtherecord
decreasingtheperformance.Besides,largeVNumsalsocon-
sizeisupto672B.Moreover,forallbenchmarks,eachDB
sumemorememoryspace,aspresentedin§7.6.Fig.8shows
tableisreplicatedtothreememorynodestomaintaina3-way
|     |     |     |     |     |     | that at | skewness | 0.7,KVS |     | reaches | the peak | throughput |     | ear- |
| --- | --- | --- | --- | --- | --- | ------- | -------- | ------- | --- | ------- | -------- | ---------- | --- | ---- |
replication,i.e.,1primaryand2backups.
lierthan0.99,sincealargerskewnessincurshigheraccess
Comparisons.WecompareourMotorwithtwostate-of-the-
contentionandrequiresmoreversionstoreduceaborts.
artsystems,i.e.,FaRMv2[64]andFORD[84].FaRMv2sup-
Weobservethat,asVNumincreasesafterthepeakthrough-
portsmulti-versioningfortransactionsonmonolithicservers,
put,thethroughputdegradationofTPCC(upto49.6%)isheav-
andusesthenew-to-oldchainstolinkversions[64].Tomake
ierthanotherworkloads.Thisisbecauseonetransactionin
FaRMv2compatiblewithdisaggregatedmemory(DM),we
TPCCcanaccesshundredsofrecords,whichismuchlarger
useone-sidedRDMAtoimplementitstransactionprotocol,
thanotherbenchmarks,e.g.,onetransactioninSmallBank
whichisreferredtoasFaRMv2-DMintherestofthispaper.
(orTATP)onlyaccesses1–3(or1–4)records.Therefore,the
Moreover,FORDsupportssingle-versioningfortransactions
|                      |     |            |     |                     |     | overall | read | overhead | (considered |     | as CVT | size | × number |     |
| -------------------- | --- | ---------- | --- | ------------------- | --- | ------- | ---- | -------- | ----------- | --- | ------ | ---- | -------- | --- |
| on the disaggregated |     | memory,and | we  | run its open-source |     |         |      |          |             |     |        |      |          |     |
ofrecords)ofTPCCtransactionsismoresensitivetoVNum,
| code. ThoughFORD |     | leverages | persistentmemory,its |     | one- |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | --------- | -------------------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
leadingtosharperperformancedecrease.SmallBankiswrite-
sidedRDMAdesignsontransactionprotocolarealsocom-
|     |     |     |     |     |     | intensive, | but | its transactions |     | are | short, | and | maintaining | 3   |
| --- | --- | --- | --- | --- | --- | ---------- | --- | ---------------- | --- | --- | ------ | --- | ----------- | --- |
patiblewithDRAM.NotethatMotortargetsonthedisaggre-
versionsreachesthepeakperformance.TATPonlyrequires
gatedarchitecture,whichisnotcomparablewiththesystems
2versionsforarecordtoachievethepeakthroughput,since
runningonthemonolithicarchitecture[39,57,76].
80%oftransactionsinTATPareread-onlyandshort-running
PerformanceMetrics.Wereportthetransactionthroughput
withlowcontentions.AsVNumgrows,thehighreadover-
bycountingthenumberofcommittedtransactionspersecond.
headleadstocontinuousthroughputdegradationinTATP.
Moreover,wereportthe50thand99thpercentilelatenciesof
|     |     |     |     |     |     | In  | summary,determining |     |     | a suitable |     | VNum | significantly |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | ---------- | --- | ---- | ------------- | --- |
committedtransactionsasthetransactionlatency.
|     |     |     |     |     |     | depends | on the | characteristics |     | of  | workloads,including |     |     | the |
| --- | --- | --- | --- | --- | --- | ------- | ------ | --------------- | --- | --- | ------------------- | --- | --- | --- |
7.2 NumberofVersionsinCVT
|     |     |     |     |     |     | access | contention | andthe |     | numberofaccessedrecords |     |     |     | in a |
| --- | --- | --- | --- | --- | --- | ------ | ---------- | ------ | --- | ----------------------- | --- | --- | --- | ---- |
We explore how the number of versions (VNum) in CVT transaction.Whenthecontentionislow(e.g.,TATP),setting
affectstheperformanceofMotor.Foreachbenchmark,we a small VNum is enough. If the contention is high, more
varyVNumfrom2to15.Theratioofread-writetransactions versionsareneededtoallowhigherconcurrency,especially
in KVS is 80%. Fig. 8 and 9 show thatas VNum increases, forthelong-runningtransactions.Wealsoneedtoconsider
810    17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

8 0 0 0
)s/nxt K( tuphguorhT )s/nxt K( tuphguorhT 8 0 0 0 )sµ( ycnetal elitnecrep ht05 3 5 )sµ( ycnetal elitnecr 2 5 0
O 2 N N 2 0 C V T O 2 N N 2 0 C V T 3 0 F a R M v 2 - D M 2 0 0 F a R M v 2 - D M
| 6 0 0 0 |     |     | 6   | 0 0 0 |     |     | 2 5 F O R | D     |     |               |     |
| ------- | --- | --- | --- | ----- | --- | --- | --------- | ----- | --- | ------------- | --- |
|         |     |     |     |       |     |     | 2 0       |       |     | 1 5 0 F O R D |     |
| 4 0 0 0 |     |     | 4   | 0 0 0 |     |     | M o       | t o r |     | M o t o r     |     |
|         |     |     |     |       |     |     | 1 5       |       |     | 1 0 0         |     |
| 2 0 0 0 |     |     | 2   | 0 0 0 |     |     | 1 0       |       |     |               |     |
|         |     |     |     |       |     |     | 5         |       |     | 5 0           |     |
| 0       |     |     |     | 0     |     |     | 0         |       |     | 0             |     |
2 0 % 4 0 % 6 0 % 8 0 % A V G 2 0 % 4 0 % 6 0 % 8 0 % A V G e p
|     |     |     |     |     |     |     | 0 1 0 0 | 0 2 0 0 0 3 0 0 0 4 0 0 | 0 5000   h 99t | 0 1 0 0 0 | 2 0 0 0 3 0 0 0 4 0 0 0 5000 |
| --- | --- | --- | --- | --- | --- | --- | ------- | ----------------------- | -------------- | --------- | ---------------------------- |
T h e  ratio   o f  r e ad - w rit e  t ra n sac ti o n s T h e ratio   o f  r e ad - w rit e  t ra n sac ti o n s T r a n s a c t io n  t h roug h p u t (K  t x n /s) T r a n s a c t io n  t h roug h p u t (K  t x n /s)
(a) VNum = 3, skewness = 0.7 (b) VNum = 4, skewness = 0.99 (a) TATP
F i g u r e 1 0 : T h e t r a n s a c t i o n t h r o u g h p u t o f d i ff e r e n t v e r s i o n )sµ( ycnetal elitnecrep ht05 1 5 0 )sµ( ycnetal elitnecr 2 0 0 0 0
|     |     |     |     |     |     |     | F a R M | v 2 - D M |     | F a R M | v 2 -D M |
| --- | --- | --- | --- | --- | --- | --- | ------- | --------- | --- | ------- | -------- |
s t r u c t u r e s o n K V S b e n c h m a r k . 1 2 0 1 5 0 0 0
|     |     |     |     |     |     |     | F O R     | D   |     | F O R D |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | ------- | --- |
|     |     |     |     |     |     |     | 9 0 M o t | o r |     | M o t o | r   |
t h e n u m b e r o f r e c o r d s a c c e s s e d p e r t r a n s a c t i o n t o a v o i d l a r g e 6 0 1 0 0 0 0
|           |                 |             |                   |             |                            |     | 3 0 |     |     | 5 00 0 |     |
| --------- | --------------- | ----------- | ----------------- | ----------- | -------------------------- | --- | --- | --- | --- | ------ | --- |
| C V T s i | n c u r r i n g | h i g h o v | e r a l l r e a d | o v e r h e | a d . A c c o r d in g t o |     |     |     |     |        |     |
|           |                 |             |                   |             |                            |     | 0   |     | e   | 0      |     |
t h e s e r e s u l ts , w e r e s p e c t i v e l y s e t th e s u i t a b l e V N u m i n T P C C , 0 2 0 4 0 6 0 8 0 1 00   h p 0 2 0 4 0 6 0 8 0 1 0 0
99t
T A T P , S m a l l B a n k , a n d K V S t o 4 , 2 , 3 , a n d 4 . T r a n s a c ti o n  throu g hput  (K  txn/ s) Tra n s a ct io n  t hrou g hput  (K  txn/ s )
(b ) TP C C
7 . 3 P e r f o r m a n c e o f V e r s i o n S t r u c t u r e s )sµ( ycnetal elitnecrep ht05 1 2 0 )sµ( ycnetal elitnecr 2 7 0
|     |     |     |     |     |     | 1   | 0 0 F a R | M v 2 - D M |     | F a R M v 2 | - D M |
| --- | --- | --- | --- | --- | --- | --- | --------- | ----------- | --- | ----------- | ----- |
|     |     |     |     |     |     |     | F O R     | D           |     | 2 2 0       |       |
W e c o m p a r e t h e p e r f o r m a n c e o f o u r C V T a n d t r a d i t i o n a l 8 0 1 7 0 F O R D
|     |     |     |     |     |     |     | 6 0 M o | t o r |     | M o t o r |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | ----- | --- | --------- | --- |
1 2 0
| l i n ke d - c | h a i n v e | r s i o n s t r u | c t u r e s , i . | e ., o l d - t | o - n e w ( O 2 N ) a n d    |     | 4 0   |                         |            |         |                              |
| -------------- | ----------- | ----------------- | ----------------- | -------------- | ---------------------------- | --- | ----- | ----------------------- | ---------- | ------- | ---------------------------- |
|                |             |                   |                   |                |                              |     | 2 0   |                         |            | 7 0     |                              |
| n e w -t o -   | o l d ( N 2 | O ) , u p o n     | t h e K V S       | b e n c h m    | a r k . W e c o n fi g u r e |     |       |                         |            |         |                              |
|                |             |                   |                   |                |                              |     | 0     |                         | e p        | 2 0     |                              |
|                |             |                   |                   |                |                              |     | 0 5 0 | 0 1 0 0 0 1 5 0 0 2 0 0 | 0 2500   h | 0 5 0 0 | 1 0 0 0 1 5 0 0 2 0 0 0 2500 |
t h e a c c e s s s k e w n e s s a s 0 . 7 a n d 0 . 9 9 , a n d v a r y t h e r a t i o o f 99t
|     |     |     |     |     |     |     | Tr a n s | a c t io n   t h roug h p u t (K  t x n | /s) | Tr a n s a c t io | n   t h roug h p u t (K  t x n /s) |
| --- | --- | --- | --- | --- | --- | --- | -------- | --------------------------------------- | --- | ----------------- | ---------------------------------- |
read-writetransactions(RW-ratio)from20%to80%inthe (c) SmallBank
Figure11:Thetransactionthroughputandlatencyofallthe
| transaction | mix | of KVS. | Based on | the results | in Fig. 8,we |     |     |     |     |     |     |
| ----------- | --- | ------- | -------- | ----------- | ------------ | --- | --- | --- | --- | --- | --- |
systemsonTATP,TPCC,andSmallBankbenchmarks.
changethemaximumnumberofversionstoholdforallstruc-
|     |     |     |     |     |     | Compared |     | with FORD, | Motor | respectively | improves |
| --- | --- | --- | --- | --- | --- | -------- | --- | ---------- | ----- | ------------ | -------- |
turesto3forskewness0.7,and4forskewness0.99.
|     |     |     |     |     |     | the | transaction | throughput | by  | 14.4% on | TATP, 98.1% on |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | --- | -------- | -------------- |
Fig.10showsthatCVTrespectivelyimprovesthethrough-
|     |     |     |     |     |     | TPCC,and |     | 65.4% on SmallBank. |     | FORD adopts | the single- |
| --- | --- | --- | --- | --- | --- | -------- | --- | ------------------- | --- | ----------- | ----------- |
putby1.7–2.4×and1.3–1.6×comparedwithO2NandN2O.
Thereasonisthat,CVTenablesthetransactiontofetchthetar- versioningdesign,whichlimitsthethroughput,sincereads
areblockedbywritesduringcommit,andtheundologscon-
getversioninasingleroundtrip,whileO2NandN2Orequire
sumenetworkbandwidth.UnlikeFORD,Motorallowstoread
multipleroundtripsforchainwalking.Whenincreasingthe
existingversionsinCVTs,anddoesnotneedtowriteundo
RW-ratio,thethroughputsofthreestructuresdecrease,since
|     |     |     |     |     |     | logs | to remote | replicas | by maintaining | oldversions | ofval- |
| --- | --- | --- | --- | --- | --- | ---- | --------- | -------- | -------------- | ----------- | ------ |
thewriteconflictsincreaseandread-writetransactionsrequire
moreroundtripstocommit.Whentheskewnessishigh(e.g., ues.Hence,MotorimprovesthethroughputoverFORD.The
|           |          |        |                |     |                | improvements |     | are higherin | TPCC | andSmallBank,because |     |
| --------- | -------- | ------ | -------------- | --- | -------------- | ------------ | --- | ------------ | ---- | -------------------- | --- |
| 0.99) and | RW-ratio | is low | (e.g.,20%),the |     | throughput gap |              |     |              |      |                      |     |
(1)theyarewrite-intensiveworkloadsinwhichMotoravoids
betweenN2OandCVTbecomessmall,becausetheaccessis
moreconcentratedandmanyread-onlytransactionsquickly many undo logs,and (2) Motor reserves multiple versions
toreducesabortsforread-onlytransactions,especiallylong-
obtainnewvaluesfromthechainheadofN2O.However,such
runningones,e.g.,STOCK_LEVELinTPCC.FORDdeliversthe
performancegapbetweenO2NandCVTbecomeslargerat
lowest50thpercentilelatencyinTATP,sincethetwotrans-
highskewnesssincethenewversionsinO2Nareplacedinthe
actions,i.e.,GET_SUBSCRIBER_DATAandGET_ACCESS_DATA,
chaintail,whichincreasesthereadoverhead.Moreover,CVT
respectivelyreducesthe50th(and99th)percentilelatencies occupy70%ofthetransactionmix,andbothofthemonlyread
oneobject.Inthiscase,FORDonlyusesoneRTTtoreaddata,
by59.8%/30.8%(and67.9%/47.7%)onaveragecompared
whileMotorrequirestwoRTTstoseparatelyreadtheCVT
| with O2N/N2O |     | at skewness | 0.99 | due to | the same reasons |     |     |     |     |     |     |
| ------------ | --- | ----------- | ---- | ------ | ---------------- | --- | --- | --- | --- | --- | --- |
anddatavalue.However,the99thpercentilelatencyofMotor
above.Wehavealsoexaminedthatwhenfurtherincreasing
onTATPisclosetoFORDwhenthetransactionbecomescom-
themaximumnumberofversionstohold,CVTcandeliver
moreperformancebenefitsoverO2NandN2O. plex.Furthermore,Motorreducesthe50thpercentilelatency
by55.8%/26.2%onTPCC/SmallBankcomparedwithFORD.
7.4 End-to-EndPerformance
ComparedwithFaRMv2-DM,Motorrespectivelyimproves
WeleverageTATP,TPCC,andSmallBanktoevaluatetheend- thetransactionthroughputby18.9%/44.3%/29.5%,andre-
to-endperformanceofMotor,FORD,andFaRMv2-DM.All ducesthe50th(99th)percentilelatenciesby8.6%(39.1%)/
systemsguaranteeserializability.Weconfigurethemaximum 52.1%(35.6%)/43.6%(34.5%),onTATP/TPCC/SmallBank.
number of versions in FaRMv2-DM’s version chain to be Motor achieves these improvements due to three reasons.
thesameasourCVTforfaircomparisons.Fig.11illustrates (1)FaRMv2usesthelinkedchaintostoredifferentversions,
thetransactionthroughputandlatency.Toplotathroughput- whichincreasesnetworkroundtripstoperformchainwalking
latencycurve,weincreasetherequestloadbyrunning10–40 toobtainthetargetversion.UnlikeFaRMv2,MotorusesCVT
threadsand2–8coroutinesperthread,i.e.,10–280concurrent tofetchtheversionstogetherinoneroundtrip.Motorshows
coordinators.Eachthreadexecutes1Mtransactionsfollowing thehighestimprovementoverFaRMv2-DMinTPCC,since
thestandardtransactionmixofeachbenchmark[1,4,13]. TPCCrequiresmoreversionsandthetransactionsreadmany
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation    811

| 5   |     |     | 1 0 |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
)B G FaRM v 2 -D M M ot o r FO RD )B G FaRM v 2 -D M M o t o r F O RD )s/nxt K( tup 1 2 0 F O R D Fa R M v2- D M M ot o r )s/nxt K( tup 2 6 0 0 F O R D F aRM v 2 -D M Mot o r
| ( daehrevo yrom 4 |     |     | ( daehrevo yrom 8 |     |     |             |     |     |     |               |     |     |     |
| ----------------- | --- | --- | ----------------- | --- | --- | ----------- | --- | --- | --- | ------------- | --- | --- | --- |
|                   |     |     |                   |     |     | 1 0 0       |     |     |     | 2 2 0         | 0   |     |     |
| 3                 |     |     | 6                 |     |     | 8 0         |     |     |     |               |     |     |     |
|                   |     |     |                   |     |     |             |     |     |     | 1 8 0         | 0   |     |     |
| 2                 |     |     | 4                 |     |     | 6 0         |     |     |     |               |     |     |     |
| 1                 |     |     | 2                 |     |     | hguorhT 4 0 |     |     |     | hguorhT 1 4 0 | 0   |     |     |
| 0                 |     |     | 0                 |     |     | 2 0         |     |     |     | 1 0 0         | 0   |     |     |
eM TPCC T A T P Sma llB a n k K VS eM TPCC T A T P Sma ll B a n k K VS 20002 5 0 0 3000 3 5 00 4 0 0045 00 5 0 00 1000 1 5 0 0 200 0 2 5 0 0 3000 3 5 00
(a) Benchmark Scale-1  (b) Benchmark Scale-2  Total memory used (MB) Total memory used (MB)
Figure 12: The space consumption in memory pool of all (a) TPCC (b) SmallBank
|     |     |     |     |     |     |     | FO RD | Fa RM v 2- | D M Mot o r |     | F O R | D Fa R M v2- | D M M ot or |
| --- | --- | --- | --- | --- | --- | --- | ----- | ---------- | ----------- | --- | ----- | ------------ | ----------- |
s y s t e m s a t t w o s c a le s o f b e n c h m a r k s . )s/nxt K( tup 4 5 0 0 )s/nxt K( tup 4 8 0 0
|                 |                     |            |             |                     |                 | 4 0 0         | 0   |     |     | 4 6 0         | 0   |     |     |
| --------------- | ------------------- | ---------- | ----------- | ------------------- | --------------- | ------------- | --- | --- | --- | ------------- | --- | --- | --- |
|                 |                     |            |             |                     |                 | 3 5 0         | 0   |     |     | 4 4 0         | 0   |     |     |
| r e c o r d s , | w h i c h e x a c e | r b a te s | t h e c h a | i n w a l k i n g i | n F a R M v 2 - |               |     |     |     |               |     |     |     |
|                 |                     |            |             |                     |                 | 3 0 0         | 0   |     |     | 4 2 0         | 0   |     |     |
|                 |                     |            |             |                     |                 | hguorhT 2 5 0 | 0   |     |     | hguorhT 4 0 0 | 0   |     |     |
D M t o c a u s e h i g h o v e r h e a d s . ( 2 ) T h e d e s i g n o f F a R M v 2 2 0 0 0 3 8 0 0
|             |                         |       |             |                     |                     | 1 5 0 | 0                      |             |            | 3 6 0 | 0                      |             |                   |
| ----------- | ----------------------- | ----- | ----------- | ------------------- | ------------------- | ----- | ---------------------- | ----------- | ---------- | ----- | ---------------------- | ----------- | ----------------- |
| c o n s u m | e s a d e d i c a t e d | R T T | t o l o c k | t h e r e a d - w r | i t e d a ta ,b u t |       |                        |             |            |       |                        |             |                   |
|             |                         |       |             |                     |                     |       | 700 1 00 0             | 130 0 1 6 0 | 0 1900 2 2 | 00    | 10001 5 0 0            | 2000 2 5 00 | 3 0 0035 00 4 000 |
|             |                         |       |             |                     |                     |       | Total memory used (MB) |             |            |       | Total memory used (MB) |             |                   |
MotorenablestobatchthelockingandCVT/valuereadre-
|     |     |     |     |     |     |     |     | (c) KVS |     |     |     | (d) TATP |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | -------- | --- |
quests to save RTTs. (3) The design of FaRMv2 uses two Figure13:Thecomparisonsoftransactionthroughputwhen
RTTstocommitthebackupsandprimaries,whileMotorup-
varyingMotormemoryfootprintbychangingVNum.
datesallreplicastogetherinoneRTT.Moreover,FORDcan
|     |     |     |     |     |     | )s/nxt K( tup 1 1 | 0   |     |     | )s/nxt K( tup 2 8 0 | 0   |     |     |
| --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | ------------------- | --- | --- | --- |
a l s o a c h i e v e l o w e r l a te n c y t h a n F aR M v 2 - D M b y a ll e v i a t in g 1 0 0 2 5 0 0
|              |                         |           |         |                    |                      |     |                 |                |     | 2 2 0 | 0          |                |     |
| ------------ | ----------------------- | --------- | ------- | ------------------ | -------------------- | --- | --------------- | -------------- | --- | ----- | ---------- | -------------- | --- |
| t h e re a d | o v e r h e a d , b u t | F a R M v | 2 - D M | a ll o w s m o r e | co n c u r r e n c y | 9   | 0               |                |     |       |            |                |     |
|              |                         |           |         |                    |                      | 8   | 0 S m a ll A BS | L a rg e A B S |     | 1 9 0 | 0 S mallAB | S Lar ge A B S |     |
|              |                         |           |         |                    |                      |     |                 |                |     | 1 6 0 | 0          |                |     |
i n m u l t i- v e r s i o n i n g t o i m p r o v e t h e th r o u g h p u t . hguo 7 0 M o t o r hguo 1 3 0 0
|     |     |     |     |     |     | 6   | 0   |     |     | 1 0 0 | 0   |     | Moto r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | ------ |
|     |     |     |     |     |     | rhT |     |     |     | rhT   |     |     |        |
7 . 5 M e m o r y O v e r h e a d 280 0 3 2 0 0 36 0 0 4 0 0 0 4400480 0 5 2 0 0 170 0 1 800 1 9 0 0 2000 2 100
|     |     |     |     |     |     |     | Total memory used (MB) |     |     |     | Total memory used (MB) |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | ---------------------- | --- | --- |
Wepresentthememoryoverheadsofallsystemsinthemem- (a) TPCC (b) SmallBank
|               |                       |               |            |                       |                       | )s/nxt K( tup 4 5 0 | 0   |     |     | )s/nxt K( tup 6 0 0 | 0   |     |     |
| ------------- | --------------------- | ------------- | ---------- | --------------------- | --------------------- | ------------------- | --- | --- | --- | ------------------- | --- | --- | --- |
| o r y p o o l | u s i n g t w o d i f | f e r e n t s | c a le s o | f b e n c h m a r k s | . S c a l e - 1 ( o r |                     |     |     |     |                     |     |     |     |
|               |                       |               |            |                       |                       | 4 0 0               | 0   |     |     | 5 0 0               | 0   |     |     |
|               |                       |               |            |                       |                       | 3 5 0               | 0   |     |     | 4 0 0               | 0   |     |     |
S c a l e - 2 ) : T P C C co n t a i n s 2 4 ( o r 4 8 ) w a r e h o u s e s ; T A T P h a s 2 M S mallABS L a r geABS 3 0 0 0
|     |     |     |     |     |     | 3 0 0 | 0   |     |     | 2 0 0 | 0 Small A | B S L a rg e ABS |     |
| --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | ----- | --------- | ---------------- | --- |
( o r 4 M ) s u b s c ri b e r s ; S m a l l B a n k h a s 1 0 M ( o r 2 0 M ) a c c o u n t s ; hguo 2 5 0 0 hguo
|       |     |     |     |     |     |           |     |     | Moto r | 1 0 0 | 0   |     | M o t o r |
| ----- | --- | --- | --- | --- | --- | --------- | --- | --- | ------ | ----- | --- | --- | --------- |
| K V S |     |     |     |     |     | rhT 2 0 0 | 0   |     |        |       | 0   |     |           |
s t o r e s 1 0 M ( o r 2 0 M ) K V p a i r s w i t h s k e w n e s s 0 . 9 9 a n d 120 0 1 5 0 0 1800 2 100 rhT 1750 1 7 7 0 1 7 9 0 1810 1 8 3 0
RW-ratio80%.Scale-1isthedefaultconfigurationin§7.1. Total memory used (MB) Total memory used (MB)
|     |     |     |     |     |     |     |     | (c) KVS |     |     |     | (d) TATP |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | -------- | --- |
AsshowninFig.12,FORDexhibitsthelowestmemory
Figure14:ThetransactionthroughputofMotorwhenvarying
overheadbystoringonlyoneversionofdata.Duetosupport- thememoryfootprintbychangingABS.
ingmulti-versioning,MotorandFaRMv2-DMconsumelarger
summary,Motortradessomeextramemoryspacetoachieve
memoryspacethanFORD.Nevertheless,Motorsavesmem-
betterperformancethanthesingle-versioningdesign,while
oryspaceinthreeaspects:(1)maintainingtheactuallymod-
alsoreducingthememoryoverheadasmuchaspossible.
ifiedattributesratherthanfullvaluesfordifferentversions;
7.6 VaryingMotorMemoryFootprint
(2)appropriatelyestimatingthesizeofattributebarwithout
wastingspace;and(3)configuringsuitableVNumsfordif- WestudyhowMotorperformswhenvaryingthememoryfoot-
ferentworkloadswithoutstoringunnecessaryversions.For printbasedonthebenchmarkScale-1(§7.5).Inthememory
example,Motorsupports4versionsofdatainTPCC,butonly pool,sincethefullvaluesalwaysexisttoprovidecomplete
consumes1.45×,insteadof4×,ofmemoryspaceoverFORD. userdata,wevaryMotormemoryfootprintbychangingthe
Suchmemorysavingisalsoshowninotherbenchmarks.In numberofversions(VNum)andtheattributebarsize(ABS).
TATP,Motoronlyincurs17.3%highermemoryoverheadthan AsMotorhassignificantlyreducedthememoryoverhead,the
FORD,sinceonly16%oftransactionsperformupdatesand roomtofurtherdecreasememoryfootprintislimited.Forex-
the modified attributes are small. In SmallBank and KVS, ample,Motoronlyreserves2versionsofdatainTATP.Thisis
Motorrespectivelyconsumes32.7%and37.7%highermem- theminimalnumberofversionsformulti-versioning.Hence,
oryspacethanFORD,sinceSmallBankandKVSarewrite- inTATP,weincreaseVNumupto8toincreasememoryfoot-
intensiveandrequiremoreversionsthanTATP.FaRMv2-DM prints.Forotherbenchmarks,sincetheirsuitableVNumsare
suffers from 14.6%-22.8% higher memory overhead than larger than 2,we decrease (and increase) VNum from the
Motorduetotworeasons.First,FaRMv2storesafull-sized suitableVNumto2(and8)tovarymemoryfootprints.When
valueforeachversion,whileMotoronlystoresthemodified changingVNum(2–8),thecorrespondingABSisestimated
attributesofvalues.Second,FaRMv2requirespointerstolink using the formula in § 4.2. Moreover,to varyABS,we fix
oldversionsinitsversionchain,whileMotordoesnotneed VNumtothesuitableVNumineachbenchmark,and(1)in-
suchpointerssinceourCVTstructureconsecutivelystoresall creaseABSto2–6×oftheestimatedABSusingthesuitable
theversions.Moreover,Fig.12bshowsthatwhenthebench- VNum,and(2)decreaseABSto1×ofthesumofdifferent
markscaleincreases,thegapofspaceconsumptionbetween TotAttrSizespertransaction.Fig.13–16showthetransaction
MotorandFORDgenerallykeepsstableinallbenchmarks. throughputandlatencyofMotorwhenvaryingmemoryfoot-
This demonstrates that our reduction of memory overhead prints.Wealsoreporttheperformanceandmemoryfootprints
still works even if the workload scale becomes larger. In ofFORDandFaRMv2-DMforcomparisons.
812    17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

)sµ( ycn F O R D F a R M v 2 - D M M ot o r )sµ( ycn F O R D F a R M v 2 - D M M ot o r )sµ 3 0 )sµ 1 6 0
| 8 0 |     | 5 0 |     |     | ( ycn 2 5 | M o t o r - S I |     | ( ycn | M o | t o r - S I |
| --- | --- | --- | --- | --- | --------- | --------------- | --- | ----- | --- | ----------- |
| 7 0 |     |     |     |     |           |                 |     | 1 2 0 |     |             |
6 0 4 0 etal elitn 2 0 M o t o r - S R etal elitn M o t o r - S R
| etal elitn 5 0 |     | etal elitn |     |     | 1 5     |     |     | 8 0     |     |     |
| -------------- | --- | ---------- | --- | --- | ------- | --- | --- | ------- | --- | --- |
| 4 0            |     | 3 0        |     |     | 1 0     |     |     | 4 0     |     |     |
| 3 0            |     |            |     |     | 5       |     |     |         |     |     |
| ecrep 2 0      |     | ecrep 2 0  |     |     | ecrep 0 |     |     | ecrep 0 |     |     |
20002 5 0 0 3 0 0 0 3 5 0 0 4 0 0 0 4 5 0 0 5 0 00 1000 1 5 0 0 2 0 0 0 2 5 0 0 30 0 0 3 5 00  h 100 0 2 0 0 0 3 0 0 0 4 0 0 0 5 0 00  h 100 0 2 0 0 0 3 0 0 0 4 0 0 0 5 0 00
 h t05 T o t a l  m e m o r y   u s e d   (M B )  h t05 To t al m e m o r y   u s e d  (M B ) t0 t9
|     |                 |     |              |             | 5   | T ransa c t io n  t h r o u ghpu | t  ( K  txn/ s ) | 9           | T ransa c t | io n  t h r o u ghpu t  ( K  txn/ s ) |
| --- | --------------- | --- | ------------ | ----------- | --- | -------------------------------- | ---------------- | ----------- | ----------- | ------------------------------------- |
|     | ( a )   T P C C |     | ( b )  S m a | l l B a n k |     |                                  |                  | (a ) TA T P |             |                                       |
)sµ( ycn 5 0 F O R D F a R M v 2 - D M M o t o r )sµ( ycn 1 6 F O R D F a R M v 2 - D M M ot o r )sµ 8 0 )sµ 1 5 0 0 0
|     |     |     |     |     | 7 0   | M o t o r - S I |     |             |     |                 |
| --- | --- | --- | --- | --- | ----- | --------------- | --- | ----------- | --- | --------------- |
| 4 0 |     | 1 2 |     |     | ( ycn |                 |     | ( ycn 1 2 0 | 0 0 | M o t o r - S I |
|     |     |     |     |     | 6 0   | M o t o r - S R |     |             |     | M o t o r - S R |
etal elitn 3 0 etal elitn 8 etal elitn 5 0 etal elitn 9 0 0 0
| 2 0     |                                |               |                     |                         | 4 0       |     |     | 6 0   | 0 0 |     |
| ------- | ------------------------------ | ------------- | ------------------- | ----------------------- | --------- | --- | --- | ----- | --- | --- |
|         |                                | 4             |                     |                         | 3 0       |     |     |       |     |     |
| 1 0     |                                |               |                     |                         |           |     |     | 3 0   | 0 0 |     |
| ecrep 0 |                                | ecrep 0       |                     |                         | ecrep 2 0 |     |     | ecrep |     |     |
|         |                                |               |                     |                         | 1 0       |     |     |       | 0   |     |
| 700     | 1 0 0 0 13 0 0 1 6 0 0 1 9 0 0 | 2 2 0 0 10001 | 5 0 0 2 0 0 0 2 5 0 | 0 3 0 0 0 3 5 00 4 0 00 |           |     |     |       |     |     |
 h t05 T o t al m e m o r y   u s e d  ( M B )  h T o t a l  m e m o r y   u s e d   (M B )  h 20 4 0 6 0 8 0 1 0 0 1 20  h 20 4 0 6 0 8 0 1 0 0 1 2 0
t05 t0 Trans a c ti o n   t h roug h put ( K  t xn/s ) t9 Trans a ct io n   t h rou g hpu t  ( K tx n /s )
|     | ( c )   K V S |     | ( d )   T A | T P | 5   |     |     | 9   |     |     |
| --- | ------------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
Figure 15: The comparisons of the 50th percentile latency (b) TPCC
Figure17:ThetransactionthroughputandlatencyonTATP
whenvaryingMotormemoryfootprintbychangingVNum.
andTPCCbenchmarkswhenusingdifferentisolationlevels.
| )sµ( ycn 10 0 0 0  | FORD FaRMv2-DM Motor | )sµ( ycn 1 1 0 | FORD FaRMv2-DM | Motor |                  |                       |              |              |              |                                 |
| ------------------ | -------------------- | -------------- | -------------- | ----- | ---------------- | --------------------- | ------------ | ------------ | ------------ | ------------------------------- |
|                    |                      |                |                |       | g e n e r a l ly | k e e p s s t a b l e | , s i n c e  | t h e tr a   | n s a c t io | n a b o r t s a r e h a r d l y |
| 8 0 0 0            |                      | 1 0 0          |                |       |                  |                       |              |              |              |                                 |
|                    |                      |                |                |       | r e d u c e d    | . T h i s d e m o n   | s t r a te s | t h e e f fi | c i e n c y  | o f o u r e s t i m a t i o n   |
| etal elitn 6 0 0 0 |                      | etal elitn 9 0 |                |       |                  |                       |              |              |              |                                 |
8 0
4 0 0 0 o n A B S , i .e . , re s e r v i n g a n e x a c ta n d s u f fi c ie n t s i z e f o r th e a t-
7 0
ecrep 2000 ecrep 60 t r i bu te b a r w i t h o u t w a s ti n g m e m o r y . F i g . 1 5 a n d 1 6 s h o w t h a t
 h 200025 0 0 3 0 0 0 3 5 0 0 4 0 0 0 4 50 05000  h 1000 1 5 0 0 2 0 0 0 2 5 0 0 30 0 0 3500 t h e l a t e n c y of M o t o r g r o w s w h e n i n c r e a s in g V N u m t o e n la r g e
| t99 | T o ta l  m e m o r y   u se d   (M B | ) t99 | T o t al m e m or y |   u s e d  (M B ) |     |     |     |     |     |     |
| --- | ------------------------------------- | ----- | ------------------- | ----------------- | --- | --- | --- | --- | --- | --- |
( a )   T P C C ( b )  S m a l l B a n k t h e m e m o r y f o o t p r in t , s in c e l a r g e - s i z e d C V T s i n c r e a se t h e
)sµ( ycn F O R D F a R M v 2 - D M M o to r )sµ( ycn F O R D F a R M v 2 - D M M ot or t r a n s m i s s i o n l a t e n c y . N e v e r t h e l e s s , M o t o r s t i l l e x h i b i t s l o w e r
| 8 0 |     | 1 0 0 |     |     |     |     |     |     |     |     |
| --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7 0 |     | 8 0   |     |     |     |     |     |     |     |     |
6 0 l a t e n c y t h a n F a R M v 2 - D M b y u s i n g th e C V T t o o b t a i n a l l
| etal elitn 5 0 |     | etal elitn 6 0 |     |     |     |     |     |     |     |     |
| -------------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
4 0 v e r s i o n s i n a s in g l e r e a d . I n T A T P , F O R D a c h i e v e s t h e l o w e s t
4 0
3 0 2 0 l a t e n c y d u e t o c o n s u m i n g l e s s R T T s t o f e t c h d a t a , a s a n a -
| ecrep 2 0 |     | ecrep 0 |     |     |     |     |     |     |     |     |
| --------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
 h 700 1 0 0 0 1 3 0 0 1 6 0 0 1 9 0 0 2 2 0 0  h 10001 5 0 0 2 0 0 0 2 5 0 0 3 0 0 0 3 5 00 4 000 l y z e d i n § 7 .4 . B u t i n o t h e r b e n c h m a r k s , M o t o r s h o w s l o w e r
| t99        | T o t al  m e m o r y  u s e d  ( M B ) | t99         | T o t a l  m e m o r y |   u s e d   (M B ) |              |                   |                 |         |           |                                |
| ---------- | --------------------------------------- | ----------- | ---------------------- | ------------------ | ------------ | ----------------- | --------------- | ------- | --------- | ------------------------------ |
|            |                                         |             |                        |                    | la t e n c y | t h a n F O R D a | t s u i t a b l | e V N u | m s d u e | t o e li m i n a t i n g t h e |
|            | ( c )  K V S                            |             | ( d )   T A            | T P                |              |                   |                 |         |           |                                |
| Figure 16: | The comparisons                         | of the 99th | percentile             | latency            |              |                   |                 |         |           |                                |
overheadsofwritinglogsforread-writetransactionsandvali-
whenvaryingMotormemoryfootprintbychangingVNum. datingversionsforread-onlytransactions.Insummary,these
resultsdemonstratethebenefitsofMotoroverstate-of-the-art
AsshowninFig.13,whendecreasingVNumfromthesuit-
ablevalue,thememoryfootprintsofMotorarereducedbyup systemswhenvaryingMotormemoryfootprint.
to22.8%andareclosetoFORDonmanyworkloads.Through 7.7 PerformanceofDifferentIsolationLevels
reducingthememoryfootprinttocontainlessversions,Motor
Motorsupportstwoisolationlevels,i.e.,serializability(SR)
stillachieveshigherthroughputthanFORDandFaRMv2-DM. andsnapshotisolation(SI).Fig.17showthatMotor-SIgener-
ThereasonisthatcomparedwithFORD,(1)Motorreserves
allyachieveslowerlatencyandhigherthroughputthanMotor-
| more than | one version to | avoid blocking | reads | and reduce |     |     |     |     |     |     |
| --------- | -------------- | -------------- | ----- | ---------- | --- | --- | --- | --- | --- | --- |
SRonbothread-intensive(TATP)andwrite-intensive(TPCC)
| transaction | aborts; (2)Motordoesnotneedtoadditionally |     |     |     |     |     |     |     |     |     |
| ----------- | ----------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
workloadsbyeliminatingthevalidationphaseforread-write
writeundologsandtheread-onlytransactionsdonotneedto
|     |     |     |     |     | transactions. | ComparedwithTATP,Motor-SIshowshigher |     |     |     |     |
| --- | --- | --- | --- | --- | ------------- | ------------------------------------ | --- | --- | --- | --- |
validateversionswithmulti-versioning.Moreover,compared throughputimprovementinTPCC,sinceTPCCaccessesmore
withFaRMv2-DM,(1)ourCVTstructureavoidschainwalk-
read-onlydatapertransactionandfeatureshigherread-write
| ingtoreducelatency; | (2)ourMVCCprotocolsavesRTTs |     |     |     |              |               |      |            |     |             |
| ------------------- | --------------------------- | --- | --- | --- | ------------ | ------------- | ---- | ---------- | --- | ----------- |
|                     |                             |     |     |     | contentions, | thus allowing | more | throughput |     | improvement |
viaefficientrequestbatching(§7.4).Whenslightlyincreas-
whenrelaxingtheisolationrequirement.
ingVNum(e.g.,from4to6inKVS),Motorstillconsumes
7.8 UsingPMinMemoryPool
lessmemorythanFaRMv2-DMthankstoonlystoringneces-
sarymodificationsinthedeltaarea.Hence,comparedwith BothDRAMandpersistentmemory(PM)canbeusedina
FaRMv2-DM,Motorcanstoremoreversionsusingasmaller memorypool[69,86].Weleveragesix128GBIntelOptane
amountofmemory. In fact,when VNum increases from 2 PM modules in each memory node to evaluate the perfor-
to 8 (4×), the Motor memory footprint only increases by manceofMotoronTPCC.WeuseRDMAREAD-after-WRITE
1.4×/2.1×/2×/1.9×onTPCC/SmallBank/TATP/KVS.Fig.14 to flush the written data from remote RNIC to PM for re-
showsthatwhenfixingVNumandreducingABSfromthe motedatapersistency[84].Fig.18showsthatthethroughput
suitableABS,thethroughputdecreases,sinceasmall-sized onlydecreasesby13.1%onPMduetothelimitedPMband-
attributebarwouldresultinmorethanoneVcellsbeingin- width[80,84].TheresultsdemonstratethatMotorefficiently
validatedingarbagecollectiontoincreaseaborts.However, worksonbothDRAMandPM,thusofferinggoodportability
whenincreasingABSfromthesuitableABS,thethroughput forapplicationstorunondifferenttypesofmemorydevices.
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation    813

1 4 0
|     | )sµ( ycnetal elitnecrep ht05 8 0 |     |     | )sµ( ycnetal elitnecrep ht99 1 | 5 0 0 0 |     |     | )s/n |     |     |     |
| --- | -------------------------------- | --- | --- | ------------------------------ | ------- | --- | --- | ---- | --- | --- | --- |
7 0 M o t o r - P M 1 2 0 0 0 M o t o r - P M xt K 1 2 0 r e co v e r y   fin i sh es
|     | 6 0 |                     |     |     |           |                   |     | 1 0 0    |                           |     |     |
| --- | --- | ------------------- | --- | --- | --------- | ----------------- | --- | -------- | ------------------------- | --- | --- |
|     | 5 0 | M o t o r - D R A M |     |     | 9 0 0 0 M | o t o r - D R A M |     | ( tu 8 0 |                           |     |     |
|     | 4 0 |                     |     |     | 6 0 0 0   |                   |     |          | f a i l u r e   o c c u r | s   |     |
|     | 3 0 |                     |     |     |           |                   |     | p 6 0    |                           |     |     |
2 0 3 0 0 0 h gu 4 0 g e n e r a t i n g   n e w   c o o r d i n a t or s
|     | 1 0 |         |           |     | 0     |           |       | o 2 0 |                         |        |                              |
| --- | --- | ------- | --------- | --- | ----- | --------- | ----- | ----- | ----------------------- | ------ | ---------------------------- |
|     |     |         |           |     |       |           |       | rh 0  | n e w   c o o r d i n a | t o rs | ta k e   o v e r   t a s k s |
|     | 2 0 | 4 0 6 0 | 8 0 1 0 0 |     | 2 0 4 | 0 6 0 8 0 | 1 0 0 | T     |                         |        |                              |
T ra nsa c ti o n   t h r o u g hp u t (K  tx n /s) T ra nsa c ti o n   t h r o ug hp u t (K  tx n /s) -200 - 1 5 0 -1 0 0 - 5 0 0 5 0 1 0 0 1 5 0 200 2 5 0 3 0 0 3 50
T im e   ( m s )
Figure18:ThetransactionthroughputandlatencyonTPCC
(a) Tolerating coordinator failures
|                                             |     |     |     |     |     |     |     |             | Primary failure |     | Backup failure |
| ------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----------- | --------------- | --- | -------------- |
| benchmarkwhenusingDRAMandPMinthememorypool. |     |     |     |     |     |     |     | )s/n1 1 4 0 |                 |     |                |
backup recovery
|     |                |     |     |     |     |     |     | xt K 2 0 |     | finishes |     |
| --- | -------------- | --- | --- | --- | --- | --- | --- | -------- | --- | -------- | --- |
| 7.9 | FaultTolerance |     |     |     |     |     |     | 100      |     |          |     |
( tu 8 0
|     |     |     |     |     |     |     |     | 6 0 | fa ilu re  o c c u r s |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- |
W e l e v er a g e T P C C t o sh o w th e r e s il ie n c e o f M o t o r u n d er co o r - p h p r i m a r y
|     |                |              |           |           |                 |              |              | gu 4 0 | re co ve ry  s t a r t s |     | r e c o v e r y |
| --- | -------------- | ------------ | --------- | --------- | --------------- | ------------ | ------------ | ------ | ------------------------ | --- | --------------- |
| din | a t o r f a il | ur e s i n c | om p u te | p o o l a | n d r e pl i ca | f a i lu r e | s in m e m - | o 2 0  |                          |     |                 |
|     |                |              |           |           |                 |              |              | rh 0   |                          |     | f i n i s h e s |
T
orypool.Wereporttheinstantaneoustransactionthroughput -200 -150 -100 -50 0 50 100 150 200 250 300 350
Time (ms)
in1msintervalovertime(thecrashoccursattime0).
(b) Tolerating replica failures
Figure19:TheMotor’stransactionthroughputonTPCCover
Fig.19ashowsthethroughputtimelineofrecoveringco-
ordinators.Werun84coordinatorsand60ofthemfailatthe timeunder(a)coordinatorfailuresand(b)replicafailures.
| same | time. | Motorthen | generates |     | 60 new | coordinators | and |     |     |     |     |
| ---- | ----- | --------- | --------- | --- | ------ | ------------ | --- | --- | --- | --- | --- |
datareplication[83]areproposedtoimprovetheperformance.
establishesnetworkconnections,whichconsumesabout170 Theabovesystemsworkonthemonolithicarchitecture,while
ms.Afterwards,thenewcoordinatorstakeovertheremaining ourMotortargetsonthedisaggregatedarchitecture.
tasks.InMotor,eachcoordinatorwriteslocaloperationlogs MemoryDisaggregation.Memorydisaggregationimproves
torecordtheoperationsduringexecution. Theseoperation the resource utilization. Existing studies explore memory
logsconsumeverysmallspace(upto556Bpertransaction)
disaggregationinmanyareas,suchashardwaredesigns[35,
andthelogspacecanbereusedacrosstransactions.Thenew 50,51],operatingsystems[65],indexes[53,75,86],key-value
coordinatorsusetheoperationlogsoffailedonestoresume stores[45,49,66,69],networking[29,67],erasurecoding[47,
in-flightcommitsandunlockCVTstoavoidstarvation.After
85],swapping[15,20,33,62],andmemorymanagements[14,
recovery,Motorregainspeakthroughput. 46,48,54,70,72,73].Infact,Motorfocusesontransaction
Fig.19bshowstheresultsofrecoveringreplicas.Consid-
processing,whichisorthogonaltotheabovesystems.Though
eringthattheCUSTOMERtableisfrequentlyused,werespec- FORD[84]supportstransactionsondisaggregatedmemory,
tivelyallowtheprimaryandonebackupofCUSTOMERtofail, itadoptssingle-versioning,whichlimitstheconcurrencyand
i.e.,cannotbeaccessed.Asmallportionoftransactionsthat
incurshighloggingoverheads.UnlikeFORD,Motorenables
donotaccessthefailedreplicasarenormallyexecuted,and multi-versioningtoaddresstheselimitations.
hencethethroughputdoesnotbecome0.Motorhandlesthe Multi-VersioningSchemes.Multi-versioningschemeshave
primaryfailurebypromotingabackupasthenewprimaryand beenadoptedtosupportdistributedtransactions.Theyfocus
addingabackup.Motortoleratesthebackupfailurebyadding onhigh-performanceMVCCprotocols[28,43,57,64],times-
abackup.Recoveringtheprimaryconsumesmoretime,since
tampgenerations[38,76,81],garbagecollections[16,44],and
Motorneeds to change the viewofprimaries forcoordina- verifications[21].Thesesystemsaredesignedfortraditional
tors,andthenewprimaryisnotvisibleuntiltheupdatesare monolithicservers,whichdonotfitthedisaggregatedmem-
committedintoalivereplicas.Addingabackuprequiresdata ory.Unlikethesestudies,ourCVTstructureanddistributed
migration,duringwhichMotorallowsamemorynodetouse transactionprotocolefficientlysupportmulti-versioningon
| RDMA | WRITE | to  | transmit | DB tables, | CVTs, | and | attribute |     |     |     |     |
| ---- | ----- | --- | -------- | ---------- | ----- | --- | --------- | --- | --- | --- | --- |
thedisaggregatedmemory.
barstoanothermemorynode.Writerequeststothereplicas 9 Conclusion
involvedinmigrationareblockedtoguaranteethedatacon-
ThispaperproposesMotor,anefficientdistributedtransac-
sistencyamongreplicas.SincetheCUSTOMERtableislarge,
tionprocessingsystemformulti-versioninginthecontextof
themigrationconsumesnearly200ms.Wealsoexaminethat
|     |     |     |     |     |     |     |     | disaggregatedmemory. |     | Motorproposesanewconsecutive |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | ---------------------------- | --- |
ifasmallDISTRICTtablefails,themigrationconsumesonly
|     |     |     |     |     |     |     |     | version tuple | structure | to efficiently | organize multiple ver- |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --------- | -------------- | ---------------------- |
1.1ms.Furtheroptimizationonmigrationisoutofourscope. sionsofdatainmemorypool.Ontopofthis,Motordesignsa
| In practice,our |     | ms-scale |     | recovery | is acceptable |     | given that |     |     |     |     |
| --------------- | --- | -------- | --- | -------- | ------------- | --- | ---------- | --- | --- | --- | --- |
fullyone-sidedRDMA-orientedMVCCprotocoltoacceler-
priorsystems[27,64,66]alsoprovidems-scalerecovery.
atetransactions.Extensiveexperimentalresultsdemonstrate
8 RelatedWork
thatMotorsignificantlyimprovesthetransactionthroughput
FastDistributedTransactions.Fastdistributedtransaction andreducesthelatencywithmoderatememoryoverhead.
Acknowledgments
processingisakeypillarindistributedsystems.Manysystems
useRDMAtoprocesstransactions[22,26,27,39,41,58,64, ThisworkwassupportedinpartbyNationalNaturalScience
77,78].Somestudiestransformadistributedtransactiontoa FoundationofChina(NSFC)underGrantNo.62125202and
localonetoreducethecommunicationoverheads[19,40,52]. U22B2022.Wearegratefultoanonymousreviewersfortheir
Someprotocolsonconcurrencycontrol[55,74,79,82]and constructivesuggestionsandfeedback.
814    17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| References |     |     |     |     | [15] EmmanuelAmaro,ChristopherBranner-Augmon,Zhi- |     |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- |
hongLuo,AmyOusterhout,MarcosK.Aguilera,Au-
[1] Telecomapplicationtransactionprocessingbenchmark. rojitPanda,SylviaRatnasamy,andScottShenker. Can
http://tatpbenchmark.sourceforge.net,2011. farmemoryimprovejobthroughput? InEuroSys’20:
FifteenthEuroSysConference2020,Heraklion,Greece,
| [2] Intel® | rackscale | design | architecture. | https://www. |     |     |     |     |     |     |     |
| ---------- | --------- | ------ | ------------- | ------------ | --- | --- | --- | --- | --- | --- | --- |
April27-30,2020,pages14:1–14:16.ACM,2020.
intel.com/content/dam/www/public/us/en/doc
uments/white-papers/rack-scale-design-arc [16] JanBöttcher,ViktorLeis,ThomasNeumann,andAlfons
hitecture-white-paper.pdf,2018.
|                                  |     |     |     |                | Kemper.      | Scalable | garbage                        | collection |     | for in-memory |     |
| -------------------------------- | --- | --- | --- | -------------- | ------------ | -------- | ------------------------------ | ---------- | --- | ------------- | --- |
|                                  |     |     |     |                | MVCCsystems. |          | Proc.VLDBEndow.,13(2):128–141, |            |     |               |     |
| [3] VmwareResearch:Remotememory. |     |     |     | https://resear |              |          |                                |            |     |               |     |
2019.
ch.vmware.com/projects/remote-memory,2021.
|     |     |     |     |     | [17] EricBrewer. | Captwelveyearslater:Howthe"rules" |     |     |     |     |     |
| --- | --- | --- | --- | --- | ---------------- | --------------------------------- | --- | --- | --- | --- | --- |
[4] Smallbankbenchmark. https://hstore.cs.brown. Computer,45(2):23–29,2012.
havechanged.
edu/documentation/deployment/benchmarks/sm
allbank,2022. [18] EricABrewer. Towardsrobustdistributedsystems. In
PODC,volume7,pages343477–343502.Portland,OR,
| [5] Precedencegraph. |     | https://en.wikipedia.org/wik |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | ---------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2000.
i/Precedence_graph,2023.
|     |     |     |     |     | [19] Qingchao | Cai, | Wentian | Guo, Hao | Zhang, | Divyakant |     |
| --- | --- | --- | --- | --- | ------------- | ---- | ------- | -------- | ------ | --------- | --- |
[6] Rdmaawarenetworksprogrammingusermanualv1.7.
|     |     |     |     |     | Agrawal,Gang |     | Chen,Beng | Chin | Ooi,Kian-Lee |     | Tan, |
| --- | --- | --- | --- | --- | ------------ | --- | --------- | ---- | ------------ | --- | ---- |
https://docs.nvidia.com/networking/display
|     |     |     |     |     | YongMengTeo,andShengWang. |     |     |     | Efficientdistributed |     |     |
| --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | -------------------- | --- | --- |
/rdmaawareprogrammingv17/transport+modes,
|     |     |     |     |     | memorymanagementwithRDMAandcaching. |     |     |     |     |     | Proc. |
| --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- | --- | --- | ----- |
2023.
VLDBEndow.,11(11):1604–1617,2018.
| [7] Computeexpresslink®. |     |     | https://www.computeexp |     |                    |     |       |             |        |          |     |
| ------------------------ | --- | --- | ---------------------- | --- | ------------------ | --- | ----- | ----------- | ------ | -------- | --- |
|                          |     |     |                        |     | [20] Irina Calciu, | M.  | Talha | Imran, Ivan | Puddu, | Sanidhya |     |
resslink.org,2024.
Kashyap,HasanAlMaruf,OnurMutlu,andAasheesh
|                                    |     |     |     |                | Kolli.  | Rethinkingsoftwareruntimesfordisaggregated |     |           |     |               |     |
| ---------------------------------- | --- | --- | --- | -------------- | ------- | ------------------------------------------ | --- | --------- | --- | ------------- | --- |
| [8] Intel®DataDirectI/OTechnology. |     |     |     | https://www.in |         |                                            |     |           |     |               |     |
|                                    |     |     |     |                | memory. | In ASPLOS                                  |     | ’21: 26th | ACM | International |     |
tel.com/content/www/us/en/io/data-direct-i
ConferenceonArchitecturalSupportforProgramming
-o-technology.html,2024.
LanguagesandOperatingSystems,VirtualEvent,USA,
April19-23,2021,pages79–92.ACM,2021.
| [9] MySQL: | The                         | world’s | most popular | open source |                |        |      |       |          |     |         |
| ---------- | --------------------------- | ------- | ------------ | ----------- | -------------- | ------ | ---- | ----- | -------- | --- | ------- |
| database.  | https://www.mysql.com,2024. |         |              |             |                |        |      |       |          |     |         |
|            |                             |         |              |             | [21] Yun-Sheng | Chang, | Ralf | Jung, | Upamanyu |     | Sharma, |
JosephTassarotti,M.FransKaashoek,andNickolaiZel-
[10] PostgreSQL:TheWorld’sMostAdvancedOpenSource
|                     |     |     |                             |     | dovich. | Verifying | vmvcc, | a high-performance |     |     | trans- |
| ------------------- | --- | --- | --------------------------- | --- | ------- | --------- | ------ | ------------------ | --- | --- | ------ |
| RelationalDatabase. |     |     | https://www.postgresql.org, |     |         |           |        |                    |     |     |        |
actionlibraryusingmulti-versionconcurrencycontrol.
2024.
In17thUSENIXSymposiumonOperatingSystemsDe-
[11] Serializability. https://en.wikipedia.org/wiki/ signandImplementation,OSDI2023,Boston,MA,USA,
Database_transaction_schedule#Serializable, July10-12,2023,pages871–886.USENIXAssociation,
2023.
2024.
[12] Snapshotisolation. https://en.wikipedia.org/w [22] Yanzhe Chen, Xingda Wei, Jiaxin Shi, Rong Chen,
|     |     |     |     |     | and Haibo | Chen. | Fast | and general | distributed |     | trans- |
| --- | --- | --- | --- | --- | --------- | ----- | ---- | ----------- | ----------- | --- | ------ |
iki/Snapshot_isolation,2024.
|     |     |     |     |     | actionsusingRDMAandHTM. |     |     |     | InProceedingsofthe |     |     |
| --- | --- | --- | --- | --- | ----------------------- | --- | --- | --- | ------------------ | --- | --- |
[13] Tpc-cbenchmark. http://www.tpc.org/tpcc,2024. EleventhEuropeanConferenceonComputerSystems,
EuroSys2016,London,UnitedKingdom,April18-21,
[14] MarcosK.Aguilera,NadavAmit,IrinaCalciu,Xavier 2016,pages26:1–26:17.ACM,2016.
| Deguillard,JayneelGandhi,Stanko |     |     |     | Novakovic,Arun |     |     |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- |
Ramanathan,PratapSubrahmanyam,LalithSuresh,Ki- [23] BrianF.Cooper,AdamSilberstein,ErwinTam,Raghu
ranTati,RajeshVenkatasubramanian,andMichaelWei. Ramakrishnan,andRussellSears. Benchmarkingcloud
Remoteregions:asimpleabstractionforremotemem- serving systems with YCSB. In Proceedings of the
ory. In 2018 USENIX Annual Technical Conference, 1stACMSymposiumonCloudComputing,SoCC2010,
USENIXATC2018,Boston,MA,USA,July11-13,2018, Indianapolis,Indiana,USA,June 10-11,2010,pages
| pages775–787.USENIXAssociation,2018. |     |     |     |     | 143–154.ACM,2010. |     |     |     |     |     |     |
| ------------------------------------ | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- |
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation    815

[24] JamesC.Corbett,JeffreyDean,MichaelEpstein,An- [31] Cary Gray and David Cheriton. Leases: An efficient
drew Fikes, Christopher Frost, J. J. Furman, Sanjay fault-tolerantmechanismfordistributedfilecachecon-
Ghemawat,AndreyGubarev,ChristopherHeiser,Peter sistency. ACM SIGOPS Operating Systems Review,
Hochschild,WilsonC.Hsieh,SebastianKanthak,Eu- 23(5):202–210,1989.
geneKogan,HongyiLi,AlexanderLloyd,SergeyMel-
|     |     |     |     |     |     |     | [32] MartinGrund,JensKrüger,HassoPlattner,Alexander |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- |
nik,DavidMwaura,DavidNagle,SeanQuinlan,Rajesh
Zeier,PhilippeCudré-Mauroux,andSamuelMadden.
Rao,LindsayRolig,YasushiSaito,MichalSzymaniak,
|             |         |      |       |          |           |     | HYRISE-Amainmemoryhybridstorageengine. |     |     |     |     | Proc. |
| ----------- | ------- | ---- | ----- | -------- | --------- | --- | -------------------------------------- | --- | --- | --- | --- | ----- |
| Christopher | Taylor, | Ruth | Wang, | and Dale | Woodford. |     |                                        |     |     |     |     |       |
VLDBEndow.,4(2):105–116,2010.
| Spanner: | Google’s | globally-distributed |     |     | database. | In  |     |     |     |     |     |     |
| -------- | -------- | -------------------- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
10thUSENIXSymposiumonOperatingSystemsDesign
|     |     |     |     |     |     |     | [33] JunchengGu,YoungmoonLee,YiwenZhang,Mosharaf |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- |
andImplementation,OSDI2012,Hollywood,CA,USA,
|     |     |     |     |     |     |     | Chowdhury,andKangG.Shin. |     |     |     | Efficientmemorydis- |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | --- | --- | ------------------- | --- |
October8-10,2012,pages251–264.USENIXAssocia-
|            |     |     |     |     |     |     | aggregationwithinfiniswap.                     |     |     | In14thUSENIXSympo- |     |     |
| ---------- | --- | --- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | ------------------ | --- | --- |
| tion,2012. |     |     |     |     |     |     | siumonNetworkedSystemsDesignandImplementation, |     |     |                    |     |     |
NSDI2017,Boston,MA,USA,March27-29,2017,pages
[25] CristianDiaconu,CraigFreedman,ErikIsmert,Per-Åke
649–667.USENIXAssociation,2017.
Larson,PravinMittal,RyanStonecipher,NitinVerma,
| and Mike      | Zwilling. | Hekaton: | SQL            | server’s | memory- |     |             |            |                 |        |             |          |
| ------------- | --------- | -------- | -------------- | -------- | ------- | --- | ----------- | ---------- | --------------- | ------ | ----------- | -------- |
|               |           |          |                |          |         |     | [34] Rachid | Guerraoui, | Antoine         | Murat, | Javier      | Picorel, |
| optimizedOLTP |           | engine.  | In Proceedings |          | ofthe   | ACM |             |            |                 |        |             |          |
|               |           |          |                |          |         |     | Athanasios  |            | Xygkis, Huabing | Yan,   | and Pengfei | Zuo.     |
SIGMODInternationalConferenceonManagementof
ukharon:Amembershipserviceformicrosecondappli-
Data,SIGMOD2013,NewYork,NY,USA,June22-27, cations. In2022USENIXAnnualTechnicalConference,
2013,pages1243–1254.ACM,2013.
|     |     |     |     |     |     |     | USENIX | ATC | 2022, Carlsbad, |     | CA, USA, | July 11-13, |
| --- | --- | --- | --- | --- | --- | --- | ------ | --- | --------------- | --- | -------- | ----------- |
2022,pages101–120.USENIXAssociation,2022.
[26] AleksandarDragojevic,DushyanthNarayanan,Miguel
Castro,and Orion Hodson. Farm: Fast remote mem- [35] ZhiyuanGuo,YizhouShan,XuhaoLuo,YutongHuang,
ory. InProceedingsofthe11thUSENIXSymposiumon and Yiying Zhang. Clio: a hardware-software co-
NetworkedSystemsDesignandImplementation,NSDI
|     |     |     |     |     |     |     | designeddisaggregatedmemorysystem. |     |     |     |     | In ASPLOS |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --------- |
2014,Seattle,WA,USA,April2-4,2014,pages401–414. ’22: 27th ACM International Conference on Architec-
USENIXAssociation,2014.
turalSupportforProgrammingLanguagesandOperat-
ingSystems,Lausanne,Switzerland,28February2022-
| [27] Aleksandar | Dragojevic, |     | Dushyanth | Narayanan, |     | Ed- |     |     |     |     |     |     |
| --------------- | ----------- | --- | --------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
4March2022,pages417–433.ACM,2022.
| mund B. | Nightingale, |     | Matthew | Renzelmann, |     | Alex |     |     |     |     |     |     |
| ------- | ------------ | --- | ------- | ----------- | --- | ---- | --- | --- | --- | --- | --- | --- |
Shamis, Anirudh Badam, and Miguel Castro. No [36] DougHakkarinen,PanruoWu,andZizhongChen. Fail-
compromises:distributedtransactionswithconsistency,
stopfailurealgorithm-basedfaulttoleranceforcholesky
availability,andperformance.InProceedingsofthe25th decomposition. IEEE Transactions on Parallel and
| Symposium | on  | Operating | Systems | Principles, |     | SOSP |     |     |     |     |     |     |
| --------- | --- | --------- | ------- | ----------- | --- | ---- | --- | --- | --- | --- | --- | --- |
DistributedSystems,26(5):1323–1335,2015.
2015,Monterey,CA,USA,October4-7,2015,pages54–
70.ACM,2015. [37] Chi Ho, Robbert van Renesse, Mark Bickford, and
|     |     |     |     |     |     |     | Danny | Dolev. | Nysiad: Practical |     | protocol | transforma- |
| --- | --- | --- | --- | --- | --- | --- | ----- | ------ | ----------------- | --- | -------- | ----------- |
[28] TamerEldeeb,XinchengXie,PhilipA.Bernstein,Asaf tiontotoleratebyzantinefailures. In5thUSENIXSym-
Cidon,andJunfengYang.Chardonnay:Fastandgeneral
posiumonNetworkedSystemsDesign&Implementa-
datacentertransactionsforon-diskdatabases. In17th tion,NSDI2008,April16-18,2008,SanFrancisco,CA,
USENIXSymposiumonOperatingSystemsDesignand USA,Proceedings,pages175–188.USENIXAssocia-
| Implementation,OSDI2023,Boston,MA,USA,July10- |     |     |     |     |     |     | tion,2008. |     |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- |
12,2023,pages343–360.USENIXAssociation,2023.
|     |     |     |     |     |     |     | [38] Tianyang |     | Jiang, Guangyan | Zhang, | Zhiyue | Li, and |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | --------------- | ------ | ------ | ------- |
[29] PeterXiangGao,AkshayNarayan,SagarKarandikar, WeiminZheng. Aurogon:Tamingabortsinallphases
JoaoCarreira,SangjinHan,RachitAgarwal,SylviaRat- fordistributedIn-Memorytransactions.In20thUSENIX
nasamy,andScottShenker. Networkrequirementsfor Conference on File and Storage Technologies (FAST
resourcedisaggregation.In12thUSENIXSymposiumon 22),pages217–232,SantaClara,CA,February2022.
OperatingSystemsDesignandImplementation,OSDI USENIXAssociation.
2016,Savannah,GA,USA,November2-4,2016,pages
|     |     |     |     |     |     |     | [39] Anuj | Kalia,MichaelKaminsky,andDavid |     |     |     | G. Ander- |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------------------------------ | --- | --- | --- | --------- |
249–264.USENIXAssociation,2016.
|     |     |     |     |     |     |     | sen. | Fasst:Fast,scalableandsimpledistributedtrans- |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --------------------------------------------- | --- | --- | --- | --- |
[30] SethGilbertandNancyLynch. Brewer’sconjectureand actions with two-sided (RDMA) datagram rpcs. In
thefeasibilityofconsistent,available,partition-tolerant 12th USENIX Symposium on Operating Systems De-
webservices. AcmSigactNews,33(2):51–59,2002. signandImplementation,OSDI2016,Savannah,GA,
816    17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

USA,November 2-4,2016,pages 185–201. USENIX [47] Youngmoon Lee,Hasan AlMaruf,MosharafChowd-
Association,2016. hury,AsafCidon,andKangG.Shin. Hydra:Resilient
|     |     |     |     |     | andhighlyavailableremotememory. |     |     | In20thUSENIX |     |
| --- | --- | --- | --- | --- | ------------------------------- | --- | --- | ------------ | --- |
[40] AntoniosKatsarakis,YijunMa,ZhaoweiTan,Andrew
|     |     |     |     |     | Conference | on File | and Storage | Technologies, | FAST |
| --- | --- | --- | --- | --- | ---------- | ------- | ----------- | ------------- | ---- |
Bainbridge,MatthewBalkwill,AleksandarDragojevic, 2022, Santa Clara, CA, USA, February 22-24, 2022,
BorisGrot,BozidarRadunovic,andYongguangZhang.
pages181–198.USENIXAssociation,2022.
| Zeus: | locality-aware | distributed | transactions. | In Eu- |     |     |     |     |     |
| ----- | -------------- | ----------- | ------------- | ------ | --- | --- | --- | --- | --- |
roSys’21:SixteenthEuropeanConferenceonComputer [48] HuaichengLi,DanielS.Berger,LisaHsu,DanielErnst,
Systems,Online Event,United Kingdom,April 26-28, Pantea Zardoshti, Stanko Novakovic, Monish Shah,
2021,pages145–161.ACM,2021. SamirRajadnya,ScottLee,IshwarAgarwal,MarkD.
|     |     |     |     |     | Hill,MarcusFontoura,andRicardoBianchini. |     |     |     | Pond: |
| --- | --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | ----- |
[41] Daehyeok Kim, Amirsaman Memaripour, Anirudh Cxl-basedmemorypoolingsystemsforcloudplatforms.
| Badam, | Yibo Zhu, | Hongqiang | Harry Liu, | Jitu Pad- |     |     |     |     |     |
| ------ | --------- | --------- | ---------- | --------- | --- | --- | --- | --- | --- |
InProceedingsofthe28thACMInternationalConfer-
hye, Shachar Raindel, Steven Swanson, Vyas Sekar, ence on ArchitecturalSupportforProgramming Lan-
| and Srinivasan | Seshan. | Hyperloop: | group-based | nic- |     |     |     |     |     |
| -------------- | ------- | ---------- | ----------- | ---- | --- | --- | --- | --- | --- |
guagesandOperatingSystems,Volume2,ASPLOS2023,
offloadingtoacceleratereplicatedtransactionsinmulti- Vancouver,BC,Canada,March25-29,2023,pages574–
| tenant | storage systems. | In  | Proceedings of | the 2018 | 587.ACM,2023. |     |     |     |     |
| ------ | ---------------- | --- | -------------- | -------- | ------------- | --- | --- | --- | --- |
ConferenceoftheACMSpecialInterestGrouponData
Communication,SIGCOMM2018,Budapest,Hungary, [49] PengfeiLi,YuHua,PengfeiZuo,ZhangyuChen,and
August20-25,2018,pages297–312.ACM,2018. JiajieSheng.ROLEX:Ascalablerdma-orientedlearned
|                                                |     |     |     |      | key-valuestorefordisaggregatedmemorysystems. |     |     |     | In  |
| ---------------------------------------------- | --- | --- | --- | ---- | -------------------------------------------- | --- | --- | --- | --- |
| [42] LeslieLamport,DahliaMalkhi,andLidongZhou. |     |     |     | Ver- |                                              |     |     |     |     |
21stUSENIXConferenceonFileandStorageTechnolo-
ticalpaxosandprimary-backupreplication. InProceed- gies,FAST2023,SantaClara,CA,USA,February21-23,
ings of the 28th Annual ACM Symposium on Princi- 2023,pages99–114.USENIXAssociation,2023.
plesofDistributedComputing,PODC2009,Calgary,
Alberta,Canada,August10-12,2009,pages312–313. [50] Kevin T. Lim, Jichuan Chang, Trevor N. Mudge,
| ACM,2009. |     |     |     |     | ParthasarathyRanganathan,StevenK.Reinhardt,and |             |               |        |         |
| --------- | --- | --- | --- | --- | ---------------------------------------------- | ----------- | ------------- | ------ | ------- |
|           |     |     |     |     | Thomas                                         | F. Wenisch. | Disaggregated | memory | for ex- |
[43] Per-ÅkeLarson,SpyrosBlanas,CristianDiaconu,Craig pansion and sharing in blade servers. In 36th Inter-
Freedman,JigneshM.Patel,andMikeZwilling. High- nationalSymposiumonComputerArchitecture(ISCA
performanceconcurrencycontrolmechanismsformain-
2009),June20-24,2009,Austin,TX,USA,pages267–
| memorydatabases. |     | Proc.VLDBEndow.,5(4):298–309, |     |     | 278.ACM,2009. |     |     |     |     |
| ---------------- | --- | ----------------------------- | --- | --- | ------------- | --- | --- | --- | --- |
2011.
[51] KevinT.Lim,YoshioTurner,JoseRenatoSantos,Alvin
| [44] Juchang | Lee, Hyungyu | Shin, | Chang Gyoo | Park, |     |     |     |     |     |
| ------------ | ------------ | ----- | ---------- | ----- | --- | --- | --- | --- | --- |
AuYoung,JichuanChang,ParthasarathyRanganathan,
Seongyun Ko,Jaeyun Noh,Yongjae Chuh,Wolfgang andThomasF.Wenisch. System-levelimplicationsof
Stephan, and Wook-Shin Han. Hybrid garbage col- disaggregatedmemory. In18thIEEEInternationalSym-
lection for multi-version concurrency control in SAP posium on HighPerformance ComputerArchitecture,
HANA. InProceedingsofthe2016InternationalCon- HPCA2012,NewOrleans,LA,USA,25-29February,
ferenceonManagementofData,SIGMODConference 2012,pages189–200.IEEEComputerSociety,2012.
2016,SanFrancisco,CA,USA,June26-July01,2016,
pages1307–1318.ACM,2016. [52] QianLin,PengfeiChang,GangChen,BengChinOoi,
|     |     |     |     |     | Kian-LeeTan,andZhengkuiWang. |     |     | Towardsanon-2pc |     |
| --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --------------- | --- |
[45] Se Kwon Lee, Soujanya Ponnapalli, Sharad Singhal, transactionmanagementindistributeddatabasesystems.
MarcosK.Aguilera,KimberlyKeeton,andVijayChi- In Proceedings of the 2016 International Conference
dambaram. DINOMO: an elastic, scalable, high- on ManagementofData,SIGMOD Conference 2016,
performancekey-valuestorefordisaggregatedpersistent
SanFrancisco,CA,USA,June26-July01,2016,pages
memory. Proc.VLDBEndow.,15(13):4023–4037,2022. 1659–1674.ACM,2016.
[46] Seung-seob Lee, Yanpeng Yu, Yupeng Tang, Anurag [53] XuchuanLuo,PengfeiZuo,JiachengShen,JiazhenGu,
Khandelwal,LinZhong,andAbhishekBhattacharjee. Xin Wang, Michael R. Lyu, and Yangfan Zhou and.
MIND:in-networkmemorymanagementfordisaggre- SMART: A high-performance adaptive radix tree for
gateddatacenters. InSOSP’21: ACMSIGOPS28th disaggregatedmemory. In17thUSENIXSymposiumon
Symposium on Operating Systems Principles,Virtual OperatingSystemsDesignandImplementation,OSDI
Event/Koblenz,Germany,October26-29,2021,pages 2023,Boston,MA,USA,July10-12,2023,pages553–
| 488–504.ACM,2021. |     |     |     |     | 566.USENIXAssociation,2023. |     |     |     |     |
| ----------------- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | --- |
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation    817

[54] Teng Ma, Mingxing Zhang, Kang Chen, Zhuo Song, [63] SQL Server. Set transaction isolation level. https:
YongweiWu,andXuehaiQian. Asymnvm:Anefficient //learn.microsoft.com/en-us/sql/t-sql/sta
frameworkforimplementingpersistentdatastructures tements/set-transaction-isolation-level-t
on asymmetric NVM architecture. In ASPLOS ’20: ransact-sql?view=sql-server-ver16,2023.
ArchitecturalSupportforProgrammingLanguagesand
[64] Alex Shamis, Matthew Renzelmann, Stanko No-
OperatingSystems,Lausanne,Switzerland,March16-
vakovic,GeorgiosChatzopoulos,AleksandarDragoje-
20,2020,pages757–773.ACM,2020.
vic, Dushyanth Narayanan, and Miguel Castro. Fast
[55] Shuai Mu,Yang Cui,Yang Zhang,Wyatt Lloyd,and general distributed transactions with opacity. In Pro-
Jinyang Li. Extracting more concurrency from dis- ceedingsofthe2019InternationalConferenceonMan-
tributedtransactions. In11thUSENIXSymposiumon agementofData,SIGMODConference2019,Amster-
OperatingSystemsDesignandImplementation,OSDI dam,The Netherlands,June 30 - July 5,2019,pages
’14,Broomfield,CO,USA,October6-8,2014,pages479– 433–448.ACM,2019.
494.USENIXAssociation,2014.
[65] YizhouShan,YutongHuang,YilunChen,andYiying
[56] MySQL. Transactionisolationlevels. https://dev. Zhang.Legoos:Adisseminated,distributedOSforhard-
mysql.com/doc/refman/8.0/en/innodb-transac wareresourcedisaggregation. In13thUSENIXSympo-
tion-isolation-levels.html,2024. siumonOperatingSystemsDesignandImplementation,
OSDI 2018,Carlsbad,CA,USA,October8-10,2018,
[57] ThomasNeumann,TobiasMühlbauer,andAlfonsKem-
pages69–87.USENIXAssociation,2018.
per. Fastserializablemulti-versionconcurrencycontrol
formain-memorydatabasesystems. InProceedingsof [66] JiachengShen,PengfeiZuo,XuchuanLuo,TianyiYang,
the2015ACMSIGMODInternationalConferenceon YuxinSu,YangfanZhou,andMichaelR.Lyu. FUSEE:
Management of Data,Melbourne,Victoria,Australia, Afullymemory-disaggregatedkey-valuestore. In21st
May31-June4,2015,pages677–689.ACM,2015. USENIXConferenceonFileandStorageTechnologies,
FAST 2023, Santa Clara, CA, USA, February 21-23,
[58] Stanko Novakovic, Yizhou Shan, Aasheesh Kolli,
2023,pages81–98.USENIXAssociation,2023.
Michael Cui, Yiying Zhang, Haggai Eran, Boris Pis-
menny,LiranLiss,MichaelWei,DanTsafrir,andMar- [67] Vishal Shrivastav, Asaf Valadarsky, Hitesh Ballani,
cosK.Aguilera. Storm:afasttransactionaldataplane PaoloCosta,Ki-SuhLee,HanWang,RachitAgarwal,
forremotedatastructures. InProceedingsofthe12th andHakimWeatherspoon. Shoal:Anetworkarchitec-
ACM International Conference on Systems and Stor- turefordisaggregatedracks. In16thUSENIXSympo-
age,SYSTOR2019,Haifa,Israel,June3-5,2019,pages siumonNetworkedSystemsDesignandImplementation,
97–108.ACM,2019. NSDI2019,Boston,MA,February26-28,2019,pages
255–270.USENIXAssociation,2019.
[59] Oracle. Transactionisolationlevels. https://www.or
eilly.com/library/view/java-programming-w [68] Abraham Silberschatz,Henry F. Korth,and S. Sudar-
ith/0596000871/0596000871_orasqlj-CHP-9-S shan. DatabaseSystemConcepts,7thEdition. McGraw-
ECT-2.html,2024. HillEducation,2019.
[60] PostgreSQL. Transactionisolation. https://www.po [69] Shin-YehTsai,YizhouShan,andYiyingZhang. Dis-
stgresql.org/docs/current/transaction-iso aggregating persistent memory and controlling them
.html,2024. remotely:Anexplorationofpassivedisaggregatedkey-
valuestores. In2020USENIXAnnualTechnicalCon-
[61] WaleedReda,MarcoCanini,DejanKostic,andSimon
ference,USENIX ATC 2020,July 15-17,2020,pages
Peter.RDMAisturingcomplete,wejustdidnotknowit
33–48.USENIXAssociation,2020.
yet! In19thUSENIXSymposiumonNetworkedSystems
DesignandImplementation,NSDI2022,Renton,WA, [70] Shin-YehTsaiandYiyingZhang. LITEkernelRDMA
USA,April4-6,2022,pages71–85.USENIXAssocia- supportfordatacenterapplications. InProceedingsof
tion,2022. the26thSymposiumonOperatingSystemsPrinciples,
Shanghai,China,October28-31,2017,pages306–324.
[62] ZhenyuanRuan,MalteSchwarzkopf,MarcosK.Aguil-
ACM,2017.
era, and Adam Belay. AIFM: high-performance,
application-integrated far memory. In 14th USENIX [71] Stephen Tu, Wenting Zheng, Eddie Kohler, Barbara
Symposium on Operating Systems Design and Imple- Liskov,and Samuel Madden. Speedy transactions in
mentation, OSDI 2020, Virtual Event, November 4-6, multicorein-memorydatabases. InACMSIGOPS24th
2020,pages315–332.USENIXAssociation,2020. SymposiumonOperatingSystemsPrinciples,SOSP’13,
818 17th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Farmington,PA,USA,November3-6,2013,pages18–32. ACID via modular concurrency control. In Proceed-
| ACM,2013. |     |     |     |     |     | ingsofthe25thSymposiumonOperatingSystemsPrin- |                              |     |     |      |
| --------- | --- | --- | --- | --- | --- | --------------------------------------------- | ---------------------------- | --- | --- | ---- |
|           |     |     |     |     |     | ciples,SOSP                                   | 2015,Monterey,CA,USA,October |     |     | 4-7, |
[72] ChenxiWang,HaoranMa,ShiLiu,YuanqiLi,Zhenyuan
2015,pages279–294.ACM,2015.
| Ruan, | Khanh Nguyen, | Michael | D.  | Bond, Ravi | Ne- |     |     |     |     |     |
| ----- | ------------- | ------- | --- | ---------- | --- | --- | --- | --- | --- | --- |
travali,MiryungKim,andGuoqingHarryXu. Semeru: [80] Jian Yang, Juno Kim, Morteza Hoseinzadeh, Joseph
A memory-disaggregated managed runtime. In 14th Izraelevitz,andStevenSwanson. Anempiricalguideto
USENIXSymposiumonOperatingSystemsDesignand thebehavioranduseofscalablepersistentmemory. In
Implementation(OSDI20),pages261–280.USENIX 18thUSENIXConferenceonFileandStorageTechnolo-
Association,November2020. gies,FAST2020,SantaClara,CA,USA,February24-27,
2020,pages169–182.USENIXAssociation,2020.
| [73] Chenxi | Wang, | Haoran Ma, | Shi Liu, | Yifan | Qiao, |     |     |     |     |     |
| ----------- | ----- | ---------- | -------- | ----- | ----- | --- | --- | --- | --- | --- |
Jonathan Eyolfson, Christian Navasca, Shan Lu, and [81] ErfanZamanian,CarstenBinnig,TimHarris,andTim
GuoqingHarryXu. Memliner:Lininguptracingand Kraska. Theendofamyth:Distributedtransactionscan
applicationforafar-memory-friendlyruntime. In16th scale. Proc. VLDBEndow.,10(6):685–696,February
| USENIXSymposiumonOperatingSystemsDesignand |     |     |     |     |     | 2017. |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- |
Implementation,OSDI2022,Carlsbad,CA,USA,July
|     |     |     |     |     |     | [82] ErfanZamanian,JulianShun,CarstenBinnig,andTim |     |     |     |     |
| --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- |
11-13,2022,pages35–53.USENIXAssociation,2022.
|     |     |     |     |     |     | Kraska. | Chiller: Contention-centric |     | transaction | exe- |
| --- | --- | --- | --- | --- | --- | ------- | --------------------------- | --- | ----------- | ---- |
[74] Jia-ChenWang,DingDing,HuanWang,ConradChris- cution anddatapartitioningformodern networks. In
tensen, Zhaoguo Wang, Haibo Chen, and Jinyang Li. Proceedingsofthe2020InternationalConferenceon
Polyjuice:High-performancetransactionsvialearned ManagementofData,SIGMODConference2020,on-
concurrencycontrol. In15thUSENIXSymposiumon lineconference[Portland,OR,USA],June14-19,2020,
OperatingSystemsDesignandImplementation,OSDI pages511–526.ACM,2020.
2021,July14-16,2021,pages198–216.USENIXAsso-
|     |     |     |     |     |     | [83] Irene Zhang, | Naveen | Kr. Sharma, | Adriana | Szekeres, |
| --- | --- | --- | --- | --- | --- | ----------------- | ------ | ----------- | ------- | --------- |
ciation,2021.
|     |     |     |     |     |     | Arvind Krishnamurthy, |     | and | Dan R. K. | Ports. Build- |
| --- | --- | --- | --- | --- | --- | --------------------- | --- | --- | --------- | ------------- |
[75] Qing Wang,Youyou Lu,and Jiwu Shu. Sherman: A ingconsistenttransactionswithinconsistentreplication.
write-optimizeddistributedb+treeindexondisaggre- In Proceedings of the 25th Symposium on Operating
gatedmemory. InProceedingsofthe2022International Systems Principles, SOSP 2015, Monterey, CA, USA,
ConferenceonManagementofData,pages1033–1048, October4-7,2015,pages263–278.ACM,2015.
2022.
|     |     |     |     |     |     | [84] Ming Zhang, | Yu Hua, | Pengfei | Zuo, and | Lurong Liu. |
| --- | --- | --- | --- | --- | --- | ---------------- | ------- | ------- | -------- | ----------- |
[76] XingdaWei,RongChen,HaiboChen,ZhaoguoWang, FORD:FastOne-sidedRDMA-basedDistributedTrans-
ZhenhanGong,andBinyuZang. Unifyingtimestamp actionsforDisaggregatedPersistentMemory. In20th
USENIXConferenceonFileandStorageTechnologies,
withtransactionorderingforMVCCwithdecentralized
scalartimestamp. In18thUSENIXSymposiumonNet- FAST 2022, Santa Clara, CA, USA, February 22-24,
workedSystemsDesignandImplementation,NSDI2021, 2022,pages51–68.USENIXAssociation,2022.
April12-14,2021,pages357–372.USENIXAssocia-
|     |     |     |     |     |     | [85] YangZhou,HassanM.G.Wassel,SihangLiu,JiaqiGao, |     |     |     |     |
| --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- |
tion,2021.
JamesMickens,MinlanYu,ChrisKennelly,PaulTurner,
[77] Xingda Wei, Zhiyuan Dong, Rong Chen, and Haibo David E. Culler, Henry M. Levy, and Amin Vahdat.
|       |                                               |     |     |     |     | Carbink:Fault-tolerantfarmemory. |     |     | In16thUSENIX |     |
| ----- | --------------------------------------------- | --- | --- | --- | --- | -------------------------------- | --- | --- | ------------ | --- |
| Chen. | Deconstructingrdma-enableddistributedtransac- |     |     |     |     |                                  |     |     |              |     |
tions:Hybridisbetter! In13thUSENIXSymposiumon Symposium on Operating Systems Design and Imple-
OperatingSystemsDesignandImplementation,OSDI mentation,OSDI2022,Carlsbad,CA,USA,July11-13,
2018,Carlsbad,CA,USA,October8-10,2018,pages 2022,pages55–71.USENIXAssociation,2022.
233–251.USENIXAssociation,2018.
|     |     |     |     |     |     | [86] PengfeiZuo,JiazhaoSun,LiuYang,ShuangwuZhang, |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- |
[78] XingdaWei,JiaxinShi,YanzheChen,RongChen,and andYuHua.One-sidedrdma-consciousextendiblehash-
HaiboChen. Fastin-memorytransactionprocessingus- ingfordisaggregatedmemory. In2021USENIXAnnual
ingRDMAandHTM. InProceedingsofthe25thSym- TechnicalConference,USENIXATC2021,July14-16,
posiumonOperatingSystemsPrinciples,SOSP2015, 2021,pages15–29.USENIXAssociation,2021.
Monterey,CA,USA,October4-7,2015,pages87–104.
ACM,2015.
| [79] Chao                   | Xie,Chunzhi | Su,Cody | Littley,Lorenzo  |     | Alvisi, |     |     |     |     |     |
| --------------------------- | ----------- | ------- | ---------------- | --- | ------- | --- | --- | --- | --- | --- |
| ManosKapritsos,andYangWang. |             |         | High-performance |     |         |     |     |     |     |     |
USENIX Association 17th USENIX Symposium on Operating Systems Design and Implementation    819