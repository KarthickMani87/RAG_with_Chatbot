from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from mangum import Mangum

app = FastAPI()

EMBEDDING_URL = os.getenv("EMBEDDING_URL")
LLM_URL = os.getenv("LLM_URL")

class Query(BaseModel):
    query: str               # user input
    mode: str                # "rag" or "chatbot"
    prompt: str = None       # optional prompt override for chatbot mode

@app.post("/query")
def query_llm(data: Query):
    if data.mode.lower() == "rag":
        # Step 1: Get top chunks
        res = requests.post(EMBEDDING_URL, json={"query": data.query})
        chunks = res.json().get("results", [])
        context = "\n".join([c["chunk"] for c in chunks])

        # Step 2: Prompt LLM with context
        prompt = f"Context:\n{context}\n\nQuestion:\n{data.query}\nAnswer:"
        llm_res = requests.post(LLM_URL, json={"prompt": prompt})

        return {
            "mode": "rag",
            "answer": llm_res.json().get("output"),
            "context_used": chunks
        }

    elif data.mode.lower() == "chatbot":
        prompt = data.prompt + data.query  # use custom prompt if provided
        llm_res = requests.post(LLM_URL, json={"prompt": prompt})

        try:
            output = llm_res.json().get("output")
        except Exception:
            output = llm_res.text  # fallback to raw text

        return {
            "mode": data.mode,
            "answer": output
        }

    else:
        return {
            "error": "Invalid mode. Use 'rag' or 'chatbot'."
        }

handler = Mangum(app)
