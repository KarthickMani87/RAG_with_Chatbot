variable "aws_region" {
  default = "ap-southeast-2"
}

variable "lambda_name" {
  default = "fastapi-lambda"
}

variable "lambda_zip_bucket_name" {
  description = "Globally unique S3 bucket name to store Lambda ZIP"
  type        = string
}

variable "s3_bucket" {
  description = "App-specific S3 bucket used inside Lambda"
  type        = string
}
