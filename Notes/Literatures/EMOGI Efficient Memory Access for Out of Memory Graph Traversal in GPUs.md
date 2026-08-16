# EMOGI

**Source**: EMOGI.pdf
**Format**: .pdf

---

|     | EMOGI:      | Efficient       | Memory-access         |     | for Out-of-memory |             |     |     |
| --- | ----------- | --------------- | --------------------- | --- | ----------------- | ----------- | --- | --- |
|     |             | Graph-traversal |                       | in  | GPUs              |             |     |     |
|     | SeungWonMin |                 | VikramSharmaMailthody |     |                   | ZaidQureshi |     |     |
UniversityofIllinoisat UniversityofIllinoisat UniversityofIllinoisat
|                             | Urbana-Champaign       |     | Urbana-Champaign     |               |     | Urbana-Champaign       |     |     |
| --------------------------- | ---------------------- | --- | -------------------- | ------------- | --- | ---------------------- | --- | --- |
|                             | Urbana,IL,USA          |     |                      | Urbana,IL,USA |     | Urbana,IL,USA          |     |     |
|                             | min16@illinois.edu     |     | vsm2@illinois.edu    |               |     | zaidq2@illinois.edu    |     |     |
|                             | JinjunXiong            |     | EimanEbrahimi        |               |     | Wen-meiHwu             |     |     |
| IBMT.J.WatsonResearchCenter |                        |     |                      | NVIDIA        |     | UniversityofIllinoisat |     |     |
|                             | YorktownHeights,NY,USA |     |                      | Austin,TX,USA |     | Urbana-Champaign       |     |     |
|                             | jinjun@us.ibm.com      |     | eebrahimi@nvidia.com |               |     | Urbana,IL,USA          |     |     |
w-hwu@illinois.edu
ABSTRACT
PVLDBAvailabilityTag:
Thesourcecodeofthisresearchpaperhasbeenmadepubliclyavailableat
Modernanalyticsandrecommendationsystemsareincreasingly
basedongraphdatathatcapturetherelationsbetweenentities https://github.com/illinois-impact/EMOGI.
| being analyzed. | Practical | graphs come in huge | sizes, offer | mas- |     |     |     |     |
| --------------- | --------- | ------------------- | ------------ | ---- | --- | --- | --- | --- |
siveparallelism,andarestoredinsparse-matrixformatssuchas 1 INTRODUCTION
compressedsparserow(CSR).Toexploitthemassiveparallelism, Graphworkloadsarebecomingincreasinglywidespreadandcom-
developers areincreasingly interestedin usingGPUsfor graph moninvariousapplicationssuchassocialnetworkanalysis,recom-
traversal.However,duetotheirsizes,graphsoftendonotfitinto mendationsystems,financialmodeling,bio-medicalapplications,
theGPUmemory.Priorworkshaveeitherusedinputdatapre-
graphdatabasesystems,webdata,geographicalmaps,andmany
processing/partitioningorunifiedvirtualmemory(UVM)tomi-
more[12–16,18,51,53,65].Graphsusedintheseapplicationsoften
gratechunksofdatafromthehostmemorytotheGPUmemory. comeinhugesizes.ArecentsurveyconductedbytheUniversityof
However,thelarge,multi-dimensional,andsparsenatureofgraph Waterloo[53]findsthatmanyorganizationsusegraphsthatconsist
datapresentsamajorchallengetotheseschemesandresultsin ofbillionsofedgesandconsumehundredsofgigabytesofstorage.
significantamplificationofdatamovementandreducedeffective
Themainchallengethatgraphapplicationdeveloperscurrently
datathroughput.Inthiswork,weproposeEMOGI,analternative
faceisperforminggraphtraversalcomputationsonlargegraphs[53].
approachtotraversegraphsthatdonotfitinGPUmemoryusing Becauseofthemassiveparallelismpresentinthegraphtraversal
directcache-line-sizedaccesstodatastoredinhostmemory. computation,GPUsareincreasinglyusedtoperformgraphanalyt-
Thispaperaddressestheopenquestionofwhetherasufficiently ics.However,theabilitytoprocesslargegraphsinGPUsiscurrently
largenumberofoverlappingcache-line-sizedaccessescanbesus-
hamperedbytheirlimitedmemorycapacity.Thusinthiswork,we
tainedto1)toleratethelonglatencytohostmemory,2)fullyutilize
primarilyfocusondevelopinganefficientgraphtraversalsystem
theavailablebandwidth,and3)achievefavorableexecutionper-
usingGPUsthataccesseslargegraphdatafromhostmemory.
formance.Weanalyzethedataaccesspatternsofseveralgraph For efficient storage and access, graphs are stored in a com-
traversalapplicationsinGPUoverPCIeusinganFPGAtounder- pressedsparserow(CSR)dataformatasithaslowmemoryover-
standthecauseofpoorexternalbandwidthutilization.Bycarefully
|     |     |     |     | head. In | CSR format, a | graph is stored as | the combination | of a |
| --- | --- | --- | --- | -------- | ------------- | ------------------ | --------------- | ---- |
coalescingandaligningexternalmemoryrequests,weshowthat
|     |     |     |     | vertex | list and an edge | list. Even with | CSR data format, | large |
| --- | --- | --- | --- | ------ | ---------------- | --------------- | ---------------- | ----- |
wecanminimizethenumberofPCIetransactionsandnearlyfully
graphdatasetscannotfitintoday’sGPUmemory.Thus,mostprior
utilizethePCIebandwidthwithdirectcache-lineaccessestothe worksstoretheselargegraphsinhostmemoryandhaveGPUs
host memory. EMOGI achieves 2.60× speedup on average com- accessthemthroughtheunifiedvirtualmemory(UVM)mecha-
paredtotheoptimizedUVMimplementationsinvariousgraph nism[10,11,23,29,34,37,39,41].UVMbringsbothCPUmemory
traversalapplications.WealsoshowthatEMOGIscalesbetterthan
andGPUmemoryintoasinglesharedaddressspace.UVMallows
aUVM-basedsolutionwhenthesystemuseshigherbandwidth
GPUstosimplyaccessthedataintheunifiedvirtualaddressspace
interconnectssuchasPCIe4.0. andittransparentlymigratesrequiredpagesbetweenhostmemory
andGPUmemoryusingapagingmechanism.
PVLDBReferenceFormat:
SeungWonMin,VikramSharmaMailthody,ZaidQureshi,JinjunXiong,
EimanEbrahimi,andWen-meiHwu.EMOGI:EfficientMemory-accessfor
thislicense.Foranyusebeyondthosecoveredbythislicense,obtainpermissionby
Out-of-memoryGraph-traversalinGPUs.PVLDB,14(2):114-127,2021.
emailinginfo@vldb.org.Copyrightisheldbytheowner/author(s).Publicationrights
| doi:10.14778/3425879.3425883 |     |     |     | licensedtotheVLDBEndowment. |     |     |     |     |
| ---------------------------- | --- | --- | --- | --------------------------- | --- | --- | --- | --- |
ProceedingsoftheVLDBEndowment,Vol.14,No.2ISSN2150-8097.
ThisworkislicensedundertheCreativeCommonsBY-NC-ND4.0International doi:10.14778/3425879.3425883
License.Visithttps://creativecommons.org/licenses/by-nc-nd/4.0/toviewacopyof
114

However, several prior work [10, 11, 23, 34, 37, 39, 41] have applythesetwooptimizationstopopulargraphtraversalapplica-
reportedthattheperformanceofgraphtraversalusingUVMisnot tionsincludingbreadth-firstsearch(BFS),single-sourceshortest
competitive.Thisisbecausememoryaccessesthatgototheedge path(SSSP),connectedcomponents(CC),andPageRank(PR)to
listduringgraphtraversalareirregularinnature.Furthermore, enableefficienttraversalonlargegraphs.
basedonouranalysisof1122graphsthathaveatleast1Mvertices Usingreal-worldandsyntheticlargegraphs(seeTable2),we
andedgesfromLAW[13],SuiteSparseMatrixCollection[18],and showthatEMOGIcanachieve2.93×speeduponaveragecompared
NetworkRepository[51],wefindtheaveragedegreepervertex totheoptimizedUVMimplementationsofBFS,SSSP,CC,andPR
isabout71.Thisimpliesthatwhenthosegraphsarerepresented benchmarksacrossavarietyofgraphs.WealsoevaluateEMOGIon
inacompressedadjacencylistformatsuchasCSR,eachvertex’s thelatestgenerationoftheNVIDIAAmpereA100GPUwithPCIe
neighbor edge list is about 71 elements long on average. Thus 4.0andshowthatEMOGIstillremainsperformantandscalesbetter
transferringanentire4KBpage,asinthecaseofUVM,cancause thantheUVMsolutionwhenusinghigher-bandwidthinterconnect.
memorythrashingandunnecessaryI/Oreadamplification. EMOGIachievesspeedupsofupto4.73×overcurrentstate-of-art
Asaresult,priorworkshaveproposedpre-processingofinput GPUsolutions[23,52]forlargeout-of-memorygraphtraversals.In
graphsbypartitioningandloadingthoseedgesthatareneeded addition,EMOGIdoesnotrequirepre-processingorruntimepage
duringthecomputation[27,52,55,63]orproposingUVMspecific migrationengine.
hardwareorsoftwarechangessuchaslocalityenhancinggraph Tothebestofourknowledge,EMOGIisthefirstworktosys-
reordering[23],GPUmemorythrottling[37,39],overlappingcom- tematicallycharacterizeGPUPCIeaccesspatternstooptimizezero-
puteandI/O[25],orevenproposingnewprefetchingpoliciesin copyaccessandtoprovidein-depthprofilingresultsofvaryingPCIe
hardwarethatcanincreasedatalocalityinGPUmemory[10,11,34]. accessbehaviorsforawiderangeofgraphtraversalapplications.
Inthiswork,wetakeastepbackandrevisittheexistinghardware Overall,ourmaincontributionscanbesummarizedasfollows:
memorymanagementmechanismforwhendatadoesnotfitin (1) WeproposeEMOGI,anovelzero-copybasedsystemforvery
GPUmemory.Specifically,wefocusonzero-copymemoryaccess largegraphtraversalonGPUs.
whichallowsGPUstodirectlyaccessthehostmemoryincache- (2) Weproposetwozero-copyoptimizations,memoryaccess
linegranularity.Withzero-copy,nocomplicateddatamigrationis mergeandmemoryaccessalignment,thatcanbeappliedto
neededandGPUscanfetchdataassmallas32-bytefromthehost graphtraversalkernelcodetomaximizePCIebandwidth.
memory.Evenwithsuchadvantages,unfortunately,zero-copyis (3) We show EMOGI performance scales linearly with CPU-
knowntohaveunderwhelmingperformanceduetothelowexternal GPUinterconnectbandwidthimprovementbyevaluating
interconnectbandwidth[22].Interestingly,however,wedonotfind PCIe3.0andPCIe4.0interconnects.
anysystematicanalysisshowingtheexactlimitingfactorofthe
Therestofthepaperisorganizedasfollows:weprovideabrief
zero-copyperformanceorleadingtoanyefforttoimproveit.
primeronGPUbasedgraphtraversalandthechallengesinexe-
Insteadofmakingaprematureconclusion,webuildasystem
cutinggraphtraversalsusingUVMin§2.Wethendiscusshowto
withacustom-designedFPGA-basedPCIetrafficmonitorandex-
enablezero-copymemorywithGPUsanddiscussthereasonsfor
ploreanyopportunitytooptimizezero-copyperformance.Weuse
itspoorperformanceinanaivebutcommonkernelcodepattern
thesystemtoaddressthequestionofwhetherasufficientlylarge
in§3.Usingthegainedinsights,wethenapplyzero-copyopti-
numberofoverlappingcache-line-sizedaccessescanbesustained
mizationstographtraversalalgorithmsin§4.WediscussEMOGI’s
to1)toleratethelonglatencytohostmemory,2)fullyutilizethe
performanceimprovementforvariousgraphtraversalalgorithms
availablebandwidth,and3)achievefavorableexecutionperfor-
onseverallargegraphsin§5.§7discusseshowEMOGIdiffers
manceforgraphtraversalapplications.Tothisend,thekeygoalof
frompriorworkandweconcludein§8.
ourworkistoavoidperforminganypre-processingordatamanip-
ulationontheinputgraphandallowingGPUthreadstodirectly
2 BACKGROUND
performcache-line-sizedaccessestodatastoredinhostmemory
duringgraphtraversals. Inthissection,wefirstprovideabriefprimeronGPUbasedgraph
Byusingatoyexample,weshowthatbynaivelyenablingzero- traversal.Thenwewilldescribetechniquesusedtotraversegraphs
copy,thesystemcannotsaturatethePCIe3.0x16bandwidth(see thatcannotfitintotheGPUmemory.
§3.3).Toaddressthis,weproposetwokeysoftwareoptimizations
neededtobestexploitPCIebandwidthforthezero-copyaccess. 2.1 ParallelizingGraphTraversalonGPUs
First,weproposethemergedmemoryaccessoptimizationthat Theexactworkflowofthegraphtraversaldependsonthetypeof
optimizesforgeneratingmaximum-sizedPCIerequesttozero-copy theapplicationandtheoptimizationlevel,butageneralflowcanbe
memory(see§3.3).Second,weproposeforcingmemoryaccess describedwithAlgorithm1.First,beforethetraversalbegins,initial
alignmentbyshiftingallwarpsto128-byteboundarieswhenthere activeverticesneedtobeset.IncaseofBFS,onlyasinglevertex
is misalignment. This is because the memory access merge op- needstobesetasactive,whichisbasicallyasourcevertex.Once
timizationdoesnotguaranteememoryrequestalignment.Such alltheinitialactiveverticesareset,thegraphtraversalcanbegin.
misalignmentcanresultinperformancedegradation.Whilethese Graphtraversaliscomposedofmultipleiterationsofsub-traversals.
optimizationssacrificesomeparallelismandincuradditionalcon- Ineachsub-traversal,allimmediatelyneighboringverticesofthe
troldivergenceduringkernelexecution,theirbenefitintermsof currentlyactiveverticesareexhaustivelytraversed.Thecondition
improvedbandwidthutilizationfaroutweighsthecost.Wethen tosetthenextactiveverticesdependsonthetypeofapplicationas
well.IncaseofBFS,anyneighboringverticeswhicharenotvisited
115

