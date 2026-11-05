resource "azurerm_resource_group" "sre" {
  name = var.resource_group_name
  location = var.location

  tags = merge( var.tags, tomap( {"role" = "rg"} ))

  lifecycle {
    prevent_destroy = true
    ignore_changes = [tags,]
  }
}

output "resource_group_id" {
  value = azurerm_resource_group.sre.id
}

output "resource_group" {
  value = azurerm_resource_group.sre.name
}
