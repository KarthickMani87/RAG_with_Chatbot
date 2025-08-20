#!/bin/bash
set -e

echo " Starting container..."

# Create model directory if it doesn't exist
mkdir -p /app/models

# Optional fallback: if no AWS credentials set, get them from EC2 metadata
if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" || -z "$AWS_SESSION_TOKEN" ]]; then
  echo " AWS credentials not found in env vars. Attempting to fetch from EC2 metadata..."

  ROLE_NAME=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/ || true)

  if [[ -n "$ROLE_NAME" ]]; then
    CREDS=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE_NAME)
    export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r .AccessKeyId)
    export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r .SecretAccessKey)
    export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r .Token)
    export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-ap-southeast-2}
    echo " Fetched temporary credentials from EC2 metadata"
  else
    echo " No IAM role found on EC2 instance and no credentials provided"
    exit 1
  fi
fi

# Download model if not already present
if [ ! -f /app/models/tinyllama.gguf ]; then
    echo " Downloading model from S3..."
    aws s3 cp s3://llm-models-tiny/tinyllama.gguf /app/models/tinyllama.gguf
else
    echo " Model already exists locally. Skipping download."
fi

# Create symbolic link to llama-cli as main (if not already present)
if [ ! -f /app/llama.cpp/build/main ]; then
    echo " Creating symbolic link to llama-cli as main..."
    ln -s /app/llama.cpp/build/bin/llama-cli /app/llama.cpp/build/main
fi

# Start the FastAPI server
echo "🚀 Launching FastAPI..."
exec uvicorn app.server:app --host 0.0.0.0 --port 5000
