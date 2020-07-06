## Running

To run the project, simply run the file ``main.py``, located in the root of the project:

```shell script
./main.py
```

or run it in Python:

```shell script
python main.py
```

## Usage

When the software is first started, you will be presented with a list of files located in the default graph file folder. 
Additionally, if no configuration file exists in ``config``, a default one will be generated. 

After picking a file, you will be presented with a new set of options, dependant on the graph file selected:

- Query a probability, such as P(Y = y | X = x).
- Query the value of a continuous variable, such as f(X).
- Detect backdoor paths between two sets of variables, X and Y, and find deconfounding sets Z.
- Generate a Joint Distribution Table
- See the topological ordering of the loaded graph
- Switch Graph Files

If there are no variables with probability tables, or no continuous variables, the respective, unavailable options will not be listed.

**Warning**: If you wish to see a Joint Distribution Table for a large graph, ensure that computation-caching is enabled in your configuration file.

### Querying Probabilities

To format a probability query:

- First, provide a "head"; this is the list of outcomes. 
- Second, provide a "body"; this is the list of "given" information.

These must be formatted as comma-separated lists of variables with their outcomes, such as "X=x, Y=y, Z=z". Whitespace is arbitrary, but these must be comma-separated.

- **Example**: For the query P(y | x), the head would be formatted as "Y=y", and the body would be formatted as "X=x".

**Do-calculus** of Judea Pearl is supported; we can query P(Y | do(X)). To format these interventions, simply format such statements with the "do(", ")" text surrounding the outcomes.

- Any number of outcomes may be listed in one "do()"; "do(X=x), do(Y=y)" and "do(X=x, Y=y)" are equivalent.

Here are a few examples, where the first on each line is the "head", and the second is the "body":

- "X = x, Y=y", "Z=z"
- "X=x", "do(Y=y, Z=z)"
- "X = ~x", "do(Y = y), Z=z"
- "X = ~x"

When an intervention (do(X)) is given, we must identify a possible deconfounding set Z. These are automatically calculated.

- Depending on configuration settings, we may *ask* the user to select one, *randomly* pick one, or try *all* of them.

### Querying Functions

If a variable is determined by a function, such as f(C) = f(A) * 2, then we simply input the variable we wish to query:

- "C"

Noise is supported, and creating functions is documented in ``Causal Graph Files``.

### Generate Joint Distribution Table

Selecting this option will try every combination of outcomes possible in the loaded graph, construct a table, and present it.

- On larger graphs, this may take some time, *especially so if result-caching is disabled*.

### Backdoor Path Detection

To compute backdoor paths between X and Y, we are prompted to enter two sets of variables:

- First, enter a comma-separated list of variables, X. 
- Second, enter a comma-separated list of variables, Y.

X should lead into Y with straight-line paths.

All sets Z are computed that are sufficient to "block" any backdoor paths from X to Y.

Depending on configuration file settings, the list presented may be reduced to **minimal sets**.
