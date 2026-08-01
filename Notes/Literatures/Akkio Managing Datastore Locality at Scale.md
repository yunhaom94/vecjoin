# Akkio Managing Datastore Locality at Scale

**Source**: Akkio Managing Datastore Locality at Scale.pdf
**Format**: .pdf

---

Sharding the Shards: Managing Datastore
Locality at Scale with Akkio
Muthukaruppan Annamalai, Kaushik Ravichandran, Harish Srinivas, Igor Zinkovsky,
Luning Pan, Tony Savor, and David Nagle, Facebook; Michael Stumm, University of Toronto
https://www.usenix.org/conference/osdi18/presentation/annamalai
This paper is included in the Proceedings of the
13th USENIX Symposium on Operating Systems Design
and Implementation (OSDI ’18).
October 8–10, 2018 • Carlsbad, CA, USA
ISBN 978-1-939133-08-3
Open access to the Proceedings of the
13th USENIX Symposium on Operating Systems
Design and Implementation
is sponsored by USENIX.

|     |     |          | Sharding  |          | the Shards: |          |      |       |     |     |
| --- | --- | -------- | --------- | -------- | ----------- | -------- | ---- | ----- | --- | --- |
|     |     | Managing | Datastore | Locality |             | at Scale | with | Akkio |     |     |
MuthukaruppanAnnamalai,† KaushikRavichandran,† HarishSrinivas,† IgorZinkovsky,†
|     |     | LuningPan,† | TonySavor,†                              | DavidNagle† |     | andMichaelStumm‡,† |     |     |     |     |
| --- | --- | ----------- | ---------------------------------------- | ----------- | --- | ------------------ | --- | --- | --- | --- |
|     |     | †           | Facebook,1HackerWay,MenloPark,CAUSA94025 |             |     |                    |     |     |     |     |
{muthu,kaushikr,harishs,igorzi,luningp,tsavor,dfnagle}@fb.com
‡ Dept.ElectricalandComputerEngineering,UniversityofToronto,CanadaM5S3G4
stumm@eecg.toronto.edu
|     |     | Abstract |     |     | andimportant,aswitnessedbySpannerCloudandCock- |     |     |     |     |     |
| --- | --- | -------- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- |
Akkioisalocalitymanagementservicelayeredbetween roachDB,twocloud-basedgeo-distributeddatastoresys-
client applications and distributed datastore systems. It temsavailabletoanyorganization[17,38].
determines how and when to migrate data to reduce re- Managingdataaccesslocality1ingeo-distributedsys-
sponse times and resource usage. Akkio primarily tar- temsisimportantbecausedoingsocansignificantlyim-
gets multi-datacenter geo-distributed datastore systems. prove data access latencies, given that intra-datacenter
Itsdesignwasmotivatedbytheobservationthatmanyof communication latencies are two orders of magnitude
Facebook’s frequently accessed datasets have low R/W smaller than cross-datacenter communication latencies;
ratios that are not well served by distributed caches or e.g., 1ms vs. 100ms. Locality management can also
full replication. Akkio’s unit of migration is called a µ- significantly reduce cross-datacenter bandwidth usage,
shard. Each µ-shard is designed to contain related data which is important because the bandwidth available be-
with some degree of access locality. At Facebook, µ- tween datacenters is often limited (§2.1), potentially
shardshavebecomeafirst-classabstraction. leading to communication bottlenecks and attendantly
AkkiowentintoproductionatFacebookin2014,and highercommunicationlatencies.Managinglocalityisall
it currently manages ∼100PB of data. Measurements the more challenging when considering that access pat-
from our production environment show that Akkio re- terns can change geographically over time; particularly,
duces access latencies by up to 50%, cross-datacenter whenshiftingworkloadfromonedatacenteroperatingat
trafficbyupto50%,andstoragefootprintbyupto40% highutilization(e.g.,duringitsday)toanotheroperating
compared to reasonable alternatives. Akkio is scalable: atlowutilization(e.g.,itsnight)(§2.2).
itcansupporttrillionsofµ-shardsandprocessmany10’s We argue that explicit data migration is a necessary
ofmillionsofdataaccessrequestspersecond. Anditis mechanism for managing data access locality in geo-
portable: itcurrentlysupportsfivedatastoresystems. distributed environments, because existing alternatives
|     |     |     |     |     | haveseriousdrawbacksinmanyscenarios. |        |        |                 |     | Forinstance,  |
| --- | --- | --- | --- | --- | ------------------------------------ | ------ | ------ | --------------- | --- | ------------- |
|     |     |     |     |     | distributed                          | caches | can be | used to improve |     | data read ac- |
1 Introduction
|     |     |     |     |     | cess | locality. | However, | because misses | often | incur re- |
| --- | --- | --- | --- | --- | ---- | --------- | -------- | -------------- | ----- | --------- |
This paper regards the management of data access lo- mote communications, these caches require extremely
|                                           |     |     |     |           | high | cache hit | rates to | be effective, | thus | demanding |
| ----------------------------------------- | --- | --- | --- | --------- | ---- | --------- | -------- | ------------- | ---- | --------- |
| calityinlargedistributeddatastoresystems. |     |     |     | Ourworkin |      |           |          |               |      |           |
thisareawasinitiallymotivatedbyouraimtoreduceser- significant hardware infrastructure. Further, distributed
|     |     |     |     |     | caches | do not | typically offer | strong | consistency | (§2.4). |
| --- | --- | --- | --- | --- | ------ | ------ | --------------- | ------ | ----------- | ------- |
viceresponsetimesandresourceusageinourclouden-
Anotheralternativeistofullyreplicatedatawithacopy
vironmentwhichoperatesgloballyandatscale:thecom-
putingandstorageresourcesarelocatedinmultiplegeo- in each datacenter to allow for (fast) localized read ac-
cesses. However,asthenumberofdatacentersincreases,
| distributed | datacenters, | hundreds | of petabytes | of data |     |     |     |     |     |     |
| ----------- | ------------ | -------- | ------------ | ------- | --- | --- | --- | --- | --- | --- |
must be available for access, data accesses occur at the storageoverheadbecomesexorbitantwithlargeamounts
rateofmanytensofmillionspersecond,andthelocation of data, and also write overheads increase significantly,
|            |     |                       |         |        | as all | replicas | need to be | updated | on each | write (§2.1). |
| ---------- | --- | --------------------- | ------- | ------ | ------ | -------- | ---------- | ------- | ------- | ------------- |
| from which | any | data item is accessed | changes | dynam- |        |          |            |         |         |               |
ically over time. Many organizations are increasingly AtFacebook,manyoftheheavilyaccesseddatasetshave
facedwithsome,ifnotall,oftheseaspects,astheytar-
1 Ouruseofthetermlocalityshouldnotbeconfoundedwiththe
| getagrowinguserbasearoundtheworld. |     |     |     | Indeed, geo- |     |     |     |     |     |     |
| ---------------------------------- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- |
termlocalization;thesolutionweproposehereisnotsuitableforseg-
distributedsystemsarebecomingincreasinglyprevalent
regatingdatabyregion.
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    445

