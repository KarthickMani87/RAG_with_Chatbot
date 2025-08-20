#!/bin/bash
set -e

# Get AWS region from first argument, or default to "us-east-1"
AWS_REGION="${1:-us-east-1}"

echo " Using AWS region: $AWS_REGION"

echo " Logging in to ECR..."
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo " Getting image URIs from Terraform outputs..."
LLM_IMAGE_URI=$(terraform output -raw llm_image_uri)
EMBEDDING_IMAGE_URI=$(terraform output -raw embedding_image_uri)
ORCHESTRATOR_IMAGE_URI=$(terraform output -raw orchestrator_image_uri)

echo " Building and pushing LLM service..."
docker build -t llm-service ./services/llm-service
docker tag llm-service:latest $LLM_IMAGE_URI
docker push $LLM_IMAGE_URI

echo " Building and pushing Embedding service..."
docker build -t embedding-service ./services/embedding-service
docker tag embedding-service:latest $EMBEDDING_IMAGE_URI
docker push $EMBEDDING_IMAGE_URI

echo " Building and pushing Orchestrator API..."
docker build -t orchestrator ./services/orchestrator
docker tag orchestrator:latest $ORCHESTRATOR_IMAGE_URI
docker push $ORCHESTRATOR_IMAGE_URI

echo " All images pushed successfully!"

