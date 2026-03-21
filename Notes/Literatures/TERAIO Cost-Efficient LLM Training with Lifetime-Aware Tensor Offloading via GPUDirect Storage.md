| Cost-Efficient | LLM        | Training      | with      | Lifetime-Aware |     |
| -------------- | ---------- | ------------- | --------- | -------------- | --- |
| Tensor         | Offloading | via           | GPUDirect | Storage        |     |
| ZiqiYuan1      |            | HaoyangZhang1 |           | YiruiEricZhou1 |     |
ziqiy6@illinois.edu zhang402@illinois.edu yiruiz2@illinois.edu
| ApoorveMohan2         |     | I-HsinChung2       |     | SeetharamiSeelam2  |     |
| --------------------- | --- | ------------------ | --- | ------------------ | --- |
| apoorve.mohan@ibm.com |     | ihchung@us.ibm.com |     | sseelam@us.ibm.com |     |
5202 nuJ 6  ]CD.sc[  1v27460.6052:viXra
JianHuang1
jianh@illinois.edu
| 1UniversityofIllinoisUrbana-Champaign |     |     |     | 2IBMResearch |     |
| ------------------------------------- | --- | --- | --- | ------------ | --- |
Abstract
Wepresentthedesignandimplementationofanewlifetime-awaretensoroffloading
| framework                                          | for GPU memory                                            | expansion using    | low-cost    | PCIe-based        | solid-state |
| -------------------------------------------------- | --------------------------------------------------------- | ------------------ | ----------- | ----------------- | ----------- |
| drives(SSDs).                                      | Ourframework,Teraio,isdevelopedexplicitlyforlargelanguage |                    |             |                   |             |
| model(LLM)trainingwithmultipleGPUsandmultipleSSDs. |                                                           |                    |             | Itsdesignisdriven |             |
| by our observation                                 | that                                                      | the active tensors | take only a | small fraction    | (1.7% on    |
average)ofallocatedGPUmemoryineachLLMtrainingiteration,theinactive
tensorsareusuallylargeandwillnotbeusedforalongperiodoftime,creating
ampleopportunitiesforoffloading/prefetchingtensorsto/fromslowSSDswithout
| stallingtheGPUtrainingprocess. |     | Teraioaccuratelyestimatesthelifetime(active |     |     |     |
| ------------------------------ | --- | ------------------------------------------- | --- | --- | --- |
periodoftimeinGPUmemory)ofeachtensorwiththeprofilingofthefirstfew
| iterationsinthetrainingprocess. |     | Withthetensorlifetimeanalysis,Teraiowill |     |     |     |
| ------------------------------- | --- | ---------------------------------------- | --- | --- | --- |
generateanoptimizedtensoroffloading/prefetchingplanandintegrateitintothe
| compiled LLM | program | via PyTorch. Teraio | has a runtime | tensor | migration |
| ------------ | ------- | ------------------- | ------------- | ------ | --------- |
enginetoexecutetheoffloading/prefetchingplanviaGPUDirectstorage,which
allowsdirecttensormigrationbetweenGPUsandSSDsforalleviatingtheCPU
| bottleneckandmaximizingtheSSDbandwidthutilization. |              |                 |                    | Incomparisonwith |              |
| -------------------------------------------------- | ------------ | --------------- | ------------------ | ---------------- | ------------ |
| state-of-the-art                                   | studies such | as ZeRO-Offload | and ZeRO-Infinity, |                  | we show that |
TeraioimprovesthetrainingperformanceofvariousLLMsby1.47×onaverage,
andachieves80.7%oftheidealperformanceassumingunlimitedGPUmemory.
1 Introduction
Largelanguagemodels(LLMs)havebeenwidelyemployedinvariousapplicationdomains[24,35,32].
However,trainingLLMsisstillawell-knownchallengingproblem,asitsmemorydemandisincreasing
atamuchfasterspeedthanthescalingspeedofGPUmemory[14,19]. ScalingtheGPUmemory
capacityisbothtechnicallychallengingandprohibitivelyexpensive. Duetospaceconstraintsand
DRAM scaling issues [15, 11], it is hard to scale up the GPU memory capacity on each server
machine. ScalingoutLLMtrainingwithaclusterofGPUserverscanincreasetheaggregatedmemory
capacity,however,itinevitablyincreasesoperationalcost,placingamajorbarrierforresearchersand
developerstoentryintocutting-edgeLLMdevelopment.
ToovercometheGPUmemorywall,priorstudiesproposedexpandingGPUmemorywithexternal
memorydevices. OnecommonapproachistoallowtensoroffloadingfromGPUmemorytohost
memory[13,30,8,34,25,31,33,16]. However,duetothefundamentalDRAMscalabilitychallenge,
suchanapproachisstilllimitedbythehostmemory. Recentstudieshaveextendedtensoroffloading

toPCIe-basedSSDsthatofferlargercapacityatamuchlowercost[1,29,12,18,36,39,22,38]. But
duetotheincapabilityofefficientlyutilizingtheSSDbandwidthandhidingtheslowSSDaccesses,
theseoffloadingsolutionsstilldeliversuboptimalperformance. Forinstance, ZeRO-infinity[29]
enabledtheoffloadingoftensorstoSSDsatthegranularityofdeepneuralnetwork(DNN)layers,its
coarse-grainedoffloading/prefetchingschemewastesnotonlythelimitedSSDbandwidthbutalsothe
preciousGPUmemoryspace,leavingthesolutionlessattractiveinpractice.
Ideally, we wish to expand GPU memory with low-cost SSDs while achieving similar training
performanceastheidealcaseassumingGPUshaveunlimitedon-boardmemory. Tothisend,we
presentanewtensoroffloadingframework–Teraio,whichenablesfine-grainedoffloadingoftensors
inanaccuratefashionbasedontheiractivitypatternsinGPUs,forbestutilizingbothSSDbandwidth
andGPUmemory. Ourstudyoftensoractivitypatterns(§2)inLLMtrainingshows(1)theactive
tensors,whichareusedinthecurrentkernelduringLLMtraining,consumeonlyasmallportion
(1.7%onaverage)ofrequestedGPUmemoryintotal;(2)manyinactivetensorsarelargeandoccupy
asubstantialGPUmemoryspaceineachtrainingiteration;but(3)theseinactivetensorsarenotused
inthetrainingforalongperiodoftime,dependingonthecomputationintensityofLLMs.
Withtheseinsights,Teraiodevelopsalifetime-awaretensoroffloadingmechanismfollowingthree
designprinciples: (1)offloadinglargeinactivetensorstoSSDscansavepreciousGPUmemoryand
maximizeSSDbandwidthutilizationduringthetrainingprocess;(2)thedistributionoftheirinactive
periodsoftimewillhelpTeraiodecidewhichinactivetensorshouldbeoffloadedatwhattime,and
similarly,whichtensorshouldbeprefetchedatwhattime;(3)preciselyschedulingtensoroffloading
andprefetchinginconsiderationoftheavailableSSDbandwidthwillhelpTeraioeffectivelyoverlap
thetensormovementwithGPUcomputation. Ourrooflinemodelanalysis(§2.2)showsthat,given
eachGPUconnectedtomultiplecommoditySSDstoday,theaggregatedstorageI/Obandwidthis
sufficienttomeetthetensormigrationrequirementwithouthurtingtheGPUtrainingprocess.
Tofulfillthedesignprinciplesdiscussedabove,wedevelopTeraiowiththreemajorcomponents:
(1)atensorlifetimeprofilerthatcanextracttensoractivitypatterns(e.g.,tensorsizeandlifetime)
in advance with the assistance of deep learning compilers such as PyTorch, (2) a lifetime-aware
tensormigrationalgorithmthatcangenerateoptimaltensoroffloading/prefetchingplansbasedon
thelearnedtensoractivitypatterns,and(3)atensormigrationenginethatwillexecutethegenerated
offloading/prefetchingplanswithefficientdirectdatatransferbetweenGPUs,hostmemory,andSSDs.
Wepresenteachofthesecomponentsasfollows.
Anopen-sourcetensorlifetimeprofiler. Teraioconductstheprofilingofthetensorsizeandlifetime
distributionsbyrunningthefirstfewiterationsofLLMtrainingonthetargetGPUsetting. Asthe
computationanddataflowpatternsofeachiterationarealmostthesame,theprofilingresultscan
accuratelyrepresentthegenericpatternsoftheentireLLMtrainingprocess. Totrackthemetadata
informationofeachtensor,weinstrumenttheautomaticoperatorgeneratorinPyTorchratherthan
intrusivelyinstrumentthesourcecodeofeachgeneratedoperator. Therefore,theproiflerrequires
minimalcodemodificationstoPyTorch. AstheexecutionofLLMonGPUshashighlypredictable
dataflowpatterns,TeraiousestheexecutiontimeofGPUkernelstoaccuratelyestimatethetensor
lifetime(i.e., thelengthoftheactiveandinactiveperiodoftime). Withtheknowledgeoftensor
activitypatterns,Teraiowillcreatethetensoroffloading/prefetchingplansinadvance.
Lifetime-awaretensormigrationalgorithm. Teraioprioritizesoffloadinglargetensorswithlong
inactiveperiodoftimetoSSDs,forfullyutilizingtheavailablestorageI/Obandwidth. Fortensors
that have short inactive periods of time, Teraio will make the best effort to retain them in GPU
memory,foravoidingunnecessarymigrationoverhead. AshostmemoryandSSDofferdifferent
capacities,bandwidths,andcosts,TeraiopreferstooffloadtensorstoSSDsfortakingadvantageof
theirlargecapacityandlowcost. However,whentheSSDbandwidthissaturatedatruntime,Teraio
willusethehostmemoryastheoffloadingdestination. GivenanexecutionplanforeachLLMtraining
iteration,Teraiowilliterativelysearchforthebestoffloadingcandidatebasedonthetensorsizeand
lifetime,untiltherequiredGPUmemoryisbelowthecapacitylimit. Afterthat,Teraiowillgenerate
anoptimizedtensormigrationplanbyaddingcorrespondingoffloadingandprefetchinginstructions
inthecompiledLLMtrainingprogram.
TensormigrationengineusingGPUDirectstorage. Followingthetensormigrationplanintegrated
intothecompiledLLMtrainingprogram,thetenormigrationengineof Teraiowilloffload/prefetch
tensorsto/fromSSDsorhostmemoryatruntime. ForthetensormigrationbetweenGPUmemory
andSSD,TeraiousesGPUDirectstoragetoenabledirectdatatransferbetweenGPUsandSSDs,
2

therefore, it can bypass the host CPU to alleviate the scalability bottleneck and maximize SSD
bandwidthutilization. WhentheavailableSSDbandwidthisinsufficienttosupporttensoroffloading
andprefetching,Teraiowillmigratetensorstothehostmemory. Totrackthelatestlocationsof
tensors (GPU memory, host memory, or SSDs), Teraio indexes tensors with their identification
numbersusinghashmaps.
WeimplementthecorecomponentsofTeraiobasedonPyTorch. Therefore,Teraiodoesnotrequire
anycodemodificationstoLLMtrainingprograms. ToevaluatetheefficiencyofTeraio,wetrainaset
ofLlamaandGranitemodelswithdifferentbatchsizesandsequencelengthsusingTorchTitan[17]
onaGPUserverthathastwoNVIDIAH100GPUsandeightPCIe-basedSSDs. Incomparisonwith
state-of-the-artoffloadingsolutionsZeRO-Offload[30]andZeRO-Infinity[29],Teraioimproves
thetrainingperformanceby1.47×onaverage,achieves80.7%oftheidealperformanceassuming
unlimited GPU on-board memory, and delivers 1.45× improvement on cost efficiency for LLM
training. Insummary,wemakethefollowingcontributions.
• Weconductaquantitativecharacterizationstudyoftensormemoryusagewhentraining
differentLLMsonmultipleGPUs, andshowthatthehighcomputeintensityofmodern
LLMsproviderichopportunitiesfortensoroffloading.
• WedevelopalightweighttensorlifetimeprofilerbasedonPyTorch,whichcanlearntensor
activitypatternsformulti-GPULLMtraining.
• We design a lifetime-aware tensor migration planning algorithm that optimizes offload-
ing/prefetchingdecisionsbasedontensoractivitypatterns,GPUmemorycapacity,andthe
availablemigrationbandwidth.
• Weimplementatransparenttensormigrationenginethatenablesdirectdatatransferbetween
GPUandSSDs,alleviatingthescalabilitybottleneckonthehost.
• WeconductathoroughevaluationofTeraiowiththetrainingofvariousLLMs,demonstrating
significantimprovementontrainingperformanceandcostefficiency,comparedtostate-of-
the-artoffloadingsolutions.
2 CharacterizationStudyofTensorActivityPatternsinLLMTraining
Inthissection,wepresentourcharacterizationstudyoftensoractivitypatternsinLLMtraining. To
facilitateourstudy,weutilizeourtensorlifetimeprofiler,whichwillbediscussedin§3.1,toanalyze
thedistributionsoftensorsizesandlifetimesduringtheLLMtraining. WeusetwoNVIDIAH100
GPUsand2-stage1f1bpipelineparallelism[21]inourexperiments. Ourstudycoversavarietyof
LLMswithdifferentarchitectures,includingdecoder-onlymodelssuchasLlama3-8B,Llama3-70B
[4],andGPT2-40B[27],aswellasencoder-decodermodelslikeT5-11B[6]. Formodelsthatrequire
morememorythanGPUmemorycapacity,weoffloadtensorsnotneededbythecurrentkernelto
SSDs. Wesummarizeourstudyresultsasfollows.
|     | all active |     |     | all active |     |
| --- | ---------- | --- | --- | ---------- | --- |
100%
100%
noitpmusnoC yromeM 10%
|   1% |     |     |   10% |     |     |
| ---- | --- | --- | ----- | --- | --- |
0.1%
| 0 10000 | 20000 30000                         | 40000 50000 | 0 5000 | 10000 15000                        | 20000 |
| ------- | ----------------------------------- | ----------- | ------ | ---------------------------------- | ----- |
|         | (a) Llama3-8B-GPU0 GPU Kernel Index |             |        | (d) GPT2-40B-GPU0 GPU Kernel Index |       |
| 100%    |                                     |             | 100%   |                                    |       |
| 10%     |                                     |             | 10%    |                                    |       |
|         |                                     |             |   1%   |                                    |       |
1%
| 0.1% |     |     | 0.1% |     |     |
| ---- | --- | --- | ---- | --- | --- |
0 50000 100000 150000 200000 250000 0 10000 20000 30000 40000 50000 60000
|     | GPU Kernel Index    |     |     | GPU Kernel Index |     |
| --- | ------------------- | --- | --- | ---------------- | --- |
|     | (c) Llama3-70B-GPU0 |     |     | (d) T5-11B-GPU0  |     |
(a)MemoryconsumptionofdifferentLLMsoneachGPU.
| noitpmusnoC  | all                         | active      |        | all active                  |       |
| ------------ | --------------------------- | ----------- | ------ | --------------------------- | ----- |
|  yromeM 100% |                             |             | 100%   |                             |       |
|   10%        |                             |             |   10%  |                             |       |
| 0            | 5000 10000                  | 15000 20000 | 0 5000 | 10000 15000                 | 20000 |
|              | GPU Kernel Index            |             |        | GPU Kernel Index            |       |
|              | (a) GPT2-40B-GPU0 (Stage-0) |             |        | (d) GPT2-40B-GPU3 (Stage-1) |       |
(b)Memoryconsumptionofdifferentstagesinthepipelineparallelism.
Figure1: Memoryconsumptionofallandactivetensors(w.r.t. theGPUmemorycapacity)inone
iterationoftheparalleltrainingprogram. Logarithmicscaleisusedinthepresentation.
3

| 100 |             |     | 100          | 100 |             |     | 100 |              |     |
| --- | ----------- | --- | ------------ | --- | ----------- | --- | --- | ------------ | --- |
|     | <1MB (9.2%) |     | <1MB (11.4%) |     | <1MB (9.9%) |     |     | <1MB (15.6%) |     |
80 1 – 1 0 M B  ( 4 . 6 % ) 80 1 – 1 0 M B  ( 1 3 . 6 % ) 80 1 – 1 0 M B  ( 1 3 . 5 % ) 80 1–10MB (28.3%)
|     | 1 100MB–200MB (47.2%) 0 – 1 00 M B   ( 2 | 2 .3%) | 1 100MB–1GB (30.2%) 0 – 1 00 M B   ( 4 4 .6 %) |     | 1 100MB–1GB (22.8%) 0 – 1 00 M B |   ( 5 3 .9 %) |     | 10–50MB (14.3%) 50MB–100MB (39.8%) |     |
| --- | ---------------------------------------- | ------ | ---------------------------------------------- | --- | -------------------------------- | ------------- | --- | ---------------------------------- | --- |
)%( FDC 60 >200MB (16.7%) )%( FDC 60 >1GB (0.1%) )%( FDC 60 )%( FDC 60 >100MB (2.0%)
| 40  |     |     | 40  | 40  |     |     | 40  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20  |     |     | 20  | 20  |     |     | 20  |     |     |
|     | 0   |     | 0   |     | 0   |     | 0   |     |     |
100 102 104 106 108 100 102 104 106 108 100 102 104 106 108 100 102 104 106 108
Inactive Time (μs) Inactive Time (μs) Inactive Time (μs) Inactive Time (μs)
|     | (a) Llama3-8B |          | (b) GPT2-40B                               |     | (c) Llama3-70B |     |     | (d) T5-11B |     |
| --- | ------------- | -------- | ------------------------------------------ | --- | -------------- | --- | --- | ---------- | --- |
|     |               | Figure2: | Thedistributionofinactiveperiodsoftensors. |     |                |     |     |            |     |
2.1 RichOpportunitiesforTensorMigration
Smallmemoryrequirementofactivetensors. Wefirststudythememorydemandandusageof
tensorsineachtrainingiteration. WedefinethetensorsthatarecurrentlyusedbyarunningGPU
kernelasactivetensors. WepresentthememoryconsumptionofactivetensorsusedbyeachGPU
kernel in Figure 1. Figure 1 (a) shows the memory consumption of tensors in different models,
Figure1(b)showsthememoryconsumptionoftensorsacrossdifferentpipelinestages. ForallLLMs
examinedinourstudy,theactivetensorsaccountforonlylessthan14%(1.7%onaverage)ofthe
totalGPUmemorycapacity,althoughtheirtotalmemoryusagegreatlyexceedstheGPUmemory
capacity. MosttensorsinGPUmemoryareinactiveandcanbeoffloadedtolow-costSSDs,thus,we
canbestutilizetheGPUmemoryfortensorsthatwillbeusedbykernelsinthenearfuture.
| Longinactiveperiodsofinactivetensors. |     |     |     | Tounderstandhow |     |     |     |     |     |
| ------------------------------------- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- |
1.0
| long                                                    | the inactive | tensors | remain inactive | and how much | GPU | tuphguorhT dezilamroN |     |     |     |
| ------------------------------------------------------- | ------------ | ------- | --------------- | ------------ | --- | --------------------- | --- | --- | --- |
| memorytheyconsume,westudythedistributionoftheirinactive |              |         |                 |              |     | 0.8                   |     |     |     |
Llama3-8B
periods,asshowninFigure2. Forallthemodelswestudy,most Llama3-70B
0.6
| tensorshavesizesthatrangefrom10MBto1GB.Weobservethat |     |     |     |     |     |     |     | T5-11B |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------ | --- |
GPT2-40B
0.4
morethan40%ofthesetensorsremaininactiveformorethan104
| microseconds. |     | Theseinactiveperiodsarelongerthanthetime |     |     |     | 0.2 |     |     |     |
| ------------- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
neededtomigratethesetensorstoSSDsatabandwidthof6.5
|     |     |     |     |     |     | 0.0 0 | 4 81216 | 24 32 48 | 64  |
| --- | --- | --- | --- | --- | --- | ----- | ------- | -------- | --- |
GB/s. Withthisinsight,wecanensurethatthesetensorscanbe
Available Migration Bandwidth (GB/s)
migratedefficientlywithoutintroducingnegativeimpactonthe Figure3: Rooflineanalysiswith
| trainingperformance. |     |     |     |     |     | different | migration | bandwidths. |     |
| -------------------- | --- | --- | --- | --- | --- | --------- | --------- | ----------- | --- |
Thetrainingperformanceisnor-
Thelonginactiveperiodsarethecauseofthesparsetensoraccess malizedtotheidealcaseassuming
pattern and high compute intensity of LLMs. From a spatial GPUmemoryisinfinite.
perspective,althoughLLMshavetensorhundredsoflayers,many
tensors are used within only a single layer. From a temporal perspective, the compute-intensive
kernels(e.g.,attention)ineachlayertakeaconsiderableamountoftime,providingrichopportunities
forTeraiotooverlapthecomputationwiththemigrationofinactivetensors.
Wealsoobservethat,comparedwithtraditionalDNNmodels,thehighercomputeintensityandlarger
modelsizesofLLMsleadtosubstantiallylongerinactiveperiods. Forexample,inBERT-Large[3],
48%oftensorsarelargerthan100MB,andtheinactiveperiodsofmorethan60%oftheselarge
tensorsaretwoordersofmagnitudeshorterthanthoseinLLMs.
2.2 BandwidthRequirementforTensorMigration
Wenowstudyhowmuchmigrationbandwidthisneededforoffloadingtoachievenear-idealtraining
performance. WequantifytherooflineperformanceofdifferentLLMmodelsunderdifferentmigration
bandwidthsavailabletoeachGPU.Tofacilitatethisstudy,webuildaperformancemodeltoestimate
thetrainingtime. Inthemodel,weassumethateachkernel’sexecutiontimeisthesameasthevalue
collectedinourcharacterizationstudy. Wesimulatetensormigrationatthedesignatedbandwidth,
and check whether the tensors needed by the kernel are already in GPU memory or not. If they
arestillbeingmigratedduetolimitedSSDbandwidth,thewaitingtimeforthemigrationisadded
to the total training time. Figure 3 shows the normalized roofline training throughput of LLMs
underdifferentmigrationbandwidths. Weobservethatabandwidthof32to48GB/sissufficientto
achievenear-idealperformanceforLLMs. Suchabandwidthrequirementcanbeeasilyachievedby
aggregatingmultiplecommoditySSDs(e.g.,anSSDarray),demonstratingthefeasibilityofTeraio.
4

| Lifetime-Aware Tensor Migration Algorithm (§3.3) |     |     |     |     | Per-GPU Tensor Migration Plans |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | ------------------------------ | --- | --- | --- | --- |
GPU Memory
|                          |              |      |                    |                          | tensor ID | type start kernel     | deadline kernel |              |     |
| ------------------------ | ------------ | ---- | ------------------ | ------------------------ | --------- | --------------------- | --------------- | ------------ | --- |
|                          |              |      |                    |                          | 1         | Offload 5             | 10              |              |     |
|  Execution Graph Tracing |              |      |                    |                          | 2         | Reload 48             | 117             |              |     |
|                          |              | T e  | n sor L i f e time |   I n f o r ma t io n    | ...       | ... ...               | ...             |              |     |
|                          | tensor usage | te n | so r               |                          |           |                       |                 |              | GPU |
|                          |              |      | s i z e            | li f e t i m e le n g th |           |                       |                 | E x e c ut e |     |
|                          |              | ID   |                    |                          |           |                       |                 | ru n t im e  |     |
|                          |              | 1    | 256MB              | {1, 3} 645us             |           |                       |                 |  migrations  |     |
|                          |              |      |                    |                          |           | Tensor Location Table |                 | via GDS      |     |
GPU Kernel Profiling kernel exec. time 2 2M B {2 ,   3} 124 0 us P C I e SSDs
|     |     | . .. | ... | . . . .. . | tensor 1 | tensor 2 | tensor 3 |     | S w it c h |
| --- | --- | ---- | --- | ---------- | -------- | -------- | -------- | --- | ---------- |
|     |     |      |     |            | GPU Mem  | SSDs     | CPU Mem  |     |            |
Tensor Lifetime Profiler (§3.2)
|     |     |     |     |     | GDS-Based Tensor Migration Engine (§3.4) |     |     |     | CPU Main Memory |
| --- | --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | --------------- |
PyTorch Framework
|     |     |     | Figure4: | SystemoverviewofTeraio. |     |     |     |     |     |
| --- | --- | --- | -------- | ----------------------- | --- | --- | --- | --- | --- |
3 TeraioDesignandImplementation
WeshowthesystemoverviewofTeraioinFigure4. GivenanLLM,Teraio’stensorlifetimeprofiler
works with PyTorch to track tensor sizes and lifetimes (§3.1). In the first few training iterations,
Teraiotracestheexecutiongraphandcollectstheexecutiontimeofeachkernel. Sincethetraining
followsthesameexecutiongraphinsubsequentiterations,thetensoractivitypatternsremainthe
same. The tensor migration algorithm (§3.2) creates a tensor migration plan that (1) maximally
overlapscomputationandmigration,and(2)minimizesmigrationtraffic. Thealgorithmiteratively
selectsthebestoffloadingcandidatesuntiltherequiredGPUmemoryfitswithintheactualGPU
memorycapacity. Forthemigrationdestination,itpreferstomigratetensorstoSSDs. OncetheSSD
bandwidthissaturated,italsousesavailableCPUmemory. DuringLLMtraining,Teraio’stensor
migrationenginetransparentlyexecutesthemigrationplan(§3.3).
3.1 TensorLifetimeProfiler
Tracking tensors. Teraio instruments PyTorch framework to track tensors and measure kernel
executiontimeatruntime. Atensorisconsideredactiveinoneofthefollowingthreescenarios.
First, a tensor is active when it is the input or output of a PyTorch CUDA operator. However,
instrumentingPyTorchtotrackeveryoperatorischallenging,astherearethousandsofoperators.
Instead,weleveragePyTorch’sautomaticoperatorgenerator,whichproducessourcecodeforeach
operator,toinsertprofilingcodethatwillmarkallinputandoutputtensorsasactivewhentheoperator
is executed at runtime. Second, for tensors that are involved in inter-GPU communication, they
shouldbeactiveinGPUmemory. Third,atensorisconsideredactivewhenPyTorchexplicitlychecks
whetheritresidesinGPUmemory. Thishappenswhenupdatingoptimizerstates. Forthesecondand
thirdscenarios,sincethereareonlyafewcommunicationoperatorsandPyTorchchecksintotal,we
directlysetthecorrespondingtensorsasactiveinthesourcecode.
|     |     |     | Inter-GPU | PyTorch |     | Active | Inactive | Not |     |
| --- | --- | --- | --------- | ------- | --- | ------ | -------- | --- | --- |
Operator
|     |     | Communication |     | Check |     | Period | Period | Allocated |     |
| --- | --- | ------------- | --- | ----- | --- | ------ | ------ | --------- | --- |
Runtime Tensor Lifetime Tracking
Tensor Inactive Periods
|          | Operator 0      | Comm 0   | Operator 1 | Check 0  | Operator 2   |        |         |            |        |
| -------- | --------------- | -------- | ---------- | -------- | ------------ | ------ | ------- | ---------- | ------ |
| Ex ec    | u tion Tensor 1 | Tensor 0 | Tensor 2   | Tensor 1 | Tensor 0,1,2 | Update | Ten sor | size start | end    |
| F lo     | w               |          |            |          |              |        | ID      |            |        |
| Tensor 0 |                 |          |            |          |              |        | 0       | 64MB op1   | op2    |
|          |                 |          |            |          |              |        | 1 128MB | op0        | check0 |
Tensor 1
|     |     |     |     |     |     |     | 2   | 64MB comm0 | op2 |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- |
Tensor 2
Figure5: Teraiotracksandanalyzestensoractivitypatternsforthetensormigrationalgorithm.
Analyzingtensoractivitypatterns. Figure5showshowtensorinformationiscollectedatruntime.
TounderstandwhenatensorconsumesGPUmemoryandwhenitmustresideinGPUmemory,we
needtocollectitstensorsizeandactivetime. Whenanoperatorisexecuted,theinstrumentedcode
recordsthetensorsizeandactivetimeforthecorrespondingtensor. Theprofilerwillcalculatethe
inactivetimeperiodbasedonthedurationbetweenitsactivestates. Specifically,forintermediate
tensorssuchasgradientsandactivations(Tensor0andTensor1inFigure5)thatwillbedeallocated
immediatelyafteritscomputationcompletes,wequantifyitsinactivetimeperiodasthetimeinterval
betweenthetwoactiveperiods. Forglobaltensorssuchasmodelweightsandoptimizerstates(Tensor
2inFigure5)thatareusedacrossmultipletrainingiterations,theyareallocatedbeforetrainingstarts
andneverdeallocatedduringtraining. Therefore,forsomecases,theprofilermayneedtocalculate
itsinactiveperiodbasedontheactivestatesacrosstwoiterations.
5

|     | I/O bandwidth saturated by previously planned tensor migrations |     |     | Total amount of required GPU memory |
| --- | --------------------------------------------------------------- | --- | --- | ----------------------------------- |
Total amount of required GPU memory after offloading this tensor
I/O bandwidth that will be used by offloading the current tensor
Benefits we can get from offloading the tensor
 yromeM UPG deriuqeR
Tensor Inactive Period I
I/O Bandwidth Usage
Offloading GPU Memory
Capacity
Prefetching
time time
|     | (a). I/O bandwidth usage affects actual migration time |     |     | (b). The benefit of offloading one inactive tensor  |
| --- | ------------------------------------------------------ | --- | --- | --------------------------------------------------- |
Figure6: Illustrationexamplestoexplainthekeyinsightsoflifetime-awaremigrationalgorithm.
3.2 Lifetime-awareTensorMigrationAlgorithm
Thelifetime-awaretensormigrationalgorithmiterativelyfindsthebestoffloadingcandidatesineach
LLMtrainingiteration,untiltherequiredGPUmemoryisbelowthecapacitylimit. Bytrackingthe
amountofrequiredGPUmemoryandthestorageI/Obandwidthutilization,thealgorithmisableto
evaluatethepotentialbenefitsoftensoroffloading. Wediscussourkeyideasasfollows.
StorageI/Obandwidth-awareplanning. Tooffloadaninactivetensor,wewishtokeepitoutof
GPU memory as long as possible. Therefore, ideally, we would offload it as soon as it becomes
inactiveandprefetchitinstantlybeforeitisneededbythesubsequentkernel. However,inreality,the
timewhenwecanoffloadandprefetchtheinactivetensorisgreatlyaffectedbythestoragebandwidth
usage. Forexample,inFigure6(a),theinactiveperiodIofthetensorisfromt tot . However,
start end
sincetheI/Obandwidthisoccupiedbypreviouslyplannedmigrations,wehavetodelaytheactual
offloadinguntilt andstarttheactualprefetchingbyt . Thismeansthatwecanonly
|     | offload |     |     | prefetch |
| --- | ------- | --- | --- | -------- |
reducethememoryconsumptionfromt tot . Whenplanningtensormigrations,our
|     |     |     | offloaded | prefetch |
| --- | --- | --- | --------- | -------- |
algorithmtrackstheestimatedstorageI/Obandwidthusageandcalculatesthereductioninmemory
consumptioninanI/O-awaremanner(Line4-5and16-17inAlgorithm1).
Algorithm1Lifetime-AwareTensorMigrationPlanning
Require: SetoftensorinactiveperiodsI={(ti,si,starti,endi)}whereti istensorID,si issize,and[starti,endi]definesthekernel
rangeofinactivity;GPUmemorycapacityMGPU ;EstimationoftotalamountofrequiredGPUmemoryM =[m0,m1,...,mN−1]
| acrossNkernels;KernelexecutiontimesT |                                                          |                           | =[τ0,τ1,...,τN−1];I/Obandwidthusagestates |                                          |
| ------------------------------------ | -------------------------------------------------------- | ------------------------- | ----------------------------------------- | ---------------------------------------- |
| E n su r e : M                       | i g ra t io n p l an l i s tP                            | = { (ti , tr ig g e r     | _t i m e, d e a d l i n                   | e , ta r ge t) }                         |
| 1 : In i t ial iz                    | e m i g r ati o n p l a n list                           | an d e st                 | im a t ion of r e q ui r e d              | G P U m em o ryM′=M                      |
|                                      |                                                          | P = { }                   |                                           |                                          |
| 2 : whi l e p                        | e a k m e m o r y c o n s                                | u m p t io n m a x ( M ′) | > M do                                    |                                          |
| 3 :                                  |                                                          |                           | G P U                                     |                                          |
| f o r                                | e a c h in a ct i v e p e ri o                           | d ( t , s ,s t a r t ,en  | d )∈ I d o                                |                                          |
| 4:                                   | Determineearliestfeasibleoffloadcompletiontimetoffloaded |                           |                                           | byanalyzingavailableoffloadingbandwidth  |
| 5:                                   | Determinelatestrequiredprefetchstarttimetprefetch        |                           |                                           | byanalyzingavailableprefetchingbandwidth |
6:
|     | iftoffloaded<tprefetch | then |     |     |
| --- | ---------------------- | ---- | --- | --- |
7:
IdentifycriticalmemorypressureregionsC={k|M′[k]>MGPU,k∈[toffloaded,tprefetch]}
| 8 : | C alculatetheoffloadingbenefitB=s×(cid:80) |     |     |     |
| --- | ------------------------------------------ | --- | --- | --- |
k∈C τk
| 9 : | end if |     |     |     |
| --- | ------ | --- | --- | --- |
10: endfor
1 1 :
| S e         | le ct i n a c ti v ep e r i o | d w it h b e st o ffl o a d i n | g cost-benefit(B/s)max |     |
| ----------- | ----------------------------- | ------------------------------- | ---------------------- | --- |
| 1 2 : i f n | o vi a b l e o ffl o a d i n  | g ca n d id a te e x is t s t   | h en                   |     |
13:
break
14: endif
15: Addmigrationplans(t,start,toffloaded,SSD/CPU)and(t,tprefetch,tprefetched,GPU)toP
16:
UpdateM′bysubtractingtensorsizesfromaffectedkernels
17: UpdateI/Obandwidthusagestates
18: Removeselectedinactiveperiodfromconsideration
19:
endwhile
20: return P
Quantifythebenefitandcostoftensoroffloading. TofullyutilizetheavailableI/Obandwidth,we
wanttoprioritizeoffloadinglargetensorswithlonginactiveperiods. Followingthisprinciple,our
algorithmsearchesforthebestoffloadingcandidatebyestimatingitsbenefitandcost. Toquantifythe
benefit,atagiventimeT,wedefinecriticalmemorypressureasthepartofGPUmemoryconsumption
thatexceedsthecapacity. Thebenefitofatensormigrationisdefinedastheintegralofthereduction
incriticalmemorypressureovertime,asillustratedbytheshadedareainFigure6(b). Wequantify
the cost as the sum of offloading and prefetching time of tensors. Teraio’s migration algorithm
sortsallcandidatesbytheirbenefit-to-costratio. Itthenselectsthetensorwiththehighestratiofor
migrationinthecurrentiteration. ThisprocedureisshowninLine6-11inAlgorithm1.
6

Decideoffloadingdestination. TeraioprioritizesSSDsbecauseoftheirlargecapacityandlowcost.
WhentheestimatedSSDbandwidthissaturated,Teraiowillmakethebestefforttomigratetensors
tothehostmemory. Teraioallowsuserstodefinethemaximumamountofhostmemorythatcan
beusedfortensormigration. Internally,themigrationalgorithmtrackstheestimatedhostmemory
consumption. Ifithasalreadyreachedtheuser-definedlimit,evenifSSDbandwidthissaturated,
Teraiowillnotoffloadtensorstothehostmemory.
Minimizekernelstalls. IftherequiredGPUmemoryexceedstheavailableGPUmemorycapacity,
andTeraiocannotoffloadtensorstoSSDsorhostmemory,Teraiowillstallkernelexecutiontowait
formoreinactivetensorstobeoffloaded. Itwillalsowaitforthetensorsneededbythekerneltobe
migratedbackintoGPUmemory. ThiswouldcausestorageI/Obandwidthcontention. Sincethe
nextkernelwillstalluntiltheneededtensorsaremigratedtoGPUmemory,thesemigrationsshould
completeasearlyaspossibletoavoidstallingtheGPUtrainingprocess. Therefore,Teraiomarks
thesemigrationsthatmustfinishbeforethenextkernelas‘urgent’. Atruntime,thetensormigration
engine(§3.3)alwaysprioritizestheseurgentmigrationsoverotherpendingmigrations.
3.3 TensorMigrationEngineUsingGPUDirectStorage
Toexecutethemigrationplan,weneedtolocatetheaddressesofthetensorstobemigrated,basedon
thetensoridentifier. Teraiomaintainsahashmap-basedtensorlocationtableinPyTorchtomap
tensoridentifierstotheircurrentdevicesandaddresses.
The migration engine migrates tensors between GPU memory and external memory. For tensor
migrationsbetweenGPUmemoryandSSDs,weuseGPUDirectstoragetoachievedirectdatatransfer
betweenthem. OurchoiceofGPUDirectstorageismotivatedbythepotentialscalabilitylimitations
of host CPU in multi-GPU systems. For example, on an 8-GPU system, to achieve near-ideal
performance,eachGPUrequires32to48GB/sbidirectionalbandwidth(see§2). WithGPUDirect
storage,wecandirectlyconnect8SSDstoeachGPUviaPCIeGen5switchestomeetthebandwidth
demand. FortheconventionalapproachthatusesthehostCPUtofirstreaddatafromSSDstothe
hostmemory,andthenusescudaMemcpytomovedatatotheGPU,theredundantdatacopynotonly
causesperformanceoverheadbutalsowastespreciousCPUcycles[7,26]. Butasdiscussed,Teraio
stillsupportsmigrationbetweenGPUsandCPUmemory.
4 Experiments
Weshowthat(1)Teraiooutperformsstate-of-the-artoffloadingframeworksby1.47×onaverage
whentrainingLLMsthatgreatlyexceedGPUmemorycapacity(§4.2);(2)Comparedtothecaseof
trainingLLMsusingonlyGPUmemory,Teraioreducesthecostbyupto5.41×(§4.3);(3)Compared
toexistingoffloadingframeworks,Teraioimprovesthecostefficiencyby1.45×onaverage(§4.3);
(4)TeraioachievesbetterthroughputthanZeRO-InfinityevenwithlessCPUmemoryandfewer
SSDs(§4.4).
4.1 ExperimentalSetup
Models. WeevaluateTeraiowithLlama3-8B,Llama3-70B[4],andGranite-code-base-8B[10]. We
useC4[28]asourtrainingdataset. Tostudyhowdifferentmemorydemandsimpacttheperformance
ofTeraio,weusebatchsizesrangingfrom16to128andsequencelengthsfrom1,024to8,192.
HardwareconfigurationandMLframework. Table1
Table1: OurGPUserverconfiguration.
showsthehardwareconfigurationusedinourexperiments.
DuetothelimitedPCIeslotsonourmachine,wecanonly GPU 2×NVIDIAH100NVL
GPUMemory 94GBHBMperGPU
installatmost8PCIeSSDs. WhenevaluatingTeraio,we CPU 2×AMDEPYC9334
use2H100GPUsand2RAID-0arrayswith4SSDsin CPUMemory 1.5TBDDR5(64GB×24)
Interconnect PCIeGen5
each array. Each RAID-0 array is logically assigned to SSDs 8×Samsung990PRO2TB
SSDRead/WriteBandwidth 6.7/6.5GB/sperSSD
oneGPU,providingapproximately16GB/sbandwidthfor
tensormigrations. WeusePyTorch2.5.0[23]andTorchTitan[17]totrainLLMs.
Baselines. WecompareTeraiowiththeIdealcase,ZeRO-Offload,andZeRO-Infinity. TheIdeal
caseassumesthatallGPUsinthesystemhaveinfiniteon-boardmemory,whichgivesthetheoretical
besttrainingperformance. ZeRO-Offload[30]andZeRO-Infinity[29]arepopularoffloading-based
trainingsystems. ZeRO-OffloadoffloadstensorsfromGPUmemoryonlytoCPUmemory,while
ZeRO-Infinity leverages both SSDs and CPU memory to expand GPU memory. Teraio-SSD
andTeraio-Mixedaretwovariationsof Teraio. Teraio-SSDonlymigratestensorstolow-cost
7

SSDs,whileTeraio-MixedusesbothSSDsandCPUmemory. Tomakeafaircomparison,welet
Teraio-MixedusethesameamountofCPUmemoryfortensormigrationasZeRO-Infinity.
In our evaluation, we aim to compare Teraio with the best performance achievable by ZeRO.
Therefore,fortheparallelizationstrategy,weusetensorparallelismforZeROseries,asitdelivers
optimalmulti-GPUtrainingperformance. Moreover,wespliteachbatchintomultiplemicro-batches
inordertoamortizethewell-knownperformancebottleneck[12]ofZeRO’sCPU-basedoptimizers.
Inaddition,althoughactivationcheckpointing[11,9,37,2]canreducememoryconsumption,we
disableitbecauseitdegradesZeRO’strainingthroughput.
In terms of training precision, we use full-precision training in all experiments. Though mixed-
precisiontraining[20]ispopular,thedifferentmemoryrequirementsofthemixed-precisiontraining
strategiesusedbyTorchTitanandZeROwillleadtoanunfaircomparison. Specifically,whenwe
enablemixed-precisiontraining,intheZeROseries,alltensorsintheGPUarerepresentedby16-bit
floatingpoints,whileinTorchTitan,mosttensors,includingmodelweights,gradients,andoptimizer
statesstillremainin32-bitfloatingpointformat. Suchdifferencesinnumericalformatsoftensors
canleadtosignificantdifferencesinGPUmemoryrequirementsforthesamemodel,resultinginan
unfairscenariowhereTeraiohastomigratelargertensorsthanZeRO.
4.2 End-to-endPerformance
We show the end-to-end average training throughput of Llama3-8B, Granite-code-base-8B and
Llama3-70B with different batch sizes and sequence lengths in Figure 7. On average, Teraio
outperformsZeRO-OffloadandZeRO-Infinityby1.47×. Comparedtotheidealsystemassuming
unlimitedGPUmemory,Teraioachieves80.7%oftheidealperformance.
Llama3-8B Granite-code-base-8B Llama3-70B
2000 1500 200
1500
1000
1000 100
500 500
0 0 0
bs32_seq2048 bs64_seq2048 bs128_seq2048 bs32_seq4096 bs64_seq4096 bs128_seq4096 bs8_seq2048 bs16_seq2048 bs32_seq2048
M = 187.56% M = 188.81% M = 191.32% M = 379.34% M = 381.84% M = 386.84% M = 940.23% M = 940.85% M = 942.10%
tuphguorhT
gniniarT
)s/nekot(
ZeRO-Infinity ZeRO-Offload TeraIO-SSD TeraIO-Mixed Ideal
(1). Averagetrainingthroughputwithdifferentbatchsizes.
Llama3-8B Granite-code-base-8B Llama3-70B
2000 1500 200
1500
1000
1000 100
500 500
0 0 0
bs64_seq1024 bs64_seq2048 bs64_seq4096 bs64_seq2048 bs64_seq4096 bs64_seq8192 bs16_seq2048 bs16_seq3072 bs16_seq4096
M = 187.56% M = 188.81% M = 191.32% M = 379.34% M = 381.84% M = 386.85% M = 942.10% M = 1091.80% M = 1242.75%
tuphguorhT
gniniarT
)s/nekot(
ZeRO-Infinity ZeRO-Offload TeraIO-SSD TeraIO-Mixed Ideal
(2). Averagetrainingthroughputwithdifferentsequencelengths.
Figure7: AveragetrainingthroughputofLlama3-8B,Granite-code-base-8BandLlama3-70Bwith
differentbatchsizesandsequencelengths. bsisthebatchsize. seqisthesequencelength. Misthe
overallpeakmemoryconsumptionoftheLLMtrainingononeGPUw.r.t. theGPUmemorycapacity.
"×"meanstheframeworkfailedtotrainthismodelduetoout-of-memoryerrors.
Trainingthroughput. AsshowninFigure7, whentrainingLlama3-8BandGranite-8B,ZeRO-
Offloadachieves65.9%and65.5%oftheidealperformance,respectively. ThoughZeRO-Infinity
takes extra time to migrate tensors further from CPU memory to SSDs, its training throughput
is slightly lowerthan ZeRO-Offload. Such a subtle performance differencecomes from the high
aggregatebandwidthof8SSDsandtherelativelysmallsizesofoptimizersandparametersoffloaded
toSSDs. ForLlama-70B,ZeRO-Offloadfailsbecausethehostmemorycapacityistoosmalltostore
offloadedtensorsofsuchalargemodel. SinceSSDsofferlargercapacity,ZeRO-Infinitycanstilltrain
Llama3-70B.However,itonlyachieves43.0%oftheidealperformance,becauseitscoarse-grained
offloadingschemecannotefficientlyutilizethelimitedSSDbandwidthtomigratelargertensors.
Teraio outperforms the ZeRO series by up to 1.59×. For Llama3-8B, both Teraio-Mixed and
Teraio-SSDcanachievenear-idealperformance,demonstratingtheeffectivenessofourlifetime-aware
tensormigrationalgorithminchoosingthemostbeneficialtensortomigrate. Moreover,wefindthat
eventhough2H100GPUscanprovidesufficientGPUmemorytotrainLlama3-8Bwithoutmemory
expansion,Teraioallowsustoincreasethe(micro-)batchsize,improvingthethroughputby9%. For
8

Granite,Teraio-SSDachievessimilarperformancetotheZeROseries,whileTeraio-Mixedcanstill
delivernear-idealperformancebyutilizingCPUmemory. Theresultshowsthatasthemodelsize
increases,achievingnear-idealperformancerequiresnotonlyourlifetime-awaretensormigration
algorithm,butalsomigrationbandwidthhigherthanwhat4SSDscanprovide. ForLlama-70B,since
itsmemoryrequirementsignificantlyexceedsGPUmemorycapacity,highermigrationbandwidthis
needed. EvenTeraio-Mixedcanonlyachieve59.7%oftheidealperformance. Nonetheless,itstill
outperformsZeRO-Infinityby1.33×.
Impactofvaryingbatchsizeandsequencelength. Asbatchsizeandsequencelengthvary,the
trainingthroughputofTeraio-Mixedisalwaystheclosesttotheidealthroughputamongalloffloading
frameworks,whileTeraio-SSDdeliverssimilarorbetterperformancethantheZeROseries. Forthe
samemodel,increasingthebatchsizedoesn’traisememoryrequirements,sinceeachbatchissplit
intomicro-batchesthatcontainthesamenumberoftrainingsamples. However,whenthesequence
lengthincreases,thememoryrequirementalsoincreases. Therefore,whenthesequencelengthis
longerthan3,072,ZeRO-InfinityfailstotrainthemodelsincetheGPUmemorycapacityissmaller
than the activation tensors of the model. In contrast, Teraio can train all model configurations
becauseitcanoffloadanyinactivetensortosavememory.
 htdiwdnaB noitargiM
|                  | Eviction from GPU |     | Fetching to GPU |     | Eviction from GPU |     | Fetching to GPU |     |
| ---------------- | ----------------- | --- | --------------- | --- | ----------------- | --- | --------------- | --- |
| )s/BG( egasU  30 |                   |     |                 | 30  |                   |     |                 |     |
| 20               |                   |     |                 | 20  |                   |     |                 |     |
|   10             |                   |     |                 |     |                   |     |                 |     |
10
| 0   |     |     |     | 0   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
0 10000 20000 30000 40000 50000 60000 0 10000 20000 30000 40000 50000 60000
|     | GPU Kernel Index in one training iteration |     |     |     | GPU Kernel Index in one training iteration |                 |     |     |
| --- | ------------------------------------------ | --- | --- | --- | ------------------------------------------ | --------------- | --- | --- |
|     |  (a) Granite-code-base-8B                  |     |     |     |                                            |  (b) Llama3-70B |     |     |
Figure8: TheaveragemigrationbandwidthutilizationwhentrainingtheGranite-code-base-8Bmodel
andtheLlama3-70BmodelinTeraio-Mixed.
Migrationbandwidthutilization. TofurtherunderstandwhyTeraioachievesgoodperformance,
westudyitsmigrationbandwidthutilization. Figure8showsthatTeraiomaintainshighutilization
ofbidirectionalmigrationbandwidth,thankstoourI/O-awaremigrationalgorithm.
4.3 TrainingCost
Toevaluatethecost Table2: CostofeachdeviceusedbyTeraioandotherbaselinesforLlama3-
of Teraio, wesum- 70Btraining. PricesarequotedfromExxact[5]. ThePureGPUssetupcontains
| marize the | prices |     |     |     |     |     |     |     |
| ---------- | ------ | --- | --- | --- | --- | --- | --- | --- |
theminimumnumberof8-GPUH100serverscapablefortrainingLlama3-70B
| of different | devices |     |     |     |     |     |     |     |
| ------------ | ------- | --- | --- | --- | --- | --- | --- | --- |
withoutoffloadingtensorstohostmemoryorSSDs.
| used in each | base- |     |     |     |     |     |     |     |
| ------------ | ----- | --- | --- | --- | --- | --- | --- | --- |
linesetupinTable2. Server(with2H100GPUs) Server(with2H100GPUs) 2×Server(with8H100GPUs) 8×Samsung990PRO
|                  |           |               | with128GBmemory | with1TBmemory |     | with128GBmemory |     | SSD2TB   |
| ---------------- | --------- | ------------- | --------------- | ------------- | --- | --------------- | --- | -------- |
| Teraio-SSD       | needs     | Cost($)       | 84,139.9        | 91,047.9      |     | 499,591.4       |     | 1,360    |
| a server         | with only | TeraIO-SSD    | (cid:33)        |               |     |                 |     | (cid:33) |
|                  |           | TeraIO-Mixed  |                 | (cid:33)      |     |                 |     | (cid:33) |
| 128GBofCPUmem-   |           | ZeRO-Offload  |                 | (cid:33)      |     |                 |     |          |
| oryand8SSDssince |           | ZeRO-Infinity |                 | (cid:33)      |     |                 |     | (cid:33) |
|                  |           | PureGPUs      |                 |               |     | (cid:33)        |     |          |
| it migrates      | tensors   |               |                 |               |     |                 |     |          |
only to SSDs, while Teraio-Mixed uses both SSDs and 1TB CPU memory for more efficient
tensormigration. SinceZeRO-OffloadandZeRO-InfinityconsumealargeamountofCPUmemory
to train LLMs, they both need a server with 1TB of memory. ZeRO-Infinity additionally uses 8
SSDsinourevaluation. WealsocomparewiththePureGPUsetup,inwhichalltensorsarekept
withinGPUmemory. ToprovideenoughGPUmemorytotrainLlama3-70Binthissetup,weneedto
pay$499,591.40fortwoservers,eachequippedwith8H100GPUs. Incomparison,Teraio-SSD
and Teraio-Mixed save costs by 5.88× and 5.41×, respectively. Compared to ZeRO-Offload
and ZeRO-Infinity, since we have similar machine setups, Teraio’s 1.47× training performance
improvementtranslatesinto1.45×and1.47×improvedcostefficiency,respectively.
4.4 ImpactofVaryingNumberofSSDsandCPUMemoryCapacity
Figure 9 shows the training throughput of Teraio as we vary the available CPU memory ca-
pacity and the number of SSDs used for each GPU. The performance of Teraio scales fa-
vorably as we increase the number of SSDs or the CPU memory capacity. For Llama-8B,
Teraio achieves near ideal performance with only 2 SSDs and 64 GB of CPU memory. Even
for Llama-70B, we observe that using only 2 SSDs and 512GB of CPU memory can still
achieve 73.1% of the training throughput obtained with 4 SSDs and 1,024GB of CPU memory.
9

| These results | validate                 | our LLM | charac- |                      |     |     |     |     |
| ------------- | ------------------------ | ------- | ------- | -------------------- | --- | --- | --- | --- |
|               |                          |         |         |  tuphguorhT gniniarT |     | 120 |     |     |
| terization    | study’s key observation: |         | with    | 1800                 |     | 100 |     |     |
1500
| lifetime-aware | tensor offloading, |     | we can | )s/nekot( |     | 80  |     |     |
| -------------- | ------------------ | --- | ------ | --------- | --- | --- | --- | --- |
1200
| achievegoodperformanceevenwithlim- |     |     |     |     |                 | 60  |                 |     |
| ---------------------------------- | --- | --- | --- | --- | --------------- | --- | --------------- | --- |
|                                    |     |     |     | 900 | 2 SSDs (TeraIO) |     | 2 SSDs (TeraIO) |     |
itedhardwareresources. 600 3 SSDs (TeraIO) 40 3 SSDs (TeraIO)
|     |     |     |     |     | 4 SSDs (TeraIO) |     | 4 SSDs (TeraIO) |     |
| --- | --- | --- | --- | --- | --------------- | --- | --------------- | --- |
|     |     |     |     | 300 |                 | 20  |                 |     |
ComparedtoZeRO-Infinity,Teraiosignif- ZeRO-Infinity ZeRO-Infinity
|     |     |     |     | 0    |        | 0      |     |      |
| --- | --- | --- | --- | ---- | ------ | ------ | --- | ---- |
|     |     |     |     | 1632 | 64 128 | 128256 | 512 | 1024 |
icantlyreducestheCPUmemorycapacity Available CPU Memory Capacity (GB) Available CPU Memory Capacity (GB)
|     |     |     |     |     | (a) Llama3-8B |     | (b) Llama3-70B |     |
| --- | --- | --- | --- | --- | ------------- | --- | -------------- | --- |
requirementwhileachievingbetterperfor-
|     |     |     |     | Figure 9: Training | throughput | as  | we vary | the CPU |
| --- | --- | --- | --- | ------------------ | ---------- | --- | ------- | ------- |
mance. ZeRO-Infinityrequires170GBand
memorycapacityandthenumberofSSDsperGPU.
770GBofCPUmemorytotrainLlama-8B
andLlama-70B,respectively,asithastooffloadgradientsandoptimizersintoCPU.Incomparison,
Teraio achieves better performance even with more limited hardware resources, as it efficiently
utilizesboththelargecapacityofSSDsandextrabandwidthofCPUmemory.
5 Conclusion
WepresentTeraio,alifetime-awaretensoroffloadingframeworkthatcanaccuratelyplanandexecute
fine-grained tensor offloading and prefetching instructions for LLM training. With predictable
tensoractivitypatterns,TeraiobestutilizespreciousGPUmemoryforacceleratingGPUtraining
process,whileleveraginglarge-capacitySSDsforloweringtrainingcost. Comparedtoexistingtensor
offloadingwork,Teraioprovidesamorepracticalandcost-efficientsolutionforLLMtraining.
References
[1] JonghyunBae,JongsungLee,YunhoJin,SamSon,ShineKim,HakbeomJang,TaeJunHam,
andJaeWLee. {FlashNeuron}:{SSD-Enabled}{Large-Batch}trainingofverydeepneural
networks. In19thUSENIXConferenceonFileandStorageTechnologies(FAST21), pages
387–401,2021.
[2] Olivier Beaumont, Lionel Eyraud-Dubois, and Alena Shilova. Efficient combination of
rematerializationandoffloadingfortrainingdnns. AdvancesinNeuralInformationProcessing
Systems,34:23844–23857,2021.
[3] JacobDevlin,Ming-WeiChang,KentonLee,andKristinaToutanova. Bert: Pre-trainingofdeep
bidirectionaltransformersforlanguageunderstanding. arXivpreprintarXiv:1810.04805,2018.
[4] Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle,
AieshaLetman,AkhilMathur,AlanSchelten,AmyYang,AngelaFan,etal. Thellama3herd
| ofmodels.   | arXivpreprintarXiv:2407.21783,2024.                  |                                   |     |     |     |     |     |     |
| ----------- | ---------------------------------------------------- | --------------------------------- | --- | --- | --- | --- | --- | --- |
| [5] EXXACT. | Exxact.                                              | https://www.exxactcorp.com/,2025. |     |     |     |     |     |     |
| [6] Google. | T511b. https://huggingface.co/google-t5/t5-11b,2025. |                                   |     |     |     |     |     |     |
[7] GPUDirectStorage: ADirectPathBetweenStorageandGPUMemory. https://developer.
nvidia.com/blog/gpudirect-storage/.
[8] Chien-ChinHuang,GuJin,andJinyangLi.Swapadvisor: Pushingdeeplearningbeyondthegpu
memorylimitviasmartswapping. InProceedingsoftheTwenty-FifthInternationalConference
onArchitecturalSupportforProgrammingLanguagesandOperatingSystems,pages1341–1355,
2020.
[9] Yanping Huang, Youlong Cheng, Ankur Bapna, Orhan Firat, Dehao Chen, Mia Chen, Hy-
oukJoongLee,JiquanNgiam,QuocVLe,YonghuiWu,etal. Gpipe: Efficienttrainingofgiant
neuralnetworksusingpipelineparallelism. Advancesinneuralinformationprocessingsystems,
32,2019.
| [10] IBM. | Ibmgranite. | https://huggingface.co/ibm-granite,2025. |     |     |     |     |     |     |
| --------- | ----------- | ---------------------------------------- | --- | --- | --- | --- | --- | --- |
[11] ParasJain,AjayJain,AniruddhaNrusimha,AmirGholami,PieterAbbeel,JosephGonzalez,
Kurt Keutzer, and Ion Stoica. Checkmate: Breaking the memory wall with optimal tensor
| rematerialization. |     | ProceedingsofMachineLearningandSystems,2:497–511,2020. |     |     |     |     |     |     |
| ------------------ | --- | ------------------------------------------------------ | --- | --- | --- | --- | --- | --- |
10

[12] HongsunJang, JaeyongSong, JaewonJung, JaeyoungPark, YoungsokKim, andJinhoLee.
Smart-infinity: Fastlargelanguagemodeltrainingusingnear-storageprocessingonarealsystem.
In2024IEEEInternationalSymposiumonHigh-PerformanceComputerArchitecture(HPCA),
pages345–360.IEEE,2024.
[13] JaehoonJung,JinpyoKim,andJaejinLee.Deepum: Tensormigrationandprefetchinginunified
memory. InProceedingsofthe28thACMInternationalConferenceonArchitecturalSupport
forProgrammingLanguagesandOperatingSystems,Volume2,pages207–221,2023.
[14] JaredKaplan,SamMcCandlish,TomHenighan,TomBBrown,BenjaminChess,RewonChild,
ScottGray,AlecRadford,JeffreyWu,andDarioAmodei. Scalinglawsforneurallanguage
models. arXivpreprintarXiv:2001.08361,2020.
[15] Youngeun Kwon and Minsoo Rhu. Beyond the memory wall: A case for memory-centric
hpcsystemfordeeplearning. In201851stAnnualIEEE/ACMInternationalSymposiumon
Microarchitecture(MICRO),pages148–161.IEEE,2018.
[16] Tung D Le, Haruki Imai, Yasushi Negishi, and Kiyokuni Kawachiya. Tflms: Large model
supportintensorflowbygraphrewriting. arXivpreprintarXiv:1807.02037,2018.
[17] WanchaoLiang,TianyuLiu,LessWright,WillConstable,AndrewGu,Chien-ChinHuang,
IrisZhang,WeiFeng,HowardHuang,JunjieWang,etal. Torchtitan: One-stoppytorchnative
solutionforproductionreadyllmpre-training. arXivpreprintarXiv:2410.06511,2024.
[18] ChangyueLiao,MoSun,ZihanYang,KaiqiChen,BinhangYuan,FeiWu,andZekeWang.
Adding nvme ssds to enable and accelerate 100b model fine-tuning on a single gpu. arXiv
preprintarXiv:2403.06504,2024.
[19] SamMcCandlish,JaredKaplan,DarioAmodei,andOpenAIDotaTeam. Anempiricalmodel
oflarge-batchtraining. arXivpreprintarXiv:1812.06162,2018.
[20] PauliusMicikevicius,SharanNarang,JonahAlben,GregoryDiamos,ErichElsen,DavidGarcia,
BorisGinsburg,MichaelHouston,OleksiiKuchaiev,GaneshVenkatesh,etal. Mixedprecision
training. arXivpreprintarXiv:1710.03740,2017.
[21] Deepak Narayanan, Aaron Harlap, Amar Phanishayee, Vivek Seshadri, Nikhil R Devanur,
GregoryRGanger,PhillipBGibbons,andMateiZaharia. Pipedream: Generalizedpipeline
parallelismfordnntraining. InProceedingsofthe27thACMsymposiumonoperatingsystems
principles,pages1–15,2019.
[22] XiaonanNie,YiLiu,FangchengFu,JinbaoXue,DianJiao,XupengMiao,YangyuTao,andBin
Cui. Angel-ptm: Ascalableandeconomicallarge-scalepre-trainingsystemintencent. arXiv
preprintarXiv:2303.02868,2023.
[23] AdamPaszke,SamGross,SoumithChintala,GregoryChanan,EdwardYang,ZacharyDeVito,
ZemingLin,AlbanDesmaison,LucaAntiga,andAdamLerer. Automaticdifferentiationin
pytorch. InNIPS-W,2017.
[24] WilliamPeeblesandSainingXie. Scalablediffusionmodelswithtransformers. InProceedings
oftheIEEE/CVFInternationalConferenceonComputerVision,pages4195–4205,2023.
[25] BharadwajPudipeddi,MaralMesmakhosroshahi,JinwenXi,andSujeethBharadwaj. Training
largeneuralnetworkswithconstantmemoryusinganewexecutionalgorithm. arXivpreprint
arXiv:2002.05645,2020.
[26] Zaid Qureshi, Vikram Sharma Mailthody, Isaac Gelado, Seungwon Min, Amna Masood,
JeongminPark,JinjunXiong,C.J.Newburn,DmitriVainbrand,I-HsinChung,MichaelGarland,
WilliamDally,andWen-meiHwu. Gpu-initiatedon-demandhigh-throughputstorageaccess
inthebamsystemarchitecture. InProceedingsofthe28thACMInternationalConferenceon
ArchitecturalSupportforProgrammingLanguagesandOperatingSystems,Volume2,ASPLOS
2023,page325–339,NewYork,NY,USA,2023.AssociationforComputingMachinery.
[27] Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever, et al.
Languagemodelsareunsupervisedmultitasklearners. OpenAIblog,1(8):9,2019.
11

[28] ColinRaffel,NoamShazeer,AdamRoberts,KatherineLee,SharanNarang,MichaelMatena,
YanqiZhou,WeiLi,andPeterJLiu. Exploringthelimitsoftransferlearningwithaunified
text-to-texttransformer. Journalofmachinelearningresearch,21(140):1–67,2020.
[29] SamyamRajbhandari, OlatunjiRuwase, JeffRasley, ShadenSmith, andYuxiongHe. Zero-
infinity: Breakingthegpumemorywallforextremescaledeeplearning. InProceedingsofthe
internationalconferenceforhighperformancecomputing,networking,storageandanalysis,
pages1–14,2021.
[30] JieRen,SamyamRajbhandari,RezaYazdaniAminabadi,OlatunjiRuwase,ShuangyanYang,
MinjiaZhang,DongLi,andYuxiongHe. {Zero-offload}: Democratizing{billion-scale}model
training. In2021USENIXAnnualTechnicalConference(USENIXATC21),pages551–564,
2021.
[31] MinsooRhu, NataliaGimelshein, JasonClemons, ArslanZulfiqar, andStephenWKeckler.
vdnn: Virtualizeddeepneuralnetworksforscalable,memory-efficientneuralnetworkdesign. In
201649thAnnualIEEE/ACMInternationalSymposiumonMicroarchitecture(MICRO),pages
1–13.IEEE,2016.
[32] ManishShetty,YinfangChen,GaganSomashekar,MinghuaMa,YogeshSimmhan,Xuchao
Zhang, Jonathan Mace, Dax Vandevoorde, Pedro Las-Casas, Shachee Mishra Gupta, et al.
Buildingaiagentsforautonomousclouds: Challengesanddesignprinciples. InProceedingsof
the2024ACMSymposiumonCloudComputing,pages99–110,2024.
[33] XiaoyangSun,WeiWang,ShenghaoQiu,RenyuYang,SongfangHuang,JieXu,andZheng
Wang. Stronghold: fastandaffordablebillion-scaledeeplearningmodeltraining. InSC22:
InternationalConferenceforHighPerformanceComputing,Networking,StorageandAnalysis,
pages1–17.IEEE,2022.
[34] LinnanWang,JinmianYe,YiyangZhao,WeiWu,AngLi,ShuaiwenLeonSong,ZenglinXu,
andTimKraska. Superneurons: Dynamicgpumemorymanagementfortrainingdeepneural
networks. InProceedingsofthe23rdACMSIGPLANsymposiumonprinciplesandpracticeof
parallelprogramming,pages41–53,2018.
[35] Duo Wu, Xianda Wang, Yaqi Qiao, Zhi Wang, Junchen Jiang, Shuguang Cui, and Fangxin
Wang. Netllm: Adaptinglargelanguagemodelsfornetworking. InProceedingsoftheACM
SIGCOMM2024Conference,pages661–678,2024.
[36] KunWu,JeongminBrianPark,XiaofanZhang,MertHidayetoğlu,VikramSharmaMailthody,
Sitao Huang, Steven Sam Lumetta, and Wen-mei Hwu. Tba: Faster large language model
trainingusingssd-basedactivationoffloading. arXivpreprintarXiv:2408.10013,2024.
[37] TailingYuan,YuliangLiu,XuchengYe,ShenglongZhang,JianchaoTan,BinChen,Chengru
Song,andDiZhang.Acceleratingthetrainingoflargelanguagemodelsusingefficientactivation
rematerializationandoptimalhybridparallelism.In2024USENIXAnnualTechnicalConference
(USENIXATC24),pages545–561,2024.
[38] JieZhangandMyoungsooJung. Zng: Architectinggpumulti-processorswithnewflashfor
scalabledataanalysis. In2020ACM/IEEE47thAnnualInternationalSymposiumonComputer
Architecture(ISCA),pages1064–1075.IEEE,2020.
[39] JieZhang,MiryeongKwon,HyojongKim,HyesoonKim,andMyoungsooJung. Flashgpu:
Placingnewflashnexttogpucores. InProceedingsofthe56thAnnualDesignAutomation
Conference2019,pages1–6,2019.
12