Fast Approximate Similarity Join in Vector Databases

JIADONG XIE, The Chinese University of Hong Kong, China
JEFFREY XU YU, The Chinese University of Hong Kong, China
YINGFAN LIU∗, Xidian University, China

Recent advancements in deep learning, particularly in embedding models, have enabled the effective represen-
tation of various data types such as text, images, and audio as vectors, thereby facilitating semantic analysis.
A large number of massive vector datasets are maintained in vector databases. Approximate similarity join is
a core operation in vector database systems that joins two datasets, and outputs all pairs of vectors from the
two datasets, if the distance between such a pair of two vectors is no more than a specified value. Existing
state-of-the-art approaches for approximate similarity join are selection-based such that they treat each data
point in a dataset as an individual query point to search data points by an approximate range query in another
dataset. Such methods do not fully capitalize on the inherent properties of the join operation itself. In this
paper, we propose a new join algorithm, SimJoin. Our join algorithm aims to boost join processing efficiency
by leveraging relationships between partial join results (e.g., join windows). In brief, our join algorithm
accelerates the join processing to process a join window by utilizing the join windows from the processed data
points. Then, we discuss optimizing join window order to minimize join costs. In addition, we discuss how to
support 𝑘-similarity join, and how to maintain proximity graph index based on 𝑘-similarity join. Extensive
experiments on real-world and synthetic datasets demonstrate the significant performance superiority of our
proposed algorithms over existing state-of-the-art methods.

CCS Concepts: • Information systems → Information retrieval query processing.

Additional Key Words and Phrases: Approximate Similarity Join, High-Dimensional Vector

ACM Reference Format:
Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu. 2025. Fast Approximate Similarity Join in Vector Databases. Proc.
ACM Manag. Data 3, 3 (SIGMOD), Article 158 (June 2025), 26 pages. https://doi.org/10.1145/3725403

1 Introduction
Recent advances in deep learning, particularly embedding models, have revolutionized the represen-
tation of various data types such as text [32], images [33], audio [6] and graphs [17]. These models
encode data as vectors, capturing crucial information in a high-dimensional space for analysis.
And many large datasets of vectors need to be maintained in the vector databases. Similarity join
is one of the fundamental operations in vector database systems that join two datasets, 𝑋 and
𝑌 , and output all pairs of vectors of 𝑋 and 𝑌 , if they are similar, e.g., the distance between their
vectors is no more than a specified threshold. As an example, auto-tagging [11, 43] is a real-world
application that needs similarity join. Here, auto-tagging is to label a large number of documents
unlabeled based on certain documents labeled. And an unlabeled document can be labeled by the

∗Yingfan Liu is the corresponding author.

Authors’ Contact Information: Jiadong Xie, The Chinese University of Hong Kong, China, jdxie@se.cuhk.edu.hk; Jeffrey Xu
Yu, The Chinese University of Hong Kong, China, yu@se.cuhk.edu.hk; Yingfan Liu, Xidian University, China, liuyingfan@
xidian.edu.cn.

Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee
provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the
full citation on the first page. Copyrights for components of this work owned by others than the author(s) must be honored.
Abstracting with credit is permitted. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires
prior specific permission and/or a fee. Request permissions from permissions@acm.org.
© 2025 Copyright held by the owner/author(s). Publication rights licensed to ACM.
ACM 2836-6573/2025/6-ART158
https://doi.org/10.1145/3725403

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:2

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

label of another labeled document, if the corresponding two document embeddings (vectors) are
sufficiently similar.

In this paper, we study 𝜖-similarity join for two 𝑑-dimensional datasets, 𝑋 and 𝑌 , denoted as
𝑋 (cid:90)𝜖 𝑌 , for 𝑑 > 0. The 𝜖-similarity join finds all pairs of vectors (𝑥𝑖, 𝑦 𝑗 ) from 𝑋 × 𝑌 , if the
distance 𝛿 (𝑥𝑖, 𝑦 𝑗 ), for 𝑥𝑖 ∈ 𝑋 and 𝑦 𝑗 ∈ 𝑌 , is no more than the given parameter 𝜖. Due to the curse of
dimensionality [21], the exact 𝜖-similarity join is computationally intensive [23, 24, 36]. We focus on
the approximate 𝜖-similarity join in this paper, which has not been well studied, whereas the 𝑘-NN
(nearest neighbor) search and 𝑘-ANN (approximate 𝑘-NN) search have been extensively studied.
In general, 𝜖-similarity join, 𝑋 (cid:90)𝜖 𝑌 , can be done by 𝑘-NN/𝑘-ANN search if it takes every vector
𝑥𝑖 ∈ 𝑋 as a query vector to search its nearest neighbors in the dataset 𝑌 , as a 𝜖-range query. We call
them a selection-based approach for 𝜖-similarity join. The existing state-of-the-art approaches for
approximate 𝜖-similarity join are all selection-based methods [44, 46, 51]. Such existing approaches
focus on optimizing the join processing time by refining the selection operations, like skipping
tuples with zero or fewer join results [46], bypassing the limitations of a top 𝑘-only interface to
support 𝜖-range search [51]. However, these approaches do not fully leverage the inherent property
of the 𝜖-similarity join. That is, they do not utilize the join results from processed data points to
accelerate the processing time of other data points that have not been processed, which is the focus
we study in this paper.

The main contributions of this work are summarized below. ➊ We propose a new 𝜖-similarity
join algorithm for 𝑋 (cid:90)𝜖 𝑌 based on two key issues in join processing, which are join window sliding
and join window order selection. Here, a join window is the join results in 𝑌 that are 𝜖-similar to a
data point 𝑥 in 𝑋 . Join window sliding is to leverage the join window results of some processed
data points to accelerate the join results for other data points. And join window order selection is
to determine the processing order of join windows to slide, in order to minimize the overall join
processing time. ➋ To allow join window sliding, we discuss the continuous sliding from a data
point to another adjacent data point in 𝑑-dimensional space. Such adjacent data points are difficult
to handle in 𝑑-dimensional space, as there are 2𝑑 directions to slide and there is no easy way to
slide in order. We discuss how to capture such adjacent data points in 𝑑-dimensional space, and
how to maintain such adjacent data points in an adjacent graph to be constructed. Furthermore, we
discuss the differences between the adjacency issue and 𝑘-NN based similarity, and we show that
the probability of using a proximity graph (e.g., 𝑘-NN based graph) as an approximate adjacent
graph in practice. ➌ We give the optimal solution to determine the join window order selection,
for 𝑋 (cid:90)𝜖 𝑌 . To find such optimal join window order, we show how to estimate the join window
sliding cost on 𝑌 based on the information we have on 𝑋 . We give our efficient approach to find the
optimal solution. ➍ Based on our 𝜖-similarity join algorithm, SimJoin, we further discuss how we
support 𝑘-similarity join, and how we maintain a proximity graph index based on the 𝑘-similarity
join algorithm we present. ➎ We report on extensive experiments on both real-world and synthetic
datasets. (a) In general, SimJoin demonstrates significant performance improvements, achieving
reductions in join time of over 1 order of magnitude compared to state-of-the-art methods for
approximate similarity joins, along with superior join result quality. Moreover, it achieves more
than 2 orders of magnitude reduction in join time compared to the state-of-the-art approach for
exact similarity joins with less than 1% loss in join results. (b) Regarding index maintenance, our
approach accelerates index maintenance significantly, consuming less peak memory, and enhancing
index quality for 𝑘-approximate nearest neighbor search, compared to the state-of-the-art methods.
The paper is organized as follows. We discuss 𝜖-similarity join and its key issues in Section 2. In
Section 3, we discuss the main difficulties for selection-based approaches to support 𝜖-similarity
join by finding nearest neighbors in one dataset for any point in another dataset. In Section 4,

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:3

we propose a new approximate 𝜖-similarity join algorithm that is based on join window sliding
and join window order selection. Sections 5 and 6 delve into the specifics of addressing the two
issues, join window sliding and join window order selection, respectively. In Section 7, we show
that our techniques can be used to support 𝑘-similarity join, and to support maintenance of 𝑘-ANN
based proximity graph indices. We conduct extensive experiments to confirm the effectiveness and
efficiency of our approach in Section 8. We discuss the related works in Section 9, and conclude
our work in Section 10.

2 The 𝜖-Similarity Join
Given two sets of points, 𝑋 = {𝑥1, 𝑥2, · · · , 𝑥𝑛 } and 𝑌 = {𝑦1, 𝑦2, · · · , 𝑦𝑚 }, in Euclidean 𝑑-dimensional
space, denoted as R𝑑 , for 𝑑 > 0, the 𝜖-similarity join 𝑋 (cid:90)𝜖 𝑌 is defined as 𝑋 (cid:90)𝜖 𝑌 = {(𝑥𝑘, 𝑦𝑙 ) ∈
𝑋 ×𝑌 | 𝛿 (𝑥𝑘, 𝑦𝑙 ) ≤ 𝜖}, where 𝛿 (𝑥𝑘, 𝑦𝑙 ) is 𝐿2 norm (i.e., Euclidean distance) between 𝑥𝑘 ∈ 𝑋 and 𝑦𝑙 ∈ 𝑌 ,
and 𝜖 is a user-given threshold where 𝜖 > 0. The 𝜖-similarity join, 𝑋 (cid:90)𝜖 𝑌 , can also be formalized
based on join windows. Let 𝐽𝑖 be the join window for 𝑥𝑖 ∈ 𝑋 such that 𝐽𝑖 = {𝑦𝑙 ∈ 𝑌 | 𝛿 (𝑥𝑖, 𝑦𝑙 ) ≤ 𝜖}.
𝑋 (cid:90)𝜖 𝑌 = (cid:208)𝑥𝑖 ∈𝑋 ({𝑥𝑖 } × 𝐽𝑖 ). We also refer the 𝜖-similarity join, as 𝜖-similarity self-join, if the
two given datasets are identical.

As the exact 𝜖-similarity join is time-consuming [23, 24, 36] due to the curse of dimensionality [21],
in this paper, we study an approximate 𝜖-similarity join algorithm, and its quality is measured by
the average recall and average precision. Here, let ˜𝐽𝑖 be the results from an approximate 𝜖-similarity
| ˜𝐽𝑖 ∩𝐽𝑖 |
join algorithm and 𝐽𝑖 = {𝑦𝑙 ∈ 𝑌 | 𝛿 (𝑥𝑖, 𝑦𝑙 ) ≤ 𝜖} , the average recall is defined as 1
| 𝐽𝑖 |
and the average precision is defined as 1

|𝑋 | · (cid:205)𝑥𝑖 ∈𝑋

.

|𝑋 | · (cid:205)𝑥𝑖 ∈𝑋

| ˜𝐽𝑖 ∩𝐽𝑖 |
| ˜𝐽𝑖 |

In the design of an approximate 𝜖-similarity join algorithm, in this work, we focus on two key
issues, namely, join window sliding and join window order selection. The join window, 𝐽𝑖 ⊆ 𝑌
of 𝑥𝑖 ∈ 𝑋 is a 𝑑-ball centered at 𝑥𝑖 with a radius of 𝜖 in the 𝑑-dimensional space. Suppose 𝐽𝑖 has
been processed for a given 𝑥𝑖 . Join window sliding refers to the process of sliding the join window
𝐽𝑖 to the join window 𝐽𝑗 to be processed next for 𝑥 𝑗 . And join window order selection is how to
select such 𝑥 𝑗 among the points in 𝑋 that have not yet been processed, in order to minimize the
join processing cost.

Here, we discuss the join cost of 𝑋 (cid:90)𝜖 𝑌 . Let ℵ be the join window order over 𝑋 such that
ℵ = ⟨(𝜅1, 𝑥1), (𝜅2, 𝑥2), · · · , (𝜅𝑛, 𝑥𝑛)⟩, where a pair of (𝜅𝑖, 𝑥𝑖 ) indicates that the join window, 𝐽𝑖 , to be
processed next for 𝑥𝑖 is slide from the join window represented by 𝜅𝑖 ∈ 𝑋 . Regarding 𝜅𝑖 , there are
two cases. One is that 𝜅𝑖 represents 𝑥 𝑗 for 1 ≤ 𝑗 < 𝑖 in ℵ, and the other is 𝜅𝑖 = ∅ as it is possible that
the cost of finding 𝐽𝑖 for 𝑥𝑖 by an individual 𝜖-range search is smaller if it does not slide from any
join window found already. Note that 𝜅1 = ∅. The total join cost for 𝑋 (cid:90)𝜖 𝑌 is defined as follows
given a join window order ℵ:

𝐶 (𝑋 (cid:90)𝜖 𝑌 ) =

(cid:26) 𝑐𝜖 (𝑥𝑖 )
𝑐𝜅 (𝜅𝑖, 𝑥𝑖 )

∑︁

𝑥𝑖 ∈𝑋

(∅, 𝑥𝑖 ) ∈ ℵ
otherwise

(1)

where 𝑐𝜖 (𝑥𝑖 ) is the cost of processing an 𝜖-range search to find 𝐽𝑖 for 𝑥𝑖 , and 𝑐𝜅 (𝜅𝑖, 𝑥𝑖 ) is the cost of
finding 𝐽𝑖 by sliding from the join window represented by 𝜅𝑖 . The problem to be studied is how to
reduce such join processing cost.

The two issues can be easily handled for 𝑋 (cid:90)𝜖 𝑌 when 𝑋 and 𝑌 are in 𝑑-dimensional space
for 𝑑 = 1. We show its join algorithm in Algorithm 1. In Algorithm 1, both 𝑋 and 𝑌 are sorted in
ascending order. For 𝑥𝑖 in the ascending order, it finds 𝐽𝑖 by finding the leftmost and rightmost
boundary point in 𝐽𝑖 , denoted as 𝑙 (𝐽𝑖 ) and 𝑟 (𝐽𝑖 ), following the linear order of 𝑌 . The join window 𝐽𝑖
forms a continuous interval in 1-dimensional space. The continuous interval is formed by sliding in
𝑌 from a point 𝑦𝑝 to another point 𝑦𝑞 on the condition that 𝑦𝑝 and 𝑦𝑞 are adjacent points such that

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:4

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

Algorithm 1: Join1D (𝑋, 𝑌, 𝜖)
Input

: two 1-dimensional datasets 𝑋 = {𝑥1, · · · , 𝑥𝑛 } and 𝑌 = {𝑦1, · · · , 𝑦𝑚 } in ascending order and a
parameter 𝜖
Output : the result of 𝑋 (cid:90)𝜖 𝑌
𝑋𝑌 ← ∅; 𝑙 ← 1; 𝑟 ← 0;
for each 𝑥𝑖 from 1 to 𝑛 in the ascending order do
while 𝑙 ≤ 𝑚 and 𝑦𝑙 < 𝑥𝑖 − 𝜖 do 𝑙 ← 𝑙 + 1;
while 𝑟 + 1 ≤ 𝑚 and 𝑦𝑟 +1 ≤ 𝑥𝑖 + 𝜖 do 𝑟 ← 𝑟 + 1;
𝐽𝑖 ← {𝑦𝑙 , · · · , 𝑦𝑟 };
if 𝑙 ≤ 𝑟 then 𝑋𝑌 ← 𝑋𝑌 ∪ ({𝑥𝑖 } × 𝐽𝑖 );

