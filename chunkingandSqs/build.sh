#!/bin/bash
set -e

echo "🛠️  Building Lambda zip package inside Docker..."
docker build -t lambda-builder .
CONTAINER_ID=$(docker create lambda-builder)
docker cp $CONTAINER_ID:/lambda.zip ./terraform/lambda.zip
docker rm $CONTAINER_ID

echo "✅ Lambda package copied to terraform/lambda.zip"

