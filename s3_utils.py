# s3_utils.py
import json
from fastapi import UploadFile
import boto3
from constants import S3_BUCKET

s3 = boto3.client("s3")

async def upload_to_s3(file: UploadFile, key: str):
    content = await file.read()
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=content)

def download_from_s3(key: str, download_path: str):
    with open(download_path, "wb") as f:
        s3.download_fileobj(S3_BUCKET, key, f)

def upload_result_to_s3(key: str, content: dict):
    json_body = json.dumps(content, indent=2)
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json_body)
