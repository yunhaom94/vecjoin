# Noria Dynamic Partially Stateful Data Flow

**Source**: Noria Dynamic Partially Stateful Data Flow.pdf
**Format**: .pdf

---

Noria: dynamic, partially-stateful data-flow
for high-performance web applications
Jon Gjengset, Malte Schwarzkopf, Jonathan Behrens, and Lara Timbó Araújo,
MIT CSAIL; Martin Ek, Norwegian University of Science and Technology;
Eddie Kohler, Harvard University; M. Frans Kaashoek and Robert Morris, MIT CSAIL
https://www.usenix.org/conference/osdi18/presentation/gjengset
This paper is included in the Proceedings of the
13th USENIX Symposium on Operating Systems Design
and Implementation (OSDI ’18).
October 8–10, 2018 • Carlsbad, CA, USA
ISBN 978-1-939133-08-3
Open access to the Proceedings of the
13th USENIX Symposium on Operating Systems
Design and Implementation
is sponsored by USENIX.

|     |     | Noria: |     | dynamic,         |     | partially-stateful |     |              | data-flow |     |     |     |     |
| --- | --- | ------ | --- | ---------------- | --- | ------------------ | --- | ------------ | --------- | --- | --- | --- | --- |
|     |     |        | for | high-performance |     |                    | web | applications |           |     |     |     |     |
JonGjengset MalteSchwarzkopf JonathanBehrens LaraTimbo´ Arau´jo
|     |           |     | ∗   |              |     | ∗               |     |     |              |     |     |     |     |
| --- | --------- | --- | --- | ------------ | --- | --------------- | --- | --- | ------------ | --- | --- | --- | --- |
|     | MartinEk† |     |     | EddieKohler‡ |     | M.FransKaashoek |     |     | RobertMorris |     |     |     |     |
MITCSAIL †NorwegianUniversityofScienceandTechnology ‡HarvardUniversity
| Abstract |     |     |     |     |     |     | tablecolumnstoavoidre-computingthemoneverypage |     |     |     |     |     |     |
| -------- | --- | --- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- |
Weintroducepartially-statefuldata-flow,anewstream- load[42].Aseachvoteisreflectedinseveralplaces,ap-
plicationlogicmustexplicitlyupdatecomputedcolumns
| ing data-flow | model | that | supports | eviction |     | and recon- |            |         |          |     |        |                 |     |
| ------------- | ----- | ---- | -------- | -------- | --- | ---------- | ---------- | ------- | -------- | --- | ------ | --------------- | --- |
|               |       |      |          |          |     |            | every time | a value | changes. |     | Hence, | pre-computation |     |
structionofdata-flowstateondemand.Byavoidingstate
|             |                |       |              |        |        |           | complicates      | both | application | reads  | and     | writes.     | In gen- |
| ----------- | -------------- | ----- | ------------ | ------ | ------ | --------- | ---------------- | ---- | ----------- | ------ | ------- | ----------- | ------- |
| explosion   | and supporting |       | live changes |        | to the | data-flow |                  |      |             |        |         |             |         |
|             |                |       |              |        |        |           | eral, developers |      | must        | choose | between | convenient, | but     |
| graph, this | model          | makes | data-flow    | viable | for    | building  |                  |      |             |        |         |             |         |
slow,“natural”relationalqueries(e.g.,withinlineaggre-
| long-lived, | low-latency | applications, |     | such | as  | web appli- |     |     |     |     |     |     |     |
| ----------- | ----------- | ------------- | --- | ---- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
gations),andincreasedperformanceatthecostofappli-
cations.Ourimplementation,Noria,simplifiestheback-
cationanddeploymentcomplexity(e.g.,duetocaching).
endinfrastructureforread-heavywebapplicationswhile
improvingtheirperformance. Noria applications do not need to choose. Noria ex-
ANoriaapplicationsuppliesarelationalschemaanda
|     |     |     |     |     |     |     | poses a | high-level | query | interface | (SQL), |     | but unlike |
| --- | --- | --- | --- | --- | --- | --- | ------- | ---------- | ----- | --------- | ------ | --- | ---------- |
setofparameterizedqueries,whichNoriacompilesinto
|     |     |     |     |     |     |     | in conventional |     | systems, | Noria | accelerates |     | the execu- |
| --- | --- | --- | --- | --- | --- | --- | --------------- | --- | -------- | ----- | ----------- | --- | ---------- |
a data-flow program that pre-computes results for reads tionofevencomplexnaturalqueriesbyansweringwith
| and incrementally |     | applies | writes. | Noria | makes | it easy |              |         |       |           |     |        |           |
| ----------------- | --- | ------- | ------- | ----- | ----- | ------- | ------------ | ------- | ----- | --------- | --- | ------ | --------- |
|                   |     |         |         |       |       |         | pre-computed | results | where | possible. |     | At its | core, No- |
to write high-performance applications without manual ria runs a continuous, but dynamically changing, data-
performancetuningorcomplex-to-maintaincachinglay- flow computation that combines the persistent store, the
| ers. Partial | statefulness | helps | Noria | limit | its | in-memory |            |          |     |             |        |      |          |
| ------------ | ------------ | ----- | ----- | ----- | --- | --------- | ---------- | -------- | --- | ----------- | ------ | ---- | -------- |
|              |              |       |       |       |     |           | cache, and | elements | of  | application | logic. | Each | write to |
statewithoutpriordata-flowsystems’restrictiontowin- Noria streams through a joint data-flow graph for the
| dowed state, | and | helps | Noria | adapt | its data-flow | to  |         |         |                   |     |         |     |         |
| ------------ | --- | ----- | ----- | ----- | ------------- | --- | ------- | ------- | ----------------- | --- | ------- | --- | ------- |
|              |     |       |       |       |               |     | current | queries | and incrementally |     | updates | the | cached, |
schema and query changes while on-line. Unlike prior eventually-consistentinternalstateandqueryresults.
data-flowsystems,Noriaalsosharesstateandcomputa-
tionacrossrelatedqueries,eliminatingduplicatework. Making this approach work for web applications is
challenging.Ana¨ıveimplementationmightmaintainun-
| On a | real web | application’s |     | queries, | our | prototype |     |     |     |     |     |     |     |
| ---- | -------- | ------------- | --- | -------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
scalesto5 higherloadthanahand-optimizedMySQL boundedpre-computedstate,causingunacceptablespace
×
baseline.NoriaalsooutperformsatypicalMySQL/mem- and time overhead, so Noria must limit its state size.
Writescanupdatemanypre-computedresults,soNoria
cachedstackandthematerializedviewsofacommercial
database. It scales to tens of millions of reads and mil- must ensure that writes are fast and avoid unnecessary
|     |     |     |     |     |     |     | work. Finally, | since | many | web | applications |     | frequently |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ----- | ---- | --- | ------------ | --- | ---------- |
lionsofwritespersecondovermultipleservers,outper-
formingastate-of-the-artstreamingdata-flowsystem. changetheirqueries[20,61],Noriamustaccommodate
changeswithoutiteratingoveralldata.
1 Introduction
Existingdata-flowsystemseithercannotperformfine-
Webapplicationsmustservemanyusersatlowlatency.
grainedincrementalupdatestostate[36,52,75],orlimit
| They respond | to each | user | request | using | data | queried |     |     |     |     |     |     |     |
| ------------ | ------- | ---- | ------- | ----- | ---- | ------- | --- | --- | --- | --- | --- | --- | --- |
thegrowthofoperatorstateusing“windowed”state(e.g.,
| from backend | stores, | usually | relational |     | databases. | The |     |     |     |     |     |     |     |
| ------------ | ------- | ------- | ---------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
thisweek’sstories).Thisboundstheirmemoryfootprint
| vast majority | of such         | store        | accesses |            | are            | reads, and |                 |              |          |             |            |         |              |
| ------------- | --------------- | ------------ | -------- | ---------- | -------------- | ---------- | --------------- | ------------ | -------- | ----------- | ---------- | ------- | ------------ |
|               |                 |              |          |            |                |            | but prohibits   | reading      | older    | data        | [11,       | 39, 46, | 51]. No-     |
| evaluating    | them as         | repeated     | queries  |            | over the       | normal-    |                 |              |          |             |            |         |              |
|               |                 |              |          |            |                |            | ria’s data-flow |              | operator | state is    | partial    | instead | of win-      |
| ized schema   | of a relational |              | database |            | is inefficient | [54,       |                 |              |          |             |            |         |              |
|               |                 |              |          |            |                |            | dowed,          | retaining    | only     | the subset  | of records |         | that the ap- |
| 57]. Hence,   | many            | applications |          | explicitly | include        | pre-       |                 |              |          |             |            |         |              |
|               |                 |              |          |            |                |            | plication       | has queried. | This     | is possible |            | thanks  | to a new,    |
| computed      | query results   |              | in their | database   | schemas,       | or         |                 |              |          |             |            |         |              |
partially-statefuldata-flowmodel:wheninneedofmiss-
| cache such   | results      | in separate | key-value |            | stores | [8, 54].    |            |           |               |     |         |          |             |
| ------------ | ------------ | ----------- | --------- | ---------- | ------ | ----------- | ---------- | --------- | ------------- | --- | ------- | -------- | ----------- |
|              |              |             |           |            |        |             | ing state, | operators | request       | an  | upquery | that     | derives the |
| For example, | the Lobsters |             | news      | aggregator |        | [43] stores |            |           |               |     |         |          |             |
|              |              |             |           |            |        |             | missing    | records   | from upstream |     | state.  | Ensuring | correct-    |
stories’computedvotecountsand“hotness”inseparate
nesswiththismodelrequirescarefulattentiontoinvari-
∗equalcontribution ants, as ordinary updates and upqueries can race. With-
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    213

Write
stories votes users
∑
⋈
Read
krow
etirW
krow
edis-daeR
1 Write 1 Write
Add new query
stories votes users stories votes users
2 Stream
∑ ∑ through Invalidate data-flow
2 cache ⋈ ⋈ ∑ ⋈
Query on
3 read miss 3 Update view
cache StoryWithVC Karma
Read Read
(a)Classicdatabaseoperation (b)Two-tierstackwith (c)Noria:statefuldata-flowoperatorspre-computedatafor
withcomputeonreads. demand-filledcache[54,§2]. readsincrementally;data-flowchangesupportsnewqueries.
Figure1:OverviewofhowcurrentwebsitebackendsandNoriaprocessfrontendreadsandwrites.
outcare,suchracescouldproducepermanentlyincorrect crease for Noria-optimized applications. When serving
state,andthereforeincorrectcachedqueryresults. the Lobsters web application on a single Amazon EC2
The state that Noria keeps is similar to a material- VM, our prototype outperforms the default MySQL-
ized view, and its data-flow processing is akin to view based backend by 5 while simultaneously simplifying
×
maintenance [2, 37]. Noria demonstrates that, contrary the application (§8.1). For a representative query, our
toconventionalwisdom,maintainingmaterializedviews prototype outperforms the widely-used MySQL/mem-
for all application queries is feasible. This is possible cached stack and the materialized views of a commer-
becausepartially-statefuloperatorscanevictrarely-used cial database by 2–10 (§8.2). It also scales the query
×
state, and discard writes for that state, which reduces to millions of writes and tens of millions of reads per
statesizeandwriteload.Noriafurtheravoidsredundant secondonaclusterofEC2VMs,outperformingastate-
computationandstatebyjointlyoptimizingitsqueriesto of-the-artdata-flowsystem,differentialdataflow[46,51]
mergeoverlappingdata-flowsubgraphs. (§8.3).Finally,ourprototypeadaptsthedata-flowwith-
Fewexistingstreamingdata-flowsystemscanchange out any perceptible downtime for reads or writes when
their queries and input schemas without downtime. For transitioningthesamequerytoamodifiedversion(§8.5).
example, Naiad must re-start to accommodate changes, Nevertheless, our current prototype has some limita-
and Spark’s Structured Streaming must restart from a tions. It only guarantees eventual consistency; its evic-
checkpoint[18].Noria,bycontrast,adaptsitsdata-flow tionfrompartialstateisrandomized;itisinefficientfor
tonewquerieswithoutinterruptingexistingclients.Itap- shardedqueriesthatrequireshufflesinthedata-flow;and
plieschangeswhileretainingexistingstateandwhilere- itlackssupportforsomeSQLkeywords.Weplantoad-
maining live for reads throughout. Writes from current dresstheselimitationsinfuturework.
clientsseesub-secondinterruptionsinthecommoncase.
Noria’stechniquesremaincompatiblewithtraditional 2 Background
parallel and distributed data-flow, and allow Noria to
parallelize and scale fine-grained, partially materialized WenowexplainhowcurrentwebsitebackendsandNoria
viewmaintenanceovermultiplecoresandmachines. processdata.Figure1showsanoverview.
Insummary,Noriamakesfourprincipalcontributions: Many web applications use a relational database to
1. the partially-stateful data-flow model, its correct- store and query data (Figure 1a). Page views generate
nessinvariants,andaconformingsystemdesign; databasequeriesthatfrequentlyrequirecomplexcompu-
2. automatic merge-and-reuse techniques for data- tation,andthequeryloadtendstoberead-heavy.Across
flow subgraphs in joint data-flows over many one month of traffic data from a HotCRP site and the
queries,whichreduceprocessingcostandstatesize; production deployment of Lobsters [32], 88% to 97%
3. near-instantaneous, dynamic transitions for data- of queries are reads (SELECT queries), and these reads
flow graphs in response to changes to queries or consume88%oftotalqueryexecutiontimeinHotCRP.
schemawithoutlossofexistingstate;and Since read performance is important, application devel-
4. a prototype implementation and an evaluation that opers often manually optimize it. For example, Lob-
demonstratesthatpracticalwebapplicationsbenefit sters stores individual votes for stories in a votes ta-
fromNoria’sapproach. ble,butalsostoresper-storyvotecountsasacolumnin
OurNoriaprototypeexposesabackwards-compatible the stories table. This speeds up read queries of vote
MySQLprotocolinterfaceandcanserverealwebappli- counts,but“de-normalizes”theschemaandcomplicates
cations with minimal changes, although its benefits in- votewrites,whichmustupdatethederivedcounts.
214 13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| Websites    | often  | deploy     | an  | in-memory |     | key-value     |                |         |     |     |     |     |     |
| ----------- | ------ | ---------- | --- | --------- | --- | ------------- | -------------- | ------- | --- | --- | --- | --- | --- |
|             |        |            |     |           |     |               | 1 /* base      | tables  | */  |     |     |     |     |
| cache (like | Redis, | memcached, |     | or        | TAO | [8]) to speed |                |         |     |     |     |     |     |
|             |        |            |     |           |     |               | 2 CREATE TABLE | stories |     |     |     |     |     |
up common-case read queries (Figure 1b). Such a 3 (id int, author int, title text, url text);
|              |               |     |     |       |      |            | CREATE TABLE | votes | (user | int,          | story_id | int);  |     |
| ------------ | ------------- | --- | --- | ----- | ---- | ---------- | ------------ | ----- | ----- | ------------- | -------- | ------ | --- |
| cache avoids | re-evaluating |     | the | query | when | the under- | 4            |       |       |               |          |        |     |
|              |               |     |     |       |      |            | CREATE TABLE | users | (id   | int, username |          | text); |     |
5
lying records are unchanged. However, the application /* internal view: vote count per story */
6
must invalidate or replace cache entries as the records CREATE INTERNAL VIEW VoteCount AS
7
change.Thisprocessiserror-proneandrequirescomplex SELECT story_id, COUNT(*) AS vcount
8
|                                                   |     |     |     |     |     |     | FROM           | votes | GROUP | BY story_id; |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | -------------- | ----- | ----- | ------------ | --- | --- | --- |
| application-sidelogic[37,48,57,64].Forexample,de- |     |     |     |     |     |     | 9              |       |       |              |     |     |     |
|                                                   |     |     |     |     |     |     | 10 /* external | view: | story | details      | */  |     |     |
velopersmustcarefullyavoidperformancecollapsedue
|     |     |     |     |     |     |     | 11 CREATE VIEW | StoriesWithVC |     | AS  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ------------- | --- | --- | --- | --- | --- |
to“thunderingherds”(viz.,manydatabasequeriesissued
|                                                   |                  |     |      |      |           |           | 12 SELECT | id, author, |     | title, url,        | vcount |     |            |
| ------------------------------------------------- | ---------------- | --- | ---- | ---- | --------- | --------- | --------- | ----------- | --- | ------------------ | ------ | --- | ---------- |
|                                                   |                  |     |      |      |           |           | FROM      | stories     |     |                    |        |     |            |
| just after                                        | an invalidation) |     | [54, | 57]. | Since the | cache can | 13        |             |     |                    |        |     |            |
|                                                   |                  |     |      |      |           |           | JOIN      | VoteCount   | ON  | VoteCount.story_id |        | =   | stories.id |
| returnstalerecords,readsareeventually-consistent. |                  |     |      |      |           |           | 14        |             |     |                    |        |     |            |
|                                                   |                  |     |      |      |           |           | WHERE     | stories.id  | =   | ?;                 |        |     |            |
15
Somesitesusestream-processingsystems[13,39]to
| maintain | results | for queries | whose | re-execution |     | over | all |     |     |     |     |     |     |
| -------- | ------- | ----------- | ----- | ------------ | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
Figure2:NoriaprogramforakeysubsetoftheLobsters
pastdataisinfeasible.Onemajorproblemforthesesys- newsaggregator[43]thatcountsusers’votesforstories.
temsisthattheymustmaintainstateatsomeoperators,
suchasaggregations.Toavoidunboundedgrowth,exist-
computeandstoreinbasetablesforperformance.Views,
ingsystems“window”thisstatebylimitingittothemost
bycontrast,willlikelybelargerthanatypicalcachefoot-
| recent records. |       | This makes  | it      | difficult | for | a stream pro- |                |     |       |              |       |           |      |
| --------------- | ----- | ----------- | ------- | --------- | --- | ------------- | -------------- | --- | ----- | ------------ | ----- | --------- | ---- |
|                 |       |             |         |           |     |               | print, because |     | Noria | derives more | data, | including | some |
| cessor to       | serve | the general | queries | needed    |     | for websites, |                |     |       |              |       |           |      |
intermediateresults.Noriastoresbasetablespersistently
whichneedtoaccessolderaswellasrecentstate.More-
|              |            |     |          |          |      |            | on disk, | either | on one | server or | sharded | across | multiple |
| ------------ | ---------- | --- | -------- | -------- | ---- | ---------- | -------- | ------ | ------ | --------- | ------- | ------ | -------- |
| over, stream | processors |     | are less | flexible | than | a database |          |        |        |           |         |        |          |
servers,butstoresviewsinservermemory.Theapplica-
| that can | execute | any relational |     | query | on its | schema: | in-            |     |        |             |        |     |           |
| -------- | ------- | -------------- | --- | ----- | ------ | ------- | -------------- | --- | ------ | ----------- | ------ | --- | --------- |
|          |         |                |     |       |        |         | tion’s working |     | set in | these views | should | fit | in memory |
troducinganewqueryoftenrequiresarestart.
forgoodperformance,butNoriareducesmemoryuseby
| Noria, | as shown | in  | Figure | 1c, combines |     | the best | of  |     |     |     |     |     |     |
| ------ | -------- | --- | ------ | ------------ | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
onlymaterializingrecordsthatareactuallyread,andby
| these worlds. |     | It supports | the | fast | reads | of key-value |     |     |     |     |     |     |     |
| ------------- | --- | ----------- | --- | ---- | ----- | ------------ | --- | --- | --- | --- | --- | --- | --- |
evictinginfrequently-accesseddata.
caches,theefficientupdatesandparallelismofstreaming
3.2 Programminginterface
data-flow,and,likeaclassicdatabase,supportschanging
queriesandbasetableschemaswithoutdowntime.
|     |     |     |     |     |     |     | Applications | interact      |     | with Noria | via      | an interface | that        |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ------------- | --- | ---------- | -------- | ------------ | ----------- |
|     |     |     |     |     |     |     | resembles    | parameterized |     | SQL        | queries. | The          | application |
3 Noriadesign
Noria program,
|     |     |     |     |     |     |     | supplies | a   |     | which | registers |     | base tables |
| --- | --- | --- | --- | --- | --- | --- | -------- | --- | --- | ----- | --------- | --- | ----------- |
Noria is a stateful, dynamic, parallel, and distributed and views with parameters supplied by the application
data-flowsystemdesignedforthestorage,queryprocess- whenitretrievesdata.Figure2showsanexampleNoria
ing,andcachingneedsoftypicalwebapplications. programforaLobsters-likenewsaggregatorapplication
(?isaparameter).TheNoriaprogramincludesbaseta-
3.1 Targetapplicationsanddeployment
bledefinitions,internalviewsusedasshorthandsinother
Noriatargetsread-heavyapplicationsthattolerateeven- expressions,andexternalviewsthattheapplicationlater
tual consistency. Many web applications fit this model: queries.Internally,Noriainstantiatesadata-flowtocon-
theyaccepttheeventualconsistencyimposedbycaches tinuously process the application’s writes through this
thatmakecommon-casereadsfast[15,19,54,72].No- program,whichinturnmaintainstheexternalviews.
ria’scurrentdesignprimarilytargetsrelationaloperators, Toretrievedata,theapplicationsuppliesNoriawithan
rather than the iterative or graph computations that are externalviewidentifier(e.g.,StoriesWithVC)andone
the focus of other data-flow systems [46, 51], and pro- or more sets of parameter values. Noria then responds
cessesstructuredrecordsintabularform[12,16].Large
|     |     |     |     |     |     |     | with the | records | in  | the view | that match | those | values. |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------- | --- | -------- | ---------- | ----- | ------- |
blobs(e.g.,videos,PDFfiles)arebeststoredinexternal To modify records in base tables, the application per-
blobstores[7,24,50]andreferencedbyNoria’srecords. formsinsertions,updates,anddeletions,similartoaSQL
Noriarunsononeormoremulticoreserversthatcom- database.Noriaappliesthesechangestotheappropriate
municatewithclientsandwithoneanotherusingRPCs. basetablesandupdatesdependentviews.
ANoriadeploymentstoresbothbasetablesandderived
TheapplicationmaychangeitsNoriaprogramtoadd
views. Roughly, base tables contain the data typically new views, to modify or remove existing views, and to
storedpersistently,andderivedviewsholddataanappli- adapt base table schemas. Noria expects such changes
cationmightchoosetocache.Comparedtoconventional tobecommonandaimstocompletethemquickly.This
databaseuse,Noriabasetablesmightbesmaller,asNo- contrasts with most previous data-flow systems, which
ria derives data that an application may otherwise pre- lacksupportforefficientchangeswithoutdowntime.
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    215

