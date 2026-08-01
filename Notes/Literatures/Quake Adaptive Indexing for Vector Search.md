# Quake Adaptive Indexing for Vector Search

**Source**: Quake Adaptive Indexing for Vector Search.pdf
**Format**: .pdf

---

Quake: Adaptive Indexing for Vector Search
Jason Mohoney, Devesh Sarda, and Mengze Tang, University of Wisconsin–Madison;
Shihabur Rahman Chowdhury and Anil Pacaci, Apple;
Ihab F. Ilyas, University of Waterloo; Theodoros Rekatsinas, Apple;
Shivaram Venkataraman, University of Wisconsin–Madison
https://www.usenix.org/conference/osdi25/presentation/mohoney
This paper is included in the Proceedings of the 19th USENIX Symposium
on Operating Systems Design and Implementation.
July 7–9, 2025 • Boston, MA, USA
ISBN 978-1-939133-47-2
Open access to the Proceedings of the 19th USENIX Symposium
on Operating Systems Design and Implementation is sponsored by

|     |                               |                               | Quake:       | Adaptive            |     | Indexing                |                               | for Vector                    | Search               |     |            |     |     |
| --- | ----------------------------- | ----------------------------- | ------------ | ------------------- | --- | ----------------------- | ----------------------------- | ----------------------------- | -------------------- | --- | ---------- | --- | --- |
|     |                               |                               | JasonMohoney |                     |     |                         |                               |                               | DeveshSarda          |     |            |     |     |
|     |                               | UniversityofWisconsin-Madison |              |                     |     |                         | UniversityofWisconsin-Madison |                               |                      |     |            |     |     |
|     |                               | MengzeTang                    |              |                     |     | ShihaburRahmanChowdhury |                               |                               |                      |     | AnilPacaci |     |     |
|     | UniversityofWisconsin-Madison |                               |              |                     |     |                         |                               | Apple                         |                      |     | Apple      |     |     |
|     |                               | IhabF.Ilyas                   |              | TheodorosRekatsinas |     |                         |                               |                               | ShivaramVenkataraman |     |            |     |     |
|     | UniversityofWaterloo          |                               |              |                     |     | Apple                   |                               | UniversityofWisconsin-Madison |                      |     |            |     |     |
Abstract tice:graph-basedandpartitionedindexes,eachwithdistinct
performancecharacteristicsunderdynamicworkloads.
Vectorsearch,thetaskoffindingthek-nearestneighbors
ofaqueryvectoragainstadatabaseofhigh-dimensionalvec- Maintaininglowlatency,highrecallvectorsearchunder
dynamicandskewedworkloadsremainsasignificantchal-
tors,underpinsmanymachinelearningapplications,includ-
ingretrieval-augmentedgeneration,recommendationsystems, lengeforexistingindexes.Real-worldapplicationsoftenex-
hibitnon-uniformquerydistributionsandevolvingdata.For
| and | information | retrieval. | However, | existing | approximate |     |     |     |     |     |     |     |     |
| --- | ----------- | ---------- | -------- | -------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
example,inanexampleWikipediasearchapplication,popu-
nearestneighbor(ANN)methodsperformpoorlyunderdy-
namicandskewedworkloadswheredatadistributionsevolve. larpageslikeLionelMessiorLeBronJamesreceivedispro-
portionatelymorequeries,resultinginskewedreadpatterns.
WeintroduceQuake,anadaptiveindexingsystemthatmain-
tainslowlatencyandhighrecallinsuchenvironments.Quake Additionally,pagesarefrequentlyadded,updated,ordeleted,
|     |     |     |     |     |     |     | causingskewedupdatepatternsthatchangeovertime |     |     |     |     |     | [6]. |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | ---- |
employsamulti-levelpartitioningschemethatadjuststoup-
Thesefactorsdegradetheperformanceofexistingindexes,
datesandchangingaccesspatterns,guidedbyacostmodel
thatpredictsquerylatencybasedonpartitionsizesandaccess leadingtoincreasedquerylatencyandreducedrecall.
|              |     |            |             |            |           |     |     | Graph-based | indexes, such | as  | HNSW | [24], | DiskANN |
| ------------ | --- | ---------- | ----------- | ---------- | --------- | --- | --- | ----------- | ------------- | --- | ---- | ----- | ------- |
| frequencies. |     | Quake also | dynamically | sets query | execution |     |     |             |               |     |      |       |         |
parameterstomeetrecalltargetsusinganovelrecallestima- [38,39], and SVS [5] construct a proximity graph where
|     |     |     |     |     |     |     | each | node (vector) | is connected |     | to its approximate |     | neigh- |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------------- | ------------ | --- | ------------------ | --- | ------ |
tionmodel.Furthermore,QuakeutilizesNUMA-awareintra-
queryparallelismforimprovedmemorybandwidthutilization bors.Queriestraversethegraphtofindapproximatenearest
duringsearch. ToevaluateQuake,weprepareaWikipedia neighbors,typicallyachievinghighrecallwithlowlatency.
However,theseindexesfacechallengeswithdynamicwork-
| vector | search | workload | and develop | a workload | generator |     |     |     |     |     |     |     |     |
| ------ | ------ | -------- | ----------- | ---------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
tocreatevectorsearchworkloadswithconfigurableaccess loadsbecauseupdatingthegraphstructuretoaccommodate
|     |     |     |     |     |     |     | frequent | insertions | and deletions |     | is computationally |     | inten- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ------------- | --- | ------------------ | --- | ------ |
patterns.Ourevaluationshowsthatondynamicworkloads,
Quakeachievesquerylatencyreductionsof1.5–38×andup- sive[45],duetotherandomaccesspatternsinvolvedingraph
datelatencyreductionsof4.5–126×comparedtostate-of-the- traversalandmodification.
artindexessuchasSVS,DiskANN,HNSW,andSCANN. Partitioned indexes, such as SCANN [10,40], SPANN
[7,45],andFaiss-IVF[8],partitionthevectorsusingaclus-
1 Introduction
|     |     |     |     |     |     |     | tering | algorithm | (e.g k-means). | Queries |     | are processed | by  |
| --- | --- | --- | --- | --- | --- | --- | ------ | --------- | -------------- | ------- | --- | ------------- | --- |
Vector search, the task of finding the k-nearest neighbors scanningasubsetofpartitions,balancingrecallandlatency
(KNN) of a query vector against a database of high- by adjusting the number of partitions scanned (denoted as
nprobe).Whileattractiveduetotheirsimplicity,partitioned
dimensionalvectors,isfundamentaltomodernmachinelearn-
ing based search [9,11,12,36] and recommendation sys- indexesfaceasignificantsearchlatencygapwhencompared
tems[21,22,32,33,43].Intheseapplications,avectorrep- withgraphindexes. Forexample,on the MSTURING10M
resentsaniteminametricspace,andthedistancebetween benchmark[2],wefoundFaiss-IVFtakes44mspersearch
vectorsreflectssemanticsimilarity.However,performingex- query while Faiss-HNSW takes only 6.8ms. On the other
actKNNsearchbecomescomputationallyinfeasibleonlarge hand,supporting updates in partitioned indexes is less ex-
datasetsduetothehighdimensionalityandvolumeofdata. pensivethanforgraphindexes,astheindexstructureneeds
To address this challenge,practitioners use approximate minimalmodificationwhenaddingorremovingvectors.But,
nearestneighbor(ANN)indexes,whichtradeoffacontrolled existingapproachesstrugglewithdynamicandskewedwork-
amountofsearchaccuracy(recall)forsignificantreductions loadsbecausetheydonotadapttochangingaccesspatterns,
inlatency.Amongthese,twobroadclassesdominateinprac- leadingtoimbalancedpartitionsthatdegradequerylatency.
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    153

Recentworkhasbeenproposedtoresolveimbalancesindy- lowerquerylatencycomparedtosingle-threadedandnon-
namic workloads by splitting and reclustering imbalanced NUMAawareconfigurations,respectively.
partitions[6,45],however,wefindthesemethodsdegradere-
2 MotivationandChallenges
callasnprobeneedstochangeastheindexstructurechanges.
Inthiswork,westudytheproblemofminimizingquery Efficientvectorsearchiscriticalforlarge-scalesystemsused
latencytomeetafixedrecalltargetfordynamicvectorsearch in recommendation, semantic search, and information re-
workloads,whereboththequeriesandthebasevectorscan trieval. These applications demand the ability to process a
change over time. To address this problem, we develop high volume of nearest neighbor queries with low latency,
Quake,apartitionedindexforANNsearchthatminimizes evenastheunderlyingdataevolves.Tomeettheserequire-
querylatencybyadaptingtheindexstructuretotheworkload. ments,vectordatabases—suchasMilvus[42],Pinecone[3],
Quake’stwoprimaryalgorithmiccontributionsare: AnalyticDB-V [44],VBASE [47],and Qdrant [1]—utilize
First,Quakeemploysanadaptivehierarchicalpartition- specializedvectorindexes(e.g.,Faiss-IVF,HNSW,Vamana)
ingschemethatmodifiesthepartitioningbyminimizingthe thatsupportfastapproximatenearestneighbor(ANN)queries.
cost(derivedfromaproposedcostmodel)ofaquery.The However,servingthesedynamicworkloadsintroducessig-
costmodeltrackspartitionsizesandaccessfrequenciesasthe nificant challenges in maintaining query performance and
workloadisprocessedanddetermineswhichpartitionsare accuracyasdataandquerypatternsshiftovertime.
mostnegativelycontributingtooverallquerylatency.Once
2.1 VectorSearchWorkload
identified, we split or merge these partitions based on ex-
pectedcostreductionderivedfromourproposedcostmodel. Avectorsearchworkloadisacontinuous,evolvingstreamof
Wealsodemonstratethatourmaintenanceprocedureisstable queriesandupdates:
andconvergestoalocalminimumofthecostmodel. • Queries:Givenaqueryvectorq,thegoalistofindthetop-k
Second,wedesignanadaptivepartitionscanningscheme nearestneighborsinasetX.Exactlinearsearchistooslow
that adjusts the number of partitions scanned on-the-fly to forlarge,high-dimensionaldatasets,soANNindexesare
meetrecalltargetsforindividualqueries.Wedothisbymain- used. Theseindexesapproximatenearestneighborswith
tainingarecallestimateduringqueryprocessingbasedonA) controlledrecalltolowerlatencybyordersofmagnitude.
thegeometryofthepartitioningandB)intermediateresults • Updates:Thedatasetevolvesovertime.Insertionsaddnew
ofthequery,andoncetheestimateexceedstherecalltarget, vectorsrepresentingfreshcontent(e.g.,newproducts,trend-
queryprocessingterminatesandtheresultsarereturned. ingnewsarticles),anddeletionsremoveoutdatedentries.
Furthermore,QuakeutilizesNUMA-awareparallelismto Typically,updatesareappliedinabatchedfashion.
maximizememorybandwidthusageonmulti-coremachines. Recall@kisthestandardmetricforaccuracy,definedas:
Itisasignificantchallengetoevaluateindexingapproaches |G∩R| where R is the vectors returned by the approximate
k
duetothelackofavailabilityofbenchmarksforonlinevector
search,andGisthegroundtruthset.Maintainingaconsistent
search.Toaddressthischallengeandcomprehensivelyevalu-
recalltarget(e.g.,>90%)andlowlatency(e.g.,milliseconds
ateourapproach,weA)prepareaWikipediavectorsearch
perquery)asbothdataandquerypatternsshiftisakeychal-
workloadderivedfrompubliclyavailablequeryandupdate
lenge.Thecomplexityoftheseworkloadsstemsfromtheir
patternsofWikipediapagesandB)developaworkloadgen-
inherentlydynamicandskewednature,whichfewexisting
eratorforcreatingworkloadswithconfigurablequeryand
indexingmethodshandlegracefully.
updatepatterns.WewillpubliclyreleasetheWikipediawork-
2.2 WhyReal-WorldWorkloadsareHard
loadandworkloadgeneratorasevaluationtoolsforthecom-
munitytouse.Usingthese,weconductacomprehensiveeval- SkewedReadPatterns Inpractice,userqueriesconcentrate
uationofQuakeincomparisontosevenbaselineapproaches. onpopularitems.Forexample,queriesagainstaWikipedia-
1. Quakeachievesthelowestsearchtimeacrossalldynamic deriveddatasettendtofocusonasmallsubsetofentitiesat
workloadscomparedtostate-of-the-artgraphindexes,with anygiventime.Asaresult,certainpartitionsorgraphregions
1.5-13×lowersearchlatencythanHNSW,DiskANN,and oftheindexareaccesseddisproportionatelyoften.
SVSwhilehaving18-126×lowerupdatelatency. Skewed Write Patterns Insertions and deletions are also
rarelyuniform.Newdataoftenarrivesinbursts—e.g.,new
2. We also find that APS matches the nprobe of an oracle
Wikipedia pages added monthly, new products introduced
acrossrecalltargetsonSIFT1M,withonlya17-29%in-
aheadofashoppingseason,ornewlyrelevantembeddings
creaseinlatencyrelativetotheoracle.
generatedbycontinuouslyupdatedlanguagemodels.
3. APSperformson-parorbetterthanexistingearlytermina-
Real-WorldExample:Wikipedia-12M Inourevaluation,
tionmethods[7,18,48]andrequiresnoofflinetuning.
wepreparedWIKIPEDIA-12M,aworkloadbasedonasubset
4. Quake’sNUMA-awarequeryprocessingexhibitslinear ofWikipediaarticlesderivedfrompubliclyavailablemonthly
scalabilityandhighmemorybandwidthutilizationonthe pageviewstatistics[4].Over103months,thedatasetgrows
MSTURING100Mdataset.Quakeachieves20×and4× frommillionstotensofmillionsofvectors.Populararticles
154 19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

