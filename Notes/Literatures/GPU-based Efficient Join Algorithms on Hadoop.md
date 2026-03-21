| GPU-based |         | Efficient |        | Join      | Algorithms     |       | on            | Hadoop |     |
| --------- | ------- | --------- | ------ | --------- | -------------- | ----- | ------------- | ------ | --- |
|           | Hongzhi | Wang,     | Ning   | Li        | , Zheng        | Wang, | Jianing       | Li     |     |
|           | P.O.Box | 750,      | Harbin | Institute | of Technology, |       | Harbin, China |        |     |
9102 rpA 52  ]BD.sc[  1v10211.4091:viXra
Abstract
Thegrowingdatahasbroughttremendouspressureforqueryprocessingand
storage, so there are many studies that focus on using GPU to accelerate join
operation, which is one of the most important operations in modern database
systems. However, existing GPU acceleration join operation researches are not
| very suitable | for the | join | operation | on  | big data. |     |     |     |     |
| ------------- | ------- | ---- | --------- | --- | --------- | --- | --- | --- | --- |
Basedonthis,thispaperspeedsupnestedloopjoin,hashjoinandthetajoin,
combining Hadoop with GPU, which is also the first to use GPU to accelerate
theta join. At the same time, after the data pre-filtering and pre-processing,
using Map-Reduce and HDFS in Hadoop proposed in this paper, the larger
data table can be handled, compared to existing GPU acceleration methods.
Also with Map-Reduce in Hadoop, the algorithm proposed in this paper can
estimate the number of results more accurately and allocate the appropriate
| storage space | without              | unnecessary |      | costs, | making       | it more | efficient. |            |        |
| ------------- | -------------------- | ----------- | ---- | ------ | ------------ | ------- | ---------- | ---------- | ------ |
| The           | rigorous experiments |             | show | that   | the proposed |         | method     | can obtain | 1.5 to |
2 times the speedup, compared to the traditional GPU acceleration equi join
algorithm. And in the synthetic data set, the GPU version of the proposed
| method | can get 1.3 | to 2 times |     | the speedup, | compared |     | to CPU | version. |     |
| ------ | ----------- | ---------- | --- | ------------ | -------- | --- | ------ | -------- | --- |
1. Introduction
| One | of the most | serious | problems |     | in the | computer | industry | today | is the |
| --- | ----------- | ------- | -------- | --- | ------ | -------- | -------- | ----- | ------ |
growing data. According to statistics, the rate at which data is generated an-
nually on the network will increase by 10 percent every five years[1]. Therefore,
we have to face how to effectively deal with this serious problem in large re-
lational databases. However, the speed of the processor has now grown to the
limits of the current level of technology, more and more attention focused on
parallel technology. One solution is to increase the number of processors[2] and
threads[3]. Another solution is using a single instruction multiple data stream
(SIMD) structure to improve the parallelism by processing multiple data under
one instruction[4].
| Now, | due to CPU | clock | frequency |     | limitations, |     | software | optimization | has |
| ---- | ---------- | ----- | --------- | --- | ------------ | --- | -------- | ------------ | --- |
come to an end. Therefore, researchers have to consider other possibilities to
speed up the query processing[5], using multicore CPUs[6]. The use of new
hardware to speed up the process is also possible[7]. In recent years, many
| Preprint submitted | to  | Elsevier |     |     |     |     |     | April | 26, 2019 |
| ------------------ | --- | -------- | --- | --- | --- | --- | --- | ----- | -------- |

studieshavechosenFPGAasanoptionforhardwareaccelerators[8,9],including
the query[10]. Similarly, image processors (GPU) have been widely used in the
field of query processing[11].
Joinoperationisoneofthemostimportantoperationsinrelationaldatabase
operationsandoneofthelongest-runningoperationsinaquery. Underthissit-
uation, there are many efforts put to speed up the join operation. IBM has
added new hardware to its commercial system Netezza[12]. Do[13] integrated
CPU processors and DRAM memory into a smart flash device (Smart SSD) to
implement query processing. Devarajan[14] and others believe that the GPU is
the most advanced distributed tool to handle computationally intensive tasks.
Kaldewey[15] and others believed the data needs to be copied to the GPU de-
vice memory for processing. He[16] thought using GPU to query co-processing
was an effective way to improve memory database performance. Yuan[17] used
the GPU device to implement the hash join operation. Pietron[18] and others
used the CUDA programming model on the GPU to achieve a part of SQL
operations. Rui[19] has conducted detailed experimental studies on how join
operation benefits from the rapid growth of the GPU. Angstadt[20] even devel-
opedadedicatedtospeeduptheSQLstatementusingtheCUDAprogramming
model on the GPU. In addition to the two-table join, multi-table join equally
occupies a very important position in the relational database, Zhou[21], who
proposedGBFSJ(GPUsBloomFilterStarJoin)algorithm, achievedastarjoin
on the GPU with the use of a Bloom filter. Cruz[22] and others have used the
GPU to achieve such connectivity.
Through the analysis of the existing research results of the new hardware
acceleration join, it is concluded that the research results have the following
problems:
• Existing join operations based on new hardware are still at the initial
stage, most are limited to simple equi join, or lack of research on complex
joinoperationsuchasthetajoin. Futureresearchworkshouldfocusmore
on complex join operation for practical applications.
• The existing research carried out by the experiment are based on small
data sets, the size of the data set mostly is MB. To use GPU in com-
mercial database systems, future research efforts should be put on scaling
operations on large-scale data.
• A serious problem with the new hardware acceleration join operation is
how to allocate the appropriate storage space for the join results. Differ-
ent from the CPU programming language, dynamically allocating storage
space, GPU needs to allocate enough storage space in advance. However,
the existing research results are not good solutions to this problem.
• Asinglenewhardwarecannotmeettheneedsofmodernbusinessdatabases,
but existing research is carried out on monolithic new hardware. There
should be more work on deploying new hardware as a distributed archi-
tecture to accelerate join operation.
2

This paper is mainly based on the distributed architecture of the GPU to
accelerate the join operation. By combining the Hadoop architecture with the
GPU, advantages of both Hadoop’s node-level parallelism and GPU’s thread-
level parallelism can be taken. Hadoop data processing tasks originally per-
formed by the CPU were sent to the GPU, using the GPU’s parallelism while
opening multiple threads to take advantage of the high computational power
and high parallelism. This paper intends to implement nested loop join, hash
join and theta join algorithm, the remaining types of join will be studied later.
The second section mainly introduces the basic hardware structure, the
thread organization form and the CUDA programming language background,
to better understand the following GPU processing join algorithm. The third
section and the fourth section mainly introduce the main research contents of
thispaper,includingpre-filteringofdataandhardwareprocessingequijoinand
non-equi join operation. The fifth section introduces the experiment and the
results obtained in this paper. The last part concludes the paper, summarizes
the contents and points out the innovation.
2. Preliminary
2.1. GPU
The GPU device has a multiparty processor core with multiple instruction
streamsandmultiplestreams(SIMDs),andeachmultiprocessorcorecontainsa
numberofprocessors. TheGPUhardwarestructureshowninFigure1contains
N multiprocessor cores, and each multiprocessor core contains M processors.
Each multiprocessor core contains an instruction processing unit and a storage
resource. Allprocessorsonthemultiprocessorsharetheinstructionunitandthe
storage space, and each processor has a set of registers. GPU devices also have
global memory, and global memory can be accessed by all multiprocessor cores.
Multi-processor core internal storage resources read and write faster, compared
to the global memory.
As shown in Figure 2, in a thread block, the organization of the thread can
beone-dimensional,two-dimensionalandthree-dimensional,withIDidentifying
each thread. Similarly, the organization of thread blocks in a thread grid can
also be divided into one-dimensional, two-dimensional, and three-dimensional.
GPU threads have a variety of organizational forms, making it applicable to
different issues. For example, when dealing with array problems, the thread
grid and the thread block can be used in the one-dimensional organization, and
each thread corresponds to a part of the array elements.
2.2. CUDA
GPU devices slowly evolved into a copier processor for intensive computa-
tion, bringing a variety of programming languages into birth, such as CUDA.
CUDA can be implemented in both CPU and GPU. Additionally, CUDA adds
some content related to GPU devices, such as the use of rich thread resources
on the GPU.
3

哈尔滨工业大学工学硕士学位论文
多的线程，同时线程的创建开销也要远远低于 CPU。GPU 上的线程以线程格、
线程块的形式进行组织。线程是最小的处理单元，若干个线程被组织成线程块，
同时若干个线程块又被组织成线程格。对于任何问题，可将其粗粒度地划分成
若干个子问题，每个线程块可处理其中一个子问题。进一步，把每个子问题划
分成更小的子问题，这些细粒度子问题由 GPU的基本处理单元线程进行处理。
线程块是每个多处理器核的基本调度单位，一个线程块内的全部线程均在相同
的核心里，并且共享相同的资源。在 GPU工作时，每个多处理器核对应一个线
程块，每个处理器对应一个线程。由于多处理器核中的存储资源十分有限，因
此每个线程的状态信息都是保存在寄存器中的，每个线程块中的线程个数越多，
所需要的寄存器个数越多。实际中，线程块的个数可能超过了 GPU设备多处理
器核的个数，通常多处理器核以线程块为基本单位，流水式的进行处理。因此，
GPU核的个数越多，能够同时处理的线程块个数越多，执行效率越高。
GPU
Multi-Professor N
Multi-Professor 2
Multi-Professor 1 Instruction
Unit
Professor 1 Professor M
Cache
Global Memory
图2-1 GPU结构
Figure1: StructureofGPU
如图 2-2 所示，在一个线程块中，线程的组织形式可以是一维、二维以及
CUDA contains two kinds of code, host code, and kernel code. Host code
三维。在一维的组织形式中，线程 ID是一个数字；在二维中，线程 ID是一个
runsontheCPU,whichisresponsiblefortheapplyingforstoragespace,calling
二th维e k坐er标n（el xco，dye）,，c分on别tro代lli表ng该d线ata程t在ra横nsf、o纵rm轴at上ion的b标et号we；en同C理P三U维an组d织GP形U式. T中h，e
kernel code is the code that runs in parallel on the GPU.
- 15 -
2.3. Join Operation
In the relational database, the join operation is the process of the combi-
nation of two tables into a relationship table under specific conditions. The
attributes that participate in the relationship table are called join keys. If the
joinkeysatisfiesthequerycondition,thecorrespondingtuplesintwotablesare
merged into one tuple and stored in the buffer.
According to the different join conditions, the join operation can be divided
into equi join and theta join:
• Equijoin: Thequerystatementspecifiesthejoinconditionfortheconnec-
tion of the equation. Consider the relationships R(A,B), S(C,D). When
R.A = S.C, it is an equi join. Figure 3 shows the result of the join. In
SQL, the syntax of this join is:
select A,B,C,D from R join S on R.A=S.C
• Theta join: The query statement specifies the join condition for the con-
nection of the non-equation. Non-equation includes >,<,≥,≤ and so on.
Figure 4 shows the result of the join. In SQL, the syntax of this join is:
4

哈尔滨工业大学工学硕士学位论文
线程ID为三维坐标（x，y，z），分别代表其在横、纵、竖坐标上的标号。每个
线程块内部的线程均有一套独立编号。与线程一样，在一个线程格中线程块的
组织形式同样可以分为一维、二维以及三维，每个线程块同样具有标识其的 ID。
GPU中线程多样的组织形式，使得其能适用于不同的问题。例如，当处理数组
问题时，线程格以及线程块可以采用一维的组织形式，每一个线程均对应数组
中的一部分元素。当处理矩阵问题时，线程格与线程块采用二维组织形式更加
适合。
GPU Device
Grid
Block Block
(0,0) (0,1)
Block Block
(1,0) (1,1)
Threads
(0,0,0) (1,0,0)
(0,1,0) (1,1,0)
F图igu2-r2e G2:POUr线ga程niz组at织ion形o式fG PUthreads
select A,B,C,D from R join S on R.A<S.C
2.3 CUDA
The join operation can be roughly divided into the following three categories:
GP•UN作e为ste一d种loo硬p件jo处in:理I器t i，s a开v发io者len为t其alg研or发ith了m多th种at编c程on语ve言rts。aGllPtUup设le计s i之n one
table to all tuples in the other table, and generates a new result tuple if
初目标是为了进行图像处理，因此研发了多种专门开发图像处理的编程语言，
the join condition is met.
例如 OpenGL、DirectX 等。随着 GPU 设备的发展，慢慢地其演变成了处理密
• Hash join: It is to put the smaller table (inner table) into a hash table
集计算的协处理器，基于此出现了多种通用编程语言，例如 CUDA语言。CUDA
and store it in memory. And then traverse the larger table (outer table)
作为一种通to用fin编d程th语e t言up，le与ofJathvea等ou语ter言t类ab似le，in适th用e 于ha多sh种ta领bl域e.，不仅仅是专门
• Sort merge join: It is to sort two tables at first, and then traverse them
- 16 -
in sequence to decide whether to join.
2.4. Hadoop
Hadoop is an open source software framework, which is used for distributed
storage and big data processing. The core of this framework is the Hadoop
Distributed File System (HDFS) and Map-Reduce.
HDFS,writteninJavafortheHadoopframework,isadistributedfilesystem
that can store data on commodity machines, providing high bandwidth across
the cluster.
5

哈尔滨工业大学工学硕士学位论文
1.2.1连接操作的分类
关系型数据库中，连接操作即是将两个表根据特定的条件合并成一个关系
表的过程。关系表中参与比较的属性称之为连接键，待连接的关系表的连接键
必须是可以进行比较的，如必须同为数值型或者同为字符型。若待连接关系表
的元组连接键满足查询语句指定条件，则将两个表中相对应元组合并成一个元
组并存入结果缓冲区中；否则，继续进行匹配。
根据连接条件的不同，连接操作可以分为等值连接以及非等值连接两大类：
（1）等值连接查询语句指定的连接条件为等式的连接操作，即为等值连接。考
虑如下两个关系：
R(cid:3435)A,B(cid:3439),S(C,D)
当连接条件为R.a=S.c时，即是一个等值连接。如图1-1所示，此连接的结果
为关系R与关系S中所有满足条件R.a=S.c的元组对所合并成的新元组组成的
集合。在SQL语句中，等值连接语法如下：
SELECT A,B,C,D FROMR JOIN S ON R.A=S. （1-1）
R S
A B C D R.A S.C R.B S.D
x 1 y 4 R.A=S.C y y 2 4
y 2 z 5 z z 3 5
z 3 t 6
图1-1等值连接
Figure3: Exampleofequijoin
哈尔滨工业大学工学硕士学位论文
（2）非等值连接查询语句指定的连接条件为不等式的连接操作，称之为非等值
R S
连接，如图 1-2 所示。非等值连接的连接条件包括>、<、<>、>=、<=，SQL
A B C D
语法如下： R.A S.C R.B S.D
1 x 1 o R.A<S.C
SELECT A,B,C,D FROMR JOIN S ON R.A<S.C; 1 3 x （1- 2q）
2 连 接 y操 作 的 1实 现 方 p式 大 致可以分为以下三类：
2 3 y q
（ 31 ）嵌 套z 循环 连3 接 嵌 q套 循环连接是一种暴力算法，即将待连接的两表中任意
一个表的所有元组一一去与另一个表中的全部元组进行比较，若符合连接条件
F ig u re 图4:1E-2x非am等p值le连o接ft hetajoin
则生成新的结果元组。显然，这种方法并不适用于尺寸较大的关系表连接。
（2）散列连接 大数据集上的连接通常采用散列连接，其核心思想是将较小的
Map -Reduceisadistributedcomputingframeworktohandlebigdata(greater
表（内表）建立成一个哈希表，并将其存放进内存中。接着遍历较大的表（外
than 1TB), including Map and Reduce. In the Map phase, the data is read in
units of表 l）in，e将s外a表nd的c每on个v元er组te分d别to探k测e内y存−中- v3 a-的 lu哈e希p表ai，rs若.探In测成th功e则R将ed两uc个e元p组ha合se, pairs
withth并e成sa新m的ek元e组y；va否lu则e，ar继e续pa遍ss历ed外t表o。th哈e希sa函m数e需R作ed用u在ce连fu接n键ct上io，n,并a且nd外t表heresult
is finall和y内re表tu需rn要ed使[2用3相, 2同4的, 2哈5希, 2函6数, 2。7]注. 意，若内存容量小于哈希表大小，则须对
Usin内g表M以a及p-外R表ed按u照ce另to外h的a哈nd希le函j数oi进n行op分e割ra，tio对n两s表is的th对e应cu块r分re别nt做m连a接in，st最ream ap-
proach,后r合ou并gh结ly果d。iv注id意e，d散in列to连t接hr只ee能w处a理ys等, j值oi连n接in。R educe, join in Map, and semi
join.
（3）排序合并连接 排序合并连接的核心思想是先对待连接的两个关系表进行
排序，接着按顺序遍历两个表，进行连接判断。由于排序合并连接需要对关系
3. GP表U进-B行a排se序d，E因q此u通i J常o情in况w下i效th率要H比ad散o列o连p接差。但现代关系数据库的关系
表通常都已经排好序，这时排序合并连接的效率会高于散列连接。
In the join algorithm above, only a small part of the data in two tables
上述三种实现方式中，散列连接只能适用于等值连接，而嵌套循环连接以
participates in the equi join operation. Therefore, initial pre-filtering in CPU,
及排序合并连接适用于等值连接以及非等值连接。嵌套循环连接由于采用暴力
passingfewerdatabetweenhosts,willbeagoodsolutiontothisproblem. Based
方法，因此仅仅适用于小数据集的情况。通常情况下，散列连接性能优于排序
on this, this section mainly introduces GPU to accelerate nested loop join and
合并连接；但若数据源已经排好序，则采用排序合并连接更优。
hash join, along with the pre-filtering through Hadoop to reduce the amount of
data tra1.n2s.f2e Mrreadp-Rbeetdwuceeen实d现ev连ic接es.操作
3.1. Da ta PMraep--fiRletdeurcien是g tGhoroogulegh公H司a所d开oo发p的一种分布式计算框架，主要用来处理
In s大em数i据j（oin大,于on1TlyB）tu的p运les算o。fMtahpe-Rleadrugcee的gr核ou心p思a想re来fi源lt于er函ed数,式b语y言ex，tr主a要cting the
join key包o括f tMhaeps以m及alRletdaubcele两. 个W阶h段en。t在woMlaapr阶ge段t，ab以le行s为ar单e位co读nn取e数ct据ed并,将fil其te转ring only
the larg换er成okneeys-viasluneo键t值su对ffi的ci形en式t；to在aRchediuecvee阶th段e，g具re有at相es同t pkeeyrf值or的m键an值c对e b经o过ost. The
pre-filte哈r希m操en作ti传on递e到d相in同t的hisRepdaucpee函r 数ex中tr，acRtesduccoem函m数o对n这jo些in具k有ey相s同ofketyw值o的tables to
pre-filte键r值bo对t进h行ta处bl理es，. 最So后, e将v结en果i汇f t总w返o回ta。bl es are very large, it can still achieve a
good performance. This pre-filtering needs two rounds of Map-Reduce through
尽管 Map-Reduce 模型更加适用于单源数据处理，而连接操作涉及到至少
Hadoop, the following is a specific implementation process.
两个关系表，属于多源数据。但利用 Map-Reduce 处理连接操作依然是目前的
In the Map phase of the first round of Map-Reduce, firstly read the data
of two tables to extract those to be c-o 4n - nected attributes, and add a label to
6

indicatewhichtabletheyarefrom. Specifically, Map’soutputis(key,tag), and
key isthevalueoftobeconnectedattribute. Whentag isT,itmeansthetuple
is from the table T, the same to those with S. Each tuple corresponds to such a
key−valuepair. Pairswiththesamekey aretransportedtothesameReducer
after shuffling, sorting, merging, and so on. In the Reduce phase, the received
(key,value ist) are analyzed. Only those value ist contains both T and S key
|     | l   |     | l   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
value will be outputted as the result to HDFS in Hadoop. All in all, the first
roundMap-Reduce’soutputisthevalueofjoinkeyattributeinthefinalresult.
Thatis,thetupleswhosevalueofjoinkeyattributearenotinitwillnotappear
| in the final  | result. |                   |       |            |      |              |
| ------------- | ------- | ----------------- | ----- | ---------- | ---- | ------------ |
| In the second | round   | of the Map-Reduce | task, | the result | from | the previous |
round is read from the HDFS firstly in the initialization function Setup() and
stored in a hash table. Then in the Map phase, read tuples of two to be joined
original table, and extract the join key. If the join key exists in the hash table,
the tuple is shown in the final result, it is outputted with a tag that identifies
its origin. In this step, only those tuples that are determined to be in the final
result will be outputted to Reduce to participate in the final operation. In this
way, the amount of data to be processed in Reduce declines greatly. At the
same time, it reduces the number of tuples that need to be stored on the GPU,
| freeing up | device memory. |                  |          |         |       |                |
| ---------- | -------------- | ---------------- | -------- | ------- | ----- | -------------- |
| In semi    | join, the raw  | data is inputted | directly | to HDFS | after | filtering, and |
then a new Map-Reduce is restarted to read and operate the filtered data.
However, it will lead to additional Map-Reduce startup time and additional
expense of both output and extraction in the new round. Therefore, the pre-
filtering method used in this paper incorporates the filtering of data and the
execution of the actual join operation into one round of tasks. That is, after
filtering,mappingandtagginginMap,dataistransferredtoReduceforjoining,
by shuffling, sorting, merging and other steps. In the Reduce phase, the data
from Map is received and processed (row and column transformation), and the
processed data is then sent to the GPU for specific join operations. After the
GPU is executed, the result is returned to the CPU, and the Reduce outputs it
| to HDFS. The | pseudo code          | is shown       | in Algorithm   | 1.  |             |            |
| ------------ | -------------------- | -------------- | -------------- | --- | ----------- | ---------- |
| 3.2. Data    | Preprocessing        | through Hadoop |                |     |             |            |
| Before       | reading the filtered | data           | and performing | the | actual join | operation, |
Reduce of Map-Reduce in Hadoop needs to perform some preprocessing of the
data. The main processing steps include mapping and row and column trans-
formation. This section describes these two operations and the effects they
bring.
3.2.1. Mapping
| For a SQL | query, only | a few attributes | in the | relational | table | will be used, |
| --------- | ----------- | ---------------- | ------ | ---------- | ----- | ------------- |
and most of them will lead to additional overhead. Therefore, analyzing SQL
statement to determine which attributes are query-related will enhance the ef-
ficiency. Existing big data query tools, such as HIVE, IMPALA, all follow a
7

|     |     | Algorithm1: | Pre-filteringAlgorithm |     |     |
| --- | --- | ----------- | ---------------------- | --- | --- |
1: Map1(null,tuple):
2:
joinkey←extractthejoinkeyfromtuple;
3: emit(joinkey,tag);
| 4: Reduce1(key,tag | list): |     |     |     |     |
| ------------------ | ------ | --- | --- | --- | --- |
5: uniquekey←thekeywhichbelongstobothofthetwotables;
| 6: forkeyinuniquekey |     | listdo |     |     |     |
| -------------------- | --- | ------ | --- | --- | --- |
7:
emit(key,null);
8: Setup()
| 9: Buildahashtablewiththeuniquekey |     |     | list; |     |     |
| ---------------------------------- | --- | --- | ----- | --- | --- |
10: Map2(null,tuple):
11: joinkey←extractthejoinkeyfromtuple;
12:
jointuple←tupletuplewhosejoinkeyiscontainedinthehashtable;
13: jointuple,←Projection(Jointuple);
14: emit(joinkey/a,taggedjointuple);
| 15: Reduce2(key,tag | list): |     |     |     |     |
| ------------------- | ------ | --- | --- | --- | --- |
16: T ←tuplesfromtableTforkey;
17:
S ←tuplesfromtableSforkey;
18: T, ←preprocessingfortableT,;
S, ←preprocessingfortableS,;
19:
20: NB T ←numberoftuplesinT,;
21: NB S ←numberoftuplesinS,;
22: Result←JoinGPU(T,,S,,NB
|     |     | T,NB | S); |     |     |
| --- | --- | ---- | --- | --- | --- |
23: fortupleinResultdo
24: emit(null,tuple);
principle: by analyzing the SQL statement, generate the implementation plan,
and optimize the implementation plan, including filtering, mapping operations
beforethejoinoperation. Thealgorithmpresentedinthispaperwillmapthetu-
plesintheMapphaseofthesecondroundofMap-Reduce. Foreachtuple,only
query-relatedattributesarekept,othersareremoved. Thosekeptattributesare
combined into new tuples. The new tuple has all the query-related attribute
values,butthesizeissmallerthantheoriginaltuple. Thepseudocodeisshown
| in Algorithm | 2.          |     |                              |     |     |
| ------------ | ----------- | --- | ---------------------------- | --- | --- |
|              | Algorithm2: |     | MappingAlgorithm(Projection) |     |     |
1: new tuple←null;
2: Attrs[]←extractattributesfromtupleT;
3: new tuple←combinerelevantattributesinAttrs[]toanewtuple;
| 3.2.2. Row  | and Column | Transformation |                 |           |                  |
| ----------- | ---------- | -------------- | --------------- | --------- | ---------------- |
| Traditional | relational | databases      | use row storage | patterns, | using tuple as a |
basic storage unit in the disk. All bytes of each tuple are stored adjacently. In
online transaction processing (OLTP), the query needs to return all or most of
| the columns, | making    | this storage | mode perform       | well.         |              |
| ------------ | --------- | ------------ | ------------------ | ------------- | ------------ |
| However,     | in online | analytical   | processing (OLAP), | queries often | involve mil- |
lions or more row tuples, but only a few of them are required for queries. For
example,asupermarketneedstocheckthetoptenhighestsalesofcommodities
this year. Users usually only concern about the name, categories, and sales.
At this point, the using of row storage will read a lot of useless data, because
8

only one line of data can be read at one time, of which only a few field value is
| required | for the query. |            |               |         |          |          |
| -------- | -------------- | ---------- | ------------- | ------- | -------- | -------- |
| The      | column storage | model is a | good solution | to this | flaw. As | shown in |
Figure 5, the column storage model stores the data in columns, and all the
data in the same column are stored in adjacent storage space. When storing
one row of data, different data fields are stored in the corresponding column’s
storage space. For thecolumn storagemodel, itonly needsto readthe columns
associated with the query. In addition, the column storage model performs
better in data compression than the line storage model. Although the column
storage model has many advantages, after being read from the disk, data still
needs to be stored in rows in memory for processing. When the number of to
bereadcolumnsistoolarge,theprocessofrowandcolumntransformationwill
bringtoomuchoverhead. Therefore,thecolumnstoragemodelismoresuitable
for the query with fewer columns involved. At present, many database systems
| use column | storage mode,  | such as SQL | Server[28].     |     |            |            |
| ---------- | -------------- | ----------- | --------------- | --- | ---------- | ---------- |
| In this    | paper, because | the data    | has been mapped | in  | the Map of | the second |
round,rowandcolumnconversioncannotbringtoomanybenefits. However,for
thejoinoperation,anecessarystepistoextractthejoinkeyvalueofeachtuple.
As is shown in Chapter 2.2, CUDA is not quite good at the string processing,
for the need of traversing the entire tuple to extract the join key, which will
undoubtedly increase the computing burden of the GPU. At the same time,
because the tuple contains variables of unsettled length, extracting the join key
is not a very wise choice in the kernel. So before sending data to the GPU, row
| and column | still need | to be transformed. |     |     |     |     |
| ---------- | ---------- | ------------------ | --- | --- | --- | --- |
Row Storage Model
|         |              |     |     | James   | Male   | 31  |
| ------- | ------------ | --- | --- | ------- | ------ | --- |
|         | Name Gender  | Age |     |         |        |     |
|         |              |     |     | Kobe    | Male   | 38  |
|         | James Male   | 31  |     |         |        |     |
|         |              |     |     | Anthony | Male   | 31  |
|         | Kobe Male    | 38  |     |         |        |     |
|         |              |     |     | Tylor   | Female | 28  |
| Anthony | Male         | 31  |     |         |        |     |
|         | Tylor Female | 28  |     |         |        |     |
Column Storage Model
|     |     |     |     | James | Kobe Anthony | Tylor  |
| --- | --- | --- | --- | ----- | ------------ | ------ |
|     |     |     |     | Male  | Male Male    | Female |
|     |     |     |     | 31    | 38 31        | 28     |
Figure5: Columnstoragemodel
9

| To do | the transformation, |     | extract all | the attribute | values | of  | each tuple | and |
| ----- | ------------------- | --- | ----------- | ------------- | ------ | --- | ---------- | --- |
store these attribute values into different buffers. Each buffer stores all the
values of an attribute. Note that attributes in each buffer are stored in the
same order. For any two different tuples t and s in the original data table, let
tuple t be preceded by tuple s. The position of each attribute of the tuple t
in the respective buffer is preceded by the corresponding attribute of the tuple.
As a result, only comparing the records in the join key buffer and extracting
the records in other locations to generate join results are needed. For example,
if the mth record in the T table join key buffer matches the nth record in the
S table join key buffer, extract the joining result of all mth records of T table
| buffers              | and all nth records | of S      | table buffers. |           |            |     |          |     |
| -------------------- | ------------------- | --------- | -------------- | --------- | ---------- | --- | -------- | --- |
| 3.3. GPU-Accelerated |                     | Equi Join | Operation      |           |            |     |          |     |
| This                 | section describes   | the       | details of     | equi join | operations | on  | the GPU, | in- |
cluding the threading model used in CUDA, the specific execution flow of join
operations, the estimation and analysis of results number, and the thread hier-
archy analysis. In addition, this section implements nested loop joins and hash
join operations.
哈尔滨工业大学工学硕士学位论文
3.3.1. GPU-B表的as缓e冲d区N中e第stned个记L录oo生p成J连o接i结n果。
| According | 3.4 t   o GP S U ec加ti速on等2值.3连,接ne操st作ed |     |   loop | join needs | to loop | through | two | tables, |
| --------- | ----------------------------------------- | --- | ------ | ---------- | ------- | ------- | --- | ------- |
sotheuseoftwo-dimensionalthreadmodelisessential,thatis,theorganization
of the thread blo至c此k，i本n文th所e(cid:6656)算th法r中ea对d数g据r的id预a过n滤d、t预h处e理o部rg分a已n经iz介a绍ti完on毕。of本t小he thread in the
节主要介绍GPU上实现等值连接操作的实现细节，包括CUDA中所采用的线
threadblockaretwo-dimensional. Figure6isathreadgridorganization, which
程模型、连接操作的具体执行流程以及对结果数量的估计分析、线程层次分析
contains a total of four thread blocks, each thread block also contains four
等。本节实现了嵌套循环连接以及哈希连接操作。
threads, and are in the form of 2∗2 organization. Thus, the line grid in both
3.4.1基于GPU的嵌套循环连接
horizontal axis and vertical axis contain two thread blocks, the same as the
| organization of | threads | in the | thread block. |     |     |     |     |     |
| --------------- | ------- | ------ | ------------- | --- | --- | --- | --- | --- |

|     |         |              |    图 ri3d-3 o 嵌 套 循 环 | 连 接 io nofnestedloopjoin |     |     |     |     |
| --- | ------- | ------------ | --------------------- | ------------------------ | --- | --- | --- | --- |
|     | Fig ure | 6: Thr e a d | g rg a n iz           | at                       |     |     |     |     |

嵌套循环连接的核心思想是对两个关系表中的元组进行循环遍历，根据匹
Whenmulti-threadsprocessnestedloopjoin,eachthreadneedstodealwith
|     | 配结果生成最后的新元组。上文说过，GPU |     |     | 最大的优点在于其强大的并行性， |     |     |     |     |
| --- | -------------------- | --- | --- | --------------- | --- | --- | --- | --- |
part of the data. 因此GPU上处理嵌套循环连接应该充分利用其丰富的线程资源。基于嵌套循环 Only when all threads have completed their tasks, the GPU
willreturnre连su接l需ts要t循o环t遍he历两C个P表U，.因O此b采v用io二u维sl的y,线t程h模e型to，t即al线p程r格o中ce线s程si块ng的组timefortaskson
织形式以及线程块中线程的组织形式均为二维的。图3-3为一个线程格的组织
形式，其中共包含四个线程块，每个线程块又都包含四个线程，并且均是以2*2
10
|     |     |     | - 27 -  |     |     |     |     |     |
| --- | --- | --- | ------- | --- | --- | --- | --- | --- |

the GPU depends on the last thread. Under this situation, something needs to
| be done | to balance | the task  | for | each      | thread. |               |     |              |     |
| ------- | ---------- | --------- | --- | --------- | ------- | ------------- | --- | ------------ | --- |
| In this | paper,     | for table | T   | and table | S,      | assuming that | the | organization | of  |
thread blocks in thread grids is m∗n, the organization of each thread in blocks
is x∗y. So the organization of whole threads in thread grids is mx∗ny. The
number of tuples to be processed in each table by each thread is given by
| equation | 1 and | equation | 2:  |     |     |     |     |     |     |
| -------- | ----- | -------- | --- | --- | --- | --- | --- | --- | --- |
|S|
|     |     |     |     | NB  | =   | +1  |     |     | (1) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
S
m∗x
|T|
|         |      |          |            | NB  | =           | +1         |     |              | (2) |
| ------- | ---- | -------- | ---------- | --- | ----------- | ---------- | --- | ------------ | --- |
|         |      |          |            | T   | n∗y         |            |     |              |     |
| Suppose | that | a thread | is located |     | in a thread | block with | the | index (a,b), | the |
index of the thread in the thread block is (c,d). The position, where to read
| NB and | NB    | tuples from                                  | table | S           | and T, | is shown in | equation | 3 and      | 4:  |
| ------ | ----- | -------------------------------------------- | ----- | ----------- | ------ | ----------- | -------- | ---------- | --- |
| S      |       | T                                            |       |             |        |             |          |            |     |
|        |       |                                              | ID    | =(a∗x+c)∗NB |        |             |          |            | (3) |
|        |       |                                              | S     |             |        | S           |          |            |     |
|        |       |                                              | ID    | =(b∗y+d)∗NB |        |             |          |            | (4) |
|        |       |                                              | T     |             |        | T           |          |            |     |
| ID     | andID | arethestartingpositionsofthedataintwotables. |       |             |        |             |          | InFigure6, |     |
| S      |       | T                                            |       |             |        |             |          |            |     |
theredboxrepresentsthethread,whichhandlesthejoinoperationbetweenT1
and S3. In CUDA, the thread block, the index of the thread in the block, sizes
of grid and block can be obtained directly, making it easy to connect the data.
| During | thread | execution, | whenever |     | a match | is successful | and | a new | tuple |
| ------ | ------ | ---------- | -------- | --- | ------- | ------------- | --- | ----- | ----- |
is generated, new tuple needs to be cached, and the result is returned when
all threads have finished executing. The biggest problem of multithreading
writing data into memory is writing memory conflicts. In order to prevent the
conflict, each thread can be allocated a fixed storage space. Whenever a thread
generatesaresult,theresultswillbewrittentoitscorrespondingstoragespace.
And when all threads have completed the task, the result will be summed and
thenreturned. Atthesametime, alocalvariableissetineachthreadtorecord
| the number | of        | results generated |     | in the       | thread. |           |           |                |     |
| ---------- | --------- | ----------------- | --- | ------------ | ------- | --------- | --------- | -------------- | --- |
| Since      | the exact | number            | of  | join results | is      | not known | until the | join operation |     |
is performed, when allocating storage space for each thread, space is set to a
| maximum          | possible | number     | of   | results, | that is,  | NB S ∗NB | T .          |     |          |
| ---------------- | -------- | ---------- | ---- | -------- | --------- | -------- | ------------ | --- | -------- |
| 3.3.2. GPU-Based |          | Hash       | Join |          |           |          |              |     |          |
| According        |          | to Section | 2.3, | hash     | join only | needs to | loop through |     | one data |
table. So one-dimensional organization of both blocks in grid and threads in
the block are more suitable for CUDA. As shown in Figure 7, the grid contains
| four thread | blocks, | and       | each thread |               | block contains | two      | threads. |      |        |
| ----------- | ------- | --------- | ----------- | ------------- | -------------- | -------- | -------- | ---- | ------ |
| Assuming    |         | that each | thread      | grid contains |                | n thread | blocks,  | each | thread |
blocks
blockcontainsn threads,andifthetableSisthelargertable,thenumber
threads
| of tuples | in the | table S allocated |     | to  | each thread | is given | by the | equation | 7:  |
| --------- | ------ | ----------------- | --- | --- | ----------- | -------- | ------ | -------- | --- |
|S|
(5)
|     |     |     |     | NB S | =   | +1  |     |     |     |
| --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- |
m∗x
11

哈尔滨工业大学工学硕士学位论文
加获得最终连接结果个数。
由于在连接操作执行之前，并不知道连接结果的确切个数。因此，当为每
个线程分配存储空间时，可按照最大可能结果数量进行分配，即分配NBS*NBT
个结果所占大小的存储空间。
3.4.2基于GPU的哈希连接

图3-4 哈希连接
|     |     |     | Figure7: | Threadgridorganizationofhashjoin |     |     |     |     |     |
| --- | --- | --- | -------- | -------------------------------- | --- | --- | --- | --- | --- |

|     |                                                                                              | 哈希连接的核心思想是对较小表建立哈希表，接着对另一个较大数据表进 |     |     |     |     |     |     |        |
| --- | -------------------------------------------------------------------------------------------- | -------------------------------- | --- | --- | --- | --- | --- | --- | ------ |
|     | In fa行c循t,环in遍a历d，d对iti大on表中to的t每he一l个as元t组th都r探ea测d哈in希表th，e进la行st匹t配h判re断ad以b及l连oc接k,操each |                                  |     |     |     |     |     |     | thread |
handles作N。B与S嵌套tu循pl环es连o接f不t同ab的le是S，,哈a希nd连接th仅e仅re需m要a循in环in遍g历t一up个le数s据a表re。h此a种ndled by the
last thr情ea况d下. ，If a b lo中c线k程in采d用ex一i维n组t织he形g式r较id为is适合p,。a即n线d程th格e中in线d程ex块的of组t织hread in the
|     |     | CU  | D A |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
block is q, the location from where to start reading NB tuples in table S can
形式以及线程块中线程的组织形式均为一维的。如图3-4所示，S线程格中包含
| be  | calculated 4个线程块，且线程块的ID是一个自然数字；每个线程块中含有2个线程，线 | by  | equation | 6:  |     |     |     |     |     |
| --- | ---------------------------------------------- | --- | -------- | --- | --- | --- | --- | --- | --- |
程的组织形式同样是一维的。
|     |     |            |     | ID =(p∗n             | +q)∗NB |           |     |     | (6) |
| --- | --- | ---------- | --- | -------------------- | ------ | --------- | --- | --- | --- |
|     |     | 假设每个线程格包含S |     | 个线th程re块ad，s每个线程块包S含 |        |           |     |     |     |
|     |     |            |     | n_blocks             |        | n_threads | 个线  |     |     |
程，不妨假设S表是较大表，每个线程分配的S表中元组个数由公式(3-5)给出：
|     | Thispaperintroducesthehashbuckettohandlehashconflicts. |     |     |     |     |     |     | Whenevera |     |
| --- | ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --------- | --- |
tupleis d e t e c t e d , i t i s fi r s t p o sit ionedt|(cid:2903)o| thec or r e s p o n d i n g h u s h b u c k etthrough
|     |            |                       |                     |                   𝑁 𝐵 = | + 1   |                      |           (3 | -5 )   |     |
| --- | ---------- | --------------------- | ------------------- | ----------------------- | ----- | -------------------- | ------------ | ------ | --- |
(cid:3020) a(cid:3041)_s(cid:3029)m(cid:3039)(cid:3042)(cid:3030)a(cid:3038)(cid:3046)l∗l(cid:3041)_(cid:3047)r(cid:3035)a(cid:3045)(cid:3032)n(cid:3028)(cid:3031)g(cid:2929)e
the hash function, followed by of detection in the bucket. Hash
bucket 实siz际e上is，fi除x了ed最,后so一个th线e程sp块a中ce最u后t一ili个za线ti程on之外is，sl每ig个ht线ly程i均n会ad处e理quNaBteS 个, but the de-
tectionSeffi表元cie组n，cy剩i下s的as元g组o全od部a由s最o后th一er个s.线程负责。
|     | As i t sh假ow设n某个in线A程lg位o于ri索th引m为1p,的w线h程en块t内h，e |     |     |     | 该da线ta程在is所se属n线t程to块t中h的e索G引PU为, |     |     | NB  | and |
| --- | -------------------------------------------------- | --- | --- | --- | --------------------------------- | --- | --- | --- | --- |
T
| NB  | arqe，s该en线t程a由s公w式ell(.3-6S)o所N给出B的T位∗置N读B取SNisBS |     |     |     | s个etSa表s中th的e元m组a。xi mum |     | storage | space. |     |
| --- | ------------------------------------------------- | --- | --- | --- | ------------------------ | --- | ------- | ------ | --- |
S
|     |                                                    𝐼𝐷 |     |     | =(𝑝∗𝑛_𝑡ℎ𝑟𝑒𝑎𝑑𝑠+𝑞)* NBS               (3-6)  |     |     |     |     |     |
| --- | ----------------------------------------------------- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- |
(cid:3020)
| 3.3.3. | E stim上a述t所io有n参of数J均o可in以R在es                                                         |     |     | u l ts S内iz核e程序中直接获得，每个线程只需遍历其 |     |     |     |        |      |
| ------ | -------------------------------------------------------------------------------------- | --- | --- | ------------------------------ | --- | --- | --- | ------ | ---- |
|        |                                                                                        |     |     | C U D A                        |     |     |     |        |      |
|        | As m对e应n的tio部n分ed元组ea即rl可ier。,基b于ef哈or希e表th的e尺k寸er可ne能l会p很ro大gr，am因此p将er哈fo希rm表s存t储h在e |     |     |                                |     |     |     | actual | join |
operation, it is necessary to preallocate enough memory in the CPU for the
result. B  utbeforethejoiniscomplet-e 2d9 -,  wecannotknowthespecificnumberof
results. Usually,memoryissetwithregardtothesizeoftheCartesianproduct.
But obviously, when tables are too large, the size of the Cartesian product will
be far larger than that of device memory. The existing research is based on
the experiments on small data set, so even if the distribution of memory is in
accordance with the Cartesian product, it does not exceed the device memory.
Although the method proposed in this paper is based on the Cartesian product
aswell,duetothedatapre-filteringandMap-Reducestructure,theperformance
| of the | estimation |      | is far | better than that | of the existing | results. |         |       |       |
| ------ | ---------- | ---- | ------ | ---------------- | --------------- | -------- | ------- | ----- | ----- |
|        | Assuming   | that | the    | ratio of tuples  | participating   | in the   | join of | table | T and |
table S is α and β. So, after pre-filtering, β∗|S| and γ∗|T| tuples respectively
perform the actual join operation. As mentioned before, tuples with the same
keyvaluearepassedtothesameReducer. IftherearekReducers,eachReducer
dealswithω 1 ∗β∗|S|,ω 2 ∗β∗|S|......ω k ∗β∗|S|S-tuplesandλ 1 ∗γ∗|T|,λ 2 ∗γ∗
|T|...λ ∗γ∗|T| T-tuples, and the parameters satisfy the following conditions:
k
|     |     |     |     | ω +ω | +......ω =1 |     |     |     |     |
| --- | --- | --- | --- | ---- | ----------- | --- | --- | --- | --- |
|     |     |     |     | 1 2  | k           |     |     |     |     |
(7)
|     |     |     |     | λ +λ | +......λ =1 |     |     |     |     |
| --- | --- | --- | --- | ---- | ----------- | --- | --- | --- | --- |
|     |     |     |     | 1 2  | k           |     |     |     |     |
12

| R   | results | need | to be allocated |     | storage | space: |     |     |     |
| --- | ------- | ---- | --------------- | --- | ------- | ------ | --- | --- | --- |
size
k
(cid:88)
|     |     |     | R =γ∗β∗|S|∗|T| |     |     | ω   | ∗λ  |     | (8) |
| --- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- |
|     |     |     | size           |     |     |     | i i |     |     |
i=1
| Because            | parameters |           | in equation | 8   | are all | below | 1, it will | save a lot of | space |
| ------------------ | ---------- | --------- | ----------- | --- | ------- | ----- | ---------- | ------------- | ----- |
| for pre-allocating |            | memory.   |             |     |         |       |            |               |       |
| 3.3.4. Thread      |            | Hierarchy |             |     |         |       |            |               |       |
InthestandardCUDAprogram,thethreadisorganizedintheformofthread
block-thread hierarchy, where the number of thread blocks and the number of
threads in each thread grid can be set, but there is only one thread grid. The
algorithm in this paper combines Hadoop with the GPU. The Map-Reduce
architecture is also a multi-threaded task. Multiple Reducers perform tasks in
parallel. EachReducercorrespondstoathread. Therefore, thehierarchyofthe
| proposed | algorithm | is           | thread grid | (Reducer)-thread |     |         | block-thread. |                  |     |
| -------- | --------- | ------------ | ----------- | ---------------- | --- | ------- | ------------- | ---------------- | --- |
| In CUDA  |           | programming, | the         | number           | of  | threads | in each       | block is usually | set |
to a multiple of 32, the number of blocks is based on the amount of data,
usually the more the better. Assuming that the GPU has a total of N threads,
the reducer number is n , and each grid contains n of blocks. Each
|     |     |     | reducers |     |     |     | blocks |     |     |
| --- | --- | --- | -------- | --- | --- | --- | ------ | --- | --- |
threadblockcontainsn threads. Theparameterrelationshipmustsatisfy
threads
| the relationship |                                             | 9   |            |            |     |        |     |                  |     |
| ---------------- | ------------------------------------------- | --- | ---------- | ---------- | --- | ------ | --- | ---------------- | --- |
|                  |                                             |     | n reducers | ∗n threads | ∗n  | blocks | <N  |                  | (9) |
| Thatis,          | inthecasewheretherelationshipisestablished, |     |            |            |     |        |     | thebiggerproduct |     |
of parameters the better. When the total number of set threads is greater than
the number of threads on the GPU, some tasks need to wait for a free thread.
In this way, the task waiting and the creation of multiple threads will bring a
lot of additional overhead. As shown in Algorithm 1, the number of Reducers
| can be     | changed     | by modifying |         | the parameter |        | α.  |          |                   |     |
| ---------- | ----------- | ------------ | ------- | ------------- | ------ | --- | -------- | ----------------- | --- |
| 3.4. Mixed | Programming |              | of GPU  | and           | Hadoop |     |          |                   |     |
| The        | Map-Reduce  |              | program | runs          | on CPU | and | is based | on Java language. |     |
While, the GPU kernel program runs on GPU, based on the CUDA program-
ming model and the C language. Therefore, the combination of Hadoop and
GPU involves a compatibility problem between Java and C. This experiment
is programmed through the JNI interface to complete this work. Since the file
format of the CUDA program is .cu, and the traditional C language is the .c
file, there is a need of an additional .c file as a middleware. Through this mid-
dleware,GPUkernelfunctioncanbecalled. AndthenMap-Reducewillcallthe
middleware, so as to achieve the join of CPU and GPU. Because the memory
cannot be shared between CPU and GPU, the same data from Java to C needs
a copy, and then another copy from C memory space to GPU device memory.
Thatis,totransferdatafromMap-ReducetoGPU,andatotaloftwocopiesare
required. Obviously,thisintroducesadditionaloverheadandmemoryfootprint,
| so future | research | should | continue | to  | solve | this problem. |     |     |     |
| --------- | -------- | ------ | -------- | --- | ----- | ------------- | --- | --- | --- |
13

| 4. GPU-Based |                | Theta | Join | with    | Hadoop |          |          |         |          |
| ------------ | -------------- | ----- | ---- | ------- | ------ | -------- | -------- | ------- | -------- |
| Given        | the importance |       | of   | Hadoop, | there  | are many | research | focused | on using |
Map-Reduce to deal with theta join operations. Koumarelas[29], Okcan[30]
and Penar[31] achieved theta join operations of two tables on Map-Reduce,
哈尔滨工业大学工学硕士学位论文
meanwhile Yan[32], Zhang[33] and Changchun[34, 35] achieved a multi-table
thetajoin匹. A配u。gu如s图tyn4[-316所]u示se，d阴th影e部G分PU所代to表es的ti区m域at均et需he要j进oin行s匹el配ec。tiv ityfortheta
join of tw o taOblkecsa.n [28](cid:6656)出了一种经典的Map-Reduce下处理非等值连接操作算法。如
ThissectionfocusesonhowtocombineHadoopwithaGPUtohandletheta
图4-2 a）所示，用一个二维矩阵表示两个关系表的笛卡尔乘积。将此二维矩阵
join operations based on two data tables, multi-table join will be studied later.
划分成许多个区域，每个区域均对应一个reducer，并且每个区域均有一个ID。
在 map 函数中，对于任意一个元组，对与其相交的每个区域均生成一个（ID,
| 4.1. Classic | Theta | Join | Algorithm |     | on Hadoop |     |     |     |     |
| ------------ | ----- | ---- | --------- | --- | --------- | --- | --- | --- | --- |
<Record, tag>）键值对，其中tag即为标识该元组来源的标识。如此一来，具有
| For theta | joins, | simply |     | passing | tuples | with the | same | join key | to the same |
| --------- | ------ | ------ | --- | ------- | ------ | -------- | ---- | -------- | ----------- |
Reducer i 相 s 同 noItDs 的 uffi 元 c 组 ie ， nt 即 to 位于 ge 同 t 一 th 个 e 区 fu 域 ll 的 re 元 su 组 lt. ，会 Be 被 ca 传 us 递 e 到 in 相 t 同 he 的 tarejdouincera 中 t 进 up 行 le
does not 处on理ly。n通ee过d此to种m方a式tc，h 能its够t保up证le二s 维wi矩th阵t中he每s一am个e元jo素in均k能ey够s,得b到ut处a理lso，n从e而ed
to match获th得e正tu确p的le结s t果ha。t are greater or less than the join key. As shown in
| Figure 8, |   the areas | represented |     | by  | the shaded | parts | all need | to be | matched. |
| --------- | ----------- | ----------- | --- | --- | ---------- | ----- | -------- | ----- | -------- |

             F ig u  re  8 : M  a tr图ix4i-n1 c非la等ss值ic连al接go rithm

| Okcan | [30]目p前ro，po所se有d |     | a c  | la s s ic | M 下ap处-R理ed两u表ce非p等ro值ce连ss接in操g |     |     | 作th的et算a法jo均in采o用pe类ra似tio的n |     |
| ----- | ----------------- | --- | ---- | --------- | -------------------------------- | --- | --- | ---------------------------- | --- |
|       |                   |     | Ma p | -R e d uc | e                                |     |     |                              |     |
algorithm, named M-Bucket-I. As shown in Figure 9(a), the Cartesian product
|     | 思想，即将代表两个表笛卡尔乘积的矩阵划分成若干个区域，每个 |     |     |     |     |     |     |     | reducer 处 |
| --- | ----------------------------- | --- | --- | --- | --- | --- | --- | --- | --------- |
oftwotablesisrepresentedbyatwo-dimensionalmatrix. Thematrixisdivided
理一个区域中数据的非等值连接。实际上，部分区域中可能并没有任何的结果
into many areas, each region corresponds to a Reducer, and each region has an
ID. In Ma产p生fu，n如ct图ion4,-1fo所r示ea，ch空t白u的ple方,格a中(I并D不,<产R生e任co何rd结,t果ag。>Ok)ckane y[2-v8]a等lu人e 同pa样ir(cid:6656)is
generated出fo了r一ea种ch称r为egiMon-Biunctkeerts-Iec改ti进ng版i本t,的wh算e法re，ta在g此is算th法e中id，en只ti对ty确th定a会ti产de生nt结ifi果es
the tuple的so区ur域ce进.行A处s 理a ，res对u确lt,定tu不p会le产s w生i结th果th区e域sa中m的e数ID据,不th进at行i任s,何tu实pl际es的lo处c理at操ed
in the same 作。但是此种算法需要事先知道一些关于原始数据的统计信息，通常需要引入 area, are passed to the same Reducer for processing. In this way, it
is possible to ensure that each element in the matrix can be processed and led
额外的开销来获取这些统计信息。
| to the correct | result. |     |     |     |     |     |     |     |     |
| -------------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
4.2.2改进Map-Reduce处理非等值连接算法
  如上一节所说，M-Bucket-I算法仅仅对能确定产生结果的区域进行非等值
|     |     |     |     |     |     | - 34 -  |     |     |     |
| --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- |
14

哈尔滨工业大学工学硕士学位论文
哈尔滨工业大学工学硕士学位论文
连接操作。本文所(cid:6656)出的算法在此基础上，进一步确定出某些区域，该区域中
连接操作。本文所(cid:6656)出的算法在此基础上，进一步确定出某些区域，该区域中
来自于两表的任意一对元组均满足连接条件。因此，对于这些区域中的数据无
来自于两表的任意一对元组均满足连接条件。因此，对于这些区域中的数据无
须进行任何判断，直接生成连接结果。
须进行任何判断，直接生成连接结果。 哈尔滨工业大学工学硕士学位论文
哈尔滨工业大学工学硕士学位论文
连接操作。本文所(cid:6656)出的算法在此基础上，进一步确定出某些区域，该区域中
连接操作。本文所(cid:6656)出的算法在此基础上，进一步确定出某些区域，该区域中
来自于两表的任意一对元组均满足连接条件。因此，对于这些区域中的数据无
来自于两表的任意一对元组均满足连接条件。因此，对于这些区域中的数据无
须进行任何判断，直接生成连接结果。
须进行任何判断，直接生成连接结果。
a）经典Map-Reduce算法 b）改进Map-Reduce算法
a）经典Map-Reduce算法 b）改进Map-Reduce算法
图4-2Map-Reduce处理非等值连接
图4-2Map-Reduce处理非等值连接
类似于M-Bucket-I算法，本文所(cid:6656)出的方法 需 要 首 先对两个原始数据表进
类似于M-Bucket-I算法
(a
，
)
本
C
文
las
所
sic
(cid:6656)
a
出
lgo
的
rit
方
hm
法需要首先
(b)
对
D
两
ev
个
el
原
op
始
ed
数
al
据
go
表
rit
进
hm
行统计，分别统计出a两）个经a）表典经连M典a接p-MR键eadp的u-Rc取eed算值uc法e范 算 围 法 ， 并 分 别 计 算b ） 出 改 b两进）个改M范a进p-围RMe的adpu-cRkee算分du法ce 算法
行统计，分别统计出两个表连接键的取值范围，并分别计算出两个范围的k分
位数 位 。 数 图 。图 4-2 4 - b 2 ） b 展 ） 示 展 了 示 当 了当 k取F k i值g 取 u为r 值 e94 为 :图 时T 44 ，h-时图2eM 二t ， a 4a 维 -pj 二2 o-MR 矩in 维eadp 阵au矩- l Rcg的 ee阵 o d处r组 u i 的 t c理h织 e组 m非处 形 等织理 o式n值形非 M。 连等式 a在 接值 p 。 - 图 连 R 在 e 接 4d 图 -u 2c 4 eb - ） 2 b）
所示二维矩阵 中， 每个元素并不代表一个元组对，而是代表着一个取值范围对。
所示二维矩阵中，每个元素并不代表一个元组对，而是代表着一个取值范围对。
与M-BucIknett-hIi算s 法a类lg不似o类r同于it似的hM于m是-B,，MuocM-nkBle-uyBt-cuIktc算hekte-e法Ita-算I，r算e本法a法文，w中本所he划文(cid:6656)re分所出t出(cid:6656)h的e的出方r区e的法su域方需lt是法要i一s需首d个要先et任对首er意两先m规个对in原模两ed始个i数s原p据始ro表数c进e据ss表ed进,
与M-Bucket-I算法不同的是，M-Bucket-I算法中划分出的区域是一个任意规模
的矩a形n，d而no本行a文c统t所行u计a(cid:6656)统l，p出计分ro算，别c法分e统s所别s计in划统出g分计i两s的出个p区e两表rf域个连or是表接m一连键ed个接的o严键取n格的值th的取范e正值d围a方范，ta形围并t，h，分a即并别td每分计o个算别es区出计n域两o算t的个出p范r两o围d个u的范ce围kt分h的ekre分-
的矩形，而本文所(cid:6656)出算法所划分的区域是一个严格的正方形，即每个区域的
横纵 s 轴 u 的 lt 长 ar 度 e 位 a 相 . 数 H 同位。 o 。数w 图如。e 4 v 此图- e 2 r 划 , 4b- t ）分2 h 展 i 的b s）示 a 好 l展了 g 处 o示当 r 在 i了t 于k h当取 m ，值k对 re取为 q 于值u 4某 ir为时 e 些 s ，4区 s时o 二域 m，维来 e二矩 i 说 n维阵 f ， o矩的 r 其 m阵组中 a的织 t 任 io 形组意 n 式织一 a 。形b 个 o 在式ut 图。t在h 4- e 2图 o b r 4） i - g 2 i n b a）l
横纵轴的长度相同。如此划分的好处在于，对于某些区域来说，其中任意一个
data in advance, which means additional overhead is needed.
元组对均符合所连示接所二条示维件二矩，维阵因矩中此阵，每可中个以，每元不个素用元并对素不这并代些不表区代一域表个中一元的个组数元对据组，进而对行是，连而代接是表判着代哈断一表尔。个着滨取如工一业值 个大范取学工围值学对范硕。士围学对位。论文
元组对均符合连接条件，因此可以不用对这些区域中的数据进行连接判断。如
与M与-BMuc-kBeutc-Ik算et-法I算不法同不的同是的，M是-，BMuc-kBeut-cIk算et-法I算中法划中分划出分的区出域的是区一域个是任一意个规任模意规模
的矩的形矩，形而，本而文本所文(cid:6656)所出(cid:6656)算出法算所法划所分划的分区的域区是域一是个一严个格严的格正方的形正，方即形每，个即区每域个的区域的
横纵横轴纵的轴长的度长相度同相。同如。此如划此分划的分好的处好在处于在，于对，于对某于些某区些域来区说域，来其说中，任其意中一任个意一个
元组元对组均对符均合符连合接连条接件条，件因，此因可此以可不以用不对用这对些这区些域区中域的中数据的进数行据连进接行判连断接。判如断 。如
(a) Greater and greater or (b) Lessandlessorequal (c) Notequal
equala)Sa表)S大表于大（于等（于等）于T）表T 表 b ) S b表)S小表于小（于等（于等）于 T ）表 T 表 c)S表不等于T表
图4-3 不同连接条件下结果分布情况
- 35 -- 35 -
Figure10: Organizationofm atrixunderdifferentjoinconditions
图 4 -3 a ） 所示，当连接条件为S表连 接键 属性值大于或者大于等于T表连接键
4.2. Improved Thae)tSa表 a J ) 大 S oi表于n大（A于等lg于（o）等ritT于h表）m属 T o性 表n 值 H 时 a d， o 绿 o p b色 ) aS区 n表 d b域小 )S G内于表P的（小U等任于于意（）等一T于对表）元 T组表对 均满足连接条件，而红色区域内的元
To solve this problem, this pape组r对pr需es要en进ts行a判n断im，p白ro色ve区d域a内lgo的ri元th组m对. 一O定n不th满e足连接条件。图4-3 b）所示
basis of th e classic algorithm, this a S lg表or连 - i t 3 接 5 h - m 键 - 35 属c -a 性n值fu小rt于he或r i者de小n于tif等y于cer T ta表in连a接re键as属,性值以及图4-3 c）所示S表
where tuples from two tables satisfy the join condition.
连接键属性值不等于T表连接键属性值等情况同样可如此判断。我们仅仅需要
Similar to the M-Bucket-I, this algorithm calculates the range of each table
将红色区域的数据下发到GPU上去进行非等值连接处理。即，仅仅对角线上的
join key and k quantiles of each range. Figure 9(b) shows the organization of
区域需要下发到GPU上执行，其它区域可根据区域ID直接进行判断。算法伪
the two-dimensional matrix when k is 4. In this matrix, each element does
not represent a tuple pair, but a ra代ng码e如pa算ir法. U7n所li示ke。t he M-Bucket-I where the
divided area is the rectangle of any size, this algorithm divides the area into
strict squares. The advantage of thi算s d法iv7i：sioMnapis-R,efdourcseo处m理e非re等gio值n连s,接if any one of
the tuple pairs meets the join condition, there is no need to judge the data in
Map(Key:null,Value: a tuple from a split of either table)
this region for the join.
join_key ← extract the join key from Value;
if Value ∈ S then
RegionID.x ←bucket ID of Value according to its join key;
15
for all possible RegionID.y according to the join condition do
emit (<RegionID.x, RegionID.y >,<Value, "S">);
end if
if Value ∈ T then
RegionID.y ←bucket ID of Value according to its join key;
for all possible RegionID.x according to the join condition do
emit (<RegionID.x, RegionID.y >,<Value, "T">);
- 36 -

