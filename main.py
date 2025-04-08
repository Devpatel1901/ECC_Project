# main.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from uuid import uuid4
import boto3
import json
from starlette.status import HTTP_413_REQUEST_ENTITY_TOO_LARGE
from s3_utils import upload_to_s3

MAX_INPUT_SIZE = 64 * 1024  # 64 KB


app = FastAPI()
sqs = boto3.client("sqs")
SQS_QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/774305605898/CodeExecutionQueue"

@app.post("/submit")
async def submit_code(language: str = Form(...), code: UploadFile = Form(...), stdin: UploadFile = Form(None)):
    submission_id = str(uuid4())

    # Validate input file size
    if stdin:
        content = await stdin.read()
        if len(content) > MAX_INPUT_SIZE:
            raise HTTPException(
                status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Input file too large. Max allowed: 64 KB"
            )
        # Rewind file pointer since we already read it
        stdin.file.seek(0)

    ext_map = {
        "python": "code.py",
        "cpp": "code.cpp",
        "java": "Code.java",
        "go": "code.go",
        "js": "code.js"
    }

    # Save to S3
    code_key = f"submissions/{submission_id}/{ext_map[language]}"
    input_key = f"submissions/{submission_id}/input.txt" if stdin else None

    await upload_to_s3(code, code_key)
    if stdin:
        await upload_to_s3(stdin, input_key)

    # Send job to SQS
    job = {
        "submission_id": submission_id,
        "language": language,
        "code_key": code_key,
        "input_key": input_key
    }
    sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(job))

    return {"submission_id": submission_id, "job": job, "status": "QUEUED"}
