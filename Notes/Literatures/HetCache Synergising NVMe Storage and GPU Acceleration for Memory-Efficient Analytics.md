# HetCache

**Source**: HetCache.pdf
**Format**: .pdf

---

HetCache: Synergising NVMe Storage and GPU acceleration
for Memory-Efficient Analytics
HamishNicholson AunnRaza
hamish.nicholson@epfl.ch aunn.raza@epfl.ch
EPFL EPFL
Switzerland Switzerland
PeriklisChrysogelos∗ AnastasiaAilamaki
periklis.chrysogelos@oracle.com anastasia.ailamaki@epfl.ch
Oracle EPFL
Switzerland Switzerland
ABSTRACT 1 INTRODUCTION
Accessinginputdataisacriticaloperationindataanalytics:i)slow Modernhardwarehasrevolutionalizedanalyticalqueryprocessing:
dataaccesssignificantlydegradesperformance,andii)storingev- NVMearraysofferpersistentstoragebandwidththatiscomparable
erythinginthefastestmedium,i.e.,memory,incurshighopera- toDRAMbandwidth,GPUsofferbothhigh-bandwidthlocalmem-
tional and hardware costs. Further, while GPUs offer increased oryforfastjoins,aswellassignificantprocessingpower[10,35,
analyticalperformance,equippingthemwithcorrespondinglyfast 40,14,29],andmodernCPUsprovidebothincreasedperformance,
memoryrequiresevenmoreexpensivememorytechnologiesthan aswellasahostingplatformforcoordinatingandconnectingthe
DRAM;makingmemoryresourcesevenmoreprecious.Existing differentdevices[15].Yet,asfertileasthisnewserverhardware
GPU-acceleratedenginesrelyonCPUmemoryforbiggerworking landscapeis,italsoinvalidatesfundamentalconceptsaboutdata
sets,albeitattheexpenseofslowerexecution.Suchacombination accessforanalytics.
ofbothmemoryandcomputedisaggregation,however,invalidates Theproblem:accessheterogeneityintheprocessinglayer.
theassumptionofexistingcachingmechanisms:i)theprocessing Existing data caching approaches rely on one or more assump-
tierishighlyheterogeneous,ii)dataaccessbandwidthdependson tionsthatareinvalidatedinmodernNVMe-andGPU-equipped
theaccessmethodandcomputeunit,iii)withNVMearrays,persis- servers.First,manyapproachesassumethatin-memorycaching
tentstoragecanapproachin-memorybandwidth,andiv)allthese ofafrequently-accesseddatapageisimportant,whilethetype
relativequantitiesdependonthecurrentqueryanddataplacement. ofqueriesaccessingitislessimportant[17,37,5,33,24,4,21].
Thus,existingcachingapproacheswasteinterconnectbandwidth, However,withNVMearraysprovidingdataaccessbandwidths
cacheinefficiently,andoverallresultinsuboptimalexecutiontimes. thatcansustaintheprocessingthroughputofmanyqueries,the
ThisworkproposesHetCache,astorageengineforanalytical importanceofthequeryitselfincreases:cachingtwopagesthat
workloadsthatoptimizesthedataaccesspathsandtunesdataplace- havethesameaccessfrequencycanprovidesignificantlydifferent
mentbyco-optimizingforthecombinationsofdifferentmemories, acceleration depending on whether the query is scan-bound or
computedevices,andqueries.Specifically,wepresenthowthein- processing-bound.Second,manyapproachesassumedthatCPUs
creasinglycomplexstoragehierarchyimpactsanalyticalquerypro- weretheonlyprocessorsandthuscouldtreattheexecutionlayer
cessinginGPU-NVMe-acceleratedservers.HetCacheaccelerates asindependentofthecachinglayer.TheproliferationofGPUsas
analyticsonCPU-GPUserversforlarger-than-memorydatasets analyticalcoprocessors,however,exacerbatesNUMAeffectsand
throughproportionalandaccess-path-awaredataplacement.Our executionimbalances:fasterprocessorsconsumehigherportions
prototypeimplementationofHetCachedemonstratesa1.14x-1.78x oftheinputdataduetoloadbalancing[6].Asaresult,theprocess-
speedupofGPU-onlyexecutiononNVMeresidentdataandachieves inglayerisheterogeneous,andhaphazardlycachingdataacross
nearin-system-memoryperformanceforhybridCPU-GPUexecu- theprocessorsmayincursignificantinter-devicecommunication
tion, while substantially improving memory efficiency. Overall, toachievebalancedexecution.Finally,manyapproachesassumed
HetCacheturnsthemulti-memory-nodenatureofsuchheteroge- thatonlywhetherapagewascachedornotwasimportantfora
neousserversfromaburdenintoaperformancebooster. query.However,thequeryselectivity,thequeryaccesspattern,
therelativedevicethroughput,andeventhedataplacementand
theinterconnectsallaffecthowefficientlyeachdevicewillaccess
∗WorkdonewhiletheauthorwasatEPFL thedatapages.Asaresult,existingapproachesresultinwasted
hardwareresourcesandincreasedmemorycapacityrequirements.
Thesolution:execution-centricdatacaching.Ourinsightis
thatmostofthewastefulhardwareutilizationresultsfromcaching
ThispaperispublishedundertheCreativeCommonsAttribution4.0International
(CC-BY4.0)license.Authorsreservetheirrightstodisseminatetheworkontheir decisions that have little impact on query execution, while the
personalandcorporateWebsiteswiththeappropriateattribution,providedthatyou tensionbetweencachingdecisionsandexecutionoriginatesfrom
attributetheoriginalworktotheauthorsandCIDR2023.13thAnnualConferenceon
InnovativeDataSystemsResearch(CIDR’23).January8-11,2023,Amsterdam,The theabsenceofanappropriatefeedbackloopacrossthetwolayers.
Netherlands. Toavoidwastefulhardwareutilization,were-evaluatehowcaching