relativelylowread-writeratios(§2.3),sofullreplication 1,000,000
wouldconsumeexcessivecross-datacenterbandwidth.A 100,000
third alternative is function shipping. But this can also 10,000
be ineffective, as it may still result in significant cross- 1,000
datacentercommunications,thetargetdatacentermaybe 100
10
operating at peak capacity, or the required data may be 1 8 15 22 29 36 43 50 57 64 71 78 85 92 99
locatedinmultipledatacenters.
Akkio. In this paper we present Akkio,2 a local-
itymanagementservicefordistributeddatastoresystems
whoseaimistoimprovedataaccessresponsetimesand
to reduce cross-datacenter bandwidth usage as well as
the total amount of storage capacity needed. Akkio is
layered between client applications servicing client re-
questsandthedistributeddatastoresystemsusednatively
by the client applications. It decides in which datacen-
ter to place and how and when to migrate data, and it
doessoinawaythatistransparenttoitsclientsandthe
underlying datastore system.3 It helps direct each data
access to where the target data is located, and it tracks
each access to be able to make appropriate placement
decisions. Akkio has been in production use at Face-
book since 2014 and thus operates at scale: it currently
managesover100PBofdataandprocessesmanytensof
millions of data accesses per second (despite Akkio not
beingsuitablemanyofFacebook’sdatasets).
µ-shards. Havingmigrationasthebasisforproviding
dataaccesslocalityraisesthequestion: whatistheright
granularity for migrating data? A ubiquitous method in
distributeddatastoresystemsistopartitionthedatainto
shardsusingkeyrangesorkeyhashing[26,37]. Shards
serveastheunitforreplication,failurerecovery,andload
balancing (e.g., upon detection of query or storage load
imbalances, shards are migrated from one node to an-
othertorebalancetheload).Eachshardisontheorderof
onetoafewtensofgigabytes,isassignedinitsentirety
toanode,andmultipleshards(10s–100s)areassigned
toanode.Shardsizesaresetbythedatastoreadministra-
tortobalance(i)theamountofmetadataneededtoman-
age the shards with (ii) effectiveness in load balancing
and failure recovery (§2.5). Notably, datastore systems
defineshardsinanapplication-transparentmanner.
Given the ubiquity of shards, migrating data at shard
granularityisanoption;infact,afewsystemsthatdothis
have been proposed [4, 12, 29, 40]. However, this ap-
proachhasaseriousdrawbackgiventypicalshardsizes:
the vast majority of the migrated data would likely not
belong to the working set of the accessing workload at
the new location, thus incurring unnecessary migration
2AkkioisaplayonHarryPotter’sAccioSummoningCharmthat
summons an object to the caster, potentially over a significant dis-
tance[31].
3 Inthispaperweusetheterm“underlyingdatastoresystem”to
refertothedatastoresystemusednativelybytheclientapplication. It
maybedifferentthanthedatastoresystemusedbyAkkio.
)elacs
gol(
sdnocesillim
shards
u-shards
writes
%
Figure1: Cumulativedistributionofcross-datacentertransfer
times. Each curve contains data obtained from 10,000 ran-
domlysampleddatapointsacrossallcross-datacenterlinksat
Facebook.Avg.shardsizeis2GB;avg.µ-shardsizeis200KB.
overhead and wasting inter-datacenter WAN communi-
cationbandwidth. AtFacebook,becausetheworkingset
sizeofaccesseddatatendstobelessthan1MB,migrat-
inganentireshard(1-10GB)wouldbeineffective.
Inthispaper,bywayofAkkio,weadvocatefortheno-
tionoffiner-graineddatasetstoserveastheunitofmigra-
tionwhenmanaginglocality. Wecallthesefiner-grained
datasetsµ-shards. Eachµ-shardisdefinedtocontainre-
lated data that exhibits some degree of access locality
with client applications. It is the application that deter-
mineswhichdataisassignedtowhichµ-shard. AtFace-
book, µ-shard sizes typically vary from a few hundred
bytes to a few megabytes in size, and a µ-shard (typi-
cally)containsmultiplekey-valuepairsordatabasetable
rows. Each µ-shard is assigned (by Akkio) to a unique
shardinthataµ-shardneverspansmultipleshards.
µ-shards are motivated by our observation that there
exist datasets that exhibit good access locality with re-
spect to a client application, but that they are best iden-
tified by the client application. Hence, µ-shards are not
simplysmaller-sizedshards. Theprimarydifferencebe-
tweenshardsandµ-shards,besidessize,isthewaydata
isassignedtothem. Withtheformer,dataisassignedto
shards by key partitioning or hashing with little expec-
tation of access locality. With the later, the application
assignsdatatoµ-shardswithhighexpectationofaccess
locality. Asaresult, µ-shardmigrationhasanoverhead
that is an order of magnitude lower than that of shard
migration(Fig.1),anditsutilityisfarhigher.
µ-shardsoffertheirbestadvantagesincontextswhere
itisunambiguoushowtosettheunitofmigrationsothat
it is simultaneously as large as possible, meets the con-
straints of good access locality, and primarily contains
data belonging to the same working set of an accessing
workload. Wehavefoundthatthereexistmanydatasets
wheretheseparametersareeasilyidentified;seeTable1
forsomeexamples. Becauseofthis,weargueitispropi-
tioustomakeµ-shardsafirstclassabstraction,suchthat
they are visible to and specified by client applications.
The motivation is that only the client applications have
thedomainknowledgetobestdeterminewhichdataare
relatedandlikelytobeusedtogether.
Having the application identify related data is not an
446 13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

– webapplicationuserprofileinformation
| 1,000,000 |     |     |     |     |     |     | – Amazonuserbrowsinghistorytoinformrecommendations |     |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- |
– Spotifyuserlisteninghistorytoinformsubsequentcontent
)elacs	gol(	BK
|     | 1,000 |     |     |     |     |     | – Facebookviewinghistorytoinformsubsequentcontent |     |     |     |     |
| --- | ----- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- |
– Slackgrouprecentmessages
|     | 1   |           |       |          | shards   |             | – Redditsubreddits |     |     |     |     |
| --- | --- | --------- | ----- | -------- | -------- | ----------- | ------------------ | --- | --- | --- | --- |
|     |     |           |       |          | u-shards |             | – emailfolders     |     |     |     |     |
|     | 0   |           |       |          |          |             | – messagingqueues  |     |     |     |     |
|     |     | 1 8 15 22 | 29 36 | 43 50 57 | 64 71    | 78 85 92 99 |                    |     |     |     |     |
Table1:Exampledatasetsconducivetoµ-shards.Notethatall
%
butthefirstexhibitrelativelylowread-writeratios.
Figure2:CumulativedistributionofShardandµ-shardsizefor
| ViewStatedatasets.                |     | TheViewStateservicekeepstrackofcon- |     |     |                       |     |                |          |                     |     |          |
| --------------------------------- | --- | ----------------------------------- | --- | --- | --------------------- | --- | -------------- | -------- | ------------------- | --- | -------- |
|                                   |     |                                     |     |     |                       |     | Akkio managing | locality | for geo-distributed |     | environ- |
| tentpreviouslyshowntotheend-user. |     |                                     |     |     | ViewStateµ-shardsizes |     |                |          |                     |     |          |
ments,Akkioanditsmechanismscanbeusefulinother
tendtobelargerthanthesizeofthetypicalµ-shardsmanaged
|     |     |     |     |     |     |     | scenarios. Forexample,Akkiocanbeusedtomigrateµ- |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------- | --- | --- | --- | --- |
byAkkio(500KBavg.vs.200KBavg.).
|     |     |     |     |     |     |     | shardsbetweencoldstoragemedia(e.g. |     |     | HDDs)andhot |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------- | --- | --- | ----------- | --- |
unreasonable expectation. Many applications already storage media (e.g., SSDs) on changes in data tempera-
group together data by prefixing keys with a common tures, similar in spirit to CockroachDB’s archival parti-
identifier to ensure that related data are assigned to the tioningsupport[38]. Further,forpubliccloudsolutions,
sameshard. Thisapproachhasbeenusedforalongtime Akkiocouldmigrateµ-shardswhenshiftingapplication
in practice. Similarly, some databases support the con- workloads from one cloud provider to another cloud
cept of separate partition keys. Spanner supports “di- provider that is operationally less expensive [39]. Fi-
rectories” although Spanner may shard directories into nally,whenreshardingisrequired,Akkiocouldmigrate
multiplefragments[11]. Finally,anumberofFacebook- µ-shards,onfirstaccess,tonewlyinstantiatedshards,al-
internallydevelopeddatabases,includingZippyDB,sup- lowingamoregentle,incrementalformofreshardingin
portµ-shardsasafirstclassabstractioninthesensethat situations where many new nodes (e.g. a row of racks)
eachaccessrequestalsoincludesaµ-shardid[3,8,34]. comeonlinesimultaneously.
Akkio’sfunctionality. Akkioisimplementedasalayer Contributions. We describe the design and imple-
betweenclientapplicationsandtheunderlyingdatastore mentationofAkkio(§4). Tothebestofourknowledge,
systemthatimplementssharding. Althoughµ-shardsare Akkio is the first system capable of managing data lo-
definedbytheclientapplications, Akkiomanagesthem calityatµ-shardgranularityandatscale,whilealsosup-
in an application-transparent manner. Akkio is respon- portingstrongconsistency. IndescribingAkkio, wefo-
sible for: (i) tracking client-application accesses to µ- cus on scalability; in that sense, this paper focuses on
the“plumbing”andnotonpolicy;i.e.,specificdecision-
| shards | so  | it can take | access | history | into | account in its |     |     |     |     |     |
| ------ | --- | ----------- | ------ | ------- | ---- | -------------- | --- | --- | --- | --- | --- |
decision making; (ii) deciding where to place each µ- makingalgorithms.ForapplicationswhereAkkioissuit-
shard; (iii) migrating µ-shards according to a given mi- able,weshowin§5thatAkkiois:
gration policy for the purpose of reducing access laten- Effectivealonganumberofdimensions:Comparedto
cies and WAN communication; and (iv) directing each typical alternatives, Akkio can achieve read latency re-
access request to the appropriate µ-shard. Akkio takes ductions: upto50%;Writelatencyreductions: 50%and
capacity constraints and resource loads into account in more;Cross-datacentertrafficreductions:byupto50%.
its placement and migration decisions, even in the face Further,Akkioreducesstoragespacerequirementsbyup
ofaheterogeneousenvironmentwithaconstantlychurn- toX−RcomparedtofullreplicationwithX datacenters
inghardwarefleet. whenareplicationfactorofRisrequiredforavailability.
Akkioisabletosupportavarietyofreplicationconfig- Scalable:Statisticsfromproductionworkloadsservic-
urationsandconsistencyrequirements(includingstrong ing well over a billion users demonstrate the system re-
consistency) as specified by each client application ser- mainsefficientandeffectiveevenwhenprocessingmany
vice. This flexibility is provided because the client ap- tensofmillionsofrequestspersecond. Akkiocansup-
plicationserviceownersareinthebestpositiontomake porttrillionsofµ-shards.
the right tradeoffs between availability, consistency, re- Portable: Akkio’s design is simple and flexible
sourcecost-effectiveness,andperformance. Akkiomaps enough to allow it to be easily layered on top of most
| each | µ-shard | with | a specified | replication |     | requirement |                   |          |       |           |         |
| ---- | ------- | ---- | ----------- | ----------- | --- | ----------- | ----------------- | -------- | ----- | --------- | ------- |
|      |         |      |             |             |     |             | backend datastore | systems. | Akkio | currently | runs on |
onto a shard configured with the same replication and top of ZippyDB, Cassandra, and three other internally-
consistencyrequirementsintheunderlyingdatastoresys- developeddatabasesatFacebook.
| tem. | As well, | it enforces | the | specified | level | of consis- |              |                  |     |             |          |
| ---- | -------- | ----------- | --- | --------- | ----- | ---------- | ------------ | ---------------- | --- | ----------- | -------- |
|      |          |             |     |           |       |            | Limitations. | Akkio’s approach |     | to managing | locality |
tencyduringµ-shardmigrations.
withµ-shardswillnotbebeneficialforalltypesofdata,
Other applications. While this paper focuses on such as those better served by distributed caches, or
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    447

| 100 |     |     |     |     |     |     | 100 |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| %   |     |     |     |     |     |     | %   |     |     |     |     |     |
| 75  |     |     |     |     |     |     | 75  |     |     |     |     |     |
| 50  |     |     |     |     |     |     | 50  |     |     |     |     |     |
| 25  |     |     |     |     |     |     | 25  |     |     |     |     |     |
| 0   |     |     |     |     |     |     | 0   |     |     |     |     |     |
04	Mar 05	Mar 06	Mar 07	Mar 08	Mar 09	Mar 10	Mar 11	Mar 04	Mar 05	Mar 06	Mar 07	Mar 08	Mar 09	Mar 10	Mar 11	Mar
Figure3:Proportion(in%)ofincomingservicerequestsorigi- Figure4:Proportion(in%)ofincomingservicerequestsorig-
natingfromRegionAprocessedateachdatacenter.Eachcurve inating from Region B processed at each datacenter. In this
represents a datacenter. The sum over all curves is always case,RegionBdoesnothavealocaldatacenter.
equalto100%.Inthiscase,RegionAhasalocaldatacenter.
putthisintoperspective,transferringa10GBshardover
datasetsthatdonotexhibitsufficientaccesslocality. For a 10 Gbps WAN link will consume roughly 10 seconds
example,Akkiowouldnothelpfulinimprovinglocality
|     |     |     |     |     |     |     | of bandwidth.) |     | As a result, | cross-datacenter |     | link band- |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------------ | ---------------- | --- | ---------- |
for data belonging to the Social Graph. Instead Akkio width will typically be constrained and therefore needs
| focuses on   | workloads | with   | datasets  | that | have            | low read- | tobeusedjudiciously. |     |     |     |     |     |
| ------------ | --------- | ------ | --------- | ---- | --------------- | --------- | -------------------- | --- | --- | --- | --- | --- |
| write ratios | and high  | access | locality. |      | These workloads |           |                      |     |     |     |     |     |
arequitecommonandnotwellservedbyacachingtier.
|          |             |     |            |     |     |            | 2.2 Servicerequestmovements |     |     |     |     |     |
| -------- | ----------- | --- | ---------- | --- | --- | ---------- | --------------------------- | --- | --- | --- | --- | --- |
| Further, | while Akkio | can | be layered | on  | top | of a vari- |                             |     |     |     |     |     |
ety of datastores, the datastore needs to provide partic- The datacenters from which data access requests origi-
| ular features | to Akkio | as  | outlined | in §4.2. | As  | a result, |     |     |     |     |     |     |
| ------------- | -------- | --- | -------- | -------- | --- | --------- | --- | --- | --- | --- | --- | --- |
natecanvaryovertime,evenfordataaccessedonbehalf
Akkiomaynotbeabletoaccommodatealldatastoresys-
|     |     |     |     |     |     |     | of a unique | user. | A change | in  | the requesting | datacen- |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ----- | -------- | --- | -------------- | -------- |
tems. Finally, Akkio does not currently support inter- tercanarise,forexample,becausetheusertravelsfrom
µ-shardtransactions,unlessimplementedentirelyclient-
|     |     |     |     |     |     |     | one region | to another, |     | or, more | likely, because | service |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ----------- | --- | -------- | --------------- | ------- |
side;providingthissupportisleftforfuturework. workloadisshiftedfromadatacenterwithhighloadsto
anotherwithlowerloadsinordertolowerservicerequest
| We begin | the | paper | by substantiating |     | our | motiva- |          |            |     |             |             |          |
| -------- | --- | ----- | ----------------- | --- | --- | ------- | -------- | ---------- | --- | ----------- | ----------- | -------- |
|          |     |       |                   |     |     |         | response | latencies. | The | alternative | to shifting | workload |
tionunderlyingAkkio’sapproach(§2)andpresentback-
|     |     |     |     |     |     |     | to other | datacenters | at  | peak times | would | be to increase |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | --- | ---------- | ----- | -------------- |
groundneededtounderstandtherestofthepaper(§3).
|     |     |     |     |     |     |     | the capacity                 | of  | the overloaded |     | datacenter           | to deal with |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | -------------- | --- | -------------------- | ------------ |
|     |     |     |     |     |     |     | peakinfluxofservicerequests. |     |                |     | Butthiscomeswithsig- |              |
2 Motivation nificantoperationaloverheads,whicharehardtojustify
whenotherdatacentersaremostlyidleatthesametime,
givendiurnalrequestpatterns.
2.1 Capitalandoperationalcostsmatter
Figure3showsthatshiftsintrafficoccuronadailyba-
Capital and operational costs become consequential sisatFacebook.Thefigureshowswhichdatacenterspro-
when an organization’s infrastructure must scale to tar- cessed incoming service requests originating from one
getalargenumberofusersaroundtheworld,justifying particular region over a week. Each curve represents a
considerableeffortstorestrainresourceusagewherepos- different datacenter to which the service requests orig-
sible. Consideranorganizationwithtendatacentersand inating from one region were forwarded. The figure
many hundredsof petabytes of datathat must beacces- shows that during busy periods, as many as 50% of the
sible. Whileitisdifficulttoobtaintransparent,publicly requestsoriginatingfromthegivenregionwereshiftedto
availablepricinginformationonthetruecostofstorage, remotedatacenters(mostoftenlocatedinanadjacentre-
a lower bound for capital depreciation and operational gion). Thefigurealsoshowsthatduringnon-peaktimes
costs could be on the order of two cents per gigabyte alloftherequestsareprocessedbythelocaldatacenter.
permonth[9,28]. Thistranslatesto$2millionper100 Figure 4 shows the same type of information, but for
petabytespermonth.Clearly,replicatingalldataontoall a region with no local datacenter. Because there is no
ten datacenters is difficult to justify from an economic localdatacenter,theservicerequestsaredistributedtoa
perspective when, in many cases, acceptable durability numberofdifferentdatacenters. Duringnon-peaktimes,
couldbeachievedwiththreereplicas. we see that almost all traffic is serviced from a single,
WAN cross-datacenter links can also be costly and non-local,butnearbydatacenter.
need to be taken into account. For example, estimates We also measured, for each individual end-user, how
for the costs of a 10 Gbps subterranean link vary from many datacenters processed service requests issued on
$1to$9perkmpermonth,dependingonroute[22]. (To behalfofthatuseroveraperiodofaweek(Table2):over
448    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Numregions: 1 2 3 4 the datastore system. Technically, it would be possible,
%ofusers: 46% 42% 10% 2%
butwearguethatthisisnotagoodideafortworeasons.
Table2: ThepercentageofusersforwhichNumregionswere
First, the size of shards are carefully selected by the
contactedtoservicerequestsonbehalfoftheuser.
datastore architects for the purpose of managing load
balancing and failure recovery, taking into account the
54%ofusershavetheirdataaccessedfromtwoormore
configuration and other metadata needed to manage the
regions. Bottom line: there is a reasonable likelihood
shards. Maintaining this data at µ-shard cardinality
that requests issued on behalf of one end-user will be
wouldcomeathighstorageoverheadswith100’sofbil-
processedbymultipledistinctdatacenters.
lionsofµ-shardsvs.10,000’sofshards. Restructuringa
datastoresystemtoachievethelevelofscalerequiredto
2.3 Lowread-writeratios supportµ-shardsacrosseachofitslayerswouldrequire
non-trivialchanges.
Many important datasets exhibit low read-write ratios
Second, many application services use data that are
(Table 1). As a Facebook-specific example, dataset
not well-served by Akkio-style locality management;
ViewState (§5.2.1) keeps track of content previously
e.g.,GooglesearchorFacebook’ssocialgraph.Hence,it
shown to the end-user and has a read-write ratio of 1.
wouldonlymakesensetoincorporateAkkio’sfunction-
Overall,Facebookhasontheorderof100PBofperiod-
alityintospecialized datastoresystems; giventhatdata-
ically accessed data that has a read-write ratio below 5.
store system designers optimize for the common case,
Notethatwithlowread-writeratios,fully-replicateddata
they would be reluctant to incorporate the additional
wouldincursignificantcross-datacentercommunication,
complexities associated with µ-shards. However, even
asallreplicaswouldhavetobeupdatedonwrites.
with a specialized datastore system, legacy issues come
intoplay;inourexperiences,applicationserviceowners
2.4 Ineffectivenessofdistributedcaches are reluctant to switch away from the underlying data-
store system for which their service was tuned and on
A common strategy to obtain localized data accesses is whichtheyrelyforspecialfeaturesorbehaviors.
todeployadistributedcacheateachdatacenter[2,5,13, We believe that Akkio bridges the functionality of-
14,15,27,32]. Inpracticethisalternativeisineffective fered by various distributed datastore systems and the
formostoftheworkloadsimportanttoFacebook. First, application services’ desire for (transparent) data local-
unless the cache hit rate in the cache is extremely high, ity management to improve response times and reduce
averagereadlatencieswillbehighifthetargetdataisnot WANdatalinkoverheads.
locatedinthelocaldatacenter. Becauseofthis,caching
will demand significant hardware infrastructure, as the
3 Background
cachesateachdatacenterwouldhavetobelargeenough
toholdtheworkingsetofthedatabeingaccessedfrom
Inthissection,webrieflyreviewseveralaspectsofshard
thedatacenter.
replication in distributed datastore systems so we can
Second, low read-write ratios lead to excessive com-
explain Akkio’s architecture in §4. In doing so, we in-
municationovercross-datacenterlinks,becausethedata
troducesomevocabularyweuseinsubsequentsections.
beingwrittenwill,inthecommoncase,beremote.
Withoutlossofgenerality,wespecificallydescribehow
Finally,manyofthedatasetsaccessedbyourservices
shard replication is handled in ZippyDB, an internally
require strong consistency. While providing strongly
developedscalablekey-valuestoresystem.4
consistent caches is possible, it significantly increases
ZippyDB’s data is partitioned horizontally, with each
the complexity of the solution, and it incurs a large
partition assigned to a different shard. Each shard may
amount of extra cross-datacenter communication, fur-
beconfiguredtohavemultiplereplicas, withonedesig-
ther exacerbating WAN latency overheads. It is notable
natedtobetheprimaryandtheothersreferredtoassec-
thatthewidelypopulardistributedcachingsystemsthat
ondaries. (SeeFig.5.) Werefertoallofthereplicasofa
are scalable, such as Memcached or Redis, do not offer
shardasashardreplicaset,andeachreplicaparticipates
strongconsistency. Andforgoodreason.
inashard-specificPaxosgroup[21,24,25]. Awritetoa
shardisdirectedtoitsprimaryreplica,whichthenrepli-
2.5 Separatelocalitymanagementlayer catesthewritetothesecondaryreplicas,usingPaxosto
ensurethatwritesareprocessedinthesameorderateach
Akkioisimplementedasalayerbetweentheapplication
service and the underlying distributed datastore system.
4ZippyDBisusedasthedatabaseserviceforhundredsofusecases
atFacebookincludingnewsproducts,InstagramservicesandWhats-
Thisraisesthequestionofwhetheritwouldmakemore
Appcomponents. Anincreasingnumberofservicesarebeingmoved
sensetoimplementAkkio’sfunctionalitydirectlywithin ontoZippyDBatFacebook.
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 449

A
B
C
sretnecataD
...
2 29 repl-1 repl-2
...
1 345
prim prim
2 345 prim repl-8
...
1 1
repl-1 repl-2
2 345
repl-2 repl-4
...
78 29 prim prim
sdrahS
write
v iii
i
ii iv
v
i iv
ii
ii
v
i iv
iii
sdrahS
sdrahS
x
x
x
etargim
of µ-shards within the replica sets. It also shows how a
writetoaµ-shardispropagatedtoallsecondaries.
Replica sets collections are provisioned and made
available to a client application service by a utility that
takes input from the client application service owners
to help them make the right tradeoffs between avail-
ability, consistency, resource-effectiveness, and perfor-
mance.Forexample,itinputsapplication-serviceparam-
x etersthatincludeexpecteddatasize,expectedaccessrate
(i.e.,QPS),R/W-ratios,etc. Italsoinputspolicyparam-
eters that includereplication factor, availability require-
ments,consistencyrequirementsandconstraintswithre-
specttowherethereplicascanbeplaced.
In general, all possible configurations are included
thatminimizethereplicationfactor(withinthespecified
constraints). However, some configurations may be ex-
cluded. Forexample, forViewState, allreplicasetcon-
Figure5: Shardswithdifferentreplicationconfigurationsdis-
figurationswiththreereplicasinthreedifferentdatacen-
tributed across datacenters. The shaded rectangles represent
tersareexcludedsothattworeplicaswillalwaysbelo-
shards. Shard1hastheprimaryreplicainDatacenterAand
cated in the same datacenter so that writes have lower
twosecondaryreplicasinDatacenterB. Shard2isreplicated
latency(giventheapplicationslowR/W-ratio).
acrossA, B, andC withtheprimaryinB. Thesmallerboxes
represent µ-shards. µ-shard v is assigned to replica set 2; a Once shards have been provisioned, then ZippyDB’s
writethatmodifiesµ-shardvisdirectedtoreplicaset2’spri- Shard Manager assigns each shard replica to a specific
maryreplicaandtheunderlyingdatastoresystemreplicatesthe ZippyDBserverwhileobeyingthespecifiedpolicyrules.
writetothesecondaryreplicas. Akkioismigratingµ-shardx The assignment is registered with a Directory Service
from replica set 78 to replica set 1, and the datastore system so that the ZippyDB client library embedded in the ap-
replicatesxonto1’ssecondary. plication service can identify the server to send its ac-
cessrequeststo. ShardManagerisalsoresponsiblefor:
replica. Readsthatneedtobestronglyconsistentaredi-
(i)loadbalancing,bymigratingshardsifnecessary;and
rected to the primary replica. If eventual consistency is
(ii)monitoringthelivelinessofZippyDBservers,taking
acceptablethenreadscanbedirectedtoasecondary.
appropriateactionwhenaserverfailureisdetected.
A shard’s replication configuration identifies the Asafinalcomment,weobservethatZippyDBisable
numberofreplicasoftheshardandhowthereplicasare to manage multiple different replication configurations
distributed over datacenters, clusters, and racks. Shard inside a single ZippyDB deployment. Other datastore
replicationconfigurationsarecustomizablegiventhatthe systems may not be able to support multiple configura-
data owners are in the best position to make the right tions inside a single deployment. However, in that case
tradeoffs between availability, consistency, resource- onecanusuallyimplementdifferentreplicationconfigu-
effectiveness, and performance. For example, a service rationsinastraight-forwardwaybyusingmultipledata-
mayspecifythatitrequiresthreereplicas,withtworepli- storedeployments.
cas (representing a quorum) in one datacenter for im-
proved write latencies and a third in different datacen-
4 AkkioDesignandImplementation
terfordurability. Anotherservicemayspecifythatitre-
quiresthreereplicaslocatedinthreedifferentdatacenters
For clarity, we describe Akkio’s design and implemen-
butthateventualconsistencyissufficient. Athirdmight
tation in the context of a single client application ser-
requireonlyonecopy,perhapsbecausetheinfrastructure
vice,ViewState,whichusesZippyDBasitsitsunderly-
overheadofhavingmultiplecopiesmaybedeemedtobe
ing datastore system. This is without loss of generality,
toohighrelativetothevalueofthedata.
because the underlying database is unaware of Akkio’s
We use the term replica set collection to refer to the
presencebeyondasmallportionofcodeinthedatabase
group of all replica sets that have the same replication
clientlibrary.
configuration. Eachsuchcollectionisassignedaunique
id we call a location handle. When running on top of
4.1 Designguidelines
ZippyDB, Akkio places µ-shards on, and migrates µ-
shardsbetweendifferentsuchreplicasetcollections.
Akkio’sdesignisinformedbythreeprimaryguidelines.
Fig.5depictsseveralshardreplicasetsandanumber First, Akkio uses an additional level of indirection: it
450 13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

| maps µ-shards | onto | shard | replica | set | collections | whose |     |     |     |     |     |
| ------------- | ---- | ----- | ------- | --- | ----------- | ----- | --- | --- | --- | --- | --- |
ViewState	Service
| shards are | in turn | mapped | to  | datastore | storage | servers. |     |     |     |     |     |
| ---------- | ------- | ------ | --- | --------- | ------- | -------- | --- | --- | --- | --- | --- |
ZippyDB	Client	Library
This allows Akkio to rely on ZippyDB functionality to Akkio	Client	Library
| provide | replication, | consistency, |     | and | intra-cluster | load |     | 	?noitacoL |     |     |     |
| ------- | ------------ | ------------ | --- | --- | ------------- | ---- | --- | ---------- | --- | --- | --- |
ViewState
balancing. Secondly, Akkio is structured so as to keep ZippyDB

| most operations |     | asynchronous |     | and | not on | any critical |     |     |     |     |     |
| --------------- | --- | ------------ | --- | --- | ------ | ------------ | --- | --- | --- | --- | --- |
path — the only operation in the critical path is the µ- Akkio	 Akkio	 Query
|     |     |     |     |     |     |     |     | Location	 | Access	 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------- | --- | --- |
shard location lookup needed for each data access to DB	 DB	 Akkio	Data
|     |     |     |     |     |     |     |     |     | Update	 | Placement	Service	 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------------------ | --- |
identifyinwhichreplicasetcollectionthetargetµ-shard
Figure6:AkkioSystemDesign
| is located. | Thirdly, | Akkio | minimizes |     | the | intersection |     |     |     |     |     |
| ----------- | -------- | ----- | --------- | --- | --- | ------------ | --- | --- | --- | --- | --- |
withtheunderlyingapplicationdatastoretier(e.g., Zip- 4.3 Architecturaloverview
| pyDB), | which makes |     | it more | portable. | The | only two |     |     |     |     |     |
| ------ | ----------- | --- | ------- | --------- | --- | -------- | --- | --- | --- | --- | --- |
points where the datastore system and Akkio meet are Akkio’s general architecture is depicted in Figure 6. A
inthedatastoreclientlibrariesandinAkkio’smigration portion of Akkio’s logic is located in the Akkio Client
logicwhichisspecifictothedatastore. Library, which is embedded into the database client li-
brary;i.e.,ZippyDBclientlibrary,inthiscase.Theclient
applicationservicemakesdataaccessrequestsbycalling
4.2 Requirements
theZippyDBclientlibrary,whichinturnmaymakecalls
totheAkkioClientLibrary.BeyondtheAkkioClientLi-
| Akkio imposes | three | requirements |     | on  | client | application |     |     |     |     |     |
| ------------- | ----- | ------------ | --- | --- | ------ | ----------- | --- | --- | --- | --- | --- |
brary,Akkioismadeupofthreeservices,whicharede-
| services | that wish | to use | it. | First, | the client | applica- |     |     |     |     |     |
| -------- | --------- | ------ | --- | ------ | ---------- | -------- | --- | --- | --- | --- | --- |
tionservicemustpartitiondataintoµ-shards, whichare pictedatthebottomofthefigureanddescribedinmore
detailinthesubsectionsthatfollow.
| expected | to exhibit | a fair | degree | of  | access | locality for |     |     |     |     |     |
| -------- | ---------- | ------ | ------ | --- | ------ | ------------ | --- | --- | --- | --- | --- |
Akkio to be effective. Second, the client application The Akkio Location Service (ALS) maintains a lo-
service must establish its own µ-shard-id scheme that cation database. The location database is used on each
identifies its µ-shards. µ-shard-ids can be any arbitrary data access to look up the location of the target µ-
string, but must be globally unique. Finally, to access shard: the ZippyDB client library makes a call to the
AkkioclientlibrarygetLocation(µ-shard-id)function
| data in | the underlying |     | application | database, |     | the client |     |     |     |     |     |
| ------- | -------------- | --- | ----------- | --------- | --- | ---------- | --- | --- | --- | --- | --- |
applicationservicemustspecifytheµ-shardthedatabe- which returns a ZippyDB location handle (represent-
longs to in the call to the database client library. For ing a replica set collection) obtained from the location
|           |         |             |     |          |          |         | database. | ThelocationhandleenablesZippyDB’sclient |     |     |     |
| --------- | ------- | ----------- | --- | -------- | -------- | ------- | --------- | --------------------------------------- | --- | --- | --- |
| databases | that do | not support |     | µ-shards | natively | as Zip- |           |                                         |     |     |     |
pyDB does, the function used to access data is mod- librarytodirecttheaccessrequesttotheappropriatestor-
|                 |         |                 |     |       |          |             | age              | server. | The location database | is updated | when a µ- |
| --------------- | ------- | --------------- | --- | ----- | -------- | ----------- | ---------------- | ------- | --------------------- | ---------- | --------- |
| ified to        | include | a µ-shard-id    |     | as an | argument | to each     |                  |         |                       |            |           |
| access request; |         | e.g., read(key) |     | must  | be       | modified to | shardismigrated. |         |                       |            |           |
read(µ-shard-id,key). An Access Counter Service (ACS) maintains an ac-
Akkio imposes two requirements on the underlying cesscounterdatabase,whichisusedtotrackallaccesses
database. First, the database must ensure µ-shards do sothatproperµ-shardplacementandmigrationdecisions
|                |     |                                 |     |     |     |     | can | be made. | Each time | the client service | accesses a |
| -------------- | --- | ------------------------------- | --- | --- | --- | --- | --- | -------- | --------- | ------------------ | ---------- |
| notspanshards. |     | BecauseZippyDBunderstandstheno- |     |     |     |     |     |          |           |                    |            |
tion of µ-shards, it will never partition µ-shards. Many µ-shard, the Akkio client library requests the ACS to
databases support explicit partition keys that inform the record the access, the type of access, and the location
database how to partition data (e.g., MySQL, Cassan- fromwhichtheaccesswasmade. Thisrequestisissued
dra). Yet other databases may recognize key prefixes asynchronouslysothatitisnotinthecriticalpath.
whenpartitioningdata(e.g.,HBase,CockroachDB). The ACS is primarily used by Akkio’s third ser-
Second,theunderlyingapplicationdatabasemustpro- vice,theDataPlacementService(DPS),whichdecides
videaminimalamountofsupportsothatAkkiocanim- where to place each µ-shard so as to minimize access
plementmigrationwhilemaintainingstrongconsistency. latenciesandreduceresourceusage. TheDPSalsoiniti-
Becausethespecificfeaturessupportedbydifferentdata- atesandmanagesµ-shardmigrations. TheAkkioClient
storesystemswillvary, theµ-shardmigrationlogicthat Library asynchronously notifies the DPS that a µ-shard
Akkio implements must be specific to the underlying placementmaybesuboptimalwheneveradataaccessre-
datastore system being supported. For example, some quest needs to be directed to a remote datacenter. The
databases, includingZippyDB,offeraccesscontrollists DPS re-evaluates the placement of a µ-shard only when
(ACLs)andtransactions,whicharesufficientforimple- it receives such a notification. This ensures the DPS
menting µ-shard migration. Other databases, including triggers migrations only when needed, thus effectively
Cassandra, offer timestamp support for ordering writes, prioritizing migrations and preventing unnecessary mi-
whichisalsosufficient. grations for µ-shards that are not being accessed. Note,
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    451

| however,                              | that a µ-shard |     | access never | waits for   | a poten- |     |             |                |        |           |       |     |
| ------------------------------------- | -------------- | --- | ------------ | ----------- | -------- | --- | ----------- | -------------- | ------ | --------- | ----- | --- |
|                                       |                |     |              |             |          |     | consistency | requirements   |        | = STRONG; |       |     |
| tialmigrationtobeevaluatedorcomplete, |                |     |              | butproceeds |          |     |             |                |        |           |       |     |
|                                       |                |     |              |             |          |     | replication | configurations |        | =         | {     |     |
|                                       |                |     |              |             |          |     | ”location   |                | handle | a”: <A,   | B, C> |     |
directlywiththeremoteaccess.
|     |     |     |     |     |     |     | ”location |     | handle | b”: <D, | E, F> |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | ------ | ------- | ----- | --- |
Wenowdiscusstheseservicesinmoredetail.
....
};
4.4 AkkioLocationService(ALS) access counter service = AccessState;
|     |     |     |     |     |     |     | migration | policy | = MigrationPolicy( |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------ | ------------------ | --- | --- | --- |
The Akkio Location Service maintains a database that microshard limit=6hours);
stores the location handle of each µ-shard. In principle, Listing1:AkkioConfigurationforSampleService
| most any | database | could | be used for | storing | this infor- |     |     |     |     |     |     |     |
| -------- | -------- | ----- | ----------- | ------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
mation; here we use ZippyDB (without Akkio layered use 3X replication. For each client application service,
ontopofit).5 Thelocationinformationisconfiguredto Akkiostoresasinglecounterperµ-shardperdatacenter.
haveaneventuallyconsistentreplicaateverydatacenter The amount of storage needed for the counters is on
to ensure low read latencies and high availability, with theorderof10’sofbytesperµ-shardanddatacenter; in
the primary replicas evenly distributed across all data- ourenvironmentlessthan200GBperdatacenter, which
centers. This configuration is justified, given the high is again trivial. The counter service can easily scale by
read-writeratio(>500)ofthedatabase. Moreover,dis- spreading the counters over a larger number of servers.
tributed in-memory caches are used at every datacenter As an optimization, the number of counters needed and
tocachethelocationinformationsoastoreducetheread theoverheadofincrementingthemcanbereducedsub-
loadonthedatabase,consideringthatthedatabaseneeds stantially by observing that many of the client applica-
tobequeriedoneveryaccessrequest. tion services have identical access patterns. For exam-
It is possible that the distributed cache will serve a ple, Facebook’s AccessState service, which records ac-
stalelocationmapping,causingtheaccessrequesttobe tionstakeninrelationtodisplayedcontent,hasverysim-
senttothewrongserver. ThetargetZippyDBserverwill ilar access traffic patterns as ViewState, which records
determinethattheµ-shardisnotpresentfromthemissing whichcontentwasdisplayed;thetrafficofbothservices
| ACL,andwillrespondaccordingly. |     |     | Whenthathappens, |     |     |     |     |     |     |     |     |     |
| ------------------------------ | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
isdrivenbyFacebookusertraffic.Forthisreason,Akkio
the ZippyDB client library queries the Akkio Location allows a client application service to specify that the
Serviceagain,thistimerequestingthatthecachebeby- countersofanotherserviceshouldbeusedasaproxyfor
passed. Theclientlibrarysubsequentlyre-populatesthe itsownaccesspattern,inwhichcasetheapplicationser-
cachewiththelatestmapping(makingthecacheatypi- vicedoesnotneedaseparatesetofcounters. Moreover,
caldemand-filledlookasidecache). therequestsarebatchedandsend-optimized,sotheextra
The amount of storage space needed for the ALS is communication traffic generated is marginal. (With our
relativelysmall:eachµ-shardrequiresatmostafewhun- workload,ACSadds0.001%innetworkingbandwidth.)
dredbytesofstorage,sothesizeofthedatasetfortypi-
calclientapplicationserviceswillbeafewhundredGB.
4.6 AkkioDataPlacementService(DPS)
Theoverheadofmaintainingadatabaseforthisamount
| of data in | every datacenter |     | is trivial. | Similarly, | the in- |     |     |     |     |     |     |     |
| ---------- | ---------------- | --- | ----------- | ---------- | ------- | --- | --- | --- | --- | --- | --- | --- |
Akkio’sDataPlacementServiceisresponsibleformap-
memorycachesrequirenomorethanahandfulofservers
|     |     |     |     |     |     | ping | µ-shards | to location | handles | and | for migrating | µ-  |
| --- | --- | --- | --- | --- | --- | ---- | -------- | ----------- | ------- | --- | ------------- | --- |
per datacenter, since a single machine can service mil- shardsinordertoimprovelocality. ThereisoneDPSper
| lionsofrequestspersecond. |     |     | Theservicecaneasilyscale |     |     |     |     |     |     |     |     |     |
| ------------------------- | --- | --- | ------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Akkio-supportedbackenddatastoresystemthatisshared
byincreasingthenumberofcachingservers.
|     |     |     |     |     |     | among     | all of the | application |     | services          | using instances | of        |
| --- | --- | --- | --- | --- | --- | --------- | ---------- | ----------- | --- | ----------------- | --------------- | --------- |
|     |     |     |     |     |     | that same | datastore  | system.     |     | It is implemented |                 | as a dis- |
4.5 AccessCounterService tributedservicewithapresenceineverydatacenter.
|     |     |     |     |     |     | The | two main | interfaces |     | exported | by  | DPS are |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | --- | -------- | --- | ------- |
Accesscountersareusedtokeeptrackofwhereµ-shards
|                                  |     |     |     |                |     | createUshard() |                 | and | evaluatePlacement(). |        |                | New |
| -------------------------------- | --- | --- | --- | -------------- | --- | -------------- | --------------- | --- | -------------------- | ------ | -------------- | --- |
| areaccessedfromandhowfrequently. |     |     |     | Tomaintainthis |     |                |                 |     |                      |        |                |     |
|                                  |     |     |     |                |     | µ-shards       | are provisioned |     | on                   | demand | when a µ-shard | is  |
information,weusethetime-windowedcounters[7]pro-
|                |           |          |             |            |      | accessedforthefirsttime; |                |     | inthatcase,theAkkioclient |     |                |     |
| -------------- | --------- | -------- | ----------- | ---------- | ---- | ------------------------ | -------------- | --- | ------------------------- | --- | -------------- | --- |
| vided natively | by        | ZippyDB. | The counter | database   | uses |                          |                |     |                           |     |                |     |
|                |           |          |             |            |      | libraryreceivesanUNKNOWN |                |     | IDresponsefromALS,soit    |     |                |     |
| a separate,    | dedicated | ZippyDB  | instance,   | configured | to   |                          |                |     |                           |     |                |     |
|                |           |          |             |            |      | invokes                  | createUshard() |     | (§4.6.1).                 |     | EvaluatePlace- |     |
5Iftheapplicationserviceusesadifferentunderlyingdatastoresys- ment() is invoked by the Akkio client library asyn-
tem,weuseaseparateinstanceofthatdatastoresystemforthelocation chronously. It first checks whether initiating a migra-
| database. We | do this | because | the product owners | of the | underlying |      |                 |     |          |         |            |     |
| ------------ | ------- | ------- | ------------------ | ------ | ---------- | ---- | --------------- | --- | -------- | ------- | ---------- | --- |
|              |         |         |                    |        |            | tion | is permissible, | by  | checking | whether | the policy | al- |
datastoreswerehesitanttoallowanothersystemtobeinthecritical
|     |     |     |     |     |     | lows | the target | µ-shard | to be | migrated | at that | time, and |
| --- | --- | --- | --- | --- | --- | ---- | ---------- | ------- | ----- | -------- | ------- | --------- |
pathofdataaccessestotheirsystem.ThetwootherAkkioservicesuse
whethertheµ-shardisnotalreadyintheprocessofbeing
ZippyDBregardless.
452    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

migrated. If migration is permissible, it determines the
Atomically:
optimalplacementfortheµ-shard(§4.6.2)andstartsthe a. acquire lock on u−shard
migration(§4.6.3). b. add migration to ongoing migrations list
Set src u−shard ACL to R/O;
DPS stores various information in its datastore sys-
Read u−shard from the src
tem for each µ-shard migration, including locks to pre-
Atomically:
ventmultipleconcurrentmigrationsofthesameµ-shard, − write u−shard to dest
and sufficient information needed to recover the migra- − set dest u−shard ACL to R/O
Update location−DB with new u−shard mapping
tionshouldaDPSserverfailduringthemigration(e.g.,
Delete source u−shard and ACL
fromandtolocationhandles,lockowners,etc). Aswell Set destination u−shard ACL to R/W
it maintains historical migration data: e.g., time of last Atomically:
migrationtolimitmigrationfrequency(toallowthepre- a. release lock on u−shard
b. remove migration from ongoing migr. list
ventionofµ-shardsping-ponging).
Listing 2: µ-shard migration for ZippyDB using ACLs and
transactions.Writesareblockedduringthemigration.
4.6.1 Provisioningnewµ-shards
which is proportional to the amount of available re-
Whenanewµ-shardisbeingcreated, DPSmustdecide
sources in the datacenter, taking into account, for ex-
wheretoinitiallyplacetheµ-shard. Ourtypicalstrategy
ample, CPUutilization, storagespaceusage, andIOPS.
istoselectareplicasetcollectionwithaprimaryreplica
Theper-replicasetcollectionscoreisthengeneratedby
localtotherequestingclientandsecondaryreplica(s)in
summing the individual datacenter scores on which the
oneofthemorelightlyloadeddatacenters. But,inprin-
replicasetcollectionhasapresence. Thereplicasetcol-
ciple,anyavailableshardreplicasetcollectioncouldbe
lectionwiththehighestscoreisthenselectedforplacing
chosen, so using a hash function to distribute initial µ-
thetargetµ-shard,orarandomoneincaseofatie.
shardassignmentsisalsoaviablestrategy.
Theprimaryreasonµ-shardprovisioningisdelegated Informationonwhichreplicasetcollectionsareavail-
toDPSisthatifanyAkkioclientlibraryinstancewereto able is obtained from Configurator [35], a Facebook
dothisdirectly,thenaraceconditionmightensueiftwo configuration service that each client application ser-
or more client instances decide to create the same new vice keeps up to date. Listing 1 shows a simpli-
µ-shardconcurrently. Afurtheradvantageofleveraging fied Akkio configuration for a sample application ser-
DPSisthatcurrentresourceusagecanbetakenintoac- vice. Replication configurationsprovidesamap-
countwhenplacingtheµ-shard. ping between location handles and lists of datacenters
in which the shard replicas are located. While location
handlesareopaquetoAkkio, itdoesunderstandthelist
4.6.2 Determiningoptimalµ-shardplacement
of datacenters and uses that information when deciding
wheretoplaceµ-shards. Consistency requirements
The default policy for selecting a target replica set col-
specifiesthatthisapplicationservicerequiresstrongcon-
lectionforanexistingµ-shardistochoosetheonewith
the highest score from among the available replica set sistency. Access counter service specifies which
datatousefortheaccesscounters. Migration policy
collections, excludingthosewithreplicasindatacenters
specifiesalimitonthenumberofmigrationsforeachµ-
withexceptionallyhighdiskusageorexceptionallyhigh
computing loads.6 Our implementation computes the shardtoonceevery6hours. Migrationsmaybelimited
topreventµ-shardmigrationping-ponging.
score in two steps. First, we compute a per-datacenter
scorebysummingthenumberoftimestheµ-shardwas
accessedfromthatdatacenteroverthelastXdays(where
4.6.3 µ-shardmigration
X isconfigurable),weightingmorerecentaccessesmore
strongly. The per-datacenter scores for the datacenters
Once the DPS has identified a destination replica set
on which the replica set collection has replicas are then
collection for a given µ-shard, it migrates the µ-shard
summed to generate a replica set collection score. If
from the source to a destination. Different µ-shard mi-
thereisaclearwinner,wepickthatwinner.
gration methods are used, depending on the functional-
Ifmultiplereplicasetcollectionshavethesamehigh- ityoftheapplicationservice’sunderlyingdatabase. We
est score, we take this set of replica set collections and firstdescribeµ-shardmigrationforZippyDB,whichof-
generate, for each, another score using resource usage fersaccesscontrollists(ACL’s)andtransactions. Other
data. A per-datacenter score is again generated first, databasesareconsideredfurtherbelow. Inthesedescrip-
tions,weassumestrongconsistencyofµ-sharddata. We
6 Policies can be configured to include specific thresholds that
also assume the systems run reliably during migration;
shouldn’tbebreached;e.g. tonotconsiderdatacenterswithovern%
CPUusage. migrationfailurehandlingisdescribedin(§4.6.5).
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation 453

beremovedfromthelistofongoingmigrations.
Atomically:
|     |               |      |            |     |            |      | With | this method, |     | each time | the | location | database | is  |
| --- | ------------- | ---- | ---------- | --- | ---------- | ---- | ---- | ------------ | --- | --------- | --- | -------- | -------- | --- |
| a.  | acquire       | lock | on u−shard |     |            |      |      |              |     |           |     |          |          |     |
| b.  | add migration |      | to ongoing |     | migrations | list |      |              |     |           |     |          |          |     |
updated,whichoccursthreetimes,itisnecessarytowait
| Start | double−writing |     | to  | src & | dest |     |     |     |     |     |     |     |     |     |
| ----- | -------------- | --- | --- | ----- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
forthelocationdatabaseTTLtoexpiretoensurenostale
| Wait | for location |     | info | cache | TTL to | expire |     |     |     |     |     |     |     |     |
| ---- | ------------ | --- | ---- | ----- | ------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
Copy data from source to dest accesses go to the wrong destination. This delay could
Switch reading to dest beavoidediftheunderlyingdatabasesupportsACLs(as,
Wait for location info cache TTL to expire e.g., open source Cassandra does), or if cache entries
| Switch | writing      | to  | dest | (ending | dbl−writes) |        |                         |          |              |                            |      |          |       |       |
| ------ | ------------ | --- | ---- | ------- | ----------- | ------ | ----------------------- | -------- | ------------ | -------------------------- | ---- | -------- | ----- | ----- |
|        |              |     |      |         |             |        | could be                | reliably | invalidated, |                            | then | the wait | times | could |
| Wait   | for location |     | info | cache   | TTL to      | expire |                         |          |              |                            |      |          |       |       |
|        |              |     |      |         |             |        | bereducedsubstantially. |          |              | Alsonotethatapotentialrace |      |          |       |       |
| Remove | src          |     |      |         |             |        |                         |          |              |                            |      |          |       |       |
Atomically: condition could occur with double-writes: if a write on
| a.  | release | lock | on u−shard |     |     |     |     |     |     |     |     |     |     |     |
| --- | ------- | ---- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
thesourcesucceeds,butnotonthedestination,thenthe
| b.  | remove | migration | from | ongoing |     | migr. list |     |     |     |     |     |     |     |     |
| --- | ------ | --------- | ---- | ------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
writeisobservablewhenreadingfromthesource,butnot
µ-shardmigrationforCassandrausingtimestamps
Listing3:
|                    |     |        |         |         |        |            | whenlaterreadingfromthedestination. |     |     |     |     | Weaddressthis |     |     |
| ------------------ | --- | ------ | ------- | ------- | ------ | ---------- | ----------------------------------- | --- | --- | --- | --- | ------------- | --- | --- |
| and double-writes. |     | Writes | are not | blocked | during | the migra- |                                     |     |     |     |     |               |     |     |
byalwaysfirstwritingtothedestination,beforewriting
tion.Thetimestampsareusedtomergedatawhencopying
tothesource,ondoublewrites.
Listing2liststhemethodwefirstusedforZippyDB.
4.6.4 Replicasetcollectionchanges
| First, a lock | is     | acquired       | on the | µ-shard  | to prevent | other       |                 |          |             |               |           |        |            |          |
| ------------- | ------ | -------------- | ------ | -------- | ---------- | ----------- | --------------- | -------- | ----------- | ------------- | --------- | ------ | ---------- | -------- |
| DPS instances |        | from migrating |        | the same | µ-shard.   | (The        |                 |          |             |               |           |        |            |          |
|               |        |                |        |          |            |             | The replica     | set      | collections |               | available | to     | the client | ap-      |
| lock does     | not    | prevent the    | client | from     | reading    | and writ-   |                 |          |             |               |           |        |            |          |
|               |        |                |        |          |            |             | plication       | service, | and         | in particular |           | the    | set of     | replica- |
| ing µ-shard   | data.) | The            | source | µ-shard  | ACL        | is then set |                 |          |             |               |           |        |            |          |
|               |        |                |        |          |            |             | tion topologies |          | they        | represent,    | will      | change | over       | time;    |
toreadonly(R/O).Thiseffectivelyblockswritesforthe
e.g.,toaccountforshiftsinrequesttrafficorbecauseof
| duration         | of the | migration; | however,    |     | the ZippyDB        | client |                                           |               |     |          |               |     |            |     |
| ---------------- | ------ | ---------- | ----------- | --- | ------------------ | ------ | ----------------------------------------- | ------------- | --- | -------- | ------------- | --- | ---------- | --- |
|                  |        |            |             |     |                    |        | changes                                   | in underlying |     | hardware | availability. |     | Adding     | a   |
| library embedded |        | in the     | application |     | will automatically |        |                                           |               |     |          |               |     |            |     |
|                  |        |            |             |     |                    |        | newreplicasetcollectionisstraightforward: |               |     |          |               |     | itissimply |     |
retrythewriteifthepreviousattemptwasblocked,thus
addedtotheconfigurationstateandtheDPScanbeginto
| hiding blocked |     | writes | from | the client | application | ser- |                                            |     |     |     |     |     |     |        |
| -------------- | --- | ------ | ---- | ---------- | ----------- | ---- | ------------------------------------------ | --- | --- | --- | --- | --- | --- | ------ |
|                |     |        |      |            |             |      | useit,migratingµ-shardstoitwhenbeneficial. |     |     |     |     |     |     | Remov- |
vice.7 Thesourceµ-shardisthenreadandsubsequently
|            |                 |     |         |     |                 |     | ing a replica | set | collection |     | is, however, |     | more involved. |     |
| ---------- | --------------- | --- | ------- | --- | --------------- | --- | ------------- | --- | ---------- | --- | ------------ | --- | -------------- | --- |
| written to | the destination |     | µ-shard | and | the destination | µ-  |               |     |            |     |              |     |                |     |
Thereplicasetcollectiontoberemovedisfirstdisabled
shardACLissettoR/O.Thelocationdatabaseisupdated
|          |             |          |     |     |        |             | in the configuration, |         | preventing |            | the  | DPS    | from selecting |     |
| -------- | ----------- | -------- | --- | --- | ------ | ----------- | --------------------- | ------- | ---------- | ---------- | ---- | ------ | -------------- | --- |
| with the | new µ-shard | mapping. |     | The | source | µ-shard and |                       |         |            |            |      |        |                |     |
|          |             |          |     |     |        |             | this shard            | replica | set        | collection | from | future | placement      |     |
itsACLisdeleted,thedestinationµ-shardACLissetto
|     |     |     |     |     |     |     | decisions. | Then,inanoff-lineprocess,aDPSevaluat- |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ------------------------------------- | --- | --- | --- | --- | --- | --- |
R/W,andthemigrationlockisreleased.
ePlacement()callismadeforeachµ-shardinthedis-
| Not all               | underlying | databases    |                           | support   | ACLs. | For ex-  |              |            |       |         |     |            |            |     |
| --------------------- | ---------- | ------------ | ------------------------- | --------- | ----- | -------- | ------------ | ---------- | ----- | ------- | --- | ---------- | ---------- | --- |
|                       |            |              |                           |           |       |          | abled shard, | which      | will  | cause   | the | DPS        | to migrate | the |
| ample, the            | variant    | of Cassandra |                           | currently | used  | at Face- |              |            |       |         |     |            |            |     |
|                       |            |              |                           |           |       |          | µ-shard      | to another | shard | replica | set | collection | using      | the |
| bookdoesnotofferACLs. |            |              | Hence,adifferentmigration |           |       |          |              |            |       |         |     |            |            |     |
processesdescribedabove.
| methodisneeded. |     | (SeeListing3.)  |     |        | Inthiscase, | themi-       |     |     |     |     |     |     |     |     |
| --------------- | --- | --------------- | --- | ------ | ----------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
| gration method  |     | takes advantage |     | of the | fact        | that Cassan- |     |     |     |     |     |     |     |     |
4.6.5 DPSfaultrecovery
draofferstimestampsnativelyandcanthusallowwrites
| during ongoing |     | migrations. | After | first | acquiring | a lock |          |     |             |         |     |         |          |     |
| -------------- | --- | ----------- | ----- | ----- | --------- | ------ | -------- | --- | ----------- | ------- | --- | ------- | -------- | --- |
|                |     |             |       |       |           |        | When any | of  | the servers | running |     | Akkio’s | location | or  |
ontheµ-shard,thelocationdatabaseinformationassoci-
|     |     |     |     |     |     |     | counter | services | ceases | to execute |     | (say, | due to | a hard- |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | ------ | ---------- | --- | ----- | ------ | ------- |
atedwiththeµ-shardismodifiedsothatclientwritesare
|     |     |     |     |     |     |     | ware or | software | failure), | they | can | simply | be restarted |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | --------- | ---- | --- | ------ | ------------ | --- |
doublewrittentoboththesourceanddestination,while
|                                       |     |     |     |     |     |            | sincetheirdataisreliablypersisted. |       |         |       |        | Thesituationisdif- |      |        |
| ------------------------------------- | --- | --- | --- | --- | --- | ---------- | ---------------------------------- | ----- | ------- | ----- | ------ | ------------------ | ---- | ------ |
| readscontinuetobedirectedtothesource. |     |     |     |     |     | Theµ-shard |                                    |       |         |       |        |                    |      |        |
|                                       |     |     |     |     |     |            | ferent with                        | a DPS | server, | since | it may | have               | been | in the |
data(frombeforethestartofthedouble-writing)isthen
middleofmigratingµ-shards.
| copied from | the | source | to the | destination. |     | The times- |         |      |      |       |       |            |          |     |
| ----------- | --- | ------ | ------ | ------------ | --- | ---------- | ------- | ---- | ---- | ----- | ----- | ---------- | -------- | --- |
|             |     |        |        |              |     |            | To deal | with | this | case, | every | DPS server | instance |     |
tampsassociatedwitheachwriteareusedtomergedata
|                |     |          |      |              |     |              | is assigned | a   | monotonically |     | increasing | sequence |     | num- |
| -------------- | --- | -------- | ---- | ------------ | --- | ------------ | ----------- | --- | ------------- | --- | ---------- | -------- | --- | ---- |
| appropriately. |     | Once the | copy | is complete, |     | the location |             |     |               |     |            |          |     |      |
ber(whichisobtainedfromaglobalZookeeperdeploy-
databaseismodifiedtohavereadsgotothedestination,
|                                               |     |                 |     |     |                  |     | ment [19]).   | This | sequence    |             | number   | is persisted |        | with all |
| --------------------------------------------- | --- | --------------- | --- | --- | ---------------- | --- | ------------- | ---- | ----------- | ----------- | -------- | ------------ | ------ | -------- |
| whilecontinuing                               |     | double-writing. |     | The | locationdatabase |     |               |      |             |             |          |              |        |          |
|                                               |     |                 |     |     |                  |     | state related | to   | pending     | migrations; |          | e.g.,        | in the | per µ-   |
| ismodifiedtohavewritesonlygotothedestination. |     |                 |     |     |                  | Fi- |               |      |             |             |          |              |        |          |
|                                               |     |                 |     |     |                  |     | shard lock    | that | is acquired |             | prior to | beginning    | of     | a mi-    |
nally,thedataatthesourcecanbedeletedatthesource,
|             |      |        |           |     |               |     | gration. | When | a DPS | server | instance | fails, | it  | will be |
| ----------- | ---- | ------ | --------- | --- | ------------- | --- | -------- | ---- | ----- | ------ | -------- | ------ | --- | ------- |
| the µ-shard | lock | can be | released, | and | the migration | can |          |      |       |        |          |        |     |         |
restarted,potentiallyonadifferentserver,withahigher
sequencenumber.ThenewlyrestartedDPSinstancewill
7 WithourViewStateworkload,whichhasaverylowread-write
|     |     |     |     |     |     |     | then go | through | a recovery |     | process | where | it queries | the |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------- | ---------- | --- | ------- | ----- | ---------- | --- |
ratio,writesareretriedin0.007%ofallaccesses.
454    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|     |     | Changestodatastore |     | Datastore-specific |     |     |     |     |     |     |     |     |
| --- | --- | ------------------ | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- |
tenteachtimeitisdisplayedtotheuser.ViewStatestores
| Database |     | clientlibrary |     | migrationlogic |     |     |     |     |     |     |     |     |
| -------- | --- | ------------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
thishistory,withanaveragesizeof500KB,inZippyDB.
| ZippyDBC++ |     |     |     | 100 |     |     |     |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
1,000
ZippyDBPHP 150 Requirements: ViewState data is read on the criti-
Cassandra 500 700 calpathwhendisplayingcontent,sominimizingreadla-
Queuedatastore 100 250 tenciesisimportant. Writesarenotonthecriticalpath,
| Datastore-X |     |     |     | 100 | 250 |     |     |     |     |     |     |     |
| ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
butlowwritelatenciesareimportantfortheapplication,
Table3: Linesofcodeimplementingthetwotouchpointsbe-
|     |     |     |     |     |     | as user engagement |     | tends | to  | drops if | the content | is not |
| --- | --- | --- | --- | --- | --- | ------------------ | --- | ----- | --- | -------- | ----------- | ------ |
tweenAkkioandunderlyingdatabases.
|     |     |     |     |     |     | “fresh”.    | The data                         | needs | to be | replicated | three | ways for |
| --- | --- | --- | --- | --- | --- | ----------- | -------------------------------- | ----- | ----- | ---------- | ----- | -------- |
|     |     |     |     |     |     | durability. | Strongconsistencyisarequirement. |       |       |            |       |          |
locationdatabasetoidentifyanyongoingmigrationsthat
|                |     |            |     |                 |         | Setup: | ViewState | uses | replica | set | collections | config- |
| -------------- | --- | ---------- | --- | --------------- | ------- | ------ | --------- | ---- | ------- | --- | ----------- | ------- |
| were initiated | by  | the failed | DPS | server instance | but did |        |           |      |         |     |             |         |
not complete. The sequence number for any recovered ured with two replicas in one (local) datacenter and a
|     |     |     |     |     |     | third in | a nearby | datacenter | with | the | primary | preferen- |
| --- | --- | --- | --- | --- | --- | -------- | -------- | ---------- | ---- | --- | ------- | --------- |
migrationisupdatedinordertoavoidanyconflictswith
astale,failedDPSserverinstance. tially located in the local datacenter. Akkio migrates µ-
|     |     |     |     |     |     | shardsaggressivelyforViewState. |     |     |     | Havingtheprimary |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------- | --- | --- | --- | ---------------- | --- | --- |
Foreachrecoveredmigration,theDPSserversidenti-
|            |       |             |     |           |               | replicabelocalensuresreadsarefast. |     |     |     |     | Havingtworepli- |     |
| ---------- | ----- | ----------- | --- | --------- | ------------- | ---------------------------------- | --- | --- | --- | --- | --------------- | --- |
| fies which | state | to continue | the | migration | on. This is a |                                    |     |     |     |     |                 |     |
custom piece of code that is different for each underly- cas locally ensures writes are fast given that a quorum
|               |        |     |           |          |           | existslocally. | Havingtworeplicaslocallyhasthefurther |     |     |     |     |     |
| ------------- | ------ | --- | --------- | -------- | --------- | -------------- | ------------------------------------- | --- | --- | --- | --- | --- |
| ing datastore | system | and | migration | approach | used. For |                |                                       |     |     |     |     |     |
example,inourACLbasedapproach,theDPSscansthe advantage that, should the primary fail, then the other
|     |     |     |     |     |     | canbecomeprimary. |     | Inaggregate,6differentreplicaset |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ----------------- | --- | -------------------------------- | --- | --- | --- | --- |
stateoftheµ-shardinthesourcebackendandthedesti-
collectionsareavailableforAkkiotomigrateViewState
| nation backend | to  | identify | which | steps of | the migration |     |     |     |     |     |     |     |
| -------------- | --- | -------- | ----- | -------- | ------------- | --- | --- | --- | --- | --- | --- | --- |
hadbeencompleted. Itthenresumesthemigrationfrom µ-shardsacrosswhenusing6datacenters.
Havingtheprimaryplusareplicainthesamedatacen-
| thatpointon. | Incaseoferrorsduringasinglemigration |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
step, we restart the migration. Migrations are typically tercould,however,causesomewritestogetlostshould
|     |     |     |     |     |     | an entire | datacenter | go  | down: | writes | that have | reached |
| --- | --- | --- | --- | --- | --- | --------- | ---------- | --- | ----- | ------ | --------- | ------- |
retrieduntiltheysucceed(althoughthisisconfigurable).
theprimaryandtheotherreplicainthesamedatacenter,
|              |     |     |     |     |     | buthavenotreachedthethirdreplica,willgetlost.   |     |     |     |     |     | The |
| ------------ | --- | --- | --- | --- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
| 5 Evaluation |     |     |     |     |     | ViewStateownerswerewillingtomakethistradeofffor |     |     |     |     |     |     |
thisrarescenario.
5.1 Implementationmetrics Result: Originally, ViewState data was fully repli-
|     |     |     |     |     |     | catedacrosssixdatacenters. |     |     | UsingAkkiowiththesetup |     |     |     |
| --- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | ---------------------- | --- | --- | --- |
A benefit of Akkio’s design that enhances portability is describedaboveledtoa40%smallerstoragefootprint,8
howlightweightthetouchpointsarebetweenAkkioand a 50% reduction of cross-datacenter traffic, and about a
| theunderlyingdatabases.                  |     |     | Table3liststhelinesofcode |     |          |               |           |         |           |           |          |              |
| ---------------------------------------- | --- | --- | ------------------------- | --- | -------- | ------------- | --------- | ------- | --------- | --------- | -------- | ------------ |
|                                          |     |     |                           |     |          | 60% reduction |           | in read | and write | latencies | compared | to           |
| (LoC)requiredforeachofthetwotouchpoints: |     |     |                           |     | e.g.,the |               |           |         |           |           |          |              |
|                                          |     |     |                           |     |          | the original  | non-Akkio |         | setup.    | Each      | remote   | access noti- |
ZippyDB client library only required 100-150 new or fies the DPS, resulting in approximately 20,000 migra-
| modified | LoC to | accommodate |     | Akkio, and | Akkio only |               |     |           |                        |     |     |     |
| -------- | ------ | ----------- | --- | ---------- | ---------- | ------------- | --- | --------- | ---------------------- | --- | --- | --- |
|          |        |             |     |            |            | tionsasecond. |     | SeeFig.7. | UsingAkkio,roughly5%of |     |     |     |
required 1,000 or fewer LoC of datastore-specific code theViewStatereadsandwritesgotoaremotedatacenter.
forµ-shardmigrationsinZippyDB.
5.2.2 AccessState
5.2 Usecasesanalysis
|     |     |     |     |     |     | Description: |     | AccessState | stores | information |     | with re- |
| --- | --- | --- | --- | --- | --- | ------------ | --- | ----------- | ------ | ----------- | --- | -------- |
We describe the effect Akkio had on 4 different client spect to user actions taken in response to content dis-
|                      |     |                              |     |     |     | played to | the | user. The | information |     | includes | the ac- |
| -------------------- | --- | ---------------------------- | --- | --- | --- | --------- | --- | --------- | ----------- | --- | -------- | ------- |
| applicationservices. |     | Allofthemetricswepresentwere |     |     |     |           |     |           |             |     |          |         |
gathered from our live production systems running at tion taken, what content it was related to, a timestamp
|                    |     |           |           |             |             | of when          | the action | was   | taken,   | and so | on.       | AccessState |
| ------------------ | --- | --------- | --------- | ----------- | ----------- | ---------------- | ---------- | ----- | -------- | ------ | --------- | ----------- |
| scale, driven      | by  | live user | traffic.  | This limits | our abil-   |                  |            |       |          |        |           |             |
|                    |     |           |           |             |             | data is appended |            | to by | a number | of     | different | services,   |
| ity to experiment, |     | so we     | primarily | compare     | against the |                  |            |       |          |        |           |             |
systemsthatwereinplacebeforeAkkiowasintroduced. butreadmostlybythedynamiccontentdisplaysystem.
|     |     |     |     |     |     | AccessState | stores | the | action | history, | with | an average |
| --- | --- | --- | --- | --- | --- | ----------- | ------ | --- | ------ | -------- | ---- | ---------- |
sizeof200KB,inZippyDB.Theread-writeratioforAc-
5.2.1 ViewState
cessStateisfarlowerthanitisforViewState.
|              |           |     |        |              |              | Requirements: |     | Reads | are | on the | critical | path when |
| ------------ | --------- | --- | ------ | ------------ | ------------ | ------------- | --- | ----- | --- | ------ | -------- | --------- |
| Description: | ViewState |     | stores | a history of | content pre- |               |     |       |     |        |          |           |
decidingwhatcontenttodisplay,andhencelowreadla-
| viouslyshowntoauser. |     |     | Eachtimeauserisshownsome |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
content,anadditionalsnapshotisappendedtotheView-
8Only40%becausethenumberofserverscouldn’tbefurtherre-
| Statedata. | Thedataisusedtoprioritizesubsequentcon- |     |     |     |     |     |     |     |     |     |     |     |
| ---------- | --------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ducedduetotheCPUbecomingthebottleneck.
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    455

|     |     |     |     |     |     |     | in storage | footprint, | a          | roughly | 50% reduction |          | of cross- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ---------- | ---------- | ------- | ------------- | -------- | --------- |
|     |     |     |     |     |     |     | datacenter | traffic,   | negligible |         | increase      | in read  | latency   |
|     |     |     |     |     |     |     | (0.4%)     | and a 60%  | reduction  | in      | write         | latency. | Roughly   |
0.4%ofthereadsgoremote,resultinginabout1,000mi-
|     |     |     |     |     |     |     | grationsasecond. |     | Figure7showsthatthereareroughly |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------------------------------- | --- | --- | --- | --- |
halfasmanymigrationsastherearecallstotheDPS.
|     |     |     |     |     |     |     | We also       | compared                                    | AccessState |              | read         | latencies | for a       |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ------------------------------------------- | ----------- | ------------ | ------------ | --------- | ----------- |
|     |     |     |     |     |     |     | configuration |                                             | with 3X     | replication, |              | with and  | without     |
|     |     |     |     |     |     |     | Akkio.        | FortheconfigurationwithoutAkkio,thereplicas |             |              |              |           |             |
|     |     |     |     |     |     |     | were spread   | evenly                                      | across      | all          | datacenters. |           | The results |
|     |     |     |     |     |     |     | are shown     | in Table.                                   | 4:          | without      | Akkio,       | access    | latencies   |
are7X–10Xhigher.
|     |     |     |     |     |     |     | 5.2.3 InstagramConnection-Info |                                       |          |       |      |      |            |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------ | ------------------------------------- | -------- | ----- | ---- | ---- | ---------- |
|     |     |     |     |     |     |     | Description:                   | Connection-Infostoresdataforeachuser, |          |       |      |      |            |
|     |     |     |     |     |     |     | including                      | when                                  | and from | where | they | were | online, as |
wellasotherstatusandconnectionendpointinformation.
|     |     |     |     |     |     |     | This data | is stored | on Cassandra. |     | There | are | roughly 30 |
| --- | --- | --- | --- | --- | --- | --- | --------- | --------- | ------------- | --- | ----- | --- | ---------- |
billionµ-shards.
|                                            |             |        |             |         |            |         | Requirements:                |           | This      | application |                       | service     | requires    |
| ------------------------------------------ | ----------- | ------ | ----------- | ------- | ---------- | ------- | ---------------------------- | --------- | --------- | ----------- | --------------------- | ----------- | ----------- |
| Figure 7:                                  | ViewState   | (top); | AccessState |         | (bottom):  | per-    |                              |           |           |             |                       |             |             |
|                                            |             |        |             |         |            |         | strong consistency,          |           | for       | which       | it uses               | Cassandra’s | quo-        |
| centage                                    | of accesses | to     | remote      | data,   | the number | of      |                              |           |           |             |                       |             |             |
|                                            |             |        |             |         |            |         | rumreadandwritefeatures[18]. |           |           |             | Intra-continentalquo- |             |             |
| evaluatePlacement()                        |             | calls  | to          | DPS per | second,    | and the |                              |           |           |             |                       |             |             |
|                                            |             |        |             |         |            |         | rum read                     | and write | latencies |             | are important.        |             | Originally, |
| numberofensuingµ-shardmigrationspersecond. |             |        |             |         | ForView-   |         |                              |           |           |             |                       |             |             |
|                                            |             |        |             |         |            |         | this service                 | stored    | its data  | using       | full                  | replication | across      |
StatethenumberofcallstoDPSpersecondandthenumberof
|     |     |     |     |     |     |     | fivedatacentersononecontinent, |     |     |     | butasusageinasec- |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------ | --- | --- | --- | ----------------- | --- | --- |
migrationspersecondarethesame.
|              |     |      |       |       |       |     | ond continent                 |                 | increased | substantially, |           | some            | of the data |
| ------------ | --- | ---- | ----- | ----- | ----- | --- | ----------------------------- | --------------- | --------- | -------------- | --------- | --------------- | ----------- |
|              |     | avg  | p90   | p95   |       | p99 | hadtobestoredonthatcontinent. |                 |           |                |           |                 |             |
| WithAkkio:   |     | 10ms | 23ms  | 26ms  | 34ms  |     |                               |                 |           |                |           |                 |             |
|              |     |      |       |       |       |     | Setup:                        | This            | service   | uses two       | replica   | configurations. |             |
| WithoutAkkio |     | 76ms | 151ms | 237ms | 371ms |     |                               |                 |           |                |           |                 |             |
|              |     |      |       |       |       |     | One has                       | 5X replication, |           | with           | a replica | in each         | of five     |
Table4:AccessStateclientserviceaccesslatencies. datacenters(asitsoriginalsetup). Thesecondhas3X
|                   |     |                                 |     |     |     |     | replication | with                                    | two in | the second | continent |     | and one in |
| ----------------- | --- | ------------------------------- | --- | --- | --- | --- | ----------- | --------------------------------------- | ------ | ---------- | --------- | --- | ---------- |
| tenciesareneeded. |     | However,writesarenotonthecriti- |     |     |     |     |             |                                         |        |            |           |     |            |
|                   |     |                                 |     |     |     |     | thefirst.   | Havingtworeplicastogetherensuresaquorum |        |            |           |     |            |
calpathandmoderatewritelatencyisacceptable(unlike
stayswithinthesamecontinentinthesteadystate.
| ViewState). | The | data needs | to  | be replicated | three | ways |         |                                      |     |     |     |     |     |
| ----------- | --- | ---------- | --- | ------------- | ----- | ---- | ------- | ------------------------------------ | --- | --- | --- | --- | --- |
|             |     |            |     |               |       |      | Result: | WithAkkioitwaspossibletokeepbothread |     |     |     |     |     |
butonlyneedstobeeventuallyconsistent.
andwritelatencieslowerthan50mswhichwasimportant
Setup:AccessStateusesreplicasetcollectionsconfig-
|     |     |     |     |     |     |     | to its operation, |     | compared | to  | greater than | 100ms | which |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | -------- | --- | ------------ | ----- | ----- |
uredtohavethreereplicas,eachoneinadifferentdata-
|     |     |     |     |     |     |     | would have | been | incurred | if quorums |     | went across | data- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ---- | -------- | ---------- | --- | ----------- | ----- |
center.Overall,20suchreplicasetcollections,eachwith
|             |          |                |     |      |             |     | centers. | This service | could | not | have | expanded | into the |
| ----------- | -------- | -------------- | --- | ---- | ----------- | --- | -------- | ------------ | ----- | --- | ---- | -------- | -------- |
| a different | topology | configuration, |     | plus | one replica | set |          |              |       |     |      |          |          |
secondcontinentwithoutAkkio.
collectionconfiguredtohaveareplicaineachdatacenter,
areavailableforAkkiotomigrateAccessStateµ-shards.
Akkioisconfiguredtonotmigrateµ-shardsaggressively
|     |     |     |     |     |     |     | 5.2.4 InstagramDirect |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- |
if,basedontheaccesshistory,itbelievestheremotepro-
cessingmaybetransient. Moreover,itdoesnotmigrate Description: Thisisatraditionalmessagingapplication
theprimaryreplicatothedatacenterfromwhichtheac- service that supports group messaging. Each message
cesswasmadeeventhoughitwouldleadtolowerwrite queue contains the sent messages as well as “cursors”
latencies, mainly because not doing so significantly re- that track the position in the queue for each subscriber.
duces the number of migrations needed. (Note that the Thereareroughly15billionsuchqueues,butwithmost
read-writeratioforAccessStateisfarhigherthanitisfor queueshavingasmallfootprintofafewhundredbytes.
ViewState.) The messaging application relies on Iris, a specialized
Result: Originally, AccessState data was configured Facebook-internalqueuingdatastoreservicethatguaran-
tobefullyreplicatedacrosssixdatacenters.UsingAkkio teesin-orderdelivery.(Underneath,IrisusesMySQLfor
| with the | setup | described | above | led to a | 40% decrease |     | persistentstorage.) |     |     |     |     |     |     |
| -------- | ----- | --------- | ----- | -------- | ------------ | --- | ------------------- | --- | --- | --- | --- | --- | --- |
456    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

|     |     |     |     |     |     |     | Step                         |     |     |     |     | Time(avg.) |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- | ---------- | --- |
|     |     |     |     |     |     |     | AcquireLock                  |     |     |     |     | 151ms      |     |
|     |     |     |     |     |     |     | SetSourceACLToReadOnly       |     |     |     |     | 315ms      |     |
|     |     |     |     |     |     |     | Readµ-shardfromSource        |     |     |     |     | 184ms      |     |
|     |     |     |     |     |     |     | Writeµ-shardtoDestination    |     |     |     |     | 130ms      |     |
|     |     |     |     |     |     |     | UpdateLocationinDB           |     |     |     |     | 151ms      |     |
|     |     |     |     |     |     |     | Deleteµ-shardFromSource      |     |     |     |     | 160ms      |     |
|     |     |     |     |     |     |     | SetDestinationACLtoReadWrite |     |     |     |     | 120ms      |     |
|     |     |     |     |     |     |     | ReleaseLock                  |     |     |     |     | 151ms      |     |
Table5:BreakdownforAccessStateµ-shardmigrationtimes.
onaverage.Readlatencyonthecacheaveragestoaround
|     |     |     |     |     |     |     | 1 ms. Figure  | 8     | show         | the distributions |             | of Akkio | client      |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ----- | ------------ | ----------------- | ----------- | -------- | ----------- |
|     |     |     |     |     |     |     | library-side  | read  | and write    | latencies         | after       | a        | miss in the |
|     |     |     |     |     |     |     | cache. Writes | take  | considerably |                   | longer      | because  | a quo-      |
|     |     |     |     |     |     |     | rum needs     | to be | achieved     | across            | datacenters |          | before a    |
writeisacknowledged.
AccessCounterService
Wepresentvariousmetrics
Figure8:Distributionofclient-sidelatenciesforaccessingthe from the Access Counter DB for AccessState as an ex-
Akkio location and counter databases, (not taking the cache ample. The amount of storage required for storing one
intoaccount).Readlatenciesareshowninthetopgraph;write
|     |     |     |     |     |     |     | counter | for each | of the | billion+ | users | and datacenter | is  |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | ------ | -------- | ----- | -------------- | --- |
latenciesinthebottomgraph.
about400GBintotal(unreplicated).TheAccessCounter
databasealsolivesinourZippyDBmulti-tenantdeploy-
| Requirements: |            | Iris           | is on the | critical  | path       | for Insta- |           |            |           |               |            |     |              |
| ------------- | ---------- | -------------- | --------- | --------- | ---------- | ---------- | --------- | ---------- | --------- | ------------- | ---------- | --- | ------------ |
|               |            |                |           |           |            |            | ment with | 1,100      | dedicated | shards.       | Figure     | 8   | depicts the  |
| gram Direct   | end-to-end |                | message   | delivery. |            | Both low   |           |            |           |               |            |     |              |
|               |            |                |           |           |            |            | counter   | database   | read      | and write     | latencies. |     | Neither the  |
| write and     | low        | read latencies | are       | thus      | important. | Strong     |           |            |           |               |            |     |              |
|               |            |                |           |           |            |            | reads nor | the writes | on        | this database | are        | on  | any critical |
consistencyisrequired.
|        |            |       |             |     |          |          | path. The | read-write | ratio | is about | 1:500. | In  | a typical |
| ------ | ---------- | ----- | ----------- | --- | -------- | -------- | --------- | ---------- | ----- | -------- | ------ | --- | --------- |
| Setup: | Currently, | three | datacenters |     | are used | to store |           |            |       |          |        |     |           |
day,theAccessCounterDBforViewStateprocessesbe-
| Instagram | Direct | data. | The | database | is configured | to  |     |     |     |     |     |     |     |
| --------- | ------ | ----- | --- | -------- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
tween300,000and550,000writespersecond.
| have replica | configurations |     | with | a primary | in  | each dat- |      |           |         |     |         |          |       |
| ------------ | -------------- | --- | ---- | --------- | --- | --------- | ---- | --------- | ------- | --- | ------- | -------- | ----- |
|              |                |     |      |           |     |           | Data | Placement | Service |     | The DPS | receives | about |
acenter. Further,eachreplicasethasasecondaryreplica
|     |     |     |     |     |     |     | 100,000 | evaluatePlacement() |     |     | calls | per | second. |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------------------- | --- | --- | ----- | --- | ------- |
inthesamedatacenterastheprimaryandtwoadditional
|     |     |     |     |     |     |     | However, | these | calls are | asynchronous |     | and | not on any |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----- | --------- | ------------ | --- | --- | ---------- |
replicainanotherdatacenter,foratotaloffourreplicas.
criticalpath.Migrationsaretheheavy-weightoperations
Useraccesshistoryinformationisusedtodecidewhere
|             |           |             |       |            |           |          | executed  | by the | DPS.        | Table 5 | shows   | the elapsed | time |
| ----------- | --------- | ----------- | ----- | ---------- | --------- | -------- | --------- | ------ | ----------- | ------- | ------- | ----------- | ---- |
| to place    | µ-shards; | for message |       | queues     | that are  | accessed |           |        |             |         |         |             |      |
|             |           |             |       |            |           |          | breakdown | of an  | AccessState |         | µ-shard | migration.  | The  |
| by multiple | users     | (i.e.,      | group | messaging) | placement | is       |           |        |             |         |         |             |      |
sumofalltheindividuallatenciesisrelativelyhigh;how-
determinedbyusingeachuser’saccesshistoryweighted
ever,someoftheoperationscanbeexecutedinparallel,
byrateofuseractions.
|          |       |             |             |     |                |           | different                         | migrations | can | proceed | in parallel,       |     | and migra- |
| -------- | ----- | ----------- | ----------- | --- | -------------- | --------- | --------------------------------- | ---------- | --- | ------- | ------------------ | --- | ---------- |
| Result:  | With  | Akkio,      | on average, |     | roughly        | 3,000 mi- |                                   |            |     |         |                    |     |            |
|          |       |             |             |     |                |           | tionitselfisnotonthecriticalpath. |            |     |         | Theselatencieshave |     |            |
| grations | occur | per second, | resulting   |     | in a reduction | in        |                                   |            |     |         |                    |     |            |
notbeenanissuefortheclientapplicationservicesusing
end-to-endmessagedeliverylatencyby90msatp90and
Akkiotoday;optimizingthemisleftforfuturework.
| 150msatp95.                                   |     | This,inturn,resultedinuserengagement |        |     |         |           |               |     |     |     |     |     |     |
| --------------------------------------------- | --- | ------------------------------------ | ------ | --- | ------- | --------- | ------------- | --- | --- | --- | --- | --- | --- |
| improvements,                                 |     | where the                            | number | of  | message | sends in- |               |     |     |     |     |     |     |
| creasedby0.9%overallandthenumberoftextmessage |     |                                      |        |     |         |           | 6 RelatedWork |     |     |     |     |     |     |
sendsincreasedby1.1%.
Almostalldatastoresystemshavesomeformofsharding
5.3 AnalysisofAkkioservices in order to be scalable, and offer replication to provide
highavailability;e.g.,[6,10,16,30,33].However,these
Location Service Using AccessState as an example, systemsofferlittleintermsoflocalitymanagement. For
thelocationdatabaseusesroughly200GBstoragespace example, while Cassandra supports fine-grained control
(unreplicated) to keep track of the location of each µ- of cross-datacenter replication, the control is static and
shard, withoneµ-shardforeachofFacebook’sbillion+ notbasedonaccesspatterns[23].
users. The location database is itself one of the use A number of systems manage data locality at shard
casesthatsharesamulti-tenantZippyDBdeployment. It granularity [4, 12, 29, 40]. Given their typical size, we
consumes1,200fullyreplicatedshardswiththeprimary argue that it is challenging to place shards so that most
replicasspreadevenlyacrossallregions. data accesses are local if the number of replicas is lim-
Thehitrateofthedistributedfront-endcacheis98% ited. Moreover, the overhead of migrating entire shards
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    457

ishigh,andhencethesesystemstendtobeslowtoreact useAkkio,andAkkiomanagesover100PBofdata. We
toshiftsinworkload. believethatourchoicetoimplementAkkioasaseparate
A few systems manage data locality at a granularity layerbetweentheapplicationservicesandtheirunderly-
finerthanshards. Spannersupportsµ-shardsintheform ing databases has worked out well. Separating the con-
of directories [11], its unit of data placement. Applica- cernsoflocalitymanagementontheonehand,andrepli-
tionscontrolthecontentsofadirectoryusingcommon- cation, load-balancing and failure recovery on the other
alityinkeyprefixes.However,[11]makesnomentionof hand,ledtoamuchsimplerdesignandmadeAkkiovi-
directory-levellocalitymanagement. abletoalargersetofapplicationservices.
| Kadambi | et al. | extend | Yahoo! | PNUTs | [10] | with a |     |     |     |     |     |     |     |     |
| ------- | ------ | ------ | ------ | ----- | ---- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
per-record selective replication policy [20] but only of- With our experiences deploying Akkio, we learned a
|              |              |     |       |         |           |     | numberoflessons, |     | mostofwhichcenteraroundhaving |     |     |     |     |     |
| ------------ | ------------ | --- | ----- | ------- | --------- | --- | ---------------- | --- | ----------------------------- | --- | --- | --- | --- | --- |
| fer eventual | consistency. |     | PNUTs | behaves | similarly | to  |                  |     |                               |     |     |     |     |     |
tomakeAkkiofarmoreconfigurablethanwehadantic-
| a distributed | cache | in that | some | replicas | of  | records are |     |     |     |     |     |     |     |     |
| ------------- | ----- | ------- | ---- | -------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
ipated. (1)weinitiallyplannedonstoringallofAkkio’s
| transient | and created  | on  | reads and | removed          |     | when stale; |          |            |     |           |     |        |            |     |
| --------- | ------------ | --- | --------- | ---------------- | --- | ----------- | -------- | ---------- | --- | --------- | --- | ------ | ---------- | --- |
|           |              |     |           |                  |     |             | metadata | in Akkio’s | own | datastore |     | system | (ZippyDB). |     |
| however   | data resides | on  | disk and  | a (configurable) |     | min-        |          |            |     |           |     |        |            |     |
imum number of replicas are kept up to date by prop- However,wefoundthatapplicationserviceownerswere
|         |          |             |       |      |            |     | not willing | to       | add an    | extra | cross-datastore |           | dependency |         |
| ------- | -------- | ----------- | ----- | ---- | ---------- | --- | ----------- | -------- | --------- | ----- | --------------- | --------- | ---------- | ------- |
| agating | updates. | The authors | argue | that | collecting | and |             |          |           |       |                 |           |            |         |
|         |          |             |       |      |            |     | in their    | critical | path (and | not   | willing         | to change |            | the un- |
maintainingaccessstatisticsofindividualrecordsistoo
complexandincurstoomuchoverhead. Akkio’sdesign derlyingdatastoresystemtheywerealreadyusing). This
forcedustomakethelocationmetadatastorelogicplug-
| shows this | need | not be. | Not tracking | these | fine | grained |     |     |     |     |     |     |     |     |
| ---------- | ---- | ------- | ------------ | ----- | ---- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
statisticscanleadtosub-optimaldecisions. gable so that the location metadata could be stored on
|           |            |             |      |            |       |           | the application’s |         | underlying      |     | datastore | system. |       | (2) We |
| --------- | ---------- | ----------- | ---- | ---------- | ----- | --------- | ----------------- | ------- | --------------- | --- | --------- | ------- | ----- | ------ |
| Volley    | determines | where       | to   | place data | based | on logs   |                   |         |                 |     |           |         |       |        |
|           |            |             |      |            |       |           | initially         | assumed | all application |     | services  |         | would | follow |
| that must | capture    | each access | [1]. | It does    | this  | at object |                   |         |                 |     |           |         |       |        |
granularity.Itgeneratesplacementandmigrationrecom- thesamemigrationstrategy. However,wefoundthatwe
|     |     |     |     |     |     |     | had to create | a   | separate | migration |     | strategy | for each | un- |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | -------- | --------- | --- | -------- | -------- | --- |
mendations,butleavesthecoordinationandexecutionof
|     |     |     |     |     |     |     | derlying | datastore | system | so  | as to | play to | its strengths. |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | --------- | ------ | --- | ----- | ------- | -------------- | --- |
anyresultingmigrationstotheapplication,thusmaking
|                                            |     |     |     |     |     |          | (3) We  | learned    | that migrations |        | didn’t    | need | to            | be real- |
| ------------------------------------------ | --- | --- | --- | --- | --- | -------- | ------- | ---------- | --------------- | ------ | --------- | ---- | ------------- | -------- |
| itcumbersomeforanapplicationtointegrateit. |     |     |     |     |     | Volley’s |         |            |                 |        |           |      |               |          |
|                                            |     |     |     |     |     |          | time in | all cases; | e.g.,           | moving | messenger |      | conversations |          |
designtoprocessaccesslogsofflinemakesitslowtore-
acttoshiftsinworkloadandtootherreal-timeevents. to their center of gravity once a day lead to more ef-
|     |     |     |     |     |     |     | ficient resource |     | usage, | in part | because | smarter, |     | off-line |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------ | ------- | ------- | -------- | --- | -------- |
Nomadisaprototypedistributedkey-valuestorethat
|     |     |     |     |     |     |     | placement | decisions | became |     | feasible. | More | generally, |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | --------- | ------ | --- | --------- | ---- | ---------- | --- |
supportsoverlaysasanabstraction[36]designedtohide
wefoundthatthedecisionofwhentomigratehadtobe
theprotocolsneededtocoordinateaccesstodataasitis
|          |        |              |     |      |         |         | customizable: |     | many application |     | services |     | wanted | to de- |
| -------- | ------ | ------------ | --- | ---- | ------- | ------- | ------------- | --- | ---------------- | --- | -------- | --- | ------ | ------ |
| migrated | across | datacenters. | The | unit | of data | manage- |               |     |                  |     |          |     |        |        |
ment is a container, which corresponds to an Akkio µ- lay having their µ-shards migrated by several hundred
|                 |     |       |          |       |        |           | milliseconds | after | the | first sub-optimal |     | access |     | in order |
| --------------- | --- | ----- | -------- | ----- | ------ | --------- | ------------ | ----- | --- | ----------------- | --- | ------ | --- | -------- |
| shard. However, |     | Nomad | does not | track | access | histories |              |       |     |                   |     |        |     |          |
todecreasethechancesofthemigrationinterferingwith
ortakecapacities,loads,andresource-effectivenessinto
|     |     |     |     |     |     |     | subsequent | write | accesses | (especially |     | if  | the migration |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ----- | -------- | ----------- | --- | --- | ------------- | --- |
accountasAkkiodoes.
strategyinvolvedtakingtheµ-shardofflinetowritesfor
|     |     |     |     |     |     |     | a small | duration). | (4) | We expected |     | to only | need | a few |
| --- | --- | --- | --- | --- | --- | --- | ------- | ---------- | --- | ----------- | --- | ------- | ---- | ----- |
7 ConcludingRemarks
|     |     |     |     |     |     |     | different | scoring | policies | when | making | placement |     | deci- |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------- | -------- | ---- | ------ | --------- | --- | ----- |
sions,butultimatelyhadtosupportquiteavarietyofspe-
| This paper | makes | two key | contributions. |     | First, | we in- |     |     |     |     |     |     |     |     |
| ---------- | ----- | ------- | -------------- | --- | ------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
cificscoringpolicies;e.g.,takingrecentactivityofindi-
troduceAkkio,adynamiclocalitymanagementservice.
|     |     |     |     |     |     |     | vidual end-users |     | into | account | when | making | messaging |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ---- | ------- | ---- | ------ | --------- | --- |
Second, we introduce and advocate for a finer-grained µ-shard placement decisions. (5) We found that Akkio
| notion of | datasets | called | µ-shards. | To  | our | knowledge, |     |     |     |     |     |     |     |     |
| --------- | -------- | ------ | --------- | --- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
madecapacityplanning(growthprojectionsfordifferent
Akkio is the first dynamic data locality system for geo- datacenters) significantly more difficult with the added
| distributed        | datastore | systems  |       | that migrates |              | data at µ- |           |              |     |           |               |     |           |     |
| ------------------ | --------- | -------- | ----- | ------------- | ------------ | ---------- | --------- | ------------ | --- | --------- | ------------- | --- | --------- | --- |
|                    |           |          |       |               |              |            | dimension | of locality, |     | requiring | finer-grained |     | estimates |     |
| shard granularity, |           | that can | offer | strong        | consistency, | and        |           |              |     |           |               |     |           |     |
ofdatacenterresourcegrowth.
| that can | operate | at scale. | The system |     | demonstrates | that |     |     |     |     |     |     |     |     |
| -------- | ------- | --------- | ---------- | --- | ------------ | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
it is possible, and advantageous, to capture data access Goingforward,moreapplicationsarebeingmovedto
statistics at fine granularity for making data placement runonAkkio,andmoredatastoresystemsarebeingsup-
decisions. ported (e.g., MySQL). Further, work has started using
Akkio’sdesignisreasonablysimpleandlargelybased Akkio (i) to migrate data between hot and cold storage,
ontechniqueswell-establishedinthedistributedsystems and(ii)tomigratedatamoregracefullyontonewlycre-
community. Yetwehavefoundittobeeffective(§5.2). atedshardswhenreshardingisrequiredtoaccommodate
| Sofar,severalhundredapplicationservicesatFacebook |     |     |     |     |     |     | (many)newnodes. |     |     |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- |
458    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association

Acknowledgements [11] CORBETT,J.C.,DEAN,J.,EPSTEIN,M.,FIKES,A.,FROST,
|     |     |     |     |     |     | C., | FURMAN, | J., GHEMAWAT, |     | S., GUBAREV, | A., | HEISER, |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------------- | --- | ------------ | --- | ------- |
ManyhelpedcontributetotheAkkiosystem;inparticu- C., HOCHSCHILD, P., HSIEH, W., KANTHAK, S., KOGAN,
|     |     |     |     |     |     | E., LI, | H., LLOYD, |     | A., MELNIK, | S., MWAURA, | D., | NAGLE, |
| --- | --- | --- | --- | --- | --- | ------- | ---------- | --- | ----------- | ----------- | --- | ------ |
larVictoriaDudin,HarshPoddar,DmitryGuyvoronsky;
|                     |     |                           |     |     |     | D.,   | QUINLAN,    | S., RAO, | R., ROLIG, | L., SAITO, | Y.,       | SZYMA- |
| ------------------- | --- | ------------------------- | --- | --- | --- | ----- | ----------- | -------- | ---------- | ---------- | --------- | ------ |
| fromtheZippyDBteam: |     | SankethIndarapu,SumeetUn- |     |     |     |       |             |          |            |            |           |        |
|                     |     |                           |     |     |     | NIAK, | M., TAYLOR, |          | C., WANG,  | R., AND    | WOODFORD, | D.     |
InProc.10th
gratwar,BenjaminRenard,DanielPereira,PrateekJain, Spanner: Google’sglobally-distributeddatabase.
USENIXSymp.onOperatingSystemsDesignandImplementa-
RenatoFerreira,JoannaBujnowska,IgorPozgaj,Charlie
tion(OSDI’12)(Hollywood,CA,Oct2012),pp.261–264.
| Pisuraj,TimMulhern;fromtheCassandrateam: |                  |     |               |     | Dikang |              |     |        |            |     |             |     |
| ---------------------------------------- | ---------------- | --- | ------------- | --- | ------ | ------------ | --- | ------ | ---------- | --- | ----------- | --- |
|                                          |                  |     |               |     |        | [12] CURINO, | C., | JONES, | E., ZHANG, | Y., | AND MADDEN, | S.  |
| Gu, Andrew                               | Whang, Xiangzhou |     | Xia, Abhishek |     | Maloo; |              |     |        |            |     |             |     |
Schism:Aworkload-drivenapproachtodatabasereplicationand
fromtheGenericIristeam:ChangleWang,JeremyFein,
partitioning.Proc.VLDBEndowment3,1-2(Sept.2010),48–57.
Kristina Shia; From the Instagram team: Colin Chang, [13] DECANDIA,G.,HASTORUN,D.,JAMPANI,M.,KAKULAPATI,
Jingsong Wang; from the Messaging Iris team: Rafal G., LAKSHMAN, A., PILCHIN, A., SIVASUBRAMANIAN, S.,
Szymanski, Jeffrey Bahr, Phil Lopreiato, Adrian Wang. VOSSHALL,P.,ANDVOGELS,W. Dynamo: Amazon’shighly
availablekey-valuestore.InProc.21stACMSymp.onOperating
| We also   | thank the reviewers, |          | and our | shepherd | Kang     |         |            |           |     |             |             |        |
| --------- | -------------------- | -------- | ------- | -------- | -------- | ------- | ---------- | --------- | --- | ----------- | ----------- | ------ |
|           |                      |          |         |          |          | Systems | Principles | (SOSP’07) |     | (Stevenson, | Washington, | 2007), |
| Chen, for | their constructive   | comments |         | that led | to a far |         |            |           |     |             |             |        |
pp.205–220.
betterpaper. [14] FITZPATRICK,B. DistributedcachingwithMemcached. Linux
Journal2004,124(2004),5.
References [15] GARROD, C., MANJHI, A., AILAMAKI, A., MAGGS, B.,
|     |     |     |     |     |     | MOWRY, | T., | OLSTON, | C., ANDTOMASIC, |     | A. Scalablequery |     |
| --- | --- | --- | --- | --- | --- | ------ | --- | ------- | --------------- | --- | ---------------- | --- |
[1] AGARWAL, S., DUNAGAN, J., JAIN, N., SAROIU, S., WOL- resultcachingforwebapplications. Proc.VLDBEndow.(Aug.
| MAN,A.,ANDBHOGAN,H.Volley:Automateddataplacement |     |     |     |     |     | 2008),550–561. |     |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- |
forgeo-distributedcloudservices.InProc.7thUSENIXConf.on [16] GEORGE, L. HBase: TheDefinitiveGuide, 2nded. O’Reilly
| NetworkedSystemsDesignandImplementation(NSDI’10)(San |     |     |     |     |     | Media,Inc.,2017. |     |     |     |     |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- |
Jose,California,April2010),pp.17–32.
|     |     |     |     |     |     | [17] GOOGLE. | Cloud | locations. | https://cloud.google.com/ |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------ | ----- | ---------- | ------------------------- | --- | --- | --- |
[2] AMIRI, K., PARK, S., TEWARI, R., ANDPADMANABHAN, S. about/locations/.[Online;retrieved12-April-2018].
DBProxy: Adynamicdatacacheforwebapplications. InProc. [18] HEWITT, E., ANDCARPENTER, J. Cassandra: TheDefinitive
19thIntl.Conf.onDataEngineering(ICDE’03)(Bangalore,In-
Guide,2ed.O’ReillyMedia,2016.
dia,March2003),pp.821–831.
|                |             |     |               |           |        | [19] HUNT, | P., KONAR, |     | M., JUNQUEIRA, | F.  | P., AND REED, | B.  |
| -------------- | ----------- | --- | ------------- | --------- | ------ | ---------- | ---------- | --- | -------------- | --- | ------------- | --- |
| [3] ANNAMALAI, | M. ZippyDB: |     | A distributed | key-value | store. |            |            |     |                |     |               |     |
ZooKeeper:Wait-freecoordinationforInternet-scalesystems.In
TalkatData@Scale:https://code.facebook.com/posts/
Proc.USENIXAnnualTechnicalConference(USENIXATC’10)
371721473024046/inside-data-scale-2015,June2015.
(Boston,MA,2010),pp.145–158.
[4] ARDEKANI,M.S.,ANDTERRY,D.B.Aself-configurablegeo- [20] KADAMBI, S., CHEN, J., COOPER, B. F., LOMAX, D., RA-
replicated cloud storage system. In Proc 11th USENIX Symp. MAKRISHNAN,R.,SILBERSTEIN,A.,TAM,E.,ANDGARCIA-
on Operating Systems Design and Implementation (OSDI’14) MOLINA,H. Whereintheworldismydata. InProc.34thIntl.
(Broomfield,CO,October2014),pp.367–381. Conf.onVeryLargeDataBases(VLDB’11)(Seattle,Washing-
[5] BRONSON,N.,AMSDEN,Z.,CABRERA,G.,CHAKKA,P.,DI- ton,August2011),pp.1040–1050.
MOV,P.,DING,H.,FERRIS,J.,GIARDULLO,A.,KULKARNI,
|     |     |     |     |     |     | [21] KIRSCH, | J., | AND AMIR, | Y.  | Paxos for system | builders: | An  |
| --- | --- | --- | --- | --- | --- | ------------ | --- | --------- | --- | ---------------- | --------- | --- |
S.,LI,H.C.,ETAL.TAO:Facebook’sdistributeddatastorefor overview.InProc.2ndWorkshoponLarge-ScaleDistributedSys-
thesocialgraph.InProc.USENIXAnnualTechnicalConference temsandMiddleware(LADIS’08)(YorktownHeights,NY,2008),
| (USENIXATC’13)(SanJose,CA,June2013),pp.49–60. |     |     |     |     |     | ACM,pp.3:1–3:6. |     |     |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- | --- |
[6] CATTELL,R. ScalableSQLandNoSQLdatastores. SIGMOD [22] KREIFELDT, E. Myriad factors conspire to lower subma-
Rec.39,4(May2011),12–27. rine bandwidth prices. http://www.lightwaveonline.
com/articles/2016/08/myriad-factors-conspire-
| [7] CHABCHOUB, | Y., AND | HEBRAIL, | G. SlidingHyperLogLog: |     |     |     |     |     |     |     |     |     |
| -------------- | ------- | -------- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Estimating cardinality in a data stream over a sliding window. to-lower-submarine-bandwidth-prices.html, August
|     |     |     |     |     |     | 2016. | [Online; | posted | 31-August-2016 |     | — original | source: |
| --- | --- | --- | --- | --- | --- | ----- | -------- | ------ | -------------- | --- | ---------- | ------- |
InProc.IEEEIntl.Conf.onDataMiningWorkshops(Sydney,
TeleGeographyhttps://www.telegeography.com].
Australia,Dec2010),pp.1297–1303.
|           |                |        |           |          |          | [23] LAKSHMAN,           |     | A., ANDMALIK, |                              | P. Cassandra: | Adecentralized |     |
| --------- | -------------- | ------ | --------- | -------- | -------- | ------------------------ | --- | ------------- | ---------------------------- | ------------- | -------------- | --- |
| [8] CHEN, | G. J., WIENER, | J. L., | IYER, S., | JAISWAL, | A., LEI, |                          |     |               |                              |               |                |     |
|           |                |        |           |          |          | structuredstoragesystem. |     |               | SIGOPSOperatingSystemsReview |               |                |     |
R.,SIMHA,N.,WANG,W.,WILFONG,K.,WILLIAMSON,T.,
44,2(Apr.2010),35–40.
| AND   | YILMAZ, S. Realtime | data          | processing | at Facebook.     | In  |                 |     |                         |     |                   |     |     |
| ----- | ------------------- | ------------- | ---------- | ---------------- | --- | --------------- | --- | ----------------------- | --- | ----------------- | --- | --- |
|       |                     |               |            |                  |     | [24] LAMPORT,L. |     | Thepart-timeparliament. |     | ACMTransactionson |     |     |
| Proc. | 2016 Intl. Conf.    | on Management | of         | Data (SIGMOD’16) |     |                 |     |                         |     |                   |     |     |
ComputerSystems16,2(May1998),133–169.
(SanFrancisco,California,2016),pp.1087–1098.
|                |                                            |     |     |     |     | [25] LAMPORT, | L.  | Paxosmadesimple. |     | ACMSIGACTNews(Dis- |     |     |
| -------------- | ------------------------------------------ | --- | --- | --- | --- | ------------- | --- | ---------------- | --- | ------------------ | --- | --- |
| [9] CHESTER,D. | Consideringtherealcostofpubliccloudstorage |     |     |     |     |               |     |                  |     |                    |     |     |
vs.on-premisesobjectstorage,June2017. [Online;posted23- tributedComputingColumn)32,4(Dec2001),51–58.
| June-2017].  |                     |     |                |     |         |                                         |     |             |     | BigData: | PrinciplesandBest |     |
| ------------ | ------------------- | --- | -------------- | --- | ------- | --------------------------------------- | --- | ----------- | --- | -------- | ----------------- | --- |
|              |                     |     |                |     |         | [26] MARZ,                              | N., | AND WARREN, | J.  |          |                   |     |
|              |                     |     |                |     |         | PracticesofScalableRealtimeDataSystems. |     |             |     |          | ManningPublica-   |     |
| [10] COOPER, | B.F., RAMAKRISHNAN, |     | R.,SRIVASTAVA, |     | U.,SIL- |                                         |     |             |     |          |                   |     |
tionsCo.,Greenwich,CT,USA,2015.
| BERSTEIN, | A., BOHANNON, |     | P., JACOBSEN, | H.-A., | PUZ, N., |     |     |     |     |     |     |     |
| --------- | ------------- | --- | ------------- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- |
WEAVER,D.,ANDYERNENI,R.PNUTS:Yahoo!’shosteddata [27] NISHTALA,R.,FUGAL,H.,GRIMM,S.,KWIATKOWSKI,M.,
servingplatform. Proc.oftheVLDBEndowment1, 2(2008), LEE,H.,LI,H.C.,MCELROY,R.,PALECZNY,M.,PEEK,D.,
| 1277–1288. |     |     |     |     |     | SAAB,P.,STAFFORD,D.,TUNG,T.,ANDVENKATARAMANI, |     |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- |
USENIX Association 13th USENIX Symposium on Operating Systems Design and Implementation    459

V.ScalingMemcacheatFacebook.InProc.10thUSENIXConf. [35] TANG,C.,KOOBURAT,T.,VENKATACHALAM,P.,CHANDER,
on Networked Systems Design and Implementation (NSDI’13) A.,WEN,Z.,NARAYANAN,A.,DOWELL,P.,ANDKARL,R.
(Lombard,IL,2013),pp.385–398. HolisticconfigurationmanagementatFacebook. InProc.25th
|              |        |               |                   |     | Symp. on Operating | Systems | Principles (SOSP’15) | (Monterey, |
| ------------ | ------ | ------------- | ----------------- | --- | ------------------ | ------- | -------------------- | ---------- |
| [28] NUFIRE, | T. The | cost of cloud | storage. https:// |     |                    |         |                      |            |
California,2015),pp.328–343.
www.backblaze.com/blog/cost-of-cloud-storage,June
2017.[Online;posted29-June-2017]. [36] TRAN,N.,AGUILERA,M.K.,ANDBALAKRISHNAN,M. On-
|     |     |     |     |     | line migration | for geo-distributed | storage systems. | In Proc. |
| --- | --- | --- | --- | --- | -------------- | ------------------- | ---------------- | -------- |
[29] PN,S.,SIVAKUMAR,A.,RAO,S.,ANDTAWARMALANI,M.
USENIXAnnualTechnicalConference(USENICATC’11)(Port-
D-tunes:Selftuningdatastoresforgeo-distributedinteractiveap-
land,Oregon,June2011),pp.201–215.
| plications. | InProc.oftheACMSIGCOMM2013Conferenceon |     |     |     |     |     |     |     |
| ----------- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
SIGCOMM(SIGCOMM’13)(HongKong,2013),pp.483–484. [37] WIKIPEDIA CONTRIBUTORS. Shard (database architecture)
[30] PLUGGE, E., HOWS, D., MEMBREY, P., HAWKINS, T. — Wikipedia. https://en.wikipedia.org/w/index.
AND
TheDefinitiveGuidetoMongoDB:Acompleteguidetodealing php?title=Shard_(database_architecture)&oldid=
845931919,2018.[Online;accessed14-September-2018].
withBigDatausingMongoDB,3rded.Apress,2015.
|     |     |     |     | [38] | WOODS, A., | AND HARRISON, | D. How to | leverage geo- |
| --- | --- | --- | --- | ---- | ---------- | ------------- | --------- | ------------- |
[31] ROWLING,J.K.HarryPotterandtheGobletofFire.Thorndike
partitioning.https://www.cockroachlabs.com/blog/geo-
Press,2000.
|              |                      |                                 |                  |     | partitioning-two/,April2018. |     | [Online;retrieved12-April- |     |
| ------------ | -------------------- | ------------------------------- | ---------------- | --- | ---------------------------- | --- | -------------------------- | --- |
| [32] SHAROV, | A., SHRAER,          | A., MERCHANT,                   | A., AND STOKELY, |     | 2018].                       |     |                            |     |
| M.           | Takemetoyourleader!: | Onlineoptimizationofdistributed |                  |     |                              |     |                            |     |
storage configurations. Proc. of the VLDB Endowment 8, 12 [39] WU,Z.,BUTKIEWICZ,M.,PERKINS,D.,KATZ-BASSETT,E.,
|                   |     |     |     |     | MADHYASTHA,        | H. V.    | SPANStore: Cost-effective | geo-     |
| ----------------- | --- | --- | --- | --- | ------------------ | -------- | ------------------------- | -------- |
| (2015),1490–1501. |     |     |     |     | AND                |          |                           |          |
|                   |     |     |     |     | replicated storage | spanning | multiple cloud services.  | In Proc. |
[33] STRICKLAND,R.Cassandra3.xHighAvailability,2nded.Packt 24th ACM Symp. on Operating Systems Principles (SOSP’13)
PublishingLtd,2016. (Farminton,Pennsylvania,November2013),pp.292–308.
| [34] TAI, | A., KRYCZKA, | A., KANAUJIA, | S., PETERSEN, C., |     |     |     |     |     |
| --------- | ------------ | ------------- | ----------------- | --- | --- | --- | --- | --- |
[40] YU,H.,ANDVAHDAT,A.Minimalreplicationcostforavailabil-
| ANTONOV, | M., WALIJI, | M., JAMIESON, | K., FREEDMAN, |     |     |     |     |     |
| -------- | ----------- | ------------- | ------------- | --- | --- | --- | --- | --- |
ity.InProc.21stAnnualSymp.onPrinciplesofDistributedCom-
| M.J.,ANDCIDON,A.                               |     | Liverecoveryofbitcorruptionsindata- |     |     |                  |            |                         |         |
| ---------------------------------------------- | --- | ----------------------------------- | --- | --- | ---------------- | ---------- | ----------------------- | ------- |
|                                                |     |                                     |     |     | puting (PODC’02) | (Monterey, | California, July 2002), | pp. 98– |
| centerstoragesystems.CoRRabs/1805.02790(2018). |     |                                     |     |     | 107.             |            |                         |         |
460    13th USENIX Symposium on Operating Systems Design and Implementation USENIX Association