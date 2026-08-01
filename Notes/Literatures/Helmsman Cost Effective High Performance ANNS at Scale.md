# Helmsman Cost Effective High Performance ANNS at Scale

**Source**: Helmsman Cost Effective High Performance ANNS at Scale.pdf
**Format**: .pdf

---

The Clustering Strikes Back: Building Cost-Effective
and High-Performance ANNS at Scale with
Helmsman (Operational Systems)
Yuchen Huang and Baiteng Ma, East China Normal University and Xiaohongshu
Inc; Yiping Sun, Yang Shi, Xiao Chen, Xiaocheng Zhong, Zhiyong Wang, and
Yao Hu, Xiaohongshu Inc; Erci Xu, Shanghai Jiaotong University;
Chuliang Weng, East China Normal University
https://www.usenix.org/conference/osdi26/presentation/huang-yuchen
This paper is included in the Proceedings of the 20th USENIX
Symposium on Operating Systems Design and Implementation.
July 13–15, 2026 • Seattle, WA, USA
ISBN 978-1-939133-55-7
Open access to the Proceedings of the 20th USENIX Symposium on
Operating Systems Design and Implementation is sponsored by

The Clustering Strikes Back:
Building Cost-Effective and High-Performance ANNS at Scale with Helmsman
(Operational Systems)
YuchenHuang1,3,BaitengMa1,3,YipingSun3,YangShi3,XiaoChen3,
XiaochengZhong3,ZhiyongWang3,YaoHu3,ErciXu2,ChuliangWeng1
1EastChinaNormalUniversity 2ShanghaiJiaotongUniversity 3XiaohongshuInc
Abstract in-DRAMANNSinfrastructure[2,9].Wearethereforemoti-
vatedtoexploremorecost-efficientalternatives.
RedNote(a.k.a.,Xiaohongshu,aglobal-scalesocialnetwork
TherecentadvancementinNVMeSSDshasmadethem
platform)widelyadoptsapproximatenearestneighborsearch
a promising candidate given theirhighbandwidthandlow
(ANNS)topoweritssearch,recommendation,andadvertising
costperGB[18,25,34].Forexample,a12-drivePCIe-Gen5
services.DuetothedemandingServiceLevelAgreements
SSDarray[12]candeliverroughly30%ofthebandwidthof
(SLAs),wehavetorelyonin-memorygraph-basedANNS
a12-channelDDR5memory[10],yetSSDcostsabout1/40
(i.e.,HNSW)toprovidehighthroughputandlowlatency.
ofDRAM(i.e.,0.2$/GBvs. 8$/GB). Whilewehavesuc-
However,theever-growinguserbaseandcontentvolume
cessfullydeployedgraph-basedhybrid(SSD+DRAM)ANNS
have ledto an explosive increase in memory footprintand
systemslikeDiskANN[49]forthemorerelaxedofflinework-
consequentlyhugeCapExandOpEx.Afterexploringvarious
loads(e.g.,contentmoderation),usingthemforonlineser-
alternatives,wefindthatbuildingaclustering-basedANNS
vices(e.g.,search)remainsimpracticableintermsoflatency
on top of all-flash servers can be promising. Yet, we still
andthroughputSLAs.Themainreasonisthegreedygraph
experiencesevereoverheadsfromthekernelI/Ostack,afixed
traversalsmaintainlongcandidatelists(e.g.,lengthscanbe
pruningstrategy,andslowindexconstruction.
upto1.5×top-k),whichincurmanyserializedI/Osandthus
We present HELMSMAN, a high-performance and cost-
failtoutilizehighbandwidthofSSDs.
effective clustering-based ANNS system,which combines
Theaboveobservationmotivatesustorethinkthepossi-
anANNS-orienteduserspacestoragestack,aleveling-learned
bility of using clustering-based ANNS. With dependency-
pruningmodule,andGPU-acceleratedpipelinesofconstruc-
freeI/Osissuedinbatches,clustering-basedANNS,suchas
tion. HELMSMAN saves over 90% of hardware costs and
SPANN [17],can be expected to achieve low latency that
enables billion-scale index (re)builds within hours. In the
meetsourSLAandalsobescaledforthroughputbyadding
currentproductiondeployment,operatingstablyforseveral
moreSSDs.Yet,toapplytheminproductionremainschal-
months,40machinesnowhostANNSworkloadsthatprevi-
lenging.First,underthetraditionalI/Ostack,SPANNuses
ouslyrequiredabout35,000coresand0.35PBDRAM.
onlyabout20–60%ofSSDbandwidth,resultinginasignifi-
cantthroughputgaptoin-DRAMHNSW.Second,giventhe
1 Introduction varying top-k ofrealworkloads,the existing fixedpruning
approachcannotsufficientlyreduceredundantscansandleads
RedNote(a.k.a.,Xiaohongshu)[8]isaglobalsocialmedia tounstableper-queryperformance.Third,theexistingsingle-
platformforuserstoshareandinteractwithphotos,videos, node andCPU-only construction can take tens ofhours or
andtextintheformof“notes”.By2025,theplatformhosts evendays,failingtosupportfastrebuildsneededbyfrequent
over300millionmonthlyactiveusersandmorethan80mil- updatesofembeddingmodelsandvectors.
lioncreators[5].Asthecoreinfrastructurebehindsearch,rec- Hence,toovercometheselimitations,wedevelopHELMS-
ommendation,andadvertising[22,41,43],ourapproximate MAN,ahigh-performanceandcost-effectiveANNSsystem
nearestneighborsearch(ANNS)servicemanageshundredsof usingclustering-basedindexesatopall-flashservers.There
billionsofembeddingvectorsandsustainsmillionsofqueries arethreemaintechniques.First,webuildanANNS-oriented
persecond(QPS)withstrictlatencyservice-levelagreements userspacestoragebackendthatbypassesthekernelI/Ostack,
(SLAs)(e.g.,5-10msforreal-timeservices). minimizingsoftwareoverheadanddirectlyorchestratingde-
Tomeetthequalityofservices(QoS),wepreviouslyrelied vicestomatchtheANNS-specificI/Opatterns.Second,we
onlargein-DRAMgraphindexes[20,40]forhighthroughput developaleveling-learnedpruningmodulethatadaptstoboth
andlowlatency.However,thescalingofusersandcontent top-k and query distributions,while remaining compatible
drasticallyincreasesthememoryfootprint,pushingtheANNS withSSD-friendlybatchedI/O.Third,weleverageGPUac-
infrastructure at RedNote to reach the petabyte level. This celerationanddynamicallyallocateCPUsforindexconstruc-
incursprohibitivelyhighCapExandOpExfortheexisting tion,enablingsub-hourbuildsforcommon-scale(e.g.,0.1B)
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1623

(a)Totalrowsofvectordatasets. (b)SLAsofperformance. (c)Top-kvalueofrequests. (d)Frequencyofconstruction.
Figure1:CharacterizingANNSofRedNotealong4aspects:scale,SLA,top-k,andconstruction.SearchisdenotedasSrch,and
othersarerecommendation(Rec),advertising(Ads),contentmoderation(CM),andretrieval-augmentedgeneration(RAG).
andhour-levelbuildsforultra-large-scale(e.g.,10B)indexes. millisecondaveragelatency[16]under∼300KQPS,ourtyp-
Our evaluations show that HELMSMAN delivers 2–16× icalpeaktraffic.Third,ANNSisthefirststageoftheranking
higherthroughputthanexistingDRAM–SSDANNSandup pipelineinsearch. Thus,itrequiresarelativelylargetop-k
to 85% of the throughput of in-DRAM ANNS,while pre- (e.g.,around100to3,000)toprovidesufficientcandidates
serving latencySLAs. We are activelyrolling out HELMS- fordownstreamre-rankingmodels[21,37].Finally,because
MANtoourproductionenvironment.Currently,HELMSMAN ourembedding models are continuouslytrainedwithdaily
can use only 40 machines with about 30-40 TB DRAM collectedmetrics(e.g.,userbehaviorsandcontentpopular-
in total to sustain online traffic that previously consumed ity),we wish to rebuild (instead of in-place updating such
roughly 35,000 CPU cores and ∼0.35 PB of in-DRAM asSPFresh[58],Quake[43]andOdinANN[23])theentire
ANNS infrastructure, saving more than 90% device costs. indexesonadailybasis.
The open-source proof-of-concept version of HELMSMAN Recommendation.Unlikesearch,recommendationonlyfo-
anddatasetsfittedtoreal-worlddistributionsareavailableat cusesonthepopularsubsetsoffullcorpus.Asaresult,the
https://github.com/Red-EAD/helmsman.
totalvectorvolumeissignificantlysmallerthanthatofsearch,
rangingfrom1to100millionvectorsperindex.Recommen-
dationdirectlyservesendusersbutinvolvesmorerecallpaths.
2 Background
Thus,theonlinerequestthroughputcanreach ∼2.5million
QPSwhilestillrequiringmillisecond-levellatencySLAs[33].
2.1 ANNS-basedServicesinRedNote
Moreover,post-filteringbasedonuser-specificconstraintsis
commoninrecommendation.Toensuresufficientresultsafter
RedNote (a.k.a., Xiaohongshu) [8] is a global social plat-
filtering[63],thetop-kfromANNScanbeupto1,000.Fi-
formwithhundredsofmillionsofactiveuserssharingand
nally,embeddingmodelsareupdatedinbatches(aggregated
interactingwithvarioustypesofcontentincludingpictures,
fromminutestohours[42,47])basedonreal-timefeedback
commentsandshortvideosonadailybasis.Theproperfunc-
(e.g.,click-throughrates),leadingtouptotenthousandindex
tioningofRedNotereliesheavilyonthesearchengine,recom-
rebuildsperdayandacumulativerebuiltvolumeontheorder
mendationsystem,advertisingplatform,contentmoderation,
oftensofbillionsofvectors.
andemergingAIservices(e.g.,retrieval-augmentedgenera-
tionforlargelanguagemodels).Alloftheabovearesupported Advertising.Embeddedfromproducts,advertisinghasfewer
byapproximatenearestneighborsearch(ANNS)overhun- vectors, around one billion in total. Similar to search and
dredsofbillionsofhigh-dimensionalvectorswithmillionsof recommendation,advertisingalsodirectlyservesusersand
queriespersecond.DespiteallbeingANNS-based,theseser- thusrequiresmillisecond-levellatencySLAsundermillions
vicescanhavedifferentcharacteristicsasshowninFigure1, ofQPS[59].Inaddition,advertisingfollowsapost-filtering
suchasscaleofdataset(Figure1a),theSLAofperformance pipeline. ANNS retrieval is followed by scalarfiltering on
(Figure1b),thetop-kofrequests(Figure1c),andtheindex multipleattributes(e.g.,exposureconstraintsandbillingsta-
building(Figure1d).Wenowfurtherdiscussthemindetail. tus),so the required top-k can be large as well (e.g.,up to
3,000)[61].Finally,forindexconstruction,sincetheembed-
Search.First,oursearchtargetsthefullcorpus(i.e.,alluser-
dingmodelsaremodifiedincrementallybyratesofclicksor
generatedcontentandweb-widedata)andtheindexcanreach
purchases on the orderof minutes,this requires that index
uptotensofbillionsofvectors.Inaddition,thesearchser-
rebuildskeepupwiththesereal-timeupdatesaswell.
vicesalsofollowamulti-pathworkflowwheredifferentrecall
pathscovervarioussubsetsofthecorpus(e.g.,texts,images, Contentmoderation.Thismaintainstwotypesofindexes,
videos,anduserbehaviors)toensurehighaccuracy.There- thelargeallow-listcorpusandthesmallerblock-listcorpus.
fore,search has the largest overall vector volume,totaling Theallowlistsconsistofallcontentconformingtopolicies
up to twenty billion vectors in practice. Second,search is andvalues,sotheirindexescanreachupto10Bvectors.The
directlyexposedtoendusers,whichrequiresanSLAof∼10 block-liststoresonlyrestrictedcontentandistypicallymuch
1624 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Memory Shard
xednI
hparG
MARD-nI
DRAM-SSD Node
DRAM
Query
Vector
(a)In-DRAMgraphindexeson
distributednodesforachieving
lowlatency.
xednI
hparG
DSS-MARD
Query Vector
DRAM
SSD
(a)PB-levelDRAMusage. (b)Throughputoverkill.
Figure3:Inouronlineservices,latencySLAsforcemassive
DRAMforpurein-DRAMindexes,whilethroughputSLAsare
(b)DRAM-SSDgraphindexeson
modesttothefull-loadmaximumofthein-DRAMdeployment.
asinglenodeforsavingmemory
footprint.
Anditiswidelydeployedforsearch,recommendation,and
advertising.Figure2ashows,foragivenquery,theHNSW
Figure2:TwosolutionsemployedinservicesofRedNote.
search starts from an entry node on the top layer and per-
smaller (e.g.,10M vectors). Content moderation is mainly forms greedy best-neighbor descent layer by layer,until it
an offline workload,and new content is compared against reachesthebottom,whereabest-firstsearchoveracandidate
bothallow-listandblock-list,thenassessmentmodelsselect poolproducesthefinaltop-kresults.Allgraphdata,including
high-riskcandidatesthatareforwardedtomanualchecking. neighborlistsandrawvectors,arekeptinDRAMsothatthe
ThispipelineresultsinmorerelaxedlatencySLAsandlower critical path consists only of in-memory accesses. When a
overallthroughputthantheabove-mentionedservices[45]. single shard cannot hold the entire index,we partition the
Additionally, to capture restricted content with best effort, datasetacrossmultiplememoryshardsandexecutesearchin-
wealsouserelativelylargetop-k(upto∼500).Sincethese dependentlyoneachHNSWshard.Thefrontendthenmerges
collectionschangeslowly,block-listindexesarerebuiltona thepartialresultsfromallshardstoobtaintheglobaltop-kan-
dailybasisandtheallow-listindexesarerefreshedweekly. swers.Thisdesigncandeliverconsistentlylowsearchlatency
Retrieval-augmentedgeneration.OurANNSalsosupports andhighQPS,guaranteeingQoS.
emergingAIapplicationslikeRAG.InRAG,ANNSismainly Hybrid DRAM-SSD Graph. For scenarios with more re-
usedtoindextask-specificknowledgebaseswithsizesvary- laxed performance SLAs,such as content moderation and
ingwidelyfromaboutonemilliontoseveralbillionvectors RAG,weemployhybridDRAM–SSDgraphindexes,asil-
dependingontheapplications.SinceLLMinferencedomi- lustrated in Figure 2b. These indexes significantly reduce
natesresourceconsumptionandcurrentmodelshavelimited DRAM consumption, allowing a large-scale graph to be
contextlength,theSLArequirementsfortheANNSstageare hosted on a single node. Representative designs include
relativelyrelaxed(e.g.,∼20ms)[29]andtherequiredtop-k DiskANN[49]anditsrecentoptimizedvariantssuchasStar-
ismuchsmaller(e.g.,10-100)thanotherservices’[44,62]. ling [56] and PipeANN [22]. They retain PQ-compressed
Moreover,theunderlyingknowledgebasesevolveslowlyand vectorsandasmallsetoffrequentlyaccessedvectorscached
theembeddingmodelschangeinfrequently,soindexrebuilds inDRAM,whilestoringthefull-precisionvectorsandgraph
areneededfarlessoftenthaninotheronlineworkloads. edgesonSSDstocutmemoryfootprint.Duringquerypro-
cessing,thegraphistraversedwiththebest-firstsearchstrat-
egy anda beam-search procedure. The search pathalways
2.2 SolutionsforANNS-basedServices
advancesalongtheedgestowardstheneighborthatisclosest
Graph-basedANNSoffershighthroughputwithlowlatency, tothequery.Thebeam-searchwidthistranslatedintoanI/O
andisthereforewidelydeployedinRedNote’sproductionser- width that controls how many candidates are fetched from
vices.TosatisfythestrictperformanceSLAsofsearch,recom- SSDsinbatches,therebyimprovingbandwidthutilizationfor
mendation,andadvertising,werunalargefleetofdistributed higherperformance.
memoryshardsthathostin-DRAMgraphindexes[20,40].
The aggregated count of CPU cores already exceeds 105 3 Motivation
among4,000nodes,spanning∼50clustersasoftoday.For
scenarioswithslightlymorerelaxedlatencyandthroughput
3.1 Can’tAffordIn-memoryANNStoScale
requirements(e.g.,contentmoderationandRAG),weinstead
employhybridDRAM–SSDnodeswithSSD-backedgraph Overthepastfewyears,thefastgrowthofRedNote’suser
indexes[22,49,56]totradesomelatencyforamuchsmaller basehasdriventhedatavolumeofourstoredvectorcorpusto
memoryfootprint. bedoubledannually.Themorethanbillionsofnewvectors
In-DRAMGraph.Inourproduction,HNSW[40],oneof persistedeachyearexactsaheavytollontheCapExofour
thestate-of-the-artin-DRAMindexes,iscommonlyadopted. in-memoryANNSdeployment.Figure3aillustratesthat,as
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1625

