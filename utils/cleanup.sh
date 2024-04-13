#!/bin/bash

script_dir=$(dirname "$0")
dir="$script_dir/../videos"
echo "Directory: $dir"

file_count=$(ls -1tr "$dir" | wc -l)
echo "File count: $file_count"

if [ "$file_count" -gt 100 ]; then
    remove_count=$((file_count - 100))
    echo "Remove count: $remove_count"

    ls -1tr "$dir" | head -n "$remove_count" | while read -r file; do
        echo "Removing: $file"
        rm -f -- "$dir/$file"
    done
fi
