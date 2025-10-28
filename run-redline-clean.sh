#!/bin/bash

# REDLINE Clean Docker Run Script
# Runs with host networking for external API access

echo "Starting REDLINE with host networking..."

# Stop any existing containers
docker stop $(docker ps -q --filter ancestor=redline-clean) 2>/dev/null

# Run with host networking for external API access
docker run --network=host -p 8080:8080 --name redline-clean-container redline-clean

echo "REDLINE is running at http://localhost:8080"




