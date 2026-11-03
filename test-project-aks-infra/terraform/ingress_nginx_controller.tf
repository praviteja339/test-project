provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.k8s.kube_admin_config[0].host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.k8s.kube_admin_config[0].client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.k8s.kube_admin_config[0].client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.k8s.kube_admin_config[0].cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = azurerm_kubernetes_cluster.k8s.kube_admin_config[0].host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.k8s.kube_admin_config[0].client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.k8s.kube_admin_config[0].client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.k8s.kube_admin_config[0].cluster_ca_certificate)
  }
}

resource "helm_release" "nginx_ingress" {
  name             = "platform"
  namespace        = var.ingress_namespace
  repository       = var.nginx_repository
  chart            = var.ingress_chart
  version          = var.nginx_chart_ver

  set {
    name  = "controller.replicaCount"
    value = var.nginx_replica_count
  }

  set {
    name  = "controller.service.loadBalancerIP"
    value = var.aks_load_balancer_ip
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-load-balancer-internal"
    value = "true"
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-load-balancer-health-probe-request-path"
    value = "/healthz"
  }

  set {
    name  = "controller.ingressClassResource.name"
    value = var.aks_load_balancer_name
  }

  depends_on = [
    azurerm_kubernetes_cluster.k8s
  ]
}
