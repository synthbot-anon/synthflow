#!/bin/bash

# This directory gets mounted into /tmp/spec

# Set up apex
cd /tmp/spec/nvidia-apex/
pip3 install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./
