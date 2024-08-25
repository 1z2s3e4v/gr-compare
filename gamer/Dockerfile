FROM nvcr.io/nvidia/pytorch:22.04-py3
LABEL maintainer="yjchen@eda.ee.ntu.edu.tw"

# update torch
RUN pip install --upgrade pip 
RUN pip install torch==1.12.0+cu116 torchvision==0.13.0+cu116 torchaudio==0.12.0 --extra-index-url https://download.pytorch.org/whl/cu116

# install dependencies
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y \
    wget \
    flex \
    libcairo2-dev 

RUN wget -O boost_1_66_0.tar.gz https://boostorg.jfrog.io/artifactory/main/release/1.66.0/source/boost_1_66_0.tar.gz && \
    tar xvf boost_1_66_0.tar.gz && \
    cd boost_1_66_0 && \
    ./bootstrap.sh  &&\
    ./b2 -q install -j 8 --without-python

# install commonly used python dependencies
RUN pip install seaborn \
    matplotlib

# ***********************************
# * Set non-root user (for VS Code) *
# ***********************************
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME
