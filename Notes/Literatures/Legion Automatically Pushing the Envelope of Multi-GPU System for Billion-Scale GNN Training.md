Legion: Automatically Pushing the Envelope of Multi-GPU System
|     |     |          |        | for Billion-Scale |               | GNN Training  |     |           |     |     |     |
| --- | --- | -------- | ------ | ----------------- | ------------- | ------------- | --- | --------- | --- | --- | --- |
|     |     | JieSun1, | LiSu2, |                   | ZuochengShi1, | WentingShen2, |     | ZekeWang1 |     |     |     |
LeiWang2, JieZhang1, YongLi2, WenyuanYu2, JingrenZhou2, FeiWu1,3
1CollaborativeInnovationCenterofArtificialIntelligence,ZhejiangUniversity,China
2AlibabaGroup
3202 nuJ 21  ]CD.sc[  2v88561.5032:viXra
3ShanghaiInstituteforAdvancedStudyofZhejiangUniversity,China
Abstract It is common to apply GNNs overlarge-scale graphs in
industrialscenarios.Forexample,inAlibaba’sTaobaorec-
Graphneuralnetwork(GNN)hasbeenwidelyappliedin
ommendationsystem,theuserbehaviorgraphcontainsmore
real-worldapplications,suchasproductrecommendationin
|     |     |     |     |     |     | than one | billion vertices | andtens | ofbillions | ofedges | [54]. |
| --- | --- | --- | --- | --- | --- | -------- | ---------------- | ------- | ---------- | ------- | ----- |
e-commerceplatformsandriskcontrolinfinancialmanage-
|     |     |     |     |     |     | In addition, | as graphs | are | often skewed, | it is infeasible | to  |
| --- | --- | --- | --- | --- | --- | ------------ | --------- | --- | ------------- | ---------------- | --- |
mentsystems.Severalcache-basedGNNsystemshavebeen
|          |            |     |               |                |      | aggregateallneighboringverticeswhen |     |     |     | traininga | specific |
| -------- | ---------- | --- | ------------- | -------------- | ---- | ----------------------------------- | --- | --- | --- | --------- | -------- |
| built to | accelerate | GNN | training in a | single machine | with |                                     |     |     |     |           |          |
vertex.Sampling-basedmini-batchtraining,suchasGraph-
multipleGPUs.However,thesesystemsfailtotrainbillion-
SAGE[16],isproposedtoextendGNNtrainingtoverylarge
scalegraphsefficiently,whichisacommonchallengeinthe
graphs.Inthesampling-basedGNNtraining,therearetwo
industry.Inthiswork,weproposeLegion,asystemthatau-
keystepsofdatapreparationsbeforetrainingabatch:(1)sam-
tomaticallypushestheenvelopeofmulti-GPUsystemsfor
plingthemulti-hopsub-graphforeachvertexinthebatch,and
acceleratingbillion-scaleGNNtraining.First,wedesignahi-
(2)extractingthefeaturesofverticesinsampledsub-graphs.
erarchicalgraphpartitioningmechanismthatsignificantlyim-
SystemssuchasDGL[41]andPyG[31]storethegraphdata
provesthemulti-GPUcacheperformance.Second,webuilda
intheCPUmemory,preparethetrainingdataofmini-batches
unifiedmulti-GPUcachethathelpstominimizethePCIetraf-
|     |     |     |     |     |     | using CPUs,and | utilize | GPUs | for | model training. | As this |
| --- | --- | --- | --- | --- | --- | -------------- | ------- | ---- | --- | --------------- | ------- |
ficincurredbycachingbothgraphtopologyandfeatureswith
approachrequirestransferringthesampledsub-graphsand
| the highesthotness. |     | Third,we | developan | automaticcache |     |     |     |     |     |     |     |
| ------------------- | --- | -------- | --------- | -------------- | --- | --- | --- | --- | --- | --- | --- |
high-dimensionfeaturedatatotheGPUforeverybatch,the
| management | mechanism |     | that adapts the | multi-GPU | cache |     |     |     |     |     |     |
| ---------- | --------- | --- | --------------- | --------- | ----- | --- | --- | --- | --- | --- | --- |
end-to-endtrainingthroughputisseverelylimitedbytheCPU-
| plan according                                |     | to the hardware | specifications |     | and various |          |              |           |          |                 |     |
| --------------------------------------------- | --- | --------------- | -------------- | --- | ----------- | -------- | ------------ | --------- | -------- | --------------- | --- |
|                                               |     |                 |                |     |             | GPU data | transferring | bandwidth | [23,46]. | In addition,the |     |
| graphstomaximizetheoveralltrainingthroughput. |     |                 |                |     | Evalu-      |          |              |           |          |                 |     |
throughputofgraphsamplingusingCPUisofteninsufficient
ationsonvariousGNNmodelsandmultipledatasetsshow
tokeepupwiththethroughputofGPUtraining,especiallyin
| that Legion | supports | training | billion-scale | GNNs | in a sin- |     |     |     |     |     |     |
| ----------- | -------- | -------- | ------------- | ---- | --------- | --- | --- | --- | --- | --- | --- |
multi-GPUmachines.
glemachineandsignificantlyoutperformsthestate-of-the-art
|     |     |     |     |     |     | Several | cache-based | approaches |     | have been | proposed to |
| --- | --- | --- | --- | --- | --- | ------- | ----------- | ---------- | --- | --------- | ----------- |
cache-basedsystemsonsmallgraphs.
|     |     |     |     |     |     | speedupGNNtraining[23,29,33,46]. |     |     |     | Asitisthefeature |     |
| --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | --- | ---------------- | --- |
datathataccountsforamajorityoftheCPU-GPUdatatrans-
1 Introduction ferring,cachingthefeaturesoffrequentlyaccessedverticesin
GPUcansignificantlyreducetheamountoftransferreddata.
|     |     |     |     |     |     | To improve | the throughputofgraphsampling,GPU-based |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ---------- | --------------------------------------- | --- | --- | --- | --- |
Graphneuralnetworks(GNNs),suchas[8,10,16,22,39,49],
samplinghasalsobeenadoptedinGNNsystems[33,41,46].
| are a class | of  | deep learning | algorithms | that learn | the low- |     |     |     |     |     |     |
| ----------- | --- | ------------- | ---------- | ---------- | -------- | --- | --- | --- | --- | --- | --- |
Weidentifythatexistingapproachesfaceseverelimitations
dimensionalembeddingusingthestructureandattributein-
formationofgraphs.Thelearnedembeddingcanbefurther or performance issues in multi-GPU training, particularly
whenthegraphislarge.First,themulti-GPUcachescalabil-
usedinmachine-learningtasksincludingnodeclassification
ityofexistingcache-basedsystemsispoor.Somecache-based
| and link | prediction. | GNNs | have been | successfully | applied |     |     |     |     |     |     |
| -------- | ----------- | ---- | --------- | ------------ | ------- | --- | --- | --- | --- | --- | --- |
in many real-world applications, such as recommendation GNNsystems[33,46]shufflethetrainingsetacrossallGPUs
andreplicateanidenticalfeaturecacheacrossallGPUsor
systemsine-commerceplatforms,frauddetectionandrisk
NVLinkcliques1tofacilitatedataparalleltraining.Thecache
controlinfinancialmanagement,andmolecularpropertypre-
|     |     |     |     |     |     | capacity | is constrainedby |     | the memory | ofa single | GPU or |
| --- | --- | --- | --- | --- | --- | -------- | ---------------- | --- | ---------- | ---------- | ------ |
dictionindrugdevelopment[13,25,36,47,48].Systemssuch
asDGL[41],PyG[31],andGraph-Learn[54]areproposed
1NVLinkcliquedenotesagroupofGPUswhereeachpairofGPUsare
toeasethedevelopmentandtrainingofGNNmodels.
connectedwithNVLink.

NVLinkclique(anNVLinkcliqueonlyconsistsoftwoGPUs
in some multi-GPU architectures),resulting in poor cache
performancewhenscalingupthenumberofGPUs(seethe
experimentinFigure2).PaGraph[23]partitionsthegraphus-
ingaself-reliantalgorithmandcachesnodeswiththehighest
in-degreefordifferentpartitionsindifferentGPUs,tryingto
makeuseofdatalocalityinsideeachpartition.Aspartitions
in PaGraph include the complete L-hop neighbors of their
Figure1:Theworkflowof2-hopGraphSAGEtraining.
training vertices,there is a significantoverlap between the
cachesofdifferentpartitions,resultinginthesameduplica-
tioningtechniquethathelpsminimizecachereplication
tionissueastheaforementionedcache-basedGNNsystems.
between NVLink cliques and extends the threshold of
Second,whenadoptingGPU-basedgraphsampling,existing
cachecapacitybeyondthelimitofanNVLinkclique.
systemsmanagethegraphtopologyinaverycoarse-grained
2. Weproposeahotness-awareunifiedcachetostoretopol-
manner:thetopologyhastobecompletelystoredinasingle
ogyandfeatureswiththehighesthotnessinGPUmemory,
GPU[33,41,46]orintheCPUmemory[33,41].Theformer
soastoimprovetheGPUmemoryutilization.
approach puts a hard limit on the graph scale,and further
3. Wepresentanautomaticcachemanagementmechanism
squeezesthecachecapacityforfeatures.Thelatterstoringthe
that searches for the optimal cache plan without requir-
topologyintheCPUandaccessingitfromGPUwouldresult
ingextraknowledgeofhardwarespecificationsandGNN
in very low utilization of the PCIe bandwidth,as the data
performancedetailsfromusers.
accessofgraphsamplingisusuallyrandomandfine-grained.
4. We implement Legion that fully explores the hardware
ThispaperpresentsLegion,aGNNsystemthatfullyex-
capabilitiesofmulti-GPUsystemstargetingbillion-scale
ploresthehardwarecapabilitiesofmodernmulti-GPUservers
GNNtraining,notsupportedbyexistingcache-basedGNN
fortraininglarge-scalegraphsinasinglemachine. Legion
systems,inasingleserver.
proposestwokeydesignstofullyexploitthememoryspace
ofmulti-GPUsforfeatureandtopologycache.First,toavoid
cachereplication,weproposeNVLink-awarehierarchical 2 Preliminaries
graphpartitioningtechniquethathelpsscalethecacheon
multi-GPUmemoryefficientlyaccordingtothespecifichard- Inthissection,weintroducethebasicconceptofGNNand
warestructure.Legionfirstpartitionsthegraphwithminimal theworkflowofmini-batchGNNtraining.
edge-cutandassignseachpartitionexclusivelytoanNVLink
clique,andthenuseshashpartitiontofurthermapthetraining 2.1 GraphNeuralNetworks
verticestoGPUsinsideeachNVLinkclique.Second,wepro-
poseahotness-awareunifiedcachethatmanagesboththe Given a graphG=(V,E),where eachvertex is associated
featureandtopologycacheinavertex-centricdatastructure. withavectorofdataasitsfeaturesX v ,v∈V,GraphNeural
WeenableanNVLink-enhancedcachespacefortheunified Networks(GNNs) learn a low-dimensional embedding for
cacheandprioritizethetopologyandfeatureswiththehigh- eachtargetvertexbystackingmultipleGNNslayersL.For
esthotnesstofillthecache,soastoimprovethemulti-GPU eachlayerl,l∈L,vertexvupdatesitsactivationbyaggregat-
memoryutilization. ingfeaturesorhiddenactivationsofitsneighborsN(v),v∈V:
TheabovedesignsposeanewchallengetoLegion.Given
a fixedsize ofGPU memory,itis hardto manuallydecide
al =AGGREGATEl(hl−1|u∈N(v))
v u
(1)
theoptimalfractionsoftopologyandfeaturecachesuchthat hl =UPDATEl(al,hl−1)
v v v
the overalltraining throughputis maximized. To solve the
challenge, we propose an automatic cache management
2.2 Mini-batchGNNsTraining
mechanism.Specifically,webuildacostmodelinthemecha-
nismtoevaluatethekeyfactortotheoverallthroughput,i.e., Mini-batchtrainingisapracticalsolutionforscalingGNN
PCIetraffic,ofbothgraphsamplingandfeatureextractionin trainingonverylargegraphs.Neighborsamplingisusedto
thetrainingphase,whichisusedtoguidetheallocationsof generatemini-batches,allowingsampling-basedGNNmod-
cachespacesforgraphtopologyandfeature.Overall,thethree elstohandleunseenvertices.Forexample,GraphSAGE[16]
keydesignsinLegionenableautomaticcachingoptimization samplesmultiplehopsofneighborsfortrainingasshownin
andfullutilizationofhardwarecapabilityofvariousmodern Figure 1. The workflow of GraphSAGE training follows a
GPUservers.ExperimentsshowthatLegioncanoutperform vertex-centric computation paradigm including the follow-
state-of-the-artcache-basedGNNsystemsupto4.32×. ingsteps:1,selectingamini-batchoftrainingverticesfrom
Insummary,thecontributionsofthispaperinclude: thetrainingset.2,uniformlysamplingthemultiplehopsof
1. We propose an NVLink-aware hierarchical graph parti- fixed-sizeneighborsforeachtrainingvertex.3,extractingthe

featuresofthesub-graphconsistingofthetrainingvertices
andtheirneighborstogeneratethemini-batchtrainingdata.
Finally,performingAGGREGATEandUPDATEaccordingto
Equations1,aswellasexecutingtheforwardandbackward
propagationtoupdatethemodelparameters.
3 ObservationandMotivation
(a)2GPUsperNVLinkclique (b)4GPUsperNVLinkclique
Whentraininglarge-scalegraphswhosesizeexceedstheca-
Figure 2: Comparing the cache scalability of cache-based
pacity of GPU memory on a multi-GPU server,the major
GNN systems using the Products [17] dataset and 2-hop
performance bottleneck becomes the data movement from
GraphSAGE[16]modelintermsofnormalizedCPU-GPU
CPU to GPUs underthe constraintofPCIe bandwidth. To
PCIetransactions.Thecacheratioissetto5%|V|onevery
thisend,existingworks[33,41,46]intendtorelievethePCIe
GPU.ThetestedplatformsareSiton(a)andDGX-V100(b)
bandwidthbottleneckbycachingthehottestgraphfeatureson
servers,asshowninTable1.
GPUmemory.Thoughthesecache-basedapproachessignifi-
cantlyreducePCIetraffic,westillidentifytwoissuesofthese
dundantverticesandedgestoincludealltheL-hopneighbor
existingcache-basedGNNsystemswhentraininglarge-scale
verticesforeachtrainvertexinthispartition.EachGPUonly
graphs:1)poormulti-GPUcachescalability,and2)coarse-
trainsitsownpartitionandsynchronizesitslocalgradients
grained GPU memory management for graph topology. In
periodicallytoupdatethemodel.However,theinclusionof
thefollowing,wediscusseachissueandthecorresponding
theL-hopneighborverticesleadstoheavilyduplicatedcache
observationthatmotivatesthedesignofLegion.
contentsonallGPUs.Figure2showsthatthePaGraphex-
hibitsasimilarcacheperformanceasGNNLabwhichadopts
3.1 Multi-GPUCacheScalability the cache replication mechanism. We further implement a
PaGraph-plusdesigntoalleviatethecacheduplicationissue
Asfeatureextractionoccupiesmostofthedatatransferring inPaGraph. Specifically,wereplacethegraphpartitioning
fromCPUtoGPU,cache-basedsystemslikeGNNLab[46] algorithminPaGraphwiththeXtraPulp[34]algorithmthat
maintainaglobalfeaturecacheforverticeswhicharemore minimizes edge-cuts between partitions and adopts a pre-
frequentlyaccessedviaapre-samplingphase.Astrainingver- sampling-basedhotnessmetrictoselectthevertexfeaturesto
ticesaregloballyshuffledamongalltrainingGPUs,GNNLab becached.AlthoughPaGraph-plusachieveshighercachehit
replicatesthiscacheacrossallGPUsinvolvedinmodeltrain- ratescomparedtoPaGraph,thecachehitratesondifferent
ing.SinceasingleGPU’smemoryspaceisquitelimited,the GPUsareveryunbalancedasdifferentpartitionshavevarious
fractionofcachedfeatureswouldinevitablybecomelower graphdistributions. Figure 3 illustrates the loadimbalance
when the graph size grows, resulting in a lower cache hit issue of PaGraph-plus by measuring the cache hit rates of
ratioevenonmulti-GPUservers.Toincreasethecacheca- eightGPUs.Weobservethatthehitratevariesbyupto17%.
pacity,thecachemechanisminQuiver[33]leverageshigh- Tosumup,forsystemsthatgloballyshufflethetraining
speedNVLinkstosupportinter-GPUcachebetweenNVLink- verticesamongGPUsineveryiteration,suchasGNNLaband
connectedGPUs.DifferentfromGNNLab,Quiverreplicates Quiver,cache replication cannot be completely eliminated
featurecachebetweenNVLinkcliquesandaveragelyhashes aseachGPUmayrandomlyaccessanyvertexintheentire
thefeaturesamongGPUsinthesameNVLinkclique.How- graph.Whereasthehigh-speedNVLinksbetweenGPUscan
ever,thismechanismcouldstillleadtopoorcachescalability, beusedtoreducethereplicationfactorandexpandthecache
especiallywhentheNVLinkcliqueisrelativelysmall.E.g., capacity.Forsystemsthatlocallyshuffletrainingverticesin
theSitonserverusedinTable1has4NVLinkcliques,each each partition to produce mini-batches fordifferent GPUs,
ofwhichcontainsonly2GPUs.Figure2illustratesthat,in such as PaGraph, the cache replication problem could be
systemslikeQuiver,thePCIetransactionsincurredbyCPU- alleviatedonlywhenthemodellayerissmall(e.g.,lessthan2).
GPUdatatransferringstopdecreasingwhenthenumberof PaGraph-pluscanfurtherreducecacheduplicationbutfaces
GPUsislargerthanthesizeofNVLinkclique. Thisresult anotherissueofunbalancedcachehitratesamongGPUs.
showsthatthecacheperformanceintheaboveGNNsystems Observation O1: Graph partitioning can be suitably
cannot scale well with the increasing number of GPUs in guided by hardware structure. Different from Quiver,
modernservers. GNNLab,PaGraph,andPaGraph-plusdonottakeadvantage
Tosolvethescalabilityissueincurredbycachereplication, oftheNVLinkbetweenGPUs,whichisacommoncapabil-
PaGraph[23]partitionsthegraphinaself-relianceapproach ityinmodernmulti-GPUservers.AsGPUsinsidethesame
andmaintainsanindependentcacheforeachpartitionusing NVLinkcliquecanaccesseachother’smemoryviathelow-
an in-degree-based metric on different GPUs. To train an latencyhigh-throughputNVLink,anNVLinkcliquecanhold
L-layerGNNmodel,PaGraphextendseverypartitionwithre- theentirecacheofapartition,whichcanberandomlysliced

