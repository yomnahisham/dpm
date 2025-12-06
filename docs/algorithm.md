# Resolution Algorithm

DPM uses a hybrid approach to resolve dependencies efficiently.

## Overview

The resolution process combines two algorithms:
1. **Greedy Resolver**: Fast path for simple cases (~90% of real-world scenarios)
2. **Backtracking Resolver**: Complete solver for complex dependency conflicts

The system tries the greedy approach first, and only falls back to backtracking when conflicts are detected.

## Greedy Resolver (Fast Path)

The greedy algorithm handles most cases efficiently. It:

1. Processes packages in topological order (dependencies before dependents)
2. For each package, selects the best version using heuristics:
   - Prefer stable versions over prereleases
   - Prefer already-installed versions (minimize changes)
   - Prefer versions with fewer dependencies
   - Prefer latest version that satisfies all constraints
3. Propagates constraints to dependents
4. Detects conflicts early and reports them

**Time Complexity**: O(n × v) where n = packages, v = average versions per package

**Space Complexity**: O(n + e) where e = dependency edges

If no conflicts are found, the greedy result is used directly.

### Example

```
Request: install flask, django

Greedy process:
1. flask → select 3.1.2 (latest stable)
2. django → select 6.0 (latest stable)
3. Check dependencies:
   - flask needs: blinker, click, jinja2, werkzeug
   - django needs: asgiref, sqlparse, tzdata
4. No conflicts → success!
```

## Backtracking Resolver (Fallback)

When greedy fails due to conflicts, backtracking kicks in:

1. **Variable ordering**: Uses MRV (Minimum Remaining Values) - packages with fewer valid versions are tried first
2. **Forward checking**: After each assignment, prunes incompatible versions from remaining packages
3. **Constraint propagation**: Detects dead-ends early
4. **Memoization**: Caches failed states to avoid redundant exploration

The backtracker explores the version space systematically until a valid assignment is found or all possibilities are exhausted.

**Time Complexity**: Worst case O(b^d) where b = branching factor, d = depth
**Space Complexity**: O(d) for recursion stack

In practice, pruning and memoization make it much faster than worst case.

### Example

```
Request: install package-a, package-b

Conflict detected:
- package-a@1.0.0 needs dependency-x@>=2.0.0
- package-b@2.0.0 needs dependency-x@<2.0.0

Backtracking process:
1. Try package-a@1.0.0, package-b@1.0.0
   - Check if dependency-x exists that satisfies both
   - No valid version → backtrack
2. Try package-a@0.9.0, package-b@2.0.0
   - Check constraints
   - Success! → return solution
```

## Conflict Handling

When conflicts occur:
- Greedy reports which packages conflict and why
- Backtracker identifies the minimal conflict region
- Error messages include the constraint chain that led to the conflict

### Conflict Reporting

The resolver provides detailed conflict information:

```
Conflict detected:
- package-a@1.0.0 requires dependency-x@>=2.0.0
- package-b@2.0.0 requires dependency-x@<2.0.0

Constraint chain:
  package-a@1.0.0
    → dependency-x@>=2.0.0
  package-b@2.0.0
    → dependency-x@<2.0.0
```

## Dependency Graph

The `DependencyGraph` class manages package relationships:

- **Topological Sort**: Orders packages so dependencies come before dependents
- **Cycle Detection**: Identifies circular dependencies
- **Dependency Tracking**: Maintains both dependencies and dependents

### Topological Sort Algorithm

Uses Kahn's algorithm:

1. Calculate in-degrees (how many dependencies each package has)
2. Start with packages that have no dependencies (in-degree = 0)
3. Remove these packages and decrease in-degrees of their dependents
4. Repeat until all packages are processed

If not all packages are processed, a cycle exists.

## Version Constraints

DPM supports semantic versioning constraints:

- **Exact**: `==1.2.3`
- **Range**: `>=1.0.0,<2.0.0`
- **Tilde**: `~1.2.3` = `>=1.2.3,<1.3.0` (allows patch updates)
- **Caret**: `^1.2.3` = `>=1.2.3,<2.0.0` (allows minor updates)