| I   | ... |     |     | II  | ... |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
upstream  upstream  forexample,anoperatorthataggregatesvotesbyuserID
∑ SUM state ∑ SUM state requiresauserIDindextoprocessnewvotesefficiently.
|     |     | 2   | upquery |     |     |     | Inmoststreamprocessors,joinoperatorskeepawin- |     |     |     |     |     |     |
| --- | --- | --- | ------- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- |
...
σ  i n t o σ  dowed cache of their inputs [3, 76], allowing an up-
| 1 incoming  |     | FILTER | u p s tream |     | FILTER | 3 upquery  |     |     |     |     |     |     |     |
| ----------- | --- | ------ | ----------- | --- | ------ | ---------- | --- | --- | --- | --- | --- | --- | --- |
response
record state date arriving at one input to join with all relevant state
a t   j o in
|          | ⨝      |      |     | ⨝   |      |     | fromtheother.InNoria,joinsinsteadperformupqueries, |     |     |     |     |     |     |
| -------- | ------ | ---- | --- | --- | ---- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
| tr i g g | e rs   | JOIN |     |     | JOIN |     |                                                    |     |     |     |     |     |     |
upquery
whicharerequestsformatchingrecordsfromstatefulan-
... ... cestors (Figure 3): when an update arrives at one join
|     |     |     |     |     |     |     | input, the | join looks | up  | the relevant | state | by querying |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ---------- | --- | ------------ | ----- | ----------- | --- |
Figure3:Noria’sdata-flowoperatorscanqueryintoup-
|        |        |               |     |         | (I) |            | its other | inputs. | This reduces |     | Noria’s | space overhead, |     |
| ------ | ------ | ------------- | --- | ------- | --- | ---------- | --------- | ------- | ------------ | --- | ------- | --------------- | --- |
| stream | state: | a join issues | an  | upquery | to  | retrieve a |           |         |              |     |         |                 |     |
.. . since joins often need not store duplicate state, but re-
rec o rdfromupstreamstatetoproduceajoinresult(II).
quirescareinthepresenceofconcurrentupdates,anis-
|     |     |     |     |     |     |     | sue further | discussed | in  | §4. Upqueries |     | also impose | in- |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --------- | --- | ------------- | --- | ----------- | --- |
In addition to its native SQL-based query interface, dexingobligationsthatNoriadetectsandsatisfies.
| Noria | provides | an implementation |     |     | of the | MySQL bi- |     |     |     |     |     |     |     |
| ----- | -------- | ----------------- | --- | --- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- |
3.4 Consistencysemantics
naryprotocol,whichallowsexistingapplicationsthatuse
| prepared | statements | against |     | a MySQL | database | to in- |     |     |     |     |     |     |     |
| -------- | ---------- | ------- | --- | ------- | -------- | ------ | --- | --- | --- | --- | --- | --- | --- |
Toachievehighparallelprocessingperformance,Noria’s
| teract | with Noria | without | further | changes. |     | The adapter |           |        |        |          |          |              |     |
| ------ | ---------- | ------- | ------- | -------- | --- | ----------- | --------- | ------ | ------ | -------- | -------- | ------------ | --- |
|        |            |         |         |          |     |             | data-flow | avoids | global | progress | tracking | or coordina- |     |
turns ad-hoc queries and prepared SQL statements into tion. An update injected by a base table takes time to
writestobasetables,readsfromexternalviews,andin-
propagatethroughthedata-flow,andtheupdatemayap-
| crementally | effects | Noria | program |     | changes. | Noria sup- |         |           |          |           |        |       |        |
| ----------- | ------- | ----- | ------- | --- | -------- | ---------- | ------- | --------- | -------- | --------- | ------ | ----- | ------ |
|             |         |       |         |     |          |            | pear in | different | views at | different | times. | Noria | opera- |
portsmuch,butnotall,SQLsyntax.Wediscusstheex- torsandthecontentsofitsexternalviewsareeventually-
perienceofbuildingandportingapplicationsin§7.
|     |     |     |     |     |     |     | consistent. | Eventual | consistency |     | is attractive | for | perfor- |
| --- | --- | --- | --- | --- | --- | --- | ----------- | -------- | ----------- | --- | ------------- | --- | ------- |
manceandscalability,andissufficientformanywebap-
3.3 Data-flowexecution
plications[15,54,72].
Noria’sdata-flowisadirectedacyclicgraphofrelational Noria does ensure that if writes quiesce, all external
| operators | such | as aggregations, |     | joins, | and | filters. Base |                  |     |              |      |         |      |           |
| --------- | ---- | ---------------- | --- | ------ | --- | ------------- | ---------------- | --- | ------------ | ---- | ------- | ---- | --------- |
|           |      |                  |     |        |     |               | views eventually |     | hold results | that | are the | same | as if the |
tablesaretherootsofthisgraph,andexternalviewsform queries had been executed directly against the base ta-
theleaves.Noriaextendsthegraphwithnewbasetables,
bledata.Makingthisworkcorrectlyrequiressomecare.
operators,andviewsastheapplicationaddsnewqueries. Likemostdata-flowsystems,Noriarequiresthatopera-
Whenanapplicationwritearrives,Noriaappliesitto torsaredeterministicfunctionsovertheirownstateand
a durable base table and injects it into the data-flow as the inputs from their ancestors. In addition, Noria must
an update. Operators process the update and emit de- avoid races between updates and upqueries; avoid re-
rivedupdatestotheirchildren;eventuallyupdatesreach
orderingupdatesonthesamedata-flowpath;andresolve
and modify the external views. Updates are deltas [46, races between related updates that arrive independently
60] that can add to, modify, and remove from down- atmulti-ancestoroperatorsviadifferentdata-flowpaths.
ConsideranORthatcombinesfiltersusingaunionoper-
streamstate.Forexample,acountoperatoremitsdeltas
that indicate how the count for a key has changed; a ator, or a join between data-flow paths connected to the
joinmayemitanupdatethatinstallsnewrowsindown- samebasetable:suchoperators’finaloutput(andstate)
stream state; and a deletion from a base table generates must be commutative over the order in which updates
a “negative” update that revokes derived records. Neg- arrive at their inputs. The standard relational operators
ative updates remove entries when Noria applies them Noriasupportshavethisproperty.
tostate,andretaintheirnegative“sign”whencombined Web applications sometimes rely on database trans-
| withotherrecords(e.g.,throughjoins).Negativeupdates |     |     |     |     |     |     |          | e.g., |            |        |              |     |      |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | -------- | ----- | ---------- | ------ | ------------ | --- | ---- |
|                                                     |     |     |     |     |     |     | actions, | to    | atomically | update | pre-computed |     | val- |
holdexactlythesamevaluesasthepositivestheyrevoke ues. Noria approach’s is compatible with basic,
andthusfollowthesamedata-flowpaths. optimistically-concurrent multi-statement transactions,
Noria supports stateless and stateful operators. State- butNoriaalsooftenobviatestheneedforthem.Forex-
less operators, such as filters and projections, need no ample, Lobsters uses transactions only to avoid write-
context to process updates; stateful operators, such as write conflicts on vote counts and stories’ “hotness”
count,min/max,andtop-k,maintainstatetoavoidinef- scores.Amulti-statementtransactionisrequiredonlybe-
ficientre-computationofaggregatevaluesfromscratch. causebaselineLobsterspre-computeshotnessforperfor-
Statefuloperators,likeexternalviews,keeponeormore mance.Noriainsteadcomputeshotnessinthedata-flow,
indexestospeedupoperation.Noriaaddsindexesbased whichavoidswrite-writeconflictswithoutatransaction,
onindexingobligationsimposedbyoperatorsemantics;
|     |     |     |     |     |     |     | albeit at | the cost | of eventual | consistency |     | for reads. | We  |
| --- | --- | --- | --- | --- | --- | --- | --------- | -------- | ----------- | ----------- | --- | ---------- | --- |
216    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| I   | ... |     |     | II ... |     |     | stories |     | votes |     |     |     |
| --- | --- | --- | --- | ------ | --- | --- | ------- | --- | ----- | --- | --- | --- |
3 recursive upquery hits
|     |     |     |     |     |     |     | id author text |     | user | story_id |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ---- | -------- | --- | --- |
∑ SUM ∑ SUM   0           u 3                 a     u 7                     0 T  = {      u 1       1   ,     u 3       1   }
|            |     |     | k x       7 |     | k   | x       7 |                                 |     |                 | e             |     |     |
| ---------- | --- | --- | ----------- | --- | --- | --------- | ------------------------------- | --- | --------------- | ------------- | --- | --- |
|            |     |     | k y       2 |     | k   | y       2 |   1           u 1               |   b |     u 1         |             1 |     |     |
| 2recursive |     |     |             |     |     |           |                                 |     |   u3          1 |               |     |     |
VoteCount
|     | upquery       |       |     |       |     |     |     |     |    u3   1    | story_idvcount            |     |     |
| --- | ------------- | ----- | --- | ----- | --- | --- | --- | --- | ------------ | ------------------------- | --- | --- |
|     |               |       |     |       |     |     |     | ⨝   |              |             0             |     |     |
|     | m is s e s ,  | ∑ SUM |     | ∑ SUM |     |     |     | J   | O IN ∑ COUNT |                           |     | e   |
|     | rec u r s e s |       | k   |       | k   | 9   |     |     |              |             1           1 |     |     |
i d:st o r y_ id
|     |       |     |     | k   | 9   |     | StoriesWithVC   |      |        | S = {      u 1       1    } |     |     |
| --- | ----- | --- | --- | --- | --- | --- | --------------- | ---- | ------ | --------------------------- | --- | --- |
| 1   | read  |     |     |     |     |     | story_id author | text | vcount | e                           |     |     |
misses 4 upquery response      0     D = {      1       u 1         b        2    }
|     | k   |     |     | k 9 |                      |     |                                         |     |     |     |     |     |
| --- | --- | --- | --- | --- | -------------------- | --- | --------------------------------------- | --- | --- | --- | --- | --- |
|     |     |     |     |     | fills missing record |     |      1           u1        b          2 |     |     | e   |     |     |
Figure4:Apartially-statefulviewsendsarecursiveup- Figure 5: Definitions for partial state entry e (yellow)
querytoderiveevictedstate( )forkeykfromupstream inVoteCount:anin-flightupdatefromvotes(blue)is
⊥
state(I);theresponsefillsthemissingstate(II). in T e, but not yet in S e; the entry in StoriesWithVC is
|     |     |     |     |     |     |     | key-descendantfromeviastory |     |     | id(green). |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | ---------- | --- | --- |
omitfurtherdiscussionoftransactionswithNoriainthis
paper;weplantodescribetheminfuturework. ing operator—while (possibly slow) upqueries are in
| 3.5 | Challenges |     |     |     |     |     | flight.Theserequirementscomplicatethedesign. |     |     |     |     |     |
| --- | ---------- | --- | --- | --- | --- | --- | -------------------------------------------- | --- | --- | --- | --- | --- |
AnefficientNoriadesignfacestwokeychallenges:first,
4.1 Data-flowmodelandinvariants
itmustlimitthesizeofitsstateandviews(§4);andsec-
ond,changestotheNoriaprogrammustadaptthedata- Wefirstdescribehigh-levelcorrectnessinvariantsofNo-
flowwithoutdowntimeinservingclients(§5). ria’spartially-statefuldata-flow.Theseinvariantsensure
|     |     |     |     |     |     |     | that Noria | remains | eventually-consistent |     | and | never re- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------- | --------------------- | --- | --- | --------- |
4 Partially-statefuldata-flow
turnsresultscontaminatedbyduplicate,missing,orspu-
Noria must limit the size of its views, as the state for riousupdates.SinceNoriaallowsoperatorstoexecutein
anapplicationwithmanyqueriescouldexceedavailable paralleltotakeadvantageofmulticoreprocessors,these
memoryandbecometooexpensivetomaintain. invariants must hold in the presence of concurrent up-
|     | partially-stateful |     | data-flow | model |     |     |     |     |     |     |     | state |
| --- | ------------------ | --- | --------- | ----- | --- | --- | --- | --- | --- | --- | --- | ----- |
The lets operators dates and eviction notices. The invariants concern
maintainonlyasubsetoftheirstate.Thisconceptofpar- entries,whereastateentrymodelsonerecordinoneop-
tialmaterializationiswell-knownformaterializedviews erator or view. Data-flow implementations derive state
indatabases[79,80],butnoveltodata-flowsystems.Par- entry values from input records, possibly after multi-
tialstatereducesmemoryuse,allowsevictionofrarely- ple steps. For ease of expression, we model a state en-
|     |     |     |     |     |     |     | try as the | multiset | of input | records | that produced | that |
| --- | --- | --- | --- | --- | --- | --- | ---------- | -------- | -------- | ------- | ------------- | ---- |
usedstate,andrelievesoperatorsfrommaintainingstate
thatisneverread.Partially-statefuldata-flowgeneralizes entry’svalue. Noria’seventualconsistencyrequiresthat
beyond Noria, but we highlight specific design choices eachstateentry’scontentsapproachtheidealsetofinput
thathelpNoriaachieveitsgoals. recordsthatwouldproducethemostup-to-datevalue.
Partialstateintroducesnewdata-flowmessagestoNo- Givensomestateentrye,wedefine:
ria.Evictionnoticesflowforwardalongtheupdatedata-
•T eisthesetofallinputrecordsreceivedsofarthat,in
| flow   | path;       | they indicate | that      | some state | entries | will no    |                          |     |     |               |        |       |
| ------ | ----------- | ------------- | --------- | ---------- | ------- | ---------- | ------------------------ | --- | --- | ------------- | ------ | ----- |
|        |             |               |           |            |         |            | a correct implementation |     | of  | the data-flow | graph, | would |
| longer | be updated. |               | Operators | drop       | updates | that would |                          |     |     |               |        |       |
beusedtocomputee.
| affect | these | evicted | state | entries without |     | further pro- |     |     |     |     |     |     |
| ------ | ----- | ------- | ----- | --------------- | --- | ------------ | --- | --- | --- | --- | --- | --- |
•S eiseitherthemultisetofinputrecordsactuallyused
| cessing | or        | forwarding. | When      | Noria    | needs       | to read from |                 |     |                                 |     |     |     |
| ------- | --------- | ----------- | --------- | -------- | ----------- | ------------ | --------------- | --- | ------------------------------- | --- | --- | --- |
|         |           |             |           |          |             |              | tocomputeine,or |     | ,whichrepresentsanevictedentry. |     |     |     |
| evicted | state—for |             | instance, | when the | application | reads        |                 |     |                                 |     |     |     |
⊥
|     |     |     |     |     |     |     | We use a | multiset | so the model | can | represent | potential |
| --- | --- | --- | --- | --- | --- | --- | -------- | -------- | ------------ | --- | --------- | --------- |
stateevictedfromanexternalview—Noriare-computes
bugssuchasduplicateupdates.
thatstate.Thisprocesssendsrecursiveupqueriestothe
|          |           |     |              |         |     |             | • D e is | the set | of key-descendant | entries | of  | e. These |
| -------- | --------- | --- | ------------ | ------- | --- | ----------- | -------- | ------- | ----------------- | ------- | --- | -------- |
| relevant | ancestors |     | in the graph | (Figure | 4). | An ancestor |          |         |                   |         |     |          |
areentriesofoperatorsdownstreamofeinthedata-flow
thathandlessuchanupquerycomputesthedesiredvalue
thatdependonethroughkeylookup.
(possiblyaftersendingitsownupqueries),thenforwards
T andS aretime-dependent,whereasthedependencies
| a response |     | that follows | the | data-flow | path | to the query- | e e |     |     |     |     |     |
| ---------- | --- | ------------ | --- | --------- | ---- | ------------- | --- | --- | --- | --- | --- | --- |
ing operator. When the upquery response eventually ar- representedinD e canbedeterminedfromthedata-flow
|     |     |     |     |     |     |     | graph. If | e is the | VoteCount | entry | for some | story in |
| --- | --- | --- | --- | --- | --- | --- | --------- | -------- | --------- | ----- | -------- | -------- |
rives,Noriausesittopopulatetheevictedentry.Afterthe
T
evictedentryhasbeenfilled,subsequentupdatesthrough Figure 5, then e contains all input votes ever received
thedata-flowkeepitup-to-dateuntilitisevictedagain. for that story; S contains the updates represented in its
e
|     |                  |     |           |              |     |             | vcount;andD | eincludesitsStoriesWithVCentry. |     |     |     |     |
| --- | ---------------- | --- | --------- | ------------ | --- | ----------- | ----------- | ------------------------------- | --- | --- | --- | --- |
|     | For correctness, |     | upqueries | must produce |     | eventually- |             |                                 |     |     |     |     |
consistent results. For performance, Noria should con- Correctnessofpartially-statefuldata-flowreliesonen-
| tinuetoprocessupdates—includingupdatestothewait- |     |     |     |     |     |     | suringtheseinvariants: |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- |
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    217