1

2

3

4

5

6

7

return 𝑋𝑌

there is no 𝑦𝑤 between 𝑦𝑝 and 𝑦𝑞. The following is obvious. That is, 𝑥𝑖 ≤ 𝑥𝑖+1 implies 𝑙 (𝐽𝑖 ) ≤ 𝑙 (𝐽𝑖+1)
and 𝑟 (𝐽𝑖 ) ≤ 𝑟 (𝐽𝑖+1). The best to slide join window is to slide from the join window 𝐽𝑖 to the join
window 𝐽𝑖+1, and the join window order is to select 𝑥𝑖+1 from 𝑥𝑖 . The time complexity of Algorithm 1
is in 𝑂 (𝑛 + 𝑚).

The issue of join window sliding is that the continuous in join window sliding in 𝑑-dimensional
space for 𝑑 > 1 becomes challenging. First, there are 2𝑑 directions to slide from a join window 𝐽𝑖
to another join window 𝐽𝑗 . In other words, two join windows, 𝐽𝑖 and 𝐽𝑗 , or the two 𝑑-balls, may
overlap in any of 2𝑑 ways. Second, the adjacent points, 𝑦𝑝 and 𝑦𝑞 in 𝑌 , are arbitrary as there are
2𝑑 directions to slide, and there is no easy way to slide in order. In this paper, we propose a new
efficient approximate 𝜖-similarity join algorithm with high quality of the join results.

3 Selection-based Approaches
The 𝜖-similarity join, 𝑋 (cid:90)𝜖 𝑌 , can be processed using the state-of-the-art 𝑘-ANN (Approximate
Nearest Neighbor) search. That is, for every point 𝑥𝑖 ∈ 𝑋 , it issues an approximate 𝜖-range
query [46, 51] to find its join window 𝐽𝑖 in 𝑌 . In [51], it presents a method to deal with 𝜖 as a filter
on 𝑘-ANN search. In [46], it utilizes learning techniques to predict the number of join results for
each data point, enabling the skipping of those with zero or fewer results. By such a selection-based
approach, there are no issues on join window sliding and join window selection, because each of
join window is treated individually. We discuss its main problem to slide exact/approximate join
window, 𝐽𝑖 ⊆ 𝑌 , for 𝑥𝑖 ∈ 𝑋 , below using an example.
Example 3.1: Let 𝑋 = {𝑥1, 𝑥2, 𝑥3} and 𝑌 = {𝑦1, 𝑦2, · · · , 𝑦10}. Fig. 1 shows a 𝑘-NN graph over 𝑌 for
𝑘 = 2, where a point is connected to its 1-NN and 2-NN, as indicated by blue solid/dashed edges.
The 𝑋 points are not explicitly shown in Fig. 1. Instead, we show every join window 𝐽𝑖 for 𝑥𝑖 in 𝑋 ,
where 𝑥𝑖 is the center of the corresponding 𝑑-ball, illustrated by a circle in 2-dimensional space.
Here, 𝐽1 = {𝑦8, 𝑦9, 𝑦10}, 𝐽2 = {𝑦2, 𝑦3}, and 𝐽3 = {𝑦3, 𝑦4, 𝑦5}. As shown in Fig. 1, the two clusters of 𝑌
points, namely, {𝑦1, · · · , 𝑦7} and {𝑦8, 𝑦9, 𝑦10}, are not connected over the 𝑘-NN graph. To enforce all
points connected in a graph, in 𝑘-ANN graph (𝑘 = 2), it adds some red edges to make it connected
and prunes some dashed blue edges to make the graph small for efficiency.

As shown in Example 3.1 with Fig. 1, first, on the 𝑘-NN graph, the join window 𝐽1 cannot slide
to the join window 𝐽2, as there is no point in 𝐽1 that has an blue edge to a point in 𝐽2. Suppose that
there is 𝑥4 in 𝑋 , and its join window 𝐽4 = {𝑦8, 𝑦1}, where 𝑦1 and 𝑦8 are not connected in the 𝑘-NN
graph. The selection-based approaches start the search from a single entry point, which results
in the inability to simultaneously locate both 𝑦1 and 𝑦8, since they belong to separate connected
components. Second, on the 𝑘-ANN graph with red/blue solid edges, consider finding 𝐽2 for 𝑥2

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:5

Fig. 1. 𝑘-NN/𝑘-ANN graph

Fig. 2. An adjacent graph

from 𝐽3. Staring from 𝑦2 and 𝑦3, it finds 𝑦4 included in 𝐽2, then it finds that 𝑦6 cannot be in 𝐽2,
and accordingly, it stops search and misses 𝑦5 which should be in 𝐽2. In short, it is difficult for a
selection-based 𝑘-NN or 𝑘-ANN approach to ensure high recall for 𝜖-similarity join.

4 A New 𝜖-Similarity Join Algorithm
In this section, we address the two key issues: join window sliding (Section 4.1) and join window
order selection (Section 4.2). Subsequently, we integrate the techniques proposed to present our
similarity join algorithm, SimJoin (Section 4.3).

4.1 Join Window Sliding
First, we define adjacent points, 𝑦 and 𝑦′, in a 𝑑-dimensional dataset 𝑌 . The definition applies to
any 𝑑-dimensional spaces.
Definition 4.1: [Adjacent points] For any point set 𝑌 in a 𝑑-dimensional space for 𝑑 > 0, two
points 𝑦 and 𝑦′ in 𝑌 are adjacent if there exists a 𝑑-ball such that 𝑦 and 𝑦′ are two points on the
boundary of 𝑑-ball and there is no any point 𝑦′′ in 𝑌 inside 𝑑-ball.

A point 𝑦 in 𝑌 may have multiple adjacent points, for instance, as illustrated in Fig. 2, 𝑦2 is

adjacent to 𝑦1, 𝑦3 and 𝑦5.
Definition 4.2: [Continuous Window] A join window 𝐽 is a continuous window if any two
points, 𝑦𝑝 and 𝑦𝑞, in 𝐽 are connected by a sequence of pairs of adjacent points.

Definition 4.3: [Continous Sliding] A join window 𝐽𝑖 slides to a join window 𝐽𝑗 in a continuous
manner, if there are two adjacent points, 𝑦𝑝 and 𝑦𝑞, for 𝑦𝑝 ∈ 𝐽𝑖 and 𝑦𝑞 ∈ 𝐽𝑗 .

From a different view, a point 𝑦𝑝 sliding to its adjacent point 𝑦𝑞 may cause a join window slides
to a new join window. Note that the 𝑑-ball in Definition 4.1 is used to define two adjacent points
in a 𝑑-dimensional space, and is different from the 𝑑-ball that corresponds to a join window or a
continuous join window. It is important to note that the continous sliding ensures that we do not
miss any points in 𝑌 for 𝑋 (cid:90)𝜖 𝑌 .
Example 4.1: Reconsider Example 3.1. Fig. 2 shows points in 𝑌 , where there is a line between two
adjacent points. With the adjacent points in Fig. 2, the join window 𝐽1 can slide to 𝐽3 as 𝑦8 ∈ 𝐽1 and
𝑦1 ∈ 𝐽3 are adjacent points, and the join window 𝐽3 can slide to 𝐽2. All the three join windows are
continuous windows. There are no missing points in any join windows.
Similarity vs Adjacency: First, regarding the 𝑘-NN based similarity and adjacency in one 𝑑-
dimensional space (e.g., 𝑌 ), the adjacency defined is different from the 𝑘-NN based similarity. It
does not necessarily mean that two adjacent points are similar, and it does not necessarily mean
two similar points are adjacent. Consider Example 4.1 and its Fig. 2. for 𝑦1, its 1-NN, 2-NN, and
3-NN are 𝑦2, 𝑦3, and 𝑦5, respectively. 𝑦3 is more similar to 𝑦1 than 𝑦5. But, 𝑦3 is not adjacent point

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

!!!"!#!$!%"!""!&!'!$(!)!*"$!!!""!"""#!#"$"%"&"#'"(")"*158:6

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

of 𝑦1 but 𝑦5 is. This is because 𝑦1 can slide to 𝑦5 directly, but 𝑦1 cannot slide to 𝑦3 without passing
through 𝑦2. Second, regarding 𝑋 (cid:90)𝜖 𝑌 in two 𝑑-dimensional spaces, if 𝑦𝑝 and 𝑦𝑞 are adjacent in 𝑌 ,
it means that it is possible that there exists a point 𝑥𝑖 in 𝑋 , which takes 𝑦𝑝 and 𝑦𝑞 as its 1-NN and
2-NN to join. In general, if 𝑥𝑖 can 𝜖-similarity join 𝑦𝑝 but cannot 𝜖-similarity join its adjacent point
𝑦𝑞, it does not necessarily to explore 𝜖-similarity join between 𝑥𝑖 and any other adjacent points of
𝑦𝑞 in 𝑌 . In other words, if 𝑦𝑝 is in the join window 𝐽𝑖 for 𝑥𝑖 , but its adjacent point 𝑦𝑞 not, then it
does not need to slide from 𝑦𝑞 to any other adjacent points of 𝑦𝑞 in 𝑌 .

Next, we show that a join window, 𝐽𝑖 , for arbitary data point 𝑥𝑖 is continuous window (Defini-

tion 4.2).

First, for an arbitrary 𝑦𝑥 , its 1-NN 𝑦𝑝 and 2-NN 𝑦𝑞 are adjacent since the 𝑑-ball centered at 𝑦𝑥
contains only 𝑦𝑝 and 𝑦𝑞 in it. However, in general, for an arbitrary 𝑦𝑥 , it does not necessarily mean
that (𝑘-1)-NN 𝑦𝑝 and 𝑘-NN 𝑦𝑞 are adjacent from the viewpoint of 𝑦𝑥 . In Fig. 3, suppose 𝑦𝑥 is the
large circle center, the distance between 𝑦𝑖 and 𝑦𝑥 is smaller than the distance between 𝑦 𝑗 and 𝑦𝑥 if
𝑖 < 𝑗, and the adjacent points are connected by blue lines. Here, 𝑦1 and 𝑦2 are adjacent, and are
1-NN and 2-NN of 𝑦𝑥 , whereas 𝑦5 and 𝑦6 are 5-NN and 6-NN of 𝑦𝑥 , but 𝑦5 and 𝑦6 are not adjacent.
For easy discussion, in the following, we use 𝑦𝑝 to show that 𝑦𝑝 is 𝑝-NN of 𝑦𝑥 . To show that a
join window, 𝐽𝑖 is continuous, we show that 𝑦𝑘 is adjacent to one of 𝑦 𝑗 , for 1 ≤ 𝑗 < 𝑘. Consider a
𝑑-ball centered at the segment from 𝑦𝑘 to 𝑦𝑥 , passing through 𝑦𝑘 . By sliding the 𝑑-ball center along
the segment from 𝑦𝑘 towards 𝑦𝑥 , 𝑦 𝑗 is the adjacent to 𝑦𝑘 if 𝑦 𝑗 is the first on such a 𝑑-ball. Note that
𝑦 𝑗 must be closer to 𝑦𝑥 . This is because the sliding 𝑑-ball remains within the large 𝑑-ball centered
at 𝑦𝑥 and passing through 𝑦𝑘 , and 𝑦 𝑗 is on the sliding 𝑑-ball. We explain it using Fig. 3. Consider 𝑦8
in Fig. 3. We show that 𝑦8 must be adjacent to 𝑦5. The segment is depicted as a yellow line between
𝑦8 and 𝑦𝑥 . By sliding a 𝑑-ball (depicted as a red circle), it encounters 𝑦5, and 𝑦5 and 𝑦8 are adjacent.
And 𝑦5 must be closer to 𝑦𝑥 than 𝑦8. This is because the red 𝑑-ball remains within the large 𝑑-ball
centered at 𝑦𝑥 and passing through 𝑦8, and 𝑦5 is on the red 𝑑-ball. This fact implies that the join
window of an arbitrary data point 𝑦𝑥 is continuous.
Lemma 4.1: Given a dataset 𝑌 , regarding an arbitrary data point 𝑦𝑥 , its 𝑘-NN 𝑦𝑘 in 𝑌 are adjacent
with at least one of the 𝑗-NN of 𝑦𝑥 in 𝑌 , for 1 ≤ 𝑗 < 𝑘.

We omit the proof as it can be done as discussed above.
To handle the adjacent points in a 𝑑-dimensional space 𝑌 , we define an adjacent graph, G =

(V, E).
Definition 4.4: [Adjacent Graph] An adjacent graph, G = (V, E) is for a given 𝑑-dimensional
dataset 𝑌 . Here, V is a set of points in 𝑌 , and E is a set of edges where (𝑦𝑝, 𝑦𝑞) ∈ E if 𝑦𝑝 and 𝑦𝑞
are adjacent points by Definition 4.1.

Based on Lemma 4.1, we further show that a join window forms a connected subgraph G𝑖 in G

for 𝑌 , i.e., it is continous window.
Corollary 4.1: For an adjacent graph G of dataset 𝑌 , for an arbitrary data point 𝑦𝑥 , the nodes within
its join window form a connected subgraph in G.
Proof Sketch: It is evident that the join window of 𝑦𝑥 contains its top-𝑘 nearest data points,
{𝑦1, 𝑦2, · · · , 𝑦𝑘 }, in 𝑌 , if 𝛿 (𝑦𝑖, 𝑦𝑥 ) ≤ 𝜖 for 1 ≤ 𝑖 ≤ 𝑘 and 𝛿 (𝑦𝑘+1, 𝑦𝑥 ) > 𝜖. We prove that its top-𝑘 data
points in 𝑌 form a connected subgraph by induction. For the base case where 𝑘 = 2, 1-NN and
2-NN of 𝑦𝑥 are adjacent, hence there is an edge to connect both in G. Suppose that the subgraph for
top-(𝑘-1) nearest data points, {𝑦1, 𝑦2, · · · , 𝑦𝑘 −1} are connected in G. Based on Lemma 4.1, we have

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:7

Fig. 3. Example for adjacency

Fig. 4. Example for similarity join window order

the 𝑘-NN 𝑦𝑘 is connected to one of its 𝑗-NN 𝑦 𝑗 , where 1 ≤ 𝑗 < 𝑘. This implies that the sugraph for
□
the top-𝑘 data points are connected.

As a join window, 𝐽𝑖 , is a connected subgraph, G𝑖 , in G, we can slide a join window 𝐽𝑖 to another

