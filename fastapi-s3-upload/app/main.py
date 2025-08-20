from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3, os, re, traceback
#from dotenv import load_dotenv
from datetime import datetime, timezone
from mangum import Mangum

#load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
print("S3_BUCKET: ", S3_BUCKET)

s3_client = boto3.client(
    "s3"
)

@app.get("/")
def root():
    return {"status": "ok"}

class FileRequest(BaseModel):
    filename: str
    content_type: str

@app.post("/generate_presigned_url/")
def generate_presigned_url(data: FileRequest):
    try:
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', data.filename)
        key = f"uploads/{datetime.now(timezone.utc).isoformat()}_{clean_name}"

        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": S3_BUCKET, "Key": key, "ContentType": data.content_type},
            ExpiresIn=3600
        )
        return {"url": url, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DeleteRequest(BaseModel):
    key: str

@app.delete("/delete_file/")
def delete_file(req: DeleteRequest = Body(...)):
    try:
        print(f"Deleting from bucket: {S3_BUCKET}, key: '{req.key}'")
        s3_client.delete_object(Bucket=S3_BUCKET, Key=req.key)
        return {"message": f"Deleted {req.key}"}
    except Exception as e:
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

# 👇 This is what Lambda uses
handler = Mangum(app)