Multiple constraints can be combined with commas.

## Performance Optimizations

1. **Parallel Fetching**: Fetches package metadata in parallel using ThreadPoolExecutor
2. **Caching**: Caches API responses with TTL and size limits to avoid repeated network requests
3. **Early Termination**: Stops as soon as a valid solution is found
4. **Memoization**: Caches failed states in backtracking to avoid redundant work
5. **Constraint Propagation**: Prunes invalid versions early
6. **SystemSource Optimization**: Caches system package checks and uses heuristics to skip unnecessary subprocess calls
7. **Cache Size Management**: Periodic cache size checks (every 50 writes) with automatic eviction

## Algorithm Selection

The resolver automatically chooses the algorithm:

```python
def resolve(packages, sources):
    # try greedy first
    greedy_result = greedy_resolver.resolve(packages, sources)
    
    if greedy_result.success:
        return greedy_result
    
    # fall back to backtracking
    backtrack_result = backtrack_resolver.resolve(packages, sources)
    return backtrack_result
```

## Real-World Performance

Based on testing with real packages:

- **Greedy**: ~90% of cases resolve in <1 second
- **Backtracking**: Complex cases resolve in 1-5 seconds
- **Large dependency trees** (100+ packages): 5-15 seconds
- **Multiple packages** (2-3 packages): <3 seconds
- **Complex resolution** (5+ packages): ~20-25 seconds

Most real-world scenarios use the greedy path, making DPM fast for typical use cases.

## Robustness Features

### Timeout Protection

The resolver includes a timeout mechanism (default: 60 seconds) to prevent infinite hangs:
- Uses `concurrent.futures.ThreadPoolExecutor` with timeout
- Returns clear error message if resolution times out
- Prevents resource exhaustion from complex dependency graphs

### Error Recovery

- **Network Failures**: Automatic retry with exponential backoff
- **Cache Failures**: Graceful degradation to network requests
- **Installation Failures**: Automatic rollback of partial installations
- **Resolution Failures**: Detailed conflict reporting for debugging

DPM uses a hybrid approach to resolve dependencies efficiently.

## Overview

The resolution process combines two algorithms:
1. **Greedy Resolver**: Fast path for simple cases (~90% of real-world scenarios)
2. **Backtracking Resolver**: Complete solver for complex dependency conflicts

The system tries the greedy approach first, and only falls back to backtracking when conflicts are detected.

## Greedy Resolver (Fast Path)

The greedy algorithm handles most cases efficiently. It:

1. Processes packages in topological order (dependencies before dependents)
2. For each package, selects the best version using heuristics:
   - Prefer stable versions over prereleases
   - Prefer already-installed versions (minimize changes)
   - Prefer versions with fewer dependencies
   - Prefer latest version that satisfies all constraints
3. Propagates constraints to dependents
4. Detects conflicts early and reports them

**Time Complexity**: O(n × v) where n = packages, v = average versions per package

**Space Complexity**: O(n + e) where e = dependency edges

If no conflicts are found, the greedy result is used directly.

### Example

```
Request: install flask, django

Greedy process:
1. flask → select 3.1.2 (latest stable)
2. django → select 6.0 (latest stable)
3. Check dependencies:
   - flask needs: blinker, click, jinja2, werkzeug
   - django needs: asgiref, sqlparse, tzdata
4. No conflicts → success!
```

## Backtracking Resolver (Fallback)

When greedy fails due to conflicts, backtracking kicks in:

1. **Variable ordering**: Uses MRV (Minimum Remaining Values) - packages with fewer valid versions are tried first
2. **Forward checking**: After each assignment, prunes incompatible versions from remaining packages
3. **Constraint propagation**: Detects dead-ends early
4. **Memoization**: Caches failed states to avoid redundant exploration

The backtracker explores the version space systematically until a valid assignment is found or all possibilities are exhausted.

**Time Complexity**: Worst case O(b^d) where b = branching factor, d = depth
**Space Complexity**: O(d) for recursion stack

