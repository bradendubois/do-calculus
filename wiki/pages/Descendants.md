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
