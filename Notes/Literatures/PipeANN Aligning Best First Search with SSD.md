# PipeANN Aligning Best First Search with SSD

**Source**: PipeANN Aligning Best First Search with SSD.pdf
**Format**: .pdf

---

Achieving Low-Latency Graph-Based Vector Search
via Aligning Best-First Search Algorithm with SSD
Hao Guo and Youyou Lu, Tsinghua University
https://www.usenix.org/conference/osdi25/presentation/guo
This paper is included in the Proceedings of the 19th USENIX Symposium
on Operating Systems Design and Implementation.
July 7–9, 2025 • Boston, MA, USA
ISBN 978-1-939133-47-2
Open access to the Proceedings of the 19th USENIX Symposium
on Operating Systems Design and Implementation is sponsored by

|     |     | Achieving |          | Low-Latency |            |        | Graph-Based |           | Vector | Search | via |     |
| --- | --- | --------- | -------- | ----------- | ---------- | ------ | ----------- | --------- | ------ | ------ | --- | --- |
|     |     |           | Aligning |             | Best-First |        | Search      | Algorithm | with   | SSD    |     |     |
|     |     |           |          |             |            | HaoGuo |             | YouyouLu∗ |        |        |     |     |
TsinghuaUniversity
Abstract
|                                                  |     |     |     |     |     |     |     | Vamana (In-Memory) |     | DiskANN (On-Disk) |          | PipeANN |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | ----------------- | -------- | ------- |
|                                                  |     |     |     |     |     |     |     | (a) SIFT           |     |                   | (b) DEEP |         |
| WeproposePipeANN,anon-diskgraph-basedapproximate |     |     |     |     |     |     |     | 01@01llaceR 1.0    |     |                   |          |         |
nearestneighborsearch(ANNS)system,whichsignificantly
0.9
bridgesthelatencygapwithin-memoryones.Weachievethis
0.8
byaligningthebest-firstsearchalgorithmwithSSDcharacter-
| istics,avoidingstrictcompute-I/Oorderacrosssearchsteps. |     |     |     |     |     |     |     | 0.7 |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Experiments show that PipeANN has 1.14×–2.02× search 0 1 2 3 4 0 2 4
latencycomparedtoin-memoryVamana,and35.0%ofthe Search Latency (ms)
latencyofon-diskDiskANNinbillion-scaledatasets,without
sacrificingsearchaccuracy.
|     |     |     |     |     |     |     |     | Figure1: | Latencygapbetweenin-memory(Vamana[23])and |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ----------------------------------------- | --- | --- | --- |
on-disk(DiskANN[23])graph-basedindexesintwodatasets.
Oursystem(PipeANN)significantlybridgesthegap.
1 Introduction
| High-dimensional |     | vectors | with | tens orhundreds |     | of  | dimen- |     |     |     |     |     |
| ---------------- | --- | ------- | ---- | --------------- | --- | --- | ------ | --- | --- | --- | --- | --- |
best-firstsearchalgorithmtoexplorevectorsinthegraph—
sionsarepowerfuldatarepresentations[17,19].Vectorsearch,
|                |     |         |         |         |           |     |         | in eachsearchstep,itexplores |     |     | the bestneighbors | (i.e.,the |
| -------------- | --- | ------- | ------- | ------- | --------- | --- | ------- | ---------------------------- | --- | --- | ----------------- | --------- |
| which searches | a   | dataset | for the | closest | neighbors |     | given a |                              |     |     |                   |           |
nearestones)ofalltheexploredvectors,toreducethenumber
| target vector, | is used | in  | various | scenarios | such | as  | recom- |     |     |     |     |     |
| -------------- | ------- | --- | ------- | --------- | ---- | --- | ------ | --- | --- | --- | --- | --- |
ofaccessedvectorspersearch.However,twoissuesprevent
| mendation | [14,15,27] | and | retrieval | augmented |     | generation |     |     |     |     |     |     |
| --------- | ---------- | --- | --------- | --------- | --- | ---------- | --- | --- | --- | --- | --- | --- |
itfromachievinglowlatencyondisk.First,thebest-firstal-
(RAG)[12].Itisnotefficienttodoaccuratevectorsearches
gorithmincursorderedcomputeandI/Oacrosssearchsteps.
| for high-dimensional |     | vectors | [9], | so  | approximate |     | nearest |     |     |     |     |     |
| -------------------- | --- | ------- | ---- | --- | ----------- | --- | ------- | --- | --- | --- | --- | --- |
Itharmssearchlatencybecauseofthelong(e.g.,7.43×than
neighborsearch(ANNS)ispreferred,whichreturnsanap-
computelatency,§2.2)butwastedI/Olatencywhichfailsto
proximatedsetofknearestneighbors(i.e.,top-k).Amongall
overlapwithcompute.Second,thebest-firstalgorithmforces
typesofANNSindexes,graph-basedindexes[6,16],where
synchronousI/Oineachsearchstep,whereitbatch-readsthe
vectorsareorganizedasadirectedgraph,arefavoredfortheir
nearestneighborssynchronously.Itinducesanunderutilized
lowsearchlatencyunderhighaccuracy.
I/Opipeline(e.g.,76%utilized,§2.2)whenwaitingforslow
Tosupportlarge-scaledatasets(e.g.,billionsofvectors[6,
readsinthebatch.
14,21,27]),anincreasingnumberoforganizations[4,21,33]
Inthispaper,weseektoalignthesearchalgorithmwith
prefersolid-statedrives(SSDs)forstoringANNSindexes,
SSDI/Ocharacteristics.Wefindthisideafeasiblewithout
cost-efficiency.
due to their However,graph-based indexes affectingsearchconvergence,byobservingthatthebest-first
failtomaintainlowsearchlatencyondiskasinmemory.As
|          |              |                |     |     |     |               |     | algorithmisnotamust:Unlikescalarindexes(e.g.,B |     |     |     | + -tree) |
| -------- | ------------ | -------------- | --- | --- | --- | ------------- | --- | ---------------------------------------------- | --- | --- | --- | -------- |
| shown in | Figure 1,the | on-diskDiskANN |     |     | has | significantly |     |                                                |     |     |     |          |
whereobjectshaveonesearchpath,graph-basedANNSin-
highersearchlatencythanthein-memoryVamana(e.g.,4.18×
dexeshavemultiplesearchpathsforeachvector,considering
for0.9recalland3.14×for0.99recall).
itsmultiplein-edges.Thebest-firstalgorithmonlyestimates
Byanalysis,wefindthehighlatencyiscausedbythein-
oneshortsearchpath,nottheuniqueone.Thus,atweaked
trinsicmismatchbetweengraph-basedANNSalgorithmsand
searchalgorithmcanexploitotherpathsforconvergence.
theI/OcharacteristicsofSSDs,namelylongI/Olatencyand
PipeSearch,an
asynchronous,parallelI/O: We propose on-disk graph-based ANNS
Graph-basedANNSfollowthe
algorithmthatachieveslowlatencybyaligningthebest-first
∗YouyouLuisthecorrespondingauthor(luyouyou@tsinghua.edu.cn). searchalgorithmwithSSDI/Ocharacteristics.Thekeyob-
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    171