1. Updatecompleteness:ifS = ,theneitherallup- use recursive upqueries to fill it in. Moreover, operators
e (cid:54) ⊥
datesinT S eareinflighttowarde,oraneviction now encounter evicted state when they handle updates.
e
−
noticeforeisinflighttowarde. ThesefactorsinfluencetheNoriadesigninseveralways.
2. Nospuriousorduplicateupdates:S T e. First and simplest, Noria operators drop updates that
|                        |     |     |     |     | e            | ⊆   |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Descendanteviction:ifS |     |     |     | =   | ,thenforalld | D   |     |     |     |     |     |     |     |     |
3. e e, encounter evicted entries. This reduces the time spent
|     |     |     |     | ⊥   |     | ∈   |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
eitherS d = ,oranevictionnoticefordisinflight processingupdatesdownstream,butnecessitatesthede-
⊥
towardd’soperator. scendantevictioninvariant:operatorsdownstreamofan
4. Eventual consistency: if T e stops growing, then evicted entry never see updates for that entry, so they
eventuallyeitherS =T eorS = . must evict their own dependent entries lest they remain
|     |     |     | e   | e   | ⊥   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
WenowexplainthemechanismsthatNoriausestoreal- permanentlyoutofdate.
izethisdata-flowmodelandmaintaintheinvariants. Second,recursiveupqueriesnowoccasionallycascade
|     |     |     |     |     |     |     | up in the | data-flow | until | they | encounter | the | necessary |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | --------- | ----- | ---- | --------- | --- | --------- | --- |
4.2 Updateordering
|     |     |     |     |     |     |     | state—in | the worst | case, | up  | to base | tables. | Responses |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | --------- | ----- | --- | ------- | ------- | --------- | --- |
Noria uses update ordering to ensure eventual consis- thenflowforwardtothequeryingoperator.Upqueryre-
tencywithoutglobaldata-flowcoordination.Eachoper-
|     |     |     |     |     |     |     | sults are | snapshots | of operator |     | state, | and | do not | com- |
| --- | --- | --- | --- | --- | --- | --- | --------- | --------- | ----------- | --- | ------ | --- | ------ | ---- |
atortotallyordersallupdatesandupqueryrequestsitre-
mutewithupdates.Forunbranchedchains,updateorder-
ceivesforanentry;and,critically,thedownstreamdata- ing (§4.2) and the fact that updates to evicted state are
flowensuresthatallupdatesandupqueryresponsesfrom
|            |     |           |        |           |     |                | dropped | ensure | that the | requested | upquery |     | response | is  |
| ---------- | --- | --------- | ------ | --------- | --- | -------------- | ------- | ------ | -------- | --------- | ------- | --- | -------- | --- |
| that entry | are | processed | by all | consumers |     | in that order. |         |        |          |           |         |     |          |     |
processedbeforeanyupdatefortheevictedstate.
| Thus, if | the operator |     | orders | update | u before | u , then |           |           |     |              |     |            |      |     |
| -------- | ------------ | --- | ------ | ------ | -------- | -------- | --------- | --------- | --- | ------------ | --- | ---------- | ---- | --- |
|          |              |     |        |        | 1        | 2        | Recursive | upqueries |     | of branching |     | subgraphs, | such | as  |
everydownstreamconsumerlikewiseprocessesupdates
joins,aremorecomplex.Ajoinoperatormustemitasin-
| derivedfromu |     | beforethosederivedfromu |     |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | --- | ----------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
1 2 .Noriadata- glecorrectresponseforeachupqueryitreceives,evenif
| flows can | split | and merge | (e.g., | at joins), | but | update or- |     |     |     |     |     |     |     |     |
| --------- | ----- | --------- | ------ | ---------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
itmustmakeoneormorerecursiveupqueriesofitsown
deringandoperatorcommutativityensurethattheeven-
|     |     |     |     |     |     |     | to produce | the | needed | state. Combining |     | the | upqueries’ |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ------ | ---------------- | --- | --- | ---------- | --- |
tualresultiscorrectindependentofprocessingorder.
resultsdirectlywouldbeincorrect:thoseupqueriesexe-
4.3 Joinupqueries cuteindependently,andupdatescanarrivebetweentheir
responses.Joinsthusissuerecursiveupqueries,butcom-
| Join operators |     | use upqueries |     | (§3.3): | when | an updatear- |     |     |     |     |     |     |     |     |
| -------------- | --- | ------------- | --- | ------- | ---- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
putethefinalresultexclusivelywithjoinupqueriesonce
rivesatoneinput,thejoinupqueriesitsotherinputforthe
therecursiveupqueriescomplete(multipleroundsofre-
correspondingrecords,andcombinesthemwiththeup-
cursiveupqueriesmayberequired).Thesejoinupqueries
date.Joinupqueriesreachthenextupstreamstatefulop-
executewithinasingleoperatorchainandexcludecon-
erator,whichcomputesasnapshotoftherequestedstate
|     |     |     |     |     |     |     | current updates. |     | Noria | supports | other | branching |     | opera- |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ----- | -------- | ----- | --------- | --- | ------ |
entryandforwardsitalongthedata-flowtothequerying
tors,suchasunions,whichobeythesamerulesasjoins.
| join. Intermediate |     | operators | process |     | the response | as ap- |          |        |         |           |     |        |        |      |
| ------------------ | --- | --------- | ------- | --- | ------------ | ------ | -------- | ------ | ------- | --------- | --- | ------ | ------ | ---- |
|                    |     |           |         |     |              |        | Finally, | a join | upquery | performed |     | during | update | pro- |
propriate.Unlikenormalupdates,upqueryresponsesfol-
|     |     |     |     |     |     |     | cessing | may encounter |     | evicted | state. | In this | case, | No- |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------------- | --- | ------- | ------ | ------- | ----- | --- |
lowthesinglepathbacktothequeryingoperatorwithout
|            |         |               |     |              |      |              | ria chooses       | to drop      | the      | update     | and      | evict dependent |             | en-    |
| ---------- | ------- | ------------- | --- | ------------ | ---- | ------------ | ----------------- | ------------ | -------- | ---------- | -------- | --------------- | ----------- | ------ |
| forking.   | Upquery | responses     |     | also commute |      | neither with |                   |              |          |            |          |                 |             |        |
|            |         |               |     |              |      |              | tries downstream; |              | Noria    | statically | analyzes |                 | the graphto |        |
| each other | nor     | with previous |     | updates.     | This | introduces a |                   |              |          |            |          |                 |             |        |
|            |         |               |     |              |      |              | compute           | the required | eviction |            | notices. | There           | is a        | trade- |
problemforjoinupdateprocessing,sinceeverysuchup-
offhere:computingthemissingentrycouldavoidfuture
daterequiresanupquerythatproducesnon-commutative
results,yetmustproduceanupdatethatdoescommute. upqueries. Noria chooses to evict to avoid blocking the
writepathwhilefillinginthemissingstate.
| Noria         | achieves | this         | by ensuring  |          | that no        | updates are |                   |           |         |            |     |           |     |        |
| ------------- | -------- | ------------ | ------------ | -------- | -------------- | ----------- | ----------------- | --------- | ------- | ---------- | --- | --------- | --- | ------ |
|               |          |              |              |          |                |             | Such              | evictions | are     | rare,      | but | they      | can | occur. |
| in flight     | between  | the upstream |              | stateful | operator       | and the     |                   |           |         |            |     |           |     |        |
|               |          |              |              |          |                |             | For example,      |           | imagine | a version  |     | of Figure |     | 2 that |
| join when     | a join   | upquery      | occurs.      | To       | do so,         | Noria lim-  |                   |           |         |            |     |           |     |        |
|               |          |              |              |          |                |             | adds AuthorVotes, |           | which   | aggregates |     | VoteCount |     | by     |
| its the scope | of       | each         | join upquery |          | to an operator | chain       |                   |           |         |            |     |           |     |        |
stories.author,andthefollowingsystemstate:
processedbyasinglethread.Noriaexecutesupdateson
•stories[id=1]hasauthor=Elena.
otheroperatorchainsinparallelwithjoinupqueries.
|                 |     |             |     |         |             |     | •VoteCount[story |     |     | id=1]hasvcount=8. |     |     |     |     |
| --------------- | --- | ----------- | --- | ------- | ----------- | --- | ---------------- | --- | --- | ----------------- | --- | --- | --- | --- |
| This introduces |     | a trade-off |     | between | parallelism | and |                  |     |     |                   |     |     |     |     |
•AuthorVotes[author=Elena]hasvcount=8.
stateduplication:joinprocessingmuststaywithinasin-
•stories[id=2]hasauthor=Bob.
| gle operator | chain, | so  | copies | of upstream |     | state may be |                  |     |     |                 |     |     |     |     |
| ------------ | ------ | --- | ------ | ----------- | --- | ------------ | ---------------- | --- | --- | --------------- | --- | --- | --- | --- |
|              |        |     |        |             |     |              | •VoteCount[story |     |     | id=2]isevicted. |     |     |     |     |
requiredineachoperatorchainthatcontainsajoin.
|     |     |     |     |     |     |     | Now imagine |     | that an | update | changes | story | 2’s | au- |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ------- | ------ | ------- | ----- | --- | --- |
4.4 Evictionandrecursiveupqueries
|     |     |     |     |     |     |     | thor to | Elena. | When | this update |     | arrives | at the | join |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------ | ---- | ----------- | --- | ------- | ------ | ---- |
EvictedstateintroducesnewchallengesforNoria’sdata- for AuthorVotes, that join operator upqueries for
|     |     |     |     |     |     |     | VoteCount[story |     | id=2],whichisevicted.Asaresult, |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ------------------------------- | --- | --- | --- | --- | --- |
flow.Iftheapplicationrequestsevictedstate,Noriamust
218    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

