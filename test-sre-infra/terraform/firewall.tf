resource "azurerm_firewall" "sre" {
  name                = var.firewall_name
  location            = azurerm_resource_group.sre.location
  resource_group_name = azurerm_resource_group.sre.name

  ip_configuration {
    name                 = "ip_conf"
    subnet_id            = azurerm_subnet.firewall.id
    public_ip_address_id = azurerm_public_ip.firewall.id
  }
}

resource "azurerm_firewall_nat_rule_collection" "sre" {
  name                = var.nat_rule_collection_name
  azure_firewall_name = azurerm_firewall.sre.name
  resource_group_name = azurerm_resource_group.sre.name
  priority            = 100
  action              = "Dnat"

  rule {
    name = "http"
    source_addresses = ["*"]
    destination_ports = ["80"]
    destination_addresses = [azurerm_public_ip.firewall.ip_address]
    translated_port = 80
    translated_address = var.ag_private_ip
    protocols = [
      "TCP",
      "UDP",
    ]
  }

  rule {
    name = "https"
    source_addresses = ["*"]
    destination_ports = ["443"]
    destination_addresses = [azurerm_public_ip.firewall.ip_address]
    translated_port = 443
    translated_address = var.ag_private_ip
    protocols = [
      "TCP",
      "UDP",
    ]
  }
}
