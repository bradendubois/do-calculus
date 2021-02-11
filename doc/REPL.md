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

### Loading Models

### Computing Probabilities

### Deconfounding Sets

To see deconfounding sets, any of the follows commands:
- ``dcs``
- ``dcf``
- ``deconfound``
- ``deconfounding``
followed by the appropriate sets of the form ``src -> dst``, where:
- each respective set is a comma-separated set of vertices in the loaded model
- ``src`` corresponds to the **source vertices** to search for backdoor paths from
- ``dst`` corresponds to **destination vertices** reachable by vertices in ``src`` through traditional paths


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