NoriasendsanevictionnoticeforElena—whosenumber newexpression.Thesharingcandidatesareexistingex-
ofvoteshaschanged—toAuthorVotes. pressions that likely overlap with the new expression.
Next, Noria generates a verbose intermediate represen-
4.5 Partialandfullstate
tation (IR), which splits the new expression into more
Noria makes state partial whenever it can service up- fine-grained operators. This simplifies common subex-
queries using efficient index lookups. If Noria would pressiondetection,andallowsNoriatoefficientlymerge
havetoscanthefullstateofanupstreamoperatortosat- thenewIRwiththecachedIRofthesharingcandidates.
isfyupqueries,Noriadisablespartialstateforthatoper- Foreachsharingcandidate,Noriareordersjoinsinthe
ator.Thismayhappenbecauseeverydownstreamrecord new IR to match the candidate when possible to max-
dependsonallupstreamones—considere.g.,thetop20 imize re-use opportunities. It then traverses the candi-
stories by vote count. In addition, the descendant evic- date’s IR in topological order from the base tables. For
tion invariant implies that partial-state operators cannot eachoperator,Noriasearchesforamatchingoperator(or
havefull-statedescendants. cliqueofoperators)inthenewIR.Amatchrepresentsa
Partial-state operators in Noria start out fully evicted reusablesubexpression,andNoriasplicesthetwoIRsto-
andaregraduallyandlazilypopulatedbyupqueries.As getheratthedeepestmatches.
we show next, this choice has important consequences This process continues until Noria has considered all
forNoria’sabilitytotransitionthedata-flowefficiently. identifiedreusecandidates,producingafinal,mergedIR.
5 Dynamicdata-flow 5.2 Data-flowtransition
Application queries evolve over time, so Noria’s dy- The combined final IRs of all current expressions rep-
namic data-flow represents a continuously-changing set resent the transition’s target data-flow. Noria must add
ofSQLexpressions.Existingdata-flowsystemsrunsep- anyoperatorinthefinalIRthatdoesnotalreadyexistin
arate data-flows for each expression, initialize new op- the data-flow. To do so, Noria first informs existing op-
erators with empty state and reflect only new writes, or erators of index obligations (§3.3) incurred by new op-
requirerestartingfromacheckpoint.ChangestotheNo- erators that they must construct indexes for. Noria then
riaprograminsteadadaptthedata-flowdynamically. walksthetargetdata-flowintopologicalorderandinserts
Givenneworremovedexpressions,Noriatransitions each new operator into the running data-flow and boot-
thedata-flowtoreflectthechanges.Noriafirstplansthe strapsitsstate.Finally,afterinstallingnewoperatorsand
transition,reusingoperatorsandstateofexistingexpres- deletingremovedqueries’externalviews,Noriaremoves
sionswherepossible(§5.1).Itthenincrementallyapplies obsoleteoperatorsandstatefromthedata-flow.
thesechangestothedata-flow,takingcaretomaintainits Bootstrapping operator state. When Noria adds a
correctnessinvariants(§5.2).Oncebothstepscomplete, new stateful operator, it must ensure that the operator
theapplicationcanusenewtablesandqueries. starts with the correct state. Partially-stateful operators
Thekeychallengesfortransitionsaretoavoidunnec- and views start processing immediately. They are ini-
essarystateduplicationandtocontinueprocessingreads tially empty and bootstrap via upqueries in response to
and writes throughout. Operator reuse and partial state application reads during normal operation, amortizing
helpNoriaaddressthesechallenges. the bootstrapping work over time. Fully-stateful opera-
torsareinitiallymarkedas“inactive”,whichcausesthem
5.1 Determiningdata-flowchanges
to ignore all incoming updates. Noria then executes a
To initiate a transition, the application provides Noria special,largeupqueryforallkeysonbehalfofthefully-
withsetsofaddedandremovedexpressions.Noriathen statefuloperator.Oncethelastupqueryresponsehasar-
computesrequiredchangestothecurrently-runningdata- rived,Noriaactivatestheoperatorforupdateprocessing
flow. This process resembles traditional database query andmovesontothenextnewoperator.
planning,butproducesalong-termjointdata-flowacross Basetablechanges.Asapplicationsevolve,develop-
allexpressionsintheNoriaprogram.ThisallowsNoria ers often add or remove base table columns [17]. This
to reuse existing operators for efficiency: if two queries affects existing operators in the data-flow: new updates
includethesamejoin,thedata-flowcontainsitonlyonce. fromthebasetablemaynowlackvaluesthatexistingop-
Toplanatransition,Noriafirsttranslateseachnewex- eratorsexpect.Noriacouldrebuildthedata-flowortrans-
pression into an extended query graph [21]. The query formtheexistingbasetablestatetoeffectsuchachange,
graph contains a node for each table or view in the ex- butthiswouldbeinefficientforlargebasetables.Instead,
pression,andanedgeforeveryjoinorgroup-byclause. Noria base tables internally track all columns that have
Noriausesquerygraphstoinexpensivelyrejectmanyex- existed in the table’s schema, including those that have
pressions from consideration [21, §3.4, 78, §3] and to beendeleted.Whenabasetableprocessesanapplication
quickly establish a set of sharing candidates for each write,itautomaticallyinjectsdefaultvaluesformissing
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 219

columns(butdoesnotstorethem).Thispermitsqueries There are typically fewer data-flow workers than oper-
for different base table schemas to coexist in the data- atorsinthedata-flowgraph,soNoriamultiplexesopera-
flowgraph,andmakesmostbasetablechangescheap. torworkacrosstheworkerthreads.Withinoneinstance,
Noriascheduleschainsofoperatorswiththesamekeyas
6 Implementation
aunit.Thisreducesqueueingandinter-coredatamove-
Our Noria prototype implementation consists of 45k mentatoperatorboundaries.ItalsoallowsNoriatoop-
|     |     |     |     |     |     |     | timize some | upqueries: |     | an upquery | within | a chain | can |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | --- | ---------- | ------ | ------- | --- |
linesofRustandcanoperatebothonasingleserverand
across a cluster of servers. Applications interface with simplyaccesstheancestor’sdatasynchronously,without
Noria either through native Rust bindings, using JSON worryofcontaminationfromin-flightupdates(§4.3).
overHTTP,orthroughaMySQLprotocoladapter. Readhandlersprocessclients’RPCstoreadfromex-
ternalviews.Theymustaccesstheviewwithlowlatency
6.1 Persistentdatastorage
|     |     |     |     |     |     |     | and high | concurrency, | even | while | a data-flow | worker | is  |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------------ | ---- | ----- | ----------- | ------ | --- |
Noria persists base tables in RocksDB [66], a high- applyingupdatestotheview.Tominimizesynchroniza-
performance key-value store based on log-structured tion,Noriausesdouble-bufferedhashtablesforexternal
views[27]:thedata-flowworkerupdatesonetablewhile
| merge (LSM) | trees. | Batches |     | of application |     | updates are |     |     |     |     |     |     |     |
| ----------- | ------ | ------- | --- | -------------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
synchronously flushed into RocksDB’s log before No- readhandlersreadtheother,andanatomicpointerswap
ria acknowledges them and admits them into the data- exposesnewwrites.Thistradesspaceandtimelinessfor
flow; a background thread asynchronously merges log performance: with skewed key popularity distributions,
entriesintotheLSMtrees.Eachbasetableindexforms it can improve read throughput by 10 over a single-
×
bufferedhashtablewithbucket-levellocks.
| a RocksDB | “column | family”. |     | For base | tables | with non- |     |     |     |     |     |     |     |
| --------- | ------- | -------- | --- | -------- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- |
uniqueindexes,NoriausesRocksDB’sorderediterators
6.3 Distributedoperation
toefficientlyretrieveallrowsforanindexkey[14,67].
|     |     |     |     |     |     |     | A Noria | controller | process | manages |     | distributed | in- |
| --- | --- | --- | --- | --- | --- | --- | ------- | ---------- | ------- | ------- | --- | ----------- | --- |
PersistencereducesNoria’swritethroughputbyabout
|         |           |      |         |       |     |             | stances | on a cluster     | of  | servers, | and | informs them | of      |
| ------- | --------- | ---- | ------- | ----- | --- | ----------- | ------- | ---------------- | --- | -------- | --- | ------------ | ------- |
| 5% over | in-memory | base | tables. | Reads | are | not greatly |         |                  |     |          |     |              |         |
|         |           |      |         |       |     |             | changes | to the data-flow |     | graph    | and | of shard     | assign- |
impactedwhenanapplication’sworkingsetfitsinmem-
|           |            |           |     |        |          |     | ments. Noria | elects | the | controller | and | persists its | state |
| --------- | ---------- | --------- | --- | ------ | -------- | --- | ------------ | ------ | --- | ---------- | --- | ------------ | ----- |
| ory: only | occasional | upqueries |     | access | RocksDB, | and |              |        |     |            |     |              |       |
theseadd<1msofadditionallatencyonafastSSD. via ZooKeeper [34]. Clients discover the controller via
ZooKeeper,andobtainlong-livedreadandwritehandles
| 6.2 Parallelprocessing |     |           |     |        |            |       | tosendrequestsdirectlytoinstances. |         |          |               |     |                |     |
| ---------------------- | --- | --------- | --- | ------ | ---------- | ----- | ---------------------------------- | ------- | -------- | ------------- | --- | -------------- | --- |
|                        |     |           |     |        |            |       | Noria                              | handles | failures | by rebuilding |     | the data-flow. | If  |
| Noria shards           | the | data-flow | and | allows | concurrent | reads |                                    |         |          |               |     |                |     |
thecontrollerfails,Noriaelectsanewcontrollerthatre-
andwriteswithminimalsynchronizationforparallelism.
| Sharding.  |                   |           |      |          |             |           | storesthedata-flowgraph.Itthenstreamsthepersistent |            |         |           |            |                |      |
| ---------- | ----------------- | --------- | ---- | -------- | ----------- | --------- | -------------------------------------------------- | ---------- | ------- | --------- | ---------- | -------------- | ---- |
|            | Noria             | processes |      | updates  | in parallel | on a      |                                                    |            |         |           |            |                |      |
|            |                   |           |      |          |             |           | base table                                         | data from  | RocksDB |           | to rebuild | fully-stateful |      |
| cluster by | hash-partitioning |           | each | operator | on          | a key and |                                                    |            |         |           |            |                |      |
|            |                   |           |      |          |             |           | operators                                          | and views. | Partial | operators |            | are instead    | pop- |
assigningshardstodifferentservers.Eachmachineruns
|     |     |     |     |     |     |     | ulated through | on-demand |     | upqueries. |     | If individual | in- |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --------- | --- | ---------- | --- | ------------- | --- |
aNoriainstance,aprocessthatcontainsacompletecopy
stancesfail,Noriarebuildsonlytheaffectedoperators.
ofthedata-flowgraph,butholdsstateonlyforitsshards
6.4 MySQLadapter
ofeachoperator.Whenanoperatorwithonehashparti-
tioninglinkstoanoperatorwithadifferentpartitioning,
|     |     |     |     |     |     |     | Our prototype |     | includes | an  | implementation |     | of the |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | -------- | --- | -------------- | --- | ------ |
Noriainserts“shuffle”operatorsthatperforminter-shard
MySQLbinaryprotocolinadedicatedstatelessadapter
| transfers | over TCP | connections. |     | Upqueries | across | shuf- |     |     |     |     |     |     |     |
| --------- | -------- | ------------ | --- | --------- | ------ | ----- | --- | --- | --- | --- | --- | --- | --- |
thatappearsasastandardMySQLservertotheapplica-
| fle operators | are | expensive | since | they | must | contact all |     |     |     |     |     |     |     |
| ------------- | --- | --------- | ----- | ---- | ---- | ----------- | --- | --- | --- | --- | --- | --- | --- |
tion.Thisadapterallowsdeveloperstoeasilyrunexisting
ancestorshards.Thislimitsscalability,butallowsopera- applications on Noria. The adapter transparently trans-
torsbelowashuffletomaintainpartialstate.
latespreparedstatementsandad-hocqueriesintotransi-
Multicoreparallelism.Noriaachievesmulticorepar-
|          |             |        |     |     |         |            | tions on | Noria’s | data-flow, | and | applies | reads and | writes |
| -------- | ----------- | ------ | --- | --- | ------- | ---------- | -------- | ------- | ---------- | --- | ------- | --------- | ------ |
| allelism | within each | server | in  | two | ways: a | server can |          |         |            |     |         |           |        |
usingNoria’sAPIbehindthescenes.ItsSQLsupportis
| handle multiple |     | shards | by running |     | multiple | Noria in- |     |     |     |     |     |     |     |
| --------------- | --- | ------ | ---------- | --- | -------- | --------- | --- | --- | --- | --- | --- | --- | --- |
sufficientlycompletetorunsomeunmodifiedwebappli-
stances, and each instance runs multiple threads to pro- cations(e.g.,JConf[74]writteninDjango[22]),andto
cessitsshard.Eachinstancehastwothreadpools:data-
runLobsterswithminimalsyntaxadaptation.
flowworkersprocessupdateswithinthedata-flowgraph,
6.5 Limitations
andreadhandlershandlereadsfromexternalviews.
At most one data-flow worker executes updates for Ourcurrentprototypehassomelimitationsthatweplan
each data-flow operator at a time. This arrangement toaddressinfuturework;noneofthemarefundamental.
yields CPU parallelism among different operators, and First,itonlyshardsbyhashpartitioningonasinglecol-
also allows lock-free processing within each operator. umn, and resharding requires sending updates through
220    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

