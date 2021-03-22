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

## Further

Now that a model is successfully loaded, one can begin [[querying distributions|Probability Queries]].

See any of the more specific pages:
* [[Loading a Model]]
* [[Probability Queries]]
* [[Backdoor Paths]]
* [[Deconfounding Sets]]
