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

See any of the specific pages on API functions provided:
* [[Do.\_\_init\_\_|Loading a Model]]
* [[Do.load_model|Loading a Model]]
* [[Do.p|Probability Queries]]
* [[Do.joint_distribution_table|Joint Distribution Table]
* [[Do.backdoor_paths|Backdoor Paths]]
* [[Do.standard_paths|Standard Paths]]]
* [[Do.deconfounding_sets|Deconfounding Sets]]
* [[Do.independent|Conditional Independence]]
* [[Do.roots|Graph Boilerplates]]
* [[Do.sinks|Graph Boilerplates]]
* [[Do.parents|Graph Boilerplates]]
* [[Do.children|Graph Boilerplates]]
* [[Do.ancestors|Graph Boilerplates]]
* [[Do.descendants|Graph Boilerplates]]
* [[Do.topology|Topology]]
* [[Do.topology_position|Topology]]
* [[Do.set_print_result|Output]]
* [[Do.set_print_detail|Output]]
* [[Do.set_logging|Output]]
* [[Do.set_log_fd|Output]]
* [[Exceptions]]