DRAM-SSD Node
DRAM-SSD Clustering Index
HNSW
10 ms 10x DRAM SSD
5 ms 20x 25x
10 ms
Query
5 ms Vector Batched and Dependency-Free
PipeANN
Figure 5: DRAM-SSD clustering-based index follows the
(a)Averagelatency. (b)P999latency. (c)Throughputgap. batchedanddependency-freeI/OpatternontheNVMeSSDs.
Figure4:Allgraph-basedsystemsfailinreplacingin-DRAM
Latency. Figure 4a and Figure 4b report the mean and
solution.DiskANNandStarlingcannevermeetthelatency
99.9thpercentiletaillatencyofthethreecandidates.Wetest
SLAs.PipeANNshowsaninsuperablegapinthroughput.Srch
them with a latency-friendly strategy by executing single-
referstothesearchbusiness,withlatencySLAsof10ms.And
threadedqueries(i.e.,lowestconcurrency).Wecanobserve
Rec&Adsreferstotherecommendationandadvertising,with
bothDiskANNandStarlingconsistentlyfailtomeetbothour
latencySLAsof5ms.
averageandtaillatencySLAsinthefield(thegreenshaded
area).PipeANN,byleveragingintra-queryparallelism(i.e.,
Hardware DRAM[10] Gen5SSD[12] Gen4SSD[11]
multi-threadedbeam-searchtraversal)tobetterutilizeSSD
Price($/GB) 8(100%) 0.2(2.5%) 0.15(1.9%)
bandwidth,achievesthelowestlatencyamongthethreebut
BW(GB/s) 12×38(100%) 12×12(32%) 12×6.5(17%)
stillstrugglestosatisfytheonlineSLAsathightop-kvalues,
Table1:PriceandbandwidthcomparisonsasofDec.2025. especiallyfortaillatency.
Throughput.TofurtherexplorewhetherPipeANNcanserve
of 2025,the in-DRAM HNSW indexes for search,recom- asa(partial)replacement,weevaluateitsthroughputagainst
mendation,andadvertisinghavealreadyconsumedPB-level in-DRAMHNSWunderthelatencySLAs.AsshowninFig-
DRAMinpractice. EvenjusttheANNindexesofasingle ure4c,evenwith12PCIe-Gen5SSDsprovidingover30%of
service(e.g.,search)cannowconsumehundredsofterabytes DDR5DRAMbandwidth(Table1),PipeANN’speakthrough-
ofDRAM. putremains10–25×lowerthanthatofHNSW.Therootcause
However,themassiveDRAMusageismostlyprovisioned isthatthegraph-basedDRAM-SSDANNSinherentlysuf-
to maintain the QoS (e.g., 10 ms average latency SLA fersfromstronglyserialized,dependency-chainI/Osduring
of search). Specifically, Figure 3b shows that, out of the search (i.e.,each expansion step depends on the results of
100%throughputprovidedbyin-DRAMdeployments,only previousreads).Thisserializedaccesspatternmagnifiesthe
∼32–43%isactuallyneededtomaintaintherequiredlatency
rawlatencygapbetweenSSDsandDRAM(around102-103).
SLAs.Nevertheless,westillneedtherest57–68%ofDRAM, Inourlow-latencyandhigh-throughputonlineservices,this
notforthroughput,butforthecapacitytohosttheentireset limitedperformancerulesoutthepossibilityofgraph-based
ofindexestoavoidlatencyspikesunderworkloadbursts[39]. DRAM-SSDsystemsasaviablereplacementforin-DRAM
solutionsatscale.
3.2 Can’tReplacewithHybridGraph
3.3 Clustering-BasedANNSBringsHope
RecallthatourCMandRAGservices(see§2)haveadopted
a hybrid DRAM-SSD architecture for the graph-based Failingtoportin-memoryANNSwithgraph-basedhybrid
DiskANNtoreducememoryconsumption.GiventhatSSDs designsmotivatesustoreconsideranotherdesign,clustering-
arebecomingincreasinglyaffordableandhigh-performance basedDRAM-SSDANNS.Atahighlevel,Figure5shows
asTable1,itthusmotivatesustoconsiderintegratingSSDs thatSPANN[17],arepresentativeclustering-basedANNS,
into otherservices (e.g.,search) as well. Here,we explore uses a clustered layout. The clusters’ centroids are kept in
thefeasibilitybyconductingcomprehensiveevaluationsof DRAM,whilevectorsarestoredonSSDasclusteredposting
existinggraph-basedDRAM-SSDANNSsystems,including lists.Duringsearch,itfirstsearchesthein-memorygraphof
DiskANN,Starling,andPipeANN,onourstandard96-core centroids to identify the nprobe number of (e.g.,3 in Fig-
serverequippedwith12PCIe-5.0SSDs.UsingtheSIFT100M ure5)closestpartitions,thenissuesbatchedreadstofetchthe
dataset[13],wetargeta90%recallrateandevaluatetop-k correspondingpostinglists,andfinallycomputesthetop-k
valuesfrom10to3,000,whichisconsistentwithboththeBi- neighborsfromtheloadedcandidatesoftheselists.
gAnnBenchmark[48]andouronlineservices’requirements Historically,thislineofresearchwasknowntobelatency-
(§2.1).Unfortunately,theresultsaredisappointinginterms friendly but largely dismissed in the field due to the lim-
ofbothlatencyandthroughput. ited throughput [22,51,56]. However, the recent advance-
1626 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

10 ms
~12x
~12x ~12x
5 ms
~12x
86%
88%
|     |     |     |     |     |     |     |     |     | 87% | 86% |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(a)Near-SLAslatency. (b)Scalablethroughput. (a)Insufficientthroughput. (b)Lowbandwidthutilization.
| Figure           | 6: Based | on    | high-bandwidth | modern    | SSDs, | the        |     |     |     |     |     |     |
| ---------------- | -------- | ----- | -------------- | --------- | ----- | ---------- | --- | --- | --- | --- | --- | --- |
| clustering-based |          | SPANN | shows nearly   | qualified |       | search la- |     |     |     |     |     |     |
tencyandscalablethroughputunderthelargetop-kvalues.
| ment in      | high-bandwidth |             | NVMe SSDs    | (e.g.,12GB/s |       | from    |     |     |     |     |     |     |
| ------------ | -------------- | ----------- | ------------ | ------------ | ----- | ------- | --- | --- | --- | --- | --- | --- |
| Gen5 SSD)    | has            | changedthis | landscape.   | As           | shown | in Fig- |     |     |     |     |     |     |
| ure 6, using | SPANN          |             | and up to 12 | PCIe-Gen5    |       | SSDs on |     |     |     |     |     |     |
SIFT100M,ourevaluationsdemonstratethat,withthebatched
anddependency-freeI/Opattern,thisclustering-baseddesign
|                |          |                 |              |           |          |          | (c)Un-adaptedrangeofscans. |     |     | (d)Long-timeindexbuilding. |     |     |
| -------------- | -------- | --------------- | ------------ | --------- | -------- | -------- | -------------------------- | --- | --- | -------------------------- | --- | --- |
| can already    | approach |                 | latency SLAs | of online | services | un-      |                            |     |     |                            |     |     |
| der processing |          | single-threaded | query        | and       | achieve  | scalable |                            |     |     |                            |     |     |
Figure7:Clustering-basedSPANNstillhasdeficiencies.Its
| throughput | by   | adding      | SSDs. In addition,Figure |              |     | 6a shows |             |      |       |               |                |      |
| ---------- | ---- | ----------- | ------------------------ | ------------ | --- | -------- | ----------- | ---- | ----- | ------------- | -------------- | ---- |
|            |      |             |                          |              |     |          | performance | also | fails | to fully meet | the throughput | SLAs |
| that, even | when | we increase | top-k                    | up to 3×103, |     | SPANN    |             |      |       |               |                |      |
(∼12%-14%ofin-DRAMHNSW),duetothelowbandwidth
nearlykeepstheaverageandtaillatencywithinorclosetothe
utilizationandun-adaptedrangeofscans.Furthermore,its
SLAsofsearch,recommendation,andadvertising.Moreover,
single-nodeCPU-onlyconstructionofindexesincursaheavy
Figure6billustratesthatthethroughputscalesalmostlinearly
expenditureoftime,violatingthefreshnessofservices.
withthenumberofSSDsandreaches∼12×speedupwhen
using12SSDs,reinforcingourassumptionthatmodernSSDs
|     |     |     |     |     |     |     | scan range | (i.e.,the | numberofloadedclusters |     | nprobe) | im- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --------- | ---------------------- | --- | ------- | --- |
withclustering-basedindexcanbeapromisingdirection.
pactsboththroughputandsearchquality.Itreliesonafixed
|                                       |     |     |     |     |     |     | distance-basedpruningruleshownin |     |           |                         | Equation1.Afterlo- |       |
| ------------------------------------- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --------- | ----------------------- | ------------------ | ----- |
|                                       |     |     |     |     |     |     | catingtheclosestcentroidc        |     |           | ,SPANNincludesclustersX |                    |       |
| 3.4 ChallengesinDeployingSPANNatScale |     |     |     |     |     |     |                                  |     |           | i1                      |                    | ij    |
|                                       |     |     |     |     |     |     | in the search                    | if  | distances | from q to               | their centroids    | c are |
ij
However,evenwhenwepairSPANNwiththearrayofNVMe withina(1+ε)factorofthedistancetoc ,whereεischo-
i1
SSDs,suchasolutionstillcannotbedirectlydeployedinthe
senempiricallyanddoesnotadapttoquerydifficultyordata
field.Challengespersistinbothonlinesearchandofflinecon- distribution. Figure 7c presents statistics for∼100 queries
struction.Foronlineserving,theachievedsearchthroughput undervaryingtop-k.Thescannedrangeafterpruningisonly
iswellbelowourproductionSLAs.Moreover,intheoffline slightlysmallerthantheno-pruning(W/O)baseline,yetfor
stage,theconstructionofindexesincursprohibitivetimeover- eachindividualquery,itoftenovershootstherangeneededto
headsthatmustbesubstantiallyreduced.
reachthetargetrecall(e.g.,90%),wastingI/Oandreducing
First,SPANNcannotyetserveasascalablereplacementfor throughput;orundershootsit,causinglargevarianceinrecall
thein-DRAMHNSWindexesdeployedinouronlinestack. andresultinginunstablesearchquality.
UnderthelatencySLAsofonlineservices,evenona96-core
search
nodewith12PCIe5.0SSDs,thethroughputremainsinsuffi- q−−−→Xij⇐⇒Dist(q,cij)≤(1+ε)Dist(q,c i1 ),
(1)
cient.AsshowninFigure7a,thereisstillathroughputgap Dist(q,c )≤Dist(q,c )≤···≤Dist(q,ciK)
|     |     |     |     |     |     |     |     |     | i1  | i2  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ofabout86-88%betweenSPANNandthein-DRAMHNSW
Finally,SPANNalsofacessignificantchallengesinoffline
| baseline.1 | Thisgapislargelyduetoinsufficientutilization |     |     |     |     |     |     |     |     |     |     |     |
| ---------- | -------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
index(re)building.AsshowninFigure7d,theexistingimple-
ofNVMeSSDs’bandwidth.Figure7bshowsthatSPANN
mentationconstructstheclusteringstructuresonastandalone
usesonly∼26-59%oftheavailablebandwidthonPCIeGen5
CPUnode.Whenthedatasetgrowsfromtenmilliontotensof
andGen4arrays,highlightingaprimaryopportunitytoscale
billionsofvectors,theconstructiontimeescalatesfromsev-
throughputbydrivingSSDbandwidthactuallyutilizedcloser
eralhourstomultipledays.Theseconstructionwindowsare
tothehardwarelimits.
farlongerthanwhatisacceptableinourproductionscenarios,
| Second, | SPANN’s | current | strategy | for | determining | the |     |     |     |     |     |     |
| ------- | ------- | ------- | -------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
whereembeddingmodelsandvectordataarerefreshedfre-
quently.Consequently,indexbuildingalsobecomesamajor
| 1Referring | to  | our production | index-building |     | settings, | edges and |     |     |     |     |     |     |
| ---------- | --- | -------------- | -------------- | --- | --------- | --------- | --- | --- | --- | --- | --- | --- |
bottleneckhinderingthepracticaldeploymentofSPANN.
efConstructionofHNSWaresetas24and120.SPANNissetas§5.1
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1627