| As shown | in Figure | 10(a), when the | join condition | is that | join key | attribute |
| -------- | --------- | --------------- | -------------- | ------- | -------- | --------- |
value of S-table is greater than or greater than or equal to that of T-table, any
pair of tuple pairs in the green region satisfies the join condition, and the tuple
pair in the red region needs to be judged. While the tuple pair in the white
region must not satisfy the join condition. Figure 10(b) shows that of S-table
is less than or less than or equal to that of T-table. And Figure 10(c) show the
condition that two values are not equal. So only the red area of the data needs
to be sent to the GPU for theta join processing. And the other areas can be
| judged directly | by the area | ID. The pseudo | code | is shown in | algorithm | 3.  |
| --------------- | ----------- | -------------- | ---- | ----------- | --------- | --- |
Algorithm3: thetajoinonMap-Reduce
| 1: Map(key:null,value: | atuplefromasplitofeithertable) |     |     |     |     |     |
| ---------------------- | ------------------------------ | --- | --- | --- | --- | --- |
2:
joinkey←extractthejoinkeyfromvalue;
| 3: if value∈S | then |     |     |     |     |     |
| ------------- | ---- | --- | --- | --- | --- | --- |
4: RegionID.x←bucketIDofvalueaccordingtoitsjoinkey;
5: forallpossibleRegionID.yaccordingtothejoinconditiondo
6: emit(<RegionID.x,RegionID.y>,<value,”S”>);
| 7: if value∈T | then |     |     |     |     |     |
| ------------- | ---- | --- | --- | --- | --- | --- |
8: RegionID.y←bucketIDofvalueaccordingtoitsjoinkey;
9: forallpossibleRegionID.xaccordingtothejoinconditiondo
10: emit(<RegionID.x,RegionID.y>,<value,”T”>);
| 11: Reduce(key,:RegionID,valuelist: |     | taggedtuplescorrespondinginRegionID) |     |     |     |     |
| ----------------------------------- | --- | ------------------------------------ | --- | --- | --- | --- |
12: T ←null;
13: S ←null;
14:
foreachtupletinvaluelistdo
15: addttoSorTaccordingtoitstag;
16: if RegionID.x==RegionID.ythen
| 17: result←GPU | thetajoin(S,T); |     |     |     |     |     |
| -------------- | --------------- | --- | --- | --- | --- | --- |
18: foreachrecordinresultdo
19:
emit(null,record);
| 20: elseif                          | RegionID.xmatchesRegionID.yaccordingtothejoinconditionthen |     |       |     |     |     |
| ----------------------------------- | ---------------------------------------------------------- | --- | ----- | --- | --- | --- |
| 21: cartesianresult←docrossjoinforS |                                                            |     | andT; |     |     |     |
22: foreachrecordincartesianresultdo
23: emit(null,record);
AsshowninFigure10(a),theAregioncoordinatesare(3,1)andtheabscissa
is greater than the ordinate. Therefore, any tuple in the A region satisfies the
condition, that join key attribute value of table S is greater than that of table
T.Whentheabscissaisequaltotheordinate,theregionmayhaveajoinresult,
| so it is necessary | to send              | it to the GPU | for theta   | join judgment. |           |        |
| ------------------ | -------------------- | ------------- | ----------- | -------------- | --------- | ------ |
| In the             | theta join operation | on the        | GPU, nested | loop join      | algorithm | can be |
used, the thread organization form and the processing mode are the same as
| those of | the GPU in Chapter | 3.                |         |             |              |      |
| -------- | ------------------ | ----------------- | ------- | ----------- | ------------ | ---- |
| The      | method used in     | this article only | applies | the data in | the diagonal | area |
to the GPU, so it is only necessary to allocate storage space for the data in the
| diagonal        | area, which can | increase the | storage space | utilization. |     |     |
| --------------- | --------------- | ------------ | ------------- | ------------ | --- | --- |
| 5. Experimental | Results         |              |               |              |     |     |
Thissectioncomparesthemethodsproposedinthispaper,throughtheexist-
ingGPUacceleratedjoinoperationalgorithmtoverifywhetherithasimproved
performance, being more efficient. At the same time, compared with the CPU
16

