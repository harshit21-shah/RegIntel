variable "project" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "alb_security_group_id" { type = string }
variable "ecs_security_group_id" { type = string }
variable "api_image" { type = string }
variable "worker_image" { type = string }
variable "api_desired_count" { type = number }
variable "worker_desired_count" { type = number }
variable "sqs_queue_arn" { type = string }
variable "documents_bucket_arn" { type = string }
variable "secret_arns" { type = map(string) }
variable "database_url" {
  type      = string
  sensitive = true
}
variable "sqs_queue_url" { type = string }
variable "documents_bucket_name" { type = string }
variable "neo4j_uri" { type = string }
variable "qdrant_url" { type = string }
variable "redis_url" { type = string }
variable "app_base_url" { type = string }
