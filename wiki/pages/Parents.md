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