address(UVA[27])technique.Whilethedataaccesspattern
ofgraphsamplingisusuallyrandomandfine-grained.E.g.,
Figure4ashowsthatthePCIethroughputofgraphsampling
ismuchlowerthanfeatureextraction.Alargenumberofsam-
plingPCIetransactionswithsmallpayloadsizeswillincrease
theCPU-GPUPCIecontentionandleadtolowbandwidth
Figure3:Cachehitratesofdifferentsystemsinaserverwith
utilization.
8GPUs.Thecacheratioissetto5%|V|oneveryGPU.The
ObservationO2:Theaccessofgraphtopologyisskewed
graphsamplingfollowsthe2-hopGraphSAGE[16]model’s
asgraphfeatures.Existingcache-basedGNNsystems[23,
settingusingtheProducts[17]dataset.“NVx"meansutilizing
33,46] only maintain feature cache in GPU to reduce the
NVLinkcliquewithxGPUs.
CPU-GPUcommunicationcosts.However,weobservethat
theperformancegainoftheper-unitfeaturecachedecreases
oncethecachecapacityexceedsathreshold(seeFigure4b).
Weobservethattheaccessofgraphtopologyduringgraph
samplingisalsoskewedastheaccessoffeatures.Insteadof
allocatingalltheavailableGPUmemory(exceptforthereser-
vationformodeltraining)forfeaturecache,itisreasonable
tocacheasubsetofgraphtopology,i.e.,edgesofverticesthat
arefrequentlyaccessedduringsampling,intheGPUmemory
(a)PCIethroughputvs.payloadsize (b)
to accelerate GPU sampling. Figure 4b shows that a rela-
Figure4:(a)ThePCIe3.0throughputunderdifferentpayload tivelysmalltopologycachecanobviouslyreducethenumber
sizesofPCIerequests.(b)ThePCIetrafficreductionratefor ofPCIetransactionsincurredbyGPUsampling.Motivated
Paper100Mwiththegrowthofthecachecapacity.Thecache byO2,weproposeahotness-awareunifiedcacheinLegion.
isonasingleGPUandselectedafterpre-sampling. Specifically,Legioncachesbothgraphtopologyandgraph
featureswiththegoalofminimizingCPU-GPUcommunica-
andaveragelyallocatedamongGPUsinsideaclique. This tionoverhead(seeSection4.2).Underthecapacitylimitof
hardware-coherent design can balance the cache hit ratios GPUmemory,itisdifficulttomanuallydecidetheoptimal
between intra-clique GPUs. As the numberofpartitions is fractionsoftopologyandfeaturecache.Legionsolvesthis
reducedtothenumberofNVLinkcliques,itismorelikely challengewithanautomaticcachemanagementmechanism,
thatthepartitionsfollowasimilardistribution(seethecache whichcangeneratetheoptimalcacheplanwithoutrequiring
hitratedistributionofLegioninFigure3).InspiredbyO1, knowledgeofhardwarespecificationsfromusers.
weproposeanNVLink-awarehierarchicalpartitioningtopre-
servemulti-GPUcachescalabilityinLegion(Section4.1). 4 DesignofLegion
Inordertoaddresstheaforementionedperformanceissues
3.2 Coarse-grained GPU Memory Manage-
ofexistingcache-basedGNNsystems,weproposeLegion,
mentforGraphTopology
acache-optimalGNNsystemthatcanpushtheenvelopeof
In multi-GPUservers,thethroughputofCPU-basedgraph themulti-GPUsystemautomaticallyforbillion-scaleGNN
samplingmaynotcatchupwiththethroughputofGPU-based training. Theoveralldesignof Legion ispresentedinFig-
training.Toimprovetheend-to-endtrainingthroughput,re- ure5.WeproposeanNVLink-awarehierarchicalpartitioning
centGNNsystems[33,41,46]adoptGPUstoaccelerategraph technique(Section4.1)inLegionthatfacilitatesscalingup
sampling. We observe that all these systems apply a very thecachecapacityandreducingcacheduplicationinmulti-
coarse-grainedmemorymanagementmechanismforgraph GPUservers.ToutilizeGPUcacheforbothgraphsampling
topology.Inparticular,theystoretheentiregraphtopology and feature extraction,we present a hotness-aware unified
eitherinCPUmemoryorinasingleGPU,dependingonthe cache(Section4.2)thatmaintainsboththetopologyandfea-
sizeofgraphtopology:thegraphtopologyisstoredinCPU turecachestooptimizetheoverheadofPCIetraffic.Wealso
memorywhenitistoolargeorexceedsthecapacityofasin- developanautomaticcachemanagementmechanism(Sec-
gleGPU.Theapproachofstoringtheentiregraphtopology tion4.3)toautomaticallydecidethememoryallocationsfor
inasingleGPUsetsahardlimitonthescaleofthegraph. bothtopologyandfeaturecaches.
For example, a V100 GPU with 16GB memory can store
atmost4 billion edges [16] withoutconsidering any other 4.1 NVLink-awareHierarchicalPartitioning
memory usage of feature cache and model training. When
storing the graph topology in CPU memory,GPUs can di- MotivatedbyobservationO1,weproposeasimpleyeteffec-
rectlyaccessthegraphtopologyviaaunifiedvirtualmemory tivegraphpartitioningmechanism,referredtoashierarchical

