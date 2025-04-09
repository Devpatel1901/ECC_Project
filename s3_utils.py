# s3_utils.py
import json
from fastapi import UploadFile
import boto3

s3 = boto3.client("s3")
BUCKET_NAME = "code-nexus-submissions"

async def upload_to_s3(file: UploadFile, key: str):
    content = await file.read()
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=content)

def download_from_s3(key: str, download_path: str):
    with open(download_path, "wb") as f:
        s3.download_fileobj(BUCKET_NAME, key, f)

def upload_result_to_s3(key: str, content: dict):
    json_body = json.dumps(content, indent=2)
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=json_body)
