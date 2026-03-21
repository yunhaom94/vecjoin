| Xling:           |     | A         | Learned |     | Filter |             | Framework |        |     |            | for       | Accelerating |      |      |     |
| ---------------- | --- | --------- | ------- | --- | ------ | ----------- | --------- | ------ | --- | ---------- | --------- | ------------ | ---- | ---- | --- |
| High-Dimensional |     |           |         |     |        | Approximate |           |        |     | Similarity |           |              |      | Join |     |
|                  |     | 1st Yifan | Wang    |     |        | 2nd         | Vyom      | Pathak |     |            | 3rd Daisy | Zhe          | Wang |      |     |
University of Florida University of Florida University of Florida
|     |     | wangyifan@ufl.edu |     |     |     |     | v.pathak@ufl.edu |     |     |     | daisyw@ufl.edu |     |     |     |     |
| --- | --- | ----------------- | --- | --- | --- | --- | ---------------- | --- | --- | --- | -------------- | --- | --- | --- | --- |
Abstract—Similarityjoinisacriticalandwidelyusedoperation the data representation in a wide range of applications, which
in multi-dimensional data applications, which finds all pairs of raises the demands for effective and efficient similarity join
4202 beF 02  ]BD.sc[  1v79331.2042:viXra
| close points | within  | a given       | distance | threshold.       |           | Being studied | for |                       |           |      |             |      |              |             |       |
| ------------ | ------- | ------------- | -------- | ---------------- | --------- | ------------- | --- | --------------------- | --------- | ---- | ----------- | ---- | ------------ | ----------- | ----- |
|              |         |               |          |                  |           |               |     | over high-dimensional |           |      | data. Those |      | applications | include     | near- |
| decades,     | many    | similarity    | join     | methods          | have been | proposed,     | but |                       |           |      |             |      |              |             |       |
|              |         |               |          |                  |           |               |     | duplicate             | detection | [1], | [2], [3],   | [4], | [5], data    | integration | [6],  |
| they are     | usually | not efficient | on       | high-dimensional |           | space         | due | to                    |           |      |             |      |              |             |       |
[7],[8],dataexploration[9],[10],[11],privacy[12],[13]and
| the curse | of dimensionality |     | and | data-unawareness. |     | Inspired | by  |     |     |     |     |     |     |     |     |
| --------- | ----------------- | --- | --- | ----------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
theBloomjoininRDBMS,weinvestigatethepossibilityofusing so on. Specifically, distance between embeddings reflects the
metric space Bloom filter (MSBF), a family of data structures semanticsimilaritybetweenthedataobjects,meaningthatthe
| checking   | if a query | point         | has  | neighbors      | in a | multi-dimensional |         |              |                |               |                |                 |          |                 |        |
| ---------- | ---------- | ------------- | ---- | -------------- | ---- | ----------------- | ------- | ------------ | -------------- | ------------- | -------------- | --------------- | -------- | --------------- | ------ |
|            |            |               |      |                |      |                   |         | applications | have           | to frequently |                | search          | for      | close points    | in the |
| space, to  | speed      | up similarity |      | join. However, |      | there are         | several |              |                |               |                |                 |          |                 |        |
|            |            |               |      |                |      |                   |         | embedding    | space,         | i.e.,         | the similarity |                 | join. In | many real-world |        |
| challenges | when       | applying      | MSBF | to similarity  |      | join, including   |         |              |                |               |                |                 |          |                 |        |
|            |            |               |      |                |      |                   |         | use cases,   | the similarity |               | join           | is approximate, |          | i.e., they      | do not |
excessiveinformationloss,data-unawarenessandhardconstraint
onthedistancemetric,becauseofwhichfewworksaredesigned require100%accurateresults,butdodemandhighprocessing
in this way. speed, especially on large-scale data. A typical example is
Inthispaper,weproposeXling,agenericframeworktobuild
|                  |        |               |            |             |              |            |       | near-duplicate | video        | retrieval |           | [3] that | identifies | online     | videos |
| ---------------- | ------ | ------------- | ---------- | ----------- | ------------ | ---------- | ----- | -------------- | ------------ | --------- | --------- | -------- | ---------- | ---------- | ------ |
| a learning-based |        | metric        | space      | filter with | any existing | regression |       |                |              |           |           |          |            |            |        |
|                  |        |               |            |             |              |            |       | with identical |              | or almost | identical | content  |            | during the | search |
| model, aiming    |        | at accurately | predicting |             | whether      | a query    | point |                |              |           |           |          |            |            |        |
|                  |        |               |            |             |              |            |       | process        | to diversify | the       | video     | search   | results,   | in which   | case   |
| has enough       | number | of            | neighbors. | The         | framework    | provides   |       | a              |              |           |           |          |            |            |        |
suiteofoptimizationstrategiestofurtherimprovetheprediction missing a few pairs of similar videos is acceptable, while fast
quality based on the learning model, which has demonstrated response is required.
| significantly | higher  | prediction |            | quality            | than existing | MSBF.       | We     |                 |         |              |       |            |       |          |           |
| ------------- | ------- | ---------- | ---------- | ------------------ | ------------- | ----------- | ------ | --------------- | ------- | ------------ | ----- | ---------- | ----- | -------- | --------- |
|               |         |            |            |                    |               |             |        | Existing        | work    | on efficient |       | similarity | join  | mainly   | includes  |
| also propose  | XJoin,  | one        | of the     | first filter-based |               | similarity  | join   |                 |         |              |       |            |       |          |           |
|               |         |            |            |                    |               |             |        | two categories: |         | space-grid   | [14], | [15],      | [16], | [17] and | locality- |
| methods,      | based   | on Xling.  | By         | predicting         | and           | skipping    | those  |                 |         |              |       |            |       |          |           |
|               |         |            |            |                    |               |             |        | sensitive       | hashing | (LSH)        | based | methods    | [18], | [19],    | [4], [5], |
| queries       | without | enough     | neighbors, | XJoin              | can           | effectively | reduce |                 |         |              |       |            |       |          |           |
unnecessary neighbor searching and therefore it achieves a [12], [13]. The former splits the data space into grids and
remarkable acceleration. Benefiting from the generalization ca- joinsthepointswithinthesameorneighboringgrids,whilethe
pabilityofdeeplearningmodels,XJoincanbeeasilytransferred
latterisessentiallyanadoptionofRDBMShash-joinprinciple
| onto new     | dataset | (in           | similar     | distribution) | without       | re-training. |        |          |                  |         |        |            |         |             |          |
| ------------ | ------- | ------------- | ----------- | ------------- | ------------- | ------------ | ------ | -------- | ---------------- | ------- | ------ | ---------- | ------- | ----------- | -------- |
|              |         |               |             |               |               |              |        | onto the | high-dimensional |         | join,  | i.e.,      | hashing | one dataset | by       |
| Furthermore, |         | Xling is      | not limited | to            | being applied | in           | XJoin, |          |                  |         |        |            |         |             |          |
|              |         |               |             |               |               |              |        | LSH and  | then             | probing | it for | the points | in      | another     | dataset. |
| instead,     | it acts | as a flexible | plugin      | that          | can be        | inserted     | to any |          |                  |         |        |            |         |             |          |
loop-basedsimilarityjoinmethodsforaspeedup.Ourevaluation However,thegrid-basedmethodspoorlyperforminveryhigh-
showsthatXlingnotonlyleadstothehighperformanceofXJoin dimensionalspaceduetothecurseofdimensionality,whilethe
(e.g.,beingupto17xfasterthanthebaselineswhilemaintaining unawareness for data distribution usually causes a non-trivial
ahighquality),butalsobeabletofurtherspeedupmanyexisting
|            |                  |         |              |                  |     |      |         | performance | degradation |          | to LSH-based |     | methods    | on      | unevenly |
| ---------- | ---------------- | ------- | ------------ | ---------------- | --- | ---- | ------- | ----------- | ----------- | -------- | ------------ | --- | ---------- | ------- | -------- |
| similarity | join             | methods | with quality | guarantee.       |     |      |         |             |             |          |              |     |            |         |          |
|            |                  |         |              |                  |     |      |         | distributed | data        | [20]. In | addition,    | the | grid-based | methods | are      |
| Index      | Terms—similarity |         | join,        | high-dimensional |     | data | manage- |             |             |          |              |     |            |         |          |
ment, machine learning usually exact while LSH-based methods are approximate, i.e.,
|     |     |     |     |     |     |     |     | their accuracies |     | are respectively |     | 100% | and | lower than | 100%. |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ---------------- | --- | ---- | --- | ---------- | ----- |
I. INTRODUCTION In this paper we focus on approximate similarity join.
In multi-dimensional data management, metric space range There is one more possible way that speeds up similarity
search (shortly called range search) and similarity join are joinwithmetricspaceBloomfilter,inspiredbytheBloomjoin
critical operators. Given a distance threshold ϵ, the former in RDBMS (which uses a Bloom filter to prune unnecessary
operation finds all points in a dataset D whose distance to probings). Metric space Bloom filter (MSBF) is designed for
a given query point is less than ϵ, while the latter operation checking whether a query point has neighbors within the
finds all pairs of points between two datasets R and S whose given distance threshold. Among the various MSBFs [21],
distance is less than ϵ. As range search can be seen as a [22], [23], [24], [25], [26], [27], Locality-Sensitive Bloom
special case of similarity join where |R| = 1 or |S| = 1, Filter (LSBF) [21] is the most widely used, based on which a
unless it is necessary, we will only discuss similarity join substantialnumberofMSBFshavebeendeveloped.Mirroring
in this paper. With the emergence of deep learning, high- to the hashing functions in Bloom filter, LSBF utilizes LSH
dimensional neural embedding has been widely adopted as functions to map a multi-dimensional point to several bits

in the bit array, and determines the neighbor existence by efficiency with tiny or no quality loss. We have applied
counting the non-zero bits. Given datasets R and S, an LSBF Xling to a brute-force nested-loop similarity join, named
canbebuiltonRandeachpoints∈S willactasaquery.By XJoin, which achieves significantly higher efficiency (up to
skipping the range search for those negative queries (i.e., the 14.6x faster) than the existing high-performance similarity
queries having no neighbors in R), the similarity join can be join methods (some are used in industry), with a guarantee
accelerated.NotethatunlikeBloomfilter,mostMSBFscannot of high quality. In these applications, filtering-by-counting
guarantee a zero false negative rate since they are based on enables Xling to help the base similarity join method ignore
LSH which raises both false positives and negatives. thequerieshavingonlyatrivialnumberofneighbors(e.g.,3or
According to our evaluation, negative queries usually take 5, or even 50), which makes the acceleration more significant
up a non-trivial portion (20% ∼ 90%), meaning that the fil- with tiny sacrifice of recall. In addition, we also apply Xling
teringshouldresultinasignificantperformanceimprovement. onto those prior methods and show that they are substantially
But few methods are designed in such a way, due to several accelerated with slightly more quality loss. Finally, XJoin and
problems of MSBF: (1) Given the fact that they are built on Xling are evaluated on their generalization capability, and the
top of LSH, their effectiveness is also limited by the data- results prove that they can be transferred to updated or fully
unawareness. (2) They lose more information compared to new dataset without re-training the learning model. To our
the original LSH because of further mapping LSH values best knowledge, We are the first to propose such a learning-
to one-dimension bit array, which additionally lowers their basedMSBFandXJoinisamongthefirstpracticalfilter-based
effectiveness. (3) They indicate the index of target bit by the similarity join methods for high-dimensional data.
LSH value, and this disables them to support many popular The main contributions of this paper are as follows:
distance metrics, like cosine distance where the LSH values 1) We propose XJoin, the first filter-based similarity join
are always 0 or 1. method for high-dimensional data, which is both effi-
| Inspired | by  | the “learned | Bloom | filter” | [28] | that enhances |     |       |                |     |     |     |     |     |
| -------- | --- | ------------ | ----- | ------- | ---- | ------------- | --- | ----- | -------------- | --- | --- | --- | --- | --- |
|          |     |              |       |         |      |               |     | cient | and effective. |     |     |     |     |     |
Bloom filter with machine learning, we propose a new type 2) WeproposeXling,agenericframeworkforconstructing
| of MSBF | based | on  | machine learning |     | techniques | which | ad- |         |        |       |       |         |              |         |
| ------- | ----- | --- | ---------------- | --- | ---------- | ----- | --- | ------- | ------ | ----- | ----- | ------- | ------------ | ------- |
|         |       |     |                  |     |            |       |     | learned | metric | space | Bloom | filters | with general | regres- |
dresses the problems above. Specifically, in this paper, we sion models.
propose Xling, a generic framework for building a MSBF 3) WedesignperformanceoptimizationstrategiesinXling,
| with deep | learning | model. | Instead | of  | LSH, Xling |     | relies on |           |           |     |             |     |                    |     |
| --------- | -------- | ------ | ------- | --- | ---------- | --- | --------- | --------- | --------- | --- | ----------- | --- | ------------------ | --- |
|           |          |        |         |     |            |     |           | including | selection |     | of ϵ values | for | effective training | and |
the learned cardinality estimation techniques which utilize adaptive computing of XDT.
regression models to predict the number of neighbors for 4) We conduct extensive evaluation to show the efficiency,
range search before actually executing it. Xling is designed effectiveness,usefulnessandgeneralizationofXlingand
to be generic such that any cardinality estimator (or simply, XJoin, as well as the remarkable performance improve-
regressionmodel)canbeencapsulatedintoaneffectiveMSBF.
mentbyapplyingXlingtoothersimilarityjoinmethods.
Its core is a cardinality estimator with a Xling decision The rest of this paper is organized as follows: Section II
| threshold | (XDT). | For | a range query, | Xling | predicts | the | result |            |           |       |         |     |                |         |
| --------- | ------ | --- | -------------- | ----- | -------- | --- | ------ | ---------- | --------- | ----- | ------- | --- | -------------- | ------- |
|           |        |     |                |       |          |     |        | introduces | the prior | works | related | to  | the techniques | in this |
cardinality, then determines the query is positive (i.e., having paper.SectionIIIformallydefinesthekeyproblemsstudiedby
| enough neighbors) |     | if           | the prediction | exceeds | XDT,        | otherwise |      |            |         |           |           |     |             |            |
| ----------------- | --- | ------------ | -------------- | ------- | ----------- | --------- | ---- | ---------- | ------- | --------- | --------- | --- | ----------- | ---------- |
|                   |     |              |                |         |             |           |      | this paper | and the | important | notations |     | being used. | Section IV |
| it is negative    |     | (i.e., being | without        | enough  | neighbors). |           | Note |            |         |           |           |     |             |            |
presentsthearchitectureofXlingandtheworkflowofapplying
that we mention “enough neighbors” instead of “any neigh- Xlingtoenhancingsimilarityjoin.SectionVdiscussesdetails
bors”,whichrevealsanadvancedfeature:Xlingcandetermine
|                        |           |       |          |      |                  |     |       | about the  | optimization |     | strategies | integrated     | in Xling. | And |
| ---------------------- | --------- | ----- | -------- | ---- | ---------------- | --- | ----- | ---------- | ------------ | --- | ---------- | -------------- | --------- | --- |
| whether                | the query | point | has more | than | τ neighbors,     |     | where |            |              |     |            |                |           |     |
|                        |           |       |          |      |                  |     |       | Section VI | reports      | and | analyzes   | the evaluation | results.  |     |
| τ is a user-determined |           |       | number.  | And  | Xling downgrades |     | to    | a          |              |     |            |                |           |     |
general MSBF when τ =0. We call such a feature “filtering- II. RELATEDWORK
by-counting”. Learned Bloom filter: The learned Bloom filter is first
By learning the data distribution, Xling solves the data- proposedby[28]whichtreatstheexistencecheckinginBloom
unawareness problem, and essentially as a regressor, it is not filter as a classification task, thereby replaces the traditional
limited to any specific distance metric. Note that we have Bloom filter with a deep learning based binary classifier
mentionedthreethresholdsuntilnow,thedistancethresholdϵ, followed by an overflow Bloom filter (to double check the
the Xling decision threshold XDT, and the neighbor threshold negative outputs of the classifier to guarantee a zero false
τ. To make it clearer, we will indicate them respectively negative rate). And there have been many following works
with “distance threshold”, “decision threshold” and “neighbor that further improve the learned Bloom filter [29], [30], [31]
threshold”, or directly using their symbols. byaddingauxiliarycomponentsorimprovingtheperformance
Xling deploys novel optimization strategies to further im- of the hashing functions being used.
prove the performance, including strategy to select ϵ values Learned cardinality estimation: Learning models have
for effective training, and strategy to select the best XDT. been widely used to predict the number of neighbors for a
Furthermore, Xling can be applied as a plugin onto many metricspacerangesearch,whichiscalled“learnedcardinality
existing similarity join methods to significantly enhance their estimation”. The learned cardinality estimation techniques

