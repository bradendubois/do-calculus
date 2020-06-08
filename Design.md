
# CausalGraph

- Name: Y
- Outcomes: [y, ~y]
- Parents: [X, Z]
- Rows: [[y, [x, ~z], -.5], [y, [~x, z], 0.4]]

A CPT should have *all* combinations of values

Slice: [:-1] For all but last

- Can insert any variable when doing P(x | z) = P(x | y, z)... but should be relevant
- In re-ordering, any children in the RHS go to the LHS

- Graph
- Tables for each variable, which is the parents and relevant probabilities