everbeforearemarkedtobethenextactivevertices.Thetraversal
1 4
endsoncetherearenomoreactiveverticesleftinthegraph.
ThemainbenefitoftheGPUimplementationofthegraphtra- 0
versalcomesfromthemassivenumberofvertices[15,16,65].With 2 3
ahelpofseveralatomicinstructions,boththeinnerloopandthe
outerloopinAlgorithm1canbefullyparallelizedwithGPUfor (a) Graph
variouskindsofgraphtraversalapplications[17,28,30,31]. • • • Vertex 1 Vertex 2 • • •
AsaninputgraphformatfortheGPUgraphtraversal,weuse Neighbor List Neighbor List
compressedsparserow(CSR)format.CSRisarguablythemost Edge List 1 2 0 2 3 4 0 1 4 1 2 3 1 4
popularwaytorepresentagraphbecauseofitslowmemoryover-
head[27,48,52,55,63,69].Certaingraphprocessingframeworks
Vertex List 0 2 6 9 12 14
suchasnvGRAPH[1]supportotherinputformatslikecoordinate
Vertex ID 0 1 2 3 4 end
list(COO),buttheyinternallyconverttheinputstotheCSRformat (b) CSR
beforetheactualprocessingstep.CSRencodestheentiregraph
withjust2arrays,asshowninFigure1.Theedgeliststoreseach Figure1:Sampleundirected(a)graphandits(b)CSRrepresentation.
vertex’sneighborlistsequentially,suchthatalltheneighborsof Theedgelistcontainstheneighborlistforeachnode.Thevertex
vertex0arestoredfirst,thentheneighborsofvertex1,andsoon. listisindexedbyvertexIDsandcontainstheoffsetsforthestarting
ThevertexlistisindexedbyavertexIDandstoresthestarting positionofthatvertex’sneighborlistintheedgelist.
offsetofthatvertex’sneighborlistintheedgelist.Thedatatypes
ofbothedgeandvertexlistscanvarydependingonthegraphsize.
samepagedonotneedadditionaldatamigrationsandtheaccesses
Forexample,usinga4-bytedatatypefortheedgelistcanidentify
candirectlygototheGPUmemory.Ifthememoryfootprintof
atmost4billionnodes.
thekernelislargerthantheGPUmemory,somepagesneedto
beevictedfromtheGPUmemorytohostotherpagesduringthe
2.2 Out-of-MemoryGraphTraversalonGPUs
kernel runtime. Since the entire management process is single-
Graphs,evenintheCSRformat,canbeordersofmagnitudelarger
threaded, the overall performance of the UVM page migration
thanGPUmemory.TheeasiestwaytoenableGPUbasedgraph
heavilydependsonthesingle-threadperformanceofthehostCPU.
traversal on such graphs is to use the Unified Virtual Memory
TheinefficiencyofUVMingraphtraversalcomesintwoways.
(UVM)[2,3,10,11,23,29,34,37,39,41,50].UVMisaunifiedmem-
First,fortheverylargegraphs,itishardtoexploittemporallo-
orymanagementmodulethatprovidesasinglememoryaddress
cality as the limited GPU memory capacity will cause frequent
spaceaccessiblebybothCPUandGPUthroughthepagefaulting
pagethrashing.Second,thereisalackofspatiallocalitybetween
mechanism.UVMreducestheburdenontheprogrammerasthey
neighborlists,causingsignificantI/Oreadamplificationandmore
donothavetoexplicitlymanagewherethedataresides.UVMtrans-
frequentpagemigrations.Forexample,inFigure1,theneighbor
parentlyallowsdevicememoryover-subscriptionwiththeuseof
listsofthevertex1and3needtobeaccessedatthesametime
CPUmemory,enablingcomputationonlargedatasetsthatexceed
westartBFSfromthevertex4.However,asshownintheCSR
GPUdevicememorycapacity.TheUVMdriverisresponsiblefor
representation,thelistsarenon-contiguousintheedgelist.Ina
on-demandpagemigrationbetweentheCPUandGPU.
morerealisticcasewithalargegraph,theselistscanbeseparated
Thegranularityofthedatamigrationmayvarydependingonthe
bymillionsofelementsintheedgelist.Therefore,accessingthese
dataaccesspattern,buttheminimumgranularityisasystempage
twolistswilllikelygeneratetwoseparate4KBpagemigrations.As-
size(4KB).Oncethepageismigrated,subsequentaccessestothe
sumingthatallaccessestothedifferentneighborlistswillgenerate
separate4KBpagemigrations,allneighborlistsshouldhaveleast
512to1024ofelements(dependsonthedatatypesize)tomakethe
Algorithm1:High-levelGraphTraversalFlow
4KBdatatransfer100%efficient,whichmightbequitechallenging.
set_initial_active_vertex()
Bycombiningthefrequentpagemigrationscausedbythelackof
whilethereexistactiveverticesinGdo datalocalityandthehighpagefaulthandlingoverheadofUVM,
forallverticesv1inGraphGdo GPUperformancecanbeseverelythrottled.
ifv1isactivethen
setv1 asinactive
3 ZERO-COPY
forallneighborsv2ofv1do
application_dependant_workload() ToallowGPUthreadsaccesstotheexternalmemoryinsmaller
ifapplication_dependant_condition()then granularitythanUVM,GPUssupportmarkingmemoryaddress
setv2 asactive rangesaszero-copymemory[4].Zero-copy,alsooftenreferredto
end asdirectaccess,doesnotrequireanypagemigrationorduplication
end betweentheexternalandGPUmemories.Instead,GPUthreads
accesszero-copymemoryasifitwasGPUglobalmemory,and
end
theGPUtransformsmemoryrequestsfromthethreadstomemory
end
requests over an external interconnect like PCIe. The target of
end
thememoryrequestscanbeanywhereinthesystemaslongas
116

advertiseitselfasalargememoryusingthebaseaddressregister
GGPPUU PCIe PCIe 3.0 (BAR)regionprovidedbythePCIespecification[8].Thisadvertised
FPGA
VV110000 1166GGBB Switch FPGAmemoryregioncanbemappedtotheuserspaceusingthe
mmap()systemcall.Thereturnedpointervaluefromthemmap()
callcanbeusedbyCPUtoaccesstheFPGAasazero-copyregion.
ToallowtheGPUdirectaccesstotheFPGA,wepassthepointerto
CPU Root Complex H H o o s s t t M M e e m m o o r r y y cudaHostRegister()andcudaGetDevicePointer()CUDAAPIs.
Host Memory
ThefinalpointergeneratedbythetwoAPIscanbepassedtothe
CUDAkernelcodeanddereferencedbyGPUthreads,thusallow-
Figure2:PCIetrafficmonitoringenvironment.TheFPGAisusedto ingzero-copyaccesstotheFPGA.Usingthissystem,wecannow
characterizethezero-copymemoryaccesspatternfromGPU. analyzethelow-levelPCIetrafficofzero-copymemoryaccessby
theGPU.Tothisend,weaddcustomlogicintheFPGAtomonitor
therequestcount,average/peaknumberofoutstandingmemory
thelocationcanbememory-mappedintothesharedbusaddress.
requests,andrequestsizes.
Commonexamplesincludesystemmemory,peer-connectedPCIe
networkinterfacecards,andpeer-connectedGPUs.Duetothehigh
latencyoftheexternalinterconnects,usingzero-copywasthought
3.3 Zero-CopyMechanismandOptimization
tohavelowbandwidth[22]andthususedforonlyaccessingsmall
Nowthatwehaveawaytotrackzero-copymemoryrequests,we
andfrequentlyshareddata.Inthissection,wedescribehowto
nextneedtounderstandtheGPUaccesspatterntozero-copymem-
enablezero-copyanduseapeer-connectedFPGAtoexploreany
ory.WecreateatoyexamplewheretheGPUneedstotraversea
optimizationopportunitiesavailableforzero-copyindetail.Based
large1Darrayinazero-copyregionanduseaGPUkerneltocopy
ontheanalysis,weapplyseveraloptimizationsandshowcorrectly
itscontenttotheGPU’sglobalmemory.Thealgorithmtosolve
usingzero-copycannearlysaturatethePCIebandwidth.
thetoyexamplecaneitherperformstridedaccessormergedwith
misalignedaccessormergedwithalignedaccess.AllPCIetraffic
3.1 EnablingZero-Copy
generatedbythesethreevariantsismonitoredusingtheFPGA
Fromthesystem’spointofview,zero-copyisenabledasfollows: monitoringplatformandIntelVTune[5].PCIelayerinFigure3
First,thedatatobesharedwithGPUmustbepinnedinthehost showstheGPUaccesspatternsweobservedwiththeFPGAmoni-
memory.Pinnedmemorycannotbeswappedouttothediskor toringplatformwhiletryingdifferentCUDAkernels.Weobserve
relocatedbythehostOSmemorymanager.Second,thecorrespond- thatGPUcanaccessthezero-copymemoryinfourdifferentsizes
ingbusaddress(e.g.PCIe)ofthepinneddatashouldbemapped startingfrom32-byteto128-bytein32-bytesteps.Theaccesssize
intotheGPUpagetablesotheGPUcangenerateacorrectexternal isdependentonthealgorithmaccesspatternandisdescribednext.
memoryrequest.Finally,themappedaddressshouldbepassedto StridedAccess:Inthismethod,eachthreadtakesachunkof
theuserspacesotheprogrammercanusepointersintheGPU the1D-arrayanditeratesoverthechunkoneelementatatime.
kerneltoaccesstheregion. ThisaccesspatternisillustratedinFigure3(a).WithGPUthreads
FromCUDAAPI’spointofview,zero-copycanbeenabledin iteratingovertheirownneighborlists,wefindthateachthread
threeways.FirsttechniqueusescudaMallocManged()toallocate generatesanew32-byterequesteverytimetheycrossa32-byte
UVMspaceandappliescudaMemAdviseSetAccessedByflagwith addressboundary.Therefore,ifthedatatypeofthearrayis4-byte,
cudaMemAdvise().Theresultingdatapointercanbedirectlyused eachPCIerequestcanserveupto8memoryaccesses.
fromCUDAkernelstogeneratezero-copymemoryaccess.One However,this32-byterequestbringsseverallimitationstothe
thingworthnotinghereisthatthecudaMemAdviseSetAccessedBy overallsystem.First,eachPCIe3.0transactionlayerpacket(TLP)
flagshouldnotbeusedwithothercudaMemAdvise()flagssince hasatleastan18-byteofheaderoverhead.Thus,fetching32-byte
theotherflagsoverridecudaMemAdviseSetAccessedBy.Secondis of data makes the PCIe overhead ratio of at least 36%. Second,
byusingcudaMallocHost().Thisisthesimplestmethodsincethe consideringthePCIelatency,thenumberofoutstandingrequests
memoryallocatedbycudaMallocHost()canbedirectlyusedin tosaturatethePCIeinterconnectisnon-negligible.Withourtest
theCUDAkerneltodozero-copyaccess.Thelastschemeusesgen- platform, we find the PCIe round trip time (RTT) between the
eralmemoryallocators,likemalloc(),andcudaHostRegister() GPUandtheFPGAisaboutroughly1.0usto1.6us.BythePCIe
and cudaGetDevicePointer() on top of the allocated memory. 3.0specification,themaximumnumberofoutstandingrequests
Inthiscase,thecudaHostRegister()pinstheallocatedmemory is256asthewidthofthetagfieldusedtorecordtheoutstanding
spaceandcudaGetDevicePointer()returnsaCUDA-compatible requestis8-bit[8].Inthiscase,themaximumbandwidthwecan
pointer.Ourexperimentsshowedallthreetechniquesprovidedthe achievewithonly32-byterequestsand1.0usofRTTismerely32B
sameperformance. /(1.0us/256)=7.63GB/s.IfweassumethePCIeRTTisalways
1.6us,thebandwidthdecreasesto4.77GB/s.Third,theminimum
3.2 Zero-CopyAnalysisSetup memoryaccesssizeforDDR4DRAMis64-byteinthetestsystem.
InordertounderstandhowGPUaccessesexternalzero-copymem- ConsideringthatDDR42400MHzDRAMcanprovide19.2GB/sof
oryoverPCIe,wedesignedandbuiltthemonitoringsystemshown sequentialbandwidth,requestingonly32-bytereadrequestshalves
inFigure2.TheFPGAisconnectedtotheGPUusingaPCIeswitch theeffectiveDRAMbandwidthto9.6GB/s.EventheoverallDRAM
inpeer-to-peermode.Furthermore,theFPGAisprogrammedto bandwidthcanbeincreasedbyaddingmorememorychannels,
117

