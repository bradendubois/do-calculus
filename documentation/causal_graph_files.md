# Causal Graph Files

This document outlines  the structure of how to create a causal graph file.

- The graph file must be a valid ``JSON`` file.
- By default, there is a folder labelled ``causal_graphs``, and any file in this directory with a ``.json`` file
    extension will by listed when starting the software.
    - The graph file can be placed anywhere and accessed through modifying the main file, ``ProPyBilityRunner.py`` where it checks/loads.

## Graph File Structure

The graph file must be structured as follows:

```json
{
  "name": "NAME_OF_VARIABLE",
  "variables": [
  
  ]
}
```

Where ``name`` is an *optional* parameter and ``variables`` is a list of variables in the graph.
 
### Variables

Variables all require the following:

- **"name"**: The actual label of the variable itself, "X", "WEATHER", etc. Generally, it may be helpful to make this name uppercase. Must be unique.
- **"outcomes"**: A list of strings, representing all possible outcomes for the given variable. Cannot have the same outcome twice in one variable, but two separate variables could have the same outcome.
- **"parents"**: A list of strings, representing the "parents" of the given variable. Leave empty to represent zero parents.
- **"determination"**: How the given variable is calculated/evaluated. Consists of the following:
    - **"type"**: Whether the given variable is determined by a table, or a function. Must have the value "table" or "function", respectively.

Depending on the ``type``, Variables must conform to one of the two following examples:

#### Table-Based

```json
{
  "name": "VARIABLE_NAME",
  "outcomes": ["OUTCOME_1,", "OUTCOME_2", "..."],
  "parents": ["PARENT_1", "PARENT_2", "..."],
  "determination": {
    "type": "table",
    "tables": [{
      "given": ["PARENT_1", "PARENT_2", "..."],
      "rows": [
        ["OUTCOME_1", ["PARENT_1_OUTCOME_1", "PARENT_2_OUTCOME_1", "..."], 0.0],
        ["OUTCOME_1", ["PARENT_1_OUTCOME_1", "PARENT_2_OUTCOME_2", "..."], 0.0],
        ["OUTCOME_1", ["PARENT_1_OUTCOME_2", "PARENT_2_OUTCOME_1", "..."], 0.0],
        ["..."]
      ]
    }]
  }
}
```

If the ``type`` is "table", the following attribute is necessary:

- **"tables"**: A list of tables determining the given variable, each table consisting of the following:
    - **"given"**: A list of "given" variables, such as the parents of the variable.
    - **"rows"**: A list of lists, each list representing one "row" in the table, with each sublist formatted as follows:
        - ["outcome", ["parent_1_outcome_1", "parent_2_outcome_1"], probability]
        - "outcome" is a specific outcome of the given variable.
        - The inner list is a specific combination of given outcomes, and they must be given in the same order as specified in "given", and a probability as a float.
        - The table must be complete.
    
#### Probabilistic-Function-Based

```json
{
  "name": "VARIABLE_NAME",
  "outcomes": ["OUTCOME_1,", "OUTCOME_2", "..."],
  "parents": ["PARENT_1", "PARENT_2", "..."],
  "determination": {
    "type": "function",
    "function": "10 * p(A=~a) / val(B) + 1"
  }
}
```

If the ``type`` is "function", the following attribute is necessary:

- **"function"**: A function determining the value of the variable. "Noise" is still being added, but the function must be supplied as a valid arithmetic string.

Functions are **case-sensitive** and **spacing-sensitive**, and can involve the following:
- **basic arithmetic**: Order of operations, +-*/, parentheses, exponentiation all supported.
- **nested probabilistic evaluation**: If a Variable *X* is defined in the Causal Graph as being calculated by a (also valid) probabilistic function, you can write ``val(X)`` to reference the evaluation of X.
- **nested probability evaluation**: The probability of some query can be supplied, by being written as ``p(VAR=V,VAR2=V2|VAR3=V3)``.
    - **Notes**
        - Whitespace should not be present in this notation.
            - **Example**: ``p(Y=y|X=x,Z=~z)``
        - Each variable given should be expressed as ``VARIABLE=OUTCOME``.
        - If there is no "given", the vertical bar "|" should be omitted.
            - **Example**: ``p(Y=y)``

- **Note**: At present, "outcomes" is still a required part of the probabilistic function variables, though they yield continuous evaluations; provide the "outcomes" field, but leave it empty.
