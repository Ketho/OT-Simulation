#!/bin/sh

# Find any .inp file in the /app folder
INP_FILE=$(find /app -name "*.inp" | head -n 1)

# Check if an .inp file was found
if [ -z "$INP_FILE" ]; then
    echo "No .inp file found in /app"
    exit 1
fi

# Run the Python script with the found .inp file as argv2
python /app/epanet.py "$INP_FILE"
