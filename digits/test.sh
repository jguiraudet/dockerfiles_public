#!/bin/bash

set -x
set -e

# Test caffe
cd ~/caffe/build/
time make pytest
time make runtest

# Test torch
cd ~/torch
time ./test.sh

# Test digits
cd ~/digits
time ./digits-test



