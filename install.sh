#!/bin/bash

# Initialize Conda for bash
source "$(conda info --base)/etc/profile.d/conda.sh"

# Replace "new_environment_name" with the desired name for the new environment
env_name="whispering_assistant_env"

conda env create -f environment.yml -n "$env_name" --verbose
conda activate "$env_name"

# Manual install of gstreamer is needed for the playback video using pyqt5
# Latest version of gstreamer is not yet set as dependency for pyqt5
conda install --no-deps -c conda-forge gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gstreamer=1.22.0 -y
