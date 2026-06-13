terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # backend "s3" {
  #   bucket = "regintel-terraform-state"
  #   key    = "production/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "regintel"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "alert_email" {
  type    = string
  default = ""
}

variable "slack_webhook_url" {
  type    = string
  default = ""
}

variable "api_image" {
  type    = string
  default = "regintel/api:latest"
}

variable "worker_image" {
  type    = string
  default = "regintel/agent-worker:latest"
}

module "network" {
  source      = "../../modules/network"
  project     = "regintel"
  environment = "production"
}

module "database" {
  source               = "../../modules/database"
  project              = "regintel"
  environment          = "production"
  private_subnet_ids   = module.network.private_subnet_ids
  security_group_id    = module.network.rds_security_group_id
  instance_class       = "db.t4g.small"
  allocated_storage_gb = 50
  db_name              = "regintel"
  db_username          = "regintel"
}

module "queue" {
  source      = "../../modules/queue"
  project     = "regintel"
  environment = "production"
}

module "storage" {
  source      = "../../modules/storage"
  project     = "regintel"
  environment = "production"
}

module "secrets" {
  source       = "../../modules/secrets"
  project      = "regintel"
  environment  = "production"
  database_url = module.database.connection_string
}

module "compute" {
  source                  = "../../modules/compute"
  project                 = "regintel"
  environment             = "production"
  vpc_id                  = module.network.vpc_id
  public_subnet_ids       = module.network.public_subnet_ids
  private_subnet_ids      = module.network.private_subnet_ids
  alb_security_group_id   = module.network.alb_security_group_id
  ecs_security_group_id   = module.network.ecs_security_group_id
  api_image               = var.api_image
  worker_image            = var.worker_image
  api_desired_count       = 2
  worker_desired_count    = 2
  sqs_queue_arn           = module.queue.queue_arn
  sqs_queue_url           = module.queue.queue_url
  documents_bucket_arn    = module.storage.documents_bucket_arn
  secret_arns             = module.secrets.secret_arns
  database_url            = module.database.connection_string
}

module "monitoring" {
  source            = "../../modules/monitoring"
  project           = "regintel"
  environment       = "production"
  sqs_queue_name    = module.queue.queue_name
  rds_instance_id   = module.database.instance_id
  ecs_cluster_name  = module.compute.cluster_name
  api_service_name  = module.compute.api_service_name
  alert_email       = var.alert_email
  slack_webhook_url = var.slack_webhook_url
}

module "waf" {
  source      = "../../modules/waf"
  project     = "regintel"
  environment = "production"
  alb_arn     = module.compute.alb_arn
}

output "alb_url" {
  value = "http://${module.compute.alb_dns_name}"
}

output "ecr_repositories" {
  value = {
    api       = module.compute.ecr_api_repository_url
    worker    = module.compute.ecr_worker_repository_url
    ingestion = module.compute.ecr_ingestion_repository_url
  }
}

output "sqs_queue_url" {
  value = module.queue.queue_url
}

output "documents_bucket" {
  value = module.storage.documents_bucket_name
}

output "migrate_task_definition_arn" {
  value = module.compute.migrate_task_definition_arn
}