Figure5:DesignoverviewofLegion.LegionconsistsofthreemaincontributionsC1,C2,andC3.
partitioning,tofacilitatecachescalabilityin Legion.Differ- mini-batchesforgraphsamplingandtraining.
entfromconventionalgraphpartitioningalgorithmswhich Assuch,Legionprovidesbettercachescalabilityandload
partition alledges/vertices ofa graphinto multiple tablets, balancingcomparedtoexistingsystems.Figure2showsthe
hierarchicalpartitioninginLegionaimstodividethetraining cache performance of Legion improves with the increase
vertices/edgesintomultipledisjointtablets.Theinputsofhi- of GPUs almost linearly. Figure 3 illustrates that Legion
| erarchicalpartitioningareanNVLinktopologymatrixM |     |     | of  |                                                     |     |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                                                  |     |     | T   | hassmallerfluctuationsinthecachehitratesonmulti-GPU |     |     |     |     |     |     |
theunderlyingmulti-GPUserverandagraphG.Theoutput serverswithNVLinkcliquesofvarioussizes.
isanassignmentplandisseminatingtrainingvertices/edges
amongGPUs.Specifically,theprocessofhierarchicalparti-
4.2 Hotness-awareUnifiedCache
tioningmainlyconsistsoffoursteps:
S1:NVLinkCliqueDetection. Withthetopologymatrix Motivated by the observation O2, we propose a hotness-
M of the server, Legion employs a MaxCliqueDyn algo- awareunifiedcachetocachebothgraphtopologyandgraph
T
M
rithm [44] to identify the NVLink clique sets in T , and features.InthisSection,weintroducethedetailedmechanism
outputsthenumberofNVLinkcliquesK andthenumberof oftheunifiedcache.
c
| GPUsineachcliqueK | .   |     |     |     |     |     |     |     |     |     |
| ----------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
g
4.2.1 CacheStructure
S2:Inter-cliqueGraphPartitioning.Toreducethecache
duplicationbetweenNVLinkcliques,Legionusesanedge-
Theunifiedcacheconsistsoftwoparts:thetopologycache
cutminimizingpartitioningalgorithm,e.g.,METIS[21]and andthefeaturecache.Inparticular,thetopologycachemain-
| XtraPulp[34],tosplittheinputgraphGintoK |     |     | partitions,i.e., |                                                    |     |     |     |     |     |     |
| --------------------------------------- | --- | --- | ---------------- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                                         |     |     | c                | tainsout-edgeneighborIDsforeachselectedhotvertexin |     |     |     |     |     |     |
P 1 ,P 2 ,...,P Kc ,suchthatnodesarebalancedamongpartitions the format of a compressed sparse row (CSR). As for the
andinter-partitionedge-cutsareminimized.Thetrainingver-
featurecache,Legionstoresthefeaturevectorsofselected
| tex setin | P is denotedasVP. | As the training | vertices are |                                                    |     |     |     |     |     |     |
| --------- | ----------------- | --------------- | ------------ | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|           | i                 | i               |              | hotverticesintheformatofa2Darray,whereeachrowisthe |     |     |     |     |     |     |
randomlyselectedfromG,thetrainingvertexsetsofdifferent featurevectorofaselectedhotvertex.Notethat,theselected
partitionsarealmostoftheequalsize.Thenumberofparti-
verticesinthetopologyandfeaturecachescouldbedifferent.
tionsisequaltothenumberofdetectedNVLinkcliques,and
eachNVLinkcliquehoststhecacheforadedicatedpartition. 4.2.2 CacheConstruction
Thisway,Legioncanreducethecacheduplicationbetween
|     |     |     |     | The construction | of  | the unified | cache | is divided | into | three |
| --- | --- | --- | --- | ---------------- | --- | ----------- | ----- | ---------- | ---- | ----- |
NVLinkcliquesandtakeadvantageofcachelocalitywithin
steps:(1)pre-sampling,(2)cachecandidateselection,and(3)
anNVLinkclique.
cacheinitialization.AlltheGPUs/NVLinkcliquesperform
S3: Intra-cliqueTrainingVertexPartitioning.AsGPUs
thesestepsconcurrentlytoconstructtheirownunifiedcache.
withinanNVLinkcliquecanaccesseachother’smemoryvia
S1:Pre-sampling.SimilartoGNNLab[46],Legionadopts
low-latencyhigh-throughputNVLinkinterconnect,hierarchi- phase2
|     |     |     |     | a pre-sampling |     | to estimate |     | the hotness | metrics | of  |
| --- | --- | --- | --- | -------------- | --- | ----------- | --- | ----------- | ------- | --- |
calpartitioningfurtherhashesthetrainingvertexsetofeach
|                |                               |                   |            | graph topology | and                                | feature | data during | the | training      | phase. |
| -------------- | ----------------------------- | ----------------- | ---------- | -------------- | ---------------------------------- | ------- | ----------- | --- | ------------- | ------ |
| partitionintoK | tablets,whereK                | istheGPUnumberina |            |                |                                    |         |             |     |               |        |
|                | g                             | g                 |            |                |                                    |         |             |     |               |        |
|                |                               |                   |            | Once the       | process ofhierarchicalpartitioning |         |             |     | is completed, |        |
| clique.E.g.,VP | i issplitintoVP[1]andVP[2]ifK | i i               | g equals2. |                |                                    |         |             |     |               |        |
thetrainingvertextabletassignedtoeachGPUisdetermined,
EachtabletisexclusivelymappedtoaGPUinthecorrespond-
|     |     |     |     | whichis | usedas the | inputforpre-sampling. |     |     | The outputof |     |
| --- | --- | --- | --- | ------- | ---------- | --------------------- | --- | --- | ------------ | --- |
ingNVLinkclique.Weexplainhowtogeneratethecachefor
|     |     |     |     | pre-sampling | includes | two | hotness | matrices: | topology | hot- |
| --- | --- | --- | --- | ------------ | -------- | --- | ------- | --------- | -------- | ---- |
eachtrainingvertextabletinSection4.2.
|     |     |     |     | nessmatrixH | andfeaturehotnessmatrixH |     |     |     | .Eachmatrix’s |     |
| --- | --- | --- | --- | ----------- | ------------------------ | --- | --- | --- | ------------- | --- |
|     |     |     |     |             | T                        |     |     | F   |               |     |
S4: Training VertexAssignment. Finally,Legion assigns rowrepresents the GPU IDs within an NVLinkclique,the
trainingverticesofeachtablettoacorrespondingGPUasthe
batchseeds,whichwillthenbeshuffledlocallytogenerate 2Duringpre-sampling,graphtopologyisstoredintheCPUmemory.

Algorithm1COMPLETESHARINGWITHLOCALPREFER-
ENCE(CSLP)
|     |     |     |     |     |     |     |     | Input | :Kg:numberofGPUsperNVLinkclique |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ------------------------------- | --- | --- | --- | --- |
HF:featurehotnessmatrix
HT:topologyhotnessmatrix
|     |     |     |     |     |     |     |     | Output | :AF:accumulatedvertex-wisefeaturehotnessvector |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ---------------------------------------------- | --- | --- | --- | --- |
AT:accumulatedvertex-wisetopologyhotnessvector
QT:vertexIDqueuerepresentingclique-leveltopologyorder,
QF:vertexIDqueuerepresentingclique-levelfeatureorder
GT:vertexIDqueuerepresentingGPU-leveltopologyorder
Figure6:Updatethehotnessmatricesofgraphtopologyand GF:vertexIDqueuerepresentingGPU-levelfeatureorder
|     |     |     |     |     |     |     |     | /*Step1:Accumulateeachvertex’shotnessfromKgGPUs. |     |     |     |     | */  |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- |
featuresbypre-sampling.Forsimplicity,weonlyshowthe
|     |     |     |     |     |     |     |     | 1 AF=HF.columnWiseSum();AT |     | =HT.columnWiseSum(); |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------- | --- | -------------------- | --- | --- | --- |
resultforGPU1.
|     |     |     |     |     |     |     |     | /*Step2:SortverticesinAFandAT |     |                         |     |     | */  |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------- | --- | ----------------------- | --- | --- | --- |
|     |     |     |     |     |     |     |     | QF<-SortbyKeyDescend(AF);QT   |     | <-SortbyKeyDescend(AT); |     |     |     |
2
columnrepresentsthevertexIDs,andtheelementH ofei- /*Step3:AssigneachvertextotheGPUwiththehighestlocalhotness. */
ij
|                                     |     |     |     |     |                     |     |     | forv_idinQT | do  |     |     |     |     |
| ----------------------------------- | --- | --- | --- | --- | ------------------- | --- | --- | ----------- | --- | --- | --- | --- | --- |
| thermatrixrepresentsthehotnessofthe |     |     |     |     | j-thvertexinthei-th |     |     | 3           |     |     |     |     |     |
gpu_id=max(HT[1:Kg][v_id]).index;
| GPU.Duringthepre-sampling,eachGPUconductsalocal |     |     |     |     |     |     |     | 4   |     |     |     |     |     |
| ----------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
GT[gpu_id].push(v_id);
| shuffleonitsowntrainingvertextablettogenerateseedsfor |     |     |     |     |     |     |     | 5 end           |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- |
| mini-batches,performsgraphsamplingforeachmini-batch,  |     |     |     |     |     |     |     | 6 forv_idinQFdo |     |     |     |     |     |
andupdatesthecorrespondingrowinH andH .Figure6 7 gpu_id=max(HF[1:Kg][v_id]).index;
|     |     |     |     |     | T   | F   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
GF[gpu_id].push(v_id);
| showsapre-samplingexample. |     |     |     | ForH | T ,wheneveranedge |     |     |       |     |     |     |     |     |
| -------------------------- | --- | --- | --- | ---- | ----------------- | --- | --- | ----- | --- | --- | --- | --- | --- |
|                            |     |     |     |      |                   |     |     | 8 end |     |     |     |     |     |
istraversedduringsampling,thehotnessofitssourcevertex
isincrementedby1.ForH
F ,thehotnessforeachvertexthat
appearsinthesampleresultsofthemini-batchisincremented 4.3 AutomaticCacheManagement
by1.Additionally,LegionusesIntel®PerformanceCounter
Thedesignoftheunifiedcacheposesanewchallenge:how
| Monitor(PCM) |     | [18]tocollectthesummationofPCIetrans- |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | --- | ------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
actionsnumber,N ,generatedbyallGPUsinanNVLink to properly specify the cache size for graph topology and
TSUM
cliqueduringpre-sampling.3 featuresundertheconstraintofGPUmemorysuchthatthe
overalltrainingthroughputismaximized.
| S2: Cache | Candidate |     | Selection. |     | The objective |     | of cache |     |     |     |     |     |     |
| --------- | --------- | --- | ---------- | --- | ------------- | --- | -------- | --- | --- | --- | --- | --- | --- |
candidateselectionistoselectanddisseminatethehottopol- Thegeneralideaistopredicttheoverallthroughputunder
differentcacheplansandsearchforthebestcacheplanthat
ogysub-structuresandfeaturesamongGPUswithinthesame
NVLinkcliquebasedonpre-sampledhotnessmatrices.Thus maximizesoverallthroughput.Wedefinethecacheplanas
acachememorymanagementsetting(B,α)attheNVLink
| this phase | is conducted |     | in the | unit | of NVLink | clique,and |     |     |     |     |     |     |     |
| ---------- | ------------ | --- | ------ | ---- | --------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
cliquegranularity,whereBisthemulti-GPUcachememory
| eachclique | requires | one | GPU | to perform | the | computation. |     |     |     |     |     |     |     |
| ---------- | -------- | --- | --- | ---------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |
Thedetailedprocessofcachecandidateselectionispresented sizeinanNVLinkcliqueandαisthememoryratiofortopol-
|     |     |     |     |     |     |     |     | ogycache. | BisidenticalamongNVLinkcliques |     |     |     | andisby |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------------------------------ | --- | --- | --- | ------- |
inAlgorithm1.Inbrief,thisalgorithmcomputestheglobal
|                  |     |         |                      |     |     |      |     | default set | as the total | multi-GPU | memory | minus | the size |
| ---------------- | --- | ------- | -------------------- | --- | --- | ---- | --- | ----------- | ------------ | --------- | ------ | ----- | -------- |
| topology/feature |     | hotness | ofallvertices,i.e.,A |     |     | andA | ,in |             |              |           |        |       |          |
|                  |     |         |                      |     |     | T    | F   |             |              |           |        |       |          |
ofGPUmemoryreservedforGNNmodelsandintermediate
| theNVLinkcliquebyconductingacolumn-wisesumonH |     |     |     |      |                 |     | T   |            |                  |     |           |       |           |
| --------------------------------------------- | --- | --- | --- | ---- | --------------- | --- | --- | ---------- | ---------------- | --- | --------- | ----- | --------- |
|                                               |     |     |     |      |                 |     |     | buffers in | an NVLinkclique. | We  | needthree | steps | to deter- |
| andH ,respectively(Line1).A                   |     |     |     | andA | arethensortedin |     |     |            |                  |     |           |       |           |
| F                                             |     |     |     | T    | F               |     |     |            |                  |     |           |       |           |
descendingordertogenerateQ andQ (Line2).Next,We minetheoptimalcachememorymanagementsetting(B,α),
|     |     |     |     | T   | F   |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
asdiscussedinSections4.3.1,4.3.2,and4.3.3.
| iterateQ | T andQ  | F inorderandassigneveryvisitedvertexto |     |     |      |      |       |     |     |     |     |     |     |
| -------- | ------- | -------------------------------------- | --- | --- | ---- | ---- | ----- | --- | --- | --- | --- | --- | --- |
| the GPU  | withthe | highestlocalhotness                    |     |     | in H | andH | . For |     |     |     |     |     |     |
|          |         |                                        |     |     |      | T    | F     |     |     |     |     |     |     |
eachGPU,wemaintaintwoqueues,i.e.,G ,G 4.3.1 EstimatingOverallThroughput
|     |     |     |     |     | T   | F ,whoseorder |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- |
representsthepriorityofverticestobeincludedinthisGPU
ThekeygoalofthisSectionistobuildtherelationshipbe-
cache.TheoutputsofAlgorithm1arefurtherusedbythecost
tweentheoverallthroughputandacacheplan.Webuildthe
model(seeSection4.3)togeneratethephysicalcacheplan.
relationshipbyestimatingakeyfactor:thetotalPCIetraffic
| S3:CacheInitializationandFill-up. |     |     |     |     | Legion’scacheman- |     |     |        |                 |           |      |         |            |
| --------------------------------- | --- | --- | --- | --- | ----------------- | --- | --- | ------ | --------------- | --------- | ---- | ------- | ---------- |
|                                   |     |     |     |     |                   |     |     | N ,due | to two reasons. | First,the | PCIe | traffic | is the ma- |
total
agementautomaticallydecidesthecacheratiofortopology
|     |     |     |     |     |     |     |     | jor bottleneck | of the overall | system | throughput,and |     | lower |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | -------------- | ------ | -------------- | --- | ----- |
andfeaturesothattheoverallthroughputismaximized(see
PCIetrafficleadstohigheroverallsystemthroughput.Sec-
| Section | 4.3). Guided | by  | this | mechanism,Legion |     |     | allocates |     |     |     |     |     |     |
| ------- | ------------ | --- | ---- | ---------------- | --- | --- | --------- | --- | --- | --- | --- | --- | --- |
ond,varyingcacheplansmajorresultsinthevarianceofPCIe
memoryforboththetopologyandfeaturecache(TCandFC)
traffic.4BecauseeachNVLinkcliquemaintainscachesforits
| of each | GPU,and | fetches | the | corresponding |     | topology | and |     |     |     |     |     |     |
| ------- | ------- | ------- | --- | ------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
ownpartition,weindependentlyselecttheoptimalcacheplan
| feature | data from | CPU | memoryto |     | fillupeachGPU |     | cache |     |     |     |     |     |     |
| ------- | --------- | --- | -------- | --- | ------------- | --- | ----- | --- | --- | --- | --- | --- | --- |
foreachNVLinkcliquesoastominimizethePCIetrafficof
| accordingtothecorrespondingcacheordersinG |     |     |     |     |     |     | andG . |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
|                                           |     |     |     |     |     | T   | F      |     |     |     |     |     |     |
4ThoughNVLinktrafficisalsoinfluencedbythecacheplan,weneglect
3NTSUMisfurtherusedbycostmodel’sevaluation.
itsinceNVLinkhasamuchhigherbandwidththanPCIe.