In practice, pruning and memoization make it much faster than worst case.

### Example

```
Request: install package-a, package-b

Conflict detected:
- package-a@1.0.0 needs dependency-x@>=2.0.0
- package-b@2.0.0 needs dependency-x@<2.0.0

Backtracking process:
1. Try package-a@1.0.0, package-b@1.0.0
   - Check if dependency-x exists that satisfies both
   - No valid version → backtrack
2. Try package-a@0.9.0, package-b@2.0.0
   - Check constraints
   - Success! → return solution
```

## Conflict Handling

When conflicts occur:
- Greedy reports which packages conflict and why
- Backtracker identifies the minimal conflict region
- Error messages include the constraint chain that led to the conflict

### Conflict Reporting

The resolver provides detailed conflict information:

```
Conflict detected:
- package-a@1.0.0 requires dependency-x@>=2.0.0
- package-b@2.0.0 requires dependency-x@<2.0.0

Constraint chain:
  package-a@1.0.0
    → dependency-x@>=2.0.0
  package-b@2.0.0
    → dependency-x@<2.0.0
```

## Dependency Graph

The `DependencyGraph` class manages package relationships:

- **Topological Sort**: Orders packages so dependencies come before dependents
- **Cycle Detection**: Identifies circular dependencies
- **Dependency Tracking**: Maintains both dependencies and dependents

### Topological Sort Algorithm

Uses Kahn's algorithm:

1. Calculate in-degrees (how many dependencies each package has)
2. Start with packages that have no dependencies (in-degree = 0)
3. Remove these packages and decrease in-degrees of their dependents
4. Repeat until all packages are processed

If not all packages are processed, a cycle exists.

## Version Constraints

DPM supports semantic versioning constraints:

- **Exact**: `==1.2.3`
- **Range**: `>=1.0.0,<2.0.0`
- **Tilde**: `~1.2.3` = `>=1.2.3,<1.3.0` (allows patch updates)
- **Caret**: `^1.2.3` = `>=1.2.3,<2.0.0` (allows minor updates)

Multiple constraints can be combined with commas.

## Performance Optimizations

1. **Parallel Fetching**: Fetches package metadata in parallel using ThreadPoolExecutor
2. **Caching**: Caches API responses with TTL and size limits to avoid repeated network requests
3. **Early Termination**: Stops as soon as a valid solution is found
4. **Memoization**: Caches failed states in backtracking to avoid redundant work
5. **Constraint Propagation**: Prunes invalid versions early
6. **SystemSource Optimization**: Caches system package checks and uses heuristics to skip unnecessary subprocess calls
7. **Cache Size Management**: Periodic cache size checks (every 50 writes) with automatic eviction

## Algorithm Selection

The resolver automatically chooses the algorithm:

```python
def resolve(packages, sources):
    # try greedy first
    greedy_result = greedy_resolver.resolve(packages, sources)
    
    if greedy_result.success:
        return greedy_result
    
    # fall back to backtracking
    backtrack_result = backtrack_resolver.resolve(packages, sources)
    return backtrack_result
```

## Real-World Performance

Based on testing with real packages:

- **Greedy**: ~90% of cases resolve in <1 second
- **Backtracking**: Complex cases resolve in 1-5 seconds
- **Large dependency trees** (100+ packages): 5-15 seconds
- **Multiple packages** (2-3 packages): <3 seconds
- **Complex resolution** (5+ packages): ~20-25 seconds

Most real-world scenarios use the greedy path, making DPM fast for typical use cases.

## Robustness Features

### Timeout Protection

The resolver includes a timeout mechanism (default: 60 seconds) to prevent infinite hangs:
- Uses `concurrent.futures.ThreadPoolExecutor` with timeout
- Returns clear error message if resolution times out
- Prevents resource exhaustion from complex dependency graphs

### Error Recovery

- **Network Failures**: Automatic retry with exponential backoff
- **Cache Failures**: Graceful degradation to network requests
- **Installation Failures**: Automatic rollback of partial installations
- **Resolution Failures**: Detailed conflict reporting for debugging

