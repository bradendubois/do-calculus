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

- ``json`` (used to read to/from text files)
- ``argparse`` (used to enable command-line flags given to override configuartion settings)
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

There is an in

The project has a fully function CLI interface, as well as an in-development GUI version. To run the GUI version, additional libraries must be installed and set up; see the subsection **Installation (GUI)** for additional setup instructions. The following is necessary exclusively for the **GUI version**.

- **[pywebview](https://pywebview.flowrl.com/)**
- **[node](https://nodejs.org/en/)**
- **[npm](https://www.npmjs.com/)**

## Installation

This code is a private repository on Github, hosting the most up-to-date version of the project.

Link: [https://github.com/bradendubois/probability-code](https://github.com/bradendubois/probability-code)

```shell script
git clone https://github.com/bradendubois/probability-code
cd probability-code
```

As it is private, you will likely be prompted to login and verify your collaborator status.

For both the CLI and GUI versions, **numpy** is used and may not be installed on a user's machine.

If Python is installed, ``pip`` should also be installed. To install *numpy*, run:

```shell script
pip install -U numpy
```

The following subsection concerns additional installation steps necessary to run the **GUI** version.

### Installation (GUI)

The GUI version is driven by **[Pywebview](https://pywebview.flowrl.com/)** providing a Python API / back-end capable of running a progressive web app.

To set up the GUI, **[node](https://nodejs.org/en/)** must be installed on the user's machine. **[npm](https://www.npmjs.com/)** must also be installed, and is included with a **[node](https://nodejs.org/en/)** installation.

Once **[node](https://nodejs.org/en/)** and **[npm](https://www.npmjs.com/)** are installed, from the root of the project, run:

```shell_script
npm run init
```

This will:

- Install Node dependencies (and may take a while)
- Set up a Python virtual environment
- Install required modules in the virtual environment
- Attempt to install any necessary GUI toolkit (QT or GTK)

#### Troubleshooting

This script may fail on a Linux system without "apt" installed.

- Try running both ``npm run init:qt5`` and ``npm run init:gtk`` directly, and one should succeed.
