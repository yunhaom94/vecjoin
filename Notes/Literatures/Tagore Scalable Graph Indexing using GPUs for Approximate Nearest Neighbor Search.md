Scalable Graph Indexing using GPUs
for Approximate Nearest Neighbor Search
ZhonggenLi XiangyuKe Yifan Zhu
ZhejiangUniversity ZhejiangUniversity ZhejiangUniversity
zgli@zju.edu.cn xiangyu.ke@zju.edu.cn xtf_z@zju.edu.cn
BochengYu BaihuaZheng Yunjun Gao
ZhejiangUniversity SingaporeManagementUniversity ZhejiangUniversity
yubc@zju.edu.cn bhzheng@smu.edu.sg gaoyj@zju.edu.cn
Abstract Tree-based C S on tr s a tr te u g c i t e i s on Description Rep In r s e t s a e n n c ta es tive
Approximatenearestneighborsearch(ANNS)inhigh-dimensional Indexes for Hash-based Divide-and-conquer s R u e b c g u r r a s p iv h e s l a y n g d e n m e e r r a g te e S G E P G L T N A PI N G S ( ( ( G C C P P P U U U ) ) ) [ [ [ 2 1 6 3 1 ] ] ]
v o e u c s t m or e s th p o ac d e s s h h a a v s e a be w e i n d p e r r o a p n o g s e ed of to re h a a l- n w d o le rl A d N a N pp S l e ic ffi at c i i o e n n s t . ly N , u w m h e il r e - ANNS Graph-based Increment-based Conti i n n u to o u t s h l e y i i n n d s e e x rt data G H N A N S N S W N W ( S C ( ( C G P P U P U U )[ ) 4 [ ) 4 [ 2 7 3 ] 2 ] ]
graph-basedindexeshavegainedprominenceduetotheirhighac- Quantization-based Refinement-based Ini p ti r a u l n iz e e i t a t g o r r a e p f h in a e nd C V A N am G S a G R n ( A a C ( ( C P G U P P U ) U [ ) 1 ) [ 8 [ 2 4 ] 8 8 ] ]
curacyand efficiency. However, theindexing overhead ofgraph-
based indexes remains substantial. With exponential growth in Figure 1: Categories of Index construction methods for
data volume and increasing demands for dynamic index adjust- ANNS.Tagorefocusesontherefinement-basedmethods.
ments,thisoverhead continuestoescalate,posingacriticalchal-
lenge.
In this paper,we introduce Tagore, a fasT library accelerated
byGPUsforgraphindexing,whichhaspowerfulcapabilitiesof 1 Introduction
constructingrefinement-basedgraphindexessuchasNSGandVa-
Approximate nearest neighbor search (ANNS) is a fundamental
mana.WefirstintroduceGNN-Descent,aGPU-specificalgorithm
component in database systems [19, 20, 50, 56], with numerous
forefficientk-NearestNeighbor(k-NN)graphinitialization.GNN-
real-worldapplications,includinginformationretrieval[21,33,35],
Descent speedsupthesimilaritycomparisonbyatwo-phasede-
retrieval-augmentedgeneration[5,30,71],andrecommendation[44,
scentprocedureandenableshighlyparallelizedneighborupdates.
51]. To efficiently respond to user queries, various ANNS meth-
Next, aiming to support various k-NN graph pruning strategies,
odshavebeenexplored,includingtree-basedmethods[15,43,74],
weformulateauniversal pruningproceduretermedCFSand de-
hash-basedmethods[41,75],quantization-basedmethods[4,20],
visetwogeneralizedGPUkernelsforparallelprocessingcomplex
andgraph-basedmethods[18,43,52].Amongthese,graph-based
dependenciesinneighborrelationships.Forlarge-scaledatasetsex-
methodshavegainedsignificantpopularityduetoremarkableper-
ceedingGPUmemorycapacity,weproposeanasynchronousGPU-
formance in both efficiency and accuracy [6, 50, 65]. As shown
CPU-diskindexingframeworkwithacluster-awarecachingmech-
in Figure 1, divide-and-conquer,increment-based,and refinement-
anismtominimizetheI/Opressureonthedisk.Extensiveexperi-
basedmethodsarethethreeprimaryindexconstructionmethods
mentson7real-worlddatasetsexhibitthatTagoreachieves1.32×
for graph-based index. Recent studies highlight that refinement-
to112.79×speedupwhilemaintainingtheindexquality.
based indexes (e.g., NSG [18], Vamana [28], NSSG [17]) demon-
stratesuperiorefficiency in bothconstructionand query[3, 65].
ACMReferenceFormat: Thesemethodsarewidelyadoptedincommercialvectordatabases
ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYun- likeMilvus[62],aswellasbycompaniessuchasMicrosoftandAl-
junGao.2026.ScalableGraphIndexingusingGPUsforApproximateNear- ibaba[18,28,55].
estNeighborSearch.InProceedingsofthe2026InternationalConferenceon
Numerous research initiatives focus on enhancing query effi-
ManagementofData(SIGMOD’26).ACM,Bengaluru,BLR,India,15pages.
ciency ofANNS, treating index constructionas an offline proce-
https://doi.org/XXXXXXX.XXXXXXX
durewithlimitedoptimization[19,34,40].However,efficientin-
dex construction has become increasingly crucial for real-world
applications[63,70].Withtheexponentialgrowthofdata,thevol-
umeofvectordatarequiredforretrievalinenterprise-scaledatabases
Permissiontomakedigitalorhardcopiesofallorpartofthisworkforpersonalor
has surpassed the billion-scale threshold, as seen in Meta’s im-
classroomuseisgrantedwithoutfeeprovidedthatcopiesarenotmadeordistributed
forprofitorcommercialadvantageandthatcopiesbearthisnoticeandthefullcita- agedatabases[31]andTaobao’sproductvectors[18].Asaresult,
tiononthefirstpage.Copyrightsforcomponentsofthisworkownedbyothersthan constructing a graph-based index has become increasingly time-
theauthor(s)mustbehonored.Abstractingwithcreditispermitted.Tocopyother-
consuming,requiringdozensofhourstobuildanindexonbillion-
wise,orrepublish,topostonserversortoredistributetolists,requirespriorspecific
permissionand/orafee.Requestpermissionsfrompermissions@acm.org. scaledatasets[28].Theoverheadisinsufficientforindustrialneeds,
SIGMOD’26,May31–June05,2026,Bengaluru,India wherenightlyindexreconstructionisnecessarytomaintainboth
©2026Copyrightheldbytheowner/author(s).PublicationrightslicensedtoACM.
accuracyandefficiency. Furthermore,embeddingmodelsarefre-
ACMISBN978-1-4503-XXXX-X/18/06
https://doi.org/XXXXXXX.XXXXXXX quentlyupdatedtoalignwithevolvingrequirements,andvectors
5202
guA
31
]BD.sc[
2v44780.8052:viXra

SIGMOD’26,May31–June05,2026,Bengaluru,India ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao
GPU-optimizedpruningstrategythatimprovespruningefficiency.
| NSG | Initialization (58.9%) |     |     | Pruning (41.1%) |     |     |     |     |     |     |     |     |     |     |
| --- | ---------------------- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
However,itsinitializationphaseremainsabottleneck,evenwhen
leveragingthestate-of-the-artGPU-acceleratedNN-Descentalgo-
| CAGRA | Initialization (84.8%) |     |     | Pruning (15.2%) |     |     |     |     |     |     |     |     |     |     |
| ----- | ---------------------- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
rithm[61].AlthoughGPUsexcelatparalleldistancecomputation
1s 10s 100s duringNN-Descent,theircomputationaladvantagesdiminishasit-
(a) Time breakdown of NSG and CAGRA. erationconvergenceslows,coupledwithpersistentoverheadfrom
frequentneighborupdates.Theseupdatesinvolveextensivemem-
| Initialization |     |       | 2313M |     |     |     |           |                     |     |                                    |                   |     |     |              |
| -------------- | --- | ----- | ----- | --- | --- | --- | --------- | ------------------- | --- | ---------------------------------- | ----------------- | --- | --- | ------------ |
|                |     |       |       |     |     |     | oryaccess | and synchronization |     |                                    | locks,reducingGPU |     |     | parallelism. |
|                |     |       |       |     |     |     | Thus,slow | convergence         | and | frequentneighborupdatesarecritical |                   |     |     |              |
| Pruning        |     | 1285M |       |     |     |     |           |                     |     |                                    |                   |     |     |              |
factorshinderingtheefficiencyoftheinitializationphaseonGPUs.
1000M 2000M Followinginitialization,thediversityofpruningstrategiescom-
(b) Memory overhead of NSG. plicatesthedesignofaunifiedaccelerationframework.Moreover,
pruningstrategiessuchasNSG[18],NSSG[17]andVamana[28]
Figure2:Timebreakdown(a)andmemoryusage(b)ofrep-
|     |     |     |     |     |     |     | require the | serial | computation |     | of complex | neighbor | dependencies, |     |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ------ | ----------- | --- | ---------- | -------- | ------------- | --- |
resentativerefinement-basedmethods,NSG(CPU)andCA-
whereneighborsneedtobegraduallyinsertedintotheneighbor
GRA(GPU),ondatasetSIFT1.
list.Thisserialcomputationproveschallengingtoparallelizeeffec-
tivelyonGPUs.Furthermore,asillustratedinFigure2(b),thehigh
memoryfootprintofrefinement-basedmethodsmakesitdifficult
aredynamicallyinsertedordeleted[55,68].Althoughrecentstud-
forGPUstohandlelarge-scaledatasetsduetotheirlimitedmem-
| ieshaveinvestigated |     | in-placeindexupdates,thesemethodstypi- |     |     |     |     |     |     |     |     |     |     |     |     |
| ------------------- | --- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
orycapacity.ThisoftennecessitatesGPU-CPU-diskcoordination,
callysuffera5%-10%accuracydegradationafterseveralupdatecy-
leadingtoexcessivediskI/O,whichfurtherdegradesperformance.
cles[63].Consequently,periodicindexrebuildingremainsacom-
Consequently,efficientlyindexingbillion-scaledatasetswithlimited
monstrategytobalanceefficiencyandqueryaccuracy[66].
GPUmemoryandorchestratingthecooperationbetweenCPU,GPU,
| Recent | research | has proposed | various | optimized |     | solutions to |     |     |     |     |     |     |     |     |
| ------ | -------- | ------------ | ------- | --------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
anddiskpresentsanothersignificantchallenge.
| address the | inefficiency | of graph | index | construction |     | on modern |     |     |     |     |     |     |     |     |
| ----------- | ------------ | -------- | ----- | ------------ | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
Toaddressthesechallenges,wepresentTagore,anefficientand
CPUs[22,47,63,70,78].However,theconstructionoverheadre-
scalableGPU-acceleratedlibrarythatincorporatesnoveloptimiza-
mainssignificantonCPUs.Forinstance,constructingin-memory
|     |     |     |     |     |     |     | tionsforinitialization,pruning, |     |     |     | and large-scaleindexing. |     |     | Tagore |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------- | --- | --- | --- | ------------------------ | --- | --- | ------ |
indexesfordatasetsof1Bvectorsstillrequiresmorethan10hours,
whichremainsunsatisfactoryintermsofefficiency[22,63]. offersuser-friendlyPythonAPIs,enablingseamlessintegrationof
GPUaccelerationintoindexconstructionworkflows.InTagore,we
| Tofurtherenhance |     | efficiency,somestudieshaveexploredthe |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | ------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
introduceGNN-Descent,atwo-phasealgorithmdesignedtoaccel-
accelerationofgraph-basedindexconstructionusingGPUs[23,48,
erateconvergenceandsupportlock-freeneighborupdates(§4).In
61,72].WhileGPU-basedmethodsoutperformCPU-basedmeth-
thefirstphase,adjacentnodesshareabatchofsamplestoexploit
ods,thefullpotentialofGPUsremainslargelyuntapped,restrict-
ing their widespread applicability. For example, GANNS [72] in- GPU parallelism, facilitating efficient neighbor list initialization.
Thesecondphaseemploysnode-specificsamplingforfine-grained
cursadditionalmergingoverheadwhenparallelizingtheindexcon-
|     |     |     |     |     |     |     | neighbor | refinement, | reducing |     | computational |     | redundancy. | Both |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | -------- | --- | ------------- | --- | ----------- | ---- |
structionofHNSWonGPUs.Increment-basedmethods(e.g.,HNSW
|                |                                   |            |             |     |                   |     | phases utilize | a               | lock-free | merging   | strategy | to       | update | neighbors,   |
| -------------- | --------------------------------- | ---------- | ----------- | --- | ----------------- | --- | -------------- | --------------- | --------- | --------- | -------- | -------- | ------ | ------------ |
| and NSW),      | whichrequiresequentiallyinserting |            |             |     | nodestoensure     |     |                |                 |           |           |          |          |        |              |
|                |                                   |            |             |     |                   |     | eliminating    | synchronization |           | overhead. |          | To unify | the    | acceleration |
| index quality, | are not                           | inherently | well-suited |     | for parallelizing | on  |                |                 |           |           |          |          |        |              |
ofvariouspruningstrategies,weproposetheCFS(Collect-Filter-
GPUs.Incontrast,refinement-basedmethods,particularlythecore
|     |     |     |     |     |     |     | Store) framework, |     | which | decomposes |     | pruning | into | three modu- |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | ----- | ---------- | --- | ------- | ---- | ----------- |
components-initialization(typicallyviaNN-Descent[14])andprun-
|     |     |     |     |     |     |     | larstages: | 1)collecting | candidateneighbors,2)filtering |     |     |     |     | basedon |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------------ | ------------------------------ | --- | --- | --- | --- | ------- |
ing(oftenusingtheRelativeNeighborhoodGraphstrategy[43])-
pruningstrategies,and3)storingoptimizedneighbors(§5.1).Ad-
arenaturallyparallelizableduetotheirdatadecoupling,offering
|     |     |     |     |     |     |     | ditionally, | we develop | two | specialized |     | GPU | kernels | for the CFS |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | --- | ----------- | --- | --- | ------- | ----------- |
significantpotentialforacceleration.However,existingstudiesof
|     |     |     |     |     |     |     | framework:1)aparallelincrementkernel |     |     |     |     | forcomputingcomplex |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------ | --- | --- | --- | --- | ------------------- | --- | --- |
acceleratingrefinement-basedmethodsusingGPUshavefailedto
|                      |     |              |     |          |       |          | neighbor | dependencies, |     | and 2) | a parallel | balance | kernel | for dis- |
| -------------------- | --- | ------------ | --- | -------- | ----- | -------- | -------- | ------------- | --- | ------ | ---------- | ------- | ------ | -------- |
| achieve satisfactory |     | performance. | For | example, | CAGRA | [48] op- |          |               |     |        |            |         |        |          |
tributingunevencomputationtasksacrossGPUthreads(§5.2).For
| timizes the | pruning | process | but leaves | graph | initialization | as a |             |           |     |        |                 |     |              |     |
| ----------- | ------- | ------- | ---------- | ----- | -------------- | ---- | ----------- | --------- | --- | ------ | --------------- | --- | ------------ | --- |
|             |         |         |            |       |                |      | large-scale | datasets, | we  | design | an asynchronous |     | GPU-CPU-disk |     |
bottleneck.Additionally,mostexistingGPU-basedmethodsfocus
frameworkthatdecouplescomputation,merging,andpersistence
onacceleratingtheconstructionofspecificindexesordesigning
tasks(§6.1).ThisframeworkenablescontinuousGPUprocessing
customizedindexestailoredforGPUs,oftenlackingsupportfora
|     |     |     |     |     |     |     | of graph | construction | subtasks, |     | while | the CPU | asynchronously |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------------ | --------- | --- | ----- | ------- | -------------- | --- |
broaderrangeofmainstreamgraphindexes[23,48,72].Scalability
mergespartialindexesandthediskhandleslarge-scaledataper-
withlargedatasetsalsoremainsachallenge[32,60,76].
|           |            |     |                |     |         |             | sistence.        | To mitigate | I/O                    | times, | we introducea |     | clustering-aware   |     |
| --------- | ---------- | --- | -------------- | --- | ------- | ----------- | ---------------- | ----------- | ---------------------- | ------ | ------------- | --- | ------------------ | --- |
| To better | understand | the | inefficiencies | in  | current | refinement- |                  |             |                        |        |               |     |                    |     |
|           |            |     |                |     |         |             | cachingmechanism |             | thatprioritizesmerging |        |               |     | operationsforover- |     |
based methods,weprofilethetimebreakdownandmemorycon-
lappingnodeclusters,significantlyreducingredundantdiskI/O(§6.2).
sumptionofNSGandCAGRA.AsshowninFigure2(a),NSGex-
hibitssubstantialoverheadinboththeinitializationandpruning Insummary,thispapermakesthefollowingcontributions.
phases.CAGRAacceleratesindexingontheGPUandintroducesa
1ForFigure2(b),CAGRAshowsasimilartrendof2434MmemoryusageontheGPU.

