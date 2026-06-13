variable "project" { type = string }
variable "environment" { type = string }
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "ingestion_image" { type = string }
