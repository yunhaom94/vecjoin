# FlashANNS

**Source**: FlashANNS.pdf
**Format**: .pdf

---

FlashANNS: GPU-Driven I/O Pipelining for Eliminating
Storage-Compute Bottlenecks in Billion-Scale Similarity Search
YangXiao MoSun ZiyuSong BingTian
ZhejiangUniversity ZhejiangUniversity ZhejiangUniversity HuazhongUniversityof
Hangzhou,China Hangzhou,China Hangzhou,China ScienceandTechnology
12221061@zju.edu.cn sunmo@zju.edu.cn songziyu@zju.edu.cn Wuhan,China
tbing@hust.edu.cn
JieSun JieZhang ZekeWang ZonghuiWang
ZhejiangUniversity ZhejiangUniversity ZhejiangUniversity ZhejiangUniversity
Hangzhou,China Hangzhou,China Hangzhou,China Hangzhou,China
jiesun@zju.edu.cn carlzhang4@zju.edu.cn wangzeke@zju.edu.cn zhwang@zju.edu.cn
WenzhiChen FeiWu
ZhejiangUniversity ZhejiangUniversity
Hangzhou,China Hangzhou,China
chenwz@zju.edu.cn wufei@zju.edu.cn
Abstract andstorageaccesslatencyacrossdifferenthardwarecharacteristics,
ApproximateNearestNeighborSearch(ANNS)enablesefficient differentdatasets,anddifferentqueryrequirements.
similarityretrievalinhigh-dimensionalvectorspaces,andbecomes WeimplementFlashANNSandcompareitwiththreestate-of-
afundamentalcomponentofupper-layerworkloadsrangingfrom the-artout-of-coreANNSsystems(SPANN,DiskANN,andFusion-
recommendationsystemstoretrieval-augmentedgeneration(RAG).
ANNS).Experimentalresultsdemonstratethatatthesame≥95%
ModernANNSsystemsintegrateSSDstosupportterabyte-scale recall@10accuracy,ourmethodachieves2.7–5.9×higherquery
vectordatasets,primarilyemployingcluster-indexingandgraph- throughputcomparedtoexistingSOTAmethodswithasingleSSD,
indexing.However,cluster-indexingANNSsystemssufferfrom andfurtherachieves3.9–12.2×querythroughputimprovementin
suboptimalquerythroughputbecauseofthecoarse-grainedvector themulti-SSDconfigurations.
indexing,whilegraph-indexingsystemssufferfromsuboptimal
CCSConcepts
performanceduetotwoinherentlimitations:1)failingtooverlap
SSDaccesseswithdistancecomputationprocessesand2)poorI/O •Informationsystems→Informationretrievalquerypro-
performanceduetolongtaillatency. cessing;Storagemanagement.
To address these challenges, we present FlashANNS, a GPU-
acceleratedout-of-coregraph-basedANNSsystemthroughI/O- Keywords
computeoverlapping.Ourcoreinsightliesinthecarefulorches-
ApproximateNearestNeighborSearch(ANNS),Large-scalesim-
trationofI/Oandcomputationthroughthreekeyinnovations:1)
ilaritysearch,High-dimensionalvectorretrieval,Parallelquery
Dependency-relaxedasynchronouspipelinewithrigoroustheoreti-
execution
calconvergenceguarantee:FlashANNSdecouplesI/O-computation
dependenciestofullyoverlapbetweenGPUdistancecalculations ACMReferenceFormat:
andSSDdatatransfers;2)Query-grainedconcurrentSSDaccess: YangXiao,MoSun,ZiyuSong,BingTian,JieSun,JieZhang,ZekeWang,
ZonghuiWang,WenzhiChen,andFeiWu.2018.FlashANNS:GPU-Driven
FlashANNSimplementalock-freeI/Ostackwithquery-grained
I/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-Scale
concurrencycontrol,toavoidI/Operformancedegradationdueto
SimilaritySearch.InProceedingsofMakesuretoenterthecorrectconference
longtaillatency;and3)Computation-I/Obalancedgraphdegreese-
titlefromyourrightsconfirmationemail(Conference’XX).ACM,NewYork,
lection,whichensuresoptimalbalancebetweencomputationalload
NY,USA,15pages.https://doi.org/XXXXXXX.XXXXXXX
1 Introduction
Permissiontomakedigitalorhardcopiesofallorpartofthisworkforpersonalor
ApproximateNearestNeighborSearch(ANNS)referstoasetof
classroomuseisgrantedwithoutfeeprovidedthatcopiesarenotmadeordistributed
forprofitorcommercialadvantageandthatcopiesbearthisnoticeandthefullcitation methodsforfindingthetop-kvectorsmostsimilartoagivenquery
onthefirstpage.Copyrightsforcomponentsofthisworkownedbyothersthanthe vectorinahigh-dimensionalvectordataset.Comparedwithexact
author(s)mustbehonored.Abstractingwithcreditispermitted.Tocopyotherwise,or
search,ANNSsacrificesalittleprecisionformuchlessretrievaltime.
republish,topostonserversortoredistributetolists,requirespriorspecificpermission
and/orafee.Requestpermissionsfrompermissions@acm.org. ANNSiswidelyappliedinvariousdomains,includinginformation
Conference’XX,June03–05,2018,Woodstock,NY retrieval[8,24,28,39,61],recommendationsystems[13,49,56],
©2018Copyrightheldbytheowner/author(s).PublicationrightslicensedtoACM.
andlargelanguagemodels[14,30,33,37,59].Especially,theriseof
ACMISBN978-1-4503-XXXX-X/2018/06
https://doi.org/XXXXXXX.XXXXXXX generativeAIandlarge-scalerecommendationsystemshasdriven
6202
raM
2
]BD.sc[
2v07001.7052:viXra

Conference’XX,June03–05,2018,Woodstock,NY Trovatoetal.
largershareoftheend-to-endlatencyisattributabletocomputation,
indicatingthepotentialforcompute-sideoptimization.
Whilegraph-basedindexingreducesI/O,itincreasescompute
intensity,makingcomputationalargershareoflatency.Thismo-
tivatesaGPU-offloadingdirectionforcompute-sideoptimization.
However,directlyintegratingGPUsintroducesthreekeychallenges:
(1)serializedorcoarse-grainedexecutionthatfailstofullyexploit
GPUcomputecapacity;(2)fine-grainedsynchronizationthatam-
plifies I/O latency; and (3) small random SSD accesses that are
IOPS-bound,leavingSSDbandwidthunderutilized.
Figure1:ComparisonofqueryQPSperformancebetween Tothisend,wepresentFlashANNS,aGPU-accelerated,SSD-
datasetDEEP1BandDEEP2B residentgraphindexingframeworkthatbalancescomputationand
I/O for billion-scale similarity search. Our approach centers on
threekeydesigns:
• Dependency-RelaxedAsynchronousI/OPipeline. To
thedemandforbillion-scaleANNS,withmoderndatasets(often
addressthelowGPU/SSDutilizationproblemcausedbythe
exceeding1000Mvectors)andtheirindices(upto6×datasetsize)
serializedexecutionofcomputationandI/Ooperations,we
overwhelmingtraditionalin-memoryframeworksduetoprohibi-
proposeadependency-relaxedasynchronousI/Opipeline,
tivememoryandcomputationrequirements.
andprovidearigoroustheoreticalconvergenceguarantee
Astraightforwardscale-outsolutionistoemployadistributedin-
toensurethatFlashANNScanachievethesamerecall.
memorysolution[43,69]thatutilizesthehostmemoryofmultiple • Query-GrainedConcurrentSSDAccess. Toaddressthe
servers for index storage. Vearch [43] partitions a size-N index
prolongedI/Olatencyduetosynchronizationoverheadin
intonshardsofsizeN/n,eachshardisstoredintheDRAMofa
thekernel-grainedGPUI/Ostack,weproposeaquery-grained
server.Duringqueryexecution,allnodesprocessthesamequery
concurrent SSD access architecture optimized for ANNS
concurrentlyon theirlocalshards,andeach node computesits
workloads,eliminatingtheGPUkernel-grainedglobalsyn-
localtop-Kresultsfromitsassignedshard.Finally,globalresults
chronizationinherenttoconventionalCAM-basedI/Ostacks.
aremergedbysortingandtruncatingthe𝑛×𝐾localresultstoyield
Underthisarchitecture,eachquery-issuedSSDaccesscan
thefinalK-nearestneighbors.However,bringing𝑛×computation
completeandresumeexecutionindependentlywithinthe
resourcecannotincreasequerythroughputby𝑛×,mainlybecause
warpwithoutkernel-wideglobalstalls.
thequerytimedoesnotscalelinearlywiththedatasetshardsize. • Computation-I/OBalancedGraphDegreeSelection. To
AsshowninFigure1,halvingthedatasetsizecanonlyincrease
addresstheI/OamplificationduetoSSDpagerealignment,
querythroughputby10.8%-19.5%.
weproposeahardware-awaregraphdegreeselectionmecha-
Consideringthesuboptimalperformanceofscale-outsolutions,
nism.ThisapproachquantifiesSSDI/ObandwidthandGPU
recentANNSsystems[11,31,52,67,75]areequippedwithSolid
computationalcapacitythroughsampling-basedprofiling,
StateDrives(SSDs)tofitsuchhugedatasets/indices(uptotensof
enablingadaptiveselectionofgraphdegreeparametersin
Terabytes),tofurtherextendsinglenodecapacity.Accordingtothe
theindexstructure.Thismaintainscomputation-I/Oequilib-
kindofindexingmethodused,thesesystemscanbecategorized
riumthroughoutpipelineoperations.
intocluster-basedandgraph-basedsystems.Weidentifythatboth
WeimplementFlashANNSandevaluateitonwidelyadopted
ofthesesystemssufferfromlowsystemresourceutilization.
billion-scalevectordatasets(SIFT1B,SPACEV1B,DEEP1B),bench-
Cluster-BasedIndexing.Cluster-indexingmethodssuchasSPANN[11]
markingagainststate-of-the-artout-of-coreANNSsystems(SPANN,
partitionthedatasetintocluster-basedinvertedlists,storingorig-
DiskANN) and a GPU-accelerated out-of-core baseline (Fusion-
inalvectorsondiskwhilemaintainingcentroidindicesinmem-
ANNS).Experimentalresultsshowthatat≥95%recall@10accu-
ory.However,itscoarse-grainedclusteringleadstoalargecan-
racy,FlashANNSachieves2.7–5.9×higherQPSthanexistingSOTA
didate search space, requiring extensive vector comparisons in
methodswithasingleSSDconfiguration,andscalestoupto12.2×
high-precisionscenarios.
QPSimprovementsinmulti-SSDsetups.WewillmakeFlashANNS
FusionANNS[67]mitigatesthisissueviaGPU-acceleratedpre-
open-sourcedatGitHubtobenefitourcommunityoncethispaper
filtering to reduce I/O overhead by selectively fetching vectors
getsaccepted.
from SSDs. Despite this improvement, FusionANNS still incurs
highSSDaccessesduetotheinherentlimitationsofcoarse-grained
2 Background
clustering.Furthermore,itscomputationalpipelinedoesnotfully
utilizetheGPU’sprocessingcapabilityduetohighoverheadfrom TheApproximateNearestNeighborSearch(ANNS)hasemerged
theCPU-managedtasksynchronization. asafundamentaloperationinmoderndataprocessingsystems,
Graph-BasedIndexing. Fine-grainedgraphindexingsuchas enablingefficientsimilarityretrievalinhigh-dimensionalvector
DiskANN[31]canachievethetargetaccuracywithasmallercan- spaces.Asafundamentalcomponentofupper-layerworkloads
didatesize,therebyreducingthenumberofSSDfetchesandthe ranging from recommendation systems to retrieval-augmented
overallI/Ocost.However,itincreasesper-fetchcomputationalwork generation(RAG),ANNSevolvesrapidlyasthescaleofthesework-
(e.g.,distanceevaluationsandneighbormanagement).Asaresult,a loadsbecomeslargerandlarger.Vectorindexingservesasacritical

FlashANNS:GPU-DrivenI/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-ScaleSimilaritySearch Conference’XX,June03–05,2018,Woodstock,NY
Figure3:Candidatevectorsizeduringsearchingprogress
ofcluster-indexing(SPANN)andgraph-indexing(DiskANN)
underdifferentrecallaccuracy
(a)Cluster-Basedindexing
Figure 4: SSD page read requirements of FussionANNS,
SPANNandDiskANNunderdifferentrecallaccuracy
2.1 Cluster-BasedVectorIndexing
Cluster-basedvectorindexingiswidelyusedduetoitslowquery
(b)FilteredCluster-Basedindexing
latency.Thesesystemsmainlymaintaintwodatastructures:1)SSD-
residentclusteredvectorsand2)anin-memorynavigationgraph
of cluster centroids. During the index construction, the system
scanstheentirevectordatasetandpartitionsvectorsintoseveral
clusters.ThevectorsarestoredintheSSDbyclusters,whilethe
centroidofeachclusterformsagraphandisstoredintheCPU
memory.Figure2ademonstratesthethree-phasesearchworkflow
ofcluster-basedvectorindexing.
• 1.GraphTraversalPhase.Withinthein-memorycentroid
navigationgraph,thesearchprocesstraversesthegraphto
identifytheK-nearestcentroidstothequeryvector.
• 2.CandidateRetrievalPhase.Theretrievalphasefetches
clusterscorrespondingtotheselectedKcentroidsfromSSD-
(c)CPU-Basedgraphindexing residentclusteredvectors.
• 3.DistanceCalculationPhase.Thesearchprocesscom-
Figure2:Overallcomparisonofindexingarchitectures putesprecisedistancesbetweenallvectorsinretrievedclus-
tersandthequeryvector,thenranksvectorsbydistanceto
selectthefinalresult.
However,cluster-indexingANNSsystemssufferfromsubopti-
malquerythroughput,becausethesesystemsusecoarse-grained
vectorindexing,andgraphtraversalphase(1)’scomputationcan
ANNScomponent,organizingvectordataanddeterminingsearch beverylight-weight,whiletherewouldbenumerouscandidates
methodologies.Substantialindexstorageoverheadsconsumeup tobeaccessedincandidateretrievalphase(2)andcorresponding
to86%ofthequeryexecutionstoragefootprint.ModernANNS distancecalculationindistancecalculationphase(3).
systems[11,31,67]integrateSSDstosupportterabyte-scalevector Thefundamentallimitationstemsfromthegraphtraversalphase
datasetsrequiredbycontemporaryapplications. (1)’s assumption that centroids within posting lists adequately

