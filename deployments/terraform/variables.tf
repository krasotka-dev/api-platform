variable "name" {
  default = "api-webplatform"
}
variable "chart" {
    default = "./api-platform"

}
variable "version" {
    default = "6.0.1"

}
variable "deployment_image" {
}


variable "deployment_environment" {
  default = "dev"
}

variable "deployment_endpoint" {
  type = "map"

  default = {
    dev  = "dev.api.fuchicorp.com"
    qa   = "qa.api.fuchicorp.com"
    prod = "api.fuchicorp.com"
  }
}
