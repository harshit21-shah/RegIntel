locals {
  secret_names = [
    "anthropic-api-key",
    "openai-api-key",
    "voyage-api-key",
    "neo4j-password",
    "qdrant-api-key",
    "jwt-secret-key",
    "cohere-api-key",
    "slack-webhook-url",
  ]
}

resource "aws_secretsmanager_secret" "app" {
  for_each = toset(local.secret_names)

  name                    = "${var.project}/${var.environment}/${each.key}"
  recovery_window_in_days = var.environment == "production" ? 30 : 0

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "database_url" {
  name                    = "${var.project}/${var.environment}/database-url"
  recovery_window_in_days = var.environment == "production" ? 30 : 0

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = var.database_url
}