a single instance, which limits scalability. Second, it longcommithistory).Mostapplicationupdatesreduced
re-computes data-flow state on failure; recovering from tosingle-tableinserts,deletes,orupdates.
snapshots or data-flow replicas would be more efficient Limitations. Though applications traditionally use
(e.g.,usingselectiverollback[35]).Andthird,itdoesnot
|     |     |     |     |     |     |     | parameterized | queries | to avoid | SQL | injection | attacks |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ------- | -------- | --- | --------- | ------- |
currentlysupportrangeindicesormulti-columnjoins. andcachequeryplans,Noriaparameterizedqueriesalso
buildmaterializedviews.Anapplicationwithmanydis-
7 Applications
|     |     |     |     |     |     |     | tinct parameterized |     | queries | can thus end | up  | with more |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | ------- | ------------ | --- | --------- |
This section discusses our experiences with developing views than necessary. The developer can correct thisby
Noria applications. Noria aims to simplify the develop- addingsharedviews.Ourprototypedoesnotyetsupport
ment of high-performance web applications; several as- updateanddeleteoperationsconditionedonnon-primary
pectsofourimplementationhelpitachievethatgoal. keycolumns,andlackssupportforparameterizedrange
|     |     |     |     |     |     |     | (e.g., | age > | ?), |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | ----- | --- | --- | --- | --- |
First, applications written for a MySQL database can queries which some applications need.
use Noria directly via its MySQL adapter, provided Plannedsupportforrangeindexesandanextendedbase
tableimplementationwilladdresstheselimitations.
| they generate | parameterized |     |      | SQL queries |      | (for instance, |     |     |     |     |     |     |
| ------------- | ------------- | --- | ---- | ----------- | ---- | -------------- | --- | --- | --- | --- | --- | --- |
| via libraries | like          | PHP | Data | Objects     | [69] | or Python’s    |     |     |     |     |     |     |
8 Evaluation
MySQLconnector[55,§10.6.8]).Portingtypicallypro-
ceedsinthreesteps.First,thedeveloperpointstheappli-
|     |     |     |     |     |     |     | We evaluated | our Noria | prototype | using | backend | work- |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --------- | --------- | ----- | ------- | ----- |
cationattheNoriaMySQLadapterinsteadofaMySQL
loadsgeneratedfromtheproductionLobsterswebappli-
serverandimportsexistingdataintoNoriafromdatabase cation, as well as using individual queries. Our experi-
| dumps. | The application |     | will | immediately |     | see perfor- |     |     |     |     |     |     |
| ------ | --------------- | --- | ---- | ----------- | --- | ----------- | --- | --- | --- | --- | --- | --- |
mentsseektoanswerthefollowingquestions:
| mance improvements |     |     | for read | queries | that | formerly ran |         |             |       |            |         |       |
| ------------------ | --- | --- | -------- | ------- | ---- | ------------ | ------- | ----------- | ----- | ---------- | ------- | ----- |
|                    |     |     |          |         |      |              | 1. What | performance | gains | does Noria | deliver | for a |
substantialin-linecompute.ThoughtheMySQLadapter
typicaldatabase-backedwebapplication?(§8.1)
| even supports |             | ad-hoc   | read              | queries | (it transitions | the           |                 |                 |         |            |              |           |
| ------------- | ----------- | -------- | ----------------- | ------- | --------------- | ------------- | --------------- | --------------- | ------- | ---------- | ------------ | --------- |
|               |             |          |                   |         |                 |               | 2. How          | does Noria      | perform | compared   |              | to a      |
| data-flow     | as required |          | to support        | each    | query),         | the most      |                 |                 |         |            |              |           |
|               |             |          |                   |         |                 |               | MySQL/memcached |                 |         | stack, the | materialized |           |
| benefit       | will be     | seen for | frequently-reused |         |                 | queries. Sec- |                 |                 |         |            |              |           |
|               |             |          |                   |         |                 |               | views           | of a commercial |         | database,  | and an       | idealized |
| ond, the      | developer   | creates  | views             | for     | computations    | that          |                 |                 |         |            |              |           |
cache-onlydeployment?(§8.2)
| the MySQL | application |     | manually | materialized, |     | such as |     |     |     |     |     |     |
| --------- | ----------- | --- | -------- | ------------- | --- | ------- | --- | --- | --- | --- | --- | --- |
3. Givenascalableworkload,howdoesourprototype
| the per-story | vote | count | in  | Lobsters. | These | views co- |     |     |     |     |     |     |
| ------------- | ---- | ----- | --- | --------- | ----- | --------- | --- | --- | --- | --- | --- | --- |
utilizemultipleservers,andhowdoesitcompareto
| exist with | the manual |     | materializations, |     | and | allow exist- |     |     |     |     |     |     |
| ---------- | ---------- | --- | ----------------- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- |
astate-of-the-artdata-flowsystem?(§8.3)
ingqueriestocontinuetoworkasthedeveloperupdates
|             |         |         |              |          |           |             | 4. What | space overhead | does | Noria’s       | data-flow | state   |
| ----------- | ------- | ------- | ------------ | -------- | --------- | ----------- | ------- | -------------- | ---- | ------------- | --------- | ------- |
| the write   | path so | that    | it no longer | manually |           | updates de- |         |                |      |               |           |         |
|             |         |         |              |          |           |             | impose, | and how        | does | Noria perform | with      | limited |
| rived views | and     | caches. | Third,       | the      | developer | incremen-   |         |                |      |               |           |         |
memoryandpartialstate?(§8.4)
| tally rewrites | their | application |     | to rely | on  | natural views |     |     |     |     |     |     |
| -------------- | ----- | ----------- | --- | ------- | --- | ------------- | --- | --- | --- | --- | --- | --- |
5. CanNoriadata-flowsadapttonewqueriesandinput
| and remove | manual | write | optimizations. |     | These | changes |     |     |     |     |     |     |
| ---------- | ------ | ----- | -------------- | --- | ----- | ------- | --- | --- | --- | --- | --- | --- |
schemachangeswithoutdowntime?(§8.5)
graduallyincreaseapplicationperformanceasthedevel-
|     |     |     |     |     |     |     | Setup. | In all experiments, |     | Noria and | other | storage |
| --- | --- | --- | --- | --- | --- | --- | ------ | ------------------- | --- | --------- | ----- | ------- |
operremovesnow-unnecessarycomplexityfromtheap-
|     |     |     |     |     |     |     | backends | run on an | Amazon | EC2 c5.4xlarge |     | instance |
| --- | --- | --- | --- | --- | --- | --- | -------- | --------- | ------ | -------------- | --- | -------- |
plication’sreadandwritepaths.
|             |                 |         |        |             |      |           | with 16 vCPUs; | clients | run        | on separate | c5.4xlarge | in-        |
| ----------- | --------------- | ------- | ------ | ----------- | ---- | --------- | -------------- | ------- | ---------- | ----------- | ---------- | ---------- |
| The porting |                 | process | is not | burdensome. |      | We ported |                |         |            |             |            |            |
|             |                 |         |        |             |      |           | stances unless | stated  | otherwise. | Our setup   | is         | “partially |
| a PHP       | web application |         | for    | college     | room | ballots—  |                |         |            |             |            |            |
open-loop”:clientsgenerateloadaccordingtoaPoisson
| developed | by one | of  | the authors | and | used | production |     |     |     |     |     |     |
| --------- | ------ | --- | ----------- | --- | ---- | ---------- | --- | --- | --- | --- | --- | --- |
distributionofinterarrival-timesandhavealimitednum-
| for a decade—to |     | Noria; | the process |     | took two | evenings, |     |     |     |     |     |     |
| --------------- | --- | ------ | ----------- | --- | -------- | --------- | --- | --- | --- | --- | --- | --- |
berofbackendrequestsoutstanding,queueingadditional
| and required | changes |     | to four | queries. | We  | also used |     |     |     |     |     |     |
| ------------ | ------- | --- | ------- | -------- | --- | --------- | --- | --- | --- | --- | --- | --- |
requests.Thisensuresthatclientsmaintainthemeasure-
| the MySQL | adapter |     | to port | the Lobsters |     | application’s |     |     |     |     |     |     |
| --------- | ------- | --- | ------- | ------------ | --- | ------------- | --- | --- | --- | --- | --- | --- |
queriestoNoria;theresultisafocusofourevaluation. mentfrequencyevenduringperiodsofhighlatency[45].
Ourtestharnessmeasuresofferedrequestthroughputand
DevelopingnativeNoriaapplicationscanbeeveneas-
“sojourntime”[62],whichisthedelayfromrequestgen-
ier.Wedevelopedasimplewebapplicationtoshowthe
erationuntilaresponsereturnsfromthebackend.
| results of | our continuous |        | integration |         | (CI)      | tests for No- |     |     |     |     |     |     |
| ---------- | -------------- | ------ | ----------- | ------- | --------- | ------------- | --- | --- | --- | --- | --- | --- |
| ria. The   | CI system      | stores | its         | results | in Noria, | and the       |     |     |     |     |     |     |
8.1 Applicationperformance:Lobsters
webapplicationdisplaysperformanceresultsandaggre-
gatestatistics.SincewedevelopeddirectlyforNoria,we WefirstevaluateNoria’sperformanceonarealisticweb
were not tempted to cache intermediate results or ap- applicationworkloadtoanswertwoquestions:
ply other manual optimizations, and could use aggrega- 1. Do Noria’s fast reads help it outperform a conven-
tions and joins in queries without fear that performance tionaldatabaseonarealapplicationworkload,even
wouldsufferasaresult(e.g.,duetoaggregationsoverthe
onahand-optimizedapplication?
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    221

|     |                     |     |                   |     |                  |     | The baseline   |     | queries  | manually | pre-compute      |     | aggre-  |
| --- | ------------------- | --- | ----------------- | --- | ---------------- | --- | -------------- | --- | -------- | -------- | ---------------- | --- | ------- |
|     | MariaDB,baselinequ. |     | Noria,baselinequ. |     | Noria,naturalqu. |     |                |     |          |          |                  |     |         |
|     |                     |     |                   |     |                  |     | gates. MariaDB |     | requires | this     | for performance: |     | without |
100
thepre-computation,itsupportsjust20pages/sec.Noria
]sm[ycnetaL 80 instead maintains pre-computed aggregates in its data-
|     | 60  |     |     |     |     |     | flow.Thisallowsustoincludetheaggregationsdirectly |     |       |            |          |       |         |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | ----- | ---------- | -------- | ----- | ------- |
|     |     |     |     |     |     |     | in the queries,                                   |     | which | normalizes | the base | table | schema, |
40
|     |     |     |     |     |     |     | reduces | write load, | and | avoids | bugs due | to  | missed up- |
| --- | --- | --- | --- | --- | --- | --- | ------- | ----------- | --- | ------ | -------- | --- | ---------- |
20
datestopre-computedvalues.Withallaggregatecompu-
|     | 0   |     |     |     |     |     | tation moved | into | Noria’s | data-flow | (“natural |     | queries”), |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ---- | ------- | --------- | --------- | --- | ---------- |
|     | 0   | 1K  | 2K  | 3K  | 4K  | 5K  |              |      |         |           |           |     |            |
throughputscaleshigherstill,to5,000pages/second(5
|     |     | Offeredload[pageviews/sec] |     |     |     |     |           |             |     |             |                 |     | ×   |
| --- | --- | -------------------------- | --- | --- | --- | --- | --------- | ----------- | --- | ----------- | --------------- | --- | --- |
|     |     |                            |     |     |     |     | MariaDB). | Eliminating |     | application | pre-computation |     | re- |
Figure 6: Noria scales Lobsters to a 5 higher load duces overall write load and compacts the data-flow,
×
thanMariaDB(2.3 withbaselinequeries)atsub-100ms whichletsNoriaparallelizeitmoreeffectively.
×
95%ilelatency(dashed:median).MariaDBislimitedby
|     |     |     |     |     |     |     | The result | is  | that Noria | achieves | both | good | perfor- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ---------- | -------- | ---- | ---- | ------- |
readcomputation,whileNoriabecomeswrite-bound.
|     |     |     |     |     |     |     | mance and | natural, | robust | queries. | We  | observed | similar |
| --- | --- | --- | --- | --- | --- | --- | --------- | -------- | ------ | -------- | --- | -------- | ------- |
(e.g.,
|     |     |     |     |     |     |     | benefits | with other | applications |     |     | a synthetic | TPC- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ------------ | --- | --- | ----------- | ---- |
2. CanNoriapreservegoodperformanceforanappli- W-likeworkload),whichweomitforspace.
cationwithouthandoptimization?
Our workload models production Lobsters traffic. The 8.2 In-depthperformancecomparison
| benchmark |     | emulates | authenticated | Lobsters | users | vis- |     |     |     |     |     |     |     |
| --------- | --- | -------- | ------------- | -------- | ----- | ---- | --- | --- | --- | --- | --- | --- | --- |
iting different pages according to the access frequen- We compare to alternative systems using a subset of
|     |     |     |     |     |     |     | Lobsters. | This | restriction | gives | us better | control | over |
| --- | --- | --- | --- | --- | --- | --- | --------- | ---- | ----------- | ----- | --------- | ------- | ---- |
ciesandpopularitydistributionsintheproductionwork-
load [32]. Lobsters is a Ruby-on-Rails application, but workloadproperties,whilecapturingtheaspectsofweb
|     |     |     |     |     |     |     | workloads | that | motivated | the | Noria design. | We  | use one |
| --- | --- | --- | --- | --- | --- | --- | --------- | ---- | --------- | --- | ------------- | --- | ------- |
ourbenchmarkgeneratesdatabaseoperationsdirectlyin
ordertoeliminateRailsoverhead.Weseedthedatabase kind of write, inserting a vote, and one read query,
with 9.2k users, 40k stories and 120k comments—the StoriesWithVCfromFigure2.Thisreadqueryfetches
storiesandtheirvotecounts;85%ofpageviewsinpro-
sizeoftherealLobstersdeployment—andrunincreasing
requestloadstopushthedifferentsetupstotheirlimits. ductionLobstersareforpagesthatexecutethisquery.
ThebaselinequeriesincludetheLobstersdevelopers’ We compare five single-server deployments that all
optimizations,whichmanuallymaterializeandmaintain haveaccesstothesameresources,butdifferinhowthey
aggregate values like vote counts to reduce read-side MariaDB
|     |     |     |     |     |     |     | store and | calculate | the | per-story | vote | count. |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | --------- | --- | --------- | ---- | ------ | --- |
work.Wealsodeveloped“natural”queriesthatproduce uses the baseline Lobsters approach of pre-computing
the same results using Noria data-flow to compute ag- and storing vote counts in a column of the Lob-
gregations rather than manual optimizations. We com- sters stories table. System Z, a commercial database
pare MariaDB (a community-developed MySQL fork; with materialized view support, uses an incrementally-
| v10.1.34) | with | Noria | using baseline |     | queries, and | then |            |              |     |      |         |           |     |
| --------- | ---- | ----- | -------------- | --- | ------------ | ---- | ---------- | ------------ | --- | ---- | ------- | --------- | --- |
|           |      |       |                |     |              |      | maintained | materialized |     | view | defined | similarly | to  |
toNoriausingnaturalqueries(bothviaNoria’sMySQL StoriesWithVC;weuseSystemZtocomparedatabase
adapter). We configured MariaDB to use a thread pool, view maintenance with Noria’s data-flow-based ap-
to avoid flushing to disk after transactions, and to store proach.MariaDBandSystemZrunatthefastesttransac-
thedatabaseonaramdisktoremoveoverheadsunrelated tionalisolationlevel(“readuncommitted”)andarecon-
toqueryexecution.Withthebaselinequeries,themedian figuredtokeepdatainmemory.MariaDB+memcached
pageviewexecutes11queries;thisreducestoeightwith adds a demand-filled memcached (v1.5.6) cache [54]
natural queries. This experiment uses an m5.24xlarge to MariaDB that caches StoryWithVC entries. This re-
EC2instancefortheCPU-intensiveclients. duces read load on MariaDB, but complicates applica-
Figure 6 shows the results as throughput-latency tioncodeevenbeyondpre-computation:writesmustin-
curves.Anidealsystemwouldshowasahorizontalline validatethecacheandreadsmustsometimespopulateit.
with low latency; in reality, each setup hits a “hockey We also measure memcached-only without a relational
stick” once it fails to keep up with the offered load. backend.Thissetupoffersgoodperformance,butisun-
MariaDB scales to 1,000 pages/second, after which it realistic: it does not store individual votes or stories, is
saturates all 16 CPU cores with read-side computation notpersistent,andcannotpreventdouble-voting.Ithelps
(e.g., for per-page notification counts [33]). Noria run- us estimate how a backend that serves all reads from
ning the same baseline queries scales to a 2.3 higher memory and does minimal work for writes might per-
×
offeredload,sinceitsincrementalwrite-sideprocessing form. Finally, we measure Noria sharded four ways on
stories.id,withtheremaining12coresservingreads.
avoidsredundantre-computationonreads.
222    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

100
50
0
0 2M 4M 6M 8M 10M 12M 14M
Offeredload[requests/sec]
]sm[ycnetaleli-%59 MariaDB(hand-opt.) 100
SystemZ
MariaDB+memcached
memcached-only 50
Noria(4shards)
0
0 2M 4M 6M 8M 10M 12M 14M
Offeredload[requests/sec]
(a) Read-heavy workload (95%/5%): Noria outperforms all
othersystems(allbutmemcachedat100–200krequests/sec).
]sm[ycnetaleli-%59 MariaDB(hand-opt.)
SystemZ
MariaDB+memcached
memcached-only
Noria(4shards)
(b)Mixedread-writeworkload(50%/50%):Noriaoutperforms
allsystemsbutmemcached(othersareat20krequests/sec).
Figure 7: A Lobsters subset (Figure 2) benchmarked on Noria hand-optimized MariaDB, System Z’s materialized
views,aMariaDB/memcachedsetup,andonmemcachedonly,allwithZipf-distributed(s=1.08)readsandvotes.
100
50
0
0 2M 4M 6M 8M 10M 12M 14M
Offeredload[requests/sec]
]sm[ycnetaleli-%59
s/second with four shards. Noria also handles a write-
MariaDB(hand-opt.) heavyworkload(50%writes)well(Figure7b):although
SystemZ absolute performance has dropped, Noria still outper-
MariaDB+memcached formsallothersystemsapartfromthecache-onlysetup.
memcached-only This is because sharding allows data-parallel write pro-
Noria(4shards) cessing,whichhelpsNoriascaleto2Mrequests/second.
With a (less-realistic) uniform workload, other
systems come closer to Noria’s 5M requests/second
(Figure 8). System Z does better than before, but
suffers from slow writes to the materialized view.
Figure 8: For a uniformly-distributed, read-heavy
MariaDB+memcached, perhaps surprisingly, performs
(95%/5%) workload on Figure 2, Noria performs simi-
worse than MariaDB, which scales to 3M requests/sec-
larlytothe(unrealistic)memcached-onlysetup.
ond:thereasonliesintheextrawork(andRPCs)theap-
plicationmustperformforinvalidations.Thisillustrates
Noriausesnaturalqueries;othersystemsexceptSystem that a look-aside cache only helps if it avoid expensive
Zmanuallypre-computevotecounts. queries; a write-through cache avoids invalidation over-
heads, but would still perform worse than the idealized
Clientsreadandinsertvotesforrandomly-chosensto-
memcached-onlysetup(andthus,thanNoria).
ries;wemeasurethe95th-percentilelatencyforeachof-
feredload.Beforemeasurementbegins,wepopulatethe Separately, we evaluated Noria’s view maintenance
stories table with 500k records and perform 40 sec- against DBToaster [2, 53], a state-of-the-art material-
ondsofwarmupusingthesameworkloadasthebench- ized view maintenance system that compiles view def-
mark itself. Absolute throughput is higher in these ex- initions to native code. DBToaster (v2.2.3387) lacks
periments because the data-flow only contains a single support for persistent base tables, concurrent reads, or
queryandclientsbatchreadsandwritesforupto1ms. multicore parallelism—its only read operation snap-
Figure 7 shows results for a skewed workload simi- shots entire views—but it does provide fast updates
lar to Lobsters’, with story popularity following a Zip- to materialized views. When we constrain Noria to
fian distribution (s = 1.08). With 95% reads, Noria only one shard and data-flow worker thread, we expect
outperforms all other systems, including the unrealis- DBToastertooutperformit,sinceDBToaster’sgenerated
tic cache-only deployment (Figure 7a). Most updates C++ code does close-to-minimal work to incrementally
write votes for popular stories, which creates write maintainthevotecount.Wemeasurethewritethrough-
contention problems in MariaDB and System Z. The put of 50M uniformly-distributed votes that update
MariaDB+memcached setup performs equally poorly: StoriesWithVC for 500k stories. Noria achieves 240k
on memcached invalidations for popular keys, multiple single-recordwrites/secondforfully-populatedstate,and
clients miss and a “thundering herd” of clients simulta- 1Mwrites/secondforfully-evictedstate.DBToasteronly
neouslyissuesdatabasequeries[54,§3.2.1].memcached supportsfully-populatedstate,andachieves520ksingle-
on its own scales, but Noria outperforms it (despite do- record writes/second. At the same time, Noria is more
ingmorework)sinceNoria’slocklessviewsavoidcon- memory-efficient, using 6.2 GB of memory for base ta-
tention for popular keys. Noria scales to 14M request- bles and all derived state, 36% of DBToaster’s 17 GB.
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 223

|     |     |     |     |     |     |     | overhead | as the | number | of machines | grows. | DD  | amor- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------ | ------ | ----------- | ------ | --- | ----- |
]ces/qer[tuphguorhT 30M tizes this coordination by increasing its batch size, and
DifferentialDataflow
|     |     | Noria |     |     |     |     | consequently | sees | increased | latency | as  | throughput | in- |
| --- | --- | ----- | --- | --- | --- | --- | ------------ | ---- | --------- | ------- | --- | ---------- | --- |
20M
creases.Noriaavoidssuchcoordinationandscaleswell,
butoffersonlyeventually-consistentreads.
10M
|     |     |     |     |     |     |     | 8.4 Statesize |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- |
0
Noriareliesonpartialstatetokeepitsmemoryfootprint
|     | 1   | 2   | 3 4 | 5 6 7 | 8   | 9 10 |     |     |     |     |     |     |     |
| --- | --- | --- | --- | ----- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
low.HowmuchofNoria’sstateforLobsterscanbepar-
Numberofmachines
tial,andhowdoesNoriaperformwhenitevictsfrompar-
Figure9:Forauniform95%/5%workload,Noriascales tial state to meet a memory limit? We investigate these
questionsusingthefullLobstersapplication,firstatLob-
| to ten machines |     | with | sub-100ms | 95th %tile | latency | by  |     |     |     |     |     |     |     |
| --------------- | --- | ---- | --------- | ---------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
sharding the data-flow. Differential dataflow [44] scales stersproductionscale,andthenat10 scale.
×
lesswellduetoitsinter-workercoordination. The Noria data-flow for the natural Lobsters queries
has235operators,ofwhich60ofarestateful.Withpar-
|     |     |     |     |     |     |     | tial state | disabled, | i.e., | forcing | all data-flow | operators |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --------- | ----- | ------- | ------------- | --------- | --- |
Additionally,Noriacanprocessshardsinparallelanduse
moremachinestoincreasethroughput. to keep full state, Noria needs 789 MB of in-memory
|                                     |     |     |     |     |     |     | state (8 | the base | table | size | of 137 MB). | With | partial |
| ----------------------------------- | --- | --- | --- | --- | --- | --- | -------- | -------- | ----- | ---- | ----------- | ---- | ------- |
| 8.3 Distributionovermultipleservers |     |     |     |     |     |     | ×        |          |       |      |             |      |         |
stateenabled,35ofthestatefuloperatorscanusepartial
We next evaluate Noria’s support for distributed opera- state;theremaining25arepartofunparameterizedviews
tion. Can Noria effectively use multiple machines’ re- (e.g.,allstoriesonthefrontpage)whosestateNoriacan-
sourcesgivenascalableworkload? not make partial as they lack suitable keys. Together,
We evaluate the 95%-read Lobsters subset from §8.2 the non-partial state occupies 73 MB: Noria’s essential
|          |         |          |     |           |           |     | memory | requirement | for | Lobsters | therefore | amounts | to  |
| -------- | ------- | -------- | --- | --------- | --------- | --- | ------ | ----------- | --- | -------- | --------- | ------- | --- |
| with two | million | stories. | We  | shard the | data-flow | on  |        |             |     |          |           |         |     |
stories.idandvarythenumberofmachinesfromone 9%oftotalstate(addinganoverheadof53%ofbaseta-
toten,witheachmachinehostingfourshards.Forade- blesize).Noriacanevictandre-computetheremaining
91%ofstateshoulditexceedamemorylimit.
ploymentwithnNoriamachines,wescaleclientloadto
n 3Mrequests/secondinapartiallyopen-looptesthar- As for any cache, this memory limit should exceed
| ×          |             |     |          |          |         |       | the application’s |     | working | set | size to achieve | low | read |
| ---------- | ----------- | --- | -------- | -------- | ------- | ----- | ----------------- | --- | ------- | --- | --------------- | --- | ---- |
| ness. This | arrangement |     | achieves | close to | Noria’s | maxi- |                   |     |         |     |                 |     |      |
mum load atsub-100ms 95th-percentile latency fortwo latency and avoid thrashing of evictions and upqueries.
million stories on one machine. Load generators select For Lobsters, the working set size depends on the of-
storiesuniformlyatrandom,sotheworkloadisperfectly fered load, as higher load means a wider range of sto-
shardable.Theidealresultisastraightdiagonal,withn ries are read. We determine it by varying Noria’s state
|          |           | n   |       |                |     |          | size limit | (and | hence, | eviction | frequency) | and measur- |     |
| -------- | --------- | --- | ----- | -------------- | --- | -------- | ---------- | ---- | ------ | -------- | ---------- | ----------- | --- |
| machines | achieving |     | times | the throughput | of  | a single |            |      |        |          |            |             |     |
one. Figure 9 shows that Noria achieves this and serves ing 95th-percentile read latency. With production-scale
thefullper-machineloadatallpoints. Lobsters data, Noria’s working set contains 525 MB of
We also implemented this benchmark for a state- state(60%oftotal,3.8 basetables)atanofferedloadof
×
of-the-art Differential Dataflow (DD) implementation 2,300pages/second.However,withafewthousandusers,
theproductionLobstersdeploymentissmall.Ourbench-
(v0.7)inRust[44]basedonNaiadanditsearlierversion
ofDD[46,51].SinceDDlacksaclient-facingRPCin- markfurtherunderstatesitssizeasweusesyntheticstory
terface,weco-locateDDclientswithworkers;thisdoes and comment texts of a few bytes. Hence, we repeated
notdisadvantageDDsinceloadgenerationischeapcom- thisexperimentwiththeLobstersdatascaledupby10 .
×
paredtoRPCprocessing.DDuses12workerthreadsand Noriameetssub-100ms95thpercentilelatencyat2,300
|     |     |     |     |     |     |     | pages/second | if  | the memory | limit | exceeds | the | 2.6 GB |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ---------- | ----- | ------- | --- | ------ |
fournetworkthreadspermachine.
Figure9showsthatNoriaiscompetitivewithDDon workingset(38%of7GBtotalstate;3 basetables).
×
thisbenchmark.Ononeandtwomachines,DDsupports TheseresultssuggestthatNoriaimposesareasonable
a slightly higher per-machine load (3.5M requests/sec- spaceoverhead(around3 basetablesize)forLobsters,
×
ond vs. Noria’s 3M) within our 95th-percentile latency andthatpartialstateiskeytoreducingtheoverhead.
| budget   | of 100ms. | Beyond  | four    | machines,   | however, | DD        |                             |     |     |     |     |     |     |
| -------- | --------- | ------- | ------- | ----------- | -------- | --------- | --------------------------- | --- | --- | --- | --- | --- | --- |
|          |           |         |         |             |          |           | 8.5 Livedata-flowadaptation |     |     |     |     |     |     |
| fails to | meet      | Noria’s | maximum | per-machine |          | load. Its |                             |     |     |     |     |     |     |
supported throughputtails off toaround 20M requests/- In a traditional database, query changes are easy and
secattenmachines.Thistail-offisduetoDD’sprogress- instantaneous. Can Noria’s data-flow adaptation seam-
trackingprotocol,whichcoordinatesbetweenworkersto lessly transition to include new SQL expressions? The
exposewritesatomically,andwhichimposesincreasing goal is for the transition to complete quickly, for write
224    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

300K
200K
100K
0
tuphguorhT
Totalwritethroughput %fastreadsfromnewview
100%
0%
(a)Withpartialmaterializationandreuse(Zipfian).
300K
200K
100K
0
tuphguorhT
100%
0%
(b)Withpartialmaterializationandreuse(uniform).
300K
200K
100K
0
tuphguorhT
ria to serve the majority of rating reads without recur-
sive upqueries. Reuse is also crucial: without reusing
VoteCount, Noria must upquery rating reads by re-
computing from the base tables. This leads to slow up-
queries for popular stories, as the data-flow must re-
counttheirvotes.Withreuseenabled,pre-computedvote
countssatisfytheupqueries.Theresultsalsofollowthis
pattern for a uniform workload (Figure 10b). Initially,
mostratingreadsareslow,butfastreadsincreaseasthe
partial state populates; write throughput is reduced be-
causedata-flowupdatescontendwithupqueryresponses.
Contention increases as more entries populate, since
fewerupdateshitevictedstate.
Figure 10c shows the same transition (with a Zip-
fian workload), but with partial materialization and
100% operator reuse disabled. Noria fully populates the
15 0 30 60 90 0% StoriesWithRatings view and all internal stateful
− operators during the transition. It copies votes and
Timeaftertransitionstart[sec]
stories to bootstrap the rating aggregation state, and
(c)Noreuseorpartialmaterialization(Zipfian).
then copies the resulting state again to initialize the
new external view. Each copy stops write processing
Figure 10: Reuse and partial state allow Noria to adapt
for several seconds, and Noria’s state transfer to the
thelivedata-flow.Graylinesdelimitstartandendofthe
new operators via the data-flow slows down concurrent
transition (in (a) and (b), the transitions are almost in-
writes. When transition completes after 25 seconds, the
stantaneous);thegreenshadedareashowsthefractionof
StoriesWithRatingsviewisfullymaterializedandall
newviewreadsthatrequirenoupqueries.Readsfromthe
ratingreadsarefast.Thisillustratesthatpartialstateand
oldview(notshown)proceedatfullspeedthroughout.
reusearecrucialfordowntime-freedata-flowtransitions.
How often can Noria achieve a live transition in
performance to remain stable, for reads from existing
practice? In a separate analysis of query and schema
viewstobeunaffected,andforreadsfromnewly-added
changes in HotCRP and TPC-W, we found that Noria
viewstoquicklyachievelowlatency.
live-transitioned for over 95% of program changes. Ex-
We test this by adding a modified version of the
istingapproachesarelessflexible:SystemZmustrebuild
StoriesWithVC view to the Lobsters subset. This
its materialized views on change; a memcached clus-
new view, StoriesWithRatings, uses numeric rat-
ter mustbe carefully transitioned [54, §4.3];DBToaster
ings stored in a ratings base table instead of votes.
lacks support for query changes; and even relational
It also reflects old votes scaled to a rating. We first
databasespausewritesduringsomeschemaupdates.
load an unsharded Noria with 2M stories and 30M
votes, then transition to the new program. Once the 8.6 Discussion
transition finishes, clients perform “rating reads” from
StoriesWithRatings and start writing to the new We evaluated Lobsters both at production scale and at
ratings table. Throughout the experiment, clients 10 scale, but many web applications are much larger
×
also read the StoriesWithVC view, and write to the still. We believe that Noria can also support such appli-
votes table. We expect post-transition throughput to cations. For applications with many queries, and conse-
be reduced—the new data-flow graph is larger, with quentlyalargedata-flow,Noriacanassignshardsofonly
more tables and deeper paths—although removing the someoperatorstoeachmachine,sendingcross-operator
oldviewwouldincreasethroughputagain.However,we trafficoverthenetwork.Similarly,Noriacanshardlarge
hope that throughput and latency do not suffer greatly base tables and operators with large state across ma-
duringthetransition. chines. Efficient resharding and partitioning the data-
Figure 10a shows the transition with reuse and par- flowtominimizenetworktransfersareimportantfuture
tialmaterializationenabled.Thetransitioncompletesim- workforNoriatoachievetrulylargescale.
mediately: Noria creates the new operators and view as We also believe Noria is well suited for applications
empty, and populates them on demand in response to whoseworkingsetschangeovertime.Manylarge,real-
reads. Due to the skewed read and write distributions, worldapplicationsseesuchchangingworkloads;forin-
upqueries for only a few popular keys suffice for No- stance, an old story may suddenly become popular. As
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 225

clientsrequestsuchitems,Noria’supqueriesbringthem quodislimitedtostaticqueries,andunlikeNoria,neither
intotheworkingset,makingsubsequentreadsfast. sharesstatenorprocessingacrossqueries.
|     |     |     |     |     |     |     | The | problem | of  | detecting | shared | subexpressions |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --------- | ------ | -------------- | --- |
9 Relatedwork
|     |     |     |     |     |     |     | (§5.1) is | a multi-query |     | optimization |     |     | (MQO) prob- |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------------- | --- | ------------ | --- | --- | ----------- |
Noriabuildsonconsiderablerelatedwork. lem[21,59,78].MQOtriestomaximizesharingacross
Data-flow systems excel at data-parallel comput- a batch of expressions, with the freedom to rewrite any
|     |     |     |     |     |     |     | expression | to suit | the | others. | Like | joint query | process- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------- | --- | ------- | ---- | ----------- | -------- |
ing[36,51],includingonstreams,butcannotserveweb
applications directly. They only achieve low-latency in- ingsystems[10,25,31],Noriafacesthemorerestricted
|     |     |     |     |     |     |     | problem | of mutating |     | new expressions |     | to  | increase their |
| --- | --- | --- | --- | --- | --- | --- | ------- | ----------- | --- | --------------- | --- | --- | -------------- |
crementalupdatesattheexpenseofwindowedstate(and
opportunitytoshareexistingexpressionsinthedata-flow.
| incomplete | results) | or  | by keeping | full | state in | memory. |     |     |     |     |     |     |     |
| ---------- | -------- | --- | ---------- | ---- | -------- | ------- | --- | --- | --- | --- | --- | --- | --- |
Noria’spartially-statefuldata-flowliftsthisrestriction.A A wide array of tools deal with websites’ query and
|     |     |     |     |     |     |     | schema | transitions | [9, | 23, | 26, 56, | 65]. | Like Noria, |
| --- | --- | --- | --- | --- | --- | --- | ------ | ----------- | --- | --- | ------- | ---- | ----------- |
fewdata-flowsystemscanreuseoperatorsautomatically:
for example, Nectar [28] detects similar subexpressions they aim to transition backend stores without interrup-
|              |        |           |                    |     |         |           | tion in  | client    | service, | but | they require |         | developers to |
| ------------ | ------ | --------- | ------------------ | --- | ------- | --------- | -------- | --------- | -------- | --- | ------------ | ------- | ------------- |
| in DryadLINQ |        | programs, | similar            | to  | Noria’s | automated |          |           |          |     |              |         |               |
|              |        |           |                    |     |         |           | manually | configure | complex  |     | “ghost       | tables” | or binlog-    |
| operator     | reuse, | using     | DryadLINQ-specific |     |         | merge and |          |           |          |     |              |         |               |
rewriterules.Supportfordynamicchangestoarunning following triggers. Base table schema changes increase
|           |         |         |      |      |             |     | complexity | further | [73]. | Noria | handles | query | changes |
| --------- | ------- | ------- | ---- | ---- | ----------- | --- | ---------- | ------- | ----- | ----- | ------- | ----- | ------- |
| data-flow | is more | common: | CIEL | [52] | dynamically | ex- |            |         |       |       |         |       |         |
tends batch-processing data-flows, as does Ray [58] for transparently,andefficientlyappliescommonbasetable
schemachangesbysupportingmanyconcurrentbaseta-
| stateful | “actor” | operators’ | state | transitions | in  | reinforce- |     |     |     |     |     |     |     |
| -------- | ------- | ---------- | ----- | ----------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
bleschemas.Mostofitsdata-flowtransitionsarelivefor
| ment learning | applications. |     | Noria | dynamically |     | changes |     |     |     |     |     |     |     |
| ------------- | ------------- | --- | ----- | ----------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
long-running, low-latency streaming computations by readsandwriteswithoutaddedcomplexity.
|     |     |     |     |     |     |     | Finally, | some | open-source |     | systems |     | have experi- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---- | ----------- | --- | ------- | --- | ------------ |
modifyingthedata-flow;unlikeexistingstreamingdata-
flowsystemslikeNaiad[51]orSparkStreaming[76],it mentedwithflexiblequeryandschemachanges.Apache
hasnoneedforarestartorrecoveryfromacheckpoint. Kafka[5]achievessomeflexibilityinqueryandschema
|        |            |     |         |         |         |           | changes | as used | by the | New | York | Times | [68], and sim- |
| ------ | ---------- | --- | ------- | ------- | ------- | --------- | ------- | ------- | ------ | --- | ---- | ----- | -------------- |
| Stream | processing |     | systems | [3, 11, | 39, 71, | 76] often |         |         |        |     |      |       |                |
usedata-flow,butusuallyhavewindowedstateandstatic ilar ideas were proposed as an extension proposal for
|         |              |     |          |          |        |     | Samza [38]. | To  | our knowledge, |     | however, |     | no prior sys- |
| ------- | ------------ | --- | -------- | -------- | ------ | --- | ----------- | --- | -------------- | --- | -------- | --- | ------------- |
| queries | that process |     | only new | records. | STREAM | [6] |             |     |                |     |          |     |               |
identifies opportunities for operator reuse among static temachievestheperformanceandflexibilityofNoria.
| queries; | Noria | achieves | similar | reuse | for | dynamic | 10 Conclusions |     |     |     |     |     |     |
| -------- | ----- | -------- | ------- | ----- | --- | ------- | -------------- | --- | --- | --- | --- | --- | --- |
queries.S-Store[47]lacksNoria’spartialmaterialization
|           |        |              |     |           |          |        | Noria is    | a web | application |     | backend        | that | delivers high |
| --------- | ------ | ------------ | --- | --------- | -------- | ------ | ----------- | ----- | ----------- | --- | -------------- | ---- | ------------- |
| and state | reuse, | but combines |     | a classic | database | with a |             |       |             |     |                |      |               |
|           |        |              |     |           |          |        | performance | while | allowing    |     | for simplified |      | application   |
streamprocessingsystemusingtrigger-basedviewmain-
|          |         |         |               |     |             |       | logic. Partially-stateful |     |     | data-flow | is  | essential | to achiev- |
| -------- | ------- | ------- | ------------- | --- | ----------- | ----- | ------------------------- | --- | --- | --------- | --- | --------- | ---------- |
| tenance. | S-Store | enables | transactional |     | processing, | a fu- |                           |     |     |           |     |           |            |
ingthisgoal:itallowsfastreads,restrictsNoria’smem-
turegoalforNoria.
|          |              |     |       |      |          |         | ory footprint | to  | state          | that is | actually  | used, | and enables |
| -------- | ------------ | --- | ----- | ---- | -------- | ------- | ------------- | --- | -------------- | ------- | --------- | ----- | ----------- |
| Database | materialized |     | views | [29, | 41] were | devised |               |     |                |         |           |       |             |
|          |              |     |       |      |          |         | live changes  | to  | the data-flow. |         | In future | work, | we plan     |
tocacheexpensiveanalyticalqueryresults.Commercial
|            |              |     |      |         |                |      | toadd moreflexible |     | sharding,range |     |     | indexes,andbetter |     |
| ---------- | ------------ | --- | ---- | ------- | -------------- | ---- | ------------------ | --- | -------------- | --- | --- | ----------------- | --- |
| databases’ | materialized |     | view | support | [1] is limited | [49, |                    |     |                |     |     |                   |     |
evictionstrategies.
| 63] and | views must | usually | be  | rebuilt | on change. | How- |     |     |     |     |     |     |     |
| ------- | ---------- | ------- | --- | ------- | ---------- | ---- | --- | --- | --- | --- | --- | --- | --- |
Noriaisopen-sourcesoftwareandavailableat:
ever,thereisconsiderableresearchonincrementalview
maintenance in databases [30, 40, 41, 70, 77, 81]. No- https://pdos.csail.mit.edu/noria
| ria builds | upon | ideas | from this | work, | but applies | them |     |     |     |     |     |     |     |
| ---------- | ---- | ----- | --------- | ----- | ----------- | ---- | --- | --- | --- | --- | --- | --- | --- |
Acknowledgements
inthecontextofaconcurrent,statefuldata-flowsystem
forwebapplications.Thisrequiresefficientfine-grained We thank Joana da Trindade and Nikhil Benesch for
accesstoviews,solutionstonewcoordinationproblems contributions to our implementation, as well as Frank
andconcurrencyraces,aswellasinexpensivelong-term McSherry for assisting with implementation and tuning
adaptationasviewdefinitionschange.DBToaster[2,53] ofthedifferentialdataflowbenchmark.JonHowellpro-
supportsincrementalviewmaintenanceunderhighwrite vided helpful feedback that much improved the paper,
loads with generated recursive delta query implemen- as did Ionel Gog, Frank McSherry, David DeWitt, Sam
tations. Noria sees lower single-threaded performance, Madden, Amy Ousterhout, Tej Chajed, Anish Athalye,
but supports parallel processing and changing queries; andthePDOSandDatabasegroupsatMIT.Wearealso
addingnative-codegenerationtoNoriamightfurtherim- grateful to the helpful comments we received from our
prove its performance, but would complicate operator anonymousreviewers,aswellasfromWyattLloyd,our
reuse.Pequod[37]andDBProxy[4]supportpartialma- shepherd. This work was funded through NSF awards
terializationinresponsetoclientdemand,althoughPe-
CSR-1301934,CSR-1704172,andCSR-1704376.
226    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

References YeeJiunSong,andVenkatVenkataramani.“TAO:
Facebook’s Distributed Data Store for the Social
[1] SanjayAgrawal,SurajitChaudhuri,andVivekR.
Graph”. In: Proceedings of the USENIX Annual
Narasayya.“AutomatedSelectionofMaterialized
TechnicalConference.SanJose,California,USA,
Views and Indexes in SQL Databases”. In: Pro-
ceedings of the 26th International Conference on June2013,pages49–60.
Very Large Data Bases (VLDB). Cairo, Egypt, [9] Mark Callaghan. Online Schema Change for
Sept.2000,pages496–505. MySQL. URL: https://www.facebook.com/
note.php?note_id=430801045932(visitedon
[2] Yanif Ahmad, Oliver Kennedy, Christoph Koch,
02/01/2017).
and Milos Nikolic. “DBToaster: Higher-order
Delta Processing for Dynamic, Frequently Fresh [10] George Candea, Neoklis Polyzotis, and Radek
Views”.In:ProceedingsoftheVLDBEndowment Vingralek. “A Scalable, Predictable Join Opera-
5.10(June2012),pages968–979. tor for Highly Concurrent Data Warehouses”. In:
Proceedings of the VLDB Endowment 2.1 (Aug.
[3] Tyler Akidau, Alex Balikov, Kaya Bekirog˘lu,
2009),pages277–288.
Slava Chernyak, Josh Haberman, Reuven Lax,
SamMcVeety,DanielMills,PaulNordstrom,and [11] Paris Carbone, Stephan Ewen, Seif Haridi, As-
Sam Whittle. “MillWheel: Fault-tolerant Stream terios Katsifodimos, Volker Markl, and Kostas
Processing at Internet Scale”. In: Proceedings Tzoumas. “Apache Flink: Stream and batch pro-
of the VLDB Endowment 6.11 (Aug. 2013), cessing in a single engine”. In: IEEE Data Engi-
pages1033–1044. neering38.4(Dec.2015).
[4] Khalil Amiri, Sanghyun Park, Renu Tewari, and [12] FayChang,JeffreyDean,SanjayGhemawat,Wil-
SriramPadmanabhan.“DBProxy:adynamicdata son C. Hsieh, Deborah A. Wallach, Mike Bur-
cache for web applications”. In: Proceedings of rows,TusharChandra,AndrewFikes,andRobert
the 19th International Conference on Data Engi- E. Gruber. “Bigtable: A Distributed Storage Sys-
neering(ICDE).Mar.2003,pages821–831. tem for Structured Data”. In: Proceedings of the
7thUSENIXSymposiumonOperatingSystemDe-
[5] Apache Software Foundation. Apache Kafka: a
sign and Implementation (OSDI). Seattle, Wash-
distributed streaming platform. URL: http://
ington,USA,Nov.2006.
kafka.apache.org/(visitedon09/14/2017).
[13] Guoqiang Jerry Chen, Janet L. Wiener, Shrid-
[6] Arvind Arasu, Brian Babcock, Shivnath Babu,
har Iyer, Anshul Jaiswal, Ran Lei, Nikhil Simha,
John Cieslewicz, Mayur Datar, Keith Ito, Ra-
Wei Wang, Kevin Wilfong, Tim Williamson, and
jeev Motwani, Utkarsh Srivastava, and Jennifer
Serhat Yilmaz. “Realtime Data Processing at
Widom. “STREAM: The Stanford Data Stream
Management System”. In: Data Stream Man- Facebook”. In: Proceedings of the 2016 SIG-
MOD International Conference on Management
agement: Processing High-Speed Data Streams.
of Data. San Francisco, California, USA, 2016,
Edited by Minos Garofalakis, Johannes Gehrke,
pages1087–1098.
andRajeevRastogi.Berlin/Heidelberg,Germany:
Springer,2016,pages317–336. [14] CockroachDB.StructureddataencodinginCock-
[7] Doug Beaver, Sanjeev Kumar, Harry C. Li, Ja-
roachDB SQL. Jan. 2018. URL: https : / /
github . com / cockroachdb / cockroach /
son Sobel, and Peter Vajgel. “Finding a Nee-
blob/master/docs/tech-notes/encoding.
dle in Haystack: Facebook’s Photo Storage”. In:
Proceedings of the 9th USENIX Conference on md(visitedon04/20/2018).
Operating Systems Design and Implementation [15] Brian F. Cooper, Raghu Ramakrishnan, Utkarsh
(OSDI). Vancouver, British Columbia, Canada, Srivastava, Adam Silberstein, Philip Bohannon,
Oct.2010,pages1–8. Hans-Arno Jacobsen, Nick Puz, Daniel Weaver,
[8] NathanBronson,ZachAmsden,GeorgeCabrera, and Ramana Yerneni. “PNUTS: Yahoo!’s Hosted
PrasadChakka,PeterDimov,HuiDing,JackFer- Data Serving Platform”. In: Proceedings of the
ris, Anthony Giardullo, Sachin Kulkarni, Harry VLDBEndowment 1.2(Aug.2008),pages1277–
Li,MarkMarchukov,DmitriPetrov,LovroPuzar, 1288.
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 227

[16] JamesC.Corbett,JeffreyDean,MichaelEpstein, [24] Sanjay Ghemawat, Howard Gobioff, and Shun-
Andrew Fikes, Christopher Frost, J. J. Furman, Tak Leung. “The Google File System”. In: Pro-
Sanjay Ghemawat, Andrey Gubarev, Christopher ceedingsofthe19th ACMSymposiumonOperat-
Heiser, Peter Hochschild, Wilson Hsieh, Sebas- ing Systems Principles (SOSP). Bolton Landing,
tianKanthak,EugeneKogan,HongyiLi,Alexan- NY,USA,Oct.2003,pages29–43.
derLloyd,SergeyMelnik,DavidMwaura,David
[25] GeorgiosGiannikis,GustavoAlonso,andDonald
Nagle,SeanQuinlan,RajeshRao,LindsayRolig,
Kossmann. “SharedDB: Killing One Thousand
Yasushi Saito, Michal Szymaniak, Christopher
Queries with One Stone”. In: Proceedings of the
Taylor, Ruth Wang, and Dale Woodford. “Span-
VLDB Endowment 5.6 (Feb. 2012), pages 526–
ner:Google’sGloballyDistributedDatabase”.In:
537.
ACM Transactions on Computer Systems 31.3
[26] GitHub, Inc. gh-ost: GitHub’sonline schemami-
(Aug.2013),8:1–8:22.
gration for MySQL. URL: https://github.
[17] Carlo A. Curino, Letizia Tanca, Hyun J. Moon, com/github/gh-ost(visitedon02/01/2017).
and Carlo Zaniolo. “Schema Evolution in
[27] JonGjengset.evmap:Alock-free,eventuallycon-
Wikipedia: toward a Web Information System
Benchmark”.In:ProceedingsoftheInternational
sistent,concurrentmulti-valuemap.URL:https:
//github.com/jonhoo/rust-evmap (visited
Conference on Enterprise Information Systems
on09/13/2018).
(ICEIS).June2008.
[28] Pradeep Kumar Gunda, Lenin Ravindranath,
[18] Databricks, Inc. Structured Streaming in Produc-
Chandramohan A. Thekkath, Yuan Yu, and Li
tion–Recoverafterchangesinastreamingquery.
URL: https://docs.databricks.com/ Zhuang.“Nectar:AutomaticManagementofData
spark/latest/structured- streaming/
andComputationinDatacenters”.In:Proceedings
ofthe9th USENIXConferenceonOperatingSys-
production . html # recover - after -
changes-in-a-streaming-query(visitedon
temsDesignandImplementation(OSDI).Vancou-
ver, British Columbia, Canada, 2010, pages 75–
09/06/2018).
88.
[19] Giuseppe DeCandia, Deniz Hastorun, Madan
[29] Himanshu Gupta and Inderpal Singh Mumick.
Jampani, Gunavardhan Kakulapati, Avinash Lak-
“Selectionofviewstomaterializeinadataware-
shman,AlexPilchin,SwaminathanSivasubrama-
house”.In:IEEETransactionsonKnowledgeand
nian, Peter Vosshall, and Werner Vogels. “Dy-
DataEngineering17.1(Jan.2005),pages24–43.
namo: Amazon’s Highly Available Key-value
Store”. In: Proceedings of 21st ACM SIGOPS [30] Himanshu Gupta and Inderpal Singh Mumick.
Symposium on Operating Systems Principles “IncrementalMaintenanceofAggregateandOut-
(SOSP).Stevenson,Washington,USA,Oct.2007, erjoinExpressions”.In:InformationSystems31.6
pages205–220. (Sept.2006),pages435–464.
[20] Dror G. Feitelson, Eitan Frachtenberg, and Kent [31] StavrosHarizopoulos,VladislavShkapenyuk,and
L.Beck.“DevelopmentandDeploymentatFace- Anastassia Ailamaki. “QPipe: A Simultaneously
book”. In: IEEE Internet Computing 17.4 (July PipelinedRelationalQueryEngine”.In:Proceed-
2013),pages8–17. ings of the 2005 ACM SIGMOD International
Conference on Management of Data. Baltimore,
[21] SheldonFinkelstein.“CommonExpressionAnal-
Maryland,USA,June2005,pages383–394.
ysis in Database Applications”. In: Proceedings
ofthe1982ACMSIGMODInternationalConfer- [32] Peter Bhat Harkins. Lobste.rs access pattern
ence on Management of Data. Orlando, Florida, statistics for research purposes. Mar. 2018. URL:
USA,June1982,pages235–245. https://lobste.rs/s/cqnzl5/lobste_
rs_access_pattern_statistics_for#c_
[22] Django Software Foundation. Django: The Web
hj0r1b(visitedon03/12/2018).
frameworkforperfectionistswithdeadlines.Mar.
2018. URL: https://www.djangoproject. [33] Peter Bhat Harkins. replying comments
com/(visitedon03/20/2018). view in Lobsters. Feb. 2018. URL: https :
//github.com/lobsters/lobsters/blob/
[23] Matt Freels. TableMigrator. URL: https : / /
640f2cdca10cc737aa627dbdf0bbe398b81b497f/
github.com/freels/table_migrator (vis-
db/views/replying_comments_v06.sql
itedon02/01/2017).
(visitedon04/20/2018).
228 13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

