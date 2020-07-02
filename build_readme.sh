#!/usr/bin/bash

readme_sections="readme_sections"

# Concatenate all 3 sections into one README.md
cat "${readme_sections}/README_1.md" "${readme_sections}/README_2.md" "${readme_sections}/README_3.md" > "README.md"

# Generate a specially-labelled file for quick access
cat "${readme_sections}/README_2.md" > "Quick_Usage.md"
