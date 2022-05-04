How to load a model into an instance of the API.

All examples will be using the model from [[Markovian Models]].

STUB|load_model

As shown in [[\_\_init\_\_|\_\_init\_\_]], the following forms of models are acceptable:
- a Python dictionary
- a string path to a file
- a [pathlib.Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) object

One can have instantiated a **Do**, and wish to replace the model loaded, or one may have deferred providing a model at the time of instantiation, and wish to provide one now.

## Examples

### Swapping a Model

```python
from do.API import Do
from pathlib import Path

model_1 = "data/graph1.yml"

do_api = Do(model=model_1)

model_2 = Path("data/graph2.yml")

do_api.load_model(model_2)
```

**Important**:
- One can mix and match the model argument provided when swapping models; a dictionary could be given, then a path, or vice versa.

### Deferred Loading a Model

```python
from do.API import Do

do_api = Do(model=None)

model_path = "data/graph1.yml"
do_api.load_model(model_path)
```
