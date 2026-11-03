resource "azurerm_resource_group_policy_assignment" "aks_user_group_assignment" {
  name                 = azurerm_policy_definition.aks_user_group_assignment_definition.name
  description          = azurerm_policy_definition.aks_user_group_assignment_definition.description
  policy_definition_id = azurerm_policy_definition.aks_user_group_assignment_definition.id
  resource_group_id    = azurerm_resource_group.aks.id
  location             = azurerm_resource_group.aks.location
}

resource "azurerm_resource_group_policy_assignment" "aks_privilege_escalation_assignment" {
  name                 = azurerm_policy_definition.aks_privilege_escalation_definition.name
  description          = azurerm_policy_definition.aks_privilege_escalation_definition.description
  policy_definition_id = azurerm_policy_definition.aks_privilege_escalation_definition.id
  resource_group_id    = azurerm_resource_group.aks.id
  location             = azurerm_resource_group.aks.location
}

resource "azurerm_resource_group_policy_assignment" "aks_privileged_containers_assignment" {
  name                 = azurerm_policy_definition.aks_privileged_containers_definition.name
  description          = azurerm_policy_definition.aks_privileged_containers_definition.description
  policy_definition_id = azurerm_policy_definition.aks_privileged_containers_definition.id
  resource_group_id    = azurerm_resource_group.aks.id
  location             = azurerm_resource_group.aks.location
}
