# Data source for Lambda zip files (we'll reference existing deployment packages)
data "archive_file" "ec2_scanner" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/scanner"
  output_path = "${path.module}/builds/ec2-scanner.zip"
}

data "archive_file" "cost_analyzer" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/cost_analyzer"
  output_path = "${path.module}/builds/cost-analyzer.zip"
}

data "archive_file" "advanced_scanner" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/advanced_scanner"
  output_path = "${path.module}/builds/advanced-scanner.zip"
}

# Lambda function: EC2 Idle Scanner
resource "aws_lambda_function" "ec2_scanner" {
  filename         = data.archive_file.ec2_scanner.output_path
  function_name    = "EC2IdleScanner"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.ec2_scanner.output_base64sha256
  runtime          = "python3.13"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      IDLE_CPU_THRESHOLD = var.idle_cpu_threshold
      DYNAMODB_TABLE     = aws_dynamodb_table.scans.name
    }
  }

  tags = {
    Name        = "EC2 Idle Scanner"
    Description = "Scans EC2 instances for idle resources"
  }
}

# Lambda function: Cost Analyzer
resource "aws_lambda_function" "cost_analyzer" {
  filename         = data.archive_file.cost_analyzer.output_path
  function_name    = "CostAnalyzer"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.cost_analyzer.output_base64sha256
  runtime          = "python3.13"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      SCANS_TABLE = aws_dynamodb_table.scans.name
      COST_TABLE  = aws_dynamodb_table.cost_history.name
    }
  }

  tags = {
    Name        = "Cost Analyzer"
    Description = "Analyzes AWS costs using Cost Explorer"
  }
}

# Lambda function: Advanced Resource Scanner
resource "aws_lambda_function" "advanced_scanner" {
  filename         = data.archive_file.advanced_scanner.output_path
  function_name    = "AdvancedResourceScanner"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.advanced_scanner.output_base64sha256
  runtime          = "python3.13"
  timeout          = 300
  memory_size      = 512

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.advanced_scans.name
    }
  }

  tags = {
    Name        = "Advanced Resource Scanner"
    Description = "Scans EBS, RDS, S3, Lambda for cost optimization"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "ec2_scanner_logs" {
  name              = "/aws/lambda/${aws_lambda_function.ec2_scanner.function_name}"
  retention_in_days = 7

  tags = {
    Name = "EC2 Scanner Logs"
  }
}

resource "aws_cloudwatch_log_group" "cost_analyzer_logs" {
  name              = "/aws/lambda/${aws_lambda_function.cost_analyzer.function_name}"
  retention_in_days = 7

  tags = {
    Name = "Cost Analyzer Logs"
  }
}

resource "aws_cloudwatch_log_group" "advanced_scanner_logs" {
  name              = "/aws/lambda/${aws_lambda_function.advanced_scanner.function_name}"
  retention_in_days = 7

  tags = {
    Name = "Advanced Scanner Logs"
  }
}