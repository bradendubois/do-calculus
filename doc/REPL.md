# REPL

Details on the basic [REPL interface](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) provided in the project.

This assumes the steps in [[Getting Started]] have been followed, and the project is set up.

#### Table of Contents

* [Running](#running)
* [Interface](#interface)

## Running

Assuming one's current working directory is the root of the project, the following will start the software

```shell
python main.py
```

Alternatively:

```shell
./main.py
```

Either will start the software. To run the regression tests, run ``python main.py debug``, which will run tests on the manually-created models provided with the software, taken from [Causality](http://bayes.cs.ucla.edu/BOOK-2K/) and [The Book of Why](http://bayes.cs.ucla.edu/WHY/), although supplementary distributions have been added to these models.

## Interface

A basic REPL begins, with interaction conforming to the following structure:
- A *singular* model is loaded at a time.
- Minimal functionality is available without a model being loaded.

The following functionality is currently available:
- [listing all models](#listing-models)
- [loading a model](#loading-models)
- [computing a probability](#computing-probabilities)
- [finding deconfounding sets](#deconfounding-sets)
- [finding backdoor paths](#backdoor-paths)
- [computing a joint distribution table](#joint-distribution-tables)
- [exiting the software](#exiting)

### Listing Models

To see all models provided, any of the following commands:
- ``list``
_ ``all``
_ ``see``
- ``l``
- ``ls``

### Loading Models

To load a model present (see: [listing models](#listing-models)), any of the following commands:
- ``load``
- ``import``
- ``start``
- ``graph``

followed by the name of a model. Models are currently stored as **JSON**; if the model given does not end with ``.json``, it will be automatically appended.

#### Examples

The following are examples of valid inputs for loading models:

```
load causal_graph_2
```

```
import fumigant_model.json
```

```
start model_42
```

### Computing Probabilities

To compute a probability, any of the following commands:
- ``probability``
- ``p``
- ``compute``
- ``query``

followed by a query of the form "Y | X", where:
- ``Y`` is any number of observations possible in the model
- ``X`` is any number of outcomes and/or interventions/treatments in the model
- if there are no observations or interventions, the ``|`` can also be omitted

Observations and interventions are formatted as ``NAME=OUTCOME``, where:
- ``NAME`` is the name of the variable; this must be defined in the loaded model
- ``OUTCOME`` is some outcome of the variable; this must be defined as a valid outcome for this variable.
- both ``NAME`` and ``OUTCOME`` are **case-sensitive**
- interventions are wrapped with "do()"; **do(NAME=OUTCOME)**

If interventions are present, it is possible for the query to not be completed in the presence of un-blockable backdoor paths.

#### Examples

The following are examples of valid inputs for some hypothetical models:

```
p Y=y | X=x
```

```
compute Y=y, X=x
```

```
query Y=~y | do(X=x)
```

```
p Y=y | do(X=~x), Z=z
```

### Deconfounding Sets

To see deconfounding sets, any of the following commands:
- ``dcs``
- ``dcf``
- ``deconfound``
- ``deconfounding``

followed by the appropriate sets of the form ``src -> dst``, where:
- each respective set is a comma-separated set of vertices in the loaded model
- ``src`` corresponds to the **source vertices** to search for backdoor paths from
- ``dst`` corresponds to **destination vertices** reachable by vertices in ``src`` through traditional paths

#### Examples

The following are examples of valid inputs for some hypothetical model:

```
dcs Y -> X
```

```
dcf Y, Z -> W
```

```
deconfound W, X -> Y, Z
```

### Backdoor Paths

To compute backdoor paths, any of the following commands:
- ``backdoor``
- ``backdoors``
- ``path``
- ``paths``

followed by the appropriate sets of the form ``src -> dst | dcf``, where:
- each respective set is a comma-separated set of vertices in the loaded model
- ``src`` corresponds to the **source vertices** to search for backdoor paths from
- ``dst`` corresponds to **destination vertices** reachable by vertices in ``src`` through traditional paths
- ``dcf`` is an optional set of **deconfounding vertices** that may block or open backdoor paths.

If there are no *deconfounding vertices*, the ``|`` can also be omitted.

#### Examples

The following are examples of valid inputs for some hypothetical model:

```
backdoor Y -> X
```

```
path Y, Z -> W
```

```
backdoors X -> Y | W
```

```
paths S, Y -> X, T | W, Q
```

```
backdoor S -> X | W, T
```

### Joint Distribution Tables

To see a joint distribution of the model, either of the following:
- ``jdt``
- ``joint``

### Exiting 

To exit the software, any of the following inputs are sufficient:
- ``quit``
- ``exit``
- ``stop``
- ``leave``
- ``q``
