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