Conference’XX,June03–05,2018,Woodstock,NY Trovatoetal.
representassociatedclustervectors.Inpractice,thisrepresentation
provestobeinaccurate,manifestingtwodistinctdeficiencies:
1.FalseInclusion.Centroidsproximatetothequerymaycor-
respondtodistantvectors,forcingcandidateretrievalphase(2)
anddistancecalculationphase(3)toprocessmassivevolumesof
irrelevantcandidates.
2.FalseExclusion.Duringcandidateretrieval(2),thesearch
processmayerroneouslyexcludedistantcentroidscontainingneigh-
boringvectors,misclassifyingthetrulynearestneighborswithin
them as distant. This initial error leads to their absence in the
candidatepool,severelydegradingqueryaccuracy. Figure5:DiskANNquerythroughputvariationwithincreas-
Figure3demonstratesthecandidatesizedisparitybetweenthe ingCPUcores
cluster-indexingimplementation(SPANN)andthegraph-indexing
implementation(DiskANN)onSIFT1B.Under81%-95%recall@10,
toachieveequivalentrecall,cluster-indexingimplementationre-
quires1.14-2.34×morecandidatesthangraph-indexing.Andthis
gapiswideningwiththeincreasingaccuracy.Thisimposesprohib-
itivecomputationalandI/Opressureduringqueries.Consequently,
DiskANNachieves1.23×to1.88×higherQPSthanSPANN.
GPU-AcceleratedCluster-BasedVectorIndexing.Tomitigate
excessivecomputationalandSSDaccessdemands,FusionANNS[67]
leveragesaGPUandstoresquantifiedvectorsinGPUmemory.
Thesevectorsreducedimensionandarequantifiedasuint8values
viaproductquantization(PQ).AsFigure2bdemonstrates,compared
Figure6:NormalizedI/Oandcomputedemandsofgraph
tothecluster-indexingapproach’sthree-phasesearchworkflow,
indexingacrossdatasets(vs.clusterindexing)
FusionANNSintroducesaGPU-basedquantizationfilteringphase
(2)betweengraphtraversal(1)andcandidateretrieval(3).
Inquantizationfilteringphase(2),theGPUcalculatesquantiza-
distancesviaamin-heap.Thenexttraversalnodeisdynami-
tiondistancesforvectorswithinclustersselectedduringgraphtra-
callyselectedfromthemin-heapbyminimalPQdistance.
versal(1)usingPQ-codedvectors.Itscreensvectorswithdistances
• 3.NeighborAccessPhase.Thesystemaccessesselected
belowapredeterminedthreshold,directingsubsequentphasesto
node’sfull-precisionvectorsanditsneighborlistsfromSSDs.
retrieveandprocessonlythesefilteredcandidatesfromSSDstorage
forexactdistancecalculations. By employing high-precision vector indexing, this approach
Despiteefficiencygainsfromquantizationfiltering,FusionANNS reducesthecandidatesizeandminimizesdistancecomputations.
canonlypartiallymitigatesevereSSDI/Opressuresbecauseitsfil- AsshowninFigure3andFigure4,DiskANNachievessignificantly
teringstagereliessolelyonPQ-compresseddistancesforcandidate smallercandidatesizeandlowerSSDaccessrequirementscompared
selection,lackingthefine-grainednavigationguidanceformedby toSPANNandFusionANNS.
exactdistances.ThisnecessitatesadditionalSSDaccessestoobtain
3 Motivation
exactdistancesforcompensatingquantizationerrors.Asshown
inFigure4,FusionANNSstillincurs1.36–1.70×moreSSDpage AsshowninFigure6,graph-indexingreducesmanymoreSSD
accessesthanDiskANNwhenevaluatingontheSIFT1Bdataset. accessesthancalculation,whichmakesthesystemeasilybottle-
neckedbythecomputation.Figure5showshowquerythroughput
changeswithvaryingCPUcorecounts.Weobservethatquery
2.2 Graph-BasedVectorIndexing
throughputscalesnearlylinearlywithcorecount.Inparticular,
To minimize SSD accesses and the corresponding computation, whenall52coresareused,theconsumedSSDthroughputisonly
emergingANNSsystems(e.g.,DiskANN[31],DiskANN++[52])use 3.7GB/s,whichisslightlyhigherthantheI/ObandwidthofaPCIe
afine-grainedvectorgraphinsteadofacoarse-grainedclustercen- 4.0x4SSD(IntelP5510[62]).Whenthesystemscalestomultiple
troidgraph.Thesesystemsmainlymaintaintwodatastructures:1) SSDs,theSSDI/Othroughputisunderutilized.
in-memoryquantifiedvectors,and2)SSD-residentadjacencylistof InspiredbyFusionANNS,whichadoptsGPUtoaddressthecom-
thevectorgraphandfull-precisionvectors.Figure2cdemonstrates putationbottleneckofpreranking,itisstraightforwardtoconsider
howgraph-indexingANNSsystemsretrieveresultsiteratively. introducing GPUs to alleviate the computational pressure from
distancecalculation.Theoveralldesignseemsstraightforward,but
• 1.DistanceCalculationPhase.Thesystemcomputesex- facesthreeseverechallenges.
actquery-to-nodedistancesandcalculatesPQdistancesfor C1:LowGPUUtilizationduetoSerializedExecutionof
neighborsusingin-memoryquantizedvectors. ComputationandI/O.Graph-indexingANNSalgorithmsinher-
• 2.TraversalStateManagementPhase.Thesystemmain- entlysufferfromafundamentalcomputationaldependency:the
tainsexactdistancesinaresultheapwhilemanagingPQ distancecalculationphaserequiresneighborvectordatastoredon

