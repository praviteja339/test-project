resource "azurerm_policy_definition" "aks_user_group_assignment_definition" {
  name         = "aks_user_group_assignment_${var.env}"
  description  = "Kubernetes cluster pods and containers should only run with approved user and group IDs"
  policy_type  = "Custom"
  mode         = "Microsoft.Kubernetes.Data"
  display_name = "TEST AKS User Group Assignment ${var.env}"

  metadata = jsonencode({
    category = "Kubernetes"
    version = "1.0.0"
  })

  policy_rule = file("policies/user_group_assignment/policy_rule.json")
  parameters = file("policies/user_group_assignment/parameters.json")
}

resource "azurerm_policy_definition" "aks_privilege_escalation_definition" {
  name         = "aks_privilege_escalation_${var.env}"
  description  = "Kubernetes clusters should not allow container privilege escalation"
  policy_type  = "Custom"
  mode         = "Microsoft.Kubernetes.Data"
  display_name = "TEST AKS Privilege Escalation ${var.env}"

  metadata = jsonencode({
    category = "Kubernetes"
    version = "1.0.0"
  })

  policy_rule = file("policies/privilege_escalation/policy_rule.json")
  parameters = file("policies/privilege_escalation/parameters.json")
}

resource "azurerm_policy_definition" "aks_privileged_containers_definition" {
  name         = "aks_privileged_containers_${var.env}"
  description  = "Kubernetes cluster should not allow privileged containers"
  policy_type  = "Custom"
  mode         = "Microsoft.Kubernetes.Data"
  display_name = "TEST AKS Privileged Containers ${var.env}"

  metadata = jsonencode({
    category = "Kubernetes"
    version = "1.0.0"
  })

  policy_rule = file("policies/privileged_containers/policy_rule.json")
  parameters = file("policies/privileged_containers/parameters.json")
}
#################
#HI-AKS-INFRA-config#
node_resource_group_name: '{{ resource_group_name }}-Node'
aks_vnet_name: '{{ project }}-{{ env }}-vNET'
aks_vnet_cidr: 10.0.0.0/16
aks_subnet_name: '{{ project }}-{{ env }}-Subnet'
aks_subnet_cidr: 10.0.0.0/17
aks_network_security_group_name: '{{ project }}-{{ env }}-NSG'
data_subscription_id: 
aks_to_peer_name: '{{ aks_vnet_name }}_to_Open-VPN'
peer_to_aks_name: Open-VPN_to_{{ aks_vnet_name }}
aks_peer_vnet_name: 
aks_peer_rg_name: 
aks_to_encoder_peer_name: '{{ aks_vnet_name }}_to_DMA2-DEV'
encoder_to_aks_peer_name: DMA2-DEV_to_{{ aks_vnet_name }}
aks_encoder_vnet_name: 
aks_encoder_rg_name: 
firewall_ip: 10.0.0.4
open_vpn_ip: 172.0.0.4
aks_agent_min_count: 1
aks_agent_max_count: 3
aks_agent_type: Standard_D4s_v3
aks_dns_prefix: test
aks_k8s_version: 1.34.8
aks_docker_bridge_cidr: 10.0.0.0/18
aks_dns_service_ip: 10.0.3.13
aks_service_cidr: 10.0.0.0/19
admin_group_id: 
provisioner_group_id: 
monitor_group_id: 
deployer_group_id: 
docker_repo_secret: test-docker-secret
nginx_chart_ver: 4.0.11
dragon_nginx_chart_ver: 4.7.2
nginx_replica_count: 2
storage_account_type: StorageV2
storage_account_tier: Standard
storage_account_replication_type: ZRS
ai_app_type: Node.JS
oms_agent_ver: 1.13
log_analytics_name: '{{ project }}-{{ env }}-Logs'
log_analytics_sku: PerGB2018
log_analytics_retention: 90
log_analytics_log_level: -CollectDebug
postgres_server_resource_group_name: PostgresDB
postgres_private_endpoint_name: '{{ project | lower }}-{{ env | lower }}_to_{{ postgres_server_name | lower }}'
connect_pg_private_endpoint_name: '{{ project | lower }}-{{ env | lower }}_to_{{ connect_pg_server_name | lower }}'
pg_storage_private_endpoint_name: '{{ project | lower }}-{{ env | lower }}_to_{{ postgres_storage_account | lower }}'
nginx_repository: oci://test.azurecr.io/helm
ingress_chart: ingress-nginx
ingress_namespace: kube-system
nginx_dragon_repository: https://kubernetes.github.io/ingress-nginx
nginx_dragon_chart: ingress-nginx
nginx_dragon_namespace: dragon
monitoring_namespace: monitoring
prometheus_repository: https://prometheus-community.github.io/helm-charts
prometheus_chart: prometheus
prometheus_chart_version: 29.27.1
grafana_repository: https://grafana.github.io/helm-charts
grafana_chart: alloy
grafana_chart_version: 1.0.0
monitor_storage_account_name: testdevops
monitor_storage_resource_group_name: Test-DevOps
loki_repository: https://grafana-community.github.io/helm-charts
loki_chart: loki
loki_chart_version: 18.13.5
monitor_storage_account_key: 