# Adapted from: https://github.com/gw0/docker-keras-jupyter/blob/master/Dockerfile
# docker-debian-cuda - Debian 9 with CUDA Toolkit

FROM gw000/keras:2.1.1-gpu
MAINTAINER gw0 [http://gw.tnode.com/] <gw.2017@ena.one>

# install py3-tf-cpu/gpu (Python 3, TensorFlow, CPU/GPU)
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install python 3
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-virtualenv \
    python3-wheel \
    pkg-config \
    # requirements for numpy
    libopenblas-base \
    python3-numpy \
    python3-scipy \
    # requirements for keras
    python3-h5py \
    python3-yaml \
    python3-pydot \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ARG TENSORFLOW_VERSION=1.4.0
ARG TENSORFLOW_DEVICE=gpu
ARG TENSORFLOW_APPEND=_gpu
RUN pip3 --no-cache-dir install https://storage.googleapis.com/tensorflow/linux/${TENSORFLOW_DEVICE}/tensorflow${TENSORFLOW_APPEND}-${TENSORFLOW_VERSION}-cp35-cp35m-linux_x86_64.whl


# install Keras for Python 3
ARG KERAS_VERSION=2.1.1
ENV KERAS_BACKEND=tensorflow
RUN pip3 --no-cache-dir install --no-dependencies git+https://github.com/fchollet/keras.git@${KERAS_VERSION}

# install additional debian packages
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # system tools
    less \
    procps \
    vim-tiny \
    # build dependencies
    build-essential \
    libffi-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

 RUN python3 -c "import tensorflow; print(tensorflow.__version__)" \
 && dpkg-query -l > /dpkg-query-l.txt \
 && pip3 freeze > /pip3-freeze.txt

 # Copy application to container
 RUN mkdir -p app
 WORKDIR /app
 COPY . /app

 # Install requirements
 RUN pip install -r requirements.txt

 # Expose default port and start app
 EXPOSE 5000
 ENTRYPOINT ["python", "web_demo.py", "--bind-address", "0.0.0.0", "--pg-agent", "/app/agents/9x9_from_nothing/round_007.hdf5", "--predict-agent", "/app/agents/betago.hdf5"]
