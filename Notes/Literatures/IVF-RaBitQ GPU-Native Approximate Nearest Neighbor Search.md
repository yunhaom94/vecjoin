|     | GPU-Native |          |             | Approximate |      | Nearest     |       | Neighbor |            | Search |          | with |     |
| --- | ---------- | -------- | ----------- | ----------- | ---- | ----------- | ----- | -------- | ---------- | ------ | -------- | ---- | --- |
|     |            |          | IVF-RaBitQ: |             | Fast | Index       | Build |          | and Search |        |          |      |     |
|     |            | JifanShi |             |             |      | JianyangGao |       |          |            |        | JamesXia |      |     |
NanyangTechnologicalUniversity NanyangTechnologicalUniversity NVIDIA
|     |     | Singapore |     |     |     | Singapore |     |     |     |     | USA |     |     |
| --- | --- | --------- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
jifan002@e.ntu.edu.sg gaoj0017@e.ntu.edu.sg jamxia@nvidia.com
|     |     |     |     | TamásBélaFehér |     |     |                                | ChengLong |           |     |     |     |     |
| --- | --- | --- | --- | -------------- | --- | --- | ------------------------------ | --------- | --------- | --- | --- | --- | --- |
|     |     |     |     | NVIDIA         |     |     | NanyangTechnologicalUniversity |           |           |     |     |     |     |
|     |     |     |     | Germany        |     |     |                                |           | Singapore |     |     |     |     |
6202 beF 72  ]BD.sc[  1v99932.2062:viXra
|          |     |     |     | tfeher@nvidia.com |     |     |                                                    | c.long@ntu.edu.sg |     |     |     |     |     |
| -------- | --- | --- | --- | ----------------- | --- | --- | -------------------------------------------------- | ----------------- | --- | --- | --- | --- | --- |
| ABSTRACT |     |     |     |                   |     |     | AvarietyofANNSsolutionshavebeenproposed,amongwhich |                   |     |     |     |     |     |
graph-basedmethodsandcluster-basedmethodsaremostcom-
Approximatenearestneighborsearch(ANNS)onGPUsisgaining
increasingpopularityformodernretrievalandrecommendation monlyusedinindustrialsystems.Graph-basedmethodsusually
workloads that operate over massive high-dimensional vectors. constructproximitygraphsoverdatapointsandperformgreedy
Graph-basedindexesdeliverhighrecallandthroughputbutin- traversaltolocatenearestneighbors.Representativealgorithms,
suchasHNSW[36],NSG[15],andVamanagraph[23],areknown
curheavybuild-timeandstoragecosts.Incontrast,cluster-based
fortheircompetitiverecall-performancetrade-offs.Cluster-based
methodsbuildandscaleefficientlyyetoftenneedmanyprobesfor
|     |     |     |     |     |     |     | methods, | most | notably inverted-file |     | (IVF) | indices, partition | the |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---- | --------------------- | --- | ----- | ------------------ | --- |
highrecall,strainingmemorybandwidthandcompute.Aimingto
simultaneouslyachievefastindexbuild,high-throughputsearch, vectorspaceintocoarseclustersandrestrictsearchtoasubsetof
high recall, and low storage requirement for GPUs, we present clusters.Thesemethodsoffersimpledataorganizationandefficient
indexconstruction,whichenableeasyintegrationwithexisting
IVF-RaBitQ(GPU),aGPU-nativeANNSsolutionthatintegrates
databasesystems.Furthermore,bothtypesofmethodsareoftenen-
thecluster-basedmethodIVFwithRaBitQquantizationintoaneffi-
hancedbyleveragingvectorquantizationforreducingthecostsof
cientGPUindexbuild/searchpipeline.Specifically,forindexbuild,
we develop a scalable GPU-native RaBitQ quantization method storingandaccessingrawvectorsand/orthecostsofcomputingdis-
thatenablesfastandaccuratelow-bitencodingatscale.Forsearch, tancesamongrawvectors[1,16,20,23,28].Mostofthesesolutions
wereoriginallydevelopedandoptimizedforCPUarchitectures.
wedevelopGPU-nativedistancecomputationschemesforRaBitQ
Asdatascaleandqueryvolumecontinuetogrow,manyreal-
codesandafusedsearchkerneltoachievehighthroughputwith
worldANNSdeploymentschoosetouseGPUsastheiraccelera-
highrecall.WithIVF-RaBitQimplementedandintegratedintothe
NVIDIAcuVSLibrary,experimentsoncuVSBenchacrossmultiple tors due to GPUs’ massive parallelism and high memory band-
datasetsshowthatIVF-RaBitQoffersastrongperformancefron- width. For instance, Faiss has deployed GPU-based ANNS li-
|     |     |     |     |     |     |     | brary | cuVS to | handle large-scale |     | batched | queries offline | 1. Ex- |
| --- | --- | --- | --- | --- | --- | --- | ----- | ------- | ------------------ | --- | ------- | --------------- | ------ |
tierinrecall,throughput,indexbuildtime,andstoragefootprint.
|     |     |     |     |     |     |     | isting | GPU-based | ANNS | methods | largely | follow the same | two |
| --- | --- | --- | --- | --- | --- | --- | ------ | --------- | ---- | ------- | ------- | --------------- | --- |
ForRecall≈0.95,IVF-RaBitQachieves2.2×higherQPSthanthe
|     |     |     |     |     |     |     | paradigms | as  | their CPU | counterparts, | namely | graph-based | ap- |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | --------- | ------------- | ------ | ----------- | --- |
state-of-the-artgraph-basedmethodCAGRA,whilealsoconstruct-
ingindices7.7×fasteronaverage.Comparedtothecluster-based proaches[21,26,29,40,48,49,53,54,57]andcluster-basedap-
methodIVF-PQ,IVF-RaBitQdeliversonaverageover2.7×higher proaches [6, 24, 46, 50, 52, 56]. Graph-based GPU methods re-
throughputwhileavoidingaccessingtherawvectorsforreranking. design proximity graph building and traversal to better match
GPUexecution,leveragingwarp-levelparallelism,shared-memory
caching,andfine-grainedschedulingtomitigatecontrol-flowdi-
ArtifactAvailability: vergence and irregular memory access. Representative systems
Thesourcecode,data,and/orotherartifactshavebeenmadeavailableat suchasSONG[57],cuHNSW[26],GGNN[21],andCAGRA[40]
https://github.com/VectorDB-NTU/cuvs_rabitq. demonstratethatgraph-basedANNScanachievestrongrecalland
competitivequeryperformanceonGPUs.
Comparedwithgraph-basedindices,cluster-basedGPUmethods
1 INTRODUCTION
offeradifferentsetoftrade-offs.Akeymeritisthatcluster-based
| Approximate |     | Nearest | Neighbor | Search (ANNS) |     | on high- |     |     |     |     |     |     |     |
| ----------- | --- | ------- | -------- | ------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
dimensionalvectordatahasbecomeafundamentalcomponentin methodsexposeregularcomputationpatternsthatalignwellwith
GPUprimitives:coarseclusterselectioncanbeimplementedusing
moderndatamanagementandmachinelearning.Itsupportskey
denselinearalgebra(e.g.,GEMMforcomputingquery–centroid
applicationssuchassemanticsearch[4],Retrieval-AugmentedGen-
distances),andthesubsequentprobingwithinselectedclusterscan
eration(RAG)[12],andrecommendersystems[8,13,31].Withthe
beparallelizedaslarge,contiguousstreamsofcodesorvectors.
widespreadadoptionofembedding-basedmodels[11,19,41,42],
productionworkloadsnowofteninvolvemassivehigh-dimensional ThismakesitnaturaltoexploitGPUbatchingandachievehigh
vectors[47,51].Asaresult,designingscalableandefficientANNS
1https://developer.nvidia.com/blog/enhancing-gpu-accelerated-vector-search-in-
| solutionshasbecomealong-standingandactiveresearchtopic. |     |     |     |     |     |     | faiss-with-nvidia-cuvs/ |     |     |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- |

throughput.Moreover,cluster-basedindicestypicallyhavesimpler pipeline.Withinthepipeline,wefurtherdevelopatwo-phasepar-
structuresthanproximitygraphs,withmorepredictablememory allelgridsearchalgorithmforexploringtherescalingfactorsin
access,whicheasesGPUmemorymanagementandimprovesmem- RaBitQquantization.Thesetechniquesenablescalableandhigh-
orycoalescing. throughputRaBitQquantizationformassivedatavectorsonGPUs
Motivatedbytheaboveconsiderations,thispaperfocuseson (e.g.,quantizingover1million960-dimensionalvectorspersecond
cluster-basedANNSmethodsonGPUs.Withinthisfamily,IVF-Flat to 8-bit RaBitQ codes). Second, during search, we adopt a two-
andIVF-PQarewidelyusedbaselines[24,33,43,46,56].IVF-Flat stagedistanceestimationstrategyforfindingnearestneighborsof
stores full-precision vectors and performs brute-force scanning aquery,namelyafilteringstagebasedonthe1-bitRaBitQcode
withinselectedclusters.Itsaccuracyisstrong,butthescanstageis (whichconsistsofthemostsignificantbitofeachdiemensionof
oftendominatedbymemorybandwidthduetohigh-dimensional thecode),followedbyarefinementstageusingtheex-code(which
floating-pointloads.IVF-PQreducesmemorytrafficbycompressing consistsoftheremainingbitsofeachdimensionofthecode)only
vectorsusingproductquantization(PQ)[28].However,itrequires forcandidatesthatpassthefilter.Sincethefilteringstage(which
learningcodebooksduringindexconstruction,introducingaddi- checkesmanydatavectors)dominatestheoverallcomputation,
tionaloverheadonbuildingcomplexity.Also,thecompressedrep- wedeveloptwoGPU-nativeinner-productcomputationschemes,
resentationonlyprovidesapproximatedistanceestimateswithout namelyonebasedonlookuptablesandtheotherbasedonbitwise
strictaccuracyguarantees.Asaresult,achievinghighrecalloften decomposition,toacceleratethisstage.Third,wedesignafused
requiresrerankingwiththerawvectors(e.g.,rawvectorsarestored cluster-localsearchkernelforfindingnearestneighborslocally
inmainmemoryandareaccessedduringsearch),whichincreases withinacluster,whichintegratesdistancefiltering,refinement,
thememoryfootprintandcomplicatestheoverallpipeline. andtop-𝐾 selectionintoasingleGPUkernel,substantiallyreduc-
Recently,anewvectorquantizationmethodcalledRaBitQwas ingkernel-launchoverheadandglobal-memorytraffic.Fourth,to
proposed[17,18],whichimprovesuponPQinseveralimportant supporttheindexbuildandsearchpipelines,wedesignaGPU-
aspects.First,RaBitQdoesnotrequirecodebooktraining.Second, oriented index layout that aligns data organization with access
RaBitQenablesmoreaccuratedistanceestimationwithtight,the- patternsofthefusedkernel,enablinghighmemorycoalescingand
oreticallygroundederrorbounds,whichcaneliminatetheneed cacheefficiency.
torerankcandidatesusingrawvectorswhentargetinghighrecall. WeintegrateIVF-RaBitQintoNVIDIAcuVSlibrary[43]and
RaBitQhasbeencombinedwithIVFforCPU-basedANNsearch cuVSBench[39],enablingreproduciblebenchmarkinganddirect
andhasshownconsistentimprovementsoverPQ[17,18].Never- comparisonswithexistingGPUbaselinesunderaunifiedevaluation
theless,bringingRaBitQtoGPUsandintegratingitwithIVFis framework.WeconductextensiveexperimentsusingcuVSBench
non-trivial andintroduces severalalgorithmic and systemchal- withdiversedatasets, demonstratingIVF-RaBitQ’sadvantagesin
lenges.Specifically,thequantizationprocedureofRaBitQinvolves thetrade-offamongrecall,throughput,indexbuildtime,andstor-
searchingoverrescalingfactorsandevaluatingcandidates,which agefootprint.Forqueryperformance,weevaluatemethodsunder
canbeexpensiveandcontrol-flowheavy. Whenimplementedon large-batch query settings to fully utilize GPU resources. Com-
CPU,RaBitQ’sdistanceevaluationstepbenefitsfromwideSIMD paredwiththestate-of-the-artgraph-basedGPUmethod,CAGRA,
vectorizationandspecializedbit-levelroutines(e.g.,AVX-512-style IVF-RaBitQachievescomparableorhigherthroughput(1.3×~5.6×
packed/shuffleoperationsandfastbit-scan/popcountprimitives) speedupforRecall≈0.95)whilereducingindexconstructiontimeby
toaccelerateasymmetricinnerproductsandreduceper-dimension uptoorderofmagnitude(3.4×~13.1×speedup)withfarlessstorage
overhead[16].OnGPUswithSIMT(SingleInstruction,Multiple requirement.ComparedwithIVF-PQimplementedinNVIDIAcuVS
Thread) execution models, the control-flow heavy quantization Library,IVF-RaBitQachievessignificantlyhigherquerythroughput
becomeswarp-divergent,andtheCPUSIMD-optimizeddistance (1.3×~31.4×speedupforRecall≈0.95)andaccuracyundersimilar
kernelshavenodirectequivalent.Anaiveporteitherunderutilizes indexbuildcostandstoragebudget.TheseresultsshowthatIVF-
theGPUorincursexcessivememorytrafficandkerneloverhead.Re- RaBitQisapracticalandscalablesolutionforlarge-scaleGPU-based
alizingRaBitQeffectivelyonGPUsthereforerequiresGPU-native ANNSproblems.
design,includingscalablequantizationstrategies,GPU-oriented Fortherestofthepaper,wepresentthepreliminariesinSection2,
distance-evaluationprimitives,andcarefulintegrationwiththeIVF the IVF-RaBitQ (GPU) method in Section 3, the experiments in
probe-and-scanpipeline. Section 4, the related work in Section 5, and the conclusion in
Inthispaper,wepresentIVF-RaBitQ(GPU)2,thefirstGPU- Section6.
nativeANNSsolutionthattightlyintegratesIVFcoarsepartition-
ingwithRaBitQquantization,forachievingfastindexbuild,high-
2 PRELIMIARIES
throughputsearch,highrecall,andcompactstoragesimultaneously.
Wesummarizeourtechnicalcontributionstothedevelopmentof 2.1 ApproximateNNSearchandtheIVFIndex
IVF-RaBitQasfollows.First,duringindexbuild,apartfrombuilding ApproximateNearestNeighborSearch(ANNS)findsnearestneigh-
theIVFindex,wequantizethedatavectorswithRaBitQ.Forthis borsofaqueryvectorfromalargecollectionofhigh-dimensional
task,wedesignacluster-at-a-time,block-per-vectorquantization datavectors.Itinvolvestwophases,namelytheindexphaseand
thequeryphase.Intheindexphase,itbuildsanindexonagiven
setof𝑁 vectorsO⊆R𝐷.Inthequeryphase,givenaqueryvector
2SincetheGPUsettingisthefocusofthispaper,wemayrefertoitsimplyasIVF-
q∈R𝐷,itfinds𝐾 approximatenearestneighborswiththehelpof
RaBitQintherestofthepaper. theindex.Comparedtoexactsearch,ANNStradesasmalllossin
2

accuracyforsubstantialgainsinefficiency.TheaccuracyofANNS G,thequantizationprocessdoesnotneedtoenumerateallofthem.
isusuallymeasuredusingrecall.Foraqueryvectorq,letN𝐾(q) Instead,itonlyenumeratesthosewhichareclosestto𝑡·o′forsome
denotethesetofitsexact𝐾 nearestneighbors,andletN ˆ 𝐾(q)be 𝑡.Furthermore,whilethereareinfiniterescalingfactors,thereare
the𝐾 neighborsreturnedbyanANNSalgorithm.Therecallfor only𝐷·2𝐵−1criticalones,atwhichthevectorsthatareclosestto
thisqueryisdefinedasRecall@𝐾(q)=|N𝐾(q)∩N ˆ 𝐾(q)|/𝐾.That 𝑡·o′inGwouldchange[17].Asaresult,thequantizationprocess
is,thismetricmeasureshowmanyofthetruenearestneighborsof canexplorethesecriticalrescalingfactorsonly.Insummary,the
thequeryarereturnedbytheapproximatesearch.Inthispaper,we quantizationprocessistoidentifyandenumerate𝐷·2𝐵−1critical
targetthebatchedsetting:theinputqueriesareprovidedasabatch rescalingfactors.Foreachfactor𝑡,itfindsthevectorxinGthatis
Q ∈ R𝑛𝑞×𝐷,andandwewanttofindthe𝐾 approximatenearest closestto𝑡·o′andcomputesitscosinesimilaritywitho′.Finally,
neighborsforeveryqueryinthebatch. itreturnsthevectorxˆ,whichhasthegreatestcosinesimilarity.
IntheIVFindex,vectorsarefirstpartitionedintoclustersusing Givenarawqueryvectorqr ,wereviewtheprocessofestimat-
aclusteringalgorithm(e.g.,K-means[38]oritsvariations[3,34]). ingtheEuclideandistancebetweenqr andarawdatavectoror in
WhenIVFisusedfornearestneighborsearch,thesearchprocessis RaBitQasfollows.Itfirstrotatesqr withthesamematrixPusedfor
usuallycarriedoutintwostages[28].First,givenaqueryvector,a rotatingthedatavectors.Wedenotethequeryvectorafterrotation
fewnearestclustersareidentifiedbasedonthedistancesbetween byq′.Itthenestimatesthedistancebetweenqr andor basedonsev-
theircentroidstothequery.Then,theseclustersareprobedby eralvariables:namely(1)thedotproductbetweentheRaBitQcode
computingthedistancesbetweenthevectorsintheclustersand ofo,i.e.,xˆ,andtherotatedqueryvector,q′and(2)somefactors[16].
thequeryvectorandfindingthenearestneighbors.Withdifferent Notethatsomeofthese factorsareindependentonthequeryand
settingsofthenumberofclusterstoprobe,IVFprovidesdifferent canbepre-computedbeforethequeryisknown.Otherfactorscan
accuracy-efficiencytrade-offs. onlybecomputedgiventhequery,butcanbesharedamongdata
vectorssothattheamortizedcostforcomputingthefactorsfor
2.2 TheRaBitQQuantizationMethod eachdatavectorisnegligible.Asaresult,thecostofestimating
thedistanceisdominatedbythatofcomputingthedotproduct
Wefirstreviewtheprocessofquantizingarawvectoror inRa-
v B e it c Q to [ r 1 c 7 , , i 1 .e 8 . ] , . w Fi e rs h t, a i v t e n o or = mal o i r z − e c so . r T t h o e a n, u i n t i f t o v c e u c s t e o s r o o n w q r u t a a n c t e iz n i t n e g r b re e f t e w r e r e e n ad xˆ er a s nd to q t ′ h . e Fo d r oc d u et m ai e l n ed ta e ti x o p n re o s f si t o h n e s R o a f B t i h tQ ec L o i m br p a u ry ta 3 ti . on,we
∥or−c∥
theunitvectorosincetheEuclideandistanceordotproductbe-
tweentworawvectorscanbecomputedbasedonthedotproduct 2.3 NVIDIAGPUArchitecture
betweentheirnormalizedvectorsandsomefactorswhichcanbe 2.3.1 ThreadHierarchy. NVIDIAGPUimplementstheSingleIn-
pre-computedandstored[17,18].Specifically,itconstructsacode- struction Multiple Threads (SIMT) execution model. The basic
bookbyshifting,normalizing,andrandomlyrotatingvectorswhose schedulingandexecutionunitintheGPUisthewarp,whichisa
coordinatesare𝐵-bitunsignedintegers,where𝐵couldbe1,2,3,.... groupof32threads.Allthethreadsinawarpexecutethesame
Formally,giventhenumberofdimensionsofavector𝐷 andthe instructionsand canusewarp-levelprimitivesto communicate
numberofbitsusedtoquantizeeachdimension𝐵,thecodebook andexchangedata.Ifthreadswithinasinglewarptakedifferent
Gr isdefinedasfollows: conditionalpaths,thisscenarioconstituteswarpdivergencewhich
carriesaperformancepenalty.Agroupofwarpsareorganized
(cid:40) 2𝐵−1 (cid:12) (cid:12) (cid:41)𝐷 asathreadblock.Theblockservesasthebasicunitthatcanbe
G:= − +𝑢 (cid:12)𝑢 =0,1,2,3,...,2𝐵−1 (1) independentlyscheduledontoaStreamingMultiprocessor(SM),
2 (cid:12)
(cid:12) whichisthephysicalcoreunitontheGPU.Multipleblockscan
(cid:40) (cid:12) (cid:41) beresidentonasingleSMsimultaneously,dependingonresource
x (cid:12)
Gr := P
∥x∥
(cid:12)
(cid:12)
x∈G (2) availabilityandkernelrequirements.Agroupofblocksconstitutes
(cid:12) agrid.Agridisthetop-levelorganizationalstructuretoexecute
wherePisarandomorthogonalmatrix[25].
asinglekernel,whichisafunctionlaunchedfromthehost(CPU)
Toquantizethevectoro,ittakeso’snearestvectorinthecode-
andexecutedonthedevice(GPU).
bookGr ,whichwedenotebyoˆ,asitsquantizedvector.Letxˆbethe
vectorinG,whichcorrespondstooˆ (notethateachvectorinGr 2.3.2 MemoryHierarchy. GPUmemoryhierarchyiscriticaltothe
correspondstoavectorinG(beforenormalizationandrotation)). designofaGPU-basedsolution.Atthebottom,thereisaglobal
Thisprocesscanbeformallydescribedasfollows. memory(alsoknownasdevicememory),whichservesasthepri-
marystoragefordataandcanbeaccessedbyallthreads.Theglobal
(cid:13) (cid:13)2 (cid:28) (cid:29) memoryhasthelargestspaceandthehighestlatencyontheGPU,
xˆ =argmin(cid:13) (cid:13)P x −o (cid:13) (cid:13) =argmax x ,o′ (3) andthelocalityofdataaccesstotheglobalmemoryiscriticalto
x∈G (cid:13) ∥x∥ (cid:13) x∈G ∥x∥ theefficiency.Specifically,globalmemoryaccessesareissuedat
whereo′ =P−1oisthedatavectorafterrotation. the warplevel. Whenthreadswithin awarp access contiguous
AccordingtoEquation3,thequantizationprocessistofindxˆ, andalignedmemoryaddresses,theaccessescanbecoalescedinto
whichisthevectorx∈Gthatmaximizesthethecosinesimilairty fewermemorytransactions,whicheffectivelyexploitstheband-
withthedatavectorafterrotation,i.e.,o′.Accordingtotheanalysis widthofglobalmemory.Upontheglobalmemory,thereisacache
in[17],thevectorxˆmustbeclosesttoare-scaledvectoro′forsome
rescalingfactor𝑡,i.e.,𝑡·o′.Therefore,whilethereare2𝐵·𝐷vectorsin 3https://vectordb-ntu.github.io/RaBitQ-Library/rabitq/estimator/
3

levelnamedL2cache,whichkeepsdataread/writtentotheglobal IVF-RaBitQ,itisusedtostoretheIVFindexinGPUglobalmemory,
memoryandissharedamongallSMs.ForeachSM,thereisanL1 which has separate contiguous arrays for 1-bit codes, ex-codes,
cacheandsharedmemorythatusethesamehardware.Thistypeof andauxiliaryfactors.Wefurtheradoptaninterleavedlayoutfor
memoryhaslowlatencyandcanonlybesharedforthreadswithin 1-bitcodesthatistailoredtotheaccesspatternofthedominant
anSM.Atthetop,eachSMhas32-bitregisters,whichareprivate filterstage,leadingtoimprovedmemorycoalescingontheGPU
tothreadsandhavethelowestread/writelatency. (Section3.4.3).
3 THEGPU-BASEDIVF-RABITQMETHOD 3.2 IndexBuildonGPU
3.1 Overview 3.2.1 Clustering,NormalizationandRotation. WerunGPU-based
BalancedK-means[44]tolearn𝑛 centroidsandassigneachdata-
IVF-RaBitQ(GPU)isaGPU-nativeANNSsolutionthatcombinesan 𝑘
basevectortoitsnearestcentroid.Thisproducesthecentroidmatrix
IVFcoarsepartitionwithRaBitQquantizationandimplementsboth
C ∈ R𝑛𝑘×𝐷 andaclusteridforeachvector.Withineachcluster,
indexbuildandsearchasGPU-friendlypipelines.Theoverviewof
wenormalizeeachvectortounitℓ normwrtitscorresponding
itsworkflowisdescribedasfollows. 2
centroid.Forsimplicity,whenthecontextisclear,werefertothe
Indexbuild.Givenasetof𝑁 rawdatavectorsO ∈ R𝑁×𝐷 (𝐷 normalizedvectorsas(data)vectorsanddenoteadatavectorby
isthevectordimensionality),wefirstlearn𝑛
𝑘
IVFcentroidsand o.WethenapplyasharedrandomorthogonalmatrixPtorotate
assigneachdatavectortoitsnearestcentroid,therebyforming datavectorsandcentroids,whichisimplementedusingGeneral
𝑛 𝑘 invertedlists.Withineachcluster,wenormalizethevectors Matrix Multiplication (GEMM). Since P is orthogonal, the rota-
withrespecttothecentroid,rotatethemwitharandomorthogonal tionpreservesinnerproductsanddistancesbetweendatavectors,
matrixP,andquantizethemusingRaBitQandobtaintheircodes. centroids,andthereforedoesnotalterexactnearest-neighborrela-
Eachcodeisstoredintwoparts:(i)themostsignificantbitofeach tionships.Wedenoteadatavectorafterrotationbyo′.
dimension(whichwecallthe1-bitRaBitQcodeorsimplythe1-
bitcode)and(ii)theremainingbits(whichwecalltheex-code). 3.2.2 GPU-basedRaBitQQuantizationforDataVectors. Givena
Toenableefficientlarge-scaleRaBitQquantizationonGPU,we
setof𝑁 datavectorsoandabudgetof𝐵bitsperdimension,weaim
todevelopaGPU-basedsolutionforquantizingthedatavectors
writeGPUkernelstoprocessvectorsinacluster-wisemanner,and
usingRaBitQ,i.e.,computingtheRaBitQcodesofthedatavectors.
developGPU-friendlyalgorithmsforexploringtherescalingfactors
usedinRaBitQquantization(Section3.2). Kernelgranularityandthreadmapping.Wefirstdecidetheker-
nelgranularity(i.e.,howmanyvectorsareprocessedperlaunch),
Search. In IVF-RaBitQ, queries are processed in batches whichdirectlyaffectstheparallelismeffectivenessbydetermining
(Section3.3).GivenaquerybatchQ ∈ R𝑛𝑞×𝐷 andaprobecount howcomputationandmemoryresourcesarescheduled.Quantizing
𝑛 ,wefirstapplythesamerandomorthogonaltransformation
probe onevectoratatimeisprohibitivelyexpensivewhenthedataset
Pusedinindexbuildtothequeriesandselectthe𝑛
probe
closestIVF
containsmillionstobillionsofvectors,becausekernel-launchover-
clustersforeachquery.Thesearchworkloadisthenorganizedatthe
headandper-vectorschedulingcostsaccumulatequickly,andthe
granularityof(query,cluster)pairs,enablingindependentandparal-
GPU’smassiveparallelism(hundredsofthousandsofconcurrent
lelprocessingwithineachprobedcluster.Foreach(query,cluster)
threads)isdifficulttofullyutilize.Attheotherextreme,quantiz-
pair,weperformacluster-localsearchthatevaluatescandidates
ingallvectorsatoncecansaturatetheGPU,butitimposesahigh
storedinthecorrespondinginvertedlistandfindsthetop-𝐾 can-
GPUmemoryfootprint(especiallyforintermediatebuffers)andis
didates(i.e.,𝐾 nearestneighbors)ofthequerywithinthecluster.
inflexibleacrossdatasetsofdifferentsizes.Wethereforeadopta
Specifically,itadoptsatwo-stagedistanceestimationstrategy:a
cluster-at-a-timedesign:eachkernellaunchprocessesthevectors
filteringstagebasedonthe1-bitRaBitQcode,followedbyarefine-
inonecluster,whichgivesanaturalandboundedunitofwork
mentstageusingtheex-codeonlyforcandidatesthatpassthefilter.
aligned with the IVF structure, and makes the implementation
Sincethefilteringstagechecksmanydatavectorsanddominates
largelydata-sizeindependent.
theoverallcomputation,wedesignGPU-nativeinner-productcom-
Next,wedecidethemappingbetweenGPUexecutionunitsand
putationmethodstoacceleratethisstage(Section3.4.1),andfurther
vectors.Astraightforwardapproachistoassignasinglethread
integrateitwithfiltering,refinement,andtop-𝐾 selectionintoa
toeachvector,analogoustotheparallelizationstrategytypically
fusedGPUkerneltoreducekernel-launchandmemory-accessover-
employedonCPUs.However,thispreventsintra-vectorparalleliza-
heads(Section3.4.2).Finally,thetop-𝐾 candidatesobtainedfrom
tion:thecomputationrequiredbyRaBitQforasinglevector(which
allprobedclustersaremergedtoproducetheglobaltop-𝐾 result
involvesexploringmultiplecriticalscalingfactors)becomesseri-
foreachquery.
alizedwithinonethread,limitingthroughput.Moreover,adjacent
GPU index layout. To efficiently support ANNS on GPU, we threadsinawarpwouldtypicallyaccessdifferentvectorslocated
designaflattenedCompressedSparseRow(CSR)-likelayout[5]. at different regions in global memory, which can easily lead to
Intuitively,afterK-meanstraining,eachvectorisassignedtoex- uncoalescedmemoryaccessesandlowereffectivebandwidth.Addi-
actlyonecluster.Ifweconceptuallyuseabinarymatrixofsize tionally,underacluster-at-a-timeexecutionschedule,thenumber
num_clusters×num_vectors,whereentry(𝑖,𝑗)=1indicatesthat ofconcurrentlyprocessedvectorsmaybeinsufficienttofullyutilize
vector𝑗 belongstocluster𝑖(and0otherwise),theresultingmatrix theGPU.Thus,weadoptablock-per-vectormappingasarobustand
isasparsematrixsinceeachcolumncontainsonlyonenon-zero flexibledesignpoint,whichhasseveraladvantages:(1)itenables
entry.Thus,thedatacanbeorganizedintoaCSR-likeformat.In fine-grainedparallelismforthatvector,e.g.,itcanexploremultiple
4

criticalscalingfactorsinparallel;and(2)thethreadsinthesame Algorithm1:Two-PhaseParallelGrid-SearchforRaBitQ
| warpaccesscontiguous(ornear-contiguous)locationsofthesame |     |     |     |     |     |     | Quantization |     |     |     |     |     |     |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- |
vector,yieldingcoalescedglobal-memoryaccesses.Thisimproves
Input:A𝐷-dimensionalrotatednormalizedvectoro′;the
bothcomputeefficiencyandmemorythroughput,andmakesit numberofbitsperdimension𝐵;
easiertomaintainhighoccupancyevenwhenoperatingclusterby Output:Thequantizationcodexˆ.
cluster.
1 max 𝑜 ←ParallelMax(|o′|);
Efficient exploration of rescaling factors. The standard Ra- Initialize𝑡 and𝑡 basedonmax and𝐵;
|     |     |     |     |     |     |     | 2   | start | end |     | 𝑜   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
BitQquantizationalgorithmenumerates𝐷·2𝐵−1criticalrescaling 𝑣 max←0, 𝑡 max←𝑡 ;
|            |           |       |     |           |            |           | 3                       |     | start |     |           |     |     |
| ---------- | --------- | ----- | --- | --------- | ---------- | --------- | ----------------------- | --- | ----- | --- | --------- | --- | --- |
| factors in | ascending | order | and | evaluates | them using | incremen- |                         |     |       |     |           |     |     |
|            |           |       |     |           |            |           | for𝑡inuniformgridover[𝑡 |     |       | ,𝑡  | end]with𝑁 |     |     |
talupdates[17].Tosupportthisefficientenumeration,previous 4 start coarsesamplesdo
| CPUimplementationmaintainsper-vectorstate,typicallyusing |     |     |     |     |     |     | inparallel      |     |     |                               |     |     |     |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | ----------------------------- | --- | --- | --- |
|                                                          |     |     |     |     |     |     | Findthecodexcur |     |     | thatisclosestto𝑡·o′andcompute |     |     |     |
| asmallpriorityqueuetogeneratethenextrescalingfactorwith- |     |     |     |     |     |     | 5               |     |     |                               |     |     |     |
,o′⟩and∥xcur∥;
| outexplicitlymaterializingorsortingallcandidates[17].However, |     |     |     |     |     |     | ⟨xcur |     |     |     |     |     |     |
| ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- |
thissequentialenumerationreliesonfine-grainedstateupdates if ⟨xcur ,o′⟩/∥xcur∥ >𝑣 maxthen
6
andinvolvesirregularcontrolflow,whichisnotfriendlytoGPU 𝑣 max←⟨xcur ,o′⟩/∥xcur∥, 𝑡 max←𝑡;
7
executionmodel.
8 end
| Toachievehighaccuracyacrossdimensionalitieswhilemain- |     |     |     |     |     |     | end |     |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
9
taininghighperformance,weproposeaGPU-friendlysearchfor 𝑡 center←ParallelArgMax(𝑣 ,𝑡 max);
|     |     |     |     |     |     |     | 10  |     |     | max |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
therescalingfactor.RecallthatthequantizationprocessofRaBitQ
|                                                                |     |          |                    |     |                 |     | 𝛿 ←(𝑡                | end−𝑡 start)/(𝑁 | coarse−1);           |     |          |                   |     |
| -------------------------------------------------------------- | --- | -------- | ------------------ | --- | --------------- | --- | -------------------- | --------------- | -------------------- | --- | -------- | ----------------- | --- |
| exploresasetofciriticalrescalingfactors.Foreachfactor𝑡,itiden- |     |          |                    |     |                 |     | 11                   |                 |                      |     |          |                   |     |
| tifiesavectorx∈                                                |     | G(wh     | ichistheclosestto𝑡 |     | ·o′)andcomputes |     |                      |                 |                      |     |          |                   |     |
|                                                                |     |          |                    |     |                 |     | 12 𝑡 s ′ tart ←max(𝑡 |                 | start ,𝑡 center−𝛿),𝑡 |     | ′ ←min(𝑡 | end ,𝑡 center+𝛿); |     |
|                                                                |     | (cid:68) | (cid:69)           |     |                 |     |                      |                 |                      | e   | nd       |                   |     |
thedotproduct x ,o′ (or ⟨x,o′⟩/∥x∥).Finally,itreturnsthe 𝑣 max←0, 𝑡 max←𝑡 ;
|     |     | ∥ x∥ |     |     |     |     | 13                       |     | center |     |             |     |     |
| --- | --- | ---- | --- | --- | --- | --- | ------------------------ | --- | ------ | --- | ----------- | --- | --- |
|     |     |      |     |     |     |     | for𝑡 inuniformgridover[𝑡 |     |        | ′   | ,𝑡 ′ ]with𝑁 |     |     |
vectorxˆ,whichhasthegreatestdotprodcut.Thisquantization 14 s tart e nd finesamplesdo
| processcanberegardedasoneofoptimizinganobjectivefunction |     |     |     |     |     |     | inparallel |     |     |     |     |     |     |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- |
⟨x,o′⟩/∥x∥of𝑡.Weobservethisobjectivefunctionisoftenapprox- Findthecodexcur thatisclosestto𝑡·o′andcompute
15
imatelyunimodalinpractice(i.e.,ittendstoincreasethendecrease ,o′⟩and∥xcur∥;
⟨xcur
withasinglepeak(possiblywithsmalllocalfluctuations)).Aclassi-
|     |     |     |     |     |     |     | if  | ⟨xcur ,o′⟩/∥xcur∥ |     | >𝑣 maxthen |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | ---------- | --- | --- | --- |
16
calternarysearchlocatesthemaximumofaunimodalfunctionby 𝑣 max←⟨xcur ,o′⟩/∥xcur∥, 𝑡 max←𝑡;
17
repeatedlyshrinkingtheinterval;however,itisinherentlyiterative
18 end
andnotidealforGPUcontrolflow.
end
| I n s p ir e | d by t e | rn a r y se | a r c h , w | e ad o p t | a               |                  | 19                     |     |     |     |          |     |     |
| ------------ | -------- | ----------- | ----------- | ---------- | --------------- | ---------------- | ---------------------- | --- | --- | --- | -------- | --- | --- |
|              |          |             |             |            | t w o -p h a se | g r id se a r ch | 𝑡 max←ParallelArgMax(𝑣 |     |     |     | ,𝑡 max); |     |     |
tha t a c h ie v es as i m il a r co ar s e - to - fi ne n ar r ow i n g e ff e ct us i n ga fi x e d 20 max
|     |     |     |     |     |     |     | Computexˆ | viarescalingandroundingofo′with𝑡 |     |     |     |     | ;   |
| --- | --- | --- | --- | --- | --- | --- | --------- | -------------------------------- | --- | --- | --- | --- | --- |
numberofGPU-parallelrounds.Thepseudocodeofouralgorithm 21 max
| ispresentedinAlgorithm1.Givena𝐷-dimensionalnormalized |     |     |     |     |     |     | returnxˆ; |     |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- |
22
| vector o′               | (after | rotation) | and bit-width𝐵, |                             | we first | compute the |     |     |     |     |     |     |     |
| ----------------------- | ------ | --------- | --------------- | --------------------------- | -------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
| maximumabsoluteentrymax |        |           | =max            | 𝑖|𝑜 ′|viaaparallelreduction |          |             |     |     |     |     |     |     |     |
|                         |        |           | 𝑜               | 𝑖                           |          |             |     |     |     |     |     |     |     |
acrossdimensions,whichisusedtodeterminethesearchrange
theindexbuild.ThisoperationisimplementedasasingleGEMM
| [ 𝑡 st a rt ,𝑡 e n d | ] ( li n e | 1 ~ 2) . T h | e a l g o r it | h m th e n | p r o c e ed si | n tw o p hases. |     |     |     |     |     |     |     |
| -------------------- | ---------- | ------------ | -------------- | ---------- | --------------- | --------------- | --- | --- | --- | --- | --- | --- | --- |
ontheGPU,producingacontiguousrotatedquerybatchQ′thatis
| I n t h e c o a | r s e s e ar | c h p h a s | e (l i n e 3 | ~ 1 0), w e u | n i fo r m ly s | am pl e 𝑁 |                                                 |     |     |     |     |     |     |
| --------------- | ------------ | ----------- | ------------ | ------------- | --------------- | --------- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                 |              |             |              |               |                 | coarse    | reusedbyallsubsequentstagesinthesearchpipeline. |     |     |     |     |     |     |
candidaterescalingfactorsacrossthesearchrangeandevaluate
theminparallelusingmultiplethreads.Foreachcandidate𝑡,we
|                 |     |                  |     |     |                     |     | 3.3.2 ClusterSelection. |     |     | Weselectthe𝑛             | probe | closestclustersfor |        |
| --------------- | --- | ---------------- | --- | --- | ------------------- | --- | ----------------------- | --- | --- | ------------------------ | ----- | ------------------ | ------ |
| findthecodexcur |     | thatisclosestto𝑡 |     | ·o′ | andcomputetheobjec- |     |                         |     |     |                          |       |                    |        |
|                 |     |                  |     |     |                     |     | eachquery.LetC∈R𝑛𝑘×𝐷    |     |     | bethecentroidmatrixandQ′ |       |                    | ∈R𝑛𝑞×𝐷 |
tive⟨xcur ,o′⟩/∥xcur∥.Aparallelreductionthenidentifiesthebest betherotatedquerybatch.ThesquaredEuclideandistancematrix
candidate𝑡 center .Inthefinesearchphase(line11~20),wenarrow betweenqueriesandcentroidscanbewritteninmatrixformas
| thesearchrangetoasmallneighborhoodaround𝑡 |     |     |     |     |     | andrepeat |     |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
center
theparallelevaluationwith𝑁 samplestorefinethesolution. D=sq1𝑛 ⊤ +1𝑛𝑞 s⊤ −2Q′C⊤, (4)
|                          |     |     | fine                           |     |     |     |     |     |     | 𝑘   | c   |     |     |
| ------------------------ | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Thefinalrescalingfactor𝑡 |     |     | isusedtoproducethequantization |     |     |     |     |     |     |     |     |     |     |
m a x
codexˆ.OntheGPU,forea c h rescalingfactor,weassignathread wheresq ∈R𝑛𝑞 andsc ∈R𝑛𝑘 storethesquaredℓ 2 normsofqueries
andcentroids,respectively.ThedominanttermQ′C⊤iscomputed
blocktodothesamplingandthereductioninparallel.Inthisway,
|     |     |     |     |     |     |     | viaasingleGEMMontheGPU,andaparalleltop-𝐾 |     |     |     |     |     | kernel[55]is |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | ------------ |
thealgorithmcanfinishin𝑂(1)roundsontheGPU,whichsignifi-
|     |     |     |     |     |     |     | thenusedtoselectthe𝑛 |     |     | nearestclustersperquery. |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | ------------------------ | --- | --- | --- |
cantlyoutperformsthestandardquantizationalgorithm(𝑂(𝐷·2𝐵) probe
complexity).
|     |     |     |     |     |     |     | 3.3.3 ProbeSchedulingviaWorkloadReorganization. |     |            |     |          |            | Afterclus-  |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------- | --- | ---------- | --- | -------- | ---------- | ----------- |
|     |     |     |     |     |     |     | ter selection,                                  | we  | reorganize | the | workload | explicitly | as a set of |
3.3 SearchPipelineonGPU (query,cluster) pairs,onepairperprobedclusterofeachquery.
LetQ R𝑛𝑞×𝐷 beabatchofqueries.We Wesortthesepairsbyclusteridentifierbeforelaunchingthesearch
| 3.3.1 BatchRotation. |     |     | ∈   |     |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
rotatethebatchusingthesamesharedorthogonalmatrixPasin kernels.ThisreorganizationisadoptedfromcuVS’sIVF-PQ[43],
5

whichconvertstheirregularper-queryprobelistsintoanexecu- instructionsandcannotbedirectlyportedtoGPUsduetofunda-
tionorderthatisfriendlytoGPU:first,blocksthatprocessthe mentaldifferencesinexecutionmodelsandavailableinstruction
same(ornearby)clustersexecutecloserintime,improvingcache sets. Thus, a straightforward approach would be to expand the
localityfortheRaBitQcodes;second,theclustersofafixedquery binarycodesintobytevaluesandreuseconventionalinner-product
acrossthebatcharelesslikelytobeprobedconcurrently,which operators.However,suchadesignisinefficientonGPUs,asitin-
givesatigherrunningtop-𝐾 thershold(i.e.,thecurrent𝐾-thbest troducesunnecessarytypeconversionsandleadstosuboptimal
distanceforeachquery)toenablemoreaggressivepruninginlater utilizationofGPUcomputeandmemoryresources.
probes.BeforetheseworkloadsaremappedtoSMsontheGPU,we To address the problem, we develop two GPU-native inner-
computequery-dependentfactorsonceperqueryandpreparethe productcomputationschemesforthistypeofinnerproduct.The
queryrepresentationneededbythechoseninner-productmethod firstschemeadoptsalookuptablebasedstrategythattradesshared-
(Section3.4.1);theseresultsarereusedacrossthatquery’s𝑛 memorycapacityforreducedarithmeticoperations,whilethesec-
probe
clusterscans. ondschemereformulatestheinnerproductintoabitwisedecom-
positionthatexploitsGPU-friendlybitwiseoperations.Thesetwo
3.3.4 Cluster-localSearchandTwo-stageDistanceEstimation. For schemesrepresentdifferentdesignpointsinthetrade-offbetween
| each (query,cluster) | pair,wecomputecluster-local |     | top-𝐾 candi- |     |     |     |     |     |     |
| -------------------- | --------------------------- | --- | ------------ | --- | --- | --- | --- | --- | --- |
arithmeticintensityandon-chipmemoryusage,andaredescribed
dates(whicharethequery’s𝐾nearestneighborslocallywithinthe
indetailbelow.
thecluster)usingatwo-stageestimator: (1)LookupTablebasedStrategy.Wefirstconsideramemory-
• Stage1(filter):computeafast1-bitdistanceestimate(and centric strategy that replaces arithmetic operations with table
alowerbound)basedonthe1-bitRaBitQcodeandprune lookupsbyleveragingGPUsharedmemory.Specifically,wepre-
vectorswhosevaluesexceedthecurrentthreshold(i.e.,the computequery-dependentlookuptables(LUTs)andreusethem
current𝐾-thbestdistanceforeachquery). acrossalldatavectorswhenevaluatingthe1-bitestimateddistance.
DifferentfromGPUimplementationsofIVF-PQ(e.g.,cuVS[43])
• Stage2(refinement):forthesurvivingcandidates,read
additionalbitsoftheRaBitQcode(ex-code)tocompute that build LUTs over PQ codewords (i.e., per PQ dimen-
a more accurate estimated distance and then select the sion/subspace),weconstructLUTsthataggregateinner-product
cluster-localtop-𝐾 candidates. contributionsovermultipledimensionsofthe1-bitRaBitQcode.
|     |     |     |     | Formally,wepartitionthedimensionsintogroupsof𝑈 |     |     |     | bitsand |     |
| --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | ------- | --- |
Forsimplicity,werefertotheestimateddistancesinStage1and
|     |     |     |     | constructmultiplelookuptablesaccordingly.Let𝑚=𝐷/𝑈 |     |     |     |     | bethe |
| --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | ----- |
Stage2asthe1-bitestimateddistanceandtherefinedestimateddis-
numberofpartitionedblocks,and
tance,respectively.Sincetheinner-productcomputationbetween
thequeryandthe1-bitRaBitQcodesinStage1dominatesthecom- xˆ (𝑗), q′(𝑗) ∈R𝑈, 𝑗 =1,...,𝑚
b
putation(notethatthecomputationisconductedforallvectors
bethesubvectorscorrespondingtothe𝑗-thblockofthe1-bitcode
| in the probed | clusters) | [16], we develop | two GPU-native inner- |     |     |     |     |     |     |
| ------------- | --------- | ---------------- | --------------------- | --- | --- | --- | --- | --- | --- |
andthequeryvector(afterrotation)q′,respectively.Foreach
| productcomputationschemestailoredtotheGPUexecutionmodel |     |     |     | xˆb |     |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
block,weprecomputealookuptable(LUT)thatstorestheinner
(Section3.4.1).Moreover,thistwo-stageestimatorisrealizedon
|     |     |     |     | products | between | q′(𝑗) and all possible | 2𝑈 binary | patterns | and |
| --- | --- | --- | --- | -------- | ------- | ---------------------- | --------- | -------- | --- |
theGPUasafour-stepcluster-localsearchprocedure,including(1)
|     |     |     |     | storethevalues.Specifically,giventhe |     |     | 𝑗thblock,wedefinethe |     |     |
| --- | --- | --- | --- | ------------------------------------ | --- | --- | -------------------- | --- | --- |
1-bitestimateddistancecomputation,(2)candidateselection(i.e.,
correspondingLUTasfollows:
retainingvectorswhoseestimateddistancespassthecurrentthresh-
old),(3)refinedestimateddistancecomputation,and(4)in-block 𝐿 :{0,1}𝑈 →R (5)
𝑗
top-𝐾selection(i.e.,selectingthebest𝐾candidateswithinathread
𝑈
block).ThesestepsarefusedintoasingleGPUkerneltoreduce 𝑗(b)=⟨q′(𝑗),b⟩= ∑︁ b∈{0,1}𝑈
|     |     |     |     | 𝐿   |     | q′[(𝑗−1)𝑈 | +𝑖]·b[𝑖], |     | (6) |
| --- | --- | --- | --- | --- | --- | --------- | --------- | --- | --- |
kernellaunchoverheadandglobal-memorytraffic(Section3.4.2).
𝑖=1
|                         |     |                                     |     | Givenabinarycodevectorxˆb |     | ,theinnerproduct⟨xˆb |     | ,q′⟩canthen |     |
| ----------------------- | --- | ----------------------------------- | --- | ------------------------- | --- | -------------------- | --- | ----------- | --- |
| 3.3.5 Batch-levelMerge. |     | Eachblockoutputscluster-localcandi- |     |                           |     |                      |     |             |     |
becomputedbysummingtheLUTentriescorrespondingtoeach
dates.Foreachquery,wemergecandidatesfromits𝑛 clusters
|                 |                                     |     | probe | block: |            |                |           |             |     |
| --------------- | ----------------------------------- | --- | ----- | ------ | ---------- | -------------- | --------- | ----------- | --- |
| andrunaGPUtop-𝐾 | toproducethefinalapproximatenearest |     |       |        |            |                |           |             |     |
| neighbours.     |                                     |     |       |        |            | 𝑚              | 𝑚         |             |     |
|                 |                                     |     |       |        |            | ∑︁ (𝑗),q′(𝑗)⟩= | ∑︁        | (𝑗)(cid:1). |     |
|                 |                                     |     |       |        | ⟨xˆb ,q′⟩= | ⟨xˆ            | 𝐿 (cid:0) | xˆ          | (7) |
|                 |                                     |     |       |        |            | b              | 𝑗         | b           |     |
|                 |                                     |     |       |        |            | 𝑗=1            | 𝑗=1       |             |     |
3.4 KernelandData-LayoutCo-design
|     |     |     |     | Inpractice,eachbinaryblockxˆ |     | (𝑗) isinterpretedasanintegerindex |     |     |     |
| --- | --- | --- | --- | ---------------------------- | --- | --------------------------------- | --- | --- | --- |
3.4.1 GPUInner-ProductComputationfor1-bitEstimatedDistance. b
RecallinRaBitQ,weneedtocomputetheinnerproductbetweena 𝑘 ∈{0,...,2𝑈 −1},allowingtheinnerproductcomputationtobe
queryvectorq′(afterrotation)andthe1-bitRaBitQcodeofadata performedvia𝑚tablelookupsfollowedbyasummation.
vector,whichwedenotebyxˆb ,forcomputingthe1-bitestimated AccordingtoSection2.2,inIVF-RaBitQ,theinnerproductbe-
distancebetweenthequeryandthevector(Section2.2).Thatis, tweenxˆb andq′hasnorelationshipwithwhichclusterxˆb belongs
theinnerproductiscomputedinanasymmetricform,wherequery to.Thatis,tocomputethe1-bitestimateddistancebetweenaquery
vectorsarerepresentedinhigherprecision(e.g.,floating-point), vectoranddifferentdatavectors,theLUTsonlyneedtobecom-
whiledatavectorsareencodedascompact1-bitRaBitQcodes.Exist- putedonceandcanbereusedacrossalldatavectors.Foreachquery,
ingCPU-orientedaccelerationtechniques[16]arebasedonSIMD wehave𝐷/𝑈LUTs,whereeachLUTusesthe𝑈bitsasentryandhas
6

|     |     |     | qˆ(0)[1] |     | qˆ(0)[2] | qˆ(0)[D] |     | popcnt |     |     |     |      |              |     |
| --- | --- | --- | -------- | --- | -------- | -------- | --- | ------ | --- | --- | --- | ---- | ------------ | --- |
|     |     |     |          |     | · · ·    |          |     |        |     |     | ≪ 0 | 2Bq− | 1 xˆ ,qˆ(Bq− | 1)  |
b
|               |        | &   | qˆ(1)[1] |     | qˆ(1)[2] | qˆ(1)[D] |     | popcnt |     |     | 1   | −   | ⟨   | ⟩   |
| ------------- | ------ | --- | -------- | --- | -------- | -------- | --- | ------ | --- | --- | --- | --- | --- | --- |
|               |        | &   |          |     | · · ·    |          |     |        |     |     | ≪   |     | +   |     |
| xˆb[1] xˆb[2] | xˆb[D] | &   |          | ... | ... ...  | ...      |     |        | ... |     | ... |     |     |     |
|               | ···    |     |          |     |          |          |     |        |     |     |     | Bq− | 2   |     |
&
qˆ(Bq−1)[1] qˆ(Bq−1)[2] qˆ(Bq−1)[D] popcnt (Bq− 1) 2j xˆ b ,qˆ(j)
|     |     |     |     |     | ··· |     |     |     |     | ≪   |     |     | ⟨   | ⟩   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Xj=0
| DataVectorxˆb |     |     |     |     | QueryVectorqˆ |     |     |     |     |     |     | InnerProductResult |     |     |
| ------------- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --- |
Figure1:BitwiseInnerProductComputation.xˆ b[𝑖]denotesthe𝑖thdimension(bit)ofthedatavectorxˆ b,andqˆ(𝑗)[𝑖]denotesthe
𝑗thbitofthequeryvector’s𝑖thdimensionqˆ[𝑖].
| asizeofsizeof(lut_type)×2𝑈 |     |     | bytes.Toenablehigh-throughput |     |     |     |     |     |     |     |     |     |     |     |
| -------------------------- | --- | --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
execution,anidealcaseshouldbethatLUTsfromdifferentqueries
𝐷
| canresideinanSM’ssharedmemory(e.g.,upto164KBonAmpere  |     |     |     |     |     |     |     |       | ∑︁            |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----- | ------------- | --- | --- | --- | --- | --- |
|                                                       |     |     |     |     |     |     | ⟨xˆ | ,qˆ⟩= | xˆ b[𝑖]·qˆ[𝑖] |     |     |     |     | (9) |
| and228KBonHopper-classGPUs)atthesametime,sothatmulti- |     |     |     |     |     |     |     | b     |               |     |     |     |     |     |
𝑖=1
plequeriescanbeprocessedconcurrentlyonasingleSM.Thus,we
𝐵q−2
𝐷
s e t 𝑈 t o 4 t o a c h i e v e t h e b e s t p e r f o r m a nc e . F o r e x a m p le ,if w e u s e ∑︁ xˆ b[𝑖]·(cid:169) −2𝐵q−1 qˆ(𝐵q−1)[𝑖]+ ∑︁ 2𝑗 qˆ(𝑗)[𝑖](cid:170) (10)
|              |                      |                  |               |               |                      |       |     | =   |     | (cid:173) |     |     |     | (cid:174) |
| ------------ | -------------------- | ---------------- | ------------- | ------------- | -------------------- | ----- | --- | --- | --- | --------- | --- | --- | --- | --------- |
| F P 1 6t o s | to r e i n n e r p r | o d u c t r e su | l t s i n L U | T , f o r a 1 | ,0 2 4 -d im en s io | n a l |     |     |     |           |     |     |     |           |
|              |                      |                  |               |               |                      |       |     |     | 𝑖=1 |           |     | 𝑗=0 |     |           |
query,weonlyneed 1024/4×24×2B = 8KBtostoreallLUTs. (cid:171) (cid:172)
|               |                    |                   |            |              |                  |       |     |            |     |             | 𝐵 q−2    |         |     |      |
| ------------- | ------------------ | ----------------- | ---------- | ------------ | ---------------- | ----- | --- | ---------- | --- | ----------- | -------- | ------- | --- | ---- |
| O n c e t h e | L U T s ar e l o a | d e d i n t o t h | e G P U ’s | sh a r e d m | em o ry , th e y | c a n |     |            |     |             |          |         |     |      |
|               |                    |                   |            |              |                  |       |     | =−2𝐵q−1⟨xˆ |     | ,qˆ(𝐵q−1)⟩+ | ∑︁ 2𝑗⟨xˆ | ,qˆ(𝑗)⟩ |     | (11) |
be s h a r e d w i th h u n d r e d s o f t h r e a ds w i th in a t h r e ad blo c k w i th l o w b b
𝑗=0
accesslatency,enablingparallelinner-productevaluationforlarge
batchesof1-bitRaBitQcodes. Thisequationdepictsthattheinnerproductcanbeviewedasa
|     |     |     |     |     |     |     | weightedsumofinnerproductsbetweenbinaryvectorsxˆb |     |     |     |     |     |     | andqˆ(𝑗). |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --------- |
(2)BitwiseDecompositionbasedStrategy.WhiletheLUT-based
AsshowninFigure1,theinnerproductbetweentwobinaryvec-
approachiseffective,itreliesonquery-dependenttablesresidingin
torscanbeefficientlycomputedviabitwiseAND(&)andpopulation
sharedmemory,whichcanlimiton-chipresidencyandparallelism
forhigh-dimensionalvectorsorGPUswithrelativelysmallshared count(POPCNT)operations.SinceGPUregistersare32bitswide,
memory.Tocomplementthismemory-centricdesign,werevisit wecanprocess32dimensionswithinasingleoperation,which
theinner-productcomputationitselftodevelopacompute-centric providesanadvantageoverclassicaldimension-wiseinner-product
|                                                        |     |     |     |     |     |     | computation.Once⟨xˆ |     |     | ,qˆ(𝑗)⟩iscomputed,thefinalweightedsum |     |     |     |     |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | ------------------------------------- | --- | --- | --- | --- |
| schemethatminimizesshared-memoryusageandbetterexploits |     |     |     |     |     |     |                     |     |     | b                                     |     |     |     |     |
canbeobtainedthroughseveralshiftandaddoperations.Compared
GPUbitwiseinstructions.
Theclassicalinner-productcomputationprocessesvectorsdi- totheLUT-basedapproach,thebitwiseinnerproducttradesaddi-
mensionbydimension.OnGPUs,however,thereisnonativein- tionalintegerarithmeticforasubstantiallysmallershared-memory
structionthatmultipliesapackedbitstringdirectlywithfloating- footprint.OnGPU,onlythequantizedqueryrepresentationneeds
tobestoredinsharedmemory(e.g.,0.5KBfora1,024-dimensional
pointvalues.Asaresult,astraightforwardimplementationmust
querywith4-bitquantization),makingthisapproachparticularly
| firstextracteach1-bitentryfromthebitstringxˆ |                   |     |                      |     | (atleastatbyte |     |                                                           |     |     |     |     |     |     |     |
| -------------------------------------------- | ----------------- | --- | -------------------- | --- | -------------- | --- | --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|                                              |                   |     |                      |     | b              |     | suitableforhigh-dimensionalsettingsorscenarioswhereshared |     |     |     |     |     |     |     |
| granularity)                                 | before performing |     | the multiplications. |     | Inspired       | by  |                                                           |     |     |     |     |     |     |     |
thebitwisedecompositioninRaBitQ[18],weinsteadadoptabit- memoryisthelimitingresource.
wiseinner-productcomputationthatcontrastswiththeclassical
Buildingontheoptimized
|     |     |     |     |     |     |     | 3.4.2 | FusedCluster-localSearchKernel. |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | ------------------------------- | --- | --- | --- | --- | --- | --- |
dimension-wiseapproach.Thekeyideaistoreorganizethecom-
inner-productcomputation,wenextdesignafusedcluster-local
putationsothateachinstructionprocessesmultipledimensions
searchkerneltoefficientlyexecutethetwo-stagedistanceestima-
atonceusingbitoperations.Toenablethis,wefirstquantizeeach
tionontheGPU.RecallinSection3.3.4thatthecluster-localsearch
| rotatedqueryinto𝐵 |     | -bitsignedintegersqˆ.BasedonSection2.2, |     |     |     |     |               |     |                 |     |                     |     |     |         |
| ----------------- | --- | --------------------------------------- | --- | --- | --- | --- | ------------- | --- | --------------- | --- | ------------------- | --- | --- | ------- |
|                   | q   |                                         |     |     |     |     | procedurefora |     | (query,cluster) |     | pair(whichfindsthe𝐾 |     |     | nearest |
thisquantizationisperformedonceperqueryandreusedacross
neighborsofthequerywithinthecluster)consistsoffourlogical
allprobedclusters,contributingnegligibleoverheadtotheoverall
steps,namely(1)1-bitestimateddistancecomputation,(2)candi-
searchpipeline.Withthequantizedquery,thetargetinnerproduct
dateselection,(3)refinedestimateddistancecomputation,and(4)
⟨xˆ ,q′⟩canberewrittenas:
| b   |     |     |     |     |     |     | in-blocktop-𝐾 |     | selection.Astraightforwardapproachistoimple- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | -------------------------------------------- | --- | --- | --- | --- | --- |
menteachofthethesestepsasaseparatekernel.However,dueto
⟨xˆ b ,q′⟩ ≈ Δ q·⟨xˆ b ,qˆ⟩. (8) datadependenciesbetweenconsecutivesteps,thisdesignrequires
where Δ q is the query quantization scale (step size) that maps launchingmultiplekernelssequentially,whereeachkernelloads
theinteger-domaininnerproductbacktoitsoriginalscale(e.g., itsinputsfromglobalmemoryandwritesintermediateresultsback
floating-point). toglobalmemory.Wenotethatsharedmemoryisscopedtoasin-
Let qˆ[𝑖] be the 𝑖th dimension of qˆ where 1 ≤ 𝑖 ≤ 𝐷 and glethreadblockandcannotbesharedacrossblocksindifferent
qˆ(𝑗)[𝑖] {0,1} bethe 𝑗thbitofqˆ[𝑖] where0 𝑗 < 𝐵 (please kernels, which means that it is necessary to store intermediate
| ∈   |     |     |     | ≤   | q   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
refertopresentationofqˆ inFigure1forillustration).Thebitwise resultsinglobalmemorybetweenstages.Moreover,whenwork-
decompositioncanberepresentedusingthefollowingequation: loadimbalancearisesacrossthreadblocks,laterkernelsmustwait
7

forthecompletionofearlierones,leadingtolong-taileffectsand memoryprimarilyforstoringintermediateinner-productresults,
underutilizationofstreamingmultiprocessors(SMs). candidatemetadata,andtop-𝐾 buffers.Exploitingthisproperty,
Toaddresstheseinefficiencies,wedesignafusedcluster-local wereuseshared-memoryregionsacrossstageswhenevertheirlife-
search kernel that integrates all four logical steps into a single timesdonotoverlap:(1)theshared-memoryregioninitiallyusedto
kernelexecution.Ratherthanlaunchingmultiplekernelsfordiffer- storetheLUTsorquantizedqueriesisreusedtostoreintermediate
entstages,thefuseddesignpropagatesintermediateresultsacross inner-productresultsduringdistancerefinement;(2)theshared
stagesusingon-chipmemory,enablingblock-levelsynchronization memoryallocatedacrossthefirstthreestagesisrepurposedasa
insteadofkernel-levelsynchronization.Thisdesignsignificantly sortingbufferformaintainingthecluster-localtop-𝐾 resultsin
reduceskernellaunchoverhead,global-memorytraffic,andsyn- thefinalstage.Bycarefullycoordinatingthesereusepatterns,the
chronizationcosts,especiallyunderworkloadimbalance. fusedkernelachievesasubstantiallysmallerpeakshared-memory
footprintthananaiveallocationthatreservesseparatebuffersfor
Kernel organization. The fused kernel adopts a block-centric
allstages.
executionmodel,whereeachblocktakesa(query,cluster)pairas
aninputandreturnsthecluster-local𝐾-nearestneighboursfor
thequery.Uponlaunch,ablockfirstloadsthequery-dependent 3.4.3 GPU-OrientedIndexLayout. Tosupportefficientexecution
representation into shared memory. Depending on the selected of the fused kernel, we co-design a GPU-oriented index layout
inner-productcomputationmethod(Section3.4.1),thisrepresenta- thatalignsdataorganizationwithcluster-localaccesspatterns.IVF-
tioniseithertheprecomputedlookuptables(LUTs)orthequantized RaBitQfollowsaflattenedIVForganizationinspiredbyCompressed
queryvectorusedforbitwiseinner-productevaluation.Afterthat, SparseRow(CSR)[5]techniques,wherevectorsbelongingtothe
threadsintheblockcollaborativelyscanthedatavectorsintheclus- same cluster are stored contiguously and indexed via an offset
terandcomputelowerboundsofthe1-bitestimateddistances.Each array.Buildingonthisbaselineorganization,wefurtherreorganize
threadprocessesoneormorevectorsandevaluatestheinnerprod- RaBitQcodesandauxiliarydatatoimprovedatalocality,memory
uctbetweenthequeryrepresentationandthe1-bitRaBitQcodes. coalescing,andcacheefficiencyduringGPUexecution.Thislayout
Basedontheinnerproductresults,the1-bitestimateddistance isco-designedwiththefusedkerneltoenablehigh-throughput
lowerboundsarecomputedandcomparedagainstaquery-specific searchonmodernGPUs.
threshold(thecurrent𝐾-thlargestdistanceamongthecandidates
foundsofaracrossclusters).Vectorswhoselowerboundsexceed
Stage-awaredatadecomposition.Tomatchthemulti-stageex-
ecutionofthefusedkernel,thedataassociatedwitheachcluster
thethresholdareprunedearly,whiletheremainingvectorsare
isdecomposedintomultiplecontiguousarraysaccordingtotheir
selectedascandidatesforfurtherrefinement.Then,thefusedkernel
usagepatterns.Specifically,weseparatetheRaBitQrepresenta-
performsdistancerefinementforthesurvivingcandidates.Since
tionintoshortcodes(themostsignificantbit,i.e.,1-bitRaBitQ
thenumberofcandidatestypicallyconstitutesasmallfractionof
codes)andlongcodes(ex-codes),whichareaccessedinthefiltering
theclustersize,weassigngroupsofthreadswithinawarptoco-
andrefinementstages,respectively.Correspondingly,auxiliaryfac-
operativelyprocesseachcandidate.Specifically,threadswithina
torsrequiredfordistanceestimationaresplitintoshort-factorand
warpjointlycomputetheinnerproductbetweenthequeryandthe
long-factorarrays,usedforcomputing1-bitdistancesandrefined
ex-codesofacandidate,whichhelpsamortizethecostofaccess-
ingadditionalcodebitsandachievesbetterworkloadbalancefor
distances,respectively.Inaddition,aPidarraystorestheunique
identifierofeachvectorwithinthecluster.Thisstage-awarede-
caseswherethenumberofcandidatesissmall.Usingtherefined
compositionimprovesdatalocalityandavoidsloadingunuseddata
inner-productresultstogetherwiththeassociatedauxiliaryfactors,
inearlystagesofthefusedkernel.
theblockcomputestherefinedestimateddistanceforthesecandi-
dates.Finally,eachblockconductsacluster-localtop-𝐾 selection
Interleavedlayoutfor1-bitcodes.Efficientinner-productcom-
usingsharedmemory.Afterallvectorsintheclusterhavebeen
putationinthefilteringstagerequireshighmemorybandwidth
processed,theblockwritesthecluster-localtop-𝐾 resultsbackto
whenaccessingthe1-bitRaBitQcodes.OnGPUs,globalmemory
globalmemoryforsubsequentmergingacrossclusters,andupdates
accessesareservicedviaalignedmemorytransactions(e.g.,32,64,
thequery-specificthresholdatomically.
or128bytes),andaccessesfromconsecutivethreadsinawarpcan
Shared-memorymanagementviastage-awarereuse.Akey becoalescedwhentheytargetadjacentaddresses.Toexploitthis
challengeofkernelfusionismanagingshared-memoryusageacross behavior,wedesignaninterleavedlayoutforthe1-bitcodes.Asil-
stageswhilepreservingsufficientSMresidency.UnlikeCPUpro- lustratedinFigure2,foraclustercontaining𝑛vectorsofdimension
gramsthatcanallocateandfreememorydynamically,theshared- 𝐷,the1-bitcodesaregroupedevery32dimensions(e.g.,dimensions
memoryfootprintofaGPUkernelmustbedeterminedatlaunch 1–32,33–64)andpackedinto32-bitunsignedintegerstomatch
time,asitdirectlyconstrainsthenumberofthreadblocksthatcan theGPUregisterwidth.Thestorageisinterleavedsuchthat,for
concurrentlyresideonanSM.Excessiveshared-memoryallocation eachgroupof32dimensions,thepackedcodesofall𝑛vectorsare
canthereforereduceoccupancyandlimitoverallthroughput.We storedcontiguouslybeforeproceedingtothenextgroup.Withthis
observethattheshared-memoryrequirementsofdifferentstages layout,threadswithinawarpaccessadjacent32-bitwordswhen
inthefusedkerneldonotfullyoverlapintime.Specifically,the processingthesamedimensiongroupacrossdifferentvectors.Asa
memory used to store the query-dependent representation (i.e., result,memoryaccessesarecoalescedinto128-bytetransactions
lookuptablesorquantizedqueryvectors)isonlyneededduringthe andfitwithinasingleL1cacheline,enablingefficientutilization
1-bitdistanceestimationstage,whilelaterstagesrequireshared ofGPUmemorybandwidthduringinner-productcomputation.
8

|     |     |     | 0 1 | 2   |     | nk-1 nk |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
Offsets
|     |           |     | 0 128 | 350 |     | Offset[nk-1] Total |     |     |                                   |     |     |     |     |
| --- | --------- | --- | ----- | --- | --- | ------------------ | --- | --- | --------------------------------- | --- | --- | --- | --- |
|     | (Indices) |     |       |     | ··· |                    |     |     | InterleavedDataLayoutforShortCode |     |     |     |     |
Start
|     | ShortCode | C[1]Data | C[2]Data |     | C[3]Data | C[nk]Data |     |          | xˆ         | xˆ       | xˆ           |     | xˆ         |
| --- | --------- | -------- | -------- | --- | -------- | --------- | --- | -------- | ---------- | -------- | ------------ | --- | ---------- |
|     |           |          |          |     |          | ···       |     | Dims1-32 | b , 1      | b , 2    | b , 3        |     | b , n      |
|     |           |          |          |     |          |           |     |          | [ 1- 3 2 ] | [ 1- 3 2 | ] [ 1- 3 2 ] | ··· | [ 1- 3 2 ] |
|     |           |          |          |     |          |           |     |          | xˆ         | xˆ       | xˆ           |     | xˆ         |
ShortFactors C[1]Data C[2]Data C[3]Data ··· C[nk]Data Dims33-64 b ,1 b ,2 b ,3 b , n
|     |          |          |          |     |          |           |     |     | [3 3 -6 4] | [3 3 -6 4] | [3 3 -6 4] | ··· | [3 3 - 6 4] |
| --- | -------- | -------- | -------- | --- | -------- | --------- | --- | --- | ---------- | ---------- | ---------- | --- | ----------- |
|     |          |          |          |     |          |           |     |     | ... ...    | ...        | ...        |     | ...         |
|     | LongCode | C[1]Data | C[2]Data |     | C[3]Data | C[nk]Data |     |     |            |            |            | ... |             |
···
|             |     |          |          |     |          |           |     |              | xˆ                   | xˆ                   | xˆ                   |     | xˆ                   |
| ----------- | --- | -------- | -------- | --- | -------- | --------- | --- | ------------ | -------------------- | -------------------- | -------------------- | --- | -------------------- |
|             |     |          |          |     |          |           |     | DimsD-31...D | [D- 3 b 1 , . 1 ..D] | [D- 3 b 1 , . 2 ..D] | [D- 3 b 1 , . 3 ..D] | ··· | [D- 3 b 1 , . n ..D] |
| LongFactors |     | C[1]Data | C[2]Data |     | C[3]Data | C[nk]Data |     |              |                      |                      |                      |     |                      |
···
|     |      |          |          |     |          |               |     |     | xˆb,1 | xˆb,2 | xˆb,3 | ··· | xˆb,n |
| --- | ---- | -------- | -------- | --- | -------- | ------------- | --- | --- | ----- | ----- | ----- | --- | ----- |
|     | Pids | C[1]Data | C[2]Data |     | C[3]Data | ··· C[nk]Data |     |     |       |       |       |     |       |
ContiguousmemoryforCluster2
|     |     |     | Figure2:DatalayoutforInvertedListsinIVF-RaBitQ.n |     |     |     |     | k   | isthenumberofclusters. |     |     |     |     |
| --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- |
Table1:Datasetsusedinevaluation.𝑁
isthetotalnumber compressdatabasevectorsintocompactcodes.Itprovidestwoop-
ofdatabasevectorsand𝐷isthenumberofdimensions. tions,namelyonewithrefinement(namedIVF-PQ(w/ref))andthe
otherwithoutrefinement(namedIVF-PQ(wo/ref)).IVF-PQ(w/ref)
re-evaluatesshortlistedcandidatesproducedbasedonthePQcodes
|     | Name |     | Type |     | 𝑵   | 𝑫 Size(GB) |     |     |     |     |     |     |     |
| --- | ---- | --- | ---- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
usingrawdatavectorstoimproverecall.ApartfromGPU-based
|     | ImageNet |     | Image | 1,281,167 |     | 512 2.44 |     |     |     |     |     |     |     |
| --- | -------- | --- | ----- | --------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
methodsthatarebasedonclustering,wealsoincludeCAGRA[40],a
|     | CodeSearchNet |     | Code | 1,374,067 |     | 768 3.93 |     |     |     |     |     |     |     |
| --- | ------------- | --- | ---- | --------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
state-of-the-artgraph-basedGPUANNSalgorithmthatconstructs
|     | GIST |     | Image | 1,000,000 |     | 960 3.58 |     |     |     |     |     |     |     |
| --- | ---- | --- | ----- | --------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
andsearchesfixed-degreeproximitygraphsfullyinparallel.For
|     | OpenAI-3072-1M |     | Text | 1,000,000 |     | 3072 11.44 |     |     |     |     |     |     |     |
| --- | -------------- | --- | ---- | --------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
CPU-basedmethods,weincludeRaBitQLib[16](whichimplements
|     | OpenAI-1536-5M |     | Text | 5,000,000 |     | 1536 28.61 |     |     |     |     |     |     |     |
| --- | -------------- | --- | ---- | --------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
IVF-RaBitQforANNSwithefficientSIMDinstructions).Among
|     | Wiki-all |     | Text | 10,000,000 |     | 768 28.64 |     |     |     |     |     |     |     |
| --- | -------- | --- | ---- | ---------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
thesecompetitors,IVF-PQandRaBitQLibprovidetheoptionfor
vectorquantization.ForIVF-PQ(w/ref)andIVF-PQ(wo/ref),we
choosethebestindexsettings(e.g.,quantizationdimensions,quan-
4 EXPERIMENTS tizationbits,andnumberofclusters)forsearchingatRecall=0.95to
evaluatethetime-accuracytradeoff.ForIVF-RaBitQandRaBitQLib,
4.1 ExperimentalSetup
wequantizeeachdimensionofvectorsto8bitsunlessmentioned
ExperimentalPlatform.TheGPU-basedexperimentsarecon- otherwise.ForRaBitQquantizationonGPU,weempiricallyset
ductedonamachineprovidedbyAmazonWebServices[2].The 𝑁 and𝑁 to64and32,respectively.
|     |     |     |     |     |     |     | coarse | fine |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | ---- | --- | --- | --- | --- | --- |
machineisequippedwithasingleNVIDIAL40SGPUwith48GB
|     |     |     |     |     |     |     | Benchmark. |     | All experiments |     | with GPU | are | conducted using |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --------------- | --- | -------- | --- | --------------- |
ofdevicememory,andanAMDEPYC7R13processorproviding
cuVSBench[43],anopen-sourcebenchmarkingsuitedeveloped
8virtualCPUcores.TheNVIDIAdriverversionis590.48.01with byNVIDIAforevaluatingapproximatenearestneighbor(ANN)
CUDA13.1.TheCPU-basedexperimentsareperformedonama-
algorithmsonGPUs.Itenablesfaircomparisonacrossmethodsby
chineequippedwithIntelXeonGold6418Hprocessorsand1TB
enforcingconsistentdataloading,querybatching,andperformance
ofmainmemory.BothmachinesrunUbuntu22.04LTS(x86_64).
measurementunderGPU-residentsettings.Wehaveextendedthe
Datasets.Weusesixmodernreal-worldhigh-dimensionalvector cuVSBenchframeworkbyintegratingourIVF-RaBitQintothecuVS
datasetstoevaluatetheperformance,asdetailedinTable1.These LibrarytoallowfaircomparisonofIVF-RaBitQwithotherGPU
datasetsaretakenfromthepopularANNSbenchmarksandreflect methodsunderunifiedworkloads.Unlessmentionedotherwise,we
real-worldANNSsearchscenarios[9,27,41,45].Thetypesinclude use𝑏𝑎𝑡𝑐ℎ𝑠𝑖𝑧𝑒 =104forthebenchmark.
| image(ImageNet[10]andGIST |     |     |     | [28]),code(CodeSearchNet[22]), |     |     |     |     |     |     |     |     |     |
| ------------------------- | --- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
andtext(OpenAI-3072-1M,OpenAI-1536-5M[41]andWiki-all[45]). 4.2 ExperimentalResults
Foreachdataset(exceptforWiki-all),weexclude10,000vectors
|      |             |     |                   |     |         |                     | 4.2.1 | GPUANNSSearchPerformance. |     |     | Inthissubsection,weevalu- |     |     |
| ---- | ----------- | --- | ----------------- | --- | ------- | ------------------- | ----- | ------------------------- | --- | --- | ------------------------- | --- | --- |
| from | the dataset |     | as query vectors, |     | and use | the rest of them as |       |                           |     |     |                           |     |     |
atetheGPU-basedANNsearchperformanceofIVF-RaBitQagainst
basedatavectorsforindexconstruction.ForWiki-all,thedataset otherrepresentativebaselines.ForIVF-RaBitQ,wereporttwodiffer-
includes10,000queryvectorsalready.
entGPUsearchmodes:IVF-RaBitQ(LUT)andIVF-RaBitQ(Bitwise),
Baselines.WecompareourmethodagainstseveralmodernANN whichcorrespondtotwodifferentinnerproductioncomputation
methods.ForGPU-basedmethods,wefirstchoosethewidelyused methods(recallSection3.4.1)usedinourfusedkernel.Ourcom-
clustering-basedmethods,IVF-FlatandIVF-PQ,implementedin petitorsincludeIVF-PQ(withandwithoutrefinement),IVF-Flat,
thecuVSLibrary[43].Thesemethodsarebuiltontheinverted andCAGRA.Figure3reportsthetime-accuracytrade-offforthese
file (IVF) index. [14] stores all database vectors in un- methodsonsixhigh-dimensionaldatasets.Theperformanceiseval-
IVF-Flat
compressedform.IVF-PQ[7]appliesproductquantization[28]to uatedinQPS(query-per-second),andtheaccuracyismeasuredby
9

|     |          | IVF-RaBitQ (Bitwise) | IVF-RaBitQ (LUT) | CAGRA IVF-PQ (w/ref) | IVF-PQ (wo/ref) | IVF-FLAT |               |     |
| --- | -------- | -------------------- | ---------------- | -------------------- | --------------- | -------- | ------------- | --- |
|     | ImageNet |                      | ImageNet         |                      | CodeSearchNet   |          | CodeSearchNet |     |
106
106
|     |     |     |     | 105 |     | 105 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 105 |     | 105 |     |     |     |     |     |     |
| SPQ |     | SPQ |     | SPQ |     | SPQ |     |     |
|     |     |     |     | 104 |     | 104 |     |     |
| 104 |     | 104 |     |     |     |     |     |     |
|     |     |     |     | 103 |     | 103 |     |     |
| 103 |     | 103 |     |     |     |     |     |     |
0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00
|     | Recall@10 |     | Recall@50 |     | Recall@10      |     | Recall@50      |     |
| --- | --------- | --- | --------- | --- | -------------- | --- | -------------- | --- |
|     | GIST      |     | GIST      |     | OpenAI-3072-1M |     | OpenAI-3072-1M |     |
105
|     |     | 105 |     | 105 |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
105
|     |     |         |     | 104 |     | 104 |     |     |
| --- | --- | ------- | --- | --- | --- | --- | --- | --- |
| SPQ |     | SPQ 104 |     | SPQ |     | SPQ |     |     |
104
|     |     |     |     | 103 |     | 103 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 103 |     | 103 |     |     |     |     |     |     |
|     |     |     |     | 102 |     | 102 |     |     |
0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00
|     | Recall@10      |     | Recall@50      |     | Recall@10 |     | Recall@50 |     |
| --- | -------------- | --- | -------------- | --- | --------- | --- | --------- | --- |
|     | OpenAI-1536-5M |     | OpenAI-1536-5M |     | Wiki-all  |     | Wiki-all  |     |
| 105 |                | 105 |                | 105 |           | 105 |           |     |
104
| SPQ 104 |     | SPQ |     | SPQ 104 |     | SPQ 104 |     |     |
| ------- | --- | --- | --- | ------- | --- | ------- | --- | --- |
| 103     |     | 103 |     |         |     |         |     |     |
|         |     |     |     | 103     |     | 103     |     |     |
| 102     |     | 102 |     |         |     |         |     |     |
0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00 0.80 0.85 0.90 0.95 1.00
|     | Recall@10 |     | Recall@50 |     | Recall@10 |     | Recall@50 |     |
| --- | --------- | --- | --------- | --- | --------- | --- | --------- | --- |
Figure3:Time–accuracytrade-offofANNsearchonrepresentativedatasets(log-scale).BitwiseandLUT denotethetwoGPU
inner-productmethodsusedbyIVF-RaBitQ,whilew/refineandw/orefineindicatewhetherdistancerefinementisenabledfor
IVF-PQ.
Recall@K(theratiooftruenearestneighborsfoundinthetop-𝐾 becomesmoreevidentonhigherrecall,whichhighlightstheadvan-
resultsreturnedbyanANNSalgorithm).Basedontheresults,we tageofcachereusewhileprobingmanyclustersforalargebatch
| havethefollowingobservations. |     |     |     | ofqueries. |     |     |     |     |
| ----------------------------- | --- | --- | --- | ---------- | --- | --- | --- | --- |
(1)Overallperformancetrends.IVF-RaBitQconsistentlyachieves (4)Bitwisevs.LUT-basedGPUkernels.Wefurtherinvestigate
highquerythroughputwhilemaintainingstrongrecallacrossall two inner product computation methods for IVF-RaBitQ: a bit-
datasets.Comparedwithallcompetitors,IVF-RaBitQprovidessub- wiseinner-productkernelandalookup-table(LUT)basedkernel.
stantially higher throughput at medium-to-high recall regimes Bothimplementationsachievehighperformanceacrossalldatasets.
(0.85–1). Asdimensionalityincreases,theLUT-basedkernelisboundedby
(2)ComparisonamongIVF-basedmethods.Acrossalldatasets, shared-memorycapacity,whereasthebitwiseformulationremains
IVF-RaBitQsignificantlyoutperformsIVF-PQintermsofthrough- lightweightandscalablewhichisreflectedbygapbetweenthetwo
put,especiallyathigherrecalltargets.AlthoughIVF-PQwithrefine- methodsontheOpenAI-3072-1Mdataset.Wenotethattherelative
ment(denotedasIVF-PQ(w/ref))improvesretrievalaccuracyby performanceofthesetwomethodsmayvarybasedonthememory
introducinganadditionalrefinementstage,itstillincursconsider- bandwidthandsharedmemorysizeofdifferentGPUs.
ablecomputationalandmemoryoverheadwhenusingrawvectors (5)Scalabilityacrossdatasetsizesanddimensionalities.Across
for reranking. In contrast, IVF-RaBitQ attains a more favorable datasetsrangingfrom1Mto10Mvectorsanddimensionsfrom512
efficiency–accuracybalancewithoutrelyingonrerankingofraw to3072,IVF-RaBitQmaintainsrobustperformanceandconsistent
vectors.Tobespecific,forRecall=0.95,IVF-RaBitQhas2.0×~31.4× throughputadvantages.
speedupcomparedtoIVF-PQwithoutrefinement(denotedasIVF-
Figure4showstheindexbuildtimefor
PQ(wo/ref)),and1.3×~5.3×speedupcomparedtoIVF-PQ(w/ref). 4.2.2 IndexBuildTime.
(3)ComparisonwithCAGRA.IVF-RaBitQdemonstratescompa- theindexesusedinSection4.2.1.ForallIVF-basedmethods,we
useone-tenthofthedatasetvectorstotraintheclustersandalign
rableorhigherthroughputthanCAGRAacrossmostdatasetsand
thenumberofclusterstobetrained.Also,wealigntheIVF-PQand
recallranges.IVF-RaBitQbenefitsfromcompressionwhileCAGRA
IVF-RaBitQtousethesamecompressionratioforquantization(i.e.,
workswithuncompresseddata.Onaverage,IVF-RaBitQ(Bitwise)
8bitsperdimension).WeobservethatIVF-RaBitQhasaveryshort
achievesaspeedupof1.8×,2.2×,3.3×comparedtoCAGRAfor
|     |     |     |     | index | build time across all | evaluated datasets. | When | compared |
| --- | --- | --- | --- | ----- | --------------------- | ------------------- | ---- | -------- |
recall=0.9,0.95,0.99@10,respectively.Theperformanceadvantage
withCAGRA,theproposedmethodattainsanaveragespeedup
10

|     |     |     |     | IVF-RaBitQ | CAGRA |     | IVF-PQ | IVF-FLAT |     |     |     |     |
| --- | --- | --- | --- | ---------- | ----- | --- | ------ | -------- | --- | --- | --- | --- |
ImageNet CodeSearchNet GIST OpenAI-3072-1M OpenAI-1536-5M Wiki-all
|                |     |     |     |     |     | 15.0 |     |     | 60  |     |     |     |
| -------------- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
| 5              |     |     |     | 5   |     |      |     |     |     |     |     |     |
| )s( emiT dliuB |     | 6   |     |     |     | 12.5 |     |     | 50  |     | 60  |     |
| 4              |     |     |     | 4   |     |      |     |     |     |     |     |     |
|                |     |     |     |     |     | 10.0 |     |     | 40  |     |     |     |
| 3              |     | 4   |     | 3   |     | 7.5  |     |     | 30  |     | 40  |     |
| 2              |     |     |     | 2   |     | 5.0  |     |     | 20  |     |     |     |
|                |     | 2   |     |     |     |      |     |     |     |     | 20  |     |
| 1              |     |     |     | 1   |     | 2.5  |     |     | 10  |     |     |     |
0 IVF-RaBitQ CAGRA IVF-PQ IVF-FLAT 0 IVF-RaBitQ CAGRA IVF-PQ IVF-FLAT 0 IVF-RaBitQ CAGRA IVF-PQ IVF-FLAT 0.0 IVF-RaBitQ CAGRA IVF-PQ IVF-FLAT 0 IVF-RaBitQ CAGRA IVF-PQ IVF-FLAT 0 IVF-RaBitQ CAGRA IVF-PQ IVF-FLAT
Figure4:Indexbuildtimeacrossdifferentdatasets.Eachsubplotcomparesbuildtimeacrossmethods.
|     |     |     | RAW vectors | IVF-RaBitQ | CAGRA | IVF-PQ (w/ref) |     | IVF-PQ (wo/ref) | IVF-FLAT |     |     |     |
| --- | --- | --- | ----------- | ---------- | ----- | -------------- | --- | --------------- | -------- | --- | --- | --- |
ImageNet CodeSearchNet GIST OpenAI-3072-1M OpenAI-1536-5M Wiki-all
| 3.0 |     | 5   |     |     |     | 15.0 |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
4
| 2.5        |     | 4   |     |     |     | 12.5 |     |     | 30  |     | 30  |     |
| ---------- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
| )BiG( eziS |     |     |     |     |     | 10.0 |     |     |     |     |     |     |
| 2.0        |     | 3   |     | 3   |     |      |     |     |     |     |     |     |
|            |     |     |     |     |     | 7.5  |     |     | 20  |     | 20  |     |
| 1.5        |     | 2   |     | 2   |     |      |     |     |     |     |     |     |
| 1.0        |     |     |     |     |     | 5.0  |     |     |     |     |     |     |
|            |     | 1   |     | 1   |     |      |     |     | 10  |     | 10  |     |
| 0.5        |     |     |     |     |     | 2.5  |     |     |     |     |     |     |
0.0 IVF-RaBitQ A f) Q (wo/ref) IVF-FLAT IVF-RaBitQ 0 A f) Q (wo/ref) IVF-FLAT IVF-RaBitQ 0 A f) Q (wo/ref) IVF-FLAT 0.0 IVF-RaBitQ A f) Q (wo/ref) IVF-FLAT IVF-RaBitQ 0 A f) Q (wo/ref) IVF-FLAT IVF-RaBitQ 0 A f) Q (wo/ref) IVF-FLAT
CA G R -PQ (w /r e CA G R -PQ (w /r e CA G R -PQ (w /r e CA G R -PQ (w /r e CA G R -PQ (w /r e CA G R -PQ (w /r e
|     | V F F -P |     | V F F -P | V F | F -P |     | V F | F -P | V   | F F -P |     | V F F -P |
| --- | -------- | --- | -------- | --- | ---- | --- | --- | ---- | --- | ------ | --- | -------- |
|     | I IV     |     | I IV     | I   | IV   |     | I   | IV   | I   | IV     |     | I IV     |
Figure5:Storagerequirementofdifferentindexingmethods.CAGRAandIVF-PQ(w/ref)requireRAWvectorsforrefinement,
thusRAWstorageisincluded.
of 7.7×. This is because CAGRA needs to spend more time on 4.2.4 Space-AccuracyTrade-off. IVF-RaBitQoffersflexibleandfine-
itsKNNgraphbuildingandgraphoptimizationprocedures.This grainedcontroloverthespace–accuracytrade-offbyofferingdiffer-
overheadbecomesincreasinglydominantasthedatasetscaleand entbitsforquantization.Inthissubsection,wefurtherinvestigate
dimensionalitygrow.ComparedwithotherIVF-basedmethods, thetrade-offbetweenstorageefficiencyandretrievalaccuracyby
IVF-RaBitQisoverallfasterthanIVF-PQ(witha4.4×speedupon varyingthebitsusedtoquantizeadimensioninIVF-RaBitQ.For
average)andisonlysuboptimaltoIVF-Flat.Ourproposedparallel theinnerproductcomputation,weusethebitwisemethod.Figure6
quantizationalgorithmtakes𝑂(1)roundstoquantizeavector,and showstheRecall–QPScurvesunderdifferentbitconfigurations
doesnotneedtotraincodebooksasIVF-PQdoes.Atthesametime, ontworepresentativedatasetswithdifferentdimensions.Fora
duetotheefficientquantizationofRaBitQ,ourmethodincurslower low-recallregion(e.g.,recalllessthan0.6),1-bitIVF-RaBitQhasa
memorywritevolumecomparedtoIVF-Flat.Whendatascalegrows, significantadvantageoverotherbitsettings.Thisisbecauseitdoes
thebottleneckofIVF-basedmethodsshiftsfromquantizationto notneedtoaccesstheex-codetorefinethe1-bitestimateddistance.
clustering,whichleadstoasmallerperformancegapbetweenIVF- Weobservethatfor𝐵 =5and𝐵 =7,IVF-RaBitQissufficientto
| RaBitQandIVF-PQ. |     |     |     |     |     |     | produce>0.95and0.99recall,respectively. |          |         |     |     |      |
| ---------------- | --- | --- | --- | --- | --- | --- | --------------------------------------- | -------- | ------- | --- | --- | ---- |
|                  |     |     |     |     |     |     |                                         |          | B=1 B=3 | B=5 | B=7 | B=9  |
|                  |     |     |     |     |     |     |                                         | ImageNet |         |     |     | GIST |
106
| 4.2.3                                                     | StorageRequirement. | Weanalyzethestoragerequirementof |     |     |     |     |     |     |     |     |     |     |
| --------------------------------------------------------- | ------------------- | -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| differentANNindices,whichisthetotalamountofdatathatmustbe |                     |                                  |     |     |     |     | 106 |     |     |     |     |     |
storedtosupportsearch,asshowninFigure5.WenotethatIVF-PQ SPQ SPQ
(wo/ref)usesthesamecompressionratio(8bitsperdimensionfor
105
| afloating-pointvector)asIVF-RaBitQ.CAGRA,IVF-Flat,andIVF- |     |     |     |     |     |     | 105 |     |     |     |     |     |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
PQwithrefinementneedtostoretherawdatavectorstosupport
|     |     |     |     |     |     |     | 0.5 | 0.6 0.7 | 0.8 0.9 | 1.0 0.5 | 0.6 | 0.7 0.8 0.9 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------- | ------- | --- | --------------- |
exactorrefineddistancecomputation,whichsignificantlyincreases Recall@10 Recall@10
theirstoragedemand.Comparedtothesemethods,IVF-RaBitQ
Figure6:Space-Performancetrade-offofIVF-RaBitQ.
onlyneedslessthan25%oftheirstoragerequirementtoachievea
| comparablerecall.Forexample,onWiki-all(10M,𝐷 |     |     |     | =768),IVF- |     |     |     |     |     |     |     |     |
| -------------------------------------------- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
RaBitQrequiresonly7.49gigabytesofstorage,whereasCAGRA 4.2.5 ComparisonwithCPU-basedCounterpart. Wefurthercom-
andIVF-PQ(w/ref)consumemorethan30GB.Comparedwith pareIVF-RaBitQ(GPU)withthebitwiseinnerproductcomputation
IVF-PQ(wo/ref),whichdoesnotstorerawvectors,IVF-RaBitQ methodanditscounterpartonCPU,forwhichweadopttheim-
achievesasimilarstoragefootprintwhiledeliveringsubstantially plementationfromtheRaBitQLib[16].TheCPUcounterpartis
higherrecallandquerythroughput.Thisadvantagecouldenable evaluated on an Intel Xeon Gold 6418H processor (24 cores, 48
deployinglarge-scaleANNsystemswithinthelimitedmemory threads),whichrepresentsahigh-performanceserver-classCPU
budgetofmodernGPUs. platform.Figure7reportsthetime-accuracytrade-offcurveson
11

106
105
104
0.80 0.85 0.90 0.95 1.00
Recall@10
SPQ
ImageNet
105
104
0.80 0.85 0.90 0.95 1.00
Recall@10
SPQ
IVF-RaBitQ (GPU) RaBitQLib (CPU) andtailorthetraversalstrategyforhigherGPUthroughput.CA-
GRA[40]proposesafastsearchalgorithmthatexploitssoftware
GIST
warp splitting and lightweight (forgettable) hash-table manage-
menttoimproveGPUutilization.BANG[48]targetsgraph-based
billion-scalesearch,whichintroducesaparallelmergealgorithm
andintegratesabloomfilterforacceleration.
Cluster-basedANNSonGPU.Whilemostgraph-basedmeth-
odsfocusonmaximizingthesearchthroughput,thecluster-based
methodsusuallydeliverfasterindexbuilds,lowermemoryusage,
Figure7:Time-accuracytrade-offcomparisonbetweenIVF-
andastrongbalancebetweenspeedandaccuracy[30].In2016,
RaBitQ(GPU)anditsCPUcounterpartfromRaBitQLib.The
Wiescholleket.al.proposedatwo-levelproductandvectorquan-
GPUimplementationrunsonanNVIDIAL40S,andtheCPU
tizationtreethatreducesthenumberofvectorcomparisonsfor
counterpartrunsonanIntelXeonGold6418H(24cores,48
ANNStreetraversal,whichfirstlydemonstratesGPUperformance
threads).
issuperiortoCPUperformanceinlarge-scaleANNproblems[50].
Later,FAISS[24]developsahigh-performancetop-𝐾 selectional-
tworepresentativedatasets.AtRecall@10=0.9,0.95,and0.99,IVF-
gorithmonaGPUandintegratesitwithIVF-PQforbillion-scale
RaBitQ(GPU)achievesaverageQPSspeedupsof13.0×,12.9×,and
ANNSsearchonmultipleGPUs.Chenet.al.proposedahierarchical
12.5×,respectivelyoveritsCPUcounterpart.Moreover,IVF-RaBitQ
invertedindexstructuregeneratedbylinequantizationtoenable
(GPU)achievesthesameaccuracy(recall)asitsCPUcounterpart,
morefine-grainedsearchinIVF[6].Recently,NvidiacuVS[43]fur-
demonstratingtheeffectivenessofourGPU-quantizationalgorithm.
theroptimizesLUTresidencyinsharedmemory(vialow-precision
LUTtypesandkernel-pathswitching),andemploysfused/early-
5 RELATEDWORK stopkernelsforIVF-PQ,makingitastate-of-the-artimplementation
Graph-BasedANNSonGPU.Graph-basedmethodstypically forIVF-PQonGPU.Rummy[56]andFusionANNS[46]bothfocus
buildaproximitygraphandanswerqueriesbyiterativelyexpand- onthescenariowhenvectordataislargerthantheGPUglobal
ingacandidatefrontierfromoneorafewentrypoints,whileprun- memory,whereRummyisbasedonpureIVFandFusionANNSfur-
ingcandidatesbasedondistancecomparisons.Abranchofrecent therextendsitwithProductQuantizationandanavigationgraph.
studyutilizesmodernGPUstoaccelerategraphindexconstruc- JUNO[33]utilizesray-tracingcoresonGPUforANNSacceleration,
tion.Graph-basedGPUNearestNeighbor(GGNN)[21]proposesa whichimplementsasparsity-andlocality-awaresearchalgorithmto
parallel,bottom-uphierarchicalconstructionalgorithmthatrecur- selectapproximatetop-𝐾neighbourcandidates.Incontrasttothese
sivelymergessmaller,independentsub-graphsintoafinalglobal GPUcluster-basedsoltionsthatprimarilybuildonIVF-Flat/IVF-PQ
index.Yuetal.[54]developedGGraphCon,aGPU-basedgraph (andtheircodebook-baseddistanceestimators),ourIVF-RaBitQ
constructionframeworkthatusesadivide-and-conquerframework integratesRaBitQandintroducesGPU-nativequantization,inner-
thatpartitionsthegraphbuildingintodifferentsmalltasks,anda product computation, and fused-kernel designs tailored to this
sort-basedstrategytobuildhigh-qualitygraphsinparallel.CAGRA method.
[40]designsasearchimplementation-centricproximitygraphcon-
structionmethodoptimizedforGPU,whichutilizesafixed-degree
structureandanovelrank-basedreorderingstrategytooptimize 6 CONCLUSION
graphconnectivity.Arecentwork,concurrentwithours,develops WepresentIVF-RaBitQ(GPU),anend-to-endGPU-nativeANNS
agraph-basedmethodcalledJasperforANNSonGPU,whichuses frameworkthatintegratesIVFpartitioningwithRaBitQquantiza-
RaBitQforvectorquantizationandsupportsdataupdates[37].We tion.IVF-RaBitQenablesfastindexbuild,high-throughputsearch,
notethatthisworkcomputestherescalingfactorontheCPU,while high recall, and compact storage by combining a scalable GPU
performingtherescalingandroundingontheGPU-anexecution quantizationpipeline,GPU-nativeinner-productcomputation,a
splitthatdistinguishesitfromourapproach.Tagore[32]integrates fusedcluster-localsearchkernel,andaGPU-orientedindexlayout.
atwo-phaseGNN-Descentalgorithmforrapidgraphinitialization WefurtherintegrateIVF-RaBitQintoNVIDIAcuVSandthecuVS
andaunifiedCollect-Filter-Store(CFS)frameworkwithspecialized benchpipelinetosupportreproducibleevaluationandfaircompar-
parallelkernelsforfastgraphedgepruningonGPU.Thegraph isonswithexistingGPUbaselines.Experimentsonvariousdatasets
indexusuallyoccupiesalotofspace,whereasfewmethodscan showthatIVF-RaBitQoffersastrongtrade-offfrontieracrossre-
achievehighrecallwithasmallindexsize. call,throughput,buildtime,andmemoryfootprint,especiallyin
Thegraph-basedANNSsearchalgorithmsworkcooperatively high-recallregimes.
withthegraphindex,andrecentGPUdesignsmainlyfocusonac-
celeratinggraphtraversalandcandidatemanagement(e.g.,priority
queues,visitedsets,andhash-table-basedfiltering)undermassive ACKNOWLEDGMENTS
parallelism.SONG[57]isthefirstworktoimplementgraph-based Wesincerelyappreciatetheinsightfuldiscussionsandconstruc-
ANNS search on GPU, adopting a three-stage pipeline with an tivesuggestionsprovidedbyArtemChirkin,AkiraNaruse,and
optimizedpriorityqueueandhashtablesforNSW[35].GGNN HiroyukiOotomoatNVIDIA,aswellasYutongGouandYuexuan
[21] and GANNS [54] further use hierarchical graph structures XuatNanyangTechnologicalUniversity.
12

REFERENCES [20] YutongGou,JianyangGao,YuexuanXu,andChengLong.2025.SymphonyQG:
[1] CeciliaAguerrebere,IshwarSinghBhati,MarkHildebrand,MarianoTepper, TowardsSymphoniousIntegrationofQuantizationandGraphforApproximate
andTheodoreWillke.2023. SimilaritySearchintheBlinkofanEyewith NearestNeighborSearch. Proc.ACMManag.Data3,1,Article80(Feb.2025),
26pages. https://doi.org/10.1145/3709730
| CompressedIndices.Proc.VLDBEndow.16,11(July2023),3433–3446. |     | https: |     |     |     |     |
| ----------------------------------------------------------- | --- | ------ | --- | --- | --- | --- |
//doi.org/10.14778/3611479.3611537 [21] FabianGroh,LukasRuppert,PatrickWieschollek,andHendrikP.A.Lensch.
2023.GGNN:Graph-BasedGPUNearestNeighborSearch.IEEETransactionson
| [2] AmazonWebServices,Inc.2026. | AmazonEC2G6eInstances. | https://aws. |     |     |     |     |
| ------------------------------- | ---------------------- | ------------ | --- | --- | --- | --- |
amazon.com/ec2/instance-types/g6e/. Accessed:2026-02-23. BigData9,1(2023),267–279. https://doi.org/10.1109/TBDATA.2022.3161156
[22] HamelHusain,Ho-HsiangWu,TiferetGazit,MiltiadisAllamanis,andMarc
[3] DavidArthurandSergeiVassilvitskii.2007. k-means++:theadvantagesof
Brockschmidt.2019.CodeSearchNetchallenge:Evaluatingthestateofsemantic
carefulseeding.InProceedingsoftheEighteenthAnnualACM-SIAMSymposium
onDiscreteAlgorithms(NewOrleans,Louisiana)(SODA’07).SocietyforIndustrial codesearch.arXivpreprintarXiv:1909.09436(2019).
[23] SuhasJayaramSubramanya,FnuDevvrit,HarshaVardhanSimhadri,Ravishankar
andAppliedMathematics,USA,1027–1035.
[4] FedorBorisyuk,SiddarthMalreddy,JunMei,YiqunLiu,XiaoyiLiu,Piyush Krishnawamy,andRohanKadekodi.2019.DiskANN:FastAccurateBillion-point
NearestNeighborSearchonaSingleNode.InAdvancesinNeuralInformationPro-
| Maheshwari,AnthonyBell,andKaushikRangadurai.2021. |     | VisRel:Media |     |     |     |     |
| ------------------------------------------------- | --- | ------------ | --- | --- | --- | --- |
cessingSystems,H.Wallach,H.Larochelle,A.Beygelzimer,F.d'Alché-Buc,E.Fox,
SearchatScale.InProceedingsofthe27thACMSIGKDDConferenceonKnowl-
(VirtualEvent,Singapore)(KDD’21).Asso- andR.Garnett(Eds.),Vol.32.CurranAssociates,Inc.https://proceedings.neurips.
edgeDiscovery&DataMining cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf
| ciationforComputingMachinery,NewYork,NY,USA,2584–2592. |     | https: |     |     |     |     |
| ------------------------------------------------------ | --- | ------ | --- | --- | --- | --- |
//doi.org/10.1145/3447548.3467081 [24] JeffJohnson,MatthijsDouze,andHervéJégou.2021. Billion-ScaleSimilarity
|     |     |     | SearchwithGPUs.IEEETransactionsonBigData7,3(2021),535–547. |     |     | https: |
| --- | --- | --- | ---------------------------------------------------------- | --- | --- | ------ |
[5] AydinBuluç,JeremyT.Fineman,MatteoFrigo,JohnR.Gilbert,andCharlesE.
//doi.org/10.1109/TBDATA.2019.2921572
Leiserson.2009.Parallelsparsematrix-vectorandmatrix-transpose-vectormul-
tiplicationusingcompressedsparseblocks.InProceedingsoftheTwenty-First [25] WilliamBJohnsonandJoramLindenstrauss.1984. ExtensionsofLipschitz
mappingsintoaHilbertspace26.Contemporarymathematics26(1984),28.
AnnualSymposiumonParallelisminAlgorithmsandArchitectures(Calgary,AB,
Canada)(SPAA’09).AssociationforComputingMachinery,NewYork,NY,USA, [26] js1010.2021.cuhnsw:CUDAimplementationofHierarchicalNavigableSmall
|     |     |     | WorldGraphalgorithm.https://github.com/js1010/cuhnsw. |     |     | GitHubrepository, |
| --- | --- | --- | ----------------------------------------------------- | --- | --- | ----------------- |
233–244. https://doi.org/10.1145/1583991.1584053
Accessed:2026-02-01.
[6] WeiChen,JincaiChen,FuhaoZou,Yuan-FangLi,PingLu,QiangWang,andWei
Zhao.2019. Vectorandlinequantizationforbillion-scalesimilaritysearch [27] Elias Jääsaari, Ville Hyvönen, Matteo Ceccarello, Teemu Roos, and Mar-
|                                                          |     |        | tin Aumüller. 2025. | VIBE: Vector | Index Benchmark | for Embeddings. |
| -------------------------------------------------------- | --- | ------ | ------------------- | ------------ | --------------- | --------------- |
| onGPUs. FutureGenerationComputerSystems99(2019),295–307. |     | https: |                     |              |                 |                 |
//doi.org/10.1016/j.future.2019.04.033 arXiv:2505.17810[cs.LG] https://arxiv.org/abs/2505.17810
[28] HerveJégou,MatthijsDouze,andCordeliaSchmid.2011.ProductQuantization
[7] ArtemChirkin,AkiraNaruse,TamásFehér,YongWang,andCoreyNolet.2024.
forNearestNeighborSearch.IEEETransactionsonPatternAnalysisandMachine
AcceleratingVectorSearch:NVIDIAcuVSIVF-PQ(Part1,DeepDive).NVIDIA
TechnicalBlog. https://developer.nvidia.com/blog/accelerating-vector-search- Intelligence33,1(2011),117–128. https://doi.org/10.1109/TPAMI.2010.57
[29] SukjinKim,SeongyeonPark,SiUngNoh,JungukHong,TaeheeKwon,Hunseong
nvidia-cuvs-ivf-pq-deep-dive-part-1/
[8] YannisChronis,HelenaCaminal,YannisPapakonstantinou,FatmaÖzcan,and Lim,andJinhoLee.2025.PathWeaver:ahigh-throughputmulti-GPUsystem
forgraph-basedapproximatenearestneighborsearch.InProceedingsofthe2025
AnastasiaAilamaki.2025.FilteredVectorSearch:State-of-the-ArtandResearch
Opportunities.Proc.VLDBEndow.18,12(Aug.2025),5488–5492. https://doi. USENIXConferenceonUsenixAnnualTechnicalConference(Boston,MA,USA)
org/10.14778/3750601.3750700 (USENIXATC’25).USENIXAssociation,USA,Article89,17pages.
|     |     |     | [30] JackLi.2025. UnderstandingIVFVectorIndex:HowItWorksandWhento |     |     |     |
| --- | --- | --- | ----------------------------------------------------------------- | --- | --- | --- |
[9] CSE,CUHK.2018.GQRDatasets.https://www.cse.cuhk.edu.hk/systems/hash/
gqr/datasets.html. Accessed:2026-01-29. ChooseItOverHNSW.MilvusBlog. https://milvus.io/blog/understanding-ivf-
vector-index-how-It-works-and-when-to-choose-it-over-hnsw.mdAccessed:
[10] JiaDeng,WeiDong,RichardSocher,Li-JiaLi,KaiLi,andLiFei-Fei.2009.Im-
| ageNet:Alarge-scalehierarchicalimagedatabase.In2009IEEEConferenceon |     |     | 2026-01-03. |     |     |     |
| ------------------------------------------------------------------- | --- | --- | ----------- | --- | --- | --- |
ComputerVisionandPatternRecognition.248–255. https://doi.org/10.1109/CVPR. [31] WenLi,YingZhang,YifangSun,WeiWang,MingjieLi,WenjieZhang,and
XueminLin.2020.ApproximateNearestNeighborSearchonHighDimensional
2009.5206848
[11] JacobDevlin,Ming-WeiChang,KentonLee,andKristinaToutanova.2019.BERT: Data—Experiments,Analyses,andImprovement.IEEETransactionsonKnowl-
|     |     |     | edgeandDataEngineering32,8(2020),1475–1488. |     | https://doi.org/10.1109/TKDE. |     |
| --- | --- | --- | ------------------------------------------- | --- | ----------------------------- | --- |
Pre-trainingofDeepBidirectionalTransformersforLanguageUnderstanding.
| arXiv:1810.04805[cs.CL] | https://arxiv.org/abs/1810.04805 |     | 2019.2909204 |     |     |     |
| ----------------------- | -------------------------------- | --- | ------------ | --- | --- | --- |
[32] ZhonggenLi,XiangyuKe,YifanZhu,BochengYu,BaihuaZheng,andYunjunGao.
[12] XinLunaDong.2024.TheJourneytoAKnowledgeableAssistantwithRetrieval-
2025.ScalableGraphIndexingusingGPUsforApproximateNearestNeighbor
AugmentedGeneration(RAG).InProceedingsofthe17thACMInternational
ConferenceonWebSearchandDataMining(Merida,Mexico)(WSDM’24).Asso- Search.Proc.ACMManag.Data3,6,Article360(Dec.2025),27pages. https:
//doi.org/10.1145/3769825
| ciationforComputingMachinery,NewYork,NY,USA,4. |     | https://doi.org/10. |     |     |     |     |
| ---------------------------------------------- | --- | ------------------- | --- | --- | --- | --- |
1145/3616855.3638207 [33] ZihanLiu,WentaoNi,JingwenLeng,YuFeng,CongGuo,QuanChen,Chao
|     |     |     | Li,MinyiGuo,andYuhaoZhu.2024. | JUNO:OptimizingHigh-Dimensional |     |     |
| --- | --- | --- | ----------------------------- | ------------------------------- | --- | --- |
[13] MingDu,ArnauRamisa,AmitKumarKC,SampathChanda,MengjiaoWang,
ApproximateNearestNeighbourSearchwithSparsity-AwareAlgorithmandRay-
NeelakandanRajesh,ShashaLi,YingchuanHu,TaoZhou,NagashriLakshmi-
narayana,SonTran,andDougGray.2022. AmazonShoptheLook:AVisual TracingCoreMapping.InProceedingsofthe29thACMInternationalConferenceon
SearchSystemforFashionandHome.InProceedingsofthe28thACMSIGKDD ArchitecturalSupportforProgrammingLanguagesandOperatingSystems,Volume
ConferenceonKnowledgeDiscoveryandDataMining(WashingtonDC,USA) 2(LaJolla,CA,USA)(ASPLOS’24).AssociationforComputingMachinery,New
|     |     |     | York,NY,USA,549–565. | https://doi.org/10.1145/3620665.3640360 |     |     |
| --- | --- | --- | -------------------- | --------------------------------------- | --- | --- |
(KDD’22).AssociationforComputingMachinery,NewYork,NY,USA,2822–2830.
|     |     |     | [34] MikkoI.MalinenandPasiFränti.2014. |     | BalancedK-MeansforClustering.In |     |
| --- | --- | --- | -------------------------------------- | --- | ------------------------------- | --- |
https://doi.org/10.1145/3534678.3539071
[14] TamásFehér,ArtemChirkin,ChristinaZhang,andMaheshDoijade.2023.Accel- ProceedingsoftheJointIAPRInternationalWorkshoponStructural,Syntactic,and
StatisticalPatternRecognition-Volume8621(Joensuu,Finland)(S+SSPR2014).
eratedVectorSearch:ApproximatingwithNVIDIAcuVSInvertedIndex.NVIDIA
TechnicalBlog. https://developer.nvidia.com/blog/accelerated-vector-search- Springer-Verlag,Berlin,Heidelberg,32–41. https://doi.org/10.1007/978-3-662-
44415-3_4
approximating-with-nvidia-cuvs-ivf-flat/
[35] YuryMalkov,AlexanderPonomarenko,AndreyLogvinov,andVladimirKrylov.
[15] CongFu,ChaoXiang,ChangxuWang,andDengCai.2019.Fastapproximate
nearestneighborsearchwiththenavigatingspreading-outgraph.Proc.VLDB 2014.Approximatenearestneighboralgorithmbasedonnavigablesmallworld
|                                                                     |                                          |        | graphs.InformationSystems45(2014),61–68. |     | https://doi.org/10.1016/j.is.2013. |     |
| ------------------------------------------------------------------- | ---------------------------------------- | ------ | ---------------------------------------- | --- | ---------------------------------- | --- |
| Endow.12,5(Jan.2019),461–474.                                       | https://doi.org/10.14778/3303753.3303754 |        |                                          |     |                                    |     |
| [16] JianyangGao,YutongGou,YuexuanXu,JifanShi,ZhonghaoYang,andCheng |                                          |        | 10.006                                   |     |                                    |     |
|                                                                     |                                          |        | [36] YuA.MalkovandD.A.Yashunin.2020.     |     | EfficientandRobustApproximate      |     |
| Long.2025.TheRaBitQLibrary.InThe1stWorkshoponVectorDatabases.       |                                          | https: |                                          |     |                                    |     |
//openreview.net/forum?id=OeZHhOsFir NearestNeighborSearchUsingHierarchicalNavigableSmallWorldGraphs.
[17] JianyangGao,YutongGou,YuexuanXu,YongyiYang,ChengLong,andRaymond IEEETrans.PatternAnal.Mach.Intell.42,4(April2020),824–836. https://doi.
org/10.1109/TPAMI.2018.2889473
Chi-WingWong.2025.PracticalandAsymptoticallyOptimalQuantizationof
High-DimensionalVectorsinEuclideanSpaceforApproximateNearestNeighbor [37] HunterMcCoy,ZikunWang,andPrashantPandey.2026. GPU-Accelerated
|                                                            |     |        | ANNS:QuantizedforSpeed,BuiltforChange. |     | arXiv:2601.07048[cs.DB] | https: |
| ---------------------------------------------------------- | --- | ------ | -------------------------------------- | --- | ----------------------- | ------ |
| Search.Proc.ACMManag.Data3,3,Article202(June2025),26pages. |     | https: |                                        |     |                         |        |
| //doi.org/10.1145/3725413                                  |     |        | //arxiv.org/abs/2601.07048             |     |                         |        |
[18] JianyangGaoandChengLong.2024. RaBitQ:QuantizingHigh-Dimensional [38] JamesBMcQueen.1967.Somemethodsofclassificationandanalysisofmulti-
variateobservations.InProc.of5thBerkeleySymposiumonMath.Stat.andProb.
VectorswithaTheoreticalErrorBoundforApproximateNearestNeighbor
| Search.Proc.ACMManag.Data2,3,Article167(May2024),27pages. |     | https: | 281–297.                     |                                  |     |        |
| --------------------------------------------------------- | --- | ------ | ---------------------------- | -------------------------------- | --- | ------ |
|                                                           |     |        | [39] NVIDIACorporation.2026. | cuVSBenchmark—cuVSdocumentation. |     | https: |
//doi.org/10.1145/3654970
[19] GoogleAI.2024.Embeddings|GeminiAPI|GoogleAIforDevelopers.https: //docs.rapids.ai/api/cuvs/stable/cuvs_bench/. Accessed:2026-02-26.
[40] HiroyukiOotomo,AkiraNaruse,CoreyNolet,RayWang,TamasFeher,andYong
//ai.google.dev/gemini-api/docs/embeddings. Accessed:2026-02-01.
|     |     |     | Wang.2024. CAGRA:HighlyParallelGraphConstructionandApproximate |     |     |     |
| --- | --- | --- | -------------------------------------------------------------- | --- | --- | --- |
NearestNeighborSearchforGPUs.In2024IEEE40thInternationalConference
13

onDataEngineering(ICDE).IEEEComputerSociety,LosAlamitos,CA,USA, [50] PatrickWieschollek,OliverWang,AlexanderSorkine-Hornung,andHendrik
4236–4247. https://doi.org/10.1109/ICDE60146.2024.00323 P.A.Lensch.2016.EfficientLarge-ScaleApproximateNearestNeighborSearch
[41] OpenAI.2024.NewembeddingmodelsandAPIupdates.https://openai.com/ ontheGPU.In2016IEEEConferenceonComputerVisionandPatternRecognition
index/new-embedding-models-and-api-updates/. Accessed:2026-01-29. (CVPR).2027–2035. https://doi.org/10.1109/CVPR.2016.223
[42] AlecRadford,JongWookKim,ChrisHallacy,AdityaRamesh,GabrielGoh, [51] Wikipediacontributors.2024.Wikipedia:Pageviewstatistics—Wikipedia,The
SandhiniAgarwal,GirishSastry,AmandaAskell,PamelaMishkin,JackClark, FreeEncyclopedia.https://en.wikipedia.org/wiki/Wikipedia:Pageview_statistics.
GretchenKrueger,andIlyaSutskever.2021.LearningTransferableVisualModels Accessed:2026-02-01.
FromNaturalLanguageSupervision. arXiv:2103.00020[cs.CV] https://arxiv. [52] JingyiXi,ChenghaoMo,BenKarsin,ArtemChirkin,MingqinLi,andMinjia
org/abs/2103.00020 Zhang.2025.VecFlow:AHigh-PerformanceVectorDataManagementSystem
[43] RAPIDSAI.[n.d.].rapidsai/cuvs:cuVS–alibraryforvectorsearchandclustering forFiltered-SearchonGPUs. Proc.ACMManag.Data3,4,Article271(Sept.
ontheGPU. GitHubrepository. https://github.com/rapidsai/cuvs Accessed: 2025),27pages. https://doi.org/10.1145/3749189
2026-01-03. [53] YuxiangYang,ShiwenChen,YangshenDeng,andBoTang.2025.ParaGraph:
[44] RAPIDSAI.2025. K-Means—cuVSC++APIDocumentation(stable25.12). AcceleratingGraphIndexingthroughGPU-CPUParallelProcessingforEfficient
RAPIDScuVSdocumentation. https://docs.rapids.ai/api/cuvs/stable/cpp_api/ Cross-modalANNS.InProceedingsofthe21stInternationalWorkshoponData
cluster_kmeans/Accessed:2026-01-26. ManagementonNewHardware(DaMoN’25).AssociationforComputingMachin-
[45] RAPIDSTeam.2024. Wiki-allDataset—cuVSDocumentation. https://docs. ery,NewYork,NY,USA,Article7,10pages. https://doi.org/10.1145/3736227.
rapids.ai/api/cuvs/stable/cuvs_bench/wiki_all_dataset/. Accessed:2026-01-29. 3736237
[46] BingTian,HaikunLiu,YuhangTang,ShihaiXiao,ZhuohuiDuan,XiaofeiLiao, [54] YuanhangYu,DongWen,YingZhang,LuQin,WenjieZhang,andXueminLin.
HaiJin,XuecangZhang,JunhuaZhu,andYuZhang.2025. Towardshigh- 2022.GPU-acceleratedProximityGraphApproximateNearestNeighborSearch
throughputandlow-latencybillion-scalevectorsearchviaCPU/GPUcollabora- andConstruction.In2022IEEE38thInternationalConferenceonDataEngineering
tivefilteringandre-ranking.InProceedingsofthe23rdUSENIXConferenceonFile (ICDE).552–564. https://doi.org/10.1109/ICDE53745.2022.00046
andStorageTechnologies(SantaClara,CA,USA)(FAST’25).USENIXAssociation, [55] JingrongZhang,AkiraNaruse,XipengLi,andYongWang.2023.ParallelTop-K
USA,Article11,15pages. AlgorithmsonGPU:AComprehensiveStudyandNewMethods.InProceedings
[47] DanVanderkam,RobSchonberger,HenryRowley,andSanjivKumar.2013. oftheInternationalConferenceforHighPerformanceComputing,Networking,
NearestNeighborSearchinGoogleCorrelate. TechnicalReport.Google. http: StorageandAnalysis(Denver,CO,USA)(SC’23).AssociationforComputing
//www.google.com/trends/correlate/nnsearch.pdf Machinery,NewYork,NY,USA,Article76,13pages. https://doi.org/10.1145/
[48] KarthikVenkatasubba,SaimKhan,SomeshSingh,HarshaVardhanSimhadri,and 3581784.3607062
JyothiVedurada.2025. BANG:Billion-ScaleApproximateNearestNeighbour [56] ZiliZhang,FangyueLiu,GangHuang,XuanzheLiu,andXinJin.2024.Fastvector
SearchUsingaSingleGPU.IEEETransactionsonBigData11,06(Dec.2025), queryprocessingforlargedatasetsbeyondGPUmemorywithreorderedpipelin-
3142–3157. https://doi.org/10.1109/TBDATA.2025.3581085 ing.InProceedingsofthe21stUSENIXSymposiumonNetworkedSystemsDesign
[49] HuiWang,Wan-LeiZhao,XiangxiangZeng,andJianyeYang.2021.Fastk-NN andImplementation(SantaClara,CA,USA)(NSDI’24).USENIXAssociation,USA,
GraphConstructionbyGPUbasedNN-Descent.InProceedingsofthe30thACM Article2,18pages.
InternationalConferenceonInformation&KnowledgeManagement(VirtualEvent, [57] WeijieZhao,ShulongTan,andPingLi.2020. SONG:ApproximateNearest
Queensland,Australia)(CIKM’21).AssociationforComputingMachinery,New NeighborSearchonGPU.In2020IEEE36thInternationalConferenceonData
York,NY,USA,1929–1938. https://doi.org/10.1145/3459637.3482344 Engineering(ICDE).1033–1044. https://doi.org/10.1109/ICDE48307.2020.00094
14