CIDR’23,January8-11,2023,Amsterdam,TheNetherlands Nicholsonetal.
apageinCPU/GPUmemoryaffectsqueryexecutioninthepresence 2 SHORTCOMINGSOFCACHINGPOLICIES
ofbothGPUsandNVMearraysandproposeHetCache,astorage Frequency-basedcaching.Existingcachingpoliciesaimtominimize
enginedesignthatexploitstheseobservationstoprovideexecution- thenumberofdiskaccessesbymaximizingthecachehitrate.The
centricdatacachingonGPU-NVMeservers. mostcommoncachingheuristicssuchasLRU,MRU,and2Qcache
HetCache:Caching&memoryefficiency.Weseethatthere pagesbasedonthefrequencyand/orrecencyofuse[17,37,5,33,
aretwomaincontributingfactorsregardingthecachingefficiency: 24].Suchpoliciesassumethatprocessingthroughputandinput
the query type and the relative performance of the consuming accessbandwidtharehighlycorrelatedandthusworkwellwhen
devices.Further,thereisaninputproportionforeachqueryafter storageisasignificantbottleneck.Historicallythishasbeenthe
whichcachingmoreinputresultsindiminishingreturns[26],and caseduetothesignificantbandwidthdifferencebetweenCPUmem-
ahardware-query-dependentaccessgranularitybelowwhichfine- oryanddiskbandwidth:evenifaqueryaccessedasmallnumber
grainedaccessesforselectivequeriesboostthecachingeffect. ofdatapagesfromstorage,theperformancepenaltywassignifi-
HetCache:Caching&accelerators.Wepinpointthetension cant.Incontrast,recentimprovementsininterconnectandstorage
betweencachingandexecutiontothestageddecision-makingpro- technologysignificantlyreducethebandwidthgap:aggregating
cess:thestoragelayertraditionallyplacesthedataintoamemory NVMedrivesintoarrayscanofferstoragebandwidthcomparable
ofitschoice,whichisincompatiblewiththeflexiblequeryexecu- toDRAMbandwidth.Asaresult,thebenefitofcachingapagede-
tionrequiredforhybridCPU-GPUexecution.HetCachealleviates pendsonitsuse:cachingapageparticipatinginaquerythatisslow
thetensionbyenablingatightintegrationbetweenthecaching duetoanotheroperationwillprovideasmallbenefitcomparedto
layerandtheexecution’sdatatransfers.Traditionally,thecaching cachingapageforaninput-IOboundquery.Evenifthepagesare
layerwoulddecidewheretoplaceapagereadfromstorage.This accessedwiththesamefrequency.Cachingpoliciesthattreat
causestheexecutionlayertofurthertransferitduringexecution
pagesconsumedbyslowandfastqueriesasequalwastes
andrequiresthecachinglayertopredicttherelativedeviceper-
memorycapacityonserverswithhighbandwidthstorage.
formancetoprovideagoodsplitofthedataacrossNUMAnodes, Themore-caching-the-better.Mostpastapproachestreatallpages
priortoexecution.Instead,HetCacheletstheexecutionlayerdothe ofa(disk-residentobjects1,accessfrequency)-combinationasequal
dataplacementandmovesthecachinglayerintoasuggestiverole. andwilltrytocacheasmanypagesaspossible.However,asdisk
Specifically,theexecutiondoesthetransfersthemoreperformant bandwidthincreasesrelativetoqueryprocessingthroughput,the
wayforthecurrentqueryandthecachinglayerprovideshintsto following scenario occurs: even for a column where caching is
steertheexecutionlayertowardsbetterlong-termconfigurations. beneficial,asmorepagesarecached,wecrossathresholdwhere
Intherestofthispaper,weshowhowmodernhardware(NVMe input-IObandwidthceasestobethebottleneckandcachingmore
andGPUacceleration)affectsanalyticalenginesandprovideHet- pagesprovidesdiminishingperformanceimprovements.Asaresult,
Cache, a blueprint for storage engines that i) efficiently exploit HPCache[26]cachescolumnproportions;forCPU-NVMeexecu-
theavailablememoryandstorageresourcesandii)enableGPU- tion,HPCachefindsabalancebetweencapacity,optimalcolumn
acceleratedanalyticalenginestobenefitfromout-of-memorystor- cachingproportion,andexpectedquerypatterns.Still,HPCache
ageandNVMearrays. assumesalinearstoragehierarchyanddoesnothandleeithermul-
Thecontributionsofthispaperare: tipletransferpathsorheterogeneouscomputedevices,whichhave
• Analyzeswhenandwhyprocessingout-of-memorydatais varyingqueryprocessingperformance,Cachingbenefitsareno
aviablealternative,performance-wise,foranalytics–and longerlineartothesizeofthecache;thepointofdiminishing
whyprocessingin-memorydataisstillarequirementfor returnsforcachingdependsonbothhowmuchandwhere
performance(Sections2and3). dataiscached.
• Showsthatthechoiceofstoragemediadependsongranu- Centralizedcachingforhomogeneousarchitectures.Theexisting
larityandquerybenefitandthatthehighlyNUMAnature centralized caching process assumes a uniform and centralized,
ofCPU-GPU-NVMeserverscomplicatesthelandscapebut shared-everythingarchitectureinsidetheserver,withasinglepro-
providessignificantquerybenefits(Section4). cessingunittype,theCPU.Yet,modernservershavemultipleCPU
• ProposesHetCache,astorageenginedesignforanalytical socketsandprocessingunittypes(e.g.,GPUs).Asaresult,such
workloadsthatenvisionsanimpact-orientedcachingmech- architectureshavemultipleaccesspaths,eachwithdifferentband-
anismandtherebyenablesefficientqueryprocessingand widths.Further,themultipleprocessingunitsinvalidatethesingle
memoryutilizationinthepresenceofheterogeneousCPU- processingthroughputassumption:GPUsprocessqueriesatdiffer-
GPUhardwareandhigh-bandwidthstoragethroughpropor- ent(slowerorfaster,dependingonthecase)ratesthantheCPU.
tionalandaccess-path-awaredataplacement(Section5). Exacerbatingthis,hybridCPU-GPUexecutionmayalsodistrib-
• WebuildaprototypeimplementationofHetCacheintoPro- utedataacrossthedifferentdevicesforload-balancingpurposes,
teus (Section 6) and show that HetCache achieves up to makingtheoverallsystemthroughputdynamic.Lastly,memoryis
1.78xspeedupforGPU-onlyexecutionwithNVMe-resident heterogeneousanddistributedacrossmultipledevices:GPUmem-
datacomparedtonaiveNVMe-GPUtransfersandishighly oryhasadifferentaccessprofilethanCPUmemory,andbothare
memory-efficientforhybridCPU-GPUexecution(Section7). distributedacrossmultiplechip(let)s.Asaresult,cachingdatain
one memory node provides a potentially different benefit from
Overall,HetCacheturnsthemulti-memory-nodenatureofhet-
erogeneousCPU-GPU-NVMeserversfromaburdenintoaperfor-
manceboosterforanalytics. 1Columnsorsegments,dependingonthespecificsystem.

