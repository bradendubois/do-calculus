# Do API

Details on the [API](https://en.wikipedia.org/wiki/API) provided in the project.

This assumes the steps in the [[Installation]] section have been followed, and the project is set up.

**Note**: For simplicity of import-statements, any examples will *assume* the project was installed as [PyPI](https://pypi.org/project/do-calculus/) package.

## Table of Contents

* [Importing the **Do** API](#importing)
* [Loading a Model](#loading-a-model)

## Importing

To import the package:

```python
import do
```

**Important**:
- The package name on [PyPI](https://pypi.org/) is [do-calculus](https://pypi.org/project/do-calculus/), but the module to import is called ``do``.

<hr />

To import *just* the API:

```python
from do.API import Do
```

**Important**:
- The API, represented as a Python class, is called **Do**.
- **Do** is stored in the file ``API``, so it can be imported from ``do.API``.

## Loading a Model

Let's create an instance of the API, using the model from [[Installation]]:

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

x = Do(m)
```

**Important**:
- A regular Python dictionary representation of a [[causal model|Causal Models]] is valid input to **Do**.
- Since **Do** is a class, multiple instances of **Do** - each with their own model - can be instantiated in one project at a time.

## Further

Now that a model is successfully loaded, one can begin [[querying distributions|Probability Queries]].

See any of the more specific pages:
* [[Probability Queries]]
* [[Backdoor Paths]]
* [[Deconfounding Sets]]
