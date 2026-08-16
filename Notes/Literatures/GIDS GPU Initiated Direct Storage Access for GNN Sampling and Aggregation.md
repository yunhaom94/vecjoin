# GIDS

**Source**: GIDS.pdf
**Format**: .pdf

---

GIDS: Accelerating Sampling and Aggregation Operations in
GNN Frameworks with GPU Initiated Direct Storage Accesses
JeongminBrianPark VikramSharmaMailthody
UIUC NVIDIA
USA USA
jpark346@illinois.edu vmailthody@nvidia.com
ZaidQureshi Wen-meiHwu
NVIDIA NVIDIA/UIUC
USA USA
zqureshi@nvidia.com whwu@nvidia.com
ABSTRACT 1 INTRODUCTION
GraphNeuralNetworks(GNNs)areemergingasapowerfultoolfor Owingtotheirexpressivepower,GraphNeuralNetworks(GNNs)
learningfromgraph-structureddataandperformingsophisticated effectivelycapturetherichrelationalinformationembeddedamong
inferencetasksinvariousapplicationdomains.AlthoughGNNs inputnodesandedges,leadingtoimprovedgeneralizationperfor-
havebeenshowntobeeffectiveonmodest-sizedgraphs,training manceovertraditionalmachinelearningtechniques.Asaresult,
themonlarge-scale graphsremainsasignificant challengedue GNNshavegainedsignificantattentioninrecentyearsanddemon-
to the lack of efficient storage access and caching methods for stratedtheirefficacyingraph-basedmachinelearningapplications,
graphdata.ExistingframeworksfortrainingGNNsuseCPUsfor suchasnodeclassification[11,20,33,35],recommendation[7,27],
graphsamplingandfeatureaggregation,whilethetrainingand frauddetection[22,38,42,43],andlinkprediction[9,34,45].
updatingofmodelweightsareexecutedonGPUs.However,our Tocatertothisgrowinginterest,newopen-sourceframeworks
in-depthprofilingshowsCPUscannotachievethegraphsampling suchasPyTorchGeometric(PyG)[8],Spektral[10],andDeepGraph
andfeatureaggregationthroughputrequiredtokeepupwithGPUs. Library(DGL)[49]havebeendevelopedtoprovideoptimizedoper-
Furthermore,whenthegraphanditsembeddingsdonotfitinthe atorsrequiredbyGNNs,suchasmessage-passingforaggregating
CPUmemory,theoverheadintroducedbytheoperatingsystem,say featureinformationacrossrelatedgraphnodes,andgraph-specific
forhandlingpage-faults,causesgrossunder-utilizationofhardware neuralnetworkcomputationlayers.AlthoughGNNframeworks
andprolongedend-to-endexecutiontime. leverageGPUs’high-throughputtensoroperations,GNNtraining
Toaddresstheseissues,weproposetheGPUInitiatedDirect faceschallengesbeyonditscomputationalrequirement.Amajor
StorageAccess(GIDS)dataloader,toenableGPU-orientedGNN challengeisthefast-growinggraphdatasetsizesthatcannotfit
trainingforlarge-scalegraphswhileefficientlyutilizingallhard- intothelimitedGPUmemorycapacity.Toaddressthischallenge,
wareresources,suchasCPUmemory,storage,andGPUmemory. frameworkslikeDGLexploitUnifiedVirtualAddressing(UVA)by
TheGIDSdataloaderfirstaddressesmemorycapacityconstraints pinningboththegraphstructuredataandfeaturedataintotheCPU
by enabling GPU threads to directly fetch feature vectors from memory,thusenablingGPUkernelstoefficientlyperformsubgraph
storage.Then,weintroduceasetofinnovativesolutions,including extractionandfeatureaggregationwhilemakingzero-copyaccess
thedynamicstorageaccessaccumulator,constantCPUbuffer,and tothegraphdatafromtheCPUmemory[26].
GPUsoftwarecachewithwindowbuffering,tobalanceresourceuti- Forlarge-scalegraphsthatdonotfitintotheCPUmemory,the
lizationacrosstheentiresystemforimprovedend-to-endtraining UVAapproachisnolongersufficient.Thereareclassesoftraditional
throughput.OurevaluationusingasingleGPUonterabyte-scale solutionstosupportlarge-scaleGNNtraining:(a)multi-node/multi-
GNNdatasetsshowsthattheGIDSdataloaderacceleratestheover- GPU,(b)tiling,and(c)memory-mappedfiles.Leveragingmultiple
allDGLGNNtrainingpipelinebyupto582×whencomparedto nodesorGPUs[2,4,16,23,40]bypartitioningthegraphacrossthe
thecurrent,state-of-the-artDGLdataloader. nodes/GPUstosupportlarge-scaleGNNtrainingisanexpensiveap-
proach[48].Tiling[14,47]canbeusedtosupportlarge-scaleGNN
trainingbyleveraginggraphpartitioningtomovetilesofgraph
datainandoutoftheGPUmemory.Thisapproachshowspoorper-
ReferenceFormat: formanceduetorandomaccesspatternsandtheadditionalcostof
JeongminBrianPark,VikramSharmaMailthody,ZaidQureshi,
pre-processingtheinputdata.Finally,themostconvenientsolution
andWen-meiHwu.GIDS:AcceleratingSamplingandAggregation
totrainlarge-scalegraphdatasetsonasingleGPUisexploitingthe
OperationsinGNNFrameworkswithGPUInitiatedDirectStorage
memory-mappedfiletechnique,whichmapsthegraphdatastored
Accesses.PVLDB,17(6):1227-1240,2024.
ondisktotheGPU’svirtualaddressspace,enablingtheGPUto
doi:10.14778/3648160.3648166
accessthedatawithoutfirstloadingtheentiredatasetintomem-
ArtifactAvailability: ory.Previousstudies[21,28,32,50]extendedthememory-mapped
Thesourcecode,data,and/orotherartifactshavebeenmadeavailableat
https://github.com/jeongminpark417/GIDS.
4202
raM
6
]CD.sc[
2v48361.6032:viXra

fileapproachandleveragedthein-memorycachingmechanismto
mitigatethestorageaccessoverhead. CPU Memory GPU Memory GPU Memory GPU Memory Storage(SSD)
Despiteitsconceptualsimplicity,theuseofmemory-mapped Struc G t r u a r p e h D ata W B i u n f d fe o r w Software Cache Acc B u u m ff u e la r tor Feat T u a r b e l e D ata
filesinGNNtrainingfacesperformancechallengesduetotheheavy
softwareoverheadinhandlingpagefaultsanditsinabilitytotoler- UV P A CI v e ia No Enqueue Update Dequeue Fetch
a st t o e r l a o g n e g la la te te n n c c y y ,w in h c i u ch rre is d t d w u o ri t n o g th d r a e t e a o re rd tr e i r e s va o l f f m ro a m gn s i t t o u r d a e g l e o . n T g h e e r G S P a U m G p r li a n p g h E G n ID ab S l ? e Yes B W u i f n f 3 e d r o in w g Re C u a s lc e 3 u C la o t u e nt A F c e c t B u c u m h f f u F e r la r o t m or A w gg it r h e g B a a t M ion
t tr h a a i n ni t n h g e p D r R oc A e M ss. a T c h ce is ss is la d t u e e nc to y, s b p e a c r o se m a e n s d a i b rr o e t g tl u e l n a e r c g k ra in ph th d e a G ta N a N c- NoEn A o cc u e g s h s e S s S ? D Yes I B s u A f c fe cu r m em ul p a t t y o ? r No Is GIDS? No T M ra o in d i e n l g
Yes
cesspatternsandtheinabilityofthememory-mappedfileapproach 2 1 Yes
tooverlapthelatenciesoftheseaccesses,resultinginpooroverall A w gg i r t e h g C a P ti U o n Yes CP F U ea C tu o r n e s t in ant S M am e p rg le e d 1 Acc F u i m ll u u p la tor
Buffer Buffer? Node List Buffer
performance.InSection2.3,weshowthatwhenusingmemory-
Fetch No Dequeue Enqueue
mappedfiles,thesamplingandfeatureaggregationstagesofthe Traditional GNN
CPU Constant Operation + BaM
Buffer
G se N ve N re t l r y ai li n m in it g t p h i e p o e v li e n r e al d l o G m N i N na t t r e ai t n h i e ng ov p e e r r a fo ll r e m x a e n c c u e t . iontimeand CPU Memory GPU W B M i u n e f d f m e o r w or y G A P c U c B u M u m e ff u m e la r o t r o y r G G I N D N S O Ad p d er it a i t o i n o a n l
Data Structure
Inthispaper,weproposeanewapproachcalledGPUInitiated
Scope of
DirectStorageAccess(GIDS)dataloadertotacklethechallenges Operation
ofGNNtrainingonlarge-scalegraphsbyleveragingGNN-specific
characteristicstoefficientlyutilizealltheinvolvedhardwarere- Figure1:IllustrationoftheGNNtrainingprocesswiththe
sources(CPUmemory,storage,andGPUmemory). GIDSdataloaderortheBaMdataloader.
Figure1illustratestheGNNtrainingworkflowwiththeGIDS
dataloader.First,GIDSkeepsthefeaturedataofthegraphinstor-
age as the feature data typically accounts for the vast majority
ofthetotalgraphdatasetsizeforlarge-scalegraphs(seeTable4
fordetails).GIDSovercomesthelongstorageaccesslatencyby
leveragingBaM[31]toallowGPUthreadstodirectlyfetchfeature • Weintroduceanoveldynamicstorageaccessaccumula-
data,usingthemassiveGPUthread-levelparallelismtooverlap tor, which accurately estimates the required number of
thelatenciesofmanystorageaccesses.However,toachievethe overlappingstorageaccessrequeststoachievepeakSSD
peakSSDbandwidth,ensuringasufficientnumberofconcurrent bandwidthwiththeBaMsystem.Theaccumulatorauto-
storageaccessrequestsisacriticalprerequisite.Thenumberof maticallymaintainsasufficientnumberofstoragerequests
storageaccessrequestscanvarybasedonthesamplingparameters bydecouplingthegraphsamplingstagefromthetraining
orhardwareconfiguration.Tomaintainsufficientoverlappingstor- stageandallowingtheformertorunaheadofthelatter.
ageaccessesforanyenvironment,GIDSfeaturesadynamicstorage • Weconductananalysisofthelogicaldependenciesamong
accessaccumulator (1),anoveltechniquethatexploitstheinde- theoverallGNNtrainingpipelinestagesandproposean
pendencyofthegraphsamplingprocesstoautomaticallymerge innovativeoptimizationstrategynamedwindowbuffering.
iterationsbasedonthesystemhardwarespecification. ItenablestheGIDSdataloadertoforeseetheupcoming
Second,GIDSpinsthegraphstructuredata,whosesizeistyp- nodeaccesspatterntooptimizethecacheevictionpolicy.
icallytinycomparedtothefeaturedata,intheCPUmemoryto • WeincreasetheeffectivebandwidthoftheGIDSdataloader
enableGPUgraphsamplingviaUVAzero-datacopytransferto beyondthelimitedSSDbandwidthbyclassifyinghotnodes
avoidI/Oamplificationandcachepollution.Third,GIDSenables usingreversepagerankscores,storingthemintheconstant
users to reserve CPU memory for a constant CPU buffer (2) to CPUbuffer,andredirectingsomeofthestorageaccessesto
achievehigherfeatureaggregationeffectivebandwidthbyredirect- theCPUmemorywhenPCIebandwidthisunderutilized
ingaccessesfromstoragetotheconstantCPUbufferforhotnodes duetolimitedSSDbandwidth.
whenPCIebandwidthisnotfullyutilized.
Finally,GIDSallocatesGPUmemoryfortheBaMApplication- WedemonstratetheGIDSdataloader’seffectivenessandflexi-
DefinedSoftwareCachetostorefeaturedataforrecentlyaccessed bilitybymeasuringperformanceusingbillion-scaledatasetsthat
nodes to minimize the storage accesses. As a new contribution donotfitintheCPUmemory.TheresultsbasedontheNVIDIA
to the cache design, we introduce a novel window buffering (3) A100GPUsand512GBCPUmemorycapacityshowthattheGIDS
techniquethattakesadvantageofthetimingflexibilityofthegraph dataloaderachieves582×speedupinoveralltrainingoverthestate-
samplingprocesstoexploitlocalityacrossmini-batchesandfurther of-the-artGNNdataloader.
improveGPUcacheutilization.
Wemakethefollowingkeycontributionsinthispaper.
2 BACKGROUND
• WeanalyzethelimitationsoftheexistingGNNframeworks Inthissection,weprovideanoverviewofGNNmodels,followedby
whiletrainingonlargegraphdatasetsandshowthatthe anintroductiontomini-batchingandsampling-basedGNNtraining.
existingCPU-initiatedapproachcannotkeepupwiththe Wethenexplainthestate-of-the-artframeworkforlarge-scaleGNN
demandsofGPU-acceleratedGNNtraining. traininganditschallenges.

2.1 GraphNeuralNetworks(GNNs) Target node 1st layer sampled nodes 2nd layer sampled nodes
GraphNeuralNetworks(GNNs)haverecentlygainedprominence
Not sampled nodes Sampled nodes
insolvingmachinelearningproblemsbyincorporatinggraphstruc-
tureinformation[3,6,20,35].Thesenetworkstypicallyconsistof
multiplelayersandoperatethroughlayer-wisemessagepassing.
GivenagraphG(V,E),withvertexsetVandedgesetE,the
nodefeaturevectorsforeachvertex𝑣 ∈Varerepresentedas𝑥
𝑣
.
Thenodeembeddingofvertex𝑣atlayer𝑙 isdenotedasℎ(𝑙),with
𝑣
ℎ(0) initializedwith𝑣’sfeaturevector𝑥 .TheGNNupdatesthe
𝑣 𝑣
nodeembeddingsusingtheequation:
ℎ
𝑣
(𝑙+1) =𝑓(ℎ
𝑣
(𝑙),ℎ
𝑤
(𝑙)
𝑤∈N(𝑣)
), (1)
Figure2:Asubgraphgeneratedbyauniformlyrandomse-
whereN(𝑣) definestheneighborhoodsetof𝑣,ℎ
𝑤
(𝑙) denotesthe lectionmethodfortwo-layerNeighborhoodSampling.
node embedding of the neighbor node𝑤 at layer𝑙, and 𝑓 is a
parameterizedupdatefunction.
thecomputationandmemoryfootprintbyrandomlysamplinga
Graphdataconsistsoftwocomponents:graphstructuredata
fixednumberofneighboringnodesratherthanincludingallnodes
and node feature data. The graph structure data represents the
in the graph. To ensure a sufficient level of randomness in the
edgesandnodesofthegraph,whilethenodefeaturedatarepre-
trainingprocess,GraphSAGEusesauniformlyrandomselection
sentsthefeatureembeddingsforeachnode.Sparsematrixformats
methodforneighborhoodsampling.Figure2illustratesanexample
suchasCoordinate(COO)formatandCompressedSparseColumn
ofneighborhoodsamplingwitha2-hopcomputationalgraph.In
(CSC)formatarecommonlyusedtostorethegraphstructuredata,
thisexample,thesamplingsizeissetto3,meaninguptothree
whereasthenodefeaturesaretypicallystoredinan𝑁 ×𝐷matrix,
neighboringnodesofthetargetnodeareselected.Withtwolayers,
where𝑁 isthetotalnumberofnodesinthegraph,and𝐷 isthe
thesampledsubgraphconsistsof10(1+3+6)verticesand9edges.
dimensionofeachnodefeature.Thesizeofeachnode’sfeaturecan
varygreatlybuttypicallyrangesfrom512Bto4KB.Forlarge-scale 2.2.3 NodeFeatureAggregation. Thenodefeaturesforthesampled
graphswithbillionsofnodes,thesizeofthenodefeaturedatacan subgraphofamini-batchmustbeaggregated,orgathered,before
reachseveraltensofterabytes.Asaresult,managingthenode training on the mini-batch can start. For smaller graphs whose
featuredataforlarge-scaleGNNtrainingwithlimitedmemory nodefeaturedatacanfitintotheCPUmemory,theentirefeature
capacityisachallengingtask. dataisfirstloadedintotheCPUmemory.Thenodefeaturesfor
eachmini-batch’ssampledsubgrapharegatheredfromtheCPU
2.2 GNNTrainingPipeline memoryandtransferredintotheGPUmemory.Incaseswhere
GNNtrainingonlargegraphdatasetsinvolvesmainlyfourstages: nodefeaturedatafortheoriginalgraphexceedstheCPUmemory
graphsampling,featureaggregation,datatransfer,andmodeltrain- capacity,thecurrentstate-of-the-artapproach[19,49]usesthe
ing. Mini-batch training is commonly used in these models for CPUtofirstgatherthenodefeaturesofthesampledsubgraphfrom
scalabilityandcomputationalefficiency[18,29,41].Inthissection, storageintoabufferintheCPUmemory,andthentransferthe
webrieflydescribethemini-batchingtechniqueandeachkeystage bufferedfeaturedatafromtheCPUmemorytotheGPUmemory.
oftheGNNtrainingpipeline.
2.3 LimitationofExistingGNNFrameworks
2.2.1 Mini-batching. Mini-batchingofGNNmodelsinvolvessplit-
State-of-the-artGNNframeworks,suchasDGL[49]andPyG[8],
tingthegraphintosmallersub-graphsandtrainingthenetwork
haveadoptedahybridCPU-GPUtrainingsystem,wheretheCPU
oneachofthesesub-graphs.Duringeachiterationofthetrain-
isresponsiblefordatapreparation,andtheGPUhandlesthemodel
ingprocess,abatchofsub-graphsisloadedintoGPUmemoryfor
training.Ourprofilingresultsshowthatsuchahybridtraining
computation.Thebatchsizemustbecarefullychosentoprevent
approachcanleadtosignificantunder-utilizationoftheGPUand
GPUmemoryoverflowduringtraining.Mini-batchingalsoexposes
suboptimaltrainingtime.Figure3comparesthenodefeaturevector
moreparallelismasmini-batchescanbeassignedtodifferentGPUs
requestgenerationrateofthedatapreparationstages,i.e.,nodesam-
duringtraining,whichsignificantlyimprovestrainingspeedand
plingandnodefeatureaggregation,oftheGNNtrainingpipeline
efficiencyandmakesitapopularapproachformanyGNNmodels.
whenthesestagesareexecutedontheCPUvs.ontheGPU.Asa
Previousstudieshavedemonstratedthattrainingneuralnetworks
reference,Figure3alsoshowsthatthetrainingkernelsrunningon
withmini-batchescanalsoleadtofasterconvergenceandbetter
theGPUcanconsumetheaggregatednodefeaturesatarateof29
optimizationcomparedtotrainingontheentiredataset[18,29,41].
millionrequestspersecond.TomaximizeGPUutilizationandmin-
2.2.2 NodeSampling. Mini-batchingalonecannotfullyaddress imizeGNNtrainingtimeforlargegraphs,therequestgeneration
thescalabilitylimitationswhenworkingwithlargegraphs.Even ratemustmatchorexceedtheconsumptionrate.
with small batch sizes, the training cost can still be substantial However,asshowninFigure3,thedatapreparationstagescan-
duetotheexponentialgrowthofmemoryfootprintwhencollect- not generate more than 4.1 million feature vector requests per
ingk-hopneighbors.GraphSAGE[11]introducedtheconceptof second,evenwhenusingmultiplethreads(16inthisexperiment
neighborhoodsamplingtotacklethisproblem.GraphSAGEreduces beyondwhichtherateplateaus)ontheCPU.Thisisbecausethe

samplingcomputationinvolvesrepeatedlytraversingthegraphand thatcannotfitintotheCPUmemory.Thekeyideaistoprovidea
accessingitsedgesandnodes,makingitdifficultfortheCPU,with notionofinfinitevirtualmemorybymemory-mappingthenode
itslimitedmemorybandwidthandthread-levelparallelism,tokeep featurevectorfilesintotheCPUvirtualaddressspaceandallow
upwiththeconsumptionrateoftheGPU-acceleratedtrainingker- the node feature aggregation computation on the CPU to page
nels.Incontrast,theGPUcangenerate77millionfeaturerequests faultwhentherequestedfeaturevectorisunavailableintheCPU
persecond,whichismorethansufficienttomatchtheconsumption memory.Figure4illustratestheGNNtrainingprocessusingthe
rateofthetrainingkernels.Basedontheseobservations,wewill approachofthememory-mappedfileintheDGLframework.Dur-
focusonGNNtrainingpipelinesthatoffloadthedatapreparation ingthenodefeatureaggregationstage,theCPUaccessesthenode
stagestotheGPUfortheremainderofthepaper. featuresmappedinitsvirtualmemoryspace,andtheOSpagefault
AchallengeinrunningthedatapreparationstagesontheGPUis handlerbringsthepagesthatcontaintheaccessedfeaturesfrom
thelimitedGPUmemorycapacitythatcanbesignificantlysmaller storageintotheCPUmemorywhenitmissesfromtheOSpage
thantheCPUmemory.Toaddressthischallenge,DGLrecently cache.Thememory-mappedfileapproach,alongwiththeCPU
introducedtheUVA-basedGNNtrainingtechnique[26],whichpins executionofnodefeatureaggregation,eliminatestheneedforload-
theentiregraphdataset(bothgraphandfeaturevectors)intheCPU ing/pinningtheentiredatasetintotheCPUmemoryaprioriand
memoryandenablesthegraphsamplingandfeatureaggregation onlybringsinthedatabeingactivelyusedon-demand.
kernelsrunningontheGPUtodirectlyaccessthegraphdataset
throughzero-copyaccesses.WhilethisapproachhelpstoscaleGNN
trainingtographdatasetswhosesizesexceedtheGPUmemory 1
capacity,itcannothandlelarge-scalegraphswhosesizessurpass
0.8
thecapacityoftheCPUmemorysinceallgraphdatamustbepinned
0.6
intheCPUmemoryfortheUVA-basedtechniquetowork.
0.4
0.2
0
CPU Sampling 4.1 IGB - Full IGBH - Full IGB - Full IGBH - Full ogbn-papers MAG240M
1TB RAM 512GB RAM
GPU Sampling 77.0
GPU Training 29.0
0 10 20 30 40 50 60 70 80 90
Million Requests per Second
Figure3:RequestgenerationrateofdatapreparationonCPU
and GPU, and request consumption rate on GPU on IGB-
smalldataset.TheCPUandGPUusedinthismeasurement
arelistedinTable1.
Graph Structure
Data File
Mini-batch Mini-batch
Sampled Features Sampled Features
Feature Data Data
File Page Transfer
Faults (PCIe)
CPU GPU
Storage
Figure4:IllustrationoftheGNNtrainingprocesswiththe
memory-mappingDGLdataloader
ExistingGNNframeworksfallbacktotheCPUforgraphsam-
plingandfeatureaggregationexecutiontosupportgraphdatasets
emiT
noitucexE
dezilamroN
Graph Sampling Aggregation Transfer Train
Figure5:GNNtrainingtimebreakdownforthebaselineDGL
dataloader for different graph datasets. The node feature
dataisaccessedfrommemory-mappedfiles,whilethegraph
structuredataisstoredintheCPUmemory.TheGraphSAGE
modelisusedastheGNNtrainingmodel.Thegraphproper-
tiesarelistedinTable2.
Unfortunately,thememory-mappedfileapproachmakesthe
nodefeatureaggregationbyfartheworstbottleneckoftheoverall
trainingpipeline.OurprofilingofeachstageintheGNNtraining
execution shows the iteration time is clearly dominated by the
samplingandnodeaggregationstages,asshowninFigure5.For
example,thetrainingstageisbarelyvisiblefortheIGB-Fulland
IGBH-Fullgraphs,thelargesttwographsusedinourevaluations.
Thisisbecause,forlarge-scalegraphs,theadditionalcostofpage
faultsexacerbatesthegapbetweenthedatapreparationthroughput
andmodeltrainingthroughput.Thus,thekeytoimprovingtheGNN
trainingperformancewhiletrainingonlargegraphsistodrastically
acceleratethesamplingandfeatureaggregationstages(i.e.,thedata
preparationstages).
Previousresearch[21,28,37,50]hasaimedtoenhancetheef-
ficiencyofnodeaggregationandsamplingstagesrunningonthe
CPUsbyusingspecificin-memorycachingmechanismstomini-
mizeredundantstorageaccessesand/orutilizingpipeliningtech-
niques to conceal graph sampling time. However, as shown in
Figure3,thedatapreparationstagesrunningontheCPUcannot
evengeneratenodefeaturerequestsatasufficientlyhighrateto
matchtheconsumptionrateofthetrainingkernels.Asuccessful
solutiontotheproblemofefficientlyaccessingnodefeaturevectors
fromthestorageon-demandmustallowthedatapreparationstages
runningontheGPUtomakedirectrequeststothestoragedevices.

Tothisend,wedeveloptheGIDSdataloaderbasedontheBaM[31] accesspatternthanthenodefeaturedata(512-4096B)accessedby
softwarestack,arecentlyreleasedresearchinfrastructurethaten- theaggregationprocess.Despitethegraphstructuredatabeing
ablesdirectstoragedeviceaccessbytheGPU,eliminatingtheover- pinnedinmemory,thisdoesnotleadtomemorycapacityissues
headofOSpagefaultsduringfeaturevectordataaccess. asitconstitutesonlyasmallfraction,typicallyaround5%ofthe
totaldatasetsize.ThestructuredatacomfortablyfitswithinCPU
2.4 TheBaMSystem memory,evenforterabyte-scalegraphs(refertoTable4).
TheBaMsystem[31]aimstotackletheproblemofstoragelatency TheGIDSdataloaderallocatesauser-configurableportionof
inbig-dataGPUapplications.ThekeyideabehindBaMistoallow CPUmemoryasaconstantbuffertopinasmallsubsetofthe
GPUthreadstohavedirectaccesstothestorage.Asamassive nodefeaturedata.Thisbufferredirectsstorageaccessesforhot
numberofGPUthreadscaninitiatedirectstorageaccesswithout nodestotheconstantCPUbuffer,amplifyingtheeffectivefeature
incurringCPU-GPUsynchronizationorCPUsoftwareoverhead, aggregationbandwidthbeyondtheavailableSSDbandwidth(Sec-
theGPUcantakefulladvantageofparallelismtohidelongstorage tion3.3).
accesslatency,enablingittoachievepeakstoragebandwidthwhen GPUMemory:TheGIDSdataloaderemploysBaM’sapplication-
thereisasufficientnumberofconcurrentstorageaccessrequests. definedsoftwarecachetotemporarilystorethefeaturedataofre-
However,straightforwardadoptionofBaMinthedataprepara- centlyaccessednodesintheGPUmemory.Thisreducesthenumber
tionstagesoftheGNNtrainingpipelineleavesmuchend-to-end ofstorageaccessesandimprovesfeatureaggregationperformance.
performance on the table due to the imbalanced use of critical Additionally,theGIDSdataloaderrunsthedatapreparationseveral
resourcesinthesystem.Therefore,weproposeasuiteofnovel iterationsaheadofthetrainingstageandmaintainsanodeaccess
techniquestoshifttheuseofhardwareresourcesduringthedata listforfutureiterationsinawindowbuffer,enhancingtheGPU
preparationstagesandsignificantlyimprovetheend-to-endGNN softwarecachehitratiobyleveragingGNN-specificdataaccess
trainingtime. patterns(Section3.4).
3 SYSTEMDESIGN 3.2 DynamicStorageAccessAccumulator
Toaddressthechallengesassociatedwithstate-of-the-artlarge- TheGIDSdataloaderleveragestheBaMsystemandtakesadvan-
scaleGNNtraining,wedesignandimplementtheGIDSdataloader, tageofthemassivethread-levelparallelismprovidedbyGPUsto
whichenablesfullyGPU-orientedGNNtrainingforlargegraphs effectivelyhandlestoragelatencyduringfeatureaggregation.To
andefficientlyutilizeshardwareresources.Thissectiondescribes achievethis,acriticalprerequisiteisensuringasufficientnumberof
thedesignandoptimizationoftheGIDSdataloader1. concurrentstorageaccessrequestsduringthefeatureaggregation
stagetomaximizetheutilizationofthepeakstoragethroughput.
3.1 GIDSDataloaderSystemOverview ThefeatureaggregationkernelviatheBaMsystemcanbedi-
videdintothreedistinctstages.Thefirststageistheinitialstage,
TheGIDSdataloaderimprovestheperformanceandscalabilityof
occurringfromthebeginningoffeatureaggregationuntilthefirst
GNNsbyefficientlyutilizingallavailablehardwareresourceswhen
dataisfetchedfromtheSSD.Thesecondstageisthesteady-state
aggregatingnodefeaturesthatcannotfitintotheCPUmemory.
stage,wheredatareceptionfromtheSSDreachesitspeakIOPs.
Thissectionprovidesadetailedbreakdownofhoweachresource
Thefinalstageistheterminationstage,thetimebetweenwhen
isharnessedtoaccelerateGNNdatapreparation.Theillustration
thelastaccessrequesttotheSSDishandledandtheconclusion
oftheGNNtrainingworkflowwiththeGIDSdataloaderisshown
ofthefeatureaggregationprocess.Duringtheinitialandtermi-
inFigure1.
nationstages,SSDbandwidthutilizationisalmostzero,whileit
GPU: AsdiscussedinSection2.3,theGIDSdataloadermoves
reachesitspeakduringthesteady-statestage.Usingthisinforma-
thedatapreparationstagesfromtheCPUtotheGPU.Asshown
tion,onecancalculatethenumberofoverlappingstorageaccess
inFigure3,therequestgenerationrateofthesamplingandnode
requestsrequiredtoachievepeakSSD’sreadthroughputbasedon
featureaggregationstagesrunningontheGPUexceedstheGPU
thefollowingmathematicalequations:
trainingkernelthroughput.
Storage: Toovercomememorycapacityconstraints,theGIDS
dataloaderstoresthefeaturedatainstorage.Toaddressthechal- 𝑁
𝑎𝑐𝑐𝑒𝑠𝑠
=𝐼𝑂𝑃
𝑎𝑐ℎ𝑖𝑒𝑣𝑒𝑑
∗(𝑇
𝑖
+𝑇
𝑠
+𝑇 𝑡)∗𝑁
𝑠𝑠𝑑
(2)
lengeofstorageaccessbottlenecks,theGIDSdataloaderemploys
theBaMsystem[31],enablingGPUthreadstodirectlyaccessstor- 𝑇 𝑠 = 𝑁 𝑎𝑐𝑐𝑒𝑠𝑠 (3)
ageandbypassingCPUpage-faulthandlingsoftwareoverhead. 𝐼𝑂𝑃 𝑝𝑒𝑎𝑘
TheGIDSdataloaderalsofeaturesanoveldynamicstorage
where𝑁 definestherequirednumberofconcurrentstorage
𝑎𝑐𝑐𝑒𝑠𝑠
accessaccumulatortomergeiterationsforthegraphsampling
accessesthatmustbemaintainedovertime.𝑇,𝑇 ,and𝑇 denotethe
𝑖 𝑠 𝑡
andfeatureaggregationprocesses,ensuringasufficientnumberof
timespentduringtheinitial,steady-state,andterminationstages,
concurrentstorageaccesses(Section3.2).
respectively.𝐼𝑂𝑃 representsthepeakIOPsforeachSSDwhile
𝑝𝑒𝑎𝑘
CPUMemory: TheGIDSdataloaderpinsthegraphstructure 𝐼𝑂𝑃 istheaverageachievedIOPsperSSDduringthefeature
𝑎𝑐ℎ𝑖𝑒𝑣𝑒𝑑
datainCPUmemorybecausethegraphstructuredata(4-8B)ac-
aggregationstage.Finally,𝑁 isthenumberofSSDsconnected
𝑠𝑠𝑑
cessedbythesamplingprocessexhibitsamuchfinergranularity
toasingleGPU.
Ingeneral,onedeterminesthe𝑁 valuebymaking𝑇 much
1AlthoughtheGIDSdiscussioninthissectionisbasedonDGLframework,itcanbe 𝑎𝑐𝑐𝑒𝑠𝑠 𝑠
easilyextendedtootherGNNframeworkssuchasPyG[8]andAliGraph[50]. largerthan𝑇 𝑖 +𝑇 𝑡 ,whichcanbedeterminedempiricallyforthe

systemused.Naively,onecanincrease𝑇 byincreasingthemini- istypicallyaround32GB/s.Forinstance,thepeakreadIOPsfor
𝑠
batchsize.Whilethesizeofthemini-batchcanbeadjustedbasedon IntelOptaneSSDsisaround1.5millionrequestspersecondwitha
availablecomputationalresourcesandtask-specificrequirements, 4KBcache-linegranularity(equivalentto6GB/s)[15,31],whereas
itmaynotbeabletoincreasebeyondacertainpointduetotraining NANDFlashSSDscanonlyreachamaximumof800thousand
qualityconsiderations.Thus,oneneedstoeliminatethestop-and-go requestspersecond(approximately3.2GB/s).
boundariesbetweenmini-batchesbymergingthedata-preparation BaM[31]addressesthischallengebyconnectingmultipleSSDs
ofconsecutiveiterationsandthuseffectivelyincrease𝑇 .Statically toasingleGPU,therebylinearlyscalingthecollectiveSSDband-
𝑠
settingthenumberofiterationstomergetoeffectivelyhidestorage widthtosaturatethePCIebandwidth.However,implementingsuch
latencywiththeBaMsystemisnotstraightforward.Settingthe asystemmaynotbepracticalforGNNdevelopers,asittypically
numberstoosmallwillresultinpoor𝐼𝑂𝑃 andsettingthe requirestheconnectionofatleast4to5IntelOptaneSSDstoa
𝑎𝑐ℎ𝑖𝑒𝑣𝑒𝑑
numbertoohighwillincuranexcessivelevelofbuffermemory singleGPU.InthecaseofSamsung980proSSDs,amoresubstan-
usage. tialnumber,exceeding10SSDsormore,mayberequiredtofully
Therequirednumberofconcurrentstorageaccessesdependson saturatethePCIebandwidth.
thecharacteristicsoftheSSD,withSSDsexhibitinghigherlatency Toamplifytheeffectivebandwidthofthefeatureaggregation
𝑇 demandingevenmoreconcurrentaccesses.Furthermore,ifmul- processwhenthePCIebandwidthisunder-utilized,theGIDSdat-
𝑖
tipleSSDsareconnectedtoincreasethecollectiveSSDbandwidth, aloaderleveragesCPUmemoryasaconstantCPUbuffer.When
therequirednumberofconcurrentstorageaccessesscaleslinearly thereisavailableCPUmemory,GIDSoffersuserstheflexibilityto
withthenumberofSSDs.Additionally,theGIDSdataloaderlever- allocateaconfigurableportionofCPUmemoryasaconstantCPU
agesbothCPUandGPUmemorytoamplifyfeatureaggregation buffertopinaportionofthefeaturedataintotheCPUmemory.
throughputbyredirectingsomestorageaccessestoCPU/GPUmem- AccessestothefeaturetableintheSSDareredirectedtothe
ory.Thus,ensuringanadequatenumberofnodefeatureaccesses constantCPUbufferwhentherequestedfeaturedataresidesinthe
iscrucial,astheremustbeenoughstorageaccessavailabilityeven constantCPUbuffer.WiththeassistanceoftheGIDSdataloader’s
aftersomeaccessesareredirected. storageaccessaccumulator,thereremainsasufficientnumberof
Toaddressthischallenge,weintroducethedynamicstorage storageaccessestohidethestoragelatency,therebypreserving
accessaccumulatorwithintheGIDSdataloader.Thisinnovative peakSSDreadbandwidth.Astheseredirectedaccessesaremanaged
approachtakesadvantageoftheworkindependenceinherentinthe byCPUmemory,theeffectivebandwidthofthefeatureaggrega-
graphsamplingprocess.Notably,thegraphsamplingandfeature tionprocessincreasesproportionallytothenumberofredirected
aggregationstagesofaniterationarelogicallyindependentofthe accessesuntiltheGPUingressPCIebandwidthisfullyutilized.
modeltrainingstageofpreviousiterationsbecausetheoutputofthe TomaximizetheutilizationoftheconstantCPUbuffer,itises-
modeltrainingstagesolelyupdatesmodelparametersanddoesnot sentialtooptimizethenumberofredirectedaccesses.Thiscanbe
impactgraphsamplingorfeatureaggregationoffutureiterations. achievedbyleveragingtheaccesspatternofthegraphsampling
Based on this observation, the dynamic storage access accu- process.Priorresearch[25]demonstratestheuseofweightedre-
mulatorcombinesiterationsforthegraphsamplingandfeature versepagerankasametricfordistinguishingbetweenhotnodes
aggregationprocessestomaintainasufficientnumberofconcur- andcoldnodescanhelpinthisregard.Asaresult,theGIDSdat-
rentstorageaccessesovertime.Initially,itcalculatesthethreshold aloaderselectivelyretainsnodeswiththehighestweightedreverse
fortherequirednodeaccessesbasedontheproposedmathematical pagerankintheconstantCPUbuffer.Furthermore,theGIDSdata
model.Theaccumulatorexecutesgraphsamplingprocessesfor loaderprovidesuserswiththeflexibilitytodefinewhichnodes
futureiterationsuntilthenumberofnodeaccessessurpassesthe shouldbepinnedinthestaticGPUbufferwhenalternativemetrics
threshold.Atthispoint,theGIDSdataloaderentersthesteadystate, aremoresuitableforidentifyinghotnodes.
retrievingnodefeaturevectorsintomini-batchbuffersintheGPU
memoryandstartingnewiterationsastheaccessesfortheolder
iterationsarecompleted.Thetrainingstagemakesprogressbyac- 3.4 WindowBuffering
cessingthenextmini-batchfromthebatchbuffersandperforming AlthoughtheGIDSdataloadercaneffectivelyhandlestoragelatency
modeltrainingonthemini-batch. andachieveuptoPCIebandwidthduringfeatureaggregation,the
Notethatthenumberofrequirednodeaccessesisinfluenced achievablestoragereadbandwidthisordersofmagnitudelower
bythenumberofstorageaccessesredirectedtoCPU/GPUmem- thantheGPUmemorybandwidthasHighBandwidthMemory2
ory.Therefore,thedynamicstorageaccessaccumulatortracksthe (HBM2)ofrecentNVIDIAGPUscanprovide2TB/sbandwidth[1]
numberofredirectedstorageaccessesanddynamicallyadjuststhe whereasthestoragereadbandwidthislimitedbythe32GB/sPCIe
thresholdvalueaccordingly. in-takebandwidthofA100.Therefore,efficientutilizationofGPU
memoryisnecessarytoamplifytheeffectivebandwidthandfurther
acceleratethefeatureaggregationprocess.
3.3 ConstantCPUBuffer Toaddressthebandwidthshortfall,GIDSemploysBaM’sGPU
ByexploitingtheGPU’smassiveparallelismandasufficientnumber application-definedsoftwarecache.UnliketheGPUhardwarecaches,
ofconcurrentstoragerequests,theGIDSdataloadercanachieve whichhelptoconserveDRAMbandwidth,theGIDSsoftwarecache
peakSSDreadbandwidthduringfeatureaggregation.However, isusedtohelpconservestoragebandwidth.BaM’ssoftwarecache
it is crucial to acknowledge that the peak read bandwidth of a temporarilystoresthepreviouslyaccessedcache-linesbasedonthe
singleSSDfallssignificantlyshortofthePCIebandwidth,which randomevictionpolicy.

However,whenthegraphdatasetismuchlargerthantheGPU fortheGPUcachetoexploitdatalocality,whichcandegradethe
cache, achieving high reusability of node feature data becomes performanceofthefeatureaggregationprocess.Thisisbecause
challengingduetotherandomnatureoftheneighborhoodsampling theGPUmemoryisalimitedresource,andtherandomdataaccess
process.Insuchscenarios,itiscriticaltoaccuratelypredictthe patterncanpollutetheGPUsoftware-definedcache.
cache-linesthatwillbereusedinthenearfuture. Toaddressthesechallenges,theGIDSdataloaderemployszero-
Toovercomethischallenge,theGIDSdataloaderintroducesa copydatatransferviaUnifiedVirtualAddressing(UVA)forgraph
noveltechniquecalledwindowbufferingandintegratesitintothe structuredata.Insteadofstoringtheentiregraphdatainstorage
softwarecache.Unlikethetraditionalframeworks,GIDSleverages devices,ourdataloaderallowsuserstostorenodefeaturedataon
theBaMsoftware-definedcachewhichsupportsthecustomization storagewhilepinninggraphstructuredataintheCPUmemory.
ofcache-lineevictionpolicies.Thewindowbufferingtechnique Thismakesitpossibletoexecutethegraphsamplingprocesson
reducescachethrashingbyavoidingtheevictionofreusablenode eitherCPUorGPU.Thisisapracticalapproachbecausethegraph
featurevectorsthroughmini-batchlook-ahead.Thisisachievedby structuredataissmallcomparedtothenodefeaturedata,evenfor
conductingagraphsamplingoperationforaconfigurablenumber theterabyte-scalegraphsthatweexpecttoaccommodateinthe
ofiterationstofillthewindowbufferwithsamplednodeIDsand foreseeablefuture,asshowninTable4.
avoidingtheevictionoffeaturevectorsforreusednodesinthe
windowbuffer.Therefore,thedataloadercanlook-aheadtothelist 4 EVALUATION
ofthesamplednodesforfutureiterations.
4.1 ExperimentalSetup
Specifically,asillustratedinFigure6,thewindowbufferinthe
GIDSdataloaderisinitiallyfilledwiththenodeIDsthatwillbe
Environment.Table1summarizesthesystemconfigurationforall
evaluations.WecompareGIDSandthestate-of-the-artbaselinedat-
sampledinthenextfewiterations(1).Oncethewindowbufferis
aloadersonanAMDEPYChigh-endserver-gradesystemequipped
filled,thesamplednodeIDsinthecurrentmini-batcharecompared
withaNVIDIAA100-40GBGPUand1TBDDR4CPUDRAM.Addi-
withthenodesinthewindowbuffer(2).Then,thelistofnodesthat
tionally,either768GBor512GBoftheCPUmemorywaslocked
willbereusedinthenextiterationsandthenumberofoccurrencesis
for exclusion to limit the CPU memory capacity for evaluation
generated(3).Thisinformationisthenusedtoupdatethesoftware
purposes.TheevaluationswereconductedusingIntelOptanePCIe
cachemetadata,whichtracksthenumberofreusesinthenext
Gen4NVMeSSDsasthedefaultstorage.Tocomprehensivelyassess
iterationsforeachnode(4).
overallperformance,measurementswerealsotakenwithSamsung
Duringtheupdate,whenthefuturereusecountervaluechanges
980ProSSDs.
from0toanypositivenumber,thestateofthenodeintheGPU
cacheischangedfromthe“SafetoEvict”statetothe"USE"state
Table1:ConfigurationusedtoevaluateGIDS.
so that the corresponding cache-line will not be evicted. If the
countervalueisalreadyapositivenumber,thestateiskeptmarked
Configuration Specification
asthe"USE"state(5).Thecountervalueisdecreasedeachtime
CPU AMDEPYC770264-CoreProcessor
thenodeisreusedduringthefeatureaggregationstage.Whenthe
Memory 1TBDDR4
countervaluebecomes0,thestateofthecorrespondingcache-line NVIDIAA100HBM240GB
isthensetbacktothe“SafetoEvict”statesothatotherthreads GPU 108SMs,192KBSharedMemoryperSM
40MBLLC,1555GBpsHBMBandwidth
cansafelyevictthecache-line.Thisapproacheffectivelyreduces
Ubuntu20.04LTS,NVIDIADriver470.103
cachethrashingandimprovestheperformanceofGNNfeature CUDA11.4
S/W
aggregationonGPUs. DGL0.10
Pytorch1.13.0
IntelOptaneSSDs
SSDs
Samsung980ProSSDs
3.5 GraphStructureDatainCPUMemory PCIeGen4Interconnect
AsshowninFigure5,thegraphsamplingthroughputishigher
onGPUthanonCPUdespitegraphsamplingbeingasequential Datasets.ToassesstheperformanceofGIDSdataloaderonlarge-
process.Thisisbecausethegraphsamplingprocessisespecially scalegraphdatasets,weconductedexperimentsusingfourreal-
latency-criticalforlarge-scalegraphs.Thefundamentalapproach worlddatasets:IGB-Full[19],IGBH-Full[19],ogbn-papers100M[13],
toacceleratesuchaprocessistoexploitparallelismtohidethe andMAG240M[39].Table2presentsthecharacteristicsofthese
latency,whichGPUsnaturallyprovide.Figure7showsthatGPU datasets,suchasthenumberofnodesandedges,thedimensionof
outperformsCPUforallthreedatasets,withaperformancegainof thenodefeaturedata,andthetypeofgraph.Itisworthnotingthat
over3×forthemediumdataset.However,storinggraphstructure ogbn-papers100MandMAG240Mdatasetsaresmallenoughtofit
datainstorageincursmultipleproblems. intotheCPUmemoryofourevaluationsystem.
Firstly,thegraphsamplingprocesshasasmallerdataaccessgran- GIDSImplementationWeextendedDGL[49]toimplementthe
ularitythanthefeatureaggregationprocess,resultinginsignificant GIDSdataloader.Ourapproachinvolvescreatingnewextensions
I/Oamplification.Thisisbecausethedataaccessestothestorage forthestorage-basedfeaturegatheringbyleveragingBaM[31]to
devicesarehandledinpagegranularity,suchas4KB,meaningeven supportuser-levelGPU-initiateddirectstorageaccess.Wethen
ifonlyasmallsegmentofdataisrequested,theentirecache-lineis extendedtheDGLdataloaderclasstoincorporateGIDSfunctional-
transferredfromthestoragetoGPUmemory.Secondly,therandom ities.TousetheGIDSdataloader,usersonlyneedtosettheGIDS
dataaccesspatternfromthesamplingprocessmakesitchallenging flagwheninitializingtheDGLdataloader.

GPU
|     |     |     |                      |     |     |     |                          |               |     | G P U   |
| --- | --- | --- | -------------------- | --- | --- | --- | ------------------------ | ------------- | --- | ------- |
|     |     |     | nibatchM 3inibatch 4 |     | 1   |     | 4 So ft w a r e  Cache M | e ta - d a ta |     |         |
Next  MinibatcMh 1inibatc M h  i 2 N o d e   ID Co u n t e r Softw ar e  C ache
Mini-batches
|         |                   |                   |                    |                    |     | Reusable  | 2   | 0 à3 | Node ID | State              |
| ------- | ----------------- | ----------------- | ------------------ | ------------------ | --- | --------- | --- | ---- | ------- | ------------------ |
|         |                   |                   |                    |                    |     | Nodes     | 3   | 2    | X       | …..                |
|         |                   |                   |                    |                    |     | 2         | 4   | 0 à1 | 2       | Safe to Evict àUSE |
| Window  | (2, 7, 10, 12, …) | (2, 4, 29, 80, …) | (2, 30, 81, 99, …) | (3, 10, 19, 30, …) |     |           |     |      |         |                    |
| Buffer  |                   |                   |                    |                    |     | 4         |     |      | 4       | Safe to Evict àUSE |
|         |                   |                   | 	⋂ Intersection    |                    | 2   | 29        | 28  | 0    | X       | …..                |
|         |                   |                   |                    |                    |     | 30        | 29  | 0 à1 | 29      | Safe to Evict àUSE |
|         |                   |                   | Operation          |                    |     |           |     |      | 3 0     | à                  |
C u r r e n t   (1, 2, 4, 17, 18, 27, 29, 30, 89,  ….,  998, 1000) 30 2 à3 USE USE
| M in i - b a t c h |     |                               |     |     |     | 998  |         |         | X       | . ....                   |
| ------------------ | --- | ----------------------------- | --- | --- | --- | ---- | ------- | ------- | ------- | ------------------------ |
|                    |     |                               |     |     |     |      |         |         | 9 9 8   | Safe  to  E v ict  à USE |
|                    |     |                               |     |     |     | 1000 | 998     | 0 à     | 1 0 0 0 | U SE   à U SE            |
| Re u s a b le      |     |                               |     |     | 3   |      | 9 9 9   | 0   à 3 |         |                          |
|                    |     | (2, 4, 29, 30, …, 998,  1000) |     |     |     |      | 1 0 0 0 | 1   à 2 |         | 5                        |
N o d e s
Figure6:ExampleofthewindowbufferingtechniquefromGIDSdataloader
GIDSDataloader:Inthedefaultconfiguration,weallocated8
CPU GPU
10
)s( emiT gnilpmaS hparG GBofGPUdevicememoryforGPUsoftware-definedcachingand
allocatedCPUmemoryfor10%ofthedataset.Weutilizedasingle
NVMeSSDforboththeGIDSdataloaderandtheDGLbaseline
| 1   |     |     |     |     |     | dataloader. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- |
Baseline:WecomparedGIDSwiththeDGLdataloaderthatis
extendedtoworkwithmemory-mappedfiles.Weusedthememmap
0.1
functionfromNumPytocreateamemory-mappedarraytensorfor
|     | Tiny |     | Small | Medium |     |     |     |     |     |     |
| --- | ---- | --- | ----- | ------ | --- | --- | --- | --- | --- | --- |
thegraphdata.Additionally,weimplementedaBaMdataloader,
whichintegratestheBaMsystemintotheDGLdataloader,and
Figure7:GraphsamplingtimeofCPUandGPUgraphsam-
compareditwithGIDStoshowcasethenovelbenefitsofferedby
plingonthegraphswithdifferentsizes
GIDS.Furthermore,weconductedcomparisonswithGinex[28].
However,Ginexexclusivelysupportshomogeneousgraphsand
Table2:Real-worlddatasetusedforevaluatingGIDS.
neighborhoodsamplingtechniques.
MeasuringExecutionTime:Whenworkingwithlargegraph
Dataset GraphType Numberof Numberof FeatureDi- datasets,thetrainingprocesscanbeexcessivelylong,especiallyfor
|     |     |     | Nodes | Edges | mension |     |     |     |     |     |
| --- | --- | --- | ----- | ----- | ------- | --- | --- | --- | --- | --- |
thebaseline.Therefore,weconductedtheevaluationsbymeasuring
| ogbn- | Homogeneous |     | 111,059,956 1,615,685,872 |     | 128 |     |     |     |     |     |
| ----- | ----------- | --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- |
papers100M the execution time for 100 iterations after a warm-up stage of
| IGB-Full | Homogeneous |     | 269,364,174 3,995,777,033 |     | 1024 |     |     |     |     |     |
| -------- | ----------- | --- | ------------------------- | --- | ---- | --- | --- | --- | --- | --- |
1,000iterations.Weusedthelistedmodelconfiguration,witha
| MAG240M | Heterogeneous |     | 244,160,499 1,728,364,232 |     | 768 |     |     |     |     |     |
| ------- | ------------- | --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- |
mini-batchsizetypicallyrangingfrom1GBto3GB.Thissetupis
| IGBH-Full | Heterogeneous |     | 547,306,935 5,812,005,639 |     | 1024 |     |     |     |     |     |
| --------- | ------------- | --- | ------------------------- | --- | ---- | --- | --- | --- | --- | --- |
favorableforthebaselinesmmapandGinexaswearenotmeasuring
thestoragelatencyoverheadfromthefirst1,000iterationswhen
Table3:IGBdatasetsusedformicro-benchmarks.
thepagecacheintheCPUmemoryisbeingwarmedupforthe
baseline.However,fortheGIDSdataloader,only10iterationsare
| Dataset | GraphType |     | Numberof Numberof |     | FeatureDi- |     |     |     |     |     |
| ------- | --------- | --- | ----------------- | --- | ---------- | --- | --- | --- | --- | --- |
requiredtowarmuptheGPUsoftware-definedcache,andthecache
|     |     |     | Nodes | Edges | mension |     |     |     |     |     |
| --- | --- | --- | ----- | ----- | ------- | --- | --- | --- | --- | --- |
missforthebaselineismorecriticalduetotheexposedstorage
| IGB-tiny   | Homogeneous |     | 100,000                   | 547,416    | 1024 |          |     |     |     |     |
| ---------- | ----------- | --- | ------------------------- | ---------- | ---- | -------- | --- | --- | --- | --- |
| IGB-small  | Homogeneous |     | 1,000,000                 | 12,070,502 | 1024 | latency. |     |     |     |     |
| IGB-medium | Homogeneous |     | 10,000,000 120,077,694    |            | 1024 |          |     |     |     |     |
| IGB-large  | Homogeneous |     | 100,000,000 1,223,571,364 |            | 1024 |          |     |     |     |     |
4.2 EstimationoftheRequiredNumberof
Table4:Datasizedistributionforthereal-worlddatasets.
OverlappingStorageAccesses
Dataset FeatureDataSize GraphStructure TotalSize(GB) InSection3.2,weintroducedamathematicalmodeltoestimate
|     |     | (%) | DataSize(%) |     |     |     |     |     |     |     |
| --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
thenecessarynumberofoverlappingstorageaccessestoattainthe
| ogbn- |     | 68.3 | 31.0 |     | 77.4 |     |     |     |     |     |
| ----- | --- | ---- | ---- | --- | ---- | --- | --- | --- | --- | --- |
papers100M targetSSDbandwidth.Tovalidateourmodel,wemeasuredthe
IGB-Full 94.7 5.1 1084.0 achievedSSDbandwidthwithdifferentnumbersofoverlapping
MAG240M 86.7 12.8 200.0 storageaccessesfortwodistinctSSDs:theIntelOptaneSSDand
| IGBH-Full |     | 96.0 | 3.8 |     | 2773.0 |     |     |     |     |     |
| --------- | --- | ---- | --- | --- | ------ | --- | --- | --- | --- | --- |
theSamsung980ProSSD.Then,wecomparedtheachievedSSD
bandwidthwiththeexpectedSSDbandwidthcalculatedbyour
Model:WeassessedtheperformanceoftheGIDSdataloaderus- model.Forthisevaluation,weconfiguredourIOsizetobe4KB.
ingtwodistinctsamplingtechniques:neighborhoodsampling[11] With a 4KB IO size, the peak IOPs reached 1.5M IOPs for Intel
andLADIES[51]forlayer-wisesampling.Allmodelswereconfig- Optaneand700KIOPsfortheSamsung980ProSSDs.TheSSD
uredwithahiddendimensionof128,andamini-batchsizeof4,096 latencywasmeasuredat11𝜇sforIntelOptaneSSDsand324𝜇sfor
wasemployedwiththreesamplinglayers Samsung980ProSSDs.Additionally,weadded25𝜇stoaccountfor

theinitiallatencyrelatedtokernellaunchandtocaptureinitial
softwareoverheadswhilewesettheterminationlatencyto5𝜇s.
3
2.5
2
1.5
1
0.5
0
1 10 100 1000 10000 100000
)s/BG(
htdiwdnaB
Samsung SSD 980 PRO
7
6
5 4
3
2
1
0
1 10 100 1000 10000 100000
Number of Overlapping Accesses
SSD Bandwidth Model
)s/BG(
htdiwdnaB
Intel Optane SSD
Number of Overlapping Accesses
SSD Bandwidth Model
Figure 8: SSD bandwidth with different numbers of over-
lappingaccessesusingestimationfromthemodelandmea-
surementfromthemicrobenchmark.Themodelaccurately
predictsboththetrendandvaluesofthemeasurements.
Figure8displaystheachievedSSDbandwidthandtheexpected
SSDbandwidthfromourmodelbasedonthenumberofoverlap-
pingSSDaccesses.Despitethehighvarianceinlatency,ourmodel
accuratelyestimatestheSSDbandwidth,particularlywhenitap-
proachesthepeakbandwidth.Forexample,ifweaimtoachieve
95%ofthepeakSSDIOPs,ourmodelestimatesthat812accessesare
requiredfortheIntelOptaneSSD,whilewemeasuredthetargeted
IOPswith1024overlappingaccesses.Theseresultsshowthatour
modelaccuratelyestimatestherequirednumberofoverlapping
storageaccessesforGIDStechniques,suchasthedynamicstorage
accessaccumulator.
4.3 ImpactoftheDynamicStorageAccess
Accumulator
Inthisevaluation,wepresentanexperimentusingtwoIntelOptane
SSDsconnectedtoasingleGPUtoassesstheeffectivenessofthe
dynamicstorageaccessaccumulator.Wevariedthebatchsizeacross
arangefrom32to128whilekeepingthefan-outvaluesconstantfor
neighborhoodsamplingat(5,5).OurevaluationemployedtheIGB-
Fulldataset,andwemeasuredtheGPUPCIeingressbandwidth.
20
15
10
5
0
BaM BaM + GIDSGIDS + BaM BaM + GIDSGIDS + BaM BaM + GIDSGIDS +
Acc ACC Acc ACC Acc ACC
Batch Size: 32 Batch Size: 64 Batch Size: 128
htdiwdnaB
ssergnI
eICP
UPG
)s/BG(
Figure9illustratestheGPUPCIeingressbandwidthwithdif-
ferentconfigurationsduringthefeatureaggregationstageofthe
GIDSdataloader.TheBaMdataloaderintegratestheBaMsystem
intotheDGLdataloaderwhilewindowbufferingandtheconstant
CPUbufferareactivatedfortheGIDSdataloader.
ThebaselineBaMdataloaderachievesPCIeingressbandwidths
of7.6GB/s,9.4GB/s,and10.1GB/sforbatchsizesof32,64,and
128,respectively.SincethepeakbandwidthforIntelOptaneSSDs
isapproximately5.8GB/s,thepeakcollectiveSSDbandwidthis
11.6GB/s,showingthatthereareinsufficientoverlappingstorage
accessestoeffectivelyhidelatency,particularlyevidentwithabatch
sizeof32.Withtheaccumulator,BaMcanachieve9.8GB/s,10.4
GB/s,and10.6GB/s,whichismuchclosertothepeakbandwidth.
WiththeincorporationoftheconstantCPUbufferandwindow
buffering,theperformancegapwidens.GIDSwiththeaccumulator
achieves1.95×,1.46×,and1.31×speedupcomparedtoGIDSwithout
the accumulator. The number of concurrent storage accesses is
reducedinGIDSassomestoragerequestsareredirectedtoeither
theGPUsoftwarecacheortheconstantCPUbuffer,resultingin
lowerSSDbandwidthutilization.Thus,theperformancegainbythe
accumulatorishigherinGIDSasitensuresthepeakSSDbandwidth
utilizationevenwithredirectedstorageaccess.Whiletheachieved
SSDbandwidthisslightlybelowthepeak,thisisduetoadecrease
inthenumberofGPUthreadsthatcansimultaneouslyenqueue
storageaccesses,astheyareinvolvedincopyingdatafromthe
CPUbuffertoGPUmemory.Overall,thedynamicstorageaccess
accumulatorempowersuserstoenhanceSSDbandwidthutilization
forvariousconfigurationsoftheirGNNmodels,irrespectiveof
theirhardwarespecifications.
4.4 ImpactoftheConstantCPUBuffer
Inthissection,weexaminetheimpactoftheconstantCPUbuffer
onthefeatureaggregationperformance,particularlywhenthePCIe
bandwidthisunderutilized.Inthisevaluation,theGIDSdataloader
fetchesfeaturedatafromstoragethatconsistsofasingleSSDfor
theIGB-fulldataset.
Acrossalldataloaders,weconsistentlyconfiguredtheGPUsoft-
warecachetobe8GB,withouttheapplicationofthewindowbuffer-
ingtechnique.ToassesstheinfluenceoftheCPUbuffer,wesystem-
Storage Constant CPU buffer
aticallyvarieditssize,rangingfrom10%to20%ofthedatasetsize.
Furthermore,weexploredtheperformanceoffeatureaggregation
whenimplementingthereversepage-rankalgorithmtodetermine
whichnodesshouldbepinnedintheconstantCPUbuffer.
Figure10providesinsightsintotheeffectivebandwidthwhen
10%or20%ofthefeaturedataispinnedintheconstantCPUbuffer.
ThebaselineGIDSdataloaderachievedafeatureaggregationband-
widthof6.6GBps,whichslightlyexceedsthepeakSSDbandwidth
(5.8GBps)asitfullysaturatedtheSSDbandwidth,andsomeac-
Figure9:Thedynamicstorageaccessaccumulatorincreases cesses were redirected to the GPU software cache. However, it
GPUPCIeingressbandwidthforBaM(1.25×)andGIDSdat- isessentialtohighlightthatthebaselinedataloadercannotfully
aloader(1.95×)byenhancingoverlappingstorageaccesses. utilizetheavailableGPUingressPCIebandwidth.
ThisimprovementismorepronouncedinGIDSduetoits Incontrast,witha20%constantCPUbuffersize,particularly
lowerSSDbandwidthusethrough(1)ahighersoftwarecache whenemployingthereversepage-rankselectionstrategy,thefea-
hitratioduetowindowbufferingand(2)areducednumber tureaggregationthroughputoftheGIDSdataloaderisincreased
ofstorageaccessesthroughtheCPUconstantbuffer. from10.4GBpsand23.4GBps.Thisisbecauseasignificantportion

| 25  |     |     | 30  |     |     |     | Aggregation Time |     | Hit Ratio |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | --------- | --- |
)s/BG( htdiwdnaB evitceffE )6E( sesseccA DSS fo rebmuN 11000 0.2
|     |     |     | 25  |     |     | )s( emIT noitagerggA erutaeF |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- |
20
|     |     |     |     |     |     | 10500 |     |     |     |  oitaR tiH ehcaC UPG |
| --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | -------------------- |
| 15  |     |     | 20  |     |     |       |     |     |     | 0.15                 |
|     |     |     | 15  |     |     | 10000 |     |     |     |                      |
10
|     |     |     | 10  |     |     |      |     |     |     | 0.1 |
| --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
| 5   |     |     |     |     |     | 9500 |     |     |     |     |
5
| 0        |                |                   | 0        |                |                   |      |     |     |     | 0.05 |
| -------- | -------------- | ----------------- | -------- | -------------- | ----------------- | ---- | --- | --- | --- | ---- |
|          | Random         | Reverse Page Rank |          | Random         | Reverse Page Rank | 9000 |     |     |     |      |
| Baseline | 10% CPU Buffer | 20% CPU Buffer    | Baseline | 10% CPU Buffer | 20% CPU Buffer    |      |     |     |     |      |
|          |                |                   |          |                |                   | 8500 |     |     |     | 0    |
|          |                |                   |          |                |                   |      | 0   | 4   | 8   |      |
Window Buffer Depth
Figure10:Featureaggregationthroughputofthebaseline
GIDSandGIDSwiththeconstantCPUbuffer.GIDSachieves
Figure11:Performancecomparisonoffeatureaggregation
| up to | 3.53× higher | effective | bandwidth | with | the constant |     |     |     |     |     |
| ----- | ------------ | --------- | --------- | ---- | ------------ | --- | --- | --- | --- | --- |
processonGIDSdataloaderfordifferentwindowbuffering
CPUbufferwithreversepagerank.Withreversepagerank,
depths.
theCPUconstantbufferholding20%ofthegraphfeature
dataeffectivelymagnifiesthebandwidthofasingleSSDto
thatoffourSSDs. nodefeaturesthatwillbereusedinfuturemini-batchestoavoid
evictingreusablecache-linesacrossmini-batches,whichresultsin
asubstantialdifferencecomparedtorandomeviction.Whenthe
ofstorageaccessesareredirectedtotheconstantCPUbuffer,in- windowbuffersizeissetto8,thecachednodefeaturesthatthe
creasingthePCIebandwidthutilizationbeyondtheSSDbandwidth. GPUcacheexceedsthenumberofthenodefeaturesthatcanfit
These results show that GIDS dataloader’s capacity to mitigate intotheGPUcache.Anyfurtherincreaseinthewindowbuffer
resourceconstraintsonSSDsbyharnessingthepotentialofCPU depthshouldbeaccompaniedbyanincreasedGPUcachesize.
resources,establishingitasapracticalsolutionacrossawidespec-
trumofsystems.
|     |     |     |     |     |     | 40  |     | 0.25 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- |
)s( emiT noitagerggA 35
|     |     |     |     |     |     | 30  |     | 0.2 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
4.5 ImpactoftheWindowBufferingCache
|     |     |     |     |     |     | 25  |     | oitaR tiH 0.15 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | --- |
20
|     | Optimization |     |     |     |     |     |     | 0.1 |     |     |
| --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
15
In this section, we present an evaluation of the impact of GPU 10 0.05
5
| software-definedcacheoptimizationonthefeatureaggregation |     |     |     |     |     |             |                  | 0      |                  |                    |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | ----------- | ---------------- | ------ | ---------------- | ------------------ |
|                                                          |     |     |     |     |     | 0           |                  |        | GIDS GIDS + GIDS | GIDS + GIDS GIDS + |
|                                                          |     |     |     |     |     | GIDS GIDS + | GIDS GIDS + GIDS | GIDS + | WB (8)           | WB WB              |
process.Toconductthisevaluation,wecomparedtheperformance WB (8) WB (16) WB (32) (16) (32)
ofGIDSwithabasicGPUsoftware-definedcacheagainstGIDS 4 GB 8 GB 16 GB 4 GB 8 GB 16 GB
withwindowbufferingoptimization.Toensureafaircomparison,
weusedtheIGB-fulldatasetwiththesameneighborhoodsampling Figure12:Featureaggregationperformancecomparisonbe-
parametersandmini-batchsize.Weevaluatedtheperformance tweenwindowbufferingandthebaseline.GIDSachievesa
higherGPUsoftwarecachehitratiobycapturingmorelo-
withan8GBGPUsoftwarecache.
calitywiththewindowbuffer.
Toaccuratelymeasuretheimpactofthewindowbufferingtech-
nique,wevariedthedepthofthewindowbufferfrom0to4,and
thento8whileevaluatingthefeatureaggregationtimeandthe Next, we compare the performance of the window buffering
GPUsoftware-definedcachehitratio.Whenthewindowbuffer techniquewith4GB,8GB,and16GBoftheGPUsoftwarecache.
depthis0,theGPUsoftware-definedcachefollowstherandom Whenwindowbufferingisactivated,wesetthedepthofthewindow
evictionpolicy,whichservesasthebaseline.Figure11displays bufferto16forall4GB,8GB,and16GBGPUsoftwarecache,
| theresults,whichshowthatthewindowbufferingtechniquecan |     |     |     |     |     | respectively. |     |     |     |     |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- |
improvethecachehitratio.Awindowsizeof4improvesthecache AsshowninFigure12,thewindowbufferingtechniquedemon-
hitratiobyonly1.2×andthefeatureaggregationtimeby1.04×. stratesanimprovement,outperformingtheGIDSwithoutwindow
Settingthewindowbufferdepthtoolow,comparedtothesize bufferingbyafactorof1.20,1.18,and1.12fortheIGB-Fulldataset
oftheGPUcache,canleadtoasimilarperformanceasrandom with4GB,8GB,and16GBGPUcache,respectively.Thehitratio
eviction.Forinstance,ifthemini-batchsizeis2GB,andtheGPU forthebaselineGPUsoftwarecacheincreasesasthesizeofthe
cachesizeis10GB,mostofthenodefeaturesfromtheprevious cacheincreasessinceitcanexploitmoretemporallocality.How-
fourmini-batchesstillresideinthecachewitharandomeviction ever,eventhe16GBGPUcacheperformsworsethanthe4GB
policy.Therefore,theoptimalhitratiowithawindowsizeoffouris GPUcachewithwindowbufferingbecausethehitratioofGIDS’s
similartorandomeviction,makingithardtoachieveameaningful GPUcacheislessaffectedbytheGPUcachesizeunlessthewindow
| performancegain. |     |     |     |     |     | bufferdepthischanged. |     |     |     |     |
| ---------------- | --- | --- | --- | --- | --- | --------------------- | --- | --- | --- | --- |
Whenweincreasethewindowbuffersizeto8,thecachehitratio However,thereisatrade-offtoconsiderwhenincreasingthe
improvesby2.19×overnothavinganywindowbuffering,andthe windowbufferdepth.First,thereneedstobeenoughmemoryspace
aggregationtimedecreasesby1.13×.Thisisbecausethedepthof forthewindowbuffer.Asthenumberofnodesamplesforeach
thewindowbufferprovidesenoughinformationaboutthecached mini-batchisaround1M,thesizeofthelistofsamplednodesfora

mini-batchisseveralmegabytes.Althoughthisisnotasignificantly BaM.TheseresultshighlightGIDS’sexceptionalperformancewith
largeamount,largerwindowsizesincreasetheGPUmemoryre- layer-wisesamplingtechniques.
quirementasthelistofsamplednodesinthewindowbuffermust Forsubgraph-basedsamplingtechniques,suchasClusterGCN[5],
bekeptinGPUmemoryforsubsequentiterations.Additionally,a theGIDSdataloadercanalsobeutilized.However,subgraph-based
largerwindowsizemeansalargerportionoftheGPUcachewillbe samplingtechniquesinvolvetheuseoftheMetis[17]algorithmto
pinnedforfuturereuse,increasingthecontentionontheavailable partitionthegraphandfeaturevectorstofitintheCPUmemory.
cache-linesintheGPUsoftwarecache.Therefore,itisessentialto Metis-basedgraphdatasetpartitionisanextremelytime-consuming
carefullychoosethewindowbuffersizetoensurethatthebenefitof processforlarge-scalegraphdatasetslikeIGB(morethan2days).
ahighercachehitratiooutweighstheoverheadofalargerwindow Ontheotherhand,GIDSleveragesSSDstostoregraphdatasets
buffersize.Bydefault,theGIDSdataloadersetsthedepthofthe andenablesthemappingofsignificantlylargegraphdatasetsin
windowbufferto8basedonthesystemenvironment.However,the asinglenode(dependingonthesizeandnumberofSSDsinthe
windowbufferdepthisatunableparameterthatuserscanadjust system)withouttheneedforagraphpartitioningstep.Giventhis,
basedonthehardwareenvironment,suchasGPUmemorysize. wechosenottoevaluateGIDSforsubgraph-basedpartitioningdue
tothepotentialimpracticalityofemployingtheMetisalgorithmin
suchcases.
4.6 OverallPerformance
Figure13andFigure14illustratetheEnd-to-End(E2E)GNNtrain-
ingtimesforboththebaselineandGIDSdataloadersonhomoge- 5 RELATEDWORK
neousandheterogeneousgraphs,usingSamsung980proandIntel SeveralGNNspecificapplicationsandoptimizationshavebeen
OptaneSSDs,respectively.Notably,Ginexdoesnotsupporthet- proposedintheliterature[12,24,30,36,44,46].ROC[16],Neu-
erogeneousgraphs,andtherefore,theperformanceonIGBH-Full Graph[23],andDSP[4]proposemulti-GPUtrainingsystemfor
andMAG240MdatasetsforGinexisnotmeasured.ForIGBH-Full large-scaleGNNtraining.However,theyrequiresignificantaddi-
datasets,twoSSDsareusedfortheevaluationduetostorageca- tionalhardwareresourcesandarenotscalablesolutions.
pacity. FeatGraph[14]andZIPPER[47]proposetilingtomitigatethe
AsshowninFigure13andFigure14,theGIDSdataloaderachieves memoryfootprintduringGNNtraining.FeatGraphreducesmem-
speedups,reachingupto8.3×and582×comparedtotheDGLbase- oryusagebyutilizinggraphpartitioningandfeaturedimension
linedataloaderforIntelOptaneandSamsung980proSSDs,respec- tiling.Meanwhile,ZIPPERemploysgraph-nativeintermediaterep-
tively.TheperformancegainishigherwithSamsung980proSSDs, resentationtooptimizeGNN,suchassparsegraphtilingandredun-
primarilybecausethefeatureaggregationprocessinthebaseline dantoperationelimination.However,theseapproachessufferfrom
dataloaderislimitedbytheSSDlatency,andtheSSDreadlatency randomaccessesfromGNN,leadingtopoorperformance.More-
ofSamsung980proSSDsisapproximately30×higherthanthat over,thesesolutionsdonotleverageGPUforthedatapreparation
ofIntelOptaneSSDs.Furthermore,theperformancegainforIGB- process.
FullandIGBH-Fulldatasetsissubstantiallylargerthanthatfor AliGraph [50], PaGraph [21], and Ginex [28] use in-memory
ogbn-papers100MandMAG240Mbecausethesizesofthelatter cachingtoreducedatatransferoverhead.AliGraphandPaGraph
twographsaresmallerthantheCPUmemorycapacity,andthus cachehighout-degreeverticesinGPUmemorytominimizedata
thebaselinedoesnotincurasignificantnumberofpagefaultswhile transferbetweenCPUandGPU.GinexusesBelady’salgorithmwith
trainingwiththesedatasets. super-batchsamplesandpipeliningtechniquestohidethelatency
WhencomparedwithGinex,GIDSattainsspeedupsofupto fromspecializedcachingpolicies.However,theseapproachesrely
10.6×and37.2×withIntelOptaneandSamsung980proSSDs.Ginex ontheCPUforthedatapreparationprocessandcannotfullyhide
aimstoalleviatestorageoverheadbyreducingredundantaccesses storagelatency.
tostorage,butthestoragelatencyremainsachallengetoeffec- DataTiering[25]usesweightedreversePageRanktoestimate
tivelymitigate,resultinginsignificantoverhead.Finally,GIDSalso thefrequencyofaccessesduringnodesampling,improvingGPU
outperformsthe BaM dataloaderby 1.3× to 3.1×. This isattrib- memoryutilization.However,itrequiresallgraphdatatobestored
utedtoGIDS’sefficientutilizationofCPUandGPUmemory,which in either CPU or GPU for GNN training execution, so it is not
minimizesstorageaccessesandleadstohighereffectivebandwidth. applicabletolarge-scaleGNNtraining.
4.7 PerformanceofGIDSwithLayer-wise 6 CONCLUSION
Sampling Training Graph Neural Networks (GNNs) on large-scale graph
WealsoconductedaperformancecomparisonofGIDSwithlayer- datasetsisachallengingtaskduetotheirsizeexceedingtheCPU
wisesamplingtechniques,suchasLADIES[51],againstthebaseline memorycapacity.Althoughdistributedtrainingisapossiblesolu-
dataloaders.SinceGinex[28]doesnotsupportsamplingtechniques tion,itisnotcost-effectiveorevenpracticalformanyusers.Inthis
otherthanneighborhoodsampling,wecomparedGIDSwiththe paper,weproposetheGIDSdataloader,aGPU-orientedGNNtrain-
DGLdataloaderandBaM.Inthisevaluation,wepinned512GBof ingsystemthatenablesthetrainingoflarge-scalegraphdatasets
CPUmemorywhileallocating8GBGPUcacheforbothBaMand onasinglemachine.TheGIDSdataloaderenablesGPUthreadsto
GIDS.AsshowninFigure15,GIDSachievedaspeedupof412× directlyaccessstorageandfullytoleratesthelongstoragelatency
comparedtotheDGLdataloaderanda1.92×speedupcomparedto byexploitingthemassivedata-levelparallelismprovidedbyGPUs

10000
1000
100
10
1
Paper100M IGB-Full MAG IGBH-Full Paper100M IGB-Full MAG IGBH-Full
256GB CPU Memory 512GB CPU Memory
)s(emiT
noitucexE
DGL mmap Ginex BaM GIDS
T
ROPPUS
ON
T
ROPPUS
ON
T
ROPPUS
ON
T
ROPPUS
ON
Figure13:End-to-End(E2E)GNNtrainingperformancecomparisonoftheGIDSdataloadersandthebaselinedataloaders
withSamsung980proSSDs.GIDSachievesupto582×,10.62×,and3.09×speedupcomparedtoDGLmmap,Ginex,andBaM
dataloaders,respectively.
1000
100
10
1
Paper100M IGB-Full MAG IGBH-Full Paper100M IGB-Full MAG IGBH-Full
256GB CPU Memory 512GB CPU Memory
)s(emiT
noitucexE
DGL mmap Ginex BaM GIDS
T
ROPPUS
ON
T
ROPPUS
ON
T
ROPPUS
ON
T
ROPPUS
ON
Figure14:End-to-End(E2E)GNNtrainingperformancecomparisonoftheGIDSdataloadersandthebaselinedataloaders
withIntelOptaneSSDs.GIDSachievesupto17.28×,37.21×,and3.23×speedupcomparedtoDGLmmap,Ginex,andBaM
dataloaders,respectively.
1000
100
10
1
0.1
GraphSAGE LADIES GraphSAGE LADIES
ogbn-papers100M IGB-Full
)s(emiT
noitucexE
whileachievingupto582×speedupsoverthestate-of-the-artdat-
DGL mmap BaM GIDS
aloaderfortheoverallexecutionofanend-to-endGNNtraining
pipeline.
ACKNOWLEDGMENTS
Wewouldliketoacknowledgeallofthehelpfrommembersof
theIMPACTresearchgroup,theIBM-IllinoisCenterforCognitive
ComputingSystemsResearch(C3SR)andNVIDIAResearchwithout
whichwecouldnothaveachievedtheresultsreportedinthispaper.
SpecialthankstoKunWu,IsaacGelado,andScottMahlkewho
generouslysharedtheirinsightsthroughnumerousdiscussions.
ThisworkusesGPUsdonatedbyNVIDIAandispartiallysupported
Figure15:FeatureaggregationtimecomparisonoftheGIDS
bytheIBM-ILLINOISC3SRandbytheIBM-ILLINOISDiscovery
dataloadersandthebaselinedataloadersforneighborhood
AcceleratorInstitute(IIDA).
andLADIESsampling.
REFERENCES
[1] 2023.Nvidiaamperearchitecturein-depth. https://developer.nvidia.com/blog/
nvidia-ampere-architecture-in-depth/
andournovelstorageaccessaccumulator.Moreover,theGIDSdat-
[2] MuhammedFatihBalin,KaanSancak,andUmitV.Catalyurek.2023.MG-GCN:
aloaderfurtherimprovesperformancebyutilizingGPUmemoryas AScalableMulti-GPUGCNTrainingFramework.InProceedingsofthe51st
asoftware-definedcachewithwindowbufferingandCPUmemory InternationalConferenceonParallelProcessing(Bordeaux,France)(ICPP’22).
AssociationforComputingMachinery,NewYork,NY,USA,Article79,11pages.
astheconstantCPUbuffer.ByreducingtheI/Ooverheadandmax- https://doi.org/10.1145/3545008.3545082
imizinghardwareresourceutilization,GIDSdataloadercanscale [3] JoanBruna,WojciechZaremba,ArthurSzlam,andYannLeCun.2014.Spectral
GNNtrainingtodatasetswhosesizesaremorethananorderof NetworksandLocallyConnectedNetworksonGraphs. arXiv:1312.6203[cs.LG]
[4] ZhenkunCai,QihuiZhou,XiaoYan,DaZheng,XiangSong,ChenguangZheng,
magnitudelargerthanasinglemachine’sCPUmemorycapacity JamesCheng,andGeorgeKarypis.2023. DSP:EfficientGNNTrainingwith

MultipleGPUs.InProceedingsofthe28thACMSIGPLANAnnualSymposium [24] XupengMiao,YiningShi,HailinZhang,XinZhang,XiaonanNie,ZhiYang,and
onPrinciplesandPracticeofParallelProgramming(Montreal,QC,Canada) BinCui.2022. HET-GMP:AGraph-BasedSystemApproachtoScalingLarge
(PPoPP’23).392–404. EmbeddingModelTraining.InProceedingsofthe2022InternationalConference
[5] Wei-LinChiang,XuanqingLiu,SiSi,YangLi,SamyBengio,andCho-JuiHsieh. onManagementofData(Philadelphia,PA,USA)(SIGMOD’22).Associationfor
2019.Cluster-GCN:AnEfficientAlgorithmforTrainingDeepandLargeGraph ComputingMachinery,NewYork,NY,USA,470–480. https://doi.org/10.1145/
ConvolutionalNetworks.InProceedingsofthe25thACMSIGKDDInternational 3514221.3517902
ConferenceonKnowledgeDiscovery&DataMining(Anchorage,AK,USA) [25] SeungWonMin,KunWu,MertHidayetoglu,JinjunXiong,XiangSong,and
(KDD’19).AssociationforComputingMachinery,NewYork,NY,USA,257–266. Wen-meiHwu.2022. GraphNeuralNetworkTrainingandDataTiering.In
https://doi.org/10.1145/3292500.3330925 Proceedingsofthe28thACMSIGKDDConferenceonKnowledgeDiscovery
[6] MichaëlDefferrard,XavierBresson,andPierreVandergheynst.2016. Con- andDataMining(WashingtonDC,USA)(KDD’22).AssociationforComputing
volutionalNeuralNetworksonGraphswithFastLocalizedSpectralFiltering Machinery,NewYork,NY,USA,3555–3565. https://doi.org/10.1145/3534678.
(NIPS’16).CurranAssociatesInc.,RedHook,NY,USA,3844–3852. 3539038
[7] WenqiFan,YaoMa,QingLi,YuanHe,EricZhao,JiliangTang,andDawei [26] SeungWonMin,KunWu,SitaoHuang,MertHidayetoğlu,JinjunXiong,Eiman
Yin.2019.GraphNeuralNetworksforSocialRecommendation.InTheWorld Ebrahimi,DemingChen,andWenmeiHwu.2021. PyTorch-Direct:Enabling
WideWebConference(SanFrancisco,CA,USA)(WWW’19).Associationfor GPUCentricDataAccessforVeryLargeGraphNeuralNetworkTrainingwith
ComputingMachinery,NewYork,NY,USA,417–426. https://doi.org/10.1145/ IrregularAccesses. arXiv:2101.07956[cs.LG]
3308558.3313488 [27] AdityaPal,ChantatEksombatchai,YitongZhou,BoZhao,CharlesRosenberg,
[8] MatthiasFeyandJanEricLenssen.2019.FastGraphRepresentationLearning andJureLeskovec.2020.PinnerSage:Multi-ModalUserEmbeddingFramework
withPyTorchGeometric. arXiv:1903.02428[cs.LG] forRecommendationsatPinterest.InProceedingsofthe26thACMSIGKDD
[9] VictorGarciaandJoanBruna.2018. Few-ShotLearningwithGraphNeural InternationalConferenceonKnowledgeDiscoveryandDataMining(Virtual
Networks. arXiv:1711.04043[stat.ML] Event,CA,USA)(KDD’20).AssociationforComputingMachinery,NewYork,
[10] DanieleGrattarolaandCesareAlippi.2021.GraphNeuralNetworksinTensor- NY,USA,2311–2320. https://doi.org/10.1145/3394486.3403280
FlowandKeraswithSpektral[ApplicationNotes].Comp.Intell.Mag.16,1(feb [28] YeonhongPark,SunhongMin,andJaeW.Lee.2022.Ginex:SSD-EnabledBillion-
2021),99–106. https://doi.org/10.1109/MCI.2020.3039072 ScaleGraphNeuralNetworkTrainingonaSingleMachineviaProvablyOptimal
[11] WilliamL.Hamilton,RexYing,andJureLeskovec.2017. InductiveRepre- in-MemoryCaching.Proc.VLDBEndow.15,11(jul2022),2626–2639. https:
sentationLearningonLargeGraphs.InProceedingsofthe31stInternational //doi.org/10.14778/3551793.3551819
ConferenceonNeuralInformationProcessingSystems(LongBeach,California, [29] APreprint,YunshengShi,ZhengjieHuang,andWeibinLi.2021. R-UNIMP:
USA)(NIPS’17).CurranAssociatesInc.,RedHook,NY,USA,1025–1035. SOLUTIONFORKDDCUP2021MAG240M-LSC.
[12] Pei-YuHou,DanielR.Korn,CleberC.Melo-Filho,DavidR.Wright,Alexan- [30] JiezhongQiu,LaxmanDhulipala,JieTang,RichardPeng,andChiWang.2021.
derTropsha,andRadaChirkova.2022. CompactWalks:TamingKnowledge- LightNE:ALightweightGraphProcessingSystemforNetworkEmbedding.
GraphEmbeddingswithDomain-andTask-SpecificPathways.InProceedings InProceedingsofthe2021InternationalConferenceonManagementofData
ofthe2022InternationalConferenceonManagementofData(Philadelphia,PA, (VirtualEvent,China)(SIGMOD’21).AssociationforComputingMachinery,
USA)(SIGMOD’22).AssociationforComputingMachinery,NewYork,NY,USA, NewYork,NY,USA,2281–2289. https://doi.org/10.1145/3448016.3457329
458–469. https://doi.org/10.1145/3514221.3517903 [31] ZaidQureshi,VikramSharmaMailthody,IsaacGelado,SeungwonMin,Amna
[13] WeihuaHu,MatthiasFey,MarinkaZitnik,YuxiaoDong,HongyuRen,Bowen Masood,JeongminPark,JinjunXiong,C.J.Newburn,DmitriVainbrand,I-Hsin
Liu,MicheleCatasta,andJureLeskovec.2021.OpenGraphBenchmark:Datasets Chung,MichaelGarland,WilliamDally,andWen-meiHwu.2023.GPU-Initiated
forMachineLearningonGraphs. arXiv:2005.00687[cs.LG] On-DemandHigh-ThroughputStorageAccessintheBaMSystemArchitec-
[14] YuweiHu,ZihaoYe,MinjieWang,JialiYu,DaZheng,MuLi,ZhengZhang,Zhiru ture.InProceedingsofthe28thACMInternationalConferenceonArchitectural
Zhang,andYidaWang.2020.FeatGraph:AFlexibleandEfficientBackendfor SupportforProgrammingLanguagesandOperatingSystems,Volume2(Van-
GraphNeuralNetworkSystems.InProceedingsoftheInternationalConference couver,BC,Canada)(ASPLOS2023).AssociationforComputingMachinery,New
forHighPerformanceComputing,Networking,StorageandAnalysis(Atlanta, York,NY,USA,325–339. https://doi.org/10.1145/3575693.3575748
Georgia)(SC’20).IEEEPress,Article71,13pages. [32] SamyamRajbhandari,OlatunjiRuwase,JeffRasley,ShadenSmith,andYuxiong
[15] Intel.2021.Intel®Optane™Technology.https://www.intel.com/content/www/ He.2021.ZeRO-Infinity:BreakingtheGPUMemoryWallforExtremeScaleDeep
us/en/architecture-and-technology/intel-optane-technology.html. Learning.InProceedingsoftheInternationalConferenceforHighPerformance
[16] ZhihaoJia,SinaLin,MingyuGao,MateiZaharia,andAlexAiken.2020.Improv- Computing,Networking,StorageandAnalysis(St.Louis,Missouri)(SC’21).
ingtheaccuracy,scalability,andperformanceofgraphneuralnetworkswith AssociationforComputingMachinery,NewYork,NY,USA,Article59,14pages.
roc.ProceedingsofMachineLearningandSystems2(2020),187–198. https://doi.org/10.1145/3458817.3476205
[17] GeorgeKarypisandVipinKumar.1997.METIS:Asoftwarepackageforparti- [33] MortezaRamezani,WeilinCong,MehrdadMahdavi,AnandSivasubramaniam,
tioningunstructuredgraphs,partitioningmeshes,andcomputingfill-reducing andMahmutT.Kandemir.2020.GCNMeetsGPU:Decoupling"WhentoSample"
orderingsofsparsematrices. from"HowtoSample".InProceedingsofthe34thInternationalConference
[18] NitishShirishKeskar,DheevatsaMudigere,JorgeNocedal,MikhailSmelyanskiy, onNeuralInformationProcessingSystems(Vancouver,BC,Canada)(NIPS’20).
andPingTakPeterTang.2017. OnLarge-BatchTrainingforDeepLearning: CurranAssociatesInc.,RedHook,NY,USA,Article1552,11pages.
GeneralizationGapandSharpMinima. arXiv:1609.04836[cs.LG] [34] AndreaRossi,DonatellaFirmani,PaoloMerialdo,andTommasoTeofili.2022.
[19] ArpandeepKhatua,VikramSharmaMailthody,BhagyashreeTaleka,TengfeiMa, ExplainingLinkPredictionSystemsBasedonKnowledgeGraphEmbeddings.
XiangSong,andWenmeiHwu.2023.IGB:AddressingTheGapsInLabeling, InProceedingsofthe2022InternationalConferenceonManagementofData
Features,Heterogeneity,andSizeofPublicGraphDatasetsforDeepLearning (Philadelphia,PA,USA)(SIGMOD’22).AssociationforComputingMachinery,
Research. arXiv:2302.13522[cs.LG] NewYork,NY,USA,2062–2075. https://doi.org/10.1145/3514221.3517887
[20] Thomas N. Kipf and Max Welling. 2017. Semi-Supervised Classification [35] Petar Veličković, Guillem Cucurull, Arantxa Casanova, Adriana Romero,
withGraphConvolutionalNetworks.InProceedingsofthe5thInternational Pietro Liò, and Yoshua Bengio. 2018. Graph Attention Networks.
ConferenceonLearningRepresentations(PalaisdesCongrèsNeptune,Toulon, arXiv:1710.10903[stat.ML]
France)(ICLR’17). [36] AlinaVretinaris,ChuanLei,VasilisEfthymiou,XiaoQin,andFatmaÖzcan.2021.
[21] ZhiqiLin,ChengLi,YoushanMiao,YunxinLiu,andYinlongXu.2020.PaGraph: MedicalEntityDisambiguationUsingGraphNeuralNetworks.InProceedings
ScalingGNNTrainingonLargeGraphsviaComputation-AwareCaching.In ofthe2021InternationalConferenceonManagementofData(VirtualEvent,
Proceedingsofthe11thACMSymposiumonCloudComputing(VirtualEvent, China)(SIGMOD’21).AssociationforComputingMachinery,NewYork,NY,
USA)(SoCC’20).AssociationforComputingMachinery,NewYork,NY,USA, USA,2310–2318. https://doi.org/10.1145/3448016.3457328
401–415. https://doi.org/10.1145/3419111.3421281 [37] ChunyangWang,DesenSun,andYuebinBai.2023.PiPAD.InProceedingsofthe
[22] ZhiweiLiu,YingtongDou,PhilipS.Yu,YutongDeng,andHaoPeng.2020. 28thACMSIGPLANAnnualSymposiumonPrinciplesandPracticeofParallel
AlleviatingtheInconsistencyProblemofApplyingGraphNeuralNetwork Programming.ACM. https://doi.org/10.1145/3572848.3577487
to Fraud Detection. In Proceedings of the 43rd International ACM SIGIR [38] JianyuWang,RuiWen,ChunmingWu,YuHuang,andJianXiong.2019.FdGars:
ConferenceonResearchandDevelopmentinInformationRetrieval(Virtual FraudsterDetectionviaGraphConvolutionalNetworksinOnlineAppReview
Event,China)(SIGIR’20).AssociationforComputingMachinery,NewYork, System.InCompanionProceedingsofThe2019WorldWideWebConference
NY,USA,1569–1572. https://doi.org/10.1145/3397271.3401253 (SanFrancisco,USA)(WWW’19).AssociationforComputingMachinery,New
[23] LingxiaoMa,ZhiYang,YoushanMiao,JilongXue,MingWu,LidongZhou, York,NY,USA,310–316. https://doi.org/10.1145/3308560.3316586
andYafeiDai.2019. Neugraph:ParallelDeepNeuralNetworkComputation [39] Kuansan Wang, Zhihong Shen, Chiyuan Huang, Chieh-Han Wu, Yuxiao
onLargeGraphs.InProceedingsofthe2019USENIXConferenceonUsenix Dong, and Anshul Kanakia. 2020. Microsoft Academic Graph: When ex-
AnnualTechnicalConference(Renton,WA,USA)(USENIXATC’19).USENIX perts are not enough. Quantitative Science Studies 1, 1 (02 2020), 396–
Association,USA,443–457. 413. https://doi.org/10.1162/qss_a_00021arXiv:https://direct.mit.edu/qss/article-
pdf/1/1/396/1760880/qss_a_00021.pdf

[40] QiangeWang,YanfengZhang,HaoWang,ChaoyiChen,XiaodongZhang,and [46] WentaoZhang,YuShen,YangLi,LeiChen,ZhiYang,andBinCui.2021.ALG:Fast
GeYu.2022. NeutronStar:DistributedGNNTrainingwithHybridDepen- andAccurateActiveLearningFrameworkforGraphConvolutionalNetworks.
dencyManagement.InProceedingsofthe2022InternationalConferenceon InProceedingsofthe2021InternationalConferenceonManagementofData
ManagementofData(Philadelphia,PA,USA)(SIGMOD’22).Associationfor (VirtualEvent,China)(SIGMOD’21).AssociationforComputingMachinery,
ComputingMachinery,NewYork,NY,USA,1301–1315. https://doi.org/10.1145/ NewYork,NY,USA,2366–2374. https://doi.org/10.1145/3448016.3457325
3514221.3526134 [47] ZhihuiZhang,JingwenLeng,ShuwenLu,YoushanMiao,YijiaDiao,Minyi
[41] D.RandallWilsonandTonyR.Martinez.2003. TheGeneralInefficiencyof Guo,ChaoLi,andYuhaoZhu.2021. ZIPPER:ExploitingTile-andOperator-
BatchTrainingforGradientDescentLearning.NeuralNetw.16,10(dec2003), levelParallelismforGeneralandScalableGraphNeuralNetworkAcceleration.
1429–1451. https://doi.org/10.1016/S0893-6080(03)00138-2 arXiv:2107.08709[cs.AR]
[42] QitianWu,YitingChen,ChenxiaoYang,andJunchiYan.2023.Energy-basedOut- [48] JishenZhao,ShengLi,JichuanChang,JohnL.Byrne,LauraL.Ramirez,Kevin
of-DistributionDetectionforGraphNeuralNetworks. arXiv:2302.02914[cs.LG] Lim,YuanXie,andPaoloFaraboschi.2015.Buri:ScalingBig-MemoryComputing
[43] ChangYe,YuchenLi,BingshengHe,ZhaoLi,andJianlingSun.2021. GPU- withHardware-BasedMemoryExpansion.ACMTrans.Archit.CodeOptim.12,
Accelerated Graph Label Propagation for Real-Time Fraud Detection. In 3,Article31(oct2015),24pages. https://doi.org/10.1145/2808233
Proceedingsofthe2021InternationalConferenceonManagementofData(Vir- [49] DaZheng,ChaoMa,MinjieWang,JinjingZhou,QidongSu,XiangSong,Quan
tualEvent,China)(SIGMOD’21).AssociationforComputingMachinery,New Gan,ZhengZhang,andGeorgeKarypis.2021. DistDGL:DistributedGraph
York,NY,USA,2348–2356. https://doi.org/10.1145/3448016.3452774 NeuralNetworkTrainingforBillion-ScaleGraphs.arXiv:2010.05337.
[44] HanqingZeng,HongkuanZhou,AjiteshSrivastava,RajgopalKannan,and [50] RongZhu,KunZhao,HongxiaYang,WeiLin,ChangZhou,BaoleAi,YongLi,
ViktorPrasanna.2021. Accurate,efficientandscalabletrainingofGraph andJingrenZhou.2019.AliGraph:AComprehensiveGraphNeuralNetwork
NeuralNetworks. J.ParallelandDistrib.Comput.147(jan2021),166–183. Platform.Proc.VLDBEndow.12,12(aug2019),2094–2105. https://doi.org/10.
https://doi.org/10.1016/j.jpdc.2020.08.011 14778/3352063.3352127
[45] MuhanZhangandYixinChen.2018. LinkPredictionBasedonGraphNeu- [51] DifanZou,ZiniuHu,YewenWang,SongJiang,YizhouSun,andQuanquan
ralNetworks.InProceedingsofthe32ndInternationalConferenceonNeural Gu.2019.Layer-DependentImportanceSamplingforTrainingDeepandLarge
InformationProcessingSystems(Montréal,Canada)(NIPS’18).CurranAsso- GraphConvolutionalNetworks.CurranAssociatesInc.,RedHook,NY,USA.
ciatesInc.,RedHook,NY,USA,5171–5181.