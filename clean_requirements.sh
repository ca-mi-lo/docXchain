#!/bin/bash

if [ $# -eq 0 ]; then
  requirements_file="requirements_extra.txt"
else
  requirements_file="$1"
fi

# File to process
requirements_extra_file="requirements_extra.txt"

# Temporary output file
temp_file="requirements_extra_temp.txt"

# Process the requirements_extra file
while IFS= read -r line; do
  # Remove the @ suffix and everything after it
  clean_line=$(echo "$line" | cut -d '@' -f 1)
  echo "$clean_line" >> "$temp_file"
done < "$requirements_extra_file"

# Overwrite the original file with the cleaned content
mv "$temp_file" "$requirements_extra_file"

echo "requirements_extra.txt cleaned successfully"