implementation of the proposed algorithm in this paper, to verify whether the
GPU implementation has the speedup for the join operation.
The experiments done in this section are based on larger datasets. Unless
special instructions, all experimental raw data are TPC-H data sets. GPU
devices running on the Linux operating system, the version of Ubuntu 14.04,
and Hadoop is version 2.6.0.
5.1. Nested Loop Join
This section focuses on the experiments of the nested loop join. It is com-
paredseparatelywiththeGPUacceleratednestedloopjoinwithasingledevice
and the proposed algorithm in CPU. At the same time by changing the value
of α in algorithm 1 to change the number of Reducers started by Map-Reduce,
changes in the execution time can be observed. At the same time, through the
synthetic data, the performance of the method can be observed. If there is no
specialdescription, thevalueofα is100. Thisexperimentisbasedonthesmall
dataset, because the cost of the nested loop join is very large, the traditional
GPU acceleration method is not able to effectively support large data sets.
5.1.1. Comparison of Nested Loop Join with Single GPU
In this experiment, in order to ensure the reliability of the experimental
results, the proposed method is also implemented on a single GPU device, and
Hadoop is a pseudo-distributed structure. As shown in Figure 16, when the
data set is small, the efficiency of the proposed method is lower than that of
the traditional one. However, the execution time of the traditional method is
significantlyincreasedwiththe哈i尔n滨cr工e业a大se学工of学t硕h士e学o位r论ig文i naldataset,whichisdifferent
tothepro不p会os出ed现a在lg最o终rit结h果m中. A的s数s据ho过w滤n掉in，t实h际efi执g行ur连e接,i操tw作i的ll数ha据v远ea远t小le于as原t始onetimes
the speed数up据o集v。er经t过he预t过ra滤d后iti，on实a际l处on理e,连w接h操ic作h的m时ea间n大s大un降d低er，t但he预s过am滤过e a程c同celerating
condition样o引f G入P了U额,外t的he时p间ro开p销os。ed因此m，et当ho数d据is集m比o较r小e时effi，c预ie过nt滤.所带来的增益效
10
9
8
7
6
5
4
3
2
1
0
2MB X 4MB X 8MB X 12MB X 16MB X
1MB 2MB 4MB 6MB 8MB
图5-1 与单一GPU下嵌套循环连接对比
果低于其所带来的额外开销，此时本文(cid:6656)出的方法执行时间较长；随着数据集
尺寸的增加，当预过滤带来的增益效果超过其所带来的开销时，本文所(cid:6656)出的
方法执行时间明显低于传统方法。本次实验是基于小数据集上进行，是因为嵌
套循环连接的代价十分庞大，传统的GPU加速方法并不能够有效地支持大数据
集，因此本次实验选择小数据集进行。
5.2.2 TPC-H数据集上与CPU处理嵌套循环连接对比实验
图 5-2 所示为 TPC-H数据集下本文所(cid:6656)出的加速嵌套循环连接算法 GPU
版本与CPU版本对比实验结果。GPU版本中，算法5中α取值为100，而CPU
版本中α取值为1，从而保证了CPU版本的执行效率最佳，使得对比实验结果
更加公正。除α取值不同以外，GPU版本与CPU版本的执行流程完全一样，
仅仅是执行实际连接操作的设备不同，保证了本次实验结果的可靠性。从图5-2
可以看出，相比于CPU实现，用GPU实现本文所(cid:6656)出的嵌套循环连接算法并
无明显的加速效果。这是因为本文所(cid:6656)出的算法的CPU版本中，在第二轮任务
的reduce阶段，只有具有相同连接键值的元组才会传递到相同的 reducer中。
而本次实验采用的是TPC-H数据集，连接键的分布较为均匀，每个连接键值仅
- 40 -
s/emit
GPU
HADOOP+GPU
data size
Figure11: ComparisonofnestedloopjoinwithsingleGPU
Data that does not appear in the final result is filtered out, and the data
thatactuallyperformsthejoinoperationismuchsmallerthantheoriginaldata
set. After pre-filtration, the actual processing time is greatly reduced, but the
pre-filtration process also introduces additional time overhead.
17

