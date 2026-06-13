data "aws_region" "current" {}

resource "aws_iam_role" "ingestion_lambda" {
  name = "${var.project}-${var.environment}-ingestion-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.ingestion_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "ingestion" {
  function_name = "${var.project}-${var.environment}-ingestion"
  role          = aws_iam_role.ingestion_lambda.arn
  package_type  = "Image"
  image_uri     = var.ingestion_image
  timeout       = 900
  memory_size   = 1024

  environment {
    variables = {
      INGEST_SOURCES = "ecfr,federal_register,ca_food_code,sec_edgar"
      INGEST_PARTS   = "1,101"
    }
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_rule" "ingestion_schedule" {
  name                = "${var.project}-${var.environment}-ingestion-daily"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "ingestion" {
  rule      = aws_cloudwatch_event_rule.ingestion_schedule.name
  target_id = "ingestion-lambda"
  arn       = aws_lambda_function.ingestion.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ingestion_schedule.arn
}
