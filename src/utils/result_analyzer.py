#!/usr/bin/env python3
# Results analyzer for graph algorithms - incorporating parallel implementation results

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


def load_results(results_dir):
    """
    Load all result files from the given directory.

    Args:
        results_dir: Path to results directory

    Returns:
        Dictionary containing performance data for each algorithm and dataset
    """
    print(f"Loading results from {results_dir}...")

    # Initialize data collection structures
    results = {}

    # Read sequential Dijkstra results
    seq_dijkstra_files = [f for f in os.listdir(results_dir) if f.startswith("sequential_dijkstra_")]
    for file in seq_dijkstra_files:
        source_node = file.split('_')[-1].split('.')[0]
        data = {"algorithm": "Sequential Dijkstra", "source_node": source_node}

        # Extract size from filename if available, otherwise infer from performance
        if "small" in file:
            data["size"] = "small"
        elif "medium" in file:
            data["size"] = "medium"
        elif "large" in file:
            data["size"] = "large"
        else:
            data["size"] = "unknown"

        with open(os.path.join(results_dir, file), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "Execution time:" in line:
                    data["execution_time"] = float(line.split(':')[1].strip().split()[0])
                elif "Nodes reachable:" in line:
                    parts = line.split(':')[1].strip().split()
                    data["reachable_nodes"] = int(parts[0])
                    data["total_nodes"] = int(parts[-1])

        # Add to results
        key = f"sequential_dijkstra_{data['size']}"
        results[key] = data

    # Read sequential BFS results
    seq_bfs_files = [f for f in os.listdir(results_dir) if f.startswith("sequential_bfs_")]
    for file in seq_bfs_files:
        source_node = file.split('_')[-1].split('.')[0]
        data = {"algorithm": "Sequential BFS", "source_node": source_node}

        # Extract size from filename if available, otherwise infer from performance
        if "small" in file:
            data["size"] = "small"
        elif "medium" in file:
            data["size"] = "medium"
        elif "large" in file:
            data["size"] = "large"
        else:
            data["size"] = "unknown"

        with open(os.path.join(results_dir, file), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "Execution time:" in line:
                    data["execution_time"] = float(line.split(':')[1].strip().split()[0])
                elif "Nodes reachable:" in line:
                    parts = line.split(':')[1].strip().split()
                    data["reachable_nodes"] = int(parts[0])
                    data["total_nodes"] = int(parts[-1])

        # Add to results
        key = f"sequential_bfs_{data['size']}"
        results[key] = data

    # Read parallel Dijkstra stats
    par_dijkstra_files = [f for f in os.listdir(results_dir) if f.startswith("parallel_dijkstra_stats_")]
    for file in par_dijkstra_files:
        with open(os.path.join(results_dir, file), 'r') as f:
            stats = json.load(f)
            data = {
                "algorithm": "Parallel Dijkstra",
                "source_node": stats["source_node"],
                "execution_time": stats["total_execution_time"],
                "iterations": stats["total_iterations"],
                "reachable_nodes": stats["reachable_nodes"],
                "num_processes": stats["num_processes"]
            }

            # Extract size from input graph
            if "small" in stats["input_graph"]:
                data["size"] = "small"
            elif "medium" in stats["input_graph"]:
                data["size"] = "medium"
            elif "large" in stats["input_graph"]:
                data["size"] = "large"
            else:
                data["size"] = "unknown"

            # Add detailed iteration stats
            data["iteration_times"] = [it["duration"] for it in stats["iterations"]]

            # Add to results
            key = f"parallel_dijkstra_{data['size']}_{data['num_processes']}"
            results[key] = data

    # Read parallel BFS stats
    par_bfs_files = [f for f in os.listdir(results_dir) if f.startswith("parallel_bfs_stats_")]
    for file in par_bfs_files:
        with open(os.path.join(results_dir, file), 'r') as f:
            stats = json.load(f)
            data = {
                "algorithm": "Parallel BFS",
                "source_node": stats["source_node"],
                "execution_time": stats["total_execution_time"],
                "iterations": stats["total_iterations"],
                "reachable_nodes": stats["reachable_nodes"],
                "num_processes": stats["num_processes"]
            }

            # Extract size from input graph
            if "small" in stats["input_graph"]:
                data["size"] = "small"
            elif "medium" in stats["input_graph"]:
                data["size"] = "medium"
            elif "large" in stats["input_graph"]:
                data["size"] = "large"
            else:
                data["size"] = "unknown"

            # Add detailed iteration stats
            data["iteration_times"] = [it["duration"] for it in stats["iterations"]]

            # Add to results
            key = f"parallel_bfs_{data['size']}_{data['num_processes']}"
            results[key] = data

    print(f"Loaded {len(results)} result sets")
    return results


def create_comparison_table(results):
    """
    Create a comparison table of algorithm performance.

    Args:
        results: Dictionary of results

    Returns:
        DataFrame with performance comparison
    """
    # Prepare data for DataFrame
    data = []

    # Group results by size
    by_size = defaultdict(list)
    for key, result in results.items():
        by_size[result["size"]].append(result)

    # Process each size category
    for size in ["small", "medium", "large"]:
        if size not in by_size:
            continue

        size_results = by_size[size]

        # Get sequential results
        seq_dijkstra = next((r for r in size_results if r["algorithm"] == "Sequential Dijkstra"), None)
        seq_bfs = next((r for r in size_results if r["algorithm"] == "Sequential BFS"), None)

        # Get parallel results with different process counts
        par_dijkstra_results = [r for r in size_results if r["algorithm"] == "Parallel Dijkstra"]
        par_bfs_results = [r for r in size_results if r["algorithm"] == "Parallel BFS"]

        # Add Dijkstra results
        if seq_dijkstra:
            data.append({
                "Size": size.capitalize(),
                "Algorithm": "Dijkstra",
                "Implementation": "Sequential",
                "Processes": 1,
                "Execution Time (s)": seq_dijkstra["execution_time"],
                "Iterations": 1,  # Sequential runs in a single pass
                "Reachable Nodes": seq_dijkstra.get("reachable_nodes", "N/A"),
                "Speedup": 1.0  # Reference for speedup
            })

        for par_dijkstra in sorted(par_dijkstra_results, key=lambda x: x.get("num_processes", 0)):
            if seq_dijkstra:
                speedup = seq_dijkstra["execution_time"] / par_dijkstra["execution_time"]
            else:
                speedup = None

            data.append({
                "Size": size.capitalize(),
                "Algorithm": "Dijkstra",
                "Implementation": "Parallel",
                "Processes": par_dijkstra.get("num_processes", "N/A"),
                "Execution Time (s)": par_dijkstra["execution_time"],
                "Iterations": par_dijkstra.get("iterations", "N/A"),
                "Reachable Nodes": par_dijkstra.get("reachable_nodes", "N/A"),
                "Speedup": speedup
            })

        # Add BFS results
        if seq_bfs:
            data.append({
                "Size": size.capitalize(),
                "Algorithm": "BFS",
                "Implementation": "Sequential",
                "Processes": 1,
                "Execution Time (s)": seq_bfs["execution_time"],
                "Iterations": 1,  # Sequential runs in a single pass
                "Reachable Nodes": seq_bfs.get("reachable_nodes", "N/A"),
                "Speedup": 1.0  # Reference for speedup
            })

        for par_bfs in sorted(par_bfs_results, key=lambda x: x.get("num_processes", 0)):
            if seq_bfs:
                speedup = seq_bfs["execution_time"] / par_bfs["execution_time"]
            else:
                speedup = None

            data.append({
                "Size": size.capitalize(),
                "Algorithm": "BFS",
                "Implementation": "Parallel",
                "Processes": par_bfs.get("num_processes", "N/A"),
                "Execution Time (s)": par_bfs["execution_time"],
                "Iterations": par_bfs.get("iterations", "N/A"),
                "Reachable Nodes": par_bfs.get("reachable_nodes", "N/A"),
                "Speedup": speedup
            })

    # Create DataFrame
    df = pd.DataFrame(data)

    return df


def plot_execution_times(df, output_dir):
    """
    Plot execution times for different algorithms and implementations.

    Args:
        df: DataFrame with performance data
        output_dir: Directory to save plots
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Set up the figure
    plt.figure(figsize=(14, 8))

    # Plot execution times grouped by size and algorithm
    sizes = df["Size"].unique()
    algorithms = df["Algorithm"].unique()

    # Set up x-axis positions
    x = np.arange(len(sizes))
    width = 0.15  # Width of bars

    # Define colors for different implementations
    colors = {
        ("Dijkstra", "Sequential"): "royalblue",
        ("Dijkstra", "Parallel", 2): "lightblue",
        ("Dijkstra", "Parallel", 4): "skyblue",
        ("Dijkstra", "Parallel", 8): "powderblue",
        ("BFS", "Sequential"): "forestgreen",
        ("BFS", "Parallel", 2): "lightgreen",
        ("BFS", "Parallel", 4): "palegreen",
        ("BFS", "Parallel", 8): "springgreen"
    }

    # Plot bars for each algorithm and implementation
    bar_positions = []
    for i, algo in enumerate(algorithms):
        if algo == "Dijkstra":
            base_offset = -width * 1.5
        else:
            base_offset = width * 1.5

        # Plot sequential first
        seq_data = df[(df["Algorithm"] == algo) & (df["Implementation"] == "Sequential")]
        if not seq_data.empty:
            times = []
            for size in sizes:
                time_val = seq_data[seq_data["Size"] == size]["Execution Time (s)"].values
                times.append(time_val[0] if len(time_val) > 0 else 0)

            plt.bar(x + base_offset, times, width,
                    label=f"{algo} Sequential",
                    color=colors.get((algo, "Sequential"), "gray"))
            bar_positions.append(base_offset)

        # Plot parallel with different process counts
        parallel_data = df[(df["Algorithm"] == algo) & (df["Implementation"] == "Parallel")]
        if not parallel_data.empty:
            process_counts = sorted(parallel_data["Processes"].unique())

            for j, procs in enumerate(process_counts):
                proc_data = parallel_data[parallel_data["Processes"] == procs]

                if not proc_data.empty:
                    times = []
                    for size in sizes:
                        time_val = proc_data[proc_data["Size"] == size]["Execution Time (s)"].values
                        times.append(time_val[0] if len(time_val) > 0 else 0)

                    offset = base_offset + (j + 1) * width * 0.75 * (1 if algo == "Dijkstra" else 1)
                    plt.bar(x + offset, times, width,
                            label=f"{algo} Parallel ({procs} processes)",
                            color=colors.get((algo, "Parallel", procs), f"C{j + 2}"))
                    bar_positions.append(offset)

    # Set labels and title
    plt.xlabel("Dataset Size")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Execution Time Comparison")
    plt.xticks(x, sizes)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "execution_times.png"), dpi=300)
    plt.close()


def plot_speedup_comparison(df, output_dir):
    """
    Plot speedup comparison for different algorithms and process counts.

    Args:
        df: DataFrame with performance data
        output_dir: Directory to save plots
    """
    # Filter data to include only parallel implementations with speedup info
    parallel_df = df[df["Implementation"] == "Parallel"].dropna(subset=["Speedup"])

    if parallel_df.empty:
        print("No speedup data available for plotting")
        return

    # Set up the figure
    plt.figure(figsize=(12, 8))

    # Plot speedup by size, algorithm, and process count
    sizes = parallel_df["Size"].unique()
    algorithms = parallel_df["Algorithm"].unique()

    # Create categorical size for proper ordering
    size_order = ["Small", "Medium", "Large"]

    # Set markers and colors for different algorithms
    markers = {"Dijkstra": ["o", "s", "D"], "BFS": ["^", "v", "*"]}
    colors = {"Dijkstra": "blue", "BFS": "green"}

    # Plot lines for each algorithm and process count
    for algo in algorithms:
        algo_data = parallel_df[parallel_df["Algorithm"] == algo]
        process_counts = sorted(algo_data["Processes"].unique())

        for i, procs in enumerate(process_counts):
            proc_data = algo_data[algo_data["Processes"] == procs]

            # Sort by size
            proc_data["Size"] = pd.Categorical(proc_data["Size"],
                                               categories=size_order,
                                               ordered=True)
            proc_data = proc_data.sort_values("Size")

            # Plot line
            plt.plot(proc_data["Size"], proc_data["Speedup"],
                     marker=markers.get(algo, ["x"])[min(i, len(markers.get(algo, ["x"])) - 1)],
                     color=colors.get(algo, "gray"),
                     label=f"{algo} ({procs} processes)",
                     linewidth=2)

    # Set labels and title
    plt.xlabel("Dataset Size")
    plt.ylabel("Speedup (Sequential / Parallel)")
    plt.title("Speedup Comparison by Algorithm, Process Count, and Dataset Size")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "speedup_comparison.png"), dpi=300)
    plt.close()


def plot_iterations_comparison(df, results, output_dir):
    """
    Plot iteration count and per-iteration time for parallel implementations.

    Args:
        df: DataFrame with performance data
        results: Original results dictionary with detailed iteration data
        output_dir: Directory to save plots
    """
    # Filter parallel implementations
    parallel_df = df[df["Implementation"] == "Parallel"]

    if parallel_df.empty:
        print("No parallel implementation data available for plotting")
        return

    # Set up the figure for iteration counts
    plt.figure(figsize=(12, 8))

    # Plot iteration counts by size, algorithm and process count
    sizes = parallel_df["Size"].unique()
    algorithms = parallel_df["Algorithm"].unique()

    # Set up x-axis positions
    x = np.arange(len(sizes))
    width = 0.15  # Width of bars

    # Plot bars for each algorithm and process count
    bar_positions = []
    for i, algo in enumerate(algorithms):
        algo_data = parallel_df[parallel_df["Algorithm"] == algo]
        if algo_data.empty:
            continue

        process_counts = sorted(algo_data["Processes"].unique())

        for j, procs in enumerate(process_counts):
            proc_data = algo_data[algo_data["Processes"] == procs]

            if not proc_data.empty:
                # Get iteration counts for each size
                iterations = []
                for size in sizes:
                    iter_val = proc_data[proc_data["Size"] == size]["Iterations"].values
                    iterations.append(iter_val[0] if len(iter_val) > 0 else 0)

                # Calculate bar position
                if i == 0:  # Dijkstra
                    offset = -width * 2 + j * width
                else:  # BFS
                    offset = width + j * width

                plt.bar(x + offset, iterations, width,
                        label=f"{algo} ({procs} processes)")
                bar_positions.append(offset)

    # Set labels and title
    plt.xlabel("Dataset Size")
    plt.ylabel("Number of Iterations")
    plt.title("Iteration Count Comparison for Parallel Implementations")
    plt.xticks(x, sizes)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "iteration_counts.png"), dpi=300)
    plt.close()

    # Plot per-iteration times
    # Collect data for parallel implementations with iteration_times
    iter_data = []
    for key, result in results.items():
        if "Parallel" in result["algorithm"] and "iteration_times" in result:
            for i, time in enumerate(result["iteration_times"]):
                iter_data.append({
                    "Algorithm": result["algorithm"].split()[1],  # Remove "Parallel" prefix
                    "Size": result["size"].capitalize(),
                    "Processes": result.get("num_processes", "N/A"),
                    "Iteration": i + 1,
                    "Time": time
                })

    if not iter_data:
        print("No iteration time data available for plotting")
        return

    # Create DataFrame for iteration times
    iter_df = pd.DataFrame(iter_data)

    # Plot iteration times for each algorithm, size, and process count
    for algo in iter_df["Algorithm"].unique():
        for size in iter_df["Size"].unique():
            plt.figure(figsize=(12, 8))

            proc_counts = sorted(iter_df[(iter_df["Algorithm"] == algo) &
                                         (iter_df["Size"] == size)]["Processes"].unique())

            for procs in proc_counts:
                data = iter_df[(iter_df["Algorithm"] == algo) &
                               (iter_df["Size"] == size) &
                               (iter_df["Processes"] == procs)]

                if not data.empty:
                    plt.plot(data["Iteration"], data["Time"],
                             marker="o",
                             label=f"{procs} processes",
                             linewidth=2)

            plt.xlabel("Iteration Number")
            plt.ylabel("Execution Time (seconds)")
            plt.title(f"Per-Iteration Execution Time for Parallel {algo} - {size} Dataset")
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.legend()

            # Save plot
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"iteration_times_{algo.lower()}_{size.lower()}.png"), dpi=300)
            plt.close()


def plot_scaling_efficiency(df, output_dir):
    """
    Plot scaling efficiency (speedup / number of processes) for parallel implementations.

    Args:
        df: DataFrame with performance data
        output_dir: Directory to save plots
    """
    # Filter data to include only parallel implementations with speedup info
    parallel_df = df[df["Implementation"] == "Parallel"].dropna(subset=["Speedup", "Processes"])

    if parallel_df.empty:
        print("No scaling efficiency data available for plotting")
        return

    # Calculate scaling efficiency
    parallel_df["Efficiency"] = parallel_df["Speedup"] / parallel_df["Processes"]

    # Set up the figure
    plt.figure(figsize=(12, 8))

    # Plot efficiency by processes, size, and algorithm
    sizes = parallel_df["Size"].unique()
    algorithms = parallel_df["Algorithm"].unique()

    # Set markers and colors for different algorithms
    markers = {"Dijkstra": "o", "BFS": "s"}
    colors = {"Dijkstra": "blue", "BFS": "green"}

    # Plot lines for each algorithm and size
    for algo in algorithms:
        for size in sizes:
            size_data = parallel_df[(parallel_df["Algorithm"] == algo) &
                                    (parallel_df["Size"] == size)]

            if not size_data.empty:
                # Sort by process count
                size_data = size_data.sort_values("Processes")

                # Plot line
                plt.plot(size_data["Processes"], size_data["Efficiency"],
                         marker=markers.get(algo, "x"),
                         color=colors.get(algo, "gray"),
                         label=f"{algo} - {size}",
                         linewidth=2)

    # Add ideal efficiency line (1.0)
    proc_counts = sorted(parallel_df["Processes"].unique())
    if proc_counts:
        plt.plot(proc_counts, [1.0] * len(proc_counts), 'k--', label='Ideal Efficiency')

    # Set labels and title
    plt.xlabel("Number of Processes")
    plt.ylabel("Scaling Efficiency (Speedup / Processes)")
    plt.title("Scaling Efficiency by Algorithm and Dataset Size")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "scaling_efficiency.png"), dpi=300)
    plt.close()


def save_results_to_csv(df, output_dir):
    """
    Save results to CSV file.

    Args:
        df: DataFrame with performance data
        output_dir: Directory to save CSV file
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save to CSV
    csv_path = os.path.join(output_dir, "performance_comparison.csv")
    df.to_csv(csv_path, index=False)
    print(f"Results saved to {csv_path}")


def main():
    """Main function to analyze results"""
    print("Graph Algorithm Results Analyzer")
    print("===============================")

    # Load results
    results_dir = "../../results"
    output_dir = "../../analysis"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load results
    results = load_results(results_dir)

    # Create comparison table
    df = create_comparison_table(results)

    # Display table
    print("\nPerformance Comparison:")
    print(df)

    # Plot results
    print("\nGenerating plots...")
    plot_execution_times(df, output_dir)
    plot_speedup_comparison(df, output_dir)
    plot_iterations_comparison(df, results, output_dir)
    plot_scaling_efficiency(df, output_dir)

    # Save results to CSV
    save_results_to_csv(df, output_dir)

    print(f"\nAnalysis completed. Results saved to {output_dir}")


if __name__ == "__main__":
    main()