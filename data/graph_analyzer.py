#!/usr/bin/env python3
# Simple Graph Data Analysis Script

import os
import sys
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from collections import Counter


def parse_bfs_file(file_path):
    """
    Parse BFS format file (unweighted graph)
    Format: nodeID    neighbor1,neighbor2,...
    """
    graph = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 2:
                continue

            node = parts[0]
            neighbors_str = parts[1]
            neighbors = neighbors_str.split(',')

            graph[node] = neighbors

    return graph


def parse_dijkstra_file(file_path):
    """
    Parse Dijkstra format file (weighted graph)
    Format: nodeID    neighbor1:weight1,neighbor2:weight2,...
    """
    graph = {}
    weighted_edges = []

    with open(file_path, 'r', encoding='utf-8') as f:
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
                    weight = float(weight)
                    neighbors[neighbor] = weight
                    weighted_edges.append((node, neighbor, weight))

            graph[node] = neighbors

    return graph, weighted_edges


def analyze_graph(file_path):
    """
    Analyze graph data file - simplified version
    """
    file_name = os.path.basename(file_path)
    print(f"Analyzing file: {file_name}")

    if "bfs" in file_name:
        graph = parse_bfs_file(file_path)
        is_weighted = False
        weighted_edges = None
    else:  # dijkstra
        graph, weighted_edges = parse_dijkstra_file(file_path)
        is_weighted = True

    # Basic statistics
    node_count = len(graph)

    # Calculate edge count and degrees
    edge_count = 0
    degrees = []
    for node, neighbors in graph.items():
        if is_weighted:
            num_neighbors = len(neighbors)
        else:
            num_neighbors = len(neighbors)
        edge_count += num_neighbors
        degrees.append(num_neighbors)

    # For undirected graphs, each edge is counted twice
    if "bfs" in file_name:
        edge_count //= 2

    # Calculate degree statistics
    avg_degree = np.mean(degrees)
    max_degree = np.max(degrees)
    min_degree = np.min(degrees)

    # Weight statistics (for weighted graphs)
    if is_weighted:
        weights = [weight for node, neighbors in graph.items()
                   for _, weight in neighbors.items()]
        avg_weight = np.mean(weights)
        max_weight = np.max(weights)
        min_weight = np.min(weights)
    else:
        avg_weight = max_weight = min_weight = None

    # Collect analysis results
    results = {
        "file_name": file_name,
        "is_weighted": is_weighted,
        "node_count": node_count,
        "edge_count": edge_count,
        "avg_degree": avg_degree,
        "max_degree": max_degree,
        "min_degree": min_degree,
        "degree_histogram": Counter(degrees),
    }

    # Add weight statistics for weighted graphs
    if is_weighted:
        results.update({
            "avg_weight": avg_weight,
            "max_weight": max_weight,
            "min_weight": min_weight,
        })

    return results


def create_basic_visualizations(results_list, output_dir):
    """
    Create simple visualizations
    """
    os.makedirs(output_dir, exist_ok=True)

    # Separate results by type
    bfs_results = [r for r in results_list if not r["is_weighted"]]
    dijkstra_results = [r for r in results_list if r["is_weighted"]]

    # Create node and edge count bar chart
    plt.figure(figsize=(10, 6))

    file_names = [r["file_name"].replace("_bfs.txt", "").replace("_dijkstra.txt", "")
                  for r in results_list]
    node_counts = [r["node_count"] for r in results_list]
    edge_counts = [r["edge_count"] for r in results_list]

    x = np.arange(len(file_names))
    width = 0.35

    plt.bar(x - width / 2, node_counts, width, label='Nodes')
    plt.bar(x + width / 2, edge_counts, width, label='Edges')

    plt.xlabel('Dataset')
    plt.ylabel('Count')
    plt.title('Graph Size Comparison')
    plt.xticks(x, file_names)
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "graph_size_comparison.png"))
    plt.close()

    # Create degree comparison
    plt.figure(figsize=(8, 6))

    avg_degrees = [r["avg_degree"] for r in results_list]
    labels = [f"{name}\n{r['node_count']} nodes" for name, r in zip(file_names, results_list)]

    plt.bar(x, avg_degrees)
    plt.xticks(x, labels)
    plt.ylabel('Average Degree')
    plt.title('Average Node Degree by Dataset')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "average_degree.png"))
    plt.close()

    # Create weight comparison for Dijkstra graphs
    if dijkstra_results:
        plt.figure(figsize=(8, 6))

        dijkstra_names = [r["file_name"].replace("_dijkstra.txt", "")
                          for r in dijkstra_results]
        avg_weights = [r["avg_weight"] for r in dijkstra_results]

        plt.bar(range(len(dijkstra_names)), avg_weights, color='purple')
        plt.xticks(range(len(dijkstra_names)), dijkstra_names)
        plt.ylabel('Average Weight')
        plt.title('Average Edge Weight by Dataset')

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "average_weight.png"))
        plt.close()


def save_summary(results_list, output_dir):
    """
    Save analysis summary as CSV
    """
    os.makedirs(output_dir, exist_ok=True)

    # Create summary data
    summary_data = []
    for result in results_list:
        row = {
            "File Name": result["file_name"],
            "Graph Type": "Weighted" if result["is_weighted"] else "Unweighted",
            "Node Count": result["node_count"],
            "Edge Count": result["edge_count"],
            "Average Degree": round(result["avg_degree"], 2),
            "Maximum Degree": result["max_degree"],
            "Minimum Degree": result["min_degree"],
        }

        if result["is_weighted"]:
            row.update({
                "Average Weight": round(result["avg_weight"], 2),
                "Maximum Weight": round(result["max_weight"], 2),
                "Minimum Weight": round(result["min_weight"], 2)
            })

        summary_data.append(row)

    # Save as CSV
    df = pd.DataFrame(summary_data)
    output_file = os.path.join(output_dir, "graph_summary.csv")
    df.to_csv(output_file, index=False)

    print(f"Summary saved to {output_file}")

    # Print summary table
    print("\nSummary of Graph Analysis:")
    print(df.to_string())


def main():
    """
    Main function
    """
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # Default to current directory
        data_dir = "."

    output_dir = "graph_analysis_results"

    print(f"Analyzing graph data files in {data_dir}...")

    # Find all BFS and Dijkstra files
    graph_files = []
    for file in os.listdir(data_dir):
        if file.endswith(("_bfs.txt", "_dijkstra.txt")):
            graph_files.append(os.path.join(data_dir, file))

    if not graph_files:
        print(f"No graph data files found in {data_dir}")
        return

    print(f"Found {len(graph_files)} graph data files")

    # Analyze each file
    results_list = []
    for file_path in graph_files:
        try:
            result = analyze_graph(file_path)
            results_list.append(result)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    # Create visualizations and save summary
    if results_list:
        create_basic_visualizations(results_list, output_dir)
        save_summary(results_list, output_dir)
        print(f"Analysis complete. Results saved to {output_dir}")
    else:
        print("No files were successfully analyzed")


if __name__ == "__main__":
    main()