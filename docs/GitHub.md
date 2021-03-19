# GitHub

Instructions for installing the project from the [source code](https://github.com/bradendubois/do-calculus/wiki).

## Acquiring a Copy

To acquire a copy of the source code, one can [**clone the repository**](#clone), [**download a release**](#release), or use the [**GitHub CLI**](#cli).

After a copy has been acquired, [install the extra dependencies](#extra-dependencies).

## Clone

In order to clone the repository, you must have [git](https://git-scm.com/) installed; if you are on [macOS](https://www.apple.com/ca/macos/) or [Linux](https://www.linux.org/), you almost certainly already have this installed.

You can clone the repository using either the **HTTPS** or **SSH** URL.  If you do not know which to choose, or do not intend to commit to the project, use **HTTPS**.

To clone with the **HTTPS** URL:

```shell
git clone https://github.com/bradendubois/do-calculus.git
```

To clone with the **SSH** URL:
```shell
git clone git@github.com:bradendubois/do-calculus.git
```

## Release

The project's [releases page](https://github.com/bradendubois/do-calculus/releases) shows all tagged version of the project, according to [semantic versioning](https://semver.org/). Both **.zip** and **.tar.gz** archives are available. 

**Releases**: [https://github.com/bradendubois/do-calculus/releases](https://github.com/bradendubois/do-calculus/releases)

Releases are automatically created, tagged, and versioned using [semantic-release](https://github.com/semantic-release/semantic-release). 

## CLI

To clone with the [GitHub CLI](https://cli.github.com/).

```shell
gh repo clone bradendubois/do-calculus
```

## Extra Dependencies

After acquiring a copy from any of the above steps:

```shell
pip install -r requirements.txt
```

The above command will install all dependencies listed in ``requirements.txt``.

## Further

An [API](https://en.wikipedia.org/wiki/API) is available and [[details can be found here|Do API]].