treat the task as a regression problem and solve it using This section presents the critical notations frequently used
regression models. The state-of-the-art methods [32], [33], in this paper and defines the key problems being studied, i.e.,
[34], [35] are usually based on deep regression models to range search and similarity join. The notations are listed and
effectively learn the data distribution and make more accurate explained in Table I, and more details of them are introduced
prediction than the non-deep approaches. Recursive Model where they are first referred in this paper.
Index(RMI) [36] is a hierarchical learning model that consists In multi-dimensional space, range search is defined as the
of multiple sub-models, where each sub-model is a regression search of all data points whose distance to the query is
model like neural network. CardNet [33] consists of a feature smaller than a given threshold under some distance metric.
extraction model and a regression model. The raw data is And similarity join is to find all close point pairs whose
transformed by the feature extraction model into Hamming distance is less than a threshold between two datasets. The
space,whichwillthenusedbytheregressionmodeltopredict formal definitions are as below:
itscardinality.SelNet[35]predictsthecardinalitybyalearned Definition 1 (range search): Given a dataset P = {p i |i =
query-dependent piece-wise linear function. 1,2,...,n}, a distance metric d(·,·), a query point q and a
Metric space Bloom filter: DSBF [26] and LSBF [21] radius/thresholdϵ,rangesearchtriestofindasetofdatapoints
|     |     |     |     |     |     |     | P∗  |     |     | p∗ ∈P∗, | d(q,p∗)≤ϵ. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ---------- | --- | --- | --- | --- |
are two of the representatives for metric space Bloom filter such that for any
|     |     |     |     |     |     |     |     |     |     | i   |     | i   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(MSBF), and following them many MSBF variants and rel- Definition2(similarityjoin): GiventwodatasetsRandS,a
evant applications have been developed. [25] enables LSBF distancethresholdϵ,andadistancemetricd(·,·),thesimilarity
to handle multiple Euclidean distance granularity without re- joinbetweenRandS isdenotedbyR▷◁ S,whichcombines
ϵ
buildingthedatastructure.[24]extends[25]toHammingdis- each point r ∈ R with each point s ∈ S that is close/similar
tance. [23] proposes a DSBF variant with zero false negative enough to r (i.e., with distance smaller than or equal to ϵ).
| rate theoretically. | Since               | most    | of those   | works   | are                | built on top | Formally |              |     |         |     |       |      |       |     |
| ------------------- | ------------------- | ------- | ---------- | ------- | ------------------ | ------------ | -------- | ------------ | --- | ------- | --- | ----- | ---- | ----- | --- |
| of LSH,             | their effectiveness |         | is usually | limited | by                 | unknowing    |          |              |     |         |     |       |      |       |     |
|                     |                     |         |            |         |                    |              | R▷◁      | S ={(r,s)|∀r |     | ∈R,∀s∈S |     | where | d(r, | s)≤ϵ} | (1) |
| of the data         | distribution.       |         |            |         |                    |              | ϵ        |              |     |         |     |       |      |       |     |
| Similarity          | join: This          | problem | can        | be      | further classified | into         |          |              |     |         |     |       |      |       |     |
Therearethreecritical“thresholds”inthispaper,aslistedin
two sub-types, exact and approximate similarity join, where Table I, the “distance threshold” ϵ, the “neighbor threshold” τ
the former is to exactly find all the truly close points while and the “Xling decision threshold” XDT. To avoid confusion,
| the latter | allows some   | errors.          |     |           |     |             | we further | explain  | them      | here: |           |        |       |        |     |
| ---------- | ------------- | ---------------- | --- | --------- | --- | ----------- | ---------- | -------- | --------- | ----- | --------- | ------ | ----- | ------ | --- |
| One        | family of the | state-of-the-art |     | efficient |     | methods for |            |          |           |       |           |        |       |        |     |
|            |               |                  |     |           |     |             | 1) The     | distance | threshold |       | ϵ is part | of the | range | search | and |
exact similarity join is the epsilon-grid-order (EGO) based similarity join operations, which indicates the search
methods,includingEGO-join[15],EGO-star-join[16],Super-
|           |             |      |       |           |      |              | range | as  | shown | in Definition |     | 1 and | 2.  |     |     |
| --------- | ----------- | ---- | ----- | --------- | ---- | ------------ | ----- | --- | ----- | ------------- | --- | ----- | --- | --- | --- |
| EGO [17], | FGF-Hilbert | join | [14], | etc. They | work | by splitting |       |     |       |               |     |       |     |     |     |
2) τ isathresholdforthegroundtruthneighbors.Ifaquery
thespaceintocellsandsortingthedatapointsalongwiththose trulyhasmorethanτ neighbors,wecallitagroundtruth
cells,whichwillthenhelpreduceunnecessarycomputationin
|                |       |     |     |     |     |     | positive, |       | otherwise | it        | is a groundtruth |       | negative. |           |     |
| -------------- | ----- | --- | --- | --- | --- | --- | --------- | ----- | --------- | --------- | ---------------- | ----- | --------- | --------- | --- |
| the similarity | join. |     |     |     |     |     |           |       |           |           |                  |       |           |           |     |
|                |       |     |     |     |     |     | 3) The    | Xling | decision  | threshold |                  | (XDT) | is the    | threshold | to  |
Approximate similarity join methods are usually based on classifythequerybasedonthepredictedneighbors.Ifa
LSH[18],[37],[19],[4],[5],[12],[13].Theproblemofthose
|     |     |     |     |     |     |     | query | is  | predicted | as having | more | than | XDT | neighbors, |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | --------- | --------- | ---- | ---- | --- | ---------- | --- |
methods is data unawareness, i.e., the hashing-based space we name it as a predicted positive, otherwise it is
| partitioning | usually | does | not consider |     | the data | distribution, |           |     |           |     |     |     |     |     |     |
| ------------ | ------- | ---- | ------------ | --- | -------- | ------------- | --------- | --- | --------- | --- | --- | --- | --- | --- | --- |
|              |         |      |              |     |          |               | predicted |     | negative. |     |     |     |     |     |     |
which may leads to imbalanced partitions that significantly Notethatwedonotdirectlyuseτ
tothresholdthepredictions.
| lower the | overall search | performance        |     | [20].       |     |     |                  |            |           |             |         |              |           |             |      |
| --------- | -------------- | ------------------ | --- | ----------- | --- | --- | ---------------- | ---------- | --------- | ----------- | ------- | ------------ | --------- | ----------- | ---- |
|           |                |                    |     |             |     |     | This is          | because    | different | cardinality |         | estimation   |           | models      | have |
|           |                |                    |     |             |     |     | different        | prediction |           | accuracy,   | leading | to           | different | predicted   |      |
|           |                | III. PRELIMINARIES |     |             |     |     |                  |            |           |             |         |              |           |             |      |
|           |                |                    |     |             |     |     | values for       | the        | same      | query.      | So it   | is necessary |           | to use      | an   |
|           |                |                    |     |             |     |     | adpative         | threshold  | driven    | by          | both    | model        | and data  | to classify |      |
|           |                |                    |     |             |     |     | the predictions, |            | which     | is XDT,     | such    | that         | we can    | control     | the  |
| Notation  |                |                    |     | Description |     |     |                  |            |           |             |         |              |           |             |      |
ϵ The distance threshold for range search and false positive or negative rate. More details are introduced in
|     | similarity |          | join       |     |               |          | Section | V-A. |     |     |     |     |     |     |     |
| --- | ---------- | -------- | ---------- | --- | ------------- | -------- | ------- | ---- | --- | --- | --- | --- | --- | --- | --- |
| τ   | The        | neighbor | threshold, |     | i.e., whether | or not a |         |      |     |     |     |     |     |     |     |
IV. ARCHITECTUREANDWORKFLOW
|     | query | has | more than | τ neighbors |     |     |     |     |     |     |     |     |     |     |     |
| --- | ----- | --- | --------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
XDT The Xling decision threshold to classify the A. The core and optimization strategies
|          | prediction |       | as positive | or    | negative |     |            |               |        |             |              |           |           |              |     |
| -------- | ---------- | ----- | ----------- | ----- | -------- | --- | ---------- | ------------- | ------ | ----------- | ------------ | --------- | --------- | ------------ | --- |
|          |            |       |             |       |          |     | Figure     | 1 illustrates |        | the overall | architecture |           | and       | workflow     | of  |
| N        | Dataset    | size  |             |       |          |     |            |               |        |             |              |           |           |              |     |
|          |            |       |             |       |          |     | Xling. The | core          | is the | learned     | cardinality  |           | estimator | and          | XDT |
| |R|, |S| | The        | sizes | of set R    | and S |          |     |            |               |        |             |              |           |           |              |     |
|          |            |       |             |       |          |     | (yellow    | boxes).       | The    | green       | boxes        | represent | the       | optimization |     |
MAE, MSE Mean absolute error and mean squared error strategies deployed in the training and predicting stages. The
|      |           |          |      |           |          |      | blue shapes | stand | for   | the      | training  | data, | including | the      | raw  |
| ---- | --------- | -------- | ---- | --------- | -------- | ---- | ----------- | ----- | ----- | -------- | --------- | ----- | --------- | -------- | ---- |
| FPR, | FNR False | positive | rate | and false | negative | rate |             |       |       |          |           |       |           |          |      |
|      |           |          |      |           |          |      | data (which | is    | input | from the | external) | and   | the       | prepared | data |
TABLEI:Listofnotationsusedinthisandfollowingsections

