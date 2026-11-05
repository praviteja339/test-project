#Global Variables
variable "tags" {
    type = map(string)
    default = {}
}

variable "env" {}
variable "location" {}
variable "country" {}
variable "region" {}
variable "subscription_id" {}
variable "service_principal_id" {}
variable "service_principal_secret" {}
variable "tenant_id" {}
variable "resource_group_name" {}

#SRE Network Variables
variable "sre_vnet_name" {}
variable "sre_vnet_cidr" {}
variable "ag_name" {}
variable "ag_waf_fw_mode" {}
variable "ag_rule_set_ver" {}
variable "backend_http_request_timeout" {}
variable "hi_backend_http_request_timeout" {}
variable "sre_to_ca_peer_name" {}
variable "sre_to_prod_peer_name" {}
variable "sre_to_uat_peer_name" {}
variable "sre_to_staging_peer_name" {}
variable "prod_peer_to_sre_name" {}
variable "uat_peer_to_sre_name" {}
variable "hi_peer_to_sre_name" {}
variable "staging_peer_to_sre_name" {}
variable "query_central_ca_cert_name" {}
variable "cr_test_uat_cert_name" {}
variable "portal_uat_cert_name" {}

#Application Gateway Variables
variable "ag_private_ip" {}
variable "ag_subnet_name" {}
variable "ag_subnet_cidr" {}
variable "prod_aks_load_balancer_ip" {}
variable "uat_aks_load_balancer_ip" {}
variable "hi_aks_load_balancer_ip" {}
variable "test_aks_load_balancer_ip" {}
variable "staging_aks_load_balancer_ip" {}
variable "hihi_aks_load_balancer_ip" {}
variable "helo_aks_load_balancer_ip" {}

#Firewall Variables
variable "firewall_name" {}
variable "firewall_subnet_cidr" {}
variable "nat_rule_collection_name" {}

#Network Security Group Variables
variable "firewall_ip" {}
variable "sre_network_security_group_name" {}
