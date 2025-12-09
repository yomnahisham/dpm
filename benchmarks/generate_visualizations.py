"""
generate_visualizations.py - create performance graphs and tables
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Dict

def load_results() -> List[Dict]:
    """load benchmark results"""
    results_path = Path(__file__).parent / "benchmark_results.json"
    if not results_path.exists():
        print("No benchmark results found. Run performance_test.py first.")
        return []
    
    with open(results_path, 'r') as f:
        return json.load(f)

def create_runtime_comparison(results: List[Dict]):
    """create runtime comparison graph"""
    algorithms = ["greedy", "backtracking"]
    categories = ["small_simple", "small_medium", "medium", "medium_large", "large"]
    
    # organize data by category and algorithm
    data = {cat: {alg: [] for alg in algorithms} for cat in categories}
    
    for result in results:
        cat = result.get("category", "")
        alg = result.get("algorithm", "")
        if cat in data and alg in data[cat]:
            data[cat][alg].append(result["runtime"])
    
    # calculate averages
    avg_data = {cat: {alg: np.mean(data[cat][alg]) if data[cat][alg] else 0 
                      for alg in algorithms} 
                for cat in categories}
    
    # create graph
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(categories))
    width = 0.35
    
    greedy_times = [avg_data[cat]["greedy"] for cat in categories]
    backtrack_times = [avg_data[cat]["backtracking"] for cat in categories]
    
    ax.bar(x - width/2, greedy_times, width, label='Greedy', color='#2ecc71')
    ax.bar(x + width/2, backtrack_times, width, label='Backtracking', color='#3498db')
    
    ax.set_xlabel('Test Case Category')
    ax.set_ylabel('Runtime (seconds)')
    ax.set_title('Algorithm Performance Comparison: Runtime vs Input Size')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    ax.set_yscale('log')  # log scale for better visualization
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'runtime_comparison.png', dpi=300)
    print("Created runtime_comparison.png")

def create_memory_comparison(results: List[Dict]):
    """create memory usage comparison graph"""
    algorithms = ["greedy", "backtracking"]
    categories = ["small_simple", "small_medium", "medium", "medium_large", "large"]
    
    data = {cat: {alg: [] for alg in algorithms} for cat in categories}
    
    for result in results:
        cat = result.get("category", "")
        alg = result.get("algorithm", "")
        if cat in data and alg in data[cat]:
            data[cat][alg].append(result["memory_peak"])
    
    avg_data = {cat: {alg: np.mean(data[cat][alg]) if data[cat][alg] else 0 
                      for alg in algorithms} 
                for cat in categories}
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(categories))
    width = 0.35
    
    greedy_mem = [avg_data[cat]["greedy"] for cat in categories]
    backtrack_mem = [avg_data[cat]["backtracking"] for cat in categories]
    
    ax.bar(x - width/2, greedy_mem, width, label='Greedy', color='#2ecc71')
    ax.bar(x + width/2, backtrack_mem, width, label='Backtracking', color='#3498db')
    
    ax.set_xlabel('Test Case Category')
    ax.set_ylabel('Peak Memory Usage (MB)')
    ax.set_title('Algorithm Performance Comparison: Memory Usage vs Input Size')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'memory_comparison.png', dpi=300)
    print("Created memory_comparison.png")

def create_scalability_graph(results: List[Dict]):
    """create scalability graph showing runtime vs number of packages"""
    algorithms = ["greedy", "backtracking"]
    
    data = {alg: {"packages": [], "runtime": []} for alg in algorithms}
    
    for result in results:
        alg = result.get("algorithm", "")
        if alg in data:
            data[alg]["packages"].append(result["packages"])
            data[alg]["runtime"].append(result["runtime"])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"greedy": "#2ecc71", "backtracking": "#3498db"}
    for alg in algorithms:
        if data[alg]["packages"]:
            # sort by packages
            sorted_data = sorted(zip(data[alg]["packages"], data[alg]["runtime"]))
            packages, runtimes = zip(*sorted_data)
            
            ax.plot(packages, runtimes, marker='o', label=alg.capitalize(), 
                   linewidth=2, color=colors[alg])
    
    ax.set_xlabel('Number of Packages')
    ax.set_ylabel('Runtime (seconds)')
    ax.set_title('Algorithm Scalability: Runtime vs Number of Packages')
    ax.legend()
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'scalability.png', dpi=300)
    print("Created scalability.png")

def create_performance_table(results: List[Dict]):
    """create performance summary table"""
    algorithms = ["greedy", "backtracking"]
    
    table_data = []
    for alg in algorithms:
        alg_results = [r for r in results if r.get("algorithm") == alg]
        if alg_results:
            avg_runtime = np.mean([r["runtime"] for r in alg_results])
            avg_memory = np.mean([r["memory_peak"] for r in alg_results])
            success_rate = sum(1 for r in alg_results if r["success"]) / len(alg_results) * 100
            max_packages = max([r["packages"] for r in alg_results])
            
            table_data.append({
                "Algorithm": alg.capitalize(),
                "Avg Runtime (s)": f"{avg_runtime:.3f}",
                "Avg Memory (MB)": f"{avg_memory:.2f}",
                "Success Rate (%)": f"{success_rate:.1f}",
                "Max Packages Tested": max_packages
            })
    
    # save as markdown table
    output_path = Path(__file__).parent / 'performance_table.md'
    with open(output_path, 'w') as f:
        f.write("# Performance Summary Table\n\n")
        f.write("| Algorithm | Avg Runtime (s) | Avg Memory (MB) | Success Rate (%) | Max Packages Tested |\n")
        f.write("|-----------|----------------|-----------------|------------------|---------------------|\n")
        for row in table_data:
            f.write(f"| {row['Algorithm']} | {row['Avg Runtime (s)']} | {row['Avg Memory (MB)']} | {row['Success Rate (%)']} | {row['Max Packages Tested']} |\n")
    
    print("Created performance_table.md")

def main():
    results = load_results()
    if not results:
        return
    
    print("Generating visualizations...")
    create_runtime_comparison(results)
    create_memory_comparison(results)
    create_scalability_graph(results)
    create_performance_table(results)
    print("\nAll visualizations created!")

if __name__ == "__main__":
    main()