FlashANNS:GPU-DrivenI/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-ScaleSimilaritySearch Conference’XX,June03–05,2018,Woodstock,NY
Figure8:Exampledsearchpathsofbest-firstsearchvs.re-
laxeddependencysearch
Figure7:FlashANNSoverview
storagedevices,andtheneighboraccessphasefetchesdatadepend-
ingonpreliminarydistanceresults.Thiscyclicdependencycreates
unavoidablecomputationstalls.WithGPUs,accelerateddistance
calculationsmakeseverepipelineimbalance-computationcom-
pletesquicker,leadingtoalargerproportionoftimewaitingfor
I/O.Inourexperiments(§5.3),underthesamerecall@10condi-
tion,theQPSofserialexecutiondemonstrates67.6%–73.1%ofour
asynchronousexecution.
(a)Best-firstsearchpipeline
C2:ProlongedI/OLatencyduetoSynchronizationinthe
Kernel-grainedGPUI/OStack.Kernel-grainedGPUI/Ostacks
optimizeI/OthroughputviabatchedSSDaccesses,butanysin-
glelong-taillatencyeventwithinabatchpropagatesdelaystoall
co-batchedrequests.IntheGPU-acceleratedANNSsystems,mas-
sivelyincreasedconcurrentSSDaccesstrafficcriticallyintensifies
thislatencyamplification.Inourexperiments(§5.4),underthe
samerecall@10condition,theQPSofkernel-grainedexecution
demonstrates55.3%–67.4%ofquery-grainedexecution.
C3:I/OAmplificationduetoSSDPageMisalignment.In
thegraph-indexingANNSaccesspatterns,SSDreadstypicallyuse
a4KBminimumgranularitysinceIOPSremainconsistentwhen (b)Relaxeddependencysearchpipeline
theaccesssizeissmallerthan4KB[31].Duringgraphtraversal,
eachquerystepaccessesonegraphnode.However,standardgraph Figure9:Executionpipelineofbest-firstsearchandrelaxed
nodesstoringvectordataandneighborindicesareoftensignif- dependencysearch
icantly smaller than 4KB, causing severe I/O amplification. For
example,a64-degreegraphnodeoccupiesmerely384B(9.37%of
4KB),resultingin90.63%bandwidthwasteperaccess. varyinggraphdegreesundercurrenthardwareprofiles,therebyse-
lectingoptimaldegreesthatmaximizepipelineoverlapfordistinct
4 DesignofFlashANNS SSDquantities.
Toaddresstheseissues,weproposeFlashANNS,aGPU-accelerated
4.1 Dependency-RelaxedAsynchronousI/O
out-of-coregraph-indexingANNSsystem.
Pipeline
Figure7showstheoverallarchitectureofFlashANNS.FlashANNS
consistsofthreenoveldesigns.1)PipelinedI/O-computeprocessing. ToaddressC1,weproposeadependency-relaxedI/Opipeline.In-
ItparallelizesGPUcomputationandI/Oaccessesbylooseningdata steadofenforcingstrictstep-by-stepdependencies,ourdesignper-
dependency.2)query-grainedGPU-SSDdirectI/Ostack.Itemploys mitsSSDaccessestoproceedbeforetheprecedingcomputestage
query-grainedsynchronizationtoreducetaillatencyinterference hasfinished.Inthissection,wefirstidentifywherestrictsequential
duringSSDdataretrieval.3)Sampling-basedgraphdegreeselector. dependenciesariseandthenpresentastaleness-awarepipelinethat
Usingsampleindicestocharacterizepipelineperformanceacross relaxesthem.Finally,weestablishconvergenceguaranteesforthe

Conference’XX,June03–05,2018,Woodstock,NY Trovatoetal.
dependency-relaxedsearchandprovideanexplanationsupporting
thechoiceofstalenessstep.
4.1.1 Data-Dependency in Traditional Best-First Search. As the
searchpathshowninFigure8,traditionalbest-firstsearchinANNS
graphindicesbeginsfromanentrancenodeanditerativelyvisits
neighboringnodes.Inthisprocess,wedefineonesearchstepas
apop–expanditeration:atstep𝑖,thealgorithmpopsthecurrent
closestnode𝑣 𝑖 fromthecandidatemin-heap,issuesanSSDreadto
fetchallneighborsof𝑣 𝑖,computestheirdistancestothequery,and
insertsthemintothecandidatemin-heap.
Figure10:Searchstepcountunderdifferentstalenesssteps
Figure9ashowsthatthealgorithmcomputesneighboringnodes’
distancestothequeryandmaintainsacandidatemin-heapthatis
rankedbynodes’distancestothequeryvector.Each"min-heap" However, as shown in the comparison of time consumption
infigure9isasnapshotofthecandidatemin-heapattheendofa betweenFigure9aandFigure9b,thestalenessalgorithmallows
searchstep,andthenodeattheheadofthequeueistheheaproot theoverlappingoftheSSDaccessstageanddistancecalculation
thatwillbepoppedandexpanded.Onceanodehasbeenpopped stage,andtheoverallexecutiontimecanbegreatlyreducedeven
anditsneighborshavebeenprocessed,thenodeisremovedfrom withslightlymoresteps.
theheapandthereforedoesnotappearinthelater’min-heap’.Each
4.1.3 ConvergenceAnalysis. Weprovidetheconvergenceguaran-
stephastwotime-consumingstages:1)anSSDaccessstage(reading
teeofthesearchalgorithmunderthestalenessmechanismwith
neighborsofthepoppednode),and2)adistancecomputationstage
boundedsearchsteps.
(calculatingdistancesoftheseneighbornodestothequeryvector
andupdatingthecandidatemin-heap). DefineΔ 𝑡 asthemaximalpositionaldeviationbetweenpaths
P andP atthestep𝑡,constrainedbyatmost𝑘-stepdirec-
Thesetwostagesexhibittwotypesofdependencies:a)intra- relax strict
tionalvariances.Thedeviationsatisfies:
stepdependencythatrequiresdistancecomputationanduses
theresultsofSSDaccessfromthesamestep,andb)inter-step Δ 𝑡 ≤Δ 𝑡−1 +𝑘 for 𝑡 ≥1 (1)
dependencythatrequiresSSDaccessinthecurrentstep,uses
withinitialconditionat𝑡 =0:
thecandidatemin-heapupdatedbythecomputationresultsofthe
previousstep.Thedependenciespreventtheoverlappingofthe Δ =0 (2)
0
twostages.
sincenostalenessexistsatinitialization.
Bymathematicalinductionoversteps:
4.1.2 DependencyRelaxedStrategy. Tomitigatelowcomputational
resourceutilization,weproposerelaxinginter-stepdependenciesto
• BaseCase(𝑡 =0).TriviallyΔ
0
=0≤𝑘·0
overlapthecomputationandI/Ostages.Thisapproachisgrounded • InductiveStep.AssumeΔ 𝑡−1 ≤𝑘(𝑡−1).Then
inakeyinsight:thegraphsearchprocessexhibitsanaturaltoler- Δ 𝑡 ≤Δ 𝑡−1 +𝑘 ≤𝑘(𝑡−1)+𝑘 =𝑘𝑡 (3)
ancetostaleness(usingcandidatesetsfromuptokstepsprior). After𝑇 steps,themaximalcumulativedetourdepth𝑑satisfies:
Thisinsightissupportedbytwoobservations.First,ouranalysison
theSIFT1Bdatasetrevealsthatonly24.3%ofsearchstepsdirectly 𝑑 ≤Δ 𝑇 ≤𝑘𝑇 (4)
dependontheimmediatelyup-to-datecandidatemin-heap.Second,
Consequently, the total traversal steps of the relaxed path are
evenwiththestalecandidatemin-heap,thesearchdirectionoften
boundedby:
remainsvalid.Consequently,thetotalnumberofadditionalsteps
incurredbystalenessislimitedandslight.AsshowninFigure10,
thestepcountrisesbyjust2.4%to9.8%peradditionalstaleness |P relax |≤ 𝑇 + 𝑘×𝑇 =(𝑘+1)×𝑇 (5)
(cid:124)(cid:123)(cid:122)(cid:125) (cid:124)(cid:123)(cid:122)(cid:125)
step.
strictpathsteps maxdetoursteps
Upontheinherenttoleranceofgraphsearchtostaleness,we
Thisguaranteesthattherelaxedsearchconvergeswithinabounded
implementadependency-relaxedpipelinetomaximizeresource numberofadditionalstepsdeterminedby𝑘.
utilization.AsFigure9bshows,webreaktheinter-stepdependency
by allowing the SSD access stage of the current step i to start 4.1.4 StalenessStepSelection. InFlashANNS,wefixthestaleness
withoutwaitingforthecompletionofthedistancecalculationstage stepatk=1asthedefaultoptimalconfiguration.Thisdecisionis
inthepreviousstepi-1.Thenodeselectedforaccessinthestepiis groundedinaco-designprincipleunderourgraphdegreeselector
chosenfromthecandidatemin-heapupdatedbasedonthedistance (Section4.3).Thedegreeselectortunesthegraphdegreebefore
calculationresultsfromthestepi-2.AsillustratedinFigure8,in indexconstructiontoexplicitlybalancetheper-stepGPUcompu-
thiscase,thestepiproceedswithoutincorporatingthedistance tationtime𝑇 𝑐 andSSDI/Otime𝑇 𝑓,makingthemapproximately
calculationresultsfromthestepi-1,whichmayoverlookacloser equal.Underthisbalancedcondition,astalenessof𝑘 =1issuf-
nodethatshouldbechoseninthestepiinthetraditionalbest-first ficienttoachievefulloverlapbetweenthecomputationandI/O
search.Assuch,thestalenessmechanismmayrequireslightlymore stages,therebymaximizingpipelineefficiencywithoutintroducing
stepstosearchthevector. unnecessarylatency,asillustratedinFigure9b.

FlashANNS:GPU-DrivenI/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-ScaleSimilaritySearch Conference’XX,June03–05,2018,Woodstock,NY
Figure11:End-to-endQPSperformanceunderdifferentstal-
enesssteps
Figure13:I/OprocessofFlashANNS
Figure12:Two-stepsstalenesspipeline
Increasingthestalenesstok=2orhigherisnotbeneficial.For
example,increasingthestalenesstok=2doesnotreducetheintrin-
sicdurationsof𝑇 𝑓 and𝑇 𝑐.Whilehigherstalenesscaninitiatedata
fetchesearlier,thecomputationunitcannotfinishitsworkahead
oftime.Asaresult,asshowninFigure9b,thepipelinecycletime
(a)Kernel-GrainedSSDaccess
remainsunchangedcomparedtok=1.Furthermore,asshownin
Figure10,alargerkgenerallyincreasesthetotalnumberofsearch
stepsduetotheuseofamorestalecandidate,ultimatelyresulting
inhigheroverallquerylatency.Thesamerationaleappliestoeven
largervaluesofk.AsshowninFigure11,k=1consistentlyachieves
thehighestQPSinFlashANNS’send-to-endevaluation.
4.2 Resource-EfficientQuery-Grained
ConcurrentI/OStack
ToaddressC2,weintroducearesource-efficient,query-grained
concurrentI/OstacktailoredtoANNSworkloads.Itovercomes
thelimitationsofexistingI/Ostackswhenprocessingtheiterative,
batched, and fine-grained SSD requests characteristic of ANNS
workloads. Our design facilitates direct GPU-SSD data transfer
(b)Query-GrainedSSDaccess
withminimalGPUoverhead,entirelybypassingthehostOSfile
system.
Figure14:Pipelineperformancecomparison:kernel-grained
DesignandExecutionoftheQuery-GrainedI/OStack.Asillus-
vs.query-grainedSSDaccess
tratedinFigure13,FlashANNSimplementsthequery-grainedI/O
stackwiththreecomponents:(1)ACPU-hostedI/Orequestarray,
(2)AGPU-residentcompletionsignalarray(3)AGPUdatabuffer. pinnedhostmemoryandmappedintotheGPUaddressspaceusing
Eacharrayelementcorrespondstoasinglequery,andeachquery CUDA’smappedmemory.Aftersubmittingtheaddress,thewarp
isexecutedbyawarp(agroupof32threadsinGPUcomputing). isfreetoresumeitscomputationalwork,withoutblockingforthe
WhenissuinganSSDread,thepipelineproceedsinfourstages I/Orequesttocomplete.(2)ACPUagentpollsthisarray,batches
thatenablecomputationandI/Ooverlap:(1)Eachwarpwritesits theaddressesintoreadrequests,andsubmitsthemtotheSSD.(3)
targetSSDblockaddressintoarequestbufferthatisallocatedin Oncompletion,theSSDDMAtransfersthepayloaddirectlyinto