ScalableGraphIndexingusingGPUsforApproximateNearestNeighborSearch SIGMOD’26,May31–June05,2026,Bengaluru,India
• Two-phase parallelized graph construction. We introduce a 2.2 IndexingAcceleration
two-phaseconstructionalgorithmtoaccelerateconvergence Indexing acceleration on CPUs. Computational inefficiencies
andenablelock-freeneighborupdateswithhighparallelism.
ingraphindexinghavedrivenresearchtowardreducingcomputa-
• Refinement-basedpruningacceleration.Supportedbytwospe-
tionalcosts.ExistingCPU-basedaccelerationapproachesfallinto
cializedGPUkernelsforefficientserialandunbalancedcom- threecategories.Thefirsttypeaimstoredesigntheindexstructure
putation,weproposeaunifiedpipelinetoacceleraterefinement-
tooptimizethetimecomplexityofsearch[47,52,70,78],whilethe
basedpruning.
secondtypeattemptstoreducethedistancecomputationoverhead
• AsynchronousGPU-CPU-diskframework.Wedesignanasyn- viaquantization[20,22,27]orstatisticalestimation[10,69].The
chronousGPU-CPU-diskframeworkandacachingmecha-
third type leverages SIMD instructions ofmodernCPUs and ad-
nism to index billion-scale datasets within GPU and CPU
juststhedatalayouttominimizerandommemoryaccess[22,63].
memoryconstraintswhilealleviatingdiskI/Opressure. These methods achieve significant improvement. However, they
• Extensive experiments. We conduct comprehensive experi- requiresubstantial resources for large-scale datasetsand remain
mentsdemonstratingthatTagoreoutperformsexistingmeth-
impracticalfornightlyindexreconstructioninproductionenviron-
odson7real-worlddatasets,achieving1.32×-112.79×speedup.
ments.
IndexingaccelerationonGPUs.GPUs’parallelcomputingcapa-
Therestofthispaperisorganizedasfollows.Section2reviews
bilitieshavebeenwidelyexploitedforacceleratingANNSqueries
the related studies. Section 3 introduces graph-based index con-
usinggraph-basedindexes[23,24,32,39,48,60,72,77,81].More-
structionandGPUarchitectures.Section4describestheGNN-Descent
over,someresearchexploresANNSonotheremerginghardware
algorithm. Section5 exhibits thepruning acceleration. Section 6
besides GPUs, such as FPGAs [29, 30, 73], SmartSSDs [59], and
presents theGPU-CPU-disk asynchronous framework. Section7
CXL [25, 26]. Recent work hasnoticed the inefficiency ofindex-
reportstheexperimentalresults.Section8concludesthepaper.
ingandbegunleveragingGPUstooptimizeindexconstruction[48,
61,72].Forexample,GANNS[72]andGGNN[23]employadivide-
2 RelatedWork
and-conquerstrategy,partitioningdatasetsintosubgraphsbuiltin
Inthissection,wereviewtherelatedworkaboutgraph-basedin- parallelonGPUthreadblocks.Thesubgraphsarefinallymergedto
dexesandindexingacceleration. constructaglobalgraphindex.Thisstrategyintroducesadditional
mergingoverhead,eventhoughonsmalldatasets,resultinginsub-
optimalperformance[48].GNND[61]proposesaGPU-accelerated
2.1 Graph-basedIndexes
NN-Descent algorithm, providing a foundation for the accelera-
Graph-basedindexesareprominentamongvarioustypesofANNS
tionofrefinement-basedmethods.BasedonGNNDimplemented
methodsduetotheirsuperioraccuracyandefficiency[16,27,43, incuVS[46],CAGRA[48]introducesapruningstrategyespecially
53].Theymodelaproximitygraphwhereverticesrepresentvec-
forGPUs,achievingstate-of-the-artperformanceinbothindexing
torsindatabasesandedgesencodethenearest-neighborrelation-
andsearch.However,existingGPUmethodslackaunifiedlibrary
ships.Existinggraph-basedmethodsarecategorizedintothreeclasses foracceleratingmainstreamrefinement-basedindexes,andthepo-
basedonconstructionstrategies[65].
tentialofGPUshasnotyetbeenfullyrealized.
Refinement-basedmethodsinitialize neighbors for eachnode
Out-of-core indexing acceleration. DiskANN [28] employs a
using randomization[13,28],multipleKD-trees[16],ortheNN- divide-and-conquerstrategytoconstructtheout-of-coreindex,par-
Descentalgorithm[18,48].Whilerandominitializationyieldslow-
titioningthedatasetvia𝑘-meansclusteringandbuildinglocalin-
qualitygraphsandKD-treesincurhighcomputationalcosts[65],
dexesthatarelatermergedintoaglobalindex.SPANN[12]adopts
NN-Descenthasbecomeapopularinitializationmethodforitsbal- aninvertedindexapproach,storingonlypostinglistcentroidsin
ance of efficiency and quality [17, 18, 36, 48]. Subsequent prun-
memoryandutilizinghierarchicalbalancedclusteringforefficient
ingphasesrefineneighbordistributionstooptimizesearchperfor-
postinglistsgeneration.Starling[64]enhancesdatalocalitythrough
mance,withstrategieslikeRelativeNeighborhoodGraph(RNG)in blockshuffling during index construction.However, these meth-
NSG[18]andrank-basedpruninginCAGRA[48]andNGT[27].
odsrelyontheCPUtoconstructtheindex,leadingtoinefficiency
Increment-basedmethodsconstructtheindexincrementallyby
andsubstantialI/Ooverhead.Similartoourproposedmethod,some
inserting vectorsintothegraph[42,43,53].Foreachvector,the out-of-coreGNNtrainingframeworksleveragecachingtechniques
nearestneighborsareretrievedfromthecurrentgraph,andedges
to mitigate I/O costs. These methods cache frequently accessed
areattachedbetweennewvectorsandtheirnearestneighbors.More-
(“hot”)featuresontheGPUandminimizeinter-partitioncutedges
over,somemethodsincorporatepruningtodeterminewhetheran basedongraphconnectivitytoreducedatatransferoverhead,em-
edgecanbeestablishedbetweenavectoranditsnearestneighbors ployingstrategiessuchasstaticcaching[58],dynamiccaching[38],
duringconstruction[78].
andadvancedpartitioning[37,57,79].However,theirprimarychal-
Divide-and-conquermethodspartitiondatasetsintoclustersand lengeliesinidentifyinghotfeaturesandoptimizingpartitioning,
constructlocalsubgraphsforeachpartition[6,9,11,23,54].They whereas out-of-core indexing primarily requires efficient cluster
mergethesubgraphstoestablishaglobalproximitynearestneigh-
schedulingforsubgraphconstruction.Thisdistinctionrendersour
borgraphtoensurehighsearchperformance. problemfundamentallydifferent, withauniqueoptimizationob-
Consideringthesuperiorqueryperformanceandparallelization- jective.
friendlyworkflowofrefinement-basedmethods,wefocusonaccel-
eratingtheconstructionofthistypeofindex.

SIGMOD’26,May31–June05,2026,Bengaluru,India ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao
Table 1: Pruning strategies of refinement-based indexes, betweenvectors𝑎®and𝑏®.Agreedyalgorithmisdesignedtoitera-
where𝑅referstotheneighborlistforpoint𝑝.
tivelyinsertneighborsinto𝑅,maximizingthisangulardispersion.
NSSG[17]alsoconsiderstheanglebetweenneighbors.Itsetsa
| Index | Pruningstrategies | Computingparadigm |     |     |     |     |     |     |
| ----- | ----------------- | ----------------- | --- | --- | --- | --- | --- | --- |
threshold𝛾.Foreachnode𝑝,theneighborsand2-hopneighbors
| DPG | maxÍ 𝛿(𝑝®𝑝𝑖,𝑝®𝑝𝑗) | Serial |     |     |     |     |     |     |
| --- | ----------------- | ------ | --- | --- | --- | --- | --- | --- |
𝑝𝑖,𝑝𝑗∈𝑅 arecollectedintoacandidateset𝑉.Thealgorithmiterativelyse-
| NSSG   | 𝛿(𝑝®𝑝∗,𝑝®𝑝′)>𝛾          | Serial |     |                               |     |                           |     |     |
| ------ | ----------------------- | ------ | --- | ----------------------------- | --- | ------------------------- | --- | --- |
|        |                         |        |     | lectsthenearestneighbor𝑝′for𝑝 |     | from𝑉.𝑝′isinsertedinto𝑅if |     |     |
| NSG    | 𝑑𝑖𝑠(𝑝,𝑝′)<𝑑𝑖𝑠(𝑝∗,𝑝′)    | Serial |     |                               |     |                           |     |     |
|        |                         |        |     | andonlyif∀𝑝∗∈𝑅,𝛿(𝑝®𝑝∗,𝑝®𝑝′)   |     | >𝛾.                       |     |     |
| Vamana | 𝑑𝑖𝑠(𝑝,𝑝′) <𝛼∗𝑑𝑖𝑠(𝑝∗,𝑝′) | Serial |     |                               |     |                           |     |     |
max(𝑑𝑖𝑠(𝑝𝑖,𝑝𝑘 ),𝑑𝑖𝑠(𝑝𝑘,𝑝𝑗)) < NSG [18] claims that not all neighbors of a node contribute
| CAGRA |     | Unbalancedparallel |     |     |     |     |     |     |
| ----- | --- | ------------------ | --- | --- | --- | --- | --- | --- |
𝑑𝑖𝑠(𝑝𝑖,𝑝𝑗) equallyto search efficiency. For each node𝑝,it firstcollectsthe
|     |     |     |     | candidateset𝑉 | byrecordingallvisitednodeswhilesearching𝑝on |     |     |     |
| --- | --- | --- | --- | ------------- | ------------------------------------------- | --- | --- | --- |
thek-NNgraph.Ittheniterativelyselectsthenearestnode𝑝′for
|     |     |     |     | 𝑝from𝑉.𝑝′isinsertedinto𝑅iff𝑑𝑖𝑠(𝑝,𝑝′) |     |     | <𝑚𝑖𝑛𝑝∗∈𝑅𝑑𝑖𝑠(𝑝∗,𝑝′). |     |
| --- | --- | --- | --- | ------------------------------------ | --- | --- | ------------------- | --- |
3 Preliminaries
Vamana[28]modifiesNSG’sstrategybyrelaxingtheproximity
In this section, we introduce the background of the refinement- constraintto𝑑𝑖𝑠(𝑝,𝑝′) <𝛼∗𝑑𝑖𝑠(𝑝∗,𝑝′),where𝛼 >1,promoting
basedindexconstructionandGPUarchitectures. long-rangeconnectionstoimprovegraphnavigability.
|     |     |     |     | CAGRA | [48],inspired | byNGT[27],takesaninitialized𝑘-NN |     |     |
| --- | --- | --- | --- | ----- | ------------- | -------------------------------- | --- | --- |
3.1 Refinement-basedIndexing graphasinput,whereitonlystorestheneighborlistsforallthe
nodes,withoutstoringtheexactdistancesbetweennodesandtheir
Theconstructionofrefinement-basedindexescomprisestwophases:
|            |                                   |                |       | neighbors. | Instead, CAGRA | estimates the | distances between | the |
| ---------- | --------------------------------- | -------------- | ----- | ---------- | -------------- | ------------- | ----------------- | --- |
| k-NN graph | initialization and graph pruning. | Initialization | typi- |            |                |               |                   |     |
nodeanditsneighborsbasedonthepositionoftheneighborsin
callyemploystheNN-Descentalgorithm[14],whichhasbecome
|     |     |     |     | thesortedneighborlist.Forexample,foraneighbor𝑋 |     |     | thatislo- |     |
| --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --------- | --- |
themostpopularmethodinKGraph[13],DPG[36],NSG[18],and
catedatthefirstpositioninnode𝐴’sneighborlist,itsposition1is
CAGRA[48].Pruningleveragesavarietyofstrategies,including
usedasanestimateof𝑑𝑖𝑠(𝐴,𝑋).CAGRAprunesedgesbasedona
theRNG-based[18]andrank-based[48]methods.Inthissubsec-
conceptofadetourableroute.Foranedge(𝑝𝑖,𝑝𝑗),where𝑝𝑖and𝑝𝑗
tion,wefirstoutlinetheNN-Descentalgorithmandthensumma-
arenodesintheinitializedgraph,theedgehasadetourableroute
rizekeypruningstrategiesusedinrefinement-basedmethods.
|     |     |     |     | (𝑝𝑖 →𝑝 | →𝑝𝑗)ifmax(𝑑𝑖𝑠(𝑝𝑖,𝑝 | ),𝑑𝑖𝑠(𝑝 ,𝑝𝑗)) | <𝑑𝑖𝑠(𝑝𝑖,𝑝𝑗).This |     |
| --- | --- | --- | --- | ------ | ------------------ | ------------- | ---------------- | --- |
|     |     |     |     | 𝑘      |                    | 𝑘 𝑘           |                  |     |
3.1.1
NN-Descent. TheNN-Descent algorithm[14]isawidely strategyprunesneighborswithmoredetourableroutes.
adoptedmethodforconstructingapproximatek-NNgraphs.Itlever- These pruning strategies are summarized in Table 1. Notably,
ages theprinciple of“neighbors are morelikely tobeneighbors DPG, NSSG, NSG, and Vamanarely onserial neighbor insertion
ofeachother”,anditerativelyrefinesaninitialgraphwhereeach tomanage complex dependencies in neighbor lists.Thisprocess
nodeisrandomlyconnectedto𝑘neighbors.Ineachiteration,each requires sequential validation of each candidate against existing
neighborsbeforeinsertion,whichinherentlylimitsGPUparallelism
nodeintroducesitsneighborstoeachother,allowingthemtodis-
cover closerneighbors.Specifically,duringeachiteration,theal- duetodependency chains. While CAGRA’spruning strategyen-
gorithm(1)samplesnew(previouslyunsampled)andold(already ablesparallelcomputation,itintroducesunbalancedworkloadsamong
sampled)nodesfromtheneighborlistofeachnode,(2)performs GPUthreadsduetothevariablenumberofnodesaccessedacross
alocaljoinoperationtocalculatepairwisedistancesbetweennew- neighbors,whichfurtherreducesGPUefficiency.
| newandnew-old | nodepairs,and(3)updatesthecloserneighbors |     |     |     |     |     |     |     |
| ------------- | ----------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
intotheneighborlistsofthecorrespondingnodes.Thenewnodes
insertedinthecurrentiterationarelabeledasnew,whiletheprevi-
ouslysamplednodesarelabeledasold.Thisprocessrepeatsuntil
theapproximatek-nearestneighborsconvergetothedesiredqual-
ity.
|     |     |     |     | 3.2 GPUArchitecture |     |     |     |     |
| --- | --- | --- | --- | ------------------- | --- | --- | --- | --- |
GPU-acceleratedimplementationsoptimizeNN-Descentbyre-
formulatingthelocaljoinoperationasbatchedmatrixmultiplica- ThememoryarchitectureoftheGPUcomprisesthreeprimarytiers:
tion,whichGPUsefficientlyperform[46,61].However,frequent globalmemory,sharedmemory,andregisters.Globalmemorypro-
neighbor listupdatesleadtosignificant memoryaccessandsyn- videsalargestoragecapacitybuthascomparativelyloweraccess
chronizationoverhead[61].Tomitigatethis,existingmethodspri- speeds.Sharedmemory,ontheotherhand,allowshigh-bandwidth
|     |     |     |     | dataexchange | within thread | blocks,facilitating | faster communi- |     |
| --- | --- | --- | --- | ------------ | ------------- | ------------------- | --------------- | --- |
oritizeinsertingonlytheclosestneighborperiterationratherthan
allcloserneighborsidentifiedduringtheiteration. cationbetweenthreads.Registersofferthefastestaccesslatency,
storingthread-specificdataandensuringisolationforeachthread
3.1.2
PruningStrategies. Pruningstrategiesrefineneighbordis- onceallocated[8,49].InmodernGPUarchitectures,therearetwo
tributionsininitialized𝑘-NNgraphstoimprovequeryperformance. maintypesofcomputingunits:CUDAcoresandTensorcores.CUDA
Belowaresomenotableapproaches. coresfunctionasgeneral-purposeprocessorsandareresponsible
DPG[36]adjuststheneighbordistributionbymaximizingthe
forhandlingawiderangeofcomputationalworkloads.Tensorcores,
averageanglebetweenneighbors.Formally,foreachnode𝑝andits
|     |     |     |     | however, | are specialized | hardware designed | for accelerating | ma- |
| --- | --- | --- | --- | -------- | --------------- | ----------------- | ---------------- | --- |
finalneighborlist𝑅,theobjectiveistomaximizetheangulardis- trixoperations,performingfixed-sizematrixmultiplicationswith
persionmaxÍ 𝛿(𝑝®𝑝𝑖,𝑝®𝑝𝑗),where𝛿(𝑎®,𝑏®)denotestheangle highefficiencyperclockcycle[80].
𝑝𝑖,𝑝𝑗∈𝑅

