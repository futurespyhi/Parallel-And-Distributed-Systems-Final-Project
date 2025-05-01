#!/usr/bin/env python3
# Parallel implementation of Dijkstra's algorithm
# Uses a parallel frontier-based approach with synchronization after each distance threshold

import sys
import os
import time
import json
import heapq
import multiprocessing as mp
from functools import partial


def parse_input(input_file):
    """
    Parse input graph file in the format:
    nodeID    neighbor1:weight1,neighbor2:weight2,...

    Returns a dictionary representing the graph's adjacency list with weights
    """
    graph = {}
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 2:
                continue

            node = parts[0]
            neighbors_str = parts[1]
            neighbors = {}

            for neighbor_info in neighbors_str.split(','):
                if ':' in neighbor_info:
                    neighbor, weight = neighbor_info.split(':')
                    neighbors[neighbor] = float(weight)

            graph[node] = neighbors

    return graph


def process_node_batch(graph, current_distances, current_paths, node_batch, queue):
    """
    Process a batch of nodes in parallel and update distances and paths

    Args:
        graph: Dictionary representing the graph's adjacency list with weights
        current_distances: Dictionary of current known shortest distances
        current_paths: Dictionary of current known shortest paths
        node_batch: List of nodes to process in this batch
        queue: Multiprocessing queue to put results

    Returns: None (results are put in the queue)
    """
    local_updates = {}  # Store local distance updates
    local_paths = {}  # Store local path updates

    # Process all nodes in the batch
    for node in node_batch:
        node_distance = current_distances.get(node, float('infinity'))

        # Skip if node is not in current_distances (should not happen)
        if node_distance == float('infinity'):
            continue

        # Process all neighbors
        for neighbor, weight in graph.get(node, {}).items():
            # Calculate potential new distance
            distance = node_distance + weight

            # Update if shorter path found
            if distance < current_distances.get(neighbor, float('infinity')):
                local_updates[neighbor] = distance
                local_paths[neighbor] = current_paths.get(node, []) + [neighbor]

    # Put results in queue
    queue.put((local_updates, local_paths))


def parallel_dijkstra(graph, source, num_processes=None):
    """
    Implement parallel Dijkstra's algorithm using delta-stepping approach

    Args:
        graph: Dictionary representing the graph's adjacency list with weights
        source: Source node ID
        num_processes: Number of processes to use (defaults to CPU count)

    Returns:
        distances: Dictionary of shortest distances from source to all reachable nodes
        paths: Dictionary of shortest paths from source to all reachable nodes
    """
    if num_processes is None:
        num_processes = mp.cpu_count()

    # Initialize distances and paths
    distances = {source: 0}
    paths = {source: [source]}

    # Priority queue for nodes to visit (distance, node)
    pq = [(0, source)]

    # Keep track of processed nodes
    processed = set()

    # Statistics for iterations
    iterations_stats = []
    iteration = 0

    # Process nodes until priority queue is empty
    while pq:
        iteration_start = time.time()

        # Get current distance threshold
        current_min_dist, _ = pq[0]

        # Collect all nodes at the current distance threshold
        current_batch = []
        while pq and pq[0][0] == current_min_dist:
            _, node = heapq.heappop(pq)
            if node not in processed:
                current_batch.append(node)
                processed.add(node)

        # Skip if batch is empty
        if not current_batch:
            continue

        # Create batches for parallel processing
        batch_size = max(1, len(current_batch) // num_processes)
        batches = [current_batch[i:i + batch_size] for i in range(0, len(current_batch), batch_size)]

        # Create a queue for collecting results
        result_queue = mp.Queue()

        # Create processes
        processes = []
        for batch in batches:
            process = mp.Process(
                target=process_node_batch,
                args=(graph, distances, paths, batch, result_queue)
            )
            processes.append(process)
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()

        # Collect results from queue
        all_updates = {}
        all_paths = {}

        while not result_queue.empty():
            local_updates, local_paths = result_queue.get()
            # Merge updates
            for node, distance in local_updates.items():
                if node not in all_updates or distance < all_updates[node]:
                    all_updates[node] = distance
                    all_paths[node] = local_paths[node]

        # Apply updates globally
        for node, distance in all_updates.items():
            if node not in distances or distance < distances[node]:
                distances[node] = distance
                paths[node] = all_paths[node]
                heapq.heappush(pq, (distance, node))

        # Record statistics for this iteration
        iteration_end = time.time()
        iteration_time = iteration_end - iteration_start
        iterations_stats.append({
            "iteration": iteration,
            "nodes_processed": len(current_batch),
            "distance_threshold": current_min_dist,
            "duration": iteration_time
        })

        iteration += 1

    return distances, paths, iterations_stats


def main():
    """Main function to run parallel Dijkstra algorithm"""
    if len(sys.argv) != 4:
        print("Usage: python parallel_dijkstra.py <input_graph_file> <source_node> <num_processes>")
        sys.exit(1)

    input_file = sys.argv[1]
    source_node = sys.argv[2]
    num_processes = int(sys.argv[3])

    # Parse input graph
    print(f"Parsing input graph from {input_file}...")
    graph = parse_input(input_file)
    print(f"Graph loaded: {len(graph)} nodes")

    # Run parallel Dijkstra's algorithm with timing
    print(f"Running parallel Dijkstra's algorithm from source node {source_node} with {num_processes} processes...")
    start_time = time.time()
    distances, paths, iterations_stats = parallel_dijkstra(graph, source_node, num_processes)
    end_time = time.time()

    # Calculate statistics
    execution_time = end_time - start_time
    num_nodes = len(graph)
    num_reachable = len([d for d in distances.values() if d != float('infinity')])
    total_iterations = len(iterations_stats)

    # Output results
    print(f"Execution completed in {execution_time:.4f} seconds")
    print(f"Nodes in graph: {num_nodes}")
    print(f"Nodes reachable from source: {num_reachable}")
    print(f"Total iterations: {total_iterations}")

    # Save results to file
    os.makedirs("../../results", exist_ok=True)
    output_file = f"../../results/parallel_dijkstra_{source_node}.txt"
    stats_file = f"../../results/parallel_dijkstra_stats_{source_node}.json"

    with open(output_file, 'w') as f:
        f.write(f"Source node: {source_node}\n")
        f.write(f"Execution time: {execution_time:.4f} seconds\n")
        f.write(f"Nodes reachable: {num_reachable} out of {num_nodes}\n")
        f.write(f"Total iterations: {total_iterations}\n\n")

        f.write("Node\tDistance\tPath\n")
        for node, distance in sorted(distances.items()):
            if distance != float('infinity'):
                path_str = '->'.join(paths.get(node, []))
                f.write(f"{node}\t{distance}\t{path_str}\n")

    # Save detailed stats
    stats = {
        "algorithm": "Parallel Dijkstra",
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