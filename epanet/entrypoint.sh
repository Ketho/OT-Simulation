#!/bin/sh

# Find any .inp file in the /app/epanet folder
INP_FILE=$(find /app/epanet -name "*.inp" | head -n 1)

# Check if an .inp file was found
if [ -z "$INP_FILE" ]; then
    echo "No .inp file found in /app/epanet!"
    exit 1
fi

# Run the Python script with the found .inp file as argv2
python /app/epanet/epanet.py "$INP_FILE"
