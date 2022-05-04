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