eachNVLinkclique.Thus,theoverallsystem’sPCIetraffic Estimating N . We explain howto calculate N when the
|              |     |     |     |     |     |     |                           | F   |     |         |     | F         |     |
| ------------ | --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | ------- | --- | --------- | --- |
| isminimized. |     |     |     |     |     |     | featurecachememorysizeism |     |     | ,wherem |     | =B×(1−α). |     |
|              |     |     |     |     |     |     |                           |     |     | F       |     | F         |     |
Therearealsothreestepsinestimation.
|       |                      |     |     |       |     |     | First,givenm |           | ,wedecidewhichvertices’featuresshould |        |     |             |       |
| ----- | -------------------- | --- | --- | ----- | --- | --- | ------------ | --------- | ------------------------------------- | ------ | --- | ----------- | ----- |
| 4.3.2 | CostModeltoEstimateN |     |     | total |     |     |              | F         |                                       |        |     |             |       |
|       |                      |     |     |       |     |     | be cached.   | We define | V                                     | as the | set | of vertices | whose |
Fcache
The key goal of this Section is to present a cost model to featuredataiscached.Thenweincreasetheverticeswiththeir
estimateN underaspecificcacheplan(B,α).First,given featureintocachebytheorderQ untiltheoccupiedfeature
|                    | total |             |     |                      |     |     |                         |     |     | F                         |     |     |     |
| ------------------ | ----- | ----------- | --- | -------------------- | --- | --- | ----------------------- | --- | --- | ------------------------- | --- | --- | --- |
| aspecificcacheplan |       | (B,α),wecan |     | calculatethetopology |     |     |                         |     |     |                           |     |     |     |
|                    |       |             |     |                      |     |     | cachememorysizereachesm |     |     | F ,asdefinedinEquation6.D |     |     |     |
cache size m T and the feature cache size m F . Second,we representsthedimensionofafeaturevectorandthefeature
findwhichvertices’topology/featuresshouldbestoredinthe dataistheFloat32typeeachofwhichneedss bytesto
float32
| topology/featurecache.Third,weestimatethePCIetrafficfor |     |     |     |     |     |     | store. |     |     |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
graphsampling(N )andforfeatureextraction(N )withthe ∑ D×s =m (6)
|     |     | T   |     |     | F   |     |     |     |     | float32 |     | F   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- |
currenttopology/featurecacheutilization.Atlast,weestimate
v∈VFcache
| N total byaddingupN |     | T andN | F   | ,asshowninEquation2. |     |     |                   |          |                |     |              |           |           |
| ------------------- | --- | ------ | --- | -------------------- | --- | --- | ----------------- | -------- | -------------- | --- | ------------ | --------- | --------- |
|                     |     |        |     |                      |     |     | Second,           | as shown | in Equation    |     | 7, we        | calculate | the total |
|                     |     |        |     |                      |     |     | numberoffeaturesU |          | thatstillneeds |     | transferring |           | through   |
F
|     |     | N total | =N  | T +N F |     | (2) |     |     |     |     |     |     |     |
| --- | --- | ------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
PCIewithafeaturecache.
| ToestimateN |     | andN | ,weneedtocollectotherinforma- |     |     |     |     |     |     |     |     |     |     |
| ----------- | --- | ---- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|             |     | T    | F                             |     |     |     |     |     |     |     |     |     |     |
tion apartfrom a given cache plan: the hotness vectors A U = ∑(a (v))− ∑ (a (v)) (7)
|                                            |     |     |     |     |     | T    |     | F   | F   |           |     | F   |     |
| ------------------------------------------ | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --------- | --- | --- | --- |
| andA ,thesummationofPCIetransactionnumberN |     |     |     |     |     |      |     |     | v∈V | v∈VFcache |     |     |     |
| F                                          |     |     |     |     |     | TSUM |     |     |     |           |     |     |     |
incurredbygraphsampling,andtheorderqueuesoftopol-
|                              |     |              |     |                      |     |     | Third,wegetN                                           |     | F bymultiplyingthetransactionnumber |     |                      |     |     |
| ---------------------------- | --- | ------------ | --- | -------------------- | --- | --- | ------------------------------------------------------ | --- | ----------------------------------- | --- | -------------------- | --- | --- |
| ogy/featurecachecandidates,Q |     |              |     | andQ .               |     |     |                                                        |     |                                     |     |                      |     |     |
|                              |     |              |     | T F                  |     |     | neededbytransferringonevertex’sfeaturewiththetotalnum- |     |                                     |     |                      |     |     |
| EstimatingN                  |     | .WeestimateN |     | whenthememorysizeofa |     |     |                                                        |     |                                     |     |                      |     |     |
|                              | T   |              |     | T                    |     |     | beroffeaturestobetransferred,U                         |     |                                     |     | ,asshowninEquation8. |     |     |
F
| topologycacheunderonespecificcacheplan(B,α)ism |     |     |     |     |     | ,   |     |     |     |     |     |     |     |
| ---------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
T HereCLSmeansthetransferredcachelinesize.CLSmight
| wherem      | =B×α.Theestimationconsistsofthreesteps. |                                         |     |     |     |     |                                                 |     |     |     |     |     |     |
| ----------- | --------------------------------------- | --------------------------------------- | --- | --- | --- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
|             | T                                       |                                         |     |     |     |     | bedifferentforvariousCPUsandGPUs.WecangettheCLS |     |     |     |     |     |     |
| First,withm |                                         | T ,wedecidewhichvertices’topologyshould |     |     |     |     |                                                 |     |     |     |     |     |     |
fromPCM.E.g.,CLSequals64inourmachinesettings.And
| becached.WedefineV |     |                                  | asthesetofallverticesinthegraph. |     |     |     |                                          |     |     |     |     |     |          |
| ------------------ | --- | -------------------------------- | -------------------------------- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | -------- |
|                    |     |                                  |                                  |     |     |     | a (v)meansthehotnessofaspecificvertexv(a |     |     |     |     |     | (v)∈A ). |
| AndwedefineV       |     | asthesetofallverticeswhosetopol- |                                  |     |     |     | F                                        |     |     |     |     | F   | F        |
Tcache
| ogyiscachedundercurrenttopologycachesizem |     |     |     |     |     | .Toget |     |     | D×s |         |     |     |     |
| ----------------------------------------- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | ------- | --- | --- | --- |
|                                           |     |     |     |     | T   |        |     |     |     | float32 |     |     |     |
V ,weincreaseverticesandtheirtopologyintothecache N F =(⌈ ⌉)×U F (8)
| Tcache |     |     |     |     |     |     |     |     |     | CLS |     |     |     |
| ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
withthegrowthofoccupiedtopologycachememorybythe
| orderQ          | . Untilthe | overalloccupiedtopology |     |                       | cache | mem- |                                              |     |     |     |     |     |     |
| --------------- | ---------- | ----------------------- | --- | --------------------- | ----- | ---- | -------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                 | T          |                         |     |                       |       |      | 4.3.3 SearchingforOptimalCachePlaninParallel |     |     |     |     |     |     |
| orysizereachesm |            | ,werecordV              |     | .Equation3illustrates |       |      |                                              |     |     |     |     |     |     |
|                 |            | T                       |     | Tcache                |       |      |                                              |     |     |     |     |     |     |
therelationbetweenm T andV Tcache ,wherenc(v)meansthe ThekeygoalofthisSectionistoefficientlydeterminetheopti-
neighborcountofthevertexv.Hereweassumethedatatypes malcacheplanforeachclique.AsdiscussedinSection4.3.1,
areUint64andUint32fortherowandthecolumnindicesof wesearchfortheoptimalcacheplanindependentlywithone
thecompressedsparserowformat(CSR),respectively.We GPUforeachNVLinkclique.IneachNVLinkclique,wefirst
uses ands todenotethenumberofbytestostorea needtotraverseαfrom0to1byaninterval∆α5togenerate
| uint64 |     | uint32 |     |     |     |     |     |     |     |     |     |     |     |
| ------ | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
singleUint64andUint32dataaccordingly. thecandidatecacheplans,andthecalculateN accordingly.
total
|     |     |     |     |     |     |     | ThenweneedtosearchN |     |     | sequencesandfindthesmallest |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --------------------------- | --- | --- | --- |
total
|     | ∑   | (nc(v)×s |     | +s )=m |     | (3) |     |     |     |     |     |     |     |
| --- | --- | -------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
uint32 uint64 T onewiththededicatedα.Tominimizeoverhead,theprocess
|     | v∈VTcache |     |     |     |     |     | iswellparallelized,includingfoursteps: |     |     |     |     |     |     |
| --- | --------- | --- | --- | --- | --- | --- | -------------------------------------- | --- | --- | --- | --- | --- | --- |
First,wegenerateallthecandidatecacheplansinparallel
| Second, | once | we getV |     | , we can calculate | the | ratio |     |     |     |     |     |     |     |
| ------- | ---- | ------- | --- | ------------------ | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
Tcache
|             |             |     |         |                 |       |     | andgetsequencesofm |     | andm | ineachsetting. |     |     |     |
| ----------- | ----------- | --- | ------- | --------------- | ----- | --- | ------------------ | --- | ---- | -------------- | --- | --- | --- |
| of the PCIe | transaction |     | reduced | by the topology | cache | by  |                    |     | T    | F              |     |     |     |
Second,wegettheboundariesofcachedverticessetV
| Equation4.Leta |     | (v)meanthetopologyhotnessofaspecific |     |     |     |     |     |     |     |     |     |     | Tcache |
| -------------- | --- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ |
T
|           |         |      |     |     |     |     | andV Fcache     | usingEquations3and6,wheretheboundaries |           |         |     |          |        |
| --------- | ------- | ---- | --- | --- | --- | --- | --------------- | -------------------------------------- | --------- | ------- | --- | -------- | ------ |
| vertexv(a | T (v)∈A | T ). |     |     |     |     |                 |                                        |           |         |     |          |        |
|           |         |      |     |     |     |     | are the largest | cached                                 | vertices’ | indexes |     | in Q and | Q . To |
|           |         |      |     |     |     |     |                 |                                        |           |         |     | T        | F      |
∑ a (v) d o so , w e g e t t he t o p o l o g y a n d f ea tu r em e m o ry s iz e o f e v e r y
|     |     | R = | v ∈V Tc | ac he T ) |     | (4) |     |     |     |     |     |     |     |
| --- | --- | --- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
T si ng le v e rt e x i n pa r a l le l a n d s t or e th e m in t w o ar ra y s, S
|              |     |                                       | ∑   | a T ( v) |     |     |         |                              |     |     |     |      | T s in g l e |
| ------------ | --- | ------------------------------------- | --- | -------- | --- | --- | ------- | ---------------------------- | --- | --- | --- | ---- | ------------ |
|              |     |                                       | v∈  | V        |     |     | andS    | ,followingtheverticesorder,Q |     |     |     | andQ | .Next,       |
|              |     |                                       |     |          |     |     | Fsingle |                              |     |     |     | T    | F            |
| Third,wegetN |     | bymultiplyingtheentirePCIetransaction |     |          |     |     |         |                              |     |     |     |      |              |
T we calculate the cumulative sum of S Tsingle and S Fsingle by
N TSUM with the ratio of PCIe transactions that can not be aparallelinclusivescanandgetS andS . Thenfor
|     |     |     |     |     |     |     |     |     |     |     | Tsum | Fsum |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | ---- | --- |
reducedbythetopologycache.WecangetN byEquation5. each cache plan with m and m ,we use a parallel binary
|     |     |      |      |         | T   |     |                            |     | T   | F   |     |     |     |
| --- | --- | ---- | ---- | ------- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | --- |
|     |     | N =N |      | ×(1−R ) |     | (5) | 5∆αissettobe0.01bydefault. |     |     |     |     |     |     |
|     |     | T    | TSUM | T       |     |     |                            |     |     |     |     |     |     |