ONLINE: ANNS-Oriented Serving Storage & Leveling-Learned Search Pruning  OFFLINE: Three-Step Heterogeneous Construction
(Sec 4.2 and Sec 4.3)
|     | Top-k Nearest Neighbors |     |     |     |     | Query, top-k |     |     |     |     |  (Sec 4.4) |     |     |
| --- | ----------------------- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | ---------- | --- | --- |
Generate
Multi-GPU Servers
|     |           |             |      | DRAM-SSD Serving Nodes |          |        |        |                |     |     | 1   | Initial   |     |
| --- | --------- | ----------- | ---- | ---------------------- | -------- | ------ | ------ | -------------- | --- | --- | --- | --------- | --- |
|     |           |             | DRAM | & CPU Cores            |          |        |        |                |     |     |     | Centroids |     |
|     |           |             |      |                        |          | Decide | Router |                |     |     |     |           |     |
|     | Calculate |             |      |                        | Locate   | 1      |        | gninurP hcraeS |     |     |     |           |     |
|     | Thread    | Intra-Query | 6    |                        | 2 nprobe | nprobe | Model  |                |     |     |     |           |     |
Parallel
Pool Distance  Rank Centroids Query, top-k, nprobe Local CPU Elastic CPU
|     | …   | Calculate | Top-k |     |     |           |     |     |     | Workers | BalanceClusters |     |     |
| --- | --- | --------- | ----- | --- | --- | --------- | --- | --- | --- | ------- | --------------- | --- | --- |
|     |     | …         |       |     |     | P r u n e |     |     |     | …       | 2               | &   |     |
(Optional) Nearest Ce n t r o ids Q u e ry ,   t o p - k, B u c k e t i n gB …- 0 : … Pad Boundary
|     |     |     | Neighbors |         | [ { C e n t r  | o i d , 3 n p r o b e | P r u n i n g |     |                        |     |     |     |     |
| --- | --- | --- | --------- | ------- | -------------- | --------------------- | ------------- | --- | ---------------------- | --- | --- | --- | --- |
|     |     |     |           | G r a p | h              | C l u s t e rs        | M o d e l s   |     |                        |     |     |     |     |
|     |     |     |           | I n d e | x D i s ta n c | e } , … ]             | B - n         | :   | Multi-Core CPU Servers |     |     |     |     |
Merge Index
|     | Search Thread |     | Thread-Local NVMeI/O Completion Queue |     |     | Thread-Local NVMe I/O Submission Queue |     |     |     |     |     |     |     |
| --- | ------------- | --- | ------------------------------------- | --- | --- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|     |               |     |                                       |     |     |                                        |     |     |     | …   | 3   | &   |     |
Train Model
|     | 5 Poll Completion of Clusters I/O |     |     | SSD |     | 4   | Submit Clusters I/O |     |     |     |     |     |     |
| --- | --------------------------------- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- |
…
Meta Data Raw NVMe 0 NVMe 1 NVMe 10NVMe 11 Global Distributed File System
|     | S A T A  S      | S D Index 0…Index x | NVMeCluster Lists of One Index (uniformly dist…ributed across blocks of multiple NVMe SSDs) |     |     |     |     |     |       |             |         |             |     |
| --- | --------------- | ------------------- | ------------------------------------------------------------------------------------------- | --- | --- | --- | --- | --- | ----- | ----------- | ------- | ----------- | --- |
|     | (F il e  S y st | e m)                |                                                                                             |     |     |     |     |     | Index | Pruning Tmp | Raw     | Release     |     |
|     |                 | NVMe Management     | SSD                                                                                         |     |     |     |     |     | Data  | Model Data  | Dataset | Final Index |     |
Figure8:Designoverviewof HELMSMANwithworkflowsofonlinesearchandofflineindexconstruction.
| 4   | HELMSMAN |     | Design |     |     |     |     |     |     |     |     |     |     |
| --- | -------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
stagepipeline.Notethatamajordrawbackinpreviousbuilds
|     |     |     |     |     |     |     | by a | single | node’s CPUs | is limited | computing | power | and |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------ | ----------- | ---------- | --------- | ----- | --- |
theinabilitytoscale.Hence,weintroduceGPUstogenerate
4.1 Overview
|     |     |     |     |     |     |     | initialcentroids |     | anddistributednodes |     | to  | acceleratebalanc- |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------------------- | --- | --- | ----------------- | --- |
ingandpadding.Backedbyaglobaldistributedfilesystem
| We  | present | HELMSMAN, | a   | high-performance |     | and cost- |     |     |     |     |     |     |     |
| --- | ------- | --------- | --- | ---------------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
effective ANNS system using clustering-based indexes on holdingthefinalindex,pruningmodels,temporarydata(e.g.,
all-flashservers.Figure8presentsanoverviewofHELMS- checkpoints),andrawdatasets,weorchestratetheentirecon-
structionpipelineend-to-end,achievingminute-levelindex
MAN,includingonlineserving(i.e.,thelefthalfofFigure8)
andofflineindexconstruction(i.e.,therighthalf). buildingfordatasetsuptomillion-scalevectorsandhour-level
constructionforbillion-scaledatasets.
Onlineserving.Weemployall-flashserversasANNSserv-
ingnodeswhereeachisequippedwith12×2TBPCIeGen5 Inofflineconstruction, 1 multi-GPUserversrunk-means
|     |     |     |     |     |     |     | to generate |     | initial centroids | from | the raw | dataset and | save |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ----------------- | ---- | ------- | ----------- | ---- |
NVMeSSDs,12×96GBDDR5DRAM,anda96-coreCPU.
Recall that existing solutions such as SPANN fall short in thesecentroidstothedistributedstorage. 2 Then,owning
throughput due to bandwidth utilization and pruning effi- initialcentroids,localCPUsofmulti-GPUserversorelastic
CPUworkerssplitandrebalanceclustersfromtheinitialcen-
ciency.Wethereforeredesignthestoragestackandtheprun-
ingmodule.ThekeyideaiseliminatingoverheadfromI/O troids,padclusterboundaries,andwriteintermediateindex
|     |     |     |     |     |     |     | shardstotheglobaldistributedfilesystem. |     |     |     |     | 3 Multi-core |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------- | --- | --- | --- | --- | ------------ | --- |
softwareandintroducingadaptivelearning-basedmodels.At
ahighlevel,foreachindexreleasedtoserving,weuseDRAM CPUserversmergetheshards,buildthegraphforallfinalcen-
tostorethecentroidgraphforlocatingnearestclustersand troids,trainlevelingpruningmodels,andfinallymaterialize
theindexfilesforreleasingthemonservingnodes.
weightsofthesearchpruningmodule(routerandpruning).
Meanwhile, the cluster lists are striped across raw NVMe Designadvantages.Withthesedesigns,HELMSMANeffec-
SSDsasthegranularityoflogicalblocks,bypassingthetradi- tivelysolvestheaforementionedchallenges.First,as 4 and
tionalLinuxsoftwarestack.Sinceasinglenodecanusually 5 oftheonlineservingintheleftofFigure8,itbypasses
hostmultiplevectorindexes,weuseanextraSSDtostorethe thekernelonthethroughput-criticalI/Opath(i.e.,cluster-list
metadataofallindexesandmanagementofrawSSDs. reads)completelytoexploitthehighbandwidthofmodern
For each query with target top-k, 1 the router model multi-SSDarrays,minimizingsoftwareoverheadbydirectly
decides the nprobe value, 2 then HELMSMAN uses the steeringNVMeSSDstomatchANNSaccesspatterns(§4.2).
centroidsgraphindextolocatethenprobeclosestcentroids, Second, as 1 , 2 , and 3 of the online serving, it
and 3 the leveling pruning model routed at the first step adaptively chooses the search range (i.e., probed clusters)
furtherprunesthecandidateclusters. 4 Thesearchthreads onaper-querybasis,achievingtargetrecallwhileavoiding
submitasynchronousNVMeI/Ocommandsfortheselected unnecessary I/O and computation: a trained router model
cluster lists, 5 poll completions of cluster reads on the predicts the recall-sufficient nprobe, and leveling pruning
hardware completion queue, and 6 calculate the loaded modelsfurthereliminateunnecessaryscans(§4.3).
vectorsinthelocalthreadordispatchthemtothecalculate Third,as 1 and 2 ofthe offline building,to support
threadpooltocomputedistancesandfinallyrankthetop-k frequent index building for incremental embedding model
nearestneighborsastheresultofANNS.
trainingandcontinuouslyevolvingvectordata,weutilizehet-
Offlineindexconstruction.Tofacilitatefrequentindexbuild- erogeneousaccelerationandmakesupportforelasticscaling.
ing,HELMSMANemploysmulti-GPUserverstoformathree- Multi-GPUserversacceleratecentroidgenerationonlarge-
1628    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

58.5% 58.4% 58.9% 58.8%
(a)I/ObreakdownofSPANN. (b)IdealIOPSpercore.
Figure9:SPANN’sI/OpathreliesonthetraditionalLinux
I/Osoftwarestack,includingAK(application-kernelswitch-
ing),FS(filesystem),BLK(blocklayer),DM(devicemapper
forRAID),andND(NVMedriver).Byissuingfixed-size12
KBreadsinbatches—anewbatchonlyafterthepreviousone
completes—weshowtheI/ObreakdownofSPANN,andcom-
paretheperformanceoflibaio,io_uring,andSPDK.
scaledatasetsandwecandynamicallyallocateCPUstospeed
upthefollowingfine-grainedindexconstructionflexiblyac-
cordingtorequirements(§4.4).
4.2 ANNS-orientedStorageStack
Tobetterservetheclustering-basedANNSindexes,westudy
the existing storage stack and propose an ANNS-oriented
storage design. We start by analyzing the I/O behavior of
clustering-basedsearchandthendiscussthecorresponding
designchoiceswhichtakeadvantageofmultipleNVMeSSDs
withthehelpoftheuser-spaceSPDKdriver[14].
UnderstandingI/Opatterns.Clustering-basedANNShas
twooutstandingI/Opatternsduringonlinesearch.First,the
searchprocesstendstogeneratealargenumberofbatched
reads.Forexample,asinglequerycangenerateupto∼103
cluster-list loading requests when searching the top-3,000
nearestneighbors,atypicalcaseinonlinesearchandadver-
tising. Suchmassivereadscanleadtoademandinglyhigh
IOPSrequirement.TakingSIFT100Masanexample,undera
10mslatencySLA,computation(e.g.,findingthenearestcen-
troids,distancecalculationsonvectorsloaded,andranking
top-k results)canalreadycost∼2-4mswithonly∼6-8ms
leftforI/Os,whichinreturntranslatesto∼120-170KIOPS
persearch thread on a single core. However,the I/O stack
usedinSPANNcanoftenonlyachieve∼30-40KIOPS.
Second,theclustersofanindexhavethesamesizewhich
isalsothesizeoftheissuedreads.Thisisbecause,toavoid
long-taillatencyandtheboundaryerrorduringsearch[17],
the clustering-based index usually balances clusters’ sizes
belowathresholdandpadsclusterswithboundaryvectorsto
thesamesize(e.g.,12KBperclusterforSIFTinSPANN).
Asaresult,eachclustercanhavesamecountofpages,and
eachprobetypicallyissuesfixed-sizereads(e.g.,12KBfrom
three4KBpages)whenloadingthenearestclusters.
Exploringdesignchoices.WenextprofiletheI/Ooverhead
tsoH
eciveD
I/O Commands
Runtime Data 1 Batched Enqueue
ClusterMaps,Weights,
Centroids_Indexes CQs/SQs 2Single Knock
…
Meta Data Files
Do…orbell Do
…
orbell Do
…
orbell
Index_name, Index … … …
(C M lu o s d t e e l r s… ) , : ( C S e S n D tr , o L i b d a s ), Chunk L L b b …a a : : n n +1 L L b b …a a : : n n +1 Cl
L
u
i
s
s
t
t
e r L L b b a a : : n n +1
… … Lb…a: n+2
Chunk Allocator
SATA SSD NVMe SSD 0 SSD 1 SSD 11
Figure10:Metadataasfiles,clusters’listsasrawblocks.
ofSPANN(Figure9a)andthreepopularI/Ostacksincluding
libaio,io_uring,andSPDK(Figure9b)underworkloads
ofbatchedandfixed-sizereadpatterns(i.e.,thesameI/Obe-
haviorastheclustering-basedsearch)asshowninFigure9.
ResultsindicatethattheoverheadofthetraditionalI/Ostack
withlibaiodominatestheend-to-endpath(upto58%ofthe
total)acrossalltop-ksettings,evenexceedingthatofaccess-
ing the SSD (i.e.,PD,physical devices). io_uring shows
moderateimprovementsoverlibaiosinceitdoesnothave
systemcalls[25].SPDKachievesthehighestIOPSbybypass-
ing the traditionalkernelstackcompletely. Note thatthese
throughput numbers are all measured without considering
thecomputationcostinFigure9b.Giventhatio_uringand
libaiohavealreadyfailedtomeettheexpectedIOPS,we
thereforechoosetobuildourservingstorageoverSPDK.
Customizingthestoragestack.AdoptingSPDKmeansdrop-
pingthesupportfromthekernel,andwehenceneedtoman-
agethedatalayoutofindexes,theI/Ocontrolofrawdevices,
andthemulti-devicespaceallocation. Wedemonstrateour
servingstoragestack,asshownin Figure10.
• Datalayout.Theindexdataconsistsofmetadataandclus-
terlists. Metadataincludestheindexname,mappingsof
eachclusteranditsphysicallocation(SSDidandLBA),
pruningmodels,andthecentroidindex.Sincethesestruc-
turesaresmallandcanresideinmemorywithoutexternal
readsatruntime,wesimplystorethemasregularfileson
alocalSSD.Incontrast,theefficiency-criticalclusterlists
areplaceddirectlyonthelogicalblocksoftheNVMeSSD
array.Eachclusterlistoccupiesacontiguousblockrange
ofasingleSSD(e.g.,aclusterlistusesthreeconsecutive
LBAsofSSD11inFigure10),sothatreadingonecluster
onlyrequiresasingleI/Ocommand,avoidingmultipleI/Os
duetocrossingdevicesorblocks.
• I/Ocontrol.FortheonlyruntimeexternalI/O–loadingclus-
terlists–webypasssystemcallsanddirectlysubmitNVMe
commandstohardwarequeueswhilepollingforcomple-
tions.Withthisdirectcontrolofdevices,weoptimizesub-
mission at hardware granularity. I/O commands are en-
queued to host-side NVMe queues in batches,and each
NVMedeviceisnotifiedwithasinglePCIedoorbellknock
perbatch.Thiseliminateshundredsofper-commandPCIe
round-trips(atthemicrosecondscale)andsignificantlyre-
ducesCPUoverheadonthecriticalreadpath.
• Spaceallocation.Sinceallclustersarepaddedtoafixed
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1629