WARP WARP WARP WARP WARP
0 31 0 31 0 31 0 31 0 31
128-byte
• • • • •
Blocks
L1/L2
Cache 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B 32B
PCIe 32B 32B 32B 32B 32B 32B 32B 32B 128B 128B 32B 96B 32B 96B
(a) Strided (b) Merged and Aligned (c) Merged but Misaligned
Figure3:GPUPCIememoryrequestpatternsobservedwithFPGA.In(a),eachthreadscansadifferent128Bblockandendupmakingmultiple
32BPCIememoryreadrequests.In(b),individual32BmemoryreadrequestsinacontiguousaddressspaceoccuratthesametimeandGPU
mergesthemintoasingle128BPCIememoryreadrequest.In(c)eachwarpisperformingamisalignedmemoryrequest(offby32Bfrom
128Bboundary)resultingingeneratinga32BPCIeand96BPCIerequest.Inthisfigure,weassumeeachmemoryaccessis4B.
Merged and Merged but 16GB/sofbandwidth(withoutconsideringotherPCIeoverheads).
(a) Strided (b) (c)
Aligned Misaligned
Lastly,128-byteisamultipleDRAMrequestsizeandthereforethere
PCIe UVM 12.23 GB/s 9.40 GB/s isnoinefficiencyintheDRAMinterface.InFigure4(b),wesee
9.11GB/s
h 4.74 GB/s thisapproachcansaturatethePCIebandwidthatabout12.23GB/s,
td
iw matchingthemeasuredbandwidthwhenusingthecudaMemcpy()
d n DRAM APItoperformablockdatatransfer.
a
B 9.61 GB/s 9.2 U 6 V G M B/s 12.36 GB/s 14.26 GB/s MergedbutMisalignedAccess:However,forallpracticalpur-
poses,guaranteeing128-bytealignmentforanydatastructurecan
bedifficult.Itispossiblethatthestartingindexofawarpisnot
Time
alignedwiththe128-byteboundary.Somewarpsmayneedtomake
Figure4:AveragePCIeandDRAMbandwidthutilizationforthedif- twoseparatePCIerequeststofetchasingle128-bytecacheline.In
ferentzero-copyaccesspatterns,asreportedbyIntelVTune. theworstcase,ifawarp’smemoryaccessisnot128-bytealigned
andwarpsaccesscontiguousregionsofmemory,themisalignment
canbecascadedtoallsubsequentwarps.Unfortunately,thisre-
sultsinallwarpsgeneratingtwoPCIerequests.InFigure3(c),we
this is still very wasteful. Finally, these 32-byte data items will
showanemulatedmisalignedcasewhereeachwarpisintentionally
likelyoccupyGPUcacheandcanbeevictedbeforeallelementsare
accessingmemoryoffsetby32-bytefrom128-byteboundaryand
traversedduetocachethrashing.
thereforeallwarpsendupgeneratinga32-byteanda96-bytePCIe
Figure4showstheaveragePCIeandDRAMbandwidthutiliza-
request.FromFigure4(c),wecanseetheachievedPCIebandwidth
tionovertimewhenexecutingthetraversingkernelasreported
islowerthanthealignedcase.Toavoidthis,eitherthestarting
byIntelVTune.ThepeakbandwidthweachievedwithUVMis
indexofwarpsshouldbeshiftedortheinputdatamustbeshifted
drawnasareddashedlineinthefigureasareference.Looking
inmemorysothedataaccessedfirstis128-bytealigned.
atFigure4(a),wecanclearlyidentifythelimitationspreviously
described.TheamountofdatathatneedstobereadfromDRAM
isdoubledtoserve32-bytePCIerequests.ThePCIebandwidthis 4 EMOGI:ZERO-COPYGRAPHTRAVERSAL
alsofarfromthemaximumPCIe3.0x16bandwidthasthenumber
Nowthatweunderstandzero-copymemoryanditscharacteristics,
ofoutstandingrequestsisnotenoughandtheper-requestPCIe
we discuss how to efficiently use zero-copy memory for graph
overheadissignificant.Furthermore,itresultsintransferringmore
traversalwhenthegraphcannotfitintheGPUmemory.First,we
bytestotheGPUcomparedtotheoriginaldatasetsizeduetothe
describethemicrodatalocalityweobservedingraphtraversal
frequentcachelineevictions.Toaddresstheselimitationsthekey
applicationstojustifywhyzero-copyshouldperformbetterthan
istoalignandmergeaccesses.WeanalyzethePCIeandDRAM
UVM(see§4.1).Then,weintroduceourbaselinegraphtraversal
bandwidthutilizationwiththeseoptimizationsnext.
algorithm(see§4.2)andoptimizeitforzero-copymemorybased
MergedandAlignedAccess:Inthiscase,threadsaregrouped
ontheknowledgewegatheredfrom§3.3(see§4.3).
intowarps,witheachwarpcontaining32threads,andthethreads
inawarpaccessconsecutiveelementsina128-bytecachelineofthe
inputarray.ThisallowstheGPUcoalescingunittoautomatically 4.1 DatalocalityinGraphTraversal
mergethecontiguous32-bytememoryrequestsintoasinglelarger Toexploitzero-copyforgraphtraversal,wepreferablyneedatleast
128-bytePCIerequest(Figure3(b)).With128-bytePCIerequests,it 128-byteofspatiallocalitytobestuseeachmemoryaccess.Asingle
becomesmucheasiertoreachthemaximumPCIebandwidth.First, 128-bytezero-copyaccesscanhave16or32elementsofdataifthe
thePCIeTLPoverheadratiodecreasesfrom36%to12.3%.Second, CSRdatatypeis8-byteor4-byte,respectively.ComparedtoUVM,
havingonly135PCIeoutstandingrequestsissufficienttoreach whichrequiresatleast4KBofspatiallocality(512or1024elements
118

ofdata),finding16to32elementsofspatiallocalityisreasonable
forthegraphswestudied. Listing1:UncoalescedMemoryAccess
Based on our analysis of 1122 graphs from Network Reposi- 1 void strided(*edgeList, *offset, ...) {
tory[51],SuiteSparseMatrixCollection[18],andLAW[13],we 2 thread_id = get_thread_id();
findtheaveragedegreepervertexis71.Thismeans,whenthose 3 ...
graphsarerepresentedinanadjacencylistformatlikeCSR,each 4 start = offset[thread_id];
vertex’sneighborlistis71elementslongonaverage.Considering 5 end = offset[thread_id + 1];
6
thatgraphtraversalalgorithmsrequirescanningtheentireneigh-
7 // Each thread loops over a chunk of edge list
borlistofavertex,wecanobtainaspatiallocalityof71elements
8 for (i = start; i < end; i++) {
onaverageingraphs.Suchaspatiallocalitycanbenefitfromeffi-
9 edgeDst = edgeList[i]; ...
cient128-byterequeststozero-copymemory.Incontrast,itismore 10 } ...
difficulttoachievethesamelevelofefficiencyusingUVMsince 11 }
theavailablespatiallocalityissignificantlylessthantherequired
512or1024elements.
toanentirewarp(i.e.,32threads).Thusawholewarpisresponsible
4.2 EMOGIBaseline
fortraversingtheneighborlistofonevertex.Thespecificimple-
EMOGIassumestheinputgraphisstoredinthememoryusing mentationofthisoptimizationisexplainedwithredcommentsin
theCSRdatalayout(see§2.1).Allinputdatastructuresarestat- Listing2.ThisallowsEMOGItoalwaysoptimizeforgeneratingthe
icallymappedduringinitialization.Theedgelistisallocatedin maximumsizedPCIerequesttothezero-copymemory.Iftheinput
thehostmemoryasitdoesn’tfitinGPUmemory,butothersmall graphfitsintheGPUmemoryandtheaveragedegreeofvertices
datastructuressuchasbuffersandthevertexlistareallocatedin inthegraphissmall,fine-tuningtheworkersizecouldpotentially
GPUmemory.Itisworthnotingthatevenforthebiggestgraphs reducethenumberofidlethreadsduringeachfetch,exploitmore
weevaluated(see§5.2),thevertexlistconsumesatmost1GBof memoryparallelism,andultimatelyutilizeGPUglobalmemory
memorywhiletheedgelistcanconsume38GB.Thus,GPUmemory bandwidthmoreefficiently.However,EMOGI’sprimarygoalisto
issufficientforthevertexlist. achievegoodperformanceongraphsthatdonotfitintheGPU
EMOGIadoptsvertex-centricgraphtraversalalgorithms.For memoryanditrequiresfetchingdataoveranexternalintercon-
everyvertexthatneedstobeprocessed,aworkerisassignedand nectthatisabout10-100×slowerthantheGPUglobalmemory.
theworkertraversesaneighborlistassociatedwiththevertexin Inthiscase,fine-tuningandreducingtheworkersizecannotadd
theedgelist.Listing1showsthepseudocodeofournaivebaseline anyadditionalbenefitasthereisnofurtherroomtoacceptmore
implementation.Here,theworkerisasingleGPUthreadandeach memoryrequestsinthealreadyconstrainedinterconnect.Infact,
workerisassignedtotheneighborlistassociatedwithitscorre- makingsmallermemoryrequestscanhaveanadverseeffectand
spondingvertex.Wheneachneighborlistislargerthan128-byte, decreasetheeffectivebandwidth.Empiricallyweobservedwhen
thisbaselineimplementationhasasimilarmemoryaccesspattern theinterconnectbandwidthislow,alargenumberofthreadsare
tothestridedcaseexplainedin§3.3. idle.Therefore,assigninga32-threadwarptofetchdataforeven
ComparedwiththeUVMapproach,EMOGI’sgraphtraversal verticeswithveryfewneighborsresultsinacceptableperformance.
approachremovesthepagefaultsfromoccurringandreducesthe
I/Oamplificationasonlytheneededbytesaremoved.Inthevertex- 4.3.2 Aligned Memory Access. As we discussed in § 3.3, a mis-
centricgraphtraversalapproach,theinputgraphistraversedbya alignedaccesstothe1Ddataarraycanresultinmultiplesmaller
singlevertexdepthoneverykernelexecution.Thereforethetotal zero-copyrequests.Toaddressthis,wehavetonotonlymerge
numberofkernelslaunched,sayinthecaseofbreadth-first-search memoryaccessesbutalignthemaswell.However,doingthisona
(BFS),isequaltothedistancebetweenthesourcevertextothe CSRedgelistisnotstraightforward.ThisisbecauseCSRdoesn’t
furthestreachablevertex. aligntheedgelistasalignmentrequirespaddingandthusincreases
memoryfootprint.Startingaddressesofneighborlistsforgraphs
4.3 Optimizations storedinCSRcanbeatanylocationinthememory.
Onewaytoaddressthischallengeistopre-processtheCSR
SincetheEMOGIbaselineimplementationissimilartothestrided
graphsandalignneighborliststo128-byteboundaries.However,
casepresentedin§3.3,itsuffersfromuncoalescedmemoryrequests.
thismightincurexcessivememoryoverhead.Moreimportantly,
Aswenoted,withoutaddressingthis,onecannotgenerateefficient
oneofthegoalsofthisworkistoavoidanypre-processing.
PCIerequeststothezero-copymemory.Inthissubsection,wewill
Therefore,insteadofmanipulatingtheinputdata,weforceall
discusshowEMOGIaddressesthislimitationusingtheinsights
warpstostartfromtheclosestpreceding128-byteboundarywhen
from§3.3andmodifyingonlytheGPUkernelcodeofthetraversal
thereismisalignment.Forinstance,asshowninListing2with
application.Thus,itisentirelypossibletopackagetheproposed
bluecomments,allstartingindicesfetchedfromtheoffsetarray
optimizationsintoalibrarytolessentheprogrammer’seffortwhen
isshiftedtotheclosest128-byteboundarybeforethelist.With
tryingtoexploitthem.
thischangetotheGPUkernelcode,allsubsequentwarpmemory
4.3.1 MergedMemoryAccess: EMOGIperformsmergedmemory accesses are guaranteed to have 128-byte alignment. Of course,
accessesinpervertexgranularity,similarto[31].Thedifferencebe- someofthethreadsinthewarpmustbeturnedoffduringthefirst
tweenEMOGIand[31]isthatEMOGIalwaysfixestheworkersize iterationofdatafetchingwithaconditionalstatementtoprevent
119

