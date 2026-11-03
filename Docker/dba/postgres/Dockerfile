# This dockerfile contains the build tools we use for AMPS Infrastructure PGaaS Blinded DB
# It uses the ubuntu:22.04 base (because this is what Azure Devops needs)
# These are the tools installed:
# Ansible (latest)
# Azure CLI (latest)
# Git (latest)
# Docker (latest - stable)
# Kubectl (latest)
# Helm 3 (latest)
# SOPS (3.6.1)
# PSQL Client (latest)

FROM ubuntu:22.04
LABEL maintainer="TEST DevOps"

RUN apt update && apt upgrade -y
#SHARED TOOLS
RUN apt update && apt install -y curl
#INSTALL PIP3
RUN apt update && apt install -y python3-pip
RUN pip3 install --upgrade pip
RUN apt update && apt upgrade -y
#ANSIBLE
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y software-properties-common
RUN pip3 install ansible
RUN pip3 install setuptools
RUN pip3 install packaging
RUN pip3 install netaddr
RUN pip3 install requests
RUN pip3 install jmespath
#AZURE CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
#GIT
RUN apt update && apt install -y git
#DOCKER
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        -o /etc/apt/trusted.gpg.d/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu jammy stable" \
        > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        docker-ce-cli docker-buildx-plugin docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*
#KUBECTL
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list
RUN apt update && apt install -y kubectl
#HELM 3
ENV DESIRED_VERSION=v3.6.3
RUN curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
#SOPS
RUN apt update && apt install -y golang
RUN echo 'export GOPATH=~/go' >> ~/.bashrc
RUN . ~/.bashrc
RUN mkdir ~/go
RUN curl -OL https://github.com/mozilla/sops/releases/download/v3.6.1/sops_3.6.1_amd64.deb
RUN dpkg -i sops_3.6.1_amd64.deb
RUN rm sops_3.6.1_amd64.deb
#INSTALL PSQL CLIENT
RUN apt update && apt install -y postgresql-client
#REMOVE EXTRA FILES AND UNUSED APPS
RUN apt autoremove --purge
#SYMLINK FOR PY3
RUN ln -sf $(which python3) /usr/bin/python
RUN ln -sf $(which pip3) /usr/bin/pip
CMD ["/bin/bash", "-c", "tail -f /dev/null"]
