# Dockerfile

# Use a base Python image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the epanet folder into the container
COPY epanet /app/epanet

# Install epyt
RUN pip install epyt

# Install pymodbus
RUN pip install pymodbus 

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh

# Give execute permission to the entrypoint script
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/app/entrypoint.sh"]
