import os
import json
import time
import subprocess
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("aks-maintenance-collector")

COLLECTION_INTERVAL = 300

tenant_id = os.getenv("tenant_id")
storage_account_name = os.getenv("storage_account_name","testfilesdev")
storage_account_key = os.getenv("storage_account_key")
storage_container_name = os.getenv("storage_container_name","devops")
folder_name = "clusters_info"
file_name = "cluster_info.json"

# subscriptions
dev_subscription_id = os.getenv("dev_subscription_id")
sub_subscription_id = os.getenv("sub_subscription_id")

# cluster configuration
CLUSTER_ENVIRONMENTS = [
    {
        "environment": "DEV",
        "cluster_name": "TEST-AKS-Dev-Cluster",
        "resource_group": "TEST-AKS-Dev",
        "service_principal_id": os.getenv("dev_service_principal_id"),
        "service_principal_secret": os.getenv("dev_service_principal_secret"),
        "subscription_id": dev_subscription_id,
    },
    {
        "environment": "QA",
        "cluster_name": "TEST-AKS-QA-Cluster",
        "resource_group": "TEST-AKS-QA",
        "service_principal_id": os.getenv("dev_service_principal_id"),
        "service_principal_secret": os.getenv("dev_service_principal_secret"),
        "subscription_id": dev_subscription_id,
    },
]

def run_command(command, description=None, env=None):
    if description:
        logger.info(description)
    logger.debug("Running command: %s"," ".join(command),)
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        logger.error(
            "Command failed with exit code %s",
            result.returncode,
        )
        if result.stdout:
            logger.error("stdout: %s",result.stdout.strip(),)
        if result.stderr:
            logger.error("stderr: %s",result.stderr.strip(),)
        raise RuntimeError(
            f"Command failed: {' '.join(command)}"
        )
    if result.stdout:
        logger.debug("stdout: %s",result.stdout.strip(),)
    return result.stdout


def validate_global_config():
    required = {
        "tenant_id": tenant_id,
        "storage_account_name": storage_account_name,
        "storage_account_key": storage_account_key,
        "dev_subscription_id": dev_subscription_id,
        "sub_subscription_id": sub_subscription_id,
    }
    missing = [
        name
        for name, value in required.items()
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
        )

def validate_cluster_config(config):
    required = {
        "cluster_name": config.get("cluster_name"),
        "resource_group": config.get("resource_group"),
        "service_principal_id": config.get("service_principal_id"),
        "service_principal_secret": config.get("service_principal_secret"),
        "subscription_id": config.get("subscription_id"),
    }
    missing = [
        name
        for name, value in required.items()
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing configuration for "
            f"{config.get('environment', 'Unknown')}: "
            f"{', '.join(missing)}"
        )

def login_to_azure(config):
    logger.info(
        "Logging into Azure for environment: %s",
        config["environment"],
    )
    #logger.info(
    #  "Using service principal: %s",
    #   config["service_principal_id"],
    #)
    run_command(
        [
            "az",
            "login",
            "--service-principal",
            "--username",
            config["service_principal_id"],
            "--password",
            config["service_principal_secret"],
            "--tenant",
            tenant_id,
        ],
        description=(
            f"Azure login for "
            f"{config['environment']}"
        ),
    )
    run_command(
        [
            "az",
            "account",
            "set",
            "--subscription",
            config["subscription_id"],
        ],
        description=(
            f"Setting subscription for "
            f"{config['environment']}"
        ),
    )

'''
def verify_azure_identity(config):
    logger.info(
        "Verifying Azure identity for %s",
        config["environment"],
    )
    output = run_command(
        [
            "az",
            "account",
            "show",
            "--query",
            "{subscription:id,tenant:tenantId,user:user.name,type:user.type}",
            "-o",
            "json",
        ],
        description=(
            f"Checking Azure identity for "
            f"{config['environment']}"
        ),
    )
    logger.info(
        "Azure identity for %s: %s",
        config["environment"],
        output.strip(),
    )
    return output
'''

def get_aks_credentials(config):
    logger.info(
        "Getting AKS credentials for %s",
        config["cluster_name"],
    )
    run_command(
        [
            "az",
            "aks",
            "get-credentials",
            "--resource-group",
            config["resource_group"],
            "--name",
            config["cluster_name"],
            "--overwrite-existing",
        ],
        description=(
            f"Getting kubeconfig for "
            f"{config['cluster_name']}"
        ),
    )
    run_command(
        [
            "kubelogin",
            "convert-kubeconfig",
            "-l",
            "azurecli",
        ],
        description=(
            f"Converting kubeconfig for "
            f"{config['cluster_name']}"
        ),
    )

