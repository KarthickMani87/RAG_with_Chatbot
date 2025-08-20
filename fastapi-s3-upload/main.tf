provider "aws" {
    region = var.aws_region
  }
  
  # S3 bucket to store Lambda ZIP
  resource "aws_s3_bucket" "lambda_bucket" {
    bucket = var.lambda_zip_bucket_name
    force_destroy = true
  }
  
  data "archive_file" "lambda_zip" {
    type        = "zip"
    source_dir  = "${path.module}/app"
    output_path = "${path.module}/lambda_function_payload.zip"
  }
  
  resource "aws_s3_object" "lambda_zip" {
    bucket = aws_s3_bucket.lambda_bucket.id
    key    = "lambda_function_payload.zip"
    source = data.archive_file.lambda_zip.output_path
    etag   = filemd5(data.archive_file.lambda_zip.output_path)
  }
  
  resource "aws_lambda_function" "fastapi_lambda" {
    function_name = var.lambda_name
    role          = aws_iam_role.lambda_exec.arn
    handler       = "main.handler"
    runtime       = "python3.11"
  
    s3_bucket     = aws_s3_bucket.lambda_bucket.id
    s3_key        = aws_s3_object.lambda_zip.key
  
    source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  
    environment {
      variables = {
        S3_BUCKET = var.s3_bucket
      }
    }
  
    timeout = 30
  }

  # API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "fastapi-http-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.fastapi_lambda.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# ❗Move this block after the route
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# Lambda permission for API Gateway to invoke the function
resource "aws_lambda_permission" "api_gateway" {
    statement_id  = "AllowExecutionFromAPIGateway"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.fastapi_lambda.function_name
    principal     = "apigateway.amazonaws.com"
    source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_iam_policy" "lambda_s3_modify_access" {
  name = "lambda_s3_modify_access"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid      = "AllowListBucket",
        Effect   = "Allow",
        Action   = [
          "s3:ListBucket"
        ],
        Resource = "arn:aws:s3:::${var.s3_bucket}"
      },
      {
        Sid      = "AllowObjectActions",
        Effect   = "Allow",
        Action   = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = "arn:aws:s3:::${var.s3_bucket}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_modify_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_s3_modify_access.arn
}