|     |     |     |     |     |     |     |     | Vector |     | top |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- |
size,wecanpre-allocatecluster-alignedregionsonSSDs,
avoidingfragmentationandcomplexfile-systemallocators. [d ,d ,…,d ,d ,k]  Features
|                                                  |     |     |     |     |     |     | 0   | 1   | n-1 n |     |         |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | ------- |
| Hence,onrawNVMedevices,weexploitthispropertywith |     |     |     |     |     |     |     |     |       |     | Router  |
1 Find Max Range
| aunifiedchunk-basedfree-listallocator(e.g.,64MBper |     |     |     |     |     |     |     |     |     |     | Model |
| -------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- |
chunk)thatmanagesSSDspaceforallindexes.Itallocates
|     |     |     |     |     |     | L0:64 | …   | L3:256  | …   | L15:1024 | Labels |
| --- | --- | --- | --- | --- | --- | ----- | --- | ------- | --- | -------- | ------ |
andrecyclesfixed-sizeregionsfordeployinganddeleting
indexesatthechunkgranularity.Eachindexthenpartitions
2 Search top-256 nearest centroids
| itschunksintoconsecutiveblockrangessizedtoacluster |     |     |     |     | Centroids |     |     |     |     |     |     |
| -------------------------------------------------- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- |
listandassignseachrangetoasinglecluster. Graph Vector topCentroids Distribution
Index
|     |     |     |     |     |     | [d  | ,…,d | ,k,c ,c | /c ,,…, c | /c  | ]  Features |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------- | --------- | --- | ----------- |
|     |     |     |     |     |     |     | 0 n  | 0 1     | 0         | 255 | 0           |
4.3 Leveling-learnedSearchPruning
|     |     |     |     |     |     |     | Prune   |     |     |     | Pruning |
| --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | ------- |
|     |     |     |     |     | L0  | …   | 3       | L3  | …   |     |         |
|     |     |     |     |     |     |     | Range   |     |     | L15 | Models  |
Problemandpurpose.Inclustering-basedsearch,thenum-
|               |                 |                    |        |     | nprobe:193 |     | nprobe:203 |     |     | nprobe:256 | Labels |
| ------------- | --------------- | ------------------ | ------ | --- | ---------- | --- | ---------- | --- | --- | ---------- | ------ |
| ber of probed | clusters (i.e., | nprobe) determines | recall | and |            |     |            |     |     |            |        |
nprobe
performance. The trade-off is that an overly large Figure11:Pruningworkflowofsearchduringonlineserving.
significantlyincreasestheI/Oandcomputationcostdueto
redundantscans,whileanoverlysmallnprobehurtsrecall.
Adapting nprobe by pruning. Many prior works such as Online-offlineworkflow.Indetail,wefirstpresenttheprun-
Quake[43],Auncel[64],andLAET[36]proposeearlyter-
ingprocessofsearchinonlineservingandthendescribehow
minationinpruning,whichseemssuitableforouradaptive themodelsaretrainedinofflinebuilding.
adjustmentofnprobe.However,theyinfactcannotbeapplied
• Onlineservingworkflow.AsshowninFigure11,wefirst
toourscenarioduetothelackofsupportforchangingtop-k
feedthequeryvectoranditsrequestedtop-kintotherouter
ofrequestsandthestrongdependenceonintermediateresults.
model,whichpredictsacoarsemaximumsearchrange’s
First,existingmethodstypicallymakeearly-terminationrules
level(e.g.,level3with256asnprobehere,L3:256)asthe
forafixedtop-kwhilevaryingtargetrecall.Incontrast,inour
|     |     |     |     |     | upper bound | of  | nprobe. | Then | the centroids |     | graph index |
| --- | --- | --- | --- | --- | ----------- | --- | ------- | ---- | ------------- | --- | ----------- |
services,therecalltargetcanbepredeterminedfromscenarios
|     |     |     |     |     | returns the | top-nprobe |     | nearest | centroids. | Finally, | LLSP |
| --- | --- | --- | --- | --- | ----------- | ---------- | --- | ------- | ---------- | -------- | ---- |
(e.g.,90%inonlinesearch)buttop-kcanvaryacrossrequests
constructspruningfeaturesfromthequery,top-k,andthe
(e.g.,100-3,000inonlinesearch).
centroid–distancedistribution(thenearestcentroid-query
| Second,LAET | also relies | on intermediate | features | such |     |     |     |     |     |     |     |
| ----------- | ----------- | --------------- | -------- | ---- | --- | --- | --- | --- | --- | --- | --- |
distanceandrelativeratiosofthefollowing255centroids’
| as the distances | to the current1stand10thneighbors |     |     | after |     |     |     |     |     |     |     |
| ---------------- | --------------------------------- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
tothe1stcentroid’s),andappliesthecorrespondinglevel-
| probing a | subset of the | nearest candidate | clusters | located. |     |     |     |     |     |     |     |
| --------- | ------------- | ----------------- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- |
specific(i.e.,level3here)pruningmodeltorefinenprobe
Similarly,QuakeandAuncelneedtocheckaftereachnewly
forbatchedloadingnonredundantclustersfromSSDs.
scannedclusterwhethertherecalltargetismet.Suchitera-
|     |     |     |     |     | • Offline training |     | workflow. | We  | first | set a series | of range |
| --- | --- | --- | --- | --- | ------------------ | --- | --------- | --- | ----- | ------------ | -------- |
tiveprobe–compute–decideloopsserializeclusterI/Os,and
levelswithincreasingupperboundsonnprobe(e.g.,64to
thusareunfriendlytothebatchedSSDreadsforclusterlists,
1,024withastepof64).Fromarecenttimewindow(e.g.,
leadingtoreducedbandwidthutilization.
theprevious1dayforsearch,1hourforrecommendation
Leveling-learnedsearchpruning.Weproposetheleveling-
andads),weuniformlysampleabout1%ofloggeditemsas
| learnedsearchpruning(LLSP)basedon |     |     | gradientboosting |     |     |     |     |     |     |     |     |
| --------------------------------- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- |
thetrainingsupervision.Thisisbecausemostproduction
decisiontrees(GBDT)2[19,32].First,toaddressvaryingtop-
tracesshowupto90%duplicationinshortwindows[15,
kvalues,LLSPhasaroutermodelforchoosingthemaximum
53,54].Toavoidtheoverheadofbrute-forcegroundtruth,
| range according | to the | different search difficulty |     | (i.e., the |     |     |     |     |     |     |     |
| --------------- | ------ | --------------------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
weapproximatelabelsbyrunningnon-pruningsearchwith
distributionofqueryvectorandthetop-kvalue)ofrequests.
alargenprobe(e.g.,4,096).Wethentraintheroutermodel
Second,ithasagroupofmulti-levellearning-basedmodels
bytheprocedurethat,foreachqueryandbusiness-required
forpruningredundantscans.Atthisstage,tokeepbatched
|     |     |     |     |     | top-k, finding | the | smallest | level | whose | range | meets the |
| --- | --- | --- | --- | --- | -------------- | --- | -------- | ----- | ----- | ----- | --------- |
clusterreads,weavoidusingintermediatesearchresultsas
targetrecallandusingthepair(query,top-k)asfeaturesand
| features, | and instead use | only pre-search | information: | the |     |     |     |     |     |     |     |
| --------- | --------------- | --------------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
thelevelaslabel.Afterward,withineachlevel,wederive
queryvector,thetop-kvalue,andstatisticsofitsdistancesto
labelsfortrainingpruningmodelsbygraduallydecreasing
allnearestcandidatecentroids3.
nprobefromthelevel’smaximumuntilrecalldropstothe
threshold;theresultingnprobeistakenasthelabel.And
2GBDTisaneffectivearchitectureforpruningofonlinesearchbecause
ofitsfasttraining(e.g.,minute-leveloverheadfor1millionentries),low- thequery,top-k,andcentroid-distancedistributionsunder
overheadinference(e.g.,∼10-30usperprediction),andsmallmemoryfoot- the maximum nprobe form the feature vectors together.
print(e.g.,onlyhundredsofKBpermodel).
Withthelabels(i.e.,actualnprobeminimized)andthese
3Feature-importanceanalysisshowsqueryvectorsandcentroid-distance
features,wetrainthepruningmodelofeachlevel.
ratioscancontributenearly50–70%ofpredictivepower[36].
1630    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Minute Raw …Coarse …Balanced Post
To Dataset Clusters Clusters Lists
Hour
Builds Centroids
e.g., ≤0.1B … Local CPU Cores Multi- Index
GPUs … Core
Daily Elastic Workers Server Index
Meta
Builds
e.g., >0.1B Raw …Coarse …Balanced Pruning
Dataset Clusters Clusters Model
Figure12:Pipelinesofthethree-stepindexconstruction. Figure13:ThespeedupratioofGPUclusteringacrossvary-
ingvectorcountswithanNVIDIAL20vs.48CPUcores.
4.4 GPU-acceleratedandElasticBuilding
threshold(e.g.,105bydefault).WethenuseCPUstoperform
Toreducetheindexconstructiontimeformillion-tobillion- fine-grainedsplittingandredundantpaddingofboundaryvec-
scaledatasetsfromdaystotensofminutes,weleverageGPU- tors.Dependingontheapplicationscenarioanddatasetscale,
basedaccelerationandfurtherdesignanelasticpipelineto weadopttwoexecutionschemes.
scalethecomputationfromadistributedCPUpool. Forminute-to-hourbuildsofcommon-scaledatasets(e.g.,
Procedureandissuesofexistingindexconstruction.Again, <0.1Bvectorsfromrecommendationandadvertising),we
wefirstexaminethestatusquo(i.e.,theindexconstructionin employlocalCPUcorestoimmediatelyfinishthefinesplit-
SPANN).Therearethreesteps.First,itapplieshierarchical tingandduplicationwithRNGchecking,avoidingnetwork
k-meanstopartitionvectorsintomanysize-boundedclusters, transfersandextraschedulingoverhead.
avoidingoversizeandunbalancedpartitions.Then,itperforms For search services that require daily rebuilds on larger
closure multi-cluster assignment that duplicates boundary corpora,elasticworkersinonlineCPUclustersperformthe
vectors,using RNG rules [52] to controlredundantcopies. fine-grained clustering and padding during off-peak hours,
Finally,itbuildsanin-DRAMgraphonthecentroidsofall opportunisticallyharvestingidleresourcesfromexistingclus-
clustersforlocatingthenearestclusterstothequeryduring tersunderdiurnalloadpatterns(i.e.,lighterutilizationatnight
onlineserving. andheavierloadsduringtheday).
We can see that there are two main drawbacks in the Inaddition,toavoidimpactingreal-timeservices,ween-
firstclusteringstep,whichincursthemainoverhead(upto forceaQoSpolicy:wheneveronlineandofflinejobscontend
∼60-80%)ofexistingconstructions.First,k-meansonlarge- forresources,onlinetrafficalwayshaspriorityandtheindex-
scaledatasetsincursrepeateddistancecalculationsonhigh- buildingtaskonthatnodeispreemptedandterminated,and
dimensionalvectors andthusplacesa heavyloadwhichis wouldretrylater.Tocontroltheresultingtaillatency,wefur-
beyond the capability of a CPU. Second,when vectors in- ther introduce task re-assignment and node eviction: once
creasetobillionsfrommillions,itstillrequiresmultiplehours a taskexceeds a retrythreshold,itis reassignedto another
ofbuilding,requiringparallelingabout102-103×resources
node,andtheoriginalnodeistemporarilyremovedfromthe
as data scaling. However,the currentSPANN construction resourcepool,preventingafewunstablenodesfromdominat-
canonlyuseoneCPUinbuildingandthustakesdaystofin- ingtheoverallconstructiontime.
ishbuildingabillion-scaleindex,whichisunacceptablefor Buildingfinalindexdata.Finally,balancedandreplicated
productionservices. clustersgeneratedbybothlocalCPUsofGPUserversand
GPU acceleration and elastic scaling. Hence,we exploit elastic CPU workers are uniformly prepared for releasing.
GPUstoacceleratecentroidinitializationanditerativebalanc- Theyareconsolidatedonthemulti-coreserverstoproduce
ing,andemploytheelasticCPUpooltoaddressthescaling deployableindexfiles,includingpostinglists,centroidindex,
ofdatasets. Figure12showstheworkflowofourthree-step metadata,andthepruningmodel.
indexconstructionpipeline.
GeneratingcoarsecentroidswithGPUs.First,fordatasets
5 Evaluation
ofallscales,weuseGPUstoperformcoarseclustering.In
thisstep,wedonotdirectlysplitclustersdowntotheirfinal
Inthissection,weconductextensiveexperimentstoevaluate
size,becausewefoundthatGPUaccelerationisnotalways
effective4.AsshowninFigure13,GPUsprovideuptoorders- thepracticalimpactsofHELMSMAN,summarizedasfollows:
of-magnitudespeedupsonmulti-million–scaleandmorevec-
• HELMSMANachieves2-16×throughputofbaselines,and
tors,whileforsmalljobs(e.g.,clusteringon<105 128-dim canmeetlatencySLAstoreplacein-DRAMHNSW(§5.2).
vectors),extrahost–devicetransferscandominate,making
• HELMSMANachieves1.6-7.5×SSDbandwidthutilization
ofotherDRAM-SSDsystems,yieldingupto87%improve-
GPUsslowerthantheCPUs.
mentbysimplyupgradingSSDs(§5.3).
Constructingbalancedpostinglists.Aftertheearlycluster-
ingphaseonGPUs,mostclustersarealreadysmallerthanthe
• Underthesameaveragerecall,HELMSMANensuresthat
>80%ofqueriesindividuallymeetthetargetrecallbynear
4Atpresent,thedevelopmentourGPUK-meansisbasedonFaiss. 30percentagepointsoverSPANN(§5.4).
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1631