topreservegraphconnectivityandproximityproperties.Our
evaluation(Table1)showsthatupdatelatencycanbemultiple
ordersofmagnitudehigherthanpartitionedindexes.
Partitioned Indexes Partitioned indexes such as Faiss-
IVF[8],SCANN[10,40],andSpFresh[45]dividethevector
spaceintodisjointpartitionsusingaclusteringalgorithmsuch
ask-means.Queriesareprocessedbyscanningasubsetofpar-
titionstoretrieveapproximatenearestneighbors.Partitioned
indexesaremoreupdate-friendlythangraph-basedmethod
sinceinsertionsanddeletionsleadstosequentialaccess.For
(a)Read(top)andwriteskew. (b)Queryperformance. writeskewedworkloadssomepartitionsbecomesignificantly
larger,degradingquerylatency,thiscanbeexacerbatedby
Figure1:SkewedaccesspatternsofFaiss-IVFindexpartitions
readskewiflargepartitionsarealsomorefrequentlyaccessed
intheWIKIPEDIA-12Mworkloadandtheireffectonquery
("hot partitions"). Query processing is memory-bound, as
performanceforFaiss-IVFandSCANN
achievinghighrecallrequiresscanningmanymegabytesof
dataacrossmultiplepartitions,forexamplereachingarecall
Table 1: Comparison ofupdatable vectorindexes. Tuning:
targetof90%ontheMSTURING100Mdatasetrequireseach
Requiresmanualparametertuninginindexing/queryprocess-
query to scan 1GB of vectors. Moreover,most partitioned
ing.Maintenance:Modifiesindexwithincrementalupdates.
indexesuseafixednumberofpartitionstoprobe(nprobe),
Adaptive:Usesqueryinformationtoinformindexing.
whichdoesnotadapttochangingdatadistributionsorquery
patterns,leadingtoeitherinsufficientrecallorexcessivedata
Method Tuning Maint. Adaptive scanning.Thechallengesyieldsubparperformanceforpar-
Quake(Ours) ✗ ✓ ✓ titionedindexesonreal-worldworkloads.Forexample,Fig-
Faiss-IVF[8] ✓ ✗ ✗ ure1bshowsthedegradationoflatencyandrecallovertime
DeDrift[6] ✓ ✓ ✗ whenusingFaiss-IVFandSCANNwithafixednprobeon
SpFresh[45] ✓ ✓ ✗ WIKIPEDIA-12M(workloaddetailsinSection7).
SCANN[10,40] ✓ ✓ ✗ EarlyTermination Early-terminationmethodshavebeen
DiskANN[31,38] ✓ ✓ ✗
proposed to reduce query latency or meet recall targets in
Faiss-HNSW[24] ✓ ✗ ✗
partitionedindexesbydynamicallyadjustingthenumberof
SVS[5] ✓ ✓ ✗
partitionsscannedperquery.SPANN[7]appliesasimplerule:
itprunespartitionsoncethecentroiddistanceexceedsauser-
tunedthresholdrelativetotheclosestcentroid.LAET[18]isa
dominatequerytraffic,whileembeddingsofnewlycreated
learning-basedapproachthatpredictstherequirednprobeper
pagesaccumulateincertainregionsoftheembeddingspace.
queryusingatrainedmodel,butstillrequiresdataset-specific
Thisworkloadshowsreadskewandwriteskew,asevidenced
training and calibration foreach recall target. Auncel [48]
byFigure1a,readsandwritespredominantlyaffectasmall
usesageometricmodeltoestimatewhenrecallforagiven
portionoftheindex.
query,settingnprobeperquery,butitsconservativeestima-
2.3 ShortcomingsofExistingApproaches tionleadstosubstantialovershootingoftherecalltarget(See
Figure13in[48]).Allthreemethodsrequiretuningorcali-
Existingindexeswereoftendevelopedandevaluatedunder
brationanddonotadapttochangesintheindexstructureor
assumptionsofstaticdatadistributions;conditionsnotmet
datadistribution.
in real-worlduse cases. Table 1 compares a range ofstate-
of-the-artvectorindexes.Althoughwidelyadoptedinvector 2.4 TechnicalChallengesforPartitionedIndexes
databases,nonefullysolvetheproblemofmaintaininglow-
The following technicalchallenges are yetto be solvedby
latency,high-recallsearchunderdynamic,skewedworkloads
existingpartitionedindexes
withoutconstantmanualinterventionorofflinetuning.
Graph Indexes Graph-based index systems, such as 1. Adaptation to Queries Query adaptivity is overlooked
HNSW [24],DiskANN [31,38],and SVS [5] construct a byexistingpartitionedindexapproachesandexhibitsan
proximity graph where each node represents a vector con- opportunityforoptimization,particularlyformaintaining
nectedtoitsapproximateneighbors.Theseindexesachieve hotpartitionsinducedbyreadskew.
highrecallwithlowlatencyinstaticsettingsbyefficiently 2. OnlineAdjustmentofNprobeAstheindexstructureand
traversingthegraphtolocatenearestneighborsusingapro- datachange,partitionedindexesneedtoadjustthenumber
cess known as greedy traversal. However,maintaining the ofpartitionsscannedorrecallwillsuffer.Existingearly
graphstructureunderfrequentupdatesiscomputationallyin- terminationworksareinsufficientastheyassumeastatic
tensive,aseachupdatemayrequirerewiringmultipleedges indexandrequireretuningastheindexanddatachange.
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation 155

3. Performance Gap with Graph Indexes Standard par- bedeletedandthevectorisremovedfromthepartitionwith
titioned indexes such as Faiss-IVF are memory bound, immediatecompaction.AsdemonstratedinSection2,modi-
andexhibitanorderofmagnitudehigherquerylatencyin ficationscannegativelyaffectindexperformanceovertime,
comparisonthangraphindexes. requiringmaintenance(Figure1b).Quakeusesthefollowing
Quakeisoursolutiontothesetechnicalchallenges.Quake maintenanceactionsinordertominimizequerylatency:
A)adaptstheindexstructuretoqueriesbyutilizingmainte- 1. SplitPartition:Usesk-meansclusteringtosplitaparti-
nancethatminimizesacostmodelforquerylatency,B)using
tionintotwo,removingtheoldpartitionanditscentroid
arecallestimationmodel,Quakeindividuallysetsnprobefor andaddingtwonewpartitionsandcentroids.Tomitigate
queriestomeetrecalltargetsastheindexstructurechanges, potentialoverlapduetothenewpartitions,weperformad-
| and C) uses | NUMA-aware | parallelism | in orderto | saturate |     |     |     |     |     |     |
| ----------- | ---------- | ----------- | ---------- | -------- | --- | --- | --- | --- | --- | --- |
ditionaliterationsofk-meansclusteringoverthepartitions
memorybandwidthduringqueryprocessing,closingtheper- neighboringthesplitpartitions(bycentroiddistance).
| formance | gap with graph | indexes. | We next briefly | discuss |          |            |         |             |         |           |
| -------- | -------------- | -------- | --------------- | ------- | -------- | ---------- | ------- | ----------- | ------- | --------- |
|          |                |          |                 |         | 2. Merge | Partition: | Removes | a partition | and its | centroid, |
otherrelatedworkbeforecoveringQuakeindetail.
|                    |     |     |     |     | reassigning                    |     | the vectors | of the | removed partition | to the |
| ------------------ | --- | --- | --- | --- | ------------------------------ | --- | ----------- | ------ | ----------------- | ------ |
| 3 SolutionOverview |     |     |     |     | remainingpartitionsintheindex. |     |             |        |                   |        |
3. AddLevel:Addsalevelofpartitioningtotheindexby
A. Select  partitioningthecurrenttop-levelusingk-meansclustering.
| Adaptive  | Partitions to  |     | Quake  B. Update  |       |     |     |     |     |     |     |
| --------- | -------------- | --- | ----------------- | ----- | --- | --- | --- | --- | --- | --- |
|           |                |     | I n d             | e x   |     |     |     |     |     |     |
Partition  Scan Metadata  4. RemoveLevel:Removescurrenttop-levelandmergesthe
|           |     |     | M e ta | d a t a |                           |     |     |     |     |     |
| --------- | --- | --- | ------ | ------- | ------------------------- | --- | --- | --- | --- | --- |
| Selection |     |     |        | Table   | partitionsinthenextlevel. |     |     |     |     |     |
C. Estimate
|     |     |     |     |     | Quake | uses | a costmodelthatestimates |     | querylatencyto |     |
| --- | --- | --- | --- | --- | ----- | ---- | ------------------------ | --- | -------------- | --- |
Cost Model
determineifmaintenanceactionsshouldbetakenandwhich
D. Modify Index
|          |         |     |     | Index       | partitions   | to apply | them     | to. The   | cost model is | a function |
| -------- | ------- | --- | --- | ----------- | ------------ | -------- | -------- | --------- | ------------- | ---------- |
|          |         |     |     | Maintenance | of partition | access   | patterns | and sizes | to determine  | which      |
| Searches | Updates |     |     |             |              |          |          |           |               |            |
partitionsarecontributingmosttotheoverallquerylatency.
Figure2:QuakeArchitectureDiagram.Searchqueriesuse Wecheckformaintenanceaftereachoperationbyevaluating
thecostmodel,butthemaintenancefrequencyisconfigurable.
AdaptivePartitionSelection(APS)todeterminewhichparti-
tionstoscan(A).Scanningpartitionsmodifiesaccesspatterns Partitionswiththelargestcostcontributionareconsideredfor
splitordeletion.Intuitively,frequentlyaccessedand/orlarge
oftheindex,trackedinthemetadatatable(B).Acostmodel
isusedtodeterminewhichmaintenanceactionstotake(C) partitions are split and infrequently accessed and/or small
wherethechosenmaintenanceactionsmodifytheindex(D). partitionsaremergedastheydonotjustifytheoverheadof
maintainingacentroid.SeeSection4fordetailsonthecost
Thisprocessoperatesinacontinuousonlinefashionassearch
andupdatequeries(inserts/deletes)areissuedtotheindex. modelandmaintenancemethodology.
|     |     |     |     |     | AdaptivePartitionScanning |     |     | Inordertodeterminethenum- |     |     |
| --- | --- | --- | --- | --- | ------------------------- | --- | --- | ------------------------- | --- | --- |
Index Structure Quake organizes the vectors in a multi- berofpartitionsasearchqueryshouldscantoreachagiven
levelindex,whereeachlevelisapartitionedindexsimilarto recall target,we apply Adaptive Partition Scanning (APS)
Faiss-IVF[8].Thelowestlevelintheindexisconstructedby ateachleveloftheindex.APSsolvesacriticalproblemfor
organizingthevectorsintodisjointpartitions(usingk-means partitionedindexeswhenappliedtodynamicworkloads:as
clustering)whereeachpartitionhasarepresentativecentroid. thenumberandcontentsofpartitionschange,thenumberof
Thesecentroidscanbefurtherpartitionedinasimilarmanner partitionsscannedneedstochange,otherwiserecallwillde-
tocreateadditionallevelsintheindex.Searchqueriesscan grade(Figure1b).APSmaintainsarecallestimatorbasedon
theindexinatop-downfashion,findingthenearestcentroids theintermediatetop-kresultsofthequeryandthegeometry
ateachleveltodeterminethepartitionstoscaninthenext ofneighboringpartitions.Asmorepartitionsarescanned,the
level.Partitionsinthelowestlevelcontaintheactualvectors intermediateresultsandrecallmodelareupdatedandwhen
and subsets of these partitions are scanned to return the k- the recallestimate exceeds the targetrecall,the results are
nearestneighbors.Utilizingamulti-leveldesignenablesus returned.Tomitigateoverheadsintroducedbytheestimator,
toemployfine-grainedpartitioningofvectorsatlargescale we use pre-computation of expensive geometric functions
(showntoimprovesearchquality[7]),whilemitigatingthe andonlyupdatetheestimatewhentheintermediateresults
highcostofscanningcentroids. havechangedsignificantly.APSsupportsbothEuclideanand
Adaptive Incremental Maintenance Inserts and deletes inner-productdistancemetrics.WecoverAPSinSection5.
modifytheQuakedatastructurebyappendingvectorstoand NUMA-Aware Query Processing Modern multi-core
removingvectorsfromindexpartitions.Insertionstraverse servers often use Non-Uniform Memory Access (NUMA)
theindexstructuretop-downtofindthenearestpartitioninthe architectures,wherememoryclosetoaprocessor’slocalnode
lowestleveltotheinsertedvectorandappendtothatpartition. isfastertoaccessthanremotememory. Quakeisdesigned
Deletesuseamaptofindthepartitioncontainingthevectorto to capitalize on this heterogeneous memory. It distributes
156    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

indexpartitionsacrossNUMAnodes.Tominimizeremote of scanning centroids. The model furthercaptures that fre-
memory access,Quake employs affinity-based scheduling, quentlyaccessedpartitionsdominatethetotalcost,motivating
andsupportsworkstealingwithinaNUMAnodetomitigate targetedmaintenanceactionstobalancethesetrade-offs.
workloadimbalances.Byco-locatingcomputationwiththe GuidingMaintenanceDecisions Maintenanceactionssuch
relevantdata,Quakereducesremotememoryaccesses,satu- assplittingordeletingaimtoreducethetotalcostC.Each
ratesmemorybandwidth,andthuslowersquerylatency.See actionisevaluatedbasedonitspredictedchangeincost:
Section6fordetailsonQuake’sNUMA-awareoptimizations.
∆C=C −C (3)
4 AdaptiveIncrementalMaintenance after before
Wepresentouradaptivemaintenancemethodology,beginning whereC before andC after are the total costs before and after
withacostmodelthatestimateseachpartition’scontribution theaction,respectively.Actionsareappliedonlyif∆C<−τ,
toquerylatencyandguidesmaintenancedecisions.Next,we whereτisanon-negativetunablethreshold,ensuringmono-
describetheavailablemaintenanceactions,analyzingtheir tonic improvement in query performance. By focusing on
impactonthecostmodel.Wethendetailthemulti-stagedeci- reducingC,theindexisdynamicallyrestructuredtomaintain
sionworkflowthatprioritizesbeneficialactionsandconclude efficientqueryperformanceundervaryingworkloads.
withaconcreteexample. 4.2 ConductingMaintenance
4.1 CostModel Maintenance at each level of the index proceeds in three
The costmodelestimates the query latency contributedby phases—estimate,verify,and commit / reject. We first list
eachpartition,intheindex. Estimatingtheper-partitionla- theavailableactions,thenderivetheircostdeltas,describe
tencycontributionenablestargetedmaintenancetotheparti- theworkflow,andfinallywalkthroughaconcreteexample.
tionsmostaffectingqueryperformance.
4.2.1 MaintenanceActions
PartitionProperties ConsideranindexwithLlevels,num-
Tominimizequerylatency,Quakeemploysaseriesofmain-
beredl=0,1,...,L−1.Levell containsN partitions.The
l
tenanceactionsthatdynamicallyadjusttheindexstructure
baselevelcorrespondstol=0andcontainspartitionsofthe
inresponsetoevolvingworkloads.Herewedefinethemain-
originaldatasetvectors. Higherlevelscontainpartitionsof
tenanceactionsandthenanalyzetheimpactofeachmainte-
centroid vectors that summarize the partitions in the level
nanceactionontheoverallcostmodel.
below.Atthetoplevel,l=L−1,thereisasinglepartition
SplitPartition Ifapartition(l,j)istoolargeorfrequently
containingtop-levelcentroids.
accessed,we considersplitting it into two partitions (l,j )
Each partition j at level l has a size s (the number of L
lj
and(l,j ).Weapplyk-meansclusteringwithinthatpartition,
vectorsitcontains)andanaccessfrequencyA ∈[0.0,1.0]. R
l,j
formingtwosmallerpartitionswiththeirowncentroids.The
A denotes the fraction of queries, measured in a sliding
l,j
originalpartitionisremovedanditsvectorsarereassigned.
windowW,thatscanthepartition jatlevell.Thecostmodel
Asubsequentpartitionrefinementstepadjustsvectorassign-
isprimarilydrivenbythesesizesandaccessfrequencies.
mentstoensureminimaloverlapandbalancedpartitionsizes.
PartitionCost Apartition(l,j)contributeslatencypropor-
PartitionRefinement Afterasplit,refinementusesk-means
tionaltoitssizeandhowfrequentlyitisaccessed.Letλ(s)
(seededbycurrentcentroids)onnearbypartitionstomitigate
bethelatencyfunctionforscanningsvectors.Wemeasure
overlap and ensure that each vectoris assigned to its most
λ(s)throughofflineprofiling.Thecostofpartition(l,j)is:
representativepartition.Nearbypartitionsaredeterminedby
C lj =A lj ·λ(s lj ) (1) findingther f nearestcentroidstothesplitcentroids,where
r is a tunable parameter (typically between 10 and 100).
f
TotalCost Theoverallquerylatency(cost)estimateisthe Thisisageneralizationofthereassignmentprocedureusedin
sumacrossalllevelsandpartitions SpFresh/LIRE[45],usingadditionalroundsofk-meansprior
toreassignment,andhasbeenappliedsuccessfullybyrecent
L−1Nl−1
indexmaintenanceworks[23]and[25].Refinementavoids
C= ∑ ∑ A ·λ(s ) (2)
lj lj performancedegradationbymitigatingoverlapandensuring
l=0 j=0
vectorsareassignedtotheirmostrepresentativepartition.
Interpretation Thecostmodelreflectstherelationshipbe- MergePartition Ifapartitionisrarelyaccessedandbelowa
tweenpartitionsize,accessfrequency,andquerylatency.The minimumsizethreshold,weconsiderdeletingittoremove
fundamentaltrade-offthatneedstobebalancedisthenumber thecostofmaintainingitscentroid.Afterdeletion,thevectors
and size of partitions. Larger partitions require more time arereassignedtotheirrespectivenearestexistingpartitions.
toscan,increasinglatency,butreducingthetotalnumberof Thiscanreducetotalcostbyremovingalow-benefitpartition,
partitionsandtheoverheadofscanningcentroids.Conversely, althoughthe reassignmentmay increase the size (andthus
smaller,fine-grainedpartitionsreducethenumberofvectors cost)ofotherpartitions,andthereforecarefulconsideration
neededtoscantoreachahighrecallbutincreasetheoverhead isneededbeforeconductingamerge.
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation 157