HetCache:SynergisingNVMeStorageandGPUacceleration CIDR’23,January8-11,2023,Amsterdam,TheNetherlands
cachingitinanothernode,dependingontheinterconnectcon- Benchmark(SSB)[27]querieswhenthefacttableisondiskandthe
gestion,therelativeprocessingunit,queryprocessingthroughput, storagebandwidthincreasesfrom7GB/sto86GB/s.3Bothofthese
andeventheaccessgranularity.Heterogeneitybreaksunifor- queriesconstructin-memoryhashtablesandthenaccessthefact
mityassumptionsabouttheprocessingandcachinglayerof tablesequentiallytoprobethejoinhashtable.Theexecutiontimeof
adaptivecachingmechanisms. thetwoqueriesonmemory-residentdataisshownindashedlines.
Thesimplifyingalternative:nocachingforanalytics.Giventhe Query1.3consumesinputdataatarelativelyhighinputbandwidth
multitudeofchallengesrelatedtocachingandthehigh-bandwidth andexecutesfasterastheavailablestoragebandwidthincreases.
storagealternatives,pastworkhasalsosuggestedjustexcluding Incontrast,query3.1consumesdataatalowerrateasthequery
analyticalqueriesfromcaching[3].Thesecachingpolicies,while processingismorecomplex,involvingmultiplejoinsandgrouping.
potentially simplifying analytical query processing, rely on the Itonlyimprovesupto14GB/sbecause,beyondthis,storageisnot
assumptionthatanalyticsareeitherunpredictableorveryslow thebottleneckinqueryexecution.Highbandwidthstorageshifts
already.Still,withwarehousesandmoredata-demandingapplica- thebottleneckawayfromstorageforcoarse-grainedaccesses.
tions,analyticalquerieshavebecomemorepopular.Further,with
theintroductionofNUMA-aware,parallelandGPU-acceleratedso- 3.2 GPUacceleration
lutions,analyticscanreachresponsetimesofafewmillisecondsfor GPUssignificantlyaccelerateanalyticalqueryprocessing.Whendata
hundredofGBsofinputs.Asaresult,somequeriesseesignificant isinlocalmemory,GPUsexecutequeriesupto25xfasterthan
performancedegradationduetowaitingonout-of-memorydata CPUs[35,40,14,10].Thisisduetoboththehigherbandwidth
fetches.High-performanceanalyticsrequires,atleastsome, memoryavailableonGPUs,upto2TB/sonacurrent-generation
memoryforcaching. NvidiaA100GPU,andthethreadingmodel,whichenablesGPU
executiontomitigatethecostofmemorystalls.However,suchper-
3 APITSTOPBEFORETHEDISK formancerequiresthedatatobeGPUresidentpriortoprocessing.
Despite the availability of high bandwidth storage, not all data WhileGPUexecutionmaystillbebeneficialforprocessingnon-
shouldbestoredonblockstoragedevices.Inthissection,weargue GPU-residentdata,itispredominantlybottleneckedbythedata
whenandwhyitisstillnecessarytostoreinputdatainmemory. transferovertheinterconnect[32,18,7,40].Cachingcanalleviate
Inthescopeofthispaper,wedonotconsiderspillingintermediate thisbottleneck,butcachesizesareconstrainedbythecompara-
data,suchashashtables,toblockstorage. tivelysmallGPUmemorycapacity.Hence,GPUmemorymustbe
usedjudiciouslytocachedatawiththelargestimpactonquery
3.1 CPUisnotalwaysslow execution times. GPU acceleration needs memory efficient
CPUworkloadscanstillbebottleneckedbyscans,eveninmemory. cachingtomitigatedatatransferbottlenecks.
Figure2showstheconsumptionthroughputofaquerythatscansa Example.However,bandwidthtoinputdataisstillabottleneck
singlecolumn,appliesaselectivefilterandperformsasummation. forGPU-acceleratedqueryexecution.ArraysofNVMedrivescan
Inordertoapplythepredicate,thequerymustreadeachvaluein haveabandwidththatfarexceedstherelativelylimitedintercon-
thecolumn.Theblacklineshowsthequeryconsumptionthrough- nectbandwidthofaGPU.Figure1bshowstheexecutiontimeforthe
putwhenthedataisonNVMestorageastheavailablestorage samesetupbutwhenexecutingonaGPU.Bothquery1.3andquery
increases.Thedashedbluelineshowstheconsumptionthroughput 3.1improveasthestoragebandwidthincreasesuntil32GB/s,which
ofthesamequerywhenthecolumnisfullymemoryresident.The isthemaximumbandwidthofthePCIe4.0x16connectionthatthe
queryprocessingthroughputofNVMeresidentdatascaleslinearly GPUisequippedwith.Theverticaldashedorangelineshowsthe
withtheavailablestoragebandwidthuntilthestoragebandwidth PCIe4.0x16bandwidth.Evenwiththisbottleneck,queriessuchas
exceedshalfofthememorybandwidth(measuredtobe126GB/s). 3.1improveoverCPUexecutionduetotheGPU’shighmemory
ThisisbecauseinadditiontotheCPUreadingthedatafrommem- bandwidthandthehighnumberofconcurrentcontexts.However,
ory, each NVMe transfer also consumes memory bandwidth in queriessuchas1.3performworsethanontheCPUastheCPUcan
ordertowrite(stage)thedatatomemory2.Inourtestbed,thefilter scanthedatafastersinceitcanreaddatafromtheNVMedrives
readsfrommemoryandnottheCPU’slastlevelcache;thus,asthe atagreaterbandwidth.NaiveNVMe-GPUtransfersdonotfully
storagebandwidthapproacheshalfofthememorybandwidth,the exploitthebandwidthofNVMearrays.
querybecomesmemory-bandwidthbound.Incontrast,whenthe
dataisfullymemoryresident,thequeryistheonlythingreadingor 4 HETEROGENEOUSMEMORYHIERARCHY
writingtomemoryandcanreadthedataatfullmemorybandwidth. In-memorydatacachingprovidessignificantaccelerationforsome
QueryexecutiononNVMe-residentdatacanbebottlenecked analyticalworkloads;however,itisalsoexpensiveasmemoryca-
bymemorybandwidth. pacitycomesatasignificantcost[39].Incontrast,out-of-memory
Example. Arrays of NVMe storage have a bandwidth greater storage1)issignificantlycheaperwithabetterprice/performance
thantheprocessingthroughputofmanyquerieswhenexecutedon ratio[22],2)continuestogetcheaperrelativetoDRAM[13],but3)
CPUs[26].Figure1aplotstheexecutiontimeoftwoStarSchema isalsoslower.However,fastandslowneedtobeconsideredrelative
totheworkloadrequirements.Whilestoringdatainmemorycan
2Thisismicro-architecturedependent.IntelXeonsfeatureDDIO,whichtransparently
improvequeryresponsetimes,notallworkloadsbenefitequally
enablesIOdevicestoread/writedirectlyfromtheCPUlast-levelcachesbypassing
DRAM,insomecasesreducingthememorybandwidthrequirementsofIO[1].Tothe
bestofourknowledge,AMDCPUsdonothaveanequivalentfeature.Ourtestbed 3ThestoragebandwidthiscontrolledbyvaryingthenumberofNVMedrivesthedata
(Section7)usesanAMDEPYCCPU. isstripedacross.