Table1:GPUServerStatistics.
|     |     |     |     |     |     |     | Server      |     | DGX-V100    |        | Siton       | DGX-A100    |     |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ----------- | ------ | ----------- | ----------- | --- |
|     |     |     |     |     |     |     | GPUType     |     | 16GB-V100x8 |        | 40GB-A100x8 | 80GB-A100x8 |     |
|     |     |     |     |     |     |     | NVLinkTopo. |     | Kc=2,Kg=4   |        | Kc=4,Kg=2   | Kc=1,Kg=8   |     |
|     |     |     |     |     |     |     | PCIeGen.    |     |             | 3.0x16 | 4.0x16      | 4.0x16      |     |
|     |     |     |     |     |     |     |             |     | 4switches,  |        | 2switches,  | 4switches,  |     |
PCIeTopo.
Figure7:Anexampleoffine-grainedGNNtrainingpipeline 2GPUs/switch 4GPUs/switch 2GPUs/switch
| for2-hopGraphSAGEmodel. |     |     |     |     |     |     | CPUMem.          |     |     | 384GB | 1TB | 1TB |     |
| ----------------------- | --- | --- | --- | --- | --- | --- | ---------------- | --- | --- | ----- | --- | --- | --- |
|                         |     |     |     |     |     |     | CPUCoreNum.      |     |     | 96    | 104 | 128 |     |
|                         |     |     |     |     |     |     | Sockets,NUMANum. |     |     | 2,1   | 2,2 | 2,1 |     |
searchtowardsS andS togettheboundaryindexes Table2:DatasetStatistics.
|     | Tsum | Fsum |     |     |     |     |     |     |     |     |     |     |     |
| --- | ---- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ofvertices,respectively.
Third,wegettheR T andU F accordingtoEquations4and7. Dataset PR PA CO UKS UKL CL
| Todoso,wecalculatethecumulativesumofA |     |     |      | andA         | bya |     |          |     |      |           |      |       |       |
| ------------------------------------- | --- | --- | ---- | ------------ | --- | --- | -------- | --- | ---- | --------- | ---- | ----- | ----- |
|                                       |     |     |      | T            | F   |     | Vertices |     | 2.4M | 111M 65M  | 133M | 0.79B | 1B    |
| parallelinclusivescanandgetA          |     |     | andA | .Thenforeach |     |     |          |     |      |           |      |       |       |
|                                       |     |     | Tsum | Fsum         |     |     | Edges    |     | 120M | 1.6B 1.8B | 5.5B | 47.2B | 42.5B |
cacheplan,welookupA andA withtheboundaryin- TopologyStorage 640M 6.4GB 7.2GB 22GB 189GB 170GB
Tsum Fsum
| dexesofverticessetV |     | ,V  | ,andget∑ |     | a (v) |     |     |     |     |     |     |     |     |
| ------------------- | --- | --- | -------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
Tcache Fcache v∈VTcache T FeatureSize 100 128 256 256 128 128
and∑ v∈VFcache a F (v),respectively.Similarly,afterlookupthe FeatureStorage 960M 56GB 65GB 136GB 400GB 512GB
| largestindexes                         | in A | andA | ,we get∑ |     | a (v) and |                                                   |     |     |     |     |     |     |     |
| -------------------------------------- | ---- | ---- | -------- | --- | --------- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|                                        | Tsum |      | Fsum     | v∈V | F         |                                                   |     |     |     |     |     |     |     |
| a (v).Assuch,wecangetthecorrespondingR |      |      |          |     | and       |                                                   |     |     |     |     |     |     |     |
| ∑ v∈V F                                |      |      |          |     | T         | onthesampledresults.Forthesamebatch,graphsampling |     |     |     |     |     |     |     |
U F .
andgraphconstructioncanbeoverlappedwithfeatureextrac-
| Atlast,wecalculateN           |     | andN | foreachcacheplanaccord- |                |     |       |     |     |     |     |     |     |     |
| ----------------------------- | --- | ---- | ----------------------- | -------------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
|                               |     | T    | F                       |                |     | tion. |     |     |     |     |     |     |     |
| ingtoEquation5and8.ThenwegetN |     |      | total                   | byEquation2and |     |       |     |     |     |     |     |     |     |
searchinparallelforthesmallestN withthecorrespond- 6 Evaluation
total
ingα.
Aftergettingtheoptimalcacheplans(B,α),Legioncan
6.1 ExperimentalSetting
automaticallyallocatethecachespaceandfillupthecache.
ExperimentalPlatform.Theexperimentsareconductedus-
5 ImplementationofLegion ingthreedifferentGPUservers:DGX-V100,Siton,andDGX-
Legionmainlyconsistsoftwocomponents,whicharethesam- A100,asshowninTable1.ForDGX-A100,wesettheupper
plingserverandthetrainingbackend.Thesamplingserveris limitofGPUmemoryto40GB.
implementedfromscratchandthetrainingbackendisbuilt GNN Models. We use two sampling-based GNN models:
ontopofPytorch[31]. Thesamplingserverisresponsible GraphSAGE[16]andGCN[22],whichbothadopta2-hop
randomneighborsampling.Thesamplingfan-outsare25and
forgeneratingsampledresults,andthetrainingbackendtakes
thesampledresultsasinputtotraintheGNNmodels. 10.Thedimensionofthehiddenlayersinbothmodelsisset
InLegion,everyGPUexecutesthegraphsampling,feature to256.Similartoexistingwork[46],thebatchsizeissetto
extraction,andmodeltrainingstages,andallthesestagesare 8000.Unlessexplicitlyexplained,nodeclassificationisused
| scheduledinafine-grainedpipelinetofullyutilizetheGPU |     |     |     |     |     | astheGNNtask. |     |            |     |                 |     |             |       |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | ------------- | --- | ---------- | --- | --------------- | --- | ----------- | ----- |
|                                                      |     |     |     |     |     | Datasets.     |     | We conduct |     | our experiments |     | on multiple | real- |
computationcycles.Figure7illustrateshowthetrainingpro-
cessispipelinedfora2-hopGraphSAGE[16]model.Inorder worldgraphdatasetswithvariousscales.Table2showsthe
toimprovetheoverallthroughput,wedesignaninter-batch dataset characteristics. The Products (PR) and Paper100M
pipelineoverlappingthetasksofthesamplingserverandthe (PA)areavailableinOpenGraphBenchmark[17].TheCom-
training backendfordifferentbatches. E.g.,the training of Friendster(CO)graphisanonlinegamingnetwork[45].And
| B       |                   |      |              |     |         | theUk-Union(UKS),UK-2014(UKL),andClue-web(CL) |     |     |     |     |     |     |     |
| ------- | ----------------- | ---- | ------------ | --- | ------- | --------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| batch i | can be overlapped | with | the sampling | and | feature |                                               |     |     |     |     |     |     |     |
extractionofbatchB .Tofurtherimprovethethroughput arefromWebGraph[2–5].AsCO,UKS,UKL,andCLhave
i+1
ofsamplingandfeatureextraction,wedesignanintra-batch no feature,we manually generate the features with the di-
pipeline inside the sampling server. Specifically,we break mensionspecifiedas128or256.FollowingPR’ssetting,we
downtheworkloadsofthesamplingserverintofourtypes, choose10%ofverticesfromeachgraphastrainingvertices.
eachofwhichcorrespondstoatypeofoperator:(1)Batch Baselines. We use DGL [41], PaGraph [23] and
generatorshufflesthelocaltrainingverticestogenerateseeds GNNLab[46]asthebaselinesystems.TheDGLversionis
forminibatches;(2)NeighborsamplerexecutestheL-hop v0.9.1,whichsupportsaccessinggraphtopologyandfeatures
neighborsampling;(4)Featureextractorextractsthefeature viatheUVAtechnique.Wedon’tcomparewithQuiver[33]in
of the batch seeds and vertices in the sampled results; (4) theoverallperformanceexperimentasitsopen-sourcedver-
Graphconstructorisusedtogeneratingthesubgraphbased sioncannotsupporttrainingonserverswith8GPUs.Instead,

