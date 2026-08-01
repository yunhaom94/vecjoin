# FlowANN Disentangling Graph Dependencies for GPU Vector Search

**Source**: FlowANN Disentangling Graph Dependencies for GPU Vector Search.pdf
**Format**: .pdf

---

Disentangling Graph Dependencies for Efficient
Billion-Scale GPU Vector Search
Haoru Zhao, Jingkai He, Jingyao Zeng, Mingkai Dong, and Dong Du,
Shanghai Jiao Tong University
https://www.usenix.org/conference/osdi26/presentation/zhao
This paper is included in the Proceedings of the 20th USENIX
Symposium on Operating Systems Design and Implementation.
July 13–15, 2026 • Seattle, WA, USA
ISBN 978-1-939133-55-7
Open access to the Proceedings of the 20th USENIX Symposium on
Operating Systems Design and Implementation is sponsored by

Disentangling Graph Dependencies for Efficient Billion-Scale GPU Vector Search
HaoruZhao∗,JingkaiHe∗,JingyaoZeng,MingkaiDong,DongDu
InstituteofParallelandDistributedSystems,ShanghaiJiaoTongUniversity
Abstract Step-level Dependency
parent node CPU-GPU
#1 #2 #3
transfer
Graph-basedapproximatenearestneighborsearch(ANNS) #1 step-level dep.
driveshigh-performancevectorsearchforAIsystems.Nowa- sync GPU stall #2 #3
days,GPUbecomestheemergingANNSplatformforitshigh fetch disc w ov i e n r d -e o x w pand
performance and cost efficiency. However, GPU’s limited Node-level Dependency (FlowANN)
memorycapacityhindersgraphANNSsystemsfromscaling parent node #1 #2 #3 CPU-GPUtransfer
discover a1er fetch
to billion-level,due to graph’s high memory consumption #1
#2 Expand Fetch nbrs
(239–334GB). Existing efforts mitigate this by offloading uncached node-level dep. #3 #…3 … Discover fetched nbrs
graphto CPU memory; however,this incurs severe perfor- (async fetch) (discover & expand same node) Discover cached nbrs
mancepenaltiesduetodatatransferoverheadandGPUstalls. Figure1:Step-leveldependencyvs.node-leveldependency.“nbr”
Weidentifytherootcauseofthisinefficiency:astrictstep- isshortforneighbor;“dep”isshortfordependency.
leveldependencyingraphsearch,whereeachsteprelieson
thetraversalandcomputationsofallnodesintheprevious queryvector,enablingefficientretrievalofrelevantinforma-
step.Ourkeyinsightisthatthismonolithicstep-leveldepen- tion.AmongallANNSindexes,graph-basedapproaches[8–
dencycanbedisentangledintoamoreflexible,fine-grained 18]arefavoredfortheirsuperiorsearchefficiency.
node-leveldependency.Specifically,foreachnode,itisfirst Therapidgrowthofdatascalesandtheexplosivecomputa-
accessedasaneighborviaanedge(i.e.,discovery),andlater tionaldemandsofANNShasdriventheemergingadoptionof
selectedasaparenttotraverseitsneighbors(i.e.,expansion). GPUsforANNS[19–23],leveragingtheirhighcomputational
Thesetwostagesaretypicallyseparatedbymanysteps,expos- efficiencyandcostefficiency.GPU’sparallelcomputingca-
ingasufficientdiscovery-expansionwindow.Leveragingthis pabilitiesnaturallyalignwithANNS’vectorcomputationre-
timewindow,theedgefetchingtoaccesssomeneighborscan quirements,makingasinglemid-tierGPUachieveover200×
bedeferredandoverlappedwithcomputation.Basedonthis
thethroughputofahigh-endCPUserver1(Fig.2).Thus,GPU
insight,weproposeFlowANN,agraph-basedANNSsystem ANNShasbeenwidelyadoptedbythecommunity[24,25]
thatefficientlysupportsbillion-scalesearchonasingleGPU. andindustry(Meta[26],NVIDIA[27],etc.[28–30]).
FlowANNemploysatieredgraphstructure,offloadingthe However, the limited memory capacity of GPUs poses
edgesconnectedtoneighborsthathavesufficienttimewin- significant challenges for deploying large-scale graph-
dowstotheCPU.IteffectivelypipelinesGPUcomputation based ANNS on GPUs. For instance, even after quantiza-
withedgefetchingviaoptimizedasynchronoustransferand tion[31,32],billion-scalegraph-basedANNSindexes[33–
dynamiccoordination.EvaluationsshowthatFlowANNout- 36] (datasets in Table1) stillrequire 258–350GB memory,
performsstate-of-the-artsystemsby4.08–45.7×onaverage with the graph alone consuming 239–334GB. This far ex-
(upto172.6×),withoutcompromisingsearchaccuracy. ceedsthe80–96GBmemorycapacityofmainstreamGPUs.
Alternatively,offloadinggraphtohostmemoryandfetching
dataondemandsuffersfromhighdatatransferoverheaddue
1 Introduction tothestrictdependenciesinthesearchprocess.Specifically,
graph ANNS employs a best-first search algorithm,which
Approximate nearest neighbor search (ANNS) serves as a proceedsiteratively.Ineachstep,itselectsthenodeclosest
foundationalcomponentofmodernAIsystems,andiswidely tothequeryfromthecandidatepoolastheparent,fetches
usedinretrieval-augmentedgeneration(RAG)[1,2],recom- the parent’s edges from the graphto retrieve its neighbors,
mendationsystems[3,4],imageretrieval[5],andLLMserv- computesallneighbors’distancestothequery,andaddsthem
ing[6,7].Thesesystemsembeddataintohigh-dimensional intothecandidatepoolforsubsequentsteps.Astheselection
vectorsandemployANNStoidentifynearestvectorstothe oftheparentrequiresthatallneighborsfromthepreviousstep
∗Bothauthorscontributedequallytothisworkandshouldbeconsidered 1GPU:NVIDIAH20,with15%ofcomputingcapability(TFLOPS)ofH100;
asco-firstauthors. CPU:2xIntelPlatinum8457C.Allexperimentsfollowsettingsin§7.
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1563