CIDR’23,January8-11,2023,Amsterdam,TheNetherlands Nicholsonetal.
|     |     | SSB Q1.3           |     |     | SSB Q3.1           |     |     |     |     |     |          |          |     |
| --- | --- | ------------------ | --- | --- | ------------------ | --- | --- | --- | --- | --- | -------- | -------- | --- |
|     | 16  |                    |     |     |                    |     |     |     | 16  |     | SSB Q1.3 | SSB Q3.1 |     |
|     |     | SSB Q1.3 in-memory |     |     | SSB Q3.1 in-memory |     |     |     |     |     |          |          |     |
)s( emIT noitucexE yreuQ
)s( emiT noitucexE yreuQ
|     | 12  |     |     |     |     |     |     |     | 12  |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
PCIe 4.0 x16
8
8
|     | 4   |                      |                           |     |     |     |     |     | 4   |     |                           |     |        |
| --- | --- | -------------------- | ------------------------- | --- | --- | --- | --- | --- | --- | --- | ------------------------- | --- | ------ |
|     | 0   |                      |                           |     |     |     |     |     | 0   |     |                           |     |        |
|     | 0   | 20                   | 40                        |     | 60  | 80  | 100 |     | 0   | 20  | 40                        | 60  | 80 100 |
|     |     |                      | Storage Bandwidth (GiB/s) |     |     |     |     |     |     |     | Storage Bandwidth (GiB/s) |     |        |
|     |     | (a)CPU-onlyexecution |                           |     |     |     |     |     |     |     | (b)GPU-onlyexecution      |     |        |
Figure1:ExecutiontimeastheavailablestoragebandwidthincreasesfortwoSSBqueriesatscalefactor1000.SeeSection7forthefull
experimentalsetup.
|     |     |           |     |     |             |     |     | DBMS. | Caching | policies | must determine | both | when and where |
| --- | --- | --------- | --- | --- | ----------- | --- | --- | ----- | ------- | -------- | -------------- | ---- | -------------- |
|     |     | NVMe Scan |     |     | Memory Scan |     |     |       |         |          |                |      |                |
tocache.Individually,eachcomputedeviceachievesmaximum
140
|     |     |     |     |     |     |     |     | query | processing | throughput | when | consuming | data from local |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ---------- | ---------- | ---- | --------- | --------------- |
)s/BiG( tuphguorhT nacS 120 memory.ForhybridCPU-GPUexecution,theidealdataplacement
100 acrossdevicesisproportionaltotheirqueryprocessingthroughput.
80 However,thereisacapacityconstraint,whichisnon-uniformacross
devices;CPUmemoryismuchlargerthanGPUmemory,yetGPUs
60
typicallyhavegreaterqueryprocessingthroughput.Thus,oncethe
|     | 40  |     |     |     |     |     |     | GPUcacheisfull,GPUqueryexecutiondependsonefficientdata     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------- | --- | --- | --- | --- | --- |
|     | 20  |     |     |     |     |     |     | transfers.ThisdatacanbetransferredfromCPUmemoryorNVMe      |     |     |     |     |     |
|     | 0   |     |     |     |     |     |     | storage,andbothcansaturatetheinterconnect.Thekeydifference |     |     |     |     |     |
0 20 40 60 80 100 betweenthetwooptionsistheaccessgranularity.GPUscandirectly
Storage Bandwidth (GiB/s) accessCPUmemoryatfinegranularitybutcanonlyaccessNVMe
storageattheblocklevel.Becausemanyqueriesselectivelyaccess
Figure2:Scanthroughputforscan-filter-aggregatequerywithvary-
columns,e.g.,duetojoinsorfilters,CPU-memorycachingforGPU
ingstoragebandwidth.SeeSection7forthefullexperimentalsetup.
consumptioncanenablefasterqueryresponsetimesduetothe
reductioninIO-amplificationcomparedtotransferringfullpages.
fromin-memorystorage.Thus,treatingalltheinputdataequally Figure3demonstratestheimpactontheperformanceofpushing
forin-memorycachingmaywastememoryforlittle-to-nobenefit. wholepagestotheGPUcomparedtoaccessingvaluesdirectlyin
Conversely,out-of-memoryprocessingcansignificantlyslowdown CPUmemoryastheselectivityvaries.Forthismicro-benchmark,
someworkloads.Further,withtheproliferationofaccelerators,the theinputdataisatableoftwocolumnsofuniformlydistributed
performancebenefitofstoringdatainmemorydependsonboth
integers.Eachcolumnis100GB.Thequeryfilterstuplesusingthe
thecomputedeviceconsumingitaswellasthedifferenceinband- firstcolumnandthensumsthevaluesfromthesecondcolumnfor
widthbetweenmemoryandout-of-memorystorage.Efficientuse tuplesthatpassthefilterusinglatematerialization.Thefilterisused
ofmemorydemandsaworkload-awareapproach. tocontroltheselectivity.ForGPUexecution,directlyaccessing
Traditionally,storagesystemsfollowalinearhierarchy.Data valuesinCPUmemoryisadvantageousforselectivitiesbelow10%
| is loaded | into | faster mediums | before | being | processed; |     | the CPU |     |     |     |     |     |     |
| --------- | ---- | -------------- | ------ | ----- | ---------- | --- | ------- | --- | --- | --- | --- | --- | --- |
comparedtotransferringallthedatausing2MiBpages.However,
loadsdatafromNVMetoDRAM,andthentheCPUloadsthedata forhigherselectivities,itismoreperformanttopushthedatavia
| frommemorytoitscachesand,ultimately,registersforprocessing. |     |     |     |     |     |     |     | 2MiBpages. |     |     |     |     |     |
| ----------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- |
However,heterogeneousserversdonotmaintainalinearhierarchy. CPUmemorycanserveasacacheforpagesselectivelyaccessed
DatacanbecopiedbetweenCPUandGPUmemoryatcache-lineor byGPUexecution:theselectivityreducestheamountofdatatrans-
greatergranularity,andGPUscanalsodirectlyaccessCPUmemory
ferredovertheinterconnectduringlatematerializationforCPU-
atfinegranularity[8].BothCPUsandGPUscandirectlytransfer residentdata.UsingCPUmemorytocachedatafortheGPUis
datafromNVMedrivestotheirlocalmemory.Further,datacanbe viablebecause,formanyqueries,CPUexecutionisslowerthanstor-
transferredfrompointtopointviamultipleintermediatetransfers. agebandwidthandthereforedoesnotrequirealargecachetomax-
Forexample,datacanflowfromNVMestoragetoGPUmemory imizetheCPU’sownprocessingthroughput.However,CPUmem-
throughCPUmemory.
orytoGPUtransfersalsoconsumesCPUmemorybandwidth.This
|     | The diversity | in available | access | paths | and | the non-uniform |     |     |     |     |     |     |     |
| --- | ------------- | ------------ | ------ | ----- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- |
maycauseinterferenceinCPUexecutionforbandwidth-intensive
queryprocessingthroughputschallengesthecachingdesignof

HetCache:SynergisingNVMeStorageandGPUacceleration CIDR’23,January8-11,2023,Amsterdam,TheNetherlands
eagerlytransferpagesforcolumnsthatneedtobenearlyentirely
accessedandlazilytransfervaluesfrompagesthatareselectively
accessed.
HetCachemitigatestheinterconnectbottleneckthroughStaged
SemiLazy Transfers. Lazy transfers require the accessed data to
beinCPUmemory.Basedonper-columnqueryselectivityhints,
HetCachehandlesGPUpagerequestsforNVMe-residentdataby
eithereagerlymovingthepagefromNVMestoragetoGPUmemory
orstagingthepageinCPUmemorythroughanNVMetoCPU
memorytransfer.TheGPUcanthenlazilyfetchvaluesinthepageat
afinergranularityresultinginmoreefficientutilizationoftheGPU
interconnect.StagedSemiLazytransfersresultinbetterstorage
Figure3:Executiontimeforascan-filter-aggregatequeryasthese- bandwidthutilization,asthefullstoragebandwidthisavailablefor
lectivityofthefilterisvaried.SeeSection7forthefullexperimental NVMetoCPUmemorytransfers,whileNVMetoGPUtransfersis
setup. limitedbytheGPUinterconnect.
queries.Cachinginaheterogenousmemoryhierarchyisatrade-off 5.2 Heterogeneity-awareCaching
betweenaccessgranularity,capacity,andbandwidths.Effective HetCache implements a heterogeneity-aware caching policy. It
caching policies must consider all three properties to meet the usesbothworkloadinformation,queryprocessingthroughput,and
bandwidthdemandsoftheworkload. selectivityhints,aswellashardwareinformation,interconnect
storage,andmemorybandwidths,todeterminehowmuchand
5 HETCACHE:WORKLOADANDHARDWARE wheretocache.
AWARESTORAGE To determine how much to cache on each device for device-
localaccess,HetCacheobservestheper-devicequeryprocessing
WeenvisionHetCache,astorageenginethatefficientlyutilizesthe
throughput.Therateofpagerequeststhataquerymakesfromeach
memoryandstorageresourcesofNVMe-CPU-GPUserverstoac-
deviceisusedtoinferthequery’sper-deviceprocessingthroughput.
celeratequeryexecutiononlarger-than-memorydata.HetCacheis
Withtheper-deviceprocessingthroughput,theknownintercon-
workload-awareinordertodeterminewhentocachedata,utilizing
nect,storage,andmemorybandwidths,HetCachedeterminesthe
memorytoonlycachecolumnsthatwillacceleratequeryresponse
maximumamountofeachcolumntobecachedoneachdevice
times.Further,HetCacheholisticallyconsidersthequerythrough-
withoutcachinganycolumnbeyondthepointofdiminishingre-
putofCPUsandGPUsaswellastheper-queryper-columnaccess
turns.i.e.,itaimstomatchtheeffectivebandwidthtoqueryinputs,
selectivitytodeterminewheretocachedataandwhichtransfer
whichcanbepartiallyinmemoryandpartiallyinstorage,tothe
pathtouse.
queryprocessingthroughput.
HetCachealsousesCPUmemorytocachedataforGPUaccesses.
5.1 StagedSemiLazyTransfers
AsCPUmemorycapacityislargecomparedtoqueryprocessing
GPU query throughput for non-GPU resident data is primarily
throughput,CPUstypicallyexperiencelessmemorypressurethan
bottleneckedbytheinterconnect.Bothmemoryandstorageband-
GPUswhichhavehigherqueryprocessingthroughputsandcon-
widthsexceedtheGPU-systeminterconnectbandwidth,andin
strainedmemorycapacities.StagedSemiLazycachingcanmovethe
mostcases,theprocessingthroughputofGPUqueryexecution
bottleneckfromtheinterconnectbacktostorageforqueriesthatse-
also exceeds the interconnect bandwidth. Input data can either
lectivelyaccesscolumns.Hence,forthesequeries,itisnecessaryto
beeagerly(pushed)orlazilytransferred(pulled)toGPUs.Eager
cachepagesfromselectivelyaccessedcolumnsinthehigherband-
transferspushfullpagesofdataovertheinterconnectintoGPU
widthCPUmemorytoutilizetheGPUinterconnectfully.HetCache
memorybeforetheGPUbeginsprocessingthosepages,overlap-
usesboththeper-devicequerythroughputandtheselectivityhints
pingprocessinganddatatransfersasthroughHetExchange[6].
todetermineifGPUqueryprocessingisinterconnect-bandwidth-
Eagertransfersresultinasequentialaccesspattern,enablingfull
boundorstoragebandwidth-bound.Inbothcases,itwillcache
utilizationoftheinterconnectbandwidth.GPUqueryexecution
pages in GPU memory until limited by GPU memory capacity.
onGPUresidentdatabenefitsfromboththehighbandwidthand
OnceconstrainedbytheGPUmemorycapacity,HetCachewill
lowlatencyofGPUmemorydataaccesses.However,notallvalues
preferentiallycachedenselyaccessedpagesinGPUmemoryand
pushedacrosstheinterconnectmaybeaccessedbythequery.For
cachesparselyaccessedpagesforstorage-bandwidthboundqueries
example,valuesfromcolumnsthatareaccessedafteraseriesof
in CPU memory, optimizing for overall GPU query processing
selectiveconditions,suchasjoinsandfilters,havealowerprobabil-
throughputwhetherqueriesarebottleneckedbytheinterconnect
ityofbeingaccessedbythequery.ModernGPUscanuseaunified
bandwidthorbystoragebandwidth.
virtualmemoryaddressspacewithCPUmemory,enablingGPUs
todirectlyaccessCPUmemoryatafinegranularitybutathigher
latencythanaccessingGPU-localmemory[8].Lazytransfersare 6 SYSTEM
beneficialwhenfewvaluesarerequiredperpage,aslessdataneeds WeuseProteusasouranalyticalengine[6,32].Proteusisanin-
tobetransferredacrosstheinterconnect.SemiLazytransfers[32] memoryexecutionenginewithsupportforparallelqueryexecution

CIDR’23,January8-11,2023,Amsterdam,TheNetherlands Nicholsonetal.
acrossmixesofCPUsandGPUs.Querypipelinesareparallelized pageinthecache,weusereferencecounting:eachdatapageis
byinstantiatingapipelineinstancepercomputeunit(CPUcore accompaniedbyareferencecountfortheflow-basedexecution;we
orGPU).Alogicalscanoperatoremitspagehandlesthatarethen extendthatandkeeponeextrareferenceinHetCachetoprevent
routedtoquerypipelineinstances.Theroutingpoliciesareplug- thepagefrombeingevicted/releasedwhenitisconsumed.Toevict
gable,defaultingtoaprefer-localroutingpolicy.Theprefer-local apage,HetCachereleasesitsreference,thoughthismaynotimme-
routingpolicyroutespagehandles(inrowsets)topipelineinstances diatelyfreethepage’smemoryasquerypipelinesmaystillhold
runningonacomputeunitlocaltothememoryreferencedbythe temporaryreferences.Atthemomentthatthemem-movedecides
correspondingrowset,withafallbackoptionofusinganon-local todoadatatransfer,ithasderivedasourceandatargetlocation;
computeunitifthelocaloneisbusy.Whendatatransfersareeager, still,thereareasetofdifferentactionsrequiredtoimplementthe
beforetouchingthetuplesinsideapage,amem-moveoperator[6] transfers.Specifically,themem-moveinspectsthesourceandtarget
transfersthepagetotheconsumptionsiteifit’snotalreadythere. locationandinvokestheblockorthestoragemanagertodothe
Memorytransfersarescheduledasynchronouslytocomputetasks actualdatatransfers,dependingonwhetherit’samemory-onlyor
tooverlapdatatransfersandintra-deviceexecution. NVMe-involveddatatransfer.
IntegratingHetCacheintoProteusrequiredhandlingthelate
bindingofinputpagestomemory.Specifically,beforeHetCache, 7 EVALUATION
Proteus, as an in-memory engine, expected the data to already
Thissectionincludestheresultsofourexperimentalevaluation.
bepopulatedinmemoryandapagehandletorefertoasingle
First,wedescribethehardware,somespecificsofthetransfers,
actual data page – with only the exception of snapshot-related
andthebenchmarkusedinourexperiments.Thenwepresentthe
copies[32].Anycopiesoftheinputdata,e.g.,duetoatransfer
resultsforGPUexecutionforvaryingaccesspathsandinitialdata
fromonedevicetoanother,weretransientandonlyexistedforthe
locations,demonstratingtheperformancebenefitofindirectNVMe-
requiredsubsetofthequerylifetime,i.e.untiltheywereconsumed
GPUtransfers.Finally,weevaluatethedataplacementofHetCache
andthememoryreclaimedforanotherdatatransfer.Further,when
forhybridCPU-GPUexecutionandshowthememory-efficiency
themem-moveoperatorreceivedapagehandle,itwouldcheckits
benefitsofworkloadandhardwareawarecaching.
currentplacement.Ifthecurrentlocationwasacceptable(i.e.,for
aneagertransferifitwasalreadyinthedestinationnode,orfora
7.1 Experimentalsetup
lazytransferifitwasaccessiblebythetargetnode),andifnot,it
wouldmoveittotheappropriatenode.
Hardware.Allexperimentswereconductedonaserverwitha
2x24-coreAMDEPYC7413processor,havingtwothreadspercore,
In contrast, HetCache, similar to traditional storage engines,
totalling 96 threads and 256 GB of DRAM. Each CPU socket is
canresultintwoormorecopiesofadatapage:oneinstorage
connectedwithasingleNvidiaA40GPUwith48GBmemoryusing
(NVMe)andpotentiallyoneormorecopiesintheblockmanager
16PCIe4.0lanesand12CorsairMP600ProNVMedrives,each
(in-memorycachedpage,potentiallyreplicatedacrossCPU/GPU
using4PCIe4.0lanes.Weobserveamaximummemorybandwidth
memory).Havingmultiple(immutable)copiesofthesamepage
of116GB/spersocketontheSTREAMtriadbenchmark[23],and
providesadditionalfreedomformemorytransfersbutalsochal-
86GB/ssequentialreadbandwidthfromall12NVMewhenusing
lenges.WeimplementaroutingpolicythatconsultsHetCacheon
fio [2]. All experiments were conducted on a single socket and
thelocationsofthepagesinarowset.Rowsetsareroutedbasedon
utilizedall12NVMedrivesunlessotherwisestated.
thelocationsofthefirstcolumnintherowsetsinceitisthemost
likelytobecachedinGPUmemory,asProteuswillaccessallthe
Software.CPU-GPUmemorypagetransfersuseCUDA’smem-
copymechanism,whiletheNVMe-involvedtransfersbranchbased
valuesfromthefirstcolumn.RecallthatcachingforCPUrequests
onwhetherthetargetisCPUorGPUmemory:ForNVMetoCPU-
doesnotconsidertheselectivity;thus,thereisnobiastowards
memoryIO,weuseio_uring[9],andfordirectNVMetoGPUIO,
cachingthefirstcolumninCPUmemory.IfthepageisinbothCPU
weuseNvidia’sGPU-DirectstorageAPI[11].Allpage-leveltrans-
andGPUmemory,therowsetisroutedtoaGPUpipelineinstance
fersuse2MiBastheIOtransfersizetoalignwiththe2MiBhuge
toleveragetheGPU’sgreaterprocessingspeedoncacheddata.We
pagesusedbyProteus.Lazysub-pagedataaccesseshappenasDMA
updatedthemem-movetoconsultwithHetCacheonthreethings:
requests,andweenforcetheaccessedpagetobepresentinCPU
1)thelocationofcopiesofthecorrespondingpage,2)whether
memorytobegloballyaccessible.
thetransferredpagewouldbecachedinitstargetnodeforsubse-
quentqueries,and3)ifyes,whetherthetransferredpageshouldbe
Benchmark.WeevaluateourmethodsusingtheStarSchema
Benchmark(SSB)[27]withascalefactor(SF)of1000.SSBhasfour
cachedforselectiveaccessornot.HetCache’sanswersto(2)and
querygroups,andwithineachquerygroup,thequery’sselectivity
(3)aretreatedashints,andthemem-moveisallowedtoignore
decreaseswiththerank;forexample,Q1.3ismoreselectivethan
them.Basedonthethreeanswers,themem-movedecideswhether
Q1.2,whichismoreselectivethanQ1.1.Westorethedatainbinary
atransferisnecessaryorifanexistingin-memorycopyofthepage
columnarformat,resultinginQuerygroups1-3havingaworking
issuitable.Ifatransferisnecessary,itselectsatargetmemorynode,
setof96GBperqueryandgroup4havingaworkingsetof144GB.
schedulesthetransfer,andonitscompletion,itregistersthenew
pagelocationwithHetCachealongwiththeIDofthequerymak-
ingtherequestandaselectivityhintpasseddownfromthequery 7.2 StagedSemiLazytransfers
plan.ThequeryIDisusedbyHetCachetoinferthequery’spro- Figure4analyzestheperformanceofSemiLazytransfersfrommem-
cessingthroughput.Then,HetCachecandecidewhetheritwants oryandstagedSemiLazytransfersfromNVMecomparedtoeager
tokeeptheresultingpageaspartofthecache.Tomaintainthe transfersunderGPU-onlyexecution.TheexperimentexecutesSSB

