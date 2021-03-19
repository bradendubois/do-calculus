from pathlib import Path
from setuptools import setup
from os import environ

cwd = Path(".")

README = (cwd / "README.md").read_text()
dependencies = (cwd / "requirements.txt").read_text().strip().split("\n")

# This should be set by the automated Github workflow
VERSION = environ["SEMANTIC_VERSION"]

setup(
    name="do-calculus",
    version=VERSION,
    description="A Python implementation of the do-calculus of Judea Pearl et. al.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bradendubois/do-calculus",
    author="Braden Dubois",
    author_email="braden.dubois@usask.ca",
    packages=["do"],
    keywords="do-calculus causation statistics pearl python",
    include_package_data=True,
    install_requires=dependencies,
    entry_points={
        "console_scripts": [
            "do=do.__main__:main",
        ]
    },
)