|     |     |                 |     |     | training | ϵ selection |     | strategy | is further | discussed |     | in Section |
| --- | --- | --------------- | --- | --- | -------- | ----------- | --- | -------- | ---------- | --------- | --- | ---------- |
|     | Raw | Query point + ε |     |     |          |             |     |          |            |           |     |            |
training data
V-A.
|     |     |     |     |     | B. Training | and | querying | workflows |     |     |     |     |
| --- | --- | --- | --- | --- | ----------- | --- | -------- | --------- | --- | --- | --- | --- |
Training ε selection
|     |     |     |     |     | There    | are two | workflows |          | in Xling, | the | offline   | training |
| --- | --- | --- | --- | --- | -------- | ------- | --------- | -------- | --------- | --- | --------- | -------- |
|     |     |     |     |     | workflow | and     | online    | querying | workflow. |     | In Figure | 1, the   |
Prepared Train Learned solid arrows illustrate the training workflow. As introduced
training data
cardinality estimator
|     |     |     |     |     | in Definition | 2        | and Section |            | I, the two | point | sets           | to be joined |
| --- | --- | --- | --- | --- | ------------- | -------- | ----------- | ---------- | ---------- | ----- | -------------- | ------------ |
|     |     |     |     |     | are denoted   | by       | R and       | S, and     | without    | loss  | of generality, | we           |
|     |     |     |     |     | assume        | that the | size        | of R (|R|) | is larger  | than  | size           | of S (|S|).  |
Adaptive XDT
|     |     |     | XDT |     | ThenRisusedasthetrainingset(i.e.,the“rawtrainingdata” |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
selection
|     |     |     |     |     | inFigure1)totrainXlingwhileS |     |     |     | actsasthequeries.Theraw |     |     |     |
| --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | ----------------------- | --- | --- | --- |
Predict
|     |       |                   |     |     | training      | data includes |              | all points | in       | R without    | ϵ information. |             |
| --- | ----- | ----------------- | --- | --- | ------------- | ------------- | ------------ | ---------- | -------- | ------------ | -------------- | ----------- |
|     |       |                   |     |     | 1) Training:  |               | The          | first step | in       | the training |                | workflow is |
|     | 𝜏 + ε | Positive/Negative |     |     |               |               |              |            |          |              |                |             |
|     |       |                   |     |     | concatenating |               | the selected |            | ϵ values | onto each    | training       | point       |
Fig. 1: Architecture and workflow of Xling r ∈ R (where i = 1,2,...,|R|), generating the “prepared
i
|     |     |     |     |     | training | data” | that is | a Cartesian | product |     | between | the point |
| --- | --- | --- | --- | --- | -------- | ----- | ------- | ----------- | ------- | --- | ------- | --------- |
(which is generated based on the raw data inside Xling). set R and ϵ set E, i.e., the prepared training data is the set
The workflow of Xling mainly relies on the prepared training {(r , ϵ ) | ∀(r ,ϵ )∈R×E}, where r is a multi-dimensional
|     |     |     |     |     | i j | i   | j   |     |     | i   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
data instead of the raw data. In addition, the pink boxes vector and ϵ j is a real number. Here the set E is generated by
indicate the query-time inputs, including the query point, ϵ the training ϵ selection strategy (Section V-A).
and τ, where the query point and ϵ are fed into the learned To make it clearer, suppose R is a toy raw training set of 2
cardinality estimator while the ϵ and τ are used to compute pointsr andr ,andE includestwoselectedvaluesϵ andϵ .
|     |     |     |     |     |     | a   | b   |     |     |     |     | 1 2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
XDT. The grey box stands for the output, i.e., whether the Thenthepreparedtrainingsetlookslike{(r ,ϵ ),(r ,ϵ ),(r ,
|     |     |     |     |     |     |     |     |     |     |     | a 1 | a 2 b |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- |
query point is positive (with enough neighbors) or negative ϵ 1 ),(r b ,ϵ 2 )}associatedwiththeirtargets(i.e.,thegroundtruth
(having insufficient neighbors). For the workflow, the solid numbers of neighbors). Then the learned cardinality estimator
arrows present the offline training workflow, while the hollow is trained with the prepared training data.
arrows indicate the online workflow for querying and XDT 2) Querying: The querying workflow is presented with
computing. hollow arrows in Figure 1. First, ϵ and τ are input to compute
The overall architecture includes (1) the core learned car- the XDT using the adaptive XDT selection strategy based on
dinility estimator and XDT and (2) the surrounding optimiza- the prepared training data. Second, the query point and the ϵ
tion strategy modules. [28] uses a classifier and a decision areconcatenatedandfedtothecardinalityestimatortopredict
threshold to build a learned Bloom filter, while we use a the number of neighbors. Finally, the prediction is compared
regressor and the XDT to construct Xling, which is similar to withXDTandtheanswer(positiveornegative)isdetermined.
| the learned | accelerator  | framework (LAF) | in        | [38]. Specifically, |        |               |     |      |     |     |     |     |
| ----------- | ------------ | --------------- | --------- | ------------------- | ------ | ------------- | --- | ---- | --- | --- | --- | --- |
|             |              |                 |           |                     | C. Use | in similarity |     | join |     |     |     |     |
| LAF proves  | that learned | cardinality     | estimator | with a proper       |        |               |     |      |     |     |     |     |
decision threshold can significantly accelerate range-search Use of Xling to speed up similarity join is straightforward:
based high-dimensional clustering. As similarity join is also givenϵ,τ,RandS,supposing|R|>|S|,Xlingisfirsttrained
based on range search, such a solution works for it too. And onR,thenforeachquerypoints∈S,Xlingpredictswhether
unlike the case of learned Bloom filter, since filtering-by- s has enough neighbors in R under the ϵ. If yes, the range
counting requires estimating the specific number (mentioned search (either a brute-force search or an indexed search like
inSectionI),regressoristhebestchoiceratherthanclassifier. using LSH) will be executed in R for query s, otherwise s
But in LAF, the decision threshold has to be determined by is predicted as negative and the search for it will be skipped.
grid search. To overcome this shortcoming, we design an In this way, unnecessary range search is reduced and the join
adaptive XDT selection strategy based on the training data efficiency is improved.
such that XDT can be efficiently computed. More details are As a generic filter, Xling can be applied onto any nested-
introduced in Section V-B. loop based similarity join algorithms to speed them up. When
To reduce the false results, in addition to adaptively select- usingdeepregressorasthecorecardinalityestimatorinXling,
ing a proper XDT, we also propose an adaptive training ϵ its prediction time complexity for each query is constant
selection strategy to sample the most representative ϵ values (O(1)) with the data scale, which in practice can be further
for training the cardinality estimator effectively and thereby accelerated by GPU. And the training time is not an issue
reducing the prediction error. The existing learned cardinality due to the generalization capability of the deep models, i.e., a
estimation studies (e.g., [39]) usually select the training ϵ val- trainedestimatorcanbeusedonanyotherdatasetwithsimilar
uesuniformly,whichisnotoptimal,andweshowinthispaper distribution,whichisprovedbyourevaluationinSectionVI-F.
that our proposed strategy generates a more representative WeimplementXJoinbyapplyingXlingontoanaivenested-
training set and leads to a more effective model training. This loop similarity join method which does a brute-force range

search for each query. Our evaluation presents that XJoin machine. Therefore only the s sampled conditions are used to
outperforms the state-of-the-art similarity join baselines. We form the training tuples.
alsoapplyXlingtosomeapproximatesimilarityjoinmethods, Uniformly sampling training conditions cannot reflect the
which shows Xling successfully improves their speed-quality unevenly data distribution in real-world datasets. Therefore,
trade-off capability. we design a generic adaptive strategy to further fine-tune the
initial uniformly sampling conditions for CR problem based
V. OPTIMIZATIONSTRATEGIES on the density of the targets, such that the resulting training
tuples are more representative for the data distribution of
In this section we introduce the details for the optimization
the whole dataset. Our adaptive training condition selection
strategies we propose in Xling.
(ATCS) strategy (Algorithm 1) follows the steps below for
each data point p in the training set:
A. Training ϵ selection
1) Given the uniformly sampled candidate conditions C
[39]uniformlysamplesthetrainingϵfromrange[0,θ ], p
max and the corresponding targets T for point p (i.e., when
whereθ isauser-determinedupperlimitforthedistances. p
max condition c ∈ C is applied to point p, the target is
However, such a selection strategy is not optimal. We show i p
correspondingly t ∈ T ), the minimum and maximum
in this section that the cardinality estimation models can be i p
targetsarefound(t andt ,line5)andtheinterval
trained more effectively by using our data-aware threshold min max
[t ,t ] is then partitioned into s bins evenly (line
selectionstrategy.Furthermore,ourstrategycanbegeneralized min max
6).
to better solve a family of regression problems.
2) Then each candidate condition is mapped into one bin
The specific family of regression problems is named
based on its paired target (line 7-8).
Condition-based Regression (shortly denoted by CR) and
3) Finally the specific number of condition-target pairs are
defined as follows:
sampled from each bin (line 10-11) according to the
Definition 3 (Condition-based Regression problem): Given
fraction of the bin size (|B |) over total number of the
a dataset D, a condition c associated with each data point i
conditions (|C |), where bin size is the number of pairs
p ∈ D, and a target t corresponding to each (p,c) pairs, the p
in that specific bin.
CR problem is to learn the relationship between the presented
4) Since some bins may generate zero samples (i.e., when
(p,c) and t, then predict the corresponding t for any given
s|B | < |C |), the final sampled condition-target pairs
(p,c). i p
may be not enough given the required s. In such a case,
In the context of learned cardinality estimation, the condi-
the rest1 of the pairs will be randomly chosen from the
tion is the ϵ while the target is the number of neighbors.
unselected ones that are not yet included in the samples
InmostCondition-basedRegressionproblems,thecondition
above (line 12-13).
is usually a continuous variable (like distance) whose values
The final training set for the whole D is the collection of
cannot be fully enumerated, therefore it is worth studying
the training tuples (p, c, t) generated by the strategy for each
howtosampletheconditionsforbettertrainingtheregression
p∈D, i.e., the final training set includes s|D| tuples.
model in order to lower prediction error, which is formally
Unlikeuniformlysampling,ATCSisdata-awarebybinning
defined as such:
the condition-target pairs to estimate the density of the targets
Definition 4 (Training condition selection for CR): Given
and then sampling the final conditions based on the density,
a dataset D of size n, a set of m candidate values
which generates more representative training conditions and
{c ,c ,...,c } of the condition c for each data point
i1 i2 im i
targets. For example, let m = 100,s = 5, i.e., the interval of
p ∈ D,1 ≤ i ≤ n, the corresponding target t for each
i ij
targets [t , t ] is split into 5 bins evenly and their corre-
(p ,c ),1 ≤ j ≤ m, and a sampling number s, the training min max
i ij
spondingconditionvaluesareplacedintothebinsaccordingly.
conditionselectiontaskistoselectspairsfromthem(c ,t )
ij ij
Supposing the numbers of conditions from B to B are 59,
pairs to form s training tuples for each point p , which results 1 5
i
1, 19, 1, 20, the uniformly sampling will select 2, 1, 0, 1, 1
intotallysntrainingtuplesforthewholedatasetD,suchthat
conditions from them (i.e., selecting one per 20), while ATCS
the mean regression error is minimized.
will first select 2, 0, 0, 0, 1 from them (Algorithm 1 Line
Note that our discussion starts from a discrete candidate
11) then probably select the rest 2 conditions from B , B
set, instead of directly beginning from the continuous range 1 3
and B which are the most dense areas (Algorithm 1 Line
(like [0, θ ]). This is just to unify the discussion between 5
max
13). In this example, the uniformly sampling gets 2 out of
continuous-range uniform sampling and our sampling method
the 5 sampled conditions from very sparse areas (B and B )
which requires preprocessing to discretize the range, which 2 4
in the distribution of targets, which cannot well reflect the
willnotlosegenerality.misusuallylarge(suchthatthevalues
overall distribution, while ATCS probably selects all the 5
are dense enough) to approximate the case of the continuous
from dense areas and results in more representative training
condition values, so we do not use all the m candidate values
togeneratemntrainingtuples,asthememoryspaceislimited.
1Inourevaluation,therestofthepairs(whicharerandomlychosen)usually
For example, in our evaluation, m = 100, in which case mn
occupy10%∼20%inthefinaltrainingsetforthewholeD,i.e.,0.1s|D|∼
tuples require more memory space than that of our evaluation 0.2s|D|

Algorithm 1 Adaptive training condition selection (ATCS) which is straightforward to understand: a larger τ causes
strategy trainingsampleswithmoreneighborstobenegative,therefore
Input: DatasetD,mapfromeachdatapointtoitsuniformlysampled cardinalities of the negative samples increase overall, making
candidate condition list C, map from each point to its target list the computed XDT increased.
T, sampling number s
Output: set of resulting training tuples R But both methods have a problem: we have to first identify
1: R := ∅ the groundtruth negative samples in the training set, which
2: for each point p in D do
3: C p := C(p) ▷ the condition list for p is costly in the high-dimensional cases. Since the negative
4: T p := T(p) ▷ the target list for p, one-to-one corresponding samples depend on ϵ, and the training set only include a
to C
p tiny portion of all possible ϵ, the queried ϵ will probably
5: t min , t max := min(T p ), max(T p )
6: Split interval [t min , t max ] into s bins evenly not exist in training set (named “out-of-domain ϵ”), in which
7: for each c in C p and corresponding t in T p do case intensive range search has to be executed to compute the
8: Place (c,t) into a bin bounded by [t a ,t b ) such that t ∈
[t ,t ) negative samples from scratch.
a b
9: S := ∅ ▷ the selected (c,t) collection for p Therefore, it is non-trivial to study how to easily get the
10: for each bin B i(cid:106) do (cid:107) training targets (i.e., groundtruth cardinalities) under the out-
11: S := S ∪{ s|Bi| randomly sampled (c,t) pairs from
|Cp| of-domainϵsuchthatthegroundtruthnegativesamplescanbe
B }
i identified without doing range search for each training point.
12: if |S|<s then
Weproposeaninterpolation-basedstrategytogeneratetheap-
13: Fill with random samples from unselected (c,t) until
|S|=s proximate targets. Specifically, given a point, its ϵ-cardinality
14: R := R∪{(p,c s ,t s )|(c s ,t s )∈S} ▷ combine all pairs in curve is monotonically non-decreasing, i.e., with ϵ increasing,
S with p
the cardinality will never decrease. So we can approximate
15: return R
the curve segment between two neighboring training ϵ values
(denoted by ϵ and ϵ ) as linear, and use linear-interpolation
1 2
to estimate the groundtruth cardinality for any training point
samples, by which the model can be trained more effectively.
under a out-of-domain ϵ between ϵ and ϵ , as shown in
OurevaluationinSectionVI-BshowsthatATCShelpsreduce 3 1 2
Equation 2.
50% ∼ 98% of the prediction error (MAE and MSE).
B. Xling decision threshold (XDT) selection t −t
t =t + 2 1(ϵ −ϵ ) (2)
Xling decision threshold (XDT) determines whether the 3 1 ϵ 2 −ϵ 1 3 1
prediction means positive. Its value is influenced by τ, the where t is the target of the current training point under ϵ
i i
way it is computed, and the way to identify the groundtruth (i = 1,2), t is the approximate target under out-of-domain
3
negative training samples, which will be introduced in this ϵ , and ϵ <ϵ . The approximate targets are then used to find
3 1 2
section. Note that XDT is determined purely based on the all groundtruth negative training samples under ϵ based on
3
training set offline, regardless of the online queries, i.e., the which XDT is computed.
computation of XDT does not raise overhead on the online Our evaluation shows that in most cases, Xling deploying
querying. the interpolation-based method has a competitive prediction
Basically, XDT is computed using the groundtruth negative qualitytothatusingthenaivesolution.Furthermore,thereare
training samples (i.e., the training points with no more than two advantages of the proposed method over the naive way:
τ neighbors). We propose two ways to compute XDT: false (1) it is significantly faster since no range search is executed,
positive rate (FPR) based and mean based. and(2)asinSectionVI-B2,interpolation-basedmethodtends
1) FPR-based XDT selection: similarly to [36], [40], [30], to result in no higher false negative rate (FNR) than the naive
givenaFPRtolerancevaluet (e.g.,5%),thismethod method, which is better for the effectiveness (e.g., the recall)
fpr
letstheestimatormakepredictionsforthetrainingpoints of Xling.
and sets XDT such that the resulting filter FPR on
training set is lower than t . VI. EXPERIMENTS
fpr
2) mean-basedXDTselection:thismethodsetsXDTtobe
A. Experiment settings
themeanpredictedvalueforallthegroundtruthnegative
training samples. Environment: All the experiments are executed on a Lambda
Quad workstation with 28 3.30GHz Intel Core i9-9940X
In our evaluation (Section VI-B2), FPR-based method usually
CPUs, 4 RTX 2080 Ti GPUs and 128 GB RAM.
results in a higher XDT, leading to more speedup and lower
Datasets: Table II provides an overview for our evaluation
quality in end-to-end similarity join, so we design the mean-
datasets,reportingtheirsizes,datadimensionsanddatatypes.
based method to provide the second option which results in a
We introduce more details here:
lowerXDTandleadstohigherqualityandlessspeedup.They
areusefulindifferentsituationsasshowninourevaluation.In 1) FastText: 1M word embeddings (300-dimensional) gen-
addition, no matter using FPR-based or mean-based selection, eratedbyfastTextmodelpre-trainedonWikipedia2017,
there is a trend that a larger τ will result in a higher XDT, UMBC webbase corpus and statmt.org news dataset.