| AddingandRemovingLevels |     |     |     | Ifthenumberofcentroids |     |     |     |         |     |        |     |     |     |
| ----------------------- | --- | --- | --- | ---------------------- | --- | --- | --- | ------- | --- | ------ | --- | --- | --- |
|                         |     |     |     |                        |     |     |     | ∆′Split |     | =∆O+−A |     |     |     |
inthetoplevelgrowsbeyondathreshold,weaddanewtop l,j λ(s l,j )
|     |     |     |     |     |     |     |     |     | l,j |     |     |     | (6) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:0)sl,j(cid:1)
levelbyclusteringthosecentroids.Conversely,ifthetoplevel +2αA λ .
|     |     |     |     |     |     |     |     |     |     |     | l,j | 2   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
becomestoosparse(belowaconfiguredlowerthreshold),we
removethetoplevelandmergeitscentroidsinthelevelbelow. andtheanalogousmergeestimate,derivedwithauniform
redistributionassumption,islocatedinthetechnicalreport
| Both actions               | help | maintain | hierarchy                 | balance | and | control |                   |     |       |             |        |     |             |
| -------------------------- | ---- | -------- | ------------------------- | ------- | --- | ------- | ----------------- | --- | ----- | ----------- | ------ | --- | ----------- |
|                            |      |          |                           |         |     |         | [27]. Immediately |     | after | a tentative | action | we  | measure the |
| centroid-scanningoverhead. |      |          | Wedeferdiscussionofthisto |         |     |         |                   |     |       |             |        |     |             |
actualsizes(and,formerges,theexactreceivingpartitions)
ourtechnicalreport[27].
andre-evaluateEqs.(4)or(5).Iftherecomputedgainisstill
4.2.2 CostDeltas below−τtheactioniscommitted;otherwiseitisrolledback
|     |     |     |     |     |     |     | (§4.2.3). This | “estimate-then-verify” |     |     | strategyis |     | crucialfor |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ---------------------- | --- | --- | ---------- | --- | ---------- |
Themaintenancelooptreatseverycandidateactionasapro-
ensuringmonotoniccostimprovement.
posededittotheindexandscoresitbythechangeitwould
| induceinthetotalcost(Eq.(3)). |     |     |     |     |     |     | 4.2.3 DecisionWorkflow |     |     |     |     |     |     |
| ----------------------------- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- |
Wetentativelyacceptanactionwhenever∆C<−τ.Below Maintenance is a bottom-up pass over the hierarchy. Each
wegivetheexact∆Cformulasfortheprimarymaintenance level executes the five stages below starting from the base
actions:splitandmerge.Fullderivationsareinthetechnical
|     |     |     |     |     |     |     | level. This | workflow | is  | triggered | by the | user. | An avenue |
| --- | --- | --- | --- | --- | --- | --- | ----------- | -------- | --- | --------- | ------ | ----- | --------- |
report[27];hereweshowonlythefinalexpressions. forfutureworkistodevelopschedulingpoliciestocallthis
ExactSplitDelta Splittingahotoroversizedpartition(l,j) workflow and limitits scope. In ourevaluation,we trigger
intochildren(l,j L )and(l,j R )insertsonenewcentroidatthe maintenanceafterasetamountofquerieshavebeenrun.
parentlevel,changingtheoverheadby∆O+=λ(N +1)− Stage 0: Track Statistics At the end of each query batch
l
λ(N).Theresultingcostdifferenceis l we update,foreverypartition (l,j): (i) size s l,j ,(ii) access
|     |     |     |     |     |     |     | count overthe | sliding | window |     | of queriesW,giving |     | A = |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ------- | ------ | --- | ------------------ | --- | --- |
l,j
|     |        |     | ∆O+ |        |     |     | hits(l,j)/|W|.Thesevaluesareinputsofthecostmodel. |     |     |     |     |     |     |
| --- | ------ | --- | --- | ------ | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|     | ∆Split | =   |     | −A λ(s | )   |     |                                                   |     |     |     |     |     |     |
|     | l,j    |     |     | l,j    | l,j |     |                                                   |     |     |     |     |     |     |
(cid:124)(cid:123)(cid:122)(cid:125) Stage1:Estimate Forthecurrentlevell computetheesti-
|     |     | newcentroid |     |     |     | (4) |     |     |     |     |     |     |     |
| --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
mate∆′(§4.2.2)ofsplittinganddeletingforeverypartition.
|     |     | +A  | λ(s  | )+A  | λ(s       | )   |                                     |        |             |     |                  |     |             |
| --- | --- | --- | ---- | ---- | --------- | --- | ----------------------------------- | ------ | ----------- | --- | ---------------- | --- | ----------- |
|     |     |     | l,jL | l,jL | l,jR l,jR |     | Tentativelyapplyanyactionwith∆′<−τ. |        |             |     |                  |     |             |
|     |     |     |      |      |           |     | Stage 2:                            | Verify | Immediately |     | after performing |     | a tentative |
wherethefirsttermpaysfortheextracentroid,thesecond
action,wemeasuretheactualresultingpartitionsizes(and
removestheoldscancost,andthelasttwoaddthecostsof
theexactreceiverpartitionsformerges).Werecomputethe
| scanning | the new, | smaller | partitions. | Note | that | we do not |            |             |       |     |            |        |              |
| -------- | -------- | ------- | ----------- | ---- | ---- | --------- | ---------- | ----------- | ----- | --- | ---------- | ------ | ------------ |
|          |          |         |             |      |      |           | cost delta | using these | known |     | values but | retain | the original |
explicitlymodeltheeffectofrefinement,asrefinementdoes
frequencyassumptionsfromStage1.
| notchangethenumberofpartitions. |     |     |     | Itsimpactiscaptured |     |     |     |     |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Stage3:Commit/Reject
automaticallyasstatisticsarecollectedfromfuturequeries,
soweomititfromthe∆-formulaandletlatermaintenance
|     |     |     |     |     |     |     | ∆<−τ |     | → commit, |     | ∆≥−τ | → reject. |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- | --------- | --- | ---- | --------- | --- |
iterationsadjustifnecessary.
ExactMergeDelta Deletingacold,tinypartition(l,j)re- Rejectiondiscardstheactionandkeepsthepreviousstateof
movesacentroid(∆O−=λ(N
l −1)−λ(N))andredistributes l thepartition(s),inordertopreventcostincreases.
itsvectorstoareceiversetR .Let∆s and∆A bethere- Stage4:PropagateUpward. RepeatStages1-3onthenext
|                                                   |     |     | l,j | m   |     | m   |           |     |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- |
| sultingsizeandfrequencybumpsforeachreceiverm.Then |     |     |     |     |     |     | levell+1, |     |     |     |     |     |     |
Safety:Becauseeverylevelenforcesthesame∆<−τguard,
totalcostacrossalllevelsmonotonicallydecreasesandthe
| ∆Merge | =∆O−−A |     | λ(s | )   |     |     |     |     |     |     |     |     |     |
| ------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
l,j l,j l,j hierarchyconvergestoastablestateunderafixedworkload
|     |     | (cid:2) |     |     |     | (cid:3) |     |     |     |     |     |     |     |
| --- | --- | ------- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
+ ∑ (A m +∆A m )λ(s m +∆s m )−A m λ(s m ) distribution(proofintechnicalreport[27]).
m∈Rl,j
4.2.4 ExampleMaintenanceWorkflow
(5)
|     |     |     |     |     |     |     | Belowwe | walkthroughthe |     | estimate | →   | verify→ | commit/ |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------------- | --- | -------- | --- | ------- | ------- |
capturesboththebenefitofdeletingthepartitionandthe
rejectloopfortwoexamplepartitionsandshowhowanim-
penaltyofswellingitsneighbors.
balancedsplitisautomaticallyrejectedtopreventaccidental
| EstimatingDeltas |     | Atdecisiontimewedonotyetknowthe |     |     |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | ------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
costincreases.
| post-actionquantities{s |             |               | ,A     | ,...}orthetrue∆s |       | ,∆A .      |                  |                 |            |             |           |       |                |
| ----------------------- | ----------- | ------------- | ------ | ---------------- | ----- | ---------- | ---------------- | --------------- | ---------- | ----------- | --------- | ----- | -------------- |
|                         |             |               | l,jL   | l,jL             |       | m m        |                  |                 |            |             |           |       |                |
|                         |             |               |        |                  |       |            | Set-up: Consider |                 | partitions | P           | 1 and P 2 | with  | identical size |
| We therefore            | use         | a lightweight |        | estimate         | based | on two as- |                  |                 |            |             |           |       |                |
|                         |             |               |        |                  |       | sl,j,      | andaccess        | frequency,where |            | bothcontain |           | s=500 | vectors        |
| sumptions:              | 1) Balanced |               | Split: | s ≈s             | ≈     | and 2)     |                  |                 |            |             |           |       |                |
l,jL l,jR 2 and appear in A=0.10 of queries. From profiling we ob-
Proportional-AccessScaling:eachchildinheritsafixedfrac-
|     |     |     |     |     |     |     | servenon-linear1 |     | scanlatenciesforthefollowingpartition |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------------------------------------- | --- | --- | --- | --- |
tionαoftheparent’sfrequency.
Undertheseassumptionsthesplitestimatebecomes 1Scanlatencyisnon-linearw.r.t.sizeduetotop-ksortingoverhead.
158    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

sizes: λ(50) = 250µs, λ(250) = 550µs, λ(450) = 1050µs, eachpartitionasasinglehalf-space,definedbytheperpen-
λ(500)=1200µsAddingacentroidcosts∆O+=60µs.We dicularbisectorbetweenthequery’snearestcentroidc and
0
useadecisionthresholdofτ=4µsandα=.5 eachneighboring centroidc. i This simplification results in
|             |           |                             |     |     | ahypersphericalcapwhosevolumev                         |     | hasaclosed-formex- |     |
| ----------- | --------- | --------------------------- | --- | --- | ------------------------------------------------------ | --- | ------------------ | --- |
| 1. Estimate | ForP andP | theestimateassumesabalanced |     |     |                                                        |     | i                  |     |
|             | 1         | 2                           |     |     | pressionviatheregularizedincompletebetafunction[16,19] |     |                    |     |
250/250splitandα=0.5trafficperchild:
(seetechnicalreport[27]).
|     |     |     |     |     | NearestPartitionVolumeApproximation |     | Thehalf-space |     |
| --- | --- | --- | --- | --- | ----------------------------------- | --- | ------------- | --- |
C =0.10×1200=120µs,
before
|     |     |     |     |     | approximationisinvalidforthenearestpartitionP |     | 0 ,sincethe |     |
| --- | --- | --- | --- | --- | --------------------------------------------- | --- | ----------- | --- |
C =0.05×(550+550)=55µs,
|     | est |     |     |     | querylieswithinit.Instead,wefirstcomputehyperspherical |     |     |     |
| --- | --- | --- | --- | --- | ------------------------------------------------------ | --- | --- | --- |
∆′=60−120+55=−5µs. capvolumesv fortheremainingM−1candidatepartitions
j
|                    |     |      |                      |     | andnormalizethesesothat∑        | M − | 1v =1.Theprobability | p   |
| ------------------ | --- | ---- | -------------------- | --- | ------------------------------- | --- | -------------------- | --- |
| Because∆′<−τ,bothP |     | andP | aretentativelysplit. |     |                                 | j=  | 1 j                  | 0   |
|                    |     | 1    | 2                    |     | thatnoneighborislocatedoutsideP |     | is:                  |     |
0
| 2. Verify | AftersplittingweseethatP |     | 1 hasa250/250split, |     |     |     |     |     |
| --------- | ------------------------ | --- | ------------------- | --- | --- | --- | --- | --- |
butP comesout450/50:
|     | 2   |     |     |     |     | M−1       |     |     |
| --- | --- | --- | --- | --- | --- | --------- | --- | --- |
|     |     |     |     |     |     | p = ∏(1−v | ),  | (8) |
|     |     |     |     |     |     | 0         | j   |     |
C (P )=0.05×(1050+250)=65µs,
|     | verify 2 |     |     |     |     | j=1 |     |     |
| --- | -------- | --- | --- | --- | --- | --- | --- | --- |
∆(P )=60−120+65=+5µs.
|     | 2   |     |     |     | withtheremainingprobabilitydistributedproportionally |     |     |     |
| --- | --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- |
amongotherpartitionsaccordingtotheirvolumesv:
i
3. Decide
| • P | :commitbecause∆=−5µs<−τ=−4µs |     |     |     |     | p i =(1−p | 0 )v i . | (9) |
| --- | ---------------------------- | --- | --- | --- | --- | --------- | -------- | --- |
1
• P :rejectbecause∆=+5µs>−τ=−4µs
2
| Theverifystepthereforeblocksanimbalancedsplitthat |     |     |     |     |     |     | c 1 |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
wouldotherwiseincreasequerylatency.
v
|                                  |     |     |     |     |     | v   | 1   |     |
| -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 AdaptivePartitionScanning(APS) |     |     |     |     |     | 0   |     |     |
h 1
ρ
q
AdaptivePartitionScanning(APS)dynamicallydetermines
h
t h e nu m b e r o f p a rt itio ns t o sc a n p e rq u e r y to ac h iev e a s p e c - 2
|              |                       |                 |                       |                |     | c   | v   |     |
| ------------ | --------------------- | --------------- | --------------------- | -------------- | --- | --- | --- | --- |
|              |                       |                 |                       |                |     | 0   | 2   |     |
| i fi ed r ec | a ll t a rg e t τ R w | it h m i n im a | l la t e n cy . A P S | a da p t s t o |     |     |     |     |
evolvingworkloadsandchangingindexstructures,making
itparticularlyeffectiveindynamicdatasettings.Wefirstin-
c
2
troducethegeometricmodelunderlyingAPS,followedbya
detaileddescriptionofthescanningalgorithm,andconclude Figure3:Thequeryhypersphere(centeredatqwithradiusρ)
withkeyperformanceoptimizations.WeapplyAPSateach intersectingpartitionboundaries.Theintersectionvolumes
leveloftheindexindependently.Forclaritywefocusonthe v andv correspondtotheprobabilityoffindinganearest
1 2
Euclideandistance,wediscussinnerproductmetricsinthe neighborinpartitionsP andP ,respectively.
1 2
technicalreport[27].
| GeometricModel | Toestimatetheprobabilitythateachpar- |     |     |     |     |     |     |     |
| -------------- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
5.1 APSalgorithm
titioncontainsoneofthequery’sknearestneighbors,APS
usesageometricinterpretation.Givenqueryqandρthedis- Algorithm1detailstheAPSprocedure.Givenqueryq,recall
tancetothek-thnearestneighbor,considerthehypersphere targetτ ,andtheinitialcandidatefraction f :
|                                                      |     |     |     |     | R                 |                               | M   |     |
| ---------------------------------------------------- | --- | --- | --- | --- | ----------------- | ----------------------------- | --- | --- |
|                                                      |     |     |     |     | 1. ScanpartitionP | ,initializingthequeryradiusρ. |     |     |
| B(q,ρ).Underauniform-densityassumption,thefractionof |     |     |     |     |                   | 0                             |     |     |
this sphere’s volume intersecting partition P estimates the 2. Compute probabilities p i for each remaining candidate
i
partitionsbasedonradiusρ.
| probabilitythatP | i holdsanearestneighbor: |     |     |     |     |     |     |     |
| ---------------- | ------------------------ | --- | --- | --- | --- | --- | --- | --- |
3. Iterativelyscanpartitionsindescendingprobabilityorder
|     |     | (cid:0) | (cid:1) |     |     |     |     |     |
| --- | --- | ------- | ------- | --- | --- | --- | --- | --- |
Vol B(q,ρ)∩P untilcumulativerecallexceedstargetτ ,updatingradius
|     | p = |     | i , | (7) |     |     | R   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
i (cid:0) (cid:1) ρandrecomputingprobabilitieswheneverρshrinkssig-
Vol B(q,ρ)
|     |     |     |     |     | nificantly(beyondthresholdτ |     | ρ ). |     |
| --- | --- | --- | --- | --- | --------------------------- | --- | ---- | --- |
Becausewedonotknowthetruedistanceofthek-thnear- This process is conducted at each level of the index. To
estneighborapriori,wesetρtothecurrentk-thnearestneigh- avoidpropagatingerrorsfromsearchinghigherlevels,wefix
borobservedandupdateitonlineaspartitionsarescanned. therecalltargetto99%forthehigherlevels(Table6).
IntersectionVolumeApproximation Exactcomputationof Performance Optimizations APS incorporates two opti-
intersectionvolumesbetweenasphereandhigh-dimensional mizationstominimizecomputationaloverhead.First,itpre-
Voronoi partition boundariesisinfeasible,aspartitionsare computesvaluesoftheregularizedincompletebetafunction
intersectionsofmultiplehalf-spaces.Instead,weapproximate at1024evenlyspacedpointsin[0,1]andlinearlyinterpolates
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    159