HetCache:SynergisingNVMeStorageandGPUacceleration CIDR’23,January8-11,2023,Amsterdam,TheNetherlands
4
2
0
Q3.1 Q3.4
)s(
emiT
noitucexE
yreuQ
CPU-resident (eager) CPU-resident (SemiLazy)
NVMe-resident (eager) NVMe-resident (Staged SemiLazy)
4
2
0
Q1.3 Hybrid Q3.1 Hybrid
SSB Query
Figure4:ComparisonoftransferpathsforGPU-onlyexecutionwith
CPU-memoryresidentdata(blue)andNVMeresidentdata(yellow)
Q3.1andQ3.4atSF1000;thequerieshaveselectivitiesof3.4%and
0.000076%,respectively.Inbothcases,whetherthedataisreadfrom
CPUmemoryorNVMedirectly,eagertransfersarebottlenecked
bytheGPUinterconnectforbothqueries;thisisbecause,regard-
lessofqueryselectivity,theentirequery’sworkingset(96GB)
istransferredtoGPU,althoughthetransfersareoverlappedwith
processing.AlthoughSemiLazytransferslessdataovertheinter-
connect,itdoessoatthecostofhighermemorylatencyfromCPU
memory.ThebenefitofSemiLazytransfersismoreapparentin
Q3.4comparedtoQ3.1becauseQ3.4ismoreselective,andthus,less
dataistransferredovertheinterconnectfortheselectivelyaccessed
columns.However,inthecaseofStagedSemiLazytransfers,the
lowerselectivitycausesthequerybottlenecktoshiftfromthein-
terconnecttotheNVMetransfers.Althoughlessdataistransferred
acrosstheinterconnect,theselectivelyaccessedcolumnsmuststill
beloadedfromtheNVMedrivesintoCPU-memory.
Insummary,SemiLazyandstagedSemiLazytransfersenable
GPUstoaccessdataatafinergranularity(directlyaccessingvalues
inCPUmemorycomparedtodiskblocks)andtherebyreducedata
transferredovertheinterconnectinthecaseofselectiveaccesses,
andforveryselectiveaccesses,shiftsthebottleneckfromGPU
interconnecttostorage.StagedSemiLazytransfersenabletheDBMS
tooptimizetransfergranularity,capacity,andlimitedinterconnect
bandwidth.
7.3 Workload-awarecaching
Figure5plotstheexecutiontimeofSSBQ1.3andQ3.1atscalefactor
1000,executedonboth,CPUandGPU(HetExchange[6]),with
(staged)SemiLazytransfers.WesettheCPUandGPUmaximum
cachesizesto90GBand10GB,respectively.Weplottheexecution
timeswhenthedataiscompletelyNVMeresident,completelyCPU
memoryresident,andwithwarmHetCache-managedcaches.Q1.3
isbandwidth-intensiveandthusbenefitsfromdatabeinginmemory.
Incomparison,Q3.1ismorecompute-intensiveandonlysuffersa5%
penaltywhenaccessingdatadirectlyfromNVMe.Q1.3requires
75GBofCPUcache,inadditionto10GBofGPUcache,toapproach
fullyCPU-memoryresidentperformance,whileQ3.1requiresonly
thefull10GBofGPU-memorycacheandnoCPU-memory.This
isduetothefactthatquerypipelinesbeingexecutedonGPUare
bottleneckedbytheinterconnectbandwidth,whileforQ1.3the
)s(
emiT
noitucexE
yreuQ
CPU-resident NVMe-resident HetCache
SSB Query
Figure5:QueryprocessingonCPU-GPUwithCPU-resident,NVMe-
resident,andHetCache’ddata
CPUqueryprocessingperformanceisthesamewhetherthedata
isinitiallyNVMe-residentorCPU-memoryresident.
Figure6analyzestheeffectofCPUcachesizeonQ1.3byplotting
executiontimewithvaryingcachesizesinCPUmemorywhile
havingafixed10GBGPUcache.RecallthatQ1.3isbandwidth-
intensiveandhencefullyusesa10GBGPUcacheandrequiresup
to80%ofdatainCPUmemorybeforetherearediminishingreturns
oncachinganymoreinputdata.
Impact-orientedcachingthroughproportionalcachingallows
HetCachetotunetheamountofcacheddatatobestefforttosatisfy
thequery’sconsumptionbandwidthrequirementsbutnotbeyond
thepointofdiminishingreturns.Q3.1representstheclassofqueries
thatdonotrequirecachingdatainCPUmemorygiventhatthe
availablestoragebandwidthishigherthanthequery’sbandwidth
requirementforCPUexecution,andthus,savesCPUmemoryfor
cachingotherdata,whichmayhaveahigherimpactontheoverall
performanceoftheanalyticalengine.WhileQ1.3isrepresentative
ofclassqueriesthatarebandwidth-intensiveandbenefitmorefrom
cachinginfastermemory;inthiscase,thequery’sexecutiontime
improvesuntil80%ofinputdataiscached.Further,workloadaware-
nessallowstheHetCachetoselectappropriatetransfermethods
acrossdevices,overcomingthecommonbandwidthwallforacceler-
atedqueryprocessing.Querieswithlowerselectivitiesbenefitfrom
stagingdatainCPU-memory,gettingthebestofbothworlds;high-
bandwidthloadingfromNVMetoCPU-memorywhileefficiently
usingCPU-GPUinterconnectviagranularaccesses.Insummary,
HetCacheintroducesworkload-awareandimpact-orientedcaching
andefficientlyutilizesthestoragetiersformaximumperformance.
8 RELATEDWORK
Buffermanagersoptimizedfornearlyin-memoryprocessing.
Recentworkhasminimizedtheoverheadsofbuffermanagerswhen
processingin-memorydata.Thisenablesin-memoryperformance
whentheworkingsetfitsinmemorybutalsogracefulperformance
degradationwhentheworkingsetexceedsmemorycapacity.Pro-
vidingpersistencyandsupportforout-of-memorydatatraditionally
introducestwooverheadswithrespecttothebufferpool.First,hav-
ing a centralized buffer pool creates a point of contention [16].
Second,persistencerequiresalevelofindirectionwhentranslating
in-memoryreferencestoout-of-memoryobjectreferences.Graefe

CIDR’23,January8-11,2023,Amsterdam,TheNetherlands Nicholsonetal.
2
1.5
1
0.5
0
0 20 40 60 80 100
)s(
emiT
noitucexE
yreuQ
NVMestoragetotheGPUforqueryprocessing[20].PG-Strom[30]
canloaddatadirectlyfromNVMetoaGPUaswellasfromCPU
memory.WhileitimplementsaGPUcache,itdoessoatthetable
levelofgranularity,limitingitsutilitytotablessmallerthanGPU
memory.
9 CONCLUSION
Thispapershowshowmodernhardware(NVMeandGPUacceler-
ation)affectsanalyticalenginesanddemonstratesthatdataplace-
ment at each layer in the heterogenous memory hierarchy is a
trade-offbetween:1)Bandwidth:Eachmemorytiercanaccessdata
atdifferentbandwidths.Themaximumbandwidthtierisnotnec-
Percentage of Input Data in CPU-memory essarilyoptimal.Itcanusecapacitywithoutperformancegainat
theexpenseofotherqueries,whichcouldbenefitfromincreased
Figure6:ExecutiontimeofSSBQ1.3atSF1000withafixed10GB
bandwidth.2)Capacity:Datastoredindevice-localmemoryresults
GPUcacheandvaryingsizeCPUmemorycache.
inthehighestperformance.However,withtheconstrainedcapacity
ofeachdevice,notalldatacanbestoredinlocalmemory.Heteroge-
etal.[12]usepointerswizzlingtoeliminatebufferpooloverheads nousprocessingthroughputandcapacitymeanshigh-throughput
whenalldatafitsinmemory.Byavoidingahashtable,theyavoid capacity-limiteddevicescancacheinotherdevices’memory.3)Ac-
a costly central point of contention. LeanStore [19] extends on cessgranularity:Eveniftwoaccesspathsofferthesamebandwidth,
pointerswizzlingbyspeculativelyunswizzlingpages,keepinghot theaccessgranularitycanlimittheeffectivebandwidthduetoIO
pagesinmemorywithoutexplicitlytrackingpageaccessesina amplification.Indirecttransfersfromblock-leveldevicesviaan
shareddatastructure.Umbra[25]extendsLeanStorewithsupport additionalcache-lineaddressabledevicecanmitigatethecostofIO
forvariable-lengthbufferframes,improvingthehandlingoflarge amplificationduetonon-uniformaccesstostoragebandwidth.
objects.Optimizingbufferpoolaccessesreducestheoverheadim- WeproposeHetCache,astorageenginedesignforanalytical
posedonmostly-in-memoryanalyticswhileaddingsupportfor workloads.HetCacheencapsulatesheterogeneitythroughimpact-
out-of-memory data. Unlike HetCache, these approaches strive orientedproportionalcachingandaccess-path-awaredataplace-
tokeeptheworkingsetinmemory,regardlessofthebandwidth ment.OurprototypeimplementationofHetCacheachievesupto
requiredbytheworkload.Thesemethodsarecomplementaryto 1.78xspeedupofGPU-onlyexecutiononNVMeresidentdata,and
HetCache,whichimprovesthecacheefficiencywithrespecttothe HetCache-managedcachescanachievein-CPU-memoryperfor-
performancegainsachievedbycachingdatainmemorybutdoes mancewithhybridCPU-GPUexecutionwithoutstoringalldatain
notattempttoimproveuponthebuffermanageroverhead. memory.
GPUdatatransfers.HetCacheisnotthefirstsystemdesigned
toovercometheGPUinterconnectbottleneck.Toalleviatetheinter- ACKNOWLEDGMENTS
connectbottleneckforhighlyselectivequeries,Yuanetal.studied
Wewouldliketothankthereviewersfortheirvaluablefeedback.
theeffectsofdifferentCPU-GPUtransferoptimizationsonGPU
ThisworkwaspartiallyfundedbySNSFproject“EfficientReal-time
query performance, including compression, invisible joins, and
AnalyticsonGeneral-PurposeGPUs”subsideno.200021_178894/1.
transferoverlapping[40].Razaetal.introduceSemiLazytransfers
toGPUforsystemmemoryresidentdata[32].HippogriffDB[20]
REFERENCES
usesworkload-awareadaptivecompressiontomaximisetheeffec-
[1] MohammadAlian,YifanYuan,JieZhang,RenWang,My-
tivebandwidthofdatatransferstoGPUsandalsointroducesdirect
oungsooJung,andNamSungKim.2020.DataDirectI/O
NVMe-GPUtransfersbypassingCPUmemory.Dataisstoredin
CharacterizationforFutureI/OSystemExploration.In2020
memoryorondiskinacompressedformatandisdecompressedby
IEEEInternationalSymposiumonPerformanceAnalysisof
theGPUjustbeforeitisconsumedbyqueryexecution.BaM[31]
SystemsandSoftware(ISPASS).(August2020),160–169.doi:
introducesatechniquetoenableGPUorchestrationofIOrequests,
10.1109/ISPASS48437.2020.00031.
bypassingtheCPUforbothorchestrationanddatatransfers.This
[2] JensAxboe.2022.Fio.original-date:2012-10-22T08:20:41Z.
enablesGPUstoaccessNVMeresidentdatawithdisk-block-sized
(January2022).Retrieved01/26/2022fromhttps://github.
data-dependentaccesspatternsperformantly.
com/axboe/fio.
IntegratingGPUsintothestoragehierarchy.MostGPU-
[3] WBridge,AJoshi,MKeihl,TLahiri,JLoaiza,andNMac-
accelerateddatabasesystemseitheroperateonlyonGPU-resident
naughton.1997.TheOracleUniversalServerBufferMan-
dataortransferdatafromsystem-memorytoGPU-memoryatquery
ager.en.InProceedingsofthe23rdVLDBConference.Athens,
executiontime[29,34].GPUmemorycaneitherbetreatedasa
Greece,5.
peertoCPUmemoryorasahigherlevelofthestoragehierarchy.
[4] MustafaCanim,GeorgeA.Mihaila,BishwaranjanBhattachar-
SystemssuchasAresDB[36]andHeavyDB[38,28]takethelatter
jee,KennethA.Ross,andChristianA.Lang.2010.SSDbuffer-
approach,usingCPUmemoryasastagingareaforalltransfers
poolextensionsfordatabasesystems.en.Proceedingsofthe
toGPUmemory.HippogriffDBtreatsGPUmemoryasapeerto
CPUmemory.ItstreamsinputdatafrombothCPUmemoryand