DPM uses a hybrid approach to resolve dependencies efficiently.

## Overview

The resolution process combines two algorithms:
1. **Greedy Resolver**: Fast path for simple cases (~90% of real-world scenarios)
2. **Backtracking Resolver**: Complete solver for complex dependency conflicts

The system tries the greedy approach first, and only falls back to backtracking when conflicts are detected.

## Greedy Resolver (Fast Path)

The greedy algorithm handles most cases efficiently. It:

1. Processes packages in topological order (dependencies before dependents)
2. For each package, selects the best version using heuristics:
   - Prefer stable versions over prereleases
   - Prefer already-installed versions (minimize changes)
   - Prefer versions with fewer dependencies
   - Prefer latest version that satisfies all constraints
3. Propagates constraints to dependents
4. Detects conflicts early and reports them

**Time Complexity**: O(n × v) where n = packages, v = average versions per package

**Space Complexity**: O(n + e) where e = dependency edges

If no conflicts are found, the greedy result is used directly.

### Example

```
Request: install flask, django

Greedy process:
1. flask → select 3.1.2 (latest stable)
2. django → select 6.0 (latest stable)
3. Check dependencies:
   - flask needs: blinker, click, jinja2, werkzeug
   - django needs: asgiref, sqlparse, tzdata
4. No conflicts → success!
```

## Backtracking Resolver (Fallback)

When greedy fails due to conflicts, backtracking kicks in:

1. **Variable ordering**: Uses MRV (Minimum Remaining Values) - packages with fewer valid versions are tried first
2. **Forward checking**: After each assignment, prunes incompatible versions from remaining packages
3. **Constraint propagation**: Detects dead-ends early
4. **Memoization**: Caches failed states to avoid redundant exploration

The backtracker explores the version space systematically until a valid assignment is found or all possibilities are exhausted.

**Time Complexity**: Worst case O(b^d) where b = branching factor, d = depth
**Space Complexity**: O(d) for recursion stack

In practice, pruning and memoization make it much faster than worst case.

### Example

```
Request: install package-a, package-b

Conflict detected:
- package-a@1.0.0 needs dependency-x@>=2.0.0
- package-b@2.0.0 needs dependency-x@<2.0.0

Backtracking process:
1. Try package-a@1.0.0, package-b@1.0.0
   - Check if dependency-x exists that satisfies both
   - No valid version → backtrack
2. Try package-a@0.9.0, package-b@2.0.0
   - Check constraints
   - Success! → return solution
```

## Conflict Handling

When conflicts occur:
- Greedy reports which packages conflict and why
- Backtracker identifies the minimal conflict region
- Error messages include the constraint chain that led to the conflict

### Conflict Reporting

The resolver provides detailed conflict information:

```
Conflict detected:
- package-a@1.0.0 requires dependency-x@>=2.0.0
- package-b@2.0.0 requires dependency-x@<2.0.0

Constraint chain:
  package-a@1.0.0
    → dependency-x@>=2.0.0
  package-b@2.0.0
    → dependency-x@<2.0.0
```

## Dependency Graph

The `DependencyGraph` class manages package relationships:

- **Topological Sort**: Orders packages so dependencies come before dependents
- **Cycle Detection**: Identifies circular dependencies
- **Dependency Tracking**: Maintains both dependencies and dependents

### Topological Sort Algorithm

Uses Kahn's algorithm:

1. Calculate in-degrees (how many dependencies each package has)
2. Start with packages that have no dependencies (in-degree = 0)
3. Remove these packages and decrease in-degrees of their dependents
4. Repeat until all packages are processed

If not all packages are processed, a cycle exists.

## Version Constraints

DPM supports semantic versioning constraints:

- **Exact**: `==1.2.3`
- **Range**: `>=1.0.0,<2.0.0`
- **Tilde**: `~1.2.3` = `>=1.2.3,<1.3.0` (allows patch updates)
- **Caret**: `^1.2.3` = `>=1.2.3,<2.0.0` (allows minor updates)

