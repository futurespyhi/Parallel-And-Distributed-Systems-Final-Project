# Parallel Graph Algorithms on OpenStreetMap Networks

This project implements and analyzes parallel versions of BFS and Dijkstra's shortest path algorithms on OpenStreetMap data. The implementation uses Python's multiprocessing library to achieve process-based parallelism.

## Project Overview

The goal of this project is to compare the performance of sequential and parallel implementations of two fundamental graph traversal algorithms:
- Breadth-First Search (BFS)
- Dijkstra's Shortest Path Algorithm

The algorithms are applied to real-world street network data of varying sizes from OpenStreetMap:
- Small dataset: Ithaca, NY
- Medium dataset: Rochester, NY
- Large dataset: New York City, NY

## Repository Structure

```
project/
├── src/
│   ├── parallel/
│   │   ├── bfs.py          # Parallel BFS implementation
│   │   └── dijkstra.py     # Parallel Dijkstra implementation
│   ├── sequential/
│   │   ├── bfs.py          # Sequential BFS implementation
│   │   └── dijkstra.py     # Sequential Dijkstra implementation
│   └── utils/
│       ├── dataset_generator.py  # Data preparation
│       └── result_analyzer.py    # Performance analysis
├── data/
│   ├── small_bfs.txt       # BFS format data for Ithaca
│   ├── medium_bfs.txt      # BFS format data for Rochester
│   ├── large_bfs.txt       # BFS format data for NYC
│   ├── small_dijkstra.txt  # Dijkstra format data for Ithaca
│   ├── medium_dijkstra.txt # Dijkstra format data for Rochester
│   ├── large_dijkstra.txt  # Dijkstra format data for NYC
│   └── source_nodes.txt    # Selected source nodes for experiments
├── results/                # Directory for experimental results
├── README.md               # This file
└── requirements.txt        # Required Python packages
```

## Requirements

- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - osmnx==1.2.2
  - networkx==2.8.8
  - matplotlib==3.6.2
  - pandas==1.5.2
  - numpy==1.23.5

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/futurespyhi/Parallel-And-Distributed-Systems-Final-Project.git
   cd Parallel-And-Distributed-Systems-Final-Project
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create required directories:
   ```
   mkdir -p data results
   ```

## Generating Datasets

The project uses OpenStreetMap data through the OSMnx library. To generate the datasets:

```
python src/utils/dataset_generator.py
```

This script will:
1. Download street networks for Ithaca, Rochester, and NYC from OpenStreetMap
2. Process them into appropriate formats for BFS and Dijkstra algorithms
3. Save the processed data to the `data/` directory
4. Select and save random source nodes for experiments

> Note: If OSMnx is not available or encounters issues with OpenStreetMap, the script will automatically fall back to generating synthetic graphs with similar properties.

## Running the Algorithms

### Sequential Implementations

To run the sequential BFS algorithm:
```
python src/sequential/bfs.py data/small_bfs.txt SOURCE_NODE
```

To run the sequential Dijkstra algorithm:
```
python src/sequential/dijkstra.py data/small_dijkstra.txt SOURCE_NODE
```

Replace `small_bfs.txt` or `small_dijkstra.txt` with the appropriate dataset file, and `SOURCE_NODE` with a node ID from the graph (or use one from `data/source_nodes.txt`).

### Parallel Implementations

To run the parallel BFS algorithm:
```
python src/parallel/bfs.py data/small_bfs.txt SOURCE_NODE NUM_PROCESSES
```

To run the parallel Dijkstra algorithm:
```
python src/parallel/dijkstra.py data/small_dijkstra.txt SOURCE_NODE NUM_PROCESSES
```

Replace `NUM_PROCESSES` with the desired number of processes (e.g., 2, 4, or 8).

## Analyzing Results

After running the algorithms, results are saved to the `results/` directory. To analyze and visualize the results:

```
python src/utils/result_analyzer.py
```

This script will:
1. Load all result files from the `results/` directory
2. Generate comparative performance tables
3. Create visualization plots (execution times, speedup, iteration counts, etc.)
4. Save the analysis outputs to the `results/` directory

## Data Formats

### BFS Format
```
nodeID    neighbor1,neighbor2,...
```

### Dijkstra Format
```
nodeID    neighbor1:weight1,neighbor2:weight2,...
```

## Implementation Details

### Sequential Implementations
- Standard implementations of BFS and Dijkstra algorithms
- BFS uses a queue-based approach
- Dijkstra uses a priority queue (Python's heapq)

### Parallel Implementations
- BFS: Level-synchronized approach with queue partitioning
- Dijkstra: Threshold-based approach with frontier partitioning
- Both use Python's multiprocessing for parallelism
- Special care is taken to preserve exact path correctness

## Notes on Performance

- The parallel implementations aim to produce identical paths to the sequential versions
- Python's multiprocessing introduces significant overhead
- Performance benefits are most apparent on larger graphs
- BFS generally shows better scaling with parallelism than Dijkstra

## Citations

The implementation is based on the following papers:
1. Crauser, A., Mehlhorn, K., Meyer, U., & Sanders, P. (1998). A Parallelization of Dijkstra's Shortest Path Algorithm. In Mathematical Foundations of Computer Science (pp. 722-731).
2. Meyer, U., & Sanders, P. (2003). Δ-stepping: A Parallelizable Shortest Path Algorithm. Journal of Algorithms, 49(1), 114-152.
3. Beamer, S., Asanović, K., & Patterson, D. (2012). Direction-optimizing Breadth-first Search. In Proceedings of the International Conference on High Performance Computing, Networking, Storage and Analysis (pp. 1-10).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Norton Gu
