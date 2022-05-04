# API

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

To create an instance of the API:

```python
from do import API

api = API()
```
