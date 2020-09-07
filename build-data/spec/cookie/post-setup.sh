#!/bin/bash

# The run-data directory gets mounted into /data

# Download the nvidia-apex repo if it doesn't already exist
if [ ! -d /data/src/nvidia-apex ]; then
  git clone 'https://github.com/NVIDIA/apex.git' /data/src/nvidia-apex
fi

# Set up apex
cd /data/src/nvidia-apex/
pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./
