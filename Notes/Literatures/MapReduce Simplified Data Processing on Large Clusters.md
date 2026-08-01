# MapReduce Simplified Data Processing on Large Clusters

**Source**: MapReduce Simplified Data Processing on Large Clusters.pdf
**Format**: .pdf

---

|     | MapReduce: |     | Simplified | Data | Processing | on  | Large | Clusters |     |     |     |
| --- | ---------- | --- | ---------- | ---- | ---------- | --- | ----- | -------- | --- | --- | --- |
JeffreyDeanandSanjayGhemawat
jeff@google.com,sanjay@google.com
Google,Inc.
Abstract given day, etc. Most such computations are conceptu-
|           |     |               |           |            | ally straightforward. |     | However,the |     | input | data is | usually |
| --------- | --- | ------------- | --------- | ---------- | --------------------- | --- | ----------- | --- | ----- | ------- | ------- |
| MapReduce | is  | a programming | model and | an associ- |                       |     |             |     |       |         |         |
largeandthecomputationshavetobedistributedacross
atedimplementationforprocessingandgeneratinglarge
|           |                                        |     |     |     | hundreds                  | or thousands | of  | machines  | in  | order to | finish in |
| --------- | -------------------------------------- | --- | --- | --- | ------------------------- | ------------ | --- | --------- | --- | -------- | --------- |
| datasets. | Usersspecifyamapfunctionthatprocessesa |     |     |     |                           |              |     |           |     |          |           |
|           |                                        |     |     |     | a reasonableamountoftime. |              |     | Theissues |     | ofhowto  | par-      |
key/valuepairtogenerateasetofintermediatekey/value
|     |     |     |     |     | allelize | the computation, |     | distribute | the | data, and | handle |
| --- | --- | --- | --- | --- | -------- | ---------------- | --- | ---------- | --- | --------- | ------ |
pairs,andareducefunctionthatmergesallintermediate failures conspire to obscure the original simple compu-
| valuesassociatedwiththesameintermediatekey. |     |     |     | Many    |             |              |     |                |     |         |      |
| ------------------------------------------- | --- | --- | --- | ------- | ----------- | ------------ | --- | -------------- | --- | ------- | ---- |
|                                             |     |     |     |         | tation with | largeamounts |     | of complexcode |     | to deal | with |
| realworldtasksareexpressibleinthismodel,    |     |     |     | asshown |             |              |     |                |     |         |      |
theseissues.
inthepaper.
|     |     |     |     |     | As a | reaction | to this complexity, |     | we  | designed | a new |
| --- | --- | --- | --- | --- | ---- | -------- | ------------------- | --- | --- | -------- | ----- |
Programswritteninthisfunctionalstyleareautomati- abstractionthatallowsustoexpressthesimplecomputa-
callyparallelizedandexecutedonalargeclusterofcom- tionsweweretryingtoperformbuthidesthemessyde-
moditymachines. Therun-timesystemtakescareofthe tails of parallelization, fault-tolerance, data distribution
detailsofpartitioningtheinputdata,schedulingthepro- and load balancing in a library. Our abstraction is in-
gram’sexecutionacrossasetofmachines,handlingma-
spiredbythemapandreduceprimitivespresentinLisp
chinefailures,andmanagingtherequiredinter-machine and many other functional languages. We realized that
communication. This allows programmers without any most of our computations involved applying a map op-
experience with parallel and distributed systems to eas- eration to each logical “record” in our input in order to
ilyutilizetheresourcesofalargedistributedsystem. compute a set of intermediate key/valuepairs, and then
Our implementation of MapReduce runs on a large applyingareduceoperationtoallthevaluesthatshared
cluster of commodity machines and is highly scalable: the same key, in order to combine the derived data ap-
|           |           |             |           |           | propriately. | Our | use of | a functional | model | with | user- |
| --------- | --------- | ----------- | --------- | --------- | ------------ | --- | ------ | ------------ | ----- | ---- | ----- |
| a typical | MapReduce | computation | processes | many ter- |              |     |        |              |       |      |       |
abytesof dataonthousandsof machines. Programmers specified mapandreduce operationsallowsus to paral-
|     |     |     |     |     | lelize largecomputations |     |     | easily | and to | use re-execution |     |
| --- | --- | --- | --- | --- | ------------------------ | --- | --- | ------ | ------ | ---------------- | --- |
findthesystemeasytouse:hundredsofMapReducepro-
gramshavebeenimplementedandupwardsofonethou- astheprimarymechanismforfaulttolerance.
sandMapReducejobsareexecutedonGoogle’sclusters Themajorcontributionsofthisworkareasimpleand
everyday. powerfulinterfacethatenablesautomaticparallelization
|     |     |     |     |     | and distribution |                | of large-scale | computations, |           | combined |          |
| --- | --- | --- | --- | --- | ---------------- | -------------- | -------------- | ------------- | --------- | -------- | -------- |
|     |     |     |     |     | with an          | implementation |                | of this       | interface | that     | achieves |
1 Introduction
highperformanceonlargeclustersofcommodityPCs.
Section2describesthebasicprogrammingmodeland
Overthepastfiveyears, theauthorsandmanyothersat gives several examples. Section 3 describes an imple-
Google have implemented hundreds of special-purpose mentation of the MapReduce interface tailored towards
computations that process large amounts of raw data, ourcluster-basedcomputingenvironment. Section4de-
such as crawled documents, web request logs, etc., to scribes several refinements of the programming model
computevariouskindsof deriveddata, such as inverted that we have found useful. Section 5 has performance
indices, various representations of the graph structure measurements of our implementation for a variety of
of web documents, summaries of the number of pages tasks. Section 6 explores the use of MapReduce within
crawled per host, the set of most frequent queries in a Googleincludingourexperiencesinusingitasthebasis
USENIX Association OSDI ’04:6th Symposium on Operating Systems Design and Implementation 137

for a rewrite of our production indexing system. Sec- 2.2 Types
tion7discussesrelatedandfuturework.
Eventhoughthepreviouspseudo-codeiswritteninterms
of string inputs and outputs, conceptually the map and
2 Programming Model
reduce functions supplied by the user have associated
types:
Thecomputationtakesasetofinputkey/valuepairs,and
produces a set of output key/value pairs. The user of
map (k1,v1) →list(k2,v2)
theMapReducelibraryexpressesthecomputationastwo
reduce (k2,list(v2)) →list(v2)
functions: MapandReduce. I.e.,theinputkeysandvaluesaredrawnfromadifferent
Map,writtenbytheuser,takesaninputpairandpro- domain than the output keys and values. Furthermore,
ducesasetofintermediatekey/valuepairs. TheMapRe- the intermediate keys and values are from the same do-
ducelibrarygroupstogetherallintermediatevaluesasso- mainastheoutputkeysandvalues.
ciatedwiththesameintermediatekeyI andpassesthem Our C++ implementation passes strings to and from
totheReducefunction. theuser-definedfunctionsandleavesitto theusercode
TheReducefunction,alsowrittenbytheuser,accepts toconvertbetweenstringsandappropriatetypes.
anintermediatekeyI andasetofvaluesforthatkey. It
mergestogetherthese valuesto forma possiblysmaller
set of values. Typically justzero or one output value is 2.3 More Examples
produced per Reduce invocation. The intermediate val-
uesaresuppliedtotheuser’sreducefunctionviaaniter- Hereareafewsimpleexamplesofinterestingprograms
ator. Thisallowsustohandlelistsofvaluesthataretoo that can be easily expressed as MapReduce computa-
largetofitinmemory. tions.
2.1 Example
DistributedGrep: Themapfunctionemitsalineifit
matches a supplied pattern. The reduce function is an
Consider the problem of counting the number of oc-
identityfunctionthatjustcopiesthesuppliedintermedi-
currences of each word in a large collection of docu-
atedatatotheoutput.
ments. Theuserwouldwritecodesimilartothefollow-
ingpseudo-code:
Count of URL Access Frequency: The map func-
map(String key, String value):
tion processes logs of web page requests and outputs
// key: document name
hURL,1i. The reduce function adds together all values
// value: document contents
for each word w in value:
for the same URL and emits a hURL,total counti
pair.
EmitIntermediate(w, "1");
reduce(String key, Iterator values):
ReverseWeb-LinkGraph: Themapfunctionoutputs
// key: a word
// values: a list of counts
htarget,sourcei pairs for each link to a target
int result = 0; URL found in a page named source. The reduce
for each v in values: function concatenates the list of all source URLs as-
result += ParseInt(v); sociated with a given target URL and emits the pair:
Emit(AsString(result)); htarget,list(source)i
Themapfunctionemitseachwordplusanassociated
count of occurrences (just ‘1’ in this simple example). Term-VectorperHost: Atermvectorsummarizesthe
The reducefunctionsums together all countsemitted most importantwordsthat occur ina documentor a set
foraparticularword. ofdocumentsasalistofhword,frequencyipairs. The
Inaddition,theuserwritescodetofillinamapreduce map function emits a hhostname,term vectori
specificationobjectwiththenamesoftheinputandout- pair for each input document (where the hostname is
putfiles,andoptionaltuningparameters. Theuserthen extracted from the URL of the document). The re-
invokesthe MapReduce function, passing it the specifi- duce function is passed all per-document term vectors
cationobject.Theuser’scodeislinkedtogetherwiththe for a given host. It adds these term vectors together,
MapReducelibrary(implementedinC++). AppendixA throwing away infrequent terms, and then emits a final
containsthefullprogramtextforthisexample. hhostname,term vectoripair.
138 OSDI ’04:6th Symposium on Operating Systems Design and Implementation USENIX Association