Algorithm1AdaptivePartitionScanning(APS) To maximize the benefits of data placement,Quake em-
Input: queryq,centroidsC,recalltargetτR,initialcandidatefrac- ployspartitionaffinityandNUMA-awareworkscheduling.
tion fM,recomputethresholdτρ,k PartitionsareboundtospecificCPUcores.Thisbindingen-
Output: knearestneighborsofq suresthatpartitionsarealwaysscannedbythesamecoreto
1: R←emptymax-heapofsizek maximizecacheutilization.Queriesarescheduledtoworker
2: S← fM∗N l nearestcentroidstoq threadsbasedonthelocationofthedatapartitionstheyneed
3: scanP 0 ;updateR;setρ toaccess.Whenaqueryrequiresscanningmultiplepartitions,
4: foreach(ci,Pi)∈S\{c 0 }do the workis dividedamong threads on the relevantNUMA
5: computepi
nodeswherethepartitionsreside.Byaligningthreadexecu-
6: r←p 0 ;m←1 tionwithdataplacement,Quakeminimizesremotememory
7: whiler<τRandunscannedcandidatesremaindo
accessestomaximizememorybandwidthutilization.
8: chooseiwithmaximalpi;scanPi;updateH
NUMA-Aware Query Execution with APS Quake inte-
9: m←m+1
10: ρ′←distancetok-thinH gratesNUMA-awareprocessingwithAdaptivePartitionSe-
11: if|ρ′−ρ|>τρρthen lection(APS)todynamicallyselectwhichpartitionstoscan
12: ρ←ρ′;recomputepj basedonqueryrequirementsanddesiredrecall.Thequery
13: r←r=∑ m
i=
−
0
1pi p
ti
r
o
o
n
c
s
e
a
ss
n
i
d
ng
a
i
m
nv
a
o
in
lv
t
e
h
s
re
b
a
o
d
th
co
w
o
o
r
r
d
k
i
e
n
r
a
t
t
h
in
r
g
ea
t
d
h
s
e
s
p
c
r
a
o
n
c
n
e
i
s
n
s
g
.
localparti-
14: returnR
Algorithm2NUMA-AwareQueryProcessingwithAdaptive
Table2: Meansingle-threadedquerylatencyandrecallfor
PartitionSelection
APSvariantsonSIFT1Mdatasetatrecalltarget90%.APS-
RP:recomputesprobabilitiesaftereachpartitionscanwithout
Input: Queryvectorq,IndexpartitionsPi withlocationsNodej,
RecallthresholdτR,PeriodtocheckrecallTwait
precomputation.APS-R:recomputesaftereachpartitionscan
Output: Top-knearestneighborstoqsatisfyingrecallthresholdτ
withprecomputation.APS:recomputesprobabilitiesonlyif 1: Initialize:R←0/ (globalresultset),S←sortedlistofpartitions
queryradiuschangesbymorethanτ ρ =1%,usingprecom- basedondistancetoq(obtainedfromsearchingparent)
putedbetafunctionvalues. 2: DistributeqtolocalmemoryofNUMAnodes
3: forallNUMAnodesNodejinparalleldo
Configuration Recall SearchLatency 4: Wj←workerthreadsonNodej
APS 91.2% .48ms 5: Pj←partitionsonNodejfromS
APS-R 91.2% .59ms 6: EnqueuepartitionsPjtolocaljobqueue
APS-RP 91.2% .68ms 7: whilenotallpartitionsinShavebeenprocesseddo
8: MainThread:
9: WaitforapredefinedintervalTwait
duringqueries.Second,partitionprobabilitiesarerecomputed 10: MergepartialresultsfromworkerthreadsintoR
onlywhenthequeryradiusρshrinksbymorethanarelative 11: EstimatecurrentrecallrusingEqn.7
thresholdτ
ρ
.Table2showstheseoptimizationsreducequery 12: ifr≥τRthen
latencyby29%onSIFT1Mwithoutsacrificingrecall. 13: Breakandterminateworkerthreads
14: Returntop-kresultsfromR
6 QuakeImplementation 15: functionWORKERTHREAD(q,LocalJobQueue)
16: whileJobQueuenotemptydo
HerewediscussNUMA-awarequeryprocessingandimple-
17: Pi←DequeuenextpartitionfromJobQueue
mentationdetailsofQuake.
18: ComputedistancesbetweenqandvectorsinPi
NUMADataPlacementandQueryProcessing Querypro- 19: UpdatelocalpartialresultsRj
cessinginpartitionedvectorindexesismemory-bound,and 20: SignalMainThreadaboutnewpartialresults
thereforeincreasingtheeffectivememorybandwidthavail-
abletothesystemwillreducequerylatency.NUMA-aware
AlgorithmExplanation: InAlgorithm2,themainstepsare:
intra-queryparallelismhasbeenappliedinthecontextofre-
1. Initialization: The query vector q is distributed to the
lationaldatabasesystemstogreatsuccess[17,35],buthasyet
localmemory of NUMA nodes withrelevant partitions.
tobeappliedtovectordatabases.
Partitionsaresortedusingtheircentroiddistancetoq.
Inordertomaximizememorybandwidthutilization,Quake
distributesindexpartitionsacrossNUMAnodesandensures 2. Worker Threads Execution: Each NUMA node has
thatcoresonlyscanpartitionsresidentintheirrespectivenode. workerthreadsthatprocesspartitionsassignedtothatnode.
QuakeassignsindexpartitionstospecificNUMAnodesusing Theycomputedistancesbetweenqandvectorsintheirlo-
round-robinassignment.Thisassignmentprocedureallows calpartitions,updatingtheirlocalpartialresults.
forsimpleloadbalancingaspartitionsareaddedtotheindex 3. Main Thread Coordination: The main thread periodi-
bythemaintenanceprocedure. callymergespartialresultsfromallworkerthreads.Ituses
160 19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

theAPSrecallmodeltoestimatethecurrentrecallbased withprobabilityproportionaltotheirpageviewscorrespond-
ontheresultsaccumulatedsofar. ingtoroughlya50/50read/writeratio.Thissettingimitates
4. AdaptiveTermination:Iftheestimatedrecallmeetsor evolvinginterestandperiodicgrowthofthedataset.
exceedsthethresholdτ ,themainthreadreturnsthetop- OpenImages-13M Using the methodology described by
R
kresultsandsignalstheworkerthreadstoterminatethe SVS[5],wegenerateaworkloadof13Mimagesfrom the
processingofremainingpartitions. OpenImagesdataset[15].Embeddingsareproducedusing
Clip [37] in an inner product metric space. The workload
Thisadaptiveapproachensuresthatthesystemprocesses
maintainsaslidingwindowof2millionresidentvectorsand
onlyasmuchdataasneededtomeettherecallrequirements,
insertsanddeletesvectorsbasedonclasslabelsuntilall13
improvingefficiencyandreducingquerylatency.
millionvectorshavebeenindexedatleastonce.Eachinsert
ImplementationDetails WeimplementedQuakein7,500
and delete affects roughly 110K vectors. After each insert
linesofC++andprovideaPythonAPIforease-of-use.We
anddeleteoperation,werun1,000queriesrandomlysampled
usedprimitivesinFaiss[8],PyTorch[20],andSimSIMD[30]
fromtheentirevectorset.Thisscenariostressesbothinsertion
toenablehigh-performancemanagementofinvertedlists,ef-
anddeletionperformanceaswellassustainedquerylatency.
ficientbatchtensoroperations,andAVX512intrinsicsforfast
Workload Generator To test performance under varying
distancecomparisons.Wealsousedahighperformancecon-
workloadproperties,weemployaconfigurableworkloadgen-
currentqueue[29]topreventcontentionduringcoordination
eratorapplicabletoanyvectordataset.Thekeyparameters
ofqueryprocessing.Inaddition,wedevelopedaworkload
are:numberofvectorsperoperation,operationcount,oper-
generatorandevaluationframeworkinPythontocreateand
ation mix (read/write ratio), and spatial skew. For skewed
evaluatevectorsearchworkloads.Quakeisopen-sourcedat
workloads,vectorsareclusteredandsampledfromtoproduce
https://github.com/marius-team/quake.
queriesandupdates,reflectinghotspotsinthevectorspace.
7 Experiments Weconstructtwoexampleworkloadsfroma10Mvector
subsetoftheMSTuring[2]datasetusingL2distance:
WeevaluateQuakeusinganumberofbenchmarksandsum-
marizeourmainfindings: • MSTuring-RO: A pure search workload. We uniformly
samplefrom100,000providedqueryvectorsandexecute
1. Quakeachievesthelowestsearchtimeacrossalldynamic
100searchoperations,eachquerying10,000vectors.This
workloadscomparedtostate-of-the-artgraphindexes,with
setuptestssearchefficiencyinastaticsetting.
1.5-13×lowersearchlatencythanHNSW,DiskANN,and
• MSTuring-IH:Adynamicworkloadinterleavinginserts
SVSwhilehaving18-126×lowerupdatelatency.
andsearches.Beginningwith1millionvectors,thedataset
2. We also find that APS matches the nprobe of an oracle
growsto10millionasweprocess1,000operationswitha
acrossrecalltargetsonSIFT1M,withonlya17-29%in-
90%insertand10%searchratio.Thisteststheabilityto
creaseinlatencyrelativetotheoracle.
handlelarge-scalegrowthwhilemaintainingqueryquality.
3. APSperformson-parorbetterthanexistingearlytermina-
WeusethedatasetsSIFT1M[13],SIFT10M,andMSTUR-
tionmethods[7,18,48]andrequiresnoofflinetuning.
ING100M[2]toconductmicrobenchmarks.
4. Quake’sNUMA-awarequeryprocessingexhibitslinear
7.2 ExperimentalSetup
scalabilityandhighmemorybandwidthutilizationonthe
MSTURING100Mdataset.Quakeachieves20×and4× Large-scale experiments are run on a 4-socket server with
lowerquerylatencycomparedtosingle-threadedandnon- IntelXeonGold6148CPUs(80cores,160threads),500GB
NUMAawareconfigurations,respectively. RAMacross4NUMAnodes,and 300GB/stotalmemory
bandwidth. Some microbenchmarks (Tables 2,5,7,and6)
7.1 Workloads
arerunona2023MacBookProwithaM2Maxchip.
Weperformedourevaluationonadiversesetofreal-world Searchqueriesareprocessedoneatatimeandwereport
andsyntheticworkloads. thetotaltimetoprocessallqueriestoreachatargetof90%
Wikipedia-12M Thisdatasetandworkloadtracearederived recallfork=100.Unlessotherwisestated,allsearchnumbers
frommonthlyWikipediapageadditionsandpage-view[4] useasingleworkerthread.Quakeadditionallyreportsamulti-
frequenciesbetweenApril2013andDecember2021.Wecon- threadconfigurationQuake-MT(16threads)wherepartition
sideronlypagesaboutpeopleorthoselinkingtopeople.The scansareparallelizedforindividualqueries,whileQuake-ST
datasetbeginswith1.6millionpagesandgrowsto12million uses a single thread for search. For updates we report the
after103 updates,and therefore the average update size is totalupdate and maintenance time,where bothQuake and
≈ 100,000 vectors. Embeddings are generated by training the baselines process updates in batches using 16 threads.
DistMult[46]graphembeddings(viaMarius[28,41])onthe This setup simulates an online environment where queries
Wikipedialinkstructure,andusetheinnerproductmetric. arrive individually,andupdates are appliedin batches. We
Theworkloadsimulatesmonthlyinsertsofnewpages,fol- reportmaintenancetimeseparatelyfromupdatelatency,as
lowedby100,000searchqueriessamplingpageembeddings maintenancecanbeconductedinthebackgroundinonline
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation 161

