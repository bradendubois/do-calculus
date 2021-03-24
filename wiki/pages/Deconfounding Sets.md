# Deconfounding Sets

Finding all deconfounding sets between two sets of vertices.

## Basic Example

Assuming the basic 3-vertex graph from [[Backdoor Paths]], **G = (V, E)** where:
- **V** = ``{x, y, z}``
- **E** = ``{(x, y), (z, x), (z, y)}``

```python
from do.API import Do

# Assume this were a detailed model conforming to the above graph...
model = dict()

do_api = Do(model)

dcf = do_api.deconfounding_sets({"x"}, {"y"})

for deconfounding_set in dcf:
    print(f"Deconfounding set for x->y!: {deconfounding_set}")
```

**Important**:
- ``deconfounding_sets`` takes a *source* set of variables, and a *destination/target* set of variables.
- A list of sets is returned, where each set consists of one possible set by which to block all deconfounding paths.

## Usage of Deconfounding Sets

Finding a deconfounding set can be helpful, but any [[probability queries involving interventions|Probability Queries]] automatically handles deconfounding. An easy check to verify each deconfounding set:


```python
from do.API import Do

# Assume this were a more complicated model
model = dict()

do_api = Do(model)

dcf = do_api.deconfounding_sets({"x"}, {"y"})

for deconfounding_set in dcf:
    assert len(do_api.backdoor_paths({"x"}, {"y"}, deconfounding_set)) == 0
```
