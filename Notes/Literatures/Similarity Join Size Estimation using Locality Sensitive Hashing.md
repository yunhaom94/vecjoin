| Similarity |     |     | Join | Size |     | Estimation |     | using |     | Locality |     |     | Sensitive |     |     |
| ---------- | --- | --- | ---- | ---- | --- | ---------- | --- | ----- | --- | -------- | --- | --- | --------- | --- | --- |
Hashing∗
|     |     | Hongrae | Lee |     |     |     | Raymond | T. Ng |     |     | Kyuseok |     | Shim |     |     |
| --- | --- | ------- | --- | --- | --- | --- | ------- | ----- | --- | --- | ------- | --- | ---- | --- | --- |
UniversityofBritishColumbia UniversityofBritishColumbia SeoulNationalUniversity
|     | xguy@cs.ubc.ca |     |     |     |     |     | rng@cs.ubc.ca |     |     | shim@ee.snu.ac.kr |     |     |     |     |     |
| --- | -------------- | --- | --- | --- | --- | --- | ------------- | --- | --- | ----------------- | --- | --- | --- | --- | --- |
ABSTRACT
queryrefinementforwebsearch,coalitiondetection[3],and
|     |     |     |     |     |     |     |     | datacleaningprocesses[17,2]. |     |     |     | Accordingly,similarityjoins |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --------------------------- | --- | --- | --- |
Similarityjoinsareimportantoperationswithabroadrange
|                 |      |                                     |     |        |       |               |     | have recently | received |             | much attention, |            | e.g. | [17, 2,   | 6, 3, 11]. |
| --------------- | ---- | ----------------------------------- | --- | ------ | ----- | ------------- | --- | ------------- | -------- | ----------- | --------------- | ---------- | ---- | --------- | ---------- |
| ofapplications. |      | Inthispaper,westudytheproblemofvec- |     |        |       |               |     |               |          |             |                 |            |      |           |            |
|                 |      |                                     |     |        |       |               |     | Chaudhuri     | et al.   | identified  | a               | similarity | join | operation | as a       |
| tor similarity  | join | size estimation                     |     | (VSJ). | It is | a generaliza- |     |               |          |             |                 |            |      |           |            |
|                 |      |                                     |     |        |       |               |     | primitive     | operator | in database |                 | systems    | [6]. |           |            |
tionofthepreviouslystudiedsetsimilarityjoinsizeestima-
|            |         |     |            |      |             |     |       | To successfully |     | incorporate |     | similarity | join | operations | in  |
| ---------- | ------- | --- | ---------- | ---- | ----------- | --- | ----- | --------------- | --- | ----------- | --- | ---------- | ---- | ---------- | --- |
| tion (SSJ) | problem | and | can handle | more | interesting |     | cases |                 |     |             |     |            |      |            |     |
databasesystems,itisimperativethatwehavereliablesize
| such as TF-IDF |      | vectors.   | One of  | the key | challenges |     | in sim- |            |           |     |       |     |       |           |       |
| -------------- | ---- | ---------- | ------- | ------- | ---------- | --- | ------- | ---------- | --------- | --- | ----- | --- | ----- | --------- | ----- |
|                |      |            |         |         |            |     |         | estimation | technique | for | them. | The | query | optimizer | needs |
| ilarity join   | size | estimation | is that | the     | join size  | can | change  |            |           |     |       |     |       |           |       |
dramatically depending on the input similarity threshold. accurate size estimations to produce an optimized query
WeproposeasamplingbasedalgorithmthatusesLocality- plan. Thus, in this paper, we focus on the size estimation
|     |     |     |     |     |     |     |     | of vector | similarity | joins. |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ---------- | ------ | --- | --- | --- | --- | --- |
Sensitive-Hashing(LSH).TheproposedalgorithmLSH-SS
|     |     |     |     |     |     |     |     | In the | literature, | the | similarity | join | size | estimation | prob- |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ----------- | --- | ---------- | ---- | ---- | ---------- | ----- |
usesanLSHindextoenableeffectivesamplingevenathigh
|             |     |         |              |     |           |      |      | lem has been | defined | using | sets | as  | follows: |     |     |
| ----------- | --- | ------- | ------------ | --- | --------- | ---- | ---- | ------------ | ------- | ----- | ---- | --- | -------- | --- | --- |
| thresholds. | We  | compare | the proposed |     | technique | with | ran- |              |         |       |      |     |          |     |     |
dom sampling and the state-of-the-art technique for SSJ Definition 2 (The SSJ Problem). Givenacollection
(adaptedtoVSJ)anddemonstrateLSH-SS offersmoreac- of real-valued sets S = {s ,...,s } and a threshold τ on a
|     |     |     |     |     |     |     |     |     |     |     | 1   | n   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
curate estimates throughout the similarity threshold range similarity measure sim, estimate the number of pairs J =
and small variance using real-world data sets. |{(r,s):r,s∈S,sim(r,s)≥τ,r(cid:54)=s}|.
|     |     |     |     |     |     |     |     | Note that | our formulation |     | of  | similarity | joins | with | vectors |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --------------- | --- | --- | ---------- | ----- | ---- | ------- |
1. INTRODUCTION ismoregeneralandcanhandlemorepracticalapplications.
|       |              |         |     |       |         |            |     | For instance, | while | in the | SSJ | problem | a document |     | is sim- |
| ----- | ------------ | ------- | --- | ----- | ------- | ---------- | --- | ------------- | ----- | ------ | --- | ------- | ---------- | --- | ------- |
| Given | a similarity | measure |     | and a | minimum | similarity |     |               |       |        |     |         |            |     |         |
threshold, a similarity join is to find all pairs of objects ply a set of words in the document, in the VSJ problem a
whosesimilarityisnotsmallerthanthesimilaritythreshold. document can be modeled with a vector of words with TF-
Theobjectinasimilarityjoinisoftenavector. Forinstance, IDF weights. It can also deal with multiset semantics with
a document can be represented by a vector of words in the occurrences. In fact, most of the studies on similarity joins
document,oranimagecanberepresentedbyavectorfrom firstformulatetheproblemwithsetsandthenextenditwith
its color histogram. In this paper, we focus on the vector TF-IDF weights, which is indeed a vector similarity join.
representation of objects and study the following problem. The SSJ problem has been previously studied by Lee et
|     |     |     |     |     |     |     |     | al. [14]. | A straightforward |     | extension |     | of SSJ | techniques | for |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----------------- | --- | --------- | --- | ------ | ---------- | --- |
Definition 1 (The VSJ Problem). Givenacollection the VSJ problem is to embed a vector into a set space. We
of real-valued vectors V = {v ,...,v } and a threshold τ convert a vector into a set by treating a dimension as an
1 n
on a similarity measure sim, estimate the number of pairs element and repeating the element as many times as the
J =|{(u,v):u,v∈V,sim(u,v)≥τ,u(cid:54)=v}|.
|            |       |      |         |       |                 |     |     | dimensionvalue, |              | usingstandard |              | roundingtechniques |          |          | ifval- |
| ---------- | ----- | ---- | ------- | ----- | --------------- | --- | --- | --------------- | ------------ | ------------- | ------------ | ------------------ | -------- | -------- | ------ |
|            |       |      |         |       |                 |     |     | ues are not     | integral     | [2].          | In practice, |                    | however, | this     | embed- |
| Similarity | joins | have | a broad | range | of applications |     | in- |                 |              |               |              |                    |          |          |        |
|            |       |      |         |       |                 |     |     | ding can        | have adverse |               | effects      | on performance,    |          | accuracy | or     |
cludingnearduplicatedocumentdetectionandelimination,
|           |       |             |        |          |          |       |         | requiredresources.                                  |         | Intuitively,asetisaspecialcaseofabi- |        |            |     |        |            |
| --------- | ----- | ----------- | ------ | -------- | -------- | ----- | ------- | --------------------------------------------------- | ------- | ------------------------------------ | ------ | ---------- | --- | ------ | ---------- |
| ∗         |       |             |        |          |          |       |         | naryvectorandisnotmoredifficulttohandlethanavector. |         |                                      |        |            |     |        |            |
| This work | was   | supported   | by the | National | Research |       | Foun-   |                                                     |         |                                      |        |            |     |        |            |
|           |       |             |        |          |          |       |         | For instance,                                       | Bayardo |                                      | et al. | [3] define | the | vector | similarity |
| dation of | Korea | (NRF) grant | funded | by       | the      | Korea | govern- |                                                     |         |                                      |        |            |     |        |            |
joinproblemandaddspecialoptimizationsthatarepossible
| ment (MEST) | (No. | 2010-0000793). |     |     |     |     |     |              |              |        |             |         |        |            |        |
| ----------- | ---- | -------------- | --- | --- | --- | --- | --- | ------------ | ------------ | ------ | ----------- | ------- | ------ | ---------- | ------ |
|             |      |                |     |     |     |     |     | when vectors | are          | binary | vectors     | (sets). |        |            |        |
|             |      |                |     |     |     |     |     | In our       | VSJ problem, |        | we consider |         | cosine | similarity | as the |
Permissiontomakedigitalorhardcopiesofallorpartofthisworkfor similarity measure sim since it has been successfully used
personalorclassroomuseisgrantedwithoutfeeprovidedthatcopiesare
|     |     |     |     |     |     |     |     | acrossseveraldomains[3]. |     |     | Letu[i]denotethei-thdimension |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | --- | ----------------------------- | --- | --- | --- | --- |
notmadeordistributedforprofitorcommercialadvantageandthatcopies
bearthisnoticeandthefullcitationonthefirstpage.Tocopyotherwise,to valueofvectoru. Cosinesimilarityisdefinedascos(u,v)=
|     |     |     |     |     |     |     |     |     |     |     | (cid:80) |     |     | (cid:112)(cid:80) |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | --- | ----------------- | --- |
republish,topostonserversortoredistributetolists,requirespriorspecific u·v/(cid:107)u(cid:107)(cid:107)v(cid:107),whereu·v= u[i]·v[i]and(cid:107)u(cid:107)= u[i]2.
permissionand/orafee. Articlesfromthisvolumewereinvitedtopresent i i
Wefocusonself-joinsanddiscussextensionstogeneraljoins
theirresultsatThe37thInternationalConferenceonVeryLargeDataBases,
|     |     |     |     |     |     |     |     | in Appendix | B.2. |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ---- | --- | --- | --- | --- | --- | --- |
August29th-September3rd2011,Seattle,Washington.
Oneofthekeychallengesinsimilarityjoinsizeestimation
ProceedingsoftheVLDBEndowment,Vol.4,No.6
Copyright2011VLDBEndowment2150-8097/11/03...$10.00. is that the join size can change dramatically depending on
338