Conference’XX,June03–05,2018,Woodstock,NY Trovatoetal.
FlashANNSoffloadsI/OmanagementtotheCPU,andimplements
anasynchronousdata-passingmechanismtomakecomputation
andIOprocessparallelize.TomitigateCAM’slongwaitingtimefor
batchSSDaccess,asshowninFigure14b,FlashANNSenableseach
querytoindependentlyissueI/Orequestsandreceivecompletion
signals,therebypreventingstragglerrequestsfromdelayingthe
entirebatch.
WeevaluateFlashANNSwiththreealternativeI/Ostacksin-
tegratedintoitsarchitecture:GDS,BaM,andCAM.Asshownin
Figure15,underthe4-SSDSIFT1Bsetup,ourcustomI/Ostack
Figure 15: End-to-End QPS performance with various I/O demonstrates superior performance, achieving 14.5×, 3.9×, and
stack-basedFlashANNS
1.5×higherQPSthantheserespectivealternatives.Theseresults
conclusivelydemonstratethatFlashANNS’I/Ostackdeliverssupe-
riorperformanceandisbetteroptimizedfortheaccesspatternsof
thequery-graineddatabufferinGPUglobalmemory,andtheCPU ANNSworkloadscomparedtoexistingsolutions.
I/OthreadspostacompletionsignaltotheGPU-sidearray.(4)
Whenawarpfinishesitscurrentcomputationaltasksandreaches 4.3 Sampling-BasedGraphDegreeSelector
asynchronizationpoint,itchecksforthecompletionsignal.Ifthe
ToaddressC3,weproposeasampling-basedgraphdegreeselector.
dataisready,thewarpretrievesthedata.
Thisisapre–index-constructionprocedure.Itanalyzespipeline
ANNSworkload’suniquecharacterandchallengeANNS
behavioronsampleindiceswithdifferentdegreestoestimatethe
workloadsarecharacterizedbyalargebatchofqueries,wherethe
relative latencies of I/O and computation, and then selects the
processingofeachqueryinvolvesaniterativeexecutionoftheSSD
degreeconfigurationthatmaximizespipelineoverlapbymaking
accessstageandGPUcomputationstage.Thisintroducesthree
useofthewastedbandwidthcausedbyI/Oamplification.
challenges:First,ANNSworkloadscontainamassivenumberof
small,randomI/Os.Second,ourproposedSSDaccess/GPUcompu- 4.3.1 ImpactofGraphDegreeonComputation/IOBottleneck. The
tationoverlappingrequireshandlingSSDaccessesasynchronously. I/O characteristics of SSDs dictate that when the access granu-
Third,synchronizingSSDaccessesacrossdifferentqueriescauses larityisnomorethan4KB,IOPSinsteadofbandwidthbecomes
the long-tail latency (stragglers) of individual I/Os to delay the theprimaryperformancebottleneck.Graph-index’snodesizesare
entirebatch.Inaniterativesearchprocess,thesedelaysaccumulate mostlysmallerthan4KB.Forinstance,inDiskANN’s[31]default
significantly,severelydegradingoverallthroughput.Tothebest configuration(degree64)forSIFT1B,anodeis384bytes.Inthis
ofourknowledge,noneoftheexistingI/Ostacksaddressthese case,SSDaccessisusuallyperformedin4KBblocks(asnotedin
challengessimultaneously. DiskANN).ThismismatchbetweentheSSDaccessblockandthe
LimitationsofexistingGPU–SSDIOstacks.ExistingI/O graph-index’ssizenoderesultsinsignificantI/Oamplification,as
stacksintroducecriticalbottlenecksthatundermineperformance. eachreadretrievesanentire4KBblockbututilizesonlyasmall
GDS(GPUDirectStorage)[55]bypassestheCPUfordatatrans- portion.
fer but relies on the host OS filesystem for control operations. Thenodeiscomposedofanoriginalfull-precisionvectorand
Thisreliancenecessitatessystemcallsandfrequentkernel-user indicesofitsneighbors.Whileincreasingthegraphdegreetoinflate
modetransitions,whichincursubstantialoverheadwhenmanag- thenodesizeto4KBseemslikeadirectsolutiontoeliminateI/Oam-
ingthemassivenumberofsmall,randomI/OstypicalinANNS. plification,itintroducesadifferentissue.Ahigherdegreelinearly
BaM(GPU-InitiatedOn-DemandStorage)[58]employsaGPU- increasestheper-stepGPUcomputationtime,asmoreneighbors
centricI/Ocontrolpath.BaMcan’tresolvethesecondchallenge necessitatemoredistancecalculations.Meanwhile,addingmore
duetoitssynchronousinterface.BaM’sthreadsareforcedtowait neighborsyieldsdiminishingmarginalreturns.Therefore,selecting
fortheirI/Orequeststocompleteinsteadofperformingcomputa- theoptimalgraphdegreerequiresacarefulbalancebetweenI/O
tions.Thereby,itpreventstheoverlappingofcomputationandI/O andcomputationalload,andmustbeadaptedtotheavailableSSD
stagesinANNSworkloads.CAM(AsynchronousGPU-Initiated, bandwidth.
CPU-ManagedSSDManagement)[63]attemptsabalancedap- AsmentionedinSection4.1.4,toenabletheone-stepstaleness
proachwithasynchronous,CPU-managedaccessbutenforcesa pipeline,thedegreeselectorchoosestobalancetheper-stepGPU
kernel-grainedglobalsynchronizationmodel.ThismeanstheGPU computationtime𝑇 𝑐 andSSDI/Otime𝑇 𝑓,makingthemapproxi-
mustwaitforallI/Orequestsinabatchtocompletebeforeproceed- matelyequal.
ing.WhenfacingthethirdchallengeofANNSoffload,asshown
inFigure14a,CAM’ssynchronizationmechanismwaitsforthe 4.3.2 WorkflowofGraphDegreeSelector. Priortothefullindex
completionofallpendingSSDaccessesacrossdifferentqueriesand construction,FlashANNSusesthelightweightgraphdegreeselec-
thusbecomesasourceofsignificantlatencyinflation. tortodeterminetheoptimalgraphdegree.Thisprocessoperates
Howdoesthequery-grainedI/Ostackovercomethelimita- onacompactdatasample(e.g.,100knodes,indexsize<200MB)
tionsofexistingdesigns?ToovercomeGDS’soverhead,FlashANNS thatmatchesthetargetdataset’sdatatypeanddimensionality.It
leveragesSPDKtoentirelybypassthekernelstack,therebyelimi- constructstemporarygraphindicesforasetofcandidatedegrees
natingfilesystemoverhead.ToimproveBaM’ssynchronousdesign, (e.g., 64, 150, 250), where edges are formed using random links