servation for such alignment is the pseudo-dependency of ANNSindexesondisk,PipeANNshowsatleast70.6%lower
computeandI/Oinbest-firstsearch:Ineachsearchstep,the latencyand1.35×higherthroughputfor0.9recall.Inbillion-
neighborstobereadcanbedecidedbyonlythein-memory scaledatasets,PipeANNhas35.0%latencyand1.71×higher
candidatepoolcontainingtheneighborIDs,withoutwaiting throughputcomparedtoDiskANN[23].
forongoingI/Oorcompute(i.e.,neighborexploration)tofin- WhileprimarilydesignedforSSDs,PipeANN’stechniques
ish.Thus,PipeSearchavoidsstrictcompute-I/Oorderacross
couldalsobeadoptedtootherstoragemedia,suchasremote
searchsteps:WhentheI/Opipelineisnotfull,PipeSearchfills memory.ThesestoragemediaexhibitsimilarI/Ocharacteris-
itbyasynchronouslyreadingthecurrentnearestneighborsin ticsasSSDs,namelyµs-scaleI/OlatencyandparallelI/O,so
thecandidatepool,regardlessofongoingI/Oorunfinished
ANNSindexesstoredonthesemedia[5]couldimprovetheir
compute.OverlappedwithI/O,PipeSearchexploresthepre- performancebyadoptingPipeANN.
readneighborsinabest-effortmanner. PipeANN has its limitations. Despite the techniques for
PipeSearchbringssignificantperformancebenefits.Onthe throughput,PipeANN’s speculative I/O still leads to lower
onehand,computeandI/Oareoverlapped,whichaccelerates search throughput than the greedy I/O in best-first search.
ANNSastheyshowclose(thesameorderofmagnitude)la- However,webelievePipeANN’slatency-throughputtradeoff
tency.Ontheotherhand,theI/Opipelineisbetterutilized.Ex-
isworthwhileinapplicationswithms-scalelatencybudgets
perimentsdemonstratethelowlatencyofPipeSearch,which
(e.g.,large-scalesearchandrecommendation[6,21]),where
has∼50%latencycomparedtobest-firstsearch. PipeANNcouldbenefitfromlowersearchlatencyorhigher
PipeSearchachieveslowlatencybutatthecostofthrough- searchaccuracywiththesamelatency.
put. There are two challenges to increasing its throughput. Insummary,thispapermakesthefollowingcontributions:
The first is how to dynamically adjust to suitable pipeline
• Wefindthebest-firstsearchalgorithmrestrictsthedesign
widthsduringasinglesearch,inordertoleveragethehigh
spaceinexploitingSSDcharacteristics,inducinghighla-
throughputofnarrowpipelinesandthelowlatencyofwide
tencyforon-diskgraph-basedANNS(§2).
ones simultaneously. The second is howto avoidthe accu-
mulationofread-but-unexploredneighborvectorscausedby
• WedesignPipeSearch,alow-latencygraph-basedANNS
widepipelineandslowneighborexploration,whichinduces algorithm on disk by aligning the best-first search algo-
sub-optimalI/Odecisionsandreducedsearchthroughput. rithmwithSSD(§3).
Tothisend,weimplementPipeANN,alow-latencyANNS • WeimplementPipeANN,alow-latencyANNSsystemwith
systemwithhighsearchthroughput. PipeANNtacklesthe highsearchthroughput. PipeANNincreasesthethrough-
twochallengesinPipeSearchwithtwotechniques: putofPipeSearchbydynamicpipelineandalgorithmopti-
First,wedynamicallyincreasetheI/Opipelinewidthdur- mization(§4).
ingthesearch,insteadofkeepingastaticpipelinewidth,to • WeevaluatePipeANNtodemonstrateitsefficacyinachiev-
benefitfromhighthroughputandlowlatencysimultaneously. inglow-latencyandhigh-throughputANNSondisk(§5).
Thethroughputdropinlargepipelinewidthsmainlyarises
fromI/Owaste,whichmakesiteasiertosaturateSSDIOPS
becauseofmoreI/Opersearch.However,wefindthatI/O
2 BackgroundandMotivation
wastedecreasesasthesearchprogresses.Thisisduetothe
growing numberofunexploredtop-k neighbors during the
Inthissection,wefirstprovideaprimerforon-diskgraph-
search.Inlatersearchsteps,thecandidatepoolcontainsmore
basedANNS.Then,wecharacterizethebest-firstsearchal-
unexploredtop-kneighbors,whichallowsawiderI/Opipeline
gorithmtoshowitsmismatchwithSSDcharacteristics.
withlittleI/Owaste.
Second, we ensure an upper bound for the number of
missedneighbors(i.e.,ongoingI/Oandread-but-unexplored
2.1 Graph-BasedANNSandBest-FirstSearch
neighbors)whendecidingoneachI/O,insteadofensuring
afullI/Opipelineatalltimes,toavoidneighboraccumula- The k-nearest neighbor search problem aims to find the k
tion.Specifically,whenmultipleI/Osfinishsimultaneously, nearestvectorsofthetargetvectorinadataset.However,ac-
we repeatedly explore one neighbor and issue one I/O,in- curatesearchischallenginginhigh-dimensionalvectorspaces
steadofissuingmultipleI/Ostofillupthepipeline.Thus,we (e.g.,hundredsofdimensions),whichisknownasthecurseof
strikeabalancebetweenafullI/Opipeline(PipeSearch)and dimensionality[9].Totacklethischallenge,approximatenear-
reducedI/Owaste(best-firstsearch),increasingthroughput estneighborsearch(ANNS)algorithmsareproposed.Given
whilesacrificinglittlelatency. thetargetvector,ANNSfindsanapproximatesetofitstop-k
WeevaluatePipeANNtoshowitsefficiencyinlow-latency nearest vectors. Of all the ANNS algorithms,graph-based
ANNS.AsshowninFigure1,PipeANNsignificantlybridges ones[6,16,23]showpromisingperformanceandaccuracy.
thelatencygapbetweenin-memoryandon-diskANNS,espe- They organize the vectors as a directed graph, and vector
ciallyforhighrecall(≥0.9).Comparedwithstate-of-the-art searchisconductedbygraphtraversal.
172 19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|     |     |      |        |        |        |              | Compute |     | I/O |               |     |     |     |
| --- | --- | ---- | ------ | ------ | ------ | ------------ | ------- | --- | --- | ------------- | --- | --- | --- |
| 1   |     | Disk | Page 0 | Page 1 | Page 2 |              | 3       |     |     |               |     |     |     |
|     | 7   |      |        |        |        | )sm( ycnetaL |         |     |     | (a)           | 100 |     | (b) |
| 3   |     |      |        |        |        |              |         |     |     | )%( .litU O/I |     |     |     |
76%
2
| 0   | 6   | Record 0 | Record 1 |     | Record 2 |     |     |     |     |     |     |     | 58% |
| --- | --- | -------- | -------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
50
5
| 2   |     |     |          |     |         |     | 1   |     |     |     |     |     |     |
| --- | --- | --- | -------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     | vector V |     | 1 2 3 5 |     |     |     |     |     |     |     |     |
0
4
|     |     |     |     |     | neighbors |     | 0   |     |      |     | 0   |     |         |
| --- | --- | --- | --- | --- | --------- | --- | --- | --- | ---- | --- | --- | --- | ------- |
|     |     |     |     |     |           |     | 1   | 2 4 | 8 16 | 32  | 1   | 2 4 | 8 16 32 |
I/O Pipeline Width (W)
| Figure2: | Indexlayoutofon-diskgraph-basedANNS. |     |     |     |     |        |     |            |         |            |     |     |              |
| -------- | ------------------------------------ | --- | --- | --- | --- | ------ | --- | ---------- | ------- | ---------- | --- | --- | ------------ |
|          |                                      |     |     |     |     | Figure | 3:  | (a) Search | latency | breakdown. |     | (b) | I/O pipeline |
Algorithm1Best-firstsearch utilizationrate(average#ongoingI/O÷I/Opipelinewidth).
1: G←graph,q←queryvector,W←I/Opipelinewidth
procedureBestFirstSearch(G,q,W)
2:
|     |     |     |     |     |     | withoutdiskreads.Ineachsearchstep,onlyW |     |     |     |     |     |     | diskreadsare |
| --- | --- | --- | --- | --- | --- | --------------------------------------- | --- | --- | --- | --- | --- | --- | ------------ |
3: s←startingvector,L←candidatepoollength
conducted.Inthispaper,best-firstsearcheswithW=1and
candidatepoolP←{<s>},exploredpoolE←∅
4:
| whileP⊊Edo |     |     |     |     |     | W>1arealsocalledgreedysearchandbeamsearch. |     |     |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
5:
|     |         |                             |     |     |     | Low-latencyANNS. |     |     | AchievinglowlatencyANNSisben- |     |     |     |     |
| --- | ------- | --------------------------- | --- | --- | --- | ---------------- | --- | --- | ----------------------------- | --- | --- | --- | --- |
| 6:  | V←top-W | nearestvectorstoqinP,notinE |     |     |     |                  |     |     |                               |     |     |     |     |
ReadV frommemoryordisk eficialforreal-worldapplications.First,real-worldsystems
7:
havestrictlatencydemands.Inlarge-scalesearchorrecom-
| 8:  | E.insert(V) |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
fornbrinV.neighborsdo mendationsystems[6,21],billion-scale,orevenlarger,vector
9:
P.insert(<nbr,Distance(nbr,q)>) searches should complete within ∼10ms to meet response
10:
|     |        |     |     |     |     | time | requirements. |     | Second, | for | ANNS | systems, | a longer |
| --- | ------ | --- | --- | --- | --- | ---- | ------------- | --- | ------- | --- | ---- | -------- | -------- |
| 11: | endfor |     |     |     |     |      |               |     |         |     |      |          |          |
P←lnearestvectorstoqinP searchtimeallowsexploringmorevectors,thusleadingto
12:
|     |     |     |     |     |     | higher | search | accuracy. |     | Therefore, | if  | we could | reduce the |
| --- | --- | --- | --- | --- | --- | ------ | ------ | --------- | --- | ---------- | --- | -------- | ---------- |
13: endwhile
returnknearestvectorstoqinE searchlatencyatthesameaccuracy,wecouldsimultaneously
14:
increasesearchaccuracywithinthesamelatencydemands.
15: endprocedure
2.2 Best-FirstSearchMismatcheswithSSD
| Graphlayout. | Tosupportbillion-scalevectorsearch[6,21], |     |     |     |     |             |     |      |       |     |         |           |         |
| ------------ | ----------------------------------------- | --- | --- | --- | --- | ----------- | --- | ---- | ----- | --- | ------- | --------- | ------- |
|              |                                           |     |     |     |     | Graph-based |     | ANNS | shows | low | latency | in memory | [6,16], |
existingsystems[23,25]storethegraphindexondiskanddo
butfailstomaintainsuchlatencyondisk.Weconductexper-
on-diskgraph-basedANNS.AsshowninFigure2,thegraph
|     |     |     |     |     |     | iments | to  | demonstrate | this | issue. | We do | best-firstsearches |     |
| --- | --- | --- | --- | --- | --- | ------ | --- | ----------- | ---- | ------ | ----- | ------------------ | --- |
isstoredondiskasmultiplerecords.Eachrecordconsistsof
withdifferentWs,usingagraphindexbuilton100million
avectorandallitsneighborIDs.
vectorsintheSIFTdataset[10].Thetargetrecallis90%,as
| Best-firstsearchalgorithm. |     |     | Existinggraph-basedvector |     |     |     |     |     |     |     |     |     |     |
| -------------------------- | --- | --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
recommendedbytheBigANNbenchmark[20].
searchsystems,eitherinmemory[6,16]orondisk[23,25],
AsshowninFigure1(a),thesearchlatencyondiskis4.18×
takeabest-firstsearchalgorithmforgraphtraversal[1,26]
comparedtothatinmemory.Byanalysis,wefindthecause
| As shown | in Algorithm |     | 1, best-first | search | maintains a |     |     |     |     |     |     |     |     |
| -------- | ------------ | --- | ------------- | ------ | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
oflonglatencyisthatbest-firstsearchalgorithmmismatches
candidatepoolwithafixedcandidatepoollength(denotedas withSSDI/Ocharacteristics.
Specifically,wefocusonthe
Linthispaper),containingcurrenttop-Lnearestvectors.
|     |     |     |     |     | The | followingtwoSSDI/Ocharacteristics: |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- |
searchstartswithafixedstartingvectorandcontainsmultiple
• LongI/Olatency.Microsecondortensofmicroseconds
searchsteps.Eachstepexploresthetop-Wnearestunexplored
latencies,commontoflash-basedSSDs.
vectorsinthecandidatepool,byreadingtheminabatchand
• Asynchronous,parallelI/O.Theabilitytohandlemulti-
insertingtheirneighborsintothecandidatepool.Thesearch
terminates when all the vectors in the candidate pool are ple(e.g.,32)in-flightreadrequestsinparallel.
|     |     | torepresentI/Opipelinewidth(i.e.,the |     |     |     | Wefindtwoissuesasfollows. |     |     |     |     |     |     |     |
| --- | --- | ------------------------------------ | --- | --- | --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- |
explored.WeuseW
maximumnumberofparallelI/Orequests)inthispaper.This Issue 1: Ordered compute and I/O across search steps.
definitionequalsthebeamwidthinbest-firstsearch[23]. Thebest-firstsearchalgorithmnaturallycausesdatadepen-
Forin-memoryindexes[6,16],readingthevectors(line7) dency,inducingorderedcomputeandI/O.Ineachsearchstep,
takesashorttime,sotheyuseW=1toreducethewasteof thebest-firstsearchbatchreadsandexplorestheW nearest
computeandI/O.However,SSDhashighI/Olatency,soit
unexploredneighborstothetargetvector.Therefore,thecur-
takesmoretimetoreadavectorthanexploreitforon-disk rentI/Obatchdependsontheprevioussearchstep,namely
thepreviouscomputeandthepreviousI/Obatch.
| indexes [23,25]. | Therefore, |     | they use | W >1 | to utilize the |     |     |     |     |     |     |     |     |
| ---------------- | ---------- | --- | -------- | ---- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
SSDI/Opipeline.Also,theyusePQ-compressedvectorsin SuchorderedcomputeandI/Oshowlittleoverheadinmem-
memory to calculate the distance with neighbors (line 10), orybutharmtheANNSlatencyondisk.Thisisbecause,when
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    173

conductingANNSinmemory,thememoryaccesslatencyis 1 Compute 1 Disk I/O
ordersofmagnitudelowerthancompute,whichistypically
(a) Best-First Search (W = 4)
disk,I/O
executed serially in a search thread. When on la- 1 2 3 4 Under-utilized5 6
tencyishigherthancompute,whichshiftsthebottleneckto I/O pipeline
|     |     |     |     |     |     |     | 1   |     |     |     | 5   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
I/O.Figure3(a)demonstratesthisissuebybreakingdownthe Ordered …
|     |     |     |     |     |     |     | 2   |     |     |     | 6   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
latency.WhenW=1(i.e.,greedysearch),computelatencyis
|                                                 |     |     |     |     |     |     |     | 3   |     |     |     | 7   |     |     |
| ----------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only9.5%ofI/Olatency.EvenwhenusingW=8(thelowest |     |     |     |     |     |     |     | 4   |     |     |     | 8   |     |     |
overalllatency)toutilizeI/Oparallelism,computelatencyis
|     |     |     |     |     |     | (b) PipeSearch (W = 4) |     |     |     | Compute-I/O overlapping |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | ----------------------- | --- | --- | --- | --- |
still45.6%ofI/Olatency.Unfortunately,thelongI/Olatency 1 2 3 4 5 6 7 8 910
| iswasted,asitfailstooverlapwithcompute. |     |     |     |     |     |     |     |     |     |     |     | Better-utilized |     |     |
| --------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- |
|                                         |     |     |     |     |     |     | 1   |     | 5   | 7   |     |                 |     | …   |
I/O pipeline
| Issue2:SynchronousI/Oineachsearchstep. |      |               |          |         | Best-first |     |     | 2   | 6   |     | 9   |     |     |     |
| -------------------------------------- | ---- | ------------- | -------- | ------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|                                        |      |               |          |         |            |     |     | 3   |     | 8   |     | 11  |     |     |
| search uses                            | W >1 | to batch-read | multiple | records | in each    |     |     |     |     |     |     |     |     |     |
|                                        |      |               |          |         |            |     |     | 4   |     | 10  |     | 12  |     |     |
searchstep,toutilizeI/Oparallelism.However,itstillrequires
synchronouslywaitingforalltheI/Ostofinish.
SuchsynchronousI/Ocausesanunder-utilizedI/Opipeline. ComparisonofPipeSearchwithbest-firstsearch.
Figure4:
Figure3(b)showstheI/Opipelineutilizationrate(theaverage
numberofongoingI/OsduringI/Otime÷W).DuringI/O
time,thepipelineisonly76%fullforW=8,and58%fullfor I/O in order, unfriendly to SSDs. In contrast, PipeSearch
tweaksthealgorithmtoavoidsuchstrictorder,thusachieving
W =32.ThisisbecausetheI/OlatencyfluctuatesinSSDs.
compute-I/Ooverlappingandabetter-utilizedI/Opipeline.
Best-firstsearchwaitsforawholeI/Obatchtofinish,sothe
Keyobservation:pseudo-dependencyofcomputeandI/O.
latencydependsonthetaillatencyoftheI/Os.Whenwaiting
forsomeslowI/Os,theI/Opipelineisnotfullyutilized. In each search step,the best-first search issues I/O and ex-
ploresthenearestneighborsinorder.However,suchanorder
isnotnecessary:I/Ocanbedecidedonlybythein-memory
3 PipeSearch
|     |     |     |     |     |     | candidate |     | pool, | regardless | of ongoing |     | I/O and | unexplored |     |
| --- | --- | --- | --- | --- | --- | --------- | --- | ----- | ---------- | ---------- | --- | ------- | ---------- | --- |
neighbors.Thus,whenthereareongoingI/O,wecandirectly
Basedontheobservationsabove,weproposePipeSearch,a
|     |     |     |     |     |     | issue | I/O | for the | nearest | unread | neighbor | in  | the candidate |     |
| --- | --- | --- | --- | --- | --- | ----- | --- | ------- | ------- | ------ | -------- | --- | ------------- | --- |
low-latencyANNSalgorithmbyaligningthebest-firstsearch
pool,thereisnoneedtowaitforalltheongoingI/Otofinish
algorithmwithSSDhardware.Inthissection,wefirstshow
(likebest-firstsearch).Neighborexplorationcanbeexecuted
thatthisideaisfeasible.Then,weintroducePipeSearchand
inabest-effortmanner,independentfromdiskI/O.
| analyze | its performance | benefits. | Finally,we | evaluate | itto |                    |     |     |     |                                   |     |     |     |     |
| ------- | --------------- | --------- | ---------- | -------- | ---- | ------------------ | --- | --- | --- | --------------------------------- | --- | --- | --- | --- |
|         |                 |           |            |          |      | Algorithmoverview. |     |     |     | PipeSearchavoidsstrictcompute-I/O |     |     |     |     |
demonstrateitsdilemmainlatencyandthroughput.
orderacrosssearchsteps.Specifically,itmaintainsacandi-
|     |     |     |     |     |     | date | pool | witha | fixed length | L,similarto |     | best-firstsearch. |     |     |
| --- | --- | --- | --- | --- | --- | ---- | ---- | ----- | ------------ | ----------- | --- | ----------------- | --- | --- |
3.1 TweakingBest-FirstSearchisPossible
|     |     |     |     |     |     | Also,it | maintains |     | an I/O | pipeline | Q   | with a | specific | width |
| --- | --- | --- | --- | --- | --- | ------- | --------- | --- | ------ | -------- | --- | ------ | -------- | ----- |
W,containingongoingI/O.Thesearchiterativelyexecutes
Onemaythinkthattweakingthebest-firstsearchalgorithm
thefollowingsteps:IftheI/Opipelineisnotfull,PipeSearch
mayprohibitthesearchfromconvergence.However,wear-
issuesI/Otofillupthepipelinebasedonthecurrentcandidate
guethatthebest-firstalgorithmisnotamustandcanbe
pool.OverlappedwithI/O,itexploresthenearestvectorin
tweakedwithoutaffectingsearchconvergence.
|                                    |              |          |                    |     |             | anunexploredsetU                                    |     |     | andupdatesthecandidatepoolusingits |     |     |     |     |     |
| ---------------------------------- | ------------ | -------- | ------------------ | --- | ----------- | --------------------------------------------------- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --- |
| This                               | is enabledby | multiple | searchpaths        | in  | graph-based |                                                     |     |     |                                    |     |     |     |     |     |
|                                    |              |          | +                  |     |             | neighbors.Then,itpollsforI/Ocompletionandaddsallthe |     |     |                                    |     |     |     |     |     |
| indexes:Unlikescalarindexes(e.g.,B |              |          | -tree)whereeachob- |     |             |                                                     |     |     |                                    |     |     |     |     |     |
vectorsacquiredtotheunexploredsetU.
jecthasonlyonesearchpath,ingraph-basedANNSindexes,
eachvectorcanbefoundinmultiplepathsusingitsmultiple
in-edges.Thebest-firstsearchonlyestimatesashortsearch 3.3 PipeSearchReducesSearchLatency
pathinthegraph,butnottheuniquepath.Therefore,tweaking
PipeSearchachieveslow-latencygraph-basedANNSondisk
| thesearchalgorithmispossible. |     |     | Althoughitmaylengthen |     |     |     |     |     |     |     |     |     |     |     |
| ----------------------------- | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
thesearchpath,itdoesnotprohibitsearchfromconvergence bytacklingthetwoissuesin§2.2.Weanalyzeitasfollows.
PipeSearchachievescompute-I/Ooverlapping,whichac-
andbringsmoreopportunitiesforreducinglatency.
|     |     |     |     |     |     | celerates |      | ANNS          | as they | show     | close      | latency. | Bothshort    |     |
| --- | --- | --- | --- | --- | --- | --------- | ---- | ------------- | ------- | -------- | ---------- | -------- | ------------ | --- |
|     |     |     |     |     |     | and       | long | I/O latencies |         | may make | pipelining |          | inefficient. | If  |
3.2 PipeSearchAlgorithm
I/O
|     |     |     |     |     |     |     | latency | is short | like | in memory, |     | greedy | search | shows |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | ---- | ---------- | --- | ------ | ------ | ----- |
WeproposePipeSearch,alow-latencyalgorithmforgraph- low latency. If I/O latency is long,pipelining will degrade
basedANNSondisk.ThekeyideaofPipeSearchistoalign
tobest-firstsearchduetoshortcompute.However,ingraph-
thebest-firstsearchalgorithmwithSSDcharacteristics.As basedANNSondisk,computeandI/Olatenciesareofthe
shown in Figure 4,best-first search executes compute and same orderofmagnitude,making PipeSearch efficient. As
174    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|              | SIFT (L=30, pipe)   |     |     | SIFT (L=30, BF)   |                |     |                   |                        |              |     |     |     |                       |     |     |
| ------------ | ------------------- | --- | --- | ----------------- | -------------- | --- | ----------------- | ---------------------- | ------------ | --- | --- | --- | --------------------- | --- | --- |
|              |                     |     |     |                   |                |     |                   | 1. In-memoryentrypoint |              |     |     |     | 2. On-disk PipeSearch |     |     |
|              | SPACEV (L=30, pipe) |     |     | SPACEV (L=30, BF) |                |     |                   |                        |              |     |     |     |                       |     |     |
|              | 4                   |     |     |                   |                |     | Throughput (Op/s) | Vector                 | optimization |     |     |     |                       |     |     |
|              | (a) Search Latency  |     |     |                   | (b) Throughput |     |                   |                        |              |     |     |     | with dynamic pipeline |     |     |
| )sm( ycnetaL |                     |     |     |                   |                |     | 15k               | search                 |              |     |     |     |                       |     |     |
§4.3 Algorithm
10k
|     | 2   |     |     |     |     |     |     |     |     |     |     |         | Optimization |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------------ | --- | --- |
|     |     |     |     |     |     |     | 5k  |     |     |     |     | Compute |              |     |     |
…
|     | 0     |                        |     |     |     |       | 0   |     |     |     |     | I/O |               |     |     |
| --- | ----- | ---------------------- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | ------------- | --- | --- |
|     | 1 2 4 | 8 16 32                |     | 1 2 | 4 8 | 16 32 |     |     |     |     | *   |     |               |     |     |
|     |       | I/O Pipeline Width (W) |     |     |     |       |     |     |     |     |     |     | §4.2 Dynamic  |     |     |
Pipeline
Figure5: LatencyandthroughputofPipeSearchandbest-first
search(BF)withdifferentWs.WithL=30,bothalgorithms Figure7: PipeANNoverview.
achieve90%accuracyintermsofrecall10@10.
W=8)failstoachievehighthroughputsimultaneously.Ithas
|     | SIFT (L=100)         |     | SPACEV (L=100) |     |                |     |                   |                                               |     |     |     |     |     |     |     |
| --- | -------------------- | --- | -------------- | --- | -------------- | --- | ----------------- | --------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|     |                      |     |                |     |                |     | Throughput (Op/s) | 71.0%/72.4%lowerthroughputcomparedtoW=2.Onthe |     |     |     |     |     |     |     |
|     | 8 (a) Search Latency |     |                |     | (b) Throughput |     | 8k                |                                               |     |     |     |     |     |     |     |
)sm( ycnetaL otherhand,theoptimalpipelinewidthvariesindifferentcon-
|     | 6   |     |     |     |     |     | 6k  | figurations.Figure6showstheresultswithL=100,where |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
W=16showsthelowestlatency(82.7%/81.1%comparedto
|     | 4   |     |     |     |     |     | 4k  |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
W=8),andW=4deliversthehighestthroughput.
|     | 2   |     |     |     |     |     | 2k  |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(2)Comparedtobest-firstsearch,PipeSearchreducesla-
|     | 0   |     |     |     |     |     | 0   |     |     |     |     |     | W = | PipeSearch |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- |
1 2 4 8 16 32 1 2 4 8 16 32 tency but degrades throughput. When 8,
has50.7%/56.3%lowerlatencythanbest-firstsearchinthe
I/O Pipeline Width (W)
|     |     |     |     |     |     |     |     | SIFT/SPACEV |     | dataset. | However,the |     | throughput | degrades |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | -------- | ----------- | --- | ---------- | -------- | --- |
88.1%/82.5%.
LatencyandthroughputofPipeSearchwithdiffer- to This issue is more significant for larger
Figure6:
|     |     |     |     |     |     |     |     | pipeline | widths. | When | W   | =16, PipeSearch |     | only | achieves |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------- | ---- | --- | --------------- | --- | ---- | -------- |
entWsandL=100.PipeSearchachieves99%/97%accuracy
75.8%/73.8%ofthethroughputofbest-firstsearch.
intermsofrecall10@10inSIFT/SPACEV.
|     |     |     |     |     |     |     |     | The    | throughput |                 | degradation | results | from | I/O     | waste. |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ---------- | --------------- | ----------- | ------- | ---- | ------- | ------ |
|     |     |     |     |     |     |     |     | I/O    |            |                 |             |         | I/O  |         |        |
|     |     |     |     |     |     |     |     | waste, |            | which increases |             | average | per  | search, | makes  |
showninFigure3(a),whenW=32,thecomputelatencyis PipeSearcheasiertosaturateSSDbandwidthandthuscauses
75.6%/72.7%oftheI/Olatency.Overlappingthemispossible athroughputdrop.Itarisesfromtwoaspects.Thefirstislarge
pipelinewidths.ForPipeSearch,W=32has2.44×/2.24×av-
toprovidea1.7×performanceboost.
TheI/OpipelinecanbesaturatedbyenoughI/O,because erageI/OpersearchcomparedtoW=8,duetomorespecula-
tiveI/O.AlthoughasmallpipelinewidthreducesI/Owaste,it
| ofthenavigationgraphfeature. |     |     |     | Inatypicalnavigation |     |     |     |     |     |     |     |     |     |     |     |
| ---------------------------- | --- | --- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
leadstomoresequentialaccesses,thusincreasingthenumber
| graph, | each vector | contains | hundreds |     | of neighbors, |     | so the |     |     |     |     |     |     |     |     |
| ------ | ----------- | -------- | -------- | --- | ------------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
ofsearchstepsandsearchlatency.
candidatepoolcontainshundredsofunexploredvectorsafter
thefirstsearchstep,whichcanbeusedtofillupthepipeline. The second is the accumulation of read-but-unexplored
|     |     |     |     |     |     |     |     | neighbor | vectors. |     | When the | neighbor | exploration |     | is slow, |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | -------- | --- | -------- | -------- | ----------- | --- | -------- |
Itispossibletoprovideanother1.7×performanceboostwhen
W=32,asinFigure3(b).Theremaynotbeenoughvectorsto thepre-readneighborsmaybeaccumulatedinmemorybut
fillupthepipelineinthelatersearchstepswhenmostvectors unexplored.Thiscausessub-optimalI/Odecisionsbecauseof
missedneighborinformation,andthusintrinsicI/Owasteof
arerecalled.However,in§4.2,wefinditdoesnotlastlong.
PipeSearch.Comparedtobest-firstsearch,PipeSearchshows
1.34×/1.43×averageI/OpersearchwhenW=8.
| 3.4 | DilemmaofLatencyandThroughput |     |     |     |     |     |     |     |       |             |     |           |     | I/O   |     |
| --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | ----- | ----------- | --- | --------- | --- | ----- | --- |
|     |                               |     |     |     |     |     |     | We  | raise | a question: | Can | we reduce | the | waste | in  |
PipeSearchreducesthelatencyofbest-firstsearchbutfailsto PipeSearch,toachievelowlatencyandhighthroughput
simultaneously?Basedontheanalysisabove,wesummarize
achievelowlatencyandhighthroughputsimultaneously.We
evaluatePipeSearchusing100millionvectorsintwodatasets, twochallengesforthisquestion.Thefirstistodynamically
|     |     |     |     |     |     |     |     | adjust | to suitable |     | pipeline | widths | in a single | search. | The |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ----------- | --- | -------- | ------ | ----------- | ------- | --- |
SIFT[10]andSPACEV[4],using1threadforlatencyand
56threadsforthroughput.Asacomparison,weevaluatethe secondistoavoidtheaccumulationofneighborvectors.
best-firstsearchwiththesameW.Theresultsareshownin
Figure5,andwemakethefollowingobservations: 4 PipeANNDesignandImplementation
(1)PipeSearchfailstoensurelowlatencyandhighthrough-
putsimultaneously,withastaticpipelinewidth.Ontheone WedesignPipeANN,alow-latencygraph-basedANNSsys-
hand,thepipelinewidthwiththelowestsearchlatency(i.e., temondiskwithhighsearchthroughput. PipeANNintegrates
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    175

Algorithm2OptimizedPipeSearchinPipeANN
|     |     |     |     |     |     |     | W=1 | W=2 | W=4 | W=8 | W=16 |     | W=32 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | ---- |
G←graph,q←queryvector,L←candidatepoollength 300 (a) SIFT (b) SPACEV
1:
hcraeS/OI#
2: L m ←candidatepoollengthofthein-memoryindex
| procedurePipeSearch(G,q,L) |     |     |     |     |     | 200 |     |     |     |     |     |     |     |
| -------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
3:
W←4
| 4:  |     |     | ▷Startingpipelinewidth. |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
100
5: //Approachphase:entrypointoptimization.
|     | candidatepoolP←InMemSearch(q,min(L,L |     |     |     | ))  |     |     |     |     |     |     |     |     |
| --- | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6:  |                                      |     |     |     | m   |     | 0   |     |     |     |     |     |     |
| 7:  | exploredpoolE←∅                      |     |     |     |     |     | 0   | 50  | 100 | 0   | 50  |     | 100 |
Candidate Pool Length (L)
8: unexploredsetU←∅,unfinishedI/OsQ←∅
//Convergephase:dynamicpipeline.
9:
whileP⊊Edo
| 10: |     |     |     |     |     | Figure8: | I/Owasteof |     | PipeSearchdecreasesacrosssearch |     |     |     |     |
| --- | --- | --- | --- | --- | --- | -------- | ---------- | --- | ------------------------------- | --- | --- | --- | --- |
if Q.size()<W then ▷I/Opipelinenotfull. steps.Ingeneral,itcontainsaturningpointforeachW,after
11:
whichtheI/Owasteissimilartotheidealcase(i.e.,W=1).
| 12: | V←top-1nearestvectorstoqinP,notinE |     |                    |     |     |     |     |     |     |     |     |     |     |
| --- | ---------------------------------- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 13: | Q.insert(V)                        |     | ▷sendreadrequests. |     |     |     |     |     |     |     |     |     |     |
endif
| 14: |                       |     |     |                  |     |                   |     |        | currentI/O |     |               |     |     |
| --- | --------------------- | --- | --- | ---------------- | --- | ----------------- | --- | ------ | ---------- | --- | ------------- | --- | --- |
|     |                       |     |     | ▷overlapwithI/O. |     | ofrecalledvectors |     | andthe |            |     | waste,basedon |     | the |
| 15: | v←nearestvectortoqinU |     |     |                  |     |                   |     |        |            |     |               |     |     |
candidatepoolstateandthefinishedI/O.
|     | E.insert(v),U.remove(v) |     |     | ▷explorev. |     |              |     |         |     |       |            |     |     |
| --- | ----------------------- | --- | --- | ---------- | --- | ------------ | --- | ------- | --- | ----- | ---------- | --- | --- |
| 16: |                         |     |     |            |     | Also,PipeANN |     |         |     | I/O   | PipeSearch |     |     |
|     |                         |     |     |            |     |              |     | reduces | the | waste | of         |     | by  |
| 17: | fornbrinv.neighborsdo   |     |     |            |     |              |     |         |     |       |            |     |     |
notensuringaperfectpipelineatalltimes(lines11–14,§4.3).
| 18: | dis←PQ_distance(nbr,q) |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
WhenmultipleI/Osfinishsimultaneously,PipeANNdoesnot
P.insert(<nbr,dis>)
| 19: |        |     |                       |     |     | immediatelyfillupthepipeline.Instead,PipeANNrepeatedly |     |     |     |     |     |     |     |
| --- | ------ | --- | --------------------- | --- | --- | ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
| 20: | endfor |     | ▷updatecandidatepool. |     |     |                                                        |     |     |     |     |     |     |     |
issuesoneI/Oandexploresonevectorinthecandidatepool.
|     | P←lnearestvectorstoqinP |     |     | ▷PQdistance. |     |                                                      |     |     |     |     |     |     |     |
| --- | ----------------------- | --- | --- | ------------ | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| 21: |                         |     |     |              |     | Inthisway,itensuresthatthenthI/Oisdecidedbytheneigh- |     |     |     |     |     |     |     |
F←finishedI/OsinQ
| 22: |     |     | ▷pollforcompletion. |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
borinformationofthe(n−W)thcompute,thusincreasingthe
| 23: | W←AdaptPipelineWidth(P,F) |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
I/Oaccuracy.Theperfectpipelinecanbefinallyensured,as
U.insert(F),Q.remove(F)
| 24: |     |     |     |     |     | theI/Ocompletiontimestendtodifferinthisstrategy. |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
25: endwhile
| 26: | returnknearestvectorstoqinE |     |     | ▷exactdistance. |     |     |     |     |     |     |     |     |     |
| --- | --------------------------- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
4.2 DynamicPipeline
27: endprocedure
PipeSearchfailstoensurelowlatencyandhighthroughput
PipeSearch simultaneously with a fixed pipeline width. Therefore,we
|     | and improves | it using | dynamic | pipeline | width |         |          |     |          |                   |     |     |         |
| --- | ------------ | -------- | ------- | -------- | ----- | ------- | -------- | --- | -------- | ----------------- | --- | --- | ------- |
|     |              |          |         |          |       | propose | to adapt | the | pipeline | width dynamically |     | in  | search. |
(§4.2)andalgorithmoptimization(§4.3).
|     |     |     |     |     |     | In  | this section,we | first | introduce | the | key observation |     | that |
| --- | --- | --- | --- | --- | --- | --- | --------------- | ----- | --------- | --- | --------------- | --- | ---- |
motivatesustoadaptthepipelinewidth.Then,wedescribe
4.1 PipeANNOverview
thetwophasesofvectorsearchseparately.
Figure7showstheoverviewofPipeANN.
4.2.1 I/OWasteDecreasesAcrossSearchSteps
| Graphlayout. | Ondisk,PipeANNstoresthegraphasadja- |     |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
centlists(§2.1).Inmemory,itstoresPQ-compressedvectors In §3.4,we demonstrate the dilemma of PipeSearch in la-
forneighbordistance comparison anda smallgraph-based tencyandthroughput.Withhigherpipelinewidth,PipeSearch
indexforentrypointoptimization. showslowlatencybutlowthroughput,becauseofhighI/O
Vectorsearch. PipeANNusesPipeSearchforvectorsearch waste.However,weobservethatthisdilemmaisnotfunda-
but increases its throughput (Algorithm 2). It separates a mental:ItconsidersANNSatacoarsegranularityofawhole
single vector search into two phases, approach phase and search,insteadofeachsearchstep.
convergephase,basedonthekeyobservationthatI/Owaste
ToconsiderANNSatthegranularityofeachstep,weeval-
uatetheaverageI/OpersearchwithdifferentLs,asshown
decreasesacrosssteps(§4.2).
In the approach phase, the vector search gradually ap- in Figure 8. This evaluation is based on an observation:
| proachesthetargetvector,whenI/Owasteissignificantand |     |     |     |     |     | PipeSearch |      |         |      |               |     |              |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | ---------- | ---- | ------- | ---- | ------------- | --- | ------------ | --- |
|                                                      |     |     |     |     |     |            | with | a small | L is | approximately |     | a subprocess |     |
thusPipeSearchisinefficient.Therefore,PipeANNusesanin- (inotherwords,anearlytermination)ofonewithalargeL.
memoryindex(line6)forentrypointoptimization,andthen Therefore,theslopeinFigure8revealstheaverageI/Ofor
startsPipeSearch(lines7–25)withasmallpipelinewidth. recallingtheLthvector;asmallerslopemeanslessI/Owaste.
Intheconvergephase,thevectorsearchrecallsvectorsnear InFigure8,weobservethattheI/Owasteacrosssearch
thetargetvector,whenI/Owastegraduallydecreasesandthus
|     |     |     |     |     |     | steps | shows | two stages. | At  | the beginning |     | of the | search, |
| --- | --- | --- | --- | --- | --- | ----- | ----- | ----------- | --- | ------------- | --- | ------ | ------- |
PipeSearchshowsefficiency.Thus,PipeANNdynamicallyin- PipeSearch shows a significantI/O waste,whichincreases
creasesthepipelinewidth(line23)byestimatingthenumber withW.Then,itreachesaturningpoint,afterwhichtheI/O
176    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

* Target Vector 1 Explored Vector 1 Unexplored Vector andbuildsanin-memorygraph-basedindexusingthem.The
1 Unexplored Top-k Neighbor (i.e., in the candidate pool) indexisbuiltofflineandisthusstatic.Fortheonlinevector
search,PipeANNfirsttraversesthein-memoryindextoselect
| (a) Approach Phase |         |        |     | (b) Converge Phase |         |        |     |                                              |     |                                  |     |     |     |     |
| ------------------ | ------- | ------ | --- | ------------------ | ------- | ------ | --- | -------------------------------------------- | --- | -------------------------------- | --- | --- | --- | --- |
|                    |         | Search |     |                    |         | Search |     | entrypointsandthenconductson-diskPipeSearch. |     |                                  |     |     |     |     |
| 10                 | 6 top-k |        | 12  | 10                 | 6 top-k |        | 12  |                                              |     |                                  |     |     |     |     |
|                    |         | 7      |     |                    |         | 7      |     | Parameterselection.                          |     | In-memoryindextraversalliesinthe |     |     |     |     |
|                    | 2       |        | 14  |                    | 2       |        | 14  |                                              |     |                                  |     |     |     |     |
criticalpathofthewholevectorsearch.Therefore,weshould
|     | 5   |     |     | 5   |     |     |     |                                                    |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|     | *   |     | 13  |     | *   |     | 13  |                                                    |     |     |     |     |     |     |
|     | 1   | 3   |     |     | 1   | 3   |     | carefullyselectitsparameterstoensureitslowlatency. |     |     |     |     |     |     |
|     |     |     | 15  |     |     |     | 15  |                                                    |     |     |     |     |     |     |
Followingpreviouswork[25],PipeANNusesa1%sample
|     | 4   | 11  |     |     | 4   | 11  |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
9 8 9 8 rate forthe entry points to balance entry point quality and
Candidate Pool (  = 8): Candidate Pool (  = 8): memoryusage.WeuseVamana(i.e.,in-memoryDiskANN)
asthegraphindexstructure.Theindexisonlyusedtoeffi-
|     | 3 11 12 | 13 14 15 |     | 1   | 2 3 | 4 5 6 | 7 8 |     |     |     |     |     |     |     |
| --- | ------- | -------- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |         | 𝐿𝐿       |     |     |     | 𝐿𝐿    |     |     |     |     |     |     |     |     |
cientlyfindthetop-ksampledentrypoints,sootherindexes
|     |     |     |     |     |     |     |     | (e.g.,HNSW | [16] | and NSG | [6]) | show | similar tradeoffs | to  |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---- | ------- | ---- | ---- | ----------------- | --- |
Vamana.Thisisalsodemonstratedinpreviouswork[25].
| Figure9: | Two-phasesearchofgraph-basedANNSindexes. |     |           |         |      |     |         |                                 |            |        |           |                     |          |        |
| -------- | ---------------------------------------- | --- | --------- | ------- | ---- | --- | ------- | ------------------------------- | ---------- | ------ | --------- | ------------------- | -------- | ------ |
|          |                                          |     |           |         |      |     |         | Here,                           | we discuss | the    | maximum   | out-degree,         | which    | con-   |
|          |                                          |     |           |         |      |     |         | tributesmosttothesearchlatency. |            |        |           | Webuildthein-memory |          |        |
| waste    | is similarto                             | the | idealcase | (i.e.,W | =1). | The | turning |                                 |            |        |           |                     |          |        |
|          |                                          |     |           |         |      |     |         | index using                     | the        | Vamana | algorithm | [23],               | which is | an ap- |
pointarriveslater(i.e.,alargerL)foralargerW. proximationofaMonotonicRelativeNeighborhoodGraph
WeuseFigure9tofurtherdemonstratethisobservation. (MRNG)[6]. Itssearchcomplexitylinearlyincreaseswith
Thebest-firstpolicyofvectorsearchnaturallydividesitinto
theaverageout-degree.Asthisin-memoryindexisonlyused
twophases,approachphaseandconvergephase.Intheap- forentrypointselection,nottheoverallindexing,wecanuse
proachphase,thevectorsinthecandidatepoolquicklyap-
|     |     |     |     |     |     |     |     | asmallermaximum |     | out-degree,toleratingtheconnectivity |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ------------------------------------ | --- | --- | --- | --- |
proachthetargetvector.Duringthisphase,PipeSearchwith
lossofsomepointsforlowersearchlatency.Bydefault,we
largepipelinewidthsfailstorecallmorevectorsthatarelikely use 32 as the maximum out-degree of in-memory indexes,
inthesearch’scriticalpath,inducingI/Owaste.
smallerthaninpreviousworks[6,25].
Intheconvergephase,thenearestvectorinthecandidate
poolremainsstable,andthetop-knearestvectorsaregradu-
|     |     |     |     |     |     |     |     | 4.2.3 ConvergePhase:PipelineWidthAdjustment |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------- | --- | --- | --- | --- | --- | --- |
allyrecalled.Themorerecalledvectors(largerLinFigure8),
PipeANNdynamicallyadjuststhepipelinewidthduringthe
themoretop-kneighborstheyconnect.Thus,therearemore
"unverified"top-kvectorsinthecandidatepool,whichallows search. To achieve this,two questions shouldbe answered.
usingalargepipelinewidthforfastverification.Duringthis Thefirstiswhentostartadjustingthepipelinewidth,andthe
phase,theaverageI/Oforeachvectorremainsstable. secondiswhichpipelinewidthshouldbeselected.
Method:two-phasegraphtraversal. Basedontheobser- Whentostartadjusting. Weapproximatethenumberof
vationsabove,weusedifferentapproachesinthetwophases, vectorsthatarealreadyrecalledn .Whenthenumberreaches
v
inordertoreducetheI/OwasteinPipeSearch.Weseekto
|     |     |     |     |     |     |     |     | a threshold, | we  | consider | the search | to  | reach the converge |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | -------- | ---------- | --- | ------------------ | --- |
quicklypass the approachphase,where PipeSearch shows phaseandstarttoincreasethepipelinewidth.
inefficiency.Therefore,weoptimizetheentrypoint(§4.2.2) Specifically,afterexploringonevector,weiterateoverthe
andstartPipeSearchwithasmallpipelinewidth.Inthecon- candidatepooltofindthefirstvectorwhosereadrequesthas
vergephase,wedynamicallyincreasethepipelinewidthof not been issued. Its index is used as an approximation of
| PipeSearch,basedonthecandidatepoolstate(§4.2.3). |     |     |     |     |     |     |     | n   |     |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
v ’supperbound.Thisisnotanaccurateestimationbecause
theremaybeunexploredvectorsthathavebeenalreadyread.
| Pipelinedrainingdoesnotlastlong. |     |     |     |     | ThisrecallstheOb- |     |     |     |     |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Exploringthemmayaddnewnearerneighbors.
servation2in§3.1.Inthelatersearchsteps,mostvectorsare
recalled,soPipeANNfailstoensureafullpipeline.However, We further understand this estimation. In the approach
asshowninFigure8,theI/Owasteisnotsignificantinthe phase,thereareusuallynewnearestneighborsafterexploring
|                                                     |     |     |     |     |     |     |     | avector,sotheestimatedn |         |         | typicallyequals0.Intheconverge |           |          |         |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----------------------- | ------- | ------- | ------------------------------ | --------- | -------- | ------- |
| latersearchsteps.Weconcludethatmostremainingvectors |     |     |     |     |     |     |     |                         |         |         | v                              |           |          |         |
|                                                     |     |     |     |     |     |     |     | phase, it               | is hard | to find | nearer                         | neighbors | than the | already |
areaccuratetop-kneighborsofthetargetvector:Newvectors
exploredonesbyexploringanewvector,sotheestimatedn
are less likely to be inserted into the candidate pool when v
readingthem.Therefore,thisprocessdoesnotlastlong. graduallyincreases.
|     |     |     |     |     |     |     |     | Aftertheestimatedn |     |     | reachesathreshold(5inourevalua- |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --- | ------------------------------- | --- | --- | --- |
v
tion),westartadjustingthepipelinewidth.Beforethat,the
4.2.2 ApproachPhase:EntryPointOptimization pipelinewidthissettoafixedvalueof4toreduceI/Owaste.
PipeANN
uses an in-memory graph-based index for entry Howtoadjust. Weproposetwoapproachesforthis,static
pointoptimization,similartopreviousworks[25]. Specifi- approach and dynamic approach,and we use the dynamic
cally,PipeANNsamplesaportionofentrypointsinthedataset approachbydefault.
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    177

|     |     |           |         |            |      |     |     | 4.4 ImplementationandOtherOptimizations |     |     |                          |     |     |
| --- | --- | --------- | ------- | ---------- | ---- | --- | --- | --------------------------------------- | --- | --- | ------------------------ | --- | --- |
|     |     | 1 Compute |         | 1 Disk I/O |      |     |     |                                         |     |     |                          |     |     |
|     |     | 1 2       | 3 4 5 6 | 7 8        | 9 10 | 11  | 12  |                                         |     |     | PipeANNneedstowaitforthe |     |     |
Overlappinginitialization.
1 5 9 firstdiskI/Otofinish,togetneighborinformationforfilling
|     | 2   |     | 6   | 10  |     |     | …   |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
upthepipeline.Thisprocesshasalatencyof∼50µsinour
|     | 3   |     | 7   |     | 11  |     |     |                                                    |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- |
|     |     | 4   | 8   |     | 12  |     |     | NVMeSSD.WeoverlapitwithlocalPQtableinitialization, |     |     |     |     |     |
whichisperformedforeachquerytoenablefastPQdistance
lookup.However,localPQtableinitializationneedstoread
| Figure10: | WhenmultipleI/Ofinishsimultaneously,weissue |     |     |     |     |     |     |            |           |       |        |                |          |
| --------- | ------------------------------------------- | --- | --- | --- | --- | --- | --- | ---------- | --------- | ----- | ------ | -------------- | -------- |
|           |                                             |     |     |     |     |     |     | the global | PQ table, | which | is not | used in search | and thus |
oneI/Oafterexploringonerecord,insteadofissuingmultiple
causescachepollution.Weusenon-temporalloadinAVX512
I/Otosaturatethepipeline.Therefore,everydiskI/Omisses
instructiontoavoidthisissue.
| theneighborinformationinnomorethanW |     |     |     |     |     | records. |     |              |      |         |      |          |             |
| ----------------------------------- | --- | --- | --- | --- | --- | -------- | --- | ------------ | ---- | ------- | ---- | -------- | ----------- |
|                                     |     |     |     |     |     |          |     |              | I/O. | PipeANN |      | io_uring |             |
|                                     |     |     |     |     |     |          |     | Asynchronous |      |         | uses |          | [11] to is- |
I/O
|     |     |     |     |     |     |     |     | sue | requests,due | to  | its performance | and | compatibility. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | --------------- | --- | -------------- |
Specifically,eachthreadusesitsprivateio_uringtosend
ThestaticapproachfirstprofilesthedatasetbyPipeSearch
I/Orequestsasynchronously,withtheprep_readcommand
withdifferentWsandLstogettheresultslikeFigure8.Then,
(line13inAlgorithm2).ItpollsforI/Ocompletion(line22)
itgeneratesafixed(#vectorsrecalled–W)mappingbasedon
usingthenon-blockingpeek_batch_cqecommand.
theresults.Inthismapping,each"#vectorsrecalled"corre-
|     |     |     |     |     |     |     |     | Polling-basedI/O. |     | Existingsystemsadoptinterrupt-based |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | ----------------------------------- | --- | --- | --- |
spondstothelargestWafteritsturningpoint.Duringavector
I/Oforbest-firstsearch.Theydonotusepolling-basedI/Oas
| search,itadjustsW |     |     | basedontheestimatedn |     |     | .   |     |     |     |     |     |     |     |
| ----------------- | --- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
v
itslatencyadvantagedoesnotboosttheperformance.They
Thedynamicapproachusesanothermetric:thepercentage
synchronouslywaitforalltheI/Osinabatchtofinishbefore
ofI/Othatthevectorfetchedisinthecandidatepool.Specifi-
compute,thusinterruptoverheadisminorcomparedtoI/O
cally,afterstartingpipelinewidthadjustment,were-calculate
latency.However,PipeANNneedstoissueandpollI/Owith
| this ratio | when | there | exists finishedI/O. |     | When | the ratio | is  |     |     |     |     |     |     |
| ---------- | ---- | ----- | ------------------- | --- | ---- | --------- | --- | --- | --- | --- | --- | --- | --- |
lowlatency,asitcouldusethesavedI/Otimeforcomputation.
greaterthanathreshold(0.9inourevaluation),weincrease
Hence,weenableSQpollingoftheio_uringengine.
thepipelinewidthby1.
|     |     |     |     |     |     |     |     | 4.5 Discussion |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | --- | --- | --- | --- |
4.3 AlgorithmOptimization Beyond SSD. PipeSearch is designed for on-disk graph-
basedANNSbutisnotrestrictedtoit.Themechanismscanbe
Comparedtobeamsearch,naivePipeSearchshowsathrough- usedforotherhardwarewithµs-scaleaccesslatency,suchas
| put drop,especially |     |     | with large | pipeline | widths,due |     | to I/O |     |     |     |     |     |     |
| ------------------- | --- | --- | ---------- | -------- | ---------- | --- | ------ | --- | --- | --- | --- | --- | --- |
remotememoryusingremotedirectmemoryaccess(RDMA)
wastecausedbyaccumulatedneighborvectors.Here,wede- orcomputeexpresslink(CXL).Inthiscase,thewholegraph-
scribethisindetail. basedindexisstoredinremotememory.PQ-compressedvec-
TherootcauseofI/Owasteismissingneighborinformation torsandthesmallindexforentrypointoptimizationarestored
in the fetched vectors. Less missed neighbor information inlocalmemory.AsynchronousI/Ocouldbeimplementedby
|         |      |          | I/O        |     |      | I/O  |        | replacingio_uringcommandswithcorrespondingremote |     |     |     |     |     |
| ------- | ---- | -------- | ---------- | --- | ---- | ---- | ------ | ------------------------------------------------ | --- | --- | --- | --- | --- |
| induces | more | accurate | decisions, |     | thus | less | waste. |                                                  |     |     |     |     |     |
Forexample,greedysearchissuesI/Oafterexploringallthe memorycommands(e.g.,usingRDMAreadorCXLprefetch
|     |     |     |     |     |     |     |     | insteadofprep_read). |     |     | Astheremotememorylatency(e.g., |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | ------------------------------ | --- | --- |
vectors,soitmissesnoneighborinformationandshowsless
I/OwastecomparedtobeamsearchandPipeSearch. 2µs for RDMA) is still the same order of magnitude with
Ideally,ifcomputeandI/Oareperfectlyoverlapped,each compute(µs-scaleforeachrecord),PipeSearchisexpected
toboostANNSperformanceonremotememory.
I/OinPipeSearchmissestheneighborinformationinnomore
on-flightI/Os).However,thisisbased Two-phasesearchinotherworks. VBASE[31]alsoob-
thanW records(inW
on the assumption that I/Os are finished uniformly in the servesasimilarphenomenonoftwo-phasevectorindexing,
timeline,whichisnottrueinSSDs. calledrelaxedmonotonicity.Itleveragesthisforefficientsim-
ilaritysearchwithtags,bydesigninganinterfacethatreturns
| When | multiple |     | I/Os finish | simultaneously,filling |     |     | up the |     |     |     |     |     |     |
| ---- | -------- | --- | ----------- | ---------------------- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
pipelinemaymakeI/Omisstheneighborinformationinmore thenextvectorinreplaceoftheinterfacethatreturnstop-k
|           |     |                                             |     |     |     |     |     | vectors. | We exploit | this | phenomenon | to reduce | I/O waste |
| --------- | --- | ------------------------------------------- | --- | --- | --- | --- | --- | -------- | ---------- | ---- | ---------- | --------- | --------- |
| records(W |     | on-flightI/Osandmultipleread-but-unexplored |     |     |     |     |     |          |            |      |            |           |           |
inPipeSearch,aimingtoensurebothlowlatencyandhigh
vectors).Toavoidthis,welimittheI/Oratebyhandlingmulti-
pleI/Osonebyone,asshowninFigure10.Specifically,after throughput.Specifically,weobservethatI/Owastedecreases
duringthesearchprocess,givenafixedpipelinewidth.
| multiple | I/O | finishes,we | repeatedly |     | send one | I/O,explore |     |              |     |                                 |     |     |     |
| -------- | --- | ----------- | ---------- | --- | -------- | ----------- | --- | ------------ | --- | ------------------------------- | --- | --- | --- |
|          |     |             |            |     |          |             |     | Memoryusage. |     | PipeANNrequires<40GBofmemoryfor |     |     |     |
onenearestvector,andupdatetheneighborset.Thiswaycan
reduceI/OwasteandgraduallyscattertheI/Osuniformlyin billion-scaledatasets,including:
thetimeline,thusnotincurringmuchoverhead. • 32GBforPQ-compressedvectors,32bytespervector.
178    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

• <4GBforthein-memorygraphindex.Inourevaluation, GraphType R L B
ituses2.4GBfortheSIFT1B[10]datasetand3.1GBfor On-Disk(100M) 96 128 32
theSPACEV1Bdataset[4]. On-Disk(1B) 128 200 32
• Minoroverheadsforotherin-memorydatastructures. In-Memory 32 64 /
Incomparison,DiskANN[23]requires∼32GBofmemory,
Table1: ParametersusedforVamana(i.e.,DiskANN)graph
mainlyforthePQ-compressedvectors.
building [23]. R: maximum out-degree. L: candidate pool
PipeANN’smemory-to-disksizeratiois∼1:15,considering
size for finding neighbors. B: PQ-compressed vector size
thatbillion-scalegraphindexesondisktypicallyrequireover (bits/vector).Thein-memoryindexisusedbyPipeANNand
600GBofdiskspace(e.g.,636GBforSIFT1Band892GBfor
Starlingforentrypointoptimization.
SPACEV1B).PipeANN’sprimarymemoryconstraintliesin
thePQ-compressedvectors,similartoDiskANN.Therefore,
Name #Vectors Type Dim #Queries
memory-efficient quantization (e.g., RaBitQ [7]) methods
SIFT1B[10] 1B uint8 128 10,000
couldreducetheirmemoryusage.
SPACEV1B[4] 1.4B int8 100 29,316
SIFT100M[10] 100M uint8 128 10,000
5 Evaluation DEEP100M[2] 100M float 96 10,000
SPACEV100M[4] 100M int8 100 29,316
Intheevaluation,weseektoanswerthefollowingquestions:
• How does PipeANN perform in latency and throughput Table 2: Datasets used in the evaluation. SIFT100M,
comparedtootheron-diskANNSindexes?(§5.2) DEEP100M, and SPACEV100M are subsets of SIFT1B,
• CanPipeANNscaletobillion-scaledatasets?(§5.3) DEEP1B,andSPACEV1B.
• IsPipeANNcomparablewiththein-memorygraph-based
ANNSindexintermsofsearchlatency?(§5.4)
thatStarlingreorderstheon-diskrecords.Thegraphindexes
• HowdothetechniquesinPipeANNcontributetoitsper-
arebuiltusingtheparametersinTable1.Forsearchparam-
formance?(§5.5) eters, the candidate pool size of in-memory index traver-
• Howdotheapproachesforpipelinewidthadjustmentim- sal L mem is fixed to 10 for PipeANN and Starling. We use
pactsearchperformance?(§5.6)
io_uring[11]astheI/OengineofPipeANNandenableSQ
• HowmuchdoesPipeANNtradesthroughputandaccuracy polling.Forfairness,wealsoreplacetheoriginalI/Oengine
withthesamesearchparametersforlatency?(§5.7)
(libaio)withio_uringforDiskANNandStarling.Wedis-
ableSQpollingforthem.WeuseW =8forDiskANNand
W=4forStarling,whichshowsthelowestlatencyseparately.
5.1 ExperimentalSetup WelimitthemaximumW ofPipeANNto32.
ForSPANN,webuildcluster-basedindexesusingthesame
Basic configuration. We use one server for evaluation,
parameter in the SPFresh [29] repository. Specifically,for
whichhasthefollowingconfiguration:
SIFT and SPACEV, we set their maximum cluster size to
• CPU:2×28-coreIntelXeonGold6330@2.00GHz;
16KB.ForDEEP,wesetitto48KB.Eachvectorisreplicated
• RAM:512GB(16×32GBDDR42933MT/s);
toitsnearest8clusters.
• SSD:1×SamsungPM9A33.84TB; Datasets. Weusefivepublicdatasetsintheevaluation,in-
• OS:Ubuntu22.04LTSwithLinuxkernel5.15.0. cluding100M-scaleandbillion-scaledatasets.Detailedcon-
Comparedsystems. WecomparePipeANNwithon-disk figurationsofthedatasetsareshowninTable2.
ANNS indexes,including graph-based DiskANN [23] and Metrics. Wemainlycomparethelatencyandthroughput
Starling[25],aswellascluster-basedSPANN[4].DiskANN for0.9recall,whichisrecommendedbytheBigANNbench-
isagraph-basedANNSindexusingbest-firstsearch.Starling mark[20].Lowrecall(e.g.,0.8)andhighrecall(e.g.,0.99)
optimizes the I/O of DiskANN by reordering the on-disk arealsousedinsomeexperimentsformorethoroughcompar-
recordstoimprovesearchlocalityandusinganin-memory ison.Weevaluatetherecallbysearchingthetop10nearest
indextooptimizetheentrypoint. neighbors(i.e.,recall10@10).
SPANNisanon-diskcluster-basedindex.Itseparatesthe
vectorsintoclustersandmaintainsanin-memorynavigation
5.2 OverallPerformance
graphtoindextheclustercentroids.ToconductANNS,itfirst
searchesthenearestclustersinthein-memorygraphandthen In this section, we evaluate the latency and throughput of
re-ranksallthevectorsintheclusterstogettheresults. PipeANNusingdatasetswith100Mvectors.Wedonotuse
Parameters. We use the same in-memory and on-disk billion-scaledatasets,wherethegraphreorderingalgorithm
graphindexesforPipeANN,DiskANN,andStarling,except in Starling has huge time and memory overhead. We will
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation 179

|             |          | PipeANN | DiskANN    |     | Starling |          | SPANN |     |             |            |     |              |     |     |
| ----------- | -------- | ------- | ---------- | --- | -------- | -------- | ----- | --- | ----------- | ---------- | --- | ------------ | --- | --- |
|             |          |         |            |     |          |          |       |     |             | PipeANN    |     | DiskANN      |     |     |
|             | (a) SIFT |         | (b) SPACEV |     |          | (c) DEEP |       |     |             | (a) SIFT1B |     | (b) SPACEV1B |     |     |
| 01@01llaceR | 1.0      |         |            |     |          |          |       |     | 01@01llaceR | 1.0        |     |              |     |     |
0.9
0.9
0.8
0.8
|     | 0   | 1   | 2 3 0               | 1   | 2   | 3 0 | 1   | 2 3 |     | 0   | 2 4                 | 0   | 2   | 4   |
| --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- |
|     |     |     | Search Latency (ms) |     |     |     |     |     |     |     | Search Latency (ms) |     |     |     |
Figure11: Searchlatencyondatasetswith100Mvectors. Figure13: Searchlatencyinbillion-scaledatasets.
|                   |     | PipeANN  | DiskANN |            | Starling |     | SPANN    |     |       |            |     |     |     |     |
| ----------------- | --- | -------- | ------- | ---------- | -------- | --- | -------- | --- | ----- | ---------- | --- | --- | --- | --- |
| )s/pO( tuphguorhT |     |          |         |            |          |     |          |     | 5.2.2 | Throughput |     |     |     |     |
|                   | 40k | (a) SIFT |         | (b) SPACEV |          |     | (c) DEEP |     |       |            |     |     |     |     |
Weuse56threads(allthecoresofourCPU)toconductANNS
|     | 20k |     |     |     |     |     |     |     | inthecomparedsystems.Figure12showstheresults.From |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- |
thefigure,wemakethefollowingobservations:
|     |     |     |     |     |     |         |     |     |                                                   | (1) When recall | = 0.9,PipeANN |     | consistently | shows the |
| --- | --- | --- | --- | --- | --- | ------- | --- | --- | ------------------------------------------------- | --------------- | ------------- | --- | ------------ | --------- |
|     | 0   |     |     |     |     |         |     |     | highestthroughput.Toachieve0.9recall10@10,PipeANN |                 |               |     |              |           |
|     | 0.8 | 0.9 | 1.0 | 0.8 | 0.9 | 1.0 0.8 | 0.9 | 1.0 |                                                   |                 |               |     |              |           |
Recall10@10 outperformsothersystemsby1.35×onaverage.Inthiscase,
thediskbandwidthisnotsaturated,becauseothertasks(e.g.,
Figure12: Searchthroughputondatasetswith100Mvectors. PQ table initialization) accountfora hightime percentage.
TheextraI/OofPipeANNdoesnotharmtheoverallthrough-
PipeANN’s
|     |     |     |     |     |     |     |     |     | put | much. | high | throughput | owes | to its shorter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | ---- | ---------- | ---- | -------------- |
showtheresultsinbillion-scaledatasetsin§5.3. criticalpath,becauseofpipelining.
(2)Forhigherrecall,PipeANNhasalowerthroughputthan
Starling.Toachieve0.99recall10@10,PipeANNhas0.80×
5.2.1 Latency
|     |     |     |     |     |     |     |     |     | lower | throughput | than Starling | on  | average,because | of the |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | ---------- | ------------- | --- | --------------- | ------ |
wasteddiskI/O.Inthiscase,thesearchproceduretakesup
Weuse1threadtoconductANNSinthecomparedsystems.
mostofthetime,whichsaturatesthediskbandwidth.Foreach
| Figure11 |     | shows | theresults. | From | thefigure,we |     | makethe |     |     |     |     |     |     |     |
| -------- | --- | ----- | ----------- | ---- | ------------ | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
search,PipeANNrequires1.94×averagediskI/Oonaverage
followingobservations:
(1)Comparedwithgraph-basedindexes,PipeANNshows comparedtoStarling,whichresultsinlowerthroughput.This
isbecauseofthereorderingtechniqueofStarling.Starling
| lower | latency. |     | To achieve | 0.9 | recall10@10, |     | PipeANN | has |     |     |     |     |     |     |
| ----- | -------- | --- | ---------- | --- | ------------ | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
39.1%/48.5%latencyonaverage,comparedtoDiskANN/S- reorderstheon-diskindexformoreneighboringrecordson
|          |      |     |         | PipeANN | efficiently |     |      |         | thesamepage,thusreducingdiskI/O. |     |     |     |     |     |
| -------- | ---- | --- | ------- | ------- | ----------- | --- | ---- | ------- | -------------------------------- | --- | --- | --- | --- | --- |
| tarling. | This | is  | because |         |             |     | uses | dynamic |                                  |     |     |     |     |     |
NotethatthedesignofPipeANNisorthogonalwithStar-
PipeSearchtooverlapcomputeandI/Oandincreasetheav-
|       | I/O |            |          |     |          |          |     |       | ling.InPipeANN,wecandirectlyadoptthesamereordering |     |     |     |     |     |
| ----- | --- | ---------- | -------- | --- | -------- | -------- | --- | ----- | -------------------------------------------------- | --- | --- | --- | --- | --- |
| erage |     | depth,thus | reducing |     | latency. | Starling | has | lower |                                                    |     |     |     |     |     |
techniquetoreduceI/O.However,consideringthehugetime
latencycomparedtoDiskANN.ThisisbecauseStarlinguses
thein-memoryindexforentrypointoptimizationandreorders andmemoryoverheadforreorderinginbillion-scaledatasets,
theon-diskgraphtoreducetheaverageI/Opersearch. wedonotadoptthistechniqueinPipeANN.
ComparedwithDiskANN,PipeANNshowshigherthrough-
(2)Comparedwithcluster-basedindexes,PipeANNshows
put.PipeANNhasasimilar(0.98×for0.99recall)average
lowerlatencywhenrecall≥0.9.Toachieve0.9recall10@10,
I/OpersearchcomparedtoDiskANN,butitcanbetteruti-
| PipeANN |     | has 70.6% | lower | latency |     | compared | to  | SPANN. |     |     |     |     |     |     |
| ------- | --- | --------- | ----- | ------- | --- | -------- | --- | ------ | --- | --- | --- | --- | --- | --- |
lizethediskbandwidthbecauseofpipelining.Thisresultsin
SPANNshowslowerlatencythanothergraph-basedindexes,
becauseofitsI/Ofriendliness.SPANNfirsttraversesanin- PipeANN’shigherthroughput.
memorygraph-basedindexforthenearestclustersofthetar-
getvector.Then,itsendsI/Otofetchtheclustersinparallel.
5.3 OverallPerformance:Billion-Scale
Incontrast,existinggraph-basedindexestraversethegraph
byissuingI/Obatchesinsequential,whereI/Olatencysig- In this section, we show the performance of PipeANN in
nificantlyharmstheoverallsearchlatency.PipeANNgreatly billion-scaledatasets.WecomparePipeANNwithDiskANN.
eliminatesthisissuebypipelining,whichmakesitfasterthan WedonotcomparePipeANNtootherbaselinesbecausebuild-
SPANNforrecall≥0.9.However,whentherecallissmaller ingorsearchingthemexceedsthememorycapacityinour
(e.g.,0.8),PipeANNsuffersfromtheoverheadofapproaching setup. Figures 13 and 14 show the results. In SPACEV1B,
thetargetvector,makingitslowerthanSPANN. we do not show DiskANN with accuracies less than 96%,
180    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|     | PipeANN |     | DiskANN |     |     |     |     |                       | Baseline |     | +Pipe | +AlgOpt |     | PipeANN |     |
| --- | ------- | --- | ------- | --- | --- | --- | --- | --------------------- | -------- | --- | ----- | ------- | --- | ------- | --- |
|     |         |     |         |     |     |     |     | )s/pO( tuphguorhT 30k |          |     |       |         |     |         | 10k |
)s/pO( tuphguorhT 40k (a) SIFT1B (b) SPACEV1B (a) Recall = 0.9 (b) Recall = 0.99
20k
5k
20k
10k
|     | 0   |     |             |     |     |     |     | 0   |     |                     |     |     |     |     | 0   |
| --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- |
|     | 0.6 | 0.8 | 1.0         | 0.9 |     |     | 1.0 |     | 0   | 1                   | 2   | 0   | 2   | 4 6 |     |
|     |     |     | Recall10@10 |     |     |     |     |     |     | Search Latency (ms) |     |     |     |     |     |
BreakdownanalysisofPipeANN.
| Figure14: |         | Searchthroughputinbillion-scaledatasets. |                    |     |     |     |     |     | Figure16: |     |     |     |     |     |     |
| --------- | ------- | ---------------------------------------- | ------------------ | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- |
|           | PipeANN |                                          | Vamana (In-Memory) |     |     |     |     |     |           |     |     |     |     |     |     |
(a) SIFT (b) DEEP phase,where PipeSearch cannot maintain a large pipeline
01@01llaceR 1.0
width.Therefore,PipeANNfailstohidealltheI/Olatency,
|     |     |     |     |     |     |     |     | which | makes | the performance |     | of PipeANN |     | lower | than the |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ----- | --------------- | --- | ---------- | --- | ----- | -------- |
0.9
in-memoryindex.
| 0.8 |     |     |     |     |     |     |     | (2)Forrecall≥0.9,theperformanceofPipeANNiscloseto |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
thein-memoryindex.Toachieve0.9recall10@10,PipeANN
|     | 0   | 1   |     | 2 0 | 1   | 2   | 3   |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
has2.02×/1.14×latencycomparedtoVamana.Inthiscase,
Search Latency (ms)
bothPipeANNandVamanausealargeL(e.g.,30).Thecon-
PipeSearch
|           |     |                 |     |                        |     |     |     | verge     | phase | accounts       | for a higher | ratio,where |        |             |     |
| --------- | --- | --------------- | --- | ---------------------- | --- | --- | --- | --------- | ----- | -------------- | ------------ | ----------- | ------ | ----------- | --- |
| Figure15: |     | Searchlatencyof |     | PipeANNcomparedwithVa- |     |     |     |           |       |                |              |             |        |             |     |
|           |     |                 |     |                        |     |     |     | maintains | a     | large pipeline | width        | for         | better | overlapping | of  |
mana(in-memoryDiskANN). computeandI/O.Therefore,theperformancegapbetween
PipeANNandVamanareduces.
|     |     |     |     |     |     |     |     | PipeANN’s |     | slowdown | is less | significant |     | in DEEP100M. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | -------- | ------- | ----------- | --- | ------------ | --- |
becauseitsaccuracyonlyachieves60%usingasmallerL.
Thisisbecause,inDEEP,distancecomparisonforVamana
| Latency. |     | As shown | in Figure | 13, | to achieve |     | 0.9 re- |     |     |     |     |     |     |     |     |
| -------- | --- | -------- | --------- | --- | ---------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
ismorecostlythaninSIFT.DEEPcalculates96floatsper
call10@10,PipeANNhaslatenciesof0.719msand0.578ms
vector,whichhasahigheroverheadthanthe128uint8sper
inSIFT1BandSPACEV1B,whichare1.28×/1.09×compared
contrast,PipeANN
|     |     |     |     |     |     |     |     | vectorin | SIFT. | In  |     |     | uses | PQ distance | for |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ----- | --- | --- | --- | ---- | ----------- | --- |
toSIFT100MandSPACEV100M.ComparedtoDiskANN,
neighbors,whichhassimilaroverheadsfordistancecompar-
PipeANNachieves35.0%latencyinSIFT.
thatPipeANN
|             |     |          |     |        |                |     |         | ison | in the | two datasets. | We conclude |     |     |     | is ex- |
| ----------- | --- | -------- | --- | ------ | -------------- | --- | ------- | ---- | ------ | ------------- | ----------- | --- | --- | --- | ------ |
| Throughput. |     | As shown | in  | Figure | 14, to achieve |     | 0.9 re- |      |        |               |             |     |     |     |        |
pectedtohavemorecomparableperformancewithin-memory
call10@10,PipeANNhas19.4Kand26.1KQPSinSIFT1B
ANNSwithhighervectordimensions.
andSPACEV1B,whichare79.9%and98.0%comparedto
SIFT100MandSPACEV100M.ComparedtoDiskANN,Pi-
peANNachieves1.71×higherthroughput.
|           |     |                                               |     |     |     |     |     | 5.5 | BreakdownAnalysis |     |     |     |     |     |     |
| --------- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- |
| Analysis. |     | Thesearchpathislongerforbillion-scaledatasets |     |     |     |     |     |     |                   |     |     |     |     |     |     |
Inthissection,webreakdowntheperformancegapofBase-
| than | 100M-scale | datasets,which |     | incurs | a highersearch |     | la- |                 |     |                                  |     |     |     |     |     |
| ---- | ---------- | -------------- | --- | ------ | -------------- | --- | --- | --------------- | --- | -------------------------------- | --- | --- | --- | --- | --- |
|      |            |                |     |        |                |     |     | lineandPipeANN. |     | Weaccumulatekeytechniquesintothe |     |     |     |     |     |
tencytoachievethesamerecall.However,italsobringsmore
|     |     |     |     |     |     |     |     | Baseline | and | evaluate | the latency-throughput |     |     | graph | with |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | -------- | ---------------------- | --- | --- | ----- | ---- |
opportunitiesforpipelining,whichcontributestoamoresig-
|     |     |     |     |     |     |     |     | 0.9 and | 0.99 | recall10@10. | We  | use | the index | built | on the |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ---- | ------------ | --- | --- | --------- | ----- | ------ |
nificantperformanceboostcomparedtoDiskANN.
SIFT100Mdataset,andthesameconfigurationsasin§5.2.
|     |     |     |     |     |     |     |     | Baseline. |     | WeimplementtheBaselinebasedontheframe- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | -------------------------------------- | --- | --- | --- | --- | --- |
5.4 ComparewithIn-MemoryIndex workofPipeANN.Itusesbest-firstsearchlikeDiskANNwith
|         |            |         |     |             |       | PipeANN |     | W =8 | and | adopts the | same in-memory |     | index | as PipeANN |     |
| ------- | ---------- | ------- | --- | ----------- | ----- | ------- | --- | ---- | --- | ---------- | -------------- | --- | ----- | ---------- | --- |
| In this | section,we | showthe |     | performance | gapof |         |     |      |     |            |                |     |       |            |     |
withanin-memorygraph-basedindex.Wedirectlystorethe forentrypointoptimization.AsshowninFigure16(a),the
on-diskindexofPipeANNinmemoryanduseitforsearching. Baseline shows ms-scale latency to achieve 0.9 recall. Al-
thoughadoptedentrypointoptimization,itsbest-firstsearch
| We  | callthis | baseline Vamana. |     | We compare | PipeANN |     | with |     |     |     |     |     |     |     |     |
| --- | -------- | ---------------- | --- | ---------- | ------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
VamanausingSIFT100MandDEEP100Mdatasets.Figure15 algorithmstillincurshighsearchlatencyondisk.
|     |     |     |     |     |     |     |     | +Pipe. | WeusePipeSearch(§3)withW |     |     |     | =8inreplaceof |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------------------------ | --- | --- | --- | ------------- | --- | --- |
showstheresults,andwemakethefollowingobservations:
(1)Forlowrecall,PipeANNshowshigherlatencythanthe best-firstsearchinBaseline.Itreduceslatencyto55.1%for
in-memoryindex.Toachieve0.8recall10@10inSIFT100M, 0.9recall.However,thethroughputisalsoreducedto88.5%.
PipeANN has 3.38× higherlatency than Vamana. Because ThisisbecausePipeSearchhasa1.11×averageI/Opersearch
ofasmallL(e.g.,10),thesearchismainlyintheapproach comparedtobest-firstsearch.TheI/Owasteandthroughput
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    181

#VectorsRecalled 0 10 20 30 40
PipelineWidth 4 8 16 24 32
Table3: Pipelinewidthusedbystaticapproach.
01@01llaceR
Throughput
(Op/s)
Dynamic Static
1.0 (a) (b) 40k
30k
0.9
20k
0.8
10k
0.7
0 0.5 1.0 1.5 0.8 1.0
Latency (ms) Recall10@10
Figure17: Performanceofdynamicapproachandstaticap-
proachforpipelinewidthadjustment.Dataset:SIFT100M.
droparelesssignificantthanin§3.4,asentrypointoptimiza-
tionreducestheI/Owasteduringtheapproachphase.
+AlgOpt. Weadoptthealgorithmoptimizationformulti-
plefinishedI/Os(§4.3).Itincreasesthethroughputto1.08×
becauseitreducestheaverageI/Opersearchto91.8%.The
performance boost is more significant in high-throughput
cases,whichconcludesthatmultipleI/Osaremorefrequent
tofinishsimultaneouslyinsuchcases.Thelatencyisslightly
reducedto97.5%,astheperformancedegradationoftheun-
saturatedI/Opipelineislesssignificantthantheperformance
boostofreducedI/O.
PipeANN. Weadoptthedynamicpipeline(§4.2)inreplace
ofthestaticonewithW=8.Itreducesthelatencyto81.1%
for0.99recallandincreasesthethroughputto1.07×. This
is because, in the converge phase, a large W allows more
computeandI/Ooverlapping,whilenotinducingmuchI/O
waste.Itdoesnotshowmuchperformanceboostfor0.9recall,
asthesearchterminatesearlyintheconvergephasewhenW
isnotsignificantlylargerthan8.
5.6 ApproachesforPipelineAdjustment
Inthissection,wecomparethetwoapproachesforpipeline
widthadjustment(§4.2.3),namelythestaticapproachandthe
dynamicapproach.Forthestaticapproach,wesetthepipeline
widthaccordingtotheprofilingresultssimilartoFigure8(a).
TheparametersusedareshowninTable3.
Figure 17 shows the results. We find that the dynamic
approachslightlyoutperformsthestaticapproachbyupto
6.1%/9.1%forlatencyandthroughput.Thisdemonstratesthat
PipeANNisnotsensitivetotheapproachforpipelinewidth
adjustment.Thedynamicapproachsuccessfullyfollowsthe
decreasingtrendofI/Owastetoincreasethepipelinewidth
acrossthesearchsteps.
)s/pO(
tuphguorhT
PipeANN DiskANN (ideal throughput)
(a) SIFT (b) SPACEV (c) DEEP
60k
40k
20k
0
0.7 0.8 0.9 1.00.7 0.8 0.9 1.0 0.7 0.8 0.9 1.0
Recall10@10
Figure18: ThroughputofPipeANNandDiskANNwithideal
throughput(best-firstsearchwithW=1).
5.7 TradeoffsinPipeANN
PipeANNtweaksthebest-firstsearchalgorithmforlowerla-
tency,butwithsometradeoffs.Inthissection,wedemonstrate
themusingexperiments.
Throughput. AlthoughPipeANNintroducestechniquesto
reduceI/Owaste,itsW>1couldstillwastemoreI/Ocom-
paredtotheidealbest-firstsearchwithW=1(notethatwe
useW=8forlowerlatencyin§5.2),andthusleadtolower
throughput.WeimplementthisidealbaselineusingDiskANN,
whichwecallDiskANN(idealthroughput).TosaturateSSD,
thisbaselineusesasynchronousI/O;oneCPUcoreexecutes
multiplesearchrequestssimultaneouslyandswitchesacross
themtoavoidI/Owaiting.WecomparePipeANNwiththis
baselineusingthesamedatasetsasin§5.2.
Figure18showstheresults.Fromthefigure,weobserve
that:First,PipeANNshowslowerthroughputthantheideal
DiskANNatlowaccuracy.Whenrecall=0.8,thethroughput
drop of PipeANN is 31.6%/34.1%/17.5% separately in the
threedatasets.Thisisbecausetheapproachphaseaccounts
foralargepercentage,whenPipeANN’sW>1leadstoI/O
waste.Second,thethroughputdropbecomeslesssignificant
athigheraccuracy.Whentherecallreaches0.95,thethrough-
put drop becomes 14.7%/6.15%/4.90%. In such cases,the
convergephaselastslonger,andsomewastedI/Ointheap-
proachphasearealsoexploredinbest-firstsearch.Thesetwo
reasonscontributetolessI/Owasteof PipeANN. Third,at
thesameaccuracy,PipeANNshowslessI/OwasteinDEEP
thantheothertwodatasets.ThisisbecauseDEEPrequires
alargercandidatepoollengthL,andthusalongerconverge
phase.ThisleadstolessI/Owaste.
Search accuracy with the same parameters. PipeANN
tweaksthebest-firstsearchalgorithm,whichmayleadtoan
accuracydropunderthesamesearchparameters.Here,we
evaluatethisissueintermsofquantity.WecomparePipeANN
withthe same L as DiskANN,whichuses best-firstsearch
withW=8.Figure19showstheresults.Fromthefigure,we
makethefollowingobservations:
(1)PipeANNshowslittleaccuracydrop.PipeANNhasat
least95.9%recallcomparedtoDiskANN.Whenrecall≥0.9,
thisvalueisfurtherincreasedto98.8%.Theaccuracydrop
182 19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

01@01llaceR
PipeANN DiskANN terminethesearchterminationconditionbasedonthesearch
1.0
(a) SIFT (b) SPACEV stateandanMLmodel,separately.ThedesignofPipeANN
0.9 is orthogonal to these works. These works can be directly
adoptedbyPipeANNforacceleration.
0.8 Incontrast,PipeANNreducesthesearchlatencybyaligning
thebest-firstsearchalgorithmwithSSDcharacteristics.
0.7
15 20 30 40 50 60 15 20 30 40 50 60 On-diskANNS. Tosupportlargerdatasets,recentworks
Candidate Pool Length (L)
storeANNSindexesondisk.Theycanbemainlydividedinto
twotypes,graph-basedindexesandcluster-basedindexes.
Figure 19: Accuracy of PipeANN and DiskANN with the Graph-basedindexesarefavoredfortheirsearchaccuracy
sameL.NotethattheY-axisdoesnotstartatzero. and I/O efficiency, which are suitable for high-throughput
ANNS.Theytypicallystorecompressedvectorsinmemory
fornavigation,and the full index on disk [8,23,25]. How-
isbecausePipeANNapproximatesthebest-firstsearchalgo-
ever,duetothebest-firstsearchalgorithm,thecriticalpathin
rithm.However,themodificationisslightenoughtoensure searchincludestensofsequentialI/O.Therefore,graph-based
similarbehaviorforsearchconvergence. indexessufferfromhighsearchlatencyondisk,whichmoti-
(2)TheaccuracydropislesssignificantforlargerL.We vatesthedesignsofPipeANN.Also,updatingthegraph-based
understandthisbyregardingPipeANNasa"best-firstsearch"
indexesinduceshighoverheads[22,29].
with a candidate pool length L−W,noticing that each I/O
Cluster-basedindexes[4,24]haveasimplerstructurethan
inPipeANNmissesatmostW vectors.Thesearchaccuracy
graph-basedindexes.Theydividethevectorsintomultiple
increasesslowerforlargerL,sotheaccuracygapofbest-first
clusters,eachofwhichcontainstensofvectors.Theclusters
searcheswithL−W andLbecomeslesssignificant.
arestoredondisk,andindexedbyanin-memorygraph.Vector
PipeANNachievesthesameaccuracywithDiskANNusing
search first finds the nearest clusters in memory and then
alargerL,butbenefitsfromlowerlatency.
readsthemondiskinparallel.Therefore,onlyoneparallel
diskI/Oliesinthecriticalpath,whichcontributestoitslow
searchlatency.Also,updatingthecluster-basedindexesincurs
6 RelatedWork
a lowercostthan graph-basedones [29]. However,cluster-
basedindexesaremorecoarse-grainedthangraph-basedones,
PipeANNtargetson-diskgraph-basedANNSwithlowlatency.
whichinduceslowersearchthroughput.
Inthissection,weintroducetwotypesofrelatedwork,namely
graphsearchoptimizationandon-diskANNS.
Graphsearchoptimization. Traditionalgraph-basedin- 7 Conclusion
dexesdoANNSinmemory.Theytypicallyusegreedysearch
totraversefromthestartingvectortothetargetvector[6,16]. WeproposePipeSearch,alow-latencyalgorithmforon-disk
Comparedtodistancecomparison,memoryaccessforvectors graph-basedANNS.PipeSearchaccelerateson-diskANNS
hasordersofmagnitudelowerlatency,sothegreedy-basedap- by aligning the best-first search algorithm with SSD fea-
proachisfavoredforreducedvectorsaccessedpersearch.In tures.Itbenefitsfromcompute-I/Ooverlappingandabetter-
suchascenario,distancecomparisonisthemajorbottleneck utilized I/O pipeline compared to best-first search. We op-
ofgraph-basedANNS,sosomeworksfocusonreducingthe timize PipeSearch andimplementPipeANN,alow-latency
overheadofdistancecomparisonforhighperformance[3,30]. ANNS system with high search throughput. Experiments
Ondisk,thebest-firstalgorithmincurshighsearchlatency show that PipeANN significantly bridges the latency gap
whenexploringonevectoratatime(i.e.,W=1).Therefore,
betweenin-memoryANNSandon-diskANNS.Thiswork
DiskANN[23]proposestousebeamsearch,whereitreads demonstratesthataligningthealgorithmwiththehardware
thebestkvectorsinparallelforeachsearchstep.Beamsearch characteristicsbringsperformancebenefits.
isalsousedbyiQAN[18]todointra-queryparallelismamong
multiplecores,whereeachcoreexploresonevector. Com-
paredtogreedysearch,beamsearchreducesthelatencybut Acknowledgments
stillfollowsabest-firstalgorithm,whichinducescompute-I/O
orderandlimitstheperformance. Wesincerelythankourshepherd,PatrickP.C.Lee,andthe
Some other works accelerate graph search by reducing anonymousreviewersfortheirvaluablefeedback.Thiswork
thelengthofthesearchpath,usingentrypointoptimization is supported by the National Key R&D Program of China
andearlytermination.LSH-APG[32]andStarling[25]opti- (GrantNo.2024YFE0203300),theNationalNaturalScience
mizethefixedentrypointusinganLSHtableorasub-graph. FoundationofChina(GrantNo.62332011),andBeijingNat-
Proxima[28]andlearnedadaptiveearlytermination[13]de- uralScienceFoundation(GrantNo.L242016).
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation 183

References
|           |               |           |     |        |           |     | [9] PiotrIndykandRajeev                         |         | Motwani. | Approximate |       | near-     |
| --------- | ------------- | --------- | --- | ------ | --------- | --- | ----------------------------------------------- | ------- | -------- | ----------- | ----- | --------- |
|           |               |           |     |        |           |     | est neighbors:                                  | towards | removing | the         | curse | of dimen- |
| [1] Ilias | Azizi, Karima | Echihabi, | and | Themis | Palpanas. |     |                                                 |         |          |             |       |           |
|           |               |           |     |        |           |     | sionality. InProceedingsoftheThirtiethAnnualACM |         |          |             |       |           |
Graph-Based VectorSearch: An Experimental Evalu- SymposiumonTheoryofComputing,STOC’98,pages
ation of the State-of-the-Art. In Proceedings of the 604–613,Dallas,TX,USA,1998.AssociationforCom-
| ACM | on Management | of  | Data,SIGMOD |     | ’25,Berlin, |     |     |     |     |     |     |     |
| --- | ------------- | --- | ----------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
putingMachinery.
Germany,2025.AssociationforComputingMachinery.
|     |     |     |     |     |     |     | [10] Hervé Jégou,Romain |     | Tavenard,Matthijs |     | Douze,and |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------------- | --- | ----------------- | --- | --------- | --- |
EfficientIn-
[2] ArtemBabenkoandVictorS.Lempitsky. LaurentAmsaleg. Searchinginonebillionvectors:re-
dexingofBillion-ScaleDatasetsofDeepDescriptors.In rankwithsourcecoding. In2011IEEEInternational
2016IEEEConferenceonComputerVisionandPattern ConferenceonAcoustics,SpeechandSignalProcessing,
Recognition,CVPR’16,pages2055–2063,LasVegas, ICASSP’11,pages861–864,Prague,CzechRepublic,
NV,USA,2016.IEEEComputerSociety.
2011.IEEEComputerSociety.
[3] PatrickChen,Wei-ChengChang,Jyun-YuJiang,Hsiang-
|     |     |     |     |     |     |     | [11] KanchanJoshi,AnujGupta,JavierGonzalez,AnkitKu- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- |
FuYu,InderjitDhillon,andCho-JuiHsieh. FINGER: mar,KrishnaKanthReddy,ArunGeorge,SimonLund,
FastInference forGraph-basedApproximate Nearest andJensAxboe. I/OPassthru:Upstreamingaflexible
NeighborSearch. InProceedingsoftheACMWebCon- andefficientI/OPathinLinux.In22ndUSENIXConfer-
ference2023,WWW’23,pages3225–3235,Austin,TX, enceonFileandStorageTechnologies,FAST’24,pages
USA,2023.AssociationforComputingMachinery. 107–121,SantaClara,CA,2024.USENIXAssociation.
[4] Qi Chen, Bing Zhao, Haidong Wang, Mingqin Li, [12] PatrickLewis,EthanPerez,AleksandraPiktus,Fabio
ChuanjieLiu,ZengzhongLi,MaoYang,andJingdong Petroni,VladimirKarpukhin,NamanGoyal,Heinrich
Wang. SPANN: highly-efficient billion-scale approx- Küttler,MikeLewis,Wen-tauYih,TimRocktäschel,Se-
| imate | nearestneighborsearch. |     |     | In Proceedings |     | ofthe |                              |     |     |                     |     |     |
| ----- | ---------------------- | --- | --- | -------------- | --- | ----- | ---------------------------- | --- | --- | ------------------- | --- | --- |
|       |                        |     |     |                |     |       | bastianRiedel,andDouweKiela. |     |     | Retrieval-augmented |     |     |
35thInternationalConferenceonNeuralInformation generationforknowledge-intensiveNLPtasks. InPro-
Processing Systems,NIPS ’21,Red Hook,NY,USA, ceedingsofthe34thInternationalConferenceonNeural
2021.CurranAssociatesInc. InformationProcessingSystems,NIPS’20,RedHook,
NY,USA,2020.CurranAssociatesInc.
[5] RongxinChen,YifanPeng,XingdaWei,HongruiXie,
RongChen,SijieShen,andHaiboChen. Characterizing [13] Conglong Li,Minjia Zhang,David G. Andersen,and
theDilemmaofPerformanceandIndexSizeinBillion- YuxiongHe. ImprovingApproximateNearestNeighbor
ScaleVectorSearchandBreakingItwithSecond-Tier Search through Learned Adaptive Early Termination.
Memory. CoRR,abs/2405.03267,2024. In Proceedings of the 2020 ACM SIGMOD Interna-
tionalConferenceonManagementofData,SIGMOD
[6] CongFu,ChaoXiang,ChangxuWang,andDengCai.
’20,pages2539–2554,Portland,OR,USA,2020.Asso-
Fastapproximatenearestneighborsearchwiththenavi-
ciationforComputingMachinery.
gatingspreading-outgraph.InProceedingsoftheVLDB
Endowment,VLDB’19,pages461–474,LosAngeles, [14] Jie Li, Haifeng Liu, Chuanghua Gui, Jianyu Chen,
CA,USA,2019.VLDBEndowment.
|     |     |     |     |     |     |     | Zhenyuan | Ni,Ning | Wang,and | Yuan | Chen. | The De- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------- | -------- | ---- | ----- | ------- |
signandImplementationofaRealTimeVisualSearch
| [7] Jianyang         | Gao and | Cheng   | Long. | RaBitQ:       | Quantiz- |     |                               |     |     |     |               |     |
| -------------------- | ------- | ------- | ----- | ------------- | -------- | --- | ----------------------------- | --- | --- | --- | ------------- | --- |
|                      |         |         |       |               |          |     | SystemonJDE-commercePlatform. |     |     |     | InProceedings |     |
| ing High-Dimensional |         | Vectors | with  | a Theoretical |          | Er- |                               |     |     |     |               |     |
ofthe19thInternationalMiddlewareConferenceIndus-
rorBoundforApproximateNearestNeighborSearch.
try,Middleware’18,pages9–16,Rennes,France,2018.
| In Proceedings | of  | the ACM | on Management |     | of  | Data, |     |     |     |     |     |     |
| -------------- | --- | ------- | ------------- | --- | --- | ----- | --- | --- | --- | --- | --- | --- |
AssociationforComputingMachinery.
| SIGMOD’24,Santiago,Chile,2024. |     |     |     | Associationfor |     |     |     |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
ComputingMachinery. [15] SenLi,FuyuLv,TaiweiJin,GuliLin,KepingYang,Xi-
|               |               |      |        |          |              |     | aoyiZeng,Xiao-MingWu,andQianliMa.    |     |     |     | Embedding- |     |
| ------------- | ------------- | ---- | ------ | -------- | ------------ | --- | ------------------------------------ | --- | --- | --- | ---------- | --- |
| [8] Siddharth | Gollapudi,    | Neel | Karia, | Varun    | Sivashankar, |     |                                      |     |     |     |            |     |
|               |               |      |        |          |              |     | basedProductRetrievalinTaobaoSearch. |     |     |     | InProceed- |     |
| Ravishankar   | Krishnaswamy, |      | Nikit  | Begwani, | Swapnil      |     |                                      |     |     |     |            |     |
ingsofthe27thACMSIGKDDConferenceonKnowl-
| Raz, | Yiyong Lin, | Yin | Zhang, | Neelam | Mahapatro, |     |     |     |     |     |     |     |
| ---- | ----------- | --- | ------ | ------ | ---------- | --- | --- | --- | --- | --- | --- | --- |
edgeDiscovery&DataMining,KDD’21,pages3181–
PremkumarSrinivasan,AmitSingh,andHarshaVard-
3189,VirtualEvent,2021.AssociationforComputing
| hanSimhadri. | Filtered-diskann:Graphalgorithmsfor |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Machinery.
| approximatenearestneighborsearchwithfilters. |     |     |     |     |     | InPro- |     |     |     |     |     |     |
| -------------------------------------------- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
EfficientandRobust
ceedingsoftheACMWebConference2023,WWW’23, [16] YuA.MalkovandD.A.Yashunin.
pages3406–3416,Austin,TX,USA,2023.Association ApproximateNearestNeighborSearchUsingHierarchi-
forComputingMachinery. calNavigableSmallWorldGraphs. IEEETransactions
184    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

onPatternAnalysisandMachineIntelligence(TPAMI), [25] Mengzhao Wang, Weizhi Xu, Xiaomeng Yi, Songlin
42(4):824–836,2020. Wu, Zhangyang Peng, Xiangyu Ke, Yunjun Gao, Xi-
TomásMikolov,KaiChen,GregCorrado,andJeffrey aoliangXu,RentongGuo,andCharlesXie. Starling:
[17]
AnI/O-EfficientDisk-ResidentGraphIndexFramework
| Dean. Efficient |     | Estimation | of Word | Representations |     |     |     |     |     |     |     |
| --------------- | --- | ---------- | ------- | --------------- | --- | --- | --- | --- | --- | --- | --- |
forHigh-DimensionalVectorSimilaritySearchonData
| in Vector | Space. | In 1st International |     | Conference | on  |     |     |     |     |     |     |
| --------- | ------ | -------------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
Segment.InProceedingsoftheACMonManagementof
LearningRepresentations,WorkshopTrackProceedings,
Data,SIGMOD’24,Santiago,Chile,2024.Association
ICLR’13,Scottsdale,Arizona,USA,2013.
forComputingMachinery.
| [18] Zhen Peng,Minjia |     | Zhang,Kai | Li,Ruoming |     | Jin,and |     |     |     |     |     |     |
| --------------------- | --- | --------- | ---------- | --- | ------- | --- | --- | --- | --- | --- | --- |
[26] MengzhaoWang,XiaoliangXu,QiangYue,andYuxi-
| BinRen. | iQAN:FastandAccurateVectorSearchwith |     |     |     |     |          |     |                                     |     |     |     |
| ------- | ------------------------------------ | --- | --- | --- | --- | -------- | --- | ----------------------------------- | --- | --- | --- |
|         |                                      |     |     |     |     | angWang. |     | Acomprehensivesurveyandexperimental |     |     |     |
EfficientIntra-QueryParallelismonMulti-CoreArchi-
comparisonofgraph-basedapproximatenearestneigh-
| tectures. | In Proceedings | of  | the 28th | ACM | SIGPLAN |            |     |                                  |     |     |     |
| --------- | -------------- | --- | -------- | --- | ------- | ---------- | --- | -------------------------------- | --- | --- | --- |
|           |                |     |          |     |         | borsearch. |     | InProceedingsoftheVLDBEndowment, |     |     |     |
AnnualSymposiumonPrinciplesandPracticeofParal-
VLDB’21,pages1964–1978,Copenhagen,Denmark,
lelProgramming,PPoPP’23,pages313–328,Montreal,
2021.VLDBEndowment.
QC,Canada,2023.AssociationforComputingMachin-
| ery. |     |     |     |     |     | [27] Chuangxian |     | Wei, Bin | Wu, Sheng Wang, | Renjie | Lou, |
| ---- | --- | --- | --- | --- | --- | --------------- | --- | -------- | --------------- | ------ | ---- |
ChaoqunZhan,FeifeiLi,andYuanzheCai.AnalyticDB-
[19] AlecRadford,JongWookKim,ChrisHallacy,Aditya
V:ahybridanalyticalenginetowardsqueryfusionfor
Ramesh,GabrielGoh,SandhiniAgarwal,GirishSastry,
|     |     |     |     |     |     | structured |     | and unstructured | data. In | Proceedings | of  |
| --- | --- | --- | --- | --- | --- | ---------- | --- | ---------------- | -------- | ----------- | --- |
AmandaAskell,PamelaMishkin,JackClark,Gretchen
theVLDBEndowment,VLDB’20,pages3152–3165,
| Krueger, | and Ilya | Sutskever. | Learning |     | Transferable |     |     |     |     |     |     |
| -------- | -------- | ---------- | -------- | --- | ------------ | --- | --- | --- | --- | --- | --- |
Tokyo,Japan,2020.VLDBEndowment.
| VisualModelsFromNaturalLanguageSupervision. |     |     |     |     | In  |     |     |     |     |     |     |
| ------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Proceedings of the 38th International Conference on [28] WeihongXu,JunweiChen,Po-KaiHsu,JaeyoungKang,
MachineLearning,ICML’21,pages8748–8763,Virtual
|     |     |     |     |     |     | Minxuan | Zhou,Sumukh |     | Pinge,Shimeng | Yu,and | Ta- |
| --- | --- | --- | --- | --- | --- | ------- | ----------- | --- | ------------- | ------ | --- |
Event,2021.PMLR.
|     |     |     |     |     |     | janaRosing. |     | Proxima: | Near-storageAccelerationfor |     |     |
| --- | --- | --- | --- | --- | --- | ----------- | --- | -------- | --------------------------- | --- | --- |
Graph-basedApproximateNearestNeighborSearchin
| [20] HarshaSimhadri. |     | ResultsoftheNeurIPS’21Challenge |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | ------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
CoRR,abs/2312.04257,2023.
| onBillion-ScaleApproximateNearestNeighborSearch. |     |     |     |     |     | 3DNAND. |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- |
InProceedingsofthe35thInternationalConferenceon
[29] YumingXu,HengyuLiang,JinLi,ShuotaoXu,QiChen,
NeuralInformationProcessingSystems,NIPS’21,Red
QianxiZhang,ChengLi,ZiyueYang,FanYang,Yuqing
Hook,NY,USA,2021.CurranAssociatesInc. Yang,PengCheng,andMaoYang. SPFresh:Incremen-
[21] HarshaSimhadri. Researchtalk:Approximatenearest talIn-PlaceUpdateforBillion-ScaleVectorSearch. In
Proceedingsofthe29thSymposiumonOperatingSys-
| neighborsearchsystemsatscale. |     |     | https://www.yout |     |     |     |     |     |     |     |     |
| ----------------------------- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- |
ube.com/watch?v=BnYNdSIKibQ&list=PLD7HFc tems Principles,SOSP ’23,pages 545–561,Koblenz,
N7LXReJTWFKYqwMcCc1nZKIXBo9&index=9,2022. Germany,2023.AssociationforComputingMachinery.
[22] Aditi Singh, Suhas Jayaram Subramanya, Ravis- [30] MingyuYang,JiabaoJin,XiangyuWang,ZhitaoShen,
|     |     |     |     |     |     | WeiJia,WentaoLi,andWeiWang. |     |     | EffectiveandGen- |     |     |
| --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | ---------------- | --- | --- |
hankarKrishnaswamy,andHarshaVardhanSimhadri.
FreshDiskANN: A Fast and Accurate Graph-Based eral Distance Computation for Approximate Nearest
ANN Index for Streaming Similarity Search. CoRR, NeighborSearch. CoRR,abs/2404.16322,2024.
abs/2105.09613,2021.
|     |     |     |     |     |     | [31] Qianxi | Zhang,Shuotao |     | Xu,Qi Chen,Guoxin |     | Sui,Ji- |
| --- | --- | --- | --- | --- | --- | ----------- | ------------- | --- | ----------------- | --- | ------- |
[23] SuhasJayaramSubramanya,Devvrit,RohanKadekodi, adong Xie, Zhizhen Cai, Yaoqi Chen, Yinxuan He,
Ravishankar Krishaswamy, and Harsha Vardhan YuqingYang,FanYang,MaoYang,andLidongZhou.
Simhadri. DiskANN:fastaccuratebillion-pointnearest VBASE:UnifyingOnlineVectorSimilaritySearchand
|                              |     |     |                    |     |     | RelationalQueriesviaRelaxedMonotonicity. |     |     |     | In17th |     |
| ---------------------------- | --- | --- | ------------------ | --- | --- | ---------------------------------------- | --- | --- | --- | ------ | --- |
| neighborsearchonasinglenode. |     |     | InProceedingsofthe |     |     |                                          |     |     |     |        |     |
33rdInternationalConferenceonNeuralInformation USENIXSymposiumonOperatingSystemsDesignand
Processing Systems,NIPS ’19,Red Hook,NY,USA, Implementation,OSDI’23,pages377–395,Boston,MA,
| 2019.CurranAssociatesInc. |     |     |     |     |     | USA,2023.USENIXAssociation. |     |     |     |     |     |
| ------------------------- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | --- | --- |
[24] BingTian,HaikunLiu,ZhuohuiDuan,XiaofeiLiao,Hai [32] XiZhao,YaoTian,KaiHuang,BolongZheng,andXi-
Efficient
Jin,andYuZhang. ScalableBillion-pointApproximate aofang Zhou. Towards Index Construction
NearestNeighborSearchUsingSmartSSDs. In2024 and Approximate Nearest Neighbor Search in High-
USENIXAnnualTechnicalConference,USENIXATC Dimensional Spaces. In Proceedings of the VLDB
’24,pages1135–1150,SantaClara,CA,2024.USENIX Endowment,VLDB’23,pages1979–1991,Vancouver,
| Association. |     |     |     |     |     | Canada,2023.VLDBEndowment. |     |     |     |     |     |
| ------------ | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- |
USENIX Association 19th USENIX Symposium on Operating Systems Design and Implementation    185

[33] XiaoyaoZhong,HaotianLi,JiabaoJin,MingyuYang,
| Deming                     | Chu, Xiangyu Wang, | Zhitao Shen,     | Wei Jia,  |
| -------------------------- | ------------------ | ---------------- | --------- |
| George                     | Gu, Yi Xie, Xuemin | Lin, Heng        | Tao Shen, |
| JingkuanSong,andPengCheng. |                    | VSAG:AnOptimized |           |
SearchFrameworkforGraph-basedApproximateNear-
CoRR,abs/2503.17911,2025.
estNeighborSearch.
186    19th USENIX Symposium on Operating Systems Design and Implementation USENIX Association