User
Program
(1) fork
|     |     |     |     |     |     | (1) fork | (1) fork |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | -------- | -------- | --- | --- | --- | --- | --- | --- |
Master
(2)
|     |     |     |     |     |     | (2) | assign |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
reduce
assign
map
worker
split 0
(6) write
output
|     | split 1 |          |     |     |                 |     |                 |     | worker |     |     |        |     |
| --- | ------- | -------- | --- | --- | --------------- | --- | --------------- | --- | ------ | --- | --- | ------ | --- |
|     |         |          |     |     |                 |     | (5) remote read |     |        |     |     | file 0 |     |
|     | split 2 | (3) read |     |     | (4) local write |     |                 |     |        |     |     |        |     |
worker
output
|     | split 3 |     |     |     |     |     |     |     | worker |     |     |     |     |
| --- | ------- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- |
file 1
split 4
worker
|     | Input |     |     | Map   |          | Intermediate files |     |     | Reduce |     |     | Output |     |
| --- | ----- | --- | --- | ----- | -------- | ------------------ | --- | --- | ------ | --- | --- | ------ | --- |
|     | files |     |     | phase |          | (on local disks)   |     |     | phase  |     |     | files  |     |
|     |       |     |     |       | Figure1: | Executionoverview  |     |     |        |     |     |        |     |
Inverted Index: The map function parses each docu- largeclustersofcommodityPCsconnectedtogetherwith
ment,andemitsasequenceofhword,document IDi switchedEthernet[4]. Inourenvironment:
| pairs. | The reduce | function | accepts |     | all pairs | for a given |     |     |     |     |     |     |     |
| ------ | ---------- | -------- | ------- | --- | --------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
(1)Machinesaretypicallydual-processorx86processors
word,sortsthecorrespondingdocumentIDsandemitsa runningLinux,with2-4GBofmemorypermachine.
| hword,list(document |     |     | ID)ipair.Thesetofalloutput |     |     |     |     |     |     |     |     |     |     |
| ------------------- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(2)Commoditynetworkinghardwareisused–typically
pairsformsasimpleinvertedindex.Itiseasytoaugment
|     |     |     |     |     |     |     | either 100 | megabits/second |     | or  | 1 gigabit/second |     | at the |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --------------- | --- | --- | ---------------- | --- | ------ |
thiscomputationtokeeptrackofwordpositions.
|     |     |     |     |     |     |     | machine | level, | but averaging | considerably |     | less | in over- |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------ | ------------- | ------------ | --- | ---- | -------- |
allbisectionbandwidth.
| Distributed                               | Sort: |     | The map | function | extracts | the key |               |          |     |             |     |           |        |
| ----------------------------------------- | ----- | --- | ------- | -------- | -------- | ------- | ------------- | -------- | --- | ----------- | --- | --------- | ------ |
|                                           |       |     |         |          |          |         | (3) A cluster | consists |     | of hundreds | or  | thousands | of ma- |
| fromeachrecord,andemitsahkey,recordipair. |       |     |         |          |          | The     |               |          |     |             |     |           |        |
chines,andthereforemachinefailuresarecommon.
| reducefunctionemitsallpairsunchanged. |     |     |     |     | Thiscompu- |     |             |     |          |                |     |     |           |
| ------------------------------------- | --- | --- | --- | --- | ---------- | --- | ----------- | --- | -------- | -------------- | --- | --- | --------- |
|                                       |     |     |     |     |            |     | (4) Storage | is  | provided | by inexpensive |     | IDE | disks at- |
tationdependsonthepartitioningfacilitiesdescribedin
Section4.1andtheorderingpropertiesdescribedinSec- tacheddirectlytoindividualmachines. Adistributedfile
system[8]developedin-houseisusedtomanagethedata
tion4.2.
|                  |           |                 |     |     |               |     | storedonthesedisks. |              |     | Thefilesystemusesreplicationto |     |        |            |
| ---------------- | --------- | --------------- | --- | --- | ------------- | --- | ------------------- | ------------ | --- | ------------------------------ | --- | ------ | ---------- |
|                  |           |                 |     |     |               |     | provide             | availability | and | reliability                    | on  | top of | unreliable |
| 3 Implementation |           |                 |     |     |               |     | hardware.           |              |     |                                |     |        |            |
|                  |           |                 |     |     |               |     | (5) Userssubmitjobs |              |     | to a schedulingsystem.         |     |        | Eachjob    |
| Many             | different | implementations |     | of  | the MapReduce | in- |                     |              |     |                                |     |        |            |
consistsofasetoftasks,andismappedbythescheduler
| terface | are possible. |     | The right | choice | depends | on the |     |     |     |     |     |     |     |
| ------- | ------------- | --- | --------- | ------ | ------- | ------ | --- | --- | --- | --- | --- | --- | --- |
toasetofavailablemachineswithinacluster.
| environment. |     | Forexample,oneimplementationmaybe |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
suitableforasmallshared-memorymachine,anotherfor
a large NUMA multi-processor, and yet another for an 3.1 ExecutionOverview
evenlargercollectionofnetworkedmachines.
This section describes an implementation targeted The Map invocations are distributed across multiple
to the computing environment in wide use at Google: machines by automatically partitioning the input data
USENIX Association OSDI ’04:6th Symposium on Operating Systems Design and Implementation 139

into a set of splits. The input splits can be pro- 7. When all map tasks and reduce tasks have been
M
cessedinparallelbydifferentmachines. Reduceinvoca- completed, the master wakes up the user program.
tionsaredistributedbypartitioningtheintermediatekey Atthispoint,theMapReducecallintheuserpro-
space into pieces using a partitioning function (e.g., gramreturnsbacktotheusercode.
R
| hash(key)modR). | Thenumberofpartitions(R)and |     |     |     |     |     |     |     |     |     |
| --------------- | --------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
thepartitioningfunctionarespecifiedbytheuser. After successful completion, the output of the mapre-
Figure 1 showsthe overallflow of a MapReduce op- duceexecutionisavailableintheRoutputfiles(oneper
eration in our implementation. When the user program reduce task, with file names as specified by the user).
|                            |     |                      |     |     | Typically, | users | do not needto | combine |     | these output |
| -------------------------- | --- | -------------------- | --- | --- | ---------- | ----- | ------------- | ------- | --- | ------------ |
| callstheMapReducefunction, |     | thefollowingsequence |     |     |            |       |               |         |     | R            |
ofactionsoccurs(thenumberedlabelsinFigure1corre- filesintoonefile–theyoftenpassthesefilesasinputto
|     |     |     |     |     | anotherMapReduce |     | call, oruse |     | them fromanotherdis- |     |
| --- | --- | --- | --- | --- | ---------------- | --- | ----------- | --- | -------------------- | --- |
spondtothenumbersinthelistbelow):
tributedapplicationthatisabletodealwithinputthatis
1. The MapReduce library in the user program first partitionedintomultiplefiles.
| splits the | input files into | M pieces    | of          | typically 16 |                |     |            |     |     |     |
| ---------- | ---------------- | ----------- | ----------- | ------------ | -------------- | --- | ---------- | --- | --- | --- |
| megabytes  | to 64 megabytes  | (MB)        | per         | piece (con-  |                |     |            |     |     |     |
|            |                  |             |             |              | 3.2 MasterData |     | Structures |     |     |     |
| trollable  | by the user via  | an optional | parameter). | It           |                |     |            |     |     |     |
thenstartsupmanycopiesoftheprogramonaclus- Themasterkeeps severaldata structures. Foreachmap
terofmachines.
taskandreducetask,itstoresthestate(idle,in-progress,
|                       |                                      |                    |            |       | or completed),      | and | the identity |         | of the   | worker machine |
| --------------------- | ------------------------------------ | ------------------ | ---------- | ----- | ------------------- | --- | ------------ | ------- | -------- | -------------- |
| 2. One of             | the copies of                        | the program        | is special | – the |                     |     |              |         |          |                |
| master.               | Therestareworkersthatareassignedwork |                    |            |       | (fornon-idletasks). |     |              |         |          |                |
|                       |                                      |                    |            |       | The master          | is  | the conduit  | through | whichthe | location       |
| bythemaster.ThereareM |                                      | maptasksandRreduce |            |       |                     |     |              |         |          |                |
tasksto assign. Themasterpicks idleworkersand ofintermediatefileregionsispropagatedfrommaptasks
toreducetasks.Therefore,foreachcompletedmaptask,
assignseachoneamaptaskorareducetask.
|     |     |     |     |     | the master | stores | the locations | and | sizes | of the inter- |
| --- | --- | --- | --- | --- | ---------- | ------ | ------------- | --- | ----- | ------------- |
R
3. A worker who is assigned a map task reads the mediatefileregionsproducedbythemaptask. Updates
contentsof the corresponding input split. It parses tothislocationandsizeinformationarereceivedasmap
key/valuepairsoutoftheinputdataandpasseseach
|     |     |     |     |     | tasks are | completed. | The | information |     | is pushed incre- |
| --- | --- | --- | --- | --- | --------- | ---------- | --- | ----------- | --- | ---------------- |
pairtotheuser-definedMapfunction. Theinterme- mentallytoworkersthathavein-progressreducetasks.
diatekey/valuepairsproducedbytheMapfunction
arebufferedinmemory.
3.3 FaultTolerance
| 4. Periodically, | the buffered | pairs | are written | to local |     |     |     |     |     |     |
| ---------------- | ------------ | ----- | ----------- | -------- | --- | --- | --- | --- | --- | --- |
SincetheMapReducelibraryisdesignedtohelpprocess
| disk, partitioned | into | R regionsby | the | partitioning |     |     |     |     |     |     |
| ----------------- | ---- | ----------- | --- | ------------ | --- | --- | --- | --- | --- | --- |
function. The locations of these buffered pairs on verylargeamountsofdatausinghundredsorthousands
|                  |                            |      |        |             | of machines, | the | library must | tolerate |     | machine failures |
| ---------------- | -------------------------- | ---- | ------ | ----------- | ------------ | --- | ------------ | -------- | --- | ---------------- |
| the local        | disk are passed            | back | to the | master, who |              |     |              |          |     |                  |
| isresponsiblefor | forwardingtheselocationsto |      |        | the         | gracefully.  |     |              |          |     |                  |
reduceworkers.
WorkerFailure
| 5. When | a reduce worker | is notified | by  | the master |     |     |     |     |     |     |
| ------- | --------------- | ----------- | --- | ---------- | --- | --- | --- | --- | --- | --- |
abouttheselocations,itusesremoteprocedurecalls
|     |     |     |     |     | The master | pings | every worker |     | periodically. | If no re- |
| --- | --- | --- | --- | --- | ---------- | ----- | ------------ | --- | ------------- | --------- |
toreadthebuffereddatafromthelocaldisksofthe
sponseisreceivedfromaworkerinacertainamountof
mapworkers.Whenareduceworkerhasreadallin- time, the master marks the worker as failed. Any map
| termediatedata, | itsortsit | bytheintermediatekeys |     |     |     |     |     |     |     |     |
| --------------- | --------- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
taskscompletedbytheworkerareresetbacktotheirini-
sothatalloccurrencesofthesamekeyaregrouped
tialidlestate,andthereforebecomeeligibleforschedul-
together. The sorting is needed because typically ingonotherworkers. Similarly,anymaptaskorreduce
| manydifferentkeysmaptothesamereducetask. |     |     |     | If  |                  |     |             |        |         |               |
| ---------------------------------------- | --- | --- | --- | --- | ---------------- | --- | ----------- | ------ | ------- | ------------- |
|                                          |     |     |     |     | task in progress |     | on a failed | worker | is also | reset to idle |
theamountofintermediatedataistoolargetofitin andbecomeseligibleforrescheduling.
memory,anexternalsortisused.
Completedmaptasksarere-executedonafailurebe-
|     |     |     |     |     | cause their | output | is stored | on the | local | disk(s) of the |
| --- | --- | --- | --- | --- | ----------- | ------ | --------- | ------ | ----- | -------------- |
6. Thereduceworkeriteratesoverthesortedinterme-
diatedataandforeachuniqueintermediatekeyen- failedmachineandisthereforeinaccessible. Completed
|            |               |         |                   |     | reduce tasks | do  | not need | to be | re-executed | since their |
| ---------- | ------------- | ------- | ----------------- | --- | ------------ | --- | -------- | ----- | ----------- | ----------- |
| countered, | it passes the | key and | the corresponding |     |              |     |          |       |             |             |
setofintermediatevaluestotheuser’sReducefunc- outputisstoredinaglobalfilesystem.
tion.TheoutputoftheReducefunctionisappended When a map task is executed first by worker and
A
toafinaloutputfileforthisreducepartition. then later executedby worker B (because A failed), all
140 OSDI ’04:6th Symposium on Operating Systems Design and Implementation USENIX Association

