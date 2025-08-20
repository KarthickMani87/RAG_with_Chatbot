import boto3, json, uuid, faiss, os
from sentence_transformers import SentenceTransformer
import numpy as np

REGION      = os.getenv("AWS_REGION", "ap-southeast-2")
QUEUE_URL   = os.getenv("SQS_URL")
DDB_TABLE   = os.getenv("DDB_TABLE", "document_chunks")
S3_BUCKET   = os.getenv("S3_BUCKET")
S3_KEY      = os.getenv("S3_KEY", "faiss/index.faiss")
INDEX_PATH  = "/data/index.faiss"

model = SentenceTransformer("all-MiniLM-L6-v2")
dim = 384
index = faiss.IndexFlatL2(dim)

# Ensure the /data directory exists
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

# Try to load FAISS index from S3
s3 = boto3.client("s3", region_name=REGION)
try:
    s3.download_file(S3_BUCKET, S3_KEY, INDEX_PATH)
    index = faiss.read_index(INDEX_PATH)
    print(" FAISS index loaded from S3.")
except s3.exceptions.NoSuchKey:
    print(" No index found in S3 (NoSuchKey). Starting with empty index.")
except Exception as e:
    print(f" Could not load FAISS index from S3: {e}")

# DynamoDB
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DDB_TABLE)

# SQS
sqs = boto3.client("sqs", region_name=REGION)

processed = 0
SAVE_INTERVAL = 10

while True:
    messages = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    ).get("Messages", [])

    for msg in messages:
        body = json.loads(msg["Body"])
        chunk = body["chunk"]
        doc_id = body["doc_id"]

        embedding = model.encode([chunk])[0]
        index.add(np.array([embedding]))

        vector_id = index.ntotal - 1
        chunk_id = str(uuid.uuid4())

        table.put_item(Item={
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "vector_id": vector_id,
            "timestamp": str(body.get("timestamp", "")),
            "s3_key": body.get("s3_key", ""),
            "chunk": chunk
        })

        # Remove from queue
        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=msg["ReceiptHandle"]
        )

        processed += 1
        if processed % SAVE_INTERVAL == 0:
            faiss.write_index(index, INDEX_PATH)
            s3.upload_file(INDEX_PATH, S3_BUCKET, S3_KEY)
            print(f"💾 FAISS index saved to S3 at {S3_KEY}")

