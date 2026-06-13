output "queue_url" {
  value = aws_sqs_queue.change_events.url
}

output "queue_arn" {
  value = aws_sqs_queue.change_events.arn
}

output "queue_name" {
  value = aws_sqs_queue.change_events.name
}

output "dlq_arn" {
  value = aws_sqs_queue.change_events_dlq.arn
}