systems [45]. DiskANN,takes12hours.Thus,Quake-MTis8×fasterto
Baselines: WecompareQuakeagainstseveralstate-of-the-art searchthanthestrongestbaselineonthisworkloadderived
methods,includingbothpartitionedandgraph-basedindexes: fromreal-worldaccesspatterns.
• Faiss-IVF[8]:Apopularinvertedfile(IVF)indexinFaiss. OntheOPENIMAGES-13Mworkload,whichincludesboth
Ithandlesupdatesbutdoesnomaintenance. insertionsanddeletions,Quake’smulti-threadedandsingle-
• DeDrift [6]: An incremental maintenance strategy de- threadedsearchtimesare.03and.14hoursrespectively.The
signedtoreduceclusteringdriftbyperiodicallyreclustering bestcompetingapproach,DiskANN,records.22hours,mak-
large partitions togetherwith small ones. We implement ingQuake-MT7.3×andQuake-ST1.6×faster.Faiss-HNSW
DeDrift’slogicwithinQuake. doesnotsupportdeletionssoitisomitted.BothSVS’sand
• LIRE[45]:MaintenanceprocedureusedbySpFresh.LIRE DiskANN’sdeleteconsolidationisexpensive,leadingtoor-
incrementallysplitslargeclustersanddeletessmallclusters ders of magnitude higher update latency than partitioned
afterupdates,followedbylocalreassignments.Weimple- indexes,illustratingthatgraph-basedindexesstrugglewith
mentLIRE’sapproachwithinQuake. dynamicoperations.Quake’scontinuousmaintenancekeep
• ScaNN[10]:Astate-of-the-arthighlyoptimizedpartitioned partitionsbalanced,achievinglowlatencyandstablerecall.
indexsystem.Itusesanunpublishedincrementalmainte- Forthestatic,read-only,MSTURING10M-ROworkload,
nanceproceduresimilartoLIRE. Quake’smaintenanceimprovestheindexstructureevenwith-
• Faiss-HNSW[24]:Agraph-basedapproach(HNSW)im- out data changes, adapting partitions to the query pattern.
plementedinFaiss.Itsupportsincrementalinsertsbutnot For Quake-MT,this yields a search time of .63 hours and
deletes.Thus,forworkloadswithdeletions,weomitFaiss- Quake-STtakes2.43hourstoconductthesearch.However,
HNSWfromthosecomparisons. theMSTURING10Mdatasetisespeciallychallengingforpar-
titioned indexes, as they need to scan roughly 10% of all
• DiskANN[38]:SystembuiltaroundtheVamana[39]index
partitionsinordertomeettherecalltarget.Incontrast,the
withsupportfordynamicupdates.
well-optimizedSVSlibraryexhibitsasuperiorsearchtimeof
• SVS[5]:Arecentlyreleasedoptimizedimplementationof
.33hours,demonstratingthatinstaticsettings,well-optimized
theVamanaindexwithsupportfordynamicupdates.
graphindexesarestrongcompetition.
WeconfigurethemainparametersofQuakeandthebase-
On MSTURING10M-IH,where the dataset grows from
linesasfollows.Wedisablevectorquantization/compression
onetotenmillionvectors,Quake-MTachievesatotalsearch
forallbaselines,asnotallbaselinessupportit.Forpartitioned
timeof.54hours.DiskANN,thesecond-bestperformer,hasa
indexesweusesqrt(|X |)partitionswhere|X |istheinitial
0 0
searchtimeof.81hours,makingQuake-MT1.5×fasterdue
numberofvectorsintheworkload.Forthegraphindexes,we
tointra-queryparallelism.However,single-threadedQuake
useagraphdegreeof64. ForLIREandQuake,wesetthe
is2.6×slowerthanDiskANN,furtherillustratingthesearch
partitionrefinementradiusr=50.ForQuakeweuseasingle
efficiencyofgraphindexes.Theotherbaselinesfailtomain-
levelofpartition,setτ=250ns,useoneiterationofk-means
taintherecalltargetorsufferfromhighlatencyduetotheir
for refinement and set f between 1%-10%. All systems
M
staticparametersandinabilitytopreventpartitionskew.
use16threadsforupdatesandmaintenance(ifapplicable).
Overall, these results demonstrate that Quake’s combi-
SCANN,DiskANN,andSVSperformmaintenanceeagerly
nation of adaptive partition scanning, incremental mainte-
duringanupdate,thereforewedonotmeasuremaintenance
nance,and NUMA-aware parallelism consistently delivers
timeseparatelyfromupdatetime.Weconsidermaintenance
low-latency queries at the desired recall. Systems without
aftereachoperation forallmethods. Throughoutallexper-
maintenance(Faiss-IVF)sufferfromskew-inducedlatency
iments,indexes search parameters are tuned to achieve an
increases,thosetiedtostaticsearchparameters(LIRE)strug-
averageof90%recallfork=100acrosstheworkloads.
gletomaintainrecallwithoutincurringhigherquerytimes,
7.3 End-to-EndEvaluation
andgraph-basedmethods(Faiss-HNSW,DiskANN)facesub-
ComparisonwithBaselines Table3showsthatQuakecon- stantialoverheadswhenhandlingupdatesanddeletions.By
sistentlyachieveslowersearch,updateandtotaltimeonall integratingthesecomponents,Quakematchesthelowupdate
workloads. On the WIKIPEDIA-12M workload,where the costofpartitionedindexeswhileoutperforminggraphindexes
dataset grows over time and partitions can become unbal- insearchlatencyindynamicworkloads.Ourdesignisanad-
anced,themulti-threadedQuake-MTtakes1.53hourstopro- vancementtothestate-of-the-art,providingstable,efficient
cess searches, while single-threaded Quake-ST takes 9.48 performanceacrossdiverse,andevolvingworkloads.
hours.Incontrast,Faiss-IVFclimbsto165hoursduetothe ComparisonwithPartitionedIndexMaintenanceMeth-
lackofmaintenance,DeDriftreaches132hoursdespiteits ods HereweperformadetailedcomparisonwithLIREand
rebalancingefforts,LIREisunabletomeettherecalltarget DeDrift, measuring the latency, recall, and number of par-
andtakes44hoursandSCANNperformssimilarlywithpoor titionsovertimeonthe WIKIPEDIA-12M workload.Fora
update latency due to over-eagermaintenance applied dur- faircomparison,weuseasingle-threadtohighlightthead-
ingupdates.Eventhebest-performinggraph-basedmethod, vantagesofAPSandmaintenanceinQuake.Theresultsare
162 19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|     |     |     | WIKIPEDIA-12M |     |     | OPENIMAGES-13M |     |     | MSTURING10M-RO |     |     | MSTURING10M-IH |     |     |
| --- | --- | --- | ------------- | --- | --- | -------------- | --- | --- | -------------- | --- | --- | -------------- | --- | --- |
Method
|     |     | S   | U   | M T |     | S U | M   | T   | S   | M   | T   | S   | U   | M T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Quake-MT 1.53 .01 .44 1.98 .03 .02 .10 .15 .63 .08 .71 .54 .02 .14 .70
Quake-ST 9.48 .01 .44 9.93 .14 .02 .10 .26 2.43 .08 2.51 2.12 .02 .14 2.28
Faiss-IVF 165.8 .005 0 165.8+ .45 .01 0 .46 12.25 0 12.25 13.72 .01 0 13.73
132.8+
DeDrift 132.6 .03 .19 .23 .03 .19 .45 – – – 19.17 .03 .55 19.75
|      |     |      |     | 44.61∗+ |     |         |     |     |     |     |     |      |     | 9.32∗ |
| ---- | --- | ---- | --- | ------- | --- | ------- | --- | --- | --- | --- | --- | ---- | --- | ----- |
| LIRE |     | 44.2 | .03 | .38     |     | .15 .05 | .11 | .31 | –   | –   | –   | 9.08 | .02 | .21   |
ScaNN 50.27 1.75 0 52.02+ .41 .21 0 .62 2.97 0 2.97 6.70 .09 0 6.79
Faiss-HNSW 14.65 .18 0 14.83 – – – – 1.9 0 1.9 1.27 1.38 0 2.64
DiskANN 12.11 .32 0 12.43 .22 1.53 0 1.75∗ 1.16 0 1.16 .81 .48 0 1.28
|     |     |       |     | 21.11∗ |     |          |     |      |     |     |     |      |     | 2.35∗ |
| --- | --- | ----- | --- | ------ | --- | -------- | --- | ---- | --- | --- | --- | ---- | --- | ----- |
| SVS |     | 20.54 | .57 | 0      |     | .29 2.32 | 0   | 2.61 | .33 | 0   | .33 | 2.11 | .24 | 0     |
Table3:Totalworkloadtimebreakdowninhours.S:search,U:update,M:maintenance,T:overalltotal.Recalltarget=90%
andk=100.Searchqueriesareprocessedone-at-time,updatesareprocessedinbatches,maintenanceisconductedaftereachbatch
ofsearchorupdateoperations.∗Denotesthemethodisunabletomeettherecalltargetwithstaticqueryparameters.+Denotesthe
methoddidnotfinishina24hourtimebudget,fortheseweestimatetheruntimebasedona10%subsampleofsearchqueries.
|     |     |     |     |     |     |     |     | These | results | show | that Quake’s | approach |     | to maintenance |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ------- | ---- | ------------ | -------- | --- | -------------- |
issuperiortoexistingmethodsforpartitionedindexmainte-
nanceinminimizingquerylatencyandrecallstability.
Table4:AblationStudyonWIKIPEDIA-12Mshowingmean
searchlatencyandthestandarddeviationofrecall.
|     |     |     |     |     |     |     |     |     | Configuration        |     |     | SearchLatency |     | RecallStd. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | ------------- | --- | ---------- |
|     |     |     |     |     |     |     |     |     | Quake-MT             |     |     | 0.53ms        |     | .008       |
|     |     |     |     |     |     |     |     |     | Quake-MTw/oAPS       |     |     | 0.50ms        |     | .025       |
|     |     |     |     |     |     |     |     |     | Quake-ST             |     |     | 3.28ms        |     | .005       |
|     |     |     |     |     |     |     |     |     | Quake-STw/oAPS       |     |     | 3.18ms        |     | .025       |
|     |     |     |     |     |     |     |     |     | Quake-STw/oMaint/APS |     |     | 45.20ms       |     | .014       |
Wikipedia-12MAblation
Toquantifythecontributionsof
Quakecomponents,wedisabledkeyfeaturesandmeasured
theimpactonWIKIPEDIA-12MworkloadinTable4.Wesee
thatdisablingAPShaslittleimpactonthequerylatency,as
Figure4:Comparisonofsingle-threadedsearchlatency,re-
|     |     |     |     |     |     |     |     | Quake | can achieve |     | a low latency | even | in  | the static nprobe |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ----------- | --- | ------------- | ---- | --- | ----------------- |
callandnumberofpartitionsforQuakevs.maintenanceap-
setting.However,APSprovidessignificantlymorerecallsta-
| proaches | LIRE | and | DeDrift | on WIKIPEDIA-12M. |     | Quake |     |     |     |     |     |     |     |     |
| -------- | ---- | --- | ------- | ----------------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
bility,asevidencedbytheincreaseinstandarddeviationwhen
maintainsstablelatencyandrecallthroughouttheworkload.
|     |     |     |     |     |     |     |     | APS | is disabled. | Disabling |     | NUMA-aware |     | multi-threading, |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --------- | --- | ---------- | --- | ---------------- |
however,showsa6×increaseinquerylatency,demonstrating
|     |     |     |     |     |     |     |     | thebenefitofparallelizationofpartitionscans. |     |     |     |     |     | Finally,we |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------- | --- | --- | --- | --- | --- | ---------- |
showninFigure4.Firstlookingatrecall,weseethatQuake disablemaintenanceandseeasignificantincreaseinlatency,
| maintains | a stable | recall | of  | near 90%,while | LIRE’s | recall |     |     |     |     |     |     |     |     |
| --------- | -------- | ------ | --- | -------------- | ------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
similartothelatencyofFaiss-IVF;herepartitionsbecome
degrades over time as it uses a static nprobe. DeDrift’s re- extremelyimbalancedduetotheskewintheworkload(see
callstaysrelativelyconstant,asitdoesnotadjustthenumber
Figure1a)causingqueriestoscanmorevectorsandtherefore
of partitions and therefore does not need to adjust nprobe. increasing latency. This furtherdemonstrates the necessity
However,whenturningourattentiontolatency,weseethat formaintenancefordynamicworkloads.Inconclusion,each
Quakehasnear-constantstablelatency,evenasthedataset
pieceofQuakecontributestoitsperformanceintermsofboth
grows,whileDeDrift’slatencyincreasessignificantlywith recallstabilityandminimalquerylatency.
| time. In | terms | of the | numberofpartitions,we |     | see | DeDrift |     |     |     |     |     |     |     |     |
| -------- | ----- | ------ | --------------------- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
staysconstantwhileQuakeandLire increaseby2.5×and 7.4 Multi-QueryProcessing
10×respectively.LIREusessignificantlymorepartitionsbe- HerewecomparethesearchperformanceofQuakeandbase-
cause it uses size thresholding to determine when to split, linemethodsinastaticbatchedquerysetting.Figure5shows
regardlessofwhetheragivenpartitionishotornot.Quakeon the QPS ata recallof90%,varying the numberofqueries
theotherhandonlysplitspartitionsiftheircontributiontothe in a batchon the WIKIPEDIA-12M workload. The dataset
costmodelishigh,allowingformoreefficientmaintenance. includesall12Mvectors,with10,000queriessampledaccord-
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    163

|     |     |     |     | sion, NUMA-aware | intra-query | parallelism | is an effective |     |
| --- | --- | --- | --- | ---------------- | ----------- | ----------- | --------------- | --- |
mechanismfordecreasingquerylatencybyutilizingthefull
memorycapabilitiesofmulti-coremachines.
Figure5:Multi-queryevaluationonWIKIPEDIA-12Mwith
10,000searchqueries.QPS@recall=90%ismeasuredfor
allbaselineswhilevaryingthebatchsize.Allmethodsuse16 (a)MeanSearchLatency (b)ScanThroughput
threadstoprocessqueries.
Figure6:MSTURING100M:Scalingthenumberofthreads
withandwithoutNUMA.
ingtoWikipediapageviewsfromDecember2021.ForQuake,
| FaissIVF, | and SCANN, | we use 3,500 partitions; | for Fais- |     |     |     |     |     |
| --------- | ---------- | ------------------------ | --------- | --- | --- | --- | --- | --- |
Table5:Early-terminationmethodsonSIFT1Mwithaparti-
sHNSW,SVS,andDiskANN,wesetthegraphdegreeto64.
tionedindexwith1000partitions.Eachrowshowstheaverage
Allexperimentsuse16threadsforqueryprocessing.Quake
employsthemulti-queryexecutionpolicyin[26]and[34], recall,nprobe,andmeanper-querylatencyinmilliseconds
|     |     |     |     | over 10000 | queries after | tuning for a specific | recall | target |
| --- | --- | --- | --- | ---------- | ------------- | --------------------- | ------ | ------ |
groupingqueriesbythepartitionstheyaccessandscanning
|     |     |     |     | fork=100. | We also reportthe | totaloffline | tuning time | in  |
| --- | --- | --- | --- | --------- | ----------------- | ------------ | ----------- | --- |
eachpartitionexactlyonceperbatchinparallel.
seconds,whereAPSneedsnoofflinetuning.
Quakeconsistentlyoutperformsallbaselinesacrossevery
batchsize,withanincreasingadvantageasbatchsizesgrow.
|     |     |     |     | Method | Target Recall | nprobe Latency | OfflineTuning |     |
| --- | --- | --- | --- | ------ | ------------- | -------------- | ------------- | --- |
Atthelargestbatchsize(10,000queries),Quakeachievesa
6.7×speedupoverFaissIVFandSCANN.Thisperformance APS 80% 82.1% 11.8 0.34ms 0
gainstemsfromQuake’sefficientmulti-queryexecutionstrat- 90% 91.2% 20.2 0.48ms 0
|     |     |     |     |     | 99% 98.9% | 50.1 0.96ms |     | 0   |
| --- | --- | --- | --- | --- | --------- | ----------- | --- | --- |
egy,whereitscanseachpartitiononceperbatch,incontrast
|     |     |     |     | Auncel[48] | 80% 85.7% | 16.4 0.41ms | 66.3s |     |
| --- | --- | --- | --- | ---------- | --------- | ----------- | ----- | --- |
toFaissIVFandSCANN,whichscanpartitionsindividually
|     |     |     |     |     | 90% 98.1% | 73.8 1.29ms | 73.8s |     |
| --- | --- | --- | --- | --- | --------- | ----------- | ----- | --- |
perquery.ComparedtoDiskANN,thestrongestgraph-based 99% 99.7% 95.9 1.61ms 83.2s
competitor,Quakestillmaintainsasubstantial1.8×speedup.
|               |             |                     |              | SPANN[7] | 80% 81.6% | 11 0.31ms | 173s |     |
| ------------- | ----------- | ------------------- | ------------ | -------- | --------- | --------- | ---- | --- |
| These results | demonstrate | that Quake delivers | high perfor- |          |           |           |      |     |
|               |             |                     |              |          | 90% 90.2% | 19 0.43ms | 183s |     |
mance not only in single-query scenarios but also in large 99% 99.0% 70 1.07ms 259s
multi-queryworkloads.
|     |     |     |     | LAET[18] | 80% 81.3% | 10.5 0.29ms | 81s  |     |
| --- | --- | --- | --- | -------- | --------- | ----------- | ---- | --- |
|     |     |     |     |          | 90% 90.5% | 18.2 0.42ms | 104s |     |
7.5 Scalability
|     |     |     |     |       | 99% 99.0% | 58.3 1.03ms | 232s |     |
| --- | --- | --- | --- | ----- | --------- | ----------- | ---- | --- |
|     |     |     |     | Fixed | 80% 81.7% | 11 0.33ms   | 318s |     |
WetestedQuake’sparallelscalabilitybyvaryingthenumber
|     |     |     |     |     | 90% 90.3% | 19 0.44ms | 330s |     |
| --- | --- | --- | --- | --- | --------- | --------- | ---- | --- |
ofthreads.InFigure6wemeasurethemeansearchlatency
|     |     |     |     |     | 99% 99.0% | 65 1.16ms | 424s |     |
| --- | --- | --- | --- | --- | --------- | --------- | ---- | --- |
andscanthroughput(bytesscanned/querylatency)onMS-
|     |     |     |     | Oracle | 80% 83.3% | 11.5 0.29ms | 320s |     |
| --- | --- | --- | --- | ------ | --------- | ----------- | ---- | --- |
TURING100Mtoreacharecallof90%.Notethatthisdataset
|     |     |     |     |     | 90% 92.4% | 19.3 0.41ms | 331s |     |
| --- | --- | --- | --- | --- | --------- | ----------- | ---- | --- |
has100millionvectorsandis10×largerthanthedatasetswe
|     |     |     |     |     | 99% 99.2% | 42.0 0.74ms | 368s |     |
| --- | --- | --- | --- | --- | --------- | ----------- | ---- | --- |
comparedagainstpreviously.WecompareourNUMA-aware
parallelismwithoneinwhichNUMAisdisabled.Forboth
7.6 ComparisonwithEarlyTerminationMethods
configurations,weseenearlinearscalabilityuptoaround8
workers,wherethenon-NUMAlatencyperformsbest(28ms). Table 5 compares early-termination methods on SIFT1M,
TheNUMAconfigurationhoweverfurtherimprovesandat highlightingthetradeoffbetweenquerylatency,tuningtime,
64workersachievesalatencyof6ms.Lookingatthescan andrecall,we do notinclude groundtruthgeneration time
throughput,weseethatNUMAachievesapeakthroughput in the tuning time for the baselines. APS analytically es-
of200GBps.Wedonotcompletelysaturatememoryband- timatesrecallatquerytime,eliminatingofflinetuningen-
widthdueto otheroverheadsinvolvedin queryprocessing tirely,whileachievinglatencywithin30%oftheoracleacross
(topksorting,memoryallocations,coordination).Inconclu- allrecalltargets.Fixedselectsastaticnprobepertargetviaan
164    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

