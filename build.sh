#!/usr/bin/env bash
# Exit on error
set -o errexit

# Initialize the mock database
python database.py

# Train the NLP model directly on the server to ensure version compatibility
python train.py