output "lambda_function_name" {
  value = aws_lambda_function.fastapi_lambda.function_name
}

output "lambda_s3_key" {
  value = aws_s3_object.lambda_zip.key
}

output "api_gateway_url" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}