expensiveofflinebinarysearch(upto424s),andSPANNsim- partitions at level L . We use an initial search fraction of
1
ilarlyperformsabinarysearchandtunesacentroid-distance f =1.5%atL and25%atL .
|     |     |     |     |     |     |     |     | M   | 0   |     | 1   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
threshold;bothcloselymatchrecalltargetsbutincurhigher WeobservethatoverlyaggressiveearlyterminationatL 1
latencyat90%and99%recall.LAETtrainsaper-querypre- bysettingτ (1)toolowleadstoacleardegradationintotal
r
dictionmodel,incurringmoderatetuningoverhead(81–232s),
|     |     |     |     |     |     |     |     | recall.Forinstance,atτ |     | r (0)=90%,reducingτ |     | r (1)from99% |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | ------------------- | --- | ------------ | --- |
andmatchesrecalltargetswithslightlyhigherlatencycom- to 80% lowers overall recall from 91.0% to 84.1%. This
paredtoAPS.AuncelisthemostsimilarmethodtoAPS,as confirmsthataccuraterecallestimationattheupperlevelis
itaimstoanalyticallyestimaterecallusingpartitionintersec- necessaryto maintain accurate end-to-endrecallestimates.
tion volumes,howeverits volume estimation requires cali- TheseresultsjustifyourdesigndecisioninSection5.1tofix
| bration,anditisaconservativemethod,overshootingrecall. |     |     |     |     |     |     |     | (1)=99% |                |     |                |         |          |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | ------- | -------------- | --- | -------------- | ------- | -------- |
|                                                        |     |     |     |     |     |     |     | τ r     | in multi-level |     | configurations | so that | only the |
WetuneAuncelbybinarysearchingageometricparameter baserecalltargetτ (0)needstobeprovided.
r
(a),overshooting recall significantly (up to 8.1 pp) and in- Inaddition,thetwo-levelindexsubstantiallyreducescen-
creasinglatencybyupto169%comparedtoAPS. Finally, troidscanningoverhead.Thesingle-levelbaselinemustevalu-
theOracle,whichscanstheminimalamountofpartitionsper- atedistancestoall40,000centroidsperquery.Incontrast,the
query,servesasapracticallowerboundonachievablelatency,
two-levelconfigurationperformsanapproximatesearchover
thoughwithprohibitivelyhightuningcost.Thetuningover- thecentroids.Forexample,atarecalltargetofτ (0)=90%
r
headofthebaselinesdemonstratesasignificantburdenfor withτ (1)=99%thetotalquerylatencydropsfrom7.86ms
r
onlinescenarioswherethequeries,data,andindexchange.
to5.08ms,a35%reduction,drivenmainlybythedropinL
1
Thetuningburdenworsensatscale,wheregroundtruthgen- latencyfrom4.89msto2.60ms.
| eration | cost grows | linearly | with | the data | size,and | running |     |                         |     |     |     |     |     |
| ------- | ---------- | -------- | ---- | -------- | -------- | ------- | --- | ----------------------- | --- | --- | --- | --- | --- |
|         |            |          |      |          |          |         |     | 7.8 MaintenanceAblation |     |     |     |     |     |
queriesmultipletimestoconductbinarysearchtakeslonger.
APSthusprovidesnear-optimalperformancewithouttuning Tounderstandtheeffectivenessoftheprimarycomponentsof
overhead,matchingorexceedingallbaselines.
adaptiveincrementalmaintenance(cost-model,partitionre-
finement,andrejection),wereplayadynamicSIFT1Mtrace
| Table6:SIFT10M:Recallandper-levelsearchlatency(ℓ |     |     |     |     |     |     | ,ℓ  |     |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0 1 ,
(30%inserts,20%deletes,50%queries)withdifferentcom-
| total)forasingle-levelbaseline(L |     |     |     | :40,000partitions;L |     |     | :1   |                                                      |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | ------------------- | --- | --- | ---- | ---------------------------------------------------- | --- | --- | --- | --- | --- |
|                                  |     |     |     | 0                   |     |     | 1    | ponentsdisabled.Allmethodsuseasingle-threadandsearch |     |     |     |     |     |
| partition)andtwo-levelindex(L    |     |     |     | :40,000partitions;L |     |     | :500 |                                                      |     |     |     |     |     |
|                                  |     |     |     | 0                   |     |     | 1    | usingAPSwithk=100anda90%recalltarget.Wealsoin-       |     |     |     |     |     |
partitions),whererecalltargetsarevariedateachlevel.The
cludeLIREasabaseline.Table7reportscumulativetimesin
| single-levelbaselineisthefirstrowofeachτ |       |        |        |        |     | (0)block. |     |                                                      |       |      |               |                |     |
| ---------------------------------------- | ----- | ------ | ------ | ------ | --- | --------- | --- | ---------------------------------------------------- | ----- | ---- | ------------- | -------------- | --- |
|                                          |       |        |        |        | r   |           |     | seconds.Forconfigurationswithrefinementweusearefine- |       |      |               |                |     |
|                                          |       |        |        |        |     |           |     | mentradius                                           | ofr f | =50. | The fullQuake | policydelivers | the |
| τr(0)                                    | τr(1) | Recall | ℓ0(ms) | ℓ1(ms) |     | Total(ms) |     |                                                      |       |      |               |                |     |
lowestsearchcost(86s)whilemeetingtherecalltarget.Ifwe
— 81.2% 2.07 4.85 6.92 keepthecostmodelbutskiprefinement(NoRef),maintenance
80% 74.8% 1.44 0.72 2.16 timedecreasessignificantlyfrom21sto5s,yetrecallslips
90% 78.3% 1.56 1.19 2.75 by2.4ppandthesearchtimeincreaseby15.4s.Thisshows
80%
|     | 95% | 80.1% | 1.67 |     | 1.69 | 3.37 |     |           |              |     |                    |              |     |
| --- | --- | ----- | ---- | --- | ---- | ---- | --- | --------- | ------------ | --- | ------------------ | ------------ | --- |
|     |     |       |      |     |      |      |     | thatwhile | refinementis |     | the dominantcostin | maintenance, |     |
|     | 99% | 81.0% | 1.75 |     | 2.57 | 4.33 |     |           |              |     |                    |              |     |
itisnecessaryforminimizingsearchlatency.Disablingthe
|     | 100% | 81.1%   | 1.82 |     | 3.81 | 5.63 |     |            |             |       |            |              |      |
| --- | ---- | ------- | ---- | --- | ---- | ---- | --- | ---------- | ----------- | ----- | ---------- | ------------ | ---- |
|     |      |         |      |     |      |      |     | cost model | and instead | using | size-based | thresholding | (No- |
|     |      | — 91.3% | 2.85 |     | 4.89 | 7.86 |     |            |             |       |            |              |      |
Cost)showswhynaivesizethresholdsareinadequate:search
|     | 80% | 84.1% | 2.07 |     | 0.77 | 2.84 |     |                                                      |            |         |             |         |         |
| --- | --- | ----- | ---- | --- | ---- | ---- | --- | ---------------------------------------------------- | ---------- | ------- | ----------- | ------- | ------- |
|     |     |       |      |     |      |      |     | time rises                                           | 8% despite | similar | maintenance | effort. | The re- |
|     | 90% | 88.2% | 2.26 |     | 1.24 | 3.50 |     |                                                      |            |         |             |         |         |
| 90% |     |       |      |     |      |      |     | jectionmechanismiscritical;onceremoved(NoRej),recall |            |         |             |         |         |
|     | 95% | 90.1% | 2.38 |     | 1.72 | 4.10 |     |                                                      |            |         |             |         |         |
99% 91.0% 2.48 2.60 5.08 collapsesto66%eventhoughsearchandmaintenanceappear
100% 91.2% 2.62 3.88 6.50 cheap.LIRE,whichreliessolelyonsizethresholding,is17%
— 99.0% 4.82 5.5 10.3 slowerinsearchlatency,confirmingthatthecostmodel,re-
jectionmechanism,andpartitionrefinementareessentialfor
|     | 80% | 91.4% | 4.11 |     | 0.77 | 4.88 |     |     |     |     |     |     |     |
| --- | --- | ----- | ---- | --- | ---- | ---- | --- | --- | --- | --- | --- | --- | --- |
maintainingbothindexperformanceandquality.
|     | 90% | 96.0% | 4.59 |     | 1.27 | 5.86 |     |     |     |     |     |     |     |
| --- | --- | ----- | ---- | --- | ---- | ---- | --- | --- | --- | --- | --- | --- | --- |
99%
|     | 95%  | 97.7% | 4.80 |     | 1.75 | 6.55 |     |              |                    |     |            |                    |     |
| --- | ---- | ----- | ---- | --- | ---- | ---- | --- | ------------ | ------------------ | --- | ---------- | ------------------ | --- |
|     |      |       |      |     |      |      |     | 8 Discussion |                    |     |            |                    |     |
|     | 99%  | 98.7% | 5.08 |     | 2.65 | 7.74 |     |              |                    |     |            |                    |     |
|     | 100% | 98.9% | 5.28 |     | 3.93 | 9.21 |     |              |                    |     |            |                    |     |
|     |      |       |      |     |      |      |     | Here we      | offer a discussion |     | of Quake’s | system parameters, |     |
howthedesignextendstonewhardwareanduse-cases.
7.7 Multi-LevelRecallEstimation
|         |          |                   |     |     |     |                |     | 8.1 SettingSystemParameters |     |     |     |     |     |
| ------- | -------- | ----------------- | --- | --- | --- | -------------- | --- | --------------------------- | --- | --- | --- | --- | --- |
| Here we | evaluate | the effectiveness |     | of  | APS | in a two-level |     |                             |     |     |     |     |     |
partitioned index by measuring the impact of varying per- Quake exposes a few search and maintenance parameters,
levelrecalltargetsonoverallrecall.Table6reportsresults which we fix across all workloads unless otherwise stated.
on SIFT10M using 40,000 partitions at level L and 500 Thesedefaultsgivestableperformancewithminimaltuning.
0
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    165

