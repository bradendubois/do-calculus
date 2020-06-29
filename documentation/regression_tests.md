# Regression Tests

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

