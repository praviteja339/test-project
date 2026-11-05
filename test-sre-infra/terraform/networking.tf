resource "azurerm_virtual_network" "sre" {
  name                = var.sre_vnet_name
  resource_group_name = azurerm_resource_group.sre.name
  location            = azurerm_resource_group.sre.location
  address_space       = [ var.sre_vnet_cidr ]
}

resource "azurerm_subnet" "app_gateway" {
  name                 = var.ag_subnet_name
  resource_group_name  = azurerm_resource_group.sre.name
  virtual_network_name = azurerm_virtual_network.sre.name
  address_prefixes     = [ var.ag_subnet_cidr ]
}

resource "azurerm_subnet" "firewall" {
  name                 = "AzureFirewallSubnet"
  resource_group_name  = azurerm_resource_group.sre.name
  virtual_network_name = azurerm_virtual_network.sre.name
  address_prefixes     = [ var.firewall_subnet_cidr ]
}

resource "azurerm_public_ip" "app_gateway" {
  name                = "TEST-AG-IP"
  resource_group_name = azurerm_resource_group.sre.name
  location            = azurerm_resource_group.sre.location
  allocation_method   = "Static"
  sku                 = "Standard"
  availability_zone   = "Zone-Redundant"
}

resource "azurerm_public_ip" "firewall" {
  name                = "TEST-FW-IP"
  resource_group_name = azurerm_resource_group.sre.name
  location            = azurerm_resource_group.sre.location
  allocation_method   = "Static"
  sku                 = "Standard"
  availability_zone   = "Zone-Redundant"
}

resource "azurerm_network_security_group" "sre" {
  name = var.sre_network_security_group_name
  location = var.location
  resource_group_name = azurerm_resource_group.sre.name

  security_rule {
    name = "Allow-ALL-from-Firewall"
    priority = 100
    access = "Allow"
    direction = "Inbound"
    protocol = "*"
    source_port_range = "*"
    destination_port_range = "*"
    source_address_prefix = var.firewall_ip
    destination_address_prefix = "*"
  }

  security_rule {
    name = "Allow-ALL-from-${var.ag_name}"
    priority = 102
    access = "Allow"
    direction = "Inbound"
    protocol = "*"
    source_port_range = "*"
    destination_port_range = "*"
    source_address_prefix = var.ag_subnet_cidr
    destination_address_prefix = "*"
  }

  security_rule {
    name = "AzureGatewayManager"
    priority = 103
    direction = "Inbound"
    access = "Allow"
    protocol = "Tcp"
    source_port_range = "*"
    destination_port_range = "65200-65535"
    source_address_prefix = "GatewayManager"
    destination_address_prefix = "*"
  }

  tags = merge(var.tags, tomap({"role" = "network_security_group"} ))
  lifecycle {
    ignore_changes = [tags,]
  }
}

resource "azurerm_subnet_network_security_group_association" "sn-to-nsg" {
  subnet_id  = azurerm_subnet.app_gateway.id
  network_security_group_id = azurerm_network_security_group.sre.id

  depends_on = [
    azurerm_network_security_group.sre,
    azurerm_subnet.app_gateway
  ]
}