FlashANNS:GPU-DrivenI/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-ScaleSimilaritySearch Conference’XX,June03–05,2018,Woodstock,NY
ratherthantrueneighborrelationships.Itissufficienttoaccurately Datasets.Ourexperimentalconfigurationincorporatesthreecanon-
probe the memory and I/O patterns for each degree. Using the icalbillion-scaledatasetsextensivelyadoptedinhigh-dimensional
sameruntimepipelineandashortwarm-upofsyntheticqueries, similaritysearchbenchmarks:
theselectormeasuresforeachcandidate𝑑thedatafetchlatency • SIFT-1Bcomprising1billion128-dimensionalvectorswith
| 𝑇 𝑓(𝑑)andper-stepcomputationlatency𝑇 |     |     | 𝑐(𝑑).Theobjectiveisto |     |     |          |               |         |            |           |       |
| ------------------------------------ | --- | --- | --------------------- | --- | --- | -------- | ------------- | ------- | ---------- | --------- | ----- |
|                                      |     |     |                       |     |     | unsigned | 8-bit integer | (uint8) | precision, | evaluated | using |
makeI/Oandcomputationtakethesametimeperstepto
10,000queryinstances.
maximizepipelineoverlap,so𝑑iscalculatedas
• DEEP-1Bfeaturing96-dimensionalfloating-pointvectors
(float32)across1billionentries,benchmarkedwith10,000
|     | 𝑑 = argmin | |𝑇  | (𝑑)−𝑇 (𝑑)|. |     | (6) |          |     |     |     |     |     |
| --- | ---------- | --- | ----------- | --- | --- | -------- | --- | --- | --- | --- | --- |
|     |            | 𝑑 c | f           |     |     | queries. |     |     |     |     |     |
•
4.3.3 OverheadofGraphDegreeSelect. Byoperatingonasmall SPACEV-1Bcontaining100-dimensionalsigned8-bitinte-
sample(e.g.,100knodes,0.01%ofabillion-scaledataset)withran- ger(int8)vectorsatbillion-scale,testedwith29,300queries.
Baselines.FlashANNShasthreebaselinestocompare.
domlinks,thisprofilingavoidsthecostofbuildingtrueneighbor-
hoods,makingbothgraphconstructionandperformancemeasure- • SPANN[11]:Aclustering-basedSSD-residentframework
mentextremelylow-cost.Theentireprocesscompletesinminutes, thatstoresclusterlistsonSSDswhilemaintainingcluster
incurringlessthan1%overheadcomparedtothemulti-hourrun- centroidsinCPUmemory.Itssearchmechanismachieves
timeofafullindexconstruction.
|     |     |     |     |     |     | low | latency at the | cost of computationally |     | intensive | per- |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ----------------------- | --- | --------- | ---- |
queryoperations.
| 4.3.4 HardwareAdaptationviatheDegreeSelector. |     |     |     | Thedegreese- |     |     |     |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |
• DiskANN[31]:Agraph-indexedSSD-residentframework
lectorequipsFlashANNSwiththecapabilitytoeffectivelyutilize
thatstoresbothindexgraphsandrawvectorsonSSDs,com-
diversehardwaresettings.Thedegreeselectorguidestheuserto
plementedbyproductquantizationcompressedvectorsin
| leverage hardware | improvements |     | by re-balancing | the computa- |     |     |     |     |     |     |     |
| ----------------- | ------------ | --- | --------------- | ------------ | --- | --- | --- | --- | --- | --- | --- |
CPUmemory.Itachievesoptimizedperformancethrough
| tionalload𝑇 | andtheI/Olatency𝑇 |     |                              |     |     |     |     |     |     |     |     |
| ----------- | ----------------- | --- | ---------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
| 𝑐           |                   |     | 𝑓,ensuringthepipelineremains |     |     |     |     |     |     |     |     |
parallelsearching.
efficient.
|            |            |             |           |        |          | • FusionANNS | [67]: | A GPU-accelerated |     | clustering-based |     |
| ---------- | ---------- | ----------- | --------- | ------ | -------- | ------------ | ----- | ----------------- | --- | ---------------- | --- |
| In case of | using SSDs | with higher | IOPS, the | degree | selector |              |       |                   |     |                  |     |
SSD-residentframeworkleveragingcooperativeCPU-GPU
| guidestheusertodecreasethegraphdegree.Thisreduces𝑇 |                                     |     |     |     | to  |                           |                                    |     |     |     |     |
| -------------------------------------------------- | ----------------------------------- | --- | --- | --- | --- | ------------------------- | ---------------------------------- | --- | --- | --- | --- |
|                                                    |                                     |     |     |     | 𝑐   | processingtooptimizeANNS. |                                    |     |     |     |     |
| realignwiththeshorter𝑇                             | 𝑓,therebyshorteningthepipelinecycle |     |     |     |     |                           |                                    |     |     |     |     |
|                                                    |                                     |     |     |     |     | EvaluationMetrics.        | Wequantifyquerythroughputinqueries |     |     |     |     |
andthusacceleratingqueries.IncaseofusingafasterGPU,the
persecond(QPS)andaccuracyviarecall@10.Recall@10measures
degreeselectorguidestheusertoincreasethegraphdegree.This
|     |     |     |     |     |     | the proportion | of true top-10 | neighbors | retrieved | from | ground |
| --- | --- | --- | --- | --- | --- | -------------- | -------------- | --------- | --------- | ---- | ------ |
leveragestheadditionalcomputationalcapacitytoexaminemore
truthamongANNS-returnedcandidates.Cluster-indexingsystems
neighborsperstepwhilemaintainingthesamepipelinecycletime,
andultimatelyreducesthetotalnumberofsearchstepsandthus tunerecallbyadjustingthecountofretrievedpostinglistsduring
|     |     |     |     |     |     | graph traversal, | whereas | graph-indexing | systems | control | recall |
| --- | --- | --- | --- | --- | --- | ---------------- | ------- | -------------- | ------- | ------- | ------ |
speedsupoverallqueryexecution.
byconfiguringthecandidatemin-heapsize.OnQPS-recall@10
tradeoffcurves,superiorimplementationsoccupytop-rightposi-
5 Evaluation
tions,achievinghigherQPSwithgreateraccuracyunderidentical
Ourevaluationsaimtoanswerthefollowingquestions:
configurations.
•
HowdoestheperformanceofFlashANNScomparetoother
SSD-basedframeworksonasingleSSDandmultipleSSDs 5.2 End-to-EndQPS-RecallTradeoff
(§5.2)?
WeevaluateFlashANNSagainstallSSD-basedbaselines[11,31,67]
• Howeffectiveisthedependency-relaxedasynchronousI/O
bymaximizingCPUthreadsto52.Figure8reportsquerythrough-
pipeline(§5.3)?
putversusrecall@10acrossthreedatasets,scalingSSDcountfrom
•
| Howeffectiveisthequery-grainedconcurrentSSDaccess |     |     |     |     |     | 1to8forindexstorage.                  |     |     |     |                |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | ------------------------------------- | --- | --- | --- | -------------- | --- |
| (§5.4)?                                           |     |     |     |     |     | ComparingunderSingleSSDConfiguration. |     |     |     | Wefirstexamine |     |
• Howdoesthroughputscalewhenincreasingthereturned
QPS-recall@10performanceundersingle-SSDconfigurations.The
top-𝑘(§5.5)?
toprowofFigure16showsFlashANNSachieving2.7-5.9×query
• Howdoesthecomputation-I/O-balancedgraphdegreese-
throughputgainsoverCPU-basedbaselines(SPANN/DiskANN)at
lectorguidedegreeselection(§5.6)? 96%recall@10.AgainstGPU-enhancedFusionANNS,FlashANNS
• HowdoesFlashANNSperformonlarger-than-memoryin- deliverscomparablequerythroughput(1.03-1.4×)onSIFT1Band
dices(§5.7)?
SPACEV1Bat98%recall@10,whereconstrainedI/Obandwidth
reducescomputationaldemandsandavoidsCPUbottlenecks.How-
5.1 ExperimentalSetting
|     |     |     |     |     |     | ever, on DEEP1B | at 98% | recall@10, | FlashANNS | achieves | 14.3× |
| --- | --- | --- | --- | --- | --- | --------------- | ------ | ---------- | --------- | -------- | ----- |
ExperimentalPlatform.Theexperimentsareconductedusinga higherquerythroughputthanFusionANNS.Thisperformancedis-
singleserverequippedwithdualIntelXeonGold5320processors crepancyoriginatesfromDEEP1B’ssingle-precisionfloating-point
operatingat2.20GHz(52threads),768GBofDDR4systemmemory, (FP32)format,whichimposessubstantialCPUpressureonFusion-
andanNVIDIA80GB-PCIe-A100GPU.Thestoragesubsystem ANNSduringprecisiondistancecalculations,revealingCPU-bound
compriseseight3.84TBIntelP5510NVMeSSDsconfiguredina limitations.Overall,FlashANNSconsistentlyoccupiesthetop-right
PCIe4.0x16topology.TheplatformrunsUbuntu22.04LTS. region of QPS-recall@10 curves, demonstrating superior query

Conference’XX,June03–05,2018,Woodstock,NY Trovatoetal.
SIFT1B DEEP1B SPACEV1B
DSS1
sDSS2
sDSS4
sDSS8
Figure16:ThequerythroughputofdifferentANNSsystemsvaryingwiththerecall@10ondifferentSSDcounts
demonstrates disproportionately greater performance improve-
mentsthanalternativesbynavigationgraphdegreeoptimizing
andI/O-computationlatencybalancing.UsingtheSIFT1Bexemplar
datainFigure16(firstcolumn),FlashANNSdeliversprogressively
higherquerythroughputat98%recall@10—achieving1.4×–7.0×,
2.0×–5.4×, 2.7×–5.9×, and 3.9×–5.7× QPS gains over baselines
whenscalingfrom1to8SSDs.
ComparisontotheIn-MemoryBaseline.Furthermore,weob-
servethatFusionANNSunderperformedrelativetoexpectations
inhighI/Obandwidthscenarios.Ouranalysissuggeststhisstems
Figure 17: FlashANNS’s QPS performance compared with fromimplicitinefficienciesinFusionANNS’I/Osubmissionqueue
in-memoryFusionANNS. schedulingmechanisms.Torigorouslyisolatealgorithmicandar-
chitecturaladvantagesfromimplementation-specificbiases,we
conductacontrolledcomparison:weevaluateFlashANNS(using
4SSDs)againstanin-memoryvariantofFusionANNS(allindices
throughputthroughparallelpipelineoptimizationandI/Ostack loadedintoDRAM),therebyremovinganyconfoundingeffectsof
efficiencyunderlimitedI/Obandwidth. storage-layeroptimizations.AsshowninFigure17,FlashANNS
ComparisonunderanIncreasingNumberofSSDs.Asavail- achieveshigherperformancethanthein-memoryFusionANNS
ableI/ObandwidthincreaseswithadditionalSSDs,FlashANNS

FlashANNS:GPU-DrivenI/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-ScaleSimilaritySearch Conference’XX,June03–05,2018,Woodstock,NY
Figure18:QuerythroughputofFlashANNSvs.FlashANNS-
Nopipeunderdifferentcandidatemin-heaplengths Figure21:Normalizedend-to-endQPSperformancecompar-
isonofFlashANNSandthenopipelineversion
enableconcurrentexecutionbetweenSSDreadoperationsanddata
computationduringgraphtraversal,whereastheno-pipevariant
strictlyadherestothestrongdependencyconstraintsinherentin
best-firstsearchalgorithms,enforcingserializedexecutionbetween
SSDaccessandcomputationalprocessing.
Figure 18 illustrates the impact of dependency relaxation on
searchpathlengths,comparingthepipelineandbest-firstsearch
Figure 19: FlashANNS’s query latency breakdown of SSD
implementationsonthesift1Bdatasetundera250-degreegraph
access, GPU computation and total pipelined time under
configuration.Weobservethattherelaxed-dependencyscheme
differentrecallrates
incursonly2.8-3.2additionalsteps,representingamere2.5%-7%
overheadrelativetothetotalquerystepsinthebaselinesearch
strategy.Weconcludethatdependencyrelaxationinducesonly
minorvariationsinsearchstepcounts.
ImpactonQueryLatency. Thissectionquantifiespipeline
overlapcharacteristicsintermsoflatency.EvaluatedontheSIFT-
1B dataset with a 250-degree graph and 4-SSD parallelism, Fig-
ure19comparestheaveragequerylatencyofpipelinedFlashANNS
againstthesummedlatencyofitsSSDaccessphaseandGPUcompu-
tationphase.Theexperimentalresultsshowthattheoverlappedexe-
cutiontimeaccountsfor35.4%to45.1%ofthetotalpipelinedlatency
acrossdifferentrecallrates.ThisdemonstratesthatFlashANNSef-
Figure20:End-to-endQPSperformanceofFlashANNSand fectivelyoverlapstheSSDaccessesandGPUcomputationstages,
theFlashANNS-Nopipe therebyreducingsearchlatencyandimprovingQPS.
OverallPipelinePerformance. Collectively,thedependency-
relaxedasynchronousI/Opipelinetradesonly2.5%-7%additional
baseline.ThisresultdemonstratesthatFlashANNS’SSD-basedim-
computationalstepsfor36%-47%pipelineoverlapratio,therebyim-
plementationmaintainsaperformanceadvantageovereventhe
provingtheoverallquerythroughput.AsFigures20and21demon-
in-memoryindexedFusionANNS.
strate,thisapproachdelivers33.6%–46.6%higherQPScomparedto
5.3 ImpactofDependency-Relaxed theno-pipelinevariantunderthesamerecall.
AsynchronousI/OPipeline
5.4 ImpactofQuery-grainedConcurrentSSD
Inthissubsection,wequantitativelyevaluatehowdependency-
Access
relaxedpipelineparallelismaffectsquerythroughputduringexecu-
tion.Weseparatelyevaluate:1)theeffectofdependencyrelaxation Tovalidatetheeffectivenessofquery-grainedconcurrentSSDac-
onstepcountingraphqueries,2)thelatencyreductionachieved cess,weemployanunoptimizedkernel-grainedI/Ostack(CAM[63])
throughexecutionoverlapping,and3)theimprovementinoverall forcomparison.Unlikequery-grainedSSDaccessthattreatsindi-
querythroughput. vidualwarpoperationsasautonomousunits,thekernel-grained
ImpactonSearchingSteps. Toelucidatetheimpactofdepen- approachaggregatesallSSDrequestsissuedduringakernelfunc-
dencyrelaxationonsearchprocedures,wepresenttwoimplemen- tion’sexecutionphaseintoabatchprocess.Thisrequirescomplet-
tationsofFlashANNS:thepipelineversionandtheno-pipevariant. ingfulldataretrievalforanentirerequestgroupbeforeinitiating
Thepipelineimplementationintroducesdependencyrelaxationto subsequentdataprocessingandnext-stageaccessoperations.In