HetCache:SynergisingNVMeStorageandGPUacceleration CIDR’23,January8-11,2023,Amsterdam,TheNetherlands
VLDBEndowment,3,1-2,(September2010),1435–1446.doi: NewHardware-DaMoN’12.ACMPress,Scottsdale,Arizona,
10.14778/1920841.1921017. 55–62.doi:10.1145/2236584.2236592.
[5] Hong-TaiChouandDavidJ.DeWitt.1986.Anevaluation [19] ViktorLeis,MichaelHaubenschild,AlfonsKemper,andThomas
ofbuffermanagementstrategiesforrelationaldatabasesys- Neumann.2018.LeanStore:In-MemoryDataManagement
tems.Algorithmica,1,3,311–336.doi:10.1007/BF01840450. beyondMainMemory.en.In2018IEEE34thInternational
[6] PeriklisChrysogelos,ManosKarpathiotakis,RajaAppuswamy, ConferenceonDataEngineering(ICDE).IEEE,Paris,(April
andAnastasiaAilamaki.2019.HetExchange:encapsulating 2018),185–196.doi:10.1109/ICDE.2018.00026.
heterogeneousCPU-GPUparallelisminJITcompileden- [20] JingLi,Hung-WeiTseng,ChunbinLin,YannisPapakonstanti-
gines.en.ProceedingsoftheVLDBEndowment,12,5,(January nou,andStevenSwanson.2016.HippogriffDB:balancingI/O
2019),544–556.doi:10.14778/3303753.3303760. andGPUbandwidthinbigdataanalytics.en.Proceedingsof
[7] PeriklisChrysogelos,PanagiotisSioulas,andAnastasiaAila- theVLDBEndowment,9,14,(October2016),1647–1658.doi:
maki.2019.Hardware-consciousqueryprocessingingpu- 10.14778/3007328.3007331.
acceleratedanalyticalengines.In9thBiennialConferenceon [21] ZhiLi,PeiquanJin,XuanSu,KaiCui,andLihuaYue.2009.
InnovativeDataSystemsResearch,CIDR2019,Asilomar,CA, CCF-LRU:anewbufferreplacementalgorithmforflashmem-
USA,January13-16,2019,OnlineProceedings.www.cidrdb.org. ory.IEEETransactionsonConsumerElectronics,55,3,(August
[8] 2020.CUDAC++ProgrammingGuide.en,379. 2009),1351–1359.ConferenceName:IEEETransactionson
[9] 2019.EfficientIOwithio_uring.(2019).Retrieved12/10/2022 ConsumerElectronics.doi:10.1109/TCE.2009.5277999.
fromhttps://kernel.dk/io_uring.pdf. [22] DavidLomet.2018.Cost/performanceinmoderndatastores:
[10] HenningFunke,SebastianBreß,StefanNoll,VolkerMarkl, how data caching systems succeed. en. In Proceedings of
andJensTeubner.2018.PipelinedQueryProcessinginCopro- the 14th International Workshop on Data Management on
cessorEnvironments.en.InProceedingsofthe2018Interna- NewHardware.ACM,HoustonTexas,(June2018),1–10.doi:
tionalConferenceonManagementofData.ACM,HoustonTX 10.1145/3211922.3211927.
USA,(May2018),1603–1618.doi:10.1145/3183713.3183734. [23] JohnD.McCalpin.1995.Memorybandwidthandmachine
[11] 2019.GPUDirectStorage:ADirectPathBetweenStorageand balanceincurrenthighperformancecomputers.IEEECom-
GPUMemory.en-US.(August2019).Retrieved12/10/2022 puterSocietyTechnicalCommitteeonComputerArchitecture
fromhttps://developer.nvidia.com/blog/gpudirect-storage/. (TCCA)Newsletter,(December1995),19–25.
[12] GoetzGraefe,HarisVolos,HideakiKimura,HarumiKuno, [24] NimrodMegiddoandDharmendraS.Modha.2003.ARC:
Joseph Tucek, Mark Lillibridge, and Alistair Veitch. 2014. ASelf-Tuning,LowOverheadReplacementCache.InPro-
In-memoryperformanceforbigdata.en.Proceedingsofthe ceedingsofthe2ndUSENIXConferenceonFileandStorage
VLDBEndowment,8,1,(September2014),37–48.doi:10. Technologies(FAST’03).USENIXAssociation,USA,(March
14778/2735461.2735465. 2003),115–130.
[13] GabrielHaas,MichaelHaubenschild,andViktorLeis.2020. [25] ThomasNeumannandMichaelJ.Freitag.2020.Umbra:A
Exploiting Directly-Attached NVMe Arrays in DBMS. In disk-based system with in-memory performance. In 10th
CIDR. ConferenceonInnovativeDataSystemsResearch,CIDR2020,
[14] BingshengHe,MianLu,KeYang,RuiFang,NagaK.Govin- Amsterdam, The Netherlands, January 12-15, 2020, Online
daraju,QiongLuo,andPedroV.Sander.2009.Relational Proceedings.www.cidrdb.org.
querycoprocessingongraphicsprocessors.en.ACMTrans- [26] HamishNicholson,PeriklisChrysogelos,andAnastasiaAil-
actionsonDatabaseSystems,34,4,(December2009),1–39. amaki.2022.HPCache:Memory-EfficientOLAPThrough
doi:10.1145/1620585.1620588. ProportionalCaching.en.InDaMoN’22.AssociationforCom-
[15] 2022.HPCTuningGuideforAMDEPYC7003SeriesProces- putingMachinery,Philadelphia,PA,USA,9.doi:10.1145/
sors.en.Technicalreport. 3533737.3535100.
[16] RyanJohnson,IppokratisPandis,NikosHardavellas,Anasta- [27] PatrickE.O’Neil,ElizabethJ.O’Neil,XuedongChen,and
siaAilamaki,andBabakFalsafi.2009.Shore-MT:ascalable Stephen Revilak. 2009. The Star Schema Benchmark and
storagemanagerforthemulticoreera.en.InProceedingsof AugmentedFactTableIndexing.InTPCTC,237–252.
the12thInternationalConferenceonExtendingDatabaseTech- [28] 2019.OmniSciDBDeveloperDocumentation—OmniSciDB
nologyAdvancesinDatabaseTechnology-EDBT’09.ACM documentation.(2019).Retrieved09/01/2022fromhttps://
Press,SaintPetersburg,Russia,24.doi:10.1145/1516360. heavyai.github.io/heavydb/.
1516365. [29] JohnsPaul,ShengliangLu,andBingshengHe.2021.Database
[17] TheodoreJohnsonandDennisE.Shasha.1994.2q:Alow systemsonGPUs.FoundationsandTrends®inDatabases,11,
overheadhighperformancebuffermanagementreplacement 1,1–108.doi:10.1561/1900000076.
algorithm.InVLDB’94,Proceedingsof20thInternationalCon- [30] 2021.PG-StromManual.(2021).Retrieved04/09/2022from
ferenceonVeryLargeDataBases,September12-15,1994,Santi- https://heterodb.github.io/pg-strom/.
agodeChile,Chile.JorgeB.Bocca,MatthiasJarke,andCarlo [31] ZaidQureshi,VikramSharmaMailthody,IsaacGelado,Se-
Zaniolo,editors.MorganKaufmann,439–450. ungWonMin,AmnaMasood,JeongminPark,JinjunXiong,
[18] TimKaldewey,GuyLohman,ReneMueller,andPeterVolk. C.J.Newburn,DmitriVainbrand,I.-HsinChung,Michael
2012.GPUjoinprocessingrevisited.en.InProceedingsof Garland,WilliamDally,andWen-meiHwu.2022.BaM:A
theEighthInternationalWorkshoponDataManagementon CaseforEnablingFine-grainHighThroughput

