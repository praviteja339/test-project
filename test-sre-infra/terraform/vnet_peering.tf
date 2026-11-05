############
# Prod vNET Peering
############

data "azurerm_virtual_network" "prod_aks_peer" {
  name = "TEST-AKS-Prod-vNET"
  resource_group_name = "TEST-AKS-Prod"
  provider = azurerm.data
}

resource "azurerm_virtual_network_peering" "sre_to_prod_peer" {
  name                      = var.sre_to_prod_peer_name
  resource_group_name       = azurerm_resource_group.sre.name
  virtual_network_name      = azurerm_virtual_network.sre.name
  remote_virtual_network_id = data.azurerm_virtual_network.prod_aks_peer.id
  allow_forwarded_traffic   = false
}

resource "azurerm_virtual_network_peering" "prod_peer_to_sre" {
  name                      = var.prod_peer_to_sre_name
  resource_group_name       = data.azurerm_virtual_network.prod_aks_peer.resource_group_name
  virtual_network_name      = data.azurerm_virtual_network.prod_aks_peer.name
  remote_virtual_network_id = azurerm_virtual_network.sre.id
  allow_forwarded_traffic   = false
}

############
# UAT vNET Peering
############

data "azurerm_virtual_network" "uat_aks_peer" {
  name = "TEST-AKS-UAT-vNET"
  resource_group_name = "TEST-AKS-UAT"
  provider = azurerm.data
}

resource "azurerm_virtual_network_peering" "sre_to_uat_peer" {
  name                      = var.sre_to_uat_peer_name
  resource_group_name       = azurerm_resource_group.sre.name
  virtual_network_name      = azurerm_virtual_network.sre.name
  remote_virtual_network_id = data.azurerm_virtual_network.uat_aks_peer.id
  allow_forwarded_traffic   = false
}

resource "azurerm_virtual_network_peering" "uat_peer_to_sre" {
  name                      = var.uat_peer_to_sre_name
  resource_group_name       = data.azurerm_virtual_network.uat_aks_peer.resource_group_name
  virtual_network_name      = data.azurerm_virtual_network.uat_aks_peer.name
  remote_virtual_network_id = azurerm_virtual_network.sre.id
  allow_forwarded_traffic   = false
}


##################
### CA vNET Peering
##################
data "azurerm_virtual_network" "hi_aks_peer" {
  name = "TEST-AKS-vNET"
  resource_group_name = "TEST-AKS"
  provider = azurerm.data
}

resource "azurerm_virtual_network_peering" "sre_to_hi_peer" {
  name                      = var.sre_to_hi_peer_name
  resource_group_name       = azurerm_resource_group.sre.name
  virtual_network_name      = azurerm_virtual_network.sre.name
  remote_virtual_network_id = data.azurerm_virtual_network.hi_aks_peer.id
  allow_forwarded_traffic   = false
}

resource "azurerm_virtual_network_peering" "hi_peer_to_sre" {
  name                      = var.chi_peer_to_sre_name
  resource_group_name       = data.azurerm_virtual_network.hi_aks_peer.resource_group_name
  virtual_network_name      = data.azurerm_virtual_network.hi_aks_peer.name
  remote_virtual_network_id = azurerm_virtual_network.sre.id
  allow_forwarded_traffic   = false
}

##################
### Staging vNET Peering
##################
#data "azurerm_virtual_network" "staging_aks_peer" {
#  name = "TEST-AKS-Staging-vNET"
#  resource_group_name = "TEST-AKS-Staging"
#  provider = azurerm.data
#}
#
#resource "azurerm_virtual_network_peering" "sre_to_staging_peer" {
#  name                      = var.sre_to_staging_peer_name
#  resource_group_name       = azurerm_resource_group.sre.name
#  virtual_network_name      = azurerm_virtual_network.sre.name
#  remote_virtual_network_id = data.azurerm_virtual_network.staging_aks_peer.id
#  allow_forwarded_traffic   = false
#}
#
#resource "azurerm_virtual_network_peering" "staging_peer_to_sre" {
#  name                      = var.staging_peer_to_sre_name
#  resource_group_name       = data.azurerm_virtual_network.staging_aks_peer.resource_group_name
#  virtual_network_name      = data.azurerm_virtual_network.staging_aks_peer.name
#  remote_virtual_network_id = azurerm_virtual_network.sre.id
#  allow_forwarded_traffic   = false
#}