Conference’XX,June03–05,2018,Woodstock,NY Trovatoetal.
{10,50,100},wetunetheparameterstomeasuretheachievable
QPSfordifferenttop-Ksizeswhentherecallrateishigherthan90%.
AsshowninFigure24,FlashANNSdelivers2.2–5.2×higherQPS
thantheotherthreebaselines,demonstratingthatitcanmaintain
highquerythroughputunderdifferent𝐾 sizes.
5.6 ProcessofComputationI/O-BalancedGraph
Figure22:End-to-endQPSperformanceofFlashANNSand
DegreeSelection
kernel-grainedaccessversion
Weconductindexconstructionexperimentsacrossthreegraph
degreeconfigurations(64,150,and250degrees)undervaryingSSD
parallelismconditions(1,2,4,and8SSDs).Ourevaluationsystem-
aticallymeasuresquerythroughputcharacteristicsacrossdifferent
I/Obandwidthsettings.Resultsdemonstratetheeffectivenessof
selectinggraphdegreesviasample-indexedanalysis.
WeevaluatetheQPS-recalltradeoffsofvaryinggraphdegreeson
theDEEP1BdatasetunderdifferentI/Obandwidthconfigurations.
AsdemonstratedinFigure25,underlowI/Obandwidthconstraints
(withindicesstoredon1-2SSDs),higher-degreegraphsconsistently
achievesuperiorquerythroughputwhilesatisfyingequivalentre-
calltargetscomparedtolower-degreegraphs.Thisadvantagestems
Figure 23: Normalized end-to-end QPS performance of fromtheirenhancedabilitytoleverageGPUparallelcomputation
FlashANNSandkernel-grainedaccessversion unitstomaskI/OlatencywhenSSDbandwidthisscarce.
However,asI/ObandwidthincreaseswithhigherSSDparal-
lelism (up to 8 SSDs), the query throughput gap between high-
degreeandlow-degreegraphsnarrowssignificantly.Notably,in
the 8-SSD configuration, the 150-degree graph outperforms its
250-degree counterpart by 13% in query throughput under 96%
recall@10.Beyondcriticalbandwidththresholds,thehighercom-
putationaldemandsinherenttohigh-degreegraphprocessing(e.g.,
requiring access to more neighbors at each traversal step) may
converselycreatecomputationalbottlenecks.
Beforedeterminingtheoptimalgraphdegreeforindexconstruc-
tion,wecreatesampleindices(asdescribedinSection4.3)—which
Figure24:End-to-endQPSperformanceunderdifferenttop- sharethesamedatatypeasthevectorindexbutexcludeactual
Ksizes neighborrelationships—topre-estimatepipelinestagelatency.
ExperimentalmeasurementshowstheI/O-computationratiochar-
acteristicsfordifferentgraphdegreesampleindicesinFigure26.
contrast,query-grainedSSDaccessenablesafiner-grainedsynchro- Thesesampleindicesreflecttheactualperformancecharacteristics
nizationmechanismforimmediateprocessingofsubsequentread offull-scaleindexgraphsatcorrespondingdegreeconfigurations.
requestsuponcompletionofquerieshandledbyindividualwarps. With1SSD,theI/Olatencyofthe150-degreegraphis4.2×its
Weevaluateourexperimentonthesift1Bdatasetwitha4-SSD computational latency, while the 250-degree graph exhibits I/O
configurationunder250-degreegraphparameters.AsFigure22 latencyat2.3×computationallatency,indicatingthatbothconfigu-
andFigure23show,thequery-grainedSSDaccessimplementation rationsremainI/O-bound,thushigher-degreegraphsretaintheir
achieves 43%-68% query throughput improvement compared to advantage.
itskernel-grainedcounterpartCAM.Theseperformancegainsare With2SSDs,the150-degreegraph’sI/Olatencybecomes3.1×
attributed primarily to the finer synchronization granularity of computationallatency(stillI/O-bound),whereasthe250-degree
query-grainedoperations,whicheffectivelyamortizesporadiclong- graphachievesnear-balanceat1.1×I/O-to-computelatencyratio,
tailSSDreadlatenciesfromANNSsystems. enablingfullpipelineutilization.
With 4 SSDs, the 150-degree graph’s I/O latency reduces to
5.5 ScalabilitytoLargerReturnSets
1.4×computationallatency(marginallyI/O-bound),whilethe250-
TovalidateFlashANNS’performancewithalargerreturnedset,we degreegraphbecomescompute-bound(0.7×I/O-to-computeratio).
compareFlashANNStothreestate-of-the-artbaselinesonSIFT- Thisimpliestheoptimaldegreeliesbetween150and250toavoid
1B (4-SSD) under more top-K sizes. For each method and 𝐾 ∈ asymmetricalbottlenecks.

FlashANNS:GPU-DrivenI/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-ScaleSimilaritySearch Conference’XX,June03–05,2018,Woodstock,NY
(a)1SSD (b)2SSDs (c)4SSDs (d)8SSDs
Figure25:FlashANNSQPS-recallperformanceonthedatasetDEEP1BdatasetunderdifferentSSDconfigurations
6 RelatedWorks
Toourknowledge,thisworkpresentsthefirstGPU-accelerated,
SSD-basedgraphANNSframework.WhileSection5providescom-
prehensive comparisons with state-of-the-art SSD-based ANNS
systems(DiskANN,SPANN,FusionANNS),wereviewrelatedwork
intwokeyareas:in-memoryANNSframeworksandSSDI/Oopti-
mizationimplementations.
In-MemoryANNSFrameworks. In-memoryANNSsystemsare
widelyutilized,withtheirindexstructuresprimarilycategorized
intofourtypes:1.Tree-basedindices[7,9,15,21,50,51,61,76]:The
corepremisecentersonconstructingatree-likedatastructurethat
Figure26:I/O-computationtimeratioofsampleindicesin
hierarchicallyorganizesvectorsviapartitioningcriteriabasedon
differentSSDcounts
distanceordensitymetrics.2.Hash-based[2–4,16,23,65]:Locality-
SensitiveHashing(LSH)mapshigh-dimensionalvectorsintohash
bucketswhilepreservingsimilarityrelationships,enablingefficient
approximate nearest neighbor search. 3. Quantization-based [5,
6,22,32,36,53,74]:Thismethoddivideshigh-dimensionalvec-
torsintosubvectors,independentlyquantizeseachsubvectorinto
compact codes. This method reduces the storage footprint and
acceleratessimilaritycomputationthroughlookuptables.4.Graph-
based[18,20,26,34,38,46,47]:Graph-basedindicesdemonstratesu-
periorsearchperformanceinEuclideanspacesduetotheirexplicit
modelingoflocalneighborproximity.Inparticular,theedgesin
thegraphstructuredirectlyencodevectoradjacencyrelationships,
enablinggreedytraversaltowardnearestneighbors.Incontrast,
Figure 27: FlashANNS’ QPS performance under TB-scale FlashANNSfocusesonout-of-orderANNSsystemswhileachieving
dataset slightlyhigherperformancethanthein-memorycounterparts.
SSDI/OOptimizations. Recently,theSSDhasbeendeployedin
manyapplicationsforitsmassivestoragevolumewhileachieving
highperformancecomparedtotraditionalharddiskdrives[1,25,
Theperformancetrendspredictedbyourdegreesamplingvia
35,48].Therearemanyworksproposedtoexploitthepotentialities
lightweightsampleindicesaligncloselywithactualtestresults,em-
ofSSD[1,10,12,17,19,27,29,40–42,44,45,48,57,64,66,68,70–
piricallyvalidatingtheeffectivenessofgraphdegreepre-selection
73,78].Existingworks[77]achievedirectGPU-SSDdatatransfer
forworkload-awareindexoptimization.
usingtheGPUDirect[54]technology.However,itreliesontheCPU
toinitiateortriggerSSDaccessandfailstoeliminatetheOSkernel
5.7 Out-of-CoreEfficiencyon30B-Vector
overheadentirely.Systems[60]donotsupportGPUDirect[54].
Dataset
ThesemethodsinvolveOSkerneloverheads,especiallymakingit
TodemonstrateFlashANNS’processingcapabilitytoout-of-core hardtosaturateSSDthroughputforbatchingaccesspatternsof
indices, we augment the DEEP1B dataset to a 30 billion-vector ANNSworkloads.
dataset(1,073GB)byduplicatingeachvectortwicewithminor BaM[58]proposesGPU-initiatedon-demanddirectSSDaccess
perturbations,therebyexpandingitsscalewhilepreservingprox- withoutCPUinvolvement.However,BaM’sdesignintroducesnew
imity relationships. Figure 27 shows that FlashANNS achieves GPUcorecontentionissues,whichareintendedtobeusedincom-
goodQPS-recalltrade-offsonthisexabyte-scaledataset,validat- putationtasks,whileCAM[63]canachievehighthroughputwith-
ingFlashANNS’scapabilitytoefficientlyperformANNSonhuge out GPU SM occupancy. However, its implementation enforces
datasetsfarexceedingDRAMcapacityforRAGapplications.

