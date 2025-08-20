Intelligent Document Processing with RAG + Chatbot

This project is an end-to-end intelligent document retrieval and question-answering system deployed on AWS. It allows users to:

Upload documents (PDF, DOCX, TXT, CSV, XLSX) via a React frontend.

Extract text & tables from documents (Lambda).

Chunk and embed documents into vector embeddings (Sentence Transformers + FAISS + DynamoDB).

Query documents via RAG (Retrieval Augmented Generation) mode or a chatbot mode using TinyLlama.

Interact through a simple chat interface.

📂 Repository Structure
intelligent_document_docker/
├── backend/                   # Lambda worker for embeddings (chunk -> FAISS + DynamoDB)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── chunkingandSqs/            # Lambda for file text extraction + chunking -> SQS
│   ├── lambda/lambda_function.py
│   ├── Dockerfile
│   └── terraform/
│
├── embeddingsAndLLM/          # Embedding + LLM microservices
│   ├── embeddings-service/    # Search API on FAISS + DynamoDB
│   │   └── app/main.py
│   ├── llm-service/           # TinyLlama service
│   │   └── app/server.py
│   └── docker-compose.yml
│
├── orchestrator-api/          # Orchestrator for RAG or chatbot mode
│   ├── main.py
│   └── requirements.txt
│
├── frontend/                  # React frontend (file upload + chat interface)
│   ├── src/App.js
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml         # Local dev orchestration
└── my-rag-on-cloud.pem        # Example key (gitignored in real projects!)



🏗️ System Design
1. Document Upload & Preprocessing

Users upload files via the React frontend (frontend/App.js).

Backend generates S3 presigned URLs for secure upload.

Upload events trigger a Lambda (chunkingandSqs/lambda_function.py):

Extracts text & tables from PDF, DOCX, TXT, CSV, XLSX.

Splits into chunks (smart_chunk).

Sends chunks to SQS with metadata.

2. Embedding Pipeline

A worker Lambda / container (backend/worker.py):

Reads chunks from SQS.

Generates embeddings using SentenceTransformers (MiniLM).

Adds embeddings to a FAISS index (persisted in S3).

Stores chunk metadata in DynamoDB.

3. Search & Retrieval

Embedding Service (embeddingsAndLLM/embeddings-service):

Exposes /search API.

Uses FAISS + DynamoDB to return top k matching chunks for a query.

4. LLM Service

TinyLlama service (embeddingsAndLLM/llm-service):

Wraps llama.cpp.

Receives prompts, generates completions.

Lightweight inference for chatbot mode.

5. Orchestrator API

FastAPI (orchestrator-api/main.py):

/query endpoint.

Modes:

RAG Mode → retrieves top chunks → passes context + query to LLM.

Chatbot Mode → directly forwards user prompt to LLM.

6. Frontend

React App (frontend/App.js):

File uploads with status.

Manage uploaded files (list, delete).

Start embeddings manually.

Chat interface:

Choose between Chatbot or RAG mode.

Display conversation history.

🔧 Tech Stack

Frontend: React + Axios + Dropzone

Backend Services: FastAPI

NLP: SentenceTransformers (all-MiniLM-L6-v2), TinyLlama (via llama.cpp)

Vector Store: FAISS (persisted in S3) + DynamoDB metadata

AWS Services:

S3 (document storage)

Lambda (chunking, embedding worker)

SQS (chunk pipeline)

DynamoDB (metadata store)


🚀 Deployment

Currently deployed on AWS Cloud (via Terraform for infra – excluded here due to hardcoded configs).
Main components run in containers (ECS/EKS compatible).

For local development:

docker-compose up --build


Frontend will be available at: http://localhost:3000
APIs (backend/orchestrator/LLM/embeddings) on respective ports.

✅ Features

 Multi-format document ingestion (PDF, DOCX, TXT, CSV, XLSX)

 Smart chunking + structured table extraction

 Embedding storage in FAISS + DynamoDB

 RAG-based contextual Q&A

 Chatbot-only mode

 React UI for upload + chat

📌 Next Steps

🔒 Improve Terraform/IaC with parameterized configs.

⚡ Optimize FAISS index loading (cold start mitigation).

🧠 Support multiple LLM backends (OpenAI API, Anthropic, etc.).

🖥️ Add authentication for frontend/backend APIs.
