variable "mysql_user" {
  default = "webplaformbbuser"
}

variable "mysql_database" {
  default = "webplatformdb"
}

variable "mysql_password" {
  default = "lhMi4XrcnejG6mlcTglxt"
}

variable "mysql_root_password" {
  default = "lhMi4XrcnejG6mlcTglxt"
}


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
    dev  = "dev.api.academy.fuchicorp.com"
    qa   = "qa.api.academy.fuchicorp.com"
    prod = "api.academy.fuchicorp.com"
  }
}
