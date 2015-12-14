#!/bin/bash

set -x
set -e

# Disable raw1394 to avoid the openCV warning "libdc1394 error: Failed to initialize libdc1394"
ln /dev/null /dev/raw1394

# List available cuda GPU
~/digits/digits/device_query.py

# Test caffe
cd ~/caffe/build/
make pytest
make runtest

# Test torch
cd ~/torch
./test.sh

# Test digits
cd ~/digits
./digits-test