Dataset #Points #Sampled Dim Type major baselines.
FastText 1M 150k 300 Text
1) Naive:Thisisabrute-forcebasednested-loopsimilarity
Glove 1.2M 150k 200 Text
Word2vec 3M 150k 300 Text join, i.e., for each query point in S, do a brute-force
Gist 1M 150k 960 Image rangesearchforitinR.Itsresultsactasthegroundtruth
Sift 1M 150k 128 Image
NUS-WIDE 270k 150k 500 Image for measuring the result quality of all other methods.
2) SuperEGO2 [17]: This is an exact method based on
TABLEII:Evaluationdatasetinformation,includingthenum-
Epsilon Grid Ordering (EGO) that sorts the data by a
ber of total points in the whole dataset (#Points), the number
specific order to facilitate the join.
of sampled points for evaluation (#Sampled), data dimension
3) LSH: This is an approximate method using LSH. First
(Dim), and the raw data type (Type). the points in R are mapped into buckets by LSH, then
eachqueryismappedtosomebucketsbythesameLSH.
Thepointsinthosebucketsandnearbybucketswillthen
2) Glove:1.2Mwordvectors(200-dimensional)pre-trained
be retrieved as candidates and verified. This method is
on tweets.
implemented using FALCONN [42], the state-of-the-art
3) Word2vec:3Mwordembeddings(300-dimensional)pre-
LSH library.
trained on Google News dataset.
4) KmeansTree: This is an approximate method using K-
4) Gist: 1M GIST image descriptors (960-dimensional).
means tree, where the tree is built on R and the space
5) Sift: 1M SIFT image descriptors (128-dimensional).
is partitioned and represented by sub-trees. Then each
6) NUS-WIDE: 270k bag-of-visual-words vectors (500-
query is passed into the tree and a specific sub-tree
dimensional) learned on a web image dataset created
(whichrepresentsasub-spaceofR)willbeinspectedto
by NUS’s Lab for Media Search.
find neighbors within the range. We use FLANN [43],
Due to computing resource limitation, we randomly sample
a widely used high-performance library for tree-based
150k vectors from each of them for the evaluation. In the
search, to implement this method.
rest of this paper, any mentioned dataset name is by default
5) Naive-LSBF:Thisisanapproximatefilter-basedmethod
meaning the 150k subset of the corresponding dataset.
that simply applies LSBF 3 onto the Naive method, in
We then normalize the sampled vectors to unit length
the same way as the use of Xling in similarity join
because(1)thismakesthedistancesbounded,i.e.,bothcosine
(Section IV-C). We use LSBF instead of the following
and Euclidean distance are within [0, 2] on unit vectors,
MSBFvariantsbecausethosevariantsraiseunnecessary
makingiteasiertodetermineϵ,and(2)somebaselinemethods
overhead to support specific extra features.
do not support cosine distance, in which case we have to
6) IVFPQ: we also select an approximate nearest neigh-
convert the cosine ϵ into equivalent Euclidean ϵ for them on
bor (ANN) index as part of the baselines, which is
unit vectors, as in our previous work [38]. We then split each
the IVFPQ index [44] in FAISS [45], one of the in-
dataset into training and testing sets by a ratio of 8:2, where
dustrial ANN search libraries. Since IVFPQ does not
the training set acts as R while the testing set is S. Xling is
support range search natively, we evaluate it by first
trained on the training set, then all the methods are evaluated
searching for a larger number of nearest candidates,
using the corresponding testing set as queries.
then verifying which candidates are the true neighbors
Learning models:weuseseverallearningmodelstoevaluate
given ϵ. And as IVFPQ tends to achieve a high search
the performance of the optimization strategies in Xling. They
speed with relatively lower quality (as discussed in our
are introduced as follows. For the deep models, we use
previous work [46]), this baseline does not make much
the recommended configurations in prior works, while for
senseinthefixed-parameterend-to-endevaluation(Sec-
non-deep models a grid search is executed to find the best
tion VI-D). Therefore, we only evaluate it in the trade-
parameters. Specifically, (1) RMI [28]: We use the same
off (Section VI-E) and generalization (Section VI-F)
configuration in [38], i.e., three stages, respectively including
experiments.
1, 2, 4 fully-connected neural networks. Each neural network
Our proposed methods: Following the way described in
has 4 hidden layers with width 512, 512, 256, and 128. The
Section IV-C, we apply Xling to several base similarity
RMI is trained for 200 epochs with batch size 512. (2) NN:
join methods mentioned above. The resulting methods are
We also evaluate the neural network (NN), which is simply
named as: (1) XJoin (2) LSH-Xling (3) KmeansTree-Xling
a single sub-model extracted from the RMI above. So all the
(4) IVFPQ-Xling. The XJoin is our major proposed method
parameters (including the training configuration) are same as
that is evaluated in all the similarity join experiments, while
that in RMI. (3) SelNet [41]: We use the the same model
the other proposed methods here are only compared with
configuration as in the paper. (4) XGBoost Regressor (XGB),
the corresponding baseline methods to show the enhancement
LightGBM Regressor (LGBM) and Support Vector Regressor
brought by Xling to them. The learned cardinality estimator
(SVR):Theseareallnon-deepregressors,wedoagridsearch
used by Xling in all these methods is an RMI. Note that
to determine their best parameters.
Similarity join baselines: The evaluation baselines include 2codeavailableathttps://www.ics.uci.edu/∼dvk/code/SuperEGO.html
both exact and approximate methods, where the latter are the 3codeavailableathttps://github.com/csunyy/LSBF

