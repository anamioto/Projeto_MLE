# 1. Provedor e Variáveis
provider "aws" {
  region = "us-east-1"
}

variable "nomeTabela" {
  type        = string
  description = "Nome da tabela DynamoDB"
}

# URI da imagem no ECR 
variable "image_uri" {
  type    = string
  description = "URI da imagem no ECR — gerada no build"
}

# 2. DynamoDB  
resource "aws_dynamodb_table" "Tabela_dos_Passageiros" {
  name         = var.nomeTabela
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

# 3. IAM Role 
resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 4. Lambda com Suporte a Docker (Container Image)
resource "aws_lambda_function" "api_handler" {
  function_name = "titanic_preditor"
  role          = aws_iam_role.lambda_exec.arn
  
  # Alteração Crítica: Usar Image em vez de Zip
  package_type = "Image"
  image_uri    = var.image_uri
  architectures = ["x86_64"]

  # Recursos aumentados para ML
  memory_size = 512
  timeout     = 30
  

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.Tabela_dos_Passageiros.name
    }
  }
}

# 5. API Gateway 
resource "aws_api_gateway_rest_api" "titanic_api" {
  name        = "TitanicAPI"
  description = "API para predição de sobreviventes"

  body = templatefile("${path.module}/../documentação/openapi.yaml", {
    lambda_invoke_arn = aws_lambda_function.api_handler.invoke_arn
  })
}

# Permissões e Deploy (Mantidos) 
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.titanic_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.titanic_api.id
  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.titanic_api.body))
  }
  lifecycle { create_before_destroy = true }
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.titanic_api.id
  stage_name    = "prod"
}

output "api_url" {
  value = aws_api_gateway_stage.api_stage.invoke_url
}