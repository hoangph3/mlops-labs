FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu18.04

RUN apt-get -y update
RUN apt-get install -y python3 python3-pip

RUN python3 -m pip install --upgrade pip && python3 -m pip install setuptools
RUN python3 -m pip install tensorflow_datasets idx2numpy tensorflow==2.6.2 tensorflow-gpu==2.6.2

ADD mnist mnist

RUN export PATH="$PATH:/usr/local/bin/python3"
ENTRYPOINT ["python3", "-m", "mnist.main"]