[34] Patrick Hunt, Mahadev Konar, Flavio Paiva Jun- db / schema . rb # L145 - L148 (visited on
queira, and Benjamin Reed. “ZooKeeper: Wait- 04/23/2018).
freeCoordinationforInternet-scaleSystems”.In: [43] Lobsters Developers. Lobsters News Aggregator.
Proceedings of the USENIX Annual Technical Mar. 2018. URL: https://lobste.rs (visited
Conference. Boston, Massachusetts, USA, June on03/02/2018).
2010,pages149–158.
[44] Frank McSherry. Differential Dataflow in Rust.
[35] MichaelIsardandMart´ınAbadi.“FalkirkWheel: URL: https : / / crates . io / crates /
Rollback Recovery for Dataflow Systems”. In: differential - dataflow (visited on
CoRRabs/1503.08877(2015).
01/15/2017).
[36] Michael Isard, Mihai Budiu, Yuan Yu, Andrew [45] Frank McSherry. Throughput and Latency in
Birrell, and Dennis Fetterly. “Dryad: Distributed Differential Dataflow: open-loop measurements.
Data-parallelProgramsfromSequentialBuilding Aug. 2017. URL: https : / / github . com /
Blocks”.In:Proceedingsofthe2ndACMSIGOPS
frankmcsherry/blog/blob/master/posts/
EuropeanConferenceonComputerSystems(Eu- 2017-07-24.md#addendum-open-loop-
roSys).Lisbon,Portugal,Mar.2007,pages59–72. measurements - 2017 - 08 - 14 (visited on
[37] Bryan Kate, Eddie Kohler, Michael S. Kester, 04/13/2018).
Neha Narula, Yandong Mao, and Robert Morris. [46] Frank McSherry, Derek G. Murray, Rebecca
“Easy Freshness with Pequod Cache Joins”. In: Isaacs,andMichaelIsard.“Differentialdataflow”.
Proceedings of the 11th USENIX Symposium on In:Proceedingsofthe6th BiennialConferenceon
Networked Systems Design and Implementation InnovativeDataSystemsResearch(CIDR).Asilo-
(NSDI). Seattle, Washington, USA, Apr. 2014, mar,California,USA,Jan.2013.
pages415–428.
[47] JohnMeehan,NesimeTatbul,StanZdonik,Cansu
[38] Martin Kleppmann. Turning the database inside- Aslantas,UgurCetintemel,JiangDu,TimKraska,
outwithApacheSamza.Mar.2015.URL:https:
Samuel Madden, David Maier, Andrew Pavlo,
//martin.kleppmann.com/2015/03/04/
Michael Stonebraker, Kristin Tufte, and Hao
turning-the-database-inside-out.html
Wang. “S-Store: Streaming Meets Transaction
(visitedon05/09/2016). Processing”.In:ProceedingsoftheVLDBEndow-
[39] Sanjeev Kulkarni, Nikunj Bhagat, Maosong Fu, ment8.13(Sept.2015),pages2134–2145.
Vikas Kedigehalli, Christopher Kellogg, Sailesh [48] Jhonny Mertz and Ingrid Nunes. “Understand-
Mittal,JigneshM.Patel,KarthikRamasamy,and ing Application-Level Caching in Web Applica-
SiddarthTaneja.“TwitterHeron:StreamProcess- tions: A Comprehensive Introduction and Survey
ing at Scale”. In: Proceedings of the 2015 ACM of State-of-the-Art Approaches”. In: ACM Com-
SIGMOD International Conference on Manage- putingSurveys50.6(Nov.2017),98:1–98:34.
ment of Data. Melbourne, Victoria, Australia,
[49] Microsoft,Inc.CreateIndexedViews–Additional
May2015,pages239–250.
Requirements. SQL Server Documentation. URL:
[40] Per-A˚ke Larson and Jingren Zhou. “Efficient https://docs.microsoft.com/en-us/sql/
Maintenance of Materialized Outer-Join Views”. relational- databases/views/create-
In: Proceedings of the 23rd International Con- indexed-views#additional-requirements
ference on Data Engineering (ICDE). Apr. 2007,
(visitedon04/16/2017).
pages56–65.
[50] Subramanian Muralidhar, Wyatt Lloyd,
[41] Ki Yong Lee and Myoung Ho Kim. “Optimiz-
Sabyasachi Roy, Cory Hill, Ernest Lin, Wei-
ingtheIncrementalMaintenanceofMultipleJoin
wen Liu, Satadru Pan, Shiva Shankar, Viswanath
Views”. In: Proceedings of the 8th ACM Inter-
Sivakumar, Linpeng Tang, and Sanjeev Kumar.
national Workshop on Data Warehousing and
“f4: Facebook’s Warm BLOB Storage System”.
OLAP (DOLAP). Bremen, Germany, Nov. 2005, In: Proceedings of the 11th USENIX Conference
pages107–113. onOperatingSystemsDesignandImplementation
[42] Lobsters Developers. Lobsters Database Schema (OSDI). Broomfield, Colorado, USA, Oct. 2014,
(schema.rb). Apr. 2018. URL: https : / / pages383–398.
github.com/lobsters/lobsters/blob/
93fe0fdd74028cf678134d6d112ae084d8fdd928/
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 229

