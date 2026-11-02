FROM python:3.10-slim

WORKDIR /app

# Install system packages required by Azure CLI
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    apt-transport-https \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install kubectl and kubelogin for AKS
RUN az aks install-cli

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY cluster-info.py /app

CMD ["python", "/app/cluster-info.py"]