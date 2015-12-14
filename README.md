# dockerfiles_public
Dockerfile for common tools

## digits server

digits server with:
* Anaconda
* cudnn v3
* caffe 0.14rc (to be compatible with cudnn v3)
* torch

This image requires the [nvidia-docker](https://github.com/NVIDIA/nvidia-docker) cuda+cudnn. The images can be built with the following command if the nvidia-docker tree is installed in a subdirectory at the same level than jguiraudet_public:
```bash
# Build images
make -C nvidia-docker 7.5-cudnn3-devel
docker build -t jguiraudet/digits jguiraudet_public/digits

# run tests with the script
jguiraudet/digits/run_test

# Start the container with the server with:
jguiraudet/digits/run_container

```

