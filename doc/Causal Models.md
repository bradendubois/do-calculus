# Causal Models

This document outlines the structure of how to create a causal model.

**TODO** - This layout of files is likely to change in the near future.

- The file must be a valid ``JSON`` file.
- The default folder is at "src/graphs/full".

## Graph File Structure

The graph file must be structured as follows:

```json
{
  "name": "NAME_OF_MODEL",
  "variables": [
  
  ]
}
```

Where ``name`` is an *optional* parameter and ``variables`` is a list of variables in the graph.
 
### Variables

Variables all require the following:

- **"name"**: The actual label of the variable itself, "X", "WEATHER", etc. Generally, it may be helpful to make this name uppercase. **Must be unique**.
- **"determination"**: How the given variable is calculated/evaluated. Consists of the following:
    - **"type"**: "table"
    - **table**: a table, see below.

#### Table-Based

```json
{
  "name": "VARIABLE_NAME",
  "outcomes": ["OUTCOME_1,", "OUTCOME_2", "..."],
  "parents": ["PARENT_1", "PARENT_2", "..."],
  "determination": {
    "type": "table",
    "table": [
      ["OUTCOME_1", ["PARENT_1_OUTCOME_1", "PARENT_2_OUTCOME_1", "..."], 0.0],
      ["OUTCOME_1", ["PARENT_1_OUTCOME_1", "PARENT_2_OUTCOME_2", "..."], 0.0],
      ["OUTCOME_1", ["PARENT_1_OUTCOME_2", "PARENT_2_OUTCOME_1", "..."], 0.0],
      ["..."]
     ]
  }
}
```

If the ``type`` is "table", the following attributes are necessary:

- **"outcomes"**: A list of strings, representing all possible outcomes for the given variable. Cannot have the same outcome twice in one variable, but two separate variables could have the same outcome.
- **"parents"**: A list of strings, representing the "parents" of the given variable. Leave empty to represent zero parents.
- **"table"**: A list of lists, each list representing one "row" in the table, with each sublist formatted as follows:
    - \["outcome", \["parent_1_outcome_1", "parent_2_outcome_1"\], probability\]
    - "outcome" is a specific outcome of the given variable.
    - The inner list is a specific combination of given outcomes, and they must be given in the same order as specified in "given", and a probability as a float.
    - The table must be complete.

- **Note**: "parents" is not necessary for variables such as "roots" without parents, and can be omitted. It will be assumed to be empty.