join window 𝐽𝑗 over G by continous sliding (Definition 4.3).
Adjacent Graph Construction: To construct an adjacent graph, G, for a 𝑑-dimensional dataset,
𝑌 , it needs to check if two points, 𝑦𝑝 and 𝑦𝑞, in 𝑌 are adjacent. In doing so, it needs to check if there
exists a 𝑑-ball, 𝐵𝑝𝑞, where 𝑦𝑝 and 𝑦𝑞 are on its boundary and no any points are in the ball. Let the
center of the 𝑑-ball, 𝐵𝑝𝑞, be 𝑦𝑐 , which is located at the bisector hyperplane between 𝑦𝑝 and 𝑦𝑞. As
shown in Fig. 2, 𝑦1 and 𝑦2 are adjacent, because there is a circle (i.e., 2-ball) whose center is on
the perpendicular bisector (the red line between 𝑦1 and 𝑦2) of 𝑦1 and 𝑦2, only 𝑦1 and 𝑦2 are on the
boundary of such circle, and no other points are in the circle. On the other hand, 𝑦1 and 𝑦3 are not
adjacent, because it is impossible to find a circle that does not have 𝑦2 inside the circle. The cost of
checking the existence of a 𝑑-ball for every pair of points is too high.

Here, we construct G by space partitioning. We partition the 𝑑-dimensional space, 𝑌 , into |𝑌 |
subspaces, where each subspace, 𝑆𝑝 , contains only one point, 𝑦𝑝 , in 𝑌 , which implies that any 𝑥𝑖 ∈ 𝑋
point in the subpace, 𝑆𝑝 , will take 𝑦𝑝 as its 1-NN. Such space partitioning is illustrated in Fig. 2 by
the red lines. With such space partitioning, 𝑦𝑝 and 𝑦𝑞 are adjacent points if their subspaces share at
least one point (note that the point mentioned here is an arbitrary data point in the space, which
may not appear in the dataset 𝑌 ). In other words, there must exist a 𝑑-ball centered at the boundary
of the two subspaces for 𝑦𝑝 and 𝑦𝑞. Such space partitioniong is equivalent to the Voronoi diagram
in the hyperspace [13]. Note that a Voronoi diagram partitions space into subspaces that are closer
to each of a specified set of data points. Its dual graph, Delaunay triangulations (DT) [12, 26] can be
identified. For example, In Fig. 2, the DT is shown by the black lines to connect two adjacent points
if their subspaces share at least one point. In this work, we construct G for 𝑌 by constructing DT
over 𝑌 .

4.2 Join Window Order Selection
We have discussed join window sliding in Section 4.1, and give a join cost function (Eq. (1)) for
𝑋 (cid:90)𝜖 𝑌 which we need to minimize. In this section, we delve into the discussion of the join cost
and strategies for minimizing it.

In processing 𝑋 (cid:90)𝜖 𝑌 , suppose that we have processed some points,

−→
𝑋 = {𝑥𝑝, · · · , 𝑥𝑖, · · · , 𝑥𝑞 } in
−→
𝑋 , and the join windows processed are
𝐽 = {𝐽𝑝, · · · , 𝐽𝑖, · · · , 𝐽𝑞 }. To minimize the total join cost is
to minimize the cost of processing a new join window. And the join window order selection is to
−→
𝑋 ) such that the cost to process the next join window 𝐽𝑗 is
select a 𝑥𝑖 ∈

