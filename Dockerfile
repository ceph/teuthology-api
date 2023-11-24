FROM ubuntu:focal
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    git \
    qemu-utils \
    python3-dev \
    libssl-dev \
    ipmitool \
    python3-pip \
    python3-venv \
    vim \
    curl \
    libev-dev \
    libvirt-dev \
    libffi-dev \
    libyaml-dev \
    lsb-release && \
    apt-get clean all

COPY setup.py .
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install -e .

COPY .teuthology.yaml /root
WORKDIR /teuthology_api
COPY . /teuthology_api/

CMD sh /teuthology_api/start_container.sh