workers executing reduce tasks are notified of the re- easyforprogrammerstoreasonabouttheirprogram’sbe-
execution. Anyreducetaskthathasnotalreadyreadthe havior. Whenthemapand/orreduce operatorsarenon-
datafromworkerAwillreadthedatafromworkerB. deterministic,weprovideweakerbutstillreasonablese-
MapReduceisresilienttolarge-scaleworkerfailures. mantics. Inthepresenceofnon-deterministicoperators,
|                                                 |      |         |        |             |     |      | theoutputofaparticularreducetaskR |     |                                  |                          |                      | isequivalentto |           |     |
| ----------------------------------------------- | ---- | ------- | ------ | ----------- | --- | ---- | --------------------------------- | --- | -------------------------------- | ------------------------ | -------------------- | -------------- | --------- | --- |
| Forexample,duringoneMapReduceoperation,network  |      |         |        |             |     |      |                                   |     |                                  |                          |                      | 1              |           |     |
|                                                 |      |         |        |             |     |      | theoutputforR                     |     | producedbyasequentialexecutionof |                          |                      |                |           |     |
| maintenanceonarunningclusterwascausinggroupsof  |      |         |        |             |     |      |                                   |     | 1                                |                          |                      |                |           |     |
|                                                 |      |         |        |             |     |      | thenon-deterministicprogram.      |     |                                  |                          | However,theoutputfor |                |           |     |
| 80 machines                                     | at a | time to | become | unreachable | for | sev- |                                   |     |                                  |                          |                      |                |           |     |
|                                                 |      |         |        |             |     |      | adifferentreducetaskR             |     |                                  | maycorrespondtotheoutput |                      |                |           |     |
| eralminutes.TheMapReducemastersimplyre-executed |      |         |        |             |     |      |                                   |     |                                  | 2                        |                      |                |           |     |
|                                                 |      |         |        |             |     |      | for produced                      |     | by a                             | different                | sequential           |                | execution | of  |
| theworkdonebytheunreachableworkermachines,and   |      |         |        |             |     |      | R                                 |     |                                  |                          |                      |                |           |     |
2
thenon-deterministicprogram.
continuedtomakeforwardprogress,eventuallycomplet-
|                           |     |     |     |     |     |     | Consider        | map      | task                          | and | reduce | tasks     | and       | .      |
| ------------------------- | --- | --- | --- | --- | --- | --- | --------------- | -------- | ----------------------------- | --- | ------ | --------- | --------- | ------ |
| ingtheMapReduceoperation. |     |     |     |     |     |     |                 |          |                               | M   |        |           | R         | R      |
|                           |     |     |     |     |     |     |                 |          |                               |     |        |           | 1         | 2      |
|                           |     |     |     |     |     |     | Let e(R         | ) be the | executionof                   |     | R that | committed |           | (there |
|                           |     |     |     |     |     |     |                 | i        |                               |     | i      |           |           |        |
|                           |     |     |     |     |     |     | is exactly      | one      | such execution).              |     | The    | weaker    | semantics |        |
| MasterFailure             |     |     |     |     |     |     | arisebecausee(R |          | )mayhavereadtheoutputproduced |     |        |           |           |        |
1
|     |     |     |     |     |     |     | by one | execution | of M | and | e(R | ) may | have read | the |
| --- | --- | --- | --- | --- | --- | --- | ------ | --------- | ---- | --- | --- | ----- | --------- | --- |
2
outputproducedbyadifferentexecutionofM.
Itiseasytomakethemasterwriteperiodiccheckpoints
ofthemasterdatastructuresdescribedabove.Ifthemas-
| ter task dies, | a new  | copy     | can be | started    | from the | last   | 3.4 Locality |     |     |     |     |     |     |     |
| -------------- | ------ | -------- | ------ | ---------- | -------- | ------ | ------------ | --- | --- | --- | --- | --- | --- | --- |
| checkpointed   | state. | However, | given  | that there | is       | only a |              |     |     |     |     |     |     |     |
single master, its failure is unlikely; therefore our cur- Networkbandwidthisarelativelyscarceresourceinour
rentimplementationabortstheMapReducecomputation computing environment. We conserve network band-
if the master fails. Clients can check for this condition widthbytakingadvantageofthefactthattheinputdata
(managedbyGFS[8])isstoredonthelocaldisksofthe
andretrytheMapReduceoperationiftheydesire.
|     |     |     |     |     |     |     | machines | that | make up | our | cluster. | GFS | divides | each |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---- | ------- | --- | -------- | --- | ------- | ---- |
fileinto64MBblocks,andstoresseveralcopiesofeach
SemanticsinthePresenceofFailures block (typically 3 copies) on different machines. The
MapReducemastertakesthelocationinformationofthe
Whentheuser-suppliedmapandreduceoperatorsarede- input files into account and attempts to schedule a map
terministicfunctionsoftheirinputvalues,ourdistributed task on a machine that contains a replica of the corre-
implementationproducesthesameoutputaswouldhave spondinginputdata. Failingthat,itattemptstoschedule
beenproducedbyanon-faultingsequentialexecutionof
amaptasknearareplicaofthattask’sinputdata(e.g.,on
theentireprogram. aworkermachinethatisonthesamenetworkswitchas
|                                         |           |                |        |             |             |      | the machine | containing |      | the   | data).      | When              | running | large  |
| --------------------------------------- | --------- | -------------- | ------ | ----------- | ----------- | ---- | ----------- | ---------- | ---- | ----- | ----------- | ----------------- | ------- | ------ |
| We rely                                 | on atomic | commits        | of map | and         | reduce      | task |             |            |      |       |             |                   |         |        |
|                                         |           |                |        |             |             |      | MapReduce   | operations |      | on a  | significant | fraction          |         | of the |
| outputs to                              | achieve   | this property. | Each   | in-progress |             | task |             |            |      |       |             |                   |         |        |
|                                         |           |                |        |             |             |      | workersin   | a cluster, | most | input | data        | is readlocallyand |         |        |
| writesitsoutputtoprivatetemporaryfiles. |           |                |        |             | Areducetask |      |             |            |      |       |             |                   |         |        |
consumesnonetworkbandwidth.
producesonesuchfile,andamaptaskproducesRsuch
| files(oneperreducetask). |     |     | Whenamaptaskcompletes, |     |     |     |     |     |     |     |     |     |     |     |
| ------------------------ | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
the worker sends a message to the master and includes 3.5 TaskGranularity
| the names                                       | of the | R temporary | files | in the | message. | If  |              |     |         |       |      |        |     |         |
| ----------------------------------------------- | ------ | ----------- | ----- | ------ | -------- | --- | ------------ | --- | ------- | ----- | ---- | ------ | --- | ------- |
|                                                 |        |             |       |        |          |     | We subdivide |     | the map | phase | into | pieces | and | the re- |
| themasterreceivesacompletionmessageforanalready |        |             |       |        |          |     |              |     |         |       | M    |        |     |         |
completedmaptask,itignoresthemessage. Otherwise, ducephaseintoRpieces,asdescribedabove.Ideally,M
andRshouldbemuchlargerthanthenumberofworker
itrecordsthenamesofRfilesinamasterdatastructure.
|      |          |                 |     |            |        |     | machines. | Having | each | worker | perform | many | different |     |
| ---- | -------- | --------------- | --- | ---------- | ------ | --- | --------- | ------ | ---- | ------ | ------- | ---- | --------- | --- |
| When | a reduce | task completes, |     | the reduce | worker |     |           |        |      |        |         |      |           |     |
tasksimprovesdynamicloadbalancing,andalsospeeds
atomicallyrenamesitstemporaryoutputfiletothefinal
|             |                                       |     |     |     |     |     | up recovery      | when | a worker |           | fails: | the many | map     | tasks |
| ----------- | ------------------------------------- | --- | --- | --- | --- | --- | ---------------- | ---- | -------- | --------- | ------ | -------- | ------- | ----- |
| outputfile. | Ifthesamereducetaskisexecutedonmulti- |     |     |     |     |     |                  |      |          |           |        |          |         |       |
|             |                                       |     |     |     |     |     | it has completed |      | can      | be spread | out    | across   | all the | other |
plemachines,multiplerenamecallswillbeexecutedfor
workermachines.
| thesamefinaloutputfile. |     |     | Werelyontheatomicrename |     |     |     |                                    |     |     |     |     |     |         |     |
| ----------------------- | --- | --- | ----------------------- | --- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --- | ------- | --- |
|                         |     |     |                         |     |     |     | TherearepracticalboundsonhowlargeM |     |     |     |     |     | andRcan |     |
operationprovidedbytheunderlyingfilesystemtoguar-
|     |     |     |     |     |     |     | be in our | implementation, |     | since | the | master | must | make |
| --- | --- | --- | --- | --- | --- | --- | --------- | --------------- | --- | ----- | --- | ------ | ---- | ---- |
anteethatthefinalfilesystemstatecontainsjustthedata
|     |     |     |     |     |     |     |         | scheduling |     | decisions | and | keeps |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | ---------- | --- | --------- | --- | ----- | --- | --- |
|     |     |     |     |     |     |     | O(M +R) |            |     |           |     |       | O(M | ∗R) |
producedbyoneexecutionofthereducetask.
|     |     |     |     |     |     |     | statein | memoryas | describedabove. |     |     | (The | constantfac- |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | --------------- | --- | --- | ---- | ------------ | --- |
Thevastmajorityofourmapandreduceoperatorsare torsformemoryusagearesmallhowever:theO(M∗R)
deterministic, andthe fact thatour semantics areequiv- piece of the state consists of approximatelyone byte of
alenttoasequentialexecutioninthiscasemakesitvery datapermaptask/reducetaskpair.)
USENIX Association OSDI ’04:6th Symposium on Operating Systems Design and Implementation 141

