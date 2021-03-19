How to measure probabilities using the **Do** API.

## Making a Query

For this, we will query a standard probability through the **Do** API.

```python
from do.API import Do
from do.probability.structures.VariableStructures import Outcome

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

x = Outcome("X", "x")
y = Outcome("Y", "y")

x_alone = do_api.p({x}, set())
print(f"The probability of X=x, P(X=x) = {x_alone:5}")

x_if_y = do_api.p({x}, {y})
print(f"The probability of P(X=x | Y=y) = {x_if_y:5}")

x_and_y = do_api.p({x, y}, set())
print(f"The probability of P(X=x, Y=y) = {x_and_y:5}")
```

**Important**:
- The representation of a variable in the model having some *observed* value is implemented as an **Outcome** object.
- The creation of an Outcome object is to supply the *name* of the variable, and *some outcome of this variable*.
- The Outcome class is located at ``do.probability.structures.VariableStructures``.
- The API function provided in **Do** to query a probability is the ``p`` function.
- **Do.p** takes *two* arguments, a *set of outcome outcomes*, and a *set of "given" outcomes*.
- **Do.p** requires an empty set as its "given" outcomes even if there are none.
- **Do.p** returns a *float*, between [0, 1].

## Querying an Interventional Distribution

Assume the existence of some more complicated model, ``m_confounded``, in which multiple variables are susceptible to *backdoor paths* or *confounding*, but a sufficient *deconfounding set* can block all backdoor paths.
- See [[Literature]] for more details on *backdoor paths* and *deconfounding*.

```python
from do.API import Do
from do.probability.structures.VariableStructures import Outcome, Intervention

# Assume this were some more complicated model...
m_confounding = dict()

do_api = Do(m_confounding)

x = Outcome("X", "x")

y_outcome = Outcome("Y", "y")
y_intervention = Intervention("Y", "y")

x_y = do_api.p({x}, {y_outcome})
x_do_y = do_api.p({x}, {y_intervention})

if x_y != x_do_y:
    print(f"P(X=x | Y=y) ({x_y:5}) != P(X=x | do(Y=y)) ({x_do_y:5}): Y shows causal influence over X!")
```

**Important**:
- A *treatment* or *intervention* is represented by the **Intervention** object.
- The Intervention class is located at ``do.probability.structures.VariableStructures``, the same as the Outcome class.
- The Intervention class takes the same arguments as the Outcome class.
- Queries involving interventions use **Do.p** just as standard queries do.
