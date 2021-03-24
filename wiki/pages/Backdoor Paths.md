How to discover backdoor paths between two sets of variables in a given [[Markovian model|Markovian Models]].

STUB|backdoor_paths

## Basic Backdoor Paths

Assume the following model uses the graph **G = (V, E)**, where:
- **V** = ``{x, y, z}``
- **E** = ``{(x, y), (z, x), (z, y)}``

```python
from do.API import Do

# Assume this were a detailed model conforming to the above graph...
model = dict()

do_api = Do(model)

backdoor_paths = do_api.backdoor_paths({"x"}, {"y"}, set())

for path in backdoor_paths:
    print(f"Backdoor path from x->y!: {path}")
```

``backdoor_paths`` returns a collection of paths, in which each path consists of the vertices (end-points included) connecting some vertex in the ``src`` collection to some vertex in the ``dst`` collection.
- In this example, the return value would be ``[["x", "z", "y"]]``, as this denotes the singular backdoor path ``x <- z -> y``.

**Important**
- The first parameter is the set of source variables from which the pathfinding begins.
- The second parameter is the set of destination variables to which the pathfinding attempts to reach.
- A third parameter is a set of *deconfounding* variables by which to "block" backdoor paths.
- Each path, a backdoor path, is ordered such that the path order is correctly maintained.

## Deconfounding Variables

Assuming the same graph as defined [above](#basic-backdoor-paths)...

```python
from do.API import Do

# Assume this were a detailed model conforming to the above graph...
model = dict()

do_api = Do(model)

backdoor_paths = do_api.backdoor_paths({"x"}, {"y"}, dcf=None)

for path in backdoor_paths:
    print(f"Backdoor path from x->y!: {path}")

blocked = do_api.backdoor_paths({"x"}, {"y"}, {"z"})

assert len(blocked) == 0
```

**Important**
- To represent that there are no deconfounding variables, an *empty* collection of vertices can be given, or specified as ``None``.
- If all backdoor paths are successfully blocked, an **empty list** is returned.
