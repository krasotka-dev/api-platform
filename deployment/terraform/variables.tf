variable "name" {
  default = "api-webplatform"
}
variable "chart" {
    default = "./api-webplatform"

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
    dev  = "dev.api-platforms.fuchicorp.com"
    qa   = "qa.api-platforms.fuchicorp.com"
    prod = "api-platforms.fuchicorp.com"
  }
}