the input similarity threshold. While the join size can be adaptivesampling[15],cross/index/tuplesampling[10],bi-
close to n2 at low thresholds where n is the database size, focal sampling [9], and tug-of-war [1]. Some of them can
itcanbeverysmallathighthresholds. Forinstance,inthe be adapted to similarity joins, but their guarantees do not
DBLP data set, the join selectivity is only about 0.00001 hold due to differences in sampling cost models or they re-
% at τ = 0.9. While many sampling algorithms have been quireimpracticalsamplesizes. Below,weoutlinetwoclosely
proposed for the (equi-)join size estimation, their guaran- related sampling algorithms.
tees fail in such a high selectivity range, e.g. [15, 10, 9]. Adaptive sampling is proposed by Lipton et al [15]. Its
Intuitively, it is not practical to apply simple random sam- main idea is to terminate sampling process when the query
pling when the selectivity is very high. This is problematic size (the accumulated answer size from the sample so far)
sincesimilaritythresholdsbetween0.5and0.9aretypically reachesathresholdnotwhenthenumberofsamplesreaches
used [3]. Note that the join size in that range may be large athreshold. Whileitdoesnotproducereliableestimatesin
enough to affect query optimization due to the large cross skewed data, we observe that its adaptive nature can still
product size. Moreover, as observed in [13], join size errors beusefulfortheVSJproblem. Itisusedasasubroutinein
propagate. That is, even if the original errors are small, our solution in Section 5.
their transitive effect can be devastating. Bifocal sampling is proposed by Ganguly et al. to cope
Inthispaper,weproposesamplingbasedtechniquesthat withtheskeweddataproblem[9]. Ittacklestheproblemby
exploittheLocalitySensitiveHashing(LSH)scheme,which considering high-frequency values and low-frequency values
has been successfully applied in similarity searches across withseparateprocedures. However,aswillbeshownshortly,
manydomains. LSHbuildshashtablessuchthatsimilarob- itcannotguaranteegoodestimatesathighthresholdswhen
jectsaremorelikelytobeinthesamebucket. Ourkeyidea applied to the VSJ problem.
isthatalthoughsamplingapairsatisfyingahighthreshold
isverydifficult,itisrelativelyeasytosamplethepairusing 3. BASELINEMETHODS
| the LSH                             | scheme       | because        | it groups     | similar    | objects         | together.  |        |                    |           |                                       |                   |               |                |              |           |
| ----------------------------------- | ------------ | -------------- | ------------- | ---------- | --------------- | ---------- | ------ | ------------------ | --------- | ------------------------------------- | ----------------- | ------------- | -------------- | ------------ | --------- |
| We show                             | that         | the proposed   | algorithm     | LSH-SS     |                 | gives      | good   |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | 3.1 RandomSampling |           |                                       |                   |               |                |              |           |
| estimates                           | throughout   | the            | similarith    | threshold  | √               | range      | with a |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | The first          | baseline  |                                       | method            | is uniform    | random         |              | sampling. |
| samplesizeofΩ(n)pairsofvectors(i.e. |              |                |               |            | Ω( n)tuplesfrom |            |        |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | We select          | m pairs   | of                                    | vectors uniformly |               | at random      |              | (with re- |
| each join                           | relation     | in an          | equi-join)    | with       | probabilistic   |            | guar-  |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | placement)         | and       | count                                 | the number        |               | of pairs       | satisfying   | the       |
| antees.                             | The proposed | solution       |               | only needs | minimal         | addition   |        |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | similarity         | threshold | τ.                                    | We return         | the           | count          | scaled       | up by     |
| to the existing                     |              | LSH index      | and           | thus is    | readily         | applicable |        |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | M/mwhereM          |           | denotesthetotalnumberofpairsofvectors |                   |               |                |              |           |
| to many                             | similarity   | search         | applications. |            | As a            | summary,   | we     |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | in the database    |           | V. We                                 | also consider     |               | an alternative |              | method    |
| make the                            | following    | contributions: |               |            |                 |            |        |                    |           | √                                     |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | of first sampling  |           | m                                     | records           | and computing |                | similarities | of        |
|                                     |              |                |               |            |                 |            |        | all the pairs      | in        | the sample                            | (cross            | sampling      |                | [10]).       |           |
| • We                                | present      | two baseline   |               | methods    | in Section      |            | 3. We  |                    |           |                                       |                   |               |                |              |           |
|                                     |              |                |               |            |                 |            |        | Equi-join          | size      | estimation                            | techniques        |               | mostly         | do           | not offer |
considerrandomsamplingandadaptLatticeCounting
|       |            |          |              |            |            |          |       | clear benefits                     | over    | the   | simple       | random                | sampling             | in      | the VSJ  |
| ----- | ---------- | -------- | ------------ | ---------- | ---------- | -------- | ----- | ---------------------------------- | ------- | ----- | ------------ | --------------------- | -------------------- | ------- | -------- |
| (LC)  | [14]       | which is | proposed     | for the    | SSJ        | problem. |       |                                    |         |       |              |                       |                      |         |          |
|       |            |          |              |            |            |          |       | problem.                           | We note | two   | challenges   | in                    | the VSJ              | problem | com-     |
| • We  | extend     | the LSH  | index        | to support | similarity |          | join  |                                    |         |       |              |                       |                      |         |          |
|       |            |          |              |            |            |          |       | paredtotheequi-joinsizeestimation. |         |       |              |                       | Intheequi-joinsizeof |         |          |
| size  | estimation | in       | Section      | 4. We also | propose    |          | LSH-S |                                    |         |       |              |                       |                      |         |          |
|       |            |          |              |            |            |          |       | |R(cid:46)(cid:47)S|,              | we can  | focus | on frequency | distribution          |                      | on      | the join |
| which | relies     | on an    | LSH function | analysis.  |            |          |       |                                    |         |       |              |                       |                      |         |          |
|       |            |          |              |            |            |          |       | columnofeachrelationRandS.         |         |       |              | Forinstance,ifweknowa |                      |         |          |
• We describe a stratified sampling algorithm LSH-SS value v appears n (v) times in R and n (v) times in S, the
|     |     |     |     |     |     |     |     |     |     | r   |     |     | s   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
that exploits the LSH index in Section 5. We apply contribution of v in the join size is simply n (v)·n (v), i.e.
r s
different sampling procedures for the two partitions multiplication of two frequencies. We do not need to com-
induced by an LSH index: pairs of vectors that are in pareallthen (v)·n (v)pairs. Insimilarityjoins, however,
r s
the same bucket and those that are not. we need to actually compare the pairs to measure similar-
|     |     |     |     |     |     |     |     | ity. This | difficulty | invalidates |     | the use | of popular |     | auxiliary |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ---------- | ----------- | --- | ------- | ---------- | --- | --------- |
• Wecomparetheproposedsolutionswithrandomsam-
|       |              |          |            |           |        |            |        | structures   | such | as indexes | [10, | 7] or | histograms | [7].       |     |
| ----- | ------------ | -------- | ---------- | --------- | ------ | ---------- | ------ | ------------ | ---- | ---------- | ---- | ----- | ---------- | ---------- | --- |
| pling | and          | LC using | real-world | data      | sets   | in Section | 6.     |              |      |            |      |       |            |            |     |
|       |              |          |            |           |        |            |        | Furthermore, |      | similarity | join | size  | at high    | thresholds | can |
| The   | experimental |          | results    | show that | LSH-SS |            | is the |              |      |            |      |       |            |            |     |
most accurate with small variance. be much smaller than the join size assumed in equi-joins.
|     |     |     |     |     |     |     |     | For instance,    | in  | the     | DBLP data | set     | (n =     | 800K),  | the join |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------- | --------- | ------- | -------- | ------- | -------- |
|     |     |     |     |     |     |     |     | size of Ω(nlogn) |     | assumed | in        | bifocal | sampling | is more | than     |
2. RELATEDWORK
|     |     |     |     |     |     |     |     | 15M pairsandcorrespondstothecosinesimilarityvalueof |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
Many algorithms have been proposed on the similarity only about 0.4. In the most cases, users will be interested
join processing, e.g. [17, 2, 6, 3]. Their focus is not on size in much smaller join sizes and thus higher thresholds.
| estimation. | In  | fact, the | existence | of many | join | processing |     |                                 |     |     |     |     |     |     |     |
| ----------- | --- | --------- | --------- | ------- | ---- | ---------- | --- | ------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|             |     |           |           |         |      |            |     | 3.2 AdaptationofLatticeCounting |     |     |     |     |     |     |     |
algorithmsmotivatesthesizeestimationstudyforqueryop-
timization. Most of them studied set similarity joins with Lattice Counting (LC) is proposed by Lee et al. [14] to
complex weights such as TF-IDF or vector similarity joins. estimate SSJ size with Jaccard similarity. Jaccard simi-
Lee et al. proposed LC for the SSJ problem [14]. We larity between two sets A,B is defined as sim (A,B) =
J
presentthistechniqueinmoredetailsinthefollowingsection |A∩B|/|A∪B|. LCreliesonsuccinctrepresentationofsets
andcomparewiththeproposedsolutionintheexperiments. usingMin-Hashing[4]. AusefulpropertyofMin-Hashingis
Hadjieleftheriou et al. studied the problem of selectivity that if h is a Min-Hash function then P(h(A) = h(B)) =
estimationforsetsimilarityselection(notjoin)queries[11]. sim (A,B). For each set A, a signature of the set sig(A)
J
There have been many studies using random sampling isconstructedbyconcatenatingk Min-Hashfunctions. Jac-
for the (equi-)join size estimation; some examples include card similarity between two sets A,B can be estimated by
339

thenumberofpositionsofsig(A)andsig(B)whichoverlap. Pr[ g(u) = g(v) ] Pr[ g(u) ≠ g(v) ]
LC performs an analysis on the signatures of all sets. For 1 1
our purposes, LC can be treated as a black box. P[L∩T]
P[H∩T]
We observe that the analysis of LC is valid as long as
the number of matching positions in the signatures of two
objectsisproportionaltotheirsimilarity. Notethatthisre-
quirementisexactlythepropertyoftheLSHscheme. Thus
LCcanbeappliedfortheVSJproblemwithanappropriate
LSH scheme. In fact, Min-Hashing is the LSH scheme for 0 similarity τ 1 0 similarity τ 1
Jaccard similarity. For the VSJ problem, we first build the (a) PDF for LSH collision (b) PDF for LSH non-collision
u & v are in the same bucket u & v are not in the same bucket
signaturedatabasebyapplyinganLSHschemetothevector
database and then apply LC. Figure 1: Probability Density Functions of (non-)
collision in the LSH scheme
4. LSHINDEXFORTHEVSJPROBLEM
WefirstdescribehowweextendtheLSHindexandpresent
4.2 EstimationwithUniformityAssumption
a naive method with a uniformity assumption, and then
present LSH-S which improves it with random sampling. GivenacollectionofvectorsV,andasimilaritythreshold
τ,letM denotethenumberoftotalpairsinV,i.e. M =
(cid:0)n(cid:1)
.
4.1 Preliminary: LSHIndexing 2
Consider a random pair (u,v),u,v,∈ V,u (cid:54)= v. We denote
Let H be a family of hash functions such that h ∈ H : the event sim(u,v) ≥ τ by T, and the event sim(u,v) <
Rd →U. Consider a function h that is chosen uniformly at τ by F. We call (u,v) a true pair (resp. false pair) if
random from H and a similarity function sim:Rd×Rd → sim(u,v)≥τ (resp. sim(u,v)<τ). Dependingonwhether
[0,1]. The family H is called locality sensitive if it satisfies uandvareinthesamebucket,wedenotetheeventB(u)=
the following property [5]. B(v) by H and the event B(u) (cid:54)= B(v) by L. With these
notations,wecandefinevariousprobabilities. Forinstance,
Definition 3. [Locality Sensitive Hashing] For any vec-
P(T) is the probability of sampling a true pair. P(H|T)
tors u,v∈Rd,
is the probability that a true pair is in the same bucket
P(h(u)=h(v))=sim(u,v). andP(T|H)istheprobabilitythatapairof vectorsfroma
bucket is a true pair. We use N to denote the cardinality
That is, the more similar a pair of vectors is, the higher E
of the set of pairs that satisfy the condition of event E. For
the collision probability is. The LSH scheme works as fol-
instance, N is the number of true pairs (the VSJ size J)
lows[12,5]: Foranintegerk,wedefineafunctionfamilyG = T
{g : Rd → Uk} such that g(v) = (h 1 (v),...,h k (v)), where b an e d co N m H pu is te t d he b n y u N mbe = ro (cid:80) fp n a g ir (cid:0) s b i j n (cid:1) . thesamebucket. N H can
h i ∈H, i.e. g is the concatenation of k LSH functions. For The key observa H tion is j t = h 1 at 2 any pair of vectors from a
an integer (cid:96), we choose (cid:96) functions G = {g ,...,g } from G
1 (cid:96) bucket is either a true pair or a false pair. Using Bayes’
independently and uniformly at random. Each g ,1≤i≤(cid:96)
i rule [16], we can express this observation as follows: N =
effectivelyconstructsahashtabledenotedbyD . Abucket H
gi N ·P(H|T)+N ·P(H|F). That is, the total number of
in D stores all v ∈ V that have the same g values. For T F
gi i pairsofvectorsinthesamebucketisthesumofthenumber
space,onlyexistingbucketsarestoredusingstandardhash-
oftruepairsthatareinthesamebucket(N ·P(H|T))and
ing. G defines a collection of (cid:96) tables I = {D ,...,D } T
G g1 g(cid:96) the number of false pairs that happened to be in the same
and we call it an LSH index. Table 3 in appendix is a sum-
bucket(N ·P(H|F)). SinceN =M−N ,rearrangingthe
mary of notations. F F T
termsgivesN =(N −M·P(H|F))/(P(H|T)−P(H|F)).
LSHfamilieshavebeendevelopedforseveral(dis)similarity T H
Using ‘ˆ’ for an estimated quantity, we have an estimator
measuresincludingHammingdistance,(cid:96) distance,Jaccard
p for the join size J(=N ) as follows:
similarity,andcosinesimilarity. WerelyontheLSHscheme T
proposed by Charikar [5] that supports cosine similarity. N −M ·Pˆ(H|F)
Nˆ =Jˆ = H . (1)
Theproposedalgorithmscaneasilysupportothersimilarity T U Pˆ(H|T)−Pˆ(H|F)
measures by using an appropriate LSH family.
Note that M and N are constants given V and D . The
H g
4.1.1 ExtendingTheLSHSchemewithBucketCounts conditional probabilities in Equation (1) need to be esti-
WedescribealgorithmsbasedonasingleLSHtable: g= mated to compute Nˆ . We next present our first estimator
T
(h ,...,h )withkhashfunctionsandanLSHtableD . Ex- that relies on an LSH function analysis and a uniformity
1 k g
tensionswithmultipleLSHtablesareinAppendixB.2. Sup- assumption to estimate the conditional probabilities.
posethatD hasn buckets;allvectorsinthedatabaseare Consider a random pair (u,v) such that sim(u,v) is se-
g g
hashed into one of the n buckets. We denote a bucket by lected from [0,1] uniformly at random. Recall that when
g
B ,1≤j ≤n . Given a vector v, B(v) denotes the bucket sim(u,v) = s, P(h(u) = h(v)) = s from Definition 3.
j g
towhichvbelongs. IntheLSHtable,eachbucketB stores P(g(u) = g(v)) = sk since g concatenates k hash values.
j
the set of vectors that are hashed into B . We extend the Figure 1(a) shows the collision probability density function
j
conventionalLSHtablebyaddingabucketcountb foreach (PDF) f(s)=sk where s=sim(u,v). The vertical dotted
j
bucketB thatisthenumberofvectorsinthedatabasethat line represents the similarity threshold τ. The darker area
j
arehashedintoB . Theoverheadofaddingabucketcount on the right side of the τ line is the good collision probabil-
j
to each bucket is not significant compared to other infor- ity,i.e. theprobabilitythatB(u)=B(v)(uandvareinthe
mation such as vectors. Depending on implementation, the same bucket) and sim(u,v) ≥ τ. Thus the area represents
count may be readily available. P(H ∩T). Likewise, the area on the left side of the τ line
340

