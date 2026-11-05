resource "azurerm_application_gateway" "app_gateway" {
  name                = var.ag_name
  resource_group_name = azurerm_resource_group.sre.name
  location            = azurerm_resource_group.sre.location
  enable_http2 = true

  tags = merge(var.tags, tomap({"role" = "app_gateway"} ))
  lifecycle {
    ignore_changes = [tags,]
  }

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
  }

  autoscale_configuration {
    min_capacity = 0
    max_capacity = 100
  }

  gateway_ip_configuration {
    name      = "ag_ip_config"
    subnet_id = azurerm_subnet.app_gateway.id
  }

  frontend_port {
    name = "ag_http_port"
    port = 80
  }

  frontend_port {
    name = "ag_https_port"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "ag_public_ip"
    public_ip_address_id = azurerm_public_ip.app_gateway.id
  }

  frontend_ip_configuration {
    name = "ag_private_ip"
    subnet_id = azurerm_subnet.app_gateway.id
    private_ip_address_allocation = "Static"
    private_ip_address = var.ag_private_ip
  }

  ##################
  # SSL Certificates
  ##################

  ssl_certificate {
    name = var.test_pricing_cert_name
    data = filebase64("${var.test_pricing_cert_name}.pfx")
    password = ""
  }

  ssl_certificate {
    name = var.test_uat_cert_name
    data = filebase64("${var.test_uat_cert_name}.pfx")
    password = ""
  }

  ssl_policy {
    min_protocol_version = "TLSv1_2"
    policy_type = "Predefined"
    policy_name = "AppGwSslPolicy20170401S"
  }

  #######################
  # Backend Address Pools
  #######################

  backend_address_pool {
    name = "prod_backend_pool"
    ip_addresses = [var.prod_aks_load_balancer_ip]
  }

  backend_address_pool {
    name = "uat_backend_pool"
    ip_addresses = [var.uat_aks_load_balancer_ip]
  }

  backend_address_pool {
    name = "cm_backend_pool"
    ip_addresses = [var.cm_aks_load_balancer_ip]
  }

  backend_address_pool {
    name = "ca_backend_pool"
    ip_addresses = [var.ca_aks_load_balancer_ip]
  }

  backend_address_pool {
    name = "staging_backend_pool"
    ip_addresses = [var.staging_aks_load_balancer_ip]
  }

  backend_address_pool {
    name = "cit_backend_pool"
    ip_addresses = [var.cit_aks_load_balancer_ip]
  }

  backend_address_pool {
    name = "aie_backend_pool"
    ip_addresses = [var.aie_aks_load_balancer_ip]
  }

 ############
  # HTTP Settings
  ############

  //TODO uncomment test.testpricing.com when ready
  # Portal HTTP settings

//  backend_http_settings {
//    name                  = "portal"
//    cookie_based_affinity = "Disabled"
//    port                  = 80
//    protocol              = "HTTP"
//    request_timeout       = var.backend_http_request_timeout
//    pick_host_name_from_backend_address = false
//    host_name = "test.testpricing.com"
//  }
//
//  backend_http_settings {
//    name                  = "portal_https"
//    cookie_based_affinity = "Disabled"
//    port                  = 443
//    protocol              = "HTTPS"
//    request_timeout       = var.backend_http_request_timeout
//    pick_host_name_from_backend_address = false
//    host_name = "test.testpricing.com"
//  }

  //TODO uncomment test-uat.testpricing.com when ready
  # Portal UAT HTTP settings

//  backend_http_settings {
//    name                  = "portal_uat"
//    cookie_based_affinity = "Disabled"
//    port                  = 80
//    protocol              = "HTTP"
//    request_timeout       = var.backend_http_request_timeout
//    pick_host_name_from_backend_address = false
//    host_name = "test-uat.testdpricing.com"
//  }
//
//  backend_http_settings {
//    name                  = "portal_uat_https"
//    cookie_based_affinity = "Disabled"
//    port                  = 443
//    protocol              = "HTTPS"
//    request_timeout       = var.backend_http_request_timeout
//    pick_host_name_from_backend_address = false
//    host_name = "test-uat.testdpricing.com"
//  }

###############################
  # Cr test PROD HTTP settings
  ###############################

  backend_http_settings {
    name                  = "cr_test"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "HTTP"
    request_timeout       = var.backend_http_request_timeout
    pick_host_name_from_backend_address = false
    host_name = "cr-test.testpricing.com"
  }

  backend_http_settings {
    name                  = "cr_test_https"
    cookie_based_affinity = "Disabled"
    port                  = 443
    protocol              = "HTTPS"
    request_timeout       = var.backend_http_request_timeout
    pick_host_name_from_backend_address = false
    host_name = "cr-test.testpricing.com"
  }

  ############
  # Request Routing Rules
  ############

  //TODO uncomment portal (prod & uat) rules when ready
  # Portal Rules

//  request_routing_rule {
//    name                       = "portal"
//    rule_type                  = "Basic"
//    http_listener_name         = "portal"
//    redirect_configuration_name = "portal_http_301_to_https"
//  }
//
//  redirect_configuration {
//    name          = "portal_http_301_to_https"
//    redirect_type = "Permanent"
//    target_listener_name = "portal_https"
//    include_path  = false
//    include_query_string = false
//  }
//
//  request_routing_rule {
//    name                       = "portal_https"
//    rule_type                  = "Basic"
//    http_listener_name         = "portal_https"
//    backend_address_pool_name  = "prod_backend_pool"
//    backend_http_settings_name = "portal_https"
//  }

###########################
  # Cr test PROD Rules
  ###########################
  request_routing_rule {
    name                       = "cr_test"
    rule_type                  = "Basic"
    http_listener_name         = "cr_test"
    redirect_configuration_name = "cr_test_301_to_https"
  }

  redirect_configuration {
    name          = "cr_test_301_to_https"
    redirect_type = "Permanent"
    target_listener_name = "cr_test_https"
    include_path  = false
    include_query_string = false
  }

  request_routing_rule {
    name                       = "cr_test_https"
    rule_type                  = "Basic"
    http_listener_name         = "cr_test_https"
    backend_address_pool_name  = "prod_backend_pool"
    backend_http_settings_name = "cr_test_https"
  }

  ############
  # WAF Configuration
  ############

  waf_configuration {
    enabled                  = true
    firewall_mode            = var.ag_waf_fw_mode
    rule_set_type            = "OWASP"
    rule_set_version         = var.ag_rule_set_ver
    request_body_check  = true
    max_request_body_size_kb = 128
    file_upload_limit_mb   = 100
  }
}