|     |     |     |     |     |     | SIFT0.1B         | RedSrch0.5B       |           |     | RedRec0.1B        |
| --- | --- | --- | --- | --- | --- | ---------------- | ----------------- | --------- | --- | ----------------- |
|     |     |     |     |     |     | (top-k:10-3,000) | (top-k:100-3,000) |           |     | (top-k:100-1,000) |
|     |     |     |     |     |     | RedAds20M        |                   | RedCM0.1B |     | RedRAG4M          |
(a)Performanceacrossvarioustop-kofsearch,underrecall=90%. (top-k:100-3,000) (top-k:100-500) (top-k:10-100)
Figure15:Trendsofthroughputandaveragelatency.
matchthehardwarecapacity.Weincludein-DRAMHNSW
|     |     |     |     |     | that is | widely used in | production | for | low-latency | services, |
| --- | --- | --- | --- | --- | ------- | -------------- | ---------- | --- | ----------- | --------- |
(b)Performanceasthetop-10search,undervariousrecallrates.
|     |     |     |     |     | which | serves as a strong | performance |     | reference | forpurely |
| --- | --- | --- | --- | --- | ----- | ------------------ | ----------- | --- | --------- | --------- |
Figure14:Comparisonsaboutthroughput,averageandtail memory-residentdeploymentsbutwithhigherDRAMcost.
latencyunderdifferenttop-kandrecall,usingSIFT100M.
Specifications.AllDRAM–SSDtestsareconductedonour
testbedequippedwiththe96-coreAMDEPYC9654CPU,
• GPUaccelerationenablesconstructing0.1B-vectorindexes 12×96 GB DDR5 DRAM, 12×1.92 TB PCIe-5.0 NVMe
within 1 hour. And by elastically scaling resources,10B SSDs.In-DRAMdistributedHNSWusesourstandardcon-
vectorscanbebuiltwithin10hours(§5.5). figurationwith32-coreCPUsand256GBDDR5DRAMto
| • HELMSMAN | canreduceDRAMusagebyover90%and |     |     |     |     |     |     |     |     |     |
| ---------- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
holdshards,aconfigurationcommonlyadoptedinproduction.
improvethroughput-per-dollarby8.3×fortheservingde-
ployment(§5.6).
5.2 SearchPerformance
5.1 Setup
End-to-endperformance.Overall,HELMSMANachievesthe
bestend-to-endefficiencyacrossawiderangeoftop-kand
| Dataset | Scale | Dim. | Totalsize | Top-kRange |     |     |     |     |     |     |
| ------- | ----- | ---- | --------- | ---------- | --- | --- | --- | --- | --- | --- |
recalltargets,asshowninFigure14.
SIFT 0.1B&10B 128 12GB&1.2TB 10–3,000 Varying top-k (Figure 14a). With recall fixed at 90%,
| RedSrch | 0.5B&10B | 64  | 30GB&0.6TB | 100–3,000 |          |          |             |            |     |             |
| ------- | -------- | --- | ---------- | --------- | -------- | -------- | ----------- | ---------- | --- | ----------- |
|         |          |     |            |           | HELMSMAN | sustains | the highest | throughput |     | on SIFT0.1B |
| RedRec  | 0.1B     | 64  | 6GB        | 100–1,000 |          |          |             |            |     |             |
acrossalltop-kvalues.Astop-kincreasesfrom10to3,000,its
| RedAds | 20M | 128 | 2.5GB | 100–3,000 |     |     |     |     |     |     |
| ------ | --- | --- | ----- | --------- | --- | --- | --- | --- | --- | --- |
RedCM 0.1B 64 6GB 100–500 throughputdegradesmoreslowlythanthatofotherDRAM-
RedRAG 4M 1024 4GB 10–100 SSDsystems,whileaveragelatencystayswithin10msand
|     |     |     |     |     | P99.9 | latency remains | well below | 20  | ms. Forgraph-based |     |
| --- | --- | --- | --- | --- | ----- | --------------- | ---------- | --- | ------------------ | --- |
Table2:Statisticsoftheevaluateddatasets.
baselines(DiskANN,Starling,PipeANN),largertop-kforces
Workloads.WeevaluateonthepublicSIFTandfiveproduc- longer greedy walks due to larger candidate lists. Starling
improvestop-10performanceviaoptimizedlayoutbutisless
| tion datasets,as | shown | in Table | 2. SIFT10B | is createdby |     |     |     |     |     |     |
| ---------------- | ----- | -------- | ---------- | ------------ | --- | --- | --- | --- | --- | --- |
10×replicatingSIFT1B.Realdatasetsspan4M–10Bvectors effectiveforlargetop-k.Thereasonisthat,astop-kincreases,
fromourmainservicesmentioned.Similaritymetricisthe thesearchdepthofgraph-basedsearchgrowssignificantly.
L2distance.ForSIFT,weuniformlygeneratequerytop-kval- Forexample,fortop-1000ontheSIFT0.1B,boththecandi-
uesrangingfrom10to3,000,whileforotherdatasets,top-k date queue length and the number of search hops increase
|     |     |     |     |     | substantially | to around | 1,500 | or more. | The number | of ac- |
| --- | --- | --- | --- | --- | ------------- | --------- | ----- | -------- | ---------- | ------ |
valuesaresampledfromourrealproductiontraces.
Baselines.WecompareHELMSMANwithDiskANN,Starling, cessedSSDpagesalsorisessignificantly,whichleaveslittle
PipeANN,SPANN,andHNSW.ForDRAM-SSDbaselines, roomforgainsfromlayoutreorderingofStarling.Meanwhile,
weusetheirreleasedimplementations.Wetunebeamwidths SPANNisconstrainedbythetraditionalI/Osoftwarestack.
ofgraph-basedsystems (16 forDiskANN andStarling,32 Consequently,boththroughputandlatencyforbaselinesdete-
| for PipeANN, | unless | otherwise | specified) | to achieve their | rioraterapidly. |     |     |     |     |     |
| ------------ | ------ | --------- | ---------- | ---------------- | --------------- | --- | --- | --- | --- | --- |
optimalperformance,sincemulti-SSDsetupsoffersufficient Varyingrecall(Figure14b). Fixingtop-k at10,HELMS-
bandwidth.WesetDRAMbudgetas25%ofthesizeofraw MANdeliverscompetitivethroughputat90-96%recalland
datasets[22].ForHELMSMANandSPANN,wereducethe keepsclearadvantageswhenrecallentersthehigh-accuracy
replicationfactorto4,withcentroidsaccountingfor8%of regime.Bothaverageandtaillatencygrowsmoothlywiththe
thetotalscale,therebysettingtheDRAM:SSDratioto1:20to recall,andHELMSMANmaintainssub-10msaveragelatency
1632    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|     |                  | SIFT0.1B |     | RedSrch0.5B       | RedRec0.1B        |     |     |     |     |     |
| --- | ---------------- | -------- | --- | ----------------- | ----------------- | --- | --- | --- | --- | --- |
|     | (top-k:10-3,000) |          |     | (top-k:100-3,000) | (top-k:100-1,000) |     |     |     |     |     |
RedAds20M RedCM0.1B RedRAG4M (a)I/OBandwidthutilizationon(b)Improvementsbyupgrading
|     | (top-k:100-3,000) |     |     | (top-k:100-500) | (top-k:10-100) |                          |     |                             |     |     |
| --- | ----------------- | --- | --- | --------------- | -------------- | ------------------------ | --- | --------------------------- | --- | --- |
|     |                   |     |     |                 |                | PCIe-4.0andPCIe-5.0SSDs. |     | SSDsfromPCIe-4.0toPCIe-5.0. |     |     |
Figure18:ImpactsofdifferentgenerationsofNVMeSSDs.
Figure16:TrendsofthroughputandP999taillatency.
|     |     |     |     |     |     |     |     | B5.0hcrSdeR B1.0ceRdeR | M02sdAdeR | M4GARdeR |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- | --------- | -------- |
B1.0MCdeR
B1.0TFIS
Avg.LatencySLA
|     | SIFT0.1B |     | RedSrch0.5B |     | SIFT10B  |     |     |     |     |     |
| --- | -------- | --- | ----------- | --- | -------- | --- | --- | --- | --- | --- |
(10 shards vs. 1 node)
Figure19:Performancespeedupbythepruningmodule.
5.3 StorageI/OImpact
|     | RedRec0.1B |     | RedAds20M |     | RedSrch10B  |     |     |     |     |     |
| --- | ---------- | --- | --------- | --- | ----------- | --- | --- | --- | --- | --- |
(10 shards vs. 1 node)
|     |     |     |     |     |     | Bandwidth | utilization. | As shown      | in Figure   | 18a, on Red- |
| --- | --- | --- | --- | --- | --- | --------- | ------------ | ------------- | ----------- | ------------ |
|     |     |     |     |     |     | Srch0.5B, | we measure   | the bandwidth | utilization | of a 12-     |
SSDarraywithbothPCIe-4.0[11]andPCIe-5.0drives[12].
Figure17:Comparisonwithin-DRAMHNSWdeployments.
Graph-basedsystemsutilizelessthan20%ofSSDbandwidth,
|     |     |     |     |     |     | while clustering-based |     | SPANN | also merely reaches | about |
| --- | --- | --- | --- | --- | --- | ---------------------- | --- | ----- | ------------------- | ----- |
andthelowestP99.9latencyacrosstheentirerecallrange. 55%(Gen4).Incontrast,HELMSMANpushesutilizationto
Throughputvs.latency.Weevaluateworkloadsfromgener- ∼85%onGen4and∼70%onGen5,showingthatitsbatched,
device-directI/Opathismuchclosertothedevicelimits.
atedSIFTandproductionswithservice-specifictop-kanda
Gainsfromhardwareupgrades.InFigure18b,wethenre-
90%recalltarget,rampingthreadsuntilallsystemssaturate.
portthroughputgainswhenupgradingSSDsfromPCIe4.0to
| Throughputvs. |     | average |     | latency. As | shown in Figure 15, |     |     |     |     |     |
| ------------- | --- | ------- | --- | ----------- | ------------------- | --- | --- | --- | --- | --- |
5.0on64-dimRedSrch,128-dimRedAds,and1024-dimRe-
graph-basedsystemscanincur∼120msaveragelatencyat
dRAGworkloads.Graph-basedsystems(DiskANN,Starling,
| only0.5-3KQPSbecauselargetop-k |     |     |     | requireslonggreedy |     |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- |
andPipeANN)improvebyonly10-30%,andSPANNbyup
walksforlongerlengthofcandidatelists(e.g.,4,000fortop-
to40%,indicatingtheyarelargelyI/O-latency-orsoftware-
| 3,000). | SPANN | benefits | from | high-bandwidth | SSDs, and |     |     |     |     |     |
| ------- | ----- | -------- | ---- | -------------- | --------- | --- | --- | --- | --- | --- |
stack-bound.Incontrast,HELMSMANgainsabout55%at64-
HELMSMANfurtherpushesthefrontier,achievingupto30×
and128-Dand87%at1024-D,demonstratingthatitsperfor-
throughputwhilekeepingaveragelatencywithin5-10ms.
mancescalesmoreefficientlywithavailablebandwidth.
Throughputvs.taillatency.ForP99.9latency(Figure16),
| graph-based |     | systems | and SPANN | exhibit | steep tail blow- |     |     |     |     |     |
| ----------- | --- | ------- | --------- | ------- | ---------------- | --- | --- | --- | --- | --- |
5.4 PruningEfficiency
upsoncesaturated.Byclustering-basedsearchandourcus-
tomizedI/Ostack,HELMSMANmaintainsuptoanorder-of-
ForthepublicSIFTdataset,werandomlysample1Mvectors
magnitudelowerP99.9latency,keepingitaround∼10ms. asthetrainingsetanduse10%ofthemasqueries;forpro-
Comparisons with in-DRAM deployments. Figure 17 ductiondatasets,weextract110Kconsecutivequeriesfrom
shows results. When HNSW fits in the same 96-core node onlinelogs,usethefirst100Kasthetrainingset,andreserve
(20M–0.5Bdatasets),HELMSMANachievesabout25–70% thelast10Kasqueries,consistentwithourproductionsce-
ofthethroughputofin-DRAMHNSWdeploymentsat90% nario.Bydefault,wesetthenumberofiterationsto500and
recall,whilealwayssatisfyingtheaverage-latencySLAs.For thelearningrateto0.2.
the10B-scaleSIFTandRedSrch,theproductionHNSWuses Performance gains. Our pruning module consistently ac-
10shardswithatotalof2.5TBDRAMand320CPUcores celerates search across all datasets,as shown in Figure 19.
(standard32-core,256-GBnodes).Incontrast,HELMSMAN Comparedwiththenon-pruningbaseline,ityields1.1–1.6×
reachesroughly47-85%oftheirthroughputunderthesame throughput,andstillprovides5–25%higherthroughputthan
SLAusingasingle96-coremachinewithonly160–330GB thefixedpruningpolicy.Thebenefitismostpronouncedon
ofDRAM.HELMSMANmeetsSLAswithmodestlyhigher RedRAG4M because its workloads use small top-k values
latency,butreducesCPUusagebyabout3–4×andDRAM (i.e.,10–100),wheretheoptimalsearchrange(i.e.,nprobe)
consumptionbynearlyanorderofmagnitude. tendstofluctuatemore,leadingtomoreredundantscans.
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1633

