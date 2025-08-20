# Dockerfile
FROM public.ecr.aws/lambda/python:3.9

# Install zip
RUN yum install -y zip

RUN pip install --upgrade pip

# Install dependencies
WORKDIR /app
COPY lambda/requirements.txt .
RUN pip install -r requirements.txt -t /app

# Add lambda code
COPY lambda/lambda_function.py .

# Package as ZIP
RUN zip -r /lambda.zip .

