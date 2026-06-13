resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-${var.environment}-db"
  subnet_ids = var.private_subnet_ids

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_db_instance" "main" {
  identifier              = "${var.project}-${var.environment}-postgres"
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage_gb
  storage_encrypted       = true
  db_name                 = var.db_name
  username                = var.db_username
  password                = random_password.db.result
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [var.security_group_id]
  skip_final_snapshot     = var.environment != "production"
  backup_retention_period = var.environment == "production" ? 7 : 1
  multi_az                = var.environment == "production"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}