Therefore, when the data set is small, the gain effect of the pre-filtering is
lowerthanthatoftheadditionalcost,sothemethodproposedinthispaperhas
a long execution time at first. With the increase of the data set, the gain effect
exceedstheoverhead,sothemethodproposedinthispaperissignificantlylower
than the traditional method.
5.1.2. Comparison of Nested Loop Join with CPU on TPC-H Data Set
The value of α in the CPU is 1, which ensures the best execution efficiency.
Except for the value of α and the equipment, the implementation process of
GPA and CPU is exactly the same. As shown in Figure 12, compared with
the CPU implementation, using the GPU to achieve the proposed nested loop
join algorithm has no obvious speedup. This is because, in Reduce phase of the
secondroundofMap-ReduceofCPUversion,onlytupleswiththesamejoinkey
will be passed to the same Reducer. In this experiment, the distribution of the
TPC-H data join keys is even. Each join key value corresponds to only a small
number of tuples. Therefore,
哈尔
th
滨
e
工业
a
大
ct
学
u
工
a
学
l
硕
e
士
x
学
ec
位
u
论
t
文
io n time of the join operation in
the CPU仅对ve应rs少io量n的i元s 组ve，r因y此sm在aCllP,Um版o本st中o连f接th操e作t的im实e际is执t行a时ke间n占b总y时da间t的a比pre-filtering.
And GP例U很小ca，n大o部n分ly时a间c用ce于le处ra理te数s据m预a过ll滤p。roGpPoUr可tio加n速o的f部d分at占a比, 小so，t所h以e加effect is not
obvious.速效果不明显。
160
140
120
100
80
60
40
20
0
0.35GB X0.70GB X1.05GB X 1.4GB X 1.75GB X
0.24GB 0.48GB 0.72GB 0.96GB 1.2GB
图5-2 TPC-H数据集上与CPU处理嵌套循环连接对比
5.2.3 人工合成数据集上与CPU处理嵌套循环连接对比实验
基于在TPC-H数据集上本文所(cid:6656)算法加速效果不明显，为此我们在人工合
成数据集上进行了另一次实验。在人工合成的数据集中，每个连接键值所对应
的元组个数较TPC-H数据集多。为保证实验结果可靠性，我们在图5-2所示实
验数据集的基础上对连接键的分布进行了修改，具体来说就是将连接键值除以
一个正整数，从而增加了每个连接键值对应的元组个数。基于原始TPC-H数据
集上连接键值的分布十分均匀，因此人工合成的数据集连接键分布同样均匀，
且除了连接键值不同以外，两个数据集其它所有性质均相同，保证了实验结果
的可靠性。从图5-3可以看出，在人工合成的数据集上，相比于CPU，采用GPU
能获得接近1倍的加速效果。从图5-1与图5-2可以看出，本文所(cid:6656)方法相比
于传统的GPU算法，能适用于更加大的数据集。由于人工合成的数据集中，连
接键的取值范围要远远小于TPC-H数据集，因此在GPU算法中，α取值较小
时即可获得良好的加速效果，本次实验中α取值5。
- 41 -
s/emit CPU
HADOOP+GPU
data size
Figure12: ComparisonofnestedloopjoinwithCPUonTPC-Hdataset
5.1.3. Comparison of Nested Loop Join with CPU on Synthetic Data Set
BasedontheunobviouseffectoftheproposedalgorithmontheTPC-Hdata
set,thesyntheticdatasetismadeforanotherexperiment. Inthesyntheticdata
set, the number of tuples corresponding to each join key is more than that of
the TPC-H data set. To ensure the reliability of the experimental results, the
distribution of join keys has been modified on the basis of the experimental
data set shown in Figure 12. Specifically, dividing the join key by a positive
integer, the number of tuples corresponding to each join key increases. As can
be seen from Figure 13, in the synthetic dataset, compared to the CPU, using
theGPUcangetnearly2timesthespeedup. ThroughFigure16andFigure12,
the proposed method can be applied to larger data sets than traditional GPU
algorithms. Because the join key value range in the synthetic data set is much
18

