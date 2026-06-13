resource "aws_sqs_queue" "change_events_dlq" {
  name                      = "${var.project}-${var.environment}-change-events-dlq"
  message_retention_seconds = 1209600

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "change_events" {
  name                       = "${var.project}-${var.environment}-change-events"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 345600
  receive_wait_time_seconds  = 20

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.change_events_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}
