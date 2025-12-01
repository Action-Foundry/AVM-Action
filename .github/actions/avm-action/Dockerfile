# AVM Action Dockerfile
# This container provides a Python-based environment for running Terraform
# commands in Azure Verified Modules (AVM)-style environments.

FROM python:3.11-slim

# Terraform version to install (can be overridden at build time)
ARG TERRAFORM_VERSION=1.6.0

# Labels for the container
LABEL org.opencontainers.image.title="AVM Action"
LABEL org.opencontainers.image.description="GitHub Action for Terraform in Azure Verified Modules environments"
LABEL org.opencontainers.image.authors="Action-Foundry"
LABEL org.opencontainers.image.source="https://github.com/Action-Foundry/AVM-Action"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN wget -q https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && chmod +x /usr/local/bin/terraform

# Verify Terraform installation
RUN terraform version

# Set up working directory
WORKDIR /action

# Copy Python dependencies
COPY requirements.txt /action/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /action/src/

# Copy and set up entrypoint
COPY entrypoint.sh /action/entrypoint.sh
RUN chmod +x /action/entrypoint.sh

# Set Python path to include the action source
ENV PYTHONPATH="/action"

# Set entrypoint
ENTRYPOINT ["/action/entrypoint.sh"]
