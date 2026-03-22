terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region     = "us-east-1"
  access_key = "test"
  secret_key = "test"

  # Configuração para LocalStack
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    apigateway = "http://localhost:4566"
    dynamodb   = "http://localhost:4566"
    ecs        = "http://localhost:4566"
    iam        = "http://localhost:4566"
    lambda     = "http://localhost:4566"
    s3         = "http://localhost:4566"
    sqs        = "http://localhost:4566"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "example_bucket" {
  bucket = "exemplo-bucket-terraform"

  tags = {
    Name        = "Exemplo Bucket"
    Environment = "Dev"
  }
}

# DynamoDB Table
resource "aws_dynamodb_table" "example_table" {
  name           = "exemplo-dynamodb-table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  range_key      = "timestamp"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Name        = "Exemplo DynamoDB Table"
    Environment = "Dev"
  }
}

# SQS Queue
resource "aws_sqs_queue" "example_queue" {
  name                      = "exemplo-sqs-queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10

  tags = {
    Name        = "Exemplo SQS Queue"
    Environment = "Dev"
  }
}

# IAM Role para Lambda
resource "aws_iam_role" "lambda_role" {
  name = "exemplo-lambda-role"

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
    Name        = "Exemplo Lambda Role"
    Environment = "Dev"
  }
}

# IAM Policy para Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "exemplo-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:*",
          "sqs:*",
          "dynamodb:*"
        ]
        resource  "*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "example_lambda" {
  filename      = "lambda_function.zip"
  function_name = "exemplo-lambda-function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.example_bucket.id
      QUEUE_URL   = aws_sqs_queue.example_queue.url
      TABLE_NAME  = aws_dynamodb_table.example_table.name
    }
  }

  tags = {
    Name        = "Exemplo Lambda Function"
    Environment = "Dev"
  }
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "example_api" {
  name        = "exemplo-api-gateway"
  description = "API Gateway de exemplo"

  tags = {
    Name        = "Exemplo API Gateway"
    Environment = "Dev"
  }
}

# API Gateway Resource
resource "aws_api_gateway_resource" "example_resource" {
  rest_api_id = aws_api_gateway_rest_api.example_api.id
  parent_id   = aws_api_gateway_rest_api.example_api.root_resource_id
  path_part   = "exemplo"
}

# API Gateway Method
resource "aws_api_gateway_method" "example_method" {
  rest_api_id   = aws_api_gateway_rest_api.example_api.id
  resource_id   = aws_api_gateway_resource.example_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration com Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.example_api.id
  resource_id             = aws_api_gateway_resource.example_resource.id
  http_method             = aws_api_gateway_method.example_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.example_lambda.invoke_arn
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "example_deployment" {
  rest_api_id = aws_api_gateway_rest_api.example_api.id
  stage_name  = "dev"

  depends_on = [
    aws_api_gateway_integration.lambda_integration
  ]
}

# Lambda Permission para API Gateway
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.example_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.example_api.execution_arn}/*/*"
}

# ECS Cluster
resource "aws_ecs_cluster" "example_cluster" {
  name = "exemplo-ecs-cluster"

  tags = {
    Name        = "Exemplo ECS Cluster"
    Environment = "Dev"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "example_task" {
  family                   = "exemplo-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "exemplo-container"
      image     = "nginx:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
    }
  ])

  tags = {
    Name        = "Exemplo ECS Task"
    Environment = "Dev"
  }
}

# IAM Role para ECS Task Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "exemplo-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "Exemplo ECS Execution Role"
    Environment = "Dev"
  }
}

# IAM Policy Attachment para ECS
resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Outputs
output "s3_bucket_name" {
  value       = aws_s3_bucket.example_bucket.id
  description = "Nome do bucket S3"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.example_table.name
  description = "Nome da tabela DynamoDB"
}

output "sqs_queue_url" {
  value       = aws_sqs_queue.example_queue.url
  description = "URL da fila SQS"
}

output "lambda_function_name" {
  value       = aws_lambda_function.example_lambda.function_name
  description = "Nome da função Lambda"
}

output "api_gateway_url" {
  value       = "${aws_api_gateway_deployment.example_deployment.invoke_url}exemplo"
  description = "URL do API Gateway"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.example_cluster.name
  description = "Nome do cluster ECS"
}
