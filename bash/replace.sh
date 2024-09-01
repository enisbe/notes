#!/bin/bash

# Get the first and second positional arguments
first_arg=$1
second_arg=$2

# Check if the second argument is provided and not empty
if [ -n "$second_arg" ]; then
  # Use sed to replace the BQ_DATASET value with the second argument
  sed -i "s/\(BQ_DATASET= *\"\)[^\"]*\"/\1$second_arg\"/" config.py
else
  echo "Second argument is empty or not provided. No changes made."
fi