−→
𝑋 to process 𝑥 𝑗 ∈ (𝑋 \

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

!!!"!#!$!%!&!'!(!)!!!"!#"$"""%"&!&!'!(!)!%!$"##$%"$&'&""()$%!$&'&!((*+#+&+"+%+$158:8

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

: two 𝑑-dimensional datasets 𝑋 and 𝑌 , and a parameter 𝜖

Algorithm 2: SimJoin (𝑋, 𝑌, 𝜖)
Input
Output : The 𝜖-similarity join results
𝐺𝐶 ← the complete weighted graph of 𝑋 ; G ← the adjacent graph of 𝑌 ; 𝑦0 ← the entry point of G;
initialize 𝑤 to control the sliding size;
ℵ ←WindowOrder (𝐺𝐶, 𝑦0);
𝑋𝑌 ← ∅;
for each (𝜅𝑖, 𝑥𝑖 ) ∈ ℵ do
if 𝜅𝑖 = 𝑦0 then

1

2

3

4

5

6

7

8

9

𝐽𝑖 ←JoinSlide (G, 𝑦0, 𝑥𝑖, {𝑦0}, 𝜖, 𝑤);

else

𝐽𝑖 ←JoinSlide (G, 𝜅𝑖, 𝑥𝑖, 𝐽𝜅𝑖 , 𝜖, 𝑤);

𝑋𝑌 ← 𝑋𝑌 ∪ 𝐽𝑖 ;

10

return 𝑋𝑌 ;

−→
𝑋 to process 𝑥 𝑗 ∈ (𝑋 \

minimized. It is important to note that a join window is a continuous window. In general, the cost
of sliding from a join window 𝐽𝑖 to a join window 𝐽𝑗 to be processed next is small, if |𝐽𝑖 ∩ 𝐽𝑗 | is large,
because we can process a part of 𝐽𝑗 while sliding from 𝐽𝑖 to 𝐽𝑗 . The difficulty is that we do not know
𝐽𝑗 , and we do not know |𝐽𝑖 ∩ 𝐽𝑗 | before processing 𝐽𝑗 . Hence, we solve this selection problem by
−→
selecting 𝑥𝑖 ∈
𝑋 ) instead. It is important to note that if 𝛿 (𝑥𝑖, 𝑥 𝑗 ) is smaller
than 𝛿 (𝑥𝑙, 𝑥 𝑗 ), it implies that cost of sliding from 𝑥𝑖 to 𝑥 𝑗 is smaller than the sliding from 𝑥𝑙 . In other
−→
words, here, we use 𝐽𝑖 for 𝑥𝑖 to process 𝐽𝑗 for 𝑥 𝑗 if 𝛿 (𝑥𝑖, 𝑥 𝑗 ) is the smallest among all points in
𝑋 . It
is easy to check whether |𝐽𝑖 ∩ 𝐽𝑗 | is empty or not. When |𝐽𝑖 ∩ 𝐽𝑗 | ≠ ∅, we continuously slide from 𝐽𝑖
to 𝐽𝑗 . When |𝐽𝑖 ∩ 𝐽𝑗 | = ∅, we have two choices to slide to 𝐽𝑗 . One is to continuously slide from a
point in 𝐽𝑖 towards 𝐽𝑗 , and the other is to slide from the entry point in the adjacent graph G for 𝑌 ,
i.e., seen finding 𝐽𝑗 as an individual 𝜖-range query. We take the smaller one when |𝐽𝑖 ∩ 𝐽𝑗 | = ∅.

As an example, consider 𝑋 (cid:90)𝜖 𝑌 for 𝑋 = {𝑥1, · · · , 𝑥5} and 𝑌 = {𝑦1, · · · , 𝑦9} as shown in Fig. 4. In
Fig. 4, we show the adjacent graph G on 𝑌 , and 𝑑-balls for the join windows, {𝐽1, · · · , 𝐽5}. Assume
that we have processed 𝐽4 = {𝑦2, 𝑦3, 𝑦4, 𝑦7} for 𝑥4. Suppose 𝑥1 is 1-NN of 𝑥4, and we know 𝐽1 ∩ 𝐽4 ≠ ∅.
Then we continuously slide from 𝑦2 towards 𝑦1 to process 𝐽1 where 𝐽1 = {𝑦1, 𝑦2, 𝑦3}. Next, suppose
𝑥5 is 1-NN of 𝑥1, and we will select 𝐽1 to process 𝐽5 for 𝑥5. By checking points in 𝐽1, we know
that 𝐽1 ∩ 𝐽5 = ∅. Next, we compare 𝛿 (𝑥1, 𝑥5) with 𝛿 (𝑦0, 𝑥5), where 𝑦0 is a fixed entry point in G. If
𝛿 (𝑥1, 𝑥5) < 𝛿 (𝑦0, 𝑥5), we continuously slide from 𝑦1 towards 𝐽5 for 𝑥5. Otherwise, we slide from the
fixed 𝑦0 towards 𝐽5.

We give details of the cost function for 𝐶 (𝑋 (cid:90)𝜖 𝑌 ) (Eq. (1)). Suppose 𝑥 𝑗 is the next point to
−→
process, and 𝑥𝑖 is the point closest to 𝑥 𝑗 among the processed data points, i.e., in
𝑋 . When 𝐽𝑖 ∩ 𝐽𝑗 = ∅,
we estimate the cost by 𝑐𝜖 (𝑥 𝑗 ) = min{𝛿 (𝑥𝑖, 𝑥 𝑗 ), 𝛿 (𝑦0, 𝑥 𝑗 )} where 𝑦0 is a fixed point in G for 𝑌 . When
𝐽𝑖 ∩ 𝐽𝑗 ≠ ∅, we estimate its cost by 𝑐 (𝑥𝑖, 𝑥 𝑗 ) = 𝛿 (𝑥𝑖, 𝑥 𝑗 ).

To solve the join window selection problem, we construct a weighted graph 𝐺𝐶 = (𝑉𝐶, 𝐸𝐶 ). Here,
𝑉𝐶 = 𝑋 ∪ {𝑦0}, and for every edge (𝑢, 𝑣) ∈ 𝐸𝐶 , its weight is 𝛿 (𝑢, 𝑣). The minimum cost of 𝐶 (𝑋 (cid:90)𝜖 𝑌 )
is the cost of the minimum spanning tree (MST) of the weight graph, 𝐺𝐶 , rooted at 𝑦0.

4.3 The Join Algorithm
The 𝜖-similarity join algorithm is given in Algorithm 2, which takes 𝑋 , 𝑌 , and 𝜖 as its inputs. Here,
G is the adjacent graph constructed over 𝑌 , and 𝐺𝐶 is the weighted graph for join window selection
over 𝑋 together with a fixed point 𝑦0 ∈ G. To control the size of the sliding window, a parameter 𝑤

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:9

is given. A higher value of 𝑤 will enhance the quality of join results but at the expense of efficiency.
In Algorithm 2, we identify a join window order, ℵ, by calling WindowOrder (line 2), and we
process 𝑋 (cid:90)𝜖 𝑌 by sliding join windows following the order given in ℵ (lines 4-9).

Note that our join algorithm can be extended to support parallelism. In brief, the join order ℵ we
use for approximate similarity join forms a tree, as discussed in the preceding subsection, where
for every (𝜅𝑖, 𝑥𝑖 ) ∈ ℵ, 𝜅𝑖 is the parent node of 𝑥𝑖 within the tree. Here, a child node can process the
join window sliding, when its parent node completes its join processing. And all the child nodes of
the same parent can be processed in parallel. Based on this, different strategies can be employed for
parallel processing in SimJoin. For example, we can utilize the idea of parallel breadth-first search
to parallelly process the join window sliding within the same layer and subsequently process them
in a layer-wise fashion.

5 Join Window Sliding
We give an adjacent graph G where the edges in G connecting adjacent points in 𝑌 . However, in a
high dimensional space, G becomes a complete graph [19, 26, 38], which implies that all points
can possibly be adjacent in a 𝑑-dimensional space when 𝑑 becomes larger (e.g., 𝑑 > 100). Thus,
it becomes impractical for G to be used to slide over the join windows. As a result, we need to
construct an approximate adjacent graph that can be used in practice.

For an approximate adjacent graph to be constructed, we consider that it is impractical in a system
to maintain two large graph indices. One is based on 𝑘-ANN for 𝑘-ANN search or approximate
𝜖-range query, and the other one is based on adjacency for 𝜖-similarity join. We explore if we can
use one graph to serve all the purposes. In other words, we explore if a proximity graph constructed
for 𝑘-ANN search can be used as an approximate adjacent graph G. The question here is how likely
a pair of near neighbors become adjacent. To answer this question, we consider the adjacency in 𝑌
from the angle of an arbitrary point in 𝑋 . To be more precise, consider the adjacency for 3 data
points, 𝑦𝑢, 𝑦𝑣, and 𝑦𝑤 in 𝑌 , for an arbitrary data point 𝑥𝑞 in 𝑋 . Here, 𝑥𝑞 is a point to join with points
in 𝑌 . Suppose 𝑦𝑢 is the nearest point to 𝑥𝑞, and 𝑦𝑣 has a smaller distance to 𝑦𝑢 in comparison with
the distance between 𝑦𝑤 and 𝑦𝑢. How likely is it for 𝑦𝑢 and 𝑦𝑣 to be adjacent?
Theorem 5.1: Assume that the data points are uniformly distributed in an infinite 𝑑-dimensional
space. Suppose that there are three data points, 𝑦𝑢 𝑦𝑣, and 𝑦𝑤 in 𝑌 , and suppose 𝑦𝑢 is the nearest data
point to a given data point 𝑥𝑞, and 𝛿 (𝑦𝑢, 𝑦𝑣) < 𝛿 (𝑦𝑢, 𝑦𝑤). Then, 𝑦𝑣 has a higher probability to have a
smaller distance to 𝑥𝑞 compared to the distance from 𝑦𝑤 to 𝑥𝑞.
Proof Sketch: Given that 𝑦𝑢 is the nearest data point to 𝑥𝑞, 𝑥𝑞 resides within the region delineated
by the two perpendicular hyperplanes between 𝑦𝑢 and 𝑦𝑣 and between 𝑦𝑢 and 𝑦𝑤, regarding 𝑦𝑢.
This region can be further segmented by the perpendicular hyperplane of 𝑦𝑣 and 𝑦𝑤. If 𝑦𝑣 is closer
to 𝑥𝑞 than 𝑦𝑤, then 𝑥𝑞 lies between the perpendicular hyperplanes of 𝑦𝑢 and 𝑦𝑣, and 𝑦𝑣 and 𝑦𝑤. The
probability of 𝑥𝑞 being in this region is given as ∠𝑢𝑣𝑤/(∠𝑢𝑣𝑤 + ∠𝑢𝑤𝑣), where ∠𝑢𝑣𝑤 is the angle
centered at 𝑣. As 𝛿 (𝑢, 𝑣) < 𝛿 (𝑢, 𝑤), we have ∠𝑢𝑣𝑤 > ∠𝑢𝑤𝑣, which implies that 𝑦𝑣 is more likely to
□
be closer to 𝑥𝑞 than the distance from 𝑦𝑤 to 𝑥𝑞.

Based on Theorem 5.1, because 𝑦𝑢 is the 1-NN to 𝑥𝑞, the data points which have a smaller distance
to 𝑦𝑢 have a higher probability to have a smaller distance to 𝑥𝑞, and in other words, have a higher
probability to become the 2-NN to 𝑥𝑞. Hence, there is a 𝑑-ball centered at 𝑥𝑞 that contain only 𝑦𝑢
and 𝑦𝑣, indicating that 𝑦𝑣 has higher probability to be adjacent with 𝑦𝑢 in the 𝑑-dimensional space,
from the angle of such 𝑥𝑞. Recall that we have shown that for two adjacent points, 𝑦𝑢 and 𝑦𝑣 in 𝑌 ,
there exists an data point that take 𝑦𝑢 and 𝑦𝑣 as their 1-NN and 2-NN. Here, we show that if 𝑦𝑢 and
𝑦𝑣 are 1-NN and 2-NN of a data point in 𝑋 , then it is likely that 𝑦𝑢 and 𝑦𝑣 are adjacent.

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:10

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

Algorithm 3: JoinSlide (G, 𝑥𝑖, 𝑥 𝑗, 𝐽𝑖, 𝜖, 𝑤)
Input

: an adjacent graph G of dataset 𝑌 , two data points 𝑥𝑖, 𝑥 𝑗 in dataset 𝑋 , the join window 𝐽𝑖 of 𝑥𝑖
and two parameters 𝜖, 𝑤

Output : the join window 𝐽𝑗 of 𝑥 𝑗 in 𝑌
𝑄 ← 𝐽𝑖 is a priority queue, sorted in ascending order based on 𝛿 (𝑦𝑝, 𝑥 𝑗 ) for every 𝑦𝑝 ∈ 𝑄;
if 𝛿 (𝑄.𝑡𝑜𝑝 (), 𝑥 𝑗 ) > 𝜖 then

𝑉 𝑖𝑠𝑖𝑡 ← 𝐽𝑖 ;
while 𝑄 is not empty do

if 𝛿 (𝑄.𝑡𝑜𝑝 (), 𝑥 𝑗 ) ≤ 𝜖 then break;
𝑢 ← 𝑄.𝑝𝑜𝑝 ();
for each 𝑣 ∈ 𝑁 G (𝑢) \ 𝑉 𝑖𝑠𝑖𝑡 do
if 𝛿 (𝑣, 𝑥 𝑗 ) < 𝛿 (𝑢, 𝑥 𝑗 ) then

𝑄.𝑝𝑢𝑠ℎ(𝑣); 𝑉 𝑖𝑠𝑖𝑡 ← 𝑉 𝑖𝑠𝑖𝑡 ∪ {𝑣 };

while 𝑄.𝑠𝑖𝑧𝑒 () > 𝑤 do

remove the last element from 𝑄;

if 𝑄 is empty then return 𝐽𝑗 = ∅;

𝐽𝑗 ← {𝑦𝑝 |𝑦𝑝 ∈ 𝑄 ∧ 𝛿 (𝑦𝑝, 𝑥 𝑗 ) ≤ 𝜖} ;
push all elements in 𝐽𝑗 into an empty queue Q;
while Q is not empty do
𝑦𝑝 ← Q.𝑝𝑜𝑝 ();
for each 𝑦𝑞 ∈ 𝑁 G (𝑦𝑝 ) do

if 𝑦𝑞 ∉ 𝐽𝑗 and 𝛿 (𝑦𝑞, 𝑥 𝑗 ) ≤ 𝜖 then
Q.𝑝𝑢𝑠ℎ(𝑣); 𝐽𝑗 ← 𝐽𝑗 ∪ {𝑦𝑞 };

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

return 𝐽𝑗 ;

Based on our analysis, we show that a single proximity graph designed for 𝑘-ANN search can be
utilized for the purpose of 𝜖-similarity join. Suppose there is a 𝑘-ANN graph with 𝑘 = 20, where 𝑦𝑣
is the 20-NN of 𝑦𝑢. This implies that, from the angle of data points in dataset 𝑋 , there might exist a
data point 𝑥𝑞 to join, which takes 𝑦𝑢 and 𝑦𝑣 as its 1-NN and 2-NN.

In the following, the adjacent graph G = (V, E) is constructed as a proximity graph (e.g., 𝑘-ANN
graph). We use 𝑁 G (𝑦𝑢) to indicate the neighbor list of node 𝑦𝑢 in G, i.e., 𝑁 G (𝑦𝑢) = {𝑦𝑣 |(𝑦𝑢, 𝑦𝑣) ∈ E}.
In a proximity graph, a degree constraint of 𝑚 is enforsed to limit the maximum of 𝑚 out-neighbors
for each node in 𝑎𝐺 [14, 28, 30, 34] such that |E | = 𝑂 (𝑛𝑚), where 𝑛 is the size of dataset 𝑌 .

The join window sliding algorithm, named JoinSlide is given in Algorithm 3. It takes 5 inputs,
namely, the adjacent graph G over 𝑌 , two points, 𝑥𝑖, 𝑥 𝑗 in 𝑋 , the join window 𝐽𝑖 for 𝑥𝑖 , together
with two parameters, 𝜖 and 𝑤. The algorithm ouputs the join window 𝐽𝑗 for 𝑥 𝑗 . We discuss two
cases, namely, 𝐽𝑖 ∩ 𝐽𝑗 = ∅ and 𝐽𝑖 ∩ 𝐽𝑗 ≠ ∅.
(i) 𝐽𝑖 ∩ 𝐽𝑗 = ∅: Furthermore, there are two cases, ➊ to slide towards 𝐽𝑗 from 𝐽𝑖 , or ➋ to slide towards
𝐽𝑗 from 𝑦0.

➊ We slide the join window from the nodes in the join window 𝐽𝑖 towards their neighbors, in
order to ultimately locate at least one data point contained in the join window 𝐽𝑗 . Specifically,
we populate the priority queue by adding data points from 𝐽𝑖 , where the priority queue is sorted
according to the ascending order of distance to 𝑥 𝑗 (line 1). For each point at the top of the queue
(lines 4-11), we explore its neighbors in G to find data points to the sliding direction, i.e., closer to 𝑥 𝑗
(lines 7-9). If closer data points are found, they are added to the queue (lines 8-9). This exploration

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:11

process continues until a data point within a distance no greater than 𝜖 from 𝑥 𝑗 is identified (line
5), or the search terminates when there are no closer data points to 𝑥 𝑗 (lines 4, 12). Note that a
parameter 𝑤 is utilized to cap the size of priority queue 𝑄 size (lines 10-11), thereby enhance the
efficiency of join window sliding algorithms by reducing distance computations in practice. After
this process, if there exists at least one data point within a distance not exceeding 𝜖 from 𝑥 𝑗 , we
then turn to process to the case (ii) (lines 13-19).

➋ This is a case of an approximate 𝜖-range query. We slide from an entry point 𝑦0 in G towards
their neighbors, in order to locate at least one data point contained in the join window 𝐽𝑗 in a similar
way as discussed for ➊. This case can be achieved by invoking JoinSlide (G, 𝑝0, 𝑥 𝑗, {𝑝0}, 𝜖, 𝑤).
Example 5.1: As illustrated in Fig. 4, the blue lines are edges in an approximate adjacent graph of
𝑌 = {𝑦1, · · · , 𝑦9}, with 𝑦2 is the entry point of the graph. Considering the join windows 𝐽1 for 𝑥1
and 𝐽5 for 𝑥5, where 𝐽1 ∩ 𝐽5 = ∅, our initial step involves acquiring at least one data point contained
in 𝐽5 by sliding the graph. This step entails two strategies: ➊ Starting from nodes 𝑦1, 𝑦2, and 𝑦3, we
discover that 𝑦1’s neighbor 𝑦8 is included in 𝐽5; ➋ Starting from node 𝑦2, we find that its neighbor
𝑦1 is closer to 𝑥5, next identifying that 𝑦1’s neighbor 𝑦8 is included in 𝐽5.
(ii) 𝐽𝑖 ∩ 𝐽𝑗 ≠ ∅: In this case, acquiring the join window 𝐽𝑗 is straightforward, given that we are already
aware of at least one data point, 𝑦𝑝 , contained in the join window 𝐽𝑗 . We begin exploration from 𝑦𝑝 .
This is because the join windows of any data points in G are continuous windows (Corollary 4.1).
To elaborate, we search from any 𝑦𝑝 in 𝐽𝑖 ∩ 𝐽𝑗 and add it to the queue (line 13-14). Then, we expand
nodes in the queue (line 16) by exploring their neighbors within a distance no greater than 𝜖 from
𝑦𝑝 (lines 17-19). We continue the search process until no more neighbors can be added to the queue
(line 15) and finally return 𝐽𝑗 (line 20).
Example 5.2: Reconsider Example 5.1, we aim to slide the join window from 𝐽1 to 𝐽5, where we
have found 𝑦8 in 𝐽5. Next, in the second step, we start from 𝑦8, and explore its neighbors, which
results in the discovery of 𝑦8 and 𝑦9 within 𝐽5. For another instance, when sliding the join window
from 𝐽1 to 𝐽4, upon finding that 𝐽1 ∩ 𝐽4 = {𝑦2, 𝑦3} as outlined in line 13 of Algorithm 3. Hence we
proceed to explore starting from these two data points, and find that 𝑦4 and 𝑦7 are also in 𝐽4. Then
the explore terminates as no additional neighbors are in 𝐽4.
The Cost of Join Window Sliding: Recall that we give the join cost function for 𝐶 (𝑋 (cid:90)𝜖 𝑌 )
(Eq. (1)), and discuss how to use distance function, 𝛿 (, ), to estimate the join costs in Section 4.2. A
question that is unanswered is whether such cost estimation is feasible given the 𝜖-similarity join
algorithm, Algorithm 2, and in particular the JoinSlide algorithm (Algorithm 3). It is important to
mention that, on the one hand, as shown in Algorithm 3, the part of the join cost of JoinSlide is the
number of distance computations (NDC) while sliding over G within the join window 𝐽𝑗 (case (ii)).
On the other hand, the cost from sliding from 𝐽𝑖 to 𝐽𝑗 (case(i)), which can be estimated by 𝛿 (𝑥𝑖, 𝑥 𝑗 ),
and it is the only cost related to the join window order.

We conduct some experimental studies using Msong dataset. Here, we randomly divide Msong
into two sets in the same size, denoted as 𝑋 and 𝑌 , and conduct the 𝜖-similarity join on such 𝑋 and
𝑌 . In particular, we select 1,000 pairs of (𝑥𝑖, 𝑥 𝑗 ) ∈ 𝑋 × 𝑋 where 𝑥𝑖 ≠ 𝑥 𝑗 , and obtain NDC during
lines 1-12 using the JoinSlide algorithm (Algorithm 3) by sliding from the join window 𝐽𝑖 of 𝑥𝑖 to
the join window 𝐽𝑗 of 𝑥 𝑗 on the adjacent graph G, which is constructed by NSG [14] of 𝑌 . The
results are presented in Fig. 5. As shown in Fig. 5, the further apart 𝑥𝑖 and 𝑥 𝑗 are, the more sliding is
required, which leads to a larger NDC. The results indicate that the NDC increases as the distances
between the two points increase, and it is almost linear when the distance is under 0.9.

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:12

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

Table 1. 𝜖NG graphs

Dataset
Rand
Gauss
Msong
GIST
GloVe
Crawl
SIFT
Higgs

𝜖

0.57690
0.85741
0.70702
0.80105
0.71288
0.56437
0.69817
0.55096

𝑑𝑎𝑣𝑔

50.966
11.201
17.277
17.026
45.205
27.796
27.769
28.755

Fig. 5. NDC v.s. 𝛿 (𝑥𝑖, 𝑥 𝑗 ) on Msong dataset

6 Join Window Order Selection
In this section, we discuss join window order selection for 𝑋 (cid:90)𝜖 𝑌 . Here we assume the set of 𝑋 is
smaller than that of 𝑌 in size.

6.1 The Weighted Graph 𝐺𝐶
To determine the join window order, we discuss a weighted graph 𝐺𝐶 = (𝑉𝐶, 𝐸𝐶 ) where 𝑉𝐶 =
𝑋 ∪ {𝑦0} in Section 4.2 with which the optimal join window order can be determined by an MST on
𝐺𝐶 . Such 𝐺𝐶 constructed is a complete weight graph, and needs to construct online because it needs
dataset 𝑋 and an entry point of 𝑦0 taken from G of 𝑌 for 𝑋 (cid:90)𝜖 𝑌 . Therefore, the 𝐺𝐶 construction
time is a part of 𝜖-similarity join. Therefore, it is impractical to construct 𝐺𝐶 as it takes 𝑂 (𝑑𝑛2) for
a 𝑑-dimensional dataset 𝑋 where 𝑛 = |𝑋 |. This construction cost can be even larger than the join
processing time given 𝐺𝐶 is constructed.

Instead of constructing a completed weighted graph, 𝐺𝐶 = (𝑉𝐶, 𝐸𝐶 ), we construct a 𝜖-neighbor
proximity graph (𝜖NG), and denote it as 𝐺𝜖 = (𝑉𝜖, 𝐸𝜖 ), where 𝑉𝜖 = 𝑋 ∪ {𝑦0}. In 𝐺𝜖 , a data point is
connected to the nodes in 𝑉𝜖 which distance between them is no greater than 𝜖. The weight of an
edge, (𝑢, 𝑣), in 𝐸𝜖 is the distance 𝛿 (𝑢, 𝑣). The following lemma establishes that the total weight of
the MST on a connected 𝜖NG is equal to the minimum join cost.
Lemma 6.1: The minimum join cost of 𝑋 (cid:90)𝜖 𝑌 is equal to the total MST weight of 𝐺𝜖 if 𝐺𝜖 is connected.

Proof Sketch: Since the 𝐺𝜖 = (𝑉𝜖, 𝐸𝜖 ) is the subgraph of the complete graph 𝐺𝐶 = (𝑉𝐶, 𝐸𝐶 ), where
𝑉𝐶 = 𝑉𝜖 = 𝑋 ∪ {𝑦0} and 𝐸𝜖 ⊆ 𝐸𝐶 ). The total MST weight over 𝐺𝜖 , denoted as 𝑤 (𝐺𝜖 ), is no less
than the total MST weight over 𝐺𝐶 , denoted as 𝑤 (𝐺𝐶 ). Assume that 𝑤 (𝐺𝜖 ) > 𝑤 (𝐺𝐶 ), there must
exist an edge (𝑢, 𝑣) such that (𝑢, 𝑣) ∉ 𝐺𝜖 and 𝛿 (𝑢, 𝑣) < 𝑤max (𝑢 ⇝ 𝑣), where 𝑤max (𝑢 ⇝ 𝑣) is the
maximum edge weight along the path from 𝑢 to 𝑣 in the MST of 𝐺𝜖 . However, it becomes evident
that for 𝜖NG, the value of 𝜖 must satisfy 𝜖 > 𝑤max (𝑢 ⇝ 𝑣), whereas 𝛿 (𝑢, 𝑣) < 𝑤max (𝑢 ⇝ 𝑣). This
implies that (𝑢, 𝑣) must be included in such 𝜖NG, leading to a contradiction. Therefore, we conclude
□
that 𝑤 (𝐺𝜖 ) = 𝑤 (𝐺𝐶 ).

Lemma 6.1 states that 𝜖NG we require is a graph with a sufficiently large 𝜖 value to guarantee
connectivity. In Table 1, we show 𝜖NG with the smallest 𝜖 value that guarantees 𝐺𝜖 connected,
where 𝑑𝑎𝑣𝑔 represents the average node degree in this minimal connected 𝜖NG. The results indicate
that the graph size needed remains consistently small across all evaluated datasets.

In practice, constructing an exact 𝜖NG, 𝐺𝜖 = (𝑉𝜖, 𝐸𝜖 ) for 𝑉𝜖 = 𝑋 ∪ {𝑦0} is still time-intensive. We
do as follows. First, we construct an approximate 𝜖NG, ˜𝐺𝜖 = ( ˜𝑉𝜖, ˜𝐸𝜖 ), over 𝑋 , which can be done
offline. Here, an approximate 𝜖NG can be constructed based on the proximity graphs by considering
both in-neighbors and out-neighbors for each node to identify its neighbors for 𝜖NG. It is because
many state-of-the-art approaches for proximity graphs rely on an approximate 𝑘-NN graph and

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

