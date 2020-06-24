#!/usr/bin/bash

# Whatever version of the project we'll call this
version="1.0"

# Generate an up-to-date version of the configuration documentation
python config/generate_config_docs.py

# This specific command probably won't work off my local machine. It just renders a markdown file into pdf
pandoc documentation/causal_graph_files.md -css ~/.config/pandoc/github-css.css -o causal_graph_files.pdf
pandoc documentation/configuration.md -css ~/.config/pandoc/github-css.css -o configuration.pdf
pandoc documentation/regression_tests.md -css ~/.config/pandoc/github-css.css -o regression_tests.pdf

# Make a directory
build_dir="probability-code-$version"
mkdir $build_dir

cp main.py $build_dir
cp README.md $build_dir

# All directories to copy
directories=("causal_graphs" "config" "probability_structures" "regression_tests")

# Copy all the directories
for directory in "${directories[@]}"
do
  cp -r "$directory" "$build_dir"
done

docs="${build_dir}/documentation"

# Copy the PDFs, not Markdown
mkdir $docs
cp documentation/causal_graph_files.pdf $docs
cp documentation/configuration.pdf $docs
cp documentation/regression_tests.pdf $docs
