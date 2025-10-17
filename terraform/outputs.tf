output "dynamodb_tables" {
  description = "DynamoDB table names"
  value = {
    scans_table          = aws_dynamodb_table.scans.name
    cost_history_table   = aws_dynamodb_table.cost_history.name
    advanced_scans_table = aws_dynamodb_table.advanced_scans.name
  }
}

output "lambda_functions" {
  description = "Lambda function details"
  value = {
    ec2_scanner = {
      name = aws_lambda_function.ec2_scanner.function_name
      arn  = aws_lambda_function.ec2_scanner.arn
    }
    cost_analyzer = {
      name = aws_lambda_function.cost_analyzer.function_name
      arn  = aws_lambda_function.cost_analyzer.arn
    }
    advanced_scanner = {
      name = aws_lambda_function.advanced_scanner.function_name
      arn  = aws_lambda_function.advanced_scanner.arn
    }
  }
}

output "iam_role" {
  description = "IAM role for Lambda functions"
  value = {
    name = aws_iam_role.lambda_role.name
    arn  = aws_iam_role.lambda_role.arn
  }
}

output "eventbridge_schedules" {
  description = "EventBridge schedule expressions"
  value = {
    ec2_scanner      = aws_cloudwatch_event_rule.ec2_scanner_schedule.schedule_expression
    cost_analyzer    = aws_cloudwatch_event_rule.cost_analyzer_schedule.schedule_expression
    advanced_scanner = aws_cloudwatch_event_rule.advanced_scanner_schedule.schedule_expression
  }
}

output "deployment_summary" {
  description = "Deployment summary"
  value = <<-EOT
  
  ═══════════════════════════════════════════════════════════
  AWS Cost Optimizer - Infrastructure Deployed Successfully!
  ═══════════════════════════════════════════════════════════
  
  📊 DynamoDB Tables:
     • ${aws_dynamodb_table.scans.name}
     • ${aws_dynamodb_table.cost_history.name}
     • ${aws_dynamodb_table.advanced_scans.name}
  
  🔧 Lambda Functions:
     • ${aws_lambda_function.ec2_scanner.function_name} (Every 6 hours)
     • ${aws_lambda_function.cost_analyzer.function_name} (Daily at midnight)
     • ${aws_lambda_function.advanced_scanner.function_name} (Daily at 1 AM)
  
  📅 Schedules:
     • EC2 Scanner: ${var.scanner_schedule}
     • Cost Analyzer: ${var.cost_analyzer_schedule}
     • Advanced Scanner: ${var.advanced_scanner_schedule}
  
  🔐 IAM Role: ${aws_iam_role.lambda_role.name}
  
  🌍 Region: ${data.aws_region.current.name}
  👤 Account: ${data.aws_caller_identity.current.account_id}
  
  ═══════════════════════════════════════════════════════════
  EOT
}