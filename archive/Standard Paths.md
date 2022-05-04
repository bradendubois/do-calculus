Get traditional, directed paths from the *DAG* encoded in the model.

This includes all standard, directed paths as well-defined in graph terminology, and explicitly does **not** include any backdoor paths.

STUB|standard_paths

## Example

```python
from do.API import Do

do_api = Do("models/model1.yml")

paths = do_api.standard_paths({"x", "y"}, {"z"})
```

**Important**
- Since collections of vertices are provided, any path from some vertex in ``src`` to some vertex in ``dst`` is included in the returned collection.