5.5 ConstructionEvaluation
|     |     |     |     | B5.0hcrSdeR | B1.0ceRdeR |     |     |     |     |     |     |     |
| --- | --- | --- | --- | ----------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
B1.0TFIS
|     |     |     |     |     |     | GPU acceleration. |     | On  | a single | 192-core | node,CPU-only |     |
| --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | -------- | -------- | ------------- | --- |
constructionof0.1B-scaleindexestakesabout9–12hours.
|     |     |           |     |           |          | Offloading | the | coarse clustering |     | stage to | 4 NVIDIA | L20 |
| --- | --- | --------- | --- | --------- | -------- | ---------- | --- | ----------------- | --- | -------- | -------- | --- |
|     |     | M02sdAdeR |     | B1.0MCdeR | M4GARdeR |            |     |                   |     |          |          |     |
GPUsreducesthetotalbuildtimetowithinanhour,asshown
|     |     |     |     |     |     | in Figure | 21a (up | to ∼10× | speedup), | transforming |     | hours- |
| --- | --- | --- | --- | --- | --- | --------- | ------- | ------- | --------- | ------------ | --- | ------ |
longofflinejobsintominute-levelbuildsforhigh-freshness
services(e.g.,recommendationandadvertising).
|     |     |     |     |     |     | Elastic | scaling. | For 10B-scale |     | datasets, | using GPUs | for |
| --- | --- | --- | --- | --- | --- | ------- | -------- | ------------- | --- | --------- | ---------- | --- |
Figure20:Searchqualityimprovedbythepruningmodule.
coarseclusteringandsingle-nodemergingforfinalindexes
(i.e.,Coarse&Merge),wefurtherparallelizethefine-grained
balancingstage(i.e.,Fine)acrossanelasticCPUcluster.In-
creasingthenumberofCPUworkersfrom1,024to104cores
reducesend-to-endbuildingtimefromover16hourstoabout
4–7hours,asshowninFigure21b,enablinghours-levelre-
constructionofbillion-scaleindexes.
| (a)Comparisonofsinglenode. |     |     | (b)Speedupfromelasticscaling. |     |     |     |     |     |     |     |     |     |
| -------------------------- | --- | --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
5.6 CostEfficiency
Figure21:AccelerationofGPUsanddistribution.
|     |     |     |     |     |     |     | DRAM | Gen5SSD |     | Throughput | StorageEff. |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------- | --- | ---------- | ----------- | --- |
System
Accuracygains.AsshowninFigure20,LLSPalsoleadsto (GB,$) (GB,$) (KQPS) (QPS/$)
amorestablesearchqualityunderthesameaveragerecall.
|     |     |     |     |     |     | HNSW | 123,1K |     | N/A | 51  |     | 51  |
| --- | --- | --- | --- | --- | --- | ---- | ------ | --- | --- | --- | --- | --- |
Incontrasttothefixedpolicy,whichfailstomeetthetarget
|     |     |     |     |     |     | PipeANN | 8,64 | 260,52 |     | 0.8 |     | 7   |
| --- | --- | --- | --- | --- | --- | ------- | ---- | ------ | --- | --- | --- | --- |
recallforover40%ofqueries,ourmethodensuresthatover SPANN 8,64 162,32 8.4 88
80%ofqueriesmeetthetargetrecall(i.e.,90%),effectively Ours 8,64 162,32 24 250
reducinglow-recalloutliersacrossallsixdatasets.
Table4:ComparisonofcostefficiencyonRedSrch0.5B.
Dataset Model FeatureImportance DRAM Gen5SSD Throughput StorageEff.
System
|     |        |     |                    |     |     |     | (TB,$) | (TB,$) |     | (KQPS) | (QPS/$) |     |
| --- | ------ | --- | ------------------ | --- | --- | --- | ------ | ------ | --- | ------ | ------- | --- |
|     | Router |     | Query:67.3%k:32.7% |     |     |     |        |        |     |        |         |     |
RedSrch
Pruning Query:34.3%k:15.2%Centroids:50.5% HNSW 2.5,20K N/A 23 1.2
|     | Router |     | Query:74.1%k:25.9% |     |     | Ours | 0.16,1.3K | 3.2,0.6K |     | 19  |     | 10  |
| --- | ------ | --- | ------------------ | --- | --- | ---- | --------- | -------- | --- | --- | --- | --- |
RedRAG
Pruning Query:48.3%k:7.8%Centroids:43.9% Table5:ComparisonofcostefficiencyonRedSrch10B.
Table3:Featureimportanceofleveling-learnedpruning.
|     |     |     |     |     |     |     | CloudPrice |     |     | BuildTime | OfflineCost |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --------- | ----------- | --- |
System
|         |             |     |         |                     |     |      | (norm.price/hour) |           |     | (hour) | (norm.cost) |     |
| ------- | ----------- | --- | ------- | ------------------- | --- | ---- | ----------------- | --------- | --- | ------ | ----------- | --- |
|         |             |     |         |                     |     | HNSW |                   | 1(96Core) |     | 1.5    |             | 1.5 |
| Feature | importance. | We  | further | show the importance | of  |      |                   |           |     |        |             |     |
|         |             |     |         |                     |     | Ours | 1.3(96Core+4GPU)  |           |     | 1.3    |             | 1.7 |
differentfeaturesintheleveling-learnedpruningmodelinTa-
ble3.RedSrch0.5BandRedRAG4Marechosenasrepresen- Table6:ComparisonofconstructioncostonRedSrch0.5B.
tativesofproductiondatasetswithdifferentdimensionsand
top-kranges.RedSrchhasalargertop-krange(100–3,000) Costefficiencyofonlineserving.Wecomparestoragecost
andsmallerdimension(64),whileRedRAGhasasmallertop- and throughput on search workloads to show online serv-
krange(10–100)andlargerdimension(1024).Resultsshow ingcosts.OnRedSrch0.5B(Table4),underproductiontop-
thatthequeryfeatures(e.g.,querycoordinatesanddistances k workloads, PipeANN sustains only 0.8 KQPS, yielding
tocentroidsusedduringpruning)areimportantforbothrouter 7 QPS/$, even lower than in-DRAM HNSW (51 QPS/$).
andpruningmodels,indicatingthatthelocaldistributionof SPANN reaches 88 QPS/$,while HELMSMAN further im-
queriesisakeyfactorfordeterminingthesearchrangeand provesto250QPS/$(5.4×overHNSW,2.9×overSPANN).
pruningratio.Meanwhile,theimportanceoftop-kishigher OnRedSrch10B(Table5),byreplacinga10-shardHNSW
fortheroutermodelthanthepruningmodel,whichisreason- deployment using ∼2.5 TB DRAM with each single node
ablesincetherouterdeterminesthesearchrange(i.e.,nprobe) using32coresand256GBDRAM,HELMSMANboostscost
based on the target top-k,while the pruning model further efficiency from 1.2 to 10 QPS/$ (8.3×) by saving 90% of
prunesclusterswithinthesmallerselectedsearchrange. DRAMusageatanadditionalSSDcostofonly$0.6K.
1634    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Costefficiencyofoffline building. In addition to compar- externalI/Obandwidth,butonlyabout70%canbeutilizedin
ingourofflinebuildingtimewiththeCPU-onlySPANN,we practice.Thebottleneckisthelimitedeffectivememoryband-
also estimate the single-node CPU-GPU construction cost widthofmodern12-channelDDR5servers,typicallyaround
ofHELMSMANandCPU-basedHNSWwedeployedprevi- 300–350GB/s,whichmustserveSSD-to-DRAMtransfers,
oulybycomparingthenormalizedcloudpriceofCPU-only DRAM-to-CPUrereads,andnearest-centroidsearch.Conse-
andCPU-GPUinstances[4].AsshowninTable6,ourGPU- quently,addingmoreSSDsbringslimitedbenefitoncemem-
acceleratedconstructionachievessimilarcostcomparedwith ory bandwidth is saturated,as observed in our early more
CPU-onlyHNSWbuilding,becauseofhigherpriceofGPU SSDs equipments (e.g.,20 Gen5 SSDs experiments). This
instancesbutshorterbuildtime.AndastheGPU-basedclus- imbalanceislikelytoworsenasmodernCPUsexposeenough
teringimplementationisdeveloping[60],weexpectthecost PCIelanes(e.g.,128-160lanes[1])toattachover32Gen5
ofclustering-basedindexes’constructiontofurtherreduce, SSDs, providing external bandwidth beyond what current
makingitmorecost-effective. memory systems can sustain. For the commercially avail-
abledevices,thedirectI/O-to-cachetechniquessuchasIntel
DDIO[6]andAMDSDCI[3]maymitigatethisissue,but
6 Deployment
currentlythesemethodsonlyworkfornetworkdevicesand
theirSSDecosystemremainsimmature.Wethinkthatextend-
6.1 DeploymentStatus
ingsuchsupporttoSSD-basedsystemsmightbeapromising
futuredirection.Atthesametime,recentstudies[27,28,57]
Atthetimeofpublication,HELMSMANhasbeenrollingout
have usedGPUs to overcome the limitations ofCPU com-
as a unified ANN layer in RedNote’s production. We use
putepowerandhostmemorybandwidth,whilealsotaking
HELMSMANtosupportallservices,andall-flashserversare
advantage of the increasingly abundant external I/O band-
graduallyreplacingpreviousin-DRAMdeploymentsacross
width provided by NVMe SSDs. We plan to explore their
search, recommendation, advertising, and other vector ser-
vices in the coming months. Currently,with only ∼40 all- optimizationsinourfuturedeployments.
flash servers-each with 0.7–1.1 TB DRAM and 12 NVMe Largetop-kcanbemoreimportantthanextremelyhigh
SSDs-HELMSMAN already sustains online workloads that recall.Inproductionsearch,recommendation,andadvertis-
previouslyrequiredabout35,000CPUcoresand∼0.35PB ingsystems,first-stageANNSistypicallyusedasacandidate
DRAM in in-DRAM deployments. In the offline construc- generatorratherthanthefinaldecisionmaker.Sincesingle-
tionphase,HELMSMANcanleverageupto10,000CPUcores vectorsimilarityonlyprovidesacompressedsemanticsignal,
fromonlineclustersduringlow-trafficperiods(e.g.,late-night downstreamstagesusuallyapplypost-filteringbasedonscalar
hours)toacceleratelarge-scalebuilds.Lookingforward,Red- attributes,orrescoretheretrievedcandidatesusingricherfea-
Noteplanstomigratethemajorityofin-DRAMdeployments turesandtheoriginalcontent,suchastext,images,andvideos
ontoHELMSMAN,withprojectedinfrastructurecostsavings [21,37,63].Therefore,inourworkloads,retrievingalarge
ontheorderoftensofmillionsofdollarsperyear. candidatepool,e.g.,top-kfrom100to1000ataround90%
recall,isoftenmorevaluablethanpursuingextremelyhighre-
callsuchas98–99.9%forsmalltop-krequests.Thelattercan
6.2 OperationalLessonsandFutureWork
substantiallyincreaseANNSsearchcostbutbringslimited
Performance bottlenecks stem from local hotspots of end-to-endbusinessgain,becausedownstreamstagesmainly
queriesandSSDs’die-levelconflicts.Inmostindexes,the benefitfromhavingenoughvalidanddiversecandidatesto
overalldeploymentremainssmoothandstable.WhenSSD filterandrescore,ratherthanfrommarginalimprovements
bandwidthandCPUutilizationremainunsaturated,latency in the vectorrecall of a small candidate set. This suggests
stays within SLAs and throughput scales with additional thatfutureANNSsystemsshouldbeevaluatednotonlyby
search threads. However, in the early stage of trial opera- recall@10[48],butalsobyperformanceunderlargetop-k,
tion,forafewrecommendationindexes,addingCPUcores whichbettermatchesmulti-stagepipelines.
failedtoincreasethroughput,eventhoughSSDbandwidth In-place updates remain challenging. Dynamic updates
remainedbelow20%.Logreplayshowsthattransientquery are importantforfreshness in vectordata management,es-
burstscantargetthesamenearestclustersandlogicalblocks, pecially to keep up with the near-real-time and streaming
causinginternalchipconflicts[31]andhigh-latencySSDac- training of embedding models. In a typical 0.1B-scale rec-
cesses.Tomitigatethis,weplaceafewredundantcopiesof ommendationworkloadwithhourlyrebuildingand∼25–30
theclusterlistsonNVMeSSDs,whichreducesconflictsand KQPS of search,fully replacing periodic rebuilds with in-
raisesthethroughputceilingby1.5–2×,whileincurringonly placeupdateswouldrequireroughly25–30KOPSofupdates
aminorextraSSDspaceoverhead. (i.e.,insertionsanddeletions)whileconcurrentlyservingon-
Memorybandwidthbecomesthebottleneckbeforeexter- line search. This is beyond the update and search through-
nalI/Obandwidthisfullyutilized.Inourall-flashdeploy- putsofrecentstate-of-the-artlarge-scaledynamicANNSsys-
ment,12 Gen5 SSDs provide roughly 140 GB/s aggregate tems[23,58].Therefore,supportingbothhigh-rateupdates
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation 1635

