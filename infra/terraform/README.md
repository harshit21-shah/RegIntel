# RegIntel Terraform

Infrastructure modules for staging and production AWS deployments.

## Layout

```
modules/
  network/     VPC, subnets, security groups
  database/    RDS Postgres
  queue/       SQS change-event queue + DLQ
  storage/     S3 document store
  secrets/     Secrets Manager placeholders
  compute/     ECS cluster, ECR, ALB, Fargate services
  monitoring/  CloudWatch alarms + SNS topics
environments/
  staging/
  production/
```

## Usage

```bash
cd infra/terraform/environments/staging
terraform init
terraform plan -var-file=staging.tfvars
terraform apply -var-file=staging.tfvars
```

Production applies require manual approval via the `deploy-prod` GitHub Actions workflow.

## Prerequisites

- AWS CLI configured with deploy role
- Remote state bucket (configure `backend "s3"` in each environment)
- Secrets values injected via CI — never commit real credentials

See [DEPLOYMENT.md](../../docs/DEPLOYMENT.md) for the full CI/CD topology.
