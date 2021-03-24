Determine if two sets of variables in the model are conditionally independent.

STUB|independent

## Independent

```python
from do.API import Do

# Assume this were a detailed model conforming to the above graph...
model = dict()

do_api = Do(model)

independent = do_api.independent({"x"}, {"y"}, set())

if independent:
    print("Independent!")
else:
    print("Not independent!")
```

A boolean for whether the two sets are conditionally independent, given some optional deconfounding set, is returned.

**Important**
- The third parameter, a set of deconfounding variables, can be given, to block backdoor paths from ``s`` to ``t``.
- If there are no deconfounding variables, an empty collection can be provided, or explicitly set to ``None``.
