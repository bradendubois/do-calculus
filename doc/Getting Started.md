# Getting Started

How to install and set up the software.

#### Table of Contents

* [Installation](#installation)
* [Setup](#setup)
* [Running](#running)

## Installation

There are multiple ways to install the software: [**clone the repository**](#clone), [**download a release**](#release), or use the [**GitHub CLI**](#cli).

### Clone

In order to clone the repository, you must have [git](https://git-scm.com/) installed; if you are on [macOS](https://www.apple.com/ca/macos/) or [Linux](https://www.linux.org/), you almost certainly already have this installed.

You can clone the repository using either the [**HTTPS**](#https) URL, or the [**SSH**](#ssh) URL.  If you do not know which to choose, or do not intend to commit to the project, use [**HTTPS**](#https).

#### HTTPS

To clone with the **HTTPS** URL:

```shell
git clone https://github.com/bradendubois/probability-code.git
```

#### SSH

To clone with the **SSH** URL:
```shell
git clone git@github.com:bradendubois/probability-code.git
```

### Release

The project's [releases page](https://github.com/bradendubois/probability-code/releases) shows all tagged version of the project, according to [semantic versioning](https://semver.org/). Both **.zip** and **.tar.gz** archives are available. 

Releases: [https://github.com/bradendubois/probability-code/releases](https://github.com/bradendubois/probability-code/releases)

Releases are automatically created and tagged using [semantic-release](https://github.com/semantic-release/semantic-release). 

### CLI

To clone with the [GitHub CLI](https://cli.github.com/).

```shell
gh repo clone bradendubois/probability-code
```

## Setup

Setup requirements for the project are:
- **[Python 3.8+](https://www.python.org/)**
- [**pip**](https://pip.pypa.io/en/stable/) is used to install [required packages](#python-requirements).

**Note**: `pip` will already be installed with any installation of **Python 3.4+**.

### Python Requirements

At present, the only package not part of a default Python installation is [NumPy](https://numpy.org/). To install *numpy* exclusively:

```shell
pip install numpy
```
However, in the event that more packages become used, the more generalized following command will install all necessary packages in ``requirements.txt``:

```shell
pip install -r requirements.txt
```

## Running

A basic [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) is available, and [details can be found here|REPL].

An [API](https://en.wikipedia.org/wiki/API) is also available, and [details can be found here|API].
