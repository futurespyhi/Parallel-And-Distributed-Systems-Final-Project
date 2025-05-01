#!/usr/bin/env python3
# Sequential implementation of Breadth-First Search (BFS) algorithm for finding shortest paths in an unweighted graph

import sys
import os
import time
from collections import deque


def parse_input(input_file):
    """
    Parse input graph file in the format:
    nodeID    neighbor1,neighbor2,...

    Returns a dictionary representing the graph's adjacency list
    """
    graph = {}
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 2:
                continue

            node = parts[0]
            neighbors_str = parts[1]
            neighbors = neighbors_str.split(',')

            graph[node] = neighbors

    return graph


def bfs(graph, source):
    """
    Implement BFS algorithm to find shortest paths from source to all nodes

    Args:
        graph: Dictionary representing the graph's adjacency list
        source: Source node ID

    Returns:
        distances: Dictionary of shortest distances from source to all reachable nodes
        paths: Dictionary of shortest paths from source to all reachable nodes
    """
    # Initialize distances dictionary
    distances = {source: 0}

    # Initialize paths
    paths = {source: [source]}

    # Queue for BFS traversal
    queue = deque([source])

    # Set of visited nodes
    visited = {source}

    while queue:
        # Get next node to process
        current = queue.popleft()
        current_distance = distances[current]

        # Process all neighbors
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                # Mark as visited
                visited.add(neighbor)

                # Update distance and path
                distances[neighbor] = current_distance + 1
                paths[neighbor] = paths[current] + [neighbor]

                # Add to queue for processing
                queue.append(neighbor)

    return distances, paths


def main():
    """Main function to run sequential BFS algorithm"""
    if len(sys.argv) != 3:
        print("Usage: python bfs.py <input_graph_file> <source_node>")
        sys.exit(1)

    input_file = sys.argv[1]
    source_node = sys.argv[2]

    # Parse input graph
    print(f"Parsing input graph from {input_file}...")
    graph = parse_input(input_file)
    print(f"Graph loaded: {len(graph)} nodes")

    # Run BFS algorithm with timing
    print(f"Running BFS algorithm from source node {source_node}...")
    start_time = time.time()
    distances, paths = bfs(graph, source_node)
    end_time = time.time()

    # Calculate statistics
    execution_time = end_time - start_time
    num_nodes = len(graph)
    num_reachable = len(distances)

    # Output results
    print(f"Execution completed in {execution_time:.4f} seconds")
    print(f"Nodes in graph: {num_nodes}")
    print(f"Nodes reachable from source: {num_reachable}")

    # Save results to file
    os.makedirs("../../results", exist_ok=True)
    output_file = f"../../results/sequential_bfs_{source_node}.txt"

    with open(output_file, 'w') as f:
        f.write(f"Source node: {source_node}\n")
        f.write(f"Execution time: {execution_time:.4f} seconds\n")
        f.write(f"Nodes reachable: {num_reachable} out of {num_nodes}\n\n")

        f.write("Node\tDistance\tPath\n")
        for node, distance in sorted(distances.items()):
            path_str = '->'.join(paths.get(node, []))
            f.write(f"{node}\t{distance}\t{path_str}\n")

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()