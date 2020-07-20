# probability-code

A Bayesian net written in Python, supporting the do-calculus of Judea Pearl.

Written for Dr. Eric Neufeld, written by Braden Dubois (braden.dubois@usask.ca).

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Running](#requirements)
- [Usage](#usage)
- [Further Documentation](#further-documentation)

## Requirements

This project is written in Python 3, and requires an up-to-date (3.8+) version to run.

Multiple libraries are needed to run the project, almost all of which *should* be a part of a standard Python installation.

- json (used to read to/from text files)
- argparse (used to enable command-line flags given to override configuartion settings)
- itertools (used to create cross-products from iterables)
- os (used to verify/create/read directories and files)
- random (used to pick a random Z set in do-calculus)
- re (used in probabilistic function evaluation / parsing text into respective Outcomes and Interventions)
- numpy (used in formatting conditional probability tables to strings)
- math (used in formatting conditional probability tables to strings)
- operator (used in getting a class attribute, used in topological sorting)
- datetime (used in getting the exact current date/time for regression test file names and decorators)
- functools (used in function wrapping for decorators)

## Installation

Of all libraries listed, it is most likely that **numpy** is not installed on a user's machine, as it is not part of a default installation.

If Python is installed, ``pip`` should also be installed. To install *numpy*, run:

```shell script
pip install -U numpy
```

To download the project, either acquire a copy from Github, Dropbox, etc.

### Git Clone

There is a private repository on Github, hosting the most up-to-date version of the project.

Link: [https://github.com/bradendubois/probability-code](https://github.com/bradendubois/probability-code)

If you *can* view the project, simply clone the project, and change your working directory to its root.

```shell script
git clone https://github.com/bradendubois/probability-code
cd probability-code
```

As it is private, you will likely be prompted to login and verify your collaborator status.
