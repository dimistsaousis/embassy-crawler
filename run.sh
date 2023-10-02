#!/bin/bash

# Check if virtual environment exists, if not create it
if [ ! -d ".embassy_crawler_venv" ]; then
  python3 -m venv .embassy_crawler_venv
fi

# Activate the virtual environment
source .embassy_crawler_venv/bin/activate

# Define cleanup procedure
function cleanup {
    deactivate
}

# Register the cleanup function to be called on the EXIT signal
trap cleanup EXIT

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q


export PYTHONWARNINGS="ignore"

# Run the script
echo "Running appointment listener..."
echo 
python main.py --email "$1" --password "$2"