Multiple constraints can be combined with commas.

## Performance Optimizations

1. **Parallel Fetching**: Fetches package metadata in parallel using ThreadPoolExecutor
2. **Caching**: Caches API responses with TTL and size limits to avoid repeated network requests
3. **Early Termination**: Stops as soon as a valid solution is found
4. **Memoization**: Caches failed states in backtracking to avoid redundant work
5. **Constraint Propagation**: Prunes invalid versions early
6. **SystemSource Optimization**: Caches system package checks and uses heuristics to skip unnecessary subprocess calls
7. **Cache Size Management**: Periodic cache size checks (every 50 writes) with automatic eviction

## Algorithm Selection

The resolver automatically chooses the algorithm:

```python
def resolve(packages, sources):
    # try greedy first
    greedy_result = greedy_resolver.resolve(packages, sources)
    
    if greedy_result.success:
        return greedy_result
    
    # fall back to backtracking
    backtrack_result = backtrack_resolver.resolve(packages, sources)
    return backtrack_result
```

## Real-World Performance

Based on testing with real packages:

- **Greedy**: ~90% of cases resolve in <1 second
- **Backtracking**: Complex cases resolve in 1-5 seconds
- **Large dependency trees** (100+ packages): 5-15 seconds
- **Multiple packages** (2-3 packages): <3 seconds
- **Complex resolution** (5+ packages): ~20-25 seconds

Most real-world scenarios use the greedy path, making DPM fast for typical use cases.

## Robustness Features

### Timeout Protection

The resolver includes a timeout mechanism (default: 60 seconds) to prevent infinite hangs:
- Uses `concurrent.futures.ThreadPoolExecutor` with timeout
- Returns clear error message if resolution times out
- Prevents resource exhaustion from complex dependency graphs

### Error Recovery

- **Network Failures**: Automatic retry with exponential backoff
- **Cache Failures**: Graceful degradation to network requests
- **Installation Failures**: Automatic rollback of partial installations
- **Resolution Failures**: Detailed conflict reporting for debugging

DPM uses a hybrid approach to resolve dependencies efficiently.

## Overview

The resolution process combines two algorithms:
1. **Greedy Resolver**: Fast path for simple cases (~90% of real-world scenarios)
2. **Backtracking Resolver**: Complete solver for complex dependency conflicts

The system tries the greedy approach first, and only falls back to backtracking when conflicts are detected.

## Greedy Resolver (Fast Path)

The greedy algorithm handles most cases efficiently. It:

1. Processes packages in topological order (dependencies before dependents)
2. For each package, selects the best version using heuristics:
   - Prefer stable versions over prereleases
   - Prefer already-installed versions (minimize changes)
   - Prefer versions with fewer dependencies
   - Prefer latest version that satisfies all constraints
3. Propagates constraints to dependents
4. Detects conflicts early and reports them

**Time Complexity**: O(n × v) where n = packages, v = average versions per package

**Space Complexity**: O(n + e) where e = dependency edges

If no conflicts are found, the greedy result is used directly.

### Example

```
Request: install flask, django

Greedy process:
1. flask → select 3.1.2 (latest stable)
2. django → select 6.0 (latest stable)
3. Check dependencies:
   - flask needs: blinker, click, jinja2, werkzeug
   - django needs: asgiref, sqlparse, tzdata
4. No conflicts → success!
```

## Backtracking Resolver (Fallback)

When greedy fails due to conflicts, backtracking kicks in:

1. **Variable ordering**: Uses MRV (Minimum Remaining Values) - packages with fewer valid versions are tried first
2. **Forward checking**: After each assignment, prunes incompatible versions from remaining packages
3. **Constraint propagation**: Detects dead-ends early
4. **Memoization**: Caches failed states to avoid redundant exploration

The backtracker explores the version space systematically until a valid assignment is found or all possibilities are exhausted.

**Time Complexity**: Worst case O(b^d) where b = branching factor, d = depth
**Space Complexity**: O(d) for recursion stack

In practice, pruning and memoization make it much faster than worst case.

