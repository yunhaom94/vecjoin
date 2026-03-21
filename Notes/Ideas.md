# Ideas
This document contains the ideas and notes for the project.

## Piloting Idea
*Piloting idea is a single short paragraph that describes the initial idea for the project, could be big could also be small. This should not be changed.*

Using GPUs to do approximate vector similarity join for large, high-dimensional datasets. A main focus should be the use of DMA to reduce the overhead of data transfer between disk and VRAM.


## Main Ideas
*Main ideas are the core concepts and features of the project. This should be a short list between 3-5 ideas that can be changed as the project evolves. **Important:** this section should evolve over time, and the ideas should be refined and updated as the project progresses, and finally becomes a detailed design document for the project.*


- Using GPUs to do approximate vector join for large, high-dimensional datasets (Database Set `D` and query set `Q`). To accelerate the process, we construct vector indices on `D` and conduct clustering on `Q`. The search is first conducted between the cluster centers of `Q` and the vector indices of `D` to find the closest clusters, then we compare the vectors within the closest pair of clusters to find the final results.
  - We should try different indices methods, such as IVF, CAGAR, etc.
- Data allocation and scheduling strategies: this is a key part of the project. Since the data is too large to fit into both VRAM and RAM. We need to partition the data into smaller chunks, and design efficient data loading and scheduling strategies to minimize the data transfer overhead between disk, RAM, and VRAM. This is where the DMA can be used to further reduce the data transfer overhead. 
  - Decide where the indices, data partitions, and intermediate results should be stored, either in RAM or VRAM, and design efficient data loading and scheduling strategies to minimize the data transfer overhead between disk, RAM, and VRAM.
  - Develop partitioning strategies for both `D` and `Q` to further reduce the data transfer overhead and improve the search efficiency. Maybe use clustering for partitioning first, then build indices/clusters again for each partition when doing search.
- CUDA and GPU optimization, details TBD.

## Minor Ideas
*Minor ideas are supplementary concepts, features, writing points in the paper, or anything that is not directly related to one of the main ideas. This should be a list of any sizes that can be changed as the project evolves. Each idea should come with a detailed description.*

- Challenges with result sets on VRAM for each batch of comparisons.
- Evaluations
  - The dataset to use
  - The evaluation metrics to use
  - The baselines to compare with


# Notes
*Notes are any other thoughts, observations, or additional information that is relevant to the project but does not constitute as an "idea" which requires action. This can include things like background, potential challenges, or any other information that is useful for the project. This should be a list of any sizes that can be changed as the project evolves.*