Table1:Evaluationsystemconfiguration.
Listing2:CoalescedMemoryAccess(Merged+Aligned)
1
|     | #define | WARP_SIZE | 32  |     |     |     | Category | Specification |
| --- | ------- | --------- | --- | --- | --- | --- | -------- | ------------- |
2
| 3   |                         |     |          |      |     |     | CPU DualSocketIntelXeonGold623020C/40T |     |
| --- | ----------------------- | --- | -------- | ---- | --- | --- | -------------------------------------- | --- |
|     | void aligned(*edgeList, |     | *offset, | ...) | {   |     |                                        |     |
4
thread_id = get_thread_id(); Memory DDR42933MHz256GBinQuadChannelMode
5
|     | lane_id  | = thread_id | % WARP_SIZE; |     |     |     |                                     |     |
| --- | -------- | ----------- | ------------ | --- | --- | --- | ----------------------------------- | --- |
| 6   |          |             |              |     |     |     | GPU TeslaV100HBM216GB,5120CUDAcores |     |
|     | // Group | by warp     |              |     |     |     |                                     |     |
7
warp_id = thread_id / WARP_SIZE; OS CentOS8.1.1911&Linuxkernel5.5.13
8
...
| 9   |           |     |                  |     |     |     | S/W NVIDIADriver440.82&CUDA10.2.89 |     |
| --- | --------- | --- | ---------------- | --- | --- | --- | ---------------------------------- | --- |
|     | start_org | =   | offset[warp_id]; |     |     |     |                                    |     |
10
|     | // Align | starting | index to 128-byte |     | boundary |     |     |     |
| --- | -------- | -------- | ----------------- | --- | -------- | --- | --- | --- |
11
|     | start | = start_org | & ~0xF; | // 8-byte | data | type |     |     |
| --- | ----- | ----------- | ------- | --------- | ---- | ---- | --- | --- |
12
end = offset[warp_id + 1]; (a)UVMimplementationstorestheCSRedgelistintheUVM
13
addressspacewhilethevertexlistiskeptintheGPUmemory.In
14
// Every thread in a warp goes to the same edgelist addition,theCSRedgelistintheUVMaddressspaceismarkedas
15
|     | for | (i = start; | i < end;     | i +=     | WARP_SIZE) | {   |                                                        |     |
| --- | --- | ----------- | ------------ | -------- | ---------- | --- | ------------------------------------------------------ | --- |
| 16  |     |             |              |          |            |     | cudaMemAdviseSetReadMostlyusingthecudaMemAdvise()CUDA  |     |
|     |     | // Prevent  | underflowed  | accesses |            |     |                                                        |     |
| 17  |     |             |              |          |            |     | APIcall.ThisoptimizationallowstheGPUtocreatearead-only |     |
|     |     | if (i >=    | start_org)   | {        |            |     |                                                        |     |
| 18  |     |             |              |          |            |     | copyoftheaccessedpagesintheGPU’smemory.Wealsotested    |     |
|     |     | edgeDst     | = edgeList[i | +        | lane_id];  |     |                                                        |     |
19 ... otheravailableUVMdriverflagsbutdidnotobservenotablydiffer-
20 } ences.(b)Naiveimplementationisthebaselineimplementationof
| 21  | } ... |     |     |     |     |     |     |     |
| --- | ----- | --- | --- | --- | --- | --- | --- | --- |
EMOGIusingzero-copymemoryandisidenticaltoAlgorithm1.
22 }
Inthisimplementation,thevertexlistisstoredintheGPUmem-
orywhiletheedgelistiskeptinthezero-copyhostmemory.(c)
MergedimplementationofEMOGImergesthememoryrequests
readingunnecessarybytes.Similartothememoryaccessmerge tothezero-copymemory,asdiscussedin§4.3.1.However,inthis
optimization,thisadditionalconditionalstatementincreasesthe
implementation,thereisnoguaranteethataccessestothezero-
occurrenceofcontroldivergenceinCUDAkernels.However,due
copymemoryarealigned.(d)Merged+Alignedimplementationis
tothehighexternalinterconnectlatency,itismoreimportantto
thefullyoptimizedversionofEMOGIwherethememoryaccesses
notmissanyopportunityforgeneratinglargememoryrequests. arenotonlymergedbutweforceallwarpstoshifttothe128-byte
boundarywhenthereisamisalignment.Thisimplementationis
5 EVALUATION
discussedin§4.3.2.
Ourevaluationshowsthat(1)EMOGIimprovestheperformance
ofgraphtraversalalgorithmsbyefficientlyaccessingthezero-copy 5.2 EvaluationDatasets
memoryforverylargegraphs,(2)EMOGIismainlylimitedbythe
Fortheevaluation,weusethegraphslistedinTable2.GK,GU,
PCIebandwidthanditscalesalmostperfectlylinearlywhenPCIe3.0
FS,andMLarethelargestfourgraphsfromSuiteSparseMatrix
isreplacedwithPCIe4.0,(3)EMOGIremainsperformantevenwith
Collection[18]andSK,andUK5arecommonlyusedlargegraphs
thelatestgenerationofGPUNVIDIAAmpereA100[6]andachieves fromLAW[13].Thiscollectionofgraphscoversdatafromdifferent
betterscalingcomparedtotheUVMoptimizedimplementation.
areassuchasbiomedicine,socialnetworks,webcrawls,andeven
syntheticgraphs.Allthegraphs,exceptforSKandUK5,areundi-
5.1 ExperimentSetup
rected.WeusethedefaultweightsforGU,GK,andMLgraphswhile
5.1.1 SystemOverview: WeuseaCascade-lakeservermachine werandomlyinitializeweightsfortherestofthegraphfromthe
withtwo20coreIntelXeonGold6230CPUsequippedwith256GB integervaluesbetween8to72.Theaveragedegreeofthegraphs
| of DDR4 | 2933MHz | memory | and an NVIDIA | Tesla | SXM2 | V100 |     |     |
| ------- | ------- | ------ | ------------- | ----- | ---- | ---- | --- | --- |
is38,exceptfortheMLgraph,whichhasanaveragedegreeof
16GBGPUasourevaluationplatform.Thesystemisconfiguredas
222.ForfairBFSandSSSPperformanceevaluations,wepick64
showninFigure2.WeusetheFPGAonlytoanalyzethezero-copy
randomverticesfromeachgraphasthestartingsourcesandreuse
memoryaccesspatternacrossdifferentgraphs.Thedetailedsystem theselectedverticesforallmeasurements.Thefinalexecutiontime
specificationisprovidedinTable1.Graphedgelistsarestoredin iscalculatedbyaveragingtheexecutiontimesofthe64cases,but
thehostmemorywhilethevertexlistandothertemporarydata someresultsareremovedfromtheaveragewhentheselectedver-
structuresarestoredintheGPUmemory.
ticeshavenooutgoingedges.Edgeweightvaluesareonlyusedby
theSSSPalgorithm.
| 5.1.2 | Systems | Compared: | To show the | performance | benefit | of  |     |     |
| ----- | ------- | --------- | ----------- | ----------- | ------- | --- | --- | --- |
EMOGI,weusethreedifferentgraphtraversalalgorithms:Breadth-
|     |     |     |     |     |     |     | 5.3 Case-Study:Breadth-FirstSearch |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------- | --- |
FirstSearch(BFS),Single-SourceShortestPath(SSSP),Connected
Components(CC),andPageRank(PR)[46].Webaseourinitial Inthissection,wetakeBFSasanexampleandthoroughlyevaluate
implementationofBFSandSSSPfrom[32,43],CCbaselineimple- PCIetrafficforrequestsizedistribution,achievedbandwidth,and
mentationfrom[64],andPRbaselineimplementationfrom[44]. thetotalamountofdatatransferred.Throughouttheevaluation,
WecompareEMOGIwiththefollowingsystems: weusetheUVMimplementationasthebaseline.
120

Table2:GraphDatasets.𝑉 =Vertex,𝐸=Edge,and𝑤=Weight. 1.1E+09 3.9E+09 1.4E+09 6.0E+09 1.2E+09 2.1E+09
1E+09
s
ts
e u8E+08
|      |       |     |     | Number | Size(GB)    | q      |     |     |     |     |     |
| ---- | ----- | --- | --- | ------ | ----------- | ------ | --- | --- | --- | --- | --- |
| Sym. | Graph |     |     |        |             | e      |     |     |     |     |     |
|      |       |     |     | |𝑉|    | |𝐸| |𝐸| |𝑤| | R6E+08 |     |     |     |     |     |
 e
IC
| GK  | GAP-kron[12] |     | 134.2M |     | 4.22B 31.5 15.7 | P4E+08 |     |     |     |     |     |
| --- | ------------ | --- | ------ | --- | --------------- | ------ | --- | --- | --- | --- | --- |
 fo
| GU  | GAP-urand[12] |     | 134.2M |     | 4.29B 32.0 16.0 |     |     |     |     |     |     |
| --- | ------------- | --- | ------ | --- | --------------- | --- | --- | --- | --- | --- | --- |
 re
| FS  | Friendster[65] |     | 65.6M |     | 3.61B 26.9 13.5 | 2E+08 |     |     |     |     |     |
| --- | -------------- | --- | ----- | --- | --------------- | ----- | --- | --- | --- | --- | --- |
b m
| ML  | MOLIERE_2016[61] |     | 30.2M |     | 6.67B 49.7 24.8 |     |     |     |     |     |     |
| --- | ---------------- | --- | ----- | --- | --------------- | --- | --- | --- | --- | --- | --- |
u N0E+00
|     |     |     |     |     |     |  la | e d d e d | d e d d | e d d e | d d e | d d |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------- | ------- | ----- | --- |
S K sk - 2 0 0 5 [ 1 4– 1 6 ] 5 0 .6 M 1 . 9 5 B 1 4 . 5 7 .3 v e e v e e v e e v e e v e e v e e
|     |     |     |     |     |     | to  | ïa g re n g ïa g re | n g ïa g re n g | ïa g re n g ïa | g re n g ïa | g re n g |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --------------- | -------------- | ----------- | -------- |
U K 5 u k - 2 0 0 7- 0 5 [1 5 , 16] 1 0 5 .9 M 3 . 7 4 B 2 7 . 8 1 3 .9 T N M ilA N M ilA N M ilA N M ilA N M ilA N M ilA
|     |     |     |     |     |     |     | +     | + + | +   | +   | +   |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- |
|     |     |     |     |     |     |     | GK GU | FS  | ML  | SK  | UK5 |
100%
n Figure 7: Number of PCIe requests sent for Naive, Merged and
o itu
| 80% |     |     |     |     |     | Merged+AlignedimplementationswhileexecutingBFSonvarious |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------------------------------- | --- | --- | --- | --- | --- |
b irts
|     |     |     |     |     |     | g r a ph . C | o ll e c te d f ro m F | P G A . M e r g ed o | p ti m i za ti o | n r e du c e s | t he P C I e |
| --- | --- | --- | --- | --- | --- | ------------ | ---------------------- | -------------------- | ---------------- | -------------- | ------------ |
iD 60%
|     |     |     |     |     |     | m e m o r y | r e q u e st s b y u | p t o 8 3 . 3 % c o | m p ar e d t o | t h e N a i | v e im p l e - |
| --- | --- | --- | --- | --- | --- | ----------- | -------------------- | ------------------- | -------------- | ----------- | -------------- |
 e
z 40% mentation. Merged+Aligned optimization can further reduce the
iS
|  s  |     |     |     |     |     | PCIememoryrequestsbyupto28.8%.+Alignedisabbreviationfor |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------------------------------- | --- | --- | --- | --- | --- |
s
| e c 20% |     |     |     |     |     | Merged+Aligned. |     |     |     |     |     |
| ------- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- |
c
A
0%
|     | e d d e | d d | e d d | e d d | e d d e d d |     |     |     |     |     |     |
| --- | ------- | --- | ----- | ----- | ----------- | --- | --- | --- | --- | --- | --- |
v e e v e e v e e v e e v e e v e e sizes for all the PCIe requests from the three implementations:
|     | ïa g re n g ïa | g re n g | ïa g re n g | ïa g re n g | ïa g re n g ïa g re n g |     |     |     |     |     |     |
| --- | -------------- | -------- | ----------- | ----------- | ----------------------- | --- | --- | --- | --- | --- | --- |
N ilA N ilA N ilA N ilA N ilA N ilA Naive,Merged,andMerged+Aligned.
|     | M   | M   | M   | M   | M M |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
+ + + + + + WeobserveinFigure5thatnearlyallPCIerequestsinthecase
|     | GK  | GU  | FS  | ML  | SK UK5 |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
ofNaiveimplementationareof32-bytegranularity.Thisisbecause
|     | 32-byte | 64-byte | 96-byte | 128-byte |     |     |     |     |     |     |     |
| --- | ------- | ------- | ------- | -------- | --- | --- | --- | --- | --- | --- | --- |
itisonlypossibletogenerateaPCIerequestlargerthan32-bytein
PCIe Read Request Size
theNaiveimplementationwhenmultipleneighborlistshappento
bespatiallynearintheedgelistandtheyareaccessedbymultiple
Figure5:DistributionofPCIereadrequestsizesinBFS.+Aligned
threadsinasinglewarp.However,suchascenarioisextremelyun-
isabbreviationforMerged+Aligned.Asthemergedandalignedop-
likely.Forexample,weobservethatonly1.3%ofthePCIerequests
timizationsareadded,theBFSapplicationgeneratesmore128-byte
requestsforefficientaccess. fromBFSontheFSgraphareofasizebiggerthan32-bytes.
WhenweanalyzetherequestsizedistributionfortheMerged
andMerged+Alignedoptimizedimplementations,weobservethe
|     | 1   |     |     |     |     | following.First,althoughwiththeMergedapproachthepercentof |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --------------------------------------------------------- | --- | --- | --- | --- | --- |
| F   |     |     |     |     |     | 128-byterequestsincreasestoabout40%onaverage,thepercentof |     |     |     |     |     |
D
C 0.8
|  s  |     |     |     |     |     | 128-byterequestsisslightlyhigherthanaveragefortheMLgraph, |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --------------------------------------------------------- | --- | --- | --- | --- | --- |
e
g d 0.6 at about 46.7%. Second, when using the +Aligned approach on
E
 fo g ra p h s t h at h a v e m o st of t h e ir e d g e s a s so c ia te d w i th h i g h - d e g re e