(cid:258)(cid:258)(cid:258)(cid:258) (cid:258)(cid:258)
ScalableGraphIndexingusingGPUsforApproximateNearestNeighborSearch SIGMOD’26,May31–June05,2026,Bengaluru,India
|     |     | GNN-Descent          |                      | CFS pruning procedure            |                                 |                  |              |               |      |                 |      |          |
| --- | --- | -------------------- | -------------------- | -------------------------------- | ------------------------------- | ---------------- | ------------ | ------------- | ---- | --------------- | ---- | -------- |
|     |     |                      |                      |                                  |                                 |                  | of 1 million | vectors, each | with | 128 dimensions. | GNND | exhibits |
|     |     | Coa rs e- g r ai ned | Fi n e -g r a i n ed | ca C n o d l i l d e a c t t e   | scan F d il i t d e a r tes r S | es to u r l e ts |              |               |      |                 |      |          |
sa m p li n g s a m p l i n g k-NN a markedly slower recall improvement rate than the CPU-based
| Vector dataset |     |     |     | Graph | (cid:258) | Graph index |     |     |     |     |     |     |
| -------------- | --- | --- | --- | ----- | --------- | ----------- | --- | --- | --- | --- | --- | --- |
Wavefront-p(cid:258)a (cid:258)(cid:258) NN-Descent under the same iterations, with convergence decel-
|     |     | GPU Neighbor update |     | computing model | rallel Balanced- computing model | parallel  |     |     |     |     |     |     |
| --- | --- | ------------------- | --- | --------------- | -------------------------------- | --------- | --- | --- | --- | --- | --- | --- |
erationbecomingmorepronouncedoncerecallexceeds0.8.This
Figure 3: Index constructionworkflow of Tagore when the slowdown is primarily due to three factors. First, GNND causes
datasetfitsinGPUmemory. multiplenodestosharethesamebatchofsamplingnodesduring
|     |     |     |     |     |            |       | each iteration, | hindering | fine-grained | neighbor | updates. | Second, |
| --- | --- | --- | --- | --- | ---------- | ----- | --------------- | --------- | ------------ | -------- | -------- | ------- |
|     |     |     |     |     | NN-Descent | 66.2s |                 |           |              |          |          |         |
limitedGPUmemorycapacityrestrictsthenumberofnewandold
GNND8.1s nodesprocessedineachiteration.Lastly,GNNDupdatestheneigh-
borlistsbyselectingonlytheclosestneighborforeachnodeper
iteration,leadingtoinefficientuseofintermediatecomputational
|     |     |     |     | 57.5% | 14.0% | 28.5% |     |     |     |     |     |     |
| --- | --- | --- | --- | ----- | ----- | ----- | --- | --- | --- | --- | --- | --- |
results(seeSection3.1.1).
|     |     |     |     | GPU kernel | Data transfer | CPU computing |     |     |     |     |     |     |
| --- | --- | --- | --- | ---------- | ------------- | ------------- | --- | --- | --- | --- | --- | --- |
Toillustratethefirstproblem,considertheexamplesubgraph
(a) The variation trend of recall.  (b) Time decomposition of GNND in cuVS.  in Figure 5, where anchor node𝐺 mediates neighbor discovery
Figure 4: Recall of k-nearest neighbors and time compo- amongitsconnectednodes.Inthissubgraph,nodes𝐴and𝐵 are
|                                  |     |     |     |     | =            |     | labeledasnew,while𝐶,𝐷,𝐸and𝐹 |     |     | arelabeledasold.DuetoGPU |     |     |
| -------------------------------- | --- | --- | --- | --- | ------------ | --- | --------------------------- | --- | --- | ------------------------ | --- | --- |
| nentsforNN-DescentandGNND,where𝑘 |     |     |     |     | 96anddataset |     |                             |     |     |                          |     |     |
memoryconstraints,newandoldnodesaresampledforlocaljoin.
isSIFT.Figure4(b)depictstheoverheadtoreachtherecall
| of95%. |     |     |     |     |     |     | Supposethesamplesizeis2.InFigure5(a),{𝐴,𝐵}and{𝐸,𝐹}are |                    |          |              |         |       |
| ------ | --- | --- | --- | --- | --- | --- | ----------------------------------------------------- | ------------------ | -------- | ------------ | ------- | ----- |
|        |     |     |     |     |     |     | sampled,                                              | requiring pairwise | distance | calculations | between | these |
setstoassesspotentialneighborlistupdates.Thissamplingstrat-
|     | Node labeled new |     | Node labeled old |     | Anchor node |     |     |     |     |     |     |     |
| --- | ---------------- | --- | ---------------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
egycausesnode𝐴and𝐵tosharethesamesamples,butasshown
Sampled nodes Sampled nodes of A Sampled nodes of B inFigure5(a),thetruenearestneighborsof𝐵are{𝐶,𝐷}not{𝐸,𝐹}.
|     |     | E   |     | E   |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     | D   |     |     | D   |     |     |     |     |     |     |
G G Consequently,theprocessoflocaljoinfailstoexploretheactual
|     | × F |     |     | F   |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
C × C × nearestneighborsofcertainnodes,leadingtoasevereslowdown
A B A B inconvergence afterrecallsurpasses0.8.Earlyiterationsremain
| Vector values |     |     | Vector values |     |     | Vector values |     |     |     |     |     |     |
| ------------- | --- | --- | ------------- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- |
unaffectedbythisissuebecausethegraphqualityislow,andeven
|     | (a) NN-Descent local join. |     |     | (b) Fine-grained neighbor update. |     |     |     |     |     |     |     |     |
| --- | -------------------------- | --- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
suboptimalsamplingyieldsincrementalrecallgains.TheCPU-based
Figure5:AnalysisofNN-Descentsamplestrategy.
|     |     |     |     |     |     |     | NN-Descent | avoids this | limitation, | as it can sample | more | nodes |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ----------- | ----------- | ---------------- | ---- | ----- |
3.3 Overview ofTagore without memory restrictions, covering the nearest neighbors of
morenodes[14],butatthecostofcomputationalredundancyfrom
| Figure | 3 illustratestheindex |     | constructionpipelineinTagore |     |     | for |     |     |     |     |     |     |
| ------ | --------------------- | --- | ---------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
extraneousdistanceevaluations.
datasetfitswithinGPUmemory.TheframeworkfirstemploysGNN-
|          |                  |     |                                  |     |     |     | Given GPUmemoryconstraints,itisinfeasible |     |     |     | toexpandthe |     |
| -------- | ---------------- | --- | -------------------------------- | --- | --- | --- | ----------------------------------------- | --- | --- | --- | ----------- | --- |
| Descent, | aGPU-accelerated |     | two-phase𝑘-NNgraphinitialization |     |     |     |                                           |     |     |     |             |     |
samplingsizeasfreelyasonCPUs.Toaddressthis,weproposea
algorithm,toefficientlyconstructanapproximate𝑘-NNgraph.Sub-
fine-grainedsamplingstrategy,showninFigure5(b),whereeach
sequently,the𝑘-NNgraphundergoespruningviaaCFSpruning
node𝑣 inthegraphindependentlysamplesfromtheneighborlist
framework,whichunifiesmultiplepruningstrategieswhileopti-
|     |     |     |     |     |     |     | ofitstop-𝑚nearestneighbors(with𝑚 |     |     | =2).Thisensuresthatthe |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | ---------------------- | --- | --- |
mizingGPUutilization.FordatasetsexceedingGPUmemoryca-
samplednodesremaincloseto𝑣,resolvingtheproblemcausedby
pacity,TagoreautomaticallytransitionstotheGPU-CPU-diskasyn-
sharedsampling.However,thisapproachintroducesanewprob-
chronousconstructionmode(Figure10).Duringtheasynchronous
lem:whiletheoriginallocaljoinprocessleveragesefficientGPU-
construction,thedatasetisdividedintoclusters,withlocalindexes
optimizedmatrixmultiplicationfornew-oldandnew-newpair-wise
| constructed |     | on GPUs, | and merged | to disk | using a | cluster-aware |     |     |     |     |     |     |
| ----------- | --- | -------- | ---------- | ------- | ------- | ------------- | --- | --- | --- | --- | --- | --- |
distancecalculations,theindependentsamplingstrategyinFigure
cachingmechanismtominimizeI/Otimes.
5(b)fragmentstheseoperationsintovector-matrixmultiplication
operations,reducingthecomputationalthroughputofGPUs.
4 Two-phaseGNN-Descent
Tomitigatethelimitationsofsharedsamplingwhilemaintain-
AsTagorefamouslysaid,“Thebutterflycountsnotmonthsbutmo-
|     |     |     |     |     |     |     | ing efficiency, | we propose | a two-phase | GNN-Descent |     | algorithm |
| --- | --- | --- | --- | --- | --- | --- | --------------- | ---------- | ----------- | ----------- | --- | --------- |
ments”,emphasizingtheimportanceofvaluingtime.Similarly,an
tailoredforGPUs,asoutlinedinAlgorithm1.Thesharedsampling
effectivegraphinitializationalgorithmembodiesthisprincipleby strategydoesnotexperiencesignificantconvergencedeceleration
prioritizing speed, making the most of each moment in its exe- duringtheearlyiterations,astheinitialgraphqualityislow.There-
| cution.Inthissection,weexplorethedesign |     |     |     |     | ofournovel | GNN- |     |     |     |     |     |     |
| --------------------------------------- | --- | --- | --- | --- | ---------- | ---- | --- | --- | --- | --- | --- | --- |
fore,inthefirstphase,weretaintheoriginalNN-Descentsample
Descent(GPU-basedNN-Descent)algorithmintegratedintoTagore,
strategy(Figure5(a))toexploititsrapidconvergenceintheearly
demonstratinghowitacceleratestheinitializationofk-NNgraphs.
stages(lines4-7).
|     |     |     |     |     |     |     | After completing | a total | of𝑖𝑡1 | iterations in | the first | phase, it |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | ------- | ----- | ------------- | --------- | --------- |
4.1 AlgorithmicDesign
switchestothesecondphase(lines8-12).Inthesecondphase,each
Figure4(a)showstheprogressionoftherecallvalueforthe𝑘-NN nodeindependentlysamplesfromtheneighborlistsofits𝑚near-
=
(with𝑘 96) on graphs constructed using the NN-Descent im- estneighbors,asshowninFigure5(b),ensuringfine-grainedneigh-
plemented in KGraph [13] on CPU and GNND implemented in borupdates.UnlikethebasicNN-Descentalgorithmin[14],ourap-
cuVS [46, 61] on GPU. The dataset used is SIFT, which consists proachenforcesanon-revisitationpolicy,wherenodesprocessed