Furthermore,Risoftenconstrainedbyusersbecause the intermediate key. A default partitioning function is
theoutputofeachreducetaskendsupinaseparateout- providedthatuseshashing(e.g. “hash(key)modR”).
put file. In practice, we tend to choose M so that each Thistendstoresultinfairlywell-balancedpartitions. In
individualtaskisroughly16MBto64MBofinputdata some cases, however, it is useful to partition data by
(sothatthelocalityoptimizationdescribedaboveismost someotherfunctionofthekey. Forexample,sometimes
effective),andwemakeRasmallmultipleofthenum- theoutput keysareURLs, andwe wantallentriesfor a
berofworkermachinesweexpecttouse. Weoftenper- singlehosttoendupinthesameoutputfile. Tosupport
formMapReducecomputationswithM = 200,000and situations like this, the user of the MapReduce library
R=5,000,using2,000workermachines. canprovideaspecialpartitioningfunction. Forexample,
using“hash(Hostname(urlkey))modR”asthepar-
titioningfunctioncausesallURLsfromthesamehostto
| 3.6 Backup |     | Tasks |     |     |     |     |     |     |     |     |     |     |
| ---------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
endupinthesameoutputfile.
Oneofthecommoncausesthatlengthensthetotaltime
takenforaMapReduceoperationisa“straggler”: ama- 4.2 Ordering Guarantees
chinethattakesanunusuallylongtimetocompleteone
|             |        |     |        |       |                     |     | We guaranteethat |     | within a | givenpartition, | the | interme- |
| ----------- | ------ | --- | ------ | ----- | ------------------- | --- | ---------------- | --- | -------- | --------------- | --- | -------- |
| of the last | fewmap | or  | reduce | tasks | in the computation. |     |                  |     |          |                 |     |          |
Stragglerscanariseforawholehostofreasons. Forex- diatekey/valuepairsareprocessedinincreasingkeyor-
|                   |         |        |       |          |                  |      | der. This       | ordering | guarantee      | makes | it easy to | generate |
| ----------------- | ------- | ------ | ----- | -------- | ---------------- | ---- | --------------- | -------- | -------------- | ----- | ---------- | -------- |
| ample, a          | machine | with   | a bad | disk may | experience       | fre- |                 |          |                |       |            |          |
|                   |         |        |       |          |                  |      | a sorted output | file     | per partition, | which | is useful  | when     |
| quent correctable |         | errors | that  | slow its | read performance |      |                 |          |                |       |            |          |
from 30 MB/s to 1 MB/s. The cluster scheduling sys- the output file format needs to support efficient random
accesslookupsbykey,orusersoftheoutputfinditcon-
| tem may | have | scheduled | other | tasks | on the | machine, |     |     |     |     |     |     |
| ------- | ---- | --------- | ----- | ----- | ------ | -------- | --- | --- | --- | --- | --- | --- |
causing it to execute the MapReduce code more slowly venienttohavethedatasorted.
duetocompetitionforCPU,memory,localdisk,ornet-
workbandwidth. Arecentproblemweexperiencedwas 4.3 Combiner Function
a bugin machineinitializationcodethatcausedproces-
Insomecases,thereissignificantrepetitionintheinter-
| sorcachestobedisabled: |     |     | computationsonaffectedma- |     |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
chinessloweddownbyoverafactorofonehundred. mediate keys produced by each map task, and the user-
|         |           |     |           |     |           |           | specified | Reduce | function is | commutative | and | associa- |
| ------- | --------- | --- | --------- | --- | --------- | --------- | --------- | ------ | ----------- | ----------- | --- | -------- |
| We have | a general |     | mechanism | to  | alleviate | the prob- |           |        |             |             |     |          |
lemofstragglers.WhenaMapReduceoperationisclose tive. Agoodexampleofthisisthewordcountingexam-
pleinSection2.1.Sincewordfrequenciestendtofollow
| to completion, |     | the master | schedules |     | backup executions |     |     |     |     |     |     |     |
| -------------- | --- | ---------- | --------- | --- | ----------------- | --- | --- | --- | --- | --- | --- | --- |
aZipfdistribution,eachmaptaskwillproducehundreds
| of the remaining |     | in-progress |     | tasks. | The task | is marked |     |     |     |     |     |     |
| ---------------- | --- | ----------- | --- | ------ | -------- | --------- | --- | --- | --- | --- | --- | --- |
ascompletedwhenevereithertheprimaryorthebackup orthousandsofrecordsoftheform<the, 1>. Allof
thesecountswillbesentoverthenetworktoasinglere-
| executioncompletes. |     |     | Wehavetunedthismechanismso |     |     |     |     |     |     |     |     |     |
| ------------------- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ducetaskandthenaddedtogetherbytheReducefunction
| that it typically |               | increases | the   | computational |       | resources |                     |     |                           |     |     |     |
| ----------------- | ------------- | --------- | ----- | ------------- | ----- | --------- | ------------------- | --- | ------------------------- | --- | --- | --- |
|                   |               |           |       |               |       |           | toproduceonenumber. |     | Weallowtheusertospecifyan |     |     |     |
| used by           | the operation |           | by no | more than     | a few | percent.  |                     |     |                           |     |     |     |
optionalCombinerfunctionthatdoespartialmergingof
| We have | found | that this | significantly |     | reduces | the time |     |     |     |     |     |     |
| ------- | ----- | --------- | ------------- | --- | ------- | -------- | --- | --- | --- | --- | --- | --- |
to complete largeMapReduce operations. As an exam- thisdatabeforeitissentoverthenetwork.
|     |     |     |     |     |     |     | The Combiner | function | is  | executedon | each | machine |
| --- | --- | --- | --- | --- | --- | --- | ------------ | -------- | --- | ---------- | ---- | ------- |
ple,thesortprogramdescribedinSection5.3takes44%
longer to complete when the backuptask mechanism is thatperformsamaptask.Typicallythesamecodeisused
|     |     |     |     |     |     |     | to implement | both | the combiner | and | the reduce | func- |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ---- | ------------ | --- | ---------- | ----- |
disabled.
tions.Theonlydifferencebetweenareducefunctionand
acombinerfunctionishowtheMapReducelibraryhan-
4 Refinements
|     |     |     |     |     |     |     | dles the output                        | of  | the function. | The | output of   | a reduce |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------------- | --- | ------------- | --- | ----------- | -------- |
|     |     |     |     |     |     |     | functioniswrittentothefinaloutputfile. |     |               |     | Theoutputof |          |
Although the basic functionality provided by simply acombinerfunctioniswrittentoanintermediatefilethat
writingMapandReducefunctionsissufficientformost willbesenttoareducetask.
needs,wehavefoundafewextensionsuseful.Theseare
|     |     |     |     |     |     |     | Partial | combining | significantly | speeds | up  | certain |
| --- | --- | --- | --- | --- | --- | --- | ------- | --------- | ------------- | ------ | --- | ------- |
describedinthissection. classesofMapReduceoperations. AppendixAcontains
anexamplethatusesacombiner.
4.1 PartitioningFunction
|           |              |     |         |     |        |           | 4.4 Inputand |     | OutputTypes |     |     |     |
| --------- | ------------ | --- | ------- | --- | ------ | --------- | ------------ | --- | ----------- | --- | --- | --- |
| The users | of MapReduce |     | specify | the | number | of reduce |              |     |             |     |     |     |
tasks/output files that they desire (R). Data gets parti- TheMapReducelibraryprovidessupportforreadingin-
tionedacrossthesetasksusingapartitioningfunctionon putdatainseveraldifferentformats.Forexample,“text”
142 OSDI ’04:6th Symposium on Operating Systems Design and Implementation USENIX Association

mode input treatseach line as a key/valuepair: the key the signal handler sends a “last gasp” UDP packet that
is the offset in the file and the value is the contents of contains the sequence number to the MapReduce mas-
the line. Another common supported format stores a ter. Whenthemasterhas seenmorethanonefailureon
sequence of key/value pairs sorted by key. Each input aparticularrecord,itindicatesthattherecordshouldbe
typeimplementationknowshowtosplititselfintomean- skippedwhenitissuesthenextre-executionofthecorre-
ingful ranges for processing as separate map tasks (e.g. spondingMaporReducetask.
| text mode’s               | range | splitting | ensures |                        | that range | splits oc- |     |     |     |     |     |     |     |
| ------------------------- | ----- | --------- | ------- | ---------------------- | ---------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
| curonlyatlineboundaries). |       |           |         | Userscanaddsupportfora |            |            |     |     |     |     |     |     |     |
4.7 LocalExecution
newinputtypebyprovidinganimplementationofasim-
plereaderinterface,thoughmostusersjustuseoneofa
DebuggingproblemsinMaporReducefunctionscanbe
smallnumberofpredefinedinputtypes.
|          |      |     |             |      |     |              | tricky, since | the     | actual computation |         | happens  |           | in a dis- |
| -------- | ---- | --- | ----------- | ---- | --- | ------------ | ------------- | ------- | ------------------ | ------- | -------- | --------- | --------- |
| A reader | does | not | necessarily | need | to  | provide data |               |         |                    |         |          |           |           |
|          |      |     |             |      |     |              | tributed      | system, | often on           | several | thousand | machines, |           |
readfromafile.Forexample,itiseasytodefineareader
|            |         |      |             |     |         |             | with work   | assignment | decisions  |            | made | dynamically | by  |
| ---------- | ------- | ---- | ----------- | --- | ------- | ----------- | ----------- | ---------- | ---------- | ---------- | ---- | ----------- | --- |
| that reads | records | from | a database, |     | or from | data struc- |             |            |            |            |      |             |     |
|            |         |      |             |     |         |             | the master. | To help    | facilitate | debugging, |      | profiling,  | and |
turesmappedinmemory.
small-scaletesting,wehavedevelopedanalternativeim-
In a similar fashion, we support a set of output types plementationoftheMapReducelibrarythatsequentially
forproducingdataindifferentformatsanditiseasyfor
|     |     |     |     |     |     |     | executes | all of the | work | for a MapReduce |     | operation | on  |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ---- | --------------- | --- | --------- | --- |
usercodetoaddsupportfornewoutputtypes. the local machine. Controls are provided to the user so
|     |     |     |     |     |     |     | that the | computation | can | be limited | to  | particular | map |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | --- | ---------- | --- | ---------- | --- |
4.5 Side-effects tasks.Usersinvoketheirprogramwithaspecialflagand
|                                    |                                        |           |              |              |            |               | can then        | easily use  | any debugging |      | or testing |     | tools they |
| ---------------------------------- | -------------------------------------- | --------- | ------------ | ------------ | ---------- | ------------- | --------------- | ----------- | ------------- | ---- | ---------- | --- | ---------- |
| In some                            | cases,                                 | users     | of MapReduce |              | have       | found it con- | finduseful(e.g. | gdb).       |               |      |            |     |            |
| venient                            | to produce                             | auxiliary |              | files as     | additional | outputs       |                 |             |               |      |            |     |            |
| fromtheirmapand/orreduceoperators. |                                        |           |              |              | We         | relyonthe     |                 |             |               |      |            |     |            |
|                                    |                                        |           |              |              |            |               | 4.8 Status      | Information |               |      |            |     |            |
| application                        | writer                                 | to make   | such         | side-effects |            | atomic and    |                 |             |               |      |            |     |            |
| idempotent.                        | Typicallytheapplicationwritestoatempo- |           |              |              |            |               |                 |             |               |      |            |     |            |
|                                    |                                        |           |              |              |            |               | The master      | runs        | an internal   | HTTP | server     | and | exports    |
raryfileandatomicallyrenamesthisfileonceithasbeen
|     |     |     |     |     |     |     | a set of | status pages | for | human | consumption. |     | The sta- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------------ | --- | ----- | ------------ | --- | -------- |
fullygenerated.
tuspagesshowtheprogressofthecomputation,suchas
Wedonotprovidesupportforatomictwo-phasecom-
howmanytaskshavebeencompleted,howmanyarein
mits of multiple output files produced by a single task. progress,bytesofinput,bytesofintermediatedata,bytes
| Therefore, | tasks                         | that | produce | multiple | output | files with   |            |            |        |      |           |      |         |
| ---------- | ----------------------------- | ---- | ------- | -------- | ------ | ------------ | ---------- | ---------- | ------ | ---- | --------- | ---- | ------- |
|            |                               |      |         |          |        |              | of output, | processing | rates, | etc. | The pages | also | contain |
| cross-file | consistencyrequirementsshould |      |         |          |        | be determin- |            |            |        |      |           |      |         |
linkstothestandarderrorandstandardoutputfilesgen-
istic. Thisrestrictionhasneverbeenanissueinpractice.
|     |     |     |     |     |     |     | erated by | each task. | The | user can | use | this data | to pre- |
| --- | --- | --- | --- | --- | --- | --- | --------- | ---------- | --- | -------- | --- | --------- | ------- |
dicthowlongthecomputationwilltake,andwhetheror
4.6 SkippingBad Records notmoreresourcesshouldbeaddedtothecomputation.
Thesepagescanalsobeusedtofigureoutwhenthecom-
SometimestherearebugsinusercodethatcausetheMap putationismuchslowerthanexpected.
orReducefunctionstocrashdeterministicallyoncertain
|     |     |     |     |     |     |     | In addition, | the | top-level | status | page | shows | which |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | --------- | ------ | ---- | ----- | ----- |
records.SuchbugspreventaMapReduceoperationfrom
|             |                                      |     |     |     |     |     | workers   | have failed, | and  | which | map and | reduce | tasks    |
| ----------- | ------------------------------------ | --- | --- | --- | --- | --- | --------- | ------------ | ---- | ----- | ------- | ------ | -------- |
| completing. | Theusualcourseofactionistofixthebug, |     |     |     |     |     |           |              |      |       |         |        |          |
|             |                                      |     |     |     |     |     | they were | processing   | when | they  | failed. | This   | informa- |
butsometimesthisisnotfeasible; perhapsthe bugisin tion is useful when attempting to diagnose bugs in the
| a third-party | library | for | which | source | code | is unavail- |     |     |     |     |     |     |     |
| ------------- | ------- | --- | ----- | ------ | ---- | ----------- | --- | --- | --- | --- | --- | --- | --- |
usercode.
| able. Also,    | sometimes   |                                 | it is | acceptable        | to  | ignore a few |              |     |     |     |     |     |     |
| -------------- | ----------- | ------------------------------- | ----- | ----------------- | --- | ------------ | ------------ | --- | --- | --- | --- | --- | --- |
| records,       | for example |                                 | when  | doing statistical |     | analysis on  |              |     |     |     |     |     |     |
| alargedataset. |             | Weprovideanoptionalmodeofexecu- |       |                   |     |              | 4.9 Counters |     |     |     |     |     |     |
tionwheretheMapReducelibrarydetectswhichrecords
causedeterministiccrashesandskipstheserecordsinor- The MapReduce library provides a counter facility to
dertomakeforwardprogress. count occurrencesof various events. For example, user
Each worker process installs a signal handler that codemaywanttocounttotalnumberofwordsprocessed
orthenumberofGermandocumentsindexed,etc.
| catches | segmentation |     | violations | and | bus errors. | Before |     |     |     |     |     |     |     |
| ------- | ------------ | --- | ---------- | --- | ----------- | ------ | --- | --- | --- | --- | --- | --- | --- |
invoking a user Map or Reduce operation, the MapRe- Tousethisfacility,usercodecreatesanamedcounter
ducelibrarystoresthesequencenumberoftheargument object and then increments the counter appropriately in
ina globalvariable. Iftheusercodegeneratesa signal, theMapand/orReducefunction. Forexample:
USENIX Association OSDI ’04:6th Symposium on Operating Systems Design and Implementation 143

