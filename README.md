# dockerfiles_public
Dockerfile for common tools

## digits server

digits server with:
* Anaconda
* cudnn
* caffe
* torch

This image requires the [nvidia-docker](https://github.com/NVIDIA/nvidia-docker) cuda+cudnn. The images can be built with the following command if the nvidia-docker tree is installed in a subdirectory at the same level than jguiraudet_public:
```bash
make -C nvidia-docker 7.5-cudnn3-devel
docker build -t digits-7.5-cudnn3 jguiraudet_public/digits

# run tests
GPU=0 nvidia-docker/nvidia-docker run -ti --rm digits-7.5-cudnn3-2 bash /root/test.sh |& test-results.txt

```