(a)DGX-V100,GraphSAGE (b)DGX-V100,GraphSAGE (c)DGX-A100,GraphSAGE (d)DGX-A100,GraphSAGE
(e)DGX-V100,GCN (f)DGX-V100,GCN (g)DGX-A100,GCN (h)DGX-A100,GCN
Figure8:OverallperformanceofLegioncomparingwithstate-of-the-artsystems.“×”denotesOOM(outofmemory).
weimplementaQuiver-likemulti-GPUcachemechanismin ory.PaGraphrunsoutoftheCPUmemoryformostgraphs
LegionforcomparisoninSection6.3. exceptforPRonDGX-V100,asthememorymanagement
inPaGraphincursextramemoryoverheads,includingdupli-
6.2 End-to-endPerformance cated multi-hop neighbors in CPU memory and redundant
intermediatebuffersgeneratedduringcomputation.
Wecomparetheend-to-endperformanceofLegionwithbase- Speedup over SOTA system on small graphs. Legion
linesystemsontheDGX-V100andDGX-A100servers.On achieves1.39-4.18×speedupforGraphSAGE(1.29-4.32×
the DGX-V100 server,we evaluate PR,PA,CO,andUKS speedupforGCN)overGNNLabonthesmallgraphs(PR,PA,
graphs whose graphtopology andfeatures can fitinto 384 CO).Theperformancegainmainlycomesfromtwoaspects.
GBCPUmemory.OntheDGX-A100server,weevaluateall First,Figure8band8fshowthatLegionsignificantlyreduces
sixgraphs.AsPaGraphandGNNLabareimplementedusing thePCIetrafficforPAandCO,asithasascalablemulti-GPU
CUDA10whichcannotsupportA100GPU,weexcludethem cachedesigncomparedwithGNNLab.ThereductionofPCIe
fromtheexperimentsusingDGX-A100. trafficrelievestheCPU-GPUcommunicationbottlenecksuch
BaselineConfiguration.Forallthebaselines,wemanually thattheoverallperformanceisimproved.Second,Legioncan
adjusttheirconfigurationstoachieveoptimalperformance. use all GPUs for model training,while GNNLab needs to
DGLusestheUVAmode,wheresamplingisperformedin allocateseveralGPUsforsamplingexclusivelyduetoitsfac-
GPU,and the topology and features are all stored in CPU toreddesign.InLegion,thegraphsamplingisoverlappedby
memory.ThenumberofworkerthreadsinPaGraphissettobe modeltrainingduetothefine-grainedpipeline(seeSection5).
64tomaximizetheCPUsamplingthroughput.ForGNNLab, E.g.,whentrainingGraphSAGEusingthePRdataset,allthe
weadjustthenumbersofsamplingandtrainingGPUssuch topologyandfeaturedatacanbestoredinGPUmemoryin
thattheoverallthroughputismaximized.Incontrast,Legion bothLegionandGNNLab.However,Legioncanuse8GPUs
reliesonitsautomaticcachemanagementmechanismtogen- fortraining while GNNLab only uses 4 GPUs fortraining
eratetheunifiedcacheplan. (seeFigures8a).
EvaluationMetrics. Werecordtheaverageepochtimefor
6.3 EffectofHierarchicalPartitioning
allsystems.WealsousePCM[18]tomeasurethemaximum
PCIe counter value across different sockets and report the Inthisexperiment,weexaminetheeffectofhierarchicalpar-
normalizedvaluesbasedontheresultofDGLforallsystems. titioninginLegion.Wereportthecachehitratesunderdiffer-
Supporttrainingonlargegraphs. AsshowninFigures8a, entpartitionstrategiesinallthreeGPUservers:DGX-V100
8e,8c and 8g,Legion outperform all the baseline systems (NV4:K =2andK =4),Siton(NV2:K =4andK =2)
c g c g
in every setting. Specifically,Legion achieves 3.78-5.69× andDGX-A100(NV8:K =1andK =8).
c g
speedup for GraphSAGE (3.5-5.19× for GCN) on DGX-
V100and2.89-4.77×speedupforGraphSAGE(2.34-4.45×
6.3.1 CachePerformance
forGCN)onDGX-A100overDGL(UVA).Figures8b,8f,8d
and8hshowthat,comparedwiththebaselines,Legioncan Baselines. Fora faircomparison,we implementthe cache
sufficiently utilize the multi-GPU cache to minimize PCIe designsofGNNLab,PaGraph-plus(describedinSection3.1),
trafficincurredbyCPU-GPUdatatransferring.GNNLabruns andQuiver-plusinLegionandcomparetheircachehitrates.
outofGPUmemoryforUKSonDGX-V100asthesizeof Specifically,GNNLabmaintainsagloballyreplicatedcache
graph topology exceeds the capacity of single GPU mem- among all GPUs without using NVLinks (noPart+noNV).

Figure9:Effectofgraphpartitionstrategies(NoPart:nopartitioning;Edge-cut:partitioningminimizingedge-cut;Hierarchical:
hierarchicalpartitioning)tomulti-GPUcacheintermsofcachehitrate,withdifferentNVLinkinfrastructures.(noNV:disable
NVLinks;NV2:K =4andK =2;NV4:K =2andK =4;NV8:K =1andK =8;).
c g c g c g
.
with Quiver-plus. Forthe case of NV8,as all GPUs are in
thesameNVLinkclique,theinter-cliquegraphpartitioning
inLegioncanbeskipped,andhierarchicalpartitioningturns
intohashpartitioningamongalltheGPUs,whichisidenti-
caltoQuiver-plusinthecaseofNV8.Legionoutperforms
PaGraph-plus because it has much less cache duplication.
Specifically,PaGraph-plus’scachemechanismmayreplicate
vertices withhighglobalhotness on multiple GPUs. Com-
paredwithGNNLab,Legionhashighercachehitratesasit
canscaleupthecachecapacitywiththeincreaseofGPUs,
whileGNNLabreplicatesthesamefeaturecacheacrossall
GPUs.TheseresultsdemonstratethatLegioncaneffectively
Figure10:DatatransferringinfeatureextractionofPAdataset
adaptthecacheplantooptimizethecacheperformancefor
onDGX-V100(NV4).Therowsandcolumnsofeachmatrix
multi-GPUserverswithvariousNVLinktopologies.
denotethedestinationandsourceofdatatransferring. The
right-most(red)columnrecordsthedatatransferringvolume
fromCPUtoGPUviaPCIe.Themiddle(green)columnsrep- 6.3.2 DataTransferringinFeatureExtraction
resenttheGPU-GPUdatatransferringvolume.Wenormalize
Inthisexperiment,wedemonstratetheGPU-GPUandCPU-
therecordedvaluesbasedontheCPU-GPUdatatransferring
GPUdatatransferringvolumeduringfeatureextractionusing
volumesinGNNLab.
thePAdataset.Specifically,weperformthegraphsampling
Quiver-plusenablesNVLinkandmaintainsreplicatedcache and feature extraction stages using the PA graph on DGX-
among NVLink cliques (noPart+NV2 / noPart+NV4 / V100(NV4)andrecordthedatatransferringvolumesoffea-
noPart+NV8).PaGraph-plustakestheXtraPulp[34]partition- tureextractiononeachGPUintheformatofatrafficmatrix.
ingwhichminimizesacross-partitionedge-cutsanddisables WeuseGNNLab,PaGraph-plus,andQuiver-plusasthebase-
NVLinks (Edge-cut+noNV). Legion uses hierarchical par- lines,andsetthe feature cache ratio on eachGPU to 2.5%
titioning (inter-NVLink-clique partitioning: XtraPulp) and |V|.TheresultsarepresentedinFigure10.Wecanseethat
enables NVLink (Hierarchical+NV2 / Hierarchical+NV4 / Legion’sdatatransferringvolumefromCPUtoGPUisthe
Hierarchical+NV8).Weusethepre-samplinghotnessmetric smallest,indicatingthebestcacheperformanceamongthe
forallthesecachedesigns.Thein-degree-basedhotnessmet- comparedsystems. As itis the GPU withthe largestCPU-
ricintheoriginalPaGraphandQuiverdesignarereplaced GPUdatatransferringvolumethatdominatestheoverallper-
with the pre-sampling hotness metric in Pagraph-plus and formance,although Legion’s CPU-GPU volumes on some
Quiver-plus, which has a better performance on cache hit GPUsarehigherthanPaGraph-plus,Legioncanstilloutper-
rates[46]. formPaGraph-plusbecauseitslargestCPU-GPUvolumeis
ThedatasetsusedinthisexperimentarePR,CO,UKL,and lowerthanthatofPaGraph-plus.
CL.Wevarythecacheratiofrom1.25%|V|to10%|V|for
6.3.3 ModelConvergence
PRandCO.ForUKLandCLwhosesizesarerelativelylarge,
the cache ratio varies from 1.25% |V| to 5% |V|. Figure 9 Comparedwithglobalshuffling(randomlygeneratingbatch
showsthat,foralmostalltheexperimentsettings,Legionhas seeds from the vertex set of the entire graph),recent stud-
thehighestcachehitrate.Specifically,Legionobviouslyout- ies[23,28]showthatlocalshuffling(generatingbatchseeds
performs Quiver-plus in the cases of NV2 and NV4,since within partitions) brings negligible impact on the rate of
Legioncanreducetheinter-NVLink-cliquecacheduplication model convergence. Legion adopts local shuffling,and we
andachieveshighermulti-GPUmemoryutilizationcompared conductanexperimentontheSitonserver(NV2)tocompare

|     | (a)GraphSAGE |     |     | (b)GCN |     |     |     | (a)PA,SingleGPU |     |     | (b)UKS,DGX-V100(NV4) |     |     |     |
| --- | ------------ | --- | --- | ------ | --- | --- | --- | --------------- | --- | --- | -------------------- | --- | --- | --- |
Figure 11: Comparing local shuffling and global shuffling Figure13:Evaluationofcostmodel.Thelefty-axismeans
onmodelconvergence(NoPart:nopartitioning;Hierarchical: the PCIe transaction number predicted by the cost model.
hierarchicalpartitioning). Therighty-axisrepresentstheexperimentalper-epochgraph
samplingandfeatureextractiontime.
Table3:EvaluationofPartitioningCost.
|     |     |     |     |     |     |     |                                  |                            | Dataset             |     |     | PA(DGX-V100) | UKL(Siton) |      |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------- | -------------------------- | ------------------- | --- | --- | ------------ | ---------- | ---- |
|     |     |     |     |     |     |     |                                  |                            | GraphPartition(min) |     |     | 7.2          |            | 75   |
|     |     |     |     |     |     |     | DataLoadingFromDiskToMemory(min) |                            |                     |     |     | 0.32         |            | 3.5  |
|     |     |     |     |     |     |     |                                  | NodeClassificationEpoch(s) |                     |     |     | 1.98         |            | 15.6 |
|     |     |     |     |     |     |     |                                  | LinkPredictionEpoch(min)   |                     |     |     | 49.8         |            | 402  |
Figure12:Theimpactoftopologycache.“×”meansOOM
(outofmemory).
Specifically,wecomparethepredictedPCIetrafficwiththe
itsconvergencespeedwithglobalshufflingonbothGraph- experimentalper-epochexecutiontimeofgraphsamplingand
SAGEandGCNusingthePRdataset.TheresultsinFigure11 feature extraction. In the experiment using the PA dataset,
showthatthelocalshufflingofLegioncouldcatchupwith
theGPUmemoryallocatedforthecacheis10GB.Andin
theconvergencespeedofglobalshuffling. theexperimentusingtheUKSdataset,theGPUmemoryal-
locatedforthecacheis8GB.Whenvaryingthesizeofthe
6.4 EffectofUnifiedCache topologycache,thesizeofthefeaturecacheisadjustedac-
cordingly.Figure13showsthatourcostmodelcanprecisely
Differentfromexistingcache-basedsystems,Legion’suni- predictthetrendofper-epochexecutiontimewithoutmanual
| fied | cache | also takes graph | topology | into account. |     | In this | interference. |     |     |     |     |     |     |     |
| ---- | ----- | ---------------- | -------- | ------------- | --- | ------- | ------------- | --- | --- | --- | --- | --- | --- | --- |
experiment,wedemonstratethebenefitsoftopologycache.
|     |         |              |           |                |     |     | 6.6 | PartitioningCost |     |     |     |     |     |     |
| --- | ------- | ------------ | --------- | -------------- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- |
| We  | compare | the training | epochtime | ofunifiedcache |     | in  |     |                  |     |     |     |     |     |     |
Legion with two baselines: (1) storing all topology in the Inthisexperiment,westudythepartitioningcostinLegion.
WerunourexperimentontheUKLdatasetthathasthelargest
| CPU | (denoted | as TopoCPU) | and (2) | replicating | the | entire |     |     |     |     |     |     |     |     |
| --- | -------- | ----------- | ------- | ----------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
topologyineverysingleGPU(denotedasTopoGPU).Fora numberofedgesamongallthedatasets,resultinginthehigh-
faircomparison,weimplementbothTopoCPUandTopoGPU estcostofedge-cutpartitioning.Wealsopresenttheresults
in Legion and use the same GPU memory volume for the ofthePAdata(mediumsize)toshowthepartitioningcosts
threesettings.Amongthethreesettings,TopoCPUhasthe of different graph scales. We partition PA on DGX-V100
|     |     |     |     |     |     |     | andUKLonSitonusingtheXtraPulpalgorithm. |     |     |     |     |     | Fornode |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------- | --- | --- | --- | --- | --- | ------- | --- |
mostGPUmemoryavailableforthefeaturecache,andthe
TopoGPUhastheleastGPUmemoryforthefeaturecacheor classification,wesetthetrainingsettobe10%ofthetotal
evenrunsoutofGPUmemory.WeevaluatePA,CO,andUKS edgesforbothgraphs.Forlinkprediction,wesetthetraining
onDGX-V100andevaluateUKLandCLonDGX-A100. settobe80%oftotaledges.Whenthegraphistoolargeto
AsshowninFigure12,theunifiedcacheoutperformsthe bepartitionedinmemory,likeUKL,werandomlysamplea
fractionofedges(25%forUKL)andkeepallverticesinthe
othertwobaselinesforallgraphs.Thisresultdemonstrates
that,whenthesizeofthefeaturecacheexceedsathreshold, graphsuchthatthesubgraphcanbepartitionedinmemory.
theincreaseofcachehitrateslowsdown.Inthiscase,caching Thistechniquecanobviouslyspeedupgraphpartitioningand
somehottopologydatainGPUmemorywillsavethesystem preservesalowedge-cutratio.
fromseverePCIecontentionincurredbygraphsamplingand Table3showsthepreprocessingcostofLegion’shierar-
benefittheoverallGNNtrainingthroughput. chicalpartitioning.Weobservethatthepartitioningcostis
|     |     |     |     |     |     |     | tolerable,because |     |     | 1) we only | partition | the | graph once | but |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | ---------- | --------- | --- | ---------- | --- |
6.5 EvaluationofCostModel
|     |     |     |     |     |     |     | can | use | the partitioning | results | for | multiple | GNN | training |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | ------- | --- | -------- | --- | -------- |
jobs,and2)theGNNtasklikelinkpredictionneedsmultiple
| Legion | proposes | the cost | model to guide | allocating |     | GPU |     |     |     |     |     |     |     |     |
| ------ | -------- | -------- | -------------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
epochstoconvergewhileasingleepochoftencostsalong
memoryforbothgraphtopologyandfeaturecache.Inthis
| experiment,weevaluatetheeffectivenessofthismechanism. |     |     |     |     |     |     | timetofinish. |     |     |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- |

