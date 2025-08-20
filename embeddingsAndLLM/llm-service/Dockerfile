FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    python3-dev \
    curl \
    jq \
    libgomp1 \
    pkg-config \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone llama.cpp
RUN git clone https://github.com/ggerganov/llama.cpp /app/llama.cpp

# Build llama.cpp with CMake (including main)
WORKDIR /app/llama.cpp
RUN mkdir -p build && cd build && \
    cmake .. -DLLAMA_CURL=OFF -DLLAMA_CUDA=OFF -DLLAMA_METAL=OFF -DLLAMA_BLAS=OFF && \
    make -j && \
    #cp ./main /app/llama.cpp/build/main  # Ensure main is in known location
    cp ./bin/llama-cli /app/llama.cpp/build/llama-cli

# Copy app code and install Python dependencies
WORKDIR /app
COPY llm-requirements.txt .
RUN pip install --no-cache-dir -r llm-requirements.txt

# Install AWS CLI (used in entrypoint)
RUN pip install awscli

# Copy FastAPI app code
COPY app/ /app/app/

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 5000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

