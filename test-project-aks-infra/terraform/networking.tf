resource "azurerm_virtual_network" "aks" {
  name                = var.aks_vnet_name
  resource_group_name = azurerm_resource_group.aks.name
  address_space       = [var.aks_vnet_cidr]
  location            = var.location

  tags = merge(var.tags, tomap({ "role" = "virtual_network" }))
  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_subnet" "aks" {
  name                 = var.aks_subnet_name
  resource_group_name  = azurerm_resource_group.aks.name
  virtual_network_name = azurerm_virtual_network.aks.name
  address_prefixes     = [var.aks_subnet_cidr]
  private_endpoint_network_policies = "Enabled"
  service_endpoints = [
    "Microsoft.Storage"
  ]

  depends_on = [
    azurerm_network_security_group.aks
  ]
}

resource "azurerm_network_security_group" "aks" {
  name                = var.aks_network_security_group_name
  location            = var.location
  resource_group_name = azurerm_resource_group.aks.name

  security_rule {
    access                     = "Allow"
    direction                  = "Inbound"
    name                       = "Allow-ALL-from-Firewall"
    priority                   = 100
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.firewall_ip
    destination_address_prefix = "*"
  }

  security_rule {
    access                     = "Allow"
    direction                  = "Inbound"
    name                       = "Allow-ALL-from-OpenVPN"
    priority                   = 101
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.open_vpn_ip
    destination_address_prefix = "*"
  }

  security_rule {
    access                     = "Allow"
    direction                  = "Inbound"
    name                       = "Allow-ALL-from-${var.aks_subnet_name}"
    priority                   = 102
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.aks_subnet_cidr
    destination_address_prefix = "*"
  }

  tags = merge(var.tags, tomap({ "role" = "network_security_group" }))
  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_subnet_network_security_group_association" "sn-to-nsg" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks.id

  depends_on = [
    azurerm_network_security_group.aks,
    azurerm_subnet.aks
  ]
}