00.30.60.91.2(xi,xj)01234NDC (×103)Fast Approximate Similarity Join in Vector Databases

158:13

Algorithm 4: MST (𝐺)
Input

: a proximity graph 𝐺 = (𝑉 , 𝐸) with each node 𝑢 ∈ 𝑉 having neighbors sorted in ascending
order by their distances to 𝑢

Output : the MST of proximity graph 𝐺
𝑇 ← ∅; 𝑙 [𝑢] ← 1 for each 𝑢 ∈ 𝑉 ;
assign 𝑢 ∈ 𝑉 to the set only contains itself;
while 𝑇 contains less than |𝑉 | − 1 edges do

𝐸min [𝑠] ← ∅ for each set 𝑠 that contains any data point 𝑢 ∈ 𝑉 ;
for each 𝑢 ∈ 𝑉 do

𝑣 ←the 𝑙 [𝑢]-th node in 𝑁𝐺 (𝑢);
while 𝑙 [𝑢] ≤ |𝑁𝐺 (𝑢)| and 𝑢, 𝑣 are in the same set do
𝑙 [𝑢] ← 𝑙 [𝑢] + 1; 𝑣 ←the 𝑙 [𝑢]-th node in 𝑁𝐺 (𝑢);

if 𝑙 [𝑢] ≤ |𝑁𝐺 (𝑢)| then

𝑠 ← the set contains data point 𝑢;
if 𝐸min [𝑠] = ∅ or 𝛿 (𝑢, 𝑣) < weight of 𝐸min [𝑠] then

𝐸min [𝑠] ← (𝑢, 𝑣);

for each set 𝑠 contains any data point 𝑢 ∈ 𝑉 do

(𝑢, 𝑣) ← 𝐸min [𝑠];
if 𝑢 and 𝑣 are in different sets then

merge the sets containing 𝑢 and 𝑣;
add edge (𝑢, 𝑣) into 𝑇 with weight 𝛿 (𝑢, 𝑣);

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

return 𝑇 ;

incorporate diverse pruning strategies [14, 34, 47]. These strategies preserve most short-distance
edges within approximate 𝑘-NN graph and further add edges to ensure graph connectivity. Next,
based on ˜𝐺𝜖 constructed over 𝑋 , we construct 𝐺𝜖 = (𝑉𝜖, 𝐸𝜖 ) by adding a new node, 𝑦0, taken from
G of 𝑌 , and add an edge between 𝑥𝑖 and 𝑦0, for every 𝑥𝑖 ∈ ˜𝑉𝜖 with the edge-weight of 𝛿 (𝑥𝑖, 𝑦0) and
satisfies 𝛿 (𝑥𝑖, 𝑦0) ≤ 𝜖.

6.2 The Algorithm for Order Selection
The MST can be computed for 𝐺𝜖 = (𝑉𝜖, 𝐸𝜖 ) using the Kruskal’s algorithm efficiently if 𝐸𝜖 has been
sorted. We can sort edges in ˜𝐺𝜖 constructed for 𝑋 offline before any 𝑋 (cid:90)𝜖 𝑌 . But, we have to sort all
edges in 𝐸𝜖 when 𝑦0 is added together with new edges between every 𝑥𝑖 and 𝑦0 online, in order to
process 𝑋 (cid:90)𝜖 𝑌 . Therefore, the time complexity to find MST using the Kruskal’s algorithm becomes
𝑂 (𝑚|𝑉𝜖 | log(𝑚|𝑉𝜖 |)), where 𝑚 is the degree limit of 𝐺𝜖 . We call it as baseline algorithm. Such a
baseline algorithm is time-consuming as illustrated in Exp. 4 in Section 8, where it consumes over
20% of the total time to determine join window selection GloVe dataset.

Thus, we need a new algorithm for MST. At a high level, in the first phase, we find MST for ˜𝐺𝜖
over 𝑋 , which can be done offline. In the second phase, for MST to be found over 𝐺𝜖 with a new
node 𝑦0 and |𝑋 | edges added, we insert |𝑋 | edges into the MST of ˜𝐺𝜖 to substitute certain existing
edges. We give the details as follows.
The first phase: It finds MST of the proximity graph ˜𝐺𝜖 = ( ˜𝑉𝜖, ˜𝐸𝜖 ), using the Kruskal’s algorithm
in 𝑂 (𝑚|𝑋 | log(𝑚|𝑋 |)). We give a more efficient algorithm in Algorithm 4, which finds MST, under
the assumption that the neighbors of each node 𝑢 ∈ ˜𝑉𝜖 are sorted in ascending order based on their

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:14

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

distance to 𝑢, which can be seamlessly integrated during the proximity graph ( ˜𝐺𝜖 ) construction
without requiring additional storage for such information.

Initially, each data point is allocated to an individual set containing only itself (line 2). Then, in
each iteration, we identify the edge with the minimum weight from each set to others (lines 5-12)
by exploring unvisited edges from each data point (lines 6-8). When we have found such edges
across sets, we add them into the MST if the two nodes of the edges are not already connected
(lines 13-17). The construction process concludes when the MST contains |𝑋 | − 1 edges (Line 5). To
store the MST in the proximity graph, we can assign a label to the edges within the MST (line 18).
Checking whether two elements are in the same set (lines 7, 15) and merging the set operation
(line 16) can be accomplished using the techniques proposed in [15]. Each operation requires
𝑂 (𝛼 (𝑁 )) time in total, where 𝑁 is the total number of elements, and 𝛼 (·) denotes the inverse
function of Ackermann’s function, which is less than 5 for any practical input, can be seen as a
constant [3]. Additionally, in each iteration, if there are |𝑆 | distinct sets containing any data point
𝑥 ∈ 𝑋 , at least ⌊|𝑆 |/2⌋ edges will be added into the MST at this iteration. Hence, the algorithm
comprises a maximum of log |𝑋 | rounds. Therefore, this phase runs in 𝑂 (𝑚|𝑋 | + |𝑋 | log |𝑋 |) time.
In practice, log |𝑋 | is lesser or comparable to 𝑚, hence the time complexity aligns with the size of
the proximity graph 𝐺.

Then, we provide the subsequent theorem to prove the correctness of this phase for constructing

MST of proximity graph of 𝑋 .
Theorem 6.1: Given a proximity graph 𝐺 of dataset 𝑋 , Algorithm 4 obtains the MST of graph 𝐺.

Proof Sketch: In Algorithm 4, each added edge connects two previously unconnected sets, cul-
minating in a connected graph with |𝑉 (𝐺)| − 1 edges, satisfying the tree property. To establish
that the resultant tree is MST of 𝐺, we prove that the minimum-weight edge bridging any two
disjoint subgraphs 𝐺1 and 𝐺2 (𝑉 (𝐺1) ∩ 𝑉 (𝐺2) = ∅) in 𝐺 is indeed part of the MST. We prove it
by contradiction. Assume the edge (𝑢, 𝑣) with the least weight crossing 𝐺1 and 𝐺2 is absent from
MST of 𝐺. It implies 𝛿 (𝑢, 𝑣) > 𝑤max (𝑢 ⇝ 𝑣), where 𝑤max(𝑢 ⇝ 𝑣) denotes the highest edge weight
along the path from 𝑢 to 𝑣 within the MST of 𝐺. This contradicts the initial premise that (𝑢, 𝑣) is
the minimum-weight edge spanning 𝐺1 and 𝐺2, since one of the edges along the path from 𝑢 to 𝑣 is
□
crossing 𝐺1, 𝐺2.
The second phase: Let 𝑦0 denote the entry point of proximity graph of 𝑌 . The second phase
˜𝐺𝜖 , resulting in
involves adding |𝑋 | edges (𝑥𝑖, 𝑦0) for each 𝑥𝑖 ∈ 𝑋 with weights 𝛿 (𝑥𝑖, 𝑦0) to MST of
the final MST of 𝐺𝜖 . We denote the new |𝑋 | edges into a sorted list 𝑒1, · · · , 𝑒 |𝑋 | (line 1). Then, we
traverse the edges in the MST of the proximity graph 𝐺 based on ascending edge weights (line 4).
Before inserting each edge, we check the sorted list 𝑒1, · · · , 𝑒 |𝑋 | by considering edges with weights
falling within the range of the previously traversed edge and the current edge (line 5-9). During
both the insertion process of edges in the sorted list and MST, we verify that the two nodes of an
edge if they do not belong to the same connected components (lines 6-8, 10-12). Following this, a
Depth-First Search (DFS) is executed on the MST to obtain the window order list (lines 13-14).

Note that, at line 1, the edge from 𝑦0 to 𝑥𝑖 ∈ 𝑋 that is larger than max𝑇 should not be included
in the MST unless it is the shortest edges from 𝑦0 to all data points in 𝑥𝑖 ∈ 𝑋 , where max𝑇 is the
˜𝐺𝜖 . To expedite the sorting process, a max𝑇 -range search can
maximum weight of edges in MST of
be conducted on ˜𝐺𝜖 , with the query point set as 𝑦0. We can find that the value of max𝑇 needed is
equal to the minimal value of 𝜖 for a connected 𝜖NG, as depicted in Table 1, the value of max𝑀𝑆𝑇
is typically small. Hence, the time complexity of this approach is similar to a 𝑘-nearest neighbor
search in practice, approximately 𝑂 (log |𝑋 |) [34]. Thereby, since lines 2-14 require 𝑂 (|𝑋 |) time,
the overall time for the second phase is 𝑂 (|𝑋 |).

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:15

: a proximity graph 𝐺 = (𝑉 , 𝐸) of 𝑋 and the entry point 𝑦0 of the proximity graph of 𝑌

Algorithm 5: WindowOrder (𝐺, 𝑦0)
Input
Output : the window order list
sort edges (𝑥𝑖, 𝑦0) with ascending order of 𝛿 (𝑥𝑖, 𝑦0) for each 𝑥𝑖 ∈ 𝑉 , and denote them as 𝑒1, 𝑒2, · · · , 𝑒 |𝑋 | ;
𝑖 ← 1; 𝑇 ← ∅;
assign each data point 𝑢 ∈ 𝑉 ∪ {𝑦0} to the set only contains itself;
for each edge (𝑝, 𝑞) in 𝐺’s MST in ascending order of 𝛿 (𝑝, 𝑞) do
while 𝑖 ≤ |𝑉 | and weight of edge 𝑒𝑖 = (𝑢, 𝑣) ≤ 𝛿 (𝑝, 𝑞) do

1

2

3

4

5

6

7

8

9

10

11

12

13

14

if 𝑢 and 𝑣 are in different sets then

merge the sets containing 𝑢 and 𝑣;
add edge (𝑢, 𝑣) into 𝑇 ;

𝑖 ← 𝑖 + 1;

if 𝑝 and 𝑞 are in different sets then

merge the sets containing 𝑝 and 𝑞;
add edge (𝑝, 𝑞) into 𝑇 ;

use DFS to derive parent node 𝑝 [𝑥𝑖 ] for each 𝑥𝑖 ∈ 𝑉 in 𝑇 rooted at 𝑦0;
return (𝑝 [𝑥𝑖 ], 𝑥𝑖 ) for each 𝑥𝑖 ∈ 𝑋 according to the DFS order;

The following theorem proves the correctness of this algorithm for obtaining the optimal join

window order list.
Theorem 6.2: Given the entry point 𝑦0 of the proximity graph of 𝑌 , Algorithm 5 returns the optimal
window order list with the minimum join cost when the given proximity graph 𝐺 of 𝑋 is a connected
𝜖NG.
Proof Sketch: We need to prove that the 𝑇 acquired in Algorithm 5 is the MST of the 𝜖NG of
dataset |𝑋 | ∪𝑦0, then we can utilize Lemma 6.1 to establish that the weight of the 𝑀𝑆𝑇 is equivalent
to the minimum join cost. Since lines 4-5 guarantee the traversal of edges in {𝑒1, 𝑒2, · · · , 𝑒 |𝑋 | } and
the MST of 𝐺 in ascending order, 𝑇 is MST among these edges. Assuming that 𝑇 is not MST of
the connected 𝜖NG of dataset |𝑋 | ∪ {𝑦0}, there must be at least one edge (𝑢, 𝑣) in the 𝜖NG that is
not in the MST of 𝐺 but is included in the MST of the 𝜖NG. This implies 𝛿 (𝑢, 𝑣) < 𝑤max (𝑢 ⇝ 𝑣),
where 𝑤max (𝑢 ⇝ 𝑣) is the maximum edge weight along the path from 𝑢 to 𝑣 in 𝑇 . Since the edge
(𝑢, 𝑣) is absent in 𝑇 , the path from 𝑢 to 𝑣 in 𝑇 must involve two edges from 𝑦0, denoted as (𝑦0, 𝑝)
and (𝑦0, 𝑞), where 𝛿 (𝑦0, 𝑝) ≤ 𝛿 (𝑦0, 𝑞). Hence, we have 𝛿 (𝑢, 𝑣) < 𝛿 (𝑦0, 𝑞). However, because (𝑢, 𝑣) is
not part of the MST of 𝐺, and (𝑦0, 𝑞) must replace one of the edges from 𝑝 to 𝑞 in the MST of 𝐺 to
max (𝑝 ⇝ 𝑞) is the maximum
be present in 𝑇 , we have 𝛿 (𝑦0, 𝑞) < 𝑤 ′
□
edge weight along the path from 𝑝 to 𝑞 in the MST of 𝐺. This leads to a contradiction.

max (𝑝 ⇝ 𝑞) ≤ 𝛿 (𝑢, 𝑣), where 𝑤 ′

7 𝑘-similarity Join
In this section, we discuss how our 𝜖-similarity join algorithm supports 𝑘-similarity join. Then, we
discuss how our 𝑘-similarity join addresses maintenance issue for the proximity graph index.

7.1 𝑘-similarity Join Algorithm
The 𝑘-similarity join 𝑋 (cid:90)𝑘 𝑌 between two 𝑑-dimensional dataset 𝑋 and 𝑌 is defined as 𝑋 (cid:90)𝑘 𝑌 =
{(𝑥𝑖, 𝑦 𝑗 ) ∈ 𝑋 × 𝑌 | 𝑦 𝑗 ∈ 𝑇𝑜𝑝𝐾 (𝑥𝑖 )}, where 𝑇𝑜𝑝𝐾 (𝑥𝑖 ) is the set of top-𝑘 nearest data points of 𝑥𝑖 in
𝑌 .

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:16

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

Algorithm 6: kJoinSlide (G, 𝑥𝑖, 𝑥 𝑗, 𝐽𝑖, 𝑘, 𝑤)
Input

