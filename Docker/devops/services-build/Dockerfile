# This dockerfile contains the build tools we use for TEST Micro Service projects
# It uses the ubuntu:22.04 base (because this is what Azure Devops needs)
# These are the tools installed:
# Ansible (latest)
# Azure CLI (latest)
# Git (latest)
# Docker (latest - stable)
# Docker-Compose (latest)
# Kubectl (latest)
# Helm 3 (latest)
# SOPS (3.6.1)
# NODE.JS (14.13.0)

FROM ubuntu:22.04
LABEL maintainer="TEST DevOps"

RUN apt update && apt upgrade -y
#SHARED TOOLS
RUN apt update && apt install -y curl
RUN apt update && apt install -y zip
RUN apt update && apt install -y unzip
RUN apt update && apt install -y sudo
#INSTALL PIP3
RUN apt update && apt install -y python3-pip
RUN pip3 install --upgrade pip
#ANSIBLE
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y software-properties-common
RUN pip3 install ansible
RUN pip3 install setuptools
RUN pip3 install packaging
RUN pip3 install netaddr
RUN pip3 install requests
RUN pip3 install jmespath
#AZURE CLI
ENV AZURE_EXTENSION_DIR=$HOME/.azure/cliextensions
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
RUN az extension add --name azure-devops
RUN az extension add --name application-insights
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
#DOCKER-COMPOSE
#RUN pip3 install docker-compose
#KUBECTL
RUN mkdir -p -m 755 /etc/apt/keyrings
RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
RUN echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt update && apt install -y kubectl
#HELM 3
ENV DESIRED_VERSION=v3.8.2
RUN curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
#SOPS
RUN apt update && apt install -y golang
RUN echo 'export GOPATH=~/go' >> ~/.bashrc
RUN . ~/.bashrc
RUN mkdir ~/go
RUN curl -OL https://github.com/mozilla/sops/releases/download/v3.6.1/sops_3.6.1_amd64.deb
RUN dpkg -i sops_3.6.1_amd64.deb
RUN rm sops_3.6.1_amd64.deb
#NODE.JS
RUN curl -sL https://deb.nodesource.com/setup_22.x | bash -
RUN apt update && apt install -y nodejs
#Maven
RUN apt update && apt install maven -y
RUN apt update && apt install default-jdk -y
#REMOVE EXTRA FILES AND UNUSED APPS
RUN apt autoremove --purge
#SYMLINK FOR PY3
RUN ln -sf $(which python3) /usr/bin/python
RUN ln -sf $(which pip3) /usr/bin/pip
#install jq
RUN apt update && apt install -y jq