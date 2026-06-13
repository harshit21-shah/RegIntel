variable "project" { type = string }
variable "environment" { type = string }
variable "database_url" {
  type      = string
  sensitive = true
}