the goal of this paper is to reveal the potential of such a Portion Portion Portion
|               |             |     |            |      |              |     |     | Dataset  |     | (ϵ=0.4) |        | (ϵ=0.45) |     | (ϵ=0.5) |     |
| ------------- | ----------- | --- | ---------- | ---- | ------------ | --- | --- | -------- | --- | ------- | ------ | -------- | --- | ------- | --- |
| new framework | on speeding | up  | similarity | join | generically, | so  |     |          |     |         |        |          |     |         |     |
|               |             |     |            |      |              |     |     | FastText |     |         | 0.1103 | 0.0443   |     | 0.0116  |     |
selectingthebestestimationmodelisoutofscope.Giventhat
RMIhasbeenusedasastrongbaselineforlearnedcardinality Glove 0.8668 0.7851 0.6637
estimation in [39] and it is not the most state-of-the-art, it is Word2vec 0.2875 0.1675 0.0803
a fair choice for Xling in the evaluation, especially when we Gist 0.8442 0.3939 0.1027
can show that RMI is already good enough to outperform the Sift 0.5578 0.3494 0.1531
| other baselines. | We will             | evaluate         | Xling | with         | other      | estimators |           |          |            |         |             |         |         |          |          |
| ---------------- | ------------------- | ---------------- | ----- | ------------ | ---------- | ---------- | --------- | -------- | ---------- | ------- | ----------- | ------- | ------- | -------- | -------- |
|                  |                     |                  |       |              |            |            |           | NUS-WIDE |            |         | 0.9743      | 0.9653  |         | 0.9544   |          |
| in the future    | work.               |                  |       |              |            |            |           |          |            |         |             |         |         |          |          |
|                  |                     |                  |       |              |            |            | TABLE     | III:     | The        | portion | of negative | queries |         | for each | dataset  |
| In XJoin,        | the XDT             | is computed      |       | by FPR-based |            | selection  |           |          |            |         |             |         |         |          |          |
| (introduced      | in Section          | V-B)             | with  | 5% FPR       | tolerance, | and        | under     | each     | ϵ          |         |             |         |         |          |          |
|                  |                     |                  |       |              |            |            | Following |          | Definition |         | 4, to       | make it | simple, | we       | have the |
| τ =50,           | while in LSH-Xling, | KmeansTree-Xling |       |              | and        | IVFPQ-     |           |          |            |         |             |         |         |          |          |
Xling,XDTiscomputedbymean-basedselectionwithτ =0. set of candidate condition values shared by all the training
As discussed in Section V-B, “mean-based XDT selection + points, i.e., the set {c ,c ,...,c } is same for any training
|         |                    |         |     |                  |     |        |       |     |        | i1  | i2    | im            |     |      |          |
| ------- | ------------------ | ------- | --- | ---------------- | --- | ------ | ----- | --- | ------ | --- | ----- | ------------- | --- | ---- | -------- |
|         |                    |         |     |                  |     |        | point | p . | We let | m   | = 100 | and construct |     | such | a set by |
| smaller | τ” leads to higher | quality |     | while “FPR-based |     | selec- |       | i   |        |     |       |               |     |      |          |
tion + larger τ” results in more acceleration. Since LSH, evenly sampling 100 values from a range[c ,c ], where
min max
|     |     |     |     |     |     |     | we  | set c | =   | 0.4,c | =   | 0.9 for | cosine | distance | while |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | ----- | --- | ------- | ------ | -------- | ----- |
KmeansTree and IVFPQ are approximate methods that sac- min max
rifice quality for efficiency, mean-based XDT with lowest τ c min = 0.5,c max = 2.0 for Euclidean distance. These c min
can accelerate them while minimizing the further quality loss. and c values are selected based on a grid search given
max
|            |                |        |             |     |       |            | the | evaluation | experience |     | from | our previous |     | work [38]. | Then |
| ---------- | -------------- | ------ | ----------- | --- | ----- | ---------- | --- | ---------- | ---------- | --- | ---- | ------------ | --- | ---------- | ---- |
| For Naive, | the bottleneck | is the | efficiency, |     | so we | choose the |     |            |            |     |      |              |     |            |      |
other configuration for Xling in order to achieve a non-trivial we set the sampling number s = 6, i.e., for each training
|     |     |     |     |     |     |     | point, | 6 distinct |     | condition | values | will | be sampled |     | from the |
| --- | --- | --- | --- | --- | --- | --- | ------ | ---------- | --- | --------- | ------ | ---- | ---------- | --- | -------- |
speedup.
Metrics: The distance metric for text data is cosine distance 100 candidate values and become the final training ϵ values
|            |           |         |           |     |           |         | to be    | paired | with       | the point | in       | the prepared | training |           | data. Two |
| ---------- | --------- | ------- | --------- | --- | --------- | ------- | -------- | ------ | ---------- | --------- | -------- | ------------ | -------- | --------- | --------- |
| while that | for image | data is | Euclidean |     | distance. | For the |          |        |            |           |          |              |          |           |           |
|            |           |         |           |     |           |         | sampling |        | strategies | are       | deployed | to select    | the      | 6 values: | (1)       |
baselineswhichdonotsupportcosinedistance,wefollow[38]
to equivalently convert cosine distance to Euclidean distance. uniform sampling, e.g., selecting the 1st, 20th, 40th, 60th,
|                |         |         |     |            |      |          | 80th | and | 100th | values | (2) our | ATCS | strategy | (Algorithm1). |     |
| -------------- | ------- | ------- | --- | ---------- | ---- | -------- | ---- | --- | ----- | ------ | ------- | ---- | -------- | ------------- | --- |
| The evaluation | metrics | include | (1) | end-to-end | join | time for |      |     |       |        |         |      |          |               |     |
measuring the efficiency of similarity join methods, (2) recall The former is presented as “fixed” while the latter is marked
|             |                   |          |           |         |                |         | as  | “auto”     | in the | Strategy | columns | of Table     | IV. |        |           |
| ----------- | ----------------- | -------- | --------- | ------- | -------------- | ------- | --- | ---------- | ------ | -------- | ------- | ------------ | --- | ------ | --------- |
| (i.e., the  | ratio of the      | returned | positive  | results | over           | all the |     |            |        |          |         |              |     |        |           |
|             |                   |          |           |         |                |         | The | regression |        | models   | (i.e.,  | the learning |     | models | listed in |
| groundtruth | positive results) | for      | measuring |         | the similarity | join    |     |            |        |          |         |              |     |        |           |
result quality, (3) mean absolute error (MAE) and mean Section VI-A) will first be trained respectively using the two
|         |                 |           |     |            |         |        | prepared |     | training | sets | from different | strategies, |     | then | they will |
| ------- | --------------- | --------- | --- | ---------- | ------- | ------ | -------- | --- | -------- | ---- | -------------- | ----------- | --- | ---- | --------- |
| squared | error (MSE) for | measuring |     | prediction | quality | of the |          |     |          |      |                |             |     |      |           |
learned cardinality estimator, and (4) false positive rate (FPR) do inference on some prepared testing sets and the inference
andfalsenegativerate(FNR)formeasuringpredictionquality quality is measured by MAE and MSE, which can reflect
|     |     |     |     |     |     |     | the | training | effectiveness. |     | For | a fair testing, |     | we generate | two |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | -------------- | --- | --- | --------------- | --- | ----------- | --- |
of Xling.
Evaluation ϵ: As we have normalized all the vectors, the kinds of prepared testing sets: (1) the testing points with
randomlyselectedϵvaluesfromthe100candidatesmentioned
distancesbetweenthemarebounded,i.e.,[0,2]forbothcosine
and Euclidean distances. Since many use cases of similarity above,and(2)thesametestingpointswithuniformlyselected
|              |                  |     |            |            |           |            | ϵ values |     | from the    | candidates. |               | The inference |     | quality   | on the |
| ------------ | ---------------- | --- | ---------- | ---------- | --------- | ---------- | -------- | --- | ----------- | ----------- | ------------- | ------------- | --- | --------- | ------ |
| join usually | choose ϵ from    | the | range      | [0.2, 0.5] | [9],      | [10], [3], |          |     |             |             |               |               |     |           |        |
|              |                  |     |            |            |           |            | former   | set | is reported |             | in the Random | Testing       |     | ϵ columns | while  |
| [47], we     | do a grid search | in  | this range | and        | determine | the        |          |     |             |             |               |               |     |           |        |
representative evaluation ϵ values: 0.4, 0.45 and 0.5, based that on the latter is reported in the Uniform Testing ϵ columns
|                |                   |         |        |           |         |            | of             | Table IV. | And    | for each   | learning | model, | the   | Strategy | which     |
| -------------- | ----------------- | ------- | ------ | --------- | ------- | ---------- | -------------- | --------- | ------ | ---------- | -------- | ------ | ----- | -------- | --------- |
| on the portion | of negative       | queries | (i.e., | the       | queries | having no  |                |           |        |            |          |        |       |          |           |
|                |                   |         |        |           |         |            | results        | in        | better | inference  | quality  | (i.e., | lower | MAE and  | MSE)      |
| neighbor       | in R) in S. We    | set the | upper  | limit     | for the | portion as |                |           |        |            |          |        |       |          |           |
|                |                   |         |        |           |         |            | is highlighted |           | by     | bold       | text.    |        |       |          |           |
| 90% as         | too many negative | queries |        | will make | the     | evaluation |                |           |        |            |          |        |       |          |           |
|                |                   |         |        |           |         |            | In             | most      | cases, | the “auto” | strategy | (i.e., | our   | ATCS     | strategy) |
unconvincing.Undertheselectedϵvalues,mostofthedatasets
(except NUS-WIDE) have a proper portion that is no more achieves a better inference quality (e.g., reducing up to 98%
|           |                   |     |         |             |     |             | of  | the MSE | on  | NUS-WIDE |     | dataset) than | uniform | training | ϵ,  |
| --------- | ----------------- | --- | ------- | ----------- | --- | ----------- | --- | ------- | --- | -------- | --- | ------------- | ------- | -------- | --- |
| than 90%. | Table III reports | the | portion | of negative |     | queries for |     |         |     |          |     |               |         |          |     |
each dataset under each ϵ. meaning that ATCS strategy is generic to facilitate various
|                 |          |            |     |     |     |     | kinds       | of      | regression  | models |             | and highly | effective   | to         | raise a  |
| --------------- | -------- | ---------- | --- | --- | --- | --- | ----------- | ------- | ----------- | ------ | ----------- | ---------- | ----------- | ---------- | -------- |
|                 |          |            |     |     |     |     | significant |         | improvement |        | on the      | prediction | quality.    | Therefore, |          |
| B. Optimization | strategy | evaluation |     |     |     |     |             |         |             |        |             |            |             |            |          |
|                 |          |            |     |     |     |     | for         | all the | following   |        | experiments | in         | this paper, | the        | training |
In this section we report and analyze the evaluation results sets are prepared by ATCS.
| of the optimization | strategies. |     |     |     |     |     |     |     |            |     |              |     |            |      |     |
| ------------------- | ----------- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ------------ | --- | ---------- | ---- | --- |
|                     |             |     |     |     |     |     | 2)  | XDT | selection: |     | As mentioned |     | in Section | V-B, | XDT |
1) Training ϵ selection: The results of the training ϵ selec- is influenced by three factors: (1) τ, (2) the XDT selection
tion strategy is reported in Table IV. Due to the space limit, method (mean-based or FPR-based), and (3) the way to
we only present the results for 4 out of 6 datasets. get training targets for out-of-domain ϵ (interpolation-based

MAE RandomTes M tin S g E ϵ MAE UniformTes M tin S g E ϵ Model Strategy MAE RandomTes M tin S g E ϵ MAE UniformTes M tin S g E ϵ Model Strategy
4.04 6.69 2.57 2.68 XGB fixed 5.32 22.84 7.81 48.16 XGB fixed
2.54 1.32 2.54 1.26 XGB auto 5.02 24.09 7.89 50.7 XGB auto
3.66 6.65 2.14 2.57 LGBM fixed 5.29 20.46 7.45 43.82 LGBM fixed
1.8 0.83 1.79 0.81 LGBM auto 4.49 19.61 7.1 43.52 LGBM auto
23.79 97.16 27.55 127.15 SVR fixed 9.01 46.41 12.6 84.58 SVR fixed
22.26 81.06 25.34 106.22 SVR auto 8.7 50.18 12.32 90.46 SVR auto
96.13 24711.7 96.44 28299.85 SelNet fixed 8.91 54.69 12.57 97.23 SelNet fixed
93.8 22228.79 94.39 25737.67 SelNet auto 8.91 54.7 12.57 97.24 SelNet auto
2.08 1.39 1.69 1.00 NN fixed 4.38 18.87 6.78 41.95 NN fixed
0.39 0.03 0.44 0.05 NN auto 3.33 11.85 5.09 23.19 NN auto
2.55 5.72 1.52 2.18 RMI fixed 4.52 19.44 6.85 42.57 RMI fixed
0.20 0.01 0.19 0.01 RMI auto 3.43 13.84 5.35 27.51 RMI auto
(a) Sift (b) Word2Vec
MAE RandomTes M tin S g E ϵ MAE UniformTes M tin S g E ϵ Model Strategy MAE RandomTes M tin S g E ϵ MAE UniformTes M tin S g E ϵ Model Strategy
4.69 5.49 5.02 5.36 XGB fixed 4.74 14.99 3.4 6.35 XGB fixed
2.53 1.43 2.55 1.49 XGB auto 3.36 2.62 3.37 2.69 XGB auto
4.7 5.49 4.76 4.94 LGBM fixed 4.23 15.29 2.89 6.4 LGBM fixed
2.45 1.28 2.47 1.33 LGBM auto 2.4 2.6 2.36 2.46 LGBM auto
27.61 141.55 29.89 169.73 SVR fixed 22.81 70.71 24.6 80.33 SVR fixed
23.45 81.06 24.5 94.06 SVR auto 25.22 99.4 25.06 97.04 SVR auto
36.19 357.57 38.14 387.45 SelNet fixed 82.26 8655.88 82.62 9886.03 SelNet fixed
36.19 357.52 38.14 387.39 SelNet auto 75.96 6560.3 75.93 7490.16 SelNet auto
0.54 0.14 0.79 0.36 NN fixed 3.39 10.56 2.51 5.01 NN fixed
0.32 0.03 0.38 0.05 NN auto 0.83 0.20 1.04 0.33 NN auto
2.09 2.23 2.80 4.49 RMI fixed 4.24 19.66 2.49 6.60 RMI fixed
0.67 0.18 0.77 0.24 RMI auto 0.48 0.27 0.39 0.13 RMI auto
(c) FastText (d) NUS-WIDE
TABLE IV: Effectiveness of the two training ϵ selection strategies for different regressors trained on different datasets, where
MAE columnsshowtheoriginalnumbersmultipliedby10−3 andMSE columnsshowtheoriginalnumbersmultipliedby10−7
Dataset Model ϵ XDTSelection FPR A F p N p R roximate Ti T m ar e g (s e ) ts XDT FPR FNR ExactTa T rg im et e s (s) XDT
0.4 m FP ea R n 0 0 . . 4 0 9 5 4 6 8 2 0 0 . . 3 8 9 5 8 7 2 8 1 1 . . 3 3 6 8 1 5 8 9 4 - 0 8 6 .4 .8 5 3 0 0 . . 4 0 9 5 4 6 8 2 0 0 . . 3 8 9 5 8 7 2 8 1 1 0 0 3 3 7 7 . . 9 9 2 2 0 7 2 8 4 - 0 8 6 .4 .8 5 3
XGB 0.45 m FP ea R n 0 0 . . 5 0 0 6 1 0 9 8 0 0 . . 4 8 2 7 4 3 7 7 2 2 . . 5 5 8 4 3 9 6 9 3 -1 9 0 2 . . 6 4 6 3 0 0 . . 4 0 9 5 9 4 6 8 0 0 . . 4 8 2 8 5 2 9 1 1 0 0 3 3 8 8 . . 6 6 5 1 5 6 4 1 4 - 0 9 5 .2 .7 8 0
Glove 0.5 m FP ea R n 0 0 . . 4 0 9 6 8 0 9 2 0 0 . . 4 8 3 9 7 0 3 3 2 2 .8 .5 5 1 15 3 -1 8 2 7 . . 5 5 6 1 0 0 . . 5 0 0 5 0 6 4 6 0 0 . . 4 8 3 9 5 4 8 6 1 1 0 0 3 3 8 8 .3 .3 4 7 8 9 9 3 -1 9 3 6 . . 5 4 0 7
0.4 m FP ea R n 0 0 . . 4 0 0 5 7 0 1 1 0 0 . . 2 5 5 0 0 4 6 9 1 9 0 . . 9 0 1 6 1 7 2 9 4 6 . . 3 4 8 6 0 0 . . 4 0 0 5 7 0 1 1 0 0 . . 2 5 5 0 0 4 6 9 1 1 0 0 4 4 6 6 . . 1 1 8 8 8 9 5 2 4 6 . . 3 4 8 6
RMI 0.45 m FP ea R n 0 0 . . 4 0 4 8 9 0 6 8 0 0 . . 2 4 3 9 0 0 8 2 1 1 0 1 . . 9 1 2 2 8 6 6 9 4 6 . . 5 4 7 8 0 0 . . 3 0 5 5 3 0 7 6 0 0 . . 2 5 7 3 0 8 2 5 1 1 0 0 4 4 6 7 . . 9 0 5 0 2 9 5 8 4 7 . . 7 3 6 7
0.5 m FP ea R n 0 0 . . 3 0 6 7 1 0 3 9 0 0 . . 2 5 5 0 4 4 6 1 1 1 0 1 . . 8 1 6 4 8 5 3 5 5 7 . . 1 9 5 9 0 0 . . 3 0 0 5 4 1 3 8 0 0 . . 5 2 4 8 2 4 4 1 1 0 0 4 4 6 6 . . 6 5 3 9 9 1 9 6 5 8 . . 3 8 4 2
0.4 m FP ea R n 0 0 . . 5 0 0 5 4 5 1 5 0 0 . . 2 6 2 5 0 5 2 4 1 1 . . 4 5 5 8 0 9 1 9 34 -3 2 . 4 3 . 1 20 0 0 . . 5 0 0 5 1 2 1 4 0 0 . . 2 6 2 6 1 4 5 5 2 2 6 6 3 3 8 8 . . 2 2 8 9 4 1 6 6 34 1 9 5 9 .4 .6 1 8
XGB 0.45 m FP ea R n 0 0 . . 5 0 0 5 2 3 4 5 0 0 . . 2 6 4 7 2 2 8 7 1 1 . . 4 4 1 3 1 4 6 1 34 -3 2 . 4 3 . 1 20 0 0 . . 5 0 0 5 0 1 8 9 0 0 . . 2 6 4 7 2 5 8 6 2 2 6 6 5 5 5 5 . . 1 1 1 1 6 8 7 8 34 5 6 . 3 5 . 5 20
NUS-WIDE 0.5 m FP ea R n 0 0 . . 5 0 0 5 0 1 9 6 0 0 . . 2 6 7 9 1 8 9 1 1 2 . . 8 0 6 8 7 7 2 3 34 -3 2 . 4 3 . 1 20 0 0 . . 5 0 0 5 0 1 9 6 0 0 . . 2 6 7 9 1 8 9 1 2 2 6 6 5 5 1 1 . . 2 1 0 7 6 5 9 4 34 -3 2 . 4 3 . 1 20
0.4 m FP ea R n 0 0 . . 3 0 6 5 7 3 2 4 0 0 . . 0 0 8 5 9 7 4 1 1 0 1 . . 6 0 2 5 3 7 6 6 2 9 . . 8 8 6 7 0 0 . . 3 0 5 4 3 8 7 0 0 . . 0 0 5 9 9 2 6 2 2 6 6 4 4 7 7 . . 5 5 0 9 2 2 5 9 1 2 0 .9 .4 9 5
RMI 0.45 m FP ea R n 0 0 . . 3 0 3 5 0 0 1 4 0 0 . . 1 0 1 7 2 1 3 1 1 0 0 . . 4 8 3 1 7 1 7 9 2 9 . . 4 5 3 5 0 0 . . 3 0 2 4 1 6 6 3 0 0 . . 1 0 1 7 6 1 1 2 2 6 6 6 6 4 4 .2 .3 9 7 2 9 5 2 9 . . 5 9 2 5
0.5 m FP ea R n 0 0 . . 2 0 8 4 7 6 2 7 0 0 . . 1 0 2 8 9 7 4 1 1 1 1 . . 3 3 2 4 3 9 9 3 2 9 . . 1 5 8 4 0 0 . . 2 0 8 4 7 6 2 7 0 0 . . 1 0 2 8 9 7 4 2 2 6 6 6 6 0 0 . . 6 3 7 7 3 4 1 8 2 9 . . 1 5 8 4
TABLE V: Prediction quality (FPR and FNR) of Xling when XDT is computed in different ways (while fixing τ = 0).
There are two dimensions for a way to compute XDT: (1) using mean-based or FPR-based XDT selection method (2) using
interpolation-based method to approximate the targets or naive method to compute the exact targets. The time to compute the
targets is also presented (Time). Results on other datasets are similar to Glove and NUS-WIDE. Note that we allow XDT to
be less than zero.
approximatetargetsornaivelycomputedexacttargets).Inthis targetapproximationisbotheffectiveandhighlyefficient.For
section we evaluate the last two factors due to page limit. the factor of XDT selection, as mentioned in Section V-B,
Specifically, here we fix τ = 0. For each dataset, the learned the results present that FPR-based XDT selection usually
cardinalityestimatorofXlingisfirsttrainedusingthetraining generates a higher XDT than mean-based, thereby the former
set,thenwevarythesettingforthetwofactors,computeXDT tends to determine more queries as negative and causes lower
under each setting, and measure the FPR and FNR of Xling FPR and higher FNR than the latter. So in the end-to-end
on the testing set of the current dataset, as well as the time similarity join, using FPR-based XDT selection will lead to
for computing the training targets. higher speedup but lower quality than mean-based, which
supports the statements in Section V-B.
Due to space limit, Table V reports the results for two
representative models (i.e., XGB for non-deep and RMI for
deep model) on two datasets Glove (text) and NUS-WIDE
C. Filter effectiveness evaluation
(image). For the factor of target computing, the results show
that the two target computing methods usually lead to sim- In this section we evaluate the prediction quality between
ilar FPR and FNR, while our proposed interpolation-based XlingandLSBF,reportedbyFPRandFNRoftheirpredictions
target approximation is around 100x ∼ 2000x faster than for the testing sets. We fix τ = 0 as LSBF does not support
the naive target computing, meaning that interpolation-based the cases where τ >0.

