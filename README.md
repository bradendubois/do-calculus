# probability-code

A modified Bayesian net written in Python, supporting the do-calculus of Judea Pearl.

Written for Dr. Eric Neufeld, written by Braden Dubois (braden.dubois@usask.ca).

This work is able to support standard probability distribution queries as in a typical Bayesian net (P(Y=y | X=x)) as well as handling interventional queries: P\*(Y=y | X=x). 

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Running](#requirements)
- [Usage](#usage)
- [Further Documentation](#further-documentation)

## Requirements

This project is written in Python 3, and requires an up-to-date (3.8+) version to run.

Multiple libraries are needed to run the project, almost all of which *should* be a part of a standard Python installation.

- ``json`` (used to read to/from text files)
- ``argparse`` (used to enable command-line flags given to override configuration settings)
- ``itertools`` (used to create cross-products from iterables)
- ``os`` (used to verify/create/read directories and files)
- ``random`` (used to pick a random Z set in do-calculus)
- ``re`` (used in probabilistic function evaluation / parsing text into respective Outcomes and Interventions)
- ``numpy`` (used in formatting conditional probability tables to strings)
- ``math`` (used in formatting conditional probability tables to strings)
- ``operator`` (used in getting a class attribute, used in topological sorting)
- ``datetime`` (used in getting the exact current date/time for regression test file names and decorators)
- ``functools`` (used in function wrapping for decorators)
- ``platform`` (used in the self-updating script to pull from Github)

The project has a command-line interface, with an API forthcoming, to enable usage in other projects.

## Installation

First, clone the repository to your machine.

```shell script
git clone https://github.com/bradendubois/probability-code
cd probability-code
```

Then, install any of the missing libraries from above. The most likely is *numpy*. If Python is installed, ``pip`` should also be installed. To install *numpy*, run:

```shell script
pip install -U numpy
```
## Running

To run the CLI, simply run the file ``main.py``, located in the ``src`` of the project:

This can be done directly:

```shell_script
cd src
./main.py
```

or

```shell_script
./src/main.py
```

Or it can be run in Python:

```shell script
cd src
python main.py
```

or

```shell script
python src/main.py
```

## Usage

When the software is first started:
1. If no configuration file exists in ``src/config``, a default one will be generated.
2. A regression test suite will run, verifying correctness of the software. Output from this can be ignored.
3. The user will be presented with a list of files located in the default graph file folder.

After picking a file, the user will be presented with a new set of options, dependant on the graph file selected:

- Query a probability, such as P(Y = y | X = x).
- See the application of the 3 rules of do-calculus
- Detect backdoor paths between two sets of variables, X and Y, and find deconfounding sets Z.
- Generate a Joint Distribution Table
- See the topological ordering of the loaded graph
- Switch Graph Files

**Warning**: If you wish to see a Joint Distribution Table for a large graph, ensure that computation-caching is enabled in your configuration file.

### Querying Probabilities

To format a probability query:

- First, provide a "head"; this is the list of outcomes.
- Second, provide a "body"; this is the list of "given" information.

These must be formatted as comma-separated lists of variables with their outcomes, such as "X=x, Y=y, Z=z". Whitespace is arbitrary, but these must be comma-separated.

- **Example**: For the query P(y | x), the head would be formatted as "Y=y", and the body would be formatted as "X=x".

**Do-calculus interventions** of Judea Pearl is supported; we can query P(Y | do(X)). To format these interventions, simply format such statements with the "do(", ")" text surrounding the outcomes.

- Any number of outcomes may be listed in one "do()"; "do(X=x), do(Y=y)" and "do(X=x, Y=y)" are equivalent.

Here are a few examples, where the first on each line is the "head", and the second is the "body":

- "X = x, Y=y", "Z=z"
- "X=x", "do(Y=y, Z=z)"
- "X = ~x", "do(Y = y), Z=z"
- "X = ~x"

When an intervention (do(X)) is given, we must identify a possible deconfounding set Z. These are automatically calculated.

- Depending on configuration settings, we may *ask* the user to select one, *randomly* pick one, or try *all* of them.

### Apply the Rules of *do*-calculus

Selecting this option will let us take a query, such as P(y | do(x)), and allow the user to step-by-step, apply the
rules of *do*-calculus, where the goal is to derive an equivalent expression without any *do*'s still in the query.

The user can see every option to apply to the query, as well as allow an *iterative-deepening search* to take place,
attempting to derive a *do*-less query itself.

This will ask for 3 sets of variables: our *outcomes*, *interventions*, and *observations*, in this order.

- For example, these three sets would match P(y | do(x), observe(w)), where y, x, and w match the respective sets.

### Backdoor Path Detection

To compute backdoor paths between X and Y, we are prompted to enter two sets of variables:

- First, enter a comma-separated list of variables, X.
- Second, enter a comma-separated list of variables, Y.

X should lead into Y with straight-line paths.

All sets Z are computed that are sufficient to "block" any backdoor paths from X to Y.

Depending on configuration file settings, the list presented may be reduced to **minimal sets**.

### Generate Joint Distribution Table

Selecting this option will try every combination of outcomes possible in the loaded graph, construct a table, and present it.

- On larger graphs, this may take some time, *especially so if result-caching is disabled*.

### Topological Graph Sort

See a topological sort of the graph.
## Further Documentation

The directory ``documentation`` contains more expansive documentation on various components of using / adding to / modifying the software.

### Graph Files

By default, there are a few files in ``causal_graphs``; any of these can be loaded, and graphs can be easily created, and placed in the same directory to be loaded by the software.

For information on creating graphs, see ``Causal Graph Files``.

### Configuration Settings

A default configuration file is generated the first time the software is run (if there is not already one). All the settings can be modified; options include directories to search, what to log or output, accuracy / formatting rules, etc.

For information on configuration settings, their usage and options, see ``Configuration``.

### Regression Tests

A regression test suite is implemented in the software, and by default, is run at launch. Any number of test files can be created, and by default are located in ``regression_tests/test_files``. They allow for various kinds of tests, including simply checking that probability calculated matches an expected, whether some set of tests sum to some value, and a couple more.

For information on creating test files, see ``Regression Tests``.

### Source Code Design / Architecture

An effort has been made to document source code consistently and clearly. As well, an emphasis has been made to write *clear*, *readable*, and *robust* code.

For information the overall architecture / design, see ``Architecture``.
