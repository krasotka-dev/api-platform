module "api-deploy" {
  source  = "fuchicorp/chart/helm"

  deployment_name        = "api-platform"
  deployment_environment = "${var.deployment_environment}"
  deployment_endpoint    = "${lookup(var.deployment_endpoint, "${var.deployment_environment}")}"
  deployment_path        = "api-platform"

  template_custom_vars  = {
    deployment_image    = "${var.deployment_image}"
  }
}