[51] Derek G. Murray, Frank McSherry, Rebecca [59] Prasan Roy, S. Seshadri, S. Sudarshan, and Sid-
Isaacs, Michael Isard, Paul Barham, and Mart´ın dhesh Bhobe. “Efficient and Extensible Algo-
Abadi. In: Proceedings of the 24th ACM Sympo- rithms for Multi Query Optimization”. In: Pro-
sium on Operating Systems Principles (SOSP). ceedings of the 2000 ACM SIGMOD Interna-
Farmington, Pennsylvania, USA, Nov. 2013, tional Conference on Management of Data. Dal-
pages439–455. las,Texas,USA,May2000,pages249–260.
[52] Derek G. Murray, Malte Schwarzkopf, Christo- [60] KennethSalem,KevinBeyer,BruceLindsay,and
pher Smowton, Steven Smith, Anil Mad- Roberta Cochrane. “How to Roll a Join: Asyn-
havapeddy, and Steven Hand. “CIEL: a universal chronous Incremental View Maintenance”. In:
execution engine for distributed data-flow com- Proceedingsofthe2000ACMSIGMODInterna-
puting”. In: Proceedings of the 8th USENIX tional Conference on Management of Data. Dal-
Symposium on Networked System Design and las,Texas,USA,2000,pages129–140.
Implementation (NSDI). Boston, Massachusetts,
[61] Tony Savor, Mitchell Douglas, Michael Gen-
USA,Mar.2011,pages113–126.
tili, Laurie Williams, Kent Beck, and Michael
[53] MilosNikolic,MohammadDashti,andChristoph Stumm. “Continuous Deployment at Facebook
Koch. “How to Win a Hot Dog Eating Contest: and OANDA”. In: Proceedings of the 38th In-
Distributed Incremental View Maintenance with ternational Conference on Software Engineering
BatchUpdates”.In:Proceedingsofthe2016ACM (ICSE).Austin,Texas,USA,2016,pages21–30.
SIGMOD International Conference on Manage-
[62] Bianca Schroeder, Adam Wierman, and Mor
mentofData(SIGMOD).SanFrancisco,Califor-
Harchol-Balter.“OpenVersusClosed:ACaution-
nia,USA,2016,pages511–526. aryTale”.In:Proceedingsofthe3rdUSENIXCon-
[54] Rajesh Nishtala, Hans Fugal, Steven Grimm, ference on Networked Systems Design and Im-
Marc Kwiatkowski, Herman Lee, Harry C. Li, plementation (NSDI). San Jose, California, USA,
RyanMcElroy,MikePaleczny,DanielPeek,Paul 2006,pages239–252.
Saab,DavidStafford,TonyTung,andVenkatesh-
[63] Jes Schultz Borland. What You Can (and Can’t)
waran Venkataramani. “Scaling Memcache at
Do With Indexed Views. Brent Ozar Unlimited
Facebook”. In: Proceedings of the 10th USENIX Blog. URL: https://www.brentozar.com/
Conference on Networked Systems Design and
archive/2013/11/what-you-can-and-
Implementation (NSDI). Lombard, Illinois, USA, cant-do-with-indexed-views/ (visited on
Apr.2013,pages385–398.
04/16/2017).
[55] Oracle Corp. MySQL Connector/Python Devel-
[64] Ziv Scully and Adam Chlipala. “A Program
oper Guide. URL: https://dev.mysql.com/
Optimization for Automatic Database Result
doc/connector-python/en/connector- Caching”. In: Proceedings of the 44th ACM SIG-
python-api-mysqlcursorprepared.html
PLAN Symposium on Principles of Program-
(visitedon09/05/2018).
ming Languages (POPL). Paris, France, 2017,
[56] Percona LLC. pt-online-schema-change. URL: pages271–284.
https://www.percona.com/doc/percona-
[65] SoundCloud Ltd. Large Hadron Migrator. URL:
toolkit/2.2/pt-online-schema-change.
https://github.com/soundcloud/lhm(vis-
html(visitedon02/01/2017).
itedon02/01/2017).
[57] DanR.K.Ports,AustinT.Clements,IreneZhang,
[66] Facebook Open Source. A persistent key-value
Samuel Madden, and Barbara Liskov. “Transac-
store for fast storage environments. Apr. 2018.
tionalConsistencyandAutomaticManagementin URL: http : / / rocksdb . org/ (visited on
an Application Data Cache”. In: Proceedings of
04/20/2018).
the9thUSENIXConferenceonOperatingSystems
[67] FacebookOpenSource.MyRocksdatadictionary
Design and Implementation (OSDI). Vancouver,
BritishColumbia,Canada,2010,pages279–292.
format.Apr.2018.URL:https://github.com/
facebook/mysql-5.6/wiki/MyRocks-data-
[58] “Ray: A Distributed Framework for Emerging dictionary-format(visitedon04/20/2018).
AI Applications”. In: Proceedings of the 13th
[68] BoergeSvingen.PublishingwithApacheKafkaat
USENIX Symposium on Operating Systems De-
The New York Times. Confluent, Inc. blog. Sept.
sign and Implementation (OSDI). Carlsbad, Cal-
ifornia,USA,Oct.2018.
2017. URL: https://www.confluent.io/
blog/publishing- apache- kafka- new-
york-times/(visitedon09/14/2017).
230 13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