哈尔滨工业大学工学硕士学位论文
5.2.4 α取值对嵌套循环连接算法执行效率的影响
|     |     | 算法5中α取值会影响到算法整体的并行数，为弄清α取值对算法的性能 |     |     |     |     |     |     |     |     |
| --- | --- | -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
影响，我们通过改变α的值，来观测算法的执行时间。本次实验采用TPC-H数
据集，数据集大小分别为1.75GB以及1.2GB。实验结果如图5-4所示，当α取
|     | 值较小时，随着 |     | α 增加，算法的执行时间逐渐减少；当 |     |     |     | α增大到一定程度时， |     |     |     |
| --- | ------- | --- | ------------------ | --- | --- | --- | ---------- | --- | --- | --- |
smaller than that in the TPC-H dataset, when the value of α is small, a good
随着α取值的增大，算法的执行时间也随之而增加。之所以会出现这样的现象
| speedup | can | be obtained. |     | Therefore, | α is | 5 in this | experiment. |     |     |     |
| ------- | --- | ------------ | --- | ---------- | ---- | --------- | ----------- | --- | --- | --- |

300
250
200
s/emit
CPU
150
HADOOP+GPU
100
50
0
|     |     |     | 0.35GB X0.70GB X1.05GB X |        | 1.4GB X       | 1.75GB X |     |     |     |     |
| --- | --- | --- | ------------------------ | ------ | ------------- | -------- | --- | --- | --- | --- |
|     |     |     | 0.24GB                   | 0.48GB | 0.72GB 0.96GB | 1.2GB    |     |     |     |     |
哈尔滨工业大学工学硕士学位论文
data size

