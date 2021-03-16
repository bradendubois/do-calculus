# Causal Models

This document outlines the structure of how to create a causal model.

Models are inherently **DAGs**, where each variable in a model is also represented as a vertex in the DAG.

Models can be stored in ``json`` and ``yml`` files, and must have either ``.json``, ``.yml``, or ``.yaml`` file extensions.
- The default graph folder is ``src/graphs/full``.

## Model Structure

The graph file must be structured such that a key with value ``model`` is present, and corresponds to a list, where each item is itself a dictionary, representing one variable in the model.
- Each variable in the model is represented by a unique key representing the variable's name, and corresponds to the following key-value pairs:
  - ``outcomes``: all discrete outcomes the variable may take, represented as a list.
  - ``parents``: parent variables (also defined in the model) of the current variable, represented as a list.
    - If the variable is a root - that is, there are no parents - the list can be left empty, or this key can be absent from this variable entirely.
  - ``table``: a list of lists, representing the probability distribution of the variable. Each sub-list is one unique combination of outcomes of the given variable and each of its parents, along with a probability between 0 and 1.
    - The order of the parent variables must correspond to the order given in the ``parents`` entry, if there are any.
  - ``latent``: a boolean representing whether the variable is unobservable in the given model. 
    - If this key is absent, it will be assumed ``False`` - that is, assumed observable.
  
Additionally, a key ``model`` can be given, corresponding to an arbitrary name for the model.

### Example

Here is an example of a very simple model in **yml**:

```yaml
name: Simple Model
model:
  Y:
    outcomes:
      - y
      - ~y
    table: [
     [ y, 0.7 ],
     [ ~y, 0.3 ]
    ]
  X:
    outcomes:
    - x
    - ~x
    parents: [ Y ]
    table: [
      [ x, y, 0.9 ],
      [ x, ~y, 0.75 ],
      [ ~x, y, 0.1 ],
      [ ~x, ~y, 0.25 ]
    ]
```

This represents the basic graph of a single edge, (Y, X).
- In the absence of any ``latent`` attributes, both variables are observable.
- ``Y`` has no parents, it is a root.
