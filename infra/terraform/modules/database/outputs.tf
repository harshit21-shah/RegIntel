output "endpoint" {
  value = aws_db_instance.main.address
}

output "instance_id" {
  value = aws_db_instance.main.identifier
}

output "port" {
  value = aws_db_instance.main.port
}

output "database_name" {
  value = aws_db_instance.main.db_name
}

output "username" {
  value = aws_db_instance.main.username
}

output "password" {
  value     = random_password.db.result
  sensitive = true
}

output "connection_string" {
  value     = "postgresql+asyncpg://${aws_db_instance.main.username}:${random_password.db.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
  sensitive = true
}
