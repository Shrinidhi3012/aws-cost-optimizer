# Scans table - stores EC2 scan results
resource "aws_dynamodb_table" "scans" {
  name         = "CostOptimizerScans"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "scan_date"
  range_key    = "scan_id"

  attribute {
    name = "scan_date"
    type = "S"
  }

  attribute {
    name = "scan_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = false
  }

  tags = {
    Name        = "Cost Optimizer Scans"
    Description = "Stores EC2 idle instance scan results"
  }
}

# Cost analysis history table
resource "aws_dynamodb_table" "cost_history" {
  name         = "CostAnalysisHistory"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "analysis_date"

  attribute {
    name = "analysis_date"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = false
  }

  tags = {
    Name        = "Cost Analysis History"
    Description = "Stores daily cost analysis results"
  }
}

# Advanced resource scans table
resource "aws_dynamodb_table" "advanced_scans" {
  name         = "AdvancedResourceScans"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "scan_date"
  range_key    = "scan_id"

  attribute {
    name = "scan_date"
    type = "S"
  }

  attribute {
    name = "scan_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = false
  }

  tags = {
    Name        = "Advanced Resource Scans"
    Description = "Stores multi-resource scan results (EBS, RDS, S3, Lambda)"
  }
}