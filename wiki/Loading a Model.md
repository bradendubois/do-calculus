How to load a model into an instance of the API.

All examples will be using the model from [[Markovian Models]].

## Loading a Model (Python dictionary)

One can have a model represented as a dictionary, and pass this as a *constructor argument* to instantiate a **Do API** instance.

```python
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

do_api = Do(m)
```

**Important**:
- A regular Python dictionary representation of a [[Markovian model|Markovian Models]] is valid input to **Do**.
- Since **Do** is a class, multiple instances of **Do** - each with their own model - can be instantiated in one project at a time.

## Loading a Model (file)

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

## Loading a Model (pathlib.Path)

One can also provide a [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) object, as part of the [pathlib library](https://docs.python.org/3/library/pathlib.html).
- **Trivia**: Providing a [string path to a file](#loading-a-model-file) works by attempting to create a [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) from the string path.

## Swapping Models

If an instance of the **Do API** is already created, a new one can be swapped in as well. 

```python
from do.API import Do

model_1 = "data/graph1.yml"
model_2 = dict()    # Assume this were some more complicated model...

do_api = Do(model_1)        # All good!
do_api.load_model(model_2)  # Reduce, reuse, recycle those object!
```

**Important**:
- One can mix and match the model argument provided when swapping models; a dictionary could be given, then a path, or vice versa.
