from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import faiss, numpy as np, boto3, os

app = FastAPI()

INDEX_PATH = "/data/index.faiss"

# Ensure /data exists
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

dim = 384

# Ensure /data directory exists
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

# Initialize FAISS index safely
if os.path.exists(INDEX_PATH):
    try:
        index = faiss.read_index(INDEX_PATH)
        print("✅ FAISS index loaded from disk.")
    except Exception as e:
        print(f"⚠️ Could not load FAISS index, starting fresh. Error: {e}")
        index = faiss.IndexFlatL2(dim)
else:
    print("⚠️ No FAISS index found on disk. Starting with empty index.")
    index = faiss.IndexFlatL2(dim)

if index.ntotal == 0:
    print("⚠️ FAISS index is empty. No results will be returned until vectors are added.")

ddb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "ap-southeast-2"))
table = ddb.Table(os.getenv("DDB_TABLE", "document_chunks"))

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class ChunkResult(BaseModel):
    chunk: str
    score: float
    doc_id: str

@app.post("/search", response_model=List[ChunkResult])
def search(req: SearchRequest):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vec = model.encode([req.query])
    D, I = index.search(np.array(vec), req.top_k)

    results = []
    for i, idx in enumerate(I[0]):
        item = table.scan(FilterExpression="vector_id = :vid", ExpressionAttributeValues={":vid": int(idx)})
        if item["Items"]:
            record = item["Items"][0]
            results.append({
                "chunk": record["chunk"],
                "score": float(D[0][i]),
                "doc_id": record["doc_id"]
            })
    return results