接算法以及CPU实现进行对比实验，观测实验结果。同时也在人工合成的数据
|     | Figure13:                                  |     | ComparisonofnestedloopjoinwithCPUonsyntheticdataset |     |     |     |     |     |     |     |
| --- | ------------------------------------------ | --- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|     | 集上，观测本文所(cid:6656)出方法的执行效率以及加速效果。并在最后，通过改变 |     | 图5-3 人工合成数据集上与CPU处理嵌套循环连接对比                         |     |     |     |     |     | α   |     |
值，观测α取值对本文所(cid:6656)出的加速哈希连接操作算法的影响。若无特殊说明，
本小节实验α取值均为10000。  是因为，当α取值较小时，reducer的个数较多，从而导致算法整体的线程个数
| 5.1.4. | Effect                                                                                  | of α | on the | Execution | Efficiency | of    | Nested | Loop Join     |              |     |
| ------ | --------------------------------------------------------------------------------------- | ---- | ------ | --------- | ---------- | ----- | ------ | ------------- | ------------ | --- |
|        | th5.e3.a1l与go单rit一hmGPrUef下pr哈efi希lte连ri接ng对al比go实, 超出了GPU设备的总线程数。部分任务需要等待其它任务完成之后，才能分配 |      |        |           |            | 验th e |        |               |              |     |
|        | In                                                                                      |      |        |           |            | value | of     | α will affect | the parallel |     |
到空闲线程执行任务。等待的时间加上线程多次创建所引入的额外开销，使得
number of the algorithm. To clarify the influence of α on the performance of
the algorithm,   当α取值较少时，算法的执行时间较高。当α值增加到一定程度时，算法的总 图5-5所示为本文所(cid:6656)出的处理哈希连接算法与传统的基于GPU上的哈希 we can observe the execution time of the algorithm by changing
连接算法对比实验结果。从图中可以看出，当数据集较小时，本文所(cid:6656)出的方 线程个数小于GPU设备总线程数时，随着α的不断增加，reducer个数减少，
the value of α. This experiment uses a TPC-H data set, the data set size is
从而导致算法总线程数降低，每个线程处理的数据量增加，因此算法执行时间
1.75GB 法 an 相 d 比 1 于 .2 传 G 统 B 的 . TGPhUe 算 ex 法 p ， e 效 rim 率 e 更 n 低 ta 。 l 当 re 数 su 据 lt 集 s 增 ar 大 e 时 sh ， o 本 w 文 n 所 in (cid:6656)出 Fi 的 gu 方 r 法 e 效 14. When α
| small,果w要i优th于t传he统的incGrePaUse算o法f。α本, | 会随着 | α   | 增加而增加。从图 | 5-4 次th实e验ex结e果cu显ti示on，本tim文所e | 可以看出，在本次实验所采用的数据集上，α |     | (cid:6656)of出t的he方a法lg能o取rit得hm1 |     |           |     |
| --------------------------------------- | --- | --- | -------- | ------------------------------- | -------------------- | --- | -------------------------------- | --- | --------- | --- |
| is                                      |     |     |          |                                 |                      |     |                                  |     | decreases |     |
graduall倍y.的W加速he效n果α。i ncreases 取值在100至250之间时，算法会获得较为理想的执行效果。
|      |                 |     |     | to a | certain | extent, | with | the increase | of α | value, |
| ---- | --------------- | --- | --- | ---- | ------- | ------- | ---- | ------------ | ---- | ------ |
| time | also increases. |     |     |      |         |         |      |              |      |        |
5.3哈希连接
|     |     | 本小节主要介绍加速哈希连接算法的实验。通过与单一GPU上实现哈希连 | 160 |     |     |     |     |     |     |     |
| --- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
155
150
|     |     | s/emit | 145 |     | - 42 -  |     |     |     |     |     |
| --- | --- | ------ | --- | --- | ------- | --- | --- | --- | --- | --- |
140
135
130
125
120
|     |     |     | 50  | 100 | 150 | 200 | 250 | 300 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
α取值

|     | Figure14: |     | Effectofαontheexecutionefficiencyofnestedloopjoin 图5-4 α取值对嵌套循环连接执行时间影响  |     |     |     |     |     |     |     |
| --- | --------- | --- | ------------------------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
160
|     | When the | value | of α is | small, | the number | of  | Reducers | is larger, | resulting | in  |
| --- | -------- | ----- | ------- | ------ | ---------- | --- | -------- | ---------- | --------- | --- |
140
the total number of threads of the algorithm beyond the total number of GPU
120
devices. Some tasks 100 need to wait for the other tasks to be completed before
s/emit
80
they can be assigned to the free thread to perform the task. The waiting time
|     |     |     | 60  |     |     |     |     | GPU |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
plus the overhead of creating multiple threads make the execution time of the
|     |     |     | 40  |     |     |     |     | HADOOP+GPU |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- |
algorithmhigherwhenthevalueofαisless. 20 Whenthevalueofαislargeenough
0
that the number of total threads of the algorithm is smaller than that of the
|     |     |     | 350MB X525MB X700MB X875MB X |     |     | 1050MB |     |     |     |     |
| --- | --- | --- | ---------------------------- | --- | --- | ------ | --- | --- | --- | --- |
total number of GPU 240MB devices, 360MB with 480MB the 600MB increase X 720MB of α, the number of Reducer
decreasdaeta osizfethe
decreases. It leads to the total number of threads, the increase

   图5-5与单一GPU下哈希连接对比
19
|     |     |     |     |     | - 43 -  |     |     |     |     |     |
| --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- |

of data amount processed by each thread, so the algorithm execution time will
increasewiththeincreaseofα. ItcanbeseenfromFigure14thatthealgorithm
哈尔滨工业大学工学硕士学位论文
will obtain the ideal execution effect when the value of α is between 100 and
250. 接算法以及CPU实现进行对比实验，观测实验结果。同时也在人工合成的数据
集上，观测本文所(cid:6656)出方法的执行效率以及加速效果。并在最后，通过改变 α
5.2. Has值h，观Jo测inα取值对本文所(cid:6656)出的加速哈希连接操作算法的影响。若无特殊说明，
本小节实验α取值均为10000。
This section focuses on the experiment of accelerating the hash join algo-
rithm. T5.h3e.1e与xp单er一imGePnUta下l r哈es希ult连s接ar对e o比b实se验rv ed by comparing the hash algorithm
with the single GPU and the CPU implementation. And in the synthetic data
set, the effi图cie5n-5c所y示an为d本t文h所e(cid:6656)sp出e的ed处u理p哈of希t连h接e算pr法o与po传se统d的m基e于thGoPdU上ca的n哈b希e observed.
Addition连a接lly算,法by对比ch实a验ng结in果g。t从he图α中可va以lu看e,出t，hi当s数se据ct集io较n小o时bs，e本rv文es所t(cid:6656)he出i的nfl方uence of α
on the a法lg相or比it于hm传.统I的f tGhPeUre算i法s，n效o率sp更ec低ia。l当in数s据tr集uc增ti大on时,，α本v文al所ue(cid:6656)i出s的10方0法00效.
果要优于传统的 GPU 算法。本次实验结果显示，本文所(cid:6656)出的方法能取得 1
5.2.1. C倍om的加pa速ri效so果n。o f Hash Join with Single GPU
In this experiment, the value of α is 10000, which is much larger than the
α when dealing with nested loop join. This is because the hash join calcula-
tion task is much16s0maller than the nested loop join, so larger amounts of data
155
processed in each15R0educer can give full play to the advantages of GPU.
As can be see1n45 from the Figure 15, when the data set is small, the pro-
140
posedmethodhas135lowerefficiency, comparedtothetraditionalGPUalgorithm.
When the data se1t30size is good enough, the proposed method is better than the
125
traditional GPU1a2l0gorithm. The experimental results show that the proposed
methodcanachieve2tim50esthe1s00peedu1p50overt2r0a0dition25a0lone,3w00hichmeansunder
thesame acceleratingcondition ofGPU,the proposed methodismore efficient.
图5-4 α取值对嵌套循环连接执行时间影响
图5-5与单一GPU下哈希连接对比
- 43 -
s/emit
α取值
160
140
120
100
80
60
40
20
0
350MB X525MB X700MB X875MB X 1050MB
240MB 360MB 480MB 600MB X 720MB
s/emit
GPU
HADOOP+GPU
data size
Figure15: ComparisonofhashjoinwithsingleGPU
5.2.2. Comparison of Hash Join with CPU on TPC-H Data Set
When the data set is small, most of the time is used to process the data
pre-filter. When the data pre-filter takes longer than the time it reduces on
the actual join operation, the total time will increase. While as the data set
continues to increase, the method proposed in this paper will achieve better
results, because the data pre-filter is less time-consuming. By comparing with
Figure 16, it is found that traditional GPU processing algorithms can handle
20

哈尔滨工业大学工学硕士学位论文
larger am不o会un出ts现o在f最d终at结a果w中h的en数h据a过nd滤li掉n，g实ha际s执h行jo连in接s.操作T的hi数s 据is远b远ec小au于s原e始when the
data set i数s据la集rg。e,经t过he预h过a滤sh后j，oi实n际al处go理ri连th接m操作pe的rf时or间m大an大c降e低is，m但u预ch过h滤ig过h程er同than the
nested loo样p引j入oi了n,额s外o的it时ca间n开h销an。d因le此m，o当re数d据a集ta比s较et小s.时，预过滤所带来的增益效
10
9
8
7
6
s/emit
5
|     |     | 4   |     |     | GPU        |     |
| --- | --- | --- | --- | --- | ---------- | --- |
|     |     | 3   |     |     | HADOOP+GPU |     |
2
1
0
|     |     | 2MB X 4MB X | 8MB X | 12MB X | 16MB X |     |
| --- | --- | ----------- | ----- | ------ | ------ | --- |
|     |     | 1MB 2MB     | 4MB   | 6MB    | 8MB    |     |
data size

|     | Figure16: | ComparisonofhashjoinwithCPUonTPC-Hdataset |     |     |     |     |
| --- | --------- | ----------------------------------------- | --- | --- | --- | --- |
图5-1 与单一GPU下嵌套循环连接对比
哈尔滨工业大学工学硕士学位论文

| 5.2.3. | Com5.3p.a3r i人so工n合of成H数a据sh集J上oin与wCiPthUC处P理U哈o希n连Sy接n对th比eti实c验Da ta 果低于其所带来的额外开销，此时本文(cid:6656)出的方法执行时间较长；随着数据集 |     |     |     |     | Set |
| ------ | ------------------------------------------------------------------------------------------------------------------- | --- | --- | --- | --- | --- |
尺寸的增加，当预过滤带来的增益效果超过其所带来的开销时，本文所(cid:6656)出的
| Dataissynthesizedinthesamewayasnestedloops. |     |     |     |     | AsshowninFigure17, |     |
| ------------------------------------------- | --- | --- | --- | --- | ------------------ | --- |
我们同样在人工合成的数据集上对哈希连接算法进行了实验。数据合成的
in the synthetic 方法执行时间明显低于传统方法。本次实验是基于小数据集上进行，是因为嵌 data, the proposed GPU algorithm is better than its CPU
|     | 套循环连接的代价十分庞大，传统的GPU加速方法并不能够有效地支持大数据 方式与嵌套循环连接中相同。如图5-7所示，在人工合成的数据上，本文所(cid:6656) |     |     |     |     |     |
| --- | -------------------------------------------------------------------------------- | --- | --- | --- | --- | --- |
version, with 1.3 times speedup. Hash join speedup is not good as nested loop
出的GPU算法优于其CPU版本，加速效果在0.3倍左右。哈希连接的加速效
join,becausethenestedloopjoinspendsmoretimeintheactualjoinprocessing, 集，因此本次实验选择小数据集进行。
果不如嵌套循环连接，是因为嵌套循环连接中实际连接操作处理时间占比较大，
| so it | can 5.2.2 TPC-H数据集上与CPU处理嵌套循环连接对比实验  be optimized | in the | proportion |     | of large. |     |
| ----- | ------------------------------------------------- | ------ | ---------- | --- | --------- | --- |
可优化的比例大，因此加速效果明显。
200
|     |   图 5-2 | 所示为 TPC-H数据集下本文所(cid:6656)出的加速嵌套循环连接算法 |     |     |     | GPU |
| --- | ------- | -------------------------------------- | --- | --- | --- | --- |
180
|     | 版本与CPU版本对比实验结果。GPU版本中，算法5中α取值为100，而CPU | 160 |     |     |     |     |
| --- | -------------------------------------- | --- | --- | --- | --- | --- |
140
|     | 版本中α取值为1，从而保证了CPU版本的执行效率最佳，使得对比实验结果 | 120 |     |     |            |     |
| --- | ----------------------------------- | --- | --- | --- | ---------- | --- |
|     | s/emit                              |     |     |     | CPU        |     |
|     | 更加公正。除α取值不同以外，GPU版本与CPU版本的执行流程完全一样， | 100 |     |     |            |     |
|     |                                     | 80  |     |     | HADOOP+GPU |     |
60
仅仅是执行实际连接操作的设备不同，保证了本次实验结果的可靠性。从图5-2
40
|     | 可以看出，相比于CPU实现，用GPU实现本文所(cid:6656)出的嵌套循环连接算法并 | 20  |     |     |     |     |
| --- | -------------------------------------------- | --- | --- | --- | --- | --- |
0
无明显的加速效果。这是因为本文所(cid:6656)出的算法的CPU版本中，在第二轮任务
|     |                                      | 0.35GB X0.70GB X1.05GB X |           | 1.4GB X | 1.75GB X |           |
| --- | ------------------------------------ | ------------------------ | --------- | ------- | -------- | --------- |
|     | 的reduce阶段，只有具有相同连接键值的元组才会传递到相同的      | 0.24GB 0.48GB            | 0.72GB    | 0.96GB  | 1.2GB    | reducer中。 |
|     | 而本次实验采用的是TPC-H数据集，连接键的分布较为均匀，每个连接键值仅 |                          | data size |         |          |           |

|     | Figure17: | ComparisonofhashjoinwithCPUonsyntheticdataset |     |         |     |     |
| --- | --------- | --------------------------------------------- | --- | ------- | --- | --- |
|     |           | 图5-7 人工合成数据集上与CPU处理哈希连接对比                     |     | - 40 -  |     |     |
5.3.4 α取值对哈希连接算法执行效率的影响
| 5.2.4. | Effect of α | on Execution | Efficiency |     | of Hash Join |     |
| ------ | ----------- | ------------ | ---------- | --- | ------------ | --- |
  为研究α取值变化对本文所(cid:6656)出的哈希连接算法执行效果的影响，我们同
ThisexperimentusesTPC-Hdataset,thedatasetsizeis1.75GBand1.2GB.
样进行了实验，通过改变α取值，观测实验结果。图5-8所示为，当α取值变
Similarly, α is changed in the experiment to observe its effect on algorithm
化时，本文所(cid:6656)出的哈希连接算法执行时间的变化情况。由图5-8可以看出当
performance. Figure18showsthechangeintheexecutiontimeofthehashjoin
α取值较小时，随着α变大，算法的执行时间明显减少。这与嵌套循环连接中
algorithmproposedinthispaperwhenthevalueofαchanges. Whenαissmall,
|     | 原因相同，当 | α 取值过小时，算法总线程个数超过了 |     |     | GPU 设备的线程总数， |     |
| --- | ------ | ------------------ | --- | --- | ------------ | --- |
the execution time of the algorithm decreases obviously as α becomes larger.
因此执行时间较长。由于哈希连接的计算任务远远小于嵌套循环连接，因此当
When the value of α is too small, the total number of threads of the algorithm
α值继续增加时，虽然每个reducer中处理数据量增加，但是总体执行时间并没
exceeds the total number of threads of the GPU device, so the execution time
有显著增加。若α值继续增加，当增加到某种程度时，算法的总体执行时间依
然会随之而增加。本次实验采用TPC-H数据集，数据集大小分别为1.75GB以
及1.2GB。
21
5.3非等值连接
  前两节对等值连接操作进行了实验，本小节对非等值连接进行对比实验。
|     |     |     |     | - 45 -  |     |     |
| --- | --- | --- | --- | ------- | --- | --- |