: an adjacent graph G of dataset 𝑌 , two data points 𝑥𝑖, 𝑥 𝑗 , the join result 𝐽𝑖 of 𝑥𝑖 and two
parameters 𝑘, 𝑤
Output : the 𝑘-join result 𝐽𝑗 of 𝑥 𝑗 in 𝑌
𝑄 ← 𝐽𝑖 is a priority queue, sorted in ascending order based on 𝛿 (𝑦𝑝, 𝑥 𝑗 ) for every 𝑦𝑝 ∈ 𝑄;
𝑉 𝑖𝑠𝑖𝑡 ← 𝐽𝑖 ; mark each 𝑢 ∈ 𝑄 unexplored;
while at least one of the elements in 𝑄 is unexplored do

1

2

3

4

5

6

7

8

9

𝑢 ← the first unexplored element in 𝑄; mark 𝑢 explored;
for each 𝑣 ∈ 𝑁 G (𝑢) \ 𝑉 𝑖𝑠𝑖𝑡 do

push 𝑣 into priority queue 𝑄;
𝑉 𝑖𝑠𝑖𝑡 ← 𝑉 𝑖𝑠𝑖𝑡 ∪ {𝑣 }; mark 𝑣 unexplored;
while 𝑄.𝑠𝑖𝑧𝑒 () > 𝑤 do

remove the last element from 𝑄;

10

return the first 𝑘 elements in 𝑄;

The main ideas used in our 𝜖-similarity join algorithm, SimJoin, can be utilized to support 𝑘-
similarity join, based on join window sliding and join window order selection. We discuss the
key difference between 𝜖-similarity join and 𝑘-similarity join. For 𝜖-similarity join, 𝑋 (cid:90)𝜖 𝑌 , a
continuous join window, 𝐽𝑖 , for 𝑥𝑖 , is bounded while sliding. In other words, suppose it slides to 𝑦𝑝 ,
for 𝛿 (𝑦𝑝, 𝑥𝑖 ) ≤ 𝜖, then it does not need to slide further from 𝑦𝑝 to 𝑦𝑞 and beyond if for 𝛿 (𝑦𝑞, 𝑥𝑖 ) > 𝜖.
For 𝑘-similarity join, 𝑋 (cid:90)𝑘 𝑌 , it is difficult to determine whether the data points are included in
the join window or not, i.e., it is a challenge for the sliding to ensure that no additional points in 𝑌
can be included in 𝑇𝑜𝑝𝐾 (𝑥𝑖 ) before terminating. Hence, we propose to explore all adjacent points
of a join window 𝐽𝑖 to ensure the points in 𝐽𝑖 are top-𝑘 nearest data points by there are no closer
neighbors to 𝑥𝑖 . Based on this, for 𝑘-similarity join, the strategies used for join window sliding and
join window order selection can be used effectively.

We give the join window sliding algorithm for 𝑘-similarity join in Algorithm 6, which is the only
part we need to modify to support for 𝑘-similarity join based on our 𝜖-similarity join algorithm,
SimJoin. It starts by enqueuing all data points from the join window of 𝐽𝑖 into the priority queue,
𝑄 (line 1). Next, it traverses each node in 𝑄 to explore closer data points to 𝑥 𝑗 by examining its
neighbors (lines 5-9). The size of 𝑄 is restricted to a maximum of 𝑤 (lines 8-9), and the iteration
concludes when no nodes in the queue have closer neighbors to 𝑥 𝑗 (line 3).
𝜖-similarity join vs 𝑘-similarity join: The main difference between 𝑘 and 𝜖 is that the former
indicates the number of nearest neighbors whereas the latter indicates the nearest neighbors in a
range. The two serve a similar purpose but are different. From the viewpoint of 𝑘, the values of 𝜖
can vary from one dataset to another. Consider 𝑘 as nSelectivity given in Exp. 3 in Section 8. As
illustrated in Fig. 7, to have nSelectivity = 10, 𝜖 needs to be greater than 0.5 in Crawl, and needs to
be less than 0.4 in Higgs.

Determining the value of 𝑘 for the join may be straightforward as it limits the number of results.
For selecting the value of 𝜖, one way is to explore the average distance in a known dataset. For
example, in the application of auto-tagging discussed in our introduction, the 𝜖 value can be
obtained by the average distance among the documents that have the same labels. Another way to
select 𝜖 for joins is to explore its relationship with nSelectivity (e.g., 𝑘).

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:17

7.2 Maintenance of Proximity Graph Index
Proximity graphs are one of the state-of-the-art approaches for approximate nearest neighbor
search in vector databases, which offers a multitude of applications including information retrieval
and recommendations. And there is a significant demand for updating these indices due to the
continuous influx of large volumes of vector data across different platforms, e.g., over 500 hours of
content are uploaded to YouTube every minute [41]. Thus, the maintenance of proximity graphs
has emerged as an important issue.

The maintenance issue for a proximity graph index, 𝐺𝑌 = (𝑉𝑌 , 𝐸𝑌 ), for a dataset 𝑌 is to deal with
data insertion/deletion [40, 42, 44]. To deal with new data point insertion, the existing approaches
will maintain it in a dataset 𝑋 , and build a different small delta proximity graph index, 𝐺𝑋 = (𝑉𝑋 , 𝐸𝑋 ),
to maintain such new points; and to deal with data point deletion from 𝑌 , the existing approaches,
for each deleted 𝑦𝑝 from 𝑌 , will connect all its in-neighbors to its out-neighbors in 𝐺𝑌 . It is important
to note that periodic global rebuilding of the entire 𝐺𝑌 is necessary and is triggered (1) when the
cumulative number of data points in 𝐺𝑋 surpasses a specific threshold (e.g., 1-10% of the total index
size) and (2) the number of deleted data points in 𝐺𝑌 exceeds a substantial threshold. Such global
rebuildings are resource-intensive and time-consuming. As shown in Table 4, global rebuilding
of an index for Higgs dataset peaked at 22.4 GB memory and required 2,962 seconds when it is
executed using 32 threads, despite the original size of Higgs is 3.8 GB. And the main cost is to
rebuild 𝐺𝑌 with 𝐺𝑋 .
To deal with data insertions: To rebuild a new proximity index G𝑌 for 𝑌 ∪ 𝑋 for data points
insertion, first, we conduct 𝑘-similarity join, 𝑋 (cid:90)𝑘 𝑌 , where 𝐺𝑋 has been built for 𝑋 and 𝐺𝑌 has
been built for 𝑌 . The 𝑘-similarity join results are the potential out-neighbors of each node across 𝑌
and 𝑋 . Second, together with 𝐺𝑋 , 𝐺𝑌 and the 𝑘-similarity resultss, we can build a new G𝑌 easily,
without rebuilding G𝑌 from scratch for 𝑌 ∪ 𝑋 . Third, we can apply various pruning techniques by
different approaches to obtain the final index.
To deal with data deletions: When a data point is deleted, we mark it on the proximity graph,
𝐺𝑌 , to ensure its exclusion from 𝑘-ANN searches, but do not remove it from 𝐺𝑌 . Upon reaching
a specified threshold of deletions, we perform batch updates on 𝐺𝑌 . For batch updates, it is to
deal with those data points, 𝑦𝑞, in 𝐺𝑌 marked deleted, because the out-degree of the in-neighbors
of 𝑦𝑞 can drop below a threshold, e.g., 𝑚. The impacts on the out-neighbors of 𝑦𝑞 are minor, as
their 𝑘-ANN on 𝐺𝑌 remains unaffected. To swiftly address the decrease in the out-degree of the
in-neighbors of such deleted nodes in 𝐺𝑌 , we employ the join window sliding algorithm instead
of adding new edges from the in-neighbors of 𝑦𝑞 to out-neighbors of 𝑦𝑞. Specifically, for each
in-neighbor 𝑦𝑥 of a deleted data point, 𝑦𝑞, on 𝐺𝑌 , we slide the join window 𝐽𝑥 = 𝑁𝐺𝑌 (𝑦𝑥 ) \𝑌𝐷 to the
𝑘-similarity join window 𝐽𝑥 of 𝑦𝑥 , where 𝑌𝐷 is the set of data points deleted from 𝑌 , which 𝐽𝑥 should
exclude. This process can be accomplished by invoking kJoinSlide (G, 𝑦𝑥, 𝑦𝑥, 𝑁𝐺𝑌 (𝑦𝑥 ) \ 𝑌𝐷, 𝑘, 𝑤) for
𝑘 > 𝑚. We can easily do it by modifying line 8 to“while |𝑄 \𝑌𝐷 | > 𝑤 do” and line 10 to “return the
first 𝑘 elements in 𝑄 \ 𝑌𝐷 ”. Next, various pruning techniques, relying on those proposed in different
proximity graph methods, can be employed on 𝐽𝑥 for each in-neighbor 𝑦𝑥 . For instance, when
maintaining NSG [14], an edge (𝑢, 𝑣) exists only if there is no edge (𝑢, 𝑤) such that 𝛿 (𝑢, 𝑤) < 𝛿 (𝑢, 𝑣)
and 𝛿 (𝑣, 𝑤) < 𝛿 (𝑢, 𝑣).

8 Experiments
In this section, we conduct extensive experiments on both real-world and synthetic datasets and
report our findings.
Datasets: We employ 6 real-world and 2 synthetic datasets with different numbers of dimensions/-
points, the real-world datasets are from diverse applications including image (SIFT [1], GIST [1]),

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:18

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

Table 2. Statistics of Datasets

dim.

# of points Type

Source Dataset

dim.

# of points Type

Source

64
64
420
960

Synthetic
Synthetic

100,000
100,000
992,272 Audio
Image

1,000,000

U(0,1)
N(0,1)
[6]
[1]

GloVe
Crawl
SIFT
Higgs

100
300
128
29

1,183,514 Text
1,989,995 Text
10,000,000
11,000,000

Image
Particles

[35]
[2]
[1]
[5]

Dataset
Rand
Gauss
Msong
GIST

Table 3. Runtime and average recall of four algorithms on different datasets (Exp. 2)

Dataset

XJoin

𝜖-self similarity join (𝜖=0.4)
FGF-Hilbert

VBASE

SimJoin

Rand
Gauss
Msong
GIST
GloVe
Crawl
SIFT
Higgs

recall
0.95688
0.95763
0.97613
0.97308
0.96599
0.97304
0.98138
0.98659

time (s)
19.368
15.788
765.82
2097.1
280.70
1063.1
14819
8258.2

recall
0.99233
0.99583
0.99055
0.98825
0.99264
0.98753
0.99251
0.99031

time (s)
16.343
13.272
528.57
1827.8
225.13
838.91
7679.5
4553.2

recall
1
1
1
1
1
1
1
1

time (s)
48.989
18.234
4904.1
10911
882.29
6072.2
166050
38724

recall
1
1
0.99368
0.99091
1
0.99998
0.99564
0.99014

time (s)
1.8626
1.1332
135.89
120.62
18.158
47.114
5232.8
2044.6

𝜖-similarity join (𝜖=0.4)

XJoin

VBASE

FGF-Hilbert

recall
0.95752
0.95727
0.97541
0.97739
0.96586
0.97321
0.98023
0.98659

time (s)
19.536
16.418
783.35
2196.7
287.76
1048.7
15479
10948

recall
0.99126
0.99583
0.99035
0.99135
0.99261
0.98659
0.99222
0.99031

time (s)
16.293
13.394
528.54
1775.7
222.77
842.63
9418.4
6339.2

recall
1
1
1
1
1
1
1
1

time (s)
49.035
18.011
4912.7
11295
897.89
6138.9
166931
38778

recall
0.99298
1.0000
0.99052
0.99256
0.99788
0.99084
0.99344
0.99067

SimJoin
time (s)
6.3837
1.0223
178.20
355.38
15.203
202.72
5532.6
2020.3

pre-ratio
0.00623%
0.03870%
0.00066%
0.00032%
0.01474%
0.00201%
0.00023%
0.00109%

audio (Msong [6]), text (GloVe [35], Crawl [2]) and high-energy physics (Higgs [5]). The summary
can be found in Table 2, with the number of dimensions (dim.) and the number of data points (# of
points). To evaluate the algorithms, the datasets are randomly divided into two parts of equal size.
Self-similarity joins are evaluated on one of the split datasets, while similarity joins are assessed on
both datasets.
Algorithms: We conduct comparisons between our approaches, named as SimJoin, and three state-
of-the-art methods, including approximate similarity join methods (VBase [51] and XJoin [46]), and
exact similarity join method (FGF-Hilbert [36]). (1) VBase [51] is the state-of-the-art in approximate
similarity join approaches. It executes the join algorithm by treating each data point in one dataset
as an individual range query and implements an efficient range filter by integrating it with an index
scan operator. (2) XJoin [46] is the latest approach for approximate similarity join. It employs a
learning-based technique to predict whether a data point possesses a sufficient number of join
results. Specifically, for 𝑋 (cid:90)𝜖 𝑌 , where 𝑋 is the larger dataset and 𝑌 is the smaller dataset to
join. First, XJoin is trained to predict if a query vector 𝑦𝑖 ∈ 𝑌 contains sufficient neighbors within
the 𝜖 range in 𝑋 . Second, the query vectors identified as having adequate neighbors are formed
as a new dataset 𝑌 ′. Finally, the LSH-based join algorithm is performed between 𝑋 and 𝑌 ′. As
demonstrated in [46], XJoin outperforms various LSH-based approaches. (3) FGF-Hilbert [36] is
the state-of-the-art method of exact similarity join, relying on the Epsilon Grid Order technique
and enhancing runtime efficiency by improving data locality, thereby rendering the algorithms
cache-oblivious. (4) SimJoin: our join algorithm contains Algorithm 2 for two distinct datasets and
a self-join algorithm. In the self-join algorithm, each data point inherently includes itself in the
results due to zero distance. Hence, for every data point in 𝑋 , we can initiate the sliding of the join
window starting with itself. In other words, for each data point 𝑥𝑖 ∈ 𝑋 , we can invoke Algorithm 3
via JoinSlide (𝐺, 𝑥𝑖, 𝑥𝑖, {𝑥𝑖 }, 𝜖, 𝑤), where 𝐺 is proximity graph of 𝑋 . For VBase and our approach,
we use the same proximity graph, NSG [14], for comparisons in each dataset.

In the comparisons of join time, we exclude the index construction time for VBase, XJoin and
our approach as the index constructed is independent of the 𝜖 value selected. The index can be
constructed offline. We include the index construction time for FGF-Hilbert, because FGF-Hilbert
requires preprocessing and cannot reuse the same index constructed for different 𝜖 values.

We evaluate the performance of the similarity join algorithms using a single thread, and all

results are averaged over 5 runs.
Performance metrics: We focus on two metrics for evaluating the join results: average recall

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

Fast Approximate Similarity Join in Vector Databases

158:19

(a) Rand (self join)

(b) Gauss (self join)

(c) Msong (self join)

(d) GIST (self join)

(e) GloVe (self join)

(f) Crawl (self join)

(g) SIFT (self join)

(h) Higgs (self join)

(i) Rand (join)

(j) Gauss (join)

(k) Msong (join)

(l) GIST (join)

(m) GloVe (join)

(n) Crawl (join)

(o) SIFT (join)

(p) Higgs (join)

Fig. 6. 𝜖-join comparisons with current three join algorithms (Runtime v.s. Recall) when 𝜖 = 0.4 (Exp. 1)

