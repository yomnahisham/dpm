# Resolution Algorithm

DPM uses a hybrid approach to resolve dependencies efficiently.

## Greedy Resolver (Fast Path)

The greedy algorithm handles ~90% of cases. It:

1. Processes packages in topological order
2. For each package, selects the best version using heuristics:
   - Prefer stable versions over prereleases
   - Prefer already-installed versions (minimize changes)
   - Prefer versions with fewer dependencies
3. Propagates constraints to dependents
4. Detects conflicts early and reports them

If no conflicts are found, the greedy result is used directly.

## Backtracking Resolver (Fallback)

When greedy fails due to conflicts, backtracking kicks in:

1. **Variable ordering**: Uses MRV (Minimum Remaining Values) - packages with fewer valid versions are tried first
2. **Forward checking**: After each assignment, prunes incompatible versions from remaining packages
3. **Constraint propagation**: Detects dead-ends early
4. **Memoization**: Caches failed states to avoid redundant exploration

The backtracker explores the version space systematically until a valid assignment is found or all possibilities are exhausted.

## Conflict Handling

When conflicts occur:
- Greedy reports which packages conflict and why
- Backtracker identifies the minimal conflict region
- Error messages include the constraint chain that led to the conflict

## Performance

- Greedy: O(n × v) where n = packages, v = average versions
- Backtracking: Worst case exponential, but pruning makes it practical for real-world cases

