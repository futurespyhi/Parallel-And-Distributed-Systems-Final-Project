import sys
import os
import time
import heapq


def parse_input(input_file):
    """
    Parse input graph file in the format:
    nodeID    neighbor1:weight1,neighbor2:weight2,...

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
            neighbors = {}

            for neighbor_info in neighbors_str.split(','):
                if ':' in neighbor_info:
                    neighbor, weight = neighbor_info.split(':')
                    neighbors[neighbor] = float(weight)

            graph[node] = neighbors

    return graph


def dijkstra(graph, source):
    """
    Implement Dijkstra's algorithm to find shortest paths from source to all nodes

    Args:
        graph: Dictionary representing the graph's adjacency list with weights
        source: Source node ID

    Returns:
        distances: Dictionary of shortest distances from source to all reachable nodes
        paths: Dictionary of shortest paths from source to all reachable nodes
    """
    # Initialize distances (infinity for all nodes except source)
    distances = {node: float('infinity') for node in graph}
    distances[source] = 0

    # Initialize paths
    paths = {source: [source]}

    # Priority queue for nodes to visit (distance, node)
    pq = [(0, source)]

    # Set of visited nodes
    visited = set()

    while pq:
        # Get node with minimum distance
        current_distance, current_node = heapq.heappop(pq)

        # Skip if already visited
        if current_node in visited:
            continue

        # Mark as visited
        visited.add(current_node)

        # Check all neighbors
        for neighbor, weight in graph.get(current_node, {}).items():
            # Calculate potential new distance
            distance = current_distance + weight

            # Update if shorter path found
            if distance < distances.get(neighbor, float('infinity')):
                distances[neighbor] = distance
                paths[neighbor] = paths.get(current_node, []) + [neighbor]
                heapq.heappush(pq, (distance, neighbor))

    return distances, paths


def main():
    """Main function to run sequential Dijkstra algorithm"""
    if len(sys.argv) != 3:
        print("Usage: python dijkstra.py <input_graph_file> <source_node>")
        sys.exit(1)

    input_file = sys.argv[1]
    source_node = sys.argv[2]

    # Parse input graph
    print(f"Parsing input graph from {input_file}...")
    graph = parse_input(input_file)
    print(f"Graph loaded: {len(graph)} nodes")

    # Run Dijkstra's algorithm with timing
    print(f"Running Dijkstra's algorithm from source node {source_node}...")
    start_time = time.time()
    distances, paths = dijkstra(graph, source_node)
    end_time = time.time()

    # Calculate statistics
    execution_time = end_time - start_time
    num_nodes = len(graph)
    num_reachable = len([d for d in distances.values() if d != float('infinity')])

    # Output results
    print(f"Execution completed in {execution_time:.4f} seconds")
    print(f"Nodes in graph: {num_nodes}")
    print(f"Nodes reachable from source: {num_reachable}")

    # Save results to file
    os.makedirs("../../results", exist_ok=True)
    output_file = f"../../results/sequential_dijkstra_{source_node}.txt"

    with open(output_file, 'w') as f:
        f.write(f"Source node: {source_node}\n")
        f.write(f"Execution time: {execution_time:.4f} seconds\n")
        f.write(f"Nodes reachable: {num_reachable} out of {num_nodes}\n\n")

        f.write("Node\tDistance\tPath\n")
        for node, distance in sorted(distances.items()):
            if distance != float('infinity'):
                path_str = '->'.join(paths.get(node, []))
                f.write(f"{node}\t{distance}\t{path_str}\n")

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()