0.4
 re v e rt i ce s , w e e x p ec t th at m o s t ze r o - c o p y m e m o ry r e qu e s t s s h o u ld
b
m 0.2 befor128-bytes.Thisisexpectedbecauseinthe+Alignedimple-
u
N
mentation,zero-copymemoryrequestsaremergedandalignedto
0
0 16 32 48 64 80 96 128-bytegranularitywheneverpossible.Weobservethisbehavior
Degree of Vertex formostgraphsinFigure5.Forexample,thepercentof128-byte
requestsimprovesby1.86×fortheGKgraphbetweentheMerged
GK GU FS ML SK UK5 and+Alignedimplementations.However,thepercentof128-byte
requestsimprovesbyonly1.25×betweenthetwoimplementations
Figure6:NumberofedgesCDFofevaluationgraph.Thisplotpro- ontheGUgraph,agraphthathasasimilarnumberofedgesand
videsusabetterunderstandingofthedistributionoftheneighbor verticesastheGKgraph.
listsizesinthegraphs.Forexample,theGUgraphhasallofitsedges To further analyze these behaviors, we plot in Figure 6, the
associatedwithverticeswithdegreebetween16and48,meaningthe cumulativedistributionfunction(CDF)onthenumberofedges
neighborlistscontainatmost48neighbors.
ineachgraph.CDFonthenumberofedgesprovidesusabetter
understandingofthedistributionoftheneighborlistsizesinthe
5.3.1 Zero-copyRequestSizeDistribution: Inthisevaluation,we graph.ThehorizontalaxisofthisCDFiscutto96asmanyofthe
showtheimpactofoptimizingthememoryaccesspatternfrom§3.3 graphshaveverticeswithanextremelyhighdegree.FromFigure6,
ongeneratingdifferentsizesofPCIerequest.Thehistogramofthe weseethattheMLgraphhasnearlynoedgesassociatedwithsmall
PCIerequestsizeisgatheredusingtheFPGAmonitoringplatform degreevertices.Thus,withtheMergeoptimizationmanyrequests
explainedin§3.2.InFigure5,weshowthebreakdownofrequest canbemergedto128-bytesfortheMLgraph.Theothergraphs,like
121

