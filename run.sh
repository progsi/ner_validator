#!/bin/bash

# Define the environment name and YAML file
ENV_NAME="ner_validator"
ENV_YAML="env.yml"

# Check if the environment already exists
if conda env list | grep -q "$ENV_NAME"; then
    echo "Environment '$ENV_NAME' already exists. Activating..."
else
    echo "Environment '$ENV_NAME' not found. Creating and installing from '$ENV_YAML'..."
    conda env create -f $ENV_YAML
fi

# Initialize Conda if not already initialized
if ! type "conda" > /dev/null 2>&1; then
    echo "Conda not found. Please ensure Conda is installed and initialized."
    exit 1
fi

# Activate the environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# Run the Streamlit app
streamlit run app.py