CIDR’23,January8-11,2023,Amsterdam,TheNetherlands Nicholsonetal.
GPU-OrchestratedAccesstoStorage.en.arXiv:2203.04910 Source,Real-timeAnalyticsEngine.(January2019).Retrieved
[cs].(March2022).Retrieved08/31/2022fromhttp://arxiv. 09/01/2022fromhttps://www.uber.com/blog/aresdb/.
org/abs/2203.04910. [37] Michael Stonebraker, John Woodfill, Jeff Ranstrom, Mar-
[32] AunnRaza,PeriklisChrysogelos,PanagiotisSioulas,Vladimir guerite C. Murphy, Marc Meyer, and Eric Allman. 1983.
Indjic,Angelos-ChristosG.Anadiotis,andAnastasiaAila- Performanceenhancementstoarelationaldatabasesystem.
maki.2020.Gpu-accelerateddatamanagementunderthe ACMTrans.DatabaseSyst.,8,2,167–185.doi:10.1145/319983.
testoftime.In10thConferenceonInnovativeDataSystems 319984.
Research,CIDR2020,Amsterdam,TheNetherlands,January [38] MostakTodd.2013.AnOverviewofMapD(MassivelyParal-
12-15,2020,OnlineProceedings.www.cidrdb.org. lelDatabase).Technicalreport.MassachusettsInstituteof
[33] AllenReiter.1976.AStudyofBufferManagementPoliciesfor Technology.
DataManagementSystems.Technicalreport.WISCONSIN [39] Johannes Weiner, Niket Agarwal, Dan Schatzberg, Leon
UNIVMADISONMATHEMATICSRESEARCHCENTER. Yang,HaoWang,BlaiseSanouillet,BikashSharma,Tejun
[34] ViktorRosenfeld,SebastianBreß,andVolkerMarkl.2023. Heo,MayankJain,ChunqiangTang,andDimitriosSkarlatos.
QueryProcessingonHeterogeneousCPU/GPUSystems.en. 2022.TMO:transparentmemoryoffloadingindatacenters.
ACMComputingSurveys,55,1,(January2023),1–38.doi: en.InProceedingsofthe27thACMInternationalConference
10.1145/3485126. on Architectural Support for Programming Languages and
[35] AnilShanbhag,SamuelMadden,andXiangyaoYu.2020.A OperatingSystems.ACM,LausanneSwitzerland,(February
StudyoftheFundamentalPerformanceCharacteristicsof 2022),609–621.doi:10.1145/3503222.3507731.
GPUsandCPUsforDatabaseAnalytics.en.InProceedings [40] YuanYuan,RubaoLee,andXiaodongZhang.2013.TheYin
ofthe2020ACMSIGMODInternationalConferenceonMan- andYangofprocessingdatawarehousingqueriesonGPUde-
agementofData.ACM,PortlandORUSA,(June2020),1617– vices.en.ProceedingsoftheVLDBEndowment,6,10,(August
1632.doi:10.1145/3318464.3380595. 2013),817–828.doi:10.14778/2536206.2536210.
[36] JianShen,ZeWang,DavidWang,JeremyShi,andSteven
Chen.2019.IntroducingAresDB:Uber’sGPU-PoweredOpen