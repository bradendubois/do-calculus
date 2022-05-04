Details on getting the topology of the model.

See details in [[Definitions]] for information on the topology-ordering.

## Topology

Getting a topological ordering of the model.

STUB|topology

### Example

```python
from do.API import Do

do_api = Do("models/model1.yml")

topology = do_api.topology()

for v in topology:
    print(v)
```

**Important**
- A sequence of *N* vertices is returned.

<hr />

## Topology Position

Get the position of some vertex in the model in its topological ordering.

STUB|topology_position

```python
from do.API import Do

do_api = Do("models/model1.yml")

position = do_api.topology("x")
print(position)
```

**Important**
- The topological ordering begins at V1, so the value returned for a graph of N vertices is in the range \[1, N\].
