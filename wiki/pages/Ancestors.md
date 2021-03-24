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