completethecomputationsandareinsertedintothecandidate Challenge#2:Laggingedgefetching.FlowANNhastofetch
pool,this rigid step-level dependency results in significant edgestoGPUasynchronously.However,despitemanymeth-
GPUstallstowaitforedgefetching,asFig.1shows. odstocopydatabetweenCPUandGPU(e.g.,cudaMemcpy,
However,thisconventionalviewofstep-leveldependency unifiedmemory)[37],currentGPUecosystemslacksupport
isoverlystrict,andtheassociatedwaitingmaybeunnecessary. for GPU-initiated async transfers. Existing methods either
Wedisentanglethestep-leveldependencyintoafiner-grained requirereturningcontroltoCPUtoinitiateasynccopies,or
node-leveldependency.Fromanode’sperspective,duringthe relyonGPU-initiatedsynchronouscopies.Furthermore,ex-
searchprocess,itisfirstreachedasaneighbor(i.e.,discov- isting CPU-GPU transfer methods typically rely on DMA.
ery)andthenusedtofinditsneighbors(i.e.,expansion).The ButDMA’shighinitializationoverheadseverelydegradesthe
best-firstsearchalgorithmensuresthat,ineachstep,multiple performanceofedgefetching,whosesizeisrelativelysmall.
nodesarediscoveredandonlyonenodeisexpanded.There- Challenge#3:Uncoordinated pipelining. Although the
fore,formostnodes,thereexistsatimewindow(i.e.,several discovery-expansionwindowsenabledeferreddiscovery,ex-
steps) between their discovery and expansion (Insight#1). cessivedeferralsleadthesearchtosuboptimalsearchpaths,
For instance, ~95.6% of expanded nodes have an average therebysacrificingefficiency.Thus,FlowANNhastowaitfor
window>5steps(§3). somediscoveriesiftheirdeferredstepsexceedtheirdiscovery-
Such discovery-expansion windows suggest an opportu- expansionwindows.However,estimatingthewindowischal-
nitytooffloadsomeedgestoCPUwith(almost)zeroover- lengingduetoitsdynamicevolutionthroughoutthesearch.
head: when expanding a node, its offloaded edges can be Furthermore, GPU computational resources (e.g., CUDA
asynchronouslyfetchedtodiscovertheneighbors.Aslongas cores,sharedmemory)arestaticallyallocatedfortheGPU
theseneighborshavesufficientdiscovery-expansionwindows, kernel,butdeferreddiscoveryleadstodynamicallyvarying
theirdeferreddiscoverieswillnotdisruptthenodes’expan- workloadsineachstep,resultinginresourceunder-utilization.
sionorderinsearchprocess(i.e.,preservingbest-firstsearch’s To address the challenges,we propose the following de-
searchpath).Moreover,suchdeferreddiscoveryeffectively signs. Firstly,we design the grouping-basedgraphtiering,
hidesdatatransferbyoverlappingitwithcomputations. whichpartitionsthegraphbygroupingspatiallyproximate
However,thoughthediscovery-expansionwindowpresents nodesandplacesedgesbetweennodeswithinthesamegroup
anopportunityforzero-overheadoffloading,identifyingsuit- ontheGPU.Buildingonrecenttheoreticaladvances[38],we
ableedgesforoffloadingremainschallenging,sincepredict- employamulti-levellabelpropagationschemeforgrouping,
ingthewindowisdifficult.Wefindthattheexpandednodes’ whichconsidersbothedgelengthsandnodespatialdistribu-
nearby neighbors (i.e., connected via short edges) are ex- tion.Furthermore,weintroduceacompactmatrixlayoutto
pandedsooner,leavinginsufficientwindowsfordeferreddis- store the tiered graph,which reduces memory waste from
covery.Thisisbecausethenodeanditsnearbyneighborsare paddingandenablesmoreedgestoresideinGPUmemory.
closeinspace,soonceoneisexpanded(i.e.,beingnearthe Secondly,wedesignxCopiertoenableGPU-initiatedasyn-
query),theotherisalsolikelytobeclosetothequeryand chronousdatatransfers.xCopiercoordinatesGPU-sidering
expanded soon. Therefore,generally,long edges are more queues and CPU-side data-moving threads, and provides
suitableforoffloading,whileshortedgesshouldresideonthe GPU-optimized programming primitives for GPU kernels.
GPUtoensuretimelydiscovery(Insight#2). Tofacilitateedgefetching(i.e.,smallcopies),xCopierem-
Based on these insights,we propose FlowANN,a GPU ploysMMIO-baseddatatransfer,bypassingtheoverheadof
graph ANNS system that efficiently supports billion-scale conventionalDMA-basedapproaches.xCopiermakesedge
searchonasingleGPU.AsFig.1shows,ateachstep,itdis- fetchinginFlowANNbothtrap-lessandasynchronous,en-
coverstheparent’sneighborsresidingontheGPUandthe ablingeffectiveoverlapofdatatransferandcomputation.
nodes deferred from previous steps,while asynchronously Finally,wedesignacoordinatedpipelineforefficientexe-
fetchingotherneighborsfromtheCPU.Wehavemathemat- cution.FlowANNemploystheadaptivesynchronizationto
ically proven that deferred discoveries do not compromise preventexcessivelydeferreddiscoveries,whichholistically
searchaccuracy,evenifFlowANNmight(sometimes)yielda considersglobalsearchconvergenceandlocalfluctuations.To
differentsearchpathcomparedtosynchronousedgefetching. efficientlyutilizeGPUresources,FlowANNintroducescross-
FlowANNfurtheraddressesthefollowingchallenges. stepbalancing,whichadaptivelybalancesworkloadsacross
Challenge#1:Imbalancedgraphtiering.Whileedgelength stepstoaligncomputingdemandswithhardwareresources.
providesamacroscopiccriterionforgraphtiering,selecting WeevaluateFlowANNonbillion-scaledatasets[39–41],
on-GPUedgesbasedonastaticedgelengththresholdleads and compare it with SOTA GPU ANNS systems from in-
tocriticalimbalances.Duetotheunevendistributionofdata dustryandacademia.FlowANNoutperformscluster-based
pointsinhigh-dimensionalspace,edgesindenseregionsare ANNSsystemslikecuVS[27],Faiss[24],Rummy[19],and
typicallyshort,whilenodesinsparseregionshavefewshort FusionANNS[22]by4.08–8.41×onaverage,whilemaintain-
edges.Simplyusingalengththresholdcausesquerieslocated ingthesameaccuracy.Itoutperformsgraph-basedsystems
insparseregionstosufferfromexcessiveuncachededges. likeBANG[20]andFlashANNS[42]by45.7×and14.3×
1564 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

)SPQK( tuphguorhT CPU-Cluster CPU-Graph GPU-Cluster GPU-Graph 1 expand as parent  2 discover Candidate Pool (Sorted)
28
|     |     |     |     |     |     |     |     |     | 2 discover |     | 4 query |     | step1 | 3   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ------- | --- | ----- | --- |
| 26  |     |     |     |     |     |     |     |     |            | 1   |         |     |       |     |
| 24  |     |     |     |     |     |     |     |     |            |     |         | 8   |       |     |
| 22  |     |     |     |     |     |     |     |     |            | 2   | 6       |     | step2 | 1 3 |
|     |     |     |     |     |     |     |     |     |            | 3   | 5       | 7   |       |     |
20
| 2−2 |     |     |     |     |     | ×   | ×   |     | entry point |     |     |     | step3 | 4 1 3 2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | ----- | ------- |
……
|     |     |     |                |      |      |      |     |                         | expansion path |     | expanded  |     |        |           |
| --- | --- | --- | -------------- | ---- | ---- | ---- | --- | ----------------------- | -------------- | --- | --------- | --- | ------ | --------- |
|     | 10M | 20M | 50M            | 100M | 200M | 500M | 1B  |                         |                |     |           |     | result |           |
|     |     |     | Dataset (SIFT) |      |      |      |     | discovered & unexpanded |                |     | expanding |     |        | 7 6 8 4 5 |
Figure2:ANNSperformanceacrossindexesonGPU/CPUwith Figure3:Best-firstgraphsearchprocedure.
| different | dataset | sizes. | Recall@10 |     | = 0.9. Recall@α | means | the |     |     |     |     |     |     |     |
| --------- | ------- | ------ | --------- | --- | --------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
proportionoftrueneighborsfoundwithinthetop-αresults.Weuse
KNNgraphandbest-firstsearch.Thegraphstructurefor
Faiss[24](w/HNSW[10])andcuVS[27]forCPU/GPUANNS.
ForCPUANNS,all(160)coresareused.Detailedsettingsin§7. ANNSistheK-NearestNeighbor(KNN)graph,agraphwhere
eachnode(vector)isconnectedtoitsapproximatelyKnearest
neighborsinthedataset,asdeterminedbydistancemetrics
onaverage,andachievescomparablethroughput(usingone
likeEuclideandistance.Thegraphisstoredasa2Dmatrix,
| GPU) | with | multi-GPU | graph | system | GGNN | [43] | using 8 |                          |     |     |     |                      |     |     |
| ---- | ---- | --------- | ----- | ------ | ---- | ---- | ------- | ------------------------ | --- | --- | --- | -------------------- | --- | --- |
|      |      |           |       |        |      |      |         | whereeachrowcontainstheK |     |     |     | neighborIDsforanode. |     |     |
GPUs.FlowANNconsistentlyachievesimprovementsacross
differentaccuracies,GPUs,andalgorithmconfigurations. Thegraphsearchalgorithmutilizesabest-firstsearchstrat-
egy.AsillustratedinFig.3,itmaintainsacandidatepoolthat
| FlowANN |     | is fully | open-sourced |     | at https://github. |     |     |     |     |     |     |     |     |     |
| ------- | --- | -------- | ------------ | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
com/SJTU-IPADS/GPU-Graph-ANN. contains a fixed number of the closest nodes found so far,
|     |     |     |     |     |     |     |     | sortedbytheirdistancetothequery. |     |     |     |     | Thealgorithmbegins |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | --- | --- | ------------------ | --- |
fromanentrypoint(e.g.,node3)andproceedsiteratively.At
2 GPUGraphANNS:FastyetMemory-bound
eachiteration,itselectsthenearestunexpandednodefromthe
candidatepoolastheparentandtraversesitsedgestoobtain
| 2.1 | GPUGraphANNSPrimer |     |     |     |     |     |     | itsneighbors(❶).3 |     |     |     |     |     |     |
| --- | ------------------ | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- |
Itthencomputesthedistancesbetween
theseneighborsandthequery,andinsertsthemintothepool
VectorsearchunderpinsmodernAIsystems,suchasRAG[1,
(❷).Thisprocessrepeatsuntilallnodesinthepoolhavebeen
2],recommendationsystems[3,4,30],imageretrieval[5],
expanded,andthealgorithmreturnsthetop-knearestvectors
andLLMinference[6].Thesesystemsembeddata(e.g.,text,
inthepoolasthefinalresult.Duringthesearch,eachnode
images)intovectors,andusevectorsearchtoretrievedata
undergoestwomainstages:❶itisreachedasaneighborvia
| relevanttotheembeddedqueryvector. |     |     |     |     | Thecoreoperation |     |     |     |     |     |     |     |     |     |
| --------------------------------- | --- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
anedgeandisinsertedintothecandidatepoolafterdistance
ofvectorsearchisk-nearestneighborsearch,whichtriesto
computation(termeddiscovery);❷itisselectedastheparent
findtheknearestvectors(top-k)toaquery.Asexactnearest
tofurtherdiscoveritsneighbors(termedexpansion).
| neighbor | search | via | brute-force | is  | infeasible | at large | data |     |     |     |     |     |     |     |
| -------- | ------ | --- | ----------- | --- | ---------- | -------- | ---- | --- | --- | --- | --- | --- | --- | --- |
scales(e.g.,billion-level[33–35,41]),modernvectorsearch GPU-based ANNS. Given the growing demand for large-
adoptsapproximatenearestneighborsearch(ANNS),which scalevectorprocessing(e.g.,billionsofvectors),GPU-based
|     |     |     |     |     |     |     |     | ANNS | is increasingly |     | favored | for its | parallel | capabilities |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --------------- | --- | ------- | ------- | -------- | ------------ |
leveragespre-builtindexesforefficientapproximateretrieval.
|                  |     |                  |                                |                 |     |         |     | and    | cost-efficiency |     | [22]. Currently, |      | GPU-based | ANNS is        |
| ---------------- | --- | ---------------- | ------------------------------ | --------------- | --- | ------- | --- | ------ | --------------- | --- | ---------------- | ---- | --------- | -------------- |
| Graph-basedANNS. |     |                  | MainstreamANNSindexesgenerally |                 |     |         |     |        |                 |     |                  |      |           |                |
|                  |     |                  |                                |                 |     |         |     | widely | adopted         | by  | industry leaders | such | as        | Meta [26, 50], |
| fallinto         | two | broadcategories: |                                | partition-based |     | [44–49] | and |        |                 |     |                  |      |           |                |
graph-based[8–12].Partition-basedindexesdividethedataset NVIDIA[27,51],etc.[28–30].Withbothdataandindexes
|     |     |     |     |     |     |     |     | (e.g.,graph)placedon |     |     | theGPU,SOTAsystemsaccelerate |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | ---------------------------- | --- | --- | --- |
intomultiplepartitions,suchasclustersofspatiallyproximate
|     |     |     |     |     |     |     |     | keyANNS |     | operations | (e.g.,distance |     | computation,sorting) |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | ---------- | -------------- | --- | -------------------- | --- |
pointsordiscretebucketsmappedviahashing.2Subsequently,
|            |     |         |           |         |        |                |     | throughparallelexecution |        |       | [27,            | 51, 52],significantlyboost- |       |             |
| ---------- | --- | ------- | --------- | ------- | ------ | -------------- | --- | ------------------------ | ------ | ----- | --------------- | --------------------------- | ----- | ----------- |
| the search |     | process | scans the | vectors | within | the partitions |     |                          |        |       |                 |                             |       |             |
|            |     |         |           |         |        |                |     | ing                      | search | speed | and throughput. | As                          | Fig.2 | shows, GPU- |
thatareclosetothequeryviabruteforce.Incontrast,graph-
basedANNSachievesa9.0–222.0×speedupoverCPU-based
| based | methods | construct | a   | proximity | graph | to capture | the |     |     |     |     |     |     |     |
| ----- | ------- | --------- | --- | --------- | ----- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
onesacrossvariousdatasetsizes.Notably,graph-basedGPU
| relationships |     | between | vectors,and |     | the search | proceeds | by  |     |     |     |     |     |     |     |
| ------------- | --- | ------- | ----------- | --- | ---------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
ANNSoutperformscluster-basedonesby5.2–15.1×,high-
traversingthegraph.
lightingthesuperiorityofgraph-basedANNSonGPU.
| Graph-based |     | ANNS | systems | offer | superior | search | effi- |     |     |     |     |     |     |     |
| ----------- | --- | ---- | ------- | ----- | -------- | ------ | ----- | --- | --- | --- | --- | --- | --- | --- |
ciencyovercluster-basedones.AsshowninFig.2,theyde-
liver1.6–10.5×higherperformanceandsuperiorscalability.
|     |     |     |     |     |     |     |     | 2.2 | MemoryStraininGPUGraphANNS |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- |
Thisadvantagestemsfromthegraphstructure,whichallows
thesearchtonavigatedirectlytowardnearestneighborsby
|     |     |     |     |     |     |     |     | Although | exhibiting |     | computational | efficiency, |     | the substan- |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | --- | ------------- | ----------- | --- | ------------ |
graphtraversal,significantlyreducingdistancecomputations
tialmemoryfootprintofthegraphlimitstheapplicabilityof
comparedtothebrute-forcescansofcluster-basedmethods.
GPUgraphANNSatbillion-scale.Forexample,evenafter
2Whilepartition-basedindexesencompassvariousapproaches(e.g.,hash-
basedandcluster-basedones),oursubsequentdiscussionmainlyfocuses 3Acommonvariantofbest-firstsearchselectsmultipleparentsineachstep
onthecluster-basedones. (i.e.,beamsearch).Wealsoconsideritinourevaluations(§7.4.2).
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1565

|     |     | SIFT1B |     |     | DEEP1B |     |               |     |      |     |                  |     |           |     |
| --- | --- | ------ | --- | --- | ------ | --- | ------------- | --- | ---- | --- | ---------------- | --- | --------- | --- |
|     |     |        |     |     |        |     | (a) Approach  |     | B t1 | G M | Candidate Pool   |     | expanded  |     |
|     |     |        |     |     |        |     |               |     | E    |     | J                |     |           |     |
eziS wodniW 300 Appr. Converge Appr. Converge A t2 I F H G E expanding
|     |      | P75 |            |     |     |     |     |             | C        | F   |                         |     |            |     |
| --- | ---- | --- | ---------- | --- | --- | --- | --- | ----------- | -------- | --- | ----------------------- | --- | ---------- | --- |
|     |      |     |            |     |     |     |     |             | D        | I   | L                       |     |            |     |
| 200 | Mean |     |            |     |     |     |     | entry point |          |     | Discovered at  t 1  ,   |     | discovered |     |
|     |      |     | window = 5 |     |     |     |     |             | current  | H   | K                       |     |            |     |
|     |      |     |            |     |     |     |     |             |          | N   | expanded att2           |     | query      |     |
100
|     |          |     |       |                |     |     | (b) Converge  |             | B t1      | G   | Candidate Pool   |              | expansion           |             |
| --- | -------- | --- | ----- | -------------- | --- | --- | ------------- | ----------- | --------- | --- | ---------------- | ------------ | ------------------- | ----------- |
| 0   |          | P25 |       |                |     |     |               |             |           | M   |                  |              |                     |             |
|     |          |     |       |                |     |     |               |             | E t2      |     | J                |              | p                   | a t h       |
| 0   | 100      | 200 | 300 0 | 100            | 200 | 300 |               | A           | C         |     | I                | F H          | L K                 |             |
|     |          |     |       |                |     |     |               |             | D         | F   | L                |              |                     | fu t u re   |
|     | SPACEV1B |     |       | SIFT10M (HNSW) |     |     |               |             |           | I   |                  |              | e                   | x p ansion  |
|     |          |     | 100   |                |     |     |               | entry point | current H |     | D                | is c o v e r | ed  a t    t 2  ,   |             |
eziS wodniW 300 Appr. Converge Appr. Converge N K e x p a n d e d  a t t 4 p a th
P75
| 200 |      |     |     |     |     |     | Figure5: |     | Twophasesin | thegraphsearchprocess.Theupper |     |     |     |     |
| --- | ---- | --- | --- | --- | --- | --- | -------- | --- | ----------- | ------------------------------ | --- | --- | --- | --- |
|     | Mean |     | 50  |     |     |     |          |     |             |                                |     |     |     |     |
win.=5 figureshowsapproachphase,andthelowershowsconvergephase.
100
P25
| 0   |     |         | 0   |      |     |       | tiondependsonalltheneighborsoftheparentbeingfetched |     |     |     |     |     |     |     |
| --- | --- | ------- | --- | ---- | --- | ----- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| 0   | 100 | 200 300 | 400 | 0 20 |     | 40 60 |                                                     |     |     |     |     |     |     |     |
Search Step Search Step anddiscoveredinthepreviousstep.Consequently,itisnearly
Figure4:Discovery-expansionwindowsoversteps. Foranode impossible to hide transfer latency by overlapping it with
beingexpanded,itswindowsize=currentstep−thestepwhenit computation(<10%overlapped).Additionally,thisapproach
wasdiscovered−1.WealsovalidateotherKNNgraphvariant(i.e., leadstosevereGPUmemoryunder-utilization(~50GBidle
HNSW)exhibitssimilarresults.TheHNSWindexisfromFAISS[24]. onan80GBHBMGPUforthequantizedSIFT1Bdataset),
asittreatsGPUmemorymerelyasatransientstagingarea.
quantization4,whichreducesthevectormemoryfootprintto
12.5%oftheoriginal,graphANNSonSIFT1Bdataset[39]
3 DisentanglingDependencyinGraphSearch
demands~258GBmemory.Thisfarexceedsthe80-96GB
capacityofmainstreamGPUs,makingitundeployableona
|     |     |     |     |     |     |     | Given | the | conventional | strict | step-level |     | dependency, | CPU- |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | ------------ | ------ | ---------- | --- | ----------- | ---- |
GPU(Fig.2).Notably,thegraphaloneconsumes~93%ofthe
GPUtieringforgraphANNSseemsinfeasibleduetohigh
totalmemory,constitutingthekeybottleneck.Suchmemory
datatransferoverhead.However,wefindthatthisstep-level
consumptionisunavoidabletopreserveadequategraphcon-
|     |     |     |     |     |     |     | dependency |     | is overly | rigid | and | can be | disentangled | into |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --------- | ----- | --- | ------ | ------------ | ---- |
nectivityandensuresearchquality.Thus,thecorechallenge
node-leveldependency.Specifically,ateachstepofagiven
inscalingGPUgraphANNStobillion-scaleliesinbreaking
best-firstsearchpath,onlythenodetobeexpandedneedsto
thememorybottleneckwhilemaintaininghighperformance.
havebeendiscovered.Basedonthisfine-graineddependency,
weanalyzethegraphsearchtracesfortensofthousandsof
2.3 ExistingEffortsandPossibleSolutions queriesonthreebillion-scaledatasets(§7).5 Fromtheanal-
|     |     |     |     |     |     |     | ysis,we | identify | opportunities |     | to  | defercertain | discoveries, |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | ------------- | --- | --- | ------------ | ------------ | --- |
MultipleGPUs.AlthoughemployingmultipleGPUs[23,43]
therebyoverlappingdatatransferwithcomputationwithout
(e.g.,throughgraphsharding)presentsatheoreticalsolution, sacrificingaccuracy.
itfacesnon-trivialchallenges.Firstly,efficientgraphpartition-
|     |     |     |     |     |     |     | Observation#1: |     | Discovery-Expansion |     |     |     | window. | We dis- |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------------------- | --- | --- | --- | ------- | ------- |
ingforANNSremainschallenging,asthesearchalgorithm’s
coverthatduringthesearchprocess,thereexistsatimewin-
| step-by-step | discovery-oriented |     | nature | makes | the | traversal |     |     |     |     |     |     |     |     |
| ------------ | ------------------ | --- | ------ | ----- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
dowbetweenanode’sdiscoveryandexpansion(discovery-
pathforagivenqueryinherentlyunpredictable.Secondly,it
expansionwindow).AsFig.4shows,for95.6%ofthesearch
| introduces | frequentinter-GPU |     | communication,whichcon- |     |     |     |           |     |                             |     |     |     |        |           |
| ---------- | ----------------- | --- | ----------------------- | --- | --- | --- | --------- | --- | --------------------------- | --- | --- | --- | ------ | --------- |
|            |                   |     |                         |     |     |     | steps,the |     | average discovery-expansion |     |     |     | window | exceeds 5 |
sumescomputationalresources,increasessearchlatency(sev-
steps(6–14µsperstep,dependingonthebatchsize).More-
eralms),anddegradesthroughput,asdemonstratedin§7.1.
|     |     |     |     |     |     |     | over, | the | window size | consistently |     | grows | throughout | the |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | ----------- | ------------ | --- | ----- | ---------- | --- |
Unifiedmemory(UM).UMextendsmemorycapacitybycre-
searchprocess.
atingaunifiedaddressspaceacrossCPUandGPU.However,
Insight#1:Deferrablediscovery.Thediscovery-expansion
itisill-suitedforgraphtraversal,whichexhibitsvirtuallyno
|     |     |     |     |     |     |     | window | presents | an  | opportunity |     | to defer | the discovery | of  |
| --- | --- | --- | --- | --- | --- | --- | ------ | -------- | --- | ----------- | --- | -------- | ------------- | --- |
locality.Consequently,thetraversalfrequentlytriggerspage
certainnodeswithoutcompromisingaccuracy.Specifically,
faultsandmigrations(62µs),whichareexceedinglycostly.
sincethiswindowcantypicallyoverlaptheedges’host-to-
CPU-GPUtiering.Anotherapproachistostorethegraph
|     |     |     |     |     |     |     | GPU | transfer | latency | (~8µs,Fig.17b),we |     |     | can offload | the |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------- | ----------------- | --- | --- | ----------- | --- |
primarilyinCPUmemoryandtransferedgesofparentnodes edges connecting to neighbors with sufficient windows to
| toGPUondemand(e.g.,BANG[20]). |            |     |            | However,thestrict |          |        |     |         |     |       |               |     |          |           |
| ----------------------------- | ---------- | --- | ---------- | ----------------- | -------- | ------ | --- | ------- | --- | ----- | ------------- | --- | -------- | --------- |
|                               |            |     |            |                   |          |        | CPU | memory, | and | defer | the discovery |     | of these | neighbors |
| step-level                    | dependency | in  | best-first | search            | severely | limits |     |         |     |       |               |     |          |           |
untiltheedgesarefetchedtoGPU.Whenfetchingtheedges,
computation-transferoverlap:eachstep’snewparentselec- GPUcancontinueexecutingsubsequentsteps’computations
withoutblocking.
4Toenhancecomputationalefficiency,SOTAsystemssearchwithlower-
Observation#2:Shortedgesindicatenon-deferrabledis-
dimensional,quantizedvectors,andreturnacandidatesetwithmorethank
items,whichisre-rankedusingthefull-dimensionalvectorstoproducethe
5WedeployCAGRA[51](NVIDIA)usingUMtocapturenode-leveltraces.
finaltop-kresults.ProductQuantization(PQ)[32]isthemostwidelyused.
1566    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

15
10
5
0
0 5 101520253035404550556065707580859095 100 105
Edge Length (K)
)%(
oitaR
evitaleR
insufficient window 1 p S a e r le e c n t t 2 u F n e c t a c c h hed 3 d C i o st m a p n u ce te s ca 4 nd U id p a d t a e t e pool
s c u m bm ds it neig r h e b le o a r s s e of c a ch ch il e d d ve d c a to ta r
nbrs GPU fetched results
p C o a o n l d (s i o d r a t t e e d) nbrs Quan)fied
fetch GPU Tiered graph vec. GPU
cmds fetch CPU
Figure 6: Proportion ofedges withinsufficientwindows (≤5 Update CPU nbrs
Re-rank
steps)foreachedgelengthbucket(SIFT1B).E.g.,intheshortest- at 4 xCopier CPU Tiered graph Raw vec. 5
edgebucket(0–5),17.7%oftheedgesconnecttoneighbornodes
withinsufficientwindows.Otherdatasetsexhibitsimilarresults. Figure7:OverviewofFlowANNworkflow. Currently,thetiered
graphisconstructedandplacedoffline.“nbr”standsforneighbor.
coveries.Whilethediscovery-expansionwindowpresentsa
nodeIatt cannotfindaclosernodethanI).Consequently,the
generalopportunityfordeferrablediscovery,notallnodesare 3
nodeselectedforexpansion(i.e.,nearestunexpandednode)
equally suitable fordeferral. As Fig.5(a) shows,when ex-
istypicallytheonethatwasdiscoveredseveralstepsearlier
pandingnodeF att ,itsneighborIislesssuitablefordeferral
2 (e.g.,nodeHatt ),resultinginthepresenceofawindow.
thanG,asI willbeexpandedsoon.Tosystematicallyiden- 4
Meanwhile,sincethenodesexpandedduringthisphaseare
tify non-deferrable discoveries,we analyze the correlation
alreadyclosetothequery,theirnearbyneighbors(connected
betweenedgelengthandwindowsize.Specifically,foreach
byshortedges)arealsolikelytobeclosetothequeryandthus
expandednode,wecollectthelengthoftheedgeusedtodis-
expandedsooner,resultinginsmallerwindows.Thispattern
coverit,andanalyzeedgeswhosecorrespondingdiscoveries
isreflectedintheoverallsearchbehavior(Fig.6)duetothe
haveinsufficientwindows(conservatively≤5steps).
dominanceoftheconvergephaseinthesearchprocess.
Resultsrevealthatdiscoveriesthroughshortedgesareless
Correctnessandaccuracy.Somemayconcernthatprecisely
likelytobedeferrable.AsFig.6shows,shorteredgesaremore
predictingthediscovery-expansionwindowsisdifficult,po-
frequentlyassociatedwithdiscoveriesthathaveinsufficient
tentiallyleadingtoover-deferralofsomenodes’expansion,
windows.Theproportionofedgeswithinsufficientwindows
andthuscompromisingaccuracy.Wemathematicallyprove
intheshortest-edgebucket(17.7%)ismuchhigherthanthatin
that,giventhegreedynatureofgraphsearch,evenintheworst
thelongest-edgebucket(0.63%).Wealsofindthatshortedges
case(i.e.,alldiscoveriesareover-deferred),FlowANNcan
havehigheraccessfrequency.Nevertheless,mostdiscoveries
achieveidenticalaccuracywithinaboundedanddeterministic
(~90.6%) have sufficient windows (>5steps) for deferral,
numberofsteps,whichisprovedinAppendixA.Wefurther
demonstratingbroadapplicabilityofdeferrablediscovery.
designthesynchronizationmechanismtoproactivelyprevent
Insight#2:Length-basedgraphtiering.Inthegraph,since
excessivedeferralofdiscoveries(§6.2).
discoveriesviashortedgesarelessdeferrableandmorefre-
quentlyaccessed,shortedgesshouldberetainedinGPUmem-
ory.ThiseffectivelyutilizestheremainingGPUmemoryafter 4 FlowANNOverview
storingthequantizedvectors.Conversely,longedgescanbe
safelyoffloadedtohostmemoryandfetchedtoGPUonde- WedesignFlowANN,agraph-basedANNSsystemthateffi-
mand,thusmaximizingmemoryefficiency. cientlyhandlesbillion-scalevectorsearchonasingleGPU.
Rootcauseandgenerality.Theseobservationsarederived Workflow. As Fig.7 shows,FlowANN tiers the graphand
from the nature ofbest-firstsearch,whichaims to findthe offloads the edges with low access frequency and large
query’stop-kclosestnodes,specificallyfromitssurrounding discovery-expansion windows to the CPU. It fuses the en-
region(e.g.,shadedareainFig.5).Thisprocessisnaturally tireGPUsearchprocess(multiplesteps)intoasingleGPU
dividedintotwophases:approachandconverge[11,53]. kernel.Eachstepcanbedividedintofourphases.❶First,it
During the approach phase,the search rapidly advances selectstheclosestunexpandednodetothequeryfromthecan-
from the entry point toward the vicinity of the query (e.g., didatepoolastheparent.❷Subsequently,itasynchronously
nodeA FinFig.5(a)).Eachdiscoverytendstofindnodes fetches the parent’s offloaded edges (i.e., uncached neigh-
closerto(cid:1)thequery,whicharethenquicklyexpanded,resulting bors)fromtheCPU-tieredgraphtotheGPUusingxCopier.
insmallwindows.AsFig.4shows,thefirstquartileofwindow ❸Meanwhile,fortheparent’scachedneighborsandthose
size(P25)remainsclosetozeroduringthefirst~22%steps. neighborsalreadyfetchedtotheGPU,FlowANNcalculates
However,uponenteringtheconvergephase,thesearchhas theirdistances to the query using theircorresponding data
reachedthenodesnearthequery(e.g.,nodeFinFig.5(b)). vectorsstoredontheGPU.Likemainstreamsystems[24,27],
During this phase, the search generally follows a query- forbettercomputationalefficiency,thevectorsstoredonthe
centric,outward-expandingtrend[53]tocollecttheactualtop- GPUarequantized.❹Finally,thecandidatepoolisupdated
knearestneighbors.Asthesearchprogresses,thelikelihood withthesediscoveredneighborsandre-sorted.❺Afterthe
ofdiscoveringaclosernodediminishes(e.g.,expansionof completionofthewholeGPUsearchphase,thenodesinthe
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1567

|                         |     |     |     |     |     | LPA  |        |     | Mul--level LPA  |     |         |     |
| ----------------------- | --- | --- | --- | --- | --- | ---- | ------ | --- | --------------- | --- | ------- | --- |
| Algorithm1FlowANNSearch |     |     |     |     |     |      | Label  |     |                 |     | Group 3 |     |
(Group ID)
|                 |                      |                      |              |                |               | 2   |     |     |     | Group 2 |     |     |
| --------------- | -------------------- | -------------------- | ------------ | -------------- | ------------- | --- | --- | --- | --- | ------- | --- | --- |
| R e q u i r e : | Q ue r y q , t ie re | d g r a ph ( G g p u | ,G c p u ) , | p o o l s i ze | L , t o p - k | 2 2 |     |     |     |         |     |     |
1 2
| 1 : I n i t ia | li ze c a nd i d a te | p o o l C w i th t h | e se l e c t e | d e n t r y po | i n t s f o rq | 3   |     |     |     |     |     |     |
| -------------- | --------------------- | -------------------- | -------------- | -------------- | -------------- | --- | --- | --- | --- | --- | --- | --- |
3 1 2
2: DeferredneighborsD←0/
Label
| whileChasunexpandednodesdo |                    |                      |       |     |     |     | 1 2 |     |                 |     |     |         |
| -------------------------- | ------------------ | -------------------- | ----- | --- | --- | --- | --- | --- | --------------- | --- | --- | ------- |
| 3:                         |                    |                      |       |     |     |     |     |     | ini*al grouping |     |     | Group 1 |
|                            |                    |                      |       |     |     | 2   |     |     | 2               |     |     |         |
| 4: v←                      | n e ar e s t u n e | x p a n d ed n o d e | i n C |     |     | 2 2 |     | 1   |                 |     | 3   |         |
2 2
▷ Asy n c n e i g h b o r f e tc h vi a x C o p i er(§6.1) 3 coa rse unco arse
|                              |     |     |            |     |     | 3 1 | 2   | via LPA |     |     | w/ LPA |     |
| ---------------------------- | --- | --- | ---------- | --- | --- | --- | --- | ------- | --- | --- | ------ | --- |
| 5: Asyncfetchv’sneighborsinG |     |     | cpu;addtoD |     |     |     |     |         |     |     |        |     |
▷GPU-cachedneighborsfromgraphtiering(§5)
Figure8:Multi-levelLPA.Thenodecolorsrepresentgroups.
E←neighborsofvinG
| 6:  |     | gpu |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
7: E←E∪{u∈D|transfercompleted};updateD;
▷Adaptivesynchronization(§6.2) Itsmotivationsanddesignsaregeneralandadaptabletovari-
| 8: Sync-waitoverduenodesinD;movetoE |     |     |     |     |     | ousKNNgraphs[9,10]. |     |     |     |     |     |     |
| ----------------------------------- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- |
9: foreachu∈Edo
• Graphupdates.Likepriorefforts[19,20,22,55],Flow-
computedistancebetweenqandu;insertuintoC
| 10: |     |     |     |     |     | ANNfocusesonthesearchprocess.Itcanuseexistingonline |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- |
11: endfor
orofflinegraphupdatemethods[56–59],andupdatethetiered
12: endwhile
|     |     |     |     |     |     | graphwithminimaleffort,e.g.,via |     |     |     | a single | roundoflabel |     |
| --- | --- | --- | --- | --- | --- | ------------------------------- | --- | --- | --- | -------- | ------------ | --- |
13: returnRerankthecandidatesinConCPUandreturnthetop-k
propagation(§5.1)toassignnewnodestogroups.
• Clusterservingandmulti-GPU.FlowANNaimstomax-
candidatepool(i.e.,GPUresults)arere-rankedonCPUusing imizesingle-GPUcapabilityforbillion-scaleANNS.Itcan
theoriginalfull-precisionvectorstoensurefinalresultaccu- bedeployedwithmultiplereplicasinclusters.Itcanbeinte-
gratedintomulti-GPUsystemsforprospectivelargerdatasets.
racy.TheCPUre-rankingandGPUsearcharealsopipelined
acrossbatches.Algorithm1providestheprecisepseudocode • Hardwaregenerality.WhileFlowANNisimplementedon
NVIDIAGPUs,whichrepresentcutting-edgearchitectures,
ofthesearchprocedure.
GPU-CPUgraphtiering.FlowANNprioritizesstoringshort itcanbeadaptedtootherSIMT-basedGPUs(e.g.,AMD).
| edges on | the GPU. | To avoid distributional |     | imbalance | of  |     |     |     |     |     |     |     |
| -------- | -------- | ----------------------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
cachededgescausedbyastaticlengththreshold,itutilizes
5 DeferrableDiscoverywithGraphTiering
groupingtoselectedgesforGPUresidency,consideringboth
edgelengthandgraphspatialdistribution. Specifically,we GuidedbyInsight#2(§3),graphtieringshouldprioritizeplac-
employmulti-levellabelpropagation(§5.1)topartitionthe
|     |     |     |     |     |     | ingshortedgesonGPU. |     |     | However,applyingafixedlength |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | ---------------------------- | --- | --- | --- |
graphintobalancedgroupswhilemaximizingtheretentionof thresholdtoselecton-GPUedgescausesimbalanceduetothe
shortedgeswithingroups,andthenplaceintra-groupedgeson
non-uniformdistributionofdatapointsinhigh-dimensional
theGPU.Moreover,onGPU,FlowANNreplaceseachnode’s
space.Specifically,indenseregions,manyedgesareshortand
globalIDfromabillion-scalenamespacewithashorterlocal wouldbestoredonGPU,whilenodesinsparseregionshave
IDwithineachgroup,anddesignsacompactmatrixgraph
fewedgescached.Thisleadstoquerieslocatedinsparsere-
layout(§5.2),allowingmoreedgestoresideonGPU. gionsbenefitinglittlefromtiering.Thus,graphtieringshould
Trap-lessasyncdatatransfer.WedesignxCopier,asystem
considerbothedgelengthandspatialnodedistribution.
servicethatenablesGPU-initiatedasynchronousdatatrans- Wefindthataftergroupingspatiallyproximatenodesinto
fer (§6.1). xCopier further enhances transfer performance the same group (i.e., grouping), the intra-group edges are
| by leveraging | hardware | capabilities: | it employs |     | Memory- |     |     |     |     |     |     |     |
| ------------- | -------- | ------------- | ---------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
suitableforGPUplacement:(1)Nodesconnectedbyshort
Mapped I/O (MMIO) via BAR mapping to replace DMA- edgesareoftenclosetoeachotherandnaturallyclusterwithin
| based cudaMemcpy,reducing |     | transferlatency |     | by  | 40× and |     |     |     |     |     |     |     |
| ------------------------- | --- | --------------- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
thesamegroup,whichsatisfiesthegoalofprioritizingshort
ensuringtheoverlapofdatamovementandcomputation.
edges;(2)Groupingholisticallyconsidersthespatialdistri-
Coordinatedpipeline.FlowANNpipelinesGPUcomputa- butionofallnodes,preventingnodesinsparseregionsfrom
tionandCPU-GPUtransfer.Topreservesearchefficiency,it
beingexcludedbyasingleedgelengththreshold.
preventsexcessivelydeferredexpansionthroughadaptivesyn- Challenges.However,designingahigh-qualitygraphgroup-
chronization,whichconsidersbothglobalsearchconvergence
ingandtieringschemeisstillchallengingduetotwoissues.
progressandlocalfluctuations.FlowANNemployscross-step First,partitioningabillion-scalegraphtomaximizethereten-
balancingtoalignthedynamicallyvaryingper-stepworkload tionofshortedgeswithingroupsisanNP-Completeprob-
withhardwareresources,andselectssuitableentrypointsto
|     |     |     |     |     |     | lem [60, | 61]. | Simplyapplying | common | grouping | methods |     |
| --- | --- | --- | --- | --- | --- | -------- | ---- | -------------- | ------ | -------- | ------- | --- |
shortentheapproachphase(§6.2). (e.g.,K-means)oftencausespoorgroupingquality,asthey
Discussions.WediscussFlowANN’sscopeandgenerality.
|     |     |     |     |     |     | only consider |     | global node | distribution | while | ignoring | the |
| --- | --- | --- | --- | --- | --- | ------------- | --- | ----------- | ------------ | ----- | -------- | --- |
• Generalityforgraphstructures.FlowANNisbasedon graph’sstructuralinformation(e.g.,edgeconnections).For
thewidely-usedCAGRA[51](i.e.,NN-Descent[54])graph. instance,whengroupingviaK-means,only~60%ofedges
1568    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Algorithm2Multi-levelLPAGraphGrouping neighbor count padding valid neighbors
Node 1 3
Require: KNNgraphG=(V,E),maxgroupsizeS max Node 2 5 35
1: Assignedgeweightw(e)←mapping(len(e)) ID within group (GPU)
Node 3 2
2: Assigneachnodewithaninitialgrouplabel 25
Node 4 5
▷Coarsening(❶inFig.8)
(a) Fixed-length 2D matrix (b) Complementary 2D matrix
3: whilegraphisnotsufficientlysmalldo
Figure9:Graphlayoutwithcomplement.
4: ▷WeightedLPA
5: Foreachnodev,sumedgeweightsperneighborlabell:
totalWeight(l)=∑u∈neighbors(v),label(u)=l w(v,u) ficientlysmall(❶);Theninitialgroupsaregeneratedonthe
6: label(v)←thelabellwithmaximumtotalWeight(l) coarsenedgraphviarecursivebipartitioning[63](❷);Finally,
7: Mergenodessharingalabelintoasuper-node
thegroupsareprojectedbacktotheoriginalgraph,withLPA
8: endwhile appliedduringuncoarseningtorefinegroupboundaries(❸).
9: ▷Initialgrouping(❷inFig.8)
ThefullprocedureisgiveninAlgorithm2.
10: Partitionthecoarsestgraphviarecursivebipartitioning
11: ▷Uncoarsening+refinement(❸inFig.8) Benefits.Multi-levelLPAcaneffectivelypreserveshortedges
12: foreachlevelfromcoarsestbacktooriginalgraphdo withingroupsandobtainbalanced,high-qualitygroupsfroma
13: Copyeachsuper-nodelabeltoitsfiner-levelnodes globalperspective.Thisismainlybecause:(1)localstructure
14: RunweightedLPAtoadjustboundarynodes awareness: it captures local graph structure through label
15: endfor propagation based on edge connections and edge lengths,
16: returnthefinalgrouplabelforeachnode ensuring that nodes connected by short edges are grouped
together;(2)globaldistributionconsideration:bygenerating
groupsfromaglobalviewofthecoarsenedgraphandrefining
that have insufficient windows are retained within groups
them locally during uncoarsening, it holistically takes the
(Fig.17a). This necessitates a grouping scheme tailored to
nodes’distributionintoaccount.Moreover,sinceLPAmainly
KNNgraphstomaximizeintra-groupshortedgeretention,
reliesonlocallabelpropagation,itachievesnear-lineartime
whilekeepingcomputationalcomplexitytractable.Second,
complexity,makingitwell-suitedforbillion-scalegraphs.
aftergrouping,thenumberofintra-groupneighborspernode
mayvary.Continuingtostoreeachnode’sneighborsina2D
5.2 CompactGraphLayoutwithComplement
matrixresultsinnon-trivialmemorywasteduetopadding.
Toensurequickrandomaccesstoeachnode’sneighbors,exist-
5.1 SpatialLocality-awareGraphGrouping inggraphANNSsystemsstorethegraphonGPUusinga2D
matrixwithfixed-lengthrows,whereeachrowcorrespondsto
Forhighintra-groupshortedgeretention,thegraphgrouping
anode’sneighborlist,asshowninFig.9(a).However,after
schemeinFlowANNshouldconsiderbothedgeconnections
grouping,thenumberofintra-groupneighborsforeachnode
andnodedistribution.Toachievethis,weemployMulti-level
becomesvariable. Continuingtousethis2Dmatrixwould
labelpropagation(multi-levelLPA)forgraphgrouping,which
leadtosignificantmemorywasteduetopadding(Fig.9(a)).
isinspiredbyatheoreticalgraphgroupingscheme[38].
Throughtheanalysisofintra-groupneighborcountdistri-
Procedure.Multi-levelLPAisbasedonthesize-constrained butions,weidentifyapotentialmemory-savingopportunity:
weightedlabelpropagation,whichproceedsasfollows:First, thedistributionexhibitsaquasi-symmetricshape,indicating
eachedgeisassignedaweight,whereshorteredgesreceive thatthespacesavedbythehalfofnodeswithfewerneighbors
higherweights.Then,eachnodeisinitializedwithaunique effectivelycomplementstheextraspacerequiredbythehalf
grouplabel.Ineachsubsequentiteration,everynodecalcu- withmoreneighbors.Thus,asFig.9(b)shows,weemploya
latesthesumofweightsfromitsneighborsforeachdistinct newgraphlayoutforthesubgraphsontheGPUandCPU.
labelandupdatesitsownlabeltotheonewiththehighesttotal ForthesubgraphontheGPU,nodesarefirstsortedbytheir
weight[62](Fig.8).6Toensurebalancedgroupsizes,weintro-
intra-groupneighborcounts. Theyarethenpairedbyitera-
duceasizeconstrainttolimitthemaximumgroupsizeduring tivelymatchingthenodewiththemostintra-groupneighbors
propagation.7 Notably,theedgeweightefficientlyincorpo- totheonewiththefewest.Eachpairisstoredinasinglerow.
rates edge length information, ensuring that shorter edges ThecaseforCPUissimilar.Thismethodnotonlyreduces
haveahigherlikelihoodofbeingretainedwithingroups. spacewastefrompadding(§7.3)butalsopreservesefficient
As Fig. 8 shows, multi-level LPA involves a coarsen- randomaccess,asthegraphisstillstoredina2Dmatrixwith
uncoarsen process: The graph is recursively coarsened by afixednumberofneighborlistsperrow.
groupingnodesintosuper-nodesthroughLPAuntilitissuf- Moreover,leveragingthepropertythatnodesintheGPU-
tieredgraphareonlyconnectedwithinthesamegroup,weuse
6Ifallneighborlabels’summedweightsaretied,oneisrandomlychosen.
7FlowANNchoosesthemaximumgroupsizethatretainsthemostintra- shortergroup-localIDs(e.g.,20–24bits)ratherthanglobal
groupshortedgeswhilestayingwithinthecurrentGPUmemorybudget. graph-wide IDs (e.g.,32bits) to representeachnode. This
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1569

Copy in process ▶ operators for GPU kernel Naive xCopier (CPU) GPU
❶cudaMemcpy (toDev)
cTail head func xCheck (tkt) -> ready:
Copy cudaRuntime ❷check & forward DMA engine HBM
finished /
b
*
e t
c
w
h
e
e
e
c
n
k
c
w
T
h
a
e
il
t h
a
e
n
r
d
t
g
h
T
e
a i
t
l
ic
*
k
/
et is cudaDriver ❸copy data& addr. trans. ❹❺issue ❻move ❼inter-
gTail return ((tkt - xQ.gTail) & MASK) DMA subsystem ❹submit DMA cmd DMA data rupt
PCIe
xeue (on GPU, xQ) < ((xQ.cTail - xQ.gTail) & MASK); (a) Normal cudaMemcpy (4 PCIe, 2 context switch)
func xCopy (dst, src, n) -> tkt: func xRelease (tkt): xCopier (CPU) GPU
idx = enqueue(xQ, {dst, src, n}); xQ.cmds[tkt & MASK] = EMPTY; PCIe ❶store instr. & MMIO ❶
return idx; // forward gTail if possible … (b) Copy w/ BAR mapping (1 PCIe, bypass kernel, no runtime)
Figure11:CopyingprocessofxCopierandcudaMemcpy.
Figure10:xQueueoperators. Theatomicoperationsaresimplified.
enablesmoreedgestoresideontheGPU(Fig.17a),thereby tiateddirectlyfromGPUthreads,bridgingthearchitectural
allowingmorecomputationtooverlapwithdatatransfer. gapintheGPUecosystem.xCopierisbuiltaroundaGPU-
sideringqueue(xQueue)andaCPU-sidedata-movingthread
(xThread). The xQueue, featuring one head and two tails,
6 ExecutionwithCoordinatedPipeline
exposesthreeprimitives:xCopy,xCheck,andxRelease.
Specifically,as Fig.10 shows,a GPU thread initiates an
Thetieredgraphenablesdeferreddiscovery.However,effi-
async transfer via xCopy, which enqueues a transfer com-
cient transfer-computation pipelining remains challenging.
mandintoxQueueandreturnsitsqueueindexastheticket.
WedesignxCopiertosupportefficienttrap-lessasynchronous
The xThreadpolls xQueue’s head,detects newcommands,
transfer(§6.1),andfurtherdevelopthecoordinatedpipeline
executes the data transfers, and finally advances the cTail
thatensuressearchefficiencyandhardwareutilization(§6.2).
(cpu_tail).TheGPUthreadchecksthestatusofanasynctrans-
ferwithxCheck,whichcomparestheticketagainstcurrent
6.1 StreamingDataMovementwithxCopier
cTail.Oncethetransferisconfirmedcompleted,thethread
canreclaimthecommandslotusingxRelease.Therelease
During search, FlowANN employs an asynchronous data
isatwo-stepprocess,whichallowsout-of-orderrelease: it
pipelinetofetchnon-cachededgesfromtheCPUtotheGPU,
firstmarksthecommandasinvalid,thenattemptstoadvance
overlappingtransfercostwithon-GPUcomputation.
gTail(gpu_tail)ifthereareinvalidcommandsatthetail.
Challenges. This design,however,is impededby two fun-
TheseprimitivesarehighlyoptimizedforGPUparallelism.
damentalconstraintsinGPUarchitecture:(1)Tominimize
Weemploybatchedinvocationandwarp-levelaggregation,so
kernellaunchoverhead,FlowANNfusesallsearchstepsinto
thatallxCopy/xReleaseinawarprequirejustoneatomicop-
amonolithickernel.However,noexistingmechanismpermits
erationtoupdatehead/gTail.xCopierfurthermitigatesatomic
aGPUkerneltoinitiateasynchronouscopiesbetweendevice
operationcontentionbysupportingmultiplexQueues.The
andhost.(2)TheperformanceofstandardCUDAcopyop-
xThreadcanbescaledtomultiplethreadsunderhighload.
erations(e.g.,cudaMemcpy)[37,64]ispoorforsmalldata
Efficient data transfervia BAR mapping. In FlowANN,
blocks(typically64–256bytespernode’sedges),astheyare
everydatatransfercommandinvolvescopyingtheuncached
bottleneckedbytheinherentDMAenginelaunchoverhead.
edgesofaparentnode(64–256bytes).Evenwhenbatched,
CPU-GPUdatamovement.Webeginbyrecapturingexist-
thetransfersremainrelativelysmall.However,conventional
ingdatamovementmechanismsbetweentheCPUandGPU.
DMA-basedmechanisms(e.g.,cudaMemcpy)performpoorly
OnCPUside,transfersareinitiatedusingcudaMemcpy[37],
forsuchfine-grainedtransfers.AsFig.11(a)shows,thisinef-
whichcanbeasynchronouswithGPUcomputation.OnGPU
ficiencystemsfromtheDMAoverhead,whichinvolvesfour
side,dataaccesstoCPUmemoryisfacilitatedthroughtwo
PCIetransactions,twocontextswitchesinto/fromGPUdriver,
mechanisms:UnifiedMemory(UM)andZero-copy(Pinned)
andruntimeoverhead.AcudaMemcpy-basedxCopiertrans-
Memory[37].UMprovidesaunifiedaddressspace,migrating
ferfor64B–1KBdataincursalatencyashighas21–22µs
pages(triggeredbyGPUpagefaults)uponaccess.Zero-copy
(Fig.12),whichcannotbeoverlappedwithGPUcomputation.
MemoryenablesdirectGPUaccesstoCPUmemory.Criti-
Tosolvethischallenge,weemployanovelhardwarestrat-
cally,botharesynchronousandblockGPUkernelexecution.
egy:GPU’sBaseAddressRegister(BAR)mapping.Leverag-
ForFlowANN,eachtransfermechanismpresentsacritical
ingtheopen-sourcedriver[65]8,xCopiermapstheGPUmem-
limitation. CPU-initiated transfers require the search flow
oryregionsdirectlyintoCPU’sphysicaladdressspace.Subse-
toreturntotheCPUaftereachstep(i.e.,trap)[20],thereby
quentaccessestotheregionsarethenperformedviaMemory-
incurringsubstantialkernelterminationandlaunchoverhead.
MappedI/O(MMIO).Withhardwarewrite-combining,con-
Conversely,UnifiedMemoryandZero-copyMemoryforfeit
secutivewritesaretransparentlycoalescedintofewer,larger
theabilitytoconstructanasynchronouscopypipeline.
MMIOs.AsFig.11(b)shows,thisreducesCPU-to-GPUcopy
Trap-lessasynccopywithxCopier.WeintroducexCopier,
asystem-levelserviceforasynchronousdatamovementini- 8BARmappingisalsosupportedbyotherGPUs,e.g.,AMDROCm[66].
1570 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

cudaMemcpy BAR mapping copy (i.e.,P increases),asnodesnearthequerygraduallyaccu-
e
Host to Device Device to Host mulateattheheadofthecandidatepoolandaresuccessively
100
| )sμ( ycnetaL |     |     | 1000 |     |     |                                                   |              |        |     |                   |            |       |
| ------------ | --- | --- | ---- | --- | --- | ------------------------------------------------- | ------------ | ------ | --- | ----------------- | ---------- | ----- |
|              |     |     |      |     |     | expanded.                                         | Our analysis | across |     | tens of thousands | of         | query |
|              | 10  |     | 100  |     |     |                                                   |              |        |     |                   |            |       |
|              |     |     |      |     |     | tracesconfirmsthestrongcorrelationbetweenP        |              |        |     |                   | andthewin- |       |
|              | 40× |     | 10   |     |     |                                                   |              |        |     |                   | e          |       |
|              | 1   |     |      |     |     | dowsizesoftheexpandednode’sneighbors,withaPearson |              |        |     |                   |            |       |
18×
|     |     |     | 1   |     |     | correlation9=0.77. |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- |
0
|     | 16 256 | 4K 64K       | 1M 16 | 256 4K       | 64K 1M |                  |     |     |                              |     |     |     |
| --- | ------ | ------------ | ----- | ------------ | ------ | ---------------- | --- | --- | ---------------------------- | --- | --- | --- |
|     |        |              |       |              |        | FlowANNthususesP |     |     | toestimatethewindowsize(W)of |     |     |     |
|     |        | Size (Bytes) |       | Size (Bytes) |        |                  |     | e   |                              |     |     |     |
Figure 12: Copy latency ofBAR mapping andcudaMemcpy. theexpandednode’sneighborsineachstep,i.e.,W =α∗P e ,
Each(batched)xCopiertransferrequiresoneD2Hcopy(xQueue whereαisderivedfromofflineprofilingwithlinearregres-
headread)andtwoH2Dcopies(datawrite,xQueuecTailupdate). sion.Relyingonofflineprofilingissufficientherebecause
αdependsprimarilyonthedataset’sunderlyingdatadistri-
bution.Furthermore,thisformulationrobustlyadaptstody-
toasinglePCIetransaction,whichisexecutedbyCPUSIMD
namicvariationsintheapproachphase’slength.Specifically,
instructions,eliminatingcontextswitchesandruntimeover-
|     |     |     |     |     |     | since P | typically remains |     | zero | during the | approachphase, |     |
| --- | --- | --- | --- | --- | --- | ------- | ----------------- | --- | ---- | ---------- | -------------- | --- |
e
head,andacceleratingsmalltransfersbyupto40×(Fig.12). theestimatedwindowW willalsobezero,ensuringaccurate
|     | In FlowANN, | each xQueue | is associated |     | with a pre- |     |     |     |     |     |     |     |
| --- | ----------- | ----------- | ------------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
synchronizationwithoutdependingonofflinestatistics.
allocated(andBAR-mapped)GPUbufferpoolforthefetched
Beyondthenormalcases,weobservethatfluctuationsdur-
edges.Asageneral-purposesystemservice[67],xCopieris
ingsearchconvergencecanleadtounexpectedlysmallwin-
readilyapplicabletootherGPUworkloads[68–70].
|     |     |     |     |     |     | dows,which | manifest | as  | a sharp | drop in | P. This happens |     |
| --- | --- | --- | --- | --- | --- | ---------- | -------- | --- | ------- | ------- | --------------- | --- |
e
whenthesearchintheconvergephaseunexpectedlydiscov-
6.2 PipeliningwithAdaptiveCoordination ers a node much closer to the query (i.e., a sharp drop in
|     |     |     |     |     |     | P). Once | such a node | is  | found,its | neighbors | become | the |
| --- | --- | --- | --- | --- | --- | -------- | ----------- | --- | --------- | --------- | ------ | --- |
e
LeveragingxCopier,FlowANNpipelinesGPUcomputation primetargetsforsubsequentexpansion,thustheirwindows
withCPU-GPUedgefetching.Ateachstep,thesearchkernel aresmall.FlowANNneedstohandlesuchcasesspecially.
firstselectstheunexpandednodeclosesttothequeryfromthe Adaptivesynchronizationbasedonwindowsize.Tohandle
candidatepoolastheparent,thenasynchronouslyfetchesits thefluctuationcases,whenFlowANNdetectsasharpdropin
uncachedneighborstoGPU(xCopy).Subsequently,itchecks P,itwaitsforallneighborsoftheparentnodetobefetched.
e
thecompletionstatusofpreviouslyissuedtransfercommands
Whilethisincursaperformancecost,suchfluctuationsoccur
(xCheck),anddiscoversboththeparent’scachedneighbors with very low probability (<3%). In our evaluation, Flow-
andtheneighborsthathavealreadybeentransferred. ANN sets the threshold for a sharp drop in P to 10% of
e
Challenges.Efficientpipeliningfacesnon-trivialchallenges. the candidate pool size. Meanwhile, in each step, if some
❶Althoughdiscovery-expansionwindowsenabledeferred neighborsfrompreviousstepshavebeendeferredformore
discovery,excessivedeferralsleadthesearchtosuboptimal thantheirestimatedwindows,FlowANNalsowaitsfortheir
paths,sacrificingefficiency(§6.2.1).❷Duetodeferreddis- discoveriestocomplete.
coveries,thediscoveryworkloadperstepvariesdynamically,
Stall-lesssynchronization.Toavoidwastingcomputational
resulting in a mismatch with pre-determined hardware re- resources,FlowANNyieldsthehardwarethreadstoschedule
sources (§6.2.2). ❸ During the approach phase (§3), the otherqueries’computationsduringthewait.Thisscheduling
windowsaretoosmalltohideedgetransfers(§6.2.3). isverylightweight,asitishandledbythehardwarescheduler.
6.2.1 Near-optimalSearchwithAdaptiveSynchronization 6.2.2 RegularizingWorkloadwithCross-StepBalancing
Excessivedeferralofdiscoveriesleadsthesearchtosubopti- Inprevioussynchronousexecution,thenumberofnodesdis-
|     |     |     |     |     |     | covered | perstep (i.e.,the |     | parent | node’s | neighborcount) | is  |
| --- | --- | --- | --- | --- | --- | ------- | ----------------- | --- | ------ | ------ | -------------- | --- |
malpaths,sacrificingefficiency.Toavoidunnecessarycom-
putationandtransfer,FlowANNsynchronouslywaitsforthe deterministic.However,asFlowANNdeferssomenodes’dis-
|     |     |     |     |     |     | coveries,this | count | becomes | dynamic. | This | causes | severe |
| --- | --- | --- | --- | --- | --- | ------------- | ----- | ------- | -------- | ---- | ------ | ------ |
completionofsomediscoveriesiftheirdeferredstepsexceed
theirdiscovery-expansionwindows.However,estimatingthe GPUunder-utilizationbecausecomputationalresources(e.g.,
windowisnon-trivial,asitvarieswiththesearchprocess. CUDAcores,sharedmemory)arestaticallypredetermined.
FlowANNintroducesacross-stepbalancingmechanismto
Estimatingthewindowsize.Wefindtheexpandednode’s
positioninthecandidatepool(P)canbeaneffectiveindi- alignthediscoveryworkloadwithhardwareresources.Specif-
e
ically,wheneachstepbegins,FlowANNidentifiesthreecat-
| cator | to estimate | the window | size. Specifically,during |     | the |     |     |     |     |     |     |     |
| ----- | ----------- | ---------- | ------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
egoriesofnodestodiscover:❶theparent’sneighborsthat
| approach | phase | (§3), the | search rapidly | advances | toward |     |     |     |     |     |     |     |
| -------- | ----- | --------- | -------------- | -------- | ------ | --- | --- | --- | --- | --- | --- | --- |
resideontheGPU,❷deferrednodesthatmustbediscovered
| thequery,andboththewindowsizeandP |     |     |     | e areusuallyzero. |     |     |     |     |     |     |     |     |
| --------------------------------- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Asthesearchconverges,thewindowsizeincreases(Fig.4).
9Pearsoncorrelationmeasuresthelinearrelationshipbetweentwovariables,
Meanwhile,theexpandednode’spositionshiftsrightwards
withvalues>0.7indicatingstrongcorrelation[71,72].
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1571

duetosynchronizationconstraints,and❸deferrednodesthat
Dataset Dimension Type #Vector#QueriesPQdim
havealreadybeentransferredtotheGPUbutcanbefurther
Datasets SIFT1B 128 uint8 1B 10,000 16
deferred. Ifthe totalnumberofthese nodes does notalign DEEP1B 96 float32 1B 10,000 24
withthehardwareresources,FlowANNdefersthediscovery SPACEV1B 100 int8 1.4B 29,316 13
ofsomenodesfromcategory❸tothenextstep.Forexample,
GPU&Arch. Memory GPU&Arch. Memory
if32threadteams(eachteamdiscoversthenodescollabora-
tively)areallocatedforeachquery,FlowANNtriestoalign GPUs H20(Hopper) 96GBHBM3 A800(Ampere)80GBHBM2
thenumberofnodesdiscoveredpersteptoamultipleof32. L20(Ada) 48GBGDDR6 V100(Volta) 32GBHBM2
Theextranodesarepassedtothenextstepviasharedmemory.
Table1:DatasetsandGPUsusedinevaluation.
6.2.3 ShorteningApproachPhasewithEntryPoints pipelining.Itsstepndependsonstep(n-2).Weimplement
itsin-memoryversionbasedonitsavailableartifact.
Intheapproachphase(§3),thesmalldiscovery-expansion
windowsnecessitatefrequentsynchronization,leadingtonon- • Unifiedmemory(UM).UMunifiesCPUandGPUmem-
negligibleoverhead.Toreducetheproportionofthisphase, ory.WeextendCAGRA[51]withUM(CAGRA-UM).
FlowANNselectssuitableentrypointsforeachquery,instead • Multi-GPU. GGNN [43] is the only billion-scale multi-
ofstartingfromrandomnodes.Inspiredbytheprinciplesof GPUgraphANNSsystemknowntous.10Itshardsdataacross
cluster-basedANNS,weselectasetofrepresentativenodes multipleGPUs,witheachGPUperformingsearchesonits
fromthedataset(e.g.,K-meanscentroids)ascandidateentry correspondingsubgraph,andthenmergestheresults.
points,andchoosetheonesclosesttothequerythroughpar-
Configurations.Giventhecharacteristicsofthedatasetsand
allelcomputation.Thisapproachquicklyidentifiessuitable
theconstraintsofCAGRA,wequantizethevectorstothedi-
entry points by leveraging the GPU’s parallel capabilities.
mensionsinTable1(PQdim)forGPUsearch,andapplythe
Thankstotheselectednodes’representativeness,onlyavery
samequantizationsettingstocuVS-clusterandfaiss-cluster.
smallnumberofcandidates(oneinamillion)arerequiredto
However,since BANG cannot achieve high accuracy with
reducetheapproachphaseto~5%oftotalsearchsteps.
thesequantizationparameters,weuseBANG’sdefaultquan-
tizationsettings(PQdim=74)toensureitattainscomparable
7 Evaluation accuracy.ForFlowANNandallgraph-basedbaselines,we
setthegraphdegreeto32,followingCAGRA[51]’sofficial
Implementation.WebuildFlowANNwith14,700linesof practice. WealsomeasureFlowANN’sperformanceunder
CUDA/C++basedonCAGRA[51](i.e.,graph-basedANNS differentquantizationsettingsanddegreesin§7.2.
incuVS[27]),aSOTAsystemopen-sourcedbyNVIDIA. Metrics.Wemeasuresearchaccuracyusingrecall@k[32]:
Hardware setup and datasets. All experiments run on a thefractionoftrueknearestneighborsinthereturnedresults.
serverwith2IntelXeonPlatinum8457CCPUs(2.60GHz, Without explicit mention,we measure the throughput (i.e.,
160cores),2TBDRAM,andNVIDIAH20GPUs.Wealso queries per second,QPS) and latency at 0.9 recall,a com-
evaluateFlowANNonotherGPUs(§7.4.2).Wemainlyuse monlyusedaccuracytargetinANNS[11,36,73].Wealso
threewidely-usedbillion-scaledatasets[39–41].Thespecifi- evaluateFlowANNunderdifferentaccuracytargetsin§7.1.
cationsofGPUsanddatasetsaresummarizedinTable1.
Baselines.Wecomparewith8GPUANNSsystems. 7.1 OverallPerformance
• Quantized cluster-based ANNS. SOTA cluster-based
ANNSsystemsfirstsearchonGPUusingquantizedvectors WeevaluateFlowANNandthebaselinesystemsundervarious
(e.g.,PQ[32]),thenre-ranktheresultswithfull-precisionvec- batchsizes(from16to2048)toreflectdifferentapplication
torsonCPU.WeevaluatecuVS-cluster[27](NVIDIA)and scenarios,suchasonlineserving(smallbatchsize)andoffline
faiss-cluster[24](Meta).Wecarefullyimplementin-memory processing(largebatchsize),similartopriorworks[19].
FusionANNS[22]basedoncuVSasitisnotopen-source. Throughput.AsFig.13shows,FlowANNoutperformsall
• Full-precisioncluster-basedANNS.Rummy[19]stores baselinesacrossbatchsizesanddatasets.Comparedtocluster-
allfullvectorsonCPUandtransfersthemtoGPUondemand, based baselines,it achieves 8.67× and 8.15× higher aver-
overlappingdatatransferwithcomputationviapipelining. agethroughputforbatchesof2048and16,respectively.The
performance gain improves with larger batches, as the in-
• Graph-based ANNS. BANG [20] supports in-memory
creasedper-stepcomputationtimebetterhidesdatatransfer.
billion-scale graph ANNS on a single GPU. It stores PQ-
Thecluster-basedmethodsunderperformFlowANNandscale
quantizedvectorsonGPU,whilethegraphandfullvectorsare
poorlywithbatchsizeastheirbrute-forceintra-clustersearch
storedinCPUmemoryandtransferredtoGPUon-demand.
• GraphANNSwithrelateddependency.Thelatestwork, 10Arecentlyproposedsystem(PathWeaver[23])cannotsupportbillion-scale
FlashANNS [42] relaxes step-level dependency for better datasetsonourtestbedduetoitshighmemoryconsumption.
1572 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

FlowANN Faiss-cluster Rummy FlashANNS FlowANN Faiss-cluster Rummy FlashANNS
)SPQK( tuphguorhT cuVS-cluster FusionANNS BANG cuVS-cluster FusionANNS BANG
|     |     |     | SIFT1B (Throughput) |     |     |     |     | )sm( ycnetaL |     |     | SIFT1B (Latency) |     |     |     |
| --- | --- | --- | ------------------- | --- | --- | --- | --- | ------------ | --- | --- | ---------------- | --- | --- | --- |
| 75  |     |     |                     |     |     |     |     | 400          |     |     |                  |     |     |     |
300
50
200
| 25  |     |     |     |     |     |     |     | 100 |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0
0
|                   | 24  | 25  | 26  | 27         | 28  | 29  | 210 211 |                   | 24  | 25  | 26  | 27 28      | 29  | 210 211 |
| ----------------- | --- | --- | --- | ---------- | --- | --- | ------- | ----------------- | --- | --- | --- | ---------- | --- | ------- |
| )SPQK( tuphguorhT |     |     |     | DEEP1B     |     |     |         | )SPQK( tuphguorhT |     |     |     | SPACEV1B   |     |         |
| 90                |     |     |     |            |     |     |         |                   | 60  |     |     |            |     |         |
| 60                |     |     |     |            |     |     |         |                   | 40  |     |     |            |     |         |
| 30                |     |     |     |            |     |     |         |                   | 20  |     |     |            |     |         |
|                   | 0   |     |     |            |     |     |         |                   | 0   |     |     |            |     |         |
|                   | 24  | 25  | 26  | 27         | 28  | 29  | 210 211 |                   | 24  | 25  | 26  | 27 28      | 29  | 210 211 |
|                   |     |     |     | Batch Size |     |     |         |                   |     |     |     | Batch Size |     |         |
Figure13:ThroughputandaveragelatencyofFlowANNandbaselines.Recall@10=0.9.Duetospaceconstraints,weonlypresentthe
latencyresultsonSIFT1B;trendsonDEEP1BandSPACEV1Baresimilar.WeomitCAGRA-UMinthefigureforitslowperformance.
saturatesGPUresourcesearlierthangraphtraversal.Fusio- )SPQK( tuphguorhT GGNN (2 GPUs) GGNN (4) GGNN (8) FlowANN
| nANNS       | outperforms |     | cuVS-cluster |     | because | of its | heuristic |     | 60  |     |     |     |     |     |
| ----------- | ----------- | --- | ------------ | --- | ------- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- |
| re-ranking. |             |     |              |     |         |        |           |     | 40  |     |     |     |     |     |
FlowANNachieves9.52×and78.8×higherthroughput
20
| than                                             | BANG | on average | for | batch | sizes | 2048 and | 16. This |        | 0                       |     |       |            |     |            |
| ------------------------------------------------ | ---- | ---------- | --- | ----- | ----- | -------- | -------- | ------ | ----------------------- | --- | ----- | ---------- | --- | ---------- |
|                                                  |      |            |     |       |       |          |          |        | 23                      | 24  | 25 26 | 27 28      | 29  | 210 211    |
| isbecauseBANGonlyoverlapsedgefetchingwithlimited |      |            |     |       |       |          |          |        |                         |     |       | Batch Size |     |            |
|                                                  |      |            |     |       |       |          |          | Figure | 14: ThroughputofFlowANN |     |       | andGGNN    |     | on SIFT1B. |
computation(i.e.,poolupdates)andreliesoncostlycudaMem-
WeuseGGNN’sdefaultconfigurations.Whenrunningon2GPUs,
cpy,causingGPUstalls.Smallerbatchsizesfurtherworsen
GGNNoffloadspartofthegraphanddatatoCPUmemory.
| BANG’s    | overlapping |      | efficiency.  |     | In contrast,FlowANN |               | ef-        |     |     |     |     |     |     |     |
| --------- | ----------- | ---- | ------------ | --- | ------------------- | ------------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
| fectively | hides       | data | transfer     | by  | leveraging          | the           | discovery- |     |     |     |     |     |     |     |
| expansion | window      |      | and ensuring |     | efficient           | data transfer | via        |     |     |     |     |     |     |     |
GPUFlowANNwithGGNN[43].AsFig.14shows,evenwith
| xCopier. |     |     |     |     |     |     |     | 8GPUs,single-GPUFlowANNoutperformsGGNNby2.22– |     |     |     |     |     |     |
| -------- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- |
FlowANNoutperformsFlashANNSby3.71×and21.8× 15.3×atbatchsizesof8–1024.Onlyatbatchsize2048does
onaverageforbatchsizes2048and16.FlashANNS’relax- FlowANN’sthroughputslightlylagbehind8-GPUGGNN
ationofstep-leveldependencyislimitedandinflexible.Itfails (92.2%).GGNNrequires8GPUsandalargebatchtomatch
tooverlapI/Oeffectivelyforsmallbatches.Itleadstosubop-
FlowANN,becauseofitshighcommunicationoverheadand
timalsearchpathsduringtheapproachphase,andexcessive GPUunder-utilizationatsmallbatches.
waitingintheconvergephase.
Differentaccuracytargets.AsshowninFig.15,wemeasure
| Compared |     | to CAGRA-UM, |     |     | FlowANN | achieves | 110.8– |     |     |     |     |     |     |     |
| -------- | --- | ------------ | --- | --- | ------- | -------- | ------ | --- | --- | --- | --- | --- | --- | --- |
FlowANN’sthroughputacrossrecall@10from0.8to0.995
1888.8×higherthroughput.SinceUMisunawareofthegraph
traversal’srandomaccesspatterns,frequentpagefaultsand under small(64) and large(2048) batch sizes. We choose
cuVS-clusterastherepresentativeofcluster-basedmethods,
migrationsaretriggered,severelyhamperingperformance.
|     |     |     |     |     |     |     |     | as  | it shares fundamental |     | operations | (e.g., | distance | compu- |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------------- | --- | ---------- | ------ | -------- | ------ |
Latency.FlowANNachieveslowerlatencythanallbaselines.
tation)withFlowANN,enablingamoredirectcomparison.
Itreduceslatencyby83.8%and81.6%onaveragecompared
FlowANNoutperformsbaselinesacrossallaccuracylevels,
tobaselinesforbatchsizesof2048and16.Notably,atbatch
andtheperformancegapwidensathigheraccuracy.Atrecall
size16,itonlytakes0.962mstoprocessaquery.Thiseffi-
|     |     |     |     |     |     |     |     | =   | 0.8,FlowANN | outperforms |     | cuVS-clusterandBANG |     | by  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ----------- | --- | ------------------- | --- | --- |
ciencystemsfromitsaccurategraphtraversalandefficient
|     |     |     |     |     |     |     |     | 5.4× | and 28.9× | on  | average; | At recall=0.995,these |     | gains |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --------- | --- | -------- | --------------------- | --- | ----- |
pipeline,whichpreserveshighaccuracywhileeffectivelyhid-
increasesubstantiallyto29.1×and111.8×,respectively.
ingtransferoverhead.ItreducestheP99taillatencyby75.4%
and86.1%onaverageforbatchsizesof2048and16.
Impactofdeferreddiscoveryonsearchsteps.Wecompare
Cluster-basedbaselinesexhibithigherlatencythanFlow- search steps to reach the same accuracy with and without
ANN,especiallyinlargerbatches.Amongthem,Rummyhas deferreddiscovery(viaCAGRA-UM).Acrossthreebillion-
the highest latency,as its full-precision GPU computation scale datasets at accuracies from 0.8 to 0.995, FlowANN
increasesprocessingoverhead.BANGandFlashANNSex- introducesnoextrastepsinmostcases(~96%),withonlya
hibithighlatencyatsmallbatchesasthenon-overlappeddata
fewshowingamarginalincreaseof~0.7–2.1%insteps.This
transferbecomesmorepronouncedwithfewerqueries. showsthatdeferreddiscoverypreservessearchcorrectness
Comparisonwithmulti-GPUsystems.Wecomparesingle- andhasanegligibleimpactonconvergencespeedinpractice.
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1573

)SPQK( tuphguorhT FlowANN cuVS-cluster BANG )SPQK( tuphguorhT FlowANN cuVS-cluster )SPQK( tuphguorhT FlowANN BANG
Batch-64 Batch-2048 Batch-64 Batch-2048 29 Batch-64 Batch-2048
|     | 90  |     |     |     |     | 120 |     |     |     | 26  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
80
|     | 60  |     |     |     |     |     |     |     |     | 22  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
40
30
|     |     |     |     |     |     | 0   |     |     |     | 2−2 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0
80 90 100 80 90 100 16 32 64 16 32 64 16 32 48 64 16 32 48 64
|     |     | Recall@10 |     | Recall@10 |     |     | Quantized Length (PQ dim) |     |     |     | Graph Degree |     |     |
| --- | --- | --------- | --- | --------- | --- | --- | ------------------------- | --- | --- | --- | ------------ | --- | --- |
(a)Differentquantizedlengths
(b)Differentgraphdegrees
Figure15:Throughputunderdifferentaccuracy Figure16:ThroughputonSIFT1Bdatasetwithdifferentconfigurations.(a)These
(SIFT1B). threelengthsaretheonlysupportedlengthsbyCAGRAgiventhedimensionalityofSIFT.
oitaR UPG nI 1.0 GPU cache ratio )B( segdE UPG w/ BAR mapping w/ cuMemcpy w/o Adaptive Sync. Adaptive Sync.
0.9
20 )sμ( ycnetaL 45 Latency Scalability )%( 01@llaceR Batch-64 Batch-2048
|     | 0.8 |     |     |     |     |     | 12  |     | 100 |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0.7
|     | 0.6                |               | 10    |             | 30  |              | 8                  |           | 80  |          |         |          |         |
| --- | ------------------ | ------------- | ----- | ----------- | --- | ------------ | ------------------ | --------- | --- | -------- | ------- | -------- | ------- |
|     | 0.5                | FlowANN(Ours) |       |             |     |              |                    |           |     |          |         |          |         |
|     | 0.4                |               |       |             | 15  |              | 4                  |           | 60  |          |         |          |         |
|     |                    | K-means       |       |             |     |              |                    |           | 40  |          |         |          |         |
|     | 0.3                |               |       | 0           | 0   |              | 0                  |           |     |          |         |          |         |
|     | 0                  | 100           | Origi | n eans Ours | 25  | 27 29        | 211 213 23 25      | 27 29 211 |     |          |         |          |         |
|     |                    |               |       |             |     |              |                    |           |     | SIFT DEE | P PACEV | SIFT DEE | P PACEV |
|     | Window Size (<150) |               | K-    | m           |     |              |                    |           |     | S        |         |          | S       |
|     |                    |               |       |             |     | Size (bytes) | # of thread blocks |           |     |          |         |          |         |
Dataset (billion-scale)
(a)Graphtieringqualitycomparison(SIFT1B) (b)PerformanceandscalabilityofxCopier (c)Impactofadaptivesynchronization
Figure17:Breakdownanalysis.ForFig.(a),allmethodsusethesameGPUmemorybudget(66GB).
7.2 SensitivityAnalysis complement-basedgraphlayoutreducesspacewaste,leaving
|     |          |         |       |                                |     |     | only ~0.506% | padding |     | for billion-scale |     | datasets, | reducing |
| --- | -------- | ------- | ----- | ------------------------------ | --- | --- | ------------ | ------- | --- | ----------------- | --- | --------- | -------- |
| We  | evaluate | FlowANN | under | different configurations,i.e., |     |     |              |         |     |                   |     |           |          |
memorywasteby~98.5%comparedtotheoriginallayout.
variousquantizationsettingsandgraphdegrees.
xCopier.WeevaluatexCopierondifferentdatasizesandcon-
Quantizationconfigurations.WeevaluateFlowANNunder
currency.AsFig.17bshows,comparedtousingcudaMemcpy,
varyingquantizedvectorlengths,usingbatchsizesof64and
xCopierwithBARmappingreducestheend-to-endfetching
| 2048 | (Fig.16(a)). | Across | different | quantization |     | configura- |         |           |     |          |       |         |          |
| ---- | ------------ | ------ | --------- | ------------ | --- | ---------- | ------- | --------- | --- | -------- | ----- | ------- | -------- |
|      |              |        |           |              |     |            | latency | by 78–80% | for | 32–8192B | data. | xCopier | achieves |
tions,FlowANNachievesaveragethroughputimprovements
highscalabilitytoserve2048concurrentthreadblocks(1024
of8.47×(smallbatch)and5.12×(largebatch)overcuVS-
threadsperblock)with64xQueuesduringsearch,thanksto
cluster,demonstratingitsadaptabilitytodifferentquantization
itslock-freedesignandthreadblock-levelaggregation.
settings.Longerquantizedvectorsimprovetraversalaccuracy,
Adaptivesynchronization.Wecomparethesearchaccuracy
reducingsearchstepstoreachtargetaccuracy.
withandwithoutadaptivesynchronization,usingthesame
Graphdegree.WeevaluateFlowANNundervaryinggraph
numberofsearchsteps.AsFig.17cshows,adaptivesynchro-
degrees(i.e.,neighborcounts).ItoutperformsBANGinall
nizationimprovesaccuracyby21.7%and6.2%onaverageat
| cases,achieving |     | 136.37× | (small | batch) | and 14.72× | (large |     |     |     |     |     |     |     |
| --------------- | --- | ------- | ------ | ------ | ---------- | ------ | --- | --- | --- | --- | --- | --- | --- |
batchsizesof64and2048,enablinghigh-accuracysearchof
batch)higherthroughputonaverage(Fig.16(b)).Ahigher
recall@10>0.9.Smallerbatchesleadtoshortercomputation
graphdegreediscoversmoreedges,improvingaccuracyand
timeperstep,demandingmorepropersynchronizations.
reducingthenumberofsteps,butraisingtransferandcom-
putationaloverhead.ThisdegradesFlowANN’sthroughput
withsmallbatches;whereasunderlargebatches,thetransfer 7.4 ExtensiveStudies
isoverlappedbycomputation,resultinginperformancegains.
|     |     |     |     |     |     |     | 7.4.1 | PerformanceUpperBoundandLowerBound |        |     |         |         |      |
| --- | --- | --- | --- | --- | --- | --- | ----- | ---------------------------------- | ------ | --- | ------- | ------- | ---- |
|     |     |     |     |     |     |     | Gap   | to ideal upper                     | bound. | We  | compare | FlowANN | with |
7.3 BreakdownAnalysis
CAGRAonsmalldatasets.Itcachesonly50%oftheedges,
Graphtiering.Toevaluatemulti-levelLPA,wemeasurethe whileCAGRAretainstheentiregraphontheGPU.AsFig.18
GPUedgecacheratioforeachdiscovery-expansionwindow shows,atbatchsizesof64and2048,FlowANNachievesav-
eragethroughputequalto67.9%and85.4%ofCAGRA.This
sizeofallqueries(Fig.17a).Foredgeswithinsufficientwin-
dows (i.e.,window ≤ 5,§3),it keeps ~87.9% of them on confirmstheefficiencyofitstieredgraphandedgefetching
theGPU(89.1%forwindow=0),a29.6%improvementover pipeline.ItsperformancenearlymatchesCAGRA’satlarge
K-means.Moreover,Fig.17arevealsthatFlowANNimproves batches,whichenhancesGPUutilizationandextendsper-step
memoryefficiencyviagroup-localnodeIDs,storing18.2% executiontime,providingawiderwindowforasynctransfers.
and30.2%moreedgesonGPUthanK-meansandtheorig- PerformancewithoutGPUedgecache.WemeasureFlow-
inal(nogrouping)method.Thisisbecausemulti-levelLPA ANN’s throughput when all edges reside on the CPU (i.e.,
generatessmaller,morebalancedgroupsthanK-means.The w/otiering).AsFig.19shows,thethroughputofFlowANN
1574    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|                   | CAGRA (all in GPU) |     |     | FlowANN    |     | )SPQK( tuphguorhT | FlowANN  |     | All in CPU |     | )SPQK( tuphguorhT |     |     |     |
| ----------------- | ------------------ | --- | --- | ---------- | --- | ----------------- | -------- | --- | ---------- | --- | ----------------- | --- | --- | --- |
| )SPQK( tuphguorhT |                    |     |     |            |     |                   |          |     |            |     | 80                |     |     |     |
|                   | Batch-64           |     | 300 | Batch-2048 |     |                   | Batch-64 |     | Batch-2048 |     | 60                |     |     |     |
90
| 45  |     |     |     |     |     | 30  |     |     |     |     | 40  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
200
| 30  |     |     |     |     |     | 20  |     | 60  |     |     | 20  |         |            |      |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ---------- | ---- |
|     |     |     | 100 |     |     |     |     |     |     |     | 0   |         |            |      |
| 15  |     |     |     |     |     | 10  |     | 30  |     |     |     |         |            |      |
|     |     |     |     |     |     |     |     |     |     |     |     | 1 2 4 8 | Faiss cuVS | BANG |
| 0   |     |     | 0   |     |     | 0   |     |     | 0   |     |     |         |            |      |
SIFT DEEPSPACEV S I F T D E E P S P A C E V SIFT DEEP SPACEV SIFT DEEP SPACEV FlowANN
|     | (200M)(100M)(100M) |     | (2  | 0 0 M )( 10 | 0 M ) ( 1 00 | M ) |     |     |     |     |     |     |     |     |
| --- | ------------------ | --- | --- | ----------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
System
|     |     |     | Dataset |     |     |     | Dataset (billion-scale) |     |     |     |     |     |     |     |
| --- | --- | --- | ------- | --- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- | --- |
Figure20:Throughputunderdifferent
Figure18:FlowANN’sthroughputon100M Figure 19: Throughput of FlowANN w/o
searchwidths(1-8).SIFT1Bdataset.
| and200Mdatasetsandtheupperbound. |     |     |     |     |     | GPUcache(representinglowerbound). |     |     |     |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | --- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
)SPQK( tuphguorhT
FlowANN cuVS-cluster BANG Graph Building Layout Window Parameters
| 30  |     | Batch-64 |     |     |     | Batch-2048 |     |     | Grouping |     | Entry Point |       |     |     |
| --- | --- | -------- | --- | --- | --- | ---------- | --- | --- | -------- | --- | ----------- | ----- | --- | --- |
| 20  |     |          |     | 60  |     |            |     |     |          |     |             |       |     |     |
|     |     |          |     | 40  |     |            |     |     | SPACEV1B |     |             | 95.1% |     |     |
tesataD
| 10  |      |      |     | 20  |      |      |     |     |        |     |     |       |     |     |
| --- | ---- | ---- | --- | --- | ---- | ---- | --- | --- | ------ | --- | --- | ----- | --- | --- |
|     |      |      |     |     |      |      |     |     | DEEP1B |     |     | 94.9% |     |     |
|     | 0    |      |     | 0   |      |      |     |     |        |     |     |       |     |     |
|     | V100 | A800 | L20 |     | V100 | A800 | L20 |     |        |     |     |       |     |     |
|     |      |      |     |     |      |      |     |     | SIFT1B |     |     | 91.6% |     |     |
GPU Type
|     |     | Figure21:ThroughputacrossGPUs. |     |     |     |     |     |     | 0%  |     | 25% | 50% | 75% | 100% |
| --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- |
Percentage of Total Preprocessing Time
Figure22:PreprocessingtimebreakdownofFlowANN.
w/otieringreaches58.4%(batchsize64)and78.1%(batch
size2048)ofstandardFlowANN.Largerbatchesnarrowthis
gap,astheybetteroverlaptransferoverhead.Itstilloutper- and parameter acquisition for window estimation. Fig.22
forms the baselines (Fig.13) by 1.5–50.6× (batch 64) and showstheproportionofeachstepinthetotalpreprocessing
4.5–12.6×(batch2048).ThisshowsthatevenwithoutGPU
time.Theresultsindicatethattheextraoverheadintroduced
edgecaching,FlowANN’soptimizations(e.g.,xCopier,adap- bythesenewstepsisrelativelysmall:only4.9%,5.1%,and
tivesynchronization)stillyieldnon-trivialperformancegains. 8.4%onthethreedatasets,respectively.
7.4.2 GeneralityforAlgorithmsandHardware
8 Discussion
Applicabilitytobest-firstsearchvariants.Acommonvari-
antofbest-firstsearchistoexpandmultiplenodesperstep[8] Offloading strategy and future adaptability. FlowANN
primarilyoffloadsgraphconnectivitybecauseitconstitutes
| (i.e.,search |     | width > | 1) to | improve | efficiency. | We  | evaluate |     |     |     |     |     |     |     |
| ------------ | --- | ------- | ----- | ------- | ----------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
FlowANN’sthroughputwithdifferentsearchwidths(1–8). the main memory bottleneck in current billion-scale work-
AsFig.20shows,FlowANNoutperformsthebaselineacross loads(e.g.,SIFT1B).Thisrationalealignswithmainstream
tieredANNSdesigns[8,11].Toaccommodatethemassive
allsearchwidths.LargersearchwidthsallowFlowANNto
findhigh-qualityneighborsfaster,reducingtotalsearchsteps high-dimensional vectors typical of emerging LLM work-
|                                      |     |     |     |     |     |             |     | loads,FlowANN’s |     | tiering |     | design can naturally | support | of- |
| ------------------------------------ | --- | --- | --- | --- | --- | ----------- | --- | --------------- | --- | ------- | --- | -------------------- | ------- | --- |
| andimprovingthroughputuptoawidthof4. |     |     |     |     |     | Beyondthat, |     |                 |     |         |     |                      |         |     |
throughputdeclinesduetohigherper-stepcomputationcost floadingbothgraphedgesanddatavectors.Insuchacase,
anddiminishingimprovementsinresultquality. theneighbor’sdatavectorisfetchedsimultaneouslyduring
theasynchronousneighborfetchphase.
ApplicabilitytootherGPUarchitectures.BesidesNVIDIA
H20,wealsoevaluateFlowANNonV100,A800,andL20, Compatibility with dynamic updates. While FlowANN
mainlyfocusesonoptimizingthesearchprocess,itsprepro-
coveringmainstreamGPUs[74],asTable1details.AsFig.21
shows, under different architectures and memory capabili- cessingmechanismsdonotinherentlyhinderdynamicgraph
updates.FlowANNcanreadilyintegratewithexistingonline
| ties,FlowANN |     | consistently |     | outperforms |     | the baselines | (by |     |     |     |     |     |     |     |
| ------------ | --- | ------------ | --- | ----------- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
4.97–29.4×),demonstratingitsgenerality.Forsmallbatches, orofflinegraphupdatemethods.Whennewlyinsertedpoints
itsgainsoverbaselinesgrowwithlargermemory.Forlarge areaddedtothegraph,thesystemdoesnotrequireacomplete,
globalre-grouping.Forexample,anewlyinsertednodecan
| batches, | the | gains | increase | with | GPU | compute | power, as |     |     |     |     |     |     |     |
| -------- | --- | ----- | -------- | ---- | --- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- |
longerper-stepcomputationtimealreadyoverlapsdatatrans- begroupedbysimplycalculatingitsneighbors’weightsand
|     |     |     |     |     |     |     |     | joining | the validgroupwiththe |     |     | highesttotalweight. |     | Only |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --------------------- | --- | --- | ------------------- | --- | ---- |
fer,amplifyingtheimpactofcomputationalcapability.
|     |     |     |     |     |     |     |     | when | the number | of  | groups | exceeds a certain | threshold,a |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | ---------- | --- | ------ | ----------------- | ----------- | --- |
globalre-groupingisrequired.
7.4.3 PreprocessingCost
Compatibilitywithvariantgraphstructures.FlowANNis
FlowANN’s additional preprocessing steps beyond graph compatiblewithvariantgraphstructuresthatsupportbest-first
building(offline)includegraphtiering,entrypointselection, search.ThecoreoptimizationofFlowANNisdisentangling
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1575

step-leveldependenciestoexploitthetimewindowsbetween optimalsearchpathwithminimalcomputationaloverhead,
nodediscoveryandexpansion.Thismechanismisrootedin improvingbothlatencyandthroughput.
theiterativenatureofbest-firstsearch.Thus,FlowANNdoes Moreover, we believe that SSD is unsuitable for GPU-
notrequireanexactKNNgraphstructureandcanseamlessly basedgraphANNS’second-tierstorage:(1)SSD’slatency
adapttodiverseproximitygraphs. (~100µs[79])farexceedsgraphsearch’sper-stepexecution
Cost-effectiveness of GPU for ANNS. Due to the mas- time(6–14µs),andishardtobeoverlapped,leadingtolow
sive parallelism ofGPUs,GPU-basedANNS can yieldsu- GPU utilization; (2) GPU servers typically have TB-level
periorcost-efficiency(i.e.,QPS/$)comparedtoCPU-based memory [80–82], which is sufficient to hold billion-scale
ones[19,22].Thiseconomicadvantagehasdriventheadop- datasetsandgraphs.
tionofGPU-basedANNSinindustry[75],furtheramplified DistributedANNS.DistributedANNSsystems[43,83,84]
by hardware repurposing. While older or lower-tier GPUs focus on horizontal scaling to support ANNS on multiple
(e.g.,NVIDIAV100)arenolongersuitablefordemanding nodes.TheyarecomplementarytoFlowANN,asFlowANN
LLMworkloads,theyremainhighlyefficientforANNSand primarilyfocusesonmaximizingthesearchcapabilityofa
canberepurposedforcost-effectivedeployment. singleGPU.Additionally,tosupportthemulti-nodescenario,
Scalability of xCopierwith MMIO-based data transfer. FlowANNcanbedeployedasmultiplereplicas.
xCopier utilizes MMIO-based data transfer (§6.1), which GPUANNS’computationaloptimizations.Previousworks
maintainsitsperformanceadvantageoverDMAevenunder exploreparallelism[21,51,85,86],quantization[22,55],and
highconcurrency(i.e.,largebatchsizes).Forinstance,with multi-GPUcollaboration[23,43]. Theycanbe(oralready
batchsize10k,thetotaldatatransferredinonestepismerely havebeen)integratedwithFlowANN.
~1MB,allowingMMIOtomaintainitsadvantage(Fig.12). Graph-basedANNSonCPU.Manyworksoptimizegraph-
Asaresult,xCopierdoesnotencounterbandwidthbottlenecks basedANNSontheCPU,suchasparallelism[87,88],enhanc-
evenwhenallSMsarefullysaturated.xCopierwillfallback inggraphstructures[9,10,57,89–92],improvingquantiza-
toDMA-basedcopyingwhenMMIOisunavailable. tionmethods[12,31,93,94],andtuningparameters[46,95–
Necessityofdeferredexpansion.Aseeminglystraightfor- 99].TheseeffortsarecomplementarytoFlowANN.
ward alternative to deferred expansion is to rely purely on
hardwareyielding(i.e.,swappingtootherqueriesduringdata 10 Conclusion
transfers).However,yieldingaloneisinsufficienttohidela-
tencyduetoGPUresourcelimitsandbatchsizeconstraints. WepresentFlowANN,agraphANNSsystemenablingeffi-
BecauseGPUcomputationalresources(e.g.,sharedmemory cientbillion-scalevectorsearchonasingleGPU.FlowANN
andregisters)strictlyboundthemaximumnumberofqueries isbuiltonthekeyinsightthattherigidstep-leveldependency
simultaneouslyresidingonSMs,yieldingduringdatatrans- ingraphsearchcanbedisentangledintoafine-grainednode-
fers quickly stalls all active queries,leaving the GPU idle. leveldependency.Guidedbythisinsight,FlowANNadoptsa
Furthermore,pure yieldingrequires massivebatchsizesto tieredgraphstructurethatoffloadstheedgeswithsufficient
successfully interleave queries,rendering it ineffective for discovery-expansionwindowstotheCPU.Leveragingthese
latency-sensitiveonlineserving.FlowANN’sdeferredexpan- windows,FlowANNdefersthediscoveryofsomenodesand
sionovercomesbothlimitationsbyoverlappingtransferover- overlapstheiredgefetchingwithGPUcomputation.Evalu-
headwithineachindividualquery,ensuringhighperformance ationsonbillion-scaledatasetsshowthatFlowANNoutper-
withoutrequiringmassiveconcurrency. formsstate-of-the-artsystemsby4.08–45.7×onaverage(up
to172.6×)withoutcompromisingsearchaccuracy.
9 RelatedWork
Acknowledgments
SSD-basedANNS.Priorefforts[76–78]employpipelining
Wethankourshepherdandtheanonymousreviewersfortheir
forfetching data from SSD. AlthoughFlashANNS [42] a
insightfulcommentsandfeedback.WesincerelythankHaibo
one-steprelaxationinthesearchprocess,itstillmaintainsthe
Chenforhisguidancethroughoutthiswork,andJingweiXu
strictstep-leveldependency.PipeANN[11]relaxescompute-
andWeidongZhangfortheirhelpfulsuggestions.Thiswork
I/O order to better saturate SSD I/O bandwidth. However,
issupportedinpartbytheFundamentalandInterdisciplinary
it treats all nodes’ expansions equally, which may cause
DisciplinesBreakthroughPlanoftheMinistryofEducation
sub-optimalsearchpathswhensomeimportantexpansions
ofChina(JYB2025XDXM113)andtheNationalNaturalSci-
aredelayed.Additionally,unliketheCPU-SSDsetting,the
ence Foundation of China (No. 62132014, No.62302300).
compute-I/OgapforGPU-CPUisrelativelynarrow(similar
Correspondingauthors:MingkaiDong(mingkaidong@sjtu.
latency),whichlimitsthedegreeofI/Oparallelismthatcan
edu.cn)andDongDu(dd_nirvana@sjtu.edu.cn).
beexploited. FlowANNaccountsforthevariabilityinthe
discovery-expansionwindowacrossnodes,keepinganear-
1576 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| References |     |     |     |     |     | [8] SuhasJayaramSubramanya,Devvrit,RohanKadekodi, |     |              |     |     |        |         |     |
| ---------- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | ------------ | --- | --- | ------ | ------- | --- |
|            |     |     |     |     |     | Ravishankar                                       |     | Krishaswamy, |     | and | Harsha | Vardhan |     |
[1] ZhengdingHu,VibhaMurthy,ZaifengPan,WanluLi, Simhadri. DiskANN:fastaccuratebillion-pointnearest
XiaoyiFang,YufeiDing,andYukeWang. HedraRAG: neighborsearchonasinglenode. CurranAssociates
Co-optimizing generation and retrieval for heteroge- Inc.,RedHook,NY,USA,2019.
| neous RAG | workflows. | In Proceedings |     | of the | ACM |                                              |     |     |     |     |     |     |     |
| --------- | ---------- | -------------- | --- | ------ | --- | -------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|           |            |                |     |        |     | [9] CongFu,ChaoXiang,ChangxuWang,andDengCai. |     |     |     |     |     |     |     |
SIGOPS31stSymposiumonOperatingSystemsPrin-
Fastapproximatenearestneighborsearchwiththenav-
ciples,SOSP’25,page623–638,NewYork,NY,USA,
|     |     |     |     |     |     | igating | spreading-out |     | graph. |     | Proc. VLDB | Endow., |     |
| --- | --- | --- | --- | --- | --- | ------- | ------------- | --- | ------ | --- | ---------- | ------- | --- |
2025.AssociationforComputingMachinery.
12(5):461–474,January2019.
[2] SiddhantRay,RuiPan,ZhuohanGu,KuntaiDu,Shaot-
|     |     |     |     |     |     | [10] Yu.A. | MalkovandD.A. |     |     | Yashunin. | Efficientandro- |     |     |
| --- | --- | --- | --- | --- | --- | ---------- | ------------- | --- | --- | --------- | --------------- | --- | --- |
ing Feng,Ganesh Ananthanarayanan,Ravi Netravali, bustapproximatenearestneighborsearchusinghierar-
| andJunchenJiang. | METIS: |     | Fastquality-awareRAG |     |     |        |           |     |             |         |       |          |     |
| ---------------- | ------ | --- | -------------------- | --- | --- | ------ | --------- | --- | ----------- | ------- | ----- | -------- | --- |
|                  |        |     |                      |     |     | chical | navigable |     | small world | graphs. | arXiv | preprint |     |
systemswithconfigurationadaptation. InProceedings arXiv:1603.09320,2018.
oftheACMSIGOPS31stSymposiumonOperatingSys-
temsPrinciples,SOSP’25,page606–622,NewYork, [11] HaoGuoandYouyouLu. Achievinglow-latencygraph-
basedvectorsearchviaaligningbest-firstsearchalgo-
NY,USA,2025.AssociationforComputingMachinery.
|     |     |     |     |     |     | rithmwithSSD. |     |     | InProceedingsofthe19thUSENIX |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------- | --- | --- | ---------------------------- | --- | --- | --- | --- |
[3] Jie Li, Haifeng Liu, Chuanghua Gui, Jianyu Chen, Conference on Operating Systems Design and Imple-
|                               |                |      |           |                 |        | mentation,OSDI |              |     | ’25,USA,2025. |     | USENIX | Associa- |       |
| ----------------------------- | -------------- | ---- | --------- | --------------- | ------ | -------------- | ------------ | --- | ------------- | --- | ------ | -------- | ----- |
| Zhenyuan                      | Ni, Ning Wang, | and  | Yuan      | Chen. The       | de-    |                |              |     |               |     |        |          |       |
| sign and                      | implementation | of a | real time | visual          | search | tion.          |              |     |               |     |        |          |       |
| systemonJDe-commerceplatform. |                |      |           | InProceedingsof |        |                |              |     |               |     |        |          |       |
|                               |                |      |           |                 |        | [12] Yutong    | Gou,Jianyang |     | Gao,Yuexuan   |     | Xu,and |          | Cheng |
the19thInternationalMiddlewareConferenceIndustry,
|     |     |     |     |     |     | Long. | SymphonyQG: |     | Towards |     | symphonious |     | integra- |
| --- | --- | --- | --- | --- | --- | ----- | ----------- | --- | ------- | --- | ----------- | --- | -------- |
Middleware’18,page9–16,NewYork,NY,USA,2018.
tionofquantizationandgraphforapproximatenearest
AssociationforComputingMachinery.
|     |     |     |     |     |     | neighborsearch. |     | Proc.ACMManag.Data,3(1),Febru- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --------------- | --- | ------------------------------ | --- | --- | --- | --- | --- |
ary2025.
[4] SenLi,FuyuLv,TaiweiJin,GuliLin,KepingYang,Xi-
aoyiZeng,Xiao-MingWu,andQianliMa. Embedding- [13] ShulinZeng,ZhenhuaZhu,JunLiu,HaoyuZhang,Guo-
basedproductretrievalinTaobaosearch.InProceedings hao Dai, Zixuan Zhou, Shuangchen Li, Xuefei Ning,
ofthe27thACMSIGKDDConferenceonKnowledge
|     |     |     |     |     |     | Yuan | Xie,Huazhong |     | Yang,and |     | Yu Wang. | DF-GAS: |     |
| --- | --- | --- | --- | --- | --- | ---- | ------------ | --- | -------- | --- | -------- | ------- | --- |
Discovery&DataMining,KDD’21,page3181–3189, adistributedFPGA-as-a-Servicearchitecturetowards
NewYork,NY,USA,2021.AssociationforComputing billion-scalegraph-basedapproximatenearestneighbor
| Machinery. |     |     |     |     |     | search. | InProceedingsofthe56thAnnualIEEE/ACM |     |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | --- | ------- | ------------------------------------ | --- | --- | --- | --- | --- | --- |
InternationalSymposiumonMicroarchitecture,MICRO
[5] Liang Zheng, Liyue Shen, Lu Tian, Shengjin Wang, ’23,page283–296,NewYork,NY,USA,2023.Associ-
| Jingdong | Wang, and | Qi Tian. | Scalable | person | re- |     |     |     |     |     |     |     |     |
| -------- | --------- | -------- | -------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ationforComputingMachinery.
| identification: | A benchmark. |     | In 2015 | IEEE Interna- |     |     |     |     |     |     |     |     |     |
| --------------- | ------------ | --- | ------- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
tionalConferenceonComputerVision(ICCV),pages [14] ZhenhuaZhu,JunLiu,GuohaoDai,ShulinZeng,Bing
|     |     |     |     |     |     | Li, | Huazhong | Yang, | and | Yu Wang. | Processing-in- |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----- | --- | -------- | -------------- | --- | --- |
1116–1124,2015.
|     |     |     |     |     |     | hierarchical-memoryarchitecture |     |     |     |     | forbillion-scale |     | ap- |
| --- | --- | --- | --- | --- | --- | ------------------------------- | --- | --- | --- | --- | ---------------- | --- | --- |
[6] DiLiu,MengChen,BaotongLu,HuiqiangJiang,Zhen- proximatenearestneighborsearch. InProceedingsof
the60thAnnualACM/IEEEDesignAutomationConfer-
huaHan,QianxiZhang,QiChen,ChengruidongZhang,
ence,DAC’23,page1–6.IEEEPress,2025.
BailuDing,KaiZhang,ChenChen,FanYang,Yuqing
| Yang, and                                   | Lili Qiu. | Retrievalattention: |     | Accelerating |       |                          |     |               |     |                         |          |     |      |
| ------------------------------------------- | --------- | ------------------- | --- | ------------ | ----- | ------------------------ | --- | ------------- | --- | ----------------------- | -------- | --- | ---- |
|                                             |           |                     |     |              |       | [15] Ji-Hoon             |     | Kim, Yeo-Reum |     | Park,                   | Jaeyoung | Do, | Soo- |
| long-contextLLMinferenceviavectorretrieval. |           |                     |     |              | arXiv |                          |     |               |     |                         |          |     |      |
|                                             |           |                     |     |              |       | YoungJi,andJoo-YoungKim. |     |               |     | Acceleratinglarge-scale |          |     |      |
preprintarXiv:2409.10516,2024.
graph-basednearestneighborsearchonacomputational
|             |                                     |     |     |     |     | storage | platform. |     | IEEE | Transactions | on  | Computers, |     |
| ----------- | ----------------------------------- | --- | --- | --- | --- | ------- | --------- | --- | ---- | ------------ | --- | ---------- | --- |
| [7] FuBang. | GPTCache:Anopen-sourcesemanticcache |     |     |     |     |         |           |     |      |              |     |            |     |
72(1):278–290,2023.
forLLMapplicationsenablingfasteranswersandcost
savings. In Liling Tan, Dmitrijs Milajevs, Geeticka [16] Bing Tian,Haikun Liu,Zhuohui Duan,Xiaofei Liao,
Chauhan,JeremyGwinnup,andElijahRippeth,editors, HaiJin,andYuZhang. Scalablebillion-pointapprox-
Proceedingsofthe3rdWorkshopforNaturalLanguage imate nearest neighbor search using SmartSSDs. In
Processing Open Source Software (NLP-OSS 2023), Proceedingsofthe2024USENIXConferenceonUsenix
pages212–218,Singapore,December2023.Association AnnualTechnicalConference,USENIXATC’24,USA,
| forComputationalLinguistics. |     |     |     |     |     | 2024.USENIXAssociation. |     |     |     |     |     |     |     |
| ---------------------------- | --- | --- | --- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- | --- |
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1577

[17] YituWang,ShiyuLi,QilinZheng,LinghaoSong,Zong- YinghaoZou,JiquanLong,YudongCai,ZhenxiangLi,
wang Li, Andrew Chang, Hai "Helen" Li, and Yiran ZhifengZhang,YihuaMo,JunGu,RuiyiJiang,YiWei,
Chen. NDSearch:Acceleratinggraph-traversal-based andCharlesXie. Milvus:Apurpose-builtvectordata
approximatenearestneighborsearchthroughneardata managementsystem. InProceedingsofthe2021Inter-
processing. InProceedingsofthe51stAnnualInterna- nationalConferenceonManagementofData,SIGMOD
tionalSymposiumonComputerArchitecture,ISCA’24, ’21,page2614–2627,NewYork,NY,USA,2021.Asso-
| page368–381.IEEEPress,2025. |       |              |            |          | ciationforComputingMachinery.                 |     |     |     |     |          |
| --------------------------- | ----- | ------------ | ---------- | -------- | --------------------------------------------- | --- | --- | --- | --- | -------- |
| [18] Junhyeok               | Jang, | Hanjin Choi, | Hanyeoreum | Bae, Se- |                                               |     |     |     |     |          |
|                             |       |              |            |          | [26] JeffJohnson,MatthijsDouze,andHervéJégou. |     |     |     |     | Billion- |
ungjun Lee, Miryeong Kwon, and Myoungsoo Jung. scale similarity search with GPUs. arXiv preprint
| CXL-ANNS: | Software-Hardware |     | collaborative | mem- |     |     |     |     |     |     |
| --------- | ----------------- | --- | ------------- | ---- | --- | --- | --- | --- | --- | --- |
arXiv:1702.08734,2017.
orydisaggregationandcomputationforBillion-Scale
approximatenearestneighborsearch. In2023USENIX [27] RAPIDSAI. cuVS:alibraryforvectorsearchandclus-
AnnualTechnicalConference(USENIXATC23),pages https://github.com/rapidsai/
teringontheGPU.
| 585–600,Boston,MA,July2023.USENIXAssociation. |     |          |               |      | cuvs,2025. |     |     |     |     |     |
| --------------------------------------------- | --- | -------- | ------------- | ---- | ---------- | --- | --- | --- | --- | --- |
| [19] Zili Zhang,Fangyue                       |     | Liu,Gang | Huang,Xuanzhe | Liu, |            |     |     |     |     |     |
[28] Meituan(thelargestonlinefooddeliverycompanyinthe
| and Xin | Jin. Fast | vector query | processing | for large |     |     |     |     |     |     |
| ------- | --------- | ------------ | ---------- | --------- | --- | --- | --- | --- | --- | --- |
world).Practiceofmeituan’sGPU-basedvectorretrieval
datasetsbeyondGPUmemorywithreorderedpipelining.
|     |     |     |     |     | system. | https://tech.meituan.com/2024/04/11/ |     |     |     |     |
| --- | --- | --- | --- | --- | ------- | ------------------------------------ | --- | --- | --- | --- |
InProceedingsofthe21stUSENIXSymposiumonNet-
gpu-vector-retrieval-system-practice.html,
workedSystemsDesignandImplementation,NSDI’24,
2024.
USA,2024.USENIXAssociation.
[20] KarthikV.,SaimKhan,SomeshSingh,HarshaVardhan [29] Zillizcloudnamedaleaderintheforresterwave.https:
//zilliz.com,2025.
| Simhadri,andJyothiVedurada. |     |     | BANG:Billion-scale |     |     |     |     |     |     |     |
| --------------------------- | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- |
approximatenearestneighborsearchusingasingleGPU.
|     |     |     |     |     | [30] Chuangxian |     | Wei, Bin | Wu, Sheng | Wang, | Renjie Lou, |
| --- | --- | --- | --- | --- | --------------- | --- | -------- | --------- | ----- | ----------- |
arXivpreprintarXiv:2401.11324,2025.
ChaoqunZhan,FeifeiLi,andYuanzheCai.AnalyticDB-
[21] YuntaoGui,PeiqiYin,XiaoYan,ChaoruiZhang,Weixi V:ahybridanalyticalenginetowardsqueryfusionfor
Zhang,andJamesCheng. PilotANN:Memory-bounded structuredandunstructureddata. Proc.VLDBEndow.,
GPU acceleration for vector search. arXiv preprint 13(12):3152–3165,August2020.
arXiv:2503.21206,2025.
|     |     |     |     |     | [31] Jianyang | Gao | andCheng | Long. | RaBitQ: | Quantizing |
| --- | --- | --- | --- | --- | ------------- | --- | -------- | ----- | ------- | ---------- |
[22] BingTian,HaikunLiu,YuhangTang,ShihaiXiao,Zhuo- high-dimensionalvectorswithatheoreticalerrorbound
huiDuan,XiaofeiLiao,HaiJin,XuecangZhang,Jun-
|     |     |     |     |     | forapproximatenearestneighborsearch. |     |     |     |     | Proc. ACM |
| --- | --- | --- | --- | --- | ------------------------------------ | --- | --- | --- | --- | --------- |
huaZhu,andYuZhang. Towardshigh-throughputand Manag.Data,2(3),May2024.
low-latencybillion-scalevectorsearchviaCPU/GPU
| collaborativefilteringandre-ranking. |     |     | InProceedingsof |     |            |        |          |        |              |         |
| ------------------------------------ | --- | --- | --------------- | --- | ---------- | ------ | -------- | ------ | ------------ | ------- |
|                                      |     |     |                 |     | [32] Herve | Jégou, | Matthijs | Douze, | and Cordelia | Schmid. |
the23rdUSENIXConferenceonFileandStorageTech- Productquantizationfornearestneighborsearch. IEEE
nologies,FAST’25,USA,2025.USENIXAssociation.
TransactionsonPatternAnalysisandMachineIntelli-
gence,33(1):117–128,2011.
[23] SukjinKim,SeongyeonPark,SiUngNoh,JungukHong,
| Taehee | Kwon, Hunseong | Lim, | and Jinho | Lee. Path- |                  |     |               |     |             |         |
| ------ | -------------- | ---- | --------- | ---------- | ---------------- | --- | ------------- | --- | ----------- | ------- |
|        |                |      |           |            | [33] NeurIPS’21. |     | Billion-scale |     | approximate | nearest |
Weaver:ahigh-throughputmulti-GPUsystemforgraph-
|                                        |     |     |     |            | neighbor | search | challenge:                      | NeurIPS’21 |     | competi- |
| -------------------------------------- | --- | --- | --- | ---------- | -------- | ------ | ------------------------------- | ---------- | --- | -------- |
| basedapproximatenearestneighborsearch. |     |     |     | InProceed- |          |        |                                 |            |     |          |
|                                        |     |     |     |            | tion     | track. | https://big-ann-benchmarks.com/ |            |     |          |
ingsofthe2025USENIXConferenceonUsenixAnnual
neurips21.html,2021.
TechnicalConference,USENIXATC’25,USA,2025.
USENIXAssociation.
|     |     |     |     |     | [34] ArtemBabenkoYandexandVictorLempitsky. |     |     |     |     | Efficient |
| --- | --- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --------- |
[24] JeffJohnson,MatthijsDouze,andHervéJégou. Faiss: indexingofbillion-scaledatasetsofdeepdescriptors. In
2016IEEEConferenceonComputerVisionandPattern
| A library | for efficient | similarity | search | and clus- |     |     |     |     |     |     |
| --------- | ------------- | ---------- | ------ | --------- | --- | --- | --- | --- | --- | --- |
tering of dense vectors. https://github.com/ Recognition(CVPR),pages2055–2063,2016.
facebookresearch/faiss,2017.
[35] AntonVoronov,DenisKuznedelev,MikhailKhoroshikh,
[25] Jianguo Wang, Xiaomeng Yi, Rentong Guo, Hai Jin, ValentinKhrulkov,andDmitryBaranchuk. Switti:De-
PengXu,ShengjunLi,XiangyuWang,XiangzhouGuo, signingscale-wisetransformersfortext-to-imagesyn-
Chengming Li, Xiaohai Xu, Kun Yu, Yuxing Yuan, thesis. arXivpreprintarXiv:2412.01819,2025.
1578    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

[36] Harsha Vardhan Simhadri, George Williams, Martin 35thInternationalConferenceonNeuralInformation
Aumüller, Matthijs Douze, Artem Babenko, Dmitry Processing Systems,NIPS ’21,Red Hook,NY,USA,
Baranchuk,QiChen,LucasHosseini,RavishankarKr- 2021.CurranAssociatesInc.
| ishnaswamy, | Gopal | Srinivasa, | Suhas | Jayaram | Subra- |     |     |     |     |     |     |     |
| ----------- | ----- | ---------- | ----- | ------- | ------ | --- | --- | --- | --- | --- | --- | --- |
manya,andJingdongWang. ResultsoftheNeurIPS’21 [46] Jason Mohoney, Devesh Sarda, Mengze Tang, Shi-
haburRahmanChowdhury,AnilPacaci,IhabF.Ilyas,
challengeonbillion-scaleapproximatenearestneighbor
|     |     |     |     |     |     | Theodoros |     | Rekatsinas, | and | Shivaram | Venkataraman. |     |
| --- | --- | --- | --- | --- | --- | --------- | --- | ----------- | --- | -------- | ------------- | --- |
search,2022.
|     |     |     |     |     |     | Quake: | adaptive | indexing |     | for vector | search. | In Pro- |
| --- | --- | --- | --- | --- | --- | ------ | -------- | -------- | --- | ---------- | ------- | ------- |
[37] NVIDIA. Nvidia CUDA C++ programming ceedingsofthe19thUSENIXConferenceonOperating
| guide. |     | https://docs.nvidia.com/cuda/ |     |     |     |     |     |     |     |     |     |     |
| ------ | --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
SystemsDesignandImplementation,OSDI’25,USA,
cuda-c-programming-guide/index.html,2025. 2025.USENIXAssociation.
[38] LarsGottesbüren,TobiasHeuer,PeterSanders,Chris- [47] Ruiqi Guo, Philip Sun, Erik Lindgren, Quan Geng,
tian Schulz, and Daniel Seemaier. Deep Multilevel David Simcha, Felix Chern, and Sanjiv Kumar. Ac-
| GraphPartitioning. |     | InPetraMutzel,RasmusPagh,and |     |     |     |     |     |     |     |     |     |     |
| ------------------ | --- | ---------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
celeratinglarge-scaleinferencewithanisotropicvector
GrzegorzHerman,editors,29thAnnualEuropeanSym- quantization. InProceedingsofthe37thInternational
posiumonAlgorithms(ESA2021),volume204ofLeib- ConferenceonMachineLearning,ICML’20.JMLR.org,
| nizInternationalProceedingsinInformatics(LIPIcs), |     |     |     |     |     | 2020. |     |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- |
pages48:1–48:17,Dagstuhl,Germany,2021.Schloss
Dagstuhl–Leibniz-ZentrumfürInformatik. [48] Philip Sun,David Simcha,Dave Dopson,Ruiqi Guo,
|                 |     |               |     |                |     | andSanjivKumar.                 |     |     | SOAR:improvedindexingforap- |     |                 |     |
| --------------- | --- | ------------- | --- | -------------- | --- | ------------------------------- | --- | --- | --------------------------- | --- | --------------- | --- |
| [39] The TEXMEX |     | Project Team. |     | Corpus-TEXMEX: |     |                                 |     |     |                             |     |                 |     |
|                 |     |               |     |                |     | proximatenearestneighborsearch. |     |     |                             |     | InProceedingsof |     |
Datasetsforapproximatenearestneighborsearch.http:
the37thInternationalConferenceonNeuralInforma-
//corpus-texmex.irisa.fr/,2011. tionProcessingSystems,NIPS’23,RedHook,NY,USA,
2023.CurranAssociatesInc.
| [40] ArtemBabenkoYandexandVictorLempitsky.        |     |     |     |     | Efficient |     |     |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
| indexingofbillion-scaledatasetsofdeepdescriptors. |     |     |     |     | In        |     |     |     |     |     |     |     |
[49] YumingXu,HengyuLiang,JinLi,ShuotaoXu,QiChen,
2016IEEEConferenceonComputerVisionandPattern
QianxiZhang,ChengLi,ZiyueYang,FanYang,Yuqing
Recognition(CVPR),pages2055–2063,2016.
|                 |     |           |     |                 |     | Yang,PengCheng,andMaoYang. |          |        |                  |     | SPFresh:Incremen- |     |
| --------------- | --- | --------- | --- | --------------- | --- | -------------------------- | -------- | ------ | ---------------- | --- | ----------------- | --- |
|                 |     |           |     |                 |     | tal                        | in-place | update | forbillion-scale |     | vectorsearch.     | In  |
| [41] Microsoft. |     | SPACEV1B: |     | A billion-scale |     |                            |          |        |                  |     |                   |     |
Proceedingsofthe29thSymposiumonOperatingSys-
| vector dataset |     | for text | descriptors. |     | https: |     |     |     |     |     |     |     |
| -------------- | --- | -------- | ------------ | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
//github.com/microsoft/SPTAG/tree/master/ temsPrinciples,SOSP’23,page545–561,NewYork,
NY,USA,2023.AssociationforComputingMachinery.
datasets/SPACEV1B,2023.
[50] JunjieQi,GergelySzilvasy,MichaelNorris,andVishal
[42] YangXiao,MoSun,ZiyuSong,BingTian,JieZhang,
Jie Sun, and Zeke Wang. Breaking the storage- Gandhi. Accelerating GPU indexes in faiss with
|                        |            |                      |     |       |          | NVIDIAcuVS.   |         | EngineeringatMeta,May2025. |       |         |       |            |
| ---------------------- | ---------- | -------------------- | --- | ----- | -------- | ------------- | ------- | -------------------------- | ----- | ------- | ----- | ---------- |
| compute                | bottleneck | in billion-scale     |     | ANNS: | A GPU-   |               |         |                            |       |         |       |            |
| driven asynchronous    |            | I/O framework.       |     | arXiv | preprint |               |         |                            |       |         |       |            |
|                        |            |                      |     |       |          | [51] Hiroyuki | Ootomo, |                            | Akira | Naruse, | Corey | Nolet, Ray |
| arXiv:2507.10070,2025. |            | Acceptedbythe2026ACM |     |       |          |               |         |                            |       |         |       |            |
|                        |            |                      |     |       |          | Wang,         | Tamas   | Feher,                     | and   | Yong    | Wang. | CAGRA:     |
SIGMOD/PODSConference(SIGMOD2026).
|     |     |     |     |     |     | Highly  | parallel | graph  | construction |       | and   | approximate |
| --- | --- | --- | --- | --- | --- | ------- | -------- | ------ | ------------ | ----- | ----- | ----------- |
|     |     |     |     |     |     | nearest | neighbor | search | for          | GPUs. | arXiv | preprint    |
[43] FabianGroh,LukasRuppert,PatrickWieschollek,and
arXiv:2308.15136,2024.
| HendrikP.A.Lensch. |     | GGNN:Graph-basedGPUnear-   |     |     |     |               |             |     |               |     |        |      |
| ------------------ | --- | -------------------------- | --- | --- | --- | ------------- | ----------- | --- | ------------- | --- | ------ | ---- |
| estneighborsearch. |     | IEEETransactionsonBigData, |     |     |     |               |             |     |               |     |        |      |
|                    |     |                            |     |     |     | [52] Jingrong | Zhang,Akira |     | Naruse,Xipeng |     | Li,and | Yong |
9(1):267–279,2023.
|     |     |     |     |     |     | Wang. | Paralleltop-kalgorithms |     |     | on  | GPU: | A compre- |
| --- | --- | --- | --- | --- | --- | ----- | ----------------------- | --- | --- | --- | ---- | --------- |
[44] AristidesGionis,PiotrIndyk,andRajeevMotwani.Sim- hensivestudyandnewmethods. InProceedingsofthe
ilaritysearchinhighdimensionsviahashing. InPro- InternationalConferenceforHighPerformanceCom-
ceedingsofthe25thInternationalConferenceonVery puting,Networking,StorageandAnalysis,SC’23,New
York,NY,USA,2023.AssociationforComputingMa-
LargeDataBases,VLDB’99,page518–529,SanFran-
| cisco,CA,USA,1999.MorganKaufmannPublishers |     |     |     |     |     | chinery. |     |     |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- |
Inc.
|     |     |     |     |     |     | [53] Qianxi | Zhang,Shuotao |     | Xu,Qi | Chen,Guoxin |     | Sui,Ji- |
| --- | --- | --- | --- | --- | --- | ----------- | ------------- | --- | ----- | ----------- | --- | ------- |
[45] Qi Chen, Bing Zhao, Haidong Wang, Mingqin Li, adong Xie, Zhizhen Cai, Yaoqi Chen, Yinxuan He,
ChuanjieLiu,ZengzhongLi,MaoYang,andJingdong YuqingYang,FanYang,MaoYang,andLidongZhou.
Wang. SPANN: highly-efficient billion-scale approx- VBASE:Unifyingonlinevectorsimilaritysearchand
imate nearestneighborsearch. In Proceedings ofthe relational queries via relaxed monotonicity. In 17th
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1579

USENIXSymposiumonOperatingSystemsDesignand [62] UshaNandiniRaghavan,RékaAlbert,andSoundarKu-
Implementation(OSDI23),pages377–395,Boston,MA, mara. Nearlineartimealgorithmtodetectcommunity
July2023.USENIXAssociation. structuresinlarge-scalenetworks. PhysicalReviewE,
76(3),September2007.
| [54] Wei Dong, | Charikar | Moses, | and Kai | Li. Efficient k- |     |     |     |     |     |
| -------------- | -------- | ------ | ------- | ---------------- | --- | --- | --- | --- | --- |
nearest neighbor graph construction for generic simi- [63] GeorgeKarypisandVipinKumar. Afastandhighqual-
itymultilevelschemeforpartitioningirregulargraphs.
| larity measures. |     | In Proceedings | of  | the 20th Interna- |     |     |     |     |     |
| ---------------- | --- | -------------- | --- | ----------------- | --- | --- | --- | --- | --- |
tionalConferenceonWorldWideWeb,WWW’11,page SIAMJournalonScientificComputing,20(1):359–392,
| 577–586,NewYork,NY,USA,2011.Associationfor |     |     |     |     | 1998. |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | ----- | --- | --- | --- | --- |
ComputingMachinery.
[64] TaeyoonKim,ChanHoPark,MansurMukimbekov,Hee-
[55] ZihanLiu,WentaoNi,JingwenLeng,YuFeng,Cong limHong,MinseokKim,ZeJin,ChangdaeKim,Ji-Yong
|     |     |     |     |     | Shin,andMyeongjaeJeon. |     |     | FusionFlow:Accelerating |     |
| --- | --- | --- | --- | --- | ---------------------- | --- | --- | ----------------------- | --- |
Guo,QuanChen,ChaoLi,MinyiGuo,andYuhaoZhu.
JUNO:Optimizinghigh-dimensionalapproximatenear- datapreprocessingformachinelearningwithCPU-GPU
estneighboursearchwithsparsity-awarealgorithmand cooperation. Proc.VLDBEndow.,17(4):863–876,De-
cember2023.
| ray-tracingcoremapping. |     |     | InProceedingsofthe29th |     |     |     |     |     |     |
| ----------------------- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- |
ACMInternationalConferenceonArchitecturalSupport
|                 |     |           |     |                    | [65] NVIDIA. | NvidiaGDRCopy. |     | https://github.com/ |     |
| --------------- | --- | --------- | --- | ------------------ | ------------ | -------------- | --- | ------------------- | --- |
| for Programming |     | Languages | and | Operating Systems, |              |                |     |                     |     |
NVIDIA/gdrcopy,2025.
Volume2,ASPLOS’24,page549–565,NewYork,NY,
USA,2024.AssociationforComputingMachinery.
|     |     |     |     |     | [66] AMD. | BAR | configuration | for AMD | GPUs. |
| --- | --- | --- | --- | --- | --------- | --- | ------------- | ------- | ----- |
https://rocm.docs.amd.com/en/latest/how-to/
| [56] HaoGuoandYouyouLu. |     |     | OdinANN:Directinsertfor |     |     |     |     |     |     |
| ----------------------- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- |
Bar-Memory.html,2025.
consistentlystableperformanceinbillion-scalegraph-
| basedvectorsearch. |     | In  | 24thUSENIX | Conference on |     |     |     |     |     |
| ------------------ | --- | --- | ---------- | ------------- | --- | --- | --- | --- | --- |
[67] JingkaiHe,YunpengDong,DongDu,MoZou,Zhitai
FileandStorageTechnologies(FAST26),SantaClara, Yu,YuxinRen,NingJia,YubinXia,andHaiboChen.
CA,2026.USENIXAssociation.
Howtocopymemory?coordinatedasynchronouscopy
|     |     |     |     |     | asafirst-classOSservice. |     |     | InProceedingsoftheACM |     |
| --- | --- | --- | --- | --- | ------------------------ | --- | --- | --------------------- | --- |
[57] XiZhao,YaoTian,KaiHuang,BolongZheng,andXiao-
SIGOPS31stSymposiumonOperatingSystemsPrinci-
| fangZhou. | Towardsefficientindexconstructionandap- |     |     |     |     |     |     |     |     |
| --------- | --------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
ples,SOSP’25,page1062–1081,NewYork,NY,USA,
proximatenearestneighborsearchinhigh-dimensional
2025.AssociationforComputingMachinery.
| spaces. | Proc.VLDBEndow.,16(8):1979–1991,April |     |     |     |                                                  |     |     |     |     |
| ------- | ------------------------------------- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- |
| 2023.   |                                       |     |     |     | [68] ZhengWang,AnnaCai,XinfengXie,ZaifengPan,Yue |     |     |     |     |
Guan,WeiweiChu,JieWang,ShikaiLi,JianyuHuang,
| [58] CongFu,ChangxuWang,andDengCai. |     |     |     | Highdimen- |                                  |     |     |          |     |
| ----------------------------------- | --- | --- | --- | ---------- | -------------------------------- | --- | --- | -------- | --- |
|                                     |     |     |     |            | ChrisCai,YuchenHao,andYufeiDing. |     |     | WLB-LLM: |     |
sionalsimilaritysearchwithsatellitesystemgraph:Effi- Workload-balanced4Dparallelismforlargelanguage
ciency,scalability,andunindexedquerycompatibility.
|                   |     |            |          |             | modeltraining. |     | In19thUSENIXSymposiumonOper- |     |     |
| ----------------- | --- | ---------- | -------- | ----------- | -------------- | --- | ---------------------------- | --- | --- |
| IEEE Transactions |     | on Pattern | Analysis | and Machine |                |     |                              |     |     |
atingSystemsDesignandImplementation(OSDI25),
Intelligence,44(8):4139–4150,2022. pages785–801,Boston,MA,USA,July2025.USENIX
Association.
[59] ShuoYang,JiadongXie,YingfanLiu,JeffreyXuYu,
XiyueGao,QianruWang,YanguoPeng,andJiangtao [69] Yeonhong Park,Jake Hyun,Hojoon Kim,and Jae W.
Cui. Revisiting the index construction of proximity Lee.DecDEC:Asystemsapproachtoadvancinglow-bit
graph-basedapproximatenearestneighborsearch. Proc.
|     |     |     |     |     | LLMquantization. |     | In19thUSENIXSymposiumonOp- |     |     |
| --- | --- | --- | --- | --- | ---------------- | --- | -------------------------- | --- | --- |
VLDBEndow.,18(6):1825–1838,February2025. eratingSystemsDesignandImplementation(OSDI25),
pages803–819,Boston,MA,USA,July2025.USENIX
| [60] LaurentHyafilandRonaldL.Rivest. |     |     |     | Graphpartitioning |     |     |     |     |     |
| ------------------------------------ | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- |
Association.
andconstructingoptimaldecisiontreesarepolynomial
completeproblems. RapportdeRecherche33,IRIA– [70] Shiwei Gao,Qing Wang,Shaoxun Zeng,Youyou Lu,
LaboratoiredeRechercheenInformatiqueetAutoma- and Jiwu Shu. Weaver: Efficient multi-LLM serving
| tique,1973.                                 |     |     |     |      | withattentionoffloading. |            | In2025USENIXAnnualTech- |               |          |
| ------------------------------------------- | --- | --- | --- | ---- | ------------------------ | ---------- | ----------------------- | ------------- | -------- |
|                                             |     |     |     |      | nical                    | Conference | (USENIX                 | ATC 25),pages | 587–595, |
| [61] M.R.Garey,D.S.Johnson,andL.Stockmeyer. |     |     |     | Some |                          |            |                         |               |          |
Boston,MA,USA,July2025.USENIXAssociation.
| simplifiedNP-completeproblems. |     |     |     | In Proceedingsof |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- |
theSixthAnnualACMSymposiumonTheoryofCom- [71] JamesD.Evans. Straightforwardstatisticsforthebe-
puting,STOC’74,page47–63,NewYork,NY,USA, havioralsciences. Brooks/ColePublishingCompany,
1974.AssociationforComputingMachinery. PacificGrove,Calif.,1996.
1580    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

[72] NationalLibraryofMedicine. Asaruleofthumb,cor- [82] MicrosoftCorporation. NDmA100v4-series–Azure
relationcoefficientsgreaterthan0.7orlessthan-0.7are Virtual Machines. https://learn.microsoft.
https://www.nlm.nih.gov/oet/ com/en-us/azure/virtual-machines/sizes/
consideredstrong.
ed/stats/02-300.html,2025. gpu-accelerated/ndma100v4-series?tabs=
sizebasic,2025.
[73] ChaojiZuo,MiaoQiao,WenchaoZhou,FeifeiLi,and
DongDeng.SeRF:Segmentgraphforrange-filteringap-
[83] PhilipAdams,MenghaoLi,ShiZhang,LiTan,QiChen,
proximatenearestneighborsearch. Proc.ACMManag. Mingqin Li, Zengzhong Li, Knut Risvik, and Har-
Data,2(1),March2024. shaVardhanSimhadri. Distributedann:Efficientscaling
ofasinglediskanngraphacrossthousandsofcomputers,
| [74] NVIDIA | Developer. |     | CUDA | GPU | Compute | Capabil- |     |     |     |     |     |
| ----------- | ---------- | --- | ---- | --- | ------- | -------- | --- | --- | --- | --- | --- |
2025.
| ity. | https://developer.nvidia.com/cuda-gpus, |     |     |     |     |     |     |     |     |     |     |
| ---- | --------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2025.
[84] YumingXu,QianxiZhang,QiChen,BaotongLu,Meng-
haoLi,PhilipAdams,MingqinLi,ZengzhongLi,Jing
[75] KarthikBharathy,ShasankChavan,IkroopDhillon,and
|             |     |                                      |     |     |     |     | Liu,ChengLi,andFanYang. |     | Scalabledistributedvec- |     |     |
| ----------- | --- | ------------------------------------ | --- | --- | --- | --- | ----------------------- | --- | ----------------------- | --- | --- |
| ManasSingh. |     | Oracleaidatabase+nvidiacollaboration |     |     |     |     |                         |     |                         |     |     |
torsearchviaaccuracypreservingindexconstruction,
advancesenterpriseaiatnvidiagtc2026,March2026.
2025.
Accessed:2026-04-15.
|               |           |        |         |          |        |             | [85] Weijie | Zhao,Shulong | Tan,and        | Ping Li. | SONG: Ap- |
| ------------- | --------- | ------ | ------- | -------- | ------ | ----------- | ----------- | ------------ | -------------- | -------- | --------- |
| [76] Mengzhao | Wang,     | Weizhi | Xu,     | Xiaomeng |        | Yi, Songlin |             |              |                |          |           |
|               |           |        |         |          |        |             | proximate   | nearest      | neighborsearch | on GPU.  | In 2020   |
| Wu,           | Zhangyang | Peng,  | Xiangyu | Ke,      | Yunjun | Gao, Xi-    |             |              |                |          |           |
IEEE36thInternationalConferenceonDataEngineer-
| aoliangXu,RentongGuo,andCharlesXie. |     |     |     |     |     | Starling: |     |     |     |     |     |
| ----------------------------------- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- |
ing(ICDE),pages1033–1044,2020.
AnI/O-efficientdisk-residentgraphindexframework
| forhigh-dimensional |     |     | vectorsimilarity |     | search | on data |     |     |     |     |     |
| ------------------- | --- | --- | ---------------- | --- | ------ | ------- | --- | --- | --- | --- | --- |
[86] YuanhangYu,DongWen,YingZhang,LuQin,Wenjie
| segment. | Proc.ACMManag.Data,2(1),March2024. |     |     |     |     |     |                 |     |                               |     |     |
| -------- | ---------------------------------- | --- | --- | --- | --- | --- | --------------- | --- | ----------------------------- | --- | --- |
|          |                                    |     |     |     |     |     | Zhang,andXuemin |     | Lin. GPU-acceleratedproximity |     |     |
graphapproximatenearestneighborsearchandconstruc-
[77] JiongkangNi,XiaoliangXu,YuxiangWang,CanLi,Jia-
|                                    |     |     |     |     |            |     | tion. | In2022IEEE38thInternationalConferenceon |     |     |     |
| ---------------------------------- | --- | --- | --- | --- | ---------- | --- | ----- | --------------------------------------- | --- | --- | --- |
| jieYao,ShihaiXiao,andXuecangZhang. |     |     |     |     | DiskANN++: |     |       |                                         |     |     |     |
DataEngineering(ICDE),pages552–564,2022.
| Efficient                                    | page-based | search |     | over isomorphic |     | mapped |     |     |     |     |     |
| -------------------------------------------- | ---------- | ------ | --- | --------------- | --- | ------ | --- | --- | --- | --- | --- |
| graphindexusingquery-sensitivityentryvertex. |            |        |     |                 |     | arXiv  |     |     |     |     |     |
[87] MagdalenDobsonManohar,ZheqiShen,GuyBlelloch,
preprintarXiv:2310.00402,2023.
LaxmanDhulipala,YanGu,HarshaVardhanSimhadri,
[78] Joobo Shim, Jaewon Oh, Hongchan Roh, Jaeyoung andYihanSun. ParlayANN:Scalableanddeterminis-
ticparallelgraph-basedapproximatenearestneighbor
| Do,       | and Sang-Won |        | Lee.  | Turbocharging |      | vector  |                   |     |                               |     |     |
| --------- | ------------ | ------ | ----- | ------------- | ---- | ------- | ----------------- | --- | ----------------------------- | --- | --- |
|           |              |        |       |               |      |         | searchalgorithms. |     | InProceedingsofthe29thACMSIG- |     |     |
| databases | using        | modern | SSDs. | Proc.         | VLDB | Endow., |                   |     |                               |     |     |
18(11):4710–4722,July2025. PLANAnnualSymposiumonPrinciplesandPractice
|     |     |     |     |     |     |     | of  | Parallel Programming,PPoPP |     | ’24,page | 270–285, |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------- | --- | -------- | -------- |
[79] ZaidQureshi,VikramSharmaMailthody,IsaacGelado, NewYork,NY,USA,2024.AssociationforComputing
| SeungwonMin,AmnaMasood,JeongminPark,Jinjun |     |     |     |     |     |     | Machinery. |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- |
Xiong,C.J.Newburn,DmitriVainbrand,I-HsinChung,
|         |          |         |        |     |         |      | [88] Zhen | Peng,Minjia | Zhang,Kai | Li,Ruoming | Jin,and |
| ------- | -------- | ------- | ------ | --- | ------- | ---- | --------- | ----------- | --------- | ---------- | ------- |
| Michael | Garland, | William | Dally, | and | Wen-mei | Hwu. |           |             |           |            |         |
GPU-initiatedon-demandhigh-throughputstorageac- BinRen. iQAN:Fastandaccuratevectorsearchwith
cessin theBaMsystem architecture. In Proceedings efficientintra-queryparallelismonmulti-corearchitec-
tures.InProceedingsofthe28thACMSIGPLANAnnual
ofthe28thACMInternationalConferenceonArchitec-
turalSupportforProgrammingLanguagesandOperat- SymposiumonPrinciplesandPracticeofParallelPro-
ingSystems,Volume2,ASPLOS2023,page325–339, gramming,PPoPP’23,page313–328,NewYork,NY,
NewYork,NY,USA,2023.AssociationforComputing USA,2023.AssociationforComputingMachinery.
Machinery.
[89] ZiqiYin,JianyangGao,PasqualeBalsebre,GaoCong,
[80] NVIDIA Corporation. NVIDIA DGX A100 andChengLong. DEG:Efficienthybridvectorsearch
Datasheet. https://www.nvidia.com/ usingthedynamicedgenavigationgraph. Proc.ACM
content/dam/en-zz/Solutions/Data-Center/ Manag.Data,3(1),February2025.
nvidia-dgx-a100-datasheet.pdf,2020.
|     |     |     |     |     |     |     | [90] ZengyangGong,YuxiangZeng,andLeiChen. |     |     |     | Accel- |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------------- | --- | --- | --- | ------ |
[81] AmazonWebServices,Inc.AmazonEC2P4dInstances. eratingapproximatenearestneighborsearchinhierar-
https://aws.amazon.com/ec2/instance-types/ chicalgraphs:Efficientlevelnavigationwithshortcuts.
| p4/,2025. |     |     |     |     |     |     | Proc.VLDBEndow.,18(10):3518–3530,June2025. |     |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- |
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1581

[91] BenjaminColeman,SantiagoSegarra,AlexSmola,and In Proceedings of the 2020 ACM SIGMOD Interna-
Anshumali Shrivastava. Graph reordering for cache- tionalConferenceonManagementofData,SIGMOD
efficient nearneighborsearch. In Proceedings of the ’20,page2539–2554,NewYork,NY,USA,2020.Asso-
36thInternationalConferenceonNeuralInformation ciationforComputingMachinery.
Processing Systems,NIPS ’22,Red Hook,NY,USA,
[96] Vo Ngoc Anh,Owen de Kretser,and Alistair Moffat.
2022.CurranAssociatesInc.
Vector-spacerankingwitheffectiveearlytermination.
[92] LarsGottesbüren,LaxmanDhulipala,RajeshJayaram,
InProceedingsofthe24thAnnualInternationalACM
SIGIRConferenceonResearchandDevelopmentinIn-
and Jakub Ła˛cki. Unleashing graph partitioning for
large-scale nearestneighborsearch. Proc. VLDB En- formationRetrieval,SIGIR’01,page35–42,NewYork,
dow.,18(6):1649–1662,February2025. NY,USA,2001.AssociationforComputingMachinery.
[97] ZiliZhang,ChaoJin,LinpengTang,XuanzheLiu,and
[93] JianyangGao,YutongGou,YuexuanXu,YongyiYang,
XinJin. Fast,approximatevectorqueriesonverylarge
Cheng Long, and Raymond Chi-Wing Wong. Prac-
unstructureddatasets. In20thUSENIXSymposiumon
ticalandasymptoticallyoptimalquantizationofhigh-
NetworkedSystemsDesignandImplementation(NSDI
dimensionalvectorsineuclideanspaceforapproximate
23),pages995–1011,Boston,MA,April2023.USENIX
nearestneighborsearch. Proc.ACMManag.Data,3(3),
Association.
June2025.
[98] ManosChatzakis,YannisPapakonstantinou,andThemis
[94] ZimingYuan,LeiDai,WenLi,JieZhang,Shengwen Palpanas. DARTH:Declarativerecallthroughearlyter-
Liang,YingWang,ChengLiu,HuaweiLi,XiaoweiLi, minationforapproximatenearestneighborsearch. Proc.
JiafengGuo,PengWang,RenhaiChen,andGongZhang. ACMManag.Data,3(4),September2025.
NeuVSA:Aunifiedandefficientacceleratorforneural
vectorsearch. In2025IEEEInternationalSymposium [99] MinjiaZhang,WenhanWang,andYuxiongHe. GraSP:
onHighPerformanceComputerArchitecture(HPCA), Optimizinggraph-basednearestneighborsearchwith
pages790–805,2025. subgraphsamplingandpruning. InProceedingsofthe
FifteenthACMInternationalConferenceonWebSearch
[95] Conglong Li,Minjia Zhang,David G. Andersen,and andDataMining,WSDM’22,page1395–1405,New
Yuxiong He. Improving approximate nearest neigh- York,NY,USA,2022.AssociationforComputingMa-
borsearchthroughlearnedadaptiveearlytermination. chinery.
1582 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

delayδ,sincev∗isoptimal(oneofthetruetop-k)andL
A ProofofCorrectnessandConvergence
issufficient,itholdsthat:
Weprovideatheoreticalanalysisregarding:(1)Searchcor-
Dist(q,v∗)<d
rectness,provingthattheasynchronousfetchingstrategydoes L (t+δ) (1)
notcompromisetheterminationandaccuracyofthebest-first
search;(2)Convergencespeedlowerbound,provingthat ThisinequalityholdsbecauseasufficientbudgetLen-
suresthatthequeueisnotfilledwithLcandidatesstrictly
theworst-casesearchstepsarestrictlybounded,ensuringthe
system efficiently converges to the target; and (3) Search betterthanatruetop-kneighbor(bydefinitionoftop-k).
| budgetbound,provingthattherequiredcandidatepoolsize |     |     |     |     |     |     |            | v∗              |          |        |              |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---------- | --------------- | -------- | ------ | ------------ |
|                                                     |     |     |     |     |     |     | Therefore, | is successfully | inserted | into C | t+δ and cor- |
toguaranteeaccuracyremainswithinpracticallimits.
rectlysorted.Thedelayδonlyshiftsthemomentofinsertion
butdoesnotpreventthenodefromdisplacingasuboptimal
A.1 SearchCorrectness candidate.Thus,underthesufficientbudgetassumption,the
|     |     |     |     |     |     |     | finalsetR | retainsthesametop-kaccuracyasthestrictsyn- |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------------------------------------------ | --- | --- | --- |
Thecoreconcerniswhetherdeferringthediscoveryofhost-
chronousexecution.
sideneighborspreventsthealgorithmfromfindingthetrue
nearestneighbors.Wemodelthesearchprocessasatraversal
A.2 BoundofSearchConvergenceSpeed
onaconnectedgraphG=(V,E).
WhileTheorem1establishestheconvergencetotop-kneigh-
| Lemma1(LosslessCandidateAvailability). |     |     |     |     |     | InFlowANN, |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- |
borsundertheassumptionofasufficientsearchbudget,itis
| for any | node | u visited | at step t, | its full | neighbor | set N(u) |     |     |     |     |     |
| ------- | ---- | --------- | ---------- | -------- | -------- | -------- | --- | --- | --- | --- | --- |
imperativetoensurethatthisrequiredbudgetremainswithin
| is eventually | added | to  | the candidate | pool | Q.  | Let N(u)= |     |     |     |     |     |
| ------------- | ----- | --- | ------------- | ---- | --- | --------- | --- | --- | --- | --- | --- |
practicallimits.Ifasynchronousfetchlatencyweretocause
| N (u)∪N |      | (u). |     |     |     |     |     |     |     |     |     |
| ------- | ---- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPU     | Host |      |     |     |     |     |     |     |     |     |     |
thesearchpathtodeviateindefinitely,thesystemwouldre-
• N (u)isaddedtoQ atstept. quireanunrealisticallylargebudgettoavoidprematuretermi-
GPU
nation.Therefore,tovalidatethepracticalityofthesufficient
| • N  | (u)isaddedtoQ |     | atstept+δ,whereδrepresents |     |     |     |                                                     |     |     |     |     |
| ---- | ------------- | --- | -------------------------- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- |
| Host |               |     |                            |     |     |     | budgetassumption,wemustprovethattheadditionalsearch |     |     |     |     |
theasynchronousfetchlatency(insteps).
costinducedbyasynchronousfetchingisstrictlybounded.
Since δ is finite (δ<∞),no candidate is permanently dis- Weassumethegoalistolimitthe“detour”causedbythe
|     |     |     |     |     |     |     | asynchronous | fetch latency, | and we define | the | search effi- |
| --- | --- | --- | --- | --- | --- | --- | ------------ | -------------- | ------------- | --- | ------------ |
carded.
ciencybyboundingthetotaltraversalsteps.
| Theorem1(Top-kConvergenceConsistency). |     |     |     |     | Givenamono- |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- |
tonicdistancemeasureandaconnectedgraph,foranyquery
Definitions:
| q,the deferred |     | discovery | mechanism | ensures |     | that the final |     |     |     |     |     |
| -------------- | --- | --------- | --------- | ------- | --- | -------------- | --- | --- | --- | --- | --- |
candidatesetR convergestothesamesetoftop-k nearest • Let P base be the search path of the strict synchronous
neighborsasthesynchronousbaseline(i.e.,theoriginalbest- baseline(best-firstsearch).Let|P |=T.
base
firstsearch),providedthatthesearchbudgetissufficient.
|     |     |     |     |     |     |     | • LetP | bethesearchpathofFlowANN. |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | ------------------------- | --- | --- | --- |
sys
| Proof. LetC | denotethecandidatepoolatstept,maintaining |     |     |     |     |     |         |                 |               |            |          |
| ----------- | ----------------------------------------- | --- | --- | --- | --- | --- | ------- | --------------- | ------------- | ---------- | -------- |
|             | t                                         |     |     |     |     |     | • Let τ | be the constant | fetch latency | (in steps) | forhost- |
thebestcandidatesfoundsofar,sortedbydistancetoq.The
residentedges.
| capacityofC | t   | isboundedbythesearchbudgetL(L≥k).Let |     |     |     |     |     |     |     |     |     |
| ----------- | --- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
d (t) be the distance of the worst candidate in C (i.e.,the • Let W(e) be the discovery-expansion window for an
| L                 |     |               |     |        |     | t   |                                                 |     |     |     |     |
| ----------------- | --- | ------------- | --- | ------ | --- | --- | ----------------------------------------------- | --- | --- | --- | --- |
| L-thnearest).If|C |     | |<L,wedefined |     | (t)=∞. |     |     |                                                 |     |     |     |     |
|                   |     | t             |     | L      |     |     | edgee=(u,v)inthebest-firstsearch,definedasW(e)= |     |     |     |     |
In the synchronous baseline, a node v is added to C if step (v)−step (u).
|             |     |      |     |     |     |     | expand |     | discover |     |     |
| ----------- | --- | ---- | --- | --- | --- | --- | ------ | --- | -------- | --- | --- |
| Dist(q,v)<d |     | (t). |     |     |     |     |        |     |          |     |     |
L
InFlowANN,considerapotentialtop-kneighborv∗ Theorem2(BoundedStepDeviation). Thenumberofsteps
resid-
|     |     |     |     |     |     |     | inFlowANN,denotedas|P |     | |,isboundedby: |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------- | --- | -------------- | --- | --- |
ing on the hostside. Due to the fetchlatency,v∗ arrives at sys
stept+δinsteadoft.
K
|                                       |     |     |     |     |     |             |     | |P |≤T+∑max(0,τ−W(e)) |     |     | (2) |
| ------------------------------------- | --- | --- | --- | --- | --- | ----------- | --- | --------------------- | --- | --- | --- |
| • Persistenceofentrycondition:Sincev∗ |     |     |     |     |     | isatruetop- |     | sys                   |     | i   |     |
i=1
k neighbor(oranodeonthepathtoone),itsdistance
Dist(q,v∗)isinherentlysmall. where{e ,...,e }denotesthesetofK offloadededges(i.e.,
|             |     |        |         |         |           |         | 1                                          | K   |     |     |        |
| ----------- | --- | ------ | ------- | ------- | --------- | ------- | ------------------------------------------ | --- | --- | --- | ------ |
|             |     |        |         |         |           |         | neighbors)encounteredalongthecriticalpathP |     |     |     | base . |
| • Insertion |     | logic: | When v∗ | becomes | available | at t+δ, |                                            |     |     |     |        |
provided that the search budget is sufficient (i.e.,L is Proof. ConsideracriticalnodevontheoptimalpathP base
largeenough),thesystemcomparesv∗ againstthecur- reachedviaedgee=(u,v).Weanalyzetheimpactoffetching
| rentstateC |     | .Evenifthepoolhasevolvedduringthe |     |     |     |     | latencyinthreecases: |     |     |     |     |
| ---------- | --- | --------------------------------- | --- | --- | --- | --- | -------------------- | --- | --- | --- | --- |
t+δ
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1583

Case1:e∈E (CachedEdge).Thenodevisavailable A.3 BoundofSearchBudget
GPU
immediatelyatstept.Nodelayisintroduced.Thedeviation
WhilethestepboundestablishedinEquation(2)guarantees
∆=0.
timeefficiency,itisequallycriticaltoverifythesearchbud-
| Case2:e∈E |     | andW(e)≥τ(SuccessfulPrediction). |     |     |     |     |     |     |     |     |     |     |     |     |
| --------- | --- | -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Host getconstraints(i.e.,candidatepoolcapacity).Apotentialrisk
| Node u is | expandedatstept,andthe |     |     | fetchrequestforv |     |     | is  |     |     |     |     |     |     |     |
| --------- | ---------------------- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
introducedbydeferreddiscoveryiscandidateoverflow:the
issued.Duetothewindowproperty,thebaselinealgorithm
intermediatenodesvisitedduringthewaitingperiodmight
| wouldnothavepopped(expanded)vfromQ |     |     |     |     | untilstept′= |     |     |     |     |     |     |     |     |     |
| ---------------------------------- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
populatethecandidatepoolwithnumeroussuboptimalcan-
| t+W(e). | In FlowANN,v |     | arrives | at Q | at step | t+τ. | Since |     |     |     |     |     |     |     |
| ------- | ------------ | --- | ------- | ---- | ------- | ---- | ----- | --- | --- | --- | --- | --- | --- | --- |
didates.Toruleoutthispossibility,weexplicitlyderivethe
| τ≤W(e), | it follows | that | t+τ≤t′. | Thus, | v arrives |     | before |     |     |     |     |     |     |     |
| ------- | ---------- | ---- | ------- | ----- | --------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
upperboundoftherequiredcandidatepoolsize.
| or exactly | when | it is | needed by | the best-first |     | search. | The |     |     |     |     |     |     |     |
| ---------- | ---- | ----- | --------- | -------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
availabilityofvmatchesthebaseline’srequirement,so∆=0. Theorem 3 (Bounded Candidate Pool Size). LetU be
base
Case3:e∈E Host andW(e)<τ(PredictionMiss).This the worst-case upper bound of the candidate pool size for
istheonlyscenariocausingadetour.Thealgorithmneedsv the synchronous baseline. The worst-case candidate pool
atstept+W(e),butvarrivesatt+τ.Thesystemisforcedto capacityU requiredbyFlowANNisboundedby:
sys
| discoversuboptimalnodesforadurationof∆ |     |     |     |     |     | =τ−W(e). |     |     |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
step
Oncetheτstepspass,ventersQ andcorrectsthepath. U ≤U ·(1+τ) (5)
sys base
Conclusion:Thetotalextracostisthesumofthese“wait-
whereτisthelatencyfactordefinedinTheorem2.
inggaps”(τ−W(e)).Sincethefetchlatencyτiseffectively
overlappedwithcomputationinmoststeps(Cases1and2), Proof. The maximum number of candidates stored in the
andthecandidatepoolensuresautomaticpathcorrection,the
poolisdeterminedbythenumberofexpandednodesandthe
searchcomplexityofFlowANNremainslinearO(T),provid-
maximumgraphdegree.Forthesynchronousbaseline,which
ingaguaranteedlowerboundonconvergencespeedcompa- executesT steps(whereT =|P |),theworst-casepoolsize
base
rabletothesynchronousbaseline.
isboundedbythecumulativenumberofaddedneighbors:
|                                                    |            |     |           |     |        |             |     |        |                                         |     | U ≈T·D |     |     | (6) |
| -------------------------------------------------- | ---------- | --- | --------- | --- | ------ | ----------- | --- | ------ | --------------------------------------- | --- | ------ | --- | --- | --- |
|                                                    |            |     |           |     |        |             |     |        |                                         |     | base   | max |     |     |
| Quantitative                                       | Worst-Case |     | Analysis: |     | We now | instantiate |     |        |                                         |     |        |     |     |     |
|                                                    |            |     |           |     |        |             |     | whereD | representsthemaximumnodedegreeingraphG. |     |        |     |     |     |
| theboundtodemonstratethelimitsofsearchexpansionun- |            |     |           |     |        |             |     |        | max                                     |     |        |     |     |     |
derextremeconditions.Weassumeacatastrophicscenario ForFlowANN,Theorem2provesthatthesearchprocess
wheretwoworst-caseconditionsoccursimultaneously:(1) expandsatmostT(1+τ)nodesintheworstcasetorecover
Zerocachehit,implyingthateverynodeonthesearchpath the optimal path. Since the node expansion logic remains
residesonthehostandrequiresafetchoperation(i.e.,K=T); identical (adding neighbors of visited nodes),the required
and(2)Zerodiscovery-expansionwindow,wherewindow poolcapacityscaleslinearlywiththemaximumnumberof
| prediction | fails | completely | forevery | step,meaning |     | data | is  | visitedsteps: |     |     |     |     |     |     |
| ---------- | ----- | ---------- | -------- | ------------ | --- | ---- | --- | ------------- | --- | --- | --- | --- | --- | --- |
neededimmediately(i.e.,W(e)≈0foralli).
i
|                                   |     |     |     |     |                 |     |     |     |     | U   | ≤[T·(1+τ)]·D |     |     | (7) |
| --------------------------------- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- |
| Substitutingtheseconditions(K=T,W |     |     |     |     | =0)intoEquation |     |     |     |     | sys |              |     | max |     |
(2),weobtainthegeneralupperbound:
|     |     |     |     |     |     |     |     | By  | rearranging | the | terms, | we can express | the bound | of  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ------ | -------------- | --------- | --- |
FlowANNintermsofthebaseline’sbound:
T
| |P | | ≤T+∑(τ−0)=T+T·τ=T(1+τ) |     |     |     |     |     | (3) |     |     |       |           |     |       |     |
| ---- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | --------- | --- | ----- | --- |
| sys  | worst                  |     |     |     |     |     |     |     | U   | ≤(T·D | )·(1+τ)=U |     | (1+τ) | (8) |
|      |                        | i=1 |     |     |     |     |     |     | sys |       | max       |     | base  |     |
Conclusion:Thisresultprovesthatthespacecomplexity
Inpractice,xCopier’sasynchronousfetchlatencyis~8µs
|     |     |     |     |     |     |     |     | of FlowANN |     | (i.e., required |     | search budget) | remains | in the |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --------------- | --- | -------------- | ------- | ------ |
(Figure19,Section7.3),whichdoesnotexceedtheduration
oftwosearchsteps(6–14µsperstep,Section3).Therefore, same orderofmagnitude as the baseline. Given thatτ≈2
inoursystem,amodestlinearincreaseinthecandidatepool
wesetthelatencypenaltyτ≈2steps.Substitutingthisinto
capacityissufficienttopreventvalidcandidatesfrombeing
thegeneralformulayields:
evicted,ensuringhighrecallwithoutunboundedmemorycon-
sumption.
|     |     | |P | | ≤T(1+2)=3T |     |     |     | (4) |     |     |     |     |     |     |     |
| --- | --- | ---- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
sys worst
| This derivation   |     | explicitly     | quantifies |     | that even | in the    | ab- |     |     |     |     |     |     |     |
| ----------------- | --- | -------------- | ---------- | --- | --------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
| solute worst-case |     | scenario—where |            | no  | caching   | or window |     |     |     |     |     |     |     |     |
optimizationworks—thesearchcomplexityremainsstrictly
linear(O(T)),boundedbyasmallconstantfactorofthebase-
linesteps.
1584    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association