'''
def verify_kubernetes_identity(config):
    logger.info(
        "Verifying Kubernetes identity for %s",
        config["environment"],
    )
    output = run_command(
        [
            "kubectl",
            "auth",
            "whoami",
        ],
        description=(
            f"Checking Kubernetes identity for "
            f"{config['environment']}"
        ),
    )
    logger.info(
        "Kubernetes identity for %s:\n%s",
        config["environment"],
        output.strip(),
    )
    return output
'''

# get nodes
def get_nodes():
    output = run_command(
        [
            "kubectl",
            "get",
            "nodes",
            "-o",
            "json",
        ],
        description="Collecting AKS node information",
    )
    return json.loads(output)

# get podes
def get_pods():
    output = run_command(
        [
            "kubectl",
            "get",
            "pods",
            "--all-namespaces",
            "-o",
            "json",
        ],
        description="Collecting AKS pod information",
    )
    return json.loads(output)

# get deployments
def get_deployments():
    output = run_command(
        [
            "kubectl",
            "get",
            "deployments",
            "--all-namespaces",
            "-o",
            "json",
        ],
        description="Collecting AKS deployment information",
    )
    return json.loads(output)


# get node info
def parse_node_information(nodes_data):
    nodes = nodes_data.get("items", [])
    if not nodes:
        return {
            "node_type": "Unknown",
            "node_count": 0,
            "vCPU": 0,
            "memory": 0,
        }
    node_count = len(nodes)
    node_types = []
    total_cpu = 0
    total_memory_gib = 0
    for node in nodes:
        labels = (
            node
            .get("metadata", {})
            .get("labels", {})
        )
        node_type = (
                labels.get(
                    "node.kubernetes.io/instance-type"
                )
                or labels.get(
            "beta.kubernetes.io/instance-type"
        )
                or "Unknown"
        )
        node_types.append(node_type)
        capacity = (
            node
            .get("status", {})
            .get("capacity", {})
        )
        cpu_value = capacity.get(
            "cpu",
            "0",
        )
        try:
            total_cpu += int(cpu_value)
        except ValueError:
            logger.warning(
                "Unable to parse CPU value: %s",
                cpu_value,
            )
        memory_value = capacity.get(
            "memory",
            "0Ki",
        )
        try:
            if memory_value.endswith("Ki"):
                memory_gib = (
                        int(memory_value[:-2])
                        / 1024
                        / 1024
                )
            elif memory_value.endswith("Mi"):
                memory_gib = (
                        int(memory_value[:-2])
                        / 1024
                )
            elif memory_value.endswith("Gi"):
                memory_gib = int(
                    memory_value[:-2]
                )
            else:
                memory_gib = 0
            total_memory_gib += memory_gib
        except ValueError:
            logger.warning(
                "Unable to parse memory value: %s",
                memory_value,
            )
    average_cpu = (
        round(total_cpu / node_count)
        if node_count
        else 0
    )
    average_memory = (
        round(total_memory_gib / node_count)
        if node_count
        else 0
    )
    unique_node_types = list(
        dict.fromkeys(node_types)
    )
    node_type_result = (
        unique_node_types[0]
        if len(unique_node_types) == 1
        else ", ".join(unique_node_types)
    )
    return {
        "node_type": node_type_result,
        "node_count": node_count,
        "vCPU": average_cpu,
        "memory": average_memory,
    }

# get pod info
def parse_pod_information(pods_data):
    pods = pods_data.get(
        "items",
        [],
    )
    running_pod_count = 0
    for pod in pods:
        phase = (
            pod
            .get("status", {})
            .get("phase")
        )
        if phase == "Running":
            running_pod_count += 1
    return running_pod_count

# get deployment info
def parse_deployment_information(
        deployments_data
):
    deployments = deployments_data.get(
        "items",
        [],
    )
    deployed_services = []
    for deployment in deployments:
        metadata = deployment.get(
            "metadata",
            {},
        )
        status = deployment.get(
            "status",
            {},
        )
        name = metadata.get(
            "name",
            "Unknown",
        )
        namespace = metadata.get(
            "namespace",
            "default",
        )
        ready_replicas = status.get(
            "readyReplicas",
            0,
        )
        deployed_services.append(
            {
                "name": name,
                "namespace": namespace,
                "pod_count": ready_replicas or 0,
            }
        )
    return deployed_services

