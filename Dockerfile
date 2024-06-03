FROM ubuntu:jammy
ENV DEBIAN_FRONTEND=noninteractive
ENV VENV=${VENV:-"venv"}
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

COPY .teuthology.yaml /root
WORKDIR /teuthology_api
COPY . /teuthology_api/
RUN python3 -m venv ${VENV}
RUN /teuthology_api/${VENV}/bin/pip3 install -e .
RUN mkdir /archive_dir/

ENTRYPOINT /teuthology_api/start_container.sh
