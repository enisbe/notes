#!/bin/bash

# Initialize variables
DEV_STATUS=""
GCP_PROJECT_ID=""

# Parse named arguments
while [ "$1" != "" ]; do
    case $1 in
        --DEV_STATUS=* )
            DEV_STATUS="${1#*=}"
            ;;
        --GCP_PROJECT_ID=* )
            GCP_PROJECT_ID="${1#*=}"
            ;;
        * )
            echo "Error: Invalid argument."
            exit 1
    esac
    shift
done

# Check if required arguments are provided
if [ -z "$DEV_STATUS" ] || [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: Missing required arguments."
    echo "Usage: deploy --DEV_STATUS=<status> --GCP_PROJECT_ID=<project_id>"
    exit 1
fi

# Write to config.py
cat <<EOL > folder1/config.py
DEV_STATUS="$DEV_STATUS"
GCP_PROJECT_ID="$GCP_PROJECT_ID"
EOL

echo "Configuration written to folder1/config.py"