TheresultsareincludedinTableVI.InadditiontoFPRand for these two datasets. SuperEGO relies on multi-threading
FNR,thetablealsoincludesthetotalnumberoftrueneighbors for acceleration, so on some datasets its running time is even
found for all the testing queries (#Nbrs) by Naive-LSBF and longer than the Naive method since we only use one thread
XJoin,thenumberofpredictedpositivequeries(#PPQ)which to evaluate all the methods. The results show that our method
are the query points predicted as positive by the filter, and XJoin has a higher speed (presented by the red bar) than all
the average number of neighbors per predicted positive query the baseline methods, as well as higher quality (reported by
(#ANPQ),i.e.,#ANPQ=#Nbrs/#PPQ.Wehavethefollowing the red line) than the other approximate methods (i.e., LSH,
observations: (1) In most cases, Xling with mean-based XDT KmeansTree and Naive-LSBF) in most cases. The recall of
has both lower FPR and FNR than LSBF, meaning it is more Naive and SuperEGO is always 1 as they are exact methods.
effectivethanLSBF.(2)Inmanycases,XlingwithFPR-based Specifically, XJoin achieves up to 17x and 14.6x speedup
XDT performs similarly to the observation above, while in respectively compared to the exact methods and approximate
someothercases,ithashigherFNRthanLSBF.However,even methods while guaranteeing a high quality. The results prove
with a higher FNR, it still finds more true neighbors in those the high efficiency and effectiveness of our proposed method.
cases than LSBF, e.g., the case of Word2vec under ϵ = 0.5.
E. Speed-quality trade-off evaluation
The reason is that the queries predicted as positive by Xling
overallhavemoreneighborsthanthosebyLSBF(reflectedby In this evaluation, We fix the dataset and ϵ, then vary some
#ANPQ), due to which Xling can find more true results with key parameters of the approximate baselines and XJoin, i.e.,
lessrangesearch(i.e.,the#PPQofFPR-basedXlingisusually n inLSH,thebranchingfactorandtheratioρinKmeansTree,
p
less than LSBF). In short, Xling learns the data distribution W andbitarraylengthinNaive-LSBF,C andpinIVFPQ,and
and makes predictions based on the data density, such that it theXDTselectionmode(meanorFPRbased)andτ inXJoin.
can maximize the recall with minimized number of search, For LSH and KmeansTree, we always set the parameters of
which is a huge advantage over the data-unaware LSBF. theirXling-enhancedversionsthesameastheoriginalversion,
inordertomakethecomparisonbetweenthemfair.Thevaried
D. End-to-end evaluation
parametersresultinvariedend-to-endsimilarityjointimeand
Inend-to-endevaluation,thekeyparametersforthemethods quality, based on which we get the speed-quality trade-off
are fixed as such: (1) Naive and SuperEGO have no user- curves, as illustrated in Figure 3.
specific parameters. (2) In LSH, the number of hash tables We select three cases to present in Figure 3: the datasets
l =10, number of has functions k =18, the number of hash Glove, Word2vec and Gist with ϵ=0.45, and other cases are
bucketstobeinspectedineachtablen =40fortextdatasets similartothem.Accordingtotheresults,weconcludethat(1)
p
while n = 2 for image datasets. (3) In KmeansTree, the XJoin has better trade-off capability than the original version
p
branching factor is fixed to be 3, the portion of leaves to be of the approximate baselines, i.e., LSH, IVFPQ, KmeansTree
inspectedρ=0.02fortextdatasetswhileρ=0.012forimage andNaive-LSBF,meaningthatXJoincanachievehighquality
datasets. (4) For Naive-LSBF, its LSH-related parameters k with minimum processing time, or sacrifice tiny quality for
and l are the same as the method LSH, length of the bit significant efficiency gain. (2) The Xling-enhanced versions
array in LSBF is fixed to be 2,160,000 (i.e., |R| × k), the of the approximate baselines (i.e., LSH-Xling, IVFPQ-Xling
parameter W in the p-stable LSH functions is set to be 2.5 and KmeansTree-Xling) have significant better trade-off ca-
for text datasets while W = 2 for image datasets. (5) For pability than the original versions, which also means Xling
IVFPQ, the parameters for building the index are C = 300, successfully accelerates the original versions with a relatively
m=32 or m=25 when the data dimension is not an integer negligible quality loss. This demonstrates the generality and
multiple of 32, b = 8, p = 50, where C is the number of usefulness of Xling to further enhance the existing similarity
clusters, m is the number of segments into which each data join methods and make them more practical.
vector will be split, b is the number of bits used to encode the
F. Generalization evaluation
clsutercentroids,andpisthenumberofnearestclusterstobe
inspected during search. In our implementation, this baseline In this section we evaluate the generalization capability of
first uses the IVFPQ index to select 1000 nearest neighbors Xling and XJoin. Another 150k dataset is sampled for each
then verifies them given ϵ. The number 1000 is determined originaldataset.Wecallthefirst150kdatasetsusedinprevious
sinceforalldatasets,atleast50%testingquerieshavelessthan experiments “the first 150k” or add “-1st” after the dataset
1000neighborswithinϵ,andinmostdatasets1000candidates name, while call the new dataset “the second 150k” or add
are enough to find all correct neighbors for 70% ∼ 90% “-2nd” after the name. The first and second 150k have no
testing queries. (6) The configuration of Xling is introduced overlap, except NUS-WIDE.
in Section VI-A, while the base methods in SuperEGO-Xling, We first evaluate the trade-off capabilities of XJoin and
LSH-Xling and KmeansTree-Xling use the same parameters Xling-enhancedmethodsagainonthesecond150k.AllXlings
as above. are those trained on the first 150k and used in the previous
The results are illustrated in Figure 2. SuperEGO has experiments. We do not re-train them anymore for the second
unknown bugs that prevent it from running on FastText and 150k. As shown in Figure 4, all those methods present a
NUS-WIDEdatasets,soFigure2doesnotincludeSuperEGO similar performance and trends as in Figure 3, which prove

|     |     |     |     |     |        | #Nbrs  | #PPQ |     |     |     |     |     | #Nbrs  | #PPQ   |
| --- | --- | --- | --- | --- | ------ | ------ | ---- | --- | --- | --- | --- | --- | ------ | ------ |
|     |     |     |     |     | (×105) | (×104) |      |     |     |     |     |     | (×105) | (×104) |
Dataset ϵ Filter FPR FNR #ANPQ Dataset ϵ Filter FPR FNR #ANPQ
LSBF 0.46 0.2908 127.73 2.05 624.58 LSBF 0.2415 0.6609 4.69 0.85 54.89
0.4 Xling(mean) Xling(FPR) 0.2523 0.0529 0.1114 0.207 142.15 141.90 2.46 2.13 578.95 664.94 0.4 Xling(mean) Xling(FPR) 0.06 0.0351 0.6119 0.6771 7.18 7.08 0.62 0.49 116.65 145.37
LSBF 0.5124 0.2471 296.05 2.23 1329.56 LSBF 0.2338 0.6358 13.04 0.96 136.42
FastText 0.45 Xling(mean) 0.3469 0.0682 325.25 2.72 1196.82 Sift 0.45 Xling(mean) 0.081 0.4565 19.49 1.15 170.09
Xling(FPR) 0.0948 0.1295 325.07 2.51 1295.92 Xling(FPR) 0.0537 0.5064 19.39 1.02 190.19
LSBF 0.5244 0.2062 708.64 2.37 2987.66 LSBF 0.2053 0.6139 35.54 1.08 330.55
0.5 Xling(mean) 0.3582 0.0376 767.57 2.87 2678.19 0.5 Xling(mean) 0.1798 0.237 52.83 2.02 261.36
Xling(FPR) 0.0802 0.099 767.23 2.68 2868.68 Xling(FPR) 0.0581 0.3678 52.50 1.63 321.55
LSBF 0.4952 0.4607 3.49 1.58 22.06 LSBF 0.2492 0.5687 1.39 0.76 18.19
0.4 Xling(mean) 0.374 0.3197 4.63 1.78 26.08 0.4 Xling(mean) 0.3671 0.057 2.14 1.15 18.65
Xling(FPR) 0.0502 0.7028 4.20 0.68 61.81 Xling(FPR) 0.0534 0.0894 2.14 0.23 94.32
LSBF 0.5516 0.3977 6.77 1.78 37.98 LSBF 0.2498 0.5374 2.82 0.77 36.53
Word2vec 0.45 Xling(mean) 0.4397 0.234 8.86 2.13 41.53 NUS-WIDE 0.45 Xling(mean) 0.3302 0.071 4.06 1.05 38.56
Xling(FPR) 0.0804 0.5996 8.19 1.04 78.70 Xling(FPR) 0.0503 0.1123 4.06 0.24 170.27
LSBF 0.5943 0.3419 13.04 1.96 66.56 LSBF 0.2469 0.5029 5.15 0.78 66.42
0.5 Xling(mean) 0.3019 0.2725 16.40 2.08 78.83 0.5 Xling(mean) 0.2873 0.087 6.98 0.95 73.69
Xling(FPR) 0.039 0.5882 15.15 1.15 132.22 Xling(FPR) 0.0467 0.1294 6.98 0.25 276.09
|     |     |     | (a) Text | datasets |     |     |     |     |     |     | (b) | Image datasets |     |     |
| --- | --- | --- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | --- |
TABLE VI: The prediction quality of LSBF and Xling (mean-based or FPR-based) on different datasets, where #Nbrs is the
total number of returned neighbors for all the queries, #PPQ stands for the number of Predicted Positive Queries, i.e., the
query points predicted as positive by the filter, and #ANPQ presents the Average number of Neighbors per predicted Positive
Query that equals #Nbrs over #PPQ. Due to space limit, the results on Glove and Gist datasets are hidden, which are similar
| to the | other | four. |     |          |     |     |     |     |            |     |     |            |     |       |
| ------ | ----- | ----- | --- | -------- | --- | --- | --- | --- | ---------- | --- | --- | ---------- | --- | ----- |
|        | Naive |       |     | SuperEGO |     | LSH |     |     | KmeansTree |     |     | Naive-LSBF |     | XJoin |
Naive(recall) SuperEGO(recall) LSH(recall) KmeansTree(recall) Naive-LSBF(recall) XJoin(recall)
|     | 450   |     |          |     | 1            | 450   |     |         |     | 1            | 600   |          |     | 1            |
| --- | ----- | --- | -------- | --- | ------------ | ----- | --- | ------- | --- | ------------ | ----- | -------- | --- | ------------ |
|     | 400   |     |          |     | 0.9          | 400   |     |         |     | 0.9          |       |          |     | 0.9          |
|     |       |     |          |     | 0.8          |       |     |         |     | 0.8          | 500   |          |     |              |
|     | 350   |     |          |     |              | 350   |     |         |     |              |       |          |     | 0.8          |
|     |       |     |          |     | 0.7          |       |     |         |     | 0.7          |       |          |     | 0.7          |
|     | 300   |     |          |     |              | 300   |     |         |     |              | 400   |          |     |              |
|     | )s( e |     |          |     | 0 . 6 llaceR | )s( e |     |         |     | 0 . 6 llaceR | )s( e |          |     | 0 . 6 llaceR |
|     | 2 5   | 0   |          |     |              | 2 5   | 0   |         |     | 0 . 5        |       |          |     |              |
|     | m 2 0 | 0   |          |     | 0 . 5        | m 2 0 | 0   |         |     |              | m 300 |          |     | 0 . 5        |
|     | iT    |     |          |     | 0 . 4        | iT    |     |         |     | 0 . 4        | iT    |          |     | 0 . 4        |
|     | 150   |     |          |     |              | 150   |     |         |     |              | 200   |          |     |              |
|     |       |     |          |     | 0.3          |       |     |         |     | 0.3          |       |          |     | 0.3          |
|     | 100   |     |          |     |              | 100   |     |         |     | 0.2          |       |          |     |              |
|     |       |     |          |     | 0.2          |       |     |         |     |              | 100   |          |     | 0.2          |
|     | 50    |     |          |     | 0.1          | 50    |     |         |     | 0.1          |       |          |     | 0.1          |
|     |       | 0   |          |     | 0            |       | 0   |         |     | 0            |       | 0        |     | 0            |
|     |       | 0.4 | 0.45     | 0.5 |              |       | 0.4 | 0.45    | 0.5 |              |       | 0.4 0.45 | 0.5 |              |
|     |       |     | Query ε  |     |              |       |     | Query ε |     |              |       | Query ε  |     |              |
|     |       |     | FastText |     |              |       |     | Glove   |     |              |       | Word2vec |     |              |
|     | 1600  |     |          |     | 1            | 250   |     |         |     | 1            | 900   |          |     | 1            |
|     |       |     |          |     | 0.9          |       |     |         |     | 0.9          | 800   |          |     | 0.9          |
1400
|     |          |     |     |     | 0.8    | 200           |        |        |        | 0.8         | 700                |     |     | 0.8    |
| --- | -------- | --- | --- | --- | ------ | ------------- | ------ | ------ | ------ | ----------- | ------------------ | --- | --- | ------ |
|     | 1200     |     |     |     |        |               |        |        |        | 0 . 7       |                    |     |     |        |
|     |          |     |     |     | 0 . 7  | 123456 000    | 000000 |        |        | 00000000001 | .... .....6789 6 0 | 0   |     | 0 . 7  |
|     | )s( e 10 | 0 0 |     |     | 0 . 6  | )s( e 15 0000 |        |        |        | 0 . 6       | 12345 )s( e        |     |     | 0 . 6  |
|     |          |     |     |     | llaceR | )             | 0      |        |        | llaceR      | l 5 0              | 0   |     | llaceR |
|     | m 8      | 0 0 |     |     | 0 . 5  | s m           |        |        |        | 0 . 5       | l m                |     |     | 0 . 5  |
|     | iT       |     |     |     |        | ( iT          |        |        |        |             | a iT 4 0           | 0   |     |        |
|     | 6        | 0 0 |     |     | 0 . 4  |   1 0         | 0      |        |        | 0 . 4       | c                  |     |     | 0 . 4  |
|     |          |     |     |     | 0 . 3  | e             | 0.     | 4 0 .4 | 5 0    | .5 0 . 3    | 3 0                | 0   |     | 0 . 3  |
|     | 4        | 0 0 |     |     |        |               |        | Q u e  | r y  ε |             | e                  |     |     |        |
|     |          |     |     |     | 0 . 2  | m 5           | 0      |        |        | 0 . 2       | R 2 0              | 0   |     | 0 . 2  |
200
|     |     |     |         |     | 0.1 | i   |     |         |     | 0.1 | 100 |                  |     | 0.1 |
| --- | --- | --- | ------- | --- | --- | --- | --- | ------- | --- | --- | --- | ---------------- | --- | --- |
|     |     | 0   |         |     | 0   | T   | 0   |         |     | 0   |     | 0                |     | 0   |
|     |     | 0.4 | 0.45    | 0.5 |     |     | 0.4 | 0.45    | 0.5 |     |     |                  |     |     |
|     |     |     | Query ε |     |     |     |     | Query ε |     |     |     | 0.4 Query ε 0.45 | 0.5 |     |
|     |     |     | Gist    |     |     |     |     | Sift    |     |     |     | NUS-WIDE         |     |     |
Fig. 2: End-to-end query processing time and recall for all the similarity join methods on all datasets, where the figures of
FastText and NUS-WIDE do not include SuperEGO, as it cannot run on these two datasets.
our statement in the Introduction that Xling and XJoin have lines and orange, “2nd Xling time”) are the two running time
great generalization capability thanks to the learning model, onthesecond150k.Thegreenandredlinesarethepercentage
and therefore it is not necessary to re-train Xling when the recall loss respectively on the first and second 150k, i.e., the
data is updated or even replaced with a fully new dataset, as difference between recall of original method and enhanced
long as the new data has similar distribution to the old. version over original recall on each dataset. The results show
|     |     |     |     |     |     |     |     | that | neither | time | improvement | nor recall | loss has | a significant |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | ------- | ---- | ----------- | ---------- | -------- | ------------- |
Tohaveafurtherquantitativeviewaboutthegeneralization,
differencebetweenfirstandsecond150k,whichfurtherprove
| we also | compare |     | the speed | improvement | and | the | recall loss |     |     |     |     |     |     |     |
| ------- | ------- | --- | --------- | ----------- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
made by Xling when attaching it to the base similarity our methods have outstanding generalization, meaning that
|          |          |        |            |        |              |         |            | they | are practical |     | in real | world.     |     |     |
| -------- | -------- | ------ | ---------- | ------ | ------------ | ------- | ---------- | ---- | ------------- | --- | ------- | ---------- | --- | --- |
| join     | methods. | In     | Figure 5,  | within | each method  | (marked | as         |      |               |     |         |            |     |     |
| “IVFPQ”, | “LSH”,   |        | etc.), the | first  | bar (solid   | and     | blue, “1st |      |               |     |         |            |     |     |
|          |          |        |            |        |              |         |            |      |               |     | VII.    | CONCLUSION |     |     |
| time”)   | and      | second | bar (solid | and    | orange, “1st | Xling   | time”)     |      |               |     |         |            |     |     |
aretheend-to-endrunningtimeoftheoriginalmethodandits In this paper we propose Xling, a generic framework of
Xling-enhanced version on the first 150k, while the third bar learned metric space Bloom filters for speeding up similarity
(diagonallinesandblue,“2ndtime”)andfourthbar(diagonal join with quality guarantee based on machine learning. Based

KmeansTree KmeansTree-Xling LSH LSH-Xling IVFPQ IVFPQ-Xling Naive-LSBF XJoin
|     | 300 |     |     |     |     | 400 |     |     |     |     | 1400 |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
350
|     | 250 |     |     |     |     |     |     |     |     |     | 1200 |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
300
1000
|     | 2 0   | 0   |     |     |     | )s( e 2 5 0 |     |     |     |     |             |     |     |     |     |
| --- | ----- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- |
|     | )s( e |     |     |     |     |             |     |     |     |     | )s( e 8 0 0 |     |     |     |     |
|     | 1 5   | 0   |     |     |     | 2 0 0       |     |     |     |     |             |     |     |     |     |
|     | m     |     |     |     |     | m           |     |     |     |     | m 6 0 0     |     |     |     |     |
|     | iT    |     |     |     |     | iT1 5 0     |     |     |     |     | iT          |     |     |     |     |
1 0 0
|     |     |     |     |     |     | 100 |     |     |     |     | 400 |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
50
|     |     |     |     |     |     | 50  |     |     |     |     | 200 |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0
|     |     | 0     |                  |         |     |     |                  |         |       |     | 0   |                  |         |       |     |
| --- | --- | ----- | ---------------- | ------- | --- | --- | ---------------- | ------- | ----- | --- | --- | ---------------- | ------- | ----- | --- |
|     |     | 0 0.2 | 0.4              | 0.6 0.8 | 1   |     | 0 0.2            | 0.4 0.6 | 0.8 1 |     | 0   | 0.2              | 0.4 0.6 | 0.8 1 |     |
|     |     |       | Recall (ε= 0.45) |         |     |     | Recall (ε= 0.45) |         |       |     |     | Recall (ε= 0.45) |         |       |     |
|     |     |       | Glove            |         |     |     | Word2vec         |         |       |     |     |                  | Gist    |       |     |
Fig. 3: Speed-quality trade-off curves for XJoin, the approximate methods and their Xling-enhanced versions on the selected
| datasets | a n d | ϵ , a n d other | c a s | e s a r e a | l s o similar. |     |     |                        |     |     |     |     |     |     |     |
| -------- | ----- | --------------- | ----- | ----------- | -------------- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- | --- |
|          |       |                 |       |             |                |     |     | 1122334 505050 0000000 |     |     |     |     |     |     |     |
)
|     |     |     |     |     |     |     |     | s 0500 |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
K m e an s Tr e e K m e a ns T r ee -X l in g LSH LS (H-Xling IVFPQ IVFPQ-Xling Naive-LSBF XJoin

|     | 400 |     |     |     |     | 450 |     | e   |     |     | 1500     |     |           |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | --------- | --- | --- |
|     |     |     |     |     |     |     |     |     |     |     | Recall ( |     | ε = 0.45) |     |     |
|     | 350 |     |     |     |     | 400 |     | m   | 0   |     |          | 0   | .5        |     | 1   |
|     |     |     |     |     |     | 350 |     |     |     |     | 1200     |     |           |     |     |
300
|     |         |     |     |     |     | 300   |     | i   |     |     |           |     |     |     |     |
| --- | ------- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --------- | --- | --- | --- | --- |
|     | )s( e 2 | 5 0 |     |     |     | )s( e |     | T   |     |     | )s( e 900 |     |     |     |     |
2 5 0
|     | m 2   | 0 0 |     |     |     | m2 0 0 |     |     |     |     | m     |     |     |     |     |
| --- | ----- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | ----- | --- | --- | --- | --- |
|     | iT150 |     |     |     |     | iT150  |     |     |     |     | iT600 |     |     |     |     |
100
|     |     |           |                  |         |     | 100 |                  |         |       |     | 300 |                  |         |       |     |
| --- | --- | --------- | ---------------- | ------- | --- | --- | ---------------- | ------- | ----- | --- | --- | ---------------- | ------- | ----- | --- |
|     |     | 50        |                  |         |     | 50  |                  |         |       |     |     |                  |         |       |     |
|     |     | 0         |                  |         |     | 0   |                  |         |       |     | 0   |                  |         |       |     |
|     |     |           |                  |         |     |     | 0 0.2            | 0.4 0.6 | 0.8 1 |     |     |                  |         |       |     |
|     |     | 0 0.2     | 0.4              | 0.6 0.8 | 1   |     | Recall (ε= 0.45) |         |       |     | 0   | 0.2              | 0.4 0.6 | 0.8 1 |     |
|     |     |           | Recall (ε= 0.45) |         |     |     |                  |         |       |     |     | Recall (ε= 0.45) |         |       |     |
|     |     | Glove-2nd |                  |         |     |     | Word2vec-2nd     |         |       |     |     | Gist-2nd         |         |       |     |
Fig. 4: Speed-quality trade-off curves for XJoin, the approximate methods and their Xling-enhanced versions on the second
150k datasets, where all Xlings are pre-trained on the original 150k 2n1122334 d X505050 dataset 0000000 without re-training for the second
1st time 1st Xling time 2nd time ) ling  time 1st recall loss (%) 2nd recall loss (%)
|     |     |     |     |     |     |     |     | s 05 00 |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
(
|     |     |     |     |     |     | 400   |     |     | 20  |     |              |     |              |       |     |
| --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | ------------ | --- | ------------ | ----- | --- |
|     | 300 |     |     |     | 7   |       |     | e   |     |     | 1400         |     |              | 18    |     |
|     |     |     |     |     |     | 3 5 0 |     |     | 1 8 |     |              |     |              | 16    |     |
|     | 250 |     |     |     | 6   |       |     | m   | 06  |     | R1200ecall ( | 0   | ε .5 = 0.45) |       | 1   |
|     |     |     |     |     |     | 3 0 0 |     |     | 1   |     |              |     |              | 1 4   |     |
|     |     |     |     |     | 5   |       |     |     | 14  |     | 1000         |     |              |       |     |
|     | 2 0 | 0   |     |     | )%  | 2 5 0 |     | i   | )%  |     |              |     |              | 1 2)% |     |
)s(em 4 ( ssol llaceR )s(em T 1 2 ( ssol llaceR )s(em 8 0 0 1 0 ( ssol llaceR
|     | 1 5 | 0   |     |     |     | 2 0 0 |     |     | 1 0 |     |          |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | -------- | --- | --- | --- | --- |
|     | iT  |     |     |     | 3   | iT    |     |     |     |     | iT 6 0 0 |     |     | 8   |     |
|     |     |     |     |     |     | 1 5 0 |     |     | 8   |     |          |     |     |     |     |
|     | 1 0 | 0   |     |     |     |       |     |     | 6   |     |          |     |     | 6   |     |
|     |     |     |     |     | 2   | 1 0 0 |     |     |     |     | 4 0 0    |     |     |     |     |
|     |     |     |     |     |     |       |     |     | 4   |     |          |     |     | 4   |     |
|     | 50  |     |     |     | 1   | 50    |     |     | 2   |     | 200      |     |     | 2   |     |
|     |     | 0   |     |     | 0   | 0     |     |     | 0   |     | 0        |     |     | 0   |     |
IVFPQ LSH KmeansTree Naive IVFPQ LSH KmeansTree Naive IVFPQ LSH KmeansTree Naive
|     |     |       | Recall (ε= 0.45) |     |     |     |          | Recall (ε= 0.45) |     |     |     |          | Recall (ε= 0.45) |     |     |
| --- | --- | ----- | ---------------- | --- | --- | --- | -------- | ---------------- | --- | --- | --- | -------- | ---------------- | --- | --- |
|     |     | Glove | 1st vs 2nd       |     |     |     | Word2vec | 1st vs 2nd       |     |     |     | Gist 1st | vs 2nd           |     |     |
Fig. 5: The differences of acceleration and recall loss resulting from Xling on the first and second 150k datasets
|     |     |     |     |     |     |     |     |     |     |     |     |     | 111 024 0000000 | 000 | )0246811111 02468 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ----------------- |
2468 0000
|     |     |     |     |     |     |     |     |     |     |     |     |     | )   | 0   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |     |     |     |     |     |     |     |     |     |     | s   |     | %   |
on Xling we develop an efficient and effective similarity join and(J.
|     |     |     |     |     |     |     |     | [2] C. Yang,                     | D. H. | Hoang, | T. Mikolov, |     | Han, “Place                      | deduplication |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------- | ----- | ------ | ----------- | --- | -------------------------------- | ------------- | --- |
|     |     |     |     |     |     |     |     | withembeddings,”inTheWorldWideWe |       |        |             |     | e bConference,2I0V19,FpPp.Q3420– |               | (   |
method that outperforms the state-of-the-art methods on both
|     |     |     |     |     |     |     |     | 3426. |     |     |     |     | m   |     | s   |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
speed and quality, as well as having a better speed-qRuaelitcyall (ε = 0.45) s
|           |            |     |                    |     |             |     |         | [3] H. B. | da Silva, | Z. K. | do Patroc´ınio, | G.  | IGravier, L. Amsaleg, | A.  | d. A.o |
| --------- | ---------- | --- | ------------------ | --- | ----------- | --- | ------- | --------- | --------- | ----- | --------------- | --- | --------------------- | --- | ------ |
| trade-off | capability |     | and generalization |     | capability. |     | We also |           |           |       |                 |     |                       |     |        |
Arau´jo,andS.J.F.Guimaraes,“Near-dupTlicatevideodetectionbasedon
l
applyXlingontothosestate-of-the-artmethodstosignificantly anapproximatesimilarityself-joinstrategy,”in201614thInternational  l
IEEE,2016,l
further enhance them. Xling has shown the great potential in WorkshoponContent-BasedMultimediaIndexing(CBMI). a
pp.1–6.
c
effectivelyspeedingupawiderangeofexistingsimilarityjoin [4] L. Zhou, J. Chen, A. Das, H. Min, L. Yu, M. Zhao, and J. Zou,e
methods. “Serving deep learning models with deduplication from relationalR
|     |     |     |     |     |     |     |     | databases,” | Proceedings |     | of the | VLDB | Endowment, vol. | 15, no. | 10, p. |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ----------- | --- | ------ | ---- | --------------- | ------- | ------ |
REFERENCES 2230–2243, Jun. 2022. [Online]. Available: http://dx.doi.org/10.14778/
3547305.3547325
[1] B. Gyawali, L. Anastasiou, and P. Knoth, “Deduplication of [5] R. Sarwar, C. Yu, N. Tungare, K. Chitavisutthivong, S. Sriratanawilai,
scholarly documents using locality sensitive hashing and word Y.Xu,D.Chow,T.Rakthanmanon,andS.Nutanong,“Aneffectiveand
|     |              |                |     |        |         |          |           | scalable | framework | for | authorship | attribution | query | processing,” | IEEE |
| --- | ------------ | -------------- | --- | ------ | ------- | -------- | --------- | -------- | --------- | --- | ---------- | ----------- | ----- | ------------ | ---- |
|     | embeddings,” | in Proceedings |     | of the | Twelfth | Language | Resources |          |           |     |            |             |       |              |      |
and Evaluation Conference. Marseille, France: European Language Access,vol.6,pp.50030–50048,2018.
Resources Association, May 2020, pp. 901–910. [Online]. Available: [6] B. Ha¨ttasch, M. Truong-Ngoc, A. Schmidt, and C. Binnig, “It’s ai
https://aclanthology.org/2020.lrec-1.113 match: A two-step approach for schema matching using embeddings,”

2022.[Online].Available:https://arxiv.org/abs/2203.04366 [29] S. Macke, A. Beutel, T. Kraska, M. Sathiamoorthy, D. Z. Cheng, and
[7] N.Adly,“Efficientrecordlinkageusingadoubleembeddingscheme.” E. H. Chi, “Lifting the curse of multidimensional data with learned
inDMIN,2009,pp.274–281. existenceindexes,”inWorkshoponMLforSystemsatNeurIPS,2018,
| [8] S.Herath,M.Roughan,andG.Glonek,“Em-kindexingforapproximate |     |     |     |     |     |     |     | pp.1–6. |     |     |     |     |     |     |     |
| -------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
querymatchinginlarge-scaleer,”2021. [30] M. Mitzenmacher, “A model for learned bloom filters and optimizing
bysandwiching,”AdvancesinNeuralInformationProcessingSystems,
| [9] F. Nargesian, |     | E. Zhu, | K. Q. Pu, | and R. J. | Miller, “Table | union | search |     |     |     |     |     |     |     |     |
| ----------------- | --- | ------- | --------- | --------- | -------------- | ----- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
vol.31,2018.
| on open | data,” | Proc. | VLDB Endow., | vol. | 11, no. 7, | p. 813–825, | mar |     |     |     |     |     |     |     |     |
| ------- | ------ | ----- | ------------ | ---- | ---------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2018.[Online].Available:https://doi.org/10.14778/3192965.3192973 [31] A. Bhattacharya, C. Gudesa, A. Bagchi, and S. Bedathur, “New wine
[10] A.Berenguer,J.-N.Mazo´n,andD.Toma´s,“Towardsatabularopendata in an old bottle: Data-aware hash functions for bloom filters,” Proc.
searchengineforpublicsectorinformation,”in2021IEEEInternational VLDB Endow., vol. 15, no. 9, p. 1924–1936, may 2022. [Online].
Available:https://doi.org/10.14778/3538598.3538613
ConferenceonBigData(BigData),2021,pp.5851–5853.
|               |           |          |          |                    |            |                  |          | [32] J.Sun,G.Li,andN.Tang,“Learnedcardinalityestimationforsimilarity |     |             |     |                        |     |            |     |
| ------------- | --------- | -------- | -------- | ------------------ | ---------- | ---------------- | -------- | -------------------------------------------------------------------- | --- | ----------- | --- | ---------------------- | --- | ---------- | --- |
| [11] Y. Dong, | K.        | Takeoka, | C. Xiao, | and M. Oyamada,    | “Efficient |                  | joinable |                                                                      |     |             |     |                        |     |            |     |
|               |           |          |          |                    |            |                  |          | queries,”                                                            | in  | Proceedings | of  | the 2021 International |     | Conference | on  |
| table         | discovery | in data  | lakes:   | A high-dimensional |            | similarity-based |          |                                                                      |     |             |     |                        |     |            |     |
approach,” in 2021 IEEE 37th International Conference on Data En- ManagementofData,2021,pp.1745–1757.
gineering(ICDE). IEEE,2021,pp.456–467. [33] Y.Wang,C.Xiao,J.Qin,X.Cao,Y.Sun,W.Wang,andM.Onizuka,
“Monotoniccardinalityestimationofsimilarityselection:Adeeplearn-
| [12] X. Yuan, | X.  | Wang, | C. Wang, | C. Yu, and | S. Nutanong, |     | “Privacy- |     |     |     |     |     |     |     |     |
| ------------- | --- | ----- | -------- | ---------- | ------------ | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
ingapproach,”inProceedingsofthe2020ACMSIGMODInternational
preservingsimilarityjoinsoverencrypteddata,”IEEETransactionson
ConferenceonManagementofData,2020,pp.1197–1212.
| Information |     | Forensics | and Security, | vol. | 12, no. 11, | pp. 2763–2775, |     |     |     |     |     |     |     |     |     |
| ----------- | --- | --------- | ------------- | ---- | ----------- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2017. [34] J.Qin,W.Wang,C.Xiao,Y.Zhang,andY.Wang,“High-dimensional
[13] J.Yao,X.Meng,Y.Zheng,andC.Wang,“Privacy-preservingcontent- similarity query processing for data science,” in Proceedings of
|     |     |     |     |     |     |     |     | the | 27th ACM | SIGKDD | Conference | on  | Knowledge | Discovery | and |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------ | ---------- | --- | --------- | --------- | --- |
basedsimilaritydetectionoverin-the-cloudmiddleboxes,”IEEETrans-
|     |     |     |     |     |     |     |     | Data | Mining, | ser. KDD | ’21. | New York, | NY, | USA: Association |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | ------- | -------- | ---- | --------- | --- | ---------------- | --- |
actionsonCloudComputing,vol.11,no.2,pp.1854–1870,2023.
|         |            |     |            |           |                  |     |       | for Computing |     | Machinery, | 2021, | p. 4062–4063. |     | [Online]. Available: |     |
| ------- | ---------- | --- | ---------- | --------- | ---------------- | --- | ----- | ------------- | --- | ---------- | ----- | ------------- | --- | -------------------- | --- |
| [14] M. | Perdacher, | C.  | Plant, and | C. Bo¨hm, | “Cache-oblivious |     | high- |               |     |            |       |               |     |                      |     |
https://doi.org/10.1145/3447548.3470811
| performance |     | similarity | join,” in | Proceedings | of the 2019 | International |     |     |     |     |     |     |     |     |     |
| ----------- | --- | ---------- | --------- | ----------- | ----------- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Conference on Management of Data, ser. SIGMOD ’19. New York, [35] Y. Wang, C. Xiao, J. Qin, R. Mao, M. Onizuka, W. Wang, R. Zhang,
andY.Ishikawa,“Consistentandflexibleselectivityestimationforhigh-
| NY, | USA: Association |     | for Computing | Machinery, |     | 2019, p. | 87–104. |     |     |     |     |     |     |     |     |
| --- | ---------------- | --- | ------------- | ---------- | --- | -------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
dimensionaldata,”inProceedingsofthe2021InternationalConference
[Online].Available:https://doi.org/10.1145/3299869.3319859
onManagementofData,2021,pp.2319–2327.
| [15] C. Bo¨hm, | B.  | Braunmu¨ller, | F. Krebs, | and | H.-P. Kriegel, | “Epsilon | grid |                                                               |     |     |     |     |     |     |     |
| -------------- | --- | ------------- | --------- | --- | -------------- | -------- | ---- | ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|                |     |               |           |     |                |          |      | [36] T.Kraska,A.Beutel,E.H.Chi,J.Dean,andN.Polyzotis,“Thecase |     |     |     |     |     |     |     |
order:Analgorithmforthesimilarityjoinonmassivehigh-dimensional
Proceedings of the 2001 ACM SIGMOD International for learned index structures,” in Proceedings of the 2018 international
| data,”     | in               |               |               |            |        |          |          | conferenceonmanagementofdata,2018,pp.489–504.                     |     |                |     |             |            |               |     |
| ---------- | ---------------- | ------------- | ------------- | ---------- | ------ | -------- | -------- | ----------------------------------------------------------------- | --- | -------------- | --- | ----------- | ---------- | ------------- | --- |
| Conference |                  | on Management | of            | Data, ser. | SIGMOD | ’01. New | York,    |                                                                   |     |                |     |             |            |               |     |
|            |                  |               |               |            |        |          |          | [37] H.ZhangandQ.Zhang,“Embedjoin:Efficienteditsimilarityjoinsvia |     |                |     |             |            |               |     |
| NY,        | USA: Association |               | for Computing | Machinery, | 2001,  | p.       | 379–388. |                                                                   |     |                |     |             |            |               |     |
|            |                  |               |               |            |        |          |          | embeddings,”                                                      |     | in Proceedings |     | of the 23rd | ACM SIGKDD | International |     |
[Online].Available:https://doi.org/10.1145/375663.375714
ConferenceonKnowledgeDiscoveryandDataMining,ser.KDD’17.
| [16] D. | V. Kalashnikov |     | and S. Prabhakar, |     | “Fast similarity |     | join for |     |           |      |             |               |     |                  |     |
| ------- | -------------- | --- | ----------------- | --- | ---------------- | --- | -------- | --- | --------- | ---- | ----------- | ------------- | --- | ---------------- | --- |
|         |                |     |                   |     |                  |     |          | New | York, NY, | USA: | Association | for Computing |     | Machinery, 2017, | p.  |
multi-dimensional data,” Information Systems, vol. 32, no. 1, pp. 585–594.[Online].Available:https://doi.org/10.1145/3097983.3098003
| 160–177, | 2007. | [Online]. | Available: | https://www.sciencedirect.com/ |     |     |     |                                                                |     |     |     |     |     |     |     |
| -------- | ----- | --------- | ---------- | ------------------------------ | --- | --- | --- | -------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|          |       |           |            |                                |     |     |     | [38] Y.WangandD.Z.Wang,“Learnedacceleratorframeworkforangular- |     |     |     |     |     |     |     |
science/article/pii/S0306437905000761
distance-basedhigh-dimensionaldbscan,”2023.
[17] D.V.Kalashnikov,“Super-ego:fastmulti-dimensionalsimilarityjoin,”
|     |     |     |     |     |     |     |     | [39] Y.Wang,C.Xiao,J.Qin,X.Cao,Y.Sun,W.Wang,andM.Onizuka, |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
TheVLDBJournal,vol.22,no.4,pp.561–585,2013. “Monotonic cardinality estimation of similarity selection: A deep
[18] C.Yu,S.Nutanong,H.Li,C.Wang,andX.Yuan,“Agenericmethodfor learning approach,” in Proceedings of the 2020 ACM SIGMOD
acceleratinglsh-basedsimilarityjoinprocessing(extendedabstract),”in International Conference on Management of Data, ser. SIGMOD ’20.
2017IEEE33rdInternationalConferenceonDataEngineering(ICDE),
|     |     |     |     |     |     |     |     | New | York, | NY, USA: | Association | for Computing |     | Machinery, | 2020, |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | -------- | ----------- | ------------- | --- | ---------- | ----- |
2017,pp.29–30.
|                                                                  |     |     |     |     |     |     |     | p. 1197–1212. |     | [Online]. | Available: | https://doi.org/10.1145/3318464. |     |     |     |
| ---------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | --------- | ---------- | -------------------------------- | --- | --- | --- |
| [19] H.Li,S.Nutanong,H.Xu,c.YU,andF.Ha,“C2net:Anetwork-efficient |     |     |     |     |     |     |     | 3380570       |     |           |            |                                  |     |     |     |
approach to collision counting lsh similarity join,” IEEE Transactions [40] S. Macke, A. Beutel, T. Kraska, M. Sathiamoorthy, D. Z. Cheng, and
onKnowledgeandDataEngineering,vol.31,no.3,pp.423–436,2019. E. H. Chi, “Lifting the curse of multidimensional data with learned
[20] Z. Yang, W. T. Ooi, and Q. Sun, “Hierarchical, non-uniform locality existenceindexes,”2018.
| sensitive | hashing | and | its application | to video | identification,” |     | in 2004 |               |     |          |         |                  |     |             |        |
| --------- | ------- | --- | --------------- | -------- | ---------------- | --- | ------- | ------------- | --- | -------- | ------- | ---------------- | --- | ----------- | ------ |
|           |         |     |                 |          |                  |     |         | [41] Y. Wang, | C.  | Xiao, J. | Qin, R. | Mao, M. Onizuka, |     | W. Wang, R. | Zhang, |
IEEEInternationalConferenceonMultimediaandExpo(ICME)(IEEE andY.Ishikawa,“Consistentandflexibleselectivityestimationforhigh-
Cat.No.04TH8763),vol.1,2004,pp.743–746Vol.1. dimensionaldata,”inProceedingsofthe2021InternationalConference
[21] Y.Hua,B.Xiao,B.Veeravalli,andD.Feng,“Locality-sensitivebloom onManagementofData,2021,pp.2319–2327.
filterforapproximatemembershipquery,”IEEETransactionsonCom- [42] A. Andoni, P. Indyk, T. Laarhoven, I. Razenshteyn, and L. Schmidt,
puters,vol.61,no.6,pp.817–830,2012.
|     |     |     |     |     |     |     |     | “Practical | and | optimal | lsh for | angular distance,” |     | Advances in | neural |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ------- | ------- | ------------------ | --- | ----------- | ------ |
[22] J. Qian, Q. Zhu, and H. Chen, “Integer-granularity locality-sensitive informationprocessingsystems,vol.28,2015.
bloomfilter,”IEEECommunicationsLetters,vol.20,no.11,pp.2125– [43] M. Muja and D. G. Lowe, “Fast approximate nearest neighbors with
2128,2016. automatic algorithm configuration.” VISAPP (1), vol. 2, no. 331-340,
| [23] M.Goswami,R.Pagh,F.Silvestri,andJ.Sivertsen,“Distancesensitive |     |     |     |     |     |     |     | p.2,2009. |     |     |     |     |     |     |     |
| ------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
bloomfilterswithoutfalsenegatives,”2016. [44] H.Jegou,M.Douze,andC.Schmid,“Productquantizationfornearest
[24] J. Qian, Z. Huang, Q. Zhu, and H. Chen, “Hamming metric neighbor search,” IEEE transactions on pattern analysis and machine
multi-granularity locality-sensitive bloom filter,” IEEE/ACM Trans. intelligence,vol.33,no.1,pp.117–128,2010.
Netw., vol. 26, no. 4, p. 1660–1673, aug 2018. [Online]. Available: [45] J. Johnson, M. Douze, and H. Je´gou, “Billion-scale similarity search
https://doi.org/10.1109/TNET.2018.2850536 withgpus,”arXivpreprintarXiv:1702.08734,2017.
[25] J. Qian, Q. Zhu, and H. Chen, “Multi-granularity locality-sensitive [46] Y.Wang,H.Ma,andD.Z.Wang,“Lider:Anefficienthigh-dimensional
|                 |          |      |              |               |      |         |         | learned                                    | index | for large-scale |     | dense passage | retrieval,” | 2022. [Online]. |     |
| --------------- | -------- | ---- | ------------ | ------------- | ---- | ------- | ------- | ------------------------------------------ | ----- | --------------- | --- | ------------- | ----------- | --------------- | --- |
| bloom           | filter,” | IEEE | Transactions | on Computers, | vol. | 64, no. | 12, pp. |                                            |       |                 |     |               |             |                 |     |
| 3500–3514,2015. |          |      |              |               |      |         |         | Available:https://arxiv.org/abs/2205.00970 |       |                 |     |               |             |                 |     |
[26] A. Kirsch and M. Mitzenmacher, “Distance-sensitive bloom filters,” in [47] L. V. Nguyen, T.-H. Nguyen, and J. J. Jung, “Content-based
2006 Proceedings of the Eighth Workshop on Algorithm Engineering collaborative filtering using word embedding: A case study on movie
|                         |     |     |                     |     |     |     |     | recommendation,” |     | in       | Proceedings    | of the   | International | Conference | on  |
| ----------------------- | --- | --- | ------------------- | --- | --- | --- | --- | ---------------- | --- | -------- | -------------- | -------- | ------------- | ---------- | --- |
| andExperiments(ALENEX). |     |     | SIAM,2006,pp.41–50. |     |     |     |     |                  |     |          |                |          |               |            |     |
|                         |     |     |                     |     |     |     |     | Research         | in  | Adaptive | and Convergent | Systems, | ser.          | RACS ’20.  | New |
[27] Y.Hua,X.Liu,Y.Hua,andX.Liu,“Locality-sensitivebloomfilterfor
|     |     |     |     |     |     |     |     | York, | NY, USA: | Association |     | for Computing | Machinery, | 2020, | p.  |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | -------- | ----------- | --- | ------------- | ---------- | ----- | --- |
approximatemembershipquery,”SearchableStorageinCloudComput-
ing,pp.99–127,2019. 96–100.[Online].Available:https://doi.org/10.1145/3400286.3418253
[28] T.Kraska,A.Beutel,E.H.Chi,J.Dean,andN.Polyzotis,“Thecase
forlearnedindexstructures,”2018.