and average precision, as detailed in Section 2. Given that the join results produced by the four
algorithms compared in our experiments are all based on exact distance comparisons, their average
precision are all 1. Therefore, our comparisons focus solely on the average recall of these algorithms.
Experimental environments: The experiments are conducted on a CentOS Linux server with
Intel(R) Xeon(R) Silver 4215 CPU @ 2.50GHz with 128GB memory. All algorithms are implemented
in C++11. The code is compiled with g++ 11.4.1 under O3 optimization.

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

0.90.951Average recall102103104Runtime (s)VBASEXJoinFGF-HilbertSimJoin0.90.951Average recall100101102Runtime (s)0.90.951Average recall100101102Runtime (s)0.90.951Average recall102103104Runtime (s)0.90.951Average recall101102103104Runtime (s)0.90.951Average recall101102103Runtime (s)0.90.951Average recall101102103104Runtime (s)0.90.951Average recall103104105Runtime (s)0.90.951Average recall103104105Runtime (s)0.90.951Average recall100101102Runtime (s)0.90.951Average recall100101102Runtime (s)0.90.951Average recall102103104Runtime (s)0.90.951Average recall101102103104Runtime (s)0.90.951Average recall101102103Runtime (s)0.90.951Average recall101102103104Runtime (s)0.90.951Average recall103104105Runtime (s)0.90.951Average recall103104105Runtime (s)158:20

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

(a) Crawl (self join)

(b) Higgs (self join)

(c) Crawl (join)

(d) Higgs (join)

Fig. 7. Runtime at 0.99 average recall when vary 𝜖 (Exp. 3)

Exp. 1. Effects of the parameters in join algorithms: In this evaluation, we keep the dataset
and 𝜖 fixed at 0.4, and then adjust various parameters in different algorithms. In our join algorithms,
we modify the parameter 𝑤. In VBASE, their search algorithms are based on beam search, so we
adjust the beam width in their algorithms. For XJoin, we vary the value of 𝜏 in their algorithm, a
parameter used to identify ground-truth negative training samples, where a higher 𝜏 value can
enhance efficiency at the loss of quality. FGF-Hilbert does not have adjustable parameters and is
represented as a single point in the figures. The results are shown in Fig. 6, where lower and further
to right curves indicate better performance.

The results reveal that our algorithms outperform the three approaches significantly, achieving
higher average recall with much-reduced runtime. Moreover, the initial points of the curves for our
algorithms are notably to the right compared to the other approximate similarity join algorithms,
showcasing that our algorithms can efficiently identify nearly all join results without heavy time
cost on searches. The results further indicate that our algorithms show reduced dependency on
parameters, as evidenced by the narrower range of average recall values of our algorithms’ curves.
Exp. 2. Overall performance of 𝜖-similarity join: As shown in Table 3, our join algorithms,
denoted as SimJoin, including the 𝜖-self similarity join algorithm and the 𝜖 similarity join algorithm,
is compared to three state-of-the-art approaches when we set 𝜖 equals 0.4. Compared to VBASE,
our approach demonstrates up to 1 order of magnitude speedups in runtime with superior quality.
Specifically, SimJoin achieves speedups of 8.8x, 11.7x, 3.9x, 15.2x, 12.4x, 17.8x, 1.5x, 2.2x in self-
similarity join, and 2.6x, 13.1x, 3.0x, 5.0x, 14.7x, 4.2x, 1.7x, 3.1x in similarity join on the Rand, Gauss,
Msong, GIST, GloVe, Crawl, SIFT, Higgs datasets respectively. Compared to the state-of-the-art
method in exact similarity join, our algorithm achieves up to speedups of over 2 orders of magnitude
in runtime while maintaining an average loss of less than 1% in join results. We further present
the ratio of the runtime of the join window order selection to the total runtime of SimJoin on
𝜖-similarity join, denoted as “pre-ratio” in Table 3, to provide the time breakdown of our algorithm.
The time of our join window order selection for many datasets, such as Rand in the first row, is
notably less than 1ms. To ensure precise reporting of such times, we conducted the join window
selection algorithm 100 times, and reported the average time. The results indicate that the order
selection phase constitutes a negligible portion of the total time of our SimJoin.
Exp. 3. Vary the value of 𝜖: In this experiment, we vary the value of 𝜖 to compare the runtime
of different algorithms when achieving an average recall of 0.99. The results are shown in Fig. 7,
which does not include XJoin, as it cannot achieve 0.99 recall in either the Crawl or Higgs datasets.
We use nSelectivity to denote the average number of join results for each data point in a dataset,
defined as the value of |𝑋 | multiplied by the selectivity of the join operation, i.e., the nSelectivity
of the join operation 𝑋 (cid:90) 𝑌 is given by |𝑋 | · |𝑋 (cid:90)𝑌 |
|𝑋 ×𝑌 | .

The results in the figures indicate that the runtime of our algorithms increases linearly with
the value of nSelectivity, demonstrating good scalability as the number of join results increases.

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

0.10.20.30.40.5101102103104Runtime (s)VBASEFGF-HilbertSimJoinnSelectivity0123456nSelectivity0.10.20.30.40.5101102103104Runtime (s)0123456nSelectivity0.10.20.30.40.5102103104105Runtime (s)100101102103104nSelectivity0.10.20.30.40.5101102103104Runtime (s)0123456nSelectivity0.10.20.30.40.5102103104105Runtime (s)100101102103104nSelectivityFast Approximate Similarity Join in Vector Databases

158:21

(a) Crawl (self join)

(b) Higgs (self join)

(c) Crawl (join)

(d) Higgs (join)

Fig. 8. NDC v.s. Recall when 𝜖 = 0.4 (Exp. 4)

(a) GIST

(b) SIFT

(a) self join

(b) join at |𝑌 | = 500 (c)

join at

|𝑋 | =

500, 000

Fig. 9. base and query data join (Exp. 5)

Fig. 10. Varying dataset size (0.99 average recall) (Exp. 6)

(a) Crawl (self join)

(b) GIST (self join)

(c) Crawl (join)

(d) GIST (join)

Fig. 11. 𝜖-join by different proximity graphs (Exp. 7)

Besides, our join algorithms consistently remain much shorter than that of VBASE and FGF-Hilbert
across different values of 𝜖.
Exp. 4. Number of distance computations during join: In this part, we conduct experiments to
compare our approach with others based on a new metric, the number of distance computations
(NDC), using Crawl and Higgs datasets. As shown in Fig. 8, our approach has a notable enhancement
in terms of NDC over the existing state-of-the-art approaches, consistent with the results of Exp. 2.
Exp. 5. Join between base and query data: In this part, we use the base data and query data as
two separate datasets for join. We evaluate our approach against three other approaches using SIFT
and GIST datasets sourced from the ANN benchmark1. The results, shown in Fig. 9, demonstrate
that, akin to the findings in Exp. 2, our approach significantly outperforms the existing methods.
Exp. 6. Vary the size of datasets for join: To evaluate the scalability of our proposed SimJoin
method, we conduct experiments on SIFT and GIST datasets by (i) varying the size of dataset (|𝑋 |)

1https://ann-benchmarks.com/

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

0.90.951Average recall102103104Runtime (s)VBASEXJoinFGF-HilbertSimJoin0.90.951Average recall107108109NDC0.90.951Average recall10910101011NDC0.90.951Average recall107108109NDC0.90.951Average recall10910101011NDC0.90.951Average recall102103104Runtime (s)VBASEXJoinFGF-HilbertSimJoin0.90.951Average recall101100101Runtime (s)0.90.951Average recall100101102Runtime (s)103104105|X|101100101102103Runtime (s)SIFTGIST103104105|X|101100101102103Runtime (s)103104105|X|00.20.40.60.81Runtime (s)103104105|Y|101100101102103Runtime (s)0.960.981Average recall101102103Runtime (s)HNSWVamanaNSG0.9980.9991Average recall101102103Runtime (s)0.960.981Average recall101102103Runtime (s)0.960.981Average recall101102103Runtime (s)0.920.961Average recall101102103Runtime (s)158:22

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

Fig. 12. Runtime of join window order algorithms (Exp. 8)

from 500 to 500, 000 in self join, (ii) varying the size of base data (|𝑋 |) from 500 to 500, 000 while
keeping the size of the query data (|𝑌 |) as 500, and (iii) varying the size of the query data (|𝑌 |) from
500 to 500, 000 while keeping the size of the base data (|𝑋 |) constant as 500, 000. The results of
runtime at 0.99 average recall are shown in Fig. 10. Notably, the runtime shows a linear increase or
a slower rate of growth in comparison to the expansion of the dataset size, which validates that our
method exhibits strong scalability when either the base data or query data size expands.
Exp. 7. Comparisons using different proximity graphs: Existing proximity graph indexes
for 𝑘-ANN searches can seamlessly integrate with our join algorithm. Here, we compare three
state-of-the-art proximity graph index methods for 𝜖-similarity joins on Crawl and GIST datasets
when 𝜖 = 0.4. As shown in Fig. 11, HNSW does not perform well due to higher edge distances, which
impacts adjacency quality according to the analysis in Theorem 5.1. The higher edge distances in
HNSW are because it is built via incremental insertion, which means candidate neighbors are only
selected among previously inserted nodes. Vamana and NSG exhibit similar performance, since
they differ mainly in pruning strategies that affect a small edge subset in the graph.
Exp. 8. Comparisons among join window order determination algorithms: We compare
our two advanced join window order determination algorithms: MST + WindowOrder-Sort (Al-
gorithms 4+5) and WindowOrder-𝜖 (Algorithms 4+5, with line 2 in Algorithm 5 replaced by an
approximate max𝑇 -range query), against the baseline algorithm BaseMST. The details of all these
algorithms are provided in Section 6.2.

The runtime of the three algorithms is shown in Fig. 12. We can find that it is essential to
accelerate the running time of the baseline approach, as it consumes a significant portion of the
total runtime. For example, in GloVe dataset, the runtime of the baseline approach for determining
the join window order is 4.4s, which accounts for over 20% of the total join processing time. For
the two advanced algorithms, MST step can be completed offline before the join operation. Even
with this preprocessing, the advanced algorithms outperform the baseline by more than 1 order
of magnitude in runtime. Moreover, WindowOrder-Sort and WindowOrder-𝜖 are faster than the
baseline by over 2 and 3 orders of magnitude, respectively. The join costs for BaseMST and MST +
WindowOrder-Sort are the same, while the difference in join costs between MST + WindowOrder-𝜖
and the others are less than 0.01% across all datasets.
Exp. 9. Comparisons in 𝑘-similarity join: We evaluate our 𝑘-similarity join algorithm by
comparing it to VBase. Although VBase does not directly support 𝑘-similarity join, we utilized their
𝑘-nearest neighbor search to facilitate the join by treating each data point in the smaller dataset
as a query point, following a similar method to their 𝜖-similarity join. The results on Crawl and
Higgs datasets are depicted in Fig. 13, showcasing that the runtime of our algorithm is significantly
lower than VBase’s while achieving similar or even better average recall.
Exp. 10. Index maintenance comparisons: We follow the experimental setup of FreshDiskANN [40]
to evaluate our algorithms for index maintenance on Crawl and Higgs datasets. For insertion, we

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

RandGaussMsongGISTGloVeCrawlSIFTHiggs104102100102Runtime (s)BaseMSTMSTWindowOrder-SortWindowOrder-RandGaussMsongGISTGloVeCrawlSIFTHiggs104102100102Runtime (s)Fast Approximate Similarity Join in Vector Databases

158:23

(a) Crawl (self join)

(b) Higgs (self join)

(c) Crawl (join)

(d) Higgs (join)

Fig. 13. 𝑘-similarity join comparisons when 𝑘 = 10 (Exp. 9)

Table 4. NSG index maintenance comparisons (Exp. 10)

Dataset

Rand
Gauss
Msong
GIST
GloVe
Crawl
SIFT
Higgs

global rebuilding

FreshDiskANN

𝑘-similarity join

peak memory

time (s)

peak memory

time (s)

peak memory

time (s)

430.72 MB
419.21 MB
3.9465 GB
9.0220 GB
4.2359 GB
7.3334 GB
17.257 GB
22.394 GB

129.624
131.991
2632.23
6632.01
958.089
1963.67
3269.74
2961.66

274.64 MB
166.51 MB
1.6452 GB
5.5203 GB
1.1092 GB
2.4671 GB
8.1037 GB
4.7927 GB

37.3372
29.9972
343.617
960.500
875.349
674.069
1989.38
769.701

249.95 MB
167.75 MB
1.6432 GB
5.5196 GB
1.0849 GB
2.4202 GB
8.0456 GB
4.7922 GB

33.3368
29.2273
327.254
906.157
864.672
585.061
1825.94
744.140

divide the original dataset into two parts with equal size. One part is used for the initial index
construction, and the other part is used for insertion; for deletion, we randomly select points for
removal following FreshDiskANN. Specifically, we randomly remove 10% of data points from one
part of the dataset and then insert the same number of data points from the other part. Our algo-
rithm is compared to (i) an approach based on global rebuilding, where the index is rebuilt globally
after the complete deletion and insertion process; and (ii) FreshDiskANN [40], the state-of-the-art
graph-based index maintenance approach. Our algorithm and FreshDiskANN utilize only one
thread for supporting maintenance, while global rebuilding employs all available threads in the
servers for processing. The comparisons are based on the NSG graph index, where the reported
times include the index rebuilding time for global rebuilding and the total time taken for index
merging during data point insertion and batch updates for data point deletion in FreshDiskANN
and our algorithms.

Regarding the global rebuilding, the results, as depicted in Table 4, show that our maintenance
algorithms achieve significantly higher efficiency and smaller peak memory. And Fig. 14 shows
that our final graph index is even better than that of global rebuilding, attributed to the higher
quality of the k-nearest neighbors of each data point in our algorithms compared to NN-descent.
For FreshDiskANN, although it has comparable memory usage and processing time to ours, in
terms of the quality of the index maintained, our approach outperforms FreshDiskANN, as shown
in Fig. 14, because FreshDiskANN focuses on delta changes within the index to be maintained.

9 Related Work
Many works focus on exact high-dimensional similarity joins, including 𝜖-similarity join [7, 9,
25, 36, 39] and 𝑘-NN join [8, 48]. However, the so-called high dimension may be different from

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

0.90.951Average recall02505007501000Runtime (s)VBASESimJoin0.90.951Average recall02505007501000Runtime (s)0.90.951Average recall040080012001600Runtime (s)0.90.951Average recall02505007501000Runtime (s)0.90.951Average recall050010001500Runtime (s)158:24

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

(a) Crawl

(b) Higgs

Fig. 14. ANNS performance on final NSG (Exp. 10)

time to time. Most of these works [8, 25, 39, 48] consider dimensions around 40 as high, whereas
current vector databases often feature significantly more dimensions, e.g., the number of dimensions
in GIST is 960. Among them, the state-of-the-art methods for exact high-dimensional similarity
join [22, 23, 29, 31, 36] involve two steps: filtering and refinement. In the filtering step, candidate
pairs of vectors that might be part of the final join results are selected through indexing or sorting.
In the refinement step, the exact distance between candidate pairs of two vectors is computed.
Filtering using index structures, such as R-trees [9], to support the join predicate can be costly in
index construction. Therefore, these approaches opt to sort the dataset based on a function that
supports the join predicate, for example, Epsilon Grid Order [7].