Table 7: Maintenance ablation on the SIFT1M workload. HeterogeneousHardware Toadapttodeviceswithvarying
Times are cumulative (in seconds) over the course of the scan throughputsuchasCPUs,GPUs,ordisk-backedstor-
workload.Recallisaveragedoverallqueries.
age,thecostmodelcanbemodifiedbyprofilingper-device
|     |     |     |     | scanlatency(e.g.,λ |     | (s),λ   | (s),λ (s))andupdating |     |
| --- | --- | --- | --- | ------------------ | --- | ------- | --------------------- | --- |
|     |     |     |     |                    |     | CPU GPU | Disk                  |     |
MaintenanceVariant Search Update Maint. Recall partitioncostestimatesaccordingly.
Quake(Full) 86.3s 21.7s 21.4s 90.5% DistributedEnvironments Inadistributedsetting,eachma-
NoRef 101.7s 22.2s 5.2s 88.1% chinecanrunAPSandmaintenanceindependentlyonitslocal
| NoRef+NoRej |     | 85.5s | 21.0s 1.0s 73.0% |     |     |     |     |     |
| ----------- | --- | ----- | ---------------- | --- | --- | --- | --- | --- |
partitions.Thecostmodelcanaccountforpartitionlocality
| NoRej |     | 84.2s | 19.6s 18.5s 66.2% |     |     |     |     |     |
| ----- | --- | ----- | ----------------- | --- | --- | --- | --- | --- |
andinter-nodevariation.Aseparateloadbalancerwouldbe
| NoCost |     | 93.5s | 20.0s 20.4s 90.1% |     |     |     |     |     |
| ------ | --- | ----- | ----------------- | --- | --- | --- | --- | --- |
requiredtoassignandreplicatepartitionsacrossmachinesin
| NoCost+NoRef |     | 100.7s | 21.2s 0.8s 87.9% |     |     |     |     |     |
| ------------ | --- | ------ | ---------------- | --- | --- | --- | --- | --- |
awaythatminimizestotalquerycost.
| LIRE |     | 100.5s | 21.2s 11.9s 90.0% |                                           |     |                                  |     |          |
| ---- | --- | ------ | ----------------- | ----------------------------------------- | --- | -------------------------------- | --- | -------- |
|      |     |        |                   | VectorCompression                         |     | Vectorcompressiontechniques,such |     |          |
|      |     |        |                   | asProductQuantization[14],reducescancost. |     |                                  |     | Quakecan |
supportcompressionbyprofilingscanlatencyoverpartitions
Searchparameters. Theinitialcandidatefraction f deter- ofcompressedvectorsandupdatingλ(s)inthecostmodel.
M
|     |     |     |     | Filters | Filtered queries | can be | supported by | scaling per- |
| --- | --- | --- | --- | ------- | ---------------- | ------ | ------------ | ------------ |
minesthenumberofpartitionstoconsiderinAPS.Ithasthe
partitionrecallprobabilitiesinAPS,basedontheestimated
largestimpactonperformance.Ifsettoolow,APSmaynot
numberofitemsthatpassthefilterineachpartition.Thiswill
meettherecalltarget;iftoohigh,theinitialscandominates
enableQuaketoavoidscanningpartitionsunlikelytocontain
latency.Wesetthisbetween1%and10%.Infuturework,we
aimtoremovethisparameterentirely.Thenumberofworker matchingresultswhilepreservingrecalltargets.
|     |     |     |     | Concurrency | Thecurrentimplementationexecutessearches, |     |     |     |
| --- | --- | --- | --- | ----------- | ----------------------------------------- | --- | --- | --- |
threadsisbestsettothenumberofphysicalcores.Forlarge
problemsizes,Quakescaleslinearlywiththreadcountuntil updates,andmaintenanceserially.Quakecansupportconcur-
memorybandwidthissaturated(Figure6). Therecompute rencythroughcopy-on-writesemantics,allowingbackground
operationstobuildnewindexviewswhilereaderscontinue
thresholdcontrolshowoftenAPSupdatesitsrecallestimate.
Wesetthisto1%,whichavoidsunnecessaryrecomputation onthecurrentonewithoutblocking.
| withnegligibleimpactonrecall(Table2). |     |     |     | 9 Conclusion |     |     |     |     |
| ------------------------------------- | --- | --- | --- | ------------ | --- | --- | --- | --- |
Thesplit/mergethresholdτsets
Maintenanceparameters.
ExperimentalresultsshowthatQuakereducesquerylatency
theminimumpredictedlatencyimprovementrequiredtotrig-
gerasplitordelete.Wesetτ=250ns.Lowervaluesincrease comparedtobaselineapproachesunderdynamicandskewed
workloads,withoutrequiringmanualtuning.Itachieveshigh
maintenancecostandmaycauseover-splitting;highervalues
recall,matchingtheperformanceofanoracleforsettingthe
canallowimbalancetopersist.Thesplitaccessscalingpa-
rameterαestimatesthedropinaccessfrequencyafterasplit. queryparameternprobe.Comparedtoexistingpartitionedin-
dexeslikeFaissandSCANN,Quakereducesquerylatencyby
| We fix α=0.9,whichworkedwellacross |     |     | allbenchmarks. |     |     |     |     |     |
| ---------------------------------- | --- | --- | -------------- | --- | --- | --- | --- | --- |
A)adaptivelymaintainingindexpartitionsandB)maximiz-
Ifmaintenancetuningisneeded,werecommendkeepingα
ingmemorybandwidthduringqueryprocessing.Compared
fixedandadjustingτ.Refinementiscontrolledbytwoparam-
|                            |     |     |                           | to graph | indexes like | SVS,HNSW,and | DiskANN,Quake |     |
| -------------------------- | --- | --- | ------------------------- | -------- | ------------ | ------------ | ------------- | --- |
| eters:therefinementradiusr |     |     | (numberofnearbypartitions |          |              |              |               |     |
f
considered)andthenumberofrefinementiterations.Weuse offers more efficientindexing andupdates while matching
orreducingquerylatency.Insummary,ourevaluationshows
oneiterationoverthe50nearestpartitions.Fromourablation
Quakeminimizesquerylatencywhilemeetingrecalltargets
study,disablingrefinementreducesmaintenancetimeby75%
ondynamicworkloadswithskewedaccesspatterns.
butincreasesquerylatencyandreducesrecall(Table7).The
|     |     |     |     | Acknowledgments |     | We would | like to thank | our shepherd, |
| --- | --- | --- | --- | --------------- | --- | -------- | ------------- | ------------- |
windowsizeforaccessfrequencystatisticsissetequaltothe
maintenanceinterval.Forexample,ifmaintenancerunsev- NitinAgrawal,andthereviewersfortheirvaluablefeedback
|     |     |     |     | andeffortsinmakingthisastrongerpaper. |     |     | Thisworkwas |     |
| --- | --- | --- | --- | ------------------------------------- | --- | --- | ----------- | --- |
ery100,000queries,thewindowalsospans100,000queries.
Smallerwindowsadaptfasterbutaremorevolatile. supported by NSF grant CNS-2237306,Apple Scholars in
|     |     |     |     | AIML PhD | Fellowship,and | UW-Madison | Hilldale | Under- |
| --- | --- | --- | --- | -------- | -------------- | ---------- | -------- | ------ |
Mostparametersarefixedacrossworkloads.Inpractice,
graduateResearchFellowship.Thisworkwasalsosupported
| only the initial | candidate | fraction | f and the maintenance |     |     |     |     |     |
| ---------------- | --------- | -------- | --------------------- | --- | --- | --- | --- | --- |
M
byDARPAunderthegrantAIEDARPA-PA-22-01.TheU.S.
thresholdτbenefitfromtuning;however,theirdefaultsare
Governmentisauthorizedtoreproduceanddistributereprints
sufficientfortheworkloadsweevaluated.
|     |     |     |     | forGovernmental | purposes | notwithstanding |     | any copyright |
| --- | --- | --- | --- | --------------- | -------- | --------------- | --- | ------------- |
notationthereon.Anyopinions,findings,andconclusionsor
8.2 DeploymentConsiderations
recommendationsexpressedinthismaterialarethoseofthe
Quake’sdesigncanbeextendedtosupportarangeofhard- authorsanddonotnecessarilyreflecttheviews,policies,or
wareanduse-casesthroughminorchangestothecostmodel endorsements,eitherexpressedorimplied,ofDARPAorthe
| andAPSlogic.Wereservetheseextensionsforfuturework. |     |     |     | U.S.Government. |     |     |     |     |
| -------------------------------------------------- | --- | --- | --- | --------------- | --- | --- | --- | --- |
166    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| References                 |     |     |                       |     |     |     | [12] HeliaHashemi,AasishPappu,MiTian,PraveenChan- |     |     |     |     |     |               |        |
| -------------------------- | --- | --- | --------------------- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | ------------- | ------ |
|                            |     |     |                       |     |     |     | dar,MouniaLalmas,andBenjaminCarterette.           |     |     |     |     |     |               | Neural |
| [1] Qdrant-VectorDatabase. |     |     | https://qdrant.tech/. |     |     |     |                                                   |     |     |     |     |     |               |        |
|                            |     |     |                       |     |     |     | instantsearchformusicandpodcast.                  |     |     |     |     |     | InProceedings |        |
ofthe27thACMSIGKDDConferenceonKnowledge
[2] Billion-scaleapproximatenearestneighborsearchchal-
Discovery&DataMining,pages2984–2992,2021.
| lenge: | Neurips’21 |     | competition | track. | https://big-ann- |     |     |     |     |     |     |     |     |     |
| ------ | ---------- | --- | ----------- | ------ | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
benchmarks.com/,2021. [13] Herve Jegou, Matthijs Douze, and Cordelia Schmid.
|                          |          |     |            |          |     |           | Productquantizationfornearestneighborsearch. |     |     |         |          |     |         | IEEE     |
| ------------------------ | -------- | --- | ---------- | -------- | --- | --------- | -------------------------------------------- | --- | --- | ------- | -------- | --- | ------- | -------- |
| [3] Vector               | database |     | for vector | search   | |   | pinecone. |                                              |     |     |         |          |     |         |          |
|                          |          |     |            |          |     |           | transactions                                 |     | on  | pattern | analysis | and | machine | intelli- |
| https://www.pinecone.io, |          |     | 2024.      | Accessed |     | on De-    |                                              |     |     |         |          |     |         |          |
gence,33(1):117–128,2010.
cember4,2023.
|                        |     |     |     |     |     |             | [14] Herve | Jégou, | Matthijs     |     | Douze,      | and | Cordelia | Schmid. |
| ---------------------- | --- | --- | --- | --- | --- | ----------- | ---------- | ------ | ------------ | --- | ----------- | --- | -------- | ------- |
| [4] Wikipedia:pageview |     |     |     |     |     | statistics. |            |        |              |     |             |     |          |         |
|                        |     |     |     |     |     |             | Product    |        | Quantization |     | for Nearest |     | Neighbor | Search. |
https://en.wikipedia.org/wiki/Wikipedia:Pageview_statistics, IEEE Transactions on Pattern Analysis and Machine
2024.
|     |     |     |     |     |     |     | Intelligence,33(1):117–128,January2011. |     |     |     |     |     |     | Conference |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------- | --- | --- | --- | --- | --- | --- | ---------- |
Name:IEEETransactionsonPatternAnalysisandMa-
| [5] Cecilia | Aguerrebere,Mark |     |     | Hildebrand,Ishwar |     | Singh |     |     |     |     |     |     |     |     |
| ----------- | ---------------- | --- | --- | ----------------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
chineIntelligence.
| Bhati,TheodoreWillke,andMarianoTepper. |     |     |     |     |     | Locally- |     |     |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
arXiv
adaptivequantizationforstreamingvectorsearch. [15] Alina Kuznetsova, Hassan Rom, Neil Alldrin, Jasper
preprintarXiv:2402.02044,2024. Uijlings,IvanKrasin,JordiPont-Tuset,ShahabKamali,
StefanPopov,MatteoMalloci,AlexanderKolesnikov,
| [6] Dmitry | Baranchuk, |     | Matthijs | Douze, | Yash | Upadhyay, |     |         |     |          |          |     |          |        |
| ---------- | ---------- | --- | -------- | ------ | ---- | --------- | --- | ------- | --- | -------- | -------- | --- | -------- | ------ |
|            |            |     |          |        |      |           | Tom | Duerig, | and | Vittorio | Ferrari. |     | The open | images |
andI.ZekiYalniz. DeDrift:RobustSimilaritySearch datasetv4:Unifiedimageclassification,objectdetection,
| underContentDrift,August2023. |     |     |     | arXiv:2308.02752 |     |     |                                                |     |     |     |     |     |               |     |
| ----------------------------- | --- | --- | --- | ---------------- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- | ------------- | --- |
|                               |     |     |     |                  |     |     | andvisualrelationshipdetectionatscale.         |     |     |     |     |     | International |     |
| [cs].                         |     |     |     |                  |     |     | JournalofComputerVision,128(7):1956–1981,March |     |     |     |     |     |               |     |
2020.
| [7] Qi | Chen, Bing | Zhao, | Haidong | Wang, | Mingqin | Li, |     |     |     |     |     |     |     |     |
| ------ | ---------- | ----- | ------- | ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ChuanjieLiu,ZengzhongLi,MaoYang,andJingdong [16] YongjaeLeeandWooChangKim.Conciseformulasfor
Wang. SPANN:Highly-efficientBillion-scaleApproxi- thesurfaceareaoftheintersectionoftwohyperspherical
| mateNearestNeighborSearch. |     |     |     |     |     |     | caps. | KAISTTechnicalReport,2014. |     |     |     |     |     |     |
| -------------------------- | --- | --- | --- | --- | --- | --- | ----- | -------------------------- | --- | --- | --- | --- | --- | --- |
[17] ViktorLeis,PeterBoncz,AlfonsKemper,andThomas
[8] MatthijsDouze,AlexandrGuzhva,ChengqiDeng,Jeff
Johnson,GergelySzilvasy,Pierre-EmmanuelMazaré, Neumann. Morsel-driven parallelism: a numa-aware
|                                          |     |     |     |     |     |     | queryevaluationframeworkforthemany-coreage. |     |     |     |     |     |     | In  |
| ---------------------------------------- | --- | --- | --- | --- | --- | --- | ------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| MariaLomeli,LucasHosseini,andHervéJégou. |     |     |     |     |     | The |                                             |     |     |     |     |     |     |     |
faisslibrary,2024. Proceedingsofthe2014ACMSIGMODInternational
|     |     |     |     |     |     |     | Conference |     | on  | Management |     | of Data, | SIGMOD | ’14, |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | ---------- | --- | -------- | ------ | ---- |
page743–754,NewYork,NY,USA,2014.Association
| [9] MihajloGrbovicandHaibinCheng. |     |     |     |     | Real-timeperson- |     |     |     |     |     |     |     |     |     |
| --------------------------------- | --- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
alizationusingembeddingsforsearchrankingatairbnb. forComputingMachinery.
InProceedingsofthe24thACMSIGKDDInternational
|     |     |     |     |     |     |     | [18] Conglong |     | Li, Minjia | Zhang, |     | David | G Andersen, | and |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ---------- | ------ | --- | ----- | ----------- | --- |
ConferenceonKnowledgeDiscovery&DataMining,
|     |     |     |     |     |     |     | YuxiongHe. |     | Improvingapproximatenearestneighbor |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ----------------------------------- | --- | --- | --- | --- | --- |
pages311–320,2018.
|     |     |     |     |     |     |     | searchthroughlearnedadaptiveearlytermination. |     |     |     |     |     |     | In  |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
Proceedingsofthe2020ACMSIGMODInternational
| [10] Ruiqi | Guo, | Philip | Sun, Erik | Lindgren, | Quan | Geng, |     |     |     |     |     |     |     |     |
| ---------- | ---- | ------ | --------- | --------- | ---- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
ConferenceonManagementofData,pages2539–2554,
| DavidSimcha,FelixChern,andSanjivKumar.           |     |                                     |     |     |     | Accel- |       |     |     |     |     |     |     |     |
| ------------------------------------------------ | --- | ----------------------------------- | --- | --- | --- | ------ | ----- | --- | --- | --- | --- | --- | --- | --- |
| eratingLarge-ScaleInferencewithAnisotropicVector |     |                                     |     |     |     |        | 2020. |     |     |     |     |     |     |     |
| Quantization.                                    |     | InProceedingsofthe37thInternational |     |     |     |        |       |     |     |     |     |     |     |     |
[19] ShengqiaoLi.Conciseformulasfortheareaandvolume
| Conference         |     | on Machine | Learning,       | pages | 3887–3896. |     |                       |     |     |     |                           |     |     |     |
| ------------------ | --- | ---------- | --------------- | ----- | ---------- | --- | --------------------- | --- | --- | --- | ------------------------- | --- | --- | --- |
|                    |     |            |                 |       |            |     | ofahypersphericalcap. |     |     |     | AsianJournalofMathematics |     |     |     |
| PMLR,November2020. |     |            | ISSN:2640-3498. |       |            |     |                       |     |     |     |                           |     |     |     |
&Statistics,4(1):66–70,2010.
[11] MalayHaldar,MustafaAbdool,PrashantRamanathan,
|     |            |       |          |       |      |        | [20] LibTorch: |     |     | PyTorch |     |     | C++ | API. |
| --- | ---------- | ----- | -------- | ----- | ---- | ------ | -------------- | --- | --- | ------- | --- | --- | --- | ---- |
| Tao | Xu, Shulin | Yang, | Huizhong | Duan, | Qing | Zhang, |                |     |     |         |     |     |     |      |
https://pytorch.org/cppdocs.
NickBarrow-Williams,BradleyCTurnbull,BrendanM
Collins,etal. Applyingdeeplearningtoairbnbsearch. [21] DavidCLiu,StephanieRogers,RaymondShiau,Dmitry
InProceedingsofthe25thACMSIGKDDInternational Kislyuk,KevinCMa,ZhigangZhong,JennyLiu,and
ConferenceonKnowledgeDiscovery&DataMining, YushiJing. Relatedpinsatpinterest:Theevolutionof
pages1927–1935,2019. areal-worldrecommendersystem. InProceedingsof
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    167

