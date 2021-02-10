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
