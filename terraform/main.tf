# Terraform for the bedrock-agentic-demo: least-privilege Bedrock role.

# Apply-safe: does NOT create a model; it only prepares IAM for Bedrock access.
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5"
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

# Role the app runs with — scoped to InvokeModel on the demo model only.
resource "aws_iam_role" "bedrock_agent_demo" {
  name = "bedrock-agentic-demo-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" } # swap for your runtime (ECS task role, lambda)
      Action    = "sts:AssumeRole"
    }]
  })
}

# Least privilege: invoke the demo model, nothing else.
resource "aws_iam_policy" "bedrock_invoke" {
  name        = "bedrock-agentic-demo-invoke"
  description = "Minimal Bedrock invoke permission for the agentic demo."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["bedrock:InvokeModel"]
      Resource = "arn:aws:bedrock:${var.region}:${data.aws_caller_identity.current.account_id}:model/anthropic.claude-3-5-sonnet-20240620-v1:0"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_invoke_attach" {
  role       = aws_iam_role.bedrock_agent_demo.name
  policy_arn = aws_iam_policy.bedrock_invoke.arn
}
