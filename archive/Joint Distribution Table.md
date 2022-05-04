Get a joint distribution table for all possible combination of outcomes for all variables in the model.

STUB|joint_distribution_table

## Example

```python
from do.API import Do

model = "models/model1.yml"
do_api = Do(model)

table = do_api.joint_distribution_table()
```

**Important**
- This table can be *extremely* computationally intensive if there are many outcomes and/or many variables in the model.
- To improve performance, ensure that [[computation-caching is enabled|Configuration]].