### Example

```
Request: install package-a, package-b

Conflict detected:
- package-a@1.0.0 needs dependency-x@>=2.0.0
- package-b@2.0.0 needs dependency-x@<2.0.0

Backtracking process:
1. Try package-a@1.0.0, package-b@1.0.0
   - Check if dependency-x exists that satisfies both
   - No valid version → backtrack
2. Try package-a@0.9.0, package-b@2.0.0
   - Check constraints
   - Success! → return solution
```

## Conflict Handling

When conflicts occur:
- Greedy reports which packages conflict and why
- Backtracker identifies the minimal conflict region
- Error messages include the constraint chain that led to the conflict

### Conflict Reporting

The resolver provides detailed conflict information:

```
Conflict detected:
- package-a@1.0.0 requires dependency-x@>=2.0.0
- package-b@2.0.0 requires dependency-x@<2.0.0

Constraint chain:
  package-a@1.0.0
    → dependency-x@>=2.0.0
  package-b@2.0.0
    → dependency-x@<2.0.0
```

## Dependency Graph

The `DependencyGraph` class manages package relationships:

- **Topological Sort**: Orders packages so dependencies come before dependents
- **Cycle Detection**: Identifies circular dependencies
- **Dependency Tracking**: Maintains both dependencies and dependents

### Topological Sort Algorithm

Uses Kahn's algorithm:

1. Calculate in-degrees (how many dependencies each package has)
2. Start with packages that have no dependencies (in-degree = 0)
3. Remove these packages and decrease in-degrees of their dependents
4. Repeat until all packages are processed

If not all packages are processed, a cycle exists.

## Version Constraints

DPM supports semantic versioning constraints:

- **Exact**: `==1.2.3`
- **Range**: `>=1.0.0,<2.0.0`
- **Tilde**: `~1.2.3` = `>=1.2.3,<1.3.0` (allows patch updates)
- **Caret**: `^1.2.3` = `>=1.2.3,<2.0.0` (allows minor updates)

Multiple constraints can be combined with commas.

## Performance Optimizations

1. **Parallel Fetching**: Fetches package metadata in parallel using ThreadPoolExecutor
2. **Caching**: Caches API responses with TTL and size limits to avoid repeated network requests
3. **Early Termination**: Stops as soon as a valid solution is found
4. **Memoization**: Caches failed states in backtracking to avoid redundant work
5. **Constraint Propagation**: Prunes invalid versions early
6. **SystemSource Optimization**: Caches system package checks and uses heuristics to skip unnecessary subprocess calls
7. **Cache Size Management**: Periodic cache size checks (every 50 writes) with automatic eviction

## Algorithm Selection

The resolver automatically chooses the algorithm:

```python
def resolve(packages, sources):
    # try greedy first
    greedy_result = greedy_resolver.resolve(packages, sources)
    
    if greedy_result.success:
        return greedy_result
    
    # fall back to backtracking
    backtrack_result = backtrack_resolver.resolve(packages, sources)
    return backtrack_result
```

## Real-World Performance

Based on testing with real packages:

- **Greedy**: ~90% of cases resolve in <1 second
- **Backtracking**: Complex cases resolve in 1-5 seconds
- **Large dependency trees** (100+ packages): 5-15 seconds
- **Multiple packages** (2-3 packages): <3 seconds
- **Complex resolution** (5+ packages): ~20-25 seconds

Most real-world scenarios use the greedy path, making DPM fast for typical use cases.

## Robustness Features

### Timeout Protection

The resolver includes a timeout mechanism (default: 60 seconds) to prevent infinite hangs:
- Uses `concurrent.futures.ThreadPoolExecutor` with timeout
- Returns clear error message if resolution times out
- Prevents resource exhaustion from complex dependency graphs

### Error Recovery

- **Network Failures**: Automatic retry with exponential backoff
- **Cache Failures**: Graceful degradation to network requests
- **Installation Failures**: Automatic rollback of partial installations
- **Resolution Failures**: Detailed conflict reporting for debugging
