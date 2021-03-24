Details on the [API](https://en.wikipedia.org/wiki/API) provided in the project.

This assumes the steps in the [[Installation]] section have been followed, and the project is set up.

**Note**: For simplicity of import-statements, any examples will *assume* the project was installed as [PyPI](https://pypi.org/project/do-calculus/) package.

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

See any of the more specific pages:
* [[Loading a Model]]
* [[Probability Queries]]
* [[Joint Distribution Table]
* [[Backdoor Paths]]
* [[Standard Paths]]]
* [[Deconfounding Sets]]
* [[Conditional Independence]]
* [[Roots / Sinks|Graph Boilerplates]]
* [[Parents / Ancestors|Graph Boilerplates]]
* [[Children / Descendants|Graph Boilerplates]]
* [[Topology]]
* [[Exceptions]]
