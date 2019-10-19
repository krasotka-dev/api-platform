
data "template_file" "api-platform_values" {
  template = "${file("./api-platform/template_values.yaml")}"
  vars = {
    docker_image = "${var.deployment_image}"
    deployment_endpoint = "${lookup(var.deployment_endpoint, "${var.deployment_environment}")}"

  }
}

resource "local_file" "api-platform_values_local_file" {
  content  = "${trimspace(data.template_file.api-platform_values.rendered)}"
  filename = "./chart-cloud/.cache/values.yaml"
}
resource "helm_release" "api-platform" {
  name       = "${var.name}"
  chart      = "${var.chart}"
  version    = "${var.version}"
  namespace = "${var.deployment_environment}"

 values = [
    "${data.template_file.api-platform_values.rendered}"
  ]
}