Conference’XX,June03–05,2018,Woodstock,NY Trovatoetal.
kernel-grainedglobalsynchronization:allwarpswithinakernel approximatenearestneighborhoodsearch. AdvancesinNeuralInformation
mustwaitfortheslowestSSDI/Orequesttocompletebeforepro- ProcessingSystems34(2021),5199–5212.
[12] JiajiaChu,YunshanTu,YaoZhang,andChuliangWeng.2020.LATTE:Anative
ceeding.Incontrast,FlashANNSenablesquery-grainedconcurrent
tableengineonNVMestorage.In2020IEEE36thInternationalConferenceonData
SSDaccesstoaccelerateGPU-basedANNS. Engineering(ICDE).IEEE,1225–1236.
[13] PaulCovington,JayAdams,andEmreSargin.2016. DeepNeuralNetworks
forYouTubeRecommendations.InProceedingsofthe10thACMConferenceon
7 Conclusion
RecommenderSystems(Boston,Massachusetts,USA)(RecSys’16).Associationfor
Inthiswork,wepresentFlashANNS,aGPU-accelerated,out-of- ComputingMachinery,NewYork,NY,USA,191–198. https://doi.org/10.1145/
2959100.2959190
coregraph-basedANNSsystem.OurapproachachievesfullI/O- [14] JiaxiCui,ZongjianLi,YangYan,BohuaChen,andLiYuan. ChatLaw:Open-
computeoverlapthroughthreecoordinatedmechanisms:First,a SourceLegalLargeLanguageModelwithIntegratedExternalKnowledgeBases.
([n.d.]). https://openreview.net/forum?id=Cjas49BCAf
dependencyrelaxationI/OpipelinetooverlapSSDnoderetrieval
[15] SanjoyDasguptaandYoavFreund.2008. Randomprojectiontreesandlow
withGPUcomputationwhileprovidingarigoroustheoreticalcon- dimensionalmanifolds.InProceedingsofthefortiethannualACMsymposiumon
vergenceguarantee.Second,aquery-grainedconcurrentSSDaccess Theoryofcomputing.537–546.
[16] MayurDatar,NicoleImmorlica,PiotrIndyk,andVahabSMirrokni.2004.Locality-
thateliminatestheGPUkernel-grainedglobalsynchronizationin-
sensitivehashingschemebasedonp-stabledistributions.InProceedingsofthe
herent.Third,ahardware-awaregraphdegreeselectionmechanism twentiethannualsymposiumonComputationalgeometry.253–262.
maximizingpipelinestageoverlapefficiency.Experimentalresults [17] JaeyoungDo,IvanLuizPicoli,DavidLomet,andPhilippeBonnet.2021.Better
databasecost/performanceviabatchedI/OonprogrammableSSD.TheVLDB
showthatunderthesamerecallaccuracy,FlashANNSachieves Journal30,3(2021),403–424.
2.7–5.9×higherquerythroughputthanexistingSOTAmethods [18] WeiDong.2011.High-dimensionalsimilaritysearchforlargedatasets.Princeton
with a single SSD configuration, and scales to 3.9–12.2× query University.
[19] CarlDuffy,JaehoonShim,Sang-HoonKim,andJin-SooKim.2023. Dotori:A
throughputimprovementsinmulti-SSDsetups. key-valuessdbasedkvstore.ProceedingsoftheVLDBEndowment16,6(2023),
1560–1572.
Acknowledgments [20] CongFuandDengCai.2016.Efanna:Anextremelyfastapproximatenearest
neighborsearchalgorithmbasedonknngraph.arXivpreprintarXiv:1609.07228
Theworkissupportedbythefollowinggrants:NationalScience (2016).
[21] KeinosukeFukunagaandPatrenahalliM.Narendra.1975.Abranchandbound
andTechnologyMajorProject(2022ZD0117000),theMajorProject
algorithmforcomputingk-nearestneighbors.IEEEtransactionsoncomputers
oftheZhejiangProvincialNaturalScienceFoundationunderGrant 100,7(1975),750–753.
No.LD26F020002,theNationalNaturalScienceFoundationofChina [22] TiezhengGe,KaimingHe,QifaKe,andJianSun.2013. Optimizedproduct
quantization.IEEEtransactionsonpatternanalysisandmachineintelligence36,4
underthegrantnumbers(62472384,62441236,U24A20326),Starry (2013),744–755.
NightScienceFundofZhejiangUniversityShanghaiInstitutefor [23] AristidesGionis,PiotrIndyk,RajeevMotwani,etal.1999.Similaritysearchin
highdimensionsviahashing.InVldb,Vol.99.518–529.
AdvancedStudy(SN-ZJU-SIAS-0010).JieZhang,ZekeWang,and
[24] MihajloGrbovicandHaibinCheng.2018.Real-timePersonalizationusingEm-
FeiWuarethecorrespondingauthors. beddingsforSearchRankingatAirbnb.InProceedingsofthe24thACMSIGKDD
InternationalConferenceonKnowledgeDiscovery&DataMining(London,United
References Kingdom)(KDD’18).AssociationforComputingMachinery,NewYork,NY,USA,
311–320. https://doi.org/10.1145/3219819.3219885
[1] GustavoAlonso,NatassaAilamaki,SaileshKrishnamurthy,SamMadden,Swami [25] GabrielHaasandViktorLeis.2023. Whatmodernnvmestoragecando,and
Sivasubramanian,andRaghuRamakrishnan.2023.FutureofDatabaseSystem howtoexploitit:High-performancei/oforhigh-performancestorageengines.
Architectures.InCompanionofthe2023InternationalConferenceonManagement ProceedingsoftheVLDBEndowment16,9(2023),2090–2102.
ofData.261–262. [26] KianaHajebi,YasinAbbasi-Yadkori,HosseinShahbazi,andHongZhang.2011.
[2] AlexandrAndoniandPiotrIndyk.2008.Near-optimalhashingalgorithmsfor Fastapproximatenearest-neighborsearchwithk-nearestneighborgraph.In
approximatenearestneighborinhighdimensions.Commun.ACM51,1(2008), IJCAIProceedings-InternationalJointConferenceonArtificialIntelligence,Vol.22.
117–122. 1312.
[3] AlexandrAndoni,PiotrIndyk,HuyLNguyê˜n,andIlyaRazenshteyn.2014.Be- [27] MichaelHaubenschild,CaetanoSauer,ThomasNeumann,andViktorLeis.2020.
yondlocality-sensitivehashing.InProceedingsofthetwenty-fifthannualACM- Rethinkinglogging,checkpoints,andrecoveryforhigh-performancestorage
SIAMsymposiumonDiscretealgorithms.SIAM,1018–1028. engines.InProceedingsofthe2020ACMSIGMODInternationalConferenceon
[4] AlexandrAndoniandIlyaRazenshteyn.2015.OptimalData-DependentHashing ManagementofData.877–892.
forApproximateNearNeighbors.InProceedingsoftheForty-SeventhAnnual [28] Jui-TingHuang,AshishSharma,ShuyingSun,LiXia,DavidZhang,PhilipPronin,
ACMSymposiumonTheoryofComputing(Portland,Oregon,USA)(STOC’15). JananiPadmanabhan,GiuseppeOttaviano,andLinjunYang.2020.Embedding-
AssociationforComputingMachinery,NewYork,NY,USA,793–801. https: basedRetrievalinFacebookSearch.InProceedingsofthe26thACMSIGKDD
//doi.org/10.1145/2746539.2746553 InternationalConferenceonKnowledgeDiscovery&DataMining(VirtualEvent,
[5] ArtemBabenkoandVictorLempitsky.2014. Theinvertedmulti-index. IEEE CA,USA)(KDD’20).AssociationforComputingMachinery,NewYork,NY,USA,
transactionsonpatternanalysisandmachineintelligence37,6(2014),1247–1260. 2553–2561. https://doi.org/10.1145/3394486.3403305
[6] ArtemBabenkoandVictorLempitsky.2015.Treequantizationforlarge-scale [29] YuchenHuang,XiaopengFan,SongYan,andChuliangWeng.2024.Neos:Anvme-
similaritysearchandclassification.InProceedingsoftheIEEEConferenceon gpusdirectvectorservicebufferinuserspace.In2024IEEE40thInternational
ComputerVisionandPatternRecognition.4240–4248. ConferenceonDataEngineering(ICDE).IEEE,3767–3781.
[7] AlinaBeygelzimer,ShamKakade,andJohnLangford.2006. Covertreesfor [30] GautierIzacard,PatrickLewis,MariaLomeli,LucasHosseini,FabioPetroni,Timo
nearestneighbor.InProceedingsofthe23rdinternationalconferenceonMachine Schick,JaneDwivedi-Yu,ArmandJoulin,SebastianRiedel,andEdouardGrave.
learning.97–104. Atlas:Few-shotLearningwithRetrievalAugmentedLanguageModels.24,251
[8] YuanCao,HengQi,WenruiZhou,JienKato,KeqiuLi,XiulongLiu,andJieGui. ([n.d.]),1–43. http://jmlr.org/papers/v24/23-0037.html
2018.BinaryHashingforApproximateNearestNeighborSearchonBigData:A [31] SuhasJayaramSubramanya,FnuDevvrit,HarshaVardhanSimhadri,Ravishankar
Survey.IEEEAccess6(2018),2039–2054. https://doi.org/10.1109/ACCESS.2017. Krishnawamy,andRohanKadekodi.2019.Diskann:Fastaccuratebillion-point
2781360 nearestneighborsearchonasinglenode.Advancesinneuralinformationpro-
[9] LawrenceCayton.2008.Fastnearestneighborretrievalforbregmandivergences. cessingSystems32(2019).
InProceedingsofthe25thinternationalconferenceonMachinelearning.112–119. [32] HerveJegou,MatthijsDouze,andCordeliaSchmid.2010.Productquantization
[10] YunpengChai,YanfengChai,XinWang,HaochengWei,NingBao,andYushi fornearestneighborsearch.IEEEtransactionsonpatternanalysisandmachine
Liang.2019. LDC:alower-leveldrivencompactionmethodtooptimizeSSD- intelligence33,1(2010),117–128.
orientedkey-valuestores.In2019IEEE35thInternationalConferenceonData [33] ChaoJin,ZiliZhang,XuanlinJiang,FangyueLiu,XinLiu,XuanzheLiu,andXin
Engineering(ICDE).IEEE,722–733. Jin.2024.RAGCache:EfficientKnowledgeCachingforRetrieval-AugmentedGen-
[11] QiChen,BingZhao,HaidongWang,MingqinLi,ChuanjieLiu,Zengzhong eration.ArXivabs/2404.12457(2024). https://api.semanticscholar.org/CorpusID:
Li,MaoYang,andJingdongWang.2021.Spann:Highly-efficientbillion-scale 269283058

