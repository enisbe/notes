#!/bin/bash

# Define source and destination directories
SOURCE_DIR="/path/to/location_A"
DEST_DIR="/path/to/location_B"

# User ownership to check for
OWNER="user1"

# Find all files owned by $OWNER in $SOURCE_DIR and copy to $DEST_DIR, preserving folder structure
find "$SOURCE_DIR" -type f -user "$OWNER" | while read -r FILE; do
    # Get the relative path of the file
    REL_PATH="${FILE#$SOURCE_DIR/}"
    
    # Create the destination directory if it doesn't exist
    mkdir -p "$DEST_DIR/$(dirname "$REL_PATH")"
    
    # Copy the file to the destination
    cp "$FILE" "$DEST_DIR/$REL_PATH"
done

# Once copy is complete, delete files in $SOURCE_DIR owned by $OWNER
find "$SOURCE_DIR" -type f -user "$OWNER" -delete