the 26thinternationalconference on worldwide web [32] Shumpei Okura, Yukihiro Tagami, Shingo Ono, and
companion,pages583–592,2017. Akira Tajima. Embedding-based news recommenda-
|              |      |      |      |      |             |       | tionformillionsofusers. |     |     |     | InProceedingsofthe23rd |     |     |
| ------------ | ---- | ---- | ---- | ---- | ----------- | ----- | ----------------------- | --- | --- | --- | ---------------------- | --- | --- |
| [22] Zhuoran | Liu, | Leqi | Zou, | Xuan | Zou, Caihua | Wang, |                         |     |     |     |                        |     |     |
ACMSIGKDDinternationalconferenceonknowledge
BiaoZhang,DaTang,BolinZhu,YijieZhu,PengWu, discoveryanddatamining,pages1933–1942,2017.
| Ke  | Wang,and | Youlong | Cheng. | Monolith: |     | Real time |     |     |     |     |     |     |     |
| --- | -------- | ------- | ------ | --------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
recommendationsystemwithcollisionlessembedding [33] Aditya Pal, Chantat Eksombatchai, Yitong Zhou,
table.In5thWorkshoponOnlineRecommenderSystems BoZhao,CharlesRosenberg,andJureLeskovec.Pinner-
andUserModeling(ORSUM2022),inconjunctionwith sage:Multi-modaluserembeddingframeworkforrec-
| the   | 16th ACM | Conference |     | on RecommenderSystems, |     |     |                                             |     |     |     |                        |     |     |
| ----- | -------- | ---------- | --- | ---------------------- | --- | --- | ------------------------------------------- | --- | --- | --- | ---------------------- | --- | --- |
|       |          |            |     |                        |     |     | ommendationsatpinterest.                    |     |     |     | InProceedingsofthe26th |     |     |
| 2022. |          |            |     |                        |     |     | ACMSIGKDDInternationalConferenceonKnowledge |     |     |     |                        |     |     |
Discovery&DataMining,pages2311–2320,2020.
| [23] Vasilis | Mageirakos,Bowen |        |        | Wu,andGustavo |       | Alonso.  |     |     |     |     |     |     |     |
| ------------ | ---------------- | ------ | ------ | ------------- | ----- | -------- | --- | --- | --- | --- | --- | --- | --- |
| Cracking     |                  | vector | search | indexes.      | arXiv | preprint |     |     |     |     |     |     |     |
[34] JeffreyPound,FlorisChabert,ArjunBhushan,Ankur
arXiv:2503.01823,2025. Goswami,AnilPacaci,andShihaburRahmanChowd-
|                                 |     |     |     |     |                    |     | hury. | Micronn:Anon-devicedisk-residentupdatable |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | --- | ------------------ | --- | ----- | ----------------------------------------- | --- | --- | --- | --- | --- |
| [24] YuA.MalkovandD.A.Yashunin. |     |     |     |     | Efficientandrobust |     |       |                                           |     |     |     |     |     |
vectordatabase.arXivpreprintarXiv:2504.05573,2025.
approximatenearestneighborsearchusinghierarchical
navigablesmallworldgraphs.IEEETrans.PatternAnal.
[35] IraklisPsaroudakis,TobiasScheuer,NormanMay,Ab-
Mach.Intell.,42(4):824–836,April2020. delkader Sellami,and Anastasia Ailamaki. Adaptive
numa-awaredataplacementandtaskschedulingforana-
[25] JasonMohoney,AnilPacaci,ShihaburRahmanChowd-
|     |     |     |     |     |     |     | lyticalworkloadsinmain-memorycolumn-stores. |     |     |     |     |     | Proc. |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------- | --- | --- | --- | --- | --- | ----- |
hury,UmarFarooqMinhas,JefferyPound,CedricReng-
VLDBEndow.,10(2):37–48,October2016.
gli,NimaReyhani,IhabFIlyas,TheodorosRekatsinas,
and Shivaram Venkataraman. Incremental ivf index [36] An Qin, Mengbai Xiao, Yongwei Wu, Xinjie Huang,
| maintenanceforstreamingvectorsearch. |     |     |     |     | arXivpreprint |     |                   |     |     |                                |     |     |     |
| ------------------------------------ | --- | --- | --- | --- | ------------- | --- | ----------------- | --- | --- | ------------------------------ | --- | --- | --- |
|                                      |     |     |     |     |               |     | andXiaodongZhang. |     |     | Mixer:efficientlyunderstanding |     |     |     |
arXiv:2411.00970,2024.
|     |     |     |     |     |     |     | andretrievingvisualcontentatweb-scale. |     |     |     |     |     | Proceedings |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------------- | --- | --- | --- | --- | --- | ----------- |
[26] JasonMohoney,AnilPacaci,ShihaburRahmanChowd- oftheVLDBEndowment,14(12):2906–2917,2021.
| hury, | Ali Mousavi, |     | Ihab F. | Ilyas, | Umar Farooq | Min- |     |     |     |     |     |     |     |
| ----- | ------------ | --- | ------- | ------ | ----------- | ---- | --- | --- | --- | --- | --- | --- | --- |
[37] AlecRadford,JongWookKim,ChrisHallacy,Aditya
| has,JeffreyPound,andTheodorosRekatsinas. |     |     |     |     |     | High- |     |     |     |     |     |     |     |
| ---------------------------------------- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
Ramesh,GabrielGoh,SandhiniAgarwal,GirishSastry,
Throughput Vector Similarity Search in Knowledge AmandaAskell,PamelaMishkin,JackClark,Gretchen
| Graphs. | Proceedings |     | ofthe | ACM | on Managementof |     |                           |     |     |     |                         |     |     |
| ------- | ----------- | --- | ----- | --- | --------------- | --- | ------------------------- | --- | --- | --- | ----------------------- | --- | --- |
|         |             |     |       |     |                 |     | Krueger,andIlyaSutskever. |     |     |     | Learningtransferablevi- |     |     |
Data,1(2):1–25,June2023.
sualmodelsfromnaturallanguagesupervision,2021.
| [27] Jason | Mohoney, |     | Devesh | Sarda, | Mengze | Tang, Shi- |            |        |       |         |             |     |        |
| ---------- | -------- | --- | ------ | ------ | ------ | ---------- | ---------- | ------ | ----- | ------- | ----------- | --- | ------ |
|            |          |     |        |        |        |            | [38] Aditi | Singh, | Suhas | Jayaram | Subramanya, |     | Ravis- |
haburRahmanChowdhury,AnilPacaci,IhabF.Ilyas,
hankarKrishnaswamy,andHarshaVardhanSimhadri.
| Theodoros |     | Rekatsinas, | and | Shivaram | Venkataraman. |     |     |     |     |     |     |     |     |
| --------- | --- | ----------- | --- | -------- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Freshdiskann:Afastandaccurategraph-basedannin-
Quake:Adaptiveindexingforvectorsearch(technical
|          |                                     |     |     |     |     |     | dex | for streaming |     | similarity | search. | arXiv | preprint |
| -------- | ----------------------------------- | --- | --- | --- | --- | --- | --- | ------------- | --- | ---------- | ------- | ----- | -------- |
| report). | arXivpreprintarXiv:2506.03437,2025. |     |     |     |     |     |     |               |     |            |         |       |          |
arXiv:2105.09613,2021.
[28] JasonMohoney,RogerWaleffe,HenryXu,Theodoros
[39] SuhasJayaramSubramanya,Devvrit,RohanKadekodi,
| Rekatsinas, |                                        | and Shivaram |                  | Venkataraman. |     | Marius:      |                              |     |                                          |     |     |                  |         |
| ----------- | -------------------------------------- | ------------ | ---------------- | ------------- | --- | ------------ | ---------------------------- | --- | ---------------------------------------- | --- | --- | ---------------- | ------- |
|             |                                        |              |                  |               |     |              | Ravishankar                  |     | Krishaswamy,                             |     | and | Harsha           | Vardhan |
| Learning    | massive                                |              | graph embeddings |               | on  | a single ma- |                              |     |                                          |     |     |                  |         |
|             |                                        |              |                  |               |     |              | Simhadri.                    |     | DiskANN:fastaccuratebillion-pointnearest |     |     |                  |         |
| chine.      | In15th{USENIX}SymposiumonOperatingSys- |              |                  |               |     |              |                              |     |                                          |     |     |                  |         |
|             |                                        |              |                  |               |     |              | neighborsearchonasinglenode. |     |                                          |     |     | CurranAssociates |         |
temsDesignandImplementation({OSDI}21),pages
Inc.,RedHook,NY,USA,2019.
533–549,2021.
|     |     |     |     |     |     |     | [40] Philip | Sun,David |     | Simcha,Dave | Dopson,Ruiqi |     | Guo, |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --------- | --- | ----------- | ------------ | --- | ---- |
[29] moodycamel::ConcurrentQueue.
|     |     |     |     |     |     |     | andSanjivKumar. |     |     | Soar:Improvedindexingforapprox- |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | ------------------------------- | --- | --- | --- |
https://github.com/cameron314/concurrentqueue.
|     |     |     |     |     |     |     | imatenearestneighborsearch. |     |     |     | InNeuralInformation |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | ------------------- | --- | --- |
[30] SimSIMD. https://github.com/ashvardanian/SimSIMD. ProcessingSystems,2023.
[31] JiongkangNi,XiaoliangXu,YuxiangWang,CanLi,Jia- [41] RogerWaleffe,JasonMohoney,TheodorosRekatsinas,
jieYao,ShihaiXiao,andXuecangZhang. DiskANN++: and Shivaram Venkataraman. Mariusgnn: Resource-
EfficientPage-basedSearchoverIsomorphicMapped efficientout-of-coretrainingofgraphneuralnetworks.
Graph Index using Query-sensitivity Entry Vertex, InACMSIGOPSEuropeanConferenceonComputer
| November2023. |     | arXiv:2310.00402[cs]. |     |     |     |     | Systems(EuroSys),2023. |     |     |     |     |     |     |
| ------------- | --- | --------------------- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- |
168    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| [42] Jianguo | Wang, | Xiaomeng | Yi, Rentong | Guo, Hai | Jin, | Scope |     |     |     |     |     |
| ------------ | ----- | -------- | ----------- | -------- | ---- | ----- | --- | --- | --- | --- | --- |
PengXu,ShengjunLi,XiangyuWang,XiangzhouGuo,
ThisartifactenablesvalidationofQuake’scoreexperimental
| ChengmingLi,XiaohaiXu,etal. |     |     |     | Milvus:Apurpose- |     |     |     |     |     |     |     |
| --------------------------- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
findings,suchasthoserelatedtoAdaptivePartitionScanning
| builtvectordatamanagementsystem. |     |     |     | InProceedings |     |     |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- |
(APS),NUMA-awaresearching,andmaintenancepolicies.
ofthe2021InternationalConferenceonManagement
Refertotheartifact’sREADMEforspecificexperiments.
ofData,pages2614–2627,2021.
Contents
[43] JizheWang,PipeiHuang,HuanZhao,ZhiboZhang,Bin- The artifact includes Python scripts (e.g.,
qiangZhao,andDikLunLee. Billion-scalecommodity experiment_runner.py, individual experiment run.py
embeddingfore-commercerecommendationinalibaba.
files),systeminstallationscripts(install.sh),experiment
InProceedingsofthe24thACMSIGKDDInternational configurations(configs/),Condaenvironmentfiles,andthe
ConferenceonKnowledgeDiscovery&DataMining, paperPDF.TheREADMEdetailsthefulldirectorystructure
pages839–848,2018.
andcontents.
Hosting
| [44] Chuangxian | Wei, | Bin | Wu, Sheng | Wang, Renjie | Lou, |     |     |     |     |     |     |
| --------------- | ---- | --- | --------- | ------------ | ---- | --- | --- | --- | --- | --- | --- |
TheartifactispartoftheQuakerepositoryintheosdi2025
| ChaoqunZhan,FeifeiLi,andYuanzheCai. |     |     |     | Analyticdb- |     |     |     |     |     |     |     |
| ----------------------------------- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
v:Ahybridanalyticalenginetowardsqueryfusionfor branch. located at https://github.com/marius-team/
structured and unstructured data. Proceedings of the quake/tree/osdi2025/test/experiments/osdi2025.
VLDBEndowment,13(12):3152–3165,2020. Usethelatestcommitonthisbranch.
Requirements
[45] YumingXu,HengyuLiang,JinLi,ShuotaoXu,QiChen,
Python3.9+andCondaarerequired.TestedonLinux(Ubuntu
QianxiZhang,ChengLi,ZiyueYang,FanYang,Yuqing
Yang,PengCheng,andMaoYang. SPFresh:Incremen- 22.04).Someexperiments(e.g.,NUMAevaluations)require
|                                                |     |     |     |     |     | a machine with | NUMA | for meaningful | reproduction. |     | The |
| ---------------------------------------------- | --- | --- | --- | --- | --- | -------------- | ---- | -------------- | ------------- | --- | --- |
| talIn-PlaceUpdateforBillion-ScaleVectorSearch. |     |     |     |     | In  |                |      |                |               |     |     |
install.shscriptlistssystem-leveldependencies.Referto
Proceedingsofthe29thSymposiumonOperatingSys-
temsPrinciples,SOSP’23,pages545–561,NewYork, theREADMEforcomprehensiverequirements.
| NY,USA,October |     | 2023. | Association | for Computing |     | A.1 Installation |     |     |     |     |     |
| -------------- | --- | ----- | ----------- | ------------- | --- | ---------------- | --- | --- | --- | --- | --- |
Machinery.
Followthedetailedinstallationinstructionsintheartifact’s
|     |     |     |     |     |     | README. | Options | include | a comprehensive | setup | using |
| --- | --- | --- | --- | --- | --- | ------- | ------- | ------- | --------------- | ----- | ----- |
[46] BishanYang,Wen-tauYih,XiaodongHe,JianfengGao,
install.shoraQuake-onlyCondaenvironmentsetup.
| andLiDeng.                       | Embeddingentitiesandrelationsforlearn- |     |     |               |     |                        |     |     |     |     |     |
| -------------------------------- | -------------------------------------- | --- | --- | ------------- | --- | ---------------------- | --- | --- | --- | --- | --- |
|                                  |                                        |     |     |               |     | A.2 ExperimentWorkflow |     |     |     |     |     |
| ingandinferenceinknowledgebases. |                                        |     |     | arXivpreprint |     |                        |     |     |     |     |     |
arXiv:1412.6575,2014.
|     |     |     |     |     |     | Allexperiments           | are launchedvia |             | experiment_runner.py |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------ | --------------- | ----------- | -------------------- | --- | --- |
|     |     |     |     |     |     | from the repositoryroot. |                 | Experiments | willtypicallydown-   |     |     |
[47] Qianxi Zhang,Shuotao Xu,Qi Chen,Guoxin Sui,Ji- load and prepare required datasets if not found locally.
| adong | Xie, Zhizhen | Cai, | Yaoqi | Chen, Yinxuan | He, |     |     |     |     |     |     |
| ----- | ------------ | ---- | ----- | ------------- | --- | --- | --- | --- | --- | --- | --- |
Experimentsarerunasfollows:
Yuqing Yang, Fan Yang, et al. {VBASE}: Unifying python3 -m test.experiments.osdi2025.experiment_runner
onlinevectorsimilaritysearchandrelationalqueriesvia -experiment kick_the_tires - config sift1m
relaxedmonotonicity. In17thUSENIXSymposiumon After execution,experiments print status updates and save
OperatingSystemsDesignandImplementation(OSDI results(e.g.,CSVfiles,plots)toanoutputdirectory,asindi-
23),pages377–395,2023.
catedintheconsoleoutput.Theartifact’sREADMEprovides
thecompletecommandstructure,detailedexplanationsofall
[48] ZiliZhang,ChaoJin,LinpengTang,XuanzheLiu,and parameters(including-output-dir),furtherexamples,and
| XinJin. | Fast,approximatevectorqueriesonverylarge |     |     |     |     |     |     |     |     |     |     |
| ------- | ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
afullsummaryofavailableexperimentswiththeirspecific
| unstructureddatasets. |     | In20thUSENIXSymposiumon |     |     |     | configurations. |     |     |     |     |     |
| --------------------- | --- | ----------------------- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- |
NetworkedSystemsDesignandImplementation(NSDI
23),pages995–1011,2023.
A ArtifactAppendix
Abstract
| This artifact | provides     | the experimental |            | setup for Quake | to  |     |     |     |     |     |     |
| ------------- | ------------ | ---------------- | ---------- | --------------- | --- | --- | --- | --- | --- | --- | --- |
| reproduce     | key results. | See the          | artifact’s | README forfull  |     |     |     |     |     |     |     |
details.
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    169