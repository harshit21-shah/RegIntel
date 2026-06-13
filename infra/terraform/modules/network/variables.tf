variable "project" {
  type        = string
  description = "Project name prefix for resources"
}

variable "environment" {
  type        = string
  description = "Deployment environment (staging, production)"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block"
  default     = "10.0.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of availability zones"
  default     = 2
}
