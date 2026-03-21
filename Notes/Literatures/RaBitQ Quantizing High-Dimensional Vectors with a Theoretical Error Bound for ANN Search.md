RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical
Error Bound for Approximate Nearest Neighbor Search
JianyangGao ChengLong∗
jianyang.gao@ntu.edu.sg c.long@ntu.edu.sg
NanyangTechnologicalUniversity NanyangTechnologicalUniversity
Singapore Singapore
ABSTRACT targettoefficientlyestimatethedistancesbetweenthedatavectors
Searchingforapproximatenearestneighbors(ANN)inthehigh- andqueryvectorsduringthequeryphasetoshortlistalistofcan-
dimensionalEuclideanspaceisapivotalproblem.Recently,with didates,whichwouldthenbere-rankedbasedonexactdistances
thehelpoffastSIMD-basedimplementations,ProductQuantization forfindingtheNN.Specifically,duringtheindexphase,they(1)
(PQ)anditsvariantscanoftenefficientlyandaccuratelyestimate constructaquantizationcodebookand(2)findforeachdatavector
thedistancesbetweenthevectorsandhaveachievedgreatsuccess thenearestvectorinthecodebookasitsquantizedvector.The
inthein-memoryANNsearch.Despitetheirempiricalsuccess,we quantizedvectorisrepresentedandstoredasashortquantization
notethatthesemethodsdonothaveatheoreticalerrorboundand code(e.g.,theIDofthequantizeddatavectorinthecodebook).
areobservedtofaildisastrouslyonsomereal-worlddatasets.Moti- Duringthequeryphase,they(1)pre-computethe(squared)dis-
vatedbythis,weproposeanewrandomizedquantizationmethod tances1betweenthequeryandthevectorsinthecodebookwhen
namedRaBitQ,whichquantizes𝐷-dimensionalvectorsinto𝐷-bit aquerycomesand(2)foradatavector,theyadoptthedistancesbe-
strings. RaBitQ guarantees a sharp theoretical error bound and tweenthequeryvectoranditsquantizeddatavector(whichcanbe
providesgoodempiricalaccuracyatthesametime.Inaddition, computedbylookingupthepre-computedvalues)astheestimated
weintroduceefficientimplementationsofRaBitQ,supportingto distances.Recently,withthehelpofthefastSIMD-basedimplemen-
estimatethedistanceswithbitwiseoperationsorSIMD-basedop- tation[4,5],PQhasachievedgreatsuccessinthein-memoryANN
erations. Extensive experiments on real-world datasets confirm search[37,43,48].Inparticular,onmanyreal-worlddatasets,the
that(1)ourmethodoutperformsPQanditsvariantsintermsof methodcanefficientlyestimatethedistanceswithhighaccuracy.
accuracy-efficiencytrade-offbyaclearmarginand(2)itsempirical Despite their empirical success on many real-world datasets,
performanceiswell-alignedwithourtheoreticalanalysis. tothebestofourknowledge,noneofPQanditsvariants[8,34,
36,45,66–68,83,85,95]providetheoreticalerrorboundsonthe
ACMReferenceFormat:
JianyangGaoandChengLong.2018.RaBitQ:QuantizingHigh-Dimensional estimateddistances.Thisisbecausetheyloseguaranteesinboth
VectorswithaTheoreticalErrorBoundforApproximateNearestNeighbor (1)thecodebookconstructioncomponentand(2)thedistancees-
Search.InProceedingsofInProceedingsofthe2024InternationalConference timationcomponent.CodebookConstruction:Theyconstructthe
onManagementofData(SIGMOD’24).ACM,NewYork,NY,USA,22pages. codebookoftenviaapproximatelysolvinganoptimizationprob-
https://doi.org/XXXXXXX.XXXXXXX lemforaheuristicobjectivefunction,e.g.,PQconductsKMeans
clusteringonthesub-segmentsofthedatavectorsandusesthe
1 INTRODUCTION setoftheproductsofclustercentroidsasthecodebook.However,
Searchingforthenearestneighbor(NN)inthehigh-dimensional duetotheirheuristicnature,itisoftendifficulttoanalyzetheir
Euclideanspaceispivotalforvariousapplicationssuchasinfor- resultstheoretically(e.g.,notheoreticalresultshavebeenachieved
mationretrieval[60],datamining[16],andrecommendations[77]. onthedistancebetweenadatavectoranditsnearestvectorinthe
However, the curse of dimensionality [39, 90] makes exact NN codebook (i.e., its quantized vector)). DistanceEstimation: They
queriesonextensivevectordatabasespracticallyinfeasibledueto estimatethedistancebetweenadatavectorandaqueryvector
theirlongresponsetime.Tostrikeabalancebetweentimeandac- withthatbetweenthequantizeddatavectorandthequeryvector,
curacy,researchersoftenexploreitsrelaxedcounterpart,knownas i.e.,theysimplytreatthequantizeddatavectorasthedatavector
approximatenearestneighbor(ANN)search[18,34,37,45,65,71]. forcomputingthedistance.Whilethislooksintuitive,itdoesnot
ProductQuantization(PQ)anditsvariantsareafamilyofpopu- comewithatheoreticalerrorboundontheapproximation.The
larmethodsforANN[8,34,36,45,66–68,83,85,95].Thesemethods lackofatheoreticalerrorboundindicatesthatthesemethodsmay
unpredictablyfailanytime,moderatelyorseverely,whentheyare
∗ChengLongisthecorrespondingauthor.
deployedinreal-worldsystemstohandlenewdatasetsandqueries
Permissiontomakedigitalorhardcopiesofallorpartofthisworkforpersonalor whichtheyhavenotbeentestedon.Infact,suchfailurehasbeen
classroomuseisgrantedwithoutfeeprovidedthatcopiesarenotmadeordistributed observedonpublicreal-worlddatasetswhicharewidelyadopted
forprofitorcommercialadvantageandthatcopiesbearthisnoticeandthefullcitation
tobenchmarkANNsearch.Forexample,onthedatasetMSong,PQ
onthefirstpage.CopyrightsforcomponentsofthisworkownedbyothersthanACM
mustbehonored.Abstractingwithcreditispermitted.Tocopyotherwise,orrepublish, (withthefastSIMD-basedimplementation[4,5])incursmorethan
topostonserversortoredistributetolists,requirespriorspecificpermissionand/ora 50%ofaveragerelativeerrorontheestimateddistancesbetween
fee.Requestpermissionsfrompermissions@acm.org.
thequeryanddatavectors,whichcausesdisastrousrecallofANN
SIGMOD’24,June08–15,2024,Santiago,Chile
©2018AssociationforComputingMachinery.
ACMISBN978-1-4503-XXXX-X/18/06...$15.00
https://doi.org/XXXXXXX.XXXXXXX 1Bydistances,werefertothesquareddistanceswithoutfurtherspecification.
4202
yaM
12
]BD.sc[
1v79421.5042:viXra

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
search(e.g.,ithasnomorethan60%recallevenwithre-ranking distancesasexplainedearlier.Table1providessomecomparison
applied,asshowninSection5.2.3). betweenRaBitQandPQanditsvariants.
Inthispaper,weproposeanewquantizationmethod,whichpro- Wesummarizeourmajorcontributionsasfollows.
videsunbiasedestimationonthedistancesandachievesasharp2
(1) Weproposeanewquantizationmethod,namelyRaBitQ.(1)
theoreticalerrorbound.Thenewmethodachievesthiswithcare-
Itconstructsthecodebookviarandomlytransformingbi-
fulandintegrateddesigninboththecodebookconstructionand
valuedvectors.(2)Itdesignsanunbiaseddistanceestimator
distanceestimationcomponents.CodebookConstruction:Itfirst
withasharpprobabilisticerrorbound.
normalizes the data vectors in order to align them on the unit
(2) Weintroduceefficientimplementationsofcomputingthe
hypersphereinthe𝐷-dimensionalspace.Itthenconstructsthe
distanceestimatorforRaBitQ.Ourimplementationismore
codebookby(1)con
√
structinga
√
setof2𝐷 bi-valuedvectorswhose
efficientthanitscounterpartofPQanditsvariantswhen
coordinatesare−1/ 𝐷or+1/ 𝐷(i.e.,thesetconsistsofthever-
estimatingthedistanceforasingledatavectorandiscompa-
ticesofahypercube,whichevenlyspreadontheunithypersphere)
rablyfastwhenestimatingthedistancesforabatchofdata
and(2) randomlyrotating thebi-valuedvectorsby multiplying
vectorswithquantizationcodesofsimilarlengths.
eachwitharandomorthogonalmatrix 3 (i.e.,itperformsatype
(3) Weconductextensiveexperimentsonreal-worlddatasets,
ofJohnson-LindenstraussTransformation[49],JLTinshort).For
which show that (1) RaBitQ provides more accurate esti-
each data vector, its nearest vector from the codebook is taken
mateddistancesthanPQ(anditsvariants)evenwhenthe
asthequantizedvector.Sinceeachquantizedvectorisarotated
formerusesshortercodesthanthelatterbyroughlyahalf
𝐷-dimensionalbi-valuedvector,werepresentitsquantizationcode
(which implies the accuracy gap would be further larger
asabitstringoflength𝐷,where0and1indicatethetwodistinct
whenbothmethodsusecodesofsimilarlengths);(2)Ra-
values.Therationaleofthecodebookconstructionisthatithasa
BitQworksstablywellonalldatasetstestedincludingsome
cleargeometricinterpretation(i.e.,thevectorsinthecodebookare
onwhichPQ(anditsvariants)fail(whichiswellaligned
asetofrandomlyrotatedvectorsontheunithypersphere)such
withthetheoreticalresults);(3)RaBitQissuperioroverPQ
thatitispossibletoanalyzethegeometricrelationshipamongthe
(anditsvariants)intermsoftime-accuracytrade-offsfor
datavectors,theirquantizedvectorsandthequeryvectorsexplic-
in-memoryANNbyaclearmarginonalldatasetstested;
itly.DistanceEstimation:Wecarefullydesignanestimatorofthe
and(4)RaBitQhasitsempiricalperformancewell-aligned
distancebetweenadatavectorandaqueryvectorbyleveraging
withthetheoreticalanalysis.
theaforementionedgeometricrelationship.Weprovethattheesti-
Theremainderofthepaperisorganizedasfollows.Section2in-
matorisunbiasedandhasasharpprobabilisticerrorboundwith
troducestheANNsearchandPQanditsvariants.Section3presents
thehelpofplentifultheoreticaltoolsabouttheJLT[28,52,82].This
ourRaBitQmethod.Section4illustratestheapplicationofRaBitQ
isincontrasttoPQanditsvariants,whichsimplytreatthequan-
tothein-memoryANNsearch.Section5providesextensiveexperi-
tizedvectorasthedatavectorforestimatingthedistances,which
mentalstudiesonreal-worlddatasets.Section6discussesrelated
isbiasedandprovidesnotheoreticalerrorbound.Wecallthenew
work.Section7presentstheconclusionanddiscussion.
quantizationmethod,whichusesrandomlytransformedbi-valued
vectorsforquantizingdatavectors,RaBitQ.ComparedwithPQand
itsvariants,RaBitQhasitssuperioritynotonlyinprovidingerror 2 ANNQUERYANDQUANTIZATION
boundsintheory,butalsoinestimatingthedistanceswithsmaller
ANNQuery.Supposethatwehaveadatabaseof𝑁 datavectors
empiricalerrorsevenwithshorterquantizationcodesbyroughlya
inthe𝐷-dimensionalEuclideanspace.Theapproximatenearest
half(asverifiedonallthetesteddatasetsshowninSection5.2.1).
neighbor(ANN)searchqueryistoretrievethenearestvectorfrom
Wefurtherintroducetwoefficientimplementationsforcomput-
thedatabaseforagivenqueryvectorq.Thequestionisusually
ingthevalueofRaBitQ’sdistanceestimator,namelyoneforasingle
extendedtothequeryofretrievingthe𝐾 nearestneighbors.For
datavectorandtheotherforabatchofdatavectors.Fortheformer,
the ease of narrative, we assume that 𝐾 = 1 in our algorithm
ourimplementationisbasedonsimplebitwiseoperations-recall
description, while all of the proposed techniques can be easily
thatourquantizationcodesarebitstrings.Ourimplementationis
adaptedtoageneral𝐾.Wefocusonthein-memoryANN,which
onaverage3xfasterthantheoriginalimplementationofPQwhich
assumesthatalltherawdatavectorsandindexescanbehostedin
reliesonlookinguptablesinRAMwhilereachingthesameaccu-
themainmemory[4–6,30,32,58,65].
racy(asshowninSection5.2.1).Notethatforasingledatavector,
theSIMD-basedimplementationofPQ[4,5]isnotfeasibleasit ProductQuantization.ProductQuantization(PQ)anditsvari-
requirestopackthequantizationcodesinabatchandreorganize antsareafamilyofpopularmethodsforANN[8,34,36,45,66–
theirlayoutcarefully.Forthelatter,thesamestrategyofthefast 68,83,85,95](forthediscussiononabroaderrangeofquantization
SIMD-basedimplementation[4,5]canbeadoptedseamlessly,and methods,seeSection6).Foraqueryvectorandadatavector,these
thusitachievessimilarefficiencyasexistingSIMD-basedimplemen- methodstargettoefficientlyestimatetheirdistancebasedonsome
tationofPQdoeswhensimilarlengthquantizationcodesareused pre-computedshortquantizationcodes.Specifically,forPQ,itsplits
-inthiscase,ourmethodwouldprovidemoreaccurateestimated the𝐷-dimensionalvectorsinto𝑀sub-segments(eachsub-segment
has𝐷/𝑀dimensions).Foreachsub-segment,itperformsKMeans
2Theerrorboundissharpinthesensethatitachievestheasymptoticoptimalityshown clusteringonthe𝐷/𝑀-dimensionalvectorstoobtain2𝑘 clusters
in[3].DetaileddiscussionscanbefoundinSection3.2.2.
andthentakesthecentroidsoftheclustersasasub-codebookwhere
3Wenotethatwedonotexplicitlymaterializethecodebook,butmaintainitconceptu-
ally,asexistingquantizationmethodssuchasPQdo. 𝑘isatunableparameterwhichcontrolsthesizeofthesub-codebook

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
Table1:ComparisonbetweenRaBitQandPQanditsvariants.More(cid:56)’sindicatesbetterefficiency.
|     | RaBitQ(new) |     |     | PQanditsvariants |     |     |     |
| --- | ----------- | --- | --- | ---------------- | --- | --- | --- |
Codebook Randomlytransformedbi-valuedvectors. Cartesianproductofsub-codebooks.
QuantizationCode Abitstring. Asequenceof4-bit/8-bitunsignedintegers.
DistanceEstimator Unbiasedandprovidesasharperrorbound. Biasedandprovidenoerrorbound.
Implementation(single) Bitwiseoperations.(cid:56)(cid:56) LookinguptablesinRAM.(cid:56)
Implementation(batch) FastSIMD-basedoperations.(cid:56)(cid:56)(cid:56) FastSIMD-basedoperations.(cid:56)(cid:56)(cid:56)
(𝑘 =8bydefault).ThecodebookofPQisthenformedbytheCarte- Table2:Notations.
sianproductofthesub-codebooksofthesub-segmentsandthushas Notation Definition
thesizeof(2𝑘)𝑀.Correspondinglyeachquantizationcodecanbe
|                                                            |     |     |     | ,q𝑟 Therawdataandqueryvectors.        |     |     |     |
| ---------------------------------------------------------- | --- | --- | --- | ------------------------------------- | --- | --- | --- |
| representedasan𝑀-sizedsequenceof𝑘-bitunsignedintegers.Dur- |     |     |     | o𝑟                                    |     |     |     |
|                                                            |     |     |     | o,q Thenormalizeddataandqueryvectors. |     |     |     |
ingthequeryphase,asymmetricdistancecomputationisadopted
|     |     |     |     | C,C𝑟𝑎𝑛𝑑 Thequantizationcodebook,itsrandomizedversion. |     |     |     |
| --- | --- | --- | --- | ----------------------------------------------------- | --- | --- | --- |
toestimatethedistance[45].Inparticular,itpre-processes𝑀look-
|     |     |     |     | 𝑃 Arandomorthogonaltransformationmatrix. |     |     |     |
| --- | --- | --- | --- | ---------------------------------------- | --- | --- | --- |
up-tables(LUTs)foreachsub-codebookwhenaquerycomes.The
|     |     |     |     | x¯ ThecodeinCs.t.𝑃x¯isthequantizedvectorofo. |     |     |     |
| --- | --- | --- | --- | -------------------------------------------- | --- | --- | --- |
𝑖thLUTcontains2𝑘numberswhichrepresentthesquareddistances
|                                                          |     |     |     | ThequantizedvectorofoinC𝑟𝑎𝑛𝑑 |     | ,i.e.,o¯ | =𝑃x¯. |
| -------------------------------------------------------- | --- | --- | --- | ---------------------------- | --- | -------- | ----- |
| betweenthevectorsinthe𝑖thsub-codebookand𝑖thsub-segmentof |     |     |     | o¯                           |     |          |       |
Thequantizationcodeofoasa𝐷-bitstring.
x¯𝑏
thequeryvector.Foragivenquantizationcode,bylookingupand Theinverselytransformedqueryvector,i.e.,𝑃−1
|     |     |     |     | q′  |     |     | q.  |
| --- | --- | --- | --- | --- | --- | --- | --- |
accumulatingthevaluesintheLUTsfor𝑀times,PQcancompute
|     |     |     |     | q¯ Thequantizedqueryvectorofq′. |     |     |     |
| --- | --- | --- | --- | ------------------------------- | --- | --- | --- |
anestimateddistance.
|     |     |     |     | q¯𝑢 Theunsignedintegerrepresentationofq¯. |     |     |     |
| --- | --- | --- | --- | ----------------------------------------- | --- | --- | --- |
Recently,[4,5]proposeaSIMD-basedfastimplementationfor
PQ(PQFastScan,PQx4fsinshort).Theyspeedupthelook-up whosedistancefromthequeryiswithintheradius𝑟).Duetothe
relaxationfactor𝑐,therecanbemanythatsatisfythestatement.
andaccumulationoperationssignificantly,makingPQanimpor-
tantcomponentinmanypopularlibrariesforin-memoryANN Theguaranteeofreturninganyofthemdoesnothelptoproduce
searchsuchasFaissfromMeta[48],ScaNNfromGoogle[37]and highrecallforANNsearch.Incontrast,aguaranteeonthedis-
NGT-QGfromYahooJapan[43].Atitscore,unliketheoriginal tanceestimationcanhelptodecidewhetheradatavectorshould
implementationofPQwhichreliesonlookinguptheLUTsinRAM, bere-rankedforachievinghighrecall(seeSection4).
[4,5]proposetohosttheLUTsinSIMDregistersandlookupthe
LUTswiththeSIMDshuffleinstructions.Toachieveso,themethod 3 THERABITQMETHOD
makesseveralmodificationsonPQ.First,inordertofittheLUTs Inthissection,wepresentthedetailsofRaBitQ.InSection3.1,
intotheAVX2256-bitregisters,itmodifiestheoriginalsettingof wepresenttheindexphaseofRaBitQ,whichnormalizesthedata
𝑘 =8to𝑘 =4sothatineachLUT,thereareonly24floating-point
vectors(Section3.1.1),constructsacodebook(Section3.1.2)and
numbers.ItfurtherquantizesthenumbersintheLUTtobe8-bit computesthequantizedvectorsofdatavectors(Section3.1.3).In
unsigned integers so that one LUT takes the space of only 128 Section3.2,weintroducethedistanceestimatorofRaBitQ,which
(24×8)bits.Thus,oneAVX2256-bitregisterisabletohosttwo is unbiased and provides a rigorous theoretical error bound. In
LUTs.Second,inordertolookuptheLUTsefficiently,themethod Section3.3,weillustratehowtoefficientlycomputethevalueof
packsevery32quantizationcodesinabatchandreorganizestheir
theestimator.InSection3.4,wesummarizetheRaBitQmethod.
layout.Inthiscase,aseriesofoperationscanestimatethedistances Table2liststhefrequentlyusednotationsandtheirdefinitions.
for32datavectorsallatonce.Withoutfurtherspecification,byPQ,
werefertoPQx4fsbydefaultbecausewithoutthefastSIMD-based 3.1 QuantizingtheDataVectorswithRaBitQ
implementation,theefficiencyofPQismuchlesscompetitivein
3.1.1 ConvertingtheRawVectorsintoUnitVectorsviaNormaliza-
thein-memoryANNsearch[4,5](seeSection5.2.1).
tion. Wenotethatdirectlyconstructingacodebookfortheraw
Nevertheless,noneofPQanditsvariantsprovideatheoretical
datavectorsischallengingforachievingthetheoreticalerrorbound
errorboundontheerrorsoftheestimateddistances[8,34,36,45,66– becausetheEuclideanspaceisunboundedandtherawdatavectors
68,83,85,95],asexplainedinSection1.Indeed,wefindthatthe
mayappearanywhereintheinfinitelylargespace.Todealwith
accuracyofPQcanbedisastrous(seeSection5.2.3),e.g.,onthe
thisissue,anaturalideaistonormalizetherawvectorsintounit
| dataset MSong, | PQ cannot achieve | 60% recall even | with re- |                                                            |     |     |     |
| -------------- | ----------------- | --------------- | -------- | ---------------------------------------------------------- | --- | --- | --- |
|                |                   | ≥               |          | vectors.Specifically,letcbethecentroidoftherawdatavectors. |     |     |     |
rankingapplied.WenotethatLocalitySensitiveHashing(LSH)is
|     |     |     |     | Wenormalizetherawdatavectorso𝑟 |     | tobeo:= o𝑟−c | .Similarly, |
| --- | --- | --- | --- | ------------------------------ | --- | ------------ | ----------- |
∥o𝑟−c∥
afamilyofmethodswhichpromiserigoroustheoreticalguaran-
|     |     |     |     | wenormalizetherawqueryvectorq𝑟 |     | (whenitcomesinthequery |     |
| --- | --- | --- | --- | ------------------------------ | --- | ---------------------- | --- |
tee[18,38,39,78–80].However,asiswidelyreported[6,58,85], q𝑟−c
|     |     |     |     | phase)tobeq := | .Thefollowingexpressionsbridgethe |     |     |
| --- | --- | --- | --- | -------------- | --------------------------------- | --- | --- |
thesemethodscanhardlyproducecompetitiveempiricalperfor- ∥q𝑟−c∥
distancebetweentherawvectors(i.e.,ourtarget)andtheinner
| mance. Furthermore, | their guarantees | are on the accuracy | of𝑐- |     |     |     |     |
| ------------------- | ---------------- | ------------------- | ---- | --- | --- | --- | --- |
approximateNNquery.Inparticular,LSHguaranteestoreturna productofthenormalizedvectors.
|     |     |     |     | 2   |     | 2   |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
datavectorwhosedistancefromthequeryisatmost(1+𝑐)times ∥o𝑟 −q𝑟∥ =∥(o𝑟 −c)−(q𝑟 −c)∥ (1)
ofafixedradius𝑟withhighprobability(ifthereexistsadatavector
|     |     |     |     | =∥o𝑟 −c∥ 2 +∥q𝑟 | −c∥ 2 −2·∥o𝑟 | −c∥·∥q𝑟 −c∥·⟨q,o⟩ | (2) |
| --- | --- | --- | --- | --------------- | ------------ | ----------------- | --- |

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
Wenotethat∥o𝑟−c∥isthedistancefromthedatavectortothecen- 3.1.3 ComputingtheQuantizedCodesofDataVectors. Withthe
troid,whichcanbepre-computedduringtheindexphase.∥q𝑟 −c∥ constructedcodebook,thenextstepistofindthenearestvector
isthedistancefromthequeryvectortothecentroid.Itcanbecom- fromC𝑟𝑎𝑛𝑑 foreachdatavectorasitsquantizedvector.Foraunit
putedduringthequeryphaseanditscostcanbesharedbyallthe vectoro,tofinditsnearestvector,itisequivalenttofindtheone
datavectors.Thus,basedonEquation(2),thequestionofcomputing whichhasthelargestinnerproductwithit.Let𝑃x¯ ∈ C𝑟𝑎𝑛𝑑 be
∥o𝑟−q𝑟∥2isreducedtothatofcomputingtheinnerproductoftwo thequantizeddatavector(wherex¯ ∈C).Thefollowingequations
unitvectors⟨q,o⟩.Wenotethatinpracticewecanclusterthedata illustratetheidearigorously.
vectorsfirst(e.g.,viaKMeansclustering)andperformthenormal-
|                                                           |     |     |     |     |     | =argmin∥o−𝑃x∥ | 2   |     | (5) |
| --------------------------------------------------------- | --- | --- | --- | --- | --- | ------------- | --- | --- | --- |
| izationfordatavectorswithinaclusterindividuallybasedonthe |     |     |     |     |     | x¯            |     |     |     |
x∈C
centroidofthecluster.Whenconsideringthedatavectorswithina 2 2
|     |     |     |     |     |     | =argmin(∥o∥ | +∥𝑃x∥ | −2⟨o,𝑃x⟩) | (6) |
| --- | --- | --- | --- | --- | --- | ----------- | ----- | --------- | --- |
cluster,wenormalizethequeryvectorbasedonthecorresponding
x∈C
centroid.Inthisway,thenormalizeddatavectorsareexpectedto
|     |     |     |     |     |     | =argmin(2−2⟨o,𝑃x⟩)=argmax⟨o,𝑃x⟩ |     |     | (7) |
| --- | --- | --- | --- | --- | --- | ------------------------------- | --- | --- | --- |
spreadevenlyontheunithypersphere,removingtheskewnessof
|     |     |     |     |     |     | x∈C |     | x∈C |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
thedata(ifany)tosomeextent.Forthesakeofconvenience,in
Equation(5)isbasedonthedefinitionofthequantizeddatavec-
thefollowingpartswithoutfurtherclarification,bythedataand tor.Equation(6)isduetoelementarylinearalgebraoperations.
queryvector,werefertotheircorrespondingunitvectors.With
Equation(7)isbecause𝑃xandoareunitvectors.However,by
thisconversion,wenextfocusonestimatingtheinnerproductof
Equation(7),itiscostlytofindthequantizeddatavectorbyphys-
theunitvectors,i.e.,⟨q,o⟩.
|     |     |     |     |     | ically transforming | the | huge codebook | and finding | the nearest |
| --- | --- | --- | --- | --- | ------------------- | --- | ------------- | ----------- | ----------- |
vectorviaenumeration.Wenotethattheinnerproductisinvari-
| 3.1.2 ConstructingtheCodebook. |     | AsmentionedinSection3.1.1, |     |     |     |     |     |     |     |
| ------------------------------ | --- | -------------------------- | --- | --- | --- | --- | --- | --- | --- |
anttoorthogonaltransformation(i.e.,rotation).Thus,insteadof
thedatavectorsaresupposed,tosomeextent,tobeevenlyspread-
ingontheunithypersphereduetothenormalization.Byintuition, transformingthehugecodebook,weinverselytransformthedata
vectoro.Thefollowingexpressionsformallypresenttheidea.
ourcodebookshouldalsospreadevenlyontheunithypersphere.To
thisend,anaturalconstructionofthecodebookisgivenasfollows. ⟨o,𝑃x⟩= (cid:10)𝑃−1 o,𝑃−1𝑃x (cid:11) = (cid:10)𝑃−1 o,x (cid:11) (8)
|     |     |     | (cid:27)𝐷 |     |     |     |     | √   |     |
| --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- |
(cid:26) 1 1 Recallthattheentriesofx∈Care±1/ 𝐷.Tomaximizetheinner
|     |     | C:= +√ ,−√ |     | (3) |                               |                                    |                          |     |     |
| --- | --- | ---------- | --- | --- | ----------------------------- | ---------------------------------- | ------------------------ | --- | --- |
|     |     |            |     |     | product,weonlyneedtopickthex¯ |                                    | ∈Cwhosesignsoftheentries |     |     |
|     |     | 𝐷          | 𝐷   |     |                               |                                    |                          |     |     |
|     |     |            |     |     | matchthoseof𝑃−1               | o.Then𝑃x¯isthequantizeddatavector. |                          |     |     |
ItiseasytoverifythatthevectorsinCareunitvectorsandthe Insummary,tofindthenearestvectorofadatavectorofrom
codebookhasthesizeof|C|=2𝐷. ,wecaninverselytransformowith𝑃−1andstorethesignsof
C𝑟𝑎𝑛𝑑
However, such construction may favor some certain vectors 𝐷.Wecallthestoredbinary
|     |     |     |     |     | itsentriesasa𝐷-bitstringx¯𝑏 |     | ∈{0,1} |     |     |
| --- | --- | --- | --- | --- | --------------------------- | --- | ------ | --- | --- |
andperformpoorlyforothers.Forexample,forthedatavector
√ √ stringx¯𝑏 asthequantizationcode,whichcanbeusedtore-construct
(1/ 𝐷,...,1/ 𝐷),itsquantizeddatavector(whichc orrespond sto thequantizedvectorx¯.Let1𝐷 bethe𝐷-dimensionalvectorwhich
|     |     |     |     | √ √ |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
thevectorinCclosestfromthedatavector)is(1/ 𝐷,...,1/ 𝐷), hasallitsentriesbeingo nes.Therelationshipbetweenx¯𝑏 andx¯is
√
| a n d i ts s qu | a r e d d i s t | an c e t o t h e q u an t | iz e d d a ta v e c to | r i s 0 .I n c o n - |               |                    |                   |                          |                     |
| --------------- | --------------- | ------------------------- | ---------------------- | -------------------- | ------------- | ------------------ | ----------------- | ------------------------ | ------------------- |
|                 |                 |                           |                        |                      | gi ve n a sx¯ | = ( 2x¯ 𝑏 − 1 𝐷 )/ | 𝐷 , i .e ., w h e | n th e 𝑖 th c o o r di n | a t e x¯𝑏 [𝑖 ] = 1, |
tr a s t , fo r th e v e c t o r (1 , 0 , ... , 0 ), i ts q u a n ti ze d d a t a v e c to r i s a ls o √ √
√ √ w e h av e x¯[ 𝑖] = 1 / 𝐷 a nd w h e n x¯ [ 𝑖] = 0 , w e h a v e x¯ [ 𝑖 ] = − 1 / 𝐷 .
𝑏
(1/ 𝐷,...,1/ 𝐷),andi tssquareddistancetothequantizeddata Forthesakeofconvenience,wedenotethequantizeddatavector
√
| vectorequalsto2−2/ |                  | 𝐷.Todealwiththisissue,weinjectthe |         |              | aso¯ :=𝑃x¯. |     |     |     |     |
| ------------------ | ---------------- | --------------------------------- | ------- | ------------ | ----------- | --- | --- | --- | --- |
| codebook           | some randomness. | Specifically,                     | let𝑃 be | a random or- |             |     |     |     |     |
Tillnow,wehavefinishedthepre-processingintheindexphase.
| thogonalmatrix.Weproposetoapplythetransformation𝑃 |     |     |     | tothe |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
Wenotethatthetimecostintheindexphaseisnotabottleneck
codebook(whichisonetypeoftheJohnson-LindenstraussTrans- forourmethod,whichisthesameasinthecasesofPQandOPQ
formation[49]).Ourfinalcodebookisgivenasfollows. (apopularvariantofPQ)[34].Forexample,onthedatasetGIST
withonemillion960-dimensionalvectors,with32threadsonCPU,
|     |     | C𝑟𝑎𝑛𝑑 :={𝑃x|x∈C} |     | (4) |     |     |     |     |     |
| --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
ourmethod,PQandOPQtake117s,105sand291srespectively.
Geometrically, the transformation simply rotates the codebook Thespacecomplexityofthemethodsisnotabottleneckforthein-
memoryANNeither,becausethespaceconsumptionislargelydue
| becausethematrix𝑃 |     | isorthogonal,andthus,thevectorsinC𝑟𝑎𝑛𝑑 |     |     |     |     |     |     |     |
| ----------------- | --- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
tothespaceforstoringtherawvectors.Asacomparison,eachraw
arestillunitvectors.Moreover,therotationisuniformlysampled
vectortakes32𝐷bits(i.e.,𝐷floating-pointnumbers).Ourmethod
from“allthepossiblerotations”ofthespace.Thus,foraunitvector
inthecodebookC,ithasequalprobabilitytoberotatedtoanywhere bydefaulthas𝐷bitsforaquantizationcode.PQandOPQbydefault
ontheunithypersphere.Thisstepthusremovesthepreferenceof have2𝐷 bitsforaquantizationcode(i.e.,𝑀 =𝐷/2)accordingto
[25,37],whichissignificantlysmallerthanthespaceforstoring
thedeterministiccodebookConspecificvectors.
therawvectors.
| WenotethattoconstructthecodebookC𝑟𝑎𝑛𝑑 |     |     | ,weonlyneedto |     |     |     |     |     |     |
| ------------------------------------- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- |
samplearandomtransformationmatrix𝑃.Tostorethecodebook
C𝑟𝑎𝑛𝑑 ,weonlyneedtophysicallystorethesampled𝑃butnotallthe 3.2 ConstructinganUnbiasedEstimator
transformedvectors.Thecodebookconstructedbythisoperation Recallthattheproblemofcomputing∥o𝑟 −q𝑟∥2canbereducedto
ismuchsimplerthanitscounterpartinPQanditsvariantswhich thatofcomputingtheinnerproductoftwounitvectors⟨o,q⟩.In
relyonapproximatelysolvinganoptimizationproblem. thissection,weintroduceanunbiasedestimatorfor⟨o,q⟩.Unlike

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
PQanditsvariantswhichsimplytreatthequantizeddatavector orthogonalmatrix𝑃,appliedittothecodebookCandgenerated
asthedatavectorforestimatingthedistanceswithouttheoretical arandomizedcodebookC𝑟𝑎𝑛𝑑 .o¯isavectorpickedfromtheran-
errorbounds,wefirstexplicitlyderivetherelationshipbetween domizedcodebookC𝑟𝑎𝑛𝑑 andthus,itisarandomvector.⟨o¯,o⟩and
⟨o,q⟩ and ⟨o¯,q⟩ inSection3.2.1.Wethenconstructanunbiased ⟨o¯,e1⟩correspondtotheprojectionoftherandomvectoro¯onto
estimatorfor⟨o,q⟩basedonthederivedrelationshipsandpresent twofixeddirections(i.e.,thedirectionsareoande1 ,whereo⊥e1 ).
itsrigorouserrorboundinSection3.2.2. Thus,theyaremutuallycorrelatedrandomvariables.
Werigorouslyanalyzethedistributionsoftherandomvariables.
|     |     |     |     |     | The core conclusions | of the | analysis are | briefly summarized | as  |
| --- | --- | --- | --- | --- | -------------------- | ------ | ------------ | ------------------ | --- |
followswhilethedetailedpresentationandproofareleftinthe
technicalreport[33]duetothepagelimit.Specifically,ouranalysis
indicatesthatwhen𝐷rangesfrom102to106,itisalwaystruethat
⟨o¯,o⟩hastheexpectation5ofaround0.8and⟨o¯,e1⟩hastheexpec-
tationofexactly0.Itfurtherindicatesthat,withhighprobability,
theserandomvariableswouldnotdeviatefromtheirexpectation
√
byΩ(1/ 𝐷).Thisconclusionquantitativelypresentstheextent
Figure1:GeometricRelationshipamongtheVectors. thattherandomvariablesconcentratearoundtheirexpectedval-
ues,whichwillbeusedlaterforanalyzingtheerrorboundofour
3.2.1 AnalyzingtheExplicitRelationshipbetween⟨o,q⟩and⟨o¯,q⟩.
estimator.Toempiricallyverifyouranalysis,werepeatedlyand
Wenotethattherelationshipbetween⟨o,q⟩and⟨o¯,q⟩dependsonly
105times
ontheprojectionofo¯onthetwo-dimensionalsubspacespanned independentlysampletherandomorthogonalmatrices𝑃
byoandq,whichisillustratedontheleftpanelofFigure1.Forthe forapairoffixedo,qinthe128-dimensionalspace.Therightpanel
ofFigure1visualizestheprojectionofo¯onthe2-dimensionalspace
componentofo¯whichisperpendiculartothesubspace,ithasno
spannedbyo,qwiththeredpointcloud(eachpointrepresents
effectontheinnerproduct⟨o¯,q⟩.Thefollowinglemmapresentsthe
|     |     |     |     |     | theprojectionofano¯ | basedonasampledrandommatrix𝑃).In |     |     |     |
| --- | --- | --- | --- | --- | ------------------- | -------------------------------- | --- | --- | --- |
specificresult.Theproofcanbefoundinthetechnicalreport[33].
particular,⟨o¯,o⟩(thex-axis)isshowntobeconcentratedaround0.8.
| Lemma3.1(GeometricRelationship). |     |     | Leto,qando¯ |       |                                                             |     |     |     |     |
| -------------------------------- | --- | --- | ----------- | ----- | ----------------------------------------------------------- | --- | --- | --- | --- |
|                                  |     |     |             | beany | ⟨o¯,e1⟩(they-axis)isconcentratedandsymmetricallydistributed |     |     |     |     |
threeunitvectors.Whenoandqarecollinear(i.e.,o=qoro=−q), around0,whichverifiesourtheoreticalanalysisperfectly.
wehave
|     |     |                     |     |     | 3.2.2 ConstructinganUnbiasedEstimatorfor⟨o,q⟩. |     |     | Basedonour |     |
| --- | --- | ------------------- | --- | --- | ---------------------------------------------- | --- | --- | ---------- | --- |
|     |     | ⟨o¯,q⟩=⟨o¯,o⟩·⟨o,q⟩ |     | (9) |                                                |     |     |            |     |
analysisonEquation(9),forthecasethato,qarecollinear,⟨o,q⟩can
Whenoandqarenon-collinear,wehave ⟨o¯,q⟩.Thus,itisnaturaltoconjecture
beexplicitlysolvedby⟨o,q⟩=
|     |                              |     | √︃      |        |                                        |     | ⟨o¯,o⟩ |               |     |
| --- | ---------------------------- | --- | ------- | ------ | -------------------------------------- | --- | ------ | ------------- | --- |
|     | ⟨o¯,q⟩=⟨o¯,o⟩·⟨o,q⟩+⟨o¯,e1⟩· |     | 1−⟨o,q⟩ | 2 (10) |                                        |     |        | ⟨o¯,q⟩        |     |
|     |                              |     |         |        | thatforthecasethato,qarenon-collinear, |     |        | shouldalsobea |     |
⟨o¯,o⟩
|     |     |     |     | :=  | goodestimatorfor⟨o,q⟩.Wethusdeducefromitasfollows. |     |     |     |     |
| --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- |
wheree1isq−⟨q,o⟩owithitsnormnormalizedtobe1,i.e.,e1
,
| q − ⟨ q | o ⟩ o | ⊥   | ⟨ , ⟩ = 0 | ∥ ∥ = 1 |     |     |     |     |     |
| ------- | ----- | --- | --------- | ------- | --- | --- | --- | --- | --- |
∥q − ⟨ q , o ⟩ o ∥ . W e n o t e t h a t o e 1 ( s in c e o e 1 ) a n d e 1 . √︃
|     |     |     |     |     |     | ⟨o¯,o⟩·⟨o,q⟩+⟨o¯,e1⟩· |     | 1−⟨o,q⟩ 2 |     |
| --- | --- | --- | --- | --- | --- | --------------------- | --- | --------- | --- |
⟨o¯,q⟩
R e c a ll th a t w e t a r g e t t o est i m a t e ⟨ o , q ⟩ . If w e e x a c tl y k n o w t he = (11)
|     |     |     |     |     | ⟨o¯,o⟩ |     | ⟨o¯,o⟩ |     |     |
| --- | --- | --- | --- | --- | ------ | --- | ------ | --- | --- |
valuesofallthevariablesotherthan⟨o,q⟩,wecancomputethe
exactvalueof⟨o,q⟩bysolvingEquations(9)and(10).Inparticular, √︃ ⟨o¯,e1⟩
|     |     |     |     |     |     | =⟨o,q⟩+ | 1−⟨o,q⟩ 2 | ·   | (12) |
| --- | --- | --- | --- | --- | --- | ------- | --------- | --- | ---- |
inEquations(9)and(10),⟨o¯,o⟩istheinnerproductbetweenthe ⟨o¯,o⟩
| quantized | data vector | and the data vector. | Its value | can be pre- |     |     |     |     |     |
| --------- | ----------- | -------------------- | --------- | ----------- | --- | --- | --- | --- | --- |
whereEquation(11)isbyEquation(10)andEquation(12)simplifies
computedintheindexphase.⟨o¯,q⟩istheinnerproductbetween
Equation(11).WenotethatthelastterminEquation(12)canbe
thequantizeddatavectorandthequeryvector.Itsvaluecanbe
efficientlycomputedinthequeryphase(wewillspecifyinSec- viewedastheerrortermoftheestimator.Recallthatbasedonour
tion3.3howitcanbeefficientlycomputed).Thus,whenoandq analysisinSection3.2.1,⟨o¯,o⟩isconcentratedaround0.8.⟨o¯,e1⟩
arecollinear,wecancomputethevalueof⟨o,q⟩exactlybysolving hastheexpectationof0andisconcentrated.Itimpliesthatthe
⟨o¯,q⟩. errortermhas0expectationandwillnotdeviatelargelyfrom0due
Equation(9),i.e.,⟨o,q⟩=
⟨o¯,o⟩ totheconcentration.Thefollowingtheorempresentsthespecific
Whenoandqarenon-collinear(whichisamorecommoncase),
results.Therigorousproofcanbefoundinthetechnicalreport[33].
inordertoexactlysolvetheEquation(10),weneedtoknowthe
| valueof⟨o¯,e1⟩.However,ase1 |     | dependsonbothoandq(whichcan |     |     |                        |     |                          |     |     |
| --------------------------- | --- | --------------------------- | --- | --- | ---------------------- | --- | ------------------------ | --- | --- |
|                             |     |                             |     |     | Theorem3.2(Estimator). |     | Theunbiasednessisgivenas |     |     |
beseenbyitsdefinition),⟨o¯,e1⟩canbeneitherpre-computedin
theindexphase(becauseitdependsonq)norcomputedefficiently (cid:20)⟨o¯,q⟩(cid:21)
| inthequeryphasewithoutaccessingo. |     |     |     |     |     | E   | =⟨o,q⟩ |     | (13) |
| --------------------------------- | --- | --- | --- | --- | --- | --- | ------ | --- | ---- |
⟨o¯,o⟩
Wenoticethatalthoughwecannotefficientlycomputetheexact
valueof⟨o¯,e1⟩4,giventherandomnatureofo¯,weexplicitlyknow
itsdistribution.Specifically,recallthatwehavesampledarandom
|     |     |     |     |     |                                   |     | √︃  | 𝐷                    |       |
| --- | --- | --- | --- | --- | --------------------------------- | --- | --- | -------------------- | ----- |
|     |     |     |     |     | 5TheexactexpectedvalueisE[⟨o¯,o⟩] |     | = 𝐷 | 2 Γ ( 2 ) ,whereΓ(·) | isthe |
4Inparticular,whenwesay“computingthevalue”ofarandomvariable,itrefersto 𝜋 (𝐷− 1 Γ 𝐷 −1)
|     |     |     |     |     |     |     |     | ) ( 2 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- |
computingitsobservedvaluebasedonacertainsampled𝑃. Gammafunction.Theexpectedvaluerangesfrom0.798to0.800for𝐷 ∈[102,106].

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
Theerrorboundoftheestimatorisgivenas 3.3 ComputingtheEstimatorEfficiently
√︄ R e c a ll th a t ⟨ o ¯ , q ⟩ is t h e e s t i m a t o r .S i n c e ⟨o¯ , ⟩ h a s b e e n p re - co m p u t e d
|     |  (cid:12) ,     | (cid:12)   | 1−  | , 2 𝜖0   |     |        |     | ⟨ , ⟩ |     |     |     | o   |     |     |
| --- | ------------------- | ---------- | --- | -------- | ------- | ------ | --- | ----- | --- | --- | --- | --- | --- | --- |
|     | P (cid:12) ⟨ o ¯ q⟩ | (cid:12) > |     | ⟨ o¯ o ⟩ | ≤2𝑒−𝑐0𝜖 | 2 (14) |     | o ¯ o |     |     |     |     |     |     |
(cid:12) −⟨o,q⟩ (cid:12) · √ 0 d u r i n g th e in d e x p h a s e , t h e r e m a i n i n g q u e s t i o n i s t o c o m p u t e t h e
|     | (cid:12)⟨ o ¯ , o ⟩ | (cid:12) | ⟨o¯ | , o ⟩ 2 𝐷 −1 |     |     |     |     |     |     |     |     |     |     |
| --- | ------------------- | -------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  v a l u e o f ⟨ o¯, q ⟩ e ffi c ie n t l y . F o r t h e s a k e o f c o n v e n i e n c e , w e d e n o t e
|       |                                      |     |     |     |                  |     |          |               |            |             |             |                |              |              |
| ----- | ------------------------------------- | --- | --- | --- | ----------------- | --- | -------- | ------------- | ---------- | ----------- | ----------- | -------------- | ------------ | ------------ |
|       |                                       |     |     |     |                   |     | 𝑃 − 1 q  | a s q′ . L ik | e w h a t  | w e d o i n | S e c t io  | n 3.1 . 3, i n | o r d er to  | c o m p u te |
| where | 𝜖0isaparameterwhichcontrolsthefailure |     |     |     | probability.𝑐0isa |     |          |               |            |             |             |                |              |              |
|       |                                       |     |     |     |                   |     | ⟨o¯ , ⟩, | w e c a n c   | om p u t e | ⟨ x¯, ′⟩ ,  | w h i c h c | an b e v e ri  | fi e d as fo | l lo w s .   |
|       |                                       |     |     |     |                   |     | q        |               |            | q           |             |                |              |              |
constantfactor.Theerrorboundcanbeconciselypresentedas
|     |     |     |     |     |     |     |     |     |     | (cid:10)𝑃−1𝑃x¯,𝑃−1 |     | (cid:11) (cid:10) | x¯,q′(cid:11) |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | ----------------- | ------------- | --- |
(cid:12) ⟨o¯,q⟩ (cid:12) (cid:18) 1 (cid:19) ⟨o¯,q⟩=⟨𝑃x¯,q⟩= q = (17)
|     | (cid:12)       |        | (cid:12)     |                     |     |      |                                |                                      |     |     |                            |                    |     |     |
| --- | -------------- | ------ | ------------ | ------------------- | --- | ---- | ------------------------------ | ------------------------------------ | --- | --- | -------------------------- | ------------------ | --- | --- |
|     | (cid:12)       | −⟨o,q⟩ | (cid:12)=𝑂 √ | 𝑤𝑖𝑡ℎℎ𝑖𝑔ℎ𝑝𝑟𝑜𝑏𝑎𝑏𝑖𝑙𝑖𝑡𝑦 |     | (15) |                                |                                      |     |     |                            |                    |     |     |
|     | (cid:12)⟨o¯,o⟩ |        | (cid:12)     | 𝐷                   |     |      |                                |                                      |     |     |                            | Recallthatx¯isabi- |     |     |
|     |                |        |              |                     |     |      | 3.3.1                          | QuantizingtheTransformedQueryVector. |     |     | √                          |                    |     |     |
|     |                |        |              |                     |     |      | valuedvectorwhoseentriesare±1/ |                                      |     |     | 𝐷.Itisrepresentedandstored |                    |     |     |
DuetoEquations(2)and(13),theunbiasedestimatorof⟨o,q⟩
canfurtherinduceanunbiasedestimatorofthesquareddistance asabinaryquantizationcodex¯𝑏 asisdiscussedinSection3.1.3.
q′isareal-valuedvector,whoseentriesareconventionallyrepre-
betweentherawdataandqueryvectors.Weprovideempiricalveri-
sentedbyfloating-pointnumbers(floatsinshort).Wenotethatin
ficationontheunbiasednessinSection5.2.6.Besides,wewouldlike
ourmethod,representingtheentriesofq′withfloatsisanoverkill.
tohighlightthatbasedonsimilaranalysis,analternativeestimator
⟨ , q⟩
⟨o,q⟩≈⟨o¯,q⟩,i.e.,bysimplytreatingthequantizeddatavectoras Specifically,recallthatourmethodadopts o ¯ asanestimatorof
⟨ o ¯ , o ⟩
thedatavectorasPQdoes,canbeeasilyprovedtobebiased. ⟨o,q⟩.Evenifweobtainaperfectlyaccurateresultinthecompu-
Equation(14)presentstheerrorboundofourestimator.Inpar- tationof⟨o¯,q⟩,ourestimationof⟨o,q⟩isstillapproximate.Thus,
2)confidenceinterval
ticular,itpresentsa1−2exp(−𝑐0𝜖 insteadofexactlycomputing⟨o¯,q⟩,weaimtoguaranteethatthe
0
errorproducedinthecomputationof⟨o¯,q⟩ismuchsmallerthan
√︄
|     |     | ⟨o¯,q⟩ | 1−⟨o¯,o⟩ | 2 𝜖0 |     |     | theerroroftheestimatoritself. |     |     |     |     |     |     |     |
| --- | --- | ------ | -------- | ---- | --- | --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- |
(16)
± 2 · √ Specifically,weapplyuniformscalarquantizationontheentries
|     |     | ⟨o¯,o⟩ |     | ⟨o¯,o⟩ 𝐷−1 |     |     |                         |     |     |                                  |     |     |     |     |
| --- | --- | ------ | --- | ---------- | --- | --- | ----------------------- | --- | --- | -------------------------------- | --- | --- | --- | --- |
|     |     |        |     |            |     |     | ofq′andrepresentthemas𝐵 |     |     | -bitunsignedintegers.Wedenotethe |     |     |     |     |
𝑞
Wenotethatthefailureprobability(i.e.,theprobabilitythatthe
|       |             |                    |           |                       |           |                     | 𝑖thentryofthevectorq′asq′[𝑖].Let𝑣 |        |           |          |            | 𝑙 :=min      | 1≤𝑖≤𝐷q′[𝑖],𝑣 | 𝑟 :=            |
| ----- | ----------- | ------------------ | --------- | --------------------- | --------- | ------------------- | --------------------------------- | ------ | --------- | -------- | ---------- | ------------ | ------------ | --------------- |
| c o n | fi d en c e | in t e r v a l d o | e s n o t | c o v e r t h e t r u | e v a l u | e o f ⟨o ,q ⟩ ) i s |                                   |        |           |          |            |              |              |                 |
|       |             |                    |           |                       |           |                     | m a x                             | q ′[ 𝑖 | ] a n d Δ | := ( 𝑣 − | 𝑣 𝑙) / ( 2 | 𝐵 𝑞 − 1 ). T | h e u n if o | r m s c a l a r |
2 e x p 𝑐0 𝜖 2) . I t d e c a y s i n a q u a d r a ti c -e x p o n en t i a l tr e nd w r t 𝜖 , 1 ≤ 𝑖≤ 𝐷 𝑟
(− 0 0 q u a n t iz at io n u n i fo r m ly sp l it s th e r a n g e o f th e v a lu e s [ 𝑣 , 𝑣 ] i n t o
𝑙 𝑟
whichisextremelyfast.Thelengthoftheconfidenceintervalgrows 2𝐵𝑞 −1segments,whereeachsegmenthasthelengthofΔ.Then
√︁log(1/𝛿))correspondstoafailure
| linearlywrt𝜖0 |     | .Thus,𝜖0=Θ( |     |     |     |     |            |     |              |     | 0,1,...,2𝐵𝑞 |      |             |     |
| ------------- | --- | ----------- | --- | --- | --- | --- | ---------- | --- | ------------ | --- | ----------- | ---- | ----------- | --- |
|               |     |             |     |     |     |     | foravalue𝑣 | =   | 𝑣 𝑙 +𝑚·Δ+𝑡,𝑚 |     | =           | −1,𝑡 | ∈ [0,Δ),the |     |
probabilityofatmost𝛿,whichindicatesthatashortconfidence
methodquantizesitbyroundingituptoitsnearestboundaryofthe
intervalcancorrespondtoahighconfidencelevel.Inpractice,𝜖0
|     |     |     |     |     |     |     | segments(i.e.,𝑣 |     | 𝑙+𝑚·Δor𝑣 | 𝑙+(𝑚+1)·Δ)andrepresentingitwith |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------- | --- | -------- | ------------------------------- | --- | --- | --- | --- |
isfixedtobe1.9inpursuitofnearlyperfectconfidence(seeSec-
|     |     |     |     |     |     |     | thecorresponding𝐵 |     | -bitunsignedinteger(i.e.,𝑚or𝑚+1).Letq¯ |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | -------------------------------------- | --- | --- | --- | --- | --- |
𝑞
tion5.2.4fortheempiricalverificationstudy).Recallthat⟨o¯,o⟩is bethevectorwhoseentriesareequaltothequantizedvaluesofthe
concentratedaround0.8.Basedonthevaluesof𝜖0 and⟨o¯,o⟩,the entriesofq′(wetermitasthequantizedqueryvector)andq¯𝑢
beits
errorboundcanbefurtherconciselypresentedasEquation(15),i.e.,
√ 𝐵 𝑞 -bitunsignedintegerrepresentation,whereq¯ =Δ·q¯𝑢+𝑣 𝑙 ·1𝐷
| itguaranteesanerrorboundof𝑂(1/ |     |     |     | 𝐷).Accordingtoarecent |     |     |               |     |                                             |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | --------------------- | --- | --- | ------------- | --- | ------------------------------------------- | --- | --- | --- | --- | --- |
|                                |     |     |     |                       |     |     | (recallthat1𝐷 |     | isthe𝐷-dimensionalvectorwithallitsentriesas |     |     |     |     |     |
theoreticalstudy[3],for𝐷-dimensionalvectors,withashortcode ones).Then,wecancompute⟨x¯,q¯⟩asanapproximationof⟨x¯,q′⟩.
of𝐷bits,itisimpossibleint heoryforamethodtoprovideabound Furthermore,toretainthetheoreticalguarantee,weadoptthe
√
| whichistighterthan𝑂(1/ |     |     | 𝐷)(thefailureprobabilityisviewed |     |     |     |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
trickofrandomizingtheuniformscalarquantization[3,93].Specif-
asaconstant).Thus,Equation(15)indicatesthatRaBitQ’serror
ically,unliketheconventionalmethodwhichroundsupavalue
boundissharp,i.e.,itachievestheasymptoticoptimality.Theerror
toitsnearestboundaryofthesegments,therandomizedmethod
boundwillbelaterusedinANNsearchtodeterminewhethera roundsittoitsleftorrightboundaryrandomly.Therationaleis
datavectorshouldbere-ranked(seeSection4). thatforavalue𝑣 =𝑣 𝑙+𝑚·Δ+𝑡,𝑚=0,1,...,2𝐵𝑞−1,𝑡 [0,Δ),when
∈
Furthermore,wenotethatRaBitQprovidesanerrorboundin
|     |     |     |     |     |     |     | itisroundedto𝑣 |     | 𝑙+𝑚·Δ,itwillcauseanerrorofunder-estimation |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------------------------------------------ | --- | --- | --- | --- | --- |
anadditiveform[3](i.e.,absoluteerror).Whenthedatavectors
|     |     |     |     |     |     |     | −𝑡 <0.Whenitisroundedto𝑣 |     |     |     | 𝑙+(𝑚+1)·Δ,itwillcauseanerror |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | --- | --- | ---------------------------- | --- | --- | --- |
arewellnormalized(recallthatinSection3.1.1wenormalizethe
|     |     |     |     |     |     |     | ofover-estimationΔ−𝑡 |     |     | >0.Ifweassign1−𝑡/Δprobabilitytothe |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | ---------------------------------- | --- | --- | --- | --- |
datavectors),theboundcanbepushedforwardtoamultiplicative formereventand𝑡/Δprobabilitytothelatterevent,theexpected
form[41](i.e.,relativeerror).Weleavethedetaileddiscussionin errorwouldbe0,whichmakesthecomputationunbiased.Wenote
thetechnicalreport[33]becauseitisbasedonanassumptionthat thatthisoperationcanbeeasilyachievedbyletting
thedatavectorsarewellnormalized.Notethatallothertheoretical
resultsintroducedinthispaperdonotrelyonanyassumptionson (cid:106)q′[𝑖]−𝑣 𝑙 (cid:107)
|     |     |     |     |     |     |     |     |     | q¯𝑢[𝑖] | :=  |     | +𝑢 𝑖 |     | (18) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | ---- | --- | ---- |
Δ
thedata,i.e.,theadditiveboundholdsregardlessofthedatadistri-
bution.Inthepresentwork,weadoptasimpleandnaturalmethod where𝑢 𝑖 issampledfromtheuniformdistributionon[0,1].More-
ofnormalization(i.e.,withthecentroidsofIVFaswillbeintroduced over,basedontherandomizedmethod,wecananalyzethemini-
inSection4)toinstantiateourschemeofquantization,whilewe mum𝐵 neededformakingtheerrorintroducedbytheuniform
𝑞
haveyettoextensivelyexplorethenormalizationstepitself.We scalarquantizationnegligible.Theresultispresentedwiththefol-
shallleaveitasfutureworktorigorouslystudythenormalization lowingtheorem.Thedetailedproofcanbefoundinthetechnical
| problem. |     |     |     |     |     |     | report[33]. |     |     |     |     |     |     |     |
| -------- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
Theorem 3.3. 𝐵 = Θ(loglog𝐷) suffices to guarantee that 0≤ 𝑗 <𝐵 .Thefollowingexpressionspecifiestheidea.
|                        |     | 𝑞   | √                      |     |     |     |     | 𝑞   |     |     |     |     |     |
| ---------------------- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| |⟨x¯,q′⟩−⟨x¯,q¯⟩|=𝑂(1/ |     |     | 𝐷)withhighprobability. |     |     |     |     |     |     |     |     |     |     |
𝐵𝑞−1
|     |     |     |     |     |     |     |        | 𝐷                |     | 𝐷          |     |            |      |
| --- | --- | --- | --- | --- | --- | --- | ------ | ---------------- | --- | ---------- | --- | ---------- | ---- |
|     |     |     |     |     | √   |     | ,q¯𝑢⟩= | ∑︁ x¯𝑏[𝑖]·q¯𝑢[𝑖] |     | ∑︁ x¯𝑏[𝑖]· | ∑︁  | (𝑗) [𝑖]·2𝑗 | (21) |
Recall that the estimator has the error of𝑂(1/ 𝐷) (see Sec- ⟨x¯𝑏 = q¯𝑢
|                                             |     |     |     |     |               |     |     | 𝑖=1  |     | 𝑖=1 | 𝑗=0  |     |     |
| ------------------------------------------- | --- | --- | --- | --- | ------------- | --- | --- | ---- | --- | --- | ---- | --- | --- |
| tion3.2.2).Theabovetheoremshowsthatsetting𝐵 |     |     |     |     | 𝑞 =Θ(loglog𝐷) |     |     |      |     |     |      |     |     |
|                                             |     |     |     |     |               |     |     | 𝐵𝑞−1 |     |     | 𝐵𝑞−1 |     |     |
sufficestoguaranteethattheerrorintroducedbytheuniformscalar 𝐷
|     |     |     |     |     |     |     |     | ∑︁ 2𝑗 ∑︁ | x¯𝑏[𝑖]·q¯𝑢 | (𝑗) [𝑖] | ∑︁  | 2𝑗 (cid:68) | ,q¯𝑢 (𝑗)(cid:69) (22) |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ------- | --- | ----------- | --------------------- |
quantizationisatthesameorderastheerrorintroducedbyestima- = · = · x¯𝑏
tor.Becausetheerrordecreasesexponentiallywrt𝐵 ,increasing 𝑗=0 𝑖=1 𝑗=0
𝑞
| 𝐵 byasmallconstant(i.e.,𝐵 |     |     | isstillattheorderofΘ(loglog𝐷)) |     |     |     |                           |     |                                |     |     |     |     |
| ------------------------- | --- | --- | ------------------------------ | --- | --- | --- | ------------------------- | --- | ------------------------------ | --- | --- | --- | --- |
| 𝑞                         |     |     | 𝑞                              |     |     |     | Equation(22)showsthat⟨x¯𝑏 |     | ,q¯𝑢⟩canbeexpressedasaweighted |     |     |     |     |
guaranteesthattheerrorismuchsmallerthanthatoftheestimator. (cid:68) (𝑗)(cid:69)
|     |     |     |     |     |     |     | sumoftheinnerproductofthebinaryvectors,i.e., |     |     |     |     |     | ,q¯𝑢 for |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------------------- | --- | --- | --- | --- | --- | -------- |
x¯𝑏
| Weprovidetheempiricalverificationstudyfor𝐵 |     |     |     |                | 𝑞 inSection5.2.5. |     |          |                         |              |              |            |             |                          |
| ------------------------------------------ | --- | --- | --- | -------------- | ----------------- | --- | -------- | ----------------------- | ------------ | ------------ | ---------- | ----------- | ------------------------ |
|                                            |     |     |     |                |                   |     | 0 ≤ 𝑗 <  | 𝐵 𝑞 . I n p a rt i cu   | l a r , w e  | n o t e t    | h a t th e | i n n e r p | r o d u c t o f b i -    |
| Theresultshowsthatwhen𝐵                    |     |     | 𝑞   | = 4,theerrorin | troducedbythe     |     |          |                         |              |              |            |             |                          |
|                                            |     |     |     |                |                   |     | na ry ve | cto r s c a n b e e ffi | c i e n t ly | a c h ie v e | d b y b it | w i s e o p | e r at i o ns , i. e . , |
uniformscalarquantizationwouldbenegligible.
|                                    |     |     |     |                        |     |     | bitwise-and | and popcount               | (a.k.a., | bitcount). |                        | Thus, the | computa- |
| ---------------------------------- | --- | --- | --- | ---------------------- | --- | --- | ----------- | -------------------------- | -------- | ---------- | ---------------------- | --------- | -------- |
|                                    |     |     |     |                        |     |     | tionof      | ⟨o¯,q⟩ isfinallyreducedto𝐵 |          |            | bitwise-andandpopcount |           |          |
| 3.3.2 Computing⟨x¯,q¯⟩Efficiently. |     |     |     | Wenextpresenthowtocom- |     |     |             |                            |          | 𝑞          |                        |           |          |
pute⟨x¯,q¯⟩efficiently.Wefirstexpress⟨x¯,q¯⟩withx¯𝑏 ,q¯𝑢 asfollows. operationson𝐷-bitstrings,whicharewellsupportedbyvirtually
|     |              |     |     |          |     |     | all platforms. | As a comparison, |     | we  | note that, | as is | comprehen- |
| --- | ------------ | --- | --- | -------- | --- | --- | -------------- | ---------------- | --- | --- | ---------- | ----- | ---------- |
|     | (cid:28)2x¯𝑏 |     |     | (cid:29) |     |     |                |                  |     |     |            |       |            |
− 1𝐷,Δ·q¯𝑢+𝑣 s i v e ly s tu d ied i n [ 4 ], P Q re li e s o n l o o k i ng up L U T s in RA M ,w h i c h
| ⟨x¯,q¯⟩= |     | √   |     | ·1𝐷 |     | (19) |     |     |     |     |     |     |     |
| -------- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
𝐷 𝑙 c a n n ot b e im pl e m e n te d effi c i e n tl y. B a s e d on ou r e x pe rim en ts in S e c -
|     |     |      |     |      |     |     | t io n 5 . 2. | 1 , o n a v e r a g e o | ur m e t h | od r un | s 3 x f as te | r th a n | P Q a n d O P Q |
| --- | --- | ---- | --- | ---- | --- | --- | ------------- | ----------------------- | ---------- | ------- | ------------- | -------- | --------------- |
|     |     |      | 𝐷   | 𝐷    | √   |     |               |                         |            |         |               |          |                 |
| 2Δ  |     | 2𝑣 𝑙 | ∑︁  | Δ ∑︁ |     |     |               |                         |            |         |               |          |                 |
=√ ⟨x¯𝑏 ,q¯𝑢⟩+ √ x¯𝑏[𝑖]− √ q¯𝑢[𝑖]− 𝐷·𝑣 𝑙 (20) ( a p o p u l a r v ar i a n t o f P Q [3 4 ] ) w hi le re a c hi n g th e s a m e ac c u ra c y.
| 𝐷   |     | 𝐷   |     | 𝐷   |     |     |                                                      |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|     |     |     | 𝑖=1 | 𝑖=1 |     |     | Forthesecondcasewheretheestimationofthedistanceisfor |     |     |     |     |     |     |
aqueryvectorandapackedbatchofquantizationcodes,wenote
| NotethatthefactorsΔand𝑣 |     |                                          | areknownwhenwequantizethe |     |     |     |                                                           |     |     |     |     |     |     |
| ----------------------- | --- | ---------------------------------------- | ------------------------- | --- | --- | --- | --------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                         |     |                                          | 𝑙                         |     |     |     | thatourmethodcanseamlesslyadoptthesamefastSIMD-based      |     |     |     |     |     |     |
| queryvector.(cid:205)   | 𝐷   | =1x¯𝑏[𝑖]correspondstothenumberof1’sinthe |                           |     |     |     |                                                           |     |     |     |     |     |     |
|                         | 𝑖   |                                          |                           |     |     |     | implementation[4,5]asPQdoes.Inparticular,fora𝐷-bitstring, |     |     |     |     |     |     |
bitstringx¯𝑏 ,whichcanbepre-computedduringtheindexphase. wesplititinto𝐷/4sub-segmentswhereeachsub-segmenthas
𝐷
(cid:205) =1q¯𝑢[𝑖]dependsonlyonthequeryvector.Itscostofcomputa- 24
| 𝑖   |     |     |     |     |     |     | 4 bits. We | then pre-process | 𝐷/4 | LUTs | where | each | LUT has |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ---------------- | --- | ---- | ----- | ---- | ------- |
tioncanbesharedbyallthedatavectors.Theremainingtaskisto
unsignedintegerscorrespondingtotheinnerproductsbetweena
| compute⟨x¯𝑏        | ,q¯𝑢⟩wherethecoordinatesofx¯𝑏 |               |     |     | are0or1andthose |     |                                                        |                                           |     |     |     |     |     |
| ------------------ | ----------------------------- | ------------- | --- | --- | --------------- | --- | ------------------------------------------------------ | ----------------------------------------- | --- | --- | --- | --- | --- |
|                    |                               |               |     |     |                 |     | sub-segmentofq¯𝑢                                       | andthe24possiblebinarystringsofa4-bitsub- |     |     |     |     |     |
| ofq¯𝑢 areunsigned𝐵 |                               | -bitintegers. |     |     |                 |     |                                                        |                                           |     |     |     |     |     |
|                    |                               | 𝑞             |     |     |                 |     | segment.Foraquantizationcodeofadatavector,wecancompute |                                           |     |     |     |     |     |
W e p r o v id e tw o v e r sio n s o f fa s t co m p u t a ti o n f o r ⟨x ¯𝑏 , q¯ 𝑢 ⟩ . T h e ,q¯ b y loo k i n g u p a n d ac c u m u la ti n g th e v a l u e s in th e L U T s f o r
|               |              |          |            |                   |                       |              | ⟨x¯ 𝑏 𝑢 ⟩  |                       |            |            |             |              |                   |
| ------------- | ------------ | -------- | ---------- | ----------------- | --------------------- | ------------ | ---------- | --------------------- | ---------- | ---------- | ----------- | ------------ | ----------------- |
| firs tv e r s | io n t ar ge | ts t h e | ca s e o f | a s in g le q u a | n t iz at i o n c o d | e , a s th e |            |                       |            |            |             |              |                   |
|               |              |          |            |                   |                       |              | 𝐷 / 4 ti m | e s .W e n o t e t ha | t t he c o | m p u ta t | io n is r e | d u c e d to | e xa c tl y t h e |
originalimplementationofPQ[45]does.Thesecondversiontargets
formofPQandthuscanadoptthefastSIMD-basedimplementation
thecaseofapackedbatchofquantizationcodes,asthefastSIMD-
seamlessly.Recallthatourmethodhasthequantizationcodesof
basedimplementationofPQ[4,5]does.Wenotethatingeneral,
|     |     |     |     |     |     |     | 𝐷 bits by | default while | PQ and | OPQ | have the | codes | of 2𝐷 bits |
| --- | --- | --- | --- | --- | --- | --- | --------- | ------------- | ------ | --- | -------- | ----- | ---------- |
bothourmethodandPQhavehigherthroughputinthesecondcase bydefault.Therefore,ourmethodhasbetterefficiencythanPQ
thanthatinthefirstcase,i.e.,theyestimatethedistancesformore
andOPQforcomputingapproximatedistancesbasedonquantized
quantizationcodeswithincertaintime.Wenotethatthesecond
vectors.Furthermore,asisshowninSection5.2.1,inthedefault
caserequiresthequantizationcodestobepackedinabatch,which
setting,ourmethodalsoachievesconsistentlybetteraccuracythan
isfeasibleinsomecertainscenariosonly.
PQandOPQdespitethatourmethodusesashorterquantization
code(i.e.,𝐷v.s.2𝐷).
...
|     |     |     |     |     |     |     | 3.4 SummaryofRaBitQ |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- | --- | --- |
WesummarizetheRaBitQalgorithminAlgorithm1(theindex
...
phase)andAlgorithm2(thequeryphase).Intheindexphase,it
|     |     |     |     |     |     |     | takes a | set of raw data | vectors | as inputs. | It  | normalizes | the set |
| --- | --- | --- | --- | --- | --- | --- | ------- | --------------- | ------- | ---------- | --- | ---------- | ------- |
ofvectorsbasedonSection3.1.1(line1),constructstheRaBitQ
codebookbysamplingarandomorthogonalmatrix𝑃basedonSec-
|     |     |     |     |     |     |     | tion3.1.2(line2)andcomputesthequantizationcodesx¯𝑏 |     |     |     |     |     | basedon |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- | ------- |
Figure2:BitwiseDecompositionofq¯𝑢. Section3.1.3(line3).Inthequeryphase,ittakesarawqueryvector,
asetofIDsofthedatavectorsandthepre-processedvariables
Forthefirstcasewheretheestimationofthedistanceisfora abouttheRaBitQmethodasinputs.Itfirstinverselytransforms,
normalizesandquantizestherawqueryvector(line1-2).Wenote
queryvectorandasinglequantizationcode,wenotethatanun-
thatthetimecostofthesestepscanbesharedbyallthedatavectors.
| signed𝐵 | 𝑞 -bitintegercanbedecomposedinto𝐵 |     |     |     | 𝑞 binaryvaluesas |     |     |     |     |     |     |     |     |
| ------- | --------------------------------- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- |
showninFigure2.Theleftpanelrepresentsthenaivecomputation ThenforeachinputIDofthedatavectors,itefficientlycomputes
o f ⟨ , ⟩ . T h e r i g h t p a n e l r ep re s e n t s th e p ro p os e d b i tw is e c om p u - t h e va l u e of ⟨ o ¯ , q ⟩ b a s e d on Se c t io n 3. 3 . 2, a d op ts i t a s a n u n b i a s e d
| x¯ 𝑏 q¯ 𝑢 |     |     |     |     |     |     |     | ⟨ , ⟩ |     |     |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- |
|           |     | (   | 𝑗 ) |     |     |     |     | o ¯ o |     |     |     |     |     |
ta t io n o f ⟨ x¯ 𝑏 , q¯ 𝑢 ⟩ . L e t q¯ 𝑢 [𝑖 ] ∈ { 0 , 1 } b e th e 𝑗 th b i t o f q¯𝑢 [ 𝑖] w he r e e st im a t io n of ⟨ o , q ⟩ b a s ed on S e c ti on 3 . 2 a n d fu rt h e r c o m p u t e s a n

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
estimateddistancebetweentherawqueryandtherawdatavectors WepresenttheworkflowoftheRaBitQmethodwiththeIVFin-
basedonSection3.1.1(line3-5). dexasfollows.Duringtheindexphase,forasetofrawdatavectors,
theIVFalgorithmfirstclustersthemwiththeKMeansalgorithm,
Algorithm1:RaBitQ(IndexPhase) buildsabucketforeachclusterandassignsthevectorstotheir
correspondingbuckets.Ourmethodthennormalizestherawdata
Input :Asetofrawdatavectors
vectorsbasedonthecentroidsoftheircorrespondingclustersand
Output:Thesampledmatrix𝑃;thequantizationcodex¯𝑏 ;
feedsthesetofthenormalizedvectorstothesubsequentstepsof
thepre-computedresultsof∥o𝑟 −c∥and⟨o¯,o⟩
ourRaBitQmethod.Duringthequeryphase,forarawqueryvector,
1 Normalizethesetofvectors(Section3.1.1) thealgorithmselectsthefirst𝑁 𝑝𝑟𝑜𝑏𝑒 clusterswhosecentroidsare
2 Samplearandomorthogonalmatrix𝑃 toconstructthe nearesttothequery.Thenforeachselectedcluster,thealgorithm
codebookC𝑟𝑎𝑛𝑑 (Section3.1.2) retrievesallthequantizationcodesandestimatestheirdistances
3
Computethequantizationcodesx¯𝑏 (Section3.1.3) basedonthequantizationcodes,whichdecidethevectorstobe
4
Pre-computethevaluesof∥o𝑟 −c∥and⟨o¯,o⟩ re-rankedbasedonexactdistances.
Asforre-ranking[85],PQanditsvariantssetafixedhyper-
parameterwhichdecidesthenumberofdatavectorstobere-ranked
(i.e.,theyre-rankthevectorswiththesmallestestimateddistances).
Algorithm2:RaBitQ(QueryPhase) Specifically,theyretrievetheirrawdatavectors,computetheexact
distancesandfindoutthefinalNN.Inparticular,thetuningofthe
Input :Arawqueryvectorq𝑟 ;thesampledmatrix𝑃;aset
hyper-parameterisempiricalandoftenhardasitcanvarylargely
ofIDsofthedatavectors,theirquantizationcodes
acrossdifferentdatasets(seeSection5.2.3).Incontrast,recallthatin
x¯𝑏 andtheresultsof∥o𝑟 −c∥and⟨o¯,o⟩
ourmethod,thereisasharperrorboundasdiscussedinSection3.2
Output:Asetofapproximatedistancesbetweentheraw
(notethattheerrorboundisrigorousandalwaysholdsregardless
queryandtherawdatavectors
ofthedatadistribution).Thus,wedecidethedatavectorstobere-
Normalizeandinverselytransformtherawqueryvector
1 rankedbasedontheerrorboundwithouttuninghyper-parameters.
andobtainq′ Specifically,ifadatavectorhasitslowerboundofthedistance
2
Quantizeq′intoq¯(Section3.3.1) greaterthantheexactdistanceofthecurrentlysearchednearest
3 foreachinputIDofthedatavectorsdo neighbor,thenwedropit.Otherwise,wecomputeitsexactdistance
Computethevalueoftheestimator ⟨o¯,q⟩ asan forre-ranking.Duetothetheoreticalerrorbound,there-ranking
4 ⟨o¯,o⟩
strategyhastheguaranteeofcorrectlysendingthetrueNNfrom
approximationof⟨o,q⟩(Section3.3.2)
theprobedclusterstore-rankingwithhighprobability.Theem-
Computeanestimateddistancebetweentherawquery
5 piricalverificationcanbefoundinSection5.2.4.Weemphasize
andthedatavectorbasedonEquation(2)
thattheideaofre-rankingbasedonaboundisnotnew.Thereare
manystudiesfromthedatabasecommunitythatadoptasimilar
strategy[24,27,76,89,90,94]forimprovingtherobustnessofsim-
ilaritysearchforvariousdatatypes.Wenotethatbeyondtheidea
4 RABITQFORIN-MEMORYANNSEARCH
ofre-rankingbasedonanerrorbound,RaBitQprovidesrigorous
Nextwepresenttheapplicationofourmethodtothein-memory theoreticalanalysisonthetightnessoftheboundsandachieves
ANNsearch.WenotethatthepopularquantizationmethodPQx4fs theasymptoticoptimalityaswehavediscussedinSection3.2.2.
hasbeenusedincombinationwiththeinverted-file-basedindexes Moreover,itisworthnotingthatre-rankingisavitalstepfor
suchasIVF[45]orthegraph-basedindexessuchasNGT-QG[43] pushingforwardRaBitQ’srigorouserrorboundsonthedistancesto
forin-memoryANNsearch.Thecombinationofaquantization therobustnessofANNsearch.Inparticular,whentheANNsearch
methodwithIVFcanbeeasilydonewithoutmuchefforts.Forex- requireshigheraccuracythanwhatRaBitQcanguarantee(e.g.,
ample,wecanusethequantizationmethodtoestimatethedistances whenthetruedistancesfromthequerytotwodifferentdatavectors
betweenthedatavectorsintheclustersthatareprobed,whichde- are extremely close to each other), then the estimated distance
cidethosevectorstobere-rankedbasedonexactdistances.Inthis producedbyRaBitQwouldbelesseffectivetorankthemcorrectly.
case,batchesofdatavectorscanbeformedandtheSIMD-based Re-ranking,inthiscase,isnecessaryforachievinghighrecall.Note
fastimplementation(i.e.,PQx4fs)canbeadopted.Nevertheless, thatitisinherentlydifficultforanymethodsofdistanceestimation
thecombinationofaquantizationmethodwithgraph-basedmeth- whenthedistancesareextremelyclosetoeachother.
odssuchasNGT-QGwouldrequiremuchmoreeffortsinorderto
makethecombinedmethodworkcompetitivelyinthein-memory
5 EXPERIMENTS
setting,whichwouldbeofindependentinterest.Thisisbecause
ingraph-basedmethods,thevectorstobesearchedaredecided 5.1 ExperimentalSetup
oneafteronebasedonthegreedysearchprocessintherun-time, Ourexperimentsinvolvethreefolds.First,wecompareourmethod
anditisnoteasytoformbatchesofthemsothatSIMD-basedfast withtheconventionalquantizationmethodsintermsofthetime-
implementationcanbeadopted.Therefore,weapplyourmethodin accuracytrade-offofdistanceestimationandtimecostofindex
combinationwithIVFindex[45]inthispaper.Weleaveitasfuture phase(withresultsshowninSection5.2.1andSection5.2.2).Second,
worktoapplyourquantizationmethodingraph-basedmethods. wecomparethemethodswhenappliedforin-memoryANN(with

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
resultsshowninSection5.2.3).ForANN,wetargettoretrievethe ashasbeenreported6,itssuperiorperformanceismainlyduetothe
100nearestneighborsforeachquery,i.e.,𝐾 =100,byfollowing[30]. fastSIMD-basedimplementation[5].Theadvantagevanisheswhen
Third,weempiricallyverifyourtheoreticalanalysis(withresults PQisimplementedwiththesametechnique.Thus,weexcludeit
showninSection5.2.4to5.2.6).Finally,wenotethatRaBitQisa fromthecomparison.Furthermore,weexcludethecomparison
methodwithrigoroustheoreticalguarantee.Itscomponentsare withtheLSHmethodsbecauseithasbeenreportedthatthequan-
anintegralwholeandtogetherexplainitsasymptoticallyoptimal tizationmethodsoutperformthesemethodsempiricallybyorders
performance.Theablationofanycomponentwouldcausetheloss ofmagnitudesinefficiencywhenreachingthesamerecall[58].
ofthetheoreticalguarantee(i.e.,themethodbecomesheuristicand ThelatestadvancesinLSHhavenotchangedthistrend[80].Thus,
theperformanceisnomoretheoreticallypredictable)andfurther comparableperformancewiththequantizationmethodsindicates
disablestheerror-bound-basedre-ranking(Section4).Despitethis, significantimprovementovertheLSHmethods.
weincludeempiricalablationstudiesinthetechnicalreport[33]. PerformanceMetrics.First,forestimatingthedistancesbetween
Datasets.Weusesixpublicreal-worlddatasetswithvaryingsizes datavectorsandqueryvectors,weusetwometricstomeasurethe
anddimensionalities,whosedetailscanbefoundinTable3.These accuracyandonemetrictomeasuretheefficiency.Inparticular,
datasetshavebeenwidelyusedtobenchmarkANNalgorithms[6, wemeasuretheaccuracywith(1)theaveragerelativeerrorand
58,62,67].Inparticular,ithasbeenreportedthatonthedatasets (2)themaximumrelativeerrorontheestimatedsquareddistances.
SIFT,DEEPandGIST,PQx4fsandOPQx4fshavegoodempirical Theformermeasuresthegeneralqualityoftheestimateddistances
performance[5].Wenotethatallthesepublicdatasetsprovideboth whilethelattermeasurestherobustnessoftheestimateddistances.
dataandqueryvectors. Wemeasuretheefficiencywiththetimefordistanceestimation
Table3:DatasetStatistics pervector.Wenotethatduetotheeffectsofcache,theefficiency
Dataset Size 𝐷 QuerySize DataType dependsontheorderofestimatingdistancesforthevectors.To
Msong 992,272 420 200 Audio simulatetheorderwhenthemethodsareusedinpractice,webuild
SIFT 1,000,000 128 10,000 Image theIVFindexforallmethodsandestimatethedistancesinthe
DEEP 1,000,000 256 1,000 Image orderthattheIVFindexprobestheclusters.Wemeasuretheend-
Word2Vec 1,000,000 300 1,000 Text to-endtimeofestimatingdistancesforallthequantizationcodes
GIST 1,000,000 960 1,000 Image inadatasetanddivideitbythesizeofthedataset.Wetakethepre-
Image 2,340,373 150 200 Image processingtimeinthequeryphase(e.g.,thetimefornormalizing,
transformingandquantizingthequeryvectorforourmethod)into
Algorithms.First,forestimatingthedistancesbetweendatavec- account,thusmakingthecomparisonsfair.Wealsomeasurethe
tors and query vectors, we consider three baselines, PQ [45], timecostsofthemethodsintheindexphase.Second,forANN,we
OPQ[34]andLSQ[66,67].Inparticular,(1)PQand(2)OPQare adoptrecallandaveragedistanceratioformeasuringtheaccuracy
themostpopularmethodsamongthequantizationmethods[34,45]. ofANNsearch.Specifically,recallistheratiobetweenthenumber
Theyarewidelydeployedinindustry[48,69,84,92].Thepopularity ofretrievedtruenearestneighborsover𝐾.Averagedistanceratio
ofPQandOPQindicatesthattheyhavebeenempiricallyevaluated istheaverageofthedistanceratiosofthereturned𝐾 datavectors
tothewidestextentandareexpectedtohavethebestknownstabil- wrtthegroundtruthnearestneighbors.Thesemetricsarewidely
ity.Thus,weadoptPQandOPQastheprimarybaselinemethods adoptedtomeasuretheaccuracyofANNalgorithms[6,31,38,58,
representingthequantizationmethodswhichhavenotheoretical 78].Weadoptquerypersecond(QPS),i.e.,thenumberofqueriesa
errorbounds.Thereisanotherlineofthequantizationmethods methodcanhandleinasecond,tomeasuretheefficiency.Itiswidely
namedtheadditivequantization[8,66,67,95].ComparedwithPQ, adoptedtomeasuretheefficiencyofANNalgorithms[6,58,86].
thesemethodstargetextremeaccuracyatthecostofmuchhigher Following[6,58,86],thequerytimeisevaluatedinasinglethread
timeforoptimizingthecodebookandmappingthedatavectors andthesearchisconductedforeachqueryindividually(insteadof
intoquantizationcodesintheindexphase.(3)LSQ[66,67]isthe queriesinabatch).Allthemetricsaremeasuredoneverysingle
state-of-the-artmethodofthisline.Thus,weadoptLSQasthebase- queryandaveragedoverthewholequeryset.
linemethodrepresentingthequantizationmethodswhichpursue
ParameterSetting.AsissuggestedbyFaiss[25],thenumberof
extremeperformanceinthequeryphase.Thebaselinemethods
clustersforIVFissettobe4,096asthedatasetsareatthemillion-
aretakenfromthe1.7.4releaseversionoftheopen-sourcelibrary
Faiss[48],whichiswell-optimizedwiththeSIMDinstructionsof
scale.Forourmethod,therearetwoparameters,i.e.,𝜖0 and𝐵
𝑞
.The
theoreticalanalysisinSection3.2.2andSection3.3.1hasprovided
AVX2.Second,forANN,wecompareourmethodwiththemost
competitivebaselinemethodOPQaccordingtotheresultsinSec-
clearsuggestionsthat𝜖0 =Θ( √︁log(1/𝛿))and𝐵
𝑞
=Θ(loglog𝐷),
where𝛿 isthefailureprobability.Inpractice,theparametersare
tion5.2.1.ForbothourmethodandOPQ,wecombinethemwiththe
IVFindexasspecifiedinSection4.Wealsoincludethecomparison
fixedtobe𝜖0=1.9and𝐵
𝑞
=4acrossallthedatasets.Theempirical
parameterstudycanbefoundinSection5.2.4andSection5.2.5.
withHNSW[65]asareference.Itisoneofthestate-of-the-art
Asforthelengthofthequantizationcode,itequalsto𝐷 bydefi-
graph-basedmethodsasisbenchmarkedin[6,86]andisalsowidely
nition,butitcanalsobevariedbypaddingtherawvectorswith
adoptedinindustry[48,69,84,92].Theimplementationistaken
0’sbeforegeneratingthequantizationcodes7.Morepadded0’s
fromthehnswlib[65]optimizedwiththeSIMDinstructionsof
AVX2.WenotethatarecentquantizationmethodScaNN[37]pro-
6https://github.com/facebookresearch/faiss/wiki/Indexing-1M-vectors
posesanewobjectivefunctionforconstructingthequantization
7Weemphasizethatthepaddeddimensionswillnotberetainedafterthegeneration,
codebookofPQandclaimsbetterempiricalperformance.However, andthus,willnotaffectthespaceandtimecostsrelatedtotherawvectors.

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
indicatelongerquantizationcodesandhigheraccuracyduetoThe- accuracy.Itindicatesthatthereasonableaccuracyoftheconven-
√
orem3.2(recallthattheerrorisboundedby𝑂(1/ 𝐷)).Bydefault, tionalquantizationmethodswith𝑘 =8doesnotindicateitsnormal
thelengthofthequantizationcodeissettobethesmallestmultiple performancewith𝑘 = 4.Thus,itisnotalwaysfeasibletospeed
of64whichisnosmallerthan𝐷 (itisequaltoorslightlylarger upaconventionalquantizationmethodwiththefastSIMD-based
than𝐷)inordertomakeitpossibletostorethebitstringwitha implementation[5].Ontheotherhand,theefficiencyofthecon-
sequenceof64-bitunsignedintegers.Fortheconventionalquanti- ventionalquantizationmethodswith𝑘 =8ishardlycomparable
zationmethods(includingPQ,OPQandLSQ),therearetwoparam- withthosewith𝑘 =4ontheotherdatasets.Itindicatesthatthe
eters,namelythenumberofsub-segmentsofquantizationcodes recentsuccessofPQinthein-memoryANNislargelyattributed
𝑀 andthenumberofcandidatesforre-rankingwhichshouldbe tothefastSIMD-basedimplementation.Thus,itisnotachoiceto
tunedempirically.Followingthedefaultparametersetting[25,37], replacethefastSIMD-basedimplementationwiththeoriginalone
wesetthenumberofpartitionstobe𝑀 = 𝐷/2.Wenotethatit inpursuitofthestability.(5)ExceptforthedatasetSIFTandDEEP,
cannotbefurtherincreasedas𝐷shouldbedivisibleby𝑀forPQ PQx4fsandOPQx4fshavetheirmaximumrelativeerrorofaround
andOPQ.Thenumberofcandidatesforre-rankingisvariedamong 100%.ItindicatesthatPQandOPQdonotrobustlyproducehigh-
500,1,000and2,500.TheexperimentalresultsinSection5.2.3show accuracyestimateddistancesevenonthedatasetstheyperform
thatnoneoftheparametersworkconsistentlywellacrossdifferent wellingeneral.Asacomparison,ourmethodhasitsmaximum
datasets.ForHNSW,wefollowitsoriginalpaper[65]bysettingthe relativeerroratmost40%onallthetesteddatasets.
numberofmaximumout-degreeofeachvertexinthegraphas32
(correspondingto𝑀
𝐻𝑁𝑆𝑊
=16)andaparameterwhichcontrols Table4:TheIndexingTimefortheGISTDataset
RaBitQ PQ OPQ LSQ
theconstructionofthegraphnamed𝑒𝑓𝐶𝑜𝑛𝑠𝑡𝑟𝑢𝑐𝑡𝑖𝑜𝑛as500.
Time 117s 105s 291s time-out(>24hours)
TheC++sourcecodesarecompiledbyg++9.4.0with-Ofast
-march=core-avx2 under Ubuntu 20.04LTS. The Python source
5.2.2 TimeintheIndexingPhase. InTable4,wereporttheindexing
codesarerunonPython3.8.Allexperimentsarerunonamachine
timeofthequantizationmethods(𝑘 = 4forPQ,OPQandLSQ)
with AMD Threadripper PRO 3955WX 3.9GHz processor (with
underthedefaultparametersettingontheGISTdatasetwith32
Zen2microarchitecturewhichsupportstheSIMDinstructionstill
threadsonCPU.Theresultsshowthattheindexingtimeisnota
AVX2)and64GBRAM.Thecodeanddatasetsareavailableathttps:
bottleneckforourmethod,PQandOPQsinceallofthemcanfinish
//github.com/gaoj0017/RaBitQ.
theindexingphasewithinafewmins.However,forLSQ,ittakes
morethan24hours.ThisisbecauseinLSQ,thestepofmappinga
datavectortoitsquantizationcodeisNP-Hard[66,67].Although
5.2 ExperimentalResults
severaltechniqueshavebeenproposedforapproximatelysolving
5.2.1 Time-AccuracyTrade-OffperVectorforDistanceEstimation.
theNP-Hardproblem[66,67],thetimecostisstillmuchlarger
Weestimatethedistancebetweenadatavector(fromthesetof
thanthatofPQ,whichlargelylimitsitsusageinpractice.
datavectors)andaqueryvector(fromthesetofqueryvectors)
withdifferentquantizationmethodsincludingPQ,OPQ,LSQand 5.2.3 Time-AccuracyTrade-OffforANNSearch. Wethenmeasure
ourRaBitQmethod.Weplotthe“averagerelativeerror”-“timeper theperformanceofthealgorithmswhentheyareusedincombina-
vector”curve(leftpanels,bottom-leftisbetter)andthe“maximum tionwiththeIVFindexforANNsearch.Consideringtheresultsin
relativeerror”-“timepervector”curve(rightpanels,bottom-leftis Section5.2.1,weonlyincludeOPQx4fs-batchandRaBitQ-batchfor
better)byvaryingthelengthofthequantizationcodesinFigure3. thecomparisonasothermethodsorimplementationsareingeneral
Inparticular,forourmethod,toplotthecurve,wevarythelength dominatedwhenthequantizationcodesareallowedtobepacked
bypaddingdifferentnumberof0’sinthevectorswhengenerating inbatch.Asareference,wealsoincludeHNSWforcomparison.
thequantizationcodes.ForPQ,OPQandLSQ,wevarythelength Wethenplotthe“QPS”-“recall”curve(leftpanel,upper-rightis
bysettingdifferent𝑀(notethat𝐷mustbedivisibleby𝑀forPQ better)andthe“QPS”-“averagedistanceratio”curve(rightpanel,
andOPQ). upper-leftisbetter)byvaryingthenumberofbucketstoprobein
BasedontheresultsinFigure3,wehavethefollowingobser- theIVFindexforthequantizationmethodsinFigure4.Thecurves
vations.(1)LSQhasmuchlessstableperformancethanPQand forHNSWareplottedbyvaryingaparameternamed𝑒𝑓𝑆𝑒𝑎𝑟𝑐ℎ
OPQ.ExceptforthedatasetSIFTandDEEP,LSQx4fshasitsac- whichcontrolstheQPS-recalltradeoffofHNSW.ForOPQ,weshow
curacyworsethanPQx4fsandOPQx4fs.(2)Comparingthesolid threecurveswhichcorrespondtothreedifferentnumbersofcan-
curves,wefindthatunderthedefaultsettingofthenumberofbits didatesforre-ranking.BasedonFigure4,wehavethefollowing
(whichcorrespondstothelastpointintheredandorangesolid observations.(1)Onallthetesteddatasets,ourmethodhasconsis-
curvesandthefirstpointinthegreensolidcurve),ourmethod tentlybetterperformancethanOPQregardlessofthere-ranking
showsconsistentlybetteraccuracythanPQandOPQwhilehaving parameter. We emphasize that it has been reported that on the
comparableefficiencyonallthetesteddatasets.Weemphasizethat datasetsSIFT,DEEPandGIST,OPQx4fshasgoodempiricalperfor-
inthedefaultsetting,thelengthofthequantizationcodeofour mance[5].OurmethodalsoconsistentlyoutperformsHNSWon
methodisonlyaroundahalfofthoseofPQandOPQ(i.e.,𝐷 v.s. allthetesteddatasets.(2)OnthedatasetMSong,theperformance
2𝐷).(3)Comparingthedashedcurves,wefindthatourmethod ofOPQisdisastrousevenwithre-rankingapplied.Inparticular,as
hassignificantlybetterefficiencythanPQandOPQwhenreaching theIVFindexprobesmorebuckets,therecallabnormallydecreases
thesameaccuracy.(4)OnthedatasetMsong,PQx8andOPQx8 becauseOPQintroducestoomucherrorontheestimateddistances.
havenormalaccuracywhilePQx4fsandOPQx4fshavedisastrous ThepooraccuracyshowninFigure3canexplainthedisastrous

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
OPQx4fs-batch OPQx8-single PQx4fs-batch PQx8-single LSQx4fs-batch RaBitQ-batch RaBitQ-single
|     |     |     |     | )%( rorrE evitaleR mumixaM |     |     |     |     |     | )%( rorrE evitaleR mumixaM |     |     |     |
| --- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- |
)%( rorrE evitaleR egarevA Image Image )%( rorrE evitaleR egarevA GIST GIST
| 12.5 |     |     |     | 150 |     |     |     |     |     | 125 |     |     |     |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
15
| 10.0 |     |     |     |     |     |     |     |     |     | 100 |     |     |     |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
100
|     |     |     |     |     |     |     | 10  |     |     | 75  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
7.5
50
| 5.0 |     |     |     | 50  |     |     | 5   |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
25
2.5
|     | 5   | 10  | 15  |     | 5 10 | 15  | 0   | 50 100 | 150 |     | 0   | 50 100 | 150 |
| --- | --- | --- | --- | --- | ---- | --- | --- | ------ | --- | --- | --- | ------ | --- |
Average Time / Vector (ns) Average Time / Vector (ns) Average Time / Vector (ns) Average Time / Vector (ns)
|     |     |     |     | )%( rorrE evitaleR mumixaM |     |     |     |     |     | )%( rorrE evitaleR mumixaM |     |     |     |
| --- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- |
)%( rorrE evitaleR egarevA MSong MSong )%( rorrE evitaleR egarevA SIFT SIFT
| 100 |                      |     |     | 200 |                                          |     |     |     |     |     |     |     |     |
| --- | -------------------- | --- | --- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | out of range (>100%) |     |     |     | oouutt  ooff  rraannggee  ((>>220000%%)) |     | 12  |     |     | 100 |     |     |     |
80
|     |     |     |     | 150 |     |     | 10  |     |     | 80  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
60
8
| 40  |     |     |     | 100 |     |     | 6   |     |     | 60  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20  |     |     |     | 50  |     |     | 4   |     |     | 40  |     |     |     |
|     |     |     |     |     |     |     | 2   |     |     | 20  |     |     |     |
0
|     | 0 20 | 40  | 60  | 0   | 20 40 | 60  |     | 5 10 15 | 20  |     | 5   | 10 15 | 20  |
| --- | ---- | --- | --- | --- | ----- | --- | --- | ------- | --- | --- | --- | ----- | --- |
Average Time / Vector (ns) Average Time / Vector (ns) Average Time / Vector (ns) Average Time / Vector (ns)
)%( rorrE evitaleR egarevA DEEP )%( rorrE evitaleR mumixaM DEEP )%( rorrE evitaleR egarevA Word2Vec )%( rorrE evitaleR mumixaM Word2Vec
| 25  |     |     |     | 80  |     |     | 25  |     |     | 200 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
out of range (>200%)
| 20  |     |     |     |     |     |     | 20  |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |     | 60  |     |     |     |     |     | 150 |     |     |     |
15
|     |     |     |     |     |     |     | 15  |     |     | 100 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10  |     |     |     | 40  |     |     |     |     |     |     |     |     |     |
10
50
| 5   |     |       |     | 20  |          |     | 5   |          |       |     |     |       |       |
| --- | --- | ----- | --- | --- | -------- | --- | --- | -------- | ----- | --- | --- | ----- | ----- |
|     | 10  | 20 30 | 40  |     | 10 20 30 | 40  |     | 10 20 30 | 40 50 |     | 10  | 20 30 | 40 50 |
Average Time / Vector (ns) Average Time / Vector (ns) Average Time / Vector (ns) Average Time / Vector (ns)
Figure3:Time-AccuracyTrade-OffforDistanceApproximation.Forbaselinemethods,(1)“x4fs-batch”meansthattheSIMD-
basedfastimplementationisadopted(where4bitsencodeaquantizedcodeandapproximatedistancesforabatchof32data
vectorsarecomputedeachtime),and(2)“x8-single”meansthat8bitsencodeaquantizedcodeandtheapproximatedistanceof
onedatavectoriscomputedeachtime.Inaddition,theresultsofLSQx8-singleareomittedsinceit,withtheimplementation
fromFaiss,hasthetimecostsignificantlylargerthanothers.
IVF-OPQx4fs (rerank=500) IVF-OPQx4fs (rerank=1000) IVF-OPQx4fs (rerank=2500) IVF-RaBitQ HNSW
|            |     | Image |     |            | Image |     |     | GIST |     |     |     | GIST |     |
| ---------- | --- | ----- | --- | ---------- | ----- | --- | --- | ---- | --- | --- | --- | ---- | --- |
| 4×         |     |       |     | 4×         |       |     | 103 |      |     | 103 |     |      |     |
|            |     |       |     |            |       |     | 8×  |      |     | 8×  |     |      |     |
| 2×         |     |       |     | 2×         |       |     | 6×  |      |     | 6×  |     |      |     |
|            |     |       |     |            |       |     | 4×  |      |     | 4×  |     |      |     |
| SPQ 810× 3 |     |       |     | SPQ 810× 3 |       |     | SPQ |      |     | SPQ |     |      |     |
| 6×         |     |       |     | 6×         |       |     | 2×  |      |     | 2×  |     |      |     |
| 4×         |     |       |     | 4×         |       |     |     |      |     |     |     |      |     |
|            |     |       |     |            |       |     | 102 |      |     | 102 |     |      |     |
| 2×         |     |       |     | 2×         |       |     |     |      |     |     |     |      |     |
80 85 90 95 100 1.000 1.002 1.004 1.006 1.008 80 85 90 95 100 1.000 1.001 1.002 1.003 1.004
Recall(%) Average Distance Ratio Recall(%) Average Distance Ratio
|     |     | MSong |     |     | MSong |     |        | SIFT |     |        |     | SIFT |     |
| --- | --- | ----- | --- | --- | ----- | --- | ------ | ---- | --- | ------ | --- | ---- | --- |
|     |     |       |     |     |       |     | 8×     |      |     | 8×     |     |      |     |
| 4×  |     |       |     | 4×  |       |     |        |      |     |        |     |      |     |
|     |     |       |     |     |       |     | 6×     |      |     | 6×     |     |      |     |
| 2×  |     |       |     | 2×  |       |     |        |      |     |        |     |      |     |
| SPQ |     |       |     | SPQ |       |     | SPQ 4× |      |     | SPQ 4× |     |      |     |
| 103 |     |       |     | 103 |       |     |        |      |     |        |     |      |     |
| 8×  |     |       |     | 8×  |       |     | 2×     |      |     | 2×     |     |      |     |
| 6×  |     |       |     | 6×  |       |     |        |      |     |        |     |      |     |
| 4×  |     |       |     | 4×  |       |     |        |      |     |        |     |      |     |
|     |     |       |     |     |       |     | 103    |      |     | 103    |     |      |     |
0 20 40 60 80 100 1.0 1.1 1.2 1.3 1.4 1.5 80 85 90 95 100 1.0001.0021.0041.0061.0081.010
Recall(%) Average Distance Ratio Recall(%) Average Distance Ratio
|        |     | DEEP |     |        | DEEP |     |         | Word2Vec |     |         |     | Word2Vec |     |
| ------ | --- | ---- | --- | ------ | ---- | --- | ------- | -------- | --- | ------- | --- | -------- | --- |
| 6×     |     |      |     | 6×     |      |     |         |          |     |         |     |          |     |
| 4×     |     |      |     | 4×     |      |     |         |          |     |         |     |          |     |
|        |     |      |     |        |      |     | 2×      |          |     | 2×      |     |          |     |
| SPQ 2× |     |      |     | SPQ 2× |      |     | SPQ 103 |          |     | SPQ 103 |     |          |     |
|        |     |      |     |        |      |     | 8×      |          |     | 8×      |     |          |     |
| 103    |     |      |     | 103    |      |     | 6×      |          |     | 6×      |     |          |     |
| 8×     |     |      |     | 8×     |      |     | 4×      |          |     | 4×      |     |          |     |
| 6×     |     |      |     | 6×     |      |     | 2×      |          |     | 2×      |     |          |     |
| 4×     |     |      |     | 4×     |      |     |         |          |     |         |     |          |     |
80 85 90 95 100 1.000 1.002 1.004 1.006 1.008 80 85 90 95 100 1.000 1.001 1.002 1.003 1.004 1.005
Recall(%) Average Distance Ratio Recall(%) Average Distance Ratio
Figure4:Time-AccuracyTrade-OffforANNSearch.Theparameter𝑟𝑒𝑟𝑎𝑛𝑘representsthenumberofcandidatesforre-ranking.

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
failure.(3)Nosinglere-rankingparameterforOPQworkswell 5.2.5 ResultsforVerifyingtheStatementabout𝐵 𝑞. 𝐵 isaparam-
𝑞
acrossallthedatasets.OnSIFT,DEEPandGIST,1,000ofcandidates eter whichcontrols the errorintroduced in thecomputation of
forre-rankingsufficetoproduceanearlyperfectrecallwhileon ⟨o¯,q⟩.DuetoouranalysisinSection3.3.1,𝐵 =Θ(loglog𝐷)suf-
𝑞
ImageandWord2Vec,alargernumberofcandidatesforre-ranking ficestomakesurethattheerrorintroducedinthecomputationof
isneeded.Wenotethatthetuningofthere-rankingparameter ⟨o¯,q⟩ismuchsmallerthantheerroroftheestimator.Wenotethat
isoftenexhaustiveastheparametersareintertwinedwithmany Θ(loglog𝐷)variesextremelyslowlywithrespectto𝐷,andthus,
factorssuchasthedatasetsandtheotherparameters.Priortothe itcanbeviewedasaconstantwhenthedimensionalitydoesnot
testing,thereisnoreliablewaytopredicttheoptimalsettingof varylargely.InFigure6,weprovidetheempiricalverificationon
parametersinpractice.Incontrast,recallthatasisdiscussedinSec- thestatement.Inparticular,weplotthe“averagerelativeerror”-
tion3.2.2andSection3.3.1,inourmethod,thetheoreticalanalysis “𝐵 𝑞 ”curvebyvarying𝐵 𝑞 from1to8.Figure6showsthatontwo
providesexplicitsuggestionsontheparameters.Thus,ourmethod differentdatasets,bothcurvesshowhighlysimilartrendsthatthe
requiresnotuning. errorconvergesquicklyataround𝐵 =4.Ontheotherhand,we
𝑞
|     |     |     |     |     | wouldalsoliketohighlightthatfurtherreducing𝐵 |     |     | wouldproduce |
| --- | --- | --- | --- | --- | -------------------------------------------- | --- | --- | ------------ |
𝑞
unignorableerrorinthecomputationof⟨o¯,q⟩.Inparticular,when
|     | SIFT (D=128) |     |     | GIST (D=960) |     |     |     |     |
| --- | ------------ | --- | --- | ------------ | --- | --- | --- | --- |
100 100 𝐵 𝑞 =1,i.e.,bothqueryanddatavectorsarequantizedintobinary
|     |     |     |     |     | strings,theerrorismuchlargerthantheerrorwhen𝐵 |     |     | 𝑞 =4.This |
| --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --------- |
| 80  |     |     | 80  |     |                                               |     |     |           |
)%( llaceR )%( llaceR resultmayhelptoexplainwhythebinaryhashingmethodscannot
| 60  |     |     | 60  |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
achievegoodempiricalperformance.
| 40  |     |     | 40  |         |     |     |     |     |
| --- | --- | --- | --- | ------- | --- | --- | --- | --- |
| 20  |     |     | 20  |         |     |     |     |     |
| 0   |     |     | 0   |         |     |     |     |     |
| 0   | 1 2 | 3 4 | 0   | 1 2 3 4 |     |     |     |     |
|     | 0   |     |     | 0       |     |     |     |     |
Figure5:VerificationStudyon𝜖0.
| 5.2.4 ResultsforVerifyingtheStatementabout𝜖0. |     |     |     | 𝜖0 isaparame- |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | ------------- | --- | --- | --- | --- |
terwhichcontrolstheconfidenceintervaloftheerrorbound(see
Section3.2.2).WhentheRaBitQmethodisappliedinANNsearch,
itfurthercontrolstheprobabilitythatwecorrectlysendtheNNto
re-ranking(seeSection4).Inparticular,tomakesurethefailure
probabilitybenogreaterthan𝛿,thetheoreticalanalysisinSec-
tion3.2.2suggeststoset𝜖0=Θ( √︁log(1/𝛿)).Weemphasizethatthe Figure7:VerificationStudyforUnbiasedness.
statementisindependentofanyotherfactorssuchasthedatasets
InFigure7,weverify
orthesettingofotherparameters.Thisisthereasonthatthepa- 5.2.6 ResultsforVerifyingtheUnbiasedness.
theunbiasednessofourmethodandshowthebiasednessofOPQ.
rameterneedsnotuning.InFigure5,weprovidetheempirical Wecollect107pairsoftheestimatedsquareddistancesandthetrue
| verificationonthestatement.Inparticular,weplotthe“recall”-“𝜖0 |     |     |     | ”   |     |     |     |     |
| ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
squareddistancesbetweenthequeryanddatavectors(i.e.,thefirst
| curvebyvarying𝜖0 | from0.0to4.0.Therecallismeasuredbyesti- |     |     |     |     |     |     |     |
| ---------------- | --------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
10queryvectorsinthequerysetandthe106datavectorsinthe
matingthedistancesforallthedatavectorsanddecidethevectors
fulldatasetofGIST)toverifytheunbiasedness.Thevaluesofthe
tobere-rankedbasedonthestrategyinSection4(notethatifa
distancesarenormalizedbythemaximumtruesquareddistances.
truenearestneighborisnotre-ranked,itwillbemissed).Thus,the Wefitthe107pairswithlinearregressionandplottheresultwith
factors(otherthantheerrorofquantizationmethods)whichmay
theblackdashedline.Wenotethatifamethodisunbiased,theresult
affecttherecallareeliminated.Figure5showsthatontwodifferent
ofthelinearregressionshouldhavetheslopeof1andthey-axis
datasets,bothcurvesshowhighlysimilartrendsthatitachieves
interceptof0(thegreendashedlineasareference).Figure7clearly
nearlyperfectrecallataround𝜖0=1.9.
showsthatourmethodisunbiased,whichverifiesthetheoretical
analysisinSection3.2.2.Ontheotherhand,theestimateddistances
producedbyOPQisclearlybiased.
| )%( rorrE evitaleR egarevA | SIFT (D=128) | )%( rorrE evitaleR egarevA |     | GIST (D=960) |               |                  |         |                     |
| -------------------------- | ------------ | -------------------------- | --- | ------------ | ------------- | ---------------- | ------- | ------------------- |
| 15                         |              |                            | 15  |              | 6 RELATEDWORK |                  |         |                     |
|                            |              |                            |     |              |               |                  |         | Existing studies on |
| 10                         |              |                            | 10  |              | Approximate   | Nearest Neighbor | Search. |                     |
ANNsearchareusuallycategorizedintofourtypes:(1)graph-based
| 5   |     |     | 5   |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
methods[29,30,58,64,65,74],(2)quantization-basedmethods[8,
0 0 34,36,37,45,66,67,73,95],(3)tree-basedmethods[10,15,17,71]
| 2   | 4 6 | 8   | 2   | 4 6 8 |                                                        |                         |           |                     |
| --- | --- | --- | --- | ----- | ------------------------------------------------------ | ----------------------- | --------- | ------------------- |
|     | Bq  |     |     | Bq    | and(4)hashing-basedmethods[18,31,35,38,39,54,56,63,78– |                         |           |                     |
|     |     |     |     |       | 80, 97]. We                                            | refer readers to recent | tutorials | [23, 75] and bench- |
Figure6:VerificationStudyon𝐵 marks/surveys[6,7,19,58,86,88]foracomprehensivereview.We
𝑞.
notethatrecently,manystudiesdesignalgorithmsorsystemsby

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
jointlyconsideringdifferenttypesofmethodssothatamethod thequeryphase,theyneeddecompresstheshortcodesandcom-
canenjoythemeritsofbothsides[1,12,13,21,43,62,96].Our putethedistanceswiththedecompressedvectors,whichdegrades
workproposesaquantizationmethodwhichprovidesasharperror tothebruteforceinefficiency.Forthisreason,thesemethodshave
boundandgoodempiricalperformanceatthesametime.Justlike not been adopted in practice. In contrast, our method supports
theconventionalquantizationmethods,itcanworkasacompo- practicallyefficientcomputationasisspecifiedinSection3.3.
nentinanintegratedalgorithmorsystem.Ourmethodhastwo
SignedRandomProjection.Wenotethattherearealineofstud-
additionaladvantages:(1)itinvolvesnoparametertuningand(2)it
iesnamedsignedrandomprojection(SRP)whichgenerateashort
supportsefficientdistanceestimationforasinglequantizationcode.
codeforestimatingtheangularvaluesbetweenvectorsviabinariz-
Theseadvantagesmayfurthersmoothenitscombinationwithother
ingthevectorsafterrandomization[11,22,46,51].Wenotethatour
typesofmethods.Recently,thereareathreadofmethodswhich
methodisdifferentfromthesestudiesinthefollowingaspects.(1)
applymachinelearning(ML)onANN[9,20,26,55,57,87,91].
Problem-wise,SRPtargetstounbiasedlyestimatetheangularvalue
Quantization. There is a vast literature about the quantiza- whileRaBitQtargetstounbiasedlyestimatetheinnerproduct(and
tionofhigh-dimensionalvectorsfromdifferentcommunitiesin- further,thesquareddistances).Notethattherelationshipbetween
cluding machine learning, computer vision and data manage- theangularvalueandtheinnerproductisnon-linear.Theunbiased
ment[8,27,34,36,45,66,67,73,81,90,95].Wereferreadersto estimatorforonedoesnottriviallyderiveanunbiasedestimator
comprehensivesurveys[24,68,83,85]andreferencebooks[76,94]. fortheother.(2)Theory-wise,RaBitQhasastrongertypeofguar-
Itisworthofmentioningthatin[81],aquantizationmethodcalled anteethanSRP.Inparticular,RaBitQguaranteesthateverydata
Split-VQ was mentioned. The method covers the major idea of vectorhasitsdistancewithintheboundswithhighprobability.In
PQ, i.e., it splits the vectors into sub-segments, constructs sub- contrast,SRPonlyboundsthevariance,i.e.,the“average”squared
codebooks for each sub-segment and forms the codebook with error,anditdoesnotprovideaboundforeveryestimatedvalue.
Cartesianproduct.BesidesPQanditsvariants,thereareothertypes Thus,itcannothelpwiththere-rankinginsimilaritysearch.(3)
ofquantizationmethods,e.g.,scalarquantization[1,27,90].These Technique-wise,inSRPthebitstringsareviewedassomehashing
methodsquantizethescalarvaluesofeachdimensionseparately, codeswhileinRaBitQ,thebitstringsarethebinaryrepresentations
whichoftenadoptmoremoderatecompressionratesthanPQin ofbi-valuedvectors.Moreover,SRPmapsboththedataandquery
exchangeforbetteraccuracy.Inparticular,VA+File[27],ascalar vectorstobitstrings,whichintroduceserrorfrombothsides.In
quantizationmethod,hasshownleadingperformanceonthesimi- contrast,RaBitQquantizesthedatavectorstobebitstringsandthe
laritysearchofdataseriesaccordingtoarecentbenchmark[24]. queryvectorstobevectorsof4-bitunsignedintegers.Theorem3.3
Besidesthestudiesonthequantizationalgorithms,wenotethat provesthatquantizingthequeryvectorsonlyintroducesnegligible
hardware-awareoptimization(withSIMD,GPU,FPGA,etc)also error.Thus,RaBitQonlyintroducestheerrorfromthesideofthe
makessignificantcontributionstotheperformanceofthesemeth- datavector.
ods[4,5,47,48,61].Toinheritthemeritsofthewell-developed
hardware-awareoptimization,inthiswork,wereduceourcom- 7 CONCLUSION
putationtothecomputationofPQ(Section3.3).However,RaBitQ, Inconclusion,weproposeanovelrandomizedquantizationmethod
initsnature,canbeimplementedwithmuchsimplerbitwiseop- RaBitQwhichhasclearadvantagesinbothempiricalaccuracyand
erations(whichisnotpossibleforPQanditsvariants).Itremains rigoroustheoreticalerrorboundoverPQanditsvariants.Thepro-
tobeaninterestingquestionwhetherdedicatedhardware-aware posedefficientimplementationsbasedonsimplebitwiseoperations
optimizationcanfurtherimprovetheperformanceofRaBitQ. orfastSIMD-basedoperationsfurthermakeitstandoutintermsof
thetime-accuracytrade-offforthein-memoryANNsearch.Exten-
TheoreticalStudiesonHigh-DimensionalVectors.Thetheo-
siveexperimentsonreal-worlddatasetsverifyboth(1)theempirical
reticalstudiesonhigh-dimensionalvectorsareprimarilyaboutthe
superiorityofourmethodintermsofthetime-accuracytrade-off
seminalJohnson-Lindenstrauss(JL)Lemma[49].Itpresentsthat
reducingthedimensionalityofavectorto𝑂(𝜖−2log(1/𝛿))suffices and(2)thealignmentoftheempiricalperformancewiththetheoret-
icalanalysis.Someinterestingresearchdirectionsincludeapplying
toguaranteetheerrorboundof𝜖.RecentadvancesimprovetheJL
ourmethodinotherscenariosofANNsearch(e.g.,withgraph-
Lemmaindifferentaspects.Forexample,[53]provestheoptimality
basedindexesoronotherstoragedevices[14,42,44,59]).Besides,
oftheJLLemma.[2,50]proposefastalgorithmstodothedimension
RaBitQcanalsobetriviallyappliedtounbiasedlyestimatecosine
reduction.Wereferreaderstoacomprehensivesurvey[28].Our
similarityandinnerproduct8,whichfurtherimpliesitspotentialin
methodfitsintoarecentlineofstudies[3,40,41,72],whichtarget
maximuminnerproductsearchandneuralnetworkquantization.
toimprovetheJLLemmabycompressinghigh-dimensionalvectors
intoshortcodes.Asacomparison,toguaranteeanerrorboundof
𝜖,theJLLemmarequiresavectorof𝑂(𝜖−2log(1/𝛿))dimensions ACKNOWLEDGEMENTS
whilethesestudiesprovethatashortcodewith𝑂(𝜖−2log(1/𝛿)) Wewouldliketothanktheanonymousreviewersforproviding
bitswouldbesufficient.Inpracticalterms,wenotethatalthough constructivefeedbackandvaluablesuggestions.Thisresearchis
theexistingstudiesachievetheimprovementintheoryintermsof
thespacecomplexity(i.e.,theminimumnumberofbitsneededfor 8The cosine similarity of two vectors exactly equals to the inner product of
guaranteeingacertainerrorbound),theycarelessabouttheim- theirunitvectors.Theinnerproductofoandqcanbeexpressedas ⟨o,q⟩ =
provementinefficiency.Inparticular,thesemethodsdonotsuitthe
⟨o−c+c,q−c+c⟩=∥o−c∥·∥q−c∥·⟨(o−c)/∥o−c∥,(q−c)/∥q−c∥⟩+
⟨o,c⟩+⟨q,c⟩−∥c∥2,wherecisthecentroidofthedatavectors,anditreducesto
in-memoryANNsearchbecause,forestimatingthedistanceduring theestimationofinnerproductbetweenunitvectorsaswedoinSection3.1.1.

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
supportedbytheMinistryofEducation,Singapore,underitsAca- [19] MagdalenDobson,ZheqiShen,GuyEBlelloch,LaxmanDhulipala,YanGu,
demicResearchFund(Tier2AwardMOE-T2EP20221-0013,Tier2 HarshaVardhanSimhadri,andYihanSun.2023. ScalingGraph-BasedANNS
AwardMOE-T2EP20220-0011,andTier1Award(RG77/21)).Any AlgorithmstoBillion-SizeDatasets:AComparativeAnalysis. arXivpreprint
arXiv:2305.04359(2023).
opinions,findingsandconclusionsorrecommendationsexpressed [20] YiheDong,PiotrIndyk,IlyaRazenshteyn,andTalWagner.2020.LearningSpace
inthismaterialarethoseoftheauthor(s)anddonotreflectthe PartitionsforNearestNeighborSearch.InInternationalConferenceonLearning
Representations. https://openreview.net/forum?id=rkenmREFDr
viewsoftheMinistryofEducation,Singapore. [21] MatthijsDouze,AlexandreSablayrolles,andHervéJégou.2018.LinkandCode:
FastIndexingwithGraphsandCompactRegressionCodes.In2018IEEE/CVF
ConferenceonComputerVisionandPatternRecognition.3646–3654. https://doi.
org/10.1109/CVPR.2018.00384
REFERENCES
[22] PunitPankajDubey,BhishamDevVerma,RameshwarPratap,andKeeganKang.
[1] CeciliaAguerrebere,IshwarSinghBhati,MarkHildebrand,MarianoTepper,and 2022.Improvingsign-random-projectionviacountsketch.InProceedingsofthe
TheodoreWillke.2023.SimilaritySearchintheBlinkofanEyewithCompressed Thirty-EighthConferenceonUncertaintyinArtificialIntelligence(Proceedingsof
Indices. Proc.VLDBEndow.16,11(aug2023),3433–3446. https://doi.org/10. MachineLearningResearch,Vol.180),JamesCussensandKunZhang(Eds.).PMLR,
14778/3611479.3611537 599–609. https://proceedings.mlr.press/v180/dubey22a.html
[2] NirAilonandBernardChazelle.2009.TheFastJohnson–LindenstraussTransform [23] KarimaEchihabi,KostasZoumpatianos,andThemisPalpanas.2021.NewTrends
andApproximateNearestNeighbors. SIAMJ.Comput.39,1(2009),302–322. inHigh-DVectorSimilaritySearch:Al-Driven,Progressive,andDistributed.Proc.
https://doi.org/10.1137/060673096arXiv:https://doi.org/10.1137/060673096 VLDBEndow.14,12(jul2021),3198–3201. https://doi.org/10.14778/3476311.
[3] NogaAlonandBo’azKlartag.2017.OptimalCompressionofApproximateInner 3476407
ProductsandDimensionReduction.In2017IEEE58thAnnualSymposiumon [24] KarimaEchihabi,KostasZoumpatianos,ThemisPalpanas,andHoudaBenbrahim.
FoundationsofComputerScience(FOCS).639–650. https://doi.org/10.1109/FOCS. 2018.TheLernaeanHydraofDataSeriesSimilaritySearch:AnExperimental
2017.65 EvaluationoftheStateoftheArt.Proc.VLDBEndow.12,2(oct2018),112–127.
[4] FabienAndré,Anne-MarieKermarrec,andNicolasLeScouarnec.2015.Cache https://doi.org/10.14778/3282495.3282498
LocalityisNotEnough:High-PerformanceNearestNeighborSearchwithProduct [25] Faiss.2023.Faiss.https://github.com/facebookresearch/faiss.
QuantizationFastScan. Proc.VLDBEndow.9,4(dec2015),288–299. https: [26] ChaoFeng,DefuLian,XitingWang,ZhengLiu,XingXie,andEnhongChen.
//doi.org/10.14778/2856318.2856324 2022.ReinforcementRoutingonProximityGraphforEfficientRecommendation.
[5] FabienAndré,Anne-MarieKermarrec,andNicolasLeScouarnec.2017.Accel- ACMTrans.Inf.Syst.(jan2022). https://doi.org/10.1145/3512767JustAccepted.
eratedNearestNeighborSearchwithQuickADC.InProceedingsofthe2017 [27] HakanFerhatosmanoglu,ErtemTuncel,DivyakantAgrawal,andAmrElAbbadi.
ACMonInternationalConferenceonMultimediaRetrieval(Bucharest,Romania) 2000.VectorApproximationBasedIndexingforNon-UniformHighDimensional
(ICMR’17).AssociationforComputingMachinery,NewYork,NY,USA,159–166. DataSets.InProceedingsoftheNinthInternationalConferenceonInformation
https://doi.org/10.1145/3078971.3078992 andKnowledgeManagement(McLean,Virginia,USA)(CIKM’00).Associationfor
[6] MartinAumüller,ErikBernhardsson,andAlexanderFaithfull.2020. ANN- ComputingMachinery,NewYork,NY,USA,202–209. https://doi.org/10.1145/
Benchmarks:ABenchmarkingToolforApproximateNearestNeighborAlgo- 354756.354820
rithms.Inf.Syst.87,C(jan2020),13pages. https://doi.org/10.1016/j.is.2019.02.006 [28] CasperBenjaminFreksen.2021. AnIntroductiontoJohnson-Lindenstrauss
[7] MartinAumüllerandMatteoCeccarello.2023.RecentApproachesandTrendsin Transforms.CoRRabs/2103.00564(2021).arXiv:2103.00564 https://arxiv.org/abs/
ApproximateNearestNeighborSearch,withRemarksonBenchmarking.Data 2103.00564
Engineering(2023),89. [29] CongFu,ChangxuWang,andDengCai.2021. Highdimensionalsimilarity
[8] ArtemBabenkoandVictorLempitsky.2014.AdditiveQuantizationforExtreme searchwithsatellitesystemgraph:Efficiency,scalability,andunindexedquery
VectorCompression.In2014IEEEConferenceonComputerVisionandPattern compatibility. IEEETransactionsonPatternAnalysisandMachineIntelligence
Recognition.931–938. https://doi.org/10.1109/CVPR.2014.124 (2021).
[9] DmitryBaranchuk,DmitryPersiyanov,AntonSinitsin,andArtemBabenko. [30] CongFu,ChaoXiang,ChangxuWang,andDengCai.2019.FastApproximate
2019.LearningtoRouteinSimilarityGraphs.InProceedingsofthe36thInterna- NearestNeighborSearchwiththeNavigatingSpreading-outGraph.Proc.VLDB
tionalConferenceonMachineLearning(ProceedingsofMachineLearningResearch, Endow.12,5(jan2019),461–474. https://doi.org/10.14778/3303753.3303754
Vol.97),KamalikaChaudhuriandRuslanSalakhutdinov(Eds.).PMLR,475–484. [31] JunhaoGan,JianlinFeng,QiongFang,andWilfredNg.2012.Locality-Sensitive
https://proceedings.mlr.press/v97/baranchuk19a.html HashingSchemeBasedonDynamicCollisionCounting.InProceedingsofthe
[10] AlinaBeygelzimer,ShamKakade,andJohnLangford.2006. Covertreesfor 2012ACMSIGMODInternationalConferenceonManagementofData(Scottsdale,
nearestneighbor.InProceedingsofthe23rdinternationalconferenceonMachine Arizona,USA)(SIGMOD’12).AssociationforComputingMachinery,NewYork,
learning.97–104. NY,USA,541–552. https://doi.org/10.1145/2213836.2213898
[11] MosesS.Charikar.2002.SimilarityEstimationTechniquesfromRoundingAlgo- [32] JianyangGaoandChengLong.2023.High-DimensionalApproximateNearest
rithms.InProceedingsoftheThiry-FourthAnnualACMSymposiumonTheoryof NeighborSearch:WithReliableandEfficientDistanceComparisonOperations.
Computing(Montreal,Quebec,Canada)(STOC’02).AssociationforComputing Proc.ACMManag.Data1,2,Article137(jun2023),27pages. https://doi.org/10.
Machinery,NewYork,NY,USA,380–388. https://doi.org/10.1145/509907.509965 1145/3589282
[12] Patrick H. Chen, Wei-Cheng Chang, Jyun-Yu Jiang, Hsiang-Fu Yu, Inder- [33] JianyangGaoandChengLong.2024. RaBitQ:QuantizingHigh-Dimensional
jit S. Dhillon, and Cho-Jui Hsieh. 2023. FINGER: Fast inference for VectorswithTheoreticalErrorBoundforApproximateNearestNeighborSearch
graph-based approximate nearest neighbor search. In The Web Conference (TechnicalReport).https://github.com/gaoj0017/RaBitQ/technical_report.pdf.
2023.https://www.amazon.science/publications/finger-fast-inference-for-graph- [34] TiezhengGe,KaimingHe,QifaKe,andJianSun.2013. Optimizedproduct
based-approximate-nearest-neighbor-search quantizationforapproximatenearestneighborsearch.InProceedingsoftheIEEE
[13] QiChen,HaidongWang,MingqinLi,GangRen,ScarlettLi,JefferyZhu,Jason ConferenceonComputerVisionandPatternRecognition.2946–2953.
Li,ChuanjieLiu,LintaoZhang,andJingdongWang.2018.SPTAG:Alibraryfor [35] LongGong,HuayiWang,MitsunoriOgihara,andJunXu.2020.IDEC:Indexable
fastapproximatenearestneighborsearch. https://github.com/Microsoft/SPTAG DistanceEstimatingCodesforApproximateNearestNeighborSearch.Proc.VLDB
[14] QiChen,BingZhao,HaidongWang,MingqinLi,ChuanjieLiu,ZengzhongLi, Endow.13,9(may2020),1483–1497. https://doi.org/10.14778/3397230.3397243
MaoYang,andJingdongWang.2021. SPANN:Highly-efficientBillion-scale [36] YunchaoGong,SvetlanaLazebnik,AlbertGordo,andFlorentPerronnin.2013.
ApproximateNearestNeighborSearch.In35thConferenceonNeuralInformation IterativeQuantization:AProcrusteanApproachtoLearningBinaryCodesfor
ProcessingSystems(NeurIPS2021). Large-ScaleImageRetrieval.IEEETransactionsonPatternAnalysisandMachine
[15] PaoloCiaccia,MarcoPatella,andPavelZezula.1997. M-Tree:AnEfficient Intelligence35,12(2013),2916–2929. https://doi.org/10.1109/TPAMI.2012.193
AccessMethodforSimilaritySearchinMetricSpaces.InProceedingsofthe23rd [37] RuiqiGuo,PhilipSun,ErikLindgren,QuanGeng,DavidSimcha,FelixChern,and
InternationalConferenceonVeryLargeDataBases(VLDB’97).MorganKaufmann SanjivKumar.2020.AcceleratingLarge-ScaleInferencewithAnisotropicVector
PublishersInc.,SanFrancisco,CA,USA,426–435. Quantization.InProceedingsofthe37thInternationalConferenceonMachine
[16] T.CoverandP.Hart.1967.Nearestneighborpatternclassification.IEEETrans- Learning(ICML’20).JMLR.org,Article364,10pages.
actionsonInformationTheory13,1(1967),21–27. https://doi.org/10.1109/TIT. [38] QiangHuang,JianlinFeng,YikaiZhang,QiongFang,andWilfredNg.2015.
1967.1053964 Query-awarelocality-sensitivehashingforapproximatenearestneighborsearch.
[17] SanjoyDasguptaandYoavFreund.2008. Randomprojectiontreesandlow ProceedingsoftheVLDBEndowment9,1(2015),1–12.
dimensionalmanifolds.InProceedingsofthefortiethannualACMsymposiumon [39] PiotrIndykandRajeevMotwani.1998.Approximatenearestneighbors:towards
Theoryofcomputing.537–546. removingthecurseofdimensionality.InProceedingsofthethirtiethannualACM
[18] MayurDatar,NicoleImmorlica,PiotrIndyk,andVahabSMirrokni.2004.Locality- symposiumonTheoryofcomputing.604–613.
sensitivehashingschemebasedonp-stabledistributions.InProceedingsofthe
twentiethannualsymposiumonComputationalgeometry.253–262.

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
[40] PiotrIndyk,IlyaRazenshteyn,andTalWagner.2017.PracticalData-Dependent 2017ACMonConferenceonInformationandKnowledgeManagement(Singapore,
MetricCompressionwithProvableGuarantees.InProceedingsofthe31stInterna- Singapore)(CIKM’17).AssociationforComputingMachinery,NewYork,NY,
tionalConferenceonNeuralInformationProcessingSystems(LongBeach,Califor- USA,667–676. https://doi.org/10.1145/3132847.3132901
nia,USA)(NIPS’17).CurranAssociatesInc.,RedHook,NY,USA,2614–2623. [60] YingLiu,DengshengZhang,GuojunLu,andWei-YingMa.2007.Asurveyof
[41] PiotrIndykandTalWagner.2022. Optimal(Euclidean)MetricCompression. content-basedimageretrievalwithhigh-levelsemantics.PatternRecognition40,
SIAMJ.Comput.51,3(2022),467–491. https://doi.org/10.1137/20M1371324 1(2007),262–282. https://doi.org/10.1016/j.patcog.2006.04.045
arXiv:https://doi.org/10.1137/20M1371324 [61] ZihanLiu,WentaoNi,JingwenLeng,YuFeng,CongGuo,QuanChen,Chao
[42] JunhyeokJang,HanjinChoi,HanyeoreumBae,SeungjunLee,MiryeongKwon, Li,MinyiGuo,andYuhaoZhu.2023. JUNO:OptimizingHigh-Dimensional
andMyoungsooJung.2023. CXL-ANNS:Software-HardwareCollaborative ApproximateNearestNeighbourSearchwithSparsity-AwareAlgorithmand
MemoryDisaggregationandComputationforBillion-ScaleApproximateNearest Ray-TracingCoreMapping. arXiv:2312.01712[cs.DC]
NeighborSearch.In2023USENIXAnnualTechnicalConference(USENIXATC23). [62] KejingLu,MineichiKudo,ChuanXiao,andYoshiharuIshikawa.2021. HVS:
USENIXAssociation,Boston,MA,585–600. https://www.usenix.org/conference/ HierarchicalGraphStructureBasedonVoronoiDiagramsforSolvingApprox-
atc23/presentation/jang imateNearestNeighborSearch. Proc.VLDBEndow.15,2(oct2021),246–258.
[43] YahooJapan.2022.NGT-QG.https://github.com/yahoojapan/NGT. https://doi.org/10.14778/3489496.3489506
[44] SuhasJayaramSubramanya,FnuDevvrit,HarshaVardhanSimhadri,Ravishankar [63] KejingLu,HongyaWang,WeiWang,andMineichiKudo.2020.VHP:approximate
Krishnawamy,andRohanKadekodi.2019.DiskANN:FastAccurateBillion-point nearestneighborsearchviavirtualhyperspherepartitioning.Proceedingsofthe
NearestNeighborSearchonaSingleNode.InAdvancesinNeuralInformation VLDBEndowment13,9(2020),1443–1455.
ProcessingSystems,H.Wallach,H.Larochelle,A.Beygelzimer,F.d'Alché-Buc, [64] YuryMalkov,AlexanderPonomarenko,AndreyLogvinov,andVladimirKrylov.
E.Fox,andR.Garnett(Eds.),Vol.32.CurranAssociates,Inc. https://proceedings. 2014.Approximatenearestneighboralgorithmbasedonnavigablesmallworld
neurips.cc/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf graphs.InformationSystems45(2014),61–68. https://doi.org/10.1016/j.is.2013.
[45] HerveJegou,MatthijsDouze,andCordeliaSchmid.2010.Productquantization 10.006
fornearestneighborsearch.IEEEtransactionsonpatternanalysisandmachine [65] YuA.MalkovandD.A.Yashunin.2020. EfficientandRobustApproximate
intelligence33,1(2010),117–128. NearestNeighborSearchUsingHierarchicalNavigableSmallWorldGraphs.
[46] JianqiuJi,JianminLi,ShuichengYan,BoZhang,andQiTian.2012.Super-Bit IEEETransactionsonPatternAnalysisandMachineIntelligence42,4(2020),824–
Locality-SensitiveHashing.InProceedingsofthe25thInternationalConferenceon 836. https://doi.org/10.1109/TPAMI.2018.2889473
NeuralInformationProcessingSystems-Volume1(LakeTahoe,Nevada)(NIPS’12). [66] JulietaMartinez,JorisClement,HolgerH.Hoos,andJamesJ.Little.2016. Re-
CurranAssociatesInc.,RedHook,NY,USA,108–116. visitingAdditiveQuantization.InComputerVision–ECCV2016,BastianLeibe,
[47] WenqiJiang,ShigangLi,YuZhu,JohannesDeFineLicht,ZhenhaoHe,Runbin JiriMatas,NicuSebe,andMaxWelling(Eds.).SpringerInternationalPublishing,
Shi,CedricRenggli,ShuaiZhang,TheodorosRekatsinas,TorstenHoefler,and Cham,137–153.
GustavoAlonso.2023.Co-designHardwareandAlgorithmforVectorSearch. [67] JulietaMartinez,ShobhitZakhmi,HolgerH.Hoos,andJamesJ.Little.2018.
InProceedingsoftheInternationalConferenceforHighPerformanceComputing, LSQ++:LowerRunningTimeandHigherRecallinMulti-CodebookQuantization.
Networking,StorageandAnalysis(Denver,CO,USA)(SC’23).Associationfor InComputerVision–ECCV2018:15thEuropeanConference,Munich,Germany,
ComputingMachinery,NewYork,NY,USA,Article87,15pages. https://doi. September8-14,2018,Proceedings,PartXVI(Munich,Germany).Springer-Verlag,
org/10.1145/3581784.3607045 Berlin,Heidelberg,508–523. https://doi.org/10.1007/978-3-030-01270-0_30
[48] JeffJohnson,MatthijsDouze,andHervéJégou.2019. Billion-scalesimilarity [68] YusukeMatsui,YusukeUchida,HervéJégou,andShin’ichiSatoh.2018.ASurvey
searchwithGPUs.IEEETransactionsonBigData7,3(2019),535–547. ofProductQuantization.ITETransactionsonMediaTechnologyandApplications
[49] WilliamBJohnsonandJoramLindenstrauss.1984. ExtensionsofLipschitz 6,1(2018),2–10.
mappingsintoaHilbertspace26.Contemporarymathematics26(1984),28. [69] JasonMohoney,AnilPacaci,ShihaburRahmanChowdhury,AliMousavi,IhabF.
[50] DanielM.KaneandJelaniNelson.2014.SparserJohnson-LindenstraussTrans- Ilyas,UmarFarooqMinhas,JeffreyPound,andTheodorosRekatsinas.2023.High-
forms.J.ACM61,1,Article4(jan2014),23pages. https://doi.org/10.1145/2559902 ThroughputVectorSimilaritySearchinKnowledgeGraphs.Proc.ACMManag.
[51] KeeganKangandWeipinWong.2018.ImprovingSignRandomProjectionsWith Data1,2,Article197(jun2023),25pages. https://doi.org/10.1145/3589777
AdditionalInformation.InProceedingsofthe35thInternationalConferenceon [70] RajeevMotwaniandPrabhakarRaghavan.1995.RandomizedAlgorithms.Cam-
MachineLearning(ProceedingsofMachineLearningResearch,Vol.80),Jennifer bridgeUniversityPress. https://doi.org/10.1017/CBO9780511814075
DyandAndreasKrause(Eds.).PMLR,2479–2487. https://proceedings.mlr.press/ [71] MariusMujaandDavidGLowe.2014. Scalablenearestneighboralgorithms
v80/kang18b.html forhighdimensionaldata. IEEEtransactionsonpatternanalysisandmachine
[52] V. I. Khokhlov. 2006. The Uniform Distribution on a Sphere in intelligence36,11(2014),2227–2240.
R𝑆. Properties of Projections. I. Theory of Probability & Its Applica- [72] RasmusPaghandJohanSivertsen.2020.TheSpaceComplexityofInnerProduct
tions 50, 3 (2006), 386–399. https://doi.org/10.1137/S0040585X97981846 Filters.In23rdInternationalConferenceonDatabaseTheory(ICDT2020)(Leib-
arXiv:https://doi.org/10.1137/S0040585X97981846 nizInternationalProceedingsinInformatics(LIPIcs),Vol.155),CarstenLutzand
[53] KasperGreenLarsenandJelaniNelson.2017. OptimalityoftheJohnson- JeanChristophJung(Eds.).SchlossDagstuhl–Leibniz-ZentrumfürInformatik,
Lindenstrausslemma.In2017IEEE58thAnnualSymposiumonFoundationsof Dagstuhl,Germany,22:1–22:14. https://doi.org/10.4230/LIPIcs.ICDT.2020.22
ComputerScience(FOCS).IEEE,633–638. [73] JohnPaparrizos,IkraduyaEdian,ChunweiLiu,AaronJ.Elmore,andMichaelJ.
[54] YifanLei,QiangHuang,MohanKankanhalli,andAnthonyK.H.Tung.2020. Franklin.2022.FastAdaptiveSimilaritySearchthroughVariance-AwareQuan-
Locality-SensitiveHashingSchemeBasedonLongestCircularCo-Substring.In tization.In2022IEEE38thInternationalConferenceonDataEngineering(ICDE).
Proceedingsofthe2020ACMSIGMODInternationalConferenceonManagementof 2969–2983. https://doi.org/10.1109/ICDE53745.2022.00268
Data(Portland,OR,USA)(SIGMOD’20).AssociationforComputingMachinery, [74] YunPeng,ByronChoi,TszNamChan,JianyeYang,andJianliangXu.2023.
NewYork,NY,USA,2589–2599. https://doi.org/10.1145/3318464.3389778 EfficientApproximateNearestNeighborSearchinMulti-DimensionalDatabases.
[55] ConglongLi,MinjiaZhang,DavidG.Andersen,andYuxiongHe.2020. Im- Proc.ACMManag.Data1,1,Article54(may2023),27pages. https://doi.org/10.
provingApproximateNearestNeighborSearchthroughLearnedAdaptiveEarly 1145/3588908
Termination.InProceedingsofthe2020ACMSIGMODInternationalConferenceon [75] JianbinQin,WeiWang,ChuanXiao,YingZhang,andYaoshuWang.2021.High-
ManagementofData(Portland,OR,USA).AssociationforComputingMachinery, DimensionalSimilarityQueryProcessingforDataScience.InProceedingsofthe
NewYork,NY,USA,2539–2554. https://doi.org/10.1145/3318464.3380600 27thACMSIGKDDConferenceonKnowledgeDiscoveryandDataMining(Virtual
[56] JinfengLi,XiaoYan,JianZhang,AnXu,JamesCheng,JieLiu,KelvinK.W.Ng,and Event,Singapore)(KDD’21).AssociationforComputingMachinery,NewYork,
Ti-chungCheng.2018.AGeneralandEfficientQueryingMethodforLearning NY,USA,4062–4063. https://doi.org/10.1145/3447548.3470811
toHash.InProceedingsofthe2018InternationalConferenceonManagementof [76] HananSamet.2005.FoundationsofMultidimensionalandMetricDataStructures
Data(Houston,TX,USA)(SIGMOD’18).AssociationforComputingMachinery, (TheMorganKaufmannSeriesinComputerGraphicsandGeometricModeling).
NewYork,NY,USA,1333–1347. https://doi.org/10.1145/3183713.3183750 MorganKaufmannPublishersInc.,SanFrancisco,CA,USA.
[57] MingjieLi,Yuan-GenWang,PengZhang,HanpinWang,LishengFan,Enxia [77] J.BenSchafer,DanFrankowski,JonHerlocker,andShiladSen.2007.Collaborative
Li,andWeiWang.2023. DeepLearningforApproximateNearestNeighbour FilteringRecommenderSystems.SpringerBerlinHeidelberg,Berlin,Heidelberg,
Search:ASurveyandFutureDirections.IEEETransactionsonKnowledgeandData 291–324. https://doi.org/10.1007/978-3-540-72079-9_9
Engineering35,9(2023),8997–9018. https://doi.org/10.1109/TKDE.2022.3220683 [78] YifangSun,WeiWang,JianbinQin,YingZhang,andXueminLin.2014. SRS:
[58] WenLi,YingZhang,YifangSun,WeiWang,MingjieLi,WenjieZhang,and solvingc-approximatenearestneighborqueriesinhighdimensionaleuclidean
XueminLin.2019.Approximatenearestneighborsearchonhighdimensional spacewithatinyindex.ProceedingsoftheVLDBEndowment(2014).
data—experiments,analyses,andimprovement.IEEETransactionsonKnowledge [79] YufeiTao,KeYi,ChengSheng,andPanosKalnis.2010. Efficientandaccu-
andDataEngineering32,8(2019),1475–1488. ratenearestneighborandclosestpairsearchinhigh-dimensionalspace.ACM
[59] YingfanLiu,HongCheng,andJiangtaoCui.2017.PQBF:I/O-EfficientApprox- TransactionsonDatabaseSystems(TODS)35,3(2010),1–46.
imateNearestNeighborSearchbyProductQuantization.InProceedingsofthe [80] Y.Tian,X.Zhao,andX.Zhou.2022.DB-LSH:Locality-SensitiveHashingwith
Query-basedDynamicBucketing.In2022IEEE38thInternationalConference

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
onDataEngineering(ICDE).IEEEComputerSociety,LosAlamitos,CA,USA,
2250–2262. https://doi.org/10.1109/ICDE53745.2022.00214
[81] ErtemTuncel,HakanFerhatosmanoglu,andKennethRose.2002.VQ-Index:An
IndexStructureforSimilaritySearchinginMultimediaDatabases.InProceedings
oftheTenthACMInternationalConferenceonMultimedia(Juan-les-Pins,France)
(MULTIMEDIA’02).AssociationforComputingMachinery,NewYork,NY,USA,
543–552. https://doi.org/10.1145/641007.641117
[82] RomanVershynin.2018. High-DimensionalProbability:AnIntroductionwith
ApplicationsinDataScience. CambridgeUniversityPress. https://doi.org/10.
1017/9781108231596
[83] JunWang,WeiLiu,SanjivKumar,andShih-FuChang.2016.LearningtoHash
forIndexingBigData-ASurvey.Proc.IEEE104,1(2016),34–57. https://doi.
org/10.1109/JPROC.2015.2487976
[84] JianguoWang,XiaomengYi,RentongGuo,HaiJin,PengXu,ShengjunLi,Xi-
angyuWang,XiangzhouGuo,ChengmingLi,XiaohaiXu,KunYu,Yuxing
Yuan,YinghaoZou,JiquanLong,YudongCai,ZhenxiangLi,ZhifengZhang,
YihuaMo,JunGu,RuiyiJiang,YiWei,andCharlesXie.2021. Milvus:A
Purpose-BuiltVectorDataManagementSystem.InProceedingsofthe2021In-
ternationalConferenceonManagementofData(VirtualEvent,China)(SIGMOD
’21).AssociationforComputingMachinery,NewYork,NY,USA,2614–2627.
https://doi.org/10.1145/3448016.3457550
[85] JingdongWang,TingZhang,jingkuansong,NicuSebe,andHengTaoShen.2018.
ASurveyonLearningtoHash.IEEETransactionsonPatternAnalysisandMachine
Intelligence40,4(2018),769–790. https://doi.org/10.1109/TPAMI.2017.2699960
[86] MengzhaoWang,XiaoliangXu,QiangYue,andYuxiangWang.2021.ACompre-
hensiveSurveyandExperimentalComparisonofGraph-BasedApproximate
NearestNeighborSearch. Proc.VLDBEndow.14,11(jul2021),1964–1978.
https://doi.org/10.14778/3476249.3476255
[87] YifanWang,HaodiMa,andDaisyZheWang.2022.LIDER:AnEfficientHigh-
DimensionalLearnedIndexforLarge-ScaleDensePassageRetrieval.Proc.VLDB
Endow.16,2(oct2022),154–166. https://doi.org/10.14778/3565816.3565819
[88] ZeyuWang,PengWang,ThemisPalpanas,andWeiWang.2023. Graph-and
Tree-basedIndexesforHigh-dimensionalVectorSimilaritySearch:Analyses,
Comparisons,andFutureDirections.DataEngineering(2023),3–21.
[89] ZeyuWang,QitongWang,PengWang,ThemisPalpanas,andWeiWang.2023.
Dumpy:Acompactandadaptiveindexforlargedataseriescollections.Proceed-
ingsoftheACMonManagementofData1,1(2023),1–27.
[90] RogerWeber,Hans-JörgSchek,andStephenBlott.1998.AQuantitativeAnalysis
andPerformanceStudyforSimilarity-SearchMethodsinHigh-Dimensional
Spaces.InProceedingsofthe24rdInternationalConferenceonVeryLargeData
Bases(VLDB’98).MorganKaufmannPublishersInc.,SanFrancisco,CA,USA,
194–205.
[91] ShitaoXiao,ZhengLiu,WeihaoHan,JianjinZhang,DefuLian,YeyunGong,Qi
Chen,FanYang,HaoSun,YingxiaShao,andXingXie.2022.Distill-VQ:Learning
RetrievalOrientedVectorQuantizationByDistillingKnowledgefromDense
Embeddings.InProceedingsofthe45thInternationalACMSIGIRConferenceon
ResearchandDevelopmentinInformationRetrieval(Madrid,Spain)(SIGIR’22).
ACM,NewYork,NY,USA,1513–1523. https://doi.org/10.1145/3477495.3531799
[92] WenYang,TaoLi,GaiFang,andHongWei.2020.PASE:PostgreSQLUltra-High-
DimensionalApproximateNearestNeighborSearchExtension.InProceedingsof
the2020ACMSIGMODInternationalConferenceonManagementofData(Portland,
OR,USA)(SIGMOD’20).AssociationforComputingMachinery,NewYork,NY,
USA,2241–2253. https://doi.org/10.1145/3318464.3386131
[93] R.ZamirandM.Feder.1992. Onuniversalquantizationbyrandomizeduni-
form/latticequantizers. IEEETransactionsonInformationTheory38,2(1992),
428–436. https://doi.org/10.1109/18.119699
[94] PavelZezula,GiuseppeAmato,VlastislavDohnal,andMichalBatko.2010.Simi-
laritySearch:TheMetricSpaceApproach(1sted.).SpringerPublishingCompany,
Incorporated.
[95] TingZhang,ChaoDu,andJingdongWang.2014. CompositeQuantization
forApproximateNearestNeighborSearch.InProceedingsofthe31stInterna-
tionalConferenceonMachineLearning(ProceedingsofMachineLearningResearch,
Vol.32),EricP.XingandTonyJebara(Eds.).PMLR,Bejing,China,838–846.
https://proceedings.mlr.press/v32/zhangd14.html
[96] XiZhao,YaoTian,KaiHuang,BolongZheng,andXiaofangZhou.2023.Towards
EfficientIndexConstructionandApproximateNearestNeighborSearchinHigh-
DimensionalSpaces. Proc.VLDBEndow.16,8(jun2023),1979–1991. https:
//doi.org/10.14778/3594512.3594527
[97] BolongZheng,ZhaoXi,LiangguiWeng,NguyenQuocVietHung,HangLiu,
andChristianSJensen.2020.PM-LSH:AfastandaccurateLSHframeworkfor
high-dimensionalapproximateNNsearch.ProceedingsoftheVLDBEndowment
13,5(2020),643–655.

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
APPENDIX product, we only need to pick the x which has its signs of the
|     |     |     |     |     |     |     | entriesmatchthevector𝑃−1 |     |     | o.Thus,theresultoftheinnerproduct |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | --- | --------------------------------- | --- | --- | --- |
A THEPROOFOFLEMMA3.1
isthesummationtheabsolutevaluesasispresentedin(30),where
| P r o o f    | . W h e n o a n d        | q a r e c o  | ll in e a r, | i. e ., q =  | − o o r q =     | o , ( 9 ) ca n |       |                 |                                                  |     |     |     |     |
| ------------ | ------------------------ | ------------ | ------------ | ------------ | --------------- | -------------- | ----- | --------------- | ------------------------------------------------ | --- | --- | --- | --- |
|              |                          |              |              |              |                 |                | ∥· ∥ℓ | is t h e ℓ1     | n o r m .                                        |     |     |     |     |
| be ea s il y | v e rifi e d b y d e fin | it i o n . W | h e n o      | a n d q a re | n o n -c ol lin | e a r , th e y |       | 1               |                                                  |     |     |     |     |
|              |                          |              |              |              |                 |                | W     | e n o t e th at | o i s a unitvector.𝑃isarandomorthogonaltransfor- |     |     |     |     |
canbehostedinatwo-dimensionalsubspace.Wefirstfindapair
mationmatrix(i.e.,randomrotation),whoseinversematrix(inverse
of(mutuallyorthogonalunit)coordinatevectorsofthesubspace,
rotation)isalsoarandomorthogonaltransformationmatrix.Thus,
,
i.e.,oande1 := q − ⟨ q o ⟩ o ,whichcanbeverifiedby thevector𝑃−1 ofollowstheuniformdistributionontheunitsphere
∥ q − ⟨ q , o ⟩ o∥
S𝐷−1 inthe𝐷-dimensionalspaceR𝐷.Wenotethatthedistribu-
|     | (cid:28) | (cid:29) | ⟨q,o⟩−⟨q,o⟩·∥o∥2 |     |     |     |     |     |     |     |     |     |     |
| --- | -------- | -------- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
q−⟨q,o⟩o
⟨o,e1⟩= o, = =0 (23) tioniswellstudied[52,82].Werestatesomeconclusionsaboutthe
|     | ∥q−⟨q,o⟩o∥ |     | ∥q−⟨q,o⟩o∥ |     |     |     |     |     |     |     |     |     |     |
| --- | ---------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
distributionwiththefollowinglemma.
Wenextdecomposeo¯andqbasedonthecoordinatevectorsoand
e1 asfollows. LemmaB.1. ([52,82])Fora𝐷-dimensionalrandomvectorx =
(x[1],x[2],...,x[𝐷])whichfollowstheuniformdistributiononthe
| o¯  | =(o¯−⟨o¯,o⟩o−⟨o¯,e1⟩e1)+⟨o¯,o⟩o+⟨o¯,e1⟩e1 |     |     |     |     | (24) |     |     |     |     |     |     |     |
| --- | ----------------------------------------- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
unitsphere,theprobabilitydensityfunctionofitseverycoordinate
| q=⟨q,o⟩o+⟨q,e1⟩e1 |     |     |     |     |     | (25) |     |     |     |     |     |     |     |
| ----------------- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
x[1],x[2],...,x[𝐷]isgivenas
| where (25) | is because | q is | in the | subspace. | Then | because |     |     |     |     |     |     |     |
| ---------- | ---------- | ---- | ------ | --------- | ---- | ------- | --- | --- | --- | --- | --- | --- | --- |
(o¯ − ⟨ o¯ ,o⟩o−⟨o¯,e1⟩e1)isorthogonaltothesubspaceando⊥e1 , Γ ( 𝐷 )
|            |     |     |     |     |     |     |     | 𝑝 𝐷(𝑥)= |     | 2 (1−𝑥2  | 𝐷 −3 | ,𝑥 [−1,1] | (31) |
| ---------- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | -------- | ---- | --------- | ---- |
| w e ha v e |     |     |     |     |     |     |     |         | √   |          | ) 2  | ∈         |      |
|            |     |     |     |     |     |     |     |         | 𝜋 Γ | ( 𝐷 −1 ) |      |           |      |
2
|     | ⟨o¯,q⟩=⟨o¯,o⟩·⟨o,q⟩+⟨o¯,e1⟩·⟨q,e1⟩ |     |     |     |     | (26) |     |     |     |     |     |     |     |
| --- | ---------------------------------- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
whereΓ(·)istheGammafunction.Thetailboundisgivenas
√︃
|     | =⟨o¯,o⟩·⟨o,q⟩+⟨o¯,e1⟩· |     |     | 1−⟨o,q⟩ | 2   | (27) |     |     |          |     |                   |               |     |
| --- | ---------------------- | --- | --- | ------- | --- | ---- | --- | --- | -------- | --- | ----------------- | ------------- | --- |
|     |                        |     |     |         |     |      |     |     | (cid:26) | 𝑡   | (cid:27) (cid:16) | −𝑐0𝑡2(cid:17) |     |
where(27)isduetothePythagoreanTheorem. □ P |x[𝑖]| > ≤2exp (32)
√
𝐷
B THEANALYSISFORTHECONCENTRATION
|     |     |     |     |     |     |     | where𝑐0isaconstant,𝑖 |     | =1,2,...,𝐷. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | ----------- | --- | --- | --- | --- |
PHENOMENON
Inthispart,weproviderigorousanalysisfortheconcentrationphe- Basedontheexplicitexpressionoftheprobabilisticdensityfunc-
nomenonpresentedinSection3.2.1.Inparticular,wewillanalyze tion,wenextderivetheexpectedvalueof⟨o¯,o⟩asfollows.
theexpectedvalueof⟨o¯,o⟩(SectionB.1),theextentofconcentration
o f , ⟩( S e c t i on B . 2 )a nd t h e jo i nt d is t r ib u t io n of o¯, ⟩, ,e (cid:34) 𝐷 (cid:35)
| ⟨ o¯ o |     |     |     |     | ( ⟨ o | ⟨o ¯ 1 ⟩ ) |     |           | 1   | ∑︁  |                             |          |      |
| ------ | --- | --- | --- | --- | ----- | ---------- | --- | --------- | --- | --- | --------------------------- | -------- | ---- |
|        |     |     |     |     |       |            |     | E[⟨o¯,o⟩] | =√  | ·E  | (cid:12) (cid:12)(𝑃−1 o)[𝑖] | (cid:12) | (33) |
( S e c t io n B . 3 ) . W e s u m m ar i ze t h e co n c l u si o n s in L e m m a B . 3 a n d (cid:12)
𝐷 𝑖=1
| empiricallyverifytheminFigure8. |                 |           |         |            |     |     |     |     | √                  |              |                  |            |      |
| ------------------------------- | --------------- | --------- | ------- | ---------- | --- | --- | --- | --- | ------------------ | ------------ | ---------------- | ---------- | ---- |
|                                 |                 |           |         |            |     |     |     |     | 𝐷·E(cid:2)(cid:12) | (cid:12)(𝑃−1 | (cid:12) (cid:3) |            |      |
|                                 |                 |           |         |            |     |     |     |     | =                  |              | o)[1] (cid:12)   |            | (34) |
| B . 1 T                         | h e E x p e c t | e d V a l | u e o f | ⟨ o¯ , o ⟩ |     |     |     |     |                    |              |                  |            |      |
|                                 |                 |           |         |            |     |     |     |     | √︂𝐷                | Γ ( 𝐷 )      | ∫ 1              |            |      |
|                                 |                 |           |         |            |     |     |     |     |                    | 2            | (1−𝑥2            | 𝐷 −3 |𝑥|d𝑥 | (35) |
A s i s a n a l yz e d i n S e c t io n 3 .2 . 1 , ⟨ o¯ , o ⟩ a n d ⟨ o¯ , e 1⟩ c o r r e sp o n d t o t h e = · ) 2
|     |     |     |     |     |     |     |     |     | 𝜋   | Γ ( 𝐷 −1 | ) −1 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---- | --- | --- |
pr o j ec t i o n o f th e r a n d o m v e c t o r o ¯ o n t o t w o m ut u a l l y o rt h o g o n a l 2
directions.Inordertoanalyzethejointdistributionoftherandom √︂𝐷 2Γ( 𝐷 )
|     |     |     |     |     |     |     |     |     |     |     | 2   |     | (36) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- |
variables,letusfirstrevisittheprocessofthegenerationofo¯.The =
|     |     |     |     |     |     |     |     |     | 𝜋   | (𝐷−1)Γ( | 𝐷−1 ) |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ----- | --- | --- |
2
generationofo¯involvestwosteps.First,thealgorithmrandomly
transformsadeterministiccodebookCintoC𝑟𝑎𝑛𝑑 witharandom where(33)isdueto(30).(34)isduetothelinearityofexpectation.
orthogonaltransformation𝑃.Second,itchoosesthevectoro¯which (35)isduetoLemmaB.1.(36)isbyelementarycalculus.
| hasthelargestinnerproductwithofromthevectorsinC𝑟𝑎𝑛𝑑 |     |     |     |     |     | .We |     |     |     |     |     |     |     |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Wenotethatalthoughtheexpectedvalueof⟨o¯,o⟩hasacompli-
nextdeducefromthedefinition(generation)of⟨o¯,o⟩asfollows.
catedform,i.e.,(36),itsnumericalvalueishighlystable.When𝐷
⟨o¯,o⟩=max⟨𝑃x,o⟩ (28) rangesfrom102to106,thevaluerangesfrom0.798to0.800,which
|     | x∈𝐶 |     |     |     |     |     | isverifiedbytheobservationsinSection3.2.1perfectly. |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- |
𝐷
|     | x,𝑃−1          |            | ∑︁     | x[𝑖]·(𝑃−1 |       |      |     |                    |     |     |        |     |     |
| --- | -------------- | ---------- | ------ | --------- | ----- | ---- | --- | ------------------ | --- | --- | ------ | --- | --- |
|     | =m a x(cid:10) | o (cid:11) | =m a x |           | o)[𝑖] | (29) |     |                    |     |     |        |     |     |
|     | 𝐶              |            | 𝐶      |           |       |      | B.2 | TheConcentrationof |     |     | ⟨o¯,o⟩ |     |     |
|     | x∈             |            | x∈     | 𝑖=1       |       |      |     |                    |     |     |        |     |     |
𝐷 Wenextanalyzetheextentoftheconcentrationof⟨o¯,o⟩.Recallthat
|     | 1 ∑︁(cid:12) |     |     | 1   |     |     |     |     |     |     |     |     |     |
| --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:12)(𝑃−1 o)[𝑖] (cid:12) ∥𝑃−1 o∥ℓ1 (30) asisshownin(30), ⟨o¯,o⟩ = √ 1 ∥𝑃−1 o∥ℓ1 .Let 𝑓(x) := √ 1 ∥x∥ℓ1 .
|     | =√  |     | (cid:12)= | √   |     |     |            |     |                                             | 𝐷   |     |     | 𝐷   |
| --- | --- | --- | --------- | --- | --- | --- | ---------- | --- | ------------------------------------------- | --- | --- | --- | --- |
|     | 𝐷   |     |           | 𝐷   |     |     |            |     |                                             |     |     |     |     |
|     | 𝑖=1 |     |           |     |     |     | Then⟨o¯,o⟩ | =   | 𝑓(𝑃−1 o).Wenotethat𝑓(x)isaLipschitzfunction |     |     |     |     |
where(28)isduetotheprocessofgenerationofo¯.(29)isbecausethe withtheLipschitzconstantof1,i.e.,
innerproductisinvarianttoorthogonaltransformation(rotation).
(30)isduetothedefinitionofourcodebookCandthedefinition |𝑓(x)−𝑓(y)| ≤1·∥x−y∥ (37)
| ofℓ1 norm.Specifically,as |     | isanalyze | dinSection3.1.3,theentry |     |     |     |     |     |     |     |     |     |     |
| ------------------------- | --- | --------- | ------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
√ √
of x ∈ C can only be 1/ 𝐷 or −1/ 𝐷. To maximize the inner foreveryx,yontheunitsphere.

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
Proof. provethatthejointdistributionof(⟨𝑈𝑃x¯,u1⟩,⟨𝑈𝑃x¯,u2⟩)isiden-
|     |              |     | 1   |                      |          |      | ticaltothatof |            |     |             |     |          |      |
| --- | ------------ | --- | --- | -------------------- | -------- | ---- | ------------- | ---------- | --- | ----------- | --- | -------- | ---- |
|     | |𝑓(x)−𝑓(y)|= |     |     | (cid:12)             | (cid:12) | (38) |               |            |     |             |     |          |      |
|     |              |     | √   | (cid:12)∥x∥ℓ1 −∥y∥ℓ1 | (cid:12) |      |               | (cid:18)   |     |             |     | (cid:19) |      |
|     |              |     | 𝐷   |                      |          |      |               |            |     | √︃          | 2   |          |      |
|     |              |     |     |                      |          |      |               | ⟨𝑈𝑃x¯,u1⟩, |     | 1−⟨𝑈𝑃x¯,u1⟩ | ·𝑋1 |          | (45) |
𝐷
|     | 1   |     | 1   |                  |     |      |     |     |     |     |     |     |     |
| --- | --- | --- | --- | ---------------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |     | ∑︁ 1·|x[𝑖]−y[𝑖]| |     | (39) |     |     |     |     |     |     |     |
≤√ ∥x−y∥ℓ1 = √ where𝑋1 isindependentto ⟨𝑈𝑃x¯,u1⟩ and𝑋1 ∼ 𝑝 𝐷−1 .Because
|     | 𝐷   |     | 𝐷   |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝑖=1 therandomorthogonaltransformationisrotation-invariant,i.e.,
(cid:118)(cid:117)(cid:116) 𝐷 (cid:118)(cid:117)(cid:116) 𝐷 t h e d i s t r i bu t i o n of 𝑈 𝑃 is i de n t ic a l to th e d is t r ib u ti o n o f 𝑃 , w ec a n
1
∑︁ 12· ∑︁ (x[𝑖]−y[𝑖])2=∥x−y∥ (40) s u bs t i t u t e a l l t he 𝑈 𝑃 w it h 𝑃 . T h e n th e s ta t e m e n t r ed u c e s to t h e
|     | ≤√  | ·   |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝐷
𝑖=1 𝑖=1 sameformastheoriginalonewhilereplacingoande1 withu1 and
where(38)isbydefinition.(39)isbytriangle’sinequality.(40)is u2 ,respectively.Thus,inordertoprovethestatementforageneral
duetoCauchy-Schwarzinequality. □ pairofoande1 ,itsufficestoprovethecaseofo=u1 ande1=u2
|     |     |     |     |     |     |     | withoutlossofgenerality.Wenextprovethecaseofu1,u2 |     |     |     |     |     | .   |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- |
Recallthat𝑃−1 oisarandomvectorwhichfollowstheuniform WeconsideranalyzingthedistributionbasedonthePrincipleof
distributionontheunitsphere.Thereisawell-knownlemma[82] DeferredDecision[70].ThebasicideaofthePrincipleofDeferred
whichpresentsthatpassingarandomvectorwhichfollowsthe
Decisionisthatforarandomizedalgorithmwhichneedssample
uniformdistributionontheunitspherethroughaLipschitzfunction severalrandomnumbers,weassumethatthesamplingoperation
producesahighlyconcentrateddistribution.Thespecificresultis happensatthetimewhenthealgorithmaccessesthesamplednum-
presentedasfollows. bersinsteadofhappeningintheverybeginning.Inourcase,recall
thatwewillsamplearandomorthogonalmatrix𝑃.Itsgeneration
| LemmaB.2. | ([82])Letxbea𝐷-dimensionalrandomvectorwhich |     |     |     |     |     |     |     |     |     |     |     |     |
| --------- | ------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
involvessampling𝐷×𝐷ofstandardGaussianrandomvariablesas
followstheuniformdistributionontheunitsphere,𝑓(x)isaLipschitz
itsentriesandorthonormalizingthematrixwiththeGram–Schmidt
functionwiththeLipschitzconstantof𝐿.Then
orthonormalization.WenotethattheGram–Schmidtorthonormal-
(cid:18) 𝑐𝐷𝑡2(cid:19) izationproceedsrowbyrow.Inparticular,assumingthatthefirst
|     | P{|𝑓(x)−E[𝑓(x)]| |     |     | ≥𝑡}≤2exp | −   | (41) |                              |     |     |                                |     |     |     |
| --- | ---------------- | --- | --- | -------- | --- | ---- | ---------------------------- | --- | --- | ------------------------------ | --- | --- | --- |
|     |                  |     |     |          | 𝐿2  |      | 𝑖 −1rowsof𝑃,i.e.,p1,...,p𝑖−1 |     |     | ,havebeenorthonormalized(i.e., |     |     |     |
where𝑐isaconstant. p𝑗 ⊥p𝑘 ,∥p𝑗∥=∥p𝑘∥=1,∀1≤ 𝑗 <𝑘 ≤𝑖−1),weorthonormalize
|     |     |     |     |     |     |     | thefirst𝑖rowbylettingp𝑖 |     |     | be  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------------- | --- | --- | --- | --- | --- | --- |
Plugging in o u r 𝑓 (x ) im m e d ia t e ly y ie ld s t h e fo l lo w in gresul t . (cid:205)𝑖 1 (cid:10) (cid:11)
|     |     |     |       |     |                   |        |     |     | g             | − − g | , p 𝑗 p 𝑗 |     |      |
| --- | --- | --- | ----- | --- | ----------------- | ------ | --- | --- | ------------- | ----- | --------- | --- | ---- |
|     |     |     |       |     | (cid:16) (cid:17) |        |     |     |               | 𝑗 = 1 |           |     | (46) |
|     | P   | ,o  | E o¯, | 𝑡   | 2 e x p 𝑐 𝐷 𝑡2    | ( 4 2) |     |     | p𝑖 = (cid:13) |       | (cid:13)  |     |      |
{ |⟨ o¯ ⟩ − [⟨ o ⟩ ] | ≥ } ≤ − (cid:205) 𝑖 − 1 (cid:10) , (cid:11)
|     |          |     |     |          |                       |     |     |     | (cid:13) g | − 𝑗 1 g | p 𝑗 p 𝑗 (cid:13) |     |     |
| --- | -------- | --- | --- | -------- | --------------------- | --- | --- | --- | ---------- | ------- | ---------------- | --- | --- |
|     | (cid:26) |     |     | (cid:27) |                       |     |     |     | (cid:13)   | =       | (cid:13)         |     |     |
|     |          |     |     | 𝑢        | (cid:16) −𝑐𝑢2(cid:17) |     |     |     |            |         |                  |     |     |
P |⟨o¯,o⟩−E[⟨o¯,o⟩]| ≥ √ ≤2exp (43) wheretheentriesofgaresampledfromastandardrandomGaussian
|     |     |     |     | 𝐷   |     |     | distribution.Thus,duetotheprocessofGram–Schmidtorthonor- |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
√
malization,thesamplingprocesscanbeviewedasasequential
| where(43)isbyletting𝑢 |     |     | =𝑡 𝐷.Theconclusionshowsthat⟨o¯,o⟩ |     |     |     |     |     |     |     |     |     |     |
| --------------------- | --- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
processof𝐷stepswhereineachstepwesampleanewrow.
ishighlyconcentratedarounditsexpectation.Itwillnotdeviate
√
fromitsexpectationbyΩ(1/ 𝐷)withhighprobability. In our algorithm, we note that the joint distribution of
|     |     |     |     |     |     |     | (⟨𝑃x¯,u1⟩,⟨𝑃x¯,u2⟩) |     | depends | only on | the first | two row | of𝑃. Let |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | ------- | ------- | --------- | ------- | -------- |
(⟨o¯,o⟩,⟨o¯,e1⟩) usfirstsamplethefirstrowof𝑃,i.e.,p1 .Thenx¯ isdetermined
B.3 TheJointDistributionof
because
Wenextanalyzethedistributionof⟨o¯,e1⟩.Recallthattherandom-
nessofboth⟨o¯,o⟩and⟨o¯,e1⟩isduetotherandomnessofo¯(which =argmax⟨𝑃x,u1⟩=argmax(cid:10) x,𝑃−1 (cid:11) (47)
|     |     |     |     |     |     |     |     | x¯  |     |     |     | u1  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |     |     |     |     |     |     | x∈C |     | x∈C |     |     |
isfurtherduetotherandomnessof𝑃).Theserandomvariablesare
|     |     |     |     |     |     |     |     | =argmax(cid:10) | x,𝑃⊤u1 | (cid:11) =argmax⟨x,p1⟩ |     |     | (48) |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | ------ | ---------------------- | --- | --- | ---- |
correlatedwitheachother,whichisundesirableforsubsequent
analysis.Wefirstconsiderdecorrelatingtherandomvariablesby x∈C x∈C
representing⟨o¯,e1⟩withafunctionof⟨o¯,o⟩andarandomvariable where(48)isbecausetheinverseofanorthogonalmatrixequalsto
whichisindependentto⟨o¯,o⟩.Inparticular,wewillshowthatthe itstranspose.Forthefixedx¯,wenextanalyzethedistributionof
jointdistributionof(⟨o¯,o⟩,⟨o¯,e1⟩)isidenticaltothatof ⟨𝑃x¯,u2⟩.Wenotethatsimilarlly,itdependsonlyonthefirsttwo
|     |     |          |     |     |          |     | rowsof𝑃 | because⟨𝑃x¯,u2⟩=⟨x¯,p2⟩(recallthatx¯dependsonp1 |     |     |     |     | ).  |
| --- | --- | -------- | --- | --- | -------- | --- | ------- | ----------------------------------------------- | --- | --- | --- | --- | --- |
|     |     | (cid:18) | √︃  |     | (cid:19) |     |         |                                                 |     |     |     |     |     |
2 Forthevectorp1 andx¯,thereexistsanorthogonalmatrix𝑉 toalign
|     |     | ⟨o¯,o⟩, | 1−⟨o¯,o⟩ |     | ·𝑋1 | (44) |     |     |     |     |     |     |     |
| --- | --- | ------- | -------- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
√︃
|         |                           |     |     |     |                 |     | themonv1=(1,0,0,...,0)andv2=(⟨x¯,p1⟩, |                |     |     | 1−⟨x¯,p1⟩ |     | 2,0,...,0), |
| ------- | ------------------------- | --- | --- | --- | --------------- | --- | ------------------------------------- | -------------- | --- | --- | --------- | --- | ----------- |
| where𝑋1 | followsthedistributionof𝑝 |     |     | 𝐷−1 | inLemmaB.1andis |     |                                       |                |     |     |           |     |             |
|         |                           |     |     |     |                 |     | i.e.,v1=𝑉p1                           | andv2=𝑉x¯.Then |     |     |           |     |             |
independentto⟨o¯,o⟩.
|     |     |     |     |     |     |     |     |          | (cid:28) |               | (cid:29) |     |      |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | -------- | ------------- | -------- | --- | ---- |
|     |     |     |     |     |     |     |     |          |          | g − ⟨ g , p 1 | ⟩ p 1    |     |      |
|     |     |     |     |     |     |     |     | ⟨x¯,p2⟩= | x¯,      |               |          |     | (49) |
Proof. Letu1 = (1,0,0,...,0),u2 = (0,1,0,...,0).Foroande1 ∥g − ⟨ g , p ⟩ p ∥
1 1
w h e r e o ⊥ e , t h e r e ex is t s a n o r th o g o n a l m a t r i x 𝑈 to a li gn t h e m (cid:28) (cid:29)
|     | 1   |     |     |     |     |     |     |     |     | 𝑉 g− ⟨ 𝑉 | g , 𝑉 p ⟩ 𝑉 | p   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | --- | --- |
o n a n d , i . e . , 𝑈 = , 𝑈 = . T h en b y a p p ly in g th e o r - = 𝑉x¯, 1 1 (50)
| u 1 | u 2 | o   | u 1 e | 1 u 2 |     |     |     |     |     | ∥𝑉 −⟨ 𝑉 | , 𝑉 ⟩ 𝑉 | ∥   |     |
| --- | --- | --- | ----- | ----- | --- | --- | --- | --- | --- | ------- | ------- | --- | --- |
th o g o n a l m a t ri x 𝑈 to b o t h s id e s o f t h e i n n e r p ro d u c t s , w e h a v e g g p 1 p 1
| a   | rg m ax |     | ,   |     | a n d |     |     |     | (cid:28) | g −⟨ g , v | ⟩ v (cid:29) |     |     |
| --- | ------- | --- | --- | --- | ----- | --- | --- | --- | -------- | ---------- | ------------ | --- | --- |
x ¯ = ⟨𝑈 𝑃 x , u1 ⟩ ⟨ 𝑃 x¯ , o ⟩ = ⟨ 𝑈 𝑃x¯ , u 1 ⟩ ⟨𝑃 x¯ , e 1 ⟩ = = v2, 1 1 (51)
|     | x ∈ | C   |     |     |     |     |     |     |     | ∥ g− ⟨ , | ⟩ ∥ |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | --- | --- |
⟨ 𝑈 𝑃x¯ ,u 2⟩ .T h u s ,to p ro v e t h e o r ig i n al sta t em e n t, i t is e qu iv a l e n tt o g v 1 v 1

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
where(49)isbyGram-Schmidtorthonormalization.(50)isbecause of𝑝 asisspecifiedinLemmaB.1.Itshowsthattheempirical
𝐷−1
innerproductandEuclideandistanceareinvarianttoorthogonal resultsandthetheoreticalresultsmatchperfectly,whichverifies
transformation.(51)isbecausestandardGaussianrandomvectoris thecorrectnessofouranalysis.Second,inthelowerpanelofFig-
rotational-invariant[82],i.e.,𝑉gandgareidenticallydistributed. ure8,theorangehistogramrepresentstheempiricaldistribution
of⟨𝑃x¯,o⟩basedontheaforementioned105samples.Itshowsthat
| Wenotethatv1 |     | onlyhasitsfirstentrynon-zero.Thus,g−⟨g,v1 |     |     |     |     | ⟩v1 |     |     |     |     |     |     |     |     |
| ------------ | --- | ----------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
hasthefirstdimensionof0andhasitsremaining𝐷−1dimensions ⟨𝑃x¯,o⟩isindeedhighlyconcentratedarounditsmeanvalueandthe
tobeindependentstandardGaussianvariables.Afternormalization, empiricalmeanvaluematchesthetheoreticalexpectationperfectly,
theremaining𝐷−1dimensionsfollowtheuniformdistributionon whichverifiesourtheoreticalanalysis.
unitsphereinthe(𝐷−1)-dimensionalspaceandareindependentto
√︃
|                            |           |             |                 |                           | 2,0,...,0).Thus,⟨x¯,p2⟩= |                  |     | C                                                     | THEPROOFOFTHEOREM3.2 |     |     |     |     |     |     |
| -------------------------- | --------- | ----------- | --------------- | ------------------------- | ------------------------ | ---------------- | --- | ----------------------------------------------------- | -------------------- | --- | --- | --- | --- | --- | --- |
| p1 .Recallthatv2=(⟨p1,x¯⟩, |           |             |                 | 1−⟨p1,x¯⟩                 |                          |                  |     |                                                       |                      |     |     |     |     |     |     |
| √︃                         |           |             |                 |                           |                          |                  |     | Basedonthelemmaabove,weprovetheunbiasenessandtheerror |                      |     |     |     |     |     |     |
| 1−⟨p1,x¯⟩                  | 2         | ·𝑋1 where𝑋1 |                 | followsthedistributionof𝑝 |                          |                  | . □ |                                                       |                      |     |     |     |     |     |     |
|                            |           |             |                 |                           |                          |                  | 𝐷−1 | boundoftheestimator.                                  |                      |     |     |     |     |     |     |
| We                         | summarize |             | our conclusions |                           | about                    | the distribution | of  |                                                       |                      |     |     |     |     |     |     |
(⟨o¯,o⟩,⟨o¯,e1⟩)withthefollowinglemma. Proof. We first prove the unbiasedness. When and are
|     |     |     |     |     |     |     |     |     |     |     |     |     |     | o   | q   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
collinear,theunbiasednesscanbetriviallyverifiedbydefinition.
| Lemma | B.3     | (Distribution). |     | Let  | o and  | e1 be      | two unit vec- |                                                      |     |     |     |     |     |     |     |
| ----- | ------- | --------------- | --- | ---- | ------ | ---------- | ------------- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|       |         | ⊥               |     | 𝑃    |        |            |               | Whenoandqarenon-collinear,inordertoprovetheunbiased- |     |     |     |     |     |     |     |
| tors, | where o | e1.             | Let | be a | random | orthogonal | transfor-     |                                                      |     |     |     |     |     |     |     |
ness,itsufficestoprovethattheerrortermoftheestimatorin(12)
| mation | matrix, | C be | our constructed |     | deterministic |     | codebook and |                                  |     |     |     |     |     |                           |     |
| ------ | ------- | ---- | --------------- | --- | ------------- | --- | ------------ | -------------------------------- | --- | --- | --- | --- | --- | ------------------------- | --- |
|        |         |      |                 |     |               |     |              | equalsto0inexpectation.Lettinge1 |     |     |     |     | :=  | q − ⟨ q , o ⟩ o ,wededuce |     |
x¯ = argmax ⟨𝑃x,o⟩, o¯ = 𝑃x¯. Then the joint distribution of ,
|                                     |     | x∈C |          |          |     |          |      |       |                           |            |            |     | ∥q  | − ⟨ q o ⟩ o ∥ |     |
| ----------------------------------- | --- | --- | -------- | -------- | --- | -------- | ---- | ----- | ------------------------- | ---------- | ---------- | --- | --- | ------------- | --- |
| (⟨o¯,o⟩,⟨o¯,e1⟩)isidenticaltothatof |     |     |          |          |     |          |      |       | (cid:104)⟨o¯,e1⟩(cid:105) |            |            |     |     |               |     |
|                                     |     |     |          |          |     |          |      | fromE |                           | asfollows. |            |     |     |               |     |
|                                     |     |     | (cid:18) |          |     | (cid:19) |      |       | ⟨o¯,o⟩                    |            |            |     |     |               |     |
|                                     |     |     |          | √︃       | 2   |          |      |       |                           |            |            |     |     |               |     |
|                                     |     |     | ⟨o¯,o⟩,  | 1−⟨o¯,o⟩ | ·𝑋1 |          | (52) |       |                           |            |            |     |     |               |     |
|                                     |     |     |          |          |     |          |      |       | (cid:20)⟨o¯,e1⟩(cid:21)   |            | (cid:20)√︃ |     |     | (cid:21)      |     |
2
|                                     |     |     |     |     |                      |     |     |     | E   |        | =E         | 1−⟨o¯,o⟩ | ·𝑋1/⟨o¯,o⟩ |          | (55) |
| ----------------------------------- | --- | --- | --- | --- | -------------------- | --- | --- | --- | --- | ------ | ---------- | -------- | ---------- | -------- | ---- |
| where𝑋1isindependentto⟨o¯,o⟩and𝑋1∼𝑝 |     |     |     |     | 𝐷−1.Theexpectedvalue |     |     |     |     | ⟨o¯,o⟩ |            |          |            |          |      |
| of⟨o¯,o⟩is                          |     |     |     |     |                      |     |     |     |     |        | (cid:20)√︃ |          |            | (cid:21) |      |
2
|     |     |           |     |          |       |          |      |     |     |     | =E         | 1−⟨o¯,o⟩ | /⟨o¯,o⟩ | ·E[𝑋1]   | (56) |
| --- | --- | --------- | --- | -------- | ----- | -------- | ---- | --- | --- | --- | ---------- | -------- | ------- | -------- | ---- |
|     |     |           |     | √︂𝐷      | 2Γ( 𝐷 | )        |      |     |     |     |            |          |         |          |      |
|     |     | E[⟨o¯,o⟩] |     |          | 2     |          | (53) |     |     |     |            |          |         |          |      |
|     |     |           | =   | ·        |       |          |      |     |     |     | (cid:20)√︃ |          |         | (cid:21) |      |
|     |     |           |     | 𝜋 (𝐷−1)Γ |       | ( 𝐷 −1 ) |      |     |     |     |            |          | 2       |          |      |
|     |     |           |     |          |       | 2        |      |     |     |     | =E         | 1−⟨o¯,o⟩ | /⟨o¯,o⟩ | ·0=0     | (57) |
whereΓ(·)istheGammafunction.Itsconcentrationboundis
|     | (cid:26) |     |     |     | (cid:27) |     |     |     |     |     |     |     |     |     |     |
| --- | -------- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝑢 (cid:16) −𝑐𝑢2(cid:17) where(55)isbyLemmaB.3.(56)isduetotheindependencebetween
|     | P   | |⟨o¯,o⟩−E[⟨o¯,o⟩]| |     | > √ | ≤2exp |     | (54) |             |     |                                   |     |     |     |         |      |
| --- | --- | ------------------ | --- | --- | ----- | --- | ---- | ----------- | --- | --------------------------------- | --- | --- | --- | ------- | ---- |
|     |     |                    |     |     | 𝐷     |     |      | ⟨o¯,o⟩and𝑋1 |     | .(57)isbecausethedistributionof𝑋1 |     |     |     | (i.e.,𝑝 | )has |
𝐷−1
themeanof0.Finally,basedon(12),wefinishtheproofofthe
where𝑐inaconstant.
unbiasedness.
Wethenprovetheerrorbound.Whenoandqarecollinear,the
erroriszeroasisspecifiedbySection3.2.2.Weprovetheerror
boundforthenon-collinearcaseasfollows.
|     |     |     |     |     |     |     |     |     |  (cid:12)    |        | (cid:12) √︄        |            | 2        |     |      |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | ------ | ------------------ | ---------- | -------- | ------- | ---- |
|     |     |     |     |     |     |     |     |     | (cid:12) ⟨ o ¯ , | q⟩     | (cid:12)           | 1− ⟨ o¯    | , o ⟩    | 𝜖0      |      |
|     |     |     |     |     |     |     |     |     | P (cid:12)       | −⟨o,q⟩ | (cid:12) >         |            | · √      |         | (58) |
|     |     |     |     |     |     |     |     |     | (cid:12)⟨ o ¯ ,  | o ⟩    | (cid:12)           | ⟨o¯ ,      | ⟩ 2      | 𝐷 −1    |      |
|     |     |     |     |     |     |     |     |     |                |        |                    | o          |          |       |      |
|     |     |     |     |     |     |     |     |     |                 |        |                    |            |          |        |      |
|     |     |     |     |     |     |     |     |     |              |        | (cid:12) ⟩(cid:12) | √︄         |          | 2   |      |
|     |     |     |     |     |     |     |     |     | √︃               |        | ⟨ o¯ , e 1         | 1−         | ⟨ o¯ , o | ⟩ 𝜖0    |      |
|     |     |     |     |     |     |     |     |     | =P 1−⟨o,q⟩       |        | 2 (cid:12)         | (cid:12) > |          | · √     | (59) |
|     |     |     |     |     |     |     |     |     |                  |        | (cid:12) ⟨ , ⟩     | (cid:12)   | , 2      |         |      |
|     |     |     |     |     |     |     |     |     |                |        | (cid:12) o¯ o      | (cid:12)   | ⟨o¯ o ⟩  | 𝐷 −1  |      |
|     |     |     |     |     |     |     |     |     |                 |        |                    |            |          |        |      |
√︄
|     |     |                                 |     |     |     |     |     |     |  (cid:12) ⟨ o¯ , | e ⟩(cid:12)  | 1− ⟨ o¯  | , o ⟩ 2 | 𝜖0   |         |      |
| --- | --- | ------------------------------- | --- | --- | --- | --- | --- | --- | -------------------- | ------------ | -------- | ------- | -------- | ------- | ---- |
|     |     |                                 |     |     |     |     |     |     | ≤P (cid:12)          | 1 (cid:12) > |          |         |          |         | (60) |
|     |     |                                 |     |     |     |     |     |     | (cid:12)             | , (cid:12)   |          | 2 · √   |          |         |      |
|     |     |                                 |     |     |     |     |     |     |  (cid:12) ⟨ o¯     | o ⟩ (cid:12) | ⟨o¯ , o  | ⟩       | 𝐷 −1   |         |      |
|     |     |                                 |     |     |     |     |     |     |                     |              |          |         |         |         |      |
|     |     |                                 |     |     |     |     |     |     | √︄                   |              |          | √︄      |          |         |      |
|     |     |                                 |     |     |     |     |     |     |  1−              | ,            | 2        | 1−      | , 2      | 𝜖0  |      |
|     |     |                                 |     |     |     |     |     |     | =P                   | ⟨ o¯ o ⟩     |          |         | ⟨ o¯ o ⟩ |         | (61) |
|     |     |                                 |     |     |     |     |     |     |                      |              | ·|𝑋1|    | >       |          | · √     |      |
|     |     |                                 |     |     |     |     |     |     |                      | ⟨o¯ , o ⟩ 2  |          | ⟨o¯     | , o ⟩ 2  | 𝐷 −1    |      |
|     |     |                                 |     |     |     |     |     |     |                    |              |          |         |          |       |      |
|     |     |                                 |     |     |     |     |     |     |                     |              |          |         |          |        |      |
|     |     |                                 |     |     |     |     |     |     | (cid:26)             | 𝜖0           | (cid:27) |         |          |         |      |
|     |     | Figure8:VerificationofLemmaB.3. |     |     |     |     |     |     |                      |              | ≤2𝑒−𝑐0𝜖  | 2       |          |         |      |
|     |     |                                 |     |     |     |     |     |     | =P |𝑋1|              | > √          |          | 0       |          |         | (62) |
𝐷−1
WenextprovideempiricalverificationforthetheoreminFig-
ure8.First,intheupperpanelofFigure8,theorangehistogram
√︃
representstheempiricaldistributionof √⟨o¯,e1⟩ basedonthe105 where(59)isbyLemma3.1.(60)relaxes 1−⟨o,q⟩ 2to1.(61)is
|            |                                                    |                                                |     |     | 1−⟨o¯,o⟩2 |     |     | duetoLemmaB.3.(62)appliesLemmaB.1. |     |     |     |     |     |     | □   |
| ---------- | -------------------------------------------------- | ---------------------------------------------- | --- | --- | --------- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| samplesof𝑃 |                                                    | inSection3.2.1.Dueto(52),itfollowsthedistribu- |     |     |           |     |     |                                    |     |     |     |     |     |     |     |
| tionof𝑝    | 𝐷−1 .Theredcurveplotsthetheoreticaldensityfunction |                                                |     |     |           |     |     |                                    |     |     |     |     |     |     |     |

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
Table5:TheSummaryoftheAnalysisfor𝐵 𝑞.
Error Δ OverallError Target 𝐵
√ √ √ 𝑞
Trivial 𝑂( 𝐷·Δ) 𝑂(1/2𝐵𝑞) 𝑂( 𝐷/2𝐵𝑞) 𝑂(1/ 𝐷) Θ(log𝐷)
Ours 𝑂(Δ) 𝑂(
√︃log𝐷
/2𝐵𝑞) 𝑂(
√︃log𝐷
/2𝐵𝑞) 𝑂(1/
√
𝐷) Θ(loglog𝐷)
𝐷 𝐷
D THEANALYSISFOR𝐵 𝑞 Let𝑆 𝑛 =(cid:205)𝑛 𝑖=1 𝑋 𝑖.Then
Inthissection,weprovethat𝐵
𝑞
=Θ(loglog𝐷)sufficestoguaran-
(cid:18) 2𝑡2 (cid:19)
t
m
ee
uc
th
h
a
s
t
m
th
a
e
lle
e
r
rr
t
o
h
r
a
i
n
nt
t
r
h
o
e
d
e
u
r
c
r
e
o
d
r
b
o
y
ft
t
h
h
e
e
e
u
s
n
t
i
i
f
m
or
a
m
tor
sc
it
a
s
l
e
a
l
r
f,
q
i
u
.e
a
.
n
,
t
𝑂
iz
(
a
1
t
/
io
√
n
𝐷
i
)
s
.
P{|𝑆 𝑛−E[𝑆 𝑛]| ≥𝑡}≤2exp −
(cid:205)𝑛
𝑖=1
(𝑏
𝑖
−𝑎 𝑖)2
(64)
Weprovethestatementintwosteps.First,wewillprovethatthe √ √
Inourcase,wenotethat𝑎 𝑖 = −Δ/ 𝐷,𝑏 𝑖 = +Δ/ 𝐷.E[𝑆 𝑛] =
e S r e r c o ti r o i n nt D ro .1 du (r c e e c d al b l y th t a h t e Δ un = ifo ( r m m ax sc q a ′ l [ a 𝑖 r ]− qu m an in ti q z ′ a [ t 𝑖 i ] o ) n / i ( s 2𝐵 𝑂 𝑞 (Δ − ) 1 i ) n ). c E o (cid:2) n (cid:205) cl 𝑛 𝑖 u = s 1 i 𝑋 on 𝑖 (cid:3) . =(cid:205)𝑛 𝑖=1 E[𝑋 𝑖] =0.Itimmediatelyyieldsthefollowing
Specifically,recallthatweapproximatelycompute⟨x¯,q′⟩as⟨x¯,q¯⟩.
T
±
h
1/
en √
𝐷
the
an
e
d
rr
q¯
o
[
r
𝑖
e
]
q
−
ua
q
l
′
s
[𝑖
t
]
o
∈
|⟨x¯
[−
,q¯
Δ
−
,Δ
q
]
′
.
⟩
T
|.
h
N
en
ot
a
e
t
t
r
h
i
a
v
t
ia
x¯
lb
h
o
a
u
s
n
it
d
s
b
e
y
nt
t
r
h
ie
e
s
t
o
ri
f
-
P (cid:40)(cid:12) (cid:12) (cid:12)
(cid:12)
∑︁ 𝐷 x¯[𝑖]·(q¯[𝑖]−q′[𝑖]) (cid:12) (cid:12) (cid:12)
(cid:12)
≥𝑡 (cid:41) ≤2exp (cid:18) −
2
𝑡
Δ
2
2
(cid:19) (65)
angle’sinequalityyields|⟨x¯,q¯−q′⟩| ≤𝐷·√ 1 ·Δ=
√
𝐷·Δ.Wenote
(cid:12)𝑖=1 (cid:12)
thattheboundisweakbecauseitdoesnot 𝐷 considerthecancella- P (cid:40)(cid:12) (cid:12) (cid:12) ∑︁ 𝐷 x¯[𝑖]·(q¯[𝑖]−q′[𝑖]) (cid:12) (cid:12) (cid:12)≥Δ𝑢 (cid:41) ≤2exp (cid:18) − 𝑢2(cid:19) (66)
tionofunder-estimateandover-estimate.Wewillproveastronger (cid:12) (cid:12)𝑖=1 (cid:12) (cid:12) 2
probabilisticboundof𝑂(Δ) byconsideringtherandomizeduni-
where(66)isbyletting𝑢 = 𝑡/Δ.Theconclusionshowsthatthe
formscalarquantizationalgorithmpresentedinSection3.3.1and
errorisboundedby𝑂(Δ)withhighprobability.
quantitativelyanalyzingthecancellation.Second,wewillprove
thatΔ=𝑂( √︃lo 𝐷 g𝐷 /2𝐵𝑞)inSectionD.2.Recallthatq′ =𝑃−1 qisa D.2 TheAnalysisforΔ
randomvectorwhichfollowstheuniformdistributionontheunit
sphere.Atrivialboundgivesthat(maxq′[𝑖]−minq′[𝑖])=𝑂(1). Next we prove Δ = 𝑂( √︃lo
𝐷
g𝐷 /2𝐵𝑞) with high probability. Re-
Wenotethattheboundisweakbecauseitdoesnotconsiderthe callthatΔ=(max 1≤𝑖≤𝐷q′[𝑖]−min 1≤𝑖≤𝐷q′[𝑖])/(2𝐵𝑞 −1).Note
concentrationphenomenonoftheentriesofq′ (seeLemmaB.1). that max 1≤𝑖≤𝐷(q′[𝑖]) −min 1≤𝑖≤𝐷(q′[𝑖]) ≤ 2max 1≤𝑖≤𝐷|q′[𝑖]|.
Wewillproveastrongerprobabilisticboundbyquantitativelycon- Inordertoprovetheoriginalstatement,itsufficestoprovethat
sid
B
er
a
i
s
n
e
g
d
th
on
ec
t
o
h
n
e
c
t
e
w
n
o
tra
p
t
r
io
o
n
ba
p
b
h
il
e
i
n
st
o
ic
m
b
e
o
n
u
on
n
.
ds,wederivetheoverall
max 1≤𝑖≤𝐷|q′[𝑖]| = 𝑂( √︃lo
𝐷
g𝐷 ) withhighprobability,whichwe
proveasfollows.
errorbyapplyingtheunionbound.Theconclusionsaresumma-
√
𝐵
ri
𝑞
ze
=
d
Θ
in
(l
T
o
a
g
b
l
l
o
e
g
5
𝐷
.
)
M
.W
ak
e
in
n
g
o
t
t
h
e
e
th
o
a
v
t
e
b
ra
a
l
s
l
e
e
d
r
o
ro
n
r
t
b
h
e
e
𝑂
tr
(
iv
1
i
/
al
𝐷
bo
)
u
,
n
w
d
e
s,
h
i
a
t
v
i
e
s P

max |q′[𝑖]| ≥
√︄ log𝐷+𝑡
(67)
necessarytoset𝐵 𝑞 =Θ(log𝐷)toguaranteethesameerrorbound,  1≤𝑖≤𝐷 𝑐0𝐷 
whichisexponentiallyworsethanourresult.  
√︄
=P

∃1≤𝑖 ≤𝐷,|q′[𝑖]| ≥
log𝐷+𝑡
(68)
D.1 TheErrorofRandomizedUniformScalar

𝑐0𝐷

Quantization  
√︄
Asisdiscussedabove,theerrorintroducedbytheuniformscalar ≤𝐷·P

|q′[1]| ≥
log𝐷+𝑡
(69)
quantizationis  𝑐0𝐷 
 
(cid:12) (cid:12) (cid:10) x¯,q¯−q′(cid:11)(cid:12) (cid:12)=
(cid:12)
(cid:12) (cid:12) (cid:12) ∑︁
𝐷
x¯[𝑖]·(q¯[𝑖]−q′[𝑖])
(cid:12)
(cid:12) (cid:12) (cid:12) (63) ≤2exp
(cid:18)
−𝑐0·
log
𝑐
𝐷
0
+𝑡
+log𝐷
(cid:19)
=2exp(−𝑡) (70)
(cid:12)𝑖=1 (cid:12)
where(69)isbyunionbound.(70)isbyLemmaB.1.Theconclusion
Duetotherandomizeduniformscalarquantizationpresentedin
Section3.3.1,eachtermoftheerror,i.e.,x¯[𝑖]·(q¯[𝑖]−q′[𝑖]),isa showsthatΔ=𝑂(
√︃log𝐷
/2𝐵𝑞)withhighprobability.
𝐷
randomvariable.The𝐷randomvariablesareindependenttoeach
other.Eachtermhastheexpectedvalueof0(seeSection3.3.1)and E DISCUSSIONONTHENORMALIZATION
√ √
hastheirvaluesboundedby[−Δ/ 𝐷,+Δ/ 𝐷].Nowthequestionis
Wenotethatourcurrenttheoreticalanalysis(withoutanyassump-
toanalyzethesummationof𝐷suchrandomvariables.Wenotethat
tionsonthedata)providesanadditiveerrorboundlike[3].Let
theHoeffding’sinequalityimmediatelyanswersthequestion[82]. 𝑑𝑖𝑠𝑡′2 betheestimatedsquareddistancebasedonourestimator,
Werestatetheinequalityinthefollowinglemma. where𝑑𝑖𝑠𝑡′2 =∥o𝑟−c∥2+∥q𝑟−c∥2−2·∥o𝑟−c∥·∥q𝑟−c∥·
⟨
⟨
o
o
¯
¯
,
,
o
q⟩
⟩
.
Lemma D.1 (Hoeffding’s Ineqality [82]). Let𝑋1,...,𝑋 𝑛 be Consideringthatwedonotnormalizethedatasetwiththecentroids
independentrandomvariables,suchthat𝑋 𝑖 ∈ [𝑎 𝑖 ,𝑏 𝑖],∀1 ≤𝑖 ≤𝑛. butwiththeoriginofthespace,thenbasedontheEquation(15)in

RaBitQ:QuantizingHigh-Dim.VectorswithaTheoreticalErrorBoundforApproximateNearestNeighborSearch SIGMOD’24,June08–15,2024,Santiago,Chile
Theorem3.2,weimmediatelyhave sameasthenumberof0’s),indicatingthatnormalizingthedataset
withthecentroidsofIVFisempiricallyeffective.
|          |             |                |                      |     | (cid:18) 1 | (cid:19) |      |     |     |     |     |     |
| -------- | ----------- | -------------- | -------------------- | --- | ---------- | -------- | ---- | --- | --- | --- | --- | --- |
| (cid:12) | 𝑑𝑖𝑠𝑡′2 −∥o𝑟 | −q𝑟∥ 2(cid:12) | (cid:12)=∥o𝑟∥·∥q𝑟∥·𝑂 |     | √          | 𝑤.ℎ.𝑝.   | (71) |     |     |     |     |     |
(cid:12)
|     |     |     |     |     | 𝐷   |     |     | F   | DISCUSSIONONTHEABLATIONSTUDY |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- |
wherew.h.p.isshortfor“withhighprobability”.
WeemphasizethatRaBitQisamethodwithrigoroustheoretical
Whenthedatavectorsarewellnormalizedandspreadevenly
guarantee.Thenewlyproposedcodebookconstructionanddistance
on the unit hypersphere, we assume that the data vector after estimationareanintegralwhole.Theablationofanycomponent
−
| normalization,i.e.,o= |     |     | o 𝑟 c ,followstheuniformdistributionon |     |     |     |     |     |     |     |     |     |
| --------------------- | --- | --- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
∥ o 𝑟 − c∥ willcausethelossofthetheoreticalguarantee(i.e.,theperformance
theunithypersphere.Thenwecanderivethefollowingcorollary
isnomoretheoreticallypredictable)andfurtherdisabletheerror-
whichpresentsamultiplicativeerrorboundlike[41].
bound-basedre-rankingforANN(Section4).Wesummarizethe
dependencyofthetheoreticalconclusionsandefficientimplemen-
| CorollaryE.1. |     | Assumingthatofollowstheuniformdistribution |     |     |     |     |     |     |     |     |     |     |
| ------------- | --- | ------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
tationsonouralgorithmcomponentsindetailinFigure9.The
ontheunithypersphere.Wehave
2 q𝑟∥2(cid:12) green, blue and orange boxes represent the components in our
|     | (cid:12) | 𝑑𝑖𝑠𝑡′ − ∥o | 𝑟 − | (cid:18) | 1 (cid:19) |     |     |     |     |     |     |     |
| --- | -------- | ---------- | --- | -------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
(cid:12) (cid:12) =𝑂 √ 𝑤.ℎ.𝑝. (72) a lg o r it h m , t h e t h e o r et i ca l c o n c lu si o n s a n d t h e i m p le m e n ta t io n s
|     | (cid:12) |     | ∥2  | (cid:12) |     |     |     |     |     |     |     |     |
| --- | -------- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:12) ∥ o 𝑟 − q 𝑟 (cid:12) 𝐷 re sp e c t iv el y . A n a r r o w i n d ic a te s t ha t a p a r ti cu l ar c o m p o ne n t o r th e -
Proof. oreticalconclusionisusedforachievingthedownstreamconclusion
|     |                    |                   |                   |        |               |             |          | o r im | p le m e n ta t io n . | In a d d i t io n , w ew o u | l d a ls o li k e to hi | g h l ig h t th a t |
| --- | ------------------ | ----------------- | ----------------- | ------ | ------------- | ----------- | -------- | ------ | ---------------------- | ---------------------------- | ----------------------- | ------------------- |
|     | (cid:12) 𝑑𝑖𝑠𝑡′ 2 − | ∥q − o𝑟∥2(cid:12) | (cid:12) 2∥q𝑟     | − c ∥∥ | o −c∥(cid:12) | (cid:18) 1  | (cid:19) |        |                        |                              |                         |                     |
|     | (cid:12)           | 𝑟                 | (cid:12) (cid:12) |        | 𝑟             | (cid:12) ·𝑂 | (73)     |        |                        |                              |                         |                     |
(cid:12) ∥2 (cid:12) = (cid:12) ∥2 (cid:12) √ al th ou g h R a B it Q a c h ie v e s t h e a s ym pt o ti c o p t im a l ity in t e r m s o f th e
|     | (cid:12) ∥ q 𝑟 | − o 𝑟 | (cid:12) (cid:12) | ∥q 𝑟 − | o 𝑟 | (cid:12) 𝐷 |     |     |     |     |     |     |
| --- | -------------- | ----- | ----------------- | ------ | --- | ---------- | --- | --- | --- | --- | --- | --- |
worst-caseerrorbound,fordatasetswhichhavecertainpromising
|     | (cid:12) | 2 ∥ − | ∥ ∥ | − ∥ | (cid:12) | (cid:18) 1 | (cid:19) |     |     |     |     |     |
| --- | -------- | ----- | --- | --- | -------- | ---------- | -------- | --- | --- | --- | --- | --- |
(cid:12) q 𝑟 c o𝑟 c (cid:12) ·𝑂 (74) p r op e rt i e s ,i t i s s t i ll po s s ib l e t o o b ta i n b e t t e r e m p ir ic a l p e rf o r m a n c e
| =   | (cid:12) |     |     |     | (cid:12) | √   |     |     |     |     |     |     |
| --- | -------- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
(cid:12)∥q𝑟 −c∥2+ ∥ o 𝑟 − c ∥ 2 − 2 ⟨o 𝑟 −c,q𝑟 −c⟩ (cid:12) 𝐷 v i a fu r t h e r ( p o s s i b ly h e u r i st i c) o p ti m i z a t i o n . W e b e li e v e t h i si s a n
(cid:12) (cid:12) interestingresearchtopicandwewouldliketoleaveitasfuture
|           | (cid:12)          |                 |           | (cid:12)   |                     |     |      |       |     |     |     |     |
| --------- | ----------------- | --------------- | --------- | ---------- | ------------------- | --- | ---- | ----- | --- | --- | --- | --- |
|           | (cid:12)          | 1               |           | (cid:12)   | (cid:18) 1 (cid:19) |     |      |       |     |     |     |     |
| =(cid:12) |                   |                 |           | (cid:12)·𝑂 |                     |     | (75) | work. |     |     |     |     |
|           | (cid:12) (cid:16) |                 | ∥(cid:17) | (cid:12)   | √                   |     |      |       |     |     |     |     |
|           | (cid:12) 1 ∥ q𝑟 − | c ∥ + ∥ o 𝑟 − c | −⟨o,q⟩    | (cid:12)   | 𝐷                   |     |      |       |     |     |     |     |
(cid:12) 2 ∥ − ∥ ∥ − ∥ (cid:12) Randomized   Efficient Implementation
|     | o 𝑟      | c q𝑟 c            |          |                   |     |     |     |     | Normalization   | Bi-Valued Codebook  | (Index Phase)  |     |
| --- | -------- | ----------------- | -------- | ----------------- | --- | --- | --- | --- | --------------- | ------------------- | -------------- | --- |
|     | (cid:12) | (cid:12) (cid:18) | (cid:19) | (cid:18) (cid:19) |     |     |     |     | (Section 3.1.1) |                     |                |     |
(cid:12) 1 (cid:12) 1 1 (Section 3.1.2) (Section 3.1.2-3.1.3)
| ≤   | (cid:12)        | (cid:12) ·𝑂 √ | =𝑂  | √ 𝑤.ℎ.𝑝. |     |     | (76) |     |     |     |     |     |
| --- | --------------- | ------------- | --- | -------- | --- | --- | ---- | --- | --- | --- | --- | --- |
|     | (cid:12)1−⟨o,q⟩ | 𝐷             |     | 𝐷        |     |     |      |     |     |     |     |     |
(cid:12)
Efficient Implementation
where(73)isdueto(71).(74)isbyelementarylinearalgebra.(75) Concentration
|     |     |     |     |     |     |     |     |     |     | (Lemma B.1-B.3) | (Query Phase) |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | ------------- | --- |
simplifies(74).Thefirstinequalityof(76)isduetothenumericalin- (Section 3.3)
(cid:16) 1(cid:17)
| equalitythat |     | 𝑥+ ≥2,∀𝑥 | >0.Thesecondequalityof(76)holds |     |     |     |     |     |     |     |     |     |
| ------------ | --- | -------- | ------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
𝑥
becauseofollowstheuniformdistributionontheunithypersphere. Geometric Error-Bounded Re-Ranking Based on an
|                |     |            |               |     |            |        |       |     | Relationship  | Unbiased Estimator  | Error Bound  |     |
| -------------- | --- | ---------- | ------------- | --- | ---------- | ------ | ----- | --- | ------------- | ------------------- | ------------ | --- |
|                |     |            |               |     |            |        |       |     | (Lemma 3.1)   | (Theorem 3.2)       | (Section 4)  |     |
| In particular, |     | due to the | concentration |     | inequality | (Lemma | B.1), |     |               |                     |              |     |
⟨o,q⟩ishighlyconcentratedaround0,e.g.,ithassufficientlyhigh
probabilitytobeupperboundedby 1. □ Randomized Scalar Negligible Error of the
|     |     |     |     | 2   |     |     |     |     |     | Quantization  | Scalar Quantization  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- | -------------------- | --- |
Weemphasizethatthecorollaryisnotfullyrigorousasitde- (Section 3.3.1) (Theorem 3.3)
pendsontheassumptionthatofollowstheuniformdistribution Figure9:DependencyamongAlgorithmComponents,Theo-
ontheunithypersphere.Notethatallourothertheoreticalresults reticalConclusions,andEfficientImplementations
| donotrelyonanyassumptionsonthedata,i.e.,theadditivebound |     |     |     |     |     |     |     |     |     | .   |     |     |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
holdsregardlessofthedatadistribution.Inthepresentwork,we
Despitethattheablationisirrationalinviewoftheory,wepro-
onlyadoptasimpleandnaturalmethodofnormalization(i.e.,with
videseveralempiricalstudiestodiscusshoweachcomponentem-
the centroids of IVF) to instantiate our scheme of quantization, piricallyaffectstheperformance10.Weinvestigatetheeffectsof
whilewehaveyettoextensivelyexplorethenormalizationstep removing a certain component from RaBitQ while keeping the
| itself.Weshallleaveitasfutureworktothoroughlyandrigorously |     |     |     |     |     |     |     | others. |     |     |     |     |
| ---------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- |
studythenormalizationproblem.
Toverifytheeffectivenessofthecurrentmethodofnormaliza-
|     |     |     |     |     |     |     |     | F.1 | TheAblationoftheCodebookConstruction |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------ | --- | --- | --- |
tion,wemeasuretheempiricaluniformityofthenormalizeddata RecallthatinSection3.1,forquantizingasetofnormalizeddatavec-
vectorswiththeentropyofeachbitinourquantizationcodes9.
tors,weconstructaquantizationcodebookbyrandomlyrotating
Thelargertheentropyis,themoreuniformthenormalizeddataset
asetofbi-valuedvectors.Weconsiderreplacingourrandomized
is(andatthesametime,themoreinformativethequantization
codebookwithalearnedheuristiccodebookofPQwhilekeeping
codesare).Wereportthatonallthedatasets,theentropyisover
othercomponents.Wenotethatwithourrandomizedcodebook,
99.9%ofthelengthofthequantizationcodes(inotherword,for RaBitQhasrigoroustheoreticalguaranteeandachievesasymptotic
everybitinthequantizationcodes,thenumberof1’sisalmostthe
10Recallthattheerror-bound-basedre-rankingwouldbedisabledwhenanyofthe
9Inourquantizationcodes,let𝑝betheproportionof1’sinthe𝑖thbitofthewhole componentsisablated.UsingitforANNentailsexhaustivetuningoftheparameters
dataset.Thentheentropyofthe𝑖thbitequalsto−[𝑝log 2(𝑝)+(1−𝑝)log 2(1−𝑝)]. ofre-ranking,whichwouldheavilyaffecttheresultsofANNsearch.Thus,theresults
Wereportthesummationoftheentropyoverallthebits.Theresultisnormalizedby ofANNwouldbelessinsightfulforanablationstudy.Weonlyreporttheresultsof
| thelengthofthequantizationcodesfortheeaseofstudy. |     |     |     |     |     |     |     | distanceestimation. |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | --- | --- | --- |

SIGMOD’24,June08–15,2024,Santiago,Chile JianyangGaoandChengLong
IVF-OPQx4fs ( D bits, w/o re-ranking) IVF-OPQx4fs (2D bits, w/o re-ranking) IVF-RaBitQ (w/o re-ranking) IVF-RaBitQ (with re-ranking)
|     |     |     | Image |     |     | GIST |     |     |     | MSong |     |
| --- | --- | --- | ----- | --- | --- | ---- | --- | --- | --- | ----- | --- |
6×
|     | 810× 4 |     |     |     | 2×      |     |     |        |     |     |     |
| --- | ------ | --- | --- | --- | ------- | --- | --- | ------ | --- | --- | --- |
|     | 6×     |     |     |     |         |     |     | 4×     |     |     |     |
|     | SPQ 4× |     |     |     | SPQ 103 |     |     | SPQ 2× |     |     |     |
8×
|     | 2×     |      |           |     | 6×  |           |        |     |      |           |     |
| --- | ------ | ---- | --------- | --- | --- | --------- | ------ | --- | ---- | --------- | --- |
|     |        |      |           |     | 4×  |           |        | 103 |      |           |     |
|     | 810× 3 |      |           |     |     |           |        | 8×  |      |           |     |
|     | 6×     |      |           |     |     |           |        | 6×  |      |           |     |
|     | 4×     |      |           |     | 2×  |           |        | 4×  |      |           |     |
|     |        | 0 20 | 40 60 80  | 100 | 0   | 20 40 60  | 80 100 |     | 0 20 | 40 60 80  | 100 |
|     |        |      | Recall(%) |     |     | Recall(%) |        |     |      | Recall(%) |     |
|     |        |      | SIFT      |     |     | DEEP      |        |     |      | Word2Vec  |     |
8×
|     | 2×     |     |     |     | 104 |     |     | 6×     |     |     |     |
| --- | ------ | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- |
|     |        |     |     |     | 8×  |     |     | 4×     |     |     |     |
|     | 104    |     |     |     | 6×  |     |     |        |     |     |     |
|     | 8×     |     |     |     | 4×  |     |     |        |     |     |     |
|     | SPQ 6× |     |     |     | SPQ |     |     | SPQ 2× |     |     |     |
4×
|     |     |     |     |     | 2×  |     |     | 8× 103 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- |
6×
|     | 2×  |     |     |     | 103 |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |     |     | 8×  |     |     | 4×  |     |     |     |
103
|     |     | 0 20 | 40 60 80  | 100 | 0   | 20 40 60  | 80 100 |     | 0 20 | 40 60 80  | 100 |
| --- | --- | ---- | --------- | --- | --- | --------- | ------ | --- | ---- | --------- | --- |
|     |     |      | Recall(%) |     |     | Recall(%) |        |     |      | Recall(%) |     |
Figure10:Time-AccuracyTrade-OffforANNSearch(withandw/ore-ranking).
optimality.However,withalearnedheuristiccodebook,theper- ⟨o¯,q⟩isbiasedbyaratioofaround0.8.Table7furtherpresentsthe
formanceofthemethodwillbenomoretheoreticallypredictable. averagerelativeerrorandmaximumrelativeerroroftheestimated
Thoughitisoftenintuitivetoexpectthatreplacingarandomized distancesontheGISTdataset.Itclearlyshowsthattaking⟨o¯,q⟩as
algorithmwithalearnedalgorithmmayimprovetheperformance, theestimatordegradesboththegeneralqualityandtherobustness
inRaBitQ,whosedesignisanintegralwhole,alearnedcodebook ofthedistanceestimation.Moreover,wenotethatbasedonthe
couldbelesssuitablethanarandomizedcodebook.Table6presents estimator⟨o¯,q⟩,theoriginaltheoreticalerrorbound(Theorem3.2)
theaveragerelativeerrorandmaximumrelativeerroroftheab- doesnotholdanymore.Thus,itisinapplicablefortheerror-bound-
lationstudyontheGISTdataset.Itclearlyshowsthatreplacinga basedre-rankingforin-memoryANNsearch(Section4).
randomizedcodebookwithalearnedonedegradesboththegen-
eralqualityandtherobustnessofdistanceestimation.Theresults
implythatdespitethatPQ,asalearning-basedmethod,hasalarge
searchspaceofcodebooks,theheuristiclearningprocess(which
isbasedonaheuristicobjectivefunctionandanapproximateop-
timizationalgorithm)onlyfindsasuboptimalsolutionamongthe
searchspace.Similarfindingscanbeobservedinthemainexper-
iments(Section5.2.1),i.e.,LSQhasitssearchspaceofcodebooks
evenlargerthanPQ,yetithasworseperformanceinmostcases.
Table6:AblationStudyoftheCodebookConstruction(GIST).
|     | Ave.Rel.Error(%) |     | Max.Rel.Error(%) |     |     |     |     |     |     |     |     |
| --- | ---------------- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Rand.Codebook 1.675 13.043 Figure11:AblationStudyoftheEstimator.Theredpoints
| LearnedCodebook |     | 3.049 |     | 34.375 |     |                                        |     |     |     |     | ⟨o¯,q⟩          |
| --------------- | --- | ----- | --- | ------ | --- | -------------------------------------- | --- | --- | --- | --- | --------------- |
|                 |     |       |     |        |     | representtheresultsbasedontheestimator |     |     |     |     | ⟨o¯,o⟩ .Theblue |
pointsrepresenttheresultsbasedontheestimator⟨o¯,q⟩.
F.2 TheAblationoftheEstimator
Table7:AblationStudyoftheEstimator(GIST).
RecallthatasisdiscussedinSection3.2,unlikePQwhichsimply
|     |     |     |     |     |     |     |     | Ave.Rel.Error(%) |     | Max.Rel.Error(%) |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ---------------- | --- |
treatsthequantizeddatavectorasthedatavector,ourmethod ⟨o¯,q⟩ 1.675 13.043
⟨o¯,o⟩
explicitlyanalyzesthegeometricrelationshipbetweenthevectors
|     |     |     |     |     |     |     | ⟨o¯,q⟩ |     | 2.196 |     | 52.400 |
| --- | --- | --- | --- | --- | --- | --- | ------ | --- | ----- | --- | ------ |
andconstructsanunbiasedestimatoraccordingly.Inthispart,we
ablateourestimatorandadoptanalternativeestimator⟨o¯,q⟩by
treatingthequantizeddatavectorasthedatavectorasPQdoes. F.3 TheAblationoftheRe-Ranking
Inparticular,wecollect107pairsoftheestimatedinnerproducts AsisdiscussedinSection4,despitethatRaBitQprovidestheguar-
andthetrueinnerproductsfromthefirst10queryvectorsandthe anteeonthedistanceestimation,whenthedistances(tothequery)
106datavectorsoftheGISTdataset.Figure11showsthescatter oftwodifferentdatavectorsareextremelyclosetoeachother,the
plotsofthetrueinnerproductandtheestimatedinnerproduct. guaranteedaccuracymightbeinsufficientforrankingthemcor-
Theredpointsrepresenttheresultsbasedourunbiasedestimator rectly.Re-ranking,inthiscase,isnecessaryforproducinghigh
⟨o¯,q⟩.Thebluepointsrepresenttheresultsbasedontheestimator recall.Figure10plotsthe“QPS”-“recall”curvesofRaBitQwithand
⟨o¯,o⟩ withoutre-ranking.Itshowsthatre-rankingisindeednecessary
⟨o¯,q⟩.Wefitthetwosetofpointswithlinearregression.Theresults
forachievingtherobustperformanceofANNsearch.
clearlyshowthatourestimatorisunbiasedwhiletheestimator