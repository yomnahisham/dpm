"""
performance_test.py - benchmark greedy vs backtracking algorithms
"""

import sys
import time
import tracemalloc
from pathlib import Path

# add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dpm.resolver.greedy import GreedyResolver
from dpm.resolver.backtrack import BacktrackResolver
from dpm.sources.pypi import PyPISource
from dpm.sources.npm import NpmSource
from dpm.sources.system import SystemSource
from dpm.sources.local import LocalSource
from dpm.network.cache import Cache
from typing import List, Dict, Tuple
import json


class PerformanceBenchmark:
    """benchmark performance of resolution algorithms"""
    
    def __init__(self):
        self.cache = Cache()
        self.sources = [
            PyPISource(self.cache),
            NpmSource(self.cache),
            SystemSource(),
            LocalSource()
        ]
        self.greedy_resolver = GreedyResolver()
        self.backtrack_resolver = BacktrackResolver()
    
    def benchmark_resolution(self, packages: List[str], algorithm: str = "greedy") -> Dict:
        """benchmark a single resolution attempt"""
        result = {
            "packages": len(packages),
            "package_names": packages,
            "algorithm": algorithm,
            "success": False,
            "runtime": 0.0,
            "memory_peak": 0,
            "memory_current": 0,
            "packages_resolved": 0,
            "combinations_tried": 0
        }
        
        # start memory tracking
        tracemalloc.start()
        
        # measure runtime
        start_time = time.time()
        
        try:
            if algorithm == "backtracking":
                backtrack_result = self.backtrack_resolver.resolve(
                    packages, {}, self.sources
                )
                result["success"] = backtrack_result.success
                result["packages_resolved"] = len(backtrack_result.selected_versions)
            else:  # greedy
                greedy_result = self.greedy_resolver.resolve(packages, self.sources)
                result["success"] = greedy_result.success
                result["packages_resolved"] = len(greedy_result.selected_versions)
        except Exception as e:
            result["error"] = str(e)
        
        end_time = time.time()
        result["runtime"] = end_time - start_time
        
        # get memory stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        result["memory_peak"] = peak / (1024 * 1024)  # MB
        result["memory_current"] = current / (1024 * 1024)  # MB
        
        return result
    
    def run_test_suite(self) -> List[Dict]:
        """run comprehensive test suite"""
        results = []
        
        # test cases of varying complexity
        test_cases = [
            # Small cases (1-2 packages) - greedy should handle
            (["requests"], "small_simple"),
            (["flask"], "small_simple"),
            (["requests", "flask"], "small_medium"),
            (["numpy", "pandas"], "small_medium"),
            
            # Medium cases (4-5 packages) - test both algorithms
            (["django", "flask", "requests", "numpy"], "medium"),
            (["flask", "django", "numpy", "pandas", "matplotlib"], "medium_large"),
            
            # Large cases (10+ packages) - test both, may need backtracking
            (["django", "flask", "requests", "numpy", "pandas", "scipy", 
              "matplotlib", "seaborn", "jupyter", "ipython"], "large"),
        ]
        
        print("Running performance benchmarks...")
        print("=" * 60)
        
        for packages, category in test_cases:
            print(f"\nTesting {category}: {len(packages)} packages")
            print(f"Packages: {', '.join(packages)}")
            
            # test greedy
            print("  Testing greedy algorithm...")
            greedy_result = self.benchmark_resolution(packages, algorithm="greedy")
            greedy_result["category"] = category
            results.append(greedy_result)
            
            print(f"    Success: {greedy_result['success']}")
            print(f"    Runtime: {greedy_result['runtime']:.3f}s")
            print(f"    Memory: {greedy_result['memory_peak']:.2f} MB")
            print(f"    Packages resolved: {greedy_result['packages_resolved']}")
            
            # test backtracking for comparison (especially for larger cases)
            # always test backtracking for medium+ cases, and when greedy fails
            if category in ["medium", "medium_large", "large"] or not greedy_result['success']:
                print("  Testing backtracking algorithm...")
                backtrack_result = self.benchmark_resolution(packages, algorithm="backtracking")
                backtrack_result["category"] = category
                results.append(backtrack_result)
                
                print(f"    Success: {backtrack_result['success']}")
                print(f"    Runtime: {backtrack_result['runtime']:.3f}s")
                print(f"    Memory: {backtrack_result['memory_peak']:.2f} MB")
                print(f"    Packages resolved: {backtrack_result['packages_resolved']}")
            
            # also test backtracking on some small cases for comparison
            elif category in ["small_medium"] and len(packages) == 2:
                print("  Testing backtracking algorithm (for comparison)...")
                backtrack_result = self.benchmark_resolution(packages, algorithm="backtracking")
                backtrack_result["category"] = category
                results.append(backtrack_result)
                
                print(f"    Success: {backtrack_result['success']}")
                print(f"    Runtime: {backtrack_result['runtime']:.3f}s")
                print(f"    Memory: {backtrack_result['memory_peak']:.2f} MB")
                print(f"    Packages resolved: {backtrack_result['packages_resolved']}")
        
        return results
    
    def save_results(self, results: List[Dict], filename: str = "benchmark_results.json"):
        """save results to JSON file"""
        output_path = Path(__file__).parent / filename
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")


def main():
    benchmark = PerformanceBenchmark()
    results = benchmark.run_test_suite()
    benchmark.save_results(results)
    
    # print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    greedy_results = [r for r in results if r["algorithm"] == "greedy"]
    backtrack_results = [r for r in results if r["algorithm"] == "backtracking"]
    
    if greedy_results:
        avg_greedy_time = sum(r["runtime"] for r in greedy_results) / len(greedy_results)
        print(f"Greedy algorithm:")
        print(f"  Average runtime: {avg_greedy_time:.3f}s")
        print(f"  Success rate: {sum(1 for r in greedy_results if r['success'])}/{len(greedy_results)}")
    
    if backtrack_results:
        avg_backtrack_time = sum(r["runtime"] for r in backtrack_results) / len(backtrack_results)
        print(f"Backtracking algorithm:")
        print(f"  Average runtime: {avg_backtrack_time:.3f}s")
        print(f"  Success rate: {sum(1 for r in backtrack_results if r['success'])}/{len(backtrack_results)}")
    


if __name__ == "__main__":
    main()

