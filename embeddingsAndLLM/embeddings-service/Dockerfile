# Stage 1: Build environment
FROM python:3.10-slim as builder

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy app source
COPY app/ /app/app/

# Stage 2: Minimal runtime image
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ /app/app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

