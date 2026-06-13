output "secret_arns" {
  value = merge(
    { for k, v in aws_secretsmanager_secret.app : k => v.arn },
    { database_url = aws_secretsmanager_secret.database_url.arn }
  )
}