In the realm of approximate high-dimensional similarity search, existing approaches treat each
data point in a dataset as an individual approximate 𝜖-range query. These queries are then supported
by a locality-sensitive hashing (LSH) based index [4, 20, 27, 37, 46, 49, 50] or a proximity graph
index [44, 51]. At a high level, LSH-based approaches support approximate similarity joins by
following three steps: (i) first projecting each vector into a hash value; (ii) next executing an
equi-join on the pairs that collide under the same hash value to establish candidate join results; (iii)
finally, exact distance computations are conducted to derive the final join results. Therefore, the
effectiveness of these approaches heavily relies on the hash functions in step (i), i.e., mapping similar
vectors to the same hash value, which is also the key factor that highly impacts the performance
in LSH-based methods for approximate nearest neighbor search. However, different to recent
graph [34, 47] and partition [10, 16, 18] based approaches, LSH-based approaches do not take data
distribution into consideration, which often leads to a significant performance decline in real-world
datasets [45], where data is unevenly distributed data.

10 Conclusion
In this paper, we introduce a novel join algorithm designed to support approximate similarity joins
in high-dimensional spaces. Our approach leverages the intrinsic properties of the join operation,
utilizing results from processed data points to expedite the entire join process. Our extensive
experiments demonstrate that our proposed join algorithm outperforms all existing state-of-the-art
methods for approximate similarity joins by up to one order of magnitude with superior quality of
join results. Our future work will focus on developing a distributed algorithm based on our current
approach to offer a more scalable approximate similarity join method.

Acknowledgements
This work was supported by the Research Grants Council of Hong Kong, China, No.14205520, and
the National Natural Science Foundation of China, No.62002274.

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

0.90.951Recall@10102103104QPSglobal rebuildingFreshDiskANNk-similarity join0.90.951Recall@10102103104QPS0.90.951Recall@10102103104QPSFast Approximate Similarity Join in Vector Databases

158:25

References
[1] 2010. Datasets for approximate nearest neighbor search. http://corpus-texmex.irisa.fr/.
[2] 2023. Common Crawl. https://commoncrawl.org/.
[3] W. Ackermann. 1928. Zum Hilbertschen Aufbau der reellen Zahlen. Math. Ann. 99 (1928), 118–133.
[4] Martin Aumüller and Matteo Ceccarello. 2022. Implementing Distributed Similarity Joins using Locality Sensitive

Hashing. In EDBT 2022. OpenProceedings.org, 1:78–1:90.

[5] Pierre Baldi, Peter Sadowski, and Daniel Whiteson. 2014. Searching for exotic particles in high-energy physics with

deep learning. Nature communications 5, 1 (2014), 4308.

[6] Thierry Bertin-Mahieux, Daniel P. W. Ellis, Brian Whitman, and Paul Lamere. 2011. The Million Song Dataset. In
Proceedings of the 12th International Society for Music Information Retrieval Conference, ISMIR 2011. University of Miami,
591–596.

[7] Christian Böhm, Bernhard Braunmüller, Florian Krebs, and Hans-Peter Kriegel. 2001. Epsilon Grid Order: An Algorithm
for the Similarity Join on Massive High-Dimensional Data. In Proceedings of the 2001 ACM SIGMOD international
conference on Management of data. ACM, 379–388.

[8] Christian Böhm and Florian Krebs. 2004. The k-Nearest Neighbour Join: Turbo Charging the KDD Process. Knowl. Inf.

Syst. 6, 6 (2004), 728–749.

[9] Thomas Brinkhoff, Hans-Peter Kriegel, and Bernhard Seeger. 1993. Efficient Processing of Spatial Joins Using R-Trees.
In Proceedings of the 1993 ACM SIGMOD International Conference on Management of Data, Washington, DC, USA, May
26-28, 1993. ACM Press, 237–246.

[10] Qi Chen, Bing Zhao, Haidong Wang, Mingqin Li, Chuanjie Liu, Zengzhong Li, Mao Yang, and Jingdong Wang. 2021.
SPANN: Highly-efficient Billion-scale Approximate Nearest Neighborhood Search. In NeurIPS 2021. 5199–5212.
[11] Sheng Chen, Akshay Soni, Aasish Pappu, and Yashar Mehdad. 2017. DocTag2Vec: An Embedding Based Multi-
label Learning Approach for Document Tagging. In Rep4NLP@ACL 2017. Association for Computational Linguistics,
111–120.

[12] B. Delaunay. 1934. Sur la sphère vide. Bull. Acad. Sci. URSS 1934, 6 (1934), 793–800.
[13] Rex A Dwyer. 1989. Higher-dimensional Voronoi diagrams in linear expected time. In Proceedings of the fifth annual

symposium on Computational geometry. 326–333.

[14] Cong Fu, Chao Xiang, Changxu Wang, and Deng Cai. 2019. Fast Approximate Nearest Neighbor Search With The

Navigating Spreading-out Graph. Proc. VLDB Endow. 12, 5 (2019), 461–474.

[15] Harold N. Gabow and Robert Endre Tarjan. 1983. A Linear-Time Algorithm for a Special Case of Disjoint Set Union. In

Proceedings of the 15th Annual ACM Symposium on Theory of Computing. ACM, 246–251.

[16] Jianyang Gao and Cheng Long. 2024. RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound

for Approximate Nearest Neighbor Search. Proc. ACM Manag. Data 2, 3 (2024), 167.

[17] Aditya Grover and Jure Leskovec. 2016. node2vec: Scalable Feature Learning for Networks. In SIGKDD International

Conference on Knowledge Discovery and Data Mining. ACM, 855–864.

[18] Ruiqi Guo, Philip Sun, Erik Lindgren, Quan Geng, David Simcha, Felix Chern, and Sanjiv Kumar. 2020. Accelerating
Large-Scale Inference with Anisotropic Vector Quantization. In Proceedings of the 37th International Conference on
Machine Learning, ICML 2020 (Proceedings of Machine Learning Research, Vol. 119). PMLR, 3887–3896.

[19] Ben Harwood and Tom Drummond. 2016. FANNG: Fast Approximate Nearest Neighbour Graphs. In 2016 IEEE

Conference on Computer Vision and Pattern Recognition, CVPR 2016. IEEE Computer Society, 5713–5722.

[20] Xiao Hu, Ke Yi, and Yufei Tao. 2019. Output-Optimal Massively Parallel Algorithms for Similarity Joins. ACM Trans.

Database Syst. 44, 2 (2019), 6:1–6:36.

[21] Piotr Indyk and Rajeev Motwani. 1998. Approximate Nearest Neighbors: Towards Removing the Curse of Dimension-

ality. In Proceedings of the Thirtieth Annual ACM Symposium on the Theory of Computing. ACM, 604–613.

[22] Edwin H. Jacox and Hanan Samet. 2008. Metric space similarity joins. ACM Trans. Database Syst. 33, 2 (2008), 7:1–7:38.
[23] Dmitri V. Kalashnikov. 2013. Super-EGO: fast multi-dimensional similarity join. VLDB J. 22, 4 (2013), 561–585.
[24] Dmitri V. Kalashnikov and Sunil Prabhakar. 2007. Fast similarity join for multi-dimensional data. Inf. Syst. 32, 1 (2007),

160–177.

[25] Nick Koudas and Kenneth C. Sevcik. 2000. High Dimensional Similarity Joins: Algorithms and Performance Evaluation.

IEEE Trans. Knowl. Data Eng. 12, 1 (2000), 3–18.

[26] D. T. Lee and Bruce J. Schachter. 1980. Two algorithms for constructing a Delaunay triangulation. Int. J. Parallel

Program. 9, 3 (1980), 219–242.

[27] Hangyu Li, Sarana Nutanong, Hong Xu, Chenyun Yu, and Foryu Ha. 2019. C2Net: A Network-Efficient Approach to

Collision Counting LSH Similarity Join. IEEE Trans. Knowl. Data Eng. 31, 3 (2019), 423–436.

[28] Wen Li, Ying Zhang, Yifang Sun, Wei Wang, Mingjie Li, Wenjie Zhang, and Xuemin Lin. 2020. Approximate Nearest
Neighbor Search on High Dimensional Data - Experiments, Analyses, and Improvement. IEEE Trans. Knowl. Data Eng.
32, 8 (2020), 1475–1488.

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

158:26

Jiadong Xie, Jeffrey Xu Yu, and Yingfan Liu

[29] Youzhong Ma, Shijie Jia, and Yongxin Zhang. 2017. A novel approach for high-dimensional vector similarity join query.

Concurr. Comput. Pract. Exp. 29, 5 (2017).

[30] Yury A. Malkov and Dmitry A. Yashunin. 2020. Efficient and Robust Approximate Nearest Neighbor Search Using

Hierarchical Navigable Small World Graphs. IEEE Trans. Pattern Anal. Mach. Intell. 42, 4 (2020), 824–836.

[31] Ahmed Metwally and Christos Faloutsos. 2012. V-SMART-Join: A Scalable MapReduce Framework for All-Pair

Similarity Joins of Multisets and Vectors. Proc. VLDB Endow. 5, 8 (2012), 704–715.

[32] Tomás Mikolov, Ilya Sutskever, Kai Chen, Gregory S. Corrado, and Jeffrey Dean. 2013. Distributed Representations of
Words and Phrases and their Compositionality. In 27th Annual Conference on Neural Information Processing Systems
2013. 3111–3119.

[33] Nasser M Nasrabadi and Robert A King. 1988. Image coding using vector quantization: A review. IEEE Transactions on

communications 36, 8 (1988), 957–971.

[34] Yun Peng, Byron Choi, Tsz Nam Chan, Jianye Yang, and Jianliang Xu. 2023. Efficient Approximate Nearest Neighbor

Search in Multi-dimensional Databases. Proc. ACM Manag. Data 1, 1 (2023), 54:1–54:27.

[35] Jeffrey Pennington, Richard Socher, and Christopher D. Manning. 2014. Glove: Global Vectors for Word Representation.
In Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing, EMNLP 2014, A meeting of
SIGDAT, a Special Interest Group of the ACL. ACL, 1532–1543.

[36] Martin Perdacher, Claudia Plant, and Christian Böhm. 2019. Cache-oblivious High-performance Similarity Join. In
Proceedings of the 2019 International Conference on Management of Data, SIGMOD Conference 2019. ACM, 87–104.
[37] Sébastien Rivault, Mostafa Bamha, Sébastien Limet, and Sophie Robert. 2022. A Scalable Similarity Join Algorithm

Based on MapReduce and LSH. Int. J. Parallel Program. 50, 3-4 (2022), 360–380.

[38] Raimund Seidel. 1995. The Upper Bound Theorem for Polytopes: an Easy Proof of Its Asymptotic Version. Comput.

Geom. 5 (1995), 115–116.

[39] Kyuseok Shim, Ramakrishnan Srikant, and Rakesh Agrawal. 1997. High-Dimensional Similarity Joins. In ICDE. IEEE

Computer Society, 301–311.

[40] Aditi Singh, Suhas Jayaram Subramanya, Ravishankar Krishnaswamy, and Harsha Vardhan Simhadri. 2021.
FreshDiskANN: A Fast and Accurate Graph-Based ANN Index for Streaming Similarity Search. CoRR abs/2105.09613
(2021).

[41] SOAX. 2024. How many hours of video are uploaded to YouTube each minute? https://soax.com/research/how-many-

hours-of-video-are-uploaded-to-youtube-every-minute

[42] Narayanan Sundaram, Aizana Turmukhametova, Nadathur Satish, Todd Mostak, Piotr Indyk, Samuel Madden, and
Pradeep Dubey. 2013. Streaming Similarity Search over one Billion Tweets using Parallel Locality-Sensitive Hashing.
Proc. VLDB Endow. 6, 14 (2013), 1930–1941.

[43] Yukihiro Tagami. 2017. AnnexML: Approximate Nearest Neighbor Search for Extreme Multi-label Classification. In

SIGKDD. ACM, 455–464.

[44] Jianguo Wang, Xiaomeng Yi, Rentong Guo, Hai Jin, Peng Xu, Shengjun Li, Xiangyu Wang, Xiangzhou Guo, Chengming
Li, Xiaohai Xu, Kun Yu, Yuxing Yuan, Yinghao Zou, Jiquan Long, Yudong Cai, Zhenxiang Li, Zhifeng Zhang, Yihua
Mo, Jun Gu, Ruiyi Jiang, Yi Wei, and Charles Xie. 2021. Milvus: A Purpose-Built Vector Data Management System. In
SIGMOD ’21. ACM, 2614–2627.

[45] Mengzhao Wang, Xiaoliang Xu, Qiang Yue, and Yuxiang Wang. 2021. A Comprehensive Survey and Experimental
Comparison of Graph-Based Approximate Nearest Neighbor Search. Proc. VLDB Endow. 14, 11 (2021), 1964–1978.
[46] Yifan Wang, Vyom Pathak, and Daisy Zhe Wang. 2024. Xling: A Learned Filter Framework for Accelerating High-

Dimensional Approximate Similarity Join. CoRR abs/2402.13397 (2024).

[47] Shuo Yang, Jiadong Xie, Yingfan Liu, Jeffrey Xu Yu, Xiyue Gao, Qianru Wang, Yanguo Peng, and Jiangtao Cui.
2024. Revisiting the Index Construction of Proximity Graph-Based Approximate Nearest Neighbor Search. CoRR
abs/2410.01231 (2024).

[48] Cui Yu, Bin Cui, Shuguang Wang, and Jianwen Su. 2007. Efficient index-based KNN join processing for high-dimensional

data. Inf. Softw. Technol. 49, 4 (2007), 332–344.

[49] Chenyun Yu, Sarana Nutanong, Hangyu Li, Cong Wang, and Xingliang Yuan. 2017. A Generic Method for Accelerating

LSH-Based Similarity Join Processing. IEEE Trans. Knowl. Data Eng. 29, 4 (2017), 712–726.

[50] Xingliang Yuan, Xinyu Wang, Cong Wang, Chenyun Yu, and Sarana Nutanong. 2017. Privacy-Preserving Similarity

Joins Over Encrypted Data. IEEE Trans. Inf. Forensics Secur. 12, 11 (2017), 2763–2775.

[51] Qianxi Zhang, Shuotao Xu, Qi Chen, Guoxin Sui, Jiadong Xie, Zhizhen Cai, Yaoqi Chen, Yinxuan He, Yuqing Yang, Fan
Yang, Mao Yang, and Lidong Zhou. 2023. VBASE: Unifying Online Vector Similarity Search and Relational Queries
via Relaxed Monotonicity. In 17th USENIX Symposium on Operating Systems Design and Implementation, OSDI 2023.
USENIX Association, 377–395.

Received October 2024; revised January 2025; accepted February 2025

Proc. ACM Manag. Data, Vol. 3, No. 3 (SIGMOD), Article 158. Publication date: June 2025.

