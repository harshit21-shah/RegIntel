variable "project" { type = string }
variable "environment" { type = string }
variable "sqs_queue_name" { type = string }
variable "rds_instance_id" { type = string }
variable "ecs_cluster_name" { type = string }
variable "worker_service_name" {
  type    = string
  default = ""
}
variable "alert_email" { type = string }
variable "slack_webhook_url" {
  type    = string
  default = ""
}
