from fastapi import FastAPI, Body
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import re
import traceback

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS (Cross-Origin Resource Sharing)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cors_configuration = {
    'CORSRules': [
        {
            'AllowedOrigins': ['http://localhost:3000'],
            'AllowedMethods': ['PUT', 'POST', 'GET'],
            'AllowedHeaders': ['*'],
            'ExposeHeaders': ['ETag'],
            'MaxAgeSeconds': 36000
        }
    ]
}

# Load from .env
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

try:
    s3_client.put_bucket_cors(Bucket=S3_BUCKET, CORSConfiguration=cors_configuration)
    print("✅ S3 CORS configuration applied.")
except Exception as e:
    print("❌ Failed to apply CORS:", e)

class FileRequest(BaseModel):
    filename: str
    content_type: str

@app.get("/debug/list-all")
def list_all():
    response = s3_client.list_objects_v2(Bucket="intelligentdocument")
    return {"keys": [obj["Key"] for obj in response.get("Contents", [])]}

@app.post("/generate_presigned_url/")
def generate_presigned_url(data: FileRequest):
    try:
        
        #print("✅ Loaded AWS_ACCESS_KEY:", os.getenv("AWS_ACCESS_KEY_ID"))
        #print("✅ Loaded AWS_SECRET_KEY:", os.getenv("AWS_SECRET_ACCESS_KEY"))

        #key = f"uploads/{datetime.now(timezone.utc).isoformat()}_{data.filename}"
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', data.filename)
        key = f"uploads/{datetime.now(timezone.utc).isoformat()}_{clean_name}"

        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": key,
                "ContentType": data.content_type
            },
            ExpiresIn=3600
        )
        print("Generated URL:", url)
        print("Generated Key:", key)
        return {"url": url, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DeleteRequest(BaseModel):
    key: str  # full key, like "uploads/abc123.docx"

@app.delete("/delete_file/")
async def delete_file(req: DeleteRequest = Body(...)):
    print("🔍 Deleting key:", req.key)
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=req.key)
        print("✅ Deleted key:", req.key)
        return {"message": f"Deleted {req.key}"}
    except Exception as e:
        print("❌ Delete failed:")
        traceback.print_exc()
        return {"error": str(e)}


@app.get("/list_files/")
def list_files():
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="uploads/")
        contents = response.get("Contents", [])
        files = [obj["Key"] for obj in contents]
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}
    

'''
@app.post("/generate_presigned_url/")
def generate_presigned_url(data: FileRequest):
    key = f"uploads/{datetime.utcnow().isoformat()}_{data.filename}"
    url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": key,
            "ContentType": data.content_type
        },
        ExpiresIn=3600
    )
    return {"url": url, "key": key}
'''
