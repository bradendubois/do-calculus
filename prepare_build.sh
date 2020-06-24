#!/usr/bin/bash

# Whatever version of the project we'll call this
version="1.0"

# Generate an up-to-date version of the configuration documentation
python config/generate_config_docs.py

# Make a directory
build_dir="probability-code-$version"
mkdir $build_dir

cp main.py $build_dir
cp README.md $build_dir

# All directories to copy
directories=("causal_graphs" "config" "probability_structures" "regression_tests")

# Copy all the directories (documentation is handled separately)
for directory in "${directories[@]}"
do
  cp -r "$directory" "$build_dir"
done

# Where to place the documentation
docs="${build_dir}/documentation"
mkdir $docs

# Copy the PDFs, not Markdown
# This specific command probably won't work off my local machine. It just renders a markdown file into pdf
pandoc documentation/causal_graph_files.md -o "${docs}/Causal Graph Files.pdf"
pandoc documentation/configuration.md -o "${docs}/Configuration.pdf"
pandoc documentation/regression_tests.md -o "${docs}/Regression Tests.pdf"