FlashANNS:GPU-DrivenI/OPipeliningforEliminatingStorage-ComputeBottlenecksinBillion-ScaleSimilaritySearch Conference’XX,June03–05,2018,Woodstock,NY
[34] ZhongmingJin,DebingZhang,YaoHu,ShidingLin,DengCai,andXiaofeiHe. DataEngineering(ICDE).IEEE,5644–5648.
2014.Fastandaccuratehashingviaiterativenearestneighborsexpansion.IEEE [58] ZaidQureshi,VikramSharmaMailthody,IsaacGelado,SeungwonMin,Amna
transactionsoncybernetics44,11(2014),2167–2177. Masood,JeongminPark,JinjunXiong,CJNewburn,DmitriVainbrand,I-Hsin
[35] YuhunJun,ShinhyunPark,Jeong-UkKang,Sang-HoonKim,andEuiseongSeo. Chung,MichaelGarland,WilliamDally,andWen-meiHwu.2023.GPU-Initiated
2024. Weain’tafraidofnofilefragmentation:causesandpreventionofits On-DemandHigh-ThroughputStorageAccessintheBaMSystemArchitecture.
performanceimpactonmodernflashSSDs.InProceedingsofthe22ndUSENIX InASPLOS.
ConferenceonFileandStorageTechnologies(SantaClara,CA,USA)(FAST’24). [59] DevendraSinghSachan,MikeLewis,MandarJoshi,ArmenAghajanyan,Wentau
USENIXAssociation,USA,Article12,16pages. Yih,JoëllePineau,andLukeZettlemoyer.2022.ImprovingPassageRetrievalwith
[36] YannisKalantidisandYannisAvrithis.2014. Locallyoptimizedproductquan- Zero-ShotQuestionGeneration.InConferenceonEmpiricalMethodsinNatural
tizationforapproximatenearestneighborsearch.InProceedingsoftheIEEE LanguageProcessing. https://api.semanticscholar.org/CorpusID:248218489
conferenceoncomputervisionandpatternrecognition.2321–2328. [60] MarkSilberstein,BryanFord,IditKeidar,andEmmettWitchel.2013. GPUfs:
[37] VladimirKarpukhin,BarlasOğuz,SewonMin,PatrickLewis,LedellYuWu, IntegratingafilesystemwithGPUs.InASPLOS.
SergeyEdunov,DanqiChen,andWentauYih.2020.DensePassageRetrieval [61] ChanopSilpa-AnanandRichardHartley.2008.OptimisedKD-treesforfastimage
forOpen-DomainQuestionAnswering. ArXivabs/2004.04906(2020). https: descriptormatching.In2008IEEEConferenceonComputerVisionandPattern
//api.semanticscholar.org/CorpusID:215737187 Recognition.1–8. https://doi.org/10.1109/CVPR.2008.4587638
[38] JonMKleinberg.2000. Navigationinasmallworld. Nature406,6798(2000), [62] Solidigm.2023. D7-P5510SeriesProductPage. https://www.solidigm.com/
845–845. products/data-center/d7/p5510.html
[39] AtsutakeKosugeandTakashiOshima.2019.AnObject-PoseEstimationAcceler- [63] ZiyuSong,JieZhang,JieSun,MoSun,ZihanYang,ZhengZhang,XuzhengChen,
ationTechniqueforPickingRobotApplicationsbyUsingGraph-Reusingk-NN FeiWu,HuajinTang,andZekeWang.2025. CAM:AsynchronousGPU-Initiated,
Search.In2019FirstInternationalConferenceonGraphComputing(GC).68–74. CPU-ManagedSSDManagementforBatchingStorageAccess.In2025IEEE41st
https://doi.org/10.1109/GC46384.2019.00018 InternationalConferenceonDataEngineering(ICDE).IEEEComputerSociety,Los
[40] ArtemKroviakov,PetrKurapov,ChristophAnneser,andJanaGiceva.2024.Het- Alamitos,CA,USA,2309–2322. https://doi.org/10.1109/ICDE65448.2025.00175
erogeneousIntra-PipelineDevice-ParallelAggregations.InProceedingsofthe [64] JieSun,MoSun,ZhengZhang,ZuochengShi,JunXie,ZihanYang,JieZhang,
20thInternationalWorkshoponDataManagementonNewHardware.1–10. ZekeWang,andFeiWu.2025.Hyperion:Co-OptimizingSSDAccessandGPU
[41] BohyunLee,MijinAn,andSang-WonLee.2023.LRU-C:ParallelizingDatabase ComputationforCost-EfficientGNNTraining.In2025IEEE41stInternational
I/OsforFlashSSDs.InVLDB. ConferenceonDataEngineering(ICDE).IEEEComputerSociety,321–335.
[42] AlbertoLernerandGustavoAlonso.2024. Dataflowarchitecturesfordata [65] KengoTerasawaandYuzuruTanaka.2007. SphericalLSHforapproximate
processingonmodernhardware.In2024IEEE40thInternationalConferenceon nearestneighborsearchonunithypersphere.InAlgorithmsandDataStructures:
DataEngineering.IEEE,5511–5522. 10thInternationalWorkshop,WADS2007,Halifax,Canada,August15-17,2007.
[43] JieLi,HaifengLiu,ChuanghuaGui,JianyuChen,ZhenyuanNi,NingWang,and Proceedings10.Springer,27–38.
YuanChen.2018.Thedesignandimplementationofarealtimevisualsearch [66] RisiThonangiandJunYang.2017.Onlog-structuredmergeforsolid-statedrives.
systemonJDE-commerceplatform.InProceedingsofthe19thInternational In2017IEEE33rdInternationalConferenceonDataEngineering(ICDE).IEEE,
MiddlewareConferenceIndustry.9–16. 683–694.
[44] JingLi,Hung-WeiTseng,ChunbinLin,YannisPapakonstantinou,andSteven [67] BingTian,HaikunLiu,YuhangTang,ShihaiXiao,ZhuohuiDuan,XiaofeiLiao,
Swanson.2016. Hippogriffdb:Balancingi/oandgpubandwidthinbigdata HaiJin,XuecangZhang,JunhuaZhu,andYuZhang.2025. TowardsHigh-
analytics.ProceedingsoftheVLDBEndowment9,14(2016),1647–1658. throughputandLow-latencyBillion-scaleVectorSearchvia{CPU/GPU}Collab-
[45] ChangyueLiao,MoSun,ZihanYang,JunXie,KaiqiChen,BinhangYuan,FeiWu, orativeFilteringandRe-ranking.In23rdUSENIXConferenceonFileandStorage
andZekeWang.2025.Ratel:OptimizingHolisticDataMovementtoFine-Tune Technologies(FAST25).171–185.
100BModelonaConsumerGPU.In2025IEEE41stInternationalConferenceon [68] LeonardVonMerzljak,PhilippFent,ThomasNeumann,andJanaGiceva.2022.
DataEngineering(ICDE).IEEEComputerSociety,292–306. WhatAreYouWaitingFor?UseCoroutinesforAsynchronousI/OtoHideI/O
[46] YuryMalkov,AlexanderPonomarenko,AndreyLogvinov,andVladimirKrylov. LatenciesandMaximizetheReadBandwidth!.InADMS@VLDB.36–46.
2014.Approximatenearestneighboralgorithmbasedonnavigablesmallworld [69] JianguoWang,XiaomengYi,RentongGuo,HaiJin,PengXu,ShengjunLi,Xi-
graphs.InformationSystems45(2014),61–68. https://doi.org/10.1016/j.is.2013. angyuWang,XiangzhouGuo,ChengmingLi,XiaohaiXu,KunYu,Yuxing
10.006 Yuan,YinghaoZou,JiquanLong,YudongCai,ZhenxiangLi,ZhifengZhang,
[47] YuA.MalkovandD.A.Yashunin.2020. EfficientandRobustApproximate YihuaMo,JunGu,RuiyiJiang,YiWei,andCharlesXie.2021. Milvus:A
NearestNeighborSearchUsingHierarchicalNavigableSmallWorldGraphs. Purpose-BuiltVectorDataManagementSystem.InProceedingsofthe2021In-
IEEETransactionsonPatternAnalysisandMachineIntelligence42,4(2020),824– ternationalConferenceonManagementofData(VirtualEvent,China)(SIGMOD
836. https://doi.org/10.1109/TPAMI.2018.2889473 ’21).AssociationforComputingMachinery,NewYork,NY,USA,2614–2627.
[48] FabioMaschiandGustavoAlonso.2023. Thedifficultbalancebetweenmod- https://doi.org/10.1145/3448016.3457550
ernhardwareandconventionalCPUs.InProceedingsofthe19thInternational [70] YiWang,JiajianHe,KaoyiSun,YunhaoDong,JiaxianChen,ChenlinMa,
WorkshoponDataManagementonNewHardware.53–62. AmelieChiZhou,andRuiMao.2024.BoostingwriteperformanceofKVstores:
[49] YitongMeng,XinyanDai,XiaoYan,JamesCheng,WeiwenLiu,JunGuo,Benben AnNVM-enabledstoragecollaborationapproach.In2024IEEE40thInternational
Liao,andGuangyongChen.2020. PMD:AnOptimalTransportation-Based ConferenceonDataEngineering(ICDE).IEEE,2082–2095.
UserDistanceforRecommenderSystems.InAdvancesinInformationRetrieval, [71] YiWang,JiananYuan,ShangyuWu,HuanLiu,JiaxianChen,ChenlinMa,and
JoemonM.Jose,EmineYilmaz,JoãoMagalhães,PabloCastells,NicolaFerro, JianbinQin.2024.Leaderkv:Improvingreadperformanceofkvstoresvialearned
MárioJ.Silva,andFlávioMartins(Eds.).SpringerInternationalPublishing,Cham, indexanddecoupledkvtable.In2024IEEE40thInternationalConferenceonData
272–280. Engineering(ICDE).IEEE,29–41.
[50] MariusMujaandDavidG.Lowe.2014.ScalableNearestNeighborAlgorithms [72] ZhenghaoWang,LidanShou,KeChen,andXuanZhou.2024.Bushstore:Efficient
forHighDimensionalData.IEEETransactionsonPatternAnalysisandMachine b+treegroupindexingforlsm-treeinnon-volatilememory.In2024IEEE40th
Intelligence36,11(2014),2227–2240.https://doi.org/10.1109/TPAMI.2014.2321376 InternationalConferenceonDataEngineering(ICDE).IEEE,4127–4139.
[51] GonzaloNavarro.2002. Searchinginmetricspacesbyspatialapproximation. [73] JiaWeiandXingjunZhang.2022.Howmuchstoragedoweneedforhighper-
TheVLDBJournal11(2002),28–46. formanceserver.In2022IEEE38thInternationalConferenceonDataEngineering
[52] JiongkangNi,XiaoliangXu,YuxiangWang,CanLi,JiajieYao,ShihaiXiao,and (ICDE).IEEE,3221–3225.
XuecangZhang.2023. Diskann++:Efficientpage-basedsearchoverisomor- [74] YanXia,KaimingHe,FangWen,andJianSun.2013.Jointinvertedindexing.In
phicmappedgraphindexusingquery-sensitivityentryvertex.arXivpreprint ProceedingsoftheIEEEInternationalConferenceonComputerVision.3416–3423.
arXiv:2310.00402(2023). [75] YumingXu,HengyuLiang,JinLi,ShuotaoXu,QiChen,QianxiZhang,Cheng
[53] MohammadNorouziandDavidJFleet.2013.Cartesiank-means.InProceedings Li,ZiyueYang,FanYang,YuqingYang,etal.2023.Spfresh:Incrementalin-place
oftheIEEEConferenceoncomputerVisionandPatternRecognition.3017–3024. updateforbillion-scalevectorsearch.InProceedingsofthe29thSymposiumon
[54] NVIDIA.2011.NVIDIAGPUDirect.https://developer.nvidia.com/gpudirect. OperatingSystemsPrinciples.545–561.
[55] NVIDIA Corporation. 2023. GPUDirect Storage. https://docs.nvidia.com/ [76] PeterNYianilos.1993. Datastructuresandalgorithmsfornearestneighbor
gpudirect-storage/index.html. searchingeneralmetricspaces.InSoda,Vol.93.311–21.
[56] Shumpei Okura, Yukihiro Tagami, Shingo Ono, and Akira Tajima. 2017. [77] JieZhang,DavidDonofrio,JohnShalf,MahmutTKandemir,andMyoungsoo
Embedding-basedNewsRecommendationforMillionsofUsers.InProceedingsof Jung.2015.Nvmmu:Anon-volatilememorymanagementunitforheterogeneous
the23rdACMSIGKDDInternationalConferenceonKnowledgeDiscoveryandData gpu-ssdarchitectures.InPACT.
Mining(Halifax,NS,Canada)(KDD’17).AssociationforComputingMachinery, [78] TobiasZiegler,CarstenBinnig,andViktorLeis.2022. ScaleStore:Afastand
NewYork,NY,USA,1933–1942. https://doi.org/10.1145/3097983.3098108 cost-efficientstorageengineusingDRAM,NVMe,andRDMA.InProceedingsof
[57] TarikulIslamPapon.2024.Enhancingdatasystemsperformancebyexploiting the2022InternationalConferenceonManagementofData.685–699.
SSDconcurrency&asymmetry.In2024IEEE40thInternationalConferenceon