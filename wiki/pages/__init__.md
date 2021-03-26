How to instantiate the **Do** API.

STUB|__init__

## Examples

One can provide a model, and specify what details and results to print and/or log to a file.

```python
from pathlib import Path
from do.API import Do

file = Path("output/model1.yml")
f = file.open("w")

do_api = Do(
    model=m,
    print_detail=False,
    print_result=True,
    log=True,
    log_fd=f
)
```

**Note**: Here, ``m`` is not defined, but multiple examples will follow, detailing acceptable forms of ``m``.

**Important**:
- Since **Do** is a class, multiple instances of **Do** - each with their own model - can be instantiated in one project at a time.
- Various parameters of outputting and logging details can be [[tweaked|Output]].

<hr />

### Model: Python dictionary

One can have a model represented as a dictionary, and pass this as a *constructor argument* to instantiate **Do**.

```python
from pathlib import Path
from do.API import Do

m = {
  "name": "Simple Model",
  "model": {
    "Y": {
        "outcomes": ["y", "~y"],
        "table": [
          ["y", 0.7], 
          ["~y", 0.3]
        ] 
    },
    "X": {
      "outcomes": ["x", "~x" ],
      "parents": [ "Y" ],
      "table": [
        ["x", "y", 0.9],
        ["x", "~y", 0.75],
        ["~x", "y", 0.1],
        ["~x", "~y", 0.25]
      ]
    }
  }
}

file = Path("output/model1.yml")
f = file.open("w")

do_api = Do(
    model=m,
    print_detail=False,
    print_result=True,
    log=True,
    log_fd=f
)
```

**Important**
- A regular Python dictionary representation of a [[Markovian model|Markovian Models]] is valid input to **Do**.

<hr />

### Model: string path to a file

One can also have a file contain a valid model, and pass the *path* to the file as input as well.

```python
from do.API import Do

model_path = "data/graph1.yml"
do_api = Do(model_path)         # All good!

fake_path = "does/not/exist.file"
do_api_2 = Do(fake_path)        # This will raise an exception!
```

**Important**:
- A *string path* is valid to pass to **Do**.
- If the file cannot be found or parsed, an exception will be raised.

<hr />

### Model: pathlib.Path

One can also provide a [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) object, as part of the [pathlib library](https://docs.python.org/3/library/pathlib.html).
- **Trivia**: Providing a [string path to a file](#model-string-path-to-a-file) works by attempting to create a [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) from the string path.

```python
from pathlib import Path
from do.API import Do

model_path = Path("graph2.yml")
do_api = Do(model_path)
```

<hr />

### Model: None

One can also create an instance of **Do**, in which no model is provided, and instead [[defer loading the model until later|Loading a Model]].

```python
from do.API import Do

do_api = Do(model=None, print_result=True)
```

**Important**
- If no model is loaded, any relevant API functionality will fail until a model [[has been loaded|Loading a Model]].