is longer. Since the computa哈t尔io滨n工a业l大t学a工s学k硕o士f学t位h论e文h  ash join is much smaller than
the nested loop join, the overall execution time does not increase significantly
基于目前尚没有关于GPU加速非等值连接的成果，因此我们选择与CPU进行
when the α value continues to increase, although the amount of data processed
对比。
in each Reducer increases. If the value of α continues to increase to a certain
| extent, | the algorithm’s |     | overall | execution | time | will continue | to increase. |     |     |
| ------- | --------------- | --- | ------- | --------- | ---- | ------------- | ------------ | --- | --- |
144
142
140
138
s/emit
136
|     |     | 134 |     | 哈尔滨工业大学工学硕士学位论文  |     |     |     |     |     |
| --- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- |
132
基于目前尚没有关于GPU加速非等值连接的成果，因此我们选择与CPU进行
130
对比。
128
126
|     |     |     | 50  | 100 | 150 | 200 250 | 300 |     |     |
| --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- |
α取值
|     |           | 144 |                                             |     |     |     |     |     |     |
| --- | --------- | --- | ------------------------------------------- | --- | --- | --- | --- | --- | --- |
|     | Figure18: |     | Effectofαontheexecutionefficiencyofhashjoin |     |     |     |     |     |     |
142
图5-8 α取值对哈希连接执行时间影响
140
|     |   与等值连接不同的是，非等值连接的选择率要很高，因此非等值连接结果 |     |     |     |     |     |     |     |     |
| --- | ---------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
138
| 5.3. Theta | 的尺寸要大于输入数据数个数量级，本次实验基于小数据集上进行。实验结果 Join | s/emit 136 |     |     |     |     |     |     |     |
| ---------- | --------------------------------------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
134
| This | 如图5-9所示，从图中可以看出，本文所(cid:6656)出的GPU上的基于Hadoop的非等 section | compares | the | theta joins. |     | Because there | is no available | mature |     |
| ---- | ------------------------------------------------------- | -------- | --- | ------------ | --- | ------------- | --------------- | ------ | --- |
132
GPU accelerating130theta 值连接算法执行效果要优于其CPU版本，加速效果大约在1倍左右。为了保证  join, this experiment compares with the CPU. This
experiment is ba1s2e8d on a small dataset. In order to ensure the validity of
16 126
the experimental results, implementation details are exactly as described in
|                                                                      |        | 14  | 50  | 100 | 150 | 200 | 250 300 |     |     |
| -------------------------------------------------------------------- | ------ | --- | --- | --- | --- | --- | ------- | --- | --- |
| Algorithm                                                            | 3      | 12  |     |     | α取值 |     |         |     |     |
| Incontrasttotheequijoin,thethetajoinhasahighselectivity, sothesizeof | s/emit | 10  |     |     |     |     |         |     |     |
8
the theta join results is la图rg5e-r8 αt取ha值n对t哈h希e连m接a执gn行i时tu间d影e响o f in p u t data. The results of
|     |     | 6   |     |     |     |     | C P U |     |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- |
the expe rim与en等t值a连re接s不ho同w的n是in，F非i等gu值re连1接9的. 4 选It择ca率n要b很e高se，e因n此HfAr非DoOm等OP值+tGhP连Ue接fi结gu果re that the
2
Hadoop-的b尺as寸ed要t大h于et输a入jo数in据a数lg个or数it量hm级，o本n次th实e验G基P于U小is数b据et集te上r进th行a。n实it验s结CP果U version,
0
and the如sp图ee5-d9u所p示is，a从b图ou中t可tw以i看ce出a，s本m文u所ch(cid:6656)a出s的thGePUla上tt的er基, 500 X 500 1000 X 1500 X 2000 X 2500 X 于whHiacdhoomp的ea非n等s under the
|                                           |     |     | 1000 | 1500     | 2000                                           | 2500 |     |        |     |
| ----------------------------------------- | --- | --- | ---- | -------- | ---------------------------------------------- | ---- | --- | ------ | --- |
| same ac值ce连le接ra算ti法ng执c行o效nd果it要io优n于o其f |     |     |      | GCPPUU版, | 本th，e加p速ro效po果s大ed约m在e1th倍o左d右is。m为o了r保e证effi  |      |     | cient. |     |
data size/row

16
|     |                                       | 14  | 图5-9 输出结果的非等值连接实验  |     |     |     |     |     |     |
| --- | ------------------------------------- | --- | ------------------ | --- | --- | --- | --- | --- | --- |
|     | 实验结果公正性，CPU版本与GPU版本的算法实现细节完全按照算法7所述。  | 12  |                    |     |     |     |     |     |     |
s/emit 10
|     |   我们同样在较大数据集上进行了实验。由于当数据集较大时，连接结果超   | 8   |     |     |     |     |            |     |     |
| --- | ------------------------------------ | --- | --- | --- | --- | --- | ---------- | --- | --- |
|     | 出了内存容量，因此我们不对连接结果进行存储。实验结果如图5-10所示，当 | 6   |     |     |     |     | CPU        |     |     |
|     |                                      | 4   |     |     |     |     | HADOOP+GPU |     |     |
2
|     |     |     |     |     | - 46 -  |     |     |     |     |
| --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- |
0
|     |     | 500 X 500 | 1000 X | 1500 X | 2000 X | 2500 X |     |     |     |
| --- | --- | --------- | ------ | ------ | ------ | ------ | --- | --- | --- |
|     |     |           | 1000   | 1500   | 2000   | 2500   |     |     |     |
data size/row

|     |     | Figure19: | Comparisonofthetajoinonsmalldataset |     |     |     |     |     |     |
| --- | --- | --------- | ----------------------------------- | --- | --- | --- | --- | --- | --- |
图5-9 输出结果的非等值连接实验
实验结果公正性，CPU版本与GPU版本的算法实现细节完全按照算法7所述。
| We  | also experimented |     | on  | larger | datasets. | Since | the join results | are | out of |
| --- | ----------------- | --- | --- | ------ | --------- | ----- | ---------------- | --- | ------ |
memory   when 我们同样在较大数据集上进行了实验。由于当数据集较大时，连接结果超 the data set is large, we do not store the results. As shown in
出了内存容量，因此我们不对连接结果进行存储。实验结果如图5-10所示，当
Figure 20, when the data set is large, GPU implementation is still better than
| the CPU | implementation. |     |     |     |         |     |     |     |     |
| ------- | --------------- | --- | --- | --- | ------- | --- | --- | --- | --- |
|         |                 |     |     |     | - 46 -  |     |     |     |     |
22

哈尔滨工业大学工学硕士学位论文
数据集较大时，GPU实现依然优于CPU实现。
25
20
15
10
5
0
50000 X 100000 X150000 X200000 X250000 X
50000 100000 150000 200000 250000
图5-10 不输出结果的非等值连接实验
5.4本章小结
本章节对本文所(cid:6656)出的嵌套循环连接、哈希连接以及非等值连接进行了对
比实验。通过与现有GPU加速成果对比，本文(cid:6656)出的嵌套循环连接以及哈希连
接方法在处理效率以及可扩展性上均有明显的改进。同时，在与CPU算法进行
对比实验时，发现本文所(cid:6656)出的处理等值连接方法在TPC-H数据集上并没有取
得明显的加速效果，但在人工合成的数据集上，取得了明显的加速效果，加速
效果在0.5倍到1倍之间。本章节同样对算法5中α取值对执行效果的影响进
行了实验，发现当α过小或者过大时，均会降低算法性能。最后，我们对非等
值连接进行了对比实验，得出结论GPU处理非等值连接相比于CPU处理加速
1倍左右。
- 47 -
s/emit
CPU
HADOOP+GPU
data size/row
Figure20: Comparisonofthetajoinonsmalldataset
6. Conclusion
ThispaperfocusesonHadoop-basedjoinoperationaccelerationtasksonim-
age processors (GPUs). GPU was originally developed as an image processing,
and nowadays, more and more GPU applications appear in general comput-
ing tasks, such as machine learning, data mining and other fields. Based on the
GPU’spowerfulcomputingpowerandhighparallelism,thereisalotofresearch
focused on using it to speed up database operations. In the field of the modern
database, the join operation as a computationally intensive task is the main
problem.
InresearchresultsofexistingGPUacceleratingjoinoperations,althoughthe
useofitsstrongparallelismsignificantlyincreasestheefficiencyofjoinexecution,
it is not good because of the limited storage resources of the GPU device and
the limited functionality of the universal programming language CUDA. The
existing research results are based on smaller data sets, and therefore can not
be applied to the practical application on a large scale.
Basedonthisidea,thedistributedcomputingplatformHadoopiscombined
with the GPU, by referring to the idea of a CPU filtering join algorithm. By
initially filtering the raw data table through the first round of the Map-Reduce
task at the CPU, it will filter the tuple that does not appear in the results, and
only send the connectable tuples to the GPU device for actual join operations.
By reducing the amount of data actually processed, it is possible to reduce the
utilization of the storage space on the device while improving the efficiency of
the algorithm execution so that it can handle a larger amount of data. At the
same time, it is possible to estimate the number of join results more accurately
withoutintroducingadditionaloverhead,toallocateaccuratestorageinadvance
and reduce the storage space occupancy rate. In addition to the equi join, this
article is the first to use the GPU to accelerate the theta join operation, which
still uses the combination of Hadoop and GPU.
The followings are the conclusions:
• TheproposedalgorithmismoreefficientthantheexistingsingleGPUde-
vice,anditcanbeappliedtothelargerdataset. ComparedwiththeCPU
implementation,theGPUalgorithmproposedinthispaperhasnoobvious
23

speedup on the dataset with fewer key numbers and fewer tuples corre-
sponding to each join key. However, the algorithm proposed in this paper
can achieve 2 times the speedup on a dataset with more corresponding
tuples.
• The accelerating hash join algorithm proposed in this paper can achieve
2 times the speedup, compared with the existing GPU acceleration hash
join. Similarly, the GPU implementation of the algorithm proposed in
thispaperhasnoobviousspeedupcomparedtotheCPUimplementation,
when the number of connected keys is large, but each join key value cor-
respondstoafewtuples. Whenthenumberofcorrespondingtuplesisbig
enough, GPU implementation can get 1.3 times the speedup.
• In this paper, the theta join processing algorithm, compared to the CPU
implementation, GPU implementation can get 2 times the speedup.
Compared with the existing research results, the research content of this paper
has achieved the following innovative achievements:
• This article is the first to use the filter join algorithm on the GPU to
deal with the equi join operation. One round of Map-Reduce filters out
non-connectable tuples and sends only connectable tuples to the GPU
device. By reducing the processing time of the actual join operation and
the occupancy rate of the device memory, it can handle more data.
• The proposed method can accurately estimate the size of the equi join
result without introducing additional overhead, and allocate the appro-
priate storage space for the result, making the GPU storage space more
efficient, more suitable for large-scale data sets.
• Among the existing GPU accelerating equi join operation, this article is
the first to have an experiment on a larger data set (GB level).
• This article is the first to use GPU to accelerate theta join operations.
Although there are a lot of research results on GPU accelerating join, these
results are not enough to be applied to the commercial database system. So
the future work should continue to conduct in-depth research, including the
following:
• The future work should use multiple GPU devices to deal with large
datasets on the join operation, in a distributed architecture. Although in
thisarticleHadoopandGPUwerecombined,becauseoflimitedresources,
theexperimentisnotcompletedinthereallargedataset. Futureresearch
should deal with TB-level datasets on multiple GPU devices.
• This paper only implements the join operation of two tables. Future re-
search work should include more complicated join operations, such as ac-
celerating multi-table join and similarity join.
24

Acknowledgement. ThispaperwaspartiallysupportedbyNSFCgrantU1509216,61472099,
National Sci-Tech Support Plan 2015BAH10F01, the Scientific Research Foun-
dation for the Returned Overseas Chinese Scholars of Heilongjiang Province
LC2016026 and MOE-Microsoft Key Laboratory of Natural Language Process-
| ing and Speech, | Harbin | Institute | of  | Technology. |     |     |     |     |     |
| --------------- | ------ | --------- | --- | ----------- | --- | --- | --- | --- | --- |
7. References
References
[1] J. F. Gantz, The diverse and exploding digital universe, An Idc White
| Paper Retrieved. |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[2] J.Kru¨ger,C.Kim,M.Grund,N.Satish,D.Schwalb,J.Chhugani,H.Plat-
| tner, P.                                                      | Dubey, | A. Zeier, | Fast  | updates | on read-optimized |     |     | databases | using |
| ------------------------------------------------------------- | ------ | --------- | ----- | ------- | ----------------- | --- | --- | --------- | ----- |
| multi-core                                                    | cpus,  | PVLDB     | 5 (1) | (2011)  | 61–72.            |     |     |           |       |
| URL http://www.vldb.org/pvldb/vol5/p061_jenskrueger_vldb2012. |        |           |       |         |                   |     |     |           |       |
pdf
[3] B. W. Low, B. Y. Ooi, C. S. Wong, Scalability of database bulk inser-
| tion with         | multi-threading, |              | in:         | J. M.     | Zain, | W. M.    | B. W.             | Mohd,    | E. El-    |
| ----------------- | ---------------- | ------------ | ----------- | --------- | ----- | -------- | ----------------- | -------- | --------- |
| Qawasmeh          | (Eds.),          | Software     | Engineering |           | and   | Computer |                   | Systems  | - Sec-    |
| ond International |                  | Conference,  |             | ICSECS    | 2011, | Kuantan, | Pahang,           |          | Malaysia, |
| June 27-29,       | 2011,            | Proceedings, |             | Part III, | Vol.  | 181      | of Communications |          | in        |
| Computer          | and              | Information  | Science,    | Springer, |       | 2011,    | pp.               | 151–162. | doi:      |
10.1007/978-3-642-22203-0_14.
| URL https://doi.org/10.1007/978-3-642-22203-0_14 |     |     |     |     |     |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[4] J. Zhou, K. A. Ross, Implementing database operations using SIMD in-
| structions, | in:      | M. J. Franklin, |     | B. Moon,      | A.    | Ailamaki   |       | (Eds.),       | Proceed- |
| ----------- | -------- | --------------- | --- | ------------- | ----- | ---------- | ----- | ------------- | -------- |
| ings of     | the 2002 | ACM SIGMOD      |     | International |       | Conference |       | on Management |          |
| of Data,    | Madison, | Wisconsin,      |     | June 3-6,     | 2002, | ACM,       | 2002, | pp.           | 145–156. |
doi:10.1145/564691.564709.
| URL http://doi.acm.org/10.1145/564691.564709 |     |     |     |     |     |     |     |     |     |
| -------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[5] B. Zhang, X. Wang, Z. Zheng, The optimization for recurring queries in
| big data | analysis | system | with | mapreduce, | Future |     | Generation |     | Computer |
| -------- | -------- | ------ | ---- | ---------- | ------ | --- | ---------- | --- | -------- |
Systems.
[6] V. Silva, J. Leite, J. J. Camata, D. de Oliveira, A. L. Coutinho, P. Val-
| duriez,         | M. Mattoso, | Raw               | data | queries  | during | data-intensive |     | parallel    | work- |
| --------------- | ----------- | ----------------- | ---- | -------- | ------ | -------------- | --- | ----------- | ----- |
| flow execution, |             | Future Generation |      | Computer |        | Systems        | 75  | (Supplement | C)    |
| (2017)          | 402 – 422.  |                   |      |          |        |                |     |             |       |
[7] D. J. DeWitt, DIRECT - A multiprocessor organization for supporting
| relational                                  | database | management                   |     | systems, | IEEE | Trans. | Computers |     | 28 (6) |
| ------------------------------------------- | -------- | ---------------------------- | --- | -------- | ---- | ------ | --------- | --- | ------ |
| (1979)                                      | 395–406. | doi:10.1109/TC.1979.1675379. |     |          |      |        |           |     |        |
| URL https://doi.org/10.1109/TC.1979.1675379 |          |                              |     |          |      |        |           |     |        |
25

