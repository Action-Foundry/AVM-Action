#!/bin/bash
# Entrypoint script for AVM Action
# This script parses GitHub Action inputs and runs the Python action code.

set -e

# Function to log messages
log() {
    echo "[AVM-Action] $1"
}

# Function to log debug messages
debug() {
    if [ "${INPUT_LOG_LEVEL}" = "DEBUG" ]; then
        echo "[AVM-Action DEBUG] $1"
    fi
}

# Function to set GitHub Action output
set_output() {
    local name="$1"
    local value="$2"
    if [ -n "${GITHUB_OUTPUT}" ]; then
        if [[ "$value" == *$'\n'* ]]; then
            echo "${name}<<EOF" >> "${GITHUB_OUTPUT}"
            echo "${value}" >> "${GITHUB_OUTPUT}"
            echo "EOF" >> "${GITHUB_OUTPUT}"
        else
            echo "${name}=${value}" >> "${GITHUB_OUTPUT}"
        fi
    else
        echo "::set-output name=${name}::${value}"
    fi
}

log "Starting AVM Action"
debug "Terraform directory: ${INPUT_TF_DIRECTORY}"
debug "Command: ${INPUT_COMMAND}"
debug "Workspace: ${INPUT_WORKSPACE}"
debug "Log level: ${INPUT_LOG_LEVEL}"

# Verify Terraform is available
if ! command -v terraform &> /dev/null; then
    log "ERROR: Terraform not found in PATH"
    exit 1
fi

log "Terraform version: $(terraform version -json | python3 -c 'import sys,json; print(json.load(sys.stdin)["terraform_version"])')"

# Change to the Terraform directory if specified
if [ -n "${INPUT_TF_DIRECTORY}" ] && [ "${INPUT_TF_DIRECTORY}" != "." ]; then
    if [ ! -d "${INPUT_TF_DIRECTORY}" ]; then
        log "ERROR: Terraform directory not found: ${INPUT_TF_DIRECTORY}"
        exit 1
    fi
    debug "Changing to directory: ${INPUT_TF_DIRECTORY}"
    cd "${INPUT_TF_DIRECTORY}"
fi

# Set up Azure environment variables if provided
if [ -n "${INPUT_AZURE_SUBSCRIPTION_ID}" ]; then
    export ARM_SUBSCRIPTION_ID="${INPUT_AZURE_SUBSCRIPTION_ID}"
    debug "Set ARM_SUBSCRIPTION_ID"
fi

if [ -n "${INPUT_AZURE_TENANT_ID}" ]; then
    export ARM_TENANT_ID="${INPUT_AZURE_TENANT_ID}"
    debug "Set ARM_TENANT_ID"
fi

if [ -n "${INPUT_AZURE_CLIENT_ID}" ]; then
    export ARM_CLIENT_ID="${INPUT_AZURE_CLIENT_ID}"
    debug "Set ARM_CLIENT_ID"
fi

# Run the Python action
log "Running Python action module"
python3 -m src.main
exit_code=$?

if [ $exit_code -ne 0 ]; then
    log "Action failed with exit code: ${exit_code}"
    exit $exit_code
fi

log "AVM Action completed successfully"
