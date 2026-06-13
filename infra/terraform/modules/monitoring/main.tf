resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.environment}-alerts"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_sns_topic_subscription" "slack" {
  count     = var.slack_webhook_url != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "https"
  endpoint  = var.slack_webhook_url
}

resource "aws_cloudwatch_metric_alarm" "sqs_backlog" {
  alarm_name          = "${var.project}-${var.environment}-sqs-backlog"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Average"
  threshold           = 100
  alarm_description   = "Change-event queue backlog exceeds threshold"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    QueueName = var.sqs_queue_name
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "${var.project}-${var.environment}-rds-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_id
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_api_running" {
  alarm_name          = "${var.project}-${var.environment}-api-running-tasks"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "API service has fewer than 1 running task"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "breaching"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.api_service_name
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_worker_running" {
  count               = var.worker_service_name != "" ? 1 : 0
  alarm_name          = "${var.project}-${var.environment}-worker-running-tasks"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Worker service has fewer than 1 running task"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "breaching"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.worker_service_name
  }
}
