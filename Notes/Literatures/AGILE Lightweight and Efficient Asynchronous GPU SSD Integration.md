# AGILE

**Source**: AGILE.pdf
**Format**: .pdf

---

AGILE: Lightweight and Efficient Asynchronous GPU-SSD
Integration
ZhuopingYang JinmingZhuang XingzhenChen
BrownUniversity BrownUniversity BrownUniversity
Providence,RhodeIsland,USA Providence,RhodeIsland,USA Providence,RhodeIsland,USA
zhuoping_yang@brown.edu jinming_zhuang@brown.edu xingzhen_chen@brown.edu
AlexK.Jones PeipeiZhou
SyracuseUniversity BrownUniversity
Syracuse,NewYork,USA Providence,RhodeIsland,USA
akj@syr.edu peipei_zhou@brown.edu
Abstract 1 Introduction
GPUsarecriticalforcompute-intensiveapplications,yetemerging GraphicsProcessingUnits(GPUs)havebecomethedefactoac-
workloadssuchasrecommendersystems,graphanalytics,anddata celeratorwidelyusedforcomputationallyintensiveapplications
analyticsoftenexceedGPUmemorycapacity.Existingsolutions such as graphics rendering [26, 53], deep learning [26, 33], and
allowGPUstouseCPUDRAMorSSDsasexternalmemory,andthe high-performancecomputing[58,59,66].However,modernap-
GPU-centricapproachenablesGPUthreadstodirectlyissueNVMe plicationsareincreasinglydata-intensive,oftenprocessingdata
requests, further avoiding CPU intervention. However, current thatfarexceedsGPUmemorycapacity[19,31,50].Forexample,
GPU-centricapproachesadoptsynchronousI/O,forcingthreadsto training large-scale models like GPTs [1, 5] involves billions of
stallduringlongcommunicationdelays. parametersandterabytesoftrainingdata[49].Similarly,analyzing
WeproposeAGILE,alightweightasynchronousGPU-centric largegraphsforsocialnetworkingorrankingwebsitestoucheson
I/Olibrarythateliminatesdeadlockrisksandintegratesaflexi- billionsofverticesandtrillionsofedges[9].Recommendersys-
bleHBM-basedsoftwarecache.AGILEoverlapscomputationand temsalsohandledatarangingfromgigabytestopetabytes[51].
I/O,improvingperformancebyupto1.88×acrossworkloadswith Moreover,whileGPUs’computationalpowerhasincreasedrapidly,
diversecomputation-to-communicationratios.ComparedtoBaM theirmemorycapacityhasnotkeptthesamepace[19].Thesenew
onDLRM,AGILEachievesupto1.75×speedupthroughefficient trendsnecessitateinnovativememoryextensiontechniquesand
designandoverlapping;ongraphapplications,AGILEreducessoft- optimizations.
warecacheoverheadbyupto3.12×andNVMeI/Ooverheadby ToexpandGPUs’memory,existingsolutionsresorttoCPUmem-
upto2.85×;AGILEalsolowersper-threadregisterusagebyupto ory[2,44,52,65].Forexample,NvidiaUnifiedMemoryenables
1.32×. GPUsandCPUstoshareasinglememoryaddressspacesothat
GPUscanaccessCPUmemorywithoutexplicitmemorycopies[44].
However, scaling the CPU memory to tens of terabytes is still
CCSConcepts
consideredachallenge[48].AnotherapproachisextendingGPU
•Informationsystems→Storagearchitectures;•Comput- memoryusingSSDs[3,4,62],whichprovidemuchlargerspace
ingmethodologies→Parallelcomputingmethodologies;• butentailsophisticateddesignsforbetterperformance.GPUDi-
Hardware→Externalstorage. rectStorage[40]enablesdirectdatatransfersbetweenGPUsand
SSDswithoutinvolvingthememoryoftheCPUasanintermedi-
Keywords ary,therebyeliminatingtheoverheadofusingCPUmemoryas
astagingbuffer.MicrosoftproposesDeepNVMe[32],whichof-
GPUs,SSDs,AsynchronousI/O,Software-managedcache,Memory
fersadditionaloptimizations,suchasasynchronousI/Ooperations
hierarchy,Storagesystems
andintegrationwithZeRO-Infinity[50]forlargeneuralnetworks.
However,GPUDirectStorageandDeepNVMestillrequiretheCPU
ACMReferenceFormat: toinitiatethedatatransfer.Asthecomputationalworkloadsareof-
ZhuopingYang,JinmingZhuang,XingzhenChen,AlexK.Jones,andPeipei floadedontotheGPUs,theCPUlacksvisibilitytorequestsmadeby
Zhou.2025.AGILE:LightweightandEfficientAsynchronousGPU-SSD GPUthreadsinflight.Consequently,frequentsynchronizationbe-
Integration.InTheInternationalConferenceforHighPerformanceComputing, tweentheGPUandthehostCPUisnecessary,leadingtosignificant
Networking,StorageandAnalysis(SC’25),November16–21,2025,StLouis, performancedegradation[48].
MO,USA.ACM,NewYork,NY,USA,13pages.https://doi.org/10.1145/
TheemerginginterconnecttechnologyCXLisbuiltontopof
3712285.3759778
PCIeandoffersnewprotocols,suchasCXL.memoryandCXL.cache,
toefficientlyextendhostmemory[14].CXL.memoryallowsdevices
touseloadorstoreinstructionstoaccessotherdevices’memory
orstorage.CXL.cachefurtherenablesdevicestocoherentlycache
memory that physically resides on other devices. CXL-enabled
ThispaperhasbeenacceptedatSupercomputing2025.
5202
guA
62
]CD.sc[
3v56391.4052:viXra

SC’25,November16–21,2025,StLouis,MO,USA ZhuopingYangetal.
SSDsarepromisingcandidatesforhelpingmaintaincoherencefor Ourcontributionsarehighlightedasfollows:
memoryexpansionwithSSDs[63],butarenotcurrentlyacomplete • WeproposeAGILE,enablingtheGPUtoissueNVMecom-
solutionforexpandingGPUs’memory.Thisisbecausetheflash
mandsasynchronously.Tothebestofourknowledge,AGILE
memoryaccesstimeisatthemicrosecondlevel[63],whichisorders
isthefirstGPU-centricasynchronousI/Omodel.
ofmagnitudehigherthanHigh-BandwidthMemory(HBM),where • Weimplementarobustlock-basedasynchronoustransac-
CXLisprimarilydeployed.AsolutiontohidethelatencyofSSDs
tionmechanism,whichallowsGPUthreadstoissueNVMe
isstillnecessary.
commandsasynchronouslywithoutholdinganylocks.Our
Overlapping memory access with computation is a common
approachefficientlyeliminatespossibledeadlocksanddata
technique used to tolerate slow data movement [8, 20, 62]. For
hazards.
example,ALCOP[22]utilizestheCUDA-providedasynchronous • WeintegrateaflexiblesoftwarecachehierarchyinAGILE
datamovementAPItoexploremulti-stagepipelining.Thisavoids
toutilizeGPUHBM,whichallowsuserstocustomizetheir
GPUidletimecausedbysynchronousdatamovement.However,
cachepolicyandprovidesasimpleinterfaceforincreased
insideaGPUkernel,onlyasynchronousdatamovementfromglobal
usability.
memory(orpinnedhostmemory)tosharedmemorycanbeinitiated • WeevaluateAGILEonmicro-benchmarkingandapplica-
usingexistingCUDAAPIs[30],andtheGPU’ssharedmemoryis
tions.TheresultsshowthatAGILEenablesoverlappingat
limited, e.g., 164 KB per Streaming Multiprocessor on an A100 thethreadlevelandachievesupto1.88×speedupoverasyn-
GPU[41].Usingalargerbufferforasynchronousloadsperthread
chronousI/Omodel.Comparedwithstate-of-the-artwork,
hasbeendemonstratedtohavemoreperformancebenefitswhen BaM,AGILEachievesupto1.75×reductioninend-to-end
usinganoverlappingtechnique[28].
execution time on DLRMs; in graph applications, AGILE
GPU-centricstorageaccessisanothermethodtoavoidthesyn-
demonstrates lower API overhead in managing software
chronizationoverheadbetweenGPUsandCPUs.BaM[48]isthe cacheandNVMeI/Orequestsupto3.12×and2.85×,respec-
firstGPU-centricmethodthatenablesGPUthreadstodirectlyini-
tively;furthermore,AGILEconsumesfewerregistersand
tiateNVMeI/OrequestswhilebypassingthehostCPU.Ittolerates exhibitsupto1.32×reductionintheusageofregisters.
longSSDaccesslatencyviamassiveconcurrentI/Osenabledby • We open-source AGILE with detailed guides for users to
theGPU’shighparallelism.ThisapproacheliminatesCPUinter-
leverageAGILEandcustomizeAGILEcomponentsinvarious
ventionoverhead.However,itadoptsasynchronousaccessmodel,
applications:https://github.com/arc-research-lab/AGILE
andthreadsmustwaitfortheI/Orequeststobecompletedbefore
concurrentlystartingcomputationorissuingothercommands.As
2 Background&DesignChallenges
aresult,communicationtimecannotbehiddenineachGPUthread,
Inthissection,wefirstintroducethebackgroundoftheNVMepro-
andapplicationsmustrelyonruntimewarpschedulingtopreempt
tocolandhowGPUthreadsarescheduledandhidememoryaccess
stalledwarpsandscheduleotherreadywarpstoavoidwasting
latencyinCUDA.Then,wepresentthechallengesinsupporting
GPUcycles[25],whichisnotalwayseffectiveandleavesspacefor
anasynchronousI/OmodelonGPUs.
furtheroptimizationopportunities.
Incontrast,anasynchronousI/Omodelcanbettertoleratelong
2.1 BackgroundofNVMeProtocol
latencyinaccessingSSDsbyoverlappingcommunicationwithcom-
putation[27].However,designingaGPU-centricasynchronousI/O Non-VolatileMemoryExpress(NVMe)isastandardprotocolthat
modelischallenging,asthemassiveGPUthreadsmaycompete allows software to communicate with non-volatile memory via
onsharedresources,e.g.,NVMequeues,software-definedcache, PCIe[46].SoftwarecanaccessanNVMeSSDviaanI/Oqueuepair,
etc.,leadingtoperformancedegradation.Usinglocksbeforeaccess- consistingofasubmissionqueue(SQ)andacompletionqueue(CQ).
ingthesesharedresourcesisacommonmethodtoavoidresource WithanI/Oqueuepair,thesoftwareisresponsibleformaintaining
conflicts,butinanasynchronousmodel,allowingthreadstohold theSQtailpointer,whichindicatesthenextavailableSQentry
lockscanleadtodeadlockissues.Forinstance,ifmultiplethreads (SQE) for a new command, and the CQ head pointer, which is
asynchronouslyrequestSSDdata,arequestqueuecanfillpriorto used to receive the next completion from the SSD. To issue an
commandsthatcheckforcompletionandsubsequentlyclearthe NVMecommand,thesoftwarewritesanewcommandtothenext
completedrequestfromtherequestqueue,creatingadeadlock.In availableSQEandnotifiesthechangesinSQtotheSSDbymoving
addition,efficientlockhandlingisnecessarytoavoidperformance the SQ tail pointer and updating the new SQ tail by writing to
degradationfromthesoftwareAPIside. the corresponding SQ doorbell register in the SSD’s PCIe Base
Moreover,BaM[48]onlysupportsafixedcachepolicyforitssoft- AddressRegisters(BAR).Then,theSSDfetchesthenewlyadded
warecacheonGPUs’HBM.Thislimitsthecachepolicycustomiza- command,andafterexecution,theSSDreturnsacompletionto
tionforvariousapplications.Asnewcachingpolicies[17,35,47]are thenextavailableCQentry(CQE).Afterreceivingacompletion,
continuouslydesigned,itisimportantforstoragesystemstochoose thesoftwareneedstorespondtoSSDbyincreasingtheCQhead
thebestsoftware-definedcachingpolicyundervariousworkloads pointerandupdatingtheassociatedCQdoorbellregister.Thisis
andrequirements[60]. necessaryforSSDstoreleasetheCQEandreuseitforanother
Toaddresstheseneedsandchallenges,weproposeAGILE,a command;otherwise,theSSDswillstallwhilewaitingforavailable
GPU-centricGPU-SSDintegrationthatenablesGPUthreadsto CQEs.Thisqueue-basedapproachalsoallowssoftwaretoissue
issueNVMerequestsasynchronouslyandefficientlywhileelimi- multiplecommandsinabatchandincreasetheSQtailpointerby
natingdeadlockrisks. thenumberofnewlyinsertedcommands.Thesoftwarecandetect

AGILE:LightweightandEfficientAsynchronousGPU-SSDIntegration SC’25,November16–21,2025,StLouis,MO,USA
Thread-1 Thread-2
andprocessthecompletionmessagebyeitherpollingtheCQor
①
respondingtoaninterrupttriggeredbytheSSD.Toachievehigh SQ
parallelism,NVMeSSDsallowmultipleSQs/CQstoberegistered
②
andusedconcurrently. ③Not reachable! checking available entries
④Xrelease the SQ entries
2.2 GPUThreadsScheduling&Asynchronous
DataMovementinCUDA CQ
Tomeettheincreasinghighthroughputdemands,modernGPUs Figure 1: A deadlock example caused by sharing NVMe
can execute tens of thousands of threads in parallel via Single queuesinasynchronousexecution.
Instruction,MultipleThreads(SIMT)[36].TheGPUthreadsare
continuetocheckforthenextavailableSQentry○2.Therefore,
groupedintothreadblocks,andthethreadsineachthreadblock
boththreadscannotreach○3,wheretheycheckthecompletionsin
willbescheduledontothesameStreamingMultiprocessor(SM)
CQtoconfirmtheirissuedcommandshavebeenprocessedbythe
[38].Ifthehardwareresource,suchasthenumberofregistersand
SSDandthenreleaselocksinSQ.Eventhoughthecorresponding
thesharedmemory,isenoughforanSMtoservemorethanone
completionsbecomeavailableintheCQ,ifThreads-1and2own
threadblock,eachSMcanaccommodatemultiplethreadblocks
alltheoccupiedSQentries,nonecanbereleased○4,resultingina
simultaneously.CurrentGPUsadoptastaticresourceallocation
deadlock.
model,whichcancauseSMunderutilization.Oncethethreadblocks
Forlargernumbersofthreads,thisdeadlockremainsaconcern
arescheduledontoSMs,theywilloccupytheSMsuntiltheirtasks
asmanythreadswillrequestmultipleoperandsinline3,hence,
arefinished.Thispreventsnewthreadblocksfrombeingscheduled,
fillingthequeuepriortoanyonereaching○3.
evenifthescheduledthreadblocksarestalledduetosomehigh-
latencyoperations.ThisproblemofSMunderutilizationismitigated 2.3.2 DeadlockintheSoftwareCache. AGILEpromisestooffer
by warp-level scheduling. The SM will schedule threads at the flexibilityinthesoftwarecachepolicy,andtherefore,eliminating
granularityofwarps(typically32threadsinawarp).Ifsomewarps thepotentialfordeadlockcausedbythesoftwarecacheisnecessary.
stall due to high-latency operations such as fetching data from Acommonscenarioresultinginadeadlockissimultaneousthreads
memoryorSSDs,otherreadywarpsfromthesamethreadblock accessingmultiplecachelines.Forexample,onecomputekernel
ordifferentthreadblockscanbescheduledtokeeptheSMbusy. needsmultipleoperandsthatarestoredindifferentcachelines.To
However,thismechanismisnotsufficient,especiallywhenmany preventredundantSSDaccesses,onceathreadchecksthesoftware
warpsencountermemoryorI/Ostalls. cacheandtherequesteddataisfound—i.e.,acachehitoccurs—
Toavoidstallscausedbymemoryaccess,userscanuseasyn- accesstothecorrespondingcachelinesmustbeatomictoavoid
chronousdatamovementAPIssuchascuda::memcpy_async[39] evictionbeforeaccessesinprocessarecompleted.Whenmultiple
orcp.async[36]inCUDAtohidelatencywithcomputationtasks. threadsblockcachelineevictionwhilerequestingnewcachelines,
However,theseasynchronousdatamovementAPIsonlyallowdata adeadlockcouldoccur.
transfers from GPU global memory or pinned host memory to 2.3.3 PotentialPerformanceDegradation. Flashmemorycannotbe
shared memory in SMs [30]. Using larger buffers for asynchro- accessedrandomly,anddataismanagedatacoarse-grainedpage
nousloadswillleadtoahigherperformanceincrease[28],butthe level,typically4KBperpage[18].Therefore,thesoftwarecache
sharedmemoryislimitedineachSM,e.g.,164KBperSMonan lineshouldalignwiththeSSDs’granularity.Thisalignmentcan
A100GPU[41]. avoidredundantI/Oswhenmultiplethreadsaccessdifferentparts
ofthesameSSDpageconcurrently.Toensurecorrectnessduring
2.3 DesignChallengesinAsynchronous
accessingthesamecachelinesimultaneously,atomicoperations
GPU-SSDintegration
are required to avoid conflicts and data hazards. It is crucial to
2.3.1 DeadlockinNVMeQueues. Designinganefficientasynchro- implementanefficientlockmechanismtopreventperformance
nousmodelforGPU-SSDintegrationischallengingasamassive degradationanddeadlock.
numberofthreadssharelimitedresourcessuchasNVMequeues Furthermore,inNVMequeues,althoughmultiplethreadscan
andthesoftwarecache.Acquiringlocksbeforeaccessingthesere- inserttheircommandsintothesameSQconcurrently,updating
sourcesisnecessarytoavoidconflicts,butcanintroducedeadlock. theSQdoorbellregistermustbeserialized.Thisisbecauseconcur-
ForNVMequeues,whenathreadputsanewNVMecommand rentwritestothesamedoorbellregistersmaycauseinconsistent
intoanSQ,thecorrespondingSQentrywillremainlockedtopre- SQtailvaluesinSSDs.Besides,theserializationensuresmemory
ventotherthreadsfromusingthesameentryuntiltheSSDhas consistencysothatthenewlysubmittedcommandsarevisiblein
receivedthecommand. globalmemorybeforetheSQdoorbellregistersareupdated.Im-
Figure1illustratesanexampleofdeadlockwhenThread-1and properhandlingofthisserializationmayalsocauseperformance
Thread-2 need to execute NVMe commands asynchronously in degradation.
parallel.First,Thread-1successfullyacquirestheSQandplacesits Lastly,real-worldSSDdevicesonlysupportasmallnumberof
readrequestintoanavailableentry.However,beforethisthread I/OqueuepairscomparedtothemassivelivingGPUthreads.For
canmovetoline3,Thread-2gainsaccesstotheSQandaddsits example,amaximumof128queuepairsinSamsung980PRONVMe
request to the last available entry, which fills the SQ ○1. Now, SSD[57].Therefore,thecompletionsfromSSDstendtoconcentrate
becausetheSQisfull,boththreadsbecomestuckatLine3,they inasmallnumberofcompletionqueues,whichrequiresanefficient

SC’25,November16–21,2025,StLouis,MO,USA ZhuopingYangetal.
andlow-overheadmechanismtoconsumethecompletionstoavoid CPUinterventionandmustbeperformedatthebeginningofthe
stallsfromSSDs. programusingAGILE.
3 AGILEDesign&Implementation
Inthissection,wewillfirstgiveanoverviewofAGILEinSection3.1.
Then,wepresentthemaincomponentsofAGILE.InSection3.2,we
willdiscusshowAGILEavoidsthedeadlockproblemresultingfrom
NVMequeuesandprocessescompletionsfromSSDsinparallel. GPU-HBM
WewilldiscusshowAGILEdealswiththeserializationprocess
requiredbytheNVMeSQsandcoalescingredundantrequestsin
User
Section3.3.InSection3.4,wewillpresentthesoftware-managed AGILE CTRL Service
code
cacheinAGILEanddiscusshowAGILEextendscachecoherencyto
user-specifiedbuffers.Finally,wewillpresentanexampleprogram, GPU GPU
illustratinghowAGILEcanbeused,andintroduceadebugoption SW-Cache SW-Cache
providedinAGILE. Interface CTRL
3.1 OverviewofAGILESystem
Figure2presentsanoverviewoftheAGILEsystem,whichenables
efficientasynchronousGPU-SSDcommunication.Thesystemin-
volvesthreetypesofhardware,includingSSDs,aGPU,andahost
CPU.ThehostCPUmanagesadminqueues,locatedinDRAM,to
establishGPU-SSDPCIepeer-to-peer(P2P)communication.The
NVMeSSDsareconnectedtothesystemviaPCIe,theirPCIeBARs
areexposedtothehostCPUformanagement,andtheirdoorbellreg-
istersareregisteredtoGPUforGPU-centricdatatransfers.Within
theGPU,AGILEconsistsofalightweightservicetohandleI/O
queues for users (Section 3.2), a software controller to manage
cached data in HBM (Section 3.4), and a Share Table to extend
cachecoherencytouser-specifiedbuffers(Section3.4.1).Userscan
interactwithAGILEthroughtheAGILEcontroller(AGILECTRL),
whichprovidessimpleAPIsforrequestingoraccessingdatain
SSDsorthesoftwarecache.
To establish the PCIe P2P communication, the SSDs and the
GPUmustbeabletoaccesstheotherdevice’smemory.Toletan
NVMeSSDaccessI/Oqueues(SQs/CQs)andthesoftwarecache,
we need to allocate a contiguous memory space on GPU HBM,
pinthememoryspacetoavoidbeingswappedout,andgetthe
physicaladdressofthememoryspacetoenableDirectMemory
Access(DMA)fortheSSDtoaccesstheGPUHBM.GDRCopy[42]
isdesignedfordirectGPUmemoryaccessfromthird-partydevices.
Itrunsinkernelspaceandservesuserspacecallsforallocatingand
pinningcontiguousmemoryontheGPU.WemodifytheGDRCopy
kernelmoduleandinvokenvidia_p2p_put_pagesinthekernel
space,enablinguserspaceapplicationstoaccessthemappingtable
thattranslatesvirtualaddressesintophysicaladdressesofGPU
memory.Then,thephysicaladdressesofSQs/CQsareregisteredto
SSDsviatheadminqueuesonthehostCPU.TolettheGPUnotify
NVMe SSDs after generating new commands, we use memory-
mapping(mmap)toexposetheSSDs’PCIeBARtouserspaceandthen
registerthedoorbellregisterstotheGPUusingcudaHostRegister
withthecudaHostRegisterIoMemoryflag.Afterthisinitialization
process,theGPUthreadscaninsertNVMecommandstoSQsin
HBMandupdatethedoorbellregisterstonotifytheNVMeSSDs
directly,andtheNVMeSSDsareabletofetchcommandsinGPU
HBM,processthem,andupdatethecompletionmessagestoCQs
inGPUHBMdirectly.InAGILE,theinitializationprocessrequires
sDSS
…
UPG
UPC
Control Path Data Path
NVME0 NVME1 NVME2
PCIe BARDB Reg PCIe BARDB Reg PCIe BARDB Reg
SQ CQ SQ CQ … SW-Cache
IO Queues
Share-Table
Application
kernels
CPU-DRAM
Admin Queues
Host Code
Figure2:OverviewofsystemarchitectureadoptingAGILE.
AGILEprovidestwotypesofasynchronousAPIsandanarray-
likesynchronousAPI.TheasynchronousAPIprefetch(src)is
usedtoissuedatarequestsfromSSDstotheGPUsoftwarecache,
andthentheuserthreadscanaccessthedatadirectlyintheGPU
softwarecache.AnotherasynchronousAPI,async_issue(src,dst),
issimilartocuda::memcpy_async[39]orcp.async[36]inCUDA,
butthesrcanddstinAGILEaremoreflexibleandcanbeeither
SSDs’addressesoruser-specifiedbuffersinGPUs’globalmem-
ory.Byusinguser-specifiedbufferswithasync_issue(src,dst),
GPUthreadscansavemultipledatachunksforlaterusesafely
withoutholdinglocksinthesoftwarecache,therebyavoidingthe
deadlocksdescribedinSection2.3.2.However,theincreasedflex-
ibilityof srcanddstinasync_issue(src,dst)mayintroduce
data hazards, and we will present our solution in Section 3.4.1.
Theasync_issue(src,dst)willreturnabarriertolettheuser
threadsknowifthedatatransferiscompleted.Lastly,thearray-like
synchronousAPIallowsuserstosimplyviewtheSSDsasatwo-
dimensionalarray,andAGILEautomaticallychecksthesoftware
cacheandissuesrequestsifthedataisnotavailable.
3.2 AGILEService
As mentioned in Section 2.3, allowing threads to hold locks on
NVMequeuesisriskyandcancausedeadlock.However,locking
SQsisnecessarysothatcommandsdonotcollide.Toaddressthis
problem,weproposealightweightAGILEservicethatrunsinthe
backgroundontheGPUandinteractswithuserthreads.
3.2.1 AvoiddeadlockfromNVMequeues. Toeliminatethedead-
lockrisk,AGILEcreatesalightweightkerneldaemonontheGPU
tokeepcheckingcompletionqueueentries(CQE)forallregistered
NVMeCQsinanon-blockingfashion.Thisservicefreestheuser
threadsfromtheburdenofprocessingcompletionmessagesand
automaticallyreleasessharedresourcesforuserthreadsaftercom-
pletion.OncetheAGILEservicereceivesacompletionfromthe
CQs,thecorrespondinglocksinSQswillbereleased.Thisallows

AGILE:LightweightandEfficientAsynchronousGPU-SSDIntegration SC’25,November16–21,2025,StLouis,MO,USA
additionalSQrequeststoproceedandavoidsdeadlockevenwhen Algorithm1Warp-centricCQpolling
userthreadsissuemultiplerequestcommands.
1:
functionCQ_Polling(𝑐𝑞_𝑖𝑑𝑥)
2:
𝑜𝑓𝑓𝑠𝑒𝑡,𝑚𝑎𝑠𝑘,𝑝ℎ𝑎𝑠𝑒_𝑏𝑖𝑡 ←𝑙𝑜𝑎𝑑_𝐶𝑄(𝑐𝑞_𝑖𝑑𝑥)
User Thread AGILE Service SQ SSD 3: if𝑚𝑎𝑠𝑘[𝑤𝑎𝑟𝑝_𝑖𝑑𝑥] ==0then
① write 4: 𝑝𝑜𝑠 ←𝑜𝑓𝑓𝑠𝑒𝑡+𝑤𝑎𝑟𝑝_𝑖𝑑𝑥
lock lock-SQE
release
5:
𝑣𝑎𝑙𝑖𝑑 ←𝑝𝑟𝑜𝑐𝑒𝑠𝑠_𝐶𝑄𝐸(𝑐𝑞_𝑖𝑑𝑥,𝑝𝑜𝑠,𝑝ℎ𝑎𝑠𝑒_𝑏𝑖𝑡)
unlock ② Release SQ 6:
𝑚𝑎𝑠𝑘[𝑤𝑎𝑟𝑝_𝑖𝑑𝑥] ←𝑣𝑎𝑙𝑖𝑑
④
check ③ 7: endif
a unlock a Notify Thread 8: if𝑚𝑎𝑠𝑘 ==0𝑥𝐹𝐹𝐹𝐹𝐹𝐹𝐹𝐹 then
9: 𝑚𝑎𝑠𝑘 ←0
Figure3:AvoidingNVMeQueueDeadlocksinAGILE.
10:
𝑢𝑝𝑑𝑎𝑡𝑒_𝐶𝑄(𝑐𝑞_𝑖𝑑𝑥,𝑜𝑓𝑓𝑠𝑒𝑡)
Figure3illustratestheprocessofhowtheAGILEserviceassists 11: endif
userthreadsinissuingcommands.InFigure3line2,whenauser 12:
𝑢𝑝𝑑𝑎𝑡𝑒_𝑚𝑎𝑠𝑘(𝑐𝑞_𝑖𝑑𝑥,𝑚𝑎𝑠𝑘)
threadsuccessfullylockstheSQ,itcansafelyenqueuethecommand 13: endfunction
intotheSQentry○1.Then,itwillhandofflock-SQEtotheAGILE
allthreadsinthewarpdetectvalidcompletions,indicatedbythe
serviceandreceivebackabarrier(locka)representingthestatusof
maskbeingfullyset,thepollingserviceconsidersthewindowfully
thetransaction.Thus,whenathreadreacheslines2–3andcannot
processed.Ifthewindowisfullyprocessed,thewarpwillupdate
additsrequeststotheSQbecauseitisfull,oncetheAGILEservice
theCQdoorbellregistertonotifytheSSDandresetthemaskforthe
receivescompletionsfromSSDs,itcanreleasetheappropriateSQ
nextround(lines9-10).Themaskwillbeupdatedeachtimetosave
entrydirectlyandthencleartheappropriatetransactionlock○2
thecurrentstatusofthetargetCQ(line12).Thiswarp-coordinated
sothattheuserthreadwillnotbeblockedforever.Meanwhile,the
approachincreasestheparallelisminprocessingeachCQwhile
AGILEservicewillnotifythecorrespondingbarrierbyclearingthe
minimizingthedivergenceacrossthreadsinawarpbecauseall
locka○3 toindicatethatthetransactionisfinished.Finally,inline
threadsoperateonphysicallycontiguousCQEsandfollowthesame
5,ifthethreadarrivesatline5priortotheSSDaccesscompletion,
pollinglogic.
itwillwaitfortheAGILEservicetoclearthelocka○4.
Sincethecompletionsmaybereturnedoutoforderrelativetothe
3.3 AGILERequestIssuingMechanism
issuedcommands,theAGILEservicetracksthemappingbetween
each completion and its corresponding SQE via the Command AsdiscussedinSection2.3.3,theSQsrequireanefficientserial-
Identifier(CID),whichisa16-bitfieldintheNVMecommandand izationmechanismbeforeupdatingtheSQdoorbellregistersto
shouldbeuniquetoidentifycommandswithinabatchusingthe avoidperformancedegradation.Inthissubsection,wefirstpresent
sameSQ. howuserthreadsissueNVMecommands.Then,weillustratehow
AGILEcoalescesredundantrequestsatthewarplevel.
3.2.2 PollingCompletionQueues(CQs). ProcessingCQsefficiently
iscriticaltosustainhighthroughputinaGPU-centricasynchro- 3.3.1 SerializationprocessinNVMeSQs. InAGILE,eachSQEis
nousI/Omodel.Inpractice,theNVMeSSDsonlysupportalimited associatedwithalockthatcanhavethreepossiblestates:EMPTY,
numberofCQs.Forexample,theSamsung980PRONVMeSSD UPDATED,andISSUED.Algorithm2illustratestheserializationpro-
supportsupto128CQs[57].Incontrast,GPUapplicationstypi- cessforissuingNVMecommands.Whenauserthreadneedsto
callyinvolveagreatnumberofthreads,manyofwhichneedto issueanNVMecommand,itfirstselectsanSQassociatedwiththe
sharethesameCQ.Asaresult,completionsmaytendtoconcen- targetSSDbasedonitsthreadindexandattemptstosubmitthe
trateinasmallnumberofCQs,whichcouldleadtocontention commandtothisSQifithasanavailableSQEforanewcommand
andperformancebottlenecks.Toensuretimelycompletionprocess- (line2).IftheSQisfull,thethreadwilltrytosubmitcommandsto
ing,AGILEincreasesintra-CQpollingparallelismbyadoptinga anotherSQbysimplyincreasingtheindexofthetargetSQ.After
warp-centricCQpollingstrategy,whereeachwarpconcurrently enqueuingthecommandstoanSQ(line6),AGILEsetsthestateof
processes32CQEswithinaCQateveryiteration.Meanwhile,AG- thecorrespondingSQE’slocktoUPDATED,whichindicatesthecom-
ILEonlyusesasmallnumberofwarpsforCQpollingandrotates mandisnowvisibleintheglobalmemoryandcanbesafelynotified
acrossallregisteredCQsinaround-robinfashion. totheSSD.ToensuretheSSDisproperlynotified,allthreadswill
Algorithm1describesthewarp-centricCQpollingroutineused attempttoupdatetheassociatedSQdoorbellregisterandverify
intheAGILEservicetoprocessCQsefficiently.Wheninvoked,the whethertheircommandshavebeenissued(line9).Athreadthat
warpisassignedwithaspecificCQ,andeachthreadisresponsible successfullyacquiresthelockfortheSQdoorbellregisterincreases
forcheckingasingleCQEwithina32-entrywindow.Inthewarp- theSQtail(line15),duringwhichitscanstheSQEsinorderand
centricCQpollingservice,thethreadsfirstloadthecurrentpolling updatestheSQEs’statesfromUPDATEDtoISSUED.Thisprocess
offset,theCQphasebitformonitoringthechangesinCQEs,anda continues until it encounters an SQE in the EMPTY state, which
32-bitmaskthatrepresentsthecompletionstatusoftheCQEs(line eithermarkstheendofthecurrentbatchofcommandsorindicates
2).Ifthecorrespondingbitinthemaskisunset,whichindicates thatthecorrespondingSQEisnotvisibleintheglobalmemory
thecompletionisnotreceived,thethreadswillcomparetheCQEs’ yet.Then,thisthreadwillupdatetheSQdoorbellregisterandre-
phasebitwiththeexpectedvalue.Ifnewcompletionsarefound, leasethelock(line15).Finally,allthreadsverifythestatesoftheir
theassociatebitsinthemaskwillbesetto1(lines5-6).When respectiveSQEs(line17)toconfirmifthecommandshavebeen

SC’25,November16–21,2025,StLouis,MO,USA ZhuopingYangetal.
successfullyissuedtotheSSD.Oncethecompletionsarereceived aswellasinterfacesforuserstocustomizecachepolicies.InAGILE,
bytheAGILEservice,thecorrespondingSQEs’statesareresetto all SSD data accesses are routed through the software cache to
EMPTY,allowingthemtobereusedforfuturecommands. ensurecoherencyandtocoalescetheredundantSSDrequests.
InAGILE,eachcachelinehasfourpossiblestates:INVALID,BUSY,
READY,andMODIFIED.Whenuserthreadsrequestanydata,AGILE
Algorithm2SerializationprocessinSQs
firstcheckstheuser-specifiedcachepolicyandobtainsthetarget
1:
functionAttempt_Enqeue(𝑠𝑞_𝑖𝑑𝑥,𝑐𝑚𝑑)
cachelineindex.Therewillbe4possiblecases:(a)cachehitand
2:
𝑠𝑞𝑒 =𝑐ℎ𝑒𝑐𝑘_𝑓𝑢𝑙𝑙(𝑠𝑞_𝑖𝑑𝑥)
dataisvalid.IfthestateofthecachelineisREADY,orMODIFIED,
3: if𝑠𝑞𝑒 ==−1then it means the data is already in GPU HBM, and the threads can
4: returnfalse directlyobtaintherequesteddata.(b)cachemissandnoeviction
5: endif required.Inthiscase,thestateisINVALID,andthethreadwill
6:
𝑒𝑛𝑞𝑢𝑒𝑢𝑒_𝑐𝑚𝑑(𝑠𝑞_𝑖𝑑𝑥,𝑠𝑞𝑒,𝑐𝑚𝑑)
issueanNVMecommandtoloaddatafromSSDtoHBMandchange
7:
𝑢𝑝𝑑𝑎𝑡𝑒_𝑆𝑄𝐸(𝑠𝑞_𝑖𝑑𝑥,𝑠𝑞𝑒,𝐸𝑁𝑄𝑈𝐸𝑈𝐸)
thecachelinestatetoBUSY.(c)cachehit,butthedataisinvalid.
8: repeat ThishappenswhenthecachelinestateisBUSY.Thismeansthe
9:
𝑠𝑡𝑎𝑡𝑢𝑠 ←𝐴𝑡𝑡𝑒𝑚𝑝𝑡_𝑆𝑄𝐷𝐵(𝑠𝑞_𝑖𝑑𝑥,𝑠𝑞𝑒)
datahasalreadybeenrequestedbyanotherthread,andthisthread
10:
until𝑠𝑡𝑎𝑡𝑢𝑠 ==𝑆𝑈𝐶𝐶𝐸𝑆𝑆
will either wait (synchronous APIs) or append its buffer to the
11: returntrue correspondinglinkedlist.(d)cachemissandevictionrequired.
12: endfunction Thisoccurswhenthecachelineisreserved,andthestateisnot
13:
functionAttempt_SQDB(𝑠𝑞_𝑖𝑑𝑥,𝑠𝑞𝑒)
INVALID.Then,AGILEwilltriggeracachelineevictionifthecache
14:
if𝑎𝑐𝑞𝑢𝑖𝑟𝑒_𝑙𝑜𝑐𝑘(𝑠𝑞_𝑖𝑑𝑥)then
linestateisREADY,MODIFIED,orBUSY.AGILEwillsimplyresetthe
15:
𝑚𝑜𝑣𝑒_𝑆𝑄_𝑡𝑎𝑖𝑙(𝑠𝑞_𝑖𝑑𝑥,𝑠𝑞𝑒)
cachelineifthestateisREADY,andwriteMODIFIEDcachelineto
16: endif the SSDs and change the state to BUSY. If the state is BUSY, the
17:
return𝑐ℎ𝑒𝑐𝑘_𝑆𝑄𝐸(𝑠𝑞_𝑖𝑑𝑥,𝑠𝑞𝑒)
correspondingcachelinecannotbeevicteduntiltheprocessingis
18: endfunction finished,andAGILEwilllettheuser-specifiedGPUsoftwarecache
policydecidewhethertowaitorfindanothercacheline.
3.3.2 Coalescingidenticalrequestsatthewarplevel. Toavoidre-
dundantrequests,AGILEcoalescesidenticaldatarequestsissued 3.4.1 ExtendingCoherencytoUser-specifiedBuffers. Itisworthnot-
bydifferentthreads,whichisessentialbecauseuserthreadsmay ingthatasync_issue(src,dst)inAGILEisconceptuallysimilar
independentlyrequestthesamedatachunkfromSSDs. tocuda::memcpy_async[39]orcp.async[36]inCUDA,which
Forprefetch()andthearray-likeinterface,AGILEemploys
enables asynchronous data movement to hide memory latency.
atwo-levelcoalescingstrategy.Thefirstleveloccursatthewarp However,theCUDA’sasynchronousAPIsarelimitedtospecific
level,whereCUDAwarp-levelprimitives[45]areusedtoexamine memorypaths,i.e.,transferringdatafromtheglobalmemoryor
duplicaterequests.Then,AGILEselectsonethreadtoforwardthe pinnedhostmemoryintothesharedmemoryontheSM[30].In
requesttothesecond-levelcoalescingstage.Thesecondlevelis contrast,async_issue(src,dst)inAGILEprovidesgreaterflexi-
handledbytheAGILEsoftwarecache(Section3.4),whichfilters bilityinthesourceanddestinationaddresses,bothofwhichcan
remainingredundantrequeststhatarenoteliminatedinthefirst beSSDdataoruser-specifiedGPUbuffers.Thisenhancedflexi-
warp-levelcoalescingstage.AGILEprioritizesthewarp-levelcoa- bility,however,introducespotentialdatahazards.Forexample,a
lescingsinceaccessingthesharedsoftwarecacherequiresatomic threadmayissueanasync_issue(src,dst)tofetchdatafrom
operationstomaintainconsistency,whichcreatescriticalsections SSDdirectlytotheuser-specifiedbuffer,whileotherthreadscan
andserializesexecution.Thisserializationcancausestallsanddif- concurrentlyaccessthesamedatafromtheAGILEsoftwarecache.
ferentexecutionpathsforthreadsinawarp,whichintroduceswarp Iftheuser-specifiedbufferorsoftwarecacheismodifiedwithout
divergenceanddegradesoverallGPUperformance. coordination,datahazardssuchasread-after-write(RAW),write-
Forasync_issue(src,dst),whichmimicscp.async[36]or
after-read(WAR),andwrite-after-write(WAW)canoccur,where
cuda::memcpy_async[39]inCUDAandnowarp-levelcoalescing
threadsmayobservestaleorpartiallyupdateddata.
isperformed.Evenifthreadsinawarprequestthesamedata,each Toaddressthesedatahazards,AGILEprovidesacompile-time
threadwillstillobtainitsowncopyoftherequesteddata.Therefore, optiontoenabletheuser-specifiedbufferstobeintegratedinto
inAGILE,theredundantrequestsareonlycoalescedatthesoftware theAGILEsoftwarecacheandsafelysharedamongmultipleuser
cachelevel,andAGILEdelegatesthewarpleveloptimizationto threads.Ifenabled,bydefault,AGILEwillmaintainahashtable-
users.Moreover,async_issue(src,dst)providesmoreflexibility
basedShareTabletotrackuser-specifiedbuffers’ownershipandap-
comparedtotheCUDAAPIs,whichcanintroducepotentialdata plyasoftware-managedcoherencyprotocolinspiredbytheMOESI
hazards.ThesedatahazardsareaddressedthroughtheShareTable model[56]toensureconsistencyacrossdifferentaccesspaths.
mechanism,whichwillbedescribedinSection3.4.1. UnliketheoriginalMOESImodel,whereeachthreadmaintains
itsowncopyofdata,AGILEmaintainsthecoherencybysharing
3.4 AGILESoftwareCache
thepointerstotheuser-specifiedbuffers,whichallowsallthreads
Asoftware-managedcachecansignificantlyreduceSSDI/Otraffic toaccessthesamephysicalmemoryregion.Thiseliminatesredun-
bystoringfrequentlyaccessedSSDdataonthedevice[21,29,48]. dantdataduplicationandavoidsextracopiesbetweenthreads.In
AGILEalsoenablesthisfeatureandprovidesbuilt-incachepolicies AGILE,theMOESIisreinterpretedtoreflecttherelationshipand

AGILE:LightweightandEfficientAsynchronousGPU-SSDIntegration SC’25,November16–21,2025,StLouis,MO,USA
|     |     |     |     | 1 class GPUCache:public |     | GPUCacheBase<GPUCache>{...}; |     |     |     |
| --- | --- | --- | --- | ----------------------- | --- | ---------------------------- | --- | --- | --- |
responsibilitybetweenuserthreadsandtheirsharedbuffers.Specif-
|                                                              |     |     |     | 2 #define    | AGILE_CTRL | AgileCtrl<GPUCache, |     | ShareTable> |     |
| ------------------------------------------------------------ | --- | --- | --- | ------------ | ---------- | ------------------- | --- | ----------- | --- |
| ically,whenathreadrequestsdataforitsbuffer,thethreadreceives |     |     |     | 3 __global__ |            |                     |     |             |     |
exclusiveownershipofthatbuffer.Meanwhile,theShareTable 4 void kernel(AGILE_CTRL * ctrl, void * data){
| recordsthesourceofthedatainthebufferandstoresthepointer |     |     |     | 5 ... |     |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
tothisbuffer.Whenotherthreadsrequestthesamesourceofdata, 6 AgileLockChain chain;
| theShareTablewillreturntheexistingpointertothatbufferand |     |     |     | 7              |       |          |     |     |     |
| -------------------------------------------------------- | --- | --- | --- | -------------- | ----- | -------- | --- | --- | --- |
|                                                          |     |     |     | 8 // Method-1: | AGILE | prefetch |     |     |     |
incrementacorrespondingreferencecounterofthesharedbuffer
|     |     |     |     | 9 ctrl->prefetch(dev_idx, |     | blk_idx, |     | chain); |     |
| --- | --- | --- | --- | ------------------------- | --- | -------- | --- | ------- | --- |
toindicatetheusage.Ifanythreadsattempttomodifythebuffer,
10
thebufferwillswitchtotheModifiedState,andtheoriginalowner
|     |     |     |     | 11 // Method-2: | AGILE | async_issue |     |     |     |
| --- | --- | --- | --- | --------------- | ----- | ----------- | --- | --- | --- |
ofthebufferwillberesponsibleforpropagatingtheupdatestoL2
|     |     |     |     | 12 AgileBufPtr | buf(data | + tid | * ctrl->line_size); |     |     |
| --- | --- | --- | --- | -------------- | -------- | ----- | ------------------- | --- | --- |
cache–softwarecacheinGPUHBM–afterotherthreadsfinish
|     |     |     |     | 13 ctrl->asyncRead(dev_idx, |     |     | blk_idx, | buf, chain); |     |
| --- | --- | --- | --- | --------------------------- | --- | --- | -------- | ------------ | --- |
usingthebuffer.
14 buf.wait();
WhenthisShareTableisenabled,itwillhavethehighestpriority 15 ctrl->asyncWrite(dev_idx, blk_idx, buf, chain);
| intheAGILEsoftwarecachehierarchy.Whennewrequestsarrive, |     |     |     | 16  |     |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
AGILEwillfirstconsulttheShareTabletodetermineifanyuser 17 // Method-3: AGILE array-like synchronous API
threadownsavalidbufferoftherequesteddata.Ifnorecordis 18 auto agileArr = ctrl->getArrayWrap<int>(chain);
found,AGILEwillfallbacktothesoftwarecacheorissueanew 19 int val = agileArr[dev_idx][idx];
20 }
requesttotheSSDandregisterthisbufferintheShareTable.Similar
21
totheflexiblecustomizationinsoftwarecache,AGILEallowsusers
|           |                   |            |                         | 22 int main(int | argc,          | char** argv){ |     |     |     |
| --------- | ----------------- | ---------- | ----------------------- | --------------- | -------------- | ------------- | --- | --- | --- |
| to design | their own sharing | policy and | integrate it into AGILE |                 |                |               |     |     |     |
|           |                   |            |                         | 23 // GPU       | Configurations |               |     |     |     |
seamlesslytomeetvariousapplicationneeds.
|     |     |     |     | 24 AGILE_HOST       | host(...);     |               |     |     |     |
| --- | --- | --- | --- | ------------------- | -------------- | ------------- | --- | --- | --- |
|     |     |     |     | 25 // Policy        | Configurations |               |     |     |     |
|     |     |     |     | 26 SHARE_TABLE_IMPL |                | s_table(...); |     |     |     |
3.5 AGILEAbstractionandSoftwareAPIs
|     |     |     |     | 27 GPU_CACHE_IMPL |     | g_cache(...); |     |     |     |
| --- | --- | --- | --- | ----------------- | --- | ------------- | --- | --- | --- |
Listing1showsanexampleGPUprogramthatusesAGILE.Users 28 host.setGPUCache(g_cache);
candefinetheirsoftwarecachepolicy(line1)ordirectlychoose 29 host.setShareTable(s_table);
thebuilt-insoftwarecachepoliciesandspecifythesoftwarecache 30 // Add and open target SSDs in the program
|     |     |     |     | 31 host.addNvmeDev("/dev/AGILE-xxx", |     |     |     | ...); |     |
| --- | --- | --- | --- | ------------------------------------ | --- | --- | --- | ----- | --- |
policyinline2.Toprovideflexibilityinsoftwarecacheandshare
|                 |               |               |                    | 32 host.addNvmeDev("/dev/AGILE-xxx", |     |     |     | ...); |     |
| --------------- | ------------- | ------------- | ------------------ | ------------------------------------ | --- | --- | --- | ----- | --- |
| table policies, | AGILE employs | the curiously | recurring template |                                      |     |     |     |       |     |
33 host.initNvme();
pattern(CRTP)toimplementthesoftwarecacheandsharetable
|     |     |     |     | 34 // Initialize |     | AGILE controller |     |     |     |
| --- | --- | --- | --- | ---------------- | --- | ---------------- | --- | --- | --- |
controllogic.CRTPenablescompile-timepolymorphismandavoids
35 host.initializeAgile(...);
usingvirtualfunctions.ThesoftwarecacheandtheShareTable
|     |     |     |     | 36 // CUDA | kernel | parallelism | configurations |     |     |
| --- | --- | --- | --- | ---------- | ------ | ----------- | -------------- | --- | --- |
policiesarespecifiedinline2.
37 host.configKernelParallelism(...);
Because AGILE allows users to provide customized policies, 38 host.queryOccupancy(kernel);
whereprocessingonlocksisnecessaryandmayintroducenew 39 // Start the lightweight AGILE service
deadlockrisks,AGILEprovidesadebugoptionatcompiletime 40 host.startAgile();
totrackacquiredlockswithineachthreadusingalockchainim- 41 // Execute the CUDA kernel
plementedasalinkedlist(line6).Ifthisdebugoptionisenabled, 42 host.runKernel(kernel, args...);
|     |     |     |     | 43 // Stop | AGILE | service |     |     |     |
| --- | --- | --- | --- | ---------- | ----- | ------- | --- | --- | --- |
whenathreadtriestoacquireatargetlockbutfails,itwillscan
44 host.stopAgile();
allpreviouslyacquiredlocksandmarktheseacquiredlocksare
|     |     |     |     | 45 // Close | the | opened SSDs |     |     |     |
| --- | --- | --- | --- | ----------- | --- | ----------- | --- | --- | --- |
dependentonthetargetlocktorelease.Then,itwillcheckifany
46 host.closeNvme();
acquiredlockexistsinthedependencychainofthetargetlock–ifa
47 }
circulardependenceresultsinadeadlock.Ifacirculardependency
Listing1:ExampleGPUprogramusingAGILE.
happens,AGILEwillreportittousers.
Lines8-19presentthethreemethodstoaccessSSDsinAGILE.
Lines22-47demonstratetheAGILEhost-sidecodeexecuted
Line9isanexampleoftheprefetch(),whichasynchronously
loadsthedatafromatargetSSDtothesoftwarecache.Line12 ontheCPU.AtLine24,usersspecifytheGPUconfigurations,e.g.,
showshowuserscanregisterauser-specifiedbuffertoAGILEand selectingwhichGPUtousefortheprogram.Lines26-29han-
useasync_issue(src,dst)toloadorstoredataasynchronously dletheinitializationofAGILE’sGPUsoftwarecacheandshare
tablepolicies.AGILEallowsmultipleNVMeSSDstobeconfigured
(lines13-15).ForasyncRead(),usersneedtoverifyifthetransfer
|     |     |     |     | and used simultaneously |     | in the program, | as  | shown in Lines | 31  |
| --- | --- | --- | --- | ----------------------- | --- | --------------- | --- | -------------- | --- |
iscompletedbeforeusing(line14),whiletheasyncWrite()will
ensure the data is updated to the software cache and the write -33.ToutilizeSDDswithAGILE,thedevicesmustbeboundto
commandisissued,andthebufferisavailablerightawayforother theAGILE-providedNVMeSSDdriver,whichcreatesadevicefile,
|     |     |     |     | /dev/AGILE-NVMe-${PCIe-BDF}, |     | for | each SSD. | AGILE supports |     |
| --- | --- | --- | --- | ---------------------------- | --- | --- | --------- | -------------- | --- |
purposes.AGILEalsoprovidesanarray-likesynchronousAPIthat
customizedNVMequeueconfigurationsforuserstoenablepriori-
viewstheSSDsasatwo-dimensionalarray,wherethefirstdimen-
tizationcontrolacrossSSDs.AtLine35,AGILEallocatesphysically
sionspecifiestheSSDindicesandtheseconddimensionisthedata
positiontoaccess(lines18-19). contiguousmemoryonHBMforNVMeI/Oqueuesandregisters

| SC’25,November16–21,2025,StLouis,MO,USA |     |     |     |     |     |     |     | ZhuopingYangetal. |     |
| --------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- |
thesequeuestotheSSDs.Lines37-38configuretheapplication asynchronouspipelinestages,suchasprefetchingandtheissuing
kernel’slaunchconfigurations(i.e,gridDim,blockDim),compile
logic,cannotbefullyhiddenbyeithercomputationorcommuni-
theapplicationkernel,andreportthemaximumnumberofactive cation,whichlimitstheidealoverlap.Theexperimentalresults
blocksperSM.TheAGILElightweightruntimeservice,described demonstratethatAGILE’sasynchronousI/Omodeliseffectivein
inSection3.2,mustbestarted(Line40)andproperlyterminated hidingcommunicationtime,especiallywhenthecomputationand
(Line44)beforeandafterkernelexecution(Line42).Finally,the communicationarebalanced.
| openedSSDsneedtobeclosedatLine46. |     |     |     |     |     | Ideal | Async | Sync |     |
| --------------------------------- | --- | --- | --- | --- | --- | ----- | ----- | ---- | --- |
2
cnyS otdezilamroN
| 4 Evaluation |     |     |     |     | 1.8         |     |     |     |     |
| ------------ | --- | --- | --- | --- | ----------- | --- | --- | --- | --- |
|              |     |     |     |     | pudeepS 1.6 |     |     |     |     |
Intheexperiments,wefirstuseamicro-benchmarktodemonstrate
| theadvantagesoftheasynchronousmodeloverasynchronous      |          |                  |          |       | 1.4 |     |     |     |     |
| -------------------------------------------------------- | -------- | ---------------- | -------- | ----- | --- | --- | --- | --- | --- |
| modelunderdifferentworkloadcharacteristics.Then,weevalu- |          |                  |          |       | 1.2 |     |     |     |     |
| ate the scalability                                      | of AGILE | using 4KB random | read and | write |     |     |     |     |     |
1
onvariousnumbersofSSDs.TodemonstratetheusabilityofAG-
0.8
|     |     |     |     |     | 0   | 0.5 | 1   | 1.5 | 2   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ILE,wecompareAGILEwiththestate-of-the-artworkBaMon
Computation-to-Communication Ratio
DeepLearningRecommendationModels(DLRMs)andusevarious
Figure4:SpeedupcomparisonofasynchronousI/Ooversyn-
configurations.WefurtherevaluatetheAPIoverheadofAGILE
chronousI/OonworkloadswithdifferentComputation-to-
againstBaMongraphapplicationstodemonstrateAGILE’seffi-
ciency.Lastly,wereportthepre-threadregisterusageofAGILE CommunicationRatio(CTC).
andBaM,whichshowsthatAGILEismorelightweightintermsof
|                         |     |     |     |     |                        | 1SSD | 2 SSDs 3 SSDs |     |     |
| ----------------------- | --- | --- | --- | --- | ---------------------- | ---- | ------------- | --- | --- |
| GPUresourceconsumption. |     |     |     |     | )s/BG( htdiwdnaB 12 12 |      |               |     |     |
|                         |     |     |     |     | 10 10                  |      |               |     |     |
4.1 ExperimentalSetup
8 8
| WeevaluateAGILEonaDellR750serverrunningUbuntu20.04, |               |                       |         |     | 6 6 |     |     |     |     |
| --------------------------------------------------- | ------------- | --------------------- | ------- | --- | --- | --- | --- | --- | --- |
| equippedwithanNvidiaRTX5000AdaGPU[43],aDellEntNVMe  |               |                       |         |     | 4 4 |     |     |     |     |
| AGN MU                                              | AIC 1.6TB SSD | [15], and two Samsung | 990 PRO | 1TB | 2 2 |     |     |     |     |
0
|     |     |     |     |     | 0 1 8 | 64  | 512 4096 | 32768 | 262144 |
| --- | --- | --- | --- | --- | ----- | --- | -------- | ----- | ------ |
SSDs[54].TheGPUandSSDsareattachedtotheserverviaPCIe 1 8 64 512 4096 32768 262144
#Request per SSD
Gen4x16andGen4x4,respectively.TheNvidiaDriver550.54and
theCUDA12.8areinstalledontheserverforexperiments.The Figure5:AGILE4KBrandomreadonmultipleSSDs
modifiedLinuxkerneldriversusedinAGILEaretestedonLinux
| 5.4.0-200-generic.                                      |     |     |     |     |                    | 1SSD | 2 SSDs 3 SSDs |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | ------------------ | ---- | ------------- | --- | --- |
|                                                         |     |     |     |     | )s/BG( htdiwdnaB 8 |      |               |     |     |
| 4.2 ComparisonbetweenasynchronousI/Oand                 |     |     |     |     | 6                  |      |               |     |     |
| synchronousI/O                                          |     |     |     |     | 4                  |      |               |     |     |
| WefirstdemonstratehowAGILE’sasynchronousI/Omodelenables |     |     |     |     | 2                  |      |               |     |     |
overlappingbetweencomputationandcommunicationtoreduce
0
end-to-endexecutiontime.Inthisexperiment,1024threadswithin 1 8 64 512 4096 32768 262144
#Request per SSD
ablockarelaunchedtoissue64NVMecommandsandperform
Figure6:AGILE4KBrandomwriteonmultipleSSDs
computationonthereturneddata.Inthesynchronousmode,com-
putationbeginsonlyafteralldatahasbeenfetched.Incontrast,the
AGILEasynchronousmodeenablescomputationandcommunica- 4.3 AGILE4KBrandomreadandwriteon
tionoverlappingatthethreadlevel.Ideally,whencomputationand
multipleSSDs
communicationperfectlyoverlapwitheachother,thespeedupcan
WeevaluatethescalabilityofAGILEusing4KBrandomreadand
bedefinedbyEquation1:
writeusing1,2,and3SSDs,asshowninFigure5andFigure6,
 1+CTC, 0≤CTC≤1
respectively.ForexperimentswithmorethanoneSSD,different
|     | IdealSpeedup= | 1   |     | (1) |     |     |     |     |     |
| --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
1+ , CTC>1 SSDsareaccessedinaninterleavedmanner.Forexample,requests0,

CTC 2,4,etc.areissuedtoSSD1,whilerequests1,3,5,etc.aredirectedto

AsshowninFigure4,weillustratetheeffectivenessofAGILE’s SSD2.Inboth4KBrandomreadandwrite,AGILEexhibitsscalable
thread-levelasynchronousmodelbyvaryingthecomputation-to- performanceasthenumberofrequestsincreasesandcanleverage
communication(CTC)ratiofrom0to2byincreasingthenumberof multipleSSDseffectively.For4KBrandomreadsinFigure5,the
computationiterations.AGILEasynchronousversioncanachieve aggregatebandwidthsaturatesat3.7GB/s,7.4GB/s,and11.1GB/s
upto1.88ximprovementoverthesynchronousbaseline.Theob- with1SSD,2SSDs,and3SSDs,respectively,afterapproximately
servedspeedupincreaseswithCTCuntilitreachesapeakwhere 32Kconcurrentrequestsperdevice.Figure6depictstheaggregate
CTCiscloseto0.9andthengraduallydecreaseswhenCTCfur- write bandwidth achieved by AGILE in the 4 KB random write
therincreases,whichalignswiththetheoreticaltrend.Thepeak workload,andAGILEsaturatesat2.2GB/s,4.4GB/s,and6.7GB/s
speedupoccursbelowCTCequals1becausecertainportionsofthe with1SSD,2SSDs,and3SSDs,respectively.

AGILE:LightweightandEfficientAsynchronousGPU-SSDIntegration SC’25,November16–21,2025,StLouis,MO,USA
4.4 EvaluationonDLRMinference overBaMwithspeedupfrom1.18×to1.30×.AGILEasyncalso
WefurtherevaluateAGILEagainstBaM[48]onDeepLearning consistentlyoutperformsAGILEsyncacrossallbatchsizesand
RecommendationModel(DLRM)inference.WeusetheCriteo1TB reaches the peak speedup to 1.75× at a batch size of 16. These
ClickLogsdataset[12]andconstructthecategoricalfeaturevocab- resultsdemonstrateAGILE’sabilitytooverlapcomputationand
computationatscale.TheresultsalsoindicatethattheAGILEasync
ularyusingthefirstthreedaysofdata.Toensureconsistentand
benefitsmorewhenthebatchsizeissmallerandnear16inthis
efficientcomputationacrossallexperiments,weusecuBLAS[37]
formatrixmultiplications.BaMandAGILEareusedtofetchem- DLRMinference,wheretheopportunitytohidecommunicationis
| beddingvectorstoHBM,andtheirkernelsareintegratedintothe |     |     |     | moresignificant. |     |     |              |     |               |     |
| ------------------------------------------------------- | --- | --- | --- | ---------------- | --- | --- | ------------ | --- | ------------- | --- |
|                                                         |     |     |     |                  |     | BaM | AGILE (sync) |     | AGILE (async) |     |
CUDAstreampipelinewithcuBLASkernels.Wekeepthesame
dezilamroN pudeepS
clockreplacementcachepolicy[10]andsetthesoftwarecachesize 1.75
enilesaBMaB ot 1.8
to2GBforallexperimentsunlessotherwisespecified.ForNVMe 1.68 1.68
I/Oqueueconfigurations,weuse128queuepairs,andthequeue 1.6 1.56 1.57
|     |     |     |     |     | 1.46 | 1.46 |     |     |     | 1.48 |
| --- | --- | --- | --- | --- | ---- | ---- | --- | --- | --- | ---- |
depthofeachqueueissetto256bydefaultacrossallexperiments 1.39 1.43
|     |     |     |     |     | 1.4 |     |     |     |     | 1.36 1.40 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- |
unlessotherwisespecified.WeuseAGILEinboththesynchronous 1.26 1.25 1.30 1.30 1.28 1.30
|     |     |     |     |     |     | 1.27 |     | 1.26 1.23 | 1.26 | 1.23 |
| --- | --- | --- | --- | --- | --- | ---- | --- | --------- | ---- | ---- |
|     |     |     |     |     | 1.2 |      |     |           | 1.18 |      |
mode(AGILEsync)andtheasynchronousmode(AGILEasync).
ForAGILEsyncandBaMimplementation,werequestdataand
1
performcomputationontherequesteddatawithinthesameepoch.
ForAGILEasync,weprefetchdataforthenextepochtoenable
|     |     |     |     |     | 1   | 2 4 | 8 16 | 32 64 | 128 256 | 512 10242048 |
| --- | --- | --- | --- | --- | --- | --- | ---- | ----- | ------- | ------------ |
overlappingofcommunicationandcomputation.
Batch Size
WeadoptDLRMarchitecturefrom[34]andevaluateseveralvari- Figure 8: Speedup comparison of AGILE (async and sync
ants.Inadditiontoprojectionlayers(fordimensionalalignment modes)andBaMacrossvaryingbatchsizesinDLRMinfer-
inmatrixmultiplication)andactivationlayers,thebottomMLPin
ence.
Config-1hasthreematrixmultiplicationkernelswithdimensions BaM AGILE (sync) AGILE (async)
dezilamroN pudeepS
| 512-512-512,andthetopMLPconsistsofthreelayerswithsizesof   |     |     |     | 1.6            |      |           |      |      |      |           |
| ---------------------------------------------------------- | --- | --- | --- | -------------- | ---- | --------- | ---- | ---- | ---- | --------- |
|                                                            |     |     |     | enilesaBMaB ot |      |           |      |      |      | 1.46 1.46 |
|                                                            |     |     |     |                |      |           | 1.41 | 1.44 |      |           |
| 1024-1024-1024.Config-2reducesthenumberofmatrixmultiplica- |     |     |     | 1.4            |      |           |      |      |      |           |
|                                                            |     |     |     |                | 1.33 | 1.32 1.31 |      | 1.31 |      | 1.34      |
| tionstooneinboththebottomMLPandthetopMLPtorepresent        |     |     |     |                |      |           |      |      | 1.30 |           |
| alesscomputationallyintensivemodel.InConfig-3,werepeatthe  |     |     |     | 1.2            |      |           |      |      |      |           |
matrixmultiplicationssixtimestoemulateamorecomputationally
intensiveworkload.Inallconfigurations,wemeasuretheend-to-
1
endexecutiontimeusingabatchsizeof2,048andanepochsizeof
| 10,000. |     |     |     | 0.8 |     |     |     |     |     |     |
| ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|         |     |     |     |     |     | 1   | 2   | 4   | 8   | 16  |
Figure7illustratesthespeedupcomparisonofAGILEinboth
#IO Queue Pairs
synchronousandasynchronousmodesrelativetoBaMacrossthree
|     |     |     |     | Figure | 9: Speedup | comparison |     | of AGILE | (async | and sync |
| --- | --- | --- | --- | ------ | ---------- | ---------- | --- | -------- | ------ | -------- |
DLRMconfigurations.AGILEsyncshowsconsistentimprovement
overBaM,achievingspeedupsof1.3×,1.39×,and1.27×inConfig- modes)andBaMundervaryingnumbersofI/Oqueuepairs
inDLRMinference.
1,Config-2,andConfig-3,respectively.TheAGILEasyncfurther
WefurtherstudythesensitivityofNVMequeuesettingsforboth
improvestheperformancebyoverlappingdatamovementwith
AGILEandBaMusingDLRMConfig-1andabatchsizeof2048.
computationandreaches1.48×,1.63×,and1.32×speedupsinthe
sameconfigurations. Specifically,wereducethequeuedepthto64andsweepthenumber
ofqueuepairsfrom1to16,whichintroducesgreatercontention
|     | BaM AGILE (sync) |     | AGILE (async) |                                                      |     |     |     |     |     |     |
| --- | ---------------- | --- | ------------- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| 22  |                  |     |               | intheNVMequeues.Figure9demonstratesthatbothAGILEsync |     |     |     |     |     |     |
MaB ot dezilamroN
andasyncmodesconsistentlyoutperformtheBaMbaselineacross
1.63
|                | 1.48 |      |           | allconfigurations.Whenonlyonequeuepairisused,theAGILE |     |     |     |     |     |     |
| -------------- | ---- | ---- | --------- | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| pudeepS 1.15.5 | 1.3  | 1.39 | 1.27 1.32 |                                                       |     |     |     |     |     |     |
asyncmodeprovidesonlymarginalspeedupovertheAGILEsync
| 11  |     |     |     | mode.Thisphenomenonarisesbecausethenumberofavailable |     |     |     |     |     |     |
| --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- |
SQEsistoosmalltosupportalltherequestsissuedinanepoch.
0.05.5 Asaresult,intheprefetchstage,thethreadsmustwaituntilthe
|     | Config-1 | Config-2 | Config-3 |       |         |                      |     |      |         |              |
| --- | -------- | -------- | -------- | ----- | ------- | -------------------- | --- | ---- | ------- | ------------ |
|     |          |          |          | AGILE | service | receives completions |     | from | the SSD | and recycles |
SQEs.Consequently,thiswaitingdegradestheasynchronousmode,
| Figure 7: | Speedup comparison | of AGILE | (async and sync |     |     |     |     |     |     |     |
| --------- | ------------------ | -------- | --------------- | --- | --- | --- | --- | --- | --- | --- |
causingittoexhibitasimilarbehaviortothesynchronousmode
modes)overBaMondifferentrecommendationmodels.
|     |     |     |     | in AGILE. | As  | the number | of queue | pairs | increases, | more SQEs |
| --- | --- | --- | --- | --------- | --- | ---------- | -------- | ----- | ---------- | --------- |
TounderstandhowAGILEperformsunderdifferentworkload areavailableforeachepoch.Thisreducescontentionduringthe
granularities,weevaluateAGILE’sspeedupacrossawiderangeof prefetchstageandallowstheprefetchstagetoproceedwithout
batchsizesusingDLRMConfig-1,whichassessesthescalability stalls.Therefore,thespeedupofAGILEasyncoverthesynchronous
ofAGILEandBaM.Figure8depictsthespeedupofAGILEinsync modebecomesmoresignificant.
and async modes normalized to the BaM baseline across batch Lastly, we evaluate the impact of software cache size on the
sizesrangingfrom1to2048.AGILEsyncmodeshowsstablegains DLRMinferenceusingDLRMConfig-1andabatchsizeof2048.

SC’25,November16–21,2025,StLouis,MO,USA ZhuopingYangetal.
Wesweepthesoftwarecachesizefrom1MBto2GBandcom-
parethespeedupofAGILEagainsttheBaMbaseline.Figure10
illustrates the changes in the speedup under different software
cachesizes.TheAGILEsyncmodeconsistentlyoutperformsBaM
acrossallcachesizes,achievingapeakspeedupof1.48×at256
MBsoftwarecachesize.Incontrast,AGILEasyncmodeinitially
lagsbehindboththeBaMbaselineandtheAGILEsyncmodewhen
thesoftwarecachesizeissmall.However,theAGILEasyncmode
surpassesthesynchronousmodeafterthesoftwarecachereaches
acertainthreshold,around64MB.Thisbehaviorstemsfromthe
softwarecachecontention.Whenthesoftwarecacheistoosmall,
eachepochmayaccessmoredatathatcannotfitinthesoftware
cachesize.Inthiscase,theprefetchstageinAGILEasyncwillnot
onlywaitforavailablecachelinestomakenewrequestsbutalso
evictthepreviouslyrequesteddataintendedforthenextepoch.
Therefore,whenthatdataisneededinthenextepoch,ithasalready
beenevicted,andadditionalrequestsbecomenecessaryduringthe
computationphase.Thedelaysintheprefetchstagedegradethe
asynchronousmodetobehavemorelikethesynchronousversion,
andtheextrarequestsduringthecomputationphasemaketheper-
formanceworse.Asthesoftwarecachesizekeepsincreasing,more
cachelinesareavailabletosupportconcurrentprefetchingwithout
evictions.Thisallowstheprefetchstagetocompletesoonafterthe
commandsareissued.Therefore,thedatamovementtimecanbe
hiddenbythecomputationagain,exhibitingconsistentspeedup
overthesynchronousmodeagain.Theseresultsindicatethatthe
asynchronousmodedoesnotalwaysoutperformthesynchronous
onebecauseanimpropersoftwarecachesizewillcausestallsand
introduceextraNVMecommands.Therefore,whenapplyingasyn-
chronousmodeinreal-worldapplications,itisessentialtoestimate
boththecapacityofthesoftwarecachesizeandthedataaccess
demandsperepochtofullyleveragethebenefitsofasynchronous
mode.
1.8
1.6
1.4
1.2
1
0.8
1 2 4 8 16 32 64 128 256 512 10242048
Software Cache Size (MB)
dezilamroN
pudeepS
enilesaBMaB
ot
bydatamovementduetotheirirregularaccesspatternsandlow
arithmeticintensity[6,13],makingthemappropriatebenchmarks
forassessingAPI-leveloverhead.Inourexperiments,weimple-
mentthebaselineversionsofBFSandSpMVusingBaMandAGILE
withoutanyapplication-leveloptimization,whichensuresthatthe
observedperformancedifferencesareattributedsolelytotheun-
derlyingsoftwareinfrastructure,includingtheAPIoverhead,cache
accessbehavior,andrequestissuing&completionpollingmecha-
nism.WeuseGAPBenchmarkSuite[55]togeneratetheuniform
randomgraphsandKroneckergraphstoemulaterealisticgraphs.
Allgraphstructuresandweights(ifapplicable)arestoredinthe
compressedsparserow(CSR)format.
TomeasuretheAPIoverhead,weconductthefollowingthree-
stepexperiment:
(1) Wefirstmeasuretheexecutiontimesoftheapplicationker-
nelswithoutusingBaMorAGILE,andthegraphdatais
directlystoredinsideHBMandaccessedusingthenative
CUDAAPI.(Kerneltime)
(2) Then, we integrate BaM and AGILE into the application
kernelsandmeasurethetotalruntime,whichincludesthe
datatransfertimeandtheoverheadfrombothsoftwarecache
accessandNVMecommandissuing.(I/OAPItime)
(3) Finally,toobtaintheoverheadinsoftwarecacheaccess,we
preloadallgraphdataintothesoftwarecachebeforekernel
execution,eliminatingtheNVMerequestsduringruntime.
(CacheAPItime)
Kernel Cache API I/O API
128
32
8
2
BaM AGILE (sync) AGILE (async)
0.5
1.73 BaM AGILE BaM AGILE BaM AGILE BaM AGILE
1.63 BFS-K BFS-U SpMV-K SpMV-U
1.55
1.27 1.32 1.40 1.45 1.43 1.36 1.31 1.32 1.48 1.40 1.3 1 5 .50 Graph Applications
1.20 1.21
1.16
1.09 1.09
1.04 1.05 0.95 1.00
Figure10:SpeedupcomparisonofAGILE(asyncandsync
modes)andBaMundervaryingsoftwarecachesizesinDLRM
inference.
4.5 EvaluateAGILEAPIoverheadongraph
applications
The overhead resulting from the implementation is also an im-
portantfactorthatinfluencesoverallperformance.Weevaluate
theAGILE’sAPIoverheadcoveringboththesoftwarecacheac-
cessandrequestissuingagainstBaMontwographapplications:
Breadth-FirstSearch(BFS)andsparsematrixvectormultiplication
(SpMV).TheexecutiontimeforbothBFSandSpMVisdominated
nwodkaerB
emiT
lenreK
ot
dezilamroN
Figure 11: Execution time breakdown of BaM and AGILE
acrossvariousgraphapplications.
Figure11illustratestheexecutiontimebreakdownofBFSand
SpMVusingdifferentgraphtypes,where‘-K’denotestheKronecker
graphs(K-graph)withskeweddegreedistribution,and‘-U’denotes
uniform random graphs (U-graph) with regular structures. The
barsaresegmentedintokernelexecution,cacheAPI,andI/OAPI
time.Allmeasuredexecutiontimesarenormalizedtothekernel
runtime.Acrossallgraphtypes,AGILEconsistentlyachieveslower
executiontimecomparedwithBaMbyeffectivelyreducingboth
thecacheAPIandI/OAPIoverheads.ForBFS,AGILEreducesthe
softwarecacheoverheadby2.27×onU-graphand1.93×onK-graph.
andcutstheI/OAPIoverheadby1.16×and1.86×,respectively.For
SpMV,AGILEachievesevengreaterreductions–2.11×and3.17×
insoftwarecacheoverhead,and1.06×and2.85×inI/Ooverhead
onU-graphandK-graph,respectively.Theseresultsunderscore
AGILE’sefficiencyinhandlingmemory-intensiveworkloadsby
minimizingtheoverheadfromtheAPIimplementationregardless
ofgraphstructure.

AGILE:LightweightandEfficientAsynchronousGPU-SSDIntegration SC’25,November16–21,2025,StLouis,MO,USA
4.6 EvaluateAGILEperthreadregisterusage
acrossCUDAkernels
TofurtherevaluateAGILE’sefficiencyonGPUresources,weex-
amineitsper-threadregisterusageacrossdifferentCUDAkernels.
Sinceregisterusagedirectlyaffectswarpoccupancyandscheduling
flexibility,optimizingitiscrucialonGPUs.Figure12depictsthe
numberofregistersusedperthreadindifferentCUDAkernelsim-
plementedusingBaMorAGILE.Wedonotimposeanyconstraints
tolimittheregisterusage,andbothBaMandAGILEuseidentical
kernelimplementationsforfaircomparison.
ComparedtoBaM,AGILEachievesareductioninper-thread
registerby1.04×,1.22×,and1.32×inVectorMean,BFS,andSpMV
kernels,respectively.Thisimprovementstemsfromtheefficient
implementationofAGILEandtheoffloadingoftheCQpollinglogic
tothededicatedAGILEservicekernel,whichalleviatespressure
onapplicationkernelsandenablesmoreefficientregisterutiliza-
tion. Moreover, the AGILE service kernel is lightweight, which
consumes37registersperthreadandcanassistmultipleCUDA
kernelssimultaneously.
BaM AGILE
80 74
60 56 54 56 56
46
40
20
0
VectorMean BFS SpMV
CUDA Kernels
retsigeR#
oneGPUtoviewotherGPUs’HBMasaremotecacheandleverage
NVLinktotransfercacheddatamayalsobeworthinvestigating.
ThisadditionalcachelevelinHBMs(sharedamongGPUs)needs
furtherstudyonthecachecoherencyamongGPUs,whichinvolves
dealingwiththecachelinemetadataandanalyzingitsperformance
benefits.
Third,extendingAGILEtosupportmoreheterogeneoussystems
withacceleratorssuchasFPGAscouldprovidemoreperformance
gainsondiverseworkloadswithvariouscomputationandIOchar-
acteristics.Forexample,byleveragingtheFPGA’sflexibilityand
advantagesinnetworkprocessing,FpgaNIC[61]developsaGPU-
orientedSmartNIConFPGAtoaccelerateabroadrangeofdis-
tributedapplicationsondistributedGPUs.Besides,FPGAexhibits
goodenergyefficiencyashardwareaccelerators[64,67,69,70],
andisagoodfitforreal-timesystems,wheredeterminismiscriti-
cal[16,23,24].CollaborationbetweenFPGAsandGPUsmayoffer
bothhighthroughputandlowerenergyconsumptionwhilemeet-
ingstringentdeadlinerequirements.Suchanextension,however,
introducesnewchallengesincoordinatingmultipledevicesand
requiresmoresophisticatedsystemdesigns.Weleavethisextension
tofutureversionsofAGILE.
Fourth,AGILEmayalsoenablenewresearchincompiler-level
optimizations.Forapplicationsinvolvingmultipledatacommuni-
cationsandcomputationswithinasinglekernel,theprogrammers
needtoexploretheoverlapopportunitymanually.Whilecurrently
AGILEfunctionsasanasynchronousI/Olibrary,itcanbeextended
withcompilersupporttoautomaticallyanalyzedependenciesand
Figure 12: Per-thread register usage comparison between performcodetransformations.Existingresearchworkshaveex-
BaMandAGILEacrossvariousCUDAkernels. ploredsimilaroptimizations.Forexample,thecompileridentifies
thedatadependencyandreordersinstructionsforbetteroverlap-
5 Discussion
ping [11, 68]. AGILE serves as a foundational first step toward
WhileAGILEdemonstratessignificantperformanceimprovement thatgoalofdevelopingacompilerthatenablesstaticdependency
overexistingworkandexhibitsstrongscalabilitywithmultiple analysistoautomaticallyexploreoverlappingopportunities.
SSDs,severalopportunitiesremainforextendingAGILEtobroader Fifth,supportingAGILEinvirtualizedenvironments,suchas
andmorecomplexsystemarchitectures. virtualmachinesorDockercontainers,isimportantforimproving
First, extending the software cache hierarchy to incorporate portability,scalability,andeaseofdeploymentinsharedcomputing
CPUDRAMasanadditionaltierisanaturalandwell-motivated infrastructures.However,thisrequiresfurtherdevelopmentand
enhancement,asdemonstratedinpriorwork[7,21,29].AGILEis investigationintotheassociatedperformanceimplications,partic-
designedwiththeflexibilitytosupportsuchanextension.Inits ularlywithrespecttoI/Ovirtualization,devicepassthrough,and
currentimplementation,AGILEincludesreservedAPIsthatenable potentialoverheadintroducedbythevirtualizationlayer.
integrationofCPUDRAMasanadditionallevelofthesoftware-
managedcache,complementingtheexistingGPUHBMcache.We 6 Conclusion
willoptimizeandincorporatethisfunctionalityinouropen-sourced
Inthispaper,weproposeAGILE,alightweightandefficientasyn-
GitHubrepositorysoon.
chronouslibraryforGPU-SSDintegration.AGILEisthefirstwork
Second, AGILE currently targets a single-GPU with multiple
thatenablesGPUthreadstoissueNVMecommandsasynchronously
SSDsscenario,butAGILEhasallthecapabilitiestobeextended
andallowsuserstocustomizesoftwarecachepolicy.AGILEenables
to support multiple GPUs with multiple SSDs. To simply share overlappingatthethreadlevelandachievesupto1.88×reduction
oneSSDamongGPUs,differentI/OqueuepairsofthetargetSSD
inexecutiontimebyhidingdatatransferwithcomputation.AG-
canworkindependentlyandbeassignedtodifferentGPUs.Itonly ILEexhibitsupto1.75×improvementonDLRMsandshows3.12×
requiressomemodificationstotheHostAPIs,whiletheAGILE and2.85×APIoverheadreductioninsoftwarecacheandNVMe
serviceandinterfacesontheCUDAkerneldonotneedanychange.
IOrequestscomparedwiththestate-of-the-artGPU-centricwork,
AllowingoneGPUtoissuepeer-to-peerdatatransfersbetween BaM[48].AGILEisalsolightweightandconsumesupto1.32×
anotherGPUandSSDsorpopulatingdatafromoneGPUdirectly
fewerregistersinvariousCUDAkernels.
toanotherGPUisalsodoableiftheGPUknowsthePCIeBARsof
theotherGPUs.However,itmayrequirefurtherinvestigationand ACKNOWLEDGEMENTS–Thisworkissupportedinpartby
optimizationtohandledatatransferandsynchronizationefficiently BrownUniversityNewFacultyStart-upGrant,andNSFawards
withoutperformancedegradation.Inamulti-GPUsystem,enabling #2213701,#2217003,#2328972,#2511445,#2536952.

SC’25,November16–21,2025,StLouis,MO,USA ZhuopingYangetal.
References
2025.ART:CustomizingAcceleratorsforDNN-EnabledReal-TimeSafety-Critical
[1] JoshAchiam,StevenAdler,SandhiniAgarwal,LamaAhmad,IlgeAkkaya,Floren- Systems.InProceedingsofthe2025ACMGreatLakesSymposiumonVLSI(GLSVLSI
ciaLeoniAleman,DiogoAlmeida,JankoAltenschmidt,SamAltman,Shyamal ’25).
Anadkat,etal.2023. Gpt-4technicalreport. arXivpreprintarXiv:2303.08774 [24] ShixinJi,ZhuopingYang,XingzhenChen,WeiZhang,JinmingZhuang,AlexK
(2023). Jones,ZhengDong,andPeipeiZhou.2025.CLARE:DeterministicCycle-Level
[2] TylerAllenandRongGe.2021.In-depthanalysesofunifiedvirtualmemorysys- AcceleratoronREconfigurableplatformsinDNN-EnabledReal-TimeSafety-
temforGPUacceleratedcomputing.InProceedingsoftheInternationalConference CriticalSystems.InThe46thIEEEReal-TimeSystemsSymposium,2025(RTSS2025)
forHighPerformanceComputing,Networking,StorageandAnalysis.1–15. (RTSS’25).
[3] JonghyunBae,JongsungLee,YunhoJin,SamSon,ShineKim,HakbeomJang, [25] DiyaJoseph,JuanLuisAragón,Joan-ManuelParcerisa,andAntonioGonzalez.
TaeJunHam,andJaeWLee.2021. {FlashNeuron}:{SSD-Enabled}{Large- 2024.Wasp:Warpschedulingtomimicprefetchingingraphicsworkloads.arXiv
Batch}trainingofverydeepneuralnetworks.In19thUSENIXConferenceonFile preprintarXiv:2404.06156(2024).
andStorageTechnologies(FAST21).387–401. [26] MarkJKilgardandJeffBolz.2012. GPU-acceleratedpathrendering. ACM
[4] ShaiBergman,TanyaBrokhman,TzachiCohen,andMarkSilberstein.2019.SPIN: TransactionsonGraphics(TOG)31,6(2012),1–10.
Seamlessoperatingsystemintegrationofpeer-to-peerDMAbetweenSSDsand [27] GyusunLee,SeokhaShin,WonsukSong,TaeJunHam,JaeWLee,andJinkyu
GPUs.ACMTransactionsonComputerSystems(TOCS)36,2(2019),1–26. Jeong.2019. Asynchronous {I/O} stack:Alow-latencykernel {I/O} stack
[5] XiaoBi,DeliChen,GuantingChen,ShanhuangChen,DamaiDai,ChengqiDeng,
for{Ultra-Low}latency{SSDs}.In2019USENIXAnnualTechnicalConference
HonghuiDing,KaiDong,QiushiDu,ZheFu,etal.2024.Deepseekllm:Scaling (USENIXATC19).603–616.
open-sourcelanguagemodelswithlongtermism.arXivpreprintarXiv:2401.02954 [28] RuihaoLi,SanjanaYadav,QinzheWu,KrishnaKavi,GayatriMehta,NeerajaJ
(2024). Yadwadkar,andLizyKJohn.2023. PerformanceImplicationsofAsyncMem-
[6] AydinBuluçandKameshMadduri.2011. Parallelbreadth-firstsearchondis- cpyandUVM:ATaleofTwoDataTransferModes.In2023IEEEInternational
tributedmemorysystems.InProceedingsof2011InternationalConferenceforHigh SymposiumonWorkloadCharacterization(IISWC).IEEE,115–127.
PerformanceComputing,Networking,StorageandAnalysis.1–12. [29] HaikunLiu,YujieChen,XiaofeiLiao,HaiJin,BingshengHe,LongZheng,andRen-
[7] Chia-Hao Chang, Jihoon Han, Anand Sivasubramaniam, Vikram tongGuo.2017.Hardware/softwarecooperativecachingforhybridDRAM/NVM
Sharma Mailthody, Zaid Qureshi, and Wen-Mei Hwu. 2024. Gmt: Gpu memoryarchitectures.InProceedingsoftheInternationalConferenceonSuper-
orchestratedmemorytieringforthebigdataera.InProceedingsofthe29thACM computing.1–10.
InternationalConferenceonArchitecturalSupportforProgrammingLanguages [30] Matthieu Tardy and Carter Edwards. 2020. Controlling Data Move-
andOperatingSystems,Volume3.464–478. ment to Boost Performance on the NVIDIA Ampere Architecture.
[8] ChangChen,XiuhongLi,QianchaoZhu,JiangfeiDuan,PengSun,Xingcheng https://developer.nvidia.com/blog/controlling-data-movement-to-boost-
Zhang, and Chao Yang. 2024. Centauri: Enabling efficient scheduling for performance-on-ampere-architecture/
communication-computationoverlapinlargemodeltrainingviacommunication [31] AvinashMaurya,JieYe,MMustafaRafique,FranckCappello,andBogdanNicolae.
partitioning.InProceedingsofthe29thACMInternationalConferenceonArchi- 2024.Breakingthememorywall:Astudyofi/opatternsandgpumemoryutiliza-
tecturalSupportforProgrammingLanguagesandOperatingSystems,Volume3. tionforhybridcpu-gpuoffloadedoptimizers.InProceedingsofthe14thWorkshop
178–191. onAIandScientificComputingatScaleusingFlexibleComputingInfrastructures.
[9] AveryChing,SergeyEdunov,MajaKabiljo,DionysiosLogothetis,andSambavi 9–16.
Muthukrishnan.2015.Onetrillionedges:Graphprocessingatfacebook-scale. [32] Microsoft.2025.DeepNVMe. https://www.deepspeed.ai/tutorials/deepnvme/
ProceedingsoftheVLDBEndowment8,12(2015),1804–1815. [33] SparshMittalandShraiyshVaishay.2019.Asurveyoftechniquesforoptimizing
[10] FernandoJCorbato.1968. Apagingexperimentwiththemulticssystem. Mas- deeplearningonGPUs.JournalofSystemsArchitecture99(2019),101635.
sachusettsInstituteofTechnology. [34] MaximNaumov,DheevatsaMudigere,Hao-JunMichaelShi,JianyuHuang,
[11] NealCCrago,SanaDamani,KarthikeyanSankaralingam,andStephenWKeckler. NarayananSundaraman,JongsooPark,XiaodongWang,UditGupta,Carole-
2024. Wasp:Exploitinggpupipelineparallelismwithhardware-accelerated JeanWu,AlissonGAzzolini,etal.2019.Deeplearningrecommendationmodel
automaticwarpspecialization.In2024IEEEInternationalSymposiumonHigh- forpersonalizationandrecommendationsystems.arXivpreprintarXiv:1906.00091
PerformanceComputerArchitecture(HPCA).IEEE,1–16. (2019).
[12] CriteoAILab.2025.DownloadCriteo1TBClickLogsdataset-CriteoAILab. [35] GiovanniNeglia,DamianoCarra,andPietroMichiardi.2018.Cachepoliciesfor
https://ailab.criteo.com/download-criteo-1tb-click-logs-dataset/ linearutilitymaximization.IEEE/ACMTransactionsonNetworking26,1(2018),
[13] JohnDDavisandEricSChung.2012.SpMV:Amemory-boundapplicationon 302–313.
theGPUstuckbetweenarockandahardplace.MicrosoftResearchSiliconValley, [36] Nvidia.2025.1.Introduction—PTXISA8.8documentation. https://docs.nvidia.
TechnicalReport14September2012(2012). com/cuda/parallel-thread-execution/
[14] Debendra Das Sharma and Ishwar Agarwal. 2023. CXL_3.0_white- [37] Nvidia.2025.cuBLAS|NVIDIADeveloper. https://developer.nvidia.com/cublas
paper_FINAL. https://computeexpresslink.org/wp-content/uploads/2023/12/ [38] Nvidia.2025.CUDAC++ProgrammingGuide. https://docs.nvidia.com/cuda/
CXL_3.0_white-paper_FINAL.pdf pdf/CUDA_C_Programming_Guide.pdf
[15] Dell.2021. DellEnterpriseAgnosticNVMeDriveTechnicalSpecifications. [39] Nvidia. 2025. cuda::memcpy_async — libcudacxx 3.1 documentation.
https://dl.dell.com/manuals/all-products/esuprt_data_center_infra_int/esuprt_ https://nvidia.github.io/cccl/libcudacxx/extended_api/asynchronous_
data_center_infra_storage_adapters/dell-poweredge-exp-fsh-nvme-pcie- operations/memcpy_async.html?utm_source=ainews&utm_medium=email&
ssd_Users-Guide7_en-us.pdf utm_campaign=ainews-a-quiet-weekend
[16] PeiyanDong,JinmingZhuang,ZhuopingYang,ShixinJi,YanyuLi,DongkuanXu, [40] Nvidia.2019. GPUDirectStorage:ADirectPathBetweenStorageandGPU
HengHuang,JingtongHu,AlexKJones,YiyuShi,etal.2024.EQ-ViT:Algorithm- Memory|NVIDIATechnicalBlog. https://developer.nvidia.com/blog/gpudirect-
hardwareco-designforend-to-endaccelerationofreal-timevisiontransformer storage/
inferenceonVersalACAParchitecture.IEEETransactionsonComputer-Aided [41] Nvidia.2025.NVIDIAAmpereGPUArchitectureTuningGuide. https://docs.
DesignofIntegratedCircuitsandSystems43,11(2024),3949–3960. nvidia.com/cuda/ampere-tuning-guide/index.html
[17] GilEinziger,RoyFriedman,andBenManes.2017. Tinylfu:Ahighlyefficient [42] Nvidia.2025. NVIDIA/gdrcopy:AfastGPUmemorycopylibrarybasedon
cacheadmissionpolicy.ACMTransactionsonStorage(ToS)13,4(2017),1–31. NVIDIAGPUDirectRDMAtechnology. https://github.com/NVIDIA/gdrcopy
[18] EranGalandSivanToledo.2005. Algorithmsanddatastructuresforflash [43] Nvidia.2025.RTX5000AdaGenerationGraphicsCard|NVIDIA. https://www.
memories.ACMComputingSurveys(CSUR)37,2(2005),138–163. nvidia.com/en-us/design-visualization/rtx-5000/
[19] AmirGholami,ZheweiYao,SehoonKim,ColemanHooper,MichaelWMahoney, [44] Nvidia.2013. UnifiedMemoryinCUDA6|NVIDIATechnicalBlog. https:
andKurtKeutzer.2024.AIandmemorywall.IEEEMicro(2024). //developer.nvidia.com/blog/unified-memory-in-cuda-6/
[20] PieterHijma,StijnHeldens,AlessioSclocco,BenVanWerkhoven,andHenriE [45] Nvidia.2018. UsingCUDAWarp-LevelPrimitives|NVIDIATechnicalBlog.
Bal.2023.OptimizationtechniquesforGPUprogramming.Comput.Surveys55, https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/
11(2023),1–81. [46] NVMExpress.2025.NVMExpress. https://nvmexpress.org/
[21] JeongminHong,SungjunCho,GeonwooPark,WonhyukYang,Young-HoGong, [47] StéfaniPires,AdrianaRibeiro,andLeobinoNSampaio.2024.Onlearningsuitable
andGwangsunKim.2024. Bandwidth-effectivedramcacheforgpuswith cachingpoliciesforin-networkcaching.IEEETransactionsonMachineLearning
storage-classmemory.In2024IEEEInternationalSymposiumonHigh-Performance inCommunicationsandNetworking(2024).
ComputerArchitecture(HPCA).IEEE,139–155. [48] ZaidQureshi,VikramSharmaMailthody,IsaacGelado,SeungwonMin,Amna
[22] GuyueHuang,YangBai,LiuLiu,YukeWang,BeiYu,YufeiDing,andYuanXie. Masood,JeongminPark,JinjunXiong,ChrisJNewburn,DmitriVainbrand,I-Hsin
2023.Alcop:Automaticload-computepipeliningindeeplearningcompilerfor Chung,etal.2023.GPU-initiatedon-demandhigh-throughputstorageaccess
ai-gpus.ProceedingsofMachineLearningandSystems5(2023),680–694. intheBaMsystemarchitecture.InProceedingsofthe28thACMInternational
[23] ShixinJi,XingzhenChen,JinmingZhuang,WeiZhang,ZhuopingYang,Sarah ConferenceonArchitecturalSupportforProgrammingLanguagesandOperating
Schultz,YukaiSong,JingtongHu,AlexJones,ZhengDong,andPeipeiZhou. Systems,Volume2.325–339.

AGILE:LightweightandEfficientAsynchronousGPU-SSDIntegration SC’25,November16–21,2025,StLouis,MO,USA
[49] MohaimenulAzamKhanRaiaan,MdSaddamHossainMukta,KanizFatema, [70] JinmingZhuang,ZhuopingYang,andPeipeiZhou.2023.HighPerformance,Low
NurMohammadFahad,SadmanSakib,MostMarufatulJannatMim,JubaerAh- PowerMatrixMultiplyDesignonACAP:fromArchitecture,DesignChallenges
mad,MohammedEunusAli,andSamiAzam.2024.AreviewonlargeLanguage andDSEPerspectives.In202360thACM/IEEEDesignAutomationConference
Models:Architectures,applications,taxonomies,openissuesandchallenges. (DAC).1–6.doi:10.1109/DAC56929.2023.10247981
IEEEAccess(2024).
[50] SamyamRajbhandari,OlatunjiRuwase,JeffRasley,ShadenSmith,andYuxiong
He.2021.Zero-infinity:Breakingthegpumemorywallforextremescaledeep
learning.InProceedingsoftheinternationalconferenceforhighperformancecom-
puting,networking,storageandanalysis.1–14.
[51] ShainaRazaandChenDing.2019. Progressincontext-awarerecommender
systems—Anoverview.ComputerScienceReview31(2019),84–97.
[52] Jie Ren, Samyam Rajbhandari, Reza Yazdani Aminabadi, Olatunji Ruwase,
ShuangyanYang,MinjiaZhang,DongLi,andYuxiongHe.2021.{Zero-offload}:
Democratizing{billion-scale}modeltraining.In2021USENIXAnnualTechnical
Conference(USENIXATC21).551–564.
[53] XiaoweiRenandMieszkoLis.2021. Chopin:Scalablegraphicsrenderingin
multi-gpusystemsviaparallelimagecomposition.In2021IEEEInternational
SymposiumonHigh-PerformanceComputerArchitecture(HPCA).IEEE,709–722.
[54] Samsung.2025.Samsung990PROPCIe4.0SSD|SamsungSemiconductorGlobal.
https://semiconductor.samsung.com/consumer-storage/internal-ssd/990-pro/
[55] ScottBeamer.2024.sbeamer/gapbs:GAPBenchmarkSuite. https://github.com/
sbeamer/gapbs
[56] PaulSweazeyandAlanJaySmith.1986.Aclassofcompatiblecacheconsistency
protocolsandtheirsupportbytheIEEEfuturebus. ACMSIGARCHComputer
ArchitectureNews14,2(1986),414–423.
[57] Tom’sHardware.2021.Samsung980ProM.2NVMeSSDReview:Redefining
Gen4Performance|Tom’sHardware. https://www.tomshardware.com/reviews/
samsung-980-pro-m-2-nvme-ssd-review
[58] PengyuWang,JingWang,ChaoLi,JianzongWang,HaojinZhu,andMinyi
Guo.2021. Grus:Towardunified-memory-efficienthigh-performancegraph
processingongpu. ACMTransactionsonArchitectureandCodeOptimization
(TACO)18,2(2021),1–25.
[59] YangzihaoWang,AndrewDavidson,YuechaoPan,YuduoWu,AndyRiffel,and
JohnDOwens.2016.Gunrock:Ahigh-performancegraphprocessinglibraryon
theGPU.InProceedingsofthe21stACMSIGPLANsymposiumonprinciplesand
practiceofparallelprogramming.1–12.
[60] YangWang,JiwuShu,GuangyanZhang,WeiXue,andWeiminZheng.2010.
Sopa:Selectingtheoptimalcachingpolicyadaptively. ACMTransactionson
Storage(TOS)6,2(2010),1–18.
[61] ZekeWang,HongjingHuang,JieZhang,FeiWu,andGustavoAlonso.2022.
{FpgaNIC}:An{FPGA-based}versatile100gb{SmartNIC}for{GPUs}.In2022
USENIXAnnualTechnicalConference(USENIXATC22).967–986.
[62] KunWu,JeongminBrianPark,XiaofanZhang,MertHidayetoğlu,VikramSharma
Mailthody,SitaoHuang,StevenSamLumetta,andWen-meiHwu.2024.SSDTrain:
AnActivationOffloadingFrameworktoSSDsforFasterLargeLanguageModel
Training.arXivpreprintarXiv:2408.10013(2024).
[63] Shao-PengYang,MinjaeKim,SanghyunNam,JuhyungPark,Jin-YongChoi,
EyeeHyunNam,EunjiLee,SungjinLee,andBryanSKim.2023.Overcoming
thememorywallwith{CXL-Enabled}{SSDs}.In2023USENIXAnnualTechnical
Conference(USENIXATC23).601–617.
[64] ZhuopingYang,JinmingZhuang,JiaqiYin,CunxiYu,AlexK.Jones,andPeipei
Zhou.2023. AIM:AcceleratingArbitrary-precisionIntegerMultiplicationon
HeterogeneousReconfigurableComputingPlatformVersalACAP.InICCAD.
[65] HaoyangZhang,YiruiZhou,YuqiXue,YiqiLiu,andJianHuang.2023. G10:
Enablinganefficientunifiedgpumemoryandstoragearchitecturewithsmart
tensormigrations.InProceedingsofthe56thAnnualIEEE/ACMInternational
SymposiumonMicroarchitecture.395–410.
[66] YuZhang,YuxuanLiang,JinZhao,FubingMao,LinGu,XiaofeiLiao,HaiJin,
HaikunLiu,SongGuo,YangqingZeng,etal.2022.Egraph:efficientconcurrent
GPU-baseddynamicgraphprocessing.IEEETransactionsonKnowledgeandData
Engineering35,6(2022),5823–5836.
[67] JinmingZhuang,JasonLau,HanchenYe,ZhuopingYang,YuboDu,JackLo,
KristofDenolf,StephenNeuendorffer,AlexJones,JingtongHu,DemingChen,
JasonCong,andPeipeiZhou.2023.CHARM:ComposingHeterogeneousAcceleR-
atorsforMatrixMultiplyonVersalACAPArchitecture.InThe2023ACM/SIGDA
InternationalSymposiumonField-ProgrammableGateArrays(FPGA’23).Associa-
tionforComputingMachinery,NewYork,NY,USA.doi:10.1145/3543622.3573210
[68] JinmingZhuang,ShaojieXiang,HongzhengChen,NiansongZhang,Zhuoping
Yang,TonyMao,ZhiruZhang,andPeipeiZhou.2025.ARIES:AnAgileMLIR-
BasedCompilationFlowforReconfigurableDeviceswithAIEngines.InProceed-
ingsofthe2025ACM/SIGDAInternationalSymposiumonFieldProgrammableGate
Arrays(Monterey,CA,USA)(FPGA’25).AssociationforComputingMachinery,
NewYork,NY,USA,92–102. doi:10.1145/3706628.3708870
[69] JinmingZhuang,ZhuopingYang,ShixinJi,HengHuang,AlexK.Jones,Jingtong
Hu,YiyuShi,andPeipeiZhou.2024.SSR:SpatialSequentialHybridArchitecture
forLatencyThroughputTradeoffinTransformerAcceleration.InProceedings
ofthe2024ACM/SIGDAInternationalSymposiumonFieldProgrammableGate
Arrays(FPGA’24).55–66.