andhigh-performancesearchremainsachallengingdirection. Acknowledgment
Ourcurrentdeploymentadoptsahybriddesign[24,26,50,55]:
the main SSD-resident index is periodically rebuilt,recent Wethankallanonymousreviewersandourshepherd,Asaf
insertions are maintained in an auxiliary in-memory index Cidon,fortheirvaluablefeedbackandhelpingusimproveour
e.g.,(HNSWandIVF),anddeletionsaretrackedbyatomb- papersignificantly.WealsothankengineersatXiaohongshu
stonebitmap.Queriessearchbothindexes,mergecandidates, Inc.fortheireffortsindeployingHELMSMANinproduction.
andfiltertombstonedvectors.Thispreservesfreshnesswith This work was conducted by Yuchen Huang and Baiteng
modestcomplexity,butstillincursextramemoryusageand MaduringtheirinternshipatRedNoteEngineArchitecture
unavoidablerebuildcosts. Department. Erci Xu is the corresponding author. Yuchen
Huang and Chuliang Weng are supported by the National
NaturalScienceFoundationofChina(GrantNo.62272171).
7 RelatedWork
References
DRAM-SSD ANNS. DRAM–SSD ANNS includes graph-
based systems (e.g., DiskANN [49], Starling [56], Pi- [1] 5th Generation AMD EPYC™ Server CPUs.
peANN[22])andclustering-baseddesigns(e.g.,SPANN[17, https://www.amd.com/en/products/processors/
58]). Thoughgraph-basedschemes are popularforissuing server/epyc/9005-series.html.
fewerI/Osthanclustering-basedsearch,ourfindingsshow
that SSD latency and serial access can make them slower [2] Accelerating Vector Database Perfor-
thanclusteringonmodernSSDswiththenear-DRAMband- mance through Disk-Based Storage.
width[25,34,35],particularlyfortop-kuptothethousandsin https://americas.kioxia.com/en-us/
production[21,37,63].Hence,weintegrateclusteringmeth- business/resources/performance-brief/
odswithhigh-bandwidthNVMeSSDarrays. cm7-vector-db-r6615-performance-brief.html.
PruningforANNS.Quake[43],LAET[36],Auncel[64],
[3] AMD Smart Data Cache Injection. https:
andANSMET[38]studypruningandearlystoppingforin-
//docs.amd.com/api/khub/documents/
DRAM ANNS, where the search can iteratively check in-
gLSrfVtcWNt~1fzExUSiIg/content.
termediateresultsandterminateonceconvergence-likecon-
ditionsaremet.However,suchfine-grained,statefulcontrol [4] AWSEC2Pricing. https://aws-pricing.com/.
conflictswithSSD-friendlybatchedI/Os,whichpreferissuing
largesequentialreadswithoutper-stepfeedback.Therefore, [5] Everything you need to know about xiaohong-
insteadoftheseintermediate-result-basedmethods,wepro- shu. Explainer piece; positions Xiaohongshu as
poseourpruningmoduletrainedonhistoricaltraces,which a lifestyle social commerce platform with 300M+
predictssearchrangeswithoutrelyingonintermediatestates. monthly active users. https://restofworld.org/
Acceleration of index building. CAGRA [46],RAFT [7], 2025/rednote-xiaohongshu-what-to-know/.
ParlayANN[41],andFaiss[30]accelerateANNSindexcon-
[6] Intel Data Direct I/O Technology. https:
structionandclusteringusinghighlyparallelgraphbuilders
//www.intel.com/content/www/us/en/io/
and heterogeneous acceleration. We adapt several of their
data-direct-i-o-technology.html.
techniques(e.g.,GPU-basedk-meansandparallelgraphcon-
struction)inourofflineindex-buildingpipelines.
[7] RAPIDSRAFT:ReusableAcceleratedFunctionsand
ToolsforVectorSearchandMore. https://github.
com/rapidsai/raft.
8 Conclusion
[8] RedNote(XiaohongshuInc). https://rednotes.co/.
OurexperienceatRedNoteshowsthat,underindustrialwork-
[9] Reduce costs with disk-based vector
loadswithlargetop-kqueries,graph-basedANNSonSSDs
search. https://opensearch.org/blog/
suffersfromlong,latency-boundsearchpathsandlosescom-
reduce-cost-with-disk-based-vector-search/.
petitiveness.Incontrast,pairinghigh-bandwidthNVMear-
rays with the clustering-based search allows DRAM–SSD [10] SamsungDDR5Data-centricDRAMMemory. https:
designstoapproachin-DRAMperformance(boththroughput //semiconductor.samsung.com/dram/ddr/ddr5/.
andlatency)whilegreatlyreducinghardwarecost.HELMS-
MANdemonstratesthispathinpractice,combiningacustom [11] Samsung PCIe-Gen4.0 PM9A3 Data-centric NVMe
storagestack,adaptivepruning,andfastelasticconstruction SSD. https://semiconductor.samsung.com/ssd/
todelivercost-effective,high-performanceANNSatscale. datacenter-ssd/pm9a3/.
1636 20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

[12] SamsungPCIe-Gen5.0PM9D3AData-centricNVMe [24] RentongGuo,XiaofanLuan,LongXiang,XiaoYan,Xi-
SSD. https://semiconductor.samsung.com/ssd/ aomengYi,JigaoLuo,QianyaCheng,WeizhiXu,Jiarui
datacenter-ssd/pm9d3a/.
|     |     |     |     |     |     |     | Luo,                       | Frank | Liu, | Zhenshan | Cao, Yanliang     |     | Qiao, Ting |
| --- | --- | --- | --- | --- | --- | --- | -------------------------- | ----- | ---- | -------- | ----------------- | --- | ---------- |
|     |     |     |     |     |     |     | Wang,BoTang,andCharlesXie. |       |      |          | Manu:acloudnative |     |            |
[13] SIFTdataset. http://corpus-texmex.irisa.fr/. vectordatabase managementsystem. Proceedings of
theVLDBEndowment,15,2022.
| [14] StoragePerformanceDevelopmentKit(SPDK). |     |     |     |     |     | https: |     |     |     |     |     |     |     |
| -------------------------------------------- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
//github.com/spdk.
|              |              |     |      |          |      |         | [25] Gabriel | Haas | and | ViktorLeis. | What | Modern  | NVMe      |
| ------------ | ------------ | --- | ---- | -------- | ---- | ------- | ------------ | ---- | --- | ----------- | ---- | ------- | --------- |
|              |              |     |      |          |      |         | Storage      | Can  | Do, | And How     | To   | Exploit | It: High- |
| [15] Mozhdeh | Ariannezhad, |     | Sami | Jullien, | Ming | Li, Min |              |      |     |             |      |         |           |
PerformanceI/OforHigh-PerformanceStorageEngines.
| Fang,Sebastian |     | Schelter,and |     | Maarten | de  | Rijke. Re- |     |     |     |     |     |     |     |
| -------------- | --- | ------------ | --- | ------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
ProceedingsoftheVLDBEndowment,2023.
CANet:ARepeatConsumption-AwareNeuralNetwork
forNextBasketRecommendationinGroceryShopping. [26] YuchenHuang,XiaopengFan,SongYan,andChuliang
| In Proceedings |     | ofthe | 45thInternationalACM |     |     | SIGIR |       |       |     |           |        |        |         |
| -------------- | --- | ----- | -------------------- | --- | --- | ----- | ----- | ----- | --- | --------- | ------ | ------ | ------- |
|                |     |       |                      |     |     |       | Weng. | Neos: | A   | NVMe-GPUs | Direct | Vector | Service |
ConferenceonResearchandDevelopmentinInforma- BufferinUserSpace. InProceedingsofthe40thIEEE
tionRetrieval,SIGIR,2022. InternationalConferenceonDataEngineering,ICDE,
2024.
| [16] Grant | Ayers, | Jung | Ho Ahn, | Christos | Kozyrakis, | and |     |     |     |     |     |     |     |
| ---------- | ------ | ---- | ------- | -------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
ParthasarathyRanganathan.MemoryHierarchyforWeb [27] Yuchen Huang, Baiteng Ma, Erci Xu, and Chuliang
Search.In2018IEEEInternationalSymposiumonHigh Weng. Don’tSurrendertoLowQPS/$:FastandCost-
PerformanceComputerArchitecture,HPCA,2018.
|     |     |     |     |     |     |     | EfficientANNSwithTridentANN. |     |     |     |     | InProceedingsof |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- | --------------- | --- |
the53rdAnnualInternationalSymposiumonComputer
[17] Qi Chen, Bing Zhao, Haidong Wang, Mingqin Li, Architecture,ISCA,2026.
ChuanjieLiu,ZengzhongLi,MaoYang,andJingdong
Wang. SPANN:Highly-efficientBillion-scaleApproxi- [28] Haodi Jiang, Hao Guo, Minhui Xie, Jiwu Shu, and
mateNearestNeighborSearch. InAdvancesinNeural YouyouLu. High-Throughput,Cost-EffectiveBillion-
InformationProcessingSystems34,NeurIPS,2021. ScaleVectorSearchwithaSingleGPU. InProceedings
ofthe2026ACMSIGMODInternationalConference
| [18] XiaopengFan,SongYan,andChuliangWeng. |     |     |     |     |     | Struc- |     |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
onManagementofData,SIGMOD,2026.
| turedstorageforubiquitousoperatingsystems. |     |     |     |     |     | SCIEN- |     |     |     |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
TIASINICAInformationis,54,2024. [29] WenqiJiang,SuvinaySubramanian,CatGraves,Gus-
|                        |     |     |                              |     |     |     | tavo  | Alonso,AmirYazdanbakhsh,andVidushi |     |             |     |              | Dadu. |
| ---------------------- | --- | --- | ---------------------------- | --- | --- | --- | ----- | ---------------------------------- | --- | ----------- | --- | ------------ | ----- |
| [19] JeromeH.Friedman. |     |     | GreedyFunctionApproximation: |     |     |     |       |                                    |     |             |     |              |       |
|                        |     |     |                              |     |     |     | RAGO: | Systematic                         |     | Performance |     | Optimization | for   |
A Gradient Boosting Machine. Annals of Statistics, Retrieval-AugmentedGenerationServing. InProceed-
29(5),2001.
|     |     |     |     |     |     |     | ings | of the | 52nd | Annual International |     | Symposium | on  |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------ | ---- | -------------------- | --- | --------- | --- |
ComputerArchitecture,ISCA,2025.
[20] CongFu,ChaoXiang,ChangxuWang,andDengCai.
FastApproximateNearestNeighborSearchWithNavi- [30] JeffJohnson,MatthijsDouze,andHervéJégou. Billion-
gatingSpreading-outGraphs. ProceedingsoftheVLDB ScaleSimilaritySearchwithGPUs. IEEETransactions
Endowment,12,2019.
onBigData,7,2021.
[21] LuyuGao,ZhuyunDai,TongfeiChen,ZhenFan,Ben- [31] YuhunJun,ShinhyunPark,Jeong-UkKang,Sang-Hoon
jaminVanDurme,andJamieCallan. ComplementLex- Kim,andEuiseongSeo. Weain’tafraidofnofilefrag-
| ical Retrieval |     | Model | with | Semantic | Residual | Embed- |            |     |        |                |     |                    |     |
| -------------- | --- | ----- | ---- | -------- | -------- | ------ | ---------- | --- | ------ | -------------- | --- | ------------------ | --- |
|                |     |       |      |          |          |        | mentation: |     | causes | and prevention |     | of its performance |     |
dings. InAdvancesinInformationRetrieval(Proceed- impacton modern flashSSDs. In Proceedings ofthe
ingsofECIR2021),ECIR,2021. 22nd USENIX Conference on File and Storage Tech-
nologies,FAST,2024.
| [22] Hao Guo | and | Youyou | Lu. | Achieving | Low-Latency |     |     |     |     |     |     |     |     |
| ------------ | --- | ------ | --- | --------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
Graph-Based Vector Search via Aligning Best-First [32] GuolinKe,QiMeng,ThomasFinley,TaifengWang,Wei
Search Algorithm with SSD. In Proceedings of the Chen,WeidongMa,QiweiYe,andTie-YanLiu. Light-
19thUSENIXSymposiumonOperatingSystemsDesign GBM:AHighlyEfficientGradientBoostingDecision
andImplementation,OSDI,2025. Tree. In Advances in NeuralInformation Processing
Systems30,NeurIPS,2017.
| [23] HaoGuoandYouyouLu. |     |     |     | OdinANN:DirectInsertfor |     |     |     |     |     |     |     |     |     |
| ----------------------- | --- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ConsistentlyStablePerformanceinBillion-ScaleGraph- [33] Barrie Kersbergen, Olivier Sprangers, and Sebastian
BasedVectorSearch. In24thUSENIXConferenceon Schelter. Serenade-Low-LatencySession-BasedRec-
FileandStorageTechnologies,FAST,2026. ommendationine-CommerceatScale. InProceedings
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1637

