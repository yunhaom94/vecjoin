|     |     | Billion-scale      |         |     |     | similarity         |          | search |     | with               |        | GPUs   |     |     |     |
| --- | --- | ------------------ | ------- | --- | --- | ------------------ | -------- | ------ | --- | ------------------ | ------ | ------ | --- | --- | --- |
|     |     | Jeff               | Johnson |     |     |                    | Matthijs | Douze  |     |                    | Herve´ | Je´gou |     |     |     |
|     |     | FacebookAIResearch |         |     |     | FacebookAIResearch |          |        |     | FacebookAIResearch |        |        |     |     |     |
|     |     | NewYork            |         |     |     |                    | Paris    |        |     |                    |        | Paris  |     |     |     |
ABSTRACT
7102 beF 82  ]VC.sc[  1v43780.2071:viXra astheunderlyingprocesseseitherhavehigharithmeticcom-
plexityand/orhighdatabandwidthdemands[28],orcannot
| Similarity | search   | finds   | application | in   | specialized | database |         |                 |     |                   |         |         |       |             |      |
| ---------- | -------- | ------- | ----------- | ---- | ----------- | -------- | ------- | --------------- | --- | ----------------- | ------- | ------- | ----- | ----------- | ---- |
|            |          |         |             |      |             |          |         | be effectively  |     | partitioned       | without | failing | due   | to communi- |      |
| systems    | handling | complex | data        | such | as images   | or       | videos, |                 |     |                   |         |         |       |             |      |
|            |          |         |             |      |             |          |         | cation overhead |     | or representation |         | quality | [38]. | Once        | pro- |
whicharetypicallyrepresentedbyhigh-dimensionalfeatures
|             |          |           |           |             |      |            |         | duced, their    | manipulation |            | is      | itself arithmetically |                      | intensive. |     |
| ----------- | -------- | --------- | --------- | ----------- | ---- | ---------- | ------- | --------------- | ------------ | ---------- | ------- | --------------------- | -------------------- | ---------- | --- |
| and require | specific | indexing  |           | structures. | This | paper      | tackles |                 |              |            |         |                       |                      |            |     |
|             |          |           |           |             |      |            |         | However,        | how          | to utilize | GPU     | assets is             | not straightforward. |            |     |
| the problem |          | of better | utilizing | GPUs        | for  | this task. | While   |                 |              |            |         |                       |                      |            |     |
|             |          |           |           |             |      |            |         | More generally, |              | how to     | exploit | new heterogeneous     |                      | architec-  |     |
GPUsexcelatdata-paralleltasks,priorapproachesarebot-
|     |     |     |     |     |     |     |     | tures is | a key subject |     | for the | database | community | [9]. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------------- | --- | ------- | -------- | --------- | ---- | --- |
tleneckedbyalgorithmsthatexposelessparallelism,suchas
k-minselection,ormakepooruseofthememoryhierarchy. In this context, searching by numerical similarity rather
We propose a design for k-selection that operates at up thanviastructuredrelationsismoresuitable. Thiscouldbe
|        |                |     |                   |     |          |     |         | to find the | most      | similar | content | to a picture, |      | or to             | find the |
| ------ | -------------- | --- | ----------------- | --- | -------- | --- | ------- | ----------- | --------- | ------- | ------- | ------------- | ---- | ----------------- | -------- |
| to 55% | of theoretical |     | peak performance, |     | enabling | a   | nearest |             |           |         |         |               |      |                   |          |
|        |                |     |                   |     |          |     |         | vectors     | that have | the     | highest | response      | to a | linear classifier |          |
neighborimplementationthatis8.5×fasterthanpriorGPU
|          |     |         |       |                 |     |            |        | on all vectors | of  | a collection. |     |     |     |     |     |
| -------- | --- | ------- | ----- | --------------- | --- | ---------- | ------ | -------------- | --- | ------------- | --- | --- | --- | --- | --- |
| state of | the | art. We | apply | it in different |     | similarity | search |                |     |               |     |     |     |     |     |
Oneofthemostexpensiveoperationstobeperformedon
scenarios,byproposingoptimizeddesignforbrute-force,ap-
|     |     |     |     |     |     |     |     | largecollectionsistocomputeak-NNgraph. |     |     |     |     |     | Itisadirected |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------- | --- | --- | --- | --- | --- | ------------- | --- |
proximateandcompressed-domainsearchbasedonproduct
graphwhereeachvectorofthedatabaseisanodeandeach
| quantization. |          | Inallthesesetups,weoutperformthestateof |          |                |       |          |         |                         |      |        |                               |           |            |     |         |
| ------------- | -------- | --------------------------------------- | -------- | -------------- | ----- | -------- | ------- | ----------------------- | ---- | ------ | ----------------------------- | --------- | ---------- | --- | ------- |
|               |          |                                         |          |                |       |          |         | edge connects           |      | a node | to its                        | k nearest | neighbors. |     | This is |
| the art       | by large | margins.                                | Our      | implementation |       | enables  | the     |                         |      |        |                               |           |            |     |         |
|               |          |                                         |          |                |       |          |         | ourflagshipapplication. |      |        | Note,stateoftheartmethodslike |           |            |     |         |
| construction  |          | of a high                               | accuracy | k-NN           | graph | on 95    | million |                         |      |        |                               |           |            |     |         |
|               |          |                                         |          |                |       |          |         | NN-Descent              | [15] | have   | a large                       | memory    | overhead   | on  | top of  |
| images        | from     | the Yfcc100M                            |          | dataset        | in 35 | minutes, | and of  |                         |      |        |                               |           |            |     |         |
a graph connecting 1 billion vectors in less than 12 hours thedatasetitselfandcannotreadilyscaletothebillion-sized
on 4 Maxwell Titan X GPUs. We have open-sourced our databases we consider.
| approach1 |     |          |               |     |     |                  |     | Suchapplicationsmustdealwiththecurse |                |      |            |             |     | of dimension- |        |
| --------- | --- | -------- | ------------- | --- | --- | ---------------- | --- | ------------------------------------ | -------------- | ---- | ---------- | ----------- | --- | ------------- | ------ |
|           | for | the sake | of comparison |     | and | reproducibility. |     |                                      |                |      |            |             |     |               |        |
|           |     |          |               |     |     |                  |     | ality [46],                          | rendering      | both | exhaustive | search      |     | or exact      | index- |
|           |     |          |               |     |     |                  |     | ing for                              | non-exhaustive |      | search     | impractical | on  | billion-scale |        |
1. INTRODUCTION
|     |     |     |     |     |     |     |     | databases. | This | is why | there | is a large | body | of work | on  |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---- | ------ | ----- | ---------- | ---- | ------- | --- |
Imagesandvideosconstituteanewmassivesourceofdata approximate search and/or graph construction. To handle
for indexing and search. Extensive metadata for this con- huge datasets that do not fit in RAM, several approaches
tentisoftennotavailable. Searchandinterpretationofthis employ an internal compressed representation of the vec-
andotherhuman-generatedcontent,liketext,isdifficultand tors using an encoding. This is especially convenient for
important. A variety of machine learning and deep learn- memory-limiteddeviceslikeGPUs. Itturnsoutthataccept-
ingalgorithmsarebeingusedtointerpretandclassifythese
|          |            |           |     |         |          |         |     | ing a minimal  |     | accuracy  | loss | results in | orders | of magnitude |     |
| -------- | ---------- | --------- | --- | ------- | -------- | ------- | --- | -------------- | --- | --------- | ---- | ---------- | ------ | ------------ | --- |
| complex, | real-world | entities. |     | Popular | examples | include | the |                |     |           |      |            |        |              |     |
|          |            |           |     |         |          |         |     | of compression |     | [21]. The | most | popular    | vector | compression  |     |
textrepresentationknownasword2vec[32],representations
|     |     |     |     |     |     |     |     | methods | can be | classified | into | either | binary | codes | [18, 22], |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------ | ---------- | ---- | ------ | ------ | ----- | --------- |
ofimagesbyconvolutionalneuralnetworks[39,19],andim-
|     |     |     |     |     |     |     |     | or quantization |     | methods | [25, | 37]. Both | have | the desirable |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ------- | ---- | --------- | ---- | ------------- | --- |
agedescriptorsforinstancesearch[20]. Suchrepresentations property that searching neighbors does not require recon-
orembeddings areusuallyreal-valued,high-dimensionalvec- structing the vectors.
torsof50to1000+dimensions. Manyofthesevectorrepre- Our paper focuses on methods based on product quanti-
sentationscanonlyeffectivelybeproducedonGPUsystems, zation(PQ)codes,asthesewereshowntobemoreeffective
|     |     |     |     |     |     |     |     | than binary | codes | [34]. | In addition, | binary | codes | incur | im- |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ----- | ----- | ------------ | ------ | ----- | ----- | --- |
1https://github.com/facebookresearch/faiss
|     |     |     |     |     |     |     |     | portant | overheads | for | non-exhaustive |     | search | methods | [35]. |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --------- | --- | -------------- | --- | ------ | ------- | ----- |
Severalimprovementswereproposedaftertheoriginalprod-
uctquantizationproposalknownasIVFADC[25];mostare
|     |     |     |     |     |     |     |     | difficult | to implement |     | efficiently | on GPU.                    | For | instance, | the |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------------ | --- | ----------- | -------------------------- | --- | --------- | --- |
|     |     |     |     |     |     |     |     | inverted  | multi-index  |     | [4], useful | for high-speed/low-quality |     |           |     |
operatingpoints,dependsonacomplicated“multi-sequence”
|     |     |     |     |     |     |     |     | algorithm. | TheoptimizedproductquantizationorOPQ[17] |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---------------------------------------- | --- | --- | --- | --- | --- | --- |
isalineartransformationontheinputvectorsthatimproves
|     |     |     |     |     |     |     |     | the accuracy | of  | the product |     | quantization; | it  | can be | applied |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ----------- | --- | ------------- | --- | ------ | ------- |
1

as a pre-processing. The SIMD-optimized IVFADC imple- Exact search. The exact solution computes the full pair-
mentationfrom[2]operatesonlywithsub-optimalparame- wise distance matrix D = [(cid:107)x −y (cid:107)2] ∈ Rnq×(cid:96).
j i 2 j=0:nq,i=0:(cid:96)
ters (few coarse quantization centroids). Many other meth- In practice, we use the decomposition
ods, like LOPQ and the Polysemous codes [27, 16] are too
complex to be implemented efficiently on GPUs.
(cid:107)x −y (cid:107)2 =(cid:107)x (cid:107)2+(cid:107)y (cid:107)2−2(cid:104)x ,y (cid:105). (2)
There are many implementations of similarity search on j i 2 j i j i
GPUs,butmostlywithbinarycodes[36],smalldatasets[44], The two first terms can be precomputed in one pass over
or exhaustive search [14, 40, 41]. To the best of our knowl- thematricesX andY whoserowsarethe[x ]and[y ]. The
j i
edge, only the work by Wieschollek et al. [47] appears suit- bottleneck is to evaluate (cid:104)x ,y (cid:105), equivalent to the matrix
j i
ableforbillion-scaledatasetswithquantizationcodes. This multiplication XY(cid:62). The k-nearest neighbors for each of
is the prior state of the art on GPUs, which we compare the n queries are k-selected along each row of D.
q
against in Section 6.4.
Compressed-domain search. From now on, we focus on
This paper makes the following contributions: approximate nearest-neighbor search. We consider, in par-
ticular,theIVFADC indexingstructure[25]. TheIVFADC
• aGPUk-selectionalgorithm,operatinginfastregister index relies on two levels of quantization, and the database
memory and flexible enough to be fusable with other vectorsareencoded. Thedatabasevectoryisapproximated
kernels, for which we provide a complexity analysis; as:
• a near-optimal algorithmic layout for exact and ap- y≈q(y)=q 1 (y)+q 2 (y−q 1 (y)) (3)
proximate k-nearest neighbor search on GPU; where q :Rd →C ⊂Rd and q :Rd →C ⊂Rd are quan-
1 1 2 2
tizers; i.e., functions that output an element from a finite
• a range of experiments that show that these improve-
set. Sincethesetsarefinite,q(y)isencodedastheindexof
ments outperform previous art by a large margin on
q (y)andthatofq (y−q (y)). Thefirst-levelquantizerisa
mid- to large-scale nearest-neighbor search tasks, in 1 2 1
coarsequantizer andthesecondlevelfinequantizer encodes
single or multi-GPU configurations.
the residual vector after the first level.
The paper is organized as follows. Section 2 introduces The Asymmetric Distance Computation (ADC) search
the context and notation. Section 3 reviews GPU archi- method returns an approximate result:
tecture and discusses problems appearing when using it for
L =k-argmin (cid:107)x−q(y )(cid:107) . (4)
similaritysearch. Section4introducesoneofourmaincon- ADC i=0:(cid:96) i 2
tributions,i.e.,ourk-selectionmethodforGPUs,whileSec- For IVFADC the search is not exhaustive. Vectors for
tion5providesdetailsregardingthealgorithmcomputation which the distance is computed are pre-selected depending
layout. Finally,Section6providesextensiveexperimentsfor on the first-level quantizer q 1 :
ourapproach,comparesittothestateoftheart,andshows
L =τ-argmin (cid:107)x−c(cid:107) . (5)
concrete use cases for image collections. IVF c∈C1 2
The multi-probe parameter τ is the number of coarse-level
2. PROBLEMSTATEMENT centroids we consider. The quantizer operates a nearest-
neighborsearchwithexactdistances,inthesetofreproduc-
We are concerned with similarity search in vector collec-
tion values. Then, the IVFADC search computes
tions. Given the query vector x ∈ Rd and the collection2
[y ] (y ∈Rd), we search:
i i=0:(cid:96) i
L = k-argmin (cid:107)x−q(y )(cid:107) . (6)
IVFADC i 2
L=k-argmin (cid:107)x−y (cid:107) , (1)
i=0:(cid:96) i 2 i=0:(cid:96)s.t. q1(yi)∈LIVF
i.e., we search the k nearest neighbors of x in terms of L2 Hence, IVFADC relies on the same distance estimations as
distance. The L2 distance is used most often, as it is op- thetwo-stepquantizationofADC,butcomputesthemonly
timized by design when learning several embeddings (e.g., on a subset of vectors.
[20]), due to its attractive linear algebra properties. Thecorrespondingdatastructure,theinvertedfile,groups
The lowest distances are collected by k-selection. For an thevectorsy i into|C 1 |inverted lists I 1 ,...,I |C1| withhomo-
array[a i ] i=0:(cid:96) ,k-selectionfindstheklowestvaluedelements geneous q 1 (y i ). Therefore, the most memory-intensive op-
[a si ] i=0:k , a si ≤ a si+1 , along with the indices [s i ] i=0:k , 0 ≤ eration is computing L IVFADC , and boils down to linearly
s <(cid:96),ofthoseelementsfromtheinputarray. Thea willbe scanning τ inverted lists.
i i
32-bitfloatingpointvalues;thes are32-or64-bitintegers.
i The quantizers. The quantizers q and q have different
Other comparators are sometimes desired; e.g., for cosine 1 2
properties. q needstohavearelativelylownumberofrepro-
similarity we search for highest values. The order between 1
ductionvaluessothatthenumber√ofinvertedlistsdoesnot
equivalent keys a =a is not specified.
si sj explode. We typically use |C
1
| ≈ (cid:96), trained via k-means.
Batching. Typically, searches are performed in batches Forq 2 ,wecanaffordtospendmorememoryforamoreex-
of n query vectors [x ] (x ∈ Rd) in parallel, which tensive representation. The ID of the vector (a 4- or 8-byte
q j j=0:nq j
allows for more flexibility when executing on multiple CPU integer) is also stored in the inverted lists, so it makes no
threadsoronGPU.Batchingfork-selectionentailsselecting sensetohaveshortercodesthanthat;i.e.,log 2 |C 2 |>4×8.
n ×k elementsandindicesfromn separatearrays,where
q q Productquantizer. Weuseaproductquantizer [25]forq ,
2
each array is of a potentially different length (cid:96) ≥k.
i whichprovidesalargenumberofreproductionvalueswith-
2To avoid clutter in 0-based indexing, we use the array no- outincreasingtheprocessingcost. Itinterpretsthevectory
tation 0:(cid:96) to denote the range {0,...,(cid:96)−1} inclusive. asbsub-vectorsy=[y0...yb−1],wherebisanevendivisorof
2

the dimension d. Each sub-vector is quantized with its own opposed to 32, then only 1–2 other blocks can run concur-
quantizer, yielding the tuple (q0(y0), ..., qb−1(yb−1)). The rently on the same SM, resulting in low occupancy. Under
sub-quantizerstypicallyhave256reproductionvalues,tofit high occupancy more blocks will be present across all SMs,
inonebyte. Thequantizationvalueoftheproductquantizer allowing more work to be in flight at once.
(y)=q0(y0)+256×q1(y1)+...+256b−1×qb−1,
is then q 2
|                                            |           |           |             |              |            |                |       | Memorytypes.  |              | Differentblocksandkernelscommunicate |                        |          |         |       |           |
| ------------------------------------------ | --------- | --------- | ----------- | ------------ | ---------- | -------------- | ----- | ------------- | ------------ | ------------------------------------ | ---------------------- | -------- | ------- | ----- | --------- |
| which from                                 | a         | storage   | point       | of view      | is just    | the concatena- |       |               |              |                                      |                        |          |         |       |           |
|                                            |           |           |             |              |            |                |       | throughglobal |              | memory,                              | typically4–32GBinsize, |          |         |       | with5–    |
| tionofthebytesproducedbyeachsub-quantizer. |           |           |             |              |            | Thus,the       |       |               |              |                                      |                        |          |         |       |           |
|                                            |           |           |             |              |            |                |       | 10× higher    | bandwidth    |                                      | than                   | CPU main | memory. |       | Shared    |
| product                                    | quantizer | generates |             | b-byte       | codes with | |C | =         | 256b  |               |              |                                      |                        |          |         |       |           |
|                                            |           |           |             |              |            | 2              |       | memory        | is analogous |                                      | to CPU                 | L1 cache | in      | terms | of speed. |
| reproduction                               | values.   |           | The k-means | dictionaries |            | of the         | quan- |               |              |                                      |                        |          |         |       |           |
GPUregisterfilememoryisthehighestbandwidthmemory.
tizersaresmallandquantizationiscomputationallycheap.
Inordertomaintainthehighnumberofinstructionsinflight
|     |     |     |     |     |     |     |     | onaGPU,avastregisterfileisalsorequired: |     |     |     |     |     | 14MBinthe |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------- | --- | --- | --- | --- | --- | --------- | --- |
3. GPU:OVERVIEWANDK-SELECTION
|     |     |     |     |     |     |     |     | latest Pascal | P100, | in  | contrast | with | a few | tens of | KB on |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | ----- | --- | -------- | ---- | ----- | ------- | ----- |
This section reviews salient details of Nvidia’s general- CPU.Aratioof250:6.25:1forregistertosharedtoglobal
purposeGPUarchitectureandprogrammingmodel[30]. We memory aggregate cross-sectional bandwidth is typical on
thenfocusononeofthelessGPU-compliantpartsinvolved GPU, yielding 10–100s of TB/s for the register file [10].
insimilaritysearch,namelythek-selection,anddiscussthe
|            |     |             |     |     |     |     |     | 3.2 GPUregisterfileusage |          |     |       |        |     |          |        |
| ---------- | --- | ----------- | --- | --- | --- | --- | --- | ------------------------ | -------- | --- | ----- | ------ | --- | -------- | ------ |
| literature | and | challenges. |     |     |     |     |     |                          |          |     |       |        |     |          |        |
|            |     |             |     |     |     |     |     | Structured               | register |     | data. | Shared | and | register | memory |
3.1 Architecture
usageinvolvesefficiencytradeoffs;theyloweroccupancybut
GPU lanes and warps. The Nvidia GPU is a general- canincreaseoverallperformancebyretainingalargerwork-
purpose computer that executes instruction streams using ing set in a faster memory. Making heavy use of register-
a 32-wide vector of CUDA threads (the warp); individual resident data at the expense of occupancy or instead of
threads in the warp are referred to as lanes, with a lane shared memory is often profitable [43].
|         |           |            |     |           |              |         |      | As the    | GPU            | register  | file is   | very large, | storing    | structured |          |
| ------- | --------- | ---------- | --- | --------- | ------------ | ------- | ---- | --------- | -------------- | --------- | --------- | ----------- | ---------- | ---------- | -------- |
| ID from | 0–31.     | Despite    | the | “thread”  | terminology, | the     | best |           |                |           |           |             |            |            |          |
|         |           |            |     |           |              |         |      | data (not | just temporary |           | operands) |             | is useful. | A single   | lane     |
| analogy | to modern | vectorized |     | multicore | CPUs         | is that | each |           |                |           |           |             |            |            |          |
|         |           |            |     |           |              |         |      | can use   | its (scalar)   | registers | to        | solve       | a local    | task,      | but with |
warpisaseparateCPUhardwarethread,asthewarpshares
|                |     |          |      |       |                  |        |     | limited | parallelism | and | storage. | Instead, |     | lanes in | a GPU |
| -------------- | --- | -------- | ---- | ----- | ---------------- | ------ | --- | ------- | ----------- | --- | -------- | -------- | --- | -------- | ----- |
| an instruction |     | counter. | Warp | lanes | taking different | execu- |     |         |             |     |          |          |     |          |       |
warpcaninsteadexchangeregisterdatausingthewarpshuf-
tionpathsresultsinwarpdivergence,reducingperformance.
|     |     |     |     |     |     |     |     | fle instruction,enablingwarp-wideparallelismandstorage. |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
Eachlanehasupto25532-bitregistersinasharedregister
| file. The | CPU | analogy | is that | there | are up | to 255 | vector |                           |     |     |     |                         |     |     |     |
| --------- | --- | ------- | ------- | ----- | ------ | ------ | ------ | ------------------------- | --- | --- | --- | ----------------------- | --- | --- | --- |
|           |     |         |         |       |        |        |        | Lane-strideregisterarray. |     |     |     | Acommonpatterntoachieve |     |     |     |
registersofwidth32,withwarplanesasSIMDvectorlanes.
|             |           |        |         |                   |              |            |      | this is a                  | lane-stride                                   | register | array.        | That | is,                   | given  | elements  |
| ----------- | --------- | ------ | ------- | ----------------- | ------------ | ---------- | ---- | -------------------------- | --------------------------------------------- | -------- | ------------- | ---- | --------------------- | ------ | --------- |
|             |           |        |         |                   |              |            |      | [a ]                       | ,eachsuccessivevalueisheldinaregisterbyneigh- |          |               |      |                       |        |           |
| Collections | of        | warps. | A       | user-configurable |              | collection | of 1 | i i=0:(cid:96)             |                                               |          |               |      |                       |        |           |
|             |           |        |         |                   |              |            |      | boring lanes.              | The                                           | array    | is stored     | in   | (cid:96)/32 registers |        | per lane, |
| to 32 warps | comprises |        | a block | or a              | co-operative | thread     | ar-  |                            |                                               |          |               |      |                       |        |           |
|             |           |        |         |                   |              |            |      | with(cid:96)amultipleof32. |                                               |          | Lanejstores{a |      | ,a                    | ,...,a | },        |
ray (CTA).Eachblockhasahighspeedsharedmemory,up j 32+j (cid:96)−32+j
|     |     |     |     |     |     |     |     | while register | r   | holds | {a ,a | ,...,a |     | }.  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ----- | ----- | ------ | --- | --- | --- |
to 48KiB in size. Individual CUDA threads have a block- 32r 32r+1 32r+31
|     |     |     |     |     |     |     |     | Formanipulatingthe[a |     |     | ],theregisterinwhicha |     |     |     | isstored |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | --------------------- | --- | --- | --- | -------- |
relative ID, called a thread id, which can be used to parti- i i
|          |        |       |      |          |          |             |     | (i.e., (cid:98)i/32(cid:99)) | and | (cid:96) must | be known | at  | assembly | time, | while |
| -------- | ------ | ----- | ---- | -------- | -------- | ----------- | --- | ---------------------------- | --- | ------------- | -------- | --- | -------- | ----- | ----- |
| tion and | assign | work. | Each | block is | run on a | single core | of  |                              |     |               |          |     |          |       |       |
the GPU called a streaming multiprocessor (SM). Each SM thelane(i.e.,imod32)canberuntimeknowledge. Awide
has functional units, including ALUs, memory load/store variety of access patterns (shift, any-to-any) are provided;
units, and various special instruction units. A GPU hides we use the butterfly permutation [29] extensively.
| execution          | latencies  | by      | having                            | many         | operations | in flight     | on  |                               |               |           |                    |           |             |             |              |
| ------------------ | ---------- | ------- | --------------------------------- | ------------ | ---------- | ------------- | --- | ----------------------------- | ------------- | --------- | ------------------ | --------- | ----------- | ----------- | ------------ |
|                    |            |         |                                   |              |            |               |     | 3.3 k-selectiononCPUversusGPU |               |           |                    |           |             |             |              |
| warpsacrossallSMs. |            |         | Eachindividualwarplaneinstruction |              |            |               |     |                               |               |           |                    |           |             |             |              |
|                    |            |         |                                   |              |            |               |     | k-selection                   | algorithms,   |           | often              | for       | arbitrarily | large       | (cid:96) and |
| throughput         | is         | low and | latency                           | is high,     | but        | the aggregate |     |                               |               |           |                    |           |             |             |              |
|                    |            |         |                                   |              |            |               |     | k, can                        | be translated |           | to a GPU,          | including |             | radix       | selection    |
| arithmetic         | throughput |         | of all                            | SMs together | is         | 5–10× higher  |     |                               |               |           |                    |           |             |             |              |
|                    |            |         |                                   |              |            |               |     | and bucket                    | selection     |           | [1], probabilistic |           | selection   | [33],       | quick-       |
| than typical       | CPUs.      |         |                                   |              |            |               |     |                               |               |           |                    |           |             |             |              |
|                    |            |         |                                   |              |            |               |     | select [14],                  | and           | truncated | sorts              | [40].     | Their       | performance | is           |
Gridsandkernels. Blocksareorganizedinagridofblocks dominatedbymultiplepassesovertheinputinglobalmem-
| in a kernel. | Each | block | is assigned |     | a grid relative | ID. | The |                                                        |     |     |     |     |     |     |     |
| ------------ | ---- | ----- | ----------- | --- | --------------- | --- | --- | ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
|              |      |       |             |     |                 |     |     | ory. Sometimesforsimilaritysearch,theinputdistancesare |     |     |     |     |     |     |     |
kernel is the unit of work (instruction stream with argu- computed on-the-fly or stored only in small blocks, not in
ments)scheduledbythehostCPUfortheGPUtoexecute. their entirety. The full, explicit array might be too large to
After a block runs through to completion, new blocks can fit into any memory, and its size could be unknown at the
bescheduled. Blocksfromdifferentkernelscanrunconcur- start of the processing, rendering algorithms that require
rently. Orderingbetweenkernelsiscontrollableviaordering multiple passes impractical. They suffer from other issues
primitives such as streams and events. as well. Quickselect requires partitioning on a storage of
|                        |     |     |     |                          |     |     |     | size O((cid:96)), | a data-dependent |     |     | memory | movement. |     | This can |
| ---------------------- | --- | --- | --- | ------------------------ | --- | --- | --- | ----------------- | ---------------- | --- | --- | ------ | --------- | --- | -------- |
| Resourcesandoccupancy. |     |     |     | Thenumberofblocksexecut- |     |     |     |                   |                  |     |     |        |           |     |          |
resultinexcessivememorytransactions,orrequiringparallel
ingconcurrentlydependsuponsharedmemoryandregister prefixsumstodeterminewriteoffsets,withsynchronization
resourcesusedbyeachblock. Per-CUDAthreadregisterus- overhead. Radix selection has no partitioning but multiple
ageisdeterminedatcompilationtime,whilesharedmemory
|           |     |        |             |      |       |         |       | passes are | still | required. |     |     |     |     |     |
| --------- | --- | ------ | ----------- | ---- | ----- | ------- | ----- | ---------- | ----- | --------- | --- | --- | --- | --- | --- |
| usage can | be  | chosen | at runtime. | This | usage | affects | occu- |            |       |           |     |     |     |     |     |
pancy ontheGPU.Ifablockdemandsall48KiBofshared Heap parallelism. In similarity search applications, one
memory for its private usage, or 128 registers per thread as is usually interested only in a small number of results, k <
3

1000orso. Inthisregime,selectionviamax-heapisatypi- Algorithm 1 Odd-size merging network
cal choice on the CPU, but heaps do not expose much data merge-odd([L
|             |      |           |      |         |     |        |          | function |          |                      |     | i ] i=0:(cid:96)L ,[R | i ] i=0:(cid:96)R | )   |     |
| ----------- | ---- | --------- | ---- | ------- | --- | ------ | -------- | -------- | -------- | -------------------- | --- | --------------------- | ----------------- | --- | --- |
| parallelism | (due | to serial | tree | update) | and | cannot | saturate |          |          |                      |     |                       |                   |     |     |
|             |      |           |      |         |     |        |          |          | parallel | for i←0:min((cid:96) |     | L ,(cid:96)           | R ) do            |     |     |
SIMDexecutionunits. Thead-heap [31]takesbetteradvan- (cid:46) inverted 1st stage; inputs are already sorted
tage of parallelism available in heterogeneous systems, but compare-swap(L ,R )
|                |           |           |        |         |          |        |           |     |          |     | (cid:96)L−i−1 |     | i   |     |     |
| -------------- | --------- | --------- | ------ | ------- | -------- | ------ | --------- | --- | -------- | --- | ------------- | --- | --- | --- | --- |
| still attempts | to        | partition | serial | and     | parallel | work   | between   |     | end for  |     |               |     |     |     |     |
| appropriate    | execution |           | units. | Despite | the      | serial | nature of |     | parallel | do  |               |     |     |     |     |
heap update, for small k the CPU can maintain all of its (cid:46)If(cid:96) =(cid:96) andapower-of-2,theseareequivalent
|     |     |     |     |     |     |     |     |     |     | L R |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
stateintheL1cachewithlittleeffort,andL1cachelatency merge-odd-continue([L ] , left)
i i=0:(cid:96)L
and bandwidth remains a limiting factor. Other similarity merge-odd-continue([R ] , right)
i i=0:(cid:96)R
searchcomponents,likePQcodemanipulation,tendtohave
|         |        |        |             |     |      |     |     |     | end do |     |     |     |     |     |     |
| ------- | ------ | ------ | ----------- | --- | ---- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
| greater | impact | on CPU | performance |     | [2]. |     |     |     |        |     |     |     |     |     |     |
end function
merge-odd-continue([x
|            |          |                                  |     |              |     |             |      | function |                                     |      |     |     | i ] i=0:(cid:96) | ,p)        |           |
| ---------- | -------- | -------------------------------- | --- | ------------ | --- | ----------- | ---- | -------- | ----------------------------------- | ---- | --- | --- | ---------------- | ---------- | --------- |
| GPU heaps. |          | Heaps                            | can | be similarly |     | implemented | on a |          |                                     |      |     |     |                  |            |           |
|            |          |                                  |     |              |     |             |      |          | if (cid:96)>1                       | then |     |     |                  |            |           |
| GPU[7].    | However, | astraightforwardGPUheapimplemen- |     |              |     |             |      |          |                                     |      |     |     |                  |            |           |
|            |          |                                  |     |              |     |             |      |          | h←2(cid:100)log2(cid:96)(cid:101)−1 |      |     |     | (cid:46) largest | power-of-2 | <(cid:96) |
tationsuffersfromhighwarpdivergenceandirregular,data-
|     |     |     |     |     |     |     |     |     | parallel | for | i←0:(cid:96)−h |     | do  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | -------------- | --- | --- | --- | --- |
dependentmemorymovement,sincethepathtakenforeach
|          |         |         |      |       |        |        |       |     |     | (cid:46) Implemented |     | with | warp | shuffle butterfly |     |
| -------- | ------- | ------- | ---- | ----- | ------ | ------ | ----- | --- | --- | -------------------- | --- | ---- | ---- | ----------------- | --- |
| inserted | element | depends | upon | other | values | in the | heap. |     |     |                      |     |      |      |                   |     |
|          |         |         |      |       |        |        |       |     |     | compare-swap(x       |     | ,x   | )    |                   |     |
GPU parallel priority queues [24] improve over the serial i i+h
|             |     |          |          |     |            |          |     |     | end      | for |     |     |     |     |     |
| ----------- | --- | -------- | -------- | --- | ---------- | -------- | --- | --- | -------- | --- | --- | --- | --- | --- | --- |
| heap update | by  | allowing | multiple |     | concurrent | updates, | but |     |          |     |     |     |     |     |     |
|             |     |          |          |     |            |          |     |     | parallel | do  |     |     |     |     |     |
theyrequireapotentialnumberofsmallsortsforeachinsert
|     |     |     |     |     |     |     |     |     |     | if p = left | then |     | (cid:46) | left side recursion |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ---- | --- | -------- | ------------------- | --- |
and data-dependent memory movement. Moreover, it uses merge-odd-continue([x
|     |     |     |     |     |     |     |     |     |     |     |     |     | i   | ] i=0:(cid:96)−h ,left) |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------- | --- |
multiplesynchronizationbarriersthroughkernellaunchesin merge-odd-continue([x
|           |          |      |     |            |         |     |            |     |     |      |     |     | i              | ] i=(cid:96)−h:(cid:96) ,right) |     |
| --------- | -------- | ---- | --- | ---------- | ------- | --- | ---------- | --- | --- | ---- | --- | --- | -------------- | ------------------------------- | --- |
| different | streams, | plus | the | additional | latency | of  | successive |     |     |      |     |     |                |                                 |     |
|           |          |      |     |            |         |     |            |     |     | else |     |     | (cid:46) right | side recursion                  |     |
kernel launches and coordination with the CPU host. merge-odd-continue([x
|                                                 |     |     |     |     |     |     |     |     |     |                       |     |     | i   | ] ,left)  |     |
| ----------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------------- | --- | --- | --- | --------- | --- |
| OthermorenovelGPUalgorithmsareavailableforsmall |     |     |     |     |     |     |     |     |     |                       |     |     |     | i=0:h     |     |
|                                                 |     |     |     |     |     |     |     |     |     | merge-odd-continue([x |     |     |     | ] ,right) |     |
k, namely the selection algorithm in the fgknn library [41]. i i=h:(cid:96)
end if
Thisisacomplexalgorithmthatmaysufferfromtoomany
|                 |     |         |         |        |        |           |     |     | end    | do  |     |     |     |     |     |
| --------------- | --- | ------- | ------- | ------ | ------ | --------- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
| synchronization |     | points, | greater | kernel | launch | overhead, | us- |     |        |     |     |     |     |     |     |
|                 |     |         |         |        |        |           |     |     | end if |     |     |     |     |     |     |
ageofslowermemories,excessiveuseofhierarchy,partition-
end function
| ing and       | buffering. | However, |            | we take | inspiration |          | from this |                                    |     |     |     |     |     |             |     |
| ------------- | ---------- | -------- | ---------- | ------- | ----------- | -------- | --------- | ---------------------------------- | --- | --- | --- | --- | --- | ----------- | --- |
| particular    | algorithm  |          | through    | the     | use of      | parallel | merges as |                                    |     |     |     |     |     |             |     |
| seen in their | merge      | queue    | structure. |         |             |          |           |                                    |     |     |     |     |     |             |     |
|               |            |          |            |         |             |          |           | Odd-sizemergingandsortingnetworks. |     |     |     |     |     | Ifsomeinput |     |
4. FASTK-SELECTIONONTHEGPU data is already sorted, we can modify the network to avoid
|     |     |     |     |     |     |     |     | mergingsteps. |     | Wemayalsonothaveafullpower-of-2setof |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ------------------------------------ | --- | --- | --- | --- | --- |
ForanyCPUorGPUalgorithm,eithermemoryorarith-
|                  |     |        |     |              |     |           |         | data,       | in which | case | we can | efficiently | shortcut | to deal | with |
| ---------------- | --- | ------ | --- | ------------ | --- | --------- | ------- | ----------- | -------- | ---- | ------ | ----------- | -------- | ------- | ---- |
| metic throughput |     | should | be  | the limiting |     | factor as | per the |             |          |      |        |             |          |         |      |
|                  |     |        |     |              |     |           |         | the smaller | size.    |      |        |             |          |         |      |
rooflineperformancemodel[48]. Forinputfromglobalmem- Algorithm1isanodd-sizedmergingnetworkthatmerges
ory, k-selection cannot run faster than the time required to alreadysortedleft andright arrays,eachofarbitrarylength.
scantheinputonceatpeakmemorybandwidth. Weaimto Whilethebitonicnetworkmergesbitonicsequences,westart
get as close to this limit as possible. Thus, we wish to per- withmonotonic sequences: sequencessortedmonotonically.
formasinglepassovertheinputdata(fromglobalmemory A bitonic merge is made monotonic by reversing the first
| or produced | on-the-fly, |        | perhaps | fused | with | a kernel | that is | comparator |     | stage. |     |     |     |     |     |
| ----------- | ----------- | ------ | ------- | ----- | ---- | -------- | ------- | ---------- | --- | ------ | --- | --- | --- | --- | --- |
| generating  | the         | data). |         |       |      |          |         |            |     |        |     |     |     |     |     |
Theoddsizealgorithmisderivedbyconsideringarraysto
Wewanttokeepintermediatestateinthefastestmemory:
|                  |          |                                      |     |          |      |         |          | be padded | to  | the next | highest | power-of-2 |     | size with | dummy |
| ---------------- | -------- | ------------------------------------ | --- | -------- | ---- | ------- | -------- | --------- | --- | -------- | ------- | ---------- | --- | --------- | ----- |
| theregisterfile. |          | Themajordisadvantageofregistermemory |     |          |      |         |          |           |     |          |         |            |     |           |       |
| is that the      | indexing | into                                 | the | register | file | must be | known at |           |     |          |         |            |     |           |       |
assemblytime,whichisastrongconstraintonthealgorithm.
|                        |     |     |     |     |     |     |     |       |     |     | 1 3 | 4 8 | 9   | 0 3 7 |     |
| ---------------------- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | ----- | --- |
| 4.1 In-registersorting |     |     |     |     |     |     |     | step1 |     |     |     |     |     |       |     |
Weuseanin-registersortingprimitiveasabuildingblock. 1 3 4 3 0 9 8 7
| Sorting | networks | are | commonly |     | used on | SIMD | architec- |     |     |     |     |     |     |     |     |
| ------- | -------- | --- | -------- | --- | ------- | ---- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
step 2
| tures [13], | as they | exploit | vector | parallelism. |     | They | are eas- |     |     |     |     |     |     |       |     |
| ----------- | ------- | ------- | ------ | ------------ | --- | ---- | -------- | --- | --- | --- | --- | --- | --- | ----- | --- |
|             |         |         |        |              |     |      |          |     |     |     | 0 3 | 4 3 | 1   | 7 8 9 |     |
ilyimplementedontheGPU,andwebuildsortingnetworks
| with lane-stride                              |     | register | arrays. |         |         |         |      | step 3 |     |     |     |     |     |       |     |
| --------------------------------------------- | --- | -------- | ------- | ------- | ------- | ------- | ---- | ------ | --- | --- | --- | --- | --- | ----- | --- |
| WeuseavariantofBatcher’s                      |     |          |         | bitonic | sorting | network | [8], |        |     |     |     |     |     |       |     |
|                                               |     |          |         |         |         |         |      |        |     |     | 0 3 | 1 3 | 4   | 7 8 9 |     |
| whichisasetofparallelmergesonanarrayofsize2k. |     |          |         |         |         |         | Each | step 4 |     |     |     |     |     |       |     |
|                                               |     |          |         |         |         |         |      |        |     |     | 0 1 | 3 3 | 4   | 7 8 9 |     |
mergetakessarraysoflengtht(sandtapowerof2)tos/2
| arrays of | length | 2t, using | log | (t) | parallel | steps. | A bitonic |     |     |     |     |     |     |     |     |
| --------- | ------ | --------- | --- | --- | -------- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
2
| sortappliesthismergerecursively: |     |     |     |     | tosortanarrayoflength |     |     |        |     |          |         |         |     |        |          |
| -------------------------------- | --- | --- | --- | --- | --------------------- | --- | --- | ------ | --- | -------- | ------- | ------- | --- | ------ | -------- |
|                                  |     |     |     |     |                       |     |     | Figure | 1:  | Odd-size | network | merging |     | arrays | of sizes |
(cid:96),merge(cid:96)arraysoflength1to(cid:96)/2arraysoflength2,to(cid:96)/4
arraysoflength4,successivelyto1sortedarrayoflength(cid:96), 5 and 3. Bullets indicate parallel compare/swap.
leading to 1(log ((cid:96))2+log ((cid:96))) parallel merge steps. Dashed lines are elided elements or comparisons.
|     | 2   | 2   | 2   |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
4

input  threadqueue warp queue The elements (on the left of Figure 2) are processed in
. . . . . . . . .  .   .   .   .   . . . . . . . . . . . . . . . . . . . . .  l a n e   0 g r o u p s o f 3 2 , t h e w a r p s i z e . L a n e j i s r e s p o n s i b le f o r p r o -
insertion m . . . . . . . . . . . . . . . . . . . .   c e s s i n g { a , a , . . . } ; t h u s , i f t h e e l e m e n t s c o m e f r o m g l o b a l
|     |     | .   .   . |   .   . | e   |     | l a n e   1 |     | j   | 3 2 + j |     |     |     |     |     |
| --- | --- | --------- | ------- | --- | --- | ----------- | --- | --- | ------- | --- | --- | --- | --- | --- |
gr
ni . . . . . . . . . . . m e m o r y , t h e r e a d s a r e c o n t i g u o u s a n d c o a l e s c e d i n t o a m i n -
| c o a lesced            |     |     |     | n   g |     |     |         |           |             |             |               |       |     |     |
| ----------------------- | --- | --- | --- | ----- | --- | --- | ------- | --------- | ----------- | ----------- | ------------- | ----- | --- | --- |
|                         |     |     |     |       |     |     | i m a l | n u m b e | r o f m e m | o r y t r a | n s a c t i o | n s . |     |     |
| re a d                  |     |     |     | wt e  |     |     |         |           |             |             |               |       |     |     |
| . . . . . . . . . . . . |     |     |     | o     |     |     |         |           |             |             |               |       |     |     |
kr D a t a s t r u c t u r e s . E a c h l a n e j m a i n t a i n s a s m a l l q u e u e
.   .   .   .   . l a n e   31 o f t e l e m e n t s i n r e g i s t e r s , c a l l e d t h e t h r e a d q u e u e s [ T j ] ,
|     |     |     |     |     |     |     |                                   |             |               |           |               |                  |           | i i = 0 : t     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------- | ----------- | ------------- | --------- | ------------- | ---------------- | --------- | --------------- |
|     |     |     |     |     |     |     | o r d e r                         | e d f r o m | l a r g e s t | t o s m a | l l e s t ( T | j ≥ T j          | ) . T h e | c h o i c e o f |
|     |     |     |     |     |     |     |                                   |             |               |           |               | i i +            | 1         |                 |
|     |     |     |     |     |     |     | tismaderelativetok,seeSection4.3. |             |               |           |               | Thethreadqueueis |           |                 |
Figure 2: Overview of WarpSelect. The input val- a first-level filter for new values coming in. If a new a 32i+j
isgreaterthanthelargestkeycurrentlyinthequeue,Tj,it
uesstreaminontheleft,andthewarpqueueonthe
0
isguaranteedthatitwon’tbeintheksmallestfinalresults.
| right holds | the | output | result. |     |     |     |                 |      |          |                      |          |       |             |          |
| ----------- | --- | ------ | ------- | --- | --- | --- | --------------- | ---- | -------- | -------------------- | -------- | ----- | ----------- | -------- |
|             |     |        |         |     |     |     | The             | warp | shares a | lane-stride          | register | array | of k        | smallest |
|             |     |        |         |     |     |     | seenelements,[W |      | ]        | ,calledthewarpqueue. |          |       | Itisordered |          |
i i=0:k
elements that are never swapped (the merge is monotonic) from smallest to largest (W ≤W ); if the requested k is
i i+1
and are already properly positioned; any comparisons with not a multiple of 32, we round it up. This is a second level
dummy elements are elided. A left array is considered to data structure that will be used to maintain all of the k
be padded with dummy elements at the start; a right ar- smallestwarp-wideseenvalues. Thethreadandwarpqueues
ray has them at the end. A merge of two sorted arrays are initialized to maximum sentinel values, e.g., +∞.
| of length                                        | (cid:96) and                              | (cid:96) to | a sorted | array of          | (cid:96) +(cid:96) | requires |         |              |       |            |            |       |      |     |
| ------------------------------------------------ | ----------------------------------------- | ----------- | -------- | ----------------- | ------------------ | -------- | ------- | ------------ | ----- | ---------- | ---------- | ----- | ---- | --- |
|                                                  | L                                         | R           |          |                   | L R                |          |         |              |       |            |            |       |      |     |
|                                                  |                                           |             |          |                   |                    |          | Update. | The          | three | invariants | maintained |       | are: |     |
| (cid:100)log 2 (max((cid:96)                     | L ,(cid:96) R ))(cid:101)+1parallelsteps. |             |          | Figure1showsAlgo- |                    |          |         |              |       |            |            |       |      |     |
| rithm1’smergingnetworkforarraysofsize5and3,with4 |                                           |             |          |                   |                    |          |         |              | Tj    |            |            |       |      |     |
|                                                  |                                           |             |          |                   |                    |          | •       | all per-lane |       | are not    | in the     | min-k |      |     |
| parallel                                         | steps.                                    |             |          |                   |                    |          |         |              | 0     |            |            |       |      |     |
Thecompare-swapisimplementedusingwarpshuffleson
|     |     |     |     |     |     |     | •   | all per-lane | Tj  | are greater | than | all | warp queue | keys |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ----------- | ---- | --- | ---------- | ---- |
0
| a lane-stride | register | array. | Swaps | with a | stride a | multiple |     | W   |     |     |     |     |     |     |
| ------------- | -------- | ------ | ----- | ------ | -------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
i
| of 32 occur | directly | within | a lane | as the | lane holds | both |     |     |     |     |     |     |     |     |
| ----------- | -------- | ------ | ------ | ------ | ---------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
elements locally. Swaps of stride ≤16 or a non-multiple of • all a seen so far in the min-k are contained in either
i
32 occur with warp shuffles. In practice, used array lengths some lane’s thread queue ([T j] ), or in the
|               |       |         |          |                |         |     |     |             |     |     |     | i i=0:t,j=0:32 |     |     |
| ------------- | ----- | ------- | -------- | -------------- | ------- | --- | --- | ----------- | --- | --- | --- | -------------- | --- | --- |
| are multiples | of 32 | as they | are held | in lane-stride | arrays. |     |     | warp queue. |     |     |     |                |     |     |
Algorithm 2 Odd-size sorting network Lanej receivesanewa andattemptstoinsertitinto
32i+j
|          |             |     |     |     |     |     | its thread | queue. | If  | a     | > T j, | then the | new | pair is by |
| -------- | ----------- | --- | --- | --- | --- | --- | ---------- | ------ | --- | ----- | ------ | -------- | --- | ---------- |
| function | sort-odd([x |     | ] ) |     |     |     |            |        |     | 32i+j | 0      |          |     |            |
i i=0:(cid:96) definition not in the k minimum, and can be rejected.
| if  | (cid:96)>1 then |     |     |     |     |     |            |        |                |      |          |         |        |           |
| --- | --------------- | --- | --- | --- | --- | --- | ---------- | ------ | -------------- | ---- | -------- | ------- | ------ | --------- |
|     |                 |     |     |     |     |     | Otherwise, |        | it is inserted |      | into its | proper  | sorted | position  |
|     | parallel        | do  |     |     |     |     |            |        |                |      |          |         |        |           |
|     |                 |     |     |     |     |     | in the     | thread | queue,         | thus | ejecting | the old | T j.   | All lanes |
|     | sort-odd([x     |     | ]   | )   |     |     |            |        |                |      |          |         | 0      |           |
i i=0:(cid:98)(cid:96)/2(cid:99) complete doing this with their new received pair and their
|     | sort-odd([x |     | ]   | )   |     |     |     |     |     |     |     |     |     |     |
| --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
i i=(cid:98)(cid:96)/2(cid:99):(cid:96)
|     | end do |     |     |     |     |     | threadqueue,butitisnowpossiblethatthesecondinvariant |     |     |     |     |     |     |     |
| --- | ------ | --- | --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
merge-odd([x have been violated. Using the warp ballot instruction, we
|     |     |     | i ] i=0:(cid:98)(cid:96)/2(cid:99) ,[x | i ] i=(cid:98)(cid:96)/2(cid:99):(cid:96) | )   |     |           |     |                  |              |            |            |            |     |
| --- | --- | --- | -------------------------------------- | ----------------------------------------- | --- | --- | --------- | --- | ---------------- | ------------ | ---------- | ---------- | ---------- | --- |
|     |     |     |                                        |                                           |     |     | determine | if  | any lane         | has violated |            | the second | invariant. | If  |
| end | if  |     |                                        |                                           |     |     |           |     |                  |              |            |            |            |     |
|     |     |     |                                        |                                           |     |     | not, we   | are | free to continue |              | processing | new        | elements.  |     |
end function
|     |     |     |     |     |     |     | Restoring |     | the invariants. |     | If any | lane | has its | invariant |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | --------------- | --- | ------ | ---- | ------- | --------- |
Algorithm2extendsthemergetoafullsort. Assumingno violated, then the warp uses odd-merge to merge and sort
structurepresentintheinputdata, 1((cid:100)log ((cid:96))(cid:101)2+(cid:100)log ((cid:96))(cid:101)) thethreadandwarpqueuestogether. Thenewwarpqueue
|                |           |          |             | 2 2  |           | 2         |           |     |              |     |            |     |          |     |
| -------------- | --------- | -------- | ----------- | ---- | --------- | --------- | --------- | --- | ------------ | --- | ---------- | --- | -------- | --- |
| parallel       | steps are | required | for sorting | data | of length | (cid:96). |           |     |              |     |            |     |          |     |
| 4.2 WarpSelect |           |          |             |      |           |           | Algorithm |     | 3 WarpSelect |     | pseudocode |     | for lane | j   |
Ourk-selectionimplementation,WarpSelect,maintains WarpSelect(a)
function
a<Tj
state entirely in registers, requires only a single pass over if then
|     |     |     |     |     | Itusesmerge- |     |     |     | 0   |     |     |     |     |     |
| --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
dataandavoidscross-warpsynchronization. insert a into our [Tj]
i i=0:t
| oddandsort-oddasprimitives. |     |     |     | Sincetheregisterfilepro- |     |     |     | end if |     |     |     |     |     |     |
| --------------------------- | --- | --- | --- | ------------------------ | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
vides much more storage than shared memory, it supports if warp-ballot(Tj <W ) then
|     |     |     |     |     |     |     |     |     |     | 0   | k−1 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
k ≤1024. Each warp is dedicated to k-selection to a single (cid:46) Reinterpret thread queues as lane-stride array
one of the n arrays [a ]. If n is large enough, a single warp [α ] ←cast([T j] )
|     |     | i   |     |     |     |     |     | i   | i=0:32t |     | i i=0:t,j=0:32 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | -------------- | --- | --- | --- |
pereach[a ]willresultinfullGPUoccupancy. Large(cid:96)per (cid:46) concatenate and sort thread queues
i
warpishandledbyrecursivedecomposition,if(cid:96)isknownin sort-odd([α
|          |     |     |     |     |     |     |     |              |                      | i ] i=0:32t | )     |           |           |        |
| -------- | --- | --- | --- | --- | --- | --- | --- | ------------ | -------------------- | ----------- | ----- | --------- | --------- | ------ |
| advance. |     |     |     |     |     |     |     | merge-odd([W |                      |             |       |           |           |        |
|          |     |     |     |     |     |     |     |              |                      | i ] i=0:k   | ,[α i | ] i=0:32t | )         |        |
|          |     |     |     |     |     |     |     |              | (cid:46) Reinterpret | lane-stride |       | array     | as thread | queues |
Overview. Ourapproach(Algorithm3andFigure2)oper- [Tj] ←cast([α
|         |              |            |         |         |       |        |     |                  | i=0:t,j=0:32 |     |     | i ] i=0:32t | )   |     |
| ------- | ------------ | ---------- | ------- | ------- | ----- | ------ | --- | ---------------- | ------------ | --- | --- | ----------- | --- | --- |
| ates on | values, with | associated | indices | carried | along | (omit- |     | i                |              |     |     |             |     |     |
|         |              |            |         |         |       |        |     | reverse-array([T |              |     | ] ) |             |     |     |
tedfromthedescriptionforsimplicity). Itselectsthekleast i i=0:t
|     |     |     |     |     |     |     |     | (cid:46) | Back in | thread | queue | order, | invariant | restored |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------- | ------ | ----- | ------ | --------- | -------- |
valuesthatcomefromglobalmemory,orfromintermediate
|     |     |     |     |     |     |     |     | end if |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
valueregistersiffusedintoanotherkernelprovidingtheval-
end function
| ues. Let | [a ] | be the | sequence | provided | for selection. |     |     |     |     |     |     |     |     |     |
| -------- | ---- | ------ | -------- | -------- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
i i=0:(cid:96)
5

willbethemin-kelementsacrossthemerged,sortedqueues, own for exact nearest neighbor search in small datasets. It
andthenewthreadqueueswillbetheremainder,frommin- is also a component of many indexes in the literature. In
(k+1)tomin-(k+32t+1). Thisrestorestheinvariantsand our case, we use it for the IVFADC coarse quantizer q .
1
we are free to continue processing subsequent elements. As stated in Section 2, the distance computation boils
Since the thread and warp queues are already sorted, we downtoamatrixmultiplication. WeuseoptimizedGEMM
merge the sorted warp queue of length k with 32 sorted routines in the cuBLAS library to calculate the −2(cid:104)x j ,y i (cid:105)
arraysoflengtht. Supportingodd-sizedmergesisimportant term for L2 distance, resulting in a partial distance matrix
because Batcher’s formulation would require that 32t = k D(cid:48). To complete the distance calculation, we use a fused
and is a power-of-2; thus if k = 1024, t must be 32. We k-selection kernel thatadds the (cid:107)y (cid:107)2 term toeachentry of
i
found that the optimal t is way smaller (see below). the distance matrix and immediately submits the value to
Using odd-merge to merge the 32 already sorted thread k-selection in registers. The (cid:107)x (cid:107)2 term need not be taken
j
queues would require a struct-of-arrays to array-of-structs into account before k-selection. Kernel fusion thus allows
transpositioninregistersacrossthewarp,sincethetsucces- foronly2passes(GEMMwrite,k-selectread)overD(cid:48),com-
sive sorted values are held in different registers in the same paredtootherimplementationsthatmayrequire3ormore.
lane rather than a lane-stride array. This is possible [12], Row-wise k-selection is likely not fusable with a well-tuned
butwoulduseacomparablenumberofwarpshuffles, sowe GEMM kernel, or would result in lower overall efficiency.
just reinterpret the thread queue registers as an (unsorted) As D(cid:48) does not fit in GPU memory for realistic problem
lane-stridearrayandsortfromscratch. Significantspeedup sizes, the problem is tiled over the batch of queries, with
is realizable by using odd-merge for the merge of the ag- t ≤n queriesbeingruninasingletile. Eachofthe(cid:100)n /t (cid:101)
|     |     |     |     |     |     |     |     | q   | q   |     |     |     |     |     | q q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
gregate sorted thread queues with the warp queue. tiles are independent problems, but we run two in parallel
ondifferentstreamstobetteroccupytheGPU,sotheeffec-
| Handlingtheremainder.                                     |     |     |     | Ifthereareremainderelements |     |     |     |                                        |           |          |                |          |                   |       |        |
| --------------------------------------------------------- | --- | --- | --- | --------------------------- | --- | --- | --- | -------------------------------------- | --------- | -------- | -------------- | -------- | ----------------- | ----- | ------ |
|                                                           |     |     |     |                             |     |     |     | tivememoryrequirementofDisO(2(cid:96)t |           |          |                |          | ). Thecomputation |       |        |
| because(cid:96)isnotamultipleof32,thoseareinsertedintothe |     |     |     |                             |     |     |     |                                        |           |          |                |          | q                 |       |        |
|                                                           |     |     |     |                             |     |     |     | can                                    | similarly | be tiled | over (cid:96). | For very | large             | input | coming |
thread queues for the lanes that have them, after which we from the CPU, we support buffering with pinned memory
| proceed | to  | the output   | stage. |       |         |        |            |            |     |            |      |      |              |     |     |
| ------- | --- | ------------ | ------ | ----- | ------- | ------ | ---------- | ---------- | --- | ---------- | ---- | ---- | ------------ | --- | --- |
|         |     |              |        |       |         |        |            | to overlap |     | CPU to GPU | copy | with | GPU compute. |     |     |
| Output. |     | A final sort | and    | merge | is made | of the | thread and |            |     |            |      |      |              |     |     |
5.2 IVFADCindexing
| warp | queues, | after | which | the warp | queue | holds | all min-k |     |     |     |     |     |     |     |     |
| ---- | ------- | ----- | ----- | -------- | ----- | ----- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
values.
|     |     |     |     |     |     |     |     | PQlookuptables. |     | Atitscore,theIVFADCrequirescom- |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ------------------------------- | --- | --- | --- | --- | --- |
4.3 Complexityandparameterselection
putingthedistancefromavectortoasetofproductquanti-
For each incoming group of 32 elements, WarpSelect zation reproduction values. By developing Equation (6) for
can perform 1, 2 or 3 constant-time operations, all happen- a database vector y, we obtain:
| ing | in warp-wide | parallel     |         | time: |        |        |             |     |                           |               |     |       |      |                 |     |
| --- | ------------ | ------------ | ------- | ----- | ------ | ------ | ----------- | --- | ------------------------- | ------------- | --- | ----- | ---- | --------------- | --- |
|     |              |              |         |       |        |        |             |     | (cid:107)x−q(y)(cid:107)2 | =(cid:107)x−q |     | (y)−q | (y−q | (y))(cid:107)2. | (7) |
|     |              |              |         |       |        |        |             |     |                           | 2             |     | 1     | 2    | 1 2             |     |
|     | 1. read      | 32 elements, | compare |       | to all | thread | queue heads |     |                           |               |     |       |      |                 |     |
T j, cost C , happens N times; If we decompose the residual vectors left after q as:
|     | 0   | 1   |     | 1   |     |     |     |     |     |     |     |     |     | 1   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2. if ∃j ∈{0,...,31}, a <T j, perform insertion sort y−q (y) = [y(cid:101)1···y(cid:101)b] and (8)
|     |      |                |        | 32n+j   | 0   |               |      |     |     | 1       |     |                             |     |     |     |
| --- | ---- | -------------- | ------ | ------- | --- | ------------- | ---- | --- | --- | ------- | --- | --------------------------- | --- | --- | --- |
|     | on   | those specific | thread | queues, |     | cost C =O(t), | hap- |     |     |         |     |                             |     |     |     |
|     |      |                |        |         |     | 2             |      |     |     | x−q (y) | =   | [x(cid:102)1···x(cid:101)b] |     |     | (9) |
|     | pens | N times;       |        |         |     |               |      |     |     | 1       |     |                             |     |     |     |
2
|     | ∃j,Tj                                   |     |       |          |       |         |            | then                      | the distance | is rewritten                                    |     | as:                                                 |     |     |     |
| --- | --------------------------------------- | --- | ----- | -------- | ----- | ------- | ---------- | ------------------------- | ------------ | ----------------------------------------------- | --- | --------------------------------------------------- | --- | --- | --- |
|     | 3. if                                   | < W | k−1 , | sort and | merge | queues, | cost C 3 = |                           |              |                                                 |     |                                                     |     |     |     |
|     | O(tlog(32t)2+klog(max(k,32t))),happensN | 0   |       |          |       |         |            |                           |              |                                                 |     |                                                     |     |     |     |
|     |                                         |     |       |          |       |         | 3 times.   | (cid:107)x−q(y)(cid:107)2 |              | =(cid:107)x(cid:102)1−q1(y(cid:101)1)(cid:107)2 |     | +...+(cid:107)x(cid:101)b−qb(y(cid:101)b)(cid:107)2 |     |     |     |
. (10)
|     |                      |     |     |      |     |      |                   |     |     | 2         |     | 2   |     |     | 2   |
| --- | -------------------- | --- | --- | ---- | --- | ---- | ----------------- | --- | --- | --------- | --- | --- | --- | --- | --- |
|     | Thus,thetotalcostisN |     |     | C +N | C   | +N C | . N =(cid:96)/32, |     |     |           |     |     |     |     |     |
|     |                      |     |     | 1 1  | 2 2 | 3 3  | 1                 |     |     | q1,...,qb |     |     |     |     |     |
andonrandomdatadrawnindependently,N =O(klog((cid:96))) Each quantizer has 256 reproduction values, so
2
and N =O(klog((cid:96))/t), see the Appendix for a full deriva- when x and q 1 (y) are known all distances can be precom-
3
tion. Hence, the trade-off is to balance a cost in N C and puted and stored in tables T 1 ,...,T b each of size 256 [25].
|                                       |       |             |                  |        |        |           | 2 2                |           |            |              |          |               |               |     |       |
| ------------------------------------- | ----- | ----------- | ---------------- | ------ | ------ | --------- | ------------------ | --------- | ---------- | ------------ | -------- | ------------- | ------------- | --- | ----- |
|                                       |       |             |                  |        |        |           |                    | Computing |            | the sum (10) | consists |               | of b look-ups | and | addi- |
| one                                   | in N  | 3 C 3 . The | practical        | choice | for    | t given   | k and (cid:96) was |           |            |              |          |               |               |     |       |
|                                       |       |             |                  |        |        |           |                    | tions.    | Comparing  | the          | cost to  | compute       | n distances:  |     |       |
| madebyexperimentonavarietyofk-NNdata. |       |             |                  |        |        |           | Fork≤32,           |           |            |              |          |               |               |     |       |
| we                                    | use t | = 2, k ≤    | 128 uses         | t =    | 3, k ≤ | 256 uses  | t = 4, and         |           |            |              |          |               |               |     |       |
|                                       |       |             |                  |        |        |           |                    |           | • Explicit | computation: | n×d      | mutiply-adds; |               |     |       |
| k≤1024                                |       | uses t=8,   | all irrespective |        | of     | (cid:96). |                    |           |            |              |          |               |               |     |       |
5. COMPUTATIONLAYOUT • With lookup tables: 256×d multiply-adds and n×b
lookup-adds.
|             | This section | explains     |       | how IVFADC,  |             | one of       | the indexing |      |         |                 |            |          |             |            |         |
| ----------- | ------------ | ------------ | ----- | ------------ | ----------- | ------------ | ------------ | ---- | ------- | --------------- | ---------- | -------- | ----------- | ---------- | ------- |
| methods     |              | originally   | built | upon product |             | quantization | [25], is     |      |         |                 |            |          |             |            |         |
|             |              |              |       |              |             |              |              | This | is the  | key to the      | efficiency | of       | the product | quantizer. |         |
| implemented |              | efficiently. |       | Details      | on distance | computations |              |      |         |                 |            |          |             |            |         |
|             |              |              |       |              |             |              |              | In   | our GPU | implementation, |            | b is any | multiple    | of         | 4 up to |
andarticulationwithk-selectionarethekeytounderstand-
64. Thecodesarestoredassequentialgroupsofbbytesper
ing why this method can outperform more recent GPU- vector within lists.
| compliant |     | approximate | nearest |     | neighbor | strategies | [47]. |        |     |                |     |      |          |      |          |
| --------- | --- | ----------- | ------- | --- | -------- | ---------- | ----- | ------ | --- | -------------- | --- | ---- | -------- | ---- | -------- |
|           |     |             |         |     |          |            |       | IVFADC |     | lookup tables. |     | When | scanning | over | the ele- |
5.1 Exactsearch
|     |     |     |     |     |     |     |     | ments | of the | inverted | list I | (where | by definition |     | q (y) is |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ------ | -------- | ------ | ------ | ------------- | --- | -------- |
|     |     |     |     |     |     |     |     |       |        |          | L      |        |               |     | 1        |
We briefly come back to the exhaustive search method, constant), the look-up table method can be applied, as the
oftenreferredtoasexactbrute-force. Itisinterestingonits query x and q (y) are known.
1
6

Moreover, the computation of the tables T ...T is fur- forasinglequery,withk-selectionfusedwithdistancecom-
1 b
theroptimized[5]. Theexpressionof(cid:107)x−q(y)(cid:107)2inEquation putation. ThisispossibleasWarpSelectdoesnotfightfor
2
(7) can be decomposed as: thesharedmemoryresourcewhichisseverelylimited. This
reducesglobalmemorywrite-back,sincealmostallinterme-
(cid:107)q (...)(cid:107)2+2(cid:104)q (y),q (...)(cid:105)+(cid:107)x−q (y)(cid:107)2−2(cid:104)x,q (...)(cid:105).
2 2 1 2 1 2 2 diateresultscanbeeliminated. However,unlikek-selection
(cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
term1 term2 term3 overheadforexactcomputation,asignificantportionofthe
(11) runtimeisthegatherfromtheT insharedmemoryandlin-
i
The objective is to minimize inner loop computations. earscanningoftheI fromglobalmemory;thewrite-backis
i
Thecomputationswecandoinadvanceandstoreinlookup not a dominant contributor. Timing for the fused kernel is
tables are as follows: improvedbyatmost15%,andforsomeproblemsizeswould
besubjecttolowerparallelismandworseperformancewith-
• Term1isindependentofthequery. Itcanbeprecom-
out subsequent decomposition. Therefore, and for reasons
puted from the quantizers, and stored in a table T of
of implementation simplicity, we do not use this layout.
size |C |×256×b;
1
• Term2isthedistancetoq ’sreproductionvalue. Itis Algorithm 4 IVFPQ batch search routine
1
thus a by-product of the first-level quantizer q 1 ; function ivfpq-search([x 1 ,...,x nq ], I 1 ,...,I |C1| )
for i←0:n do (cid:46) batch quantization of Section 5.1
q
• Term3canbecomputedindependentlyoftheinverted Li ←τ-argmin (cid:107)x−c(cid:107)
list. Its computation costs d×256 multiply-adds. IVF c∈C1 2
end for
for i←0:n do
This decomposition is used to produce the lookup tables q
L←[] (cid:46) distance table
T ...T used during the scan of the inverted list. For a
1 b Compute term 3 (see Section 5.2)
single query, computing the τ ×b tables from scratch costs
for L in Li do (cid:46) τ loops
τ ×d×256 multiply-adds, while this decomposition costs IVF
Compute distance tables T ,...,T
256×dmultiply-addsandτ×b×256additions. OntheGPU, 1 b
for j in I do
thememoryusageofT canbeprohibitive,soweenablethe L
(cid:46) distance estimation, Equation (10)
decomposition only when memory is a not a concern.
d←(cid:107)x −q(y )(cid:107)2
i j 2
5.3 GPUimplementation Append (d,L,j) to L
end for
Algorithm 4 summarizes the process as one would im-
end for
plement it on a CPU. The inverted lists are stored as two
R ← k-select smallest distances d from L
separate arrays, for PQ codes and associated IDs. IDs are i
end for
resolved only if k-selection determines k-nearest member-
return R
ship. This lookup yields a few sparse memory reads in a
end function
large array, thus the IDs can optionally be stored on CPU
for tiny performance cost.
List scanning. A kernel is responsible for scanning the τ 5.4 Multi-GPUparallelism
closestinvertedlistsforeachquery,andcalculatingtheper-
Modern servers can support several GPUs. We employ
vectorpairdistancesusingthelookuptablesT . TheT are
i i this capability for both compute power and memory.
storedinsharedmemory: upton ×τ×max |I |×blookups
q i i
arerequiredforaqueryset(trillionsofaccessesinpractice), Replication. If an index instance fits in the memory of a
and are random access. This limits b to at most 48 (32- singleGPU,itcanbereplicatedacrossRdifferentGPUs. To
bitfloatingpoint)or96(16-bitfloatingpoint)withcurrent queryn q vectors,eachreplicahandlesafractionn q /Rofthe
architectures. In case we do not use the decomposition of queries, joining the results back together on a single GPU
Equation (11), the T are calculated by a separate kernel or in CPU memory. Replication has near linear speedup,
i
before scanning. except for a potential loss in efficiency for small n q .
Multi-pass kernels. Each n ×τ pairs of query against Sharding. If an index instance does not fit in the memory
q
inverted list can be processed independently. At one ex- of a single GPU, an index can be sharded across S differ-
treme, a block is dedicated to each of these, resulting in up ent GPUs. For adding (cid:96) vectors, each shard receives (cid:96)/S of
to n ×τ ×max |I | partial results being written back to thevectors,andforquery,eachshardhandlesthefullquery
q i i
global memory, which is then k-selected to n q ×k final re- setn q ,joiningthepartialresults(anadditionalroundofk-
sults. This yields high parallelism but can exceed available selectionisstillrequired)onasingleGPUorinCPUmem-
GPU global memory; as with exact search, we choose a tile ory. For a given index size (cid:96), sharding will yield a speedup
size t q ≤ n q to reduce memory consumption, bounding its (sharding has a query of n q against (cid:96)/S versus replication
complexity by O(2t q τmax i |I i |) with multi-streaming. with a query of n q /R against (cid:96)), but is usually less than
A single warp could be dedicated to k-selection of each pure replication due to fixed overhead and cost of subse-
t set of lists, which could result in low parallelism. We quent k-selection.
q
introduceatwo-passk-selection,reducingt ×τ×max |I | Replicationandshardingcanbeusedtogether(S shards,
q i i
to t ×f ×k partial results for some subdivision factor f. eachwithRreplicasforS×RGPUsintotal). Shardingor
q
Thisisreducedagainviak-selectiontothefinalt ×kresults. replicationarebothfairlytrivial,andthesameprinciplecan
q
be used to distribute an index across multiple machines.
Fusedkernel. Aswithexactsearch,weexperimentedwith
a kernel that dedicates a single block to scanning all τ lists
7

# centroids
|     |     |     |     |     |     |     |     |     | method |     | #   | GPUs | 256 | 4096 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | ---- | --- | ---- | --- |
����
|     |     |     |     |     |     |     |     |     | BIDMach | [11] |     | 1   | 320s | 735s |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ---- | --- | --- | ---- | ---- | --- |
|     |     |     |     |     |     |     |     |     | Ours    |      |     | 1   | 140s | 316s |     |
|     |     |     |     |     |     |     |     |     | Ours    |      |     | 4   | 84s  | 100s |     |
������������ ���
|     |     |     |     |     |     |     |     |     | Table | 1: MNIST8m |     | k-means | performance |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | ---------- | --- | ------- | ----------- | --- | --- |
��
|     |     |     |     | ���������������������� |     |     |     | 6.2 | k-meansclustering |     |     |     |     |     |     |
| --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- |
������������
���������� The exact search method with k=1 can be used by a k-
����������������������
���� means clustering method in the assignment stage, to assign
����� ����� ������ ������ n training vectors to |C | centroids. Despite the fact that
|     |     |     |              |     |     |     |     | q                                               |           |         | 1   |          |       |     |         |
| --- | --- | --- | ------------ | --- | --- | --- | --- | ----------------------------------------------- | --------- | ------- | --- | -------- | ----- | --- | ------- |
|     |     |     | ������������ |     |     |     |     | itdoesnotusetheIVFADCandk=1selectionistrivial(a |           |         |     |          |       |     |         |
|     |     |     |              |     |     |     |     | parallel                                        | reduction | is used | for | the k =1 | case, | not | WarpSe- |
Figure 3: Runtimes for different k-selection meth- lect),k-meansisagoodbenchmarkfortheclusteringused
| ods, as             | a function | of  | array   | length | (cid:96).          | Simultaneous |     |                                     |     |           |       |     |     |     |         |
| ------------------- | ---------- | --- | ------- | ------ | ------------------ | ------------ | --- | ----------------------------------- | --- | --------- | ----- | --- | --- | --- | ------- |
|                     |            |     |         |        |                    |              |     | to train                            | the | quantizer | q 1 . |     |     |     |         |
| arraysprocessedaren |            |     | =10000. |        | k=100forfulllines, |              |     |                                     |     |           |       |     |     |     |         |
|                     |            |     | q       |        |                    |              |     | WeapplythealgorithmonMNIST8mimages. |     |           |       |     |     |     | The8.1M |
| k=1000              | for dashed |     | lines.  |        |                    |              |     |                                     |     |           |       |     |     |     |         |
imagesaregrayleveldigitsin28x28pixels,linearizedtovec-
|     |     |     |     |     |     |     |     | tors | of 784-d. | We compare |     | this k-means | implementation |     | to  |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --------- | ---------- | --- | ------------ | -------------- | --- | --- |
theGPUk-meansofBIDMach[11],whichwasshowntobe
6. EXPERIMENTS&APPLICATIONS
|     |     |     |     |     |     |     |     | more | efficient | than several |     | distributed | k-means | implemen- |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --------- | ------------ | --- | ----------- | ------- | --------- | --- |
This section compares our GPU k-selection and nearest- tations that require dozens of machines3. Both algorithms
neighborapproachtoexistinglibraries. Unlessstatedother- were run for 20 iterations. Table 1 shows that our imple-
wise,experimentsarecarriedoutona2×2.8GHzIntelXeon mentation is more than 2× faster, although both are built
E5-2680v2 with 4 Maxwell Titan X GPUs on CUDA 8.0. upon cuBLAS. Our implementation receives some benefit
|     |     |     |     |     |     |     |     | from | the k-selection |     | fusion | into L2 | distance | computation. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --------------- | --- | ------ | ------- | -------- | ------------ | --- |
6.1 k-selectionperformance
|     |     |     |     |     |     |     |     | For multi-GPU |     | execution | via | replicas, | the | speedup | is close |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | --------- | --- | --------- | --- | ------- | -------- |
WecompareagainsttwootherGPUsmallk-selectionim- tolinearforlargeenoughproblems(3.16×for4GPUswith
plementations: the row-based Merge Queue with Buffered 4096centroids). Notethatthisbenchmarkissomewhatun-
Search and Hierarchical Partition extracted from the fgknn realistic,asonewouldtypicallysub-samplethedatasetran-
libraryofTangetal.[41]andTruncatedBitonicSort(TBiS) domly when so few centroids are requested.
| fromSismanisetal.[40]. |              |            | Bothwereextractedfromtheirre- |     |     |     |     |       |        |               |      |           |         |                |          |
| ---------------------- | ------------ | ---------- | ----------------------------- | --- | --- | --- | --- | ----- | ------ | ------------- | ---- | --------- | ------- | -------------- | -------- |
|                        |              |            |                               |     |     |     |     | Large | scale. | We can        | also | compare   | to [3], | an approximate |          |
| spective               | exact search | libraries. |                               |     |     |     |     |       |        |               |      |           |         |                |          |
|                        |              |            |                               |     |     |     |     | CPU   | method | that clusters |      | 108 128-d | vectors | to             | 85k cen- |
Weevaluatek-selectionfork=100and1000ofeachrow
|                  |     |          |       |              |        |        |            | troids.  | Their                  | clustering | method | runs              | in 46            | minutes,  | but re- |
| ---------------- | --- | -------- | ----- | ------------ | ------ | ------ | ---------- | -------- | ---------------------- | ---------- | ------ | ----------------- | ---------------- | --------- | ------- |
| from a row-major |     | matrix   | n q   | ×(cid:96) of | random | 32-bit | floating   |          |                        |            |        |                   |                  |           |         |
|                  |     |          |       |              |        |        |            | quires   | 56 minutes             | (at        | least) | of pre-processing |                  | to encode | the     |
| point values     | on  | a single | Titan | X. The       | batch  | size n | q is fixed |          |                        |            |        |                   |                  |           |         |
|                  |     |          |       |              |        |        |            | vectors. | Ourmethodperformsexact |            |        |                   | k-meanson4GPUsin |           |         |
at10000,andthearraylengths(cid:96)varyfrom1000to128000.
|     |     |     |     |     |     |     |     | 52 minutes |     | without any | pre-processing. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ----------- | --------------- | --- | --- | --- | --- |
InputsandoutputstotheproblemremainresidentinGPU
memory, with the output being of size n ×k, with corre- 6.3 Exactnearestneighborsearch
q
| spondingindices.                                 |          | Thus,theinputproblemsizesrangefrom |            |                   |                   |        |        |                      |                 |                    |         |                             |                |          |           |
| ------------------------------------------------ | -------- | ---------------------------------- | ---------- | ----------------- | ----------------- | ------ | ------ | -------------------- | --------------- | ------------------ | ------- | --------------------------- | -------------- | -------- | --------- |
|                                                  |          |                                    |            |                   |                   |        |        | We                   | consider        | a classical        | dataset | used                        | to             | evaluate | nearest   |
| 40MB((cid:96)=1000)to5.12GB((cid:96)=128k).      |          |                                    |            |                   | TBiSrequireslarge |        |        |                      |                 |                    |         |                             |                |          |           |
|                                                  |          |                                    |            |                   |                   |        |        | neighbor             | search:         | Sift1M             | [25].   | Its                         | characteristic |          | sizes are |
| auxiliary                                        | storage, | and                                | is limited | to (cid:96)≤48000 |                   | in our | tests. |                      |                 |                    |         |                             |                |          |           |
|                                                  |          |                                    |            |                   |                   |        |        | (cid:96)=106,d=128,n |                 | =104.              |         | Computingthepartialdistance |                |          |           |
| Figure3showsourrelativeperformanceagainstTBiSand |          |                                    |            |                   |                   |        |        |                      |                 | q                  |         |                             |                |          |           |
|                                                  |          |                                    |            |                   |                   |        |        | matrix               | D(cid:48) costs | n ×(cid:96)×d=1.28 |         | Tflop,                      | which          | runs     | in less   |
fgknn. It also includes the peak possible performance given q
by the memory bandwidth limit of the Titan X. The rela- than one second on current GPUs. Figure 4 shows the cost
WarpSelect of the distance computations against the cost of our tiling
| tive performance |           | of     |            | over       | fgknn       | increases  | for             |          |          |             |              |                       |     |          |          |
| ---------------- | --------- | ------ | ---------- | ---------- | ----------- | ---------- | --------------- | -------- | -------- | ----------- | ------------ | --------------------- | --- | -------- | -------- |
|                  |           |        |            |            |             |            |                 | of the   | GEMM     | for the     | −2(cid:104)x | j ,y i (cid:105) term | of  | Equation | 2 and    |
| larger k;        | even TBiS | starts | to         | outperform | fgknn       | for        | larger (cid:96) |          |          |             |              |                       |     |          |          |
|                  |           |        |            |            |             |            |                 | the peak | possible | k-selection |              | performance           |     | on the   | distance |
| at k = 1000.     | We        | look   | especially | at         | the largest | (cid:96) = | 128000.         |          |          |             |              |                       |     |          |          |
WarpSelectis1.62×fasteratk=100,2.01×atk=1000. matrixofsizen ×(cid:96),whichadditionallyaccountsforreading
q
|             |            |          |            |           |           |           |        | the tiled   | result           | matrix      | D(cid:48) at | peak memory |         | bandwidth.      |          |
| ----------- | ---------- | -------- | ---------- | --------- | --------- | --------- | ------ | ----------- | ---------------- | ----------- | ------------ | ----------- | ------- | --------------- | -------- |
| Performance | against    | peak     | possible   |           | drops off | for all   | imple- |             |                  |             |              |             |         |                 |          |
|             |            |          |            |           |           |           |        | In          | addition         | to our      | method       | from        | Section | 5, we           | include  |
| mentations  | at larger  | k.       | WarpSelect |           | operates  | at        | 55% of |             |                  |             |              |             |         |                 |          |
|             |            |          |            |           |           |           |        | times       | from             | the two GPU | libraries    | evaluated   |         | for k-selection |          |
| peak at     | k = 100    | but      | only 16%   | of peak   | at        | k = 1000. | This   |             |                  |             |              |             |         |                 |          |
|             |            |          |            |           |           |           |        | performance |                  | in Section  | 6.1.         | We make     | several | observations:   |          |
| is due to   | additional | overhead |            | assocated | with      | bigger    | thread |             |                  |             |              |             |         |                 |          |
| queues and  | merge/sort |          | networks   | for       | large k.  |           |        |             |                  |             |              |             |         |                 |          |
|             |            |          |            |           |           |           |        | •           | for k-selection, | the         | naive        | algorithm   | that    | sorts           | the full |
resultarrayforeachqueryusingthrust::sort_by_key
| Differences | from | fgknn. |     | WarpSelect |     | is influenced | by  |     |     |     |     |     |     |     |     |
| ----------- | ---- | ------ | --- | ---------- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ismorethan10×slowerthanthecomparisonmethods;
| fgknn,buthasseveralimprovements: |     |     |     |     | allstateismaintained |     |     |     |     |     |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
inregisters(nosharedmemory),nointer-warpsynchroniza-
• L2distanceandk-selectioncostisdominantforallbut
| tion or buffering |     | is used, | no  | “hierarchical | partition”, |     | the k- |     |             |       |     |      |        |      |          |
| ----------------- | --- | -------- | --- | ------------- | ----------- | --- | ------ | --- | ----------- | ----- | --- | ---- | ------ | ---- | -------- |
|                   |     |          |     |               |             |     |        |     | our method, | which | has | 85 % | of the | peak | possible |
selectioncanbefusedintootherkernels,anditusesodd-size
|          |               |         |     |              |     |     |     |          | performance, | assuming |      | GEMM                        | usage | and | our tiling |
| -------- | ------------- | ------- | --- | ------------ | --- | --- | --- | -------- | ------------ | -------- | ---- | --------------------------- | ----- | --- | ---------- |
| networks | for efficient | merging |     | and sorting. |     |     |     |          |              |          |      |                             |       |     |            |
|          |               |         |     |              |     |     |     | 3BIDMach |              | numbers  | from | https://github.com/BIDData/ |       |     |            |
BIDMach/wiki/Benchmarks#KMeans
8

| ��  |     |     |     |     |     |     |     | ���� |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
���������������������
| ���� |     |     |     |     |     |     |     |     | ������������������������� |     |     |     |     |     |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | --- | --- |
����������� � � � � �� � �� � � ��������������������������� ���� �������������������������
|     |     |     | �          |     |     |     |     |     | ������������������������� |     |     |     |     |     |
| --- | --- | --- | ---------- | --- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | --- | --- |
| ��  |     | � � | � � � �� � | �   |     |     |     |     |                           |     |     |     |     |     |
����������������������
|     |     |     | ����� |     |     |     |     | ��� |     |     |     |     |     |     |
| --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
����������� ����
| ��  |     |     |     |     |     |     |     | ��� |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
����
���
��
���
����
��������
| ��  |     |     |     |     |     |     |     | ��  |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
�� �� ��� ��� ���� ����� ���� ���� ���� ���� ���� ���� ���� ���� ����
|     |     |     |     | ��  |     |     |     |     |     | ��������������������� |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------------- | --- | --- | --- | --- |
���
Figure 4: Exact search k-NN time for the SIFT1M �������������������������
����������������������������� �������������������������
| dataset | with | varying | k on | 1 Titan | X   | GPU. |     | ��� |     |     |     |     |     |     |
| ------- | ---- | ------- | ---- | ------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
���������������������
���������������������
���
| of         | the partial | distance  |           | matrix | D(cid:48) on   | top of GEMM | is      |     |     |     |     |     |     |     |
| ---------- | ----------- | --------- | --------- | ------ | -------------- | ----------- | ------- | --- | --- | --- | --- | --- | --- | --- |
| close      | to          | optimal.  | The       | cuBLAS | GEMM           | itself      | has low | ��� |     |     |     |     |     |     |
| efficiency |             | for small | reduction |        | sizes (d=128); |             |         |     |     |     |     |     |     |     |
��
| • Our | fused | L2/k-selection |     | kernel | is  | important. | Our |     |     |     |     |     |     |     |
| ----- | ----- | -------------- | --- | ------ | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
��
sameexactalgorithmwithoutfusion(requiringanad-
������
| ditional |     | pass through |     | D(cid:48)) is at | least | 25% slower. |     |     |     |     |     |     |     |     |
| -------- | --- | ------------ | --- | ---------------- | ----- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
��
|           |             |     |         |      |           |               |     | ���� | ���� | ���� ���� | ���� | ���� | ���� ���� | ���� |
| --------- | ----------- | --- | ------- | ---- | --------- | ------------- | --- | ---- | ---- | --------- | ---- | ---- | --------- | ---- |
| Efficient | k-selection |     | is even | more | important | in situations |     |      |      |           |      |      |           |      |
whereapproximatemethodsareusedtocomputedistances, ���������������������
| because                            | the relative |            | cost of | k-selection | with | respect | to dis- |           |                |              |           |              |                |     |
| ---------------------------------- | ------------ | ---------- | ------- | ----------- | ---- | ------- | ------- | --------- | -------------- | ------------ | --------- | ------------ | -------------- | --- |
|                                    |              |            |         |             |      |         |         | Figure 5: | Speed/accuracy |              | trade-off |              | of brute-force |     |
| tance computation                  |              | increases. |         |             |      |         |         |           |                |              |           |              |                |     |
|                                    |              |            |         |             |      |         |         | 10-NN     | graph          | construction | for       | the YFCC100M |                | and |
| 6.4 Billion-scaleapproximatesearch |              |            |         |             |      |         |         | DEEP1B    | datasets.      |              |           |              |                |     |
TherearefewstudiesonGPU-basedapproximatenearest-
| neighbor | search | on large | datasets |     | ((cid:96) (cid:29) 106). | We  | report a |     |     |     |     |     |     |     |
| -------- | ------ | -------- | -------- | --- | ------------------------ | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
different,itshowsthatmakingsearchesonGPUsisagame-
fewcomparisonpointshereonindexsearch,usingstandard
|          |                |          |          |               |             |          |         | changer in       | terms | of speed achievable |     | on a | single machine. |     |
| -------- | -------------- | -------- | -------- | ------------- | ----------- | -------- | ------- | ---------------- | ----- | ------------------- | --- | ---- | --------------- | --- |
| datasets | and evaluation |          | protocol | in            | this field. |          |         |                  |       |                     |     |      |                 |     |
|          |                |          |          |               |             |          |         | 6.5 Thek-NNgraph |       |                     |     |      |                 |     |
| SIFT1M.  | For            | the sake | of       | completeness, |             | we first | compare |                  |       |                     |     |      |                 |     |
ourGPUsearchspeedonSift1Mwiththeimplementation An example usage of our similarity search method is to
|                         |     |     |                               |     |     |     |     | construct  | a k-nearest | neighbor        | graph | of a   | dataset | via brute |
| ----------------------- | --- | --- | ----------------------------- | --- | --- | --- | --- | ---------- | ----------- | --------------- | ----- | ------ | ------- | --------- |
| ofWiescholleketal.[47]. |     |     | Theyobtainanearestneighborre- |     |     |     |     |            |             |                 |       |        |         |           |
|                         |     |     |                               |     |     |     |     | force (all | vectors     | queried against | the   | entire | index). |           |
callat1(fractionofquerieswherethetruenearestneighbor
is in the top 1 result) of R@1=0.51, and R@100=0.86 in Experimental setup. We evaluate the trade-off between
0.02ms per query on a Titan X. For the same time budget, speed, precision and memory on two datasets: 95 million
our implementation obtains R@1=0.80 and R@100=0.95. images from the Yfcc100M dataset [42] and Deep1B. For
Yfcc100M,wecomputeCNNdescriptorsastheone-before-
SIFT1B.WecompareagainwithWiescholleketal.,onthe
Sift1Bdataset[26]of1billionSIFTimagefeaturesatn = last layer of a ResNet [23], reduced to d=128 with PCA.
q
104. We compare the search performance in terms of same The evaluation measures the trade-off between:
memoryusageforsimilaraccuracy(moreaccuratemethods
|     |     |     |     |     |     |     |     | • Speed: | How | much time | it takes | to build | the | IVFADC |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | --------- | -------- | -------- | --- | ------ |
may involve greater search time or memory usage). On a indexfromscratchandconstructthewholek-NNgraph
single GPU, with m=8 bytes per vector, R@10=0.376 in (k=10)bysearchingnearestneighborsforallvectors
17.7µs per query vector, versus their reported R@10=0.35 in the dataset. Thus, this is an end-to-end test that
in 150µs per query vector. Thus, our implementation is includes indexing as well as search time;
| more accurate |     | at a speed | 8.5× | faster. |     |     |     |            |     |               |        |     |       |         |
| ------------- | --- | ---------- | ---- | ------- | --- | --- | --- | ---------- | --- | ------------- | ------ | --- | ----- | ------- |
|               |     |            |      |         |     |     |     | • Quality: | We  | sample 10,000 | images | for | which | we com- |
DEEP1B.WealsoexperimentedontheDeep1Bdataset[6]
|                       |                                    |                     |     |             |            |      |         | pute                                           | the exact | nearest          | neighbors. | Our     | accuracy   | mea- |
| --------------------- | ---------------------------------- | ------------------- | --- | ----------- | ---------- | ---- | ------- | ---------------------------------------------- | --------- | ---------------- | ---------- | ------- | ---------- | ---- |
| of (cid:96)=1 billion |                                    | CNN representations |     |             | for images | at n | =104.   |                                                |           |                  |            |         |            |      |
|                       |                                    |                     |     |             |            |      | q       | sureisthefractionof10foundnearestneighborsthat |           |                  |            |         |            |      |
| The paper             | that                               | introduces          |     | the dataset | reports    | CPU  | results |                                                |           |                  |            |         |            |      |
|                       |                                    |                     |     |             |            |      |         | are                                            | within    | the ground-truth | 10         | nearest | neighbors. |      |
| (1thread):            | R@1=0.45in20mssearchtimepervector. |                     |     |             |            |      | We      |                                                |           |                  |            |         |            |      |
|                       |                                    |                     |     |             |            |      |         | Yfcc100M,                                      |           |                  |            |         | (216       |      |
use a PQ encoding of m = 20, with d = 80 via OPQ [17], For we use a coarse quantizer centroids),
|=218,
and |C 1 which uses a comparable dataset storage as andconsiderm=16,32and64bytePQencodingsforeach
Deep1B,
theoriginalpaper(20GB).ThisrequiresmultipleGPUsas vector. For we pre-process the vectors to d=120
itistoolargeforasingleGPU’sglobalmemory,sowecon- via OPQ, use |C | = 218 and consider m = 20, 40. For a
1
sider4GPUswithS =2,R=2. WeobtainaR@1=0.4517 given encoding, we vary τ from 1 to 256, to obtain trade-
in 0.0133ms per vector. While the hardware platforms are offs between efficiency and quality, as seen in Figure 5.
9

Figure 6: Path in the k-NN graph of 95 million images from YFCC100M. The first and the last image are
| given; | the algorithm |     | computes |     | the smoothest |     | path between | them. |     |     |     |     |     |     |
| ------ | ------------- | --- | -------- | --- | ------------- | --- | ------------ | ----- | --- | --- | --- | --- | --- | --- |
Discussion. For Yfcc100M we used S = 1, R = 4. An 7. CONCLUSION
| accuracy    | of more         | than | 0.8 is   | obtained | in     | 35 minutes. | For      |                |           |               |     |              |            |           |
| ----------- | --------------- | ---- | -------- | -------- | ------ | ----------- | -------- | -------------- | --------- | ------------- | --- | ------------ | ---------- | --------- |
|             |                 |      |          |          |        |             |          | The arithmetic |           | throughput    |     | and memory   | bandwidth  | of        |
| Deep1B,     | a lower-quality |      | graph    | can      | be     | built in    | 6 hours, |                |           |               |     |              |            |           |
|             |                 |      |          |          |        |             |          | GPUs are       | well into | the teraflops |     | and hundreds | of         | gigabytes |
| with higher | quality         |      | in about | half     | a day. | We also     | experi-  |                |           |               |     |              |            |           |
|             |                 |      |          |          |        |             |          | per second.    | However,  | implementing  |     |              | algorithms | that ap-  |
mented with more GPUs by doubling the replica set, us- proach these performance levels is complex and counter-
ing 8 Maxwell M40s (the M40 is roughly equivalent in per- intuitive. Inthispaper,wepresentedthealgorithmicstruc-
formance to the Titan X). Performance is improved sub- tureofsimilaritysearchmethodsthatachievesnear-optimal
linearly (∼1.6× for m=20, ∼1.7× for m=40). performance on GPUs.
For comparison, the largest k-NN graph construction we This work enables applications that needed complex ap-
| are aware  | of    | used a | dataset   | comprising |         | 36.5 million | 384-  |           |            |         |     |          |     |            |
| ---------- | ----- | ------ | --------- | ---------- | ------- | ------------ | ----- | --------- | ---------- | ------- | --- | -------- | --- | ---------- |
|            |       |        |           |            |         |              |       | proximate | algorithms | before. | For | example, | the | approaches |
| d vectors, | which | took   | a cluster | of         | 128 CPU | servers      | 108.7 |           |            |         |     |          |     |            |
presentedheremakeitpossibletodoexactk-meanscluster-
| hours of     | compute | [45],     | using    | NN-Descent |            | [15].  | Note that |              |         |                     |       |         |               |             |
| ------------ | ------- | --------- | -------- | ---------- | ---------- | ------ | --------- | ------------ | ------- | ------------------- | ----- | ------- | ------------- | ----------- |
|              |         |           |          |            |            |        |           | ing or to    | compute | the k-NN            | graph | with    | simple        | brute-force |
| NN-Descent   | could   | also      | build    | or refine  | the        | k-NN   | graph for |              |         |                     |       |         |               |             |
|              |         |           |          |            |            |        |           | approaches   | in less | time than           | a     | CPU (or | a cluster     | of them)    |
| the datasets | we      | consider, | but      | it has     | a large    | memory | over-     |              |         |                     |       |         |               |             |
|              |         |           |          |            |            |        |           | would take   | to do   | this approximately. |       |         |               |             |
| head over    | the     | graph     | storage, | which      | is already |        | 80 GB for |              |         |                     |       |         |               |             |
|              |         |           |          |            |            |        |           | GPU hardware |         | is now              | very  | common  | on scientific | work-       |
Deep1B.Moreoveritrequiresrandomaccessacrossallvec-
|     |     |     |     |     |     |     |     | stations, | due to their | popularity |     | for machine | learning | algo- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------------ | ---------- | --- | ----------- | -------- | ----- |
Deep1B).
tors (384GB for rithms. Webelievethatourworkfurtherdemonstratestheir
The largest GPU k-NN graph construction we found is a interestfordatabaseapplications. Alongwiththiswork,we
brute-forceconstructionusingexactsearchwithGEMM,of arepublishingacarefullyengineeredimplementationofthis
adatasetof20million15,000-dvectors,whichtookacluster paper’salgorithms,sothattheseGPUscannowalsobeused
| of 32 Tesla    | C2050      | GPUs | 10       | days [14]. | Assuming       |         | computa- |               |            |         |     |     |     |     |
| -------------- | ---------- | ---- | -------- | ---------- | -------------- | ------- | -------- | ------------- | ---------- | ------- | --- | --- | --- | --- |
|                |            |      |          |            |                |         |          | for efficient | similarity | search. |     |     |     |     |
| tion scales    | with       | GEMM | cost     | for the    | distance       | matrix, | this     |               |            |         |     |     |     |     |
| approach       | for Deep1B |      | would    | take       | an impractical |         | 200 days |               |            |         |     |     |     |     |
| of computation |            | time | on their | cluster.   |                |         |          | 8. REFERENCES |            |         |     |     |     |     |
[1] T.Alabi,J.D.Blanchard,B.Gordon,andR.Steinbach.
6.6 Usingthek-NNgraph Fastk-selectionalgorithmsforgraphicsprocessingunits.
|      |        |       |     |                  |     |     |          | ACM | Journal | of Experimental |     | Algorithmics, |     |     |
| ---- | ------ | ----- | --- | ---------------- | --- | --- | -------- | --- | ------- | --------------- | --- | ------------- | --- | --- |
| When | a k-NN | graph | has | been constructed |     | for | an image |     |         |                 |     |               |     |     |
17:4.2:4.1–4.2:4.29,October2012.
| dataset, | we can | find | paths | in the | graph | between | any two |     |     |     |     |     |     |     |
| -------- | ------ | ---- | ----- | ------ | ----- | ------- | ------- | --- | --- | --- | --- | --- | --- | --- |
[2] F.Andr´e,A.-M.Kermarrec,andN.L.Scouarnec.Cache
images,providedthereisasingleconnectedcomponent(this
|     |     |     |     |     |     |     |     | localityisnotenough: |     |     | High-performancenearestneighbor |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | ------------------------------- | --- | --- | --- |
is the case). For example, we can search the shortest path searchwithproductquantizationfastscan.InProc.
between two images of flowers, by propagating neighbors International Conference on Very Large DataBases,pages
| from a starting |     | image | to a destination |     | image. | Denoting | by  | 288–299,2015. |     |     |     |     |     |     |
| --------------- | --- | ----- | ---------------- | --- | ------ | -------- | --- | ------------- | --- | --- | --- | --- | --- | --- |
[3] Y.Avrithis,Y.Kalantidis,E.Anagnostopoulos,andI.Z.
| S and D | the | source | and destination |     | images, | and | d ij the |     |     |     |     |     |     |     |
| ------- | --- | ------ | --------------- | --- | ------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
Emiris.Web-scaleimageclusteringrevisited.InProc.
distancebetweennodes,wesearchthepathP ={p 1 ,...,p n } International Conference on Computer Vision,pages
| with p 1 | =S and | p n =D | such | that |     |     |     | 1502–1510,2015. |     |     |     |     |     |     |
| -------- | ------ | ------ | ---- | ---- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- |
[4] A.BabenkoandV.Lempitsky.Theinvertedmulti-index.
min max d , (12) InProc. IEEE Conference on Computer Vision and
pipi+1
|     |     |     | P i=1..n |     |     |     |     | Pattern | Recognition,pages3069–3076,June2012. |     |     |     |     |     |
| --- | --- | --- | -------- | --- | --- | --- | --- | ------- | ------------------------------------ | --- | --- | --- | --- | --- |
[5] A.BabenkoandV.Lempitsky.Improvingbilayerproduct
i.e., we want to favor smooth transitions. An example re- quantizationforbillion-scaleapproximatenearestneighbors
|         |       |           |     |                 |     |     |            | inhighdimensions.arXiv |     |     | preprint | arXiv:1404.1831,2014. |     |     |
| ------- | ----- | --------- | --- | --------------- | --- | --- | ---------- | ---------------------- | --- | --- | -------- | --------------------- | --- | --- |
| sult is | shown | in Figure | 6   | from Yfcc100M4. |     |     | It was ob- |                        |     |     |          |                       |     |     |
[6] A.BabenkoandV.Lempitsky.Efficientindexingof
tainedafter20secondsofpropagationinak-NNgraphwith
|                |                 |                                    |             |     |     |     |     | billion-scaledatasetsofdeepdescriptors.InProc. |     |          |        |     |                      | IEEE |
| -------------- | --------------- | ---------------------------------- | ----------- | --- | --- | --- | --- | ---------------------------------------------- | --- | -------- | ------ | --- | -------------------- | ---- |
| k=15neighbors. |                 | Sincetherearemanyflowerimagesinthe |             |     |     |     |     |                                                |     |          |        |     |                      |      |
|                |                 |                                    |             |     |     |     |     | Conference                                     | on  | Computer | Vision | and | Pattern Recognition, |      |
| dataset,       | the transitions |                                    | are smooth. |     |     |     |     |                                                |     |          |        |     |                      |      |
pages2055–2063,June2016.
[7] R.Barrientos,J.Go´mez,C.Tenllado,M.Prieto,and
M.Marin.knnqueryprocessinginmetricspacesusing
4The mapping from vectors to images is not available for GPUs.InInternational European Conference on Parallel
| Deep1B |     |     |     |     |     |     |     | and Distributed |     | Computing,volume6852ofLecture |     |     |     | Notes |
| ------ | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ----------------------------- | --- | --- | --- | ----- |
10

in Computer Science,pages380–392,Bordeaux,France, and Signal Processing,pages861–864,May2011.
September2011.Springer. [27] Y.KalantidisandY.Avrithis.Locallyoptimizedproduct
[8] K.E.Batcher.Sortingnetworksandtheirapplications.In quantizationforapproximatenearestneighborsearch.In
Proc. Spring Joint Computer Conference,AFIPS’68 Proc. IEEE Conference on Computer Vision and Pattern
(Spring),pages307–314,NewYork,NY,USA,1968.ACM. Recognition,pages2329–2336,June2014.
[9] P.Boncz,W.Lehner,andT.Neumann.Specialissue: [28] A.Krizhevsky,I.Sutskever,andG.E.Hinton.Imagenet
Modernhardware.The VLDB Journal,25(5):623–624, classificationwithdeepconvolutionalneuralnetworks.In
2016. Advances in Neural Information Processing Systems,pages
[10] J.Canny,D.L.W.Hall,andD.Klein.Amulti-teraflop 1097–1105,2012.
constituencyparserusingGPUs.InProc. Empirical [29] F.T.Leighton.Introduction to Parallel Algorithms and
MethodsonNaturalLanguageProcessing,pages1898–1907. Architectures: Array, Trees, Hypercubes.Morgan
ACL,2013. KaufmannPublishersInc.,SanFrancisco,CA,USA,1992.
[11] J.CannyandH.Zhao.Bidmach: Large-scalelearningwith [30] E.Lindholm,J.Nickolls,S.Oberman,andJ.Montrym.
zeromemoryallocation.InBigLearn workshop, NIPS, NVIDIATesla: aunifiedgraphicsandcomputing
2013. architecture.IEEE Micro,28(2):39–55,March2008.
[12] B.Catanzaro,A.Keller,andM.Garland.Adecomposition [31] W.LiuandB.Vinter.Ad-heap: Anefficientheapdata
forin-placematrixtransposition.InProc. ACM structureforasymmetricmulticoreprocessors.InProc. of
Symposium on Principles and Practice of Parallel Workshop on General Purpose Processing Using GPUs,
Programming,PPoPP’14,pages193–206,2014. pages54:54–54:63.ACM,2014.
[13] J.Chhugani,A.D.Nguyen,V.W.Lee,W.Macy, [32] T.Mikolov,I.Sutskever,K.Chen,G.S.Corrado,and
M.Hagog,Y.-K.Chen,A.Baransi,S.Kumar,and J.Dean.Distributedrepresentationsofwordsandphrases
P.Dubey.Efficientimplementationofsortingonmulti-core andtheircompositionality.InAdvances in Neural
simdcpuarchitecture.Proc. VLDB Endow., Information Processing Systems,pages3111–3119,2013.
1(2):1313–1324,August2008. [33] L.Monroe,J.Wendelberger,andS.Michalak.Randomized
[14] A.Dashti.Efficientcomputationofk-nearestneighbor selectionontheGPU.InProc. ACM Symposium on High
graphsforlargehigh-dimensionaldatasetsongpuclusters. Performance Graphics,pages89–98,2011.
Master’sthesis,UniversityofWisconsinMilwaukee,August [34] M.NorouziandD.Fleet.Cartesiank-means.InProc.
2013. IEEE Conference on Computer Vision and Pattern
[15] W.Dong,M.Charikar,andK.Li.Efficientk-nearest Recognition,pages3017–3024,June2013.
neighborgraphconstructionforgenericsimilaritymeasures. [35] M.Norouzi,A.Punjani,andD.J.Fleet.Fastsearchin
InWWW: Proceeding of the International Conference on Hammingspacewithmulti-indexhashing.InProc. IEEE
World Wide Web,pages577–586,March2011. Conference on Computer Vision and Pattern Recognition,
[16] M.Douze,H.J´egou,andF.Perronnin.Polysemouscodes. pages3108–3115,2012.
InProc. European Conference on Computer Vision,pages [36] J.PanandD.Manocha.FastGPU-basedlocalitysensitive
785–801.Springer,October2016. hashingfork-nearestneighborcomputation.InProc. ACM
[17] T.Ge,K.He,Q.Ke,andJ.Sun.Optimizedproduct International Conference on Advances in Geographic
quantization.IEEE Trans. PAMI,36(4):744–755,2014. Information Systems,pages211–220,2011.
[18] Y.GongandS.Lazebnik.Iterativequantization: A [37] L.Paulev´e,H.J´egou,andL.Amsaleg.Localitysensitive
procrusteanapproachtolearningbinarycodes.InProc. hashing: acomparisonofhashfunctiontypesandquerying
IEEE Conference on Computer Vision and Pattern mechanisms.Pattern recognition letters,31(11):1348–1358,
Recognition,pages817–824,June2011. August2010.
[19] Y.Gong,L.Wang,R.Guo,andS.Lazebnik.Multi-scale [38] O.Shamir.Fundamentallimitsofonlineanddistributed
orderlesspoolingofdeepconvolutionalactivationfeatures. algorithmsforstatisticallearningandestimation.In
InProc. European Conference on Computer Vision,pages Advances in Neural Information Processing Systems,pages
392–407,2014. 163–171,2014.
[20] A.Gordo,J.Almazan,J.Revaud,andD.Larlus.Deep [39] A.SharifRazavian,H.Azizpour,J.Sullivan,and
imageretrieval: Learningglobalrepresentationsforimage S.Carlsson.CNNfeaturesoff-the-shelf: anastounding
search.InProc. European Conference on Computer Vision, baselineforrecognition.InCVPR workshops,pages
pages241–257,2016. 512–519,2014.
[21] S.Han,H.Mao,andW.J.Dally.Deepcompression: [40] N.Sismanis,N.Pitsianis,andX.Sun.Parallelsearchof
Compressingdeepneuralnetworkswithpruning,trained k-nearestneighborswithsynchronousoperations.InIEEE
quantizationandhuffmancoding.arXiv preprint High Performance Extreme Computing Conference,pages
arXiv:1510.00149,2015. 1–6,2012.
[22] K.He,F.Wen,andJ.Sun.K-meanshashing: An [41] X.Tang,Z.Huang,D.M.Eyers,S.Mills,andM.Guo.
affinity-preservingquantizationmethodforlearningbinary Efficientselectionalgorithmforfastk-nnsearchonGPUs.
compactcodes.InProc. IEEE Conference on Computer InIEEE International Parallel & Distributed Processing
Vision and Pattern Recognition,pages2938–2945,June Symposium,pages397–406,2015.
2013. [42] B.Thomee,D.A.Shamma,G.Friedland,B.Elizalde,
[23] K.He,X.Zhang,S.Ren,andJ.Sun.Deepresidual K.Ni,D.Poland,D.Borth,andL.-J.Li.YFCC100M:The
learningforimagerecognition.InProc. IEEE Conference newdatainmultimediaresearch.Communications of the
on Computer Vision and Pattern Recognition,pages ACM,59(2):64–73,January2016.
770–778,June2016. [43] V.VolkovandJ.W.Demmel.BenchmarkingGPUstotune
[24] X.He,D.Agarwal,andS.K.Prasad.Designand denselinearalgebra.InProc. ACM/IEEE Conference on
implementationofaparallelpriorityqueueonmany-core Supercomputing,pages31:1–31:11,2008.
architectures.IEEE International Conference on High [44] A.WakataniandA.Murakami.GPGPUimplementationof
Performance Computing,pages1–10,2012. nearestneighborsearchwithproductquantization.In
[25] H.J´egou,M.Douze,andC.Schmid.Productquantization IEEEInternationalSymposiumonParallelandDistributed
fornearestneighborsearch.IEEE Trans. PAMI, Processing with Applications,pages248–253,2014.
33(1):117–128,January2011. [45] T.Warashina,K.Aoyama,H.Sawada,andT.Hattori.
[26] H.J´egou,R.Tavenard,M.Douze,andL.Amsaleg. Efficientk-nearestneighborgraphconstructionusing
Searchinginonebillionvectors: re-rankwithsource mapreduceforlarge-scaledatasets.IEICE Transactions,
coding.InInternational Conference on Acoustics, Speech,
11

97-D(12):3142–3154,2014. The last case is the probability of: there is a (cid:96)−1 se-
[46] R.Weber,H.-J.Schek,andS.Blott.Aquantitative quence with m−1 successive min-k elements preceding us,
analysisandperformancestudyforsimilarity-search and the current element is in the successive min-k, or the
methodsinhigh-dimensionalspaces.InProc. International current element is not in the successive min-k, m ones are
ConferenceonVeryLargeDataBases,pages194–205,1998.
beforeus. Wecanthendeveloparecurrencerelationshipfor
[47] P.Wieschollek,O.Wang,A.Sorkine-Hornung,and
π((cid:96),k,t,1). Note that
H.P.A.Lensch.Efficientlarge-scaleapproximatenearest
neighborsearchontheGPU.InProc. IEEE Conference on
Computer Vision and Pattern Recognition,pages
min((bt+max(0,t−1)),(cid:96))
2027–2035,June2016. (cid:88)
δ((cid:96),b,k,t):= γ((cid:96),m,k) (17)
[48] S.Williams,A.Waterman,andD.Patterson.Roofline: An
insightfulvisualperformancemodelformulticore m=bt
architectures.Communications of the ACM,52(4):65–76,
for b where 0 ≤ bt ≤ (cid:96) is the fraction of all sequences of
April2009.
length(cid:96)thatwillforcebsortsofdatabywinningthethread
Appendix: Complexityanalysisof WarpSelect queue ballot, as there have to be bt to (bt+max(0,t−1))
elementsinthesuccessivemin-kforthesesortstohappen(as
Wederivetheaveragenumberoftimesupdatesaretriggered the min-k elements will overflow the thread queues). There
in WarpSelect, for use in Section 4.3. are at most (cid:98)(cid:96)/t(cid:99) won ballots that can occur, as it takes t
Let the input to k-selection be a sequence {a 1 ,a 2 ,...,a (cid:96) } separate sequential current min-k seen elements to win the
(1-basedindexing),arandomlychosenpermutationofaset ballot. π((cid:96),k,t,1) is thus the expectation of this over all
of distinct elements. Elements are read sequentially in c possible b:
groups of size w (the warp; in our case, w = 32); assume (cid:96)
is a multiple of w, so c = (cid:96)/w. Recall that t is the thread
(cid:98)(cid:96)/t(cid:99)
queue length. We call elements prior to or at position n (cid:88)
π((cid:96),k,t,1)= b·δ((cid:96),b,k,t). (18)
in the min-k seen so far the successive min-k (at n). The
likelihood that a is in the successive min-k at n is: b=1
n
This can be computed by dynamic programming. Analyti-
(cid:40) cally, notethatfort=1,k=1, π((cid:96),1,1,1)istheharmonic
1 if n≤k
α(n,k):= (13) numberH =1+1+1+...+1,whichconvergestoln((cid:96))+γ
k/n if n>k (cid:96) 2 3 (cid:96)
(the Euler-Mascheroni constant γ) as (cid:96)→∞.
as each a , n>k has a k/n chance as all permutations are
n
equally likely, and all elements in the first k qualify. For t = 1,k > 1,(cid:96) > k, π((cid:96),k,1,1) = k+k(H (cid:96) −H k )
or O(klog((cid:96))), as the first k elements are in the successive
Counting the insertion sorts. In a given lane, an inser-
min-k,andtheexpectationfortherestis k + k +...+k.
tionsortistriggerediftheincomingvalueisinthesuccessive k+1 k+2 (cid:96)
min-k+tvalues,butthelanehas“seen”onlywc +(c−c )
0 0 For t>1,k >1,(cid:96)>k, note that there are some number
values,wherec isthepreviouswonwarpballot. Theprob-
0 D, k ≤ D ≤ (cid:96) of successive min-k determinations D made
ability of this happening is:
foreachpossible{a ,...,a }. Thenumberofwonballotsfor
1 (cid:96)
k+t each case is by definition (cid:98)D/t(cid:99), as the thread queue must
α(wc +(c−c ),k+t)≈ for c>k. (14)
0 0 wc fill up t times. Thus, π((cid:96),k,t,1)=O(klog((cid:96))/t).
Theapproximationconsidersthatthethreadqueuehasseen
Multiple lanes. The w > 1 case is complicated by the
all the wc values, not just those assigned to its lane. The
fact that there are joint probabilities to consider (if more
probability of any lane triggering an insertion sort is then:
than one of the w workers triggers a sort for a given group,
(cid:18)
k+t
(cid:19)w
k+t only one sort takes place). However, the likelihood can be
1− 1− ≈ . (15)
wc c bounded. Let π(cid:48)((cid:96),k,t,w) be the expected won ballots as-
suming no mutual interference between the w workers for
Here the approximation is a first-order Taylor expansion.
winning ballots (i.e., we win b ballots if there are b ≤ w
Summinguptheprobabilitiesovercgivesanexpectednum-
workers that independently win a ballot at a single step),
ber of insertions of N ≈(k+t)log(c)=O(klog((cid:96)/w)).
2 butwiththesharedmin-k setaftereachsortfromthejoint
Counting full sorts. We seek N 3 = π((cid:96),k,t,w), the ex- sequence. Assume that k≥w. Then:
pected number of full sorts required for WarpSelect.
Single lane. For now, we assume w = 1, so c = (cid:96). Let (cid:32)(cid:24) (cid:25) (cid:100)(cid:96)/w(cid:101)−(cid:100)k/w(cid:101) (cid:33)
γ((cid:96),m,k)betheprobabilitythatinansequence{a 1 ,...,a (cid:96) }, π(cid:48)((cid:96),k,1,w)≤w k + (cid:88) k
w w((cid:100)k/w(cid:101)+i)
exactly m of the elements as encountered by a sequential
i=1
scanner(w=1)areinthesuccessivemin-k. Givenm,there ≤wπ((cid:100)(cid:96)/w(cid:101),k,1,1)=O(wklog((cid:96)/w))
are
(cid:0)
m
(cid:96)(cid:1)
places where these successive min-k elements can (19)
occur. It is given by a recurrence relation: where the likelihood of the w workers seeing a successive
min-kelementhasanupperboundofthatofthefirstworker

1 (cid:96)=0 and m=0 ateachstep. Asbefore,thenumberofwonballotsisscaled

0 (cid:96)=0 and m>0 by t, so π(cid:48)((cid:96),k,t,w) = O(wklog((cid:96)/w)/t). Mutual interfer-
encecanonlyreducethenumberofballots,soweobtainthe
γ((cid:96),m,k):= 0 (cid:96)>0 and m=0

(
γ
γ
(
(
(cid:96)
(cid:96)
−
−
1
1
,
,
m
m
,k
−
)·
1
(
,
1
k)
−
·α
α
(
(
(cid:96)
(cid:96)
,
,
k
k
)
)
+
)) otherwise.
same upper bound for π((cid:96),k,t,w).
(16)
12