# This dockerfile contains the build tools we use for TEST Infrastructure projects
# It uses the ubuntu:22.04 base (because this is what Azure Devops needs)
# These are the tools installed:
# Ansible (latest)
# Terraform (1.0.0)
# Azure CLI (latest)
# Git (latest)
# Kubectl (latest)
# Helm 3 (latest)
# Powershell
# SOPS (3.6.1)

# container with build tools
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
#TERRAFORM
RUN apt update && apt install -y unzip
RUN curl https://releases.hashicorp.com/terraform/1.0.0/terraform_1.0.0_linux_amd64.zip > terraform.zip
RUN unzip terraform.zip
RUN rm terraform.zip
RUN mv terraform /usr/local/bin
#AZURE CLI
ENV AZURE_EXTENSION_DIR=$HOME/.azure/cliextensions
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
RUN az extension add --name azure-firewall
RUN az extension add --name application-insights
#GIT
RUN apt update && apt install -y git
#KUBECTL
RUN mkdir -p -m 755 /etc/apt/keyrings
RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
RUN echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt update && apt install -y kubectl
#HELM 3
ENV DESIRED_VERSION=v3.11.0
RUN curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
#POWERSHELL
RUN curl -OL https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN rm packages-microsoft-prod.deb
RUN apt update && apt install -y powershell
#SOPS
RUN apt update && apt install -y golang
RUN echo 'export GOPATH=~/go' >> ~/.bashrc
RUN . ~/.bashrc
RUN mkdir ~/go
RUN curl -OL https://github.com/mozilla/sops/releases/download/v3.6.1/sops_3.6.1_amd64.deb
RUN dpkg -i sops_3.6.1_amd64.deb
RUN rm sops_3.6.1_amd64.deb
#REMOVE EXTRA FILES AND UNUSED APPS
RUN apt autoremove --purge
#SYMLINK FOR PY3
RUN ln -sf $(which python3) /usr/bin/python
RUN ln -sf $(which pip3) /usr/bin/pip