| Counter* |     | uppercase; |     |     |     |     |     |     | 30000 |     |     |     |     |     |
| -------- | --- | ---------- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
)s/BM( tupnI
| uppercase |     | =   | GetCounter("uppercase"); |     |     |     |     |     |     |     |     |     |     |     |
| --------- | --- | --- | ------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
20000
| map(String |     | name,     |     | String       | contents): |     |     |     |     |     |     |     |     |     |
| ---------- | --- | --------- | --- | ------------ | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|            | for | each word | w   | in contents: |            |     |     |     |     |     |     |     |     |     |
10000
|     | if                  | (IsCapitalized(w)):     |     |     |       |     |     |     |     |     |     |       |     |     |
| --- | ------------------- | ----------------------- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | ----- | --- | --- |
|     |                     | uppercase->Increment(); |     |     |       |     |     |     | 0   |     |     |       |     |     |
|     | EmitIntermediate(w, |                         |     |     | "1"); |     |     |     |     | 20  | 40  | 60 80 | 100 |     |
Seconds
| The | counter      | values     | from | individual | worker |              | machines |     |          |                          |     |     |     |     |
| --- | ------------ | ---------- | ---- | ---------- | ------ | ------------ | -------- | --- | -------- | ------------------------ | --- | --- | --- | --- |
| are | periodically | propagated |      | to the     | master | (piggybacked |          |     |          |                          |     |     |     |     |
|     |              |            |      |            |        |              |          |     | Figure2: | Datatransferrateovertime |     |     |     |     |
onthepingresponse).Themasteraggregatesthecounter
valuesfromsuccessfulmapandreducetasksandreturns
them to the user code when the MapReduce operation disks, and a gigabit Ethernet link. The machines were
| is completed. |     | The | current | counter | values | are | also dis- |          |      |           |             |          |     |         |
| ------------- | --- | --- | ------- | ------- | ------ | --- | --------- | -------- | ---- | --------- | ----------- | -------- | --- | ------- |
|               |     |     |         |         |        |     |           | arranged | in a | two-level | tree-shaped | switched |     | network |
played on the master status page so that a human can with approximately 100-200 Gbps of aggregate band-
watchtheprogressofthelivecomputation.Whenaggre-
|     |     |     |     |     |     |     |     | width available |     | at the root. | All | of the | machines | were |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ------------ | --- | ------ | -------- | ---- |
gatingcountervalues,themastereliminatestheeffectsof in the samehosting facility andthereforetheround-trip
duplicate executionsof the same map or reduce task to time betweenanypairofmachineswasless thana mil-
| avoid | double | counting. | (Duplicate |     | executions |     | can arise |     |     |     |     |     |     |     |
| ----- | ------ | --------- | ---------- | --- | ---------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
lisecond.
| from | our use | of backup |     | tasks and | from | re-execution | of  |        |         |            |               |     |     |         |
| ---- | ------- | --------- | --- | --------- | ---- | ------------ | --- | ------ | ------- | ---------- | ------------- | --- | --- | ------- |
|      |         |           |     |           |      |              |     | Out of | the 4GB | of memory, | approximately |     |     | 1-1.5GB |
tasksduetofailures.)
|     |     |     |     |     |     |     |     | wasreservedbyother |     | tasksrunningonthecluster. |     |     |     | The |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | ------------------------- | --- | --- | --- | --- |
Some counter values are automatically maintained programswere executedonaweekendafternoon, when
| by  | the MapReduce |     | library, | such | as the | number | of in- |     |     |     |     |     |     |     |
| --- | ------------- | --- | -------- | ---- | ------ | ------ | ------ | --- | --- | --- | --- | --- | --- | --- |
theCPUs,disks,andnetworkweremostlyidle.
| put | key/valuepairs |     | processed | and | the numberof |     | output |     |     |     |     |     |     |     |
| --- | -------------- | --- | --------- | --- | ------------ | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
key/valuepairsproduced.
| Users | have | found | the | counter | facility | useful | for san- | 5.2 Grep |     |     |     |     |     |     |
| ----- | ---- | ----- | --- | ------- | -------- | ------ | -------- | -------- | --- | --- | --- | --- | --- | --- |
itycheckingthebehaviorofMapReduceoperations.For
|     |     |     |     |     |     |     |     | Thegrepprogramscansthrough1010 |     |     |     | 100-byterecords, |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------ | --- | --- | --- | ---------------- | --- | --- |
example,insomeMapReduceoperations,theusercode
may want to ensure that the number of output pairs searchingforarelativelyrarethree-characterpattern(the
|          |         |          |          |            |     |             |      | patternoccursin92,337records). |     |     |     | Theinputissplitinto |     |     |
| -------- | ------- | -------- | -------- | ---------- | --- | ----------- | ---- | ------------------------------ | --- | --- | --- | ------------------- | --- | --- |
| produced | exactly |          | equals   | the number | of  | input pairs | pro- |                                |     |     |     |                     |     |     |
|          |         |          |          |            |     |             |      | approximately64MBpieces        |     |     | (M  | 15000),andtheen-    |     |     |
| cessed,  | or      | that the | fraction | of German  |     | documents   | pro- |                                |     |     |     | =                   |     |     |
tireoutputisplacedinonefile(R=1).
cessediswithinsometolerablefractionofthetotalnum-
berofdocumentsprocessed. Figure 2 shows the progress of the computation over
time.TheY-axisshowstherateatwhichtheinputdatais
|     |     |     |     |     |     |     |     | scanned. | Therategraduallypicksupasmoremachines |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------------------------------------- | --- | --- | --- | --- | --- |
5 Performance
areassignedtothisMapReducecomputation,andpeaks
atover30GB/swhen1764workershavebeenassigned.
| In this | section | we  | measure | the performance |     | of  | MapRe- |     |     |     |     |     |     |     |
| ------- | ------- | --- | ------- | --------------- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
Asthemaptasksfinish,theratestartsdroppingandhits
| duceon    | two | computations    |     | runningon | a       | largecluster | of       |           |           |         |              |     |     |        |
| --------- | --- | --------------- | --- | --------- | ------- | ------------ | -------- | --------- | --------- | ------- | ------------ | --- | --- | ------ |
|           |     |                 |     |           |         |              |          | zeroabout | 80seconds | intothe | computation. |     | The | entire |
| machines. |     | One computation |     | searches  | through |              | approxi- |           |           |         |              |     |     |        |
computationtakesapproximately150secondsfromstart
matelyoneterabyteofdatalookingforaparticularpat-
|     |     |     |     |     |     |     |     | to finish. | This | includes about | a minute | of  | startup | over- |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---- | -------------- | -------- | --- | ------- | ----- |
tern.Theothercomputationsortsapproximatelyoneter-
|     |     |     |     |     |     |     |     | head. Theoverheadisduetothepropagationofthepro- |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
abyteofdata.
gramtoallworkermachines,anddelaysinteractingwith
Thesetwoprogramsarerepresentativeofalargesub-
|     |     |     |     |     |     |     |     | GFS to | open the | set of | 1000 input | files | and to | get the |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | -------- | ------ | ---------- | ----- | ------ | ------- |
setoftherealprogramswrittenbyusersofMapReduce–
informationneededforthelocalityoptimization.
oneclassofprogramsshufflesdatafromonerepresenta-
tiontoanother,andanotherclassextractsasmallamount
| ofinterestingdatafromalargedataset. |     |     |     |     |     |     |     | 5.3 Sort |                  |     |          |                  |     |     |
| ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | -------- | ---------------- | --- | -------- | ---------------- | --- | --- |
|                                     |     |     |     |     |     |     |     | Thesort  | programsorts1010 |     | 100-byte | records(approxi- |     |     |
5.1 ClusterConfiguration
mately1terabyteofdata).Thisprogramismodeledafter
theTeraSortbenchmark[10].
| All | of the | programs | were | executed | on  | a cluster | that |     |     |     |     |     |     |     |
| --- | ------ | -------- | ---- | -------- | --- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- |
consisted of approximately 1800 machines. Each ma- The sorting program consists of less than 50 lines of
chinehadtwo2GHzIntelXeonprocessorswithHyper- usercode. Athree-lineMapfunctionextractsa10-byte
Threading enabled, 4GB of memory, two 160GB IDE sorting key from a text line and emits the key and the
144 OSDI ’04:6th Symposium on Operating Systems Design and Implementation USENIX Association

20000
15000
10000
5000
0
500 1000
)s/BM(
tupnI
20000
15000
10000
5000
0
500 1000
)s/BM(
elffuhS
20000
15000
10000
5000
0
500 1000
Seconds
)s/BM(
tuptuO
Done 20000
15000
10000
5000
0
500 1000
(a)Normalexecution
)s/BM(
tupnI
20000
15000
10000
5000
0
500 1000
)s/BM(
elffuhS
20000
15000
10000
5000
0
500 1000
Seconds
)s/BM(
tuptuO
20000
Done 15000
10000
5000
0
500 1000
(b)Nobackuptasks
)s/BM(
tupnI
20000
15000
10000
5000
0
500 1000
)s/BM(
elffuhS
20000
15000
10000
5000
0
500 1000
Seconds
)s/BM(
tuptuO
Done
(c)200taskskilled
Figure3: Datatransferratesovertimefordifferentexecutionsofthesortprogram
originaltextlineastheintermediatekey/valuepair. We the first batch of approximately 1700 reduce tasks (the
used a built-in Identity functionas the Reduce operator. entire MapReduce was assigned about 1700 machines,
Thisfunctionspassestheintermediatekey/valuepairun- andeachmachineexecutesatmostonereducetask ata
changed as the output key/value pair. The final sorted time). Roughly300secondsintothecomputation,some
output is written to a set of 2-way replicated GFS files of these first batch of reduce tasks finish and we start
(i.e.,2terabytesarewrittenastheoutputoftheprogram). shufflingdatafortheremainingreducetasks. Allofthe
shufflingisdoneabout600secondsintothecomputation.
As before, the input data is split into 64MB pieces
(M = 15000). We partitionthesortedoutputinto4000 The bottom-leftgraph showsthe rateat whichsorted
files(R = 4000). Thepartitioningfunctionusestheini- dataiswrittentothefinaloutputfilesbythereducetasks.
tialbytesofthekeytosegregateitintooneofRpieces. Thereisadelaybetweentheendofthefirstshufflingpe-
riod and the start of the writing period because the ma-
Ourpartitioningfunctionforthisbenchmarkhasbuilt-
chinesarebusysortingtheintermediatedata. Thewrites
in knowledge of the distribution of keys. In a general
continueat a rate ofabout 2-4 GB/s for a while. All of
sorting program, we would add a pre-pass MapReduce
thewritesfinishabout850secondsintothecomputation.
operation that would collect a sample of the keys and
Includingstartupoverhead,theentirecomputationtakes
usethedistributionofthesampledkeystocomputesplit-
891seconds. Thisissimilartothecurrentbestreported
pointsforthefinalsortingpass.
resultof1057secondsfortheTeraSortbenchmark[18].
Figure3(a)showstheprogressofanormalexecution
Afewthingstonote: theinputrateishigherthanthe
of the sort program. The top-left graph shows the rate
shuffle rate and the output rate because of our locality
atwhichinputisread. Theratepeaksatabout13GB/s
optimization – most data is read from a local disk and
anddies offfairlyquicklysinceallmaptasksfinishbe-
bypasses our relatively bandwidth constrained network.
fore 200 seconds haveelapsed. Note that the input rate
The shuffle rate is higher than the output rate because
islessthanfor grep. Thisisbecausethesortmaptasks
theoutputphasewritestwocopiesofthesorteddata(we
spendabouthalftheirtimeandI/Obandwidthwritingin-
maketworeplicasoftheoutputforreliabilityandavail-
termediateoutputtotheirlocaldisks. Thecorresponding
ability reasons). We write two replicas because that is
intermediateoutputforgrephadnegligiblesize.
the mechanism for reliability and availability provided
The middle-left graph shows the rate at which data by our underlying file system. Network bandwidth re-
is sent over the network from the map tasks to the re- quirementsfor writingdatawouldbereducediftheun-
duce tasks. This shuffling starts as soon as the first derlyingfilesystemusederasurecoding[14]ratherthan
map task completes. The first hump in the graph is for replication.
USENIX Association OSDI ’04:6th Symposium on Operating Systems Design and Implementation 145

1000
| 5.4 Effect |     | ofBackup |     | Tasks |     |     |     |     |     |     |     |     |
| ---------- | --- | -------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
eert ecruos ni secnatsni fo rebmuN
| In Figure | 3 (b), | we  | show an | execution | of  | the sort | pro- |     |     |     |     |     |
| --------- | ------ | --- | ------- | --------- | --- | -------- | ---- | --- | --- | --- | --- | --- |
800
| gramwithbackuptasksdisabled. |     |     |     | Theexecutionflowis |     |     |     |     |     |     |     |     |
| ---------------------------- | --- | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- |
similartothatshowninFigure3(a),exceptthatthereis
600
| a very long | tail     | where | hardly | any  | write activity |       | occurs. |     |     |     |     |     |
| ----------- | -------- | ----- | ------ | ---- | -------------- | ----- | ------- | --- | --- | --- | --- | --- |
| After 960   | seconds, | all   | except | 5 of | the reduce     | tasks | are     |     |     |     |     |     |
400
| completed.                                | Howeverthese |     | lastfew                   |     | stragglersdon’tfin- |     |     |     |     |     |     |     |
| ----------------------------------------- | ------------ | --- | ------------------------- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- |
| ishuntil300secondslater.                  |              |     | Theentirecomputationtakes |     |                     |     |     |     |     |     |     |     |
| 1283seconds,anincreaseof44%inelapsedtime. |              |     |                           |     |                     |     |     |     | 200 |     |     |     |
0
5.5 MachineFailures
|     |     |     |     |     |     |     |     |     | 2003/03 2003/06 2003/09 | 2003/12 | 2004/03 | 2004/06 2004/09 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------- | ------- | ------- | --------------- |
InFigure3(c),weshowanexecutionofthesortprogram
| where we   | intentionally |           | killed | 200         | out of       | 1746      | worker |          |                            |     |     |     |
| ---------- | ------------- | --------- | ------ | ----------- | ------------ | --------- | ------ | -------- | -------------------------- | --- | --- | --- |
|            |               |           |        |             |              |           |        | Figure4: | MapReduceinstancesovertime |     |     |     |
| processes  | several       | minutes   | into   | the         | computation. |           | The    |          |                            |     |     |     |
| underlying | cluster       | scheduler |        | immediately |              | restarted | new    |          |                            |     |     |     |
workerprocessesonthesemachines(sinceonlythepro- Numberofjobs 29,423
|             |         |        |          |       |            |             |      | Averagejobcompletiontime |     |     |            | 634secs |
| ----------- | ------- | ------ | -------- | ----- | ---------- | ----------- | ---- | ------------------------ | --- | --- | ---------- | ------- |
| cesses were | killed, | the    | machines | were  | still      | functioning |      |                          |     |     |            |         |
| properly).  |         |        |          |       |            |             |      | Machinedaysused          |     |     | 79,186days |         |
|             |         |        |          |       |            |             |      | Inputdataread            |     |     | 3,288TB    |         |
| The worker  |         | deaths | show     | up as | a negative | input       | rate |                          |     |     |            |         |
|             |         |        |          |       |            |             |      | Intermediatedataproduced |     |     |            | 758TB   |
since some previously completed map work disappears Outputdatawritten 193TB
| (since the | corresponding |     | map                | workers | were | killed)  | and  |                             |     |     |     |     |
| ---------- | ------------- | --- | ------------------ | ------- | ---- | -------- | ---- | --------------------------- | --- | --- | --- | --- |
|            |               |     |                    |         |      |          |      | Averageworkermachinesperjob |     |     |     | 157 |
| needs to   | be redone.    |     | The re-executionof |         |      | this map | work |                             |     |     |     |     |
|            |               |     |                    |         |      |          |      | Averageworkerdeathsperjob   |     |     |     | 1.2 |
happens relatively quickly. The entire computation fin- Averagemaptasksperjob 3,351
ishesin933secondsincludingstartupoverhead(justan Averagereducetasksperjob 55
|     |     |     |     |     |     |     |     | Uniquemapimplementations |     |     |     | 395 |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | --- | --- | --- |
increaseof5%overthenormalexecutiontime).
|     |     |     |     |     |     |     |     | Uniquereduceimplementations  |     |     |     | 269 |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- |
|     |     |     |     |     |     |     |     | Uniquemap/reducecombinations |     |     |     | 426 |
6 Experience
|          |     |               |     |               |     |         |     | Table1: | MapReducejobsruninAugust2004 |     |     |     |
| -------- | --- | ------------- | --- | ------------- | --- | ------- | --- | ------- | ---------------------------- | --- | --- | --- |
| We wrote | the | first version | of  | the MapReduce |     | library | in  |         |                              |     |     |     |
Februaryof2003,andmadesignificantenhancementsto
itinAugustof2003,includingthelocalityoptimization, Figure 4 shows the significant growth in the number of
dynamicloadbalancingoftaskexecutionacrossworker
separateMapReduceprogramscheckedintoourprimary
machines,etc. Sincethattime,wehavebeenpleasantly source code management system over time, from 0 in
| surprised | at how | broadly | applicable |     | the MapReduce |     | li- |            |               |          |           |            |
| --------- | ------ | ------- | ---------- | --- | ------------- | --- | --- | ---------- | ------------- | -------- | --------- | ---------- |
|           |        |         |            |     |               |     |     | early 2003 | to almost 900 | separate | instances | as of late |
brary has been for the kinds of problems we work on. September2004.MapReducehasbeensosuccessfulbe-
It has beenusedacross a widerange ofdomains within causeitmakesitpossibletowriteasimpleprogramand
Google,including:
|     |     |     |     |     |     |     |     | run it efficiently | on a thousand | machines |     | in the course |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | ------------- | -------- | --- | ------------- |
ofhalfanhour,greatlyspeedingupthedevelopmentand
• large-scalemachinelearningproblems,
|              |     |          |     |     |        |      |     | prototyping             | cycle. Furthermore, | it                        | allows | programmers |
| ------------ | --- | -------- | --- | --- | ------ | ---- | --- | ----------------------- | ------------------- | ------------------------- | ------ | ----------- |
|              |     |          |     |     |        |      |     | whohavenoexperiencewith |                     | distributedand/orparallel |        |             |
| • clustering |     | problems | for | the | Google | News | and |                         |                     |                           |        |             |
systemstoexploitlargeamountsofresourceseasily.
Froogleproducts,
|     |     |     |     |     |     |     |     | At the | end of each job, | the MapReduce |     | library logs |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ---------------- | ------------- | --- | ------------ |
• extractionofdatausedtoproducereportsofpopular statisticsabout the computational resources usedby the
queries(e.g. GoogleZeitgeist), job. In Table 1, we showsome statisticsfor a subset of
MapReducejobsrunatGoogleinAugust2004.
extractionofpropertiesofwebpagesfornewexper-
•
| iments | and | products | (e.g. | extraction |     | of geographi- |     |     |     |     |     |     |
| ------ | --- | -------- | ----- | ---------- | --- | ------------- | --- | --- | --- | --- | --- | --- |
cal locations from a large corpus of web pages for 6.1 Large-Scale Indexing
localizedsearch),and
|     |     |     |     |     |     |     |     | One of our | most significant | uses of | MapReduce | to date |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---------------- | ------- | --------- | ------- |
• large-scalegraphcomputations. has been a complete rewrite of the production index-
146 OSDI ’04:6th Symposium on Operating Systems Design and Implementation USENIX Association

ingsystemthatproducesthedatastructuresusedforthe make it easier for programmers to write parallel pro-
Google web search service. The indexing system takes grams. A key difference between these systems and
asinputalargesetofdocumentsthathavebeenretrieved MapReduceisthatMapReduceexploitsarestrictedpro-
byourcrawlingsystem,storedasasetofGFSfiles. The gramming model to parallelize the user program auto-
rawcontents for these documents are more than 20 ter- maticallyandtoprovidetransparentfault-tolerance.
abytesofdata. Theindexingprocessrunsasasequence Our locality optimization draws its inspiration from
offivetotenMapReduceoperations. UsingMapReduce techniques such as active disks [12, 15], where compu-
(insteadofthead-hocdistributedpassesinthepriorver- tation is pushed into processing elements that are close
sionoftheindexingsystem)has providedseveralbene- to local disks, to reduce the amount of data sent across
fits:
|     |     |     |     |     |     | I/O subsystems | or  | the network. | We  | run on | commodity |
| --- | --- | --- | --- | --- | --- | -------------- | --- | ------------ | --- | ------ | --------- |
processorstowhichasmallnumberofdisksaredirectly
Theindexingcodeissimpler,smaller,andeasierto
| •           |         |     |      |            |            | connectedinstead |     | ofrunning | directly | ondisk | controller |
| ----------- | ------- | --- | ---- | ---------- | ---------- | ---------------- | --- | --------- | -------- | ------ | ---------- |
| understand, | because | the | code | that deals | with fault |                  |     |           |          |        |            |
processors,butthegeneralapproachissimilar.
| tolerance, | distribution | andparallelizationishidden |          |     |              |            |           |           |     |                  |              |
| ---------- | ------------ | -------------------------- | -------- | --- | ------------ | ---------- | --------- | --------- | --- | ---------------- | ------------ |
|            |              |                            |          |     |              | Our backup | task      | mechanism | is  | similar          | to the eager |
| within the | MapReduce    |                            | library. | For | example, the |            |           |           |     |                  |              |
|            |              |                            |          |     |              | scheduling | mechanism | employed  |     | in the Charlotte | Sys-         |
sizeofonephaseofthecomputationdroppedfrom
|               |      |       |        |      |            | tem [3]. | One | of the shortcomings |     | of  | simple eager |
| ------------- | ---- | ----- | ------ | ---- | ---------- | -------- | --- | ------------------- | --- | --- | ------------ |
| approximately | 3800 | lines | of C++ | code | to approx- |          |     |                     |     |     |              |
schedulingisthatifagiventaskcausesrepeatedfailures,
| imately | 700 lines | when | expressed | using | MapRe- |     |     |     |     |     |     |
| ------- | --------- | ---- | --------- | ----- | ------ | --- | --- | --- | --- | --- | --- |
theentirecomputationfailstocomplete.Wefixsomein-
duce.
stancesofthisproblemwithourmechanismforskipping
| • TheperformanceoftheMapReducelibraryisgood |     |     |     |     |     | badrecords. |     |     |     |     |     |
| ------------------------------------------- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- |
enough that we can keep conceptually unrelated TheMapReduceimplementationreliesonanin-house
computations separate, instead of mixing them to- cluster management system that is responsible for dis-
gether to avoid extra passes over the data. This tributing andrunninguser tasksona largecollection of
|          |         |        |              |     |              | sharedmachines. |     | Thoughnotthefocusofthispaper,the |     |     |     |
| -------- | ------- | ------ | ------------ | --- | ------------ | --------------- | --- | -------------------------------- | --- | --- | --- |
| makes it | easy to | change | the indexing |     | process. For |                 |     |                                  |     |     |     |
example, one change that took a few months to cluster management system is similar in spirit to other
make in our old indexing system took only a few systemssuchasCondor[16].
daystoimplementinthenewsystem. The sorting facility that is a part of the MapReduce
|              |           |         |           |          |            | library is similar                             |          | in operationto | NOW-Sort |          | [1]. Source  |
| ------------ | --------- | ------- | --------- | -------- | ---------- | ---------------------------------------------- | -------- | -------------- | -------- | -------- | ------------ |
| The indexing | process   | has     | become    | much     | easier to  |                                                |          |                |          |          |              |
| •            |           |         |           |          |            | machines (map                                  | workers) | partition      |          | the data | to be sorted |
| operate,     | because   | most of | the       | problems | caused by  |                                                |          |                |          |          |              |
|              |           |         |           |          |            | and send it                                    | to one   | of R reduce    | workers. |          | Each reduce  |
| machine      | failures, | slow    | machines, | and      | networking |                                                |          |                |          |          |              |
|              |           |         |           |          |            | workersortsitsdatalocally(inmemoryifpossible). |          |                |          |          | Of           |
hiccupsaredealtwithautomaticallybytheMapRe-
courseNOW-Sortdoesnothavetheuser-definableMap
ducelibrarywithoutoperatorintervention.Further-
andReducefunctionsthatmakeourlibrarywidelyappli-
| more, it | is easy | to improvethe |     | performance | of the |     |     |     |     |     |     |
| -------- | ------- | ------------- | --- | ----------- | ------ | --- | --- | --- | --- | --- | --- |
cable.
indexingprocessbyaddingnewmachinestothein-
|     |     |     |     |     |     | River [2] | provides | a programming |     | model | where pro- |
| --- | --- | --- | --- | --- | --- | --------- | -------- | ------------- | --- | ----- | ---------- |
dexingcluster.
|     |     |     |     |     |     | cesses communicate |     | with each    | other      | by  | sending data |
| --- | --- | --- | --- | --- | --- | ------------------ | --- | ------------ | ---------- | --- | ------------ |
|     |     |     |     |     |     | over distributed   |     | queues. Like | MapReduce, |     | the River    |
7 Related Work system tries to provide good average case performance
|     |     |     |     |     |     | even in the | presence | of non-uniformities |     |     | introduced by |
| --- | --- | --- | --- | --- | --- | ----------- | -------- | ------------------- | --- | --- | ------------- |
Many systems have provided restricted programming heterogeneous hardwareor system perturbations. River
models and used the restrictions to parallelize the com- achievesthisbycarefulschedulingofdisk andnetwork
putationautomatically.Forexample,anassociativefunc- transferstoachievebalancedcompletiontimes. MapRe-
tioncanbecomputed overallprefixesofan N element duce has a different approach. By restricting the pro-
arrayinlogN timeonN processorsusingparallelprefix gramming model, the MapReduce framework is able
computations[6, 9, 13]. MapReducecan beconsidered to partition the problem into a large number of fine-
asimplificationanddistillationofsomeofthesemodels grained tasks. These tasks are dynamically scheduled
based on our experience with large real-world compu- onavailableworkerssothatfasterworkersprocessmore
tations. More significantly, we provide a fault-tolerant tasks. The restricted programming model also allows
implementation that scales to thousands of processors. us to schedule redundant executions of tasks near the
Incontrast,mostoftheparallelprocessingsystemshave endofthejobwhichgreatlyreducescompletiontimein
only been implemented on smaller scales and leave the the presence of non-uniformities (such as slow or stuck
| detailsofhandlingmachinefailurestotheprogrammer. |     |     |     |     |     | workers). |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- |
Bulk Synchronous Programming [17] and some MPI BAD-FS[5]hasaverydifferentprogrammingmodel
primitives [11] provide higher-level abstractions that fromMapReduce,andunlikeMapReduce,istargetedto
USENIX Association OSDI ’04:6th Symposium on Operating Systems Design and Implementation 147

theexecutionofjobsacrossawide-areanetwork. How- DavidKramer,Shun-TakLeung,andJoshRedstonefor
ever, there are two fundamental similarities. (1) Both their work in developing GFS. We would also like to
systems use redundant execution to recover from data thank Percy Liang and Olcan Sercinoglu for their work
loss caused by failures. (2) Both use locality-aware in developing the cluster management system used by
schedulingtoreducetheamountofdatasentacrosscon- MapReduce. MikeBurrows,WilsonHsieh,JoshLeven-
gestednetworklinks. berg, Sharon Perl, Rob Pike, and Debby Wallach pro-
TACC [7] is a system designed to simplify con- vided helpful comments on earlier drafts of this pa-
|           |                     |     |           |     |           |      | per. TheanonymousOSDIreviewers,andourshepherd, |     |     |     |     |     |
| --------- | ------------------- | --- | --------- | --- | --------- | ---- | ---------------------------------------------- | --- | --- | --- | --- | --- |
| struction | of highly-available |     | networked |     | services. | Like |                                                |     |     |     |     |     |
EricBrewer,providedmanyusefulsuggestionsofareas
MapReduce,itreliesonre-executionasamechanismfor
implementingfault-tolerance. wherethepapercouldbeimproved.Finally,wethankall
theusersofMapReducewithinGoogle’sengineeringor-
|               |     |     |     |     |     |     | ganization     | for providing | helpful |     | feedback, | suggestions, |
| ------------- | --- | --- | --- | --- | --- | --- | -------------- | ------------- | ------- | --- | --------- | ------------ |
| 8 Conclusions |     |     |     |     |     |     | andbugreports. |               |         |     |           |              |
TheMapReduceprogrammingmodelhasbeensuccess-
References
| fully used                            | at Google | for | many | different | purposes.      | We  |     |     |     |     |     |     |
| ------------------------------------- | --------- | --- | ---- | --------- | -------------- | --- | --- | --- | --- | --- | --- | --- |
| attributethissuccesstoseveralreasons. |           |     |      |           | First,themodel |     |     |     |     |     |     |     |
iseasytouse,evenforprogrammerswithoutexperience [1] Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau,
DavidE.Culler,JosephM.Hellerstein,andDavidA.Pat-
| with parallel | and | distributed | systems, | since | it  | hides the |     |     |     |     |     |     |
| ------------- | --- | ----------- | -------- | ----- | --- | --------- | --- | --- | --- | --- | --- | --- |
details of parallelization, fault-tolerance, locality opti- terson. High-performancesortingonnetworksofwork-
|           |          |            |     |         |         |         | stations. | InProceedingsofthe1997ACMSIGMODIn- |     |     |     |     |
| --------- | -------- | ---------- | --- | ------- | ------- | ------- | --------- | ---------------------------------- | --- | --- | --- | --- |
| mization, | and load | balancing. |     | Second, | a large | variety |           |                                    |     |     |     |     |
ternationalConferenceonManagementofData,Tucson,
| of problems | are | easily expressible |     | as MapReduce |     | com- |     |     |     |     |     |     |
| ----------- | --- | ------------------ | --- | ------------ | --- | ---- | --- | --- | --- | --- | --- | --- |
Arizona,May1997.
| putations. | Forexample,MapReduceisusedforthegen- |     |     |     |     |     |     |     |     |     |     |     |
| ---------- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
eration of data for Google’sproduction web search ser- [2] Remzi H. Arpaci-Dusseau, Eric Anderson, Noah
vice, for sorting, for data mining, for machinelearning, Treuhaft, DavidE.Culler, JosephM.Hellerstein, David
and many other systems. Third, we have developed an Patterson, and Kathy Yelick. Cluster I/O with River:
Makingthefastcasecommon.InProceedingsoftheSixth
implementationofMapReducethatscalestolargeclus-
|     |     |     |     |     |     |     | Workshop | on  | Input/Output | in  | Parallel | and Distributed |
| --- | --- | --- | --- | --- | --- | --- | -------- | --- | ------------ | --- | -------- | --------------- |
tersofmachinescomprisingthousandsofmachines.The
|     |     |     |     |     |     |     | Systems | (IOPADS | ’99), | pages | 10–22, Atlanta, | Georgia, |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------- | ----- | ----- | --------------- | -------- |
implementationmakesefficientuseofthesemachinere-
May1999.
| sourcesandthereforeissuitablefor |     |     |     | use | onmanyofthe |     |     |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
largecomputationalproblemsencounteredatGoogle. [3] Arash Baratloo, Mehmet Karaul, Zvi Kedem, and Peter
|                                          |     |     |     |     |     |        | Wyckoff. | Charlotte:Metacomputingontheweb. |     |     |     | InPro- |
| ---------------------------------------- | --- | --- | --- | --- | --- | ------ | -------- | -------------------------------- | --- | --- | --- | ------ |
| We havelearnedseveralthingsfromthiswork. |     |     |     |     |     | First, |          |                                  |     |     |     |        |
ceedingsofthe9thInternationalConferenceonParallel
restrictingtheprogrammingmodelmakesiteasytopar-
andDistributedComputingSystems,1996.
| allelize | and distribute | computations |     | and | to make | such |          |             |         |       |         |              |
| -------- | -------------- | ------------ | --- | --- | ------- | ---- | -------- | ----------- | ------- | ----- | ------- | ------------ |
|          |                |              |     |     |         |      | [4] Luiz | A. Barroso, | Jeffrey | Dean, | and Urs | Ho¨lzle. Web |
computationsfault-tolerant.Second,networkbandwidth
searchforaplanet:TheGoogleclusterarchitecture.IEEE
| is a scarce | resource. | A   | number | of optimizations |     | in our |     |     |     |     |     |     |
| ----------- | --------- | --- | ------ | ---------------- | --- | ------ | --- | --- | --- | --- | --- | --- |
Micro,23(2):22–28,April2003.
| system are | thereforetargetedat |     |     | reducing | the amount | of  |     |     |     |     |     |     |
| ---------- | ------------------- | --- | --- | -------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
datasentacrossthenetwork:thelocalityoptimizational- [5] John Bent, Douglas Thain, Andrea C.Arpaci-Dusseau,
lowsustoreaddatafromlocaldisks,andwritingasingle Remzi H. Arpaci-Dusseau, and Miron Livny. Explicit
|     |     |     |     |     |     |     | controlinabatch-awaredistributedfilesystem. |     |     |     |     | InPro- |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------- | --- | --- | --- | --- | ------ |
copyoftheintermediatedatatolocaldisksavesnetwork
|            |        |           |     |           |        |         | ceedings | of the | 1st USENIX |     | Symposium | on Networked |
| ---------- | ------ | --------- | --- | --------- | ------ | ------- | -------- | ------ | ---------- | --- | --------- | ------------ |
| bandwidth. | Third, | redundant |     | execution | can be | used to |          |        |            |     |           |              |
SystemsDesignandImplementationNSDI,March2004.
| reduce the | impact | of slowmachines, |     | andto | handle | ma- |     |     |     |     |     |     |
| ---------- | ------ | ---------------- | --- | ----- | ------ | --- | --- | --- | --- | --- | --- | --- |
chinefailuresanddataloss. [6] GuyE.Blelloch. Scansasprimitiveparalleloperations.
|     |     |     |     |     |     |     | IEEE | Transactions | on  | Computers, | C-38(11), | November |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------------ | --- | ---------- | --------- | -------- |
1989.
Acknowledgements
|                |     |          |              |     |             |     | [7] Armando          | Fox,    | Steven   | D. Gribble,               | Yatin         | Chawathe, |
| -------------- | --- | -------- | ------------ | --- | ----------- | --- | -------------------- | ------- | -------- | ------------------------- | ------------- | --------- |
|                |     |          |              |     |             |     | Eric A.              | Brewer, | and Paul | Gauthier.                 | Cluster-based | scal-     |
| Josh Levenberg |     | has been | instrumental |     | in revising | and |                      |         |          |                           |               |           |
|                |     |          |              |     |             |     | ablenetworkservices. |         |          | InProceedingsofthe16thACM |               |           |
extending the user-level MapReduce API with a num- Symposium on Operating System Principles, pages 78–
ber of new features based on his experience with using 91,Saint-Malo,France,1997.
MapReduceandotherpeople’ssuggestionsforenhance- [8] Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Le-
| ments.                          | MapReduce | reads  | its      | input from | and         | writes its |                           |         |             |                      |        |              |
| ------------------------------- | --------- | ------ | -------- | ---------- | ----------- | ---------- | ------------------------- | ------- | ----------- | -------------------- | ------ | ------------ |
|                                 |           |        |          |            |             |            | ung. TheGooglefilesystem. |         |             | In19thSymposiumonOp- |        |              |
| outputtotheGoogleFileSystem[8]. |           |        |          | We         | wouldliketo |            |                           |         |             |                      |        |              |
|                                 |           |        |          |            |             |            | erating                   | Systems | Principles, | pages                | 29–43, | Lake George, |
| thank Mohit                     | Aron,     | Howard | Gobioff, | Markus     | Gutschke,   |            | NewYork,2003.             |         |             |                      |        |              |
148 OSDI ’04:6th Symposium on Operating Systems Design and Implementation USENIX Association

| [9] | S. Gorlatch. | Systematicefficient |     |     | parallelization | ofscan |     |        |      |     |     |
| --- | ------------ | ------------------- | --- | --- | --------------- | ------ | --- | ------ | ---- | --- | --- |
|     |              |                     |     |     |                 |        | if  | (start | < i) |     |     |
Emit(text.substr(start,i-start),"1");
|     | andotherlisthomomorphisms. |     |     | InL.Bouge,P.Fraigni- |     |     |     |     |     |     |     |
| --- | -------------------------- | --- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- |
}
|     | aud, A. | Mignotte, | and Y. | Robert, | editors, | Euro-Par’96. |     |     |     |     |     |
| --- | ------- | --------- | ------ | ------- | -------- | ------------ | --- | --- | --- | --- | --- |
}
ParallelProcessing,LectureNotesinComputerScience
};
1124,pages401–408.Springer-Verlag,1996.
REGISTER_MAPPER(WordCounter);
| [10] | Jim Gray. |     | Sort | benchmark |     | home page. |     |     |     |     |     |
| ---- | --------- | --- | ---- | --------- | --- | ---------- | --- | --- | --- | --- | --- |
http://research.microsoft.com/barc/SortBenchmark/. // User’s reduce function
|      |         |        |       |           |         |           | class Adder | : public                 | Reducer | {   |          |
| ---- | ------- | ------ | ----- | --------- | ------- | --------- | ----------- | ------------------------ | ------- | --- | -------- |
| [11] | William | Gropp, | Ewing | Lusk, and | Anthony | Skjellum. |             |                          |         |     |          |
|      |         |        |       |           |         |           | virtual     | void Reduce(ReduceInput* |         |     | input) { |
Using MPI: Portable Parallel Programming with the // Iterate over all entries with the
|     |                           |     |     |                        |     |     | // same | key   | and add | the values |     |
| --- | ------------------------- | --- | --- | ---------------------- | --- | --- | ------- | ----- | ------- | ---------- | --- |
|     | Message-PassingInterface. |     |     | MITPress,Cambridge,MA, |     |     |         |       |         |            |     |
|     |                           |     |     |                        |     |     | int64   | value | = 0;    |            |     |
1999.
|     |     |     |     |     |     |     | while | (!input->done()) |     | {   |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | ---------------- | --- | --- | --- |
[12] L.Huston,R.Sukthankar,R.Wickremesinghe,M.Satya- value += StringToInt(input->value());
narayanan,G.R.Ganger,E.Riedel,andA.Ailamaki.Di- input->NextValue();
|     | amond:        | Astoragearchitectureforearlydiscardininter- |     |     |     |     | }       |     |                  |     |     |
| --- | ------------- | ------------------------------------------- | --- | --- | --- | --- | ------- | --- | ---------------- | --- | --- |
|     | activesearch. | InProceedingsofthe2004USENIXFile            |     |     |     |     |         |     |                  |     |     |
|     |               |                                             |     |     |     |     | // Emit | sum | for input->key() |     |     |
andStorageTechnologiesFASTConference,April2004.
Emit(IntToString(value));
}
| [13] | RichardE.LadnerandMichaelJ.Fischer. |     |     |     |     | Parallelprefix |     |     |     |     |     |
| ---- | ----------------------------------- | --- | --- | --- | --- | -------------- | --- | --- | --- | --- | --- |
};
|     | computation. | JournaloftheACM,27(4):831–838,1980. |     |     |     |     |     |     |     |     |     |
| --- | ------------ | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
REGISTER_REDUCER(Adder);
| [14] | MichaelO.Rabin. |     | Efficientdispersalofinformationfor |     |     |     |     |     |     |     |     |
| ---- | --------------- | --- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
security, load balancing and fault tolerance. Journal of int main(int argc, char** argv) {
theACM,36(2):335–348,1989. ParseCommandLineFlags(argc, argv);
| [15] | Erik Riedel, | Christos    | Faloutsos, |                    | Garth A. | Gibson, and |                        |      |          |       |             |
| ---- | ------------ | ----------- | ---------- | ------------------ | -------- | ----------- | ---------------------- | ---- | -------- | ----- | ----------- |
|      |              |             |            |                    |          |             | MapReduceSpecification |      |          | spec; |             |
|      | DavidNagle.  | Activedisks |            | forlarge-scaledata |          | process-    |                        |      |          |       |             |
|      |              |             |            |                    |          |             | // Store               | list | of input | files | into "spec" |
ing. IEEEComputer,pages68–74,June2001.
|     |     |     |     |     |     |     | for (int | i = 1; | i < argc; | i++) | {   |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------ | --------- | ---- | --- |
[16] Douglas Thain, Todd Tannenbaum, and Miron Livny. MapReduceInput* input = spec.add_input();
Distributed computing in practice: The Condor experi- input->set_format("text");
ence. ConcurrencyandComputation: PracticeandEx- input->set_filepattern(argv[i]);
|     | perience,2004. |     |     |     |     |     | input->set_mapper_class("WordCounter"); |     |     |     |     |
| --- | -------------- | --- | --- | --- | --- | --- | --------------------------------------- | --- | --- | --- | --- |
}
[17] L.G.Valiant.Abridgingmodelforparallelcomputation.
CommunicationsoftheACM,33(8):103–111,1997.
|     |     |     |     |     |     |     | // Specify | the | output | files: |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ------ | ------ | --- |
// /gfs/test/freq-00000-of-00100
| [18] | Jim Wyllie. | Spsort: | How | to sort | a terabyte | quickly. |     |     |     |     |     |
| ---- | ----------- | ------- | --- | ------- | ---------- | -------- | --- | --- | --- | --- | --- |
// /gfs/test/freq-00001-of-00100
http://alme1.almaden.ibm.com/cs/spsort.pdf.
// ...
|     |     |     |     |     |     |     | MapReduceOutput* |     | out = | spec.output(); |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ----- | -------------- | --- |
out->set_filebase("/gfs/test/freq");
A WordFrequency
out->set_num_tasks(100);
out->set_format("text");
This sectioncontainsa programthat countsthenumber out->set_reducer_class("Adder");
ofoccurrencesofeachuniquewordinasetofinputfiles // Optional: do partial sums within map
specifiedonthecommandline. // tasks to save network bandwidth
out->set_combiner_class("Adder");
| #include | "mapreduce/mapreduce.h" |          |     |     |     |     |             |             |        |           |           |
| -------- | ----------------------- | -------- | --- | --- | --- | --- | ----------- | ----------- | ------ | --------- | --------- |
|          |                         |          |     |     |     |     | // Tuning   | parameters: |        | use at    | most 2000 |
|          |                         |          |     |     |     |     | // machines | and         | 100 MB | of memory | per task  |
| //       | User’s map              | function |     |     |     |     |             |             |        |           |           |
spec.set_machines(2000);
| class | WordCounter |     | : public | Mapper | {   |     |     |     |     |     |     |
| ----- | ----------- | --- | -------- | ------ | --- | --- | --- | --- | --- | --- | --- |
spec.set_map_megabytes(100);
public:
virtual void Map(const MapInput& input) { spec.set_reduce_megabytes(100);
|     | const string& |       | text         | = input.value();  |     |     |                      |          |           |          |          |
| --- | ------------- | ----- | ------------ | ----------------- | --- | --- | -------------------- | -------- | --------- | -------- | -------- |
|     |               |       |              |                   |     |     | // Now               | run it   |           |          |          |
|     | const int     | n =   | text.size(); |                   |     |     |                      |          |           |          |          |
|     |               |       |              |                   |     |     | MapReduceResult      |          | result;   |          |          |
|     | for (int      | i =   | 0; i <       | n; ) {            |     |     |                      |          |           |          |          |
|     |               |       |              |                   |     |     | if (!MapReduce(spec, |          | &result)) |          | abort(); |
|     | // Skip       | past  | leading      | whitespace        |     |     |                      |          |           |          |          |
|     | while         | ((i < | n) &&        | isspace(text[i])) |     |     |                      |          |           |          |          |
|     |               |       |              |                   |     |     | // Done:             | ’result’ | structure | contains | info     |
i++;
|     |           |       |       |                    |     |     | // about    | counters, | time | taken, | number of |
| --- | --------- | ----- | ----- | ------------------ | --- | --- | ----------- | --------- | ---- | ------ | --------- |
|     |           |       |       |                    |     |     | // machines | used,     | etc. |        |           |
|     | // Find   | word  | end   |                    |     |     |             |           |      |        |           |
|     | int start | =     | i;    |                    |     |     |             |           |      |        |           |
|     | while     | ((i < | n) && | !isspace(text[i])) |     |     | return      | 0;        |      |        |           |
}
i++;
USENIX Association OSDI ’04:6th Symposium on Operating Systems Design and Implementation 149