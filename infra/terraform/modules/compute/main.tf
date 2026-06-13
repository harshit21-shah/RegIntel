data "aws_region" "current" {}

resource "aws_ecs_cluster" "main" {
  name = "${var.project}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project}/${var.environment}/api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project}/${var.environment}/agent-worker"
  retention_in_days = 30
}

resource "aws_ecr_repository" "api" {
  name                 = "${var.project}/api"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment != "production"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "worker" {
  name                 = "${var.project}/agent-worker"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment != "production"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "ingestion" {
  name                 = "${var.project}/ingestion"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment != "production"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_lb" "main" {
  name               = "${var.project}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "api" {
  name        = "${var.project}-${var.environment}-api"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/healthz"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${var.project}-${var.environment}-ecs-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "api_task" {
  name               = "${var.project}-${var.environment}-api-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role" "worker_task" {
  name               = "${var.project}-${var.environment}-worker-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

data "aws_iam_policy_document" "worker_sqs" {
  statement {
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes", "sqs:ChangeMessageVisibility"]
    resources = [var.sqs_queue_arn]
  }
}

resource "aws_iam_role_policy" "worker_sqs" {
  name   = "sqs-consume"
  role   = aws_iam_role.worker_task.id
  policy = data.aws_iam_policy_document.worker_sqs.json
}

data "aws_iam_policy_document" "secrets_read" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = values(var.secret_arns)
  }
}

resource "aws_iam_role_policy" "api_secrets" {
  name   = "secrets-read"
  role   = aws_iam_role.api_task.id
  policy = data.aws_iam_policy_document.secrets_read.json
}

resource "aws_iam_role_policy" "worker_secrets" {
  name   = "secrets-read"
  role   = aws_iam_role.worker_task.id
  policy = data.aws_iam_policy_document.secrets_read.json
}

locals {
  api_env = [
    { name = "APP_ENV", value = var.environment },
    { name = "AWS_REGION", value = data.aws_region.current.name },
    { name = "SQS_QUEUE_URL", value = var.sqs_queue_url },
    { name = "S3_DOCUMENTS_BUCKET", value = var.documents_bucket_name },
    { name = "NEO4J_URI", value = var.neo4j_uri },
    { name = "NEO4J_USER", value = "neo4j" },
    { name = "QDRANT_URL", value = var.qdrant_url },
    { name = "QDRANT_COLLECTION", value = "clauses_v1" },
    { name = "REDIS_URL", value = var.redis_url },
    { name = "APP_BASE_URL", value = var.app_base_url },
    { name = "CORS_ORIGINS", value = var.app_base_url },
    { name = "RERANKER_PROVIDER", value = "bge" },
    { name = "ALERT_CHANNELS", value = "slack,email" },
  ]
  worker_env = local.api_env
  api_secrets = [
    { name = "DATABASE_URL", valueFrom = var.secret_arns["database_url"] },
    { name = "ANTHROPIC_API_KEY", valueFrom = var.secret_arns["anthropic-api-key"] },
    { name = "OPENAI_API_KEY", valueFrom = var.secret_arns["openai-api-key"] },
    { name = "VOYAGE_API_KEY", valueFrom = var.secret_arns["voyage-api-key"] },
    { name = "NEO4J_PASSWORD", valueFrom = var.secret_arns["neo4j-password"] },
    { name = "QDRANT_API_KEY", valueFrom = var.secret_arns["qdrant-api-key"] },
    { name = "JWT_SECRET_KEY", valueFrom = var.secret_arns["jwt-secret-key"] },
    { name = "COHERE_API_KEY", valueFrom = var.secret_arns["cohere-api-key"] },
    { name = "SLACK_WEBHOOK_URL", valueFrom = var.secret_arns["slack-webhook-url"] },
  ]
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project}-${var.environment}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.api_task.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = var.api_image
      essential = true
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment  = local.api_env
      secrets      = local.api_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "api"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/healthz || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project}-${var.environment}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.worker_task.arn

  container_definitions = jsonencode([
    {
      name      = "agent-worker"
      image     = var.worker_image
      essential = true
      environment = local.worker_env
      secrets     = local.api_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.worker.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "worker"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "migrate" {
  family                   = "${var.project}-${var.environment}-migrate"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.api_task.arn

  container_definitions = jsonencode([
    {
      name      = "migrate"
      image     = var.api_image
      essential = true
      command   = ["alembic", "-c", "services/api/alembic.ini", "upgrade", "head"]
      environment = [{ name = "APP_ENV", value = var.environment }]
      secrets = [{ name = "DATABASE_URL", valueFrom = var.secret_arns["database_url"] }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "migrate"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "api" {
  name            = "${var.project}-${var.environment}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}

resource "aws_ecs_service" "worker" {
  name            = "${var.project}-${var.environment}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }
}
