#!/bin/bash

# Git Branch Helpers
#
# This script provides a set of bash functions to simplify common Git branch operations,
# such as fetching, checking out, and tracking remote branches.
#
# To use these functions, load this script into your shell environment by running:
# source git_branch_helpers.sh
#
# Once sourced, you can use the functions directly in your terminal.

# --- Function Definitions ---

# Fetches all branches and tags from the 'origin' remote.
# This updates your local repository with the latest information from the remote,
# but it does not modify your working directory.
#
# Usage:
#   git_fetch_origin
#
git_fetch_origin() {
    echo "Fetching all branches and tags from origin..."
    git fetch origin
}

# Checks out a branch that exists on the remote but not locally.
# It creates a local branch with the same name that tracks the remote branch.
# Requires the branch name as an argument.
# It's a good practice to run 'git_fetch_origin' before this.
#
# Usage:
#   git_checkout_remote <branch-name>
#
git_checkout_remote() {
    if [ -z "$1" ]; then
        echo "Error: Branch name not provided."
        echo "Usage: git_checkout_remote <branch-name>"
        return 1
    fi
    echo "Checking out '$1' and tracking 'origin/$1'..."
    git checkout "$1"
}

# A more modern approach using 'git switch'.
# Fetches from origin and then switches to the specified branch.
# If the branch doesn't exist locally, it creates a tracking branch.
#
# Usage:
#   git_switch_to_branch <branch-name>
#
git_switch_to_branch() {
    if [ -z "$1" ]; then
        echo "Error: Branch name not provided."
        echo "Usage: git_switch_to_branch <branch-name>"
        return 1
    fi
    echo "Fetching from origin..."
    git fetch origin
    echo "Switching to branch '$1'..."
    git switch "$1"
}


# Fetches from the remote and creates a local branch to track a remote branch,
# allowing you to specify a different name for your local branch.
#
# Usage:
#   git_checkout_remote_as <local-branch-name> <remote-branch-name>
#
git_checkout_remote_as() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Error: Local and remote branch names must be provided."
        echo "Usage: git_checkout_remote_as <local-branch-name> <remote-branch-name>"
        return 1
    fi
    echo "Fetching from origin..."
    git fetch origin
    echo "Checking out 'origin/$2' as local branch '$1'..."
    git checkout -b "$1" "origin/$2"
}

echo "Git helper functions loaded. You can now use:"
echo "  - git_fetch_origin"
echo "  - git_checkout_remote <branch-name>"
echo "  - git_switch_to_branch <branch-name>"
echo "  - git_checkout_remote_as <local-name> <remote-name>" 
