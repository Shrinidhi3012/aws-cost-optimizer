variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "cost-optimizer"
}

variable "scanner_schedule" {
  description = "Cron expression for EC2 scanner (every 6 hours)"
  type        = string
  default     = "cron(0 */6 * * ? *)"
}

variable "cost_analyzer_schedule" {
  description = "Cron expression for cost analyzer (daily at midnight)"
  type        = string
  default     = "cron(0 0 * * ? *)"
}

variable "advanced_scanner_schedule" {
  description = "Cron expression for advanced scanner (daily at 1 AM)"
  type        = string
  default     = "cron(0 1 * * ? *)"
}

variable "idle_cpu_threshold" {
  description = "CPU threshold for idle detection (%)"
  type        = number
  default     = 5
}