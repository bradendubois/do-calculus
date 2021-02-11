# Regression Tests

A breakdown of the Regression Suite of the software.

When run, all the test files in the default test file location are read, and one-by-one, run. Each file is run, and its results are stored; this allows the regression suite to list the outcome of every file, and return a summary "all tests passed" or "some errors found" type of response.

Each test file is run as follows:

- First, a Causal Graph is created from the file.
- Second, every variable with probability tables is evaluated; P(X) must equal 1.0, where this is calculated by Sigma_X P(X); where the probability of each outcome of X is calculated.
- Third, the actual tests listed in the file are finally run.

If any test in a file fails, this returns a failure signal and error message, moving onto the next file.

The code driving the regression suite is located in ``utilities/RegressionTesting``.

## Regression Tests

A breakdown of how to create regression tests.

Regression tests are automatically run at launch. A regression test must be a valid ``JSON`` file, and can be placed in ``regression_tests/test_files``. Any name can be assigned, as long as it has the ``.json`` extension.

A regression test has the following structure:

```json
{
  "test_file": "causal_graph.json",
  "tests": [
    
  ]
}
```

Where ``test_file`` is a causal graph file in the configuration-file-specified graph file location.

If you want to run tests on a graph, but not place that graph in the default graph-file location, you can do that;
include the following argument in the test file: ``"file_directory": "some_new_dir/secret_graphs"``. If this is absent, 
we check the default graph file location; if included, this is the directory (from the root of the project) that will 
be searched for the given graph. 

For example, if I wanted to hide a graph from the default list query-able, but still run tests on it, a test file in
the default test file location might look like the following:

```json
{
  "file_directory": "top_secret/secret_graphs",
  "test_file": "classified_graph_42.json",
  "tests": [
  
  ]
}
```

## Test Types

Each test must be one of the following. The ``name`` is arbitrary, ``type`` must always be specified as shown in each example.

If given, ``expected_result`` must match the calculated result within a configuration-specified number of digits of precision.

### Probability

A basic test for the probability of some head and some body.

In this, both strings in ``args`` is a comma-separated list of outcomes specified. The first is the head, second is the body.

```json
{
  "name": "Basic Probability Tests: P(Y = y | X = x)",
  "type": "probability",
  "args": [
    "Y = y",
    "X = x"  
  ],
  "expected_result": 0.342857
}
```

### Summation

Calculate multiple probabilities and ensure the results sum to some given value.

**Note**: Sigma_X P(X) = 1.0; that is, the summation of probabilities for each possible outcome of a variable must equal 1.0. Writing such tests are not necessary, as this identity is automatically run as part of the regression suite, for all variables in a given graph file. This failing will indicate an error in the software, or inconsistency in the given causal graph. 

- To take advantage of this automatic identity, you must at least provide the shell of a test file for the given graph file in the default test location; ``tests`` can be empty, but as long as a file exists and specifies the graph, this identity is verified.

``args`` should consist of any number of nested lists, each of which contain one/two strings (the head and optional body).

```json
{
  "name": "Basic Compliment Test: P(Y = y) + P(Y = ~y)",
  "type": "summation",
  "args": [
    ["Y = y"],
    ["Y = ~y"]
  ],
  "expected_result": 1.0
}
```

### Determinism

A basic test to ensure deterministic output.

Since sets are heavily used and can change ordering when converted to lists, a given test does not need an expected value; it just ensures that this test, repeated multiple times, always yields the same probability.

``args`` should consist of one or two strings, the first being the head, and the (optional) second being the body.

```json
{
  "name": "Deterministic Output Test: P(Y = y).",
  "type": "determinism",
  "args": [
    "Y = y"
  ]
}
```

### Feedback Loop

A basic test to ensure that a given variable, resolvable by a function (see: ``Causal Graph Files``), which **does** lead into a feedback loop / infinite loop (such as: val(C) = val(C) + 1) is detected.

``args`` should be the name of a variable in the graph, which *should* be detected as causing a feedback loop. 

```json
{
  "name": "Detect Feedback Loop: val(C) has val(C) as a noise function",
  "type": "feedback_detection",
  "args": [
    "C"
  ]
}
```

### Equivalence

A basic test to ensure that an arbitrary number of queries all yield the exact same answer (whatever that answer is).

``args`` should consist of any number of nested lists, each of which contain one/two strings (the head and optional body).

```json
{
  "name": "Verifying that P(xj | x1) === P(xj | do(x1))",
  "type": "equivalence",
  "args":  [
    ["Xj=xj", "X1=x1"],
    ["Xj=xj", "do(X1=x1)"]
  ]
}
```