[69] ThePHPGroup.PHPDataObjects.URL:http: plementation (NSDI). San Jose, California, USA,
//php.net/manual/en/book.pdo.php (vis- Apr.2012,pages15–28.
itedon09/05/2018).
[76] Matei Zaharia, Tathagata Das, Haoyuan Li, Tim-
[70] FrankW.TompaandJosephA.Blakeley.“Main- othyHunter,ScottShenker,andIonStoica.“Dis-
taining Materialized Views Without Accessing cretized Streams: Fault-tolerant Streaming Com-
Base Data”. In: Information Systems 13.4 (Oct. putation at Scale”. In: Proceedings of the 24th
1988),pages393–406. ACM Symposium on Operating Systems Prin-
[71] Ankit Toshniwal, Siddarth Taneja, Amit Shukla, ciples (SOSP). Farmington, Pennsylvania, USA,
Karthik Ramasamy, Jignesh M. Patel, Sanjeev Nov.2013,pages423–438.
Kulkarni,JasonJackson,KrishnaGade,Maosong [77] Jingren Zhou, Per-A˚ke Larson, and Hicham G.
Fu,JakeDonham,NikunjBhagat,SaileshMittal, Elmongui. “Lazy Maintenance of Materialized
and Dmitriy Ryaboy. “Storm@Twitter”. In: Pro- Views”.In:Proceedingsofthe33rd International
ceedingsofthe2014ACMSIGMODInternational Conference on Very Large Data Bases. Vienna,
Conference on Management of Data. Snowbird, Austria,Sept.2007,pages231–242.
Utah,USA,June2014,pages147–156. [78] JingrenZhou,Per-AkeLarson,Johann-Christoph
[72] WernerVogels.“EventuallyConsistent”.In:Com- Freytag, and Wolfgang Lehner. “Efficient Ex-
munications of the ACM 52.1 (Jan. 2009), ploitation of Similar Subexpressions for Query
pages40–44. Processing”. In: Proceedings of the 2007 ACM
SIGMOD International Conference on Manage-
[73] JacquelineXu.Onlinemigrationsatscale.Stripe
engineering blog. URL: https : / / stripe . ment of Data (SIGMOD). Beijing, China, 2007,
com/blog/online-migrations (visited on pages533–544.
02/01/2017). [79] Jingren Zhou, Per-A˚ke Larson, and Jonathan
Goldstein. Partially Materialized Views. Techni-
[74] Jean Yang, Travis Hance, Thomas H. Austin,
calreportMSR-TR-2005-77.MicrosoftResearch,
Armando Solar-Lezama, Cormac Flanagan, and
June2005.
Stephen Chong. “Precise, Dynamic Information
FlowforDatabase-backedApplications”.In:Pro- [80] Jingren Zhou, Per-A˚ke Larson, Jonathan Gold-
ceedings of the 37th ACM SIGPLAN Confer- stein, and Luping Ding. “Dynamic Materialized
ence on Programming Language Design and Im- Views”.In:Proceedingsofthe23rd International
plementation (PLDI). Santa Barbara, California, Conference on Data Engineering (ICDE). Istan-
USA,June2016,pages631–647. bul,Turkey,Apr.2007,pages526–535.
[75] Matei Zaharia, Mosharaf Chowdhury, Tathagata [81] YueZhuge,He´ctorGarc´ıa-Molina,JoachimHam-
Das,AnkurDave,JustinMa,MurphyMcCauley, mer, and JenniferWidom. “View Maintenancein
Michael J. Franklin, Scott Shenker, and Ion Sto- aWarehousingEnvironment”.In:Proceedingsof
ica. “Resilient Distributed Datasets: A Fault- the 1995 ACM SIGMOD International Confer-
tolerantAbstractionforIn-memoryClusterCom- ence on Management of Data. San Jose, Califor-
puting”.In:Proceedingsofthe9th USENIXCon- nia,USA,May1995,pages316–327.
ference on Networked Systems Design and Im-
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 231