(cid:258)(cid:258)
(cid:258)(cid:258)
SIGMOD’26,May31–June05,2026,Bengaluru,India ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao
Distance
|     |     |          |                 | Compare by       |               |                           |     | E'  |                  |
| --- | --- | -------- | --------------- | ---------------- | ------------- | ------------------------- | --- | --- | ---------------- |
|     |     |          |                 | _ _ s hfl_sync() |               | ×                         |     |     |                  |
|     |     | Distance |                 | C o ll           | e c t  b y    |                           | A'  |     |                  |
|     |     | A        | E               | at o m           | i c A d d ( ) |                           |     | F'  |                  |
|     |     |          | Store Registers |  o f   E         |               |                           |     |     | Candidates of A' |
|     |     |          | Warp 0          |                  |               | Thread block 1 CUDA Cores |     |     |                  |
|     |     | B        | F               | Local closest    |               |                           |     |     |                  |
| ×   |     |          |                 | neighbor         |               | Thread block 2            |     |     |                  |
Distance
|     |              |     | J                   |     |                 | ×   |     | C'  |     |
| --- | ------------ | --- | ------------------- | --- | --------------- | --- | --- | --- | --- |
|     | Tensor Cores |     | Store Registers of  |     | Candidates of A |     | B'  |     |     |
K
|     |     |     | K Warp 1 |     |     |     |     | D'  | Candidates of B' |
| --- | --- | --- | -------- | --- | --- | --- | --- | --- | ---------------- |
Local closest
| Stored in     |     |     |     | neighbor |     | Stored in  CUDA Cores |     |     |     |
| ------------- | --- | --- | --- | -------- | --- | --------------------- | --- | --- | --- |
| shared memory |     |     |     |          |     | shared memory         |     |     |     |
(a) Calculating process of phase 1. (b) Calculating process of phase 2.
Figure6:DistanceCalculationprocessofGNN-DescentonGPU.
| Algorithm1:Two-phaseGNN-Descent |     |     |     |     |     |     |     | Binary search |     |
| ------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- |
Sort
Input:dataset𝑉,numbersofiterations𝑖𝑡1and𝑖𝑡2forthe 1 9 4 6 8 7 1 4 6 7 8 9 2 3 5 6 7 9
|     | firstandsecondphasesrespective,degree𝑘 |     |     |     |     |                 |        |     | Neighbor list of A |
| --- | -------------------------------------- | --- | --- | --- | --- | --------------- | ------ | --- | ------------------ |
|     |                                        |     |     |     |     | Candidates of A | Pos: 1 |     | Pos: 2             |
Final Pos: 1+2=3
Output:k-NNgraph𝐺
| 1 for𝑣 | ∈𝑉 inparalleldo |     |     |     |     |     | 1   | 2 3 4 5 | 6   |
| ------ | --------------- | --- | --- | --- | --- | --- | --- | ------- | --- |
Initializeneighborlist𝐺[𝑣] randomly; Updated neighbor list of A
2
/* First phase */ Figure7:ParallelupdateprocessofGNN-DescentonGPU.
<𝑖𝑡1;𝑐𝑢𝑟𝐼𝑡++)do
3 for(𝑐𝑢𝑟𝐼𝑡 ←0;𝑐𝑢𝑟𝐼𝑡
| 4 for𝑣 | ∈𝑉 inparalleldo |     |     |     |     |     |     |     |     |
| ------ | --------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Samplenodesusingsharedsamplingstrategy;
5
|     |     |     |     |     | andneighbor | listupdates.Whileparallelsamplingisstraightfor- |     |     |     |
| --- | --- | --- | --- | --- | ----------- | ----------------------------------------------- | --- | --- | --- |
6 Performlocaljoinusingmatrixmultiplication;
ward,wefocusonGPU-specificoptimizationsfordistancecompu-
7 Updatecloserneighborstothecorresponding
tationandneighborupdates,whichdominateruntimeandmem-
neighborlists;
oryoverhead.
| /* Second | phase | */  |     |     |     |     |     |     |     |
| --------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
Figure6(a)illustratesthefirst-phasedistancecalculationwork-
<𝑖𝑡2;𝑐𝑢𝑟𝐼𝑡++)do
8 for(𝑐𝑢𝑟𝐼𝑡 ←0;𝑐𝑢𝑟𝐼𝑡
flow,extendingtheexamplefromFigure5withanincreasedsam-
| 9 for𝑣 | ∈𝑉 inparalleldo |     |     |     |     |     |     |     |     |
| ------ | --------------- | --- | --- | --- | --- | --- | --- | --- | --- |
plesizeof4toclarifythealgorithm’smechanics.SimilartoGNND,
Sampleneighborsoftop-𝑚unvisitedNNof𝑣;
10 GNN-Descentinitiallyloadsthecorrespondingnodesintotheshared
11 Calculatedistancebetween𝑣 andsamplednodes; memoryandperformslocaljoinviamatrixmultiplicationonTen-
12 Updatecloserneighborsto𝐺[𝑣]; sorCores.Afterthelocaljoin,GNNDretainsonlytheclosestneigh-
returnG
13 bor for each node, wasting extensive computational results and
exacerbatingtheconvergencedeceleration.Toaddressthis,GNN-
Descentimplementsadata-reuse-awarestrategy:aftermatrixmul-
tiplicationinTensorCores,partialdistancematricesarestoredin
inpreviousiterationsareexcludedfromsubsequentsampling,thereby
|     |     |     |     |     | theregisters | ofeachGPU | warp(e.g., | Warp0storesthedistance |     |
| --- | --- | --- | --- | --- | ------------ | --------- | ---------- | ---------------------- | --- |
eliminatingredundantcomputations.
between𝐴and{𝐸,𝐹},whileWarp1storesthedistancebetween𝐴
and{𝐽,𝐾}inFigure6(a)).Wethenselecttheclosestnodewithin
4.2 GPUImplementation
eachwarpforeachnode(e.g.,node𝐸for𝐴inWarp0,andnode𝐾
BuildingontheGNN-Descent framework, wenow turntoGPU- for𝐴inWarp1)andstoretheminthecorrespondingcandidatelist.
specificoptimizationsforeachalgorithmiccomponent.IncuVS[46], Theselectionofthelocalclosestnodecanbeefficientlyperformed
NN-DescentisexecutedcollaborativelyacrossCPUandGPU:the usingthewarp-levelintrinsic__shfl_sync()inCUDAforregister-
GPUhandleslocaljoinoperations,whiletheCPUmanagesneigh- based valuecomparisons, avoiding memory access and enabling
borlistupdates.Althoughtheyarepipelined,inefficiencies arise efficientmulti-candidateretention.
fromfrequentCPU-GPUdatatransfers,synchronizationoverhead, In the second phase, as shown in Figure 6(b), we implement
andthelimitedcomputationalcapacityoftheCPU.Forexample, node-centricparallelismbydistributingthecalculationofdistances
Figure4(b)showsthetimerequiredtogenerateagraphthatachieves between each node and its neighbors in the candidate list to in-
a recall of 95% in𝑘-NN searches. While GNND significantly re- dividual thread blocks in the GPU. Within each block, the vec-
ducesthetimecomparedtoNN-DescentonCPU,thereisstillroom torvaluesofsamplednodesareloadedintosharedmemory,and
forfurtherimprovement.Theinefficienciesmentionedabovecol- vector-matrix multiplicationis executed via CUDA Cores. Then,
lectivelyaccountforover40%ofthetotalexecutiontimeofGNND, threadblockscomputedistancesbetween𝐴′andthesampledcan-
underscoringtheneedforGPU-native optimizations.Toaddress didates{𝐸′,𝐹′},wherethenotation𝑋′referstothevectorofthe
these bottlenecks, we fully offload NN-Descent execution to the node𝑋.To minimize computationaloverhead in subsequent up-
GPUandredesign keycomputationalmodulestooptimizemem- dates,weretainonlycandidatescloserthanthefarthestnodein
ory access patterns and parallel efficiency. Both phases of GNN- thecurrentneighborlistwhileeachlistcapturesupto𝑘neighbors.
Descent includethreeoperations:sampling,distance calculation, Thisthresholdguaranteesthatnon-viablecandidatesareexcluded

ScalableGraphIndexingusingGPUsforApproximateNearestNeighborSearch SIGMOD’26,May31–June05,2026,Bengaluru,India
Algorithm2:TheCFSprocedureofpruning
Input:dataset𝑉,k-NNgraph𝐺 1 2 3 D C E andi F dates (cid:258)(cid:258) Iteration1 A (cid:284) B C × (cid:284) D E × (cid:284) F (cid:258)(cid:258)
Output:finalgraphindex𝐺′ 1 2 C
A B C
1 for𝑣 ∈𝑉 inparalleldo Iteration2 A B D F (cid:258)(cid:258)
Final neighbor list
/* The built-in options of parameter Mode
(a) Serial computing paradigm. (b) Wavefront-parallelcomputing model.
include ‘1-hop’, ‘2-hop’, and ‘path’ */
Figure8:SerialcomputingparadigmofFilter.
2 Fillcandidateset𝐶𝑎𝑛𝑑byCollect(Mode,CandSize,𝑣);
/* The built-in options of parameter Metric
graph,collectingallvisitednodesalongthesearchpathascandi-
include ‘dist’, ‘angle’, and ‘rank’ */
dates,whicharethenfilteredinthenextphase.Tounifytheseap-
3 FilterthecandidateswithFilter(Metric,Thres,𝐶𝑎𝑛𝑑); proaches,theCollectoperationexposesaconfigurableparameter
4
StoreresultsintotheindexusingStore(𝐺′[𝑣],𝐶𝑎𝑛𝑑);
𝑀𝑜𝑑𝑒(line2ofAlgorithm2),whichsupportsthreeoptions:‘1-hop’,
‘2-hop’and‘path’.Collecting1-hopand2-hopneighborsinparal-
lelonGPUsisstraightforward,whilethe‘path’optionleverages
early,astheycannotimprovetheneighborlistduringtheupdate
CAGRA’sbatchedsearchmethod[48]togeneratecandidateswith
phase.
lowlatency.
Toeliminatelockingoverheadandmemoryaccessduringneigh-
Filter.TheFilteroperationiscomputationallydominantduring
borlistupdates,weproposealock-freemergingmechanismthat
pruning. As shown in line 3 of Algorithm 2, it filters the candi-
uses binary search for deterministic ranking. Asdepicted in Fig-
datesin𝐶𝑎𝑛𝑑basedonauser-specifiedpruningstrategy.Aslisted
ure7,theupdatemodulealsousesnode-centricparallelism.Within
inTable1,refinement-basedpruningstrategiesfallintothreecate-
eachthreadblock,thecandidatesforeachnodearesortedbytheir
gories:distance-based,angle-based,andrank-based.NSGandVa-
distanceinsharedmemory.Subsequently,athreadisassignedto
manaaredistance-basedstrategiesthatprunecandidatesaccord-
eachelementinboththecandidatelistandtheneighborlist.These
ing to the distance between the corresponding nodes. DPG and
threadscalculatetherelativerankoftheirassignedelementwithin
NSSGareangle-basedstrategies,whileCAGRAadoptsarank-based
theopponent’slistviabinarysearch.Thisrank,combinedwiththe
strategy.Toaccommodatethesevariations,Filterexposesapa-
positionoftheelementinitsownsortedlist,definesitsinsertion
rameter𝑀𝑒𝑡𝑟𝑖𝑐toallowuserstoselecttheirdesiredcategory.More-
indexinthemergedneighborlist.
over,theparameter𝑇ℎ𝑟𝑒𝑠controlsthethresholdforpruningstrate-
5 PruningStrategies giessuchas𝛼inVamanaand𝛾inNSSG.When𝛼 =1,Vamanade-
generatestoNSG,andsetting𝛾 =0invokesDPG.Givenitscompu-
Tagoreoncesaid,“Thebestdoesnotcomealone.Itcomeswiththe
tationalintensityandthecomplexneighbordependencies,Section
companyofall”,reflectingaprincipleofcollaborativeoptimization.
5.2elaboratesonourGPU-specificoptimizationsforFilter.
Inasimilarspirit,thissectionintroducesageneralizedpipelineto
Store.Tooptimizememoryaccess,candidatenodesaretemporar-
acceleratemainstreamrefinement-basedpruningstrategies,unify-
ilystoredinhigh-speedsharedmemoryintheFilteroperation.
ing their executioninto amodularGPU-optimized pipeline. Fur-
TheStore operationthen writesthefinal set ofneighbors from
thermore,wedetailtwospecializedGPUkernelsdevelopedwithin
sharedmemorytotheirpre-allocatedpositionswithinGPUglobal
theframeworktoachievescalable,hardware-awarepruning.
memory,andthentotheCPUforstorageinfiles.
TheCFS framework providesa generalized abstractionfor di-
5.1 AnalysisofComputingProcedure
versepruningstrategies,assummarizedinTable1.Notably,itac-
Table1summarizesvariousmainstreampruningstrategiesusedin
commodatesabroadspectrumofpruningstrategieswithminimal
existingrefinement-basedmethods.Ratherthanacceleratingindi- modifications2,sincethemethodsinTable1representfundamen-
vidualstrategies,ourgoalistodesignaunifiedcomputingframe-
talstrategiesthatinfluencenumerousderivativestrategies.Impor-
work that can accelerate all such strategies. To achieve this, we
tantly,the framework maintains extensibility for future pruning
first conduct a methodical analysis of the shared computational
paradigmsthatmaydivergefromthecurrentmethodologies.Users
patternsacrossthesestrategies.Weobservethatallpruningstrate-
canselectivelyoverridespecificfunctionswhilepreservingtheover-
giesinTable1followathree-stepworkflow:(1)Collectcandidate
allpipelinearchitecture,therebyensuringbothbackwardcompat-
neighbors,(2)Filter basedonpruningstrategies,and(3)Storethe
ibilityandforwardflexibility.
final neighbors. Weformalizethisworkflow as theCFS(Collect-
Filter-Store)framework,asoutlinedinAlgorithm2.CFSpreserves 5.2 ComputingOptimizationsonGPUs
the node-centric parallelismmodelonGPUs, where each thread
WithintheCFSframeworkintroducedinSection5.1,Filteristhe
blockisassignedtopruneasinglenode’scandidateset,ensuring
mostcomputationallyintensiveoperationduetoitscentralrolein
bothscalabilityandhardwareefficiency.
pruningcomputations.Therefore, thissubsectionfocusesonthe
Collect.TheCollectoperationidentifiescandidateneighborsfor
computationalparadigmunderlyingFilteracrosspruningstrate-
eachnodefromthek-NNgraph.Thepruningstrategieslistedin
giesandtailorstheparadigmforGPU-specificoptimizations.
Table1employvariousmethodstocollectcandidates.Forinstance,
DPG,NSSG,NSG,andVamanaemployaserialcomputingpar-
DPGandCAGRAlimitcandidateselectiontoimmediateneighbors
adigmcharacterizedbysequentialdatadependencies.Asdepicted
(1-hop)inthek-NNgraph,whileNSSGexpandsto2-hopneigh-
borsinthek-NNgraphforbroaderexploration.Incontrast,NSG 2Examplesareavailableathttps://github.com/ZJU-DAILY/Tagore
and Vamana initiate searches from the entry point in the k-NN

SIGMOD’26,May31–June05,2026,Bengaluru,India ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao
1 warp 1 warp singlewarpforcalculation.Simplyemployingmultiplewarpsto
|     |       | Q   |                    |     | L i n e a r   s c a | n   |     |     |     |     |     |     |
| --- | ----- | --- | ------------------ | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- |
| U   | T S R |     | L in e a r  s ca n |     | S T U D             | V   |     |     |     |     |     |     |
V E P S T U D V B C D E B C D E B Nei g h b o r   l i s t  of  F pa r a ll e l i ze t h e c a lc ul a t io n f o r e a c h c a n d id a te l ea d s t o un b a l an c e d
|     | F   | O N eig hbo r lis t of |  F Partia l  N e i g h b o r  list of A | Par tial  Neig hbo r list o | f A |     |     |     |     |     |     |     |
| --- | --- | ---------------------- | --------------------------------------- | --------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
55 44 G H I J K w o r k l o a d s a c ro s s w a r p s, b e c a u s e d i ff e re n t ca n d id a t es (e .g . , 𝐹 , 𝐸 ,
|     | A   | D N R Q P O | S B C D | 1 w arp | N e i g h b o r   l i s | t   o f   C |     |     |     |     |     |     |
| --- | --- | ----------- | ------- | ------- | ----------------------- | ----------- | --- | --- | --- | --- | --- | --- |
33 N e i g h b o r   l i s t   o f   E P a r t i a l   N e i g h b o r   l i s t   o f   A L i n e a r   s c a n 𝐷 ,a n d 𝐶 ) n ee d t o s ca n v a r y in g n u m b e rs o f 𝐴 ’s n e ig h b o r s . F or e x -
|     | B 11 22 | L O N L K | F B C |     | R Q P O | S   |     |     |     |     |     |     |
| --- | ------- | --------- | ----- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
C K N e i g h b o r   l i s t   o f   D P a r t i a l   N e i g h b o r   l i s t   o f   A BC D BC N e i g h b o r   l i s t   o f   E am p le , no d e 𝐴 h a s fi v e n e ig h b or s . Ca n d id a te 𝐹 n e e d s t o s c a n 4 o f
|     | G   | J   |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
H I G H I J K B Partial Neighbor list of A O N L K F them,asneighbor 𝐹 canbeskipped;whilecandidate𝐸 needsto
|     |     | N eig hbo r lis t of |  C Partial Neig hbor list of A |     | Neig hbo r lis t of  | D   |     |     |     |     |     |     |
| --- | --- | -------------------- | ------------------------------ | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- |
(a) Example graph. (b) Original computing paradigm. (c) Balanced-parallelcomputing model. scan 3, as both 𝐸 and 𝐹 can be skipped. Note that 𝐸 is skipped
Figure9:UnbalancedparallelparadigmofFilter. because𝐴 → 𝐸 → 𝐸 cannot be a detourable path of𝐴 → 𝐸.
|     |     |     |     |     |     |     |            |                          |     | = > |          | =     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------------------------ | --- | --- | -------- | ----- |
|     |     |     |     |     |     |     | Similarly, | 𝐹 is skipped, as𝑑𝑖𝑠(𝐴,𝐸) |     | 4   | 𝑑𝑖𝑠(𝐴,𝐷) | 3 and |
inFigure8(a),considernodes𝐴and𝐵alreadyintheneighborlist. 𝑑𝑖𝑠(𝐴,𝐹) =5>𝑑𝑖𝑠(𝐴,𝐷)andhencethepath𝐴→𝐹 →𝐸cannot
Whennode𝐶isretrievedfromthecandidateset,itseligibilityfor beadetourablepatheither.
insertiondependsoncomputingpairwisedistances/angleswithall Toaddresstheissueofunbalancedcomputing,wedesignabalanced-
existingnodesintheneighborlist(here,𝐴and𝐵inFigure8(a)),ac- parallelcomputingmodel,asshowninFigure9(c).Itdeploystwo
cordingtothepruningstrategiesinTable1.Then,node𝐷’seligi- warpsforeachcandidatepair (𝑢,𝑣),wheretheirpositionssatisfy
bilitydependson𝐶’supdatedstatus,necessitatingstrictsequential 𝑝𝑜𝑠𝑢+𝑝𝑜𝑠𝑣 =𝑘+2(with𝑘denotingthedegreeofthek-NNgraph).
processing.Thisdependencychain—whereeachcandidate’seval- This pairing ensures that the aggregate workload for each warp
uationhingesonpriorresults—forcesasequentialexecutionpara- is balanced across warps. Each thread within a warp retrieves a
digm,whichisinherentlyincompatiblewithGPUparallelism. nodefromtheneighborlistof𝐴andscanstheneighborlistofthe
Toenablehigh-performancepruningforserialcomputationstrate- correspondingcandidate.Uponidentifyingasharednodethatsat-
gies, we propose a wavefront-parallel computing model specifi- isfiesthedetourpathcriteria,thethreadatomicallyincrementsthe
callydesignedforGPUstoexploittheirmassiveparallelism.Asil- detourablepathcountforthecorrespondingcandidates.
lustratedinFigure8(b),eachthreadblockallocatesseveralwarps ThetwooptimizedGPUkernelsenableuserstosimplymodify
(e.g., 2warpsinourexample)toprocesscandidatenodesinpar- thepruningequationsfornewlyproposedpruningstrategieswith
allel.In thefollowing, weexplain how topopulatetheneighbor theserialandunbalancedparallelcomputingparadigms,without
listwithnodesfromthecandidatepool.Eachwarpindependently consideringthecomplicatedunderlyingimplementation.
evaluatesthecandidatenodeagainstthecurrentneighborlist.For
example,initeration1,thetwowarpscalculatethedistanceoran-
|             |     |          |              |                      |     |     | 6 Large-scaleGraphIndexing |     |     |     |     |     |
| ----------- | --- | -------- | ------------ | -------------------- | --- | --- | -------------------------- | --- | --- | --- | --- | --- |
| glebetween𝐴 |     | and𝐵,and | thatbetween𝐴 | and𝐶,respectively.If |     |     |                            |     |     |     |     |     |
Tagoresaid,“Thescabbardiscontenttobedullwhenitprotectsthe
| thenumberofwarpsislessthanthenumber |     |     |     | ofcandidates,can- |     |     |          |                           |     |     |                 |      |
| ----------------------------------- | --- | --- | --- | ----------------- | --- | --- | -------- | ------------------------- | --- | --- | --------------- | ---- |
|                                     |     |     |     |                   |     |     | keenness | of the sword”. Similarly, | CPU | and | disk resources, | much |
didatesareprocessediteratively.Candidatesprunedbytheprun-
likethescabbard,playanessential,supportingroleinprotecting
| ing                | strategies | are removed | from the candidate            | set | at the | end of |               |             |                           |     |     |          |
| ------------------ | ---------- | ----------- | ----------------------------- | --- | ------ | ------ | ------------- | ----------- | ------------------------- | --- | --- | -------- |
|                    |            |             |                               |     |        |        | theefficiency | ofGPUs when | constructingbillion-scale |     |     | graphin- |
| theiteration(e.g., |            | nodes𝐶      | and𝐸 areprunedawayfromthecan- |     |        |        |               |             |                           |     |     |          |
dexesunderstringentmemoryconstraints.Inthissection,wepro-
didatesetiniteration1).Subsequently,initeration2,anarbitrary
poseanasynchronousGPU-CPU-diskpipelinetoefficientlybuild
candidate(e.g.,𝐵)withinthecurrentcandidatesetisinsertedinto
large-scaleglobalgraphindexesandintroduceacluster-awarecache
| theneighborlist.Theremainingcandidates(i.e.,𝐷 |     |     |     |     | and𝐹)arere- |     |     |     |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
mechanismtoreduceI/OoverheadbetweentheCPUanddisk.
evaluatedinsubsequentiterations,andweonlyneedtotestifthey
conflictwiththenodenewlyaddedintotheneighborlist(e.g.,𝐵
initeration2).Thismodeltransformstheinherentlysequentialde- 6.1 GPU-CPU-diskAsynchronousFramework
pendenciesintowavefrontparallelism:candidatesareprocessedin Given the prohibitive cost and capacity limitations of GPU and
batches,andeachiterationresolvesdependenciesonlywithinits CPUmemory,diskstorageprovidesapracticalsolutionforlarge-
wavefront. scaleindexing.Recentwork,suchasDiskANN[28],SPANN[12],
CAGRAadoptsadistinctunbalancedparallelparadigm,differ- andStarling[64],exploresdisk-basedindexinginscenarioswith
ingfromtheserialparadigm.Itutilizestherankofnode𝐴’sneigh- constrainedCPUmemory.However,tothebestofourknowledge,
bors(i.e.,theposition𝑝𝑜𝑠𝑢ofeachneighbor𝑢in𝐴’sneighborlist) noexistingmethodefficientlyconstructsbillion-scaleglobalgraph
asan estimateofthedistancebetween𝐴 and itsneighbors(e.g., indexeswhenbothGPUandCPUmemoryareconstrained.Totackle
𝑑𝑖𝑠(𝐴,𝐵) = 𝑝𝑜𝑠𝐵 = 1 and𝑑𝑖𝑠(𝐴,𝐶) = 𝑝𝑜𝑠𝐶 = 2, as shown in thisissue,inTagore,weadopttheworkflowofDiskANNandex-
Figure9(a)).AsdepictedinFigure9(b),foreachcandidateneigh- tendittoaheterogeneousGPU-CPU-disksystem.
borof𝐴,CAGRAemploysawarpofthreadstoretrievethecandi- DiskANN partitions each node to its𝑚 (𝑚 > 1) closest clus-
date’sneighbors.Eachthreadthenscans𝐴’sneighborlisttoiden- tersviak-means. Itthenconstructslocalgraphindexesforeach
tifysharedneighbors.Forinstance,whenathreadretrieves𝐷from clusterandwritestheseindexestodisk,finallymergingthelocal
theneighborlistof𝐹 anddetects𝐷 isin𝐴’slist,itidentifiesthe indexesintoaglobalindex.However,directlymappingDiskANN’s
path𝐴 → 𝐷 → 𝐹.As𝑑𝑖𝑠(𝐹,𝐷) = 4 < 𝑑𝑖𝑠(𝐴,𝐹) = 5,thepath workflowtotheGPU-CPU-diskheterogeneoussystemintroduces
𝐴 → 𝐷 → 𝐹 isflagged asadetourablepathfortheedge (𝐴,𝐹). twocriticallimitations.First,offloadinglocalindexconstructionto
Thecandidateneighborsof𝐴arethenprunedbasedonthenum- GPUsleavesCPUsidle,wastingtheircomputationalpotential.Sec-
ber ofdetourablepathsthecorresponding edges have. However, ond,writingandreadinglocalindexesto/fromdiskduringmerg-
thiscomputationalparadigmfordetourablepaths,showninFig- ingincursexcessiveI/Ooverhead,significantlyreducingthrough-
| ure9(b),cannotfullyutilizeGPUparallelism,asitemploysonlya |     |     |     |     |     |     | put. |     |     |     |     |     |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- |

ScalableGraphIndexingusingGPUsforApproximateNearestNeighborSearch SIGMOD’26,May31–June05,2026,Bengaluru,India
M e r g e d   g r a p h   N e ig h b o r  li s t   L o c a l   g r a p h  R A M Disk C3
w r it t e n  t o   d i s k req u ir ed   to   m e r g e tran sf e r r e d   t o  C PU 12 24
C ac he hit
|           |          |        |     |      |       | A A            |     |     |     | 33     |     |
| --------- | -------- | ------ | --- | ---- | ----- | -------------- | --- | --- | --- | ------ | --- |
| Clu sters | G P U Cl | uste r |     | R AM | D isk |                |     |     | C0  | C      | 5   |
| A B C     | B A C    | F D    |     | E E  | BB    |                |     |     | 3 4 | C 2 23 |     |
|           | A        | B D    | G B | D    |       | AA Merge Write | AA  |     |     | 2      | 8   |
| D E G     | 1 C F G  | E E    | F   | D G  | AA G  |                |     |     |     | 20 43  |     |
|           |          |        |     |      | A C   |                |     |     | C 1 | C4     |     |
| A C F G   |          |        |     |      |       |                |     |     |     | 11     |     |
GGPPUU GGPPUU GGPPUU GGPPUU 3 F D R A M Disk Bu ff er snaps ho t
| B D E F |     |     | 2   | CCPPUU |     | C ac he miss            |     |      |     |            |      |
| ------- | --- | --- | --- | ------ | --- | ----------------------- | --- | ---- | --- | ---------- | ---- |
|         |     |     |     | 4      | E   | A Prw evr ii tot uensly |     | 1 C0 | C2  | C 3 C 5 C2 | C3 2 |
R e a d A
Figure10:Asynchronousgraphconstructionframework.
|     |     |     |     |     |     | AAA Merge Write                       | AA  | 4 C1                              | C2  | C4 C5 C2 | C4 3 |
| --- | --- | --- | --- | --- | --- | ------------------------------------- | --- | --------------------------------- | --- | -------- | ---- |
|     |     |     |     |     |     | (a) Cache hit and miss demonstration. |     | (b) Cluster dispatching strategy. |     |          |      |
Algorithm3:ThemergingworkflowofCPU. Figure11:Cachemechanismbasedonclusterdispatching.
Input:clusterset𝐶𝑆
Output:globalgraphindex𝐺
1 Initialize𝑛𝑒𝑖𝐿𝑜𝑐[𝑣]foreachnode𝑣inthedatasetas𝑛𝑢𝑙𝑙;
Theasynchronousgraphconstructionframeworkestablishesa
| foreachcluster𝐶 | ∈𝐶𝑆do |     |     |     |     |                                                        |     |     |     |     |     |
| --------------- | ----- | --- | --- | --- | --- | ------------------------------------------------------ | --- | --- | --- | --- | --- |
| 2               |       |     |     |     |     | heterogeneouscomputingpipelinewhereGPUsfocusonparallel |     |     |     |     |     |
WaitingfortheGPUtotransferthelocalindex𝐿𝐼;
| 3   |     |     |     |     |     | localindexconstructionandCPUsconcurrentlymergepartialin- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | -------------------------------------------------------- | --- | --- | --- | --- | --- |
4 foreachnode𝑣 ∈𝐶do dexes. It utilizes the computing resources of CPUs and employs
| 5   | if𝑛𝑒𝑖𝐿𝑜𝑐[𝑣] =𝑛𝑢𝑙𝑙then |     |     |     |     |     |     |     |     |     |     |
| --- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
RAMasadynamiccachetoreducediskI/Ooverhead.
|     | // Fetch | the neighbor | list | pointer | of 𝑣 |     |     |     |     |     |     |
| --- | -------- | ------------ | ---- | ------- | ---- | --- | --- | --- | --- | --- | --- |
Discussion.WhilemergingsubgraphsontheGPUandstream-
𝑛𝑒𝑖𝐿𝑜𝑐[𝑣] ←𝐿𝐼[𝑣];
| 6   |     |     |     |     |     | ingthemdirectlytoNVMeSSDspresentsanappealingoptimiza- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ----------------------------------------------------- | --- | --- | --- | --- | --- |
7 else tion,weavoidGPU-to-NVMeSSDdatatransferstoprioritizebroad
// Neighbor list of 𝑣 resides in disk accessibilityofourframework.ThedirectaccessofGPU-SSDisa
|     | if𝑛𝑒𝑖𝐿𝑜𝑐[𝑣] | =−1then |     |     |     |     |     |     |     |     |     |
| --- | ----------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
8 featurelimitedtodata-center-gradeGPUs(e.g.,NVIDIAA100/H100)
9 Loadneighborlistof𝑣into𝑛𝑒𝑖𝐿𝑜𝑐[𝑣]; and remains unsupported on widely used consumer-grade hard-
𝑛𝑒𝑖𝐿𝑜𝑐[𝑣] ←𝑚𝑒𝑟𝑔𝑒(𝑛𝑒𝑖𝐿𝑜𝑐[𝑣],𝐿𝐼[𝑣]); ware(e.g.,NVIDIARTX3090/4090),whichwouldsignificantlylimit
10
ifCacheinRAMisfullthen practicaladoption.Additionally,GPU-basedsubgraphmergingne-
11
cessitatesretainingatleasttwosubgraphsinGPUmemory;other-
|     | // Evict a | local index | to  | disk |     |     |     |     |     |     |     |
| --- | ---------- | ----------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
foreachnode𝑢intheevictedlocalindexdo wise,itwouldintroduceadditionaldatatransferfromCPUorSSD
12
Write𝑛𝑒𝑖𝐿𝑜𝑐[𝑢]todisk; toGPU. However, storingtwosubgraphscanfurther reducethe
13
|     |               |     |     |     |     | already limitedGPU | memory, which | negatively |     | impactsthe | effi- |
| --- | ------------- | --- | --- | --- | --- | ------------------ | ------------- | ---------- | --- | ---------- | ----- |
| 14  | 𝑛𝑒𝑖𝐿𝑜𝑐[𝑢]←−1; |     |     |     |     |                    |               |            |     |            |       |
ciencyofindexconstruction.
Toaddressthesechallenges,weproposeanasynchronouscon-
6.2 Cluster-awareCachingMechanism
structionframeworkthatintegratestheCPUintothepipelineand
repurposes RAM as a cache to reduce I/O bottlenecks. As illus- InSection6.1,weallocateacacheinRAMtoreducetheI/Oover-
tratedinFigure10,afterdistributingthedataintoclustersviak- headbetweentheCPUanddisk.AsdepictedinFigure11(a),ifthe
meansasDiskANNdoes,TagorestreamstheseclusterstoGPUsfor neighborlistofnode𝐴residesinRAM,thecacheishit.Inthissit-
distributedlocalindexconstruction.Itsupportsmulti-GPUparal- uation,theneighborlistsofthe𝐴canbemergeddirectlyinRAM
lelism,enablingsimultaneousconstructionacrossmultipleGPUs. (line10inAlgorithm3).Ontheotherhand,iftheneighborlistof
EachGPUispairedwithadedicatedCPUthreadthatorchestrates 𝐴residesindisk(Figure11(b)),wehavetoloadtheneighborlist
datatransfersandexecutioncontrol.Uponcompletingalocalin- previously written from the disk (lines 8-9 in Algorithm 3), and
dex,theCPUthreadwritestheindex toRAMwhiletransferring thenmergeitwiththecurrentneighborlist(line10inAlgorithm
thenextclustertotheGPU,ensuringcontinuousGPUutilization. 3).Ascomparedtothecachehitsituation,thecachemisssituation
Concurrently, the CPUinitiates themerging processfor local triggerstheexecutionoflines8-9inAlgorithm3,whichrequires
indexesstoredinRAM,asformalizedinAlgorithm3.Tagoremain- twoextraI/Ooperations(theloadingof𝑣’sneighborlistfromdisk
tains an array 𝑛𝑒𝑖𝐿𝑜𝑐 to track the memory offsets of all nodes’ andpreviouslywrittentodisk).
neighbor lists. The CPU merges local indexes by scanning each Thecachehitrateisintrinsicallytiedtothenumberofoverlap-
node𝑣inthecluster(line4).Whenanodeisfirstvisited,itsneigh- pingnodesretained inRAM.Thus,theclusterschedulingpolicy
bor list location is recorded in𝑛𝑒𝑖𝐿𝑜𝑐 (lines 5-6). For previously (determiningtheorderinwhichclustersareloadedintoorevicted
visitednodes,theCPUverifieswhethertheneighborlistfromthe fromthecache)iscriticalformaximizingcacheefficiency.Tofor-
prioraccesshasbeenpersistedtodisk(line8).Ifyes(indicatedby malizethis,asdepictedinFigure11(b),wemodelclustersasver-
value-1of𝑛𝑒𝑖𝐿𝑜𝑐[𝑣]),itfetchesthelistfromdisk(line9).Other- ticesinanundirectedgraph𝐶𝐺,whereanedgebetweenclusters
wise,theneighborlistof𝑣 mustbecached.TheCPUretrieves it 𝐶𝑖 and𝐶𝑗 existsiftheysharenodes,withedgeweight𝑊(𝐶𝑖,𝐶𝑗)
andmergestheexistingneighborlistwiththecurrentone(line10). representingthenumberofsharednodes.Givenacachecapacity
Whenthecachereachesitsfullcapacity,theCPUevictsoneofthe of𝑛localindexes,ourobjectivereducestoagraphtraversalprob-
localindexes𝐿𝐼 inthecacheintothedisk,usingthemechanism lem: selecting a sequence of vertices that maximizes cumulative
introducedinSection6.2(lines11-14). edgeweights(i.e.,overlappingnodes)withinaslidingwindowof

SIGMOD’26,May31–June05,2026,Bengaluru,India ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao
|     |     |     |     |     |     | Table2:DetailsofDatasets.𝑁 |     |     |     | and𝑁𝑞 denotethenumberof |     |     |     |
| --- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- | ----------------------- | --- | --- | --- |
Algorithm4:Cluster-awaredispatchingstrategy.
|     |     |     |     |     |     | dataandqueryvectors.𝐷 |     |     | denotesthevectordimension. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --------------------- | --- | --- | -------------------------- | --- | --- | --- | --- |
Input:clustergraph𝐶𝐺(𝐶,𝐸),cachesize𝑛
Output:dispatchingorder𝑅
|     |     |     |     |     |     | Datasets |     | N   |     | D   | Size(GB) | Nq  |     |
| --- | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | -------- | --- | --- |
/* Initialize with the first cluster */ Deep-1M[7] 1,000,000 96 0.36 10,000
1 𝑏𝑢𝑓 ←{𝐶[0]};𝐶 ←𝐶−{𝐶[0]};𝑅←∅; SIFT[2] 1,000,000 128 0.48 10,000
| while|𝑏𝑢𝑓| | <𝑛do |     |     |     |     | UKBench[45] |     | 1,097,907 |     | 128 | 0.52 | 200 |     |
| ---------- | ---- | --- | --- | --- | --- | ----------- | --- | --------- | --- | --- | ---- | --- | --- |
2
𝐶∗←ar Í C o l o r [ 1] 1 , 0 0 0 , 0 0 0 2 8 2 1 . 0 5 1 0 ,0 0 0
| 3   | g m ax 𝐶𝑗∈𝑏𝑢𝑓 | 𝑊(𝐶𝑖,𝐶𝑗); |     |     |     |              |     |           |         |       |         |      |     |
| --- | ------------- | --------- | --- | --- | --- | ------------ | --- | --------- | ------- | ----- | ------- | ---- | --- |
|     | ∈𝐶            |           |     |     |     | G is t [ 2 ] |     | 1 , 0 0 0 | , 0 0 0 | 9 6 0 | 3 . 5 8 | 1 ,0 | 0 0 |
𝐶 𝑖
𝑏𝑢𝑓 ←𝑏𝑢𝑓 ∪{𝐶∗};𝐶 ←𝐶−{𝐶∗},𝑅←𝑅∪{(𝐶∗,𝑛𝑢𝑙𝑙}; BIGANN[2] 1,000,000,000 128 119.21 10,000
4
|     |     |     |     |     |     | Deep-1B[7] |     | 1,000,000,000 |     | 96  | 357.63 | 10,000 |     |
| --- | --- | --- | --- | --- | --- | ---------- | --- | ------------- | --- | --- | ------ | ------ | --- |
5 while𝐶isnotemptydo
| 6 𝐶∗,𝐶′← | argmax | (Í 𝐶𝑘∈(𝑏𝑢𝑓−{𝐶′}) |     | 𝑊(𝐶∗,𝐶 | )); |     |     |     |     |     |     |     |     |
| -------- | ------ | ---------------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝑘
𝐶∗∈𝐶,𝐶′∈𝑏𝑢𝑓
| 7 𝑏𝑢𝑓 | ←𝑏𝑢𝑓 −{𝐶′},𝑏𝑢𝑓 | ←𝑏𝑢𝑓 | ∪{𝐶∗}; |     |     |     |     |     |     |     |     |     |     |
| ----- | -------------- | ---- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝐶←𝐶−{𝐶∗},𝑅←𝑅∪{(𝐶∗,𝐶′)};
8
thedatavectors.Table2summarizesthedetailedpropertiesofeach
9 returnR
dataset.
|     |     |     |     |     |     | Methods | and | parameters. | We  | evaluate | our method | against | 7   |
| --- | --- | --- | --- | --- | --- | ------- | --- | ----------- | --- | -------- | ---------- | ------- | --- |
𝑛vertices.Thisisequivalenttoprioritizingverticeswithhighin-
open-sourcedgraph-basedbaselinesonGPUandCPUplatforms.
terconnectivity, ensuring maximal reuse ofcached nodes during Theexperimentalsettings,includinggraphdegrees,thresholds(as
merging. peroriginalpapers),threadcountsforconstructionandquery,and
Toachievethisgoal,wetraversethegraphusingagreedystrat- platforms(CPUorGPU),aresummarizedinTable3.Forfaircom-
egythatprioritizesclusterswiththehighestcumulativeedgeweights parison,wefixthenumberofCPUthreadsforindexconstruction
relativetothosealreadyinthecache.Thepseudo-codeforthispro-
|                                                           |     |     |     |     |     | and queryat      | 20  | and 1,respectively. |     | The comparedbaselines |     |     | are |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | ---------------- | --- | ------------------- | --- | --------------------- | --- | --- | --- |
| cessispresentedinAlgorithm4.Webeginbyinitializingthecache |     |     |     |     |     | listedasfollows. |     |                     |     |                       |     |     |     |
witharandomcluster(e.g.,thefirstclusterinourimplementation), (1)CAGRA[48]isthestate-of-the-artgraphindexingmethodac-
whichhasminimalimpactonitsperformance(line1).Next,theal- celeratedbyGPU.Tagore-CAGRAoptimizesCAGRAwithTagore.
gorithmiterativelyselectstheclusterin𝐶thatmaximizesthesum WeemploythequeryapproachinCAGRAusingtheGPUtoeval-
ofedgeweights,untilthecachereachesitsfullcapacity(lines2-4).
uatethequalityofindexesconstructedbybothmethods.
Whenacluster𝐶∗isidentified,itisremovedfromtheclusterset
|     |     |     |     |     |     | (2) GANNS | [72] | is the | state-of-the-art | increment-based |     | method |     |
| --- | --- | --- | --- | --- | --- | --------- | ---- | ------ | ---------------- | --------------- | --- | ------ | --- |
𝐶 (whichcorrespondstothevertexsetoftheclustergraph),and thatacceleratestheconstructionofHNSWusingtheGPU.
atuple(𝐶∗,𝑛𝑢𝑙𝑙)isappendedtothedispatchingorderset𝑅(line
(3)SymQC[22]isthestate-of-the-artgraphindexingmethodac-
4). Notethat each tuple (𝐶1,𝐶2) ∈ 𝑅 denotes the loadedcluster celeratedbyquantizationand SIMDinstructiononCPUs.It ran-
𝐶1and,ifapplicable,theevictedcluster𝐶2.Oncethecacheisfull,
domlyinitializesagraph,iterativelycollectscandidatesforevery
loadingadditionalclustersrequiresevictingexistingones.Tode-
node,andemploysthepruningstrategyinNSG[18]tofilterthe
terminewhichclustersinthecachetoevictandwhichclustersin candidates.Forafaircomparison,weemploythequeryapproach
𝐶toload,weidentifytwoclusters:𝐶∗∈𝐶and𝐶′∈𝑏𝑢𝑓,suchthat
inNSGinsteadofthatinSymQCwithquantizationoptimization
Í 𝐶𝑘∈(𝑏𝑢𝑓−{𝐶′}) 𝑊(𝐶∗,𝐶 ) ismaximized(line7).Thisprocessof toevaluatethequalityofindexes.
𝑘
loadingnewclustersintothecachewhileevictingexistingclusters (4) NSG [18] is a CPU-based method employing distance-based
continuesuntilalltheclustersareloaded.
pruningstrategy.Tagore-NSGisitsoptimizedversioninTagore.
Example.Figure11(b)depictsasimpleexampleofthedispatching (5)NSSG[17]isarefinement-basedmethodadoptingangle-based
strategy. The buffer size is 3, and there are a total of 6 clusters. pruningstrategy.Tagore-NSSGisavariantacceleratedbyTagore.
Thecacheisinitializedwith𝐶0andappendedwith(𝐶2,𝑛𝑢𝑙𝑙)and (6)DPG[36]isanotherrefinement-basedmethodemployingangle-
(𝐶3,𝑛𝑢𝑙𝑙)inturn.Nowthecacheisfull,and subsequentloading based pruning strategy. Tagore-DPG optimizes this method on
| oflocalindexes | requiresevictionofexisting |     |     | ones. Next,𝐶5 | ∈ 𝐶 |     |     |     |     |     |     |     |     |
| -------------- | -------------------------- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
theGPU.
and𝐶0∈𝑏𝑢𝑓
areselectedbasedonthecriterionlistedonline6of (7)Vamana[28]isdesigned forindexinglarge-scaledatasetsin-
Algorithm4.Accordingly,𝐶0isevictedand𝐶5isloadedasshown tegratedinDiskANN.Tagore-Vamanaoptimizesthismethodon
inbuffersnapshot②.Similarly,wegetbuffersnapshot③and④. the GPU-CPU-disk asynchronous framework. We compare both
|     |     |     |     |     |     | methods | on the | two billion-scale |     | datasets | in Table | 2. The | prun- |
| --- | --- | --- | --- | --- | --- | ------- | ------ | ----------------- | --- | -------- | -------- | ------ | ----- |
7 Experiments
|     |     |     |     |     |     | ing parameter𝛼 |     | is set to | 1.2, and | the maximal | degree | is 32. | For |
| --- | --- | --- | --- | --- | --- | -------------- | --- | --------- | -------- | ----------- | ------ | ------ | --- |
Inthissection,weevaluatetheperformanceofTagoreandconduct DiskANN, bothdatasets are partitioned into 40 clusterswith an
comparativeevaluationswithexistinggraphindexingmethods. averagesizeof50M,while400clusterswithanaveragesizeof5M
forTagoreduetothelimitedGPUmemorycapacity.Moreover,we
7.1 ExperimentSettings allocate24GBofmemorytostorethelocalindexesontheCPU
| Datasets.Forcomprehensiveevaluations,weuse7real-worlddatasets, |     |     |     |     |     | forbothmethods. |     |     |     |     |     |     |     |
| -------------------------------------------------------------- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- |
including5million-scaleand2billion-scale,whichhavebeenwidely Metrics. To quantify the index construction time of the bench-
usedinrelatedworks[8,18,22,28,48,61].Forthedatasetsthat marked methods, we measure their index construction time. In-
dexqualityisevaluatedviatwometrics:QueriesPerSecond(QPS)
don’tprovidethequeryvectors,werandomlysamplethemfrom

ScalableGraphIndexingusingGPUsforApproximateNearestNeighborSearch SIGMOD’26,May31–June05,2026,Bengaluru,India
Tagore-CAGRA (A) CAGRA (B) GANNS (C) SymQG (D) Tagore-NSG (E) NSG (F) Tagore-NSSG (G) NSSG (H) Tagore-DPG (I) DPG (J)
)s( emiT noitcurtsnoC )s( emiT noitcurtsnoC )s( emiT noitcurtsnoC )s( emiT noitcurtsnoC )s( emiT noitcurtsnoC
|     | (a)Deep-1M |     |     | (b)SIFT |     | (c)UKBench |     |     | (d) | Color |     | (e)Gist |     |
| --- | ---------- | --- | --- | ------- | --- | ---------- | --- | --- | --- | ----- | --- | ------- | --- |
Figure12:Overallindexconstructiontimeonmillion-scaledatasets.
Tagore-CAGRA CAGRA GANNS Tagore-NSG SymQG NSG Tagore-NSSG NSSG Tagore-DPG DPG
| 105 |     |     |     | 105 |     | 105 |     | 105 |     |     | 104 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPQ |     |     |     | SPQ |     | SPQ |     | SPQ |     |     | SPQ |     |     |
| 104 |     |     |     |     |     | 104 |     |     |     |     | 103 |     |     |
|     |     |     |     | 104 |     |     |     | 104 |     |     |     |     |     |
| 103 |     |     |     | 103 |     | 103 |     | 103 |     |     | 102 |     |     |
0.84 0.88 0.92 0.96 1.00 0.84 0.88 0.92 0.96 1.00 0.84 0.88 0.92 0.96 1.00 0.84 0.88 0.92 0.96 1.00 0.80 0.84 0.88 0.92 0.96 1.00
|     | Recall @10 |     |     | Recall @10 |     | Recall @10 |     |     | Recall @10 |       |     | Recall @10 |     |
| --- | ---------- | --- | --- | ---------- | --- | ---------- | --- | --- | ---------- | ----- | --- | ---------- | --- |
|     | (a)Deep-1M |     |     | (b)SIFT    |     | (c)UKBench |     |     | (d)        | Color |     | (e)Gist    |     |
Figure13:Indexqualityonmillion-scaledatasets.
Table3:Experimentalsettingsofthecomparedalgorithms.
workloadachievedbythebalanced-parallelmodel.Notably,inFig-
Parm.isshortforParameters,Constr.isshortforConstruc-
ure12,theindexconstructiontimeofTagoreincreasesondataset
tion,and𝑡 inCPU(𝑡)denotesthenumberofthreads. Gist, which has an extremely high dimension of 960, as our op-
|     |             |         |       |               |     |        | timizations | focuson  |             | algorithmic   | improvements | rather       | than low- |
| --- | ----------- | ------- | ----- | ------------- | --- | ------ | ----------- | -------- | ----------- | ------------- | ------------ | ------------ | --------- |
|     | Parm. CAGRA | GANNS   | SymQC | NSG NSSG      | DPG | Vamana |             |          |             |               |              |              |           |
|     |             |         |       |               |     |        | level       | distance | computation | enhancements. |              | The distance | calcula-  |
|     | =32         |         | =32   |               | =32 |        |             |          |             |               |              |              |           |
|     | Degree      | [32,64] |       | (0,50] (0,50] |     | (0,32] |             |          |             |               |              |              |           |
tionoptimizations(e.g.,usingPTXassemblyinstructions)remain
|     | Constr. GPU | GPU | CPU(20)CPU(20)CPU(20) |               | CPU(20) | CPU(20) |               |     |     |     |     |     |     |
| --- | ----------- | --- | --------------------- | ------------- | ------- | ------- | ------------- | --- | --- | --- | --- | --- | --- |
|     | Query GPU   | GPU | CPU(1)                | CPU(1) CPU(1) | CPU(1)  | CPU(1)  | asfuturework. |     |     |     |     |     |     |
Others - - - - 𝛾=60 - 𝛼=1.2 ToevaluatethequalityofindexesconstructedusingTagorever-
|     |     |     |     |     |     |     | susbaseline | methods,we |     | measure | queryperformance |     | (accuracy |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | --- | ------- | ---------------- | --- | --------- |
andefficiency)usingeachmethod’snativequeryimplementation.
andRecall,whichreflectthequeryefficiencyandaccuracy,respec-
ThequeryperformanceisexhibitedinFigure13.Pleasenotethat
tively.QPSisdefinedasthenumberofqueriesprocessedpersec-
thequerymethodsareconsistentwithinthebaselineindexingmethod
| ond,whileRecall |     | iscalculatedby |     | |𝐺∩𝑅| ,where𝐺 | istheground- |     |     |     |     |     |     |     |     |
| --------------- | --- | -------------- | --- | ------------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
𝑘 and the corresponding methods in Tagore (e.g., NSG vs. Tagore-
truthtop-𝑘nearestneighborsand𝑅isthesearchresults. NSG)butdifferacrossdifferenttypesofindexes(seeSection7.1).
Platforms. All experiments are conducted on an Ubuntu 22.04 Thus,resultscanonlybeusedtocomparethequalitybetweenin-
server,featuringanIntelXeonSilver4316CPU@2.30GHz,251GB
dexesconstructedbythebaselinemethodandthecorresponding
RAM,andaNvidiaGeForceRTX4090GPU(24G).Weimplement
methodinTagore(e.g.,NSGandTagore-NSG)butnotacrossdis-
TagoreinC++/CUDAunderCUDA12.2andintegrateitintoPython.
tinctindextypes(e.g.,NSGvs.NSSG).AsshowninFigure13,the
indexesconstructedbyTagoreachievecomparablerecallandQPS
7.2 OverallIndexingPerformance totheirbaselinecounterparts,whichdemonstratesthatTagoreac-
| 7.2.1 |          |             |     |                  |           |      | celeratesconstructionwithoutdegradingindexquality. |     |     |     |     |     |     |
| ----- | -------- | ----------- | --- | ---------------- | --------- | ---- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|       | Indexing | performance |     | on million-scale | datasets. | Fig- |                                                    |     |     |     |     |     |     |
ure12summarizestheindex constructiontimeacrosstheevalu- 7.2.2 Indexingperformanceonbillion-scaledatasets. Figure
atedmethods.Allrefinement-basedindexesacceleratedbyTagore 14comparestheindexingperformanceofTagoreandDiskANN[28]
demonstrate superior performance, outperforming the baselines on billion-scale datasets. Overall, the indexing time of Tagore is
bysignificantmargins.ComparedtoGPU-basedmethods,Tagore- 6.68×and6.00×lessthanthatofDiskANNondatasetsBIGANN
CAGRA achieves speedups of 1.32× to 6.39× over CAGRA and andDeep-1B,respectively.Tagorereducestheindexconstruction
1.99×to10.14×overGANNS,whichhighlightsthesuperiorityof timeofbillion-scaledatasetsfrom14hourstounder 3hoursus-
ourdesignedGPU-specificalgorithms(e.g.,GNN-descentandpar- ingasingleGPU,meetingnightlyindexrebuildrequirements.As
allel filtering kernels). Against CPU-based SymQC, which lever- showninthetimebreakdown(Figure14),thedatatransferover-
agesSIMDoptimizations,Tagore-NSGattains11.74×to47.73×faster headfromCPUtoGPUisinsignificant,accountingforonly3%-5%
construction.Furthermore,TagoreacceleratesNSG,NSSG,andDPG ofthewholeindexconstructiontime.Differentfromthequerypro-
by36.23×to64.42×,43.51×to112.79×,and21.10×to51.31×,re- cess,indexingrequiresinfrequentdataexchangebetweentheCPU
spectively.WhileallfourTagore-enhanced methodsexhibitcom- andGPU.Consequently,theGPUisaviableacceleratorforindex
parableindexingtimes,Tagore-CAGRAshowsmarginalefficiency construction,featuringlowdatamovementoverheadandhighin-
gainsduetoitsGPU-friendlyanddistance-freepruningstrategy. dexconstructionefficiency.InDiskANN,localindexconstruction
On average, Tagore-CAGRA achieves a 4.65× speedup over the isthemosttime-consumingprocedureduringtheindexconstruc-
state-of-the-artGPU-basedmethodCAGRA,whichcanbeattrib- tionofbillion-scale datasets,whichdemands substantial calcula-
utedtotherapidconvergenceofGNN-Descentandthebalanced tions.Incontrast,thisbottleneckiswellovercomebytheGPUin

SIGMOD’26,May31–June05,2026,Bengaluru,India ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao
| α(5.1%)β(49.1%) |            |         | α(3.4%)  | β(55.7%)    |                 |          | Tagore |     |      | DiskANN |     |     |
| --------------- | ---------- | ------- | -------- | ----------- | --------------- | -------- | ------ | --- | ---- | ------- | --- | --- |
|                 | γ(45.8%)   |         |          | γ(40.9%)    |                 |          |        |     |      |         |     |     |
| Tagore          |            |         | Tagore   |             |                 |          |        |     |      |         |     |     |
| 7581.45s        |            | η(0.9%) | γ(11.4%) | 8601.61s    | η(2.6%)γ(11.1%) | 300      |        |     | 75   |         |     |     |
| DiskANN         | β(87.7%)   |         | DiskANN  | β(86.3%)    |                 |          |        |     |      |         |     |     |
|                 |            |         |          |             |                 |  SPQ 200 |        |     |  SPQ |         |     |     |
|                 | 50667.29s  |         |          | 51619.49s   |                 |          |        |     | 50   |         |     |     |
|                 | (a) BIGANN |         |          | (b) Deep-1B |                 |          |        |     |      |         |     |     |
|                 |            |         |          |             |                 | 100      |        |     | 25   |         |     |     |
Figure14:Indexconstructiontimeonbillion-scaledatasets.
|     |     |     |     |     |     | 0   |     |     | 0   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝛼 denotesthedatatransfer overheadfrom CPUtoGPU,𝛽 0.92 0.94 0.96 0.98 1.00 0.92 0.94 0.96 0.98 1.00
denotesthelocalindexconstructionoverhead,𝜂denotesthe Recall @1 Recall @1
|                                  |     |     |     |                    |     |     | (a)BIGANN |     |     | (b)Deep-1B |     |     |
| -------------------------------- | --- | --- | --- | ------------------ | --- | --- | --------- | --- | --- | ---------- | --- | --- |
| writingoverheadoflocalindex,and𝛾 |     |     |     | denotesthelocalin- |     |     |           |     |     |            |     |     |
dexmergingoverheadtothedisk.
Figure15:Indexqualityonbillion-scaledatasets.
| Table 4: | Local | index construction |     | overhead | with multiple |             |     |      |                    |     |                    |     |
| -------- | ----- | ------------------ | --- | -------- | ------------- | ----------- | --- | ---- | ------------------ | --- | ------------------ | --- |
|          |       |                    |     |          |               | GNN-Descent |     | GNND | GNN-Descent Phase1 |     | GNN-Descent Phase2 |     |
GPUs.𝑎inTagore-𝑎denotesthenumberofGPUs.
1.0
1.0
| Datasets | DiskANN   |     | Tagore-1 | Tagore-2 | Tagore-4 |        |     |     |        |     |     |     |
| -------- | --------- | --- | -------- | -------- | -------- | ------ | --- | --- | ------ | --- | --- | --- |
|          |           |     |          |          |          | llaceR |     |     | llaceR |     |     |     |
|          |           |     |          |          |          | 0.9    |     |     | 0.9    |     |     |     |
| BIGANN   | 44456.13s |     | 3721.08s | 1850.90s | 933.65s  |        |     |     |        |     |     |     |
| Deep-1B  | 44538.57s |     | 4791.77s | 2454.39s | 1231.46s |        |     |     |        |     |     |     |
|          |           |     |          |          |          | 0.8    |     |     | 0.8    |     |     |     |
Tagore.Tagoreimprovesthelocalindexconstructionby11.9×and
|     |     |     |     |     |     | 0.7 |     |     | 0.7 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
9.3×overDiskANNonBIGANNandDeep-1B,respectively.More- 0 2 4 6 8 10 2 4 6 8 10
|     |     |     |     |     |     |     | Execution Time (s) |     |     | Execution Time (s) |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --- | ------------------ | --- | --- |
over,whilemerginglocalindexesintotheglobalindexisnotthe (a)SIFT (b)Color
bottleneckinDiskANN,itbecomesthebottleneckinTagoredue
Figure16:PerformancecomparisonofNN-DescentonGPU.
| to the efficient  | construction |          | of local   | indexes. The | cluster-aware   |     |     |     |     |     |     |     |
| ----------------- | ------------ | -------- | ---------- | ------------ | --------------- | --- | --- | --- | --- | --- | --- | --- |
| caching mechanism |              | proposed | in Section | 6.2 plays    | a critical role |     |     |     |     |     |     |     |
convergencerates,demonstratingtheeffectivenessofourtheory
inreducingthemergingoverhead,whichwillbefurtheranalyzed
proposedinSection4.Withthefine-grainedsamplinginthesec-
inSection7.5.
|     |     |     |     |     |     | ond phase, | GNN-Descent | can | maintain | a high | convergence | rate |
| --- | --- | --- | --- | --- | --- | ---------- | ----------- | --- | -------- | ------ | ----------- | ---- |
Tofurtherimprovecomputationalefficiencyandscalability,Tagore evenathighrecall(>95%),significantlyenhancingtheefficiencyof
supportsindexconstructionwithmultipleGPUs.Sincemulti-GPU NN-DescentonGPUs.Furthermore,althoughneithersingle-phase
indexconstructiondoesn’timpactthemergingphase,weonlyre-
|                 |     |              |                              |     |     | variant outperforms |     | GNN-Descent, | both | are superior | to  | GNND. |
| --------------- | --- | ------------ | ---------------------------- | --- | --- | ------------------- | --- | ------------ | ---- | ------------ | --- | ----- |
| porttheoverhead |     | oflocalindex | constructioninTable4.Results |     |     |                     |     |              |      |              |     |       |
ThisisbecauseweoffloadalltheoperationsofNN-Descentonto
| demonstrateTagore’s |     | abilityofnear-linear |     | scaling: | theconstruc- |     |     |     |     |     |     |     |
| ------------------- | --- | -------------------- | --- | -------- | ------------ | --- | --- | --- | --- | --- | --- | --- |
theGPU,eliminatingtheoverheadofCPU-GPUsynchronization
tiontimedecreaseslinearlywiththeincreasingnumberofGPUs. anddatatransfer.Moreover,weoptimizetheneighborupdatesby
With4GPUs,Tagorereduceslocalindexconstructionoverheadby proposingalock-freemergingstrategy,effectivelyimprovingthe
47.7×and36.17×onBIGANNandDeep-1BcomparedtoDiskANN,
efficiencyofneighborupdatesinGNN-Descent.
whilethespeedupsare24.0×and18.1×with2GPUs.
InGNN-Descent(Algorithm1),theparameters𝑖𝑡1and𝑖𝑡2define
Weevaluatetheglobalindexqualityusingthequerymethodin
|     |     |     |     |     |     | the number | of iterations | required | in two | distinct | phases. | While |
| --- | --- | --- | --- | --- | --- | ---------- | ------------- | -------- | ------ | -------- | ------- | ----- |
DiskANNonaSamsung980SSD(1TB).Thequeryperformance selecting an appropriate total number of iterations (𝑖𝑡1 +𝑖𝑡2) is
onbothdatasetsisdepictedinFigure15.Whentherecallisgreater relativelystraightforward–userscanadjustitaccordingtotheir
than95%,thedifferenceinrecallbetweenTagoreandDiskANNun- desiredrecall–thedifficultyliesindetermining howtoallocate
derthesameQPSisonlywithin1.4%.Whentherecallisgreater
|     |     |     |     |     |     | iterations | between the | two phases. | To  | explorethe | impact | of dif- |
| --- | --- | --- | --- | --- | --- | ---------- | ----------- | ----------- | --- | ---------- | ------ | ------- |
than98%,thisgapnarrowsdownto0.5%,whichistolerable.The
ferentallocationstrategies,weevaluatetheperformanceofGNN-
indexqualityconstructedbyTagoreisslightlylowerthanthatof Descent by keeping the total iteration count 𝑖𝑡1 +𝑖𝑡2 fixed and
DiskANNbecauseTagorepartitionsthedatasetsinto400clusters varyingthedistributionbetween𝑖𝑡1and𝑖𝑡2ontworepresentative
duetothelimitationofGPUmemory,whileDiskANNpartitions datasets.AsshowninFigure17,whenthetotaliterationcountis
theminto40clusters.Moreclustersareharmfultotheglobalneigh-
fixedat8,12,or16,therecallonbothdatasetsincreasesinitially
borrelationshipsoftheindex.
andthendecreases,whiletheexecutiontimeexhibitsanopposite
|     |     |     |     |     |     | trend, as we | increase𝑖𝑡2 | (and | decrease𝑖𝑡1). | This | aligns | withthe |
| --- | --- | --- | --- | --- | --- | ------------ | ----------- | ---- | ------------- | ---- | ------ | ------- |
7.3 EvaluationofGNN-Descent
observationinFigure16,wheretherecallachievedduringPhase1
ToevaluatetheGNN-DescentalgorithmproposedinSection4,we plateausafterreachingahighvalue,eveniftheexecutiontimeis
benchmarkGNN-Descentagainstthestate-of-the-artGPU-based furtherextended.Thisoccursbecause,when𝑖𝑡1islarge,thelater
NN-Descentalgorithm,GNND[61],implementedincuVS[46].Fig- iterationsinthefirstphaseinvolvemanydistancecalculationsbut
ure16comparestheirperformanceontworepresentativedatasets, contributeonlyminimalneighborupdates.Introducingmoreiter-
includingtwosingle-phasevariantsofGNN-Descent.GNN-Descent ationsinthesecond phaseenables GNN-Descent tocontinuere-
achievesspeedupsof6.7×and4.0×overGNNDontherespective finingneighborsinamorefine-grainedmanner,therebyimprov-
datasets.AsobservedinFigure16,thefirstphaseofGNN-Descent ingtherecallvalue.However,if𝑖𝑡1becomessignificantlysmaller
convergesrapidlycomparedtothesecondphaseintheinitialiter- than𝑖𝑡2,thealgorithmtransitionstothesecondphasebeforesuf-
ations.Itsconvergencespeedslowsnear93%recallandfollowsa ficientrecallhasbeenachieved inthefirstphase.Theexecution
similartrendtoGNND.Incontrast,thesecondphasesustainshigh time of each Phase 2 iteration varies, as more neighbor updates

ScalableGraphIndexingusingGPUsforApproximateNearestNeighborSearch SIGMOD’26,May31–June05,2026,Bengaluru,India
it1+it2=8 it1+it2=12 it1+it2=16 Table6:Comparisonofcachehitratiobetweenvariousclus-
)s( emiT noitucexE 1.00 )s( emiT noitucexE 1.00 terdispatchingorders.
|     |     |     | 0.96   |     | 0.96        |          |            |        |        |        |
| --- | --- | --- | ------ | --- | ----------- | -------- | ---------- | ------ | ------ | ------ |
|     |     |     | llaceR |     | 0.92 llaceR |          |            |        |        |        |
|     |     |     | 0.92   |     |             | Datasets | Sequential | Random | Gorder | Tagore |
|     |     |     | 0.88   |     | 0.88        |          |            |        |        |        |
|     |     |     |        |     | 0.84        | BIGANN   | 13.1%      | 13.6%  | 24.9%  | 61.6%  |
0.84
|     |     |     | 0.80 |     | 0.80 | Deep-1B | 12.1% | 12.5% | 19.1% | 67.2% |
| --- | --- | --- | ---- | --- | ---- | ------- | ----- | ----- | ----- | ----- |
|     |     |     | 0.76 |     | 0.76 |         |       |       |       |       |
|     | it2 |     |      | it2 |      |         |       |       |       |       |
7.5 EvaluationofCachingMechanism
|     | (a)SIFT |     |     | (b)Color |     |     |     |     |     |     |
| --- | ------- | --- | --- | -------- | --- | --- | --- | --- | --- | --- |
Figure17:Impactsofiterationcounts𝑖𝑡1and𝑖𝑡2ontheeffec- InDiskANN,thelocalindexesarefirstwrittentothediskandthen
tivenessofonGNN-Descent.Barsandlinesrepresentexecu- merged,requiringthreeCPU-diskI/Ooperationspernode.Asde-
tiontimeandrecall,respectively.
pictedinFigure14,thewritingandmergingoverheadofDiskANN
is6211.16sand7080.92sontheBIGANNandDeep-1Bdatasets,re-
Table5:Pruningoverheadoftherefinement-basedmethods
spectively.WhilethisoverheadissecondarytoDiskANN’sdomi-
(unit:second).OdenotesthatoftheoriginalmethodsandT
nantlocalindexingcosts,itbecomesthemainbottleneckinTagore,
denotestheexecutiontimeofTagore.
whereI/Ooverheadsurpasseslocalindexingcosts.Toaddressthis
|     | CAGRA |     | NSG | NSSG | DPG |     |     |     |     |     |
| --- | ----- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
Dataset issue, Tagore merges theneighbor listsofnodesinthecache di-
|     | O   | T   | O   | T O T | O T |     |     |     |     |     |
| --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- |
rectly,eliminatingtheneedforwritingtodiskfirstandreducing
| Deep-1M | 1.33 | 0.07 | 39.55 | 0.51 80.57 0.45 | 5.98 0.27 |           |               |                     |           |             |
| ------- | ---- | ---- | ----- | --------------- | --------- | --------- | ------------- | ------------------- | --------- | ----------- |
|         |      |      |       |                 |           | the disk  | I/O overhead. | Moreover, Tagore    | pipelines | the merging |
| SIFT    | 1.16 | 0.07 | 37.18 | 0.50 102.300.48 | 6.87 0.27 |           |               |                     |           |             |
|         |      |      |       |                 |           | procedure | on the CPU    | with local indexing | on the    | GPU. Conse- |
| UKBench | 1.43 | 0.08 | 37.55 | 0.50 103.370.47 | 7.39 0.30 |           |               |                     |           |             |
quently,themergingoverheadisreducedto3475.95sand3521.04s
| Color | 1.20 | 0.07 | 111.610.98 | 184.940.54 | 13.41 0.48 |     |     |     |     |     |
| ----- | ---- | ---- | ---------- | ---------- | ---------- | --- | --- | --- | --- | --- |
Gist 1.36 0.07 239.261.87 323.221.66 37.32 1.45 forthetwobillion-scaledatasets,achievingspeedupratiosof1.79×
and2.01×,respectively,demonstratingtheeffectivenessofourpro-
leadtolongerexecutiontimes.AsshowninFigure16,Phase2is posedcluster-basedcachingmechanism.
lesseffectiveatimprovingindexqualitywhenrecallislow.As𝑖𝑡2 The key innovation of our cluster-aware caching mechanism
increases, the earlier iterations yield poorindex quality,causing is the cluster dispatching order in Algorithm 4. To demonstrate
moreneighborstobeupdatedinlateriterations.Thisresultsina its superior performance, we compare it against three baselines:
higherexecutiontimeforthefinaliterations,whichconsequently sequential order, random order, and a state-of-the-art graph re-
increasestheoverallexecutiontime.Andfurtherincreasing𝑖𝑡2be- order algorithmGorder [67]. Gorder generates a permutationof
yondacertainpointleadstoreducedrecall. Tobalanceefficiency allnodesinagraphbasedonnodelocalitytominimizeCPUcache
andaccuracy,weset𝑖𝑡1 = 𝑖𝑡2 inallexperiments.Thisconfigura- misses. WeapplyGorder totheclustergraphdepictedin Figure
tionprovidesafavorabletrade-off,achievingstrongperformance
11(b).Table6presentsthecachehitratioforvariousclusterdis-
withlowcomputationaloverhead. patchingorders.Thesequentialorder,whichdispatchestheclus-
tersintheiroriginalsequence,yieldsthelowestcachehitratiosof
7.4 EvaluationofPruningOptimizations 13.1%and12.1%.Randomclusterdispatchingshowsamarginalim-
provementoversequentialorder.Gorderenhancesthelocalityof
Toassesstheefficacyofourproposedpruningoptimizations,we
clustersinthecache,leadingtoasignificantimprovementinthe
| benchmark | Tagore | against | the original | pruning strategies | listed |     |     |     |     |     |
| --------- | ------ | ------- | ------------ | ------------------ | ------ | --- | --- | --- | --- | --- |
inTable1.TheresultsareillustratedinTable5.Tagore achieves hitrate.However,itstillhaslimitations.Theclusterdispatching
speedupsof16.57×to19.43×,74.36×to127.95×,179.04×to342.48×, order in Tagore achieves hit ratesof 61.6%(BIGANN) and 67.2%
(Deep-1B),whichare2.47×and3.52×higherthanthoseofGorder.
22.15×to27.94×overthepruningphaseofCAGRA,NSG,NSSG,
Furthermore,Tagoregeneratesthedispatchingorderbeforeindex
| and DPG, | respectively. | Asmentioned |     | in Section5, | althoughCA- |               |      |                   |                 |            |
| -------- | ------------- | ----------- | --- | ------------ | ----------- | ------------- | ---- | ----------------- | --------------- | ---------- |
|          |               |             |     |              |             | construction, | with | overheads of just | 1.27s and 1.25s | on the two |
GRAperformsthepruningprocedureontheGPU,ithasnotfully
utilized the parallelism of the GPU and hence suffers a severely datasets,whichisnegligiblecomparedtothetotalindexconstruc-
| unbalancedworkload.Ourproposedbalanced-parallelcomputing |     |     |     |     |     | tiontime. |     |     |     |     |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- |
modelmitigatestheseissues,deliveringaccelerationofoveranor-
8 Conclusions
| der ofmagnitude. |     | For NSG, | NSSG, | and DPG, whichrely | heavily |     |     |     |     |     |
| ---------------- | --- | -------- | ----- | ------------------ | ------- | --- | --- | --- | --- | --- |
onincremental and compute-intensive distancecalculations,our Inthispaper,weintroduceTagore,ascalableGPU-acceleratedli-
proposedwavefrontparallelismstrategytransformstheincremen- braryforefficientgraphindexing,specializinginrefinement-based
taldistancecalculationsintobatchedGPU-friendlytasks,enabling methods.ByharnessingGPUparallelism,Tagoreoptimizesthein-
up to two orders of magnitude speedups.Moreover, we also im- dexingpipelinewiththreeinnovations.Firstly,weproposeatwo-
plement a GPU-based serial computing paradigm in Figure 8(a), phase algorithm, GNN-Descent, to achieve efficient k-NN graph
whichexhibitsa1.9×performancegaponaveragecomparedwith initialization,acceleratingconvergencethroughadaptivesampling
thewavefront parallelismstrategyinFigure8(b).Notably,inTa- criteria.Alock-freeneighborlistupdatealgorithmisdesignedfor
ble 5, the speedup ratio achieved by Tagore is more significant GNN-DescenttounleashtheparallelpotentialofGPUs.Secondly,
ondatasetswithhigherdimensions.Thisisattributedtothepow- wepresentaunifiedpipelineCFStoacceleratethedistinctrefinement-
erfulcomputingcapabilitiesofGPUsthatsignificantlyaccelerate basedstrategiesandintegratetwoGPU-tailoredkernelsfordiverse
distancecalculations,makingthemmoresuitableforconstructing pruning strategies. Thirdly, we proposea hybrid GPU-CPU-disk
indexesforhigh-dimensionaldatasetscomparedtoCPUs. asynchronousframeworkaugmentedbyacluster-awarecaching

SIGMOD’26,May31–June05,2026,Bengaluru,India ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao
mechanismtoefficientlyconstructbillion-scaleindexes,minimiz- [19] JianyangGaoandChengLong.2023. High-dimensionalapproximatenearest
ingtheI/Obottlenecks.Experimentalresultsconsistentlydemon- neighborsearch:withreliableandefficientdistancecomparisonoperations.Pro-
ceedingsoftheACMonManagementofData1,2(2023),1–27.
stratethesuperiorityofTagore.
[20] JianyangGaoandChengLong.2024.RaBitQ:quantizinghigh-dimensionalvec-
Forfuturework,thereremaintwocriticalchallenges.First,dur- torswithatheoreticalerrorboundforapproximatenearestneighborsearch.
ing k-NN graph initialization, late-stage iterations incur signifi- SIGMOD2,3(2024),1–27.
[21] QianwenGou,YunweiDong,YuJiaoWu,andQiaoKe.2024.Semanticsimilarity-
cant overhead from redundant distance calculations. Most sam- basedprogramretrieval:amulti-relationalgraphperspective. FCS18,3(2024),
plednodesinlaterphasesliefaroutsidethecurrentnode’sneigh- 183209.
[22] YutongGou,JianyangGao,YuexuanXu,andChengLong.2025.SymphonyQG:
borhood,renderingbrute-forcedistancecomparisonswasteful.A
TowardsSymphoniousIntegrationofQuantizationandGraphforApproximate
probabilisticfilteringmechanismthatskipslow-likelihoodcandi- NearestNeighborSearch.SIGMOD3,1(2025),1–26.
dates could replace brute-force distance computations, reducing [23] FabianGroh,LukasRuppert,PatrickWieschollek,andHendrikPALensch.2022.
Ggnn:Graph-basedgpunearestneighborsearch.IEEETransactionsonBigData
GPUworkload.Second,asindexconstructionhasbeenaccelerated
9,1(2022),267–279.
byTagore,diskI/O(dataloading,merging)becomesthedominant [24] YuchenHuang,XiaopengFan,SongYan,andChuliangWeng.2024. Neos:A
bottleneck.IntegratingNVMeSSDsandCXLmemorypoolscould NVMe-GPUsDirectVectorServiceBufferinUserSpace.InICDE.3767–3781.
[25] JunhyeokJang,HanjinChoi,HanyeoreumBae,SeungjunLee,MiryeongKwon,
mitigatethisbyenablingdirectdatastreamingbetweenGPUsand and Myoungsoo Jung. 2023. CXL-ANNS:Software-Hardware collaborative
high-bandwidthstorage/memorytiers. memorydisaggregationandcomputationforBillion-Scaleapproximatenearest
neighborsearch.InATC.585–600.
[26] JunhyeokJang,HanjinChoi,HanyeoreumBae,SeungjunLee,MiryeongKwon,
Acknowledgments andMyoungsooJung.2024.Bridgingsoftware-hardwareforcxlmemorydisag-
gregationinbillion-scalenearestneighborsearch.TOS20,2(2024),1–30.
Thisworkwassupportedinpart bytheNSFC under GrantsNo. [27] Yahoo Japan. 2018. Neighborhood Graph and Tree for Indexing High-
(62025206,U23A20296),ZhejiangProvince’s“Lingyan”R&DProject dimensionalData. https://github.com/yahoojapan/NGT.
[28] Suhas JayaramSubramanya,Fnu Devvrit, Harsha VardhanSimhadri, Ravis-
underGrantNo.2024C01259,CCF-Aliyun2024004,andYongjiang
hankarKrishnawamy,andRohanKadekodi.2019.Diskann:Fastaccuratebillion-
TalentIntroductionProgramme(2022A-237-G).YunjunGaoisthe pointnearestneighborsearchonasinglenode.NeurIPS32(2019).
correspondingauthorofthework. [29] WenqiJiang,ShigangLi,YuZhu,JohannesdeFineLicht,ZhenhaoHe,Runbin
Shi,CedricRenggli,ShuaiZhang,TheodorosRekatsinas,TorstenHoefler,etal.
2023.Co-designhardwareandalgorithmforvectorsearch.InProceedingsofthe
References InternationalConferenceforHighPerformanceComputing,Networking,Storage
andAnalysis.1–15.
[1] 2009.COLOR. http://cophir.isti.cnr.it. [30] WenqiJiang,MarcoZeller,RogerWaleffe,TorstenHoefler,andGustavoAlonso.
[2] 2010.SIFTandGIST. http://corpus-texmex.irisa.fr. 2024. Chameleon:aheterogeneousanddisaggregatedacceleratorsystemfor
[3] 2024.ANNBenchmark. https://ann-benchmarks.com/index.html. retrieval-augmentedlanguagemodels.PVLDB18,1(2024),42–52.
[4] FabienAndré,Anne-MarieKermarrec,andNicolasLeScouarnec.2016. Cache [31] JeffJohnson,MatthijsDouze,andHervéJégou.2019. Billion-scalesimilarity
localityisnotenough:High-performancenearestneighborsearchwithproduct searchwithGPUs.IEEETransactionsonBigData7,3(2019),535–547.
quantizationfastscan.InPVLDB,Vol.9.12. [32] SaimKhan,SomeshSingh,HarshaVardhanSimhadri,JyothiVedurada,etal.
[5] YihaoAng,YifanBao,QiangHuang,AnthonyKHTung,andZhiyongHuang. 2024.BANG:Billion-ScaleApproximateNearestNeighborSearchusingaSingle
2024.Tsgassist:Aninteractiveassistantharnessingllmsandragfortimeseries GPU.arXiv(2024).
generationrecommendationsandbenchmarking. PVLDB17,12(2024),4309– [33] KonstantinosLampropoulos,FatemehZardbani,NikosMamoulis,andPanagio-
4312. tisKarras.2023. Adaptiveindexinginhigh-dimensionalmetricspaces.PVLDB
[6] IliasAzizi,KarimaEchihabi,andThemisPalpanas.2023. Elpis:Graph-based 16,10(2023),2525–2537.
similaritysearchforscalabledatascience.PVLDB16,6(2023),1548–1559. [34] ConglongLi,MinjiaZhang,DavidGAndersen,andYuxiongHe.2020.Improv-
[7] ArtemBabenkoandVictorLempitsky.2016. Efficientindexingofbillion-scale ingapproximatenearestneighborsearchthroughlearnedadaptiveearlytermi-
datasetsofdeepdescriptors.InCVPR.2055–2063. nation.InProceedingsofthe2020ACMSIGMODInternationalConferenceonMan-
[8] JiashenCao,RathijitSen,MatteoInterlandi,JoyArulraj,andHyesoonKim.2023. agementofData.2539–2554.
GPUDatabaseSystemsCharacterizationandOptimization.PVLDB17,3(2023), [35] JieLi,HaifengLiu,ChuanghuaGui,JianyuChen,ZhenyuanNi,NingWang,and
441–454. YuanChen.2018. Thedesignandimplementationofarealtimevisualsearch
[9] JieChen,Haw-renFang,andYousefSaad.2009.FastApproximatekNNGraph systemonJDE-commerceplatform.InProceedingsofthe19thInternationalMid-
ConstructionforHighDimensionalDataviaRecursiveLanczosBisection.Jour- dlewareConferenceIndustry.9–16.
nalofMachineLearningResearch10,9(2009). [36] WenLi,YingZhang,YifangSun,WeiWang,MingjieLi,WenjieZhang,and
[10] PatrickChen,Wei-ChengChang,Jyun-YuJiang,Hsiang-FuYu,InderjitDhillon, XueminLin.2019. Approximatenearestneighborsearchonhighdimensional
andCho-JuiHsieh.2023. Finger:Fastinferenceforgraph-basedapproximate data—experiments,analyses,andimprovement.TKDE32,8(2019),1475–1488.
nearestneighborsearch.InWWW.3225–3235. [37] ZhiqiLin,ChengLi,YoushanMiao,YunxinLiu,andYinlongXu.2020.Pagraph:
[11] QiChen,HaidongWang,MingqinLi,GangRen,ScarlettLi,JefferyZhu,JasonLi, Scalinggnntrainingonlargegraphsviacomputation-awarecaching.InSoCC.
ChuanjieLiu,LintaoZhang,andJingdongWang.2018.SPTAG:Alibraryforfast 401–415.
approximatenearestneighborsearch. https://github.com/Microsoft/SPTAG [38] TianfengLiu,YangruiChen,DanLi,ChuanWu,YiboZhu,JunHe,Yanghua
[12] QiChen,BingZhao,HaidongWang,MingqinLi,ChuanjieLiu,ZengzhongLi, Peng,HongzhengChen,HongzhiChen,andChuanxiongGuo.2023.BGL:GPU-
MaoYang,andJingdongWang.2021. Spann:Highly-efficientbillion-scaleap- EfficientGNNtrainingbyoptimizinggraphdataI/Oandpreprocessing.InNSDI.
proximatenearestneighborhoodsearch.NeurIPS34(2021),5199–5212. 103–118.
[13] WeiDong.2011.KGraph:ALibraryforApproximateNearestNeighborSearch. [39] ZihanLiu,WentaoNi,JingwenLeng,YuFeng,CongGuo,QuanChen,ChaoLi,
https://github.com/aaalgo/kgraph. MinyiGuo,andYuhaoZhu.2024.JUNO:Optimizinghigh-dimensionalapprox-
[14] WeiDong,CharikarMoses,andKaiLi.2011.Efficientk-nearestneighborgraph imatenearestneighboursearchwithsparsity-awarealgorithmandray-tracing
constructionforgenericsimilaritymeasures.InWWW.577–586. coremapping.InASPLOS.549–565.
[15] KarimaEchihabi,PanagiotaFatourou,KostasZoumpatianos,ThemisPalpanas, [40] KejingLu,MineichiKudo,ChuanXiao,andYoshiharuIshikawa.2021. HVS:
andHoudaBenbrahim.2022. Herculesagainstdataseriessimilaritysearch. hierarchicalgraphstructurebasedonvoronoidiagramsforsolvingapproximate
PVLDB15,10(2022),2005–2018. nearestneighborsearch.ProceedingsoftheVLDBEndowment15,2(2021),246–
[16] CongFuandDengCai.2016. Efanna:Anextremelyfastapproximatenearest 258.
neighborsearchalgorithmbasedonknngraph.arXiv(2016). [41] KejingLu,HongyaWang,WeiWang,andMineichiKudo.2020. VHP:approxi-
[17] CongFu,ChangxuWang,andDengCai.2021. Highdimensionalsimilarity matenearestneighborsearchviavirtualhyperspherepartitioning.PVLDB13,9
searchwithsatellitesystemgraph:Efficiency,scalability,andunindexedquery (2020),1443–1455.
compatibility.TPAMI44,8(2021),4139–4150. [42] YuryMalkov,AlexanderPonomarenko,AndreyLogvinov,andVladimirKrylov.
[18] CongFu,ChaoXiang,ChangxuWang,andDengCai.2019. Fastapproximate 2014.Approximatenearestneighboralgorithmbasedonnavigablesmallworld
nearestneighborsearchwiththenavigatingspreading-outgraph.PVLDB12,5 graphs.InformationSystems45(2014),61–68.
(2019),461–474.

ScalableGraphIndexingusingGPUsforApproximateNearestNeighborSearch SIGMOD’26,May31–June05,2026,Bengaluru,India
[43] YuAMalkovandDmitryAYashunin.2018. Efficientandrobustapproximate arXiv:2410.01231(2024).
nearestneighborsearchusinghierarchicalnavigablesmallworldgraphs.TPAMI [71] RunjieYu,WeizhouHuang,ShuhanBai,JianZhou,andFeiWu.2025.AquaPipe:
42,4(2018),824–836. AQuality-AwarePipelineforKnowledgeRetrievalandLargeLanguageModels.
[44] XupengMiao,YiningShi,HailinZhang,XinZhang,XiaonanNie,ZhiYang,and SIGMOD3,1(2025),1–26.
BinCui.2022. HET-GMP:Agraph-basedsystemapproachtoscalinglargeem- [72] YuanhangYu,DongWen,YingZhang,LuQin,WenjieZhang,andXueminLin.
beddingmodeltraining.InSIGMOD.470–480. 2022. GPU-acceleratedproximitygraphapproximatenearestNeighborsearch
[45] DavidNisterandHenrikStewenius.2006. Scalablerecognitionwithavocabu- andconstruction.InICDE.552–564.
larytree.InCVPR,Vol.2.2161–2168. [73] ShulinZeng,ZhenhuaZhu,JunLiu,HaoyuZhang,GuohaoDai,ZixuanZhou,
[46] Nvidia. 2024. cuVS: Vector Search and Clustering on the GPU. ShuangchenLi,XuefeiNing,YuanXie,HuazhongYang,etal.2023. DF-GAS:
https://github.com/rapidsai/cuvs. adistributedFPGA-as-a-servicearchitecturetowardsbillion-scalegraph-based
[47] NaokiOnoandYusukeMatsui.2023.Relativenn-descent:Afastindexconstruc- approximatenearestneighborsearch.InMICRO.283–296.
tionforgraph-basedapproximatenearestneighborsearch.InMM.1659–1667. [74] YuxiangZeng,YongxinTong,andLeiChen.2023. Litehst:Atreeembedding
[48] HiroyukiOotomo,AkiraNaruse,CoreyNolet,RayWang,TamasFeher,andYong basedmethodforsimilaritysearch.SIGMOD1,1(2023),1–26.
Wang.2024.Cagra:Highlyparallelgraphconstructionandapproximatenearest [75] HuayiZhang,LeiCao,YizhouYan,SamuelMadden,andElkeARundensteiner.
neighborsearchforgpus.InICDE.4236–4247. 2020.Continuouslyadaptivesimilaritysearch.InSIGMOD.2601–2616.
[49] JohnDOwens,MikeHouston,DavidLuebke,SimonGreen,JohnEStone,and [76] ZiliZhang,FangyueLiu,GangHuang,XuanzheLiu,andXinJin.2024.FastVec-
JamesCPhillips.2008.GPUcomputing.Proc.IEEE96,5(2008),879–899. torQueryProcessingforLargeDatasetsBeyondGPUMemorywithReordered
[50] JamesJiePan,JianguoWang,andGuoliangLi.2024.Surveyofvectordatabase Pipelining.InNSDI.23–40.
managementsystems.VLDBJ33,5(2024),1591–1615. [77] WeijieZhao,ShulongTan,andPingLi.2020.Song:Approximatenearestneigh-
[51] PanosParchas,YonatanNaamad,PeterVanBouwel,ChristosFaloutsos,and borsearchongpu.InICDE.1033–1044.
MichalisPetropoulos.2020.Fastandeffectivedistribution-keyrecommendation [78] XiZhao,YaoTian,KaiHuang,BolongZheng,andXiaofangZhou.2023.Towards
foramazonredshift.PVLDB13,12(2020),2411–2423. efficientindexconstructionandapproximatenearestneighborsearchinhigh-
[52] YunPeng,ByronChoi,TszNamChan,JianyeYang,andJianliangXu.2023.Effi- dimensionalspaces.PVLDB16,8(2023),1979–1991.
cientapproximatenearestneighborsearchinmulti-dimensionaldatabases.SIG- [79] DaZheng,XiangSong,ChengruYang,DominiqueLaSalle,andGeorgeKarypis.
MOD1,1(2023),1–27. 2022. Distributedhybridcpuandgputrainingforgraphneuralnetworkson
[53] JieRen,MinjiaZhang,andDongLi.2020.HM-ANN:Efficientbillion-pointnear- billion-scaleheterogeneousgraphs.InSIGKDD.4582–4591.
estneighborsearchonheterogeneousmemory.NeurIPS33(2020),10672–10684. [80] MaohuaZhu,TaoZhang,ZhenyuGu,andYuanXie.2019. Sparsetensorcore:
[54] LarissaCapobiancoShimomuraandDanielSKaster.2019.Hgraph:aconnected- Algorithmandhardwareco-designforvector-wisesparseneuralnetworkson
partitionapproachtoproximitygraphsforsimilaritysearch.InDEXA.106–121. moderngpus.InMICRO.359–371.
[55] AditiSingh,SuhasJayaramSubramanya,RavishankarKrishnaswamy,andHar- [81] YifanZhu,RuiyaoMa,BaihuaZheng,XiangyuKe,LuChen,andYunjunGao.
shaVardhanSimhadri.2021.Freshdiskann:Afastandaccurategraph-basedann 2024.GTS:GPU-basedtreeindexforfastsimilaritysearch.SIGMOD2,3(2024),
indexforstreamingsimilaritysearch.arXiv(2021). 1–27.
[56] YongyeSu,YinqiSun,MinjiaZhang,andJianguoWang.2024.Vexless:aserver-
lessvectordatamanagementsystemusingcloudfunctions.SIGMOD2,3(2024),
1–26.
[57] JieSun,LiSu,ZuochengShi,WentingShen,ZekeWang,LeiWang,JieZhang,
YongLi,WenyuanYu,JingrenZhou,etal.2023.Legion:Automaticallypushing
theenvelopeofMulti-GPUsystemforBillion-ScaleGNNtraining.InATC.165–
179.
[58] JieSun,MoSun,ZhengZhang,ZuochengShi,JunXie,ZihanYang,JieZhang,
ZekeWang,andFeiWu.2025.Hyperion:Co-OptimizingSSDAccessandGPU
ComputationforCost-EfficientGNNTraining.InICDE.321–335.
[59] BingTian,HaikunLiu,ZhuohuiDuan,XiaofeiLiao,HaiJin,andYuZhang.2024.
ScalableBillion-pointApproximateNearestNeighborSearchUsingSmartSSDs.
InATC.1135–1150.
[60] BingTian,HaikunLiu,YuhangTang,ShihaiXiao,ZhuohuiDuan,XiaofeiLiao,
HaiJin,XuecangZhang,JunhuaZhu,andYuZhang.2025. TowardsHigh-
throughputandLow-latencyBillion-scaleVectorSearchviaCPU/GPUCollabo-
rativeFilteringandRe-ranking.InFAST.171–185.
[61] HuiWang,Wan-LeiZhao,XiangxiangZeng,andJianyeYang.2021. Fastk-nn
graphconstructionbygpubasednn-descent.InCIKM.1929–1938.
[62] JianguoWang,XiaomengYi,RentongGuo,HaiJin,PengXu,ShengjunLi,Xi-
angyuWang,XiangzhouGuo,ChengmingLi,XiaohaiXu,etal.2021.Milvus:A
purpose-builtvectordatamanagementsystem.InSIGMOD.2614–2627.
[63] MengzhaoWang,HaotianWu,XiangyuKe,YunjunGao,YifanZhu,andWen-
chaoZhou.2025. AcceleratingGraphIndexingforANNSonModernCPUs.
arXiv(2025).
[64] MengzhaoWang,WeizhiXu,XiaomengYi,SonglinWu,ZhangyangPeng,Xi-
angyuKe,YunjunGao,XiaoliangXu,RentongGuo,andCharlesXie.2024.Star-
ling:Ani/o-efficientdisk-residentgraphindexframeworkforhigh-dimensional
vectorsimilaritysearchondatasegment.SIGMOD2,1(2024),1–27.
[65] MengzhaoWang,XiaoliangXu,QiangYue,andYuxiangWang.2021. Acom-
prehensivesurveyandexperimentalcomparisonofgraph-basedapproximate
nearestneighborsearch.PVLDB14,11(2021),1964–1978.
[66] ChuangxianWei,BinWu,ShengWang,RenjieLou,ChaoqunZhan,FeifeiLi,
andYuanzheCai.2020.Analyticdb-v:Ahybridanalyticalenginetowardsquery
fusionforstructuredandunstructureddata.PVLDB13,12(2020),3152–3165.
[67] HaoWei,JeffreyXuYu,CanLu,andXueminLin.2016.Speedupgraphprocess-
ingbygraphordering.InSIGMOD.1813–1828.
[68] YumingXu,HengyuLiang,JinLi,ShuotaoXu,QiChen,QianxiZhang,Cheng
Li,ZiyueYang,FanYang,YuqingYang,etal.2023.Spfresh:Incrementalin-place
updateforbillion-scalevectorsearch.InSOSP.545–561.
[69] MingyuYang,WentaoLi,JiabaoJin,XiaoyaoZhong,XiangyuWang,Zhitao
Shen,WeiJia,andWeiWang.2024.EffectiveandGeneralDistanceComputation
forApproximateNearestNeighborSearch.arXiv(2024).
[70] ShuoYang,JiadongXie,YingfanLiu,JeffreyXuYu,XiyueGao,QianruWang,
YanguoPeng, andJiangtaoCui.2024. Revisitingthe indexconstructionof
proximitygraph-basedapproximatenearestneighborsearch. arXivpreprint