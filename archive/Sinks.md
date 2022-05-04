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