ofthe2022InternationalConferenceonManagement ZhengyuZhang,EllieWen,andAssafEisenman.Quick-
ofData,SIGMOD,2022. Update:aReal-TimePersonalizationSystemforLarge-
|     |     |     |     |     | ScaleRecommendationModels. |     |     |     | InProceedingsofthe |     |
| --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- | ------------------ | --- |
[34] Maximilian Kuschewski, Jana Giceva, Thomas Neu- 21stUSENIXSymposiumonNetworkedSystemsDesign
mann,andViktorLeis. High-PerformanceQueryPro- andImplementation,NSDI,2024.
| cessing with | NVMe Arrays: | Spilling | without | Killing |     |     |     |     |     |     |
| ------------ | ------------ | -------- | ------- | ------- | --- | --- | --- | --- | --- | --- |
Performance. In Proceedings of the 2025 ACM SIG- [43] Jason Mohoney, Devesh Sarda, Mengze Tang, Shi-
MODInternationalConferenceonManagementofData, haburRahmanChowdhury,AnilPacaci,IhabF.Ilyas,
|     |     |     |     |     | Theodoros |     | Rekatsinas, | and Shivaram | Venkataraman. |     |
| --- | --- | --- | --- | --- | --------- | --- | ----------- | ------------ | ------------- | --- |
SIGMOD,2025.
|     |     |     |     |     | Quake:AdaptiveIndexingforVectorSearch. |     |     |     |     | In19th |
| --- | --- | --- | --- | --- | -------------------------------------- | --- | --- | --- | --- | ------ |
[35] BaptisteLepers,OanaBalmau,KaranGupta,andWilly USENIXSymposiumonOperatingSystemsDesignand
| Zwaenepoel. | KVell:TheDesignandImplementationof |     |     |     |     |     |     |     |     |     |
| ----------- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Implementation,OSDI,2025.
| aFastPersistentKey-ValueStore. |     |     | InProceedingsofthe |     |     |     |     |     |     |     |
| ------------------------------ | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- |
27thACMSymposiumonOperatingSystemsPrinciples, [44] AashiqMuhamed,MonaT.Diab,andVirginiaSmith.
| SOSP,2019. |     |     |     |     | CoRAG: | Collaborative  |     | Retrieval-AugmentedGenera- |                 |        |
| ---------- | --- | --- | --- | --- | ------ | -------------- | --- | -------------------------- | --------------- | ------ |
|            |     |     |     |     | tion.  | In Proceedings |     | of the                     | 2025 Conference | of the |
[36] Conglong Li,Minjia Zhang,David G. Andersen,and NationsoftheAmericasChapteroftheAssociationfor
YuxiongHe. ImprovingApproximateNearestNeighbor ComputationalLinguistics:HumanLanguageTechnolo-
SearchthroughLearnedAdaptiveEarlyTermination. In gies(Volume2:ShortPapers),NAACL,2025.
Proceedingsofthe2020ACMSIGMODInternational
ConferenceonManagementofData,SIGMOD,2020. [45] YutoOikawa,YukiNakayama,andKojiMurakami. A
|     |     |     |     |     | Stacking-based |     | Efficient | Method | forToxic | Language |
| --- | --- | --- | --- | --- | -------------- | --- | --------- | ------ | -------- | -------- |
[37] SenLi,FuyuLv,TaiweiJin,GuliLin,KepingYang,Xi- DetectiononLiveStreamingChat. InProceedingsof
aoyiZeng,Xiao-MingWu,andQianliMa. Embedding- the2022ConferenceonEmpiricalMethodsinNatural
basedProductRetrievalinTaobaoSearch. InProceed- LanguageProcessing,EMNLP,2022.
ingsofthe27thACMSIGKDDConferenceonKnowl-
edgeDiscoveryandDataMining,KDD,2021. [46] Hiroyuki Ootomo, Akira Naruse, Corey Nolet, Ray
|     |     |     |     |     | Wang,TamasFeher,andYongWang. |     |     |     | CAGRA:Highly |     |
| --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | ------------ | --- |
[38] YiweiLi,YuxinJin,BoyuTian,HuanchenZhang,and ParallelGraphConstructionandApproximateNearest
MingyuGao. ANSMET:ApproximateNearestNeigh- NeighborSearchforGPUs. InProceedingsofthe40th
borSearchwithNear-MemoryProcessingandHybrid IEEEInternationalConferenceonDataEngineering,
| Early Termination. | In Proceedings |     | of the | 52nd An- | ICDE,2024. |     |     |     |     |     |
| ------------------ | -------------- | --- | ------ | -------- | ---------- | --- | --- | --- | --- | --- |
nualInternationalSymposiumonComputerArchitec-
[47] ChijunSima,YaoFu,Man-KitSit,LiyiGuo,XuriGong,
ture,ISCA,2025.
|     |     |     |     |     | Feng | Lin, Junyu | Wu, | Yongsheng | Li, Haidong | Rong, |
| --- | --- | --- | --- | --- | ---- | ---------- | --- | --------- | ----------- | ----- |
[39] KejingLu,MineichiKudo,ChuanXiao,andYoshiharu Pierre-Louis Aublin, and Luo Mai. Ekko: A Large-
Ishikawa. HVS: Hierarchical Graph Structure Based ScaleDeepLearningRecommenderSystemwithLow-
|     |     |     |     |     |     |     |     |     | Proceedings of | the 16th |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------- | -------- |
onVoronoiDiagramsforSolvingApproximateNearest Latency Model Update. In
NeighborSearch.ProceedingsoftheVLDBEndowment, USENIXSymposiumonOperatingSystemsDesignand
| 15,2021. |     |     |     |     | Implementation,OSDI,2022. |     |     |     |     |     |
| -------- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | --- | --- |
[40] YuA.MalkovandD.A.Yashunin. EfficientandRobust [48] Harsha Vardhan Simhadri, George Williams, Martin
ApproximateNearestNeighborSearchUsingHierarchi- Aumüller, Matthijs Douze, Artem Babenko, Dmitry
Baranchuk,QiChen,LucasHosseini,RavishankarKr-
| calNavigableSmallWorldGraphs. |     |     | IEEETransactions |     |     |     |     |     |     |     |
| ----------------------------- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
onPatternAnalysisandMachineIntelligence,42,2020. ishnaswamy, Gopal Srinivasa, Suhas Jayaram Subra-
|     |     |     |     |     | manya,andJingdongWang. |     |     | ResultsoftheNeurIPS’21 |     |     |
| --- | --- | --- | --- | --- | ---------------------- | --- | --- | ---------------------- | --- | --- |
[41] MagdalenDobsonManohar,ZheqiShen,GuyE.Blel- ChallengeonBillion-ScaleApproximateNearestNeigh-
loch, Laxman Dhulipala, Yan Gu, Harsha Vardhan borSearch. InProceedingsoftheNeurIPS2021Com-
Simhadri,and Yihan Sun. ParlayANN: Scalable and petitionsandDemonstrationsTrack,NeurIPS,2022.
DeterministicParallelGraph-BasedApproximateNear-
|                              |     |     |                    |     | [49] Suhas | Jayaram | Subramanya, |     | Devvrit, Harsha | Vard- |
| ---------------------------- | --- | --- | ------------------ | --- | ---------- | ------- | ----------- | --- | --------------- | ----- |
| estNeighborSearchAlgorithms. |     |     | InProceedingsofthe |     |            |         |             |     |                 |       |
29thACMSIGPLANAnnualSymposiumonPrinciples hanSimhadri,RavishankarKrishnawamy,andRohan
|     |     |     |     |     | Kadekodi. | DiskANN:FastAccurateBillion-pointNear- |     |     |     |     |
| --- | --- | --- | --- | --- | --------- | -------------------------------------- | --- | --- | --- | --- |
andPracticeofParallelProgramming,PPoPP,2024.
|     |     |     |     |     | est | Neighbor | Search | on a Single | Node. In | Advances |
| --- | --- | --- | --- | --- | --- | -------- | ------ | ----------- | -------- | -------- |
[42] Kiran Kumar Matam, Hani Ramezani, Fan Wang, inNeuralInformationProcessingSystems32,NeurIPS,
| ZeliangChen,YueDong,MaomaoDing,ZhiweiZhao, |     |     |     |     | 2019. |     |     |     |     |     |
| ------------------------------------------ | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
1638    20th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

[50] YipingSun,YangShi,andJiaolongDu. AReal-Time [58] YumingXu,HengyuLiang,JinLi,ShuotaoXu,QiChen,
Adaptive Multi-Stream GPU System For Online Ap- QianxiZhang,ChengLi,ZiyueYang,FanYang,Yuqing
proximateNearestNeighborhoodSearch. InProceed- Yang,PengCheng,andMaoYang. SPFresh:Incremen-
ingsofthe33rdACMInternationalConferenceonIn- talIn-PlaceUpdateforBillion-ScaleVectorSearch. In
formationandKnowledgeManagement,CIKM,2024. Proceedingsofthe29thSymposiumonOperatingSys-
temsPrinciples,SOSP,2023.
[51] BingTian,HaikunLiu,YuhangTang,ShihaiXiao,Zhuo-
huiDuan,XiaofeiLiao,XuecangZhang,JunhuaZhu, [59] ZhiqiangXu,DongLi,WeijieZhao,XingShen,Tianbo
|             |                               |     |     | Huang,XiaoyunLi,andPingLi. |     | AgileandAccurate |     |
| ----------- | ----------------------------- | --- | --- | -------------------------- | --- | ---------------- | --- |
| andYuZhang. | FusionANNS:AnEfficientCPU/GPU |     |     |                            |     |                  |     |
CooperativeProcessingArchitectureforBillion-scale CTRPredictionModelTrainingforMassive-ScaleOn-
ApproximateNearestNeighborSearch.In23rdUSENIX lineAdvertisingSystems. InProceedingsofthe2021
InternationalConferenceonManagementofData,SIG-
| Conference    | on File and   | Storage Technologies,FAST, |              |                 |          |                  |            |
| ------------- | ------------- | -------------------------- | ------------ | --------------- | -------- | ---------------- | ---------- |
| 2025.         |               |                            |              | MOD,2021.       |          |                  |            |
|               |               |                            |              | [60] Shuo Yang, | Haocheng | Xi, Yilong Zhao, | Muyang Li, |
| [52] Godfried | T. Toussaint. | The Relative               | Neighborhood |                 |          |                  |            |
XiaozeFan,JintaoZhang,HanCai,YujunLin,Xiuyu
| GraphofaFinitePlanarSet. |     | PatternRecognition,12, |     |     |     |     |     |
| ------------------------ | --- | ---------------------- | --- | --- | --- | --- | --- |
Li,KurtKeutzer,SongHan,ChenfengXu,andIonSto-
1980.
ica. Flash-KMeans:FastandMemory-EfficientExact
|                                     |     |     |                 | K-Means. | InarXiv,2026. |     |     |
| ----------------------------------- | --- | --- | --------------- | -------- | ------------- | --- | --- |
| [53] KosetsuTsukudaandMasatakaGoto. |     |     | ExplainableRec- |          |               |     |     |
ommendationforRepeatConsumption. InProceedings [61] Xinyang Yi, Ji Yang, Lichan Hong, Derek Zhiyuan
ofthe14thACMConferenceonRecommenderSystems,
Cheng,LukaszHeldt,AditeeAjitKumthekar,ZheZhao,
RecSys,2020.
|     |     |     |     | LiWei,andEdH.Chi. |     | Sampling-Bias-CorrectedNeu- |     |
| --- | --- | --- | --- | ----------------- | --- | --------------------------- | --- |
ralModelingforLargeCorpusItemRecommendations.
| [54] Chenyang | Wang,Min | Zhang,Weizhi | Ma,Yiqun Liu, |     |     |     |     |
| ------------- | -------- | ------------ | ------------- | --- | --- | --- | --- |
InProceedingsofthe13thACMConferenceonRecom-
| andShaopingMa. | ModelingItem-SpecificTemporal |     |     |     |     |     |     |
| -------------- | ----------------------------- | --- | --- | --- | --- | --- | --- |
menderSystems,RecSys,2019.
| Dynamics | ofRepeatConsumption |     | forRecommender |     |     |     |     |
| -------- | ------------------- | --- | -------------- | --- | --- | --- | --- |
Systems. InProceedingsoftheWorldWideWebCon- [62] DonghanYu,ChenguangZhu,YuweiFang,WenhaoYu,
ference,WWW,2019.
ShuohangWang,YichongXu,XiangRen,YimingYang,
andMichaelZeng.KG-FiD:InfusingKnowledgeGraph
[55] Jianguo Wang, Xiaomeng Yi, Rentong Guo, Hai Jin, inFusion-in-DecoderforOpen-DomainQuestionAn-
PengXu,ShengjunLi,XiangyuWang,XiangzhouGuo,
|     |     |     |     | swering. | InProceedingsofthe60thAnnualMeetingof |     |     |
| --- | --- | --- | --- | -------- | ------------------------------------- | --- | --- |
Chengming Li, Xiaohai Xu, Kun Yu, Yuxing Yuan, theAssociationforComputationalLinguistics(Volume
YinghaoZou,JiquanLong,YudongCai,ZhenxiangLi,
1:LongPapers),ACL,2022.
ZhifengZhang,YihuaMo,JunGu,RuiyiJiang,YiWei,
andCharlesXie. Milvus:APurpose-BuiltVectorData [63] Qianxi Zhang,Shuotao Xu,Qi Chen,Guoxin Sui,Ji-
ManagementSystem. InProceedingsofthe2021ACM adong Xie, Zhizhen Cai, Yaoqi Chen, Yinxuan He,
YuqingYang,FanYang,MaoYang,andLidongZhou.
SIGMODInternationalConferenceonManagementof
Data,SIGMOD,2021. VBASE:UnifyingOnlineVectorSimilaritySearchand
|     |     |     |     | RelationalQueriesviaRelaxedMonotonicity. |     |     | InPro- |
| --- | --- | --- | --- | ---------------------------------------- | --- | --- | ------ |
ceedingsofthe17thUSENIXSymposiumonOperating
| [56] Mengzhao | Wang, Weizhi | Xu, Xiaomeng | Yi, Songlin |     |     |     |     |
| ------------- | ------------ | ------------ | ----------- | --- | --- | --- | --- |
Wu,ZhangyangPeng,XiangyuKe,YunjunGao,Xiao- SystemsDesignandImplementation,OSDI,2023.
| liangXu,RentongGuo,andCharlesXie. |     |     | Starling:An |     |     |     |     |
| --------------------------------- | --- | --- | ----------- | --- | --- | --- | --- |
[64] ZiliZhang,ChaoJin,LinpengTang,XuanzheLiu,and
| I/O-Efficient | Disk-Resident | Graph | Index Framework |          |                   |                |         |
| ------------- | ------------- | ----- | --------------- | -------- | ----------------- | -------------- | ------- |
|               |               |       |                 | Xin Jin. | Fast, Approximate | Vector Queries | on Very |
forHigh-DimensionalVectorSimilaritySearchonData
|          |                                 |     |     | LargeUnstructuredDatasets. |     | In20thUSENIXSympo- |     |
| -------- | ------------------------------- | --- | --- | -------------------------- | --- | ------------------ | --- |
| Segment. | InProceedingsofthe2024ACMSIGMOD |     |     |                            |     |                    |     |
siumonNetworkedSystemsDesignandImplementation,
InternationalConferenceonManagementofData,SIG-
NSDI,2023.
MOD,2024.
| [57] Yang | Xiao, Mo Sun, | Ziyu Song, | Bing Tian, Jie Sun, |     |     |     |     |
| --------- | ------------- | ---------- | ------------------- | --- | --- | --- | --- |
JieZhang,ZekeWang,ZonghuiWang,WenzhiChen,
| andFeiWu. | FlashANNS:GPU-DrivenAsynchronous |     |     |     |     |     |     |
| --------- | -------------------------------- | --- | --- | --- | --- | --- | --- |
I/OPipeliningforEliminatingStorage-ComputeBottle-
necksinBillion-ScaleSimilaritySearch.InProceedings
ofthe2026ACMSIGMODInternationalConference
onManagementofData,SIGMOD,2026.
USENIX Association 20th USENIX Symposium on Operating Systems Design and Implementation    1639