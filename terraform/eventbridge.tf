# EventBridge rule for EC2 Scanner (every 6 hours)
resource "aws_cloudwatch_event_rule" "ec2_scanner_schedule" {
  name                = "cost-optimizer-ec2-scanner-schedule"
  description         = "Triggers EC2 idle scanner every 6 hours"
  schedule_expression = var.scanner_schedule

  tags = {
    Name = "EC2 Scanner Schedule"
  }
}

resource "aws_cloudwatch_event_target" "ec2_scanner_target" {
  rule      = aws_cloudwatch_event_rule.ec2_scanner_schedule.name
  target_id = "EC2ScannerLambda"
  arn       = aws_lambda_function.ec2_scanner.arn
}

resource "aws_lambda_permission" "allow_eventbridge_ec2_scanner" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_scanner.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_scanner_schedule.arn
}

# EventBridge rule for Cost Analyzer (daily at midnight)
resource "aws_cloudwatch_event_rule" "cost_analyzer_schedule" {
  name                = "cost-optimizer-cost-analyzer-schedule"
  description         = "Triggers cost analyzer daily at midnight UTC"
  schedule_expression = var.cost_analyzer_schedule

  tags = {
    Name = "Cost Analyzer Schedule"
  }
}

resource "aws_cloudwatch_event_target" "cost_analyzer_target" {
  rule      = aws_cloudwatch_event_rule.cost_analyzer_schedule.name
  target_id = "CostAnalyzerLambda"
  arn       = aws_lambda_function.cost_analyzer.arn
}

resource "aws_lambda_permission" "allow_eventbridge_cost_analyzer" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_analyzer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cost_analyzer_schedule.arn
}

# EventBridge rule for Advanced Scanner (daily at 1 AM)
resource "aws_cloudwatch_event_rule" "advanced_scanner_schedule" {
  name                = "cost-optimizer-advanced-scanner-schedule"
  description         = "Triggers advanced resource scanner daily at 1 AM UTC"
  schedule_expression = var.advanced_scanner_schedule

  tags = {
    Name = "Advanced Scanner Schedule"
  }
}

resource "aws_cloudwatch_event_target" "advanced_scanner_target" {
  rule      = aws_cloudwatch_event_rule.advanced_scanner_schedule.name
  target_id = "AdvancedScannerLambda"
  arn       = aws_lambda_function.advanced_scanner.arn
}

resource "aws_lambda_permission" "allow_eventbridge_advanced_scanner" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.advanced_scanner.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.advanced_scanner_schedule.arn
}