7 RelatedWork contrast,LegionfocusesonutilizingGPUcachestominimize
PCIetrafficfromCPUmemorytomultipleGPUs,whichis
Toourknowledge,Legionisthefirstworkthatautomatically
pushestheenvelopeofmulti-GPUsystemsforbillion-scale orthogonaltotheabovesystems.
GNNtraining.Inthefollowing,wecontrastLegionandexist- 8 Conclusion
ingworksinthefollowingaspects.
WepresentLegion,asystemthatautomaticallypushesthe
| GNNFrameworks. |     | SeveralGNNsystems[11,12,20,23,26, |     |     |     |     |     |     |     |     |     |
| -------------- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
33,37,41,42,46,50,52,54]haveemergedinrecentyears.Most envelopeofmulti-GPUsystemsforbillion-scaleGNNtrain-
oftheseGNNsystemsarebuiltontopofdeeplearningframe- ing.Legionhasthreekeyinnovations.First,weproposean
NVLink-awarehierarchicalpartitioningtechniquethathelps
workslikePytorch[31],TensorFlow[1]andMXNet[9].
GPUSampling. NextDoor[19]andC-SAW[30]focuson minimizecachereplicationandextendsthethresholdofcache
capacitybeyondthelimitofasingleGPUorNVLinkclique.
acceleratingGPUsamplingkernel.DGL[41]alsosupports
GPUsamplinginitsrecentrelease.Quiver[33]cansupport Second, we propose a novel hotness-aware unified cache
GPUsamplingwiththeentiretopologyeitherstoredinthe mechanismthathelpsacceleratebothgraphsamplingandfea-
tureextraction.Third,wepresentanautomaticcachemanage-
singleGPUorintheCPUmemory.GNNLab[46]adoptsa
factoreddesignwhereeachGPUisdedicatedtographsam- mentmechanismenablingoptimalcacheplanningwithoutre-
quiringextraknowledgeofhardwarespecificationsandGNN
plingormodeltrainingexclusively.Incontrast,Legionuses
allGPUsforend-to-endGNNacceleration. performancedetailsfromusers. ExperimentsshowLegion
GraphPartitioning. Graphpartitioningsuchas [6,14,15, outperformsSOTAcache-basedGNNsystemsupto4.32×
andsupportstrainingonbillion-scalegraphs.AndLegionis
21,32,34,35,38],hasbeenwidelyadoptedinGNNsystems.
DGL [41] adopts METIS [21] to partition the graph. Pa- open-sourcedathttps://github.com/RC4ML/Legion.
Graph[23]adoptsaself-reliantpartitioningstrategywiththe Acknowledgements. WethankourshepherdAnandIyerand
goalofachievingbalancedtrainingvertexallocationacross anonymousreviewersfortheirdetailedfeedback.Theworkis
GPUsandimprovingdatalocalityoneveryGPU.DGCL[7] supportedbythefollowinggrants:theProgramofZhejiang
ProvinceScienceandTechnology(2022C01044),aresearch
adoptsapartitioningalgorithmtopartitionthegraph’sphys-
ical edges and features and store them among distributed grant from Alibaba Group through the Alibaba Innovative
machines.Incontrast,Legionadoptshierarchicalpartitioning Research(AIR)Program,theFundamentalResearchFunds
fortheCentralUniversities226-2022-00151,KeyLaboratory
| to automatically |     | partition | graphs | to  | each GPU | in  | a single |     |     |     |     |
| ---------------- | --- | --------- | ------ | --- | -------- | --- | -------- | --- | --- | --- | --- |
multi-GPUserveraccordinglytoGPUinterconnections. forCornealDiseasesResearchofZhejiangProvince,Starry
NightScienceFundofZhejiangUniversityShanghaiInstitute
| GPU Feature |     | Cache. | PaGraph |     | [23], | BGL | [24], |     |     |     |     |
| ----------- | --- | ------ | ------- | --- | ----- | --- | ----- | --- | --- | --- | --- |
GNNLab [46], Quiver [33] and [29] explore feature forAdvancedStudy(SN-ZJU-SIAS-0010).ZekeWangand
cachingonGPUtoaccelerateGNNtraining.PaGraph[23] FeiWuarethecorrespondingauthors.
andQuiver[33]usethein-degreeofvertexesasthehotness
| metric. BGL | [24] | applies | a   | FIFO | dynamic | cache | policy |     |     |     |     |
| ----------- | ---- | ------- | --- | ---- | ------- | ----- | ------ | --- | --- | --- | --- |
References
| and selects | training | vertices |     | in a BFS | order | for | a higher |     |     |     |     |
| ----------- | -------- | -------- | --- | -------- | ----- | --- | -------- | --- | --- | --- | --- |
cache hit rate, but hinders model convergence and incurs [1] Martín Abadi, Paul Barham, Jianmin Chen, Zhifeng
| cachereplacementoverheads. |     |     |     | [29]usesaweightedreverse |     |     |     |     |     |     |     |
| -------------------------- | --- | --- | --- | ------------------------ | --- | --- | --- | --- | --- | --- | --- |
Chen,AndyDavis,JeffreyDean,MatthieuDevin,San-
PageRankalgorithmasahotnessmetric.GNNLab[46]uses jay Ghemawat, Geoffrey Irving, Michael Isard, Man-
| vertices’ | access | frequencies | in  | the | pre-sampling |     | epoch as |                |                  |              |     |
| --------- | ------ | ----------- | --- | --- | ------------ | --- | -------- | -------------- | ---------------- | ------------ | --- |
|           |        |             |     |     |              |     |          | junath Kudlur, | Josh Levenberga, | Sherry Moore | Ra- |
a hotness metric. In contrast,Legion automatically caches jat Monga, Derek G. Murray, Benoit Steiner, Paul
both features and topology with the highest hotness. And Tucker,VijayVasudevan,MartinWickePeteWarden,
Legionstaticallypartitionsthegraphwithminimaledge-cut
|     |     |     |     |     |     |     |     | YuanYu,andXiaoqiangZheng. |     | Tensorflow:asystem |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------- | --- | ------------------ | --- |
to preserve intra-partition data locality. Figures 9 and 11 forlarge-scalemachinelearning. InOSDI,2016.
| show that | Legion | can | achieve | a high | cache | hit | rate even |     |     |     |     |
| --------- | ------ | --- | ------- | ------ | ----- | --- | --------- | --- | --- | --- | --- |
[2] PaoloBoldi,BrunoCodenotti,MassimoSantini,andSe-
| with small | cache | ratios | without | compromising |     | the | model |                |                                      |     |     |
| ---------- | ----- | ------ | ------- | ------------ | --- | --- | ----- | -------------- | ------------------------------------ | --- | --- |
|            |       |        |         |              |     |     |       | bastianoVigna. | Ubicrawler:Ascalablefullydistributed |     |     |
convergencerate.
LargeGraphSystems.SSD-basedGNNsystems[40]and webcrawler. Software:Practice&Experience,2004.
| distributedGNN |     | systems | [12,24,51,53] |     | also | aim | atlarge- |     |     |     |     |
| -------------- | --- | ------- | ------------- | --- | ---- | --- | -------- | --- | --- | --- | --- |
[3] PaoloBoldi,AndreaMarino,MassimoSantini,andSe-
graphtrainingandproposedistinctapproachestosolveI/O
|     |     |     |     |     |     |     |     | bastiano Vigna. | Bubing: Massive | crawling | for the |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --------------- | -------- | ------- |
problemsatvariouslevels.MariusGNN[40]minimizesI/O
masses. InWWW,2014.
| between SSD | and | CPU | by including |     | valid | graph | data in a |     |     |     |     |
| ----------- | --- | --- | ------------ | --- | ----- | ----- | --------- | --- | --- | --- | --- |
single swap as much as possible. Systems like BGL [24], [4] PaoloBoldi,MarcoRosa,MassimoSantini,andSebas-
DistDGLv2[53],andP3[12]optimizenetworkI/Obetween tianoVigna. Layeredlabelpropagation: Amultireso-
distributed machines, whose network performance can be lutioncoordinate-freeorderingforcompressingsocial
improvedwhenintroducingGPU-centricSmartNIC[43].In networks. InWWW,2011.