is P(H ∩F), which is the probability that sim(u,v) < τ, An interesting view of an LSH index is that it partitions
butB(u)=B(v). Noticethattheareabelowf(s)doesnot allpairsofvectorsinV intotwostrata: pairsthatareinthe
equal to 1 since it does not cover the entire event space; u same bucket and pairs that are not. The pairs in the same
andvmaynotbeinthesamebucket. Figure1(b)showsthe bucket are likely to be more similar from the property of
other case where u and v are in different buckets. Its PDF LSH (Def. 3). Recall that the difficulty of sampling at high
is 1−f(s) as shown as the curve. P(L∩T) and P(L∩F) thresholds is that the join size is very small and sampling
are defined similarly as shown in the figure. a true pair is hard. Our key intuition is that even at high
Giveng(andthusf)andτ,P(H∩F),P(H∩T),P(L∩F) thresholds it is relatively easy to sample a true pair from
andP(L∩T)canbeestimatedbycomputingthecorrespond- the set of pairs that are in the same bucket.
ingareasinFigure1. Basedontheseareas,wecanestimate We demonstrate our intuition with a real-world example.
the desired conditional probabilities using the following: Table 1 shows actual probabilities varying τ in the DBLP
data set. We observe that other than at low thresholds,
P(H∩T)
P(H|T) = (2) say 0.1 ∼ 0.3, P(T) is close to 0, which implies that naive
P(H∩T)+P(L∩T)
randomsamplingisnotgoingtoworkwellwithanyreason-
P(H∩F) ablesamplesize. However,notethatP(T|H)isconsistently
P(H|F) = . (3)
P(H∩T)+P(L∩F) higher than 0.04 even at high thresholds. That is, it is not
difficult to sample true pairs among the pairs in the same
PluggingP(H|T)andP(H|F)computedasaboveintoEqua-
bucket. P(H|T) is large at high thresholds but very small
tion (1), we have the following estimator for the VSJ size:
at low thresholds. This means that at high thresholds, a
(k+1)N −τk·M sufficient fraction of true pairs are in the same bucket. But
Jˆ = H . (4)
U (cid:80)k−1τi at low thresholds, most of true pairs are not in the same
i=0 bucket, which implies that the estimate from the pairs in
We give its derivation in Appendix A.1.
thesamebucketisnotenough. However,atlowthresholds,
WenotethatJˆ implicitlyassumesthatthesimilarityof
U P(T|L) becomes larger and thus sampling from the pairs
pairs is uniformly distributed in [0,1]. However, this distri-
that are not in the same bucket becomes feasible.
butionisgenerallyhighlyskewed[14];mostofpairshavelow
similarityvaluesandonlyasmallnumberofpairshavehigh τ P(T) P(T|H) P(H|T) P(T|L)
similarityvalues. WenextpresentLSH-S thatremovesthe 0.1 .082 0.31 0.00001 0.082
uniformity assumption with sampling. 0.3 .00024 0.054 0.00041 0.00024
0.5 .0000034 0.049 0.0028 0.000032
4.3 LSH-S:RemovingUniformityAssumption 0.7 3.9E-7 0.045 0.21 2.8E-7
0.9 9.1E-8 0.040 0.86 1.3E-8
We consider two methods to remove the uniformity as-
sumption. First, we estimate the conditional probabilities Table 1: An example probabilities in DBLP
by random sampling without resorting to the LSH func-
For sampling in general, it has been observed that “if
tion analysis. For instance, we can estimate P(H|T) by
intelligently used, stratification nearly always results in a
counting the number of pairs in the same bucket among
smaller variance for the estimated mean or total than is
the true pairs in the sample. Second, we weight the condi-
given by a comparable simple random sampling” [8, p99].
tional probabilities using samples. For example, if all the
Weproposebelowonespecificschemeforstratifiedsampling
pairs in the sample have a similarity value of 0.3, we can
using LSH, and show its benefit empirically at Section 6.
only consider similarity s=0.3 in Figure 1 without consid-
ering the whole area. We call the second method LSH-S 5.1 LSH-SS:StratifiedSampling
andpresentonlyLSH-S sinceitoutperformedthefirstone Wedefinetwostrataofpairsofvectorsasfollowsdepend-
in our experiments. In LSH-S, for each similarity s that ingonwhethertwovectorsofapairareinthesamebucket.
appears in the sample, the f(s) value is weighted by the
occurrence of s in the sample. For a sample S, we use the • Stratum H (S H ): {(u,v):u,v∈V,B(u)=B(v)}
following weight: w(s)=|{(u,v)∈S :sim(u,v)=s}|/|S|.
• Stratum L (S ): {(u,v):u,v∈V,B(u)(cid:54)=B(v)}
For instance, if similarities in S are {0.1,0.1,0.1,0.2,0.2}, L
w(0.1)=3/5,w(0.2)=2/5 and w(s)=0 for s∈/ {0.1,0.2}. Note that S and S are disjoint and thus we can in-
H L
LetS denotethesubsetoftruepairsinS andS denote dependently estimate the join size from each stratum and
T F
S−S . With this weighting scheme, since f(s)=sk, add the two estimates. S and S are fixed given D . Let
T H L g
Pˆ(H|T) = (cid:88) (sim(u,v))k/|S T | (5) s J i H m = (u, |{ v ( ) u ≥ ,v τ ) } ∈ |, S a H nd : l s e i t m Jˆ (u, a v n ) d ≥ Jˆ τ} b |, e J t L he = ir | e { s ( t u im ,v a ) te ∈ s. S W L e :
H L
(u,v)∈ST estimate the join size as follows:
Pˆ(H|F) = (cid:88) (sim(u,v))k/|S F |. (6) Jˆ =Jˆ +Jˆ . (7)
SS H L
(u,v)∈SF
A straightforward implementation would be to perform
LSH-S uses Equations (5) and (6) in Equation (1).
uniformrandomsamplinginS andS ,andaggregatethe
H L
5. STRATIFIEDSAMPLINGUSINGLSH twoestimates. However,thissimpleapproachmaynotwork
well. The problem is that it can be harder to guarantee
AdifficultyinLSH-Sisthattheconditionalprobabilities, a small error of Jˆ with the same sample size due to very
L
e.g. P(H|T),needtobeestimatedanditishardtoacquire
smallP(T|L)athighthresholds[15]. Seethenextexample.
reliable estimates of them. In this section, we present an
algorithm that overcomes this difficulty by using the LSH Example 1. Assume that N = 1,000,000, J = 1 at
L L
index in a slightly different way. τ = 0.9, and the sample size is 10; only one pair out of
341

1,000,000 pairs satisfies τ = 0.9 and we sample 10 pairs. Algorithm 1 LSH-SS
Inmostcases, thetrue pairwillnotbesampledandJˆ L =0. Procedure LSH-SS
But if the only true pair is sampled, Jˆ L =100,000. The es- Input: similarity threshold τ, sample size for Stratum H mH,
timate fluctuates between 0 and 100,000 and is not reliable. answersizethresholdδ,maxsamplesizeforStratumLmL
1: Jˆ H =SampleH(τ,mH)
Our solution for this problem is to use different sampling 2: Jˆ L=SampleL(τ,δ,mL)
procedures in the two strata. Recall that similarities of the 3: returnJˆ SS =Jˆ H+Jˆ L
pairs in S are higher and P(T|H) is not too small, even Procedure SampleH
H
at high thresholds. Thus, for S
H
, we use uniform random Input: τ,mH (samplesize)
sampling. Relatively small sample size will suffice for reli- 1: nH =0
able estimation in S . In S , however, P(T|L) varies sig-
2: forifrom1tomH do
nificantly depending
H
on the t
L
hreshold. In general, while at
3: sampleabucketBj withweight(Bj)= (cid:0)b
2
j (cid:1)
lowthresholdsP(T|L)isrelativelyhighandtheestimateis
4: sampletwovectorsu,v∈Bj,u(cid:54)=v
5: if sim(u,v)≥τ then
reliable, P(T|L) becomes very small at high thresholds and 6: nH =nH+1
theresultingestimateismorelikelytohavealargeerrorand 7: endif
ismuchlessreliable. Forthesamesamplesize,thevariance 8: endfor
itself decreases as the join size decreases (e.g. Lemma 4.1 9: returnJˆ H =nH·NH/mH
of [1]). However, we may need many more samples at high Procedure SampleL
thresholds, where the join size can be very small, to have Input: τ,δ (answersizeth.),mL (samplesizeth.)
the same error guarantee [15, 9]. 1: i=0,nL=0
Thus,weuseJˆ L onlywhenitisexpectedtobereliableand 2 3 : : wh s i a l m e p n l L ea < u δ ni a f n o d rm i< ran m d L om do pair(u,v),B(u)(cid:54)=B(v)
discardJˆ L whenitisnot. DiscardingJˆ L athighthresholds 4: if sim(u,v)≥τ then
generallydoesnothurtaccuracymuchsincethecontribution 5: nL=nL+1
of J in J is not large. In Table 1, when the similarity 6: endif
L
thresholdsishigh,P(H|T)islarge,whichmeansthatalarge 7: i=i+1
8: endwhile
fractionoftruepairsareinS ,notinS . Weuseadaptive
sampling [15] in S L since it e H nables us t L o detect when the 1 9 0 : : if i r ≥ etu m r L n t J h ˆ L en = nL // or Jˆ L = nL ·cs(NL/mL) when a
estimate is not reliable. A novelty is that we return a safe dampeningfactor0<cs≤1isused.
lower bound when we cannot have a good error guarantee 11: endif
within the allowable sample size. 12: returnJˆ L=nL·(NL/i)
Algorithm1describestheproposedstratifiedsamplingal-
gorithmLSH-SS. Itappliesadifferentsamplingsubroutine
toeachstratum. ForS H ,itrunstherandomsamplingsub- such cases. In the latter case, adaptive sampling returns a
routine SampleH. For S L , it runs the adaptive sampling loose upper bound. We cannot guarantee that the estimate
subroutine SampleL. The final estimate is the sum of esti- isreliableandsimplyreturnthenumberoftruepairsfound
mates from the two Strata as in Equation (7) (line 3). in the sample, n , as Jˆ without scaling it up. Since J is
L L L
at least as large as n , we call Jˆ =n a safe lower bound.
5.1.1 SamplinginStratumH L L L
This conservative approach does not degrade accuracy
SampleH of Algorithm 1 describes the random sampling much since the majority of true pairs are in S at high
H
inS H . First,abucketB j israndomlysampledweightedby thresholds. It is possible, however, that there can be “grey
the number of pairs in the bucket, weight(B j ) =
(cid:0)b
2 j
(cid:1)
(line area” of thresholds. While the random sampling does not
3). We then select a random pair (u,v) from B j (line 4). guaranteeitsaccuracy,thereareenoughtruepairsinS L to
The resulting pair (u,v) is a uniform random sample from make its impact on underestimation significant. Hence, we
S H . SampleH has one tunable parameter m H which is the considertheuseofadampenedscale-upconstant0<c s ≤1,
sample size. We count the number of pairs satisfying the which is multiplied to the full scaling-up factor at line 10.
similarity threshold τ in m H sample pairs and return the We analyze the impact of this dampened scale-up factor in
count scaled up by N H /m H (line 9). the following section.
Forthetunableparameters,weusedm =nandm =n
H L
5.1.2 SamplinginStratumL and δ =logn1 where n is the database size, n=|V|. Note
SampleLofAlgorithm1employsadaptivesampling[15]in thatthesizeisexpressedinthenumberofpairs. Thiscorre-
√
S . Ithastwotunableparametersδandm . δistheanswer sponds to sampling n vectors from two collections of vec-
L L √ √
sizethreshold,thenumberoftruesamplestogiveareliable tors(n= n× n)inequi-joins,whichisevensmallerthan
√
estimate, and m is the maximum number of samples. We thesamplesize nlognin[9]. Theseparametervaluesgive
L
sample a pair from S (line 3) and see if it satisfies the provably good estimates at both high and low thresholds.
L
giventhreshold(line4). IncaseLSHcomputationforbucket We give the details in the following section.
checking at line 3 is expensive, we can delay the checking
5.2 Analysis
till line 5, which in effect results in slightly more samples.
The while-loop at line 2 can terminate in two ways: (1) by Let α=P(T|H) and β =P(T|L) for the sake of presen-
acquiringasufficientlylargenumberoftruesamples,n L ≥δ tation. In our analysis, a similarity threshold τ is consid-
or(2)byreachingthesamplesizethreshold,i≥m L ,where ered high when α ≥ logn/n and β < 1/n, and is consid-
i is the number of samples taken. In the former case, we ered low when α ≥ logn/n and β ≥ logn/n. Our model
return the count scaled up by N /i (line 12). Theorem 2.1
L
and 2.2 of adaptive sampling [15] provide error bounds in 1All logarithms used are base-2 logarithms.
342

is analogous to the classic approach of distinguishing high Compared with Theorem 1, the guarantee of Theorem 2 is
frequencyvaluesfromlowfrequencyvaluestomeetthechal- weaker in terms of probability, but it provides a tighther
lenge of skewed data, e.g.[9, 7]. Our distinction effectively bound; 1−c < (cid:15)(cid:48) < 1. The dampened scale-up factor c
|     |     |     |     |     |     |     |     |     | s   |     |     |     |     |     | s   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
models different conditional probabilities that are observed representsthetrade-offsbetweentheaccuracyandtheprob-
in different threshold values as in Table 1. abilistic guarantee. Using a smaller c s enables a stronger
Wefirstanalyzethehighthresholdcaseandthenthelow guarantee in probability reducing variance by a factor of c s
thresholdcase. Thisdistinctionisonlyfortheanalysispur- (see Appendix A.3), but the relative error bound increases.
poses. The behavior of Algorithm 1 is adaptive and users We discuss the choice of c in Section 6.
s
| do not | need to | distinguish |     | two cases | by parameters. |     |     |     |     |     |     |     |     |     |     |
| ------ | ------- | ----------- | --- | --------- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
5.2.2 Guaranteesatlowthresholds
5.2.1 Guaranteesathighthresholds
|     |     |     |     |     |     |     |     | At low thresholds, |     | we assume |     | that | α ≥ logn/n | and | β ≥ |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --------- | --- | ---- | ---------- | --- | --- |
Recall that α=P(T|H) is the probability that a pair of logn/n. The rationale is that as the actual join size in-
vectors in a bucket is indeed a true pair and β =P(T|L) is creases, more true pairs are in S and sampling true pairs
L
theprobabilitythatapairofvectorsthatarenotinthesame in S becomes not so difficult any more. Again these con-
L
| bucket | is a true | pair. | We assume |     | α≥logn/n | and | β <1/n |             |         |          |     |           |     |        |        |
| ------ | --------- | ----- | --------- | --- | -------- | --- | ------ | ----------- | ------- | -------- | --- | --------- | --- | ------ | ------ |
|        |           |       |           |     |          |     |        | ditions are | usually | met when | the | threshold | is  | low as | in the |
at high thresholds. The condition on α intuitively states example in Table 1. In fact, the contribution from S L , J L
that even when the join size is small, the fraction of true dominates the join size at low thresholds. The following
pairsinS H isnottoosmallfrom thepropertyofLSH. Our theorem states that LSH-SS gives a reliable estimate even
assumptiononαisnotastringentcondition, i.e. logn/nis when the threshold is low. See Appendix A.4 for a proof.
usuallyaverysmallvalueandwillbeeasilysatisfiedbyany
|            |         |     |            |     |           |     |          | Theorem | 3.  | Let 0 < | (cid:15) < | 1 be an | arbitrary | constant. |     |
| ---------- | ------- | --- | ---------- | --- | --------- | --- | -------- | ------- | --- | ------- | ---------- | ------- | --------- | --------- | --- |
| reasonably | working |     | LSH index. | The | condition | on  | β states |         |     |         |            |         |           |           |     |
thatitishardtosampletruepairsinS athighthresholds. Assume α ≥ logn/n and β ≥ logn/n. Then with c =
|     |     |     |     |     | L   |     |     | 4/(loge·(cid:15)2),c(cid:48) |     |     |     |     |     |     | =c(cid:48)n, |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- | --- | --- | ------------ |
As a sanity check, consider the example in Table 1. In =max(c,1/(1−(cid:15))),m H =cnandm L
| the data | set, | n = 34,000 | and | β ∼ | 0.00003 | (∼ 1/n) | at τ = |     |        |     |     |     |     |     |     |
| -------- | ---- | ---------- | --- | --- | ------- | ------- | ------ | --- | ------ | --- | --- | --- | --- | --- | --- |
|          |      |            |     |     |         |         |        |     | Pr(|Jˆ |     |     |     | 3   |     |     |
0.5. High thresholds correspond to [0.5,1.0]. It that range SS −J|≤(cid:15)J)≥1− .
n
| α = P(T|H) |           | is consistently |     | higher  | than 0.04  | which   | is well  |                 |     |          |            |     |        |          |      |
| ---------- | --------- | --------------- | --- | ------- | ---------- | ------- | -------- | --------------- | --- | -------- | ---------- | --- | ------ | -------- | ---- |
|            |           |                 |     |         |            |         |          | We demonstrate  |     | that our | guarantees |     | indeed | hold and | thus |
| over the   | assumed   | value           | of  | α which | is 0.00046 | (∼      | logn/n)  |                 |     |          |            |     |        |          |      |
|            |           |                 |     |         |            |         |          | LSH-SS provides |     | reliable | estimates  | at  | both   | high and | low  |
| for the    | data set. | β =P(T|L)       |     | is also | below      | or very | close to |                 |     |          |            |     |        |          |      |
thresholdswithreal-worlddatasetsinthefollowingsection.
| thecalculated0.00003intherange. |          |     |      |       | Table2inAppendixC |       |            |     |     |     |     |     |     |     |     |
| ------------------------------- | -------- | --- | ---- | ----- | ----------------- | ----- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| shows more                      | examples |     | of α | and β | values in         | other | data sets, |     |     |     |     |     |     |     |     |
6. EXPERIMENTALEVALUATION
| which again | satisfy   | our     | assumptions. |      |        |       |        |     |     |     |     |     |     |     |     |
| ----------- | --------- | ------- | ------------ | ---- | ------ | ----- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
| The         | following | theorem | states       | that | LSH-SS | gives | a good |     |     |     |     |     |     |     |     |
6.1 SetUp
| estimate | at high | thresholds. |              | See Appendix |              | A.2 for | a proof.  |            |     |                |     |             |     |       |       |
| -------- | ------- | ----------- | ------------ | ------------ | ------------ | ------- | --------- | ---------- | --- | -------------- | --- | ----------- | --- | ----- | ----- |
|          |         |             |              |              |              |         |           | Data sets: | We  | have conducted |     | experiments |     | using | three |
| Theorem  |         | 1. Let      | 0 < (cid:15) | < 1 be       | an arbitrary |         | constant. |            |     |                |     |             |     |       |       |
Assume α ≥ logn/n and β < 1/n. Then for sufficiently data sets. The DBLP data set consists of about 800K vec-
large n with c=1/(loge·(cid:15)2), m =cn and m =cn, tors. The NYT data set is NYTimes news articles and
|     |     |     |     | H   |     | L   |     |             |       |               |     |     |        |      |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ----- | ------------- | --- | --- | ------ | ---- | --- |
|     |     |     |     |     |     |     |     | consists of | about | 150K vectors. |     | The | PUBMED | data | set |
2
Pr(|Jˆ −J|≤(1+(cid:15))J)≥1− . is PubMed abstracts and consists of 400K vectors. We give
SS
|     |     |     |     |     |     | n   |     | detaileddatasetdescriptionsinAppendixC.1. |     |     |     |     |     | Weonlyre- |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------------- | --- | --- | --- | --- | --- | --------- | --- |
Theterm1intheerrorboundisfromtheconservativena- port results of the DBLP and NYT data set; results on the
ture of the SampleL procedure of not scaling up the result PUBMED data set is in Appendix C.4.
when the accuracy is not guaranteed. However, since the Algorithms compared: We implemented the following
majority of true pairs are in S at high thresholds, its im- algorithms for the VSJ problem.
H
| pact is | rather       | insignificant. |         | For overestimations, |     | the        | bound  |           |        |         |           |           |     |         |      |
| ------- | ------------ | -------------- | ------- | -------------------- | --- | ---------- | ------ | --------- | ------ | ------- | --------- | --------- | --- | ------- | ---- |
|         |              |                |         |                      |     |            |        | • LC(ξ)   | is the | Lattice | Counting  | algorithm |     | in [14] | with |
| is very | conservative |                | and our | experiments          |     | in Section | 6 show |           |        |         |           |           |     |         |      |
|         |              |                |         |                      |     |            |        | a minimum |        | support | threshold | ξ.        |     |         |      |
muchbetterresultsthanthetheoreticalguaranteesinThe-
orem 1. For underestimations, the error bound in Theo- • LSH-S istheLSHindexbasedalgorithminSection4.
rem 1 is not meaningful because underestimation is capped • LSH-SS is the LSH index based stratified sampling
by −100%. The following theorem, which is based on the algorithm in Section 5. We used m 1 = n, δ = logn,
dampenedscale-upfactor,hastheadvantageofprovidinga m =n and k =20 unless specified otherwise. LSH-
2
meaningful bound for underestimations as well. SS(D) is LSH-SS with a dampened scale-up factor.
In the approach using a dampened scale-up constant 0< Weusedc =n /δ. SeeAppendixC.3foradiscussion
s L
c ≤ 1, we multiply the full scale-up factor by c . The fol- on alternative choices.
| s   |     |     |     |     |     | s   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
lowing theorem quantifies the effect of using the dampened • We consider two random sampling methods: RS(pop)
scale-up factor. See Appendix A.3 for a proof. andRS(cross). InRS(pop),wesamplepairsfromthe
|           |              |                                            |     |        |         |            |     | crossproduct. |            | RS(cross)iscrosssampling[10],where |              |       |          |            |       |
| --------- | ------------ | ------------------------------------------ | --- | ------ | ------- | ---------- | --- | ------------- | ---------- | ---------------------------------- | ------------ | ----- | -------- | ---------- | ----- |
| Theorem   |              | 2. Foraconstant0<(cid:15)<1,usingadampened |     |        |         |            |     |               |            | √                                  |              |       |          |            |       |
|           |              |                                            |     |        |         |            |     | we sample     |            | (cid:100) m (cid:101)              | records      | and   | compare  | all the    | pairs |
| scale-up  | factor       | of 0                                       | < c | ≤ 1 at | line 10 | of SampleL | in  |               |            | R                                  |              |       |          |            |       |
|           |              |                                            | s   |        |         |            |     | in the        | sample.    | m                                  | = d·n        | where | d is     | a constant | to    |
| Algorithm | 1 guarantees |                                            |     |        |         |            |     |               |            | R                                  |              |       |          |            |       |
|           |              |                                            |     |        |         |            |     | compare       | algorithms |                                    | with roughly |       | the same | runtime.   |       |
1−β
|     | Pr(|Jˆ | −J  | |≥(cid:15)(cid:48)J | )≤(cid:15)−2· |     | .   |     |            |         |     |        |         |          |       |     |
| --- | ------ | --- | ------------------- | ------------- | --- | --- | --- | ---------- | ------- | --- | ------ | ------- | -------- | ----- | --- |
|     |        | L   | L                   | L             |     |     |     | Evaluation | metric: |     | We use | average | relative | error | to  |
m L β
|     |     |     |     |     |     |     |     | show the accuracy. |     | A relative | error | is  | defined | as est | size / |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | ---------- | ----- | --- | ------- | ------ | ------ |
Jˆ>J,
where (cid:15)(cid:48) =1−(1−(cid:15))c . When i.e. overestimation, true size. We show errors of overestimations and underes-
s
we have a tighter bound (cid:15)(cid:48) =c (1+(cid:15))−1. timations separately to clearly depict the characteristics of
s
343

|                              |       | LSH-SS    |     | RS(pop)   |     |     |                              |      | LSH-SS    |     | RS(pop)   |     |     |
| ---------------------------- | ----- | --------- | --- | --------- | --- | --- | ---------------------------- | ---- | --------- | --- | --------- | --- | --- |
|                              |       | LSH-SS(D) |     | RS(cross) |     |     |                              |      | LSH-SS(D) |     | RS(cross) |     |     |
| .tserevO ,)%( rorrE evitaleR |       |           |     |           |     |     | .tserevO ,)%( rorrE evitaleR |      |           |     |           |     |     |
|                              |  1000 |           |     |           |     |     |                              |  300 |           |     |           |     |     |
|                              |  800  |           |     |           |     |     |                              |  250 |           |     |           |     |     |
 200
 600
 150
 400
 100
|     |  200 |     |     |     |     |     |     |  50 |     |     |     |     |     |
| --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |  0   |     |     |     |     |     |     |  0  |     |     |     |     |     |
0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1
|                               |      |          | Similarity Threshold τ |            |     |     |                               |      |          | Similarity Threshold τ |            |     |     |
| ----------------------------- | ---- | -------- | ---------------------- | ---------- | --- | --- | ----------------------------- | ---- | -------- | ---------------------- | ---------- | --- | --- |
|                               | (a)  | Relative | error                  | (Overest.) |     |     |                               | (a)  | Relative | error                  | (Overest.) |     |     |
|                               | -100 |          |                        |            |     |     |                               | -100 |          |                        |            |     |     |
| .tserednU ,)%( rorrE evitaleR |      |          |                        |            |     |     | .tserednU ,)%( rorrE evitaleR |      |          |                        |            |     |     |
|                               | -80  |          |                        |            |     |     |                               | -80  |          |                        |            |     |     |
|                               | -60  |          |                        |            |     |     |                               | -60  |          |                        |            |     |     |
|                               | -40  |          |                        |            |     |     |                               | -40  |          |                        |            |     |     |
|                               | -20  |          |                        |            |     |     |                               | -20  |          |                        |            |     |     |
 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1  0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1
|     |     |     | Similarity Threshold τ |     |     |     |     |     |     | Similarity Threshold τ |     |     |     |
| --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- |
(b) Relative error (Underest.) (b) Relative error (Underest.)
|     |  1e+09 |     |     |     |     |     |     |  1e+06 |     |     |     |     |     |
| --- | ------ | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- |
 1e+08
|       |  1e+07 |     |     |     |     |     |       |  100000 |     |     |     |     |     |
| ----- | ------ | --- | --- | --- | --- | --- | ----- | ------- | --- | --- | --- | --- | --- |
|       |  1e+06 |     |     |     |     |     |       |  10000  |     |     |     |     |     |
| σ DTS |        |     |     |     |     |     | σ DTS |         |     |     |     |     |     |
 100000
|     |  10000 |     |     |     |     |     |     |  1000 |     |     |     |     |     |
| --- | ------ | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
|     |  1000  |     |     |     |     |     |     |  100  |     |     |     |     |     |
 100
|     |  10 |     |     |     |     |     |     |  10 |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1
|     |     |     | Similarity Threshold τ |     |     |     |     |     |     | Similarity Threshold τ |     |     |     |
| --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- |
|     |     |     | (c) Variance           |     |     |     |     |     |     | (c) Variance           |     |     |     |
Figure 2: Accuracy/Variance on DBLP Figure 3: Accuracy/Variance on NYT
|                  |       |            |              |            |             |           | τ           | 0.1  |        | 0.3     | 0.5 | 0.7       | 0.9       |
| ---------------- | ----- | ---------- | ------------ | ---------- | ----------- | --------- | ----------- | ---- | ------ | ------- | --- | --------- | --------- |
|                  |       |            |              |            |             |           | J           | 105B | 267M   |         | 11M | 103K      | 42K       |
| each algorithm.  |       | To measure | reliability, | we         | report      | the stan- |             |      |        |         |     |           |           |
|                  |       |            |              |            |             |           | selectivity | 33%  | 0.085% | 0.0036% |     | 0.000064% | 0.000013% |
| dard deviation   | (STD) | of         | estimates.   | We report  | figures     | over      |             |      |        |         |     |           |           |
| 100 experiments. |       | For        | efficiency,  | we measure | the         | runtime,  |             |      |        |         |     |           |           |
| which is time    | taken | for        | estimation.  | For all    | algorithms, | we        |             |      |        |         |     |           |           |
only42,000truepairs,andtheselectivityisonly0.00001%.
loadednecessarydatastructures(dataorindex)inmemory.
YetLSH-SSisabletoestimatethejoinsizequiteaccurately
| We implemented |     | all | the algorithms | in  | Java. We | ran all |                                   |     |     |     |                    |     |     |
| -------------- | --- | --- | -------------- | --- | -------- | ------- | --------------------------------- | --- | --- | --- | ------------------ | --- | --- |
|                |     |     |                |     |          |         | andreliablyexploitingtheLSHindex. |     |     |     | Moreover,inFigure2 |     |     |
our experiments on a server running 64 GNU/Linux 2.6.27 (c), LSH-SS shows very small variance at high thresholds.
over2.93GHzIntelXeonCPUswith64GBofmainmemory. RS(pop)andRS(cross)areasaccurateasLSH-SSatlow
|     |     |     |     |     |     |     | thresholds. | However | as  | the threshold | increases, |     | their errors |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ------- | --- | ------------- | ---------- | --- | ------------ |
6.2 Accuracy,VarianceandEfficiency
|     |     |     |     |     |     |     | rapidly increase; |     | their | estimations | fluctuate |     | between huge |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | ----- | ----------- | --------- | --- | ------------ |
DBLP: We first report the results on the accuracy, vari- overestimation and extreme underestimation (i.e. −100%)
ance and runtime using the DBLP data set. Figure 2(a) in Figure 2(a) and (b). As a consequence, their variance is
(resp. Figure 2(b)) shows relative errors of overestimations quite large in Figure 2(c).
(resp. underestimations)overthesimilaritythresholdrange. LSH-S and LC show consistently outperformed by oth-
Figure 2(c) shows the variance of the estimates. ers, and we omit their results. LSH-S has large errors at
LSH-SSdeliversaccurateestimationsoverthewholethresh- high thresholds, e.g. τ ≥ 0.6. This is because the esti-
oldrange. InFigure2(a),weseethatLSH-SS hardlyover- mations of conditional probabilities are not reliable due to
estimates, which is expected from the discussions in Sec- insufficient number of true pairs sampled. LC underesti-
tion 5.2. LSH-SS(D) occasionally overestimates, but its matesoverthewholethresholdrange. Wehypothesizethat
error is smaller than 30%. Figure 2(b) shows the underes- itisbecauseofthecharacteristicofthebinaryLSHfunction
timation tendency of LSH-SS, but it is much less severe for cosine similarity. Intuitively the binary LSH functions
than those of RS(pop) and RS(cross). We observe that need more hash functions (larger k) to distinguish objects,
LSH-SS(D) shows smaller underestimations. which has negative impact on the runtime. It appears that
The following table shows the actual join size J and its LC is not adequate for binary LSH functions.
selectivity at various similarity threshold τ. For runtime, LSH-SS and LSH-SS(D) took less than
Note the dramatic differences in the join size depending 750 msec and RS(pop) and RS(cross) took about 780 sec
onτ. Atτ =0.1therearemorethan100billiontruepairs, ontheaverage. TheruntimeofLSH-S was1028msec,and
and its selectivity is about 30 %. But at τ = 0.9 there are that of LC was about 3 sec.
344

150
100
50
0
-50
-100
10 20 30 40 50
5.0=τ
,)%(
rorrE
evitaleR
LSH-SS LSH-S
Number of hash functions k
(a) Accuracy, τ =0.5
500
400
300
200
100
0
-100
10 20 30 40 50
8.0=τ
,)%(
rorrE
evitaleR
7. CONCLUSION
We propose size estimation techniques for vector similar-
ityjoins. TheproposedmethodsrelyontheubiquitousLSH
indexing and enable reliable estimates even at high similar-
itythresholds. WeshowthatLSH-SS givesgoodestimates
throughout the threshold range with probabilistic guaran-
tees. The proposed techniques only need minimal addition
to the existing LSH index and can be easily applied.
8. REFERENCES
[1] N. Alon, P. B. Gibbons, Y. Matias, and M. Szegedy.
Tracking join and self-join sizes in limited storage. In
LSH-SS LSH-S
Proc. SIGMOD, pages 10–20, 1999.
[2] A. Arasu, V. Ganti, and R. Kaushik. Efficient Exact
Set-Similarity Joins. In Proc. VLDB, pages 918–929,
2006.
[3] R. J. Bayardo, Y. Ma, and R. Srikant. Scaling up all
pairs similarity search. In Proc. WWW, pages
131–140, 2007.
[4] A. Z. Broder. On the Resemblance and Containment
Number of hash functions k of Documents. In Proc. SEQUENCES, pages 21–29,
(b) Accuracy, τ =0.8
1997.
Figure 4: Impact of k on DBLP [5] M. S. Charikar. Similarity Estimation Techniques
from Rounding Algorithms. In Proc. STOC, pages
NYT:Figure3showsrelativeerrorsandvarianceonthe 380–388, 2002.
NYTdataset. LSH-SSgivesgoodestimatesathighthresh- [6] S. Chaudhuri, V. Ganti, and R. Kaushik. A Primitive
olds. It shows underestimation at τ ≤0.5. In general, how- Operator for Similarity Joins in Data Cleaning. In
ever, this is not the most interesting similarity range and Proc. ICDE, pages 5–16, 2006.
thisisprobablynotaseriousflaw. Theproblemcanbead- [7] S. Chaudhuri, R. Motwani, and V. Narasayya. On
dressed either by using a bigger dampened scale-up factor Random Sampling over Joins. In Proc. SIGMOD,
c or increasing the sample size. We see that LSH-SS(D) 1999.
s
has smaller underestimation problems. Again, we observe [8] W. G. Cochran. Sampling Techniques. John Wiley &
thatestimationsofRS(pop)andRS(cross)fluctuateathigh Sons, 1977.
thresholds. Their variance is larger than the variance of [9] S. Ganguly, P. B. Gibbons, Y. Matias, and
LSH-SS or LSH-SS(D) throughout the threshold range. A. Silberschatz. Bifocal sampling for skew-resistant
For runtime, LSH-SS took 1091 msec and RS took 920 join size estimation. In Proc. SIGMOD, pages
msec on the average. 271–281, 1996.
6.3 ImpactofParameters [10] P. J. Haas, J. F. Naughton, S. Seshadri, and A. N.
Swami. Fixed-Precision Estimation of Join Selectivity.
We assume a pre-built LSH index with parameters opti-
In Proc. PODS, pages 190–201, 1993.
mized for its similarity search. The relevant parameter for
[11] M. Hadjieleftheriou, X. Yu, N. Koudas, and
our estimation purposes is k which specifies the number of
D. Srivastava. Hashed Samples: Selectivity Estimators
hash functions used for an LSH table. We analyze the im-
For Set Similarity Selection Queries. In Proc. VLDB,
pact of k on accuracy and variance.
pages 201–212, 2008.
Figure4showsaccuracyatτ =0.5,0.8. Theconclusionis
[12] P. Indyk and R. Motwani. Approximate Nearest
the same at other thresholds. We observe that LSH-SS is
Neighbors: Towards Removing the Curse of
not much affected by k. This is because an LSH table pro-
Dimensionality. In Proc. STOC, pages 604–613, 1998.
videssufficientdistinguishingpowerwithrelativelysmallk.
[13] Y. E. Ioannidis and S. Christodoulakis. On the
LSH-SS willworkwithanyreasonablechoiceofk. LSH-S
Propagation of Errors in the Size of Join Results. In
ishighlysensitivetokforthereasonspecifiedinSection6.2.
Proc. SIGMOD, pages 268–277, 1991.
The same observation is made in variance as well.
[14] H. Lee, R. T. Ng, and K. Shim. Power-Law Based
k=10 k=20 k=30 k=40 k=50 Estimation of Set Similarity Join Size. In Proceedings
size(MB) 3.2 7.5 12.6 14.1 16.5 of the VLDB Endowment, pages 658–669, 2009.
[15] R. Lipton, J. F. Naughton, and D. A. Schneider.
The above table shows space occupied by an LSH table Practical selectivity estimation through adaptive
on the DBLP data set ignoring implementation-dependent sampling. In Proc. SIGMOD, pages 1–11, 1990.
overheads. When k=20, there are about 480K non-empty
[16] R. Motwani and P. Raghavan. Randomized
buckets which add 7.5M of space for the g function values,
Algorithms. Cambridge University Press, 1995.
bucket counts, and vector ids. The DBLP binary is 50M.
[17] S. Sarawagi and A. Kirpal. Efficient set joins on
Ifwearegiventhefreedomofchoosingk,weobservethat
similarity predicates. In Proc. SIGMOD, pages
slightly smaller k values, say between 5 and 15, generally
743–754, 2004.
givebetteraccuracy. SeeAppendixB.1formorediscussions.
345

APPENDIX E(X)=J ·mH. Thus, NH ·E(X)= NH ·m · JH =J .
H NH mH mH H NH H
Therefore,
A. PROOFS
N 1
Pr(| H ·X−J |>(cid:15)J )≤ .
A.1 Equation(4) m H H n
H
Sincef(s)=sk,thefourareasdefinedinFigure1canbe Jˆ =X·N /m inSampleH ofAlgorithm1. Pluggingin
H H H
calculated as follows: Jˆ in the above inequality completes the proof.
H
(cid:90) τ τk+1
P[H∩F] = f(s)ds= Second,thefollowinglemmastatesthatSampleLreturns
0 k+1 a safe lower bound with high probability.
P[H∩T] = (cid:90) 1 f(s)ds= 1−τk+1 Lemma 2. Assume β < 1/n. Then for sufficiently large
τ k+1 n, an arbitrary constant c(cid:48) and m L =c(cid:48)n, we have
(cid:90) τ τk+1
1
P[L∩F] = 1−f(s)ds=τ − Pr(Jˆ ≤c(cid:48))≥1− .
0 k+1 L n
(cid:90) 1 1−τk+1 Proof. Let Y be a random variable denoting the num-
P[L∩T] = 1−f(s)ds=1−τ − .
k+1 ber of pairs in the samples satisfying τ in SampleL of Al-
τ
gorithm 1. We show that Y is not likely to be bigger than
UsingtheaboveprobabilitiesinEquation(2)and(3)gives, δ=logn. Y isabinomialrandomvariablewithparameters
(m ,β).
P(H|T) = 1 (cid:90) 1 f(s)ds= (cid:80)k i=0 τi (8) For L anarbitraryconstant(cid:15)(cid:48) ≥2e−1,byChernoffbounds[16]
1−τ k+1
1(cid:90) τ
τ
τk Pr(Y
>(1+(cid:15)(cid:48))E(Y))≤2−E(Y)(1+(cid:15)(cid:48)).
P(H|F) = f(s)ds= . (9)
τ k+1 Therefore, the probability that the loop of SampleL termi-
0
nates by acquiring enough number of true pairs (δ =logn)
WehavethefollowingestimatorJˆ U byusingaboveP(H|T) is as follows:
and P(H|F) in Equation (1): 1
Pr(Y >δ=logn)≤2−logn = .
N −M ·Pˆ(H|F) n
Jˆ U = Pˆ( H H|T)−Pˆ(H|F) Since m L =c(cid:48)n and β <1/n,
N −M · τk E(Y)<c(cid:48).
= H k+1
(cid:80)k i=0 τi − τk If Y ≤δ, SampleL of Algorithm 1 returns Jˆ L =Y without
k+1 k+1 scaling it up. Therefore,
(k+1)N −M ·τk
= (cid:80)k i H = − 0 1τi . Pr(Jˆ L =E(Y)<c(cid:48))≥1− n 1 .
A.2 ProofofTheorem1
We analyze the behavior of SampleH and SampleL in Finally,weproveTheorem1usingLemma1andLemma2.
Algorithm 1 separately by the two lemmas below. We then For sufficiently large n, c(cid:48) ≤J L . Thus from Lemma 2,
combine the two results using Equation (7). 1
First, thefollowinglemmashowsthatSampleH inAlgo- Pr(|Jˆ L −J L |≤J L )≥1− n .
rithm 1 gives a reliable estimate at high thresholds.
Since Jˆ = Jˆ +Jˆ and J = J +H , combining the
SS H L H L
Lemma 1. Let 0 < (cid:15) < 1 be an arbitrary constant. As- above inequality with Lemma 1 proves the theorem.
sumeα≥logn/n. Thenwithc=4/(loge·(cid:15)2)andm =cn,
H
we have A.3 ProofofTheorem2
1
Pr(|Jˆ −J |≤(cid:15)J )≥1− . Let X be a random variable for the number of true pairs
H H H n
in the sample, i.e. n , in SampleL of Algorithm 1. X
L
Proof. Let X be a random variable denoting the num- follows a binomial distribution B(m ,β), and µ = m β
L X L
ber of pairs in the sample that satisfy τ in SampleH of and σ = (cid:112) m β(1−β). Suppose 0 < c ≤ 1 is used as a
X L s
Algorithm 1. Then X is a binomial random variable with dampeningfactor. Letsbethesamplingratio,s=m /N ,
L L
parameters (m H ,α) [16]. Since m H =cn and α≥logn/n, and Y be the estimate using c s . Y = c s /s·X, and µ Y =
(cid:112)
c /s·m β =c N β =c J andσ =c /s· m β(1−β).
E(X)≥clogn. s L s L s L Y s L
Applying Chebyshev’s inequality [16], for any k∈R+,
Foranarbitraryconstant0<(cid:15)<1,byChernoffbounds[16] 1
Pr(|Y −µ |≥k·σ )≤ .
Pr(|X−E(X)|>(cid:15)E(X))≤e−clog
4
n(cid:15)2
. (cid:112)
Y Y k2
(cid:112)
σ /µ = (1−β)/m β. Letting (cid:15) = k (1−β)/m β
Y Y L L
Letting c=4/(loge·(cid:15)2) gives gives
(cid:18) (cid:19)
Pr(|X−E(X)|>(cid:15)E(X))≤ 1 . Pr |Y −µ Y | ≥(cid:15) ≤(cid:15)−2· 1−β .
n µ Y m L β
346

The lower bound of the estimation is J −(1−(cid:15))µ . In probability. Since decreasing k increases P(H|T) and J ,
|     |     |     |     |     | L   |     | Y   |     |     |     |     |     |     | H   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
overestimation,c (1+(cid:15))J ≥J sinceotherwiseitwouldbe this means that we can decrease k as long as P(T|H) is
|     |     | s   | L L |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
underestimation. Thus, the upper bound of the estimation not too small. Decreasing k also reduces the LSH function
is(c s (1+(cid:15))−1)J L becausec s ≤1,1−(1−(cid:15))c s ≥c s (1+(cid:15))−1. computationtime. Withthisintuition,wecanformalizethe
(cid:15)(cid:48)
Letting =1−(1−(cid:15))c s proves the theorem. problem of choosing k as follows:
A.4 ProofofTheorem3 Definition 4 (The Optimal-k Problem). Givenade-
|                                |        |               |              |          |              |          |      | sired error            | bound (cid:15) >    | 0 and   | the bound    | on        | the probabilistic |           |
| ------------------------------ | ------ | ------------- | ------------ | -------- | ------------ | -------- | ---- | ---------------------- | ------------------- | ------- | ------------ | --------- | ----------------- | --------- |
| Aswehavethesameconditionsonα,m |        |               |              |          | ,andc,Lemma1 |          |      |                        |                     |         |              |           |                   |           |
|                                |        |               |              |          | H            |          |      | guarantee              | p, find the         | minimum | k            | such that | P(T|H)            | ≥ ρ,      |
| still holds                    | in the | low threshold | range        | as       | well.        | However, | due  |                        |                     |         |              |           |                   |           |
|                                |        |               |              |          |              |          |      | where ρ=ρ((cid:15),p). |                     |         |              |           |                   |           |
| to the increased               |        | β, a          | different    | analysis | needs        | to be    | done |                        |                     |         |              |           |                   |           |
| for SampleL                    | (Lemma |               | 2). We first | show     | that         | SampleL  | re-  |                        |                     |         |              |           |                   |           |
|                                |        |               |              |          |              |          |      | If can we              | assume a similarity |         | distribution |           | of the            | database, |
turnsascaled-upestimatenotasafelowerboundwithhigh
|                       |     |                     |                           |             |           |            |     | wecananalyticallyfindtheoptimalk. |                        |         |        | However,P(T|H)is |     |           |
| --------------------- | --- | ------------------- | ------------------------- | ----------- | --------- | ---------- | --- | --------------------------------- | ---------------------- | ------- | ------ | ---------------- | --- | --------- |
| probability,          | and | then                | show that                 | the         | scaled-up | estimate   | is  |                                   |                        |         |        |                  |     |           |
|                       |     |                     |                           |             |           |            |     | dependent                         | on data and            | the LSH | scheme | used,            | and | so is the |
| reliable.             |     |                     |                           |             |           |            |     | optimal                           | value of k.            |         |        |                  |     |           |
| SimilarlyasinLemma2,Y |     |                     | isabinomialrandomvariable |             |           |            |     |                                   |                        |         |        |                  |     |           |
|                       |     |                     |                           | =c(cid:48)n |           |            |     | B.2 Extensions                    |                        |         |        |                  |     |           |
| with parameters       |     | (m L ,β).           | Since                     | m L         | and       | β ≥logn/n, |     |                                   |                        |         |        |                  |     |           |
|                       |     | E(Y)≥c(cid:48)logn. |                           |             |           |            |     | B.2.1                             | UsingMultipleLSHTables |         |        |                  |     |           |
Fromthegivencondition,c(cid:48) ≥2/(loge·(cid:15)2)andc(cid:48) ≥1/(1− TheproposedalgorithmssofarassumeonlyasingleLSH
(cid:15)). Since (1−(cid:15))E(Y) ≥ (1−(cid:15))c(cid:48)logn ≥ logn = δ, by table, but a typical LSH index consists of multiple LSH ta-
|     |     |     |     |     |     |     |     | bles. In | this section, | we describe | how | we  | can utilize | more |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------------- | ----------- | --- | --- | ----------- | ---- |
Chernoff bounds,
|     |     |     |     |     |     |     |     | than one | LSH tables for | the | estimation | purposes. |     | We con- |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | -------------- | --- | ---------- | --------- | --- | ------- |
1
Pr(Y ≥δ)≥1− . sider two estimation algorithms using multiple LSH tables:
n
|     |     |     |     |     |     |     |     | median | estimator and | virtual | bucket | estimator. |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------------- | ------- | ------ | ---------- | --- | --- |
This means that the while-loop (line 2) of SampleL Al- Medianestimator. ThemedianestimatorappliesLSH-
gorithm 1 terminates by reaching the desired answer size SStoeachLSHtableindependentlywithoutmodifyingLSH-
threshold δ with high probability. Then SampleL returns SS and merges the estimates. Suppose an LSH index I =
| Jˆ  |     |     |     |     |     |     |     |     |     |     |     |     |     | G   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
= Y ·J /m . Moreover, since c(cid:48) ≥ 4/(loge·(cid:15)2), by {D ,...,D } with (cid:96) tables. From each table D ,1≤i≤
| L   | L   | L   |     |     |     |     |     | g1  | g(cid:96) |     |     |     |     | gi  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- |
Chernoff bounds, (cid:96), we generate an estimate Jˆ with a sample of n pairs. Its
i
|     |       |                       |     |     |     |     |     |               | Jˆ                |               |        |            | Jˆ               |          |
| --- | ----- | --------------------- | --- | --- | --- | --- | --- | ------------- | ----------------- | ------------- | ------ | ---------- | ---------------- | -------- |
|     |       |                       |     |     | 2   |     |     | estimate,     | m , is the median |               | of the | estimates, | i ,1≤i≤(cid:96). |          |
|     | Pr(|Y | −E(Y)|≥(cid:15)E(Y))≤ |     |     | .   |     |     |               |                   |               |        |            |                  |          |
|     |       |                       |     |     | n   |     |     | This approach | makes             | the algorithm |        | more       | reliable         | reducing |
theprobabilitythatJˆ
|            |     |        |                |      |     |     |     |                                                        | m   | deviatesmuchfromJ. |     |                | FromTheo- |        |
| ---------- | --- | ------ | -------------- | ---- | --- | --- | --- | ------------------------------------------------------ | --- | ------------------ | --- | -------------- | --------- | ------ |
| Therefore, |     |        |                |      |     |     |     |                                                        |     | abilitythatJˆ      |     |                |           |        |
|            |     |        |                |      |     |     |     | rems1and3,theprob                                      |     |                    |     | i differsfromJ |           | bymore |
|            |     |        |                |      | 2   |     |     | thanafactorof1+(cid:15)islessthan2/nwiththeassumedjoin |     |                    |     |                |           |        |
|            |     | Pr(|Jˆ | −J |≤(cid:15)J | )≥1− | .   |     |     |                                                        |     |                    |     |                |           |        |
L L L n size and sample size. When taking the median, the proba-
bilitythatmorethan(cid:96)/2Jˆ’sdeviatebymorethan(1+(cid:15))J
| SinceJˆ | =Jˆ | +Jˆ andJ | =J  | +H  | ,theaboveinequality |     |     |     |     | i   |     |     |     |     |
| ------- | --- | -------- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
SS H L H L is at most 2−(cid:96)/2 by the standard estimate of Chernoff [16].
| along with | Lemma | 1 completes |     | the proof. |     |     |     |     |     |     |     |     |     |     |
| ---------- | ----- | ----------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Jˆ
|     |     |     |     |     |     |     |     | This states        | that m is | within | the same   | factor | of       | error with |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --------- | ------ | ---------- | ------ | -------- | ---------- |
|     |     |     |     |     |     |     |     | higher probability | than      | the    | guarantees | in     | Theorems | 1 and      |
B. ADDITIONALDISCUSSION
|     |     |     |     |     |     |     |     | 3. Theeffectivesamplesizeincreasesbyafactorof(cid:96). |     |     |     |     |     | When |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------------ | --- | --- | --- | --- | --- | ---- |
asamplesizethatisgreaterthannisaffordable,exploiting
| B.1 TheOptimal-k |     |     | forTheVSJProblem |     |     |     |     |          |                |      |     |          |      |           |
| ---------------- | --- | --- | ---------------- | --- | --- | --- | --- | -------- | -------------- | ---- | --- | -------- | ---- | --------- |
|                  |     |     |                  |     |     |     |     | multiple | LSH tables can | make | the | estimate | more | reliable. |
RecallthatkisthenumberofLSHfunctionsforg. Ideally, However, dividing a total sample size of n into multiple es-
we want high P(T|H) and P(H|T) because the estimate timates can impair the accuracy of individual estimates.
from S is more reliable and having more true pairs in S Virtual bucket estimator. We consider virtual buck-
| H   |     |     |     |     |     |     | H   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
reduces the dependency on S . P(T|H) (resp. P(H|T)) is etsformedbymultipleLSHtables. Apair(u,v)isregarded
L
| analogoustoprecision(resp. |     |     | recall)ininformationretrieval. |     |     |     |     |           |             |          |       |        |      |           |
| -------------------------- | --- | --- | ------------------------------ | --- | --- | --- | --- | --------- | ----------- | -------- | ----- | ------ | ---- | --------- |
|                            |     |     |                                |     |     |     |     | as in the | same bucket | if u and | v are | in the | same | bucket in |
We note that k value has the following trade-offs between any of (cid:96) LSH tables. This can improve the accuracy when
P(T|H) and P(H|T). an existing LSH scheme has a relatively large k than nec-
• A larger k increases P(T|H) but decreases P(H|T). essary. Recall from the discussions in the previous section
|       |                |        |              |              |          |          |         | thatwhenk      | istoolarge,g          | becomesoverlyselectiveandS |             |     |            |         |
| ----- | -------------- | ------ | ------------ | ------------ | -------- | -------- | ------- | -------------- | --------------------- | -------------------------- | ----------- | --- | ---------- | ------- |
| With  | a sufficiently |        | large k,     | only exactly |          | the same | vec-    |                |                       |                            |             |     |            | H       |
|       |                |        |              |              |          |          |         | canbetoosmall. | ThenthetruepairsfromS |                            |             |     | canbeonlya |         |
| tors  | will be        | in the | same bucket. |              | P(T|H)   | = 1      | in this |                |                       |                            |             |     | H          |         |
|       |                |        |              |              |          |          |         | small portion  | of the true           | pairs.                     | Considering |     | virtual    | buckets |
| case. | However,       | only   | a very       | small        | fraction | of true  | pairs   |                |                       |                            |             |     |            |         |
canaddressthisproblembyrelaxingthebucketconditions;
isinthesamebucketresultinginaverysmallP(H|T).
|     |     |     |     |     |     |     |     | B(u)=B(v)ifandonlyifthereexistaD |     |     |     |     | suchthatuand |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | --- | --- | ------------ | --- |
gi
• A smaller k decreases P(T|H) but increases P(H|T). vbelongtothesamebucketB ∈D . Withvirtualbuckets,
gi
In an extreme case of k = 0, S H consists of all the when we check B(u) = B(v) (or (cid:54)=) for (u,v), we need to
| pairs  | of vectors | in   | V, and thus | P(H|T)=1.  |      | However, |       |                                |                        |       |       |                   |     |          |
| ------ | ---------- | ---- | ----------- | ---------- | ---- | -------- | ----- | ------------------------------ | ---------------------- | ----- | ----- | ----------------- | --- | -------- |
|        |            |      |             |            |      |          |       | check up                       | to (cid:96) tables. At | lines | 3 and | 4 of SampleH      |     | in Algo- |
| P(T|H) | =          | P(T) | and the     | LSH scheme | does | not      | offer |                                |                        |       |       |                   |     |          |
|        |            |      |             |            |      |          |       | rithm1,apair(u,v)ischosenfromV |                        |       |       | uniformlyatrandom |     |          |
any benefit.
|     |     |     |     |     |     |     |     | and is discarded | if u | and v | are not | in the | same | bucket in |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | ---- | ----- | ------- | ------ | ---- | --------- |
ObservethatP(T|H)≥P(T|L)fromthepropertyofthe any D ,1≤i≤(cid:96). At line 3 of SampleL, B (u)(cid:54)=B (v) is
|     |     |     |     |     |     |     |     | gi  |     |     |     |     | i   | i   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
LSH indexing. The intuition on choosing k is that we want checked for all D and if B (u) = B (v) in any D , (u,v)
|     |     |     |     |     |     |     |     |     | gi  | i   |     | i   |     | gi  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
toincreaseJ aslongaswehavegoodestimateswithhigh is discarded. The analysis remains the same but the set of
H
347

pairs in same buckets, S H becomes effectively larger, which 3
givespotentiallybetteraccuracy. Theruntimeincreasesbe- 2.5
cause of the bucket checking in multiple LSH tables.
2
B.2.2 Non-selfJoins 1.5
1
In this section, we discuss how to extend the proposed
algorithmstohandlejoinsbetweentwocollectionsofvectors 0.5
U and V. The basic ideas remain the same but we need to 0
LSH-SS LSH-SS LSH-SS LSH-SS RS(pop)
make sure that a pair under consideration consists of one δ=0.5 log n δ=log n δ=2log n δ= n1/2 m=1.5n
vector from each collection.
Definition 5 (The General VSJ Problem). Given
two collection of real-valued vectors V = {v ,...,v }, U =
1 n1
{u ,...,u }andathresholdτ onasimilaritymeasuresim,
1 n2
estimate the number of pairs J = |{(u,v) : u ∈ U,v ∈
V,sim(u,v)≥τ}|.
SupposethatwehavetwoLSHtablesD andE thatare g g
built on U and V respectively using g = (g ,...,g ). We 1 (cid:96)
describe how we modify LSH-S and LSH-SS.
LSH-S.WemaketwochangesforLSH-S: N computa-
H
tion and sampling. In self-joins, N in Equation (1) is the
H
number of pairs in the same bucket: N =
(cid:80)ng (cid:0)bj (cid:1)
. In
H j=1 2
generaljoins,N =
(cid:80)ng
b ·c suchthatB ∈D ,C ∈E ,
H j=1 j i j g i g
b is the bucket count of B , c is the bucket count of C ,
j j i i
and g(B ) = g(C ), where g(B) denotes the g value that
j i
identifies bucket B. For B , if there does not exist a bucket
i
C ∈E suchthatg(C )=g(B ),c =0. Next,apair(u,v)
i g i j i
issampleduniformlyatrandomsuchthatu∈U andv∈V.
LSH-SS. S is the set of pairs (u,v),u∈U,v ∈V such
H
that g(u) = g(v). That is, the buckets of u and v have
the same g value: g(B ) = g(C ) where u ∈ B in D and j i j g
u∈C inE . S isthesetofpairs(u,v),u∈U,v∈V such
i g L
that g(u)(cid:54)=g(v). To sample a pair from S , we randomly
H
sampleabucketB withweight(B )=b ·c whereg(C )=
j j j i i
g(B ),B ∈ D and C ∈ E . We sample u from B and
j j g i g j
v from C uniformly at random within the buckets. The
i
resulting pair (u,v) is a uniform random sample from S .
H
Lines3and4ofSampleHinAlgorithm1needtobechanged
accordingly. TosamplefromS ,wesampleu∈U andv∈V
L
uniformly at random, and (u,v) is discarded if g(u)=g(v).
Line 3 of SampleH needs corresponding changes.
C. SUPPLEMENTARYEXPERIMENTS
C.1 DataSetDescription
TheDBLPdatasetconsistsof794,016publicationsisthe
sameasthedatasetusedin[3]. Eachvectorisconstructed
from authors and title of a publication. There are about
56,000 distinct words in total and each word is associated
with a dimension in a vector. The vector of a publication
representswhetherthecorrespondingwordispresentinthe
publication. Thus this data set is a binary vector data set.
The average number of features is 14, and the smallest is 3
andthebiggestis219. TheNYTdatasetisNYTimesnews
articles downloaded from UCI Machine Learning Reposi-
tory2 andconsistsof149,649vectors. Againeachdimension
representsawordandhasthecorrespondingTF-IDFweight.
The dimensionality is about 100k and the average number
of feature is 232. The PUBMED data set is constructed
from PubMed abstracts and is also downloaded from the
2http://archive.ics.uci.edu/ml/datasets.html
n=m
,rorrE
evitaleR
egarevA
Figure 5: Relative error varying δ (the answer size
threshold) in SampleL
5
4
3
2
1
0
LSH-SS LSH-SS LSH-SS LSH-SS RS(pop)
δ=0.5 log nδ=log n δ=2log n δ= n1/2 m=1.5n
rorrE
giB
htiw
τ #
Underestimation
Overestimation
Figure 6: The number of τ values with Jˆ/J ≥ 10
(overest.) or J/Jˆ≥10 (underest.) varying δ
UCIrepository. Itconsistsof400,151TF-IDFvectors. The
dimensionality is about 140k. It takes 4.7, 4.6, and 5.6 sec-
onds to build LSH indexes from respective in-memory raw
data.
C.2 ImpactofParameters: δ andm
Inthissection,westudytheimpactofparametersrelated
with the sample size using the DBLP data set. The goal
is to see if our analysis and choice of parameter values are
appropriate. Recall that LSH-SS and RS have the follow-
ingparameters;m isthesamplesizeinSampleH,δ isthe
H
answer size threshold in SampleL, m is the (maximum)
L
sample size in SampleL, and m is the sample size of ran-
R
dom sampling. In our analysis and experiments, we used
the following parameter values: m = m = n, δ = logn,
H L
and m = 1.5n. Since m ,m and m control the over-
R H L R
all sample size and δ specifies the answer size threshold,
we use two functions f and f to control the parameters:
1 2
m =m =f (n), m =1.5f (n) and δ =f (n). We test
H L 1 R 1 2
the following alternatives:
√
• f : n, n/logn, 0.5n, n, 2n, and nlogn 1
√
• f : 0.5logn, logn, 2logn, and n
2
We perform two types of combinations of f and f . First,
1 2
we fix f (n) = n and vary f . Next, we fix f (n) = logn
1 2 2
and vary f . For each combination we show two results:
1
the average absolute error for τ ={0.1,0.2,...,1.0} and the
numberofτ valueswithlargeerrorsamongthe10τ values.
WedefineanerrortobeabigoverestimationwhenJˆ/J ≥10
and to be a big underestimation when J/Jˆ≥10.
C.2.1 AnswerSizeThresholdδ
Figure 5 gives the average (absolute) relative error vary-
ing δ and Figure 6 gives the number of τ values that give
large errors. m(= f ) is fixed at n. δ > 2logn has a big
1
underestimationproblem. Alargeδ maypreventevenare-
liable estimate from being scaled up and result in a huge
348

n gol=δ ,rorrE evitaleR egarevA  4
|     |  3.5 |     |     |     | LSH-SS  |     |     |     |                    |  500         |     |     |     |     |
| --- | ---- | --- | --- | --- | ------- | --- | --- | --- | ------------------ | ------------ | --- | --- | --- | --- |
|     |      |     |     |     | RS(pop) |     |     |     |                    | LSH-SS       |     |     |     |     |
|     |  3   |     |     |     |         |     |     |     |                    |  400 RS(pop) |     |     |     |     |
|     |  2.5 |     |     |     |         |     |     |     | )%( rorrE evitaleR |  300         |     |     |     |     |
 2
 200
 1.5
|     |  1   |         |               |        |           |     |     |     |     |  100 |             |         |               |     |
| --- | ---- | ------- | ------------- | ------ | --------- | --- | --- | --- | --- | ---- | ----------- | ------- | ------------- | --- |
|     |  0.5 |         |               |        |           |     |     |     |     |  0   |             |         |               |     |
|     |  0   |         |               |        |           |     |     |     |     | -100 |             |         |               |     |
|     |      | sqrt(n) | n/log n       | 0.5n n | 2n nlog n |     |     |     |     |      |             |         |               |     |
|     |      |         | Sample Size m |        |           |     |     |     |     | 0.1  | 0.2 0.3 0.4 | 0.5 0.6 | 0.7 0.8 0.9 1 |     |
Similarity Threshold τ
Figure 7: Relative error varying the sample size m (a) Relative error
 1e+09
|     |  6  |     |                        |     |     |     |     |     |     |        |     |     | LSH-SS  |     |
| --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | ------- | --- |
|     |     |     | LSH-SS, Overestimation |     |     |     |     |     |     |  1e+08 |     |     | RS(pop) |     |
RS(pop), Overestimation
|     |  5                 |     | LSH-SS, Underestimation  |     |     |     |     |     |     |  1e+07 |     |     |     |     |
| --- | ------------------ | --- | ------------------------ | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- |
|     | rorrE giB htiw τ # |     | RS(pop), Underestimation |     |     |     |     |     |     |        |     |     |     |     |
|     |  4                 |     |                          |     |     |     |     |     |     |  1e+06 |     |     |     |     |
DTS  100000
 3
 10000
|     |  2  |                 |               |     |           |     |     |     |     |  1000 |                        |             |               |     |
| --- | --- | --------------- | ------------- | --- | --------- | --- | --- | --- | --- | ----- | ---------------------- | ----------- | ------------- | --- |
|     |  1  |                 |               |     |           |     |     |     |     |  100  |                        |             |               |     |
|     |  0  |                 |               |     |           |     |     |     |     |  10   |                        |             |               |     |
|     |     |                 |               |     |           |     |     |     |     |       | 0.1 0.2 0.3            | 0.4 0.5 0.6 | 0.7 0.8 0.9 1 |     |
|     |     | sqrt(n) n/log n | 0.5n          | n   | 2n nlog n |     |     |     |     |       | Similarity Threshold τ |             |               |     |
|     |     |                 | Sample Size m |     |           |     |     |     |     |       | (b) Variance           |             |               |     |
Jˆ/J
Figure 8: The number of τ with ≥10 (overest.) Figure 9: Accuracy/Variance on PUBMED
J/Jˆ≥
| or        | 10 (underest.) |     | varying |                       | the sample |     | size m. |     |     |     |      |         |        |        |
| --------- | -------------- | --- | ------- | --------------------- | ---------- | --- | ------- | --- | --- | --- | ---- | ------- | ------ | ------ |
| The total | number         |     | of τ is | 10: {0.1,0.2,...,1.0} |            |     |         |     |     |     |      |         |        |        |
|           |                |     |         |                       |            |     |         |     |     |     | NYT  |         | PUBMED |        |
|           |                |     |         |                       |            |     |         |     | τ   |     | α    | β       | α      | β      |
|           |                |     |         |                       |            |     |         |     | 0.1 |     | .710 | 1.85E-4 | .0179  | .00593 |
√
loss in contributions from S . For instance, δ = n is too 0.3 .710 3.26E-5 2.15E-4 6.37E-7
|              |        |              | L        |         |      |        |          |     | 0.5 |     | .708 | 9.93E-6 | 2.15E-4 | 1.40E-8  |
| ------------ | ------ | ------------ | -------- | ------- | ---- | ------ | -------- | --- | --- | --- | ---- | ------- | ------- | -------- |
| conservative | and    | its          | estimate | is less | than | 10% of | the true |     |     |     |      |         |         |          |
|              |        |              |          |         |      |        |          |     | 0.7 |     | .705 | 3.25E-6 | 1.72E-4 | 2.19E-9  |
| size at 4    | out of | 10 τ values. |          |         |      |        |          |     |     |     |      |         |         |          |
|              |        |              |          |         |      |        |          |     | 0.9 |     | .696 | 6.95E-7 | 1.29E-4 | 4.98E-10 |
Simple heuristics such as using different δ depending on highth. αorβ 1.8E-4 1.17E-5 6.09E-5 4.99E-6
thethresholdcanimprovetheperformance. Forinstanceus- lowth. αorβ 1.8E-4 1.8E-4 6.09E-5 6.09E-5
| ing0.1logn≤δ≤0.5lognathighthresholds,e.g. |     |     |     |     |     |     | τ ≥0.7, |     |     |     |     |     |     |     |
| ----------------------------------------- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
greatly improved the runtime without sacrificing accuracy Table 2: α and β in NYT and PUBMED
| in our experiments. |        | At    | low   | thresholds, | e.g.     | τ ≤ 0.3, | using  |          |         |            |     |           |         |             |
| ------------------- | ------ | ----- | ----- | ----------- | -------- | -------- | ------ | -------- | ------- | ---------- | --- | --------- | ------- | ----------- |
| a slightly          | bigger | value | of δ, | e.g. 2logn, | resulted | in       | better |          |         |            |     |           |         |             |
|                     |        |       |       |             |          |          |        | similar, | smaller | k improves |     | accuracy. | In such | cases, con- |
accuracyandvariancewithoutincreasingtheruntimemuch.
|     |     |     |     |     |     |     |     | structing | an  | LSH table | on-the-fly | can | be a viable | option. |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --------- | ---------- | --- | ----------- | ------- |
C.2.2 SampleSizeThresholdm
|        |         |             |     |          |          |       |         | Symbol | Description                   |     |     |     |     |     |
| ------ | ------- | ----------- | --- | -------- | -------- | ----- | ------- | ------ | ----------------------------- | --- | --- | --- | --- | --- |
| Figure | 7 gives | the average |     | absolute | relative | error | varying |        |                               |     |     |     |     |     |
|        |         |             |     |          |          |       |         | U,V    | acollectionofvectors,database |     |     |     |     |     |
the sample size and Figure 8 gives the number of τ values J joinsize
that give large errors. δ is fixed at logn. f < 0.5n causes n databasesize,|V|=n
|         |                  |      |          |                  |       | 1       |         | m   | samplesize          |     |     |     |     |     |
| ------- | ---------------- | ---- | -------- | ---------------- | ----- | ------- | ------- | --- | ------------------- | --- | --- | --- | --- | --- |
| serious | underestimations |      | in       | both algorithms. |       | With    | f =     |     |                     |     |     |     |     |     |
|         |                  |      |          |                  |       |         | 1       | u,v | vectors             |     |     |     |     |     |
| nlogn,  | LSH-SS           | does | not give | any              | large | errors, | but the |     |                     |     |     |     |     |     |
|         |                  |      |          |                  |       |         |         | τ   | similaritythreshold |     |     |     |     |     |
runtime roughly increases by logn. h anLSHfunction,e.g. h1(u)
|                        |     |     |     |     |     |     |     | k        | #LSHfunctionsforanLSHtable         |     |     |     |     |     |
| ---------------------- | --- | --- | --- | --- | --- | --- | --- | -------- | ---------------------------------- | --- | --- | --- | --- | --- |
| C.3 ImpactofParameter: |     |     |     |     | c   |     |     | (cid:96) | #LSHtablesinanLSHindex             |     |     |     |     |     |
|                        |     |     |     |     | s   |     |     | g        | g=(h1,...,hk),vectorofLSHfunctions |     |     |     |     |     |
Usingalargerdampenedscale-upfactorc s haslessunder- Dg,Eg anLSHtableusingg
|                 |     |          |      |      |          |          |         | G   | G={g1,...,g(cid:96)}                  |     |     |     |                    |                 |
| --------------- | --- | -------- | ---- | ---- | -------- | -------- | ------- | --- | ------------------------------------- | --- | --- | --- | ------------------ | --------------- |
| estimation.     | In  | the DBLP | data | set, | setting  | c s =0.5 | reduces |     |                                       |     |     |     |                    |                 |
|                 |     |          |      |      |          |          |         | IG  | anLSHindexwithusingGthatconsistsofDg1 |     |     |     |                    | ,...,Dg(cid:96) |
| underestimation |     | errors   | from | −95% | (LSH-SS) | to −65%  | at      |     |                                       |     |     |     |                    |                 |
|                 |     |          |      |      |          |          |         | B,C | abucketinanLSHtable,e.g.              |     |     |     | B(u): thebucketofu |                 |
τ = 0.6. However, it can cause overestimation problems bj,ci bucketcounts,e.g. bj isthebucketcountofbucketBj
with large variance as discussed in Section 5.2. c = 1 T Truepairs,(u,v)suchthatsim(u,v)≥τ
|                    |     |        |              |         |     |         | s       | F   | Falsepairs,(u,v)suchthatsim(u,v)<τ |     |     |                                |     |     |
| ------------------ | --- | ------ | ------------ | ------- | --- | ------- | ------- | --- | ---------------------------------- | --- | --- | ------------------------------ | --- | --- |
| has overestimation |     | errors | between      | 100%    | and | 900%    | at high |     |                                    |     |     |                                |     |     |
|                    |     |        |              |         |     |         |         | H   | High(expected)sim.                 |     |     | pairsthatareinthesamebucket    |     |     |
| thresholds.        | c   | = 0.5  | gives errors | between |     | 16% and | 437%,   |     |                                    |     |     |                                |     |     |
|                    | s   |        |              |         |     |         |         | L   | Low(expected)sim.                  |     |     | pairsthatarenotinthesamebucket |     |     |
c = 0.1 gives errors less than 62%. The choice of c de- P(T|H) given(u,v)s.t. B(u)=B(v),prob. ofsim(u,v)≥τ
| s   |     |     |     |     |     |     | s   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
pends on specific application requirements, but if variance P(H|T) given(u,v)s.t. sim(u,v)≥τ,prob. ofB(u)=B(v)
|          |          |       |      |     |                 |     |     | P(T|L) | given(u,v)s.t. |     | B(u)(cid:54)=B(v),prob. |                                  | ofsim(u,v)≥τ        |     |
| -------- | -------- | ----- | ---- | --- | --------------- | --- | --- | ------ | -------------- | --- | ----------------------- | -------------------------------- | ------------------- | --- |
| is not a | concern, | 0.1≤c | ≤0.5 | can | be recommended. |     |     |        |                |     |                         |                                  |                     |     |
|          |          |       | s    |     |                 |     |     | P(L|T) | given(u,v)s.t. |     | sim(u,v)≥τ,prob.        |                                  | ofB(u)(cid:54)=B(v) |     |
|          |          |       |      |     |                 |     |     | S      | stratum.       |     | e.g. SH:                | setofpairsthatareinthesamebucket |                     |     |
C.4 PUBMED:Accuracy,Variance,Efficiency N #pairs,e.g. NH: #pairsinthesamebucket
|                                               |           |          |             |       |           |                 |        | M   | #pairsinV,M |     | =(cid:0)|V|(cid:1) |     |           |     |
| --------------------------------------------- | --------- | -------- | ----------- | ----- | --------- | --------------- | ------ | --- | ----------- | --- | ------------------ | --- | --------- | --- |
| Figure9showstheaccuracyandvarianceonthePUBMED |           |          |             |       |           |                 |        |     |             |     |                    | 2   |           |     |
| data set                                      | with k    | =5.      | The average | error | of LSH-SS |                 | is 73% |     |             |     |                    |     |           |     |
|                                               |           |          |             |       |           |                 |        |     | Table       | 3:  | Summary            | of  | Notations |     |
| and that                                      | of RS     | is 117%. | LSH-SS      |       | shows     | underestimation |        |     |             |     |                    |     |           |     |
| tendency                                      | but its   | STD      | is more     | than  | an order  | of magnitude    |        |     |             |     |                    |     |           |     |
| smaller                                       | than that | of       | RS. When    | the   | data set  | is largely      | dis-   |     |             |     |                    |     |           |     |
349