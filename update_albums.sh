#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run the Python script to update albums
python save_ytm_albums.py

# Check if albums.json has changed
if git diff --quiet albums.json; then
    echo "No changes detected in albums.json. Exiting."
    deactivate
    exit 0
fi

# Stage the changes
git add albums.json

# Commit the changes
git commit -m "Update albums.json"

# Push the changes to the remote repository
git push

# Deactivate the virtual environment
deactivate

echo "Albums updated, committed, and pushed successfully."