[5] Paolo Boldi and Sebastiano Vigna. The web graph [19] Abhinav Jangda,Sandeep Polisetty,Arjun Guha,and
framework:Compressiontechniques. InWWW,2004. MarcoSerafini. Acceleratinggraphsamplingforgraph
|     |     |     |     | machinelearningusinggpus. |     |     |     | InEurosys,2021. |     |     |
| --- | --- | --- | --- | ------------------------- | --- | --- | --- | --------------- | --- | --- |
[6] ErikGBoman,KarenDDevine,andSivasankaranRa-
jamanickam. Scalable matrix computations on large [20] ZhihaoJia,SinaLin,MingyuGao,MateiZaharia,and
scale-free graphs using 2d graph partitioning. In SC, Alex Aiken. Improving the accuracy,scalability,and
|     |     |     |     | performanceofgraphneuralnetworkswithroc. |     |     |     |     |     | MLSys, |
| --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | ------ |
2013.
2020.
| [7] Zhenkun | Cai,XiaoYan,Yidi | Wu,KaihaoMa,James |     |     |     |     |     |     |     |     |
| ----------- | ---------------- | ----------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Cheng,andFanYu.DGCL:Anefficientcommunication [21] GeorgeKarypisandVipinKumar. Metis:Asoftware
libraryfordistributedGNNtraining. InEurosys,2021. packageforpartitioningunstructuredgraphs,partition-
|     |     |     |     | ing | meshes,andcomputing |     |     | fill-reducing |     | orderings of |
| --- | --- | --- | --- | --- | ------------------- | --- | --- | ------------- | --- | ------------ |
[8] JieChen,TengfeiMa,andCaoXiao. Fastgcn:fastlearn- sparsematrices. 1997.
ingwithgraphconvolutionalnetworksviaimportance
sampling. arXivpreprintarXiv:1801.10247,2018. [22] Thomas N Kipf and Max Welling. Semi-supervised
arXiv
classificationwithgraphconvolutionalnetworks.
[9] TianqiChen,MuLi,YutianLi,MinLin,NaiyanWang,
preprintarXiv:1609.02907,2016.
MinjieWang,TianjunXiao,BingXu,ChiyuanZhang,
andZhengZhang. Mxnet:Aflexibleandefficientma- [23] ZhiqiLin,ChengLi,YoushanMiao,YunxinLiu,and
|     |     |     |     | Yinlong | Xu. | Pagraph: |     | Scaling | gnn training | on large |
| --- | --- | --- | --- | ------- | --- | -------- | --- | ------- | ------------ | -------- |
chinelearninglibraryforheterogeneousdistributedsys-
tems. arXivpreprintarXiv:1512.01274,2015. graphsviacomputation-awarecaching. InSoCC,2020.
[10] Wei-LinChiang,XuanqingLiu,SiSi,YangLi,Samy [24] TianfengLiu,YangruiChen,DanLi,ChuanWu,Yibo
Bengio,andCho-JuiHsieh. Cluster-gcn:Anefficiental- Zhu,JunHe,YanghuaPeng,HongzhengChen,Hongzhi
gorithmfortrainingdeepandlargegraphconvolutional Chen,and Chuanxiong Guo. Bgl: Gpu-efficient gnn
networks. InSIGKDD,2019. trainingbyoptimizinggraphdatai/oandpreprocessing.
arXivpreprintarXiv:2112.08541,2021.
| [11] MatthiasFeyandJanEricLenssen.  |     | Fastgraphrepresen- |     |           |           |     |         |              |     |             |
| ----------------------------------- | --- | ------------------ | --- | --------- | --------- | --- | ------- | ------------ | --- | ----------- |
|                                     |     |                    |     | [25] Yang | Liu,Xiang |     | Ao,Zidi | Qin,Jianfeng |     | Chi,Jinghua |
| tationlearningwithpytorchgeometric. |     | arXivpreprint      |     |           |           |     |         |              |     |             |
arXiv:1903.02428,2019. Feng,HaoYang,andQingHe. Pickandchoose:agnn-
basedimbalancedlearningapproachforfrauddetection.
| [12] SwapnilGandhiandAnandPadmanabhaIyer. |     |     | P3:Dis- |     |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
InWWW,2021.
| tributeddeepgraphlearningatscale. |     | InOSDI,2021. |     |               |     |         |       |         |       |             |
| --------------------------------- | --- | ------------ | --- | ------------- | --- | ------- | ----- | ------- | ----- | ----------- |
|                                   |     |              |     | [26] Lingxiao |     | Ma, Zhi | Yang, | Youshan | Miao, | Jilong Xue, |
[13] Justin Gilmer,Samuel S Schoenholz,Patrick F Riley, MingWu,LidongZhou,andYafeiDai. Neugraph:Par-
Oriol Vinyals, and George E Dahl. Neural message alleldeepneuralnetworkcomputationonlargegraphs.
| passingforquantumchemistry. |     | InICML,2017. |     | InUSENIXATC,2019. |     |     |     |     |     |     |
| --------------------------- | --- | ------------ | --- | ----------------- | --- | --- | --- | --- | --- | --- |
[14] Joseph E Gonzalez,Yucheng Low,Haijie Gu,Danny [27] Mark Harris. Unified Memory for CUDA Be-
Bickson,andCarlosGuestrin. Powergraph:Distributed ginners. https://developer.nvidia.com/blog/
| graph-parallelcomputationonnaturalgraphs. |     |     | InOSDI, |     |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
unified-memory-cuda-beginners/,2017.
2012.
[28] QiMeng,WeiChen,YueWang,Zhi-MingMa,andTie-
[15] JosephEGonzalez,ReynoldSXin,AnkurDave,Daniel YanLiu. Convergenceanalysisofdistributedstochastic
Crankshaw,MichaelJFranklin,andIonStoica. Graphx: Neurocomputing,2019.
gradientdescentwithshuffling.
Graphprocessinginadistributeddataflowframework.
InOSDI,2014. [29] Seung Won Min, Kun Wu, Mert Hidayetoglu, Jinjun
|     |     |     |     | Xiong,XiangSong,andWen-meiHwu. |     |     |     |     |     | Graphneural |
| --- | --- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | ----------- |
[16] WillHamilton,ZhitaoYing,andJureLeskovec. Induc- networktraininganddatatiering. InSIGKDD,2022.
| tiverepresentationlearningonlargegraphs. |     |     | NeurIPS, |     |     |     |     |     |     |     |
| ---------------------------------------- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
[30] SantoshPandey,LingdaLi,AdolfyHoisie,XiaoyeSLi,
2017.
|     |     |     |     | andHangLiu. |     | C-saw:Aframeworkforgraphsampling |     |     |     |     |
| --- | --- | --- | --- | ----------- | --- | -------------------------------- | --- | --- | --- | --- |
[17] WeihuaHu,MatthiasFey,MarinkaZitnik,YuxiaoDong, andrandomwalkongpus. InSC,2020.
| Hongyu | Ren, Bowen | Liu, Michele Catasta, | and Jure |           |         |     |        |           |        |      |
| ------ | ---------- | --------------------- | -------- | --------- | ------- | --- | ------ | --------- | ------ | ---- |
|        |            |                       |          | [31] Adam | Paszke, | Sam | Gross, | Francisco | Massa, | Adam |
Leskovec.Opengraphbenchmark:Datasetsformachine
learningongraphs. NIPS,2020. Lerer,JamesBradbury,GregoryChanan,TrevorKilleen,
|     |     |     |     | Zeming | Lin, | Natalia | Gimelshein, |     | Luca | Antiga, Al- |
| --- | --- | --- | --- | ------ | ---- | ------- | ----------- | --- | ---- | ----------- |
[18] Intel. PCM. https://github.com/intel/pcm,2022. banDesmaison,AndreasKopf,EdwardYang,Zachary

DeVito,Martin Raison,Alykhan Tejani,SasankChil- [44] Wikipedia. MaxCliqueDyn. https://en.wikipedia.
amkurthy, Benoit Steiner, Lu Fang, Junjie Bai, and org/wiki/MaxCliqueDyn_maximum_clique_
algorithm,2022.
| SoumithChintala.                |     | Pytorch:Animperativestyle,high- |     |               |     |                                 |     |     |     |                   |     |     |
| ------------------------------- | --- | ------------------------------- | --- | ------------- | --- | ------------------------------- | --- | --- | --- | ----------------- | --- | --- |
| performancedeeplearninglibrary. |     |                                 |     | NeurIPS,2019. |     |                                 |     |     |     |                   |     |     |
|                                 |     |                                 |     |               |     | [45] JaewonYangandJureLeskovec. |     |     |     | Definingandevalu- |     |     |
[32] FabioPetroni,LeonardoQuerzoni,KhuzaimaDaudjee, atingnetworkcommunitiesbasedonground-truth. In
| Shahin | Kamali,andGiorgio |               | Iacoboni. | Hdrf:   | Stream-  | SIGKDD,2012. |     |     |     |     |     |     |
| ------ | ----------------- | ------------- | --------- | ------- | -------- | ------------ | --- | --- | --- | --- | --- | --- |
| based  | partitioning      | for power-law |           | graphs. | In CIKM, |              |     |     |     |     |     |     |
[46] JianbangYang,DahaiTang,XiaoniuSong,LeiWang,
2015.
QiangYin,RongChen,WenyuanYu,andJingrenZhou.
[33] QuiverTeam. Quiver. https://github.com/ Gnnlab:Afactoredsystemforsample-basedgnntrain-
InEurosys,2022.
| quiver-team/torch-quiver,2021. |     |     |     |     |     | ingovergpus. |     |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- |
[34] GeorgeMSlota,SivasankaranRajamanickam,Karen [47] RexYing,RuiningHe,KaifengChen,PongEksombat-
Devine,andKameshMadduri. Partitioningtrillion-edge chai,WilliamLHamilton,andJureLeskovec. Graph
InIPDPS,2017. convolutional neural networks for web-scale recom-
graphsinminutes.
|               |         |             |        |           |       | mendersystems. |     | InSIGKDD,2018. |     |     |     |     |
| ------------- | ------- | ----------- | ------ | --------- | ----- | -------------- | --- | -------------- | --- | --- | --- | --- |
| [35] Isabelle | Stanton | and Gabriel | Kliot. | Streaming | graph |                |     |                |     |     |     |     |
partitioningforlargedistributedgraphs. InSIGKDD, [48] Zhongbao Yu, Jiaqi Zhang, Xin Qi, and Chao Chen.
| 2012. |     |     |     |     |     | Application |     | research | of graph | neural | networks | in the |
| ----- | --- | --- | --- | --- | --- | ----------- | --- | -------- | -------- | ------ | -------- | ------ |
financialriskcontrol.
| [36] ChangSu,YuHou,andFeiWang.            |     |     |     | Gnn-basedbiomedi- |     |              |       |          |       |         |             |     |
| ----------------------------------------- | --- | --- | --- | ----------------- | --- | ------------ | ----- | -------- | ----- | ------- | ----------- | --- |
|                                           |     |     |     |                   |     | [49] Hanqing | Zeng, | Hongkuan | Zhou, | Ajitesh | Srivastava, |     |
| calknowledgegraphminingindrugdevelopment. |     |     |     |                   | In  |              |       |          |       |         |             |     |
GraphNeuralNetworks: Foundations,Frontiers,and Rajgopal Kannan, and Viktor Prasanna. Graphsaint:
|     |     |     |     |     |     | Graphsamplingbasedinductivelearningmethod. |     |     |     |     |     | arXiv |
| --- | --- | --- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- | ----- |
Applications.2022.
preprintarXiv:1907.04931,2019.
[37] JohnThorpe,YifanQiao,JonathanEyolfson,ShenTeng,
GuanzhouHu,ZhihaoJia,KevalVora,RaviNetravali, [50] DalongZhang,XinHuang,ZiqiLiu,ZhiyangHu,Xi-
MiryungKim,andGuoqingHarryXu. Dorylus:Afford- anzhengSong,ZhibangGe,ZhiqiangZhang,LinWang,
|     |     |     |     |     |     | JunZhou,YangShuang,andYuanQi. |     |     |     |     | Agl:ascalable |     |
| --- | --- | --- | --- | --- | --- | ----------------------------- | --- | --- | --- | --- | ------------- | --- |
able,scalable,andaccuratenntrainingwithdistributed
cpuserversandserverlessthreads. InOSDI,2021. systemforindustrial-purposegraphmachinelearning.
arXivpreprintarXiv:2003.02454,2020.
[38] CharalamposTsourakakis,ChristosGkantsidis,Bozidar
|            |     |                     |     |         |           | [51] Da Zheng,Chao |     | Ma,Minjie | Wang,Jinjing |     |     | Zhou,Qi- |
| ---------- | --- | ------------------- | --- | ------- | --------- | ------------------ | --- | --------- | ------------ | --- | --- | -------- |
| Radunovic, |     | and Milan Vojnovic. |     | Fennel: | Streaming |                    |     |           |              |     |     |          |
graphpartitioningformassivescalegraphs. InWSDM, dong Su,Xiang Song,Quan Gan,Zheng Zhang,and
| 2014. |     |     |     |     |     | George  | Karypis. | Distdgl: | distributed   |         | graph | neural  |
| ----- | --- | --- | --- | --- | --- | ------- | -------- | -------- | ------------- | ------- | ----- | ------- |
|       |     |     |     |     |     | network | training | for      | billion-scale | graphs. |       | In 2020 |
PetarVelicˇkovic´,GuillemCucurull,ArantxaCasanova,
| [39] |     |     |     |     |     | IEEE/ACM10thWorkshoponIrregularApplications: |     |     |     |     |     |     |
| ---- | --- | --- | --- | --- | --- | -------------------------------------------- | --- | --- | --- | --- | --- | --- |
AdrianaRomero,PietroLio,andYoshuaBengio. Graph ArchitecturesandAlgorithms(IA3),2020.
| attentionnetworks. |     | arXivpreprintarXiv:1710.10903, |     |     |     |                |       |       |         |       |           |     |
| ------------------ | --- | ------------------------------ | --- | --- | --- | -------------- | ----- | ----- | ------- | ----- | --------- | --- |
|                    |     |                                |     |     |     | [52] Da Zheng, | Xiang | Song, | Chengru | Yang, | Dominique |     |
2017.
|     |     |     |     |     |     | LaSalle,andGeorgeKarypis. |     |     |     | Distributedhybridcpu |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | -------------------- | --- | --- |
[40] RogerWaleffe,JasonMohoney,TheodorosRekatsinas, andgputrainingforgraphneuralnetworksonbillion-
and Shivaram Venkataraman. Mariusgnn: Resource- scaleheterogeneousgraphs. InSIGKDD,2022.
efficientout-of-coretrainingofgraphneuralnetworks.
|     |     |     |     |     |     | [53] Da Zheng, | Xiang | Song, | Chengru | Yang, | Dominique |     |
| --- | --- | --- | --- | --- | --- | -------------- | ----- | ----- | ------- | ----- | --------- | --- |
InEurosys,2023.
LaSalle,QidongSu,MinjieWang,ChaoMa,andGeorge
[41] MinjieYuWang. Deepgraphlibrary:Towardsefficient Karypis. Distributedhybridcpu andgpu training for
andscalabledeeplearningongraphs. InICLR,2019. graphneuralnetworks on billion-scale graphs. arXiv
preprintarXiv:2112.15345,2021.
[42] YukeWang,BoyuanFeng,GushuLi,ShuangchenLi,
LeiDeng,YuanXie,andYufeiDing. Gnnadvisor:An [54] RongZhu,KunZhao,HongxiaYang,WeiLin,Chang
adaptiveandefficientruntimesystemforgnnaccelera- Zhou,BaoleAi,YongLi,andJingrenZhou. Aligraph:
tionongpus. InOSDI,2021. acomprehensivegraphneuralnetworkplatform. VLDB,
2019.
[43] ZekeWang,HongjingHuang,JieZhang,FeiWu,and
| GustavoAlonso.        |     | FpgaNIC:AnFPGA-basedversatile |             |     |     |     |     |     |     |     |     |     |
| --------------------- | --- | ----------------------------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100gbSmartNICforGPUs. |     |                               | InATC,2022. |     |     |     |     |     |     |     |     |     |