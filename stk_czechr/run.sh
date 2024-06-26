#!/bin/bash

set -e

# Set up environment for Python script
export PYTHONPATH=/usr/lib/python3.9/site-packages

# Start the Python script
python3 /fetch_car_inspection.py
