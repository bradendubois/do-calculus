Basic graph functionality provided from the DAG encoded in the model.

## Roots

Get all roots in the graph, where a root is defined as a vertex with no parent.

STUB|roots

### Example

```python
from do.API import Do

model = "models/model1.yml"
do_api = Do(model)

roots = do_api.roots()
```

**Important**
- The roots are always returned as a collection of vertices.

## Sinks

Get all sinks in the graph, where a sink is defined as vertex with no child.

STUB|sinks

### Example

```python
from do.API import Do

model = "models/model1.yml"
do_api = Do(model)

sinks = do_api.sinks()
```

**Important**
- The sinks are always returned as a collection of vertices.

## Parents

Get the parents of some vertex *v*, where a parent is some vertex *p* such that the edge ``(p, v)`` is in the graph.

STUB|parents

### Example

```python
from do.API import Do

model = "models/model1.yml"
do_api = Do(model)

parents = do_api.parents("x")
```

**Important**
- The parents are always returned as a (possibly **empty**) collection of vertices.

## Children

Get the children of some vertex *v*, where a child is some vertex *c* such that the edge ``(v, c)`` is in the graph.

STUB|children

### Example

```python
from do.API import Do

model = "models/model1.yml"
do_api = Do(model)

children = do_api.children("x")
```

**Important**
- The children are always returned as a (possibly **empty**) collection of vertices.

## Ancestors

Get the ancestors of some vertex *v*, where an ancestor is some vertex *a* such that a directed path ``(a, ..., v)`` is in the graph.

STUB|ancestors

### Example

```python
from do.API import Do

model = "models/model1.yml"
do_api = Do(model)

ancestors = do_api.ancestors("x")
```

**Important**
- The ancestors are always returned as a (possibly **empty**) collection of vertices.

## Descendants

Get the descendants of some vertex *v*, where a descendant is some vertex *d* such that a directed path ``(v, ..., d)`` is in the graph.

STUB|descendants

### Example

```python
from do.API import Do

model = "models/model1.yml"
do_api = Do(model)

descendants = do_api.descendants("x")
```

**Important**
- The descendants are always returned as a (possibly **empty**) collection of vertices.