[8] J. Teubner, R. Mu¨ller, G. Alonso, Frequent item computation on a chip,
IEEE Trans. Knowl. Data Eng. 23 (8) (2011) 1169–1181. doi:10.1109/
TKDE.2010.216.
URL https://doi.org/10.1109/TKDE.2010.216
[9] L. Woods, J. Teubner, G. Alonso, Real-time pattern matching with fpgas,
in: S. Abiteboul, K. B¨ohm, C. Koch, K. Tan (Eds.), Proceedings of the
27th International Conference on Data Engineering, ICDE 2011, April 11-
16, 2011, Hannover, Germany, IEEE Computer Society, 2011, pp. 1292–
1295. doi:10.1109/ICDE.2011.5767937.
URL https://doi.org/10.1109/ICDE.2011.5767937
[10] J. Singaraju, A. Thamarakuzhi, J. A. Chandy, Active storage networks:
Using embedded computation in the network switch for cluster data pro-
cessing, Future Generation Computer Systems 45 (Supplement C) (2015)
149 – 160. doi:https://doi.org/10.1016/j.future.2014.10.020.
URL http://www.sciencedirect.com/science/article/pii/
S0167739X14002143
[11] A´.B.Hern´andez,M.S.Perez,S.Gupta,V.Munt´es-Mulero,Usingmachine
learningtooptimizeparallelisminbigdataapplications,FutureGeneration
Computer Systems.
[12] M.Singh,B.Leonhardi,IntroductiontotheIBMnetezzawarehouseappli-
ance, in: J. W. Ng, C. Couturier, M. Litoiu, E. Stroulia (Eds.), Center for
Advanced Studies on Collaborative Research, CASCON ’11, Toronto, ON,
Canada, November 7-10, 2011, IBM / ACM, 2011, pp. 385–386.
URL http://dl.acm.org/citation.cfm?id=2093965
[13] J. Do, Y. Kee, J. M. Patel, C. Park, K. Park, D. J. DeWitt, Query
processing on smart ssds: opportunities and challenges, in: K. A. Ross,
D. Srivastava, D. Papadias (Eds.), Proceedings of the ACM SIGMOD
International Conference on Management of Data, SIGMOD 2013, New
York, NY, USA, June 22-27, 2013, ACM, 2013, pp. 1221–1230. doi:
10.1145/2463676.2465295.
URL http://doi.acm.org/10.1145/2463676.2465295
[14] N. Devarajan, S. Navneeth, S. Mohanavalli, GPU accelerated relational
hash join operation, in: International Conference on Advances in Comput-
ing, Communications and Informatics, ICACCI 2013, Mysore, India, Au-
gust 22-25, 2013, IEEE, 2013, pp. 891–896. doi:10.1109/ICACCI.2013.
6637294.
URL https://doi.org/10.1109/ICACCI.2013.6637294
[15] T. Kaldewey, G. M. Lohman, R. Mu¨ller, P. B. Volk, GPU join processing
revisited, in: S. Chen, S. Harizopoulos (Eds.), Proceedings of the Eighth
International Workshop on Data Management on New Hardware, DaMoN
2012, Scottsdale, AZ, USA, May 21, 2012, ACM, 2012, pp. 55–62. doi:
26

10.1145/2236584.2236592.
URL http://doi.acm.org/10.1145/2236584.2236592
[16] J.He, M.Lu, B.He, Revisitingco-processingforhashjoinsonthecoupled
| CPU-GPU | architecture, |     | PVLDB | 6 (10) | (2013) | 889–900. |     |     |     |
| ------- | ------------- | --- | ----- | ------ | ------ | -------- | --- | --- | --- |
URL http://www.vldb.org/pvldb/vol6/p889-he.pdf
[17] Y.Yuan,R.Lee,X.Zhang,Theyinandyangofprocessingdatawarehous-
| ing queries | on  | GPU | devices, | PVLDB | 6 (10) | (2013) 817–828. |     |     |     |
| ----------- | --- | --- | -------- | ----- | ------ | --------------- | --- | --- | --- |
URL http://www.vldb.org/pvldb/vol6/p817-yuan.pdf
[18] M. Pietron, P. Russek, K. Wiatr, Accelerating select where and select join
| queries | on a GPU, | Computer |     | Science | (AGH) | 14 (2) | (2013) | 243–252. | doi: |
| ------- | --------- | -------- | --- | ------- | ----- | ------ | ------ | -------- | ---- |
10.7494/csci.2013.14.2.243.
URL https://doi.org/10.7494/csci.2013.14.2.243
[19] R. Rui, H. Li, Y. Tu, Join algorithms on gpus: A revisit after seven years,
in: 2015IEEEInternationalConferenceonBigData,BigData2015,Santa
| Clara, | CA, USA, | October |     | 29 - November | 1,  | 2015, IEEE, |     | 2015, pp. | 2541– |
| ------ | -------- | ------- | --- | ------------- | --- | ----------- | --- | --------- | ----- |
2550. doi:10.1109/BigData.2015.7364051.
URL https://doi.org/10.1109/BigData.2015.7364051
[20] K. Angstadt, E. Harcourt, A virtual machine model for accelerating re-
| lational     | database   | joins            | using | a general     | purpose      | GPU,             | in:  | L. T. | Watson,  |
| ------------ | ---------- | ---------------- | ----- | ------------- | ------------ | ---------------- | ---- | ----- | -------- |
| J. Weinbub,  | M.         | Sosonkina,       |       | W. I. Thacker | (Eds.),      | Proceedings      |      | of    | the Sym- |
| posium       | on High    | Performance      |       | Computing,    |              | HPC 2015,        | part | of    | the 2015 |
| Spring       | Simulation | Multiconference, |       |               | SpringSim    | ’15, Alexandria, |      | VA,   | USA,     |
| April 12-15, | 2015,      | SCS/ACM,         |       | 2015,         | pp. 127–134. |                  |      |       |          |
URL http://dl.acm.org/citation.cfm?id=2872615
[21] G. Zhou, G. Wang, GBFSJ: bloom filter star join algorithms on gpus, in:
12thInternationalConferenceonFuzzySystemsandKnowledgeDiscovery,
FSKD2015,Zhangjiajie,China,August15-17,2015,IEEE,2015,pp.2427–
2431. doi:10.1109/FSKD.2015.7382334.
URL https://doi.org/10.1109/FSKD.2015.7382334
[22] M. S. H. Cruz, Y. Kozawa, T. Amagasa, H. Kitagawa, GPU acceleration
| of set similarity |        | joins,      | in:      | Q. Chen,   | A. Hameurlain, |         | F. Toumani,  |           | R. Wag- |
| ----------------- | ------ | ----------- | -------- | ---------- | -------------- | ------- | ------------ | --------- | ------- |
| ner, H.           | Decker | (Eds.),     | Database | and        | Expert         | Systems | Applications |           | - 26th  |
| International     |        | Conference, |          | DEXA 2015, | Valencia,      | Spain,  |              | September | 1-4,    |
2015,Proceedings,PartI,Vol.9261ofLectureNotesinComputerScience,
| Springer, | 2015, | pp. 384–398. |     | doi:10.1007/978-3-319-22849-5_26. |     |     |     |     |     |
| --------- | ----- | ------------ | --- | --------------------------------- | --- | --- | --- | --- | --- |
URL https://doi.org/10.1007/978-3-319-22849-5_26
[23] J. Myung, J. Shim, J. Yeon, S. Lee, Handling data skew in join algorithms
| using mapreduce, |     | Expert | Syst. | Appl. | 51 (2016) | 286–299. | doi:10.1016/j. |     |     |
| ---------------- | --- | ------ | ----- | ----- | --------- | -------- | -------------- | --- | --- |
eswa.2015.12.024.
URL https://doi.org/10.1016/j.eswa.2015.12.024
27

[24] T. Yuan, Z. Liu, H. Liu, Optimizing hash join with mapreduce on multi-
core cpus, IEICE Transactions 99-D (5) (2016) 1316–1325.
URL http://search.ieice.org/bin/summary.php?id=e99-d_5_1316
[25] M. A. H. Hassan, M. Bamha, F. Loulergue, Handling data-skew effects
in join operations using mapreduce, in: D. Abramson, M. Lees, V. V.
Krzhizhanovskaya,J.J.Dongarra,P.M.A.Sloot(Eds.),Proceedingsofthe
International Conference on Computational Science, ICCS 2014, Cairns,
Queensland, Australia, 10-12 June, 2014, Vol. 29 of Procedia Computer
Science,Elsevier,2014,pp.145–158.doi:10.1016/j.procs.2014.05.014.
URL https://doi.org/10.1016/j.procs.2014.05.014
[26] T.Csar, R.Pichler, E.Sallinger, V.Savenkov, Usingstatisticsforcomput-
ing joins with mapreduce, in: A. Cal`ı, M. Vidal (Eds.), Proceedings of the
9th Alberto Mendelzon International Workshop on Foundations of Data
Management, Lima, Peru, May 6 - 8, 2015., Vol. 1378 of CEUR Workshop
Proceedings, CEUR-WS.org, 2015.
URL http://ceur-ws.org/Vol-1378/AMW_2015_paper_13.pdf
[27] F. N. Afrati, N. Stasinopoulos, J. D. Ullman, A. Vasilakopoulos, Sha-
resskew: An algorithm to handle skew for joins in mapreduce, CoRR
abs/1512.03921. arXiv:1512.03921.
URL http://arxiv.org/abs/1512.03921
[28] P.Larson,E.N.Hanson,S.L.Price,ColumnarstorageinSQLserver2012,
IEEE Data Eng. Bull. 35 (1) (2012) 15–20.
URL http://sites.computer.org/debull/A12mar/apollo.pdf
[29] I.K.Koumarelas,A.Naskos,A.Gounaris,Binarytheta-joinsusingmapre-
duce: Efficiency analysis and improvements, in: K. S. Candan, S. Amer-
Yahia, N. Schweikardt, V. Christophides, V. Leroy (Eds.), Proceedings of
the Workshops of the EDBT/ICDT 2014 Joint Conference (EDBT/ICDT
2014), Athens, Greece, March 28, 2014., Vol. 1133 of CEUR Workshop
Proceedings, CEUR-WS.org, 2014, pp. 6–9.
URL http://ceur-ws.org/Vol-1133/paper-02.pdf
[30] A.Okcan,M.Riedewald,Processingtheta-joinsusingmapreduce,in: T.K.
Sellis, R. J. Miller, A. Kementsietsidis, Y. Velegrakis (Eds.), Proceedings
of the ACM SIGMOD International Conference on Management of Data,
SIGMOD 2011, Athens, Greece, June 12-16, 2011, ACM, 2011, pp. 949–
960. doi:10.1145/1989323.1989423.
URL http://doi.acm.org/10.1145/1989323.1989423
[31] M. Penar, A. Wilczek, The design of the efficient theta-join in map-reduce
environment, in: S. Kozielski, D. Mrozek, P. Kasprowski, B. Malysiak-
Mrozek,D.Kostrzewa(Eds.),BeyondDatabases,ArchitecturesandStruc-
tures. Advanced Technologies for Data Mining and Knowledge Discov-
ery - 12th International Conference, BDAS 2016, Ustron´, Poland, May
28

| 31 - June                                            | 3,  | 2016, | Proceedings, |     | Vol. 613 | of  | Communications |              | in Com- |
| ---------------------------------------------------- | --- | ----- | ------------ | --- | -------- | --- | -------------- | ------------ | ------- |
| puterandInformationScience,Springer,2016,pp.204–215. |     |       |              |     |          |     |                | doi:10.1007/ |         |
978-3-319-34099-9_15.
URL https://doi.org/10.1007/978-3-319-34099-9_15
[32] K. Yan, H. Zhu, Two mrjs for multi-way theta-join in mapreduce, in:
M.Pathan,G.Wei,G.Fortino(Eds.),InternetandDistributedComputing
Systems-6thInternationalConference,IDCS2013,Hangzhou,China,Oc-
tober28-30,2013,Proceedings,Vol.8223ofLectureNotesinComputerSci-
| ence, Springer, |     | 2013, | pp.321–332. |     | doi:10.1007/978-3-642-41428-2_26. |     |     |     |     |
| --------------- | --- | ----- | ----------- | --- | --------------------------------- | --- | --- | --- | --- |
URL
https://doi.org/10.1007/978-3-642-41428-2_26
[33] X. Zhang, L. Chen, M. Wang, Efficient multi-way theta-join processing
| using mapreduce, |     | PVLDB | 5   | (11) | (2012) | 1184–1195. |     |     |     |
| ---------------- | --- | ----- | --- | ---- | ------ | ---------- | --- | --- | --- |
URL http://vldb.org/pvldb/vol5/p1184_xiaofeizhang_vldb2012.
pdf
[34] C. Zhang, J. Li, L. Wu, M. Lin, W. Liu, SEJ: an even approach to multi-
| way theta-joins      |     | using  | mapreduce, |          | in: J. Liu, | J.   | Chen, G.    | Xu (Eds.), | 2012    |
| -------------------- | --- | ------ | ---------- | -------- | ----------- | ---- | ----------- | ---------- | ------- |
| Second International |     |        | Conference |          | on Cloud    | and  | Green       | Computing, | CGC     |
| 2012, Xiangtan,      |     | Hunan, | China,     | November |             | 1-3, | 2012, IEEE, | 2012,      | pp. 73– |
80. doi:10.1109/CGC.2012.9.
URL https://doi.org/10.1109/CGC.2012.9
[35] C. Zhang, J. Li, L. Wu, M. Lin, W. Liu, SEJ: an even approach to multi-
| way theta-joins      |     | using  | mapreduce, |          | in: J. Liu, | J.   | Chen, G.    | Xu (Eds.), | 2012    |
| -------------------- | --- | ------ | ---------- | -------- | ----------- | ---- | ----------- | ---------- | ------- |
| Second International |     |        | Conference |          | on Cloud    | and  | Green       | Computing, | CGC     |
| 2012, Xiangtan,      |     | Hunan, | China,     | November |             | 1-3, | 2012, IEEE, | 2012,      | pp. 73– |
80. doi:10.1109/CGC.2012.9.
URL
https://doi.org/10.1109/CGC.2012.9
[36] D. R. Augustyn, L. Warchal, Gpu-accelerated method of query selectiv-
| ity estimation |                                                         | for non | equi-join | conditions      |     | based                  | on discrete | fourier | trans- |
| -------------- | ------------------------------------------------------- | ------- | --------- | --------------- | --- | ---------------------- | ----------- | ------- | ------ |
| form,in:       | N.Bassiliades,M.Ivanovic,M.Kon-Popovska,Y.Manolopoulos, |         |           |                 |     |                        |             |         |        |
| T.Palpanas,    | G.Trajcevski,                                           |         |           | A.Vakali(Eds.), |     | NewTrendsinDatabaseand |             |         |        |
InformationSystemsII-Selectedpapersofthe18thEastEuropeanConfer-
| ence on        | Advances | in        | Databases | and      | Information                       |             | Systems   | and Associated |         |
| -------------- | -------- | --------- | --------- | -------- | --------------------------------- | ----------- | --------- | -------------- | ------- |
| Satellite      | Events,  | ADBIS     | 2014      | Ohrid,   | Macedonia,                        |             | September | 7-10,          | 2014    |
| Proceedings    | II,      | Vol.      | 312 of    | Advances | in                                | Intelligent | Systems   | and            | Comput- |
| ing, Springer, |          | 2014, pp. | 215–227.  |          | doi:10.1007/978-3-319-10518-5_17. |             |           |                |         |
URL https://doi.org/10.1007/978-3-319-10518-5_17
29