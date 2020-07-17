#!/usr/bin/bash

# Whatever version of the project we'll call this
version="1.5"

# Generate an up-to-date version of the configuration documentation
python config/generate_config_docs.py

# Make a directory
build_dir="probability-code-$version"
mkdir $build_dir

# Copy the "main" file
cp main.py $build_dir

# All directories to copy
directories=("causal_graphs" "config" "probability_structures" "tests" "utilities")

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
find ./documentation -name "*.md" -print0 | while read -rd $'\0' file
do
  # echo "File: ${file}"
  doc_name=${file%.md}
  doc_name=${doc_name#./documentation/}
  doc_name=$(echo -e "${doc_name}" | sed -re 's,_, ,g' -e 's/\<./\U&/g')

  # echo "Doc: ${doc_name}"
  pandoc "${file}" -o "${docs}/${doc_name}.pdf"
done

pandoc "Quick_Usage.md" -o "${build_dir}/Quick Usage.pdf"
pandoc "README.md" -o "${build_dir}/README.pdf"
