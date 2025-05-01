#!/usr/bin/env python3
# Queue Partitioning Parallel BFS implementation
# Uses level-synchronized BFS with queue partitioning for exact path preservation

import sys
import os
import time
import json
from collections import deque
import multiprocessing as mp
import copy


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


def process_nodes(nodes_batch, graph, visited_copy):
    """
    Process a batch of nodes from the BFS queue

    Args:
        nodes_batch: List of nodes to process
        graph: The graph adjacency list
        visited_copy: Copy of the current visited set

    Returns:
        List of (neighbor, parent) pairs discovered
    """
    new_nodes = []  # List of (neighbor, parent) tuples

    # Process each node in the batch
    for node in nodes_batch:
        # Process all neighbors
        for neighbor in graph.get(node, []):
            # If neighbor hasn't been visited yet
            if neighbor not in visited_copy:
                # Mark it as visited in our local copy
                visited_copy.add(neighbor)
                # Add to new discoveries
                new_nodes.append((neighbor, node))

    return new_nodes


def parallel_bfs(graph, source, num_processes=None):
    """
    Implement BFS with queue partitioning for exact same paths as sequential BFS

    Args:
        graph: Dictionary representing the graph's adjacency list
        source: Source node ID
        num_processes: Number of processes to use (defaults to CPU count)

    Returns:
        distances: Dictionary of shortest distances from source to all reachable nodes
        paths: Dictionary of shortest paths from source to all reachable nodes
    """
    if num_processes is None:
        num_processes = mp.cpu_count()

    # Initialize distances and parent pointers
    distances = {source: 0}
    parents = {source: None}

    # Initialize visited set and queue
    visited = {source}
    queue = deque([source])

    # For statistics
    iteration = 0
    iterations_stats = []

    # Continue until queue is empty
    while queue:
        iteration_start = time.time()

        # Get the current size of the queue - all these nodes are at the same distance
        level_size = len(queue)

        # Use the current queue as the nodes to process in parallel
        # This ensures exact same paths as sequential BFS
        current_level_nodes = []
        for _ in range(level_size):
            if queue:
                current_level_nodes.append(queue.popleft())

        # If no nodes at this level, we're done
        if not current_level_nodes:
            break

        # Split nodes into batches for parallel processing
        batch_size = max(1, len(current_level_nodes) // num_processes)
        node_batches = [current_level_nodes[i:i + batch_size] for i in range(0, len(current_level_nodes), batch_size)]

        # Process batches in parallel
        pool = mp.Pool(processes=min(num_processes, len(node_batches)))

        # Make a copy of visited set for each worker
        visited_copies = [copy.deepcopy(visited) for _ in range(len(node_batches))]

        # Map the process_nodes function to each batch
        batch_results = pool.starmap(
            process_nodes,
            [(batch, graph, visited_copy) for batch, visited_copy in zip(node_batches, visited_copies)]
        )

        # Close the pool and wait for all processes to finish
        pool.close()
        pool.join()

        # Merge results - strictly in order of original node batches
        # This preserves the exact path ordering of sequential BFS
        current_distance = None
        for node in current_level_nodes:
            if node in distances:
                current_distance = distances[node] + 1
                break

        if current_distance is None:
            # This should never happen if implementation is correct
            current_distance = iteration + 1

        # Process each batch's results in order
        for batch_idx, batch_discoveries in enumerate(batch_results):
            # Process discoveries in the exact order they were found
            for neighbor, parent in batch_discoveries:
                # Only process if not already visited (in the global visited set)
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    distances[neighbor] = current_distance
                    parents[neighbor] = parent

        # Record statistics for this iteration
        iteration_end = time.time()
        iteration_time = iteration_end - iteration_start
        iterations_stats.append({
            "iteration": iteration,
            "nodes_processed": len(current_level_nodes),
            "duration": iteration_time
        })

        iteration += 1

    # Reconstruct paths from parents
    paths = {}
    for node in distances:
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = parents[current]
        paths[node] = list(reversed(path))

    return distances, paths, iterations_stats


def main():
    """Main function to run parallel BFS algorithm"""
    if len(sys.argv) != 4:
        print("Usage: python parallel_bfs.py <input_graph_file> <source_node> <num_processes>")
        sys.exit(1)

    input_file = sys.argv[1]
    source_node = sys.argv[2]
    num_processes = int(sys.argv[3])

    # Parse input graph
    print(f"Parsing input graph from {input_file}...")
    graph = parse_input(input_file)
    print(f"Graph loaded: {len(graph)} nodes")

    # Run parallel BFS algorithm with timing
    print(f"Running parallel BFS algorithm from source node {source_node} with {num_processes} processes...")
    start_time = time.time()
    distances, paths, iterations_stats = parallel_bfs(graph, source_node, num_processes)
    end_time = time.time()

    # Calculate statistics
    execution_time = end_time - start_time
    num_nodes = len(graph)
    num_reachable = len(distances)
    total_iterations = len(iterations_stats)

    # Output results
    print(f"Execution completed in {execution_time:.4f} seconds")
    print(f"Nodes in graph: {num_nodes}")
    print(f"Nodes reachable from source: {num_reachable}")
    print(f"Total iterations: {total_iterations}")

    # Save results to file
    os.makedirs("../../results", exist_ok=True)
    output_file = f"../../results/parallel_bfs_{source_node}.txt"
    stats_file = f"../../results/parallel_bfs_stats_{source_node}.json"

    with open(output_file, 'w') as f:
        f.write(f"Source node: {source_node}\n")
        f.write(f"Execution time: {execution_time:.4f} seconds\n")
        f.write(f"Nodes reachable: {num_reachable} out of {num_nodes}\n")
        f.write(f"Total iterations: {total_iterations}\n\n")

        f.write("Node\tDistance\tPath\n")
        for node, distance in sorted(distances.items()):
            path_str = '->'.join(paths.get(node, []))
            f.write(f"{node}\t{distance}\t{path_str}\n")

    # Save detailed stats
    stats = {
        "algorithm": "Parallel BFS",
        "source_node": source_node,
        "input_graph": input_file,
        "num_processes": num_processes,
        "total_execution_time": execution_time,
        "total_iterations": total_iterations,
        "total_nodes": num_nodes,
        "reachable_nodes": num_reachable,
        "iterations": iterations_stats
    }

    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"Results saved to {output_file}")
    print(f"Statistics saved to {stats_file}")


if __name__ == "__main__":
    main()