# collect cluster info
def collect_cluster(config):
    logger.info("==================================================")
    logger.info(
        "Collecting information for environment: %s",
        config["environment"],
    )
    logger.info(
        "Cluster: %s",
        config["cluster_name"],
    )
    logger.info(
        "Resource group: %s",
        config["resource_group"],
    )
    #logger.info(
    #   "Subscription: %s",
    #  config["subscription_id"],
    #)
    #logger.info(
    #   "Service principal: %s",
    #  config["service_principal_id"],
    #)
    validate_cluster_config(config)
    login_to_azure(config)
    #verify_azure_identity(config)
    get_aks_credentials(config)
    #verify_kubernetes_identity(config)
    nodes_data = get_nodes()
    pods_data = get_pods()
    deployments_data = get_deployments()
    node_information = parse_node_information(
        nodes_data
    )
    total_pod_count = parse_pod_information(
        pods_data
    )
    deployed_services = (
        parse_deployment_information(
            deployments_data
        )
    )
    cluster_data = {
        "nodes": node_information,
        "pods": {
            "total_pod_count": total_pod_count,
            "deployed": deployed_services,
        },
    }
    logger.info(
        "Cluster %s collected successfully",
        config["cluster_name"],
    )
    logger.info(
        "Nodes: %s",
        node_information,
    )
    logger.info(
        "Running pods: %s",
        total_pod_count,
    )
    logger.info(
        "Deployments: %s",
        len(deployed_services),
    )
    return cluster_data

# blob storage
def get_blob_client():
    connection_string = (
        "DefaultEndpointsProtocol=https;"
        f"AccountName={storage_account_name};"
        f"AccountKey={storage_account_key};"
        "EndpointSuffix=core.windows.net"
    )
    blob_service_client = (
        BlobServiceClient.from_connection_string(
            connection_string
        )
    )
    blob_path = (
        f"{folder_name}/{file_name}"
    )
    return blob_service_client.get_blob_client(
        container=storage_container_name,
        blob=blob_path,
    )

# download existing json
def download_existing_data():
    blob_client = get_blob_client()
    try:
        logger.info(
            "Downloading existing dashboard JSON "
            "from Azure Blob Storage"
        )
        data = (
            blob_client
            .download_blob()
            .readall()
        )
        existing_data = json.loads(
            data.decode("utf-8")
        )
        if not isinstance(
                existing_data,
                dict,
        ):
            raise RuntimeError(
                "Existing JSON is not a valid object"
            )
        if not isinstance(
                existing_data.get("clusters"),
                dict,
        ):
            raise RuntimeError(
                "Existing JSON does not contain "
                "a valid 'clusters' object"
            )
        return existing_data
    except Exception as exc:
        logger.error(
            "Unable to download existing JSON: %s",
            exc,
        )
        raise

# upload json
def upload_data(data):
    blob_client = get_blob_client()
    json_data = json.dumps(
        data,
        indent=2,
    )
    blob_client.upload_blob(
        json_data,
        overwrite=True,
    )
    logger.info("Dashboard JSON uploaded successfully")

# ONE COLLECTION CYCLE
def run_collection_cycle():
    logger.info("==================================================")
    logger.info("Starting AKS Maintenance Collector cycle")
    logger.info(
        "Collection time: %s",
        datetime.now(timezone.utc).isoformat(),
    )
    logger.info("==================================================")
    validate_global_config()
    existing_data = download_existing_data()
    successful_clusters = 0
    failed_clusters = 0
    for config in CLUSTER_ENVIRONMENTS:
        try:
            if not config.get("cluster_name"):
                logger.error(
                    "Cluster name is missing for %s. "
                    "Skipping.",
                    config.get(
                        "environment",
                        "Unknown",
                    ),
                )
                failed_clusters += 1
                continue
            cluster_data = collect_cluster(
                config
            )
            existing_data["clusters"][
                config["cluster_name"]
            ] = cluster_data
            successful_clusters += 1
        except Exception as exc:
            failed_clusters += 1
            logger.exception(
                "Failed to collect cluster %s: %s",
                config.get(
                    "cluster_name",
                    "Unknown",
                ),
                exc,
            )
            continue
    existing_data["metadata"] = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "cluster_count": len(
            existing_data["clusters"]
        ),
    }

    upload_data(existing_data)
    logger.info("==================================================")
    logger.info("AKS Maintenance Collector cycle completed")
    logger.info(
        "Successful clusters: %s",
        successful_clusters,
    )
    logger.info(
        "Failed clusters: %s",
        failed_clusters,
    )
    logger.info(
        "Total clusters in dashboard JSON: %s",
        len(existing_data["clusters"]),
    )
    logger.info("==================================================")

def main():
    logger.info("Starting continuous AKS Maintenance Collector")
    logger.info(
        "Collection interval: %s seconds (%s minutes)",
        COLLECTION_INTERVAL,
        COLLECTION_INTERVAL // 60,
        )
    while True:
        try:
            run_collection_cycle()
        except Exception as exc:
            logger.exception(
                "AKS collection cycle failed: %s",
                exc,
            )
        logger.info(
            "Next AKS collection will start in %s seconds "
            "(%s minutes)",
            COLLECTION_INTERVAL,
            COLLECTION_INTERVAL // 60,
            )
        time.sleep(
            COLLECTION_INTERVAL
        )

if __name__ == "__main__":
    main()