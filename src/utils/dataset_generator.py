#!/usr/bin/env python3
# Dataset generator for graph algorithms

import os
import random
import networkx as nx
import osmnx as ox
import time


def generate_osmx_datasets():
    """
    Generate graph datasets using OSMnx to extract street networks from OpenStreetMap.
    Creates three datasets of different sizes for both Dijkstra and BFS algorithms.
    """
    print("Generating graph datasets using OSMnx...")

    # Create output directories
    data_dir = "../../data"
    os.makedirs(data_dir, exist_ok=True)

    # Generate small graph (small town)
    print("Generating small graph dataset...")
    G_small = ox.graph_from_place("Ithaca, New York", network_type="drive")
    G_small = ox.truncate.largest_component(G_small, strongly=True)

    # Generate medium graph (mid-sized city)
    print("Generating medium graph dataset...")
    G_medium = ox.graph_from_place("Rochester, New York", network_type="drive")
    G_medium = ox.truncate.largest_component(G_medium, strongly=True)

    # Generate large graph (large city)
    print("Generating large graph dataset...")
    G_large = ox.graph_from_place("New York City, New York", network_type="drive")
    G_large = ox.truncate.largest_component(G_large, strongly=True)

    # Print dataset statistics
    print(f"Small graph: {len(G_small.nodes())} nodes, {len(G_small.edges())} edges")
    print(f"Medium graph: {len(G_medium.nodes())} nodes, {len(G_medium.edges())} edges")
    print(f"Large graph: {len(G_large.nodes())} nodes, {len(G_large.edges())} edges")

    # Save datasets for Dijkstra (weighted)
    save_graph_for_dijkstra(G_small, f"{data_dir}/small_dijkstra.txt")
    save_graph_for_dijkstra(G_medium, f"{data_dir}/medium_dijkstra.txt")
    save_graph_for_dijkstra(G_large, f"{data_dir}/large_dijkstra.txt")

    # Save datasets for BFS (unweighted)
    save_graph_for_bfs(G_small, f"{data_dir}/small_bfs.txt")
    save_graph_for_bfs(G_medium, f"{data_dir}/medium_bfs.txt")
    save_graph_for_bfs(G_large, f"{data_dir}/large_bfs.txt")

    # Select source nodes (one per dataset size)
    source_nodes = {
        "small": random.choice(list(G_small.nodes())),
        "medium": random.choice(list(G_medium.nodes())),
        "large": random.choice(list(G_large.nodes()))
    }

    # Save source nodes
    with open(f"{data_dir}/source_nodes.txt", 'w') as f:
        for size, node in source_nodes.items():
            f.write(f"{size}: {node}\n")

    print(f"Source nodes: {source_nodes}")
    print(f"Datasets generated and saved to {data_dir}")


def save_graph_for_dijkstra(G, output_file):
    """
    Save graph in Dijkstra format: nodeID neighbor1:weight1,neighbor2:weight2,...

    Args:
        G: NetworkX graph
        output_file: Path to output file
    """
    with open(output_file, 'w') as f:
        for node in G.nodes():
            neighbors = []
            for neighbor, edge_data in G[node].items():
                # Use edge length as weight
                weight = edge_data[0].get('length', 1.0)
                neighbors.append(f"{neighbor}:{weight}")

            if neighbors:  # Only write nodes with neighbors
                neighbors_str = ','.join(neighbors)
                f.write(f"{node}\t{neighbors_str}\n")


def save_graph_for_bfs(G, output_file):
    """
    Save graph in BFS format: nodeID neighbor1,neighbor2,...

    Args:
        G: NetworkX graph
        output_file: Path to output file
    """
    with open(output_file, 'w') as f:
        for node in G.nodes():
            neighbors = list(G.neighbors(node))

            if neighbors:  # Only write nodes with neighbors
                neighbors_str = ','.join(map(str, neighbors))
                f.write(f"{node}\t{neighbors_str}\n")


def generate_synthetic_datasets():
    """
    Generate synthetic graph datasets as an alternative to OSMnx.
    Useful when OSMnx is not available or real-world data is not needed.
    """
    print("Generating synthetic graph datasets...")

    # Create output directories
    data_dir = "../../data"
    os.makedirs(data_dir, exist_ok=True)

    # Parameters for different graph sizes
    sizes = {
        "small": 500,
        "medium": 5000,
        "large": 50000
    }

    # Generate and save datasets
    for size_name, n_nodes in sizes.items():
        print(f"Generating {size_name} synthetic graph...")

        # Generate random graph
        G = nx.gnm_random_graph(n_nodes, n_nodes * 2)

        # Make graph connected
        if not nx.is_connected(G):
            # Get largest connected component
            largest_cc = max(nx.connected_components(G), key=len)
            G = G.subgraph(largest_cc).copy()

        # Add random weights for Dijkstra
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(1, 10)

        # Save for Dijkstra (weighted)
        with open(f"{data_dir}/{size_name}_dijkstra.txt", 'w') as f:
            for node in G.nodes():
                neighbors = []
                for neighbor in G.neighbors(node):
                    weight = G[node][neighbor]['weight']
                    neighbors.append(f"{neighbor}:{weight}")

                if neighbors:
                    neighbors_str = ','.join(neighbors)
                    f.write(f"{node}\t{neighbors_str}\n")

        # Save for BFS (unweighted)
        with open(f"{data_dir}/{size_name}_bfs.txt", 'w') as f:
            for node in G.nodes():
                neighbors = list(G.neighbors(node))

                if neighbors:
                    neighbors_str = ','.join(map(str, neighbors))
                    f.write(f"{node}\t{neighbors_str}\n")

        print(f"{size_name.capitalize()} graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Select source nodes (one per dataset size)
    source_nodes = {size: random.randint(0, sizes[size] - 1) for size in sizes}

    # Save source nodes
    with open(f"{data_dir}/source_nodes.txt", 'w') as f:
        for size, node in source_nodes.items():
            f.write(f"{size}: {node}\n")

    print(f"Source nodes: {source_nodes}")
    print(f"Synthetic datasets generated and saved to {data_dir}")


def main():
    """Main function to generate datasets"""
    print("Graph Dataset Generator")
    print("======================")

    # Check if OSMnx is available
    try:
        import osmnx
        print("Using OSMnx to generate real-world street networks...")
        generate_osmx_datasets()
    except (ImportError, Exception) as e:
        print(f"Error with OSMnx: {e}")
        print("Generating synthetic graphs instead...")
        generate_synthetic_datasets()

    print("Dataset generation completed.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total generation time: {end_time - start_time:.2f} seconds")