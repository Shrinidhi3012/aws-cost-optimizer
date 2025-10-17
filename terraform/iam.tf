# Lambda execution role
resource "aws_iam_role" "lambda_role" {
  name = "CostOptimizerLambdaRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "Cost Optimizer Lambda Role"
  }
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom policy for cost optimizer permissions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "CostOptimizerPolicy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:DescribeImages",
          "rds:DescribeDBInstances",
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation",
          "lambda:ListFunctions",
          "cloudwatch:GetMetricStatistics",
          "ce:GetCostAndUsage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem"
        ]
        Resource = [
          aws_dynamodb_table.scans.arn,
          aws_dynamodb_table.cost_history.arn,
          aws_dynamodb_table.advanced_scans.arn
        ]
      }
    ]
  })
}