FS,havesomeedgesassociatedwithsmalldegreevertices.Thus
14
notalloftheirrequestscanbemerged.Duetothefactthatmost )s cudaMemcpy Peak
/B12
| verticeshavelongneighborlistsintheMLgraph,the+Aligned |     |     |     |     | G   |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
(
 h 10
| optimizationfurthermaximizesthe128-bytezero-copyaccesses, |     |     |     |     | td  |     |     |     |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
iw 8
asshowninFigure5,and,asaresult,reducesthetotalnumberof
d
| zero-copymemoryrequestsby28.8%,asshowninFigure7. |     |     |     |     | n a 6 |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | ----- | --- | --- | --- |
B
| TounderstandwhytherequestsizedistributionofGKandGU         |     |     |     |     |  e 4 |     |     |     |
| ---------------------------------------------------------- | --- | --- | --- | --- | ---- | --- | --- | --- |
| graphsaresignificantlydifferentforthe+Alignedoptimization, |     |     |     |     | g a  |     |     |     |
re 2
| weneedtounderstandtheneighborlistsizedistributionsofthese |     |     |     |     | v   |     |     |     |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
A 0
graphs.TheneighborlistsoftheGKgraphareextremelyunbal- GK GU FS ML SK UK5
ancedwhiletheGUgraphhasuniformlylowdegreesvaryingfrom
|     |     |     |     |     | UVM | Naïve Merged | Merged + Aligned |     |
| --- | --- | --- | --- | --- | --- | ------------ | ---------------- | --- |
16to48.Ifweassumethestartinglocationofeachneighborlistis
uniformlyrandom,thenthechanceofeachneighborliststartingat
Figure8:AveragePCIe3.0x16bandwidthutilizationofthedifferent
theexact128-byteboundaryisonly6.25%whenthedatatypesize
implementationsexecutingBFS.
is8-bytes.Therefore,inmostcases,theneighborlistsofgraphsare
77
| notalignedatthe128-byteboundarybydefault.Iftheneighbor |     |     |     |     | ee  |     |     |     |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- |
cc 66
| listsizesareextremelyunbalanced,likeinGK,thenthemisalign- |     |     |     |     | nn aa    |     |     |          |
| --------------------------------------------------------- | --- | --- | --- | --- | -------- | --- | --- | -------- |
|                                                           |     |     |     |     | mm       |     |     | 33..2244 |
| mentislessproblematicsincetheverticeswithhighdegreescan   |     |     |     |     | rroo 55  |     |     |          |
|                                                           |     |     |     |     | ffrree44 |     |     | 33..5566 |
amortizethecostoftheone-timemisalignmentfix.However,ifall
PP
  dd33
| verticeshaveuniformlylowdegrees,likeinGU,thenthereisno   |     |     |     |     | ee       |     |     |          |
| -------------------------------------------------------- | --- | --- | --- | --- | -------- | --- | --- | -------- |
|                                                          |     |     |     |     | zz       |     |     | 00..7733 |
| opportunitytoamortizethecostoftheone-timemisalignmentfix |     |     |     |     | iillaa22 |     |     |          |
mm
| pervertex.Duetothis,amongallthegraphsevaluated,onlyGU |     |     |     |     | rroo11 |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | ------ | --- | --- | --- |
NN
| showsverylittleimprovementwiththe+Alignedoptimization. |     |     |     |     | 00   |           |                  |        |
| ------------------------------------------------------ | --- | --- | --- | --- | ---- | --------- | ---------------- | ------ |
|                                                        |     |     |     |     | GGKK | GGUU FFSS | MMLL SSKK UUKK55 | AAvvgg |
Thebandwidthswemeasuredare
5.3.2 PCIeBandwidthAnalysis:
|     |     |     |     |     |     | UUVVMM NNaaïïvvee MMeerrggeedd | MMeerrggeedd++AAlliiggnneedd |     |
| --- | --- | --- | --- | --- | --- | ------------------------------ | ---------------------------- | --- |
moreorlessalignedwithPCIerequestsizedistributions.InFigure8,
weshowtheaverageachievedPCIebandwidthwhileexecuting Figure9:BFSperformanceoftheNaive,MergedandMerged+Aligned
BFS.WemeasuredthemaximumachievablePCIebandwidthwith implementationsagainsttheUVMbaseline.
cudaMemcpy()tobe12.3GB/s.Becauseofthepagefaultingover-
6
| head present | in the UVM, | it can only | achieve PCIe | bandwidth | e   |     |     |     |
| ------------ | ----------- | ----------- | ------------ | --------- | --- | --- | --- | --- |
z iS5
| o f 9 G B / s. | E M O G I ’ sN a | i v e i m p l e m e n | t a ti o n of BF S c | an o n l y r ea c h |  te |     |     |     |
| -------------- | ---------------- | --------------------- | -------------------- | ------------------- | --- | --- | --- | --- |
sa 4
| u p t o 4 .7 | G B /s P C I e b a | n d w i dt h . T h i s | i s i n sy nc w it | h w h a t w e o b - | ta  |     |     |     |
| ------------ | ------------------ | ---------------------- | ------------------ | ------------------- | --- | --- | --- | --- |
D3
| s e r v e d u | s i n g t h e t o y e | x a m p l e in F i g | u r e 4 . W i th t | h e m e r g e o p t i- |  / d |     |     |     |
| ------------- | --------------------- | -------------------- | ------------------ | ---------------------- | ---- | --- | --- | --- |
2
| m i z a t i o n | , t h e P C I e b a n | d w id t h u t il iz a | t io n in c r e a s e d | u p t o 1 1G B / s , | e rre |     |     |     |
| --------------- | --------------------- | ---------------------- | ----------------------- | -------------------- | ----- | --- | --- | --- |
| re a c h i n g  | a b o u t 9 0 % o f   | th e p e ak            | b a n                   | d w i d th . W it h  | fsn 1 |     |     |     |
|                 |                       | c u d                  | a M e mc p y ( )        |                      | a     |     |     |     |
rT 0
| t h e M e r g | e d + A l i gn e d o | p t i m iz a t io n ,w | e a d d a b o u t 0  | .5 t o 1 G B / so f   |  a    |       |       |     |
| ------------- | -------------------- | ---------------------- | -------------------- | --------------------- | ----- | ----- | ----- | --- |
|               |                      |                        |                      |                       | ta GK | GU FS | ML SK | UK5 |
| a d di ti o n | a l b a n d w id t h | u t il i za ti o n o n | to p o f m e r g e o | p ti m iz a t io n in | D     |       |       |     |
allcases.TheGUgraphhastheleastamountofimprovementfrom UVM EMOGI
thealignmentoptimizationamongallgraphs.ThisisbecauseBFS
ontheGUgraphcannotsendenoughnumberof128-byterequests Figure10:I/OReadAmplificationofEMOGIandtheUVMbaseline
whileperformingBFS.
tosaturatePCIeinterconnectbandwidth.BycomparingFigure5
andFigure8,wecanclearlyseethecorrelationbetweenthedistri- canalmostfitinthe16GBGPUmemory.Whenweaddmemory
butionofPCIerequestsizesandtheachievedbandwidthsinareal accessalignmentoptimizationontopofmergingofrequestwith
application,thusconfirmingourtheanalysisin§3.3. theMerged+Alignedimplementation,wenoticea1.10×improve-
mentinperformanceovertheMergedimplementationonaverage.
Wenextevaluatethe
5.3.3 AnalysisofZero-copyOptimizations: Thisimprovementcanbeassociatedwiththereducednumberof
performancedifferencebetweenNaive,MergeandMerge+Aligned
PCIerequeststhatgoouttothezero-copymemorybecauseofthe
implementationofBFSonvariousgraphsandcompareitwiththe
Merged+Alignedoptimization,aswasshowninFigure7.
UVMimplementation.Theperformanceismeasuredbasedonthe
traversededgespersecond(TEPS)andisinverselyproportional WenowdemonstratetheI/Oread
5.3.4 I/OReadAmplification:
totheexecutiontime.AsshownintheFigure9,theNaiveimple- amplificationbenefitofEMOGI’sfine-granulardataaccessesover
mentation’sperformanceis0.73×ofthatofUVMonaverage.As the4KBpagemovementinUVMinBFSgraphtraversal.Forthis
discussedin§3.3,thisisexpectedastheNaiveimplementation experiment,wechosetheMerge+AlignedEMOGIimplementation
doesnotusethePCIebandwidthefficiently.Ontheotherhand, torepresentEMOGIasitprovidesthebestperformance.Figure10
mergingrequeststhatgotozero-copymemorywiththeMergedim- showstheratioofdatareadfromthehostmemoryoverthedataset
plementationprovidesaspeedupof3.24×overtheUVMbaselineon sizewhileperformingBFSusingUVMandEMOGIoneachgraph.
average.FortheSKgraph,theperformancegainusingtheMerged UVMgenerallyhasaveryhighI/Oreadamplificationfactor,up
optimizationisonly1.21×overUVM.ThisisbecausetheSKgraph to5.16×fortheFSgraph,asforthesegraphs,theneighborlists
122

ofSSSPandBFS,aspecificvertexisselectedasarootvertexand
7
e the applications start traversing the entire graph from the root
c n6
a vertex. However, with CC and PR, instead of picking a specific
m5
ro vertextostartwith,allverticesaresetasrootverticesandthe
fre 4
P entireedgelististraversed.Inthiscase,theapplicationdataaccess
d3
e z ila m1 2 1 .0 3 5 .0 3 1 4 .3 3 0 .9 1 2 .2 1 0 .1 5 2 .1 1 7 .4 1 9 .6 1 3 .2 1 9 .1 3 .9 3 .0 1 5 .8 6 .6 7 .0 2 3 .8 1 2 5 .7 8 1 7 .0 9 1 5 .4 0 .2 4 1 p lo a c t a te li r t n y i w s h si e m n il c a o r m to pa st r r e e d am to in th g e th o e th e e d r g a e p l p is l t ic r a e t s i u o l n ti s n a g n i d n l m es o s r I e /O sp r a e ti a a d l
ro
N0 amplificationforUVM.
K U S L K 5 K U S L K 5 K U S L K U S K 5 g
G G F M S K U G G F M S K U G G F M G G F S K U v A UsingsmallerdatatypescanreducetheoverallPCIetrafficand
SSSP BFS CC PR thereforereducetheoverallexecutiontimeaswell.InFigure12,
weshowtheperformancecomparisonofEMOGIwhenusing4-
UVM EMOGI byteedgelistvs.8-byteedgelist.Onaverage,weobserveabout
1.57×ofperformancedifferencewhenusing4-byteover8-byte
Figure11:PerformancecomparisonbetweenUVMandEMOGIwith
forEMOGI.IncaseofGKandMLgraphsinCC,theperformance
differentgraphtraversalapplicationswithV100.Actualexecution
differencesarenearly2×.TheperformancedifferencesinSSSPare
timesofUVMcasesarewrittenontopofthebars(inseconds).
relativelysmallercomparedtotheotherapplicationssinceSSSP
needs to transfer the weight values as well. Due to the higher
2
e computationtomemoryratioinPR[9],PRalsoshowsrelatively
c
n
a m
ro fre 1
0
.1 1
1
.5 3 5 .9 8 .7 5 .5
3
.1 1 1 .3 3 .3 7 .2 9 .4 5 .1 0 .3 9 .5 6 .6 1 .5
6
.4 1
7 .8
2 1
1 .3
0 1
6
.8 9
6
.3 1
2
.2 5
smallerperformancedifferences.
P
d
5.5 ComparisonwithPreviousWorks
e
z ila Inthissection,wecompareEMOGIwiththecurrentstate-of-the-art
m ro
N
0 K
G
U
G
S
F
L
M
K
S
5
K U
K
G
U
G
S
F
L
M
K
S
5
K U
K
G
U
G
S
F
L
M
K
G
U
G
S
F
K
S
5
K U
g
v A
G
Su
P
b
U
w
s
a
o
y
lu
[
t
5
i
2
o
]
n
.
s
D
fo
u
r
e
o
to
ut
t
-
h
o
e
f-
i
m
rv
e
a
m
r
o
y
r
in
y
g
gr
r
a
u
p
n
h
tim
tra
e
v
r
e
e
r
q
sa
u
l
i
s
r
,
e
H
m
A
en
L
t
O
s,
[
w
23
e
]
a
a
l
n
so
d
SSSP BFS CC PR
modifyourEMOGItestingenvironmentforaccuratecomparisons.
EMOGI + 8B Edge EMOGI + 4B Edge The details of the modifications are described in the following
sections.
Figure12:Performancecomparisonbetweenusing4Bedgeand8B
edgeforEMOGIwithV100.ActualexecutiontimesofEMOGI + 8B
5.5.1 HALO. HALOproposesanewCSRreorderingmethodto
casesarewrittenontopofthebars(inseconds).
improvedatalocalityanddatatransferduringgraphtraversalwith
UVM.SincethesourcecodeoftheHALOisnotpubliclyavailable,
accessedduringtraversalareindifferentlocationsinmemoryand
we compare EMOGI with the results available in the published
thusthereisverylittlespatiallocalityexploitedforeach4KBpage
paper.AsHALO’sresultsweregatheredusingaTitanXpGPU,
moved.However,thetwonotableexceptionstothisaretheML
wealsouseaTitanXpinsteadofV100forfaircomparisonand
andSKgraphsasUVM’sI/Oreadamplificationfactorforthemis
re-measureourexecutiontimes.Thecomparisonresultsareshown
2.28×and1.14×,respectively.Thisisbecausetheaveragedegree
intheTable3.Overall,EMOGIshows1.34×to3.19×ofspeedups
ofavertexintheMLgraphis222andtheSKgraphissosmall
againstHALO.
thatitcanalmostfitinGPUmemory,thusmakingUVM’spage
movementsalittlemoreefficientinbothcases.Incontrast,EMOGI’s 5.5.2 Subway. Subwayproposesadesignofgraphpartitioning
I/Oreadamplificationfactordoesn’texceed1.31×.Thisisbecause thatpreprocessestodeterminetheactivenessofavertex.Insteadof
thefine-granular,merged,andaligneddataaccesstozero-copy relyingonUVM,Subwayfocusesongeneratingatemporalsmall
memoryallowEMOGItoefficientlymoveonlythenecessarybytes CSR(alsocalledsubgraph)thatfitsintheGPUmemoryineach
overtheslowPCIeinterconnect. iteration.SincetheoriginalCSRislocatedinthehostmemory,
CPUs need to be in charge of generating the temporal CSR for
5.4 BeyondBFS everyiteration.TotransferthenewtemporalCSR,cudaMemcpy()
Inthissection,weapplyEMOGI’soptimizationtechniquestoother iscalledbythehostprogram.
graphtraversalapplicationsandmeasuretheirexecutiontime.In WeevaluateSubwayusingallthepubliclyavailablesourcecodes
additiontoBFSfromtheprevioussections,weaddthesingle-source (SSSP,BFS,andCC)withourplatformdescribedin§5.1.Sinceone
shortestpath(SSSP),connectedcomponents(CC),andPageRank ofthegoalsofEMOGIistoavoidanydatamanipulation,weinclude
(PR)applications.WedonotevaluatetheperformanceofCCwith thesubgraphgenerationtimeofSubwayaswellinourmeasure-
SKandUK5graphsasthesegraphsaredirected.ForPR,wedonot ments.ThepubliclyavailableimplementationofSubwayfailsto
evaluateMLgraphasitisamultigraph.Theoverallperformance executeontheGUgraphduetounidentifiedCUDAout-of-memory
resultsareshowninFigure11. errorsanditcannotexecuteontheMLgraphastheframework
EMOGIprovidesthebestperformanceforallthegraphtraversal currentlysupportsamaximumof232edges.Thecomparisonresults
applicationsandgraphdatasetswestudied.Onaverage,EMOGIis areshownintheTable4.Overall,acrossallthegraphdatasetsand
2.60×fasterthanUVM.ForCCandPR,EMOGIshowsrelatively graphtraversalalgorithms,EMOGIobservesspeedupsof1.57×to
lowerspeed-upsoverUVMthantheotherapplications.Inthecase 4.73×.
123

12
e
c n10
a
m 8
ro
fre 6
P
d e z 2
4 11
..00 33
66 ..99
22 11
55
..33 33
33
..99 11
77
..11 11
77
..99 44
88
..00 11
77
..33 11
33
..66 11
44
..22 11 88 ..11 88 ..88 99 ..99 88 ..77 55 ..66
55
..00 22
00 ..77
88 11
00 ..55
55 11
99 ..33
66 11 33 ..33
55 ..33
22 11
ila
m 0
ro GK GU FS ML SK UK5 GK GU FS ML SK UK5 GK GU FS ML GK GU FS SK UK5 Avg
N SSSP BFS CC PR
UVM + PCIe 3.0 UVM + PCIe 4.0 EMOGI + PCIe 3.0 EMOGI + PCIe 4.0
Figure13:PerformancecomparisonbetweenUVMandEMOGIusingPCIe3.0andPCIe4.0.AllresultsaremeasuredinDGXA100.Actual
executiontimesofUVM + PCIe 3.0casesarewrittenontopofthebars(inseconds).
5.6 PerformanceScalingwithPCIe4.0 Table3:ExecutiontimecomparisonwithHALO[23].NVIDIATitan
Xp(12GB)used.
Aswasshownin§5.3.2and§5.3.3,EMOGIcannearlysaturatethe
PCIe3.0bandwidthwhileout-performingtheUVMimplementation.
NVIDIA’slatestGPU,theAmpereA100,communicateswiththe Application Graph Exe.Time Speedup
hostmemoryoverthePCIe4.0interconnect.PCIe4.0’smeasured HALO EMOGI
peakbandwidth,approximately24GB/s,istwiceasmuchasPCIe ML 9.54s 4.43s 2.15×
3.0’speakmeasuredbandwidthofapproximately12GB/s.Inthis FS 8.27s 2.59s 3.19×
BFS
section, we study the ability of both UVM and EMOGI to take SK 2.17s 1.62s 1.34×
advantageoftheincreasedbandwidthinaccessingthehostmemory. UK5 6.03s 4.00s 1.51×
Tothisend,weuseaDGXA100machine[7]withtheA100GPUand
DualAMDRome7742CPUspairedwith1TBofsystemmemory.
Table 4: Execution time comparison with Subway [52]. NVIDIA
ThismachineallowsustoswitchtherootporttorunineitherPCIe
TeslaV100(16GB)used.4-byteedgeusedduetotheSubwayrequire-
3.0modeorPCIe4.0mode.NeithertheEMOGIimplementation
ment.
northeUVMimplementationwasre-optimizedfortheA100GPU
intheseexperiments.A100memoryisthrottledto16GB.
Exe.Time
Theoverallevaluationresultscomparingtheperformanceof Application Graph Speedup
Subway EMOGI
UVMandEMOGIontheDGXA100systemareshowninFigure13.
Here,wenormalizetheperformancespeed-upachievedbyeach GK 20.96s 7.94s 2.64×
configurationtotheUVMimplementationrunningontheA100 FS 14.95s 6.97s 2.14×
SSSP
GPUwiththePCIe3.0interconnect.WhileEMOGI’sperformance SK 8.99s 3.92s 2.30×
scalesby1.88×onaveragewiththefasterinterconnect,UVM’s UK5 25.78s 8.08s 3.19×
performancescalesbyonly1.53×onaverage.Thisisbecausethe
GK 6.88s 1.66s 4.14×
UVMimplementationsuffersfrompagefaulthandlingoverhead
FS 4.22s 1.49s 2.83×
whenaccessingpagesoftheedgelistinhostmemory.Thepage BFS
SK 1.69s 0.85s 1.99×
faulthandlerispartoftheUVMdriverrunningontheCPUand
UK5 8.75s 1.85s 4.73×
can’tkeepuptomakeuseofthehigherbandwidthofthePCIe4.0
interface.However,EMOGIdoesn’tsufferanypagefaultingover- GK 6.34s 3.11s 2.04×
CC
headastheedgelistispinnedinhostmemory,leadingtoEMOGI’s FS 4.31s 2.75s 1.57×
performancescalingalmostlinearlywiththePCIebandwidth.
worksarenotstrictlyidenticaltotheclassicalCSRformat,buttheir
6 DISCUSSION fundamentalstructuresresembleCSRtoretainsomelevelofdata
Extendingtootherinputformats:Inthispaper,EMOGIistar- localityforbetterbandwidthutilization.Therefore,theEMOGI’s
getingCSRwhichisusedbymanypopulargraphprocessingframe- zero-copymemoryaccessoptimizationstrategiescanbeappliedto
works[1,43,44,58,63],butthemainideaofEMOGIcanbeex- theseformatsaswell.
tendedtodifferentformatsaswell.Themostimmediateapplicable Additionaloptimizations:Thereareseveraladditionalopti-
formatiscompressedsparsecolumn(CSC).TheedgelistsinCSR mizationsavailableforEMOGIsuchasdatacompressionanddata
representoutgoingedges(push-based),buttheedgelistsinCSC cachinginGPUglobalmemory.Datacompressionongraph[33,57]
representincomingedges(pull-based).Althoughthedirectionsare canreducethetotalamountdatatransferredtoGPUandwecan
differentbetweentheCSRandCSC,thememoryaccesspatternto obtainasimilareffecttoincreasingtheexternalinterconnectband-
theedgelistsinbothinputformatsisidentical.Anotherinteresting width.Asdiscussedin§4.3,GPUisseverelyunderutilizeddue
formatexpansionforEMOGIwouldbedynamicgraphs[56]and tothelowexternalinterconnectbandwidth.ThustheidlingGPU
compressedgraphs[33,57].Thegraphinputformatsusedinthese corescanbepotentiallyusedtodecompressdatafromthehost
124

memory,withoutinterferingwiththeoriginalgraphtraversing lowforgraphtraversalapplications.Asshownin§5,bycarefully
process.Fordatacaching,aworksimilarto[38,66]canbeapplied re-orchestratingthememoryaccesspatternusingdirectaccess,
toexploitdatalocalityfurther.Forthisoptimization,weexpect EMOGIisabletoboostgraphtraversalexecutionperformancefor
thataworkloadwithhighvertexrevisits,suchasPR,wouldbenefit largegraphswithoutanyadditionaloptimizations.Indeedtheprior
themost.However,onethingtonoteisthatcurrentlythereisno proposedsoftwareandhardwareoptimizationscanbeexploitedby
fullhardware-basedmechanismtonaturallyusetheGPUglobal EMOGI.Weleavethisasfutureresearch.Also,EMOGIcouldbe
memoryasalargecacheandthereforeasoftware-basedcaching easilyincorporatedintoalibrarytolessentheprogrammer’seffort
mechanismneedstobeimplemented. andprovideout-of-theboxperformanceimprovements.
Multi-GPU and Collaborative CPU-GPU: Aside from sin-
gleGPUgraphtraversal,priorworkshaveproposedusingmulti-
7 RELATEDWORKS GPU[35,48,63,69]andcollaborativeCPU-GPUcomputationto
Graph Analytics on CPU: Efficient graph traversal algorithm meettheneedsoflargegraphscomputation[24,25,40,41,62].
implementation on CPUs have been extensively studied in the Multi-GPU and collaborative CPU-GPU computing are enabled
past[26,44,49,54,58–60].Wenotethatfromthesestudiestwo usingUVMwherehardwaremovesthepageson-demandacross
popularframeworksGalois[44]andLigra[58]haveemerged.To differentcomputingblocks.EMOGIcanbeextendedtosupport
compensatethelowparallelismofCPU,theseframeworkssupport bothmulti-GPUandhybridCPU-GPUcomputingandweleaveit
theworkloadscalingtomulti-CPUsystemssuchasnon-uniform asfutureresearch.
memoryaccess(NUMA)nodes.However,thefocusoftheseprior Architectural support for improving UVM: Besides algo-
work has been on efficient graph partition and data allocation rithmandsystem-levelchanges,priorworksalsoproposehard-
schemesacrossdifferentnodestominimizethenode-to-nodedata warechangesthatcanenableexecutinggraphtraversalalgorithms
movements.Therefore,itisinevitabletodoapre-processingfor efficientlyonlargegraphs.Specifically,memorycompressiontech-
efficientdataorganization.Besidetheframeworks,thereareother niquestoreducethememoryfootprintintheGPU[39],efficient
numerousworks[26,49,54,59,60]basedonCPU. migrationpoliciesusinghardwarecounters,andoptimizedprefetch-
GraphAnalyticsonGPU:Graphtraversalalgorithmssuch ingschemes[10,11,21],andsoftware-hardwareco-designusing
asBFSexhibitamassiveamountofparallelism.Thishasledto memoryhintsareproposed[3,6].Thesetechniquesareorthog-
increasingresearchinleveragingthemassivecomputationpower onaltoEMOGIandcanbeleveragedbyEMOGItogainfurther
offeredbyGPUstospeedupgraphanalytics.Priorworkfocusedon performanceimprovementsinfutureGPUarchitectures.
improvingtheperformanceofgraphtraversalalgorithmseitherby
makingGPUspecificalgorithmicimprovements[20,31,36,42,63,
67,69]orbyperformingdatatransformations[45,47].However, 8 CONCLUSION
mostoftheseworksassumegraphsfitintheGPUmemory. Inthiswork,wepresentEMOGI,anewmethodforoptimizingthe
Practicalgraphs,ontheotherhand,oftencannotfitintotheGPU traversalofverylargegraphswithaGPUusingzero-copy.Using
memory.Webgraphs[15,16],socialnetworkgraphs[65]andbio- thoroughanalysisoffine-grainedGPUmemoryaccesspatterns
medicalgraphs[12]canbesignificantlylargerthanavailableGPU overPCIetozero-copymemory,weidentifiedkeyoptimizationsto
memory(seeTable2).Toaddressthis,priorworkshaveproposed bestutilizebandwidthtozero-copymemory:mergedandaligned
eithertopartitiontheinputgraphandloadingonlythoseedges memoryaccesses.Weappliedtheseoptimizationstokeygraph
thatareneededduringcomputation[27,52,55,63]orleveraging traversalapplicationstoenableefficientGPUtraversalofgraphs
automaticmemoryoversubscriptionusingUVM[19,23,25,37,39, thatdonotfitinGPUmemory.OurexperimentsshowthatEMOGI
41,50].Forexample,GraphReduce[55]partitionstheoversized out-performsthestate-of-the-artsolutionsfortraversinglarges
graphsanddoesexplicitmemorymanagementbetweentheGPU graphs.ThisisbecauseEMOGIavoidsI/Oreadamplificationby
andthehostmemory.Recently,Subway[52]furtherimprovedthe leveragingefficientfine-grainedaccessestofetchonlytheneeded
design of the input partitioning scheme using GPU-accelerated bytesfromzero-copymemory.Furthermore,EMOGI’sperformance
subgraphgenerationpre-processingtechniquethattracksactive- scalesalmostlinearlywiththeimprovedbandwidthofnewerin-
nessofavertexandalsobygeneratingsubgraphsasynchronously. terconnectsasitisnotbottle-neckedbythepagefaulthandling
EMOGIdoesnotperformanyexplicitmemorymanagementor overheadoftraditionalmethodsusingUVM.
pre-processingofthegraph.
Alternatively,tosupportlargegraphsinGPU,programmerscan
useUVMwhichdoesautomaticmemoryoversubscription[2,3]. ACKNOWLEDGMENTS
Priorworkssuchas[10,11,19,23,25,34,37,39,41,50]haveob- ThisworkwaspartiallysupportedbytheApplicationsDrivingAr-
servedsignificantoverheadfromUVMandhaveproposedopti- chitectures(ADA)ResearchCenterandCenterforResearchonIn-
mizationssuchasoverlappingIOandcomputation[25],memory telligentStorageandProcessing-in-memory(CRISP),JUMPCenters
spaces[19],memorythrottling[39],modifyingdrivertosupport co-sponsoredbySRCandDARPA,IBM-ILLINOISCenterforCog-
largerpagefaultbatchsizes[37]andreorderingofgraphstoen- nitiveComputingSystemsResearch(C3SR).Thisworkwouldnot
hancelocalityinUVM[23].Insteadofleveragingthepreviouslypro- havebeenpossiblewithoutthegeneroushardwaredonationsfrom
posedoptimizations,EMOGItakesastepbackandrevisitstherea- XilinxandNVIDIA.WealsothanktheIMPACTmembers,anony-
soningbehindtheperformancedegradationwithUVM.Like[68], mousreviewers,andashepherdfortheirconstructivefeedbacks,
EMOGI initially observes the PCIe bandwidth utilization being andthechiefeditors’coordinationintheshepherdingprocess.
125

REFERENCES [25] J.Gómez-Luna,I.E.Hajj,L.Chang,V.García-Floreszx,S.G.deGonzalo,T.B.
[1] [n.d.].nvGRAPH.https://developer.nvidia.com/nvgraph. Jablin,A.J.Peña,andW.Hwu.2017.Chai:Collaborativeheterogeneousappli-
[2] 2016.NVIDIATeslaP100ArchitectureWhitepaper.https://www.nvidia.com/ cationsforintegrated-architectures.In2017IEEEInternationalSymposiumon
object/pascal-architecture-whitepaper.html. PerformanceAnalysisofSystemsandSoftware(ISPASS).43–54.
[3] 2017.NVIDIATeslaV100GPUArchitectureWhitepaper.https://images.nvidia. [26] T.J.Ham,L.Wu,N.Sundaram,N.Satish,andM.Martonosi.2016.Graphicionado:
com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf. Ahigh-performanceandenergy-efficientacceleratorforgraphanalytics.In2016
[4] 2020. CUDAC++BestPracticesGuide. https://docs.nvidia.com/cuda/cuda-c- 49thAnnualIEEE/ACMInternationalSymposiumonMicroarchitecture(MICRO).
best-practices-guide/index.html. 1–13.
[5] 2020.Intel®VTune™Profiler.https://software.intel.com/content/www/us/en/ [27] W.Han,D.Mawhirter,B.Wu,andM.Buland.2017.Graphie:Large-ScaleAsyn-
develop/tools/vtune-profiler.html. chronousGraphTraversalsonJustaGPU.InProceedingsof26thInternational
[6] 2020. NVIDIA A100 GPU Architecture Whitepaper. https://www.nvidia. ConferenceonParallelArchitecturesandCompilationTechniques(PACT).233–245.
com/content/dam/en-zz/Solutions/Data-Center/nvidia-ampere-architecture- [28] PawanHarishandP.J.Narayanan.2007.AcceleratingLargeGraphAlgorithms
whitepaper.pdf. ontheGPUUsingCUDA.InProceedingsofthe14thInternationalConference
[7] 2020.NVIDIADGXA100Datasheet.https://www.nvidia.com/content/dam/en- onHighPerformanceComputing(Goa,India)(HiPC’07).Springer-Verlag,Berlin,
zz/Solutions/Data-Center/nvidia-dgx-a100-datasheet.pdf. Heidelberg,197–208.
[8] 2020.PCIe3.0Specification.https://members.pcisig.com/wg/PCI-SIG/document/ [29] MarkHarris.2017.UnifiedMemoryforCUDABeginners.https://devblogs.nvidia.
download/8257. com/unified-memory-cuda-beginners/.
[9] T.K.Aasawat,T.Reza,andM.Ripeanu.2018.HowWelldoCPU,GPUandHybrid [30] K.A.Hawick,A.Leist,andD.P.Playne.2010. ParallelGraphComponent
GraphProcessingFrameworksPerform?.In2018IEEEInternationalParalleland LabellingwithGPUsandCUDA.ParallelComput.36,12(Dec.2010),655–678.
DistributedProcessingSymposiumWorkshops(IPDPSW).458–466. https://doi.org/10.1016/j.parco.2010.07.002
[10] NehaAgarwal,DavidNellans,MarkStephenson,MikeO’Connor,andStephenW. [31] SungpackHong,SangKyunKim,TayoOguntebi,andKunleOlukotun.2011.
Keckler.2015.PagePlacementStrategiesforGPUswithinHeterogeneousMem- AcceleratingCUDAGraphAlgorithmsatMaximumWarp.InProceedingsofthe
orySystems.SIGARCHComput.Archit.News43,1(March2015),607–618. 16thACMSymposiumonPrinciplesandPracticeofParallelProgramming(San
[11] RachataAusavarungnirun,JoshuaLandgraf,VanceMiller,SaugataGhose,Jayneel Antonio,TX,USA)(PPoPP’11).AssociationforComputingMachinery,NewYork,
Gandhi,ChristopherJ.Rossbach,andOnurMutlu.2017.Mosaic:AGPUMem- NY,USA,267–276.
oryManagerwithApplication-TransparentSupportforMultiplePageSizes.In [32] SungpackHong,SangKyunKim,TayoOguntebi,andKunleOlukotun.2011.
Proceedingsofthe50thAnnualIEEE/ACMInternationalSymposiumonMicroarchi-
AcceleratingCUDAGraphAlgorithmsatMaximumWarp.InProceedingsofthe
tecture(Cambridge,Massachusetts)(MICRO-50’17).AssociationforComputing 16thACMSymposiumonPrinciplesandPracticeofParallelProgramming(San
Machinery,NewYork,NY,USA,136–150. Antonio,TX,USA)(PPoPP’11).AssociationforComputingMachinery,NewYork,
[12] ScottBeamer,KrsteAsanovic,andDavidA.Patterson.2015.TheGAPBenchmark NY,USA,267–276.
Suite.CoRRabs/1508.03619(2015).arXiv:1508.03619 http://arxiv.org/abs/1508. [33] KrzysztofKaczmarski,PiotrPrzymus,andPawełRzążewski.2015.Improving
03619 high-performanceGPUgraphtraversalwithcompression. InNewTrendsin
[13] PaoloBoldi,BrunoCodenotti,MassimoSantini,andSebastianoVigna.2004. DatabaseandInformationSystemsII.Springer,201–214.
UbiCrawler:ascalablefullydistributedWebcrawler. Software:Practiceand [34] JensKehne,JonathanMetter,andFrankBellosa.2015. GPUswap:Enabling
Experience34,8(2004),711–726. OversubscriptionofGPUMemorythroughTransparentSwapping. SIGPLAN
[14] PaoloBoldi,BrunoCodenotti,MassimoSantini,andSebastianoVigna.2004. Not.50,7(March2015),65–77.
UbiCrawler:AScalableFullyDistributedWebCrawler. Software:Practice& [35] F.Khorasani,R.Gupta,andL.N.Bhuyan.2015.ScalableSIMD-EfficientGraph
Experience34,8(2004),711–726. ProcessingonGPUs.In2015InternationalConferenceonParallelArchitectureand
[15] PaoloBoldi,MarcoRosa,MassimoSantini,andSebastianoVigna.2011.Layered Compilation(PACT).39–50.
LabelPropagation:AMultiResolutionCoordinate-FreeOrderingforCompressing [36] FarzadKhorasani,KevalVora,RajivGupta,andLaxmiN.Bhuyan.2014.CuSha:
SocialNetworks.InProceedingsofthe20thinternationalconferenceonWorldWide Vertex-CentricGraphProcessingonGPUs.InProceedingsofthe23rdInternational
Web,SadagopanSrinivasan,KrithiRamamritham,ArunKumar,M.P.Ravindra, SymposiumonHigh-PerformanceParallelandDistributedComputing(Vancouver,
ElisaBertino,andRaviKumar(Eds.).ACMPress,587–596. BC,Canada)(HPDC’14).AssociationforComputingMachinery,NewYork,NY,
[16] PaoloBoldiandSebastianoVigna.2004.TheWebGraphFrameworkI:Compres- USA,239–252.
sionTechniques.InProceedingsoftheThirteenthInternationalWorldWideWeb [37] HyojongKim,JaewoongSim,PrasunGera,RamyadHadidi,andHyesoonKim.
Conference(WWW2004).ACMPress,Manhattan,USA,595–601. 2020.Batch-AwareUnifiedMemoryManagementinGPUsforIrregularWork-
[17] S.Che.2014.GasCL:Avertex-centricgraphmodelforGPUs.In2014IEEEHigh loads.InProceedingsoftheTwenty-FifthInternationalConferenceonArchitectural
PerformanceExtremeComputingConference(HPEC).1–6. SupportforProgrammingLanguagesandOperatingSystems(Lausanne,Switzer-
[18] TimothyA.DavisandYifanHu.2011.TheUniversityofFloridaSparseMatrix land)(ASPLOS’20).AssociationforComputingMachinery,NewYork,NY,USA,
Collection.ACMTrans.Math.Softw.38,1,Article1(Dec.2011),25pages. 1357–1370.
[19] H.CarterEdwards,ChristianR.Trott,andDanielSunderland.2014.Kokkos:En- [38] K.Lakhotia,S.Singapura,R.Kannan,andV.Prasanna.2017.ReCALL:Reordered
ablingmanycoreperformanceportabilitythroughpolymorphicmemoryaccess CacheAwareLocalityBasedGraphProcessing.In2017IEEE24thInternational
patterns. J.ParallelandDistrib.Comput.74,12(2014),3202–3216. Domain- ConferenceonHighPerformanceComputing(HiPC).273–282.
SpecificLanguagesandHigh-LevelFrameworksforHigh-PerformanceComput- [39] ChenLi,RachataAusavarungnirun,ChristopherJ.Rossbach,YoutaoZhang,Onur
ing. Mutlu,YangGuo,andJunYang.2019.AFrameworkforMemoryOversubscription
[20] AnilGaihre,ZhenlinWu,FanYao,andHangLiu.2019.XBFS:EXploringRun- ManagementinGraphicsProcessingUnits.InProceedingsoftheTwenty-Fourth
timeOptimizationsforBreadth-FirstSearchonGPUs.InProceedingsofthe28th InternationalConferenceonArchitecturalSupportforProgrammingLanguagesand
InternationalSymposiumonHigh-PerformanceParallelandDistributedComputing
OperatingSystems(Providence,RI,USA)(ASPLOS’19).AssociationforComputing
(Phoenix,AZ,USA)(HPDC’19).AssociationforComputingMachinery,New Machinery,NewYork,NY,USA,49–63.
York,NY,USA,121–131. [40] LingxiaoMa,ZhiYang,HanChen,JilongXue,andYafeiDai.2017. Garaph:
[21] DebashisGanguly,ZiyuZhang,JunYang,andRamiMelhem.2019. Interplay EfficientGPU-AcceleratedGraphProcessingonaSingleMachinewithBalanced
betweenHardwarePrefetcherandPageEvictionPolicyinCPU-GPUUnified Replication.InProceedingsofthe2017USENIXConferenceonUsenixAnnualTech-
VirtualMemory.InProceedingsofthe46thInternationalSymposiumonComputer nicalConference(SantaClara,CA,USA)(USENIXATC’17).USENIXAssociation,
Architecture(Phoenix,Arizona)(ISCA’19).AssociationforComputingMachinery, USA,195–207.
NewYork,NY,USA,224–235. [41] VikramSMailthody,KetanDate,ZaidQureshi,CarlPearson,RakeshNagi,Jinjun
[22] DebashisGanguly,ZZhang,JYang,andRamiMelhem.2020. AdaptivePage Xiong,andWen-meiHwu.2018. Collaborative(CPU+GPU)algorithmsfor
MigrationforIrregularData-intensiveApplicationsunderGPUMemoryOver- trianglecountingandtrussdecomposition.In2018IEEEHighPerformanceextreme
subscription.InProceedingsoftheThirty-forthInternationalConferenceonParallel ComputingConference(HPEC’18).Boston,USA.
andDistributedProcessing(IPDPS). [42] DuaneMerrill,MichaelGarland,andAndrewGrimshaw.2015.High-Performance
[23] PrasunGera,HyojongKim,PiyushSao,HyesoonKim,andDavidBader.2020. andScalableGPUGraphTraversal.ACMTransactionsonParallelComputing1,2,
TraversingLargeGraphsonGPUswithUnifiedMemory.ProceedingsoftheVLDB Article14(Feb.2015),30pages.
Endowment13,7(March2020),1119–1133. [43] LifengNai,YinglongXia,IlieG.Tanase,HyesoonKim,andChing-YungLin.
[24] AbdullahGharaibeh,LauroBeltrãoCosta,ElizeuSantos-Neto,andMateiRipeanu. 2015.GraphBIG:UnderstandingGraphComputingintheContextofIndustrial
2012.AYokeofOxenandaThousandChickensforHeavyLiftingGraphProcess- Solutions.InProceedingsoftheInternationalConferenceforHighPerformance
ing.InProceedingsofthe21stInternationalConferenceonParallelArchitecturesand Computing,Networking,StorageandAnalysis(Austin,Texas)(SC’15).Association
CompilationTechniques(Minneapolis,Minnesota,USA)(PACT’12).Association forComputingMachinery,NewYork,NY,USA,Article69,12pages.
forComputingMachinery,NewYork,NY,USA,345–354. [44] DonaldNguyen,AndrewLenharth,andKeshavPingali.2013. ALightweight
InfrastructureforGraphAnalytics.InProceedingsoftheTwenty-FourthACM
SymposiumonOperatingSystemsPrinciples(Farminton,Pennsylvania)(SOSP’13).
126

AssociationforComputingMachinery,NewYork,NY,USA,456–471. https: [58] JulianShunandGuyE.Blelloch.2013.Ligra:ALightweightGraphProcessing
//doi.org/10.1145/2517349.2522739 FrameworkforSharedMemory.SIGPLANNot.48,8(Feb.2013),135–146. https:
[45] AmirHosseinNodehiSabet,JunqiaoQiu,andZhijiaZhao.2018. Tigr:Trans- //doi.org/10.1145/2517327.2442530
formingIrregularGraphsforGPU-FriendlyGraphProcessing.SIGPLANNot.53, [59] YogeshSimmhan,AlokKumbhare,CharithWickramaarachchi,SoonilNagarkar,
2(March2018),622–636. SantoshRavi,CauligiRaghavendra,andViktorPrasanna.2014. GoFFish:A
[46] LawrencePage,SergeyBrin,RajeevMotwani,andTerryWinograd.1999.The Sub-graphCentricFrameworkforLarge-ScaleGraphAnalytics.InEuro-Par2014
PageRankCitationRanking:BringingOrdertotheWeb.TechnicalReport1999- ParallelProcessing,FernandoSilva,InêsDutra,andVítorSantosCosta(Eds.).
66.StanfordInfoLab. http://ilpubs.stanford.edu:8090/422/Previousnumber= SpringerInternationalPublishing,Cham,451–462.
SIDL-WP-1999-0120. [60] NarayananSundaram,NadathurSatish,MdMostofaAliPatwary,SubramanyaR.
[47] SreepathiPaiandKeshavPingali.2016.ACompilerforThroughputOptimization Dulloor,MichaelJ.Anderson,SatyaGautamVadlamudi,DipankarDas,and
ofGraphAlgorithmsonGPUs.SIGPLANNot.51,10(Oct.2016),1–19. PradeepDubey.2015. GraphMat:HighPerformanceGraphAnalyticsMade
[48] Y.Pan,Y.Wang,Y.Wu,C.Yang,andJ.D.Owens.2017. Multi-GPUGraph Productive.Proc.VLDBEndow.8,11(July2015),1214–1225. https://doi.org/10.
Analytics.In2017IEEEInternationalParallelandDistributedProcessingSymposium 14778/2809974.2809983
(IPDPS).479–490. [61] JustinSybrandt,MichaelShtutman,andIlyaSafro.2017. MOLIERE:Auto-
[49] R.Pearce,M.Gokhale,andN.M.Amato.2010. MultithreadedAsynchronous maticBiomedicalHypothesisGenerationSystem.InProceedingsofthe23rd
GraphTraversalforIn-MemoryandSemi-ExternalMemory.InSC’10:Proceedings ACMSIGKDDInternationalConferenceonKnowledgeDiscoveryandDataMining
ofthe2010ACM/IEEEInternationalConferenceforHighPerformanceComputing, (Halifax,NS,Canada)(KDD’17).AssociationforComputingMachinery,New
Networking,StorageandAnalysis.1–11. York,NY,USA,1633–1642.
[50] CarlPearson,MohammadAlmasri,OmerAnjum,VikramSMailthody,Zaid [62] YuanyuanTian,AndreyBalmin,SeverinAndreasCorsten,ShirishTatikonda,
Qureshi,RakeshNagi,JinjunXiong,andWen-meiHwu.2019.UpdateonTriangle andJohnMcPherson.2013.From“ThinklikeaVertex”to“ThinklikeaGraph”.
CountingonGPU.In2019IEEEHighPerformanceextremeComputingConference ProceedingsoftheVLDBEndowment7,3(Nov.2013),193–204.
(HPEC’19).Boston,USA. [63] YangzihaoWang,AndrewDavidson,YuechaoPan,YuduoWu,AndyRiffel,and
[51] RyanA.RossiandNesreenK.Ahmed.2015.TheNetworkDataRepositorywith JohnD.Owens.2016.Gunrock:AHigh-PerformanceGraphProcessingLibrary
InteractiveGraphAnalyticsandVisualization.InAAAI.http://networkrepository. ontheGPU.InProceedingsofthe21stACMSIGPLANSymposiumonPrinciples
com andPracticeofParallelProgramming(Barcelona,Spain)(PPoPP’16).Association
[52] AmirHosseinNodehiSabet,ZhijiaZhao,andRajivGupta.2020.Subway:Minimiz- forComputingMachinery,NewYork,NY,USA,Article11,12pages.
ingDataTransferduringout-of-GPU-MemoryGraphProcessing.InProceedings [64] ZhenXu,XuhaoChen,JieShen,YangZhang,ChengChen,andCanqunYang.
oftheFifteenthEuropeanConferenceonComputerSystems(Heraklion,Greece) 2017. GARDENIA:ADomain-specificBenchmarkSuiteforNext-generation
(EuroSys’20).AssociationforComputingMachinery,NewYork,NY,USA,Article Accelerators.CoRRabs/1708.04567(2017).arXiv:1708.04567 http://arxiv.org/abs/
12,16pages. 1708.04567
[53] SiddharthaSahu,AmineMhedhbi,SemihSalihoglu,JimmyLin,andM.Tamer [65] JaewonYangandJureLeskovec.2012.DefiningandEvaluatingNetworkCom-
Özsu.2017.TheUbiquityofLargeGraphsandSurprisingChallengesofGraph munitiesbasedonGround-truth.CoRRabs/1205.6233(2012).arXiv:1205.6233
Processing.ProceedingsoftheVLDBEndowment11,4(Dec.2017),420–431. http://arxiv.org/abs/1205.6233
[54] SalmanSalloum,RuslanDautov,XiaojunChen,PatrickXiaogangPeng,and [66] Y.Zhang,V.Kiriansky,C.Mendis,S.Amarasinghe,andM.Zaharia.2017.Making
JoshuaZhexueHuang.2016.BigdataanalyticsonApacheSpark.International cachesworkforgraphanalytics.In2017IEEEInternationalConferenceonBig
JournalofDataScienceandAnalytics1,3-4(2016),145–164. Data(BigData).293–302.
[55] DipanjanSengupta,ShuaiwenLeonSong,KapilAgarwal,andKarstenSchwan. [67] YuZhang,XiaofeiLiao,HaiJin,BingshengHe,HaikunLiu,andLinGu.2019.
2015.GraphReduce:ProcessingLarge-ScaleGraphsonAccelerator-BasedSys- DiGraph:AnEfficientPath-BasedIterativeDirectedGraphProcessingSystem
tems.InProceedingsoftheInternationalConferenceforHighPerformanceCom- onMultipleGPUs.InProceedingsoftheTwenty-FourthInternationalConference
puting,Networking,StorageandAnalysis(Austin,Texas)(SC’15).Associationfor onArchitecturalSupportforProgrammingLanguagesandOperatingSystems
ComputingMachinery,NewYork,NY,USA,Article28,12pages. (Providence,RI,USA)(ASPLOS’19).AssociationforComputingMachinery,New
[56] MoSha,YuchenLi,BingshengHe,andKian-LeeTan.2017.AcceleratingDynamic York,NY,USA,601–614.
GraphAnalyticsonGPUs.Proc.VLDBEndow.11,1(Sept.2017),107–120. https: [68] T.Zheng,D.Nellans,A.Zulfiqar,M.Stephenson,andS.W.Keckler.2016.Towards
//doi.org/10.14778/3151113.3151122 highperformancepagedmemoryforGPUs.In2016IEEEInternationalSymposium
[57] MoSha,YuchenLi,andKian-LeeTan.2019.GPU-BasedGraphTraversalonCom- onHighPerformanceComputerArchitecture(HPCA).345–357.
pressedGraphs.InProceedingsofthe2019InternationalConferenceonManagement [69] JianlongZhongandBingshengHe.2014.Medusa:SimplifiedGraphProcessing
ofData(Amsterdam,Netherlands)(SIGMOD’19).AssociationforComputingMa- onGPUs.IEEETransactionsonParallelandDistributionSystems25,6(June2014),
chinery,NewYork,NY,USA,775–792. https://doi.org/10.1145/3299869.3319871 1543–1552.
127